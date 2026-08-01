# Dream Radar — Fuelling Risk scoring formula

*Design output for the session briefed in `docs/radar-scoring-handoff.md`. Implemented in `radar/fuelling_risk.py`, weights in `radar/config.py`, verified by `scripts/verify_scoring.py`, demonstrated by `scripts/worked_example.py`.*

This document exists so that when a club's head of performance asks "how did you calculate that", there is a real answer. If a number in `config.py` changes, the reasoning here changes with it.

---

## 1. What the formula produces

A ranked list of **Fuelling Risk Windows** — non-overlapping date ranges where fuelling and hydration demand is highest — each carrying:

- a severity (0–1) and a tier (`standard` / `elevated` / `peak`)
- the full component breakdown that produced it
- a confidence label (`confirmed` / `likely` / `provisional`)
- a declarative finding, the named decision it bears on, and citations
- named players, only where minutes are genuinely unevenly spread

---

## 2. The unit: Fuelling Demand Points

Everything accumulates in **Fuelling Demand Points (FDP)**. FDP is not a measured physiological quantity and the document never pretends otherwise. It is a transparent ledger: each contribution is named, weighted, and traceable to either a published source or an explicitly declared DreamFruit calibration.

This matters more than picking "correct" weights. A nutritionist who disagrees with a weight can see exactly which one to argue with — which is a far better conversation than defending a black box.

---

## 3. Congestion — the primary driver

**The move that makes this defensible: don't count matches, count elevated-demand days.**

A naive "matches per 11 days" score is easy to build and easy to dismiss — it tells a nutritionist something they already know off the wall planner. The UEFA Expert Group Statement on Nutrition in Elite Football (*British Journal of Sports Medicine*, 2021) gives a better primitive: match day, MD-1 and MD+1 all carry a raised carbohydrate target of roughly **6–8 g/kg body mass/day**, against roughly **3–6 g/kg** on other days.

So each fixture claims a three-day block `{MD-1, MD, MD+1}`. Union those blocks across the window and you get the number of days actually under raised demand — which is a *nutrition* statement, not a fixtures statement, and it's the reason the output belongs to DreamFruit rather than to any fixture-list website.

```
congestion = (elevated_days / frame_days) × 4.0
```

**Why max, not sum, on overlapping days.** Two matches cannot make a single day more than elevated. Where fixture blocks overlap, the day takes the higher of the two weights. What back-to-back matches genuinely do is remove the low days in between — and that is scored separately, next.

**Why 4.0.** Congestion should be able to out-score everything else combined, because it is the thing that actually creates the problem; travel and climate change its shape. 4.0 against travel's realistic 1.5–2.0 and climate's 0.5–1.0 sets that ordering. Calibration, declared as such.

