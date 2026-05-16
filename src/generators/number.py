import random
from argparse import ArgumentParser
from utils import arg_parser_has_arg
from pytypes import number_precision_argtype

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
    
def add_args_number(parser: ArgumentParser) -> ArgumentParser:
    # These might have already been added by the username/email generator
    if not arg_parser_has_arg(parser, '--min'):
        parser.add_argument('--min', '-mn', type=float, default=0, help="Minimum value for number and username/email generation (default: 0)")
    if not arg_parser_has_arg(parser, '--max'):
        parser.add_argument('--max', '-mx', type=float, default=100, help="Maximum value for number and username/email generation (default: 100)")

    parser.add_argument(
        '--precision', '-p', type=number_precision_argtype, default=0,
        help="Number of decimal places for number generation. Must be a non-negative integer (default: 0)"
    )

    return parser