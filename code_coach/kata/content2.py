"""More katas: turning things into other things, and grids.

Two families that Codewars and freeCodeCamp lean on and this app did not
have. They are chosen because they are the shapes where the edge case is
the whole exercise rather than a footnote.

A cipher or an encoding has a boundary in it by construction — the
alphabet wraps, the count of one is still a count, the empty string is
still a valid input — and getting those right is most of the work. A grid
has the same property in two dimensions: one row, one column, a single
cell, no rows at all.

The grid functions here never modify the grid they were given, and that
is load-bearing rather than tidy. Counting islands by sinking them as you
go is the obvious way to write it and wrecks the caller's data; the
marker now compares the arguments before and after the call, so the
obvious way fails and says why. That check exists because a function
returning the right answer while quietly destroying its input is the bug
this language is most generous with.
"""

from __future__ import annotations

from code_coach.kata import Kata

# ── Turning things into other things ─────────────────────────


def _caesar(text: str, shift: int) -> str:
    out = []
    for c in text:
        if c.isalpha():
            base = ord("A") if c.isupper() else ord("a")
            out.append(chr((ord(c) - base + shift) % 26 + base))
        else:
            out.append(c)
    return "".join(out)


def _run_length(text: str) -> str:
    if not text:
        return ""
    out = []
    run = 1
    for i in range(1, len(text) + 1):
        if i < len(text) and text[i] == text[i - 1]:
            run += 1
        else:
            out.append(f"{text[i - 1]}{run}")
            run = 1
    return "".join(out)


def _expand(code: str) -> str:
    out = []
    i = 0
    while i < len(code):
        letter = code[i]
        i += 1
        digits = ""
        while i < len(code) and code[i].isdigit():
            digits += code[i]
            i += 1
        out.append(letter * int(digits or 1))
    return "".join(out)


def _to_roman(n: int) -> str:
    # The table lives inside the function rather than beside it. Show
    # answer hands over the source of this function and nothing else, so
    # a reference that leans on a module-level name is code the student
    # cannot run — which is what the suite found the moment it tried.
    table = (
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    )
    out = []
    for value, letters in table:
        while n >= value:
            out.append(letters)
            n -= value
    return "".join(out)


def _from_roman(text: str) -> int:
    worth = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, c in enumerate(text):
        here = worth[c]
        after = worth[text[i + 1]] if i + 1 < len(text) else 0
        total += -here if here < after else here
    return total


def _to_base(n: int, base: int) -> str:
    if n == 0:
        return "0"
    digits = "0123456789abcdef"
    out = ""
    while n:
        out = digits[n % base] + out
        n //= base
    return out


