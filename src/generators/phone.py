import random
from warnings import warn
from utils.math import clamp, randint_from_input
from utils.component import format_component

AREA_CODE_MIN = 200
AREA_CODE_MAX = 999
CENTRAL_MIN = 200
CENTRAL_MAX = 999
LINE_MIN = 0
LINE_MAX = 9999
RESERVED_CENTRAL = 555
RESERVED_LINE_MIN = 100
RESERVED_LINE_MAX = 199


def gen_phone(area: int | str | None = None, central: int | str | None = None, line: int | str | None = None, log: bool = False) -> str:
    """
        Generate a random US phone number.
        The range "XXX-555-0100" to "XXX-555-0199" is reserved for fictional use, so if the central office code
        is not specified, it will be set to 555 to guarantee no real person has the generated phone number. Similarly,
        if the line number is not specified, it will be set to a value between 100 and 199 to stay within the reserved range.

        :param area: The area code (first three digits). Will be clamped to between 200 and 999. If None, will be randomly decided.
        :param central: The central office code (second three digits). Will be clamped to between 200 and 999. If None, will be randomly decided.
        If not reserved, a warning will be issued to indicate a potentially real phone number.
        :param line: The line number (last four digits). Will be clamped to between 0 and 9999. If None, will be randomly decided.
        If this is not reserved while the central number is, a warning will be issued to indicate a potentially real phone number.
    """
    def is_reserved_central(c: int) -> bool:
        """
            Check if a given central office code is reserved/invalid.
        """
        return c == RESERVED_CENTRAL

    def get_random_reserved_central() -> int:
        """
            Get a random reserved central office code.
        """
        return RESERVED_CENTRAL

    def get_random_central() -> int:
        """
            Get a random central office code.
        """
        return random.randint(CENTRAL_MIN, CENTRAL_MAX)

    def is_reserved_line(l: int) -> bool:
        """
            Check if a given line number is reserved/invalid.
        """
        return RESERVED_LINE_MIN <= l <= RESERVED_LINE_MAX

    def get_random_reserved_line() -> int:
        """
            Get a random reserved line number.
        """
        return random.randint(RESERVED_LINE_MIN, RESERVED_LINE_MAX)

    def get_random_line() -> int:
        """
            Get a random line number.
        """
        return random.randint(LINE_MIN, LINE_MAX)

    def get_random_area() -> int:
        """
            Get a random area code.
        """
        return random.randint(AREA_CODE_MIN, AREA_CODE_MAX)

    area, area_str = format_component(area, AREA_CODE_MIN, AREA_CODE_MAX, 3, get_random_area, log)

    if central is None:
        central = get_random_reserved_central()
    else:
        central = clamp(randint_from_input(central, get_random_reserved_central, log=log), CENTRAL_MIN, CENTRAL_MAX, log=log)
        if not is_reserved_central(central):
            warn(f"The specified central office code ({central}) means the generated phone number may correspond to a real person.")
    central_str = str(central).zfill(3)

    if line is None:
        if is_reserved_central(central):
            line = get_random_reserved_line()
        else:
            # Since the number is already potentially real, use the full range of possible line numbers.
            line = get_random_line()
    else:
        line = clamp(randint_from_input(line, get_random_reserved_line, log=log), LINE_MIN, LINE_MAX, log=log)
        # Don't send the warning if the central number is already non-reserved, as that makes this warning misleading.
        if is_reserved_central(central) and not is_reserved_line(line):
            warn(f"The specified line number ({line}) means the generated phone number may correspond to a real person.")
    line_str = str(line).zfill(4)

    return f"({area_str}) {central_str}-{line_str}"