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
