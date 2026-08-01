#!/usr/bin/env python3
"""
Guardrail tests for the Fuelling Risk scoring formula.

These are not unit tests of arithmetic — they are checks that the formula
keeps the promises the spec makes to a club. Every assertion here maps to
a stated guardrail in docs/dream-radar-spec.md section 9 or a design rule
in docs/radar-scoring-design.md.

Run: python3 scripts/verify_scoring.py
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from radar.config import CONGESTION_WINDOW_DAYS, SCORING
from radar.fixtures import congestion_windows
from radar.fuelling_risk import compute_fuelling_windows, _tier_index
from radar.international import InternationalBreak
from radar.models import (
    ClimateReading,
    ConfidenceLevel,
    Fixture,
    FixtureCertainty,
    InternationalCallUp,
    PlayerBio,
    PlayerLoad,
    Venue,
)
from radar.travel import estimate_travel

HOME = Venue("Selhurst Park", 51.3983, -0.0855, 1.0)
AWAY_NEAR = Venue("Villa Park", 52.5092, -1.8848, 1.0)
AWAY_FAR = Venue("Estadio da Luz", 38.7527, -9.1846, 1.0)

D0 = date(2026, 9, 1)

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


def fx(day_offset: int, *, home=True, venue=None, certainty=FixtureCertainty.CONFIRMED,
       competition="Premier League") -> Fixture:
    return Fixture(
        competition=competition,
        kickoff=D0 + timedelta(days=day_offset),
        is_home=home,
        venue=venue or (HOME if home else AWAY_NEAR),
        opponent="[test opponent]",
        certainty=certainty,
        source="TEST FIXTURE — not real",
    )


def climate(fixture, temp_delta=0.0, humidity_delta=0.0, precip="low", is_forecast=True):
    return ClimateReading(
        fixture=fixture,
        temp_delta_c=temp_delta,
        humidity_delta_pct=humidity_delta,
        precipitation_risk=precip,
        is_forecast=is_forecast,
        source="TEST DATA — not real",
    )


def run(fixtures, *, temp_delta=0.0, humidity=0.0, is_forecast=True,
        concentration=0.19, top_n=3, call_ups=None, breaks=None, as_of=None):
    """Score a fixture list with fully controlled, deterministic inputs."""
    travel = {id(f): estimate_travel(f, HOME) for f in fixtures}
    clim = {
        id(f): climate(f, temp_delta=temp_delta, humidity_delta=humidity, is_forecast=is_forecast)
        for f in fixtures
    }
    roster = [
        PlayerBio(f"[Player {c}]", 25, 180, 78, "Midfielder", "TEST", D0)
        for c in "ABC"[:top_n]
    ]
    top = [PlayerLoad(p, 400, 5, "TEST") for p in roster]
    return compute_fuelling_windows(
        congestion_windows=congestion_windows(fixtures, CONGESTION_WINDOW_DAYS),
        travel_by_fixture=travel,
        climate_by_fixture=clim,
        load_concentration_ratio=concentration,
        top_loaded_players=top,
        international_call_ups=call_ups or [],
        home_venue_name="Selhurst Park",
        international_breaks=breaks or [],
        as_of=as_of,
    )


def top_severity(windows):
    return windows[0].severity if windows else 0.0


print("\nFuelling Risk scoring — guardrail verification")
print("=" * 62)

# ── 1. Congestion is the primary driver and behaves monotonically ────
print("\n1. Congestion behaves monotonically")

two = run([fx(0), fx(4)])
three = run([fx(0), fx(4), fx(8)])
four = run([fx(0), fx(3), fx(6), fx(9)])

check(
    "more matches in the same span score higher",
    top_severity(two) < top_severity(three) < top_severity(four),
    f"{top_severity(two)} / {top_severity(three)} / {top_severity(four)}",
)

tight = run([fx(0), fx(2), fx(4)])
spread = run([fx(0), fx(5), fx(10)])
check(
    "same match count, tighter turnarounds score higher",
    top_severity(tight) > top_severity(spread),
    f"tight {top_severity(tight)} vs spread {top_severity(spread)}",
)

single = run([fx(0)])
check("a lone fixture produces no window at all", single == [], f"got {len(single)} windows")

# ── 2. Provisional fixtures cannot manufacture a top-tier window ─────
print("\n2. Provisional fixtures are structurally constrained")

all_prov = run([
    fx(0, home=False, certainty=FixtureCertainty.PROVISIONAL, competition="EFL Cup"),
    fx(2, home=False, certainty=FixtureCertainty.PROVISIONAL, competition="EFL Cup"),
    fx(4, home=False, certainty=FixtureCertainty.PROVISIONAL, competition="FA Cup"),
    fx(6, home=False, certainty=FixtureCertainty.PROVISIONAL, competition="FA Cup"),
], temp_delta=8.0, humidity=20.0)

check(
    "an all-provisional stretch never reaches peak tier",
    all(w.contributing_factors["tier"] != "peak" for w in all_prov),
    f"tiers: {[w.contributing_factors['tier'] for w in all_prov]}",
)
check(
    "an all-provisional stretch is labelled provisional confidence",
    all(w.decision.confidence == ConfidenceLevel.PROVISIONAL for w in all_prov),
)

mixed = run([
    fx(0), fx(4),
    fx(7, certainty=FixtureCertainty.PROVISIONAL, competition="EFL Cup"),
    fx(9, certainty=FixtureCertainty.PROVISIONAL, competition="EFL Cup"),
])
check(
    "displayed tier is never more than one above the confirmed-only tier",
    all(
        _tier_index(w.severity) <= _tier_index(w.contributing_factors["severity_confirmed_only"]) + 1
        for w in mixed + all_prov
    ),
)
check(
    "provisional fixtures are named in the finding, not hidden in the score",
    all("half weight until confirmed" in w.decision.finding for w in mixed),
)

confirmed_equiv = run([fx(0), fx(4), fx(7), fx(9)])
check(
    "the same stretch scores lower when two fixtures are only provisional",
    top_severity(mixed) < top_severity(confirmed_equiv),
    f"mixed {top_severity(mixed)} vs confirmed {top_severity(confirmed_equiv)}",
)

# ── 3. Travel and climate move the score in the right direction ──────
print("\n3. Travel and climate contribute correctly")

home_only = run([fx(0), fx(4), fx(8)])
away_far = run([
    fx(0, home=False, venue=AWAY_FAR, competition="UEFA Europa League"),
    fx(4, home=False, venue=AWAY_FAR, competition="UEFA Europa League"),
    fx(8, home=False, venue=AWAY_FAR, competition="UEFA Europa League"),
])
check(
    "long-haul away fixtures score above the identical home schedule",
    top_severity(away_far) > top_severity(home_only),
    f"away {top_severity(away_far)} vs home {top_severity(home_only)}",
)
check("home fixtures contribute zero travel", home_only[0].contributing_factors["travel"] == 0.0)

hot = run([fx(0), fx(4), fx(8)], temp_delta=10.0, humidity=25.0)
cold = run([fx(0), fx(4), fx(8)], temp_delta=-10.0)
temperate = run([fx(0), fx(4), fx(8)])
check(
    "heat scores above temperate, and above cold",
    top_severity(hot) > top_severity(cold) > top_severity(temperate),
    f"hot {top_severity(hot)} / cold {top_severity(cold)} / temperate {top_severity(temperate)}",
)

forecast = run([fx(0), fx(4), fx(8)], temp_delta=10.0, is_forecast=True)
historical = run([fx(0), fx(4), fx(8)], temp_delta=10.0, is_forecast=False)
check(
    "historical-average climate is discounted against a real forecast",
    historical[0].contributing_factors["climate"] < forecast[0].contributing_factors["climate"],
    f"{historical[0].contributing_factors['climate']} vs {forecast[0].contributing_factors['climate']}",
)
check(
    "historical-average climate is disclosed in the finding when it drives the window",
    all(
        "historical averages" in w.decision.finding
        for w in historical
        if w.contributing_factors["dominant_driver"] == "climate"
    ),
)

# ── 4. Load concentration modulates but never creates ────────────────
print("\n4. Load concentration is bounded")

even = run([fx(0), fx(4), fx(8)], concentration=0.19)
skewed = run([fx(0), fx(4), fx(8)], concentration=0.85)
check("uneven minutes raise the score", top_severity(skewed) > top_severity(even))
check(
    "the load multiplier stays inside its declared bound",
    all(
        1.0 <= w.contributing_factors["load_multiplier"] <= 1.0 + SCORING.load_max_uplift + 1e-9
        for w in even + skewed
    ),
)
check(
    "players are not named when minutes are spread evenly",
    all(w.decision.players_of_note == [] for w in even),
    f"{even[0].decision.players_of_note}",
)
check(
    "named players always come with a stated reason in the finding",
    all(
        ("highest share of minutes" in w.decision.finding or "concentrated" in w.decision.finding)
        for w in skewed
        if w.decision.players_of_note
    ),
)

# ── 5. International duty only counts once squads are published ──────
print("\n5. International duty")

break_start = D0 + timedelta(days=2)
roster_player = PlayerBio("[Player A]", 25, 180, 78, "Midfielder", "TEST", D0)
unannounced = InternationalCallUp(roster_player, "[nation]", False, break_start,
                                  break_start + timedelta(days=8), "TEST")
announced = InternationalCallUp(roster_player, "[nation]", True, break_start,
                                break_start + timedelta(days=8), "TEST")

no_squad = run([fx(0), fx(4), fx(8)], call_ups=[unannounced])
with_squad = run([fx(0), fx(4), fx(8)], call_ups=[announced])
check(
    "an unconfirmed call-up contributes nothing",
    no_squad[0].contributing_factors["international"] == 0.0,
)
check(
    "a confirmed call-up contributes",
    with_squad[0].contributing_factors["international"] > 0.0,
)

# ── 5b. Unannounced break overlapping a window is disclosed, not silent ──
print("\n5b. Unannounced international break is flagged, not read as zero")

far_break = InternationalBreak(D0 + timedelta(days=60), D0 + timedelta(days=68), "TEST BREAK")
overlapping_far = run(
    [fx(58), fx(62), fx(66)], breaks=[far_break], as_of=D0,
)
check(
    "a window overlapping a not-yet-announceable break gets the caveat in its finding",
    any("isn't known yet" in w.decision.finding for w in overlapping_far),
    f"{[w.decision.finding for w in overlapping_far]}",
)
check(
    "confidence cannot read as confirmed when an unannounced break overlaps",
    all(w.decision.confidence != ConfidenceLevel.CONFIRMED for w in overlapping_far),
)

near_break = InternationalBreak(D0 + timedelta(days=5), D0 + timedelta(days=13), "TEST BREAK")
overlapping_near = run(
    [fx(3), fx(7), fx(11)], breaks=[near_break], as_of=D0,
)
check(
    "the same overlap does NOT get the caveat once the break is close enough to be announceable",
    all("isn't known yet" not in w.decision.finding for w in overlapping_near),
)

no_overlap = run([fx(0), fx(4), fx(8)], breaks=[far_break], as_of=D0)
check(
    "a break that doesn't overlap the window is not mentioned at all",
    all("isn't known yet" not in w.decision.finding for w in no_overlap),
)

# ── 6. Output integrity ──────────────────────────────────────────────
print("\n6. Output integrity and guardrails")

everything = run([
    fx(0, home=False, venue=AWAY_FAR, competition="UEFA Europa League"),
    fx(3),
    fx(6, home=False, certainty=FixtureCertainty.PROVISIONAL, competition="EFL Cup"),
    fx(9, home=False, venue=AWAY_FAR, competition="UEFA Europa League"),
], temp_delta=7.0, humidity=15.0, concentration=0.6, call_ups=[announced])

all_windows = (
    two + three + four + mixed + all_prov + away_far + hot + skewed + everything
    + overlapping_far + overlapping_near + no_overlap
)

check(
    "severity always sits inside 0-1",
    all(0.0 <= w.severity <= 1.0 for w in all_windows),
)
check(
    "severity and tier label never disagree",
    all(w.contributing_factors["tier"] == ("peak", "elevated", "standard")[
        2 - _tier_index(w.severity)] for w in all_windows),
)
check(
    "every window carries a named decision framed as a question",
    all(w.decision and w.decision.decision_question.strip().endswith("?") for w in all_windows),
)
check(
    "no finding is framed as a question — findings stay declarative",
    all("?" not in w.decision.finding for w in all_windows),
)
check(
    "every window carries at least two citations",
    all(len(w.decision.citations) >= 2 for w in all_windows),
)
check(
    "every window hooks into a Performance Matrix screen",
    all(w.decision.matrix_hook for w in all_windows),
)

BANNED = ("injur", "medical", "diagnos", "predict", "at risk", "danger", "unsafe")
offenders = [
    (term, w.decision.finding)
    for w in all_windows
    for term in BANNED
    if term in (w.decision.finding + " " + w.decision.decision_question).lower()
]
check(
    "no output text implies injury, medical or predictive claims",
    not offenders,
    f"{offenders[:1]}",
)

# ── 7. Window selection ──────────────────────────────────────────────
print("\n7. Window selection")

two_clusters = run([fx(0), fx(3), fx(30), fx(33)])
check(
    "two separated clusters produce two windows",
    len(two_clusters) == 2,
    f"got {len(two_clusters)}",
)
check(
    "returned windows never overlap each other",
    all(
        a.end < b.start or b.end < a.start
        for i, a in enumerate(two_clusters)
        for b in two_clusters[i + 1:]
    ),
)
check(
    "one tight cluster collapses to a single window, not one per fixture",
    len(four) == 1,
    f"got {len(four)} windows from 4 clustered fixtures",
)
check(
    "windows are returned in descending order of severity",
    all(a.severity >= b.severity for a, b in zip(all_prov, all_prov[1:]))
    and all(a.severity >= b.severity for a, b in zip(two_clusters, two_clusters[1:])),
)

print("\n" + "=" * 62)
if FAILURES:
    print(f"{len(FAILURES)} of {CHECKS} checks FAILED:")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print(f"All {CHECKS} guardrail checks passed.")
