"""Lightweight language detection for routing to the backend's km/en prompts.

Deliberately simple: checks for Khmer-script characters (Unicode block
U+1780-U+17FF) rather than using a full language-ID model. Farmer
questions are short, and the two languages the backend supports use
distinct, non-overlapping scripts, so a character-range check is a
reliable, zero-dependency, zero-latency signal -- no API call needed.
"""
from __future__ import annotations

_KHMER_BLOCK_START = 0x1780
_KHMER_BLOCK_END = 0x17FF


def detect_language(text: str) -> str:
    """Return "km" if the text contains any Khmer-script character,
    else "en". Defaults to "km" for text with no letters at all
    (e.g. only emoji/numbers), matching the backend's own default.
    """
    has_khmer = any(_KHMER_BLOCK_START <= ord(ch) <= _KHMER_BLOCK_END for ch in text)
    if has_khmer:
        return "km"

    has_latin_letter = any(ch.isalpha() for ch in text)
    if has_latin_letter:
        return "en"

    return "km"
