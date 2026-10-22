"""Strings Pack, JavaScript side: the same eight activities with JavaScript's rules.

Case & Trim, Split & Join, Find It, Replace It, Format It, String Math,
Char Codes, Text Check. The hand models of the string methods are shared with
the Python side (`_strings_py.py`); what is written here is where JavaScript
differs - `replace` changes only the first match, `split` with a limit drops
the rest, `split()` with no argument does not split on spaces, `toFixed` rounds
halves up, `%` keeps the sign of the left side - and the JavaScript spellings
(`toUpperCase`, `indexOf`, `padStart`, `charCodeAt`, `includes`...).
tests/test_brain_packs.py runs every template through the real node.
"""

from __future__ import annotations

import random
from string import Template
from typing import Any, Callable

from ._model import WORDS, Maker, ipow, js_show, tmod, upper, yes_no_js
from ._strings_py import (PALINDROMES, PAIRS, P, _distinct, chr_of, count_sub, digits_in, fixed,
                          find_in, is_digit, join, lex_less, lower, ord_of, pad_left, pad_right, py_replace,
                          py_split, reverse_text, rfind_in, sorted_chars, strip, title, zero_pad)
from .items import Item

# ── JavaScript's own models ─────────────────────────────────────────────


def js_split(text: str, sep: str, limit: int | None = None) -> list[str]:
    """text.split(sep, limit): an empty sep gives the letters; a limit keeps only the first pieces."""
    pieces = list(text) if sep == "" else py_split(text, sep)
    return pieces if limit is None else pieces[:limit]


def js_last_index_of(text: str, sub: str, start: int) -> int:
    """lastIndexOf(sub, start): the last match that begins at or before `start`."""
    for i in range(min(start, len(text) - len(sub)), -1, -1):
        if text[i:i + len(sub)] == sub:
            return i
    return -1


def js_pad(text: str, width: int, fill: str, at_start: bool) -> str:
    """padStart / padEnd: the fill repeats as often as needed and is cut to fit."""
    if width <= len(text) or fill == "":
        return text
    pad = ""
    while len(pad) < width - len(text):
        pad += fill[len(pad) % len(fill)]
    return pad + text if at_start else text + pad


def show(value: Any) -> str:
    return value if isinstance(value, str) else js_show(value)


def J(fmt: str, ans: str | Callable[[dict], Any], why: str | Callable[[dict], str] = "",
      check: Callable[[str], str] | None = None) -> Maker:
    """A JavaScript template: the same holes as the Python side (`P`), answers printed as console.log prints them."""
    def make(rng: random.Random) -> Item:
        p = P(rng)
        prompt = Template(fmt).substitute(p)
        got = show(ans(p) if callable(ans) else ans)
        why_text = why(p) if callable(why) else Template(why).safe_substitute(p)
        return Item(prompt, got, why_text, check=check(prompt) if check else "")
    make.__name__ = "j_" + fmt[:24].replace("\n", " ")
    return make


def JQ(fmt: str, truth: bool | Callable[[dict], bool], why: str | Callable[[dict], str] = "") -> Maker:
    return J(fmt, lambda p: "yes" if (truth(p) if callable(truth) else truth) else "no", why, check=yes_no_js)


# ── 1. Case & Trim ──────────────────────────────────────────────────────

UP = "toUpperCase() turns every letter into a capital and leaves the rest alone."
STR_NEW = "Strings never change: a method gives back a new string and the old one stays as it was."


CASE: list[Maker] = [
    J('"$w".toUpperCase()', lambda p: upper(p["w"]), UP),
    J('"$W".toLowerCase()', lambda p: lower(p["W"]), "toLowerCase() turns every capital into a small letter."),
    J('"$ph".toUpperCase()', lambda p: upper(p["ph"]), UP),
    J('"  $w  ".trim()', lambda p: p["w"], "trim() removes the spaces at both ends."),
    J('"  $w  ".length', lambda p: len(p["w"]) + 4, "Every space counts as a character: two each side."),
    J('"  $w  ".trim().length', lambda p: len(p["w"]), "trim() removes the four spaces, so only the word is left."),
    J('"  $w".trimStart()', lambda p: p["w"], "trimStart() removes whitespace from the left end."),
    J('"$w  ".trimEnd()', lambda p: p["w"], "trimEnd() removes whitespace from the right end."),
    J('"[" + "  $w ".trimStart() + "]"', lambda p: "[" + p["w"] + " ]", "trimStart() leaves the space on the right."),
    J('"[" + " $w  ".trimEnd() + "]"', lambda p: "[ " + p["w"] + "]", "trimEnd() leaves the space on the left."),
    J('"$w".toUpperCase().toLowerCase()', lambda p: p["w"], "Capitals first, then back to small: the word as it began."),
    J('"$w".toLowerCase().toUpperCase()', lambda p: p["WU"], "The last method decides: toUpperCase()."),
    J('"$w"[0].toUpperCase() + "$w".slice(1)', lambda p: p["W"], "Capitalise the first letter and glue the rest back on: JavaScript has no capitalize()."),
    J('"$w".charAt(0).toUpperCase() + "$w".slice(1)', lambda p: p["W"], "charAt(0) is the first letter; slice(1) is the rest."),
    J('"$WU".charAt(0) + "$WU".slice(1).toLowerCase()', lambda p: p["W"], "Keep the first letter, lower the rest."),
    J('"$ph".split(" ").map(s => s[0].toUpperCase() + s.slice(1)).join(" ")', lambda p: title(p["ph"]), "Capitalise each word, then join: title case by hand."),
    J('const s = "$w";\ns.toUpperCase();\ns', lambda p: p["w"], STR_NEW),
    J('let s = "$w";\ns = s.toUpperCase();\ns', lambda p: p["WU"], "s = s.toUpperCase() stores the new string under the old name."),
    J(r'"\t$w\n".trim()', lambda p: p["w"], "trim() removes tabs and newlines as well as spaces."),
    J(r'"\t$w\n".length', lambda p: len(p["w"]) + 2, r"\t and \n are one character each."),
    J(r'" \t\n ".trim().length', "0", "Nothing but whitespace: trim() leaves the empty string."),
    J('"  $ph  ".trim().toUpperCase()', lambda p: upper(p["ph"]), "trim first, then upper-case: the inner space stays."),
    J('"$w".toUpperCase() === "$WU"', "true", "Both are the same capitals."),
    J('"$W".toLowerCase() === "$w"', "true", "toLowerCase() gives back the small word."),
    J('"$w".toUpperCase()[0]', lambda p: upper(p["w"][0]), "Upper-case first, then take the first letter."),
    J('"$w".at(-1).toUpperCase()', lambda p: upper(p["w"][-1]), "at(-1) is the last letter."),
    J('"$w"[9]', "undefined", "Past the end an index gives undefined, not an error."),
    J('"$w".charAt(9).length', "0", "charAt past the end gives an empty string, whose length is 0."),
    J('"$mix".toLowerCase()', lambda p: lower(p["mix"]), "Every letter becomes small."),
    J('"$mix".toUpperCase() === "$mix"', "false", "Some letters in the original are small, so they differ."),
    J('"$ph".toUpperCase().split(" ")', lambda p: [upper(p["w"]), upper(p["v"])], "Upper-case first, then split at the space."),
    J('typeof "$w".trim()', "string", "trim() gives a string back."),
    J('"  $w  ".trim() === "$w"', "true", "After trim() only the word is left."),
    J('"$w".toUpperCase().length', lambda p: len(p["w"]), "Changing case never changes the length."),
    J('"$w".toUpperCase().charAt(1)', lambda p: upper(p["w"][1]), "The second letter, as a capital."),
    J('const name = "$W";\nname.toLowerCase() === name', "false", "toLowerCase() makes a different string from the original."),
]

