# King Follett Discourse — digital critical edition

On 7 April 1844, during the Church of Jesus Christ of Latter-day Saints' April
general conference, Joseph Smith preached a funeral sermon for King Follett in a
grove east of the partly built Nauvoo temple. No authorial text of the discourse
exists. What survives is four independent eyewitness reports, and they differ
from one another at points that carry real doctrinal weight.

This repository reconstructs the discourse from those four reports. The data
layer is the edition: the transcripts as the Joseph Smith Papers publishes them,
an explicit thematic alignment of every witness, the editorial footnotes with
their anchor positions, and a critical apparatus of the variants. The website
under `docs/` is a first pass over an earlier and much weaker version of that
data and is being superseded (see *Status*).

## Sigla

| Siglum | Witness | Kind | Role on 7 April 1844 | Reading words |
| --- | --- | --- | --- | --- |
| **B** | Thomas Bullock | eyewitness | Conference reporter and clerk; took the discourse down as Joseph Smith spoke. Base text. | 4,036 |
| **W** | Wilford Woodruff | eyewitness | Personal journal; not assigned to report, wrote up his account from notes taken during the sermon. | 2,403 |
| **R** | Willard Richards | eyewitness | Joseph Smith's private secretary and historian; recorded as Smith spoke, very telegraphically. | 1,066 |
| **C** | William Clayton | eyewitness | Joseph Smith's private clerk; recorded as Smith spoke, breaking off before the close. | 2,896 |
| **T** | *Times and Seasons* 5:15 | **derived** | Not a report. The composite Bullock and Clayton assembled from their own notes, printed 15 August 1844, pp. 612–617. | 4,949 |

Bullock is the base text because he is the fullest witness and one of only two
that cover all thirty-five sections.

**T is a derived witness and is labelled so everywhere** — in
`data/witnesses.json`, in `data/sections.json`, and in every line the CLI
prints. It is included because it is the text almost every published quotation
of the discourse actually descends from, so readers can see how the received
text was built: where it smooths a rough report, where it fuses two witnesses
into one sentence, and where it supplies wording no witness has. What T must
never be treated as is a fifth independent report. Its agreement with B or C is
not corroboration; it *is* B and C, edited. Every apparatus entry still records
a T reading so the received text can be seen being made; those readings are
typed `reception` when T itself is the thing to record.

## Data model

**`transcripts/*.md`** — the five transcripts, pasted verbatim from the Joseph
Smith Papers website and never edited. Line 1 is the JSP title, line 2 is
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

T is aligned on the same terms, with two additions. T reorders and merges
material, so where one T passage carries two sections' material it is assigned
to the section carrying most of it and the merge is described in
`boundary_notes`. Where T has material with no eyewitness counterpart — the
conference-minutes framing that opens it, the editorial parenthesis identifying
King Follett — the section is flagged `"t_only": true`.

**`data/witnesses.json`** — one record per witness: siglum, name, `kind`
(`eyewitness` or `derived`), the physical document, the reporter's role that day
with the JSP source it was verified against, the JSP citation string, JSP URL,
transcript path, raw and reading word counts, cancellation and underline span
counts, footnote count, manuscript page range, and which sections the witness
omits. T additionally records its compilers and its publication data.

**`data/footnotes.json`** — JSP's editorial footnotes, keyed by witness and
number. Each carries the note text, the character offset of its anchor in the
body, the section that offset falls in, and a `kind`: `textual` for JSP's
alternate-reading notes (those beginning `TEXT:`), `times_and_seasons` for notes
citing the 1844 amalgamation, `scripture` for cross-references, `other` for
historical and bibliographical annotation. The kinds are tested in that order,
so a `TEXT:` note that also mentions the *Times and Seasons* is `textual`.

**`data/apparatus.json`** — the critical apparatus: 131 variants `V001`–`V131`
where the witnesses differ in doctrinal claim, historical detail, rhetorical
force, scribal cancellation, or T's reception of the notes. Each names its
section and keeps lemma, per-witness readings (B W R C **and** T), type, and
a hedged `significance`. T is labelled derived; its agreement with B or C is
not corroboration. Readings for the four eyewitnesses are verbatim substrings
of the reading text (or `om.`). January 2026 scan notes sit in
`legacy_verification` where present — history, not evidence. See
`data/APPARATUS-REPORT.md` and `HANDOFF.md` for what still needs adjudication.

