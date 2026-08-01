"""
Fuelling Risk composite scoring.

Designed per docs/radar-scoring-handoff.md; the full reasoning behind
every weight lives in docs/radar-scoring-design.md. Read that before
changing a number here — the entire premise of this output is that a
club's own performance staff can ask "how did you calculate that" and
get a real answer.

The unit throughout is a Fuelling Demand Point (FDP). It is not a
measured quantity; it is a transparent accumulation of named, cited
contributions, normalised at the end against a fixed reference so
windows stay comparable across clubs and seasons.

GUARDRAIL, non-negotiable (spec section 9): this produces a *fuelling
demand* reading. It is not, and must never be presented as, an injury
or illness risk prediction for any named player. Where players are
named, they are named for a fact about minutes played — nothing more.
"""

from __future__ import annotations

from datetime import date, timedelta

from .config import SCORING
from .international import squad_announceable
from .models import (
    ClimateReading,
    ConfidenceLevel,
    FixtureCertainty,
    FuellingWindow,
    InternationalCallUp,
    NamedDecision,
    PlayerLoad,
    TravelMode,
)

# ─────────────────────────────────────────────────────────────────────
# Citations. Every scoring component points at one of these. Nothing in
# the output is allowed to be an unexplained number — where a weight is
# a DreamFruit calibration rather than a published finding, the citation
# says exactly that.
# ─────────────────────────────────────────────────────────────────────

CITE_UEFA = (
    "UEFA Expert Group Statement on Nutrition in Elite Football "
    "(British Journal of Sports Medicine, 2021): match day, MD-1 and MD+1 carry a "
    "raised carbohydrate target of roughly 6-8 g/kg body mass/day, against roughly "
    "3-6 g/kg on other days."
)
CITE_TURNAROUND = (
    "Monitoring of Post-match Fatigue in Professional Soccer (Sports Medicine, 2018): "
    "during congested schedules the 3-4 day turnaround between matches may be "
    "insufficient to fully restore players."
)
CITE_HEAT = (
    "Football hydration research (Gatorade Sports Science Institute, "
    "Hydration Science and Strategies in Football) reports substantially higher sweat "
    "rates in hot versus temperate match conditions; players drink more in the heat but "
    "arrive at a similar level of dehydration."
)
CITE_IOC = (
    "IOC Consensus Statement on Sports Nutrition (2010): limit dehydration to under "
    "roughly 2% of body mass, and replace both water and salts during recovery."
)
CITE_TRAVEL = (
    "Travel burden is estimated, not confirmed: the coach-versus-flight threshold and the "
    "travel-day-before and hotel-night assumptions are the club-practice heuristic in "
    "radar/config.py, applied per competition. Never presented as this club's actual "
    "logistics."
)
CITE_LOAD = (
    "A squad does not experience congestion uniformly - a regular starter and an unused "
    "substitute face different refuelling problems in the same week. Weighting is a "
    "DreamFruit calibration; see docs/radar-scoring-design.md."
)
CITE_INTERNATIONAL = (
    "For the duration of an international break, a called-up player's feeding, travel "
    "and recovery sit outside club control. Weighting is a DreamFruit calibration; "
    "call-ups are only counted once national squads are published."
)
CITE_CALIBRATION = (
    "Severity is normalised against a fixed reference of "
    f"{SCORING.reference_demand_points:.0f} demand points (roughly four matches in "
    "eleven days with meaningful away travel), not against this season's own maximum, "
    "so a quiet season is not scored as though it were a hard one."
)

TIER_NAMES = ("standard", "elevated", "peak")

CITE_BREAK_UNANNOUNCED = (
    "FIFA international match calendar confirms a break falls in this window; which players "
    "are called up is not yet known — national squads are typically published only 1-2 weeks "
    "before a break."
)


# ─────────────────────────────────────────────────────────────────────
# Component scoring
# ─────────────────────────────────────────────────────────────────────


def _certainty_weight(fixture) -> float:
    """Confirmed fixtures count in full. Provisional ones count at half —
    a cup round whose qualification is unconfirmed is, on a neutral read,
    a coin flip. Unknown fixtures never reach this function; fixtures.py
    filters them out before windowing."""
    if fixture.certainty == FixtureCertainty.PROVISIONAL:
        return SCORING.provisional_weight
    return 1.0


