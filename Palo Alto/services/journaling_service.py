# services/journaling_service.py
import sqlite3
from typing import Optional
from connection import get_connection
from dao.interfaces import IEntryDAO, IInsightDAO
from models.entry import Entry
from models.insights import Insight


class JournalingService:
    """
    Transactional flows that touch multiple DAOs.
    Pass DAOs that can accept an injected connection (your DAOs support this).
    """

    def __init__(self, entry_dao_factory, insight_dao_factory):
        """
        entry_dao_factory: callable(conn) -> IEntryDAO
        insight_dao_factory: callable(conn) -> IInsightDAO
        """
        self._entry_dao_factory = entry_dao_factory
        self._insight_dao_factory = insight_dao_factory

    def create_entry_with_insight(self, entry: Entry, insight: Insight) -> Entry:
        """
        Create an entry and its insight atomically:
        - If any step fails, nothing is written.
        """
        conn = get_connection()
        try:
            # start a transaction (sqlite autocommit off once a write occurs)
            entry_dao = self._entry_dao_factory(conn)
            insight_dao = self._insight_dao_factory(conn)

            # create entry
            saved_entry = entry_dao.create(entry)

            # attach entry_id to the insight, then upsert
            insight.entry_id = saved_entry.id
            insight_dao.upsert_for_entry(insight)

            conn.commit()
            return saved_entry
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_entry_and_insight(
        self,
        entry_id: int,
        entry_patch: Optional[dict] = None,
        insight_patch: Optional[dict] = None,
    ):
        """
        Atomically patch an entry and its insight.
        """
        conn = get_connection()
        try:
            entry_dao = self._entry_dao_factory(conn)
            insight_dao = self._insight_dao_factory(conn)

            if entry_patch:
                entry_dao.update_partial(entry_id, **entry_patch)

            if insight_patch:
                insight_dao.update_partial(entry_id, **insight_patch)

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
