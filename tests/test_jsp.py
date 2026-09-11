"""Tests for the JSP convention parser.

Run from the repository root::

    python3 -m unittest discover tests
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kf import jsp  # noqa: E402

ZWSP = jsp.ZWSP


def spans(text: str) -> list[jsp.Span]:
    return jsp.parse_body(text)


def kinds(text: str) -> list[str]:
    return [span.kind for span in spans(text)]


class TestPageBreaks(unittest.TestCase):
    def test_plain_page_marker(self):
        parsed = spans("understand when I come to it [p. 14] I do not calculate")
        breaks = [s for s in parsed if s.kind == "page_break"]
        self.assertEqual([b.page for b in breaks], ["14"])

    def test_jsp_supplied_pagination_keeps_inner_brackets(self):
        parsed = spans("heirs of God. [p. [67]] and ascend a throne")
        breaks = [s for s in parsed if s.kind == "page_break"]
        self.assertEqual([b.page for b in breaks], ["[67]"])
        self.assertEqual(breaks[0].raw, "[p. [67]]")

    def test_page_marker_leaves_reading_text(self):
        self.assertEqual(
            jsp.render_reading(spans("heirs of God. [p. [67]] and ascend")),
            "heirs of God. and ascend",
        )


class TestExpansions(unittest.TestCase):
    def test_suffix_expansion(self):
        parsed = spans("the fore p[ar]t. of the Con[ference]")
        expansions = [s for s in parsed if s.kind == "expansion"]
        self.assertEqual([e.content for e in expansions], ["ar", "ference"])
        self.assertTrue(all(e.mode == "insert" for e in expansions))
        self.assertEqual(
            jsp.render_reading(parsed), "the fore part. of the Conference"
        )

    def test_infix_expansion(self):
        self.assertEqual(jsp.render_reading(spans("subj[ec]t.")), "subject.")

    def test_word_initial_expansion(self):
        self.assertEqual(jsp.render_reading(spans("God bless you [a]men—")),
                         "God bless you amen—")
        self.assertEqual(jsp.render_reading(spans("Want you should all [k]now God")),
                         "Want you should all know God")

    def test_respelling_replaces_the_scribal_form(self):
        parsed = spans("& noes [knows] nothing more")
        expansion = [s for s in parsed if s.kind == "expansion"][0]
        self.assertEqual(expansion.mode, "replace")
        self.assertEqual(jsp.render_reading(parsed), "& knows nothing more")

    def test_respelling_of_an_abbreviation_with_a_period(self):
        self.assertEqual(
            jsp.render_reading(spans("the soul the imm. [immortal] Spirit")),
            "the soul the immortal Spirit",
        )

    def test_respelling_of_a_redacted_word(self):
        self.assertEqual(
            jsp.render_reading(spans("must either obey the Gospel or be d——d [damned]")),
            "must either obey the Gospel or be damned",
        )


class TestGlosses(unittest.TestCase):
    def test_identification_gloss_is_dropped_not_merged(self):
        parsed = spans("our bror. Follit [King Follett] who was crushed")
        self.assertEqual([s.kind for s in parsed if s.kind != "text"], ["gloss"])
        self.assertEqual(
            jsp.render_reading(parsed), "our bror. Follit who was crushed"
        )

    def test_multiword_gloss_content_never_reaches_the_reading_text(self):
        # The bug in the superseded data/align.py: brackets were stripped but
        # their contents kept, yielding "the great Eloe Elōheem or Elohim".
        parsed = spans("of the great Eloe [El\u014dheem or Elohim] begin[nin]g")
        reading = jsp.render_reading(parsed)
        self.assertEqual(reading, "of the great Eloe beginning")
        self.assertNotIn("El\u014dheem", reading)

    def test_initialism_gloss(self):
        self.assertEqual(
            jsp.render_reading(spans("to know God & J. C [Jesus Christ] who he has sent")),
            "to know God & J. C who he has sent",
        )

    def test_illegible_is_a_gloss(self):
        parsed = spans("brot. up this wod [illegible] only to shew")
        self.assertEqual([s.kind for s in parsed if s.kind != "text"], ["gloss"])
        self.assertEqual(
            jsp.render_reading(parsed), "brot. up this wod only to shew"
        )


class TestBlanks(unittest.TestCase):
    def test_bare_blank(self):
        parsed = spans("how far you can be Savior [blank] there is no thing")
        self.assertEqual([s.kind for s in parsed if s.kind != "text"], ["blank"])
        self.assertEqual(
            jsp.render_reading(parsed), "how far you can be Savior there is no thing"
        )

    def test_measured_blanks(self):
        for source in ("[25 lines blank]", "[11 lines blank]", "[1/3 page blank]"):
            with self.subTest(source=source):
                self.assertEqual(kinds(f"amen— {source} [p. 22]")[1], "blank")


class TestInsertions(unittest.TestCase):
    def test_zero_width_spaces_are_stripped_from_the_content(self):
        source = f"the subject which <{ZWSP}in the fore p[ar]t.{ZWSP}> was contemp"
        parsed = spans(source)
        insertion = [s for s in parsed if s.kind == "insertion"][0]
        self.assertEqual(insertion.content, "in the fore p[ar]t.")
        self.assertIn(ZWSP, insertion.raw)

    def test_insertion_is_applied_inline_and_its_expansions_resolved(self):
        source = f"which <{ZWSP}in the fore p[ar]t. of the Con[ference]{ZWSP}> was"
        self.assertEqual(
            jsp.render_reading(spans(source)),
            "which in the fore part. of the Conference was",
        )

    def test_diplomatic_shows_angle_brackets_without_zero_width_spaces(self):
        source = f"gra[ti]fied in <{ZWSP}salvati[o]n{ZWSP}> Exaltation"
        self.assertEqual(
            jsp.render_diplomatic(spans(source)),
            "gra[ti]fied in <salvati[o]n> Exaltation",
        )


class TestCancellations(unittest.TestCase):
    def test_cancelled_word_is_dropped(self):
        parsed = spans("no other prinicple— 1st ~~of~~ object to find")
        self.assertEqual([s.kind for s in parsed if s.kind != "text"], ["cancellation"])
        self.assertEqual(
            jsp.render_reading(parsed), "no other prinicple— 1st object to find"
        )

    def test_cancellation_inside_a_word(self):
        self.assertEqual(
            jsp.render_reading(spans("the character of ~~the~~ God~~s~~, he begin[s]")),
            "the character of God, he begins",
        )

    def test_cancellation_may_contain_markup(self):
        parsed = spans("up this wod ~~[illegible]~~ only to shew")
        cancellation = [s for s in parsed if s.kind == "cancellation"][0]
        self.assertEqual([c.kind for c in cancellation.children], ["gloss"])
        self.assertEqual(jsp.render_reading(parsed), "up this wod only to shew")

    def test_diplomatic_keeps_the_strikethrough(self):
        self.assertEqual(
            jsp.render_diplomatic(spans("1st ~~of~~ object")), "1st ~~of~~ object"
        )


class TestFootnoteAnchors(unittest.TestCase):
    def test_anchor_glued_to_a_word(self):
        parsed = jsp.parse_body("carry the testimony to your hearts1 & pray")
        anchors = [s for s in parsed if s.kind == "footnote_anchor"]
        self.assertEqual([a.number for a in anchors], [1])
        self.assertEqual(jsp.render_reading(parsed),
                         "carry the testimony to your hearts & pray")

    def test_anchor_glued_to_punctuation(self):
        parsed = jsp.parse_body("the instr[uctio]n.1 of Alm[ighty] God")
        self.assertEqual(
            [s.number for s in parsed if s.kind == "footnote_anchor"], [1]
        )

    def test_anchor_glued_to_an_em_dash(self):
        parsed = jsp.parse_body("baptism &c—1 one god")
        self.assertEqual(
            [s.number for s in parsed if s.kind == "footnote_anchor"], [1]
        )

    def test_anchors_run_in_sequence(self):
        parsed = jsp.parse_body("hearts1 and then Spirit—2 and then wisdom3")
        self.assertEqual(
            [s.number for s in parsed if s.kind == "footnote_anchor"], [1, 2, 3]
        )

    def test_scribal_digits_preceded_by_a_space_are_text(self):
        for source in (
            "shew that ninety nine of 100 are false prop[hets]",
            "corespends the nearest to the rev[elatio]ns. of the last 14 y[ea]rs",
            "the 21 v[erse] of 4th. Mat[thew]:",
            "(I wish I had 40 days to talk)",
        ):
            with self.subTest(source=source):
                parsed = jsp.parse_body(source)
                self.assertEqual(
                    [s for s in parsed if s.kind == "footnote_anchor"], []
                )

    def test_glued_digits_that_break_the_sequence_are_text(self):
        # "99/100": the "100" is glued to "/" but footnote 3 is what comes next.
        parsed = jsp.parse_body("to day1 and anothe[r].2 then 99/100 are false then day3")
        self.assertEqual(
            [s.number for s in parsed if s.kind == "footnote_anchor"], [1, 2, 3]
        )
        self.assertIn("99/100", jsp.render_reading(parsed))

    def test_digits_inside_markup_are_not_anchors(self):
        parsed = jsp.parse_body("meet Paul 1/2 way.— [p. [69]] [D&C 130:1, 3, 22]")
        self.assertEqual([s for s in parsed if s.kind == "footnote_anchor"], [])


class TestSpanSlicing(unittest.TestCase):
    def test_a_straddling_text_span_is_clipped(self):
        body = "first clause— second clause— third clause"
        parsed = jsp.parse_body(body)
        cut = body.index("second")
        sliced = jsp.spans_in(parsed, cut, len(body))
        self.assertEqual(jsp.render_reading(sliced), "second clause— third clause")

    def test_slices_of_a_partition_recover_every_word(self):
        body = "one [p. 1] two con[ference] three [blank] four"
        parsed = jsp.parse_body(body)
        cuts = [0, body.index("two"), body.index("three"), len(body)]
        pieces = [
            jsp.render_reading(jsp.spans_in(parsed, a, b))
            for a, b in zip(cuts, cuts[1:])
        ]
        self.assertEqual(" ".join(pieces).split(), jsp.render_reading(parsed).split())

    def test_markup_may_not_straddle_a_slice_boundary(self):
        parsed = jsp.parse_body("a con[ference] b")
        with self.assertRaises(ValueError):
            jsp.spans_in(parsed, 0, 7)


class TestNormalizedRendering(unittest.TestCase):
    def test_lowercased_and_depunctuated(self):
        source = "The Prophet while I address you— & that is the subj[ec]t. of the dead"
        self.assertEqual(
            jsp.render_normalized(spans(source)),
            "the prophet while i address you that is the subject of the dead",
        )

    def test_whitespace_is_collapsed_across_line_breaks(self):
        self.assertEqual(
            jsp.render_normalized(spans("heirs of God.\n\nand ascend   a throne")),
            "heirs of god and ascend a throne",
        )

    def test_soft_hyphen_is_removed(self):
        self.assertEqual(jsp.render_normalized(spans("nineteenth\u00adCentury")),
                         "nineteenthcentury")


class TestDocumentSplitting(unittest.TestCase):
    def test_requires_the_document_transcript_line(self):
        with self.assertRaises(ValueError):
            jsp.split_source("Title\nSomething Else\nbody\n")

    def test_footnote_block_is_separated(self):
        title, body, notes = jsp.split_source(
            "Discourse, 7 April 1844, as Reported by Thomas Bullock\n"
            "Document Transcript\n"
            "body text1\n"
            "Footnotes\n"
            "[1]See James 5:16.\n"
        )
        self.assertEqual(title,
                         "Discourse, 7 April 1844, as Reported by Thomas Bullock")
        self.assertEqual(body, "body text1")
        self.assertIn("[1]See James 5:16.", notes)

    def test_works_cited_blocks_are_kept_out_of_the_note_text(self):
        notes, cited = jsp.parse_footnotes(
            "[1]See Genesis 1:1.\n"
            "Comprehensive Works Cited\n"
            "Gibbs, Josiah W. A Manual Hebrew and English Lexicon.\n"
            "\n"
            "[2]TEXT: Possibly \u201cinspr.\u201d.\n"
        )
        self.assertEqual(notes[1], "See Genesis 1:1.")
        self.assertEqual(
            cited[1], ["Gibbs, Josiah W. A Manual Hebrew and English Lexicon."]
        )
        self.assertEqual(notes[2], "TEXT: Possibly \u201cinspr.\u201d.")
        self.assertEqual(cited[2], [])

    def test_multiline_footnote_is_joined(self):
        notes, _ = jsp.parse_footnotes("[1]first line\nsecond line\n")
        self.assertEqual(notes[1], "first line second line")


class TestRealTranscripts(unittest.TestCase):
    """Checks that must hold for all four transcripts as they stand in the repo."""

    @classmethod
    def setUpClass(cls):
        cls.documents = jsp.load_all(ROOT)

    def test_all_four_are_parsed_with_the_right_siglum(self):
        self.assertEqual(sorted(self.documents), ["B", "C", "R", "W"])
        self.assertEqual(self.documents["B"].reporter, "Thomas Bullock")
        self.assertEqual(self.documents["W"].reporter, "Wilford Woodruff")
        self.assertEqual(self.documents["R"].reporter, "Willard Richards")
        self.assertEqual(self.documents["C"].reporter, "William Clayton")

    def test_spans_reconstruct_the_body_exactly(self):
        for siglum, document in self.documents.items():
            with self.subTest(siglum=siglum):
                self.assertEqual(
                    "".join(span.raw for span in document.spans), document.body
                )

    def test_footnote_anchor_count_equals_footnote_count(self):
        for siglum, document in self.documents.items():
            with self.subTest(siglum=siglum):
                numbers = [span.number for span in document.anchors]
                self.assertEqual(numbers, list(range(1, len(document.footnotes) + 1)))
                self.assertEqual(len(numbers), len(document.footnotes))

    def test_expected_footnote_counts(self):
        self.assertEqual(
            {s: len(d.footnotes) for s, d in self.documents.items()},
            {"B": 87, "W": 3, "R": 5, "C": 11},
        )

    def test_page_sequences(self):
        self.assertEqual(
            self.documents["B"].pages,
            ["14", "15", "16", "17", "18", "19", "20", "21", "22"],
        )
        self.assertEqual(
            self.documents["R"].pages, ["[67]", "[68]", "[69]", "[70]", "[71]"]
        )

    def test_no_gloss_content_leaks_into_any_reading_text(self):
        leaks = {
            "B": ["El\u014dheem or Elohim", "King Follett", "Jesus Christ of Latter-day"],
            "C": ["Sidney Rigdon", "New Testament", "Church of Jesus Christ of"],
        }
        for siglum, phrases in leaks.items():
            reading = jsp.render_reading(self.documents[siglum].spans)
            for phrase in phrases:
                with self.subTest(siglum=siglum, phrase=phrase):
                    self.assertNotIn(phrase, reading)

    def test_body_typography_is_preserved_in_the_diplomatic_rendering(self):
        bullock = jsp.render_diplomatic(self.documents["B"].spans)
        for character in ("\u2014", "\u201c", "\u201d", "\u014d", "\u25ca"):
            with self.subTest(character=repr(character)):
                self.assertTrue(
                    character in bullock,
                    f"U+{ord(character):04X} missing from the Bullock body",
                )

    def test_footnote_typography_is_preserved(self):
        document = self.documents["B"]
        notes = " ".join(document.footnotes.values())
        notes += " ".join(
            line for lines in document.works_cited.values() for line in lines
        )
        for character in ("\u2013", "\u2019", "\u00ad", "\u201c", "\u201d"):
            with self.subTest(character=repr(character)):
                self.assertTrue(
                    character in notes,
                    f"U+{ord(character):04X} missing from the Bullock footnotes",
                )

    def test_reading_text_is_shorter_than_raw_but_close(self):
        for siglum, document in self.documents.items():
            with self.subTest(siglum=siglum):
                raw = len(document.body.split())
                reading = jsp.word_count(document.spans)
                self.assertLess(reading, raw)
                self.assertGreater(reading, raw * 0.9)


if __name__ == "__main__":
    unittest.main()
