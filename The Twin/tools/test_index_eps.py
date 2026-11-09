#!/usr/bin/env python3
"""Safety and reproducibility fixtures for the caption indexer."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

import index_eps


class EpisodeIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='episode-index-test-')
        self.root = Path(self.temp.name)
        self.captions = self.root / 'captions'
        self.captions.mkdir()
        self.sample = '1\n00:00:01,000 --> 00:00:02,000\n(悟飯)修行だ。\n\n2\n00:29:01,000 --> 00:29:02,000\n月は遠い。\n'
        for number in range(1, 292):
            (self.captions / f'Dragon_Ball_Z_{number:03}.srt').write_text(self.sample, encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def make_zip(self, duplicate=False):
        path = self.root / 'captions.zip'
        with zipfile.ZipFile(path, 'w') as z:
            for file in self.captions.iterdir():
                z.write(file, file.name)
            if duplicate:
                z.writestr('other/Dragon_Ball_Z_001.srt', self.sample)
        return path

    def test_zip_and_directory_create_identical_index(self):
        from_directory = index_eps.numbered_captions(self.captions)
        from_zip = index_eps.numbered_captions(self.make_zip())
        self.assertEqual(from_directory, from_zip)
        self.assertEqual(index_eps.make_payload(from_directory), index_eps.make_payload(from_zip))
        self.assertEqual(len(from_zip), 291)

    def test_recorded_full_read_flags_preserve_the_documented_boundary(self):
        payload = index_eps.make_payload(index_eps.numbered_captions(self.captions))
        expected = (set(range(1, 118))
                    | {183, 184, 205, 206, 207, 208, 256, 257}
                    | {123, 125, 139, 145, 153, 169, 170, 171, 181, 182,
                       191, 200, 201, 212, 229, 237, 253, 254, 285, 288, 291})
        self.assertEqual(set(payload['full_spoken_caption_reads']), expected)
        self.assertEqual(len(expected), 146)
        self.assertTrue(payload['eps'][116]['full_spoken_caption_read'])
        self.assertFalse(payload['eps'][117]['full_spoken_caption_read'])
        self.assertTrue(payload['eps'][122]['full_spoken_caption_read'])
        self.assertFalse(payload['eps'][123]['full_spoken_caption_read'])
        self.assertTrue(payload['eps'][290]['full_spoken_caption_read'])

    def test_incomplete_source_is_rejected(self):
        (self.captions / 'Dragon_Ball_Z_291.srt').unlink()
        with self.assertRaisesRegex(ValueError, '291 distinct'):
            index_eps.numbered_captions(self.captions)

    def test_duplicate_episode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, '291 distinct'):
            index_eps.numbered_captions(self.make_zip(duplicate=True))

    def test_twenty_nine_minute_limit_is_applied(self):
        result = index_eps.make_payload(index_eps.numbered_captions(self.captions))['eps'][0]
        self.assertEqual(result['non_music_cues_in_heuristic_window'], 1)
        self.assertEqual(result['hits'].get('train'), ['00:01'])
        self.assertNotIn('moon', result['hits'])

    def test_existing_and_symlink_outputs_are_not_overwritten(self):
        target = self.root / 'index.json'
        target.write_text('preserved', encoding='utf-8')
        with self.assertRaises(ValueError):
            index_eps.write_atomic(target, 'new', allow_existing=False)
        self.assertEqual(target.read_text(encoding='utf-8'), 'preserved')
        link = self.root / 'link.json'
        link.symlink_to(target)
        with self.assertRaises(ValueError):
            index_eps.write_atomic(link, 'new', allow_existing=True)
        self.assertEqual(target.read_text(encoding='utf-8'), 'preserved')

    def test_default_check_does_not_write_selected_index(self):
        source = self.make_zip()
        selected = self.root / 'selected.json'
        content = 'not the generated index'
        selected.write_text(content, encoding='utf-8')
        with mock.patch.object(index_eps, 'OUT', selected), \
             mock.patch('sys.argv', ['index_eps.py', '--source', str(source)]), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(index_eps.main(), 1)
        self.assertEqual(selected.read_text(encoding='utf-8'), content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
