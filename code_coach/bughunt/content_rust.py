"""Rust hunts: bugs the compiler lets through.

Rust's compiler stops a great deal - but not these, because each is code
that does exactly what it says, just not what was meant: `as` cutting a
number down to fit, `len()` counting bytes, `dedup` only removing
neighbours, unsigned subtraction wrapping round in a release build, and
`position` finding the first match when the last was wanted.

Run through kata/rust_harness.py, so each hunt gives one Rust type per
parameter and its return type. The same rules hold as for every hunt,
checked by tests/test_bughunt.py.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

RUST = "Rust"


def _to_byte(scores):
    return [max(0, min(255, s)) for s in scores]


def _long_names(names):
    return [n for n in names if len(n) > 3]


def _distinct(nums):
    return len(set(nums))


def _gap(a, b):
    return abs(a - b)


def _last_index(items, target):
    for i in range(len(items) - 1, -1, -1):
        if items[i] == target:
            return i
    return None


RUST_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-rs-as-truncates",
        title="A score of 300 shows as 44",
        family=RUST,
        language="rust",
        level=1,
        report="Scores are stored in a single byte, so anything over 255 should "
               "be kept at 255. A score of 300 comes out as 44. Scores under 255 "
               "are fine.",
        name="to_bytes",
        params=("scores",),
        types=("&[i32]",),
        returns="Vec<u8>",
        start=(
            "// Each score is kept in one byte.\n"
            "fn to_byte(score: i32) -> u8 {\n"
            "    score as u8\n"
            "}\n"
            "\n"
            "fn to_bytes(scores: &[i32]) -> Vec<u8> {\n"
            "    scores.iter().map(|&s| to_byte(s)).collect()\n"
            "}\n"
            "\n"
        ),
        fixed=(
            "// Each score is kept in one byte.\n"
            "fn to_byte(score: i32) -> u8 {\n"
            "    score.clamp(0, 255) as u8\n"
            "}\n"
            "\n"
            "fn to_bytes(scores: &[i32]) -> Vec<u8> {\n"
            "    scores.iter().map(|&s| to_byte(s)).collect()\n"
            "}\n"
            "\n"
        ),
        solve=_to_byte,
        reported=([300],),
        cases=(([],), ([10, 200],), ([255],), ([300],), ([0, 256, 100],)),
        cause="`as u8` does not check: it keeps the low 8 bits and drops the "
              "rest, so 300 (256 + 44) becomes 44 instead of stopping at 255.",
        decoys=(
            "u8 can only hold numbers below 100.",
            "map skips scores that are too large and the next one moves up.",
            "to_byte returns before the score has been converted.",
        ),
        lesson="`as` between integer types never fails and never complains - it "
               "wraps. Decide what out-of-range means: clamp it, or use "
               "u8::try_from(score), which returns an Err when it does not fit.",
        hint="Give it a score above 255: to_bytes(&[300]).",
        checks=((([300],), [255]), (([10, 200],), [10, 200]), (([0, 256, 100],), [0, 255, 100])),
    ),
    Hunt(
        id="hunt-rs-len-bytes",
        title="Zoë counts as a long name",
        family=RUST,
        language="rust",
        level=2,
        report="Names longer than 3 letters go on the long list. 'Zoë' has 3 "
               "letters and is on it anyway. Names without accents are sorted "
               "correctly.",
        name="long_names",
        params=("names",),
        types=("Vec<String>",),
        returns="Vec<String>",
        start=(
            "// Long names get their own list.\n"
            "fn is_long(name: &str) -> bool {\n"
            "    name.len() > 3\n"
            "}\n"
            "\n"
            "fn long_names(names: Vec<String>) -> Vec<String> {\n"
            "    names.into_iter().filter(|n| is_long(n)).collect()\n"
            "}\n"
            "\n"
        ),
        fixed=(
            "// Long names get their own list.\n"
            "fn is_long(name: &str) -> bool {\n"
            "    name.chars().count() > 3\n"
            "}\n"
            "\n"
            "fn long_names(names: Vec<String>) -> Vec<String> {\n"
            "    names.into_iter().filter(|n| is_long(n)).collect()\n"
            "}\n"
            "\n"
        ),
        solve=_long_names,
        reported=(["Zoë"],),
        cases=(([],), (["Ann", "Grace"],), (["Bo"],), (["Zoë"],), (["José", "Li"],)),
        cause="len() counts the BYTES of the UTF-8 text, and 'ë' takes two, so "
              "'Zoë' is 4 bytes long though it has 3 letters.",
        decoys=(
            "filter keeps the names that are NOT long.",
            "into_iter() changes the names to upper case.",
            "> 3 should be >= 3 for every name.",
        ),
        lesson="A Rust String is UTF-8, and len() is its size in bytes - right "
               "for buffers, wrong for 'how many letters'. chars().count() "
               "counts characters. Anything with accents or emoji shows the "
               "difference.",
        hint="Use a short name with an accent in it: long_names(vec![\"Zoë\"]).",
        checks=(((["Zoë"],), []), ((["Ann", "Grace"],), ["Grace"]), ((["José", "Li"],), ["José"])),
    ),
    Hunt(
        id="hunt-rs-dedup",
        title="Five different visitors, apparently",
        family=RUST,
        language="rust",
        level=2,
        report="The visitor log for [1, 2, 1, 2] says 4 different visitors. "
               "There were 2. When each visitor's visits come together, "
               "[1, 1, 2], the count is right.",
        name="distinct",
        params=("visits",),
        types=("Vec<i32>",),
        returns="usize",
        start=(
            "fn distinct(visits: Vec<i32>) -> usize {\n"
            "    let mut ids = visits;\n"
            "    ids.reverse();\n"
            "    ids.dedup();\n"
            "    ids.len()\n"
            "}\n"
            "\n"
            "fn main_report(visits: Vec<i32>) -> String {\n"
            "    format!(\"{} visitors\", distinct(visits))\n"
            "}\n"
        ),
        fixed=(
            "fn distinct(visits: Vec<i32>) -> usize {\n"
            "    let mut ids = visits;\n"
            "    ids.sort();\n"
            "    ids.dedup();\n"
            "    ids.len()\n"
            "}\n"
            "\n"
            "fn main_report(visits: Vec<i32>) -> String {\n"
            "    format!(\"{} visitors\", distinct(visits))\n"
            "}\n"
        ),
        solve=_distinct,
        reported=([1, 2, 1, 2],),
        cases=(([],), ([1, 1, 2],), ([7],), ([1, 2, 1, 2],), ([3, 3, 3],)),
        cause="The ids are reversed, not sorted, and dedup only removes a value "
              "that repeats the one right before it - so 1, 2, 1, 2 keeps all four.",
        decoys=(
            "len() counts the visits twice after dedup.",
            "dedup removes the first visit of each visitor.",
            "visits is moved into ids, so the original count is used.",
        ),
        lesson="dedup is for SORTED data - it collapses runs. Sort first, or "
               "collect into a HashSet and take its len(), which does not care "
               "about order.",
        hint="Let the same visitors come back in turn: distinct(vec![1, 2, 1, 2]).",
        checks=((([1, 2, 1, 2],), 2), (([1, 1, 2],), 2), (([],), 0)),
    ),
    Hunt(
        id="hunt-rs-unsigned-gap",
        title="3 days apart is four billion",
        family=RUST,
        language="rust",
        level=3,
        report="The gap between day 3 and day 10 is 7, which is right. The gap "
               "between day 10 and day 3 comes out as 4294967289.",
        name="gap",
        params=("a", "b"),
        types=("u32", "u32"),
        returns="u32",
        start=(
            "// Days are numbered from 0.\n"
            "fn gap(a: u32, b: u32) -> u32 {\n"
            "    b.wrapping_sub(a)\n"
            "}\n"
            "\n"
            "fn describe(a: u32, b: u32) -> String {\n"
            "    format!(\"{} days apart\", gap(a, b))\n"
            "}\n"
            "\n"
        ),
        fixed=(
            "// Days are numbered from 0.\n"
            "fn gap(a: u32, b: u32) -> u32 {\n"
            "    a.abs_diff(b)\n"
            "}\n"
            "\n"
            "fn describe(a: u32, b: u32) -> String {\n"
            "    format!(\"{} days apart\", gap(a, b))\n"
            "}\n"
            "\n"
        ),
        solve=_gap,
        reported=(10, 3),
        cases=((3, 10), (5, 5), (0, 1), (10, 3), (100, 1)),
        cause="u32 cannot go below zero, so 3 - 10 wraps round to the top of "
              "the range instead of giving -7 - and the gap should be 7 either way.",
        decoys=(
            "format! prints a u32 in a different number base.",
            "The days are numbered from 1, so the answer is one too high.",
            "gap is called with its arguments the wrong way round in describe.",
        ),
        lesson="Unsigned numbers wrap when they would go negative: a plain - "
               "panics in a debug build and wraps in release. For 'how far "
               "apart', use abs_diff; for a subtraction that may go below zero, "
               "use a signed type or checked_sub.",
        hint="Put the later day first: gap(10, 3).",
        checks=(((10, 3), 7), ((3, 10), 7), ((5, 5), 0)),
    ),
    Hunt(
        id="hunt-rs-first-not-last",
        title="The last time is the first time",
        family=RUST,
        language="rust",
        level=3,
        report="Asking where 'tea' was ordered LAST in ['tea', 'jam', 'tea'] "
               "says position 0. It should be 2. Items ordered only once are "
               "found correctly.",
        name="last_index",
        params=("items", "target"),
        types=("Vec<String>", "&str"),
        returns="Option<usize>",
        start=(
            "// Orders are kept in the order they were made.\n"
            "fn last_index(items: Vec<String>, target: &str) -> Option<usize> {\n"
            "    items.iter().position(|item| item == target)\n"
            "}\n"
            "\n"
            "fn ordered_again(items: Vec<String>, target: &str) -> bool {\n"
            "    last_index(items, target).is_some()\n"
            "}\n"
            "\n"
        ),
        fixed=(
            "// Orders are kept in the order they were made.\n"
            "fn last_index(items: Vec<String>, target: &str) -> Option<usize> {\n"
            "    items.iter().rposition(|item| item == target)\n"
            "}\n"
            "\n"
            "fn ordered_again(items: Vec<String>, target: &str) -> bool {\n"
            "    last_index(items, target).is_some()\n"
            "}\n"
            "\n"
        ),
        solve=_last_index,
        reported=(["tea", "jam", "tea"], "tea"),
        cases=(([], "tea"), (["jam"], "jam"), (["tea", "jam", "tea"], "tea"), (["a", "b"], "b"),
               (["x", "x", "x"], "x")),
        cause="position searches from the front and stops at the FIRST match; "
              "the last one needs rposition, which searches from the back.",
        decoys=(
            "iter() visits the items in reverse order.",
            "Option<usize> cannot hold a position larger than 1.",
            "The comparison item == target compares lengths, not text.",
        ),
        lesson="position and rposition, find and rfind: Rust gives each search "
               "both directions. When there can be more than one match, decide "
               "which one you mean.",
        hint="Order something twice: last_index(vec![\"tea\", \"jam\", \"tea\"], \"tea\").",
        checks=(((["tea", "jam", "tea"], "tea"), 2), ((["jam"], "jam"), 0), (([], "tea"), None)),
    ),
)
