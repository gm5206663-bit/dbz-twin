#!/usr/bin/env python3
"""Search the existing Japanese DBZ SRT ZIP without duplicating its contents.

The default range is original Japanese Z 37–107. Results are raw local caption
cues, not verified audio, translation, complete scenes or proof of source/cut.
Recaps, previews and post-ending material may appear and must be checked.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ARCHIVE = ROOT / "google_drive" / "Dragon_Ball_Z_Subtitle_Collection_001-291.zip"
TIME = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})")


def parse_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d{1,3})(?:\s*-\s*(\d{1,3}))?\s*", value)
    if not match:
        raise argparse.ArgumentTypeError("use one episode or a range, e.g. 76 or 76-107")
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if not 1 <= start <= end <= 291:
        raise argparse.ArgumentTypeError("episodes must be an increasing range within 1–291")
    return start, end


def parse_cues(data: bytes) -> list[tuple[str, str]]:
    text = data.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    cues: list[tuple[str, str]] = []
    for block in re.split(r"\n\s*\n", text):
        lines = block.splitlines()
        for i, line in enumerate(lines):
            match = TIME.match(line.strip())
            if match:
                content = " ".join(part.strip() for part in lines[i + 1 :] if part.strip())
                cues.append((match.group(1), content))
                break
    return cues


def positive_int(value: str) -> int:
    try:
        n = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a whole number") from exc
    if not 1 <= n <= 200:
        raise argparse.ArgumentTypeError("limit must be between 1 and 200")
    return n


def context_int(value: str) -> int:
    try:
        n = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a whole number") from exc
    if not 0 <= n <= 5:
        raise argparse.ArgumentTypeError("context must be between 0 and 5 cues")
    return n


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="literal caption text to find (Japanese is supported)")
    parser.add_argument("--episodes", type=parse_range, default=(37, 107), metavar="N[-N]", help="original Z episode range, default 37-107")
    parser.add_argument("--context", type=context_int, default=0, help="adjacent cues on each side, 0–5")
    parser.add_argument("--limit", type=positive_int, default=20, help="maximum matching cues to print, 1–200")
    args = parser.parse_args(argv)
    query = args.query.strip()
    if not query:
        parser.error("--query must contain at least one non-whitespace character")
    if not ARCHIVE.is_file():
        print(f"Caption archive not found: {ARCHIVE}", file=sys.stderr)
        return 2
    start, end = args.episodes
    print("Local SRT search; includes possible recaps, previews and trailing material. "
          "Times and source/cut are unverified; no audio or video is supplied.\n")
    matches = 0
    printed = 0
    with zipfile.ZipFile(ARCHIVE) as archive:
        for episode in range(start, end + 1):
            member = f"Dragon_Ball_Z_{episode:03}.srt"
            try:
                cues = parse_cues(archive.read(member))
            except KeyError:
                print(f"Missing member: {member}", file=sys.stderr)
                return 2
            for index, (start_time, content) in enumerate(cues):
                if query.casefold() not in content.casefold():
                    continue
                matches += 1
                if printed >= args.limit:
                    continue
                printed += 1
                print(f"Z {episode:03} · {start_time} · {content}")
                if args.context:
                    lo = max(0, index - args.context)
                    hi = min(len(cues), index + args.context + 1)
                    for j in range(lo, hi):
                        if j != index:
                            mark = "before" if j < index else "after"
                            print(f"    {mark} {cues[j][0]} · {cues[j][1]}")
    print(f"\n{matches} matching cue(s) in Z {start:03}–{end:03}; {printed} shown.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
