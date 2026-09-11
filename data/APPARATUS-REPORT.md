# Apparatus report — Phase 2b

September 2026. This report accompanies `data/apparatus.json`, which replaces the
thirty-four hand-picked variants of January 2026 with a systematic collation built
section by section against the Phase 1 reading text.

## What changed and why

The inherited apparatus had two problems. It had no stated criteria, so there was no
way to tell what it had passed over; and its readings were paraphrases. Of its
119 eyewitness readings, **thirty-five could not be found in the transcripts at all** — normalised spelling, silently joined clauses, ellipses inside quotation marks,
and in several places text taken from the wrong locus. Every reading in the new file is
a verbatim substring of that witness's reading-rendered section text, and
`python3 -m kf validate` now proves it on every run. The check bites: corrupting a
single reading or a single cancellation makes validation fail by id and siglum.

Every entry now also carries a T reading. T remains labelled derived everywhere and is
not a collation witness; it is recorded so a reader can see which eyewitness the
received text followed at each point, and where it followed none.

## Totals

**106 entries.** 34 revised (the original ids, all kept), 72 new (V035–V106). None
withdrawn.

| Type | Count |
| --- | ---: |
| theological | 40 |
| unique | 26 |
| reception | 12 |
| rhetorical | 12 |
| scribal | 7 |
| historical | 7 |
| omission | 2 |

Numbering: new ids were issued in the order the entries were written, so V035–V106 are
not in discourse order. Ordering is by `section` then `order`, which is what the file
and the CLI use; the ids are stable handles, not positions.

## Per-section counts

| Section | Entries | Types | Label |
| --- | ---: | --- | --- |
| S01 | 4 | historical 1, theological 1, unique 2 | Introduction: Occasion and Subject |
| S02 | 0 | — | Preliminary: Paving the Way |
| S03 | 2 | historical 1, theological 1 | Need to Understand God from the Beginning |
| S04 | 1 | theological 1 | The World Knows Little of God |
| S05 | 1 | unique 1 | What Kind of Being Is God? |
| S06 | 1 | theological 1 | Challenge: If I Show God's Character |
| S07 | 3 | historical 1, theological 2 | Right of Conscience / False Prophets |
| S08 | 3 | theological 2, unique 1 | God Is a Man in Form |
| S09 | 4 | theological 3, unique 1 | God Was Once a Man / Refuting Eternal Godhood |
| S10 | 3 | rhetorical 1, scribal 1, unique 1 | Christ's Power from the Father |
| S11 | 4 | scribal 1, theological 3 | Becoming Gods: Exaltation by Degrees |
| S12 | 2 | theological 2 | Consolation for Mourners: Heirs of God |
| S13 | 3 | historical 1, reception 1, theological 1 | Christ Followed the Father's Pattern |
| S14 | 2 | rhetorical 2 | First Principles / Not All Comprehended in This World |
| S15 | 5 | reception 2, scribal 1, theological 2 | Hebrew Exegesis: Bereshit / Genesis 1:1 |
| S16 | 1 | theological 1 | Grand Council of the Gods |
| S17 | 6 | rhetorical 3, scribal 1, theological 1, unique 1 | The Polyglot Bible: Jacob vs. James |
| S18 | 4 | scribal 1, theological 2, unique 1 | Creation Ex Nihilo Refuted |
| S19 | 3 | rhetorical 1, theological 1, unique 1 | The Soul / Mind of Man: Pre-existence |
| S20 | 3 | reception 1, theological 1, unique 1 | Mind of Man Coequal with God / Mourners' Comfort |
| S21 | 2 | rhetorical 1, theological 1 | Intelligence Is Self-Existent: The Ring Analogy |
| S22 | 3 | rhetorical 1, theological 2 | God Instituted Laws for Lesser Intelligences |
| S23 | 3 | theological 1, unique 2 | Revelations Save Spirit and Body |
| S24 | 4 | omission 1, reception 1, unique 2 | Awful Responsibility for Our Dead |
| S25 | 4 | scribal 1, theological 3 | All Sins Forgiven Except One |
| S26 | 5 | omission 1, scribal 1, theological 2, unique 1 | Cannot Commit Unpardonable Sin After Death / Knowledge Saves |
| S27 | 3 | historical 1, theological 1, unique 1 | The Devil's Plan vs. Christ's Plan |
| S28 | 1 | rhetorical 1 | The Unpardonable Sin Defined |
| S29 | 3 | reception 1, theological 1, unique 1 | Apostates of the Church |
| S30 | 4 | rhetorical 1, unique 3 | Warning: Be Careful |
| S31 | 5 | historical 1, reception 2, theological 1, unique 1 | Many Mansions / Degrees of Glory |
| S32 | 2 | unique 2 | Friends Gone for a Moment / Eternity |
| S33 | 4 | reception 2, theological 1, unique 1 | Mothers Shall Have Their Children |
| S34 | 5 | historical 1, reception 1, theological 2, unique 1 | Baptism: Water, Fire, and Holy Ghost |
| S35 | 3 | reception 1, rhetorical 1, unique 1 | Closing: Personal Testimony / 'You Don't Know Me' |

