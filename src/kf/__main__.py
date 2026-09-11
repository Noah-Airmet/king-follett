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
