"""Integrity checks for the derived data layers.

Every invariant the section layer claims is checked here against the transcripts
themselves, so ``python3 -m kf validate`` either passes or names the file, the
section and the witness at fault.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import jsp
from .segments import Edition

FOOTNOTE_KINDS = {"textual", "times_and_seasons", "scripture", "other"}
EXPECTED_SECTION_IDS = [f"S{n:02d}" for n in range(1, 36)]
#: Every id the apparatus has ever issued. V001-V034 are the January 2026
#: entries, kept under their original ids; V035 onward were added in Phase 2b.
#: Ids are never reused and never deleted: an entry that fails the criteria is
#: kept with ``status: "withdrawn"`` and a reason.
EXPECTED_VARIANT_IDS = [f"V{n:03d}" for n in range(1, 123)]

VARIANT_TYPES = {
    "theological",
    "historical",
    "rhetorical",
    "unique",
    "omission",
    "reception",
    "scribal",
}
VARIANT_STATUSES = {"revised", "new", "withdrawn"}

#: A reading may quote a cancelled word alongside the word that stands, in the
#: form ``kept text (canc. cancelled text)``; two struck spans at one point are
#: separated by ``"; "``. Each cancelled piece must be a real cancellation span
#: in that witness's diplomatic text for the section.
_CANCELLATION = re.compile(r"\s*\(canc\. (.+)\)$")
_CANCELLATION_SPAN = re.compile(r"~~(.+?)~~")

#: Cancellation and underline span counts per witness, from
#: ``refs/jsp-markup-audit.md``, where they were counted against the live JSP
#: pages. Checked here because a plain copy-and-paste of a JSP transcript
#: silently flattens both kinds into ordinary text: once that happens a cancelled
#: word reads like a word the scribe let stand, and nothing else in the pipeline
#: would notice. JSP encodes neither kind for the published T text.
EXPECTED_SPANS = {
    "B": {"cancellation": 16, "underline": 5},
    "W": {"cancellation": 3, "underline": 25},
    "R": {"cancellation": 7, "underline": 0},
    "C": {"cancellation": 10, "underline": 6},
    "T": {"cancellation": 0, "underline": 0},
}


def _count_kind(spans: list[jsp.Span], kind: str) -> int:
    return sum(
        (span.kind == kind) + _count_kind(span.children, kind) for span in spans
    )


def _check_transcripts(edition: Edition, problems: list[str]) -> None:
    for siglum, document in edition.documents.items():
        rebuilt = "".join(span.raw for span in document.spans)
        if rebuilt != document.body:
            problems.append(f"{siglum}: spans do not reconstruct the body text")
        if document.kind != jsp.WITNESS_KINDS[siglum]:
            problems.append(
                f"{siglum}: kind {document.kind!r} != "
                f"{jsp.WITNESS_KINDS[siglum]!r}"
            )
        for kind, expected in EXPECTED_SPANS[siglum].items():
            found = _count_kind(document.spans, kind)
            if found != expected:
                problems.append(
                    f"{siglum}: {found} {kind} spans, expected {expected} "
                    "(has the transcript been re-pasted without markup?)"
                )
        numbers = [span.number for span in document.anchors]
        if numbers != list(range(1, len(numbers) + 1)):
            problems.append(f"{siglum}: footnote anchors are not sequential: {numbers}")
        if len(numbers) != len(document.footnotes):
            problems.append(
                f"{siglum}: {len(numbers)} footnote anchors but "
                f"{len(document.footnotes)} footnotes"
            )
        missing = sorted(set(numbers) - set(document.footnotes))
        if missing:
            problems.append(f"{siglum}: anchors with no footnote text: {missing}")


def _check_sections(edition: Edition, problems: list[str]) -> None:
    ids = [section.id for section in edition.sections]
    if ids != EXPECTED_SECTION_IDS:
        problems.append(f"sections.json: expected S01..S35 in order, got {ids}")
    for section in edition.sections:
        if not section.label.strip():
            problems.append(f"{section.id}: empty label")
        if not section.summary.strip():
            problems.append(f"{section.id}: empty summary")
        for siglum in jsp.SIGLA:
            entry = section.witnesses[siglum]
            if not entry.present and not entry.note.strip():
                problems.append(f"{section.id}/{siglum}: absent with no note")

    for siglum, document in edition.documents.items():
        body = document.body
        ranges = [
            (section.id, section.witnesses[siglum])
            for section in edition.sections
            if section.witnesses[siglum].present
        ]
        if not ranges:
            problems.append(f"{siglum}: no sections present")
            continue

        # Exact slices.
        for section_id, entry in ranges:
            if entry.text != body[entry.char_start : entry.char_end]:
                problems.append(
                    f"{section_id}/{siglum}: text != body[{entry.char_start}:"
                    f"{entry.char_end}]"
                )
            if entry.char_start >= entry.char_end:
                problems.append(f"{section_id}/{siglum}: empty or inverted range")

        # Order, no overlap, no gap, full coverage.
        first_id, first = ranges[0]
        if first.char_start != 0:
            problems.append(
                f"{first_id}/{siglum}: first section starts at {first.char_start}, "
                "not 0"
            )
        last_id, last = ranges[-1]
        if last.char_end != len(body):
            problems.append(
                f"{last_id}/{siglum}: last section ends at {last.char_end}, "
                f"not {len(body)}"
            )
        for (previous_id, previous), (next_id, following) in zip(ranges, ranges[1:]):
            if following.char_start != previous.char_end:
                relation = (
                    "overlaps" if following.char_start < previous.char_end else "gap"
                )
                problems.append(
                    f"{siglum}: {relation} between {previous_id} (ends "
                    f"{previous.char_end}) and {next_id} (starts "
                    f"{following.char_start})"
                )

        # Boundaries land between tokens and outside markup.
        for section_id, entry in ranges:
            position = entry.char_start
            if position == 0:
                continue
            straddled = jsp.spans_cross(document.spans, position)
            if straddled is not None:
                problems.append(
                    f"{section_id}/{siglum}: boundary {position} falls inside a "
                    f"{straddled.kind} span {straddled.raw!r}"
                )
            if not body[position - 1].isspace():
                problems.append(
                    f"{section_id}/{siglum}: boundary {position} is mid-token "
                    f"({body[max(0, position - 12):position + 12]!r})"
                )

        # The sections' reading words account for the whole discourse.
        total = sum(entry.word_count for _, entry in ranges)
        whole = jsp.word_count(document.spans)
        if total != whole:
            problems.append(
                f"{siglum}: section word counts total {total} but the whole "
                f"transcript reads {whole} words"
            )

        # Derived fields.
        for section_id, entry in ranges:
            spans = jsp.spans_in(document.spans, entry.char_start, entry.char_end)
            expected_words = jsp.word_count(spans)
            if entry.word_count != expected_words:
                problems.append(
                    f"{section_id}/{siglum}: word_count {entry.word_count} != "
                    f"{expected_words}"
                )
            expected_pages = jsp.pages_for_range(
                document.spans, entry.char_start, entry.char_end
            )
            if list(entry.pages) != expected_pages:
                problems.append(
                    f"{section_id}/{siglum}: pages {list(entry.pages)} != "
                    f"{expected_pages}"
                )


def _check_witnesses(edition: Edition, problems: list[str]) -> None:
    data = edition.witnesses_data
    listed = {w["siglum"]: w for w in data["witnesses"]}
    if set(listed) != set(jsp.SIGLA):
        problems.append(f"witnesses.json: sigla {sorted(listed)} != {list(jsp.SIGLA)}")
        return
    for siglum, entry in listed.items():
        document = edition.documents[siglum]
        path = edition.root / entry["transcript"]
        if not path.exists():
            problems.append(f"witnesses.json/{siglum}: missing {entry['transcript']}")
        if entry.get("kind") != jsp.WITNESS_KINDS[siglum]:
            problems.append(
                f"witnesses.json/{siglum}: kind {entry.get('kind')!r} != "
                f"{jsp.WITNESS_KINDS[siglum]!r}"
            )
        if not entry.get("jsp_citation", "").strip():
            problems.append(f"witnesses.json/{siglum}: no jsp_citation")
        if not entry.get("document", "").strip():
            problems.append(f"witnesses.json/{siglum}: no physical document")
        if entry["reporter"] != document.reporter:
            problems.append(
                f"witnesses.json/{siglum}: reporter {entry['reporter']!r} != "
                f"{document.reporter!r}"
            )
        expected_reading = jsp.word_count(document.spans)
        if entry["word_count_reading"] != expected_reading:
            problems.append(
                f"witnesses.json/{siglum}: word_count_reading "
                f"{entry['word_count_reading']} != {expected_reading}"
            )
        expected_raw = len(document.body.split())
        if entry["word_count_raw"] != expected_raw:
            problems.append(
                f"witnesses.json/{siglum}: word_count_raw "
                f"{entry['word_count_raw']} != {expected_raw}"
            )
        if entry["pages"] != document.pages:
            problems.append(
                f"witnesses.json/{siglum}: pages {entry['pages']} != {document.pages}"
            )
        if entry["footnote_count"] != len(document.footnotes):
            problems.append(
                f"witnesses.json/{siglum}: footnote_count "
                f"{entry['footnote_count']} != {len(document.footnotes)}"
            )


def _check_footnotes(edition: Edition, problems: list[str]) -> None:
    data = edition.footnotes_data
    for siglum in jsp.SIGLA:
        document = edition.documents[siglum]
        entries = data["witnesses"].get(siglum)
        if entries is None:
            problems.append(f"footnotes.json: no entry for {siglum}")
            continue
        anchors = {span.number: span.start for span in document.anchors}
        if sorted(int(n) for n in entries) != sorted(document.footnotes):
            problems.append(
                f"footnotes.json/{siglum}: numbers do not match the transcript"
            )
            continue
        for number_key, entry in entries.items():
            number = int(number_key)
            if entry["text"] != document.footnotes[number]:
                problems.append(
                    f"footnotes.json/{siglum}/{number}: text does not match transcript"
                )
            if entry["anchor_char"] != anchors[number]:
                problems.append(
                    f"footnotes.json/{siglum}/{number}: anchor_char "
                    f"{entry['anchor_char']} != {anchors[number]}"
                )
            expected_section = edition.section_of_offset(siglum, anchors[number])
            if entry["section"] != expected_section:
                problems.append(
                    f"footnotes.json/{siglum}/{number}: section "
                    f"{entry['section']!r} != {expected_section!r}"
                )
            if entry["kind"] not in FOOTNOTE_KINDS:
                problems.append(
                    f"footnotes.json/{siglum}/{number}: bad kind {entry['kind']!r}"
                )


def _check_apparatus(edition: Edition, problems: list[str]) -> None:
    data = edition.apparatus_data
    ids = [v["id"] for v in data["variants"]]
    if sorted(ids) != EXPECTED_VARIANT_IDS:
        problems.append(
            f"apparatus.json: expected V001..V{len(EXPECTED_VARIANT_IDS):03d} "
            f"exactly once each, got {len(ids)} ids"
        )
    order_key = [(v["section"], v["order"]) for v in data["variants"]]
    if order_key != sorted(order_key):
        problems.append("apparatus.json: entries are not ordered by section then order")
    seen: set[tuple[str, int]] = set()
    for variant in data["variants"]:
        vid = variant["id"]
        section_id = variant["section"]
        if section_id not in edition.by_id:
            problems.append(f"apparatus.json/{vid}: unknown section {section_id!r}")
            continue
        key = (section_id, variant["order"])
        if key in seen:
            problems.append(f"apparatus.json/{vid}: duplicate order {key}")
        seen.add(key)
        if variant["type"] not in VARIANT_TYPES:
            problems.append(f"apparatus.json/{vid}: bad type {variant['type']!r}")
        if variant.get("status") not in VARIANT_STATUSES:
            problems.append(f"apparatus.json/{vid}: bad status {variant.get('status')!r}")
        if variant["type"] == "reception" and variant["readings"].get("T") == "om.":
            problems.append(f"apparatus.json/{vid}: reception entry with no T reading")
        if not isinstance(variant.get("sources"), list):
            problems.append(f"apparatus.json/{vid}: sources is not a list")
        if not isinstance(variant.get("jsp_footnotes"), list):
            problems.append(f"apparatus.json/{vid}: jsp_footnotes is not a list")
        for note in variant.get("jsp_footnotes", []):
            witness, number = note["witness"], note["n"]
            if number not in edition.documents[witness].footnotes:
                problems.append(
                    f"apparatus.json/{vid}: no footnote {witness} n. {number}"
                )
        legacy = variant.get("legacy_verification")
        if legacy is not None and not isinstance(legacy, dict):
            problems.append(
                f"apparatus.json/{vid}: legacy_verification is not an object"
            )
        for stale in ("verification", "verification_note", "witnesses", "flag", "note"):
            if stale in variant:
                problems.append(f"apparatus.json/{vid}: stale field {stale!r}")
        if set(variant["readings"]) != set(jsp.SIGLA):
            problems.append(f"apparatus.json/{vid}: readings must cover B W R C T")
            continue
        _check_variant_quotations(edition, variant, problems)


def _quoted_section(variant: dict, siglum: str) -> str:
    """The section a reading is quoted from, which is the entry's own unless the
    witness takes the material out of the base text's order."""
    return variant.get("reading_sections", {}).get(siglum, variant["section"])


