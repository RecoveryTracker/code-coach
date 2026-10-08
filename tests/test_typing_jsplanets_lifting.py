"""The JavaScript planet and bodybuilding lines and blocks obey the rules.

The guards tests/test_typing_jsgame.py puts on the game code, applied to
`snippets_jsplanets` and `snippets_jslifting` directly, so they hold
before either is registered as a theme and after: every character on the
keyboard, a note on everything, lengths inside the range the existing
JavaScript pool already uses, nothing already in that pool or in the
other module, every line parses, and every block runs in Node.

One more for the blocks, because what they print is the point of them:
each prints exactly the answer written down for it below, worked out by
hand from the block's own figures before Node was asked. A block about
Kepler's third law that printed the wrong period would still run, and
still print something, and only this would notice.
"""

from __future__ import annotations

import functools
import json
import shutil
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
from code_coach.typing.snippets import JAVASCRIPT_CODE
from code_coach.typing.snippets_js_more import (
    JAVASCRIPT_BLOCKS_MORE,
    JAVASCRIPT_LINES_MORE,
)
from code_coach.typing.snippets_jsgame import (
    JSGAME_BLOCKS,
    JSGAME_LIBRARY_LINES,
    JSGAME_LINES,
)
from code_coach.typing.snippets_jslifting import JSLIFTING_BLOCKS, JSLIFTING_LINES
from code_coach.typing.snippets_jsplanets import JSPLANETS_BLOCKS, JSPLANETS_LINES
from code_coach.typing.snippets_more import JAVASCRIPT_MORE

_PREFIX = "JavaScript · "

# Every JavaScript line and block already served somewhere. Once these
# modules are registered their own passages may turn up in a pool too,
# so they are taken out by identity before comparing.
_MINE = {
    id(p)
    for p in JSPLANETS_LINES + JSPLANETS_BLOCKS + JSLIFTING_LINES + JSLIFTING_BLOCKS
}
_POOL_LINES = code_lines_for("javascript", curated=JAVASCRIPT_CODE)
_EXISTING_LINES = [
    p for p in (
        _POOL_LINES
        + code_lines_for("typescript")
        + JAVASCRIPT_LINES_MORE
        + JAVASCRIPT_MORE
        + JSGAME_LINES
        + JSGAME_LIBRARY_LINES
    )
    if id(p) not in _MINE
]
_POOL_BLOCKS = code_blocks_for("javascript")
_EXISTING_BLOCKS = [
    p for p in _POOL_BLOCKS + JAVASCRIPT_BLOCKS_MORE + JSGAME_BLOCKS
    if id(p) not in _MINE
]

#: What each planet block prints, by its note. Worked out by hand: the
#: arithmetic is in the block, and toFixed or Math.round settles every
#: last digit, so none of this depends on how floating point rounds.
PLANET_PRINTS = {
    # 70 * 8.9 = 623, / 9.8 = 63.57; 70 * 3.7 = 259, / 9.8 = 26.43;
    # 70 * 23.1 = 1617, / 9.8 = 165 exactly.
    "weight elsewhere, as a scale set for Earth would show it":
        "Venus: 63.6 kg\nMars: 26.4 kg\nJupiter: 165.0 kg",
    # 149,597,870.7 / 299,792.458 = 499.005 s, so 499 = 8 min 19 s;
    # 228,000,000 / 299,792.458 = 760.53 s, so 761 = 12 min 41 s.
    "how long sunlight takes to arrive":
        "Sun to Earth: 8 min 19 s\nSun to Mars: 12 min 41 s",
    # 1.0000 AU -> 1.0000 years; 1.5241 AU -> 1.8815; 5.2040 -> 11.871.
    "Kepler's third law: the year from the distance":
        "Earth: 1.00 AU, 1.00 years\n"
        "Mars: 1.52 AU, 1.88 years\n"
        "Jupiter: 5.20 AU, 11.87 years",
    "a sorted copy, with the original left alone":
        "Jupiter > Earth > Mars > Mercury\nMars Mercury",
    # Columns 8, 6 and 9 wide: names hang left, numbers hang right.
    "a table in fixed columns with padEnd and padStart": "\n".join((
        "Planet  " + "     g" + "       km",
        "Mercury " + "   3.7" + "    4,879",
        "Venus   " + "   8.9" + "   12,104",
        "Earth   " + "   9.8" + "   12,756",
        "Mars    " + "   3.7" + "    6,792",
    )),
    # Step 1: a = 1, vx = -0.1, x = 0.99, y = 0.1. Step 2: r = 0.99504,
    # a = 1.0100, vx = -0.20049, vy = 0.98985, so x = 0.96995 and
    # y = 0.19898.
    "two steps of an orbit, by semi-implicit Euler": "0.970 0.199",
    # Earth: 3.98438e14 / 6.378e6 squared = 9.7947.
    # Mars: 4.28471e13 / 3.396e6 squared = 3.7152.
    "surface gravity from a planet's mass and size": "Earth 9.79\nMars 3.72",
    # -65 + 273.15 = 208.15, -110 + 273.15 = 163.15; only Venus is
    # over 400 degrees.
    "filter, map and find over mean temperatures":
        "Mars 208 K, Jupiter 163 K\nVenus",
    # 30 * 365.25 = 10957.5 days: / 88 = 124.52, / 224.7 = 48.77,
    # / 687 = 15.950 (just under), / 4331 = 2.53.
    "a thirty-year-old's age in other planets' years":
        "Mercury: 124.5\nVenus: 48.8\nMars: 15.9\nJupiter: 2.5",
    # 3.7 twice, then 8.9, 9.8 and 9 once each: four keys.
    "planets that share a gravity, grouped in a Map":
        "Mercury and Mars: 3.7 m/s^2\n4 different values",
}

