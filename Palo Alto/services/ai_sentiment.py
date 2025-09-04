# services/ai_sentiment.py
from typing import List, Tuple
import re
from collections import Counter

from sentence_transformers import SentenceTransformer
from transformers import pipeline

_EMB_MODEL = None
_SENT_PIPE = None


def _get_embedder():
    """Lazy-load the embedding model (e5-base). Produces 768-dim vectors."""
    global _EMB_MODEL
    if _EMB_MODEL is None:
        _EMB_MODEL = SentenceTransformer("intfloat/e5-base")
    return _EMB_MODEL


def _get_sentiment():
    """Lazy-load the sentiment classifier (SST-2)."""
    global _SENT_PIPE
    if _SENT_PIPE is None:
        _SENT_PIPE = pipeline(
            task="sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
    return _SENT_PIPE


class AISentiment:
    """
    Wraps embedding + sentiment + lightweight theme extraction for AI features.
    """

    def __init__(self, emb_model_name: str = "intfloat/e5-base"):
        self._emb_model_name = (
            emb_model_name  # kept for compatibility if you inspect it
        )

    # ---------- Embeddings ----------
    def embed_entries(self, texts: List[str]) -> List[List[float]]:
        emb = _get_embedder()
        to_encode = [
            f"passage: {t}" if not str(t).startswith("passage:") else str(t)
            for t in texts
        ]
        return emb.encode(to_encode, normalize_embeddings=True).tolist()

    def embed_query(self, q: str) -> List[float]:
        emb = _get_embedder()
        text = f"query: {q}" if not str(q).startswith("query:") else str(q)
        return emb.encode([text], normalize_embeddings=True)[0].tolist()

    # ---------- Sentiment + themes ----------
    def analyze_entry(self, text: str) -> Tuple[float, List[str]]:
        """
        Returns (sentiment in [-1, 1], top themes list).
        """
        pipe = _get_sentiment()

        text = (text or "").strip()
        if not text:
            return 0.0, []

        out = pipe(text, truncation=True)[
            0
        ]  # {'label': 'POSITIVE'|'NEGATIVE', 'score': ...}
        label = (out.get("label") or "").upper()
        score = float(out.get("score") or 0.0)
        signed = score if "POS" in label else -score

        return float(signed), self._themes(text)

    def _themes(self, text: str, k: int = 5) -> List[str]:
        """
        Smarter keyword-ish themes:
        - Lowercase alphas, remove rich stopwords (“today”, “just”, “made”, etc.)
        - Build unigrams + bigrams
        - Rank by frequency, prefer longer n-grams
        """
        tokens = [w.lower() for w in re.findall(r"[a-zA-Z]{2,}", text)]
        if not tokens:
            return []

        stop = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "if",
            "then",
            "so",
            "to",
            "of",
            "in",
            "on",
            "at",
            "by",
            "for",
            "from",
            "as",
            "is",
            "am",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "it",
            "its",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "hers",
            "our",
            "their",
            "with",
            "about",
            "into",
            "over",
            "after",
            "before",
            "up",
            "down",
            "out",
            "off",
            "than",
            "too",
            "very",
            "also",
            "what",
            "when",
            "where",
            "which",
            "who",
            "how",
            "why",
            # journaling fillers
            "today",
            "yesterday",
            "tomorrow",
            "now",
            "just",
            "really",
            "like",
            "well",
            "maybe",
            "kinda",
            "sorta",
            "literally",
            # common verbs that read weird as “themes”
            "make",
            "made",
            "makes",
            "do",
            "did",
            "done",
            "doing",
            "go",
            "went",
            "gone",
            "going",
            "get",
            "got",
            "getting",
            "feel",
            "feels",
            "felt",
            "think",
            "thinks",
            "thought",
            "say",
            "says",
            "said",
            "want",
            "wants",
            "wanted",
            "need",
            "needs",
            "needed",
            "try",
            "tries",
            "tried",
            "have",
            "has",
            "had",
            "love",
            "loves",
            "loved",
            "life",
            "day",
            "today",
        }

        unigrams = [t for t in tokens if t not in stop and len(t) > 2]

        bigrams = [
            " ".join(pair)
            for pair in zip(unigrams, unigrams[1:])
            if all(len(w) > 2 for w in pair)
        ]

        counts = Counter(unigrams)
        bi_counts = Counter(bigrams)

        scores = {}
        for w, c in counts.items():
            scores[w] = scores.get(w, 0) + c
        for w, c in bi_counts.items():
            scores[w] = scores.get(w, 0) + (c * 1.5)

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

        themes: List[str] = []
        for w, _ in ranked:

            if any(w in t or t in w for t in themes):
                continue
            themes.append(w)
            if len(themes) >= k:
                break
        return themes
