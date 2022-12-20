import requests
substring = 'You Know, for Search'.encode()
response = requests.get('http://127.0.0.1:9200')
print(response.content)
#%%
from elasticsearch import Elasticsearch

# Create the client instance
client = Elasticsearch("http://localhost:9200")

# Successful response!
client.info()
client.get(index='articles', id=12345)
#%%
from elasticsearch import Elasticsearch

# Create the client instance
client = Elasticsearch("http://localhost:9200")

# Successful response!
print(client.info())