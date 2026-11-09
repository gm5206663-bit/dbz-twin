#!/usr/bin/env python3
"""The audit for THE TWIN. Arithmetic, not taste.

Exit 0 = clean. Exit 1 = a list of what is wrong.
Self-test: python3 tools/check.py --selftest   (proves it still fails a dirty tree)
"""
import json, re, sys, hashlib, pathlib, tempfile, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
P, F = [], []

def ok(m):  P.append(m)
def bad(m): F.append(m)
def read(p): return (ROOT / p).read_text(encoding="utf-8")

# Both chapter formats occur in the selected manuscript. Match an actual
# heading, not the words "## Footer" inside a sentence or a fenced example.
# Keeping newlines when masking fences/comments preserves diagnostic line
# numbers. These are structural boundaries, not a judgment of story quality.
FOOTER_HEADING = re.compile(
    r"^[ \t]{0,3}(?:##[ \t]+Footer|###[ \t]+Continuity and source note)"
    r"[ \t]*#*[ \t]*$", re.I
)
FENCE_LINE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")


def _mask_nonprose(text):
    """Hide text while preserving offsets and line breaks for diagnostics."""
    return "".join(c if c in "\r\n" else " " for c in text)


def chapter_prose(text):
    """Return visible story-side text, excluding notes, fences and comments.

    Visible footer headings terminate prose. Older hidden footers are HTML
    comments and are masked, as are unfinished comments through end of file.
    Comment and fence examples cannot hide later visible story. Masking keeps
    offsets and line numbers intact for the focused diagnostics and self-test.
    """
    result = []
    fence_char = None
    fence_size = 0
    in_comment = False
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        marker = FENCE_LINE.fullmatch(content)
        if fence_char is not None:
            if (marker and marker.group(1)[0] == fence_char
                    and len(marker.group(1)) >= fence_size and not marker.group(2).strip()):
                fence_char = None
            result.append(_mask_nonprose(line))
            continue
        if (not in_comment and marker
                and not (marker.group(1)[0] == "`" and "`" in marker.group(2))):
            fence_char = marker.group(1)[0]
            fence_size = len(marker.group(1))
            result.append(_mask_nonprose(line))
            continue

        # Read comment delimiters only outside fences, retaining visible text
        # before and after them. A comment can continue across several lines.
        visible = []
        pos = 0
        while pos < len(line):
            if in_comment:
                end = line.find("-->", pos)
                if end < 0:
                    visible.append(_mask_nonprose(line[pos:]))
                    pos = len(line)
                else:
                    visible.append(_mask_nonprose(line[pos:end + 3]))
                    pos = end + 3
                    in_comment = False
            else:
                start = line.find("<!--", pos)
                if start < 0:
                    visible.append(line[pos:])
                    pos = len(line)
                else:
                    visible.append(line[pos:start])
                    pos = start
                    in_comment = True
        visible_line = "".join(visible)
        if FOOTER_HEADING.fullmatch(visible_line.rstrip("\r\n")):
            break
        result.append(visible_line)
    return "".join(result)


def live():
    """Every file in the living docset. Chapters are prose, tools are tools."""
    for f in sorted(ROOT.rglob("*")):
        if not f.is_file(): continue
        rel = str(f.relative_to(ROOT))
        # Git metadata is not part of the story or its seal. This also handles
        # worktrees, where .git is a file rather than a directory.
        if "__pycache__" in f.parts or ".git" in f.parts or f.name.startswith("MANIFEST"): continue
        yield f, rel

# 1 — the map names every file
def check_map():
    readme = read("README.md"); missing = []
    for f, rel in live():
        if rel.startswith(("chapters/", "tools/", "canon/")) or rel == "README.md": continue
        if f.name not in readme: missing.append(rel)
    if missing: bad(f"MAP: {len(missing)} file(s) not named in README: {missing}")
    else: ok("MAP: every file at the root of the docset is named in README.md")

# 2 — every file says what it owns
def check_owners():
    lacking = []
    for f, rel in live():
        if rel.startswith(("chapters/", "tools/")) or f.name == "README.md": continue
        head = "\n".join(f.read_text(encoding="utf-8").splitlines()[:6])
        if "Owns:" not in head and '"owner"' not in f.read_text(encoding="utf-8"):
            if f.suffix == ".md" or f.suffix == ".json": lacking.append(rel)
    if lacking: bad(f"OWNERS: {len(lacking)} file(s) with no owner line: {lacking}")
    else: ok("OWNERS: every living file has an ownership declaration")