def _check_variant_quotations(
    edition: Edition, variant: dict, problems: list[str]
) -> None:
    """Every reading must be verbatim in the witness's reading text.

    This is the check that keeps the apparatus honest. The January 2026 entries
    it replaces held paraphrases — normalised spelling, silently joined clauses,
    ellipses — which read as quotations and were not. Thirty-five of their 119
    eyewitness readings could not be found in the transcripts at all.
    """
    vid = variant["id"]
    lemma_witness = variant.get("lemma_witness", "B")
    lemma_section = _quoted_section(variant, lemma_witness)
    lemma_text = edition.reading(lemma_section, lemma_witness)
    if variant["lemma"] not in lemma_text:
        problems.append(
            f"apparatus.json/{vid}: lemma is not verbatim in "
            f"{lemma_section}/{lemma_witness}"
        )
    for siglum in jsp.SIGLA:
        reading = variant["readings"][siglum]
        if reading == "om.":
            continue
        section_id = _quoted_section(variant, siglum)
        if not edition.by_id[section_id].witnesses[siglum].present:
            problems.append(
                f"apparatus.json/{vid}/{siglum}: witness is absent from "
                f"{section_id} but a reading is given"
            )
            continue
        match = _CANCELLATION.search(reading)
        kept = reading
        if match:
            kept = reading[: match.start()]
            struck = set(
                _CANCELLATION_SPAN.findall(edition.diplomatic(section_id, siglum))
            )
            for piece in match.group(1).split("; "):
                if piece not in struck:
                    problems.append(
                        f"apparatus.json/{vid}/{siglum}: {piece!r} is not a "
                        f"cancellation in {section_id}"
                    )
        if kept and kept not in edition.reading(section_id, siglum):
            problems.append(
                f"apparatus.json/{vid}/{siglum}: reading is not verbatim in "
                f"{section_id}"
            )


