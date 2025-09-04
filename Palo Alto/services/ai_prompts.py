# services/ai_prompts.py
"""
Context-aware prompt generator using an instruction-tuned model (FLAN-T5).
Generates short, varied, human-sounding reflection questions.

This version is DAO-flexible:
- Works with EntryDAO.list_recent_by_user(...) if present
- Falls back to EntryDAO.list_by_user(...)
- Or filters EntryDAO.list_recent(...) by user_id

Requires: transformers, torch, sentencepiece, safetensors
"""

from __future__ import annotations
import random
import re
from typing import List, Sequence, Any, Optional

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from dao.entry_dao import EntryDAO

MODEL_NAME = "google/flan-t5-base"  # lightweight instruction-tuned model

# Decoding settings for variety without going off the rails
GEN_CFG = {
    "do_sample": True,
    "temperature": 0.95,  # jittered slightly per call
    "top_p": 0.9,
    "top_k": 60,
    "repetition_penalty": 1.12,
    "max_new_tokens": 80,
    "num_return_sequences": 1,
}


def _strip_bullets(line: str) -> str:
    # remove "1. ", "- ", "* ", "• ", etc.
    return re.sub(r"^\s*(?:\d+[\).\]]\s*|[-*•]\s*)", "", line).strip()


def _jaccard(a: str, b: str) -> float:
    ta = set(re.findall(r"[a-zA-Z']{2,}", a.lower()))
    tb = set(re.findall(r"[a-zA-Z']{2,}", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _get_field(obj: Any, key: str, default: Any = None) -> Any:
    """Access obj.key or obj['key'] interchangeably."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class AIPrompts:
    def __init__(self, entry_dao: Optional[EntryDAO] = None):
        self._tok = None
        self._model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self.entries = entry_dao or EntryDAO()

    # Lazy-load model to keep startup snappy
    def _ensure_loaded(self):
        if self._tok is None or self._model is None:
            self._tok = AutoTokenizer.from_pretrained(MODEL_NAME)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
            self._model.to(self._device)
            self._model.eval()

    # ---- DAO-flexible fetch -------------------------------------------------

    def _fetch_recent_for_user(self, user_id: int, limit: int = 50) -> List[Any]:
        """
        Try common DAO shapes without crashing:
        - list_recent_by_user(user_id, limit=?)
        - list_by_user(user_id)
        - list_recent(limit=?), then filter by user_id
        """
        # 1) list_recent_by_user
        if hasattr(self.entries, "list_recent_by_user"):
            try:
                return self.entries.list_recent_by_user(user_id=user_id, limit=limit)  # type: ignore[attr-defined]
            except Exception:
                pass

        # 2) list_by_user
        if hasattr(self.entries, "list_by_user"):
            try:
                rows = self.entries.list_by_user(user_id=user_id)  # type: ignore[attr-defined]
                # If there's a lot, trim to most recent-ish order if available
                return rows[:limit] if isinstance(rows, list) else rows
            except Exception:
                pass

        # 3) list_recent (filter client-side)
        if hasattr(self.entries, "list_recent"):
            try:
                rows = self.entries.list_recent(limit=max(2000, limit))  # type: ignore[attr-defined]
                return [r for r in rows if _get_field(r, "user_id") == user_id][:limit]
            except Exception:
                pass

        return []

    # ------------------------------------------------------------------------

    def _sample_context_snippets(self, user_id: int, k_entries: int = 5) -> List[str]:
        """
        Pull recent entries for the user, then sample a few varied snippets.
        Always include the most recent so prompts feel current.
        """
        rows = self._fetch_recent_for_user(user_id=user_id, limit=50)
        if not rows:
            return []

        # Assume rows are already recent-first; safest we can do without strict schema.
        texts = [_get_field(r, "text", "") for r in rows]
        texts = [t.strip() for t in texts if t and t.strip()]
        if not texts:
            return []

        latest = texts[0]
        pool = texts[1:15] if len(texts) > 1 else []
        random.shuffle(pool)
        pick = [latest] + pool[: max(0, min(k_entries - 1, len(pool)))]

        # Trim very long notes to keep instruction short
        trimmed = []
        for t in pick:
            if len(t) > 420:
                head = t[:210]
                tail = t[-120:]
                t = head + " … " + tail
            trimmed.append(t)
        return trimmed

    def suggest(
        self, *, user_id: int, k: int = 5, goal_hint: Optional[str] = None
    ) -> List[str]:
        """
        Generate K short reflection questions grounded in the user's recent entries.
        """
        self._ensure_loaded()

        context_snips = self._sample_context_snippets(user_id, k_entries=5)
        context_block = (
            "No prior notes available."
            if not context_snips
            else "\n".join(f"- {s}" for s in context_snips)
        )

        # Add a little stylistic variety
        tone = random.choice(["supportive", "practical", "curious"])
        k = max(3, min(7, k))

        instruction = (
            f"You are a {tone} journaling coach.\n"
            f"Based on the user's recent notes, craft {k} short, distinct reflection questions. "
            "Each should be actionable and specific; avoid repeating phrases. "
            "Keep every question to one sentence.\n"
            + (f"User goal/hint: {goal_hint}\n" if goal_hint else "")
            + "Recent notes:\n"
            f"{context_block}\n\n"
            "Return only the questions, each on its own line."
        )

        # Jitter temperature slightly for freshness
        gcfg = GEN_CFG.copy()
        jitter = random.uniform(-0.1, 0.1)
        gcfg["temperature"] = max(0.8, min(1.1, GEN_CFG["temperature"] + jitter))

        inputs = self._tok(instruction, return_tensors="pt").to(self._device)
        with torch.no_grad():
            out = self._model.generate(**inputs, **gcfg)

        text = self._tok.decode(out[0], skip_special_tokens=True)

        # Split lines, clean bullets and numbers
        lines = [_strip_bullets(s) for s in text.splitlines()]
        lines = [s for s in lines if s and len(s) > 3]

        # De-dup by Jaccard similarity
        final: List[str] = []
        for s in lines:
            if all(_jaccard(s, t) < 0.6 for t in final):
                final.append(s)
            if len(final) >= k:
                break

        # Fallback bank if model returns too few
        if len(final) < k:
            bank = [
                "What is a 5-minute step you can take next?",
                "Who or what made today a little easier?",
                "What felt heavy or light today, and why?",
                "What boundary could protect your energy this week?",
                "What small win are you grateful for today?",
                "What would make tomorrow 1% better?",
            ]
            random.shuffle(bank)
            for q in bank:
                if all(_jaccard(q, t) < 0.6 for t in final):
                    final.append(q)
                if len(final) >= k:
                    break

        return final