# 3 — the fact rows
def check_facts():
    rows = json.loads(read("canon/facts.json"))["facts"]
    ids = [r["id"] for r in rows]; dupes = {i for i in ids if ids.count(i) > 1}
    wit = set(re.findall(r"^\| (W-\d{2,}) \|", read("CANON.md"), re.M))
    probs = []
    if dupes: probs.append(f"duplicate ids {sorted(dupes)}")
    for r in rows:
        if r.get("tier") not in ("I", "II", "III"): probs.append(f"{r['id']} tier")
        if not (r.get("statement") or "").strip():  probs.append(f"{r['id']} statement")
        if not r.get("witnesses"):                  probs.append(f"{r['id']} witness")
        if not r.get("source") or not r.get("source_class"): probs.append(f"{r['id']} source/class")
        if r.get("strength") not in ("A", "B", "C", "D"): probs.append(f"{r['id']} grade")
        for w in r.get("witnesses", []):
            if w != "OC" and w not in wit: probs.append(f"{r['id']} cites unknown {w}")
    rejected = [r for r in rows if r.get("status") == "rejected-draft"]
    historical_notes = [r for r in rows if r.get("status") == "historical-note-not-on-page"]
    active = [r for r in rows if r.get("status") not in ("rejected-draft", "historical-note-not-on-page")]
    for r in rejected:
        if not r.get("statement", "").startswith("REJECTED HISTORICAL DRAFT"):
            probs.append(f"{r['id']} rejected row lacks warning")
    tier1 = sum(1 for r in active if r["tier"] == "I")
    if probs: bad(f"FACTS: {probs[:6]}")
    else: ok(f"FACTS: {len(rows)} rows · {len(active)} active or current-draft · {len(rejected)} rejected historical · {len(historical_notes)} other historical note(s) · {tier1} provisional Tier I")

# 4 — no citation to a row that does not exist
def check_citations():
    rows = {r["id"] for r in json.loads(read("canon/facts.json"))["facts"]}
    wit = set(re.findall(r"^\| (W-\d{2,}) \|", read("CANON.md"), re.M))
    probs = []
    for f, rel in live():
        if rel.startswith("tools/") or f.suffix not in (".md", ".json"): continue
        text = f.read_text(encoding="utf-8")
        for rid in set(re.findall(r"\b[CO]\d{3}\b", text)):
            if rid not in rows: probs.append(f"{rel}: {rid}")
        for wid in set(re.findall(r"\bW-\d{2,}\b", text)):
            if wid not in wit: probs.append(f"{rel}: {wid}")
        for oid in set(re.findall(r"\b(O-\d\d)\b", text)):
            if oid not in ("OPEN-1",) and oid.replace("O-", "O0") not in rows and oid not in {o for o in rows}:
                probs.append(f"{rel}: {oid}")
    if probs: bad(f"CITATIONS: {len(probs)} unresolved — {sorted(set(probs))[:8]}")
    else: ok("CITATIONS: configured C/O and W references in Markdown and JSON resolve")

# 4b — rejected material is historical, never support for the live story
def check_rejected_drafts():
    rows = json.loads(read("canon/facts.json"))["facts"]
    rejected = {r["id"] for r in rows if r.get("status") == "rejected-draft"}
    if not rejected:
        bad("REJECTED: no historical rejected-draft rows found")
        return
    paths = [ROOT / x for x in ("README.md", "STORY.md", "STATUS.md", "OPEN.md", "CRAFT.md", "canon/techniques.json")]
    paths += sorted((ROOT / "chapters").glob("Chapter_*.md"))
    hits = []
    for p in paths:
        if not p.exists(): continue
        cited = set(re.findall(r"\b[CO]\d{3}\b", p.read_text(encoding="utf-8")))
        for rid in sorted(cited & rejected):
            hits.append(f"{p.relative_to(ROOT)}: {rid}")
    if hits: bad(f"REJECTED: historical rejected rows cited as live support — {hits}")
    else: ok(f"REJECTED: {len(rejected)} historical draft rows excluded from current chapters and state/technique ledgers")

# 5 — the Saiyan name must first appear in Raditz's declared reveal
def check_reveal():
    revealed, hits, declared = False, [], []
    for f in sorted((ROOT / "chapters").glob("Chapter_*.md")):
        text = f.read_text(encoding="utf-8")
        body = chapter_prose(text)
        for number, line in enumerate(body.splitlines(), 1):
            if not re.search(r"\bBroc\b", line):
                continue
            if not revealed:
                if "NAME-REVEAL: yes" not in text or "Raditz" not in line:
                    hits.append(f"{f.name}:{number}")
                else:
                    revealed = True
                    declared.append(f.name)
    if hits: bad(f"REVEAL: Broc appears before a declared Raditz reveal — {hits}")
    elif not revealed: ok("REVEAL: Broc has not yet appeared in chapter prose")
    else: ok(f"REVEAL: first Broc appearance is Raditz's declared reveal in {declared[0]}")

