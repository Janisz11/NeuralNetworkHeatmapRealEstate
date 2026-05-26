from typing import TypedDict


class CityInfo(TypedDict):
    slug: str
    display_name: str
    centre_lat: float
    centre_lon: float
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


CITIES: dict[str, CityInfo] = {
    "warszawa": {
        "slug": "warszawa",
        "display_name": "Warszawa",
        "centre_lat": 52.2297,
        "centre_lon": 21.0122,
        "lat_min": 51.97,
        "lat_max": 52.37,
        "lon_min": 20.85,
        "lon_max": 21.27,
    },
    "krakow": {
        "slug": "krakow",
        "display_name": "Kraków",
        "centre_lat": 50.0647,
        "centre_lon": 19.9450,
        "lat_min": 49.97,
        "lat_max": 50.13,
        "lon_min": 19.79,
        "lon_max": 20.12,
    },
    "wroclaw": {
        "slug": "wroclaw",
        "display_name": "Wrocław",
        "centre_lat": 51.1079,
        "centre_lon": 17.0385,
        "lat_min": 51.02,
        "lat_max": 51.19,
        "lon_min": 16.87,
        "lon_max": 17.18,
    },
    "gdansk": {
        "slug": "gdansk",
        "display_name": "Gdańsk",
        "centre_lat": 54.3520,
        "centre_lon": 18.6466,
        "lat_min": 54.27,
        "lat_max": 54.45,
        "lon_min": 18.47,
        "lon_max": 18.85,
    },
    "poznan": {
        "slug": "poznan",
        "display_name": "Poznań",
        "centre_lat": 52.4064,
        "centre_lon": 16.9252,
        "lat_min": 52.32,
        "lat_max": 52.49,
        "lon_min": 16.78,
        "lon_max": 17.07,
    },
    "lodz": {
        "slug": "lodz",
        "display_name": "Łódź",
        "centre_lat": 51.7592,
        "centre_lon": 19.4560,
        "lat_min": 51.67,
        "lat_max": 51.85,
        "lon_min": 19.31,
        "lon_max": 19.61,
    },
}


def get_city(slug: str) -> CityInfo:
    if slug not in CITIES:
        raise ValueError(f"Unknown city: {slug!r}. Valid cities: {list(CITIES)}")
    return CITIES[slug]
