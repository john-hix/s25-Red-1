-- migrate:up

create table cuecode_config
(
    cuecode_config_id uuid not null default uuid_generate_v4()
    ,config_is_finished boolean
    ,is_live boolean
    ,primary key (cuecode_config_id)
);

create table openapi_spec
(
    openapi_spec_id uuid not null default uuid_generate_v4()
    ,cuecode_config_id uuid not null
        references cuecode_config(cuecode_config_id)
    ,spec_text text
    ,file_name varchar
    ,primary key (openapi_spec_id)
);

create table openapi_entity
(
    openapi_entity_id uuid not null default uuid_generate_v4()
    ,contained_in_oa_spec_id uuid not null
        references openapi_spec(openapi_spec_id)
    ,noun_prompt text not null
    ,noun_prompt_embedding vector(4096)
    ,primary key (openapi_entity_id)
);

create table openapi_server
(
    openapi_server_id uuid not null default uuid_generate_v4()
    ,spec_id uuid not null
        references openapi_spec(openapi_spec_id)
    ,primary key(openapi_server_id)
);

create table openapi_path
(
    openapi_path_id uuid not null default uuid_generate_v4()
    ,oa_server_id uuid not null
        references openapi_server(openapi_server_id)
    ,url_templated varchar not null
    ,selection_prompt text not null
    ,selection_prompt_embedding vector(4096)
    ,llm_content_gen_tool_call_spec jsonb
    ,primary key(openapi_path_id)
);

-- migrate:down
drop table if exists openapi_path;
drop table if exists openapi_server;
drop table if exists openapi_entity;
drop table if exists openapi_spec;
