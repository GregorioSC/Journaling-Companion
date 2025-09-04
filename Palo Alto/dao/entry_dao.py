# dao/entry_dao.py
import sqlite3
from typing import Optional, List
from connection import get_connection
from models.entry import Entry
from .exceptions import DAOError  # <-- relative
from dao.interfaces import IEntryDAO

ALLOWED_FIELDS = {"title", "text", "created_at"}  # user_id stays fixed


class EntryDAO(IEntryDAO):
    def __init__(self, conn=None):
        self._external_conn = conn

    def _conn(self):
        return self._external_conn or get_connection()

    @staticmethod
    def _row_to_entry(row) -> Entry:
        return Entry(
            id=row["id"],
            text=row["text"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            title=row["title"],
        )

    def create(self, entry: Entry) -> Entry:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO entries (user_id, title, text, created_at)
                VALUES (?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
                """,
                (
                    entry.user_id,
                    entry.title,
                    entry.text,
                    getattr(entry, "created_at", None),
                ),
            )
            entry.id = cur.lastrowid
            if not self._external_conn:
                conn.commit()
                conn.close()
            return entry
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to create entry: {e}")

    def find_by_id(self, entry_id: int) -> Optional[Entry]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
            row = cur.fetchone()
            if not self._external_conn:
                conn.close()
            return self._row_to_entry(row) if row else None
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to find entry by id: {e}")

    def list_by_user(self, user_id: int, limit: int = 100) -> List[Entry]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM entries
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (user_id, limit),
            )
            rows = cur.fetchall()
            if not self._external_conn:
                conn.close()
            return [self._row_to_entry(r) for r in rows]
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to list entries by user: {e}")

    def update(self, entry: Entry) -> Entry:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE entries
                SET title = ?, text = ?, created_at = COALESCE(?, created_at)
                WHERE id = ?
            """,
                (entry.title, entry.text, getattr(entry, "created_at", None), entry.id),
            )
            if not self._external_conn:
                conn.commit()
                conn.close()
            return entry
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to update entry: {e}")

    def update_partial(self, entry_id: int, **fields) -> Optional[Entry]:
        conn = self._conn()
        try:
            if not fields:
                cur = conn.cursor()
                cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
                row = cur.fetchone()
                if not self._external_conn:
                    conn.close()
                return self._row_to_entry(row) if row else None

            cols, vals = [], []
            for k, v in fields.items():
                if k not in ALLOWED_FIELDS:
                    continue
                if k == "created_at":
                    cols.append("created_at = COALESCE(?, created_at)")
                    vals.append(v)
                else:
                    cols.append(f"{k} = ?")
                    vals.append(v)

            if not cols:
                cur = conn.cursor()
                cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
                row = cur.fetchone()
                if not self._external_conn:
                    conn.close()
                return self._row_to_entry(row) if row else None

            vals.append(entry_id)
            cur = conn.cursor()
            cur.execute(f"UPDATE entries SET {', '.join(cols)} WHERE id = ?", vals)
            cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
            row = cur.fetchone()
            if not self._external_conn:
                conn.commit()
                conn.close()
            return self._row_to_entry(row) if row else None
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to partial-update entry: {e}")

    def delete(self, entry_id: int) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            if not self._external_conn:
                conn.commit()
                conn.close()
        except sqlite3.Error as e:
            if not self._external_conn:
                conn.close()
            raise DAOError(f"Failed to delete entry: {e}")
