#!/usr/bin/env python3
"""Index 291 redistributed Japanese DBZ SRTs for search, not as a full reading.

The corpus's official/broadcast origin is not independently verified. Captioned
text is not visual evidence. Timestamps and boundaries are local-file heuristic;
verify an episode's actual content and next-episode preview before writing.
"""
import collections
import glob
import json
import os
import pathlib
import re

SRC = os.environ.get('DBZ_SUBS', '/home/user/tmp/subs/ex')
OUT = pathlib.Path(__file__).resolve().parents[1] / 'canon' / 'episodes.json'
# Some files contain a different TV program after about 30:40. 29 minutes keeps
# normal ending/preview speech (including past 26:00), while still bounding the
# index. This is a heuristic, NOT proof that every boundary is perfectly clean.
WINDOW_SECONDS = 29 * 60
FULL_READ = set(range(1, 37)) | {49, 55, 59, 61, 65, 79, 80, 81, 82, 83,
                                 183, 184, 205, 206, 207, 208, 256, 257}
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

def stamp(t):
    sec = int(t)
    return f'{sec // 60:02d}:{sec % 60:02d}'

def parse(path):
    text = pathlib.Path(path).read_text(encoding='utf-8-sig', errors='replace')
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

def main():
    eps = []
    paths = sorted(glob.glob(f'{SRC}/Dragon_Ball_Z_*.srt'))
    for path in paths:
        match = re.search(r'_(\d{3})\.srt$', path)
        if not match:
            continue
        number = int(match.group(1))
        raw = parse(path)
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
    payload = {
        'owner': 'per-episode caption search index, with a transparent heuristic window',
        'source': 'Japanese SRTs redistributed through Kitsunekko; official/broadcast origin unverified',
        'scope': 'All files searched/indexed, not all read in full. Speech only; silent visual staging not checked.',
        'boundary_note': 'Includes nonmusic cues before 29:00; preview candidate windows are heuristic; some files contain unrelated later broadcast material. Verify against the individual file and actual video.',
        'count': len(eps),
        'full_spoken_caption_reads': sorted(FULL_READ),
        'eps': eps,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{len(eps)} caption files indexed → {OUT}; {len(FULL_READ)} full spoken-caption reads recorded')
    if len(eps) != 291:
        raise SystemExit('Expected 291 files; check DBZ_SUBS')

if __name__ == '__main__':
    main()