#: What each bodybuilding block prints, by its note, worked out by hand.
LIFTING_PRINTS = {
    # 100 * 5 twice is 1000; 70 * 8 is 560.
    "a session's volume, per exercise and in all":
        "squat: 1000 kg\nbench: 560 kg\ntotal: 1560 kg",
    # 100 * 1.1 = 110; 3600 / 34 = 105.88; at ten reps both are 133.33.
    "Epley and Brzycki side by side":
        "3 reps at 100 kg: Epley 110.0, Brzycki 105.9\n"
        "10 reps at 100 kg: Epley 133.3, Brzycki 133.3",
    # 40 a side is 25 + 15; 61.25 a side is 25 + 25 + 10 + 1.25.
    "the plates for each side of the bar": "25 + 15\n25 + 25 + 10 + 1.25",
    "personal records kept in a Map":
        "Map(3) { 'squat' => 150, 'bench' => 100, 'deadlift' => 180 }\n"
        "total 430",
    "a rest timer's mm:ss, padded with padStart":
        "rest 01:30\nrest 03:00\nrest 00:45\nrest 10:05",
    # Protein 80 * 2 = 160 g; fat 700 / 9 = 77.8, so 78 g; carbs
    # (2800 - 640 - 702) / 4 = 364.5, which Math.round takes up to 365.
    # Back to calories: 640 + 1460 + 702 = 2802.
    "macros from a calorie target, and what rounding does to it":
        "{ protein: 160, carbs: 365, fat: 78 }\n2802 kcal",
    # 60 x 11 hits: 60 x 12. Hits at 12: 62.5 x 8. Misses: no change.
    # Hits: 62.5 x 9.
    "double progression: reps first, then weight":
        "60 kg x 12\n62.5 kg x 8\n62.5 kg x 8\n62.5 kg x 9",
    "a weekly split, counted":
        "{ push: 2, pull: 2, legs: 2, rest: 1 } 6 training days",
    # 91 / 2.5 = 36.4 -> 90; 105 is already a step; 119 / 2.5 = 47.6 -> 120.
    "working sets from a training max, rounded to 2.5 kg":
        "65%: 91 -> 90 kg\n75%: 105 -> 105 kg\n85%: 119 -> 120 kg",
    # 132.28, 220.46 and 308.65 lb; 315 / 2.20462 = 142.88 kg.
    "kilograms and pounds, both ways":
        "60 kg = 132 lb\n100 kg = 220 lb\n140 kg = 309 lb\n315 lb = 142.9 kg",
}


def _node() -> bool:
    return shutil.which("node") is not None


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    from code_coach.engine import run_code

    return run_code(code, language="javascript")


def _assert_typeable(case: unittest.TestCase, text: str) -> None:
    for char in text:
        if char == "\n":
            continue
        case.assertNotIn(char, UNTYPEABLE, text)
        case.assertIn(char, BY_CHAR, f"{char!r} in {text!r}")


