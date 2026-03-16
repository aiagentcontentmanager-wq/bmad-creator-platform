"""
Consolidated Database for BMAD System.
Single SQLite connection with proper thread safety.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import contextmanager

from src.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Single database class for all BMAD operations."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._initialize()

    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def _initialize(self):
        """Create all tables."""
        with self.transaction() as conn:
            conn.executescript("""
                -- Users
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'creator',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Creators (extends users for the business domain)
                CREATE TABLE IF NOT EXISTS creators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    platform TEXT,
                    persona TEXT DEFAULT '{}',
                    language TEXT DEFAULT 'en',
                    consent BOOLEAN DEFAULT 0,
                    consent_at TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                -- Managers
                CREATE TABLE IF NOT EXISTS managers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                -- Manager-Creator assignments
                CREATE TABLE IF NOT EXISTS creator_managers (
                    creator_id INTEGER NOT NULL,
                    manager_id INTEGER NOT NULL,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (creator_id, manager_id),
                    FOREIGN KEY (creator_id) REFERENCES creators(id),
                    FOREIGN KEY (manager_id) REFERENCES managers(id)
                );

                -- Content
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id INTEGER NOT NULL,
                    content_type TEXT NOT NULL,
                    title TEXT,
                    body TEXT,
                    media_url TEXT,
                    persona_tags TEXT DEFAULT '[]',
                    status TEXT DEFAULT 'draft',
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES creators(id)
                );

                -- Publishing queue
                CREATE TABLE IF NOT EXISTS publish_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    scheduled_at TIMESTAMP NOT NULL,
                    published_at TIMESTAMP,
                    platform_post_id TEXT,
                    status TEXT DEFAULT 'scheduled',
                    retry_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (content_id) REFERENCES content(id)
                );

                -- Analytics / Metrics
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (content_id) REFERENCES content(id)
                );

                -- Finance: Revenue entries
                CREATE TABLE IF NOT EXISTS revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'EUR',
                    period_start DATE,
                    period_end DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES creators(id)
                );

                -- Finance: Payouts
                CREATE TABLE IF NOT EXISTS payouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    commission REAL NOT NULL,
                    net_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    paid_at TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (creator_id) REFERENCES creators(id),
                    FOREIGN KEY (approved_by) REFERENCES users(id)
                );

                -- Finance: Ledger (double-entry)
                CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_type TEXT NOT NULL,
                    reference_id INTEGER,
                    reference_type TEXT,
                    creator_id INTEGER,
                    debit REAL DEFAULT 0.0,
                    credit REAL DEFAULT 0.0,
                    balance REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES creators(id)
                );

                -- Recruitment funnel
                CREATE TABLE IF NOT EXISTS recruitment_funnel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id INTEGER NOT NULL,
                    stage TEXT NOT NULL,
                    recruiter_id INTEGER,
                    status TEXT DEFAULT 'active',
                    notes TEXT,
                    applied_at TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES creators(id),
                    FOREIGN KEY (recruiter_id) REFERENCES users(id)
                );

                -- Communications
                CREATE TABLE IF NOT EXISTS communications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id INTEGER NOT NULL,
                    template_id INTEGER,
                    channel TEXT NOT NULL,
                    subject TEXT,
                    message TEXT NOT NULL,
                    direction TEXT DEFAULT 'outbound',
                    status TEXT DEFAULT 'sent',
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (creator_id) REFERENCES creators(id)
                );

                -- Communication templates
                CREATE TABLE IF NOT EXISTS communication_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    subject TEXT,
                    message TEXT NOT NULL,
                    variables TEXT DEFAULT '[]',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Creator assistant conversation history
                CREATE TABLE IF NOT EXISTS assistant_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id INTEGER NOT NULL,
                    fan_identifier TEXT,
                    messages TEXT NOT NULL DEFAULT '[]',
                    last_suggestion TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES creators(id)
                );

                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_creators_user ON creators(user_id);
                CREATE INDEX IF NOT EXISTS idx_content_creator ON content(creator_id);
                CREATE INDEX IF NOT EXISTS idx_content_status ON content(status);
                CREATE INDEX IF NOT EXISTS idx_publish_queue_status ON publish_queue(status);
                CREATE INDEX IF NOT EXISTS idx_publish_queue_scheduled ON publish_queue(scheduled_at);
                CREATE INDEX IF NOT EXISTS idx_metrics_content ON metrics(content_id);
                CREATE INDEX IF NOT EXISTS idx_metrics_collected ON metrics(collected_at);
                CREATE INDEX IF NOT EXISTS idx_revenue_creator ON revenue(creator_id);
                CREATE INDEX IF NOT EXISTS idx_payouts_creator ON payouts(creator_id);
                CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
                CREATE INDEX IF NOT EXISTS idx_ledger_creator ON ledger(creator_id);
                CREATE INDEX IF NOT EXISTS idx_funnel_creator ON recruitment_funnel(creator_id);
                CREATE INDEX IF NOT EXISTS idx_communications_creator ON communications(creator_id);
                CREATE INDEX IF NOT EXISTS idx_assistant_conv_creator ON assistant_conversations(creator_id);
            """)
        logger.info("Database initialized successfully")

    # ─── Users ───

    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (data["username"], data["email"], data["password_hash"], data.get("role", "creator"))
            )
            user_id = cursor.lastrowid
        return self.get_user_by_id(user_id)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None

    # ─── Creators ───

    def create_creator(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO creators (user_id, name, platform, persona, language, consent, consent_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["user_id"], data["name"], data.get("platform"),
                 json.dumps(data.get("persona", {})), data.get("language", "en"),
                 data.get("consent", False), data.get("consent_at"))
            )
            creator_id = cursor.lastrowid
        return self.get_creator_by_id(creator_id)

    def get_creator_by_id(self, creator_id: int) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM creators WHERE id = ?", (creator_id,)).fetchone()
        if row:
            d = dict(row)
            persona_raw = d.get("persona")
            d["persona"] = json.loads(persona_raw) if persona_raw else {}
            return d
        return None

    def get_creator_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM creators WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            d = dict(row)
            persona_raw = d.get("persona")
            d["persona"] = json.loads(persona_raw) if persona_raw else {}
            return d
        return None

    def list_creators(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if status:
            rows = self.conn.execute(
                "SELECT * FROM creators WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (status, limit, offset)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM creators ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            persona_raw = d.get("persona")
            d["persona"] = json.loads(persona_raw) if persona_raw else {}
            results.append(d)
        return results

    def update_creator(self, creator_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        fields = []
        values = []
        for key in ("name", "platform", "language", "consent", "status"):
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        if "persona" in data:
            fields.append("persona = ?")
            values.append(json.dumps(data["persona"]))
        if not fields:
            return self.get_creator_by_id(creator_id)
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(creator_id)
        with self.transaction() as conn:
            conn.execute(f"UPDATE creators SET {', '.join(fields)} WHERE id = ?", values)
        return self.get_creator_by_id(creator_id)

    # ─── Content ───

    def create_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO content (creator_id, content_type, title, body, media_url, persona_tags, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["creator_id"], data["content_type"], data.get("title"),
                 data.get("body"), data.get("media_url"),
                 json.dumps(data.get("persona_tags", [])), data.get("status", "draft"))
            )
            content_id = cursor.lastrowid
        return self.get_content_by_id(content_id)

    def get_content_by_id(self, content_id: int) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM content WHERE id = ?", (content_id,)).fetchone()
        if row:
            d = dict(row)
            d["persona_tags"] = json.loads(d.get("persona_tags", "[]"))
            return d
        return None

    def list_content(self, creator_id: int, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if status:
            rows = self.conn.execute(
                "SELECT * FROM content WHERE creator_id = ? AND status = ? ORDER BY created_at DESC LIMIT ?",
                (creator_id, status, limit)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM content WHERE creator_id = ? ORDER BY created_at DESC LIMIT ?",
                (creator_id, limit)
            ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            d["persona_tags"] = json.loads(d.get("persona_tags", "[]"))
            results.append(d)
        return results

    def update_content_status(self, content_id: int, status: str, approved_by: Optional[int] = None) -> None:
        with self.transaction() as conn:
            if approved_by and status == "approved":
                conn.execute(
                    "UPDATE content SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (status, approved_by, content_id)
                )
            else:
                conn.execute("UPDATE content SET status = ? WHERE id = ?", (status, content_id))

    # ─── Publishing ───

    def create_publish_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO publish_queue (content_id, platform, scheduled_at, status)
                   VALUES (?, ?, ?, ?)""",
                (data["content_id"], data["platform"], data["scheduled_at"], data.get("status", "scheduled"))
            )
            entry_id = cursor.lastrowid
        row = self.conn.execute("SELECT * FROM publish_queue WHERE id = ?", (entry_id,)).fetchone()
        return dict(row)

    def get_scheduled_posts(self, status: str = "scheduled", limit: int = 100) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM publish_queue WHERE status = ? ORDER BY scheduled_at ASC LIMIT ?",
            (status, limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def update_publish_status(self, entry_id: int, data: Dict[str, Any]) -> None:
        fields = []
        values = []
        for key in ("status", "published_at", "platform_post_id", "retry_count", "error_message"):
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        if fields:
            values.append(entry_id)
            with self.transaction() as conn:
                conn.execute(f"UPDATE publish_queue SET {', '.join(fields)} WHERE id = ?", values)

    # ─── Metrics ───

    def create_metric(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.transaction() as conn:
            engagement = 0.0
            if data.get("views", 0) > 0:
                engagement = (data.get("likes", 0) + data.get("comments", 0) + data.get("shares", 0)) / data["views"]
            cursor = conn.execute(
                """INSERT INTO metrics (content_id, platform, likes, comments, shares, views, engagement_rate)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["content_id"], data["platform"], data.get("likes", 0),
                 data.get("comments", 0), data.get("shares", 0), data.get("views", 0), engagement)
            )
            metric_id = cursor.lastrowid
        row = self.conn.execute("SELECT * FROM metrics WHERE id = ?", (metric_id,)).fetchone()
        return dict(row)

    def get_metrics_for_creator(self, creator_id: int, days: int = 30) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT m.* FROM metrics m
               JOIN content c ON m.content_id = c.id
               WHERE c.creator_id = ? AND m.collected_at >= datetime('now', ?)
               ORDER BY m.collected_at DESC""",
            (creator_id, f"-{days} days")
        ).fetchall()
        return [dict(r) for r in rows]

    # ─── Finance ───

    def create_revenue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO revenue (creator_id, source, amount, currency, period_start, period_end, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["creator_id"], data["source"], data["amount"],
                 data.get("currency", "EUR"), data.get("period_start"),
                 data.get("period_end"), data.get("notes"))
            )
            revenue_id = cursor.lastrowid

            # Update ledger
            self._add_ledger_entry(conn, {
                "entry_type": "revenue",
                "reference_id": revenue_id,
                "reference_type": "revenue",
                "creator_id": data["creator_id"],
                "credit": data["amount"],
                "description": f"Revenue: {data['source']}"
            })

        row = self.conn.execute("SELECT * FROM revenue WHERE id = ?", (revenue_id,)).fetchone()
        return dict(row)

    def get_creator_balance(self, creator_id: int) -> Dict[str, Any]:
        total_revenue = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM revenue WHERE creator_id = ?",
            (creator_id,)
        ).fetchone()["total"]

        total_payouts = self.conn.execute(
            "SELECT COALESCE(SUM(net_amount), 0) as total FROM payouts WHERE creator_id = ? AND status = 'paid'",
            (creator_id,)
        ).fetchone()["total"]

        pending_payouts = self.conn.execute(
            "SELECT COALESCE(SUM(net_amount), 0) as total FROM payouts WHERE creator_id = ? AND status IN ('pending', 'approved')",
            (creator_id,)
        ).fetchone()["total"]

        return {
            "creator_id": creator_id,
            "total_revenue": total_revenue,
            "total_paid_out": total_payouts,
            "pending_payouts": pending_payouts,
            "available_balance": total_revenue - total_payouts - pending_payouts
        }

    def create_payout(self, data: Dict[str, Any]) -> Dict[str, Any]:
        commission_rate = data.get("commission_rate", settings.DEFAULT_COMMISSION_SPLIT)
        commission = round(data["amount"] * commission_rate, 2)
        net_amount = round(data["amount"] - commission, 2)

        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO payouts (creator_id, amount, commission, net_amount, status, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (data["creator_id"], data["amount"], commission, net_amount,
                 data.get("status", "pending"), data.get("notes"))
            )
            payout_id = cursor.lastrowid

            self._add_ledger_entry(conn, {
                "entry_type": "payout_request",
                "reference_id": payout_id,
                "reference_type": "payout",
                "creator_id": data["creator_id"],
                "debit": net_amount,
                "description": f"Payout request: {net_amount} EUR (commission: {commission})"
            })

        row = self.conn.execute("SELECT * FROM payouts WHERE id = ?", (payout_id,)).fetchone()
        return dict(row)

    def approve_payout(self, payout_id: int, approved_by: int) -> Dict[str, Any]:
        with self.transaction() as conn:
            conn.execute(
                "UPDATE payouts SET status = 'approved', approved_by = ?, approved_at = CURRENT_TIMESTAMP WHERE id = ?",
                (approved_by, payout_id)
            )
        row = self.conn.execute("SELECT * FROM payouts WHERE id = ?", (payout_id,)).fetchone()
        return dict(row)

    def mark_payout_paid(self, payout_id: int) -> None:
        with self.transaction() as conn:
            conn.execute(
                "UPDATE payouts SET status = 'paid', paid_at = CURRENT_TIMESTAMP WHERE id = ?",
                (payout_id,)
            )

    def _add_ledger_entry(self, conn, data: Dict[str, Any]):
        """Add a ledger entry within an existing transaction."""
        # Get current balance
        last = conn.execute(
            "SELECT balance FROM ledger WHERE creator_id = ? ORDER BY id DESC LIMIT 1",
            (data.get("creator_id"),)
        ).fetchone()
        current_balance = last["balance"] if last else 0.0

        debit = data.get("debit", 0.0)
        credit = data.get("credit", 0.0)
        new_balance = round(current_balance + credit - debit, 2)

        conn.execute(
            """INSERT INTO ledger (entry_type, reference_id, reference_type, creator_id, debit, credit, balance, description)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (data["entry_type"], data.get("reference_id"), data.get("reference_type"),
             data.get("creator_id"), debit, credit, new_balance, data.get("description"))
        )

    # ─── Recruitment ───

    def create_recruitment_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO recruitment_funnel (creator_id, stage, recruiter_id, status, notes, applied_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (data["creator_id"], data["stage"], data.get("recruiter_id"),
                 data.get("status", "active"), data.get("notes"),
                 data.get("applied_at", datetime.utcnow().isoformat()))
            )
            entry_id = cursor.lastrowid
        row = self.conn.execute("SELECT * FROM recruitment_funnel WHERE id = ?", (entry_id,)).fetchone()
        return dict(row)

    # ─── Communications ───

    def create_communication(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO communications (creator_id, template_id, channel, subject, message, direction, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["creator_id"], data.get("template_id"), data["channel"],
                 data.get("subject"), data["message"], data.get("direction", "outbound"),
                 data.get("status", "sent"))
            )
            comm_id = cursor.lastrowid
        row = self.conn.execute("SELECT * FROM communications WHERE id = ?", (comm_id,)).fetchone()
        return dict(row)

    # ─── Assistant Conversations ───

    def get_or_create_conversation(self, creator_id: int, fan_identifier: str) -> Dict[str, Any]:
        row = self.conn.execute(
            "SELECT * FROM assistant_conversations WHERE creator_id = ? AND fan_identifier = ?",
            (creator_id, fan_identifier)
        ).fetchone()
        if row:
            d = dict(row)
            d["messages"] = json.loads(d.get("messages", "[]"))
            return d

        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO assistant_conversations (creator_id, fan_identifier, messages) VALUES (?, ?, ?)",
                (creator_id, fan_identifier, "[]")
            )
            conv_id = cursor.lastrowid
        return {"id": conv_id, "creator_id": creator_id, "fan_identifier": fan_identifier, "messages": []}

    def update_conversation(self, conv_id: int, messages: List[Dict], last_suggestion: Optional[str] = None):
        with self.transaction() as conn:
            conn.execute(
                "UPDATE assistant_conversations SET messages = ?, last_suggestion = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (json.dumps(messages), last_suggestion, conv_id)
            )

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
