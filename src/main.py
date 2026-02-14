import argparse
import utils.output as output_utils
import random
import os
import faker
from utils.colors import clean_dirty_colors
from warnings import warn
from pytypes import *
from generators.ssn import gen_ssn
from generators.phone import gen_phone
from generators.address import gen_address, AddressArgs
from generators.typos import gen_typos, TYPO_GENERATORS, TypoArgs
from generators.color import gen_color, ColorArgs

# Put any files that are an output of the script here. "log.txt" will already exist.
OUTPUTS_DIR = output_utils.get_latest_outputs_dir("main")

def main(
        val_type: str = "ssn",
        count: int = 1,
        components: list[str] | None = None,
        address_args: AddressArgs={},
        state_abbr: bool = True,
        existing_city: bool = True,
        typo_args: TypoArgs = {
            'text': "Example text for typo generation.",
            'typos': list(TYPO_GENERATORS.keys()),
            'typo_weights': [1] * len(TYPO_GENERATORS),
            'typo_rate': 0.1,
            'typos_per_word': 1
        },
        color_args: ColorArgs = {}
    ):
    if components is None:
        components = []

    def component_or_default(index: int, default: str | None = None) -> str | None:
        if index < len(components):
            if components[index].lower() in ["none", "null"]:
                return None
            return components[index]
        return default

    results = []

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

    print("------- Output -------")
    for result in results:
        print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate fake but realistic US Social Security Numbers, phone numbers, addresses, typos, and colors for testing purposes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=output_utils.get_manual()
    )

    parser.add_argument(
        "--clean-dirty-colors", "-cdc",
        action="store_true",
        help="If set, will clean up the file at `assets/colors-dirty.json` by extracting valid color entries (and only the parts we need) and writing them to `assets/colors.json`, then abort without running further."
    )

    parser.add_argument(
        'type',
        choices=['ssn', 'phone', 'address', 'typos', 'color'],
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
    parser.add_argument('--building_number', help="Building number for address")
    parser.add_argument('--street', help="Street name for address")
    parser.add_argument('--city', help="City name for address")
    parser.add_argument('--state', help="State abbreviation for address")
    parser.add_argument('--zip', help="ZIP code for address")
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
    parser.add_argument('--min-r', type=rgb_bound_type, default=0, help="Minimum red value for color generation (0-255, default: 0)")
    parser.add_argument('--max-r', type=rgb_bound_type, default=255, help="Maximum red value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-r', '-r', type=rgb_bound_type, default=None, help="Exact red value for color generation (0-255). If specified, overrides min and max red values.")
    parser.add_argument('--min-g', type=rgb_bound_type, default=0, help="Minimum green value for color generation (0-255, default: 0)")
    parser.add_argument('--max-g', type=rgb_bound_type, default=255, help="Maximum green value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-g', '-g', type=rgb_bound_type, default=None, help="Exact green value for color generation (0-255). If specified, overrides min and max green values.")
    parser.add_argument('--min-b', type=rgb_bound_type, default=0, help="Minimum blue value for color generation (0-255, default: 0)")
    parser.add_argument('--max-b', type=rgb_bound_type, default=255, help="Maximum blue value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-b', '-b', type=rgb_bound_type, default=None, help="Exact blue value for color generation (0-255). If specified, overrides min and max blue values.")

    # Argument processing
    args = parser.parse_args()

    if args.clean_dirty_colors:
        clean_dirty_colors()
        print("Exiting after cleaning dirty colors.")
        exit(0)

    if args.seed is not None:
        print(f"Using provided seed: {args.seed}")
        faker.Faker.seed(args.seed)
        random.seed(args.seed)
    else:
        seed = int.from_bytes(os.urandom(args.seed_byte_size), 'big')
        print(f"No seed provided. Generated random seed {seed} from {args.seed_byte_size} bytes of entropy.")
        faker.Faker.seed(seed)
        random.seed(seed)

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

    main(args.type, args.count, components, address_args, not args.no_state_abbr, not args.no_existing_city, typo_args)