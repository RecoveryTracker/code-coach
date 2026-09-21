"""The line describer, held to the one rule that makes it safe to ship.

A caption under a line of code is read by somebody who cannot yet tell
whether it is true. That is the whole point of the feature and also the
whole risk in it, so the tests here are about honesty rather than
coverage: a describer that says nothing is fine, and a describer that
says something wrong is not.

The rule, stated so a machine can check it: every word in a description
that is not plain English came out of the line being described. If a
rule ever invents an identifier, paraphrases an expression, or guesses
at what a variable holds, that word will not be in the line and this
fails.

The English vocabulary below is written out by hand on purpose. Deriving
it from the module would make this a test that reads the code and then
agrees with it, which is the tautology this project keeps catching
itself writing. Adding a rule with new wording means adding the words
here, which is a thirty-second job that forces somebody to look at the
new phrasing once.
"""

from __future__ import annotations

import re
import unittest

from code_coach.typing.drills import THEMES_BY_ID
from code_coach.typing.line_notes import describe, note_for


#: Every pool the describer claims to handle. Adding a language here
#: is how a new describer gets held to the same rule as the old ones -
#: which is the whole reason this is a list rather than two literals
#: repeated in each test.
POOLS = (
    ("pycode", "python"),
    ("jscode", "javascript"),
    ("assemblycode", "assembly"),
)

#: Every English word the descriptions are allowed to use.
ALLOWED = {
    "a", "about", "add", "afterwards", "again", "all", "and", "anything",
    "as", "asked", "at", "back", "be", "branch", "bring", "build", "built",
    "but", "by", "close", "cleanup", "count", "deliberately", "do", "does",
    "done", "each", "end", "every", "failed", "file", "for", "from", "gets",
    "give", "given", "go", "going", "hand", "happens", "how", "imports",
    "in", "index", "into", "is", "it", "item", "items", "its", "just",
    "keep", "key", "keeps", "last", "leave", "list", "loop", "matched",
    "meaning", "name", "new", "next", "none", "nothing", "of", "off", "on",
    "one", "only", "open", "or", "order", "otherwise", "out", "over",
    "pairs", "part", "pass", "put", "reason", "record", "report", "rest",
    "runs", "same", "says", "set", "show", "signature", "skip", "sort",
    "start", "step", "stop", "store", "taken", "takes", "test", "that",
    "the", "their", "them", "there", "thing", "this", "through", "to",
    "together", "turn", "type", "under", "up", "value", "wait", "walk",
    "well", "what", "when", "whether", "which", "while", "whoever", "with",
    "worked", "would", "you", "your", "side", "something", "nothing",
    "block", "allowed", "fail", "failed", "offer", "pull", "name", "names",
    "reported", "counting", "got", "not", "no", "onto", "take", "these",
    # Added when the x86 describer arrived. Every one was checked to be
    # ordinary English rather than an identifier smuggled in - that
    # check is the reason this list is edited by hand.
    "across", "address", "after", "against", "also", "answer", "are",
    "bit", "bits", "bytes", "called", "compare", "comparison", "counter",
    "defined", "divide", "divides", "down", "else", "equal", "everything",
    "filled", "first", "fit", "flag", "flags", "flip", "frame", "goes",
    "greater", "if", "instruction", "jump", "keeping", "kernel", "lay",
    "leaving", "left", "less", "let", "linker", "multiply", "named",
    "needs", "older", "own", "pad", "popping", "program", "reserve",
    "right", "room", "run", "s", "save", "see", "setting", "shift",
    "short", "sign", "signed", "somewhere", "stack", "time", "top",
    "undo", "until", "was", "way", "we", "where", "widen", "widened",
    "work", "zero",
}

#: Words that carry meaning and must therefore come from the line.
#: Anything matching this that is not in ALLOWED has to be in the code.
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _borrowed_words(description: str) -> list[str]:
    """The words in a description that claim to be code."""
    return [
        word for word in _WORD.findall(description)
        if word.lower() not in ALLOWED
    ]


