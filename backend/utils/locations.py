import json
import os
from functools import lru_cache

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOCATIONS_FILE = os.path.join(BASE_DIR, 'data', 'locations.json')


@lru_cache(maxsize=1)
def get_location_data():
    with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_states():
    return sorted(get_location_data().keys())


def get_districts(state):
    data = get_location_data()
    districts = data.get(state, {})
    return sorted(districts.keys())


def get_cities(state, district):
    data = get_location_data()
    districts = data.get(state, {})
    return sorted(districts.get(district, []))


def is_valid_state(state):
    if not state:
        return False
    return state in get_location_data()


def is_valid_district(state, district):
    if not state or not district:
        return False
    return district in get_location_data().get(state, {})


def is_valid_city(state, district, city):
    if not state or not district or not city:
        return False
    return city in get_location_data().get(state, {}).get(district, [])
