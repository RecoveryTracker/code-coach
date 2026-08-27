"""Every Rust solution is compiled and run against real cases.

The source executed is the exact string the student is asked to type — read
straight out of the bank, not a copy kept alongside it. A copy is how a
solution stops being the one that was verified.

One rustc invocation per pattern rather than per problem: the preamble, all
eight solutions, and a block of assertions go into a single program, so the
cost is a handful of compiles rather than a hundred.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.engine import run_code
from code_coach.leetcode.problems_rust import PARTIAL

PATTERNS_BY_ID = {p.id: p for p in PARTIAL}

HAS_RUSTC = shutil.which("rustc") is not None

# Assertions per pattern. Written against the real problem statements rather
# than against whatever the code happens to do, so a plausible-but-wrong
# solution fails here instead of passing quietly.
CHECKS = {
    "lc-hashmap": """
        assert_eq!(two_sum(vec![2, 7, 11, 15], 9), vec![0, 1]);
        assert_eq!(two_sum(vec![3, 2, 4], 6), vec![1, 2]);
        assert_eq!(two_sum(vec![1, 2], 99), Vec::<i32>::new());
        assert!(contains_duplicate(vec![1, 2, 3, 1]));
        assert!(!contains_duplicate(vec![1, 2, 3]));
        assert!(is_anagram("anagram".to_string(), "nagaram".to_string()));
        assert!(!is_anagram("rat".to_string(), "car".to_string()));
        assert!(!is_anagram("a".to_string(), "ab".to_string()));
        let mut groups = group_anagrams(
            vec!["eat", "tea", "tan", "ate", "nat", "bat"]
                .into_iter()
                .map(String::from)
                .collect(),
        );
        for g in groups.iter_mut() {
            g.sort();
        }
        groups.sort();
        assert_eq!(groups.len(), 3);
        assert!(groups.contains(&vec![
            "ate".to_string(),
            "eat".to_string(),
            "tea".to_string()
        ]));
        assert_eq!(
            four_sum_count(vec![1, 2], vec![-2, -1], vec![-1, 2], vec![0, 2]),
            2
        );
        assert_eq!(subarray_sum(vec![1, 1, 1], 2), 2);
        assert_eq!(subarray_sum(vec![1, 2, 3], 3), 2);
        assert_eq!(longest_consecutive(vec![100, 4, 200, 1, 3, 2]), 4);
        assert_eq!(longest_consecutive(vec![]), 0);
        let mut board = vec![vec!['.'; 9]; 9];
        assert!(is_valid_sudoku(board.clone()));
        board[0][0] = '5';
        board[0][1] = '5';
        assert!(!is_valid_sudoku(board.clone()));
        board[0][1] = '.';
        board[1][0] = '5';
        assert!(!is_valid_sudoku(board.clone()));
        board[1][0] = '.';
        board[1][1] = '5';
        assert!(!is_valid_sudoku(board));
    """,
    "lc-two-pointers": """
        assert!(is_palindrome("A man, a plan, a canal: Panama".to_string()));
        assert!(!is_palindrome("race a car".to_string()));
        assert!(is_palindrome("".to_string()));
        assert_eq!(two_sum_sorted(vec![2, 7, 11, 15], 9), vec![1, 2]);
        assert_eq!(max_area(vec![1, 8, 6, 2, 5, 4, 8, 3, 7]), 49);
        let mut got = three_sum(vec![-1, 0, 1, 2, -1, -4]);
        got.sort();
        assert_eq!(got, vec![vec![-1, -1, 2], vec![-1, 0, 1]]);
        assert_eq!(three_sum(vec![0, 0]), Vec::<Vec<i32>>::new());
        let mut nums = vec![1, 1, 2, 2, 3];
        assert_eq!(remove_duplicates(&mut nums), 3);
        assert_eq!(&nums[..3], &[1, 2, 3]);
        let mut nums = vec![0, 1, 0, 3, 12];
        move_zeroes(&mut nums);
        assert_eq!(nums, vec![1, 3, 12, 0, 0]);
        assert_eq!(trap(vec![0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]), 6);
        assert_eq!(trap(vec![]), 0);
        assert_eq!(
            sorted_squares(vec![-4, -1, 0, 3, 10]),
            vec![0, 1, 9, 16, 100]
        );
    """,
    "lc-sliding-window": """
        assert_eq!(max_profit(vec![7, 1, 5, 3, 6, 4]), 5);
        assert_eq!(max_profit(vec![7, 6, 4, 3, 1]), 0);
        assert_eq!(length_of_longest_substring("abcabcbb".to_string()), 3);
        assert_eq!(length_of_longest_substring("bbbbb".to_string()), 1);
        assert_eq!(length_of_longest_substring("pwwkew".to_string()), 3);
        assert_eq!(length_of_longest_substring("".to_string()), 0);
        assert_eq!(min_sub_array_len(7, vec![2, 3, 1, 2, 4, 3]), 2);
        assert_eq!(min_sub_array_len(11, vec![1, 1, 1]), 0);
        assert_eq!(character_replacement("ABAB".to_string(), 2), 4);
        assert_eq!(character_replacement("AABABBA".to_string(), 1), 4);
        assert!(
            (find_max_average(vec![1, 12, -5, -6, 50, 3], 4) - 12.75).abs() < 1e-9
        );
        assert!(check_inclusion("ab".to_string(), "eidbaooo".to_string()));
        assert!(!check_inclusion("ab".to_string(), "eidboaoo".to_string()));
        assert!(!check_inclusion("abcd".to_string(), "ab".to_string()));
        assert_eq!(longest_ones(vec![1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), 6);
        assert_eq!(
            min_window("ADOBECODEBANC".to_string(), "ABC".to_string()),
            "BANC"
        );
        assert_eq!(min_window("a".to_string(), "aa".to_string()), "");
    """,
    "lc-stack": """
        assert!(is_valid("()[]{}".to_string()));
        assert!(!is_valid("([)]".to_string()));
        assert!(!is_valid("(".to_string()));
        assert!(!is_valid(")".to_string()));
        let mut ms = MinStack::new();
        ms.push(-2);
        ms.push(0);
        ms.push(-3);
        assert_eq!(ms.get_min(), -3);
        ms.pop();
        assert_eq!(ms.top(), 0);
        assert_eq!(ms.get_min(), -2);
        assert_eq!(eval_rpn(strs(&["2", "1", "+", "3", "*"])), 9);
        assert_eq!(eval_rpn(strs(&["4", "13", "5", "/", "+"])), 6);
        assert_eq!(eval_rpn(strs(&["7", "2", "-"])), 5);
        assert_eq!(
            daily_temperatures(vec![73, 74, 75, 71, 69, 72, 76, 73]),
            vec![1, 1, 4, 2, 1, 1, 0, 0]
        );
        assert_eq!(cal_points(strs(&["5", "2", "C", "D", "+"])), 30);
        assert_eq!(simplify_path("/home//foo/".to_string()), "/home/foo");
        assert_eq!(simplify_path("/../".to_string()), "/");
        assert_eq!(simplify_path("/a/./b/../../c/".to_string()), "/c");
        assert_eq!(largest_rectangle_area(vec![2, 1, 5, 6, 2, 3]), 10);
        assert_eq!(decode_string("3[a]2[bc]".to_string()), "aaabcbc");
        assert_eq!(decode_string("3[a2[c]]".to_string()), "accaccacc");
        assert_eq!(decode_string("10[a]".to_string()), "aaaaaaaaaa");
    """,
}

# A helper the checks use, rather than repeating the conversion inline.
HELPERS = """
fn strs(v: &[&str]) -> Vec<String> {
    v.iter().map(|x| x.to_string()).collect()
}
"""


@unittest.skipUnless(HAS_RUSTC, "needs rustc on PATH")
class RustSolutionTests(unittest.TestCase):
    def _run_pattern(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        parts = list(pattern.preamble)
        parts.append(HELPERS)
        parts.extend(p.code for p in pattern.problems)
        parts.append("fn main() {\n" + CHECKS[pattern_id] + "\n}")
        out, err, code = run_code("\n\n".join(parts), language="rust")
        self.assertEqual(code, 0, (err or out)[:2000])
        # Warnings mean the student is being taught to type something rustc
        # already objects to, which is its own kind of wrong.
        self.assertNotIn("warning:", err, err[:2000])

    def test_every_pattern_compiles_and_holds(self) -> None:
        for pattern_id in CHECKS:
            with self.subTest(pattern=pattern_id):
                self._run_pattern(pattern_id)


class CoverageTests(unittest.TestCase):
    """These run with or without a toolchain."""

    def test_every_pattern_present_has_checks(self) -> None:
        """A pattern with no assertions would compile and prove nothing."""
        self.assertEqual(sorted(CHECKS), sorted(p.id for p in PARTIAL))

    def test_every_pattern_mirrors_the_python_bank(self) -> None:
        """Same problems, same order — that is what lets you switch language
        without losing your place."""
        from code_coach.leetcode.problems import PATTERNS_BY_ID as PY

        for pattern in PARTIAL:
            with self.subTest(pattern=pattern.id):
                theirs = [p.number for p in PY[pattern.id].problems]
                mine = [p.number for p in pattern.problems]
                self.assertEqual(mine, theirs)
                titles = [p.title for p in PY[pattern.id].problems]
                self.assertEqual([p.title for p in pattern.problems], titles)

    def test_the_bank_is_not_registered_while_it_is_partial(self) -> None:
        """A half-written bank is worse than none: has_own_bank would say yes
        and the missing patterns would quietly serve Python."""
        from code_coach.leetcode.bank import has_own_bank

        self.assertFalse(has_own_bank("rust"))


if __name__ == "__main__":
    unittest.main()
