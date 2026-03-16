#!/usr/bin/env python3
"""
Database Integration for Communication Service

This module provides database integration for the CommunicationService,
using SQLite for local development and testing.
"""

import sqlite3
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommunicationDatabase:
    """
    Database class for handling all communication-related database operations.
    """

    def __init__(self, db_path: str = "bmad.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database with required communication tables."""
        logger.info("Initializing communication database...")
        
        # Create communication_templates table
        self.cursor.execute(
            """
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
            )
            """
        )
        
        # Create follow_up_sequences table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS follow_up_sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                trigger_event TEXT NOT NULL,
                steps TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Create indexes for communication-related queries
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_templates_channel ON communication_templates (channel)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_templates_is_active ON communication_templates (is_active)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sequences_trigger_event ON follow_up_sequences (trigger_event)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sequences_is_active ON follow_up_sequences (is_active)"
        )
        
        # Create indexes for communication queries
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_communications_sent_at ON communications (sent_at)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_communications_scheduled_at ON communications (sent_at) WHERE status = 'scheduled'"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_models_next_follow_up_at ON models (next_follow_up_at) WHERE next_follow_up_at IS NOT NULL"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_models_last_contacted_at ON models (last_contacted_at) WHERE last_contacted_at IS NOT NULL"
        )
        
        self.conn.commit()
        logger.info("Communication database initialized successfully")

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all communication templates from the database."""
        self.cursor.execute("SELECT * FROM communication_templates")
        rows = self.cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "channel": row[2],
                "subject": row[3],
                "message": row[4],
                "variables": row[5],
                "is_active": bool(row[6]),
                "created_at": row[7]
            }
            for row in rows
        ]
    
    def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new communication template in the database."""
        logger.info(f"Creating communication template: {template_data['name']}")
        
        self.cursor.execute(
            """
            INSERT INTO communication_templates (name, channel, subject, message, variables, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                template_data.get("name"),
                template_data.get("channel"),
                template_data.get("subject"),
                template_data.get("message"),
                template_data.get("variables", "[]"),
                template_data.get("is_active", 1)
            )
        )
        self.conn.commit()
        
        template_id = self.cursor.lastrowid
        return self.get_template(template_id)
    
    def get_template(self, template_id: int) -> Dict[str, Any]:
        """Get a communication template by ID."""
        self.cursor.execute(
            "SELECT * FROM communication_templates WHERE id = ?",
            (template_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "channel": row[2],
                "subject": row[3],
                "message": row[4],
                "variables": row[5],
                "is_active": bool(row[6]),
                "created_at": row[7]
            }
        else:
            raise ValueError(f"Template with ID {template_id} not found")
    
    def get_all_follow_up_sequences(self) -> List[Dict[str, Any]]:
        """Get all follow-up sequences from the database."""
        self.cursor.execute("SELECT * FROM follow_up_sequences")
        rows = self.cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "trigger_event": row[2],
                "steps": row[3],
                "is_active": bool(row[4]),
                "created_at": row[5]
            }
            for row in rows
        ]
    
    def create_follow_up_sequence(self, sequence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new follow-up sequence in the database."""
        logger.info(f"Creating follow-up sequence: {sequence_data['name']}")
        
        self.cursor.execute(
            """
            INSERT INTO follow_up_sequences (name, trigger_event, steps, is_active)
            VALUES (?, ?, ?, ?)
            """,
            (
                sequence_data.get("name"),
                sequence_data.get("trigger_event"),
                sequence_data.get("steps", "[]"),
                sequence_data.get("is_active", 1)
            )
        )
        self.conn.commit()
        
        sequence_id = self.cursor.lastrowid
        return self.get_follow_up_sequence(sequence_id)
    
    def get_follow_up_sequence(self, sequence_id: int) -> Dict[str, Any]:
        """Get a follow-up sequence by ID."""
        self.cursor.execute(
            "SELECT * FROM follow_up_sequences WHERE id = ?",
            (sequence_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "trigger_event": row[2],
                "steps": row[3],
                "is_active": bool(row[4]),
                "created_at": row[5]
            }
        else:
            raise ValueError(f"Sequence with ID {sequence_id} not found")
    
    def close(self):
        """Close the database connection."""
        self.conn.close()