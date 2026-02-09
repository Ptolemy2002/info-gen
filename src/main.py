import argparse
import utils.output as output_utils
import random
import os
import faker
import utils.location as location_utils
from typo.main import *
from typo.vars import letters, digits, all_characters, filler_words
from utils.colors import *
from typing import Any, Callable, NotRequired
from warnings import warn

# Put any files that are an output of the script here. "log.txt" will already exist.
OUTPUTS_DIR = output_utils.get_latest_outputs_dir("main")

# Constants for SSN validation
SSN_START_MIN = 0
SSN_START_MAX = 999
SSN_MID_MIN = 0
SSN_MID_MAX = 99
SSN_END_MIN = 0
SSN_END_MAX = 9999

# Constants for phone number validation
AREA_CODE_MIN = 200
AREA_CODE_MAX = 999
CENTRAL_MIN = 200
CENTRAL_MAX = 999
LINE_MIN = 0
LINE_MAX = 9999

# Reserved values
RESERVED_CENTRAL = 555
RESERVED_LINE_MIN = 100
RESERVED_LINE_MAX = 199
RESERVED_SSN_START_COUNT = 102  # 000, 666, and 900-999

# Constants for zip code validation
ZIPCODE_MIN = 0
ZIPCODE_MAX = 99999

# Set of available typo generators
TYPO_GENERATORS: dict[str, TypoGenerator] = {
    "let-ins": TypoInsertionGenerator(letters),
    "let-sub": TypoSubstitutionGenerator(letters),

    "digit-ins": TypoInsertionGenerator(digits),
    "digit-sub": TypoSubstitutionGenerator(digits),

    "char-ins": TypoInsertionGenerator(all_characters),
    "char-sub": TypoSubstitutionGenerator(all_characters),

    "kb-ins": TypoKeyboardProximityInsertionGenerator(False),
    "kb-sub": TypoKeyboardProximitySubstitutionGenerator(False),

    "kb-ins-as": TypoKeyboardProximityInsertionGenerator(True),
    "kb-sub-as": TypoKeyboardProximitySubstitutionGenerator(True),

    "trans": TypoTranspositionGenerator(),
    "del": TypoDeletionGenerator(),
    "case": TypoCaseChangeGenerator(),
    "word-dup": TypoWordRepetitionGenerator(),

    "dbl-miss": TypoMissedDoubleGenerator(),
    "dbl-ins": TypoExtraDoubleGenerator(),

    "filler-ins": TypoFillerWordInsertionGenerator(filler_words),

    "homophone": TypoHomophoneGenerator()
}

def rand_pick_dstrb(options: list[tuple[int, Any]]) -> Any:
    """
        Given a list of (weight, value) pairs, randomly pick a value according to the distribution of weights.

        :param options: A list of (weight, value) pairs. Weights should be non-negative integers, and at least one should be greater than 0.
        :return: A randomly picked value from the options, with probability proportional to its weight.
    """
    total_weight = sum(weight for weight, _ in options)
    if total_weight == 0:
        raise ValueError("Total weight must be greater than 0.")
    
    r = random.uniform(0, total_weight)
    cumulative_weight = 0
    for weight, value in options:
        cumulative_weight += weight
        if r < cumulative_weight:
            return value
    
    # In case of rounding errors, return the last value
    return options[-1][1]

def randint_from_input(i: str | int, fallback: Callable[[], int] | None = None, log: bool = False) -> int:
    """
        If the input is an integer, return it as-is. If it's a string with at least one digit character,
        replace any non-digit characters with random digits independently, and return the resulting integer.
        If there are no digit characters and a fallback is provided, call the fallback to get a value.
        If there are no digit characters and no fallback is provided, generate a random integer of the same length
        as the input string.
    """
    if isinstance(i, int):
        result = i
    else:
        try:
            result = int(i)
        except ValueError:
            if callable(fallback) and not any(c.isdigit() for c in i):
                result = fallback()
                if log:
                    print(f"Input '{i}' has no digits; used fallback function to generate integer {result}.")
                return result

            result_str = ""
            for c in i:
                if c.isdigit():
                    result_str += c
                else:
                    result_str += str(random.randint(0, 9))

            if log:
                print(f"Transformed input with digits '{i}' into integer {result_str} by replacing non-digits with random digits.")

            result = int(result_str)

    return result

