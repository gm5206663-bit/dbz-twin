#!/usr/bin/env python3
"""Reseal the reviewed living docset using the same file scope as check.py.

Run only after inspecting intentional changes. This updates integrity hashes; it
does not imply reader acceptance, factual correctness or source verification.
"""
import hashlib
import os
from check import ROOT, live


def main():
    rows = []
    for file, rel in live():
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        rows.append(f"{digest}  {rel}\n")
    target = ROOT / "MANIFEST.sha256"
    temp = ROOT / "MANIFEST.sha256.tmp"
    temp.write_text("".join(rows), encoding="utf-8")
    os.replace(temp, target)
    print(f"Resealed {len(rows)} reviewed living files. Run python3 tools/check.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
