# RULES — the gate, the pass, and what failure taught

**Owns: what "done" means.**

---

## 1 · The gate — a chapter is done when all of these are true

| # | Gate | Fails when |
|---|---|---|
| 1 | **Card** | no `ANIME BASE: ep. N`; or the chapter stops short of the episode it claims |
| 2 | **Canon** | a detail has no `C-` or `O-` row; or contradicts its row |
| 3 | **Order** | the sourced baseline is misrepresented, or a divergence lacks a causal explanation |
| 4 | **Information** | someone knows something with no path to knowing it |
| 5 | **Name** | "Broc" appears before Raditz says it |
| 6 | **Staging** | authored material is used but not declared |
| 7 | **Y6** | a scene centred on him adds no meaningful role; scenes without him may show consequences |
| 8 | **Price** | unlimited energy without context; violence without a relevant aftermath |
| 9 | **Scale** | an unsourced/undeclared reading, static 400, or collateral treated as a fixed number conversion |
| 10 | **Style** | the band in `WRITING §2` — under-styled fails too |
| 11 | **Direction** | the action or episode structure is not followable |
| 12 | **Voice** | a character outside their voice law or into their never-list |

**Hard fails, no repair in the same pass:** a chapter with no card · a fact from memory · an averaged detail · "Broc" too early · a time-lapse over a pivotal beat · writing Goshin as less capable than Gohan, treating Gohan as incapable of growth, or forcing an unchanged canon outcome despite the divergence.

---

## 2 · The pass

```
1. identify episode boundaries     exclude unrelated post-episode cues; index cutoff is only heuristic
2. read that episode in full       captions + any available primary video; note visual/provenance gaps
3. inventory in source order        identify retained, altered, already shown and deferred beats
4. write                            chapters/
5. check                            python3 tools/check.py
6. update everything that moved     STORY §4 · HISTORY · facts.json · coverage
7. reseal                           MANIFEST.sha256
```

**The unit of work is the pass, not the file.** Truth runs canon → STORY/RULES/WRITING → prose, never backwards: **a chapter may not teach canon.** If prose needs a fact no row holds, go back to the fetch.

**Post-draft synchronization, including review drafts:** update the actual selected-branch foundation, timeline, relationships, status panel or status delta, world/knowledge/inventory, relevant source coverage and facts, open threads, history, existing hub/register and workshop pointers in the same pass. Label unaccepted work clearly; do not replace old manuscripts or claim approval. Review remote edits before synchronizing and verify an appropriately dated backup. No process auto-syncs. If a check fails, preserve the failure and its scope rather than manufacturing a green result.

**What must move together:**

| If this changes | These move with it |
|---|---|
| a fact row | CANON §4/§6 · the chapter that spends it · STORY §4 if it is where he is |
| a grade | the row · the chapter's card |
| a correction | CANON §7 · every file that stated it — **struck in place, with the date** |
| a ruling | OPEN.md (dated) · STORY or RULES if it is a law |
| a chapter accepted | HISTORY · STORY §4 · RULES green · reseal |

---

## 3 · The ten things failure taught

| # | Rule | Held by |
|---|---|---|
| L-01 | **A summary is not a witness.** Go to the record of the work itself. | `check_facts` checks registered witnesses; source review is still necessary |
| L-02 | **Independence is by publisher.** Two copies are one witness. | CANON §2 groups |
| L-03 | **Evidence has a scope and a provenance limit.** | card and source rows declare provisional caption dialogue versus unverified visuals |
| L-04 | **A plan is not an arrival.** | CANON §7, R-03/R-04/R-09 |
| L-05 | **Not in the record → not in the prose**, unless declared authored. | `check_cards` verifies that a staging field exists, not that its content is true |
| L-06 | **Never average.** Record the contest, rule it, keep the ruling. | CANON §5 |
| L-07 | **A change is not made until every dependent file is changed in the same pass.** | the matrix above |
| L-08 | **A citation to a row that does not exist is a broken promise.** | `check_citations` |
| L-09 | **One owner per fact, said on the file's first line.** | `check_owners` |
| L-10 | **Counts are printed, never written.** | `check.py` prints them; prose must not state them |

**Rule about rules:** automate structural failures when possible; factual accuracy, scene clarity and source provenance still require a human/source review. A green script is not a canon proof.


## 4 · Growth continuity — manual check before and after writing

The author has emphasized that Goshin's growth, not merely the names of his powers, must be handled carefully. For any scene or chapter in which his ability, training, fighting, recovery or elapsed time matters, compare the actual manuscripts with `STATUS §9`, the [holder module](foundation/ADAPTATION_MODULE.md), the [status panel](foundation/GOSHIN_STATUS_PANEL.md), the [adaptation log](foundation/ADAPTATION_LOG.md) and the latest author directions. A summary or a green script is not a substitute for this comparison.

