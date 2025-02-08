-- migrate:up
create table cuecode_account(
    cuecode_account_id uuid not null default uuid_generate_v4()
    ,email varchar not null
    ,display_name varchar not null
    ,primary key (cuecode_account_id)
);

create table cuecode_api_key(
    cuecode_api_key_id uuid not null default uuid_generate_v4()
    ,grants_access_to_cuecode_account_id uuid not null
        references cuecode_account(cuecode_account_id)
    ,"secret" varchar not null
    ,primary key(cuecode_api_key_id)
);

alter table cuecode_config add column belongs_to_cuecode_account_id uuid
    references cuecode_account(cuecode_account_id) on update cascade on delete cascade;

-- migrate:down
alter table cuecode_config drop column belongs_to_cuecode_account_id;
drop table if exists cuecode_api_key;
drop table if exists cuecode_account;
