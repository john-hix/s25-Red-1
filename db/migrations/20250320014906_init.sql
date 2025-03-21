-- migrate:up
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- --- ENUMS ---
CREATE TYPE http_verb AS ENUM ('GET', 'POST', 'PUT', 'PATCH', 'DELETE');

-- --- TABLES ---

-- cuecode_account
CREATE TABLE cuecode_account (
    cuecode_account_id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,  -- Added UNIQUE constraint
    display_name VARCHAR(255),
    password VARCHAR(255) NOT NULL -- Consider using a more secure hashing mechanism
);

-- cuecode_api_key
CREATE TABLE cuecode_api_key (
    cuecode_api_key_id UUID PRIMARY KEY,
    grants_access_to_account_id UUID NOT NULL REFERENCES cuecode_account(cuecode_account_id) ON DELETE CASCADE, -- Added ON DELETE CASCADE
    secret VARCHAR(255) NOT NULL
);

-- cuecode_config
CREATE TABLE cuecode_config (
    cuecode_config_id UUID PRIMARY KEY,
    belongs_to_cuecode_account_id UUID REFERENCES cuecode_account(cuecode_account_id) ON DELETE CASCADE, -- Added ON DELETE CASCADE
    config_is_finished BOOLEAN NOT NULL DEFAULT FALSE,  -- Added default value
    is_live BOOLEAN NOT NULL DEFAULT FALSE -- Added default value
);

