# services/insight_service.py
from typing import Optional, List
from dao.interfaces import IInsightDAO
from models.insights import Insight


class InsightService:
    def __init__(self, insight_dao: IInsightDAO):
        self.insight_dao = insight_dao

    def upsert_for_entry(self, insight: Insight) -> Insight:
        self._validate_insight(insight)
        return self.insight_dao.upsert_for_entry(insight)

    def get_for_entry(self, entry_id: int) -> Optional[Insight]:
        return self.insight_dao.find_by_entry(entry_id)

    def get_by_id(self, insight_id: int) -> Optional[Insight]:
        return self.insight_dao.find_by_id(insight_id)

    def update_partial(self, entry_id: int, **fields) -> Optional[Insight]:
        self._validate_patch(fields)
        return self.insight_dao.update_partial(entry_id, **fields)

    def delete_by_entry(self, entry_id: int) -> None:
        self.insight_dao.delete_by_entry(entry_id)

    def delete(self, insight_id: int) -> None:
        self.insight_dao.delete(insight_id)

    def list_recent(self, limit: int = 100, offset: int = 0) -> List[Insight]:
        return self.insight_dao.list_recent(limit=limit, offset=offset)

    # --- validations ---
    def _validate_insight(self, insight: Insight):
        if insight.entry_id is None:
            raise ValueError("insight.entry_id is required")
        if not (-1.0 <= float(insight.sentiment) <= 1.0):
            raise ValueError("insight.sentiment must be between -1.0 and 1.0")
        if not isinstance(insight.themes, list):
            raise ValueError("insight.themes must be a list[str]")
        if not isinstance(insight.embedding, list):
            raise ValueError("insight.embedding must be a list[float]")

    def _validate_patch(self, fields: dict):
        if "sentiment" in fields and not (-1.0 <= float(fields["sentiment"]) <= 1.0):
            raise ValueError("sentiment must be between -1.0 and 1.0")
        if "themes" in fields and not isinstance(fields["themes"], list):
            raise ValueError("themes must be a list[str]")
        if "embedding" in fields and not isinstance(fields["embedding"], list):
            raise ValueError("embedding must be a list[float]")
