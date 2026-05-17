from .pytypes import month_argtype, season_argtype, hour_argtype
from argparse import ArgumentParser

def add_args_date(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument('--input-format', '-idf', default='%Y-%m-%d %H:%M:%S',
                        help="strptime format for --before/--after date strings (default: '%%Y-%%m-%%d %%H:%%M:%%S')")
    parser.add_argument('--output-format', '-odf', default='%Y-%m-%d %I:%M:%S %p',
                        help="strftime format for the generated date (default: '%%Y-%%m-%%d %%I:%%M:%%S %%p')")
    parser.add_argument('--before', '-bf', default=None,
                        help="Upper bound datetime (inclusive); parsed with --input-format")
    parser.add_argument('--after', '-af', default=None,
                        help="Lower bound datetime (inclusive); parsed with --input-format")
    parser.add_argument('--season', '-sn', type=season_argtype, default=None,
                        help="Restrict to a meteorological season: spring, summer, autumn/fall, winter (or 1–4)")
    parser.add_argument('--min-year', '-mny', type=int,
                        default=None, help="Minimum year for date generation")
    parser.add_argument('--max-year', '-mxy', type=int,
                        default=None, help="Maximum year for date generation")
    parser.add_argument('--exact-year', '-ey', type=int,
                        default=None, help="Exact year for date generation")
    parser.add_argument('--min-month', '-mnmo', type=month_argtype,
                        default=None, help="Minimum month (name or 1–12)")
    parser.add_argument('--max-month', '-mxmo', type=month_argtype,
                        default=None, help="Maximum month (name or 1–12)")
    parser.add_argument('--exact-month', '-emo', type=month_argtype,
                        default=None, help="Exact month (name or 1–12)")
    parser.add_argument('--min-day', '-mnd', type=int,
                        default=None, help="Minimum day of month")
    parser.add_argument('--max-day', '-mxd', type=int,
                        default=None, help="Maximum day of month")
    parser.add_argument('--exact-day', '-exd', type=int,
                        default=None, help="Exact day of month")
    parser.add_argument('--min-hour', '-mnh', type=hour_argtype,
                        default=None, help="Minimum hour (0–23 or 1–12am/pm)")
    parser.add_argument('--max-hour', '-mxh', type=hour_argtype,
                        default=None, help="Maximum hour (0–23 or 1–12am/pm)")
    parser.add_argument('--exact-hour', '-exh', type=hour_argtype,
                        default=None, help="Exact hour (0–23 or 1–12am/pm)")
    parser.add_argument('--min-minute', '-mnmi', type=int,
                        default=None, help="Minimum minute (0–59)")
    parser.add_argument('--max-minute', '-mxmi', type=int,
                        default=None, help="Maximum minute (0–59)")
    parser.add_argument('--exact-minute', '-exmi', type=int,
                        default=None, help="Exact minute (0–59)")
    parser.add_argument('--min-second', '-mnsc', type=int,
                        default=None, help="Minimum second (0–59)")
    parser.add_argument('--max-second', '-mxsc', type=int,
                        default=None, help="Maximum second (0–59)")
    parser.add_argument('--exact-second', '-exsc', type=int,
                        default=None, help="Exact second (0–59)")
    return parser
