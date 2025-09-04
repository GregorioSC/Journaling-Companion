from datetime import datetime
from typing import List, Optional


class Insight:
    def __init__(
        self,
        entry_id: int,
        sentiment: float,
        themes: List[str],
        embedding: List[float],
        created_at: datetime,
        id: Optional[int] = None,
    ):
        self._id = id
        self._entry_id = entry_id
        self._sentiment = sentiment
        self._themes = themes
        self._embedding = embedding
        self._created_at = created_at

    # id
    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    # entry_id
    @property
    def entry_id(self) -> int:
        return self._entry_id

    @entry_id.setter
    def entry_id(self, value: int):
        self._entry_id = value

    # sentiment
    @property
    def sentiment(self) -> float:
        return self._sentiment

    @sentiment.setter
    def sentiment(self, value: float):
        if not -1.0 <= value <= 1.0:
            raise ValueError("Sentiment must be between -1.0 and 1.0")
        self._sentiment = value

    # themes
    @property
    def themes(self) -> List[str]:
        return self._themes

    @themes.setter
    def themes(self, value: List[str]):
        if not isinstance(value, list):
            raise ValueError("Themes must be a list of strings")
        self._themes = value

    # embedding
    @property
    def embedding(self) -> List[float]:
        return self._embedding

    @embedding.setter
    def embedding(self, value: List[float]):
        if not all(isinstance(x, (float, int)) for x in value):
            raise ValueError("Embedding must be a list of floats")
        self._embedding = [float(x) for x in value]

    # created_at
    @property
    def created_at(self) -> datetime:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime):
        if not isinstance(value, datetime):
            raise ValueError("created_at must be a datetime object")
        self._created_at = value

    # convert object to dictionary (JSON-friendly)
    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "entry_id": self._entry_id,
            "sentiment": self._sentiment,
            "themes": self._themes,
            "embedding": self._embedding,
            "created_at": self._created_at.isoformat(),  # datetime → string
        }
