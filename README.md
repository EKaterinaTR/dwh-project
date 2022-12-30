# dwh-project
Training project to use different instrument in dwh.
## Introduction
- [Идея](#Idea)  
- [Используемые docker](#Docker)
- [Создание таблиц, индексов, коллекций и т.д.](#Create-table-index-collection)
- [Загрузка данных в источники](#Data-creating-and-parsing)
- [Загрузка данных в dwh - Luigi](#Luigi)
- [Немного BI, визуализация данных - Yandex DataLens](#Yandex-DataLens) 
## Idea 
Концепция с точки зрения бизнеса - компания, предоставляющая доступ к статьям для зарегистрированных пользователей.
- Есть база данных клиентов - Postgres
- Есть база данных с запросами пользователей - MySQL
- Есть база данных с текстами для предоставления клиентам - Elasticsearch
- Есть сторонняя база данных с аннотациями, на основе которых предстоит выбрать тексты для добавления в Elasticsearch - MongoDB  
## Docker
- MySQL - https://hub.docker.com/_/mysql 
- Postgres - https://hub.docker.com/_/postgres
- MongoDB - https://hub.docker.com/_/mongo
- Elasticsearch - https://hub.docker.com/r/bitnami/elasticsearch 
## Create table, index, collection
 В ddl SQL скрипты для mysql и postgres, http-запрос для elasticsearch.
## Data creating and parsing
 В create_dowload_data python скрипты для парсинга статей с habr.
 С помощью статей с хабр заполняется база статей(elasticsearch), база аннотацией(MongoDB), база запросов пользователей(MySQL).
 В качестве данных пользователей взят датасет - https://data.world/midori1017/fake-users.

## Luigi

## Yandex DataLens
