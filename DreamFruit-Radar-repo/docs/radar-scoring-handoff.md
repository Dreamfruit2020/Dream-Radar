# Handoff brief: Fuelling Risk composite scoring formula

*For an Opus 5 session. Self-contained — you shouldn't need to re-read the full spec to start, though it's at `docs/dream-radar-spec.md` if you want the wider context.*

---

## The one thing this session needs to produce

A documented, defensible formula that takes a club's upcoming fixtures plus five supporting inputs, and outputs a ranked list of **Fuelling Risk Windows** — specific date ranges where fuelling and hydration demand is highest — each with a numeric or tiered severity, and named players carrying the heaviest load into it.

This isn't a coding task first — it's a judgment task. The output needs to be something DreamFruit could defend if a club's own performance staff asked "how did you calculate that." Write the reasoning, not just the arithmetic.

---

## Inputs available (all already modelled in `radar/models.py`)

1. **Fixture congestion** — matches per rolling window (e.g., matches in any 11-day span), tagged by certainty tier: `confirmed`, `provisional` (cup round scheduled but qualification unconfirmed), or excluded entirely if `unknown`.
2. **Travel burden** — per fixture, computed from `radar/travel.py`: distance, mode (coach/flight, config-driven 2-hour threshold), timezone delta, and whether the away-day-before + hotel-night pattern applies. Already fully implemented — treat as ground truth input, not something this session needs to redesign.
3. **Climate delta** — temperature/humidity difference between the venue and the club's home conditions, plus precipitation risk. Stubbed for now (`radar/climate.py`); assume it will arrive as a numeric delta per fixture.
4. **Match load concentration** — recent minutes played per player, over a rolling window (e.g., last 4–6 weeks). The interesting signal isn't total squad minutes, it's *concentration* — how unevenly load is spread across the squad. Stubbed for now (`radar/load.py`).
5. **International call-up load** — for players away on confirmed national duty around a break, added travel/reduced club-controlled recovery time on top of their existing club load. Only populated once squads are announced (1–2 weeks out); treat as `unknown` before that. Stubbed for now (`radar/international.py`).

## What "good" looks like

- **A club nutritionist should be able to look at two different weeks and understand *why* one scored higher than the other**, not just that it did. The formula needs to be explainable in one or two sentences per window, not a black box.
- **Confirmed and provisional fixtures shouldn't be weighted the same.** A provisional cup round shouldn't be able to push a window to the top of the list on its own — see the fixture-uncertainty tiering in the spec (section 6). Suggest treating provisional fixtures as a lighter-weight addition to a window's severity rather than a full contributor, but the exact mechanism (discount factor, separate "potential" tier, etc.) is yours to design.
- **The output needs a specific "named decision," not just a score.** Per spec section 5, every Fuelling Risk Window needs to name the actual decision at stake for the nutritionist — not the answer, just what genuinely needs deciding (e.g., "how do you allocate limited hydration-protocol attention across four away trips in eleven days"). Decide whether this is templated off which inputs dominate the score, or something this session designs more directly.
- **Every component of the score needs a citation or a stated basis**, even if that basis is "industry-standard assumption, see travel heuristic config" rather than a paper. Nothing in the output should be an unexplained number.

## Hard constraints (non-negotiable, from the spec's guardrails)

- **No injury-risk score.** The formula outputs a *fuelling demand* reading. It must not be presentable as, or easily mistaken for, an injury-risk prediction for a named player. If load concentration research gets cited to justify weighting, the citation supports a fuelling claim, not a medical one.
- **Confidence, not certainty.** Whatever the output format is, it needs a built-in way to express "this is a strong signal" vs. "this is provisional/early" — not just a single clean number that implies more precision than the inputs actually support.
- **Findings stay declarative; only the decision framing becomes a question.** The severity/ranking output itself is a plain, evidenced fact ("this is your highest-demand window, here's why"). Don't build hedging into the finding itself — the hedge belongs in the confidence label, not the tone.

## Deliverable format

1. The actual formula/logic, written out with reasoning for each weighting choice — why congestion counts for what it counts for relative to travel, climate, load concentration, international duty.
2. A worked example: take a plausible multi-week Crystal Palace fixture stretch (Premier League + Europa League league phase + a provisional cup round) and show the actual output — which week wins, why, what the named decision is, what the citations are.
3. Ideally, this as Python that can drop into `radar/fuelling_risk.py` in place of the current stub — the interface is already defined there (see `compute_fuelling_windows()`), so the shape of the input/output is fixed; what's missing is what happens inside it.

## What NOT to do

- Don't redesign the travel heuristic — it's already spec-confirmed and implemented (`radar/travel.py`, `radar/config.py`). If something about it seems off for this purpose, flag it rather than silently working around it.
- Don't expand scope to multiple insights. This is one formula for one insight (Fuelling Risk Windows). The "situational awareness" / season-arc framing in the spec is a presentation layer on top of this, not something the formula itself needs to model.
