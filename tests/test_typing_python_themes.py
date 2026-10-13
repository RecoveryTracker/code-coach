"""The four themed Python typing sets obey the rules.

`snippets_pygame`, `snippets_pydata`, `snippets_pyscript` and
`snippets_pysci` are held to the guards the JavaScript sets keep in
tests/test_typing_jsnode_music_cooking.py: every character on the keyboard,
a note on everything, lengths inside the range the existing Python pool
already uses, nothing already in that pool or in the other modules, every
line is valid Python, and every block runs in the real interpreter.

One more for the blocks, because what they print is the point of them: each
prints exactly the answer written down for it below, worked out by hand
from the block's own figures before Python was asked.

The blocks are held to no clock, no dice that are not seeded (the one
that rolls any uses random.Random), no sys.argv, no other programs and no
internet. The ones that touch the disk do it inside a TemporaryDirectory,
and the one with a server listens on 127.0.0.1, port 0 and shuts it down.
"""

from __future__ import annotations

import ast
import functools
import re
import textwrap
import unittest

from code_coach.typing.curriculum import (
    MAX_BLOCK_LINES,
    MIN_BLOCK_LINES,
    MIN_LENGTH,
    code_blocks_for,
    code_lines_for,
)
from code_coach.typing.drills import UNTYPEABLE
from code_coach.typing.keys import BY_CHAR
from code_coach.typing.snippets import PYTHON_CODE
from code_coach.typing.snippets_pydata import PYDATA_BLOCKS, PYDATA_LINES
from code_coach.typing.snippets_pygame import PYGAME_BLOCKS, PYGAME_LINES
from code_coach.typing.snippets_pyscript import PYSCRIPT_BLOCKS, PYSCRIPT_LINES
from code_coach.typing.snippets_pysci import PYSCI_BLOCKS, PYSCI_LINES

_PREFIX = "Python · "

_MODULES = (
    (PYGAME_LINES, PYGAME_BLOCKS),
    (PYDATA_LINES, PYDATA_BLOCKS),
    (PYSCRIPT_LINES, PYSCRIPT_BLOCKS),
    (PYSCI_LINES, PYSCI_BLOCKS),
)
_ALL_LINES = PYGAME_LINES + PYDATA_LINES + PYSCRIPT_LINES + PYSCI_LINES
_ALL_BLOCKS = PYGAME_BLOCKS + PYDATA_BLOCKS + PYSCRIPT_BLOCKS + PYSCI_BLOCKS

# Every Python line and block already served somewhere. Once these modules
# are registered their own passages may turn up in a pool too, so they are
# taken out by identity before comparing.
_MINE = {id(p) for p in _ALL_LINES + _ALL_BLOCKS}
_POOL_LINES = code_lines_for("python", curated=PYTHON_CODE)
_EXISTING_LINES = [p for p in _POOL_LINES if id(p) not in _MINE]
_POOL_BLOCKS = code_blocks_for("python")
_EXISTING_BLOCKS = [p for p in _POOL_BLOCKS if id(p) not in _MINE]


def _table(rows: list[tuple[str, ...]]) -> str:
    return "\n".join("".join(r) for r in rows)


