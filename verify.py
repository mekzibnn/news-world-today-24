#!/usr/bin/env python3
"""verify.py — checks for news-image-20261124 v4 ("The World in One Day").

Exit 0 only if ALL checks pass. Run from the repo dir:
    python3 verify.py [path/to/entry.png]
Default image: entry.png in this directory.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import main as M  # noqa: E402  (the entry under test; data + constants + wrap)

IMG_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")

PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("PASS  %s %s" % (name, detail))
    else:
        FAIL += 1
        print("FAIL  %s %s" % (name, detail))


def wrap(font, text, max_w):
    """Greedy word wrap, mirroring main._wrap."""
    words = text.split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for word in words[1:]:
        t = cur + " " + word
        if font.getlength(t) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


# ---------------------------------------------------------------- (a) size
try:
    from PIL import Image
    im = Image.open(IMG_PATH).convert("RGB")
    W, H = im.size
    check("(a) entry.png is 1024x1024", (W, H) == (1024, 1024),
          "got %dx%d" % (W, H))
except Exception as exc:  # noqa: BLE001
    im = None
    check("(a) entry.png is 1024x1024", False, "cannot open: %s" % exc)

# ---------------------------------------------------------------- (b) margins
if im is not None:
    # Title band: rows 30..73 (skip masthead bottom row at y=26 and the
    # subhead at y>=74). Title ink is NAVY (dark).
    left, right = 1024, -1
    for y in range(30, 74):
        for x in range(1024):
            r, g, b = im.getpixel((x, y))
            if r < 120 and g < 120 and b < 120:
                if x < left:
                    left = x
                if x > right:
                    right = x
    ml, mr = left, 1023 - right
    check("(b) title margins >=30px", ml >= 30 and mr >= 30,
          "left %dpx right %dpx" % (ml, mr))
    # Masthead band: rows 2..24, white text on navy.
    left, right = 1024, -1
    for y in range(2, 25):
        for x in range(1024):
            r, g, b = im.getpixel((x, y))
            if r > 200 and g > 200 and b > 200:
                if x < left:
                    left = x
                if x > right:
                    right = x
    ml, mr = left, 1023 - right
    check("(b) masthead margins >=30px", ml >= 30 and mr >= 30,
          "left %dpx right %dpx" % (ml, mr))

# ------------------------------------------------- (c) 13 headlines whole
f_big_head = M._font("sans-bold", 20)
f_big_body = M._font("sans", M.FONT_BODY)
f_med_head = M._font("sans-bold", 17)
f_med_body = M._font("sans", M.FONT_BODY)
BIG_CW = (M.CONTENT_W - 2 * 12) // 3 - 12   # inner width of a big card
MED_CW = (M.CONTENT_W - 4 * 8) // 5 - 12     # inner width of a medium card
headlines = [L["headline"] for L in M.LEADS] + [C["headline"] for C in M.MEDIUM]
check("(c) 13 headlines present", len(headlines) == 13, "got %d" % len(headlines))
bad = []
for L in M.LEADS:
    n = len(wrap(f_big_head, L["headline"], BIG_CW))
    if n > 2 or "..." in L["headline"] or "…" in L["headline"]:
        bad.append(("big", L["headline"], n))
for C in M.MEDIUM:
    n = len(wrap(f_med_head, C["headline"], MED_CW))
    if n > 2 or "..." in C["headline"] or "…" in C["headline"]:
        bad.append(("med", C["headline"], n))
check("(c) all 13 headlines whole (<=2 lines, no ...)", not bad,
      "bad=%s" % bad if bad else "all 2 lines max")
bad_body = []
for L in M.LEADS:
    n = len(wrap(f_big_body, L["body"], BIG_CW))
    if n > 2:
        bad_body.append(("big", L["body"], n))
for C in M.MEDIUM:
    n = len(wrap(f_med_body, C["body"], MED_CW))
    if n > 2:
        bad_body.append(("med", C["body"], n))
check("(c) all 13 card bodies whole (<=2 lines)", not bad_body,
      "bad=%s" % bad_body if bad_body else "all 2 lines max")

# ------------------------------------------------------ (d) 15 briefs whole
f_brief = M._font("sans", M.FONT_BRIEF)
brief_bad = []
for num, text in M.BRIEFS:
    w = f_brief.getlength("%d. %s" % (num, text))
    if w > 684 or "..." in text or "…" in text:
        brief_bad.append((num, text, round(w, 1)))
check("(d) 15 briefs present", len(M.BRIEFS) == 15, "got %d" % len(M.BRIEFS))
check("(d) all 15 briefs whole on one line", not brief_bad,
      "bad=%s" % brief_bad if brief_bad else "max width %.0fpx" % max(
          f_brief.getlength("%d. %s" % (n, t)) for n, t in M.BRIEFS))

# ------------------------------------------------------ (e) font minimums
check("(e) briefs font >=18px", M.FONT_BRIEF >= 18, "%dpx" % M.FONT_BRIEF)
check("(e) DATE CHECK font >=16px", M.FONT_DATECHECK >= 16,
      "%dpx" % M.FONT_DATECHECK)
check("(e) card body font >=17px", M.FONT_BODY >= 17, "%dpx" % M.FONT_BODY)
check("(e) timeline font >=16px", M.FONT_TIMELINE >= 16,
      "%dpx" % M.FONT_TIMELINE)
check("(e) caption/label font >=14px", M.FONT_CAPTION >= 14,
      "%dpx" % M.FONT_CAPTION)
src = open(os.path.join(HERE, "main.py"), encoding="utf-8").read()
m_big = re.search(r'def _draw_leads.*?f_head = _font\("sans-bold", (\d+)\)', src, re.S)
m_med = re.search(r'def _draw_medium.*?f_head = _font\("sans-bold", (\d+)\)', src, re.S)
check("(e) big headline font >=17px", bool(m_big) and int(m_big.group(1)) >= 17,
      "%spx" % (m_big.group(1) if m_big else "?"))
check("(e) medium headline font >=17px", bool(m_med) and int(m_med.group(1)) >= 17,
      "%spx" % (m_med.group(1) if m_med else "?"))

# ------------------------------------------------------ (f) timeline times
tl = " ".join(M.TIMELINE)
check("(f) Miss Universe at 01:00 UTC (Wed)",
      "01:00 UTC (Wed) Miss Universe final" in tl, "")
check("(f) UCL main kick-off 20:00 GMT present",
      "20:00 GMT UCL" in tl, "")
check("(f) NO '20:00 Miss Universe' (wrong UTC time)",
      "20:00 Miss Universe" not in tl and "20:00 UTC" not in tl,
      "")
check("(f) Shenzhou-24 launch 0018 GMT (Wed) present",
      "0018 GMT (Wed) Shenzhou-24 launch" in tl, "")

# ------------------------------------------------------ (g) no "..." anywhere
all_text = []
for L in M.LEADS:
    all_text += [L["kicker"], L["headline"], L["body"], L["sources"]]
for C in M.MEDIUM:
    all_text += [C["kicker"], C["headline"], C["body"], C["sources"]]
all_text += [t for _, t in M.BRIEFS] + list(M.DATECHECK) + list(M.TIMELINE)
all_text += [M.TITLE, M.SUBHEAD] + list(M.STATS) + [M.FOOTER_SOURCES, M.FOOTER_LEGEND]
bad_ell = [t for t in all_text if "..." in t or "…" in t]
check("(g) no '...' or '…' anywhere in content", not bad_ell,
      "bad=%s" % bad_ell if bad_ell else "")

# ------------------------------------------------------ (h) README badges
readme = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
badges = [
    "https://make.fun/badge/news-image-20261124.svg",
    "https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/rank.svg",
    "https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/reward.svg",
]
missing = [b for b in badges if b not in readme]
check("(h) 3 live make.fun badges in README", not missing,
      "missing=%s" % missing if missing else "all 3 present")
check("(h) badges link to bounty page",
      readme.count("https://make.fun/bounty/news-image-20261124") >= 3,
      "links=%d" % readme.count("https://make.fun/bounty/news-image-20261124"))
check("(h) no shields.io badges", "shields.io" not in readme, "")

# ------------------------------------------------------ (i) region counts
want = {"Asia-Pacific": 9, "Americas": 7, "Europe": 4, "Africa": 3,
        "Oceania": 2, "Middle East": 2, "World": 1}
regions = {name: n for name, n, _ in M.REGION_COLORS}
check("(i) region counts 9/7/4/3/2/2/1", regions == want,
      "%s" % regions)
check("(i) regions sum to 28 stories", sum(regions.values()) == 28,
      "sum=%d" % sum(regions.values()))

# ------------------------------------------- (j) lead pictorial band >=55px
if im is not None:
    # Big cards start at Y_BIG; the kicker is RED text drawn just below the
    # pictorial band. Scan UP from below the kicker (the headline/body under
    # it are navy/dark, not red) to find the kicker's ink, so the red chart
    # line inside the pictorial cannot be mistaken for the kicker.
    y_big = M.Y_BIG
    x0 = M.MARGIN + 4
    x1 = M.MARGIN + (M.CONTENT_W - 2 * 12) // 3 - 4

    def reds_in_row(y):
        n = 0
        for x in range(x0, x1):
            r, g, b = im.getpixel((x, y))
            if r > 150 and g < 90 and b < 90:
                n += 1
        return n

    kicker_bottom = None
    for y in range(y_big + 100, y_big, -1):
        if reds_in_row(y) >= 25:
            kicker_bottom = y
            break
    if kicker_bottom is None:
        check("(j) pictorial band >=55px", False, "kicker not found")
    else:
        kicker_top = kicker_bottom
        y = kicker_bottom - 1
        while y > y_big and reds_in_row(y) >= 8:
            kicker_top = y
            y -= 1
        band = kicker_top - y_big
        # pictorial content: non-cream pixels inside the band
        pic_rows = 0
        for yy in range(y_big + 2, kicker_top):
            for x in range(x0, x1):
                r, g, b = im.getpixel((x, yy))
                if abs(r - 250) > 25 or abs(g - 244) > 25 or abs(b - 230) > 25:
                    pic_rows += 1
                    break
        check("(j) pictorial band >=55px (card top to kicker)", band >= 55,
              "band=%dpx, pictorial rows=%d" % (band, pic_rows))
        check("(j) pictorial content visible in band", pic_rows >= 10,
              "%d rows with pictorial pixels" % pic_rows)

print("\n%d PASS, %d FAIL" % (PASS, FAIL))
sys.exit(0 if FAIL == 0 else 1)