# ── 2. Split & Join ─────────────────────────────────────────────────────

SPL = "split(sep) cuts at every separator and gives an array of the pieces."


def _l3(p: dict) -> list[str]:
    return [p["s1"], p["s2"], p["s3"]]


SPLIT: list[Maker] = [
    J('"$csv".split(",")', _l3, SPL),
    J('"$sp3".split(" ")', _l3, SPL),
    J('"$csv".split(",").length', "3", "Two commas make three pieces."),
    J('"$csv".split(",")[1]', lambda p: p["s2"], "split gives an array; [1] is its second piece."),
    J('"$csv".split(",", 2)', lambda p: [p["s1"], p["s2"]], "The second argument is how many pieces to keep: the rest is thrown away (Python keeps it)."),
    J('"$s1,,$s2".split(",")', lambda p: [p["s1"], "", p["s2"]], "Two separators in a row leave an empty piece."),
    J('"$s1  $s2".split(" ")', lambda p: [p["s1"], "", p["s2"]], "Two spaces leave an empty piece between them."),
    J('"$s1  $s2".split(" ").length', "3", "The empty piece counts."),
    J('"$s1 $s2".split()', lambda p: [p["s1"] + " " + p["s2"]], "With no separator, split does not cut at spaces: you get the whole string in an array."),
    J('"$s1 $s2".split().length', "1", "One piece: JavaScript's split() is not Python's."),
    J(r'"$s1  $s2".split(/\s+/)', lambda p: [p["s1"], p["s2"]], r"The pattern /\s+/ means a run of whitespace, so this cuts like Python's split()."),
    J('"".split(",")', lambda p: [""], "Splitting the empty string on a separator gives one empty piece."),
    J('"".split("")', lambda p: [], "Splitting the empty string into letters gives nothing."),
    J('"".split(",").length', "1", "One empty piece."),
    J('"$s1,$s2,".split(",")', lambda p: [p["s1"], p["s2"], ""], "A separator at the end leaves an empty piece."),
    J('"$s1".split("")', lambda p: list(p["s1"]), 'split("") gives one piece per letter.'),
    J('"$w".split("").reverse().join("")', lambda p: reverse_text(p["w"]), "Letters, reversed, glued back: the usual way to reverse a string."),
    J('"$w".split("").sort().join("")', lambda p: "".join(sorted_chars(p["w"])), "The letters in alphabetical order."),
    J('["$s1", "$s2", "$s3"].join("-")', lambda p: join("-", _l3(p)), "join puts the string between the items."),
    J('["$s1", "$s2"].join()', lambda p: p["s1"] + "," + p["s2"], "With no argument, join uses a comma."),
    J('["$s1", "$s2"].join("")', lambda p: p["s1"] + p["s2"], "An empty separator glues the items together."),
    J('["$s1", "$s2"].join(", ")', lambda p: p["s1"] + ", " + p["s2"], "The separator goes between items, not at the ends."),
    J('"$csv".split(",").join(" ")', lambda p: join(" ", _l3(p)), "Split on commas, then join with spaces."),
    J('"$sp3".split(" ").reverse().join(" ")', lambda p: join(" ", _l3(p)[::-1]), "Reverse the word order, then join."),
    J('"$sp3".split(" ").reverse()', lambda p: _l3(p)[::-1], "reverse() flips the array in place and returns it."),
    J('"$a $b".split(" ").map(Number)', lambda p: [p["a"], p["b"]], "map(Number) turns each piece into a number."),
    J('"$a,$b,$d".split(",").map(Number).reduce((x, y) => x + y, 0)', lambda p: p["a"] + p["b"] + p["d"], "Split, convert to numbers, add them up."),
    J('"$a $b".split(" ")[0] + "$a $b".split(" ")[1]', lambda p: str(p["a"]) + str(p["b"]), "The pieces are strings, so + joins them."),
    J('[$a, $b, $d].join("+")', lambda p: f"{p['a']}+{p['b']}+{p['d']}", "join turns the numbers into text with + between."),
    J('[1, null, 3].join("-")', "1--3", "null becomes an empty string in join."),
    J('[1, [2, 3]].join("-")', "1-2,3", "The inner array becomes the text 2,3."),
    J('"$s1=$a".split("=")[1]', lambda p: str(p["a"]), "The piece after the = (as text)."),
    J('"$csv".split(",").at(-1)', lambda p: p["s3"], "The last piece."),
    J('"$w".split("$x")', lambda p: js_split(p["w"], p["x"]), "The letter is the separator and is thrown away; a missing letter leaves the word whole."),
    J('"$w".split("$x").length', lambda p: len(js_split(p["w"], p["x"])), "One more piece than there are separators."),
    J(r'"$s1 $s2\n$s3".split("\n")', lambda p: [p["s1"] + " " + p["s2"], p["s3"]], r"Cut at the newline (\n)."),
    J('"$sp3".split(" ", 1)', lambda p: [p["s1"]], "A limit of 1 keeps only the first piece."),
    J('"$s1-$s2-$s3".split("-", 2)', lambda p: [p["s1"], p["s2"]], "A limit of 2 keeps two pieces."),
    J('"-".repeat(3).split("-")', lambda p: ["", "", "", ""], "Three separators make four pieces, all empty."),
]

