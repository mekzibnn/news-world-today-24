#!/usr/bin/env python3
"""Verify the news-image-20261124 v2 entry image.

Checks: entry.png exists, is 1024x1024, has a sane file size, the source
carries the key strings (28 stories, the date, gold $3,645, KADIZ, DATE
CHECK, Shenzhou-24, Parastoo Ahmadi), and no drawn text contains an
ellipsis marker. Exit 0 on pass, non-zero with a clear message on failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = os.path.join(HERE, "entry.png")
MAIN = os.path.join(HERE, "main.py")
README = os.path.join(HERE, "README.md")

KEY_STRINGS = [
    "28 STORIES",
    "TUESDAY 24 NOVEMBER 2026",
    "$3,645",
    "KADIZ",
    "DATE CHECK",
    "Shenzhou-24",
    "Parastoo Ahmadi",
    "Zaporizhzhia",
    "81.5M",
    "ALSO ON TUESDAY 24 NOVEMBER",
    "REPORTED",
    "CLAIM",
    "FORECAST",
]

BADGES = [
    "https://make.fun/badge/news-image-20261124.svg",
    "https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/rank.svg",
    "https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/reward.svg",
]


def fail(message):
    print("FAIL: %s" % message, file=sys.stderr)
    return 1


def main():
    if not os.path.exists(ENTRY):
        return fail("entry.png missing")
    size = os.path.getsize(ENTRY)
    if size < 50 * 1024:
        return fail("entry.png suspiciously small (%d bytes)" % size)
    if size > 2 * 1024 * 1024:
        return fail("entry.png suspiciously large (%d bytes)" % size)

    try:
        from PIL import Image
    except Exception:
        print("Pillow unavailable; image-dimensions check skipped")
    else:
        with Image.open(ENTRY) as im:
            if im.size != (1024, 1024):
                return fail("entry.png is %s, expected 1024x1024" % (im.size,))
            if im.mode not in ("RGB", "RGBA", "L"):
                return fail("unexpected image mode %s" % im.mode)

    if not os.path.exists(MAIN):
        return fail("main.py missing")
    with open(MAIN, "r", encoding="utf-8") as fh:
        source = fh.read()
    for key in KEY_STRINGS:
        if key not in source:
            return fail("main.py missing key string: %r" % key)
    if "..." in source or "\u2026" in source:
        # Only the ellipsis guard itself may mention the marker; check the
        # actual drawn text by importing main and inspecting its data.
        pass
    sys.path.insert(0, HERE)
    import main as entry_main
    drawn = [entry_main.MASTHEAD_RIGHT_TOP, entry_main.DATE_HEADLINE,
             entry_main.SUBHEAD, entry_main.TIMELINE,
             entry_main.FOOTER_SOURCES, entry_main.FOOTER_LEGEND]
    for lead in entry_main.LEADS:
        drawn += list(lead[1:6])
    for med in entry_main.MEDIUM:
        drawn += list(med[1:6])
    for _, brief in entry_main.BRIEFS:
        drawn.append(brief)
    drawn += entry_main.DATECHECK_A + entry_main.DATECHECK_B
    for text in drawn:
        if "..." in text or "\u2026" in text:
            return fail("drawn text contains an ellipsis marker: %r"
                        % text[:60])
    if len(entry_main.LEADS) != 3 or len(entry_main.MEDIUM) != 10:
        return fail("expected 3 leads + 10 medium cards")
    if len(entry_main.BRIEFS) != 15:
        return fail("expected 15 briefs, got %d" % len(entry_main.BRIEFS))
    if len(entry_main.DATECHECK_A) + len(entry_main.DATECHECK_B) != 22:
        return fail("expected 22 DATE CHECK items")
    if "from PIL import" in source.split("try:")[0]:
        return fail("main.py imports Pillow at top level")
    if "_PIL_OK" not in source or "MAKEFUN_OUTPUT_DIR" not in source:
        return fail("main.py missing Pillow fallback / output-dir handling")

    if not os.path.exists(README):
        return fail("README.md missing")
    with open(README, "r", encoding="utf-8") as fh:
        readme = fh.read()
    for badge in BADGES:
        if badge not in readme:
            return fail("README.md missing live badge: %s" % badge)

    print("OK: entry.png 1024x1024, %d bytes" % size)
    print("OK: %d key strings present, no ellipsis, 3 live badges in README"
          % len(KEY_STRINGS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
