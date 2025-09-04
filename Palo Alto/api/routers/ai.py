# api/routers/ai.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List, Optional
from datetime import datetime

from api.deps import get_current_user
from api.schemas.insight import PromptRequest, PromptResponse, WeeklySummary
from services.ai_sentiment import AISentiment
from services.ai_prompts import AIPrompts
from services.ai_summary import AISummary
from dao.insight_dao import InsightDAO
from dao.entry_dao import EntryDAO
from models.insights import Insight

router = APIRouter(prefix="/ai", tags=["ai"])

_ai = AISentiment()
_insights = InsightDAO()
_entries = EntryDAO()
_prompter = AIPrompts(_ai, _insights)
_summarizer = AISummary(_insights)


def _get_field(obj: Any, key: str, default: Any = None) -> Any:
    """Access obj.key or obj[key] interchangeably."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _fetch_entry(entry_id: int) -> Optional[Any]:
    """
    Try common DAO method names so we don't crash on a name mismatch.
    Returns the entry row/model or None.
    """
    if hasattr(_entries, "find_by_id"):
        try:
            return _entries.find_by_id(entry_id)  # type: ignore[attr-defined]
        except Exception:
            pass
    if hasattr(_entries, "get_by_id"):
        try:
            return _entries.get_by_id(entry_id)  # type: ignore[attr-defined]
        except Exception:
            pass
    return None


@router.post("/prompt", response_model=PromptResponse)
def make_prompts(body: PromptRequest, current=Depends(get_current_user)):
    prompts, ctx_ids = _prompter.generate(current.id, body.goal, body.k_context)
    return PromptResponse(prompts=prompts, context_entry_ids=ctx_ids)


@router.get("/summary/weekly", response_model=WeeklySummary)
def weekly_summary(current=Depends(get_current_user)):
    data = _summarizer.weekly(current.id)
    return WeeklySummary(
        week_start=data.get("week_start"),
        summary=data["summary"],
        insights=data["insights"],
    )


@router.post("/entries/{entry_id}/analyze")
def analyze_entry(entry_id: int, current=Depends(get_current_user)):
    row = _fetch_entry(entry_id)
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Enforce ownership
    user_id = _get_field(row, "user_id")
    if user_id != current.id:
        raise HTTPException(status_code=404, detail="Entry not found")

    text = _get_field(row, "text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Entry has no text to analyze")

    # Run AI
    sentiment, themes = _ai.analyze_entry(text)
    emb = _ai.embed_entries([text])[0]

    insight = Insight(
        id=None,
        entry_id=entry_id,
        sentiment=float(sentiment),
        themes=list(themes or []),
        embedding=list(emb or []),
        created_at=datetime.utcnow(),
    )
    _insights.upsert_for_entry(insight)

    return {"entry_id": entry_id, "sentiment": sentiment, "themes": themes}


@router.post("/backfill")
def backfill_current_user(current=Depends(get_current_user)):
    """
    Analyze all existing entries for this user (creates insights for each).
    """
    rows: List[Any] = []
    if hasattr(_entries, "list_recent_by_user"):
        rows = _entries.list_recent_by_user(user_id=current.id, limit=2000)  # type: ignore[attr-defined]
    elif hasattr(_entries, "list_by_user"):
        rows = _entries.list_by_user(user_id=current.id)  # type: ignore[attr-defined]
    else:
        if hasattr(_entries, "list_recent"):
            rows = _entries.list_recent(limit=2000)  # type: ignore[attr-defined]
            rows = [r for r in rows if _get_field(r, "user_id") == current.id]

    count = 0
    for r in rows:
        text = _get_field(r, "text", "")
        entry_id = _get_field(r, "id")
        if not text or entry_id is None:
            continue

        sentiment, themes = _ai.analyze_entry(text)
        emb = _ai.embed_entries([text])[0]
        insight = Insight(
            id=None,
            entry_id=int(entry_id),
            sentiment=float(sentiment),
            themes=list(themes or []),
            embedding=list(emb or []),
            created_at=datetime.utcnow(),
        )
        _insights.upsert_for_entry(insight)
        count += 1

    return {"ok": True, "analyzed": count}