# ── 3. Find It ──────────────────────────────────────────────────────────

FIRST = "indexOf gives the position of the first match, counting from 0."
MISS = "indexOf gives -1 when there is no match."

FIND: list[Maker] = [
    J('"$w".indexOf("$c")', lambda p: find_in(p["w"], p["c"]), FIRST),
    J('"$w".indexOf("$q")', "-1", MISS),
    J('"$w".lastIndexOf("$c")', lambda p: rfind_in(p["w"], p["c"]), "lastIndexOf searches from the right: the last match."),
    J('"$w".includes("$c")', "true", "includes says whether it is in there at all."),
    J('"$w".includes("$q")', "false", "It is not in the word."),
    J('"$w".indexOf("$c") === -1', "false", "It is found, so the position is not -1."),
    J('"$w".indexOf("$sub")', lambda p: find_in(p["w"], p["sub"]), "Two letters in a row are found as a unit."),
    J('"$w".indexOf("$c", 1)', lambda p: find_in(p["w"], p["c"], 1), "The second argument is where to start looking."),
    J('"$w".indexOf("$c", 2)', lambda p: find_in(p["w"], p["c"], 2), "Start looking at position 2: earlier matches are skipped."),
    J('"$w".indexOf("$c", -5)', lambda p: find_in(p["w"], p["c"], 0), "A negative start counts as 0 in JavaScript (Python counts it from the end)."),
    J('"$w".lastIndexOf("$c", 1)', lambda p: js_last_index_of(p["w"], p["c"], 1), "The second argument is where to start looking backwards from."),
    J('"$ph".indexOf(" ")', lambda p: len(p["w"]), "The space comes right after the first word."),
    J('"$ph".indexOf("$v")', lambda p: find_in(p["ph"], p["v"]), "The second word starts after the first and the space."),
    J('"$ph".lastIndexOf("$c")', lambda p: rfind_in(p["ph"], p["c"]), "The last match in the whole text."),
    J('"$w".indexOf("")', "0", "The empty string is found at once, at position 0."),
    J('"$w".indexOf("$C")', "-1", "The capital is a different character: not found."),
    J('"$w".split("$c").length - 1', lambda p: count_sub(p["w"], p["c"]), "One fewer piece than the number of matches: a way to count."),
    J('"$w".replaceAll("$c", "").length', lambda p: len(p["w"]) - count_sub(p["w"], p["c"]), "Delete the matches and see how much is left."),
    J('"$w".slice("$w".indexOf("$c"))', lambda p: p["w"][find_in(p["w"], p["c"]):], "From the first match to the end."),
    J('"$ph".slice(0, "$ph".indexOf(" "))', lambda p: p["w"], "Everything before the first space: the first word."),
    J('"$ph".slice("$ph".indexOf(" ") + 1)', lambda p: p["v"], "Everything after the first space: the second word."),
    J('"$w".startsWith("$z0")', "true", "The word begins with its first letter."),
    J('"$w".endsWith("$z1")', "true", "The word ends with its last letter."),
    J('"$w".startsWith("$c", 1)', lambda p: p["w"][1:2] == p["c"], "The second argument is the position to start checking at."),
    J('"$w".endsWith("$c", 2)', lambda p: p["w"][1] == p["c"], "The second argument pretends the string is that long: only 2 letters are looked at."),
    J('"$w".search("$c")', lambda p: find_in(p["w"], p["c"]), "search is indexOf for patterns; a plain letter works the same."),
    J('"banana".indexOf("an")', "1", FIRST),
    J('"banana".lastIndexOf("an")', "3", "The last one starts at 3."),
    J('"$w".charAt("$w".indexOf("$c"))', lambda p: p["c"], "The letter at the position of the letter is itself."),
    J('"$w".indexOf("$c") !== "$w".lastIndexOf("$c")', lambda p: find_in(p["w"], p["c"]) != rfind_in(p["w"], p["c"]), "Different only when the letter appears more than once."),
    J('"$w".indexOf("$w")', "0", "The whole word is found at the start."),
    J('"$w".indexOf("${w}s")', "-1", "The longer text is not inside the shorter."),
    J('"$w$v".indexOf("$v")', lambda p: find_in(p["w"] + p["v"], p["v"]), "The second word starts where the first ends."),
    J('"$ph".includes(" ")', "true", "There is a space."),
    J('"$W".indexOf("$z0")', lambda p: find_in(p["W"], p["z0"]), "Searching is case sensitive: f is not F."),
    J('String($num).indexOf("$dg")', lambda p: find_in(p["num"], p["dg"]), "String() makes it text, so you can look for a digit."),
    J('String($num).split("$dg").length - 1', lambda p: count_sub(p["num"], p["dg"]), "Count how often the digit appears."),
]

