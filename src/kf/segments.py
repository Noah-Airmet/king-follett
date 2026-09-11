"""Section layer: read ``data/sections.json`` and slice the transcripts by it.

``data/sections.json`` is the source of truth for the alignment. Every section
records explicit character offsets into a witness's body plus the verbatim slice
those offsets produce, so this module never has to re-find text by searching for
snippets — the failure mode of the superseded ``data/align.py``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import jsp


@dataclass
class WitnessSection:
    section_id: str
    siglum: str
    present: bool
    note: str = ""
    char_start: int = 0
    char_end: int = 0
    text: str = ""
    pages: tuple[str, ...] = ()
    word_count: int = 0

    @property
    def spans(self) -> list[jsp.Span]:
        raise NotImplementedError  # spans need the document; see Edition.spans_for


@dataclass
class Section:
    id: str
    label: str
    summary: str
    witnesses: dict[str, WitnessSection]
    boundary_notes: dict[str, str]

    def present_sigla(self) -> list[str]:
        return [s for s in jsp.SIGLA if self.witnesses[s].present]


class Edition:
    """The transcripts plus the section, footnote and apparatus layers."""

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else jsp.repo_root()
        self.documents = jsp.load_all(self.root)
        self.sections_data = self._read("sections.json")
        self.sections = [self._section(s) for s in self.sections_data["sections"]]
        self.by_id = {s.id: s for s in self.sections}

    # -- loading ---------------------------------------------------------- #

    def _read(self, name: str) -> dict:
        path = self.root / "data" / name
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _section(raw: dict) -> Section:
        witnesses = {}
        for siglum in jsp.SIGLA:
            entry = raw[siglum]
            if entry.get("present"):
                witnesses[siglum] = WitnessSection(
                    section_id=raw["id"],
                    siglum=siglum,
                    present=True,
                    char_start=entry["char_start"],
                    char_end=entry["char_end"],
                    text=entry["text"],
                    pages=tuple(entry.get("pages", ())),
                    word_count=entry.get("word_count", 0),
                )
            else:
                witnesses[siglum] = WitnessSection(
                    section_id=raw["id"],
                    siglum=siglum,
                    present=False,
                    note=entry.get("note", ""),
                )
        return Section(
            id=raw["id"],
            label=raw["label"],
            summary=raw["summary"],
            witnesses=witnesses,
            boundary_notes=raw.get("boundary_notes", {}),
        )

    @property
    def footnotes_data(self) -> dict:
        return self._read("footnotes.json")

    @property
    def apparatus_data(self) -> dict:
        return self._read("apparatus.json")

    @property
    def witnesses_data(self) -> dict:
        return self._read("witnesses.json")

    # -- slicing ---------------------------------------------------------- #

    def spans_for(self, section_id: str, siglum: str) -> list[jsp.Span]:
        entry = self.by_id[section_id].witnesses[siglum]
        if not entry.present:
            return []
        return jsp.spans_in(
            self.documents[siglum].spans, entry.char_start, entry.char_end
        )

    def reading(self, section_id: str, siglum: str) -> str:
        return jsp.render_reading(self.spans_for(section_id, siglum))

    def diplomatic(self, section_id: str, siglum: str) -> str:
        return jsp.render_diplomatic(self.spans_for(section_id, siglum))

    def normalized(self, section_id: str, siglum: str) -> str:
        return jsp.render_normalized(self.spans_for(section_id, siglum))

    def section_of_offset(self, siglum: str, offset: int) -> str | None:
        """The section id whose range contains ``offset`` for this witness."""
        for section in self.sections:
            entry = section.witnesses[siglum]
            if entry.present and entry.char_start <= offset < entry.char_end:
                return section.id
        return None

    def word_counts(self) -> dict[str, dict[str, int | None]]:
        """``{section_id: {siglum: word_count or None}}``."""
        return {
            section.id: {
                siglum: (
                    section.witnesses[siglum].word_count
                    if section.witnesses[siglum].present
                    else None
                )
                for siglum in jsp.SIGLA
            }
            for section in self.sections
        }
