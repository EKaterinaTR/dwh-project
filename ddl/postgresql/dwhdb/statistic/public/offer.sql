create table offer
(
    id                      serial primary key,
    request                 varchar,
    description_of_articles varchar,
    id_request              integer,
    same_words              varchar,
    constraint offer_users_id_request_fk
        foreign key (username) references users (id)
);


