"""The sharing card.

A link to this edition should preview as the thing the edition is about, so the
card is the collation rail turned on its side: five threads running the length
of the sermon, one per witness, each swelling with that witness's word count.
Clayton's stops three-quarters of the way along, Woodruff's just before the
end, Richards's stays thin throughout, and the *Times and Seasons* thread —
the one text nobody heard — is the heaviest of the five.

It is generated from ``data/`` like every other surface here, so it cannot go
stale against the edition it advertises. ``build.py`` renders this HTML at
1200×630 with headless Chrome, which is what lets the card use the site's own
faces instead of approximating them.
"""

from __future__ import annotations

import math

from kf.segments import Edition

from .html import esc

WIDTH, HEIGHT = 1200, 630
SIGLA = ("B", "W", "R", "C", "T")

#: The ribbon band: full width less the sigla gutter, sitting on the base line.
BAND_X, BAND_W = 104, WIDTH - 104 - 72
BAND_TOP, ROW_PITCH = 392.0, 37.0
MAX_RIBBON = 23.0


def _thickness(words: int, largest: int) -> float:
    """Word count to ribbon thickness.

    The rail on the site square-roots this, which is right for a 64px-wide
    gutter where the job is to keep Richards's fourteen words at S04 visible
    at all. At card size the square root over-compresses instead: everything
    lands near the maximum and five witnesses read as five identical bars,
    losing the difference the card exists to show. The gentler 0.75 exponent
    keeps small values legible while letting the spread reassert itself.
    """
    if words <= 0:
        return 0.0
    return 2.0 + (MAX_RIBBON - 2.0) * (words / largest) ** 0.75


def _ribbons(edition: Edition) -> str:
    sections = edition.sections
    largest = max(
        w.word_count
        for section in sections
        for w in section.witnesses.values()
        if w.present
    )
    step = BAND_W / len(sections)
    out: list[str] = []

    for index, siglum in enumerate(SIGLA):
        centre = BAND_TOP + index * ROW_PITCH
        colour = "var(--aged)" if siglum == "T" else "var(--gall)"
        out.append(
            f'<text class="sig" x="{BAND_X - 30}" y="{centre + 9:.1f}" '
            f'fill="{colour}">{siglum}</text>'
        )
        # A hairline the full length, so a witness's silence reads as a gap in
        # something rather than as nothing at all.
        out.append(
            f'<line class="ground" x1="{BAND_X}" y1="{centre:.1f}" '
            f'x2="{BAND_X + BAND_W}" y2="{centre:.1f}" />'
        )
        for position, section in enumerate(sections):
            witness = section.witnesses[siglum]
            if not witness.present:
                continue
            height = _thickness(witness.word_count, largest)
            out.append(
                f'<rect x="{BAND_X + position * step:.2f}" '
                f'y="{centre - height / 2:.2f}" width="{step:.2f}" '
                f'height="{height:.2f}" fill="{colour}" />'
            )
    return "".join(out)


def build(edition: Edition, stats: dict) -> str:
    counts = stats["types"]
    tally = (
        f"{stats['sections']} sections · {stats['eyewitnesses']} eyewitness reports "
        f"+ 1 derived · {stats['total_variants']} variants "
        f"({counts['theological']} theological, {counts['reception']} reception)"
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
  @font-face {{ font-family:"Fraunces"; font-weight:400 600;
    src:url("fonts/fraunces-var.woff2") format("woff2"); }}
  @font-face {{ font-family:"Newsreader"; font-weight:400 600;
    src:url("fonts/newsreader-var.woff2") format("woff2"); }}
  @font-face {{ font-family:"Spline Sans Mono"; font-weight:400 500;
    src:url("fonts/spline-sans-mono-var.woff2") format("woff2"); }}
  :root {{ --paper:#f4f1e8; --ink:#1f1c17; --ink-soft:#5b544a; --ink-faint:#8b8275;
           --hair:#ddd7c8; --gall:#2f3f63; --aged:#8a6a48; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:{WIDTH}px; height:{HEIGHT}px; background:var(--paper);
    color:var(--ink); overflow:hidden; }}
  .card {{ width:{WIDTH}px; height:{HEIGHT}px; padding:72px 72px 0; position:relative; }}
  h1 {{ font-family:"Fraunces",Georgia,serif; font-weight:500; font-size:70px;
    line-height:1.04; letter-spacing:-0.005em; }}
  .kicker {{ font-family:"Spline Sans Mono",monospace; font-size:17px;
    letter-spacing:0.2em; text-transform:uppercase; color:var(--ink-faint);
    margin-bottom:22px; }}
  .lede {{ font-family:"Newsreader",Georgia,serif; font-size:26px; line-height:1.4;
    color:var(--ink-soft); margin-top:20px; max-width:820px; }}
  .tally {{ position:absolute; left:74px; bottom:30px;
    font-family:"Spline Sans Mono",monospace; font-size:15px; letter-spacing:0.09em;
    color:var(--ink-faint); }}
  svg {{ position:absolute; left:0; top:0; }}
  .sig {{ font-family:"Fraunces",Georgia,serif; font-weight:600; font-size:25px;
    text-anchor:middle; }}
  /* The ground line runs the whole length under every witness, so a witness
     who stops reads as a thread ending rather than as empty paper. */
  .ground {{ stroke:var(--hair); stroke-width:2; }}
</style></head>
<body><div class="card">
  <p class="kicker">Nauvoo · 7 April 1844</p>
  <h1>The King Follett<br>Discourse</h1>
  <p class="lede">A critical edition from the four eyewitness reports and the
     composite printed four months later.</p>
  <svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">{_ribbons(edition)}</svg>
  <p class="tally">{esc(tally)}</p>
</div></body></html>
"""
