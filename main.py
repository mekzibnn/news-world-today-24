#!/usr/bin/env python3
"""news-image-20261124 v4 — renders a 1024x1024 one-image summary of
Tuesday 24 November 2026 world news. Blind rewrite: written fresh from
the research file, no earlier implementation consulted.

Layout (1024 tall): masthead 26, title 48, subhead 14, stat 30,
region 28, timeline 34, big lead cards 178 (pictorial band 60),
medium cards 208, map+briefs 282, DATE CHECK 154, footer 22.
"""
import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except ImportError:  # pragma: no cover
    _PIL_OK = False

# ---------------------------------------------------------------- palette
CREAM = (247, 240, 220)
PAPER = (255, 253, 245)
NAVY = (27, 42, 74)
NAVY_DARK = (18, 30, 58)
RED = (185, 28, 28)
RED_DARK = (150, 20, 20)
DARK = (26, 26, 26)
GREY = (85, 85, 85)
GOLD = (212, 175, 55)
GOLD_DARK = (160, 120, 20)
SKY = (214, 228, 240)
LAND = (232, 217, 168)
LAND_LINE = (190, 170, 120)

# ---------------------------------------------------------------- layout
W, H = 1024, 1024
MARGIN = 16
CONTENT_W = W - 2 * MARGIN  # 992

Y_MASTHEAD, H_MASTHEAD = 0, 26
Y_TITLE, H_TITLE = 26, 48
Y_SUBHEAD, H_SUBHEAD = 74, 14
Y_STAT, H_STAT = 88, 28
Y_REGION, H_REGION = 116, 28
Y_TIMELINE, H_TIMELINE = 144, 34
Y_BIG, H_BIG = 178, 178
PICT_H = 60  # pictorial band height on the 3 big lead cards
Y_MED, H_MED = 356, 212
Y_MAP, H_MAP = 568, 282
Y_DATE, H_DATE = 850, 154
Y_FOOTER, H_FOOTER = 1004, 20

# ---------------------------------------------------------------- font sizes
FONT_BRIEF = 18
FONT_DATECHECK = 16
FONT_BODY = 17
FONT_TIMELINE = 16
FONT_CAPTION = 14
FONT_TITLE_MAX_W = 930
FONT_MASTHEAD_MIN_MARGIN = 30
FONT_TITLE_MIN_MARGIN = 40

# ---------------------------------------------------------------- fonts
_DEJAVU = "/usr/share/fonts/truetype/dejavu/"
_LIBERATION = "/usr/share/fonts/truetype/liberation/"


def _font(name, size):
    """Load a font by name, trying DejaVu then Liberation, then default."""
    candidates = []
    if name == "serif-bold":
        candidates = [_DEJAVU + "DejaVuSerif-Bold.ttf",
                      _LIBERATION + "LiberationSerif-Bold.ttf"]
    elif name == "sans-bold":
        candidates = [_DEJAVU + "DejaVuSans-Bold.ttf",
                      _LIBERATION + "LiberationSans-Bold.ttf"]
    elif name == "sans-italic":
        candidates = [_DEJAVU + "DejaVuSans-Oblique.ttf",
                      _DEJAVU + "DejaVuSerif-Italic.ttf",
                      _LIBERATION + "LiberationSans-Italic.ttf",
                      _DEJAVU + "DejaVuSans.ttf"]
    else:  # "sans"
        candidates = [_DEJAVU + "DejaVuSans.ttf",
                      _LIBERATION + "LiberationSans-Regular.ttf"]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _text_w(font, text):
    return font.getlength(text)


