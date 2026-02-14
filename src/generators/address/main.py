from warnings import warn
import random
import faker
import utils.location as location_utils
from .pytypes import AddressArgs

ZIPCODE_MIN = 0
ZIPCODE_MAX = 99999

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