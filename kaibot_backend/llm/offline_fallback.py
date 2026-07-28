"""
Zero-network, local-only fallback for when Gemini is genuinely
unreachable (network down, quota exhausted, DNS failure) -- distinct
from the normal low_confidence path, which requires a successful API
call that just scored low. This path never calls any external API.

Deliberately blunt: plain keyword overlap + difflib text similarity,
not real semantic understanding. Only used as a last resort when the
real pipeline has already failed to reach Gemini at all.
"""
from __future__ import annotations

import difflib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OFFLINE_CACHE_PATH = BASE_DIR / "data" / "offline_cache.json"

_MIN_MATCH_SCORE = 0.35  # combined score threshold below which we don't trust a match


def _load_cache() -> list[dict]:
    if not OFFLINE_CACHE_PATH.exists():
        return []
    with open(OFFLINE_CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_CACHE = _load_cache()


def _score(query: str, entry: dict) -> float:
    """Blend text-similarity and keyword-overlap into one 0-1 score."""
    query_lower = query.lower()

    text_sim = difflib.SequenceMatcher(
        None, query_lower, entry["question"].lower()
    ).ratio()

    keywords = entry.get("keywords", [])
    keyword_hits = sum(1 for kw in keywords if kw.lower() in query_lower)
    # Cap the "expected" keyword count at 3: a farmer only needs to hit a
    # couple of the right words, not exhaust a long keyword list. Without
    # this cap, entries with more thorough keyword coverage were unfairly
    # penalized for short/terse real-world phrasing.
    effective_count = min(len(keywords), 3) if keywords else 0
    keyword_score = min(keyword_hits / effective_count, 1.0) if effective_count else 0.0

    # Keyword hits are a stronger signal than raw text similarity for
    # short farmer questions, so weight them higher.
    return (0.4 * text_sim) + (0.6 * keyword_score)

def find_offline_answer(question: str) -> str | None:
    """
    Return the best cached answer if it clears the minimum match score,
    else None (caller should show the generic no-internet message).
    """
    if not _CACHE or not question.strip():
        return None

    best_entry = max(_CACHE, key=lambda e: _score(question, e))
    best_score = _score(question, best_entry)

    if best_score >= _MIN_MATCH_SCORE:
        return best_entry["answer"]
    return None