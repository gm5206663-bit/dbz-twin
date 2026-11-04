# Source, provenance and preservation ledger

**Audit date:** 1 November 2026. This ledger is outside the sealed story project. It describes what was actually done; where the prior project reported earlier work, it says so rather than presenting it as a new viewing.

## 1. What was examined in this pass

| Item | Actual examination | Limits |
|---|---|---|
| Chapters 1–10 | All ten current chapter bodies read, compared with project history/rules and scene coverage. | Revised 1–3 and draft 4–9 are not automatically user-approved; 10 was rejected. |
| Story rules/history | Read `STATUS.md`, `WRITING.md`, `RULES.md`, `HISTORY.md`, `OPEN.md`, `REVISION_2026-11-01.md`, `CRAFT.md`, source/coverage ledgers and relevant character/canon notes. | Earlier assistant-authored craft formulas are not necessarily user commands. Chapter 3’s camera ruling is documented as local to that chapter. |
| Z official ep. 1–35 | Retrieved and read all 35 short Toei Japanese synopses; compared them to current chapters and future hooks. | A synopsis is only a brief publisher description; it does not establish complete dialogue, timing, or silent blocking. |
| Z ep. 9 and 10 captions | Personally reread both local Japanese SRT files through the whole relevant story, previews and later material; compared with multiple outside guides. | Unknown original subtitle provider/broadcast cut; speaker labels are incomplete. Captions are not footage. The 29-minute automated cutoff is a heuristic, not certification. |
| Z ep. 1–8 coverage | Read the existing detailed coverage notes and checked their claims against identified evidence. | These records preserve prior caption reads and secondary visual accounts; they are not fresh full-video watches in this pass. |
| Selected official stills | Five single official promotional stills examined for Z 1, 2, 3, 8 and 9. | A still establishes only its own frame, not an entire scene or action order. The file named `toei_dbz_ep_008_official_still.jpg` contains PNG data despite its extension. |
| Original DB / Z / GT / 2015 Super episode index | Automated retrieval attempted 604 additional official Toei episode pages and stored 601 successful short-synopsis records, in addition to the 35 above. Titles and links checked programmatically; exceptions inspected. | **Indexing is not individually reading every synopsis, much less watching 639 episodes.** The 3 special cases are documented in `sources/INDEX_EXCEPTIONS.md`; Super 109’s combined summary covers 110. |
| DAIMA | Read official premise and distributor episode listings; 11–20 individual distributor pages fetched; series lists all 20. | Promotional blurbs/listings only. No episode video reviewed. Distributor states Japanese video availability is Japan-only. |
| Franchise, manga, films and later material | Read selected official chronology, character profiles, announcements, official episode/film-related pages and independent guides; mapped 21 theatrical films individually. | No complete films or manga series were watched/read in this pass; an issue flag is not proof that a complete film has been compared. |

The earlier project’s `canon/episodes.json` reports indexed SRTs for all 291 Z episodes, full spoken-caption reads for 1–36, 49, 55, 59, 61, 65, 79–83, 183–184, 205–208 and 256–257. Those are **historical project assertions**, not a claim that every one was reread during this pass. The index itself identifies its SRT redistribution through Kitsunekko and says official/broadcast origin is unverified. Scripted searches and on-page coverage do not establish video viewing.

## 2. Where to find the evidence

- Existing scene and source records: `dbz-twin/canon/SCENE_COVERAGE_001.md`, `SCENE_COVERAGE_002_003.md`, `SCENE_COVERAGE_004.md`–`009.md`, `canon/RESEARCH.md`, `canon/episodes.json`, `canon/facts.json`, `canon/techniques.json`. The `009` comparison concerns the rejected draft and must not be treated as accepted continuity.
- This audit’s 35 official summaries: `sources/toei_saiyan_ep_001_035_official_synopses.json`; all other fetched official summaries: `sources/toei_franchise_official_synopses.jsonl`. These are raw source caches, not reviewed full-episode inventories.
- This audit’s visible comparison: `03_EPISODE_BEAT_COMPARISON.md`; film/version register: `04_FRANCHISE_AND_FILM_MAP.md`; extracted-page caveats: `sources/INDEX_EXCEPTIONS.md`.
- Local directly reread SRTs: `/home/user/tmp/subs/ex/Dragon_Ball_Z_009.srt` and `Dragon_Ball_Z_010.srt`. They are working source copies, not authenticated releases.
- Current project SHA-256 baseline: `audit/ORIGINAL_PROJECT_SHA256.txt` (41 original files, hashes recorded before research). Verification is repeated at packaging time.

## 3. Source confidence and attribution rules

1. **Primary complete episode/film:** a specific release/video actually watched, with version and relevant timecodes noted. None was watched in this pass.
2. **Primary text or still:** an official synopsis, profile, announcement, single still, or a verified manga page. Establishes what that particular item says/shows, not the entire episode. Selected official items were read here; no full manga-page pass was completed.
3. **Local captions:** useful direct evidence of captioned dialogue, narration and labelled audio, with origin/cut explicitly unverified. Do not derive exact movement, gaze, injury side, species or a speaker from an unlabelled line solely from captions.
4. **Secondary synopsis/rewatch:** useful for visual possibilities and context, but report it as secondary, particularly where accounts conflict. A duplicated text is not two independent confirmations.
5. **AU / invented bridge:** an authored route, reaction, number or object. It may be a good idea, but is neither source fact nor a user instruction.
6. **User ruling:** record the exact scope and do not overwrite it with an author preference or a mechanical score. Where history does not prove that a preference was withdrawn, ask rather than silently withdrawing it.