#: What each pygame-style block prints, by its note. Worked out by hand.
PYGAME_PRINTS = {
    # clamp keeps t in 0..1, so 1.5 lerps like 1. 10 + 10 * 0.25 = 12.5.
    # Integer t stays an integer: lerp(10, 20, 0) is 10, and at 1 it is 20.
    "clamp and lerp, with t kept in range":
        "0 10\n0.25 12.5\n0.5 15.0\n1.5 20\n0 7 10",
    # 1/60 is 16.67 ms. Frames: 10 ms owes nothing; +20 = 30 ms, one step
    # (13.33 left); +40 = 53.33, three steps (3.33 left); +16 = 19.33, one
    # more (2.67 left). Five steps; 2.67 ms of 16.67 is 0.16 of a step.
    "a fixed timestep fed uneven frames": "5 2.67 0.16",
    # Each frame adds 90 to vy: -210, -120, -30, 60, 150, 240. y moves by
    # a tenth of vy: 279, 267, 264, 270, 285, then 309 clamps to the floor.
    # Six frames, a highest point of 264, and a landing speed of 240.
    "a jump under gravity, stepped by delta time": "6 264.0 240.0",
    # The player covers x 10..30, y 10..30. The first coin sits inside; the
    # second touches the right edge and the third the left corner, which do
    # not overlap; the fourth is inside.
    "box collision: touching edges do not count":
        "[True, False, False, True]\n2",
    # (6, 8) is 10 away: 5 + 5 touches, 100 <= 100. With 5 + 4 it does not.
    "circle collision without a square root": "True\nFalse\n5.0 10.0",
    # Walls: 7 + 2 + 3 + 7 = 19. The player is at (1, 1); gems at (4, 1)
    # and (3, 2). Pixel (40, 25) is tile column 2, row 1: a floor.
    "a level read from strings, and a pixel found on it":
        "19 [(1, 1)] [(4, 1), (3, 2)]\n(2, 1) .",
    # The menu ignores "pause"; start plays; pause pauses; pause resumes;
    # an unknown event changes nothing.
    "a state machine as a table of moves": "\n".join((
        "pause MENU",
        "start PLAYING",
        "pause PAUSED",
        "pause PLAYING",
        "quit PLAYING",
    )),
    # auto() counts from 1, so PAUSE is 2. Toggling twice comes back.
    "an enum and a match that flips it": "PAUSE True 2",
    # The same seed gives the same spawns; seeds 42 and 43 differ. Every
    # x is a multiple of 16 below 160, and there are fifty points.
    "a seeded generator replays the same spawns": "True False\nTrue 50",
    # x: 10 + 25 + 25 - 25 = 35, and the last direction was -1.
    "a dataclass entity that moves by delta time": "Ship(x=35.0, vx=-100.0)",
    # 1200 twice: ana before cy by name; then 950 and 40.
    "a high-score table, ties broken by name": _table([
        ("1. ", "ana".ljust(4), "1200".rjust(6)),
        ("2. ", "cy".ljust(4), "1200".rjust(6)),
        ("3. ", "bo".ljust(4), "950".rjust(6)),
        ("4. ", "di".ljust(4), "40".rjust(6)),
    ]),
    # Frame 2 fires (timer 500), the timer runs down 400, 300, 200, 100 and
    # reaches 0 on frame 7, which is odd, so it fires again on frame 8.
    # The timer is back at 100 on frame 12.
    "a weapon cooldown counted in whole milliseconds": "[2, 8]",
}

