import random
from argparse import ArgumentParser
from utils import arg_parser_has_arg
from global_pytypes import number_precision_argtype, number_field_length_argtype

def gen_number(min: float, max: float, precision: int = 0, field_length: int = 0, log: bool = False) -> str:
    """
        Generate a random number between the given minimum and maximum values, with the specified precision.

        :param min: The minimum value for the generated number.
        :param max: The maximum value for the generated number.
        :param precision: The number of decimal places to include in the generated number. Default is 0 (integer).
        :param padding: The minimum total length of the generated number, including decimal point and digits. Default is 0.
    """
    if min > max:
        raise ValueError("Minimum value cannot be greater than maximum value.")
    
    if precision == 0:
        if log: print(f"Generating integer due to precision=0. Range: [{int(min)}, {int(max)}]")
        num = random.randint(int(min), int(max))
    else:
        if log: print(f"Generating float with precision={precision}. Range: [{min}, {max}]")
        full_range = max - min
        num = min + (random.random() * full_range)
        factor = 10 ** precision
        num = round(num * factor) / factor
    
    if log: print(f"Generated number before applying field length: {num}")

    num_str = str(num)
    if field_length > 0:
        if log: print(f"Applying field length={field_length}.")
        num_str = num_str.zfill(field_length)

    return num_str

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

    parser.add_argument(
        '--field-length', '-fl', type=number_field_length_argtype, default=0,
        help="Minimum total length of the generated number, including decimal point and digits." \
        " If the generated number is shorter than this length, it will be left-padded with zeros (default: 0)"
    )

    return parser