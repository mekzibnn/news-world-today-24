# verify.py — checks for news-image-20261124 v3 (blind rewrite).
# Exit 0 only if EVERY check passes. Run:  python3 verify.py
#
# Checks:
#  (a) entry.png is 1024x1024
#  (b) title + masthead text keep >=30 px margin from left/right edges
#      (measured on dark / light pixels in the rendered image)
#  (c) all 13 headlines present and whole (wrap <=3 lines, no "...")
#  (d) all 15 briefs present and whole (one line each, <=50 chars)
#  (e) minimum font sizes per text class meet the thresholds
#  (f) timeline: Miss Universe at 01:00 UTC (or 20:00 ET), never 20:00 UTC;
#      UCL main kick-off 20:00 GMT present; Shenzhou-24 0018 GMT present
#  (g) no "..." / ellipsis anywhere in the content
#  (h) 3 live make.fun badges in README
#  (i) region counts correct (9/7/4/3/2/2/1, total 28 stories)
#  (j) card bodies fit (big <=2 lines, medium <=1 line); DATE CHECK items
#      fit one line per column; title fitted width <= TITLE_MAX_W.

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    from PIL import Image, ImageDraw
    _PIL_OK = True
except Exception:
    _PIL_OK = False

import main as M

PASS = 0
FAIL = 0
FAILURES = []


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("PASS  %s%s" % (name, (" — " + detail) if detail else ""))
    else:
        FAIL += 1
        FAILURES.append(name)
        print("FAIL  %s%s" % (name, (" — " + detail) if detail else ""))


def lum(px):
    r, g, b = px[0], px[1], px[2]
    return 0.299 * r + 0.587 * g + 0.114 * b


