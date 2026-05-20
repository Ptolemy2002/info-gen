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
from generators import gen_ssn, gen_phone, gen_name, gen_address, gen_typos, gen_color, gen_number, gen_identifier, gen_date, \
                       gen_date_adjust, \
                       AddressArgs, TypoArgs, ColorArgs, NameArgs, IdentifierArgs, DateArgs, DateAdjustArgs, TYPO_GENERATORS, \
                       add_args_number, add_args_phone, add_args_ssn, add_args_address, add_args_typos, add_args_color, \
                       add_args_name, add_args_identifier, add_args_date, add_args_date_adjust, \
                       post_process_args_date_adjust, post_process_args_name, post_process_args_identifier, \
                       post_process_args_color
from global_pytypes import *
from file_parse import (extract_interpolations, unique_interpolation_map,
                        resolve_interpolation_args, resolve_static_value,
                        apply_interpolations)
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
        date_args: DateArgs = cast(DateArgs, {}),
        date_adjust_args: DateAdjustArgs = cast(DateAdjustArgs, {}),
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

    if val_type == "date":
        for _ in range(count):
            results.append(gen_date(date_args, log=True))

    if val_type == "date-adjust":
        for _ in range(count):
            results.append(gen_date_adjust(date_adjust_args, log=True))

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
        description="Generate fake but realistic information for testing purposes.",
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
        help="If set, will clean up the file at `assets/colors-dirty.json` by extracting valid color entries"
        "(and only the parts we need) and writing them to `assets/colors.json`, then abort without running further."
    )

    parser = add_args_phone(parser)
    parser = add_args_ssn(parser)
    parser = add_args_number(parser)
    parser = add_args_address(parser)
    parser = add_args_typos(parser)
    parser = add_args_color(parser)
    parser = add_args_name(parser)
    parser = add_args_identifier(parser)
    parser = add_args_date(parser)
    parser = add_args_date_adjust(parser)

    parser.add_argument(
        'type',
        choices=['ssn', 'phone', 'address', 'typos', 'color', 'name', 'number', 'identifier', 'date', 'date-adjust'],
        default='ssn',
        nargs='?',
        help="Type of information to generate (default: ssn)"
    )

    parser.add_argument(
        'count',
        type=count_argtype,
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

    if args.clean_dirty_colors:
        clean_dirty_colors()
        print("Exiting after cleaning dirty colors.")
        exit(0)

    if args.usage:
        parser.print_usage()
        exit(0)

    if args.manual:
        print(output_utils.get_manual())
        exit(0)

    # Post-processing and warning messages
    args = post_process_args_name(args)
    args = post_process_args_identifier(args)
    args = post_process_args_color(args)
    args = post_process_args_date_adjust(args)

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

    name_args: NameArgs = {
        'first_name': args.first_name,
        'last_name': args.last_name,
        'gender': args.gender,
        'file_category': args.file_category,
        'file_type': args.file_type,
        'subdomains': args.subdomains,
        'music_genre': args.parent_music_genre,
        'music_instrument_category': args.music_instrument_category
    }

    identifier_args: IdentifierArgs = {
        'first_name': args.first_name,
        'last_name': args.last_name,
        'gender': args.gender,
        'username': args.user_name,
        'domain': args.domain,
        'min': args.min,
        'max': args.max,
        'domain_type': args.domain_type,
    }

    date_args: DateArgs = {
        'input_format': args.input_format,
        'output_format': args.output_format,
        'before': args.before,
        'after': args.after,
        'season': args.season,
        'min_year': args.min_year,
        'max_year': args.max_year,
        'exact_year': args.exact_year,
        'min_month': args.min_month,
        'max_month': args.max_month,
        'exact_month': args.exact_month,
        'min_day': args.min_day,
        'max_day': args.max_day,
        'exact_day': args.exact_day,
        'min_hour': args.min_hour,
        'max_hour': args.max_hour,
        'exact_hour': args.exact_hour,
        'min_minute': args.min_minute,
        'max_minute': args.max_minute,
        'exact_minute': args.exact_minute,
        'min_second': args.min_second,
        'max_second': args.max_second,
        'exact_second': args.exact_second,
        'astronomical_season_bounds': args.astronomical_season_bounds
    }

    date_adjust_args: DateAdjustArgs = {
        'input_format': args.input_format,
        'output_format': args.output_format,
        'date': args.date,
        'duration': args.duration,
        'holidays': args.holidays,
        'skip_weekends': args.skip_weekends,
        'month_length': args.month_length
    }

    return main(
        args.type, args.count, components, address_args,
        not args.no_state_abbr, not args.no_existing_city,
        typo_args, color_args, name_args=name_args, name_type=args.name_type,
        identifier_args=identifier_args, identifier_type=args.identifier_type,
        min_val=args.min, max_val=args.max, precision=args.precision,
        date_args=date_args, date_adjust_args=date_adjust_args
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
                interp = interp_map[ident]

                if interp.static:
                    print(f"------- Resolving static '{ident}' ({marker}) -------")
                    result = resolve_static_value(interp, values)
                    print(f"Static value for id '{ident}': {result}")
                    values[ident] = result
                    continue

                inner_args_lst = resolve_interpolation_args(interp, values)
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
            
            outputs.append(apply_interpolations(text, values))
        
        print("------- Final Outputs -------")
        for i in range(args.count):
            print(f"------- {i + 1}/{args.count} -------")
            print(outputs[i])
            
    else:
        main_exec(args)