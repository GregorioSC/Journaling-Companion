# services/ai_themes.py
"""
Human-friendly theme extraction for short journal entries.

- Combines KeyBERT (embedding-based) and YAKE (statistical) candidates
- Cleans and deduplicates phrases
- Heuristics to drop filler/time words and generic sentiment adjectives (no spaCy needed)
- Returns top_k short, readable themes

Requires: keybert, yake, sentence-transformers
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Iterable
import re

# --- YAKE --------------------------------------------------------------------
try:
    import yake  # type: ignore
except Exception:  # pragma: no cover
    yake = None

# --- KeyBERT -----------------------------------------------------------------
try:
    from keybert import KeyBERT  # type: ignore
except Exception:  # pragma: no cover
    KeyBERT = None  # type: ignore

# Keep a single KeyBERT instance (it loads a sentence-transformer under the hood)
_KB: Optional["KeyBERT"] = None

# ---------------------- Heuristic filters (no spaCy) -------------------------

STOPWORDS = {
    # articles/conjunctions/aux
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
    # time/fillers
    "today",
    "yesterday",
    "tonight",
    "morning",
    "afternoon",
    "evening",
    "day",
    "week",
    "month",
    "year",
    "really",
    "just",
    "like",
    "kinda",
    "sorta",
    "maybe",
    "lot",
    "stuff",
    "things",
    "thing",
    "felt",
    "feel",
    "feels",
    "feeling",
    "made",
    "make",
    "makes",
    "get",
    "got",
    "going",
    "went",
    "put",
    "puts",
    "putting",
}

# fragments we never want
BAD_FRAGMENTS = {
    "couldn",
    "couldn t",
    "couldn even",
    "even bed",
    "dont",
    "didnt",
    "im",
    "wont",
    "ill",
}

# generic sentiment adjectives (too vague as themes)
DROP_ADJECTIVES = {
    "sad",
    "happy",
    "tired",
    "mad",
    "angry",
    "upset",
    "lonely",
    "bored",
}

# keep these noun-y, meaningful mood/health words (even though sentiment-y)
ALLOW_MEANINGFUL = {
    "stress",
    "stressor",
    "anxiety",
    "panic",
    "depression",
    "burnout",
    "energy",
    "motivation",
    "sleep",
    "focus",
}

FIXUPS = [
    (r"\bcouldn\s*'?t\b", "couldn't"),
    (r"\bdon'?t\b", "don't"),
    (r"\bdidn'?t\b", "didn't"),
    (r"\bcan'?t\b", "can't"),
    (r"\bwon'?t\b", "won't"),
    (r"\bi'?m\b", "I'm"),
    (r"\byou'?re\b", "you're"),
]

TOKEN_RE = re.compile(r"[a-zA-Z']+")


def _norm(s: str) -> str:
    s = s.strip()
    for pat, rep in FIXUPS:
        s = re.sub(pat, rep, s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s)
    return s


def _is_meaningful_token(tok: str) -> bool:
    t = tok.lower()
    if t in STOPWORDS:
        return False
    if t in BAD_FRAGMENTS:
        return False
    if len(t) < 3 and t not in {"gym", "job"}:  # allow a couple short nouns
        return False
    # drop generic adjectives unless explicitly allowed
    if t in DROP_ADJECTIVES and t not in ALLOW_MEANINGFUL:
        return False
    return True


def _yake_candidates(text: str, top_n: int = 5) -> List[Tuple[str, float]]:
    if not yake:
        return []
    kw = yake.KeywordExtractor(lan="en", n=2, top=top_n, dedupLim=0.9)
    out = kw.extract_keywords(text)
    if not out:
        return []
    scores = [s for _, s in out]
    hi = max(scores) or 1.0
    return [(_norm(p), 1.0 - (s / hi)) for p, s in out]  # higher is better


def _keybert_candidates(text: str, top_n: int = 5) -> List[Tuple[str, float]]:
    global _KB
    if KeyBERT is None:
        return []
    if _KB is None:
        _KB = KeyBERT()
    cands = _KB.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        top_n=top_n,
        use_maxsum=True,
        nr_candidates=20,
    )
    return [(_norm(p), float(s)) for p, s in cands]


def _dedup_keep_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in items:
        k = x.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(x)
    return out


def _clean_phrase(p: str) -> str | None:
    """
    Clean a candidate into a short display phrase (1-2 tokens) or None to drop.
    """
    if not p:
        return None
    if p.lower() in BAD_FRAGMENTS:
        return None

    toks = [t for t in TOKEN_RE.findall(p) if _is_meaningful_token(t)]
    if not toks:
        return None

    # generic adjectives as a single token are too vague -> drop (unless allowed)
    if len(toks) == 1:
        t = toks[0].lower()
        if t in DROP_ADJECTIVES and t not in ALLOW_MEANINGFUL:
            return None
        return toks[0].lower()

    # prefer first two meaningful tokens; drop if both are still too generic
    t1, t2 = toks[0].lower(), toks[1].lower()
    if (t1 in DROP_ADJECTIVES and t1 not in ALLOW_MEANINGFUL) or (t1 in STOPWORDS):
        # try second token alone
        if t2 in DROP_ADJECTIVES and t2 not in ALLOW_MEANINGFUL:
            return None
        return t2
    if (t2 in DROP_ADJECTIVES and t2 not in ALLOW_MEANINGFUL) or (t2 in STOPWORDS):
        return t1

    return f"{t1} {t2}"


def extract_themes(text: str, top_k: int = 3) -> List[str]:
    """
    Return up to top_k short, human-friendly themes for the given entry text.
    """
    if not text or not text.strip():
        return []

    # gather candidates
    cand = []
    cand += _keybert_candidates(text, top_n=6)
    cand += _yake_candidates(text, top_n=6)

    # sort by score desc, then by shorter length
    cand.sort(key=lambda x: (x[1], -len(x[0])), reverse=True)

    cleaned: List[str] = []
    for phrase, _ in cand:
        p2 = _clean_phrase(phrase)
        if not p2:
            continue
        cleaned.append(p2)

    cleaned = _dedup_keep_order(cleaned)

    # final guard: drop any leftover noise like 'today', 'felt'
    cleaned = [c for c in cleaned if c not in STOPWORDS and c not in BAD_FRAGMENTS]

    # don’t return empty; but also don’t invent themes — empty is okay
    return cleaned[: max(1, top_k)]
