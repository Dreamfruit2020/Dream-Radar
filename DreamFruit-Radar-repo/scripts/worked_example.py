#!/usr/bin/env python3
"""
Worked example for the Fuelling Risk formula — Crystal Palace FC.

WHAT IS REAL HERE: the competition mix (Premier League, Europa League
league phase, EFL Cup, FA Cup — Palace qualified for the 2026/27 Europa
League as 2026 Conference League winners), the venue coordinates, and
the scoring formula itself.

WHAT IS NOT REAL: the specific dates, opponents, climate figures and
minutes played. Those are a plausible reconstruction of a late-autumn
stretch, standing in for a live fixture pull. Nothing in this file
should be shown to a club as a statement about their actual season.

Run: python3 scripts/worked_example.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from radar.config import CONGESTION_WINDOW_DAYS, SCORING
from radar.fixtures import SELHURST_PARK, congestion_windows
from radar.fuelling_risk import compute_fuelling_windows
from radar.models import (
    ClimateReading,
    Fixture,
    FixtureCertainty,
    PlayerBio,
    PlayerLoad,
    Venue,
)
from radar.travel import estimate_travel

# Real stadiums, real coordinates.
ST_JAMES = Venue("St James' Park", 54.9756, -1.6217, 1.0)
DA_LUZ = Venue("Estadio da Luz", 38.7527, -9.1846, 1.0)
VILLA_PARK = Venue("Villa Park", 52.5092, -1.8848, 1.0)

# Illustrative stretch — plausible shape, not an asserted fixture list.
FIXTURES = [
    Fixture("Premier League", date(2026, 11, 21), False, ST_JAMES,
            "[away, north-east]", FixtureCertainty.CONFIRMED,
            "Illustrative — replace with official Premier League fixture list"),
    Fixture("UEFA Europa League", date(2026, 11, 26), False, DA_LUZ,
            "[away, Portugal — league phase]", FixtureCertainty.CONFIRMED,
            "Illustrative — replace with UEFA Europa League league-phase schedule"),
    Fixture("Premier League", date(2026, 11, 29), True, SELHURST_PARK,
            "[home]", FixtureCertainty.CONFIRMED,
            "Illustrative — replace with official Premier League fixture list"),
    Fixture("EFL Cup", date(2026, 12, 2), False, VILLA_PARK,
            "[away — quarter-final, qualification pending]", FixtureCertainty.PROVISIONAL,
            "Illustrative — EFL Cup round date reserved, progression unconfirmed"),
    Fixture("Premier League", date(2026, 12, 5), True, SELHURST_PARK,
            "[home]", FixtureCertainty.CONFIRMED,
            "Illustrative — replace with official Premier League fixture list"),
    # A second, separated cluster — two home fixtures a week apart, no
    # travel, no provisional fixtures. Deliberately included to show what
    # a "standard" window looks like next to the peak one above: the
    # season-arc contrast the spec asks Radar to surface (section 5),
    # not just a single alarming data point.
    Fixture("Premier League", date(2027, 1, 10), True, SELHURST_PARK,
            "[home]", FixtureCertainty.CONFIRMED,
            "Illustrative — replace with official Premier League fixture list"),
    Fixture("Premier League", date(2027, 1, 17), True, SELHURST_PARK,
            "[home]", FixtureCertainty.CONFIRMED,
            "Illustrative — replace with official Premier League fixture list"),
]

# Illustrative climate: a cold north-east away day, a materially milder
# Lisbon midweek, London baseline at home. Beyond the 10-day forecast
# horizon, so flagged as historical averages and discounted accordingly.
CLIMATE = {
    "St James' Park": (-3.0, 5.0, "high"),
    "Estadio da Luz": (8.0, 12.0, "low"),
    "Selhurst Park": (0.0, 0.0, "moderate"),
    "Villa Park": (-1.0, 3.0, "moderate"),
}

# Illustrative squad: a settled starting group, minutes concentrated on
# three players. Names are placeholders — this repo does not assert
# minutes played for real, named individuals without a live source.
TOP_LOADED = [
    PlayerLoad(PlayerBio("[Player A]", 27, 183, 78, "Centre-midfield", "Illustrative", date(2026, 11, 20)),
               540, 6, "Illustrative — replace with a cited public stats source"),
    PlayerLoad(PlayerBio("[Player B]", 24, 178, 74, "Winger", "Illustrative", date(2026, 11, 20)),
               505, 6, "Illustrative — replace with a cited public stats source"),
    PlayerLoad(PlayerBio("[Player C]", 30, 190, 86, "Centre-back", "Illustrative", date(2026, 11, 20)),
               490, 6, "Illustrative — replace with a cited public stats source"),
]
CONCENTRATION_RATIO = 0.32  # top 3 of a ~16-player contributing group


def build_example_windows():
    """Reusable by other scripts (e.g. scripts/make_radar_briefing.py) so
    the illustrative Crystal Palace stretch is defined in exactly one
    place. Returns (windows, travel_by_fixture, climate_by_fixture)."""
    travel = {id(f): estimate_travel(f, SELHURST_PARK) for f in FIXTURES}
    climate = {}
    for f in FIXTURES:
        t, h, p = CLIMATE[f.venue.name]
        climate[id(f)] = ClimateReading(f, t, h, p, is_forecast=False,
                                        source="Illustrative — replace with a real weather API")

    windows = compute_fuelling_windows(
        congestion_windows=congestion_windows(FIXTURES, CONGESTION_WINDOW_DAYS),
        travel_by_fixture=travel,
        climate_by_fixture=climate,
        load_concentration_ratio=CONCENTRATION_RATIO,
        top_loaded_players=TOP_LOADED,
        international_call_ups=[],
        home_venue_name="Selhurst Park",
    )
    return windows, travel, climate


def get_windows(visit_date: date | None = None) -> tuple[list, bool]:
    """
    Real-with-fallback entry point for every deliverable generator
    (make_radar_briefing.py, make_radar_teaser.py, make_radar_shareable.py).

    Tries radar.build.build_for_club_with_source() first — real fixtures,
    roster, load, climate and call-ups when API_FOOTBALL_KEY is set and
    reachable. Falls back to THIS file's curated illustrative stretch
    (not radar.fixtures.example_fixtures()'s generic placeholder) so the
    fallback experience stays exactly the demo that's already been
    visually verified throughout this repo, rather than a different,
    untested illustrative set.

    Any unexpected failure in the real path (not just "no key
    configured") also falls back here rather than crashing the ops
    tool — fail toward the known-safe illustrative output, never toward
    a broken page.

    Returns (windows, is_real_data).
    """
    from radar.build import build_for_club_with_source

    try:
        real_windows, used_real = build_for_club_with_source(
            "Crystal Palace FC", SELHURST_PARK, visit_date
        )
        if used_real and real_windows:
            return real_windows, True
    except Exception:
        pass  # fall through to the illustrative path below

    example_windows, _, _ = build_example_windows()
    return example_windows, False


def main() -> None:
    travel = {id(f): estimate_travel(f, SELHURST_PARK) for f in FIXTURES}
    climate = {}
    for f in FIXTURES:
        t, h, p = CLIMATE[f.venue.name]
        climate[id(f)] = ClimateReading(f, t, h, p, is_forecast=False,
                                        source="Illustrative — replace with a real weather API")

    print("\n" + "=" * 76)
    print("DREAM RADAR — FUELLING RISK, WORKED EXAMPLE")
    print("Crystal Palace FC · illustrative late-autumn stretch")
    print("Formula is real. Dates, opponents, climate and minutes are illustrative.")
    print("=" * 76)

    print("\nINPUT — fixtures")
    for f in FIXTURES:
        est = travel[id(f)]
        where = "H" if f.is_home else "A"
        print(
            f"  {f.kickoff}  {where}  {f.competition:<20} {f.venue.name:<18} "
            f"{est.distance_km:>7,.0f} km  {est.mode.value:<7} {f.certainty.value}"
        )

    print(f"\nINPUT — load concentration: top 3 carry {CONCENTRATION_RATIO:.0%} of squad minutes")
    print(f"INPUT — even spread would be {3 / SCORING.assumed_contributing_squad_size:.0%} "
          f"(assumed contributing squad of {SCORING.assumed_contributing_squad_size})")

    windows = compute_fuelling_windows(
        congestion_windows=congestion_windows(FIXTURES, CONGESTION_WINDOW_DAYS),
        travel_by_fixture=travel,
        climate_by_fixture=climate,
        load_concentration_ratio=CONCENTRATION_RATIO,
        top_loaded_players=TOP_LOADED,
        international_call_ups=[],
        home_venue_name="Selhurst Park",
    )

    print(f"\nOUTPUT — {len(windows)} window(s)\n")
    for i, w in enumerate(windows, 1):
        f = w.contributing_factors
        print(f"  WINDOW {i} — {str(f['tier']).upper()}   {w.start} to {w.end}")
        print(f"    severity            {w.severity:.2f}  ({f['demand_points']} demand points "
              f"/ {SCORING.reference_demand_points:.0f} reference)")
        print(f"    confirmed-only      {f['severity_confirmed_only']:.2f}")
        print(f"    dominant driver     {f['dominant_driver']}")
        print(f"    congestion          {f['congestion']:.2f}   "
              f"({int(f['elevated_days_calendar'])} of {int(f['frame_days'])} days elevated)")
        print(f"    contiguity          {f['contiguity']:.2f}   "
              f"(longest run {int(f['longest_elevated_run_days'])} days, "
              f"{int(f['no_reset_days'])} with no reset)")
        print(f"    travel              {f['travel']:.2f}")
        print(f"    climate             {f['climate']:.2f}")
        print(f"    load multiplier     x{f['load_multiplier']:.3f}")
        print(f"    international       {f['international']:.2f}")
        print(f"    confidence          {w.decision.confidence.value}")
        print(f"\n    FINDING")
        for line in _wrap(w.decision.finding, 68):
            print(f"      {line}")
        print(f"\n    DECISION IT BEARS ON")
        for line in _wrap(w.decision.decision_question, 68):
            print(f"      {line}")
        if w.decision.players_of_note:
            print(f"\n    PLAYERS OF NOTE   {', '.join(w.decision.players_of_note)}")
        print(f"    MATRIX HOOK       {w.decision.matrix_hook}")
        print(f"\n    CITATIONS")
        for c in w.decision.citations:
            for j, line in enumerate(_wrap(c, 64)):
                print(f"      {'- ' if j == 0 else '  '}{line}")
        print()


def _wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for word in words:
        if len(cur) + len(word) + 1 > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    main()