def clamp(value: int, min_value: int, max_value: int, log: bool = False) -> int:
    """
        Clamp a value between a minimum and maximum value, inclusive on both ends.
    """
    if value < min_value:
        if log:
            print(f"Clamping value {value} to minimum {min_value}.")
        return min_value
    elif value > max_value:
        if log:
            print(f"Clamping value {value} to maximum {max_value}.")
        return max_value
    return value

def format_component(
    value: int | str | None,
    min_val: int,
    max_val: int,
    width: int,
    fallback_fn: Callable[[], int],
    log: bool = False
) -> tuple[int, str]:
    """
        Helper to process and format a component (SSN/phone part).
        Returns both the integer value and the zero-padded string.
    """
    if value is None:
        int_val = fallback_fn()
    else:
        int_val = clamp(randint_from_input(value, fallback_fn, log=log), min_val, max_val, log=log)
    return int_val, str(int_val).zfill(width)

def gen_ssn(start: int | str | None = None, mid: int  | str | None = None, end: int | str | None = None, log: bool = False) -> str:
    """
        Generate a random US Social Security Number (SSN).
        The SSA reserves 000, 666, and 900-999 in the first three digits as invalid, so they will
        be used if not specified otherwise to guarantee no real person has the generated SSN.

        :param start: The first part of the SSN. Will be clamped to between 0 and 999. If None, will be randomly decided
        from reserved ranges to ensure real-life invalidity. If not reserved, a warning will be issued to indicate a potentially real SSN.
        :param mid: The second part of the SSN. Will be clamped to between 0 and 99. If None, will be randomly decided.
        :param end: The third part of the SSN. Will be clamped to between 0 and 9999. If None, will be randomly decided.
    """
    def is_reserved_start(s: int) -> bool:
        """
            Check if a given SSN start is reserved/invalid.
        """
        return s == 0 or s == 666 or (900 <= s <= 999)

    def get_reserved_start(i: int) -> int:
        """
            Given an index for a reserved SSN start, return the corresponding reserved value.
        """
        i = clamp(i, 0, RESERVED_SSN_START_COUNT - 1)
        if i == 0:
            return 0
        elif i == 1:
            return 666
        else:
            return 900 + (i - 2)

    def get_random_reserved_start() -> int:
        """
            Get a random reserved SSN start value.
        """
        return get_reserved_start(random.randint(0, RESERVED_SSN_START_COUNT - 1))

    def get_random_mid() -> int:
        """
            Get a random SSN mid value.
        """
        return random.randint(SSN_MID_MIN, SSN_MID_MAX)

    def get_random_end() -> int:
        """
            Get a random SSN end value.
        """
        return random.randint(SSN_END_MIN, SSN_END_MAX)

    if start is None:
        start = get_random_reserved_start()
    else:
        start = clamp(randint_from_input(start, get_random_reserved_start, log=log), SSN_START_MIN, SSN_START_MAX, log=log)
        if not is_reserved_start(start):
            warn(f"The specified SSN start ({start}) means the generated SSN may correspond to a real person.")
    start_str = str(start).zfill(3)

    mid, mid_str = format_component(mid, SSN_MID_MIN, SSN_MID_MAX, 2, get_random_mid, log)
    end, end_str = format_component(end, SSN_END_MIN, SSN_END_MAX, 4, get_random_end, log)

    return f"{start_str}-{mid_str}-{end_str}"

