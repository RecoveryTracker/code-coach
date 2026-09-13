"""Katas in JavaScript: the shapes a vanilla app is actually made of.

Chosen against real work rather than against a list of famous problems.
An app without a framework spends its time turning data into other data
and text into other text — reshaping what came back from a fetch,
counting things, picking the fields a template wants, making a heading
out of a title. None of it is difficult and all of it is easy to get
subtly wrong, which is what a kata is for.

Two rules carry over from the Python set and one is new.

The oracle is still Python. `solve` computes what each case should
produce, and the expected values — numbers, strings, arrays, plain
objects — mean the same in both languages, so one implementation of the
truth is guarded by the same hand-written checks that guard everything
else. What changes is the driver, and that Show answer hands over
`js_answer` instead.

Which means `js_answer` has to agree with a Python function, and the
suite proves it does by running it: the JavaScript goes through the same
driver a student's code goes through and has to pass every case. A
reference that agreed with itself and not with the oracle would fail
there.

And nothing here may modify what it was handed. That is the rule the
marker enforces everywhere, and it matters more in this language: an
array passed into a function is the caller's array, `sort` and `reverse`
and `splice` all change it in place, and the answer can be perfectly
right while the page behind it is wrong.
"""

from __future__ import annotations

from code_coach.kata import Kata

# ── Arrays and objects ───────────────────────────────────────


def _unique_of(items: list) -> list:
    seen: list = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def _count_by(words: list) -> dict:
    counts: dict = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def _flatten_once(rows: list) -> list:
    out: list = []
    for row in rows:
        out.extend(row)
    return out


def _pick_keys(record: dict, keys: list) -> dict:
    return {k: record[k] for k in keys if k in record}


def _sorted_desc(numbers: list) -> list:
    return sorted(numbers, reverse=True)


