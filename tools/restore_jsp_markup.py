#!/usr/bin/env python3
"""Restore JSP cancellation and underline markup onto the transcripts.

The files in ``transcripts/`` are verbatim pastes of the JSP "Document
Transcript" view, but a paste flattens JSP's ``deleted`` and ``underscore``
spans into ordinary text: once flattened, a cancelled word is indistinguishable
from a word the scribe let stand. This script puts the two markers back:

    ``~~text~~``  JSP ``deleted`` span  (scribal cancellation)
    ``__text__``  JSP ``underscore`` span  (scribal underline)

It reads the server-rendered ``expandedText`` from ``refs/jsp-json/<witness>-<page>.json``
(one file per JSP page, saved when the transcripts were extracted; see
``refs/reextraction-report.md``). ``refs/`` is local reference material and is
gitignored, so this script only runs on a checkout that has it.

Markers are *mapped onto* the existing transcript rather than the transcript
being regenerated: the script matches the two texts character for character
ignoring whitespace, then splices the markers in. Every original character and
whitespace choice in ``transcripts/`` therefore survives untouched, and removing
the markers again must reproduce the input byte for byte -- which the script
checks before it writes anything, along with the per-witness span counts
recorded in ``refs/jsp-markup-audit.md``.

Usage::

    python3 tools/restore_jsp_markup.py [--check]

``--check`` verifies the transcripts already carry the expected markup and
writes nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_DIR = ROOT / "refs" / "jsp-json"

#: Witness slug -> (transcript path, JSP page count).
WITNESSES = {
    "bullock": ("transcripts/bullock.md", 9),
    "woodruff": ("transcripts/woodruff.md", 8),
    "richards": ("transcripts/richards.md", 5),
    "clayton": ("transcripts/clayton.md", 8),
}

#: Span counts from refs/jsp-markup-audit.md, independently re-counted there
#: against the live JSP pages. Restoring must reproduce these exactly.
EXPECTED = {
    "bullock": {"deleted": 16, "underscore": 5},
    "woodruff": {"deleted": 3, "underscore": 25},
    "richards": {"deleted": 7, "underscore": 0},
    "clayton": {"deleted": 10, "underscore": 6},
}

MARKERS = {"deleted": "~~", "underscore": "__"}

#: Subtrees carrying no transcript text. ``popup-content`` is the body of an
#: editorial note; the note's visible anchor digit sits outside it and is kept,
#: because that digit is the footnote anchor the parser reads.
SKIP_CLASSES = {"popup-content", "line-break"}


class ExpandedTextParser(HTMLParser):
    """Flatten one page of ``expandedText`` into text plus marker events.

    Produces ``events``: ``("char", c)`` for each character of transcript text
    and ``("open"|"close", marker)`` for each cancellation or underline
    boundary. Styling spans (superscript, italic, title) are flattened to their
    characters, matching what a paste of the page produces.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.events: list[tuple[str, str]] = []
        self._skip_depth = 0
        self._stack: list[str | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = set((dict(attrs).get("class") or "").split())
        if self._skip_depth or classes & SKIP_CLASSES:
            # A skipped subtree; void tags carry no subtree to leave.
            if tag not in ("br", "hr", "img"):
                self._skip_depth += 1
                self._stack.append(None)
            return
        marker = next((MARKERS[c] for c in classes if c in MARKERS), None)
        if marker:
            self.events.append(("open", marker))
        if tag in ("br", "hr", "img"):
            self.events.append(("char", " "))
            return
        self._stack.append(marker)

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return
        marker = self._stack.pop()
        if marker is None:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return
        if marker:
            self.events.append(("close", marker))
        if tag in ("p", "div"):
            # Keep block boundaries from welding two words together. Whitespace
            # is ignored by the mapping below, so this cannot corrupt anything.
            self.events.append(("char", " "))

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self.events.extend(("char", c) for c in data.replace("\xa0", " "))


def page_events(slug: str, pages: int) -> list[tuple[str, str]]:
    events: list[tuple[str, str]] = []
    for page in range(1, pages + 1):
        path = JSON_DIR / f"{slug}-{page}.json"
        if not path.exists():
            raise SystemExit(f"missing provenance file: {path}")
        parser = ExpandedTextParser()
        parser.feed(json.loads(path.read_text(encoding="utf-8"))["expandedText"])
        parser.close()
        events.extend(parser.events)
        events.append(("char", " "))
    return events


def transcript_body_bounds(text: str) -> tuple[int, int]:
    """Offsets of the body: after the 'Document Transcript' line, before 'Footnotes'."""
    lines = text.split("\n")
    if lines[1].strip() != "Document Transcript":
        raise SystemExit("expected 'Document Transcript' on line 2")
    start = len(lines[0]) + 1 + len(lines[1]) + 1
    offset = start
    for line in lines[2:]:
        if line.strip() == "Footnotes":
            return start, offset
        offset += len(line) + 1
    return start, len(text)


def splice(body: str, events: list[tuple[str, str]], slug: str) -> str:
    """Insert markers from ``events`` into ``body`` by non-whitespace alignment."""
    index = [i for i, c in enumerate(body) if not c.isspace()]
    source = "".join(c for kind, c in events if kind == "char" and not c.isspace())
    target = "".join(body[i] for i in index)
    if source != target:
        for n, (a, b) in enumerate(zip(source, target)):
            if a != b:
                raise SystemExit(
                    f"{slug}: JSP text and transcript diverge at non-space char {n}\n"
                    f"  jsp:        ...{source[max(0, n - 60):n + 20]!r}\n"
                    f"  transcript: ...{target[max(0, n - 60):n + 20]!r}"
                )
        raise SystemExit(
            f"{slug}: length mismatch, jsp {len(source)} vs transcript {len(target)}"
        )

    # An opening marker goes immediately before the next non-space character; a
    # closing marker immediately after the previous one. Both therefore hug the
    # word they mark and never land on the far side of a space.
    inserts: list[tuple[int, int, str]] = []
    seen = 0
    for order, (kind, value) in enumerate(events):
        if kind == "char":
            if not value.isspace():
                seen += 1
            continue
        if kind == "open":
            position = index[seen] if seen < len(index) else len(body)
        else:
            position = index[seen - 1] + 1 if seen else 0
        inserts.append((position, order, value))

    out: list[str] = []
    cursor = 0
    for position, _, value in sorted(inserts):
        out.append(body[cursor:position])
        out.append(value)
        cursor = position
    out.append(body[cursor:])
    return "".join(out)


def counts(text: str) -> dict[str, int]:
    return {kind: text.count(marker) // 2 for kind, marker in MARKERS.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify existing markup and write nothing",
    )
    args = ap.parse_args()

    failures = 0
    for slug, (relative, pages) in WITNESSES.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        start, end = transcript_body_bounds(text)
        body = text[start:end]

        if args.check:
            got = counts(body)
            ok = got == EXPECTED[slug]
            failures += not ok
            print(
                f"{'ok  ' if ok else 'FAIL'} {slug:9s} "
                f"cancellations {got['deleted']:2d}/{EXPECTED[slug]['deleted']:2d}  "
                f"underlines {got['underscore']:2d}/{EXPECTED[slug]['underscore']:2d}"
            )
            continue

        stripped = body
        for marker in MARKERS.values():
            stripped = stripped.replace(marker, "")
        marked = splice(stripped, page_events(slug, pages), slug)

        got = counts(marked)
        if got != EXPECTED[slug]:
            print(f"FAIL {slug}: got {got}, expected {EXPECTED[slug]}", file=sys.stderr)
            failures += 1
            continue
        round_trip = marked
        for marker in MARKERS.values():
            round_trip = round_trip.replace(marker, "")
        if round_trip != stripped:
            print(f"FAIL {slug}: marker removal does not round trip", file=sys.stderr)
            failures += 1
            continue

        path.write_text(text[:start] + marked + text[end:], encoding="utf-8")
        print(
            f"ok   {slug:9s} "
            f"cancellations {got['deleted']:2d}  underlines {got['underscore']:2d}"
        )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
