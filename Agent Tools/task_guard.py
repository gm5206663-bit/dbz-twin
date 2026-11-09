#!/usr/bin/env python3
"""Optional task-completion prompts and safely scoped scratch cleanup.

The checklist is self-reported: this program does not verify the truth of notes,
control the assistant, publish content, or remove anything outside its own
marked temporary task directories. No credentials or user deliverables belong
in the scratch directory or in checklist notes.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import unittest

MARKER = 'arena-agent-owned-scratch-v1\n'
MARKER_NAME = '.agent-scratch-marker'
STATE_NAME = 'task-state.json'
ROOT = Path(tempfile.gettempdir()) / f'arena-agent-scratch-{os.getuid()}'

OPTIONS = {
    'scope': ('clear', 'unclear'),
    'result': ('complete', 'partial', 'blocked'),
    'verification': ('checked', 'not-applicable', 'blocked'),
    'sync': ('done-and-verified', 'suggested', 'not-authorized', 'not-applicable', 'blocked'),
    'cleanup': ('reviewed', 'blocked'),
}


class GuardError(Exception):
    """Refuse an unsafe operation or an incomplete completion check."""


def prepare_root(root: Path) -> None:
    """Use only a private real directory belonging to the current user."""
    try:
        root.mkdir(mode=0o700, exist_ok=True)
        info = root.lstat()
    except OSError as exc:
        raise GuardError(f'Cannot access scratch root: {exc}') from exc
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise GuardError('Scratch root must be a real directory owned by this user.')
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise GuardError('Scratch root must not be accessible to other users.')


def _regular_file(path: Path) -> None:
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise GuardError(f'Missing required scratch metadata: {path.name}') from exc
    if not stat.S_ISREG(mode):
        raise GuardError(f'Scratch metadata must be a regular file: {path.name}')


def _validate(root: Path, path: Path) -> Path:
    """Accept only a real direct child of our root with our marker and state."""
    prepare_root(root)
    if not path.is_absolute() or not path.name.startswith('task-'):
        raise GuardError('Expected an absolute, assistant-created task directory.')
    try:
        info = path.lstat()
        same_parent = path.parent.resolve(strict=True) == root.resolve(strict=True)
    except OSError as exc:
        raise GuardError('Task directory does not exist.') from exc
    if not same_parent or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise GuardError('Refusing a path outside the managed scratch root or a symlink.')
    marker, state = path / MARKER_NAME, path / STATE_NAME
    _regular_file(marker)
    _regular_file(state)
    try:
        if marker.read_text(encoding='utf-8') != MARKER:
            raise GuardError('Scratch ownership marker does not match.')
    except OSError as exc:
        raise GuardError('Cannot read the scratch ownership marker.') from exc
    return path


def _read_state(path: Path) -> dict:
    try:
        data = json.loads((path / STATE_NAME).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise GuardError('Invalid task state; nothing was removed.') from exc
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('items'), dict):
        raise GuardError('Invalid task state; nothing was removed.')
    if not isinstance(data.get('summary'), str) or not data['summary'].strip():
        raise GuardError('Invalid task summary; nothing was removed.')
    return data


def _save_state(path: Path, state: dict) -> None:
    fd, filename = tempfile.mkstemp(prefix='.state-', dir=path, text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(state, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
        os.replace(filename, path / STATE_NAME)
    except BaseException:
        try:
            os.unlink(filename)
        except FileNotFoundError:
            pass
        raise


def begin(root: Path, summary: str) -> Path:
    summary = summary.strip()
    if not summary or len(summary) > 500:
        raise GuardError('Provide a task summary between 1 and 500 characters; no secrets.')
    prepare_root(root)
    path = Path(tempfile.mkdtemp(prefix='task-', dir=root))
    try:
        marker_fd = os.open(path / MARKER_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(marker_fd, 'w', encoding='utf-8') as stream:
            stream.write(MARKER)
        _save_state(path, {'version': 1, 'summary': summary, 'items': {}})
    except BaseException:
        shutil.rmtree(path, ignore_errors=True)
        raise
    return path


def record(root: Path, path: Path, item: str, status: str, note: str) -> None:
    if item not in OPTIONS or status not in OPTIONS[item]:
        raise GuardError('Invalid checklist item or status.')
    note = note.strip()
    if not note or len(note) > 600:
        raise GuardError('Provide a factual note between 1 and 600 characters; no secrets.')
    path = _validate(root, path)
    state = _read_state(path)
    state['items'][item] = {'status': status, 'note': note}
    _save_state(path, state)


def review(root: Path, path: Path) -> tuple[dict, list[str]]:
    path = _validate(root, path)
    state = _read_state(path)
    missing = []
    for item, allowed in OPTIONS.items():
        entry = state['items'].get(item)
        if (not isinstance(entry, dict) or entry.get('status') not in allowed
                or not isinstance(entry.get('note'), str) or not entry['note'].strip()):
            missing.append(item)
    return state, missing


def finish(root: Path, path: Path) -> dict:
    state, missing = review(root, path)
    if missing:
        raise GuardError('Cannot finish: record ' + ', '.join(missing) + '. Scratch was kept.')
    # Revalidate immediately before deleting; shutil.rmtree does not follow
    # symlinks contained in this directory on supported Python platforms.
    path = _validate(root, path)
    if not getattr(shutil.rmtree, 'avoids_symlink_attacks', False):
        raise GuardError('Safe symlink-resistant scratch cleanup is unavailable.')
    shutil.rmtree(path)
    try:
        root.rmdir()  # only succeeds when no other task folders remain
    except OSError:
        pass
    return state


def selftest() -> None:
    class Tests(unittest.TestCase):
        def setUp(self):
            self.temp = tempfile.TemporaryDirectory(prefix='agent-guard-test-')
            self.base = Path(self.temp.name)
            self.root = self.base / 'scratch'
            self.task = begin(self.root, 'An isolated test task')

        def tearDown(self):
            self.temp.cleanup()

        def fill(self, path=None):
            path = path or self.task
            values = {'scope': 'clear', 'result': 'complete', 'verification': 'checked',
                      'sync': 'not-applicable', 'cleanup': 'reviewed'}
            for item, value in values.items():
                record(self.root, path, item, value, 'Test evidence')

        def test_incomplete_task_is_not_removed(self):
            with self.assertRaises(GuardError):
                finish(self.root, self.task)
            self.assertTrue(self.task.exists())

        def test_finish_removes_only_completed_task(self):
            other = begin(self.root, 'Another task')
            self.fill()
            finish(self.root, self.task)
            self.assertFalse(self.task.exists())
            self.assertTrue(other.exists())

        def test_outside_directory_is_never_removed(self):
            outside = self.base / 'task-outside'
            outside.mkdir()
            (outside / MARKER_NAME).write_text(MARKER, encoding='utf-8')
            (outside / STATE_NAME).write_text('{}', encoding='utf-8')
            with self.assertRaises(GuardError):
                finish(self.root, outside)
            self.assertTrue(outside.exists())

        def test_symlink_task_is_rejected(self):
            link = self.root / 'task-link'
            link.symlink_to(self.base, target_is_directory=True)
            with self.assertRaises(GuardError):
                finish(self.root, link)
            self.assertTrue(self.base.exists())

        def test_contents_symlink_is_not_followed(self):
            treasure = self.base / 'user-file.txt'
            treasure.write_text('keep', encoding='utf-8')
            (self.task / 'external-link').symlink_to(treasure)
            self.fill()
            finish(self.root, self.task)
            self.assertEqual(treasure.read_text(encoding='utf-8'), 'keep')

        def test_marker_symlink_is_rejected(self):
            marker = self.task / MARKER_NAME
            marker.unlink()
            other = self.base / 'marker'
            other.write_text(MARKER, encoding='utf-8')
            marker.symlink_to(other)
            with self.assertRaises(GuardError):
                finish(self.root, self.task)
            self.assertTrue(self.task.exists())

        def test_corrupt_state_is_not_removed(self):
            (self.task / STATE_NAME).write_text('{oops', encoding='utf-8')
            with self.assertRaises(GuardError):
                finish(self.root, self.task)
            self.assertTrue(self.task.exists())

        def test_state_symlink_is_rejected(self):
            state = self.task / STATE_NAME
            state.unlink()
            outside = self.base / 'user-state.txt'
            outside.write_text('{}', encoding='utf-8')
            state.symlink_to(outside)
            with self.assertRaises(GuardError):
                finish(self.root, self.task)
            self.assertTrue(outside.exists())
            self.assertTrue(self.task.exists())

        def test_unmarked_directory_is_not_removed(self):
            outside = self.root / 'task-unmarked'
            outside.mkdir()
            (outside / 'valuable.txt').write_text('keep', encoding='utf-8')
            with self.assertRaises(GuardError):
                finish(self.root, outside)
            self.assertEqual((outside / 'valuable.txt').read_text(encoding='utf-8'), 'keep')

        def test_invalid_or_empty_entry_is_rejected(self):
            with self.assertRaises(GuardError):
                record(self.root, self.task, 'result', 'perfect', 'Test')
            with self.assertRaises(GuardError):
                record(self.root, self.task, 'result', 'complete', '   ')

        def test_blocked_result_can_be_reported_honestly(self):
            self.fill()
            record(self.root, self.task, 'result', 'blocked', 'Could not complete')
            state = finish(self.root, self.task)
            self.assertEqual(state['items']['result']['status'], 'blocked')

        def test_shared_root_is_rejected(self):
            self.root.chmod(0o755)
            with self.assertRaises(GuardError):
                begin(self.root, 'Must not start')
            self.root.chmod(0o700)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    new = sub.add_parser('begin', help='Create a private, disposable assistant scratch folder.')
    new.add_argument('--summary', required=True, help='Short task description; do not include secrets.')
    mark = sub.add_parser('record', help='Record one self-reported checklist decision.')
    mark.add_argument('path', type=Path)
    mark.add_argument('item', choices=OPTIONS)
    mark.add_argument('status', help='One of the statuses listed by choices.')
    mark.add_argument('--note', required=True, help='Brief factual evidence; do not include secrets.')
    check = sub.add_parser('status', help='Show recorded and missing decisions.')
    check.add_argument('path', type=Path)
    done = sub.add_parser('finish', help='Require the checklist and remove only this managed scratch folder.')
    done.add_argument('path', type=Path)
    sub.add_parser('choices', help='Show allowed checklist statuses.')
    sub.add_parser('selftest', help='Run isolated tests; no project files are touched.')
    args = parser.parse_args()
    try:
        if args.command == 'begin':
            print(begin(ROOT, args.summary))
        elif args.command == 'record':
            record(ROOT, args.path, args.item, args.status, args.note)
            print(f'Recorded {args.item}: {args.status}.')
        elif args.command == 'status':
            state, missing = review(ROOT, args.path)
            print('Task:', state['summary'])
            for item in OPTIONS:
                entry = state['items'].get(item)
                print(f"{item}: {entry['status']} — {entry['note']}" if isinstance(entry, dict) and item not in missing else f'{item}: MISSING')
        elif args.command == 'finish':
            state = finish(ROOT, args.path)
            print('Task:', state['summary'])
            for item in OPTIONS:
                entry = state['items'][item]
                print(f"{item}: {entry['status']} — {entry['note']}")
            print('Managed scratch removed. Checklist entries are self-reported.')
        elif args.command == 'choices':
            for item, values in OPTIONS.items():
                print(f"{item}: {', '.join(values)}")
        else:
            selftest()
    except (GuardError, OSError) as exc:
        print(f'Task guard: {exc}', file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == '__main__':
    main()
