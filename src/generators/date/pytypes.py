import argparse
from typing import Callable, TypedDict, Literal, NotRequired, cast
from calendar import monthrange
from datetime import datetime, timedelta

StrSeason = Literal['spring', 'summer', 'autumn', "fall", 'winter']
Season = StrSeason | int

StrMonth = Literal['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
Month = StrMonth | int

StrWeekday = Literal['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
Weekday = StrWeekday | int

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

WEEKDAY_MAP: dict[StrWeekday, int] = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
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

def normalize_weekday_int(weekday: Weekday) -> int:
    if isinstance(weekday, int):
        return min(max(0, weekday), 6)
    
    weekday_str = cast(StrWeekday, weekday.lower())
    return WEEKDAY_MAP[weekday_str]

def normalize_weekday_str(weekday: Weekday) -> StrWeekday:
    if isinstance(weekday, int):
        weekday = min(max(0, weekday), 6)

        for k, v in WEEKDAY_MAP.items():
            if v == weekday:
                return k
        
        # Should never reach here, but just in case
        return cast(StrWeekday, '')
    
    return cast(StrWeekday, weekday.lower())

def loop_month_int(month: Month, year: int, delta: int) -> tuple[int, int]:
    month_int = normalize_month_int(month) - 1 + delta
    year += month_int // 12
    month_int = month_int % 12 + 1
    return month_int, year

def loop_month_str(month: Month, year: int, delta: int) -> tuple[StrMonth, int]:
    month_int, year = loop_month_int(month, year, delta)
    month_str = normalize_month_str(month_int)
    return month_str, year

def loop_season_int(season: Season, delta: int) -> int:
    season_int = normalize_season_int(season) + delta
    return (season_int - 1) % 4 + 1

def loop_season_str(season: Season, delta: int) -> StrSeason:
    season_int = loop_season_int(season, delta)
    return SEASON_MAP[season_int]

def loop_weekday_int(weekday: Weekday, delta: int) -> int:
    weekday_int = normalize_weekday_int(weekday) + delta
    return weekday_int % 7

def loop_weekday_str(weekday: Weekday, delta: int) -> StrWeekday:
    weekday_int = loop_weekday_int(weekday, delta)
    for k, v in WEEKDAY_MAP.items():
        if v == weekday_int:
            return k
    
    # Should never reach here, but just in case
    return cast(StrWeekday, '')

def len_month(year: int, month: int) -> int:
    return monthrange(year, month)[1]

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
    
def hour_argtype(s: str) -> int:
    s = s.lower()
    is_am = s.endswith('am')
    is_pm = s.endswith('pm')

    # Ranges are not included in this validation because values should be normalized later
    try:
        if is_am or is_pm:
            value = int(s[:-2])
            if is_am:
                if value == 12:
                    return 0
                else: return value
            else:  # is_pm
                if value == 12:
                    return 12
                else: return value + 12
        else:
            return int(s)
    except ValueError:
        raise argparse.ArgumentTypeError("Value must be an integer optionally followed by 'am' or 'pm' (e.g., '3pm', '11am').")

def calc_nth_weekday(year: int, month: Month, weekday: Weekday, n: int) -> int:
    # Clamp to 1
    if n < 1:
        n = 1

    month = normalize_month_int(month)
    weekday_int = normalize_weekday_int(weekday)
    first_day_of_month = monthrange(year, month)[0] 
    first_weekday = (7 - first_day_of_month + weekday_int) % 7 + 1
    nth_weekday = first_weekday + (n - 1) * 7

    if nth_weekday > len_month(year, month):
        raise ValueError(f"{n}th {normalize_weekday_str(weekday)} does not exist in {normalize_month_str(month)} of {year}.")

    return nth_weekday

def calc_last_nth_weekday(year: int, month: Month, weekday: Weekday, n: int) -> int:
    # Get the first weekday of the next month then subtract 7 days times the number of weekdays we want to go back

    # Clamp to 1
    if n < 1:
        n = 1

    month = normalize_month_int(month)
    new_year, new_month = loop_month_int(month, year, 1)
    first_weekday_next_month = calc_nth_weekday(new_year, new_month, weekday, 1)
    date = datetime(new_year, new_month, first_weekday_next_month) - timedelta(weeks=n)

    # If we went back to the month before the target month, it means the last nth weekday does not exist in the target month
    if date.month != month:
        raise ValueError(f"Last {n}th {normalize_weekday_str(weekday)} does not exist in {normalize_month_str(month)} of {year}.")

    return date.day

def calc_mlkj_day(year: int) -> IntMonthDayPair:
    # MLKJ Day is the third Monday of January
    return 1, calc_nth_weekday(year, "january", 'monday', 3)

def calc_presidents_day(year: int) -> IntMonthDayPair:
    # Presidents' Day is the third Monday of February
    return 2, calc_nth_weekday(year, "february", 'monday', 3)

def calc_mothers_day(year: int) -> IntMonthDayPair:
    # Mother's Day is the second Sunday of May
    return 5, calc_nth_weekday(year, "may", 'sunday', 2)

def calc_fathers_day(year: int) -> IntMonthDayPair:
    # Father's Day is the third Sunday of June
    return 6, calc_nth_weekday(year, "june", 'sunday', 3)

def calc_memorial_day(year: int) -> IntMonthDayPair:
    # Memorial Day is the last Monday of May
    return 5, calc_last_nth_weekday(year, "may", 'monday', 1)

def calc_labor_day(year: int) -> IntMonthDayPair:
    # Labor Day is the first Monday of September
    return 9, calc_nth_weekday(year, "september", 'monday', 1)

def calc_columbus_day(year: int) -> IntMonthDayPair:
    # Columbus Day is the second Monday of October
    return 10, calc_nth_weekday(year, "october", 'monday', 2)

def calc_thanksgiving_day(year: int) -> IntMonthDayPair:
    # Thanksgiving is the fourth Thursday of November
    return 11, calc_nth_weekday(year, "november", 'thursday', 4)

def calc_black_friday(year: int) -> IntMonthDayPair:
    # Black Friday is the day after Thanksgiving
    thanksgiving_month, thanksgiving_day = calc_thanksgiving_day(year)
    date = datetime(year, normalize_month_int(thanksgiving_month), thanksgiving_day) + timedelta(days=1)
    return date.month, date.day

def calc_easter_sunday(year: int) -> IntMonthDayPair:
    # Anonymous Gregorian algorithm for calculating Easter Sunday
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return month, day

def calc_ash_wednesday(year: int) -> IntMonthDayPair:
    # Ash Wednesday is 46 days before Easter Sunday
    easter_month, easter_day = calc_easter_sunday(year)
    date = datetime(year, normalize_month_int(easter_month), easter_day) - timedelta(days=46)
    return date.month, date.day

def calc_good_friday(year: int) -> IntMonthDayPair:
    # Good Friday is 2 days before Easter Sunday
    easter_month, easter_day = calc_easter_sunday(year)
    date = datetime(year, normalize_month_int(easter_month), easter_day) - timedelta(days=2)
    return date.month, date.day

def calc_ascension_day(year: int) -> IntMonthDayPair:
    # Ascension Day is 39 days after Easter Sunday
    easter_month, easter_day = calc_easter_sunday(year)
    date = datetime(year, normalize_month_int(easter_month), easter_day) + timedelta(days=39)
    return date.month, date.day

def calc_pentecost(year: int) -> IntMonthDayPair:
    # Pentecost is 49 days after Easter Sunday
    easter_month, easter_day = calc_easter_sunday(year)
    date = datetime(year, normalize_month_int(easter_month), easter_day) + timedelta(days=49)
    return date.month, date.day

def calc_passover(year: int) -> IntMonthDayPair:
    # Gauss's algorithm for calculating Passover (Pesach)
    A = (12 * year + 17) % 19
    B = year % 4
    C = int(32.044093 + 1.5542418 * A + 0.25 * B - 0.0031778 * year)

    date = datetime(year, 3, 1) + timedelta(days=C - 1)

    # Adu Rule: If it is a Monday, Wednesday, or Friday, add one day
    if normalize_weekday_str(date.weekday()) in ['monday', 'wednesday', 'friday']:
        date += timedelta(days=1)

    return date.month, date.day

KnownFloatingHoliday = Literal[
    'mlkj',
    'presidents',
    'mothers',
    'fathers',
    'memorial',
    'labor',
    'columbus',
    'thanksgiving',
    'black_friday',
    'easter',
    'ash_wednesday',
    'good_friday',
    'ascension',
    'pentecost',
    'passover'
]

FLOATING_HOLIDAY_MAP: dict[KnownFloatingHoliday, Callable[[int], IntMonthDayPair]] = {
    'mlkj': calc_mlkj_day,
    'presidents': calc_presidents_day,
    'mothers': calc_mothers_day,
    'fathers': calc_fathers_day,
    'memorial': calc_memorial_day,
    'labor': calc_labor_day,
    'columbus': calc_columbus_day,
    'thanksgiving': calc_thanksgiving_day,
    'black_friday': calc_black_friday,
    'easter': calc_easter_sunday,
    'ash_wednesday': calc_ash_wednesday,
    'good_friday': calc_good_friday,
    'ascension': calc_ascension_day,
    'pentecost': calc_pentecost,
    'passover': calc_passover
}

KnownFixedHoliday = Literal[
    'new_years',
    'valentines',
    'independence',
    'halloween',
    'christmas'
]

FIXED_HOLIDAY_MAP: dict[KnownFixedHoliday, IntMonthDayPair] = {
    'new_years': (1, 1),
    'valentines': (2, 14),
    'independence': (7, 4),
    'halloween': (10, 31),
    'christmas': (12, 25)
}

KnownHoliday = KnownFloatingHoliday | KnownFixedHoliday

def is_known_floating_holiday(name: str) -> bool:
    return name in FLOATING_HOLIDAY_MAP

def is_known_fixed_holiday(name: str) -> bool:
    return name in FIXED_HOLIDAY_MAP

def is_known_holiday(name: str) -> bool:
    return is_known_floating_holiday(name) or is_known_fixed_holiday(name)

def int_month_day_pair_argtype(s: str) -> IntMonthDayPair | KnownFloatingHoliday:
    if is_known_fixed_holiday(s):
        # Since these are the same every year, we can just return the map value directly.
        return FIXED_HOLIDAY_MAP[cast(KnownFixedHoliday, s)]
    elif is_known_floating_holiday(s):
        # We need to let the generator itself handle floating holiday calculations, as that's when the year will be known.
        return cast(KnownFloatingHoliday, s)

    parts = s.split("/")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Value must be in the format 'Month/Day' (e.g., '1/15').")
    
    month_part, day_part = parts
    
    try:
        month = normalize_month_int(int(month_part))
    except ValueError:
        raise argparse.ArgumentTypeError("Month part must be an integer.")
    
    try:
        day = int(day_part)
    except ValueError:
        raise argparse.ArgumentTypeError("Day part must be an integer.")

    return month, day