def _wrap(font, text, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w."""
    words = text.split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = cur + " " + word
        if _text_w(font, trial) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


# ---------------------------------------------------------------- content
TITLE = "TUESDAY 24 NOVEMBER 2026"
MASTHEAD_LEFT = "THE WORLD IN ONE DAY"
MASTHEAD_RIGHT = "28 STORIES · 7 REGIONS"
MASTHEAD_SUB = "EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
SUBHEAD = ("Asia markets surge on Huang's return · Russian jets trigger "
           "Korea air raid alert · Zaporizhzhia attack kills 2, wounds 22")

STATS = [
    ("+4.5%", "Nikkei"),
    ("+7.5%", "Kospi"),
    ("+9.1%", "Taiwan Taiex"),
    ("$3,645", "gold, $/oz"),
    ("2 / 22", "killed / wounded"),
    ("81.5M", "Thanksgiving travel"),
]

REGION_COLORS = [
    ("Asia-Pacific", 9, (27, 42, 74)),
    ("Americas", 7, (185, 28, 28)),
    ("Europe", 4, (212, 175, 55)),
    ("Africa", 3, (46, 125, 50)),
    ("Oceania", 2, (21, 101, 140)),
    ("Middle East", 2, (123, 31, 162)),
    ("World", 1, (120, 120, 120)),
]

TIMELINE = [
    "UTC 00:23 Gold $3,645.29/oz · 00:35 Japan PMI · 02:56 Hasina exclusive · 06:29 Japan GDP -0.1% · 07:52 KST KADIZ alert",
    "17:45 & 20:00 GMT UCL kick-offs · 01:00 UTC (Wed) Miss Universe final · 0018 GMT (Wed) Shenzhou-24 launch",
]

# 3 big lead cards. Bodies fit 2 lines at 17px in a 313px column.
LEADS = [
    {
        "num": 1, "kicker": "ASIA-PACIFIC · MARKETS",
        "headline": "Asia markets surge; gold hits $3,645",
        "body": "Nikkei +4.5% as Tokyo reopens; Kospi +7.5%, Taiwan +9.1%.",
        "sources": "Reuters · Bloomberg · CNA", "tag": "REPORTED",
        "pict": "chart",
    },
    {
        "num": 2, "kicker": "ASIA-PACIFIC · SOUTH KOREA",
        "headline": "Russian jets enter Korea's air defence zone",
        "body": "KADIZ entry near Ulleung; alert 07:52 KST, no violation.",
        "sources": "AP · Al Jazeera · Yonhap", "tag": "REPORTED",
        "pict": "jets",
    },
    {
        "num": 3, "kicker": "EUROPE · UKRAINE",
        "headline": "Russian attack kills 2, wounds 22 in Zaporizhzhia",
        "body": "Overnight strike killed 2, wounded 22, including two children.",
        "sources": "Reuters", "tag": "REPORTED",
        "pict": "fire",
    },
]

# 10 medium cards. Headlines fit 2 lines at 17px bold, bodies fit 2 lines
# at 17px, in a 180px column. Bodies are complete factual phrases.
MEDIUM = [
    {"num": 4, "kicker": "APAC · BANGLADESH",
     "headline": "Hasina plans Dec 16 return",
     "body": "Ex-PM seeks papers, Biman flight Dec 16.",
     "sources": "Reuters", "tag": "REPORTED"},
    {"num": 5, "kicker": "MIDEAST · GAZA",
     "headline": "Israeli strike kills 3, wounds 5",
     "body": "Strike near a police post, 5 wounded.",
     "sources": "Reuters", "tag": "REPORTED"},
    {"num": 6, "kicker": "AMERICAS · WASHINGTON",
     "headline": "GOP breaks with Trump over Huang",
     "body": "GOP attacks it; Dec 3 hearing.",
     "sources": "WSJ", "tag": "REPORTED"},
    {"num": 7, "kicker": "APAC · JAPAN",
     "headline": "Japan taps car makers for arms",
     "body": "Aster builds motors for Anduril drones.",
     "sources": "Reuters", "tag": "REPORTED"},
    {"num": 8, "kicker": "EUROPE · BRUSSELS",
     "headline": "Germany stays top EU net payer",
     "body": "Net €14.9bn, up €1.8bn on 2024.",
     "sources": "Reuters · IW", "tag": "REPORTED"},
    {"num": 9, "kicker": "AMERICAS · TRAVEL",
     "headline": "Thanksgiving: 81.5M travel",
     "body": "First fall since 2020; 5.96M fly.",
     "sources": "AAA", "tag": "REPORTED"},
    {"num": 10, "kicker": "APAC · SPACE",
     "headline": "Shenzhou-24 launches Wed",
     "body": "Zeeshan Ali, first foreign astronaut.",
     "sources": "Reuters", "tag": "FORECAST"},
    {"num": 11, "kicker": "APAC · JAPAN",
     "headline": "Japan GDP shrinks 0.1% in Q3",
     "body": "Investment up 1.6% on AI projects.",
     "sources": "Kyodo News", "tag": "REPORTED"},
    {"num": 12, "kicker": "AMERICAS · WEATHER",
     "headline": "Twin storms hit both US coasts",
     "body": "Winds 50 mph east; floods 2.7 ft west.",
     "sources": "AP · NWS", "tag": "REPORTED"},
    {"num": 13, "kicker": "MIDEAST · SHIPPING",
     "headline": "Iran suspected in 50 ship attacks",
     "body": "US officials tell WSJ Iran is suspected.",
     "sources": "WSJ", "tag": "CLAIM"},
]

# 15 briefs, numbered 14-28. Each fits one line at 18px in the briefs column.
BRIEFS = [
    (14, "Pacific Elders accuse Australia over COP31"),
    (15, "NBA: Blazers end 76ers' 5-game win streak 128-111"),
    (16, "UCL: Arsenal v Dortmund, Man City v Napoli"),
    (17, "CAS to rule Tuesday on Senegal AFCON appeal"),
    (18, "Japan factory PMI 53.7, services slip to 50.5"),
    (19, "Japan arms makers brace for order cuts up to 80%"),
    (20, "ASEAN disaster talks; 28 disasters hit 90,200"),
    (21, "WHO chief visits Cuba as healthcare worsens"),
    (22, "Man with Alzheimer's survives 11 days in Amazon"),
    (23, "Soldiers attacked after El Chapo arrest; 8 held"),
    (24, "UK-EU reset bill goes to Parliament Thursday"),
    (25, "Sheffield Shield: Swepson 6/73, Labuschagne out"),
    (26, "Miss Universe 75th final tonight: 116 contestants"),
    (27, "First 'comfort women' statue in Africa, Dec 1"),
    (28, "Ramaphosa faces NCOP on AGOA loss, 30% tariff"),
]

# Map pins (number, x, y) in absolute image coordinates.
# Map area: x 16..316, y 578..846. Pins are 9px-radius circles.
PINS = [
    (1, 296, 660), (2, 268, 656), (3, 204, 632), (4, 242, 668),
    (5, 192, 660), (6, 86, 638), (7, 292, 624), (8, 184, 618),
    (9, 72, 652), (10, 244, 626), (11, 276, 638), (12, 66, 634),
    (13, 212, 672),
]
PIN_R = 9

# Simplified continent polygons (absolute image coordinates, map area).
CONTINENTS = [
    # North America
    [(36, 616), (76, 601), (126, 606), (136, 631), (111, 656),
     (96, 686), (71, 681), (46, 656), (31, 636)],
    # Greenland
    [(131, 591), (151, 588), (156, 606), (136, 611)],
    # South America
    [(91, 706), (121, 701), (136, 726), (126, 766), (106, 786),
     (91, 761), (81, 726)],
    # Europe
    [(171, 611), (201, 606), (216, 621), (206, 641), (186, 646),
     (171, 631)],
    # Africa
    [(176, 661), (216, 656), (231, 676), (221, 716), (201, 746),
     (181, 726), (171, 691)],
    # Asia
    [(221, 606), (296, 601), (311, 626), (301, 661), (266, 676),
     (241, 661), (226, 636)],
    # Australia / Oceania
    [(271, 756), (301, 751), (311, 771), (286, 781), (266, 771)],
]

# 22 DATE CHECK items, 3 columns of 8/7/7. "×" is U+00D7 (renders in DejaVu).
# Items are kept short (no em-dash before the date) so each fits one line
# in its 322px column at 16px.
DATECHECK = [
    "COP31 collapse Sun 22 Nov",
    "Cikande fire Sat 21 Nov",
    "Netanyahu urges Iran strike Sun 22",
    "China spy death sentence Mon 23",
    "Megaspeed; Zelensky Mon 23",
    "India-Nepal Rs15,000cr Mon 23 Nov",
    "Lowy Asia Power Index Mon 23 Nov",
    "West Bengal renamed Mon 23 Nov",
    "Indonesia Expo 2030 Mon 23 Nov",
    "WFP wheat warning Mon 23 Nov",
    "DRC Ituri Ebola responders Sun 22",
    "Samia Suluhu AU roadmap Mon 23",
    "S&P Philippines downgrade Sep 2026",
    "Jollibee UK 30 stores Mon 23 Nov",
    "Thailand wellness $46.5B 12 Nov",
    "ACT protocol review Mon 23 Nov",
    "Seychelles-Nigeria meeting Mon 23",
    "Iran singer flogged 74 lashes Mon 23",
    "India HPV 10M doses Mon 23 Nov",
    "Nigerians killed in Russia Feb 2026",
    "US Senate $9.4bn cuts vote Jul 2025",
    "Japan hosts US Treasury chief 11 Nov",
]
DATECHECK_HEADING = "DATE CHECK — NOT TUESDAY 24 NOVEMBER: first reported earlier"

FOOTER_SOURCES = ("Sources: Reuters · AP · BBC · WSJ · Kyodo News · Al Jazeera · "
                  "PINA · UEFA · The Sun · Fox Sports · Yonhap")
FOOTER_LEGEND = ("REPORTED = carried by the day's wires · CLAIM = one side's "
                 "account, labelled as such · FORECAST = still to happen when drawn")


# ---------------------------------------------------------------- pictorials
def _pict_chart(w, h):
    """Rising market line + gold coins, drawn on its own layer (clipped)."""
    layer = Image.new("RGBA", (w, h), (234, 240, 247, 255))
    d = ImageDraw.Draw(layer)
    # faint grid
    for gy in (h // 3, 2 * h // 3):
        d.line([(0, gy), (w, gy)], fill=(200, 210, 225, 255), width=1)
    # rising red line with arrowhead
    pts = [(6, h - 12), (w // 4, h - 26), (w // 2, h - 18),
           (3 * w // 4, h - 40), (w - 10, 10)]
    d.line(pts, fill=RED, width=4, joint="curve")
    d.polygon([(w - 10, 6), (w - 20, 12), (w - 12, 16)], fill=RED)
    # gold coins
    for cx, cy, r in ((w - 52, h - 16, 11), (w - 28, h - 22, 12)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD,
                  outline=GOLD_DARK, width=2)
        d.text((cx, cy), "$", font=_font("sans-bold", 12),
               fill=GOLD_DARK, anchor="mm")
    return layer


def _pict_jets(w, h):
    """Two fighter-jet silhouettes + red alert arc, clipped to the band."""
    layer = Image.new("RGBA", (w, h), (234, 240, 247, 255))
    d = ImageDraw.Draw(layer)
    # red alert arc sweeping across the top
    d.arc([-w // 4, -h, w + w // 4, h + 26], start=200, end=340,
          fill=RED, width=4)
    # jet 1 (upper left, flying right)
    j1 = [(18, 22), (52, 14), (86, 22), (58, 30), (66, 40),
          (48, 34), (30, 38), (20, 30)]
    d.polygon(j1, fill=NAVY_DARK)
    # jet 2 (lower right, flying right, slightly smaller)
    j2 = [(w - 96, h - 26), (w - 62, h - 34), (w - 28, h - 26),
          (w - 56, h - 18), (w - 48, h - 8), (w - 66, h - 14),
          (w - 84, h - 10), (w - 94, h - 18)]
    d.polygon(j2, fill=NAVY_DARK)
    # speed lines
    d.line([(8, 34), (16, 34)], fill=GREY, width=2)
    d.line([(w - 110, h - 20), (w - 100, h - 20)], fill=GREY, width=2)
    return layer


def _pict_fire(w, h):
    """City buildings + flames, clipped to the band."""
    layer = Image.new("RGBA", (w, h), (234, 240, 247, 255))
    d = ImageDraw.Draw(layer)
    # buildings (dark navy silhouettes along the bottom)
    base = h - 4
    buildings = [(8, 26, 34), (40, 16, 30), (76, 30, 36),
                 (118, 12, 28), (152, 24, 34), (192, 18, 30),
                 (228, 28, 34), (264, 14, 30), (296, 26, 20)]
    for bx, bh, bw in buildings:
        d.rectangle([bx, base - bh, bx + bw, base], fill=NAVY_DARK)
        # lit windows
        for wy in range(base - bh + 5, base - 4, 9):
            d.rectangle([bx + 4, wy, bx + 8, wy + 4], fill=GOLD)
    # flames rising from two buildings
    for fx, fh in ((52, 22), (205, 26), (272, 20)):
        d.polygon([(fx - 9, base - 14), (fx, base - 14 - fh),
                   (fx + 9, base - 14)], fill=(230, 90, 20))
        d.polygon([(fx - 5, base - 14), (fx, base - 14 - fh + 8),
                   (fx + 5, base - 14)], fill=(245, 160, 40))
    # smoke dots
    for sx, sy in ((60, 12), (212, 8), (280, 10)):
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(150, 150, 150))
    return layer


PICT_DRAWERS = {"chart": _pict_chart, "jets": _pict_jets, "fire": _pict_fire}


# ---------------------------------------------------------------- sections
def _draw_masthead(img, d):
    d.rectangle([0, Y_MASTHEAD, W, Y_MASTHEAD + H_MASTHEAD], fill=NAVY)
    f1 = _font("sans-bold", 13)
    f2 = _font("sans", 11)
    inset = 30
    d.text((inset, Y_MASTHEAD + 2), MASTHEAD_LEFT, font=f1, fill=(255, 255, 255))
    w = _text_w(f1, MASTHEAD_RIGHT)
    d.text((W - inset - w, Y_MASTHEAD + 2), MASTHEAD_RIGHT, font=f1,
           fill=(255, 255, 255))
    w2 = _text_w(f2, MASTHEAD_SUB)
    d.text((W - inset - w2, Y_MASTHEAD + 15), MASTHEAD_SUB, font=f2,
           fill=(210, 215, 230))


def _draw_title(img, d):
    size = 48
    while size > 36:
        f = _font("serif-bold", size)
        if _text_w(f, TITLE) <= FONT_TITLE_MAX_W:
            break
        size -= 1
    w = _text_w(f, TITLE)
    x = (W - w) / 2
    d.text((x, Y_TITLE + 1), TITLE, font=f, fill=NAVY)
    return size, w


def _draw_subhead(img, d):
    f = _font("sans-italic", 13)
    w = _text_w(f, SUBHEAD)
    d.text(((W - w) / 2, Y_SUBHEAD), SUBHEAD, font=f, fill=RED)


def _draw_stat(img, d):
    f_num = _font("sans-bold", 18)
    f_cap = _font("sans", 10)
    col_w = CONTENT_W / len(STATS)
    for i, (num, cap) in enumerate(STATS):
        cx = MARGIN + col_w * i + col_w / 2
        d.text((cx, Y_STAT + 1), num, font=f_num, fill=RED, anchor="ma")
        d.text((cx, Y_STAT + 18), cap, font=f_cap, fill=DARK, anchor="ma")


def _draw_region(img, d):
    total = sum(n for _, n, _ in REGION_COLORS)
    x = MARGIN
    bar_y = Y_REGION + 3
    bar_h = 8
    for name, n, color in REGION_COLORS:
        seg_w = CONTENT_W * n / total
        d.rectangle([x, bar_y, x + seg_w, bar_y + bar_h], fill=color)
        x += seg_w
    f = _font("sans", 12)
    label = "STORIES BY REGION · " + " · ".join(
        "%s %d" % (name, n) for name, n, _ in REGION_COLORS)
    d.text((MARGIN, Y_REGION + 14), label, font=f, fill=DARK)


def _draw_timeline(img, d):
    f = _font("sans", FONT_TIMELINE)
    y = Y_TIMELINE + 1
    for line in TIMELINE:
        d.text((MARGIN, y), line, font=f, fill=DARK)
        y += FONT_TIMELINE + 1


def _card_frame(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PAPER,
                outline=(200, 190, 165), width=1)


def _draw_leads(img, d):
    gap = 8
    cw = (CONTENT_W - 2 * gap) // 3
    f_kick = _font("sans-bold", 12)
    f_head = _font("sans-bold", 20)
    f_body = _font("sans", FONT_BODY)
    f_src = _font("sans", 11)
    f_tag = _font("sans-bold", 12)
    for i, lead in enumerate(LEADS):
        x = MARGIN + i * (cw + gap)
        y = Y_BIG
        _card_frame(d, x, y, cw, H_BIG)
        # pictorial band (clipped layer pasted inside the card)
        pict = PICT_DRAWERS[lead["pict"]](cw - 2, PICT_H)
        img.paste(pict, (x + 1, y + 1))
        ty = y + PICT_H + 2
        d.text((x + 6, ty), lead["kicker"], font=f_kick, fill=RED)
        ty += 13
        for line in _wrap(f_head, lead["headline"], cw - 12):
            d.text((x + 6, ty), line, font=f_head, fill=NAVY)
            ty += 21
        for line in _wrap(f_body, lead["body"], cw - 12):
            d.text((x + 6, ty), line, font=f_body, fill=DARK)
            ty += 19
        # sources + tag on the card's bottom line
        d.text((x + 6, y + H_BIG - 14), lead["sources"], font=f_src, fill=GREY)
        tw = _text_w(f_tag, lead["tag"])
        d.text((x + cw - 6 - tw, y + H_BIG - 14), lead["tag"], font=f_tag,
               fill=RED)


def _draw_medium(img, d):
    gap = 8
    cw = (CONTENT_W - 4 * gap) // 5
    row_h = 104
    f_num = _font("sans-bold", 13)
    f_kick = _font("sans-bold", 11)
    f_head = _font("sans-bold", 17)
    f_body = _font("sans", FONT_BODY)
    f_src = _font("sans", 11)
    f_tag = _font("sans-bold", 11)
    for i, card in enumerate(MEDIUM):
        row, col = divmod(i, 5)
        x = MARGIN + col * (cw + gap)
        y = Y_MED + row * (row_h + 4)
        _card_frame(d, x, y, cw, row_h)
        ty = y + 2
        d.text((x + 6, ty), "%d" % card["num"], font=f_num, fill=RED)
        kw = _text_w(f_kick, card["kicker"])
        d.text((x + cw - 6 - kw, ty), card["kicker"], font=f_kick, fill=RED)
        ty += 12
        for line in _wrap(f_head, card["headline"], cw - 12):
            d.text((x + 6, ty), line, font=f_head, fill=NAVY)
            ty += 19
        for line in _wrap(f_body, card["body"], cw - 12):
            d.text((x + 6, ty), line, font=f_body, fill=DARK)
            ty += 18
        d.text((x + 6, y + row_h - 14), card["sources"], font=f_src, fill=GREY)
        tw = _text_w(f_tag, card["tag"])
        d.text((x + cw - 6 - tw, y + row_h - 14), card["tag"], font=f_tag,
               fill=RED)


def _draw_map_briefs(img, d):
    map_x0, map_y0 = MARGIN, Y_MAP + 14
    map_w, map_h = 300, H_MAP - 16
    f_head = _font("sans-bold", 12)
    d.text((MARGIN, Y_MAP), "WHERE IT HAPPENED — 13 LEADS PINNED",
           font=f_head, fill=DARK)
    # map panel
    d.rectangle([map_x0, map_y0, map_x0 + map_w, map_y0 + map_h],
                fill=SKY, outline=(180, 195, 215), width=1)
    for poly in CONTINENTS:
        d.polygon(poly, fill=LAND, outline=LAND_LINE)
    f_pin = _font("sans-bold", 10)
    for num, px, py in PINS:
        d.ellipse([px - PIN_R, py - PIN_R, px + PIN_R, py + PIN_R],
                  fill=RED, outline=(255, 255, 255), width=1)
        d.text((px, py), str(num), font=f_pin, fill=(255, 255, 255),
               anchor="mm")
    # briefs column
    bx = map_x0 + map_w + 10
    bw = W - MARGIN - bx
    d.text((bx, Y_MAP), "ALSO ON TUESDAY 24 NOVEMBER", font=f_head, fill=DARK)
    f_brief = _font("sans", FONT_BRIEF)
    by = Y_MAP + 12
    for num, text in BRIEFS:
        line = "%d. %s" % (num, text)
        d.text((bx, by), line, font=f_brief, fill=DARK)
        by += FONT_BRIEF


def _draw_datecheck(img, d):
    d.rectangle([MARGIN, Y_DATE, W - MARGIN, Y_DATE + H_DATE],
                outline=RED, width=2)
    f_head = _font("sans-bold", 13)
    d.text((MARGIN + 6, Y_DATE + 4), DATECHECK_HEADING, font=f_head, fill=RED)
    f_item = _font("sans", FONT_DATECHECK)
    cols = [DATECHECK[0:8], DATECHECK[8:15], DATECHECK[15:22]]
    col_w = (CONTENT_W - 12) // 3
    y0 = Y_DATE + 19
    for ci, col in enumerate(cols):
        cx = MARGIN + 6 + ci * col_w
        yy = y0
        for item in col:
            d.text((cx, yy), "× " + item, font=f_item, fill=RED_DARK)
            yy += 16.5


def _draw_footer(img, d):
    f = _font("sans", 10)
    d.text((MARGIN, Y_FOOTER + 0), FOOTER_SOURCES, font=f, fill=GREY)
    d.text((MARGIN, Y_FOOTER + 10), FOOTER_LEGEND, font=f, fill=GREY)


# ---------------------------------------------------------------- render
def render():
    """Build the 1024x1024 image and return the PIL Image."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    _draw_masthead(img, d)
    _draw_title(img, d)
    _draw_subhead(img, d)
    _draw_stat(img, d)
    _draw_region(img, d)
    _draw_timeline(img, d)
    _draw_leads(img, d)
    _draw_medium(img, d)
    _draw_map_briefs(img, d)
    _draw_datecheck(img, d)
    _draw_footer(img, d)
    return img


def _output_path():
    out_dir = (os.environ.get("MAKEFUN_OUTPUT_DIR")
               or os.environ.get("ENTRY_OUTPUT")
               or "/output")
    if out_dir.endswith("entry.png"):
        return out_dir
    return os.path.join(out_dir, "entry.png")


def _fallback_copy(out_path):
    """Copy the committed entry.png to the output path; return True on success."""
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    try:
        if os.path.exists(src):
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            shutil.copyfile(src, out_path)
            return True
    except Exception:
        pass
    return False


def main():
    out_path = _output_path()
    try:
        if not _PIL_OK:
            raise RuntimeError("Pillow unavailable")
        img = render()
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        img.save(out_path, "PNG")
        print("wrote %s (%dx%d)" % (out_path, W, H))
        return 0
    except Exception as exc:  # noqa: BLE001 - any render failure falls back
        print("render failed (%s); falling back to committed entry.png" % exc,
              file=sys.stderr)
        if _fallback_copy(out_path):
            print("copied committed entry.png to %s" % out_path)
            return 0
        print("fallback also failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
