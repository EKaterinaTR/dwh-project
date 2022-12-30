import sys
import json
from multiprocessing.dummy import Pool as ThreadPool
import logging
import requests
from pymongo import MongoClient

client = MongoClient('localhost', 27011)
db = client['books']
collection = db['it-articles']


def worker(i):
    url = "https://m.habr.com/kek/v2/articles/{}/?fl=ru%2Cen&hl=ru".format(i)

    try:
        r = requests.get(url)
        if r.status_code != 200:
            logging.critical(f"{r.status_code},Error")
            return r.status_code

        data = json.loads(r.text)
        article = {'name': data['titleHtml'],
                   'description': data['leadData']['textHtml'],
                   'author': data['author']['fullname'],
                   'data': data['timePublished'],
                   'tags': [i['titleHtml'] for i in data['tags']]}
        collection.insert_one(article)
    except Exception as e:
        logging.critical(e)
        return 1


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
    min = int(sys.argv[1])
    max = int(sys.argv[2])
    pool = ThreadPool(2)
    results = pool.map(worker, range(min, max))
    pool.close()
    pool.join()
    client.close()