#: What each data block prints, by its note. Worked out by hand.
PYDATA_PRINTS = {
    # the 3, and 2, cat 1, hat 1, bat 1. A missing word counts 0 without
    # being added. After two more cats the tie at 3 goes to the first seen.
    "Counter: tally, rank and update":
        "[('the', 3), ('and', 2)]\n1 0 5\n[('the', 3)] 10",
    # Zero is added for "z" before len() runs, so the length is 4.
    "defaultdict: words grouped by first letter": "\n".join((
        "{'a': ['apple', 'avocado'], 'b': ['bob', 'banana'], "
        "'c': ['cat', 'cherry']}",
        "{'a': 2, 'b': 2, 'c': 2}",
        "[] 4",
    )),
    # Means of the window: 10, 15, 20, 30, 40. Rotating right by one puts
    # the 50 in front, so popleft gives 50.
    "deque: a moving average over the last three": (
        "deque([30, 40, 50], maxlen=3) [10.0, 15.0, 20.0, 30.0, 40.0]\n"
        "[50, 30, 40] 50"
    ),
    # 3 + 4i has length 5.
    "namedtuple: names on a tuple": (
        "Point(x=3, y=4) Point(x=10, y=4) 14\n"
        "{'x': 3, 'y': 4} ('x', 'y')\n"
        "5.0 True"
    ),
    # Sorted by length (stable): fig, then pear plum kiwi, then apple.
    "itertools: accumulate, chain, islice, product and groupby": "\n".join((
        "[1, 3, 6, 10] [3, 3, 4, 4, 5]",
        "['a', 'b', 1, 2] [2, 4, 6]",
        "[('a', 0), ('a', 1), ('b', 0), ('b', 1)]",
        "[(3, ['fig']), (4, ['pear', 'plum', 'kiwi']), (5, ['apple'])]",
    )),
    # fib(30) is 832040 and is worked out for 0..30: 31 calls. Lookups are
    # 1 + 2 * 29 = 59, of which 31 miss and 28 hit. Clearing empties it.
    "lru_cache: each Fibonacci number worked out once":
        "832040 31\n28 31\n0",
    # 2 * 3 * 4; 0b1011; 7 squared; the digits fold into 2024.
    "reduce and partial": "24 11 49\n2024\nint {'base': 2}",
    # Ordered on price only: gum 1.25, pen 2.0, tea 3.5. replace keeps the
    # empty tags tuple.
    "a frozen, ordered dataclass, copied with replace":
        "gum tea\nItem(price=0.99, name='tea', tags=()) ()",
    # ana has the top score. The writer's text is 'a,1', then b with a
    # quoted field because of its comma; repr shows the escapes.
    "CSV and JSON through io.StringIO": "\n".join((
        "{'name': 'ana', 'score': '90'} 3",
        "'a,1\\nb,\"x,y\"\\n'",
        '{"a": true, "b": [1, null]}',
    )),
    # Mean 84, median and mode 80. Deviations -14 -4 -4 6 16 squared sum to
    # 520, over 5 is 104, root 10.2. Quartiles (exclusive): 75, 80, 95.
    # 2.675 is exactly 2.675 as a Decimal, so half-up gives 2.68.
    "statistics, then exact arithmetic with Decimal and Fraction": "\n".join((
        "84 80 80",
        "10.2 [75.0, 80.0, 95.0]",
        "False True",
        "2.68",
        "1/2 3/4 0.375",
    )),
    "zip, enumerate and comprehensions": "\n".join((
        "[(90, 'ana'), (85, 'cy'), (72, 'bo')]",
        "{'ana': 90, 'cy': 85}",
        "[[1, 4], [2, 5], [3, 6]]",
        "['1:ana', '2:bo', '3:cy']",
    )),
    "generic functions and a type alias, in 3.12 syntax":
        "3 None ('y', 'x')",
}

#: What each scripting block prints, by its note. Worked out by hand.
PYSCRIPT_PRINTS = {
    # The name keeps both dots; the stem drops only the last suffix;
    # with_suffix swaps it; parts[-2] is the folder.
    "taking a path apart with PurePosixPath": "\n".join((
        "demo.final.mp3 demo.final .mp3 /home/ann/music",
        "demo.final.wav music",
        "music/demo.final.mp3 ['.final', '.mp3']",
        "a/b/c.txt True",
    )),
    # The pretty file has six lines: braces, runs, tags, a, bracket, brace.
    # Only state.json is there, and the folder is gone afterwards.
    "JSON kept in a temporary folder that cleans up after itself":
        "{'runs': 2, 'tags': ['a']} 6\n['state.json']\nFalse",
    "argparse reading an explicit list, not sys.argv": (
        "docs True 6\n"
        "Namespace(folder='src', verbose=False, limit=10)"
    ),
    "argparse subcommands": "add 9\nreset",
    "logging into a string, with a level and a format":
        "INFO:tool:copied 3 files\nWARNING:tool:skipping a.tmp",
    "a tiny server on port 0 that answers its own request": "/HELLO",
    # Results come back in the order asked for; the log is in delay order.
    "gather: results in call order, finishing in delay order":
        "['SLOW', 'FAST', 'MID'] ['fast', 'mid', 'slow']",
    "a TaskGroup that waits for every task": "['a', 'b']",
    "asyncio.timeout cuts a slow wait short": "timed out\ndone",
    # Opened a then b; the body adds A and B; they close in reverse.
    "a context manager written as a generator":
        "['open a', 'open b', 'AB', 'close b', 'close a']",
    # The division is suppressed, so "never" is skipped. ExitStack runs
    # its callbacks last in, first out.
    "suppress, and an ExitStack that closes in reverse":
        "working\nclosing 2\nclosing 1\ndone",
    # 1536 / 1024 = 1.5; 2,480,000 / 1024 = 2421.875, which rounds up to
    # 2421.9; 90 / 1024 = 0.088, which rounds to 0.1.
    "a size table, behind the main guard": _table([
        ("notes.txt".ljust(12), "1,536".rjust(10), " ", "1.5".rjust(7), " KiB"),
        ("photo.jpg".ljust(12), "2,480,000".rjust(10), " ",
         "2421.9".rjust(7), " KiB"),
        ("a.py".ljust(12), "90".rjust(10), " ", "0.1".rjust(7), " KiB"),
    ]),
    "environment variables and splitting a command line": "\n".join((
        "['python', '-m', 'venv', '.venv 2', '--prompt', 'demo']",
        "1 unset",
        "pip install 'my pkg'",
    )),
}