## 4. Important source disagreements and unresolved questions

- **Episode 9 bird:** rewatch A [5](https://animangatravelogue.weebly.com/home/dragon-ball-z-episode-9-sorry-robot-san-the-desert-of-vanishing-tears) says the eagle grabs Gohan; [rewatch B](http://dragonballanime.com/archives/629) describes different staging. The SRT labels an eagle’s call but does not settle the physical interaction. Obtain primary footage before resolving it.
- **Episode 9 broadcaster page:** Tokyo MX’s story paragraph is textually identical to Toei’s official story paragraph. This is not independent confirmation of a visually disputed detail.
- **Episode 9 duration:** the local Japanese caption at 18:54–18:59 says the robot has been buried for **80 years**. The JustWatch India listing [4](https://www.justwatch.com/in/tv-show/dragon-ball-z/season-1) instead says “over 30 years” and calls it a Capsule Corp robot. It may reflect a different localization or inaccurate metadata; no English-dub audio was checked. Do not reconcile by inventing facts.
- **Episode 10 dinosaur:** local captions label chewing; independent recaps report that the herbivore is eaten and Gohan sees its remains. The latter is visual, secondary evidence here until footage is checked.
- **Episode 4 scan:** 1,020 is spoken in the SRT but the caption does not establish the on-screen scouter target; the existing attribution to Piccolo draws on another version. Check anime footage.
- **Film and anime conflict:** Kanzenshuu’s analysis [2](https://www.kanzenshuu.com/episode/filler-plothole/) explains how *Dead Zone*, early Z introductions and the later Garlic Jr. arc do not fit without qualification. Read/watch the individual works before selecting a remedy.
- **Future Saiyan/ape designs:** separate project-specific instructions from GT and DAIMA mechanics; reconcile the existing note about being at home in ape form with the separate childhood fear note when the moment matters.
- **Digital access:** the India streaming listing [4](https://www.justwatch.com/in/tv-show/dragon-ball-z/season-1) lists Crunchyroll and Netflix for Z season 1. Availability and editions can change, and this research pass did not log in, access the streams, or verify any provider’s exact cut. A lawful accessible video or reader-supplied screenshots would permit visual checks where the environment can process them; a platform listing is not a viewing.

## 5. Selected navigational sources

| Source | What it supports | Not established by it |
|---|---|---|
| Toei Z 1–35, for example [episode 9](https://lineup.toei-anim.co.jp/ja/tv/dragonz/episode/9/) and [episode 10](https://lineup.toei-anim.co.jp/ja/tv/dragonz/episode/10/) | Brief official episode premises. | Full timing, dialogue, footage or every ending. |
| [Official franchise history](https://en.dragon-ball-official.com/about/dragon_ball_history.html) | Release chronology and series/film identification. | A single in-world chronology for every film. |
| Official manga-based profiles of Gohan [1](https://en.dragon-ball-official.com/news/01_503.html), Piccolo [6](https://en.dragon-ball-official.com/news/01_1178.html), Chi-Chi [1](https://en.dragon-ball-official.com/news/01_1412.html), and Krillin [1](https://en.dragon-ball-official.com/news/01_371.html) | Selected character motivations/relationships and context. | Exact anime silent staging. |
| Original Super arc guide [1](https://www.kanzenshuu.com/episode/super/) and [GT guide](https://www.kanzenshuu.com/episode/gt/) | Secondary navigation/arc ranges. | Complete watch-through or user approval of later continuity. |
| [Official DAIMA premise](https://dragonballdaima.com/) and [20-episode distributor list](https://www.videx.jp/detail/anime/v_a_toeianimation/atoa0483_0000/index.htm) | Series premise and episode availability list. | Viewing of the series or a settled branch order. |
| Official Super: Beerus report [1](https://en.dragon-ball-official.com/news/01_4515.html) | Japanese broadcast began 11 October 2026. | Every episode’s content or the day’s unverified broadcast. |
| Official Galactic Patrol announcement [1](https://en.dragon-ball-official.com/news/01_3974.html) | In production; involves Moro. | A release date or full series review. |
| Broly theatrical-program translation [3](https://www.kanzenshuu.com/translations/dbs-broly-theatrical-program-naohiro-shintani-2/) | Designer describes the 2018 portrayal as a different character. | An automatic decision about adapting the old films. |

## 6. Preservation and acceptance

- **No story rebuild was performed.** Research documents and caches were written only under the separate `Twin_Rebuild_Research_2026-11-01` directory.
- The original 41-file living project was hashed before this pass. `sha256sum -c` subsequently passed for all 41 files, and the file count was still 41. A final packaging-time check should repeat this.
- Previous pre-revision project versions exist in `/home/user/Pre_Revision_Project_2026-11-01.zip` and `/home/user/tmp/pre_approved_revision_2026-11-01/`. Their old chapter hashes are recorded in the proposal/audit context; those are preservation references, not assertions of user acceptance.
- The prior Drive snapshot and public GitHub `main` still contain Chapter 10 with a provisional label. They predate the user’s rejection; they were not edited, relabeled or pushed during this audit. A separate user authorization is needed before changing those copies.
- Rejected Chapter 10 and authored entries `O124`–`O129` remain preserved as history, **not accepted facts**. Its robot encounter and adult/radio rescue must not quietly seed the next draft.
- Any candidate must be built in a separate location and offered for review before replacing story, manifest, Drive or GitHub copies. User approval of a plan is not automatic approval of a chapter.
