#!/usr/bin/env python3
"""Reproduce the Japanese DBZ caption search index, not a full episode reading.

By default this reads the local 001–291 ZIP directly and compares the generated
index to canon/episodes.json without modifying it. Use --source for a different
ZIP or extracted directory; DBZ_SUBS remains supported. Use --output for a new
file, or --write to replace the selected index after preserving its old version.
The 29-minute boundary is a heuristic, not proof of a source's origin or cut.
"""
import argparse
import collections
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'canon' / 'episodes.json'
LOCAL_ARCHIVE = ROOT.parent / 'google_drive' / 'Dragon_Ball_Z_Subtitle_Collection_001-291.zip'
DEFAULT_CAPTIONS = ROOT / 'canon' / 'captions'
# Some files contain a different TV program after about 30:40. 29 minutes keeps
# normal ending/preview speech (including past 26:00), while still bounding the
# index. This is a heuristic, NOT proof that every boundary is perfectly clean.
WINDOW_SECONDS = 29 * 60
# Recorded spoken-caption reads, not a claim that the indexed source is
# authentic or that video was watched. See the dated reviews for 37–117.
FULL_READ = set(range(1, 118)) | {183, 184, 205, 206, 207, 208, 256, 257}
TERMS = {
    'moon': r'満月|月が|お月|月を|月の|月は',
    'tail': r'尻尾|しっぽ',
    'god': r'神様|神と|界王神|大魔王|創造神',
    'ssj': r'超サイヤ人',
    'revive': r'生き返|復活|ドラゴンボール',
    'dead': r'死ん|死ぬ|殺され',
    'train': r'修行|特訓|稽古',
    'flight': r'舞空術|飛べ|飛ぶ|空を飛|空を自由',
    'potential': r'潜在能力|素質|雑種|混血|地球人との血',
    'recovery': r'死のふち|死の淵|死の一歩|治して|回復|傷が治',
    'kai': r'界王様|カイオウ',
    'freeza': r'フリーザ',
    'cell': r'セル',
    'buu': r'魔人ブウ|ブウ',
    'gohan': r'悟飯',
    'goten': r'悟天',
    'study': r'塾|勉強|宿題',
    'power': r'強さ|戦闘力|パワー',
    'ki': r'\bki\b|気のコントロール|大きな気|気を',
}
CAPTION_NAME = re.compile(r'Dragon_Ball_Z_(\d{3})\.srt$')


def stamp(t):
    sec = int(t)
    return f'{sec // 60:02d}:{sec % 60:02d}'


def parse_text(text):
    cues = []
    for block in re.split(r'\n\s*\n', text):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        i = 1 if lines[0].isdigit() else 0
        if i >= len(lines) or '-->' not in lines[i]:
            continue
        ts = lines[i].split('-->')[0].strip().replace(',', '.')
        try:
            h, m, seconds = ts.split(':')
            start = int(h) * 3600 + int(m) * 60 + float(seconds)
        except ValueError:
            continue
        caption = re.sub(r'<[^>]+>', '', ' '.join(lines[i + 1:]))
        cues.append((start, caption))
    return cues


def parse(path):
    """Compatibility helper for a single extracted UTF-8 caption file."""
    return parse_text(Path(path).read_text(encoding='utf-8-sig', errors='replace'))


def numbered_captions(source):
    """Read exactly one caption per episode from a directory or ZIP, no extraction."""
    source = Path(source)
    numbered = []
    if source.is_dir():
        candidates = [(p.name, p.read_bytes) for p in source.iterdir() if p.is_file()]
        for name, read in candidates:
            match = CAPTION_NAME.fullmatch(name)
            if match:
                numbered.append((int(match.group(1)), read().decode('utf-8-sig', errors='replace')))
    elif source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                match = CAPTION_NAME.fullmatch(Path(info.filename).name)
                if match:
                    numbered.append((int(match.group(1)), archive.read(info).decode('utf-8-sig', errors='replace')))
    else:
        raise ValueError(f'Source is not an extracted caption directory or ZIP: {source}')
    numbered.sort(key=lambda item: item[0])
    if [number for number, _ in numbered] != list(range(1, 292)):
        raise ValueError(f'Expected exactly 291 distinct episodes in {source}; found {len(numbered)} caption files. No index was written.')
    return numbered


