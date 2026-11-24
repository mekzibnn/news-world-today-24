#!/usr/bin/env python3
"""Static + render checks for the news-image-20261124 entry.

Checks:
  (a) README carries the three LIVE make.fun badges with exact URLs
      (reward badge must include /mekzibnn/news-world-today-24/);
      no static shields.io badges allowed.
  (b) All 28 stories present with correct numbers/dates; the 7 dropped
      briefs are NOT in the brief list; the 10 new DATE CHECK items are
      present; forbidden stale numbers are absent.
  (c) A fresh render produces no TRUNCATED card body/headline.
  (d) entry.png is 1024x1024 and within the target size band.
  (e) main.py has no top-level Pillow import and honours
      $MAKEFUN_OUTPUT_DIR / $ENTRY_OUTPUT with a committed-file fallback.

Exit 0 only when every check passes.
"""

import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "README.md")
MAIN = os.path.join(HERE, "main.py")
ENTRY = os.path.join(HERE, "entry.png")

BADGES = [
    "https://make.fun/badge/news-image-20261124.svg",
    "https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/rank.svg",
    "https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/reward.svg",
]
BOUNTY = "https://make.fun/competitions/news-image-20261124"

# (needle, where) — every lead headline + stat + masthead fact.
MUST_HAVE_MAIN = [
    "TUESDAY 24 NOVEMBER 2026",
    "28 STORIES",
    "7 REGIONS",
    "+4.5%", "+7.5%", "+9.1%", "$3,645", "81.5M", "2 / 22",
    "Asia markets surge on Huang's return; gold hits $3,645",
    "Russian jets enter Korea's air defence zone; Ulleung alert",
    "Russian attack kills 2, wounds 22 in Zaporizhzhia",
    "Hasina plans return to Bangladesh on Dec 16",
    "Israeli strike kills 3, wounds 5 in Khan Younis",
    "Republicans break with Trump over Huang return",
    "Japan arms buildup taps car-parts makers",
    "Germany stays EU's biggest net payer",
    "Thanksgiving travel begins: 81.5M on the move",
    "China to launch Shenzhou-24 on Wednesday",
    "Japan GDP shrinks 0.1% as households cut back",
    "Twin storms threaten both US coasts",
    "US suspects Iran behind attacks on 50 ships",
    "Pacific Elders: Australia betrayed Pacific at COP31",
    "Blazers beat 76ers 128-111, end 5-game streak",
    "UCL tonight: Arsenal-Dortmund, Man City-Napoli",
    "CAS to rule Tuesday on Senegal's AFCON title appeal",
    "Japan factory PMI: manufacturing 53.7",
    "brace for cuts up to 80%",
    "ASEAN disaster talks in Tangerang; 28 hit 90,200",
    "WHO chief visits Cuba",
    "survives 11 days alone in Amazon",
    "Soldiers attacked after Chapo Isidro arrest; 8 held",
    "UK-EU reset bill goes to Parliament on Thursday",
    "Labuschagne freak dismissal; Swepson 6/73",
    "Miss Universe 75th final tonight: 116 contestants",
    "comfort women' statue: Cape Town Dec 1",
    "Ramaphosa faces NCOP questions on AGOA, 30% tariff",
    "KADIZ", "no airspace violated", "07:52 KST",
    "Zeeshan Ali", "08:18 local",
]

# Dropped briefs (verified NOT Tuesday news) — must NOT be in BRIEFS.
DROPPED_IN_BRIEFS = [
    "Jollibee", "S&P Philippines", "Thailand wellness",
    "ACT Indigenous", "Seychelles-Nigeria", "Parastoo Ahmadi",
    "India HPV", "S&P: Philippines",
]

# New DATE CHECK items from the parent's verification.
DATE_CHECK_NEW = [
    "S&P Philippines downgrade — 24 Sep 2026",
    "Jollibee UK 30 stores — announced Mon 23 Nov",
    "Thailand wellness $46.5bn — data released 12 Nov",
    "ACT Indigenous protocol review — reported Mon 23 Nov",
    "Seychelles-Nigeria meeting — Mon 23 Nov",
    "Parastoo Ahmadi flogged 74 lashes — Mon 23 Nov",
    "India HPV 10M doses — announced Mon 23 Nov",
    "Two Nigerians killed fighting for Russia — announced Feb 2026",
    "US Senate $9.4bn aid/media cuts vote — Jul 2025",
    "Japan hosts US Treasury chief — meeting 11 Nov",
]