**S02 is the only section with no entry.** Bullock, Woodruff and Clayton all report the
same preliminary — pave the way, few preliminaries, not oratory but simple truths from
heaven — and Richards omits the section. The differences are synonym-level and word
order. That is a real result, not an oversight: the one passage in the discourse where
the three full reports substantially agree is the one where Joseph Smith is describing
his method rather than making a claim.

## Withdrawn entries

**None.** Every one of the thirty-four inherited entries survives the criteria, though
several survive on different grounds than the January 2026 note gave:

- **V009** was justified on "a kingdom" against "his Kingdom", which is below the
  threshold. It is kept on the ground that Bullock places the Father's probation
  *before* worlds came into existence and Clayton *when* they did.
- **V011** was justified on the ladder being absent in W and R. Both do have a
  counterpart at that point, about duration rather than sequence; the entry is kept
  because the ladder image itself is Bullock's alone.
- **V022** conflated two loci, the self-condemnation language and Woodruff's denial that
  hell fire exists. It is kept for the first and the second is now V085.
- **V021**'s note claimed Woodruff, Richards and Clayton read "saviors on mount Zion".
  None of them does, and Smith does not use the phrase anywhere. The entry is kept on
  Bullock's use of "Savior" as a title.
- **V029**'s note gave Clayton a reading. Clayton's S33 is a clerk's summary
  ("He continued his discourse— & told of parents receiving their children"), not a
  report of words; he is now "om." there.

**V018 is the weakest survivor** and is listed among the unsure calls below.

## JSP textual footnotes

All nine `TEXT:` notes are handled. Seven became or joined a substantive entry; two are
attached to an entry without being the reason for it.

| Note | Passage | Handling |
| --- | --- | --- |
| B n. 1 | "the instruction. of Almighty God", possibly "inspr." | **V036** (S01, theological). Clayton reads "inspiration"; T prints Bullock's "instruction" *and* Clayton's gift of the Holy Ghost. |
| B n. 11 | "not as a senr.", possibly "servt.", allusion wants "scribe" | **V045** (S07, historical). Bullock alone has the Matthew 7:29 contrast; Smith adds that "senr" may abbreviate *senator*. Bullock dropped it from T himself. |
| B n. 14 | "communed.", possibly "Comd." | **V047** (S08, theological). Attached: the entry exists for Clayton's "received instruction" against Bullock's "communed", which is the same word the note questions. |
| B n. 34 | "the H[ead]", possibly "K" | **V057** (S15, theological). Attached. The entry exists for Clayton's "the head God brought forth the head God". |
| B n. 39 | "where it gives the test.", possibly "test[imony]" | **Attached to no entry as its own cause.** All four reports cite Matthew 4:21 identically; the uncertainty is in one abbreviation and changes nothing. Recorded here rather than manufactured into a variant. |
| B n. 40 | "this wod", possibly "wo[r]d" or "wo[ul]d" | **V063** (S17, rhetorical). The entry is Bullock's "to shew that I am right" against Clayton's "to back up the word rosh"; T prints both. |
| B n. 85 | "I rejoice in hearing", possibly "bearing" | **V105** (S35, reception). T prints "bearing" *and* pluralises "my aged friend" to "friends". |
| R n. 2 | "god is gra[ti]fied", possibly "g[lo]rified" | **V010** (S13, theological). Attached; "glorified" would move Richards's reading toward Clayton's "exalt his glory". |
| C n. 2 | "no the end", possibly "nor" | **V040** (S04, theological). Attached; the alternative changes nothing, and the entry exists for the four different objects of human ignorance. |

