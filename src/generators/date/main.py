from datetime import datetime, timedelta
from tzlocal import get_localzone, get_localzone_name
from random import randint, choice
from typing import Any, Callable
from .pytypes import *

def _resolve_field(
    args: DateArgs,
    name: str,
    default_min: int,
    default_max: int,
    normalize: Callable[[Any], int] | None = None,
    normalize_exact: Callable[[Any], int] | None = None,
    log: bool = False,
) -> int:
    # Check for an exact value first — it takes priority over any min/max range.
    exact = args.get(f'exact_{name}')
    # lo/hi here are the user-supplied arg values (e.g. min_year, max_year), not the
    # boundary-derived defaults passed in as default_min/default_max.
    lo = args.get(f'min_{name}')
    hi = args.get(f'max_{name}')

    if exact is not None:
        if log:
            print(f"Applying exact_{name} filter: {name} = {exact}")
        return normalize_exact(exact) if normalize_exact else exact
    elif lo is not None or hi is not None:
        # At least one bound was specified. Fill the missing side with the caller-supplied
        # default so we always have a complete range to sample from.
        lo = default_min if lo is None else (
            normalize(lo) if normalize else lo)
        hi = default_max if hi is None else (
            normalize(hi) if normalize else hi)

        if lo > hi:
            raise ValueError(
                f"Invalid {name} range: min_{name}={lo} is greater than max_{name}={hi}.")

        if log:
            print(f"Applying {name} filter: {lo} <= {name} <= {hi}")
        value = randint(int(lo), int(hi))
        if log:
            print(f"Generated {name}: {value}")
        return value
    # No user args for this field — generate randomly within the caller-supplied defaults.
    if log:
        print(
            f"Applying {name} filter: {default_min} <= {name} <= {default_max}")
    value = randint(int(default_min), int(default_max))
    if log:
        print(f"Generated {name}: {value}")
    return value


def _get_season_int_bounds(
        season: Season,
        year: int,
        astronomical: bool,
        time_zone_name: str = 'UTC',
        log: bool = False,
) -> tuple[int, int, int, int]:
    """Returns (start_month, start_day, end_month, end_day) as ints."""
    season_str = normalize_season_str(season)

    if not astronomical:
        if log:
            print("Using default meteorological season bounds.")
        (sm, sd), (em, ed) = METEOROLOGY_SEASON_BOUNDS[season_str]
        return normalize_month_int(sm), sd, normalize_month_int(em), ed

    if log:
        print("Using astronomical season bounds based on the resolved year and time zone.")
    season_bounds = calc_season_bounds(year, time_zone_name)
    (sm, sd), (em, ed) = season_bounds[season_str]
    sm_int = normalize_month_int(sm)
    em_int = normalize_month_int(em)

    if season_str == 'winter':
        # Use the day before spring of THIS year (not year+1) so that early-winter
        # dates (Jan–Mar) are bounded by the correct equinox.
        spring_sm, spring_sd = season_bounds['spring'][0]
        end_dt = datetime(year, normalize_month_int(spring_sm), spring_sd) - timedelta(days=1)
        em_int = end_dt.month
        ed = end_dt.day

    return sm_int, sd, em_int, ed


