"""The coach must name the one line that's wrong, not echo the whole block."""

import unittest

from code_coach.dictation.bank import check_block, first_block_mismatch
from code_coach.practice.adapt import line_diff_note

TWO_SUM = "\n".join(
    [
        "def two_sum(nums, target):",
        "    seen = {}",
        "    for i, n in enumerate(nums):",
        "        need = target - n",
        "        if need in seen:",
        "            return [seen[need], i]",
        "        seen[n] = i",
        "    return []",
    ]
)


class FirstBlockMismatchTests(unittest.TestCase):
    def test_exact_copy_has_no_mismatch(self):
        self.assertTrue(check_block(TWO_SUM, TWO_SUM))
        self.assertIsNone(first_block_mismatch(TWO_SUM, TWO_SUM))

    def test_missing_space_is_reported_on_its_own_line(self):
        # `return[]` runs fine but isn't verbatim — the drill must say which line.
        typed = TWO_SUM.replace("    return []", "    return[]")
        m = first_block_mismatch(typed, TWO_SUM)
        self.assertIsNotNone(m)
        self.assertEqual(m.lineno, 8)
        self.assertEqual(m.want, "return []")
        self.assertEqual(m.mine, "return[]")
        self.assertEqual(m.kind, "text")

    def test_wrong_indent_is_flagged_as_indent_not_text(self):
        typed = TWO_SUM.replace("        seen[n] = i", "    seen[n] = i")
        m = first_block_mismatch(typed, TWO_SUM)
        self.assertIsNotNone(m)
        self.assertEqual(m.lineno, 7)
        self.assertEqual(m.kind, "indent")
        self.assertGreater(m.want_indent, m.mine_indent)

    def test_partial_attempt_points_at_the_first_absent_line(self):
        typed = "\n".join(TWO_SUM.splitlines()[:4])
        m = first_block_mismatch(typed, TWO_SUM)
        self.assertIsNotNone(m)
        self.assertEqual(m.lineno, 5)
        self.assertEqual(m.kind, "missing")

    def test_block_found_among_surrounding_code(self):
        typed = f"x = 1\n{TWO_SUM}\nprint(x)"
        self.assertIsNone(first_block_mismatch(typed, TWO_SUM))

    def test_picks_the_closest_window_not_the_first(self):
        # A near-complete second attempt should be what gets critiqued.
        wrong_first = TWO_SUM.replace("    seen = {}", "    seen = []")
        typed = f"{wrong_first}\n\n{TWO_SUM.replace('    return []', '    return[]')}"
        m = first_block_mismatch(typed, TWO_SUM)
        self.assertEqual(m.lineno, 8)


class LineDiffNoteTests(unittest.TestCase):
    def test_note_is_short_and_names_the_line(self):
        typed = TWO_SUM.replace("    return []", "    return[]")
        note = line_diff_note(typed, TWO_SUM)
        self.assertIn("line 8", note)
        self.assertIn("return []", note)
        # The whole function must not be dumped back at the student.
        self.assertNotIn("def two_sum", note)

    def test_indent_note_explains_nesting_instead_of_showing_a_diff(self):
        typed = TWO_SUM.replace("        seen[n] = i", "    seen[n] = i")
        note = line_diff_note(typed, TWO_SUM)
        self.assertIn("indentation", note)
        # Stripped, both sides read the same, so a should/typed diff would be
        # meaningless here.
        self.assertNotIn("you typed:", note)

    def test_matching_block_produces_no_note(self):
        self.assertIsNone(line_diff_note(TWO_SUM, TWO_SUM))


if __name__ == "__main__":
    unittest.main()
