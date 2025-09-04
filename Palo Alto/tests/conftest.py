# tests/conftest.py
import sqlite3
import pytest

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS insights;
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL,
    age        INTEGER NOT NULL CHECK (age >= 0 AND age <= 150),
    gender     TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE entries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    title      TEXT NOT NULL,
    text       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE insights (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id   INTEGER NOT NULL UNIQUE,
    sentiment  REAL NOT NULL CHECK (sentiment >= -1.0 AND sentiment <= 1.0),
    themes     TEXT NOT NULL,
    embedding  TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);
"""


@pytest.fixture()
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA_SQL)
    return c


# ---------- DAO fixtures (use injected connection) ----------
@pytest.fixture()
def user_dao(conn):
    from dao.user_dao import UserDAO

    return UserDAO(conn)


@pytest.fixture()
def entry_dao(conn):
    from dao.entry_dao import EntryDAO

    return EntryDAO(conn)


@pytest.fixture()
def insight_dao(conn):
    from dao.insight_dao import InsightDAO

    return InsightDAO(conn)


# ---------- Service fixtures ----------
@pytest.fixture()
def user_service(user_dao):
    from services.user_service import UserService

    return UserService(user_dao)


@pytest.fixture()
def entry_service(entry_dao):
    from services.entry_service import EntryService

    return EntryService(entry_dao)


@pytest.fixture()
def insight_service(insight_dao):
    from services.insight_service import InsightService

    return InsightService(insight_dao)


@pytest.fixture()
def journaling_service(conn, monkeypatch):
    """
    JournalingService opens its own connection via connection.get_connection().
    We monkeypatch that to return our in-memory conn, and we pass factories that
    bind DAOs to the SAME conn to keep it transactional in tests.
    """
    from services.journaling_service import JournalingService
    from dao.entry_dao import EntryDAO
    from dao.insight_dao import InsightDAO

    # Patch the function imported inside the service module
    import services.journaling_service as js

    monkeypatch.setattr(js, "get_connection", lambda: conn)

    return JournalingService(
        entry_dao_factory=lambda c: EntryDAO(c),
        insight_dao_factory=lambda c: InsightDAO(c),
    )


# ---------- Model factories ----------
@pytest.fixture()
def make_user():
    from models.user import User

    def _mk(
        username="alice",
        email="alice@example.com",
        password="pass123",
        age=25,
        gender="F",
        id=None,
    ):
        return User(
            id=id,
            username=username,
            email=email,
            password=password,
            age=age,
            gender=gender,
        )

    return _mk


@pytest.fixture()
def make_entry():
    from models.entry import Entry

    def _mk(user_id: int, title="Day 1", text="Hello", created_at=None, id=None):
        return Entry(
            id=id, text=text, user_id=user_id, created_at=created_at, title=title
        )

    return _mk


@pytest.fixture()
def make_insight():
    from models.insights import Insight
    from datetime import datetime

    def _mk(
        entry_id: int,
        sentiment=0.5,
        themes=None,
        embedding=None,
        created_at=None,
        id=None,
    ):
        if themes is None:
            themes = ["work"]
        if embedding is None:
            embedding = [0.1, 0.2]
        if created_at is None:
            created_at = datetime.utcnow()
        return Insight(
            id=id,
            entry_id=entry_id,
            sentiment=sentiment,
            themes=themes,
            embedding=embedding,
            created_at=created_at,
        )

    return _mk
