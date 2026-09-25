"""Fix the bug, in C: the second set.

The same rules as `c_bugs.py`: every start compiles without a warning,
runs every case without crashing or touching undefined behaviour, and
passes some cases while failing others. The bugs are new ones:

  the range that is always true   `||` where `&&` belonged
  the threshold that excludes     `>` where "at least" meant `>=`
  the alphabet one letter short   'A' to 'Y' is not every capital
  the verdict inside the loop     an else that returns after one look
  the compare that stops early    two strings are not equal because
                                  one is the start of the other
  the champion never demoted      a new best forgets the old best
                                  was the new second
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Fix the bug: C"


def _in_range(n: int, low: int, high: int) -> bool:
    return low <= n <= high


def _passing_count(scores: list, pass_mark: int) -> int:
    return sum(1 for s in scores if s >= pass_mark)


def _count_upper(text: str) -> int:
    return sum(1 for c in text if "A" <= c <= "Z")


def _first_index_of(nums: list, target: int) -> int:
    return nums.index(target) if target in nums else -1


def _same_word(a: str, b: str) -> bool:
    return a == b


def _second_highest(nums: list) -> int:
    return sorted(nums, reverse=True)[1] if len(nums) >= 2 else 0


C_BUGS_2: tuple[Kata, ...] = (
    Kata(
        id="c-bug-in-range",
        level=1,
        language="c",
        family=FAMILY,
        name="inRange",
        brief="Return whether n lies between low and high, both ends included.",
        params=("n", "low", "high"),
        types=("int", "int", "int"),
        returns="bool",
        example="inRange(5, 1, 10) is true; inRange(11, 1, 10) is false",
        hint="Try inRange(0, 1, 10). Is 0 at least 1? Is it at most 10? What does || make of that?",
        cases=((5, 1, 10), (0, 1, 10), (1, 1, 10), (10, 1, 10), (11, 1, 10),
               (-3, -5, -1), (-6, -5, -1), (0, 0, 0)),
        solve=_in_range,
        checks=(((5, 1, 10), True), ((0, 1, 10), False), ((11, 1, 10), False),
                ((-6, -5, -1), False), ((0, 0, 0), True)),
        start=(
            "#include <stdbool.h>\n"
            "\n"
            "bool inRange(int n, int low, int high) {\n"
            "  return n >= low || n <= high;\n"
            "}\n"
        ),
        c_answer=(
            "#include <stdbool.h>\n"
            "\n"
            "bool inRange(int n, int low, int high) {\n"
            "  return n >= low && n <= high;\n"
            "}\n"
        ),
        bug=(
            "|| is true when either side is, and every number is either at "
            "least low or at most high - so the answer was true for every "
            "number there is. Being inside a range means both at once: "
            "n >= low && n <= high. It hid because every number that is "
            "in the range passes both tests anyway."
        ),
    ),
    Kata(
        id="c-bug-passing-count",
        level=1,
        language="c",
        family=FAMILY,
        name="passingCount",
        brief=(
            "Return how many scores pass. A score passes when it is at "
            "least pass - a score equal to pass passes."
        ),
        params=("scores", "pass"),
        types=("int[]", "int"),
        returns="int",
        example="passingCount({50, 70, 40}, 3, 50) is 2",
        hint="Which scores fail in the failing cases? Look for one that is exactly pass.",
        cases=(([50, 70, 40], 50), ([], 50), ([50], 50), ([49], 50), ([90, 80], 50),
               ([0, 0, 1], 0), ([-2, -1], -1), ([60, 60, 61], 60)),
        solve=_passing_count,
        checks=((([50, 70, 40], 50), 2), (([], 50), 0), (([50], 50), 1),
                (([49], 50), 0), (([-2, -1], -1), 1)),
        start=(
            "int passingCount(const int *scores, int scores_len, int pass) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; i < scores_len; i++) {\n"
            "    if (scores[i] > pass) {\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        c_answer=(
            "int passingCount(const int *scores, int scores_len, int pass) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; i < scores_len; i++) {\n"
            "    if (scores[i] >= pass) {\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        bug=(
            "\"At least pass\" includes pass itself, and > leaves it out: "
            "the student who scored exactly the mark failed. Read the rule "
            "for its boundary and pick the operator that includes it: >=. "
            "Every case without a score sitting exactly on the mark passed, "
            "which is why boundaries are what tests should aim at."
        ),
    ),
    Kata(
        id="c-bug-count-upper",
        level=2,
        language="c",
        family=FAMILY,
        name="countUpper",
        brief="Return how many capital letters, 'A' to 'Z', are in text.",
        params=("text",),
        types=("string",),
        returns="int",
        example='countUpper("Hello World") is 2',
        hint='Try countUpper("ZIP"). Which of the three letters is not counted?',
        cases=(("Hello World",), ("",), ("ZIP",), ("abc",), ("Zz",), ("A-Z",),
               ("NASA",), ("lazy Zebra",)),
        solve=_count_upper,
        checks=((("Hello World",), 2), (("",), 0), (("ZIP",), 3), (("Zz",), 1),
                (("NASA",), 4)),
        start=(
            "int countUpper(const char *text) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; text[i] != '\\0'; i++) {\n"
            "    if (text[i] >= 'A' && text[i] < 'Z') {\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        c_answer=(
            "int countUpper(const char *text) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; text[i] != '\\0'; i++) {\n"
            "    if (text[i] >= 'A' && text[i] <= 'Z') {\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        bug=(
            "text[i] < 'Z' stops one letter short, so every Z was missed. "
            "Letters are a range with two named ends, and both ends are in "
            "it: 'A' <= c && c <= 'Z'. Z is the rarest capital in ordinary "
            "text, which is how a bug like this ships."
        ),
    ),
    Kata(
        id="c-bug-first-index-of",
        level=3,
        language="c",
        family=FAMILY,
        name="firstIndexOf",
        brief="Return the index of the first number in nums equal to target, or -1 if none is.",
        params=("nums", "target"),
        types=("int[]", "int"),
        returns="int",
        example="firstIndexOf({4, 7, 9}, 3, 9) is 2",
        hint="Try {4, 7, 9} looking for 9. How many numbers does the loop look at before it returns?",
        cases=(([4, 7, 9], 4), ([4, 7, 9], 9), ([], 1), ([5], 3), ([1, 2, 1], 1),
               ([3, -2], -2), ([8, 8], 8), ([6, 5, 4, 3], 3)),
        solve=_first_index_of,
        checks=((([4, 7, 9], 9), 2), (([], 1), -1), (([5], 3), -1),
                (([1, 2, 1], 1), 0), (([3, -2], -2), 1)),
        start=(
            "int firstIndexOf(const int *nums, int nums_len, int target) {\n"
            "  for (int i = 0; i < nums_len; i++) {\n"
            "    if (nums[i] == target) {\n"
            "      return i;\n"
            "    } else {\n"
            "      return -1;\n"
            "    }\n"
            "  }\n"
            "  return -1;\n"
            "}\n"
        ),
        c_answer=(
            "int firstIndexOf(const int *nums, int nums_len, int target) {\n"
            "  for (int i = 0; i < nums_len; i++) {\n"
            "    if (nums[i] == target) {\n"
            "      return i;\n"
            "    }\n"
            "  }\n"
            "  return -1;\n"
            "}\n"
        ),
        bug=(
            "The else returned -1 the first time a number did not match, so "
            "the loop never got past index 0. One match is enough to say "
            "yes, but no is only true once every number has been looked "
            "at - so the -1 belongs after the loop, and the else goes."
        ),
    ),
    Kata(
        id="c-bug-same-word",
        level=3,
        language="c",
        family=FAMILY,
        name="sameWord",
        brief="Return whether the strings a and b hold exactly the same characters.",
        params=("a", "b"),
        types=("string", "string"),
        returns="bool",
        example='sameWord("cat", "cat") is true; sameWord("cat", "cats") is false',
        hint='Try "cat" and "cats". Why did the loop stop, and what does it say when it does?',
        cases=(("cat", "cat"), ("cat", "cats"), ("cats", "cat"), ("", ""), ("", "a"),
               ("dog", "dig"), ("Cat", "cat"), ("to", "top")),
        solve=_same_word,
        checks=((("cat", "cat"), True), (("cat", "cats"), False), (("", ""), True),
                (("", "a"), False), (("Cat", "cat"), False)),
        start=(
            "#include <stdbool.h>\n"
            "\n"
            "bool sameWord(const char *a, const char *b) {\n"
            "  int i = 0;\n"
            "  while (a[i] != '\\0' && b[i] != '\\0') {\n"
            "    if (a[i] != b[i]) {\n"
            "      return false;\n"
            "    }\n"
            "    i++;\n"
            "  }\n"
            "  return true;\n"
            "}\n"
        ),
        c_answer=(
            "#include <stdbool.h>\n"
            "\n"
            "bool sameWord(const char *a, const char *b) {\n"
            "  int i = 0;\n"
            "  while (a[i] != '\\0' && b[i] != '\\0') {\n"
            "    if (a[i] != b[i]) {\n"
            "      return false;\n"
            "    }\n"
            "    i++;\n"
            "  }\n"
            "  return a[i] == b[i];\n"
            "}\n"
        ),
        bug=(
            "The loop stops as soon as either string ends, and then said "
            "true - so \"cat\" matched \"cats\", because every character "
            "it compared was equal. When the loop stops, the words are the "
            "same only if both ended there: return a[i] == b[i], which is "
            "true only when both are '\\0'. strcmp(a, b) == 0 does all of it."
        ),
    ),
    Kata(
        id="c-bug-second-highest",
        level=4,
        language="c",
        family=FAMILY,
        name="secondHighest",
        brief=(
            "Return the second-highest number in nums, counting repeats - "
            "{9, 9, 4} gives 9. Fewer than two numbers give 0."
        ),
        params=("nums",),
        types=("int[]",),
        returns="int",
        example="secondHighest({1, 2, 5}, 3) is 2",
        hint="Try {1, 2, 5}. When 5 takes the top spot, where should the old top go?",
        cases=(([5, 1, 2],), ([1, 2, 5],), ([],), ([7],), ([3, 3],), ([4, 9, 9],),
               ([-1, -5, -3],), ([1, 2, 3, 4],), ([10, 20, 30, 5],)),
        solve=_second_highest,
        checks=((([1, 2, 5],), 2), (([5, 1, 2],), 2), (([],), 0), (([7],), 0),
                (([4, 9, 9],), 9), (([-1, -5, -3],), -3), (([1, 2, 3, 4],), 3)),
        start=(
            "int secondHighest(const int *nums, int nums_len) {\n"
            "  if (nums_len < 2) {\n"
            "    return 0;\n"
            "  }\n"
            "  int first = nums[0] > nums[1] ? nums[0] : nums[1];\n"
            "  int second = nums[0] > nums[1] ? nums[1] : nums[0];\n"
            "  for (int i = 2; i < nums_len; i++) {\n"
            "    if (nums[i] > first) {\n"
            "      first = nums[i];\n"
            "    } else if (nums[i] > second) {\n"
            "      second = nums[i];\n"
            "    }\n"
            "  }\n"
            "  return second;\n"
            "}\n"
        ),
        c_answer=(
            "int secondHighest(const int *nums, int nums_len) {\n"
            "  if (nums_len < 2) {\n"
            "    return 0;\n"
            "  }\n"
            "  int first = nums[0] > nums[1] ? nums[0] : nums[1];\n"
            "  int second = nums[0] > nums[1] ? nums[1] : nums[0];\n"
            "  for (int i = 2; i < nums_len; i++) {\n"
            "    if (nums[i] > first) {\n"
            "      second = first;\n"
            "      first = nums[i];\n"
            "    } else if (nums[i] > second) {\n"
            "      second = nums[i];\n"
            "    }\n"
            "  }\n"
            "  return second;\n"
            "}\n"
        ),
        bug=(
            "When a new highest arrived, the old highest was simply "
            "overwritten - but it had just become the second highest. "
            "Move it down before replacing it: second = first; then "
            "first = nums[i]. The order of those two lines matters. It "
            "hid whenever the largest number came first."
        ),
    ),
)
