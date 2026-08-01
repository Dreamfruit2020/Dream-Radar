# Dream Radar™ — Product Spec v1

*Nutritionist-facing intelligence briefing, built on genuinely public data, delivered across the DreamFruit Experience sales journey.*

Status: Approved to build · Owner: Connor · Pilot club: Crystal Palace FC · Last updated: 19 July 2026

---

## 1. What this is, and why

Right now DreamFruit's sales motion (see `Dreamfruit Sales Process FINAL.pdf`) sells a tasting experience first and a subscription second. Dream Radar is a third thing sitting between them: a short, personalised intelligence briefing about the club's own season — built entirely from data that's genuinely public — presented live by a Dreamfruit rep during the pitch meeting or the follow-up call.

Its job isn't to sell drinks directly. It's to make the nutritionist think *"they clearly did real homework on us, and this isn't just a fruit and juice pop-up — there's real depth behind this"* — without anyone having to say that sentence out loud. It is the proof point for the "natural health intelligence company" positioning, delivered as evidence rather than a claim.

**How this relates to the existing Dream Performance Matrix.** The two products are opposite halves of the same relationship:

| | Dream Radar (this spec) | Dream Performance Matrix / Performance Brief |
|---|---|---|
| Direction | Outbound — Dreamfruit brings insight *to* the club | Inbound — the club describes what *they're* observing |
| Data | Public data about the club, prepared in advance | The nutritionist's own context, given live |
| Moment in the sales process | Step 4 teaser, step 5 full depth, step 7 shareable | **Run live, in person, at step 5** — the same visit, while trust is highest |
| Goal | Prove depth and credibility, open the door | Walk through it there and then, produce a real Confidential Performance Brief on the spot |

Radar opens the door fast. The Matrix walks through it the same visit, while the iron's hot, rather than waiting for a separate meeting later.

---

## 2. Persona: the nutritionist, presenting onward to the head of performance

**Primary: the nutritionist**, sitting across the table during the DFX meeting and follow-up. A few things worth designing around:

- They are evidence-literate and will notice immediately if a number is wrong, stale, or unsourced. One bad figure (a player's weight that's a season out of date, say) costs more credibility than the whole briefing gains.
- They think primarily in fuelling and hydration terms. Injury and illness are still relevant to them specifically where poor fuelling is a contributing factor — fatigue-related soft-tissue issues, congestion-driven immune dips — so Radar can reference that connection, but always through a fuelling lens with a cited source, never as a standalone injury-risk or diagnostic claim. That distinction matters: "this congestion pattern is associated with higher fatigue-related illness in the literature, here's the citation" is fine; "Player X is at elevated injury risk" is not — that's medical/performance-staff territory.
- They are time-poor. The live reveal needs to land its point in under two minutes of screen time, with more depth available if they want to dig in.

**Secondary, but load-bearing: the head of performance.** The nutritionist doesn't hold the budget alone — any spend beyond what's already agreed typically needs the head of performance to sign off, and they weren't in the room for the live reveal. That means the **shareable version has to stand on its own**, without a rep narrating it: it needs to carry enough of the "why this matters" case, not just the raw insight, so the nutritionist can forward it internally and have it do real work toward a sign-off rather than just being a nice recap.

---

## 3. Positioning & voice

Not just guardrails — the actual voice this needs to have, on every screen and in both printed and shareable formats:

