from __future__ import annotations

from typing import Optional, Sequence, Set


def normalized_difficulty(value: Optional[str]) -> Optional[str]:
    """Normalize free-form difficulty strings into consistent labels."""
    if value is None:
        return None
    trimmed = value.strip()
    if not trimmed:
        return None
    lowered = trimmed.lower()
    mapping = {
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
    }
    return mapping.get(lowered, trimmed)


def difficulty_label(difficulties: Sequence[str]) -> str:
    """Return a human-friendly label for a sequence of difficulty values."""
    unique: Set[Optional[str]] = {normalized_difficulty(difficulty) for difficulty in difficulties if difficulty}
    unique.discard(None)
    if not unique:
        return "Mixed"
    if len(unique) == 1:
        # unique is non-empty, so retrieving the single element is safe
        return next(iter(unique)) or "Mixed"
    return "Mixed"


__all__ = ["normalized_difficulty", "difficulty_label"]
