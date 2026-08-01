# Dream Performance Matrix™ — MVP

The first build of Dream OS: a configurator where club nutritionists engineer
their own functional drink ecosystem. React + Tailwind CSS 4 + Framer Motion.

## Run it

```bash
npm install
npm run dev      # local dev server
npm run build    # → dist/index.html — one portable file, everything inlined
```

`Dream-Performance-Matrix.html` (next to this folder) is a pre-built copy —
open it in any browser, no install needed.

## Flow

1. **Intro** — hero, animated DragonAid bottle, telemetry graphics
2. **Club Profile** — club name, team, primary objectives
3. **Performance Moments** — day timeline, multi-select deployment moments
4. **Foundation** — ACTIVATE / CHARGE / RESTORE natural-base pillars
5. **Precision Layer Builder** — ingredient modules with Low/Med/High levels; each selection renders a glowing layer on the bottle
6. **Your Club Matrix** — generated formulas, bottles/week estimate, matrix signature, 2-month programme
7. **Your Club Performance System** — "Begin Performance Build" runs a compile
   transition, then reveals the final report: club overview, formula sheets,
   weekly squad protocol, season requirements, next steps, PDF export (print)
   and consultation CTA

## Architecture (built for what comes next)

- `src/data/matrix.js` — single data layer driving every screen. Swap these
  static structures for live services: athlete data, wearables, bloodwork,
  AI recommendations, manufacturing.
  - `estimateBottlesPerWeek()` — placeholder serving model → replace with squad scheduling + AI
  - `FORMULA_MAP` — moment → formula mapping → replace with recommendation engine
- `src/App.jsx` — wizard state machine; `config` object is the full build spec
  (this is the payload a future API would receive)
- `src/screens/*` — one component per screen
- `src/components/Bottle.jsx` — SVG bottle placeholder → future 3D/product renders
- `src/components/UI.jsx` — shared motion presets, buttons, backdrop