#: What each science block prints, by its note. Worked out by hand.
PYSCI_PRINTS = {
    # 70 * 8.9 / 9.8 = 63.57; 70 * 3.7 / 9.8 = 26.43; 70 * 23.1 / 9.8 = 165.
    "weight elsewhere, as a scale set for Earth would show it":
        "Venus: 63.6 kg\nMars: 26.4 kg\nJupiter: 165.0 kg",
    # 499.0 s is 8 min 19 s; Mars is 760.5 s, which rounds to 761 = 12 min
    # 41 s; the Moon is 1.28 s, which rounds to 1.
    "how long light takes to arrive": (
        "Sun to Earth: 8 min 19 s\n"
        "Sun to Mars: 12 min 41 s\n"
        "Moon to Earth: 0 min 1 s"
    ),
    # 149.6e6 km is 1.0000 AU. 228e6 is 1.5241 AU, whose 1.5 power is
    # 1.8815. 778.5e6 is 5.2040 AU, which gives 11.871.
    "Kepler's third law: the year from the distance": (
        "Earth: 1.00 AU, 1.00 years\n"
        "Mars: 1.52 AU, 1.88 years\n"
        "Jupiter: 5.20 AU, 11.87 years"
    ),
    # sqrt(2 G M / r): Earth 11178 m/s, Mars 5023, the Moon 2376.
    "escape velocity from mass and size":
        "Earth: 11.2 km/s\nMars: 5.0 km/s\nMoon: 2.4 km/s",
    # Epley 100 x 1.2 = 120, Brzycki 3600 / 31 = 116.1; 200 x 1.1 = 220,
    # 7200 / 34 = 211.8; 60 x 4/3 = 80, 2160 / 27 = 80.
    "two one-rep max estimates side by side":
        "100 6 120 116\n200 3 220 212\n60 10 80 80",
    # 225: 90 a side is two 45s. 185: 70 is a 45 and a 25. 137.5: 46.25
    # is a 45 with 1.25 left over, which no plate fills.
    "plate math: the plates for each side of the bar":
        "([45, 45], 0.0)\n([45, 25], 0.0)\n([45], 1.25)",
    # 120 + 200 + 108 = 428, fat 108 / 428 = 25%. 180 + 240 + 180 = 600,
    # 30%. 160 + 160 + 225 = 545, 41%. Total 1573.
    "calories from the macros of three meals": _table([
        ("breakfast".ljust(10), "428".rjust(5), " kcal ", " 25%", " fat"),
        ("lunch".ljust(10), "600".rjust(5), " kcal ", " 30%", " fat"),
        ("dinner".ljust(10), "545".rjust(5), " kcal ", " 41%", " fat"),
        ("total 1573",),
    ]),
    # 440 * 2 ** (-9 / 12) = 261.63; 440 * 2 ** (3 / 12) = 523.25.
    "MIDI numbers as note names and frequencies":
        "C4 261.63\nA4 440.00\nC5 523.25\nA5 880.00",
    # G major: G A B C D E F#. C E G down five: G B D. A B up fourteen,
    # which is 2 more than an octave: B and C#.
    "a major scale and transposing with a remainder":
        "G A B C D E F#\n['G', 'B', 'D'] ['B', 'C#']",
    # 60000 / 90 = 666.67, x 4 = 2666.7; 60000 / 174 = 344.83, x 4 = 1379.3.
    "a tempo table in fixed columns": _table([
        ("BPM".rjust(4), "beat ms".rjust(10), "bar ms".rjust(9)),
        ("60".rjust(4), "1000.0".rjust(10), "4000".rjust(9)),
        ("90".rjust(4), "666.7".rjust(10), "2667".rjust(9)),
        ("100".rjust(4), "600.0".rjust(10), "2400".rjust(9)),
        ("120".rjust(4), "500.0".rjust(10), "2000".rjust(9)),
        ("174".rjust(4), "344.8".rjust(10), "1379".rjust(9)),
    ]),
    # k = 3/2: flour 3/4 x 3/2 = 9/8, sugar 1/2, milk 3/4. For two, k = 1/2
    # and the total is 3/8 + 1/6 + 1/4 = 19/24.
    "scaling a recipe exactly with Fraction": _table([
        ("flour".ljust(6), "9/8".rjust(5), " cups ", "1.125"),
        ("sugar".ljust(6), "1/2".rjust(5), " cups ", "0.500"),
        ("milk".ljust(6), "3/4".rjust(5), " cups ", "0.750"),
        ("19/24",),
    ]),
    # 5 km is 5000 m, 3.107 miles, 16404.199 feet. 26.2 mi is 42.16 km.
    "unit conversion from one table": _table([
        ("m".rjust(3), " ", "5000.000".rjust(10)),
        ("mi".rjust(3), " ", "3.107".rjust(10)),
        ("ft".rjust(3), " ", "16404.199".rjust(10)),
        ("42.2 1.0",),
    ]),
}


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    from code_coach.engine import run_code

    return run_code(code, language="python")


