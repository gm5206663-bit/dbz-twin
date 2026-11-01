#!/usr/bin/env python3
"""Focused Chapter Ten anchors and mutation checks, not a semantic or source proof.

Run: python3 tools/check_chapter_10.py [--selftest]
The manual audit in SCENE_COVERAGE_009.md remains necessary; these checks cannot
identify every instruction, infer every addressee, watch preparation, or assess
medical, character, source and literary judgment on their own.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "chapters/Chapter_10_The_Book_and_the_Road.md"


def ordered(text, *parts):
    offset = 0
    for part in parts:
        index = text.find(part, offset)
        if index < 0:
            return False
        offset = index + len(part)
    return True


def checks(full):
    body = full.split("## Footer", 1)[0]
    card = full.split("```", 2)[1] if "```" in full else ""
    outcomes = []
    def ck(name, condition):
        outcomes.append((name, bool(condition)))

    ck("review status remains explicit", "STATUS: draft — awaiting reader review" in card
       and "This chapter is provisional" in full.split("## Footer", 1)[-1])
    ck("prior preview title is honored", "# Chapter Ten · The Book and the Road" in full)
    ck("medical stillness is echoed first", ordered(body, '"Hold still, please," the doctor says.',
       '"Hold still, please."', 'Goshin keeps his head level'))
    ck("stand instruction is echoed first", ordered(body, '"Please stand," she says to Goshin.',
       '"Please stand."', 'He rises from the chair'))
    ck("passenger-only condition is echoed before travel", ordered(body,
       '"Travel only as a passenger."', '"Travel only as a passenger."',
       'Goku lifts Chi-Chi, and the cloud rises beside them'))
    ck("head symptom report is echoed", ordered(body,
       '"Tell me if your head hurts or spins."', '"Tell me if your head hurts or spins."'))
    restrictions = '"And no running, flying on your own, heavy lifting, or training until I see you again."'
    ck("exercise restrictions are echoed", ordered(body, restrictions, restrictions))
    reading = '"Stop if reading makes your head hurt. Rest when you need it."'
    ck("reading and rest limits are echoed", ordered(body,
       'For a while. Stop if reading makes your head hurt. Rest when you need it.', reading))
    ck("group path instruction precedes echoed compliance", ordered(body,
       '"Both of you, stay together on the path," Chi-Chi says.',
       '"Both of you, stay together on the path," Goshin repeats.',
       "On the sloping path to the yard, Goshin walks on Gohan's downhill side"))
    ck("ride monitoring instruction is echoed", ordered(body,
       '"Tell me if the movement bothers your head," Chi-Chi says.',
       '"Tell me if the movement bothers your head."',
       'Goku lifts Chi-Chi, and the cloud rises beside them'))
    ck("moon precaution is echoed", ordered(body, '"Keep using that precaution," Kami says.',
       '"Keep using that precaution," Goshin repeats.', 'Goku checks the cupboard latch and then the curtains'))
    ck("tunnel prohibition is echoed", ordered(body, '"Then we\'ll listen. You won\'t go into a damaged tunnel."',
       '"You won\'t go into a damaged tunnel," Goshin repeats.'))
    ck("robot noise instruction is echoed", ordered(body, '"Don\'t shout. The sand is balanced against the roof."',
       'On the platform, Goshin turns to Chi-Chi. "Don\'t shout."'))
    connection = '"Please don\'t connect anything else without asking me."'
    ck("robot connection instruction is echoed", body.count(connection) == 2)
    rest = '"Rest before we leave, and tell me if you feel worse."'
    ck("return rest instruction is echoed before resting", ordered(body, rest, rest, 'After Goshin has rested'))
    ck("Goku invites the direct radio answer", ordered(body,
       '"Goshin, what do you see in the picture?"',
       'Goshin\'s voice comes over the set. "The picture in our book is a side view.'))
    ck("outbound and return slopes are downhill", all(x in body for x in (
       "Goshin walks on Gohan's downhill side", "Goshin keeps to Gohan's downhill side")))
    ck("representative Chi-Chi checks use hands behind", all(x in body for x in (
       'When she looks him over, he puts his hands behind his back',
       'he places his hands behind his back while she checks his face and bandage',
       'He puts his hands behind his back while she looks him over',
       'Chi-Chi looks Goshin over, and he puts his hands behind his back',
       'he puts his hands behind his back while she checks him')))
    ck("first food path includes watched raw preparation and cooking", ordered(body,
       'uncooked rice, whole vegetables, a whole uncooked fish',
       'Goshin takes his chair where he can see her hands',
       'She rinses the rice, then washes and cuts the vegetables while he watches',
       'Goshin watches the pot and pan while Gohan reads aloud',
       'Goshin watches her fill the parcels and wrap them',
       'Goshin takes his plate'))
    ck("second food path includes reheating and lemon preparation", ordered(body,
       'Goshin sits where he can see them opened and watches',
       'Goshin watches while Chi-Chi washes the lemon, cuts it and squeezes juice',
       'Goshin watches her stir it through the rice and vegetables',
       'Goshin tries his own watched portion'))
    ck("third bean stays refused", ordered(body, 'The one Roshi kept was already grown',
       '"Then I still won\'t eat that one."'))
    ck("robot agrees and instructs the different rescue", ordered(body,
       '"I would like to see the surface," C-6 says.',
       '"I want to come. Open the plate."', '"Red to blue," C-6 says.',
       'Goku raises the slab with his left hand', 'Goku pulls C-6 through the entrance'))
    ck("robot requests shutdown without certain recovery", ordered(body,
       '"I would like to switch off now."', '"I don\'t know. It gives me the best chance to save what remains."',
       'C-6 gives a small movement of his lens. Goku turns the switch off.'))
    ck("family separation is acknowledged, not guaranteed safe", all(x in body for x in (
       '"If you go, we\'re apart.', '"I cannot promise that.',
       'We can leave the site to the workers.', 'It is not a guarantee')))
    ck("family returns before late", 'The family reaches the house before it gets late.' in body)
    ck("no configured age-inappropriate early form or boast marker", not re.search(
       r'\b(god\s+ki|super saiyan|i am the strongest|i\'m the strongest)\b',
       re.sub(r'```.*?```', '', body, flags=re.S), re.I))
    return outcomes


def main():
    full = CHAPTER.read_text(encoding='utf-8')
    results = checks(full)
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failures = sum(not ok for _, ok in results)
    print(f"\nChapter Ten focused anchors: {len(results)-failures}/{len(results)} passed")
    if '--selftest' in sys.argv:
        mutations = [
            ('"Please stand."\n\nHe rises from the chair', 'He rises from the chair', 'stand instruction is echoed first'),
            ('"Both of you, stay together on the path," Goshin repeats.', 'Goshin nods.', 'group path instruction precedes echoed compliance'),
            ('"Goshin, what do you see in the picture?"', '"Can somebody look?"', 'Goku invites the direct radio answer'),
            ("Goshin walks on Gohan's downhill side", "Goshin walks on Gohan's uphill side", 'outbound and return slopes are downhill'),
            ('Goshin watches the pot and pan while Gohan reads aloud', 'Goshin looks away while the meal cooks', 'first food path includes watched raw preparation and cooking'),
            ('"I want to come. Open the plate."', '"Leave me here."', 'robot agrees and instructs the different rescue'),
            ('"I don\'t know. It gives me the best chance to save what remains."', '"I am fully repaired."', 'robot requests shutdown without certain recovery'),
            ('"Rest before we leave, and tell me if you feel worse."\n\n"Rest before we leave, and tell me if you feel worse."', '"Rest before we leave, and tell me if you feel worse."', 'return rest instruction is echoed before resting'),
        ]
        caught = 0
        for old, new, expected in mutations:
            if old not in full:
                print(f"  SELFTEST FAIL  missing mutation anchor: {expected}")
                failures += 1
                continue
            broken = full.replace(old, new, 1)
            is_caught = not dict(checks(broken))[expected]
            print(f"  SELFTEST {'PASS' if is_caught else 'FAIL'}  mutation caught: {expected}")
            caught += int(is_caught)
            failures += int(not is_caught)
        print(f"mutation selftest: {caught}/{len(mutations)} caught")
    print('Targeted textual anchors only; these checks do not certify every rule, source, safety decision or acceptance.')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
