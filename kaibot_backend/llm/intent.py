"""
Lightweight, rule-based greeting/small-talk detector. Runs BEFORE
retrieval so a "hello" or "thanks" doesn't consume an embedding+LLM call
or trigger the low-confidence fallback UI. Deliberately simple (keyword
match, not an LLM classifier) to avoid adding latency, cost, or a new
failure mode this close to the Jul 29 demo.
"""

_GREETING_PHRASES = {
    # Khmer
    "សួស្តី", "ជំរាបសួរ", "អរគុណ", "អូខេ", "បាទ", "ចាស",
    "hi", "hello", "hey", "yo", "thanks", "thank you", "ok", "okay",
}


def is_greeting(text: str) -> bool:
    """Return True if the input looks like a greeting/small-talk, not a real question."""
    normalized = text.strip().lower()
    if not normalized:
        return False
    if len(normalized) > 20:
        return False
    return any(phrase in normalized for phrase in _GREETING_PHRASES)