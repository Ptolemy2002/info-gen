import random
from typing import Callable, Any

def clamp(value: int, min_value: int, max_value: int, log: bool = False) -> int:
    """
        Clamp a value between a minimum and maximum value, inclusive on both ends.
    """
    if value < min_value:
        if log:
            print(f"Clamping value {value} to minimum {min_value}.")
        return min_value
    elif value > max_value:
        if log:
            print(f"Clamping value {value} to maximum {max_value}.")
        return max_value
    return value


def randint_from_input(i: str | int, fallback: Callable[[], int] | None = None, log: bool = False) -> int:
    """
        If the input is an integer, return it as-is. If it's a string with at least one digit character,
        replace any non-digit characters with random digits independently, and return the resulting integer.
        If there are no digit characters and a fallback is provided, call the fallback to get a value.
        If there are no digit characters and no fallback is provided, generate a random integer of the same length
        as the input string.
    """
    if isinstance(i, int):
        result = i
    else:
        try:
            result = int(i)
        except ValueError:
            if callable(fallback) and not any(c.isdigit() for c in i):
                result = fallback()
                if log:
                    print(f"Input '{i}' has no digits; used fallback function to generate integer {result}.")
                return result

            result_str = ""
            for c in i:
                if c.isdigit():
                    result_str += c
                else:
                    result_str += str(random.randint(0, 9))

            if log:
                print(f"Transformed input with digits '{i}' into integer {result_str} by replacing non-digits with random digits.")

            result = int(result_str)

    return result

def rand_pick_dstrb(options: list[tuple[int, Any]]) -> Any:
    """
        Given a list of (weight, value) pairs, randomly pick a value according to the distribution of weights.

        :param options: A list of (weight, value) pairs. Weights should be non-negative integers, and at least one should be greater than 0.
        :return: A randomly picked value from the options, with probability proportional to its weight.
    """
    total_weight = sum(weight for weight, _ in options)
    if total_weight == 0:
        raise ValueError("Total weight must be greater than 0.")
    
    r = random.uniform(0, total_weight)
    cumulative_weight = 0
    for weight, value in options:
        cumulative_weight += weight
        if r < cumulative_weight:
            return value
    
    # In case of rounding errors, return the last value
    return options[-1][1]