def _assert_typeable(case: unittest.TestCase, text: str) -> None:
    for char in text:
        if char == "\n":
            continue
        case.assertNotIn(char, UNTYPEABLE, text)
        case.assertIn(char, BY_CHAR, f"{char!r} in {text!r}")


#: Ways to finish a line that opens something, tried in turn. Every line is
#: put in an `async def` first, so await, return and yield are all fine.
_FINISHES = (
    lambda t: t,
    lambda t: t + "\n    pass",                               # opens a block
    lambda t: t + "\nclass _C: pass",                         # a decorator
    lambda t: t + "\n    case _:\n        pass",              # a match
    lambda t: "match _x:\n    " + t + "\n        pass",      # a case
    lambda t: "try:\n    pass\n" + t + "\n    pass",          # an except
)


def _parses(text: str) -> bool:
    for finish in _FINISHES:
        source = "async def _f():\n" + textwrap.indent(finish(text), "    ")
        try:
            ast.parse(source)
        except SyntaxError:
            continue
        return True
    return False


class _LineRules:
    """The rules every line in one of the modules keeps."""

    LINES: tuple = ()
    #: The other modules' lines, which these must not repeat either.
    OTHER: tuple = ()

    def test_there_are_enough(self) -> None:
        self.assertGreaterEqual(len(self.LINES), 55)

    def test_every_character_is_on_the_keyboard(self) -> None:
        for passage in self.LINES:
            _assert_typeable(self, passage.text)

    def test_single_lines_without_stray_whitespace(self) -> None:
        for passage in self.LINES:
            self.assertNotIn("\n", passage.text)
            self.assertNotIn("\t", passage.text)
            self.assertNotIn("  ", passage.text, passage.text)
            self.assertEqual(passage.text, passage.text.strip())

    def test_every_line_is_code_rather_than_a_comment(self) -> None:
        for passage in self.LINES:
            self.assertFalse(passage.text.startswith("#"), passage.text)

    def test_every_line_says_what_it_does(self) -> None:
        for passage in self.LINES:
            self.assertTrue(passage.source.strip(), passage.text)
            _assert_typeable(self, passage.source)

    def test_lengths_sit_inside_the_existing_range(self) -> None:
        high = max(len(p.text) for p in _POOL_LINES)
        low = max(MIN_LENGTH, 15)
        for passage in self.LINES:
            self.assertGreaterEqual(len(passage.text), low, passage.text)
            self.assertLessEqual(len(passage.text), high, passage.text)

    def test_no_duplicates_here_or_against_the_existing_pool(self) -> None:
        texts = [p.text for p in self.LINES]
        self.assertEqual(len(texts), len(set(texts)))
        existing = {p.text for p in _EXISTING_LINES}
        self.assertEqual(existing & set(texts), set())
        self.assertEqual({p.text for p in self.OTHER} & set(texts), set())

    def test_every_line_parses(self) -> None:
        """Each line, inside an async function, finished the way it would be
        in a file: a line that opens a block gets a body, an `except` gets
        its `try`, a `case` gets its `match`."""
        bad = [p.text for p in self.LINES if not _parses(p.text)]
        self.assertEqual(bad, [])