- **Intelligence partner, not nutrition advisor.** Radar's job is to inform, not instruct. It never tells a nutritionist what to give a player — that's their call, made with their expertise. It surfaces what they now know that they didn't before.
- **Informed, not replaced.** Every interaction should leave the nutritionist feeling sharper in front of their own staff, never second-guessed by a tool. This is the biggest failure mode to design against in a profession this protective of its own judgement — sports science and nutrition are an ego-sensitive field, and a tool that reads as grading the practitioner will get resisted no matter how good the underlying data is.
- **Findings are declarative and evidenced; actions are framed as questions.** This is the rule that reconciles "prove real depth" with "don't tell people what to do." What's true about the club's own season is stated plainly, cited, specific — that's the proof of depth, the "how did you know that" moment. What to do about it is a question handed back to the practitioner, not an instruction. *"Here's what's true, cited. How are you thinking about approaching it?"* — never *"you should do X."*
- **Situational awareness is the umbrella; Fuelling Risk Windows is the headline finding inside it.** Gives the product's own name a reason to exist — Radar should read as ongoing awareness of the season, including the season-arc thinking in section 5, not a single risk alert fired once. Scope discipline still holds: one insight, not many. This changes the framing, not what gets built.
- **The shareable artifact makes the nutritionist look prepared — not DreamFruit look clever.** Positioned as prepared *with* the nutritionist, not purely DreamFruit's report passed along: visible credit, room for their own framing, sent in a way that reads as their preparation for the head of performance, not a vendor's pitch deck forwarded on their behalf.

---

## 4. Confirmed: where Radar sits, where the Performance Matrix sits

Mapped directly against `Dreamfruit Sales Process FINAL.pdf`:

| Step | What happens | Radar | Performance Matrix |
|---|---|---|---|
| 1–3. Outreach, sales doc, nurture | Standard sales motion | — | — |
| **4. Meeting — pitch the DFX** | Opening pitch to secure the DFX stand day | **Live-presented, teaser depth.** Supports the opening move — "before we even talk about what we do, here's what we already know about your season." Light enough to land in a few minutes and earn the DFX booking. | — |
| **5. DreamFruit Experience** | Two spaces running in parallel — see section 13 | Tasting stand (public): the experience itself, staffed separately. Quiet area (private, same visit): **printed Radar piece + full Performance Matrix walkthrough, run live and completed with the nutritionist.** This is where the iron is hottest — Radar has already proven the depth is real, so the nutritionist walks straight into the deeper, consultative Matrix conversation, and leaves with an actual Confidential Performance Brief, not a promise of one. | **Run and completed here.** |
| 6. Wrap-up video | Connor films the highlights | — | — |
| **7. Follow-up call — presents Club Plan / Stay On-Demand** | The commercial ask | **Shareable digital version.** Written to stand alone so the nutritionist can forward it to the head of performance for budget sign-off. | **The Brief produced at step 5 is the supporting material for the ask** — not a preview, the real thing, already sat with the nutritionist for however long since the visit. |
| **8. Once they're buying and testing product** | Club is live — Club Plan or Stay On-Demand, product moving | — | **Revisited, not re-run.** As real usage feedback comes in, the Matrix gets used again for revisions and updates to the Brief rather than a one-off document that's never touched again. |

The short version: **Radar opens the door fast at step 4. Step 5 is where both fire together and the real work gets done — Matrix run to completion, in person, while trust is at its peak. Step 7 closes commercially on the back of an already-completed Brief. Step 8 keeps the Matrix alive as a living document as the relationship runs.**

---

## 5. V1 scope: one insight, done properly

Resist the temptation to surface everything the data allows. V1 ships **one** synthesis, built to be unmistakably useful to a nutritionist and impossible to get anywhere else without real work:

### "Fuelling Risk Windows"

*The specific weeks in the club's own fixture list where congestion, travel burden, climate, international call-ups and squad workload concentration combine to create the highest fuelling and hydration demand — and who's carrying the heaviest load into them.*

Framed as a fuelling and hydration question first. Where the underlying research connects poor fuelling to fatigue-related illness or soft-tissue issues, Radar can say so — with a citation — because that's a genuine part of what a nutritionist cares about. What it should never do is turn that into a standalone injury-risk score or a claim about a specific player's likelihood of getting hurt. The line is: *fuelling is the subject, injury/illness is a cited consequence when the evidence supports it* — not the other way round.

What it looks like on screen, roughly:

