"""
Date and Time Standardization Library (DD/MM/YYYY)
Standard format for all backend exports, PDFs, and API representations.
"""

from datetime import date, datetime
from typing import Optional, Union


def format_date_dmy(
    val: Optional[Union[str, date, datetime]], separator: str = "/"
) -> str:
    """Formats any date / datetime / ISO string into DD/MM/YYYY (or DD-MM-YYYY).

    Example:
        format_date_dmy("2024-05-18") -> "18/05/2024"
        format_date_dmy(datetime.now()) -> "13/11/2026"
    """
    if not val:
        return "—"

    if isinstance(val, (datetime, date)):
        return val.strftime(f"%d{separator}%m{separator}%Y")

    if isinstance(val, str):
        val = val.strip()
        if not val:
            return "—"

        # Check ISO format YYYY-MM-DD
        if len(val) >= 10 and val[4] == "-" and val[7] == "-":
            try:
                y, m, d = val[:10].split("-")
                return f"{int(d):02d}{separator}{int(m):02d}{separator}{int(y):04d}"
            except Exception:
                pass

        # Try parsing via datetime fromisoformat
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt.strftime(f"%d{separator}%m{separator}%Y")
        except Exception:
            pass

    return str(val)


def format_datetime_dmy(
    val: Optional[Union[str, datetime]],
    include_seconds: bool = False,
    separator: str = "/",
) -> str:
    """Formats datetime into DD/MM/YYYY, hh:mm AM/PM.

    Example: "13/11/2026, 11:05 AM"
    """
    if not val:
        return "—"

    time_fmt = "%I:%M:%S %p" if include_seconds else "%I:%M %p"

    if isinstance(val, datetime):
        return (
            val.strftime(f"%d{separator}%m{separator}%Y, ")
            + val.strftime(time_fmt).lstrip("0")
        )

    if isinstance(val, str):
        val = val.strip()
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt.strftime(
                f"%d{separator}%m{separator}%Y, {time_fmt}"
            ).replace(", 0", ", ")
        except Exception:
            return format_date_dmy(val, separator)

    return str(val)
