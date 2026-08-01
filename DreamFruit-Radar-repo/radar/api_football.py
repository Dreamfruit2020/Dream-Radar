"""
Shared client for API-Football (https://www.api-football.com) — the
approved real source for fixtures, match load and player roster/bio
(Connor's decision, 1 Aug 2026 — see docs/radar-guardrails-review.md).

One account covers three of the four remaining mock data sources: this
module is the single place that holds the API key, base URL, and
request/error handling; `fixtures.py`, `load.py` and `player_bio.py` each
import from here rather than duplicating HTTP logic three times.

IMPORTANT — NOT LIVE-TESTED, same caveat as radar/climate.py. This
sandbox cannot reach any external API (confirmed via a blocked curl and
a timed-out fetch during development), so nothing in this module or its
callers has ever made a real call to api-football.com. Everything is
written against the API's publicly documented response shape and
verified with mocked HTTP responses (scripts/verify_api_football.py) —
real, but unproven until someone with a live key and real internet runs
it for the first time.

Setup, once you have a key:
    export API_FOOTBALL_KEY="your-key-here"

Two things still need confirming with a live key before this is fully
trusted — both flagged loudly rather than guessed at:
  1. Crystal Palace's numeric team_id in API-Football's system. A widely
     reused example ID (52) shows up across public API-Football sample
     code, but that's third-party convention, not something this project
     has verified against the real API — confirm via
     GET /teams?name=Crystal Palace once the key is live, and set
     CRYSTAL_PALACE_TEAM_ID below explicitly rather than trusting a
     borrowed number.
  2. Venue latitude/longitude — API-Football's fixture data gives a venue
     *name* and city, not coordinates. travel.py needs coordinates. See
     the VENUE_COORDINATES gap noted in fixtures.py.

Fails toward "no data," never toward invented data: any request that
fails, times out, or comes back without a key returns None (or an empty
list, per function), never a fabricated fixture/player/reading.
"""

from __future__ import annotations

import os
from typing import Any

import requests

BASE_URL = "https://v3.football.api-sports.io"
REQUEST_TIMEOUT_SECONDS = 10

# NOT VERIFIED — see module docstring point 1. Confirm before relying on it.
CRYSTAL_PALACE_TEAM_ID = 52


def api_key() -> str | None:
    return os.environ.get("API_FOOTBALL_KEY")


def is_configured() -> bool:
    return bool(api_key())


def get(endpoint: str, params: dict[str, Any]) -> list[dict] | None:
    """
    GET against api-football.com. Returns the `response` array from the
    API-Football envelope on success, or None on any failure — missing
    key, network error, timeout, non-200, or an unexpected payload shape.

    API-Football wraps every response as:
        {"get": ..., "parameters": ..., "errors": [...], "results": N, "response": [...]}
    `errors` can be a non-empty list even on HTTP 200 (e.g. rate limit,
    invalid parameter) — checked explicitly rather than trusting status
    code alone.
    """
    key = api_key()
    if not key:
        return None
    try:
        r = requests.get(
            f"{BASE_URL}/{endpoint.lstrip('/')}",
            headers={"x-apisports-key": key},
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        payload = r.json()
        errors = payload.get("errors")
        if errors:
            return None
        return payload.get("response")
    except Exception:
        return None
