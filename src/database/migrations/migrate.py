#!/usr/bin/env python3
"""
Migration Runner for AI Recruiter System
"""

import sqlite3
import os
import sys
from pathlib import Path

class MigrationRunner:
    """Class to handle database migrations."""
    
    def __init__(self, db_path: str = "bmad.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.migrations_dir = Path(__file__).parent
        
        # Create migrations table if it doesn't exist
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()
    
    def get_applied_migrations(self) -> list:
        """Get list of applied migrations."""
        self.cursor.execute("SELECT migration_name FROM migrations")
        return [row[0] for row in self.cursor.fetchall()]
    
    def mark_migration_as_applied(self, migration_name: str):
        """Mark a migration as applied."""
        self.cursor.execute(
            "INSERT INTO migrations (migration_name) VALUES (?)",
            (migration_name,)
        )
        self.conn.commit()
    
    def run_migration(self, migration_file: str):
        """Run a single migration file."""
        migration_name = os.path.basename(migration_file)
        
        # Check if migration has already been applied
        if migration_name in self.get_applied_migrations():
            print(f"Migration {migration_name} already applied. Skipping...")
            return
        
        print(f"Applying migration: {migration_name}")
        
        # Read and execute migration
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        try:
            # First ensure base tables exist
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
            
            self.cursor.executescript(migration_sql)
            self.conn.commit()
            self.mark_migration_as_applied(migration_name)
            print(f"Migration {migration_name} applied successfully!")
        except Exception as e:
            print(f"Error applying migration {migration_name}: {e}")
            self.conn.rollback()
            raise
    
    def run_all_migrations(self):
        """Run all pending migrations."""
        print("Starting migration process...")
        
        # Get all migration files
        migration_files = sorted(
            [str(f) for f in self.migrations_dir.glob("*.sql")]
        )
        
        for migration_file in migration_files:
            self.run_migration(migration_file)
        
        print("Migration process completed!")
    
    def close(self):
        """Close database connection."""
        self.conn.close()

if __name__ == "__main__":
    # Initialize migration runner
    runner = MigrationRunner()
    
    try:
        # Run all migrations
        runner.run_all_migrations()
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        runner.close()
        print("Migration runner completed.")