# 5b — the author's source reference must be visible at the chapter opening.
# This checks only presence and placement, never whether an episode is the
# right source or whether the chapter has covered it completely.
EPISODE_REFERENCE = re.compile(
    r"^\*Anime episode reference:[ \t]*Dragon Ball Z,[ \t]*Episodes?[ \t]+\d[^*\n]*\*[ \t]*$"
)


def check_episode_references():
    probs = []
    chapters = sorted((ROOT / "chapters").glob("Chapter_*.md"))
    if not chapters:
        bad("EPISODE REFERENCES: no chapter files found")
        return
    for f in chapters:
        visible = f.read_text(encoding="utf-8").split("<!--", 1)[0]
        lines = [line.strip() for line in visible.splitlines() if line.strip()]
        if (len(lines) < 2 or not lines[0].startswith("# Chapter ")
                or not EPISODE_REFERENCE.fullmatch(lines[1])):
            probs.append(f.name)
    if probs:
        bad(f"EPISODE REFERENCES: missing or misplaced visible opening reference in {probs}")
    else:
        ok(f"EPISODE REFERENCES: visible opening label in {len(chapters)} chapters; episode accuracy and coverage need manual review")


# 6 — cards, evidence, staging
def check_cards():
    tier1 = any(r["tier"] == "I" for r in json.loads(read("canon/facts.json"))["facts"])
    probs = []
    for f in sorted((ROOT / "chapters").glob("Chapter_*.md")):
        t = f.read_text(encoding="utf-8"); card = t.split("```")[1] if "```" in t else ""
        if not re.search(r"ANIME BASE:|MANGA BASE:", card): probs.append(f"{f.name}: no base")
        if not re.search(r"^EVIDENCE:", card, re.M):       probs.append(f"{f.name}: evidence not declared")
        elif not tier1 and "EVIDENCE: I" in card:        probs.append(f"{f.name}: Tier I claimed but no Tier I rows")
        if "STAGING:" not in card:                         probs.append(f"{f.name}: authored material not declared")
        if not re.search(r"WITNESS:", card):               probs.append(f"{f.name}: no witness line")
    if probs: bad(f"CARDS: {probs}")
    else: ok("CARDS: every chapter declares its base, its evidence tier, its witnesses and its authored staging")


# 6b — a withdrawn claim may not stand up again
def check_withdrawn():
    canon = read("CANON.md")
    block = canon.split("## 7 · Withdrawn")[1].split("\n## ")[0] if "## 7 · Withdrawn" in canon else ""
    phrases = re.findall(r"^\| R-\d+ \| \"([^\"]+)\"", block, re.M)
    if not phrases: bad("WITHDRAWN: CANON §7 has no machine-readable rows"); return
    allow = ("struck", "retired", "it read", "was wrong", "correction", "~~", "withdrawn", "not deleted", "removed", "dub", "the episode says", "paraphrase")
    probs = []
    for f, rel in live():
        if f.suffix != ".md" or f.name in ("CANON.md", "HISTORY.md"): continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            low = line.lower()
            if any(a in low for a in allow): continue
            for ph in phrases:
                if ph.lower() in low: probs.append(f"{rel}:{i} — R? '{ph}'")
    if probs: bad(f"WITHDRAWN: {len(probs)} retired claim(s) standing — {probs[:5]}")
    else: ok(f"WITHDRAWN: {len(phrases)} retired claims, none of them standing anywhere")

# 7 — the band
def band_prose(text):
    """Count the whole chapter, including its cold open, but not metadata."""
    prose = chapter_prose(text)
    # The visible source label is metadata, not an extra sentence or story word.
    # Do not remove any scene or change the existing length/dialogue bands.
    prose = "\n".join(line for line in prose.split("\n")
                      if not EPISODE_REFERENCE.fullmatch(line.strip()))
    first_divider = re.search(r"(?m)^[ \t]*---[ \t]*$", prose)
    if first_divider:
        lead = prose[:first_divider.start()]
        lead = re.sub(r"\A\s*# Chapter[^\n]*\n", "", lead, count=1)
        if not lead.strip():
            # A title and metadata followed by a divider: retain the legacy
            # interpretation for the original source-card chapter format.
            return prose[first_divider.end():]
    # A real scene precedes the first divider: keep it, including the cold
    # open, and remove divider lines rather than discarding the whole opening.
    prose = re.sub(r"\A\s*# Chapter[^\n]*\n", "", prose, count=1)
    return re.sub(r"(?m)^[ \t]*---[ \t]*$", "", prose)


