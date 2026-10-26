"""SQL deeper queries, part 6: Pattern Match.

LIKE (`%`, `_`, ESCAPE, ASCII case ignored), GLOB (`*`, `?`, `[a-c]`, `[^a-c]`, case-sensitive), and how text compares for BETWEEN,
IN, `<`, MIN / MAX and ORDER BY (binary: every capital letter sorts before every lower-case one; COLLATE NOCASE changes that).
Models are `like`, `like_esc` and `glob`; text order is Python's own (the same for ASCII).
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker
from ._sql_model import NULL, Retry, Tbl, fit, like, not_in, sql_item, t_not
from ._sqlquery_model import glob, like_esc

PAT: list[Maker] = []


def reg(f: Callable) -> Callable:
    PAT.append(fit(f))
    return f


MIXED = ["Apple", "apple", "banana", "Cherry", "date", "Kiwi", "lemon", "Mango", "melon", "peach", "Pear", "plum", "grape", "lime", "fig", "berry"]
DIGITS = ["a1", "b22", "cc", "d4e", "77", "x9", "kiwi", "5th", "ab", "q"]
SPECIAL = ["50%", "a_b", "ab", "a%b", "100%", "x_y", "axb", "5%0", "a*b", "a?b"]


def _words(rng: random.Random, n: int = 6, pool: list | None = None, nulls: int = 0) -> Tbl:
    w = rng.sample(pool or MIXED, n)
    if nulls:
        for k in rng.sample(range(n), nulls):
            w[k] = None
    return Tbl("t", [("w", "TEXT")], [(x,) for x in w])


def W(t: Tbl) -> list:
    return t.col("w")


def cnt(t: Tbl, pred: Callable) -> int:
    return sum(1 for w in W(t) if pred(w) is True)


# ── LIKE ────────────────────────────────────────────────────────────────

@reg
def like_prefix(rng):
    t = _words(rng, 7)
    c = rng.choice("abcdklmp")
    n = cnt(t, lambda w: like(w, c + "%"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '{c}%';", n, "% stands for any run of characters; LIKE ignores the case of ASCII letters, so Apple and apple both match.")


@reg
def like_upper_prefix(rng):
    t = _words(rng, 7)
    c = rng.choice("ACKMP").upper()
    n = cnt(t, lambda w: like(w, c + "%"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '{c}%';", n, "Even with a capital letter in the pattern, LIKE ignores case: lower-case words count too.")


@reg
def like_suffix(rng):
    t = _words(rng, 7)
    c = rng.choice("enra")
    n = cnt(t, lambda w: like(w, "%" + c))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '%{c}';", n, "The text must END with that letter.")


@reg
def like_contains(rng):
    t = _words(rng, 7)
    c = rng.choice(["an", "e", "pe", "me", "a"])
    n = cnt(t, lambda w: like(w, f"%{c}%"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '%{c}%';", n, "% on both sides: the text only has to contain it somewhere.")


@reg
def like_underscore_second(rng):
    t = _words(rng, 7)
    c = rng.choice("aeio")
    n = cnt(t, lambda w: like(w, f"_{c}%"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '_{c}%';", n, "_ is exactly one character, so this means: any first letter, then that letter second.")


@reg
def like_exact_length(rng):
    t = _words(rng, 7)
    k = rng.randint(3, 5)
    n = cnt(t, lambda w: like(w, "_" * k))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '{'_' * k}';", n, "k underscores match exactly k characters.")


@reg
def like_at_least(rng):
    t = _words(rng, 7)
    k = rng.randint(4, 5)
    n = cnt(t, lambda w: like(w, "_" * k + "%"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '{'_' * k}%';", n, "k underscores then %: at least k characters.")


@reg
def like_start_end(rng):
    t = _words(rng, 7)
    a, b = rng.choice("abclmp"), rng.choice("enra")
    n = cnt(t, lambda w: like(w, f"{a}%{b}"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '{a}%{b}';", n, "Starts with the first letter and ends with the second (the % can be empty).")


@reg
def like_not(rng):
    t = _words(rng, 6, nulls=1)
    c = rng.choice("aelm")
    n = cnt(t, lambda w: t_not(like(w, c + "%")))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w NOT LIKE '{c}%';", n, "NOT LIKE is also unknown for the NULL row, so that row is left out.")


@reg
def like_all(rng):
    t = _words(rng, 6, nulls=1)
    n = cnt(t, lambda w: like(w, "%"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE '%';", n, "% matches any text at all, but NULL LIKE anything is unknown.")


@reg
def like_empty_string(rng):
    t = Tbl("t", [("w", "TEXT")], [(w,) for w in rng.sample(MIXED, 3)] + [("",), ("",)])
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE '_%';", 3, "_% needs at least one character, so the two empty strings do not match.")


@reg
def like_first_sorted(rng):
    t = _words(rng, 7)
    c = rng.choice(["e", "a", "m"])
    ws = sorted(w for w in W(t) if like(w, f"%{c}%"))
    if not ws:
        raise Retry
    return sql_item([t], f"SELECT w FROM t WHERE w LIKE '%{c}%' ORDER BY w LIMIT 1;", ws[0], "Filter first, then sort by plain character codes: a capital letter sorts before every lower-case one.")


@reg
def like_concat_pattern(rng):
    t = _words(rng, 7)
    c = rng.choice("elmp")
    n = cnt(t, lambda w: like(w, f"{c}%"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w LIKE '{c}' || '%';", n, "The pattern can be built with ||: here it is the same as 'c%'.")


@reg
def like_lower_same(rng):
    t = _words(rng, 7)
    c = rng.choice("abcdklmp")
    n = cnt(t, lambda w: like(w.lower() if w else w, c + "%"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE LOWER(w) LIKE '{c}%';", n, "LOWER first changes nothing here: LIKE already ignores the case.")


@reg
def like_vs_equal(rng):
    t = Tbl("t", [("w", "TEXT")], [(w,) for w in ["fig", "FIG", "Fig", "fog", "figs"]])
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE 'fig';", 3, "With no % or _ the pattern must match the whole text, ignoring case: fig, FIG and Fig.")


@reg
def like_equal_exact(rng):
    t = Tbl("t", [("w", "TEXT")], [(w,) for w in ["fig", "FIG", "Fig", "fog", "figs"]])
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w = 'fig';", 1, "= compares exactly, so only the lower-case fig matches.")


@reg
def like_equal_nocase(rng):
    t = Tbl("t", [("w", "TEXT")], [(w,) for w in ["fig", "FIG", "Fig", "fog", "figs"]])
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w = 'fig' COLLATE NOCASE;", 3, "COLLATE NOCASE makes = ignore the case of ASCII letters.")


# ── LIKE with ESCAPE and special characters ─────────────────────────────

@reg
def escape_percent_end(rng):
    t = _words(rng, 6, SPECIAL)
    n = cnt(t, lambda w: like_esc(w, "%!%", "!"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE '%!%' ESCAPE '!';", n, "!% means a real percent sign, so the pattern is: anything, then a % at the end.")


@reg
def escape_underscore(rng):
    t = _words(rng, 6, SPECIAL)
    n = cnt(t, lambda w: like_esc(w, "a!_b", "!"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE 'a!_b' ESCAPE '!';", n, "!_ is a real underscore: only the text a_b matches.")


@reg
def no_escape_underscore(rng):
    t = _words(rng, 6, SPECIAL)
    n = cnt(t, lambda w: like_esc(w, "a_b", "!"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE 'a_b';", n, "Without ESCAPE the underscore is a wildcard: a_b, axb, a%b and a*b all match.")


@reg
def escape_percent_start(rng):
    t = _words(rng, 6, SPECIAL)
    n = cnt(t, lambda w: like_esc(w, "5!%%", "!"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE '5!%%' ESCAPE '!';", n, "A real 5% at the start, then % for anything.")


@reg
def percent_literal_wild(rng):
    t = _words(rng, 6, SPECIAL)
    n = cnt(t, lambda w: like_esc(w, "5%", "!"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE '5%';", n, "Unescaped, % is a wildcard: anything that starts with 5.")


@reg
def contains_percent(rng):
    t = _words(rng, 7, SPECIAL)
    n = cnt(t, lambda w: like_esc(w, "%!%%", "!"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w LIKE '%!%%' ESCAPE '!';", n, "Anything, a real %, anything: texts that contain a percent sign.")


@reg
def const_escape_hit(rng):
    return sql_item([], "SELECT 'a%b' LIKE 'a!%b' ESCAPE '!';", 1, "The escaped % is a plain percent sign, and a%b has one.")


@reg
def const_escape_miss(rng):
    return sql_item([], "SELECT 'axb' LIKE 'a!%b' ESCAPE '!';", 0, "The escaped % must be a real percent sign, and axb has none.")


@reg
def const_unescaped(rng):
    return sql_item([], "SELECT 'axxb' LIKE 'a%b';", 1, "Unescaped, % matches any run of characters.")


# ── GLOB ────────────────────────────────────────────────────────────────

@reg
def glob_prefix(rng):
    t = _words(rng, 7)
    c = rng.choice("aKCMPb")
    n = cnt(t, lambda w: glob(w, c + "*"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w GLOB '{c}*';", n, "GLOB's * is like %, but GLOB is case-sensitive: only words that begin with exactly that letter.")


@reg
def glob_upper_start(rng):
    t = _words(rng, 7)
    n = cnt(t, lambda w: glob(w, "[A-Z]*"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB '[A-Z]*';", n, "[A-Z] is any capital letter: the words that start with one.")


@reg
def glob_lower_range(rng):
    t = _words(rng, 7)
    n = cnt(t, lambda w: glob(w, "[a-f]*"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB '[a-f]*';", n, "A set with a range: the first letter is one of a to f, lower case only.")


@reg
def glob_set(rng):
    t = _words(rng, 7)
    n = cnt(t, lambda w: glob(w, "[aeiou]*"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB '[aeiou]*';", n, "A set lists the allowed characters: words that start with a lower-case vowel.")


@reg
def glob_not_set(rng):
    t = _words(rng, 7)
    n = cnt(t, lambda w: glob(w, "[^a-m]*"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB '[^a-m]*';", n, "[^...] is any character NOT in the set; capital letters are not in a-m, so they count too.")


@reg
def glob_suffix(rng):
    t = _words(rng, 7)
    c = rng.choice("enrmo")
    n = cnt(t, lambda w: glob(w, "*" + c))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w GLOB '*{c}';", n, "Anything, then that letter at the end.")


@reg
def glob_question(rng):
    t = _words(rng, 7)
    c = rng.choice("aeio")
    n = cnt(t, lambda w: glob(w, f"?{c}*"))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w GLOB '?{c}*';", n, "? is exactly one character (GLOB's version of _).")


@reg
def glob_length(rng):
    t = _words(rng, 7)
    k = rng.randint(3, 5)
    n = cnt(t, lambda w: glob(w, "?" * k))
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w GLOB '{'?' * k}';", n, "k question marks match exactly k characters.")


@reg
def glob_contains_digit(rng):
    t = _words(rng, 7, DIGITS)
    n = cnt(t, lambda w: glob(w, "*[0-9]*"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB '*[0-9]*';", n, "A digit anywhere in the text.")


@reg
def glob_ends_digit(rng):
    t = _words(rng, 7, DIGITS)
    n = cnt(t, lambda w: glob(w, "*[0-9]"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB '*[0-9]';", n, "The last character is a digit.")


@reg
def glob_all_digits(rng):
    t = _words(rng, 7, DIGITS)
    n = cnt(t, lambda w: glob(w, "[0-9][0-9]"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB '[0-9][0-9]';", n, "Exactly two characters, both digits.")


@reg
def glob_no_digit(rng):
    t = _words(rng, 7, DIGITS)
    n = cnt(t, lambda w: t_not(glob(w, "*[0-9]*")))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w NOT GLOB '*[0-9]*';", n, "Texts with no digit at all.")


@reg
def glob_literal_star(rng):
    t = _words(rng, 6, SPECIAL)
    n = cnt(t, lambda w: glob(w, "a[*]b"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB 'a[*]b';", n, "Putting * in brackets makes it a plain star: only the text a*b matches.")


@reg
def glob_literal_question(rng):
    t = _words(rng, 7, SPECIAL)
    n = cnt(t, lambda w: glob(w, "a[?]b"))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w GLOB 'a[?]b';", n, "[?] is a plain question mark: only a?b matches.")


@reg
def like_minus_glob(rng):
    t = _words(rng, 7)
    c = rng.choice("aCKMPb")
    n = cnt(t, lambda w: like(w, c + "%")) - cnt(t, lambda w: glob(w, c + "*"))
    return sql_item([t], f"SELECT (SELECT COUNT(*) FROM t WHERE w LIKE '{c}%') - (SELECT COUNT(*) FROM t WHERE w GLOB '{c}*');", n, "The words LIKE accepts only because it ignores case.")


@reg
def const_glob_case(rng):
    w = rng.choice(["Hello", "World", "Maple"])
    return sql_item([], f"SELECT '{w}' GLOB '{w[0].lower()}*';", 0, "GLOB is case-sensitive, so a capital letter does not match the lower-case one.")


@reg
def const_like_case(rng):
    w = rng.choice(["Hello", "World", "Maple"])
    return sql_item([], f"SELECT '{w}' LIKE '{w[0].lower()}%';", 1, "LIKE ignores the case of ASCII letters.")


@reg
def const_like_null(rng):
    return sql_item([], "SELECT NULL LIKE '%';", NULL, "NULL LIKE anything is unknown, which prints as NULL.")


@reg
def const_empty_like(rng):
    return sql_item([], "SELECT '' LIKE '%';", 1, "% can match nothing at all, so even the empty text matches.")


@reg
def const_empty_underscore(rng):
    return sql_item([], "SELECT '' LIKE '_';", 0, "_ needs one character; the empty text has none.")


@reg
def const_concat_like(rng):
    a, b = rng.sample("abcdef", 2)
    return sql_item([], f"SELECT '{a}' || '{b}' LIKE '{a.upper()}{b.upper()}';", 1, "|| binds tighter than LIKE: the text ab is compared with AB, ignoring case.")


# ── Text order: BETWEEN, IN, <, MIN, MAX, ORDER BY ──────────────────────

@reg
def between_text(rng):
    t = _words(rng, 7, [w for w in MIXED if w[0].islower()])
    lo, hi = sorted(rng.sample("bcdfglmp", 2))
    n = sum(1 for w in W(t) if lo <= w <= hi)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w BETWEEN '{lo}' AND '{hi}';", n, "Text compares letter by letter, and a longer word is bigger than its start: 'date' is above 'd', so it is outside the range ending at 'd'.")


@reg
def between_upper(rng):
    t = _words(rng, 7)
    lo, hi = sorted(rng.sample("ACKMPB", 2))
    n = sum(1 for w in W(t) if lo <= w <= hi)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w BETWEEN '{lo}' AND '{hi}';", n, "BETWEEN compares by character codes: only capitalised words fall between two capital letters.")


@reg
def in_exact_case(rng):
    t = _words(rng, 7)
    picks = rng.sample(["Apple", "apple", "kiwi", "Kiwi", "plum", "Pear"], 3)
    n = sum(1 for w in W(t) if w in picks)
    lst = ",".join(f"'{p}'" for p in picks)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w IN ({lst});", n, "IN compares exactly, case included: Kiwi and kiwi are different texts.")


@reg
def not_in_with_null_row(rng):
    t = _words(rng, 6, nulls=1)
    picks = rng.sample(["Apple", "apple", "fig", "Kiwi", "plum", "Pear", "date", "lime"], 3)
    lst = ",".join(f"'{p}'" for p in picks)
    n = sum(1 for w in W(t) if not_in(w, picks) is True)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w NOT IN ({lst});", n, "The NULL row is unknown for NOT IN too, so it is not counted.")


@reg
def greater_than_letter(rng):
    t = _words(rng, 7)
    c = rng.choice("fklm")
    n = sum(1 for w in W(t) if w >= c)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE w >= '{c}';", n, "Every capital letter has a smaller code than every lower-case letter, so capitalised words are never >= a lower-case letter.")


@reg
def below_a(rng):
    t = _words(rng, 7)
    n = sum(1 for w in W(t) if w < "a")
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE w < 'a';", n, "All capitals sort below 'a': this counts the capitalised words.")


@reg
def min_text(rng):
    t = _words(rng, 7)
    return sql_item([t], "SELECT MIN(w) FROM t;", min(W(t)), "MIN of text uses character codes, so a capitalised word beats every lower-case one.")


@reg
def max_text(rng):
    t = _words(rng, 7)
    return sql_item([t], "SELECT MAX(w) FROM t;", max(W(t)), "MAX is the last in code order; capitals come before lower case, so it is a lower-case word if there is one.")


@reg
def order_nocase(rng):
    t = _words(rng, 7)
    k = rng.randint(0, 2)
    ws = sorted(W(t), key=lambda w: w.lower())
    if len({w.lower() for w in W(t)}) != 7:
        raise Retry
    return sql_item([t], f"SELECT w FROM t ORDER BY w COLLATE NOCASE LIMIT 1 OFFSET {k};", ws[k], "NOCASE sorts ignoring ASCII case, so Apple and apple sit together instead of capitals first.")


@reg
def order_binary(rng):
    t = _words(rng, 7)
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT w FROM t ORDER BY w LIMIT 1 OFFSET {k};", sorted(W(t))[k], "The default order is by character code: capitalised words come first.")


@reg
def length_between(rng):
    t = _words(rng, 7)
    lo = rng.randint(3, 4)
    n = sum(1 for w in W(t) if lo <= len(w) <= lo + 1)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE LENGTH(w) BETWEEN {lo} AND {lo + 1};", n, "BETWEEN on numbers is inclusive at both ends.")


@reg
def first_letter_vowel(rng):
    t = _words(rng, 7)
    n = sum(1 for w in W(t) if w[0] in "aeiou")
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE SUBSTR(w, 1, 1) IN ('a','e','i','o','u');", n, "IN is case-sensitive, so a capital A is not in the list.")


@reg
def instr_case(rng):
    t = _words(rng, 7)
    c = rng.choice("aeKP")
    n = sum(1 for w in W(t) if c in w)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE INSTR(w, '{c}') > 0;", n, "INSTR is case-sensitive, unlike LIKE: it only finds that exact letter.")


@reg
def const_text_vs_number(rng):
    a, b = rng.choice([(9, 10), (2, 15), (7, 30)])
    return sql_item([], f"SELECT '{a}' < '{b}';", int(str(a) < str(b)), "Quoted values are text, compared character by character, not as numbers.")


@reg
def const_number_vs_text(rng):
    a = rng.randint(2, 9)
    return sql_item([], f"SELECT {a} < '{a + 1}';", 1, "A number is always smaller than any text when no column converts the text.")