SHAPES: tuple[Kata, ...] = (
    Kata(
        id="js-unique-of",
        level=1,
        language="javascript",
        name="uniqueOf",
        brief=(
            "Return a new array with the duplicates removed, keeping the "
            "first time each value appeared. The array you were given "
            "must not change."
        ),
        params=("items",),
        family="JavaScript",
        example="uniqueOf([1, 2, 1]) is [1, 2]",
        hint=(
            "A Set keeps insertion order and de-duplicates in one step, "
            "and spreading it back out gives you an array again."
        ),
        cases=(
            ([1, 2, 1],), ([],), ([1],), ([1, 1, 1],), ([3, 2, 1],),
            ([0, 0, 1],), ([-1, -1, 2],), (["a", "b", "a"],),
            ([2, 1, 2, 1],), ([5, 4, 3, 2, 1],),
        ),
        solve=_unique_of,
        checks=(
            ((([1, 2, 1],)), [1, 2]), ((([],)), []), ((([1],)), [1]),
            ((([1, 1, 1],)), [1]), ((([-1, -1, 2],)), [-1, 2]),
        ),
        js_answer="function uniqueOf(items) {\n  return [...new Set(items)];\n}",
    ),
    Kata(
        id="js-flatten-once",
        level=2,
        language="javascript",
        name="flattenOnce",
        brief=(
            "Join the rows into one array, one level deep only. No rows "
            "gives an empty array."
        ),
        params=("rows",),
        family="JavaScript",
        example="flattenOnce([[1, 2], [3]]) is [1, 2, 3]",
        hint=(
            "flat() with no argument goes exactly one level, which is "
            "what is wanted here — flat(Infinity) would go all the way."
        ),
        cases=(
            ([[1, 2], [3]],), ([],), ([[]],), ([[1]],),
            ([[], [1], []],), ([[1], [2], [3]],), ([[0, 0]],),
            ([[-1], [2]],), ([[1, 2, 3]],), ([[1], []],),
        ),
        solve=_flatten_once,
        checks=(
            ((([[1, 2], [3]],)), [1, 2, 3]), ((([],)), []),
            ((([[]],)), []), ((([[1]],)), [1]),
            ((([[], [1], []],)), [1]),
        ),
        js_answer="function flattenOnce(rows) {\n  return rows.flat();\n}",
    ),
    Kata(
        id="js-count-by",
        level=3,
        language="javascript",
        name="countBy",
        brief=(
            "Return an object counting how many times each word appears, "
            "with the keys in the order the words were first seen. No "
            "words gives an empty object."
        ),
        params=("words",),
        family="JavaScript",
        example='countBy(["a", "b", "a"]) is { a: 2, b: 1 }',
        hint=(
            "Reading a key that is not there gives undefined, and adding "
            "one to undefined gives NaN — so the nought has to come from "
            "somewhere. `(counts[w] ?? 0) + 1` is the usual way."
        ),
        cases=(
            (["a", "b", "a"],), ([],), (["x"],), (["a", "a", "a"],),
            (["b", "a"],), (["one", "two", "one", "three"],),
            (["z", "z", "y", "y"],), (["q"],), (["a", "b", "c"],),
            (["hi", "hi"],),
        ),
        solve=_count_by,
        checks=(
            (((["a", "b", "a"],)), {"a": 2, "b": 1}),
            ((([],)), {}),
            (((["x"],)), {"x": 1}),
            (((["a", "a", "a"],)), {"a": 3}),
            (((["b", "a"],)), {"b": 1, "a": 1}),
        ),
        js_answer=(
            "function countBy(words) {\n"
            "  const counts = {};\n"
            "  for (const word of words) {\n"
            "    counts[word] = (counts[word] ?? 0) + 1;\n"
            "  }\n"
            "  return counts;\n"
            "}"
        ),
    ),
    Kata(
        id="js-pick-keys",
        level=3,
        language="javascript",
        name="pickKeys",
        brief=(
            "Return a new object holding only the named keys, in the "
            "order they were named. A key the record has not got is left "
            "out rather than set to undefined."
        ),
        params=("record", "keys"),
        family="JavaScript",
        example='pickKeys({ a: 1, b: 2 }, ["a"]) is { a: 1 }',
        hint=(
            "`in` asks whether the key exists; reading it and testing the "
            "value cannot tell a missing key from one holding undefined "
            "or nought."
        ),
        cases=(
            ({"a": 1, "b": 2}, ["a"]),
            ({}, []),
            ({"a": 1}, []),
            ({}, ["a"]),
            ({"a": 1, "b": 2}, ["b", "a"]),
            ({"a": 0}, ["a"]),
            ({"a": 1, "b": 2, "c": 3}, ["a", "c"]),
            ({"a": 1}, ["a", "zz"]),
            ({"name": "ada", "age": 36}, ["name"]),
            ({"a": -1}, ["a"]),
        ),
        solve=_pick_keys,
        checks=(
            (({"a": 1, "b": 2}, ["a"]), {"a": 1}),
            (({}, []), {}),
            (({}, ["a"]), {}),
            (({"a": 0}, ["a"]), {"a": 0}),
            (({"a": 1}, ["a", "zz"]), {"a": 1}),
            (({"a": 1, "b": 2}, ["b", "a"]), {"b": 2, "a": 1}),
        ),
        js_answer=(
            "function pickKeys(record, keys) {\n"
            "  const out = {};\n"
            "  for (const key of keys) {\n"
            "    if (key in record) out[key] = record[key];\n"
            "  }\n"
            "  return out;\n"
            "}"
        ),
    ),
    Kata(
        id="js-sorted-desc",
        level=2,
        language="javascript",
        name="sortedDesc",
        brief=(
            "Return a new array of the numbers, largest first. The array "
            "you were given must not change."
        ),
        params=("numbers",),
        family="JavaScript",
        example="sortedDesc([1, 3, 2]) is [3, 2, 1]",
        hint=(
            "sort changes the array in place and compares as text unless "
            "you give it a comparator. Both of those have to be dealt "
            "with, and a copy is how the first one is."
        ),
        cases=(
            ([1, 3, 2],), ([],), ([1],), ([2, 2],), ([-1, 1],),
            ([10, 9, 100],), ([0, -5],), ([5, 5, 4],), ([1, 2, 3],),
            ([-3, -1, -2],),
        ),
        solve=_sorted_desc,
        checks=(
            ((([1, 3, 2],)), [3, 2, 1]), ((([],)), []), ((([1],)), [1]),
            ((([-1, 1],)), [1, -1]),
            # The one that catches sorting as text: 100 is not smallest.
            ((([10, 9, 100],)), [100, 10, 9]),
        ),
        js_answer=(
            "function sortedDesc(numbers) {\n"
            "  return [...numbers].sort((a, b) => b - a);\n"
            "}"
        ),
    ),
)


# ── Text ─────────────────────────────────────────────────────


def _title_case(sentence: str) -> str:
    return " ".join(
        word[0].upper() + word[1:] if word else word
        for word in sentence.split(" ")
    )


