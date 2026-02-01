"""
King Follett Discourse - Alignment & Collation Tool
Phase 1-2 Bridge: Parses witness transcripts, segments them by the alignment map,
and prepares normalized text for word-level collation in Phase 2.

Usage:
    python align.py                  # Print alignment overview
    python align.py --segment S08    # Print all witnesses for a section
    python align.py --export         # Export normalized segments to data/segments/
    python align.py --stats          # Print coverage statistics
"""

import json
import re
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ALIGNMENT_FILE = DATA_DIR / "alignment_map.json"

WITNESS_FILES = {
    "W": "woodruff.md",
    "B": "bullock.md",
    "R": "richards.md",
    "C": "clayton.md",
}


def load_transcript(siglum: str) -> str:
    """Load a witness transcript, returning only the body text (no header, no footnotes)."""
    filepath = BASE_DIR / WITNESS_FILES[siglum]
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip header (first two lines: title + "Document Transcript")
    body_start = 0
    for i, line in enumerate(lines):
        if "Document Transcript" in line:
            body_start = i + 1
            break

    # Find footnotes section
    body_end = len(lines)
    for i in range(body_start, len(lines)):
        if lines[i].strip() == "Footnotes":
            body_end = i
            break

    body = "".join(lines[body_start:body_end]).strip()
    return body


