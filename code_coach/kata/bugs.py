"""Fix the bug: the function is written, and it is wrong.

A kata starts from an empty box. This starts from working-looking code
that fails two of its ten cases, and the job is to find out why. Codewars
has a whole category of these and this app had nothing like it.

It is a different skill from writing the thing yourself, and the one more
of your time actually goes on. Reading code that looks right, finding the
one place it is not, and changing that and nothing else is most of what
maintaining anything consists of.

Every bug here is one a person writes, not a puzzle:

  the off-by-one      `range(1, n)` where the last one matters
  the wrong operator  `<` where it should be `<=`
  the shared default  a list as a default argument, kept between calls
  the aliased list    mutating the argument instead of a copy
  the early return    returning inside the loop on the first item
  the missed case     handling the empty input by accident, not on purpose
  the wrong variable  a name that looks right and is the other one
  the reversed test   `if not found` where it should be `if found`

The machinery is the kata machinery. A broken exercise is a kata whose
`start` is filled in, so the driver, the marker, the screen and the
comparison rules are all the ones already in use and already tested. What
is added here is the broken code and a note saying what the bug *was*,
shown only after it passes — reading the name of your mistake once you
have found it is what makes it the last time you make it.

The same discipline applies as to the katas, and more sharply. The
expected answers come from `solve`, which is correct. The broken version
is `start`. A test runs both: `solve` must pass every case and `start`
must fail at least one, because a "broken" exercise that already passes
is a page that wastes your time and cannot be noticed any other way.
"""

from __future__ import annotations

from code_coach.kata import Kata

# ── The off-by-one ───────────────────────────────────────────


def _sum_to(n: int) -> int:
    return sum(range(1, n + 1))


def _count_evens(numbers: list) -> int:
    return sum(1 for x in numbers if x % 2 == 0)


def _last_index(numbers: list, target: int) -> int:
    found = -1
    for i, x in enumerate(numbers):
        if x == target:
            found = i
    return found


def _average(numbers: list) -> float:
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def _add_item(item: int, basket: list | None = None) -> list:
    if basket is None:
        basket = []
    basket.append(item)
    return basket


def _doubled(numbers: list) -> list:
    out = list(numbers)
    for i, x in enumerate(out):
        out[i] = x * 2
    return out


def _all_positive(numbers: list) -> bool:
    for x in numbers:
        if x <= 0:
            return False
    return True


def _initials(name: str) -> str:
    return "".join(part[0].upper() for part in name.split())