def gen_phone(area: int | str | None = None, central: int | str | None = None, line: int | str | None = None, log: bool = False) -> str:
    """
        Generate a random US phone number.
        The range "XXX-555-0100" to "XXX-555-0199" is reserved for fictional use, so if the central office code
        is not specified, it will be set to 555 to guarantee no real person has the generated phone number. Similarly,
        if the line number is not specified, it will be set to a value between 100 and 199 to stay within the reserved range.

        :param area: The area code (first three digits). Will be clamped to between 200 and 999. If None, will be randomly decided.
        :param central: The central office code (second three digits). Will be clamped to between 200 and 999. If None, will be randomly decided.
        If not reserved, a warning will be issued to indicate a potentially real phone number.
        :param line: The line number (last four digits). Will be clamped to between 0 and 9999. If None, will be randomly decided.
        If this is not reserved while the central number is, a warning will be issued to indicate a potentially real phone number.
    """
    def is_reserved_central(c: int) -> bool:
        """
            Check if a given central office code is reserved/invalid.
        """
        return c == RESERVED_CENTRAL

    def get_random_reserved_central() -> int:
        """
            Get a random reserved central office code.
        """
        return RESERVED_CENTRAL

    def get_random_central() -> int:
        """
            Get a random central office code.
        """
        return random.randint(CENTRAL_MIN, CENTRAL_MAX)

    def is_reserved_line(l: int) -> bool:
        """
            Check if a given line number is reserved/invalid.
        """
        return RESERVED_LINE_MIN <= l <= RESERVED_LINE_MAX

    def get_random_reserved_line() -> int:
        """
            Get a random reserved line number.
        """
        return random.randint(RESERVED_LINE_MIN, RESERVED_LINE_MAX)

    def get_random_line() -> int:
        """
            Get a random line number.
        """
        return random.randint(LINE_MIN, LINE_MAX)

    def get_random_area() -> int:
        """
            Get a random area code.
        """
        return random.randint(AREA_CODE_MIN, AREA_CODE_MAX)

    area, area_str = format_component(area, AREA_CODE_MIN, AREA_CODE_MAX, 3, get_random_area, log)

    if central is None:
        central = get_random_reserved_central()
    else:
        central = clamp(randint_from_input(central, get_random_reserved_central, log=log), CENTRAL_MIN, CENTRAL_MAX, log=log)
        if not is_reserved_central(central):
            warn(f"The specified central office code ({central}) means the generated phone number may correspond to a real person.")
    central_str = str(central).zfill(3)

    if line is None:
        if is_reserved_central(central):
            line = get_random_reserved_line()
        else:
            # Since the number is already potentially real, use the full range of possible line numbers.
            line = get_random_line()
    else:
        line = clamp(randint_from_input(line, get_random_reserved_line, log=log), LINE_MIN, LINE_MAX, log=log)
        # Don't send the warning if the central number is already non-reserved, as that makes this warning misleading.
        if is_reserved_central(central) and not is_reserved_line(line):
            warn(f"The specified line number ({line}) means the generated phone number may correspond to a real person.")
    line_str = str(line).zfill(4)

    return f"({area_str}) {central_str}-{line_str}"

class AddressArgs(TypedDict):
    building_number: NotRequired[str | None]
    street: NotRequired[str | None]
    city: NotRequired[str | None]
    state: NotRequired[str | None]
    zip: NotRequired[str | None]

