from pydantic import BaseModel
from typing import Optional


class EntryCreate(BaseModel):
    user_id: int
    title: str
    text: str


class EntryPatch(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None


class EntryOut(BaseModel):
    id: int
    user_id: int
    title: str
    text: str
    created_at: str