class _BlockRules:
    """The rules every block in one of the modules keeps."""

    BLOCKS: tuple = ()
    OTHER: tuple = ()
    #: What each block prints, by its note, worked out by hand.
    PRINTS: dict[str, str] = {}
    #: The most lines a block of this theme may have.
    MAX_LINES = 12
    #: Words a block of this theme may not use.
    BANNED = (
        "import time", "time.", "datetime", "perf_counter", "monotonic",
        "sys.argv", "input(", "subprocess", "socket", "requests", "pygame",
        "open(", "mkdtemp", "mkstemp", "os.system", "os.remove",
    )

    def test_there_are_enough(self) -> None:
        self.assertGreaterEqual(len(self.BLOCKS), 8)

    def test_every_character_is_on_the_keyboard(self) -> None:
        for passage in self.BLOCKS:
            _assert_typeable(self, passage.text)

    def test_a_length_a_person_will_finish(self) -> None:
        width = max(
            len(ln) for b in _POOL_BLOCKS for ln in b.text.splitlines()
        )
        for passage in self.BLOCKS:
            lines = [ln for ln in passage.text.splitlines() if ln.strip()]
            with self.subTest(block=passage.text[:30]):
                self.assertGreaterEqual(len(lines), max(MIN_BLOCK_LINES, 4))
                self.assertLessEqual(len(lines), min(MAX_BLOCK_LINES, self.MAX_LINES))
                for line in passage.text.splitlines():
                    self.assertLessEqual(len(line), width, line)

    def test_tidy_and_really_indented(self) -> None:
        for passage in self.BLOCKS:
            with self.subTest(block=passage.text[:30]):
                self.assertEqual(passage.text, passage.text.strip("\n"))
                self.assertNotIn("\t", passage.text)
                for line in passage.text.splitlines():
                    self.assertEqual(line, line.rstrip())
                    indent = len(line) - len(line.lstrip(" "))
                    self.assertEqual(indent % 4, 0, line)

    def test_nothing_reads_the_clock_or_rolls_unseeded_dice(self) -> None:
        """The printed answer is held to a fixed one, so it must be the
        same on every run."""
        for passage in self.BLOCKS:
            for word in self.BANNED:
                self.assertNotIn(word, passage.text)
            self.assertIsNone(
                re.search(r"\brandom\.(?!Random\()", passage.text), passage.text)
            self.assertNotIn("urlopen", passage.text)

    def test_every_note_names_the_language(self) -> None:
        for passage in self.BLOCKS:
            self.assertTrue(passage.source.startswith(_PREFIX))
            self.assertTrue(passage.source[len(_PREFIX):].strip())

    def test_no_duplicates_here_or_against_the_existing_blocks(self) -> None:
        texts = [p.text for p in self.BLOCKS]
        self.assertEqual(len(texts), len(set(texts)))
        existing = {p.text for p in _EXISTING_BLOCKS}
        self.assertEqual(existing & set(texts), set())
        self.assertEqual({p.text for p in self.OTHER} & set(texts), set())

    def test_every_block_has_a_worked_out_answer_and_no_answer_is_stale(self) -> None:
        notes = [p.source[len(_PREFIX):] for p in self.BLOCKS]
        self.assertEqual(len(notes), len(set(notes)))
        self.assertEqual(set(notes) - set(self.PRINTS), set(),
                         "a block with nothing written down for it to print")
        self.assertEqual(set(self.PRINTS) - set(notes), set(),
                         "an answer for a block that is no longer here")
        for answer in self.PRINTS.values():
            self.assertTrue(answer.strip())

    def test_every_block_runs_and_prints_what_was_worked_out(self) -> None:
        for passage in self.BLOCKS:
            note = passage.source[len(_PREFIX):]
            with self.subTest(block=note):
                out, err, rc = _run(passage.text)
                self.assertEqual(rc, 0, err)
                self.assertEqual(err.strip(), "")
                self.assertEqual(
                    out.replace("\r\n", "\n").rstrip("\n"), self.PRINTS.get(note),
                    f"python prints {out.rstrip()!r}")


