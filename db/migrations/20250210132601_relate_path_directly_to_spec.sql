-- migrate:up
-- no regard for data migration here, since we're in early dev.

alter table openapi_path add column contained_in_openapi_spec_id uuid not null
    references openapi_spec(openapi_spec_id);
alter table openapi_path drop column if exists contained_in_oa_spec_id;

-- migrate:down
alter table openapi_path add column contained_in_oa_spec_id uuid not null
    references openapi_server(openapi_server_id);
alter table openapi_path drop column if exists contained_in_openapi_spec_id;
