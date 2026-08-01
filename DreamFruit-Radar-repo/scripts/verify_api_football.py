#!/usr/bin/env python3
"""
Verification for the API-Football integration (radar/api_football.py,
and the real_* functions in fixtures.py, player_bio.py, load.py).

Same situation as scripts/verify_climate.py: this sandbox cannot reach
api-football.com (confirmed during earlier development — see
radar/climate.py's module docstring for the network test that proved
it), so this tests parsing/mapping/fallback logic against mocked HTTP
responses shaped like API-Football's documented envelope, not a real
round trip. Someone with a live key and real internet needs to run the
real thing before this touches a club — see radar/api_football.py.

Run: python3 scripts/verify_api_football.py
"""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from radar import api_football, fixtures as fixtures_mod, load, player_bio
from radar.models import FixtureCertainty, PlayerBio

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


def envelope(response, errors=None):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = {"response": response, "errors": errors or []}
    return m


CP_ID = api_football.CRYSTAL_PALACE_TEAM_ID

print("\nAPI-Football integration — verification (mocked HTTP)")
print("=" * 70)

# ── 1. api_football.get() — the shared client ──────────────────────────
print("\n1. Shared client (radar/api_football.py)")

with patch.dict(os.environ, {}, clear=False):
    os.environ.pop("API_FOOTBALL_KEY", None)
    check("no key configured -> is_configured() is False", api_football.is_configured() is False)
    check("no key configured -> get() returns None without a request", api_football.get("fixtures", {}) is None)

with patch.dict(os.environ, {"API_FOOTBALL_KEY": "test-key"}):
    check("key set -> is_configured() is True", api_football.is_configured() is True)

    with patch("radar.api_football.requests.get", side_effect=Exception("network error")):
        check("request exception -> get() returns None, doesn't raise", api_football.get("fixtures", {}) is None)

    with patch("radar.api_football.requests.get", return_value=envelope([], errors=["rate limit exceeded"])):
        check("non-empty errors array (even on HTTP 200) -> get() returns None",
              api_football.get("fixtures", {}) is None)

    with patch("radar.api_football.requests.get", return_value=envelope([{"a": 1}])):
        check("clean response -> get() returns the response array", api_football.get("fixtures", {}) == [{"a": 1}])

# ── 2. fixtures.real_fixtures() ─────────────────────────────────────────
print("\n2. Real fixtures (radar/fixtures.py)")

RAW_FIXTURES = [
    {  # confirmed league fixture, away, known venue
        "fixture": {"id": 111, "date": "2026-11-21T15:00:00+00:00", "venue": {"name": "Anfield"}},
        "league": {"name": "Premier League", "round": "Regular Season - 12"},
        "teams": {"home": {"id": 66, "name": "Liverpool"}, "away": {"id": CP_ID, "name": "Crystal Palace"}},
    },
    {  # confirmed home fixture
        "fixture": {"id": 112, "date": "2026-11-29T20:00:00+00:00", "venue": {"name": "Selhurst Park"}},
        "league": {"name": "Premier League", "round": "Regular Season - 13"},
        "teams": {"home": {"id": CP_ID, "name": "Crystal Palace"}, "away": {"id": 40, "name": "West Ham"}},
    },
    {  # qualifying round -> should map to PROVISIONAL
        "fixture": {"id": 113, "date": "2026-12-02T19:45:00+00:00", "venue": {"name": "Villa Park"}},
        "league": {"name": "EFL Cup", "round": "Qualifying Round"},
        "teams": {"home": {"id": 42, "name": "Aston Villa"}, "away": {"id": CP_ID, "name": "Crystal Palace"}},
    },
    {  # venue not in VENUE_COORDINATES -> should be dropped, not guessed
        "fixture": {"id": 114, "date": "2026-12-06T15:00:00+00:00", "venue": {"name": "Some New Ground Nobody Mapped"}},
        "league": {"name": "Premier League", "round": "Regular Season - 14"},
        "teams": {"home": {"id": 99, "name": "Somewhere FC"}, "away": {"id": CP_ID, "name": "Crystal Palace"}},
    },
]

with patch.dict(os.environ, {"API_FOOTBALL_KEY": "test-key"}):
    with patch("radar.api_football.requests.get", return_value=envelope(RAW_FIXTURES)):
        result = fixtures_mod.real_fixtures(CP_ID, 2026, date(2026, 11, 1), date(2026, 12, 31))

check("known venue -> 3 of 4 raw fixtures kept (one dropped)", len(result) == 3, str(len(result)))
away_lfc = next(f for f in result if f.external_id == 111)
check("away/home correctly detected from team ids", away_lfc.is_home is False)
check("opponent correctly extracted", away_lfc.opponent == "Liverpool")
check("kickoff date correctly parsed", away_lfc.kickoff == date(2026, 11, 21))
check("venue correctly resolved via VENUE_COORDINATES", away_lfc.venue.name == "Anfield")

home_fixture = next(f for f in result if f.external_id == 112)
check("home fixture correctly detected", home_fixture.is_home is True)

qualifying = next(f for f in result if f.external_id == 113)
check("'Qualifying Round' maps to PROVISIONAL certainty", qualifying.certainty == FixtureCertainty.PROVISIONAL)
check("non-qualifying round maps to CONFIRMED certainty", away_lfc.certainty == FixtureCertainty.CONFIRMED)
check("fixture at an unmapped venue is dropped, not given a guessed location",
      all(f.external_id != 114 for f in result))

