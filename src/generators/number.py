import random

def gen_number(min: float, max: float, precision: int = 0, log: bool = False) -> str:
    """
        Generate a random number between the given minimum and maximum values, with the specified precision.

        :param min: The minimum value for the generated number.
        :param max: The maximum value for the generated number.
        :param precision: The number of decimal places to include in the generated number. Default is 0 (integer).
    """
    if min > max:
        raise ValueError("Minimum value cannot be greater than maximum value.")
    
    if precision == 0:
        return str(random.randint(int(min), int(max)))
    else:
        full_range = max - min
        num = min + (random.random() * full_range)
        factor = 10 ** precision
        return str(round(num * factor) / factor)