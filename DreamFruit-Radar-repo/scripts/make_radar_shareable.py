#!/usr/bin/env python3
"""
Dream Radar — shareable web version (spec section 7, delivery format 3).

Sent after the visit as part of the step-7 follow-up (Club Plan / Stay
On-Demand), paired with the printed PDF from the same session
(scripts/make_radar_briefing.py) — spec section 12 confirmed the
shareable format as "both web link and PDF," not one or the other.

Same content depth as the PDF, laid out as a scrollable web page rather
than two fixed sheets, so it holds up on a laptop or a phone when a
nutritionist forwards it to their head of performance.

Runs on real fixture/roster/load/climate data when API_FOOTBALL_KEY is
configured and reachable (see worked_example.get_windows() ->
radar.build.build_for_club_with_source()); falls back to the
illustrative Crystal Palace worked example otherwise. Visibly marked
either "Live Data — Verify Before Sharing" or "Sample Output —
Illustrative Data" depending on which happened, never silently either.

Output: a single self-contained HTML file. No build step, no server.
Uses Google Fonts (Archivo Black + Inter) by CDN; falls back to a bold
system sans-serif if opened offline.

Carries a "Prepared with [Nutritionist Name]" credit line (spec section
3: "makes the nutritionist look prepared — not DreamFruit look clever,"
Connor's decision 1 Aug 2026 — this belongs in the artifact itself).
Pass a name as the third CLI arg; without one it renders a visible
placeholder rather than silently omitting the credit.

Run: python3 scripts/make_radar_shareable.py [output.html] [pdf_link] ["Nutritionist Name"]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from worked_example import get_windows  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "Dream-Radar-Shareable.html"
PDF_LINK = sys.argv[2] if len(sys.argv) > 2 else "Dream-Radar-Briefing.pdf"
NUTRITIONIST_NAME = sys.argv[3] if len(sys.argv) > 3 else "[Nutritionist Name]"

TIER_COLOR = {"peak": "#e02875", "elevated": "#ffd166", "standard": "#c8e63d"}
COMPONENTS = [
    ("Congestion", "congestion", "#e02875", 4.0),
    ("Contiguity", "contiguity", "#ff4f9a", 2.0),
    ("Travel", "travel", "#4cc9f0", 2.0),
    ("Climate", "climate", "#ffd166", 1.5),
    ("International duty", "international", "#8b5cf6", 2.0),
]


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def fmt(d) -> str:
    return f"{d.day} {d.strftime('%b')}"


def window_card(w, expanded: bool) -> str:
    f = w.contributing_factors
    tier = str(f["tier"])
    col = TIER_COLOR.get(tier, "#c8e63d")
    pct = min(w.severity, 1.0) * 100

    head = f"""
    <div class="w-card {'expanded' if expanded else ''}" style="--accent:{col}">
      <div class="w-card-top">
        <div>
          <div class="w-tier" style="color:{col}">{tier.upper()}</div>
          <div class="w-dates">{fmt(w.start)} – {fmt(w.end)}</div>
        </div>
        <div class="w-severity">
          <div class="w-severity-num">{w.severity:.2f}</div>
          <div class="w-severity-label">severity</div>
        </div>
      </div>
      <div class="bar-track"><div class="bar-fill" style="width:{pct:.0f}%; background:{col}"></div></div>
      <div class="w-meta">
        <span class="tag">Driven by {esc(str(f['dominant_driver']))}</span>
        <span class="tag">Confidence: {w.decision.confidence.value}</span>
      </div>
    """

    if not expanded:
        return head + "</div>"

    # component breakdown bars
    bars = ""
    for label, key, bcol, ref in COMPONENTS:
        val = f.get(key, 0.0)
        frac = min(val / ref, 1.0) * 100 if ref else 0
        bars += f"""
        <div class="comp-row">
          <span class="comp-label">{label}</span>
          <div class="comp-track"><div class="comp-fill" style="width:{frac:.0f}%; background:{bcol}"></div></div>
          <span class="comp-val">{val:.2f}</span>
        </div>"""

    players_html = ""
    if w.decision.players_of_note:
        chips = "".join(f'<span class="chip">{esc(p)}</span>' for p in w.decision.players_of_note)
        players_html = f'<div class="players"><div class="section-label">Players of note</div><div class="chip-row">{chips}</div></div>'

    citations_html = "".join(
        f'<li>{esc(c)}</li>' for c in w.decision.citations
    )

    return head + f"""
      <div class="deep-grid">
        <div class="deep-col">
          <div class="card-block">
            <div class="section-label">Finding</div>
            <p class="finding-text">{esc(w.decision.finding)}</p>
          </div>
          <div class="card-block decision-block">
            <div class="section-label" style="color:#8b5cf6">The decision this bears on</div>
            <p class="decision-text">{esc(w.decision.decision_question)}</p>
          </div>
          {players_html}
          <div class="matrix-hook">Goes straight into your Performance Matrix session.</div>
        </div>
        <div class="deep-col">
          <div class="section-label">Score breakdown</div>
          {bars}
          <div class="comp-row" style="margin-top:10px">
            <span class="comp-label">Load multiplier</span>
            <span class="comp-val" style="color:#c8e63d">×{f['load_multiplier']:.3f}</span>
          </div>
          <div class="days-line">{int(f['elevated_days_calendar'])} of {int(f['frame_days'])} days elevated
            &nbsp;·&nbsp; longest run with no reset: {int(f['longest_elevated_run_days'])} days</div>
          <div class="section-label" style="margin-top:18px">Evidence base</div>
          <ul class="citations">{citations_html}</ul>
        </div>
      </div>
    </div>
    """


def main() -> None:
    windows, is_real = get_windows()
    windows = sorted(windows, key=lambda w: w.severity, reverse=True)
    cards = "".join(window_card(w, expanded=(i == 0)) for i, w in enumerate(windows))

    if is_real:
        data_pill = "Live Data — Verify Before Sharing"
        disclaimer = (
            "LIVE DATA: fixture dates, opponents, climate readings and player minutes on this page "
            "were pulled live for this club. This is a new integration — verify names and numbers "
            "before this reaches a nutritionist. The scoring formula and citations are real — "
            "see docs/radar-scoring-design.md."
        )
    else:
        data_pill = "Sample Output — Illustrative Data"
        disclaimer = (
            "SAMPLE OUTPUT: fixture dates, opponents, climate readings and player minutes on this "
            "page are illustrative, not a live pull. The scoring formula and citations are real — "
            "see docs/radar-scoring-design.md. Built from public data. Validated with your own staff."
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dream Radar — Crystal Palace FC</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #08040a;
    --panel: rgba(255,255,255,0.045);
    --panel-border: rgba(255,255,255,0.13);
    --magenta: #e02875;
    --lime: #c8e63d;
    --violet: #8b5cf6;
    --gold: #ffd166;
    --white: #ffffff;
    --muted: rgba(255,255,255,0.55);
    --faint: rgba(255,255,255,0.35);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--ink);
    background-image:
      radial-gradient(circle at 5% 0%, rgba(224,40,117,0.14), transparent 40%),
      radial-gradient(circle at 95% 60%, rgba(200,230,61,0.08), transparent 40%);
    background-attachment: fixed;
    color: var(--white);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.5;
  }}
  .wrap {{ max-width: 920px; margin: 0 auto; padding: 28px 24px 80px; }}

  header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 14px;
    padding-bottom: 18px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
    margin-bottom: 36px;
  }}
  .brand {{ display: flex; align-items: center; gap: 12px; }}
  .mark {{
    width: 30px; height: 30px; flex-shrink: 0;
    background: var(--magenta);
    clip-path: polygon(50% 0%, 80% 35%, 100% 55%, 78% 60%, 62% 100%, 38% 100%,
                        22% 60%, 0% 55%, 20% 35%);
  }}
  .wordmark {{ font-family: 'Archivo Black', sans-serif; font-size: 14px; letter-spacing: 0.1em; }}
  .subwordmark {{ font-size: 9px; letter-spacing: 0.12em; color: var(--faint); text-transform: uppercase; margin-top: 2px; }}
  .header-right {{ display: flex; align-items: center; gap: 12px; }}
  .pill {{
    border: 1px solid var(--gold); color: var(--gold); background: rgba(255,209,102,0.10);
    font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 6px 12px; border-radius: 999px; white-space: nowrap;
  }}
  .pdf-btn {{
    display: inline-block;
    font-family: 'Archivo Black', sans-serif;
    font-size: 11px; letter-spacing: 0.08em;
    color: var(--ink); background: var(--white);
    padding: 10px 18px; border-radius: 999px; text-decoration: none;
    white-space: nowrap;
  }}

  .eyebrow {{ font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--magenta); margin-bottom: 14px; }}
  h1 {{ font-family: 'Archivo Black', sans-serif; font-size: clamp(30px, 5vw, 46px); line-height: 1.05; margin: 0 0 12px; }}
  .credit {{ font-family: 'Archivo Black', sans-serif; font-size: 11.5px; letter-spacing: 0.06em; color: var(--lime); margin: 0 0 22px; }}
  .lede {{ color: var(--muted); font-size: 15px; max-width: 640px; margin-bottom: 44px; }}

  .section-title {{
    font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--faint);
    margin: 0 0 16px;
  }}

  .w-card {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 16px;
  }}
  .w-card.expanded {{
    border-color: color-mix(in srgb, var(--accent) 55%, var(--panel-border));
    box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent) 18%, transparent);
  }}
  .w-card-top {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }}
  .w-tier {{ font-family: 'Archivo Black', sans-serif; font-size: 15px; letter-spacing: 0.06em; }}
  .w-dates {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}
  .w-severity {{ text-align: right; }}
  .w-severity-num {{ font-family: 'Archivo Black', sans-serif; font-size: 22px; }}
  .w-severity-label {{ font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--faint); }}

  .bar-track {{ height: 8px; background: rgba(255,255,255,0.08); border-radius: 999px; margin: 16px 0 12px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 999px; }}

  .w-meta {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  .tag {{
    font-size: 11px; color: var(--muted);
    border: 1px solid rgba(255,255,255,0.15);
    padding: 4px 10px; border-radius: 999px;
  }}

  .deep-grid {{
    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 28px;
    margin-top: 26px;
    padding-top: 22px;
    border-top: 1px solid rgba(255,255,255,0.10);
  }}
  @media (max-width: 720px) {{ .deep-grid {{ grid-template-columns: 1fr; }} }}

  .section-label {{ font-size: 10.5px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--faint); margin-bottom: 8px; }}
  .card-block {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
  }}
  .finding-text {{ margin: 0; font-size: 14px; color: rgba(255,255,255,0.85); }}
  .decision-block {{ border-color: rgba(139,92,246,0.35); background: rgba(139,92,246,0.06); }}
  .decision-text {{ margin: 0; font-size: 14.5px; font-style: italic; color: var(--white); }}

  .chip-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .chip {{
    font-size: 11.5px; font-weight: 600;
    border: 1px solid rgba(200,230,61,0.5); color: var(--lime);
    background: rgba(200,230,61,0.08);
    padding: 5px 12px; border-radius: 999px;
  }}
  .players {{ margin-bottom: 14px; }}
  .matrix-hook {{ font-size: 11px; letter-spacing: 0.04em; color: var(--faint); }}

  .comp-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
  .comp-label {{ width: 118px; flex-shrink: 0; font-size: 11.5px; color: var(--muted); }}
  .comp-track {{ flex: 1; height: 7px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden; }}
  .comp-fill {{ height: 100%; border-radius: 999px; }}
  .comp-val {{ width: 42px; text-align: right; font-family: 'Archivo Black', sans-serif; font-size: 11.5px; flex-shrink: 0; }}
  .days-line {{ font-size: 11.5px; color: var(--muted); margin: 6px 0 4px; }}

  .citations {{ margin: 0; padding-left: 18px; font-size: 11.5px; color: rgba(255,255,255,0.42); }}
  .citations li {{ margin-bottom: 8px; }}

  footer {{
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.10);
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
  }}
  .disclaimer {{ font-size: 11px; color: var(--faint); max-width: 620px; line-height: 1.6; }}
  .strapline {{ font-family: 'Archivo Black', sans-serif; font-size: 10px; letter-spacing: 0.1em; color: var(--faint); white-space: nowrap; }}

  .opportunity {{
    background: rgba(200,230,61,0.05);
    border: 1px solid rgba(200,230,61,0.3);
    border-radius: 14px;
    padding: 20px 22px;
    margin: -6px 0 32px;
  }}
  .opportunity .section-label {{ color: var(--lime); margin-bottom: 6px; }}
  .opportunity p {{ margin: 0; font-size: 13.5px; color: rgba(255,255,255,0.75); }}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="brand">
        <div class="mark"></div>
        <div>
          <div class="wordmark">DREAM RADAR</div>
          <div class="subwordmark">Fuelling Risk Briefing · Crystal Palace FC</div>
        </div>
      </div>
      <div class="header-right">
        <span class="pill">{esc(data_pill)}</span>
        <a class="pdf-btn" href="{esc(PDF_LINK)}">Download PDF ↓</a>
      </div>
    </header>

    <div class="eyebrow">Fuelling risk · situational awareness</div>
    <h1>Where the season gets hard.<br>And where it doesn't.</h1>
    <div class="credit">Prepared with {esc(NUTRITIONIST_NAME)} &middot; Crystal Palace FC</div>
    <p class="lede">Built entirely from Crystal Palace's own public fixture list, travel geography,
      climate and recent match load — not a generic seasonal template. Every finding below names the
      specific decision it bears on, with the evidence behind it.</p>

    <div class="section-title">This season's windows · {len(windows)} identified</div>
    {cards}

    <div class="opportunity">
      <div class="section-label">The same window is the opportunity</div>
      <p>Most clubs don't run a fuelling protocol tuned to their own specific pattern of congestion,
        travel and international duty. The ones that do gain a real edge exactly when it matters most.
        And these spikes sit on a season-long baseline: good habits early, protected availability through
        winter, a squad that finishes strong rather than fading.</p>
    </div>

    <footer>
      <p class="disclaimer">{esc(disclaimer)}</p>
      <div class="strapline">DREAM OS · v1</div>
    </footer>
  </div>
</body>
</html>
"""
    Path(OUT).write_text(html)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
