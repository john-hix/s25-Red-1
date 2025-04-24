-- migrate:up

alter table openapi_operation drop column if exists selection_prompt;
alter table openapi_operation drop column if exists selection_prompt_embedding;

-- per-sentence embeddings require splitting our selection prompt into multiple
-- db entries, all referencing the same OpenAPI Operation
create table openapi_operation_selection_prompt(
    openapi_operation_selection_prompt_id uuid not null,
    openapi_operation_id uuid not null
        references openapi_operation(openapi_operation_id)
        on delete cascade on update cascade,
    selection_prompt text,
    selection_prompt_embedding vector(384), -- 384 is the dim for all-MiniLM-L6-v2
    primary key (openapi_operation_selection_prompt_id)
);
-- migrate:down

drop table if exists openapi_operation_selection_prompt;

alter table openapi_operation add column selection_prompt text;
alter table openapi_operation add column selection_prompt_embedding vector(4096);
