#!/usr/bin/env python3
"""Build the static edition into ``site/``.

Everything the site shows comes from ``data/`` and ``transcripts/`` — the same
files ``python3 -m kf validate`` checks — or from the Markdown in ``content/``.
No number is typed into a page by hand: prose refers to counts as
``{{stats.total_variants}}`` and this script fills them, so the commentary
cannot drift from the edition it describes.

    python3 build.py              # write site/
    python3 build.py --serve      # write site/, then serve it on :8000

``docs/`` is the January 2026 site and is never touched here; it stays until
the move to kingfollett.noahairmet.com replaces it with a redirect stub.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from kf.segments import Edition  # noqa: E402
from kfweb import pages, render  # noqa: E402

OUT = ROOT / "site"
WEB = ROOT / "web"
CONTENT = ROOT / "content"

PLACEHOLDER = re.compile(r"\{\{\s*stats\.([a-zA-Z0-9_.]+)\s*\}\}")

#: Filled by ``build`` before any content is rendered, so prose can cite
#: variants and sections as links without each page passing them down.
_VARIANT_IDS: set[str] = set()
_SECTION_IDS: set[str] = set()


# --------------------------------------------------------------------------- #
# numbers
# --------------------------------------------------------------------------- #


def statistics(edition: Edition) -> dict[str, object]:
    """Every number the prose is allowed to quote, keyed as it is written.

    ``{{stats.words.B}}`` resolves through the dots, so the content files read
    naturally and a typo in a key fails the build loudly instead of printing a
    placeholder into a published page.
    """
    variants = edition.apparatus_data["variants"]
    types: dict[str, int] = {}
    for variant in variants:
        types[variant["type"]] = types.get(variant["type"], 0) + 1
    witnesses = {w["siglum"]: w for w in edition.witnesses_data["witnesses"]}
    return {
        "sections": len(edition.sections),
        "total_variants": len(variants),
        "witnesses": len(witnesses),
        "eyewitnesses": sum(1 for w in witnesses.values() if w["kind"] == "eyewitness"),
        "types": types,
        "words": {s: w["word_count_reading"] for s, w in witnesses.items()},
        "cancellations": {s: w["cancellation_spans"] for s, w in witnesses.items()},
        "footnotes": {s: w["footnote_count"] for s, w in witnesses.items()},
        "pages": {s: w["page_range"] for s, w in witnesses.items()},
    }


def _resolve(stats: dict, dotted: str) -> str:
    value: object = stats
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(f"unknown placeholder: stats.{dotted}")
        value = value[part]
    return f"{value:,}" if isinstance(value, int) and value >= 10000 else str(value)


# --------------------------------------------------------------------------- #
# content
# --------------------------------------------------------------------------- #


def read_content(name: str, stats: dict) -> tuple[dict, str]:
    """One Markdown file from ``content/`` as (front matter, HTML).

    Returns an empty pair when the file does not exist: Phase 2d writes these,
    and the site is expected to build — with honest gaps — before it has run.
    """
    path = CONTENT / f"{name}.md"
    if not path.exists():
        return {}, ""
    raw = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    if raw.startswith("---"):
        _, front, raw = raw.split("---", 2)
        for line in front.strip().splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
    raw = PLACEHOLDER.sub(lambda m: _resolve(stats, m.group(1)), raw)

    import markdown  # imported here so `--help` works without the dependency

    html = markdown.markdown(raw, extensions=["footnotes", "tables", "attr_list"])
    return meta, render.linkify(html, _VARIANT_IDS, _SECTION_IDS)


def split_by_siglum(html: str) -> dict[str, str]:
    """Cut ``content/witnesses.md``'s rendered HTML into one block per witness.

    The file is written as one essay with a heading per witness, which is how
    it reads best; the site wants each witness's paragraphs on that witness's
    own page. Splitting on the rendered headings keeps the source a single
    coherent document rather than five fragments maintained in parallel.

    python-markdown collects every footnote into one list at the end of the
    document, which would otherwise ride along on whichever witness came last.
    Each block therefore gets back only the notes its own text cites, so a page
    carries its references and no one else's.
    """
    notes = ""
    match = re.search(r'<div class="footnote">.*?</div>', html, re.S)
    if match:
        notes = match.group(0)
        html = html[: match.start()]

    items = dict(re.findall(r'(<li id="fn:([^"]+)">.*?</li>)', notes, re.S)) if notes else {}
    by_id = {key: item for item, key in re.findall(r'(<li id="fn:([^"]+)">.*?</li>)', notes, re.S)}

    blocks: dict[str, str] = {}
    current = ""
    for chunk in re.split(r"(<h2[^>]*>.*?</h2>)", html, flags=re.S):
        heading = re.match(r"<h2[^>]*>\s*([BWRCT])\s*(?:—|&mdash;|-)", chunk)
        if heading:
            current = heading.group(1)
            blocks[current] = ""
        elif current:
            blocks[current] += chunk

    for siglum, block in blocks.items():
        cited = dict.fromkeys(re.findall(r'href="#fn:([^"]+)"', block))
        mine = [by_id[key] for key in cited if key in by_id]
        if mine:
            blocks[siglum] = (
                block
                + '<div class="footnote"><hr><ol>'
                + "".join(mine)
                + "</ol></div>"
            )
    return blocks


def stub(what: str, charter: str) -> str:
    """An honest gap.

    A page whose prose has not been written says so rather than shipping filler
    that reads like an edition's considered statement.
    """
    return (
        f'<p class="stub">The {what} has not been written yet. It is Phase 2d, '
        f"charted in <code>{charter}</code>, and must be written against the "
        "adjudicated apparatus rather than before it.</p>"
    )


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #


def write(path: str, html: str) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def reception_page(edition: Edition, stats: dict) -> str:
    _, prose = read_content("textual-history", stats)
    entries = [v for v in edition.apparatus_data["variants"] if v["type"] == "reception"]
    ledger = pages.tag(
        "section",
        pages.tag("h2", "Where the printed text departs from the notes"),
        pages.tag(
            "p",
            pages.esc(
                f"{len(entries)} entries. These are the places the Times and "
                "Seasons said something no eyewitness wrote down, or chose one "
                "report against the others at a point that shaped what was "
                "afterwards quoted."
            ),
            class_="lede",
        ),
        pages.tag("div", *(pages.entry_html(v) for v in entries), class_="ledger"),
        class_="reception-ledger",
    )
    return pages.prose_page(
        title="Reception",
        description="How the received text of the King Follett Discourse was built.",
        html=prose or stub("account of the received text", "charters/phase2d-content.md"),
        active="/reception/",
        extra=ledger,
    )


def commentary_page(edition: Edition, stats: dict) -> str:
    _, prose = read_content("commentary", stats)
    return pages.prose_page(
        title="Analysis and commentary",
        description=(
            "What the reports agree on, where they diverge, and what can and "
            "cannot be inferred from the difference."
        ),
        html=prose or stub("commentary", "charters/phase2d-content.md"),
        active="/commentary/",
    )


def about_page(edition: Edition, stats: dict) -> str:
    sections = []
    for name, heading in (
        ("introduction", "The edition"),
        ("reading-the-apparatus", "Reading the apparatus"),
        ("verification", "What this edition claims"),
        ("bibliography", "Sources"),
    ):
        _, prose = read_content(name, stats)
        sections.append(
            pages.tag(
                "section",
                pages.tag("h2", pages.esc(heading)),
                prose or stub(heading.lower(), "charters/phase2d-content.md"),
                id=name,
            )
        )
    return pages.prose_page(
        title="About",
        description="What this edition is, how it was made, and what it does not claim.",
        html="".join(sections),
        active="/about/",
    )


FAVICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" fill="#f4f1e8"/>'
    '<g fill="#2f3f63">'
    '<rect x="6" y="5" width="3" height="22"/>'
    '<rect x="12" y="5" width="2" height="17"/>'
    '<rect x="17" y="5" width="1.2" height="22"/>'
    "</g>"
    '<rect x="22" y="5" width="4" height="22" fill="#8a6a48"/>'
    "</svg>"
)


def build(*, verbose: bool = True) -> Edition:
    edition = Edition(ROOT)
    stats = statistics(edition)

    digest = hashlib.sha256()
    for asset in ("edition.css", "edition.js"):
        digest.update((WEB / asset).read_bytes())
    pages.ASSET_VERSION = digest.hexdigest()[:8]

    _VARIANT_IDS.update(v["id"] for v in edition.apparatus_data["variants"])
    _SECTION_IDS.update(s.id for s in edition.sections)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    write("index.html", pages.spine(edition))
    write("apparatus/index.html", pages.apparatus_page(edition))
    for type_ in sorted({v["type"] for v in edition.apparatus_data["variants"]}):
        write(f"apparatus/{type_}/index.html", pages.apparatus_page(edition, only=type_))
    write("witnesses/index.html", pages.witness_index(edition))
    _, witness_prose = read_content("witnesses", stats)
    by_siglum = split_by_siglum(witness_prose) if witness_prose else {}
    for siglum in pages.SIGLA:
        write(
            f"witnesses/{siglum.lower()}/index.html",
            pages.witness_page(edition, siglum, by_siglum.get(siglum, "")),
        )
    write("commentary/index.html", commentary_page(edition, stats))
    write("reception/index.html", reception_page(edition, stats))
    write("about/index.html", about_page(edition, stats))
    write("favicon.svg", FAVICON)
    write("stats.json", json.dumps(stats, indent=2, ensure_ascii=False))

    for asset in ("edition.css", "edition.js"):
        shutil.copy2(WEB / asset, OUT / asset)
    shutil.copytree(WEB / "fonts", OUT / "fonts")

    if verbose:
        written = sorted(p.relative_to(OUT) for p in OUT.rglob("*") if p.is_file())
        total = sum((OUT / p).stat().st_size for p in written)
        print(f"site/ — {len(written)} files, {total / 1024:.0f} KB")
        print(
            f"  {stats['sections']} sections · {stats['total_variants']} variants · "
            f"{stats['witnesses']} witnesses"
        )
        missing = [n for n in ("introduction", "verification") if not (CONTENT / f"{n}.md").exists()]
        if missing:
            print(f"  prose still to come (Phase 2d): {', '.join(missing)}")
    return edition


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--serve", action="store_true", help="serve site/ on :8000")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    build()

    if args.serve:
        import functools
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

        class Handler(SimpleHTTPRequestHandler):
            """Serve site/ with caching off.

            The pages are hashed-asset-versioned for production, but the HTML
            itself is not, and a browser holding a stale index.html will show
            you the previous build while reporting the new one's URL. That has
            cost real debugging time on this project more than once.
            """

            def end_headers(self):
                self.send_header("Cache-Control", "no-store, must-revalidate")
                super().end_headers()

        handler = functools.partial(Handler, directory=str(OUT))
        print(f"http://localhost:{args.port}/")
        ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
