"""The JavaScript Node, music and cooking lines and blocks obey the rules.

The guards tests/test_typing_jsgame.py puts on the game code, applied to
`snippets_jsnode`, `snippets_jsmusic` and `snippets_jscooking` directly, so
they hold before any is registered as a theme and after: every character
on the keyboard, a note on everything, lengths inside the range the
existing JavaScript pool already uses, nothing already in that pool or in
the other modules, every line parses, and every block runs in Node.

One more for the blocks, because what they print is the point of them:
each prints exactly the answer written down for it below, worked out by
hand from the block's own figures before Node was asked.

The Node blocks are allowed what the other themes' blocks are not:
process, because they read process.argv and process.env, and fetch, for
the one that asks its own local server a question. They are still held to
no clock and no dice, and the ones that touch the disk or the network are
kept deterministic (a mkdtemp folder removed afterwards; 127.0.0.1, port 0).
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
from code_coach.typing.snippets_jscooking import JSCOOKING_BLOCKS, JSCOOKING_LINES
from code_coach.typing.snippets_jsgame import (
    JSGAME_BLOCKS,
    JSGAME_LIBRARY_LINES,
    JSGAME_LINES,
)
from code_coach.typing.snippets_jslifting import JSLIFTING_BLOCKS, JSLIFTING_LINES
from code_coach.typing.snippets_jsmusic import JSMUSIC_BLOCKS, JSMUSIC_LINES
from code_coach.typing.snippets_jsnode import JSNODE_BLOCKS, JSNODE_LINES
from code_coach.typing.snippets_jsplanets import JSPLANETS_BLOCKS, JSPLANETS_LINES
from code_coach.typing.snippets_more import JAVASCRIPT_MORE

_PREFIX = "JavaScript · "

_ALL_LINES = (
    JSNODE_LINES + JSMUSIC_LINES + JSCOOKING_LINES
)
_ALL_BLOCKS = JSNODE_BLOCKS + JSMUSIC_BLOCKS + JSCOOKING_BLOCKS
_SIBLINGS = JSPLANETS_LINES + JSLIFTING_LINES
_SIBLING_BLOCKS = JSPLANETS_BLOCKS + JSLIFTING_BLOCKS

# Every JavaScript line and block already served somewhere. Once these
# modules are registered their own passages may turn up in a pool too,
# so they are taken out by identity before comparing.
_MINE = {id(p) for p in _ALL_LINES + _ALL_BLOCKS + _SIBLINGS + _SIBLING_BLOCKS}
_POOL_LINES = code_lines_for("javascript", curated=JAVASCRIPT_CODE)
_EXISTING_LINES = [
    p for p in (
        _POOL_LINES
        + code_lines_for("typescript")
        + JAVASCRIPT_LINES_MORE
        + JAVASCRIPT_MORE
        + JSGAME_LINES
        + JSGAME_LIBRARY_LINES
        + _SIBLINGS
    )
    if id(p) not in {id(q) for q in _ALL_LINES}
]
_POOL_BLOCKS = code_blocks_for("javascript")
_EXISTING_BLOCKS = [
    p for p in (_POOL_BLOCKS + JAVASCRIPT_BLOCKS_MORE + JSGAME_BLOCKS + _SIBLING_BLOCKS)
    if id(p) not in {id(q) for q in _ALL_BLOCKS}
]


def _table(rows: list[tuple[str, ...]]) -> str:
    return "\n".join("".join(r) for r in rows)


#: What each Node block prints, by its note. Worked out by hand.
NODE_PRINTS = {
    # basename keeps the extension; with '.mp3' it is taken off. dirname
    # is everything before the last slash. join climbs out of b: /a/c/d.txt.
    # parse().name is the base without its last extension.
    "taking a path apart with path.posix":
        "demo.final.mp3 .mp3\n"
        "demo.final /home/ann/music\n"
        "/a/c/d.txt\n"
        "demo.final",
    # 3000 + 1; debug stays false; the pretty file has { , two lines, }.
    "JSON saved to disk and read back": "3001 false\n4",
    # b.txt and c.txt sort to b first; four files were written.
    "listing a folder and filtering by extension": "b.txt,c.txt 4",
    # First emit: early, first, once. Second: once is gone. Two left,
    # and an event nobody listens to returns false.
    "listener order, once and prependListener":
        "early 1 | first 1 | once 1 | early 2 | first 2\n2 false",
    # No arguments were given, so 0; 8080 + 1; no such name set.
    "arguments and environment variables with defaults":
        "0 8081 hello world\nfalse",
    "parsing a command line with util.parseArgs":
        "true 4001\n[ 'input.txt', 'out.txt' ]",
    # 3 + 5 + 0 (fig is NaN, which || turns into 0).
    "readline over a stream, adding up the numbers": "total 8",
    "a pipeline of a source, a transform and a sink": "AB-CD",
    # 'one\ntwo\n' is 8 bytes.
    "fs/promises: write, append, read and measure": "[ 'one', 'two' ] 8",
    "a server that answers its own fetch": "{ msg: 'hi', method: 'GET' } 404 nope",
}

#: What each music block prints, by its note. Worked out by hand.
MUSIC_PRINTS = {
    # 60000 / 90 = 666.67, x 4 = 2666.7; 60000 / 140 = 428.57, x 4 = 1714.3;
    # 60000 / 174 = 344.83, x 4 = 1379.3.
    "tempo turned into milliseconds": "\n".join((
        "60 bpm: 1000.0 ms, bar 4000 ms",
        "90 bpm: 666.7 ms, bar 2667 ms",
        "120 bpm: 500.0 ms, bar 2000 ms",
        "140 bpm: 428.6 ms, bar 1714 ms",
        "174 bpm: 344.8 ms, bar 1379 ms",
    )),
    # 21 = 9 + 12 * 1: A in octave 0. C#3 = 1 + 4 * 12 = 49.
    "MIDI numbers to note names and back": "C4 C#4 A4 C5 A0\n69 49 0",
    # 440 * 2 ** (-9 / 12) = 261.63; 2 ** (-33 / 12) * 440 = 65.41.
    "equal-tempered frequencies, and the way back":
        "A4 440.00 Hz\nC4 261.63 Hz\nA5 880.00 Hz\nC2 65.41 Hz\n60",
    # 0: C E G B. -5: 55 59 62 66 = G B D F#. 14: 74 78 81 85 = D F# A C#.
    "transposing a melody with a remainder that handles negatives":
        "C E G B\nG B D F#\nD F# A C#\n11 -1",
    # A minor from 9: A B C D E F G. G pentatonic: G A# C D F.
    "scales as arrays of intervals, in any key":
        "C D E F G A B\nA B C D E F G\nG A# C D F",
    # 20 log10 2 = 6.02; 10 ** (-6 / 20) = 0.501; 10 ** -1 = 0.1;
    # 10 ** (6 / 20) = 1.995; the peak 0.5 is -6.02 dBFS.
    "decibels and gain, in both directions":
        "6.02 -6.02 20\n0.501 0.1 1.995\npeak -6.02 dBFS",
    # 0.5 * 44100; 0.6667 * 44100; 140 -> 18900; 128 -> 20671.875;
    # 44100 * 2 * 16 / 8 = 176400.
    "samples per beat at CD rate":
        "22050 29400\n18900 20671.88\n22050 11025\n176400 bytes per second",
    # Step is 125 ms. Kick on 0 4 8 12; snare on 4 12; hat on every other.
    "a step sequencer's pattern turned into times":
        "kick  4 0,500,1000\nsnare 2 500,1500\nhat   8 0,250,500",
    # 0.02 -> 0; 0.27 -> 0.25; 0.49 -> 0.5; 0.62 -> 0.5; 0.88 -> 1;
    # 1.13 -> 1.25. Worst miss 0.12. Ties round up: 1 2 3, and -0.5 -> -0.
    "quantizing played notes to a grid":
        "0 0.25 0.5 0.5 1 1.25\n0.12\n1 2 3 -0",
    # Sorted by tempo: Pad 90, Lead 100, Kick 128. Gains: -12 dB 0.25,
    # -6 dB 0.50, -3 dB 0.71. Names 6 wide, tempos 4, gains 7.
    "a mixer table sorted by tempo and lined up": _table([
        ("Pad".ljust(6), "90".rjust(4), "0.25".rjust(7)),
        ("Lead".ljust(6), "100".rjust(4), "0.50".rjust(7)),
        ("Kick".ljust(6), "128".rjust(4), "0.71".rjust(7)),
    ]),
}

#: What each cooking block prints, by its note. Worked out by hand.
COOKING_PRINTS = {
    # k = 1.5: 375, 450, 3 eggs, 0.75 tsp. For 3 servings k = 0.75, so
    # 1.5 eggs, which rounds up to 2.
    "scaling a recipe to a different number of servings":
        "{ servings: 6, flourG: 375, milkMl: 450, eggs: 3, saltTsp: 0.75 }\n1.5 2",
    # 1.5 cups = 354.9 ml; 3 tsp = 14.787 ml; 8 oz = 226.8 g; 500 g = 17.64 oz.
    "kitchen unit conversions from one table": "355 14.8\n227 17.64",
    # 121.1, 176.7, 218.3, 246.1 degrees C. 180 C = 356 F; 212 F = 100 C.
    "oven temperatures in both scales":
        "250F = 121C\n350F = 177C\n425F = 218C\n475F = 246C\n356 -40 100",
    # 40 + 20 = 60; 72 + 20 = 92; 100 + 20 = 120; 168 + 20 = 188.
    "a roasting time as hours and minutes":
        "1 kg 1 h\n1.8 kg 1 h 32 min\n2.5 kg 2 h\n4.2 kg 3 h 8 min",
    # 19:30 is minute 1170. Minus 15, 105, 135: 1155, 1065, 1035. Minus
    # 60 from half past midnight wraps to 23:00.
    "a timeline counted back from dinner, with a wrap past midnight":
        "19:30 serve\n19:15 rest\n17:45 roast\n17:15 preheat\n23:00",
    # flour 200 + 125, milk 300 + 50 + 250, egg 2 + 3 + 1, in order seen.
    "one shopping list merged from three recipes":
        "Map(3) { 'flour' => 325, 'milk' => 600, 'egg' => 6 }\n"
        "flour, milk, egg 6",
    # rice 2.4 * 300 / 1000 = 0.72; chicken 7.4 * 450 / 1000 = 3.33;
    # peas 1.8 * 100 / 500 = 0.36. Total 4.41, a quarter is 1.1025.
    "what a dish costs, and what one serving costs":
        "0.72 3.33 0.36\n4.41 1.10",
    # 2.49 x 2 = 4.98; 3.99; 4.75 x 3 = 14.25; total 23.22.
    "a receipt with Intl.NumberFormat currency": _table([
        ("flour".ljust(8), "2x ", "$4.98".rjust(8)),
        ("eggs".ljust(8), "1x ", "$3.99".rjust(8)),
        ("butter".ljust(8), "3x ", "$14.25".rjust(8)),
        ("total".ljust(8), "   ", "$23.22".rjust(8)),
    ]),
    # Vegetarian and at most 45 minutes: Salad, Curry, Risotto. By time:
    # 10, 35, 45, 180. Something over 120: yes. Everything over 10: no.
    "filtering, sorting and testing a list of recipes":
        "Salad, Curry, Risotto\n"
        "Salad 10m < Risotto 35m < Curry 45m < Ragu 180m\n"
        "true false",
    # 32 * 4 + 45 * 4 + 14 * 9 = 128 + 180 + 126 = 434; fat is 126 / 434 =
    # 29%. Six batches are 2604 kcal, over four is 651; 2000 / 3 = 667.
    "calories from the macros, and a big batch shared out":
        "434 29% from fat\n651 667",
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
    """The rules every block in one of the modules keeps."""

    BLOCKS: tuple = ()
    OTHER: tuple = ()
    #: What each block prints, by its note, worked out by hand.
    PRINTS: dict[str, str] = {}
    #: Words a block of this theme may not use.
    BANNED = ("Math.random", "Date", "performance.now", "setTimeout",
              "setInterval")

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

    def test_no_dom_in_a_block(self) -> None:
        """They run in Node, so a page or a window would be a crash."""
        for passage in self.BLOCKS:
            for word in ("document", "window", "canvas", "ctx."):
                self.assertNotIn(word, passage.text)

    def test_nothing_reads_the_clock_or_the_dice(self) -> None:
        """The printed answer is held to a fixed one, so it must be the
        same on every run."""
        for passage in self.BLOCKS:
            for word in self.BANNED:
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


def _others(*modules: tuple) -> tuple:
    out: tuple = ()
    for m in modules:
        out += m
    return out


class NodeLinesTests(_LineRules, unittest.TestCase):
    LINES = JSNODE_LINES
    OTHER = _others(JSMUSIC_LINES, JSCOOKING_LINES)


class NodeBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = JSNODE_BLOCKS
    OTHER = _others(JSMUSIC_BLOCKS, JSCOOKING_BLOCKS)
    PRINTS = NODE_PRINTS

    def test_disk_work_stays_in_a_temp_folder_and_is_cleaned_up(self) -> None:
        for passage in self.BLOCKS:
            if "writeFile" in passage.text or "mkdtemp" in passage.text:
                with self.subTest(block=passage.source):
                    self.assertIn("os.tmpdir()", passage.text)
                    self.assertIn("mkdtemp", passage.text)
                    self.assertIn("rm", passage.text)

    def test_the_server_listens_on_loopback_port_zero_and_closes(self) -> None:
        for passage in self.BLOCKS:
            if "createServer" in passage.text:
                with self.subTest(block=passage.source):
                    self.assertIn("listen(0, '127.0.0.1'", passage.text)
                    self.assertIn("server.close()", passage.text)


class MusicLinesTests(_LineRules, unittest.TestCase):
    LINES = JSMUSIC_LINES
    OTHER = _others(JSNODE_LINES, JSCOOKING_LINES)


class MusicBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = JSMUSIC_BLOCKS
    OTHER = _others(JSNODE_BLOCKS, JSCOOKING_BLOCKS)
    PRINTS = MUSIC_PRINTS
    BANNED = _BlockRules.BANNED + ("fetch(", "process.", "AudioContext")


class CookingLinesTests(_LineRules, unittest.TestCase):
    LINES = JSCOOKING_LINES
    OTHER = _others(JSNODE_LINES, JSMUSIC_LINES)


class CookingBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = JSCOOKING_BLOCKS
    OTHER = _others(JSNODE_BLOCKS, JSMUSIC_BLOCKS)
    PRINTS = COOKING_PRINTS
    BANNED = _BlockRules.BANNED + ("fetch(", "process.")


class RegistrationTests(unittest.TestCase):
    """Holds before the themes are registered and after, whatever ids
    they are given. A theme that serves any of a module's lines has to be
    JavaScript, serve every one of them and every block with them, and
    sit under JavaScript Lore with the rest of the JavaScript code."""

    def test_a_theme_that_serves_them_serves_them_whole(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES

        for lines, blocks in ((JSNODE_LINES, JSNODE_BLOCKS),
                              (JSMUSIC_LINES, JSMUSIC_BLOCKS),
                              (JSCOOKING_LINES, JSCOOKING_BLOCKS)):
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

    def test_registered_under_the_expected_names(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES

        by_id = {t.id: t for t in THEMES}
        for theme_id, name in (("jsnode", "JavaScript Node Code"),
                               ("jsmusic", "JavaScript Music Code"),
                               ("jscooking", "JavaScript Kitchen Code")):
            with self.subTest(theme=theme_id):
                self.assertEqual(by_id[theme_id].name, name)
                self.assertIn(theme_id, BESIDE_LORE["javascript"])


if __name__ == "__main__":
    unittest.main()
