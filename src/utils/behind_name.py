import requests
import os
from typing import cast
from bs4 import BeautifulSoup

MAX_NAMES = 6
API_BASE = "https://www.behindthename.com/api/random.json"

USAGE_TYPES: list[str] | None = None
FIRST_NAMES: dict[str, list[str]] = {}
LAST_NAMES: dict[str, list[str]] = {}

def normalize_gender(gender: str | None) -> str | None:
    if gender:
        gender = gender.lower()
        if gender in ["male", "m"]:
            return "m"
        elif gender in ["female", "f"]:
            return "f"
        elif gender in ["nb", "non-binary"]:
            return None
    return None

def _cache_key(usage: str | None, gender: str | None) -> str:
    return f"{usage or ''}:{normalize_gender(gender) or ''}"


def fetch_names(key: str, usage: str | None = None, gender: str | None = None) -> None:
    params: dict[str, str | int] = {
        "key": key,
        "number": MAX_NAMES,
        "randomsurname": "yes",
    }

    gender = normalize_gender(gender)
    if gender:
        params["gender"] = gender
    if usage:
        if usage not in get_usage_types():
            raise ValueError(f"Invalid usage type '{usage}'. Valid usage types can be seen at https://www.behindthename.com/api/appendix2.php")
        
        params["usage"] = usage

    response = requests.get(API_BASE, params=params)
    response.raise_for_status()
    names: list[str] = response.json()["names"]

    # Last element is the surname; everything before is given names
    given, surname = names[:-1], names[-1]

    cache_key_first = _cache_key(usage, gender)
    cache_key_last = _cache_key(usage, None)  # Last names are not gender-specific
    FIRST_NAMES.setdefault(cache_key_first, []).extend(given)
    LAST_NAMES.setdefault(cache_key_last, []).append(surname)


def get_first_name_with_usage(key: str, usage: str | None = None, gender: str | None = None) -> str:
    cache_key = _cache_key(usage, gender)
    if not FIRST_NAMES.get(cache_key):
        fetch_names(key, usage, gender)
    return FIRST_NAMES[cache_key].pop()


def get_last_name_with_usage(key: str, usage: str | None = None) -> str:
    cache_key = _cache_key(usage, None)  # Last names are not gender-specific
    if not LAST_NAMES.get(cache_key):
        fetch_names(key, usage, None)
    return LAST_NAMES[cache_key].pop()

def get_usage_types() -> list[str]:
    global USAGE_TYPES
    if USAGE_TYPES is not None:
        return USAGE_TYPES

    if os.path.exists("./src/assets/behind_name_table.html"):
        with open("./src/assets/behind_name_table.html", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            
        USAGE_TYPES = [
            row.find_all("td")[0].get_text(strip=True)
            for row in soup.find_all("tr")
            if row.find("td")
        ]
    else:
        USAGE_TYPES = []

    return cast(list[str], USAGE_TYPES)