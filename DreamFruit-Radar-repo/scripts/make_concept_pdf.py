#!/usr/bin/env python3
"""DragonAid example drink concept sheet — Dreamfruit dark theme, A4, 2 pages."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys
from pathlib import Path

DEFAULT_FONT = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "ArchivoBlack.ttf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "DragonAid-Concept.pdf"
FONT = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_FONT)
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

def rgba(hexc, a):
    c = HexColor(hexc)
    return Color(c.red, c.green, c.blue, alpha=a)

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("DragonAid ACTIVATE AM — Example Drink Concept")
c.setAuthor("Dreamfruit")


def bg():
    c.setFillColor(INK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # telemetry grid
    c.setStrokeColor(Color(1, 1, 1, alpha=0.03))
    c.setLineWidth(0.5)
    for x in range(0, int(W), 40):
        c.line(x, 0, x, H)
    for y in range(0, int(H), 40):
        c.line(0, y, W, y)
    # glow orbs
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
        c.setFillColor(Color(glow.red, glow.green, glow.blue, alpha=0.06))
        c.roundRect(x - 3, y - 3, w + 6, h + 6, r + 3, stroke=0, fill=1)
    c.setFillColor(Color(1, 1, 1, alpha=0.045))
    c.setStrokeColor(Color(1, 1, 1, alpha=0.13))
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)


def chip(x, y, text, color, size=8, pad=8, track=1.2):
    tw = pdfmetrics.stringWidth(text, "Archivo", size) + track * max(len(text) - 1, 0)
    w = tw + pad * 2
    h = size + 11
    c.setFillColor(Color(color.red, color.green, color.blue, alpha=0.10))
    c.setStrokeColor(Color(color.red, color.green, color.blue, alpha=0.5))
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, h / 2, stroke=1, fill=1)
    tracked(x + pad, y + 5.5, text, size, color, track=track)
    return w


def mark(x, y, s=1.0):
    """Simplified Dreamfruit dragonfruit mark."""
    c.saveState()
    c.translate(x, y)
    c.scale(s, s)
    c.setLineWidth(1.6)
    c.setStrokeColor(MAROON)
    # lime spikes
    c.setFillColor(LIME)
    p = c.beginPath(); p.moveTo(0, 16); p.lineTo(3.5, 7); p.lineTo(0, 9); p.lineTo(-3.5, 7); p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath(); p.moveTo(-8, 10); p.lineTo(-2, 5); p.lineTo(-8, 3); p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath(); p.moveTo(8, 10); p.lineTo(2, 5); p.lineTo(8, 3); p.close()
    c.drawPath(p, stroke=1, fill=1)
    # magenta fruit
    c.setFillColor(MAGENTA)
    p = c.beginPath()
    p.moveTo(0, 8)
    p.curveTo(9, 4, 11, -4, 8, -9)
    p.curveTo(5, -14, -5, -14, -8, -9)
    p.curveTo(-11, -4, -9, 4, 0, 8)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def header(page_label):
    mark(46, H - 46, 1.05)
    tracked(62, H - 51, "DREAMFRUIT", 12, WHITE, track=2.4)
    tracked(62, H - 62, "PERFORMANCE MATRIX", 5.5, Color(1, 1, 1, alpha=0.38), track=2.2)
    t = "CONFIDENTIAL CONCEPT"
    tw = pdfmetrics.stringWidth(t, "Archivo", 6.5) + 1.4 * (len(t) - 1)
    chip(W - 40 - tw - 16, H - 58, t, GOLD, size=6.5)
    c.setStrokeColor(Color(1, 1, 1, alpha=0.1))
    c.setLineWidth(0.75)
    c.line(40, H - 76, W - 40, H - 76)
    # footer
    c.line(40, 46, W - 40, 46)
    tracked(40, 34, "POWERING UP ELITE ATHLETES THROUGH NATURE", 6, Color(1, 1, 1, alpha=0.32), track=1.8)
    tracked(W - 74, 34, page_label, 6, Color(1, 1, 1, alpha=0.32), track=1.8)


def body_text(x, y, lines, size=8.5, leading=13, color=None, font="Helvetica"):
    c.setFont(font, size)
    c.setFillColor(color or Color(1, 1, 1, alpha=0.6))
    for i, ln in enumerate(lines):
        c.drawString(x, y - i * leading, ln)


def bottle(x, y, h):
    """DragonAid bottle, brand-accurate: white cap, arc badge, arrow, vertical type, spikes."""
    w = h * 0.42
    bx, by = x - w / 2, y
    c.saveState()
    # glow
    c.setFillColor(Color(0.878, 0.157, 0.459, alpha=0.10))
    c.ellipse(bx - 26, by - 14, bx + w + 26, by + h * 0.92, stroke=0, fill=1)
    # cap
    ch = h * 0.09
    c.setFillColor(HexColor("#efefe9"))
    c.setStrokeColor(HexColor("#c9c9c2"))
    c.setLineWidth(1)
    c.roundRect(x - w * 0.30, by + h * 0.86, w * 0.60, ch, 3, stroke=1, fill=1)
    c.setStrokeColor(Color(0, 0, 0, alpha=0.10))
    for i in range(1, 6):
        lx = x - w * 0.30 + i * (w * 0.60 / 6)
        c.line(lx, by + h * 0.865, lx, by + h * 0.86 + ch - 2)
    # neck
    c.setFillColor(Color(1, 1, 1, alpha=0.08))
    c.setStrokeColor(Color(1, 1, 1, alpha=0.2))
    c.rect(x - w * 0.24, by + h * 0.80, w * 0.48, h * 0.06, stroke=1, fill=1)
    # body with gradient liquid
    bodyh = h * 0.80
    p = c.beginPath()
    p.roundRect(bx, by, w, bodyh, w * 0.16)
    c.saveState()
    c.clipPath(p, stroke=0, fill=0)
    c.linearGradient(x, by, x, by + bodyh, (PINK, MAGENTA), extend=True)
    # DREAMFRUIT badge
    c.setFillColor(HexColor("#f7f7f2"))
    c.setStrokeColor(MAROON)
    c.setLineWidth(1.2)
    c.roundRect(x - w * 0.31, by + bodyh * 0.855, w * 0.62, bodyh * 0.055, 4, stroke=1, fill=1)
    tracked_c(x, by + bodyh * 0.868, "DREAMFRUIT", 4.6, HexColor("#141014"), track=0.8)
    # two-tone arrow
    def arrow(dx, col, alpha):
        c.setFillColor(Color(col.red, col.green, col.blue, alpha=alpha))
        ax = x + dx
        p2 = c.beginPath()
        p2.moveTo(ax, by + bodyh * 0.80)
        p2.lineTo(ax - w * 0.26, by + bodyh * 0.60)
        p2.lineTo(ax - w * 0.09, by + bodyh * 0.635)
        p2.lineTo(ax - w * 0.09, by + bodyh * 0.16)
        p2.lineTo(ax + w * 0.09, by + bodyh * 0.16)
        p2.lineTo(ax + w * 0.09, by + bodyh * 0.635)
        p2.lineTo(ax + w * 0.26, by + bodyh * 0.60)
        p2.close()
        c.drawPath(p2, stroke=0, fill=1)
    arrow(-w * 0.06, LIME, 0.85)
    arrow(w * 0.05, HexColor("#ff2d6f"), 0.9)
    # vertical DRAGONAID
    c.saveState()
    c.translate(x, by + bodyh * 0.47)
    c.rotate(90)
    t = "DRAGONAID"
    fs = w * 0.185
    tracked(-tracked_width(t, "Archivo", fs, 1.2) / 2, -w * 0.066, t, fs, WHITE, track=1.2)
    c.restoreState()
    # POWER UP
    tracked_c(x, by + bodyh * 0.095, "POWER UP", w * 0.085, WHITE, track=1.0)
    # spike rows
    n = 7
    sw = w / n
    for i in range(n):
        sx = bx + i * sw
        c.setFillColor(LIME if i % 2 else HexColor("#7cc832"))
        c.setStrokeColor(MAROON)
        c.setLineWidth(0.8)
        p3 = c.beginPath()
        p3.moveTo(sx, by)
        p3.lineTo(sx + sw / 2, by + h * 0.055)
        p3.lineTo(sx + sw, by)
        p3.close()
        c.drawPath(p3, stroke=1, fill=1)
        if i < n - 1:
            c.setFillColor(PINK if i % 2 else MAGENTA)
            p4 = c.beginPath()
            p4.moveTo(sx + sw / 2, by)
            p4.lineTo(sx + sw, by + h * 0.045)
            p4.lineTo(sx + sw * 1.5, by)
            p4.close()
            c.drawPath(p4, stroke=1, fill=1)
    # sheen
    c.setFillColor(Color(1, 1, 1, alpha=0.22))
    c.roundRect(bx + w * 0.10, by + h * 0.10, w * 0.055, bodyh * 0.78, 3, stroke=0, fill=1)
    c.restoreState()
    # glass outline
    c.setStrokeColor(Color(1, 1, 1, alpha=0.25))
    c.setLineWidth(1.2)
    c.roundRect(bx, by, w, bodyh, w * 0.16, stroke=1, fill=0)
    c.restoreState()


# ══ PAGE 1 — the drink ═══════════════════════════════════
bg()
header("01 / 02")

tracked(40, H - 116, "DRAGONAID PRODUCT CONCEPT · EXAMPLE", 8, MAGENTA, track=2.6)
c.setFont("Archivo", 34)
c.setFillColor(WHITE)
c.drawString(38, H - 156, "ACTIVATE AM™")
chip(40, H - 186, "POWER UP FAMILY", MAGENTA, size=7.5)
chip(148, H - 186, "MORNING / PRE-TRAINING", LIME, size=7.5)

body_text(40, H - 216, [
    "An example of what a Dream drink can be. One drink from the DragonAid",
    "range, built on a natural fruit matrix and charged with an ultra-fine",
    "emulsion of performance bioactives.",
], size=9.5, leading=14.5)

# bottle right
bottle(W - 130, 180, 420)

# purpose card
glass(40, H - 450, 330, 180, glow=MAGENTA)
tracked(58, H - 296, "PURPOSE", 8, Color(1, 1, 1, alpha=0.4), track=2.4)
c.setFont("Archivo", 13)
c.setFillColor(WHITE)
c.drawString(58, H - 316, "Prepare body + mind for performance.")
body_text(58, H - 336, [
    "The morning primer. Taken 60-90 minutes before training or",
    "kick-off, it opens blood flow, switches on energy metabolism",
    "and sharpens cognitive readiness - naturally.",
], size=9, leading=14)
for i, o in enumerate(["BLOOD FLOW", "ENERGY METABOLISM", "COGNITIVE READINESS"]):
    c.setFillColor(MAGENTA)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(58, H - 394 - i * 15, "✓")
    tracked(72, H - 394 - i * 15, o, 6.6, Color(1, 1, 1, alpha=0.75), track=1.0)

# natural matrix card
glass(40, H - 590, 330, 118, glow=LIME)
tracked(58, H - 494, "NATURAL MATRIX", 8, Color(1, 1, 1, alpha=0.4), track=2.4)
x = 58
for f in ["DRAGONFRUIT", "BEETROOT", "CITRUS"]:
    x += chip(x, H - 526, f, LIME, size=8) + 8
body_text(58, H - 552, [
    "Whole-fruit foundation. No synthetic base, no artificial",
    "sweeteners. The fruit does the flavour and half of the work.",
], size=9, leading=14)

# usage strip
glass(40, H - 670, 330, 64)
tracked(58, H - 628, "USAGE", 8, Color(1, 1, 1, alpha=0.4), track=2.4)
body_text(58, H - 645, [
    "Morning  ·  Pre-Training  ·  Matchday primer",
    "Taken 60-90 minutes before the session.",
], size=9, leading=13)

# strapline
tracked(40, 92, "NATURE-FIRST. NANO-ENGINEERED. CLUB-VALIDATED.", 9, Color(1, 1, 1, alpha=0.5), track=2.6)

c.showPage()

# ══ PAGE 2 — the nano blend ══════════════════════════════
bg()
header("02 / 02")

tracked(40, H - 116, "INSIDE THE DRINK · ULTRA-FINE EMULSION", 8, LIME, track=2.6)
c.setFont("Archivo", 26)
c.setFillColor(WHITE)
c.drawString(38, H - 150, "THE NANO BLEND")

body_text(40, H - 176, [
    "Every DragonAid bioactive is carried in an ultra-fine emulsion. Droplets measured",
    "in nanometres mean natural actives arrive faster, absorb better and sit lighter",
    "on a matchday stomach.",
], size=9.5, leading=14.5)

# stat chips
stats = [("~150 NM", "DROPLET SIZE"), ("HIGHER", "BIOAVAILABILITY"), ("RAPID", "UPTAKE"), ("GENTLE", "ON THE GUT")]
sw = (W - 80 - 3 * 12) / 4
for i, (v, l) in enumerate(stats):
    x = 40 + i * (sw + 12)
    glass(x, H - 268, sw, 56)
    tracked_c(x + sw / 2, H - 240, v, 11, LIME, track=1.2)
    tracked_c(x + sw / 2, H - 256, l, 5.8, Color(1, 1, 1, alpha=0.42), track=1.4)

# ingredient cards
ingredients = [
    ("NANO BEETROOT NITRATE COMPLEX", MAGENTA, "Blood flow and oxygen efficiency. Supports repeat sprint output and second-half staying power."),
    ("NANO CITRULLINE MALATE", PINK, "Vasodilation and muscular endurance. Keeps working muscle supplied when intensity climbs."),
    ("NANO POLYPHENOL COMPLEX", VIOLET, "Dragonfruit and citrus bioflavonoids. Antioxidant priming ahead of high-load sessions."),
    ("NANO FOCUS BLEND", CYAN, "Natural caffeine paired with L-theanine. Calm, sharp cognition without the spike and crash."),
    ("ELECTROLYTE MICRO-BASE", LIME, "Sodium, potassium and magnesium in solution. The hydration foundation under everything."),
    ("B-VITAMIN MICRO-EMULSION", GOLD, "Energy metabolism support — helping the engine actually use the fuel."),
]
cw = (W - 80 - 14) / 2
chh = 74
top = H - 296
for i, (name, col, desc) in enumerate(ingredients):
    xx = 40 + (i % 2) * (cw + 14)
    yy = top - (i // 2) * (chh + 12) - chh
    glass(xx, yy, cw, chh, glow=col)
    c.setFillColor(col)
    c.circle(xx + 17, yy + chh - 18, 3.4, stroke=0, fill=1)
    tracked(xx + 28, yy + chh - 21, name, 8, WHITE, track=1.1)
    # wrap desc inside the card
    words, lines, cur = desc.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if pdfmetrics.stringWidth(t, "Helvetica", 7.8) > cw - 64:
            lines.append(cur); cur = wd
        else:
            cur = t
    lines.append(cur)
    body_text(xx + 28, yy + chh - 37, lines[:3], size=7.8, leading=11)

# outcomes + disclaimer
oy = top - 3 * (chh + 12) - 26
tracked(40, oy, "KEY OUTCOMES", 8, Color(1, 1, 1, alpha=0.4), track=2.4)
x = 40
for o in ["BLOOD FLOW", "ENERGY METABOLISM", "COGNITIVE READINESS", "HYDRATION FOUNDATION"]:
    c.setFillColor(MAGENTA); c.setFont("Helvetica-Bold", 9)
    c.drawString(x, oy - 20, "✓")
    tracked(x + 12, oy - 20, o, 6.6, Color(1, 1, 1, alpha=0.78), track=1.0)
    x += 12 + pdfmetrics.stringWidth(o, "Archivo", 6.6) + 1.0 * len(o) + 22

glass(40, 60, W - 80, 46)
body_text(56, 90, [
    "Illustrative concept only. Final bioactive selection, doses and preparation technology are defined",
    "with your Biological Architect, formulated to batch-tested, anti-doping-certified standards, and",
    "validated with your club's nutrition and medical staff.",
], size=7.6, leading=10.5, color=Color(1, 1, 1, alpha=0.45))

c.showPage()
c.save()
print("wrote", OUT)
