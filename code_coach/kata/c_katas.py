"""Katas in C: the loops every other language hides from you.

C gives you an array as a pointer and a length, a string as characters
running up to a zero byte, and a list result as a buffer someone else
owns. Nothing here is hard in Python, and that is the point: each one is
the same small job done with nothing but a loop, an index and the
rules C actually has.

  an array is a pointer and a count   arraySum, maxOrZero
  a string ends at '\\0'               stringLength, readsBothWays,
                                      countWords
  a list result goes into `out`       reverseInto, clampInto
  % and / on whole numbers            digitSum

The oracle is Python, as for every kata. There is no C field on Kata
yet, so the worked answers live in `C_ANSWERS`, keyed by id; the suite
compiles each one and runs it against the oracle through the C driver
(kata/c_harness.py), and checks it compiles without a warning.

Nothing here may change what it was handed - the parameters are
`const`, and the driver compares every array before and after the call.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "C"


def _array_sum(nums: list) -> int:
    return sum(nums)


def _string_length(text: str) -> int:
    return len(text)


def _max_or_zero(nums: list) -> int:
    return max(nums) if nums else 0


def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def _reverse_into(nums: list) -> list:
    return nums[::-1]


def _clamp_into(nums: list, lo: int, hi: int) -> list:
    return [min(max(n, lo), hi) for n in nums]


def _reads_both_ways(text: str) -> bool:
    return text == text[::-1]


def _count_words(text: str) -> int:
    return len([word for word in text.split(" ") if word])


C_KATAS: tuple[Kata, ...] = (
    Kata(
        id="c-array-sum",
        level=1,
        language="c",
        family=FAMILY,
        name="arraySum",
        brief="Return the total of the nums_len numbers in nums. No numbers total 0.",
        params=("nums",),
        types=("int[]",),
        returns="int",
        example="arraySum({1, 2, 3}, 3) is 6",
        hint=(
            "C cannot ask an array how long it is - that is what nums_len "
            "is for. Start a total at 0 and walk i from 0 while i < nums_len."
        ),
        cases=(([1, 2, 3],), ([],), ([5],), ([-4],), ([-2, 2],),
               ([10, 20, 30, 40],), ([0, 0, 0],), ([7, -3, 1],)),
        solve=_array_sum,
        checks=((([1, 2, 3],), 6), (([],), 0), (([-4],), -4), (([7, -3, 1],), 5)),
    ),
    Kata(
        id="c-string-length",
        level=1,
        language="c",
        family=FAMILY,
        name="stringLength",
        brief=(
            "Return how many characters are in text, without calling "
            "strlen. A C string ends at the first '\\0' character."
        ),
        params=("text",),
        types=("string",),
        returns="int",
        example='stringLength("cat") is 3',
        hint=(
            "Count up from 0 until text[i] is '\\0'. The zero byte is how "
            "the string ends; it is not one of its characters."
        ),
        cases=(("cat",), ("",), ("a",), ("hello world",), ("  ",), ("C17",),
               ("a longer sentence here",)),
        solve=_string_length,
        checks=((("cat",), 3), (("",), 0), (("a",), 1), (("  ",), 2)),
    ),
    Kata(
        id="c-max-or-zero",
        level=2,
        language="c",
        family=FAMILY,
        name="maxOrZero",
        brief=(
            "Return the largest of the nums_len numbers in nums, or 0 when "
            "there are none. The numbers may all be negative."
        ),
        params=("nums",),
        types=("int[]",),
        returns="int",
        example="maxOrZero({3, 9, 4}, 3) is 9, and maxOrZero({}, 0) is 0",
        hint=(
            "Starting the best at 0 is wrong when every number is negative. "
            "Handle the empty array first, then start from nums[0]."
        ),
        cases=(([3, 9, 4],), ([],), ([-5],), ([-3, -1, -7],), ([2, 2],),
               ([0, -1],), ([1, 5, 3, 8, 2],), ([100],)),
        solve=_max_or_zero,
        checks=((([3, 9, 4],), 9), (([],), 0), (([-3, -1, -7],), -1), (([-5],), -5)),
    ),
    Kata(
        id="c-digit-sum",
        level=2,
        language="c",
        family=FAMILY,
        name="digitSum",
        brief=(
            "Return the sum of the decimal digits of n. A negative number "
            "has the same digits as its positive: digitSum(-45) is 9."
        ),
        params=("n",),
        types=("int",),
        returns="int",
        example="digitSum(123) is 6",
        hint=(
            "n % 10 is the last digit and n / 10 drops it. In C, -45 % 10 "
            "is -5, not 5 - so make n positive before you start."
        ),
        cases=((123,), (0,), (7,), (-45,), (9999,), (1000,), (505,), (-1,)),
        solve=_digit_sum,
        checks=(((123,), 6), ((0,), 0), ((-45,), 9), ((1000,), 1), ((-1,), 1)),
    ),
    Kata(
        id="c-reverse-into",
        level=2,
        language="c",
        family=FAMILY,
        name="reverseInto",
        brief=(
            "Write the numbers of nums into out in reverse order, and "
            "return how many you wrote. nums itself must not change."
        ),
        params=("nums",),
        types=("int[]",),
        returns="int[]",
        example="reverseInto({1, 2, 3}, 3, out) writes 3, 2, 1 and returns 3",
        hint=(
            "out[i] gets nums[nums_len - 1 - i]. The count you return is "
            "what tells the caller how much of out is filled."
        ),
        cases=(([1, 2, 3],), ([],), ([4],), ([-1, 0, 1],), ([5, 5, 6],),
               ([9, 8, 7, 6, 5, 4],)),
        solve=_reverse_into,
        checks=((([1, 2, 3],), [3, 2, 1]), (([],), []), (([4],), [4]),
                (([-1, 0, 1],), [1, 0, -1])),
    ),
    Kata(
        id="c-clamp-into",
        level=3,
        language="c",
        family=FAMILY,
        name="clampInto",
        brief=(
            "Write each number of nums into out, raised to lo if it is "
            "below lo and lowered to hi if it is above hi. Return how many "
            "you wrote. lo is never more than hi."
        ),
        params=("nums", "lo", "hi"),
        types=("int[]", "int", "int"),
        returns="int[]",
        example="clampInto({-5, 3, 12}, 3, 0, 10, out) writes 0, 3, 10 and returns 3",
        hint=(
            "Two ifs per number, into a local, then out[i] = that local. "
            "Write to out, never to nums - nums is const for a reason."
        ),
        cases=(([-5, 3, 12], 0, 10), ([], 0, 10), ([7], 7, 7), ([1, 2, 3], -1, 1),
               ([-10, -20], -15, -5), ([0, 5, 10], 0, 10), ([100, -100, 50], 0, 60)),
        solve=_clamp_into,
        checks=((([-5, 3, 12], 0, 10), [0, 3, 10]), (([], 0, 10), []),
                (([1, 2, 3], -1, 1), [1, 1, 1]), (([-10, -20], -15, -5), [-10, -15])),
    ),
    Kata(
        id="c-reads-both-ways",
        level=3,
        language="c",
        family=FAMILY,
        name="readsBothWays",
        brief=(
            "Say whether text reads the same backwards as forwards, "
            "character for character. Case and spaces count. An empty "
            "string does."
        ),
        params=("text",),
        types=("string",),
        returns="bool",
        example='readsBothWays("racecar") is true, readsBothWays("Abba") is false',
        hint=(
            "One index from the front, one from the back, meeting in the "
            "middle. You need the length first, and bool needs <stdbool.h>."
        ),
        cases=(("racecar",), ("",), ("a",), ("ab",), ("abba",), ("Abba",),
               ("abca",), ("never odd or even",), ("step on no pets",)),
        solve=_reads_both_ways,
        checks=((("racecar",), True), (("",), True), (("ab",), False),
                (("Abba",), False), (("step on no pets",), True)),
    ),
    Kata(
        id="c-count-words",
        level=4,
        language="c",
        family=FAMILY,
        name="countWords",
        brief=(
            "Return how many words are in text, where words are separated "
            "by one or more spaces. Spaces at the start and end do not "
            "make words."
        ),
        params=("text",),
        types=("string",),
        returns="int",
        example='countWords("  hello   big world ") is 3',
        hint=(
            "Count the starts of words: a character that is not a space "
            "where the one before it was a space, or was nothing at all."
        ),
        cases=(("hello world",), ("",), ("   ",), ("one",), ("  hello   big world ",),
               ("a b c d",), (" x",), ("trailing  ",)),
        solve=_count_words,
        checks=((("hello world",), 2), (("",), 0), (("   ",), 0),
                (("  hello   big world ",), 3), ((" x",), 1)),
    ),
)


C_ANSWERS: dict[str, str] = {
    "c-array-sum": (
        "int arraySum(const int *nums, int nums_len) {\n"
        "  int total = 0;\n"
        "  for (int i = 0; i < nums_len; i++) {\n"
        "    total += nums[i];\n"
        "  }\n"
        "  return total;\n"
        "}\n"
    ),
    "c-string-length": (
        "int stringLength(const char *text) {\n"
        "  int n = 0;\n"
        "  while (text[n] != '\\0') {\n"
        "    n++;\n"
        "  }\n"
        "  return n;\n"
        "}\n"
    ),
    "c-max-or-zero": (
        "int maxOrZero(const int *nums, int nums_len) {\n"
        "  if (nums_len == 0) {\n"
        "    return 0;\n"
        "  }\n"
        "  int best = nums[0];\n"
        "  for (int i = 1; i < nums_len; i++) {\n"
        "    if (nums[i] > best) {\n"
        "      best = nums[i];\n"
        "    }\n"
        "  }\n"
        "  return best;\n"
        "}\n"
    ),
    "c-digit-sum": (
        "int digitSum(int n) {\n"
        "  if (n < 0) {\n"
        "    n = -n;\n"
        "  }\n"
        "  int total = 0;\n"
        "  while (n > 0) {\n"
        "    total += n % 10;\n"
        "    n /= 10;\n"
        "  }\n"
        "  return total;\n"
        "}\n"
    ),
    "c-reverse-into": (
        "int reverseInto(const int *nums, int nums_len, int *out) {\n"
        "  for (int i = 0; i < nums_len; i++) {\n"
        "    out[i] = nums[nums_len - 1 - i];\n"
        "  }\n"
        "  return nums_len;\n"
        "}\n"
    ),
    "c-clamp-into": (
        "int clampInto(const int *nums, int nums_len, int lo, int hi, int *out) {\n"
        "  for (int i = 0; i < nums_len; i++) {\n"
        "    int n = nums[i];\n"
        "    if (n < lo) {\n"
        "      n = lo;\n"
        "    }\n"
        "    if (n > hi) {\n"
        "      n = hi;\n"
        "    }\n"
        "    out[i] = n;\n"
        "  }\n"
        "  return nums_len;\n"
        "}\n"
    ),
    "c-reads-both-ways": (
        "#include <stdbool.h>\n"
        "#include <string.h>\n"
        "\n"
        "bool readsBothWays(const char *text) {\n"
        "  int left = 0;\n"
        "  int right = (int)strlen(text) - 1;\n"
        "  while (left < right) {\n"
        "    if (text[left] != text[right]) {\n"
        "      return false;\n"
        "    }\n"
        "    left++;\n"
        "    right--;\n"
        "  }\n"
        "  return true;\n"
        "}\n"
    ),
    "c-count-words": (
        "int countWords(const char *text) {\n"
        "  int count = 0;\n"
        "  char before = ' ';\n"
        "  for (int i = 0; text[i] != '\\0'; i++) {\n"
        "    if (text[i] != ' ' && before == ' ') {\n"
        "      count++;\n"
        "    }\n"
        "    before = text[i];\n"
        "  }\n"
        "  return count;\n"
        "}\n"
    ),
}


def _with_answers():
    from dataclasses import replace

    return tuple(replace(k, c_answer=C_ANSWERS[k.id]) for k in C_KATAS)


C_KATAS = _with_answers()