class _LineRules:
    """The rules every line in one of the two modules keeps."""

    LINES: tuple = ()
    #: The other module's lines, which these must not repeat either.
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
            self.assertFalse(passage.text.startswith(("//", "/*")), passage.text)

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

    @unittest.skipUnless(_node(), "node is not installed")
    def test_every_line_parses(self) -> None:
        """Each line, as the body of an async function. A line that opens a
        block gets its closing braces added, the way it would in a file."""
        bodies = []
        for passage in self.LINES:
            text = passage.text
            opens = text.count("{") - text.count("}")
            bodies.append(text + "\n}" * max(opens, 0))
        program = (
            "const AsyncFunction = (async () => {}).constructor;\n"
            f"const bodies = {json.dumps(bodies)};\n"
            "let bad = 0;\n"
            "for (const body of bodies) {\n"
            "  try { new AsyncFunction(body); }\n"
            "  catch (e) { bad++; console.log('BAD', JSON.stringify(body), e.message); }\n"
            "}\n"
            "console.log('bad=' + bad);\n"
        )
        out, err, rc = _run(program)
        self.assertEqual(rc, 0, err)
        self.assertIn("bad=0", out, out)


class _BlockRules:
    """The rules every block in one of the two modules keeps."""

    BLOCKS: tuple = ()
    OTHER: tuple = ()
    #: What each block prints, by its note, worked out by hand.
    PRINTS: dict[str, str] = {}

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
                self.assertLessEqual(len(lines), min(MAX_BLOCK_LINES, 12))
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
                    self.assertEqual(indent % 2, 0, line)
                self.assertTrue(
                    any(ln.startswith("  ") for ln in passage.text.splitlines())
                )

    def test_no_dom_in_a_block(self) -> None:
        """They run in Node, so a page or a window would be a crash."""
        for passage in self.BLOCKS:
            for word in ("document", "window", "canvas", "ctx."):
                self.assertNotIn(word, passage.text)

    def test_nothing_reads_the_clock_the_dice_or_the_network(self) -> None:
        """The printed answer is held to a fixed one, so it must be the
        same on every run and on a machine with no connection."""
        for passage in self.BLOCKS:
            for word in ("Math.random", "Date", "performance.now", "fetch(",
                         "setTimeout", "setInterval", "process."):
                self.assertNotIn(word, passage.text)

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

    @unittest.skipUnless(_node(), "node is not installed")
    def test_every_block_runs_and_prints_what_was_worked_out(self) -> None:
        for passage in self.BLOCKS:
            note = passage.source[len(_PREFIX):]
            with self.subTest(block=note):
                out, err, rc = _run(passage.text)
                self.assertEqual(rc, 0, err)
                self.assertEqual(err.strip(), "")
                self.assertEqual(
                    out.replace("\r\n", "\n").rstrip("\n"), self.PRINTS.get(note),
                    f"node prints {out.rstrip()!r}")


class PlanetLinesTests(_LineRules, unittest.TestCase):
    LINES = JSPLANETS_LINES
    OTHER = JSLIFTING_LINES


class PlanetBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = JSPLANETS_BLOCKS
    OTHER = JSLIFTING_BLOCKS
    PRINTS = PLANET_PRINTS


class LiftingLinesTests(_LineRules, unittest.TestCase):
    LINES = JSLIFTING_LINES
    OTHER = JSPLANETS_LINES


class LiftingBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = JSLIFTING_BLOCKS
    OTHER = JSPLANETS_BLOCKS
    PRINTS = LIFTING_PRINTS


class RegistrationTests(unittest.TestCase):
    """Holds before the themes are registered and after, whatever ids
    they are given. A theme that serves any of a module's lines has to be
    JavaScript, serve every one of them and every block with them, and
    sit under JavaScript Lore with the rest of the JavaScript code."""

    def test_a_theme_that_serves_them_serves_them_whole(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES

        for lines, blocks in ((JSPLANETS_LINES, JSPLANETS_BLOCKS),
                              (JSLIFTING_LINES, JSLIFTING_BLOCKS)):
            texts = {p.text for p in lines}
            for theme in THEMES:
                served = {p.text for p in theme.passages}
                if not served & texts:
                    continue
                with self.subTest(theme=theme.id):
                    self.assertEqual(theme.language, "javascript")
                    self.assertLessEqual(texts, served)
                    self.assertLessEqual(
                        {p.text for p in blocks}, {p.text for p in theme.blocks})
                    self.assertIn(theme.id, BESIDE_LORE["javascript"])


if __name__ == "__main__":
    unittest.main()