with patch.dict(os.environ, {}, clear=False):
    os.environ.pop("API_FOOTBALL_KEY", None)
    check("no key -> real_fixtures() returns None",
          fixtures_mod.real_fixtures(CP_ID, 2026, date(2026, 11, 1), date(2026, 12, 31)) is None)

# ── 3. player_bio.real_get_roster() ─────────────────────────────────────
print("\n3. Real roster (radar/player_bio.py)")

def player_entry(name, age, height, weight, position):
    return {
        "player": {"name": name, "age": age, "height": height, "weight": weight},
        "statistics": [{"games": {"position": position}}],
    }

PAGE_1 = [player_entry(f"Player {i}", 20 + i, "180 cm", "76 kg", "Midfielder") for i in range(20)]
PAGE_2 = [player_entry("Last Player", 30, "190 cm", "88 kg", "Goalkeeper")]

with patch.dict(os.environ, {"API_FOOTBALL_KEY": "test-key"}):
    call_count = {"n": 0}

    def paginated_side_effect(url, params=None, headers=None, timeout=None):
        call_count["n"] += 1
        page = params.get("page", 1)
        return envelope(PAGE_1 if page == 1 else (PAGE_2 if page == 2 else []))

    with patch("radar.api_football.requests.get", side_effect=paginated_side_effect):
        roster = player_bio.real_get_roster(CP_ID, 2026)

check("pagination stops once a short page comes back (2 pages, not 3)", call_count["n"] == 2, str(call_count["n"]))
check("all players across pages collected (20 + 1)", len(roster) == 21, str(len(roster)))
last = next(p for p in roster if p.name == "Last Player")
check("height string parsed to int correctly ('190 cm' -> 190)", last.height_cm == 190, str(last.height_cm))
check("weight string parsed to int correctly ('88 kg' -> 88)", last.weight_kg == 88, str(last.weight_kg))
check("position pulled from statistics.games.position", last.position == "Goalkeeper")

with patch.dict(os.environ, {"API_FOOTBALL_KEY": "test-key"}):
    with patch("radar.api_football.requests.get", return_value=envelope([])):
        check("empty response -> real_get_roster() returns None", player_bio.real_get_roster(CP_ID, 2026) is None)

# ── 4. load.real_get_recent_load() ──────────────────────────────────────
print("\n4. Real recent load (radar/load.py)")

roster = [
    PlayerBio("Player A", 24, 178, 74, "Winger", "TEST", date.today()),
    PlayerBio("Player B", 27, 185, 80, "Midfielder", "TEST", date.today()),
]

def lineup_response(minutes_a, minutes_b, other_team=False):
    team_id = 999 if other_team else CP_ID
    return envelope([
        {
            "team": {"id": team_id, "name": "Crystal Palace"},
            "players": [
                {"player": {"name": "Player A"}, "statistics": [{"games": {"minutes": minutes_a}}]},
                {"player": {"name": "Player B"}, "statistics": [{"games": {"minutes": minutes_b}}]},
                {"player": {"name": "Unrostered Player"}, "statistics": [{"games": {"minutes": 15}}]},
            ],
        }
    ])

with patch.dict(os.environ, {"API_FOOTBALL_KEY": "test-key"}):
    def two_fixture_side_effect(url, params=None, headers=None, timeout=None):
        fid = params.get("fixture")
        if fid == 201:
            return lineup_response(90, 60)
        if fid == 202:
            return lineup_response(90, 0)  # Player B didn't feature
        return envelope([])

    with patch("radar.api_football.requests.get", side_effect=two_fixture_side_effect):
        loads = load.real_get_recent_load(CP_ID, roster, [201, 202])

check("minutes summed correctly across fixtures (Player A: 90+90)",
      next(l for l in loads if l.player.name == "Player A").minutes_last_28_days == 180)
check("zero-minute appearance doesn't inflate matches_last_28_days (Player B: only 1 match)",
      next(l for l in loads if l.player.name == "Player B").minutes_last_28_days == 60)
check("player not in roster is skipped, not fabricated",
      all(l.player.name != "Unrostered Player" for l in loads))

with patch.dict(os.environ, {"API_FOOTBALL_KEY": "test-key"}):
    def one_fails_side_effect(url, params=None, headers=None, timeout=None):
        if params.get("fixture") == 201:
            raise Exception("simulated failure")
        return lineup_response(45, 45)

    with patch("radar.api_football.requests.get", side_effect=one_fails_side_effect):
        partial = load.real_get_recent_load(CP_ID, roster, [201, 202])

check("one fixture failing doesn't discard the other's data", partial is not None and len(partial) == 2)
check("partial-failure source string says how partial it is",
      "1/2" in partial[0].source, partial[0].source)

with patch.dict(os.environ, {"API_FOOTBALL_KEY": "test-key"}):
    with patch("radar.api_football.requests.get", side_effect=Exception("all fail")):
        check("every fixture failing -> returns None, not an empty fabricated list",
              load.real_get_recent_load(CP_ID, roster, [201, 202]) is None)

print("\n" + "=" * 70)
if FAILURES:
    print(f"{len(FAILURES)} of {CHECKS} checks FAILED:")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print(f"All {CHECKS} checks passed (mocked — see radar/api_football.py for the live-test caveat).")
