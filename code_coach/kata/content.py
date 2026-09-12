"""The first katas: text, numbers, and the things that catch people out.

Chosen against what the app already has rather than against a list of
famous problems. The LeetCode bank covers thirteen patterns — hash maps,
two pointers, sliding window, stacks, linked lists, binary search, the
two tree traversals, graphs, backtracking, heaps, topological sort and
dynamic programming — and those are interview shapes. What Codewars and
freeCodeCamp drill and this app did not is the other half: text you have
to take apart, numbers with a rule in them, and input that is trying to
be wrong.

Every kata's cases are chosen for the edges rather than the middle. An
empty string, a single element, a zero, a negative, a duplicate, a
boundary. That is the whole reason this mode exists: a print-based
exercise runs once on the input in the prompt, and an edge case you never
run is an edge case you never learn.

The answers are computed by the reference below each set, never written
out. The suite runs every reference through the same driver a student's
code goes through, so a reference that does not pass its own cases fails
the build.
"""

from __future__ import annotations

from code_coach.kata import Kata

# ── Text ─────────────────────────────────────────────────────


def _count_vowels(word: str) -> int:
    return sum(1 for c in word.lower() if c in "aeiou")


def _reverse_words(sentence: str) -> str:
    return " ".join(reversed(sentence.split()))


def _is_pangram(sentence: str) -> bool:
    letters = {c for c in sentence.lower() if c.isalpha()}
    return len(letters) == 26


def _to_snake(name: str) -> str:
    out = []
    for i, c in enumerate(name):
        if c.isupper() and i:
            out.append("_")
        out.append(c.lower())
    return "".join(out)


def _longest_word(sentence: str) -> str:
    words = sentence.split()
    if not words:
        return ""
    return max(words, key=len)


def _are_anagrams(one: str, two: str) -> bool:
    return sorted(one.lower()) == sorted(two.lower())


TEXT: tuple[Kata, ...] = (
    Kata(
        id="count-vowels",
        name="count_vowels",
        brief="Return how many vowels are in the word. Upper case counts.",
        params=("word",),
        family="Text",
        example='count_vowels("Apple") is 2',
        hint="Lower-casing first means one membership test instead of ten.",
        cases=(
            ("apple",), ("Apple",), ("",), ("xyz",), ("AEIOU",),
            ("rhythm",), ("Queueing",), ("a",), ("Y",), ("Mississippi",),
        ),
        solve=_count_vowels,
        checks=((("Mississippi",), 4), (("rhythm",), 0), (("AEIOU",), 5),
            (("",), 0), (("Y",), 0)),
    ),
    Kata(
        id="reverse-words",
        name="reverse_words",
        brief=(
            "Return the sentence with its words in reverse order, one space "
            "between each. The letters inside a word stay as they are."
        ),
        params=("sentence",),
        family="Text",
        example='reverse_words("one two three") is "three two one"',
        hint=(
            "split() with no argument drops the runs of spaces for you, "
            "which is the part that catches people out."
        ),
        cases=(
            ("one two three",), ("hello",), ("",), ("  padded  out  ",),
            ("a b",), ("the quick brown fox",), ("   ",),
            ("trailing space ",), (" leading space",), ("two  spaces",),
        ),
        solve=_reverse_words,
        checks=((("  padded  out  ",), "out padded"), (("a b",), "b a"),
            (("",), ""), (("   ",), "")),
    ),
    Kata(
        id="is-pangram",
        name="is_pangram",
        brief=(
            "Return True when the sentence uses every letter of the "
            "alphabet at least once, and False when it does not."
        ),
        params=("sentence",),
        family="Text",
        example='is_pangram("The quick brown fox jumps over the lazy dog") '
                "is True",
        hint="A set of the letters, and its size. Case does not count.",
        cases=(
            ("The quick brown fox jumps over the lazy dog",),
            ("Pack my box with five dozen liquor jugs",),
            ("hello world",),
            ("",),
            ("abcdefghijklmnopqrstuvwxyz",),
            ("ABCDEFGHIJKLMNOPQRSTUVWXYZ",),
            ("abcdefghijklmnopqrstuvwxy",),
            ("The five boxing wizards jump quickly!",),
            ("a" * 100,),
            ("Sphinx of black quartz, judge my vow",),
        ),
        solve=_is_pangram,
        checks=((("abcdefghijklmnopqrstuvwxy",), False),
            (("abcdefghijklmnopqrstuvwxyz",), True),
            (("",), False)),
    ),
    Kata(
        id="to-snake",
        name="to_snake",
        brief=(
            "Turn a camelCase name into snake_case: an underscore before "
            "each capital, and everything lower case."
        ),
        params=("name",),
        family="Text",
        example='to_snake("camelCase") is "camel_case"',
        hint=(
            "The first character is the one to be careful about — a "
            "capital there should not produce a leading underscore."
        ),
        cases=(
            ("camelCase",), ("alreadysnake",), ("",), ("A",),
            ("PascalCase",), ("aB",), ("oneTwoThree",), ("x",),
            ("HTTPServer",), ("getHTTPResponseCode",),
        ),
        solve=_to_snake,
        checks=((("HTTPServer",), "h_t_t_p_server"), (("aB",), "a_b"),
            (("",), ""), (("A",), "a")),
    ),
    Kata(
        id="longest-word",
        name="longest_word",
        brief=(
            "Return the longest word in the sentence. When two are equally "
            "long, return the one that comes first."
        ),
        params=("sentence",),
        family="Text",
        example='longest_word("one three go") is "three"',
        hint="max() with key=len already keeps the first of a tie.",
        cases=(
            ("one three go",), ("hello",), ("",), ("ab cd",),
            ("a bb ccc",), ("ccc bb a",), ("tie four five",),
            ("  spaced  words  here  ",), ("x",), ("equal equal",),
        ),
        solve=_longest_word,
        checks=((("tie four five",), "four"), (("a bb ccc",), "ccc"),
            (("",), ""), (("x",), "x")),
    ),
    Kata(
        id="are-anagrams",
        name="are_anagrams",
        brief=(
            "Return True when the two words use exactly the same letters, "
            "ignoring case, and False otherwise."
        ),
        params=("one", "two"),
        family="Text",
        example='are_anagrams("Listen", "Silent") is True',
        hint="Sorted letters are equal for an anagram and not for anything else.",
        cases=(
            ("listen", "silent"), ("Listen", "Silent"), ("", ""),
            ("a", "a"), ("a", "b"), ("abc", "cab"), ("abc", "abcd"),
            ("aab", "abb"), ("Dormitory", "dirtyroom"), ("night", "thing"),
        ),
        solve=_are_anagrams,
        checks=(((("aab", "abb")), False), ((("night", "thing")), True),
            ((("", "")), True), ((("a", "b")), False)),
    ),
)