-- auth_type
CREATE TABLE auth_type (
    auth_type_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- service_credential
CREATE TABLE service_credential (
    id UUID PRIMARY KEY,
    type_id UUID REFERENCES auth_type(auth_type_id) ON DELETE SET NULL, -- Added ON DELETE SET NULL
    secret VARCHAR(255) NOT NULL
);

-- openapi_spec
CREATE TABLE openapi_spec (
    openapi_spec_id UUID PRIMARY KEY,
    cuecode_config_id UUID NOT NULL UNIQUE REFERENCES cuecode_config(cuecode_config_id) ON DELETE CASCADE, -- Added ON DELETE CASCADE and UNIQUE
    spec_text TEXT NOT NULL,
    file_name VARCHAR(255),
    base_url VARCHAR(255)
);

-- configuration_job
CREATE TABLE configuration_job (
    configuration_job_id UUID PRIMARY KEY,
    openapi_spec_id UUID NOT NULL REFERENCES openapi_spec(openapi_spec_id) ON DELETE CASCADE,  -- Added ON DELETE CASCADE
    status VARCHAR(255) NOT NULL,  -- Consider creating an ENUM for status
    start_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(), --added default
    end_timestamp TIMESTAMP WITHOUT TIME ZONE
);

-- openapi_server
CREATE TABLE openapi_server (
    openapi_server_id UUID PRIMARY KEY,
    spec_id UUID NOT NULL REFERENCES openapi_spec(openapi_spec_id) ON DELETE CASCADE,  -- Added ON DELETE CASCADE
    url VARCHAR(255) NOT NULL
);

-- openapi_path
CREATE TABLE openapi_path (
    openapi_path_id UUID PRIMARY KEY,
    spec_id UUID NOT NULL REFERENCES openapi_spec(openapi_spec_id) ON DELETE CASCADE,  -- Added ON DELETE CASCADE
    path_templated VARCHAR(255) NOT NULL
);

-- openapi_operation
CREATE TABLE openapi_operation (
    openapi_operation_id UUID PRIMARY KEY,
    openapi_server_id UUID NOT NULL REFERENCES openapi_server(openapi_server_id) ON DELETE CASCADE, -- Added ON DELETE CASCADE
    openapi_path_id UUID NOT NULL REFERENCES openapi_path(openapi_path_id) ON DELETE CASCADE, -- Added ON DELETE CASCADE
    http_verb http_verb NOT NULL,
    selection_prompt TEXT,
    selection_prompt_embedding vector(4096),
    llm_content_gen_tool_call_spec JSONB
);

-- openapi_payload_examples
CREATE TABLE openapi_payload_examples (
    payload_examples_id UUID PRIMARY KEY,
    example_of_openapi_op_id UUID NOT NULL REFERENCES openapi_operation(openapi_operation_id) ON DELETE CASCADE,  -- Added ON DELETE CASCADE
    example_text TEXT
);

-- openapi_entity
CREATE TABLE openapi_entity (
    openapi_entity_id UUID PRIMARY KEY,
    contained_in_oa_spec_id UUID NOT NULL REFERENCES openapi_spec(openapi_spec_id) ON DELETE CASCADE,  -- Added ON DELETE CASCADE
    noun_prompt TEXT,
    noun_prompt_embedding vector(4096)
);

-- openapi_entity_to_operation (Join Table)
CREATE TABLE openapi_entity_to_operation (
    openapi_request_body UUID PRIMARY KEY,
    contains_openapi_entity_id UUID NOT NULL REFERENCES openapi_entity(openapi_entity_id) ON DELETE CASCADE,
    contained_in_openapi_operation_id UUID NOT NULL REFERENCES openapi_operation(openapi_operation_id) ON DELETE CASCADE
    -- Removed UNIQUE constraint on individual FKs, added combined UNIQUE.  A request body should be unique, but entities and operations can repeat across many request bodies
);


-- openapi_entity_dependency (Self-Referencing Join Table)
CREATE TABLE openapi_entity_dependency (
    child_openapi_entity_id UUID REFERENCES openapi_entity(openapi_entity_id) ON DELETE CASCADE,
    parent_openapi_entity_id UUID REFERENCES openapi_entity(openapi_entity_id) ON DELETE CASCADE,
    PRIMARY KEY (child_openapi_entity_id, parent_openapi_entity_id),
     CHECK (child_openapi_entity_id != parent_openapi_entity_id)  -- Prevent self-referential loops

);

-- verb_lemma
CREATE TABLE verb_lemma (
    verb_id UUID PRIMARY KEY,
    verb_lemma VARCHAR NOT NULL UNIQUE, -- Added UNIQUE constraint
    verb_lemma_embedding vector(4096)
);

-- openapi_default_verb_http_equiv  -- lookup table for default verb lemmas
CREATE TABLE openapi_default_verb_http_equiv(
    openapi_default_verb_http_equiv_id UUID PRIMARY KEY,
    http_verb http_verb NOT NULL,
    verb_lemma varchar NOT NULL,
    verb_lemma_embedding vector(4096)
);


-- openapi_subject_of_verb
CREATE TABLE openapi_subject_of_verb (
    subject_of_verb_id UUID PRIMARY KEY,
    noun_openapi_entity_id UUID NOT NULL REFERENCES openapi_entity(openapi_entity_id) ON DELETE CASCADE -- Added ON DELETE CASCADE
);


-- openapi_verb_http_equiv
CREATE TABLE openapi_verb_http_equiv (
    openapi_verb_http_equiv_id UUID PRIMARY KEY,
    subject_oa_subject_of_verb_id UUID REFERENCES openapi_subject_of_verb(subject_of_verb_id) ON DELETE SET NULL,   -- Added ON DELETE SET NULL,
    verb_applied_to_oa_operation_id UUID REFERENCES openapi_operation(openapi_operation_id) ON DELETE CASCADE,   -- Added ON DELETE CASCADE,
    verb_lemma_id UUID REFERENCES verb_lemma(verb_id)  ON DELETE SET NULL      -- Added ON DELETE SET NULL
);


-- --- INDEXES ---  (Crucial for performance, especially with pgvector)

-- Indexes on Foreign Keys (for JOIN performance)
CREATE INDEX idx_cuecode_api_key_account_id ON cuecode_api_key (grants_access_to_account_id);
CREATE INDEX idx_cuecode_config_account_id ON cuecode_config (belongs_to_cuecode_account_id);
CREATE INDEX idx_service_credential_type_id ON service_credential (type_id);
CREATE INDEX idx_openapi_spec_config_id ON openapi_spec (cuecode_config_id);
CREATE INDEX idx_configuration_job_spec_id ON configuration_job (openapi_spec_id);
CREATE INDEX idx_openapi_server_spec_id ON openapi_server (spec_id);
CREATE INDEX idx_openapi_path_spec_id ON openapi_path (spec_id);
CREATE INDEX idx_openapi_operation_server_id ON openapi_operation (openapi_server_id);
CREATE INDEX idx_openapi_operation_path_id ON openapi_operation (openapi_path_id);
CREATE INDEX idx_openapi_payload_examples_op_id ON openapi_payload_examples (example_of_openapi_op_id);
CREATE INDEX idx_openapi_entity_spec_id ON openapi_entity (contained_in_oa_spec_id);
CREATE INDEX idx_openapi_entity_to_operation_entity_id ON openapi_entity_to_operation (contains_openapi_entity_id);
CREATE INDEX idx_openapi_entity_to_operation_operation_id ON openapi_entity_to_operation (contained_in_openapi_operation_id);
CREATE INDEX idx_openapi_entity_dependency_child_id ON openapi_entity_dependency (child_openapi_entity_id);
CREATE INDEX idx_openapi_entity_dependency_parent_id ON openapi_entity_dependency (parent_openapi_entity_id);
CREATE INDEX idx_openapi_subject_of_verb_entity_id ON openapi_subject_of_verb (noun_openapi_entity_id);
CREATE INDEX idx_openapi_verb_http_equiv_subject_id ON openapi_verb_http_equiv (subject_oa_subject_of_verb_id);
CREATE INDEX idx_openapi_verb_http_equiv_operation_id ON openapi_verb_http_equiv (verb_applied_to_oa_operation_id);
CREATE INDEX idx_openapi_verb_http_equiv_verb_lemma_id ON openapi_verb_http_equiv (verb_lemma_id);

-- Index on email for faster lookups
CREATE UNIQUE INDEX idx_cuecode_account_email ON cuecode_account (email);

-- Index on verb_lemma
CREATE INDEX idx_verb_lemma ON verb_lemma(verb_lemma);

-- migrate:down

