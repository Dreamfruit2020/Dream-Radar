# Dream Radar — data-build scaffold

Backend for `docs/dream-radar-spec.md`. Pilot club: Crystal Palace FC.

## Status

| Module | Status |
|---|---|
| `config.py` | Real — editable travel heuristic thresholds |
| `travel.py` | Real — distance/mode/timezone/hotel computation |
| `api_football.py` | **Real** — shared client for API-Football (fixtures, load, roster). NOT live-tested — see caveat below. |
| `fixtures.py` | **Real** (`real_fixtures()`) when `API_FOOTBALL_KEY` is set, else falls back to the illustrative `example_fixtures()`. Known gap: venue coordinates aren't in API-Football's fixture data — see `VENUE_COORDINATES` in the module. |
| `climate.py` | **Real** — Open-Meteo integration (free, keyless). NOT live-tested — this sandbox can't reach external APIs at all; verified against mocked HTTP responses only (`scripts/verify_climate.py`). |
| `load.py` | **Real** (`real_get_recent_load()`) when configured, else falls back to randomised mock minutes. Sums minutes per player across recent fixture lineups — a rolling window, not a season total. |
| `player_bio.py` | **Real** (`real_get_roster()`) when configured, else falls back to the mock roster. |
| `international.py` | Real announce-window logic; call-ups are a **manual process** (Connor's decision) rather than an automated source — see `manual_call_ups.json` below. |
| `fuelling_risk.py` | **Real** — composite scoring formula, reasoning in `docs/radar-scoring-design.md` |
| `build.py` | Orchestrates all of the above. `build_for_club_with_source()` additionally reports whether fixtures came from the real API-Football pull or the illustrative fallback — see below. |

**The formula is real, and every data source now has a real implementation behind it** — fixtures/load/roster via API-Football, climate via Open-Meteo, international call-ups via a manual entry file. What's still missing is proof any of it works against a live network — see below.

**The ops tool's "Generate materials" button is now wired to this, not a fixed sample.** `scripts/worked_example.get_windows()` is the shared entry point every deliverable generator (`make_radar_briefing.py`, `make_radar_teaser.py`, `make_radar_shareable.py`) calls: it tries `build_for_club_with_source()` first, and falls back to the curated illustrative demo only if `API_FOOTBALL_KEY` isn't set, the real pull comes back empty, or anything in the real path throws. Every generated file is labelled honestly either way — "LIVE DATA — VERIFY BEFORE SHARING" or "SAMPLE OUTPUT — ILLUSTRATIVE DATA" — never silently one when it's actually the other. `ops/app.py` is deployed on Render (not Netlify — their Functions platform is JS/TS-first, see `ops/app.py`'s docstring for that call), so this is also the first environment with real outbound internet this project has ever run in.

## Run it

```bash
pip install -r requirements.txt     # requests, flask
export API_FOOTBALL_KEY="..."       # optional — omit to run on mock/illustrative data
python3 -m radar.build              # full pipeline
python3 scripts/worked_example.py   # worked Crystal Palace example, deterministic, always offline
python3 scripts/verify_scoring.py       # 34 checks — the formula
python3 scripts/verify_climate.py       # 23 checks — Open-Meteo integration (mocked HTTP)
python3 scripts/verify_api_football.py  # 28 checks — API-Football integration (mocked HTTP)
python3 scripts/verify_real_data_wiring.py  # 8 checks — real-vs-fallback branch in get_windows() (mocked HTTP)
```

**Note on network — read before trusting any of this in front of a club.** This repo was developed in a sandbox whose outbound network is allowlisted and blocks arbitrary external APIs entirely (confirmed via a blocked curl and a timed-out fetch to both Open-Meteo and api-football.com). Every check above passes against mocked HTTP responses shaped like each API's documented contract — that proves the parsing/fallback/failure-handling logic is correct, not that a live call actually works. The first real signal will be running any of the above from a normal internet connection: real-looking output (temperatures, real opponent names, real minutes) means it's working; seeing `UNAVAILABLE_SOURCE` text or a silent fallback to mock data means something's still wrong. Two specific unverified assumptions to check first: `CRYSTAL_PALACE_TEAM_ID = 52` in `api_football.py` (a commonly reused example id in public API-Football sample code, not something this project has confirmed against the real API), and the exact JSON shape assumed throughout — written from API-Football's public docs, not a real response.

## Next steps

1. ~~Get real network access~~ — done: `ops/app.py` is live on Render with a real `API_FOOTBALL_KEY`, the first environment this project has had real internet in. Click "Generate materials" and check the label on the output — "LIVE DATA" confirms the real pull actually worked end to end; "SAMPLE OUTPUT" means it fell back, worth checking Render's logs for why.
2. Confirm `CRYSTAL_PALACE_TEAM_ID` via a real `GET /teams?name=Crystal Palace` call — the first live run either confirms this or exposes it as wrong.
3. Expand `VENUE_COORDINATES` in `fixtures.py` as real away fixtures surface grounds not yet in the lookup.
4. Settle the remaining flagged calibration in `docs/radar-scoring-design.md` section 15 (`assumed_contributing_squad_size`) now that a real roster source exists.
5. Connect `NamedDecision.matrix_hook` into the Performance Matrix intake (spec section 5).
