from typing import Optional


def normalize_gender(value: Optional[str]) -> Optional[str]:
    """
    Normalize a gender string to 'male' or 'female', or None if missing/empty.
    Raises ValueError if a non-empty unrecognized value is provided.
    """
    if value is None:
        return None
    cleaned = str(value).strip().lower()
    if not cleaned:
        return None
    if cleaned in ("male", "female"):
        return cleaned
    raise ValueError(f"Invalid gender value '{value}'. Must be 'male' or 'female'.")
