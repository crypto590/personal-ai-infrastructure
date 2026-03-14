-- Skill Tracker Schema for Neon (Postgres + pgvector)
-- Run this once to set up the database.

-- Enable pgvector extension (available on Neon by default)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- SKILLS: Registry of all known skills across projects
-- ============================================================
CREATE TABLE IF NOT EXISTS skills (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    file_path       TEXT,                          -- relative path within PAI (e.g., skills/technical/code-review/SKILL.md)
    current_version INTEGER NOT NULL DEFAULT 1,
    embedding       vector(1536),                  -- semantic embedding of skill content
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_embedding ON skills USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- ============================================================
-- OBSERVATIONS: One record per skill execution
-- ============================================================
CREATE TABLE IF NOT EXISTS observations (
    id              SERIAL PRIMARY KEY,
    skill_name      TEXT NOT NULL REFERENCES skills(name),
    project         TEXT,                          -- project directory or identifier
    agent_name      TEXT,                          -- which agent ran this skill
    task_summary    TEXT,                          -- what was attempted
    outcome         TEXT NOT NULL CHECK (outcome IN ('success', 'partial_failure', 'failure', 'unknown')),
    error_type      TEXT CHECK (error_type IN ('routing', 'instruction', 'tool_call', 'output_quality', 'timeout', NULL)),
    error_detail    TEXT,
    duration_seconds REAL,
    user_feedback   TEXT,                          -- explicit user feedback if any
    transcript_ref  TEXT,                          -- path to full transcript JSONL
    skill_version   INTEGER NOT NULL DEFAULT 1,    -- which version of the skill was active
    embedding       vector(1536),                  -- embedding of task + outcome for semantic search
    metadata        JSONB DEFAULT '{}',            -- extensible metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_observations_skill ON observations(skill_name);
CREATE INDEX IF NOT EXISTS idx_observations_outcome ON observations(outcome);
CREATE INDEX IF NOT EXISTS idx_observations_created ON observations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_observations_project ON observations(project);
CREATE INDEX IF NOT EXISTS idx_observations_embedding ON observations USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);

-- ============================================================
-- AMENDMENTS: Proposed and applied changes to skills
-- ============================================================
CREATE TABLE IF NOT EXISTS amendments (
    id              SERIAL PRIMARY KEY,
    skill_name      TEXT NOT NULL REFERENCES skills(name),
    from_version    INTEGER NOT NULL,
    to_version      INTEGER NOT NULL,
    change_type     TEXT NOT NULL CHECK (change_type IN ('tighten_trigger', 'add_condition', 'reorder_steps', 'change_format', 'fix_tool_call', 'rewrite', 'other')),
    rationale       TEXT NOT NULL,                 -- why this change was proposed
    evidence        JSONB NOT NULL DEFAULT '[]',   -- observation IDs and patterns that motivated it
    diff_summary    TEXT,                          -- human-readable summary of what changed
    original_content TEXT,                         -- full SKILL.md before amendment
    amended_content  TEXT,                         -- full SKILL.md after amendment
    status          TEXT NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed', 'approved', 'applied', 'rolled_back', 'rejected')),
    applied_at      TIMESTAMPTZ,
    rolled_back_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_amendments_skill ON amendments(skill_name);
CREATE INDEX IF NOT EXISTS idx_amendments_status ON amendments(status);

-- ============================================================
-- EVALUATIONS: Before/after comparison of amendments
-- ============================================================
CREATE TABLE IF NOT EXISTS evaluations (
    id                  SERIAL PRIMARY KEY,
    amendment_id        INTEGER NOT NULL REFERENCES amendments(id),
    skill_name          TEXT NOT NULL REFERENCES skills(name),
    observations_before INTEGER NOT NULL DEFAULT 0,  -- count of observations before amendment
    observations_after  INTEGER NOT NULL DEFAULT 0,  -- count of observations after amendment
    success_rate_before REAL,                        -- success rate before (0.0 - 1.0)
    success_rate_after  REAL,                        -- success rate after (0.0 - 1.0)
    new_error_types     JSONB DEFAULT '[]',          -- any new error types introduced
    verdict             TEXT CHECK (verdict IN ('improved', 'degraded', 'neutral', 'insufficient_data')),
    notes               TEXT,
    evaluated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluations_amendment ON evaluations(amendment_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_verdict ON evaluations(verdict);

-- ============================================================
-- VIEWS: Convenience queries
-- ============================================================

-- Skill health dashboard
CREATE OR REPLACE VIEW skill_health AS
SELECT
    s.name,
    s.current_version,
    COUNT(o.id) AS total_runs,
    COUNT(o.id) FILTER (WHERE o.outcome = 'success') AS successes,
    COUNT(o.id) FILTER (WHERE o.outcome IN ('failure', 'partial_failure')) AS failures,
    ROUND(
        COUNT(o.id) FILTER (WHERE o.outcome = 'success')::NUMERIC /
        NULLIF(COUNT(o.id), 0), 3
    ) AS success_rate,
    MODE() WITHIN GROUP (ORDER BY o.error_type) FILTER (WHERE o.error_type IS NOT NULL) AS most_common_error,
    MAX(o.created_at) AS last_run,
    COUNT(DISTINCT o.project) AS projects_used_in
FROM skills s
LEFT JOIN observations o ON o.skill_name = s.name
GROUP BY s.name, s.current_version;

-- Recent failures for inspection
CREATE OR REPLACE VIEW recent_failures AS
SELECT
    o.skill_name,
    o.project,
    o.agent_name,
    o.task_summary,
    o.outcome,
    o.error_type,
    o.error_detail,
    o.created_at,
    o.transcript_ref
FROM observations o
WHERE o.outcome IN ('failure', 'partial_failure')
ORDER BY o.created_at DESC
LIMIT 50;