class DescriberHonestyTests(unittest.TestCase):

    def _pool(self, theme_id: str):
        return THEMES_BY_ID[theme_id].passages

    def test_every_described_word_came_from_the_line(self) -> None:
        """The rule the whole feature rests on, checked against every
        line in both curricula rather than against examples."""
        for theme_id, language in POOLS:
            for passage in self._pool(theme_id):
                described = describe(passage.text, language)
                if described is None:
                    continue
                for word in _borrowed_words(described):
                    with self.subTest(line=passage.text, word=word):
                        self.assertIn(
                            word, passage.text,
                            f"{described!r} says {word!r}, which is not in "
                            f"the line it describes",
                        )

    def test_a_description_is_one_readable_line(self) -> None:
        for theme_id, language in POOLS:
            for passage in self._pool(theme_id):
                described = describe(passage.text, language)
                if described is None:
                    continue
                with self.subTest(line=passage.text):
                    self.assertNotIn("\n", described)
                    self.assertTrue(described.strip())
                    self.assertEqual(described, described.strip())

    def test_silence_is_an_answer(self) -> None:
        """Refusing to describe is the behaviour that makes the rest
        safe, so it has to keep working."""
        for line in ("", "   ", "}", "});", ")", "],", ";"):
            with self.subTest(line=line):
                self.assertIsNone(describe(line, "python"))
                self.assertIsNone(describe(line, "javascript"))

    def test_a_language_with_no_rules_gets_no_captions(self) -> None:
        """Rather than running the Python rules over Rust and producing
        something that reads plausibly and is not true."""
        for language in ("rust", "haskell", "sql", "", "PYTHON"):
            with self.subTest(language=language):
                self.assertIsNone(describe("let x = 1;", language))

    def test_multiline_input_is_refused(self) -> None:
        self.assertIsNone(describe("def f():\n    return 1", "python"))


class DescriberUsefulnessTests(unittest.TestCase):
    """Honest and useless is still useless, so: a floor on coverage.

    The floor is well under what the rules manage today. It is here to
    catch a change that quietly breaks a whole family of rules, not to
    pin the current number - pinning the number would mean this test
    fails every time somebody adds material, which teaches people to
    edit the test without reading it.
    """

    def test_most_curriculum_lines_get_a_caption(self) -> None:
        for theme_id, language in POOLS:
            passages = THEMES_BY_ID[theme_id].passages
            described = sum(
                1 for p in passages if describe(p.text, language)
            )
            with self.subTest(theme=theme_id):
                self.assertGreater(described / len(passages), 0.6)

    def test_the_shapes_a_beginner_meets_first_are_all_covered(self) -> None:
        """Not a sample of the pool: the specific shapes that appear in
        every program, which are the ones somebody typing their first
        solutions will see most."""
        for line in (
            "for item in items:",
            "for i in range(10):",
            "for i, item in enumerate(items):",
            "while left < right:",
            "if total > best:",
            "else:",
            "def solve(nums):",
            "return total",
            "break",
            "continue",
            "total += 1",
            "out.append(value)",
        ):
            with self.subTest(line=line):
                self.assertIsNotNone(describe(line, "python"), line)

    def test_the_caption_says_something_the_problem_name_does_not(self) -> None:
        """Two lines from one solution share a source and must not share
        a note, which was the complaint that prompted the feature."""
        first = note_for("for ch in text:", "python", "#394 Decode String")
        second = note_for("return out", "python", "#394 Decode String")
        self.assertNotEqual(first, second)
        self.assertIn("#394 Decode String", first)
        self.assertIn("#394 Decode String", second)


class NoteAssemblyTests(unittest.TestCase):

    def test_an_undescribed_line_keeps_the_note_it_had(self) -> None:
        source = "#84 Largest Rectangle in Histogram"
        self.assertEqual(note_for("}", "python", source), source)
        self.assertEqual(note_for("x", "rust", source), source)

    def test_a_described_line_shows_both(self) -> None:
        note = note_for("return total", "python", "#1 Two Sum")
        self.assertIn("total", note)
        self.assertIn("#1 Two Sum", note)

    def test_a_description_with_no_source_stands_alone(self) -> None:
        note = note_for("return total", "python", "")
        self.assertTrue(note)
        self.assertNotIn("·", note)


if __name__ == "__main__":
    unittest.main()
