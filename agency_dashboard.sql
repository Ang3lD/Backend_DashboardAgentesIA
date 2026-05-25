--
-- PostgreSQL database dump
--

\restrict Q6BmWZllwZf3uN2iIGzdODsM9pmBIkQ4NKg0DloRmNCsxYyUvvEY5fIj4uCPRPe

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: set_updated_at(); Type: FUNCTION; Schema: public; Owner: admin
--

CREATE FUNCTION public.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.set_updated_at() OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agents; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.agents (
    id integer NOT NULL,
    client_id integer NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(50),
    description text,
    workflow_id character varying(100),
    chatwoot_inbox character varying(100),
    model character varying(50) DEFAULT 'gpt-4o-mini'::character varying,
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT agents_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'testing'::character varying])::text[])))
);


ALTER TABLE public.agents OWNER TO admin;

--
-- Name: agents_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.agents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agents_id_seq OWNER TO admin;

--
-- Name: agents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.agents_id_seq OWNED BY public.agents.id;


--
-- Name: clients; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.clients (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(50) NOT NULL,
    plan_id integer,
    status character varying(20) DEFAULT 'active'::character varying,
    start_date date,
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT clients_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'paused'::character varying])::text[])))
);


ALTER TABLE public.clients OWNER TO admin;

--
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clients_id_seq OWNER TO admin;

--
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- Name: plans; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.plans (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    price_mxn numeric(10,2) DEFAULT 0 NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.plans OWNER TO admin;

--
-- Name: plans_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plans_id_seq OWNER TO admin;

--
-- Name: plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.plans_id_seq OWNED BY public.plans.id;


--
-- Name: agents id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents ALTER COLUMN id SET DEFAULT nextval('public.agents_id_seq'::regclass);


--
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- Name: plans id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.plans ALTER COLUMN id SET DEFAULT nextval('public.plans_id_seq'::regclass);


--
-- Data for Name: agents; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.agents (id, client_id, name, type, description, workflow_id, chatwoot_inbox, model, status, created_at, updated_at) FROM stdin;
1	1	Villafuerte Support Bot	chatbot	Bot de soporte al cliente 24/7	\N	inbox_123	gpt-4o-mini	active	2026-05-20 12:00:00	2026-05-20 12:00:00
2	1	Villafuerte Sales Agent	agent	Agente de calificación de leads	\N	\N	gpt-4o	active	2026-05-20 12:00:00	2026-05-20 12:00:00
3	1	Data Analyst Bot	agent	Analizador de reportes mensuales	\N	\N	claude-3-5-sonnet-20241022	active	2026-05-20 12:00:00	2026-05-20 12:00:00
4	1	SEO Content Writer	agent	Generador de artículos de blog	\N	\N	gpt-4o-mini	testing	2026-05-20 12:00:00	2026-05-20 12:00:00
5	2	Pie Feliz Reservas	chatbot	Asistente para agendar reservaciones	\N	inbox_456	gpt-4o-mini	active	2026-05-20 12:00:00	2026-05-20 12:00:00
6	2	Recepción Virtual	chatbot	Atención general para clientes	\N	inbox_789	gpt-4o	active	2026-05-20 12:00:00	2026-05-20 12:00:00
7	2	Analista de Inventario	agent	Agente para cruzar datos de stock	\N	\N	gemini-1.5-pro	testing	2026-05-20 12:00:00	2026-05-20 12:00:00
\.


--
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.clients (id, name, slug, plan_id, status, start_date, notes, created_at, updated_at) FROM stdin;
1	Villafuerte	villafuerte	2	active	2025-01-01	\N	2026-05-20 12:46:29.390879	2026-05-20 12:46:29.390879
2	Pie Feliz	pie-feliz	2	active	2025-01-01	\N	2026-05-20 12:46:29.390879	2026-05-20 12:46:29.390879
\.


--
-- Data for Name: plans; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.plans (id, name, price_mxn, description, created_at) FROM stdin;
1	basico	1000.00	Un agente, soporte por WhatsApp	2026-05-20 12:46:29.390879
2	estandar	1500.00	Hasta 3 agentes, soporte prioritario	2026-05-20 12:46:29.390879
3	premium	2500.00	Agentes ilimitados, reportes, SLA	2026-05-20 12:46:29.390879
\.


--
-- Name: agents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.agents_id_seq', 7, true);


--
-- Name: clients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.clients_id_seq', 2, true);


--
-- Name: plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.plans_id_seq', 3, true);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- Name: clients clients_slug_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_slug_key UNIQUE (slug);


--
-- Name: plans plans_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT plans_name_key UNIQUE (name);


--
-- Name: plans plans_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT plans_pkey PRIMARY KEY (id);


--
-- Name: idx_agents_client; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_agents_client ON public.agents USING btree (client_id);


--
-- Name: idx_agents_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_agents_status ON public.agents USING btree (status);


--
-- Name: idx_clients_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_clients_status ON public.clients USING btree (status);


--
-- Name: agents agents_updated_at; Type: TRIGGER; Schema: public; Owner: admin
--

CREATE TRIGGER agents_updated_at BEFORE UPDATE ON public.agents FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: clients clients_updated_at; Type: TRIGGER; Schema: public; Owner: admin
--

CREATE TRIGGER clients_updated_at BEFORE UPDATE ON public.clients FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: agents agents_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- Name: clients clients_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.plans(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict Q6BmWZllwZf3uN2iIGzdODsM9pmBIkQ4NKg0DloRmNCsxYyUvvEY5fIj4uCPRPe

