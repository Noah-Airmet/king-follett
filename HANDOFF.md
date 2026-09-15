# Handoff — King Follett digital critical edition

Written 2026-09-15 for the next agent. The prior Cursor session (Fable 5.1) ran
out of usage. Do **not** rebuild the web UI in this Cursor window; the data
layer is the remaining work, then a separate session (or Claude Code) should
do the site.

Read this file, then `README.md`. Run `python3 -m kf validate` and
`python3 -m unittest discover tests` before changing anything. Both passed
on 2026-09-15.

This is not school work. Dev root: `/Users/nairmet/development/king-follett`.
GitHub: `Noah-Airmet/king-follett` on `main`. Live site (stale):
https://noah-airmet.github.io/king-follett/ (`docs/index.html`, **do not
edit** until migration). Do not push unless Noah asks.

## What the project is

A scholarly reconstruction of Joseph Smith's King Follett Discourse
(7 April 1844) from four eyewitness reports plus the 1844 *Times and Seasons*
composite. The data layer is the edition; the website is generated from it.

Sigla: **B** Bullock (base text), **W** Woodruff, **R** Richards, **C** Clayton
(eyewitness); **T** *Times and Seasons* 5:15, 15 Aug 1844 (**derived**, never
a fifth independent witness). History of the Church is **not** a witness.

## Noah's decisions (do not reopen)

1. Host at **`kingfollett.noahairmet.com`** (Cloudflare Pages), not a path on
   `noahairmet.com`. The personal site (`development/noahairmet.com`) forbids
   client-side JS and Worker runtime code. Recipe:
   `~/.agent-bus/cloudflare-recipes.md`. After ship, link from the home page
   or a field note; do not proxy through the Astro Worker.
2. Add T as a fifth, derived witness. Do **not** add *History of the Church*.
3. Accept the **Joseph Smith Papers transcriptions as authoritative**. Do not
   claim manuscript-image verification. Old scan notes live only as
   `legacy_verification` on some entries. JSP `TEXT:` footnotes are the
   edition's uncertainty layer.
4. Web edition only. No `.docx` / print pipeline.
5. The Smith biography PDF stays local (`refs/`, gitignored). Never commit it.

## Git state (HEAD `19105b2`)

Working tree clean except this handoff. Latest commits:

- `19105b2` APPARATUS-REPORT
- `0d78603` `python3 -m kf apparatus Sxx`
- `1dccf81` `apparatus.json`: 106 entries, verbatim readings
- `bdddc93` … `ebdbf2e` Phase 1 data model (transcripts, parser, sections,
  T, restored `~~`/`__` markup)

**Stash `stash@{0}` is poison.** It is a half-finished adjudication from
2026-09-11 13:05 when Claude Code hit its session limit. It fails validate
(duplicate order on `V019` / S22). **Do not `git stash pop`.** Inspect with
`git stash show -p` if you want the attempted merge; otherwise ignore it.

## What is done (Phases 1 and 2b)

**Phase 1 — data is the source of truth.** `python3 -m kf validate` proves:

- Five transcripts in `transcripts/` with JSP markup, including cancellations
  `~~…~~` (B16 / W3 / R7 / C10) and underlines `__…__` (B5 / W25 / R0 / C6).
  Stripping those markers reproduces the January 2026 paste byte-for-byte.
- `data/sections.json`: 35 sections, all five witnesses, gapless partition of
  every body, cuts outside markup.
- `data/witnesses.json`, `data/footnotes.json`, `src/kf/` (stdlib only).

**Phase 2b — systematic apparatus.** `data/apparatus.json`: **106 entries**
(34 revised + 72 new, none withdrawn). Types: theological 40, unique 26,
rhetorical 12, reception 12, historical 7, scribal 7, omission 2. Every
eyewitness reading is a verbatim substring of that witness's reading text
(or `om.`). Report: `data/APPARATUS-REPORT.md`.

The root `README.md` *Status* section still described the apparatus as
"carried forward unchanged" until this handoff; that sentence was stale
after 2b. Trust `data/apparatus.json` metadata and the report, not the old
Status paragraph.

## What is not done

### Phase 2e — adjudicate (blocked, next)

Two independent lists exist and have **not** been merged:

| Lane | Output | Count |
| --- | --- | ---: |
| A (Claude Opus 5, 2b) | `data/apparatus.json` | 106 |
| B (Codex Sol, blind) | `refs/variant-candidates-independent.md` | 150 (62 eyewitness a–e, 88 reception) |

Charter: `charters/phase2e-adjudicate.md`. Principal already ruled **call 10**:
add separate `reception` entries wherever T departs from all eyewitnesses in
a meaning-bearing way, or sides with one against the others at a point that
shaped the received text (~15 extra entries wanted). Keep T readings on
eyewitness entries too.