# ── 4. Replace It ───────────────────────────────────────────────────────

ONE = "replace with a string changes only the first match."
ALL = "replaceAll changes every match."


def _ci(text: str, ch: str, new: str) -> str:
    """The case-insensitive replace of one letter, everywhere."""
    return "".join(new if lower(c) == ch else c for c in text)


REPLACE: list[Maker] = [
    J('"$w".replace("$c", "$x")', lambda p: py_replace(p["w"], p["c"], p["x"], 1), ONE),
    J('"$w".replaceAll("$c", "$x")', lambda p: py_replace(p["w"], p["c"], p["x"]), ALL),
    J('"$w".replace("$c", "")', lambda p: py_replace(p["w"], p["c"], "", 1), "Only the first match is deleted."),
    J('"$w".replaceAll("$c", "")', lambda p: py_replace(p["w"], p["c"], ""), "Every match is deleted."),
    J('"$w".replace("$c", "-").replace("$c", "-")', lambda p: py_replace(py_replace(p["w"], p["c"], "-", 1), p["c"], "-", 1),
      "Each replace changes one match, so two in a row change two."),
    J('"$w".replace(/$c/g, "-")', lambda p: py_replace(p["w"], p["c"], "-"), "A pattern with the g flag replaces every match."),
    J('"$W".replace(/$z0/gi, "-")', lambda p: _ci(p["W"], p["z0"], "-"), "The i flag ignores case, the g flag replaces all."),
    J('"$ph".replaceAll(" ", "")', lambda p: p["w"] + p["v"], "Deleting the space glues the words."),
    J('"$ph".replace(" ", "_")', lambda p: p["w"] + "_" + p["v"], "The only space is the first match."),
    J('"$ph3".replace(" ", "-")', lambda p: py_replace(p["ph3"], " ", "-", 1), ONE),
    J('"$ph3".replaceAll(" ", "-")', lambda p: py_replace(p["ph3"], " ", "-"), ALL),
    J('"aaa".replaceAll("aa", "b")', "ba", "Matches do not overlap: one aa is replaced, one a is left."),
    J('"abc".replace("", "-")', "-abc", "The empty string matches before the first letter, and replace uses only the first match."),
    J('"abc".replaceAll("", "-")', "-a-b-c-", "The empty string matches between every letter and at both ends."),
    J('"$w".replace("$C", "-")', lambda p: p["w"], "Case matters: the capital is not in the word."),
    J('"$w".toUpperCase().replaceAll("$C", "-")', lambda p: py_replace(p["WU"], p["C"], "-"), "Upper-case first, so the capital does match."),
    J('"$w".split("$c").join("-")', lambda p: join("-", py_split(p["w"], p["c"])), "The old way to replace all: split on it, join with the new text."),
    J('const s = "$w";\ns.replace("$c", "-");\ns', lambda p: p["w"], STR_NEW),
    J('let s = "$w";\ns = s.replace("$c", "-");\ns', lambda p: py_replace(p["w"], p["c"], "-", 1), "s = s.replace(...) keeps the new string; only the first match changed."),
    J('"$w".replaceAll("$c", "").length', lambda p: len(p["w"]) - count_sub(p["w"], p["c"]), "The word, minus each match."),
    J('"$w".replaceAll("$c", "--").length', lambda p: len(p["w"]) + count_sub(p["w"], p["c"]), "Each match grows by one character."),
    J('"banana".replaceAll("a", "o")', "bonono", ALL),
    J('"banana".replace("a", "o")', "bonana", ONE),
    J('"$w".replace("$w", "$v")', lambda p: p["v"], "The whole string matches, so it is replaced whole."),
    J('"$a+$b".replace("+", "-")', lambda p: f"{p['a']}-{p['b']}", ONE),
    J('String($num).replaceAll("$dg", "0")', lambda p: py_replace(p["num"], p["dg"], "0"), "Every such digit becomes 0."),
    J('"$w".replaceAll("$sub", "")', lambda p: py_replace(p["w"], p["sub"], ""), "The pair is deleted."),
    J('"   $w   ".replaceAll(" ", "")', lambda p: p["w"], "Deleting every space."),
    J('"$x$y$x".replace("$x", "$y").replace("$y", "$x")', lambda p: py_replace(py_replace(p["x"] + p["y"] + p["x"], p["x"], p["y"], 1), p["y"], p["x"], 1),
      "Each replace changes just one match, one after the other."),
    J('"$w".replaceAll("e", "3").replaceAll("o", "0")', lambda p: py_replace(py_replace(p["w"], "e", "3"), "o", "0"), "Two replaces: e first, then o."),
    J('"$ph".replace("$w", "").trim()', lambda p: strip(py_replace(p["ph"], p["w"], "", 1)), "Remove the first word, then the leftover space with trim()."),
]

# ── 5. Format It ────────────────────────────────────────────────────────

PAD = "padStart(width, fill) adds the fill on the left until the text is that long."
FIX = "toFixed(n) writes the number with n decimal places, as text."
TIE = "toFixed rounds an exact halfway to the larger number (Python's formats round to even)."


def _fx(p: dict, key: str, places: int) -> str:
    return fixed(p["dw"], p["f" + key[-1]], places)


