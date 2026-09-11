# King Follett Discourse — digital critical edition

On 7 April 1844, during the Church of Jesus Christ of Latter-day Saints' April
general conference, Joseph Smith preached a funeral sermon for King Follett in a
grove east of the partly built Nauvoo temple. No authorial text of the discourse
exists. What survives is four independent eyewitness reports, and they differ
from one another at points that carry real doctrinal weight.

This repository reconstructs the discourse from those four reports. The data
layer is the edition: the transcripts as the Joseph Smith Papers publishes them,
an explicit thematic alignment of all four witnesses, the editorial footnotes
with their anchor positions, and a critical apparatus of the variants. The
website under `docs/` is a first pass over an earlier and much weaker version of
that data and is being superseded (see *Status*).

## Sigla

| Siglum | Reporter | Role on 7 April 1844 | Reading words |
| --- | --- | --- | --- |
| **B** | Thomas Bullock | Conference reporter and clerk; took the discourse down as Joseph Smith spoke. Base text. | 4,074 |
| **W** | Wilford Woodruff | Personal journal; not assigned to report, wrote up his account from notes taken during the sermon. | 2,406 |
| **R** | Willard Richards | Joseph Smith's private secretary and historian; recorded as Smith spoke, very telegraphically. | 1,072 |
| **C** | William Clayton | Joseph Smith's private clerk; recorded as Smith spoke, breaking off before the close. | 2,907 |

Bullock is the base text because it is the fullest witness and the only one that
covers all thirty-five sections. A fifth text, the *Times and Seasons* account of
15 August 1844, is a later amalgamation of Bullock's and Clayton's notes rather
than an independent witness; it is not collated here, though JSP's footnotes cite
it constantly.

## Data model

**`transcripts/*.md`** — the four reports, pasted verbatim from the Joseph Smith
Papers website and never edited. Line 1 is the JSP title, line 2 is
`Document Transcript`, then the body, then a line `Footnotes` followed by
`[N]text` lines. This content is authoritative: everything else in the
repository is derived from it and must be rebuilt rather than hand-corrected.

**`data/sections.json`** — the alignment. Thirty-five thematic sections `S01`–`S35`,
each with a label, a summary, and an entry per witness. A witness entry either
records that the witness has no material for the section, with a note saying so,
or gives `char_start`, `char_end`, the verbatim body slice those offsets
produce, the manuscript pages the slice touches, and a reading-text word count.
For each witness the sections **partition the entire body**: in order, no
overlap, no gap, every character in exactly one section. That property is what
makes the file safe to build on, and `validate` proves it on every run. Where a
passage did not obviously belong to one section, the decision and its reasoning
are recorded in the section's `boundary_notes`.

**`data/witnesses.json`** — one record per witness: reporter, role that day with
the JSP source it was verified against, transcript path, JSP URL, raw and
reading word counts, footnote count, manuscript page range, and which sections
the witness omits.

**`data/footnotes.json`** — JSP's editorial footnotes, keyed by witness and
number. Each carries the note text, the character offset of its anchor in the
body, the section that offset falls in, and a `kind`: `textual` for JSP's
alternate-reading notes (those beginning `TEXT:`), `times_and_seasons` for notes
citing the 1844 amalgamation, `scripture` for cross-references, `other` for
historical and bibliographical annotation. The kinds are tested in that order,
so a `TEXT:` note that also mentions the *Times and Seasons* is `textual`.

**`data/apparatus.json`** — the critical apparatus: thirty-four variants
`V001`–`V034` where the witnesses differ in doctrinal claim, historical detail or
rhetorical force. Each names its section and keeps its lemma, per-witness
readings, type, flag and note. The verification notes an earlier pass made
against manuscript scans now sit in `legacy_verification`, marked superseded;
they are history, not evidence. Every variant carries `status:
"carried_forward"` and an empty `sources` list, both to be filled in when the
apparatus is revised.

**`src/kf/`** — the code, Python 3.11 or later, standard library only.
`jsp.py` parses the JSP transcript conventions and renders the body three ways;
`segments.py` reads `sections.json` and slices the transcripts by it;
`validate.py` checks every invariant the data claims. `history/` holds the
January 2026 artifacts these files replace.

## Editorial conventions as parsed

`src/kf/jsp.py` types every piece of a transcript body as one of `text`,
`expansion`, `gloss`, `insertion`, `cancellation`, `page_break`,
`footnote_anchor` or `blank`. Concatenating the spans reproduces the source
character for character.

