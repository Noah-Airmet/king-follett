"""Spans and section text as HTML.

Two renderings reach the page, and they answer different questions.

``reading_html`` is the text a reader reads. It is built *from the string
``jsp.render_reading`` produces*, not from a parallel re-implementation, so
what the page shows is character for character what ``python3 -m kf validate``
checks the apparatus readings against. Variant lemmas are then wrapped in place
by offset. If the two ever drift, the apparatus would point at text the reader
cannot see, so this indirection is the point rather than an inefficiency.

``diplomatic_html`` walks the spans instead, because its whole job is to show
the editorial matter the reading text drops: what the scribe struck out, where
the page turned, what JSP supplied in brackets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from kf import jsp

from .html import esc, tag


@dataclass
class Mark:
    """A variant lemma located in a witness's reading text."""

    start: int
    end: int
    variant_id: str
    type: str


def locate(text: str, readings: list[tuple[str, str, str]]) -> list[Mark]:
    """Find each reading in ``text``, left to right, without overlapping.

    ``readings`` is ``(variant_id, type, reading)`` in apparatus order. A
    reading may legitimately occur more than once in a section — "the Father"
    and "God" recur constantly — so each is matched at the first position at
    or after the previous match's end. Anything that cannot be placed that way
    is returned by the caller's miss list rather than guessed at.
    """
    marks: list[Mark] = []
    cursor = 0
    for variant_id, type_, reading in readings:
        if not reading or reading == "om.":
            continue
        at = text.find(reading, cursor)
        if at < 0:
            # Out of document order: fall back to the first free occurrence.
            at = text.find(reading)
            if at < 0 or any(at < m.end and at + len(reading) > m.start for m in marks):
                continue
        marks.append(Mark(at, at + len(reading), variant_id, type_))
        cursor = max(cursor, at + len(reading))
    marks.sort(key=lambda m: m.start)
    return marks


def reading_html(text: str, marks: list[Mark] | None = None) -> str:
    """Escaped reading text with each located lemma wrapped.

    The wrapper is a link so that a variant is reachable, quotable and
    shareable with scripting off; ``edition.js`` upgrades it to a slip.
    """
    if not marks:
        return esc(text)
    out: list[str] = []
    cursor = 0
    for mark in marks:
        if mark.start < cursor:
            continue
        out.append(esc(text[cursor : mark.start]))
        out.append(
            tag(
                "a",
                esc(text[mark.start : mark.end]),
                class_="lemma",
                href=f"/apparatus/#{mark.variant_id}",
                data_variant=mark.variant_id,
                data_type=mark.type,
            )
        )
        cursor = mark.end
    out.append(esc(text[cursor:]))
    return "".join(out)


def diplomatic_html(spans: list[jsp.Span], siglum: str) -> str:
    """The JSP presentation: cancellations, insertions, page turns, brackets.

    Footnote anchors become links to the witness's note list. Glosses keep
    their brackets and are marked, because the distinction between an
    editorial gloss and an expansion of the scribe's own abbreviation is the
    distinction the parser exists to draw.
    """
    out: list[str] = []
    for span in spans:
        kind = span.kind
        if kind == "footnote_anchor":
            out.append(
                tag(
                    "a",
                    esc(span.number),
                    class_="fn",
                    href=f"/witnesses/{siglum.lower()}/#n{span.number}",
                    id=f"r{span.number}",
                    data_note=f"{siglum}{span.number}",
                )
            )
        elif kind == "insertion":
            out.append(
                tag(
                    "ins",
                    diplomatic_html(span.children, siglum),
                    title="interlinear insertion",
                )
            )
        elif kind == "cancellation":
            out.append(
                tag(
                    "del",
                    diplomatic_html(span.children, siglum),
                    title="struck out by the scribe",
                )
            )
        elif kind == "underline":
            out.append(tag("u", diplomatic_html(span.children, siglum)))
        elif kind == "page_break":
            out.append(tag("span", esc(span.page), class_="pb", title="page turn"))
        elif kind == "gloss":
            out.append(tag("span", esc(span.raw), class_="gloss", title="editorial"))
        elif kind == "expansion":
            out.append(tag("span", esc(span.raw), class_="expansion"))
        elif kind == "blank":
            out.append(tag("span", esc(span.raw), class_="blank"))
        else:
            out.append(esc(span.raw))
    return "".join(out)


#: Text outside a tag, so a substitution over rendered HTML cannot wander into
#: an attribute value.
_OUTSIDE_TAGS = re.compile(r"(<[^>]*>)")
_VARIANT_REF = re.compile(r"\bV\d{3}\b")
_SECTION_REF = re.compile(r"\bS[0-3]\d\b")


def linkify(html: str, variants: set[str], sections: set[str]) -> str:
    """Make every V-id and S-id in prose a link to the thing it names.

    The commentary cites variants constantly — "the ladder image (V011)" — and
    a citation a reader cannot follow is half a citation. Only ids that
    actually exist are linked, so a typo in the prose stays visible as plain
    text rather than becoming a link to nothing.
    """
    parts = _OUTSIDE_TAGS.split(html)
    for index, part in enumerate(parts):
        if index % 2:  # a tag
            continue
        part = _VARIANT_REF.sub(
            lambda m: (
                f'<a class="ref" href="/apparatus/#{m.group(0)}">{m.group(0)}</a>'
                if m.group(0) in variants
                else m.group(0)
            ),
            part,
        )
        part = _SECTION_REF.sub(
            lambda m: (
                f'<a class="ref" href="/#{m.group(0)}">{m.group(0)}</a>'
                if m.group(0) in sections
                else m.group(0)
            ),
            part,
        )
        parts[index] = part
    return "".join(parts)
