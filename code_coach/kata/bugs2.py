"""More broken functions, in the shapes the first eight did not cover.

The first set was about control flow and defaults. These are about the
things that look right because they nearly are: a slice that is one short
of what was meant, a range missing its step, an assignment where an
addition was meant, a comparison on the wrong property, and a dict being
edited while it is being read.

Every one of these was written both ways and run against the same inputs
before it was put here, because a broken exercise that turns out not to
be broken is worse than no exercise — it wastes your time and reads as
though the marker is at fault. Three more candidates were written and
thrown away for exactly that: they behaved identically to the correct
version on every input tried, so there was nothing to find.
"""

from __future__ import annotations

from code_coach.kata import Kata


def _drop_low(scores: dict) -> dict:
    return {name: score for name, score in scores.items() if score >= 50}


def _countdown(n: int) -> list:
    return list(range(n, 0, -1))


def _first_letters(names: list) -> str:
    out = ""
    for name in names:
        out += name[0]
    return out


def _swapped(pair: list) -> list:
    a, b = pair
    return [b, a]


def _all_but_last(items: list) -> list:
    return items[:-1]


def _longest(words: list) -> str:
    best = ""
    for word in words:
        if len(word) > len(best):
            best = word
    return best


def _mean(numbers: list) -> float:
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