**`src/kf/`** — the code, Python 3.11 or later, standard library only.
`jsp.py` parses the JSP transcript conventions and renders the body three ways;
`segments.py` reads `sections.json` and slices the transcripts by it;
`validate.py` checks every invariant the data claims. `history/` holds the
January 2026 artifacts these files replace.

**`tools/restore_jsp_markup.py`** — restores the two scribal markers onto the
transcripts from the saved JSP page JSON in `refs/`. See *Cancellations and
underlines* below for why this exists.

## Editorial conventions as parsed

`src/kf/jsp.py` types every piece of a transcript body as one of `text`,
`expansion`, `gloss`, `insertion`, `cancellation`, `underline`, `page_break`,
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
| `~~text~~` | `cancellation` — scribal cancellation | **dropped**; cancelled words are not part of the reading text |
| `__text__` | `underline` — scribal underline | marks dropped, words kept |
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
count equals the footnote count in all four eyewitness transcripts: 87 for
Bullock, 3 for Woodruff, 5 for Richards, 11 for Clayton. JSP supplies no
footnotes for the printed T text, so T must yield no anchors at all.

The three renderings:

- `render_diplomatic` reproduces the JSP presentation — brackets, page markers,
  `~~` strikethroughs, `__` underlines and line breaks as they stand, insertions
  as `<text>` with the zero-width spaces removed, and footnote anchors as `[n]`
  so they cannot be mistaken for scribal digits.
- `render_reading` gives clean reading text: expansions applied, glosses
  dropped, insertions inline, underline marks dropped but their words kept,
  cancellations, page markers, blank notations and anchors removed, whitespace
  collapsed. Spelling, capitalisation and punctuation are left exactly as the
  scribe has them.
- `render_normalized` lowercases the reading text, strips punctuation and
  collapses whitespace, for machine comparison only.

Source typography is preserved throughout: em and en dashes, curly quotes, the
`ō` of "Elōheem", the soft hyphen in a footnote, the lozenge Bullock uses for an
illegible character. Nothing is ASCII-folded.

### Cancellations and underlines

JSP renders scribal cancellations struck through and scribal underlines
underlined, but a plain copy-and-paste of a JSP transcript page keeps neither.
That failure is quiet and costly: once the formatting is gone, a word the scribe
struck out is indistinguishable from a word he let stand, so cancelled readings
become part of the reading text and the manuscript's record of the scribe
changing his mind is lost. Bullock's "as the father ~~hath~~ had power" would
read as "hath had power"; Clayton's cancelled "~~eternal sin~~" would read as
though he wrote both "eternal sin" and "unpardonable sin".

The transcripts here carry both markers. The counts are fixed, and come from
`refs/jsp-markup-audit.md`, where they were taken from the `deleted` and
`underscore` spans of the live JSP pages:

| | B | W | R | C | T |
| --- | ---: | ---: | ---: | ---: | ---: |
| cancellations | 16 | 3 | 7 | 10 | 0 |
| underlines | 5 | 25 | 0 | 6 | 0 |

Both `validate` and the test suite assert these numbers, so a re-paste that
flattens the markup fails loudly instead of silently degrading the edition.
`tools/restore_jsp_markup.py` puts the markers back from the saved JSP page
JSON: it maps them onto the existing transcript rather than regenerating it, so
every original character and whitespace choice survives, and it refuses to write
unless removing the markers again reproduces its input byte for byte and the
counts above come out exactly. It needs `refs/jsp-json/`, which is local
reference material and gitignored.

## Running it

From the repository root, no installation and no dependencies:

```
python3 -m kf validate                # check every data invariant
python3 -m kf stats                   # per-witness, per-section word counts
python3 -m kf section S08             # one section across all five witnesses
python3 -m kf section S08 --render reading
python3 -m kf apparatus S20          # one section in classical form
python3 -m unittest discover tests    # parser tests
```

`python3 -m kf export-segments` writes one text file per section per witness
into `data/segments/`, which is generated and gitignored.

The package lives in `src/kf/`; the root `kf` symlink is what lets `python3 -m kf`
work from the repository root without installing anything.

