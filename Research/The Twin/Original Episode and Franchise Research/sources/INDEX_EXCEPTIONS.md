# Official-series index: completeness and exceptions

As of 1 November 2026. The fetcher requested 604 Toei pages outside Z 1–35 and wrote one record per requested episode to `toei_franchise_official_synopses.jsonl`. **601 records contain a title and short Japanese synopsis; three did not pass the extractor.** The separate Z 1–35 file contains 35 more successful Toei synopsis records. Thus there are **636 fetched official synopsis pages**, not 639 separately available episode summaries and not 636 episodes watched or independently reviewed.

| Series | Requested slots | Extracted individual Toei synopsis pages | Exception |
|---|---:|---:|---|
| Dragon Ball | 153 | 153 | None detected by the extractor. |
| Dragon Ball Z | 291 | 289 | Episodes 189 and 209 have official page titles and stills but no synopsis text visible on the fetched pages. |
| Dragon Ball GT | 64 | 64 | None detected by the extractor. |
| Dragon Ball Super, 2015–2018 | 131 | 130 | Episode 110 is covered by the official combined 109/110 special page, not a distinct extracted 110 page. |
| **Total** | **639** | **636** | Two title-only Z pages; one separately absent Super page paired with 109. |

### Z 189 and 209

- Toei [Z 189](https://lineup.toei-anim.co.jp/ja/tv/dragonz/episode/189/) exposes the title and a still, but the fetched page contains no synopsis. A separate episode synopsis exists in the [secondary 189 guide](https://www.kanzenshuu.com/episode/dbz/eps-189/) [1](https://www.kanzenshuu.com/episode/dbz/eps-189/). Its summary is secondary evidence, not missing Toei text.
- Toei [Z 209](https://lineup.toei-anim.co.jp/ja/tv/dragonz/episode/209/) likewise exposes the title and a still only. The [secondary 209 guide](https://www.kanzenshuu.com/episode/dbz/eps-209/) [1](https://www.kanzenshuu.com/episode/dbz/eps-209/) has a synopsis; treat it as secondary.

### Super 109/110

- The requested `.../episode/110/` redirected to Toei’s general Japanese lineup page. However, [Toei’s episode 109 page](https://lineup.toei-anim.co.jp/ja/tv/dragon_super/episode/109/) explicitly labels the special as **episodes 109 and 110** and has one combined synopsis. Its page is already indexed once as episode 109.
- For the distinct 110 title and another secondary account, see [Kanzenshuu’s episode 110 page](https://www.kanzenshuu.com/wiki/Dragon_Ball_Super_Episode_110) [2](https://www.kanzenshuu.com/wiki/Dragon_Ball_Super_Episode_110). Do not mistake the combined listing for evidence of every separate scene.

### DAIMA

DAIMA’s 20 episode listings are separate from the 639 Toei page slots above. A distributor’s [series listing](https://www.videx.jp/detail/anime/v_a_toeianimation/atoa0483_0000/index.htm) reports all 20 episodes and displays 1–10. Its [episode 14 page](https://www.videx.jp/detail/anime/v_a_toeianimation/atoa0483_0014/index.htm) also displays the titles and short Japanese blurbs for episodes 11–20. Individual 11–20 pages were fetched. The listing says the video itself is available only in Japan; a readable page or blurb is **not** viewing an episode. No DAIMA episode footage was watched.

### Quality limits

- A successful response only means a nonempty title and synopsis were parsed, and the requested number matched the title on a sampled automated check. It does **not** establish that the story summary is error-free, complete, locally available video, or a true scene-level inventory.
- The fetcher skips a number already present in its output even if that record is an exception. Do not rerun it unchanged and claim the three gaps were fixed.
- The supplemental spreadsheet’s English title column, if present, is machine translation for navigation and is **not an official localization or a trusted translation**. Check the linked Japanese original and a human translation before relying on wording.
