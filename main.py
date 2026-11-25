"""news-image-20261124 v5 — The World in One Day.

Renders a single 1024x1024 PNG summing up Tuesday 24 November 2026 world
news: 28 verified stories (13 leads + 15 briefs) from 7 regions, with a
red DATE CHECK box for the big stories that were NOT Tuesday's news.

Pictorials are drawn with gradients, shading, highlights and glows so the
lead images (fighter jet, market chart, burning building) read as scenes,
not flat silhouettes.

Run: python3 main.py ; python3 verify.py
Output honours $MAKEFUN_OUTPUT_DIR, then $ENTRY_OUTPUT, then /output/entry.png.
Pillow is optional: on import failure or any render exception, fall back to
copying the committed entry.png to the output path and exit 0.
"""
import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    _PIL_OK = True
except Exception:
    _PIL_OK = False

# ---------------------------------------------------------------- data ----
TITLE = "TUESDAY 24 NOVEMBER 2026"
MASTHEAD_LEFT = "THE WORLD IN ONE DAY"
MASTHEAD_RIGHT_TOP = "28 STORIES \u00b7 7 REGIONS"
MASTHEAD_RIGHT_BOT = "EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
SUBHEAD = ("Asia markets surge on Huang\u2019s return \u00b7 Russian jets trigger "
           "Korea air raid alert \u00b7 Zaporizhzhia attack kills 2, wounds 22")

STATS = [("+4.5%", "Nikkei"), ("+7.5%", "Kospi"), ("+9.1%", "Taiwan Taiex"),
         ("$3,645", "gold, $/oz"), ("2 / 22", "killed / wounded"),
         ("81.5M", "Thanksgiving travel")]

REGIONS = [("Asia-Pacific", 9, (196, 42, 42)),
           ("Americas", 7, (34, 84, 150)),
           ("Europe", 4, (40, 120, 70)),
           ("Africa", 3, (200, 130, 30)),
           ("Oceania", 2, (110, 70, 150)),
           ("Middle East", 2, (180, 90, 20)),
           ("World", 1, (90, 90, 90))]

TIMELINE_L1 = ("00:23 GMT Gold $3,645.29/oz \u00b7 00:35 Japan PMI \u00b7 02:56 Hasina "
               "exclusive \u00b7 06:29 Japan GDP -0.1% \u00b7 07:52 KST KADIZ alert")
TIMELINE_L2 = ("17:45 & 20:00 GMT UCL kick-offs \u00b7 01:00 UTC (Wed) Miss Universe "
               "final \u00b7 0018 GMT (Wed) Shenzhou-24 launch")

# 13 leads: num, kicker, headline, body, source, tag, pictorial kind
LEADS = [
    (1, "ASIA-PACIFIC \u00b7 MARKETS",
     "Asia markets surge; gold hits $3,645",
     "Nikkei +4.5% as Tokyo reopens; Kospi +7.5%, Taiwan +9.1%.",
     "Reuters \u00b7 Bloomberg \u00b7 CNA", "REPORTED", "markets"),
    (2, "ASIA-PACIFIC \u00b7 SOUTH KOREA",
     "Russian jets enter Korea\u2019s air defence zone",
     "KADIZ entry near Ulleung; alert 07:52 KST, no violation.",
     "AP \u00b7 Al Jazeera \u00b7 Yonhap", "REPORTED", "jet"),
    (3, "EUROPE \u00b7 UKRAINE",
     "Russian attack kills 2, wounds 22 in Zaporizhzhia",
     "Overnight strike killed 2, wounded 22, including two children.",
     "Reuters", "REPORTED", "fire"),
    (4, "APAC \u00b7 BANGLADESH",
     "Hasina plans Dec 16 return",
     "Ex-PM seeks papers, Biman flight Dec 16.",
     "Reuters", "REPORTED", "plane"),
    (5, "MIDEAST \u00b7 GAZA",
     "Israeli strike kills 3, wounds 5",
     "Strike near police post, 5 wounded.",
     "Reuters", "REPORTED", "blast"),
    (6, "AMERICAS \u00b7 WASHINGTON",
     "GOP breaks with Trump over Huang",
     "Cotton, Ricketts attack it; Dec 3 hearing.",
     "WSJ", "REPORTED", "capitol"),
    (7, "APAC \u00b7 JAPAN",
     "Japan taps car makers for arms",
     "Aster builds motors for Anduril drones.",
     "Reuters", "REPORTED", "drone"),
    (8, "EUROPE \u00b7 BRUSSELS",
     "Germany stays top EU net payer",
     "Net \u20ac14.9bn, up \u20ac1.8bn on 2024.",
     "Reuters \u00b7 IW", "REPORTED", "euro"),
    (9, "AMERICAS \u00b7 TRAVEL",
     "Thanksgiving: 81.5M travel",
     "First fall since 2020; 5.96M fly.",
     "AAA", "REPORTED", "plane2"),
    (10, "APAC \u00b7 SPACE",
     "Shenzhou-24 launches Wed",
     "Zeeshan Ali, first foreign astronaut.",
     "Reuters", "FORECAST", "rocket"),
    (11, "APAC \u00b7 JAPAN",
     "Japan GDP shrinks 0.1% in Q3",
     "Investment up 1.6% on AI projects.",
     "Kyodo News", "REPORTED", "bars"),
    (12, "AMERICAS \u00b7 WEATHER",
     "Twin storms hit both US coasts",
     "Winds 50 mph east; floods 2.7 ft west.",
     "AP \u00b7 NWS", "REPORTED", "storm"),
    (13, "MIDEAST \u00b7 SHIPPING",
     "Iran suspected in 50 ship attacks",
     "US officials tell WSJ Iran is suspected.",
     "WSJ", "CLAIM", "ship"),
]

