import random
from warnings import warn
from utils.math import clamp, randint_from_input
from utils.component import format_component

SSN_START_MIN = 0
SSN_START_MAX = 999
SSN_MID_MIN = 0
SSN_MID_MAX = 99
SSN_END_MIN = 0
SSN_END_MAX = 9999
RESERVED_SSN_START_COUNT = 102  # 000, 666, and 900-999

def gen_ssn(start: int | str | None = None, mid: int  | str | None = None, end: int | str | None = None, log: bool = False) -> str:
    """
        Generate a random US Social Security Number (SSN).
        The SSA reserves 000, 666, and 900-999 in the first three digits as invalid, so they will
        be used if not specified otherwise to guarantee no real person has the generated SSN.

        :param start: The first part of the SSN. Will be clamped to between 0 and 999. If None, will be randomly decided
        from reserved ranges to ensure real-life invalidity. If not reserved, a warning will be issued to indicate a potentially real SSN.
        :param mid: The second part of the SSN. Will be clamped to between 0 and 99. If None, will be randomly decided.
        :param end: The third part of the SSN. Will be clamped to between 0 and 9999. If None, will be randomly decided.
    """
    def is_reserved_start(s: int) -> bool:
        """
            Check if a given SSN start is reserved/invalid.
        """
        return s == 0 or s == 666 or (900 <= s <= 999)

    def get_reserved_start(i: int) -> int:
        """
            Given an index for a reserved SSN start, return the corresponding reserved value.
        """
        i = clamp(i, 0, RESERVED_SSN_START_COUNT - 1)
        if i == 0:
            return 0
        elif i == 1:
            return 666
        else:
            return 900 + (i - 2)

    def get_random_reserved_start() -> int:
        """
            Get a random reserved SSN start value.
        """
        return get_reserved_start(random.randint(0, RESERVED_SSN_START_COUNT - 1))

    def get_random_mid() -> int:
        """
            Get a random SSN mid value.
        """
        return random.randint(SSN_MID_MIN, SSN_MID_MAX)

    def get_random_end() -> int:
        """
            Get a random SSN end value.
        """
        return random.randint(SSN_END_MIN, SSN_END_MAX)

    if start is None:
        start = get_random_reserved_start()
    else:
        start = clamp(randint_from_input(start, get_random_reserved_start, log=log), SSN_START_MIN, SSN_START_MAX, log=log)
        if not is_reserved_start(start):
            warn(f"The specified SSN start ({start}) means the generated SSN may correspond to a real person.")
    start_str = str(start).zfill(3)

    mid, mid_str = format_component(mid, SSN_MID_MIN, SSN_MID_MAX, 2, get_random_mid, log)
    end, end_str = format_component(end, SSN_END_MIN, SSN_END_MAX, 4, get_random_end, log)

    return f"{start_str}-{mid_str}-{end_str}"