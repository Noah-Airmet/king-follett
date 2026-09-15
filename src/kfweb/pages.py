"""The five page shapes.

The site has one reading surface — the spine — and everything else is an
entrance into it. The reader's whole configuration is three things: which
witnesses are lit, whether variants are marked, and whether the text is shown
as the scribe left it or as it reads. All three are plain checkboxes driven by
CSS, so the edition is fully operable with scripting disabled; ``edition.js``
adds URL state, the slip and the keyboard, and nothing else.
"""

from __future__ import annotations

from kf.segments import Edition

from . import rail, render
from .html import esc, tag

SIGLA = ("B", "W", "R", "C", "T")

NAV = (
    ("/", "The discourse"),
    ("/apparatus/", "Apparatus"),
    ("/reception/", "Reception"),
    ("/witnesses/", "Witnesses"),
    ("/about/", "About"),
)


# --------------------------------------------------------------------------- #
# shell
# --------------------------------------------------------------------------- #


def shell(
    *,
    title: str,
    description: str,
    body: str,
    active: str = "",
    body_class: str = "",
    controls: bool = False,
) -> str:
    nav = "".join(
        tag(
            "a",
            esc(label),
            href=href,
            class_="on" if href == active else None,
            aria_current="page" if href == active else None,
        )
        for href, label in NAV
    )
    full = f"{title} · King Follett Discourse" if title else "King Follett Discourse"
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{esc(full)}</title>\n"
        f'<meta name="description" content="{esc(description)}">\n'
        '<link rel="stylesheet" href="/edition.css">\n'
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
        "</head>\n"
        f'<body class="{esc(body_class)}">\n'
        '<a class="skip-link" href="#main">Skip to the text</a>\n'
        '<header class="masthead">'
        '<a class="wordmark" href="/">King Follett Discourse'
        '<span class="wordmark-sub">Nauvoo, 7 April 1844</span></a>'
        f'<nav class="nav">{nav}</nav>'
        "</header>\n"
        f"{_state_inputs() if controls else ''}"
        f"{body}\n"
        '<script type="module" src="/edition.js"></script>\n'
        "</body>\n</html>\n"
    )


def _state_inputs() -> str:
    """The reader's state, as checkboxes the stylesheet reads with ``:has()``.

    They live immediately inside ``<body>`` and out of the layout so that every
    selector below can be written against ``body:has(#w-W:checked)``. Bullock
    is lit by default because he is the base text; the others join him.
    """
    boxes = [
        tag(
            "input",
            type="checkbox",
            id=f"w-{s}",
            class_="state",
            checked=(s == "B"),
            data_witness=s,
        )
        for s in SIGLA
    ]
    boxes.append(tag("input", type="checkbox", id="show-variants", class_="state", checked=True))
    boxes.append(tag("input", type="checkbox", id="show-diplomatic", class_="state"))
    return f'<div class="state-store" hidden>{"".join(boxes)}</div>\n'


def controls_bar(edition: Edition) -> str:
    """The sigla are the controls, and therefore also the legend.

    No separate key: a letterform that is lit is a witness that is showing, and
    T stands past a rule because it is derived. Two switches follow.
    """
    marks = []
    for siglum in SIGLA:
        witness = edition.documents[siglum]
        marks.append(
            tag(
                "label",
                tag("span", esc(siglum), class_="sig-letter"),
                tag("span", esc(witness.reporter), class_="sig-name"),
                for_=f"w-{siglum}",
                class_=f"sig sig-{siglum}" + (" sig-derived" if siglum == "T" else ""),
                title=f"{witness.reporter} — {witness.kind}",
            )
        )
    switches = tag(
        "div",
        tag("label", "Variants", for_="show-variants", class_="switch"),
        tag("label", "Manuscript", for_="show-diplomatic", class_="switch"),
        class_="switches",
    )
    return tag(
        "div",
        tag("div", *marks, class_="sigla"),
        switches,
        class_="controls",
    )


# --------------------------------------------------------------------------- #
# the spine
# --------------------------------------------------------------------------- #