`validate` checks that the spans reconstruct each body exactly; that the
cancellation and underline span counts match the JSP audit; that footnote
anchors are sequential and match the footnote count; that every section's `text`
equals its own slice of the body; that the sections are ordered, non-overlapping
and partition the whole body with no gaps; that no boundary falls inside markup
or inside a word; that the per-section word counts total to the whole
transcript's; that page ranges are right; and that `witnesses.json`,
`footnotes.json` and `apparatus.json` agree with the transcripts and with
`sections.json`.

## The site

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py            # write site/
.venv/bin/python build.py --serve    # write site/, then serve it
```

`build.py` generates the whole edition into `site/`, which is gitignored: the
data is the source, the site is output, and nothing is ever hand-edited there.
`docs/` is the January 2026 site and is not touched by the build; it stays until
the move to `kingfollett.noahairmet.com` replaces it with a redirect stub.

Every number on the site comes from `data/`. Prose in `content/` refers to
counts as `{{stats.total_variants}}` or `{{stats.words.B}}` and `build.py`
fills them in, so commentary cannot drift from the edition it describes; an
unknown placeholder fails the build rather than printing into a page. The
reading text on the page is rendered *from the string* `jsp.render_reading`
produces, not from a second implementation of the same rules, so what a reader
sees is what `validate` checks the apparatus readings against.

The edition has one reading surface. The thirty-five-section partition is the
only structure the data guarantees, so it is the site's spine; the witness
pages, the apparatus ledger and the reception view are entrances into it rather
than separate copies of the text. The reader's configuration is three things —
which witnesses are lit, whether variants are marked, and whether the text is
shown as the scribe left it or as it reads — and each is a checkbox the
stylesheet reads with `:has()`. The edition is therefore fully operable with
scripting disabled. `web/edition.js` adds the configuration to the URL so a
link carries what the sender was looking at, opens the apparatus slip, tells
the rail where you are, binds `1`–`5`/`v`/`m`/`j`/`k`, and attaches the siglum,
section and manuscript page to anything copied out of a witness column.

The rail down the left is five ribbons, one per witness, each swelling with
that witness's word count in each section. It is nowhere labelled, because the
shape is the claim: Clayton's ribbon stops at S31, Woodruff's at S35,
Richards's is thin the whole way, and T's — the one text nobody heard — is the
widest on the page.

`markdown` is the only dependency and it is used at build time to render
`content/`; nothing ships to the browser, and `src/kf` remains standard library
only.

## Status

The edition is live at **<https://kingfollett.noahairmet.com>** (Cloudflare
Pages project `king-follett`; `~/.agent-bus/cloudflare-recipes.md` has the
deploy recipe). Deploys are explicit — `build.py`, then
`wrangler pages deploy site --project-name king-follett` — and are not tied to
a git push.

`docs/index.html` was the January 2026 first pass, built from
`history/alignment_map.legacy.json` and `history/collation_map.legacy.json`,
whose alignment pointers were unreliable. It is now a redirect stub: GitHub
Pages cannot issue a 301, so the page carries a canonical link, a meta refresh
and a script redirect, and says plainly that the old edition's
manuscript-verification claim has been withdrawn.

**Data layer (Phases 1–2e, September 2026).** Transcripts, alignment, footnotes
and the `src/kf` parser are in place and validated. The apparatus in
`data/apparatus.json` is a systematic collation of **131 entries**, built by two
independent passes, adjudicated, and then audited: 46 theological, 29 reception,
26 unique, 12 rhetorical, 9 historical, 7 scribal, 2 omission. Statuses are 97
new and 34 revised; none are withdrawn. See `data/APPARATUS-REPORT.md`,
`data/ADJUDICATION.md`, `data/REJECTIONS.md` (an independent second pass over
the forty-two rejected candidates) and `data/AUDIT.md` (the principal's review
of that second pass and of the ninety-three accepted matches). JSP transcriptions are accepted as authoritative;
January 2026 scan notes survive only as `legacy_verification` and are not
evidence for this edition.

**Site (Phase 3, September 2026).** `build.py` generates the edition from
`data/` into `site/`; see *The site* above.

**Migrated (Phase 4, September 2026).** Cloudflare Pages, custom domain, and
the GitHub Pages redirect stub are in place.

**Not yet done.** Commentary files under `content/` do not exist (Phase 2d), so
the About and Reception pages carry an explicit note in place of prose rather
than filler. Read `HANDOFF.md` before continuing.