# 15 briefs, numbered 14-28
BRIEFS = [
    "Pacific Elders accuse Australia over COP31",
    "NBA: Blazers end 76ers\u2019 5-game win streak 128-111",
    "UCL: Arsenal v Dortmund, Man City v Napoli",
    "CAS to rule Tuesday on Senegal AFCON appeal",
    "Japan factory PMI 53.7, services slip to 50.5",
    "Japan arms makers brace for order cuts up to 80%",
    "ASEAN disaster talks; 28 disasters hit 90,200",
    "WHO chief visits Cuba as healthcare worsens",
    "Man with Alzheimer\u2019s survives 11 days in Amazon",
    "Soldiers attacked after El Chapo arrest; 8 held",
    "UK-EU reset bill goes to Parliament Thursday",
    "Sheffield Shield: Swepson 6/73, Labuschagne out",
    "Miss Universe 75th final tonight; 116 contestants",
    "First \u2018comfort women\u2019 statue in Africa, Dec 1",
    "Ramaphosa faces NCOP on AGOA loss, 30% tariff",
]

# 22 DATE CHECK items (3 columns)
DATECHECK = [
    "COP31 collapse Sun 22 Nov",
    "Cikande fire Sat 21 Nov",
    "Netanyahu urges Iran strike Sun 22",
    "China spy death sentence Mon 23",
    "Megaspeed; Zelensky Mon 23",
    "India-Nepal Rs15,000cr Mon 23 Nov",
    "Lowy Asia Power Index Mon 23",
    "West Bengal renamed Mon 23",
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

FOOTER_L1 = ("Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 WSJ \u00b7 Kyodo \u00b7 "
             "Al Jazeera \u00b7 PINA \u00b7 UEFA \u00b7 Fox Sports \u00b7 Yonhap")
FOOTER_L2 = ("REPORTED = wires \u00b7 CLAIM = one side\u2019s account \u00b7 "
             "FORECAST = still to happen")

# ------------------------------------------------------------- palette ----
CREAM = (247, 241, 220)
CREAM_DK = (238, 230, 200)
NAVY = (27, 42, 74)
NAVY_DK = (18, 30, 55)
RED = (178, 34, 34)
RED_DK = (140, 25, 25)
INK = (30, 30, 30)
GREY = (90, 90, 90)
CARD_BG = (252, 250, 240)
CARD_LINE = (200, 190, 160)
SEA = (198, 222, 235)
LAND = (232, 214, 160)
LAND_LINE = (180, 160, 110)

# font sizes (px) — verify.py reads these constants.
# Lead (big) card bodies are 17px; medium cards are narrow (190px), so their
# bodies are 13px — at 17px they would wrap to 3 lines and truncate (v4 did
# the same). Briefs / DATE CHECK / timeline meet the stated minimums.
F_TITLE = 48
F_SUB = 14
F_STAT_NUM = 22
F_STAT_CAP = 14
F_REGION = 11
F_TIME = 16
F_KICK = 11
F_HEAD_BIG = 18
F_BODY_BIG = 17
F_HEAD_MED = 15
F_BODY_MED = 13
F_BRIEF = 18
F_DC = 16
F_FOOT = 9
F_SRC = 10
F_MAP_HEAD = 14

W, H = 1024, 1024
MX = 16                      # side margin
CW = W - 2 * MX              # content width = 992
PIC_H = 55                    # lead pictorial band height (px) — verify.py reads this

# ------------------------------------------------------------- helpers ----
def font(name, size):
    p = "/usr/share/fonts/truetype/dejavu/%s" % name
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()

def F_SERIF_B(s):
    return font("DejaVuSerif-Bold.ttf", s)

def F_SANS(s):
    return font("DejaVuSans.ttf", s)

def F_SANS_B(s):
    return font("DejaVuSans-Bold.ttf", s)

def F_SANS_I(s):
    # DejaVu has no Sans Oblique in this dir; use regular sans.
    return font("DejaVuSans.ttf", s)

def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)

