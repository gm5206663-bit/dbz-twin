# THE TWIN — Dragon Ball Z

**Son Goshin** is Goku and Chi-Chi's twin son alongside Gohan. Raditz takes both. The Japanese Z anime is the baseline; manga, guidebooks, movies and later series are identified separately. Canon is a floor for the world, not a track that forces unchanged outcomes.

## Start here

- **`canon/RESEARCH.md`** — the deep research report: hybrid potential, growth, Namek recovery, scouters, training, tails, the Dragon Balls, later arcs and a transparent correction log.
- **`canon/SAGAS.md`** — the 291-episode navigation map and source cautions.
- **`CANON.md` / `canon/facts.json`** — witness registry, fact rows, source tiers and corrections.
- **`STATUS.md`** — Goshin's design, standing capability rule, growth and the separately ruled future god progression.
- **`STORY.md`** — world and continuity laws, the current state and moment-specific readings.
- **`WRITING.md`** — anime episode form, action clarity, names, supernatural flow and scale.
- **`CRAFT.md`** — three non-canon examples with plain-word descriptions and action.
- **`RULES.md` / `OPEN.md` / `HISTORY.md`** — the gate, decisions and the dated record.
- **`chapters/`** — Chapters One–Three are user-authorized targeted revisions of previously accepted bodies, presented for review rather than automatically re-accepted. Their original bodies and hashes are preserved in the pre-revision snapshot. The five earlier island supplements are now integrated into Chapter Two; `Restored_Chapter_Two_Island_Moments.md` is historical, not a second occurrence. Chapters Four–Ten remain provisional, including the earlier local continuity and instruction repairs.
- **`canon/episodes.json`** — the 291-file search index; **not** a complete reading of each episode.
- **`canon/SCENE_COVERAGE_001.md`** — retrospective episode-1 ordered inventory, hat and forest gaps, and source limits.
- **`AUDIT_2026-11-01.md`** — the historical project-wide audit as of its original pass; see the later implementation report for what changed.
- **`REVISION_2026-11-01.md`** — authorization, exact scope, review status, preserved original hashes and remaining limits of the implemented repair.
- **`canon/SCENE_COVERAGE_002_003.md`** — ordered source-scene coverage for the corrected abduction and rescue, including authored changes and visual-evidence limits.
- **`canon/SCENE_COVERAGE_004.md`** — episode-4 beat inventory, draft coverage, the changed tail escape and the already-accepted Chi-Chi overlap.
- **`canon/SCENE_COVERAGE_005.md`** — episode-5 ordered inventory, two-boy causality, the changed outcome, later scouter beat moved earlier, home overlap and evidence limits.
- **`canon/SCENE_COVERAGE_006.md`** — episode-6 source-order inventory, the crater confrontation, Kame House telling, Senzu trip and Otherworld divergence, with evidence limits.
- **`canon/SCENE_COVERAGE_007.md`** — episode-7 source-order inventory and causal treatment: reunion, care, Kami, Piccolo, Baba, family decisions and displaced wilderness beats.
- **`canon/SCENE_COVERAGE_008.md`** — episode-8 caption baseline, secondary visual reports, moon/source-order issue and Chapter Nine divergences.
- **`canon/SCENE_COVERAGE_009.md`** — episode-9 source-order inventory, secondary visual reports, Chapter Ten divergences and focused character-rule review.
- **`canon/techniques.json`** — technique register.
- **`tools/index_eps.py`** — rebuilds the bounded caption search index.
- **`tools/check.py`** — mechanical checks and self-test; green does not independently verify canon.
- **`tools/check_revision.py`** — focused regression checks for the approved revision and dependent handoffs; not a semantic or video certification.
- **`tools/check_chapter_10.py`** — Chapter Ten's selected rule/continuity anchors and mutation self-test; not a semantic or video certification.
- **`tools/seal.py`** — reseals reviewed changes to the living docset; a seal is integrity, not acceptance.

## Source and reading status

All 291 Japanese SRT files were indexed and searched. Full spoken-caption reads cover **1–36, 49, 55, 59, 61, 65, 79–83, 183–184, 205–208, 256–257**; episodes 1 and 4–9 were reread for inventories and audit. Other episodes were read only in selected passages. Some files contain unrelated material after the DBZ ending; the index already uses a 29-minute heuristic, which is not a verified episode boundary. The files were redistributed through Kitsunekko; their broadcaster/official provenance has not been independently verified. Caption dialogue is provisionally Tier I. Selected episode-3 fan-gallery stills of the pickup and the Nimbus journey were inspected; their release is unverified. Episode-4–9 visuals are supported by secondary synopses and reports, not complete checked video; one episode-5 report was available only as search snippets. Read each episode fully and identify the remaining visual gaps before writing its scenes.

## Standing creative direction

Senzu fully heal battle injuries and restore strength: Goku and Gohan each ate one and are completely restored. Goshin refused the third because he did not watch it being made; he alone remains injured (`O103`).

Goshin's Kame House scan of **~400** is one authored snapshot, not a lasting level. For this abduction the user rules that Raditz cannot take Goshin conscious: the corrected draft shows an earned knockout first and a changed fight after he wakes (`O080`). His first Kamehameha has more raw ki than Goku's wave in that scene, but less practiced control; the separate **1,450** scan is an authored snapshot, not a canon value or ceiling (`O088`). His later **1,500** surge in Chapter Six is another authored moment, not the same reading or a cap (`O089`). Both brothers grow. The authored rule is that Goshin is never less capable than Gohan; this is not a canon equation and does not automatically set his rank against everyone else. He flies, uses techniques and learns visibly. His deliberate training masters or perfects what he already has before pursuing new abilities, with serious foundational work; instinctive emergency copying remains allowed (`O104`, `O105`). Fatigue, suppression and injuries can lower performance without erasing skills. Fight damage follows feats and context, not arithmetic on a printed number. No god ki in the current Z era; the user's separately ruled future god progression remains intact.

## Checks

```bash
# Review intentional changes before resealing; a seal is not acceptance.
python3 tools/seal.py
python3 tools/check.py
python3 tools/check.py --selftest
python3 tools/check_revision.py --selftest
python3 tools/check_chapter_10.py --selftest
```

Accepted work is never silently rewritten. On 1 November the user explicitly authorized the targeted proposal, including the same-day timeline. Chapters One–Three now contain the resulting revisions, with prior versions retained in the workspace snapshot; the implementation remains for reader review. Chapter Four continues the same island fight and preserves the earned knockout. The same school paper, Ox-King visit and unanswered call are shared overlaps; Roshi calls promptly afterward. `W-65` is secondary visual evidence, not checked episode footage. Chapters Four–Ten are still provisional, and a wider line-by-line character-rule review remains open (`OPEN-17`).

Drive, GitHub, bundles and ZIPs are snapshots, not automatic synchronization. Earlier snapshots exist both from before Chapter Five and from the revised project through Chapter Nine; inspect a backup's actual version before relying on it.
