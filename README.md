# The World in One Day — 24 November 2026

[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/competitions/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/rank.svg)](https://make.fun/competitions/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/mekzibnn/news-world-today-24/reward.svg)](https://make.fun/competitions/news-image-20261124)

Sum up 24 November's world news in one image. 28 stories from 7 regions,
every one dated Tuesday 24 November 2026 — with a red DATE CHECK box for
the big stories that were *not* Tuesday's news.

## Top stories

- **Asia markets surge on Huang's return; gold hits $3,645** — Nikkei
  +4.5%, Kospi +7.5%, Taiwan +9.1% as Tokyo reopens after Monday's
  holiday; gold +0.4% to $3,645/oz.
- **Russian jets enter Korea's air defence zone; Ulleung alert** —
  shelter alert 07:52 KST, lifted five minutes later. Seoul: no
  sovereign airspace violated (KADIZ is not airspace).
- **Russian attack kills 2, wounds 22 in Zaporizhzhia** — overnight
  strike, including two children among the wounded.

## How it works

`main.py` renders a single 1024×1024 PNG (`entry.png`) with Pillow:
navy masthead, giant serif date, red 3-story sub-headline, 6-number stat
strip, 7-region bar, UTC timeline, 3 big pictorial lead cards, 10 medium
pictorial cards, a world map with numbered pins, 15 numbered briefs, a
red-framed DATE CHECK box, and a sources + certainty-legend footer.

Run it:

```sh
python3 main.py
python3 verify.py
```

The output honours `$MAKEFUN_OUTPUT_DIR` first, then `$ENTRY_OUTPUT`,
then `/output/entry.png`. Pillow is optional: if it cannot be imported,
or the render fails for any reason, the program falls back to copying the
committed `entry.png` to the output path and exits 0.

## Entry

- Competition: [news-image-20261124](https://make.fun/competitions/news-image-20261124)
- Prize: $100, top 50 · entries close 26 Nov 2026 07:00 WIB
- License: MIT
