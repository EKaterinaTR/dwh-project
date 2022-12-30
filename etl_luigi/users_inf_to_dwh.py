import psycopg2 as pg
from luigi import Task, run


class MyTask(Task):
    insert = "INSERT INTO users (username, subscription , creation_date) VALUES "
    get = """select username, name as subscription_name, creation_date
                                                from users
                                                join subscription on type_subscription = subscription.id """

    def run(self):
        with open("secret/pg-user.txt") as file:
            database_info = file.read().replace('\n', ' ')
            with pg.connect(database_info) as from_connection:
                with from_connection.cursor() as from_cursor:
                    with open("secret/pg-dwh.txt") as file2:
                        database_info2 = file2.read().replace('\n', ' ')
                        with pg.connect(database_info2) as to_connection:
                            with to_connection.cursor() as to_cursor:
                                from_cursor.execute(self.get)
                                result = from_cursor.fetchall()
                                to_cursor.execute(self.insert + str(
                                    [(row[0], row[1], row[2].strftime('%Y-%m-%d')) for row in result])[
                                                                1: -1] + ";")


if __name__ == '__main__':
    run()
