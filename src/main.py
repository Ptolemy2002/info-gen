import argparse
from argparse import Namespace
import random
import os
import sys
import faker
from warnings import warn
import utils.output as output_utils
from typing import cast
from utils import clean_dirty_colors
from generators import gen_ssn, gen_phone, gen_name, gen_address, gen_typos, gen_color, gen_number, gen_identifier, \
                       AddressArgs, TypoArgs, ColorArgs, NameArgs, IdentifierArgs, TYPO_GENERATORS, NAME_TYPES, \
                       FILE_CATEGORIES, MUSIC_GENRES, INSTRUMENT_CATEGORIES, IDENTIFIER_TYPES
from pytypes import *
from file_parse import (extract_interpolations, unique_interpolation_map,
                        resolve_interpolation_args, apply_interpolations)
import zlib

# Put any files that are an output of the script here. "log.txt" will already exist.
OUTPUTS_DIR = output_utils.get_latest_outputs_dir("main")

def main(
        val_type: str = "ssn",
        count: int = 1,
        components: list[str] | None = None,
        address_args: AddressArgs = cast(AddressArgs, {}),
        state_abbr: bool = True,
        existing_city: bool = True,
        typo_args: TypoArgs = cast(TypoArgs, {
            'text': "Example text for typo generation.",
            'typos': list(TYPO_GENERATORS.keys()),
            'typo_weights': [1] * len(TYPO_GENERATORS),
            'typo_rate': 0.1,
            'typos_per_word': 1
        }),
        color_args: ColorArgs = cast(ColorArgs, {}),
        name_args: NameArgs = cast(NameArgs, {}),
        name_type: str = "person",
        identifier_args: IdentifierArgs = cast(IdentifierArgs, {}),
        identifier_type: str = "email",
        min_val: float = 0,
        max_val: float = 100,
        precision: int = 0,
    ) -> list[str]:
    if components is None:
        components = []

    def component_or_default(index: int, default: str | None = None) -> str | None:
        if index < len(components):
            if components[index].lower() in ["none", "null"]:
                return None
            return components[index]
        return default

    results: list[str] = []

    if val_type == "ssn":
        start = component_or_default(0)
        mid = component_or_default(1)
        end = component_or_default(2)
        for _ in range(count):
            results.append(gen_ssn(start, mid, end, log=True))

    if val_type == "phone":
        area = component_or_default(0)
        central = component_or_default(1)
        line = component_or_default(2)
        for _ in range(count):
            results.append(gen_phone(area, central, line, log=True))

    if val_type == "address":
        for _ in range(count):
            results.append(gen_address(address_args, state_abbr, existing_city, log=True))

    if val_type == "typos":
        typo_distrb = [(int(typo_args['typo_weights'][i]), typo) for i, typo in enumerate(typo_args['typos'])]
        for _ in range(count):
            results.append(gen_typos(typo_args['text'], typo_distrb, typo_args['typo_rate'], typo_args['typos_per_word'], log=True))

    if val_type == "color":
        for _ in range(count):
            results.append(gen_color(color_args, log=True))

    if val_type == "name":
        for _ in range(count):
            results.append(gen_name(name_type, name_args, log=True))

    if val_type == "number":
        for _ in range(count):
            results.append(gen_number(min_val, max_val, precision, log=True))

    if val_type == "identifier":
        for _ in range(count):
            results.append(gen_identifier(identifier_type, identifier_args, log=True))

    print("------- Output -------")
    for result in results:
        print(result)

    return results

def gen_seed(seed_byte_size: int = 16) -> int:
    seed = int.from_bytes(os.urandom(seed_byte_size), 'big')
    print(f"Generated random seed {seed} from {seed_byte_size} bytes of entropy.")
    return seed

def derive_seed(base: int, identifier: str, seed_byte_size: int = 16) -> int:
    # Derive a new seed based on the base seed and the identifier using a hash function
    derived_seed = (base + zlib.crc32(identifier.encode())) % (2**(8 * seed_byte_size))
    return derived_seed

def apply_seed(seed: int):
    faker.Faker.seed(seed)
    random.seed(seed)

