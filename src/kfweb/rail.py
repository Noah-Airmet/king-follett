"""The collation rail.

Five ribbons running the height of the sermon, one per witness, each swelling
and narrowing with how many words that witness has in each of the thirty-five
sections. It is the table of contents, the reader's position, and the edition's
central fact in one object: Clayton's ribbon stops at S31, Woodruff's at S35,
Richards's is thin the whole way down, and the *Times and Seasons* ribbon — the
one text nobody heard — is the widest on the page.

Nothing here is labelled, because the shape is the claim. The rail is built as
ordinary SVG links with ``<title>`` children, so it navigates and explains
itself with scripting off.
"""

from __future__ import annotations

import math

from kf.segments import Edition

from .html import esc

ROW = 18.0
#: Ribbon centres. The eyewitnesses cluster; T sits beyond a rule, because it
#: is derived and must never read as a fifth column of the same kind.
COLUMNS = {"B": 7.0, "W": 16.0, "R": 25.0, "C": 34.0, "T": 47.0}
DIVIDER_X = 40.5
VARIANT_X = 58.0
MAX_RIBBON = 6.6
WIDTH = 64.0


def _ribbon_width(words: int, largest: int) -> float:
    """Words to ribbon width.

    Square-rooted, not linear, and capped short of the 9px column pitch so a
    gutter always survives between ribbons: four lit eyewitnesses have to read
    as four threads, not as one band. Linearly, Richards's fourteen words at S04 would
    be a third of a pixel against Bullock's 357 at S34 — honest arithmetic that
    renders as nothing at all. The square root keeps every present witness
    visible while preserving the ordering and the gross disproportion, which
    are the things the rail is actually asserting.
    """
    if words <= 0:
        return 0.0
    return 1.0 + (MAX_RIBBON - 1.0) * math.sqrt(words / largest)


def build(edition: Edition) -> str:
    sections = edition.sections
    height = ROW * len(sections)
    largest = max(
        w.word_count
        for section in sections
        for w in section.witnesses.values()
        if w.present
    )
    variant_counts: dict[str, int] = {}
    for variant in edition.apparatus_data["variants"]:
        variant_counts[variant["section"]] = variant_counts.get(variant["section"], 0) + 1
    busiest = max(variant_counts.values()) if variant_counts else 1

    parts = [
        f'<svg class="rail-plot" viewBox="0 0 {WIDTH:g} {height:g}" '
        f'width="{WIDTH:g}" height="{height:g}" role="presentation">',
        f'<line class="rail-divider" x1="{DIVIDER_X:g}" y1="0" '
        f'x2="{DIVIDER_X:g}" y2="{height:g}" />',
    ]

    for index, section in enumerate(sections):
        top = index * ROW
        parts.append(
            f'<g class="rail-row" data-section="{esc(section.id)}" '
            f'transform="translate(0 {top:g})">'
        )
        for siglum, centre in COLUMNS.items():
            witness = section.witnesses[siglum]
            if not witness.present:
                continue
            width = _ribbon_width(witness.word_count, largest)
            parts.append(
                f'<rect class="rib rib-{siglum}" x="{centre - width / 2:g}" y="0" '
                f'width="{width:g}" height="{ROW:g}" />'
            )
        count = variant_counts.get(section.id, 0)
        if count:
            radius = 1.1 + 2.0 * math.sqrt(count / busiest)
            parts.append(
                f'<circle class="rail-var" cx="{VARIANT_X:g}" '
                f'cy="{ROW / 2:g}" r="{radius:g}" />'
            )
        present = "".join(s for s in COLUMNS if section.witnesses[s].present)
        label = (
            f"{section.id}. {section.label} — "
            f"{present or 'no witness'}; "
            f"{count} variant{'' if count == 1 else 's'}"
        )
        parts.append(
            f'<a href="#{esc(section.id)}" class="rail-hit">'
            f"<title>{esc(label)}</title>"
            f'<rect x="0" y="0" width="{WIDTH:g}" height="{ROW:g}" fill="transparent" />'
            f"</a></g>"
        )

    parts.append("</svg>")
    return "".join(parts)
