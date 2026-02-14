import us
from uszipcode import SearchEngine
import random

# Initialize the SearchEngine once (loading the DB takes a moment)
# simple_zipcode=True is faster and sufficient for just names/numbers
engine = SearchEngine(simple_or_comprehensive=SearchEngine.SimpleOrComprehensiveArgEnum.simple)

def get_all_us_states(include_territories: bool=True) -> list[dict[str, str]]:
    """
        Get a list of all US states (and optionally territories) with their names and abbreviations.
        :param include_territories: Whether to include US territories in the list.
        :return: A list of dictionaries with 'name' and 'abbr' keys.
    """
    state_list = us.states.STATES
    if include_territories:
        state_list += us.states.TERRITORIES

    return [{"name": state.name, "abbr": state.abbr} for state in state_list]

def normalize_state_name(name_or_abbr: str | None, get_abbr: bool=False) -> str | None:
    """
        Given a state name or abbreviation, return either one or the other.
        :param name_or_abbr: The state name or abbreviation.
        :param get_abbr: If True, return the abbreviation; otherwise, return the full name. By default, this is False.
        :return: The abbreviation or full state name, or None if not found.
    """
    if not name_or_abbr:
        return None
    state = us.states.lookup(name_or_abbr)

    if get_abbr:
        return state.abbr if state else None
    else:
        return state.name if state else None

def get_cities_by_state(name_or_abbr: str | None) -> list[str]:
    """
        Returns a sorted list of all major cities in a given state abbreviation.
        Example: get_cities_by_state('IN') -> ['Anderson', 'Bloomington', ...]

        :param name_or_abbr: The state name or abbreviation.
        :return: A sorted list of major city names in that state.
    """
    if not name_or_abbr:
        return []
    name_or_abbr = normalize_state_name(name_or_abbr, True)
    if not name_or_abbr:
        return []
    
    results = engine.by_state(name_or_abbr, returns=0)
    
    # Use a set to remove duplicates, as many zip codes map to the same city
    unique_cities = set()
    for zipcode_obj in results:
        if zipcode_obj.major_city:
            unique_cities.add(zipcode_obj.major_city)
            
    return sorted(list(unique_cities))

def get_zipcodes_by_city(city_name: str, state_name_or_abbr: str | None) -> list[str]:
    """
        Returns a list of valid zip codes for a specific city and state.

        :param city_name: The name of the city.
        :param state_name_or_abbr: The state name or abbreviation.
        :return: A list of zip code strings for that city.
    """
    if not state_name_or_abbr:
        return []
    state_abbr = normalize_state_name(state_name_or_abbr, True)
    if not state_abbr:
        return []
    
    results = engine.by_city_and_state(city_name, state_abbr, returns=0)
    return [res.zipcode for res in results]

def get_zipcodes_by_state(name_or_abbr: str | None) -> list[str]:
    """
        Returns a list of all zip codes in a given state abbreviation.

        :param name_or_abbr: The state name or abbreviation.
        :return: A list of zip code strings for that state.
    """
    if not name_or_abbr:
        return []
    name_or_abbr = normalize_state_name(name_or_abbr, True)
    if not name_or_abbr:
        return []

    results = engine.by_state(name_or_abbr, returns=0)
    return [res.zipcode for res in results]

def get_city_state_by_zipcode(zipcode: str) -> tuple[str, str] | None:
    """
        Given a zip code, return the corresponding city and state.

        :param zipcode: The zip code string.
        :return: The (city, state) tuple, or None if not found.
    """
    result = engine.by_zipcode(zipcode)

    if result is not None:
        # The city and state will be columns. We need to convert to str to avoid type issues.
        city = str(result.major_city)
        state = normalize_state_name(str(result.state))

        if not state:
            return None

        return (city, state)
        
    
    return None

def find_states_with_city(city_name: str) -> list[str]:
    """
    Returns a sorted list of State Abbreviations that contain
    a city with the given name.
    """
    results = engine.query(city=city_name, returns=0)
    
    # Use a set comprehension to extract unique state abbreviations
    found_states = {res.state for res in results}
    
    return sorted(list(found_states))