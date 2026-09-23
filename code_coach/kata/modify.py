"""Change it: working code, and a change request.

The missing step. The research model most of this app already follows
is PRIMM - predict, run, investigate, modify, make - and every stage had
a screen except modify. Predict and Trace are reading; Forms, Workbook
and LeetCode are making. Between them there was nothing where you take
a program that works and make it do something new, which is the thing a
developer on a team does on their first morning and almost every
morning after. Nobody starts from an empty file at work.

It is not the same exercise as Fix the bug, and the difference is the
whole design. A bug drill starts broken: the code is wrong, and you make
it right. Here the code is right - right for what it was asked to do
yesterday - and the request is what changed. So a drill here has to
prove four things, and the suite checks all four:

  the start works      it passes every case under the OLD requirement,
                       so you are changing working code, not fixing it
  there is a change    it fails at least one case under the new one
  keep what worked     some cases have the same answer before and after,
                       so a rewrite that breaks the old behaviour fails -
                       which is the habit a team actually needs
  the change is small  the model answer is a few lines away from the
                       start, because modifying means editing; a
                       drill whose answer is a rewrite is a kata in
                       disguise

`before` is the old requirement as a Python oracle, `solve` the new one.
Both are Python whatever the drill is written in, for the reason katas
give: the answers are strings, numbers and lists, which mean the same
thing in both languages. `after` is the model answer - the start with
the change made - and it is run through the driver like everything
else, so the answer on screen is one that has been seen to pass.
"""

from __future__ import annotations

import re

from code_coach.kata import Kata

PYTHON = "Change it"
JAVASCRIPT = "Change it: JavaScript"


# ── Python ───────────────────────────────────────────────────


def _greet_before(name: str) -> str:
    return "Hello, " + name + "!"


def _greet(name: str) -> str:
    return "Hello, " + (name or "friend") + "!"


def _grade_before(score: int) -> str:
    return "pass" if score >= 50 else "fail"


def _grade(score: int) -> str:
    if score >= 85:
        return "distinction"
    return "pass" if score >= 50 else "fail"


def _fizz_before(n: int) -> str:
    return "Fizz" if n % 3 == 0 else str(n)


def _fizz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


def _shipping_before(weight: int) -> int:
    return 5


def _shipping(weight: int) -> int:
    return 5 + (weight - 10) if weight > 10 else 5


def _count_words_before(text: str) -> int:
    return len(text.split())


def _count_words(text: str) -> int:
    return len([w for w in text.split() if w.lower() not in ("a", "an", "the")])


def _monogram_before(name: str) -> str:
    return "".join(part[0] for part in name.split())


def _monogram(name: str) -> str:
    return "".join(part[0].upper() + "." for part in name.split())


