import pymysql
from elasticsearch import Elasticsearch
from luigi import Task, run
import psycopg2 as pg
from numpy import mean


class ArticlesForRequest(Task):
    get = """select creator, request  from  users_requests"""

    insert = """INSERT INTO articles_requests_statistic 
    (username, request, answer_time, max_percent,min_percent, average_percent, ans_docs, ans_percents) 
    VALUES ({}, {}, {}, {}, {}, {}, {}, {})"""

    def run(self):
        with open("secret/mysql.txt") as file:
            database_info = file.read().replace('\n', ' ')
            with pymysql.connect(database_info) as requests_from:
                with requests_from.cursor() as requests:
                    requests.execute(self.get)
                    with Elasticsearch("http://localhost:9200") as articles:
                        with open("secret/pg-dwh.txt") as file2:
                            database_info2 = file2.read().replace('\n', ' ')
                            with pg.connect(database_info2) as to_connection:
                                with to_connection.cursor() as to_cursor:
                                    row = requests.fetchone()
                                    while row is not None:
                                        response = self.get_articles(row, articles)
                                        self.send_result_of_searching(row, response, to_cursor)
                                        row = requests.fetchone()

    def get_articles(self, row, articles):
        get_match_query = {"query": {
            "bool": {
                "should": [  # or
                    {
                        "match": {
                            "text": row['request']
                        }},
                    {
                        "match": {
                            "name": row['request']
                        }}]
            }}}
        return articles.search(index="articles", body=get_match_query)

    def send_result_of_searching(self, row, response, cursor):
        creator, request, max_score, min_score, average_score, list_doc, list_percent = self.prepare_data_for_sending(
            row, response)

        cursor.execute(
            self.insert.format(creator,
                               request,
                               'CURRENT_TIMESTAMP',
                               max_score,
                               min_score,
                               average_score,
                               list_doc,
                               list_percent))

    def prepare_data_for_sending(self, row, response):
        creator = f"'{row['creator']}'"
        request = row['request'].replace("'", "''")
        request = f"'{request}'"
        max_score = response["hits"]["max_score"] if response["hits"]["max_score"] else 0
        min_score = max_score
        average_score = max_score
        list_doc = []
        list_percent = []
        if response["hits"]["hits"]:
            for doc in response["hits"]["hits"]:
                list_doc.append(int(doc["_id"]))
                list_percent.append(doc["_score"])
            if len(list_percent) > 0:
                min_score = min(list_percent)
                average_score = mean(list_percent)
        list_doc = "'{" + str(list_doc)[1:-1] + "}'"
        list_percent = "'{" + str(list_percent)[1:-1] + "}'"
        return creator, request, max_score, min_score, average_score, list_doc, list_percent


if __name__ == '__main__':
    run()
