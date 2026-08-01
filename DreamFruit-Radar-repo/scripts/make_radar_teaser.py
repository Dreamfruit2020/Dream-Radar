#!/usr/bin/env python3
"""
Dream Radar — live teaser (spec section 7, delivery format 1).

Shown live, on a laptop or tablet, at DFX step 4 — "pitch the DFX." This
is the opening move: one finding, no login, no depth dump. It exists to
prove in about ten seconds that DreamFruit did real homework on this
specific club's specific season, then hand the room over to the DFX
itself for the full sit-down at step 5.

Deliberately NOT the same content as the printed briefing. Spec section
3 (positioning): surface a hidden planning challenge, don't dump the
dataset. One number, one sentence, one door left open.

Runs on real fixture/roster/load/climate data when API_FOOTBALL_KEY is
configured and reachable (see worked_example.get_windows() ->
radar.build.build_for_club_with_source()); falls back to the
illustrative Crystal Palace worked example otherwise. Visibly marked
either "Live Data — Verify Before Sharing" or "Sample Output —
Illustrative Data" depending on which happened, never silently either.

Output: a single self-contained HTML file. No build step, no server —
open directly in a browser. Uses Google Fonts (Archivo Black + Inter) by
CDN; falls back to a bold system sans-serif if opened offline.

Run: python3 scripts/make_radar_teaser.py [output.html]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from worked_example import get_windows  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "Dream-Radar-Teaser.html"

TIER_COLOR = {"peak": "#e02875", "elevated": "#ffd166", "standard": "#c8e63d"}


def fmt(d) -> str:
    return f"{d.day} {d.strftime('%b')}"


def main() -> None:
    windows, is_real = get_windows()
    data_pill = "Live Data — Verify Before Sharing" if is_real else "Sample Output — Illustrative Data"
    top = sorted(windows, key=lambda w: w.severity, reverse=True)[0]
    f = top.contributing_factors
    tier = str(f["tier"])
    col = TIER_COLOR.get(tier, "#c8e63d")

    run_days = int(f["longest_elevated_run_days"])
    no_reset = int(f["no_reset_days"])

    if no_reset > 0:
        headline_num = str(run_days)
        headline_unit = "CONSECUTIVE DAYS"
        headline_sub = "with no lower-intake day to reset against"
    else:
        headline_num = f"{top.severity:.2f}"
        headline_unit = "SEVERITY"
        headline_sub = "the highest-demand window this season"

    club = "Crystal Palace FC"
    date_range = f"{fmt(top.start)} – {fmt(top.end)}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dream Radar — {club}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #08040a;
    --magenta: #e02875;
    --lime: #c8e63d;
    --violet: #8b5cf6;
    --gold: #ffd166;
    --white: #ffffff;
    --accent: {col};
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    height: 100%;
    background: var(--ink);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--white);
    overflow: hidden;
  }}
  body {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100vh;
    padding: clamp(24px, 4vw, 56px);
    position: relative;
  }}
  .bg-glow {{
    position: fixed;
    border-radius: 50%;
    filter: blur(10px);
    pointer-events: none;
    z-index: 0;
  }}
  .bg-glow.a {{ width: 480px; height: 480px; top: -160px; left: -160px;
    background: radial-gradient(circle, rgba(224,40,117,0.16), transparent 70%); }}
  .bg-glow.b {{ width: 560px; height: 560px; bottom: -220px; right: -220px;
    background: radial-gradient(circle, rgba(200,230,61,0.10), transparent 70%); }}

  header, footer, main {{ position: relative; z-index: 1; }}

  header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }}
  .brand {{ display: flex; align-items: center; gap: 12px; }}
  .mark {{
    width: 34px; height: 34px; flex-shrink: 0;
    background: var(--magenta);
    clip-path: polygon(50% 0%, 80% 35%, 100% 55%, 78% 60%, 62% 100%, 38% 100%,
                        22% 60%, 0% 55%, 20% 35%);
  }}
  .wordmark {{ font-family: 'Archivo Black', sans-serif; font-size: 15px; letter-spacing: 0.12em; }}
  .subwordmark {{ font-family: 'Inter', sans-serif; font-size: 9px; letter-spacing: 0.14em;
    color: rgba(255,255,255,0.4); text-transform: uppercase; margin-top: 2px; }}
  .pill {{
    border: 1px solid var(--gold);
    color: var(--gold);
    background: rgba(255,209,102,0.10);
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 999px;
    white-space: nowrap;
  }}

  main {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    max-width: 900px;
  }}
  .eyebrow {{
    font-size: clamp(10px, 1.4vw, 13px);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 18px;
  }}
  .headline {{
    font-family: 'Archivo Black', sans-serif;
    font-size: clamp(64px, 13vw, 168px);
    line-height: 0.92;
    color: var(--white);
  }}
  .headline .unit {{
    display: block;
    font-size: clamp(20px, 3.4vw, 40px);
    color: var(--accent);
    letter-spacing: 0.05em;
    margin-top: 6px;
  }}
  .sub {{
    font-size: clamp(15px, 2vw, 22px);
    color: rgba(255,255,255,0.72);
    margin-top: 20px;
    max-width: 620px;
    line-height: 1.45;
  }}
  .meta {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 30px;
    font-size: 13px;
    color: rgba(255,255,255,0.5);
  }}
  .tier-chip {{
    border: 1px solid var(--accent);
    color: var(--accent);
    background: rgba(255,255,255,0.04);
    padding: 5px 12px;
    border-radius: 999px;
    font-family: 'Archivo Black', sans-serif;
    font-size: 10px;
    letter-spacing: 0.1em;
  }}

  footer {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    border-top: 1px solid rgba(255,255,255,0.10);
    padding-top: 18px;
  }}
  .cta {{
    font-size: 13px;
    color: rgba(255,255,255,0.55);
    max-width: 520px;
    line-height: 1.5;
  }}
  .cta strong {{ color: var(--white); font-weight: 600; }}
  .club-tag {{
    font-family: 'Archivo Black', sans-serif;
    font-size: 11px;
    letter-spacing: 0.1em;
    color: rgba(255,255,255,0.35);
    text-align: right;
    white-space: nowrap;
  }}

  @media (max-height: 560px) {{
    body {{ overflow: auto; height: auto; min-height: 100vh; }}
    html {{ overflow: auto; }}
  }}
</style>
</head>
<body>
  <div class="bg-glow a"></div>
  <div class="bg-glow b"></div>

  <header>
    <div class="brand">
      <div class="mark"></div>
      <div>
        <div class="wordmark">DREAM RADAR</div>
        <div class="subwordmark">Live preview · {club}</div>
      </div>
    </div>
    <div class="pill">{data_pill}</div>
  </header>

  <main>
    <div class="eyebrow">One finding, built from public data alone</div>
    <div class="headline">{headline_num}<span class="unit">{headline_unit}</span></div>
    <p class="sub">{headline_sub.capitalize()} — {date_range}.</p>
    <div class="meta">
      <span class="tier-chip">{tier.upper()}</span>
      <span>Confidence: {top.decision.confidence.value}</span>
    </div>
  </main>

  <footer>
    <p class="cta">This is one finding, for one club, built entirely from public data —
      <strong>before we've said what DreamFruit actually does.</strong>
      There's a full breakdown, and what it means for your squad, waiting in
      today's DreamFruit Experience.</p>
    <div class="club-tag">DREAM OS · v1</div>
  </footer>
</body>
</html>
"""
    Path(OUT).write_text(html)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