def gen_address(data: AddressArgs={}, state_abbr: bool = True, existing_city: bool = True, log: bool = False) -> str:
    """
        Generate a random US address using the Faker library.
        These components can be optionally specified in the input dictionary:
        - building_number
        - street
        - city
        - state
        - zip

        If a city and/or state is missing, but a zip is provided, the missing component(s) will be
        derived from the zip code. If a city and/or state is provided, but the zip is missing,
        the zip will be looked up based on the city and state. If multiple zip codes match the provided city/state,
        one will be chosen at random. If there are any errors with these lookups, fallback is a randomly generated value.

        :param data: A dictionary with optional keys: 'street', 'city', 'state', 'zip'.
        :param existing_city: Whether to use existing city names in a resolved state, or generate completely random city names.
        :return: A formatted address string.
    """
    fake = faker.Faker('en_US')

    city = data.get('city')
    state = location_utils.normalize_state_name(data.get('state'), state_abbr)
    if state is None and data.get('state') is not None:
        warn(f"State name {data.get('state')} could not be normalized; it may not correspond to a valid US state abbreviation or name.")
    zip = data.get('zip')

    def random_state():
        states = location_utils.get_all_us_states()
        return random.choice(states)['abbr']
    
    def random_city() -> str:
        return fake.city()
    
    def random_city_existing(state: str) -> str:
        cities = location_utils.get_cities_by_state(state)
        return random.choice(cities)
    
    def is_valid_zip(zip_code: str) -> bool:
        return zip_code.isdigit() and (ZIPCODE_MIN <= int(zip_code) <= ZIPCODE_MAX)
    
    def random_zip():
        return str(random.randint(ZIPCODE_MIN, ZIPCODE_MAX)).zfill(5)

    if zip is not None:
        if not is_valid_zip(zip):
            if log: print(f"Provided zip code '{zip}' is not valid. Generating a random zip code.")
            zip = random_zip()
            if log: print(f"Using zip code '{zip}'.")

        correct_city_state = location_utils.get_city_state_by_zipcode(zip)
        correct_city_state_found = correct_city_state is not None

        if not correct_city_state_found:
            if log: print(f"Could not find city/state for provided zip code '{zip}'. Generating random values.")

            if city and not state:
                try:
                    state_options = location_utils.find_states_with_city(city)
                    if len(state_options) == 0:
                        state = random_state()
                        if log: print(f"No states found with city '{city}'. Randomly selected state '{state}'.")
                    else:
                        state = random.choice(state_options)
                        if log: print(f"Found states {state_options} with city '{city}'. Randomly selected state '{state}'.")
                except:
                    state = random_state()
                    if log: print(f"Error looking up states for city '{city}'. Randomly selected state '{state}'.")
            
            state = state or random_state()
            city = city or (random_city_existing(state) if existing_city else random_city())
            if log: print(f"Using city '{city}' and state '{state}' for zip code '{zip}'.")
        else:
            correct_city, correct_state = correct_city_state
            city_matches = (city is None) or (city.lower() == correct_city.lower())
            state_matches = (state is None) or (state.lower() == correct_state.lower())
            
            # Do not override the user's choice to have these mismatches; just warn them.
            if not city_matches:
                print(f"Provided city '{city}' does not match city '{correct_city}' for zip code '{zip}'. Using provided city.")

            if not state_matches:
                print(f"Provided state '{state}' does not match state '{correct_state}' for zip code '{zip}'. Using provided state.")

            if city is None: city = correct_city
            if state is None: state = correct_state
    else:
        if state is None:
            if city is not None:
                try:
                    state_options = location_utils.find_states_with_city(city)
                    if len(state_options) == 0:
                        state = random_state()
                        if log: print(f"No states found with city '{city}'. Randomly selected state '{state}'.")
                    else:
                        state = random.choice(state_options)
                        if log: print(f"Found states {state_options} with city '{city}'. Randomly selected state '{state}'.")
                except:
                    state = random_state()
                    if log: print(f"Error looking up states for city '{city}'. Randomly selected state '{state}'.")
            else:
                state = random_state()
                if log:
                    print(f"No state provided; randomly selected state '{state}'.")

        if city is None:
            city = random_city_existing(state) if existing_city else random_city()
            if log:
                print(f"No city provided; randomly selected city '{city}' for state '{state}'.")

        try:
            zips = location_utils.get_zipcodes_by_city(city, state)
            if len(zips) == 0:
                if log: print(f"No zip codes found for city '{city}', state '{state}'. Generating a random zip code.")
                zip = random_zip()
                if log: print(f"Using zip code '{zip}' for city '{city}', state '{state}'.")
            else:
                if log: print(f"Found {len(zips)} zip code(s) for city '{city}', state '{state}'. Selecting one at random.")
                zip = random.choice(zips)
                if log: print(f"Selected zip code '{zip}' for city '{city}', state '{state}'.")
        except:
            if log: print(f"Error looking up zip codes for city '{city}', state '{state}'. Generating a random zip code.")
            zip = random_zip()
            if log: print(f"Using zip code '{zip}' for city '{city}', state '{state}'.")
    
    building_number = data.get('building_number')
    street = data.get('street')

    if building_number and street:
        warn(f"The specified street address ('{building_number} {street}') may correspond to a real location.")

    building_number = building_number or fake.building_number()
    street = street or fake.street_name()

    address = f"{building_number} {street}, {city} {state}, {zip}"
    return address