| Source | Type | In the reading text |
| --- | --- | --- |
| `[p. 14]`, `[p. [133]]` | `page_break` — the preceding text stands on that page | removed |
| `con[ference]`, `subj[ec]t`, `[k]now` | `expansion` — bracket glued to the word | applied silently |
| `noes [knows]`, `evelastig [everlasting]` | `expansion` — spaced bracket respelling the word before it | replaces the scribal form |
| `Follit [King Follett]`, `Eloe [Elōheem or Elohim]`, `[illegible]` | `gloss` — editorial identification | **dropped**; the scribe's word is kept |
| `[blank]`, `[25 lines blank]` | `blank` — notation of blank manuscript space | removed |
| `<​text​>` (with U+200B inside the angle brackets) | `insertion` — scribal interlinear insertion | applied inline |
| `~~text~~` | `cancellation` — scribal cancellation | dropped |
| `hearts2`, `Spirit—46` | `footnote_anchor` | removed |

Distinguishing an expansion from a gloss is the point of the exercise. The
superseded `data/align.py` stripped brackets but kept their contents, so its
reading text said "the great Eloe Elōheem or Elohim" — editorial matter passing
as Joseph Smith's words. Glosses are now dropped outright.

Footnote anchors are bare digits glued to the end of a word or a mark of
punctuation, and some digits in these texts are genuine content: "ninety nine of
100", "the last 14 y[ea]rs", "99/100", "meet Paul 1/2 way". A digit run counts as
an anchor only when it is glued to what precedes it *and* equals the next
expected footnote number, so anchors run 1..N in order of appearance. The anchor
count equals the footnote count in all four transcripts: 87 for Bullock, 3 for
Woodruff, 5 for Richards, 11 for Clayton.

The three renderings:

- `render_diplomatic` reproduces the JSP presentation — brackets, page markers,
  strikethroughs and line breaks as they stand, insertions as `<text>` with the
  zero-width spaces removed, and footnote anchors as `[n]` so they cannot be
  mistaken for scribal digits.
- `render_reading` gives clean reading text: expansions applied, glosses
  dropped, insertions inline, cancellations, page markers, blank notations and
  anchors removed, whitespace collapsed. Spelling, capitalisation and
  punctuation are left exactly as the scribe has them.
- `render_normalized` lowercases the reading text, strips punctuation and
  collapses whitespace, for machine comparison only.

Source typography is preserved throughout: em and en dashes, curly quotes, the
`ō` of "Elōheem", the soft hyphen in a footnote, the lozenge Bullock uses for an
illegible character. Nothing is ASCII-folded.

One gap is worth naming. JSP renders scribal cancellations struck through, but
the pastes in `transcripts/` did not preserve that formatting, so cancelled words
stand in them as ordinary text and are read as such. The parser handles `~~text~~`
so that a future re-paste keeping the strikethrough will be read correctly; until
then a handful of cancelled readings are silently part of the reading text.

## Running it

From the repository root, no installation and no dependencies:

```
python3 -m kf validate                # check every data invariant
python3 -m kf stats                   # per-witness, per-section word counts
python3 -m kf section S08             # one section across all four witnesses
python3 -m kf section S08 --render reading
python3 -m unittest discover tests    # parser tests
```

`python3 -m kf export-segments` writes one text file per section per witness
into `data/segments/`, which is generated and gitignored.

The package lives in `src/kf/`; the root `kf` symlink is what lets `python3 -m kf`
work from the repository root without installing anything.

`validate` checks that the spans reconstruct each body exactly; that footnote
anchors are sequential and match the footnote count; that every section's `text`
equals its own slice of the body; that the sections are ordered, non-overlapping
and partition the whole body with no gaps; that no boundary falls inside markup
or inside a word; that the per-section word counts total to the whole
transcript's; that page ranges are right; and that `witnesses.json`,
`footnotes.json` and `apparatus.json` agree with the transcripts and with
`sections.json`.

## Status

The web edition at `docs/index.html` is the January 2026 first pass. It was
built from `history/alignment_map.legacy.json` and
`history/collation_map.legacy.json`, whose alignment pointers were unreliable,
and it is being superseded. It is left in place and untouched for now because it
is the live GitHub Pages site; the static build will be regenerated from `data/`
in a later phase.

Revising the apparatus — reassessing the thirty-four variants, adding what the
collation missed, and citing sources for each — is the next phase and was
deliberately not attempted in this one. The apparatus as it stands is the
earlier collation carried forward unchanged.
