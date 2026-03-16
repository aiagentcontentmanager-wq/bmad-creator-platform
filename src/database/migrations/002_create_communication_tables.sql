-- Migration script for Communication Service
-- Creates communication_templates and follow_up_sequences tables

-- Create communication_templates table
CREATE TABLE IF NOT EXISTS communication_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    channel TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    variables TEXT DEFAULT '[]',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (channel IN ('email', 'sms', 'whatsapp', 'phone', 'video_call', 'in_person')),
    CHECK (is_active IN (0, 1))
);

-- Create index on communication_templates for performance
CREATE INDEX IF NOT EXISTS idx_templates_channel ON communication_templates (channel);
CREATE INDEX IF NOT EXISTS idx_templates_is_active ON communication_templates (is_active);

-- Create follow_up_sequences table
CREATE TABLE IF NOT EXISTS follow_up_sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    trigger_event TEXT NOT NULL,
    steps TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on follow_up_sequences for performance
CREATE INDEX IF NOT EXISTS idx_sequences_trigger_event ON follow_up_sequences (trigger_event);
CREATE INDEX IF NOT EXISTS idx_sequences_is_active ON follow_up_sequences (is_active);

-- Create indexes for communication-related queries
CREATE INDEX IF NOT EXISTS idx_communications_sent_at ON communications (sent_at);
CREATE INDEX IF NOT EXISTS idx_communications_scheduled_at ON communications (sent_at) WHERE status = 'scheduled';
CREATE INDEX IF NOT EXISTS idx_models_next_follow_up_at ON models (next_follow_up_at) WHERE next_follow_up_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_models_last_contacted_at ON models (last_contacted_at) WHERE last_contacted_at IS NOT NULL;