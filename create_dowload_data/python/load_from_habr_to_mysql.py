import sys
import json
import logging
import requests
import pymysql.cursors
import pandas as pd
import psycopg2 as pg


def get_str_before_str(main_string: str, str2: str) -> str:
    return main_string[: (main_string.find(str2) if main_string.find(str2) != -1 else len(main_string))]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
    min = int(sys.argv[1])
    max = int(sys.argv[2])
    df = None
    with open("secret/pg-dwh.txt") as file:
        with pg.connect(file.read().replace('\n', ' ')) as users_conn:
            df = pd.read_sql('select username from users', con=users_conn)
    if df is not None:
        with open("secret/mysql.txt") as file:
            with pymysql.connect(file.read().replace('\n', ' '))as connection:
                sql = "INSERT INTO users_requests (creator, request) VALUES "
                with connection.cursor() as cursor:
                    indicator = False
                    for i in range(min, max):
                        logging.info(i)
                        url = "https://m.habr.com/kek/v2/articles/{}/?fl=ru%2Cen&hl=ru".format(i)
                        r = requests.get(url)
                        if r.status_code == 200:
                            data = json.loads(r.text)
                            article = {'name': data['titleHtml'],
                                       'description': get_str_before_str(data['leadData']['textHtml'], '<'),
                                       'tag': data['tags'][0]}
                            if indicator:
                                sql += ','
                            sql += f"('{df.sample(n=1).values[0][0]}', '{article['description']}')"
                            sql += ','
                            sql += f"('{df.sample(n=1).values[0][0]}', '{article['name']}')"
                            indicator = True
                    cursor.execute(sql + ';')
                connection.commit()
    else:
        logging.exception("No users")
