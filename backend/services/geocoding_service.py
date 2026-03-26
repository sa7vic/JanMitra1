import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests


@dataclass
class CacheEntry:
    value: Dict[str, Any]
    expires_at: float


class GeocodingService:
    """OpenStreetMap geocoding with policy-safe defaults."""

    def __init__(self) -> None:
        self.nominatim_url = os.getenv(
            'NOMINATIM_URL',
            'https://nominatim.openstreetmap.org',
        )
        self.photon_url = os.getenv('PHOTON_URL', 'https://photon.komoot.io')
        self.enable_photon_fallback = (
            os.getenv('PHOTON_FALLBACK', 'true').lower() == 'true'
        )
        self.timeout_seconds = float(
            os.getenv('GEOCODING_TIMEOUT_SECONDS', '8')
        )
        self.ttl_seconds = int(
            os.getenv('GEOCODING_CACHE_TTL_SECONDS', '3600')
        )
        # Keep Nominatim usage polite: default 1 request/sec.
        self.min_request_interval_seconds = float(
            os.getenv('GEOCODING_MIN_INTERVAL_SECONDS', '1.0')
        )
        self.cache_max_entries = int(
            os.getenv('GEOCODING_CACHE_MAX_ENTRIES', '5000')
        )

        app_name = os.getenv('APP_NAME', 'JanMitra')
        contact = os.getenv(
            'GEOCODING_CONTACT_EMAIL',
            'opensource-demo@example.com',
        )
        self.user_agent = f"{app_name}/1.0 ({contact})"

        self._forward_cache: Dict[str, CacheEntry] = {}
        self._reverse_cache: Dict[str, CacheEntry] = {}
        self._last_call_ts = 0.0
        self._lock = threading.Lock()

        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
        })

    def geocode(self, query: str, limit: int = 5) -> Dict[str, Any]:
        normalized_query = (query or '').strip()
        if not normalized_query:
            return {'ok': False, 'error': 'query is required', 'results': []}

        cache_key = f"{normalized_query.lower()}::{limit}"
        cached = self._cache_get(self._forward_cache, cache_key)
        if cached is not None:
            return {'ok': True, 'provider': 'cache', 'results': cached}

        nominatim = self._nominatim_search(normalized_query, limit)
        if nominatim['ok'] and nominatim['results']:
            self._cache_set(
                self._forward_cache,
                cache_key,
                nominatim['results'],
            )
            return nominatim

        if self.enable_photon_fallback:
            photon = self._photon_search(normalized_query, limit)
            if photon['ok'] and photon['results']:
                self._cache_set(
                    self._forward_cache,
                    cache_key,
                    photon['results'],
                )
                return photon

        if nominatim['error']:
            return {'ok': False, 'error': nominatim['error'], 'results': []}
        return {
            'ok': False,
            'error': 'No geocoding results found',
            'results': [],
        }

    def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        if latitude is None or longitude is None:
            return {
                'ok': False,
                'error': 'latitude and longitude are required',
            }

        rounded_lat = round(float(latitude), 6)
        rounded_lon = round(float(longitude), 6)
        cache_key = f"{rounded_lat},{rounded_lon}"

        cached = self._cache_get(self._reverse_cache, cache_key)
        if cached is not None:
            return {'ok': True, 'provider': 'cache', 'result': cached}

        result = self._nominatim_reverse(rounded_lat, rounded_lon)
        if result['ok'] and result['result']:
            self._cache_set(self._reverse_cache, cache_key, result['result'])
        return result

    def _cache_get(
        self,
        cache_store: Dict[str, CacheEntry],
        key: str,
    ) -> Optional[Any]:
        now = time.time()
        with self._lock:
            entry = cache_store.get(key)
            if not entry:
                return None
            if entry.expires_at <= now:
                cache_store.pop(key, None)
                return None
            return entry.value

    def _cache_set(
        self,
        cache_store: Dict[str, CacheEntry],
        key: str,
        value: Any,
    ) -> None:
        with self._lock:
            if len(cache_store) >= self.cache_max_entries:
                # Remove oldest 10% to avoid unbounded growth.
                items = sorted(
                    cache_store.items(),
                    key=lambda kv: kv[1].expires_at,
                )
                remove_count = max(1, len(items) // 10)
                for old_key, _ in items[:remove_count]:
                    cache_store.pop(old_key, None)
            cache_store[key] = CacheEntry(
                value=value,
                expires_at=time.time() + self.ttl_seconds,
            )

    def _throttle(self) -> None:
        with self._lock:
            now = time.time()
            wait_seconds = self.min_request_interval_seconds - (
                now - self._last_call_ts
            )
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            self._last_call_ts = time.time()

    def _http_get(
        self,
        url: str,
        params: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            self._throttle()
            response = self._session.get(
                url,
                params=params,
                timeout=self.timeout_seconds,
            )
            if response.status_code == 429:
                return None, 'Geocoding provider rate limited request (429)'
            if response.status_code >= 400:
                return (
                    None,
                    f'Geocoding provider returned HTTP {response.status_code}',
                )
            return response.json(), None
        except requests.Timeout:
            return None, 'Geocoding provider timed out'
        except requests.RequestException as exc:
            return None, f'Geocoding request failed: {exc}'

    def _nominatim_search(self, query: str, limit: int) -> Dict[str, Any]:
        payload, error = self._http_get(
            f"{self.nominatim_url.rstrip('/')}/search",
            {
                'q': query,
                'format': 'jsonv2',
                'addressdetails': 1,
                'limit': max(1, min(int(limit), 20)),
            },
        )
        if error:
            return {
                'ok': False,
                'provider': 'nominatim',
                'error': error,
                'results': [],
            }

        results = []
        for item in payload or []:
            try:
                results.append({
                    'provider': 'nominatim',
                    'display_name': item.get('display_name'),
                    'latitude': float(item['lat']),
                    'longitude': float(item['lon']),
                    'importance': item.get('importance'),
                    'type': item.get('type'),
                    'address': item.get('address', {}),
                })
            except (KeyError, TypeError, ValueError):
                continue

        return {
            'ok': True,
            'provider': 'nominatim',
            'results': results,
            'error': None,
        }

    def _photon_search(self, query: str, limit: int) -> Dict[str, Any]:
        payload, error = self._http_get(
            f"{self.photon_url.rstrip('/')}/api",
            {
                'q': query,
                'limit': max(1, min(int(limit), 20)),
            },
        )
        if error:
            return {
                'ok': False,
                'provider': 'photon',
                'error': error,
                'results': [],
            }

        results = []
        for feature in (payload or {}).get('features', []):
            coordinates = (
                (feature.get('geometry') or {}).get('coordinates') or []
            )
            props = feature.get('properties', {})
            if len(coordinates) != 2:
                continue
            try:
                longitude = float(coordinates[0])
                latitude = float(coordinates[1])
            except (TypeError, ValueError):
                continue

            display_parts = [
                props.get('name'),
                props.get('city'),
                props.get('state'),
                props.get('country'),
            ]
            display_name = ', '.join([part for part in display_parts if part])

            results.append({
                'provider': 'photon',
                'display_name': display_name,
                'latitude': latitude,
                'longitude': longitude,
                'importance': props.get('importance'),
                'type': props.get('osm_value'),
                'address': {
                    'city': props.get('city'),
                    'state': props.get('state'),
                    'country': props.get('country'),
                    'postcode': props.get('postcode'),
                },
            })

        return {
            'ok': True,
            'provider': 'photon',
            'results': results,
            'error': None,
        }

    def _nominatim_reverse(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        payload, error = self._http_get(
            f"{self.nominatim_url.rstrip('/')}/reverse",
            {
                'lat': latitude,
                'lon': longitude,
                'format': 'jsonv2',
                'addressdetails': 1,
                'zoom': 18,
            },
        )
        if error:
            return {
                'ok': False,
                'provider': 'nominatim',
                'error': error,
                'result': None,
            }

        if not payload:
            return {
                'ok': False,
                'provider': 'nominatim',
                'error': 'No reverse geocoding result found',
                'result': None,
            }

        result = {
            'provider': 'nominatim',
            'display_name': payload.get('display_name'),
            'latitude': latitude,
            'longitude': longitude,
            'address': payload.get('address', {}),
            'osm_id': payload.get('osm_id'),
            'osm_type': payload.get('osm_type'),
        }
        return {
            'ok': True,
            'provider': 'nominatim',
            'error': None,
            'result': result,
        }
