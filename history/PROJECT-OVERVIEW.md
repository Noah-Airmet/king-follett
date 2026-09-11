Project: King Follett Discourse (KFD) Digital Critical Edition
1. Project Objective
To create a scholarly "Linear Side-by-Side" tool that reconstructs the King Follett Discourse from four primary eyewitness accounts. The tool will feature a Synoptic Viewer (parallel accounts) and a Digital Critical Apparatus (notating textual variants).

2. Directory Structure
Plaintext
/kfd-scholar/
├── PROJECT_OVERVIEW.md    <-- (This file)
├── transcripts/           <-- (Primary Data)
│   ├── woodruff.md        (Siglum: W)
│   ├── bullock.md         (Siglum: B)
│   ├── richards.md        (Siglum: R)
│   └── clayton.md         (Siglum: C)
├── images/                <-- (Ground Truth)
│   ├── woodruff-jpgs/
│   ├── bullock-jpgs/
│   ├── richards-jpgs/
│   └── clayton-jpgs/
├── app/                   <-- (Proposed Web Tool)
└── data/                  <-- (Generated Collation Files)
    ├── collation_map.json
    └── base_text.md       (The reconstructed Lemma)

3. Workflow Definitions
Phase 1: Text Normalization & Alignment
Action: Verify that .md transcripts are clean. Original line breaks have been removed but paragraph breaks remain.

Goal: Create a "fuzzy alignment" where the AI identifies which paragraphs in woodruff.md correspond to the same moments in bullock.md.

Phase 2: Automated Collation (The Apparatus Engine)
Action: Using Claude Code, perform a word-level "diff" analysis across all four witnesses against a "Base Text" (The History of the Church version or the Bullock account).

Technical Requirement: Generate a collation_map.json that stores:

lemma: The word/phrase in the base text.

witnesses: The specific variants found in W, B, R, and C.

location: Pointer to the specific line/paragraph.

Phase 3: Vision-Assisted Verification
Action: When the AI identifies a "Critical Variant" (a difference that changes the meaning, e.g., "Gods" vs. "God"), it should flag the entry.

Human-in-the-loop: The user will provide the specific .jpg from the image folders to Gemini/Claude to verify if the transcript accurately reflects the handwriting.

4. UI/UX Vision: Needs to be in a Google Doc (or Google Sheet)
Top Pane: The "Reconstructed" readable text.

Middle Pane: Four columns (W, B, R, C) that scroll in sync.

Bottom Pane: The Critical Apparatus. If a user clicks a word in the top pane, the bottom pane displays:

dwell on an earth ] B; was once a man W; was as one of us C; om. R.

5. Instructions for AI Agent
Analyze the four files in /transcripts/ to determine the total word count and structural similarities.

Suggest which account should serve as the "Base Text" (Lemma) based on completeness.

Create a Python script to begin the alignment process.

Reference the /images/ directories only when a textual conflict is found that requires visual verification of the original manuscript.