class TypoArgs(TypedDict):
    text: str
    typos: list[str]
    typo_weights: list[int]
    typo_rate: float
    typos_per_word: int

def gen_typos(text: str, typo_distrb: list[tuple[int, str]], rate: float=0.1, typos_per_word: int=1, log: bool = False) -> str:
    words = process_words(text)
    if log: print(f"Got {len(words)} words from input text for typo generation.")
    result = words.copy()
    offset = 0  # Track how much result list has grown/shrunk
    
    for i in range(len(words)):
        # if we're at the end, refuse to do filler word typos unless it's the only option.
        def cannot_do_filler_ins() -> bool:
            return i + offset == len(result) - 1
        
        # if we're generating homophones and the word has no homophones, refuse to do that typo unless it's the only option.
        def cannot_do_homophone() -> bool:
            homophone_gen = TYPO_GENERATORS["homophone"]
            return isinstance(homophone_gen, TypoHomophoneGenerator) and not homophone_gen.has_any_homophones(result[i + offset])

        if random.random() < rate:
            num_typos = random.randint(1, typos_per_word)
            if log: print(f"Generating {num_typos} typos to word '{words[i]}' at original index {i}.")

            for _ in range(num_typos):
                typo_type = rand_pick_dstrb(typo_distrb)
                if log: print(f"Picked typo type '{typo_type}' for word '{result[i + offset]}' at current index {i + offset}.")

                attempts = 0
                while (
                    (typo_type == "filler-ins" and cannot_do_filler_ins())
                    or (typo_type == "homophone" and cannot_do_homophone())
                ) and len(typo_distrb) > 1 and attempts < 10:
                    typo_type = rand_pick_dstrb(typo_distrb)
                    attempts += 1
                    if log:
                        if typo_type == "filler-ins":
                            print(f"Refused to apply 'filler-ins' typo to last word. Picked new typo type '{typo_type}' instead.")
                        elif typo_type == "homophone":
                            print(f"Refused to apply 'homophone' typo to word '{result[i + offset]}' with no homophones. Picked new typo type '{typo_type}' instead.")

                if (typo_type == "filler-ins" and cannot_do_filler_ins()) or (typo_type == "homophone" and cannot_do_homophone()):
                    if log: print(f"Could not find a suitable typo type for word '{result[i + offset]}' after 10 attempts. Skipping typo generation for this word.")
                    continue

                typo_generator = TYPO_GENERATORS[typo_type]
                new_words = typo_generator.generate([result[i + offset]])
                if log: print(f"Generated new word(s) {new_words} from original word '{result[i + offset]}' using typo type '{typo_type}'.")
                
                # Calculate new offset based on word count change
                word_count_diff = len(new_words) - 1
                result = result[:i + offset] + new_words + result[i + offset + 1:]
                offset += word_count_diff
    
    return ' '.join(result)

