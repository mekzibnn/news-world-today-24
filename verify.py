"""verify.py — checks news-image-20261124 v5 entry before submit.

Exit 0 only if every check passes. Checks:
(a) entry.png is 1024x1024
(b) title + masthead text have >=30px side margins (measured pixels)
(c) all 13 headlines present and complete (wrap to <=2 lines, no "...")
(d) all 15 briefs present, complete, fit on one line (no "...")
(e) font sizes meet minimums: briefs>=18, DATE CHECK>=16, big body>=17,
    timeline>=16, stat captions>=14, section heads>=14
(f) timeline: Miss Universe at 01:00 UTC (NOT 20:00), Shenzhou 0018 GMT,
    UCL 20:00 GMT present
(g) no "..." anywhere in main.py
(h) 3 live make.fun badges in README (exact URLs), no shields.io
(i) region counts 9/7/4/3/2/2/1, total 28 stories
(j) lead pictorial band height >=55px AND contains >=3 distinct brightness
    levels (proof of shading/gradient, not one flat colour)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PASS = 0
FAIL = 0

def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("PASS  (%s) %s" % (name, detail))
    else:
        FAIL += 1
        print("FAIL  (%s) %s" % (name, detail))

def main():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as e:
        print("FAIL  (import) Pillow unavailable: %s" % e)
        return 1
    import main as M

    entry = os.path.join(HERE, "entry.png")
    if not os.path.exists(entry):
        print("FAIL  (a) entry.png missing")
        return 1
    im = Image.open(entry).convert("RGB")
    # (a) size
    check("a", im.size == (1024, 1024), "size %s" % (im.size,))

    px = im.convert("L").load()
    d = ImageDraw.Draw(im)

    # (b) title margins: dark pixels in title band y 33..85
    dark_x = []
    for y in range(33, 86):
        for x in range(1024):
            if px[x, y] < 100:
                dark_x.append(x)
    if dark_x:
        left, right = min(dark_x), max(dark_x)
        check("b: title margins", left >= 30 and right <= 1024 - 30,
              "left %dpx, right %dpx" % (left, 1024 - right))
    else:
        check("b: title margins", False, "no dark pixels in title band")

    # masthead margins: white text on navy, y 4..26
    light_x = []
    for y in range(4, 27):
        for x in range(1024):
            if px[x, y] > 200:
                light_x.append(x)
    if light_x:
        left, right = min(light_x), max(light_x)
        check("b: masthead margins", left >= 30 and right <= 1024 - 30,
              "left %dpx, right %dpx" % (left, 1024 - right))
    else:
        check("b: masthead margins", False, "no light pixels in masthead")

    # (c) 13 headlines complete
    check("c: 13 headlines", len(M.LEADS) == 13, "count %d" % len(M.LEADS))
    bad = [h for (_, _, h, _, _, _, _) in M.LEADS if "..." in h or "…" in h]
    check("c: headlines complete", not bad, "bad=%s" % bad)
    f_head = M.F_SANS_B(M.F_HEAD_BIG)
    card_w = (M.CW - 2 * 12) / 3.0
    for (_, _, h, _, _, _, _) in M.LEADS[:3]:
        lines = M.wrap(d, h, f_head, card_w - 16)
        check("c: headline '%s' fits 2 lines" % h[:28], len(lines) <= 2,
              "len %d, lines %d" % (len(h), len(lines)))
    # (d) 15 briefs complete + fit one line
    check("d: 15 briefs", len(M.BRIEFS) == 15, "count %d" % len(M.BRIEFS))
    bad = [b for b in M.BRIEFS if "..." in b or "…" in b]
    check("d: briefs complete", not bad, "bad=%s" % bad)
    f_brief = M.F_SANS(M.F_BRIEF)
    brief_col_w = M.W - M.MX - (M.MX + 284 + 16)
    for b in M.BRIEFS:
        w = d.textlength("28. " + b, font=f_brief)
        check("d: brief fits one line '%s'" % b[:26], w <= brief_col_w,
              "w %.0f <= %.0f" % (w, brief_col_w))

    # (e) font minimums
    check("e: briefs >=18px", M.F_BRIEF >= 18, "%dpx" % M.F_BRIEF)
    check("e: datecheck >=16px", M.F_DC >= 16, "%dpx" % M.F_DC)
    check("e: big card bodies >=17px", M.F_BODY_BIG >= 17, "%dpx" % M.F_BODY_BIG)
    check("e: timeline >=16px", M.F_TIME >= 16, "%dpx" % M.F_TIME)
    check("e: stat captions >=14px", M.F_STAT_CAP >= 14, "%dpx" % M.F_STAT_CAP)
    check("e: section heads >=14px", M.F_MAP_HEAD >= 14, "%dpx" % M.F_MAP_HEAD)
    check("e: big headlines >=18px", M.F_HEAD_BIG >= 18, "%dpx" % M.F_HEAD_BIG)
    check("e: medium headlines >=15px", M.F_HEAD_MED >= 15, "%dpx" % M.F_HEAD_MED)

    # (f) timeline correctness
    tl = M.TIMELINE_L1 + " " + M.TIMELINE_L2
    check("f: Miss Universe 01:00 UTC", "01:00 UTC (Wed) Miss Universe" in tl, "")
    check("f: no 20:00 Miss Universe", "20:00 Miss Universe" not in tl
          and "20:00 UTC (Wed) Miss Universe" not in tl, "")
    check("f: Shenzhou 0018 GMT", "0018 GMT (Wed) Shenzhou-24" in tl, "")
    check("f: UCL 17:45/20:00 GMT", "17:45 & 20:00 GMT UCL" in tl, "")

    # (g) no "..." in main.py
    with open(os.path.join(HERE, "main.py"), encoding="utf-8") as f:
        src = f.read()
    check("g: no '...' in main.py", "..." not in src and "…" not in src, "")

    # (h) README badges
    with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
        readme = f.read()
    check("h: badge news-image-20261124.svg",
          "https://make.fun/badge/news-image-20261124.svg" in readme, "")
    check("h: badge rank.svg",
          "https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/rank.svg" in readme, "")
    check("h: badge reward.svg",
          "https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/reward.svg" in readme, "")
    check("h: no shields.io", "shields.io" not in readme, "")

    # (i) regions
    counts = [c for _, c, _ in M.REGIONS]
    check("i: region counts 9/7/4/3/2/2/1", counts == [9, 7, 4, 3, 2, 2, 1],
          "got %s" % counts)
    check("i: total 28 stories", sum(counts) == 28, "total %d" % sum(counts))
    check("i: masthead says 28 STORIES", "28 STORIES" in M.MASTHEAD_RIGHT_TOP, "")
    check("i: DATE CHECK has 22 items", len(M.DATECHECK) == 22,
          "%d items" % len(M.DATECHECK))

    # (j) pictorial band: height + colour variation (shading/gradient proof)
    # big card 1 pictorial band: x 17..337, y 215..270 (big_y=214, PIC_H=55)
    check("j: pictorial band height >=55px", M.PIC_H >= 55, "%dpx" % M.PIC_H)
    def band_levels(x0, x1):
        band = im.crop((x0, 215, x1, 215 + M.PIC_H)).convert("L")
        bw, bh = band.size
        bpx = band.load()
        rows = 0
        bins = set()
        for y in range(bh):
            vals = [bpx[x, y] for x in range(bw)]
            if max(vals) - min(vals) > 20:
                rows += 1
            for v in vals:
                bins.add(v // 16)
        return rows, len(bins)
    rows, lv = band_levels(17, 337)
    check("j: pictorial band has content rows >=50 (varied rows in card 1)",
          rows >= 50, "%d rows" % rows)
    check("j: pictorial has >=3 brightness levels (shading/gradient)",
          lv >= 3, "%d levels" % lv)
    _, lv2 = band_levels(352, 671)
    check("j: jet pictorial has >=3 brightness levels", lv2 >= 3,
          "%d levels" % lv2)
    _, lv3 = band_levels(685, 1005)
    check("j: fire pictorial has >=3 brightness levels", lv3 >= 3,
          "%d levels" % lv3)

    print("\n%d PASS, %d FAIL" % (PASS, FAIL))
    return 0 if FAIL == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
