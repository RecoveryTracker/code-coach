"""The extra JavaScript lines and blocks obey the typing rules, and run.

The same guards `test_typing` puts on every served target, applied to
`snippets_js_more` directly so they hold before it is registered: every
character on the keyboard, a note on everything, lengths inside the range
the existing JavaScript pool already uses, nothing already in that pool,
every line parses, and every block runs in Node.
"""

from __future__ import annotations

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

_EXISTING_LINES = code_lines_for("javascript", curated=JAVASCRIPT_CODE)
_EXISTING_BLOCKS = code_blocks_for("javascript")

# Blocks that only define something get a call here, so running them
# proves the function works and not only that it parses.
_HARNESS = {
    "async function getJson(url) {": (
        "\nglobalThis.fetch = async (url) => url === 'ok'\n"
        "  ? { ok: true, status: 200, json: async () => ({ hi: 1 }) }\n"
        "  : { ok: false, status: 404 };\n"
        "getJson('ok').then((d) => console.log(d));\n"
        "getJson('missing').then((d) => console.log(d));\n"
    ),
}


def _node() -> bool:
    return shutil.which("node") is not None


class JavaScriptMoreLinesTests(unittest.TestCase):
    def test_there_are_enough(self) -> None:
        self.assertGreaterEqual(len(JAVASCRIPT_LINES_MORE), 55)

    def test_every_character_is_on_the_keyboard(self) -> None:
        for passage in JAVASCRIPT_LINES_MORE:
            for char in passage.text:
                self.assertNotIn(char, UNTYPEABLE, passage.text)
                self.assertIn(char, BY_CHAR, f"{char!r} in {passage.text!r}")

    def test_single_lines_without_stray_whitespace(self) -> None:
        for passage in JAVASCRIPT_LINES_MORE:
            self.assertNotIn("\n", passage.text)
            self.assertNotIn("\t", passage.text)
            self.assertEqual(passage.text, passage.text.strip())

    def test_every_line_says_what_it_does(self) -> None:
        for passage in JAVASCRIPT_LINES_MORE:
            self.assertTrue(passage.source.strip(), passage.text)
            for char in passage.source:
                self.assertNotIn(char, UNTYPEABLE, passage.source)

    def test_lengths_sit_inside_the_existing_range(self) -> None:
        lengths = [len(p.text) for p in _EXISTING_LINES]
        high = max(lengths)
        # 15 is what Perfect mode asks of a target; MIN_LENGTH is the
        # curriculum's own floor.
        low = max(MIN_LENGTH, 15)
        for passage in JAVASCRIPT_LINES_MORE:
            self.assertGreaterEqual(len(passage.text), low, passage.text)
            self.assertLessEqual(len(passage.text), high, passage.text)

    def test_no_duplicates_here_or_against_the_existing_pool(self) -> None:
        texts = [p.text for p in JAVASCRIPT_LINES_MORE]
        self.assertEqual(len(texts), len(set(texts)))
        # Everything else in the pool - these lines are in it too, once
        # registered, so they are taken out before comparing.
        mine = {id(p) for p in JAVASCRIPT_LINES_MORE}
        existing = [p.text for p in _EXISTING_LINES if id(p) not in mine]
        self.assertEqual(set(existing) & set(texts), set())

    @unittest.skipUnless(_node(), "node is not installed")
    def test_every_line_parses(self) -> None:
        """Each line, as the body of an async function. A line that opens a
        block gets its closing braces added, the way it would in a file."""
        from code_coach.engine import run_code

        bodies = []
        for passage in JAVASCRIPT_LINES_MORE:
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
        out, err, rc = run_code(program, language="javascript")
        self.assertEqual(rc, 0, err)
        self.assertIn("bad=0", out, out)


class JavaScriptMoreBlocksTests(unittest.TestCase):
    def test_there_are_enough(self) -> None:
        self.assertGreaterEqual(len(JAVASCRIPT_BLOCKS_MORE), 15)

    def test_every_character_is_on_the_keyboard(self) -> None:
        for passage in JAVASCRIPT_BLOCKS_MORE:
            for char in passage.text:
                if char == "\n":
                    continue
                self.assertNotIn(char, UNTYPEABLE, passage.text)
                self.assertIn(char, BY_CHAR, f"{char!r} in {passage.text!r}")

    def test_a_length_a_person_will_finish(self) -> None:
        width = max(
            len(ln) for b in _EXISTING_BLOCKS for ln in b.text.splitlines()
        )
        for passage in JAVASCRIPT_BLOCKS_MORE:
            lines = [ln for ln in passage.text.splitlines() if ln.strip()]
            with self.subTest(block=passage.text[:30]):
                self.assertGreaterEqual(len(lines), max(MIN_BLOCK_LINES, 4))
                self.assertLessEqual(len(lines), min(MAX_BLOCK_LINES, 12))
                for line in passage.text.splitlines():
                    self.assertLessEqual(len(line), width, line)

    def test_tidy_and_really_indented(self) -> None:
        for passage in JAVASCRIPT_BLOCKS_MORE:
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

    def test_every_note_names_the_language(self) -> None:
        for passage in JAVASCRIPT_BLOCKS_MORE:
            self.assertTrue(passage.source.startswith("JavaScript · "))
            self.assertTrue(passage.source[len("JavaScript · "):].strip())

    def test_no_duplicates_here_or_against_the_existing_blocks(self) -> None:
        texts = [p.text for p in JAVASCRIPT_BLOCKS_MORE]
        self.assertEqual(len(texts), len(set(texts)))
        existing = {p.text for p in _EXISTING_BLOCKS}
        self.assertEqual(existing & set(texts), set())

    @unittest.skipUnless(_node(), "node is not installed")
    def test_every_block_runs_in_node(self) -> None:
        from code_coach.engine import run_code

        for passage in JAVASCRIPT_BLOCKS_MORE:
            first = passage.text.splitlines()[0]
            code = passage.text + "\n" + _HARNESS.get(first, "")
            with self.subTest(block=first):
                out, err, rc = run_code(code, language="javascript")
                self.assertEqual(rc, 0, err)
                self.assertTrue(out.strip(), f"no output from {first}")


if __name__ == "__main__":
    unittest.main()
