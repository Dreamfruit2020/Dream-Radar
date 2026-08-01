"""
Match load (minutes played) + concentration — spec section 6.

Real integration: API-Football per-fixture lineup data
(/fixtures/players), summed across a club's recent matches. NOT
LIVE-TESTED — see radar/api_football.py's module docstring.

Deliberately NOT a single call to a season-totals endpoint: the spec
asks for a rolling recent window ("last 4-6 weeks," config.LOAD_LOOKBACK_DAYS),
which is a different number from cumulative season minutes — a player
back from injury three weeks ago should read as lightly loaded even in
May. That means one API call per recent fixture rather than one call
total; still comfortably inside API-Football's free tier for a single
club refreshed periodically.

`load_concentration()` is the one piece of real logic that was already
here before this integration: how unevenly minutes are spread across the
squad, which is the actual signal fuelling_risk.py needs (per the
handoff brief) — not total squad minutes.
"""

from __future__ import annotations

import random
from datetime import date

from . import api_football
from .models import PlayerBio, PlayerLoad
from .player_bio import get_roster


def get_recent_load(roster: list[PlayerBio] | None = None, recent_fixture_ids: list[int] | None = None) -> list[PlayerLoad]:
    """Uses the real API-Football pull when API_FOOTBALL_KEY is set AND
    recent fixture ids are supplied (build.py is responsible for finding
    those — see real_get_recent_load below); falls back to randomised
    mock data otherwise, so the worked example and offline tests keep
    working unchanged."""
    roster = roster or get_roster()
    if api_football.is_configured() and recent_fixture_ids:
        real = real_get_recent_load(api_football.CRYSTAL_PALACE_TEAM_ID, roster, recent_fixture_ids)
        if real:
            return real
    return [
        PlayerLoad(
            player=p,
            minutes_last_28_days=random.randint(90, 450),
            matches_last_28_days=random.randint(1, 5),
            source="MOCK DATA — replace with real match-load stats source",
        )
        for p in roster
    ]


def real_get_recent_load(
    team_id: int, roster: list[PlayerBio], recent_fixture_ids: list[int]
) -> list[PlayerLoad] | None:
    """
    Real integration. Sums minutes played per player across the supplied
    fixture ids via API-Football's per-fixture lineup endpoint
    (/fixtures/players) — the caller (build.py) is expected to have
    already selected "recent" as the club's own fixtures within
    config.LOAD_LOOKBACK_DAYS, using real_fixtures()'s output.

    Returns None if the API isn't configured or every fixture call
    failed. Returns whatever could be aggregated if only some fixtures
    succeeded — a partial recent-load picture is still more honest than
    discarding it, and the source string says exactly how partial it is.

    Players who appear in a lineup but aren't in `roster` are skipped
    rather than given a fabricated bio — this can happen for a debut or
    a youth player not yet in the season squad pull.
    """
    if not api_football.is_configured():
        return None

    minutes_by_name: dict[str, int] = {}
    matches_by_name: dict[str, int] = {}
    succeeded: list[int] = []

    for fixture_id in recent_fixture_ids:
        raw = api_football.get("fixtures/players", {"fixture": fixture_id})
        if raw is None:
            continue
        succeeded.append(fixture_id)
        for team_entry in raw:
            if (team_entry.get("team") or {}).get("id") != team_id:
                continue
            for p in team_entry.get("players", []):
                name = (p.get("player") or {}).get("name")
                stats = (p.get("statistics") or [{}])[0]
                minutes = ((stats.get("games") or {}).get("minutes")) or 0
                if not name or minutes <= 0:
                    continue
                minutes_by_name[name] = minutes_by_name.get(name, 0) + minutes
                matches_by_name[name] = matches_by_name.get(name, 0) + 1

    if not succeeded:
        return None

    roster_by_name = {p.name: p for p in roster}
    source = (
        f"API-Football fixture lineups — {len(succeeded)}/{len(recent_fixture_ids)} recent "
        f"fixtures pulled, {date.today().isoformat()}"
    )

    loads: list[PlayerLoad] = []
    for name, minutes in minutes_by_name.items():
        bio = roster_by_name.get(name)
        if bio is None:
            continue
        loads.append(
            PlayerLoad(player=bio, minutes_last_28_days=minutes, matches_last_28_days=matches_by_name[name], source=source)
        )
    return loads


def load_concentration(loads: list[PlayerLoad], top_n: int = 3) -> tuple[float, list[PlayerLoad]]:
    """
    Real logic. Returns (concentration_ratio, top_n_loaded_players).

    concentration_ratio = minutes carried by the top_n most-used players
    ÷ total squad minutes. High ratio = load stacked on a few players,
    which is the fuelling-relevant signal — not the raw minutes total.
    """
    if not loads:
        return 0.0, []

    ranked = sorted(loads, key=lambda l: l.minutes_last_28_days, reverse=True)
    top = ranked[:top_n]
    total = sum(l.minutes_last_28_days for l in loads)
    top_total = sum(l.minutes_last_28_days for l in top)

    ratio = (top_total / total) if total > 0 else 0.0
    return round(ratio, 3), top