PYTHON_MODIFY: tuple[Kata, ...] = (
    Kata(
        id="mod-greet",
        name="greet",
        family=PYTHON,
        level=1,
        params=("name",),
        was="It greets whoever it is given: greet('Ada') is 'Hello, Ada!'.",
        brief="Change it so an empty name is greeted as a friend: "
              "greet('') should be 'Hello, friend!'.",
        example="greet('') → 'Hello, friend!'   greet('Ada') → 'Hello, Ada!'",
        hint="Only the empty name is different. Deal with it before the "
             "line that builds the greeting.",
        change="One new case, handled before the old line, so every name "
               "that already worked still goes through it unchanged.",
        cases=(("Ada",), ("",), ("Bo",), ("Grace Hopper",)),
        before=_greet_before,
        solve=_greet,
        start=(
            "def greet(name):\n"
            "    return \"Hello, \" + name + \"!\"\n"
        ),
        after=(
            "def greet(name):\n"
            "    if name == \"\":\n"
            "        name = \"friend\"\n"
            "    return \"Hello, \" + name + \"!\"\n"
        ),
        checks=((("",), "Hello, friend!"), (("Ada",), "Hello, Ada!")),
    ),
    Kata(
        id="mod-grade",
        name="grade",
        family=PYTHON,
        level=1,
        params=("score",),
        was="Scores of 50 and up pass; everything under 50 fails.",
        brief="Add a top grade: 85 or more is 'distinction'. Everything "
              "else stays exactly as it was.",
        example="grade(90) → 'distinction'   grade(60) → 'pass'",
        hint="Which test has to be asked first? The first one that "
             "matches is the one that answers.",
        change="The new test goes first. Put it after the 50 check and a "
               "score of 90 comes back as 'pass', because the first test "
               "that matches wins.",
        cases=((0,), (49,), (50,), (84,), (85,), (100,)),
        before=_grade_before,
        solve=_grade,
        start=(
            "def grade(score):\n"
            "    if score >= 50:\n"
            "        return \"pass\"\n"
            "    return \"fail\"\n"
        ),
        after=(
            "def grade(score):\n"
            "    if score >= 85:\n"
            "        return \"distinction\"\n"
            "    if score >= 50:\n"
            "        return \"pass\"\n"
            "    return \"fail\"\n"
        ),
        checks=(((85,), "distinction"), ((84,), "pass"), ((0,), "fail")),
    ),
    Kata(
        id="mod-fizz",
        name="fizz",
        family=PYTHON,
        level=2,
        params=("n",),
        was="Multiples of 3 say 'Fizz'; every other number is itself, as "
            "text.",
        brief="Multiples of 5 should now say 'Buzz', and multiples of both "
              "3 and 5 should say 'FizzBuzz'.",
        example="fizz(5) → 'Buzz'   fizz(15) → 'FizzBuzz'   fizz(7) → '7'",
        hint="15 is a multiple of 3 as well. Which question has to be "
             "asked before the others?",
        change="The both-case has to be tested before either one alone. "
               "Test for 3 first and 15 answers 'Fizz' and never gets "
               "any further.",
        cases=((1,), (3,), (5,), (7,), (10,), (15,), (30,)),
        before=_fizz_before,
        solve=_fizz,
        start=(
            "def fizz(n):\n"
            "    if n % 3 == 0:\n"
            "        return \"Fizz\"\n"
            "    return str(n)\n"
        ),
        after=(
            "def fizz(n):\n"
            "    if n % 15 == 0:\n"
            "        return \"FizzBuzz\"\n"
            "    if n % 3 == 0:\n"
            "        return \"Fizz\"\n"
            "    if n % 5 == 0:\n"
            "        return \"Buzz\"\n"
            "    return str(n)\n"
        ),
        checks=(((15,), "FizzBuzz"), ((5,), "Buzz"), ((1,), "1")),
    ),
    Kata(
        id="mod-shipping",
        name="shipping",
        family=PYTHON,
        level=2,
        params=("weight",),
        was="Every parcel costs a flat 5, whatever it weighs.",
        brief="Heavy parcels cost more now: over 10 kg, add 1 for every "
              "kilo past 10. Up to and including 10 kg, it is still 5.",
        example="shipping(10) → 5   shipping(11) → 6   shipping(25) → 20",
        hint="The ticket says 'over 10'. Is a 10 kg parcel over 10?",
        change="The boundary is the whole ticket: 10 kg is still the flat "
               "rate, so the test is 'more than 10', not 'from 10'.",
        cases=((0,), (1,), (10,), (11,), (25,)),
        before=_shipping_before,
        solve=_shipping,
        start=(
            "def shipping(weight):\n"
            "    return 5\n"
        ),
        after=(
            "def shipping(weight):\n"
            "    if weight > 10:\n"
            "        return 5 + (weight - 10)\n"
            "    return 5\n"
        ),
        checks=(((10,), 5), ((11,), 6), ((0,), 5)),
    ),
    Kata(
        id="mod-count-words",
        name="count_words",
        family=PYTHON,
        level=3,
        params=("text",),
        was="It counts the words in a piece of text, split on spaces.",
        brief="Stop counting the little words: 'a', 'an' and 'the' should "
              "not count, whether or not they start with a capital.",
        example="count_words('A cat and a dog') → 3",
        hint="'The' and 'the' have to be treated the same. What would make "
             "them equal before you compare?",
        change="Lower-casing each word before the comparison is the part "
               "that is easy to miss: 'The' is not in the list, 'the' is.",
        cases=(("",), ("the cat",), ("A cat and a dog",), ("hello world",),
               ("The end",)),
        before=_count_words_before,
        solve=_count_words,
        start=(
            "def count_words(text):\n"
            "    return len(text.split())\n"
        ),
        after=(
            "def count_words(text):\n"
            "    words = [w for w in text.split() if w.lower() not in (\"a\", \"an\", \"the\")]\n"
            "    return len(words)\n"
        ),
        checks=((("A cat and a dog",), 3), (("",), 0), (("the cat",), 1)),
    ),
    Kata(
        id="mod-monogram",
        name="monogram",
        family=PYTHON,
        level=3,
        params=("name",),
        was="It joins the first letter of each part of a name: "
            "'ada lovelace' gives 'al'.",
        brief="Initials should now be capitals with a dot after each one: "
              "'ada lovelace' becomes 'A.L.'",
        example="monogram('ada lovelace') → 'A.L.'",
        hint="Two things change about each letter, and both happen in the "
             "same place.",
        change="Two changes on one line - upper-case the letter, add the "
               "dot. An empty name still gives an empty string, because "
               "there are no parts to join.",
        cases=(("Ada Lovelace",), ("grace",), ("",),
               ("alan mathison turing",)),
        before=_monogram_before,
        solve=_monogram,
        start=(
            "def monogram(name):\n"
            "    return \"\".join(part[0] for part in name.split())\n"
        ),
        after=(
            "def monogram(name):\n"
            "    return \"\".join(part[0].upper() + \".\" for part in name.split())\n"
        ),
        checks=((("alan mathison turing",), "A.M.T."), (("",), "")),
    ),
)