> *"Your toughest fuelling window this season: 14–25 October. Four matches in eleven days, including a Thursday-night away trip to [Club] with a 2am hotel arrival and a 6°C temperature drop from home, plus [N] first-team players returning from international duty three days prior. [Player A], [Player B] and [Player C] are carrying the heaviest recent load into it — and it's exactly the kind of window most squads don't have a specific fuelling protocol built for."*

### Risk and opportunity are the same window

The highest-demand weeks aren't just the highest-risk weeks — they're the highest-*differentiation* weeks. Most opposing squads won't have a fuelling protocol specifically tuned to their own congestion, travel and international-duty pattern; a club that does gets a real edge in exactly the weeks that matter most. Worth building this framing into the copy directly rather than leaving Radar purely defensive ("protect against this risk") — "this is where you can out-execute the opposition" is a stronger, more compelling story for both the nutritionist and the head of performance approving spend.

One honesty guardrail on this: we can say, generally and fairly, that most clubs don't run bespoke fuelling protocols tuned to specific congestion windows — that's a reasonable industry-level observation. What we can't do is claim to know a *specific* rival's specific weakness — we have no public data that tells us that, and pretending otherwise is the same credibility risk flagged elsewhere in this spec.

### The season arc: baseline habits, plus the spikes

Fuelling Risk Windows shouldn't be presented as the only weeks that matter — they're the spikes on top of a season-long baseline need, and the briefing should say so explicitly:

- **Early season:** the opportunity to build good fuelling and hydration habits before the calendar gets demanding — establishing the routine while there's room to.
- **Winter months:** protecting availability through the congestion period specifically via immune and recovery support, not just performance output.
- **End of season:** sustaining output through accumulated fatigue so the squad finishes strong rather than fading.

This has a direct commercial implication worth stating plainly: the case for DreamFruit product isn't "buy extra for three specific weeks," it's a **season-long baseline** with **intensified need at the flagged windows** — which is exactly what supports a **Club Plan (contracted weekly)** rather than framing this as something to dip in and out of on-demand around risk weeks only. Radar's own output should make that structure the obvious conclusion, not something a rep has to argue for separately.

### Every finding names the decision it bears on — and that decision doesn't die on the screen

A finding on its own — "here's your toughest fuelling window" — is only half the value. The output should name the actual decision at stake, not the answer, just what genuinely needs deciding. That named decision then goes three places:

- **Into the Matrix, the same visit.** Since Radar and the Matrix now run back to back in the same quiet-room sit-down (section 4), the decision Radar names should carry straight into the Matrix's observation-led intake — pre-surfaced as something to work through together, rather than the nutritionist starting the intake cold. Practically, this means the data structure Radar uses to name a decision needs to be readable by the Matrix session — one connected handoff, not two tools that happen to run on the same afternoon.
- **Into DreamFruit's own product development.** Named decisions, aggregated across visits over time, are a genuine signal for what to build next — a real view into what clubs are actually wrestling with, season to season, that most beverage or supplement companies never get. This reinforces the "natural health intelligence company" positioning at the company level, not just the room level.
- **Said out loud to the nutritionist.** The sit-down should make this visible: *this is a decision we're already set up to build against.* Stated honestly, though — the credible version of that claim is that DreamFruit already has a natural-base platform (ACTIVATE, CHARGE, RESTORE) built for exactly this category of decision, and the Matrix session tailors it to their specific brief, not that anything gets invented from scratch overnight. Overpromising instant bespoke formulation on the spot risks exactly the credibility trap flagged throughout this spec — "we're not starting from zero" is the honest claim, and it's still a genuinely strong one.

Two things worth being upfront about before this gets built:

- **This is a v1 design requirement, not a v1 analysis engine.** Structure named decisions cleanly from day one — even while the Matrix intake itself stays manual for now — so the data exists to learn from later. The actual product-development signal engine, aggregating patterns across clubs, is v2+, once there's more than one pilot club's worth of decisions to draw on.
- **Confidentiality holds even inside the aggregation.** A specific club's specific decision stays confidential to that club, exactly as the Confidential Performance Brief already is. Anything that feeds product development has to be anonymised and aggregated — "this kind of decision recurs across several clubs in this period" — never one club's specific context surfacing in how DreamFruit talks to another.

