"""Forms in TypeScript: small functions, written with their types.

The same exercise as every other language's forms - write the function, and
it is called with inputs you have not seen - with one more judge: the whole
file goes through `tsc --strict` before anything runs, so a missing type, a
possibly-undefined value used as if it were there, or a return that does
not match the signature fails before a single case does.

The brief gives the full typed signature, because in TypeScript the types
ARE part of the question. The oracle is Python, as for every kata; the worked
answer is checked by running it through the TypeScript driver against it.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "TypeScript"


def _sum_evens(nums):
    return sum(n for n in nums if n % 2 == 0)


def _initials(name):
    return "".join(part[0].upper() for part in name.split())


def _clamp(n, lo, hi):
    return max(lo, min(hi, n))


def _count_words(words):
    out = {}
    for w in words:
        out[w] = out.get(w, 0) + 1
    return out


def _unique_sorted(nums):
    return sorted(set(nums))


def _longest_word(text):
    best = ""
    for w in text.split():
        if len(w) > len(best):
            best = w
    return best


def _safe_divide(a, b):
    return None if b == 0 else a / b


def _title_case(text):
    return " ".join(w[:1].upper() + w[1:].lower() for w in text.split(" "))


def _flatten(rows):
    return [x for row in rows for x in row]


def _parse_age(text):
    t = text.strip()
    return int(t) if t.isdigit() and int(t) <= 150 else None


def _group_by_length(words):
    out = {}
    for w in words:
        out.setdefault(str(len(w)), []).append(w)
    return out


def _pick(obj, keys):
    return {k: obj[k] for k in keys if k in obj}


def _chunk(nums, size):
    return [nums[i:i + size] for i in range(0, len(nums), size)]


def _zip_object(keys, values):
    return {k: v for k, v in zip(keys, values)}


TS_KATAS: tuple[Kata, ...] = (
    Kata(
        id="ts-sum-evens", level=1, language="typescript", family=FAMILY, name="sumEvens",
        brief="function sumEvens(nums: number[]): number - the total of the even numbers. None at all totals 0.",
        params=("nums",),
        example="sumEvens([1, 2, 3, 4]) is 6",
        hint="filter keeps the ones where n % 2 === 0; reduce adds them up, starting from 0.",
        cases=(([1, 2, 3, 4],), ([],), ([1, 3],), ([-2, 5, 8],), ([0],), ([10, 20, 30],)),
        solve=_sum_evens,
        checks=((([1, 2, 3, 4],), 6), (([],), 0), (([-2, 5, 8],), 6)),
        ts_answer=(
            "function sumEvens(nums: number[]): number {\n"
            "  return nums.filter((n) => n % 2 === 0).reduce((a, b) => a + b, 0);\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-initials", level=1, language="typescript", family=FAMILY, name="nameInitials",
        brief="function nameInitials(name: string): string - the first letter of each word, in capitals.",
        params=("name",),
        example='nameInitials("ada lovelace") is "AL"',
        hint="split(\" \") gives the words; take [0] of each and toUpperCase() it. Watch for double spaces.",
        cases=(("ada lovelace",), ("Grace Brewster Hopper",), ("bo",), ("",), ("  two  spaces  ",)),
        solve=_initials,
        checks=((("ada lovelace",), "AL"), (("",), ""), (("  two  spaces  ",), "TS")),
        ts_answer=(
            "function nameInitials(name: string): string {\n"
            "  return name\n"
            "    .split(\" \")\n"
            "    .filter((w) => w.length > 0)\n"
            "    .map((w) => w[0].toUpperCase())\n"
            "    .join(\"\");\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-clamp", level=1, language="typescript", family=FAMILY, name="clamp",
        brief="function clamp(n: number, lo: number, hi: number): number - n, but never below lo or above hi.",
        params=("n", "lo", "hi"),
        example="clamp(15, 0, 10) is 10",
        hint="Math.min with hi first, then Math.max with lo.",
        cases=((15, 0, 10), (-5, 0, 10), (5, 0, 10), (0, 0, 10), (10, 0, 10), (3, 3, 3)),
        solve=_clamp,
        checks=(((15, 0, 10), 10), ((-5, 0, 10), 0), ((5, 0, 10), 5)),
        ts_answer=(
            "function clamp(n: number, lo: number, hi: number): number {\n"
            "  return Math.max(lo, Math.min(hi, n));\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-count-words", level=2, language="typescript", family=FAMILY, name="tallyWords",
        brief="function tallyWords(words: string[]): Record<string, number> - how many times each word appears.",
        params=("words",),
        example='tallyWords(["a", "b", "a"]) is { a: 2, b: 1 }',
        hint="Start from {} typed as Record<string, number>; (counts[w] ?? 0) + 1 starts a new word at 0.",
        cases=(([],), (["a", "b", "a"],), (["x"],), (["to", "be", "or", "not", "to", "be"],)),
        solve=_count_words,
        checks=(((["a", "b", "a"],), {"a": 2, "b": 1}), (([],), {})),
        ts_answer=(
            "function tallyWords(words: string[]): Record<string, number> {\n"
            "  const counts: Record<string, number> = {};\n"
            "  for (const w of words) {\n"
            "    counts[w] = (counts[w] ?? 0) + 1;\n"
            "  }\n"
            "  return counts;\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-unique-sorted", level=2, language="typescript", family=FAMILY, name="uniqueSorted",
        brief="function uniqueSorted(nums: number[]): number[] - each number once, smallest first. Do not change nums.",
        params=("nums",),
        example="uniqueSorted([3, 1, 3, 2]) is [1, 2, 3]",
        hint="[...new Set(nums)] makes a new array of each value once; sort it with (a, b) => a - b, "
             "because sort() with nothing sorts numbers as text.",
        cases=(([3, 1, 3, 2],), ([],), ([5, 5, 5],), ([10, 9, 100, 1],), ([-1, 0, -1],)),
        solve=_unique_sorted,
        checks=((([3, 1, 3, 2],), [1, 2, 3]), (([10, 9, 100, 1],), [1, 9, 10, 100]), (([],), [])),
        ts_answer=(
            "function uniqueSorted(nums: number[]): number[] {\n"
            "  return [...new Set(nums)].sort((a, b) => a - b);\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-longest-word", level=2, language="typescript", family=FAMILY, name="longestWord",
        brief="function longestWord(text: string): string - the longest word; the first one if there is a tie; "
              "\"\" if there are none.",
        params=("text",),
        example='longestWord("a quick fox") is "quick"',
        hint="Keep a best-so-far string starting at \"\", and only replace it when a word is strictly longer.",
        cases=(("a quick fox",), ("",), ("one two six",), ("  padded  words ",), ("aa bb ccc dd",)),
        solve=_longest_word,
        checks=((("a quick fox",), "quick"), (("one two six",), "one"), (("",), "")),
        ts_answer=(
            "function longestWord(text: string): string {\n"
            "  let best = \"\";\n"
            "  for (const w of text.split(\" \")) {\n"
            "    if (w.length > best.length) best = w;\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-safe-divide", level=2, language="typescript", family=FAMILY, name="safeDivide",
        brief="function safeDivide(a: number, b: number): number | null - a / b, or null when b is 0.",
        params=("a", "b"),
        example="safeDivide(7, 2) is 3.5, and safeDivide(1, 0) is null",
        hint="The return type allows null, so you may - and must - say what happens when b is 0.",
        cases=((7, 2), (1, 0), (0, 5), (-9, 3), (0, 0)),
        solve=_safe_divide,
        checks=(((7, 2), 3.5), ((1, 0), None), ((-9, 3), -3.0)),
        ts_answer=(
            "function safeDivide(a: number, b: number): number | null {\n"
            "  return b === 0 ? null : a / b;\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-title-case", level=2, language="typescript", family=FAMILY, name="capitalizeWords",
        brief="function capitalizeWords(text: string): string - each word with a capital first letter and the rest small. "
              "Keep the spaces as they are.",
        params=("text",),
        example='capitalizeWords("hELLO wORLD") is "Hello World"',
        hint="split(\" \") and join(\" \") keep every space; w.slice(0, 1) is safe even for an empty word.",
        cases=(("hELLO wORLD",), ("",), ("a",), ("two  spaces",), ("ALL CAPS HERE",)),
        solve=_title_case,
        checks=((("hELLO wORLD",), "Hello World"), (("two  spaces",), "Two  Spaces"), (("a",), "A")),
        ts_answer=(
            "function capitalizeWords(text: string): string {\n"
            "  return text\n"
            "    .split(\" \")\n"
            "    .map((w) => w.slice(0, 1).toUpperCase() + w.slice(1).toLowerCase())\n"
            "    .join(\" \");\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-flatten", level=2, language="typescript", family=FAMILY, name="flatten",
        brief="function flatten(rows: number[][]): number[] - every number, row by row, in one list.",
        params=("rows",),
        example="flatten([[1, 2], [3]]) is [1, 2, 3]",
        hint="rows.flat() does it in one call; a loop that pushes each row's items works too.",
        cases=(([[1, 2], [3]],), ([],), ([[], [4], []],), ([[1], [2], [3, 4, 5]],)),
        solve=_flatten,
        checks=((([[1, 2], [3]],), [1, 2, 3]), (([],), [])),
        ts_answer=(
            "function flatten(rows: number[][]): number[] {\n"
            "  const out: number[] = [];\n"
            "  for (const row of rows) out.push(...row);\n"
            "  return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-parse-age", level=3, language="typescript", family=FAMILY, name="parseAge",
        brief="function parseAge(text: string): number | null - the age as a whole number from 0 to 150, "
              "or null for anything else. Spaces round it are fine.",
        params=("text",),
        example='parseAge(" 36 ") is 36; parseAge("thirty") and parseAge("-3") are null',
        hint="Trim first. /^\\d+$/ tests for digits only - parseInt alone would accept \"12abc\" as 12.",
        cases=((" 36 ",), ("thirty",), ("-3",), ("0",), ("151",), ("12abc",), ("",), ("150",)),
        solve=_parse_age,
        checks=(((" 36 ",), 36), (("12abc",), None), (("151",), None), (("0",), 0)),
        ts_answer=(
            "function parseAge(text: string): number | null {\n"
            "  const t = text.trim();\n"
            "  if (!/^\\d+$/.test(t)) return null;\n"
            "  const n = Number(t);\n"
            "  return n <= 150 ? n : null;\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-group-by-length", level=3, language="typescript", family=FAMILY, name="groupByLength",
        brief="function groupByLength(words: string[]): Record<string, string[]> - the words grouped under their "
              "length, in the order they came.",
        params=("words",),
        example='groupByLength(["ox", "cat", "be"]) is { "2": ["ox", "be"], "3": ["cat"] }',
        hint="For each word, make the group if it is not there yet (??=), then push the word into it.",
        cases=(([],), (["ox", "cat", "be"],), (["a"],), (["one", "two", "three"],)),
        solve=_group_by_length,
        checks=(((["ox", "cat", "be"],), {"2": ["ox", "be"], "3": ["cat"]}), (([],), {})),
        ts_answer=(
            "function groupByLength(words: string[]): Record<string, string[]> {\n"
            "  const groups: Record<string, string[]> = {};\n"
            "  for (const w of words) {\n"
            "    (groups[String(w.length)] ??= []).push(w);\n"
            "  }\n"
            "  return groups;\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-pick", level=3, language="typescript", family=FAMILY, name="pick",
        brief="function pick(obj: Record<string, number>, keys: string[]): Record<string, number> - a new object "
              "with only those keys; a key obj does not have is left out.",
        params=("obj", "keys"),
        example='pick({ a: 1, b: 2, c: 3 }, ["a", "c", "z"]) is { a: 1, c: 3 }',
        hint="`key in obj` asks whether obj has it. Build a new object - do not delete from obj.",
        cases=(({"a": 1, "b": 2, "c": 3}, ["a", "c", "z"]), ({}, ["a"]), ({"x": 0}, ["x"]), ({"a": 1}, [])),
        solve=_pick,
        checks=((({"a": 1, "b": 2, "c": 3}, ["a", "c", "z"]), {"a": 1, "c": 3}), (({"x": 0}, ["x"]), {"x": 0})),
        ts_answer=(
            "function pick(obj: Record<string, number>, keys: string[]): Record<string, number> {\n"
            "  const out: Record<string, number> = {};\n"
            "  for (const k of keys) {\n"
            "    if (k in obj) out[k] = obj[k];\n"
            "  }\n"
            "  return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-chunk", level=3, language="typescript", family=FAMILY, name="chunk",
        brief="function chunk(nums: number[], size: number): number[][] - nums cut into pieces of size; the last "
              "may be shorter.",
        params=("nums", "size"),
        example="chunk([1, 2, 3, 4, 5], 2) is [[1, 2], [3, 4], [5]]",
        hint="Step i by size and slice(i, i + size) - slice never runs past the end.",
        cases=(([1, 2, 3, 4, 5], 2), ([], 3), ([1, 2, 3], 3), ([1, 2, 3], 5), ([1, 2, 3, 4], 1)),
        solve=_chunk,
        checks=((([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]), (([], 3), [])),
        ts_answer=(
            "function chunk(nums: number[], size: number): number[][] {\n"
            "  const out: number[][] = [];\n"
            "  for (let i = 0; i < nums.length; i += size) {\n"
            "    out.push(nums.slice(i, i + size));\n"
            "  }\n"
            "  return out;\n"
            "}\n"
        ),
    ),
    Kata(
        id="ts-zip-object", level=4, language="typescript", family=FAMILY, name="zipObject",
        brief="function zipObject(keys: string[], values: number[]): Record<string, number> - each key paired with "
              "the value at the same place; extra keys or values are dropped.",
        params=("keys", "values"),
        example='zipObject(["a", "b"], [1, 2, 3]) is { a: 1, b: 2 }',
        hint="Loop to the SHORTER length - Math.min(keys.length, values.length) - so nothing is undefined.",
        cases=((["a", "b"], [1, 2, 3]), ([], [1]), (["x", "y", "z"], [9]), (["k"], [0])),
        solve=_zip_object,
        checks=(((["a", "b"], [1, 2, 3]), {"a": 1, "b": 2}), ((["x", "y", "z"], [9]), {"x": 9})),
        ts_answer=(
            "function zipObject(keys: string[], values: number[]): Record<string, number> {\n"
            "  const out: Record<string, number> = {};\n"
            "  const n = Math.min(keys.length, values.length);\n"
            "  for (let i = 0; i < n; i++) out[keys[i]] = values[i];\n"
            "  return out;\n"
            "}\n"
        ),
    ),
)
