"""
Travel burden — computed, not sourced. Spec section 6.

Real, working logic: this is one of the two pieces (alongside fixture
tiering) that doesn't need live data integration or the Opus scoring
session to be correct today. Everything here reads its assumptions from
config.py, per the "must stay editable" build requirement.

We do not know a club's actual travel logistics — this produces a
well-informed estimate based on standard practice, always labelled as
such downstream (see TravelEstimate.basis in models.py).
"""

from __future__ import annotations

import math

from .config import travel_rules_for
from .models import Fixture, TravelEstimate, TravelMode, Venue


def haversine_km(a: Venue, b: Venue) -> float:
    """Great-circle distance between two venues, in km."""
    r = 6371.0  # earth radius km
    lat1, lon1 = math.radians(a.latitude), math.radians(a.longitude)
    lat2, lon2 = math.radians(b.latitude), math.radians(b.longitude)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def estimate_travel(fixture: Fixture, home_venue: Venue) -> TravelEstimate:
    """Estimate travel burden for a single fixture relative to the club's
    home venue. Home fixtures return a HOME-mode, zero-burden estimate."""

    if fixture.is_home:
        return TravelEstimate(
            fixture=fixture,
            distance_km=0.0,
            mode=TravelMode.HOME,
            travel_day_before=False,
            hotel_night_before=False,
            timezone_delta_hours=0.0,
        )

    rules = travel_rules_for(fixture.competition)
    distance = haversine_km(home_venue, fixture.venue)
    estimated_drive_hours = distance / rules.assumed_road_speed_kmh

    mode = TravelMode.COACH if estimated_drive_hours < rules.coach_threshold_hours else TravelMode.FLIGHT
    tz_delta = fixture.venue.timezone_offset_hours - home_venue.timezone_offset_hours

    return TravelEstimate(
        fixture=fixture,
        distance_km=round(distance, 1),
        mode=mode,
        travel_day_before=rules.travel_day_before,
        hotel_night_before=rules.hotel_night_before,
        timezone_delta_hours=tz_delta,
    )