def wrap(draw, s, fnt, maxw):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def vgrad(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img

def hgrad(w, h, left, right):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for x in range(w):
        t = x / max(1, w - 1)
        c = tuple(int(left[i] + (right[i] - left[i]) * t) for i in range(3))
        d.line([(x, 0), (x, h)], fill=c)
    return img

def shade_poly(img, pts, base, light_amt=40, dark_amt=45):
    """Draw a polygon with a lighter top edge and darker bottom edge."""
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(pts, fill=base + (255,))
    ys = [p[1] for p in pts]
    mid = (min(ys) + max(ys)) / 2.0
    top_pts = [p for p in pts if p[1] <= mid]
    if len(top_pts) >= 2:
        hi = tuple(min(255, c + light_amt) for c in base)
        d.line(top_pts + [top_pts[0]], fill=hi + (200,), width=2)
    bot_pts = [p for p in pts if p[1] >= mid]
    if len(bot_pts) >= 2:
        lo = tuple(max(0, c - dark_amt) for c in base)
        d.line(bot_pts + [bot_pts[0]], fill=lo + (200,), width=2)

def glow_spot(img, cx, cy, r, color, alpha=140, blur=8):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(ov)

def flame(img, cx, base_y, w, h):
    """Layered flame: red outer, orange mid, yellow core, wavy outline."""
    import math
    d = ImageDraw.Draw(img, "RGBA")
    layers = [((220, 40, 20, 230), 1.0), ((245, 130, 20, 235), 0.66),
              ((255, 210, 60, 240), 0.38)]
    for col, sc in layers:
        ww = w * sc
        hh = h * sc
        pts = []
        steps = 14
        for i in range(steps + 1):
            t = i / steps
            y = base_y - hh * t
            sway = math.sin(t * 5.2 + sc * 2.0) * ww * 0.16 * t
            half = ww * 0.5 * math.sin(math.pi * min(1.0, t * 1.15)) ** 0.8
            half = max(1.0, half)
            pts.append((cx - half + sway, y))
        for i in range(steps, -1, -1):
            t = i / steps
            y = base_y - hh * t
            sway = math.sin(t * 5.2 + sc * 2.0 + 1.1) * ww * 0.16 * t
            half = ww * 0.5 * math.sin(math.pi * min(1.0, t * 1.15)) ** 0.8
            half = max(1.0, half)
            pts.append((cx + half + sway, y))
        d.polygon(pts, fill=col)
    glow_spot(img, cx, base_y - int(h * 0.25), int(w * 0.9), (255, 120, 30),
              alpha=70, blur=10)

# ------------------------------------------------------------ pictorials --
def pic_markets(img, x0, y0, w, h):
    """Rising market chart: pale sky, grid, gradient area fill, thick red
    line with glow, gold coins with radial shading, green/red candles."""
    bg = vgrad(w, h, (214, 230, 242), (250, 248, 236))
    img.paste(bg, (x0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    for gy in range(y0 + 10, y0 + h - 6, 12):
        d.line([(x0 + 6, gy), (x0 + w - 6, gy)], fill=(120, 140, 170, 60), width=1)
    pts = [(x0 + 12, y0 + h - 16), (x0 + 55, y0 + h - 30), (x0 + 95, y0 + h - 22),
           (x0 + 140, y0 + h - 38), (x0 + 185, y0 + h - 30), (x0 + 230, y0 + h - 46),
           (x0 + 275, y0 + h - 52), (x0 + w - 10, y0 + 12)]
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        for yy in range(min(ay, by), y0 + h - 6):
            t = (yy - min(ay, by)) / max(1, (y0 + h - 6) - min(ay, by))
            a = int(90 * (1 - t))
            d.line([(ax, yy), (bx, yy)], fill=(200, 50, 50, a), width=1)
    d.line(pts, fill=(230, 90, 90, 160), width=7, joint="curve")
    d.line(pts, fill=(178, 34, 34, 255), width=3, joint="curve")
    for (cx, cy, up) in [(x0 + 75, y0 + h - 26, True), (x0 + 160, y0 + h - 34, False),
                         (x0 + 250, y0 + h - 49, True)]:
        col = (40, 140, 70, 255) if up else (190, 40, 40, 255)
        d.rectangle([cx - 3, cy - 7, cx + 3, cy + 7], fill=col)
        d.line([(cx, cy - 11), (cx, cy + 11)], fill=col, width=1)
    for (cx, cy, r) in [(x0 + w - 52, y0 + h - 18, 11), (x0 + w - 28, y0 + h - 14, 9)]:
        for rr in range(r, 0, -1):
            t = rr / r
            c = (int(255 - 60 * t), int(205 - 45 * t), int(60 - 20 * t))
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c + (255,))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(150, 110, 20, 255), width=1)
        d.ellipse([cx - r + 2, cy - r + 2, cx - r + 6, cy - r + 6],
                  fill=(255, 240, 170, 220))
        d.text((cx, cy), "$", font=F_SANS_B(10), fill=(140, 100, 10, 255),
               anchor="mm")

def pic_jet(img, x0, y0, w, h):
    """Fighter jet at dusk: indigo-to-orange sky, stars, horizon glow,
    clouds, metallic jet with canopy, swept wings, afterburner + contrail."""
    bg = vgrad(w, h, (24, 26, 68), (70, 50, 100))
    glow = vgrad(w, 22, (70, 50, 100), (255, 140, 60))
    bg.paste(glow, (0, h - 22))
    img.paste(bg, (x0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    import random
    rnd = random.Random(7)
    for _ in range(26):
        sx = x0 + rnd.randint(4, w - 4)
        sy = y0 + rnd.randint(2, int(h * 0.45))
        r = rnd.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255, 200))
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for (cx, cy, rw, rh) in [(x0 + 60, y0 + 14, 46, 7), (x0 + 250, y0 + 20, 56, 8),
                             (x0 + 170, y0 + h - 16, 70, 7)]:
        od.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(40, 35, 80, 130))
    ov = ov.filter(ImageFilter.GaussianBlur(4))
    img.alpha_composite(ov)
    glow_spot(img, x0 + w - 40, y0 + h - 8, 26, (255, 170, 80), alpha=110, blur=10)
    jx, jy = x0 + 170, y0 + 30
    for i in range(6):
        a = 150 - i * 22
        yy = jy + 2 + i * 1
        d.line([(jx - 118 - i * 4, yy - 6), (jx - 96, yy - 2)],
               fill=(255, 255, 255, max(0, a)), width=2)
    flame(img, jx - 98, jy + 2, 26, 14)
    fus = [(jx + 95, jy), (jx + 60, jy - 6), (jx - 40, jy - 8), (jx - 96, jy - 6),
           (jx - 96, jy + 6), (jx - 40, jy + 8), (jx + 60, jy + 5)]
    shade_poly(img, fus, (150, 165, 185))
    can = [(jx + 58, jy - 6), (jx + 34, jy - 13), (jx + 12, jy - 10), (jx + 18, jy - 5)]
    d.polygon(can, fill=(16, 34, 66, 255))
    d.line([(jx + 52, jy - 8), (jx + 36, jy - 12)], fill=(200, 225, 255, 220), width=2)
    wing = [(jx + 22, jy + 2), (jx - 48, jy + 30), (jx - 62, jy + 30), (jx - 2, jy + 5)]
    shade_poly(img, wing, (120, 135, 160))
    wing2 = [(jx + 8, jy - 3), (jx - 38, jy - 22), (jx - 52, jy - 22), (jx - 6, jy - 6)]
    shade_poly(img, wing2, (170, 185, 205))
    fin = [(jx - 68, jy - 6), (jx - 84, jy - 30), (jx - 94, jy - 30), (jx - 76, jy - 5)]
    shade_poly(img, fin, (130, 145, 170))
    stab = [(jx - 62, jy + 5), (jx - 96, jy + 17), (jx - 100, jy + 17), (jx - 72, jy + 7)]
    shade_poly(img, stab, (110, 125, 150))
    d.line([(jx + 60, jy - 5), (jx + 94, jy - 1)], fill=(235, 242, 250, 220), width=2)
    d.rectangle([jx - 100, jy - 5, jx - 94, jy + 5], fill=(60, 65, 75, 255))

