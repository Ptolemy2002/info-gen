import argparse
from typing import TypedDict, Literal, NotRequired, cast
from calendar import monthrange

StrSeason = Literal['spring', 'summer', 'autumn', "fall", 'winter']
Season = StrSeason | int

StrMonth = Literal['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
Month = StrMonth | int

StrMonthDayPair = tuple[StrMonth, int]
MonthDayPair = tuple[Month, int]
IntMonthDayPair = tuple[int, int]

MONTH_MAP: dict[StrMonth, int] = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12
}

SEASON_MAP: dict[int, StrSeason] = {
    1: 'spring',
    2: 'summer',
    3: 'autumn',
    4: 'winter'
}

class DateArgs(TypedDict):
    input_format: str
    output_format: str

    before: NotRequired[str | None]
    after: NotRequired[str | None]
    season: NotRequired[Season | None]

    min_month: NotRequired[Month | None]
    min_day: NotRequired[int | None]
    min_year: NotRequired[int | None]

    max_month: NotRequired[Month | None]
    max_day: NotRequired[int | None]
    max_year: NotRequired[int | None]

    exact_month: NotRequired[Month | None]
    exact_day: NotRequired[int | None]
    exact_year: NotRequired[int | None]

    min_hour: NotRequired[int | None]
    min_minute: NotRequired[int | None]
    min_second: NotRequired[int | None]

    max_hour: NotRequired[int | None]
    max_minute: NotRequired[int | None]
    max_second: NotRequired[int | None]

    exact_hour: NotRequired[int | None]
    exact_minute: NotRequired[int | None]
    exact_second: NotRequired[int | None]

def normalize_hour(hour: int) -> int:
    return min(max(0, hour), 23)

def normalize_minute(minute: int) -> int:
    return min(max(0, minute), 59)

def normalize_second(second: int) -> int:
    return min(max(0, second), 59)

def normalize_day(year: int, month: Month, day: int) -> int:
    month_int = normalize_month_int(month)
    days_in_month = monthrange(year, month_int)[1]
    return min(max(1, day), days_in_month)

def normalize_season_str(season: Season) -> StrSeason:
    if isinstance(season, int):
        return SEASON_MAP[season]

    if season == 'fall':
        return 'autumn'
    
    return season

def normalize_season_int(season: Season) -> int:
    if isinstance(season, int):
        return min(max(1, season), 4)
    
    season_str = normalize_season_str(season)
    for k, v in SEASON_MAP.items():
        if v == season_str:
            return k
    
    # Should never reach here, but just in case
    return 0

def normalize_month_int(month: Month) -> int:
    global MONTH_MAP

    if isinstance(month, int):
        return min(max(1, month), 12)
    
    return MONTH_MAP[month]

def normalize_month_str(month: Month) -> StrMonth:
    global MONTH_MAP

    if isinstance(month, int):
        month = min(max(1, month), 12)

        for k, v in MONTH_MAP.items():
            if v == month:
                return k
        
        # Should never reach here, but just in case
        return cast(StrMonth, '')
    
    return month


def month_argtype(s: str) -> int | str:
    lower = s.lower()
    if lower in MONTH_MAP:
        return lower
    try:
        val = int(s)
        if 1 <= val <= 12:
            return val
        raise argparse.ArgumentTypeError("Month integer must be between 1 and 12.")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Month must be a month name or integer 1–12.")

def season_argtype(s: str) -> int | str:
    lower = s.lower()
    if lower in SEASON_MAP.values() or lower == 'fall':
        return lower

    try:
        val = int(s)
        if 1 <= val <= 4:
            return val
        raise argparse.ArgumentTypeError("Season integer must be between 1 and 4 (1=spring, 2=summer, 3=autumn, 4=winter).")
    except ValueError:
        raise argparse.ArgumentTypeError("Season must be a name (spring/summer/autumn/fall/winter) or integer 1–4.")