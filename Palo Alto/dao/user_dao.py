# dao/user_dao.py
import sqlite3
from typing import Optional, List
from connection import get_connection
from models.user import User
from dao.interfaces import IUserDAO
from dao.exceptions import DAOError


class UserDAO(IUserDAO):
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self._external_conn = conn

    # --------------- helpers ---------------

    def _conn(self) -> sqlite3.Connection:
        if self._external_conn:
            return self._external_conn
        c = get_connection()
        c.row_factory = sqlite3.Row
        return c

    def _row_to_user(self, row) -> Optional[User]:
        if row is None:
            return None
        d = dict(row)
        return User(
            id=d["id"],
            username=d["username"],
            email=d["email"],
            password=d["password"],
            age=d["age"],
            gender=d["gender"],
            last_entry_date=d.get("last_entry_date"),
            current_streak=d.get("current_streak", 0),
            longest_streak=d.get("longest_streak", 0),
        )

    # --------------- CRUD ---------------

    def create(self, user: User) -> User:
        conn = self._conn()
        try:
            cur = conn.execute(
                """
                INSERT INTO users (username, email, password, age, gender)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user.username, user.email, user.password, user.age, user.gender),
            )
            if not self._external_conn:
                conn.commit()
            user.id = cur.lastrowid
            # fetch full row (to include defaults)
            return self.find_by_id(user.id)
        except Exception as e:
            if not self._external_conn:
                conn.rollback()
            raise DAOError(f"UserDAO.create failed: {e}")

    def find_by_id(self, user_id: int) -> Optional[User]:
        conn = self._conn()
        try:
            cur = conn.execute(
                """
                SELECT id, username, email, password, age, gender,
                       last_entry_date, current_streak, longest_streak
                FROM users WHERE id = ?
                """,
                (user_id,),
            )
            row = cur.fetchone()
            return self._row_to_user(row)
        except Exception as e:
            raise DAOError(f"UserDAO.find_by_id failed: {e}")

    def find_by_email(self, email: str) -> Optional[User]:
        conn = self._conn()
        try:
            cur = conn.execute(
                """
                SELECT id, username, email, password, age, gender,
                       last_entry_date, current_streak, longest_streak
                FROM users WHERE email = ?
                """,
                (email,),
            )
            row = cur.fetchone()
            return self._row_to_user(row)
        except Exception as e:
            raise DAOError(f"UserDAO.find_by_email failed: {e}")

    def update(self, user: User) -> User:
        if user.id is None:
            raise DAOError("UserDAO.update requires user.id")
        conn = self._conn()
        try:
            conn.execute(
                """
                UPDATE users
                   SET username = ?,
                       email = ?,
                       password = ?,
                       age = ?,
                       gender = ?,
                       last_entry_date = ?,
                       current_streak = ?,
                       longest_streak = ?
                 WHERE id = ?
                """,
                (
                    user.username,
                    user.email,
                    user.password,
                    user.age,
                    user.gender,
                    user.last_entry_date,
                    user.current_streak,
                    user.longest_streak,
                    user.id,
                ),
            )
            if not self._external_conn:
                conn.commit()
            return self.find_by_id(user.id)
        except Exception as e:
            if not self._external_conn:
                conn.rollback()
            raise DAOError(f"UserDAO.update failed: {e}")

    def update_partial(self, user_id: int, **fields) -> Optional[User]:
        if not fields:
            return self.find_by_id(user_id)

        # Only allow known columns
        allowed = {
            "username",
            "email",
            "password",
            "age",
            "gender",
            "last_entry_date",
            "current_streak",
            "longest_streak",
        }
        sets = []
        values = []
        for k, v in fields.items():
            if k in allowed:
                sets.append(f"{k} = ?")
                values.append(v)

        if not sets:
            return self.find_by_id(user_id)

        sql = f"UPDATE users SET {', '.join(sets)} WHERE id = ?"
        values.append(user_id)

        conn = self._conn()
        try:
            conn.execute(sql, tuple(values))
            if not self._external_conn:
                conn.commit()
            return self.find_by_id(user_id)
        except Exception as e:
            if not self._external_conn:
                conn.rollback()
            raise DAOError(f"UserDAO.update_partial failed: {e}")

    def delete(self, user_id: int) -> None:
        conn = self._conn()
        try:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if not self._external_conn:
                conn.commit()
        except Exception as e:
            if not self._external_conn:
                conn.rollback()
            raise DAOError(f"UserDAO.delete failed: {e}")

    def list_recent(self, limit: int = 50, offset: int = 0) -> List[User]:
        conn = self._conn()
        try:
            cur = conn.execute(
                f"""
                SELECT id, username, email, password, age, gender,
                       last_entry_date, current_streak, longest_streak
                FROM users
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            rows = cur.fetchall()
            return [self._row_to_user(r) for r in rows]
        except Exception as e:
            raise DAOError(f"UserDAO.list_recent failed: {e}")
