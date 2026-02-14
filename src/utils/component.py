from utils.math import clamp, randint_from_input
from typing import Callable

def format_component(
    value: int | str | None,
    min_val: int,
    max_val: int,
    width: int,
    fallback_fn: Callable[[], int],
    log: bool = False
) -> tuple[int, str]:
    """
        Helper to process and format a component (SSN/phone part).
        Returns both the integer value and the zero-padded string.
    """
    if value is None:
        int_val = fallback_fn()
    else:
        int_val = clamp(randint_from_input(value, fallback_fn, log=log), min_val, max_val, log=log)
    return int_val, str(int_val).zfill(width)