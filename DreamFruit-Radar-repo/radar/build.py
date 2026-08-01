"""
The "night before" data build — spec section 8.

Orchestrates every module into a list of FuellingWindow/NamedDecision
objects for one club + visit date. This is what a rep's prep step runs
ahead of a DFX visit; the PDF/reveal/shareable generators (not yet
built) will consume this output.

Runnable today end-to-end on mock/placeholder data to prove the pipeline
shape — see the loud warnings throughout radar/ before this touches a
real club visit.
"""

from __future__ import annotations

from datetime import date, timedelta

from . import api_football, climate, fixtures as fixtures_mod, international, load
from .config import LOAD_LOOKBACK_DAYS
from .fuelling_risk import compute_fuelling_windows
from .models import FuellingWindow
from .player_bio import get_roster
from .travel import estimate_travel


def build_for_club(club_name: str, home_venue, visit_date: date | None = None) -> list[FuellingWindow]:
    windows, _used_real_fixtures = build_for_club_with_source(club_name, home_venue, visit_date)
    return windows


def build_for_club_with_source(
    club_name: str, home_venue, visit_date: date | None = None
) -> tuple[list[FuellingWindow], bool]:
    """
    Same pipeline as build_for_club(), but also reports whether the
    fixture list came from a real API-Football pull or the illustrative
    placeholder — fixtures drive everything downstream (congestion,
    travel, climate), so that's the meaningful "is this real" signal for
    a caller deciding how to label output. Individual components below
    (roster, load, international) can still each independently fall back
    to their own mock data even when fixtures are real — see
    radar/README.md — so this flag means "primarily real," not
    "every single number is verified live."
    """
    visit_date = visit_date or date.today()

    # Real fixtures when API_FOOTBALL_KEY is set, else the illustrative
    # placeholder set. real_fixtures() returns None (not []) on failure,
    # so a real-but-empty result and "couldn't reach the source" don't
    # get confused — either way we fail toward the known-safe illustrative
    # path rather than silently building on nothing.
    all_fixtures = None
    used_real_fixtures = False
    if api_football.is_configured():
        all_fixtures = fixtures_mod.real_fixtures(
            api_football.CRYSTAL_PALACE_TEAM_ID,
            season=visit_date.year if visit_date.month >= 7 else visit_date.year - 1,
            from_date=visit_date - timedelta(days=LOAD_LOOKBACK_DAYS),
            to_date=visit_date + timedelta(days=30),
        )
        if all_fixtures:
            used_real_fixtures = True
    if not all_fixtures:
        all_fixtures = fixtures_mod.example_fixtures(season_start=visit_date)

    windows = fixtures_mod.congestion_windows(all_fixtures)

    # Fixture is a plain dataclass (unhashable) — key by id() rather than
    # the object itself. These maps are transient within a single build run.
    travel_by_fixture = {id(f): estimate_travel(f, home_venue) for f in all_fixtures}
    climate_by_fixture = {id(f): climate.get_climate_reading(f, home_venue) for f in all_fixtures}

    roster = get_roster()

    # Recent fixtures (already played, within the lookback window) supply
    # the fixture ids real_get_recent_load() needs — see load.py for why
    # this is per-fixture rather than a single season-totals call.
    recent_fixture_ids = [
        f.external_id
        for f in all_fixtures
        if f.external_id is not None and visit_date - timedelta(days=LOAD_LOOKBACK_DAYS) <= f.kickoff < visit_date
    ]
    loads = load.get_recent_load(roster, recent_fixture_ids)
    concentration_ratio, top_loaded = load.load_concentration(loads)

    # international call-ups — only meaningful near a real break date;
    # using a placeholder break window here just to exercise the code path
    example_break_start = visit_date + timedelta(days=20)
    example_break_end = example_break_start + timedelta(days=10)
    call_ups = international.get_call_ups(roster, example_break_start, example_break_end)

    fuelling_windows = compute_fuelling_windows(
        congestion_windows=windows,
        travel_by_fixture=travel_by_fixture,
        climate_by_fixture=climate_by_fixture,
        load_concentration_ratio=concentration_ratio,
        top_loaded_players=top_loaded,
        international_call_ups=call_ups,
        home_venue_name=home_venue.name,
        international_breaks=international.INTERNATIONAL_BREAKS,
    )

    return fuelling_windows, used_real_fixtures


if __name__ == "__main__":
    from .fixtures import SELHURST_PARK

    result = build_for_club("Crystal Palace FC", SELHURST_PARK)

    print(f"\n{'='*74}")
    print("DREAM RADAR — scaffold run")
    print("Scoring formula is real (see docs/radar-scoring-design.md).")
    print("Fixture, climate, load and roster DATA below is mock — not real output.")
    print(f"{'='*74}\n")

    for w in result:
        f = w.contributing_factors
        print(f"[{str(f['tier']).upper()}]  {w.start} -> {w.end}   severity {w.severity:.2f}")
        print(f"  driver: {f['dominant_driver']}   demand points: {f['demand_points']}")
        print(
            f"  breakdown: congestion {f['congestion']} + contiguity {f['contiguity']} "
            f"+ travel {f['travel']} + climate {f['climate']} "
            f"x load {f['load_multiplier']} + intl {f['international']}"
        )
        print(
            f"  {int(f['elevated_days'])}/{int(f['frame_days'])} elevated days, "
            f"longest run {int(f['longest_elevated_run_days'])} days, "
            f"confirmed-only severity {f['severity_confirmed_only']:.2f}"
        )
        if w.decision:
            print(f"  FINDING:  {w.decision.finding}")
            print(f"  DECISION: {w.decision.decision_question}")
            print(f"  confidence: {w.decision.confidence.value}   matrix hook: {w.decision.matrix_hook}")
            if w.decision.players_of_note:
                print(f"  players of note: {', '.join(w.decision.players_of_note)}")
        print()
