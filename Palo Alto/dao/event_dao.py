# dao/event_dao.py
import sqlite3, json
from typing import Optional, Dict, Any
from connection import get_connection


class EventDAO:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self._external_conn = conn

    def _conn(self):
        return self._external_conn or get_connection()

    def create(
        self, user_id: int, type_: str, meta: Dict[str, Any] | None = None
    ) -> None:
        meta_json = json.dumps(meta or {})
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO events (user_id, type, meta) VALUES (?, ?, ?)",
                (user_id, type_, meta_json),
            )
            if not self._external_conn:
                conn.commit()
        except Exception as e:
            if not self._external_conn:
                conn.rollback()
            raise
        finally:
            if not self._external_conn:
                conn.close()