def parse_args(og_args: list[str]) -> Namespace:
    parser = argparse.ArgumentParser(
        description="Generate fake but realistic numbers, US Social Security Numbers, phone numbers, addresses, typos, names, and colors for testing purposes.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--usage", "-u",
        action="store_true",
        help="Print usage instructions and examples, then exit."
    )

    parser.add_argument(
        "--manual", "-m",
        action="store_true",
        help="Print detailed manual, then exit."
    )

    parser.add_argument(
        "--clean-dirty-colors", "-cdc",
        action="store_true",
        help="If set, will clean up the file at `assets/colors-dirty.json` by extracting valid color entries (and only the parts we need) and writing them to `assets/colors.json`, then abort without running further."
    )

    parser.add_argument(
        'type',
        choices=['ssn', 'phone', 'address', 'typos', 'color', 'name', 'number', 'identifier'],
        default='ssn',
        nargs='?',
        help="Type of information to generate (default: ssn)"
    )

    def count_type(s: str) -> int:
        try:
            value = int(s)
            if value < 1:
                raise argparse.ArgumentTypeError("Count must be a positive integer.")
            return value
        except ValueError:
            raise argparse.ArgumentTypeError("Count must be a positive integer.")

    parser.add_argument(
        'count',
        type=count_type,
        default=1,
        nargs='?',
        help="Number of identifiers to generate (default: 1)"
    )

    parser.add_argument(
        "--seed", "-s",
        nargs='?',
        type=int,
        default=None,
        help="Optional seed for random generators to produce deterministic results."
    )

    parser.add_argument(
        '--seed-byte-size', '-sb',
        type=int,
        default=16,
        help="Number of random bytes to use for seed generation if no seed is provided (default: 16)."
    )

    # Common arguments for SSN and phone (freeform components)
    parser.add_argument(
        '--components', '-c',
        nargs='*',
        help="Optional components with patterns for SSN/phone. Use digits for fixed values, non-digits (like 'x') for random digits. Separate with spaces or dashes."
    )

    # Specific arguments for address generation
    parser.add_argument('--building_number', '-bn', help="Building number for address")
    parser.add_argument('--street', '-ste', help="Street name for address")
    parser.add_argument('--city', '-ci', help="City name for address")
    parser.add_argument('--state', '-st', help="State abbreviation for address")
    parser.add_argument('--zip', '-z', help="ZIP code for address")
    parser.add_argument('--no-state-abbr', action='store_true', help="Do not convert state names to abbreviations")
    parser.add_argument('--no-existing-city', action='store_true', help="Do not use existing city names; generate random city names instead")

    # Specific arguments for typo generation
    parser.add_argument(
        "--text", "-t",
        type=text_regex_type,
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
        type=typo_weights_type,
        help="Weights for each typo types. If not specified, all types will have equal weight."
    )
    parser.add_argument('--typo-rate', '-tr', type=float, default=0.1, help="Probability of applying a typo to each word (default: 0.1)")
    parser.add_argument('--typos-per-word', '-tpw', type=int, default=1, help="Maximum number of typos to apply per word (default: 1)")
    
    # Specific arguments for color generation
    parser.add_argument('--min-r', '-mnr', type=rgb_bound_type, default=0, help="Minimum red value for color generation (0-255, default: 0)")
    parser.add_argument('--max-r', '-mxr', type=rgb_bound_type, default=255, help="Maximum red value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-r', '-r', type=rgb_bound_type, default=None, help="Exact red value for color generation (0-255). If specified, overrides min and max red values.")
    parser.add_argument('--min-g', '-mng', type=rgb_bound_type, default=0, help="Minimum green value for color generation (0-255, default: 0)")
    parser.add_argument('--max-g', '-mxg', type=rgb_bound_type, default=255, help="Maximum green value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-g', '-g', type=rgb_bound_type, default=None, help="Exact green value for color generation (0-255). If specified, overrides min and max green values.")
    parser.add_argument('--min-b', '-mnb', type=rgb_bound_type, default=0, help="Minimum blue value for color generation (0-255, default: 0)")
    parser.add_argument('--max-b', '-mxb', type=rgb_bound_type, default=255, help="Maximum blue value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-b', '-b', type=rgb_bound_type, default=None, help="Exact blue value for color generation (0-255). If specified, overrides min and max blue values.")

    # Specific arguments for name generation
    def full_name_type(s: str) -> str:
        if s.count(' ') < 1:
            raise argparse.ArgumentTypeError("Full name must contain at least a first name and a last name separated by space.")
        return s

    parser.add_argument(
        '--name-type', '-nt',
        choices=NAME_TYPES,
        default='person',
        help="Type of name to generate (default: person)"
    )
    parser.add_argument('--first-name', '-fn', help="First name to use for person name and username/email generation")
    parser.add_argument('--last-name', '-ln', help="Last name to use for person name and username/email generation")
    parser.add_argument(
        '--gender', '-ge',
        choices=['male', 'female', 'nb'],
        default=None,
        help="Gender for person/job name and username/email generation (default: random)"
    )
    parser.add_argument(
        "--full_name", "-fln",
        type=full_name_type,
        nargs='?',
        help="Full name to use for person name/username/email generation. If provided, will be split into first and last name components and override --first-name and --last-name."
    )

    parser.add_argument(
        '--file-category', '-fc',
        choices=FILE_CATEGORIES,
        default=None,
        help="File category for file_name generation"
    )
    parser.add_argument('--file-type', '-ft', help="File extension for file_name generation (overrides --file-category)")
    parser.add_argument('--subdomains', '-sd', type=subdomain_count_type, default=1, help="Number of subdomains for website generation (default: 1)")
    parser.add_argument(
        '--parent-music-genre', '-pmg',
        choices=MUSIC_GENRES,
        default=None,
        type=case_insensitive_choice_type(MUSIC_GENRES),
        help="Parent music genre for music_genre generation"
    )
    parser.add_argument(
        '--music-instrument-category', '-mic',
        choices=INSTRUMENT_CATEGORIES,
        default=None,
        type=case_insensitive_choice_type(INSTRUMENT_CATEGORIES),
        help="Instrument category for music_instrument generation"
    )

    # Specific arguments for number generation
    def precision_type(s: str) -> int:
        try:
            value = int(s)
            if value < 0:
                raise argparse.ArgumentTypeError("Precision must be a non-negative integer.")
            return value
        except ValueError:
            raise argparse.ArgumentTypeError("Precision must be a non-negative integer.")
        
    parser.add_argument('--min', '-mn', type=float, default=0, help="Minimum value for number and username/email generation (default: 0)")
    parser.add_argument('--max', '-mx', type=float, default=100, help="Maximum value for number and username/email generation (default: 100)")
    parser.add_argument(
        '--precision', '-p', type=precision_type, default=0,
        help="Number of decimal places for number generation. Must be a non-negative integer (default: 0)"
    )

    # Specific arguments for identifier generation
    parser.add_argument(
        '--identifier-type', '-idt',
        choices=IDENTIFIER_TYPES,
        default='email',
        help="Type of identifier to generate (default: email)"
    )
    parser.add_argument('--user-name', '-un', help="Username to use for email generation")
    parser.add_argument('--domain', '-dm', help="Domain to use for email generation")
    parser.add_argument('--domain-type', '-dt', choices=['personal', 'business'], default=None, help="Type of domain to use for email generation if domain is not specified (default: random)")

    # File input argument for interpolation processing
    parser.add_argument(
        "--file", "-f",
        nargs='?',
        type=argparse.FileType('r'),
        help=
            "Path to input file. If provided, will read the file and "
            "generate output for each interpolation token found, then "
            "substitute them in the text and print the final result."
    )

    # Argument processing
    args = parser.parse_args(og_args)

    if args.full_name:
        if args.first_name or args.last_name:
            warn("Full name provided; overriding first name and last name arguments.")
        split = args.full_name.split()
        args.first_name = split[0]
        args.last_name = split[-1]

    if args.clean_dirty_colors:
        clean_dirty_colors()
        print("Exiting after cleaning dirty colors.")
        exit(0)

    if args.type == 'color':
        warn("Color generation will pick random values, but all will correspond to an actual color.")

    if args.type == 'name' and args.name_type in ['job', 'music_genre', 'music_instrument', 'vehicle']:
        warn(f"{args.name_type} generation will pick random values, but all will correspond to real entries in the Faker database for that category.")

    if args.usage:
        parser.print_usage()
        exit(0)

    if args.manual:
        print(output_utils.get_manual())
        exit(0)

    return args

def main_exec(args: Namespace) -> list[str]:
    if args.seed is not None:
        print(f"Using seed: {args.seed}")
        apply_seed(args.seed)
    else:
        print(f"No seed provided.")
        seed = gen_seed(args.seed_byte_size)
        apply_seed(seed)
    
    address_args: AddressArgs = {
        'building_number': str(args.building_number) if args.building_number is not None else None,
        'street': str(args.street) if args.street is not None else None,
        'city': str(args.city) if args.city is not None else None,
        'state': str(args.state) if args.state is not None else None,
        'zip': str(args.zip) if args.zip is not None else None
    }

    typo_args: TypoArgs = {
        'text': args.text,
        'typos': args.typos,
        'typo_weights': args.typo_weights if args.typo_weights else [],
        'typo_rate': args.typo_rate,
        'typos_per_word': args.typos_per_word
    }

    if args.type == "typos" and len(typo_args['typo_weights']) < len(typo_args['typos']):
        warn(f"Fewer typo weights provided than typo types. Missing weights will be set to 1.")
        typo_args['typo_weights'].extend([1] * (len(typo_args['typos']) - len(typo_args['typo_weights'])))

    # Split components at dashes to allow formats like "666-12-3456"
    # Only used for SSN and phone types
    components = []
    if args.components:
        for component in args.components:
            if '-' in component:
                components.extend(component.split('-'))
            else:
                components.append(component)

    color_args: ColorArgs = {
        'min_r': args.min_r,
        'max_r': args.max_r,
        'exact_r': args.exact_r,
        'min_g': args.min_g,
        'max_g': args.max_g,
        'exact_g': args.exact_g,
        'min_b': args.min_b,
        'max_b': args.max_b,
        'exact_b': args.exact_b,
    }

    name_args: NameArgs = {}
    if args.first_name is not None:
        name_args['first_name'] = args.first_name
    if args.last_name is not None:
        name_args['last_name'] = args.last_name
    if args.gender is not None:
        name_args['gender'] = args.gender
    if args.file_category is not None:
        name_args['file_category'] = args.file_category
    if args.file_type is not None:
        name_args['file_type'] = args.file_type
    name_args['subdomains'] = args.subdomains
    if args.parent_music_genre is not None:
        name_args['music_genre'] = args.parent_music_genre
    if args.music_instrument_category is not None:
        name_args['music_instrument_category'] = args.music_instrument_category

    identifier_args: IdentifierArgs = {}
    if args.first_name is not None:
        identifier_args['first_name'] = args.first_name
    if args.last_name is not None:
        identifier_args['last_name'] = args.last_name
    if args.gender is not None:
        identifier_args['gender'] = args.gender
    if args.user_name is not None:
        identifier_args['username'] = args.user_name
    if args.domain is not None:
        identifier_args['domain'] = args.domain
    if args.min is not None:
        identifier_args['min'] = args.min
    if args.max is not None:
        identifier_args['max'] = args.max
    if args.domain_type is not None:
        identifier_args['domain_type'] = args.domain_type

    return main(
        args.type, args.count, components, address_args,
        not args.no_state_abbr, not args.no_existing_city,
        typo_args, color_args, name_args=name_args, name_type=args.name_type,
        identifier_args=identifier_args, identifier_type=args.identifier_type,
        min_val=args.min, max_val=args.max, precision=args.precision
    )

def _topo_sort_interpolations(interp_map: dict) -> list[str]:
    """Return interpolation IDs ordered so each dependency precedes its dependents."""
    visited: set[str] = set()
    order: list[str] = []

    def visit(ident: str, ancestors: set[str]):
        if ident in ancestors:
            raise ValueError(f"Circular dependency in interpolations involving '{ident}'")
        if ident in visited:
            return
        for dep in interp_map[ident].result_deps:
            if dep not in interp_map:
                raise ValueError(
                    f"Interpolation '{ident}' references $({{dep}}), but '{dep}' is not defined"
                )
            visit(dep, ancestors | {ident})
        visited.add(ident)
        order.append(ident)

    for ident in interp_map:
        visit(ident, set())

    return order


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.seed is None:
        print(f"No seed provided.")
        args.seed = gen_seed(args.seed_byte_size)
        apply_seed(args.seed)

    if args.file:
        text = args.file.read()
        interpolations = extract_interpolations(text)

        print(f"Found {len(interpolations)} interpolation(s) in the file.")

        outputs: list[str] = []
        for i in range(args.count):
            marker = f"{i + 1}/{args.count}"
            print(f"------- Processing Interpolations ({marker}) -------")

            values = {}
            interp_map = unique_interpolation_map(interpolations)
            for ident in _topo_sort_interpolations(interp_map):
                inner_args_lst = resolve_interpolation_args(interp_map[ident], values)
                try:
                    inner_args = parse_args(inner_args_lst)
                except SystemExit:
                    print(f"Unexpected exit while parsing arguments for interpolation '{ident}'. Arguments: {inner_args_lst}")
                    raise

                # Vary the seed based on the identifier to ensure different results
                # for each interpolation, but in a deterministic way. Add the index
                # to ensure the same file generates differently on each run.
                inner_args.seed = derive_seed(inner_args.seed if inner_args.seed is not None else args.seed, f"{i}_{ident}", args.seed_byte_size)
                
                print(f"------- Processing '{ident}' ({marker}) -------")
                results = main_exec(inner_args)
                print("------- End Generation -------")
                
                # Get the last result so that the count argument can be used to force N
                # generations before a final value (could be useful if using seeds in interpolations)
                result = results[-1] if results else ""
                if inner_args.type == "color" and result:
                    # Get just the part that comes before the first dash, and strip whitespace
                    result = result.split('-')[0].strip()

                if result:
                    print(f"Generated value for id '{ident}': {result}")
                    values[ident] = result
                
                i += 1
            
            outputs.append(apply_interpolations(text, values))
        
        print("------- Final Outputs -------")
        for i in range(args.count):
            print(f"------- {i + 1}/{args.count} -------")
            print(outputs[i])
            
    else:
        main_exec(args)