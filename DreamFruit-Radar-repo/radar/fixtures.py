"""
Fixture modelling + certainty tiering — spec section 6, "Handling fixture
uncertainty (cup progression)".

Real, working logic for tiering. The actual fixture *data* below for
Crystal Palace is illustrative scaffolding, not a live pull — see the
loud warning in `example_fixtures()`. Wiring a real fixture source
(official league calendar) is listed as a TODO; nothing here should be
read as an assertion about Crystal Palace's actual confirmed match
dates or opponents.

What IS a verified, real fact (checked at spec time, see
docs/dream-radar-spec.md section 6): Crystal Palace won the 2026 UEFA
Conference League final and qualify directly into the 2026/27 Europa
League league phase, alongside the Premier League, FA Cup and EFL Cup —
a genuinely congested, multi-competition season. That's *why* they're
the pilot; the specific dates below are placeholders standing in for
that real competition mix until a live fixture source is wired in.
"""

from __future__ import annotations

from datetime import date, timedelta

from . import api_football
from .config import CONGESTION_WINDOW_DAYS
from .models import Fixture, FixtureCertainty, Venue

# Real, fixed venue for the pilot club.
SELHURST_PARK = Venue(name="Selhurst Park", latitude=51.3983, longitude=-0.0855, timezone_offset_hours=1.0)

# Illustrative away venues — real stadiums, real coordinates, used only to
# exercise the travel/climate pipeline with plausible geography. Not tied
# to any asserted real fixture date.
_EXAMPLE_VENUES = {
    "Anfield": Venue("Anfield", 53.4308, -2.9608, 1.0),
    "Villa Park": Venue("Villa Park", 52.5092, -1.8848, 1.0),
    "Signal Iduna Park": Venue("Signal Iduna Park", 51.4926, 7.4517, 2.0),
    "Estadio da Luz": Venue("Estadio da Luz", 38.7527, -9.1846, 1.0),
}

# KNOWN GAP: API-Football's fixture data gives a venue *name* and city,
# not coordinates — travel.py needs coordinates. This is a partial,
# manually-maintained lookup of long-standing top-flight grounds to
# unblock the pilot; it will miss newer/smaller/rotating venues (a
# ground this doesn't recognise fails toward "no travel signal" for that
# fixture, per _real_venue() below, rather than a guessed location).
# Expand as real fixtures surface venues not yet in here.
VENUE_COORDINATES: dict[str, Venue] = {
    "Anfield": Venue("Anfield", 53.4308, -2.9608, 1.0),
    "Emirates Stadium": Venue("Emirates Stadium", 51.5549, -0.1084, 1.0),
    "Etihad Stadium": Venue("Etihad Stadium", 53.4831, -2.2004, 1.0),
    "Old Trafford": Venue("Old Trafford", 53.4631, -2.2913, 1.0),
    "Stamford Bridge": Venue("Stamford Bridge", 51.4817, -0.1910, 1.0),
    "Tottenham Hotspur Stadium": Venue("Tottenham Hotspur Stadium", 51.6043, -0.0664, 1.0),
    "Villa Park": Venue("Villa Park", 52.5092, -1.8848, 1.0),
    "London Stadium": Venue("London Stadium", 51.5387, -0.0166, 1.0),
    "St James' Park": Venue("St James' Park", 54.9756, -1.6217, 1.0),
    "Molineux Stadium": Venue("Molineux Stadium", 52.5903, -2.1300, 1.0),
    "Craven Cottage": Venue("Craven Cottage", 51.4749, -0.2216, 1.0),
    "Selhurst Park": SELHURST_PARK,
    "King Power Stadium": Venue("King Power Stadium", 52.6204, -1.1422, 1.0),
    "Vitality Stadium": Venue("Vitality Stadium", 50.7352, -1.8384, 1.0),
    "American Express Stadium": Venue("American Express Stadium", 50.8617, -0.0837, 1.0),
    "City Ground": Venue("City Ground", 52.9399, -1.1327, 1.0),
    "Elland Road": Venue("Elland Road", 53.7778, -1.5722, 1.0),
    "Portman Road": Venue("Portman Road", 52.0552, 1.1450, 1.0),
    "Estadio da Luz": Venue("Estadio da Luz", 38.7527, -9.1846, 1.0),
    "Signal Iduna Park": Venue("Signal Iduna Park", 51.4926, 7.4517, 2.0),
}


def _certainty_from_api_fixture(raw: dict) -> FixtureCertainty:
    """
    Best-effort mapping from an API-Football fixture entry to our
    certainty tiers (spec section 6). NOT LIVE-VERIFIED — API-Football
    only creates a fixture row once a match is actually scheduled with
    two named teams, which covers most of what the spec calls
    'confirmed.' The spec's 'provisional' tier (a cup round date that's
    reserved before qualification is known) describes a state
    API-Football's fixtures endpoint may not model at all — if a round
    hasn't been drawn yet, there may simply be no fixture row to return,
    rather than a fixture flagged as provisional. Treated conservatively:
    anything API-Football returns is CONFIRMED unless the round name
    itself signals otherwise (e.g. contains 'Qualifying' or 'Play-off').
    Revisit this mapping once real cup-competition data has actually been
    seen — this is a first pass, not a settled rule.
    """
    round_name = (raw.get("league", {}).get("round") or "").lower()
    if "qualif" in round_name or "play-off" in round_name or "playoff" in round_name:
        return FixtureCertainty.PROVISIONAL
    return FixtureCertainty.CONFIRMED


