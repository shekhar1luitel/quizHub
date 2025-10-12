import re


def slugify(value: str) -> str:
    """Return a URL-friendly slug for the provided value."""

    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "subject"
