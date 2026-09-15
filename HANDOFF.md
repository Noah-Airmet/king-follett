# Handoff — King Follett digital critical edition

Rewritten 2026-09-15 (afternoon). The version this replaces was written that
morning, before Phases 2e, 3 and 4 ran; it is in git history if you want it.

Read this, then `README.md`. Run `python3 -m kf validate` and
`python3 -m unittest discover tests` before changing anything. Both passed at
`cc23975`.

This is not school work. Dev root: `/Users/nairmet/development/king-follett`.
GitHub: `Noah-Airmet/king-follett` on `main`. **Live at
<https://kingfollett.noahairmet.com>.** Pushed to GitHub 2026-09-15
(`cc23975`); `docs/`'s redirect stub is therefore in effect and the old
January edition is off the web. Do not push again unless Noah asks.

The two are independent: `wrangler pages deploy` uploads `site/` directly, so
a push does **not** update the live site and a deploy does **not** update
GitHub. Do both.

## What the project is

A scholarly reconstruction of Joseph Smith's King Follett Discourse
(7 April 1844) from four eyewitness reports plus the 1844 *Times and Seasons*
composite. The data layer is the edition; the website is generated from it.

Sigla: **B** Bullock (base text), **W** Woodruff, **R** Richards, **C** Clayton
(eyewitness); **T** *Times and Seasons* 5:15, 15 Aug 1844 (**derived**, never
a fifth independent witness). History of the Church is **not** a witness.

## Noah's decisions (do not reopen)

1. Hosted at **`kingfollett.noahairmet.com`** on Cloudflare Pages. Done.
2. T is a fifth, derived witness. Do **not** add *History of the Church*.
3. The **Joseph Smith Papers transcriptions are authoritative**. Do not claim
   manuscript-image verification anywhere. Old scan notes survive only as
   `legacy_verification` on some entries. JSP `TEXT:` footnotes are the
   edition's uncertainty layer.
4. Web edition only. No `.docx` / print pipeline.
5. The Smith biography PDF stays local (`refs/`, gitignored). Never commit it.
6. Structure: **the spine**, not separate Reading/Synopsis/Apparatus views.
   The 35-section partition is the site's backbone; other pages are entrances
   into it. Chosen 2026-09-15 against the four-desks alternative.
7. Visual identity: **pulpit-archive family, as a sibling** — same faces, same
   discipline, manuscript paper, iron-gall ink instead of oxblood.

## State at `cc23975`

Working tree clean. Commits since the morning handoff, newest first:

- `cc23975` centre the masthead; dev server sends no-store
- `a50f505` this handoff
- `2f735a2` wire the commentary and witness essays; link cited ids
- `1ed34e4` Phase 2d prose (Codex Sol)
- `fb153d8` the previous rewrite of this handoff
- `9b2b584` migrate to kingfollett.noahairmet.com; `docs/` redirect stub
- `2653a99` count-aware stacking; content-hashed assets
- `724e8da` README: the site
- `dda8705` the site itself
- `5be3dbf` … `4cc9d3f` Phase 2e adjudication (Codex Sol)

Every charted phase is now done. What remains is in *What is not done* below,
and none of it blocks anything.

**Stash `stash@{0}` is still poison.** Half-finished adjudication from
2026-09-11 that fails validate. Do not `git stash pop`. It is now also
superseded by the 2e work; it can simply be dropped.

### Phase 2e — adjudication: DONE

`data/ADJUDICATION.md`. Apparatus went 106 → 122 there, and **122 → 131**
after the audit below: 46 theological, 29 reception, 26 unique, 12 rhetorical,
9 historical, 7 scribal, 2 omission; 97 new, 34 revised, none withdrawn. Lane B: 93 matched, 15 added, 42 rejected. All
nine unsure calls decided. `tests/test_apparatus.py` added (64 tests pass).

Two things a reviewer should know:

- **The 42 rejection reasons in the merge table are boilerplate** — one
  sentence repeated, so the table cannot be checked. `data/REJECTIONS.md`
  (2026-09-15, `cursor-grok-4.6-high`) is an independent second pass over those
  forty-two with a specific, checkable reason each. It **upholds 32 and
  disagrees with 10**; the ten are listed at the end of that file with a short
  argument each. They have *not* been added to `data/apparatus.json` — that is
  an editorial call for Noah. Its own strongest two are S24.1 (the scope of
  which spirits must obey the gospel) and S26.6 (Woodruff makes receiving the
  Holy Ghost the condition of the unpardonable sin where the others set a
  mortal-life boundary). The 93 *matches* still share a second boilerplate
  template; nobody has audited those.
- **No boundary moved.** All six of Lane B's alignment flags were resolved as
  "defensible in physical order" and recorded in `boundary_notes`. Two
  independent lanes flagged the same six cuts, so this is deferred rather than
  settled. `data/ADJUDICATION.md` §"Human-editor review" also flags V018, V038
  and the W/R council recapitulations in S17.

### Phase 3 — the site: DONE