def _others(*modules: tuple) -> tuple:
    out: tuple = ()
    for m in modules:
        out += m
    return out


class PygameLinesTests(_LineRules, unittest.TestCase):
    LINES = PYGAME_LINES
    OTHER = _others(PYDATA_LINES, PYSCRIPT_LINES, PYSCI_LINES)


class PygameBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = PYGAME_BLOCKS
    OTHER = _others(PYDATA_BLOCKS, PYSCRIPT_BLOCKS, PYSCI_BLOCKS)
    PRINTS = PYGAME_PRINTS

    def test_the_blocks_need_nothing_but_the_standard_library(self) -> None:
        """Positions are tuples and distances come from math; pygame and its
        Vector2 are for the lines."""
        for passage in self.BLOCKS:
            self.assertNotIn("Vector2", passage.text)
            self.assertNotIn("import pygame", passage.text)


class PydataLinesTests(_LineRules, unittest.TestCase):
    LINES = PYDATA_LINES
    OTHER = _others(PYGAME_LINES, PYSCRIPT_LINES, PYSCI_LINES)


class PydataBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = PYDATA_BLOCKS
    OTHER = _others(PYGAME_BLOCKS, PYSCRIPT_BLOCKS, PYSCI_BLOCKS)
    PRINTS = PYDATA_PRINTS
    BANNED = _BlockRules.BANNED + ("pathlib", "tempfile", "urllib", "asyncio")


class PyscriptLinesTests(_LineRules, unittest.TestCase):
    LINES = PYSCRIPT_LINES
    OTHER = _others(PYGAME_LINES, PYDATA_LINES, PYSCI_LINES)


class PyscriptBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = PYSCRIPT_BLOCKS
    OTHER = _others(PYGAME_BLOCKS, PYDATA_BLOCKS, PYSCI_BLOCKS)
    PRINTS = PYSCRIPT_PRINTS
    #: The server block is the longest, and is allowed the longest.
    MAX_LINES = 14
    #: urllib's opener has an open() method; nothing else here opens files.
    BANNED = tuple(w for w in _BlockRules.BANNED if w != "open(")

    def test_disk_work_stays_in_a_temp_folder_that_cleans_itself_up(self) -> None:
        for passage in self.BLOCKS:
            if "write_text" in passage.text or "tempfile" in passage.text:
                with self.subTest(block=passage.source):
                    self.assertIn("tempfile.TemporaryDirectory()", passage.text)

    def test_at_most_one_block_runs_a_server_on_loopback_port_zero(self) -> None:
        servers = [p for p in self.BLOCKS if "HTTPServer" in p.text]
        self.assertLessEqual(len(servers), 1)
        for passage in servers:
            self.assertIn('HTTPServer(("127.0.0.1", 0)', passage.text)
            self.assertIn("server.shutdown()", passage.text)
            self.assertIn("daemon=True", passage.text)

    def test_argparse_is_always_given_an_explicit_list(self) -> None:
        for passage in self.BLOCKS:
            self.assertNotIn("parse_args()", passage.text)


