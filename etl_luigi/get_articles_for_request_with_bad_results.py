import psycopg2 as pg
from pymongo import MongoClient
from luigi import Task, run


class GetArticlesFromMongoDB(Task):
    insert = "INSERT INTO offer(request, description_of_articles, id_request,same_words) VALUES({},{},{},{}); "
    get = "select * from get_worse_response_30_percent; "

    def run(self):
        with open("secret/pg-dwh.txt") as file:
            database_info = file.read().replace('\n', ' ')
            with pg.connect(database_info) as dwh:
                with dwh.cursor() as dwh_cursor:
                    with dwh.cursor() as insert_result:
                        with MongoClient('localhost', 27011) as mongo_client:
                            mongo_db = mongo_client['books']
                            dwh_cursor.execute(self.get)
                            row = dwh_cursor.fetchone()
                            while row is not None:
                                all_offer = mongo_db['it-articles'].find({})
                                for text in all_offer:
                                    count = 0
                                    req_word = row[0].split(" ")
                                    if "" in req_word:
                                        req_word.remove("")
                                    if " " in req_word:
                                        req_word.remove(" ")
                                    text_word = text['description'].split(" ")
                                    same_words = []
                                    for word in req_word:
                                        if word in text_word or word in text['tags']:
                                            count += 1
                                            same_words.append(word)
                                    if count > len(req_word) * 0.4:
                                        request = row[0].replace("'", "''")
                                        description = text['description'].replace("'", "''")
                                        same_words = str(same_words).replace("'", "''")
                                        insert_result.execute(self.insert.format(f"'{request}'",
                                                                                 f"'{description}'",
                                                                                 row[1],
                                                                                 f"'{same_words}'"
                                                                                 ))
                                row = dwh_cursor.fetchone()


if __name__ == '__main__':
    run()
