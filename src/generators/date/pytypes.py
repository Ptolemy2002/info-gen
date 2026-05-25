import argparse
from skyfield.api import load
from skyfield import almanac
from typing import Callable, TypedDict, Literal, NotRequired, cast, Sequence
from calendar import monthrange
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

StrSeason = Literal['spring', 'summer', 'autumn', "fall", 'winter']
Season = StrSeason | int

StrMonth = Literal['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
Month = StrMonth | int

StrWeekday = Literal['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
Weekday = StrWeekday | int

StrMonthDayPair = tuple[StrMonth, int]
IntMonthDayPair = tuple[int, int]
MonthDayPair = tuple[Month, int]

MONTH_NUM_MAP: dict[StrMonth, int] = {
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

NUM_MONTH_MAP: dict[int, StrMonth] = {v: k for k, v in MONTH_NUM_MAP.items()}

# Add fall as an alias for autumn in the season number map, but keep it out of the number season map
# so that fall-equivalent is always normalized to autumn, but users can still input fall as a season.
NUM_SEASON_MAP: dict[int, StrSeason] = {
    1: 'spring',
    2: 'summer',
    3: 'autumn',
    4: 'winter'
}

SEASON_NUM_MAP: dict[StrSeason, int] = {**{v: k for k, v in NUM_SEASON_MAP.items()}, 'fall': 3}

WEEKDAY_NUM_MAP: dict[StrWeekday, int] = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
}

NUM_WEEKDAY_MAP: dict[int, StrWeekday] = {v: k for k, v in WEEKDAY_NUM_MAP.items()}

class DateArgs(TypedDict):
    input_format: str
    output_format: str

    before: NotRequired[str | None]
    after: NotRequired[str | None]
    season: NotRequired[Season | None]
    astronomical_season_bounds: bool

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
        return NUM_SEASON_MAP[season]

    if season == 'fall':
        return 'autumn'
    
    return season

def normalize_season_int(season: Season) -> int:
    if isinstance(season, int):
        return min(max(1, season), 4)
    
    season_str = normalize_season_str(season)
    return SEASON_NUM_MAP[season_str]

def normalize_month_int(month: Month) -> int:
    if isinstance(month, int):
        return min(max(1, month), 12)
    
    return MONTH_NUM_MAP[month]

def normalize_month_str(month: Month) -> StrMonth:
    if isinstance(month, int):
        month = min(max(1, month), 12)
        return NUM_MONTH_MAP[month]
    
    return month

def normalize_weekday_int(weekday: Weekday) -> int:
    if isinstance(weekday, int):
        return min(max(0, weekday), 6)
    
    weekday_str = cast(StrWeekday, weekday.lower())
    return WEEKDAY_NUM_MAP[weekday_str]

def normalize_weekday_str(weekday: Weekday) -> StrWeekday:
    if isinstance(weekday, int):
        weekday = min(max(0, weekday), 6)
        return NUM_WEEKDAY_MAP[weekday]
    
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
    return NUM_SEASON_MAP[season_int]

def loop_weekday_int(weekday: Weekday, delta: int) -> int:
    weekday_int = normalize_weekday_int(weekday) + delta
    return weekday_int % 7

def loop_weekday_str(weekday: Weekday, delta: int) -> StrWeekday:
    weekday_int = loop_weekday_int(weekday, delta)
    return NUM_WEEKDAY_MAP[weekday_int]

def len_month(year: int, month: int) -> int:
    return monthrange(year, month)[1]

def month_argtype(s: str) -> int | str:
    lower = s.lower()
    if lower in MONTH_NUM_MAP:
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
    if lower in SEASON_NUM_MAP:
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
    'st_patricks',
    'independence',
    'halloween',
    'christmas',
    'veterans'
]

FIXED_HOLIDAY_MAP: dict[KnownFixedHoliday, IntMonthDayPair] = {
    'new_years': (1, 1),
    'valentines': (2, 14),
    'st_patricks': (3, 17),
    'independence': (7, 4),
    'halloween': (10, 31),
    'christmas': (12, 25),
    'veterans': (11, 11)
}

KnownHoliday = KnownFloatingHoliday | KnownFixedHoliday

def is_known_floating_holiday(name: str) -> bool:
    return name in FLOATING_HOLIDAY_MAP

def is_known_fixed_holiday(name: str) -> bool:
    return name in FIXED_HOLIDAY_MAP

def is_known_holiday(name: str) -> bool:
    return is_known_floating_holiday(name) or is_known_fixed_holiday(name)

def which_known_holiday(month: Month, day: int, year: int, holiday_set: Sequence[KnownHoliday] | None = None) -> KnownHoliday | None:
    if holiday_set is None:
        holiday_set = list(FIXED_HOLIDAY_MAP.keys()) + list(FLOATING_HOLIDAY_MAP.keys())

    month = normalize_month_int(month)
    day = normalize_day(year, month, day)

    for holiday in holiday_set:
        if is_known_fixed_holiday(holiday):
            holiday_month, holiday_day = FIXED_HOLIDAY_MAP[cast(KnownFixedHoliday, holiday)]
        else:  # is known floating holiday
            holiday_month, holiday_day = FLOATING_HOLIDAY_MAP[cast(KnownFloatingHoliday, holiday)](year)

        if month == holiday_month and day == holiday_day:
            return holiday

    return None

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

SeasonBoundSet = dict[StrSeason, tuple[StrMonthDayPair, StrMonthDayPair]]

# Meteorological season bounds
METEOROLOGY_SEASON_BOUNDS: SeasonBoundSet = {
    "spring": (('march', 1), ('may', 31)),
    "summer": (('june', 1), ('august', 31)),
    "autumn": (('september', 1), ('november', 30)),
    "winter": (('december', 1), ('february', 29))
}

eph = None
ts = None
def calc_season_bounds(year: int, target_tz: str='UTC') -> SeasonBoundSet:
    global eph, ts

    # 1. Only load the ephemeris and timescale when this function is called for the first time, since they can be reused across calls and are expensive to load.
    if eph is None or ts is None:
        eph = load('de421.bsp')
        ts = load.timescale()

    # 2. Search up to April 1st of the NEXT year to capture the true end of Winter
    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year + 1, 4, 1) 

    times, season_indices = almanac.find_discrete(t0, t1, almanac.seasons(eph))

    season_names = [NUM_SEASON_MAP[index + 1] for index in range(4)]
    results: SeasonBoundSet = {}
    
    # Store localized datetime objects temporarily to make the math precise
    season_starts = {}
    next_spring_dt = None

    for time_obj, index in zip(times, season_indices):
        season_name = season_names[index]
        dt = time_obj.astimezone(ZoneInfo(target_tz))
        
        # Separate the events of the current year from the Spring of the next year
        if dt.year == year:
            season_starts[season_name] = dt
        elif dt.year == year + 1 and season_name == 'spring':
            next_spring_dt = dt

    # 3. Build the bounds
    for i in range(4):
        current_season = cast(StrSeason, season_names[i])
        start_dt = season_starts[current_season]
        
        start_month_str = normalize_month_str(start_dt.month)
        start_day = start_dt.day

        # Capping off the bounds
        if current_season == 'winter':
            # Use the actual Spring of the following year to cap Winter
            end_dt = cast(datetime, next_spring_dt) - timedelta(days=1)
        else:
            # Otherwise, use the start of the next season in the current year
            next_season = season_names[i + 1]
            end_dt = season_starts[next_season] - timedelta(days=1)

        end_month_str = normalize_month_str(end_dt.month)
        end_day = end_dt.day

        results[current_season] = ((start_month_str, start_day), (end_month_str, end_day))
    
    return results
