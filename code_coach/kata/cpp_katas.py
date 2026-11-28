"""Forms in C++: small functions, written with the standard library.

The same exercise as every other language's forms - write the function, and
it is called with inputs you have not seen - through kata/cpp_harness.py,
which writes each case into the program as C++ literals and catches a thrown
exception per case. Types are the harness's: int, long long, double, bool,
string and vectors of those. An argument is passed as an lvalue, so a
function may take it by value, by const reference or by reference; the
harness compares each container before and after the call, so a function that
sorts the vector it was given fails even when its answer is right.

C++ has no "no answer" value in this subset, so where another language
returns None these katas say what stands in (0, an empty vector).

The oracle is Python, as for every kata; the worked answer is checked by
compiling it and running it through the C++ driver against it.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "C++"


def _sum_positive(nums):
    return sum(n for n in nums if n > 0)


def _count_vowels(text):
    return sum(1 for ch in text.lower() if ch in "aeiou")


def _doubled(nums):
    return [n * 2 for n in nums]


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def _reversed_words(text):
    return " ".join(reversed(text.split()))


def _running_total(nums):
    out, total = [], 0
    for n in nums:
        total += n
        out.append(total)
    return out


def _fizz(n):
    out = []
    for i in range(1, n + 1):
        out.append("FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i))
    return out


def _longest_word(text):
    best = ""
    for word in text.split():
        if len(word) > len(best):
            best = word
    return best


def _unique_sorted(nums):
    return sorted(set(nums))


def _average(nums):
    return sum(nums) / len(nums) if nums else 0.0


def _is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _is_palindrome(text):
    cleaned = [ch.lower() for ch in text if ch.isalnum()]
    return cleaned == cleaned[::-1]


def _first_repeat(nums):
    seen = set()
    for n in nums:
        if n in seen:
            return n
        seen.add(n)
    return 0


def _caesar(text, shift):
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _digit_sum(n):
    return sum(int(d) for d in str(abs(n)))


def _min_max(nums):
    return [min(nums), max(nums)] if nums else []


def _binary(n):
    return bin(n)[2:]


def _count_primes(n):
    return sum(1 for k in range(2, n + 1) if all(k % d for d in range(2, int(k ** 0.5) + 1)))


def _fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


CPP_KATAS: tuple[Kata, ...] = (
    Kata(
        id="cpp-sum-positive", level=1, language="cpp", family=FAMILY, name="sumPositive",
        brief="Add up only the numbers above zero. An empty vector totals 0.",
        params=("nums",), types=("vector<int>",), returns="int",
        example="sumPositive({3, -1, 4}) is 7",
        hint="A range-for over nums with a running total; add n only when n > 0.",
        cases=(([3, -1, 4],), ([],), ([-5, -2],), ([0, 1],), ([10, 20, -30],)),
        solve=_sum_positive,
        checks=((([3, -1, 4],), 7), (([],), 0), (([-5, -2],), 0)),
        cpp_answer=(
            "int sumPositive(const std::vector<int> &nums) {\n"
            "    int total = 0;\n"
            "    for (int n : nums) {\n"
            "        if (n > 0) total += n;\n"
            "    }\n"
            "    return total;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-vowel-count", level=1, language="cpp", family=FAMILY, name="vowelCount",
        brief="How many vowels (a, e, i, o, u, either case) are in the text?",
        params=("text",), types=("string",), returns="int",
        example='vowelCount("Hello") is 2',
        hint="Walk the characters; std::tolower((unsigned char)c) makes the case match, then look it up in std::string(\"aeiou\").",
        cases=(("Hello",), ("",), ("AEIOU",), ("rhythm",), ("Hello, World!",)),
        solve=_count_vowels,
        checks=((("Hello",), 2), (("rhythm",), 0), (("AEIOU",), 5), (("",), 0)),
        cpp_answer=(
            "int vowelCount(const std::string &text) {\n"
            "    int count = 0;\n"
            "    for (char c : text) {\n"
            "        char lower = (char)std::tolower((unsigned char)c);\n"
            "        if (lower == 'a' || lower == 'e' || lower == 'i' || lower == 'o' || lower == 'u') count++;\n"
            "    }\n"
            "    return count;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-doubled-all", level=1, language="cpp", family=FAMILY, name="doubledAll",
        brief="A new vector with every number doubled. Leave the vector you were given alone.",
        params=("nums",), types=("vector<int>",), returns="vector<int>",
        example="doubledAll({1, 2, 3}) is {2, 4, 6}",
        hint="Build a vector<int> out, push_back(n * 2) for each n, and return it.",
        cases=(([1, 2, 3],), ([],), ([-4],), ([0, 5, 10],)),
        solve=_doubled,
        checks=((([1, 2, 3],), [2, 4, 6]), (([],), []), (([-4],), [-8])),
        cpp_answer=(
            "std::vector<int> doubledAll(const std::vector<int> &nums) {\n"
            "    std::vector<int> out;\n"
            "    for (int n : nums) out.push_back(n * 2);\n"
            "    return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-clamp", level=1, language="cpp", family=FAMILY, name="clampTo",
        brief="Keep x between lo and hi: below lo gives lo, above hi gives hi, otherwise x.",
        params=("x", "lo", "hi"), types=("int", "int", "int"), returns="int",
        example="clampTo(15, 0, 10) is 10",
        hint="std::max(lo, std::min(hi, x)) does it in one line - or two ifs.",
        cases=((5, 0, 10), (15, 0, 10), (-3, 0, 10), (0, 0, 0), (-8, -5, -1)),
        solve=_clamp,
        checks=(((15, 0, 10), 10), ((-3, 0, 10), 0), ((5, 0, 10), 5)),
        cpp_answer=(
            "int clampTo(int x, int lo, int hi) {\n"
            "    if (x < lo) return lo;\n"
            "    if (x > hi) return hi;\n"
            "    return x;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-reversed-words", level=2, language="cpp", family=FAMILY, name="reversedWords",
        brief="The words of the text in reverse order, joined by single spaces.",
        params=("text",), types=("string",), returns="string",
        example='reversedWords("one two three") is "three two one"',
        hint="An std::istringstream read with >> skips extra spaces and hands you one word at a time; put each at the front of a vector (or collect and walk it backwards).",
        cases=(("one two three",), ("",), ("single",), ("  lots   of space ",)),
        solve=_reversed_words,
        checks=((("one two three",), "three two one"), (("",), ""), (("  lots   of space ",), "space of lots")),
        cpp_answer=(
            "std::string reversedWords(const std::string &text) {\n"
            "    std::istringstream in(text);\n"
            "    std::vector<std::string> words;\n"
            "    std::string word;\n"
            "    while (in >> word) words.push_back(word);\n"
            "    std::string out;\n"
            "    for (size_t i = words.size(); i > 0; i--) {\n"
            "        if (!out.empty()) out += ' ';\n"
            "        out += words[i - 1];\n"
            "    }\n"
            "    return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-running-total", level=2, language="cpp", family=FAMILY, name="prefixTotals",
        brief="Each position holds the total of every number up to and including it.",
        params=("nums",), types=("vector<int>",), returns="vector<int>",
        example="prefixTotals({1, 2, 3}) is {1, 3, 6}",
        hint="Keep an int total; add each number, then push_back the total.",
        cases=(([1, 2, 3],), ([],), ([5],), ([2, -2, 2],)),
        solve=_running_total,
        checks=((([1, 2, 3],), [1, 3, 6]), (([2, -2, 2],), [2, 0, 2]), (([],), [])),
        cpp_answer=(
            "std::vector<int> prefixTotals(const std::vector<int> &nums) {\n"
            "    std::vector<int> out;\n"
            "    int total = 0;\n"
            "    for (int n : nums) {\n"
            "        total += n;\n"
            "        out.push_back(total);\n"
            "    }\n"
            "    return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-fizz-buzz", level=2, language="cpp", family=FAMILY, name="fizzBuzz",
        brief="From 1 to n: \"Fizz\" for multiples of 3, \"Buzz\" for 5, \"FizzBuzz\" for both, otherwise the number.",
        params=("n",), types=("int",), returns="vector<string>",
        example='fizzBuzz(5) is {"1", "2", "Fizz", "4", "Buzz"}',
        hint="Test 15 first. std::to_string(i) turns the number into a string.",
        cases=((5,), (0,), (15,), (3,)),
        solve=_fizz,
        checks=(((5,), ["1", "2", "Fizz", "4", "Buzz"]), ((0,), []),),
        cpp_answer=(
            "std::vector<std::string> fizzBuzz(int n) {\n"
            "    std::vector<std::string> out;\n"
            "    for (int i = 1; i <= n; i++) {\n"
            "        if (i % 15 == 0) out.push_back(\"FizzBuzz\");\n"
            "        else if (i % 3 == 0) out.push_back(\"Fizz\");\n"
            "        else if (i % 5 == 0) out.push_back(\"Buzz\");\n"
            "        else out.push_back(std::to_string(i));\n"
            "    }\n"
            "    return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-longest-word", level=2, language="cpp", family=FAMILY, name="longestOf",
        brief="The longest word in the text (the first one if several tie), or an empty string if there are no words.",
        params=("text",), types=("string",), returns="string",
        example='longestOf("a quick brown fox") is "quick"',
        hint="Read words with an istringstream and keep the best so far; replace it only when a word is strictly longer.",
        cases=(("a quick brown fox",), ("",), ("hi",), ("one two six",), ("  spaced   out words  ",)),
        solve=_longest_word,
        checks=((("a quick brown fox",), "quick"), (("",), ""), (("one two six",), "one")),
        cpp_answer=(
            "std::string longestOf(const std::string &text) {\n"
            "    std::istringstream in(text);\n"
            "    std::string word, best;\n"
            "    while (in >> word) {\n"
            "        if (word.size() > best.size()) best = word;\n"
            "    }\n"
            "    return best;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-unique-sorted", level=2, language="cpp", family=FAMILY, name="distinctAscending",
        brief="The distinct numbers, smallest first. Do not change the vector you were given.",
        params=("nums",), types=("vector<int>",), returns="vector<int>",
        example="distinctAscending({3, 1, 3, 2, 1}) is {1, 2, 3}",
        hint="Copy the input into an std::set<int> - it keeps each value once, in order - then copy the set back out.",
        cases=(([3, 1, 3, 2, 1],), ([],), ([7],), ([-2, -2, 0, -5],), ([4, 4, 4],)),
        solve=_unique_sorted,
        checks=((([3, 1, 3, 2, 1],), [1, 2, 3]), (([],), []), (([-2, -2, 0, -5],), [-5, -2, 0])),
        cpp_answer=(
            "std::vector<int> distinctAscending(const std::vector<int> &nums) {\n"
            "    std::set<int> seen(nums.begin(), nums.end());\n"
            "    return std::vector<int>(seen.begin(), seen.end());\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-average", level=2, language="cpp", family=FAMILY, name="averageOf",
        brief="The average as a double. An empty vector averages 0.",
        params=("nums",), types=("vector<int>",), returns="double",
        example="averageOf({1, 2}) is 1.5",
        hint="Add up into a long long or double, then divide by (double)nums.size() - dividing two ints would throw the .5 away.",
        cases=(([1, 2],), ([],), ([4, 4, 4],), ([-3, 3],), ([1, 2, 2],)),
        solve=_average,
        checks=((([1, 2],), 1.5), (([],), 0.0), (([-3, 3],), 0.0)),
        cpp_answer=(
            "double averageOf(const std::vector<int> &nums) {\n"
            "    if (nums.empty()) return 0.0;\n"
            "    double total = 0;\n"
            "    for (int n : nums) total += n;\n"
            "    return total / (double)nums.size();\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-leap-year", level=2, language="cpp", family=FAMILY, name="isLeapYear",
        brief="Is the year a leap year? Every 4th year, except centuries, except every 400th.",
        params=("year",), types=("int",), returns="bool",
        example="isLeapYear(1900) is false; isLeapYear(2000) is true",
        hint="year % 4 == 0 && (year % 100 != 0 || year % 400 == 0).",
        cases=((2024,), (1900,), (2000,), (2023,), (1,), (0,)),
        solve=_is_leap,
        checks=(((1900,), False), ((2000,), True), ((2023,), False), ((1,), False), ((0,), True)),
        cpp_answer=(
            "bool isLeapYear(int year) {\n"
            "    return year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-is-palindrome", level=3, language="cpp", family=FAMILY, name="isPalindrome",
        brief="Does it read the same both ways, ignoring case and anything that is not a letter or digit?",
        params=("text",), types=("string",), returns="bool",
        example='isPalindrome("A man, a plan, a canal: Panama") is true',
        hint="Build a cleaned std::string of the lower-cased alphanumerics (std::isalnum, std::tolower); compare it with its reverse.",
        cases=(("A man, a plan, a canal: Panama",), ("",), ("cpp",), ("No lemon, no melon",), ("ab",)),
        solve=_is_palindrome,
        checks=((("A man, a plan, a canal: Panama",), True), (("cpp",), False), (("",), True)),
        cpp_answer=(
            "bool isPalindrome(const std::string &text) {\n"
            "    std::string cleaned;\n"
            "    for (char c : text) {\n"
            "        if (std::isalnum((unsigned char)c)) cleaned += (char)std::tolower((unsigned char)c);\n"
            "    }\n"
            "    std::string backwards(cleaned.rbegin(), cleaned.rend());\n"
            "    return cleaned == backwards;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-first-repeat", level=3, language="cpp", family=FAMILY, name="firstRepeat",
        brief="The first number that has already appeared earlier in the vector, or 0 if nothing repeats. (The numbers are never 0.)",
        params=("nums",), types=("vector<int>",), returns="int",
        example="firstRepeat({3, 1, 4, 1, 3}) is 1",
        hint="An std::unordered_set remembers what you have seen: insert(n).second is false when n was already there.",
        cases=(([3, 1, 4, 1, 3],), ([],), ([1, 2, 3],), ([7, 7],), ([5, 6, 6, 5],)),
        solve=_first_repeat,
        checks=((([3, 1, 4, 1, 3],), 1), (([1, 2, 3],), 0), (([5, 6, 6, 5],), 6), (([],), 0)),
        cpp_answer=(
            "int firstRepeat(const std::vector<int> &nums) {\n"
            "    std::unordered_set<int> seen;\n"
            "    for (int n : nums) {\n"
            "        if (!seen.insert(n).second) return n;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-digit-sum", level=3, language="cpp", family=FAMILY, name="digitTotal",
        brief="Add up the digits of the number, ignoring any minus sign.",
        params=("n",), types=("int",), returns="int",
        example="digitTotal(-1234) is 10",
        hint="Make n non-negative first, then peel digits off with n % 10 and n / 10 until nothing is left.",
        cases=((1234,), (0,), (-1234,), (7,), (1000,), (99999,)),
        solve=_digit_sum,
        checks=(((1234,), 10), ((0,), 0), ((-1234,), 10), ((1000,), 1)),
        cpp_answer=(
            "int digitTotal(int n) {\n"
            "    if (n < 0) n = -n;\n"
            "    int total = 0;\n"
            "    while (n > 0) {\n"
            "        total += n % 10;\n"
            "        n /= 10;\n"
            "    }\n"
            "    return total;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-caesar", level=3, language="cpp", family=FAMILY, name="rotateLetters",
        brief="Shift every small letter a-z forward by shift places, wrapping z round to a. Anything else stays.",
        params=("text", "shift"), types=("string", "int"), returns="string",
        example='rotateLetters("abc xyz", 2) is "cde zab"',
        hint="For a small letter: 'a' + (c - 'a' + shift) % 26. Build the answer in a copy of the string.",
        cases=(("abc xyz", 2), ("", 5), ("hello, world!", 13), ("zzz", 1), ("Abc", 1), ("abc", 0)),
        solve=_caesar,
        checks=((("abc xyz", 2), "cde zab"), (("zzz", 1), "aaa"), (("Abc", 1), "Acd"), (("", 5), "")),
        cpp_answer=(
            "std::string rotateLetters(const std::string &text, int shift) {\n"
            "    std::string out = text;\n"
            "    for (char &c : out) {\n"
            "        if (c >= 'a' && c <= 'z') c = (char)('a' + (c - 'a' + shift) % 26);\n"
            "    }\n"
            "    return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-gcd", level=3, language="cpp", family=FAMILY, name="gcdOf",
        brief="The greatest common divisor of two non-negative numbers. gcdOf(n, 0) is n.",
        params=("a", "b"), types=("long long", "long long"), returns="long long",
        example="gcdOf(12, 18) is 6",
        hint="Euclid: while b is not 0, replace (a, b) with (b, a % b). What is left in a is the answer.",
        cases=((12, 18), (7, 0), (0, 5), (17, 5), (1, 1), (1000000007, 998244353), (84, 36)),
        solve=_gcd,
        checks=(((12, 18), 6), ((7, 0), 7), ((0, 5), 5), ((1, 1), 1)),
        cpp_answer=(
            "long long gcdOf(long long a, long long b) {\n"
            "    while (b != 0) {\n"
            "        long long rest = a % b;\n"
            "        a = b;\n"
            "        b = rest;\n"
            "    }\n"
            "    return a;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-min-max", level=4, language="cpp", family=FAMILY, name="minMax",
        brief="The smallest and largest numbers as a two-element vector {smallest, largest}; an empty vector for an empty input.",
        params=("nums",), types=("vector<int>",), returns="vector<int>",
        example="minMax({3, 9, 2}) is {2, 9}",
        hint="One pass: start both at nums[0] (after checking empty()), then widen them as you go. std::min_element and max_element also work.",
        cases=(([3, 9, 2],), ([],), ([4],), ([-1, -5, 0],), ([6, 6],)),
        solve=_min_max,
        checks=((([3, 9, 2],), [2, 9]), (([],), []), (([4],), [4, 4]), (([-1, -5, 0],), [-5, 0])),
        cpp_answer=(
            "std::vector<int> minMax(const std::vector<int> &nums) {\n"
            "    if (nums.empty()) return {};\n"
            "    int lo = nums[0], hi = nums[0];\n"
            "    for (int n : nums) {\n"
            "        lo = std::min(lo, n);\n"
            "        hi = std::max(hi, n);\n"
            "    }\n"
            "    return {lo, hi};\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-binary", level=4, language="cpp", family=FAMILY, name="toBinary",
        brief="The number written in binary, with no leading zeros. Zero is \"0\". The number is never negative.",
        params=("n",), types=("int",), returns="string",
        example='toBinary(10) is "1010"',
        hint="Peel off n % 2 and n / 2 until n is 0, adding each bit to the FRONT of the string (or reverse at the end).",
        cases=((10,), (0,), (1,), (255,), (1024,), (2,)),
        solve=_binary,
        checks=(((10,), "1010"), ((0,), "0"), ((1,), "1"), ((255,), "11111111")),
        cpp_answer=(
            "std::string toBinary(int n) {\n"
            "    if (n == 0) return \"0\";\n"
            "    std::string out;\n"
            "    while (n > 0) {\n"
            "        out.insert(out.begin(), (char)('0' + n % 2));\n"
            "        n /= 2;\n"
            "    }\n"
            "    return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-count-primes", level=4, language="cpp", family=FAMILY, name="countPrimes",
        brief="How many prime numbers are there from 2 up to and including n?",
        params=("n",), types=("int",), returns="int",
        example="countPrimes(10) is 4 (2, 3, 5, 7)",
        hint="Sieve of Eratosthenes: a vector<bool> of n + 1 flags; for each prime p, cross off p * p, p * p + p, ...",
        cases=((10,), (0,), (1,), (2,), (30,), (100,), (-5,)),
        solve=_count_primes,
        checks=(((10,), 4), ((1,), 0), ((2,), 1), ((100,), 25), ((-5,), 0)),
        cpp_answer=(
            "int countPrimes(int n) {\n"
            "    if (n < 2) return 0;\n"
            "    std::vector<bool> composite(n + 1, false);\n"
            "    int count = 0;\n"
            "    for (int p = 2; p <= n; p++) {\n"
            "        if (composite[p]) continue;\n"
            "        count++;\n"
            "        for (long long m = (long long)p * p; m <= n; m += p) composite[m] = true;\n"
            "    }\n"
            "    return count;\n"
            "}\n"
        ),
    ),
    Kata(
        id="cpp-fibonacci", level=4, language="cpp", family=FAMILY, name="fibAt",
        brief="The n-th Fibonacci number, starting 0, 1, 1, 2, 3, 5 (so fibAt(0) is 0). n is at most 90.",
        params=("n",), types=("int",), returns="long long",
        example="fibAt(10) is 55",
        hint="Loop n times keeping the last two values; they outgrow int past n = 46, which is why this returns long long.",
        cases=((10,), (0,), (1,), (2,), (50,), (90,)),
        solve=_fib,
        checks=(((10,), 55), ((0,), 0), ((1,), 1), ((50,), 12586269025)),
        cpp_answer=(
            "long long fibAt(int n) {\n"
            "    long long a = 0, b = 1;\n"
            "    for (int i = 0; i < n; i++) {\n"
            "        long long next = a + b;\n"
            "        a = b;\n"
            "        b = next;\n"
            "    }\n"
            "    return a;\n"
            "}\n"
        ),
    ),
)