Unsure calls 1–9 are listed in `data/APPARATUS-REPORT.md` §"Places where I
was genuinely unsure". Lane B's six alignment flags are at the end of
`refs/variant-candidates-independent.md` (T S01/S02, W+R S17/S16, T S17/S18,
T S21/S22, W S24/S25, T S28/S29). Lane A noted S21/S22 and a few T clause
offsets via `reading_sections` instead of moving boundaries.

A first 2e attempt on Claude Code died on **session limit**
("resets 5:20pm America/Denver"). A sleep-until-17:25 retry was scheduled
that evening and **never ran** (process gone by 2026-09-15). Content
revision (2d) was chained after 2e and also never ran.

### Phase 2d — prose (`content/`)

Does not exist. Charter: `charters/phase2d-content.md`. Must wait until 2e
finishes so the commentary cites the adjudicated apparatus. **Do not edit
`docs/index.html`.**

### Phase 3 — static site

Not started. Keep it a static Python `build.py` + one vanilla JS file, no
framework, self-hosted Literata/Besley/Plex Mono from noahairmet.com's kit.
Pages: reading edition, synoptic four/five columns, witness pages, filterable
apparatus, about. CSP: if this stays a Pages project it can have a small JS
file; do not try to fold it into `noahairmet.com`.

### Phase 4 — migrate off GitHub Pages

Pages project + CNAME `kingfollett.noahairmet.com` + custom domain via
`~/.agent-bus/cloudflare-recipes.md`. Old `docs/index.html` becomes a
redirect stub (GitHub Pages cannot 301). Document the recipe in that file
and a dated homelab runbook entry. `npm run deploy` of noahairmet.com is
unrelated and needs Noah's explicit OK.

## Local-only files (`refs/`, gitignored)

Needed for 2e/2d. Do not commit. Copyrighted Smith PDF.

- `refs/jsp-json/` — 36 JSP page JSON files; `tools/restore_jsp_markup.py`
  depends on them
- `refs/jsp-markup-audit.md`, `refs/reextraction-report.md`
- `refs/times-and-seasons-raw.md`
- `refs/smith-king-follett-sermon-biography.pdf` + `.txt` (pdftotext)
- `refs/smith-textual-history-notes.md` — machine-extracted; **verify every
  cite** against the `.txt`. Known error: it said T kept B's "immortal" at
  V017; T actually prints "their spirits existed coequal with God" at that
  locus (and still has "immortal spirit" nearby). 2b already caught this.
- `refs/variant-candidates-independent.md` — Lane B
- `refs/phase1-report.md` — Phase 1 builder notes
- `refs/collation_map.snapshot.json` — frozen January list

## Routing (from `~/.agent-bus/delegation.md` and Noah)

Noah asked: **Claude Code first** (`--to claude --model claude-opus-5
--effort medium|high`), then Codex (`gpt-5.6-sol` or `gpt-5.6-luna`,
**not Astra**), or Antigravity for bulk. Cursor Fable is the overflow pool
and was burning the usage this session ran out of — prefer Claude/Codex
for 2e and 2d.

```bash
# 2e
agent-dispatch submit --to claude --model claude-opus-5 --effort high \
  --mode write --cwd /Users/nairmet/development/king-follett \
  --scope "data/, tests/, README.md" \
  --id kf-phase2e-adjudicate-v2 --timeout 7200 \
  --prompt-file charters/phase2e-adjudicate.md --run

# 2d only after 2e validates and is committed
agent-dispatch submit --to claude --model claude-opus-5 --effort medium \
  --mode write --cwd /Users/nairmet/development/king-follett \
  --scope "content/ only" \
  --id kf-phase2d-content --timeout 5400 \
  --prompt-file charters/phase2d-content.md --run
```

If Claude Code says session limit, **tell Noah and wait**; do not silently
reroute to Cursor. (That mistake already happened once this project.)

A lane reviews its own work, never another lane's findings. Adjudication
is a principal/Opus job, not a cheap-lane review of 2b.

## Acceptance before calling 2e done

- `python3 -m kf validate` and `python3 -m unittest discover tests` pass
- `tests/test_apparatus.py` exists and covers verbatim readings, types,
  statuses, unique V-ids, cancellation notation
- `data/ADJUDICATION.md` exists with the merge table, the ten decisions,
  boundary decisions, and final counts
- README *Status* describes the actual apparatus
- No changes to `docs/`, `refs/`, `transcripts/`

## Site-builder notes (Phase 3, later)

- Numbers in prose must come from data (`{{stats.*}}` placeholders in 2d)
- T labelled derived in every UI surface
- Diplomatic vs reading toggle from `src/kf/jsp.py` renderers
- Variant permalinks `#V017`, section permalinks `#S20`
- Old GH Pages URL gets a redirect stub, not a 301 (GH Pages cannot 301)