# ── Numbers ──────────────────────────────────────────────────


def _digital_root(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    factor = 2
    while factor * factor <= n:
        if n % factor == 0:
            return False
        factor += 1
    return True


def _collatz_steps(n: int) -> int:
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def _sum_digits(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def _sort_odds(numbers: list) -> list:
    odds = sorted(n for n in numbers if n % 2 != 0)
    out = list(numbers)
    spare = iter(odds)
    for i, n in enumerate(out):
        if n % 2 != 0:
            out[i] = next(spare)
    return out


NUMBERS: tuple[Kata, ...] = (
    Kata(
        id="digital-root",
        name="digital_root",
        brief=(
            "Add the digits of the number, then add the digits of that, "
            "until one digit is left. Return it."
        ),
        params=("n",),
        family="Numbers",
        example="digital_root(942) is 6, because 9+4+2 is 15 and 1+5 is 6",
        hint="A while loop that keeps going while the number is more than 9.",
        cases=(
            (942,), (0,), (9,), (10,), (99,), (12345,), (100,),
            (999999999,), (1,), (18,),
        ),
        solve=_digital_root,
        checks=(((999999999,), 9), ((12345,), 6), ((100,), 1), ((10,), 1),
                ((9,), 9),
            ((0,), 0), ((1,), 1)),
    ),
    Kata(
        id="is-prime",
        name="is_prime",
        brief=(
            "Return True when the number is prime and False when it is "
            "not. One and everything below it are not prime."
        ),
        params=("n",),
        family="Numbers",
        example="is_prime(7) is True, is_prime(1) is False",
        hint=(
            "Nothing above the square root can be a factor unless "
            "something below it already was."
        ),
        cases=(
            (7,), (1,), (0,), (2,), (-7,), (9,), (97,), (100,),
            (7919,), (3,),
        ),
        solve=_is_prime,
        checks=(((-7,), False), ((97,), True), ((9,), False),
            ((0,), False), ((1,), False)),
    ),
    Kata(
        id="collatz-steps",
        name="collatz_steps",
        brief=(
            "Count the steps to reach 1: halve an even number, and treble "
            "an odd one and add one. Return how many steps it took."
        ),
        params=("n",),
        family="Numbers",
        example="collatz_steps(6) is 8",
        hint="One is zero steps, not one — you are already there.",
        cases=(
            (6,), (1,), (2,), (3,), (7,), (27,), (16,), (9,), (97,), (871,),
        ),
        solve=_collatz_steps,
        checks=(((3,), 7), ((7,), 16), ((2,), 1),
            ((1,), 0)),
    ),
    Kata(
        id="gcd",
        name="gcd",
        brief=(
            "Return the largest number that divides both, and 0 when both "
            "are 0."
        ),
        params=("a", "b"),
        family="Numbers",
        example="gcd(12, 18) is 6",
        hint=(
            "Euclid: replace the pair with (b, a % b) until the second is "
            "zero, and the first is the answer."
        ),
        cases=(
            (12, 18), (0, 0), (5, 0), (0, 5), (7, 13), (100, 75),
            (-12, 18), (270, 192), (1, 1), (17, 17),
        ),
        solve=_gcd,
        checks=(((270, 192), 6), ((-12, 18), 6), ((7, 13), 1),
            ((0, 0), 0), ((5, 0), 5)),
    ),
    Kata(
        id="sum-digits",
        name="sum_digits",
        brief=(
            "Add up the digits of the number. A negative number has the "
            "same answer as its positive."
        ),
        params=("n",),
        family="Numbers",
        example="sum_digits(1234) is 10",
        hint="The minus sign is not a digit, and int() will not add it up.",
        cases=(
            (1234,), (0,), (9,), (-1234,), (100,), (999,), (-7,),
            (1000000,), (5,), (86420,),
        ),
        solve=_sum_digits,
        checks=(((86420,), 20), ((-1234,), 10),
            ((0,), 0), ((-7,), 7)),
    ),
    Kata(
        id="sort-odds",
        name="sort_odds",
        brief=(
            "Sort only the odd numbers, leaving every even number where it "
            "was. Return the new list."
        ),
        params=("numbers",),
        family="Numbers",
        example="sort_odds([5, 8, 6, 3, 4]) is [3, 8, 6, 5, 4]",
        hint=(
            "Take the odds out, sort them, and put them back into the "
            "positions the odds were in."
        ),
        cases=(
            ([5, 8, 6, 3, 4],), ([],), ([2, 4, 6],), ([9, 7, 5],),
            ([1],), ([2],), ([7, 2, 9, 4, 1],), ([3, 3, 1],),
            ([10, 1, 20, 3, 30, 2],), ([-3, 4, -1],),
        ),
        solve=_sort_odds,
        checks=(((([7, 2, 9, 4, 1],)), [1, 2, 7, 4, 9]),
            ((([-3, 4, -1],)), [-3, 4, -1]),
            ((([],)), []), ((([2],)), [2])),
    ),
)


# ── Input that is trying to be wrong ─────────────────────────


def _luhn_valid(digits: str) -> bool:
    numbers = [int(c) for c in digits if c.isdigit()]
    if not numbers:
        return False
    total = 0
    for i, n in enumerate(reversed(numbers)):
        if i % 2:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _valid_ip(text: str) -> bool:
    parts = text.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or (len(part) > 1 and part[0] == "0"):
            return False
        if not 0 <= int(part) <= 255:
            return False
    return True


def _balanced(text: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list = []
    for c in text:
        if c in "([{":
            stack.append(c)
        elif c in pairs:
            if not stack or stack.pop() != pairs[c]:
                return False
    return not stack


VALIDATION: tuple[Kata, ...] = (
    Kata(
        id="luhn-valid",
        name="luhn_valid",
        brief=(
            "Return True when the digits pass the Luhn check: double every "
            "second digit from the right, subtract 9 from any result over "
            "9, and the total must divide by 10. Ignore anything that is "
            "not a digit. A string with no digits is not valid."
        ),
        params=("digits",),
        family="Validation",
        example='luhn_valid("4539 1488 0343 6467") is True',
        hint=(
            "Reverse first, then the ones to double are the odd positions, "
            "which is easier to get right than counting from the other end."
        ),
        cases=(
            ("4539 1488 0343 6467",), ("1234 5678 1234 5678",), ("",),
            ("0",), ("00",), ("abc",), ("79927398713",), ("79927398710",),
            ("4539-1488-0343-6467",), ("1",),
        ),
        solve=_luhn_valid,
        checks=((("79927398713",), True), (("79927398710",), False),
            (("",), False), (("0",), True)),
    ),
    Kata(
        id="valid-ip",
        name="valid_ip",
        brief=(
            "Return True when the text is four numbers separated by dots, "
            "each from 0 to 255, with no leading zeros and nothing else."
        ),
        params=("text",),
        family="Validation",
        example='valid_ip("192.168.0.1") is True, valid_ip("1.2.3.04") '
                "is False",
        hint=(
            "The leading zero is the rule everyone forgets, and the reason "
            "int() on its own is not enough."
        ),
        cases=(
            ("192.168.0.1",), ("0.0.0.0",), ("255.255.255.255",),
            ("256.1.1.1",), ("1.2.3",), ("1.2.3.4.5",), ("1.2.3.04",),
            ("",), ("1.2.3.-4",), ("01.2.3.4",),
        ),
        solve=_valid_ip,
        checks=((("1.2.3.04",), False), (("256.1.1.1",), False),
            (("01.2.3.4",), False),
            (("",), False)),
    ),
    Kata(
        id="balanced",
        name="balanced",
        brief=(
            "Return True when every bracket is closed by its own kind in "
            "the right order. Anything that is not a bracket is ignored."
        ),
        params=("text",),
        family="Validation",
        example='balanced("a(b[c]d)e") is True, balanced("(]") is False',
        hint=(
            "A stack: push an opener, and on a closer check the top is the "
            "one that matches before you pop it."
        ),
        cases=(
            ("a(b[c]d)e",), ("(]",), ("",), ("(",), (")",), ("()[]{}",),
            ("([)]",), ("{[()]}",), ("no brackets here",), ("((((",),
        ),
        solve=_balanced,
        checks=((("([)]",), False), (("{[()]}",), True), (("((((",), False),
            (("",), True), (("(",), False)),
    ),
)


KATAS: tuple[Kata, ...] = TEXT + NUMBERS + VALIDATION
