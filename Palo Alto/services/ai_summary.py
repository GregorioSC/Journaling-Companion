# services/ai_summary.py
from __future__ import annotations
import json
from datetime import datetime, timedelta, date
from collections import Counter
from typing import Dict, List, Any

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


class AISummary:
    """Weekly recap for current user, current week (Mon..Sun)."""

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
                "summary": "No entries this week.",
                "insights": {"count": 0, "avg_sentiment": 0.0, "themes": []},
                "week_start": week_start.isoformat(),
            }

        sentiments = [
            float(r.get("sentiment") or 0.0)
            for r in week_rows
            if r.get("sentiment") is not None
        ]
        avg = sum(sentiments) / max(1, len(sentiments))

        # Collect all themes
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

        common = [t for t, _ in Counter(all_themes).most_common(3)]

        # --- Build natural language summary ---
        parts: List[str] = []

        if avg >= 0.25:
            parts.append("Overall, your reflections trended positive this week.")
        elif avg <= -0.25:
            parts.append("This week carried a more negative tone overall.")
        else:
            parts.append("Your tone was fairly balanced, with ups and downs.")

        if common:
            top = common[0]
            parts.append(
                f"A recurring theme was **{top}**, which came up several times."
            )
            if len(common) > 1:
                others = ", ".join(common[1:])
                parts.append(f"Other themes included {others}.")

        parts.append(f"You wrote {len(week_rows)} entries this week.")

        return {
            "summary": " ".join(parts),
            "insights": {
                "count": len(week_rows),
                "avg_sentiment": avg,
                "themes": common,
            },
            "week_start": week_start.isoformat(),
        }
