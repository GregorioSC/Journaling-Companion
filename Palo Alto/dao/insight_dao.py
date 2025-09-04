# dao/insight_dao.py
import json
import sqlite3
from typing import Optional, List, Any, Dict
from datetime import datetime
from connection import get_connection
from models.insights import Insight
from .exceptions import DAOError
from dao.interfaces import IInsightDAO

ALLOWED_FIELDS = {"sentiment", "themes", "embedding", "created_at"}


def _dt_to_db(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _db_to_dt(value: Any) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.utcnow()


def _maybe_load_json(v: Any):
    if v is None:
        return None
    if isinstance(v, (list, dict)):
        return v
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return None
    return None


class InsightDAO(IInsightDAO):
    def __init__(self, conn=None):
        self._external_conn = conn

    def _conn(self):
        return self._external_conn or get_connection()

    @staticmethod
    def _row_to_insight(row) -> Insight:
        return Insight(
            id=row["id"],
            entry_id=row["entry_id"],
            sentiment=row["sentiment"],
            themes=json.loads(row["themes"]),
            embedding=json.loads(row["embedding"]),
            created_at=_db_to_dt(row["created_at"]),
        )

    def get_for_user(self, user_id: int, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Return recent entries for this user joined with their insight.
        Each item:
        {
          "entry_id": int, "text": str, "created_at": str,
          "sentiment": float | None, "themes": list[str] | None,
          "embedding": list[float] | None
        }
        """
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT
                    e.id         AS entry_id,
                    e.text       AS text,
                    e.created_at AS created_at,
                    i.sentiment  AS sentiment,
                    i.themes     AS themes,
                    i.embedding  AS embedding
                FROM entries e
                LEFT JOIN insights i ON i.entry_id = e.id
                WHERE e.user_id = ?
                ORDER BY e.created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            rows = cur.fetchall()
            if not self._external_conn:
                conn.close()
            out: List[Dict[str, Any]] = []
            for r in rows:
                out.append(
                    {
                        "entry_id": r["entry_id"],
                        "text": r["text"],
                        "created_at": r["created_at"],
                        "sentiment": r["sentiment"],
                        "themes": _maybe_load_json(r["themes"]),
                        "embedding": _maybe_load_json(r["embedding"]),
                    }
                )
            return out
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to get insights for user: {e}")

    def upsert_for_entry(self, insight: Insight) -> Insight:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO insights (entry_id, sentiment, themes, embedding, created_at)
                VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
                ON CONFLICT(entry_id) DO UPDATE SET
                    sentiment = excluded.sentiment,
                    themes    = excluded.themes,
                    embedding = excluded.embedding,
                    created_at= excluded.created_at
                """,
                (
                    insight.entry_id,
                    insight.sentiment,
                    json.dumps(insight.themes),
                    json.dumps(insight.embedding),
                    _dt_to_db(getattr(insight, "created_at", None)),
                ),
            )
            if not self._external_conn:
                conn.commit()
                conn.close()
            return insight
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to upsert insight: {e}")

    def find_by_entry(self, entry_id: int) -> Optional[Insight]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM insights WHERE entry_id = ?", (entry_id,))
            row = cur.fetchone()
            if not self._external_conn:
                conn.close()
            return self._row_to_insight(row) if row else None
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to find insight by entry: {e}")

    def find_by_id(self, insight_id: int) -> Optional[Insight]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM insights WHERE id = ?", (insight_id,))
            row = cur.fetchone()
            if not self._external_conn:
                conn.close()
            return self._row_to_insight(row) if row else None
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to find insight by id: {e}")

    def update_partial(self, entry_id: int, **fields) -> Optional[Insight]:
        conn = self._conn()
        try:
            if not fields:
                cur = conn.cursor()
                cur.execute("SELECT * FROM insights WHERE entry_id = ?", (entry_id,))
                row = cur.fetchone()
                if not self._external_conn:
                    conn.close()
                return self._row_to_insight(row) if row else None

            cols, vals = [], []
            for k, v in fields.items():
                if k not in ALLOWED_FIELDS:
                    continue
                if k == "themes":
                    cols.append("themes = ?")
                    vals.append(json.dumps(v))
                elif k == "embedding":
                    cols.append("embedding = ?")
                    vals.append(json.dumps(v))
                elif k == "created_at":
                    cols.append("created_at = COALESCE(?, created_at)")
                    vals.append(_dt_to_db(v))
                else:  # sentiment
                    cols.append("sentiment = ?")
                    vals.append(v)

            if not cols:
                cur = conn.cursor()
                cur.execute("SELECT * FROM insights WHERE entry_id = ?", (entry_id,))
                row = cur.fetchone()
                if not self._external_conn:
                    conn.close()
                return self._row_to_insight(row) if row else None

            vals.append(entry_id)
            cur = conn.cursor()
            cur.execute(
                f"UPDATE insights SET {', '.join(cols)} WHERE entry_id = ?", vals
            )
            cur.execute("SELECT * FROM insights WHERE entry_id = ?", (entry_id,))
            row = cur.fetchone()
            if not self._external_conn:
                conn.commit()
                conn.close()
            return self._row_to_insight(row) if row else None
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to partial-update insight: {e}")

    def delete_by_entry(self, entry_id: int) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM insights WHERE entry_id = ?", (entry_id,))
            if not self._external_conn:
                conn.commit()
                conn.close()
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to delete insight by entry: {e}")

    def delete(self, insight_id: int) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM insights WHERE id = ?", (insight_id,))
            if not self._external_conn:
                conn.commit()
                conn.close()
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to delete insight: {e}")

    def list_recent(self, limit: int = 100, offset: int = 0) -> List[Insight]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM insights
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            rows = cur.fetchall()
            if not self._external_conn:
                conn.close()
            return [self._row_to_insight(r) for r in rows]
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to list recent insights: {e}")