FORMAT: list[Maker] = [
    J('String($a).padStart(3, "0")', lambda p: zero_pad(str(p["a"]), 3), PAD),
    J('String($n).padStart(5, "0")', lambda p: zero_pad(str(p["n"]), 5), PAD),
    J('String($a).padStart(String($n).length, "0")', lambda p: zero_pad(str(p["a"]), len(str(p["n"]))), "Pad to the length of the other number's text."),
    J('"$w".padEnd(9, "*")', lambda p: pad_right(p["w"], 9, "*"), "padEnd adds the fill on the right."),
    J('"$w".padStart(9, "-")', lambda p: pad_left(p["w"], 9, "-"), PAD),
    J('"$a".padStart(5, "ab")', lambda p: js_pad(str(p["a"]), 5, "ab", True), "A longer fill repeats and is cut to fit."),
    J('"$a".padEnd(5, "xy")', lambda p: js_pad(str(p["a"]), 5, "xy", False), "The fill repeats and is cut where the width ends."),
    J('"$w".padStart(11, "ab")', lambda p: js_pad(p["w"], 11, "ab", True), "The fill starts again at its first letter each time."),
    J('"$w".padEnd(10, "12")', lambda p: js_pad(p["w"], 10, "12", False), "The fill repeats until the text is 10 long."),
    J('"$w".padStart(2, "*")', lambda p: p["w"], "The width is smaller than the word: nothing is added."),
    J('"$w".padEnd(3, "*")', lambda p: p["w"], "Already at least 3 long: unchanged."),
    J('($dec2).toFixed(1)', lambda p: _fx(p, "dec2", 1), FIX),
    J('($dec3).toFixed(2)', lambda p: _fx(p, "dec3", 2), FIX),
    J('($dec1).toFixed(0)', lambda p: _fx(p, "dec1", 0), "toFixed(0) rounds to a whole number, as text."),
    J('($dec3).toFixed(2).padStart(8, "0")', lambda p: zero_pad(_fx(p, "dec3", 2), 8), "toFixed gives a string, so padStart works on it."),
    J('($dec3).toFixed(2).length', lambda p: len(_fx(p, "dec3", 2)), "The text includes the point and the two decimals."),
    J('($dec3).toFixed(2) + "%"', lambda p: _fx(p, "dec3", 2) + "%", "toFixed gives text, so + adds the sign after it."),
    J('(2.5).toFixed(0)', "3", TIE),
    J('(3.5).toFixed(0)', "4", TIE),
    J('(0.5).toFixed(0)', "1", TIE),
    J('(0.25).toFixed(1)', "0.3", TIE),
    J('(0.75).toFixed(1)', "0.8", TIE),
    J('(0.125).toFixed(2)', "0.13", TIE),
    J('(1 / 3).toFixed(3)', "0.333", "A third is 0.3333..., cut to three places."),
    J('($n).toString(2)', lambda p: digits_in(p["n"], 2), "toString(2) writes the number in binary."),
    J('($n).toString(16)', lambda p: digits_in(p["n"], 16), "toString(16) writes it in hexadecimal."),
    J('($n).toString(8)', lambda p: digits_in(p["n"], 8), "toString(8) writes it in octal (base 8)."),
    J('($n).toString(2).padStart(8, "0")', lambda p: zero_pad(digits_in(p["n"], 2), 8), "Binary, padded with zeros to 8 digits."),
    J('($n * 7).toString(16).toUpperCase()', lambda p: digits_in(p["n"] * 7, 16, True), "The product in hex, then in capitals."),
    J('"$w" + $a', lambda p: p["w"] + str(p["a"]), "A string and a number: + joins them as text."),
    J('$a + $b + "$w"', lambda p: str(p["a"] + p["b"]) + p["w"], "Left to right: the numbers add first, then the string joins."),
    J('"$w" + $a + $b', lambda p: p["w"] + str(p["a"]) + str(p["b"]), "Left to right: it is text from the start, so both join."),
    J('"$w" + ($a + $b)', lambda p: p["w"] + str(p["a"] + p["b"]), "The brackets add first."),
    J('"Total: " + $a + $b', lambda p: f"Total: {p['a']}{p['b']}", "Text first, so each number is joined, not added."),
    J('"Total: " + ($a + $b)', lambda p: f"Total: {p['a'] + p['b']}", "The brackets add first, then join."),
    J('[$a, $b].join(":")', lambda p: f"{p['a']}:{p['b']}", "join builds text with : between."),
    J('String($n).length', "2", "Two digits, two characters."),
    J('Number("00$a")', lambda p: p["a"], "Number() reads the text as a number: the zeros vanish."),
    J('parseInt("$a$b")', lambda p: int(str(p["a"]) + str(p["b"])), "The digits read as one number."),
    J('("$w" + "-").repeat(2)', lambda p: (p["w"] + "-") * 2, "Join first, then repeat the pair."),
    J('"$w".concat("-", $a)', lambda p: p["w"] + "-" + str(p["a"]), "concat joins all its arguments, turning numbers into text."),
    J('String([$a, $b])', lambda p: f"{p['a']},{p['b']}", "An array becomes its items with commas."),
    J('"" + [$a, $b]', lambda p: f"{p['a']},{p['b']}", "Joining an array to a string turns it into text with commas."),
    J('JSON.stringify("$w")', lambda p: '"' + p["w"] + '"', "JSON.stringify keeps the quotes round a string."),
    J('JSON.stringify([$a, $b])', lambda p: f"[{p['a']},{p['b']}]", "JSON text has no spaces."),
    J('$a + "" + $b', lambda p: str(p["a"]) + str(p["b"]), "The empty string makes everything after it text."),
]

# ── 6. String Math ──────────────────────────────────────────────────────

VOW = "aeiou"


def _vowels(text: str) -> int:
    return sum(1 for ch in text if ch in VOW)