def _witness_column(edition: Edition, section, siglum: str, marks_by: dict) -> str:
    witness = section.witnesses[siglum]
    document = edition.documents[siglum]
    if not witness.present:
        return tag(
            "article",
            tag("span", esc(siglum), class_="wit-mark"),
            tag("p", esc(witness.note or "No material here."), class_="wit-absent"),
            class_=f"wit wit-{siglum} is-absent",
            data_siglum=siglum,
        )
    text = edition.reading(section.id, siglum)
    spans = edition.spans_for(section.id, siglum)
    pages = ", ".join(witness.pages)
    return tag(
        "article",
        tag("span", esc(siglum), class_="wit-mark"),
        tag(
            "div",
            render.reading_html(text, marks_by.get(siglum, [])),
            class_="reading",
        ),
        tag("div", render.diplomatic_html(spans, siglum), class_="diplomatic"),
        tag(
            "p",
            tag("span", esc(document.reporter), class_="wit-who"),
            tag("span", esc(f"p. {pages}" if pages else ""), class_="wit-page"),
            tag("span", esc(f"{witness.word_count} words"), class_="wit-words"),
            class_="wit-foot",
        ),
        class_=f"wit wit-{siglum}",
        data_siglum=siglum,
    )


def _section_apparatus(entries: list[dict]) -> str:
    if not entries:
        return ""
    count = len(entries)
    return tag(
        "details",
        tag(
            "summary",
            esc(f"{count} variant{'' if count == 1 else 's'} here"),
            class_="app-summary",
        ),
        tag("div", *(entry_html(e, compact=True) for e in entries), class_="app-list"),
        class_="sec-app",
    )


def spine(edition: Edition) -> str:
    variants = edition.apparatus_data["variants"]
    by_section: dict[str, list[dict]] = {}
    for variant in variants:
        by_section.setdefault(variant["section"], []).append(variant)

    blocks = []
    for section in edition.sections:
        entries = by_section.get(section.id, [])
        marks_by: dict[str, list[render.Mark]] = {}
        for siglum in SIGLA:
            witness = section.witnesses[siglum]
            if not witness.present:
                continue
            readings = [
                (e["id"], e["type"], e["readings"].get(siglum, ""))
                for e in entries
                if e.get("reading_sections", {}).get(siglum, e["section"]) == section.id
            ]
            marks_by[siglum] = render.locate(edition.reading(section.id, siglum), readings)

        columns = "".join(
            _witness_column(edition, section, siglum, marks_by) for siglum in SIGLA
        )
        blocks.append(
            tag(
                "section",
                tag(
                    "header",
                    tag("a", esc(section.id), class_="sec-id", href=f"#{section.id}"),
                    tag("h2", esc(section.label)),
                    tag("p", esc(section.summary), class_="sec-sum"),
                    class_="sec-head",
                ),
                tag("div", columns, class_="spread"),
                _section_apparatus(entries),
                class_="sec",
                id=section.id,
            )
        )

    body = tag(
        "div",
        tag(
            "aside",
            tag("div", rail.build(edition), class_="rail-inner"),
            class_="rail",
            aria_label="Section rail",
        ),
        tag(
            "main",
            controls_bar(edition),
            tag("div", *blocks, class_="spine"),
            id="main",
        ),
        class_="frame",
    )
    return shell(
        title="",
        description=(
            "A critical edition of Joseph Smith's King Follett Discourse, "
            "7 April 1844, from four eyewitness reports and the Times and "
            "Seasons composite."
        ),
        body=body,
        active="/",
        body_class="page-spine",
        controls=True,
    )


# --------------------------------------------------------------------------- #
# apparatus
# --------------------------------------------------------------------------- #


