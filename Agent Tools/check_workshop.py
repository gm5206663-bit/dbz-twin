#!/usr/bin/env python3
"""Integrity check for the local workshop, including all persisted working files.

Default: compare every persisted regular file with WORKSHOP_MANIFEST.sha256 and
check local Markdown paths. --seal records intentional local changes; it does
not sync or publish. The manifest includes local paths and hashes; visibility
follows the author's direction. --selftest uses a disposable directory.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_NAME = "WORKSHOP_MANIFEST.sha256"
EXCLUDED_DIRS = {
    ".arena", ".cache", ".local", ".mypy_cache", ".next", ".nox", ".npm",
    ".nuxt", ".output", ".parcel-cache", ".playwright-cli", ".pytest_cache",
    ".ruff_cache", ".svelte-kit", ".tox", ".turbo", ".venv", ".vite",
    "__pycache__", "build", "coverage", "dist", "node_modules", "out", "target",
    ".git",
}
EXCLUDED_FILE_NAMES = {".git-credentials", ".netrc"}
DIGEST = re.compile(r"^[0-9a-f]{64}$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCED_CODE = re.compile(r"(?ms)^\s*```.*?^\s*```")


class WorkshopError(Exception):
    """A file, manifest, or link could not be checked safely."""


def _walk_error(error: OSError) -> None:
    raise WorkshopError(str(error)) from error


def workspace_files(root: Path) -> dict[str, Path]:
    """Return persisted regular files without following links or credentials."""
    root = root.resolve(strict=True)
    found: dict[str, Path] = {}
    for directory, names, filenames in os.walk(root, followlinks=False, onerror=_walk_error):
        base = Path(directory)
        kept = []
        for name in sorted(names):
            if name in EXCLUDED_DIRS:
                continue
            candidate = base / name
            if candidate.is_symlink():
                raise WorkshopError(f"Symlinked directory requires manual review: {candidate.relative_to(root)}")
            kept.append(name)
        names[:] = kept
        for name in sorted(filenames):
            if name in EXCLUDED_FILE_NAMES:
                continue
            path = base / name
            rel = path.relative_to(root).as_posix()
            if rel == MANIFEST_NAME:
                continue
            if any(c in rel for c in "\r\n\\"):
                raise WorkshopError(f"Filename cannot be represented safely in this manifest: {rel!r}")
            if path.is_symlink():
                raise WorkshopError(f"Symlinked file requires manual review: {rel}")
            if not stat.S_ISREG(path.stat().st_mode):
                raise WorkshopError(f"Non-regular file requires manual review: {rel}")
            found[rel] = path
    return dict(sorted(found.items()))


def file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def read_manifest(root: Path) -> dict[str, str]:
    target = root / MANIFEST_NAME
    if not target.is_file() or target.is_symlink():
        raise WorkshopError(f"Missing or unsafe {MANIFEST_NAME}")
    rows: dict[str, str] = {}
    for number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if "  " not in line:
            raise WorkshopError(f"Malformed manifest line {number}")
        digest, rel = line.split("  ", 1)
        parts = PurePosixPath(rel)
        if not DIGEST.fullmatch(digest) or not rel or parts.is_absolute() or ".." in parts.parts:
            raise WorkshopError(f"Invalid digest or path on manifest line {number}")
        if rel in rows:
            raise WorkshopError(f"Duplicate path in manifest: {rel}")
        rows[rel] = digest
    return rows


def seal(root: Path) -> int:
    """Atomically record the current local files, never the manifest itself."""
    root = root.resolve(strict=True)
    files = workspace_files(root)
    text = "".join(f"{file_hash(path)}  {rel}\n" for rel, path in files.items())
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         prefix=".workshop-manifest-", dir=root,
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, root / MANIFEST_NAME)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return len(files)


def verify(root: Path) -> tuple[int, list[str]]:
    root = root.resolve(strict=True)
    actual = workspace_files(root)
    expected = read_manifest(root)
    errors: list[str] = []
    for rel in sorted(set(expected) - set(actual)):
        errors.append(f"Missing: {rel}")
    for rel in sorted(set(actual) - set(expected)):
        errors.append(f"Unrecorded: {rel}")
    for rel in sorted(set(actual) & set(expected)):
        if file_hash(actual[rel]) != expected[rel]:
            errors.append(f"Changed: {rel}")
    return len(actual), errors


def check_markdown_links(root: Path) -> tuple[int, list[str]]:
    """Check relative file paths, not external URLs or heading anchors."""
    root = root.resolve(strict=True)
    files = workspace_files(root)
    count = 0
    errors: list[str] = []
    for rel, path in files.items():
        if path.suffix.lower() != ".md":
            continue
        text = FENCED_CODE.sub("", path.read_text(encoding="utf-8"))
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).strip().split(" ", 1)[0]
            if re.match(r"^(?:https?://|mailto:|tel:|#|data:)", target, re.I):
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            url = urlsplit(target)
            if url.scheme or not url.path:
                continue
            count += 1
            destination = (path.parent / unquote(url.path)).resolve()
            if not destination.exists():
                errors.append(f"{rel}: {target}")
    return count, errors


def selftest() -> bool:
    class Tests(unittest.TestCase):
        def setUp(self) -> None:
            self.temp = tempfile.TemporaryDirectory(prefix="workshop-check-")
            self.root = Path(self.temp.name)
            (self.root / "Sara").mkdir()
            (self.root / "Sara" / "SARA.md").write_text("Private fixture.\n", encoding="utf-8")
            (self.root / "README.md").write_text("[private](Sara/SARA.md)\n", encoding="utf-8")
            (self.root / ".cache").mkdir()
            (self.root / ".cache" / "ignored").write_text("generated", encoding="utf-8")
            (self.root / ".netrc").write_text("excluded fixture", encoding="utf-8")

        def tearDown(self) -> None:
            self.temp.cleanup()

        def test_seal_includes_private_files_but_excludes_cache_credentials_and_itself(self) -> None:
            self.assertEqual(seal(self.root), 2)
            count, errors = verify(self.root)
            self.assertEqual((count, errors), (2, []))
            self.assertEqual(set(read_manifest(self.root)), {"README.md", "Sara/SARA.md"})

        def test_changed_missing_and_unrecorded_are_detected(self) -> None:
            seal(self.root)
            (self.root / "README.md").write_text("changed", encoding="utf-8")
            (self.root / "Sara" / "SARA.md").unlink()
            (self.root / "new.txt").write_text("new", encoding="utf-8")
            _, errors = verify(self.root)
            self.assertTrue(any(x.startswith("Changed:") for x in errors))
            self.assertTrue(any(x.startswith("Missing:") for x in errors))
            self.assertTrue(any(x.startswith("Unrecorded:") for x in errors))

        def test_local_links_are_checked(self) -> None:
            self.assertEqual(check_markdown_links(self.root), (1, []))
            (self.root / "Sara" / "SARA.md").unlink()
            count, errors = check_markdown_links(self.root)
            self.assertEqual(count, 1)
            self.assertEqual(len(errors), 1)

        def test_unsafe_manifest_path_is_rejected(self) -> None:
            (self.root / MANIFEST_NAME).write_text("0" * 64 + "  ../outside\n", encoding="utf-8")
            with self.assertRaises(WorkshopError):
                read_manifest(self.root)

        def test_symlink_is_not_followed(self) -> None:
            (self.root / "link").symlink_to(self.root / "README.md")
            with self.assertRaises(WorkshopError):
                workspace_files(self.root)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--seal", action="store_true", help="Record intentional current local file hashes")
    group.add_argument("--selftest", action="store_true", help="Run isolated integrity and safety tests")
    args = parser.parse_args()
    if args.selftest:
        return 0 if selftest() else 1
    try:
        if args.seal:
            print(f"Recorded {seal(ROOT)} local files in {MANIFEST_NAME}.")
        count, errors = verify(ROOT)
        links, bad_links = check_markdown_links(ROOT)
        print(f"Workshop integrity: {count} files; {len(errors)} mismatches.")
        print(f"Local Markdown paths: {links} checked; {len(bad_links)} unresolved.")
        for issue in errors + bad_links:
            print(f"  FAIL {issue}")
        print("Scope: local persisted files; excludes the manifest itself, generated/cache directories, Git metadata and credential paths.")
        print("Working-file paths and hashes are included; visibility follows the author's direction.")
        print("Hashes and link checks do not establish story quality, source completeness, acceptance or remote sync.")
        return 1 if errors or bad_links else 0
    except (OSError, UnicodeError, WorkshopError, ValueError) as error:
        print(f"Workshop check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
