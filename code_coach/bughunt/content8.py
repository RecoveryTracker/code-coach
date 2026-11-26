"""A fourth set of Python hunts, each a bug the other twenty-four do not
cover: a string method whose result is thrown away, // where / was meant,
lstrip taking characters rather than a prefix, max() of a dict giving the
biggest key, and a generator read twice.

The same rules hold as for every hunt, and tests/test_bughunt.py checks
them all: the bug is real, it hides on some inputs, the report's own input
shows it, and the fix changes one or two lines in place.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

PYTHON = "Python"


def _shout(words: list) -> list:
    return [w.upper() + "!" for w in words]


def _average(scores: list):
    return sum(scores) / len(scores) if scores else 0


def _without_title(names: list) -> list:
    return [n[4:] if n.startswith("Dr. ") else n for n in names]


def _top_scorer(scores: dict) -> str:
    return max(scores, key=scores.get) if scores else ""


def _stats(nums: list) -> list:
    squares = [n * n for n in nums]
    return [sum(squares), max(squares, default=0)]


PYTHON_HUNTS_4: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-upper-thrown-away",
        title="The shouting is quiet",
        family=PYTHON,
        language="python",
        level=1,
        report="Every word should come back in capitals with a ! on the end. "
               "The ! is there, but 'hi' comes back as 'hi!', not 'HI!'. Words "
               "already in capitals look right.",
        name="shout",
        params=("words",),
        start=(
            "def loud(word):\n"
            "    word.upper()\n"
            "    return word + \"!\"\n"
            "\n"
            "\n"
            "def shout(words):\n"
            "    out = []\n"
            "    for w in words:\n"
            "        out.append(loud(w))\n"
            "    return out\n"
        ),
        fixed=(
            "def loud(word):\n"
            "    word = word.upper()\n"
            "    return word + \"!\"\n"
            "\n"
            "\n"
            "def shout(words):\n"
            "    out = []\n"
            "    for w in words:\n"
            "        out.append(loud(w))\n"
            "    return out\n"
        ),
        solve=_shout,
        reported=(["hi"],),
        cases=(([],), (["OK"],), (["hi"],), (["Go", "STOP"],), (["ABC", "x"],)),
        cause="word.upper() makes a new, upper-case string and the line throws "
              "it away; strings cannot be changed, so word is still lower case.",
        decoys=(
            "upper() only changes the first letter of a word.",
            "The ! is added before the word is made upper case, so it is lost.",
            "out.append adds the word before loud has finished with it.",
        ),
        lesson="String methods never change the string they are called on - "
               "they return a new one. A line that calls one and does nothing "
               "with the result is almost always a bug: keep it, word = "
               "word.upper(), or use it directly.",
        hint="Shout a lower-case word: shout([\"hi\"]).",
        checks=(((["hi"],), ["HI!"]), (([],), []), ((["Go", "STOP"],), ["GO!", "STOP!"])),
    ),
    Hunt(
        id="hunt-floor-average",
        title="The average of 1 and 2 is 1",
        family=PYTHON,
        language="python",
        level=1,
        report="The class average for scores of 1 and 2 shows 1. It should be "
               "1.5. When the scores add up evenly - 2 and 4, say - it is right.",
        name="average",
        params=("scores",),
        start=(
            "def total(scores):\n"
            "    return sum(scores)\n"
            "\n"
            "\n"
            "def average(scores):\n"
            "    if not scores:\n"
            "        return 0\n"
            "    return total(scores) // len(scores)\n"
        ),
        fixed=(
            "def total(scores):\n"
            "    return sum(scores)\n"
            "\n"
            "\n"
            "def average(scores):\n"
            "    if not scores:\n"
            "        return 0\n"
            "    return total(scores) / len(scores)\n"
        ),
        solve=_average,
        reported=([1, 2],),
        cases=(([],), ([2, 4],), ([5],), ([1, 2],), ([7, 8, 9],), ([1, 1, 2],)),
        cause="// is floor division: it throws the fraction away, so 3 // 2 is "
              "1. The average needs /, which always gives the exact answer.",
        decoys=(
            "sum() rounds the total down before it is divided.",
            "len() counts one score too many.",
            "An empty list of scores makes every average 0.",
        ),
        lesson="In Python 3, / always divides exactly and // always rounds down. "
               "Use // only when you WANT a whole number - how many full boxes, "
               "which row - never for an average.",
        hint="Use two scores that do not divide evenly: average([1, 2]).",
        checks=((([1, 2],), 1.5), (([2, 4],), 3.0), (([],), 0), (([1, 1, 2],), 4 / 3)),
    ),
    Hunt(
        id="hunt-lstrip-characters",
        title="Drake became ake",
        family=PYTHON,
        language="python",
        level=2,
        report="We take 'Dr. ' off the front of doctors' names. 'Dr. Who' "
               "becomes 'Who', which is right, but 'Drake' became 'ake'.",
        name="without_title",
        params=("names",),
        start=(
            "TITLE = \"Dr. \"\n"
            "\n"
            "\n"
            "def plain(name):\n"
            "    return name.lstrip(TITLE)\n"
            "\n"
            "\n"
            "def without_title(names):\n"
            "    return [plain(n) for n in names]\n"
        ),
        fixed=(
            "TITLE = \"Dr. \"\n"
            "\n"
            "\n"
            "def plain(name):\n"
            "    return name.removeprefix(TITLE)\n"
            "\n"
            "\n"
            "def without_title(names):\n"
            "    return [plain(n) for n in names]\n"
        ),
        solve=_without_title,
        reported=(["Drake"],),
        cases=(([],), (["Dr. Who"],), (["Ann"],), (["Drake"],), (["Dr. Ruth", "Dre"],)),
        cause="lstrip takes a SET of characters, not a prefix: it strips any "
              "D, r, . or space from the start, so it eats 'Dr' from 'Drake'.",
        decoys=(
            "TITLE has a space at the end, which removes the first letter.",
            "lstrip only works on names that start with a capital.",
            "The list comprehension skips the first character of each name.",
        ),
        lesson="strip, lstrip and rstrip treat their argument as a bag of "
               "characters to remove, in any order. To remove an exact piece "
               "of text, use removeprefix or removesuffix (Python 3.9+).",
        hint="Try a name that starts with the same letters but has no title: without_title([\"Drake\"]).",
        checks=(((["Drake"],), ["Drake"]), ((["Dr. Who"],), ["Who"]),
                ((["Dr. Ruth", "Dre"],), ["Ruth", "Dre"])),
    ),
    Hunt(
        id="hunt-max-of-dict",
        title="Zoe always wins",
        family=PYTHON,
        language="python",
        level=2,
        report="The top scorer is always the name last in the alphabet. With "
               "Ann on 90 and Zoe on 10 it still says Zoe. When the alphabet "
               "and the scores agree, it looks right.",
        name="top_scorer",
        params=("scores",),
        start=(
            "def top_scorer(scores):\n"
            "    if not scores:\n"
            "        return \"\"\n"
            "    best = max(scores)\n"
            "    return best\n"
            "\n"
            "\n"
            "def show(scores):\n"
            "    return \"Winner: \" + top_scorer(scores)\n"
        ),
        fixed=(
            "def top_scorer(scores):\n"
            "    if not scores:\n"
            "        return \"\"\n"
            "    best = max(scores, key=scores.get)\n"
            "    return best\n"
            "\n"
            "\n"
            "def show(scores):\n"
            "    return \"Winner: \" + top_scorer(scores)\n"
        ),
        solve=_top_scorer,
        reported=({"Ann": 90, "Zoe": 10},),
        cases=(({},), ({"Bo": 5},), ({"Ann": 1, "Zoe": 9},), ({"Ann": 90, "Zoe": 10},),
               ({"Cy": 3, "Ada": 7, "Bea": 5},)),
        cause="max() of a dict looks at its KEYS, so it picks the name that "
              "sorts last, not the one with the highest score.",
        decoys=(
            "The dict keeps only the last score it was given.",
            "max() cannot compare scores that are whole numbers.",
            "show adds the word Winner to the wrong name.",
        ),
        lesson="Looping over a dict, or handing it to max, min, sorted or sum, "
               "uses the keys. To compare by value, say so: max(scores, "
               "key=scores.get) gives the key whose value is biggest.",
        hint="Give the high score to a name early in the alphabet: top_scorer({\"Ann\": 90, \"Zoe\": 10}).",
        checks=((({"Ann": 90, "Zoe": 10},), "Ann"), (({},), ""), (({"Cy": 3, "Ada": 7, "Bea": 5},), "Ada")),
    ),
    Hunt(
        id="hunt-used-up-generator",
        title="The biggest square is 0",
        family=PYTHON,
        language="python",
        level=4,
        report="stats([1, 2, 3]) should give the total of the squares and the "
               "biggest square: [14, 9]. It gives [14, 0]. For an empty list, "
               "[0, 0] is right.",
        name="stats",
        params=("nums",),
        start=(
            "def squares_of(nums):\n"
            "    return (n * n for n in nums)\n"
            "\n"
            "\n"
            "def stats(nums):\n"
            "    squares = squares_of(nums)\n"
            "    total = sum(squares)\n"
            "    biggest = max(squares, default=0)\n"
            "    return [total, biggest]\n"
        ),
        fixed=(
            "def squares_of(nums):\n"
            "    return [n * n for n in nums]\n"
            "\n"
            "\n"
            "def stats(nums):\n"
            "    squares = squares_of(nums)\n"
            "    total = sum(squares)\n"
            "    biggest = max(squares, default=0)\n"
            "    return [total, biggest]\n"
        ),
        solve=_stats,
        reported=([1, 2, 3],),
        cases=(([],), ([1, 2, 3],), ([5],), ([-4, 2],)),
        cause="squares_of returns a generator, which hands its values out once. "
              "sum takes them all, so max finds it empty and falls back to 0.",
        decoys=(
            "max() cannot find the biggest of a list of squares.",
            "default=0 makes max always return 0.",
            "sum() changes the numbers as it adds them up.",
        ),
        lesson="Round brackets make a generator, square brackets a list. A "
               "generator is a one-pass stream: fine for a single sum, empty "
               "the second time you read it. Make a list when the values are "
               "needed more than once.",
        hint="Use any non-empty list: stats([1, 2, 3]).",
        checks=((([1, 2, 3],), [14, 9]), (([],), [0, 0]), (([-4, 2],), [20, 16])),
    ),
)
