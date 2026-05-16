from pytypes import text_regex_argtype, typo_weights_argtype
from argparse import ArgumentParser
from .main import TYPO_GENERATORS

def add_args_typos(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument(
        "--text", "-t",
        type=text_regex_argtype,
        default="Example text for typo generation.",
        help="The text to apply typos to. Should be only keyboard characters and spaces. (default: 'Example text for typo generation.')"
    )

    parser.add_argument(
        '--typos', '-ts',
        nargs="+",
        choices=TYPO_GENERATORS.keys(),
        default=TYPO_GENERATORS.keys(),
        help="Categories of typos to apply (default: all types)."
    )

    parser.add_argument(
        '--typo-weights', '-tw',
        nargs="+",
        type=typo_weights_argtype,
        help="Weights for each typo types. If not specified, all types will have equal weight."
    )
    parser.add_argument('--typo-rate', '-tr', type=float, default=0.1, help="Probability of applying a typo to each word (default: 0.1)")
    parser.add_argument('--typos-per-word', '-tpw', type=int, default=1, help="Maximum number of typos to apply per word (default: 1)")

    return parser