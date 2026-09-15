You are the adjudicator for a digital critical edition of Joseph Smith's King Follett Discourse (7 April 1844) in the git repo /Users/nairmet/development/king-follett (sigla: B Bullock = base text, W Woodruff, R Richards, C Clayton = eyewitness reports; T = *Times and Seasons* 15 Aug 1844, derived composite). Read ~/AGENTS.md (short), then the repo README.md and HANDOFF.md, then run `python3 -m kf validate` and `python3 -m unittest discover tests` (both must pass before and after your work).

# Situation

Two independent lanes produced variant lists from the same `data/sections.json`:

- Lane A (Claude, Opus 5): `data/apparatus.json` — 106 entries (34 revised legacy + 72 new), with criteria in its metadata, and `data/APPARATUS-REPORT.md` describing every decision, ten "genuinely unsure" calls, and boundary problems it noticed.
- Lane B (Codex, Sol), blind to Lane A: `refs/variant-candidates-independent.md` — 150 candidates (62 eyewitness categories a–e, 88 "reception" where T departs from the notes), a ranked top ten, and six suspected alignment problems in `sections.json`.

Your job is to reconcile them into one apparatus and one set of section boundaries, recording every decision.

# Rulings already made by the principal (apply, do not reopen)

1. Lane A's unsure call #10 (how to record T's behaviour): ADD separate `reception` entries wherever T departs from ALL eyewitnesses in a meaning-bearing way, or sides with one eyewitness against the others at a point that shaped the received text. The edition exists partly to show how the published text was built, and the site will filter by type, so the extra ~15 entries are wanted. Keep T's reading inside eyewitness entries as well.
2. The `noes [knows]` expansion stays as a replace-mode expansion (reading text shows "knows").
3. Nothing is verified against manuscript images in this project; JSP's transcription is the authority. Do not add verification claims.

# Tasks

1. Merge. For each Lane B candidate: is it already in Lane A (same locus and substance)? If yes, note the match; if Lane B's reading or significance adds something, fold it in. If no: does it meet the criteria in `data/apparatus.json` metadata? If yes, add it as a new entry (next free V-number; `status: "new"`; in `sources` add "independent pass (Codex Sol) S09.1" style provenance). If no, record it as rejected with a one-line reason. Conversely, review Lane A entries that Lane B did not find: keep them unless they fail the criteria on re-reading (then `status: "withdrawn"` with reason). Do not delete entries; ids are permanent.

2. Decide Lane A's ten unsure calls (except #10, ruled above) and record each decision with reasoning.

3. Alignment. Examine Lane B's six alignment flags and Lane A's "Boundary problems". For each: is the boundary wrong? If yes, move it in `data/sections.json` following the Phase 1 rules (verbatim slices, gapless partition, cuts at clause boundaries outside markup — the validator enforces these), update `boundary_notes`, and re-check any apparatus entry in the affected sections (readings must still be verbatim substrings of their section's reading text; the validator checks this). If the move is defensible either way, leave it and record why.

4. Add `tests/test_apparatus.py` covering: every eyewitness reading is a verbatim substring of its section reading text (or "om."); every entry has a valid section id, type, status; cancellation notation "(canc. …)" only appears in `scribal`-typed entries or where a `~~…~~` span exists in that witness's section text; V-numbers are unique and contiguous in id space.

5. Update README.md's Status section to describe the apparatus accurately (entry counts by type, that it was built by two independent passes and adjudicated, and that JSP transcriptions are accepted as authoritative).

6. Write `data/ADJUDICATION.md`: the merge table (Lane B candidate → matched V / new V / rejected + reason), the ten decisions, the boundary decisions, final totals by type and status, and a short list of anything you think a human editor should still look at. Summarize the same in your final message.

7. Commit in logical steps (merge; boundaries; tests; README + adjudication log). Do not push. Do not touch `docs/`, `refs/`, `transcripts/`.

Be consistent rather than generous: an apparatus is only useful if its inclusion rule is predictable.

# Note on restart

A previous attempt at this task was cut off by a Claude Code session limit mid-way; its partial, non-validating changes are in `git stash` (do not apply them). Start from the clean committed state. `refs/smith-textual-history-notes.md` is machine-extracted — verify any Smith page you cite against `refs/smith-king-follett-sermon-biography.txt`.
