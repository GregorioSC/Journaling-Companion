from pydantic import BaseModel
from typing import List, Optional, Dict


class PromptRequest(BaseModel):
    goal: Optional[str] = None
    k_context: int = 5


class PromptResponse(BaseModel):
    prompts: List[str]
    context_entry_ids: List[int] = []


class WeeklySummary(BaseModel):
    week_start: str
    summary: str
    insights: Dict


class InsightPatch(BaseModel):
    sentiment: Optional[float] = None
    themes: Optional[List[str]] = None
    embedding: Optional[List[float]] = None


class InsightOut(BaseModel):
    id: int
    entry_id: int
    sentiment: float
    themes: list[str]
    embedding: list[float]
    created_at: str
