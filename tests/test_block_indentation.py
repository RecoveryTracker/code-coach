"""
check_block must treat indentation as syntax.

Regression guard: comparing stripped text alone accepted a flat copy of a
function body, so the exercise completed and auto-advanced while the code
raised IndentationError the moment the student pressed Run.
"""

from __future__ import annotations

import unittest

from code_coach.dictation.bank import check_block

SOLUTION = (
    "def max_profit(prices):\n"
    "    best = 0\n"
    "    for price in prices:\n"
    "        best = max(best, price)\n"
    "    return best"
)


class TestBlockIndentation(unittest.TestCase):
    def test_exact_copy_passes(self):
        self.assertTrue(check_block(SOLUTION, SOLUTION))

    def test_flat_copy_is_rejected(self):
        flat = "\n".join(ln.strip() for ln in SOLUTION.splitlines())
        self.assertFalse(check_block(flat, SOLUTION))

    def test_wrong_nesting_is_rejected(self):
        # `return best` pulled inside the loop — runs, but returns too early.
        wrong = SOLUTION.replace("    return best", "        return best")
        self.assertFalse(check_block(wrong, SOLUTION))

    def test_whole_block_shifted_still_passes(self):
        """Typing the block at a different base indent is fine."""
        shifted = "\n".join("    " + ln for ln in SOLUTION.splitlines())
        self.assertTrue(check_block(shifted, SOLUTION))

    def test_single_line_ignores_leading_whitespace(self):
        self.assertTrue(check_block("      seen = {}", "seen = {}"))

    def test_block_found_among_surrounding_code(self):
        noisy = "x = 1\n" + SOLUTION + "\nprint(max_profit([1, 2]))"
        self.assertTrue(check_block(noisy, SOLUTION))

    def test_comments_and_blank_lines_ignored(self):
        spaced = (
            "def max_profit(prices):\n"
            "    # running best\n"
            "    best = 0\n"
            "\n"
            "    for price in prices:\n"
            "        best = max(best, price)\n"
            "    return best"
        )
        self.assertTrue(check_block(spaced, SOLUTION))

    def test_typo_still_rejected(self):
        self.assertFalse(check_block(SOLUTION.replace("best", "bset", 1), SOLUTION))


if __name__ == "__main__":
    unittest.main()