---

## 6. Data sources — what's genuinely public, and how each is used

Confirmed: proceed with public stats sources, cited on every use — no separate licensing gate before build, citation is the mitigation.

| Input | Source (realistic examples) | Refresh | How it's used | Caveats |
|---|---|---|---|---|
| **Fixtures** | Official league/competition calendars | Weekly, and always re-pulled close to a visit | Base timeline — dates, venues, home/away, competition | See "handling fixture uncertainty" below — not every future fixture is equally certain |
| **Travel** | *Not a separate dataset* — computed from fixtures + venue geodata | Computed on demand from fixtures | Distance and travel time between venues; timezone deltas for European trips | See travel heuristic below — a well-informed estimate, not confirmed club logistics, and always labelled as such |
| **Climate** | Public historical/forecast weather data for venue + date | Per fixture | Temperature/humidity delta vs. home climate, precipitation risk | Forecast accuracy degrades beyond ~10 days out; use historical averages further ahead |
| **Match load (minutes played)** | Public stats sites (FBref-style, league-published stats) | Weekly in-season | Identify which players are carrying the heaviest recent club workload | Cite the source and pull date on every figure shown |
| **International call-ups** | Published national squad lists | Announced roughly 1–2 weeks before each international break | Adds international minutes/travel on top of club load for called-up players around break windows | Squads aren't known further out than that — see below |
| **Player bio** | Official club roster pages, public reference sites | Start of season + transfer windows | Age, height, weight, position — context for individual load readings | Often stale or self-reported; always show "as published" and a source link, never assert as verified fact |

### Travel heuristic (confirmed correct — must stay editable)

Rather than trying to source actual travel logistics (which are private to the club), Radar applies a documented, sensible rule set:

- Away trips are assumed to involve **travel the day before** and an **overnight hotel stay**, consistent with standard practice.
- **Mode of travel:** coach if the point-to-point journey is under ~2 hours, otherwise flight — the Premier League norm and the default assumption.
- Timezone deltas are calculated directly from fixture venue coordinates for European away fixtures.
- Every travel figure shown is labelled as an **estimate based on standard club practice**, never presented as confirmed fact about this specific club.
- **Build requirement:** the threshold (2 hours), the day-before/hotel assumption, and the coach-vs-flight rule must all be **stored as configuration, not hardcoded**, so they can be corrected or tuned per competition later without a code change.

### Handling fixture uncertainty (cup progression)

Not every fixture on a club's calendar is equally certain, and presenting a maybe as a fact is exactly the kind of error that costs credibility. Three tiers:

