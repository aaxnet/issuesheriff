"""
Utility functions for IssueSheriff.
"""


def truncate(text: str, max_len: int = 60, suffix: str = "…") -> str:
    """Truncate text to max_len characters."""
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def format_score_bar(score: float, width: int = 8) -> str:
    """
    Returns a unicode bar chart for a score between 0 and 1.
    E.g. 0.75 → '██████░░'
    """
    filled = round(score * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def sanitize_label(label: str) -> str:
    """Convert a label string to a valid GitHub label name."""
    return label.lower().strip().replace(" ", "-")[:50]


def chunk_text(text: str, max_chars: int = 3000) -> list[str]:
    """Split text into chunks of max_chars."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:max_chars])
        text = text[max_chars:]
    return chunks
