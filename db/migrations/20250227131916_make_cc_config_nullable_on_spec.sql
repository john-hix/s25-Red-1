-- migrate:up
ALTER TABLE openapi_spec 
ALTER COLUMN cuecode_config_id DROP NOT NULL;

-- migrate:down
ALTER TABLE openapi_spec 
ALTER COLUMN cuecode_config_id SET NOT NULL;

