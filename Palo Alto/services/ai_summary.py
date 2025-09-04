# services/ai_summary.py
from __future__ import annotations
import json
import re
from datetime import datetime, timedelta, date
from collections import Counter
from typing import Dict, List, Any, Iterable

from dao.insight_dao import InsightDAO


def _to_dt(x) -> datetime | None:
    if x is None:
        return None
    if isinstance(x, datetime):
        return x
    s = str(x)
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        pass
    try:
        return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def _monday_of_week(today: date) -> date:
    return today - timedelta(days=today.weekday())


# ------------------------ Theme cleanup helpers -----------------------------

_STOPWORDS = {
    "the",
    "and",
    "but",
    "or",
    "so",
    "to",
    "a",
    "an",
    "in",
    "on",
    "for",
    "of",
    "with",
    "at",
    "by",
    "is",
    "it",
    "this",
    "that",
    "was",
    "were",
    "am",
    "are",
    "be",
    "been",
    "being",
    "i",
    "me",
    "my",
    "we",
    "us",
    "our",
    "you",
    "your",
    "they",
    "them",
    "their",
}

_BAD_FRAGMENTS = {
    "couldn",
    "couldn t",
    "couldn even",
    "even bed",
    "dont",
    "didnt",
    "im",
    "cant",
    "wont",
    "ive",
    "id",
    "youre",
    "ill",
}

_FIXUPS = {
    r"\bcouldn\s*'?t\b": "couldn't",
    r"\bdon'?t\b": "don't",
    r"\bdidn'?t\b": "didn't",
    r"\bcan'?t\b": "can't",
    r"\bwon'?t\b": "won't",
    r"\bi'?m\b": "I'm",
    r"\byou'?re\b": "you're",
}


def _normalize_phrase(s: str) -> str:
    s = s.strip().lower()
    # apply simple fixups
    for pat, rep in _FIXUPS.items():
        s = re.sub(pat, rep, s)
    # remove extra spaces
    s = re.sub(r"\s+", " ", s)
    return s


def _is_meaningful_token(tok: str) -> bool:
    if not tok or tok in _STOPWORDS:
        return False
    if len(tok) < 3 and tok not in {"sad", "mad"}:
        return False
    if tok in {"even", "bed"}:  # common junk from broken bigrams
        return False
    return True


def _clean_themes(raw: Iterable[str], top_k: int = 3) -> List[str]:
    """
    Take raw theme strings (often n-grams) and return a short list of human-friendly themes.
    - drops obvious fragments/stopwords
    - merges small broken n-grams into a single token when helpful
    - applies simple apostrophe fixups (couldn't, didn't)
    """
    counts: Counter[str] = Counter()

    for t in raw:
        if not t:
            continue
        t = _normalize_phrase(str(t))
        if t in _BAD_FRAGMENTS:
            continue

        # split to tokens and keep meaningful ones
        toks = [w for w in re.findall(r"[a-zA-Z']+", t) if _is_meaningful_token(w)]
        if not toks:
            continue

        # prefer single, readable words; keep short bigrams if they look natural
        candidates: List[str] = []
        if len(toks) == 1:
            candidates = [toks[0]]
        else:
            # try to keep a compact phrase like "sleep routine", "social time"
            phrase = " ".join(toks[:2])
            if 6 <= len(phrase) <= 20:
                candidates = [phrase]
            else:
                candidates = toks[:1]  # fall back to the lead token

        for c in candidates:
            counts[c] += 1

    if not counts:
        return []

    # most common, dedup close variants (simple lowercase exact here)
    result = [w for w, _ in counts.most_common(10)]
    # prune to top_k
    return result[:top_k]


def _humanize_list(items: List[str]) -> str:
    """Return 'a', 'a and b' or 'a, b and c'."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f" and {items[-1]}"


# ---------------------------------------------------------------------------


class AISummary:
    """Weekly recap for the current user (Mon..Sun)."""

    def __init__(self, insights: InsightDAO):
        self.insights = insights

    def weekly(self, user_id: int) -> Dict[str, Any]:
        today = date.today()
        week_start = _monday_of_week(today)
        window_start = datetime.combine(week_start, datetime.min.time())
        window_end = window_start + timedelta(days=7)

        rows = self.insights.get_for_user(user_id=user_id, limit=1000)

        week_rows: List[Dict[str, Any]] = []
        for r in rows:
            dt = _to_dt(r.get("created_at"))
            if dt and window_start <= dt < window_end:
                week_rows.append(r)

        if not week_rows:
            return {
                "summary": "No entries this week. If you’d like, jot one small note about today—two sentences is plenty.",
                "insights": {"count": 0, "avg_sentiment": 0.0, "themes": []},
                "week_start": week_start.isoformat(),
            }

        sentiments = [
            float(r.get("sentiment") or 0.0)
            for r in week_rows
            if r.get("sentiment") is not None
        ]
        avg = sum(sentiments) / max(1, len(sentiments))

        # Gather all raw themes
        all_themes: List[str] = []
        for r in week_rows:
            th = r.get("themes")
            if isinstance(th, str):
                try:
                    th = json.loads(th)
                except Exception:
                    th = []
            if isinstance(th, list):
                all_themes.extend([str(x) for x in th])

        clean = _clean_themes(all_themes, top_k=3)

        # --- Build natural, supportive summary ---
        sentences: List[str] = []

        if avg >= 0.25:
            sentences.append(
                "This week generally felt positive—nice work staying grounded."
            )
        elif avg <= -0.25:
            sentences.append(
                "This week felt a bit heavier overall. Thanks for showing up anyway."
            )
        else:
            sentences.append(
                "Your tone was fairly balanced this week—some highs, some lows."
            )

        if clean:
            sentences.append(
                f"I noticed a recurring theme around *{_humanize_list(clean)}*."
            )

        sentences.append(
            f"You logged {len(week_rows)} entries. That consistency matters."
        )

        summary = " ".join(sentences)

        return {
            "summary": summary,
            "insights": {
                "count": len(week_rows),
                "avg_sentiment": avg,
                "themes": clean,
            },
            "week_start": week_start.isoformat(),
        }
