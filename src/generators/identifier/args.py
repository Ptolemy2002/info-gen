from global_pytypes import full_name_argtype
from utils import arg_parser_has_arg
from argparse import ArgumentParser, Namespace
from .vars import IDENTIFIER_TYPES

def add_args_identifier(parser: ArgumentParser) -> ArgumentParser:
    if not arg_parser_has_arg(parser, '--first-name'):
        parser.add_argument(
            '--first-name', '-fn', help="First name to use for person name and username/email generation")
    if not arg_parser_has_arg(parser, '--last-name'):
        parser.add_argument(
            '--last-name', '-ln', help="Last name to use for person name and username/email generation")

    if not arg_parser_has_arg(parser, '--full-name'):
        parser.add_argument(
            "--full-name", "-fln",
            type=full_name_argtype,
            nargs='?',
            help="Full name to use for person name/username/email generation. If provided, will be split into first and last name components and override --first-name and --last-name."
        )

    parser.add_argument(
        '--identifier-type', '-idt',
        choices=IDENTIFIER_TYPES,
        default='email',
        help="Type of identifier to generate (default: email)"
    )
    parser.add_argument('--user-name', '-un',
                        help="Username to use for email generation")
    parser.add_argument('--domain', '-dm',
                        help="Domain to use for email generation")
    parser.add_argument('--domain-type', '-dt', choices=['personal', 'business'], default=None,
                        help="Type of domain to use for email generation if domain is not specified (default: random)")

    return parser

def post_process_args_identifier(args: Namespace) -> Namespace:
    # If full name is provided, split it into first and last name components
    if args.type == 'identifier' and args.full_name:
        first_name, last_name = args.full_name.split()
        args.first_name = first_name
        args.last_name = last_name

    return args