# Principal's audit, 15 September 2026

Two questions were left open after Phase 2e and the second pass over its
rejections: whether the ten candidates that second pass wanted included should
be included, and whether the ninety-three it *accepted* as already-recorded were
really recorded. Both are adjudication — settling another lane's flags — so both
were done here rather than dispatched. Every reading added was checked as a
verbatim substring of its witness's section reading text before it was written,
and `python3 -m kf validate` and the test suite pass.

The apparatus goes **122 → 131**.

## Part 1 — the ten disagreements in `REJECTIONS.md`

Seven upheld, three rejected. Judged against the type definitions in
`apparatus.json` metadata rather than against the second pass's own framing;
that is what moves three of them.

| Candidate | Second pass | This audit | Reason |
| --- | --- | --- | --- |
| S07.3 | omission | **reject** | `omission` requires the gap be "more than a scribe's compression". Woodruff has 39 words in S07 against Bullock's 150 and Richards 16; both are compressing hard throughout the section, so the missing persecution-will-cease clause is not evidence of anything but brevity. |
| S13.2 | omission | **reject** | Woodruff records the same sentence without "with fear & trembling", so this is not compression — but the phrase's absence does not change what is claimed, and the doctrinal content (the Father worked out a kingdom) is identical in all four. Worth noting that the phrase itself appears nowhere in the apparatus: all witnesses that have it agree, and the apparatus records differences. |
| S14.2 | theological | **reject** | The second pass says B/R/C deny completion "without dating the remainder to a long postmortem interval". They do date it: Bullock has "it is a great thing to learn Salvation. beyond the grave" and Clayton "will be a great while before you learn the last". Woodruff combines the two elements; the difference is arrangement, not doctrine. |
| S17.2 | historical | **V123** | Bullock alone dates the revelatory career at fourteen years; Clayton has the correspondence with no span; T prints Bullock's figure. |
| S22.4 | theological | **V124** | The claimed source of the teaching differs — Holy Spirit, revelations of Jesus Christ, or unnamed — and T drops the attribution. |
| S24.1 | theological | **V125** | The scope of who must obey, and what they must obey, both differ; T takes Clayton's narrower scope. |
| S26.6 | theological | **V126** | Woodruff makes receiving the Holy Ghost a prerequisite where the others set a mortal-life boundary. Two different kinds of limit. |
| S32.1 | historical | **V127** | Woodruff includes children among the speaker's dead; Bullock and T do not. A biographical detail in a funeral sermon. |
| S34.1 | reception | **V128** | T prints both that water alone "is of no use" and that the three "are necessary". Woodruff has the first, but Woodruff was not used in the composite, so the strengthening does not come from T's sources. |
| S34.2 | theological | **V129** | Richards grounds the baptismal authority in keys, Bullock in power. Keys name a conferred office where power need not. |

## Part 2 — the ninety-three matches

The merge table's ninety-three "matched" rows share a second boilerplate
template, so they had the same auditability problem as the rejections. The
failure mode they risk is worse and quieter: a candidate matched to an entry
about something *else* at the same locus disappears, because the table records
it as already covered.

This was checked mechanically first rather than re-read by hand. For each pair,
every reading in the candidate's collation line was compared against every
reading in the matched entry, normalised through `jsp.render_normalized`, and
the best overlap kept. A first attempt compared lemmas alone and produced seven
apparent zero-overlap pairs, all false: an entry may quote its lemma from a
witness other than Bullock, so lemma-to-lemma comparison is not a test of
whether two records describe the same place. Comparing whole collation lines
against whole entries gives the real distribution:

| best-reading overlap | pairs |
| --- | ---: |
| ≥ 0.60 | 87 |
| 0.34 – 0.60 | 3 |
| < 0.34 | 3 |

Eighty-seven need no examination. The six that do:

| Pair | Finding |
| --- | --- |
| S29.3 → V091 | **Miss — added as V130.** V091 records Clayton's mechanism for apostasy ("the spirit leaves them"). The candidate is a different point a clause later: Woodruff's "you cannot save them" against Clayton's "cant renew them to repentance", with T following Clayton. |
| S11.2 → V007 | **Miss — added as V131.** V007 records "be a God yourself" against "make yourselves Gods". The candidate is the neighbouring "same as all have done" against "as all Gods has done" — whether the pattern followed is that of other men or of a succession of Gods, which T prints in the plural. |
| S21.2 → V073 | Reject. V073 is the ring image and the candidate is the beginning-implies-end syllogism, so the match is indeed loose — but all four witnesses state that syllogism, and the only variation is Clayton's "spirit" for the others' "man", which tracks his framing throughout and is already the subject of V018. |
| S22.1 → V019 | **Mislabelled, substance covered.** Clayton's "because he was greater" is recorded — at **V074**, not the V019 the table names. No entry needed; the pointer is wrong. |
| S26.2 → V023 | Covered. The escape-and-duration cluster is carried between V023 and V087. |
| S30.4 → V093 | Reject. Bullock's savior criterion and Richards's works maxim are two separate one-witness statements, not two readings of one locus; recording them would mean two `unique` entries, which is a larger claim than the candidate makes. |

## Totals after this audit

131 entries: 46 theological, 29 reception, 26 unique, 12 rhetorical, 9
historical, 7 scribal, 2 omission. 97 new, 34 revised, none withdrawn.

Nine entries were added here (V123–V131). All are `status: "new"`, and each
records its provenance in `sources`: which pass proposed it, where it was
recorded as rejected or matched, and that it was added on this audit.

## Still open for a human editor

- The merge table's reason strings remain boilerplate for both the rejections
  and the matches. `REJECTIONS.md` and this file supply real reasons for the
  forty-two rejections and for the six matches worth examining; the other
  eighty-seven matches were cleared by measurement, not by reading.
- No section boundary has moved. Two independent passes flagged the same six
  cuts and both declined to move any. That is still deferred, not settled.
- `ADJUDICATION.md` §"Human-editor review" flags V018 and V038, which this
  audit did not revisit.