**Frame vs. span.** Scoring uses a fixed 13-day frame (the spec's 11-day rolling window, extended by one day either side to capture the first MD-1 and the last MD+1) so windows stay comparable to each other. The window *presented* to the reader is the actual demand span: MD-1 of the first match to MD+1 of the last.

---

## 4. Contiguity — the periodisation collapse

An isolated match produces a natural 3-day elevated run. A run longer than that means matches close enough together that the lower-carbohydrate days in between have disappeared — the periodisation UEFA describes has nothing left to periodise against.

```
no_reset_days = max(0, longest_elevated_run − 3)
contiguity    = min(no_reset_days × 0.40, 2.0)
```

Supported by *Monitoring of Post-match Fatigue in Professional Soccer* (**Sports Medicine**, 2018): during congested schedules, the 3–4 day turnaround between matches may be insufficient to fully restore players.

Capped at 2.0 so a freak run cannot swamp everything else.

**Why this earns its place:** it separates two windows a match count would score identically. Three matches on days 0/2/4 and three on days 0/5/10 are the same number of matches and a very different fuelling problem. The formula sees the difference.

---

## 5. Travel

Read entirely off the spec-confirmed heuristic in `radar/config.py` — this session did not redesign it, per the brief. It is translated into demand on one argument: **how many consecutive feeding opportunities move outside club catering.**

| Component | Points | Basis |
|---|---|---|
| Coach away | 0.15 | One meal cycle moves to club-provided coach catering — displaced, still controlled |
| Flight away | 0.40 | Airport and cabin time replaces a meal window entirely; less control, less appetite |
| Hotel night before | +0.15 | Config-driven; breakfast and MD-1 dinner move to a third-party kitchen |
| Distance | up to +0.25 (ref 1500 km) | Door-to-door time scales with distance within a mode; capped so geography cannot dominate |
| Timezone shift | up to +0.30 (ref 3 h) | Each hour pushes habitual meal timing further from the players' own clock |
| **Per-fixture cap** | **1.00** | One away trip should never out-weigh the congestion of the window it sits in |

Home fixtures score zero. The club controls every meal.

All of it carries `TravelEstimate.basis` downstream: estimated from standard club practice, never presented as this club's actual logistics.

---

## 6. Climate — deliberately asymmetric

| Component | Points | Basis |
|---|---|---|
| Warmer than home | up to 0.50 (ref +10 °C) | Sweat rates rise materially in hot versus temperate match conditions; players drink more but finish similarly dehydrated (Gatorade Sports Science Institute, *Hydration Science and Strategies in Football*) |
| Humidity higher | up to 0.30 (ref +25 pts) | Reduced evaporative cooling raises sweat rate for the same work |
| Colder than home | up to 0.20 (ref −10 °C) | Voluntary drinking falls in the cold while losses under kit do not — a quieter problem, not an absent one |
| Precipitation risk | 0.05 / 0.10 | Cold-wet raises energy cost and further suppresses voluntary drinking |
| **Per-fixture cap** | **1.00** | |

Heat outweighs cold roughly 2.5:1 because heat is a planning problem that does not self-correct — the research shows players drinking more and still arriving at a similar deficit. IOC Consensus Statement on Sports Nutrition (2010) anchors the target: keep dehydration under roughly 2% of body mass, and replace salts as well as water in recovery.

**Honesty note.** The dramatic sweat-rate figures come from genuinely hot conditions. A November away day in the north-east is not that. The climate term will be a small modifier across most of a domestic English season and will only speak up for continental travel south, pre-season tours, and early/late-season heat. That is the correct behaviour, not a weakness — but it means the climate line should never be over-sold in the room.

**Beyond the forecast horizon** (`FORECAST_RELIABLE_HORIZON_DAYS = 10`), `climate.py` falls back to historical averages for the venue and month. Those contributions are halved, *and* the finding says so in plain words when climate is the driver.

---

## 7. Load concentration — a multiplier, never a creator

The signal is not total squad minutes. It is how unevenly minutes are spread. A squad does not experience congestion uniformly: a regular starter and an unused substitute face different refuelling problems in the same week.

Raw concentration ratios are meaningless without knowing the pool size, so the ratio is normalised against what an even spread would look like:

```
even_share = top_n / assumed_contributing_squad_size     # 3 / 16 = 0.1875
excess     = clamp((ratio − even_share) / (1 − even_share), 0, 1)
multiplier = 1 + 0.30 × excess                            # 1.00 … 1.30
```

Applied to the sum of congestion, contiguity, travel and climate. **Capped at +30% by design** — load concentration should sharpen a window that already exists, never conjure one. A perfectly even squad in a quiet fortnight must not be scored as a hard fortnight because of a multiplier.

This is a nutrition-planning claim about who has the shortest turnaround. It is not, and must never be presented as, a statement about anyone's physical condition.

---

## 8. International duty

```
international = min(0.5 × confirmed_call_ups, 2.0)
```

Additive, not multiplicative, because it applies to specific named individuals rather than to the whole window. For the duration of a break, a called-up player's feeding, travel and recovery sit outside club control entirely, and they return with that load already on board.

**Only confirmed call-ups count.** Squads are published roughly 1–2 weeks out (`INTERNATIONAL_SQUAD_ANNOUNCE_LEAD_DAYS = 14`); before that, `international.py` correctly returns nothing rather than guessing who gets picked. Capped at 2.0 because beyond about four players it has become a squad-wide condition, which load concentration is already reading.

---

## 9. Confirmed vs. provisional — the two-score mechanism

The brief asked for a mechanism, not just a discount factor. This is it.

**Every window is scored twice:**

1. **Full score** — provisional fixtures included at weight **0.5**. A cup round whose qualification is unconfirmed is, on a neutral read, a coin flip.
2. **Floor score** — provisional fixtures removed entirely. What the window is worth on confirmed data alone.

Then a structural rule:

```
displayed_tier = min(full_tier, floor_tier + 1)
```

**A provisional fixture can lift a window by at most one tier. It can never manufacture a peak window out of a standard one, however many of them stack up.** Verified: an entirely provisional stretch — four cup fixtures, long-haul travel, hot conditions — cannot reach peak tier, no matter how the numbers fall.

Where the guardrail caps a tier, the severity number is capped with it, so the number and the label can never disagree in the room.

Both scores travel with the window (`severity`, `severity_confirmed_only`), and provisional fixtures are **named explicitly in the finding text** — "counted at half weight until confirmed" — rather than being quietly folded into a number.

---

## 10. Normalisation, tiers, confidence

```
severity = min(demand_points / 10.0, 1.0)
```

**Normalised against a fixed reference, not against the season's own maximum.** Relative normalisation would make every club's quietest month look like a crisis and every hard month look average — and it would make two clubs' Radars incomparable. The reference of 10 points is roughly four matches in eleven days with meaningful away travel: the spec's own worked example of a genuinely hard stretch. An anchor, declared as an anchor.

| Tier | Severity |
|---|---|
| `peak` | ≥ 0.70 |
| `elevated` | ≥ 0.45 |
| `standard` | < 0.45 |

**Confidence** is derived, not asserted:

| Label | When |
|---|---|
| `provisional` | Provisional fixtures are what lifted the tier |
| `likely` | Any estimated input in play — travel heuristic, historical-average climate, or provisional fixtures present but not decisive |
| `confirmed` | Confirmed fixtures, all home, real forecasts. Rare, and correctly so |

In practice most real windows land on `likely`, because travel is always an estimate. That is the honest answer and the spec asks for it: confidence, not certainty.

---

## 11. Window selection

`congestion_windows()` is deliberately exhaustive — one candidate per fixture — so a four-match stretch emits four heavily overlapping windows. Handing a nutritionist four near-identical date ranges would be noise dressed as depth.

Selection is greedy: take the highest-scoring window, then accept only later windows that do not overlap one already taken. A tight cluster collapses to one window; two separated clusters produce two.

---

## 12. Every finding names the decision it bears on

Per spec section 5, and the positioning rule in section 3: **findings stay declarative, only the decision becomes a question.** The hedge belongs in the confidence label, not in the tone. The severity finding is a plain evidenced fact — that is the proof of depth. The question back to the practitioner is the action layer, and it never contains its own answer.

The decision is templated off the **dominant driver** — whichever component actually produced the score, with the load multiplier converted to points so it can be compared like for like:

| Driver | Decision put to the nutritionist | Matrix hook |
|---|---|---|
| Congestion | How the refuelling load splits between club-provided and player-managed | `observation:slow-recovery + timing:congested` |
| Travel | What travels with the squad vs. what the hotel is relied on for | `observation:travel-dips + timing:away` |
| Climate (heat) | Different hydration protocol, or the standard one applied harder | `observation:cramping + timing:heat` |
| Climate (cold) | Same, framed around drift in voluntary drinking | `observation:illness + timing:all-season` |
| Load concentration | Squad-wide provision vs. individualised for the highest-minute players | `scope:individuals + observation:slow-recovery` |
| International duty | What goes with players on national duty, and what re-entry looks like | `observation:travel-dips + scope:individuals` |

The `matrix_hook` field points at real ids in `src/data/matrix.js`, so a window can pre-surface the exact Performance Matrix observation it bears on when the sit-down moves from Radar to Matrix at step 5. That is the connective tissue the spec asked for — and, in aggregate and anonymised, the same field is what tells DreamFruit which decisions clubs are actually facing.

**Naming players.** Names appear only where minutes are genuinely unevenly spread (`load_excess ≥ 0.15`) or where a player is individually identifiable through a confirmed call-up. Where names appear on a window whose driver is something else, the finding adds the reason they are listed. A name should never sit on a page with nothing explaining why — that is precisely how a fuelling read gets misheard as a medical one.

---

## 13. Worked example

Crystal Palace FC, illustrative late-autumn stretch. The competition mix and venue geography are real; dates, opponents, climate and minutes are illustrative. Reproduce with `python3 scripts/worked_example.py`.

**Input**

| Date | | Competition | Venue | Distance | Mode | Certainty |
|---|---|---|---|---|---|---|
| 21 Nov | A | Premier League | St James' Park | 411 km | flight | confirmed |
| 26 Nov | A | UEFA Europa League | Estádio da Luz | 1,574 km | flight | confirmed |
| 29 Nov | H | Premier League | Selhurst Park | — | home | confirmed |
| 2 Dec | A | EFL Cup | Villa Park | 174 km | coach | **provisional** |
| 5 Dec | H | Premier League | Selhurst Park | — | home | confirmed |

Top 3 players carry 32% of squad minutes (even spread would be 19%).

**Output — one window, 20 Nov to 3 Dec, `PEAK`, severity 0.74**

| Component | Points |
|---|---|
| Congestion | 3.08 — 11 of 13 days under raised carbohydrate demand |
| Contiguity | 2.00 — longest run 8 days, 5 with no reset (capped) |
| Travel | 1.58 — two flights, one 1,574 km |
| Climate | 0.43 — Lisbon +8 °C, halved as historical average |
| Load multiplier | ×1.049 |
| **Demand points** | **7.44 / 10** |
| Confirmed-only severity | 0.61 (`elevated`) |
| Confidence | `provisional` — the EFL Cup tie is what lifts it to peak |

**Finding** (verbatim from the code)

> 4 matches fall between 20 Nov and 3 Dec. That puts 11 of 13 days under a raised carbohydrate requirement, including a run of 8 consecutive days with no lower-intake day to reset against. The players listed are the 3 carrying the highest share of minutes over the last 28 days, so they meet this window with the shortest turnaround behind them. This includes 1 fixture in EFL Cup that depends on progression and is counted at half weight until confirmed.

**Decision it bears on**

> Across this stretch, how do you want the refuelling load split between what the club provides directly and what players are expected to manage themselves?

**Why this window and not another.** Congestion and contiguity supply 5.08 of the 7.44 points. Four matches in twelve days is the headline, but the thing that makes it peak rather than merely elevated is the eight-day unbroken elevated run between 21 and 29 November — there is no day in that stretch on which a lower carbohydrate intake is available. Travel adds meaningfully (1.58) because two of the four are flights, one long-haul. Climate contributes least (0.43) and is honestly discounted, because it is a historical average this far out, not a forecast. Remove the provisional cup tie and the window is still `elevated` at 0.61 — the stretch is real either way; progression is what decides whether it is the hardest of the season.

---

## 14. How the guardrails are enforced

`scripts/verify_scoring.py` — **30 checks, all passing.** These are not arithmetic tests; each maps to a promise the spec makes to a club.

- Congestion behaves monotonically; tighter turnarounds out-score spread ones; a lone fixture produces no window
- An all-provisional stretch can never reach peak tier, and is always labelled provisional
- Displayed tier is never more than one above the confirmed-only tier
- Provisional fixtures are named in the finding, not hidden in the score
- Home fixtures contribute zero travel; long-haul out-scores the identical home schedule
- Heat > cold > temperate; historical-average climate is discounted *and* disclosed
- Load multiplier stays inside 1.00–1.30; players are never named on an evenly-spread squad; named players always come with a stated reason
- Unconfirmed call-ups contribute nothing
- Severity always in 0–1 and never disagrees with its tier label
- Every window carries a question-framed decision, a declarative (non-question) finding, at least two citations, and a Matrix hook
- **No output text contains injury, medical, diagnostic or predictive language** — enforced by a term scan across every finding and question

That last check is the one to keep. It is the guardrail most likely to erode as findings get rewritten for tone.

---

## 15. Flagged for Connor — three things worth a decision

Per the brief: flag rather than silently work around.

**1. The travel threshold makes most away trips "flights."** At 90 km/h assumed road speed and a 2-hour coach threshold, anything beyond ~180 km scores as a flight. In the worked example that puts St James' Park (411 km) in the flight band — plausible for a Premier League club — but it also means almost every non-London away trip lands there, so travel loses some discriminating power domestically. Both values are config, and both were spec-confirmed, so this is a calibration question for the pilot rather than a bug: **is the real dividing line coach-vs-flight, or is it "does the squad sleep away the night before"?** The second may be the better lever.

**2. `assumed_contributing_squad_size = 16` is the most important number to revisit.** Load concentration is normalised against it, and it has to match however `load.py` ends up defining its player pool once real stats are wired in. If the real pull returns a 25-man roster including players with near-zero minutes, the ratio drops and the multiplier under-reads. Worth setting deliberately at the same time as the stats source, not before.

**3. Resolved.** Unannounced squads and empty squads used to look identical to the scorer — `get_call_ups()` returned an empty list either way. Fixed: `international.py` now carries the real FIFA international match calendar break dates for 2026-27 (`INTERNATIONAL_BREAKS`, sourced from the confirmed September/October combined window and the November window), and `compute_fuelling_windows()` takes an `international_breaks` argument. Where a confirmed break overlaps a window but isn't yet announceable (`squad_announceable()`), the finding now says so explicitly — "which players are called up isn't known yet" — rather than silently reading the gap as zero, and confidence can no longer read as `confirmed` while that gap exists. Verified by four new checks in `scripts/verify_scoring.py` (section 5b).

One smaller note: a fixture falling just outside the 11-day frame is excluded from the presented span even when it is close (the 5 December match in the worked example sits two days past the window end). Defensible, and consistent with the spec's own 11-day framing, but worth watching once real fixture lists land.

---

## 16. What this deliberately does not do

- **No injury or illness risk score.** This reads fuelling demand. Nothing more, and the term scan enforces it.
- **No single clean number without a confidence label.** The inputs do not support that precision.
- **No prediction of cup progression.** Provisional stays provisional at half weight and says so.
- **No second insight.** One formula, one insight, per the brief. The season-arc and situational-awareness framing in the spec sits on top of this as presentation, not inside it.
- **No redesign of the travel heuristic.** Flagged above instead.

---

## 17. Next

1. Replace the mock sources — climate, load, player bio, international call-ups, and the fixture list — each already behind a stable interface.
2. Settle the three flagged calibrations above with the pilot.
3. Build the three delivery formats (spec section 7) on top of this output: live teaser at step 4, printed depth at step 5, web + PDF shareable at step 7.
4. Wire `matrix_hook` into the Performance Matrix intake so a Radar window pre-surfaces the observation it bears on.
5. Guardrails and voice review before this is used with a real Crystal Palace visit.

---

**Sources**

- [UEFA expert group statement on nutrition in elite football (British Journal of Sports Medicine)](https://pubmed.ncbi.nlm.nih.gov/33097528/)
- [Monitoring of Post-match Fatigue in Professional Soccer (Sports Medicine)](https://link.springer.com/article/10.1007/s40279-018-0935-z)
- [Hydration Science and Strategies in Football (Gatorade Sports Science Institute)](https://www.gssiweb.org/sports-science-exchange/article/sse-128-hydration-science-and-strategies-in-football)
- [IOC Consensus Statement on Sports Nutrition (2010)](https://stillmed.olympic.org/media/Document%20Library/OlympicOrg/IOC/Who-We-Are/Commissions/Medical-and-Scientific-Commission/EN-IOC-Consensus-Statement-on-Sports-Nutrition-2010.pdf)
