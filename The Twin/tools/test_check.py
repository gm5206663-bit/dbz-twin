#!/usr/bin/env python3
"""Focused regression tests for the Twin checker; uses only temporary fixtures."""
import pathlib
import tempfile
import unittest

import check


class CheckerFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="twin-check-fixtures-")
        self.previous_root = check.ROOT
        check.ROOT = pathlib.Path(self.temp.name)
        (check.ROOT / "chapters").mkdir()
        check.P.clear()
        check.F.clear()

    def tearDown(self):
        check.ROOT = self.previous_root
        check.P.clear()
        check.F.clear()
        self.temp.cleanup()

    def test_selftest_inserts_into_first_visible_scene_with_any_title(self):
        chapter = "# Chapter One\n\n## The Mountain Morning\n\nStory.\n<!--\n## Footer\nHistory.\n-->\n"
        altered = check.insert_selftest_prose(chapter, "Broc.")
        self.assertIn("## The Mountain Morning\n\nBroc.\n", altered)
        self.assertEqual(altered.split("<!--", 1)[1], chapter.split("<!--", 1)[1])

    def test_selftest_refuses_a_footer_only_heading(self):
        with self.assertRaises(ValueError):
            check.insert_selftest_prose("# Title\n<!--\n## Footer\n-->\n", "Broc.")

    def test_band_includes_cold_open_and_excludes_metadata(self):
        story = (
            "# Chapter Example\n\n```\nMETADATA_DO_NOT_COUNT\n```\n\n"
            "FIRST_SCENE stays here.\n\n---\n\nSECOND_SCENE stays too.\n"
            "## Footer\nFOOTER_DO_NOT_COUNT\n"
        )
        prose = check.band_prose(story)
        self.assertIn("FIRST_SCENE", prose)
        self.assertIn("SECOND_SCENE", prose)
        self.assertNotIn("METADATA_DO_NOT_COUNT", prose)
        self.assertNotIn("FOOTER_DO_NOT_COUNT", prose)
        hidden_footer = "# Chapter Fixture\n\nThe story remains.\n\n<!--\n## Footer\nsecret\n-->\n"
        clean = check.band_prose(hidden_footer)
        self.assertIn("The story remains.", clean)
        self.assertNotIn("<!--", clean)
        self.assertEqual(check.sentence_runs(clean), [3])

    def test_counting_cold_open_still_rejects_short_chapters(self):
        chapter = check.ROOT / "chapters" / "Chapter_99_Fixture.md"
        lines = []
        for i in range(465):
            words = "One two three four five six seven eight nine ten."
            lines.append('"' + words + '"' if i % 5 < 3 else words)
        chapter.write_text("# Chapter Fixture\n\n" + "\n".join(lines[:100]) +
                           "\n\n---\n\n" + "\n".join(lines[100:]) +
                           "\n\n## Footer\n", encoding="utf-8")
        check.check_band()
        self.assertFalse(check.F, check.F)
        self.assertTrue(any("4650 words" in p for p in check.P), check.P)
        chapter.write_text("# Chapter Fixture\n\n" + "\n".join(lines[:100]) +
                           "\n\n---\n\n" + "\n".join(lines[100:250]) +
                           "\n\n## Footer\n", encoding="utf-8")
        check.P.clear()
        check.F.clear()
        check.check_band()
        self.assertTrue(any("2,500" in f or "2500" in f for f in check.F), check.F)
        self.assertFalse(any("Chapter_99_Fixture" in p for p in check.P), check.P)

    def test_titles_before_names_are_not_sentence_endings(self):
        prose = "Dr. Brief met Mr. Popo. He waved! Mrs. Vale smiled?"
        self.assertEqual(check.sentence_runs(prose), [5, 2, 3])
        # Actual periods remain boundaries, so a string of short sentences
        # still has the same short-sentence average as before.
        self.assertEqual(check.sentence_runs("He stops. She waits. They go."), [2, 2, 2])

    def test_dialogue_attribution_stays_with_its_question_or_exclamation(self):
        prose = '"Go!" Gohan shouts. Chi-Chi follows. "Where?" she asks.'
        self.assertEqual(check.sentence_runs(prose), [3, 2, 3])
        # An action is not a speech attribution, nor is a new paragraph.
        self.assertEqual(len(check.sentence_runs('"Go!" Gohan runs away.')), 2)
        self.assertEqual(len(check.sentence_runs('"Go!"\n\nGohan shouts.')), 2)

    def test_short_sentences_still_fail_after_dialogue_tag_correction(self):
        chapter = check.ROOT / "chapters" / "Chapter_99_Fixture.md"
        lines = ['"Go!" Gohan shouts.', 'Goku watches the tree by the river.'] * 450
        chapter.write_text("# Chapter Fixture\n\n" + "\n".join(lines) + "\n\n## Footer\n", encoding="utf-8")
        check.check_band()
        self.assertTrue(any("average sentence" in failure for failure in check.F), check.F)
        self.assertFalse(any("Chapter_99_Fixture" in result for result in check.P), check.P)

    def test_three_digit_witness_is_registered_and_unknown_ids_fail(self):
        import json
        canon = check.ROOT / "canon"
        canon.mkdir()
        (check.ROOT / "CANON.md").write_text(
            "| W-99 | existing |\n| W-100 | new source |\n", encoding="utf-8")
        data = {"facts": [{"id": "C001", "tier": "I", "statement": "A bounded fact.",
                          "source": "fixture", "source_class": "fixture",
                          "witnesses": ["W-100"], "strength": "A"}]}
        (canon / "facts.json").write_text(json.dumps(data), encoding="utf-8")
        note = canon / "note.md"
        note.write_text("Registered: W-100.\n", encoding="utf-8")
        check.check_facts()
        check.check_citations()
        self.assertFalse(check.F, check.F)
        check.P.clear()
        check.F.clear()
        note.write_text("Unknown: W-101.\n", encoding="utf-8")
        check.check_citations()
        self.assertTrue(any("W-101" in failure for failure in check.F), check.F)
        check.P.clear()
        check.F.clear()
        data["facts"][0]["witnesses"] = ["W-101"]
        (canon / "facts.json").write_text(json.dumps(data), encoding="utf-8")
        check.check_facts()
        self.assertTrue(any("W-101" in failure for failure in check.F), check.F)

    def test_dinosaur_exception_is_exact_and_does_not_hide_other_matches(self):
        chapter = check.ROOT / "chapters" / "Chapter_08_The_Dinosaur_by_the_River.md"
        reviewed = ("The large dinosaur breaks through the falling mud. "
                    "Gohan sets the small one down and backs away.")
        chapter.write_text("# Chapter Eight\n\nGoshin watches.\n\n" + reviewed + "\n", encoding="utf-8")
        check.check_names()
        self.assertFalse(check.F, check.F)
        check.P.clear()
        check.F.clear()
        chapter.write_text("# Chapter Eight\n\nGoshin watches.\n\n" + reviewed +
                           "\n\nThe small one returns to his brother.\n", encoding="utf-8")
        check.check_names()
        self.assertTrue(any("the small one" in f for f in check.F), check.F)


if __name__ == "__main__":
    unittest.main(verbosity=2)
