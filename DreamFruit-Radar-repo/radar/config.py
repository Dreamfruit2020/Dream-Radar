"""
Editable configuration — spec section 6 build requirement:

  "the threshold (2 hours), the day-before/hotel assumption, and the
   coach-vs-flight rule must all be stored as configuration, not
   hardcoded, so they can be corrected or tuned per competition later
   without a code change."

Everything here is deliberately just data. Nothing downstream should
hardcode these values — always read from this module (or, later, from
wherever this gets promoted to — a database row, an env var, whatever)
so a wrong assumption is a config edit, not a redeploy.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TravelRules:
    coach_threshold_hours: float = 2.0   # under this drive time -> coach, else flight
    travel_day_before: bool = True
    hotel_night_before: bool = True
    # average road speed used to estimate drive time from distance, since we
    # don't have real routing — deliberately conservative for UK motorway travel
    assumed_road_speed_kmh: float = 90.0


# Per-competition overrides. Confirmed correct for the Premier League;
# European away trips may warrant different assumptions (longer transfers,
# more likely to fly regardless of distance) — override here if so, rather
# than touching travel.py.
TRAVEL_RULES_BY_COMPETITION: dict[str, TravelRules] = {
    "default": TravelRules(),
    "Premier League": TravelRules(),
    "EFL Cup": TravelRules(),
    "FA Cup": TravelRules(),
    # Deliberately more flight-biased for continental away trips — still a
    # placeholder threshold, tune once real match-day logistics feedback
    # comes in from the pilot.
    "UEFA Europa League": TravelRules(coach_threshold_hours=1.0),
}


def travel_rules_for(competition: str) -> TravelRules:
    return TRAVEL_RULES_BY_COMPETITION.get(competition, TRAVEL_RULES_BY_COMPETITION["default"])


# Rolling windows used for congestion / load-concentration reads.
CONGESTION_WINDOW_DAYS = 11       # matches spec's own illustrative example ("four matches in eleven days")
LOAD_LOOKBACK_DAYS = 28
INTERNATIONAL_SQUAD_ANNOUNCE_LEAD_DAYS = 14  # squads not known further out than this — treat as unknown
FORECAST_RELIABLE_HORIZON_DAYS = 10          # beyond this, climate.py should fall back to historical averages


# ─────────────────────────────────────────────────────────────────────
# Fuelling Risk scoring weights
#
# Every value below is a calibration choice, not a measured constant.
# The reasoning for each one is written out in docs/radar-scoring-design.md
# — if you change a number here, change the reasoning there too, because
# the whole premise of this output is that a club's performance staff can
# ask "how did you calculate that" and get a real answer.
# ─────────────────────────────────────────────────────────────────────


@dataclass
class ScoringWeights:
    # --- congestion (the primary driver) ---
    # Points awarded at 100% elevated-demand-day saturation across the frame.
    congestion_max_points: float = 4.0
    # A single isolated match naturally produces a 3-day elevated run
    # (MD-1, MD, MD+1). Days beyond that mean back-to-back matches with no
    # lower-carbohydrate day in between — the periodisation has collapsed.
    natural_elevated_run_days: int = 3
    contiguity_points_per_day: float = 0.40
    contiguity_cap: float = 2.0

    # --- travel (per fixture, capped) ---
    travel_coach_points: float = 0.15
    travel_flight_points: float = 0.40
    travel_hotel_night_points: float = 0.15
    travel_distance_max_points: float = 0.25
    travel_distance_reference_km: float = 1500.0
    travel_timezone_max_points: float = 0.30
    travel_timezone_reference_hours: float = 3.0
    travel_per_fixture_cap: float = 1.00

    # --- climate (per fixture, capped) ---
    climate_heat_max_points: float = 0.50
    climate_heat_reference_delta_c: float = 10.0
    climate_humidity_max_points: float = 0.30
    climate_humidity_reference_delta_pct: float = 25.0
    climate_cold_max_points: float = 0.20
    climate_cold_reference_delta_c: float = 10.0
    climate_precipitation_points: dict = None  # set in __post_init__
    climate_per_fixture_cap: float = 1.00
    # Beyond the forecast horizon climate.py falls back to historical
    # averages for the venue/month. Still useful, materially less certain.
    climate_historical_discount: float = 0.5

    # --- load concentration (window multiplier) ---
    load_max_uplift: float = 0.30          # never more than +30%: modulates, never creates
    load_notable_excess: float = 0.15      # below this, don't name individual players
    # Players who accrue material minutes over the lookback window —
    # starting XI plus regular rotation. Used to work out what an "even"
    # spread of minutes would look like, so concentration is squad-size
    # independent. Assumption, editable — see design doc.
    assumed_contributing_squad_size: int = 16

    # --- international duty (additive) ---
    international_points_per_player: float = 0.5
    international_cap: float = 2.0

    # --- normalisation + tiers ---
    # Anchor, not an empirical constant: roughly the demand of four matches
    # in eleven days with meaningful away travel — the spec's own worked
    # example of a genuinely hard stretch. Fixed rather than relative to the
    # season's own maximum, so a quiet season doesn't get scored as if it
    # were a hard one.
    reference_demand_points: float = 10.0
    tier_peak_threshold: float = 0.70
    tier_elevated_threshold: float = 0.45

    # Provisional fixtures count at half weight, and structurally cannot
    # lift a window more than one tier on their own (see design doc).
    provisional_weight: float = 0.5

    def __post_init__(self):
        if self.climate_precipitation_points is None:
            self.climate_precipitation_points = {"low": 0.0, "moderate": 0.05, "high": 0.10}


SCORING = ScoringWeights()