class PysciLinesTests(_LineRules, unittest.TestCase):
    LINES = PYSCI_LINES
    OTHER = _others(PYGAME_LINES, PYDATA_LINES, PYSCRIPT_LINES)


class PysciBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = PYSCI_BLOCKS
    OTHER = _others(PYGAME_BLOCKS, PYDATA_BLOCKS, PYSCRIPT_BLOCKS)
    PRINTS = PYSCI_PRINTS
    BANNED = _BlockRules.BANNED + ("pathlib", "tempfile", "urllib", "asyncio")


class RegistrationTests(unittest.TestCase):
    """Holds before the themes are registered and after, whatever ids they
    are given. A theme that serves any of a module's lines has to be Python,
    serve every one of them and every block with them, and sit under Python
    Lore with the rest of the Python code."""

    def test_a_theme_that_serves_them_serves_them_whole(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES

        for lines, blocks in _MODULES:
            texts = {p.text for p in lines}
            for theme in THEMES:
                served = {p.text for p in theme.passages}
                if not served & texts:
                    continue
                with self.subTest(theme=theme.id):
                    self.assertEqual(theme.language, "python")
                    self.assertLessEqual(texts, served)
                    self.assertLessEqual(
                        {p.text for p in blocks}, {p.text for p in theme.blocks})
                    self.assertIn(theme.id, BESIDE_LORE["python"])

    def test_registered_under_the_expected_names(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES

        by_id = {t.id: t for t in THEMES}
        for theme_id, name, (lines, blocks) in (
            ("pygame", "Python Game Code", _MODULES[0]),
            ("pydata", "Python Data Code", _MODULES[1]),
            ("pyscript", "Python Scripting Code", _MODULES[2]),
            ("pysci", "Python Science Code", _MODULES[3]),
        ):
            with self.subTest(theme=theme_id):
                theme = by_id[theme_id]
                self.assertEqual(theme.name, name)
                self.assertEqual(theme.language, "python")
                self.assertEqual(theme.passages, lines)
                self.assertEqual(theme.blocks, blocks)
                self.assertIn(theme_id, BESIDE_LORE["python"])

    def test_they_sit_after_python_code_and_keep_it(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES

        self.assertEqual(BESIDE_LORE["python"][0], "pycode")
        ids = [t.id for t in THEMES]
        at = ids.index("python")
        placed = ids[at + 1:at + 1 + len(BESIDE_LORE["python"])]
        self.assertEqual(placed, list(BESIDE_LORE["python"]))

    def test_no_other_theme_already_serves_one_of_their_lines(self) -> None:
        """The generic code sets (Useful, School and the rest) are themes
        too, and a line they already hold would be served twice to anyone
        who ticks both."""
        from code_coach.typing.drills import THEMES

        mine = {p.text for p in _ALL_LINES}
        mine_blocks = {p.text for p in _ALL_BLOCKS}
        for theme in THEMES:
            if theme.id in ("pygame", "pydata", "pyscript", "pysci"):
                continue
            with self.subTest(theme=theme.id):
                self.assertEqual({p.text for p in theme.passages} & mine, set())
                self.assertEqual({p.text for p in theme.blocks} & mine_blocks, set())

    def test_no_theme_serves_a_line_twice(self) -> None:
        from code_coach.typing.drills import THEMES_BY_ID

        for theme_id in ("pygame", "pydata", "pyscript", "pysci"):
            texts = [p.text for p in THEMES_BY_ID[theme_id].passages]
            with self.subTest(theme=theme_id):
                self.assertEqual(len(texts), len(set(texts)))


if __name__ == "__main__":
    unittest.main()
