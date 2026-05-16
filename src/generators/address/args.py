from utils import arg_parser_has_arg
from argparse import ArgumentParser

def add_args_address(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument('--building_number', '-bn', help="Building number for address")
    parser.add_argument('--street', '-ste', help="Street name for address")
    parser.add_argument('--city', '-ci', help="City name for address")
    parser.add_argument('--state', '-st', help="State abbreviation for address")
    parser.add_argument('--zip', '-z', help="ZIP code for address")
    parser.add_argument('--no-state-abbr', action='store_true', help="Do not convert state names to abbreviations")
    parser.add_argument('--no-existing-city', action='store_true', help="Do not use existing city names; generate random city names instead")
    return parser