def gen_date(args: DateArgs, log: bool = False) -> str:
    input_format = args['input_format']
    output_format = args['output_format']

    before = args.get('before')
    before = datetime.strptime(
        cast(str, before), input_format) if before is not None else None
    after = args.get('after')
    after = datetime.strptime(
        cast(str, after), input_format) if after is not None else None
    
    time_zone_data = None
    time_zone_name = ''
    if before is not None:
        time_zone_data = before.tzinfo
        time_zone_name = before.tzname()
    elif after is not None:
        time_zone_data = after.tzinfo
        time_zone_name = after.tzname()

    if after is not None and before is not None and after > before:
        raise ValueError(
            "The 'after' date must be earlier than the 'before' date.")

    if time_zone_data is None or time_zone_name is None:
        # Use the system's local time zone as a fallback if neither before nor after provided tzinfo.
        if log: print("No time zone info found in 'before' or 'after' constraints; using system local time zone.")
        time_zone_data = get_localzone()
        time_zone_name = get_localzone_name()
        if log: print(f"Local time zone: {time_zone_name}")

    # These two flags track whether the date being built is still "at the boundary" of the
    # after/before constraints for all fields resolved so far. They start True and are set
    # to False the moment any field falls strictly inside the allowed range (e.g. year is
    # between after.year and before.year, not equal to either). Once a flag is False, all
    # finer-grained fields (month, day, …) are free to use their full default range rather
    # than being pinned to the boundary datetime's value.
    at_after = True
    at_before = True

    def resolve(name, default_min, default_max, normalize=None, normalize_exact=None, clamp_min=None, clamp_max=None):
        nonlocal at_after, at_before
        # Use the boundary datetime's field value as the bound while we're still "at" that
        # boundary; otherwise fall back to the field's natural default range.
        lo = getattr(
            after, name) if at_after and after is not None else default_min
        hi = getattr(
            before, name) if at_before and before is not None else default_max
        # Apply any additional clamps (e.g. from season constraints) on top.
        if clamp_min is not None:
            lo = max(lo, clamp_min)
        if clamp_max is not None:
            hi = min(hi, clamp_max)
        if lo > hi:
            raise ValueError(
                f"No valid {name} in [{lo}, {hi}] after applying all constraints.")
        value = int(_resolve_field(args, name, lo, hi,
                    normalize=normalize, normalize_exact=normalize_exact, log=log))
        # If the resolved value equals the boundary's value, we remain "at" the boundary
        # and the next field must still respect it. If not, we've moved strictly inside.
        at_after = at_after and after is not None and value == getattr(
            after, name)
        at_before = at_before and before is not None and value == getattr(
            before, name)
        return value

    year = resolve('year', 1970, 2100)

    # --- Season resolution ---
    # A season maps to a (start_month, start_day) → (end_month, end_day) range. We
    # translate it into two things:
    #   s_clamp_lo/hi  — month range clamps passed to resolve() below
    #   s_start/s_end  — (month, day) pairs used to tighten the day range *only* when the
    #                    resolved month lands exactly on the season's first or last month.
    #                    Months in the middle of the season have no day restriction.
    season = args.get('season')
    s_clamp_lo = s_clamp_hi = None
    # inclusive lower season bound (month, day)
    s_start: IntMonthDayPair | None = None
    # inclusive upper season bound (month, day)
    s_end:   IntMonthDayPair | None = None

    if season is not None:
        sm, sd, em, ed = _get_season_int_bounds(
            season, year, args['astronomical_season_bounds'], time_zone_name, log
        )
        season_str = normalize_season_str(season)
        # Winter is the only season whose month range wraps across the calendar year
        # (december=12 → february=2, so start > end numerically).
        wraps = sm > em

        if log:
            print(
                f"Season filter: {season_str} (month {sm} day {sd} → month {em} day {ed})")

        # Current effective month bounds, accounting for after/before boundary tracking.
        lo_m = after.month if at_after and after is not None else 1
        hi_m = before.month if at_before and before is not None else 12

        if wraps:
            # Winter spans two calendar halves within a single year:
            #   early side — January 1 through February end
            #   late side  — December 1 through December 31
            # Check which halves are reachable given the current month bounds.
            can_early = lo_m <= em   # after constraint doesn't push us past Feb
            can_late = hi_m >= sm   # before constraint doesn't cut off before Dec
            if not can_early and not can_late:
                raise ValueError(
                    f"Season '{season_str}' conflicts with the date range constraints.")
            # If both halves are reachable, pick one randomly; otherwise use whichever fits.
            use_early = choice([True, False]) if (
                can_early and can_late) else can_early
            if use_early:
                s_clamp_lo, s_clamp_hi = 1, em
                s_start, s_end = (1, 1), (em, ed)
            else:
                s_clamp_lo, s_clamp_hi = sm, 12
                s_start, s_end = (sm, sd), (12, 31)
            if log:
                print(
                    f"Winter side: {'early' if use_early else 'late'}, month range [{s_clamp_lo}, {s_clamp_hi}]")
        else:
            # Non-wrapping season: verify the current month window overlaps the season.
            # lo_m > em means after is already past the season end;
            # hi_m < sm means before is before the season even starts.
            if lo_m > em or hi_m < sm:
                raise ValueError(
                    f"Season '{season_str}' (months {sm}–{em}) conflicts with the date range constraints.")
            s_clamp_lo, s_clamp_hi = sm, em
            s_start, s_end = (sm, sd), (em, ed)
            if log:
                print(
                    f"Season month range: [{s_clamp_lo}, {s_clamp_hi}], day bounds: start={s_start}, end={s_end}")

    month = resolve('month', 1, 12, normalize_month_int,
                    normalize_month_int, clamp_min=s_clamp_lo, clamp_max=s_clamp_hi)

    # Day normalization must happen after year and month are resolved because the number
    # of days in a month depends on both (e.g. February in a leap year has 29 days).
    def norm_day(d): return normalize_day(year, month, d)
    lo_day = after.day if at_after and after is not None else 1
    # Pass 31 as the raw max — norm_day clamps it to the actual last day of the month.
    hi_day = norm_day(before.day if at_before and before is not None else 31)

    # Tighten the day range with season day bounds, but only when the resolved month is
    # the season's first or last month. A mid-season month (e.g. April in spring) is
    # fully open and doesn't need any day adjustment.
    if s_start is not None and month == s_start[0]:
        lo_day = max(lo_day, s_start[1])
        if log:
            print(f"Season start-day constraint: lo_day = {lo_day}")
    if s_end is not None and month == s_end[0]:
        # Also normalize the season's end day in case it's 29 and it's not a leap year.
        hi_day = min(hi_day, norm_day(s_end[1]))
        if log:
            print(f"Season end-day constraint: hi_day = {hi_day}")
    if lo_day > hi_day:
        raise ValueError(
            f"No valid day in [{lo_day}, {hi_day}] after applying all constraints.")

    day = int(_resolve_field(args, 'day', lo_day, hi_day,
              normalize=norm_day, normalize_exact=norm_day, log=log))
    at_after = at_after and after is not None and day == after.day
    at_before = at_before and before is not None and day == before.day

    hour = resolve('hour', 0, 23, normalize_hour)
    minute = resolve('minute', 0, 59, normalize_minute)
    second = resolve('second', 0, 59, normalize_second)

    return datetime(year, month, day, hour, minute, second, tzinfo=time_zone_data).strftime(output_format)
