import random
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.utils.edgemodifier import Label
from airflow.utils.trigger_rule import TriggerRule
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from numpy import mean

def get_articles(row, articles):
        get_match_query = {"query": {
            "bool": {
                "should": [  # or
                    {
                        "match": {
                            "text": row[1]
                        }},
                    {
                        "match": {
                            "name": row[1]
                        }}]
            }}}
        return articles.search(get_match_query,index="articles")

def send_result_of_searching(row, response, cursor):
    insert = """INSERT INTO articles_requests_statistic 
    (username, request, answer_time, max_percent,min_percent, average_percent, ans_docs, ans_percents) 
    VALUES ({}, {}, {}, {}, {}, {}, {}, {})"""
    creator, request, max_score, min_score, average_score, list_doc, list_percent = prepare_data_for_sending(row, response)
    cursor.execute(insert.format(creator,
                               request,
                               'CURRENT_TIMESTAMP',
                               max_score,
                               min_score,
                               average_score,
                               list_doc,
                               list_percent))

def prepare_data_for_sending(row, response):
    creator = f"'{row[0]}'"
    request = row[1].replace("'", "''")
    request = f"'{request}'"
    print(response)
    max_score = response["max_score"] if response["max_score"] else 0
    min_score = max_score
    average_score = max_score
    list_doc = []
    list_percent = []
    if response["hits"]:
        for doc in response["hits"]:
            list_doc.append(int(doc["_id"]))
            list_percent.append(doc["_score"])
        if len(list_percent) > 0:
            min_score = min(list_percent)
            average_score = mean(list_percent)
    list_doc = "'{" + str(list_doc)[1:-1] + "}'"
    list_percent = "'{" + str(list_percent)[1:-1] + "}'"
    return creator, request, max_score, min_score, average_score, list_doc, list_percent

with DAG(
    dag_id='request_to_dwh',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    schedule_interval="@daily",
    tags=['my', 'example2'],
) as dag:
    run_this_first = EmptyOperator(
        task_id='start',
    )

    @task(task_id="etl")
    def request_to_dwh():
        get = """select creator, request  from  users_requests"""
        to_connection = PostgresHook(postgres_conn_id="postgres")
        requests_from = MySqlHook(mysql_conn_id="mysql-request")
        articles = ElasticsearchPythonHook(hosts=["http://elasticsearch:9200"])
        with requests_from.get_conn() as conn:
            with conn.cursor() as requests:
                requests.execute(get)
                with to_connection.get_conn() as conn:
                    with conn.cursor() as to_cursor:
                        row = requests.fetchone()
                        while row is not None:
                            response = get_articles(row, articles)
                            send_result_of_searching(row, response, to_cursor)
                            row = requests.fetchone()

    requests_ins = request_to_dwh()

    run_this_first >> requests_ins