def normalize_text(text: str) -> str:
    """Normalize transcript text for comparison purposes.

    - Removes page markers [p. [133]]
    - Expands interlinear insertions <text> into the text
    - Expands abbreviated words: con[ference] -> conference
    - Removes footnote reference numbers
    - Normalizes whitespace
    """
    # Remove page markers
    text = re.sub(r'\[p\.\s*\[?\d+\]?\]', '', text)

    # Remove blank line markers like [25 lines blank], [1/3 page blank]
    text = re.sub(r'\[[\d/]+ (?:lines? )?blank\]', '', text)

    # Expand interlinear insertions (remove angle brackets with zero-width spaces)
    text = re.sub(r'<\u200B([^>]*)\u200B>', r'\1', text)
    text = re.sub(r'<([^>]*)>', r'\1', text)

    # Expand abbreviated words: e.g., con[ference] -> conference
    text = re.sub(r'(\w)\[(\w+)\]', r'\1\2', text)

    # Remove standalone editorial brackets like [King Follett]
    # but keep the text inside
    text = re.sub(r'\[([A-Z][^\]]+)\]', r'\1', text)

    # Remove remaining isolated brackets that are just letters
    text = re.sub(r'\[(\w)\]', r'\1', text)

    # Remove footnote reference numbers (digits right after punctuation or words)
    text = re.sub(r'(?<=[.,:;—\w])(\d{1,2})(?=\s|[A-Z]|$)', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def find_passage(body: str, start_marker: str, end_marker: str) -> str:
    """Extract a passage from the body text between start and end markers.

    Uses fuzzy matching to find the closest match for the markers.
    """
    # Normalize for searching
    norm_body = normalize_text(body)

    # Clean up markers for searching
    start_clean = re.sub(r'\[.*?\]', '', start_marker).strip()
    end_clean = re.sub(r'\[.*?\]', '', end_marker).strip()

    start_idx = norm_body.find(start_clean)
    end_idx = norm_body.find(end_clean)

    if start_idx == -1:
        # Try with first few words
        words = start_clean.split()[:5]
        partial = " ".join(words)
        start_idx = norm_body.find(partial)

    if end_idx == -1:
        words = end_clean.split()[:5]
        partial = " ".join(words)
        end_idx = norm_body.find(partial)

    if start_idx == -1:
        return f"[MARKER NOT FOUND: {start_marker[:50]}...]"

    if end_idx == -1 or end_idx <= start_idx:
        # Return from start to end of a reasonable chunk
        return norm_body[start_idx:start_idx + 500] + "..."

    # Include the end marker text
    end_idx = norm_body.find(" ", end_idx + len(end_clean))
    if end_idx == -1:
        end_idx = len(norm_body)

    return norm_body[start_idx:end_idx].strip()


def load_alignment():
    """Load the alignment map."""
    with open(ALIGNMENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_section_text(section: dict, siglum: str, transcripts: dict) -> str:
    """Get the normalized text for a witness in a given section."""
    witness_data = section.get(siglum, {})

    if isinstance(witness_data, dict):
        if witness_data.get("present") is False:
            return f"[om. {witness_data.get('note', 'Not present in this witness.')}]"

        start = witness_data.get("text_start", "")
        end = witness_data.get("text_end", "")

        if not start:
            return "[No text markers defined]"

        body = transcripts[siglum]
        return find_passage(body, start, end)

    return "[No data]"


def print_overview(alignment, transcripts):
    """Print an overview of all sections and which witnesses cover them."""
    print("=" * 80)
    print("KING FOLLETT DISCOURSE - ALIGNMENT OVERVIEW")
    print("=" * 80)
    print()
    print(f"{'ID':<6} {'Section':<50} {'W':>3} {'B':>3} {'R':>3} {'C':>3}")
    print("-" * 70)

    for section in alignment["sections"]:
        sid = section["id"]
        label = section["label"][:48]

        coverage = {}
        for sig in ["W", "B", "R", "C"]:
            w_data = section.get(sig, {})
            if isinstance(w_data, dict) and w_data.get("present") is False:
                coverage[sig] = " - "
            elif isinstance(w_data, dict) and w_data.get("text_start"):
                coverage[sig] = " + "
            else:
                coverage[sig] = " ? "

        print(f"{sid:<6} {label:<50} {coverage['W']:>3}{coverage['B']:>3}{coverage['R']:>3}{coverage['C']:>3}")

    print()
    print("Legend: + = present, - = omitted, ? = uncertain")


def print_section(alignment, transcripts, section_id):
    """Print all witness texts for a given section."""
    section = None
    for s in alignment["sections"]:
        if s["id"] == section_id:
            section = s
            break

    if not section:
        print(f"Section {section_id} not found.")
        return

    print("=" * 80)
    print(f"Section {section['id']}: {section['label']}")
    print(f"Summary: {section['summary']}")
    print("=" * 80)

    for sig in ["W", "B", "R", "C"]:
        name = alignment["metadata"]["witnesses"][sig]["name"]
        text = get_section_text(section, sig, transcripts)
        print(f"\n[{sig}] {name}:")
        print("-" * 40)
        # Word wrap
        words = text.split()
        line = "  "
        for word in words:
            if len(line) + len(word) + 1 > 78:
                print(line)
                line = "  " + word
            else:
                line += " " + word if line.strip() else "  " + word
        if line.strip():
            print(line)
    print()


def print_stats(alignment, transcripts):
    """Print coverage statistics."""
    print("=" * 80)
    print("COVERAGE STATISTICS")
    print("=" * 80)

    total_sections = len(alignment["sections"])
    coverage = {sig: 0 for sig in ["W", "B", "R", "C"]}

    for section in alignment["sections"]:
        for sig in ["W", "B", "R", "C"]:
            w_data = section.get(sig, {})
            if isinstance(w_data, dict) and w_data.get("present") is not False and w_data.get("text_start"):
                coverage[sig] += 1

    print(f"\nTotal thematic sections: {total_sections}")
    print()
    for sig in ["B", "C", "W", "R"]:
        name = alignment["metadata"]["witnesses"][sig]["name"]
        count = coverage[sig]
        pct = count / total_sections * 100
        bar = "#" * int(pct / 2)
        print(f"  [{sig}] {name:<20} {count:>2}/{total_sections} sections ({pct:.0f}%)  {bar}")

    print()
    print("Sections absent from each witness:")
    for sig in ["W", "B", "R", "C"]:
        name = alignment["metadata"]["witnesses"][sig]["name"]
        missing = []
        for section in alignment["sections"]:
            w_data = section.get(sig, {})
            if isinstance(w_data, dict) and w_data.get("present") is False:
                missing.append(section["id"])
        if missing:
            print(f"  [{sig}] {name}: {', '.join(missing)}")
        else:
            print(f"  [{sig}] {name}: (none)")


def export_segments(alignment, transcripts):
    """Export normalized segments to individual files for Phase 2 processing."""
    seg_dir = DATA_DIR / "segments"
    seg_dir.mkdir(exist_ok=True)

    for section in alignment["sections"]:
        sid = section["id"]
        for sig in ["W", "B", "R", "C"]:
            text = get_section_text(section, sig, transcripts)
            outfile = seg_dir / f"{sid}_{sig}.txt"
            with open(outfile, "w", encoding="utf-8") as f:
                f.write(text)

    print(f"Exported {len(alignment['sections']) * 4} segment files to {seg_dir}")


def main():
    # Load data
    alignment = load_alignment()
    transcripts = {}
    for sig in ["W", "B", "R", "C"]:
        transcripts[sig] = load_transcript(sig)

    # Parse arguments
    if len(sys.argv) == 1:
        print_overview(alignment, transcripts)
    elif sys.argv[1] == "--segment" and len(sys.argv) > 2:
        section_id = sys.argv[2].upper()
        print_section(alignment, transcripts, section_id)
    elif sys.argv[1] == "--stats":
        print_stats(alignment, transcripts)
    elif sys.argv[1] == "--export":
        export_segments(alignment, transcripts)
    elif sys.argv[1] == "--help":
        print(__doc__)
    else:
        print(f"Unknown argument: {sys.argv[1]}")
        print(__doc__)


if __name__ == "__main__":
    main()
