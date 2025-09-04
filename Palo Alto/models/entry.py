from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Entry:
    id: Optional[int]  # autoincrement
    text: str
    user_id: int
    created_at: datetime
    title: str

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
