"""More TypeScript and Rust hunts (set 2 of each).

Same rules as content_ts.py and content_rust.py: every TypeScript program
passes `tsc --strict`, every Rust program compiles, and each one prints the
same in a debug and an optimised build (no implicit overflow, no map
iteration order). The bug is real, it hides on some inputs, the report's own
input shows it, and the fix changes one or two lines in place.
Checked by tests/test_bughunt_tsrust2.py.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

TS = "TypeScript"
RUST = "Rust"


# ── TypeScript oracles ───────────────────────────────────────


def _smallest(nums, n):
    return sorted(nums)[:n]


def _page(items, page_no, size):
    start = (page_no - 1) * size
    return items[start:start + size]


def _valid_count(boxes):
    def ok(s):
        if s.strip() == "":
            return False
        try:
            float(s)
        except ValueError:
            return False
        return True
    return sum(1 for b in boxes if ok(b))


def _total_cents(prices):
    return sum(round(p * 100) for p in prices)


def _first_over(nums, limit):
    for n in nums:
        if n > limit:
            return n
    return None


def _label_all(names):
    return [["new", n] for n in names]


def _first_seen(names):
    return list(dict.fromkeys(names))


TS_HUNTS_2: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-ts-sort-default",
        title="The smallest of 10, 9 and 1 is 10",
        family=TS,
        language="typescript",
        level=1,
        report="Asking for the 2 smallest of the scores 10, 9 and 1 gives 1 "
               "and 10. It should be 1 and 9. Scores that are all one digit "
               "come out right.",
        name="smallest",
        params=("nums", "n"),
        start=(
            "// Scores come in as plain numbers.\n"
            "function ascending(nums: number[]): number[] {\n"
            "  return [...nums].sort();\n"
            "}\n"
            "\n"
            "function smallest(nums: number[], n: number): number[] {\n"
            "  return ascending(nums).slice(0, n);\n"
            "}\n"
        ),
        fixed=(
            "// Scores come in as plain numbers.\n"
            "function ascending(nums: number[]): number[] {\n"
            "  return [...nums].sort((a, b) => a - b);\n"
            "}\n"
            "\n"
            "function smallest(nums: number[], n: number): number[] {\n"
            "  return ascending(nums).slice(0, n);\n"
            "}\n"
        ),
        solve=_smallest,
        reported=([10, 9, 1], 2),
        cases=(([], 1), ([3, 1, 2], 2), ([10, 9, 1], 2), ([100, 25, 7], 1), ([5, 4], 2)),
        cause="sort() with no comparator compares the numbers as TEXT, so "
              "'10' sorts before '9' - the order is alphabetical, not numeric.",
        decoys=(
            "slice(0, n) keeps the n largest instead of the n smallest.",
            "The spread [...nums] turns the numbers into strings.",
            "sort() only works on arrays of strings, so numbers are skipped.",
        ),
        lesson="Array.prototype.sort() defaults to string order, and tsc "
               "accepts it for numbers. Always pass a comparator for numbers: "
               "sort((a, b) => a - b).",
        hint="Use a score with two digits: smallest([10, 9, 1], 2).",
        checks=((([10, 9, 1], 2), [1, 9]), (([3, 1, 2], 2), [1, 2]), (([100, 25, 7], 1), [7])),
    ),
    Hunt(
        id="hunt-ts-slice-end",
        title="Every full page is one short",
        family=TS,
        language="typescript",
        level=2,
        report="Pages are meant to show 3 items. Page 1 of [1, 2, 3, 4, 5] "
               "shows only 1 and 2. The last page, which has fewer items, is "
               "fine.",
        name="page",
        params=("items", "pageNo", "size"),
        start=(
            "// Pages are numbered from 1.\n"
            "function pageEnd(start: number, size: number): number {\n"
            "  return start + size - 1;\n"
            "}\n"
            "\n"
            "function page(items: number[], pageNo: number, size: number): number[] {\n"
            "  const start = (pageNo - 1) * size;\n"
            "  return items.slice(start, pageEnd(start, size));\n"
            "}\n"
        ),
        fixed=(
            "// Pages are numbered from 1.\n"
            "function pageEnd(start: number, size: number): number {\n"
            "  return start + size;\n"
            "}\n"
            "\n"
            "function page(items: number[], pageNo: number, size: number): number[] {\n"
            "  const start = (pageNo - 1) * size;\n"
            "  return items.slice(start, pageEnd(start, size));\n"
            "}\n"
        ),
        solve=_page,
        reported=([1, 2, 3, 4, 5], 1, 3),
        cases=(([], 1, 3), ([1, 2], 1, 3), ([1, 2, 3, 4, 5], 1, 3),
               ([1, 2, 3, 4, 5], 2, 3), ([1, 2, 3, 4, 5, 6], 2, 3)),
        cause="slice's end index is EXCLUSIVE, so the end of a page is "
              "start + size; start + size - 1 stops one item early.",
        decoys=(
            "The page number is counted from 0, so every page starts one late.",
            "slice(start, end) includes both ends, so the end must be pulled back.",
            "The start is wrong: (pageNo - 1) * size should be pageNo * size.",
        ),
        lesson="slice(start, end) takes items from start up to but NOT "
               "including end, so a window of `size` items is slice(start, "
               "start + size). The -1 belongs to languages whose ranges are "
               "inclusive.",
        hint="Ask for a full page of 3: page([1, 2, 3, 4, 5], 1, 3).",
        checks=((([1, 2, 3, 4, 5], 1, 3), [1, 2, 3]), (([1, 2, 3, 4, 5], 2, 3), [4, 5]),
                (([], 1, 3), [])),
    ),
    Hunt(
        id="hunt-ts-number-blank",
        title="An empty box counts as a number",
        family=TS,
        language="typescript",
        level=2,
        report="The form says 2 of the quantity boxes are filled in for "
               "['', '3']. Only one is. Boxes with letters in them are "
               "rejected correctly.",
        name="validCount",
        params=("boxes",),
        start=(
            "// A quantity box is valid when it holds a number.\n"
            "function isNumeric(text: string): boolean {\n"
            "  return !Number.isNaN(Number(text));\n"
            "}\n"
            "\n"
            "function validCount(boxes: string[]): number {\n"
            "  return boxes.filter((b) => isNumeric(b)).length;\n"
            "}\n"
        ),
        fixed=(
            "// A quantity box is valid when it holds a number.\n"
            "function isNumeric(text: string): boolean {\n"
            "  return text.trim() !== \"\" && !Number.isNaN(Number(text));\n"
            "}\n"
            "\n"
            "function validCount(boxes: string[]): number {\n"
            "  return boxes.filter((b) => isNumeric(b)).length;\n"
            "}\n"
        ),
        solve=_valid_count,
        reported=(["", "3"],),
        cases=(([],), (["4", "x"],), (["7", "8"],), (["", "3"],), (["  "],)),
        cause="Number('') is 0, not NaN, and so is Number('  '): a blank "
              "string passes the NaN test as if it were the number 0.",
        decoys=(
            "Number.isNaN is true for every string, so nothing is counted.",
            "filter counts the items it removes instead of the ones it keeps.",
            "Number('3') is NaN until the string is trimmed.",
        ),
        lesson="Number() turns an empty or all-space string into 0. Test for "
               "blank first (text.trim() !== ''), or use a stricter check, "
               "before treating 'not NaN' as 'a number was typed'.",
        hint="Leave one box empty: validCount([\"\", \"3\"]).",
        checks=(((["", "3"],), 1), ((["4", "x"],), 1), (([],), 0), ((["  "],), 0)),
    ),
    Hunt(
        id="hunt-ts-money-floor",
        title="29 cents is 28",
        family=TS,
        language="typescript",
        level=3,
        report="A basket with one item priced 0.29 comes to 28 cents. A "
               "basket of 0.5 and 1.1 comes to 160, which is right.",
        name="totalCents",
        params=("prices",),
        start=(
            "// Prices arrive in dollars; totals are kept in whole cents.\n"
            "function toCents(dollars: number): number {\n"
            "  return Math.floor(dollars * 100);\n"
            "}\n"
            "\n"
            "function totalCents(prices: number[]): number {\n"
            "  return prices.reduce((sum, p) => sum + toCents(p), 0);\n"
            "}\n"
        ),
        fixed=(
            "// Prices arrive in dollars; totals are kept in whole cents.\n"
            "function toCents(dollars: number): number {\n"
            "  return Math.round(dollars * 100);\n"
            "}\n"
            "\n"
            "function totalCents(prices: number[]): number {\n"
            "  return prices.reduce((sum, p) => sum + toCents(p), 0);\n"
            "}\n"
        ),
        solve=_total_cents,
        reported=([0.29],),
        cases=(([],), ([0.5, 1.1],), ([2],), ([0.29],), ([0.57, 0.5],)),
        cause="0.29 * 100 is 28.999999999999996 in floating point, and "
              "Math.floor cuts that down to 28 instead of rounding to 29.",
        decoys=(
            "reduce adds the prices as text, so the cents are lost.",
            "Math.floor rounds every price down to a whole dollar.",
            "The starting value 0 in reduce is subtracted from the total.",
        ),
        lesson="Decimal fractions such as 0.29 cannot be stored exactly in a "
               "double, so dollars * 100 can land just under a whole number. "
               "Round when converting to cents (Math.round), and keep money "
               "in integer cents from then on.",
        hint="Price one item at 0.29: totalCents([0.29]).",
        checks=((([0.29],), 29), (([0.5, 1.1],), 160), (([],), 0)),
    ),
    Hunt(
        id="hunt-ts-foreach-return",
        title="The first over the limit is the last",
        family=TS,
        language="typescript",
        level=3,
        report="The first reading over 5 in [6, 2, 9] should be 6, and the "
               "app reports 9. A list with only one reading over the limit "
               "is right.",
        name="firstOver",
        params=("nums", "limit"),
        start=(
            "function firstOver(nums: number[], limit: number): number | null {\n"
            "  let found: number | null = null;\n"
            "  nums.forEach((n) => {\n"
            "    if (n > limit) {\n"
            "      found = n;\n"
            "      return;\n"
            "    }\n"
            "  });\n"
            "  return found;\n"
            "}\n"
        ),
        fixed=(
            "function firstOver(nums: number[], limit: number): number | null {\n"
            "  let found: number | null = null;\n"
            "  nums.forEach((n) => {\n"
            "    if (n > limit && found === null) {\n"
            "      found = n;\n"
            "      return;\n"
            "    }\n"
            "  });\n"
            "  return found;\n"
            "}\n"
        ),
        solve=_first_over,
        reported=([6, 2, 9], 5),
        cases=(([], 5), ([1, 2], 5), ([9], 5), ([6, 2, 9], 5), ([3, 8, 4], 5)),
        cause="`return` inside a forEach callback only leaves that one call "
              "of the callback; forEach carries on with the next item, so a "
              "later match overwrites found.",
        decoys=(
            "forEach visits the items from the last to the first.",
            "`n > limit` should be `n >= limit` for the first one to count.",
            "found is declared with let, so it is reset on every item.",
        ),
        lesson="forEach cannot be stopped with return or break. To stop at "
               "the first match use a for...of loop with return, or find(), "
               "some() or every(), which do stop.",
        hint="Put two readings over the limit: firstOver([6, 2, 9], 5).",
        checks=((([6, 2, 9], 5), 6), (([3, 8, 4], 5), 8), (([1, 2], 5), None)),
    ),
    Hunt(
        id="hunt-ts-shared-default",
        title="Everyone gets everyone's tags",
        family=TS,
        language="typescript",
        level=4,
        report="Labelling the names a and b should give ['new', 'a'] and "
               "['new', 'b']. Both come out as ['new', 'a', 'b']. Labelling "
               "a single name is fine.",
        name="labelAll",
        params=("names",),
        start=(
            "const DEFAULT_TAGS: string[] = [\"new\"];\n"
            "\n"
            "function tagsFor(name: string, tags: string[] = DEFAULT_TAGS): string[] {\n"
            "  const out = tags;\n"
            "  out.push(name);\n"
            "  return out;\n"
            "}\n"
            "\n"
            "function labelAll(names: string[]): string[][] {\n"
            "  return names.map((n) => tagsFor(n));\n"
            "}\n"
        ),
        fixed=(
            "const DEFAULT_TAGS: string[] = [\"new\"];\n"
            "\n"
            "function tagsFor(name: string, tags: string[] = DEFAULT_TAGS): string[] {\n"
            "  const out = [...tags];\n"
            "  out.push(name);\n"
            "  return out;\n"
            "}\n"
            "\n"
            "function labelAll(names: string[]): string[][] {\n"
            "  return names.map((n) => tagsFor(n));\n"
            "}\n"
        ),
        solve=_label_all,
        reported=(["a", "b"],),
        cases=(([],), (["a"],), (["a", "b"],), (["x"],), (["p", "q", "r"],)),
        cause="The default value is one array shared by every call, and "
              "`out` is that same array, not a copy, so push changes it for "
              "everyone.",
        decoys=(
            "A default parameter is evaluated again on every call, so each "
            "call starts with an empty array.",
            "push returns the new length, so the result is a number.",
            "map passes the whole names array to tagsFor as its tags.",
        ),
        lesson="`const out = tags` copies the reference, not the array. When "
               "a default (or any argument) is an object or array, copy it "
               "before changing it: [...tags], or build a fresh one.",
        hint="Label two names in one call: labelAll([\"a\", \"b\"]).",
        checks=(((["a", "b"],), [["new", "a"], ["new", "b"]]), ((["x"],), [["new", "x"]]),
                (([],), [])),
    ),
    Hunt(
        id="hunt-ts-key-order",
        title="Joined in the wrong order",
        family=TS,
        language="typescript",
        level=4,
        report="Members joined in the order b, 10, 2, but the list of "
               "who joined first says 2, 10, b. Names that are plain words "
               "come out in the right order.",
        name="firstSeen",
        params=("names",),
        start=(
            "function indexByName(names: string[]): Record<string, number> {\n"
            "  const index: Record<string, number> = {};\n"
            "  names.forEach((n, i) => {\n"
            "    if (!(n in index)) index[n] = i;\n"
            "  });\n"
            "  return index;\n"
            "}\n"
            "\n"
            "function firstSeen(names: string[]): string[] {\n"
            "  const index = indexByName(names);\n"
            "  return Object.keys(index);\n"
            "}\n"
        ),
        fixed=(
            "function indexByName(names: string[]): Record<string, number> {\n"
            "  const index: Record<string, number> = {};\n"
            "  names.forEach((n, i) => {\n"
            "    if (!(n in index)) index[n] = i;\n"
            "  });\n"
            "  return index;\n"
            "}\n"
            "\n"
            "function firstSeen(names: string[]): string[] {\n"
            "  const index = indexByName(names);\n"
            "  return Object.keys(index).sort((a, b) => index[a] - index[b]);\n"
            "}\n"
        ),
        solve=_first_seen,
        reported=(["b", "10", "2"],),
        cases=(([],), (["b", "a"],), (["x", "y", "x"],), (["b", "10", "2"],), (["7", "3"],)),
        cause="Object.keys lists keys that look like whole numbers first, in "
              "ascending numeric order, and only then the other keys in the "
              "order they were added - so insertion order is lost.",
        decoys=(
            "`n in index` is false for numeric names, so they are added twice.",
            "Object.keys returns the keys sorted alphabetically.",
            "forEach visits the numeric names before the others.",
        ),
        lesson="An object's key order is insertion order only for non-numeric "
               "keys; integer-like keys jump to the front, sorted. If order "
               "matters, use a Map or a Set, or sort by a stored position.",
        hint="Mix words and numbers: firstSeen([\"b\", \"10\", \"2\"]).",
        checks=(((["b", "10", "2"],), ["b", "10", "2"]), ((["x", "y", "x"],), ["x", "y"]),
                (([],), [])),
    ),
)


# ── Rust oracles ─────────────────────────────────────────────


def _average(scores):
    return sum(scores) / len(scores) if scores else 0.0


def _left_after(stock, sold):
    return max(0, stock - sold)


def _word_count(text):
    return len(text.split())


def _without_negatives(nums):
    return [n for n in nums if n >= 0]


def _count_of(words, target):
    return sum(1 for w in words if w == target)


def _band(score):
    if score < 60:
        return "fail"
    if score < 90:
        return "pass"
    if score <= 100:
        return "honors"
    return "invalid"


def _reverse_word(word):
    return word[::-1]


RUST_HUNTS_2: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-rs-int-average",
        title="The average of 1 and 2 is 1",
        family=RUST,
        language="rust",
        level=1,
        report="The average of the scores 1 and 2 shows as 1. It should be "
               "1.5. When the total divides evenly, like 4 and 6, it is "
               "right.",
        name="average",
        params=("scores",),
        types=("&[i32]",),
        returns="f64",
        start=(
            "// Average of a list of scores.\n"
            "fn mean(sum: i32, count: usize) -> f64 {\n"
            "    (sum / count as i32) as f64\n"
            "}\n"
            "\n"
            "fn average(scores: &[i32]) -> f64 {\n"
            "    if scores.is_empty() {\n"
            "        return 0.0;\n"
            "    }\n"
            "    mean(scores.iter().sum(), scores.len())\n"
            "}\n"
        ),
        fixed=(
            "// Average of a list of scores.\n"
            "fn mean(sum: i32, count: usize) -> f64 {\n"
            "    sum as f64 / count as f64\n"
            "}\n"
            "\n"
            "fn average(scores: &[i32]) -> f64 {\n"
            "    if scores.is_empty() {\n"
            "        return 0.0;\n"
            "    }\n"
            "    mean(scores.iter().sum(), scores.len())\n"
            "}\n"
        ),
        solve=_average,
        reported=([1, 2],),
        cases=(([],), ([4, 6],), ([3],), ([1, 2],), ([10, 15, 20, 25],)),
        cause="`sum / count` divides two integers, which drops the fraction "
              "(3 / 2 is 1) BEFORE the result is turned into an f64.",
        decoys=(
            "`as f64` rounds the average down to a whole number.",
            "scores.len() counts one score too many.",
            "iter().sum() adds only the first two scores.",
        ),
        lesson="Integer division truncates, and converting to f64 afterwards "
               "cannot bring the fraction back. Convert the operands first: "
               "sum as f64 / count as f64.",
        hint="Use two scores that do not divide evenly: average(&[1, 2]).",
        checks=((([1, 2],), 1.5), (([4, 6],), 5.0), (([],), 0.0), (([10, 15, 20, 25],), 17.5)),
    ),
    Hunt(
        id="hunt-rs-checked-sub",
        title="Selling more than we have leaves all of it",
        family=RUST,
        language="rust",
        level=2,
        report="With 3 in stock, an order for 5 should leave 0. The app says "
               "3 are left. Orders that are within the stock are fine.",
        name="left_after",
        params=("stock", "sold"),
        types=("u32", "u32"),
        returns="u32",
        start=(
            "// Stock counts are never negative.\n"
            "fn left_after(stock: u32, sold: u32) -> u32 {\n"
            "    stock.checked_sub(sold).unwrap_or(stock)\n"
            "}\n"
            "\n"
            "fn sold_out(stock: u32, sold: u32) -> bool {\n"
            "    left_after(stock, sold) == 0\n"
            "}\n"
        ),
        fixed=(
            "// Stock counts are never negative.\n"
            "fn left_after(stock: u32, sold: u32) -> u32 {\n"
            "    stock.saturating_sub(sold)\n"
            "}\n"
            "\n"
            "fn sold_out(stock: u32, sold: u32) -> bool {\n"
            "    left_after(stock, sold) == 0\n"
            "}\n"
        ),
        solve=_left_after,
        reported=(3, 5),
        cases=((10, 4), (4, 4), (0, 0), (3, 5), (0, 2), (7, 100)),
        cause="checked_sub returns None when the subtraction would go below "
              "zero, and unwrap_or(stock) turns that None into the ORIGINAL "
              "stock instead of 0.",
        decoys=(
            "checked_sub wraps round to a huge number when it goes below zero.",
            "sold_out is called first and changes the stock.",
            "u32 cannot hold the number 0.",
        ),
        lesson="checked_sub says 'this does not fit' with None - what to do "
               "then is your decision, and falling back to the old value is "
               "rarely it. For 'not below zero' use saturating_sub, which "
               "stops at 0.",
        hint="Sell more than there is: left_after(3, 5).",
        checks=(((3, 5), 0), ((10, 4), 6), ((4, 4), 0), ((0, 2), 0)),
    ),
    Hunt(
        id="hunt-rs-split-space",
        title="Two spaces make an extra word",
        family=RUST,
        language="rust",
        level=2,
        report="'one  two' (with two spaces between) is counted as 3 words, "
               "and an empty text as 1. Text with single spaces is counted "
               "correctly.",
        name="word_count",
        params=("text",),
        types=("&str",),
        returns="usize",
        start=(
            "// Count the words in a line of text.\n"
            "fn words(text: &str) -> Vec<&str> {\n"
            "    text.split(' ').collect()\n"
            "}\n"
            "\n"
            "fn word_count(text: &str) -> usize {\n"
            "    words(text).len()\n"
            "}\n"
        ),
        fixed=(
            "// Count the words in a line of text.\n"
            "fn words(text: &str) -> Vec<&str> {\n"
            "    text.split_whitespace().collect()\n"
            "}\n"
            "\n"
            "fn word_count(text: &str) -> usize {\n"
            "    words(text).len()\n"
            "}\n"
        ),
        solve=_word_count,
        reported=("one  two",),
        cases=(("",), ("hello",), ("a b c",), ("one  two",), ("  hi  ",)),
        cause="split(' ') cuts at EVERY single space, so two spaces in a row "
              "(or a space at either end) leave an empty piece that is "
              "counted as a word.",
        decoys=(
            "collect() adds one extra item to every Vec it builds.",
            "len() on a Vec counts its bytes, not its items.",
            "split(' ') only splits at the first space it finds.",
        ),
        lesson="split with a pattern keeps the empty pieces between "
               "neighbouring separators. split_whitespace() treats any run "
               "of spaces, tabs and newlines as one gap and skips empties.",
        hint="Type two spaces between the words: word_count(\"one  two\").",
        checks=((("one  two",), 2), (("",), 0), (("a b c",), 3), (("  hi  ",), 1)),
    ),
    Hunt(
        id="hunt-rs-retain-zero",
        title="Zero readings disappear",
        family=RUST,
        language="rust",
        level=3,
        report="Removing the negative readings from [0, 5] leaves just [5]. "
               "Zero is a real reading and should stay. Lists with no zero "
               "are cleaned correctly.",
        name="without_negatives",
        params=("nums",),
        types=("Vec<i32>",),
        returns="Vec<i32>",
        start=(
            "// Remove the negative readings; zero is a real reading.\n"
            "fn keep_readings(readings: &mut Vec<i32>) {\n"
            "    readings.retain(|&n| n > 0);\n"
            "}\n"
            "\n"
            "fn without_negatives(nums: Vec<i32>) -> Vec<i32> {\n"
            "    let mut kept = nums;\n"
            "    keep_readings(&mut kept);\n"
            "    kept\n"
            "}\n"
        ),
        fixed=(
            "// Remove the negative readings; zero is a real reading.\n"
            "fn keep_readings(readings: &mut Vec<i32>) {\n"
            "    readings.retain(|&n| n >= 0);\n"
            "}\n"
            "\n"
            "fn without_negatives(nums: Vec<i32>) -> Vec<i32> {\n"
            "    let mut kept = nums;\n"
            "    keep_readings(&mut kept);\n"
            "    kept\n"
            "}\n"
        ),
        solve=_without_negatives,
        reported=([0, 5],),
        cases=(([],), ([1, 2, 3],), ([-1, 2, -3],), ([0, 5],), ([0],)),
        cause="retain KEEPS the items for which the closure is true, and "
              "`n > 0` is false for 0, so zero is thrown away with the "
              "negatives. The test should be n >= 0.",
        decoys=(
            "retain removes the items for which the closure is true.",
            "`&n` in the closure copies the reading, so retain cannot remove it.",
            "kept is a copy of nums, so the original is not cleaned.",
        ),
        lesson="retain(f) keeps what f says yes to - say what you want to "
               "KEEP, and check the boundary (> or >=) with the value that "
               "sits on it, here 0.",
        hint="Include a zero in the readings: without_negatives(vec![0, 5]).",
        checks=((([0, 5],), [0, 5]), (([-1, 2, -3],), [2]), (([],), [])),
    ),
    Hunt(
        id="hunt-rs-or-insert",
        title="Every word is counted one too many",
        family=RUST,
        language="rust",
        level=3,
        report="In ['a', 'a', 'b'] the word 'a' is counted 3 times, not 2. "
               "A word that is not in the list correctly counts 0.",
        name="count_of",
        params=("words", "target"),
        types=("Vec<String>", "&str"),
        returns="u32",
        start=(
            "use std::collections::HashMap;\n"
            "\n"
            "fn tally(words: &[String]) -> HashMap<String, u32> {\n"
            "    let mut counts = HashMap::new();\n"
            "    for w in words {\n"
            "        *counts.entry(w.clone()).or_insert(1) += 1;\n"
            "    }\n"
            "    counts\n"
            "}\n"
            "\n"
            "fn count_of(words: Vec<String>, target: &str) -> u32 {\n"
            "    tally(&words).get(target).copied().unwrap_or(0)\n"
            "}\n"
        ),
        fixed=(
            "use std::collections::HashMap;\n"
            "\n"
            "fn tally(words: &[String]) -> HashMap<String, u32> {\n"
            "    let mut counts = HashMap::new();\n"
            "    for w in words {\n"
            "        *counts.entry(w.clone()).or_insert(0) += 1;\n"
            "    }\n"
            "    counts\n"
            "}\n"
            "\n"
            "fn count_of(words: Vec<String>, target: &str) -> u32 {\n"
            "    tally(&words).get(target).copied().unwrap_or(0)\n"
            "}\n"
        ),
        solve=_count_of,
        reported=(["a", "a", "b"], "a"),
        cases=(([], "a"), (["a"], "b"), (["b", "c"], "c"), (["a"], "a"), (["a", "a", "b"], "a")),
        cause="or_insert(1) puts a 1 into a word's slot the FIRST time it is "
              "seen and the `+= 1` then adds another, so every word that "
              "appears starts at 2.",
        decoys=(
            "entry() adds the word to the map twice, once per loop.",
            "get(target) returns the count of the word before it.",
            "copied() adds one to the count it copies.",
        ),
        lesson="entry(k).or_insert(v) supplies the STARTING value for a new "
               "key, and the update after it still runs. For a counter the "
               "start is 0: *map.entry(k).or_insert(0) += 1.",
        hint="Count a word that appears: count_of(vec![\"a\"], \"a\").",
        checks=(((["a", "a", "b"], "a"), 2), ((["a"], "a"), 1), ((["a"], "b"), 0), (([], "a"), 0)),
    ),
    Hunt(
        id="hunt-rs-match-order",
        title="Nobody gets honors",
        family=RUST,
        language="rust",
        level=4,
        report="A score of 95 is labelled 'pass'; 90 and above should be "
               "'honors'. Scores below 90 are labelled correctly.",
        name="band",
        params=("score",),
        types=("u32",),
        returns="String",
        start=(
            "// Scores run from 0 to 100.\n"
            "fn label(score: u32) -> &'static str {\n"
            "    match score {\n"
            "        0..=59 => \"fail\",\n"
            "        60..=100 => \"pass\",\n"
            "        90..=100 => \"honors\",\n"
            "        _ => \"invalid\",\n"
            "    }\n"
            "}\n"
            "\n"
            "fn band(score: u32) -> String {\n"
            "    label(score).to_string()\n"
            "}\n"
        ),
        fixed=(
            "// Scores run from 0 to 100.\n"
            "fn label(score: u32) -> &'static str {\n"
            "    match score {\n"
            "        0..=59 => \"fail\",\n"
            "        60..=89 => \"pass\",\n"
            "        90..=100 => \"honors\",\n"
            "        _ => \"invalid\",\n"
            "    }\n"
            "}\n"
            "\n"
            "fn band(score: u32) -> String {\n"
            "    label(score).to_string()\n"
            "}\n"
        ),
        solve=_band,
        reported=(95,),
        cases=((0,), (40,), (75,), (89,), (90,), (95,), (100,), (101,)),
        cause="match takes the FIRST arm that fits, and 60..=100 already "
              "covers 90 to 100, so the honors arm below it can never run.",
        decoys=(
            "A range pattern 60..=100 stops before 100, so 100 is missed.",
            "match checks the arms from the bottom up.",
            "90..=100 is not allowed in a match on a u32.",
        ),
        lesson="Arms are tried top to bottom and the first fit wins, so a "
               "wide range written before a narrow one hides it (the "
               "compiler only hints with an 'unreachable pattern' warning). "
               "Keep the ranges from overlapping or put the narrow one first.",
        hint="Try a top score: band(95).",
        checks=(((95,), "honors"), ((75,), "pass"), ((40,), "fail"), ((101,), "invalid")),
    ),
    Hunt(
        id="hunt-rs-bytes-rev",
        title="'café' reverses into replacement marks",
        family=RUST,
        language="rust",
        level=4,
        report="Reversing 'abc' gives 'cba', but reversing 'café' gives "
               "a pair of replacement marks followed by 'fac' instead of "
               "'éfac'.",
        name="reverse_word",
        params=("word",),
        types=("&str",),
        returns="String",
        start=(
            "// Reverse a word, letter by letter.\n"
            "fn flip(word: &str) -> String {\n"
            "    String::from_utf8_lossy(&word.bytes().rev().collect::<Vec<u8>>()).to_string()\n"
            "}\n"
            "\n"
            "fn reverse_word(word: &str) -> String {\n"
            "    flip(word)\n"
            "}\n"
            "\n"
            "fn is_palindrome(word: &str) -> bool {\n"
            "    reverse_word(word) == word\n"
            "}\n"
        ),
        fixed=(
            "// Reverse a word, letter by letter.\n"
            "fn flip(word: &str) -> String {\n"
            "    word.chars().rev().collect()\n"
            "}\n"
            "\n"
            "fn reverse_word(word: &str) -> String {\n"
            "    flip(word)\n"
            "}\n"
            "\n"
            "fn is_palindrome(word: &str) -> bool {\n"
            "    reverse_word(word) == word\n"
            "}\n"
        ),
        solve=_reverse_word,
        reported=("café",),
        cases=(("",), ("abc",), ("a",), ("café",), ("naïve",)),
        cause="bytes() walks the UTF-8 BYTES, and a letter like 'é' is two "
              "of them; reversing the bytes puts each pair back to front, "
              "which is no longer valid text.",
        decoys=(
            "rev() cannot be used on text at all.",
            "from_utf8_lossy drops every letter that has an accent.",
            "collect::<Vec<u8>>() sorts the bytes before reversing them.",
        ),
        lesson="A Rust String is UTF-8: a letter can be several bytes. To "
               "reverse (or count, or index) by LETTER use chars(); bytes() "
               "is for when you really mean bytes.",
        hint="Use a word with an accent: reverse_word(\"café\").",
        checks=((("abc",), "cba"), (("café",), "éfac"), (("",), "")),
    ),
)
