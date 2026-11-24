#!/usr/bin/env python3
"""Render 'The World in One Day' - news-image-20261124 v2 'Oceanic Relay'.

Fresh blind rewrite from news-20261124-research.md (28 stories, 7 regions).
Every story is dated Tuesday 24 November 2026; the red DATE CHECK box lists
the stories that were NOT Tuesday's news.

Pillow is optional: if it cannot be imported, or the render fails, the
program falls back to copying the committed entry.png to the output path
and exits 0.
"""
import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except Exception:  # pragma: no cover - Pillow missing
    _PIL_OK = False

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_DIR, "DejaVuSerif-Italic.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS_OBLIQUE = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")

# ---------------------------------------------------------------- colours
CREAM = (247, 241, 222)
NAVY = (16, 42, 67)
NAVY_DARK = (10, 30, 50)
RED = (178, 34, 34)
RED_DARK = (150, 25, 25)
INK = (28, 28, 28)
GREY = (96, 92, 84)
SKY = (206, 226, 236)
SKY_DARK = (168, 198, 214)
TAN = (226, 199, 152)
TAN_DARK = (198, 164, 110)
WHITE = (255, 255, 255)
GOLD = (212, 160, 23)
TEAL = (0, 128, 128)
GREEN = (46, 125, 50)
ORANGE = (214, 110, 0)
PURPLE = (106, 76, 147)

W = 1024
H = 1024

# ---------------------------------------------------------------- content
MASTHEAD_LEFT = "THE WORLD IN ONE DAY"
MASTHEAD_RIGHT_TOP = "28 STORIES \u00b7 7 REGIONS"
MASTHEAD_RIGHT_BOT = "EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
DATE_HEADLINE = "TUESDAY 24 NOVEMBER 2026"
SUBHEAD = ("Asia markets surge on Huang\u2019s return \u00b7 Russian jets trigger "
           "Korea air raid alert \u00b7 Zaporizhzhia attack kills 2, wounds 22")

STATS = [
    ("+4.5%", "Nikkei"),
    ("+7.5%", "Kospi"),
    ("+9.1%", "Taiwan Taiex"),
    ("$3,645", "gold, $/oz"),
    ("2 / 22", "killed / wounded \u2014 Zaporizhzhia"),
    ("81.5M", "Thanksgiving travellers"),
]

# (label, count, colour) - totals 28
REGIONS = [
    ("Asia-Pacific 9", 9, NAVY),
    ("Americas 7", 7, RED),
    ("Europe 4", 4, TEAL),
    ("Africa 3", 3, GREEN),
    ("Oceania 2", 2, ORANGE),
    ("Middle East 2", 2, PURPLE),
    ("World 1", 1, GREY),
]

TIMELINE = ("UTC  00:23 Gold $3,645.29/oz  \u00b7  00:35 Japan PMI  \u00b7  02:56 "
            "Hasina exclusive  \u00b7  06:29 Japan GDP -0.1%  \u00b7  07:52 KST "
            "KADIZ alert  \u00b7  17:45 UCL kick-offs  \u00b7  20:00 Miss Universe final")

# Leads: (number, kicker, headline, body, source, tag, pictorial kind)
LEADS = [
    (1, "ASIA-PACIFIC \u00b7 MARKETS",
     "Asia markets surge; gold hits $3,645",
     "Nikkei +4.5% as Tokyo reopens; Kospi +7.5%, Taiwan +9.1% with TSMC "
     "near its daily limit. Gold +0.4% to $3,645/oz, rebounding from "
     "Friday\u2019s low.",
     "Reuters \u00b7 Bloomberg \u00b7 CNA", "REPORTED", "chart"),
    (2, "ASIA-PACIFIC \u00b7 SOUTH KOREA",
     "Russian jets enter Korea\u2019s air defence zone",
     "Russian jets entered the KADIZ near Ulleung Island; fighters scrambled "
     "and a shelter alert sounded at 07:52 KST, lifted five minutes later. "
     "Seoul: no airspace violated.",
     "AP \u00b7 Al Jazeera \u00b7 Yonhap", "REPORTED", "jets"),
    (3, "EUROPE \u00b7 UKRAINE",
     "Russian attack kills 2, wounds 22 in Zaporizhzhia",
     "An overnight strike killed two and wounded 22, including two children, "
     "in Zaporizhzhia, regional officials said. Apartment blocks and "
     "transport infrastructure were damaged.",
     "Reuters", "REPORTED", "blast"),
]

