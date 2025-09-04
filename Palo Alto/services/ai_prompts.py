# services/ai_prompts.py
from __future__ import annotations
import json
import random
from typing import List, Tuple, Dict, Any
import numpy as np

from services.ai_sentiment import AISentiment
from dao.insight_dao import InsightDAO

# --- Rotating prompt bank used when context is sparse/empty ---
PROMPT_BANK = [
    "What drained your energy today, and what restored it?",
    "Which moment would you like to remember from today?",
    "What’s one belief that helped or hurt you today?",
    "Where did you feel most at ease?",
    "What did you avoid today, and why?",
    "Who supported you recently, and how could you thank them?",
    "What small question are you sitting with right now?",
    "If today had a headline, what would it be?",
    "What would ‘1% better’ look like tomorrow?",
    "What do you want to let go of before bed?",
    "What gave you a spark of curiosity?",
    "What did your body need today?",
    "What was unexpectedly harder than you thought?",
    "Where did you show courage, even if small?",
    "What would be a kind next step for yourself?",
]

GRATITUDE_TEMPLATES = [
    "Name one small win you’re grateful for today.",
    "What quietly went right today?",
    "Who or what made today a little easier?",
]

ACTION_TEMPLATES = [
    "What’s one tiny action you’ll try tomorrow?",
    "What is a 5-minute step you can take next?",
    "What would help you start gently tomorrow?",
]


def _cosine(a: List[float], b: List[float]) -> float:
    A = np.asarray(a, dtype=float)
    B = np.asarray(b, dtype=float)
    denom = float(np.linalg.norm(A) * np.linalg.norm(B))
    return float((A @ B) / denom) if denom else 0.0


class AIPrompts:
    """
    Generates reflective prompts using nearest past entries (by embedding),
    and rotates a bank of prompts when context is sparse.
    """

    def __init__(self, ai: AISentiment, insights: InsightDAO):
        self.ai = ai
        self.insights = insights

    def _decode_embedding(self, v) -> List[float] | None:
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return None
        if isinstance(v, list):
            return v
        return None

    def _decode_themes(self, v) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            try:
                out = json.loads(v)
                return out if isinstance(out, list) else []
            except Exception:
                return []
        if isinstance(v, list):
            return [str(x) for x in v]
        return []

    def retrieve_context(
        self, user_id: int, query: str, k: int = 5
    ) -> List[Dict[str, Any]]:
        qv = self.ai.embed_query(query)
        rows = self.insights.get_for_user(user_id=user_id, limit=300)
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for r in rows:
            emb = self._decode_embedding(r.get("embedding"))
            if emb:
                sim = _cosine(qv, emb)
                scored.append((sim, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:k]]

    def _sparse_fallback(self, n: int = 3) -> List[str]:
        """Return n distinct prompts from the rotating bank."""
        n = max(1, min(n, len(PROMPT_BANK)))
        return random.sample(PROMPT_BANK, n)

    def generate(
        self, user_id: int, goal: str | None, k_context: int = 5
    ) -> Tuple[List[str], List[int]]:
        goal = (goal or "daily reflection").strip()
        ctx = self.retrieve_context(user_id, goal, k_context)

        ctx_themes: List[str] = []
        for r in ctx:
            ctx_themes.extend(self._decode_themes(r.get("themes")))
        has_themes = any(t for t in ctx_themes)

        if len(ctx) == 0 or not has_themes:

            return (
                self._sparse_fallback(3),
                [] if len(ctx) == 0 else [int(r["entry_id"]) for r in ctx],
            )

        top = ctx[0]
        themes = [t for t in self._decode_themes(top.get("themes")) if t]
        prompts: List[str] = []

        if themes:
            t = themes[0]
            t_disp = f"“{t}”" if " " in t else t
            prompts.append(f"Today, did {t_disp} feel better, worse, or the same?")

        vals = [float(r.get("sentiment") or 0.0) for r in ctx]
        avg = sum(vals) / max(1, len(vals))
        if avg < 0:
            prompts.append("Where did you find a small moment of relief today?")
        else:
            prompts.append(random.choice(GRATITUDE_TEMPLATES))

        prompts.append(random.choice(ACTION_TEMPLATES))

        entry_ids = [int(r["entry_id"]) for r in ctx if r.get("entry_id") is not None]

        seen = set()
        deduped = []
        for p in prompts:
            if p not in seen:
                deduped.append(p)
                seen.add(p)
            if len(deduped) == 3:
                break
        return deduped, entry_ids
