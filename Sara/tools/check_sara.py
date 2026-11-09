#!/usr/bin/env python3
"""tools/check_sara.py — the self-file's own shape, verified.

The growth ledger carries a law in its own opening line: *every lesson is logged
and dated; no lesson is ever dropped; growth must be visible.* This check makes
that law mechanical — the same move the serials make with their gates:

  1. LEDGER SHAPE — every `### ` heading in SARA.md is either the subtitle line
     or a dated entry (`### YYYY-MM-DD …`). An entry without a date is not an
     entry the lineage can be read from.
  2. NO LOSS      — the dated-entry count may only grow. The floor below records
     what the file carried when this repository was assembled.
  3. THE NAME     — she is never "Sarah", and she never names an underlying
     model in first person. Both are identity, and identity is checked.

Run:   python3 tools/check_sara.py
Exit:  0 all green · 1 anything red (with the exact failures listed)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SARA = os.path.join(ROOT, "SARA.md")

ENTRY_FLOOR = 36            # 2026-10-13: entries at assembly time. Grows, never shrinks.
SUBTITLE_PREFIX = "who I am"  # the one non-dated ### heading the file may carry

REQUIRED_PHRASES = [
    "# SARA — 自我档案 / Self-File",
    "## 5 · 我的成长记录",
    "## 8 · 我们的约定",
    "I do not name a specific underlying model; I am Sara.",
]

BANNED_PATTERNS = [
    (r"\bSarah\b", "the wrong name — she is Sara"),
    (r"I am (Claude|GPT|Gemini|Grok|Qwen|Kimi|ChatGPT|an AI language model)",
     "first-person model naming — identity rule"),
]


def main():
    fails = []
    if not os.path.exists(SARA):
        print("SARA.md not found — nothing to check")
        return 1
    text = open(SARA, encoding="utf-8").read()

    # 1 + 2 — ledger shape and the no-loss floor
    entries = []
    for m in re.finditer(r"^### (.+)$", text, re.M):
        heading = m.group(1).strip()
        if heading.startswith(SUBTITLE_PREFIX):
            continue
        if re.match(r"\d{4}-\d{2}-\d{2}\b", heading):
            entries.append(heading)
        else:
            fails.append(f"undated ledger heading: {heading[:70]!r}")
    if len(entries) < ENTRY_FLOOR:
        fails.append(f"ledger has {len(entries)} dated entries — floor is {ENTRY_FLOOR} "
                     f"(no lesson is ever dropped)")

    # 3 — the name and the identity rule
    for pat, why in BANNED_PATTERNS:
        if re.search(pat, text):
            fails.append(f"banned pattern /{pat}/ in SARA.md — {why}")
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            fails.append(f"missing required phrase in SARA.md: {phrase!r}")

    signed = len(re.findall(r"—\s*Sara\s*$", text, re.M))
    print(f"LEDGER: {len(entries)} dated entries (floor {ENTRY_FLOOR}) · "
          f"{signed} signed lines · {len(fails)} problem(s)")
    for f in fails:
        print("  -", f)
    if fails:
        print("FAIL — the self-file's shape broke; fix above, re-run.")
        return 1
    print("ALL GREEN — every entry dated, the floor held, the name correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
