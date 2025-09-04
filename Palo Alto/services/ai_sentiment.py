# services/ai_sentiment.py
from __future__ import annotations
from typing import List, Tuple
import torch
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np

# NEW: better theme extraction
from services.ai_themes import extract_themes


class AISentiment:
    def __init__(self):
        self._sent_pipe = None
        self._embed = None
        self._device = 0 if torch.cuda.is_available() else -1

    def _ensure_sent(self):
        if self._sent_pipe is None:
            # simple, accurate SST-2 classifier from HF
            self._sent_pipe = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=self._device,
            )

    def _ensure_embedder(self):
        if self._embed is None:
            # good all-round encoder that works well on journaling text
            self._embed = SentenceTransformer("intfloat/e5-base")

    # ---- Public API ---------------------------------------------------------

    def analyze_entry(self, text: str) -> Tuple[float, List[str]]:
        """
        Returns (sentiment_score in [-1, 1], top_themes[List[str]])
        """
        if not text or not text.strip():
            return 0.0, []

        # sentiment
        self._ensure_sent()
        out = self._sent_pipe(text[:4096])[0]
        label = out["label"].upper()
        score = float(out["score"])
        sent = score if label == "POSITIVE" else -score

        # themes (KeyBERT + YAKE + optional spaCy noun-chunks)
        themes = extract_themes(text, top_k=3)

        return sent, themes

    def embed_entries(self, texts: List[str]) -> List[List[float]]:
        self._ensure_embedder()
        vecs = self._embed.encode(texts, normalize_embeddings=True)
        if isinstance(vecs, np.ndarray):
            return vecs.tolist()
        return [list(map(float, v)) for v in vecs]
