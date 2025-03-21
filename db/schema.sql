SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: http_verb; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.http_verb AS ENUM (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_type (
    auth_type_id uuid NOT NULL,
    name character varying(255) NOT NULL
);


--
-- Name: configuration_job; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.configuration_job (
    configuration_job_id uuid NOT NULL,
    openapi_spec_id uuid NOT NULL,
    status character varying(255) NOT NULL,
    start_timestamp timestamp without time zone DEFAULT now() NOT NULL,
    end_timestamp timestamp without time zone
);


--
-- Name: cuecode_account; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cuecode_account (
    cuecode_account_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    display_name character varying(255),
    password character varying(255) NOT NULL
);


--
-- Name: cuecode_api_key; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cuecode_api_key (
    cuecode_api_key_id uuid NOT NULL,
    grants_access_to_account_id uuid NOT NULL,
    secret character varying(255) NOT NULL
);


--
-- Name: cuecode_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cuecode_config (
    cuecode_config_id uuid NOT NULL,
    belongs_to_cuecode_account_id uuid,
    config_is_finished boolean DEFAULT false NOT NULL,
    is_live boolean DEFAULT false NOT NULL
);


--
-- Name: openapi_default_verb_http_equiv; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_default_verb_http_equiv (
    openapi_default_verb_http_equiv_id uuid NOT NULL,
    http_verb public.http_verb NOT NULL,
    verb_lemma character varying NOT NULL,
    verb_lemma_embedding public.vector(4096)
);


--
-- Name: openapi_entity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_entity (
    openapi_entity_id uuid NOT NULL,
    contained_in_oa_spec_id uuid NOT NULL,
    noun_prompt text,
    noun_prompt_embedding public.vector(4096)
);


--
-- Name: openapi_entity_dependency; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_entity_dependency (
    child_openapi_entity_id uuid NOT NULL,
    parent_openapi_entity_id uuid NOT NULL,
    CONSTRAINT openapi_entity_dependency_check CHECK ((child_openapi_entity_id <> parent_openapi_entity_id))
);


--
-- Name: openapi_entity_to_operation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_entity_to_operation (
    openapi_request_body uuid NOT NULL,
    contains_openapi_entity_id uuid NOT NULL,
    contained_in_openapi_operation_id uuid NOT NULL
);


--
-- Name: openapi_operation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_operation (
    openapi_operation_id uuid NOT NULL,
    openapi_server_id uuid NOT NULL,
    openapi_path_id uuid NOT NULL,
    http_verb public.http_verb NOT NULL,
    selection_prompt text,
    selection_prompt_embedding public.vector(4096),
    llm_content_gen_tool_call_spec jsonb
);


--
-- Name: openapi_path; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_path (
    openapi_path_id uuid NOT NULL,
    spec_id uuid NOT NULL,
    path_templated character varying(255) NOT NULL
);


--
-- Name: openapi_payload_examples; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_payload_examples (
    payload_examples_id uuid NOT NULL,
    example_of_openapi_op_id uuid NOT NULL,
    example_text text
);


--
-- Name: openapi_server; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_server (
    openapi_server_id uuid NOT NULL,
    spec_id uuid NOT NULL,
    url character varying(255) NOT NULL
);


--
-- Name: openapi_spec; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_spec (
    openapi_spec_id uuid NOT NULL,
    cuecode_config_id uuid NOT NULL,
    spec_text text NOT NULL,
    file_name character varying(255),
    base_url character varying(255)
);


--
-- Name: openapi_subject_of_verb; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_subject_of_verb (
    subject_of_verb_id uuid NOT NULL,
    noun_openapi_entity_id uuid NOT NULL
);


--
-- Name: openapi_verb_http_equiv; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_verb_http_equiv (
    openapi_verb_http_equiv_id uuid NOT NULL,
    subject_oa_subject_of_verb_id uuid,
    verb_applied_to_oa_operation_id uuid,
    verb_lemma_id uuid
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: service_credential; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.service_credential (
    id uuid NOT NULL,
    type_id uuid,
    secret character varying(255) NOT NULL
);


--
-- Name: verb_lemma; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.verb_lemma (
    verb_id uuid NOT NULL,
    verb_lemma character varying NOT NULL,
    verb_lemma_embedding public.vector(4096)
);


--
-- Name: auth_type auth_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_type
    ADD CONSTRAINT auth_type_pkey PRIMARY KEY (auth_type_id);


--
-- Name: configuration_job configuration_job_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuration_job
    ADD CONSTRAINT configuration_job_pkey PRIMARY KEY (configuration_job_id);


--
-- Name: cuecode_account cuecode_account_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuecode_account
    ADD CONSTRAINT cuecode_account_email_key UNIQUE (email);


--
-- Name: cuecode_account cuecode_account_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuecode_account
    ADD CONSTRAINT cuecode_account_pkey PRIMARY KEY (cuecode_account_id);


--
-- Name: cuecode_api_key cuecode_api_key_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuecode_api_key
    ADD CONSTRAINT cuecode_api_key_pkey PRIMARY KEY (cuecode_api_key_id);


--
-- Name: cuecode_config cuecode_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuecode_config
    ADD CONSTRAINT cuecode_config_pkey PRIMARY KEY (cuecode_config_id);


--
-- Name: openapi_default_verb_http_equiv openapi_default_verb_http_equiv_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_default_verb_http_equiv
    ADD CONSTRAINT openapi_default_verb_http_equiv_pkey PRIMARY KEY (openapi_default_verb_http_equiv_id);


--
-- Name: openapi_entity_dependency openapi_entity_dependency_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity_dependency
    ADD CONSTRAINT openapi_entity_dependency_pkey PRIMARY KEY (child_openapi_entity_id, parent_openapi_entity_id);


--
-- Name: openapi_entity openapi_entity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity
    ADD CONSTRAINT openapi_entity_pkey PRIMARY KEY (openapi_entity_id);


--
-- Name: openapi_entity_to_operation openapi_entity_to_operation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity_to_operation
    ADD CONSTRAINT openapi_entity_to_operation_pkey PRIMARY KEY (openapi_request_body);


--
-- Name: openapi_operation openapi_operation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_operation
    ADD CONSTRAINT openapi_operation_pkey PRIMARY KEY (openapi_operation_id);


--
-- Name: openapi_path openapi_path_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_path
    ADD CONSTRAINT openapi_path_pkey PRIMARY KEY (openapi_path_id);


--
-- Name: openapi_payload_examples openapi_payload_examples_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_payload_examples
    ADD CONSTRAINT openapi_payload_examples_pkey PRIMARY KEY (payload_examples_id);


--
-- Name: openapi_server openapi_server_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_server
    ADD CONSTRAINT openapi_server_pkey PRIMARY KEY (openapi_server_id);


--
-- Name: openapi_spec openapi_spec_cuecode_config_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_spec
    ADD CONSTRAINT openapi_spec_cuecode_config_id_key UNIQUE (cuecode_config_id);


--
-- Name: openapi_spec openapi_spec_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_spec
    ADD CONSTRAINT openapi_spec_pkey PRIMARY KEY (openapi_spec_id);


--
-- Name: openapi_subject_of_verb openapi_subject_of_verb_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_subject_of_verb
    ADD CONSTRAINT openapi_subject_of_verb_pkey PRIMARY KEY (subject_of_verb_id);


--
-- Name: openapi_verb_http_equiv openapi_verb_http_equiv_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_verb_http_equiv
    ADD CONSTRAINT openapi_verb_http_equiv_pkey PRIMARY KEY (openapi_verb_http_equiv_id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: service_credential service_credential_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_credential
    ADD CONSTRAINT service_credential_pkey PRIMARY KEY (id);


--
-- Name: verb_lemma verb_lemma_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verb_lemma
    ADD CONSTRAINT verb_lemma_pkey PRIMARY KEY (verb_id);


--
-- Name: verb_lemma verb_lemma_verb_lemma_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verb_lemma
    ADD CONSTRAINT verb_lemma_verb_lemma_key UNIQUE (verb_lemma);


--
-- Name: idx_configuration_job_spec_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_configuration_job_spec_id ON public.configuration_job USING btree (openapi_spec_id);


--
-- Name: idx_cuecode_account_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_cuecode_account_email ON public.cuecode_account USING btree (email);


--
-- Name: idx_cuecode_api_key_account_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cuecode_api_key_account_id ON public.cuecode_api_key USING btree (grants_access_to_account_id);


--
-- Name: idx_cuecode_config_account_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cuecode_config_account_id ON public.cuecode_config USING btree (belongs_to_cuecode_account_id);


--
-- Name: idx_openapi_entity_dependency_child_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_entity_dependency_child_id ON public.openapi_entity_dependency USING btree (child_openapi_entity_id);


--
-- Name: idx_openapi_entity_dependency_parent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_entity_dependency_parent_id ON public.openapi_entity_dependency USING btree (parent_openapi_entity_id);


--
-- Name: idx_openapi_entity_spec_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_entity_spec_id ON public.openapi_entity USING btree (contained_in_oa_spec_id);


--
-- Name: idx_openapi_entity_to_operation_entity_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_entity_to_operation_entity_id ON public.openapi_entity_to_operation USING btree (contains_openapi_entity_id);


--
-- Name: idx_openapi_entity_to_operation_operation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_entity_to_operation_operation_id ON public.openapi_entity_to_operation USING btree (contained_in_openapi_operation_id);


--
-- Name: idx_openapi_operation_path_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_operation_path_id ON public.openapi_operation USING btree (openapi_path_id);


--
-- Name: idx_openapi_operation_server_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_operation_server_id ON public.openapi_operation USING btree (openapi_server_id);


--
-- Name: idx_openapi_path_spec_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_path_spec_id ON public.openapi_path USING btree (spec_id);


--
-- Name: idx_openapi_payload_examples_op_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_payload_examples_op_id ON public.openapi_payload_examples USING btree (example_of_openapi_op_id);


--
-- Name: idx_openapi_server_spec_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_server_spec_id ON public.openapi_server USING btree (spec_id);


--
-- Name: idx_openapi_spec_config_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_spec_config_id ON public.openapi_spec USING btree (cuecode_config_id);


--
-- Name: idx_openapi_subject_of_verb_entity_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_subject_of_verb_entity_id ON public.openapi_subject_of_verb USING btree (noun_openapi_entity_id);


--
-- Name: idx_openapi_verb_http_equiv_operation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_verb_http_equiv_operation_id ON public.openapi_verb_http_equiv USING btree (verb_applied_to_oa_operation_id);


--
-- Name: idx_openapi_verb_http_equiv_subject_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_verb_http_equiv_subject_id ON public.openapi_verb_http_equiv USING btree (subject_oa_subject_of_verb_id);


--
-- Name: idx_openapi_verb_http_equiv_verb_lemma_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_openapi_verb_http_equiv_verb_lemma_id ON public.openapi_verb_http_equiv USING btree (verb_lemma_id);


--
-- Name: idx_service_credential_type_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_service_credential_type_id ON public.service_credential USING btree (type_id);


--
-- Name: idx_verb_lemma; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_verb_lemma ON public.verb_lemma USING btree (verb_lemma);


--
-- Name: configuration_job configuration_job_openapi_spec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuration_job
    ADD CONSTRAINT configuration_job_openapi_spec_id_fkey FOREIGN KEY (openapi_spec_id) REFERENCES public.openapi_spec(openapi_spec_id) ON DELETE CASCADE;


--
-- Name: cuecode_api_key cuecode_api_key_grants_access_to_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuecode_api_key
    ADD CONSTRAINT cuecode_api_key_grants_access_to_account_id_fkey FOREIGN KEY (grants_access_to_account_id) REFERENCES public.cuecode_account(cuecode_account_id) ON DELETE CASCADE;


--
-- Name: cuecode_config cuecode_config_belongs_to_cuecode_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuecode_config
    ADD CONSTRAINT cuecode_config_belongs_to_cuecode_account_id_fkey FOREIGN KEY (belongs_to_cuecode_account_id) REFERENCES public.cuecode_account(cuecode_account_id) ON DELETE CASCADE;


--
-- Name: openapi_entity openapi_entity_contained_in_oa_spec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity
    ADD CONSTRAINT openapi_entity_contained_in_oa_spec_id_fkey FOREIGN KEY (contained_in_oa_spec_id) REFERENCES public.openapi_spec(openapi_spec_id) ON DELETE CASCADE;


--
-- Name: openapi_entity_dependency openapi_entity_dependency_child_openapi_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity_dependency
    ADD CONSTRAINT openapi_entity_dependency_child_openapi_entity_id_fkey FOREIGN KEY (child_openapi_entity_id) REFERENCES public.openapi_entity(openapi_entity_id) ON DELETE CASCADE;


--
-- Name: openapi_entity_dependency openapi_entity_dependency_parent_openapi_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity_dependency
    ADD CONSTRAINT openapi_entity_dependency_parent_openapi_entity_id_fkey FOREIGN KEY (parent_openapi_entity_id) REFERENCES public.openapi_entity(openapi_entity_id) ON DELETE CASCADE;


--
-- Name: openapi_entity_to_operation openapi_entity_to_operation_contained_in_openapi_operation_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity_to_operation
    ADD CONSTRAINT openapi_entity_to_operation_contained_in_openapi_operation_fkey FOREIGN KEY (contained_in_openapi_operation_id) REFERENCES public.openapi_operation(openapi_operation_id) ON DELETE CASCADE;


--
-- Name: openapi_entity_to_operation openapi_entity_to_operation_contains_openapi_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity_to_operation
    ADD CONSTRAINT openapi_entity_to_operation_contains_openapi_entity_id_fkey FOREIGN KEY (contains_openapi_entity_id) REFERENCES public.openapi_entity(openapi_entity_id) ON DELETE CASCADE;


--
-- Name: openapi_operation openapi_operation_openapi_path_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_operation
    ADD CONSTRAINT openapi_operation_openapi_path_id_fkey FOREIGN KEY (openapi_path_id) REFERENCES public.openapi_path(openapi_path_id) ON DELETE CASCADE;


--
-- Name: openapi_operation openapi_operation_openapi_server_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_operation
    ADD CONSTRAINT openapi_operation_openapi_server_id_fkey FOREIGN KEY (openapi_server_id) REFERENCES public.openapi_server(openapi_server_id) ON DELETE CASCADE;


--
-- Name: openapi_path openapi_path_spec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_path
    ADD CONSTRAINT openapi_path_spec_id_fkey FOREIGN KEY (spec_id) REFERENCES public.openapi_spec(openapi_spec_id) ON DELETE CASCADE;


--
-- Name: openapi_payload_examples openapi_payload_examples_example_of_openapi_op_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_payload_examples
    ADD CONSTRAINT openapi_payload_examples_example_of_openapi_op_id_fkey FOREIGN KEY (example_of_openapi_op_id) REFERENCES public.openapi_operation(openapi_operation_id) ON DELETE CASCADE;


--
-- Name: openapi_server openapi_server_spec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_server
    ADD CONSTRAINT openapi_server_spec_id_fkey FOREIGN KEY (spec_id) REFERENCES public.openapi_spec(openapi_spec_id) ON DELETE CASCADE;


--
-- Name: openapi_spec openapi_spec_cuecode_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_spec
    ADD CONSTRAINT openapi_spec_cuecode_config_id_fkey FOREIGN KEY (cuecode_config_id) REFERENCES public.cuecode_config(cuecode_config_id) ON DELETE CASCADE;


--
-- Name: openapi_subject_of_verb openapi_subject_of_verb_noun_openapi_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_subject_of_verb
    ADD CONSTRAINT openapi_subject_of_verb_noun_openapi_entity_id_fkey FOREIGN KEY (noun_openapi_entity_id) REFERENCES public.openapi_entity(openapi_entity_id) ON DELETE CASCADE;


--
-- Name: openapi_verb_http_equiv openapi_verb_http_equiv_subject_oa_subject_of_verb_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_verb_http_equiv
    ADD CONSTRAINT openapi_verb_http_equiv_subject_oa_subject_of_verb_id_fkey FOREIGN KEY (subject_oa_subject_of_verb_id) REFERENCES public.openapi_subject_of_verb(subject_of_verb_id) ON DELETE SET NULL;


--
-- Name: openapi_verb_http_equiv openapi_verb_http_equiv_verb_applied_to_oa_operation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_verb_http_equiv
    ADD CONSTRAINT openapi_verb_http_equiv_verb_applied_to_oa_operation_id_fkey FOREIGN KEY (verb_applied_to_oa_operation_id) REFERENCES public.openapi_operation(openapi_operation_id) ON DELETE CASCADE;


--
-- Name: openapi_verb_http_equiv openapi_verb_http_equiv_verb_lemma_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_verb_http_equiv
    ADD CONSTRAINT openapi_verb_http_equiv_verb_lemma_id_fkey FOREIGN KEY (verb_lemma_id) REFERENCES public.verb_lemma(verb_id) ON DELETE SET NULL;


--
-- Name: service_credential service_credential_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_credential
    ADD CONSTRAINT service_credential_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.auth_type(auth_type_id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20250320014305'),
    ('20250320014906');