TURNING: tuple[Kata, ...] = (
    Kata(
        id="caesar",
        name="caesar",
        brief=(
            "Shift every letter along the alphabet by the given amount, "
            "wrapping round from z to a. Keep the case, and leave anything "
            "that is not a letter alone."
        ),
        params=("text", "shift"),
        family="Turning things",
        example='caesar("abc", 1) is "bcd"',
        hint=(
            "The modulo is what wraps it. Subtract the base letter first, "
            "take the remainder by 26, then add the base back."
        ),
        cases=(
            ("abc", 1), ("", 5), ("xyz", 3), ("Hello, World!", 0),
            ("Hello, World!", 13), ("a", 26), ("a", 25), ("ABC", 1),
            ("z", 1), ("The quick brown fox", 5),
        ),
        solve=_caesar,
        checks=(
            (("abc", 1), "bcd"), (("", 5), ""), (("xyz", 3), "abc"),
            (("Hello, World!", 0), "Hello, World!"), (("z", 1), "a"),
            (("a", 26), "a"), (("ABC", 1), "BCD"),
        ),
    ),
    Kata(
        id="run-length",
        name="run_length",
        brief=(
            "Compress the text by writing each character followed by how "
            "many times it repeats. A single character still gets its 1."
        ),
        params=("text",),
        family="Turning things",
        example='run_length("aaabb") is "a3b2"',
        hint=(
            "Walk one past the end, and let that be what closes the last "
            "run — otherwise the final group never gets written."
        ),
        cases=(
            ("aaabb",), ("",), ("a",), ("abc",), ("aaaaaaaaaa",),
            ("aabbaa",), ("ab",), ("zzz",), ("Hello",), ("112233",),
        ),
        solve=_run_length,
        checks=(
            (("aaabb",), "a3b2"), (("",), ""), (("a",), "a1"),
            (("abc",), "a1b1c1"), (("aabbaa",), "a2b2a2"),
            (("aaaaaaaaaa",), "a10"),
        ),
    ),
    Kata(
        id="expand",
        name="expand",
        brief=(
            "The other direction: turn a character and a count back into "
            "that many of it. The counts can be more than one digit."
        ),
        params=("code",),
        family="Turning things",
        example='expand("a3b2") is "aaabb"',
        hint=(
            "Read the digits after a letter until they stop. A count of "
            "ten is two characters, not one."
        ),
        cases=(
            ("a3b2",), ("",), ("a1",), ("a1b1c1",), ("a10",),
            ("a2b2a2",), ("z3",), ("H1e1l2o1",), ("x12",), ("a1b20",),
        ),
        solve=_expand,
        checks=(
            (("a3b2",), "aaabb"), (("",), ""), (("a1",), "a"),
            (("a10",), "aaaaaaaaaa"), (("x12",), "x" * 12),
        ),
    ),
    Kata(
        id="to-roman",
        name="to_roman",
        brief=(
            "Write the number in Roman numerals. Four is IV rather than "
            "IIII, and the same subtraction applies at nine, forty, ninety "
            "and so on."
        ),
        params=("n",),
        family="Turning things",
        example="to_roman(1994) is MCMXCIV",
        hint=(
            "Put the subtracting pairs — CM, CD, XC, XL, IX, IV — in the "
            "same table as the plain ones, largest first, and the rule "
            "falls out of taking each as often as it fits."
        ),
        cases=(
            (1,), (4,), (9,), (14,), (40,), (90,), (400,), (1994,),
            (3999,), (2026,),
        ),
        solve=_to_roman,
        checks=(
            ((1,), "I"), ((4,), "IV"), ((9,), "IX"), ((14,), "XIV"),
            ((40,), "XL"), ((1994,), "MCMXCIV"), ((3999,), "MMMCMXCIX"),
        ),
    ),
    Kata(
        id="from-roman",
        name="from_roman",
        brief=(
            "Read a Roman numeral back as a number. A smaller letter "
            "before a larger one is subtracted."
        ),
        params=("text",),
        family="Turning things",
        example="from_roman('MCMXCIV') is 1994",
        hint=(
            "Compare each letter with the one after it. If this one is "
            "worth less, it counts as negative."
        ),
        cases=(
            ("I",), ("IV",), ("IX",), ("XIV",), ("XL",), ("MCMXCIV",),
            ("MMMCMXCIX",), ("MMXXVI",), ("V",), ("XC",),
        ),
        solve=_from_roman,
        checks=(
            (("I",), 1), (("IV",), 4), (("IX",), 9), (("XIV",), 14),
            (("MCMXCIV",), 1994), (("MMMCMXCIX",), 3999),
        ),
    ),
    Kata(
        id="to-base",
        name="to_base",
        brief=(
            "Write the number in the given base, from 2 to 16, using "
            "lower-case letters for the digits past nine. Zero is '0' in "
            "every base."
        ),
        params=("n", "base"),
        family="Turning things",
        example="to_base(255, 16) is 'ff'",
        hint=(
            "Take the remainder for the last digit, divide, repeat. Zero "
            "is the case that falls out of the loop having written "
            "nothing."
        ),
        cases=(
            (10, 2), (0, 2), (255, 16), (7, 8), (1, 2), (0, 16),
            (64, 8), (4095, 16), (5, 10), (31, 2),
        ),
        solve=_to_base,
        checks=(
            ((10, 2), "1010"), ((0, 2), "0"), ((255, 16), "ff"),
            ((7, 8), "7"), ((1, 2), "1"), ((0, 16), "0"),
            ((4095, 16), "fff"),
        ),
    ),
)


