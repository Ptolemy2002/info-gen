import re
import math
from typing import TypedDict

class Duration(TypedDict):
    seconds: int
    minutes: int
    hours: int
    days: int
    weeks: int
    months: int
    years: int
    weekdays: int

_UNIT_MAP: dict[str, str] = {
    "s": "seconds", "sec": "seconds", "secs": "seconds",
    "second": "seconds", "seconds": "seconds",

    "m": "minutes", "min": "minutes", "mins": "minutes",
    "minute": "minutes", "minutes": "minutes",

    "h": "hours", "hr": "hours", "hrs": "hours",
    "hour": "hours", "hours": "hours",

    "d": "days", "day": "days", "days": "days",

    "w": "weeks", "wk": "weeks", "wks": "weeks",
    "week": "weeks", "weeks": "weeks",

    "mo": "months", "mon": "months", "mos": "months",
    "month": "months", "months": "months",

    "y": "years", "yr": "years", "yrs": "years",
    "year": "years", "years": "years",

    "wd": "weekdays", "wday": "weekdays", "wdays": "weekdays",
    "weekday": "weekdays", "weekdays": "weekdays",
}

_TOKEN_RE = re.compile(r"((?:\+|\-)?\d+)\s*([a-zA-Z]+)")


def parse_duration(s: str) -> Duration:
    result: Duration = {
        "seconds": 0, "minutes": 0, "hours": 0, "days": 0,
        "weeks": 0, "months": 0, "years": 0, "weekdays": 0,
    }

    i = 0
    for value_str, unit_str in _TOKEN_RE.findall(s):
        key = _UNIT_MAP.get(unit_str.lower())
        if key is None:
            raise ValueError(f"Unknown duration unit: {unit_str!r}")
        result[key] += int(value_str)  # type: ignore[literal-required]
        i += 1
    
    if i == 0:
        raise ValueError(f"String does not contain any valid duration tokens: {s!r}")

    return result

def is_duration(s: str) -> bool:
    try:
        parse_duration(s)
        return True
    except ValueError:
        return False
