#!/usr/bin/env python3
"""Focused regression tests for the Twin checker; uses only temporary fixtures."""
import pathlib
import tempfile
import unittest
from unittest import mock

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

    def test_selftest_mutations_are_isolated_and_temporary(self):
        original_root = check.ROOT
        chapter = original_root / "chapters" / "test.md"
        chapter.write_text("original", encoding="utf-8")
        fixture_roots = []

        def simulate_negative_test():
            fixture_roots.append(check.ROOT)
            (check.ROOT / "chapters" / "test.md").write_text("injected", encoding="utf-8")
            return 0

        with mock.patch.object(check, "_selftest_in_root", side_effect=simulate_negative_test):
            self.assertEqual(check.selftest(), 0)
        self.assertEqual(check.ROOT, original_root)
        self.assertEqual(chapter.read_text(encoding="utf-8"), "original")
        self.assertEqual(len(fixture_roots), 1)
        self.assertNotEqual(fixture_roots[0], original_root)
        self.assertFalse(fixture_roots[0].exists())

    def test_selftest_restores_root_and_cleans_up_on_failure(self):
        original_root = check.ROOT
        fixture_roots = []

        def fail_inside_fixture():
            fixture_roots.append(check.ROOT)
            raise RuntimeError("fixture failed")

        with mock.patch.object(check, "_selftest_in_root", side_effect=fail_inside_fixture):
            with self.assertRaisesRegex(RuntimeError, "fixture failed"):
                check.selftest()
        self.assertEqual(check.ROOT, original_root)
        self.assertEqual(len(fixture_roots), 1)
        self.assertFalse(fixture_roots[0].exists())

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

    def test_alternate_continuity_note_is_not_story_or_prose_metrics(self):
        story = ("# Chapter Fixture\n\n## First scene\nThe first scene stays.\n\n"
                 "---\n\n## Next scene\nThe second scene stays.\n\n")
        note = ("### Continuity and source note\n\n"
                "This is explanatory metadata, not a story sentence.\n\n"
                "```text\nANIME BASE: a source\n```\n\n"
                "This draft awaits the author's review.\n")
        self.assertEqual(check.band_prose(story + note), check.band_prose(story))

    def test_metadata_boundary_applies_to_story_checks_but_not_story_text(self):
        chapter = check.ROOT / "chapters" / "Chapter_99_Fixture.md"
        story = "# Chapter Fixture\n\n## Scene\nRoshi watches Goku by the river.\n\n"
        terms = "Broc. The pure light carries divine ki. Nobody saw the old man.\n"
        checks = (check.check_reveal, check.check_purity, check.check_era,
                  check.check_names, check.check_flow)
        for heading in ("## Footer\n", "<!--\n## Footer\n",
                        "### Continuity and source note\n"):
            for placement in ("metadata", "story"):
                body = (story + heading + "\n" + terms if placement == "metadata"
                        else story + terms + "\n" + heading)
                chapter.write_text(body, encoding="utf-8")
                for fn in checks:
                    with self.subTest(check=fn.__name__, heading=heading, placement=placement):
                        check.P.clear(); check.F.clear()
                        fn()
                        if placement == "metadata":
                            self.assertFalse(check.F, check.F)
                        else:
                            self.assertTrue(check.F, check.P)

    def test_footer_like_heading_inside_a_fence_does_not_end_story(self):
        text = ("# Chapter Fixture\n\n```text\n## Footer\nnot a real footer\n```\n\n"
                "## The scene\nThe actual story remains.\n\n"
                "### Continuity and source note\nThis note is metadata.\n")
        prose = check.band_prose(text)
        self.assertIn("The actual story remains.", prose)
        self.assertNotIn("This note is metadata.", prose)

    def test_story_boundary_masks_comments_and_preserves_story_offsets(self):
        text = ("# Chapter Fixture\n\n<!-- A hidden note about divine ki. -->\n\n"
                "~~~text\n### Continuity and source note\nexample only\n~~~\n\n"
                "## The scene\nThe story mentions ## Footer in a sentence.\n\n"
                "### Continuity and source note\nThis is metadata.\n")
        clean = check.chapter_prose(text)
        self.assertNotIn("divine ki", clean)
        self.assertNotIn("example only", clean)
        self.assertIn("The story mentions ## Footer in a sentence.", clean)
        self.assertNotIn("This is metadata.", clean)
        self.assertEqual(clean.index("## The scene"), text.index("## The scene"))
        altered = check.insert_selftest_prose(text, "Broc.")
        self.assertIn("## The scene\n\nBroc.\n", altered)

    def test_footer_example_in_comment_cannot_hide_later_story(self):
        text = ("# Chapter Fixture\n\n<!-- an example\n## Footer\n"
                "This is not the real end of the story.\n-->\n\n"
                "## The scene\nThe story contains divine ki.\n")
        body = check.chapter_prose(text)
        self.assertIn("The story contains divine ki.", body)
        self.assertNotIn("This is not the real end", body)
        self.assertEqual(body.index("## The scene"), text.index("## The scene"))
        chapter = check.ROOT / "chapters" / "Chapter_99_Fixture.md"
        chapter.write_text(text, encoding="utf-8")
        check.check_era()
        self.assertTrue(check.F, "A later story violation must not be hidden by a comment")

    def test_comment_and_fence_delimiters_do_not_leak_between_states(self):
        text = ("# Chapter Fixture\n\n```text\n<!-- unclosed code example\n```\n\n"
                "<!--\n~~~text\n### Continuity and source note\n~~~\n-->\n\n"
                "## The scene\nThe actual story stays.\n\n"
                "### Continuity and source note\nThis is metadata.\n")
        body = check.chapter_prose(text)
        self.assertIn("The actual story stays.", body)
        self.assertNotIn("unclosed code example", body)
        self.assertNotIn("This is metadata.", body)
        self.assertEqual(body.index("## The scene"), text.index("## The scene"))
        unclosed = check.chapter_prose("# Title\n\n<!-- unfinished\nHidden text.\n")
        self.assertNotIn("Hidden text.", unclosed)

    def test_selftest_refuses_a_visible_footer_only_heading(self):
        with self.assertRaises(ValueError):
            check.insert_selftest_prose("# Title\n\n## Footer\nmetadata\n", "Broc.")

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

    def test_visible_episode_reference_must_follow_title(self):
        chapter = check.ROOT / "chapters" / "Chapter_99_Fixture.md"
        label = ("*Anime episode reference: Dragon Ball Z, Episodes 23–24 "
                 "(selected scenes); Episode 31 brought forward.*")
        chapter.write_text("# Chapter Fixture\n\n" + label + "\n\nStory.\n", encoding="utf-8")
        check.check_episode_references()
        self.assertFalse(check.F, check.F)
        self.assertTrue(any("accuracy" in result for result in check.P), check.P)
        for body in (
            "# Chapter Fixture\n\nStory.\n\n<!--\n" + label + "\n-->\n",
            "# Chapter Fixture\n\n*Draft.*\n\n" + label + "\n\nStory.\n",
            "# Chapter Fixture\n\nStory.\n",
        ):
            check.P.clear()
            check.F.clear()
            chapter.write_text(body, encoding="utf-8")
            check.check_episode_references()
            self.assertTrue(any("missing or misplaced" in f for f in check.F), check.F)

    def test_episode_label_does_not_change_prose_metrics(self):
        before = "# Chapter Fixture\n\n*Draft.*\n\nOne two three.\n\n---\n\nFour five.\n"
        label = "*Anime episode reference: Dragon Ball Z, Episodes 23–24.*\n\n"
        after = before.replace("# Chapter Fixture\n\n", "# Chapter Fixture\n\n" + label, 1)
        plain = check.band_prose(before)
        labelled = check.band_prose(after)
        self.assertEqual(plain.split(), labelled.split())
        self.assertEqual(check.sentence_runs(plain), check.sentence_runs(labelled))
        self.assertNotIn("Anime episode reference", labelled)

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

    def make_hybrid_fixture(self):
        import json
        for name in check.HYBRID_RULE_PATHS:
            path = check.ROOT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("His whole Saiyan–Earthling hybrid bloodline develops.\n", encoding="utf-8")
        canon = check.ROOT / "canon"
        canon.mkdir(exist_ok=True)
        facts = {"facts": [
            {"id": "O230", "statement": "His whole Saiyan–Earthling hybrid bloodline becomes purer, deeper and stronger.",
             "previous_statement": "His Saiyan bloodline becomes purer."},
            {"id": "O243", "statement": "The Saiyan–Earthling hybrid inheritance is the whole bloodline."},
            {"id": "O244", "statement": "The Saiyan–Earthling hybrid potential and Talent develop across the whole existence."},
        ]}
        (canon / "facts.json").write_text(json.dumps(facts), encoding="utf-8")
        chapter = check.ROOT / "chapters" / "Chapter_27_The_Space_to_Stand.md"
        chapter.write_text("Strength from both parents grows.\n<!--\n## Footer\n"
                           "The Saiyan strength in him feels deeper now.\n-->\n", encoding="utf-8")
        return facts, chapter

    def test_hybrid_guard_allows_preserved_historical_wording(self):
        self.make_hybrid_fixture()
        check.check_hybrid_bloodline()
        self.assertFalse(check.F, check.F)
        self.assertTrue(any("HYBRID REGRESSION" in p for p in check.P), check.P)

    def test_hybrid_guard_flags_exact_old_rule_and_chapter_sentence(self):
        _, chapter = self.make_hybrid_fixture()
        (check.ROOT / "WRITING.md").write_text("His Saiyan bloodline becomes purer.\n", encoding="utf-8")
        chapter.write_text("The Saiyan strength in him feels deeper now.\n", encoding="utf-8")
        check.check_hybrid_bloodline()
        self.assertTrue(any("WRITING.md" in f for f in check.F), check.F)
        self.assertTrue(any("Chapter 27" in f for f in check.F), check.F)

    def test_hybrid_guard_flags_narrow_active_fact(self):
        import json
        facts, _ = self.make_hybrid_fixture()
        facts["facts"][0]["statement"] = "His Saiyan bloodline becomes purer, deeper and stronger."
        (check.ROOT / "canon" / "facts.json").write_text(json.dumps(facts), encoding="utf-8")
        check.check_hybrid_bloodline()
        self.assertTrue(any("O230" in f for f in check.F), check.F)

    def test_hybrid_guard_flags_missing_whole_existence_confirmation(self):
        import json
        facts, _ = self.make_hybrid_fixture()
        facts["facts"][2]["statement"] = "His Saiyan–Earthling hybrid is stronger in combat."
        (check.ROOT / "canon" / "facts.json").write_text(json.dumps(facts), encoding="utf-8")
        check.check_hybrid_bloodline()
        self.assertTrue(any("O244" in f for f in check.F), check.F)

    def make_kaioken_fixture(self):
        import json
        canon = check.ROOT / "canon"
        canon.mkdir(exist_ok=True)
        facts = {"facts": [
            {"id": "O240", "statement": "Uses times two and times three of unboosted output; the temporary boost ends.",
             "previous_statement": "The technique is not a named transformation or fixed multiplier."},
            {"id": "O245", "statement": "The unaccepted draft uses times two as a temporary boost."},
            {"id": "O249", "statement": "The unaccepted correction has unboosted output and temporary amplification."},
        ]}
        (canon / "facts.json").write_text(json.dumps(facts), encoding="utf-8")
        chapter = check.ROOT / "chapters" / "Chapter_32_The_Road_Beyond_Earth.md"
        chapter.write_text("Kaiō-ken, times two!\n" * 3 + "Kaiō-ken, times three!\n", encoding="utf-8")
        return facts, chapter

    def test_kaioken_guard_allows_historical_denial_and_current_chosen_factors(self):
        self.make_kaioken_fixture()
        check.check_kaioken_regression()
        self.assertFalse(check.F, check.F)
        self.assertTrue(any("KAIOKEN REGRESSION" in p for p in check.P), check.P)

    def test_kaioken_guard_flags_a_reverted_active_fact(self):
        import json
        facts, _ = self.make_kaioken_fixture()
        facts["facts"][0]["statement"] = "The technique is not a named transformation or fixed multiplier."
        (check.ROOT / "canon" / "facts.json").write_text(json.dumps(facts), encoding="utf-8")
        check.check_kaioken_regression()
        self.assertTrue(any("O240" in f for f in check.F), check.F)

    def test_kaioken_guard_flags_missing_current_call_without_reading_footer(self):
        _, chapter = self.make_kaioken_fixture()
        chapter.write_text("Kaiō-ken, times two!\n" * 3 + "<!-- Kaiō-ken, times three! -->\n", encoding="utf-8")
        check.check_kaioken_regression()
        self.assertTrue(any("Chapter 32" in f for f in check.F), check.F)


if __name__ == "__main__":
    unittest.main(verbosity=2)
