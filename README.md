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
- **`chapters/`** — three accepted chapters; `Restored_Chapter_Two_Island_Moments.md` supplies five explicitly placed narrative passages without silently rewriting the accepted body; the revised Chapter Four draft, **The Rescue**, follows the abduction through episode 3's opening fight.
- **`canon/episodes.json`** — the 291-file search index; **not** a complete reading of each episode.
- **`canon/SCENE_COVERAGE_002_003.md`** — ordered source-scene coverage for the corrected abduction and rescue, including authored changes and visual-evidence limits.
- **`canon/techniques.json`** — technique register.
- **`tools/index_eps.py`** — rebuilds the bounded caption search index.
- **`tools/check.py`** — mechanical checks and self-test; green does not independently verify canon.

## Source and reading status

All 291 Japanese SRT files were indexed and searched. Full spoken-caption reads cover **1–36, 49, 55, 59, 61, 65, 79–83, 183–184, 205–208, 256–257**. Other episodes were read only in selected passages. The files were redistributed through Kitsunekko; their broadcaster/official provenance has not been independently verified. Caption dialogue is provisionally Tier I. Selected episode-3 fan-gallery stills of the pickup and the Nimbus journey were inspected; their release is unverified, and the full video was not examined. Read each episode fully and identify the remaining visual gaps before writing its scenes.

## Standing creative direction

Goshin's Kame House scan of **~400** is one authored snapshot, not a lasting level. For this abduction the user rules that Raditz cannot take Goshin conscious: the corrected draft shows an earned knockout first and a changed fight after he wakes (`O080`). Both brothers grow. The authored rule is that Goshin is never less capable than Gohan; this is not a canon equation and does not automatically set his rank against everyone else. He flies, uses techniques and learns visibly. Fatigue, suppression and injuries can lower performance without erasing skills. Fight damage follows feats and context, not arithmetic on a printed number. No god ki in the current Z era; the user's separately ruled future god progression remains intact.

## Checks

```bash
python3 tools/check.py
# after intentional edits: reseal the living files, then run the check again
python3 tools/check.py --selftest
```

Accepted chapters are not silently rewritten. Chapter Two's conscious-capture passage is explicitly superseded in its footer and replaced by the full island fight at the start of Chapter Four; its supplemental scenes restore missed moments but do not fix every source-order issue in the older body. Chapter One's misplaced Raditz line and unverified city insert, and Chapter Three's date/time treatment and anticipatory Snake Way/wilderness narration, are explicit revision debts. Chapter Three's mountain thread overlaps and extends beyond the episode-3 rescue; its episode-7 preview does not authorize skipping or forcing the fight.