def main():
    global PASS, FAIL
    # --- (a) image size ---
    entry = os.path.join(HERE, "entry.png")
    check("entry.png exists", os.path.exists(entry))
    if not _PIL_OK:
        print("FAIL  Pillow unavailable; cannot run image checks")
        return 1
    img = Image.open(entry).convert("RGB")
    check("entry.png 1024x1024", img.size == (1024, 1024),
          "got %s" % (img.size,))
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    px = img.load()

    # --- (b) title margin: dark pixels in the title band ---
    # Band starts 2px below the masthead bar so the bar's bottom row
    # is not counted as title pixels.
    y0 = M.H_MASTHEAD + 2
    y1 = M.H_MASTHEAD + M.H_TITLE
    dark_xs = [x for yy in range(y0, y1) for x in range(M.W)
               if lum(px[x, yy]) < 120]
    if dark_xs:
        mn, mx = min(dark_xs), max(dark_xs)
        check("title margin >=30px left", mn >= 30, "min dark x=%d" % mn)
        check("title margin >=30px right", mx <= M.W - 30,
              "max dark x=%d" % mx)
        check("title width <= TITLE_MAX_W", (mx - mn + 1) <= M.TITLE_MAX_W,
              "extent=%d px" % (mx - mn + 1))
    else:
        check("title dark pixels found", False, "no dark pixels in title band")

    # --- (b) masthead margin: bright (white) pixels in the navy bar ---
    bright_xs = [x for yy in range(0, M.H_MASTHEAD) for x in range(M.W)
                 if lum(px[x, yy]) > 180]
    if bright_xs:
        mn, mx = min(bright_xs), max(bright_xs)
        check("masthead margin >=30px left", mn >= 30, "min bright x=%d" % mn)
        check("masthead margin >=30px right", mx <= M.W - 30,
              "max bright x=%d" % mx)
    else:
        check("masthead bright pixels found", False,
              "no bright pixels in masthead band")

    # --- (e) minimum font sizes (from main.py constants) ---
    check("brief font >= 18", M.FONT_BRIEF >= 18, "FONT_BRIEF=%d" % M.FONT_BRIEF)
    check("datecheck font >= 16", M.FONT_DATECHECK >= 16,
          "FONT_DATECHECK=%d" % M.FONT_DATECHECK)
    check("body font >= 17", M.FONT_BODY >= 17, "FONT_BODY=%d" % M.FONT_BODY)
    check("timeline font >= 16", M.FONT_TIMELINE >= 16,
          "FONT_TIMELINE=%d" % M.FONT_TIMELINE)
    check("caption font >= 14", M.FONT_CAPTION >= 14,
          "FONT_CAPTION=%d" % M.FONT_CAPTION)

    # --- (g) no ellipsis anywhere in content strings ---
    all_text = []
    for _, _, head, body, _, _, _ in M.BIG_CARDS:
        all_text += [head, body]
    for _, _, head, body, _, _ in M.MED_CARDS:
        all_text += [head, body]
    all_text += [t for _, t in M.BRIEFS]
    all_text += list(M.DATE_CHECK)
    all_text += list(M.TIMELINE) + [M.SUBHEAD, M.SOURCES_LINE, M.LEGEND_LINE]
    bad = [t for t in all_text if "..." in t or "\u2026" in t]
    check("no '...' / ellipsis in content", not bad,
          "bad=%r" % (bad[:2],) if bad else "")

    # --- (c) 13 headlines whole, wrap <= 3 lines ---
    card_w = (M.CARD_X1 - M.CARD_X0 - 16) // 3
    med_w = (M.CARD_X1 - M.CARD_X0 - 4 * 8) // 5
    heads = [(c[2], M.FONT_BIG_HEAD, card_w - 16, "big") for c in M.BIG_CARDS]
    heads += [(c[2], M.FONT_MED_HEAD, med_w - 14, "med") for c in M.MED_CARDS]
    check("13 headlines present", len(heads) == 13, "count=%d" % len(heads))
    for head, size, wmax, kind in heads:
        f = M.font(M.F_SANS_B, size)
        lines = M.wrap(d, head, f, wmax)
        joined = " ".join(lines)
        ok = len(lines) <= 3 and joined == head
        check("headline whole (%s): %r" % (kind, head[:28]),
              ok, "%d lines" % len(lines) if ok else "%d lines / joined!=orig"
              % len(lines))

    # --- (j) card bodies fit ---
    for _, _, _, body, _, _, _ in M.BIG_CARDS:
        f = M.font(M.F_SANS, M.FONT_BODY)
        lines = M.wrap(d, body, f, card_w - 16)
        check("big body <=2 lines", len(lines) <= 2,
              "%d lines" % len(lines))
    for _, _, _, body, _, _ in M.MED_CARDS:
        f = M.font(M.F_SANS, M.FONT_BODY)
        lines = M.wrap(d, body, f, med_w - 14)
        check("med body <=1 line", len(lines) <= 1,
              "%d lines" % len(lines))

    # --- (d) 15 briefs whole, one line, <= 50 chars ---
    check("15 briefs present", len(M.BRIEFS) == 15,
          "count=%d" % len(M.BRIEFS))
    fb = M.font(M.F_SANS, M.FONT_BRIEF)
    brief_col_w = M.W - (M.CARD_X0 + 316) - 16
    for n, txt in M.BRIEFS:
        line = "%d.  %s" % (n, txt)
        wline = d.textlength(line, font=fb)
        ok = len(txt) <= 50 and wline <= brief_col_w and "..." not in txt
        check("brief %d whole (<=50ch, 1 line)" % n, ok,
              "%d chars, %.0f px" % (len(txt), wline))

    # --- (i) region counts ---
    counts = [n for _, n, _ in M.REGIONS]
    check("region counts 9/7/4/3/2/2/1", counts == [9, 7, 4, 3, 2, 2, 1],
          "got %s" % (counts,))
    check("28 stories total", sum(counts) == 28, "sum=%d" % sum(counts))

    # --- (f) timeline correctness ---
    tl = " ".join(M.TIMELINE)
    check("Miss Universe at 01:00 UTC (or 20:00 ET)",
          ("01:00 UTC" in tl) or ("20:00 ET" in tl), tl[:60])
    check("no '20:00 Miss Universe' (UTC strip)", "20:00 Miss Universe" not in tl)
    check("UCL main kick-off 20:00 GMT present", "20:00 GMT" in tl)
    check("Shenzhou-24 0018 GMT present", "0018 GMT" in tl)

    # --- (j) DATE CHECK: 22 items, one line per column ---
    check("22 DATE CHECK items", len(M.DATE_CHECK) == 22,
          "count=%d" % len(M.DATE_CHECK))
    fdc = M.font(M.F_SANS, M.FONT_DATECHECK)
    col_w = (M.CARD_X1 - M.CARD_X0 - 16) // 3
    for item in M.DATE_CHECK:
        witem = d.textlength("\u2715 " + item, font=fdc)
        check("datecheck 1 line: %r" % item[:30], witem <= col_w - 4,
              "%.0f px vs col %d px" % (witem, col_w))

    # --- (h) README live badges ---
    readme = os.path.join(HERE, "README.md")
    if os.path.exists(readme):
        txt = open(readme, encoding="utf-8").read()
        slug = "news-image-20261124"
        badges = [
            "https://make.fun/badge/%s.svg" % slug,
            "https://make.fun/badge/%s/mekzibnn/news-world-today-24/rank.svg" % slug,
            "https://make.fun/badge/%s/mekzibnn/news-world-today-24/reward.svg" % slug,
        ]
        for b in badges:
            check("README badge %s" % b.split("/")[-1], b in txt)
        check("README badges link to bounty",
              "https://make.fun/bounty/%s" % slug in txt)
        check("README has no shields.io badges", "shields.io" not in txt)
    else:
        check("README exists", False)

    # --- title fitted width ---
    tsize = M.fit_size(d, "TUESDAY 24 NOVEMBER 2026", M.F_SERIF_B,
                       M.FONT_TITLE_MAX, M.TITLE_MAX_W)
    tw = d.textlength("TUESDAY 24 NOVEMBER 2026",
                      font=M.font(M.F_SERIF_B, tsize))
    check("title fitted width <= TITLE_MAX_W", tw <= M.TITLE_MAX_W,
          "size=%d, width=%.0f px" % (tsize, tw))

    print("\n%d PASS, %d FAIL" % (PASS, FAIL))
    if FAILURES:
        print("failures: %s" % ", ".join(FAILURES))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