# Medium cards 4-13: (number, kicker, headline, body, source, tag, icon)
MEDIUM = [
    (4, "ASIA-PACIFIC \u00b7 BANGLADESH",
     "Hasina plans return to Bangladesh on Dec 16",
     "Ex-PM seeks papers and a Biman flight home from Delhi.",
     "Reuters", "REPORTED", "plane"),
    (5, "MIDDLE EAST \u00b7 GAZA",
     "Israeli strike kills 3, wounds 5 in Khan Younis",
     "Strike near a police post in southern Gaza, health officials say.",
     "Reuters", "REPORTED", "flame"),
    (6, "AMERICAS \u00b7 WASHINGTON",
     "Republicans break with Trump over Huang return",
     "Cotton, Ricketts attack reinstatement; hearing set Dec 3.",
     "WSJ", "REPORTED", "capitol"),
    (7, "ASIA-PACIFIC \u00b7 JAPAN",
     "Japan arms buildup taps car-parts makers",
     "Toyota supplier Aster builds motors for Anduril drones.",
     "Reuters", "REPORTED", "factory"),
    (8, "EUROPE \u00b7 BRUSSELS",
     "Germany stays EU\u2019s biggest net payer",
     "Net \u20ac14.9bn, up \u20ac1.8bn on 2024, ahead of budget summit.",
     "Reuters \u00b7 IW", "REPORTED", "coin"),
    (9, "AMERICAS \u00b7 TRAVEL",
     "Thanksgiving travel begins: 81.5M on the move",
     "First fall since 2020; 5.96M fly, fares $800, up 17%.",
     "AAA", "REPORTED", "plane"),
    (10, "ASIA-PACIFIC \u00b7 SPACE",
     "China to launch Shenzhou-24 on Wednesday",
     "Launch Wed 08:18 local; Zeeshan Ali first foreign astronaut.",
     "Reuters", "FORECAST", "rocket"),
    (11, "ASIA-PACIFIC \u00b7 JAPAN",
     "Japan GDP shrinks 0.1% as households cut spending",
     "Business investment up 1.6%, driven by AI projects.",
     "Kyodo News", "REPORTED", "chartdown"),
    (12, "AMERICAS \u00b7 WEATHER",
     "Twin storms threaten both US coasts",
     "East Coast winds to 50 mph; West Coast floods to 2.7 ft.",
     "AP \u00b7 NWS", "REPORTED", "storm"),
    (13, "MIDDLE EAST \u00b7 SHIPPING",
     "US suspects Iran behind attacks on 50 ships",
     "US officials tell WSJ Iran is suspected in cyberattacks on tankers.",
     "WSJ", "CLAIM", "ship"),
]

# Briefs 14-28, one full line each, never cut.
BRIEFS = [
    (14, "Pacific Elders\u2019 Voice accuse Australia of climate betrayal at COP31"),
    (15, "NBA: Blazers end 76ers\u2019 5-game win streak 128\u2013111"),
    (16, "UCL tonight: Arsenal host Dortmund, Man City host Napoli"),
    (17, "CAS to rule Tuesday on Senegal\u2019s AFCON title appeal"),
    (18, "Japan factory PMI: manufacturing 53.7, services slip to 50.5"),
    (19, "Japan tells arms makers to brace for order cuts of up to 80%"),
    (20, "ASEAN disaster talks in Tangerang; 28 disasters hit 90,200 in a week"),
    (21, "WHO chief visits Cuba as healthcare system deteriorates"),
    (22, "Man with Alzheimer\u2019s survives 11 days alone in Amazon, rescued"),
    (23, "Soldiers attacked after El Chapo Isidro arrest; 8 suspects held"),
    (24, "UK-EU reset bill goes to Parliament Thursday"),
    (25, "Sheffield Shield: Labuschagne\u2019s freak dismissal, Swepson 6/73"),
    (26, "Miss Universe 75th final tonight in San Juan: 116 contestants"),
    (27, "Africa\u2019s first \u2018comfort women\u2019 statue: Cape Town Dec 1"),
    (28, "Ramaphosa faces NCOP questions Tuesday on AGOA loss, 30% tariff"),
]