# ── JavaScript ───────────────────────────────────────────────


def _pluralize_before(count: int, word: str) -> str:
    return f"{count} {word}s"


def _pluralize(count: int, word: str) -> str:
    return f"{count} {word}" + ("" if count == 1 else "s")


def _format_price_before(cents: int) -> str:
    return "$" + f"{cents / 100:.2f}"


def _format_price(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    return sign + "$" + f"{abs(cents) / 100:.2f}"


def _count_vowels_before(text: str) -> int:
    return sum(1 for ch in text if ch in "aeiou")


def _count_vowels(text: str) -> int:
    return sum(1 for ch in text if ch.lower() in "aeiou")


def _url_slug_before(title: str) -> str:
    return "-".join(title.lower().split(" "))


def _url_slug(title: str) -> str:
    return "-".join(re.sub(r"[^a-z0-9 ]", "", title.lower()).split(" "))


def _is_adult_before(age: int, country: str) -> bool:
    return age >= 18


def _is_adult(age: int, country: str) -> bool:
    return age >= (21 if country == "us" else 18)


def _word_lengths_before(words: list) -> list:
    return [len(w) for w in words]


def _word_lengths(words: list) -> list:
    return [len(w) for w in words if w != ""]


JAVASCRIPT_MODIFY: tuple[Kata, ...] = (
    Kata(
        id="mod-js-pluralize",
        name="pluralize",
        family=JAVASCRIPT,
        language="javascript",
        level=1,
        params=("count", "word"),
        was="It always adds an s: pluralize(3, 'cat') is '3 cats'.",
        brief="One amount is not plural: when count is 1, leave the s off. "
              "pluralize(1, 'cat') should be '1 cat'.",
        example="pluralize(1, 'cat') → '1 cat'   pluralize(0, 'cat') → '0 cats'",
        hint="Only one number is singular. What does English do with zero?",
        change="Zero is plural in English - '0 cats' - so the test is "
               "exactly 1, not 'less than 2'.",
        cases=((0, "cat"), (1, "cat"), (2, "dog"), (12, "book")),
        before=_pluralize_before,
        solve=_pluralize,
        start=(
            "function pluralize(count, word) {\n"
            "  return `${count} ${word}s`;\n"
            "}\n"
        ),
        after=(
            "function pluralize(count, word) {\n"
            "  if (count === 1) return `${count} ${word}`;\n"
            "  return `${count} ${word}s`;\n"
            "}\n"
        ),
        checks=(((1, "cat"), "1 cat"), ((0, "cat"), "0 cats")),
    ),
    Kata(
        id="mod-js-format-price",
        name="formatPrice",
        family=JAVASCRIPT,
        language="javascript",
        level=1,
        params=("cents",),
        was="It turns cents into dollars: formatPrice(350) is '$3.50'.",
        brief="Negative amounts are refunds, and the minus belongs before "
              "the dollar sign: -250 should be '-$2.50', not '$-2.50'.",
        example="formatPrice(-250) → '-$2.50'   formatPrice(350) → '$3.50'",
        hint="Format the size of the number, and put the sign where it "
             "belongs yourself.",
        change="Take the sign off, format the size, put the sign back in "
               "front. Formatting the negative number directly is what "
               "put the minus inside.",
        cases=((350,), (5,), (0,), (-250,), (199,)),
        before=_format_price_before,
        solve=_format_price,
        start=(
            "function formatPrice(cents) {\n"
            "  return \"$\" + (cents / 100).toFixed(2);\n"
            "}\n"
        ),
        after=(
            "function formatPrice(cents) {\n"
            "  const sign = cents < 0 ? \"-\" : \"\";\n"
            "  return sign + \"$\" + (Math.abs(cents) / 100).toFixed(2);\n"
            "}\n"
        ),
        checks=(((-250,), "-$2.50"), ((0,), "$0.00")),
    ),
    Kata(
        id="mod-js-count-vowels",
        name="countVowels",
        family=JAVASCRIPT,
        language="javascript",
        level=2,
        params=("text",),
        was="It counts the lower-case vowels in a string.",
        brief="Capital vowels should count too: 'Apple' has 2 vowels, "
              "not 1.",
        example="countVowels('Apple') → 2   countVowels('AEIOU') → 5",
        hint="You could list the capitals as well - or make each letter "
             "lower-case before you check it.",
        change="Lower-case the character you are testing, not the list you "
               "test against. One call in one place covers every capital.",
        cases=(("",), ("apple",), ("Apple",), ("AEIOU",), ("rhythm",),
               ("Hello World",)),
        before=_count_vowels_before,
        solve=_count_vowels,
        start=(
            "function countVowels(text) {\n"
            "  let count = 0;\n"
            "  for (const ch of text) {\n"
            "    if (\"aeiou\".includes(ch)) count++;\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        after=(
            "function countVowels(text) {\n"
            "  let count = 0;\n"
            "  for (const ch of text) {\n"
            "    if (\"aeiou\".includes(ch.toLowerCase())) count++;\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        checks=((("AEIOU",), 5), (("",), 0), (("Apple",), 2)),
    ),
    Kata(
        id="mod-js-url-slug",
        name="urlSlug",
        family=JAVASCRIPT,
        language="javascript",
        level=2,
        params=("title",),
        was="It lower-cases a title and joins the words with dashes: "
            "'Hello World' is 'hello-world'.",
        brief="Punctuation is getting into the links. Remove anything that "
              "is not a letter, a digit or a space, so 'Hello, World!' "
              "becomes 'hello-world'.",
        example="urlSlug('Hello, World!') → 'hello-world'",
        hint="A regular expression can remove every character that is not "
             "in a set. Where in the chain does it go?",
        change="The new step goes in the middle of the chain, after "
               "lower-casing - so the pattern only has to list lower-case "
               "letters.",
        cases=(("Hello World",), ("Hello, World!",), ("",), ("C3PO",),
               ("What's new",)),
        before=_url_slug_before,
        solve=_url_slug,
        start=(
            "function urlSlug(title) {\n"
            "  return title.toLowerCase().split(\" \").join(\"-\");\n"
            "}\n"
        ),
        after=(
            "function urlSlug(title) {\n"
            "  return title.toLowerCase().replace(/[^a-z0-9 ]/g, \"\").split(\" \").join(\"-\");\n"
            "}\n"
        ),
        checks=((("Hello, World!",), "hello-world"), (("",), "")),
    ),
    Kata(
        id="mod-js-is-adult",
        name="isAdult",
        family=JAVASCRIPT,
        language="javascript",
        level=3,
        params=("age", "country"),
        was="Anyone 18 or older is an adult.",
        brief="The legal age now depends on the country, passed as a second "
              "argument: for 'us' it is 21. Everywhere else it is still 18.",
        example="isAdult(20, 'us') → false   isAdult(20, 'uk') → true",
        hint="The function needs a second parameter. Then only one number "
             "changes, depending on it.",
        change="Adding a parameter is a change every caller has to hear "
               "about. Old callers that pass one argument still run in "
               "JavaScript - country is just undefined - which is why "
               "'everywhere else is 18' matters.",
        cases=((18, "uk"), (20, "us"), (21, "us"), (17, "fr"), (0, "us"),
               (30, "uk")),
        before=_is_adult_before,
        solve=_is_adult,
        start=(
            "function isAdult(age) {\n"
            "  return age >= 18;\n"
            "}\n"
        ),
        after=(
            "function isAdult(age, country) {\n"
            "  const limit = country === \"us\" ? 21 : 18;\n"
            "  return age >= limit;\n"
            "}\n"
        ),
        checks=(((20, "us"), False), ((0, "us"), False), ((18, "uk"), True)),
    ),
    Kata(
        id="mod-js-word-lengths",
        name="wordLengths",
        family=JAVASCRIPT,
        language="javascript",
        level=3,
        params=("words",),
        was="It gives back the length of every word in a list.",
        brief="Empty strings have crept into the list. Leave them out of "
              "the result entirely.",
        example="wordLengths(['', 'cat', '']) → [3]",
        hint="Take the empty words out first, then measure what is left.",
        change="Filter, then map. Filtering after the map would be "
               "filtering numbers, and a length of 0 is a different "
               "question from an empty word.",
        cases=(([],), (["a", "bb"],), (["", "cat", ""],), (["hello"],),
               (["", ""],)),
        before=_word_lengths_before,
        solve=_word_lengths,
        start=(
            "function wordLengths(words) {\n"
            "  return words.map((w) => w.length);\n"
            "}\n"
        ),
        after=(
            "function wordLengths(words) {\n"
            "  return words.filter((w) => w !== \"\").map((w) => w.length);\n"
            "}\n"
        ),
        checks=(((["", "cat", ""],), [3]), (([],), [])),
    ),
)

MODIFY: tuple[Kata, ...] = PYTHON_MODIFY + JAVASCRIPT_MODIFY
