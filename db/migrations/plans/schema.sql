-- Enable pgvector extension for vector data types
CREATE EXTENSION IF NOT EXISTS vector;

-- Enum type for HTTP verbs
CREATE TYPE http_verb_enum AS ENUM ('GET', 'POST', 'PUT', 'PATCH', 'DELETE');

-- Table: cuecode_config
CREATE TABLE cuecode_config (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES cuecode_account(id),
    finished_config BOOLEAN NOT NULL,
    live BOOLEAN NOT NULL
);

-- Table: cuecode_account
CREATE TABLE cuecode_account (
    id UUID PRIMARY KEY,
    email VARCHAR NOT NULL,
    display_name VARCHAR NOT NULL,
    pwd_hash VARCHAR NOT NULL
);

-- Table: cuecode_api_key
CREATE TABLE cuecode_api_key (
    id UUID PRIMARY KEY,
    access_account_id UUID REFERENCES cuecode_account(id),
    secret_hash VARCHAR NOT NULL
);

-- Table: openapi_spec
CREATE TABLE openapi_spec (
    id UUID PRIMARY KEY,
    config_id UUID REFERENCES cuecode_config(id),
    spec_text TEXT NOT NULL,
    live BOOLEAN NOT NULL,
    finished_config BOOLEAN NOT NULL,
    file_name VARCHAR NOT NULL
);

-- Table: openapi_server
CREATE TABLE openapi_server (
    id UUID PRIMARY KEY,
    spec_id UUID REFERENCES openapi_spec(id)
);

-- Table: configuration_job
CREATE TABLE configuration_job (
    id UUID PRIMARY KEY,
    openapi_spec_id UUID REFERENCES openapi_spec(id),
    status VARCHAR NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP
);

-- Table: openapi_path
CREATE TABLE openapi_path (
    id UUID PRIMARY KEY,
    spec_id UUID REFERENCES openapi_spec(id),
    url_template VARCHAR NOT NULL,
    section_prompt TEXT,
    section_prompt_embedding VECTOR(4096),
    llm_tool_spec JSONB
);

-- Table: openapi_payload_examples
CREATE TABLE openapi_payload_examples (
    id UUID PRIMARY KEY,
    example_path_id UUID REFERENCES openapi_path(id),
    example_text TEXT NOT NULL
);

-- Table: openapi_http_equiv
CREATE TABLE openapi_http_equiv (
    id UUID PRIMARY KEY,
    openapi_verb_id UUID REFERENCES verb_lemma(id),
    openapi_path_id UUID REFERENCES openapi_path(id),
    verb_lemma_id UUID REFERENCES verb_lemma(id),
    http_verb http_verb_enum NOT NULL
);

-- Table: openapi_subject_of_verb
CREATE TABLE openapi_subject_of_verb (
    id UUID PRIMARY KEY,
    openapi_entity_id UUID REFERENCES openapi_entity(id)
);

-- Table: verb_lemma
CREATE TABLE verb_lemma (
    id UUID PRIMARY KEY,
    verb_lemma VARCHAR NOT NULL,
    verb_lemma_embedding VECTOR(4096)
);

-- Table: openapi_entity
CREATE TABLE openapi_entity (
    id UUID PRIMARY KEY,
    openapi_spec_id UUID REFERENCES openapi_spec(id),
    noun_prompt TEXT,
    noun_prompt_embedding VECTOR(4096)
);

-- Table: openapi_entity_dependency
CREATE TABLE openapi_entity_dependency (
    child_id UUID REFERENCES openapi_entity(id),
    parent_id UUID REFERENCES openapi_entity(id),
    PRIMARY KEY (child_id, parent_id)
);
