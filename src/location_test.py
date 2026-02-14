from utils.location import *

if __name__ == "__main__":
    states = get_all_us_states()
    print(f"Loaded {len(states)} states/territories.")
    print(f"Sample: {states[:3]} ... {states[-3:]}")

    print("\n--- States with Springfield ---")
    states_with_springfield = find_states_with_city("Springfield")
    print(f"States with Springfield: {states_with_springfield}")
    
    # Select a random state to demonstrate city retrieval
    target_state = random.choice(states)['abbr']
    print(f"\n--- Cities in randomly selected state/territory ({normalize_state_name(target_state)}) ---")
    cities = get_cities_by_state(target_state)

    print(f"Total Cities Found: {len(cities)}")
    print(f"Sample: {cities[:5]} ... {cities[-5:]}")

    print(f"\n--- Zip codes in {normalize_state_name(target_state)} ---")
    zips_in_state = get_zipcodes_by_state(target_state)
    print(f"Total Zip Codes Found: {len(zips_in_state)}")
    print(f"Sample: {zips_in_state[:5]} ... {zips_in_state[-5:]}")

    # Select a random city from the list to demonstrate zip code retrieval
    target_city = random.choice(cities)
    if target_city in cities:
        zips = get_zipcodes_by_city(target_city, target_state)
        print(f"\nZip codes for randomly selected city ({target_city}, {normalize_state_name(target_state, True)}): {zips}")

        # Demonstrate city/state retrieval by zip code
        print(f"\n--- Confirming city/state by zip code ---")

        success_count = 0
        for zc in zips:
            city_state = get_city_state_by_zipcode(zc)
            if not city_state:
                print(f"Zip code {zc} not found to match any city/state.")
            else:
                city, state = city_state
                if state != normalize_state_name(target_state) or city != target_city:
                    print(f"Mismatch for zip {zc}: expected ({target_city}, {normalize_state_name(target_state)}), got ({city}, {state})")
                else:
                    success_count += 1

        print(f"Successfully matched {success_count}/{len(zips)} zip codes back to ({target_city}, {target_state}).")