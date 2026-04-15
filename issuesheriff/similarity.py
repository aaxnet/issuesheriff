"""
Duplicate detection using TF-IDF + cosine similarity.
Falls back to simple token overlap if scikit-learn is not installed.
"""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from typing import NamedTuple

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.45  # Pairs above this are reported as duplicates


class SimilarIssue(NamedTuple):
    id: int
    title: str
    score: float


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def find_duplicates(issues: list[dict], threshold: float = SIMILARITY_THRESHOLD) -> list[dict]:
    """
    Compare all issue pairs and return those above `threshold`.

    Returns list of dicts:
        { "a": int, "b": int, "title_a": str, "title_b": str, "score": float }
    """
    if len(issues) < 2:
        return []

    texts = [_issue_text(i) for i in issues]
    numbers = [i.get("number", idx) for idx, i in enumerate(issues)]
    titles = [i.get("title", "") for i in issues]

    matrix = _similarity_matrix(texts)
    pairs = []

    for i in range(len(issues)):
        for j in range(i + 1, len(issues)):
            score = matrix[i][j]
            if score >= threshold:
                pairs.append({
                    "a": numbers[i],
                    "b": numbers[j],
                    "title_a": titles[i],
                    "title_b": titles[j],
                    "score": round(score, 4),
                })

    pairs.sort(key=lambda x: x["score"], reverse=True)
    return pairs


def find_similar(query_issue: dict, corpus: list[dict], top_k: int = 5) -> list[SimilarIssue]:
    """
    Find top-k issues similar to query_issue from corpus.
    Used for single-issue duplicate lookup.
    """
    query_text = _issue_text(query_issue)
    corpus_texts = [_issue_text(i) for i in corpus]

    all_texts = [query_text] + corpus_texts
    matrix = _similarity_matrix(all_texts)
    query_row = matrix[0][1:]

    results = []
    for idx, score in enumerate(query_row):
        issue = corpus[idx]
        results.append(SimilarIssue(
            id=issue.get("number", idx),
            title=issue.get("title", ""),
            score=round(score, 4),
        ))

    results.sort(key=lambda x: x.score, reverse=True)
    return results[:top_k]


# ─────────────────────────────────────────────
#  Backends
# ─────────────────────────────────────────────

def _similarity_matrix(texts: list[str]) -> list[list[float]]:
    """Compute pairwise cosine similarity matrix."""
    try:
        return _sklearn_matrix(texts)
    except ImportError:
        logger.debug("scikit-learn not available, using token overlap similarity")
        return _tfidf_matrix(texts)


def _sklearn_matrix(texts: list[str]) -> list[list[float]]:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    vec = TfidfVectorizer(
        sublinear_tf=True,
        min_df=1,
        stop_words="english",
        ngram_range=(1, 2),
    )
    tfidf = vec.fit_transform(texts)
    sim = cosine_similarity(tfidf).tolist()
    return sim


def _tfidf_matrix(texts: list[str]) -> list[list[float]]:
    """Pure-Python TF-IDF fallback."""
    tokenized = [_tokenize(t) for t in texts]
    tfidf_vecs = _compute_tfidf(tokenized)

    n = len(texts)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i, n):
            score = _cosine(tfidf_vecs[i], tfidf_vecs[j])
            matrix[i][j] = score
            matrix[j][i] = score

    return matrix


def _compute_tfidf(docs: list[list[str]]) -> list[dict[str, float]]:
    n = len(docs)
    df: Counter = Counter()
    for doc in docs:
        df.update(set(doc))

    vecs = []
    for doc in docs:
        tf = Counter(doc)
        total = len(doc) or 1
        vec = {}
        for term, count in tf.items():
            t = count / total
            idf = math.log((n + 1) / (df[term] + 1)) + 1
            vec[term] = t * idf
        vecs.append(vec)

    return vecs


def _cosine(a: dict, b: dict) -> float:
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    mag_a = math.sqrt(sum(v * v for v in a.values()))
    mag_b = math.sqrt(sum(v * v for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _issue_text(issue: dict) -> str:
    parts = [
        issue.get("title", "") * 2,  # Weight title more
        issue.get("body", ""),
    ]
    return " ".join(filter(None, parts))


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 2]
