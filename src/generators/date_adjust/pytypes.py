from typing import NotRequired, TypedDict
from generators.date import IntMonthDayPair, KnownFixedHoliday
from .duration_parse import Duration, is_duration, parse_duration
import argparse

class DateAdjustArgs(TypedDict):
    input_format: str
    output_format: str
    date: NotRequired[str | None]
    duration: Duration
    holidays: list[IntMonthDayPair | KnownFixedHoliday]
    skip_weekends: bool
    month_length: int | None

def duration_argtype(s: str) -> Duration:
    if not is_duration(s):
        raise argparse.ArgumentTypeError(f"String does not contain any valid duration tokens: {s!r}")
    return parse_duration(s)