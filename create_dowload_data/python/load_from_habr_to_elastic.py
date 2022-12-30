import sys
import json
from multiprocessing.dummy import Pool as ThreadPool
import logging
import requests
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def worker(i):
    url = "https://m.habr.com/kek/v2/articles/{}/?fl=ru%2Cen&hl=ru".format(i)
    try:
        r = requests.get(url)
        if r.status_code != 200:
            logging.critical(f"{r.status_code},Error")
            return r.status_code
        data = json.loads(r.text)
        article = {'name': data['titleHtml'],
                   'text': data['textHtml'],
                   'author': data['author']['fullname'],
                   'date': data['timePublished'],
                   'lang': data['lang']}
        if article['lang'] == 'ru':
            es.index(index='articles', id=i, body=article)
        return 0
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
    es.close()