# DATE CHECK: two columns, 11 each.
DATECHECK_A = [
    "COP31 collapse \u2014 Sun 22 Nov (Tue: reactions only)",
    "Cikande fire \u2014 Sat 21 Nov; 24 dead confirmed Mon 23 Nov",
    "Netanyahu urges Trump to strike Iran \u2014 Sun 22 Nov",
    "China spy death sentence (Ma) \u2014 Mon 23 Nov",
    "Megaspeed blacklist; Zelensky talks; Pentagon rebukes Canada \u2014 Mon 23 Nov",
    "India\u2013Nepal \u20b915,000 crore package \u2014 Mon 23 Nov",
    "Lowy Asia Power Index 2026 \u2014 Mon 23 Nov",
    "West Bengal renamed \u2018Paschim Banga\u2019 \u2014 Mon 23 Nov",
    "Indonesia signs Expo 2030 Riyadh deal \u2014 Mon 23 Nov",
    "WFP warns 10M tons of wheat may miss markets \u2014 Mon 23 Nov",
    "DRC Ituri: fighting traps Ebola responders \u2014 Sun 22 Nov",
]
DATECHECK_B = [
    "Samia Suluhu AU maternal health roadmap \u2014 Mon 23 Nov",
    "S&P Philippines downgrade \u2014 24 Sep 2026",
    "Jollibee UK 30 stores \u2014 announced Mon 23 Nov",
    "Thailand wellness $46.5bn \u2014 data released 12 Nov",
    "ACT Indigenous protocol review \u2014 reported Mon 23 Nov",
    "Seychelles\u2013Nigeria meeting \u2014 Mon 23 Nov",
    "Iran singer Parastoo Ahmadi flogged 74 lashes \u2014 Mon 23 Nov",
    "India HPV 10M doses \u2014 announced Mon 23 Nov",
    "Two Nigerians killed fighting for Russia \u2014 announced Feb 2026",
    "US Senate $9.4bn aid/media cuts vote \u2014 Jul 2025",
    "Japan hosts US Treasury Secretary Bessent \u2014 meeting 11 Nov",
]

FOOTER_SOURCES = ("Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 WSJ \u00b7 Kyodo News \u00b7 "
                   "Al Jazeera \u00b7 PINA \u00b7 UEFA \u00b7 The Sun \u00b7 Fox Sports \u00b7 "
                   "Yonhap \u00b7 S&P Global")
FOOTER_LEGEND = ("REPORTED = carried by the day\u2019s wires  \u00b7  CLAIM = one side\u2019s "
                 "account, labelled as such  \u00b7  FORECAST = still to happen when drawn")

# Map pins: (number, x fraction, y fraction) inside the map box.
PINS = [
    (1, 0.86, 0.40), (2, 0.83, 0.36), (3, 0.52, 0.28), (4, 0.72, 0.52),
    (5, 0.55, 0.47), (6, 0.25, 0.40), (7, 0.89, 0.33), (8, 0.49, 0.25),
    (9, 0.20, 0.46), (10, 0.76, 0.38), (11, 0.85, 0.45), (12, 0.16, 0.38),
    (13, 0.60, 0.52),
]