MATH: list[Maker] = [
    J('"$w".length', lambda p: len(p["w"]), "length counts the characters."),
    J('("$w" + "$v").length', lambda p: len(p["w"]) + len(p["v"]), "+ joins them, and the length is the sum."),
    J('"$w".repeat($k)', lambda p: p["w"] * p["k"], "repeat(k) gives k copies joined."),
    J('"$x".repeat($a)', lambda p: p["x"] * p["a"], "The letter, repeated."),
    J('"$a" + "$b"', lambda p: str(p["a"]) + str(p["b"]), "Both are text, so + joins them."),
    J('"$a" * "$b"', lambda p: p["a"] * p["b"], "* only means multiply, so both texts become numbers."),
    J('"$a" - "$b"', lambda p: p["a"] - p["b"], "- only means subtract, so both texts become numbers."),
    J('"$a" + +"$b"', lambda p: str(p["a"]) + str(p["b"]), "The unary + makes the second a number, but then + joins text and number as text."),
    J('$a + $b', lambda p: p["a"] + p["b"], "Both are numbers, so + adds them."),
    J('"$a" + $b - $d', lambda p: int(str(p["a"]) + str(p["b"])) - p["d"], "Left to right: join into the text, then - turns it into a number."),
    J('"$w".repeat($k).length', lambda p: len(p["w"]) * p["k"], "Repeating k times multiplies the length by k."),
    J('"$ph".length', lambda p: len(p["w"]) + len(p["v"]) + 1, "Both words and the space between."),
    J('"".length', "0", "The empty string has no characters."),
    J(r'"\n".length', "1", r"\n is a single newline character."),
    J('"$w".concat("$v")', lambda p: p["w"] + p["v"], "concat joins in the order written."),
    J('"$w".length * $k', lambda p: len(p["w"]) * p["k"], "A number times a number."),
    J('"$x" + "$y".repeat($k)', lambda p: p["x"] + p["y"] * p["k"], "The method binds to the nearest string: only the y repeats."),
    J('("$x" + "$y").repeat($k)', lambda p: (p["x"] + p["y"]) * p["k"], "The brackets go first: the pair repeats."),
    J('"$w".repeat(0).length', "0", "Zero copies: the empty string."),
    J('String($a * $b).length', lambda p: len(str(p["a"] * p["b"])), "Work out the product, then count its digits."),
    J('"b" + "a" + +"a" + "a"', "baNaNa", 'The +"a" is a number: not-a-number, NaN, which joins as the text "NaN".'),
    J('"$w".split("").filter(c => "aeiou".includes(c)).length', lambda p: _vowels(p["w"]), "Keep the vowels and count them."),
    J('"$w".split("").filter(c => !"aeiou".includes(c)).join("")', lambda p: "".join(ch for ch in p["w"] if ch not in VOW), "Drop the vowels."),
    J('"$w".split("").reverse().join("") + "$w"', lambda p: reverse_text(p["w"]) + p["w"], "The reversed word, then the word."),
    J('[..."$w"].sort().at(-1)', lambda p: sorted_chars(p["w"])[-1], "Sorted letters: the last is the latest in the alphabet."),
    J('"$w" < "$v" ? "$w" : "$v"', lambda p: p["w"] if lex_less(p["w"], p["v"]) else p["v"], "The one that comes first in the dictionary."),
    J('"$ph".replaceAll(" ", "").length', lambda p: len(p["w"]) + len(p["v"]), "Without the space, just the two words."),
    J('"$w".repeat(2) + "$v"', lambda p: p["w"] * 2 + p["v"], "Two copies, then the other word."),
    J('"$a".repeat($b)', lambda p: str(p["a"]) * p["b"], "The text, repeated b times."),
    J('("$w" + "$v")[$k]', lambda p: (p["w"] + p["v"])[p["k"]], "Join first, then pick the letter at that position."),
    J('"$w"[0].repeat($a)', lambda p: p["w"][0] * p["a"], "The first letter, repeated."),
    J('[..."$an"].filter(c => c >= "0" && c <= "9").join("")', lambda p: "".join(ch for ch in p["an"] if is_digit(ch)), "Keep the characters between 0 and 9."),
    J('"$w".length - "$w".replaceAll("$c", "").length', lambda p: count_sub(p["w"], p["c"]), "The characters lost are the matches."),
    J('"$mix".split("").filter(c => c === c.toUpperCase()).length', lambda p: sum(1 for ch in p["mix"] if "A" <= ch <= "Z"), "A letter equal to its capital version is a capital."),
    J('String(2 ** $n).length', lambda p: len(str(ipow(2, p["n"]))), "Work out the power, then count its digits."),
    J('"$num".split("").reduce((s, d) => s + Number(d), 0)', lambda p: sum(int(d) for d in p["num"]), "The digits of the number, added up."),
]

# ── 7. Char Codes ───────────────────────────────────────────────────────

LETTERS = "The letters are in order, so a small letter's code is 97 plus its position from 0, and a capital's is 65 plus it."
CODE = "charCodeAt gives a character's number and String.fromCharCode turns a number back into a character."


def _shift(letter: str, base: int, by: int) -> str:
    return chr_of((ord_of(letter) - base + by + 26 * 30) % 26 + base)


