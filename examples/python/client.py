"""Minimal client for the Fotocasa API on RapidAPI.

Set RAPIDAPI_KEY in your environment (or in a .env file at the repo root).
"""

import os

import requests

HOST = "fotocasa3.p.rapidapi.com"


def _load_dotenv():
    """Read RAPIDAPI_KEY from a .env in the current folder or the repo root, if present."""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    for path in (".env", os.path.join(root, ".env")):
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                key, sep, value = line.strip().partition("=")
                if sep and value and not key.startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def get(path, **params):
    """GET an endpoint and return the `data` part of the response."""
    key = os.environ.get("RAPIDAPI_KEY")
    if not key:
        raise SystemExit("Set RAPIDAPI_KEY first (see .env.example).")
    response = requests.get(
        f"https://{HOST}{path}",
        params={k: v for k, v in params.items() if v is not None},
        headers={"x-rapidapi-host": HOST, "x-rapidapi-key": key},
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()
    if not body.get("success", True):
        raise RuntimeError(f"{path} failed: {body}")
    return body["data"]


def find_location(query):
    """Resolve a place name to the combinedLocations string and centre point searches need."""
    matches = get("/suggestions", query=query)
    if not matches:
        raise SystemExit(f"No Fotocasa location matches {query!r}")
    return matches[0]


def search_params(place):
    """The three location parameters /searchads requires, taken from a suggestion."""
    return {
        "combinedLocations": place["combinedLocationIds"],
        "latitude": place["coordinates"]["latitude"],
        "longitude": place["coordinates"]["longitude"],
    }


def neighbourhood(ad):
    """The most specific location name on a row (level8, then level7, then level5)."""
    loc = ad.get("location") or {}
    return loc.get("level8Name") or loc.get("level7Name") or loc.get("level5Name")


def price_per_m2(ad):
    price = (ad.get("transaction") or {}).get("price")
    surface = ad.get("surface")
    return round(price / surface) if price and surface else None


def feature_map(details):
    """/property-details lists features as one-key objects: [{"rooms": 3}, {"surface": 78}]."""
    merged = {}
    for item in details.get("features") or []:
        merged.update(item)
    return merged