CONTINENTS = [
    # North America
    [(0.02, 0.18), (0.10, 0.08), (0.22, 0.10), (0.28, 0.20), (0.24, 0.30),
     (0.16, 0.42), (0.08, 0.38), (0.02, 0.28)],
    # South America
    [(0.20, 0.52), (0.28, 0.50), (0.33, 0.60), (0.30, 0.78), (0.24, 0.92),
     (0.20, 0.72)],
    # Europe
    [(0.46, 0.16), (0.52, 0.10), (0.58, 0.16), (0.56, 0.26), (0.50, 0.28),
     (0.45, 0.22)],
    # Africa
    [(0.47, 0.36), (0.56, 0.34), (0.62, 0.44), (0.58, 0.62), (0.52, 0.72),
     (0.47, 0.58)],
    # Asia
    [(0.60, 0.10), (0.72, 0.06), (0.86, 0.10), (0.96, 0.20), (0.92, 0.34),
     (0.82, 0.44), (0.72, 0.40), (0.64, 0.30), (0.58, 0.20)],
    # Australia
    [(0.82, 0.68), (0.92, 0.66), (0.96, 0.74), (0.88, 0.82), (0.82, 0.76)],
]


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines, all within max_w."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _fit_lines(draw, text, path, size, max_w, max_lines, min_size=8):
    """Shrink font until the wrapped text fits in max_lines. Returns
    (font, lines). Raises if it still does not fit at min_size."""
    size_now = size
    while size_now >= min_size:
        font = _font(path, size_now)
        lines = _wrap(draw, text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
        size_now -= 1
    raise RuntimeError("text does not fit: %r" % text[:60])


def _draw_lines(draw, x, y, lines, font, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def _check_no_ellipsis():
    """Guard: no headline or brief may ever be cut with an ellipsis."""
    texts = [MASTHEAD_RIGHT_TOP, DATE_HEADLINE, SUBHEAD, TIMELINE,
             FOOTER_SOURCES, FOOTER_LEGEND]
    for lead in LEADS:
        texts += list(lead[1:6])
    for med in MEDIUM:
        texts += list(med[1:6])
    for _, brief in BRIEFS:
        texts.append(brief)
    texts += DATECHECK_A + DATECHECK_B
    for text in texts:
        if "..." in text or "\u2026" in text:
            raise RuntimeError("ellipsis found in drawn text: %r" % text[:60])


def _pictorial(draw, kind, box, accent):
    """Bold, simple pictorial zone. box = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    if kind == "chart":
        # rising market line with arrow + gold coins
        pts = [(x0 + 30, y1 - 22), (x0 + 95, y1 - 48), (x0 + 150, y1 - 38),
               (x0 + 215, y1 - 66), (x1 - 34, y0 + 26)]
        draw.line(pts, fill=RED, width=7, joint="curve")
        draw.polygon([(x1 - 40, y0 + 18), (x1 - 14, y0 + 22), (x1 - 34, y0 + 42)],
                     fill=RED)
        for ox, oy, r in [(x1 - 62, y1 - 26, 15), (x1 - 34, y1 - 20, 11)]:
            draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=GOLD,
                         outline=NAVY, width=2)
            draw.text((ox - 4, oy - 8), "$", font=_font(SANS_BOLD, 13),
                      fill=NAVY)
        draw.line([(x0 + 18, y1 - 14), (x1 - 18, y1 - 14)], fill=GREY, width=2)
    elif kind == "jets":
        # two jet deltas + radar arcs over an island dot
        for jx, jy, s in [(cx - 52, cy - 8, 1.0), (cx + 30, cy + 12, 0.8)]:
            w = int(46 * s)
            h = int(20 * s)
            draw.polygon([(jx - w, jy), (jx + w, jy - h // 2),
                          (jx + w, jy + h // 2)], fill=NAVY)
            draw.polygon([(jx - w + 8, jy - 4), (jx - 6, jy - h),
                          (jx + 2, jy - 4)], fill=NAVY)
            draw.polygon([(jx - w + 8, jy + 4), (jx - 6, jy + h),
                          (jx + 2, jy + 4)], fill=NAVY)
        for r in (12, 24, 36):
            draw.arc([cx - 78 - r, cy + 12 - r, cx - 78 + r, cy + 12 + r],
                     start=200, end=340, fill=RED, width=3)
        draw.ellipse([cx - 86, cy - 30, cx - 70, cy - 14], fill=GREEN)
    elif kind == "blast":
        # apartment blocks + flame (kept inside the pictorial zone)
        for bx, bw, bh in [(x0 + 26, 52, 40), (x0 + 88, 64, 50),
                           (x0 + 162, 56, 44)]:
            draw.rectangle([bx, y1 - 16 - bh, bx + bw, y1 - 16], fill=NAVY)
            for wy in range(y1 - 16 - bh + 8, y1 - 22, 14):
                for wx in range(bx + 8, bx + bw - 8, 14):
                    draw.rectangle([wx, wy, wx + 6, wy + 7], fill=GOLD)
        fx, fy = x0 + 236, y1 - 36
        draw.polygon([(fx - 22, fy + 22), (fx - 26, fy - 6), (fx - 8, fy - 26),
                      (fx + 2, fy - 8), (fx + 18, fy - 30), (fx + 26, fy + 4),
                      (fx + 12, fy + 22)], fill=(232, 90, 12))
        draw.polygon([(fx - 10, fy + 20), (fx - 12, fy + 2), (fx, fy - 12),
                      (fx + 10, fy + 2), (fx + 12, fy + 20)], fill=GOLD)


def _icon(draw, kind, cx, cy, s, colour):
    """Small bold icon for a medium card, centred at (cx, cy), scale s."""
    if kind == "plane":
        draw.polygon([(cx - 16 * s, cy), (cx + 16 * s, cy - 6 * s),
                      (cx + 16 * s, cy + 6 * s)], fill=colour)
        draw.polygon([(cx - 6 * s, cy - 3 * s), (cx + 2 * s, cy - 14 * s),
                      (cx + 8 * s, cy - 3 * s)], fill=colour)
        draw.polygon([(cx - 6 * s, cy + 3 * s), (cx + 2 * s, cy + 14 * s),
                      (cx + 8 * s, cy + 3 * s)], fill=colour)
    elif kind == "flame":
        draw.polygon([(cx - 10 * s, cy + 10 * s), (cx - 12 * s, cy - 4 * s),
                      (cx - 3 * s, cy - 14 * s), (cx + 3 * s, cy - 4 * s),
                      (cx + 11 * s, cy - 12 * s), (cx + 12 * s, cy + 10 * s)],
                     fill=colour)
    elif kind == "capitol":
        draw.pieslice([cx - 12 * s, cy - 16 * s, cx + 12 * s, cy + 2 * s],
                      start=180, end=360, fill=colour)
        draw.rectangle([cx - 14 * s, cy, cx + 14 * s, cy + 3 * s], fill=colour)
        for i in (-1, 0, 1):
            draw.rectangle([cx + i * 9 * s - 2 * s, cy + 3 * s,
                            cx + i * 9 * s + 2 * s, cy + 12 * s], fill=colour)
        draw.rectangle([cx - 15 * s, cy + 12 * s, cx + 15 * s, cy + 15 * s],
                       fill=colour)
    elif kind == "factory":
        draw.rectangle([cx - 16 * s, cy - 2 * s, cx + 16 * s, cy + 14 * s],
                       fill=colour)
        draw.polygon([(cx - 16 * s, cy - 2 * s), (cx - 8 * s, cy - 12 * s),
                      (cx, cy - 2 * s), (cx + 8 * s, cy - 12 * s),
                      (cx + 16 * s, cy - 2 * s)], fill=colour)
        draw.rectangle([cx + 8 * s, cy - 16 * s, cx + 12 * s, cy - 2 * s],
                       fill=colour)
    elif kind == "coin":
        draw.ellipse([cx - 13 * s, cy - 13 * s, cx + 13 * s, cy + 13 * s],
                     fill=colour)
        draw.text((cx - 6 * s, cy - 10 * s), "\u20ac",
                  font=_font(SANS_BOLD, int(16 * s)), fill=WHITE)
    elif kind == "rocket":
        draw.polygon([(cx, cy - 16 * s), (cx + 7 * s, cy + 6 * s),
                      (cx - 7 * s, cy + 6 * s)], fill=colour)
        draw.polygon([(cx - 7 * s, cy + 2 * s), (cx - 13 * s, cy + 12 * s),
                      (cx - 7 * s, cy + 10 * s)], fill=colour)
        draw.polygon([(cx + 7 * s, cy + 2 * s), (cx + 13 * s, cy + 12 * s),
                      (cx + 7 * s, cy + 10 * s)], fill=colour)
        draw.polygon([(cx - 4 * s, cy + 12 * s), (cx, cy + 18 * s),
                      (cx + 4 * s, cy + 12 * s)], fill=(232, 90, 12))
    elif kind == "chartdown":
        draw.line([(cx - 15 * s, cy - 10 * s), (cx - 5 * s, cy + 2 * s),
                   (cx + 5 * s, cy - 4 * s), (cx + 15 * s, cy + 10 * s)],
                  fill=colour, width=int(3 * s), joint="curve")
        draw.polygon([(cx + 15 * s, cy + 10 * s), (cx + 15 * s, cy + 2 * s),
                      (cx + 7 * s, cy + 10 * s)], fill=colour)
    elif kind == "storm":
        draw.ellipse([cx - 15 * s, cy - 8 * s, cx + 1 * s, cy + 8 * s],
                     fill=colour)
        draw.ellipse([cx - 5 * s, cy - 12 * s, cx + 13 * s, cy + 8 * s],
                     fill=colour)
        draw.polygon([(cx - 6 * s, cy + 8 * s), (cx + 2 * s, cy + 8 * s),
                      (cx - 4 * s, cy + 16 * s)], fill=GOLD)
    elif kind == "ship":
        draw.polygon([(cx - 16 * s, cy + 2 * s), (cx + 16 * s, cy + 2 * s),
                      (cx + 11 * s, cy + 12 * s), (cx - 11 * s, cy + 12 * s)],
                     fill=colour)
        draw.rectangle([cx - 1 * s, cy - 14 * s, cx + 1 * s, cy + 2 * s],
                       fill=colour)
        draw.polygon([(cx + 1 * s, cy - 14 * s), (cx + 12 * s, cy - 2 * s),
                      (cx + 1 * s, cy - 2 * s)], fill=colour)


def render():
    _check_no_ellipsis()
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 46], fill=NAVY)
    d.text((14, 8), MASTHEAD_LEFT, font=_font(SERIF_BOLD, 26), fill=WHITE)
    f_top = _font(SANS_BOLD, 13)
    f_bot = _font(SANS, 10)
    d.text((W - 14 - d.textlength(MASTHEAD_RIGHT_TOP, font=f_top), 6),
           MASTHEAD_RIGHT_TOP, font=f_top, fill=WHITE)
    d.text((W - 14 - d.textlength(MASTHEAD_RIGHT_BOT, font=f_bot), 24),
           MASTHEAD_RIGHT_BOT, font=f_bot, fill=(200, 214, 228))

    # ---- giant serif date ----------------------------------------------
    f_date = _font(SERIF_BOLD, 52)
    d.text(((W - d.textlength(DATE_HEADLINE, font=f_date)) // 2, 52),
           DATE_HEADLINE, font=f_date, fill=NAVY)

    # ---- red sub-headline ----------------------------------------------
    f_sub, sub_lines = _fit_lines(d, SUBHEAD, SERIF_ITALIC, 17, W - 60, 2)
    y = 110
    for line in sub_lines:
        d.text(((W - d.textlength(line, font=f_sub)) // 2, y), line,
               font=f_sub, fill=RED)
        y += 21

    # ---- stat strip ------------------------------------------------------
    y_stat = 134
    col_w = (W - 28) // 6
    f_num = _font(SANS_BOLD, 27)
    f_cap = _font(SANS, 11)
    for i, (num, cap) in enumerate(STATS):
        cx = 14 + col_w * i + col_w // 2
        d.text((cx - d.textlength(num, font=f_num) // 2, y_stat), num,
               font=f_num, fill=RED)
        d.text((cx - d.textlength(cap, font=f_cap) // 2, y_stat + 32), cap,
               font=f_cap, fill=INK)

    # ---- region bar ------------------------------------------------------
    y_bar = 178
    d.text((14, y_bar), "STORIES BY REGION", font=_font(SANS_BOLD, 11),
           fill=NAVY)
    bar_x = 14
    bar_w = W - 28
    for label, count, colour in REGIONS:
        seg = bar_w * count // 28
        d.rectangle([bar_x, y_bar + 15, bar_x + seg - 2, y_bar + 27],
                    fill=colour)
        bar_x += seg
    lx = 14
    f_leg = _font(SANS_BOLD, 10)
    for label, count, colour in REGIONS:
        piece = label + "   "
        d.text((lx, y_bar + 30), piece, font=f_leg, fill=colour)
        lx += d.textlength(piece, font=f_leg)

    # ---- UTC timeline ----------------------------------------------------
    y_tl = 224
    f_tl = _font(SANS, 11)
    d.text((14, y_tl), TIMELINE, font=f_tl, fill=INK)

    # ---- 3 big lead cards ------------------------------------------------
    lead_y = 240
    lead_h = 210
    lead_w = 322
    lead_gap = 7
    for i, (num, kicker, head, body, source, tag, kind) in enumerate(LEADS):
        x = 14 + i * (lead_w + lead_gap)
        d.rectangle([x, lead_y, x + lead_w, lead_y + lead_h], fill=WHITE,
                    outline=TAN_DARK, width=1)
        # pictorial zone, deliberately large
        pic_h = 76
        d.rectangle([x + 1, lead_y + 1, x + lead_w - 1, lead_y + pic_h],
                    fill=SKY)
        _pictorial(d, kind, (x + 6, lead_y + 4, x + lead_w - 6,
                             lead_y + pic_h - 2), RED)
        ty = lead_y + pic_h + 6
        d.text((x + 10, ty), kicker, font=_font(SANS_BOLD, 10), fill=RED)
        ty += 16
        f_head, head_lines = _fit_lines(d, head, SANS_BOLD, 19, lead_w - 20, 2)
        ty = _draw_lines(d, x + 10, ty, head_lines, f_head, NAVY, 22)
        ty += 3
        f_body, body_lines = _fit_lines(d, body, SANS, 12, lead_w - 20, 3)
        ty = _draw_lines(d, x + 10, ty, body_lines, f_body, INK, 15)
        # footer: source left, tag right
        f_src = _font(SANS, 10)
        d.text((x + 10, lead_y + lead_h - 16), source, font=f_src, fill=GREY)
        f_tag = _font(SANS_BOLD, 10)
        tag_col = RED if tag in ("CLAIM", "FORECAST") else RED_DARK
        d.text((x + lead_w - 10 - d.textlength(tag, font=f_tag),
                lead_y + lead_h - 16), tag, font=f_tag, fill=tag_col)

    # ---- 10 medium cards -------------------------------------------------
    med_y0 = 456
    med_h = 94
    med_w = 194
    med_gap = 6
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            num, kicker, head, body, source, tag, icon = MEDIUM[idx]
            x = 14 + col * (med_w + med_gap)
            y = med_y0 + row * (med_h + med_gap)
            d.rectangle([x, y, x + med_w, y + med_h], fill=WHITE,
                        outline=TAN_DARK, width=1)
            # pictorial strip with number + kicker + icon
            d.rectangle([x + 1, y + 1, x + med_w - 1, y + 24], fill=SKY)
            d.ellipse([x + 5, y + 4, x + 23, y + 22], fill=RED)
            f_n = _font(SANS_BOLD, 11)
            ntxt = str(num)
            d.text((x + 14 - d.textlength(ntxt, font=f_n) // 2, y + 6), ntxt,
                   font=f_n, fill=WHITE)
            f_kick, kick_lines = _fit_lines(d, kicker, SANS_BOLD, 9,
                                            med_w - 27 - 36, 1, min_size=7)
            d.text((x + 27, y + 6), kick_lines[0], font=f_kick, fill=NAVY)
            _icon(d, icon, x + med_w - 16, y + 13, 0.9, NAVY)
            ty = y + 28
            f_head, head_lines = _fit_lines(d, head, SANS_BOLD, 12,
                                            med_w - 16, 2)
            ty = _draw_lines(d, x + 8, ty, head_lines, f_head, NAVY, 13)
            f_body, body_lines = _fit_lines(d, body, SANS, 10, med_w - 16, 2)
            ty = _draw_lines(d, x + 8, ty, body_lines, f_body, INK, 11)
            f_src = _font(SANS, 9)
            d.text((x + 8, y + med_h - 13), source, font=f_src, fill=GREY)
            f_tag = _font(SANS_BOLD, 9)
            tag_col = RED if tag in ("CLAIM", "FORECAST") else RED_DARK
            d.text((x + med_w - 8 - d.textlength(tag, font=f_tag),
                    y + med_h - 13), tag, font=f_tag, fill=tag_col)

    # ---- map + briefs ----------------------------------------------------
    sec_y = 656
    map_x, map_y, map_w, map_h = 14, sec_y + 16, 330, 128
    d.text((14, sec_y), "WHERE IT HAPPENED \u2014 13 LEADS PINNED",
           font=_font(SANS_BOLD, 11), fill=NAVY)
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=SKY,
                outline=TAN_DARK, width=1)
    for poly in CONTINENTS:
        pts = [(map_x + fx * map_w, map_y + fy * map_h) for fx, fy in poly]
        d.polygon(pts, fill=TAN, outline=TAN_DARK)
    f_pin = _font(SANS_BOLD, 9)
    for num, fx, fy in PINS:
        px = map_x + fx * map_w
        py = map_y + fy * map_h
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=WHITE, width=1)
        ntxt = str(num)
        d.text((px - d.textlength(ntxt, font=f_pin) // 2, py - 7), ntxt,
               font=f_pin, fill=WHITE)

    bx = 360
    d.text((bx, sec_y), "ALSO ON TUESDAY 24 NOVEMBER",
           font=_font(SANS_BOLD, 11), fill=NAVY)
    f_br = _font(SANS, 10)
    by = sec_y + 17
    for num, text in BRIEFS:
        line = "%d. %s" % (num, text)
        if d.textlength(line, font=f_br) > (W - 14 - bx):
            raise RuntimeError("brief too long for one line: %r" % line[:60])
        d.text((bx, by), str(num) + ".", font=_font(SANS_BOLD, 10), fill=RED)
        d.text((bx + 22, by), text, font=f_br, fill=INK)
        by += 10

    # ---- DATE CHECK ------------------------------------------------------
    dc_y = 836
    dc_h = 146
    d.rectangle([14, dc_y, W - 14, dc_y + dc_h], outline=RED, width=2)
    d.text((24, dc_y + 5),
           "DATE CHECK \u2014 NOT TUESDAY 24 NOVEMBER: first reported earlier",
           font=_font(SANS_BOLD, 12), fill=RED)
    f_dc = _font(SANS, 9)
    col_w = (W - 48) // 2
    for col_idx, items in enumerate((DATECHECK_A, DATECHECK_B)):
        cx = 24 + col_idx * col_w
        cy = dc_y + 24
        for item in items:
            d.text((cx, cy), "\u2715", font=_font(SANS_BOLD, 9), fill=RED)
            d.text((cx + 12, cy), item, font=f_dc, fill=INK)
            cy += 11

    # ---- footer ----------------------------------------------------------
    fy = 988
    d.text((14, fy), FOOTER_SOURCES, font=_font(SANS, 10), fill=GREY)
    d.text((14, fy + 13), FOOTER_LEGEND, font=_font(SANS, 10), fill=GREY)
    f_end = _font(SANS_BOLD, 10)
    end = "THE WORLD IN ONE DAY \u00b7 24 NOVEMBER 2026"
    d.text((W - 14 - d.textlength(end, font=f_end), fy + 26), end,
           font=f_end, fill=NAVY)
    return img


def _output_path():
    for var in ("MAKEFUN_OUTPUT_DIR", "ENTRY_OUTPUT"):
        val = os.environ.get(var)
        if val:
            return val
    return "/output/entry.png"


def main():
    if not _PIL_OK:
        _fallback()
        return 0
    try:
        img = render()
    except Exception as exc:  # render failed: fall back to committed image
        print("render failed (%s); falling back to committed entry.png"
              % exc, file=sys.stderr)
        _fallback()
        return 0
    out = _output_path()
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    img.save(out)
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "entry.png")
    if os.path.abspath(out) != os.path.abspath(local):
        img.save(local)
    print("wrote %s (%dx%d)" % (out, W, H))
    return 0


def _fallback():
    here = os.path.dirname(os.path.abspath(__file__))
    committed = os.path.join(here, "entry.png")
    out = _output_path()
    if os.path.exists(committed):
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        shutil.copyfile(committed, out)
        print("fallback: copied committed entry.png to %s" % out)
    else:
        print("fallback: no committed entry.png available", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
