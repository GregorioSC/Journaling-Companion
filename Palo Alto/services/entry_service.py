# services/entry_service.py
from typing import Optional, List
from datetime import datetime, timezone

from models.entry import Entry
from models.insights import Insight

from dao.interfaces import IEntryDAO
from dao.user_dao import UserDAO
from dao.event_dao import EventDAO
from dao.insight_dao import InsightDAO

from services.ai_sentiment import AISentiment


class EntryService:
    def __init__(
        self,
        entry_dao: IEntryDAO,
        user_dao: Optional[UserDAO] = None,
        event_dao: Optional[EventDAO] = None,
        insight_dao: Optional[InsightDAO] = None,
        ai: Optional[AISentiment] = None,
    ):
        """
        Orchestrates CRUD for entries, streak updates, event logging,
        and AI analysis (sentiment/themes/embeddings).
        """
        self.entry_dao = entry_dao
        self.user_dao = user_dao or UserDAO()
        self.event_dao = event_dao or EventDAO()
        self.insight_dao = insight_dao or InsightDAO()
        self.ai = ai or AISentiment()

    # ----------------------
    # Create
    # ----------------------
    def create(self, entry: Entry) -> Entry:
        """
        Creates an entry, updates the user's streaks, logs an event,
        and stores AI analysis (sentiment, themes, embedding) for the entry.
        """
        self._validate_entry(entry)

        saved = self.entry_dao.create(entry)

        self._update_user_streak_after_entry(saved.user_id, saved.created_at)

        try:
            self.event_dao.create(
                saved.user_id, "entry.created", {"entry_id": saved.id}
            )
        except Exception:
            pass

        try:
            self._analyze_and_upsert_insight(saved)
        except Exception:

            pass

        return saved

    # ----------------------
    # Read
    # ----------------------
    def get(self, entry_id: int) -> Optional[Entry]:
        return self.entry_dao.find_by_id(entry_id)

    def list_for_user(self, user_id: int, limit: int = 100) -> List[Entry]:
        return self.entry_dao.list_by_user(user_id, limit)

    # ----------------------
    # Update
    # ----------------------
    def update_full(self, entry: Entry) -> Entry:
        self._validate_entry(entry)
        updated = self.entry_dao.update(entry)

        try:
            self._analyze_and_upsert_insight(updated)
        except Exception:
            pass

        return updated

    def update_partial(self, entry_id: int, **fields) -> Optional[Entry]:
        self._validate_entry_patch(fields)
        updated = self.entry_dao.update_partial(entry_id, **fields)

        if updated and ("text" in fields or "title" in fields):
            try:
                self._analyze_and_upsert_insight(updated)
            except Exception:
                pass

        return updated

    # ----------------------
    # Delete
    # ----------------------
    def remove(self, entry_id: int) -> None:

        try:
            self.insight_dao.delete_by_entry(entry_id)
        except Exception:
            pass
        self.entry_dao.delete(entry_id)

    # ----------------------
    # Helpers
    # ----------------------
    def reanalyze(self, entry_id: int) -> Optional[Insight]:
        """
        Public helper to (re)compute AI insight for an existing entry.
        Returns the stored Insight or None if entry not found.
        """
        entry = self.entry_dao.find_by_id(entry_id)
        if not entry:
            return None
        return self._analyze_and_upsert_insight(entry)

    def _analyze_and_upsert_insight(self, entry: Entry) -> Insight:
        """
        Runs AI (sentiment, themes, embedding) and upserts to insights table.
        """
        sentiment, themes = self.ai.analyze_entry(entry.text)
        embedding = self.ai.embed_entries([entry.text])[0]

        ins = Insight(
            id=None,
            entry_id=entry.id,
            sentiment=sentiment,
            themes=themes,
            embedding=embedding,
        )
        self.insight_dao.upsert_for_entry(ins)

        try:
            self.event_dao.create(
                entry.user_id,
                "entry.analyzed",
                {"entry_id": entry.id, "sentiment": sentiment, "themes": themes[:3]},
            )
        except Exception:
            pass

        return ins

    # ----------------------
    # Validations
    # ----------------------
    def _validate_entry(self, entry: Entry):
        if not entry.user_id:
            raise ValueError("entry.user_id is required")
        if not entry.title or not str(entry.title).strip():
            raise ValueError("entry.title is required")
        if not entry.text or not str(entry.text).strip():
            raise ValueError("entry.text is required")

    def _validate_entry_patch(self, fields: dict):
        if "title" in fields and (
            fields["title"] is None or not str(fields["title"]).strip()
        ):
            raise ValueError("title cannot be empty")
        if "text" in fields and (
            fields["text"] is None or not str(fields["text"]).strip()
        ):
            raise ValueError("text cannot be empty")

    # ----------------------
    # Streak logic
    # ----------------------
    def _update_user_streak_after_entry(self, user_id: int, created_at) -> None:
        """
        Update last_entry_date/current_streak/longest_streak when a new entry is created.
        - Counts one per calendar day (UTC).
        - Increments streak if last entry was yesterday.
        - Resets to 1 if gap >= 2 days.
        """

        if isinstance(created_at, str):
            try:
                created_dt = datetime.fromisoformat(created_at.replace("Z", ""))
            except Exception:
                created_dt = datetime.now(timezone.utc)
        elif isinstance(created_at, datetime):
            created_dt = created_at
        else:
            created_dt = datetime.now(timezone.utc)

        today = created_dt.astimezone(timezone.utc).date()

        u = self.user_dao.find_by_id(user_id)
        last_str = u.last_entry_date if u else None

        if not last_str:
            patch = dict(last_entry_date=str(today), current_streak=1, longest_streak=1)
            self.user_dao.update_partial(user_id, **patch)
            try:
                self.event_dao.create(
                    user_id, "streak.updated", {"current": 1, "longest": 1}
                )
            except Exception:
                pass
            return

        try:
            last_date = datetime.fromisoformat(last_str).date()
        except Exception:
            last_date = today

        delta = (today - last_date).days
        if delta == 0:

            return
        elif delta == 1:
            new_current = int(u.current_streak or 0) + 1
        else:
            new_current = 1

        new_longest = max(int(u.longest_streak or 0), new_current)
        patch = dict(
            last_entry_date=str(today),
            current_streak=new_current,
            longest_streak=new_longest,
        )
        self.user_dao.update_partial(user_id, **patch)
        try:
            self.event_dao.create(
                user_id,
                "streak.updated",
                {"current": new_current, "longest": new_longest},
            )
        except Exception:
            pass
