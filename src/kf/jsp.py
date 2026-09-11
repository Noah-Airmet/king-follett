"""Parser for Joseph Smith Papers document-transcript conventions.

The five King Follett transcripts in ``transcripts/`` are verbatim pastes of the
JSP "Document Transcript" view. This module turns one of those files into a
structured document and provides three renderings of the body.

Four transcripts are eyewitness reports (B, W, R, C). The fifth, T, is the
*Times and Seasons* composite that Bullock and Clayton assembled from the notes:
a derived witness, not a fifth independent report. This module records that as
``Document.kind`` and ``WITNESS_KINDS``; nothing here treats T as evidence
independent of B and C.

Conventions recognised inside the body
--------------------------------------

``[p. 14]`` / ``[p. [133]]``
    Manuscript page break. The text *preceding* the marker stands on that page.
    Parsed as a ``page_break`` span whose ``page`` is the label with any
    JSP-supplied brackets kept (``"14"``, ``"[133]"``).

``con[ference]``, ``subj[ec]t``, ``Follet[t]``, ``[k]now``
    Editorial expansion of a scribal abbreviation, recognisable because the
    bracket is glued to the word with no intervening space (at either end).
    Parsed as an ``expansion`` span with ``mode="insert"``; the reading text
    applies it silently.

``noes [knows]``, ``evelastig [everlasting]``, ``Intiignc [Intelligence]``
    Editorial *respelling* of the preceding word: a space-separated bracket
    holding a single token that is a near-match of the word before it. Parsed as
    an ``expansion`` span with ``mode="replace"``; the reading text substitutes
    the bracketed form for the scribal form.

``Follit [King Follett]``, ``Eloe [Elōheem or Elohim]``, ``H. G. [Holy Ghost]``
    Editorial gloss or identification. Parsed as a ``gloss`` span and **dropped**
    from the reading text; the scribe's own word before it is kept. The old
    ``data/align.py`` stripped the brackets but kept their contents, producing
    reading text like "the great Eloe Elōheem or Elohim"; this distinction exists
    to prevent that. ``[illegible]`` is also a gloss.

``[blank]``, ``[25 lines blank]``, ``[1/3 page blank]``
    Editorial notation of blank manuscript space. Parsed as a ``blank`` span.

``__text__``
    Scribal underline (JSP ``underscore`` span), e.g. Woodruff underlining
    "__yonder__ __heavens__ ... __man__ __like__ __yourselves__ ... __GOD__".
    Parsed as an ``underline`` span. Shown as-is in the diplomatic rendering and
    dropped to plain text in the reading rendering: the underlining is a fact
    about the manuscript, not about the words. Content is parsed recursively, so
    an underline may contain an expansion (``Et[erna]__l__`` is an expansion
    followed by an underline; ``Pres__t__`` is text plus an underline).

``~~text~~``
    Scribal cancellation. JSP renders cancelled text struck through and the paste
    keeps it as a markdown strikethrough. Parsed as a ``cancellation`` span and
    dropped from the reading text, since cancelled words are not part of what the
    scribe let stand: ``1st ~~of~~ object`` reads "1st object" and ``as the father
    ~~hath~~ had power`` reads "as the father had power". A cancellation may fall
    inside a word (``God~~s~~``) and may contain other markup
    (``~~[illegible]~~``), so its content is parsed recursively. This kind was not
    in the convention list the project brief gave; it is here because all four
    transcripts use it and folding it into plain text would carry cancelled
    readings into the reading text.

``<text>`` with U+200B just inside the angle brackets
    Interlinear insertion by the scribe. The zero-width spaces are stripped from
    the span's content but the raw source form is retained. Insertions may
    themselves contain expansions, so their content is parsed recursively.
    Applied inline in every rendering.

Footnote anchors
    Bare digits glued to the end of a word or punctuation (``hearts2``,
    ``Spirit—46``, ``instr[uctio]n.1``). Some digits in these texts are genuine
    scribal content ("ninety nine of 100", "the last 14 y[ea]rs", "99/100",
    "meet Paul 1/2 way"), so a digit run is only taken as an anchor when it is
    glued to the preceding character *and* equals the next expected footnote
    number. Anchors therefore run 1..N strictly in order of appearance, and the
    count is checked against the number of footnotes for all four eyewitness
    transcripts (see ``tests/test_jsp.py``). JSP supplies no footnotes for T, so
    T must yield no anchors at all.

Typography (em and en dashes, curly quotes, U+014D, U+00AD, U+25CA) is preserved
everywhere. Nothing is ASCII-folded and no transcript character is corrected.
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ZWSP = "\u200b"

#: Kinds a body span may take.
SPAN_KINDS = (
    "text",
    "expansion",
    "gloss",
    "insertion",
    "cancellation",
    "underline",
    "page_break",
    "footnote_anchor",
    "blank",
)

#: Span kinds delimited by a paired marker whose content is parsed recursively.
_PAIRED = {"~~": "cancellation", "__": "underline"}

#: Span kinds that are markup rather than scribal reading text. A section
#: boundary may never fall inside one of these.
MARKUP_KINDS = tuple(k for k in SPAN_KINDS if k != "text")

#: JSP titles read "as Reported by <reporter>" for the eyewitness accounts and
#: "as Published in Times and Seasons" for the composite.
_SIGLA_BY_SOURCE = {
    "Thomas Bullock": "B",
    "Wilford Woodruff": "W",
    "Willard Richards": "R",
    "William Clayton": "C",
    "Times and Seasons": "T",
}

_TITLE_RE = re.compile(r"as (?:Reported by|Published in)\s+(.+?)\s*$")
_FOOTNOTE_RE = re.compile(r"^\[(\d+)\](.*)$")
_PAGE_RE = re.compile(r"^p\.\s*(.+)$")
_BLANK_RE = re.compile(r"^(?:blank|\S.*\bblank)$")
_WORD_TAIL_RE = re.compile(r"[^\s\[\]<>~]+$")
_PUNCT_STRIP_RE = re.compile(r"[^\w\s]", re.UNICODE)

#: Minimum difflib similarity for a spaced single-token bracket to count as a
#: respelling of the preceding word rather than an editorial gloss.
RESPELL_THRESHOLD = 0.5


@dataclass
class Span:
    """One typed piece of the body text.

    ``raw`` is always the exact source slice, so ``"".join(s.raw for s in spans)``
    reconstructs the body character for character.
    """

    kind: str
    raw: str
    start: int
    end: int
    #: Bracket, angle-bracket or strikethrough content, ZWSP stripped.
    content: str = ""
    #: ``"insert"`` (con[ference]) or ``"replace"`` (noes [knows]) for expansions.
    mode: str = ""
    #: Page label for page_break spans.
    page: str = ""
    #: Footnote number for footnote_anchor spans.
    number: int = 0
    #: Parsed sub-spans for insertion and cancellation spans.
    children: list["Span"] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.kind not in SPAN_KINDS:
            raise ValueError(f"unknown span kind: {self.kind!r}")


@dataclass
class Document:
    siglum: str
    title: str
    #: Reporter's name; for T, the name of the publication.
    reporter: str
    #: ``"eyewitness"`` or ``"derived"``.
    kind: str
    path: str
    #: Raw body text; every span offset is an index into this string.
    body: str
    spans: list[Span]
    footnotes: dict[int, str]
    #: Bibliography blocks JSP prints under a footnote, by footnote number.
    works_cited: dict[int, list[str]]

    @property
    def pages(self) -> list[str]:
        return [s.page for s in self.spans if s.kind == "page_break"]

    @property
    def anchors(self) -> list[Span]:
        return [s for s in self.spans if s.kind == "footnote_anchor"]


# --------------------------------------------------------------------------- #
# file splitting
# --------------------------------------------------------------------------- #


def split_source(text: str) -> tuple[str, str, str]:
    """Split a transcript file into (title, body, footnote block)."""
    lines = text.split("\n")
    if len(lines) < 3 or lines[1].strip() != "Document Transcript":
        raise ValueError("expected 'Document Transcript' on line 2")
    title = lines[0].strip()
    for i, line in enumerate(lines[2:], start=2):
        if line.strip() == "Footnotes":
            return title, "\n".join(lines[2:i]).strip("\n"), "\n".join(lines[i + 1 :])
    return title, "\n".join(lines[2:]).strip("\n"), ""


def parse_footnotes(block: str) -> tuple[dict[int, str], dict[int, list[str]]]:
    """Parse the ``[N]text`` lines following the ``Footnotes`` heading.

    A footnote runs until the next ``[N]`` line, so JSP's "Comprehensive Works
    Cited" blocks are gathered onto the footnote they follow and returned
    separately rather than being mixed into the note text.
    """
    notes: dict[int, list[str]] = {}
    cited: dict[int, list[str]] = {}
    current: int | None = None
    in_cited = False
    for line in block.split("\n"):
        match = _FOOTNOTE_RE.match(line)
        if match:
            current = int(match.group(1))
            if current in notes:
                raise ValueError(f"duplicate footnote {current}")
            notes[current] = [match.group(2).strip()]
            cited[current] = []
            in_cited = False
            continue
        if current is None:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "Comprehensive Works Cited":
            in_cited = True
            continue
        (cited[current] if in_cited else notes[current]).append(stripped)
    return (
        {n: " ".join(parts).strip() for n, parts in notes.items()},
        dict(cited),
    )


# --------------------------------------------------------------------------- #
# body tokenising
# --------------------------------------------------------------------------- #


def _matching_bracket(text: str, open_at: int) -> int:
    """Index just past the ``]`` closing the ``[`` at ``open_at`` (nesting aware)."""
    depth = 0
    for i in range(open_at, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError(f"unbalanced '[' at offset {open_at}")


def _is_respelling(previous_word: str, content: str) -> bool:
    """True when a spaced bracket respells the word before it."""
    if not previous_word or " " in content:
        return False
    a = "".join(c for c in previous_word.lower() if c.isalpha())
    b = "".join(c for c in content.lower() if c.isalpha())
    if len(a) < 2 or len(b) < 2:
        return False
    return difflib.SequenceMatcher(None, a, b).ratio() >= RESPELL_THRESHOLD


def _classify_bracket(raw: str, preceding: str, following: str) -> tuple[str, dict]:
    """Type a bracketed run given the source text around it."""
    content = raw[1:-1].strip()
    page = _PAGE_RE.match(content)
    if page:
        return "page_break", {"content": content, "page": page.group(1).strip()}
    if _BLANK_RE.match(content):
        return "blank", {"content": content}
    glued = bool(preceding) and preceding[-1] not in " \n\t"
    if glued and _WORD_TAIL_RE.search(preceding):
        return "expansion", {"content": content, "mode": "insert"}
    # Word-initial expansion: "[a]men", "[k]now".
    if " " not in content and following[:1].isalpha():
        return "expansion", {"content": content, "mode": "insert"}
    tail = _WORD_TAIL_RE.search(preceding.rstrip())
    if tail and _is_respelling(tail.group(0), content):
        return "expansion", {"content": content, "mode": "replace"}
    return "gloss", {"content": content}


def parse_body(body: str, *, offset: int = 0, count_anchors: bool = True) -> list[Span]:
    """Tokenise body text into typed spans.

    ``offset`` is added to every span position, so recursive calls on insertion
    and cancellation contents still report offsets into the whole body.
    ``count_anchors`` is False for those recursive calls: footnote numbering is
    tracked once, at the top level.
    """
    spans: list[Span] = []
    pending: list[str] = []
    pending_start = 0
    expected = 1
    i = 0

    def flush(end: int) -> None:
        if pending:
            spans.append(
                Span("text", "".join(pending), offset + pending_start, offset + end)
            )
            pending.clear()

    while i < len(body):
        char = body[i]
        if char == "[":
            close = _matching_bracket(body, i)
            raw = body[i:close]
            kind, extra = _classify_bracket(raw, body[:i], body[close:])
            flush(i)
            spans.append(Span(kind, raw, offset + i, offset + close, **extra))
            i = close
            pending_start = i
            continue
        if char == "<":
            close = body.find(">", i)
            if close == -1:
                raise ValueError(f"unbalanced '<' at offset {i}")
            close += 1
            raw = body[i:close]
            inner = raw[1:-1].replace(ZWSP, "")
            flush(i)
            inner_offset = offset + i + 1 + (1 if raw[1:2] == ZWSP else 0)
            spans.append(
                Span(
                    "insertion",
                    raw,
                    offset + i,
                    offset + close,
                    content=inner,
                    children=parse_body(
                        inner, offset=inner_offset, count_anchors=False
                    ),
                )
            )
            i = close
            pending_start = i
            continue
        marker = next((m for m in _PAIRED if body.startswith(m, i)), None)
        if marker:
            close = body.find(marker, i + len(marker))
            if close == -1:
                raise ValueError(f"unbalanced {marker!r} at offset {i}")
            close += len(marker)
            raw = body[i:close]
            inner = raw[len(marker) : -len(marker)]
            flush(i)
            spans.append(
                Span(
                    _PAIRED[marker],
                    raw,
                    offset + i,
                    offset + close,
                    content=inner,
                    children=parse_body(
                        inner,
                        offset=offset + i + len(marker),
                        count_anchors=False,
                    ),
                )
            )
            i = close
            pending_start = i
            continue
        if count_anchors and char.isdigit():
            run = i
            while run < len(body) and body[run].isdigit():
                run += 1
            glued = i > 0 and not body[i - 1].isspace()
            if glued and int(body[i:run]) == expected:
                flush(i)
                spans.append(
                    Span(
                        "footnote_anchor",
                        body[i:run],
                        offset + i,
                        offset + run,
                        number=expected,
                    )
                )
                expected += 1
                i = run
                pending_start = i
                continue
            if not pending:
                pending_start = i
            pending.append(body[i:run])
            i = run
            continue
        if not pending:
            pending_start = i
        pending.append(char)
        i += 1

    flush(len(body))
    return spans


def parse_file(path: str | Path) -> Document:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    title, body, footnote_block = split_source(text)
    reporter_match = _TITLE_RE.search(title)
    if not reporter_match:
        raise ValueError(f"cannot read reporter from title: {title!r}")
    reporter = reporter_match.group(1)
    if reporter not in _SIGLA_BY_SOURCE:
        raise ValueError(f"unknown transcript source: {reporter!r}")
    siglum = _SIGLA_BY_SOURCE[reporter]
    notes, cited = parse_footnotes(footnote_block)
    return Document(
        siglum=siglum,
        title=title,
        reporter=reporter,
        kind=WITNESS_KINDS[siglum],
        path=str(path),
        body=body,
        spans=parse_body(body),
        footnotes=notes,
        works_cited=cited,
    )


# --------------------------------------------------------------------------- #
# renderings
# --------------------------------------------------------------------------- #


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def render_diplomatic(spans: list[Span]) -> str:
    """Reproduce the JSP presentation.

    Expansions, glosses, blank notations and page markers keep their source
    form; cancellations stay wrapped in ``~~`` and underlines in ``__``;
    insertions are shown as ``<text>`` with the zero-width spaces removed;
    footnote anchors are shown as ``[n]`` so they cannot be confused with
    scribal digits. Line breaks and internal whitespace are preserved.
    """
    out: list[str] = []
    for span in spans:
        if span.kind == "footnote_anchor":
            out.append(f"[{span.number}]")
        elif span.kind == "insertion":
            out.append(f"<{render_diplomatic(span.children)}>")
        elif span.kind in ("cancellation", "underline"):
            marker = "~~" if span.kind == "cancellation" else "__"
            out.append(f"{marker}{render_diplomatic(span.children)}{marker}")
        else:
            out.append(span.raw)
    return "".join(out)


def render_reading(spans: list[Span]) -> str:
    """Clean reading text.

    Expansions are applied silently, glosses are dropped rather than merged,
    insertions are applied inline, underline marks are dropped but the words
    they mark are kept, cancellations, page breaks, blank notations and footnote
    anchors are removed, and whitespace is normalised to single spaces.
    Capitalisation, spelling and punctuation are otherwise untouched.
    """
    out: list[str] = []
    for span in spans:
        if span.kind == "text":
            out.append(span.raw)
        elif span.kind == "expansion":
            if span.mode == "replace":
                # Drop the scribal form that the bracket respells.
                out = [_WORD_TAIL_RE.sub("", "".join(out).rstrip()), " ", span.content]
            else:
                out.append(span.content)
        elif span.kind in ("insertion", "underline"):
            out.append(render_reading(span.children))
        # gloss, cancellation, page_break, footnote_anchor, blank: dropped
    return _collapse("".join(out))


def render_normalized(spans: list[Span]) -> str:
    """Reading text lowercased, punctuation stripped, whitespace collapsed.

    For machine comparison only. NFC-normalised so composed and decomposed forms
    of ``ō`` compare equal; the soft hyphen U+00AD is removed.
    """
    text = unicodedata.normalize("NFC", render_reading(spans))
    text = text.replace("\u00ad", "")
    text = _PUNCT_STRIP_RE.sub(" ", text.lower())
    return _collapse(text)


def word_count(spans: list[Span]) -> int:
    reading = render_reading(spans)
    return len(reading.split()) if reading else 0


# --------------------------------------------------------------------------- #
# span helpers used by the section layer
# --------------------------------------------------------------------------- #


def spans_in(spans: list[Span], start: int, end: int) -> list[Span]:
    """The spans covering ``[start, end)``, with plain text clipped to fit.

    A single run of plain text often spans several sections, so text spans that
    straddle the range are cut down to the overlap. Markup spans are returned
    whole; a markup span can never straddle a section boundary, which is one of
    the invariants ``validate`` enforces.
    """
    out: list[Span] = []
    for span in spans:
        if span.end <= start or span.start >= end:
            continue
        if span.start >= start and span.end <= end:
            out.append(span)
            continue
        if span.kind != "text":
            raise ValueError(
                f"{span.kind} span {span.raw!r} straddles the range "
                f"[{start}, {end})"
            )
        left, right = max(start, span.start), min(end, span.end)
        out.append(
            Span(
                "text",
                span.raw[left - span.start : right - span.start],
                left,
                right,
            )
        )
    return out


def spans_cross(spans: list[Span], position: int) -> Span | None:
    """The markup span strictly straddling ``position``, if any.

    Used by ``validate`` to prove no section boundary falls inside a ``[...]``,
    ``<...>`` or ``~~...~~`` run or a footnote anchor.
    """
    for span in spans:
        if span.kind == "text":
            continue
        if span.start < position < span.end:
            return span
    return None


def pages_for_range(spans: list[Span], start: int, end: int) -> list[str]:
    """Manuscript pages a body range touches.

    A ``[p. N]`` marker closes page N, so the page in force at a position is the
    first marker at or after it.
    """
    breaks = [s for s in spans if s.kind == "page_break"]
    order = [b.page for b in breaks]
    pages: list[str] = []
    for position in (start, max(start, end - 1)):
        page = next((b.page for b in breaks if b.end > position), "")
        if page and page not in pages:
            pages.append(page)
    for brk in breaks:
        if start <= brk.start < end and brk.page not in pages:
            pages.append(brk.page)
    return sorted(pages, key=order.index)


# --------------------------------------------------------------------------- #
# repo conveniences
# --------------------------------------------------------------------------- #

TRANSCRIPTS = {
    "B": "transcripts/bullock.md",
    "W": "transcripts/woodruff.md",
    "R": "transcripts/richards.md",
    "C": "transcripts/clayton.md",
    "T": "transcripts/times-and-seasons.md",
}

#: All five witnesses, in edition order.
SIGLA = ("B", "W", "R", "C", "T")

#: The four independent reports taken down on 7 April 1844.
EYEWITNESS_SIGLA = ("B", "W", "R", "C")

#: T is the published composite Bullock and Clayton assembled from the notes.
#: It is included so readers can see how the received text was built, and must
#: be labelled derived wherever it is shown.
WITNESS_KINDS = {
    "B": "eyewitness",
    "W": "eyewitness",
    "R": "eyewitness",
    "C": "eyewitness",
    "T": "derived",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_all(root: Path | None = None) -> dict[str, Document]:
    root = Path(root) if root else repo_root()
    return {s: parse_file(root / p) for s, p in TRANSCRIPTS.items()}