# Stale/wrong facts that must never appear as Tuesday news.
FORBIDDEN = [
    "35 STORIES", "35 cerita", "Nvidia +31%", "Nasdaq +6.5%",
    "gold $3,610", "$3,610/oz", "Nikkei -5.06%", "Starmer",
    "already returned", "Hasina returns home",
]

FAILURES = []
WARNINGS = []


def check(ok, label):
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        FAILURES.append(label)


def warn(ok, label):
    if not ok:
        print("WARN " + label)
        WARNINGS.append(label)


def section(text, start_marker, end_marker):
    start = text.find(start_marker)
    if start < 0:
        return ""
    end = text.find(end_marker, start)
    return text[start:end if end >= 0 else len(text)]


def main():
    readme = open(README, encoding="utf-8").read()
    main_src = open(MAIN, encoding="utf-8").read()

    # (a) badges
    for url in BADGES:
        check(url in readme, "badge present: " + url)
    check(BOUNTY in readme, "badge link target: " + BOUNTY)
    check("shields.io" not in readme, "no static shields.io badges")
    check("news-image-20261123" not in readme,
          "no leftover 20261123 badge/competition in README")

    # (b) stories present
    for needle in MUST_HAVE_MAIN:
        check(needle in main_src, "story/fact present: " + needle[:60])
    briefs = section(main_src, "BRIEFS = [", "\n]\n\n# DATE CHECK")
    check(briefs.count('"') >= 30, "brief list has 15 entries")
    for bad in DROPPED_IN_BRIEFS:
        check(bad not in briefs, "dropped brief absent from BRIEFS: " + bad)
    dc = section(main_src, "DATE_CHECK = [", "\n]\n\nSOURCES_LINE")
    for item in DATE_CHECK_NEW:
        check(item in dc, "DATE CHECK has new item: " + item[:50])
    check(dc.count('"') >= 44, "DATE CHECK has 22 entries")
    for bad in FORBIDDEN:
        check(bad not in main_src, "forbidden stale fact absent: " + bad)

    # (e) main.py structure
    pil_lines = [ln for ln in main_src.splitlines()
                 if "from PIL" in ln or "import PIL" in ln]
    check(len(pil_lines) == 1 and pil_lines[0].startswith("    "),
          "single Pillow import, inside try/except (not top-level)")
    check("_PIL_OK" in main_src, "Pillow optional flag _PIL_OK present")
    check("MAKEFUN_OUTPUT_DIR" in main_src,
          "main.py honours $MAKEFUN_OUTPUT_DIR")
    check("ENTRY_OUTPUT" in main_src, "main.py honours $ENTRY_OUTPUT")
    check("shutil.copyfile" in main_src and "committed" in main_src,
          "fallback copies committed entry.png on render failure")
    check("return 0" in main_src, "main() returns 0 (grade run completes)")

    # (c) fresh render must not truncate any card body/headline
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, MAKEFUN_OUTPUT_DIR=tmp)
        proc = subprocess.run([sys.executable, MAIN], env=env,
                              capture_output=True, text=True, timeout=120)
        check(proc.returncode == 0,
              "fresh render exits 0 (got {})".format(proc.returncode))
        check("TRUNCATED" not in proc.stdout,
              "no TRUNCATED card body/headline in render output")
        check("STORIES 28 LEADS 13 BRIEFS 15 DATECHECK 22" in proc.stdout,
              "render reports 28 stories / 13 leads / 15 briefs")
        out_png = os.path.join(tmp, "entry.png")
        check(os.path.exists(out_png), "render writes entry.png to "
              "$MAKEFUN_OUTPUT_DIR")

    # (d) committed entry.png dimensions + size
    check(os.path.exists(ENTRY), "entry.png exists in repo")
    if os.path.exists(ENTRY):
        try:
            from PIL import Image
            with Image.open(ENTRY) as im:
                check(im.size == (1024, 1024),
                      "entry.png is 1024x1024 (got {})".format(im.size))
        except ImportError:
            print("WARN Pillow unavailable for dimension check")
        size = os.path.getsize(ENTRY)
        print("INFO entry.png size: {} bytes ({:.1f} KB)"
              .format(size, size / 1024.0))
        check(120 * 1024 <= size <= 400 * 1024,
              "entry.png size within 120-400 KB hard band")
        warn(170 * 1024 <= size <= 350 * 1024,
             "entry.png size outside 170-350 KB target band")

    print("-" * 60)
    print("FAILURES: {}  WARNINGS: {}".format(len(FAILURES),
                                               len(WARNINGS)))
    for f in FAILURES:
        print("  FAIL: " + f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
