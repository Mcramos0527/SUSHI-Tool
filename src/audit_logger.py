"""
Audit Logger — SUSHI Tool
Immutable audit trail for all user queries and data access events.

IAM Requirement: Every data access event must be logged with:
- Who accessed (user_id, role)
- What they queried (natural language + order reference)
- When (UTC timestamp)
- What was returned (response summary)

This log is compliance evidence for:
- SOX access audits
- Data governance reviews
- Security incident investigations
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

AUDIT_LOG_PATH = Path("logs/audit_trail.jsonl")


class AuditLogger:
    """
    Writes immutable audit log entries for every SUSHI Tool interaction.

    Log format: JSONL (one JSON object per line)
    Each entry is append-only — no modification or deletion.
    """

    def __init__(self):
        AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Audit logger initialized — log path: {AUDIT_LOG_PATH}")

    def log_query(self, user_id: str, user_role: str, query: str, timestamp: str):
        """Log an incoming user query."""
        entry = {
            "event_type": "QUERY_RECEIVED",
            "timestamp": timestamp,
            "user_id": user_id,
            "user_role": user_role,
            "query": query,
            "session_id": self._generate_session_id(user_id, timestamp)
        }
        self._write(entry)

    def log_response(self, user_id: str, query: str, response_summary: str,
                     order_number: str | None, timestamp: str):
        """Log the response returned to the user."""
        entry = {
            "event_type": "RESPONSE_DELIVERED",
            "timestamp": timestamp,
            "user_id": user_id,
            "order_number": order_number,
            "query_summary": query[:100],
            "response_summary": response_summary,
            "data_accessed": order_number is not None
        }
        self._write(entry)

    def log_blocked_access(self, user_id: str, user_role: str,
                           field_requested: str, timestamp: str):
        """Log when a user attempts to access a blocked field."""
        entry = {
            "event_type": "ACCESS_BLOCKED",
            "timestamp": timestamp,
            "user_id": user_id,
            "user_role": user_role,
            "field_requested": field_requested,
            "action": "DENIED — field not permitted for role"
        }
        self._write(entry)
        logger.warning(f"ACCESS BLOCKED — User: {user_id} | Field: {field_requested}")

    def log_session_start(self, user_id: str, user_role: str, timestamp: str):
        """Log session initiation."""
        entry = {
            "event_type": "SESSION_START",
            "timestamp": timestamp,
            "user_id": user_id,
            "user_role": user_role
        }
        self._write(entry)

    def log_session_end(self, user_id: str, query_count: int, timestamp: str):
        """Log session termination."""
        entry = {
            "event_type": "SESSION_END",
            "timestamp": timestamp,
            "user_id": user_id,
            "total_queries": query_count
        }
        self._write(entry)

    def _write(self, entry: dict):
        """Append entry to audit log — immutable, append-only."""
        try:
            with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            # Audit failures are critical — log to system logger
            logger.critical(f"AUDIT LOG FAILURE: {e} | Entry: {entry}")

    def _generate_session_id(self, user_id: str, timestamp: str) -> str:
        """Generate a session identifier."""
        return f"{user_id}-{timestamp[:10]}-{hash(timestamp) % 10000:04d}"
