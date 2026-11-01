#!/usr/bin/env python3
"""Narrow regression checks for the 2026-11-01 authorized chapter revision.

These check explicit anchors and state records, not all meanings, all instructions,
canon fidelity, prose quality, original video, or reader acceptance.
Run: python3 tools/check_revision.py [--selftest]
"""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def ordered(text, *items):
    pos = -1
    for item in items:
        pos = text.find(item, pos + 1)
        if pos < 0:
            return False
    return True


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def load():
    full = {}
    body = {}
    for i in range(1, 10):
        found = list((ROOT / "chapters").glob(f"Chapter_{i:02d}_*.md"))
        if len(found) != 1:
            raise ValueError(f"Chapter {i}: expected one chapter file, found {len(found)}")
        full[i] = found[0].read_text(encoding="utf-8")
        body[i] = full[i].split("## Footer")[0]
    return full, body


def run_checks(full, b):
    out = []
    def ck(name, condition):
        out.append((name, bool(condition)))
    one, two, three, four, five, six, seven, eight, nine = (b[i] for i in range(1, 10))
    c3preview = three.split("## PREVIEW", 1)[1]
    original = {
        1: "57a67bbf882df4cd72c3ed5c0782c7010cc1fef3ae33d1f57981b52e06939ea9",
        2: "5363a6c15ae72da8aa3b9af7c4b346dfe7a54cfab5def1c6217725bfa8df89cc",
        3: "0e24b47c60bac3d12237378e23d48170b9ca06cb62b1f6290aaa1cb75ec76259",
    }
    revision = text("REVISION_2026-11-01.md")
    openfile = text("OPEN.md")
    facts = json.loads(text("canon/facts.json"))
    rows = {r["id"]: r for r in facts["facts"]}

    ck("original accepted hashes are recorded and revised bodies differ", all(
        h in revision and hashlib.sha256(b[i].encode()).hexdigest() != h for i, h in original.items()))
    ck("explicit authorization and review status are recorded", all(x in revision for x in (
        "explicitly chose to apply", "not automatic acceptance", "Four–Nine remain provisional")))
    ck("wider habits and source limits remain open", "scene-by-scene review" in openfile and "secondary synopsis" in openfile)
    ck("revision facts are authored and provisional", all(rows[x]["tier"] == "III" and rows[x]["status"] == "active-draft" for x in ("O122", "O123")))
    ck("secondary visual evidence has not been promoted to checked footage", "synopsis is secondary" in rows["C181"]["statement"] and "not independently checked video" in rows["C181"]["statement"])
    ck("false historical island cat retelling stays historical", rows["O009"]["status"] == "historical-note-not-on-page" and "no such retelling" in rows["O009"]["statement"])

    ck("first breakfast preparation precedes eating", ordered(one, "watches Chi-Chi wash the rice", "breaks an egg", "sits down on the step beside it and eats"))
    ck("second breakfast is watched before it is eaten", ordered(one, "watches her fry another egg", "He eats the second bowl"))
    ck("stay is echoed and held until changed", ordered(one, '"Stay," Chi-Chi says', '"Stay," Goshin says.', '"Come now."', '"Come now." Goshin'))
    ck("tree instruction is repeated before tightening grip", ordered(one, '"Hold on," Goku says.', '"Hold on," Goshin says.', "He tightens his grip"))
    ck("mother inspection has hands behind back", "Chi-Chi looks Goshin over. His hands go behind his back." in one)
    ck("father conversation invites the boy", ordered(one, '"What do you want to do?"', '"Can I go too?"', '"You\'ll stay," Goshin says.'))
    ck("bucket order is repeated and limited", ordered(one, '"Not the whole bucket," Chi-Chi says.', '"Not the whole bucket," Goshin says.', "He pours half the water back"))
    ck("downhill side is staged with Gohan", "keeping to the downhill side" in one)
    ck("forest rescue explicitly recovers and returns the hat", ordered(one, "cat licks him, takes his hat", "Goku finds the cat wearing Gohan's hat", "Goku picks it up", "Goku settles the recovered hat on Gohan's head"))
    ck("field question, city and Piccolo challenge follow revised order", ordered(one, "Could that be Kakarot?", "Goku settles the recovered hat", "a city passes", "Do you want to die?", "Three hundred and twenty-two", "This time it is Kakarot"))
    ck("Chapter One declares secondary synopsis witness", "W-65" in full[1].split("## Footer")[0])

    ck("island arrival is not duplicated", two.count("The cloud comes down") == 1 and "From above the beach" not in two)
    heads = re.findall(r"^## (ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)\b", two, re.M)
    ck("Chapter Two headings are in order", heads == ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN"])
    ck("five integrated island moments are present", all(x in two for x in ("Krillin puts a manju in his mouth", "Rock, paper, scissors", "Goku throws a stone", "Grandpa Gohan carries Goku home", "We find planets worth selling")))
    ck("group order is echoed before Turtle moves away", ordered(two, '"Don\'t go too far," Goku calls.', '"Don\'t go too far," Goshin says.'))
    ck("Saiyan explanation follows specified source order", ordered(two, "We find planets worth selling", '"The moon?"', "I'm Son Goku", "Our planet was called Vegeta", "There is a world with good land"))
    ck("Raditz tells them his name before later chapters use it", "I am your brother, Raditz." in two)
    ck("Broc remains first spoken by Raditz", "\"is Broc.\"" in two and "Broc" not in re.sub(r"```.*?```", "", one, flags=re.S))
    ck("Chapter Two ends at intervention, not conscious capture", ordered(two, "Raditz drives a knee into his stomach", "Goshin pulls free", "moves between them, raising his hands") and "picks up Goshin" not in two)

    ck("Eight Hours remains schooling and title", "**EIGHT HOURS**" in three and '"Eight hours a day,"' in three)
    ck("old calendar, countdown, moon-phase and false future removed", not any(x in three.lower() for x in ("the fourth day of the twelfth month", "seven hours remain", "zero hours", "snake way", "moon a little past full")))
    ck("same-day departure is explicit", "Both boys went with their father earlier today, on the cloud." in three)
    ck("two spare pairs of boots are shown", "Two spare pairs of boots" in three)
    ck("five diners: four places, then fifth; two used", all(x in three for x in ("four bowls turned upside down", "sets out a fifth bowl", "Five bowls, right way up", "two used and three untouched")))
    ck("schoolbag name stays unidentified", "a name burned into the flap" in three and "Chi-Chi runs a finger over the name" in three)
    ck("one unanswered call and yard-camera preview remain", "Nobody is available to speak to you at present" in three and "*(The telephone rests in its cradle. Outside, the road is still empty.)*" in c3preview and "*(Nimbus carries" not in c3preview)
    ck("Chapter Two cut and Chapter Three three bowls join", "sets three bowls by the door" in two and "carries the three bowls from the step" in three)
    ck("Chapter Five and Nine track the same school paper", "paper with the red circle hangs against the doorframe" in five and "Gohan's school paper is still fastened to the doorframe" in nine)
    ck("Chapter Seven reuses the unanswered call and has Roshi call promptly", "Nobody is available to speak to you at present" in seven and ordered(seven, "We're back", "I'm going now", "He picks up the receiver and dials the mountain house"))

    ck("Chapter Four resumes without a second knockdown", "Goku has been knocked down" in four and "Raditz drives a knee into his stomach" not in four)
    ck("anger rise, earned knockout and carrying are ordered", ordered(four, "Ki flares around him", "strikes the side of his head", "pick up Goshin with the other"))
    ck("truck, pod and waking remain ordered", ordered(four, "crawls under the truck with him", "drives his fist down into the engine", "throws the truck high", "places Goshin in the pod", "Goshin opens his eyes"))
    ck("pod escape does not ignore the old direct order", "Get back in there." not in four and "You think a broken hatch will keep me from taking you?" in four)
    ck("Chapter Five preserves first-wave scan and control distinction", "**1,450**" in five and "higher than Kakarot's" in five and "His first wave carries more raw ki than Goku's in this scene but is less practiced" in full[5])
    ck("separate Chapter Six surge remains ordinary", "Fifteen hundred?" in six and "god ki" not in six.lower() and not re.search(r"\bsuper saiyan\b", six, re.I))
    ck("Senzu offer does not direct both boys to eat", "Gohan, would you like yours?" in seven and "You two have yours" not in seven)
    ck("Goku and Gohan eat and are fully restored", ordered(seven, "Goku eats it", "his strength has returned", "Gohan takes a bean", "I'm all healed, and I'm not tired anymore"))
    ck("Goshin refuses the third bean after not seeing it made", ordered(seven, "Krillin offers the last bean to Goshin", "he doesn't eat it", "I didn't see it made", "sets it gently back"))
    ck("Roshi keeps the uneaten bean", "Roshi closes the string and puts the bag safely in his pocket" in eight and "I'll keep it with me" in nine)
    ck("Goshin watches subsequent meals prepared", "Goshin stays on his chair through the chopping" in eight and "Goshin watches his mother beat the eggs and cook them" in nine and "watches as Chi-Chi rinses vegetables and cuts them for soup" in nine)
    ck("no stranger hand is placed on his head by Krillin", "Goshin parts his own hair, and Krillin looks at the sore place without touching him" in seven)
    ck("representative medical instruction is repeated exactly", ordered(eight, '"Follow my finger without moving your head."', '"Follow my finger without moving your head," Goshin repeats.'))
    ck("representative practice instruction is repeated exactly", ordered(nine, '"Try letting your weight settle before you move the other one."', '"Try letting your weight settle before you move the other one," Goshin repeats.'))
    ck("provisional drafts have review notices", all("This chapter remains provisional" in full[i] for i in range(4, 10)))
    return out


def main():
    full, bodies = load()
    checks = run_checks(full, bodies)
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failures = sum(not ok for _, ok in checks)
    print(f"\nrevision checks: {len(checks)-failures}/{len(checks)} passed")
    if "--selftest" in sys.argv:
        mutations = [
            (1, "Goku settles the recovered hat on Gohan's head", "Goku puts the hat away", "forest rescue explicitly recovers and returns the hat"),
            (2, "The cloud comes down", "The cloud comes down. The cloud comes down", "island arrival is not duplicated"),
            (3, "Both boys went with their father earlier today, on the cloud.", "They went yesterday.", "same-day departure is explicit"),
            (4, "strikes the side of his head", "takes him while he is conscious", "anger rise, earned knockout and carrying are ordered"),
            (7, "Gohan, would you like yours?", "You two have yours", "Senzu offer does not direct both boys to eat"),
            (3, "Two spare pairs of boots", "one pair", "two spare pairs of boots are shown"),
        ]
        mutated_pass = 0
        for chapter, old, new, expected in mutations:
            assert old in bodies[chapter], f"selftest anchor absent: {old}"
            broken = dict(bodies)
            broken[chapter] = broken[chapter].replace(old, new, 1)
            result = dict(run_checks(full, broken))
            caught = not result[expected]
            mutated_pass += caught
            print(f"  SELFTEST {'PASS' if caught else 'FAIL'}  mutation caught: {expected}")
        print(f"mutation selftest: {mutated_pass}/{len(mutations)} caught")
        failures += len(mutations) - mutated_pass
    print("These are targeted string regressions, not exhaustive semantic or video verification.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
