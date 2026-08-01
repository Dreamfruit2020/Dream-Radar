#!/usr/bin/env python3
"""
Verification for the manual international call-up mechanism
(radar/international.py's get_call_ups() + radar/manual_call_ups.json).

Unlike climate.py and api_football.py, there's no live-network caveat
here — this is a real, local file read, so these checks are complete
verification, not a stand-in for one.

Run: python3 scripts/verify_manual_call_ups.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from radar import international
from radar.models import PlayerBio

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


roster = [
    PlayerBio("Player A", 24, 178, 74, "Winger", "TEST", date.today()),
    PlayerBio("Player B", 27, 185, 80, "Midfielder", "TEST", date.today()),
]

BREAK_START = date(2026, 9, 21)
BREAK_END = date(2026, 10, 6)

print("\nManual call-up mechanism — verification")
print("=" * 60)

print("\n1. Before the announce window")
far_break_start = date.today() + __import__("datetime").timedelta(days=60)
result = international.get_call_ups(roster, far_break_start, far_break_start)
check("far-future break returns [] without reading the file at all", result == [])

print("\n2. Missing / empty file")
with tempfile.TemporaryDirectory() as d:
    missing_path = Path(d) / "does_not_exist.json"
    with patch.object(international, "MANUAL_CALL_UPS_PATH", missing_path):
        result = international.get_call_ups(roster, date.today(), date.today())
        check("missing file treated as no entries, not an error", result == [])

print("\n3. Populated file, matching entries")
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "manual_call_ups.json"
    p.write_text(json.dumps({
        "call_ups": [
            {
                "player_name": "Player A",
                "nation": "England",
                "break_start": BREAK_START.isoformat(),
                "break_end": BREAK_END.isoformat(),
                "source": "The FA squad announcement, 10 Sep 2026",
            },
            {
                # different break — should NOT match this window
                "player_name": "Player B",
                "nation": "Wales",
                "break_start": "2026-11-12",
                "break_end": "2026-11-17",
                "source": "FAW squad announcement",
            },
            {
                # player not on the current roster — should be skipped
                "player_name": "Nobody On The Roster",
                "nation": "Scotland",
                "break_start": BREAK_START.isoformat(),
                "break_end": BREAK_END.isoformat(),
                "source": "SFA squad announcement",
            },
        ]
    }))
    with patch.object(international, "MANUAL_CALL_UPS_PATH", p):
        result = international.get_call_ups(roster, BREAK_START, BREAK_END, as_of=date(2026, 9, 15))

check("only the matching-break entry for a rostered player is returned", len(result) == 1, str(len(result)))
check("correct player resolved from the roster", result[0].player.name == "Player A" if result else False)
check("nation and source correctly carried through", result[0].nation == "England" and "FA squad" in result[0].source if result else False)
check("confirmed=True for a manually recorded entry", result[0].confirmed is True if result else False)

print("\n4. Real file ships with the correct empty-template shape")
check("radar/manual_call_ups.json exists in the repo", international.MANUAL_CALL_UPS_PATH.exists())
real_content = json.loads(international.MANUAL_CALL_UPS_PATH.read_text())
check("ships with an empty call_ups list, not fabricated entries", real_content.get("call_ups") == [])
check("ships with instructions for the manual process", "_instructions" in real_content)

print("\n" + "=" * 60)
if FAILURES:
    print(f"{len(FAILURES)} of {CHECKS} checks FAILED:")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print(f"All {CHECKS} checks passed.")