def entry_html(variant: dict, *, compact: bool = False) -> str:
    readings = []
    for siglum in SIGLA:
        reading = variant["readings"].get(siglum, "om.")
        readings.append(
            tag(
                "div",
                tag("span", esc(siglum), class_="rd-sig"),
                tag("span", esc(reading), class_="rd-text"),
                class_="rd" + (" rd-derived" if siglum == "T" else "")
                + (" rd-om" if reading == "om." else ""),
            )
        )
    head = tag(
        "div",
        tag("a", esc(variant["id"]), class_="v-id", href=f"#{variant['id']}"),
        tag("a", esc(variant["section"]), class_="v-sec", href=f"/#{variant['section']}"),
        tag("span", esc(variant["type"]), class_=f"v-type v-{variant['type']}"),
        class_="v-head",
    )
    # ``compact`` drops the bibliography, never the argument: the significance
    # note is what the slip shows when a reader taps a lemma in the text, so it
    # has to be in the page beside the reading it explains.
    parts = [
        head,
        tag("p", esc(variant["lemma"]), class_="v-lemma"),
        tag("div", *readings, class_="v-readings"),
        tag("p", esc(variant["significance"]), class_="v-sig"),
    ]
    if not compact:
        if variant.get("sources"):
            parts.append(
                tag(
                    "p",
                    esc("; ".join(variant["sources"])),
                    class_="v-sources",
                )
            )
    return tag(
        "article",
        *parts,
        class_="entry",
        id=variant["id"],
        data_type=variant["type"],
        data_section=variant["section"],
    )


def apparatus_page(edition: Edition, *, only: str = "") -> str:
    variants = edition.apparatus_data["variants"]
    types = sorted({v["type"] for v in variants})
    shown = [v for v in variants if not only or v["type"] == only]

    counts = {t: sum(1 for v in variants if v["type"] == t) for t in types}
    filters = [
        tag(
            "a",
            tag("span", "all", class_="f-name"),
            tag("span", esc(len(variants)), class_="f-count"),
            href="/apparatus/",
            class_="filter" + ("" if only else " on"),
            data_filter="",
        )
    ]
    filters += [
        tag(
            "a",
            tag("span", esc(t), class_="f-name"),
            tag("span", esc(counts[t]), class_="f-count"),
            href=f"/apparatus/{t}/",
            class_="filter" + (" on" if only == t else ""),
            data_filter=t,
        )
        for t in types
    ]

    body = tag(
        "main",
        tag(
            "div",
            tag("h1", "Apparatus"),
            tag(
                "p",
                esc(
                    "Every point where the reports differ in doctrinal claim, "
                    "historical detail, rhetorical force, scribal correction, or "
                    "in what the printed text made of them. T is recorded in "
                    "every entry and is never corroboration."
                ),
                class_="lede",
            ),
            class_="page-head",
        ),
        tag("nav", *filters, class_="filters", aria_label="Filter by type"),
        tag("div", *(entry_html(v) for v in shown), class_="ledger"),
        id="main",
        class_="sheet",
    )
    return shell(
        title="Apparatus" + (f" · {only}" if only else ""),
        description=f"The critical apparatus: {len(variants)} variants across 35 sections.",
        body=body,
        active="/apparatus/",
        body_class="page-apparatus",
    )


# --------------------------------------------------------------------------- #
# witnesses
# --------------------------------------------------------------------------- #


def witness_index(edition: Edition) -> str:
    rows = []
    for siglum in SIGLA:
        record = next(
            w for w in edition.witnesses_data["witnesses"] if w["siglum"] == siglum
        )
        rows.append(
            tag(
                "a",
                tag("span", esc(siglum), class_="w-sig"),
                tag(
                    "span",
                    tag("strong", esc(record["reporter"])),
                    tag("span", esc(record["role"].split(".")[0] + "."), class_="w-role"),
                    class_="w-body",
                ),
                tag("span", esc(record["kind"]), class_=f"w-kind w-{record['kind']}"),
                href=f"/witnesses/{siglum.lower()}/",
                class_="w-row",
            )
        )
    body = tag(
        "main",
        tag("div", tag("h1", "The witnesses"), class_="page-head"),
        tag("div", *rows, class_="w-list"),
        id="main",
        class_="sheet",
    )
    return shell(
        title="Witnesses",
        description="The four eyewitness reports and the derived Times and Seasons text.",
        body=body,
        active="/witnesses/",
        body_class="page-witnesses",
    )


