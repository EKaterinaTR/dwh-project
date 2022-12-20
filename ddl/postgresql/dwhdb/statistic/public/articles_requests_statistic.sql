create table articles_requests_statistic
(
    id              bigint primary key ,
    answer_time     timestamp,
    username        varchar,
    request         varchar,
    ans_docs        integer[],
    ans_percents    double precision[],
    max_percent     double precision,
    min_percent     double precision,
    average_percent double precision,
    constraint articles_requests_statistic_users_username_fk
        foreign key (username) references users (username)
);

