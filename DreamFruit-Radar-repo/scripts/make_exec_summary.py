#!/usr/bin/env python3
"""One-page internal exec summary + sales-process flow diagram for
Dream Radar + Dream Performance Matrix. Light background, brand accents —
built for quick internal sharing (email/Slack), not the cinematic
prospect-facing style used elsewhere in this repo."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys
from pathlib import Path

DEFAULT_FONT = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "ArchivoBlack.ttf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "Dream-Radar-Matrix-Exec-Summary.pdf"
FONT = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_FONT)
pdfmetrics.registerFont(TTFont("Archivo", FONT))

W, H = A4
INK = HexColor("#141014")
SUB = HexColor("#5c5560")
MAGENTA = HexColor("#e02875")
LIME_D = HexColor("#5c8a12")   # darker lime for readable text on white
LIME_BG = HexColor("#c8e63d")
VIOLET = HexColor("#8b5cf6")
GOLD = HexColor("#b8860b")
LINE = HexColor("#e4e0e6")
PAPER = HexColor("#fcfaf9")

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("Dream Radar + Performance Matrix — Executive Summary")
c.setAuthor("DreamFruit")


def tracked_width(text, font, size, track):
    return pdfmetrics.stringWidth(text, font, size) + track * max(len(text) - 1, 0)


def tracked(x, y, text, size, color, font="Archivo", track=1.6):
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(track)
    t.textOut(text)
    t.setCharSpace(0)
    c.drawText(t)


def body(x, y, lines, size=9.5, leading=14, color=None, font="Helvetica"):
    c.setFont(font, size)
    c.setFillColor(color or SUB)
    for i, ln in enumerate(lines):
        c.drawString(x, y - i * leading, ln)


def wrap(text, font, size, max_width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def mark(x, y, s=1.0):
    c.saveState()
    c.translate(x, y)
    c.scale(s, s)
    c.setLineWidth(1.3)
    c.setStrokeColor(INK)
    c.setFillColor(LIME_BG)
    p = c.beginPath(); p.moveTo(0, 14); p.lineTo(3, 6); p.lineTo(0, 8); p.lineTo(-3, 6); p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath(); p.moveTo(-7, 9); p.lineTo(-2, 4); p.lineTo(-7, 2); p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath(); p.moveTo(7, 9); p.lineTo(2, 4); p.lineTo(7, 2); p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.setFillColor(MAGENTA)
    p = c.beginPath()
    p.moveTo(0, 7)
    p.curveTo(8, 3, 10, -4, 7, -8)
    p.curveTo(4, -12, -4, -12, -7, -8)
    p.curveTo(-10, -4, -8, 3, 0, 7)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def badge(x, y, text, color, size=6.6):
    w = tracked_width(text, "Archivo", size, 0.8) + 14
    h = 13
    c.setFillColor(Color(color.red, color.green, color.blue, alpha=0.13))
    c.setStrokeColor(color)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, h / 2, stroke=1, fill=1)
    tracked(x + 7, y + 4, text, size, color, track=0.8)
    return w


# ── background ──────────────────────────────────────────────
c.setFillColor(PAPER)
c.rect(0, 0, W, H, stroke=0, fill=1)

# ── header ──────────────────────────────────────────────────
mark(46, H - 44, 1.0)
tracked(60, H - 49, "DREAMFRUIT", 11.5, INK, track=2.0)
tracked(60, H - 60, "INTERNAL — DREAM OS PROGRAMME", 5.6, SUB, track=1.8)
tracked(W - 40 - tracked_width("19 JUL 2026", "Helvetica", 7.5, 0), H - 50, "19 JUL 2026", 7.5, SUB, font="Helvetica", track=0)
c.setStrokeColor(LINE)
c.setLineWidth(0.75)
c.line(40, H - 72, W - 40, H - 72)

c.setFont("Archivo", 19)
c.setFillColor(INK)
c.drawString(38, H - 104, "Dream Radar + Performance Matrix")
tracked(40, H - 122, "EXECUTIVE SUMMARY", 8.5, MAGENTA, track=2.4)

# ── summary paragraphs ──────────────────────────────────────
summary = [
    ("What it is",
     "Two connected tools that turn a DreamFruit visit into proof of real intelligence, not just a "
     "tasting session. Dream Radar is a short briefing built entirely from public data about a club's "
     "own season — fixtures, travel, climate, squad workload. Dream Performance Matrix is the deeper, "
     "consultative session that follows immediately after, producing a real confidential brief the club "
     "can act on."),
    ("Why it matters",
     "Radar proves depth in minutes, before we've even said what we do — positioning DreamFruit as a "
     "natural health intelligence company, not a drinks brand. The Matrix then does the real work, live, "
     "while that trust is highest, so the club leaves the visit with something tangible rather than a "
     "promise of one."),
    ("Where it fits",
     "Both are built directly into the existing DreamFruit Experience sales process — see the flow "
     "opposite. Nothing about how DFX visits are sold changes; this adds substance to the moments that "
     "already exist."),
    ("Status",
     "Product spec complete. Pilot club confirmed: Crystal Palace FC. Technical build underway — the "
     "core data pipeline is scaffolded and verified; the next step is finalising the scoring logic "
     "before this touches a real club visit."),
]

y = H - 156
label_w = 108
for label, text in summary:
    tracked(40, y, label.upper(), 7.5, INK, track=1.4)
    lines = wrap(text, "Helvetica", 9, 300)
    body(40, y - 15, lines, size=9, leading=12.5)
    y -= 15 + len(lines) * 12.5 + 14

# ── divider ─────────────────────────────────────────────────
c.setStrokeColor(LINE)
c.line(40, y + 2, W - 40, y + 2)

# ── flow diagram ────────────────────────────────────────────
tracked(40, y - 20, "HOW IT MAPS TO THE SALES PROCESS", 8.5, MAGENTA, track=2.2)

steps = [
    ("1–3", "Outreach · sales doc · nurture", None),
    ("4", "Meeting — pitch the DFX", "RADAR"),
    ("5", "DreamFruit Experience — stand + quiet-room sit-down", "RADAR + MATRIX"),
    ("6", "Wrap-up video", None),
    ("7", "Follow-up — Club Plan / Stay On-Demand", "RADAR + MATRIX BRIEF"),
    ("8", "Buying & testing — ongoing", "MATRIX (revisited)"),
]

box_h = 30
gap = 9
top = y - 44
box_x = 40
box_w = 300

for i, (num, label, tag) in enumerate(steps):
    by = top - i * (box_h + gap)
    highlighted = tag is not None
    c.setFillColor(Color(0.878, 0.157, 0.459, 0.05) if highlighted else Color(0, 0, 0, 0.015))
    c.setStrokeColor(MAGENTA if highlighted else LINE)
    c.setLineWidth(1.1 if highlighted else 0.75)
    c.roundRect(box_x, by - box_h, box_w, box_h, 8, stroke=1, fill=1)

    # step number circle
    cx, cy = box_x + 18, by - box_h / 2
    c.setFillColor(INK if highlighted else SUB)
    c.circle(cx, cy, 10, stroke=0, fill=1)
    c.setFillColor(PAPER)
    c.setFont("Archivo", 8)
    tw = pdfmetrics.stringWidth(num, "Archivo", 8)
    c.drawString(cx - tw / 2, cy - 3, num)

    c.setFont("Helvetica-Bold" if highlighted else "Helvetica", 8.6)
    c.setFillColor(INK if highlighted else SUB)
    c.drawString(box_x + 36, by - box_h / 2 - 3, label)

    # connector arrow to next box
    if i < len(steps) - 1:
        ax = box_x + box_w / 2
        c.setStrokeColor(LINE)
        c.setLineWidth(1)
        c.line(ax, by - box_h, ax, by - box_h - gap)

    # badge to the right
    if tag:
        color = MAGENTA if "MATRIX" not in tag or "RADAR" in tag and "MATRIX" not in tag.split(" + MATRIX")[0] else LIME_D
        # simpler: pick color by content
        if tag == "RADAR":
            bcolor = MAGENTA
        elif "BRIEF" in tag or tag == "RADAR + MATRIX":
            bcolor = VIOLET
        else:
            bcolor = LIME_D
        badge(box_x + box_w + 14, by - box_h / 2 - 6, tag, bcolor)

bottom = top - (len(steps) - 1) * (box_h + gap) - box_h

# ── legend ──────────────────────────────────────────────────
ly = bottom - 26
tracked(40, ly, "LEGEND", 7, SUB, track=1.6)
lx = 40
for text, col in [("RADAR", MAGENTA), ("MATRIX", LIME_D), ("RADAR + MATRIX / BRIEF", VIOLET)]:
    w = badge(lx, ly - 18, text, col)
    lx += w + 10

# ── footer ──────────────────────────────────────────────────
c.setStrokeColor(LINE)
c.line(40, 46, W - 40, 46)
tracked(40, 34, "CONFIDENTIAL — INTERNAL USE", 6, SUB, track=1.6)
tracked(W - 40 - tracked_width("DREAM OS · v1", "Archivo", 6, 1.6), 34, "DREAM OS · v1", 6, SUB, track=1.6)

c.showPage()
c.save()
print("wrote", OUT)
