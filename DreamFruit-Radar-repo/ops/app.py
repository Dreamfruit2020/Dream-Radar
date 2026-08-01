#!/usr/bin/env python3
"""
Dream Radar — internal ops interface (prototype).

Answers a real question Connor asked: does generating a club's Radar
materials require going through Claude (or an engineer) every time, or
can it be operated like a website? Until now, the honest answer was "you
need to run Python scripts by hand." This is a first, working step
toward "no" — a local web page with a Generate button that runs the
existing, already-tested pipeline (scripts/make_radar_briefing.py,
make_radar_teaser.py, make_radar_shareable.py) and hands back files,
with no Python or terminal involved for whoever's using the page.

WHAT THIS IS: a working prototype, run locally, proving the interaction
model — click a button, get materials, no engineer needed. The
underlying scoring formula and generators are real; fixtures, roster and
recent match load pull from API-Football when API_FOOTBALL_KEY is set
(radar/api_football.py), climate from Open-Meteo (keyless), and
international call-ups from a manually maintained file
(radar/manual_call_ups.json) — see radar/README.md for exactly what's
real vs. still-mock-fallback.

WHAT THIS IS NOT YET: deployed, or multi-club. There's one club wired up
(Crystal Palace) and one dataset behind the button. Once club/date
become meaningful inputs, this same Flask app is the right shape to
extend (add form fields, thread them into radar.build.build_for_club()).

DEPLOYMENT: Netlify's serverless functions are JS/TS-first with no
first-class Python support (checked their docs directly, Aug 2026), so
this stays a normal Python web app rather than being ported to Netlify
Functions — a rewrite of the whole generation pipeline (reportlab PDFs,
the scoring formula, the API clients) wasn't worth it just to live on
one platform. Decision: keep this Flask app as-is, host it on a small
always-on Python host (Render or Fly.io) instead. Procfile included for
that. Static/frontend pieces (like the Performance Matrix wizard) can
still live on Netlify separately — those are genuinely static builds.

Run:
    pip install -r requirements.txt
    python3 ops/app.py
    open http://127.0.0.1:5057
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, request, send_from_directory, url_for

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
OUTPUT_ROOT = ROOT / "ops" / "generated"
FONT = str(ROOT / "assets" / "fonts" / "ArchivoBlack.ttf")

app = Flask(__name__)

BASE_CSS = """
  :root { --ink:#08040a; --magenta:#e02875; --lime:#c8e63d; --gold:#ffd166; --white:#fff; --muted:rgba(255,255,255,0.55); }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--ink); color:var(--white); font-family:-apple-system,'Segoe UI',sans-serif;
    min-height:100vh; display:flex; flex-direction:column; align-items:center; padding:60px 24px; }
  .wrap { max-width: 640px; width:100%; }
  header { display:flex; align-items:center; gap:12px; margin-bottom:40px; }
  .mark { width:28px; height:28px; background:var(--magenta);
    clip-path: polygon(50% 0%, 80% 35%, 100% 55%, 78% 60%, 62% 100%, 38% 100%, 22% 60%, 0% 55%, 20% 35%); }
  .wordmark { font-weight:800; letter-spacing:0.08em; font-size:15px; }
  .subwordmark { font-size:10px; letter-spacing:0.1em; color:var(--muted); text-transform:uppercase; margin-top:2px; }
  h1 { font-size: 26px; margin: 0 0 10px; }
  p.lede { color: var(--muted); font-size: 14px; line-height:1.6; margin-bottom: 28px; }
  .card { background:rgba(255,255,255,0.045); border:1px solid rgba(255,255,255,0.13); border-radius:14px; padding:24px; margin-bottom:16px; }
  label { display:block; font-size:11px; letter-spacing:0.08em; text-transform:uppercase; color:var(--muted); margin-bottom:8px; }
  select, button { font-family:inherit; }
  select { width:100%; padding:10px 12px; border-radius:8px; background:rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.2); color:var(--white); font-size:14px; margin-bottom:18px; }
  button { width:100%; padding:14px; border-radius:999px; border:none; background:var(--white); color:var(--ink);
    font-weight:800; letter-spacing:0.04em; font-size:14px; cursor:pointer; }
  button:hover { opacity: 0.9; }
  .note { font-size:12px; color:var(--muted); margin-top:14px; line-height:1.6; }
  .pill { display:inline-block; border:1px solid var(--gold); color:var(--gold); background:rgba(255,209,102,0.1);
    font-size:10px; letter-spacing:0.08em; text-transform:uppercase; padding:4px 10px; border-radius:999px; margin-bottom:18px; }
  .result-row { display:flex; align-items:center; justify-content:space-between; padding:14px 0; border-bottom:1px solid rgba(255,255,255,0.08); }
  .result-row:last-child { border-bottom:none; }
  .result-row a { color:var(--lime); text-decoration:none; font-weight:700; font-size:13px; }
  .result-row a:hover { text-decoration:underline; }
  .stat { display:flex; gap:24px; margin: 4px 0 22px; }
  .stat div b { display:block; font-size:22px; }
  .stat div span { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:0.06em; }
  .back { color: var(--muted); font-size: 13px; text-decoration:none; }
"""

HEADER = """
<header>
  <div class="mark"></div>
  <div><div class="wordmark">DREAM RADAR — OPS</div><div class="subwordmark">Internal generation tool · prototype</div></div>
