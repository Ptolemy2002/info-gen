import os
from warnings import warn
from argparse import ArgumentParser, Namespace
from utils import arg_parser_has_arg
from generators.date import int_month_day_pair_argtype
from .pytypes import duration_argtype

def add_args_date_adjust(parser: ArgumentParser) -> ArgumentParser:
    if not arg_parser_has_arg(parser, '--input-format'):
        parser.add_argument('--input-format', '-idf', default='%Y-%m-%d %H:%M:%S',
                            help="strptime format for --before/--after date strings (default: '%%Y-%%m-%%d %%H:%%M:%%S')")

    if not arg_parser_has_arg(parser, '--output-format'):
        parser.add_argument('--output-format', '-odf', default='%Y-%m-%d %I:%M:%S %p',
                            help="strftime format for the generated date (default: '%%Y-%%m-%%d %%I:%%M:%%S %%p')")

    parser.add_argument('--date', '-dte', default=None,
                        help="Base datetime for adjustment; parsed with --input-format")

    parser.add_argument('--duration', '-dur', type=duration_argtype, default="0s",
                        help="Duration to adjust the base datetime; parsed with parse_duration")

    parser.add_argument('--holidays', '-hol', nargs='*', type=int_month_day_pair_argtype, default=None,
                        help="List of holidays in 'Month/Day' format (e.g., '1/15'). If calculations" \
                        "cause the date to land on a holiday, it will be adjusted forward to the next non-holiday"
                        "(combines with --skip-weekends if present to adjust to the next non-holiday weekday).")
    
    parser.add_argument('--skip-weekends', '-sw', action='store_true',
                        help="If set, any adjustments that would land on a Saturday or Sunday will be adjusted forward to the next weekday" \
                        "(combines with --holidays if present to adjust to the next non-holiday weekday).")
    
    parser.add_argument('--month-length', '-ml', type=float, default=None,
                        help="If set, month adjustments will use this fixed month length instead of the adjusting actual calendar months" \
                        " and possibly losing precision if the target month has fewer days than the date of the source date (e.g., adjusting" \
                        "March 31 by -1 month with --month-length 30 would yield March 1, while without --month-length it would yield February 28 or 29).")

    return parser

def post_process_args_date_adjust(args: Namespace) -> Namespace:
    if args.type == 'date-adjust' and args.holidays is None:
        # See if the file `assets/holidays.txt` exists, and if so, use it as the default holidays list
        if os.path.isfile("src/assets/holidays.txt"):
            warn("No holidays provided for date adjustment, but found `src/assets/holidays.txt`. Using holidays from that file.")
            with open("src/assets/holidays.txt", 'r') as f:
                holidays = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                args.holidays = [int_month_day_pair_argtype(holiday) for holiday in holidays]
        else:
            warn("No holidays provided for date adjustment, and `src/assets/holidays.txt` not found. No holidays will be used.")
            args.holidays = []

    return args