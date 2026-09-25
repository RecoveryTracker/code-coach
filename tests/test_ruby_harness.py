"""The Ruby kata driver: every way a Ruby answer can go, marked correctly.

Runs real Ruby, and skips on a machine without it.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.kata import Kata, judge
from code_coach.kata import ruby_harness as rh


def _ruby_runs() -> bool:
    try:
        return run_code("puts 6 * 7", language="ruby")[0].strip() == "42"
    except Exception:  # noqa: BLE001 - no Ruby is a skip, not a failure
        return False


HAS_RUBY = _ruby_runs()
NEEDS_RUBY = "needs Ruby"

UNIQUE = Kata(id="rb-unique", name="unique_of", brief="", params=("items",),
              cases=(([1, 2, 1],), ([],), (["a", "b", "a"],)),
              solve=lambda items: list(dict.fromkeys(items)), language="ruby")


def _run(code: str):
    out, err, code_ = run_code(rh.harness(UNIQUE, code), language="ruby")
    return judge(UNIQUE, out, rh.tidy(err), code_)


class SignatureTests(unittest.TestCase):

    def test_the_box_opens_on_a_ruby_def(self) -> None:
        self.assertEqual(rh.signature(UNIQUE), "def unique_of(items)")

    def test_tidy_takes_the_temporary_file_out(self) -> None:
        err = ("C:/Temp/tmpab12.rb:3:in 'unique_of': undefined method 'nope' (NoMethodError)\n"
               "\tfrom C:/Temp/tmpab12.rb:9:in 'block in <main>'")
        self.assertEqual(rh.tidy(err),
                         "Line 3: in 'unique_of': undefined method 'nope' (NoMethodError)")


@unittest.skipUnless(HAS_RUBY, NEEDS_RUBY)
class MarkingTests(unittest.TestCase):

    def test_a_right_answer_passes(self) -> None:
        self.assertTrue(_run("def unique_of(items)\n  items.uniq\nend").passed)

    def test_a_wrong_answer_names_the_inputs(self) -> None:
        outcome = _run("def unique_of(items)\n  items\nend")
        self.assertEqual([r.args for r in outcome.results if not r.passed],
                         [([1, 2, 1],), (["a", "b", "a"],)])

    def test_changing_what_it_was_given_fails(self) -> None:
        outcome = _run("def unique_of(items)\n  items.uniq!\n  items\nend")
        self.assertFalse(outcome.passed)
        self.assertTrue(any(r.changed for r in outcome.results))

    def test_a_missing_method_is_named(self) -> None:
        self.assertIn("no function called unique_of",
                      _run("def uniq_of(items)\n  items.uniq\nend").broke)

    def test_an_exception_is_reported_against_its_own_case(self) -> None:
        outcome = _run("def unique_of(items)\n  items.fetch(5)\nend")
        self.assertEqual(outcome.broke, "")
        self.assertTrue(all("IndexError" in r.error for r in outcome.results))

    def test_a_syntax_error_names_a_line_and_not_the_file(self) -> None:
        broke = _run("def unique_of(items)\n  items.uniq(\nend").broke
        self.assertIn("Line ", broke)
        self.assertNotIn(".rb", broke)


if __name__ == "__main__":
    unittest.main()