- **Confirmed, full season:** domestic league fixtures, and — usefully for the pilot — the Europa League **league phase**, where opponents and dates are set in advance for all eight games, not just conditionally scheduled. Crystal Palace qualify directly into this phase as 2026 Conference League winners, alongside the Premier League, FA Cup and EFL Cup — a genuinely congested, multi-competition season and a good real test of this problem. [[Premier League: how Palace's Conference League win affects European qualification]](https://www.premierleague.com/en/news/4671711/how-crystal-palace-uefa-conference-league-final-affects-european-qualification)
- **Calendar-blocked, conditional:** domestic cup rounds (FA Cup, EFL Cup) and continental knockout rounds. The *date* is usually set well in advance even before it's known whether the club will play it. These should show on the timeline as a **provisional/potential congestion flag**, distinct from confirmed fixtures, and shouldn't be baked into the core Fuelling Risk score until qualification is confirmed.
- **Unknown:** anything beyond the current season's qualification picture. Out of scope for a fuelling briefing.

This reinforces why the data build has to be refreshed close to the visit date rather than prepared weeks ahead — qualification status changes week to week during cup competitions.

### International call-ups

International breaks themselves are fixed and known well in advance (FIFA calendar), but **who gets called up isn't** — national squads are typically announced only one to two weeks before the break. Practically: the international-duty component of the load score can only be populated close to the break, following the same "refresh near the visit date" principle as fixture uncertainty above. Players away on international duty return with less club-controlled recovery time, added travel, and often added minutes — a genuine, citable fuelling consideration once squads are announced, and worth flagging as "provisional — squads not yet announced" before that point rather than guessing who'll be picked.

---

## 7. Delivery formats — three, prepared together, at three different steps

This ships as three coordinated outputs from a single data build, not three separate efforts — but each has a distinct depth and a distinct job, matching where it sits in the sales process (section 4):

1. **Live-presented reveal — step 4, teaser depth.** A short, cinematic on-screen moment — in the same visual language as the existing Performance Matrix (dark, glass, DreamFruit brand) — driven by the rep on a tablet during the pitch meeting. **Runs entirely on data cached the night before the visit.** No live API calls during the sit-down; a training-ground canteen with patchy wifi cannot be the failure point for the one moment this needs to land. Job: earn the DFX booking, fast.
2. **Printed leave-behind — step 5, full depth.** A prepared PDF, brought into the quiet-room sit-down alongside the Matrix walkthrough — not left on display at the public stand, since it's built for the nutritionist's eyes and the depth only lands with someone talking them through it. Reuses the same design system and generation pipeline already built for the DragonAid concept sheet (`scripts/make_concept_pdf.py`). This is the deepest version of the three: more data, more context, something tangible that outlasts the visit itself.
3. **Shareable — step 7, written to stand alone, both a web link and a PDF.** Sent alongside the existing "wrap-up video" step, timed to support the Club Plan / Stay On-Demand ask. Both formats carry the same content: the web link is the easy, low-friction thing to open and glance at on a phone; the PDF is what actually gets attached to an email and forwarded on to the head of performance for sign-off — internal approval chains tend to want a fixed document, not a link that could change. Unlike the other two formats, nobody from DreamFruit is necessarily in the room when either version gets read, so it needs to carry its own case (why this matters, what's being asked for), not just restate the insight.

All three are generated from the same underlying data build for a given club and visit date, so the numbers never disagree with each other.

---

## 8. Operational workflow ("the night before")

For v1, this is a **prepared, not live**, process — intentionally simple so we can prove the concept before building automation we don't yet need:

1. Rep confirms the club and visit date.
2. Data is pulled for that club: fixtures (tiered by certainty), computed travel/climate for upcoming fixtures, recent minutes-played, current roster, and any confirmed international call-ups.
3. The Fuelling Risk Window(s) are computed, each with its named decision, and all three outputs are generated from the same build — teaser (step 4), full-depth PDF (step 5), standalone shareable (step 7).
4. **A human sanity-check pass** before it's ever shown to a club — confirms the numbers are current, provisional items are clearly marked, and nothing reads as a standalone injury claim. This matters more early on, while we're building trust in the system's own output.
5. Rep takes the tablet (with the reveal cached locally) and the printed copy to the DFX visit — **and is ready to run the Matrix live with the nutritionist at step 5, in the same visit**, straight off the back of the Radar reveal, with the named decisions ready to carry into that conversation.

Worth noting: the Performance Matrix already runs entirely client-side, with no backend dependency, which means it's already fit to be walked through live and offline at a training-ground stand — this pivot is a process decision, not a rebuild.

v2 can automate steps 2–3 into a scheduled pipeline once the format and the sanity-check process have proven themselves manually.

---

## 9. Guardrails

Carried forward from earlier discussion, made concrete for this build:

- **Every figure is sourced.** A visible citation or "as of [date]" tag on every data point that came from outside DreamFruit.
- **Confidence, not certainty.** Travel, fixture-uncertainty and load-risk readings are framed as informed estimates ("likely," "provisional," "based on published data"), never asserted as fact.
- **Fuelling first, injury only as a cited consequence.** Radar can connect poor fuelling to fatigue-related illness or soft-tissue issues where the research supports it, always with a citation — but never scores or predicts a specific player's injury risk. That line stays with medical/performance staff.
- **Data minimisation.** Even though every input is public, we only hold what's needed to regenerate a given club's briefing — no reason to build a broader player database than the product requires.
- **Confidentiality holds inside aggregation too.** See section 5 — a club's named decisions stay confidential to that club, even when patterns across clubs inform product development.

---

## 10. Technical implications

The current Performance Matrix is a static, single-file client app with no backend — that was the right call for a configurator, but Radar needs more:

- A small backend for the data build: fetch/compute jobs, a lightweight store for cached club data, and the composite scoring logic for Fuelling Risk Windows.
- A PDF generation step, extending the existing `reportlab`-based pipeline.
- A simple way to serve the shareable link (this can likely still sit on the current Netlify hosting via serverless functions, avoiding a heavier infra commitment for v1).
- No live third-party API calls during a client visit — everything the rep uses in the room is pre-built.
- A named-decision data structure that both Radar and the Matrix can read — the connective layer described in section 5.

This is a genuinely bigger lift than anything shipped so far on this project, which is exactly why v1 scope stays to one club, one insight, and a manual prep step rather than a fully automated platform. The Performance Matrix side of step 5 needs no new engineering — it already runs offline, client-side, and is built to be walked through live.

---

## 11. Success criteria for v1

- Does the nutritionist visibly engage with the step 4 reveal (questions, asking to see more)?
- Does the nutritionist actually complete the Matrix at step 5, in person, rather than it needing a follow-up session to finish?
- Does the decision Radar names actually get picked up and worked through in the Matrix sit-down, or does it get lost between the two?
- Does the step 7 shareable version actually get forwarded — and does it produce a faster or easier sign-off from the head of performance?
- Does the completed Brief from step 5 visibly do work at step 7 — does it come up unprompted in that conversation?
- Does the season-long baseline + spike-window framing land as a case for **Club Plan** specifically, rather than Stay On-Demand?
- Does the club move to Club Plan or Stay On-Demand at a noticeably higher rate for visits where Radar + Matrix were run together vs. those where they weren't?
- Not a goal for v1: serving any persona beyond the nutritionist and the head of performance as a forwarded audience, or any dataset beyond the six listed above.

---

## 12. Decisions confirmed

1. **Naming.** Dream Radar — confirmed.
2. **Stats sourcing.** Confirmed to proceed using public stats sources, cited on every figure. No separate licensing gate before build.
3. **Travel rule set.** Confirmed correct. Built as configuration, not hardcoded, so it can be corrected later without a code change.
4. **Pilot club.** Crystal Palace FC. Useful test case beyond the existing relationship — as 2026 Conference League winners they've qualified directly into the Europa League league phase alongside the Premier League, FA Cup and EFL Cup, giving a genuinely congested, multi-competition season to build the fixture-uncertainty logic against from day one.
5. **Shareable format.** Both a web link and a PDF — see section 7.
6. **Positioning and voice.** Intelligence partner over advisor, findings-as-evidence with actions-as-questions, situational awareness as the umbrella frame, and named decisions that connect Radar to the Matrix and to DreamFruit's own product development — see sections 3 and 5.

No open items remain. Spec is ready to build against.

## 13. DFX day staffing (confirmed)

Two people, two spaces, running in parallel:

- **On the stand:** a staff member runs the tasting experience itself — players and staff, drinks, fruit, the DFX atmosphere in the reference photo.
- **In a quiet area:** a second staff member takes the nutritionist through Radar's printed piece and the full Matrix sit-down, away from the noise of the stand, with the unhurried, consultative time that conversation actually needs.

Both are happening on the same visit, so the printed piece brought into the quiet room, the step 4 teaser that opened the relationship, and the step 7 shareable that follows it all come from the same underlying data build (section 8) — the numbers never shift between them.