def _elevated_day_weights(fixtures, frame_start: date, frame_end: date) -> dict[date, float]:
    """
    The congestion core, built on the UEFA statement rather than on a raw
    match count: every fixture raises the carbohydrate requirement on
    MD-1, MD and MD+1. Union those days across the window.

    A day is either elevated or it isn't, so overlapping fixtures take the
    MAX weight for a shared day, never the sum — two matches cannot make a
    single day more than elevated. What back-to-back matches actually do is
    remove the lower-intake days in between, and that is picked up
    separately by the contiguity term.
    """
    weights: dict[date, float] = {}
    for f in fixtures:
        w = _certainty_weight(f)
        for offset in (-1, 0, 1):
            d = f.kickoff + timedelta(days=offset)
            if frame_start <= d <= frame_end:
                weights[d] = max(weights.get(d, 0.0), w)
    return weights


def _longest_elevated_run(weights: dict[date, float]) -> int:
    """Longest unbroken run of elevated days. A single isolated match
    produces a run of 3; anything longer means matches close enough
    together that the periodised lower-carbohydrate days disappear."""
    if not weights:
        return 0
    days = sorted(weights)
    longest = run = 1
    for prev, cur in zip(days, days[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        longest = max(longest, run)
    return longest


def _travel_points(estimate) -> float:
    """Per-fixture travel burden. Home fixtures score zero — the club
    controls every meal. Away burden is read entirely off the
    spec-confirmed heuristic in config.py (this session does not redesign
    it) and translated into demand on one argument: how many consecutive
    feeding opportunities move outside club catering."""
    if estimate is None or estimate.mode == TravelMode.HOME:
        return 0.0

    pts = SCORING.travel_flight_points if estimate.mode == TravelMode.FLIGHT else SCORING.travel_coach_points

    if estimate.hotel_night_before:
        pts += SCORING.travel_hotel_night_points

    # Door-to-door time scales with distance even within a single mode;
    # capped so geography alone can never dominate a window.
    pts += min(estimate.distance_km / SCORING.travel_distance_reference_km, 1.0) * SCORING.travel_distance_max_points

    # Each hour of timezone shift pushes habitual meal timing further from
    # the players' own clock. Capped at the reference because beyond that
    # it becomes a different problem, not simply a bigger one.
    tz = min(abs(estimate.timezone_delta_hours), SCORING.travel_timezone_reference_hours)
    pts += (tz / SCORING.travel_timezone_reference_hours) * SCORING.travel_timezone_max_points

    return min(pts, SCORING.travel_per_fixture_cap)


def _climate_points(reading: ClimateReading | None) -> float:
    """
    Per-fixture climate burden, deliberately asymmetric.

    Heat carries the most weight: sweat rate rises materially in hot
    conditions and players end up similarly dehydrated despite drinking
    more, so it is a planning problem rather than a self-regulating one.
    Cold carries a smaller but non-zero weight, because voluntary drinking
    falls in the cold while losses under kit do not.
    """
    if reading is None:
        return 0.0

    pts = 0.0

    if reading.temp_delta_c > 0:
        pts += min(reading.temp_delta_c / SCORING.climate_heat_reference_delta_c, 1.0) * SCORING.climate_heat_max_points
    else:
        pts += min(-reading.temp_delta_c / SCORING.climate_cold_reference_delta_c, 1.0) * SCORING.climate_cold_max_points

    if reading.humidity_delta_pct > 0:
        pts += (
            min(reading.humidity_delta_pct / SCORING.climate_humidity_reference_delta_pct, 1.0)
            * SCORING.climate_humidity_max_points
        )

    pts += SCORING.climate_precipitation_points.get(reading.precipitation_risk, 0.0)

    # Beyond the forecast horizon this is a historical average for the
    # venue and month, not a forecast. Still a real signal, materially less
    # certain — so it is discounted here and the window's confidence label
    # is downgraded separately.
    if not reading.is_forecast:
        pts *= SCORING.climate_historical_discount

    return min(pts, SCORING.climate_per_fixture_cap)


def _load_excess(concentration_ratio: float, top_n: int) -> float:
    """
    Normalise concentration so it means the same thing regardless of how
    many players are in the pool. An even spread of minutes would give the
    top N players N/squad_size of the total; this returns how far beyond
    that the actual share sits, on a 0-1 scale.
    """
    squad = max(SCORING.assumed_contributing_squad_size, top_n + 1)
    even_share = top_n / squad
    if concentration_ratio <= even_share:
        return 0.0
    return min((concentration_ratio - even_share) / (1.0 - even_share), 1.0)


def _score_window(
    fixtures,
    frame_start: date,
    frame_end: date,
    travel_by_fixture: dict,
    climate_by_fixture: dict,
    load_excess: float,
    call_ups_in_window: int,
) -> dict[str, float]:
    """Returns the full component breakdown. Nothing is collapsed into a
    single number until the caller asks for it — the breakdown IS the
    explanation."""

    frame_days = (frame_end - frame_start).days + 1

    day_weights = _elevated_day_weights(fixtures, frame_start, frame_end)
    elevated_days = sum(day_weights.values())
    congestion = (elevated_days / frame_days) * SCORING.congestion_max_points

    longest_run = _longest_elevated_run(day_weights)
    no_reset_days = max(0, longest_run - SCORING.natural_elevated_run_days)
    contiguity = min(no_reset_days * SCORING.contiguity_points_per_day, SCORING.contiguity_cap)

    travel = sum(_certainty_weight(f) * _travel_points(travel_by_fixture.get(id(f))) for f in fixtures)
    climate = sum(_certainty_weight(f) * _climate_points(climate_by_fixture.get(id(f))) for f in fixtures)

    load_multiplier = 1.0 + SCORING.load_max_uplift * load_excess
    international = min(
        call_ups_in_window * SCORING.international_points_per_player, SCORING.international_cap
    )

    base = congestion + contiguity + travel + climate
    raw = base * load_multiplier + international

    return {
        "congestion": round(congestion, 3),
        "contiguity": round(contiguity, 3),
        "travel": round(travel, 3),
        "climate": round(climate, 3),
        "international": round(international, 3),
        "load_multiplier": round(load_multiplier, 3),
        # Weighted total is what scores; the calendar count is what a human
        # counts off a wall planner. They differ whenever a provisional
        # fixture is in the window, so both travel — and the reader is only
        # ever shown the calendar count.
        "elevated_days": round(elevated_days, 2),
        "elevated_days_calendar": float(len(day_weights)),
        "frame_days": float(frame_days),
        "longest_elevated_run_days": float(longest_run),
        "no_reset_days": float(no_reset_days),
        "demand_points": round(raw, 3),
    }


def _severity(demand_points: float) -> float:
    return round(min(demand_points / SCORING.reference_demand_points, 1.0), 3)


def _tier_index(severity: float) -> int:
    if severity >= SCORING.tier_peak_threshold:
        return 2
    if severity >= SCORING.tier_elevated_threshold:
        return 1
    return 0


def _tier_ceiling(tier_index: int) -> float:
    """Upper bound of severity for a given tier, used when the provisional
    guardrail has capped a window's tier below its raw score."""
    if tier_index >= 2:
        return 1.0
    if tier_index == 1:
        return round(SCORING.tier_peak_threshold - 0.001, 3)
    return round(SCORING.tier_elevated_threshold - 0.001, 3)


def tier_name(severity: float) -> str:
    """Public helper for the presentation layer."""
    return TIER_NAMES[_tier_index(severity)]


# ─────────────────────────────────────────────────────────────────────
# Findings and named decisions
# ─────────────────────────────────────────────────────────────────────


def _fmt(d: date) -> str:
    return f"{d.day} {d.strftime('%b')}"


def _dominant_driver(breakdown: dict[str, float]) -> str:
    """Which component actually made this window score what it scored.
    Congestion and contiguity are read together — they are the same story
    told two ways. Load is expressed as the points its multiplier added,
    so it can be compared like for like against the additive terms."""
    base = breakdown["congestion"] + breakdown["contiguity"] + breakdown["travel"] + breakdown["climate"]
    load_points = base * (breakdown["load_multiplier"] - 1.0)
    candidates = {
        "congestion": breakdown["congestion"] + breakdown["contiguity"],
        "travel": breakdown["travel"],
        "climate": breakdown["climate"],
        "load": load_points,
        "international": breakdown["international"],
    }
    return max(candidates, key=candidates.get)


def _build_decision(
    driver: str,
    start: date,
    end: date,
    fixtures,
    breakdown: dict[str, float],
    travel_by_fixture: dict,
    climate_by_fixture: dict,
    load_excess: float,
    concentration_ratio: float,
    top_loaded: list[PlayerLoad],
    call_ups_in_window: list[InternationalCallUp],
    confidence: ConfidenceLevel,
    provisional_fixtures: list,
    home_venue_name: str,
    unannounced_breaks: list,
) -> NamedDecision:
    """
    Findings stay declarative and evidenced — the hedge belongs in the
    confidence label, not the tone. Only the decision becomes a question,
    and the question never contains its own answer.
    """
    n = len(fixtures)
    citations = [CITE_UEFA, CITE_CALIBRATION]
    players: list[str] = []

    if driver == "congestion":
        finding = (
            f"{n} matches fall between {_fmt(start)} and {_fmt(end)}. That puts "
            f"{int(breakdown['elevated_days_calendar'])} of {int(breakdown['frame_days'])} days under a "
            f"raised carbohydrate requirement"
        )
        if breakdown["no_reset_days"] > 0:
            finding += (
                f", including a run of {int(breakdown['longest_elevated_run_days'])} consecutive days "
                f"with no lower-intake day to reset against"
            )
            citations.append(CITE_TURNAROUND)
        finding += "."
        question = (
            "Across this stretch, how do you want the refuelling load split between what the club "
            "provides directly and what players are expected to manage themselves?"
        )
        hook = "observation:slow-recovery + timing:congested"

    elif driver == "travel":
        aways = [f for f in fixtures if not f.is_home]
        flights = [
            f for f in aways
            if id(f) in travel_by_fixture and travel_by_fixture[id(f)].mode == TravelMode.FLIGHT
        ]
        furthest = max(
            (travel_by_fixture[id(f)].distance_km for f in aways if id(f) in travel_by_fixture),
            default=0.0,
        )
        finding = (
            f"{len(aways)} of {n} matches in this window are away"
            + (f", {len(flights)} of them beyond coach range" if flights else "")
            + f", the furthest around {furthest:,.0f} km from {home_venue_name}. On the standard "
            f"travel-day-before and hotel-night pattern, that moves several consecutive feeding "
            f"opportunities outside club catering."
        )
        question = (
            "For these trips, what travels with the squad and what are you relying on the hotel to "
            "get right?"
        )
        citations.append(CITE_TRAVEL)
        hook = "observation:travel-dips + timing:away"

    elif driver == "climate":
        readings = [climate_by_fixture[id(f)] for f in fixtures if id(f) in climate_by_fixture]
        hottest = max(readings, key=lambda r: r.temp_delta_c) if readings else None
        if hottest is not None and hottest.temp_delta_c > 0:
            finding = (
                f"Conditions at {hottest.fixture.venue.name} sit around {hottest.temp_delta_c:.0f}°C "
                f"warmer than home"
                + (
                    f", with humidity {hottest.humidity_delta_pct:.0f} points higher"
                    if hottest.humidity_delta_pct > 0
                    else ""
                )
                + ". Sweat rates rise materially in warmer conditions, and players tend to finish "
                "similarly dehydrated despite drinking more."
            )
            citations.extend([CITE_HEAT, CITE_IOC])
            hook = "observation:cramping + timing:heat"
        else:
            coldest = min(readings, key=lambda r: r.temp_delta_c) if readings else None
            delta = abs(coldest.temp_delta_c) if coldest else 0.0
            finding = (
                f"Conditions across this window sit around {delta:.0f}°C colder than home. Voluntary "
                f"drinking falls in the cold while losses under kit do not, so hydration tends to drift "
                f"without anyone noticing."
            )
            citations.append(CITE_IOC)
            hook = "observation:illness + timing:all-season"
        if any(not r.is_forecast for r in readings):
            finding += " These are historical averages for the venue and month, not forecasts."
        question = (
            "Do these fixtures warrant a different hydration protocol from your standard away-day one, "
            "or the same one applied harder?"
        )

    elif driver == "load":
        even = len(top_loaded) / SCORING.assumed_contributing_squad_size if top_loaded else 0.0
        finding = (
            f"Minutes over the last 28 days are concentrated: the {len(top_loaded)} most-used players "
            f"carry {concentration_ratio * 100:.0f}% of squad minutes, against roughly {even * 100:.0f}% "
            f"if minutes were spread evenly. The players inside this window are not all facing the same "
            f"turnaround."
        )
        question = (
            "Does provision through this window stay squad-wide, or shift to something individualised "
            "for the players carrying the most minutes?"
        )
        citations.append(CITE_LOAD)
        hook = "scope:individuals + observation:slow-recovery"

    else:  # international
        nations = sorted({c.nation for c in call_ups_in_window})
        finding = (
            f"{len(call_ups_in_window)} players are on confirmed national duty across this window"
            + (f" ({', '.join(nations)})" if nations else "")
            + ". For that period their feeding, travel and recovery sit outside club control, and they "
            "return with that load already on board."
        )
        question = (
            "What travels with those players while they are away, and what does the first week back "
            "look like for them?"
        )
        citations.append(CITE_INTERNATIONAL)
        hook = "observation:travel-dips + scope:individuals"

    # Name players only where minutes are genuinely unevenly spread, or
    # where they are individually identifiable through a call-up. Naming a
    # player attaches a fact about minutes played to them and nothing else.
    if load_excess >= SCORING.load_notable_excess and top_loaded:
        players = [pl.player.name for pl in top_loaded]
        # Never leave names sitting on a window with nothing explaining why
        # they are there — that is exactly how a fuelling read gets misread
        # as something medical.
        if driver != "load":
            finding += (
                f" The players listed are the {len(top_loaded)} carrying the highest share of "
                f"minutes over the last 28 days, so they meet this window with the shortest "
                f"turnaround behind them."
            )
    if driver == "international" and call_ups_in_window:
        players = [c.player.name for c in call_ups_in_window]

    # Provisional fixtures are named explicitly rather than folded silently
    # into the score — the nutritionist should see what is contingent.
    if provisional_fixtures:
        comps = sorted({f.competition for f in provisional_fixtures})
        count = len(provisional_fixtures)
        subject = f"{count} fixture" if count == 1 else f"{count} fixtures"
        verb = "depends" if count == 1 else "depend"
        aux = "is" if count == 1 else "are"
        finding += (
            f" This includes {subject} in {', '.join(comps)} that {verb} on progression and {aux} "
            f"counted at half weight until confirmed."
        )

    # A confirmed international break can overlap this window with no
    # call-ups yet showing. Say so explicitly — an empty list here means
    # "not known yet," not "nobody's away." Silently reading it as zero
    # would understate a window right when a squad's own workload spikes.
    if unannounced_breaks:
        b = unannounced_breaks[0]
        finding += (
            f" A confirmed international break ({_fmt(b.start)}-{_fmt(b.end)}) also falls in this "
            f"window; which players are called up isn't known yet, so their added load isn't reflected "
            f"in this score."
        )
        citations.append(CITE_BREAK_UNANNOUNCED)

    return NamedDecision(
        window_start=start,
        window_end=end,
        finding=finding,
        decision_question=question,
        players_of_note=players,
        confidence=confidence,
        citations=citations,
        matrix_hook=hook,
    )


# ─────────────────────────────────────────────────────────────────────
# Entry point — signature fixed by the handoff brief
# ─────────────────────────────────────────────────────────────────────


def compute_fuelling_windows(
    congestion_windows: list[tuple[date, date, list]],
    travel_by_fixture: dict,
    climate_by_fixture: dict[object, ClimateReading],
    load_concentration_ratio: float,
    top_loaded_players: list[PlayerLoad],
    international_call_ups: list[InternationalCallUp],
    home_venue_name: str = "home",
    international_breaks: list | None = None,
    as_of: date | None = None,
) -> list[FuellingWindow]:
    """
    Score every candidate window, then return the non-overlapping peaks in
    descending order of demand.

    congestion_windows() is deliberately exhaustive — it emits one window
    per fixture, so a four-match stretch produces four heavily overlapping
    candidates. Handing a nutritionist four near-identical windows would be
    noise, so this takes the highest-scoring window and then only accepts
    later windows that don't overlap one already taken.
    """
    load_excess = _load_excess(load_concentration_ratio, len(top_loaded_players) or 3)
    international_breaks = international_breaks or []
    as_of = as_of or date.today()

    scored: list[tuple] = []

    for frame_start, frame_end, fixtures in congestion_windows:
        if not fixtures:
            continue

        kickoffs = sorted(f.kickoff for f in fixtures)
        # The frame is a fixed-width comparison window so scores stay
        # comparable between windows; the span presented to the reader is
        # the actual range of raised demand, MD-1 of the first match to
        # MD+1 of the last.
        score_start = frame_start - timedelta(days=1)
        span_start, span_end = kickoffs[0] - timedelta(days=1), kickoffs[-1] + timedelta(days=1)

        in_window_call_ups = [
            c
            for c in international_call_ups
            if c.confirmed and c.break_start <= span_end and c.break_end >= span_start
        ]

        full = _score_window(
            fixtures, score_start, frame_end, travel_by_fixture, climate_by_fixture,
            load_excess, len(in_window_call_ups),
        )

        # Floor score: the same window with provisional fixtures removed
        # entirely. This is what the window is worth on confirmed data alone.
        confirmed_only = [f for f in fixtures if f.certainty == FixtureCertainty.CONFIRMED]
        floor = (
            _score_window(
                confirmed_only, score_start, frame_end, travel_by_fixture, climate_by_fixture,
                load_excess, len(in_window_call_ups),
            )
            if confirmed_only
            else None
        )

        scored.append(
            (full["demand_points"], span_start, span_end, full, fixtures, in_window_call_ups, floor)
        )

    # Greedy non-overlapping selection, highest demand first.
    scored.sort(key=lambda row: row[0], reverse=True)
    accepted: list[tuple] = []
    for row in scored:
        span_start, span_end = row[1], row[2]
        if any(span_start <= a[2] and span_end >= a[1] for a in accepted):
            continue
        accepted.append(row)

    windows: list[FuellingWindow] = []

    for demand_points, span_start, span_end, full, fixtures, call_ups, floor in accepted:
        full_severity = _severity(demand_points)
        floor_severity = _severity(floor["demand_points"]) if floor else 0.0

        full_tier = _tier_index(full_severity)
        floor_tier = _tier_index(floor_severity)

        # Structural guardrail: provisional fixtures may lift a window by
        # at most one tier. They can never manufacture a peak window out of
        # a standard one, however many of them stack up.
        displayed_tier = min(full_tier, floor_tier + 1)

        provisional = [f for f in fixtures if f.certainty == FixtureCertainty.PROVISIONAL]
        readings = [climate_by_fixture[id(f)] for f in fixtures if id(f) in climate_by_fixture]
        has_estimated_input = any(not r.is_forecast for r in readings) or any(
            not f.is_home for f in fixtures
        )

        # Confirmed break dates that overlap this window but aren't yet
        # announceable — the case get_call_ups() alone can't distinguish
        # from "nobody's away." If one applies, this window's international
        # component is a known gap, not a verified zero.
        unannounced = [
            b for b in international_breaks
            if b.start <= span_end and b.end >= span_start and not squad_announceable(b.start, as_of)
        ]

        if displayed_tier > floor_tier:
            confidence = ConfidenceLevel.PROVISIONAL
        elif unannounced or has_estimated_input or provisional:
            confidence = ConfidenceLevel.LIKELY
        else:
            confidence = ConfidenceLevel.CONFIRMED

        driver = _dominant_driver(full)
        decision = _build_decision(
            driver=driver,
            start=span_start,
            end=span_end,
            fixtures=fixtures,
            breakdown=full,
            travel_by_fixture=travel_by_fixture,
            climate_by_fixture=climate_by_fixture,
            load_excess=load_excess,
            concentration_ratio=load_concentration_ratio,
            top_loaded=top_loaded_players,
            call_ups_in_window=call_ups,
            confidence=confidence,
            provisional_fixtures=provisional,
            home_venue_name=home_venue_name,
            unannounced_breaks=unannounced,
        )

        factors = dict(full)
        factors["severity_confirmed_only"] = floor_severity
        factors["load_excess"] = round(load_excess, 3)
        factors["match_count"] = float(len(fixtures))
        factors["dominant_driver"] = driver
        factors["tier"] = TIER_NAMES[displayed_tier]

        windows.append(
            FuellingWindow(
                start=span_start,
                end=span_end,
                # Where the provisional guardrail has capped a window's
                # tier, the severity is capped with it, so the number and
                # the label can never disagree.
                severity=min(full_severity, _tier_ceiling(displayed_tier)),
                contributing_factors=factors,
                decision=decision,
            )
        )

    windows.sort(key=lambda w: w.severity, reverse=True)
    return windows
