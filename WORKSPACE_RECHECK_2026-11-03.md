# The Twin workspace — independent recheck

**Later local orientation, 3 November:** This is the earlier 195-file audit and its observations are preserved below as a dated checkpoint. The later checker repair corrected the seven reported mechanical findings; the live Great Ape guidance and selected Chapter Seven facts `O098`/`O099` were subsequently reconciled. Other historical-branch fact questions and source-provenance limits remain open. Chapter 20 is now explicitly accepted, while Chapters 19, 21 and 22 remain unaccepted; see [OPEN](The%20Twin/OPEN.md), [HISTORY](The%20Twin/HISTORY.md) and the [workshop sync register](WORKSHOP_SYNC.md) for current scope. No new remote synchronization is implied.

**Date:** 3 November 2026  
**Result:** The files and backups are intact, but the continuity records are **not yet fully consistent**. I missed some of these contradictions in the previous repair. This is an audit, not a declaration that the writing or research has been approved.

## Issues that need attention

### 1. Great Ape direction is recorded inconsistently

The [Goshin status panel](The%20Twin/foundation/GOSHIN_STATUS_PANEL.md) and the register’s **Rules & Continuity** tab correctly record the later direction: Goshin’s first eventual Great Ape is aware and controlled from the start; fear of the form is not a mandatory cost. His bloodline and the form can develop, but those future applications are not present Chapter 17 feats.

Other live records still conflict with that direction:

- [STATUS.md §13](The%20Twin/STATUS.md) says the ape “costs him fear,” even though the preceding ladder table says there is no mandatory fear.
- [WRITING.md §9](The%20Twin/WRITING.md) says to write “the fear before the fur, every time.”
- [OPEN.md](The%20Twin/OPEN.md) OPEN-17 and OPEN-18 still describe fear wording or timing as unresolved, while OPEN-3 says the old mandatory-fear reading is superseded.
- In the [project register](https://docs.google.com/spreadsheets/d/1M0o391G21FJt2fMVKF7Ut_JnAjwevbkedbKARbG2Mq0/edit), **Decisions R-05** still calls the question open; **Rules & Continuity**, row 22, records the later correction.

The old phrasing should not override the later direction. Whether a particular scene contains ordinary fear is a separate creative choice, not a required loss of control or obligatory cost.

### 2. The fact ledger and Chapter 10 references mix branches

- In [canon/facts.json](The%20Twin/canon/facts.json), **O124–O129** describe the older adult-led Chapter 10, including passenger-only clearance and C-6’s uncertain awakening, yet are marked `active-draft` and described as current draft state. The selected Chapter 10 instead permits normal movement with symptom reporting, and the boys encounter C-6 under the riverbank. Later selected chapters have C-6 awake at Bulma’s lab.
- **O098**, also marked `active-draft`, describes Goshin copying a non-contact hold in an older Chapter 7; that particular event is not shown in the selected Chapter 7. Other earlier-branch rows should be reviewed individually: some details may overlap the selected branch, so they should not all be discarded as a group.
- [canon/RESEARCH.md](The%20Twin/canon/RESEARCH.md), episode-9 section, describes the old passenger-only and adult-led treatment without a nearby selected-branch warning. [OPEN.md](The%20Twin/OPEN.md) OPEN-17 calls the historical `SCENE_COVERAGE_009.md` a focused check of the new Chapter 10, although that coverage file explicitly warns that its treatment is the older branch.
- The checker’s rejected-draft pass does not resolve this: it tests rows already labeled `rejected-draft`; it does not identify old-branch claims incorrectly left `active-draft`.

The selected manuscripts, [timeline](The%20Twin/foundation/TIMELINE.md) and [world state](The%20Twin/foundation/WORLD_STATE.md) are the safer references for the current provisional branch. Reconciliation must preserve the historical evidence rather than silently rewriting the manuscripts.

### 3. Automated Twin checks still fail

`tools/check.py` reports **27 passes and 7 failure entries**:

- One grouped **source-card** failure: Chapters 6–14 lack the checker’s four fenced-card declarations; Chapter 15 lacks its `WITNESS:` line. Separate source and coverage notes exist, so this is not proof that no research exists.
- Six **band** findings: Chapter 6 is 3,721 words against the 4,400–6,600 target; average-sentence measurements for Chapters 6–9 and 15 fall below the configured 8-word threshold. These are automated heuristics, not a judgment that a particular sentence or draft is bad. Chapters 1–2 are evaluated under a separate legacy-length exception.

The three dedicated regression fixtures pass. In a temporary copy, all 13 focused mutation checks in `check.py --selftest` passed, but the self-test’s overall exit remains nonzero because the underlying project check has the seven findings. No chapter was edited to make a test pass.

### 4. Security follow-up remains unverified

A historical project audit records that credentials had previously appeared in conversation and that revocation was not verified. This recheck cannot establish whether they were later revoked. If that has not already been done, revoke or rotate the affected credentials through their providers without reposting them. A basic pattern scan of 118 local text/code files found no common token or private-key signatures; it is not an exhaustive secret scan and does not prove revocation.

## What was verified

- **Workspace and backup:** All **195 pre-audit working files** matched the downloaded [repaired Drive checkpoint](https://drive.google.com/file/d/1VAursK4gWI5_mraGNuRVkcxfnAXTedf5/view) byte-for-byte. Its SHA-256 remains `37d2a2b40815a492f5b8149e9a909b0a2768fbc3a95052f243bec0eeff5410d5`; Drive metadata shows it is not shared. The report you are reading was created after that checkpoint and is not in it.
- **Manuscripts:** Chapters 1–15 match the pre-cleanup source-verification hashes; selected Chapters 16–17 match their corresponding pre-cleanup recovery copies. The independent Twin seal check passed for **76 files**. Chapters 6–17 remain unaccepted review material.
- **Research:** All **109 restored references** were matched by SHA-256: 101 against downloaded source archives and eight Adaptation Talent files against the pinned public repository. The original research package’s own 11-item checksum list also passed.
- **Sara:** The original **86,020-byte** self-file is an exact prefix of the local file, with the repair lesson appended. The ledger checker reports 39 dated entries and no shape problems. It checks ledger shape, a minimum count and identity patterns—not the truth of every historical claim or remote synchronization.
- **Backups:** Six downloaded ZIP archives and the Black Clover tarball matched their recorded SHA-256 values. ZIP CRCs passed, including **23 nested ZIPs**; the Black Clover archive’s 54 regular files were read successfully. The pre-cleanup recovery manifest’s 82 records all matched its contents.
- **Reading copies:** The 15 individual Drive DOCX files and combined collection match their pre-cleanup verification hashes. Their normalized story body text was checked against the selected local Chapters 1–15; the combined copy contains the same chapter paragraphs, apart from the individual copies’ cover-status lines. There are no separate Drive reading documents for Chapters 16–17. Copies do not auto-sync.
- **Captions and indexing:** The Drive caption ZIP contains exactly episodes 001–291; all 16 local captions match it. Rebuilding the index in an isolated temporary directory reproduced the current index byte-for-byte. The incomplete-input guard left its test output untouched. Caption origin and exact cut remain unverified.
- **File structure and links:** All 195 pre-audit files were readable; text/JSON/JSONL/Python syntax and the two Office packages parsed, all 58 images decoded, and local SRT timestamp syntax passed. All 82 detected relative Markdown file links resolved. External URLs and in-page anchors were not comprehensively tested.
- **Remote state:** Public `dbz-twin` main is still `3de86b7f168dc7c20e7fdaa8dee661f03173124f` and differs from the local workshop. Sara’s public main is `040f3fcafbff8d361f8ffc11f6ebf56f9eb71bf1`, before the local appended lesson. No GitHub push or Drive content edit was made during this recheck.

## Scope limits

The local Sara folder contains the self-file and six supporting files, not all 32 files in the public Sara repository. The local Adaptation Talent reference set contains eight files, not all 58 files in its public repository. They are selected working subsets, not complete local clones.

This recheck did **not** reread every scene for literary quality, independently verify every external citation, or view complete source-episode video/audio. Structural checks and hashes establish identity and readability, not canon accuracy, character-rule compliance, literary quality or reader acceptance. Temporary audit downloads were removed after verification; the working manuscripts and reference files were not altered.
