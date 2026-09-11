"""``python3 -m kf`` — command line for the King Follett data layer."""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

from . import jsp, validate
from .segments import Edition


def cmd_validate(args: argparse.Namespace) -> int:
    ok, text = validate.report(args.root)
    print(text)
    return 0 if ok else 1


def cmd_section(args: argparse.Namespace) -> int:
    edition = Edition(args.root)
    section_id = args.id.upper()
    if section_id not in edition.by_id:
        print(f"no such section: {args.id}", file=sys.stderr)
        return 2
    section = edition.by_id[section_id]
    print(f"{section.id}  {section.label}")
    print(textwrap.fill(section.summary, 78, initial_indent="  ", subsequent_indent="  "))
    for siglum in jsp.SIGLA:
        entry = section.witnesses[siglum]
        document = edition.documents[siglum]
        label = f"{siglum} ({document.reporter}"
        label += ", derived)" if document.kind == "derived" else ")"
        print()
        if not entry.present:
            print(f"{label} — absent")
            print(textwrap.fill(entry.note, 78, initial_indent="  ", subsequent_indent="  "))
            continue
        print(
            f"{label} — chars {entry.char_start}–{entry.char_end}, "
            f"p. {', '.join(entry.pages)}, {entry.word_count} words"
            + ("  [t_only]" if entry.t_only else "")
        )
        body = (
            edition.diplomatic(section_id, siglum)
            if args.render == "diplomatic"
            else edition.reading(section_id, siglum)
            if args.render == "reading"
            else edition.normalized(section_id, siglum)
        )
        print(textwrap.fill(body, 78, initial_indent="  ", subsequent_indent="  "))
    if section.boundary_notes:
        print()
        print("boundary notes")
        for siglum, note in section.boundary_notes.items():
            print(
                textwrap.fill(
                    f"{siglum}: {note}",
                    78,
                    initial_indent="  ",
                    subsequent_indent="     ",
                )
            )
    return 0


def cmd_apparatus(args: argparse.Namespace) -> int:
    edition = Edition(args.root)
    section_id = args.id.upper()
    if section_id not in edition.by_id:
        print(f"no such section: {args.id}", file=sys.stderr)
        return 2
    section = edition.by_id[section_id]
    variants = [
        v for v in edition.apparatus_data["variants"] if v["section"] == section_id
    ]
    print(f"{section.id}  {section.label}")
    print(f"  {len(variants)} variant(s).  B is the base text; T is derived, not a report.")
    print("  lemma ] B ; W ; R ; C ‖ T")
    if not variants:
        print()
        print("  no variants recorded in this section")
        return 0
    for variant in variants:
        print()
        heading = f"{variant['id']}  {variant['type']}  [{variant['status']}]"
        lemma_witness = variant.get("lemma_witness", "B")
        if lemma_witness != "B":
            heading += f"  (lemma from {lemma_witness}; B has no counterpart)"
        print(heading)
        print(
            textwrap.fill(
                _apparatus_line(variant),
                78,
                initial_indent="  ",
                subsequent_indent="      ",
            )
        )
        if not args.brief:
            print(
                textwrap.fill(
                    variant["significance"],
                    78,
                    initial_indent="    ",
                    subsequent_indent="    ",
                )
            )
            trailer = []
            for note in variant["jsp_footnotes"]:
                trailer.append(f"JSP {note['witness']} n. {note['n']}")
            trailer.extend(variant["sources"])
            if trailer:
                print(
                    textwrap.fill(
                        "sources: " + "; ".join(trailer),
                        78,
                        initial_indent="    ",
                        subsequent_indent="      ",
                    )
                )
            if variant.get("legacy_verification"):
                print("    legacy_verification present (January 2026; superseded)")
    return 0


def _apparatus_line(variant: dict) -> str:
    """One variant in the classical form: lemma ] B ; W ; R ; C ‖ T."""
    sections = variant.get("reading_sections", {})

    def cell(siglum: str) -> str:
        text = variant["readings"][siglum]
        if siglum in sections:
            text += f" [{sections[siglum]}]"
        return f"{siglum} {text}"

    eyewitnesses = " ; ".join(cell(s) for s in jsp.EYEWITNESS_SIGLA)
    return f"{variant['lemma']} ] {eyewitnesses} \u2016 {cell('T')}"


def cmd_stats(args: argparse.Namespace) -> int:
    edition = Edition(args.root)
    print("Reading-text word counts per section (om. = witness omits the section)")
    print("T is the derived Times and Seasons composite, not a fifth report.")
    print()
    print("id   " + " ".join(f"{s:>6}" for s in jsp.SIGLA) + "  label")
    print("-" * 78)
    totals = dict.fromkeys(jsp.SIGLA, 0)
    for section in edition.sections:
        cells = []
        for siglum in jsp.SIGLA:
            entry = section.witnesses[siglum]
            if entry.present:
                totals[siglum] += entry.word_count
                cells.append(f"{entry.word_count:>6}")
            else:
                cells.append(f"{'om.':>6}")
        print(f"{section.id:<4} {' '.join(cells)}  {section.label}")
    print("-" * 78)
    print(
        f"{'all':<4} " + " ".join(f"{totals[s]:>6}" for s in jsp.SIGLA) + "  totals"
    )
    print()
    for siglum in jsp.SIGLA:
        document = edition.documents[siglum]
        print(
            f"  {siglum} {document.reporter:<18}"
            f"{'(derived) ' if document.kind == 'derived' else '          '}"
            f"raw {len(document.body.split()):>5}  "
            f"reading {jsp.word_count(document.spans):>5}  "
            f"sections {len([s for s in edition.sections if s.witnesses[siglum].present]):>2}"
        )
    return 0


def cmd_export_segments(args: argparse.Namespace) -> int:
    edition = Edition(args.root)
    out = Path(args.out) if args.out else edition.root / "data" / "segments"
    out.mkdir(parents=True, exist_ok=True)
    written = 0
    for section in edition.sections:
        for siglum in jsp.SIGLA:
            entry = section.witnesses[siglum]
            if not entry.present:
                continue
            for kind, text in (
                ("diplomatic", edition.diplomatic(section.id, siglum)),
                ("reading", edition.reading(section.id, siglum)),
            ):
                path = out / f"{section.id}-{siglum}.{kind}.txt"
                path.write_text(text + "\n", encoding="utf-8")
                written += 1
    print(f"wrote {written} files to {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m kf",
        description="King Follett Discourse critical edition — data tools.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (default: inferred from this package)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sub = subparsers.add_parser("validate", help="check every data invariant")
    sub.set_defaults(func=cmd_validate)

    sub = subparsers.add_parser("section", help="print one section in all witnesses")
    sub.add_argument("id", help="section id, e.g. S08")
    sub.add_argument(
        "--render",
        choices=("diplomatic", "reading", "normalized"),
        default="diplomatic",
    )
    sub.set_defaults(func=cmd_section)

    sub = subparsers.add_parser(
        "apparatus", help="print the critical apparatus for one section"
    )
    sub.add_argument("id", help="section id, e.g. S20")
    sub.add_argument(
        "--brief",
        action="store_true",
        help="apparatus lines only, without significance and sources",
    )
    sub.set_defaults(func=cmd_apparatus)

    sub = subparsers.add_parser("stats", help="per-witness per-section word counts")
    sub.set_defaults(func=cmd_stats)

    sub = subparsers.add_parser(
        "export-segments", help="write per-section text files (generated, gitignored)"
    )
    sub.add_argument("--out", default=None, help="output directory")
    sub.set_defaults(func=cmd_export_segments)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