</header>
"""


@app.route("/")
def index():
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Dream Radar — Ops</title><style>{BASE_CSS}</style></head><body><div class="wrap">
{HEADER}
<span class="pill">Prototype — one dataset, no live data yet</span>
<h1>Generate this week's materials</h1>
<p class="lede">Runs the existing, tested pipeline and hands back the teaser, printed briefing and
shareable page — no Python, no terminal. Right now there's one dataset behind this button (the
illustrative Crystal Palace example); once real fixture/load/roster/international sources are wired
in (see <code>radar/README.md</code>), club and visit date become real inputs here instead of a
fixed sample.</p>
<div class="card">
  <form method="post" action="/generate">
    <label>Club</label>
    <select disabled><option>Crystal Palace FC (pilot club)</option></select>
    <label>Nutritionist name</label>
    <input type="text" name="nutritionist_name" placeholder="e.g. Sam Whitfield"
      style="width:100%;padding:10px 12px;border-radius:8px;background:rgba(255,255,255,0.06);
      border:1px solid rgba(255,255,255,0.2);color:#fff;font-size:14px;margin-bottom:18px;">
    <button type="submit">Generate materials</button>
  </form>
  <p class="note">Printed for the "Prepared with&nbsp;&hellip;" credit on the briefing and shareable
    page (spec section 3 — this belongs in the artifact, not a covering email). Leave blank to
    generate with a visible placeholder instead. This calls scripts/make_radar_briefing.py,
    make_radar_teaser.py and make_radar_shareable.py directly — the same generators already
    verified in docs/radar-scoring-design.md and docs/radar-guardrails-review.md. Every file is
    marked SAMPLE OUTPUT.</p>
</div>
</div></body></html>"""


@app.route("/generate", methods=["POST"])
def generate():
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = OUTPUT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Credit line, spec section 3 — belongs in the artifact (Connor's
    # decision). Not passed to the teaser: that's the live-narrated step-4
    # opener, before any "prepared with" relationship exists yet.
    nutritionist_name = (request.form.get("nutritionist_name") or "").strip() or "[Nutritionist Name]"

    jobs = [
        ("Dream-Radar-Teaser.html", SCRIPTS / "make_radar_teaser.py", []),
        ("Dream-Radar-Briefing.pdf", SCRIPTS / "make_radar_briefing.py", [FONT, nutritionist_name]),
        ("Dream-Radar-Shareable.html", SCRIPTS / "make_radar_shareable.py",
         ["Dream-Radar-Briefing.pdf", nutritionist_name]),
    ]

    errors = []
    for filename, script, extra_args in jobs:
        out_path = out_dir / filename
        result = subprocess.run(
            [sys.executable, str(script), str(out_path), *extra_args],
            capture_output=True, text=True, cwd=str(ROOT), timeout=60,
        )
        if result.returncode != 0 or not out_path.exists():
            errors.append(f"{filename}: {result.stderr.strip()[-300:]}")

    if errors:
        return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Generation failed</title><style>{BASE_CSS}</style></head><body><div class="wrap">
{HEADER}<h1>Generation failed</h1>
<div class="card"><pre style="white-space:pre-wrap;color:#ff8fae;font-size:12px">{chr(10).join(errors)}</pre></div>
<a class="back" href="/">&larr; back</a></div></body></html>""", 500

    return redirect(url_for("results", run_id=run_id))


@app.route("/r/<run_id>")
def results(run_id: str):
    out_dir = OUTPUT_ROOT / run_id
    if not out_dir.is_dir():
        return "Run not found", 404

    # Pull a quick summary straight from the same illustrative dataset the
    # generators use, so the page shows something more useful than a bare
    # file list.
    sys.path.insert(0, str(SCRIPTS))
    from worked_example import build_example_windows  # noqa: E402

    windows, _, _ = build_example_windows()
    windows = sorted(windows, key=lambda w: w.severity, reverse=True)
    top = windows[0]
    f = top.contributing_factors

    files_html = "".join(
        f'<div class="result-row"><span>{name}</span><a href="/file/{run_id}/{name}">Open / download &rarr;</a></div>'
        for name in ["Dream-Radar-Teaser.html", "Dream-Radar-Briefing.pdf", "Dream-Radar-Shareable.html"]
    )

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Materials ready</title><style>{BASE_CSS}</style></head><body><div class="wrap">
{HEADER}
<span class="pill">Sample output — illustrative data</span>
<h1>Materials ready</h1>
<div class="stat">
  <div><b>{len(windows)}</b><span>windows found</span></div>
  <div><b>{top.severity:.2f}</b><span>top severity</span></div>
  <div><b>{str(f['tier']).upper()}</b><span>tier</span></div>
</div>
<div class="card">{files_html}</div>
<p class="note">Run id: {run_id} &middot; generated by ops/app.py, calling the same scripts you'd run by
hand — nothing here is a separate code path.</p>
<a class="back" href="/">&larr; generate again</a>
</div></body></html>"""


@app.route("/file/<run_id>/<filename>")
def serve_file(run_id: str, filename: str):
    out_dir = OUTPUT_ROOT / run_id
    return send_from_directory(out_dir, filename)


OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    # Local dev only. In production this module is served by gunicorn
    # (see Procfile) — Render/Fly.io inject PORT and expect a bind to
    # 0.0.0.0, not the loopback-only address used for local testing.
    import os

    port = int(os.environ.get("PORT", 5057))
    app.run(host="0.0.0.0", port=port, debug=False)
