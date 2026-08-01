"""
Player roster / bio — spec section 6.

Real integration: API-Football /players (team + season), paginated.
NOT LIVE-TESTED — see radar/api_football.py's module docstring for why
(this sandbox can't reach any external API) and scripts/verify_api_football.py
for the mocked-response verification that stands in for it.

Mock roster below uses clearly fictional player identifiers, not real
current Crystal Palace players — this repo should never assert specific
stats about real, named individuals without a verified live source. It
remains the default when API_FOOTBALL_KEY isn't set (e.g. the worked
example, which is deliberately deterministic and offline).
"""

from __future__ import annotations

from datetime import date

from . import api_football
from .models import PlayerBio

MOCK_ROSTER: list[PlayerBio] = [
    PlayerBio(name="[Player A]", age=24, height_cm=178, weight_kg=74, position="Winger",
               source="MOCK DATA — replace with real roster source", as_of=date.today()),
    PlayerBio(name="[Player B]", age=27, height_cm=185, weight_kg=80, position="Midfielder",
               source="MOCK DATA — replace with real roster source", as_of=date.today()),
    PlayerBio(name="[Player C]", age=22, height_cm=190, weight_kg=86, position="Centre-back",
               source="MOCK DATA — replace with real roster source", as_of=date.today()),
    PlayerBio(name="[Player D]", age=29, height_cm=183, weight_kg=78, position="Striker",
               source="MOCK DATA — replace with real roster source", as_of=date.today()),
]


def get_roster() -> list[PlayerBio]:
    """Uses the real API-Football pull when API_FOOTBALL_KEY is set (see
    real_get_roster below); falls back to the mock roster otherwise, so
    the worked example and offline tests keep working unchanged."""
    if api_football.is_configured():
        real = real_get_roster(api_football.CRYSTAL_PALACE_TEAM_ID, season=_current_season())
        if real:
            return real
    return MOCK_ROSTER


def _current_season() -> int:
    """API-Football seasons are keyed by the year a season starts (e.g.
    2026 for 2026/27). English football seasons start in August."""
    today = date.today()
    return today.year if today.month >= 7 else today.year - 1


def _parse_measurement(value: str | None) -> int | None:
    """API-Football gives height/weight as strings like '185 cm' / '80 kg'."""
    if not value:
        return None
    digits = "".join(ch for ch in value if ch.isdigit())
    return int(digits) if digits else None


def real_get_roster(team_id: int, season: int) -> list[PlayerBio] | None:
    """
    Real integration — API-Football /players, paginated (the API returns
    20 players/page). Refreshed at season start and each transfer window,
    per spec section 6. Returns None if the API isn't configured or every
    page fails; returns whatever pages succeeded otherwise, since a
    partial roster is still useful and each entry carries its own
    pull-date source.
    """
    all_players: list[dict] = []
    for page in range(1, 4):  # 3 pages comfortably covers a first-team squad
        raw = api_football.get("players", {"team": team_id, "season": season, "page": page})
        if not raw:
            break
        all_players.extend(raw)
        if len(raw) < 20:
            break

    if not all_players:
        return None

    pulled = date.today()
    roster: list[PlayerBio] = []
    for entry in all_players:
        p = entry.get("player", {}) or {}
        stats = entry.get("statistics") or [{}]
        position = ((stats[0] or {}).get("games") or {}).get("position") or "Unknown"
        name = p.get("name")
        if not name:
            continue
        roster.append(
            PlayerBio(
                name=name,
                age=p.get("age"),
                height_cm=_parse_measurement(p.get("height")),
                weight_kg=_parse_measurement(p.get("weight")),
                position=position,
                source=f"API-Football players endpoint, pulled {pulled.isoformat()}",
                as_of=pulled,
            )
        )
    return roster
