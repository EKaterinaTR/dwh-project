create table users_requests
(
    creator varchar(40) null,
    request text        not null,
    id      bigint auto_increment primary key,
    time    datetime    null
);