def sentence_runs(prose):
    """Count sentences rather than title dots or attached dialogue tags.

    Protect a title period immediately before a capitalized name and a quoted
    question/exclamation immediately followed on the same line by an explicit
    speech attribution. Other sentence punctuation and all bands stay intact.
    """
    protected = re.sub(r"\b(?:Mr|Mrs|Ms|Dr)\.(?=\s+[A-Z])",
                       lambda m: m.group(0)[:-1] + "\u2024", prose)
    speech_tag = (r'([!?]+)(["”])([ \t]+(?:[A-Z][\w-]*|he|she|they)'
                  r'[ \t]+(?:says|asks|shouts|calls|replies|answers|whispers|'
                  r'murmurs|cries|adds|tells|begs|snaps|warns|growls|yells|'
                  r'screams|laughs)\b)')
    protected = re.sub(speech_tag, lambda m: "\u2024" + m.group(2) + m.group(3), protected)
    return [len(c.split()) for c in re.split(r"[.!?]+", protected) if c.strip()]


def check_band():
    for f in sorted((ROOT / "chapters").glob("Chapter_*.md")):
        t = f.read_text(encoding="utf-8")
        prose = band_prose(t)
        words = len(prose.split())
        runs = sentence_runs(prose)
        lines = [l for l in prose.splitlines() if l.strip() and not l.startswith("#")]
        dial = 100 * sum(1 for l in lines if '"' in l) / max(len(lines), 1)
        avg = sum(runs) / max(len(runs), 1)
        card = t.split("```")[1] if "```" in t else ""
        legacy = {"Chapter_01_Two_Names.md", "Chapter_02_The_Second_Name.md"}
        lo, hi = (2600, 3600) if f.name in legacy and "FORM: EPISODE" not in card else (4400, 6600)
        failures_before = len(F)
        if not (lo <= words <= hi): bad(f"BAND: {f.name} is {words} words ({lo:,}–{hi:,})")
        if max(runs) > 60:              bad(f"BAND: {f.name} has a {max(runs)}-word sentence (cap 60)")
        if not (8 <= avg <= 14):        bad(f"BAND: {f.name} average sentence {avg:.2f} (8–14)")
        if not (42 <= dial <= 70):      bad(f"BAND: {f.name} dialogue {dial:.1f}% (42–70)")
        if len(F) == failures_before:
            ok(f"BAND: {f.name} — {words} words · avg {avg:.1f} · longest {max(runs)} · dialogue {dial:.1f}%")