def run(root: Path | None = None) -> list[str]:
    """Run every check and return a list of problem descriptions."""
    edition = Edition(root)
    problems: list[str] = []
    _check_transcripts(edition, problems)
    _check_sections(edition, problems)
    _check_witnesses(edition, problems)
    _check_footnotes(edition, problems)
    _check_apparatus(edition, problems)
    return problems


def report(root: Path | None = None) -> tuple[bool, str]:
    """Human-readable validation report and whether everything passed."""
    edition = Edition(root)
    problems = run(root)
    lines = ["King Follett data validation", ""]
    for siglum in jsp.SIGLA:
        document = edition.documents[siglum]
        present = [
            section.id
            for section in edition.sections
            if section.witnesses[siglum].present
        ]
        lines.append(
            f"  {siglum} {document.reporter:<18}"
            f"{'(derived) ' if document.kind == 'derived' else '          '}"
            f"body {len(document.body):>6} chars  "
            f"{jsp.word_count(document.spans):>5} reading words  "
            f"{len(present):>2}/35 sections  "
            f"{len(document.footnotes):>2} footnotes  "
            f"pages {document.pages[0]}–{document.pages[-1]}"
        )
    lines.append("")
    lines.append("  checks: span/body round trip, cancellation and underline span")
    lines.append("          counts against the JSP audit, footnote anchor sequence and")
    lines.append("          count, section slice equality, order, non-overlap, gapless")
    lines.append("          partition of the whole body, boundaries outside markup and")
    lines.append("          between tokens, word counts, page ranges, witnesses.json,")
    lines.append("          footnotes.json anchors and sections, apparatus.json ids,")
    lines.append("          types, statuses, order and verbatim readings")
    lines.append("")
    if problems:
        lines.append(f"FAIL — {len(problems)} problem(s):")
        lines.extend(f"  - {problem}" for problem in problems)
    else:
        lines.append("OK — all checks passed.")
    return not problems, "\n".join(lines)
