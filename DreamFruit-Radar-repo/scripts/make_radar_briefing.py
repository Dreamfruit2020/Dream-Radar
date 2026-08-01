#!/usr/bin/env python3
"""
Dream Radar — printed Fuelling Risk briefing.

Spec section 7, delivery format 2: "printed full-depth, handed over in
the quiet room at DFX step 5." Same dark, cinematic brand system as
scripts/make_concept_pdf.py — this is a prospect-facing artefact, not an
internal one, so it should look and feel like the same product family.

Runs on the illustrative Crystal Palace worked example
(scripts/worked_example.py) — every page carries a visible SAMPLE OUTPUT
marker so this is never mistaken for a real club's real data. Swap the
data source in worked_example.py once fixtures/climate/load/roster are
real; nothing in this script needs to change.

Carries a "Prepared with [Nutritionist Name]" credit line (spec section
3: "the shareable artifact makes the nutritionist look prepared — not
DreamFruit look clever," Connor's decision 1 Aug 2026 — this belongs in
the artifact itself). Pass a name as the third CLI arg; without one it
renders a visible placeholder rather than silently omitting the credit,
so it's obvious the field needs filling in before this goes to a club.

Usage: python3 scripts/make_radar_briefing.py [out.pdf] [font.ttf] ["Nutritionist Name"]
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from radar.fuelling_risk import tier_name  # noqa: E402
from worked_example import build_example_windows  # noqa: E402

DEFAULT_FONT = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "ArchivoBlack.ttf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "Dream-Radar-Briefing.pdf"
FONT = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_FONT)
NUTRITIONIST_NAME = sys.argv[3] if len(sys.argv) > 3 else "[Nutritionist Name]"
pdfmetrics.registerFont(TTFont("Archivo", FONT))

W, H = A4
INK = HexColor("#08040a")
MAGENTA = HexColor("#e02875")
PINK = HexColor("#ff4f9a")
LIME = HexColor("#c8e63d")
VIOLET = HexColor("#8b5cf6")
CYAN = HexColor("#4cc9f0")
GOLD = HexColor("#ffd166")
MAROON = HexColor("#2b0d16")
WHITE = HexColor("#ffffff")

TIER_COLOR = {"peak": MAGENTA, "elevated": GOLD, "standard": LIME}

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("Dream Radar — Fuelling Risk Briefing (Sample)")
c.setAuthor("DreamFruit")


def rgba(hexc, a):
    x = HexColor(hexc) if isinstance(hexc, str) else hexc
    return Color(x.red, x.green, x.blue, alpha=a)


def bg():
    c.setFillColor(INK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setStrokeColor(Color(1, 1, 1, alpha=0.03))
    c.setLineWidth(0.5)
    for x in range(0, int(W), 40):
        c.line(x, 0, x, H)
    for y in range(0, int(H), 40):
        c.line(0, y, W, y)
    for r, a in [(240, 0.05), (180, 0.05), (120, 0.06)]:
        c.setFillColor(Color(0.878, 0.157, 0.459, alpha=a))
        c.circle(60, H - 60, r, stroke=0, fill=1)
        c.setFillColor(Color(0.784, 0.902, 0.239, alpha=a * 0.7))
        c.circle(W - 40, 120, r, stroke=0, fill=1)


def tracked_width(text, font, size, track):
    return pdfmetrics.stringWidth(text, font, size) + track * max(len(text) - 1, 0)


def tracked(x, y, text, size, color, font="Archivo", track=2.2):
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(track)
    t.textOut(text)
    t.setCharSpace(0)  # Tc is graphics state — reset or it leaks into later draws
    c.drawText(t)


def tracked_c(cx, y, text, size, color, font="Archivo", track=2.2):
    tracked(cx - tracked_width(text, font, size, track) / 2, y, text, size, color, font, track)


def glass(x, y, w, h, r=14, glow=None):
    if glow:
        c.setFillColor(rgba(glow, 0.06))
        c.roundRect(x - 3, y - 3, w + 6, h + 6, r + 3, stroke=0, fill=1)
    c.setFillColor(Color(1, 1, 1, alpha=0.045))
    c.setStrokeColor(Color(1, 1, 1, alpha=0.13))
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)


def chip(x, y, text, color, size=8, pad=8, track=1.2):
    tw = tracked_width(text, "Archivo", size, track)
    w = tw + pad * 2
    h = size + 11
    c.setFillColor(rgba(color, 0.12))
    c.setStrokeColor(rgba(color, 0.55))
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, h / 2, stroke=1, fill=1)
    tracked(x + pad, y + 5.5, text, size, color, track=track)
    return w


def mark(x, y, s=1.0):
    c.saveState()
    c.translate(x, y)
    c.scale(s, s)
    c.setLineWidth(1.6)
    c.setStrokeColor(MAROON)
    c.setFillColor(LIME)
    p = c.beginPath(); p.moveTo(0, 16); p.lineTo(3.5, 7); p.lineTo(0, 9); p.lineTo(-3.5, 7); p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath(); p.moveTo(-8, 10); p.lineTo(-2, 5); p.lineTo(-8, 3); p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath(); p.moveTo(8, 10); p.lineTo(2, 5); p.lineTo(8, 3); p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.setFillColor(MAGENTA)
    p = c.beginPath()
    p.moveTo(0, 8)
    p.curveTo(9, 4, 11, -4, 8, -9)
    p.curveTo(5, -14, -5, -14, -8, -9)
    p.curveTo(-11, -4, -9, 4, 0, 8)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def header(page_label, club="CRYSTAL PALACE FC"):
    mark(46, H - 46, 1.05)
    tracked(62, H - 51, "DREAM RADAR", 12, WHITE, track=2.4)
    tracked(62, H - 62, f"FUELLING RISK BRIEFING · {club}", 5.5, Color(1, 1, 1, alpha=0.38), track=1.8)
    t = "SAMPLE OUTPUT — ILLUSTRATIVE DATA"
    tw = tracked_width(t, "Archivo", 6.2, 1.2)
    chip(W - 40 - tw - 16, H - 58, t, GOLD, size=6.2, track=1.2)
    c.setStrokeColor(Color(1, 1, 1, alpha=0.1))
    c.setLineWidth(0.75)
    c.line(40, H - 76, W - 40, H - 76)
    c.line(40, 46, W - 40, 46)
    tracked(40, 34, "BUILT FROM PUBLIC DATA. VALIDATED WITH YOUR OWN STAFF.", 6, Color(1, 1, 1, alpha=0.32), track=1.6)
    tracked(W - 74, 34, page_label, 6, Color(1, 1, 1, alpha=0.32), track=1.8)


def body_text(x, y, lines, size=8.5, leading=13, color=None, font="Helvetica"):
    c.setFont(font, size)
    c.setFillColor(color or Color(1, 1, 1, alpha=0.6))
    for i, ln in enumerate(lines):
        c.drawString(x, y - i * leading, ln)


def wrap(text, font, size, max_width):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if pdfmetrics.stringWidth(t, font, size) > max_width:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def fmt(d):
    return f"{d.day} {d.strftime('%b')}"


def severity_bar(x, y, w, h, severity, color):
    c.setFillColor(Color(1, 1, 1, alpha=0.08))
    c.roundRect(x, y, w, h, h / 2, stroke=0, fill=1)
    fw = max(w * severity, h)
    c.setFillColor(color)
    c.roundRect(x, y, fw, h, h / 2, stroke=0, fill=1)


# ═══════════════════════════════════════════════════════════════════
windows, travel_by_fixture, climate_by_fixture = build_example_windows()
windows = sorted(windows, key=lambda w: w.severity, reverse=True)
top = windows[0]
rest = windows[1:]

# ══ PAGE 1 — cover + season overview ═════════════════════════════
bg()
header("01 / 02")

tracked(40, H - 116, "FUELLING RISK · SITUATIONAL AWARENESS", 8, MAGENTA, track=2.6)
c.setFont("Archivo", 30)
c.setFillColor(WHITE)
c.drawString(38, H - 152, "Where the season gets hard.")
c.setFont("Archivo", 30)
c.drawString(38, H - 186, "And where it doesn't.")

# Credit line — spec section 3: this should read as prepared WITH the
# nutritionist, not a vendor report forwarded on their behalf. Deliberate
# placeholder text when no name is supplied, rather than silently
# omitting it, so an unfilled credit is obvious before this reaches a club.
tracked(40, H - 204, f"PREPARED WITH {NUTRITIONIST_NAME.upper()} · CRYSTAL PALACE FC", 8, LIME, track=1.6)

body_text(40, H - 234, [
    "Built entirely from Crystal Palace's own public fixture list, travel geography, climate",
    "and recent match load — not a generic seasonal template. Every finding on the pages",
    "that follow names the specific decision it bears on, with the evidence behind it.",
], size=9.5, leading=14.5)

# season strip — every window, ranked
tracked(40, H - 280, f"THIS SEASON'S WINDOWS · {len(windows)} IDENTIFIED", 7.5, Color(1, 1, 1, alpha=0.4), track=2.0)

row_h = 74
top_y = H - 300
for i, wnd in enumerate(windows):
    f = wnd.contributing_factors
    tier = str(f["tier"])
    col = TIER_COLOR.get(tier, LIME)
    ry = top_y - i * (row_h + 14) - row_h
    glass(40, ry, W - 80, row_h, glow=col if tier != "standard" else None)

    tracked(60, ry + row_h - 24, tier.upper(), 9, col, track=1.6)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(Color(1, 1, 1, alpha=0.55))
    c.drawString(60, ry + row_h - 40, f"{fmt(wnd.start)} – {fmt(wnd.end)}")

    severity_bar(60, ry + 16, 200, 7, wnd.severity, col)
    c.setFont("Archivo", 9)
    c.setFillColor(WHITE)
    c.drawString(268, ry + 15, f"{wnd.severity:.2f}")
    tracked(300, ry + 15.5, "SEVERITY", 5.8, Color(1, 1, 1, alpha=0.35), track=1.4)

    driver = str(f["dominant_driver"]).upper()
    tracked(380, ry + row_h - 24, "DRIVEN BY", 6, Color(1, 1, 1, alpha=0.35), track=1.6)
    tracked(380, ry + row_h - 38, driver, 8.5, col, track=1.2)

    conf = wnd.decision.confidence.value.upper()
    chip(380, ry + 12, conf, Color(1, 1, 1, alpha=0.7), size=6.5, track=1.2)

    if i == 0:
        right_edge = 40 + (W - 80) - 20
        lbl1, lbl2 = "FULL BRIEFING", "OVERLEAF →"
        tracked(right_edge - tracked_width(lbl1, "Archivo", 6, 1.4), ry + row_h - 24,
                lbl1, 6, Color(1, 1, 1, alpha=0.4), track=1.4)
        tracked(right_edge - tracked_width(lbl2, "Archivo", 7, 1.2), ry + row_h - 40,
                lbl2, 7, WHITE, track=1.2)

# risk-and-opportunity + season-arc framing (spec section 5) — belongs
# here as presentation copy, not inside the formula: these windows aren't
# just the hardest weeks, and they aren't the only weeks that matter.
fy = top_y - len(windows) * (row_h + 14) - 6
glass(40, fy - 70, W - 80, 70, glow=LIME)
tracked(58, fy - 26, "THE SAME WINDOW IS THE OPPORTUNITY", 7, LIME, track=1.8)
body_text(58, fy - 42, wrap(
    "Most clubs don't run a fuelling protocol tuned to their own specific pattern of congestion, "
    "travel and international duty. The ones that do gain a real edge exactly when it matters most. "
    "And these spikes sit on a season-long baseline: good habits early, protected availability through "
    "winter, a squad that finishes strong rather than fading.",
    "Helvetica", 8.2, W - 80 - 36,
), size=8.2, leading=12)

# fill the remaining space with what this is built from — reinforces
# depth without repeating the findings above
sy = fy - 96
tracked(40, sy, "WHAT THIS IS BUILT FROM", 7.5, Color(1, 1, 1, alpha=0.4), track=2.0)
sources = [
    ("FIXTURES", "Official competition calendars", MAGENTA),
    ("TRAVEL", "Venue geography + standard club practice", CYAN),
    ("CLIMATE", "Forecast, or historical average beyond 10 days", GOLD),
    ("MATCH LOAD", "Public minutes-played data, last 28 days", LIME),
    ("INTERNATIONAL DUTY", "FIFA calendar + published national squads", VIOLET),
]
sw = (W - 80 - 4 * 12) / 5
for i, (label, desc, scol) in enumerate(sources):
    sx = 40 + i * (sw + 12)
    sry = sy - 26 - 96
    glass(sx, sry, sw, 96, glow=scol)
    c.setFillColor(scol)
    c.circle(sx + 16, sry + 96 - 20, 3, stroke=0, fill=1)
    lines = wrap(label, "Archivo", 6.8, sw - 30)
    for j, ln in enumerate(lines):
        tracked(sx + 26, sry + 96 - 21 - j * 10, ln, 6.8, WHITE, track=0.8)
    dlines = wrap(desc, "Helvetica", 6.4, sw - 24)
    body_text(sx + 14, sry + 96 - 44, dlines, size=6.4, leading=9.5, color=Color(1, 1, 1, alpha=0.45))

tracked(40, 92, "ONE FORMULA. ONE INSIGHT. EVERY WINDOW EARNS ITS OWN EVIDENCE.", 8.5, Color(1, 1, 1, alpha=0.5), track=2.2)

c.showPage()

# ══ PAGE 2 — deep dive on the top window ═════════════════════════
bg()
header("02 / 02")

f = top.contributing_factors
tier = str(f["tier"])
col = TIER_COLOR.get(tier, LIME)

tracked(40, H - 112, "HIGHEST-DEMAND WINDOW THIS SEASON", 8, col, track=2.4)
c.setFont("Archivo", 24)
c.setFillColor(WHITE)
c.drawString(38, H - 144, f"{fmt(top.start)} – {fmt(top.end)}")

chip(40, H - 172, tier.upper(), col, size=8)
chip(40 + tracked_width(tier.upper(), "Archivo", 8, 1.2) + 24, H - 172,
     f"CONFIDENCE: {top.decision.confidence.value.upper()}", Color(1, 1, 1, alpha=0.75), size=7.5)

# severity gauge — value sits ABOVE the bar so it never competes for the
# same vertical band as the breakdown column alongside it
gx, gy, gw, gh = 40, H - 224, 300, 14
c.setFont("Archivo", 13)
c.setFillColor(WHITE)
c.drawString(gx, gy + gh + 12, f"{top.severity:.2f} / 1.00 SEVERITY")
severity_bar(gx, gy, gw, gh, top.severity, col)
c.setFont("Helvetica", 7)
c.setFillColor(Color(1, 1, 1, alpha=0.4))
c.drawString(gx, gy - 12, f"On confirmed fixtures alone: {f['severity_confirmed_only']:.2f}")

# finding
glass(40, H - 378, 330, 130, glow=col)
tracked(58, H - 278, "FINDING", 7.5, Color(1, 1, 1, alpha=0.4), track=2.2)
lines = wrap(top.decision.finding, "Helvetica", 8.6, 296)
body_text(58, H - 296, lines, size=8.6, leading=12.6)

# decision
glass(40, H - 488, 330, 100, glow=VIOLET)
tracked(58, H - 404, "THE DECISION THIS BEARS ON", 7.5, VIOLET, track=2.0)
lines = wrap(top.decision.decision_question, "Helvetica-Oblique", 9.2, 296)
body_text(58, H - 422, lines, size=9.2, leading=13.5, color=Color(1, 1, 1, alpha=0.88), font="Helvetica-Oblique")

# players + matrix hook
py = H - 508
if top.decision.players_of_note:
    tracked(40, py, "PLAYERS OF NOTE", 7, Color(1, 1, 1, alpha=0.4), track=1.8)
    x = 40
    for p in top.decision.players_of_note:
        x += chip(x, py - 24, p, LIME, size=7.5) + 8
    py -= 46
tracked(40, py, "GOES STRAIGHT INTO YOUR PERFORMANCE MATRIX SESSION", 6.3, Color(1, 1, 1, alpha=0.4), track=1.4)
py -= 46

# season-context recap — the calmer window(s) this page doesn't dive into,
# so the deep-dive page still carries the "not just one alarming data
# point" contrast the season-arc framing (spec section 5) asks for
if rest:
    c.setStrokeColor(Color(1, 1, 1, alpha=0.1))
    c.setLineWidth(0.75)
    c.line(40, py, 370, py)
    py -= 24
    tracked(40, py, "ALSO ON THE RADAR THIS SEASON", 7.5, Color(1, 1, 1, alpha=0.4), track=1.8)
    py -= 22
    for wnd in rest:
        wf = wnd.contributing_factors
        wtier = str(wf["tier"])
        wcol = TIER_COLOR.get(wtier, LIME)
        rh = 58
        glass(40, py - rh, 330, rh)
        tracked(58, py - 22, wtier.upper(), 7.5, wcol, track=1.4)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(Color(1, 1, 1, alpha=0.55))
        c.drawString(58, py - 36, f"{fmt(wnd.start)} - {fmt(wnd.end)}")
        severity_bar(210, py - rh + 18, 90, 6, wnd.severity, wcol)
        c.setFont("Archivo", 8)
        c.setFillColor(WHITE)
        c.drawString(310, py - rh + 15, f"{wnd.severity:.2f}")
        py -= rh + 12

# ── right column: component breakdown ──
rx = 396
tracked(rx, H - 112, "SCORE BREAKDOWN", 7.5, Color(1, 1, 1, alpha=0.4), track=2.0)

components = [
    ("CONGESTION", f["congestion"], MAGENTA, 4.0),
    ("CONTIGUITY", f["contiguity"], PINK, 2.0),
    ("TRAVEL", f["travel"], CYAN, 2.0),
    ("CLIMATE", f["climate"], GOLD, 1.5),
    ("INTERNATIONAL", f["international"], VIOLET, 2.0),
]
by = H - 140
bar_w = W - 40 - rx - 70
for name, val, bcol, ref in components:
    c.setFont("Helvetica", 7.2)
    c.setFillColor(Color(1, 1, 1, alpha=0.55))
    c.drawString(rx, by, name)
    c.setFillColor(Color(1, 1, 1, alpha=0.08))
    c.roundRect(rx, by - 14, bar_w, 8, 4, stroke=0, fill=1)
    frac = min(val / ref, 1.0) if ref else 0.0
    if frac > 0:
        c.setFillColor(bcol)
        c.roundRect(rx, by - 14, max(bar_w * frac, 6), 8, 4, stroke=0, fill=1)
    c.setFont("Archivo", 7.5)
    c.setFillColor(WHITE)
    c.drawString(rx + bar_w + 8, by - 13, f"{val:.2f}")
    by -= 30

c.setFont("Helvetica", 7.2)
c.setFillColor(Color(1, 1, 1, alpha=0.55))
c.drawString(rx, by, "LOAD MULTIPLIER")
c.setFont("Archivo", 9)
c.setFillColor(LIME)
c.drawString(rx, by - 16, f"×{f['load_multiplier']:.3f}")
by -= 42

c.setStrokeColor(Color(1, 1, 1, alpha=0.1))
c.setLineWidth(0.75)
c.line(rx, by, W - 40, by)
by -= 20

tracked(rx, by, f"{int(f['elevated_days_calendar'])} of {int(f['frame_days'])} days elevated", 8, WHITE, track=0.6)
by -= 16
c.setFont("Helvetica", 7.4)
c.setFillColor(Color(1, 1, 1, alpha=0.5))
c.drawString(rx, by, f"Longest run with no reset day: {int(f['longest_elevated_run_days'])} days")
by -= 30

# citations
tracked(rx, by, "EVIDENCE BASE", 7, Color(1, 1, 1, alpha=0.4), track=1.8)
by -= 16
for cite in top.decision.citations:
    clines = wrap(cite, "Helvetica", 6.7, W - 40 - rx)
    c.setFont("Helvetica", 6.7)
    c.setFillColor(Color(1, 1, 1, alpha=0.42))
    for j, ln in enumerate(clines):
        c.drawString(rx, by, ("– " if j == 0 else "  ") + ln)
        by -= 9.5
    by -= 6

# disclaimer
glass(40, 60, W - 80, 40)
body_text(56, 88, [
    "SAMPLE OUTPUT: fixture dates, opponents, climate readings and player minutes on this page are",
    "illustrative, not a live pull. The scoring formula and citations are real — see docs/radar-scoring-design.md.",
], size=6.8, leading=10, color=Color(1, 1, 1, alpha=0.4))

c.showPage()
c.save()
print("wrote", OUT)
