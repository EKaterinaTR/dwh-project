create table users
(
    id            serial primary key,
    username      varchar unique,
    subscription  varchar,
    creation_date date,
    further_id    integer unique
);

