-- MeetMind core PostgreSQL schema. See docs/BLUEPRINT.md §8.
-- Apply via Alembic migrations in app/db/migrations/ for real deployments;
-- this file is the reference DDL.

-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users & Directory
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    slack_user_id TEXT,
    jira_account_id TEXT,
    github_username TEXT,
    name_aliases TEXT[],    -- ["Priya", "PS", "priya.shah"]
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Meetings
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    title TEXT,
    meeting_date DATE NOT NULL,
    timezone TEXT DEFAULT 'UTC',
    duration_seconds INT,
    participants UUID[],    -- FK to users
    input_hash TEXT UNIQUE, -- SHA-256 for dedup
    raw_input_path TEXT,    -- S3/GCS path
    transcript_path TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    submitted_by UUID REFERENCES users(id),
    langgraph_thread_id TEXT,   -- for checkpointing
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Meeting Reports
CREATE TABLE meeting_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID UNIQUE REFERENCES meetings(id),
    executive_summary TEXT,
    decisions JSONB,        -- List[Decision]
    open_questions JSONB,   -- List[Question]
    risks JSONB,            -- List[Risk]
    dependencies JSONB,
    discussion_topics JSONB,
    key_insights JSONB,
    follow_ups JSONB,
    health_metrics JSONB,   -- talk time, decision density, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Action Items
CREATE TABLE action_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id),
    org_id UUID REFERENCES organizations(id),
    fingerprint TEXT NOT NULL,  -- for dedup
    title TEXT NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    owner_raw TEXT,
    owner_resolved TEXT,
    owner_email TEXT,
    owner_confidence FLOAT,
    due_date_raw TEXT,
    due_date DATE,
    due_date_confidence FLOAT,
    priority TEXT DEFAULT 'medium',
    confidence_score FLOAT NOT NULL,
    evidence_quote TEXT,
    evidence_timestamp FLOAT,
    meeting_section TEXT,
    dependencies UUID[],
    is_repeat_commitment BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'pending',  -- pending/approved/rejected/executed
    external_id TEXT,           -- Jira issue ID, GitHub issue number, etc.
    external_system TEXT,       -- jira/github/linear/asana
    external_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    UNIQUE(meeting_id, fingerprint)
);

-- Approval Requests (HITL)
CREATE TABLE approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id),
    status TEXT DEFAULT 'pending',   -- pending/approved/rejected
    approved_by UUID REFERENCES users(id),
    approved_items JSONB,
    rejected_items JSONB,
    edited_items JSONB,
    edit_history JSONB,     -- full diff of every change made
    created_at TIMESTAMPTZ DEFAULT NOW(),
    decided_at TIMESTAMPTZ
);

-- Audit Trail
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id),
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    reasoning TEXT,
    tool_calls JSONB,
    duration_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Integration Configurations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    system_type TEXT NOT NULL,  -- jira/github/slack/gcal/linear
    config JSONB,               -- encrypted connection details
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Idempotency Keys
CREATE TABLE idempotency_keys (
    key TEXT PRIMARY KEY,
    meeting_id UUID REFERENCES meetings(id),
    external_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_meetings_org ON meetings(org_id, meeting_date DESC);
CREATE INDEX idx_action_items_org ON action_items(org_id, status);
CREATE INDEX idx_action_items_owner ON action_items(owner_email, status);
CREATE INDEX idx_action_items_fingerprint ON action_items(fingerprint);
CREATE INDEX idx_action_items_due ON action_items(due_date) WHERE status = 'executed';
CREATE INDEX idx_audit_meeting ON audit_logs(meeting_id, created_at);

-- Row-Level Security — every query is scoped to org_id
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
CREATE POLICY org_isolation ON meetings
    USING (org_id = current_setting('app.current_org_id')::UUID);