BUGS: tuple[Kata, ...] = (
    Kata(
        id="bug-sum-to",
        level=1,
        name="sum_to",
        brief=(
            "Add up every number from 1 to n, including n itself. It is "
            "one short every time."
        ),
        params=("n",),
        family="Fix the bug",
        example="sum_to(5) is 15, because 1+2+3+4+5",
        hint="range stops before the number you give it.",
        cases=((5,), (1,), (0,), (10,), (2,), (100,), (3,), (7,), (50,), (4,)),
        solve=_sum_to,
        checks=(((5,), 15), ((1,), 1), ((0,), 0), ((10,), 55)),
        start=(
            "def sum_to(n):\n"
            "    total = 0\n"
            "    for i in range(1, n):\n"
            "        total += i\n"
            "    return total"
        ),
        bug="The classic off-by-one. range(1, n) stops at n - 1, so the "
            "last number never gets added.",
    ),
    Kata(
        id="bug-count-evens",
        level=3,
        name="count_evens",
        brief=(
            "Count how many numbers in the list are even. Zero is even, "
            "and so are negative even numbers."
        ),
        params=("numbers",),
        family="Fix the bug",
        example="count_evens([1, 2, 3, 4]) is 2",
        hint="What does -4 % 2 give you, and what does the test compare it to?",
        cases=(
            ([1, 2, 3, 4],), ([],), ([0],), ([-4, -2],), ([1, 3, 5],),
            ([2],), ([-1, 0, 1],), ([10, 11, 12],), ([-6],), ([7, 8],),
        ),
        solve=_count_evens,
        checks=((([1, 2, 3, 4],), 2), (([],), 0), (([0],), 1),
                (([-4, -2],), 2)),
        start=(
            "def count_evens(numbers):\n"
            "    found = 0\n"
            "    for x in numbers:\n"
            "        if x % 2 == 1:\n"
            "            continue\n"
            "        if x > 0:\n"
            "            found += 1\n"
            "    return found"
        ),
        bug="Two mistakes that hide each other. Zero and negative evens "
            "are both skipped by the `x > 0` test, and it only looks even "
            "because the first guard sends the odd ones away first.",
    ),
    Kata(
        id="bug-last-index",
        level=2,
        name="last_index",
        brief=(
            "Return the position of the LAST time the target appears, or "
            "-1 when it never does."
        ),
        params=("numbers", "target"),
        family="Fix the bug",
        example="last_index([1, 2, 1], 1) is 2",
        hint="It stops as soon as it finds one. Which one does it find?",
        cases=(
            ([1, 2, 1], 1), ([], 1), ([5], 5), ([5], 9), ([1, 1, 1], 1),
            ([1, 2, 3], 3), ([3, 2, 1], 3), ([0, 0], 0), ([7, 8, 7, 8], 7),
            ([-1, -1], -1),
        ),
        solve=_last_index,
        checks=((([1, 2, 1], 1), 2), (([], 1), -1), (([5], 9), -1),
                (([1, 1, 1], 1), 2)),
        start=(
            "def last_index(numbers, target):\n"
            "    for i, x in enumerate(numbers):\n"
            "        if x == target:\n"
            "            return i\n"
            "    return -1"
        ),
        bug="The early return. Returning inside the loop gives you the "
            "first match; to get the last one you have to keep going and "
            "remember.",
    ),
    Kata(
        id="bug-average",
        level=2,
        name="average",
        brief=(
            "Return the mean of the numbers, and 0.0 for an empty list "
            "rather than raising."
        ),
        params=("numbers",),
        family="Fix the bug",
        example="average([1, 2, 3]) is 2.0",
        hint="Try it on the empty list and read what it says.",
        cases=(
            ([1, 2, 3],), ([],), ([5],), ([0],), ([-2, 2],), ([1, 2],),
            ([10, 20, 30, 40],), ([-1],), ([3, 3, 3],), ([0, 0, 0],),
        ),
        solve=_average,
        checks=((([1, 2, 3],), 2.0), (([],), 0.0), (([5],), 5.0),
                (([0],), 0.0)),
        start=(
            "def average(numbers):\n"
            "    return sum(numbers) / len(numbers)"
        ),
        bug="The missed case. Dividing by the length of an empty list is "
            "a ZeroDivisionError, and the empty list is the input nobody "
            "tries until it happens.",
    ),
    Kata(
        id="bug-add-item",
        level=4,
        name="add_item",
        brief=(
            "Add the item to the basket and return it. With no basket "
            "given, start a new empty one — a new one every time."
        ),
        params=("item", "basket"),
        family="Fix the bug",
        example="add_item(1) is [1], and calling it again is [1] again",
        hint=(
            "The default is built once, when the function is defined, not "
            "once per call."
        ),
        cases=(
            (1, None), (2, None), (3, []), (4, [9]), (5, None),
            (6, [1, 2]), (7, None), (8, []), (9, [0]), (10, None),
        ),
        solve=_add_item,
        mutates=True,
        checks=(((1, None), [1]), ((2, None), [2]), ((3, []), [3]),
                ((4, [9]), [9, 4])),
        start=(
            "def add_item(item, basket=[]):\n"
            "    basket.append(item)\n"
            "    return basket"
        ),
        bug="The mutable default argument, which is Python's most famous "
            "trap. The list in the signature is made once and shared by "
            "every call that does not pass its own.",
    ),
    Kata(
        id="bug-doubled",
        level=4,
        name="doubled",
        brief=(
            "Return a new list with every number doubled. The list you "
            "were given must not change."
        ),
        params=("numbers",),
        family="Fix the bug",
        example="doubled([1, 2]) is [2, 4], and the original is still [1, 2]",
        hint="Which list is being written to?",
        cases=(
            ([1, 2],), ([],), ([0],), ([-3],), ([5, 5],), ([1, 2, 3],),
            ([100],), ([-1, 1],), ([7],), ([2, 4, 6],),
        ),
        solve=_doubled,
        checks=((([1, 2],), [2, 4]), (([],), []), (([0],), [0]),
                (([-3],), [-6])),
        start=(
            "def doubled(numbers):\n"
            "    out = numbers\n"
            "    for i, x in enumerate(out):\n"
            "        out[i] = x * 2\n"
            "    return out"
        ),
        bug="The aliased list. `out = numbers` is a second name for the "
            "same list, not a copy, so writing to one writes to both — "
            "and the answer looks right while the caller's list is "
            "quietly wrecked.",
    ),
    Kata(
        id="bug-all-positive",
        level=2,
        name="all_positive",
        brief=(
            "Return True when every number is greater than zero. An empty "
            "list has nothing that is not, so it is True."
        ),
        params=("numbers",),
        family="Fix the bug",
        example="all_positive([1, 2]) is True, all_positive([1, 0]) is False",
        hint="Where does the True come back from, and how many numbers has "
             "it seen by then?",
        cases=(
            ([1, 2],), ([],), ([0],), ([-1],), ([1, 0],), ([1],),
            ([3, 2, 1],), ([1, -1, 1],), ([0, 0],), ([5, 5, 5],),
        ),
        solve=_all_positive,
        checks=((([1, 2],), True), (([],), True), (([0],), False),
                (([-1],), False)),
        start=(
            "def all_positive(numbers):\n"
            "    for x in numbers:\n"
            "        if x <= 0:\n"
            "            return False\n"
            "        else:\n"
            "            return True\n"
            "    return True"
        ),
        bug="Returning True from inside the loop. It answers on the first "
            "number and never looks at the rest, so [1, -1, 1] is True.",
    ),
    Kata(
        id="bug-initials",
        level=3,
        name="initials",
        brief=(
            "Return the first letter of each word, in upper case, joined "
            "together. An empty name gives an empty string."
        ),
        params=("name",),
        family="Fix the bug",
        example='initials("ada lovelace") is "AL"',
        hint=(
            "split(' ') and split() are not the same function. Try it on "
            "a name with two spaces in the middle."
        ),
        cases=(
            ("ada lovelace",), ("",), ("x",), ("grace  hopper",),
            (" alan turing",), ("alan turing ",), ("one two three",),
            ("Ada",), ("  ",), ("john von neumann",),
        ),
        solve=_initials,
        checks=((("ada lovelace",), "AL"), (("",), ""), (("x",), "X"),
                (("grace  hopper",), "GH")),
        start=(
            "def initials(name):\n"
            "    out = ''\n"
            "    for part in name.split(' '):\n"
            "        out += part[0].upper()\n"
            "    return out"
        ),
        bug="split(' ') keeps the empty strings that a double space or a "
            "leading space produces, and part[0] on an empty string is an "
            "IndexError. split() with no argument drops them for you.",
    ),
)