CODES: list[Maker] = [
    J('"$L".charCodeAt(0)', lambda p: ord_of(p["L"]), CODE),
    J('"$LU".charCodeAt(0)', lambda p: ord_of(p["LU"]), "Capitals have codes from 65 (A) to 90 (Z)."),
    J('String.fromCharCode($code)', lambda p: p["L"], CODE),
    J('String.fromCharCode(97 + $a)', lambda p: chr_of(97 + p["a"]), LETTERS),
    J('String.fromCharCode(65 + $a)', lambda p: chr_of(65 + p["a"]), LETTERS),
    J('"a".charCodeAt(0)', "97", "A small a has code 97."),
    J('"A".charCodeAt(0)', "65", "A capital A has code 65."),
    J('"0".charCodeAt(0)', "48", "The digit characters start at 48."),
    J('" ".charCodeAt(0)', "32", "A space is character 32."),
    J('"$LU".charCodeAt(0) - "$L".charCodeAt(0)', "-32", "A small letter's code is 32 above its capital's."),
    J('"$L".charCodeAt(0) - "a".charCodeAt(0)', lambda p: ord_of(p["L"]) - 97, "The position in the alphabet, counting a as 0."),
    J('"$dg".charCodeAt(0) - "0".charCodeAt(0)', lambda p: int(p["dg"]), "The digit characters are in order, so this is the digit's value."),
    J('String.fromCharCode("0".charCodeAt(0) + $a)', lambda p: str(p["a"]), "48 plus a is the digit character for a."),
    J('String.fromCharCode("$L".charCodeAt(0) + 1)', lambda p: chr_of(ord_of(p["L"]) + 1), "The next character in the code table."),
    J('String.fromCharCode("$L".charCodeAt(0) - 32)', lambda p: p["LU"], "A small letter minus 32 is its capital."),
    J('String.fromCharCode("$LU".charCodeAt(0) + 32)', lambda p: p["L"], "A capital plus 32 is its small letter."),
    J('String.fromCharCode(("$L".charCodeAt(0) - 97 + $k) % 26 + 97)', lambda p: _shift(p["L"], 97, p["k"]), "A Caesar shift: move k along the alphabet, wrapping round after z."),
    J('String.fromCharCode(("z".charCodeAt(0) - 97 + $k) % 26 + 97)', lambda p: _shift("z", 97, p["k"]), "z shifted forward wraps round to the start of the alphabet."),
    J('String.fromCharCode(("$L".charCodeAt(0) - 97 - $k + 26) % 26 + 97)', lambda p: _shift(p["L"], 97, -p["k"]), "Shifting back: adding 26 first keeps the % from going negative."),
    J('("$L".charCodeAt(0) - 97 - 30) % 26', lambda p: tmod(ord_of(p["L"]) - 97 - 30, 26), "JavaScript's % keeps the sign of the left side, so the answer is negative."),
    J('"$w".charCodeAt(9)', "NaN", "Past the end, charCodeAt gives NaN."),
    J('"$w".codePointAt(0)', lambda p: ord_of(p["w"][0]), "For plain letters, codePointAt is the same number as charCodeAt."),
    J('"$w".split("").map(c => String.fromCharCode(c.charCodeAt(0) + 1)).join("")', lambda p: "".join(chr_of(ord_of(ch) + 1) for ch in p["w"]), "Every letter moves one along: a becomes b."),
    J('"$sub".split("").map(c => c.charCodeAt(0))', lambda p: [ord_of(ch) for ch in p["sub"]], "An array with each letter's code."),
    J('"$w".charCodeAt($k)', lambda p: ord_of(p["w"][p["k"]]), "The code of the letter at that position."),
    J('"$w"[0].charCodeAt(0)', lambda p: ord_of(p["w"][0]), "The code of the first letter."),
    J('"$w".at(-1).charCodeAt(0)', lambda p: ord_of(p["w"][-1]), "The code of the last letter."),
    J('String.fromCharCode(72, 105)', "Hi", "Several numbers make several characters."),
    J('String.fromCharCode($a + 64, $b + 64)', lambda p: chr_of(p["a"] + 64) + chr_of(p["b"] + 64), "64 plus the position: A is 65."),
    J('"z".charCodeAt(0) + 1', "123", "z is 122."),
    J('String.fromCharCode("z".charCodeAt(0) + 1)', "{", "The code table goes on after z: next comes {."),
    J('String.fromCharCode("Z".charCodeAt(0) + 1)', "[", "After Z comes [."),
    J('"$x".charCodeAt(0) + "$y".charCodeAt(0)', lambda p: ord_of(p["x"]) + ord_of(p["y"]), "Two numbers added."),
    J('"$L".charCodeAt(0).toString(16)', lambda p: digits_in(ord_of(p["L"]), 16), "The code in hexadecimal."),
    J('"$y".charCodeAt() - "$x".charCodeAt()', lambda p: ord_of(p["y"]) - ord_of(p["x"]), "With no argument, charCodeAt reads position 0."),
    J('"$w".split("").reduce((s, c) => s + c.charCodeAt(0), 0)', lambda p: sum(ord_of(ch) for ch in p["w"]), "Add up the code of each letter."),
    J('"a".charCodeAt(0) === 97', "true", "A small a is 97."),
    J('"$x".charCodeAt(0) < "$y".charCodeAt(0)', lambda p: ord_of(p["x"]) < ord_of(p["y"]), "Earlier letters have smaller codes."),
]

# ── 8. Text Check ───────────────────────────────────────────────────────


def _pal(rng: random.Random) -> Item:
    word = rng.choice(PALINDROMES + tuple(rng.sample(WORDS, 3)))
    code = f'"{word}".split("").reverse().join("") === "{word}"'
    return Item(code, "yes" if word == reverse_text(word) else "no",
                "A palindrome reads the same backwards: compare it with its reverse.", check=yes_no_js(code))


def _anagram(rng: random.Random) -> Item:
    a, b = rng.choice(PAIRS)
    if rng.random() < 0.5:
        a, b = b, a
    code = f'[..."{a}"].sort().join("") === [..."{b}"].sort().join("")'
    return Item(code, "yes" if sorted_chars(a) == sorted_chars(b) else "no",
                "Anagrams have the same letters: sort both and compare.", check=yes_no_js(code))


