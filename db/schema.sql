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
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cuecode_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cuecode_config (
    cuecode_config_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    config_is_finished boolean,
    is_live boolean
);


--
-- Name: openapi_entity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_entity (
    openapi_entity_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    contained_in_oa_spec_id uuid NOT NULL,
    noun_prompt text NOT NULL,
    noun_prompt_embedding public.vector(4096)
);


--
-- Name: openapi_path; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_path (
    openapi_path_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    oa_server_id uuid NOT NULL,
    url_templated character varying NOT NULL,
    selection_prompt text NOT NULL,
    selection_prompt_embedding public.vector(4096),
    llm_content_gen_tool_call_spec jsonb,
    contained_in_openapi_spec_id uuid NOT NULL
);


--
-- Name: openapi_server; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_server (
    openapi_server_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    spec_id uuid NOT NULL,
    url character varying NOT NULL
);


--
-- Name: openapi_spec; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.openapi_spec (
    openapi_spec_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    cuecode_config_id uuid,
    spec_text text,
    file_name character varying,
    base_url character varying NOT NULL
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: cuecode_config cuecode_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuecode_config
    ADD CONSTRAINT cuecode_config_pkey PRIMARY KEY (cuecode_config_id);


--
-- Name: openapi_entity openapi_entity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity
    ADD CONSTRAINT openapi_entity_pkey PRIMARY KEY (openapi_entity_id);


--
-- Name: openapi_path openapi_path_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_path
    ADD CONSTRAINT openapi_path_pkey PRIMARY KEY (openapi_path_id);


--
-- Name: openapi_server openapi_server_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_server
    ADD CONSTRAINT openapi_server_pkey PRIMARY KEY (openapi_server_id);


--
-- Name: openapi_spec openapi_spec_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_spec
    ADD CONSTRAINT openapi_spec_pkey PRIMARY KEY (openapi_spec_id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: openapi_entity openapi_entity_contained_in_oa_spec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_entity
    ADD CONSTRAINT openapi_entity_contained_in_oa_spec_id_fkey FOREIGN KEY (contained_in_oa_spec_id) REFERENCES public.openapi_spec(openapi_spec_id);


--
-- Name: openapi_path openapi_path_contained_in_openapi_spec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_path
    ADD CONSTRAINT openapi_path_contained_in_openapi_spec_id_fkey FOREIGN KEY (contained_in_openapi_spec_id) REFERENCES public.openapi_spec(openapi_spec_id);


--
-- Name: openapi_path openapi_path_oa_server_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_path
    ADD CONSTRAINT openapi_path_oa_server_id_fkey FOREIGN KEY (oa_server_id) REFERENCES public.openapi_server(openapi_server_id);


--
-- Name: openapi_server openapi_server_spec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_server
    ADD CONSTRAINT openapi_server_spec_id_fkey FOREIGN KEY (spec_id) REFERENCES public.openapi_spec(openapi_spec_id);


--
-- Name: openapi_spec openapi_spec_cuecode_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.openapi_spec
    ADD CONSTRAINT openapi_spec_cuecode_config_id_fkey FOREIGN KEY (cuecode_config_id) REFERENCES public.cuecode_config(cuecode_config_id);


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20250129040542'),
    ('20250129040912'),
    ('20250210132601'),
    ('20250211115733'),
    ('20250227131916'),
    ('20250301201046');
