"""Fix the bug, in JavaScript: the function is written, and it is wrong.

The same exercise as the Python family - working-looking code that fails
some of its cases - but every bug here is JavaScript's own, the kind a
Python habit walks straight into:

  the text sort          `sort()` with no comparator compares as strings
  the loose equal        `==` says 0 and "0" and "" are all the same
  the stopping parse     `parseInt("1,000")` is 1, not 1000
  the in-place splice    `splice` changes the caller's array
  the radix argument     `.map(parseInt)` hands the index in as the radix
  the null default       `size = 10` replaces undefined, never null
  the shared fill        `Array(n).fill([])` is one array n times
  the var closure        every function made in a `var` loop sees the last i

Each one runs, because a start with a syntax error teaches the parser
rather than the bug. And each one passes some of its cases, because that
is what makes these hard to see: they are right on the inputs you
thought of and wrong on the ones you did not.

The oracle is Python, as for every kata. What is JavaScript is the
start, the worked answer in `js_answer`, and the run.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Fix the bug: JavaScript"


def _sort_numbers(numbers: list) -> list:
    return sorted(numbers)


def _count_matches(items: list, target) -> int:
    return sum(1 for x in items if type(x) is type(target) and x == target)


def _parse_amount(text: str) -> int:
    return int(text.replace(",", ""))


def _without_index(items: list, index: int) -> list:
    return [x for i, x in enumerate(items) if i != index]


def _to_numbers(texts: list) -> list:
    return [int(t) for t in texts]


def _page_count(total: int, size) -> int:
    per = 10 if size is None else size
    return -(-total // per)


def _buckets_by_length(words: list, longest: int) -> list:
    buckets: list = [[] for _ in range(longest + 1)]
    for word in words:
        buckets[len(word)].append(word)
    return buckets


def _times_table(n: int, x: int) -> list:
    return [i * x for i in range(n)]


JS_BUGS: tuple[Kata, ...] = (
    Kata(
        id="js-bug-sort-numbers",
        level=1,
        language="javascript",
        name="sortNumbers",
        brief=(
            "Return a new array of the numbers, smallest first. It gets "
            "single digits right and goes wrong somewhere past ten."
        ),
        params=("numbers",),
        family=FAMILY,
        example="sortNumbers([10, 9, 1]) is [1, 9, 10]",
        hint="What does sort compare when it is not told how?",
        cases=(
            ([3, 1, 2],), ([],), ([1],), ([10, 9, 1],), ([2, 1],),
            ([100, 20, 3],), ([-1, -2],), ([5, 5, 1],), ([0, -3, 3],),
            ([1, 2, 3],),
        ),
        solve=_sort_numbers,
        checks=(
            (([3, 1, 2],), [1, 2, 3]), (([],), []),
            (([10, 9, 1],), [1, 9, 10]), (([-1, -2],), [-2, -1]),
        ),
        start=(
            "function sortNumbers(numbers) {\n"
            "  return [...numbers].sort();\n"
            "}"
        ),
        bug=(
            "sort() with no comparator turns every item into a string and "
            'sorts those, so "10" comes before "9". Numbers need '
            "(a, b) => a - b."
        ),
        js_answer=(
            "function sortNumbers(numbers) {\n"
            "  return [...numbers].sort((a, b) => a - b);\n"
            "}"
        ),
    ),
    Kata(
        id="js-bug-count-matches",
        level=1,
        language="javascript",
        name="countMatches",
        brief=(
            "Count the items that are exactly the target - the same value "
            'and the same type, so the number 0 and the text "0" are '
            "different things."
        ),
        params=("items", "target"),
        family=FAMILY,
        example='countMatches([0, "0", 1], 0) is 1',
        hint='Try 0 == "0" and 0 == "" in the console.',
        cases=(
            ([0, "0", 1], 0), ([], 0), (["0"], "0"), ([1, 2, 1], 1),
            (["1", 1, "1"], "1"), ([0, ""], 0), (["a", "b"], "c"),
            ([-1, "-1"], -1), ([5], 5), ([2, "2", 2, "2"], 2),
        ),
        solve=_count_matches,
        checks=(
            (([0, "0", 1], 0), 1), (([], 0), 0), (([0, ""], 0), 1),
            (([1, 2, 1], 1), 2), ((["1", 1, "1"], "1"), 2),
        ),
        start=(
            "function countMatches(items, target) {\n"
            "  return items.filter((x) => x == target).length;\n"
            "}"
        ),
        bug=(
            "== converts types before comparing, so 0, \"0\" and \"\" all "
            "count as equal. === compares without converting, which is "
            "almost always what is meant."
        ),
        js_answer=(
            "function countMatches(items, target) {\n"
            "  return items.filter((x) => x === target).length;\n"
            "}"
        ),
    ),
    Kata(
        id="js-bug-parse-amount",
        level=2,
        language="javascript",
        name="parseAmount",
        brief=(
            "Turn an amount typed with thousands separators, like "
            '"1,234", into the whole number it means.'
        ),
        params=("text",),
        family=FAMILY,
        example='parseAmount("1,000") is 1000',
        hint="parseInt reads until it meets something that is not a digit.",
        cases=(
            ("5",), ("0",), ("1,000",), ("42",), ("1,234,567",), ("-3",),
            ("-1,000",), ("999",), ("10,000",), ("100",),
        ),
        solve=_parse_amount,
        checks=(
            (("5",), 5), (("0",), 0), (("1,000",), 1000),
            (("-1,000",), -1000), (("1,234,567",), 1234567),
        ),
        start=(
            "function parseAmount(text) {\n"
            "  return parseInt(text, 10);\n"
            "}"
        ),
        bug=(
            "parseInt stops quietly at the first character it cannot read "
            'and returns what it had, so "1,000" is 1 - no error, just the '
            "wrong number. Take the commas out first."
        ),
        js_answer=(
            "function parseAmount(text) {\n"
            '  return parseInt(text.replaceAll(",", ""), 10);\n'
            "}"
        ),
    ),
    Kata(
        id="js-bug-without-index",
        level=2,
        language="javascript",
        name="withoutIndex",
        brief=(
            "Return a new array with the item at `index` left out. An "
            "index past the end leaves nothing out. The array you were "
            "given must not change."
        ),
        params=("items", "index"),
        family=FAMILY,
        example="withoutIndex([1, 2, 3], 1) is [1, 3]",
        hint="The answer it returns is right. Look at the caller's array afterwards.",
        cases=(
            ([1, 2, 3], 1), ([], 0), ([7], 0), ([1, 2], 5), (["a", "b"], 0),
            ([1, 2, 3], 2), ([0, 0], 1), ([-1, 4], 0), ([5, 6, 7], 3),
            ([9, 8], 1),
        ),
        solve=_without_index,
        checks=(
            (([1, 2, 3], 1), [1, 3]), (([], 0), []), (([7], 0), []),
            (([1, 2], 5), [1, 2]), (([-1, 4], 0), [4]),
        ),
        start=(
            "function withoutIndex(items, index) {\n"
            "  items.splice(index, 1);\n"
            "  return items;\n"
            "}"
        ),
        bug=(
            "splice removes from the array it is called on, and that array "
            "is the caller's. The return value is right and the damage is "
            "somewhere else. filter (or toSpliced) builds a new one."
        ),
        js_answer=(
            "function withoutIndex(items, index) {\n"
            "  return items.filter((_, i) => i !== index);\n"
            "}"
        ),
    ),
    Kata(
        id="js-bug-to-numbers",
        level=3,
        language="javascript",
        name="toNumbers",
        brief="Turn every piece of text in the array into the whole number it spells.",
        params=("texts",),
        family=FAMILY,
        example='toNumbers(["1", "2", "3"]) is [1, 2, 3]',
        hint="map calls its function with more than one argument. What is the second?",
        cases=(
            (["1", "2", "3"],), ([],), (["7"],), (["10", "11"],), (["0"],),
            (["-4"],), (["5", "5"],), (["1", "0"],), (["12", "3", "100"],),
            (["-1", "-2"],),
        ),
        solve=_to_numbers,
        checks=(
            ((["1", "2", "3"],), [1, 2, 3]), (([],), []), ((["7"],), [7]),
            ((["10", "11"],), [10, 11]), ((["-4"],), [-4]),
        ),
        start=(
            "function toNumbers(texts) {\n"
            "  return texts.map(parseInt);\n"
            "}"
        ),
        bug=(
            "map passes (item, index, array), and parseInt's second "
            "argument is the radix - so the second item is read in base 1 "
            "and comes out NaN. Wrap it: (t) => parseInt(t, 10)."
        ),
        js_answer=(
            "function toNumbers(texts) {\n"
            "  return texts.map((t) => parseInt(t, 10));\n"
            "}"
        ),
    ),
    Kata(
        id="js-bug-page-count",
        level=3,
        language="javascript",
        name="pageCount",
        brief=(
            "How many pages `total` items fill at `size` per page, a "
            "part-filled last page counting as one. A size of null means "
            "the default, 10."
        ),
        params=("total", "size"),
        family=FAMILY,
        example="pageCount(25, null) is 3",
        hint="When does a default parameter actually kick in?",
        cases=(
            (25, 5), (25, None), (0, None), (1, 1), (100, None), (7, 2),
            (10, 10), (0, 3), (11, None), (1, None),
        ),
        solve=_page_count,
        checks=(
            ((25, 5), 5), ((25, None), 3), ((0, None), 0), ((1, 1), 1),
            ((11, None), 2),
        ),
        start=(
            "function pageCount(total, size = 10) {\n"
            "  return Math.ceil(total / size);\n"
            "}"
        ),
        bug=(
            "A default parameter replaces undefined and nothing else. null "
            "is a value that was passed, so size stays null and total / "
            "null divides by zero. size ?? 10 catches both."
        ),
        js_answer=(
            "function pageCount(total, size) {\n"
            "  return Math.ceil(total / (size ?? 10));\n"
            "}"
        ),
    ),
    Kata(
        id="js-bug-buckets-by-length",
        level=4,
        language="javascript",
        name="bucketsByLength",
        brief=(
            "Return `longest + 1` arrays where bucket i holds the words of "
            "length i, in the order given. No word is longer than `longest`."
        ),
        params=("words", "longest"),
        family=FAMILY,
        example='bucketsByLength(["hi", "a"], 2) is [[], ["a"], ["hi"]]',
        hint="How many arrays does fill([]) actually make?",
        cases=(
            ([], 2), (["a"], 1), ([], 0), (["", ""], 0), (["hi", "a", "yo"], 2),
            (["abc"], 3), (["a", "b"], 1), ([""], 1), (["tea", "me", "x"], 3),
            (["no"], 2),
        ),
        solve=_buckets_by_length,
        checks=(
            (([], 2), [[], [], []]), ((["a"], 1), [[], ["a"]]),
            ((["", ""], 0), [["", ""]]),
            ((["hi", "a", "yo"], 2), [[], ["a"], ["hi", "yo"]]),
        ),
        start=(
            "function bucketsByLength(words, longest) {\n"
            "  const buckets = Array(longest + 1).fill([]);\n"
            "  for (const word of words) {\n"
            "    buckets[word.length].push(word);\n"
            "  }\n"
            "  return buckets;\n"
            "}"
        ),
        bug=(
            "fill evaluates its argument once and puts that one array in "
            "every slot, so a push into any bucket shows up in all of "
            "them. Array.from with a function makes a fresh one each time."
        ),
        js_answer=(
            "function bucketsByLength(words, longest) {\n"
            "  const buckets = Array.from({ length: longest + 1 }, () => []);\n"
            "  for (const word of words) {\n"
            "    buckets[word.length].push(word);\n"
            "  }\n"
            "  return buckets;\n"
            "}"
        ),
    ),
    Kata(
        id="js-bug-times-table",
        level=4,
        language="javascript",
        name="timesTable",
        brief=(
            "Build one function per row i from 0 to n - 1, each giving "
            "i * x, then call them all and return the results."
        ),
        params=("n", "x"),
        family=FAMILY,
        example="timesTable(3, 2) is [0, 2, 4]",
        hint="When the functions finally run, what is i?",
        cases=(
            (0, 5), (1, 0), (3, 2), (1, 7), (4, 1), (2, -3), (5, 0), (3, 10),
            (2, 1), (1, -1),
        ),
        solve=_times_table,
        checks=(
            ((0, 5), []), ((1, 7), [0]), ((3, 2), [0, 2, 4]),
            ((2, -3), [0, -3]), ((5, 0), [0, 0, 0, 0, 0]),
        ),
        start=(
            "function timesTable(n, x) {\n"
            "  var makers = [];\n"
            "  for (var i = 0; i < n; i++) {\n"
            "    makers.push(function () { return i * x; });\n"
            "  }\n"
            "  return makers.map(function (make) { return make(); });\n"
            "}"
        ),
        bug=(
            "var gives the whole function one i, and every closure shares "
            "it - by the time they run the loop is over and i is n. let "
            "makes a new i for each pass of the loop."
        ),
        js_answer=(
            "function timesTable(n, x) {\n"
            "  const makers = [];\n"
            "  for (let i = 0; i < n; i++) {\n"
            "    makers.push(() => i * x);\n"
            "  }\n"
            "  return makers.map((make) => make());\n"
            "}"
        ),
    ),
)