# ── Grids ────────────────────────────────────────────────────


def _transpose(grid: list) -> list:
    if not grid:
        return []
    return [[row[c] for row in grid] for c in range(len(grid[0]))]


def _diagonal_sum(grid: list) -> int:
    size = len(grid)
    total = 0
    for i in range(size):
        total += grid[i][i]
        if i != size - 1 - i:
            total += grid[i][size - 1 - i]
    return total


def _spiral(grid: list) -> list:
    if not grid or not grid[0]:
        return []
    top, bottom = 0, len(grid) - 1
    left, right = 0, len(grid[0]) - 1
    out = []
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            out.append(grid[top][c])
        top += 1
        for r in range(top, bottom + 1):
            out.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                out.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                out.append(grid[r][left])
            left += 1
    return out


def _rotate(grid: list) -> list:
    if not grid:
        return []
    size = len(grid)
    return [[grid[size - 1 - r][c] for r in range(size)]
            for c in range(len(grid[0]))]


def _count_islands(grid: list) -> int:
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen: set = set()
    found = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 1 or (r, c) in seen:
                continue
            found += 1
            stack = [(r, c)]
            seen.add((r, c))
            while stack:
                y, x = stack.pop()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if not (0 <= ny < rows and 0 <= nx < cols):
                        continue
                    if grid[ny][nx] == 1 and (ny, nx) not in seen:
                        seen.add((ny, nx))
                        stack.append((ny, nx))
    return found