def _real_venue(raw: dict) -> Venue | None:
    name = (raw.get("fixture", {}).get("venue", {}) or {}).get("name")
    if not name:
        return None
    return VENUE_COORDINATES.get(name)


def real_fixtures(team_id: int, season: int, from_date: date, to_date: date) -> list[Fixture] | None:
    """
    Real integration — API-Football /fixtures. Returns None (not an empty
    list) if the API isn't configured or the call fails, so callers can
    tell "no fixtures in range" apart from "couldn't reach the source."

    Fixtures at a venue not in VENUE_COORDINATES are dropped rather than
    given a guessed location — see the module-level gap note above.
    """
    raw = api_football.get(
        "fixtures",
        {
            "team": team_id,
            "season": season,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        },
    )
    if raw is None:
        return None

    fixtures: list[Fixture] = []
    for entry in raw:
        venue = _real_venue(entry)
        if venue is None:
            continue  # known gap — see VENUE_COORDINATES note
        teams = entry.get("teams", {})
        is_home = (teams.get("home", {}) or {}).get("id") == team_id
        opponent_team = teams.get("away") if is_home else teams.get("home")
        kickoff_raw = entry.get("fixture", {}).get("date", "")
        try:
            kickoff = date.fromisoformat(kickoff_raw[:10])
        except ValueError:
            continue
        fixtures.append(
            Fixture(
                competition=entry.get("league", {}).get("name", "Unknown competition"),
                kickoff=kickoff,
                is_home=is_home,
                venue=venue,
                opponent=(opponent_team or {}).get("name", "[unknown opponent]"),
                certainty=_certainty_from_api_fixture(entry),
                source=f"API-Football fixtures endpoint, pulled {date.today().isoformat()}",
                external_id=entry.get("fixture", {}).get("id"),
            )
        )
    return fixtures


def example_fixtures(season_start: date | None = None) -> list[Fixture]:
    """
    ILLUSTRATIVE ONLY. Stands in for a real fixture-list pull so the rest
    of the pipeline (travel, climate, congestion tiering) can be exercised
    end to end. Replace with a real official-calendar integration before
    this touches a real club visit — do not present this list to a
    nutritionist as-is.

    Deliberately includes one of each certainty tier so
    fuelling_risk.py (once designed) has something real to discriminate
    between.
    """
    start = season_start or date.today()

    return [
        Fixture(
            competition="Premier League",
            kickoff=start + timedelta(days=2),
            is_home=False,
            venue=_EXAMPLE_VENUES["Anfield"],
            opponent="[example opponent — Premier League]",
            certainty=FixtureCertainty.CONFIRMED,
            source="Illustrative placeholder — replace with official Premier League fixture list",
        ),
        Fixture(
            competition="UEFA Europa League",
            kickoff=start + timedelta(days=6),
            is_home=True,
            venue=SELHURST_PARK,
            opponent="[example opponent — Europa League league phase]",
            certainty=FixtureCertainty.CONFIRMED,  # league phase opponents/dates are set in advance
            source="Illustrative placeholder — replace with UEFA Europa League league-phase schedule",
        ),
        Fixture(
            competition="EFL Cup",
            kickoff=start + timedelta(days=9),
            is_home=False,
            venue=_EXAMPLE_VENUES["Villa Park"],
            opponent="[example opponent — EFL Cup, qualification pending]",
            certainty=FixtureCertainty.PROVISIONAL,  # date blocked, progression not yet confirmed
            source="Illustrative placeholder — EFL Cup round date reserved, qualification unconfirmed",
        ),
        Fixture(
            competition="UEFA Europa League",
            kickoff=start + timedelta(days=13),
            is_home=False,
            venue=_EXAMPLE_VENUES["Signal Iduna Park"],
            opponent="[example opponent — Europa League league phase]",
            certainty=FixtureCertainty.CONFIRMED,
            source="Illustrative placeholder — replace with UEFA Europa League league-phase schedule",
        ),
    ]


def fixtures_in_window(fixtures: list[Fixture], start: date, end: date) -> list[Fixture]:
    return [f for f in fixtures if start <= f.kickoff <= end]


def congestion_windows(fixtures: list[Fixture], window_days: int = CONGESTION_WINDOW_DAYS) -> list[tuple[date, date, list[Fixture]]]:
    """
    Slide a rolling window (default matches the spec's own illustrative
    example — 'four matches in eleven days') across the confirmed +
    provisional fixture list and return every window with 2+ matches,
    each tagged with the fixtures that fall inside it.

    This is deliberately dumb/exhaustive — fuelling_risk.py decides what
    to *do* with congestion, this just surfaces the raw candidate windows.
    """
    scored = [f for f in fixtures if f.certainty != FixtureCertainty.UNKNOWN]
    windows = []
    for f in scored:
        start = f.kickoff
        end = start + timedelta(days=window_days)
        in_window = fixtures_in_window(scored, start, end)
        if len(in_window) >= 2:
            windows.append((start, end, in_window))
    return windows
