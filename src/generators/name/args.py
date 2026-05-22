from warnings import warn
from utils import arg_parser_has_arg
from global_pytypes import case_insensitive_choice_argtype, full_name_argtype, subdomain_count_argtype
from argparse import ArgumentParser, Namespace
from .vars import FILE_CATEGORIES, INSTRUMENT_CATEGORIES, MUSIC_GENRES, NAME_TYPES

def add_args_name(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument(
        '--name-type', '-nt',
        choices=NAME_TYPES,
        default='person',
        help="Type of name to generate (default: person)"
    )

    if not arg_parser_has_arg(parser, '--first-name'):
        parser.add_argument('--first-name', '-fn', help="First name to use for person name and username/email generation")
    if not arg_parser_has_arg(parser, '--last-name'):
        parser.add_argument('--last-name', '-ln', help="Last name to use for person name and username/email generation")

    if not arg_parser_has_arg(parser, '--full-name'):
        parser.add_argument(
            "--full-name", "-fln",
            type=full_name_argtype,
            nargs='?',
            help="Full name to use for person name/username/email generation. If provided, will be split into first and last name components and override --first-name and --last-name."
        )

    parser.add_argument(
        '--gender', '-ge',
        choices=['male', 'female', 'nb'],
        default=None,
        help="Gender for person/job name and username/email generation (default: random)"
    )

    parser.add_argument(
        '--file-category', '-fc',
        choices=FILE_CATEGORIES,
        default=None,
        help="File category for file_name generation"
    )
    parser.add_argument('--file-type', '-ft', help="File extension for file_name generation (overrides --file-category)")
    parser.add_argument('--subdomains', '-sd', type=subdomain_count_argtype, default=1, help="Number of subdomains for website generation (default: 1)")
    parser.add_argument(
        '--parent-music-genre', '-pmg',
        choices=MUSIC_GENRES,
        default=None,
        type=case_insensitive_choice_argtype(MUSIC_GENRES),
        help="Parent music genre for music_genre generation"
    )
    parser.add_argument(
        '--music-instrument-category', '-mic',
        choices=INSTRUMENT_CATEGORIES,
        default=None,
        type=case_insensitive_choice_argtype(INSTRUMENT_CATEGORIES),
        help="Instrument category for music_instrument generation"
    )

    parser.add_argument(
        '--first-only', '-fo',
        action='store_true',
        help="For person name generation, only return the first name component."
    )

    parser.add_argument(
        '--last-only', '-lo',
        action='store_true',
        help="For person name generation, only return the last name component."
    )

    return parser

def post_process_args_name(args: Namespace) -> Namespace:
    # If full name is provided, split it into first and last name components
    if args.type == 'name':
        if args.name_type in ['job', 'music_genre', 'music_instrument', 'vehicle']:
            warn(f"{args.name_type} generation will pick random values, but all will correspond to real entries in the Faker database for that category.")

        if args.full_name:
            first_name, last_name = args.full_name.split()
            args.first_name = first_name
            args.last_name = last_name

    return args