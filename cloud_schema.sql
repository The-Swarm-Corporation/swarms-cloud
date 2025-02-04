-- Enable UUID generation extension.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-----------------------------------------------------------
-- Table: swarms_cloud_api_keys
-----------------------------------------------------------
CREATE TABLE swarms_cloud_api_keys (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    key text NOT NULL UNIQUE,
    owner uuid NOT NULL,  -- Should match auth.uid() for the owner of this API key.
    created_at timestamptz DEFAULT now()
);

-- Enable Row Level Security on the API keys table.
ALTER TABLE swarms_cloud_api_keys ENABLE ROW LEVEL SECURITY;

-- Only allow users to select their own API key.
CREATE POLICY api_keys_select_policy ON swarms_cloud_api_keys
  FOR SELECT
  USING (owner = auth.uid());

-- Only allow inserting a new API key if the owner field matches auth.uid().
CREATE POLICY api_keys_insert_policy ON swarms_cloud_api_keys
  FOR INSERT
  WITH CHECK (owner = auth.uid());

-----------------------------------------------------------
-- Table: swarms_cloud_agents
-----------------------------------------------------------
CREATE TABLE swarms_cloud_agents (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name text NOT NULL,
  description text,
  code text NOT NULL,
  requirements text,
  envs text,
  autoscaling boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  owner uuid NOT NULL  -- The owner of the agent (should be auth.uid())
);

-- Enable Row Level Security on agents.
ALTER TABLE swarms_cloud_agents ENABLE ROW LEVEL SECURITY;

-- Allow a user to SELECT only their own agents.
CREATE POLICY agents_select_policy ON swarms_cloud_agents
  FOR SELECT
  USING (owner = auth.uid());

-- Allow a user to INSERT a new agent only if owner matches auth.uid().
CREATE POLICY agents_insert_policy ON swarms_cloud_agents
  FOR INSERT
  WITH CHECK (owner = auth.uid());

-- Allow a user to UPDATE an agent only if they are the owner.
CREATE POLICY agents_update_policy ON swarms_cloud_agents
  FOR UPDATE
  USING (owner = auth.uid())
  WITH CHECK (owner = auth.uid());

-- Allow a user to DELETE an agent only if they are the owner.
CREATE POLICY agents_delete_policy ON swarms_cloud_agents
  FOR DELETE
  USING (owner = auth.uid());

-----------------------------------------------------------
-- Table: swarms_cloud_runs
-----------------------------------------------------------
CREATE TABLE swarms_cloud_runs (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id uuid NOT NULL REFERENCES swarms_cloud_agents(id) ON DELETE CASCADE,
    api_key uuid NOT NULL REFERENCES swarms_cloud_api_keys(id) ON DELETE CASCADE,
    execution_result text,
    execution_time numeric,  -- Execution time in seconds.
    memory_usage bigint,     -- Memory delta (in bytes).
    logs jsonb,              -- Detailed logs stored as JSON.
    created_at timestamptz DEFAULT now()
);

-- Enable RLS on runs.
ALTER TABLE swarms_cloud_runs ENABLE ROW LEVEL SECURITY;

-- Allow users to SELECT runs only if the api_key matches their auth.uid() (after a lookup).
CREATE POLICY runs_select_policy ON swarms_cloud_runs
  FOR SELECT
  USING (api_key = auth.uid());

-- Allow inserting a run only if the api_key matches auth.uid().
CREATE POLICY runs_insert_policy ON swarms_cloud_runs
  FOR INSERT
  WITH CHECK (api_key = auth.uid());

-----------------------------------------------------------
-- Table: swarms_cloud_logs
-----------------------------------------------------------
CREATE TABLE swarms_cloud_logs (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_key uuid NOT NULL REFERENCES swarms_cloud_api_keys(id) ON DELETE CASCADE,
    route text NOT NULL,
    method text NOT NULL,
    status_code integer,
    request_payload jsonb,
    response_payload jsonb,
    execution_time numeric,  -- In seconds.
    memory_usage bigint,
    timestamp timestamptz DEFAULT now()
);

-- Enable RLS on logs.
ALTER TABLE swarms_cloud_logs ENABLE ROW LEVEL SECURITY;

-- Allow users to SELECT logs only if the api_key matches auth.uid().
CREATE POLICY logs_select_policy ON swarms_cloud_logs
  FOR SELECT
  USING (api_key = auth.uid());

-- Allow inserting logs only if the api_key matches auth.uid().
CREATE POLICY logs_insert_policy ON swarms_cloud_logs
  FOR INSERT
  WITH CHECK (api_key = auth.uid());
