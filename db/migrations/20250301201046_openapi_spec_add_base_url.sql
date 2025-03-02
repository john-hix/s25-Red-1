-- migrate:up
alter table openapi_spec add column base_url varchar not null;

-- migrate:down
alter table openapi_spec drop column if exists base_url;