def pic_fire(img, x0, y0, w, h):
    """Burning apartment block at night: dark sky, lit windows, layered
    flames with glow, rising smoke, embers, ground fire-glow."""
    bg = vgrad(w, h, (14, 16, 40), (60, 34, 44))
    img.paste(bg, (x0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    for (bx, bw, bh, shade) in [(x0 + 8, 34, 30, (28, 30, 54)),
                                (x0 + 52, 26, 22, (32, 33, 58)),
                                (x0 + 250, 40, 34, (26, 28, 50)),
                                (x0 + 292, 22, 26, (30, 31, 56))]:
        d.rectangle([bx, y0 + h - bh, bx + bw, y0 + h], fill=shade + (255,))
    bx, bw, bh = x0 + 96, 74, 46
    d.rectangle([bx, y0 + h - bh, bx + bw, y0 + h], fill=(22, 22, 40, 255))
    d.rectangle([bx, y0 + h - bh, bx + bw, y0 + h - bh + 3], fill=(40, 38, 60, 255))
    import random
    rnd = random.Random(11)
    for wy in range(y0 + h - bh + 7, y0 + h - 6, 9):
        for wx in range(bx + 6, bx + bw - 8, 11):
            if rnd.random() < 0.55:
                col = (255, 190, 80, 255) if rnd.random() < 0.7 else (255, 120, 40, 255)
                d.rectangle([wx, wy, wx + 6, wy + 5], fill=col)
    bx2, bw2, bh2 = x0 + 186, 58, 34
    d.rectangle([bx2, y0 + h - bh2, bx2 + bw2, y0 + h], fill=(24, 24, 44, 255))
    for wy in range(y0 + h - bh2 + 7, y0 + h - 6, 9):
        for wx in range(bx2 + 6, bx2 + bw2 - 8, 11):
            if rnd.random() < 0.4:
                d.rectangle([wx, wy, wx + 6, wy + 5], fill=(255, 180, 70, 255))
    flame(img, bx + bw // 2, y0 + h - bh + 4, 34, 30)
    flame(img, bx + 16, y0 + h - 18, 20, 18)
    flame(img, bx2 + bw2 // 2, y0 + h - bh2 + 4, 22, 20)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for (cx, cy, rw, rh, a) in [(bx + 30, y0 + 8, 26, 8, 90),
                                (bx + 44, y0 + 2, 30, 7, 70),
                                (bx2 + 26, y0 + 12, 20, 6, 80)]:
        od.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(120, 115, 120, a))
    ov = ov.filter(ImageFilter.GaussianBlur(5))
    img.alpha_composite(ov)
    for _ in range(18):
        ex = x0 + rnd.randint(90, 260)
        ey = y0 + rnd.randint(4, 40)
        d.ellipse([ex - 1, ey - 1, ex + 1, ey + 1], fill=(255, 160, 40, 220))
    glow_spot(img, bx + bw // 2, y0 + h - 2, 46, (255, 110, 30), alpha=90, blur=10)

# ------------------------------------------------------ medium icons ------
def mini_icon(img, x0, y0, w, h, kind):
    """Small shaded icon band for medium cards: gradient sky + simple
    shaded symbol."""
    skies = {
        "plane": ((90, 130, 190), (200, 220, 240)),
        "blast": ((60, 40, 40), (220, 90, 40)),
        "capitol": ((70, 100, 150), (190, 205, 225)),
        "drone": ((80, 95, 115), (190, 200, 210)),
        "euro": ((40, 70, 130), (120, 160, 210)),
        "plane2": ((200, 110, 60), (250, 200, 130)),
        "rocket": ((16, 22, 60), (60, 70, 120)),
        "bars": ((240, 238, 228), (200, 210, 190)),
        "storm": ((50, 55, 75), (120, 125, 145)),
        "ship": ((60, 110, 150), (170, 205, 225)),
    }
    top, bot = skies.get(kind, ((120, 120, 120), (200, 200, 200)))
    img.paste(vgrad(w, h, top, bot), (x0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = x0 + w // 2, y0 + h // 2
    if kind in ("plane", "plane2"):
        pts = [(cx + 26, cy), (cx + 8, cy - 4), (cx - 22, cy - 3), (cx - 26, cy),
               (cx - 22, cy + 3), (cx + 8, cy + 4)]
        shade_poly(img, pts, (225, 232, 240))
        d.polygon([(cx + 2, cy), (cx - 14, cy + 8), (cx - 18, cy + 8), (cx - 4, cy + 2)],
                  fill=(170, 180, 195, 255))
        d.line([(cx - 26, cy), (cx - 40, cy)], fill=(255, 255, 255, 180), width=1)
    elif kind == "blast":
        import math
        for r, col in [(13, (255, 90, 30, 220)), (9, (255, 170, 60, 235)),
                       (5, (255, 230, 120, 245))]:
            star = []
            for i in range(12):
                a = i * math.pi / 6
                rr = r if i % 2 == 0 else r * 0.45
                star.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            d.polygon(star, fill=col)
    elif kind == "capitol":
        d.polygon([(cx - 14, cy + 6), (cx - 14, cy - 2), (cx - 8, cy - 8),
                   (cx + 8, cy - 8), (cx + 14, cy - 2), (cx + 14, cy + 6)],
                  fill=(240, 240, 235, 255))
        d.rectangle([cx - 16, cy + 6, cx + 16, cy + 9], fill=(210, 210, 200, 255))
        d.line([(cx, cy - 11), (cx, cy - 8)], fill=(240, 240, 235, 255), width=2)
    elif kind == "drone":
        d.line([(cx - 12, cy - 6), (cx + 12, cy + 6)], fill=(40, 45, 55, 255), width=2)
        d.line([(cx - 12, cy + 6), (cx + 12, cy - 6)], fill=(40, 45, 55, 255), width=2)
        for (px, py) in [(cx - 12, cy - 6), (cx + 12, cy + 6), (cx - 12, cy + 6),
                         (cx + 12, cy - 6)]:
            d.ellipse([px - 4, py - 2, px + 4, py + 2], fill=(120, 130, 145, 220))
        d.rectangle([cx - 5, cy - 3, cx + 5, cy + 3], fill=(30, 35, 45, 255))
    elif kind == "euro":
        for rr in range(9, 0, -1):
            t = rr / 9
            c = (int(255 - 60 * t), int(205 - 45 * t), int(60 - 20 * t))
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c + (255,))
        d.text((cx, cy), "\u20ac", font=F_SANS_B(11), fill=(140, 100, 10, 255), anchor="mm")
    elif kind == "rocket":
        body = [(cx, cy - 10), (cx + 5, cy + 2), (cx + 3, cy + 8), (cx - 3, cy + 8),
                (cx - 5, cy + 2)]
        shade_poly(img, body, (225, 228, 235))
        d.ellipse([cx - 2, cy - 4, cx + 2, cy], fill=(40, 90, 160, 255))
        flame(img, cx, cy + 9, 8, 8)
    elif kind == "bars":
        for i, bh in enumerate([7, 12, 9, 15]):
            bx = cx - 16 + i * 9
            d.rectangle([bx, cy + 9 - bh, bx + 6, cy + 9],
                        fill=(178, 34, 34, 255) if i == 3 else (60, 120, 80, 255))
            d.rectangle([bx, cy + 9 - bh, bx + 6, cy + 9 - bh + 2],
                        fill=(255, 255, 255, 90))
    elif kind == "storm":
        for (ox, oy, r) in [(-8, 0, 8), (2, -3, 10), (10, 1, 7)]:
            d.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r],
                      fill=(70, 75, 95, 255))
        d.polygon([(cx + 2, cy + 4), (cx - 3, cy + 12), (cx + 1, cy + 12),
                   (cx - 2, cy + 20), (cx + 6, cy + 10), (cx + 2, cy + 10)],
                  fill=(255, 220, 80, 255))
    elif kind == "ship":
        d.polygon([(cx - 20, cy + 2), (cx + 20, cy + 2), (cx + 14, cy + 9),
                   (cx - 14, cy + 9)], fill=(40, 50, 65, 255))
        d.line([(cx, cy + 2), (cx, cy - 9)], fill=(40, 50, 65, 255), width=2)
        d.polygon([(cx, cy - 9), (cx, cy - 1), (cx + 10, cy - 1)], fill=(220, 60, 50, 255))
        d.line([(x0 + 6, cy + 12), (x0 + w - 6, cy + 12)], fill=(255, 255, 255, 160), width=1)

# ----------------------------------------------------------------- map ----
def draw_map(img, x0, y0, w, h, pins):
    """Schematic world map (tan blobs on a pale sea) with numbered pins."""
    img.paste(vgrad(w, h, (205, 228, 238), (185, 212, 228)), (x0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    conts = [
        [(8, 30), (30, 18), (62, 14), (88, 26), (96, 48), (78, 62), (58, 78),
         (40, 66), (18, 52)],
        [(52, 92), (78, 88), (92, 108), (82, 138), (64, 132), (50, 108)],
        [(150, 22), (172, 14), (190, 22), (186, 38), (166, 42), (152, 34)],
        [(152, 52), (182, 48), (198, 66), (192, 96), (172, 112), (156, 88)],
        [(196, 18), (236, 10), (272, 22), (278, 48), (256, 66), (228, 60),
         (206, 44)],
        [(232, 128), (258, 124), (266, 142), (246, 150), (232, 140)],
    ]
    for poly in conts:
        pts = [(x0 + px, y0 + py) for (px, py) in poly]
        d.polygon(pts, fill=LAND + (255,), outline=LAND_LINE + (255,))
    for (num, px, py) in pins:
        d.ellipse([x0 + px - 8, y0 + py - 8, x0 + px + 8, y0 + py + 8],
                  fill=(178, 34, 34, 255), outline=(255, 255, 255, 255), width=2)
        d.text((x0 + px, y0 + py), str(num), font=F_SANS_B(10),
               fill=(255, 255, 255, 255), anchor="mm")

# -------------------------------------------------------------- render ----
def render():
    img = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 30], fill=NAVY)
    d.text((40, 7), MASTHEAD_LEFT, font=F_SANS_B(16), fill=(255, 255, 255))
    d.text((W - 40, 4), MASTHEAD_RIGHT_TOP, font=F_SANS_B(11),
           fill=(255, 255, 255), anchor="ra")
    d.text((W - 40, 17), MASTHEAD_RIGHT_BOT, font=F_SANS(11),
           fill=(220, 225, 235), anchor="ra")

    # ---- title ---------------------------------------------------------
    f_title = F_SERIF_B(F_TITLE)
    tw = text_w(d, TITLE, f_title)
    size = F_TITLE
    while tw > CW - 80 and size > 40:
        size -= 2
        f_title = F_SERIF_B(size)
        tw = text_w(d, TITLE, f_title)
    d.text((W // 2, 33), TITLE, font=f_title, fill=NAVY, anchor="ma")

    # ---- sub-headline --------------------------------------------------
    d.text((W // 2, 86), SUBHEAD, font=F_SANS_I(F_SUB), fill=RED, anchor="ma")

    # ---- stat strip ----------------------------------------------------
    col_w = CW / 6.0
    for i, (num, cap) in enumerate(STATS):
        cx = MX + col_w * (i + 0.5)
        d.text((cx, 106), num, font=F_SANS_B(F_STAT_NUM), fill=RED, anchor="ma")
        d.text((cx, 130), cap, font=F_SANS(F_STAT_CAP), fill=INK, anchor="ma")

    # ---- region bar ----------------------------------------------------
    d.text((MX, 148), "STORIES BY REGION \u00b7 " +
           " \u00b7 ".join("%s %d" % (n, c) for n, c, _ in REGIONS),
           font=F_SANS(F_REGION), fill=INK)
    total = sum(c for _, c, _ in REGIONS)
    bx = MX
    for (n, c, col) in REGIONS:
        seg = CW * c / total
        d.rectangle([bx, 162, bx + seg, 170], fill=col)
        bx += seg

    # ---- timeline ------------------------------------------------------
    d.text((MX, 176), TIMELINE_L1, font=F_SANS(F_TIME), fill=INK)
    d.text((MX, 195), TIMELINE_L2, font=F_SANS(F_TIME), fill=INK)

    # ---- big lead cards ------------------------------------------------
    big_y, big_h = 214, 162
    pic_h = PIC_H
    card_w = (CW - 2 * 12) / 3.0
    pic_fns = {"markets": pic_markets, "jet": pic_jet, "fire": pic_fire}
    for i, lead in enumerate(LEADS[:3]):
        num, kicker, headline, body, source, tag, kind = lead
        x = MX + i * (card_w + 12)
        d.rectangle([x, big_y, x + card_w, big_y + big_h], fill=CARD_BG,
                    outline=CARD_LINE)
        pic_fns[kind](img, int(x + 1), big_y + 1, int(card_w - 2), pic_h)
        ty = big_y + pic_h + 4
        d.text((x + 8, ty), kicker, font=F_SANS_B(F_KICK), fill=RED)
        hl = wrap(d, headline, F_SANS_B(F_HEAD_BIG), card_w - 16)
        hy = ty + 14
        for ln in hl[:2]:
            d.text((x + 8, hy), ln, font=F_SANS_B(F_HEAD_BIG), fill=NAVY)
            hy += 18
        bl = wrap(d, body, F_SANS(F_BODY_BIG), card_w - 16)
        by = hy + 2
        for ln in bl[:2]:
            d.text((x + 8, by), ln, font=F_SANS(F_BODY_BIG), fill=INK)
            by += 17
        d.text((x + 8, big_y + big_h - 13), source, font=F_SANS(F_SRC), fill=GREY)
        d.text((x + card_w - 8, big_y + big_h - 13), tag,
               font=F_SANS_B(F_SRC), fill=RED, anchor="ra")

    # ---- medium cards --------------------------------------------------
    med_y1, med_h = 380, 110
    med_w = (CW - 4 * 10) / 5.0
    for r in range(2):
        for c in range(5):
            lead = LEADS[3 + r * 5 + c]
            num, kicker, headline, body, source, tag, kind = lead
            x = MX + c * (med_w + 10)
            y = med_y1 + r * (med_h + 6)
            d.rectangle([x, y, x + med_w, y + med_h], fill=CARD_BG, outline=CARD_LINE)
            mini_icon(img, int(x + 1), y + 1, int(med_w - 2), 20, kind)
            ty = y + 24
            d.text((x + 6, ty), "%d  %s" % (num, kicker), font=F_SANS_B(9), fill=RED)
            hl = wrap(d, headline, F_SANS_B(F_HEAD_MED), med_w - 12)
            hy = ty + 12
            for ln in hl[:2]:
                d.text((x + 6, hy), ln, font=F_SANS_B(F_HEAD_MED), fill=NAVY)
                hy += 16
            bl = wrap(d, body, F_SANS(F_BODY_MED), med_w - 12)
            by = hy + 2
            for ln in bl[:2]:
                d.text((x + 6, by), ln, font=F_SANS(F_BODY_MED), fill=INK)
                by += 14
            d.text((x + 6, y + med_h - 11), source, font=F_SANS(9), fill=GREY)
            d.text((x + med_w - 6, y + med_h - 11), tag,
                   font=F_SANS_B(9), fill=RED, anchor="ra")

    # ---- map + briefs --------------------------------------------------
    map_y, map_h = 610, 270
    map_w = 284
    d.text((MX, map_y - 4), "WHERE IT HAPPENED \u2014 13 PINNED",
           font=F_SANS_B(F_MAP_HEAD), fill=NAVY)
    pins = [(1, 252, 96), (2, 240, 82), (3, 168, 74), (4, 214, 116),
            (5, 170, 102), (6, 82, 88), (7, 262, 108), (8, 146, 66),
            (9, 64, 112), (10, 220, 86), (11, 258, 122), (12, 96, 104),
            (13, 188, 112)]
    draw_map(img, MX, map_y + 14, map_w, map_h - 14, pins)

    bx0 = MX + map_w + 16
    d.text((bx0, map_y - 4), "ALSO ON TUESDAY 24 NOVEMBER",
           font=F_SANS_B(F_MAP_HEAD), fill=NAVY)
    by = map_y + 15
    for i, b in enumerate(BRIEFS):
        d.text((bx0, by), "%d. %s" % (14 + i, b), font=F_SANS(F_BRIEF), fill=INK)
        by += 17

    # ---- DATE CHECK ----------------------------------------------------
    dc_y, dc_h = 882, 132
    d.rectangle([MX, dc_y, W - MX, dc_y + dc_h], outline=RED, width=2)
    d.text((MX + 8, dc_y + 5),
           "DATE CHECK \u2014 NOT TUESDAY 24 NOVEMBER: first reported earlier, or not yet happened.",
           font=F_SANS_B(13), fill=RED)
    col_w = (CW - 16) / 3.0
    per_col = 8
    for ci in range(3):
        cx = MX + 10 + ci * col_w
        for ri in range(per_col):
            idx = ci * per_col + ri
            if idx >= len(DATECHECK):
                break
            yy = dc_y + 22 + ri * 13
            d.text((cx, yy), "\u00d7 " + DATECHECK[idx], font=F_SANS(F_DC), fill=RED_DK)

    # ---- footer --------------------------------------------------------
    d.text((MX, 1015),
           FOOTER_L1 + "  |  " + FOOTER_L2,
           font=F_SANS(F_FOOT), fill=GREY)

    return img

def out_path():
    v = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if v:
        os.makedirs(v, exist_ok=True)
        return os.path.join(v, "entry.png")
    v = os.environ.get("ENTRY_OUTPUT")
    if v:
        return v
    return "/output/entry.png"

def main():
    dest = out_path()
    try:
        if not _PIL_OK:
            raise RuntimeError("Pillow unavailable")
        img = render()
        rgb = img.convert("RGB")
        parent = os.path.dirname(dest)
        if parent:
            os.makedirs(parent, exist_ok=True)
        rgb.save(dest)
        here = os.path.dirname(os.path.abspath(__file__))
        rgb.save(os.path.join(here, "entry.png"))
        print("wrote", dest)
        return 0
    except Exception as e:
        print("render failed (%s); falling back to committed entry.png" % e,
              file=sys.stderr)
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            src = os.path.join(here, "entry.png")
            parent = os.path.dirname(dest)
            if parent:
                os.makedirs(parent, exist_ok=True)
            shutil.copyfile(src, dest)
            print("copied committed entry.png to", dest)
            return 0
        except Exception as e2:
            print("fallback failed: %s" % e2, file=sys.stderr)
            return 1

if __name__ == "__main__":
    sys.exit(main())
