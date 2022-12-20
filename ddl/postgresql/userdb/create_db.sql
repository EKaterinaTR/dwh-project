create table subscription
(
    id   serial primary key,
    name varchar
);

create table users
(
    id                serial primary key,
    username          varchar unique,
    hash_password     varchar,
    email             varchar,
    creation_date     date,
    type_subscription integer
        constraint users_subscp_fk
            references subscription
);