def _truncate(text: str, most: int) -> str:
    if len(text) <= most:
        return text
    if most <= 1:
        return "…"[:most]
    return text[:most - 1] + "…"


def _slugify(text: str) -> str:
    kept = [
        c.lower() if c.isalnum() else "-"
        for c in text.strip()
    ]
    slug = "".join(kept)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


TEXT: tuple[Kata, ...] = (
    Kata(
        id="js-title-case",
        level=2,
        language="javascript",
        name="titleCase",
        brief=(
            "Capitalise the first letter of each word, leaving the rest "
            "of each word as it was. Words are separated by single "
            "spaces, and the spacing must come back unchanged."
        ),
        params=("sentence",),
        family="JavaScript",
        example='titleCase("hello there") is "Hello There"',
        hint=(
            "split(' ') rather than split(), because the spacing has to "
            "survive — and an empty piece between two spaces has no "
            "first letter to take."
        ),
        cases=(
            ("hello there",), ("",), ("a",), ("hello",),
            ("ada lovelace",), ("ALL CAPS",), ("mixed Case here",),
            ("x y z",), ("1st place",), ("two  spaces",),
        ),
        solve=_title_case,
        checks=(
            (("hello there",), "Hello There"), (("",), ""),
            (("a",), "A"), (("1st place",), "1st Place"),
            (("two  spaces",), "Two  Spaces"),
        ),
        js_answer=(
            "function titleCase(sentence) {\n"
            '  return sentence\n'
            '    .split(" ")\n'
            "    .map((word) => (word ? word[0].toUpperCase() + word.slice(1) : word))\n"
            '    .join(" ");\n'
            "}"
        ),
    ),
    Kata(
        id="js-truncate",
        level=3,
        language="javascript",
        name="truncate",
        brief=(
            "Shorten the text to at most `most` characters. If it is "
            "already short enough return it unchanged; otherwise cut it "
            "and put a single ellipsis character on the end, so that the "
            "whole thing is exactly `most` characters long."
        ),
        params=("text", "most"),
        family="JavaScript",
        example='truncate("hello", 4) is "hel…"',
        hint=(
            "The ellipsis takes one of the characters you are allowed, so "
            "the cut is at most minus one — and `most` of nought or one "
            "leaves no room for anything else."
        ),
        cases=(
            ("hello", 4), ("hi", 5), ("", 3), ("hello", 5), ("hello", 1),
            ("hello", 0), ("abc", 2), ("a", 1), ("hello world", 8),
            ("abc", 3),
        ),
        solve=_truncate,
        checks=(
            (("hello", 4), "hel\u2026"), (("hi", 5), "hi"), (("", 3), ""),
            (("hello", 5), "hello"), (("hello", 1), "\u2026"),
            (("hello", 0), ""), (("a", 1), "a"),
        ),
        js_answer=(
            "function truncate(text, most) {\n"
            "  if (text.length <= most) return text;\n"
            '  if (most <= 1) return "\\u2026".slice(0, most);\n'
            '  return text.slice(0, most - 1) + "\\u2026";\n'
            "}"
        ),
    ),
    Kata(
        id="js-slugify",
        level=4,
        language="javascript",
        name="slugify",
        brief=(
            "Turn a title into a slug for a URL: lower case, every run of "
            "anything that is not a letter or a digit becomes one dash, "
            "and no dash at either end."
        ),
        params=("text",),
        family="JavaScript",
        example='slugify("Hello, World!") is "hello-world"',
        hint=(
            "Do it in three passes and each one is easy: lower case, "
            "replace the runs, then trim the ends. Doing it in one goes "
            "wrong at the edges."
        ),
        cases=(
            ("Hello, World!",), ("",), ("a",), ("  spaced  ",),
            ("Already-Slugged",), ("!!!",), ("one   two",),
            ("Mixed CASE 123",), ("-leading",), ("trailing-",),
        ),
        solve=_slugify,
        checks=(
            (("Hello, World!",), "hello-world"), (("",), ""),
            (("a",), "a"), (("!!!",), ""), (("  spaced  ",), "spaced"),
            (("-leading",), "leading"), (("one   two",), "one-two"),
        ),
        js_answer=(
            "function slugify(text) {\n"
            "  return text\n"
            "    .trim()\n"
            "    .toLowerCase()\n"
            '    .replace(/[^a-z0-9]+/g, "-")\n'
            '    .replace(/^-+|-+$/g, "");\n'
            "}"
        ),
    ),
)


JS_KATAS: tuple[Kata, ...] = SHAPES + TEXT
