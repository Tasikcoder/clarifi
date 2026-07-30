-- Fuzzy AHP tables for ClariFi DSS
-- Run against CLARIFI.CLAIMS schema

-- Criteria weights (dynamic, updateable via Skill 1)
CREATE TABLE IF NOT EXISTS CLARIFI.CLAIMS.FUZZY_AHP_WEIGHTS (
    criteria_id STRING PRIMARY KEY,
    criteria_name STRING NOT NULL,
    weight NUMBER(5,4) NOT NULL,
    parent_criteria_id STRING,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_guideline STRING
);

-- Seed data
INSERT INTO CLARIFI.CLAIMS.FUZZY_AHP_WEIGHTS (criteria_id, criteria_name, weight, source_guideline)
VALUES
    ('C1', 'Medical Necessity', 0.4000, 'Initial MVP Config'),
    ('C2', 'Policy Compliance', 0.2500, 'Initial MVP Config'),
    ('C3', 'Documentation Completeness', 0.2000, 'Initial MVP Config'),
    ('C4', 'Cost Reasonableness', 0.1500, 'Initial MVP Config');

-- Adjudication results (stores scoring output per claim)
CREATE TABLE IF NOT EXISTS CLARIFI.CLAIMS.ADJUDICATION_RESULTS (
    adjudication_id STRING DEFAULT UUID_STRING(),
    claim_id STRING NOT NULL,
    final_score NUMBER(5,2),
    decision STRING,
    decision_reason STRING,
    criteria_breakdown VARIANT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    assessed_by STRING DEFAULT 'SYSTEM'
);