## Smith-flagged passages

Section 3 of `refs/smith-textual-history-notes.md` lists twelve passages the old list
missed. Every Smith page cite used in `apparatus.json` was checked against
`refs/smith-king-follett-sermon-biography.txt`; page index in that pdftotext output
equals the printed page number exactly, which made verification straightforward.

| # | Smith's flag | Handling |
| --- | --- | --- |
| 1 | "Beloved Saints:" inserted in *The Voice of Truth* | **Not recorded.** Confirmed at Smith p. 287 n. 2, but VOT is downstream of T; this edition's reception scope stops at the 1844 composite. Noted here instead. |
| 2 | Divine name *Eloi* / *Elohim* | **V038** (S03, historical). The extracted note attributes *Eloi* to Richards. Smith p. 288 n. 9 in fact attributes it to **Bullock** — "TB has Eloi or Eloe. WW has Eloheem, WC has Elohem" — and Richards has no S03 material at all. Recorded with Bullock as the *Eloe* witness. |
| 3 | Lorenzo Dow child-rearing proverb in Clayton | **V039** (S03, theological). The extracted note quotes "if a man starts wrong in bringing up his child it is a hard matter to get it right" as Clayton's text. It is not: that is Smith's gloss of Dow's original (p. 59, p. 102 n. 85). Clayton, Bullock and Woodruff all have the start-right saying; the recordable variant is Woodruff's weaker modal, "you may go wrong" for "hard matter to get right". |
| 4 | Richards's reflexive principle of knowing God | **V040** (S04, theological). Confirmed at Smith p. 288 n. 11 and p. 93 n. 6. The extracted note says it is omitted from Clayton; Clayton has a near parallel ("do not comprehend their own character"), and Smith's point is precisely that the two are **not** equivalent. Recorded on that basis. |
| 5 | Richards's warning on speaking against the servants of the Most High | **V042** (S06, theological). The quoted sentence ("will be found liars") is nowhere in Richards. What Smith actually says, at p. 288 n. 15, is that Richards "alters the sense somewhat with 'never lift your voice against the servants of God again'" — a change of scope from Joseph Smith singular to the servants plural. Recorded as that. |
| 6 | Anti-clerical interpolation in the Manuscript History | **Noted inside V044** (S07). Confirmed at Smith p. 289 n. 21, but it is an 1855 addition, downstream of T. The entry records the Bullock/Clayton difference ("false prophets" / "false teachers") and cites the later drift in its significance. |
| 7 | Sarcasm against scribes and senators sanitised | **V045** (S07, historical). Confirmed at Smith p. 289 n. 24, which also confirms Bullock himself dropped the phrase while preparing T. |
| 8 | Core godhood proposition recast as the Snow couplet | **Noted inside V004** (S09). Confirmed at Smith p. 290 n. 26. It is a GM2/RC act, downstream of T; T prints Bullock. |
| 9 | Bullock's "disputation" for "comprehension" | **V055** (S13, reception). The extracted note has the direction backwards — it says Bullock wrote "disputation" and TS corrected it. Smith p. 290 n. 43 says the reverse: "In TS, Bullock wrote 'disputation' for 'comprehension'", and the manuscript reads "comprehension". Recorded in the correct direction. Also note the number: it is n. 43, not n. 40. |
| 10 | Premature insertion of *Baurau* into Genesis 1:1 | **V060** (S15, reception), and **V058** (S15, scribal). Confirmed at Smith p. 291 n. 49. V058 is the find worth having: Clayton wrote "Berosheit", began "Barau", and struck it — manuscript evidence at the exact point Smith says T inserts the word without warrant. |
| 11 | Woodruff's extended sealing paragraph | **V020** (S24, unique). Confirmed at Smith p. 294 n. 71. |
| 12 | "My aged friend" pluralised | **V105** (S35, reception). Confirmed at Smith p. 43 and p. 298 n. 89. |