class ColorArgs(TypedDict):
    min_r: NotRequired[int]
    max_r: NotRequired[int]
    exact_r: NotRequired[int | None]
    min_g: NotRequired[int]
    max_g: NotRequired[int]
    exact_g: NotRequired[int | None]
    min_b: NotRequired[int]
    max_b: NotRequired[int]
    exact_b: NotRequired[int | None]

def gen_color(
        args: ColorArgs = {},
        log: bool = False
    ) -> str:
    """
        Generate a random color, represent it in Hex, RGB, and HSL formats, name the color, and return a formatted string with all this information.

        :param min_r: Minimum red value (0-255)
        :param max_r: Maximum red value (0-255)
        :param exact_r: If specified, use this exact red value instead of generating a random one.
        :param min_g: Minimum green value (0-255)
        :param max_g: Maximum green value (0-255)
        :param exact_g: If specified, use this exact green value instead of generating a random one.
        :param min_b: Minimum blue value (0-255)
        :param max_b: Maximum blue value (0-255)
        :param exact_b: If specified, use this exact blue value instead of generating a random one.
    """
    min_r = clamp(args.get('min_r', 0), 0, 255, log)
    max_r = clamp(args.get('max_r', 255), 0, 255, log)
    min_g = clamp(args.get('min_g', 0), 0, 255, log)
    max_g = clamp(args.get('max_g', 255), 0, 255, log)
    min_b = clamp(args.get('min_b', 0), 0, 255, log)
    max_b = clamp(args.get('max_b', 255), 0, 255, log)

    exact_r = args.get('exact_r')
    exact_g = args.get('exact_g')
    exact_b = args.get('exact_b')

    rgb: RGB = {
        'r': clamp(exact_r if exact_r is not None else random.randint(min_r, max_r), 0, 255, log),
        'g': clamp(exact_g if exact_g is not None else random.randint(min_g, max_g), 0, 255, log),
        'b': clamp(exact_b if exact_b is not None else random.randint(min_b, max_b), 0, 255, log)
    }

    hex: str = rgb_to_hex(rgb)
    hsl: HSL = rgb_to_hsl(rgb)
    name: str = nearest_color(rgb)

    return f"{name} - rgb({rgb['r']}, {rgb['g']}, {rgb['b']}), hex: {hex}, hsl({hsl['h']:.2f}, {hsl['s']:.2f}%, {hsl['l']:.2f}%)"

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

    def text_regex_type(s: str) -> str:
        re_groups = '|'.join([re.escape(c) for c in all_characters])
        if not re.fullmatch(fr'([{re_groups}]+)', s):
            raise argparse.ArgumentTypeError(f"Text must only contain the following characters or a space: {all_characters.strip()}")
        return s

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

    def typo_weights_type(s: str) -> int:
        try:
            value = int(s)
            if value < 0:
                raise argparse.ArgumentTypeError("Typo weights must be non-negative integers.")
            return value
        except ValueError:
            raise argparse.ArgumentTypeError("Typo weights must be non-negative integers.")

    parser.add_argument(
        '--typo-weights', '-tw',
        nargs="+",
        type=typo_weights_type,
        help="Weights for each typo types. If not specified, all types will have equal weight."
    )
    parser.add_argument('--typo-rate', '-tr', type=float, default=0.1, help="Probability of applying a typo to each word (default: 0.1)")
    parser.add_argument('--typos-per-word', '-tpw', type=int, default=1, help="Maximum number of typos to apply per word (default: 1)")
    
    # Specific arguments for color generation
    def rgb_bound_type(s: str) -> int:
        try:
            value = int(s)
            if not (0 <= value <= 255):
                raise argparse.ArgumentTypeError("RGB bounds must be integers between 0 and 255.")
            return value
        except ValueError:
            raise argparse.ArgumentTypeError("RGB bounds must be integers between 0 and 255.")
        
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