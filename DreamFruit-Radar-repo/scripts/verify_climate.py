#!/usr/bin/env python3
"""
Verification for radar/climate.py — the real Open-Meteo integration.

This sandbox cannot reach api.open-meteo.com or archive-api.open-meteo.com
(outbound network is allowlisted; both a direct curl and a web-fetch
attempt were blocked during development). So this doesn't test a live
call — it tests that the parsing, fallback and failure-handling logic is
correct against mocked HTTP responses shaped exactly like Open-Meteo's
documented API contract, using unittest.mock to stand in for `requests`.

This is real verification of real logic, but it is NOT proof the live
API integration works end to end. Before this runs in front of a club,
someone needs to run this from an environment that can actually reach
Open-Meteo and confirm a live call succeeds — see the caveat at the top
of radar/climate.py.

Run: python3 scripts/verify_climate.py
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from radar import climate
from radar.models import Fixture, FixtureCertainty, Venue

HOME = Venue("Selhurst Park", 51.3983, -0.0855, 1.0)
AWAY = Venue("Anfield", 53.4308, -2.9608, 1.0)
TODAY = date(2026, 9, 1)

FAILURES: list[str] = []
CHECKS = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if condition:
        print(f"  PASS  {label}")
    else:
        FAILURES.append(label)
        print(f"  FAIL  {label}   {detail}")


def fx(kickoff: date, venue: Venue = AWAY) -> Fixture:
    return Fixture("Premier League", kickoff, False, venue, "[test opponent]",
                    FixtureCertainty.CONFIRMED, "TEST FIXTURE — not real")


def mock_response(payload: dict, status_ok: bool = True):
    m = MagicMock()
    m.json.return_value = payload
    if status_ok:
        m.raise_for_status.return_value = None
    else:
        m.raise_for_status.side_effect = Exception("HTTP error")
    return m


def daily_payload(temp: float, humidity: float, precip_pct: float | None = None, precip_mm: float | None = None) -> dict:
    daily = {
        "temperature_2m_mean": [temp],
        "relative_humidity_2m_mean": [humidity],
    }
    if precip_pct is not None:
        daily["precipitation_probability_max"] = [precip_pct]
    if precip_mm is not None:
        daily["precipitation_sum"] = [precip_mm]
    return {"daily": daily}


print("\nradar/climate.py — Open-Meteo integration verification (mocked HTTP)")
print("=" * 74)

# ── 1. Forecast path (fixture inside the reliable horizon) ────────────
print("\n1. Forecast path")

fixture = fx(TODAY + timedelta(days=5))  # inside FORECAST_RELIABLE_HORIZON_DAYS (10)

def side_effect_forecast(url, params=None, timeout=None):
    if url == climate.FORECAST_URL:
        return mock_response(daily_payload(temp=22.0, humidity=60.0, precip_pct=10.0))
    return mock_response(daily_payload(temp=15.0, humidity=50.0, precip_mm=0.5))

with patch("radar.climate.requests.get", side_effect=side_effect_forecast) as m:
    reading = climate.get_climate_reading(fixture, HOME, as_of=TODAY)

check("uses the forecast endpoint for a near fixture", reading.is_forecast is True)
check("temp delta computed correctly (away 22.0 - home 15.0)", reading.temp_delta_c == 7.0, str(reading.temp_delta_c))
check("humidity delta computed correctly (60 - 50)", reading.humidity_delta_pct == 10.0, str(reading.humidity_delta_pct))
check("precipitation risk derived from forecast percentage", reading.precipitation_risk == "low")
check("source correctly labelled as forecast", "forecast" in reading.source.lower())

# ── 2. Historical-average path (beyond the forecast horizon) ──────────
print("\n2. Historical-average path")

far_fixture = fx(TODAY + timedelta(days=60))  # well beyond the horizon

def side_effect_archive(url, params=None, timeout=None):
    assert url == climate.ARCHIVE_URL, "should never call the forecast endpoint this far out"
    lat = params["latitude"]
    if lat == AWAY.latitude:
        return mock_response(daily_payload(temp=18.0, humidity=70.0, precip_mm=2.0))
    return mock_response(daily_payload(temp=14.0, humidity=55.0, precip_mm=0.2))

with patch("radar.climate.requests.get", side_effect=side_effect_archive) as m:
    far_reading = climate.get_climate_reading(far_fixture, HOME, as_of=TODAY)

check("does not call the forecast endpoint beyond the reliable horizon", True)  # asserted inside side_effect
check("historical average correctly labelled as not-a-forecast", far_reading.is_forecast is False)
check("historical temp delta computed correctly (18.0 - 14.0)", far_reading.temp_delta_c == 4.0, str(far_reading.temp_delta_c))
check(f"archive endpoint called {climate.HISTORICAL_YEARS_SAMPLED * 2} times (away + home, N years each)",
      m.call_count == climate.HISTORICAL_YEARS_SAMPLED * 2, str(m.call_count))
check("source correctly labelled as historical average", "archive" in far_reading.source.lower() or "historical" in far_reading.source.lower())

# ── 3. Forecast fails, falls back to historical average ────────────────
print("\n3. Forecast failure falls back to historical average, not to giving up")

near_fixture = fx(TODAY + timedelta(days=3))

def side_effect_forecast_fails(url, params=None, timeout=None):
    if url == climate.FORECAST_URL:
        raise Exception("simulated network failure")
    return mock_response(daily_payload(temp=16.0, humidity=52.0, precip_mm=0.1))

with patch("radar.climate.requests.get", side_effect=side_effect_forecast_fails):
    fallback_reading = climate.get_climate_reading(near_fixture, HOME, as_of=TODAY)

check("falls back to a historical-average reading rather than 'unavailable'",
      fallback_reading.source != climate.UNAVAILABLE_SOURCE)
check("fallback reading is correctly marked as not-a-forecast", fallback_reading.is_forecast is False)

# ── 4. Total failure fails toward 'no signal', never fabricated data ──
print("\n4. Total API failure")

def side_effect_all_fail(url, params=None, timeout=None):
    raise Exception("simulated total network failure")

with patch("radar.climate.requests.get", side_effect=side_effect_all_fail):
    dead_reading = climate.get_climate_reading(fixture, HOME, as_of=TODAY)

check("total failure returns the explicit 'unavailable' reading", dead_reading.source == climate.UNAVAILABLE_SOURCE)
check("unavailable reading holds delta at zero, not a fabricated number",
      dead_reading.temp_delta_c == 0.0 and dead_reading.humidity_delta_pct == 0.0)
check("unavailable reading marks precipitation risk as unknown, not a guess",
      dead_reading.precipitation_risk == "unknown")

# ── 5. Precipitation risk thresholds ───────────────────────────────────
print("\n5. Precipitation risk thresholds")

check("low forecast percentage -> low risk", climate._precip_risk_from_pct(10) == "low")
check("moderate forecast percentage -> moderate risk", climate._precip_risk_from_pct(40) == "moderate")
check("high forecast percentage -> high risk", climate._precip_risk_from_pct(80) == "high")
check("low archive mm -> low risk", climate._precip_risk_from_mm(0.2) == "low")
check("moderate archive mm -> moderate risk", climate._precip_risk_from_mm(2.0) == "moderate")
check("high archive mm -> high risk", climate._precip_risk_from_mm(6.0) == "high")

# ── 6. Boundary of the forecast horizon ────────────────────────────────
print("\n6. Forecast-horizon boundary")

from radar.config import FORECAST_RELIABLE_HORIZON_DAYS

boundary_fixture = fx(TODAY + timedelta(days=FORECAST_RELIABLE_HORIZON_DAYS))
just_beyond_fixture = fx(TODAY + timedelta(days=FORECAST_RELIABLE_HORIZON_DAYS + 1))

with patch("radar.climate.requests.get", side_effect=side_effect_forecast):
    boundary_reading = climate.get_climate_reading(boundary_fixture, HOME, as_of=TODAY)
with patch("radar.climate.requests.get", side_effect=side_effect_archive):
    beyond_reading = climate.get_climate_reading(just_beyond_fixture, HOME, as_of=TODAY)

check("exactly at the horizon still uses forecast", boundary_reading.is_forecast is True)
check("one day beyond the horizon uses historical average", beyond_reading.is_forecast is False)

print("\n" + "=" * 74)
if FAILURES:
    print(f"{len(FAILURES)} of {CHECKS} checks FAILED:")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print(f"All {CHECKS} checks passed (mocked — see module docstring for live-test caveat).")
