from .pytypes import StrSeason, StrMonthDayPair

# Meteorological season bounds
SEASON_BOUNDS: dict[StrSeason, tuple[StrMonthDayPair, StrMonthDayPair]] = {
    "spring": (('march', 1), ('may', 31)),
    "summer": (('june', 1), ('august', 31)),
    "autumn": (('september', 1), ('november', 30)),
    "winter": (('december', 1), ('february', 29))
}