Two claims in the extracted notes could **not** be confirmed and are not cited anywhere
in `apparatus.json`: that Woodruff, Richards and Clayton read "saviors on Mount Zion"
at V021 (the phrase appears nowhere in Smith's book), and that Smith glosses Richards's
"Gnolom" as Hebrew *olam* at p. 297–298 n. 87 (neither "Gnolom" nor "olam" appears in
the full text). V021 and V032 are written without relying on either.

The extracted notes also state at V017 that T "kept B's 'immortal'". It does — and it
also prints "their spirits existed coequal with God" three lines later, which is
Clayton's reading against Bullock's "coexisted". Both facts are now recorded, as V017
and V071.

## Scribal cancellations

Seven of the thirty-six cancellation spans bear on the sense and are recorded as
`scribal` entries. The rest are false starts, repeated articles and corrected
abbreviations. Three of the seven are the ones the brief singles out, and one more is
independently confirmed by Smith from the manuscript:

- **V053** (S11) — Bullock: "be a K[ing] & ~~God~~ Priest to God". Smith p. 290 n. 37
  confirms the sequence from the manuscript. The scribe first wrote the more extreme
  claim.
- **V082** (S25) — Clayton: "hath not committed the ~~eternal sin~~ unpardonable sin".
  The struck phrase is the Mark 3:29 reading; the correction is evidence that
  "unpardonable" is what was spoken.
- **V068** (S18) — Richards: "the character of ~~the~~ God~~s~~". Two struck spans at one
  point; the plural was written and then corrected to the singular, in a sermon whose
  argument is that the Gods are plural.
- **V086** (S26) — Bullock struck an entire clause, "so long as man will not give acct.
  of his sins", whose counterpart survives in Clayton nearly word for word and in
  Richards in substance. This is the only cancellation that removes a whole thought from
  the base text's reading text, and T prints Clayton's version of it.
- **V052** (S10) — Clayton: "as the father ~~hath~~ had power". Tense, and not indifferent
  here: Richards independently has "Had".
- **V058** (S15) — Clayton: "Berosheit ~~Barau~~". See Smith flag 10 above.
- **V064** (S17) — Bullock: "Greek says ~~Jachem~~ ⟨Jacob⟩", inside the polyglot
  demonstration whose force depends on the four languages agreeing.

**Underlines are not recorded as entries.** The `scribal` criterion covers cancellations
and insertions, and an underline marks emphasis rather than changing the sense. They are
worth a note nonetheless, because Woodruff's twenty-five underlines are not scattered:
nineteen of them fall on two sentences, "God who sits in __yonder heavens__ is a __man
like yourselves__ That __GOD__" (S08) and the whole of the John 5:19 quotation (S10),
with a twentieth on "__sin against__" him at S28. Woodruff was marking what he took
to be the doctrinal core of the discourse. Clayton's underlines mark the questions
"__heard__ him? __communed with him__?" (S05). That pattern is a datum about how the
reporters heard the sermon, and a later phase could surface it in the web edition.

## Boundary problems

Two places where `data/sections.json` boundaries make a comparison awkward. Per the
brief, neither was moved; both are handled by a new optional per-entry field,
`reading_sections`, which names the section a witness's reading is quoted from when it
differs from the entry's own. The CLI prints the section in brackets.

- **S21/S22 (V018).** Bullock's "intelligence is self existent" falls at the end of S21;
  the counterparts in Woodruff, Richards and Clayton all open S22. The entry sits in
  S21 with B and T, and quotes W, R and C from S22.
- **S09/S10 (V051) and S17/S18 (V067, V068).** T's section divisions fall one clause
  away from Bullock's at three points, so T's counterpart is quoted from the adjacent
  section.

A third is recorded in the entry rather than the field: **V065** (S17) collates
Woodruff's and Richards's out-of-order return to the grand council, which belongs with
S16's material but is contiguous in those two reports only where it stands.

## Places where I was genuinely unsure

Ten calls the principal may want to adjudicate. My call is given in each case and is
what the file currently does.

1. **V018 (S21), "from age to end".** Bullock's phrase differs from Clayton's "age to
   age" by one word, and the likeliest explanation is a slip of the pen — which the
   criteria exclude as spelling. **Call: kept**, because if it is not a slip it gives
   intelligence a terminus and contradicts the sentence it stands in, and the apparatus
   should not decide that question silently. This is the weakest of the thirty-four.
2. **T's capitalised "unless WE are able to comprehend" (S04).** Typographic emphasis
   the printer supplies, which no report supports. **Call: not recorded.** The criteria
   exclude capitalisation, and nothing here carries sense beyond the emphasis. But it is
   one of only a handful of places where T's compositor editorialises visibly.
3. **V038 (S03), the divine name.** Transliteration is spelling, and the criteria
   exclude spelling. **Call: recorded**, because it is the name the whole sermon is
   about and Bullock's form would carry an accidental echo of Mark 15:34. Reasonable
   people could strike it.
4. **T's relocation of Clayton's "good logic" to the head of S21.** Order, not reading.
   **Call: not recorded** as a variant; it is already in `sections.json`'s
   `boundary_notes`. The same applies to T's true reordering in S30.
5. **T's "were open" for Bullock's "are open" (S28).** A tense shift in the definition
   of the unpardonable sin: heavens standing open, or having been opened. **Call: not
   given its own entry**; recorded in V025's significance. It may deserve a `reception`
   entry of its own.
6. **V036 (S01), "instruction" against "inspiration".** Typed `theological`, which is a
   stretch — it concerns what is asked for in a prayer, not a doctrinal claim. **Call:
   kept as theological**, since JSP flags it and T prints both, but `rhetorical` would
   be defensible and so would demoting it to an attached footnote.
7. **The `unique` entries in S34 and S35.** Clayton has broken off (five words in S34,
   none in S35) and Richards is very brief, so "unique to Bullock" is nearly vacuous
   there. **Call: restrained to what JSP or Smith independently flags** — V031, V104 and
   V106 only — rather than recording every B-only clause in the longest section in the
   discourse. The same restraint was not needed elsewhere.
8. **V065 (S17), "concocted a scheme".** Recorded as `rhetorical` in S17 although the
   material belongs with S16, because Woodruff and Richards recapitulate out of order.
   **Call: recorded in S17** with a note. Moving it would require moving a boundary,
   which the brief forbids.
9. **V009 (S13), "before" against "when" worlds came into existence.** Bullock's
   "before worlds came rolled nto existence" may be a dropped "i" and nothing more, or
   it may place the Father's probation prior to creation. **Call: recorded as
   historical**, hedged in the significance.
10. **Whether `reception` should have more entries.** I adopted the rule that T's
    behaviour is recorded in an eyewitness entry's T reading unless T's own reading is
    the only thing to record, which produced twelve reception entries. A stricter
    reading of the brief would make a reception entry at every point where T fuses two
    witnesses — S11's three-part ascent, S17's doubled remark, S25's fused provision —
    which would add roughly fifteen more. **Call: the narrower rule**, stated in the
    file's metadata so it can be reversed mechanically.

## Sources

- William V. Smith, *The King Follett Sermon: A Biography* (BCC Press, 2023). Every
  `Smith, p. NN` cite in `apparatus.json` was verified against
  `refs/smith-king-follett-sermon-biography.txt`, which is present and complete.
  Smith's own critical text with sigla runs from p. 271; his notes on it from p. 287.
- The Joseph Smith Papers editorial footnotes, as captured in `data/footnotes.json`.
- `refs/phase1-report.md` supplied ten T-versus-eyewitness leads. All ten are now
  entries: V101 and V102 (S33), V103 (S34), V059 and V060 (S15), V028 (S31), V055
  (S13), V005 (S11), V097 (S31), V090 (S29). Its two further flags are V079 (S24) and
  unsure call 2 above.
