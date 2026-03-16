-- Migration script for AI Recruiter System
-- Creates recruitment_funnel, contracts, and communications tables

-- Create recruitment_funnel table
CREATE TABLE IF NOT EXISTS recruitment_funnel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    stage TEXT NOT NULL,
    recruiter_id INTEGER,
    status TEXT DEFAULT 'active',
    notes TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models (id),
    FOREIGN KEY (recruiter_id) REFERENCES managers (id),
    CHECK (stage IN ('applied', 'screened', 'interviewed', 'offered', 'hired', 'rejected')),
    CHECK (status IN ('active', 'inactive', 'completed'))
);

-- Create index on recruitment_funnel for performance
CREATE INDEX IF NOT EXISTS idx_recruitment_funnel_model_id ON recruitment_funnel (model_id);
CREATE INDEX IF NOT EXISTS idx_recruitment_funnel_recruiter_id ON recruitment_funnel (recruiter_id);
CREATE INDEX IF NOT EXISTS idx_recruitment_funnel_stage ON recruitment_funnel (stage);
CREATE INDEX IF NOT EXISTS idx_recruitment_funnel_status ON recruitment_funnel (status);

-- Create contracts table
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    recruiter_id INTEGER,
    contract_type TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    rate REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    status TEXT DEFAULT 'active',
    signed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models (id),
    FOREIGN KEY (recruiter_id) REFERENCES managers (id),
    CHECK (contract_type IN ('full-time', 'part-time', 'contract', 'freelance')),
    CHECK (status IN ('active', 'terminated', 'completed', 'suspended'))
);

-- Create index on contracts for performance
CREATE INDEX IF NOT EXISTS idx_contracts_model_id ON contracts (model_id);
CREATE INDEX IF NOT EXISTS idx_contracts_recruiter_id ON contracts (recruiter_id);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts (status);
CREATE INDEX IF NOT EXISTS idx_contracts_contract_type ON contracts (contract_type);

-- Create communications table
CREATE TABLE IF NOT EXISTS communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    recruiter_id INTEGER,
    communication_type TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    direction TEXT NOT NULL,
    status TEXT DEFAULT 'sent',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models (id),
    FOREIGN KEY (recruiter_id) REFERENCES managers (id),
    CHECK (communication_type IN ('email', 'sms', 'whatsapp', 'phone', 'video_call', 'in_person')),
    CHECK (direction IN ('outbound', 'inbound')),
    CHECK (status IN ('sent', 'delivered', 'read', 'failed', 'scheduled'))
);

-- Create index on communications for performance
CREATE INDEX IF NOT EXISTS idx_communications_model_id ON communications (model_id);
CREATE INDEX IF NOT EXISTS idx_communications_recruiter_id ON communications (recruiter_id);
CREATE INDEX IF NOT EXISTS idx_communications_type ON communications (communication_type);
CREATE INDEX IF NOT EXISTS idx_communications_direction ON communications (direction);
CREATE INDEX IF NOT EXISTS idx_communications_status ON communications (status);

-- Extend models table with recruiter fields
ALTER TABLE models ADD COLUMN recruiter_id INTEGER;
ALTER TABLE models ADD COLUMN recruitment_status TEXT DEFAULT 'unassigned';
ALTER TABLE models ADD COLUMN last_contacted_at TIMESTAMP;
ALTER TABLE models ADD COLUMN next_follow_up_at TIMESTAMP;
ALTER TABLE models ADD COLUMN source TEXT;
ALTER TABLE models ADD COLUMN tags TEXT;

-- Create indexes for extended models fields
CREATE INDEX IF NOT EXISTS idx_models_recruiter_id ON models (recruiter_id);
CREATE INDEX IF NOT EXISTS idx_models_recruitment_status ON models (recruitment_status);
CREATE INDEX IF NOT EXISTS idx_models_source ON models (source);