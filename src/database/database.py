#!/usr/bin/env python3
"""
Database Integration for BMAD System

This module provides database integration for the BMAD system,
using SQLite for local development and testing.
"""

import sqlite3
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """
    Database class for handling all database operations.
    """

    def __init__(self, db_path: str = "bmad.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database with required tables."""
        logger.info("Initializing database...")
        
        # Create users table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Create managers table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS managers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        
        # Create model_manager table for assigning managers to models
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS model_manager (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER NOT NULL,
                manager_id INTEGER NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models (id),
                FOREIGN KEY (manager_id) REFERENCES managers (id)
            )
            """
        )
        
        # Create models table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                language TEXT DEFAULT 'en',
                persona TEXT,
                consent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create posts table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                caption TEXT,
                media_url TEXT,
                platform TEXT,
                status TEXT,
                posted_at TIMESTAMP,
                engagement TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
            """
        )

        # Create metrics table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
            """
        )

        # Create audit_log table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id TEXT,
                trace_id TEXT NOT NULL,
                outcome TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Create recruitment_funnel table
        self.cursor.execute(
            """
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
            )
            """
        )
        
        # Create index on recruitment_funnel for performance
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recruitment_funnel_model_id ON recruitment_funnel (model_id)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recruitment_funnel_recruiter_id ON recruitment_funnel (recruiter_id)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recruitment_funnel_stage ON recruitment_funnel (stage)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recruitment_funnel_status ON recruitment_funnel (status)"
        )
        
        # Create contracts table
        self.cursor.execute(
            """
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
            )
            """
        )
        
        # Create index on contracts for performance
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_contracts_model_id ON contracts (model_id)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_contracts_recruiter_id ON contracts (recruiter_id)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts (status)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_contracts_contract_type ON contracts (contract_type)"
        )
        
        # Create communications table
        self.cursor.execute(
            """
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
            )
            """
        )
        
        # Create index on communications for performance
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_communications_model_id ON communications (model_id)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_communications_recruiter_id ON communications (recruiter_id)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_communications_type ON communications (communication_type)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_communications_direction ON communications (direction)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_communications_status ON communications (status)"
        )
        
        # Extend models table with recruiter fields
        self.cursor.execute(
            """
            ALTER TABLE models ADD COLUMN recruiter_id INTEGER
            """
        )
        self.cursor.execute(
            """
            ALTER TABLE models ADD COLUMN recruitment_status TEXT DEFAULT 'unassigned'
            """
        )
        self.cursor.execute(
            """
            ALTER TABLE models ADD COLUMN last_contacted_at TIMESTAMP
            """
        )
        self.cursor.execute(
            """
            ALTER TABLE models ADD COLUMN next_follow_up_at TIMESTAMP
            """
        )
        self.cursor.execute(
            """
            ALTER TABLE models ADD COLUMN source TEXT
            """
        )
        self.cursor.execute(
            """
            ALTER TABLE models ADD COLUMN tags TEXT
            """
        )
        
        # Create indexes for extended models fields
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_models_recruiter_id ON models (recruiter_id)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_models_recruitment_status ON models (recruitment_status)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_models_source ON models (source)"
        )
        
        self.conn.commit()
        logger.info("Database initialized successfully")

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in the database."""
        logger.info(f"Creating user: {user_data['username']}")
        
        self.cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_data.get("username"),
                user_data.get("email"),
                user_data.get("password_hash"),
                user_data.get("role", "user")
            )
        )
        self.conn.commit()
        
        user_id = self.cursor.lastrowid
        return self.get_user(user_id)

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get a user by ID."""
        self.cursor.execute(
            """
            SELECT * FROM users WHERE id = ?
            """,
            (user_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        else:
            raise ValueError(f"User with ID {user_id} not found")

    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get a user by username."""
        self.cursor.execute(
            """
            SELECT * FROM users WHERE username = ?
            """,
            (username,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        else:
            raise ValueError(f"User with username {username} not found")

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get a user by email."""
        self.cursor.execute(
            """
            SELECT * FROM users WHERE email = ?
            """,
            (email,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        else:
            raise ValueError(f"User with email {email} not found")

    def create_manager(self, manager_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new manager in the database."""
        logger.info(f"Creating manager: {manager_data['name']}")
        
        self.cursor.execute(
            """
            INSERT INTO managers (user_id, name, email, phone)
            VALUES (?, ?, ?, ?)
            """,
            (
                manager_data.get("user_id"),
                manager_data.get("name"),
                manager_data.get("email"),
                manager_data.get("phone")
            )
        )
        self.conn.commit()
        
        manager_id = self.cursor.lastrowid
        return self.get_manager(manager_id)

    def get_manager(self, manager_id: int) -> Dict[str, Any]:
        """Get a manager by ID."""
        self.cursor.execute(
            """
            SELECT * FROM managers WHERE id = ?
            """,
            (manager_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "email": row[3],
                "phone": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        else:
            raise ValueError(f"Manager with ID {manager_id} not found")

    def assign_manager_to_model(self, model_id: int, manager_id: int) -> Dict[str, Any]:
        """Assign a manager to a model."""
        logger.info(f"Assigning manager {manager_id} to model {model_id}")
        
        self.cursor.execute(
            """
            INSERT INTO model_manager (model_id, manager_id)
            VALUES (?, ?)
            """,
            (model_id, manager_id)
        )
        self.conn.commit()
        
        assignment_id = self.cursor.lastrowid
        return self.get_model_manager_assignment(assignment_id)

    def get_model_manager_assignment(self, assignment_id: int) -> Dict[str, Any]:
        """Get a model-manager assignment by ID."""
        self.cursor.execute(
            """
            SELECT * FROM model_manager WHERE id = ?
            """,
            (assignment_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "model_id": row[1],
                "manager_id": row[2],
                "assigned_at": row[3]
            }
        else:
            raise ValueError(f"Assignment with ID {assignment_id} not found")

    def create_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new model in the database."""
        logger.info(f"Creating model: {model_data['name']}")
        
        self.cursor.execute(
            """
            INSERT INTO models (external_id, name, email, language, persona, consent)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                model_data.get("external_id"),
                model_data.get("name"),
                model_data.get("email"),
                model_data.get("language", "en"),
                str(model_data.get("persona", {})),
                model_data.get("consent", False)
            )
        )
        self.conn.commit()
        
        model_id = self.cursor.lastrowid
        return self.get_model(model_id)

    def get_model(self, model_id: int) -> Dict[str, Any]:
        """Get a model by ID."""
        self.cursor.execute(
            """
            SELECT * FROM models WHERE id = ?
            """,
            (model_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "external_id": row[1],
                "name": row[2],
                "email": row[3],
                "language": row[4],
                "persona": eval(row[5]) if row[5] else {},
                "consent": bool(row[6]),
                "created_at": row[7],
                "updated_at": row[8]
            }
        else:
            raise ValueError(f"Model with ID {model_id} not found")

    def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all models from the database."""
        self.cursor.execute("SELECT * FROM models")
        rows = self.cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "external_id": row[1],
                "name": row[2],
                "email": row[3],
                "language": row[4],
                "persona": eval(row[5]) if row[5] else {},
                "consent": bool(row[6]),
                "created_at": row[7],
                "updated_at": row[8]
            }
            for row in rows
        ]

    def create_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new post in the database."""
        logger.info(f"Creating post for model {post_data['model_id']}")
        
        self.cursor.execute(
            """
            INSERT INTO posts (model_id, caption, media_url, platform, status, posted_at, engagement)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_data.get("model_id"),
                post_data.get("caption"),
                post_data.get("media_url"),
                post_data.get("platform"),
                post_data.get("status"),
                post_data.get("posted_at"),
                str(post_data.get("engagement", {}))
            )
        )
        self.conn.commit()
        
        post_id = self.cursor.lastrowid
        return self.get_post(post_id)

    def get_post(self, post_id: int) -> Dict[str, Any]:
        """Get a post by ID."""
        self.cursor.execute(
            """
            SELECT * FROM posts WHERE id = ?
            """,
            (post_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "model_id": row[1],
                "caption": row[2],
                "media_url": row[3],
                "platform": row[4],
                "status": row[5],
                "posted_at": row[6],
                "engagement": eval(row[7]) if row[7] else {},
                "created_at": row[8]
            }
        else:
            raise ValueError(f"Post with ID {post_id} not found")

    def get_all_posts(self) -> List[Dict[str, Any]]:
        """Get all posts from the database."""
        self.cursor.execute("SELECT * FROM posts")
        rows = self.cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "model_id": row[1],
                "caption": row[2],
                "media_url": row[3],
                "platform": row[4],
                "status": row[5],
                "posted_at": row[6],
                "engagement": eval(row[7]) if row[7] else {},
                "created_at": row[8]
            }
            for row in rows
        ]

    def create_metric(self, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new metric in the database."""
        logger.info(f"Creating metric for post {metric_data['post_id']}")
        
        self.cursor.execute(
            """
            INSERT INTO metrics (post_id, likes, comments, shares, views)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                metric_data.get("post_id"),
                metric_data.get("likes", 0),
                metric_data.get("comments", 0),
                metric_data.get("shares", 0),
                metric_data.get("views", 0)
            )
        )
        self.conn.commit()
        
        metric_id = self.cursor.lastrowid
        return self.get_metric(metric_id)

    def get_metric(self, metric_id: int) -> Dict[str, Any]:
        """Get a metric by ID."""
        self.cursor.execute(
            """
            SELECT * FROM metrics WHERE id = ?
            """,
            (metric_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "post_id": row[1],
                "likes": row[2],
                "comments": row[3],
                "shares": row[4],
                "views": row[5],
                "collected_at": row[6]
            }
        else:
            raise ValueError(f"Metric with ID {metric_id} not found")

    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get all metrics from the database."""
        self.cursor.execute("SELECT * FROM metrics")
        rows = self.cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "post_id": row[1],
                "likes": row[2],
                "comments": row[3],
                "shares": row[4],
                "views": row[5],
                "collected_at": row[6]
            }
            for row in rows
        ]

    def log_audit(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log an audit entry in the database."""
        logger.info(f"Logging audit entry for agent {audit_data['agent_id']}")
        
        self.cursor.execute(
            """
            INSERT INTO audit_log (agent_id, action, entity_type, entity_id, trace_id, outcome, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_data.get("agent_id"),
                audit_data.get("action"),
                audit_data.get("entity_type"),
                audit_data.get("entity_id"),
                audit_data.get("trace_id"),
                audit_data.get("outcome"),
                str(audit_data.get("metadata", {}))
            )
        )
        self.conn.commit()
        
        audit_id = self.cursor.lastrowid
        return self.get_audit_log(audit_id)

    def get_audit_log(self, audit_id: int) -> Dict[str, Any]:
        """Get an audit log entry by ID."""
        self.cursor.execute(
            """
            SELECT * FROM audit_log WHERE id = ?
            """,
            (audit_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "agent_id": row[1],
                "action": row[2],
                "entity_type": row[3],
                "entity_id": row[4],
                "trace_id": row[5],
                "outcome": row[6],
                "metadata": eval(row[7]) if row[7] else {},
                "created_at": row[8]
            }
        else:
            raise ValueError(f"Audit log with ID {audit_id} not found")

    def create_recruitment_funnel_entry(self, funnel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new recruitment funnel entry in the database."""
        logger.info(f"Creating recruitment funnel entry for model {funnel_data['model_id']}")
        
        self.cursor.execute(
            """
            INSERT INTO recruitment_funnel (model_id, stage, recruiter_id, status, notes, applied_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                funnel_data.get("model_id"),
                funnel_data.get("stage"),
                funnel_data.get("recruiter_id"),
                funnel_data.get("status", "active"),
                funnel_data.get("notes"),
                funnel_data.get("applied_at"),
                funnel_data.get("updated_at")
            )
        )
        self.conn.commit()
        
        funnel_id = self.cursor.lastrowid
        return self.get_recruitment_funnel_entry(funnel_id)
    
    def get_recruitment_funnel_entry(self, funnel_id: int) -> Dict[str, Any]:
        """Get a recruitment funnel entry by ID."""
        self.cursor.execute(
            """
            SELECT * FROM recruitment_funnel WHERE id = ?
            """,
            (funnel_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "model_id": row[1],
                "stage": row[2],
                "recruiter_id": row[3],
                "status": row[4],
                "notes": row[5],
                "applied_at": row[6],
                "updated_at": row[7]
            }
        else:
            raise ValueError(f"Recruitment funnel entry with ID {funnel_id} not found")
    
    def get_all_funnel_entries(self) -> List[Dict[str, Any]]:
        """Get all recruitment funnel entries from the database."""
        self.cursor.execute("SELECT * FROM recruitment_funnel")
        rows = self.cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "model_id": row[1],
                "stage": row[2],
                "recruiter_id": row[3],
                "status": row[4],
                "notes": row[5],
                "applied_at": row[6],
                "updated_at": row[7]
            }
            for row in rows
        ]
    
    def create_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contract in the database."""
        logger.info(f"Creating contract for model {contract_data['model_id']}")
        
        self.cursor.execute(
            """
            INSERT INTO contracts (model_id, recruiter_id, contract_type, start_date, end_date, rate, currency, status, signed_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                contract_data.get("model_id"),
                contract_data.get("recruiter_id"),
                contract_data.get("contract_type"),
                contract_data.get("start_date"),
                contract_data.get("end_date"),
                contract_data.get("rate"),
                contract_data.get("currency", "USD"),
                contract_data.get("status", "active"),
                contract_data.get("signed_at"),
                contract_data.get("created_at"),
                contract_data.get("updated_at")
            )
        )
        self.conn.commit()
        
        contract_id = self.cursor.lastrowid
        return self.get_contract(contract_id)
    
    def get_contract(self, contract_id: int) -> Dict[str, Any]:
        """Get a contract by ID."""
        self.cursor.execute(
            """
            SELECT * FROM contracts WHERE id = ?
            """,
            (contract_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "model_id": row[1],
                "recruiter_id": row[2],
                "contract_type": row[3],
                "start_date": row[4],
                "end_date": row[5],
                "rate": row[6],
                "currency": row[7],
                "status": row[8],
                "signed_at": row[9],
                "created_at": row[10],
                "updated_at": row[11]
            }
        else:
            raise ValueError(f"Contract with ID {contract_id} not found")
    
    def get_all_contracts(self) -> List[Dict[str, Any]]:
        """Get all contracts from the database."""
        self.cursor.execute("SELECT * FROM contracts")
        rows = self.cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "model_id": row[1],
                "recruiter_id": row[2],
                "contract_type": row[3],
                "start_date": row[4],
                "end_date": row[5],
                "rate": row[6],
                "currency": row[7],
                "status": row[8],
                "signed_at": row[9],
                "created_at": row[10],
                "updated_at": row[11]
            }
            for row in rows
        ]
    
    def create_communication(self, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new communication in the database."""
        logger.info(f"Creating communication for model {communication_data['model_id']}")
        
        self.cursor.execute(
            """
            INSERT INTO communications (model_id, recruiter_id, communication_type, subject, message, direction, status, sent_at, read_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                communication_data.get("model_id"),
                communication_data.get("recruiter_id"),
                communication_data.get("communication_type"),
                communication_data.get("subject"),
                communication_data.get("message"),
                communication_data.get("direction"),
                communication_data.get("status", "sent"),
                communication_data.get("sent_at"),
                communication_data.get("read_at")
            )
        )
        self.conn.commit()
        
        communication_id = self.cursor.lastrowid
        return self.get_communication(communication_id)
    
    def get_communication(self, communication_id: int) -> Dict[str, Any]:
        """Get a communication by ID."""
        self.cursor.execute(
            """
            SELECT * FROM communications WHERE id = ?
            """,
            (communication_id,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "model_id": row[1],
                "recruiter_id": row[2],
                "communication_type": row[3],
                "subject": row[4],
                "message": row[5],
                "direction": row[6],
                "status": row[7],
                "sent_at": row[8],
                "read_at": row[9]
            }
        else:
            raise ValueError(f"Communication with ID {communication_id} not found")
    
    def update_model_recruiter(self, model_id: int, recruiter_id: Optional[int]) -> Dict[str, Any]:
        """Update the recruiter assigned to a model."""
        logger.info(f"Updating recruiter for model {model_id} to {recruiter_id}")
        
        self.cursor.execute(
            """
            UPDATE models 
            SET recruiter_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (recruiter_id, model_id)
        )
        self.conn.commit()
        
        return self.get_model(model_id)
    
    def update_model_recruitment_status(self, model_id: int, status: str) -> Dict[str, Any]:
        """Update the recruitment status of a model."""
        logger.info(f"Updating recruitment status for model {model_id} to {status}")
        
        self.cursor.execute(
            """
            UPDATE models 
            SET recruitment_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, model_id)
        )
        self.conn.commit()
        
        return self.get_model(model_id)
    
    def update_model_last_contacted(self, model_id: int, last_contacted_at: Optional[str]) -> Dict[str, Any]:
        """Update the last contacted timestamp for a model."""
        logger.info(f"Updating last contacted for model {model_id} to {last_contacted_at}")
        
        self.cursor.execute(
            """
            UPDATE models 
            SET last_contacted_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (last_contacted_at, model_id)
        )
        self.conn.commit()
        
        return self.get_model(model_id)
    
    def update_model_next_follow_up(self, model_id: int, next_follow_up_at: Optional[str]) -> Dict[str, Any]:
        """Update the next follow-up timestamp for a model."""
        logger.info(f"Updating next follow-up for model {model_id} to {next_follow_up_at}")
        
        self.cursor.execute(
            """
            UPDATE models 
            SET next_follow_up_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (next_follow_up_at, model_id)
        )
        self.conn.commit()
        
        return self.get_model(model_id)
    
    def update_model_source(self, model_id: int, source: Optional[str]) -> Dict[str, Any]:
        """Update the source of a model."""
        logger.info(f"Updating source for model {model_id} to {source}")
        
        self.cursor.execute(
            """
            UPDATE models 
            SET source = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (source, model_id)
        )
        self.conn.commit()
        
        return self.get_model(model_id)
    
    def update_funnel_recruiter(self, model_id: int, recruiter_id: int) -> Dict[str, Any]:
        """Update the recruiter_id in recruitment_funnel entries for a model."""
        logger.info(f"Updating recruiter_id in recruitment_funnel for model {model_id} to {recruiter_id}")
        
        self.cursor.execute(
            """
            UPDATE recruitment_funnel 
            SET recruiter_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE model_id = ?
            """,
            (recruiter_id, model_id)
        )
        self.conn.commit()
        
        return self.get_model(model_id)
    
    def update_contracts_recruiter(self, model_id: int, recruiter_id: int) -> Dict[str, Any]:
        """Update the recruiter_id in contracts entries for a model."""
        logger.info(f"Updating recruiter_id in contracts for model {model_id} to {recruiter_id}")
        
        self.cursor.execute(
            """
            UPDATE contracts 
            SET recruiter_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE model_id = ?
            """,
            (recruiter_id, model_id)
        )
        self.conn.commit()
        
        return self.get_model(model_id)
    
    def update_communications_recruiter(self, model_id: int, recruiter_id: int) -> Dict[str, Any]:
        """Update the recruiter_id in communications entries for a model."""
        logger.info(f"Updating recruiter_id in communications for model {model_id} to {recruiter_id}")
        
        self.cursor.execute(
            """
            UPDATE communications 
            SET recruiter_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE model_id = ?
            """,
            (recruiter_id, model_id)
        )
        self.conn.commit()
        
        return self.get_model(model_id)


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = Database()

    # Create a model
    model_data = {
        "external_id": "M001",
        "name": "Test Model",
        "email": "test@example.com",
        "language": "en",
        "persona": {"tags": ["creative", "friendly"]},
        "consent": True
    }
    model = db.create_model(model_data)
    print(f"Created model: {model}")

    # Create a post
    post_data = {
        "model_id": model["id"],
        "caption": "Test post",
        "media_url": "http://example.com/media.jpg",
        "platform": "instagram",
        "status": "draft",
        "posted_at": None,
        "engagement": {}
    }
    post = db.create_post(post_data)
    print(f"Created post: {post}")

    # Create a metric
    metric_data = {
        "post_id": post["id"],
        "likes": 10,
        "comments": 5,
        "shares": 2,
        "views": 100
    }
    metric = db.create_metric(metric_data)
    print(f"Created metric: {metric}")

    # Log an audit entry
    audit_data = {
        "agent_id": "ContentAgent",
        "action": "create_post",
        "entity_type": "post",
        "entity_id": str(post["id"]),
        "trace_id": str(uuid.uuid4()),
        "outcome": "success",
        "metadata": {"post_id": post["id"]}
    }
    audit_log = db.log_audit(audit_data)
    print(f"Created audit log: {audit_log}")

    # Close database
    db.close()