`build.py` → `site/` (gitignored). `python3 -m venv .venv && .venv/bin/pip
install -r requirements.txt`, then `.venv/bin/python build.py`, or
`--serve` to serve it. One dependency, `markdown`, build-time only; `src/kf`
stays standard library.

- `src/kfweb/` — `html.py` (escaping), `render.py` (spans → HTML),
  `rail.py` (the collation rail), `pages.py` (the five page shapes)
- `web/edition.css`, `web/edition.js`, `web/fonts/` — self-hosted
- Reading text is rendered **from the string `jsp.render_reading` produces**,
  not from a second implementation, so the page and `validate` cannot disagree
- Reader state = three checkboxes the stylesheet reads with `:has()`, so the
  edition works with JS off. `edition.js` adds URL state, the slip, the rail's
  position sense, the keyboard, and citation-on-copy
- `{{stats.*}}` placeholders in `content/` are filled at build time; an unknown
  key raises. `site/stats.json` lists every valid key
- Verified at 375, 1024, 1440 and 1600px, light and dark, no console errors

The stacking rule is expanded by hand over `:has()` combinations because CSS
cannot count checked boxes. If you add a witness, regenerate those blocks.

### Phase 2d — prose: DONE

Seven files in `content/`, ~5,900 words, by Codex Sol at medium effort
(`1ed34e4`), wired into the site at `2f735a2`. No "(citation to be confirmed)"
items. Quality is markedly better than the low-effort 2e pass.

Its report lists every old-commentary claim that did not survive the check
against the revised apparatus. I spot-verified the factual corrections against
`data/apparatus.json` and they hold — Richards's "Lot fell on Jesus" is V088,
not V024 (which is the devil's offer to save all); Woodruff's hell-fire denial
is the separate unique reading V085, not part of V022; R does not contain
Bullock's "age to end" formula at V018; R preserves the positive half of V033
but not Bullock's two-part juxtaposition. All 28 variants cited across
`commentary.md` and `verification.md` exist.

Where each file landed: `introduction`, `reading-the-apparatus`,
`verification` and `bibliography` are the four sections of `/about/`;
`textual-history` is the prose of `/reception/`; `commentary` is `/commentary/`
(sixth in the nav); `witnesses` is split on its headings onto the five witness
pages. V-ids and S-ids in prose are linked to what they name.

### Phase 4 — migration: DONE

Pages project `king-follett`, custom domain, CNAME in the noahairmet.com zone.
Recipe and its gotchas: `~/.agent-bus/cloudflare-recipes.md`. **Deploys are
explicit and not tied to git**:

```bash
source ~/.config/cloudflare/credentials
export CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_KEY CLOUDFLARE_EMAIL
.venv/bin/python build.py
~/development/noahairmet.com/node_modules/.bin/wrangler pages deploy site \
  --project-name king-follett --branch main --commit-dirty=true
```

`docs/index.html` is now a redirect stub. It only takes effect on GitHub Pages
once the local commits are pushed; until then the old January edition is still
what `noah-airmet.github.io/king-follett/` serves.

There is no dated homelab runbook file in `~/development/homelab` — no such
convention exists — so the recipe went only to `cloudflare-recipes.md`.

## What is not done

### Open, smaller

- The apparatus ledger has no free-text search. 122 entries is browsable, but a
  client-side index over the five witnesses would be a real addition.
- No OG card. `favicon.svg` is generated inline in `build.py`.
- Link the edition from noahairmet.com's home page or a field note. **Do not**
  proxy it through the Astro Worker; `npm run deploy` there is unrelated and
  needs Noah's explicit OK.

## Local-only files (`refs/`, gitignored)

Needed for 2d. Do not commit. Copyrighted Smith PDF.

- `refs/jsp-json/` — 36 JSP page JSON files; `tools/restore_jsp_markup.py`
  depends on them
- `refs/jsp-markup-audit.md`, `refs/reextraction-report.md`
- `refs/times-and-seasons-raw.md`
- `refs/smith-king-follett-sermon-biography.pdf` + `.txt` (pdftotext)
- `refs/smith-textual-history-notes.md` — machine-extracted; **verify every
  cite** against the `.txt`. Known error: it said T kept B's "immortal" at
  V017; T actually prints "their spirits existed coequal with God" at that
  locus. 2b already caught this.
- `refs/variant-candidates-independent.md` — Lane B (Codex Sol, blind pass)
- `refs/phase1-report.md`, `refs/collation_map.snapshot.json`

## Routing

Read `~/AGENTS.md`, then `~/.agent-bus/delegation.md`, before delegating
anything. Two rules this project has already paid for:

- **A lane reviews its own work, never another lane's findings.** Cross-lane
  adjudication is a principal/Opus job. `~/.agent-bus/models.md` says
  explicitly that Luna must never be given another lane's guard findings.
- **If Claude Code says session limit, tell Noah and wait.** Do not silently
  reroute to Cursor. That happened once on this project.

Cursor's third-party pool was **exhausted as of 2026-09-15** — Noah's report,
not a probe. Sol and cursor's first-party models were the available lanes that
day.
