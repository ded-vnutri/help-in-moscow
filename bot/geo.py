"""Free nearby search on OpenStreetMap data through the Overpass API."""

import asyncio
import logging
import math
from urllib.parse import quote

import aiohttp

from .net import make_session

log = logging.getLogger(__name__)

OVERPASS_URLS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
ATTEMPTS = 1  # passes over the mirror list
TOTAL_TIMEOUT_S = 25  # then the bot sends a map search link instead
RADIUS_M = 1500
MAX_RESULTS = 5

FILTERS = {
    "pharmacy": ['nwr["amenity"="pharmacy"]'],
    "metro": ['nwr["railway"="station"]["station"="subway"]', 'nwr["railway"="station"]["subway"="yes"]'],
    "mobile": ['nwr["shop"="mobile_phone"]', 'nwr["shop"="telecommunication"]'],
    "atm": ['nwr["amenity"="atm"]', 'nwr["amenity"="bank"]["atm"="yes"]'],
    "hospital": ['nwr["amenity"~"^(hospital|clinic|doctors)$"]'],
}


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _name(tags: dict, lang: str) -> str | None:
    return (
        tags.get(f"name:{lang}")
        or (tags.get("name:en") if lang != "ru" else None)
        or tags.get("name")
        or tags.get("brand")
        or tags.get("operator")
    )


async def find_nearby(category: str, lat: float, lon: float, lang: str, proxy: str | None = None) -> list[dict]:
    return await asyncio.wait_for(_find_nearby(category, lat, lon, lang, proxy), TOTAL_TIMEOUT_S)


async def _find_nearby(category: str, lat: float, lon: float, lang: str, proxy: str | None = None) -> list[dict]:
    parts = "".join(f"{f}(around:{RADIUS_M},{lat},{lon});" for f in FILTERS[category])
    query = f"[out:json][timeout:20];({parts});out center 60;"
    headers = {"User-Agent": "HelpInMoscowBot/1.0 (student project)", "Accept": "application/json, */*"}

    data = None
    async with make_session(proxy, timeout=aiohttp.ClientTimeout(total=30), headers=headers) as session:
        for url in OVERPASS_URLS * ATTEMPTS:
            try:
                async with session.post(url, data={"data": query}) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        break
                    log.warning("Overpass %s answered %s", url, resp.status)
            except (aiohttp.ClientError, TimeoutError, ValueError) as e:
                log.warning("Overpass %s failed: %s", url, e)
    if data is None:
        raise RuntimeError("Overpass is unavailable")

    places = []
    seen = set()
    for el in data.get("elements", []):
        plat = el.get("lat") or el.get("center", {}).get("lat")
        plon = el.get("lon") or el.get("center", {}).get("lon")
        if plat is None or plon is None:
            continue
        tags = el.get("tags", {})
        name = _name(tags, lang) or ""
        dist = distance_m(lat, lon, plat, plon)
        key = (name.lower(), round(plat, 3), round(plon, 3)) if name else (el["type"], el["id"])
        if key in seen:
            continue
        seen.add(key)
        places.append({
            "name": name,
            "lat": plat,
            "lon": plon,
            "distance": dist,
            "hours": tags.get("opening_hours"),
        })

    places.sort(key=lambda p: p["distance"])
    return places[:MAX_RESULTS]


YANDEX_QUERIES = {
    "pharmacy": "аптека",
    "metro": "метро",
    "mobile": "салон связи",
    "atm": "банкомат",
    "hospital": "больница поликлиника",
}


def search_link(category: str, lat: float, lon: float) -> str:
    """Yandex Maps search around the user: works even when Overpass is down."""
    return f"https://yandex.ru/maps/?text={quote(YANDEX_QUERIES[category])}&ll={lon},{lat}&z=16"


def route_link(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> str:
    """Walking route in Yandex Maps (opens the app on a phone)."""
    return f"https://yandex.ru/maps/?rtext={from_lat},{from_lon}~{to_lat},{to_lon}&rtt=pd"