CHECK: list[Maker] = [
    JQ('"$w" < "$v"', lambda p: lex_less(p["w"], p["v"]), "Strings compare letter by letter, like a dictionary."),
    JQ('"$w" > "$v"', lambda p: lex_less(p["v"], p["w"]), "The one later in the dictionary is greater."),
    JQ('"10" < "9"', True, "As text, '1' comes before '9', so '10' is smaller."),
    JQ('"10" < 9', False, "With a number, the text becomes a number: 10 < 9 is false."),
    JQ('"abc" < 5', False, "'abc' becomes NaN, and NaN is never smaller than anything."),
    JQ('"abc" > 5', False, "NaN is never greater either: both comparisons are false."),
    JQ('"$n" < "$a"', lambda p: lex_less(str(p["n"]), str(p["a"])), "Text compares first digit first, not by size."),
    JQ('"Z" < "a"', True, "Capitals come before small letters in the code table."),
    JQ('"a" < "B"', False, "A small a comes after every capital."),
    JQ('"B" < "a"', True, "A capital comes before a small letter."),
    JQ('"$W" < "$w"', True, "The capital is the earlier character, so Farm sorts first."),
    JQ('"apple" < "apples"', True, "A prefix is smaller than the longer text."),
    JQ('"" < "a"', True, "The empty string is smaller than any text."),
    JQ('"b" > "abc"', True, "The first letters decide: b is after a."),
    JQ('"apple" < "Banana"', False, "A capital B is before a small a, so Banana is first."),
    JQ('"Zebra" < "apple"', True, "Capitals come before small letters."),
    JQ('"a" < "b" && "b" < "c"', True, "Both comparisons hold."),
    JQ('"$w".includes("$c")', True, "That letter is in the word."),
    JQ('"$w".includes("$q")', False, "That letter is not in the word."),
    JQ('"$v".includes("$w")', lambda p: find_in(p["v"], p["w"]) >= 0, "includes asks whether the whole text is somewhere inside."),
    JQ('"$ph".includes(" ")', True, "There is a space."),
    JQ('"$w".startsWith("$z0")', True, "The word begins with its first letter."),
    JQ('"$w".startsWith("$c")', lambda p: p["w"][0] == p["c"], "Only the first letter counts for startsWith."),
    JQ('"$w".endsWith("$z1")', True, "The word ends with its last letter."),
    JQ('"$w".endsWith("$c")', lambda p: p["w"][-1] == p["c"], "Only the last letter counts for endsWith."),
    JQ('"$w".startsWith("$c", 1)', lambda p: p["w"][1:2] == p["c"], "The second argument is where to start checking: position 1."),
    JQ('"$W".startsWith("$z0")', False, "A capital F is not a small f: case matters."),
    JQ('"$ph".endsWith("$v")', True, "The text ends with its second word."),
    JQ('"$ph".startsWith("$v")', lambda p: p["ph"][:len(p["v"])] == p["v"], "Only the beginning of the text counts: the first word is there, not the second."),
    JQ('"$w" === "$w".toLowerCase()', lambda p: p["w"] == lower(p["w"]), "The word is already in small letters."),
    JQ('"$W".toLowerCase() === "$w"', True, "toLowerCase() gives back the small word."),
    JQ('"$w".toUpperCase() === "$w"', False, "Capitals are different characters."),
    JQ('"$w" + "$v" === "$v" + "$w"', lambda p: p["w"] + p["v"] == p["v"] + p["w"], "Joining in a different order gives a different text."),
    JQ('"$a" == $a', True, "== converts the text to a number first."),
    JQ('"$a" === $a', False, "=== also compares types: text is not a number."),
    JQ('"a" == "A"', False, "Capital and small are different characters."),
    JQ('"$w".length > "$v".length', lambda p: len(p["w"]) > len(p["v"]), "Compare the lengths."),
    JQ('"$w".at(-1) === "$z1"', True, "at(-1) is the last letter."),
    JQ('"$w".indexOf("$c") !== -1', True, "The letter is found."),
    JQ('"$w".indexOf("$q") !== -1', False, "The letter is not found."),
    JQ('"$num".split("").every(c => c >= "0" && c <= "9")', True, "Every character is between 0 and 9."),
    JQ('"$an".split("").every(c => c >= "0" && c <= "9")', False, "There are letters in it."),
    JQ('"$an".split("").some(c => c >= "0" && c <= "9")', True, "At least one digit."),
    JQ('"$w".split("").every(c => c >= "a" && c <= "z")', True, "Every letter is small."),
    JQ('"$mix".split("").every(c => c >= "a" && c <= "z")', False, "Some letters are capitals."),
    JQ('!isNaN("$a")', True, "The text reads as a number."),
    JQ('!isNaN("$w")', False, "A word does not read as a number: NaN."),
    JQ('Number.isNaN(Number("$w"))', True, "Number() of a word is NaN."),
    JQ('"$w".split("").every(c => "aeiou".includes(c))', lambda p: all(ch in VOW for ch in p["w"]), "Is every letter a vowel?"),
    JQ('"$w".split("").some(c => "aeiou".includes(c))', True, "Every word here has a vowel."),
    JQ('"abc" == "abc "', False, "The space makes it a different string."),
    JQ('"$w".trim() === "$w"', True, "There was nothing to trim."),
    JQ('" $w".trim() === "$w"', True, "trim removes the leading space."),
    JQ('new Set("$w").size === "$w".length', lambda p: _distinct(p["w"]), "A Set drops repeats: the same size means no letter repeats."),
    JQ('"$w"[0] === "$w".at(-1)', lambda p: p["w"][0] == p["w"][-1], "Compare the first and last letters."),
    JQ('"$w".split("$c").length > 2', lambda p: count_sub(p["w"], p["c"]) > 1, "More than two pieces means the letter appears more than once."),
    _pal,
    _anagram,
]
