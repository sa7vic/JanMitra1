import math
from typing import Optional, Tuple


EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute distance between two WGS84 coordinates in kilometers."""
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


def parse_bbox(bbox_value: Optional[str]) -> Optional[Tuple[float, float, float, float]]:
    """Parse bbox string in format minLon,minLat,maxLon,maxLat."""
    if not bbox_value:
        return None

    raw = [part.strip() for part in bbox_value.split(',')]
    if len(raw) != 4:
        return None

    try:
        min_lon, min_lat, max_lon, max_lat = [float(part) for part in raw]
    except ValueError:
        return None

    if min_lon >= max_lon or min_lat >= max_lat:
        return None

    if min_lat < -90 or max_lat > 90 or min_lon < -180 or max_lon > 180:
        return None

    return min_lon, min_lat, max_lon, max_lat
