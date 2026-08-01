# Dream Radar — guardrails & voice review

*Review pass against `docs/dream-radar-spec.md` sections 3 (positioning & voice) and 9 (guardrails), run across everything Radar-facing that's been built so far: `radar/fuelling_risk.py`, `scripts/make_radar_briefing.py`, `scripts/make_radar_teaser.py`, `scripts/make_radar_shareable.py`.*

## Automated guardrails

`scripts/verify_scoring.py` — 34 of 34 passing, including a term scan across every generated finding and decision question for injury/medical/diagnostic/predictive language.

Extended that scan to the three delivery-format scripts' own static copy (not just the dynamic formula output) — clean:

```
grep -inE "injur|diagnos|predict|at risk|danger|unsafe" scripts/make_radar_briefing.py \
  scripts/make_radar_teaser.py scripts/make_radar_shareable.py
```

No hits.

## Positioning checklist (spec section 3)

| Principle | Status |
|---|---|
| Intelligence partner, not advisor — never instructs, only informs | **Pass.** Decisions are always framed as questions (enforced by `verify_scoring.py`); none of the static copy in the three formats tells the nutritionist what to do. |
| Informed, not replaced | **Pass.** Nothing reads as grading the practitioner — no "you missed this" framing anywhere. |
| Findings declarative and evidenced; actions as questions | **Pass.** Enforced programmatically at the formula level. |
| Situational awareness is the umbrella; Fuelling Risk Windows the headline finding inside it | **Pass.** Both the PDF and the shareable page carry the "FUELLING RISK · SITUATIONAL AWARENESS" eyebrow verbatim from the spec's own framing. |
| The shareable artifact makes the nutritionist look prepared, not DreamFruit look clever | **Pass — resolved below.** |
| Risk and opportunity are the same window (spec section 5) | **Was missing, now fixed.** |
| Season arc — baseline habits, plus the spikes (spec section 5) | **Was missing, now fixed.** |

## Two real gaps found, and fixed

The spec is explicit that both of these should be "built into the copy directly" / "the briefing should say so explicitly" — neither was present anywhere across the three delivery formats before this review. Both are now added as a short paragraph on the PDF cover (page 1, below the windows list) and on the shareable page (below the windows list, above the footer):

> "Most clubs don't run a fuelling protocol tuned to their own specific pattern of congestion, travel and international duty. The ones that do gain a real edge exactly when it matters most. And these spikes sit on a season-long baseline: good habits early, protected availability through winter, a squad that finishes strong rather than fading."

Deliberately added as **presentation-layer copy**, not inside `radar/fuelling_risk.py` — the handoff brief that scoped the formula explicitly ruled this framing out of the formula's own responsibility ("a presentation layer on top of this, not something the formula itself needs to model"), so it belongs in the deliverable generators, not the scoring logic. Kept to the honesty guardrail already in the spec: "most clubs" is a fair industry-level observation, not a claim about a specific rival's specific weakness.

The teaser deliberately does **not** carry this — it's built to be one number, one sentence, one door left open (spec section 7, format 1), and season-arc framing would work against that intentional minimalism.

## Two smaller items — decided by Connor, 1 Aug 2026

1. **"Prepared with the nutritionist, not DreamFruit's report forwarded on their behalf"** (spec section 3, last bullet). **Decided and built.** The framing belongs in the artifact itself, not a covering email. `make_radar_briefing.py` and `make_radar_shareable.py` both now carry a styled "Prepared with [Name] · Crystal Palace FC" credit line, sourced from a new third CLI arg (surfaced as a form field in `ops/app.py`), between the headline and lede. Falls back to a visible `[Nutritionist Name]` placeholder rather than silently omitting the credit if no name is supplied. Deliberately not added to the teaser — that's the live, pre-relationship step-4 opener, before there's a relationship to credit.
2. **The cited fuelling→illness/fatigue connection** (spec sections 2, 5, 9: Radar *can* make this link, always with a citation). **Explicitly deferred, not built** — Connor's call: "leave it out until i see what it looks like." Nothing in the current output is wrong or unsourced; none of the five driver branches in `_build_decision()` currently exercises this specific connection, and it stays that way until this gets a fresh look alongside a rendered example.

## One capability gap in this sandbox, not in the product

The two HTML deliverables (`Dream-Radar-Teaser.html`, `Dream-Radar-Shareable.html`) could not be screenshot-verified the way the PDFs were — no working headless browser in this sandbox (Playwright installs but is missing system libraries, and there's no sudo to fix it here). Verified structurally instead: balanced HTML tags, no unformatted template placeholders, every dynamic value populated correctly. Worth an actual visual check in a browser before these go anywhere near a club.