def witness_page(edition: Edition, siglum: str) -> str:
    record = next(w for w in edition.witnesses_data["witnesses"] if w["siglum"] == siglum)
    document = edition.documents[siglum]
    notes = edition.footnotes_data["witnesses"].get(siglum, {})

    blocks = []
    for section in edition.sections:
        witness = section.witnesses[siglum]
        if not witness.present:
            continue
        spans = edition.spans_for(section.id, siglum)
        blocks.append(
            tag(
                "section",
                tag(
                    "header",
                    tag("a", esc(section.id), href=f"/#{section.id}", class_="sec-id"),
                    tag("h2", esc(section.label)),
                    class_="sec-head",
                ),
                tag("div", render.reading_html(edition.reading(section.id, siglum)), class_="reading"),
                tag("div", render.diplomatic_html(spans, siglum), class_="diplomatic"),
                class_="sec sec-solo",
                id=f"{siglum}-{section.id}",
            )
        )

    # JSP's "TEXT: Possibly ..." notes are this edition's uncertainty layer, so
    # they are marked rather than filed with the bibliographical annotation.
    note_items = [
        tag(
            "li",
            tag("a", esc(number), href=f"#r{number}", class_="fn-back"),
            tag("span", esc(note["text"]), class_="fn-text"),
            tag("span", esc(note["kind"].replace("_", " ")), class_="fn-kind"),
            id=f"n{number}",
            class_=f"fn-{note['kind']}",
        )
        for number, note in sorted(notes.items(), key=lambda kv: int(kv[0]))
    ]

    # T's record is a different kind of thing from a reporter's minute-book, so
    # its facts are different facts: who compiled it, out of which reports, and
    # where it was printed. Forcing it into the eyewitness shape would be the
    # first step towards reading it as a fifth report.
    if record["kind"] == "derived":
        publication = record["publication"]
        facts = [
            ("Compiled by", ", ".join(record["compilers"])),
            ("Out of", ", ".join(record["derived_from"])),
            (
                "Printed",
                f"{publication['periodical']} {publication['volume']}:{publication['number']}, "
                f"{publication['date']}, pp. {publication['pages']}",
            ),
            ("Reading words", record.get("word_count_reading", "")),
        ]
    else:
        facts = [
            ("Record", record["record"]),
            ("Taken down", record.get("taken_down", "")),
            ("Manuscript pages", record.get("page_range", "")),
            ("Reading words", record.get("word_count_reading", "")),
            ("Cancellations", record.get("cancellation_spans", "") or ""),
        ]
    fact_rows = "".join(
        tag("div", tag("dt", esc(k)), tag("dd", esc(v)), class_="fact")
        for k, v in facts
        if v
    )

    body = tag(
        "main",
        tag(
            "div",
            tag("span", esc(siglum), class_="w-sig-big"),
            tag("h1", esc(record["reporter"])),
            tag("p", esc(record["role"]), class_="lede"),
            tag("dl", fact_rows, class_="facts"),
            tag(
                "p",
                tag("a", "On the Joseph Smith Papers", href=record["jsp_url"], rel="external"),
                class_="jsp-link",
            ),
            class_="page-head",
        ),
        tag("div", tag("label", "Manuscript", for_="show-diplomatic", class_="switch"), class_="controls controls-solo"),
        tag("div", *blocks, class_="spine spine-solo"),
        tag(
            "section",
            tag("h2", "Editorial notes"),
            tag("ol", *note_items, class_="fn-list"),
            class_="notes",
        )
        if note_items
        else "",
        id="main",
        class_="sheet sheet-wide",
    )
    return shell(
        title=record["reporter"],
        description=f"{record['reporter']}'s report of the King Follett Discourse.",
        body=body,
        active="/witnesses/",
        body_class=f"page-witness page-witness-{siglum}",
        controls=True,
    )


# --------------------------------------------------------------------------- #
# prose pages
# --------------------------------------------------------------------------- #


def prose_page(
    *, title: str, description: str, html: str, active: str, extra: str = ""
) -> str:
    body = tag(
        "main",
        tag("div", tag("h1", esc(title)), class_="page-head"),
        tag("div", html, class_="prose"),
        extra,
        id="main",
        class_="sheet",
    )
    return shell(
        title=title,
        description=description,
        body=body,
        active=active,
        body_class="page-prose",
    )
