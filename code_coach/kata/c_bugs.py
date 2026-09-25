"""Fix the bug, in C: the function is written, and it is wrong.

The same exercise as the other Fix the bug families, with the bugs C is
known for - and only the well-defined ones. Reading past the end of an
array is the most famous C bug of all, and it is left out on purpose: it
is undefined behaviour, so what it does depends on whatever sits in
memory next, and a start that passes one run and fails the next teaches
nothing. Every bug here does the same wrong thing every time:

  the whole-number divide   int / int throws the remainder away
  the stopped-short loop    `i < nums_len - 1` never sees the last one
  the odd remainder         -3 % 2 is -1 in C, not 1
  the character code        '7' is 55, not 7
  the made-up starting min  0 is smaller than every positive number
  the counter never reset   a run that ended keeps counting

Each one compiles and runs on every case, and passes some of them,
because that is what makes a bug hard to see.

The expected answers come from the Python oracle. There is no C field on
Kata yet, so the fixed code lives in `C_BUG_ANSWERS`, keyed by id.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Fix the bug: C"


def _average_score(scores: list) -> float:
    return sum(scores) / len(scores) if scores else 0.0


def _count_above(nums: list, limit: int) -> int:
    return sum(1 for n in nums if n > limit)


def _odd_count(nums: list) -> int:
    return sum(1 for n in nums if n % 2 != 0)


def _sum_digit_chars(text: str) -> int:
    return sum(int(c) for c in text if c in "0123456789")


def _smallest_of(nums: list) -> int:
    return min(nums) if nums else 0


def _longest_positive_run(nums: list) -> int:
    best = run = 0
    for n in nums:
        run = run + 1 if n > 0 else 0
        best = max(best, run)
    return best


C_BUGS: tuple[Kata, ...] = (
    Kata(
        id="c-bug-average-score",
        level=1,
        language="c",
        family=FAMILY,
        name="averageScore",
        brief=(
            "Return the average of the scores as a double, with its "
            "fraction. No scores average 0.0."
        ),
        params=("scores",),
        types=("int[]",),
        returns="double",
        example="averageScore({1, 2}, 2) is 1.5",
        hint="Try {1, 2}. The result is a double - but what type is total / scores_len?",
        cases=(([1, 2],), ([],), ([4],), ([2, 4, 6],), ([1, 2, 3, 4],),
               ([-3, 0],), ([10, 10, 10],), ([7, 8],)),
        solve=_average_score,
        checks=((([1, 2],), 1.5), (([],), 0.0), (([4],), 4.0), (([-3, 0],), -1.5)),
        start=(
            "double averageScore(const int *scores, int scores_len) {\n"
            "  if (scores_len == 0) {\n"
            "    return 0.0;\n"
            "  }\n"
            "  int total = 0;\n"
            "  for (int i = 0; i < scores_len; i++) {\n"
            "    total += scores[i];\n"
            "  }\n"
            "  return total / scores_len;\n"
            "}\n"
        ),
        bug=(
            "total and scores_len are both ints, so total / scores_len is "
            "whole-number division: the fraction is thrown away before the "
            "result is turned into a double. Returning a double does not "
            "make the division one. Convert first - (double)total / "
            "scores_len."
        ),
    ),
    Kata(
        id="c-bug-count-above",
        level=1,
        language="c",
        family=FAMILY,
        name="countAbove",
        brief="Return how many of the numbers in nums are greater than limit.",
        params=("nums", "limit"),
        types=("int[]", "int"),
        returns="int",
        example="countAbove({5, 1, 9}, 3, 4) is 2",
        hint="Which cases fail? Look at where the big number sits in each of them.",
        cases=(([5, 1, 9], 4), ([], 4), ([9], 4), ([1, 2, 3], 5), ([8, 7, 1], 5),
               ([1, 2, 10], 5), ([-1, -5], -3), ([6, 6, 6], 6)),
        solve=_count_above,
        checks=((([5, 1, 9], 4), 2), (([], 4), 0), (([9], 4), 1), (([-1, -5], -3), 1)),
        start=(
            "int countAbove(const int *nums, int nums_len, int limit) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; i < nums_len - 1; i++) {\n"
            "    if (nums[i] > limit) {\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        bug=(
            "The loop stopped at i < nums_len - 1, so the last number was "
            "never looked at. The indexes of an array of nums_len things "
            "run from 0 to nums_len - 1 inclusive, which is exactly what "
            "i < nums_len gives you. It hid whenever the last number was "
            "not above the limit."
        ),
    ),
    Kata(
        id="c-bug-odd-count",
        level=2,
        language="c",
        family=FAMILY,
        name="oddCount",
        brief="Return how many of the numbers in nums are odd. Negative numbers can be odd too.",
        params=("nums",),
        types=("int[]",),
        returns="int",
        example="oddCount({1, 2, -3}, 3) is 2",
        hint="Work out -3 % 2 in C. It is not what Python says.",
        cases=(([1, 2, -3],), ([],), ([-1],), ([2, 4, 6],), ([1, 3, 5],),
               ([-2, -4],), ([7, -7, 0],), ([10, 11],)),
        solve=_odd_count,
        checks=((([1, 2, -3],), 2), (([],), 0), (([-1],), 1), (([7, -7, 0],), 2)),
        start=(
            "int oddCount(const int *nums, int nums_len) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; i < nums_len; i++) {\n"
            "    if (nums[i] % 2 == 1) {\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        bug=(
            "In C the remainder takes the sign of the number being divided, "
            "so -3 % 2 is -1, never 1, and every negative odd number was "
            "missed. Ask the question that has one answer for both signs: "
            "nums[i] % 2 != 0."
        ),
    ),
    Kata(
        id="c-bug-sum-digit-chars",
        level=2,
        language="c",
        family=FAMILY,
        name="sumDigitChars",
        brief=(
            "Add up the digits that appear in text, skipping every other "
            "character: \"a1b2\" gives 3."
        ),
        params=("text",),
        types=("string",),
        returns="int",
        example='sumDigitChars("a1b2") is 3',
        hint="What number is the character '1'? printf(\"%d\", '1') will tell you.",
        cases=(("a1b2",), ("",), ("7",), ("abc",), ("2026",), ("x-9y",),
               ("no digits here",), ("1 2 3",)),
        solve=_sum_digit_chars,
        checks=((("a1b2",), 3), (("",), 0), (("7",), 7), (("abc",), 0), (("2026",), 10)),
        start=(
            "int sumDigitChars(const char *text) {\n"
            "  int total = 0;\n"
            "  for (int i = 0; text[i] != '\\0'; i++) {\n"
            "    if (text[i] >= '0' && text[i] <= '9') {\n"
            "      total += text[i];\n"
            "    }\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        bug=(
            "A char is a number, but it is the character's code, not the "
            "digit it shows: '1' is 49. The digits are in order, so "
            "text[i] - '0' is the value - '1' - '0' is 1. It only looked "
            "right on strings with no digits at all."
        ),
    ),
    Kata(
        id="c-bug-smallest-of",
        level=2,
        language="c",
        family=FAMILY,
        name="smallestOf",
        brief="Return the smallest of the numbers in nums, or 0 when there are none.",
        params=("nums",),
        types=("int[]",),
        returns="int",
        example="smallestOf({4, 2, 8}, 3) is 2",
        hint="Try {4, 2, 8}. What is the smallest number the loop could ever report?",
        cases=(([4, 2, 8],), ([],), ([-5],), ([3],), ([0, 9],), ([-1, -7, 2],),
               ([10, 20, 30],), ([6, 6],)),
        solve=_smallest_of,
        checks=((([4, 2, 8],), 2), (([],), 0), (([-5],), -5), (([3],), 3),
                (([-1, -7, 2],), -7)),
        start=(
            "int smallestOf(const int *nums, int nums_len) {\n"
            "  int best = 0;\n"
            "  for (int i = 0; i < nums_len; i++) {\n"
            "    if (nums[i] < best) {\n"
            "      best = nums[i];\n"
            "    }\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        bug=(
            "best started at 0, a number that was never in the array, so "
            "whenever every number was positive nothing beat it and 0 came "
            "back. Deal with the empty array on its own, then start from "
            "nums[0] - the only honest first guess is a real one."
        ),
    ),
    Kata(
        id="c-bug-longest-positive-run",
        level=3,
        language="c",
        family=FAMILY,
        name="longestPositiveRun",
        brief=(
            "Return the length of the longest stretch of numbers in a row "
            "that are all greater than 0."
        ),
        params=("nums",),
        types=("int[]",),
        returns="int",
        example="longestPositiveRun({1, 2, 0, 3}, 4) is 2",
        hint="Try {1, 2, 0, 3}. What should happen to run when the 0 comes along?",
        cases=(([1, 2, 0, 3],), ([],), ([5],), ([-1],), ([1, 1, 1],),
               ([0, 4, 4, 0],), ([2, -1, 2, -1, 2],), ([3, 3, 0, 3, 3, 3],)),
        solve=_longest_positive_run,
        checks=((([1, 2, 0, 3],), 2), (([],), 0), (([-1],), 0), (([5],), 1),
                (([2, -1, 2, -1, 2],), 1), (([3, 3, 0, 3, 3, 3],), 3)),
        start=(
            "int longestPositiveRun(const int *nums, int nums_len) {\n"
            "  int run = 0;\n"
            "  int best = 0;\n"
            "  for (int i = 0; i < nums_len; i++) {\n"
            "    if (nums[i] > 0) {\n"
            "      run++;\n"
            "      if (run > best) {\n"
            "        best = run;\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        bug=(
            "Nothing set run back to 0 when a number that was not positive "
            "came along, so it counted every positive number in the array "
            "rather than the ones in a row. A counter for a streak needs "
            "an else that ends the streak: else run = 0;"
        ),
    ),
)


C_BUG_ANSWERS: dict[str, str] = {
    "c-bug-average-score": (
        "double averageScore(const int *scores, int scores_len) {\n"
        "  if (scores_len == 0) {\n"
        "    return 0.0;\n"
        "  }\n"
        "  int total = 0;\n"
        "  for (int i = 0; i < scores_len; i++) {\n"
        "    total += scores[i];\n"
        "  }\n"
        "  return (double)total / scores_len;\n"
        "}\n"
    ),
    "c-bug-count-above": (
        "int countAbove(const int *nums, int nums_len, int limit) {\n"
        "  int count = 0;\n"
        "  for (int i = 0; i < nums_len; i++) {\n"
        "    if (nums[i] > limit) {\n"
        "      count++;\n"
        "    }\n"
        "  }\n"
        "  return count;\n"
        "}\n"
    ),
    "c-bug-odd-count": (
        "int oddCount(const int *nums, int nums_len) {\n"
        "  int count = 0;\n"
        "  for (int i = 0; i < nums_len; i++) {\n"
        "    if (nums[i] % 2 != 0) {\n"
        "      count++;\n"
        "    }\n"
        "  }\n"
        "  return count;\n"
        "}\n"
    ),
    "c-bug-sum-digit-chars": (
        "int sumDigitChars(const char *text) {\n"
        "  int total = 0;\n"
        "  for (int i = 0; text[i] != '\\0'; i++) {\n"
        "    if (text[i] >= '0' && text[i] <= '9') {\n"
        "      total += text[i] - '0';\n"
        "    }\n"
        "  }\n"
        "  return total;\n"
        "}\n"
    ),
    "c-bug-smallest-of": (
        "int smallestOf(const int *nums, int nums_len) {\n"
        "  if (nums_len == 0) {\n"
        "    return 0;\n"
        "  }\n"
        "  int best = nums[0];\n"
        "  for (int i = 1; i < nums_len; i++) {\n"
        "    if (nums[i] < best) {\n"
        "      best = nums[i];\n"
        "    }\n"
        "  }\n"
        "  return best;\n"
        "}\n"
    ),
    "c-bug-longest-positive-run": (
        "int longestPositiveRun(const int *nums, int nums_len) {\n"
        "  int run = 0;\n"
        "  int best = 0;\n"
        "  for (int i = 0; i < nums_len; i++) {\n"
        "    if (nums[i] > 0) {\n"
        "      run++;\n"
        "      if (run > best) {\n"
        "        best = run;\n"
        "      }\n"
        "    } else {\n"
        "      run = 0;\n"
        "    }\n"
        "  }\n"
        "  return best;\n"
        "}\n"
    ),
}


def _with_answers():
    from dataclasses import replace

    return tuple(replace(k, c_answer=C_BUG_ANSWERS[k.id]) for k in C_BUGS)


C_BUGS = _with_answers()
