"""
Climate delta per fixture — spec section 6.

Real integration: Open-Meteo (https://open-meteo.com), a free, keyless
weather API. Forecast endpoint for fixtures inside the reliable horizon
(config.FORECAST_RELIABLE_HORIZON_DAYS); beyond that, a historical
average — the mean of the same calendar date across the past
HISTORICAL_YEARS_SAMPLED years, via Open-Meteo's archive endpoint — per
the spec's own caveat ("forecast accuracy degrades beyond ~10 days out;
use historical averages further ahead").

IMPORTANT — NOT LIVE-TESTED. This module was written and unit-tested
against Open-Meteo's documented API contract using mocked HTTP responses
(scripts/verify_climate.py), because this sandbox's outbound network is
allowlisted and does not include api.open-meteo.com or
archive-api.open-meteo.com — confirmed by both a direct curl (403,
blocked-by-allowlist) and mcp workspace web_fetch (timed out) during
development. Confirm a real call actually succeeds from wherever this
runs in practice before trusting it in front of a club.

Fails toward "no signal," never toward invented data: if the API is
unreachable, times out, or returns something unexpected,
get_climate_reading() returns a reading with delta held at 0 and a
source field that says so explicitly — never a silently fabricated
number standing in for a real one.
"""

from __future__ import annotations

from datetime import date

import requests

from .config import FORECAST_RELIABLE_HORIZON_DAYS
from .models import ClimateReading, Fixture, Venue

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HISTORICAL_YEARS_SAMPLED = 5
REQUEST_TIMEOUT_SECONDS = 8

UNAVAILABLE_SOURCE = (
    "Open-Meteo API unreachable or returned unexpected data — treated as no climate "
    "signal for this fixture (delta held at 0), not a real reading."
)


def _unavailable(fixture: Fixture) -> ClimateReading:
    return ClimateReading(
        fixture=fixture,
        temp_delta_c=0.0,
        humidity_delta_pct=0.0,
        precipitation_risk="unknown",
        is_forecast=False,
        source=UNAVAILABLE_SOURCE,
    )


def _historical_average(venue: Venue, on: date, years: int = HISTORICAL_YEARS_SAMPLED) -> dict | None:
    """Mean of the same calendar date across the past `years` years. This
    IS the spec's 'historical average' fallback beyond the forecast
    horizon (section 6), not a placeholder for one."""
    temps, humidities, precips = [], [], []
    for y in range(1, years + 1):
        try:
            sample_date = on.replace(year=on.year - y)
        except ValueError:
            # 29 Feb with no matching day in that sample year — skip it
            # rather than guess a nearby date.
            continue
        try:
            r = requests.get(
                ARCHIVE_URL,
                params={
                    "latitude": venue.latitude,
                    "longitude": venue.longitude,
                    "start_date": sample_date.isoformat(),
                    "end_date": sample_date.isoformat(),
                    "daily": "temperature_2m_mean,relative_humidity_2m_mean,precipitation_sum",
                    "timezone": "auto",
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            r.raise_for_status()
            daily = r.json()["daily"]
            temps.append(daily["temperature_2m_mean"][0])
            humidities.append(daily["relative_humidity_2m_mean"][0])
            precips.append(daily["precipitation_sum"][0])
        except Exception:
            continue
    if not temps:
        return None
    return {
        "temp": sum(temps) / len(temps),
        "humidity": sum(humidities) / len(humidities),
        "precip_mm": sum(precips) / len(precips),
    }


def _forecast(venue: Venue, on: date) -> dict | None:
    try:
        r = requests.get(
            FORECAST_URL,
            params={
                "latitude": venue.latitude,
                "longitude": venue.longitude,
                "start_date": on.isoformat(),
                "end_date": on.isoformat(),
                "daily": "temperature_2m_mean,relative_humidity_2m_mean,precipitation_probability_max",
                "timezone": "auto",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        daily = r.json()["daily"]
        return {
            "temp": daily["temperature_2m_mean"][0],
            "humidity": daily["relative_humidity_2m_mean"][0],
            "precip_pct": daily["precipitation_probability_max"][0],
        }
    except Exception:
        return None


def _precip_risk_from_pct(pct: float) -> str:
    if pct >= 60:
        return "high"
    if pct >= 25:
        return "moderate"
    return "low"


def _precip_risk_from_mm(mm: float) -> str:
    if mm >= 4:
        return "high"
    if mm >= 1:
        return "moderate"
    return "low"


def get_climate_reading(fixture: Fixture, home_venue: Venue, as_of: date | None = None) -> ClimateReading:
    """Real integration. See module docstring for the not-live-tested
    caveat. `as_of` is injectable for deterministic testing (mirrors the
    pattern already used in international.squad_announceable)."""
    as_of = as_of or date.today()
    is_forecast = (fixture.kickoff - as_of).days <= FORECAST_RELIABLE_HORIZON_DAYS

    home = _historical_average(home_venue, fixture.kickoff)
    if home is None:
        return _unavailable(fixture)

    if is_forecast:
        away = _forecast(fixture.venue, fixture.kickoff)
        source = "Open-Meteo forecast API"
        if away is None:
            # Forecast call failed — fall back to historical average
            # rather than giving up on this fixture entirely.
            away = _historical_average(fixture.venue, fixture.kickoff)
            is_forecast = False
            source = "Open-Meteo archive API (forecast unavailable, used historical average)"
    else:
        away = _historical_average(fixture.venue, fixture.kickoff)
        source = f"Open-Meteo archive API — mean of same calendar date, past {HISTORICAL_YEARS_SAMPLED} years"

    if away is None:
        return _unavailable(fixture)

    precip_risk = (
        _precip_risk_from_pct(away["precip_pct"])
        if "precip_pct" in away
        else _precip_risk_from_mm(away["precip_mm"])
    )

    return ClimateReading(
        fixture=fixture,
        temp_delta_c=round(away["temp"] - home["temp"], 1),
        humidity_delta_pct=round(away["humidity"] - home["humidity"], 1),
        precipitation_risk=precip_risk,
        is_forecast=is_forecast,
        source=source,
    )
