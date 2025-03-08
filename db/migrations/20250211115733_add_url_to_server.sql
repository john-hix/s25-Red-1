-- migrate:up
alter table openapi_server add column "url" varchar not null;

-- migrate:down
alter table openapi_server drop column if exists "url";