GRIDS: tuple[Kata, ...] = (
    Kata(
        id="transpose",
        name="transpose",
        brief=(
            "Turn the rows into columns. The grid you were given must not "
            "change."
        ),
        params=("grid",),
        family="Grids",
        example="transpose([[1, 2], [3, 4]]) is [[1, 3], [2, 4]]",
        hint="Build it column by column: each new row is one old column.",
        cases=(
            ([[1, 2], [3, 4]],), ([],), ([[1]],), ([[1, 2, 3]],),
            ([[1], [2], [3]],), ([[1, 2], [3, 4], [5, 6]],),
            ([[0, 0], [0, 0]],), ([[-1, 2], [3, -4]],),
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), ([[9]],),
        ),
        solve=_transpose,
        checks=(
            ((([[1, 2], [3, 4]],)), [[1, 3], [2, 4]]),
            ((([],)), []),
            ((([[1]],)), [[1]]),
            ((([[1, 2, 3]],)), [[1], [2], [3]]),
            ((([[1], [2], [3]],)), [[1, 2, 3]]),
        ),
    ),
    Kata(
        id="diagonal-sum",
        name="diagonal_sum",
        brief=(
            "Add up both diagonals of a square grid. Where they cross, "
            "that cell is counted once, not twice."
        ),
        params=("grid",),
        family="Grids",
        example="diagonal_sum([[1, 2], [3, 4]]) is 10",
        hint=(
            "An odd-sized grid has a middle cell on both diagonals. The "
            "test for it is whether the two column numbers are the same."
        ),
        cases=(
            ([[1, 2], [3, 4]],), ([[5]],), ([],),
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],),
            ([[0, 0], [0, 0]],), ([[1, 1], [1, 1]],),
            ([[-1, -2], [-3, -4]],), ([[2, 0, 0], [0, 3, 0], [0, 0, 4]],),
            ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
              [13, 14, 15, 16]],),
            ([[7, 0], [0, 7]],),
        ),
        solve=_diagonal_sum,
        checks=(
            ((([[1, 2], [3, 4]],)), 10),
            ((([[5]],)), 5),
            ((([],)), 0),
            ((([[1, 2, 3], [4, 5, 6], [7, 8, 9]],)), 25),
            ((([[1, 1], [1, 1]],)), 4),
        ),
    ),
    Kata(
        id="spiral",
        name="spiral",
        brief=(
            "Read the grid clockwise from the top left, spiralling "
            "inwards, and return the values in that order."
        ),
        params=("grid",),
        family="Grids",
        example="spiral([[1, 2], [3, 4]]) is [1, 2, 4, 3]",
        hint=(
            "Keep four edges and move them inwards. The two checks in the "
            "middle are what stop a single row being read back again."
        ),
        cases=(
            ([[1, 2], [3, 4]],), ([],), ([[1]],), ([[1, 2, 3]],),
            ([[1], [2], [3]],),
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],),
            ([[1, 2], [3, 4], [5, 6]],),
            ([[1, 2, 3, 4]],),
            ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],),
            ([[0]],),
        ),
        solve=_spiral,
        checks=(
            ((([[1, 2], [3, 4]],)), [1, 2, 4, 3]),
            ((([],)), []),
            ((([[1]],)), [1]),
            ((([[1, 2, 3]],)), [1, 2, 3]),
            ((([[1], [2], [3]],)), [1, 2, 3]),
            ((([[1, 2, 3], [4, 5, 6], [7, 8, 9]],)),
             [1, 2, 3, 6, 9, 8, 7, 4, 5]),
        ),
    ),
    Kata(
        id="rotate",
        name="rotate",
        brief=(
            "Turn the square grid a quarter turn clockwise and return the "
            "new one. The grid you were given must not change."
        ),
        params=("grid",),
        family="Grids",
        example="rotate([[1, 2], [3, 4]]) is [[3, 1], [4, 2]]",
        hint=(
            "The new top row is the old first column read from the bottom "
            "up."
        ),
        cases=(
            ([[1, 2], [3, 4]],), ([],), ([[1]],),
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],),
            ([[0, 0], [0, 0]],), ([[1, 1], [2, 2]],),
            ([[-1, 2], [3, -4]],), ([[5, 6], [7, 8]],),
            ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
              [13, 14, 15, 16]],),
            ([[9]],),
        ),
        solve=_rotate,
        checks=(
            ((([[1, 2], [3, 4]],)), [[3, 1], [4, 2]]),
            ((([],)), []),
            ((([[1]],)), [[1]]),
            ((([[1, 2, 3], [4, 5, 6], [7, 8, 9]],)),
             [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
        ),
    ),
    Kata(
        id="count-islands",
        name="count_islands",
        brief=(
            "Count the groups of 1s in the grid. Two cells are in the same "
            "group when they touch up, down, left or right — not "
            "diagonally. The grid you were given must not change."
        ),
        params=("grid",),
        family="Grids",
        example="count_islands([[1, 0], [0, 1]]) is 2",
        hint=(
            "Keep a set of the cells you have already counted. Sinking "
            "the island by writing zeros over it is the usual way and it "
            "wrecks the grid you were handed."
        ),
        cases=(
            ([[1, 0], [0, 1]],), ([],), ([[0]],), ([[1]],),
            ([[1, 1], [1, 1]],), ([[0, 0], [0, 0]],),
            ([[1, 0, 1], [0, 0, 0], [1, 0, 1]],),
            ([[1, 1, 0], [0, 1, 0], [0, 0, 1]],),
            ([[1, 0, 1, 0, 1]],),
            ([[1], [0], [1]],),
        ),
        solve=_count_islands,
        checks=(
            ((([[1, 0], [0, 1]],)), 2),
            ((([],)), 0),
            ((([[0]],)), 0),
            ((([[1]],)), 1),
            ((([[1, 1], [1, 1]],)), 1),
            ((([[1, 0, 1], [0, 0, 0], [1, 0, 1]],)), 4),
            ((([[1, 1, 0], [0, 1, 0], [0, 0, 1]],)), 2),
        ),
    ),
)


MORE: tuple[Kata, ...] = TURNING + GRIDS
