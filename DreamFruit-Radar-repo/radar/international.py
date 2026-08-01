"""
International call-ups — spec section 6.

Break DATES are real (FIFA international match calendar). Which PLAYERS
get called up is a MANUAL process (Connor's decision, 1 Aug 2026) rather
than an automated source — no API cleanly covers "which of this one
club's rostered players got called up by any of several national
federations." Someone checks federation announcements roughly 1-2 weeks
before each date in INTERNATIONAL_BREAKS and records it in
radar/manual_call_ups.json; get_call_ups() below just reads that file.
Before the announce window, it correctly reports "unknown" rather than
reading the file at all — squads genuinely aren't known yet, so there's
nothing to check.

Known interface limitation, fixed earlier (flagged in
docs/radar-scoring-design.md section 15): get_call_ups() alone can't tell
a scorer whether "no call-ups in this window" means the squad genuinely
has no one away, or nobody's checked yet. breaks_overlapping() closes
that gap by giving fuelling_risk.py the confirmed break dates directly,
independent of who's picked, so it can add the right caveat instead of
silently reading zero. That fix covers "not yet announceable." Once a
break IS inside the announce window, an empty manual_call_ups.json entry
is read as "checked, nobody away" — the instructions field in that file
says so explicitly, and it's on the manual process (check before each
break) to keep that honest, not the code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .config import INTERNATIONAL_SQUAD_ANNOUNCE_LEAD_DAYS
from .models import InternationalCallUp, PlayerBio

MANUAL_CALL_UPS_PATH = Path(__file__).resolve().parent / "manual_call_ups.json"


@dataclass
class InternationalBreak:
    start: date
    end: date
    source: str


# Real dates — FIFA international match calendar, confirmed 2026-27 season
# structure (from 2026, the September and October windows are combined
# into one extended break). See docs/radar-scoring-design.md sources.
# WHO gets called up from any given club's roster is still unknown this
# far out — these are the break windows only, not a squad list.
INTERNATIONAL_BREAKS: list[InternationalBreak] = [
    InternationalBreak(
        date(2026, 9, 21), date(2026, 10, 6),
        "FIFA international match calendar: September/October windows combined into one "
        "16-day break from 2026 onward.",
    ),
    InternationalBreak(
        date(2026, 11, 12), date(2026, 11, 17),
        "FIFA international match calendar: November window, Matchday 5 (12-14 Nov) and "
        "Matchday 6 (15-17 Nov).",
    ),
    # March break: confirmed by FIFA to remain a 9-day window, but exact
    # 2027 dates were not available at spec time — deliberately omitted
    # rather than guessed. Add once published.
]


def breaks_overlapping(start: date, end: date) -> list[InternationalBreak]:
    """Real logic — which confirmed international breaks fall inside a
    given date range, independent of which players get picked."""
    return [b for b in INTERNATIONAL_BREAKS if b.start <= end and b.end >= start]


def squad_announceable(break_start: date, as_of: date | None = None) -> bool:
    """Real logic: can call-ups plausibly be known yet for a given break?"""
    as_of = as_of or date.today()
    return (break_start - as_of).days <= INTERNATIONAL_SQUAD_ANNOUNCE_LEAD_DAYS


def _load_manual_call_ups() -> list[dict]:
    """Real logic — reads radar/manual_call_ups.json. Missing or
    unreadable file is treated as no entries recorded yet, not an error;
    the file ships with an empty template (see the repo) so this is the
    expected state until someone starts the manual process."""
    try:
        raw = json.loads(MANUAL_CALL_UPS_PATH.read_text())
        return raw.get("call_ups", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_call_ups(
    roster: list[PlayerBio], break_start: date, break_end: date, as_of: date | None = None
) -> list[InternationalCallUp]:
    """
    Real integration — manual process. Before the announce window this
    correctly returns [] without even reading the file (squads genuinely
    aren't known yet). Once inside the window, reads
    radar/manual_call_ups.json for entries matching this exact break and
    resolves each player_name against the roster by name — an entry for
    a player not currently on the roster is skipped rather than
    fabricating a bio for them. `as_of` is injectable for deterministic
    testing (mirrors the pattern used throughout radar/climate.py).
    """
    if not squad_announceable(break_start, as_of):
        return []  # correct behaviour, not a shortcut — squads genuinely aren't known yet

    roster_by_name = {p.name: p for p in roster}
    call_ups: list[InternationalCallUp] = []
    for entry in _load_manual_call_ups():
        if entry.get("break_start") != break_start.isoformat() or entry.get("break_end") != break_end.isoformat():
            continue
        player = roster_by_name.get(entry.get("player_name"))
        if player is None:
            continue  # recorded call-up for a player not on the current roster pull — skip, don't guess
        call_ups.append(
            InternationalCallUp(
                player=player,
                nation=entry.get("nation", "[nation not recorded]"),
                confirmed=True,
                break_start=break_start,
                break_end=break_end,
                source=entry.get("source", "Manually recorded — no source noted"),
            )
        )
    return call_ups