# 8 — the seal
def check_seal():
    man = ROOT / "MANIFEST.sha256"
    if not man.exists(): bad("SEAL: missing"); return
    listed = {}
    for line in man.read_text(encoding="utf-8").splitlines():
        if "  " in line:
            h, p = line.split("  ", 1); listed[p.strip()] = h.strip()
    drift = [p for p, h in listed.items()
             if not (ROOT / p).exists() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    stale = [rel for _, rel in live() if rel not in listed]
    if drift: bad(f"SEAL: {len(drift)} file(s) changed since sealing: {drift[:5]}")
    elif stale: bad(f"SEAL: {len(stale)} file(s) exist but are not sealed: {stale[:5]}")
    else: ok(f"SEAL: {len(listed)} file(s) match their sealed hash")

# 6c — the cloud says it, not the prose
def check_purity():
    probs = []
    for f in sorted((ROOT / "chapters").glob("Chapter_*.md")):
        prose = chapter_prose(f.read_text(encoding="utf-8"))
        if re.search(r"\b(pure|purity|pure-hearted|purehearted)\b", prose, re.I):
            probs.append(f.name)
    if probs: bad(f"PURITY: the word is in the prose of {probs} — the cloud says it, the prose never does")
    else: ok("PURITY: no configured purity term in chapter prose; semantic review still required")

# 6d — the era lock: a four-year-old is not a god
def check_era():
    words = r"\b(god\s+ki|godly\s+ki|divine\s+ki|godhood|divinity|divine|super saiyan)\b"
    probs = []
    for f in sorted((ROOT / "chapters").glob("Chapter_*.md")):
        prose = chapter_prose(f.read_text(encoding="utf-8"))
        hit = re.search(words, prose, re.I)
        if hit: probs.append(f"{f.name}: '{hit.group(0)}'")
    if probs: bad(f"ERA: a chapter has reached above the locking rung — {probs[:4]}")
    else: ok("ERA: no configured exact forbidden phrase matched; speculation and actual transformations still require semantic review")

# 6e — a named character is called by name in narration
EPITHET = {
    r"the woman with blue hair": "Bulma",
    r"the blue-haired woman": "Bulma",
    r"the tall man": "Raditz",
    r"the scarred man": "Raditz",
    r"the big man": "Ox-King",
    r"the huge man": "Ox-King",
    r"the giant": "Ox-King",
    r"the old man": "Roshi",
    r"the old master": "Roshi",
    r"the demon": "Piccolo",
    r"the green man": "Piccolo",
    r"the taller boy": "Gohan",
    r"the taller one": "Gohan",
    r"the tall one": "Gohan",
    r"the larger boy": "Gohan",
    r"the smaller boy": "Goshin",
    r"the smaller one": "Goshin",
    r"the small one": "Goshin",
    r"the little one": "Goshin",
}

# Reviewed non-character use: this 'small one' is the rescued dinosaur, not
# Goshin. Other occurrences, including in this same chapter, still fail.
EPITHET_NONCHARACTER_LINES = {
    ("Chapter_08_The_Dinosaur_by_the_River.md", "the small one",
     "The large dinosaur breaks through the falling mud. Gohan sets the small one down and backs away."),
}


def check_names():
    probs = []
    files = sorted((ROOT / "chapters").glob("Chapter_*.md")) + [ROOT / "CRAFT.md"]
    for f in files:
        if not f.exists(): continue
        text = f.read_text(encoding="utf-8")
        t = (chapter_prose(text) if f.parent == ROOT / "chapters"
             else re.sub(r"```.*?```", "", text.split("## Footer")[0], flags=re.S))
        prose = re.sub(r'"[^"]*"', "", t)          # dialogue is a licence
        for pat, name in EPITHET.items():
            if not re.search(rf"\b{name}\b", t): continue
            for match in re.finditer(pat, prose, re.I):
                start = prose.rfind("\n", 0, match.start()) + 1
                end = prose.find("\n", match.end())
                line = prose[start:end if end >= 0 else len(prose)].strip()
                if (f.name, pat, line) in EPITHET_NONCHARACTER_LINES: continue
                probs.append(f"{f.name}: '{pat}' for {name}")
                break
    if probs: bad(f"NAMES: narration uses an epithet for a named character — {probs[:5]}")
    else: ok("NAMES: no configured epithet matched; other descriptions still require manual review")

# 6f — every specimen carries a plain-words crib before its prose
def check_crib():
    f = ROOT / "CRAFT.md"
    if not f.exists(): bad("CRIB: CRAFT.md is missing"); return
    t = f.read_text(encoding="utf-8")
    specs = t.count("# SPECIMEN")
    cribs = t.count("IN PLAIN WORDS")
    prose = t.count("## THE PROSE")
    what = t.count("**WHAT THIS IS:**")
    if specs and what < specs:
        bad(f"CRIB: {specs} specimen(s) but {what} 'WHAT THIS IS' statement(s) — name the situation first")
    if specs == 0: bad("CRIB: no specimens found")
    elif cribs < specs or prose < specs:
        bad(f"CRIB: {specs} specimen(s), {cribs} crib(s), {prose} prose block(s) — every specimen needs a crib first")
    else: ok(f"CRIB: {specs} specimens, each with a plain-words crib before the prose")

# 6g — the flow: no telling the reader they could not see it, no flagging the impossible
TICS = [
    r"nobody saw", r"no one saw", r"nobody could see", r"no one could see",
    r"blink of an eye", r"faster than the eye", r"quicker than the eye",
    r"too fast to see", r"impossibly", r"which is impossible",
    r"the wrong way round", r"should not have been possible",
]

def check_flow():
    probs = []
    files = [(f, chapter_prose(f.read_text(encoding="utf-8")))
             for f in sorted((ROOT / "chapters").glob("Chapter_*.md"))]
    craft = ROOT / "CRAFT.md"
    if craft.exists():
        blocks = []
        for part in craft.read_text(encoding="utf-8").split("## THE PROSE")[1:]:
            blocks.append(part.split("## WHAT IT IS DOING")[0])
        files.append((craft, "\n".join(blocks)))
    for f, t in files:
        t = re.sub(r"```.*?```", "", t, flags=re.S)
        low = t.lower()
        for pat in TICS:
            if re.search(pat, low): probs.append(f"{f.name}: '{pat}'")
    if probs: bad(f"FLOW: the prose reports what could not be seen, or flags the impossible — {probs[:4]}")
    else: ok("FLOW: no configured visibility/implausibility tic matched; camera and meaning require manual review")

# 6h — a fight declares its scale before it declares its damage
def check_scale():
    probs = []
    craft = ROOT / "CRAFT.md"
    if craft.exists():
        t = craft.read_text(encoding="utf-8")
        specs = t.count("# SPECIMEN"); scales = t.count("**SCALE:")
        if scales < specs: probs.append(f"CRAFT.md: {specs} specimen(s), {scales} SCALE line(s)")
    for f in sorted((ROOT / "chapters").glob("Chapter_*.md")):
        t = f.read_text(encoding="utf-8")
        card = t.split("```")[1] if "```" in t else ""
        if "FIGHT:" in card and "SCALE:" not in card:
            probs.append(f"{f.name}: declares a fight and no scale")
    if probs: bad(f"SCALE: {probs}")
    else: ok("SCALE: specimens declare context; damage must still be reviewed against feats and circumstances, not inferred from numbers")

# 6i — narrow marker guard, not a substitute for source review
# Exact prose markers catch accidental loss of the repaired capture/truck/pod sequence.
def check_scene_markers():
    chapter = ROOT / "chapters" / "Chapter_04_The_Rescue.md"
    if not chapter.exists():
        bad("SCENE MARKERS: Chapter Four is missing")
        return
    body = chapter_prose(chapter.read_text(encoding="utf-8")).lower()
    landmarks = [
        "strikes the side of his head",
        "pick up goshin with the other",
        "## 7 · the truck",
        "crawls under the truck with him",
        "drives his fist down into the engine",
        "throws the truck high",
        "places goshin in the pod",
        "goshin opens his eyes",
    ]
    positions = [body.find(s) for s in landmarks]
    if any(p < 0 for p in positions):
        bad(f"SCENE MARKERS: missing {[landmarks[i] for i, p in enumerate(positions) if p < 0]}")
    elif positions != sorted(positions):
        bad("SCENE MARKERS: capture/truck/pod markers are out of order")
    else:
        ok("SCENE MARKERS: knockout, transport, truck, confinement and waking markers appear in order; this does not prove completeness")

def check_moon_regression():
    """Catch exact superseded Jupiter wording only; manual scene review is still essential."""
    files = {
        "Chapter_30_The_House_That_Waited.md": (
            "until his brother points out a smaller bright shape nearby",
            "arguing over whether it could be one of jupiter's moons",
            "then goshin sees another bright point beyond the first",
        ),
        "Chapter_31_The_Other_Side_of_the_Sky.md": (
            "those really might be moons",
            "we'd have to get closer to know which ones we're looking at",
            "we could see little bright points beside it. we think they were moons",
        ),
    }
    hits = []
    for name, phrases in files.items():
        path = ROOT / "chapters" / name
        if not path.exists():
            hits.append(f"{name} missing")
            continue
        body = " ".join(chapter_prose(path.read_text(encoding="utf-8")).lower().split())
        hits.extend(f"{name}: {phrase}" for phrase in phrases if phrase in body)
    if hits: bad(f"MOON REGRESSION: superseded wording found: {hits}")
    else: ok("MOON REGRESSION: exact superseded Jupiter lines absent; this cannot detect paraphrases or replace a continuity review")


# These are current rules, not the dated history or preserved previous statements.
# This catches a few exact regressions only; it cannot judge the meaning of prose.
HYBRID_RULE_PATHS = (
    "WRITING.md", "README.md", "OPEN.md", "STATUS.md", "STORY.md",
    "foundation/FOUNDATION.md", "foundation/ADAPTATION_MODULE.md",
    "foundation/ADAPTATION_LOG.md", "foundation/GOSHIN_STATUS_PANEL.md",
    "foundation/WORLD_STATE.md", "foundation/TIMELINE.md",
)
SAIYAN_ONLY_REGRESSION = re.compile(
    r"\b(?:his|goshin['’]s)\s+saiyan\s+bloodline\s+(?:becomes|grows)\s+(?:\*\*)?purer",
    re.I,
)


def check_hybrid_bloodline():
    """Check the active facts and narrowly matching obsolete wording, not historical notes."""
    hits = []
    rows = {row["id"]: row for row in json.loads(read("canon/facts.json"))["facts"]}
    for ident in ("O230", "O243", "O244"):
        current = rows.get(ident, {}).get("statement", "").casefold()
        required = ("hybrid", "saiyan", "earthling")
        if ident == "O230":
            required += ("purer", "deeper", "stronger")
        if ident == "O244":
            required += ("whole existence", "talent", "potential")
        if not all(word in current for word in required):
            hits.append(f"{ident}: current statement missing hybrid or whole-existence direction")
    for name in HYBRID_RULE_PATHS:
        path = ROOT / name
        if not path.exists():
            hits.append(f"{name}: missing")
        elif SAIYAN_ONLY_REGRESSION.search(path.read_text(encoding="utf-8")):
            hits.append(f"{name}: exact Saiyan-only pattern")
    chapter = ROOT / "chapters" / "Chapter_27_The_Space_to_Stand.md"
    if not chapter.exists():
        hits.append("Chapter 27: missing")
    else:
        body = " ".join(chapter_prose(chapter.read_text(encoding="utf-8")).casefold().split())
        if "the saiyan strength in him feels deeper now" in body:
            hits.append("Chapter 27: exact superseded Saiyan-only sentence")
    if hits:
        bad(f"HYBRID REGRESSION: {hits}")
    else:
        ok("HYBRID REGRESSION: active facts and selected exact old wording checked; paraphrases and meaning require manual review")


def check_kaioken_regression():
    """Narrow literal checks on the selected correction, not a power or prose proof.

    These track the current draft, not an author-imposed permanent ×2/×3 ladder.
    If a future authorized revision changes the scene, update the guard and fixtures.
    Historical previous_statement fields and the audit are deliberately excluded.
    """
    hits = []
    rows = {row["id"]: row for row in json.loads(read("canon/facts.json"))["facts"]}
    for ident, terms in {
        "O240": ("times two", "times three", "unboosted", "temporary"),
        "O245": ("times two", "temporary", "unaccepted"),
        "O249": ("unboosted", "temporary", "unaccepted"),
    }.items():
        current = rows.get(ident, {}).get("statement", "").casefold()
        if not all(term in current for term in terms):
            hits.append(f"{ident}: active statement missing current correction markers")
        if "not a named transformation or fixed multiplier" in current:
            hits.append(f"{ident}: exact superseded multiplier denial")
    chapter = ROOT / "chapters" / "Chapter_32_The_Road_Beyond_Earth.md"
    if not chapter.exists():
        hits.append("Chapter 32: missing")
    else:
        body = chapter_prose(chapter.read_text(encoding="utf-8")).casefold()
        if body.count("kaiō-ken, times two") < 3 or "kaiō-ken, times three" not in body:
            hits.append("Chapter 32: selected literal multiplier calls missing")
    if hits:
        bad(f"KAIOKEN REGRESSION: {hits}")
    else:
        ok("KAIOKEN REGRESSION: selected literal calls and active fact markers checked; attribution, arithmetic and scene meaning require manual review")


def run():
    for c in (check_map, check_owners, check_facts, check_citations, check_rejected_drafts, check_reveal,
              check_episode_references, check_cards, check_purity, check_era, check_names, check_crib, check_flow, check_scale, check_withdrawn, check_scene_markers, check_moon_regression, check_hybrid_bloodline, check_kaioken_regression, check_band, check_seal):
        try: c()
        except Exception as e: bad(f"{c.__name__}: crashed — {e}")
    for m in P: print(f"  PASS  {m}")
    for m in F[:40]: print(f"  FAIL  {m}")
    if re.search(r"^### OPEN-17", read("OPEN.md"), re.M):
        print("  NOTE  OPEN-17: revision review, wider character-rule review and source limits remain open; mechanical checks are not editorial clearance")
    print(f"\n{len(P)} passed · {len(F)} failed")
    return 1 if F else 0

def focused_check(fn):
    P.clear(); F.clear()
    fn()
    return list(P), list(F)

def insert_selftest_prose(chapter: str, paragraph: str) -> str:
    """Insert test prose into the first visible scene, regardless of its title.

    The opening chapter has been rewritten; assuming the old ``## ONE``
    heading would silently make negative tests no-ops. Never inject into the
    historical footer or modify the live chapter outside the disposable copy.
    """
    visible = chapter_prose(chapter)
    heading = re.search(r"(?m)^## [^\n]+\n", visible)
    if not heading:
        raise ValueError("chapter has no visible scene heading for self-test")
    i = heading.end()
    return chapter[:i] + "\n" + paragraph + "\n" + chapter[i:]


def _selftest_in_root():
    """Run mutation fixtures only in the isolated project copy."""
    global ROOT
    clean = run()
    results = []
    facts = ROOT / "canon" / "facts.json"
    before = facts.read_text(encoding="utf-8")
    try:
        data = json.loads(before)
        data["facts"].append({"id": "C001", "tier": "IV", "source": "", "statement": ""})
        facts.write_text(json.dumps(data), encoding="utf-8")
        _, failures = focused_check(check_facts)
        results.append(("duplicate/invalid fact fails", bool(failures)))
        data = json.loads(before)
        data["facts"][0]["statement"] += " Broken internal citation C999."
        facts.write_text(json.dumps(data), encoding="utf-8")
        _, failures = focused_check(check_citations)
        results.append(("missing fact cross-reference in JSON fails", bool(failures)))
    finally:
        facts.write_text(before, encoding="utf-8")
    chapter = ROOT / "chapters" / "Chapter_01_Two_Names.md"
    before = chapter.read_text(encoding="utf-8")
    try:
        chapter.write_text(insert_selftest_prose(before, "Broc."), encoding="utf-8")
        _, failures = focused_check(check_reveal)
        results.append(("early Broc reveal fails", bool(failures)))
        chapter.write_text(insert_selftest_prose(before, "His ki rose."), encoding="utf-8")
        _, failures = focused_check(check_era)
        results.append(("ordinary ki is allowed", not failures))
        chapter.write_text(insert_selftest_prose(before, "His god ki rose."), encoding="utf-8")
        _, failures = focused_check(check_era)
        results.append(("early god ki fails", bool(failures)))
        chapter.write_text(insert_selftest_prose(before, "His Super Saiyan form appeared."), encoding="utf-8")
        _, failures = focused_check(check_era)
        results.append(("configured early transformation phrase fails", bool(failures)))
        chapter.write_text(insert_selftest_prose(before, '"Super Saiyans?"'), encoding="utf-8")
        _, failures = focused_check(check_era)
        results.append(("plural speculative dialogue is not automatically treated as a transformation", not failures))
        chapter.write_text(before.replace("## Footer\n", "## Footer\n\nC999\n", 1), encoding="utf-8")
        _, failures = focused_check(check_citations)
        results.append(("missing citation fails", bool(failures)))
        chapter.write_text(before.replace("## Footer\n", "## Footer\n\nO062\n", 1), encoding="utf-8")
        _, failures = focused_check(check_rejected_drafts)
        results.append(("rejected draft cannot support a live chapter", bool(failures)))
        chapter.write_text(before.replace("## Footer\n", "## Footer\n\nO068\n", 1), encoding="utf-8")
        _, failures = focused_check(check_rejected_drafts)
        results.append(("conscious-capture draft cannot support a live chapter", bool(failures)))
        oversized = ("ground " * 1500) + "."
        chapter.write_text(insert_selftest_prose(before, oversized), encoding="utf-8")
        passes, failures = focused_check(check_band)
        name = chapter.name
        results.append(("out-of-band chapter fails without a false pass",
                        any(name in item for item in failures)
                        and not any(name in item for item in passes)))
    finally:
        chapter.write_text(before, encoding="utf-8")
    rescue = ROOT / "chapters" / "Chapter_04_The_Rescue.md"
    before = rescue.read_text(encoding="utf-8")
    try:
        needle = "Raditz throws the truck high"
        assert needle in before
        rescue.write_text(before.replace(needle, "Raditz turns away", 1), encoding="utf-8")
        _, failures = focused_check(check_scene_markers)
        results.append(("removed truck-scene marker fails", bool(failures)))
    finally:
        rescue.write_text(before, encoding="utf-8")
    moon_chapter = ROOT / "chapters" / "Chapter_31_The_Other_Side_of_the_Sky.md"
    before = moon_chapter.read_text(encoding="utf-8")
    try:
        moon_chapter.write_text(insert_selftest_prose(before, '"Those really might be moons."'), encoding="utf-8")
        _, failures = focused_check(check_moon_regression)
        results.append(("known superseded moon line fails", bool(failures)))
    finally:
        moon_chapter.write_text(before, encoding="utf-8")
    # A Git clone and a Git worktree expose metadata differently; neither
    # should enter the living docset or its checksum seal.
    original_root = ROOT
    try:
        with tempfile.TemporaryDirectory(prefix="twin-git-audit-", dir="/tmp") as tmp:
            ROOT = pathlib.Path(tmp)
            (ROOT / "story.md").write_text("story", encoding="utf-8")
            git_meta = ROOT / ".git"
            git_meta.mkdir()
            (git_meta / "index").write_bytes(b"\xff\x00")
            with_directory = {rel for _, rel in live()}
            (git_meta / "index").unlink()
            git_meta.rmdir()
            git_meta.write_text("gitdir: elsewhere\n", encoding="utf-8")
            with_worktree_file = {rel for _, rel in live()}
            results.append(("Git directory and worktree file excluded",
                            with_directory == {"story.md"} == with_worktree_file))
    finally:
        ROOT = original_root
    for name, passed in results:
        print(f"  SELFTEST {'PASS' if passed else 'FAIL'}  {name}")
    success = clean == 0 and all(passed for _, passed in results)
    print(f"selftest: clean={clean}; {sum(passed for _, passed in results)}/{len(results)} focused checks → {'OK' if success else 'FAILED'}")
    return 0 if success else 1

def selftest():
    """Copy the project to system scratch before running mutation fixtures.

    A failed or interrupted negative test must never leave injected text in the
    live manuscript. The temporary copy is outside the workshop and is removed
    by TemporaryDirectory; it is a test fixture, not a project backup.
    """
    global ROOT
    original_root = ROOT
    try:
        with tempfile.TemporaryDirectory(prefix="twin-selftest-", dir="/tmp") as tmp:
            fixture = pathlib.Path(tmp) / "project"
            shutil.copytree(original_root, fixture,
                            ignore=shutil.ignore_patterns("__pycache__", ".git"))
            ROOT = fixture
            return _selftest_in_root()
    finally:
        ROOT = original_root


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else run())
