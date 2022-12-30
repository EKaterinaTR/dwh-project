import json
from datetime import datetime

import psycopg2 as pg
from kafka import KafkaConsumer



def insert(connection, data, subscription):
    insert_sql = f"""INSERT INTO users (username, subscription , creation_date, further_id)
                     VALUES('{data['username']}',
                            '{subscription[data['type_subscription']]}',
                            '{get_date_in_str(data['creation_date'])}',
                             {data['id']});
    """
    connection.execute(insert_sql)


def delete(connection, data):
    delete_sql = f"DELETE FROM users WHERE further_id = {data['id']};"
    connection.execute(delete_sql)


def update(connection, data, subscription):
    update_sql = f""" UPDATE users SET  
                            subscription = '{subscription[data['type_subscription']]}'
                      WHERE further_id = {data['id']};"""
    connection.execute(update_sql)


def get_date_in_str(days_from_epoch):
    return datetime.fromtimestamp(days_from_epoch * 24 * 60 * 60).strftime('%Y-%m-%d')


def get_subscription():
    with open("secret/pg-user.txt") as file:
        database_info_subscription = file.read().replace('\n', ' ')
    with pg.connect(database_info_subscription) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM subscription;')
            return {row[0]: row[1] for row in cursor.fetchall()}


def cdc(from_connection, to_connection):
    subscription = get_subscription()
    for message in from_connection:
        with to_connection.cursor() as to_cursor:
            try:
                value = json.loads(message.value.decode("utf-8"))
                if value['op'] == 'c':
                    insert(to_cursor, value['after'], subscription)
                elif value['op'] == 'd':
                    delete(to_cursor, value['before'])
                elif value['op'] == 'u':
                    update(to_cursor, value['after'], subscription)
                else:
                    print("don't know")
                to_connection.commit()
            except Exception as e:
                print(e)
                to_connection.rollback()


if __name__ == '__main__':
    try:
        consumer = KafkaConsumer('pg-user.public.users',
                                 bootstrap_servers=['localhost:29092'],
                                 auto_offset_reset='earliest')

        with open("secret/pg-dwh.txt") as file:
            database_info = file.read().replace('\n', ' ')

        with pg.connect(database_info) as to_connection:
            cdc(consumer, to_connection)
        consumer.close()
    except Exception as e:
        print(e)
