#!/usr/bin/env python3
"""The audit for THE TWIN. Arithmetic, not taste.

Exit 0 = clean. Exit 1 = a list of what is wrong.
Self-test: python3 tools/check.py --selftest   (proves it still fails a dirty tree)
"""
import json, re, sys, hashlib, pathlib, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
P, F = [], []

def ok(m):  P.append(m)
def bad(m): F.append(m)
def read(p): return (ROOT / p).read_text(encoding="utf-8")

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
    wit = set(re.findall(r"^\| (W-\d\d) \|", read("CANON.md"), re.M))
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
    wit = set(re.findall(r"^\| (W-\d\d) \|", read("CANON.md"), re.M))
    probs = []
    for f, rel in live():
        if rel.startswith("tools/") or f.suffix not in (".md", ".json"): continue
        text = f.read_text(encoding="utf-8")
        for rid in set(re.findall(r"\b[CO]\d{3}\b", text)):
            if rid not in rows: probs.append(f"{rel}: {rid}")
        for wid in set(re.findall(r"\bW-\d\d\b", text)):
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
        body = re.sub(r"```.*?```", "", text.split("## Footer")[0], flags=re.S)
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
def check_band():
    for f in sorted((ROOT / "chapters").glob("Chapter_*.md")):
        t = f.read_text(encoding="utf-8")
        body = t.split("## Footer")[0]
        prose = re.sub(r"```.*?```", "", body, flags=re.S)
        prose = prose.split("---", 1)[1] if "---" in prose else prose
        words = len(prose.split())
        runs = [len(c.split()) for c in re.split(r"[.!?]+", prose) if c.strip()]
        lines = [l for l in prose.splitlines() if l.strip() and not l.startswith("#")]
        dial = 100 * sum(1 for l in lines if '"' in l) / max(len(lines), 1)
        avg = sum(runs) / max(len(runs), 1)
        card = t.split("```")[1] if "```" in t else ""
        legacy = {"Chapter_01_Two_Names.md", "Chapter_02_The_Second_Name.md"}
        lo, hi = (2600, 3600) if f.name in legacy and "FORM: EPISODE" not in card else (4400, 6600)
        failures_before = len(F)
        if not (lo <= words <= hi): bad(f"BAND: {f.name} is {words} words ({lo:,}–{hi:,})")
        if max(runs) > 60:              bad(f"BAND: {f.name} has a {max(runs)}-word sentence (cap 60)")
        if not (8 <= avg <= 14):        bad(f"BAND: {f.name} average sentence {avg:.1f} (8–14)")
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
        body = f.read_text(encoding="utf-8").split("## Footer")[0]
        prose = re.sub(r"```.*?```", "", body, flags=re.S)
        if re.search(r"\b(pure|purity|pure-hearted|purehearted)\b", prose, re.I):
            probs.append(f.name)
    if probs: bad(f"PURITY: the word is in the prose of {probs} — the cloud says it, the prose never does")
    else: ok("PURITY: no configured purity term in chapter prose; semantic review still required")

# 6d — the era lock: a four-year-old is not a god
def check_era():
    words = r"\b(god\s+ki|godly\s+ki|divine\s+ki|godhood|divinity|divine|super saiyan)\b"
    probs = []
    for f in sorted((ROOT / "chapters").glob("Chapter_*.md")):
        body = f.read_text(encoding="utf-8").split("## Footer")[0]
        prose = re.sub(r"```.*?```", "", body, flags=re.S)
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

def check_names():
    probs = []
    files = sorted((ROOT / "chapters").glob("Chapter_*.md")) + [ROOT / "CRAFT.md"]
    for f in files:
        if not f.exists(): continue
        t = f.read_text(encoding="utf-8").split("## Footer")[0]
        t = re.sub(r"```.*?```", "", t, flags=re.S)
        prose = re.sub(r'"[^"]*"', "", t)          # dialogue is a licence
        for pat, name in EPITHET.items():
            if re.search(pat, prose, re.I) and re.search(rf"\b{name}\b", t):
                probs.append(f"{f.name}: '{pat}' for {name}")
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
    files = [(f, f.read_text(encoding="utf-8").split("## Footer")[0])
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
    body = chapter.read_text(encoding="utf-8").split("## Footer")[0].lower()
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

def run():
    for c in (check_map, check_owners, check_facts, check_citations, check_rejected_drafts, check_reveal,
              check_cards, check_purity, check_era, check_names, check_crib, check_flow, check_scale, check_withdrawn, check_scene_markers, check_band, check_seal):
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

def selftest():
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
        chapter.write_text(before.replace("## ONE\n", "## ONE\n\nBroc.\n", 1), encoding="utf-8")
        _, failures = focused_check(check_reveal)
        results.append(("early Broc reveal fails", bool(failures)))
        chapter.write_text(before.replace("## ONE\n", "## ONE\n\nHis ki rose.\n", 1), encoding="utf-8")
        _, failures = focused_check(check_era)
        results.append(("ordinary ki is allowed", not failures))
        chapter.write_text(before.replace("## ONE\n", "## ONE\n\nHis god ki rose.\n", 1), encoding="utf-8")
        _, failures = focused_check(check_era)
        results.append(("early god ki fails", bool(failures)))
        chapter.write_text(before.replace("## ONE\n", "## ONE\n\nHis Super Saiyan form appeared.\n", 1), encoding="utf-8")
        _, failures = focused_check(check_era)
        results.append(("configured early transformation phrase fails", bool(failures)))
        chapter.write_text(before.replace("## ONE\n", '## ONE\n\n"Super Saiyans?"\n', 1), encoding="utf-8")
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
        oversized = "## ONE\n\n" + ("ground " * 1500) + ".\n"
        chapter.write_text(before.replace("## ONE\n", oversized, 1), encoding="utf-8")
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
    # A Git clone and a Git worktree expose metadata differently; neither
    # should enter the living docset or its checksum seal.
    original_root = ROOT
    try:
        with tempfile.TemporaryDirectory(prefix="twin-git-audit-") as tmp:
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

if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else run())
