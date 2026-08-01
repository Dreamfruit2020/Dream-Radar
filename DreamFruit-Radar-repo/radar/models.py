"""
Core data shapes shared across the Radar pipeline.

These are the contracts between modules — travel.py, climate.py, load.py etc.
all produce/consume these, and fuelling_risk.py (the Opus-designed piece)
consumes all of them to produce FuellingWindow + NamedDecision objects that
build.py hands off to the PDF/reveal/shareable generators and, eventually,
the Performance Matrix session (spec section 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class FixtureCertainty(str, Enum):
    """Spec section 6, 'Handling fixture uncertainty'."""

    CONFIRMED = "confirmed"        # domestic league, continental league phase
    PROVISIONAL = "provisional"    # cup round date blocked, qualification not yet confirmed
    UNKNOWN = "unknown"            # beyond current season's picture — excluded from scoring


class TravelMode(str, Enum):
    COACH = "coach"
    FLIGHT = "flight"
    HOME = "home"  # not an away fixture


@dataclass
class Venue:
    name: str
    latitude: float
    longitude: float
    timezone_offset_hours: float  # relative to UTC, standard time


@dataclass
class Fixture:
    competition: str
    kickoff: date
    is_home: bool
    venue: Venue
    opponent: str
    certainty: FixtureCertainty
    source: str  # citation — e.g. "Premier League official fixture list, pulled 2026-07-19"
    external_id: int | None = None  # API-Football fixture id, when sourced from real_fixtures()


@dataclass
class TravelEstimate:
    """Computed, not sourced directly — see travel.py. Always an estimate,
    per spec section 6: 'never presented as confirmed fact about this
    specific club.'"""

    fixture: Fixture
    distance_km: float
    mode: TravelMode
    travel_day_before: bool
    hotel_night_before: bool
    timezone_delta_hours: float
    basis: str = "Estimated from standard club practice (config-driven heuristic), not confirmed club logistics."


@dataclass
class ClimateReading:
    fixture: Fixture
    temp_delta_c: float          # away venue vs. home, positive = warmer
    humidity_delta_pct: float
    precipitation_risk: str      # "low" | "moderate" | "high"
    is_forecast: bool            # True if within ~10 days, else historical-average based
    source: str


@dataclass
class PlayerBio:
    name: str
    age: int | None
    height_cm: int | None
    weight_kg: int | None
    position: str
    source: str
    as_of: date  # staleness caveat — spec section 6


@dataclass
class PlayerLoad:
    player: PlayerBio
    minutes_last_28_days: int
    matches_last_28_days: int
    source: str


@dataclass
class InternationalCallUp:
    player: PlayerBio
    nation: str
    confirmed: bool  # False until squad announced ~1-2 weeks before the break
    break_start: date
    break_end: date
    source: str


class ConfidenceLevel(str, Enum):
    """Spec section 9: 'Confidence, not certainty.'"""

    PROVISIONAL = "provisional"      # early signal, inputs incomplete (e.g. call-ups not yet announced)
    LIKELY = "likely"                # good signal, some estimated components (e.g. travel heuristic)
    CONFIRMED = "confirmed"          # based on confirmed fixtures/data only


@dataclass
class NamedDecision:
    """The connective layer between Radar and the Performance Matrix —
    spec section 5, 'Every finding names the decision it bears on.'

    This is what gets handed to the Matrix session at step 5, and what
    (in aggregate, anonymised) can inform DreamFruit's own product
    development per the same spec section.
    """

    window_start: date
    window_end: date
    finding: str              # declarative, evidenced statement of fact
    decision_question: str    # framed as a question back to the practitioner, never a directive
    players_of_note: list[str]
    confidence: ConfidenceLevel
    citations: list[str]
    matrix_hook: str | None = None  # which Matrix screen/observation this should pre-surface


@dataclass
class FuellingWindow:
    """Output of fuelling_risk.py (Opus-designed formula) — a scored window
    plus the NamedDecision derived from it."""

    start: date
    end: date
    severity: float  # 0-1, normalised against a fixed reference — see fuelling_risk.py
    # Full component breakdown: every number that went into the severity,
    # plus the derived tier and dominant driver as strings. This is what
    # makes the score explainable rather than a black box, so it travels
    # with the window rather than being recomputed downstream.
    contributing_factors: dict[str, float | str] = field(default_factory=dict)
    decision: NamedDecision | None = None
