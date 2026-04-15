"""
IssueSheriff tests.
"""

import json
import pytest

from issuesheriff.similarity import find_duplicates, find_similar, _tokenize
from issuesheriff.utils import truncate, format_score_bar, sanitize_label
from issuesheriff.ai import _classify_heuristic, suggest_labels


# ─────────────────────────────────────────────
#  Utils
# ─────────────────────────────────────────────

def test_truncate_short():
    assert truncate("hello", 10) == "hello"


def test_truncate_long():
    result = truncate("hello world this is a long string", 15)
    assert len(result) <= 15
    assert result.endswith("…")


def test_format_score_bar():
    bar = format_score_bar(1.0, width=8)
    assert bar == "████████"
    bar = format_score_bar(0.0, width=8)
    assert bar == "░░░░░░░░"


def test_sanitize_label():
    assert sanitize_label("My Label") == "my-label"
    assert sanitize_label("BUG") == "bug"


# ─────────────────────────────────────────────
#  AI (heuristics only — no API key needed)
# ─────────────────────────────────────────────

def test_classify_bug():
    t = _classify_heuristic("App crashes on startup", "Getting a segfault error")
    assert t == "bug"


def test_classify_feature():
    t = _classify_heuristic("Add dark mode support", "Feature request: implement dark theme")
    assert t == "feature"


def test_classify_question():
    t = _classify_heuristic("How do I configure the proxy?", "I need help understanding the docs")
    assert t == "question"


def test_suggest_labels_bug():
    labels = suggest_labels("App crashes with exception", "Getting a regression after update", as_list=True)
    assert "bug" in labels


def test_suggest_labels_returns_list():
    result = suggest_labels("feature request", "please add this", as_list=True)
    assert isinstance(result, list)
    assert len(result) >= 1


# ─────────────────────────────────────────────
#  Similarity
# ─────────────────────────────────────────────

ISSUES = [
    {"number": 1, "title": "Dark mode feature request", "body": "Please add dark theme support to the app"},
    {"number": 2, "title": "Add dark theme support", "body": "Feature request: dark mode option for the interface"},
    {"number": 3, "title": "App crashes on startup", "body": "Getting a crash error on launch every time"},
    {"number": 4, "title": "Startup crash bug", "body": "App crashes on startup with error message"},
]


def test_find_duplicates_finds_pairs():
    pairs = find_duplicates(ISSUES, threshold=0.25)
    assert len(pairs) >= 1
    numbers_in_pairs = {n for p in pairs for n in (p["a"], p["b"])}
    # At least one of the two similar pairs should be detected
    assert (1 in numbers_in_pairs and 2 in numbers_in_pairs) or \
           (3 in numbers_in_pairs and 4 in numbers_in_pairs)


def test_find_duplicates_empty():
    assert find_duplicates([], threshold=0.3) == []
    assert find_duplicates([ISSUES[0]], threshold=0.3) == []


def test_find_similar():
    query = {"title": "dark mode request", "body": "please add dark theme option"}
    corpus = ISSUES[1:]
    results = find_similar(query, corpus, top_k=3)
    assert len(results) <= 3
    assert all(0.0 <= r.score <= 1.0 for r in results)


def test_tokenize():
    tokens = _tokenize("Hello World, this is a test!")
    assert "hello" in tokens
    assert "world" in tokens
    # Stop short tokens
    assert "is" not in tokens