1. **Start from what he has already become.** Identify earlier established abilities, their real conditions and any consolidated gains; do not reset him to an old reading, or treat a deliberately small demonstration as his maximum. Separate accepted chapters from the selected unaccepted branch.
2. **Count the time and causes.** Check what training, combat, ordinary life, rest, recovery and relevant environmental exposure have actually occurred. His whole-being Talent and Saiyan inheritance can develop together, with especially rapid and substantial growth possible in battle. The author-directed chamber stay is one full lived year *inside*, with about a day outside; the Chapter 18 mental experience is different (`O155`). It is staged in unaccepted Chapter 22, not in Chapters 18–21 or the accepted Chapter 20. Carry its consequences in a Chapter 22 continuation and still honor its proximity to the future Saiyan arrival.
3. **Carry and show consequences.** Consider strength, speed, ki, recovery, senses, instincts, technique, inherited traits and applicable transformations as the author and circumstances support. Earlier gains inform later performance; a temporary injury, suppression or fatigue is not automatic erasure. After meaningful development, show its consequences in what he can do, not only in a smaller repeat of an old feat. A practice scene may repeat an exercise; this is not a demand for a new power every scene or a fixed numerical progression.
4. **Check everyone fairly.** Gohan retains his own agency and growth, while Goshin remains never less capable than Gohan (`O056`). Do not weaken either boy, invent a ceiling or force unchanged canon outcomes for convenience.
5. **Record what the story actually supports.** Distinguish demonstrated performance, a current but unmeasured capacity, author-directed future growth and possibilities not yet acquired. Do not retroactively invent an event, multiplier, near-death recovery or transformation; a new development can be written when supported by the story and directions. Update the relevant status/log after the draft and preserve previous versions. Apply the author's current correction request to the chapters it actually concerns; an earlier one-time hold is not a permanent blanket ban, and a revised version is not automatically accepted.

**Current world-scale direction (`O214`, `O225`):** Present ordinary-bodied Goshin can destroy Earth. Earlier Moon-destroying source fighters and Vegeta’s planet-threatening attack establish context, not a new scouter conversion; the Moon remains intact in this branch. The author places original-Dragon-Ball Goku at light speed or above as the project’s working interpretation. Write extraordinary speed and planetary capacity into consequences where relevant without inventing an official exact speed, an obligatory maximum in every movement, or a fixed multiplier. Control, injury and small tasks do not erase the scale.

**Output, technique and development are distinct (`O188`).** A fighter may release more ki already possessed, or concentrate a technique, without permanently acquiring new capacity. A scouter reads the output at that moment; it cannot by itself distinguish stored power from new growth. Actual growth—including Goshin's very rapid, substantial battle adaptation—remains possible. Anger and being pushed hard are examples, not requirements: do not invent mandatory triggers, a fixed rate, a numerical ceiling or a rule that only extreme situations allow growth. Apply character, story and context rather than automatically awarding a permanent gain for every ordinary action.

**Known example, revised at the author's request:** the prior Chapter 21 repeated four-pebble-plus-wave work from Chapters 15 and 19 without clearly showing Goshin's progress. The unaccepted revision now gives him an in-fight increase in strength and ki and a stronger controlled wave at the same marked bank after further practice. The revision, not a checklist, is for the author to judge. The pre-correction Chapter 20 remains accepted; its selected corrected version awaits review.

**Current author-directed scaling example:** The former Chapter 23 made Goshin winded against this era's Piccolo after the boys' full additional chamber year. The author rejected that portrayal; the selected correction shows both brothers comfortably outclass him in an ordinary spar while holding back. Goshin uses speed and ki already developed rather than gaining permanent power from that easy exchange. Chapter 24 carries their accumulated power into Nappa's defeat in the city exchange, gives Gohan independent action and shows both Saiyans reacting tactically. Its higher readings show release and technique concentration, not a fresh permanent gain from one wave or a slab lift. A large observed gap must affect the action; no fixed damage equation, universal ranking, maximum or predetermined final Saiyan outcome follows (`O170`, `O181`, `O182`, `O187`, `O188`).

**Appearance is a separate continuity check.** Goshin's near-likeness to Goku—including face and black spiked hair—with Chi-Chi's eyes is an authored design, not an optional behavioural tell (`O003`, `STATUS §1`). Carry his tail, clothing and physical condition through the actual scenes. Integrate the appearance naturally when useful, without inventing a fixed costume, an unspecified eye colour, a new form or the visual effect of a future year. Keep earlier versions recoverable, and follow the actual scope of the author's current directions rather than a blanket freeze.