def make_payload(numbered):
    eps = []
    for number, text in numbered:
        raw = parse_text(text)
        cues = [(t, text) for t, text in raw
                if t < WINDOW_SECONDS and text and not text.startswith(('♬', '♪'))]
        speakers = collections.Counter(
            m.group(1) for _, text in cues
            for m in [re.match(r'[（(]([^)）]{1,12})[)）]', text)] if m)
        narration = [f'{stamp(t)} {text}' for t, text in cues
                     if 'ナレーション' in text or text.startswith('〈')]
        markers = [t for t, text in cues if t >= 23 * 60 and '次回' in text]
        marker = markers[-1] if markers else None
        # A labelled candidate excerpt, not a definitive segmentation.
        preview = [f'{stamp(t)} {text}' for t, text in cues
                   if marker is not None and marker - 25 <= t <= marker + 20]
        hits = {key: [stamp(t) for t, text in cues if re.search(pattern, text)]
                for key, pattern in TERMS.items()}
        eps.append({
            'ep': number,
            'full_spoken_caption_read': number in FULL_READ,
            'non_music_cues_in_heuristic_window': len(cues),
            'last_indexed_cue': stamp(cues[-1][0]) if cues else None,
            'speakers': [{'name': name, 'tagged_cues': count}
                         for name, count in speakers.most_common(12)],
            'narration_cues': narration,
            'next_episode_marker': stamp(marker) if marker is not None else None,
            'preview_candidates': preview,
            'hits': {key: values for key, values in hits.items() if values},
        })
    return {
        'owner': 'per-episode caption search index, with a transparent heuristic window',
        'source': 'Japanese SRTs; earlier records attribute redistribution to Kitsunekko, unverified here; official/broadcast origin and cut unverified',
        'scope': 'All files searched/indexed, not all read in full. Speech only; silent visual staging not checked.',
        'boundary_note': 'Includes nonmusic cues before 29:00; preview candidate windows are heuristic; some files contain unrelated later broadcast material. Verify against the individual file and actual video.',
        'count': len(eps),
        'full_spoken_caption_reads': sorted(FULL_READ),
        'eps': eps,
    }


def write_atomic(target, text, allow_existing):
    if target.is_symlink() or (target.exists() and not allow_existing):
        raise ValueError(f'Output already exists or is a symlink; not overwritten: {target}')
    if not target.parent.is_dir():
        raise ValueError(f'Output directory does not exist: {target.parent}')
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         prefix='.episode-index-', dir=target.parent,
                                         delete=False) as stream:
            temp = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
        temp = None
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', help='291-caption ZIP or extracted directory (overrides DBZ_SUBS)')
    output = parser.add_mutually_exclusive_group()
    output.add_argument('--output', help='write to a new file, refusing to overwrite')
    output.add_argument('--write', action='store_true', help='replace selected episodes.json after preserving its previous version')
    args = parser.parse_args()
    source = Path(args.source or os.environ.get('DBZ_SUBS') or
                  (LOCAL_ARCHIVE if LOCAL_ARCHIVE.is_file() else DEFAULT_CAPTIONS))
    try:
        numbered = numbered_captions(source)
        payload = make_payload(numbered)
        text = json.dumps(payload, ensure_ascii=False, indent=1) + '\n'
        if args.write:
            write_atomic(OUT, text, allow_existing=True)
            print(f'{len(numbered)} captions indexed -> {OUT}; preserve/reseal the project and workshop as needed.')
        elif args.output:
            target = Path(args.output)
            if target.resolve() == source.resolve():
                raise ValueError('Output cannot replace the source archive or directory.')
            write_atomic(target, text, allow_existing=False)
            print(f'{len(numbered)} captions indexed -> {target}; selected index unchanged.')
        else:
            if not OUT.is_file() or OUT.is_symlink():
                raise ValueError(f'Selected index missing or unsafe: {OUT}; no index was written.')
            if OUT.read_text(encoding='utf-8') != text:
                raise ValueError(f'Generated index differs from {OUT}; no index was written. Review before --write.')
            print(f'{len(numbered)} captions reproduce the selected index exactly; no index was written.')
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f'Episode index: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
