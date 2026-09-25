"""More katas in C: the second shelf of loops C makes you write yourself.

The first eight (c_katas.py) are sums, lengths and one pass over an
array. These go a step further into what C programmers actually do:

  a char is a small number           countChar, isAnagram (26 counters)
  an array of strings                totalLength
  bits and whole numbers             isPowerOfTwo, euclidGcd
  long long when int is too small    fibLong
  a sorted array is a promise        binarySearch, dedupeSorted,
                                     mergeSorted
  the value you track beside best    secondLargest

The worked answer rides on each Kata as `c_answer`; the suite compiles
it, runs it against the Python oracle through the C driver
(kata/c_harness.py), and checks it compiles without a warning.

Nothing here may change what it was handed - the parameters are
`const`, and the driver compares every array before and after the call.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "C"
INT_MIN = -2147483648


def _count_char(text: str, c: str) -> int:
    return text.count(c)


def _total_length(words: list) -> int:
    return sum(len(w) for w in words)


def _is_power_of_two(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


def _euclid_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def _fib_long(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _binary_search(nums: list, target: int) -> int:
    return nums.index(target) if target in nums else -1


def _dedupe_sorted(nums: list) -> list:
    return [n for i, n in enumerate(nums) if i == 0 or nums[i - 1] != n]


def _merge_sorted(a: list, b: list) -> list:
    return sorted(a + b)


def _is_anagram(first: str, second: str) -> bool:
    return sorted(first) == sorted(second)


def _second_largest(nums: list) -> int:
    distinct = sorted(set(nums))
    return distinct[-2] if len(distinct) >= 2 else INT_MIN


C_KATAS_2: tuple[Kata, ...] = (
    Kata(
        id="c-count-char",
        level=1,
        language="c",
        family=FAMILY,
        name="countChar",
        brief="Return how many times the character c appears in text.",
        params=("text", "c"),
        types=("string", "char"),
        returns="int",
        example="countChar(\"banana\", 'a') is 3",
        hint=(
            "Walk text until '\\0' and compare each text[i] with c using ==. "
            "A char is a small number, so comparing two of them is cheap."
        ),
        cases=(("banana", "a"), ("", "a"), ("a", "a"), ("banana", "z"),
               ("Mississippi", "s"), ("AaAa", "A"), ("  x  ", " "), ("zzz", "z")),
        solve=_count_char,
        checks=((("banana", "a"), 3), (("", "a"), 0), (("banana", "z"), 0),
                (("AaAa", "A"), 2), (("  x  ", " "), 4)),
    ),
    Kata(
        id="c-total-length",
        level=1,
        language="c",
        family=FAMILY,
        name="totalLength",
        brief=(
            "words is an array of words_len strings. Return how many "
            "characters they hold between them."
        ),
        params=("words",),
        types=("string[]",),
        returns="int",
        example='totalLength({"hi", "there"}, 2) is 7',
        hint=(
            "Each words[i] is a const char *, a string of its own. strlen "
            "from <string.h> gives its length as a size_t - cast it to int "
            "as you add it up."
        ),
        cases=((["hi", "there"],), ([],), ([""],), (["a"],), (["", "", "abc"],),
               (["one", "two", "three"],), (["a longer word here"],)),
        solve=_total_length,
        checks=(((["hi", "there"],), 7), (([],), 0), (([""],), 0),
                ((["", "", "abc"],), 3)),
    ),
    Kata(
        id="c-is-power-of-two",
        level=2,
        language="c",
        family=FAMILY,
        name="isPowerOfTwo",
        brief=(
            "Say whether n is a power of two: 1, 2, 4, 8 and so on. Zero "
            "and negative numbers are not."
        ),
        params=("n",),
        types=("int",),
        returns="bool",
        example="isPowerOfTwo(8) is true, isPowerOfTwo(6) is false",
        hint=(
            "A power of two has exactly one bit set, and n - 1 flips that "
            "bit and sets every bit below it - so n & (n - 1) is 0. Check "
            "n > 0 first, or 0 slips through."
        ),
        cases=((8,), (0,), (1,), (-8,), (6,), (2,), (1024,), (1023,),
               (1073741824,), (-1,)),
        solve=_is_power_of_two,
        checks=(((8,), True), ((0,), False), ((1,), True), ((-8,), False),
                ((6,), False), ((1073741824,), True)),
    ),
    Kata(
        id="c-euclid-gcd",
        level=2,
        language="c",
        family=FAMILY,
        name="euclidGcd",
        brief=(
            "Return the greatest common divisor of a and b, which are never "
            "negative. The gcd of a number and 0 is that number, and "
            "euclidGcd(0, 0) is 0."
        ),
        params=("a", "b"),
        types=("int", "int"),
        returns="int",
        example="euclidGcd(12, 18) is 6",
        hint=(
            "Euclid: while b is not 0, replace (a, b) with (b, a % b). C "
            "has no tuple swap - keep a % b in a temporary first."
        ),
        cases=((12, 18), (0, 0), (0, 5), (7, 0), (1, 1), (17, 5), (100, 75),
               (270, 192), (9, 9)),
        solve=_euclid_gcd,
        checks=(((12, 18), 6), ((0, 0), 0), ((0, 5), 5), ((7, 0), 7),
                ((17, 5), 1), ((270, 192), 6)),
    ),
    Kata(
        id="c-fib-long",
        level=3,
        language="c",
        family=FAMILY,
        name="fibLong",
        brief=(
            "Return the nth Fibonacci number, where fibLong(0) is 0 and "
            "fibLong(1) is 1. n goes up to 90, far past what an int holds."
        ),
        params=("n",),
        types=("int",),
        returns="long long",
        example="fibLong(10) is 55",
        hint=(
            "Two long long variables walked forward n times. An int "
            "overflows after fibLong(46), and signed overflow in C is "
            "undefined - not just a wrong number."
        ),
        cases=((10,), (0,), (1,), (2,), (46,), (47,), (60,), (90,)),
        solve=_fib_long,
        checks=(((10,), 55), ((0,), 0), ((1,), 1), ((47,), 2971215073),
                ((90,), 2880067194370816120)),
    ),
    Kata(
        id="c-binary-search",
        level=3,
        language="c",
        family=FAMILY,
        name="binarySearch",
        brief=(
            "nums is sorted from smallest to largest with no repeats. "
            "Return the index of target in nums, or -1 when it is not "
            "there. Halve the range each step rather than walking it all."
        ),
        params=("nums", "target"),
        types=("int[]", "int"),
        returns="int",
        example="binarySearch({1, 3, 5, 7}, 4, 5) is 2",
        hint=(
            "Keep lo and hi as the ends of the range still possible. Take "
            "mid = lo + (hi - lo) / 2, which cannot overflow, and move lo "
            "or hi past mid. Stop when lo passes hi."
        ),
        cases=(([1, 3, 5, 7], 5), ([], 3), ([4], 4), ([4], 5), ([1, 3, 5, 7], 1),
               ([1, 3, 5, 7], 7), ([1, 3, 5, 7], 4), ([-9, -4, 0, 2], -4),
               ([-9, -4, 0, 2], -10), ([2, 4, 6, 8, 10, 12, 14], 12)),
        solve=_binary_search,
        checks=((([1, 3, 5, 7], 5), 2), (([], 3), -1), (([4], 4), 0),
                (([1, 3, 5, 7], 4), -1), (([-9, -4, 0, 2], -4), 1),
                (([1, 3, 5, 7], 7), 3)),
    ),
    Kata(
        id="c-dedupe-sorted",
        level=4,
        language="c",
        family=FAMILY,
        name="dedupeSorted",
        brief=(
            "nums is sorted. Write each different value into out once, in "
            "order, and return how many you wrote."
        ),
        params=("nums",),
        types=("int[]",),
        returns="int[]",
        example="dedupeSorted({1, 1, 2, 3, 3}, 5, out) writes 1, 2, 3 and returns 3",
        hint=(
            "Because nums is sorted, repeats sit next to each other. Copy "
            "nums[i] when it is the first one or differs from nums[i - 1], "
            "and keep a separate count for where the next one goes in out."
        ),
        cases=(([1, 1, 2, 3, 3],), ([],), ([5],), ([2, 2, 2],), ([-3, -3, 0, 0, 4],),
               ([1, 2, 3],), ([7, 7, 8, 9, 9, 9, 10],)),
        solve=_dedupe_sorted,
        checks=((([1, 1, 2, 3, 3],), [1, 2, 3]), (([],), []), (([2, 2, 2],), [2]),
                (([-3, -3, 0, 0, 4],), [-3, 0, 4])),
    ),
    Kata(
        id="c-merge-sorted",
        level=4,
        language="c",
        family=FAMILY,
        name="mergeSorted",
        brief=(
            "a and b are each sorted. Write every number from both into out "
            "so that out is sorted too, and return how many you wrote. "
            "Numbers in both arrays appear twice."
        ),
        params=("a", "b"),
        types=("int[]", "int[]"),
        returns="int[]",
        example="mergeSorted({1, 4}, 2, {2, 3, 5}, 3, out) writes 1, 2, 3, 4, 5",
        hint=(
            "One index into each array. Take the smaller front each step. "
            "When one array runs out, copy the rest of the other - that "
            "last step is the one that gets forgotten."
        ),
        cases=(([1, 4], [2, 3, 5]), ([], []), ([], [1, 2]), ([3], []),
               ([1, 1], [1]), ([-5, 0, 5], [-6, 6]), ([1, 2, 3], [4, 5, 6]),
               ([4, 5, 6], [1, 2, 3])),
        solve=_merge_sorted,
        checks=((([1, 4], [2, 3, 5]), [1, 2, 3, 4, 5]), (([], []), []),
                (([], [1, 2]), [1, 2]), (([1, 1], [1]), [1, 1, 1]),
                (([-5, 0, 5], [-6, 6]), [-6, -5, 0, 5, 6])),
    ),
    Kata(
        id="c-is-anagram",
        level=5,
        language="c",
        family=FAMILY,
        name="isAnagram",
        brief=(
            "first and second hold only the lowercase letters a to z. Say "
            "whether one is a rearrangement of the other, using every "
            "letter exactly as many times. Two empty strings are."
        ),
        params=("first", "second"),
        types=("string", "string"),
        returns="bool",
        example='isAnagram("listen", "silent") is true',
        hint=(
            "int counts[26] = {0}; add one at counts[ch - 'a'] for each "
            "letter of first, take one away for each of second, then every "
            "counter must be back at 0. Different lengths never match."
        ),
        cases=(("listen", "silent"), ("", ""), ("a", "a"), ("a", ""), ("ab", "ba"),
               ("aab", "abb"), ("rat", "car"), ("abc", "abcd"), ("anagram", "nagaram")),
        solve=_is_anagram,
        checks=((("listen", "silent"), True), (("", ""), True), (("a", ""), False),
                (("aab", "abb"), False), (("abc", "abcd"), False)),
    ),
    Kata(
        id="c-second-largest",
        level=5,
        language="c",
        family=FAMILY,
        name="secondLargest",
        brief=(
            "Return the second largest different value in nums: in {5, 9, "
            "9} it is 5. When there are fewer than two different values, "
            "return INT_MIN from <limits.h>."
        ),
        params=("nums",),
        types=("int[]",),
        returns="int",
        example="secondLargest({3, 9, 4, 9}, 4) is 4",
        hint=(
            "Track two values in one pass: best and second, plus whether "
            "each has been seen yet. A new best pushes the old best down; "
            "a number equal to best changes nothing."
        ),
        cases=(([3, 9, 4, 9],), ([],), ([7],), ([2, 2, 2],), ([5, 9, 9],),
               ([-1, -5, -3],), ([1, 2],), ([2, 1],), ([10, 20, 30, 20, 10],)),
        solve=_second_largest,
        checks=((([3, 9, 4, 9],), 4), (([],), INT_MIN), (([2, 2, 2],), INT_MIN),
                (([5, 9, 9],), 5), (([-1, -5, -3],), -3), (([2, 1],), 1)),
    ),
)


C_ANSWERS_2: dict[str, str] = {
    "c-count-char": (
        "int countChar(const char *text, char c) {\n"
        "  int count = 0;\n"
        "  for (int i = 0; text[i] != '\\0'; i++) {\n"
        "    if (text[i] == c) {\n"
        "      count++;\n"
        "    }\n"
        "  }\n"
        "  return count;\n"
        "}\n"
    ),
    "c-total-length": (
        "#include <string.h>\n"
        "\n"
        "int totalLength(const char **words, int words_len) {\n"
        "  int total = 0;\n"
        "  for (int i = 0; i < words_len; i++) {\n"
        "    total += (int)strlen(words[i]);\n"
        "  }\n"
        "  return total;\n"
        "}\n"
    ),
    "c-is-power-of-two": (
        "#include <stdbool.h>\n"
        "\n"
        "bool isPowerOfTwo(int n) {\n"
        "  return n > 0 && (n & (n - 1)) == 0;\n"
        "}\n"
    ),
    "c-euclid-gcd": (
        "int euclidGcd(int a, int b) {\n"
        "  while (b != 0) {\n"
        "    int rest = a % b;\n"
        "    a = b;\n"
        "    b = rest;\n"
        "  }\n"
        "  return a;\n"
        "}\n"
    ),
    "c-fib-long": (
        "long long fibLong(int n) {\n"
        "  long long a = 0;\n"
        "  long long b = 1;\n"
        "  for (int i = 0; i < n; i++) {\n"
        "    long long next = a + b;\n"
        "    a = b;\n"
        "    b = next;\n"
        "  }\n"
        "  return a;\n"
        "}\n"
    ),
    "c-binary-search": (
        "int binarySearch(const int *nums, int nums_len, int target) {\n"
        "  int lo = 0;\n"
        "  int hi = nums_len - 1;\n"
        "  while (lo <= hi) {\n"
        "    int mid = lo + (hi - lo) / 2;\n"
        "    if (nums[mid] == target) {\n"
        "      return mid;\n"
        "    }\n"
        "    if (nums[mid] < target) {\n"
        "      lo = mid + 1;\n"
        "    } else {\n"
        "      hi = mid - 1;\n"
        "    }\n"
        "  }\n"
        "  return -1;\n"
        "}\n"
    ),
    "c-dedupe-sorted": (
        "int dedupeSorted(const int *nums, int nums_len, int *out) {\n"
        "  int count = 0;\n"
        "  for (int i = 0; i < nums_len; i++) {\n"
        "    if (i == 0 || nums[i] != nums[i - 1]) {\n"
        "      out[count] = nums[i];\n"
        "      count++;\n"
        "    }\n"
        "  }\n"
        "  return count;\n"
        "}\n"
    ),
    "c-merge-sorted": (
        "int mergeSorted(const int *a, int a_len, const int *b, int b_len, int *out) {\n"
        "  int i = 0;\n"
        "  int j = 0;\n"
        "  int n = 0;\n"
        "  while (i < a_len && j < b_len) {\n"
        "    if (a[i] <= b[j]) {\n"
        "      out[n++] = a[i++];\n"
        "    } else {\n"
        "      out[n++] = b[j++];\n"
        "    }\n"
        "  }\n"
        "  while (i < a_len) {\n"
        "    out[n++] = a[i++];\n"
        "  }\n"
        "  while (j < b_len) {\n"
        "    out[n++] = b[j++];\n"
        "  }\n"
        "  return n;\n"
        "}\n"
    ),
    "c-is-anagram": (
        "#include <stdbool.h>\n"
        "\n"
        "bool isAnagram(const char *first, const char *second) {\n"
        "  int counts[26] = {0};\n"
        "  int i = 0;\n"
        "  for (; first[i] != '\\0' && second[i] != '\\0'; i++) {\n"
        "    counts[first[i] - 'a']++;\n"
        "    counts[second[i] - 'a']--;\n"
        "  }\n"
        "  if (first[i] != second[i]) {\n"
        "    return false;\n"
        "  }\n"
        "  for (int k = 0; k < 26; k++) {\n"
        "    if (counts[k] != 0) {\n"
        "      return false;\n"
        "    }\n"
        "  }\n"
        "  return true;\n"
        "}\n"
    ),
    "c-second-largest": (
        "#include <limits.h>\n"
        "#include <stdbool.h>\n"
        "\n"
        "int secondLargest(const int *nums, int nums_len) {\n"
        "  bool have_best = false;\n"
        "  bool have_second = false;\n"
        "  int best = 0;\n"
        "  int second = 0;\n"
        "  for (int i = 0; i < nums_len; i++) {\n"
        "    int n = nums[i];\n"
        "    if (!have_best || n > best) {\n"
        "      if (have_best) {\n"
        "        second = best;\n"
        "        have_second = true;\n"
        "      }\n"
        "      best = n;\n"
        "      have_best = true;\n"
        "    } else if (n < best && (!have_second || n > second)) {\n"
        "      second = n;\n"
        "      have_second = true;\n"
        "    }\n"
        "  }\n"
        "  return have_second ? second : INT_MIN;\n"
        "}\n"
    ),
}


def _with_answers():
    from dataclasses import replace

    return tuple(replace(k, c_answer=C_ANSWERS_2[k.id]) for k in C_KATAS_2)


C_KATAS_2 = _with_answers()