BUGS2: tuple[Kata, ...] = (
    Kata(
        id="bug-drop-low",
        name="drop_low",
        brief=(
            "Return the scores of 50 and over, leaving the ones below out. "
            "The dictionary you were given must not change."
        ),
        params=("scores",),
        family="Fix the bug",
        example='drop_low({"a": 10, "b": 60}) is {"b": 60}',
        hint="Read what the error says about the size of the dictionary.",
        cases=(
            ({"a": 10, "b": 60},), ({},), ({"a": 60},), ({"a": 10},),
            ({"a": 50},), ({"a": 49, "b": 51},),
            ({"a": 10, "b": 20, "c": 90},), ({"a": 0},),
            ({"a": 100, "b": 100},), ({"a": 49},),
        ),
        solve=_drop_low,
        checks=(
            (({"a": 10, "b": 60},), {"b": 60}), (({},), {}),
            (({"a": 50},), {"a": 50}), (({"a": 49},), {}),
        ),
        start=(
            "def drop_low(scores):\n"
            "    for name in scores:\n"
            "        if scores[name] < 50:\n"
            "            del scores[name]\n"
            "    return scores"
        ),
        bug="Changing the size of a dictionary while looping over it "
            "raises, because the loop is walking a thing that moved under "
            "it. Build a new dictionary instead — and that also leaves "
            "the caller's alone, which this was not doing either.",
    ),
    Kata(
        id="bug-countdown",
        name="countdown",
        brief=(
            "Return the numbers from n down to 1. An n of 0 or less gives "
            "an empty list."
        ),
        params=("n",),
        family="Fix the bug",
        example="countdown(3) is [3, 2, 1]",
        hint="range has a third argument, and without it it only counts up.",
        cases=(
            (3,), (0,), (1,), (5,), (2,), (10,), (-1,), (4,), (7,), (6,),
        ),
        solve=_countdown,
        checks=(((3,), [3, 2, 1]), ((0,), []), ((1,), [1]),
                ((-1,), []), ((2,), [2, 1])),
        start=(
            "def countdown(n):\n"
            "    return list(range(n, 0))"
        ),
        bug="range counts upwards unless told otherwise, and from 3 up to "
            "0 there is nothing, so it comes back empty rather than "
            "backwards. The step of -1 is the missing third argument.",
    ),
    Kata(
        id="bug-first-letters",
        name="first_letters",
        brief=(
            "Return the first letter of every name, joined together. No "
            "names gives an empty string."
        ),
        params=("names",),
        family="Fix the bug",
        example='first_letters(["ada", "alan"]) is "aa"',
        hint="Look closely at what happens to `out` on each pass.",
        cases=(
            (["ada", "alan"],), ([],), (["x"],), (["a", "b", "c"],),
            (["grace", "hopper"],), (["one"],), (["a", "a"],),
            (["zed", "yan", "xu"],), (["Q"],), (["m", "n"],),
        ),
        solve=_first_letters,
        checks=(
            (((["ada", "alan"],)), "aa"), ((([],)), ""), (((["x"],)), "x"),
            (((["a", "b", "c"],)), "abc"),
        ),
        start=(
            "def first_letters(names):\n"
            "    out = ''\n"
            "    for name in names:\n"
            "        out = name[0]\n"
            "    return out"
        ),
        bug="A plain `=` replaces what was there, so each pass throws away "
            "everything collected so far and the answer is only ever the "
            "last letter. `+=` is what adds to it.",
    ),
    Kata(
        id="bug-swapped",
        name="swapped",
        brief=(
            "Return a two-item list with the pair the other way round. The "
            "list you were given must not change."
        ),
        params=("pair",),
        family="Fix the bug",
        example="swapped([1, 2]) is [2, 1]",
        hint=(
            "Write down what a and b hold after each of the two lines, "
            "one line at a time."
        ),
        cases=(
            ([1, 2],), ([0, 0],), ([-1, 1],), ([5, 5],), ([2, 1],),
            ([0, 9],), ([-3, -7],), ([100, 1],), ([1, 0],), ([7, 8],),
        ),
        solve=_swapped,
        checks=(
            ((([1, 2],)), [2, 1]), ((([0, 0],)), [0, 0]),
            ((([-1, 1],)), [1, -1]), ((([1, 0],)), [0, 1]),
        ),
        start=(
            "def swapped(pair):\n"
            "    a, b = pair\n"
            "    a = b\n"
            "    b = a\n"
            "    return [a, b]"
        ),
        bug="The first line overwrites a, so by the second line the "
            "original a is gone and b is assigned from itself. Both end up "
            "holding the same value. Python can do this in one line: "
            "`a, b = b, a`.",
    ),
    Kata(
        id="bug-all-but-last",
        name="all_but_last",
        brief=(
            "Return a new list with everything except the final item. An "
            "empty list stays empty."
        ),
        params=("items",),
        family="Fix the bug",
        example="all_but_last([1, 2, 3]) is [1, 2]",
        hint="Count what the slice actually stops at.",
        cases=(
            ([1, 2, 3],), ([],), ([1],), ([1, 2],), ([0],),
            ([5, 5, 5],), ([-1, -2],), ([9],), ([1, 2, 3, 4],), ([7, 8],),
        ),
        solve=_all_but_last,
        checks=(
            ((([1, 2, 3],)), [1, 2]), ((([],)), []), ((([1],)), []),
            ((([1, 2],)), [1]),
        ),
        start=(
            "def all_but_last(items):\n"
            "    return items[:len(items)]"
        ),
        bug="A slice up to the length is the whole list — it stops before "
            "that position, and the last position is one less. `[:-1]` "
            "says it directly, and works on an empty list too.",
    ),
    Kata(
        id="bug-longest",
        name="longest",
        brief=(
            "Return the longest word. When two are equally long, return "
            "the one that came first. No words gives an empty string."
        ),
        params=("words",),
        family="Fix the bug",
        example='longest(["apple", "fig"]) is "apple"',
        hint="What does `>` compare, when both sides are text?",
        cases=(
            (["apple", "fig"],), ([],), (["a"],), (["zoo", "aardvark"],),
            (["ab", "cd"],), (["one", "three", "go"],), (["x", "yy"],),
            (["same", "size"],), (["b", "a"],), (["tiny", "a", "big"],),
        ),
        solve=_longest,
        checks=(
            (((["apple", "fig"],)), "apple"), ((([],)), ""),
            (((["a"],)), "a"), (((["zoo", "aardvark"],)), "aardvark"),
            (((["ab", "cd"],)), "ab"),
        ),
        start=(
            "def longest(words):\n"
            "    best = ''\n"
            "    for word in words:\n"
            "        if word > best:\n"
            "            best = word\n"
            "    return best"
        ),
        bug="`>` on two strings compares them alphabetically, not by "
            "length, so this returns the word latest in the dictionary. "
            "It is the comparison that needs to be on len(word), not the "
            "word.",
    ),
    Kata(
        id="bug-mean",
        name="mean",
        brief=(
            "Return the average of the numbers as a real number, and 0.0 "
            "for an empty list."
        ),
        params=("numbers",),
        family="Fix the bug",
        example="mean([1, 2]) is 1.5",
        hint="There are two division operators and this is the other one.",
        cases=(
            ([1, 2],), ([],), ([2, 2],), ([0],), ([1, 2, 4],),
            ([5],), ([-1, 1],), ([3, 4],), ([10, 20],), ([7],),
        ),
        solve=_mean,
        checks=(
            ((([1, 2],)), 1.5), ((([],)), 0.0), ((([0],)), 0.0),
            ((([2, 2],)), 2.0), ((([5],)), 5.0),
        ),
        start=(
            "def mean(numbers):\n"
            "    if not numbers:\n"
            "        return 0.0\n"
            "    return sum(numbers) // len(numbers)"
        ),
        bug="`//` throws away the fraction, so the average of 1 and 2 is "
            "1 rather than 1.5. `/` is the one that keeps it.",
    ),
)
