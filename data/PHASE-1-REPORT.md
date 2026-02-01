Phase 1 Report: Text Normalization & Alignment

1. Transcript Cleanliness Assessment

All four transcripts come from the Joseph Smith Papers (JSP) and use consistent editorial conventions. The texts are clean and ready for collation with the following features preserved:

Feature                   | W   | B   | R   | C
--------------------------|-----|-----|-----|-----
Page markers [p. XX]      | 8   | 9   | 5   | 8
Abbreviated expansions    | 6   | 184 | 122 | 71
Interlinear insertions <> | 2   | 8   | 2   | 1
Footnote apparatus lines  | 4   | 136 | 8   | 12

Editorial conventions present in the transcripts:
- Page markers: [p. [133]], [p. 14], etc. (original manuscript pagination)
- Abbreviated word expansions: con[ference], subj[ec]t, etc.
- Interlinear insertions: <text> marks words added between lines
- Square bracket completions: [t], [ed] for uncertain readings
- Siglum-style annotations in footnotes cross-referencing other witnesses

Status: CLEAN. No normalization corrections needed. Original line breaks have been removed; paragraph breaks remain. The editorial apparatus should be preserved for scholarly reference but stripped during word-level collation (handled by align.py's normalize_text function).


2. Word Count & Structural Analysis

Witness                    | Words | Pages | Coverage
---------------------------|-------|-------|----------
[B] Thomas Bullock         | 4,103 | 9     | 100% (35/35 sections)
[C] William Clayton        | 2,927 | 8     | 91%  (32/35 sections)
[W] Wilford Woodruff       | 2,409 | 8     | 97%  (34/35 sections)
[R] Willard Richards       | 1,091 | 5     | 94%  (33/35 sections)
TOTAL                      | 10,530|       |

Structural observations:
- Bullock writes in dense, continuous prose with heavy abbreviation
- Woodruff writes in flowing, readable prose with few abbreviations
- Clayton falls between Bullock and Woodruff in style
- Richards is highly telegraphic, using sentence fragments and dashes


3. Base Text Recommendation

RECOMMENDED: Thomas Bullock [B]

Rationale:
- Most complete account at 4,103 words (39% of total corpus)
- Only witness covering all 35 identified thematic sections (100%)
- Historically used as the basis for the History of the Church version
- The PROJECT-OVERVIEW itself suggests "The History of the Church version or the Bullock account"
- Richest in detail for virtually every section of the discourse
- Extensive JSP footnote apparatus provides cross-references to all other witnesses

Supplementary value of each witness:
- [W] Woodruff: Best for readable prose reconstruction; captures unique phrasings (e.g., "That GOD if you were to see him to day")
- [C] Clayton: Strong second witness for most sections; records the "mark it Br Rigdn" aside
- [R] Richards: Valuable for confirming key phrases despite brevity; unique "Gnolom" (Hebrew 'olam) reference


4. Alignment Map

The discourse has been segmented into 35 thematic sections (S01-S35). The full alignment map is in alignment_map.json.

Discourse Structure Overview:

  S01  Introduction: Occasion and Subject              W B R C
  S02  Preliminary: Paving the Way                     W B . C
  S03  Need to Understand God from the Beginning       W B R C
  S04  The World Knows Little of God                   W B . C
  S05  What Kind of Being Is God?                      W B R C
  S06  Challenge: If I Show God's Character            W B R C
  S07  Right of Conscience / False Prophets            W B R C
  S08  God Is a Man in Form                            W B R C
  S09  God Was Once a Man / Refuting Eternal Godhood   W B R C
  S10  Christ's Power from the Father                  W B R C
  S11  Becoming Gods: Exaltation by Degrees            W B R C
  S12  Consolation for Mourners: Heirs of God          W B R C
  S13  Christ Followed the Father's Pattern            W B R C
  S14  First Principles / Not All in This World        W B R C
  S15  Hebrew Exegesis: Bereshit / Genesis 1:1         W B R C
  S16  Grand Council of the Gods                       W B R C
  S17  The Polyglot Bible: Jacob vs. James             W B R C
  S18  Creation Ex Nihilo Refuted                      W B R C
  S19  The Soul / Mind of Man: Pre-existence           W B R C
  S20  Mind of Man Coequal with God                    W B R C
  S21  Intelligence Is Self-Existent: Ring Analogy     W B R C
  S22  God's Laws for Lesser Intelligences             W B R C
  S23  Revelations Save Spirit and Body                W B R C
  S24  Awful Responsibility for Our Dead               W B R C
  S25  All Sins Forgiven Except One                    W B R C
  S26  Unpardonable Sin After Death / Knowledge        W B R C
  S27  The Devil's Plan vs. Christ's Plan              W B R C
  S28  The Unpardonable Sin Defined                    W B R C
  S29  Apostates of the Church                         W B R C
  S30  Warning: Be Careful                             W B R C
  S31  Many Mansions / Degrees of Glory                W B R .
  S32  Friends Gone for a Moment / Eternity            W B R .
  S33  Mothers Shall Have Their Children               W B R C
  S34  Baptism: Water, Fire, and Holy Ghost            W B R C
  S35  Closing: 'You Don't Know Me'                    . B R .

Key gaps:
- Richards omits S02 (Preliminary) and S04 (World Knows Little) -- fits his telegraphic style
- Clayton omits S31-S32 (Mansions/Eternity) and S35 (Closing)
- Woodruff omits S35 (Closing personal testimony)
- Bullock is the only witness to cover ALL 35 sections


5. Deliverables Produced

  data/
    alignment_map.json         Fuzzy alignment of all 35 sections across 4 witnesses
    transcript_analysis.json   Word counts and structural metrics
    align.py                   Python tool for viewing and exporting aligned segments
    segments/                  140 individual segment files (35 sections x 4 witnesses)
    PHASE-1-REPORT.md          This report


6. Tools & Usage

  python3 data/align.py                  # Print alignment overview grid
  python3 data/align.py --segment S08    # View all 4 witnesses for section S08
  python3 data/align.py --stats          # Coverage statistics
  python3 data/align.py --export         # Re-export all segments to data/segments/


7. Notes for Phase 2

The alignment map provides paragraph-level alignment. Phase 2 will require:
- Word-level diff analysis within each aligned section
- Generation of collation_map.json with lemma/variant entries
- Identification of "Critical Variants" (meaning-changing differences) for Phase 3 flagging

Key critical variants to watch for (noticed during alignment):
- S08: "holds the worlds" (W) vs. "holds this world in its orbit" (B) vs. "holds this world in its sphere in its orbit" (C)
- S09: "the Father was once on an earth like us" (W) vs. "God himself the father of us all dwelt on a Earth same as J C himself did" (B) vs. "was on a planet as Jesus was in the flesh" (C)
- S11: "dwelling in everlasting burnings" (W) vs. "sit in everlasting power" (B) vs. "dwell in evelastig burning & everlasting power" (R)
- S15: "broat forth the gods" (W) vs. "brought forth the Gods" (B/R/C) -- spelling variant vs. textual variant
- S21: "my ring" (W) vs. "I take my ring from my finger" (B) -- level of detail
- S35: "you never knew my heart no man knows my history" (B) vs. "You dont know me— you never will" (R) -- significant variant in personal statement
