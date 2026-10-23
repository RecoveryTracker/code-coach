"""Dart data pack, part 8: RegExp & Buffer - regular expressions, StringBuffer and string interpolation.

RegExp `hasMatch`, `firstMatch`, `allMatches`, `replaceAll`, `replaceAllMapped`, `split`, groups, greedy and lazy;
`StringBuffer` `write`/`writeAll`/`writeln`/`writeCharCode`; and `'$a'`, `'${a + b}'` interpolation with its traps.
The patterns are plain ones (digits, letters, groups, alternation, anchors, lazy `+?`) whose meaning is the same in
Dart and in Python, so the matches are worked out with Python's `re` module; the Dart runtime is only asked by the
oracle test. Test strings never contain a newline (where `$` would differ).
"""

from __future__ import annotations

import random
import re

from ._dart_model import fixed
from ._dartdata_model import R, ints, words
from ._model import Maker


def _mixed(r: random.Random, runs: int = 2) -> str:
    """A string like farm12key345: words and digit runs, starting with a word."""
    parts = []
    for _ in range(runs):
        parts.append(words(r, 1)[0])
        parts.append(str(r.choice((r.randint(2, 9), r.randint(10, 99), r.randint(100, 999)))))
    return "".join(parts)


def _pr(*lines: str) -> str:
    return "\n".join(lines)


# ── RegExp ──────────────────────────────────────────────────────────────

def x_hasmatch_yes(r):
    s = _mixed(r, 1)
    return rf"print(RegExp(r'\d').hasMatch('{s}'));", True, "hasMatch is true when the pattern matches anywhere in the text."


def x_hasmatch_no(r):
    w = words(r, 1)[0]
    return rf"print(RegExp(r'\d').hasMatch('{w}'));", False, "The word has no digit anywhere."


def x_whole(r):
    a = r.randint(10, 999)
    s = r.choice((str(a), f"{a}x", f"x{a}"))
    return rf"print(RegExp(r'^\d+$').hasMatch('{s}'));", s.isdigit(), "The start and end anchors force the whole text to be digits."


def x_partial(r):
    a = r.randint(10, 999)
    return rf"print(RegExp(r'\d+').hasMatch('x{a}x'));", True, "Without the start and end anchors a match anywhere is enough."


def x_first(r):
    s = _mixed(r)
    return rf"print(RegExp(r'\d+').firstMatch('{s}')!.group(0));", re.search(r"\d+", s).group(0), "firstMatch finds the leftmost run of digits; group(0) is the whole match."


def x_first_null(r):
    w = words(r, 1)[0]
    return rf"print(RegExp(r'\d').firstMatch('{w}'));", None, "No match: firstMatch gives null."


def x_first_null_group(r):
    w = words(r, 1)[0]
    return rf"print(RegExp(r'\d').firstMatch('{w}')?.group(0));", None, "?. stops at the null match, so the whole thing is null."


def x_string_match(r):
    s = _mixed(r)
    return rf"print(RegExp(r'[a-z]+').stringMatch('{s}'));", re.search(r"[a-z]+", s).group(0), "stringMatch is the text of the first match."


def x_count(r):
    s = _mixed(r, 3)
    return rf"print(RegExp(r'\d+').allMatches('{s}').length);", len(re.findall(r"\d+", s)), "Each run of digits is one match."


def x_count_each(r):
    s = _mixed(r, 2)
    return rf"print(RegExp(r'\d').allMatches('{s}').length);", len(re.findall(r"\d", s)), "\\d matches ONE digit, so every digit counts."


def x_all_list(r):
    s = _mixed(r, 3)
    return (rf"print(RegExp(r'\d+').allMatches('{s}').map((m) => m[0]).toList());", re.findall(r"\d+", s),
            "m[0] is the text of each match; the numbers print without quotes.")


def x_all_sum(r):
    s = _mixed(r, 3)
    return (rf"print(RegExp(r'\d+').allMatches('{s}').map((m) => int.parse(m[0]!)).reduce((a, b) => a + b));", sum(map(int, re.findall(r"\d+", s))),
            "Turn each digit run into a number and add them.")


def x_all_start(r):
    s = _mixed(r, 2)
    return (rf"print(RegExp(r'\d+').allMatches('{s}').map((m) => m.start).toList());", [m.start() for m in re.finditer(r"\d+", s)],
            "start is the position where each match begins.")


def x_start(r):
    s = _mixed(r, 1)
    return rf"print(RegExp(r'\d+').firstMatch('{s}')!.start);", re.search(r"\d+", s).start(), "The digits begin right after the word."


def x_end(r):
    s = _mixed(r, 1)
    return rf"print(RegExp(r'\d+').firstMatch('{s}')!.end);", re.search(r"\d+", s).end(), "end is the position just after the match: here the end of the text."


def x_replace_each(r):
    s = _mixed(r, 2)
    return rf"print('{s}'.replaceAll(RegExp(r'\d'), '#'));", re.sub(r"\d", "#", s), "Every digit becomes one #."


def x_replace_run(r):
    s = _mixed(r, 2)
    return rf"print('{s}'.replaceAll(RegExp(r'\d+'), '#'));", re.sub(r"\d+", "#", s), "Every run of digits becomes a single #."


def x_replace_first(r):
    s = _mixed(r, 2)
    return rf"print('{s}'.replaceFirst(RegExp(r'\d+'), '#'));", re.sub(r"\d+", "#", s, count=1), "Only the first run of digits is replaced."


def x_replace_letters(r):
    s = _mixed(r, 2)
    return rf"print('{s}'.replaceAll(RegExp(r'[a-z]'), ''));", re.sub(r"[a-z]", "", s), "Deleting the letters leaves only the digits."


def x_mapped(r):
    s = _mixed(r, 2)
    return (_pr(rf"print('{s}'.replaceAllMapped(RegExp(r'\d+'), (m) => '<${{m[0]}}>'));"), re.sub(r"\d+", lambda m: f"<{m.group(0)}>", s),
            "replaceAllMapped calls the function for each match and uses the text it returns.")


def x_mapped_double(r):
    s = _mixed(r, 2)
    return (rf"print('{s}'.replaceAllMapped(RegExp(r'\d+'), (m) => '${{int.parse(m[0]!) * 2}}'));", re.sub(r"\d+", lambda m: str(int(m.group(0)) * 2), s),
            "Each number is doubled and put back where it was.")


def x_mapped_swap(r):
    w, a = words(r, 1)[0], r.randint(2, 9)
    return (rf"print('{w}{a}'.replaceAllMapped(RegExp(r'([a-z]+)(\d)'), (m) => '${{m[2]}}${{m[1]}}'));", f"{a}{w}",
            "Group 1 is the letters and group 2 the digit; the function puts them in the other order.")


def x_title(r):
    w, v = words(r, 2)
    return (rf"print('{w} {v}'.replaceAllMapped(RegExp(r'\b\w'), (m) => m[0]!.toUpperCase()));", f"{w.capitalize()} {v.capitalize()}",
            r"\b\w is the first letter of each word; each is made a capital.")


def x_group_in_text(r):
    a = r.randint(2, 9)
    return (rf"print('x{a}y'.replaceAllMapped(RegExp(r'(\d)'), (m) => '<${{m[1]}}>'));", f"x<{a}>y",
            "m[1] is what group 1 captured: the digit.")


def x_split_space(r):
    w, v, u = words(r, 3)
    return rf"print('{w}  {v}   {u}'.split(RegExp(r'\s+')));", [w, v, u], r"\s+ treats a whole run of spaces as one separator."


def x_split_plain(r):
    w, v, u = words(r, 3)
    return rf"print('{w}  {v}   {u}'.split(' ').length);", 6, "A plain split on one space cuts at each space and keeps the empty pieces between them."


def x_split_class(r):
    w, v, u = words(r, 3)
    sep = r.choice((",;", ";,"))
    return rf"print('{w}{sep[0]}{v}{sep[1]}{u}'.split(RegExp(r'[,;]')));", [w, v, u], "[,;] matches either a comma or a semicolon."


def x_split_digits(r):
    w, v = words(r, 2)
    a = r.randint(2, 9)
    return rf"print('{w}{a}{v}'.split(RegExp(r'\d')));", [w, v], "The digit is the separator, so the two words are left."


def x_group2(r):
    w, v = words(r, 2)
    return rf"print(RegExp(r'(\w+)@(\w+)').firstMatch('{w}@{v}')!.group(2));", v, "Group 2 is the second pair of brackets: the part after @."


def x_group1(r):
    w, v = words(r, 2)
    return rf"print(RegExp(r'(\w+)@(\w+)').firstMatch('{w}@{v}')!.group(1));", w, "Group 1 is the first pair of brackets."


def x_group_count(r):
    return r"print(RegExp(r'(\w+)@(\w+)\.com').firstMatch('a@b.com')!.groupCount);", 2, "groupCount counts the capturing brackets in the pattern: two."


def x_group_sum(r):
    a, b = r.randint(10, 99), r.randint(10, 99)
    return (rf"var m = RegExp(r'(\d+)-(\d+)').firstMatch('{a}-{b}')!;" + "\n" + r"print(int.parse(m[1]!) + int.parse(m[2]!));", a + b,
            "m[1] and m[2] are the texts around the dash; parse them and add.")


def x_named(r):
    y, m, d = r.randint(2000, 2030), r.randint(10, 12), r.randint(10, 28)
    return (rf"print(RegExp(r'(?<y>\d{{4}})-(?<m>\d{{2}})').firstMatch('on {y}-{m}-{d}')!.namedGroup('m'));", str(m),
            "A named group (?<m>...) is read back with namedGroup('m').")


def x_case(r):
    w = words(r, 1)[0]
    return rf"print(RegExp('{w[:2]}', caseSensitive: false).hasMatch('X{w[:2].upper()}'));", True, "caseSensitive: false ignores capitals."


def x_case_default(r):
    w = words(r, 1)[0]
    return rf"print(RegExp('{w[:2]}').hasMatch('X{w[:2].upper()}'));", False, "A RegExp is case sensitive unless told otherwise."


def x_greedy(r):
    a, b = words(r, 2)
    return rf"print(RegExp(r'<.+>').firstMatch('<{a}><{b}>')!.group(0));", f"<{a}><{b}>", ".+ is greedy: it takes as much as it can, up to the LAST >."


def x_lazy(r):
    a, b = words(r, 2)
    return rf"print(RegExp(r'<.+?>').firstMatch('<{a}><{b}>')!.group(0));", f"<{a}>", ".+? is lazy: it stops at the first >."


def x_alt_count(r):
    ws = [r.choice(("cat", "dog", "bird")) for _ in range(5)]
    s = " ".join(ws)
    return rf"print(RegExp(r'cat|dog').allMatches('{s}').length);", sum(1 for w in ws if w != "bird"), "| means either: count the cat and dog words."


def x_vowel_idx(r):
    w = words(r, 1)[0]
    m = re.search(r"[aeiou]", w)
    return rf"print('{w}'.indexOf(RegExp(r'[aeiou]')));", m.start() if m else -1, "indexOf with a RegExp gives the position of the first match, or -1."


def x_contains(r):
    w = words(r, 1)[0]
    return rf"print('{w}'.contains(RegExp(r'[aeiou]')));", bool(re.search(r"[aeiou]", w)), "contains accepts a RegExp too."


def x_quant(r):
    n = r.randint(1000, 99999)
    return rf"print(RegExp(r'\d{{2}}').allMatches('{n}').map((m) => m[0]).toList());", re.findall(r"\d{2}", str(n)), "{2} means exactly two digits; matches never overlap."


def x_boundary(r):
    return r"print(RegExp(r'\bcat\b').hasMatch('concat'));", False, r"\b needs a word edge on both sides, and concat has none before the cat."


def x_boundary_yes(r):
    w = words(r, 1)[0]
    return rf"print(RegExp(r'\bcat\b').hasMatch('{w} cat'));", True, r"There is a space before and the end after, which are word edges."


def x_backref(r):
    w = r.choice(("book", "farm", "seed", "loop", "wheat", "tree", "code"))
    return rf"print(RegExp(r'(\w)\1').hasMatch('{w}'));", bool(re.search(r"(\w)\1", w)), r"\1 repeats what group 1 matched: it finds a doubled letter."


def x_start_anchor(r):
    w = words(r, 1)[0]
    s = r.choice((w.capitalize(), w))
    return rf"print(RegExp(r'^[A-Z]').hasMatch('{s}'));", s[0].isupper(), "^ anchors at the start: is the first letter a capital?"


def x_escape(r):
    return "print(RegExp.escape('a.b'));", r"a\.b", "escape puts a backslash before characters that mean something in a pattern."


def x_dot_match(r):
    a, b = r.sample("abcdefgh", 2)
    return rf"print(RegExp(r'a.c').hasMatch('a{b}c'));", True, ". matches any one character."


def x_dot_literal(r):
    b = r.choice("xyz")
    return rf"print(RegExp(r'a\.c').hasMatch('a{b}c'));", False, r"\. is a real dot, and the text has a letter there."


def x_trim_ws(r):
    w, v = words(r, 2)
    return rf"print('  {w} {v} '.replaceAll(RegExp(r'\s'), '').length);", len(w) + len(v), "Every space is deleted; only the letters count."


# ── StringBuffer ────────────────────────────────────────────────────────

def b_write2(r):
    w, v = words(r, 2)
    return _pr("var b = StringBuffer();", f"b.write('{w}');", f"b.write('{v}');", "print(b.toString());"), w + v, "write adds text to the end, with nothing between."


def b_write_num(r):
    a, w = r.randint(2, 99), words(r, 1)[0]
    return _pr("var b = StringBuffer();", f"b.write('{w}');", f"b.write({a});", "print(b);"), f"{w}{a}", "write turns a number into text; print(b) shows the text."


def b_length(r):
    w, v = words(r, 2)
    return _pr("var b = StringBuffer();", f"b.write('{w}');", f"b.write('{v}');", "print(b.length);"), len(w) + len(v), "length is the number of characters written so far."


def b_writeall_sep(r):
    w, v, u = words(r, 3)
    return f"var b = StringBuffer();\nb.writeAll(['{w}', '{v}', '{u}'], '-');\nprint(b);", f"{w}-{v}-{u}", "writeAll puts the separator BETWEEN the items, not after the last."


def b_writeall_nosep(r):
    a, b_, c = ints(r, 3, 1, 9)
    return f"var b = StringBuffer();\nb.writeAll([{a}, {b_}, {c}]);\nprint(b);", f"{a}{b_}{c}", "With no separator the items are written one after the other."


def b_writeln_len(r):
    w, v = words(r, 2)
    return f"var b = StringBuffer();\nb.writeln('{w}');\nb.writeln('{v}');\nprint(b.length);", len(w) + len(v) + 2, "writeln adds the text and one newline character each time."


def b_writeln_lines(r):
    w, v = words(r, 2)
    return f"var b = StringBuffer();\nb.writeln('{w}');\nb.write('{v}');\nprint(b.toString().split('\\n'));", [w, v], "The newline splits the text into the two words."


def b_charcode(r):
    k = r.randint(0, 20)
    return f"var b = StringBuffer();\nb.writeCharCode({65 + k});\nb.writeCharCode({66 + k});\nprint(b);", chr(65 + k) + chr(66 + k), "writeCharCode writes the character with that code: 65 is A."


def b_empty(r):
    return "var b = StringBuffer();\nprint(b.isEmpty);", True, "Nothing has been written yet."


def b_not_empty(r):
    w = words(r, 1)[0]
    return f"var b = StringBuffer();\nb.write('{w}');\nprint(b.isNotEmpty);", True, "After a write the buffer holds text."


def b_clear(r):
    w = words(r, 1)[0]
    return f"var b = StringBuffer();\nb.write('{w}');\nb.clear();\nprint(b.length);", 0, "clear empties the buffer."


def b_initial(r):
    w, v = words(r, 2)
    return f"var b = StringBuffer('{w}');\nb.write('{v}');\nprint(b);", w + v, "The text given to the constructor is the start of the buffer."


def b_null(r):
    w = words(r, 1)[0]
    return f"var b = StringBuffer();\nb.write('{w}');\nb.write(null);\nprint(b);", w + "null", "write(null) writes the word null, it does not fail."


def b_bool(r):
    return "var b = StringBuffer();\nb.write(true);\nb.write(1.5);\nprint(b);", "true1.5", "write uses toString: true and 1.5."


def b_list(r):
    a, c = ints(r, 2, 1, 9)
    return f"var b = StringBuffer();\nb.write([{a}, {c}]);\nprint(b);", f"[{a}, {c}]", "A list is written the way print would show it."


def b_loop(r):
    n = r.randint(3, 7)
    return f"var b = StringBuffer();\nfor (var i = 1; i <= {n}; i++) {{\n  b.write(i);\n}}\nprint(b);", "".join(str(i) for i in range(1, n + 1)), "The numbers 1 to n are written one after the other."


def b_loop_sep(r):
    n = r.randint(3, 6)
    return (f"var b = StringBuffer();\nfor (var i = 1; i <= {n}; i++) {{\n  if (i > 1) b.write(',');\n  b.write(i);\n}}\nprint(b);", ",".join(str(i) for i in range(1, n + 1)),
            "The comma goes in before every number except the first.")


def b_cascade(r):
    w, v = words(r, 2)
    return f"print((StringBuffer()..write('{w}')..write('{v}')).toString());", w + v, "A cascade calls write twice and keeps the buffer."


def b_stars(r):
    n = r.randint(2, 5)
    return f"var b = StringBuffer();\nfor (var i = 1; i <= {n}; i++) {{\n  b.write('*' * i);\n}}\nprint(b.length);", n * (n + 1) // 2, "i stars each turn: 1 + 2 + ... + n characters."


# ── Interpolation ───────────────────────────────────────────────────────

def s_no_math(r):
    a, b = ints(r, 2, 2, 9)
    return f"var a = {a}, b = {b};\nprint('$a + $b');", f"{a} + {b}", "Inside quotes the + is just text: no sum is made."


def s_math(r):
    a, b = ints(r, 2, 2, 9)
    return f"var a = {a}, b = {b};\nprint('${{a + b}}');", a + b, "Braces after the dollar sign evaluate any expression."


def s_len_trap(r):
    w = words(r, 1)[0]
    return f"var w = '{w}';\nprint('$w.length');", f"{w}.length", "Without braces the interpolation takes only the name; .length is plain text."


def s_len_ok(r):
    w = words(r, 1)[0]
    return f"var w = '{w}';\nprint('${{w.length}}');", len(w), "The braces include the whole expression w.length."


def s_items(r):
    xs = ints(r, r.randint(2, 5), 1, 9)
    return f"var xs = {xs};\nprint('${{xs.length}} items');", f"{len(xs)} items", "The braces hold any expression."


def s_list_text(r):
    xs = ints(r, 3, 1, 9)
    return f"var xs = {xs};\nprint('xs=$xs');", f"xs={xs}".replace("'", ""), "A list in a string is written the way print shows it."


def s_lazy_text(r):
    xs = ints(r, 3, 1, 9)
    return f"var xs = {xs};\nprint('${{xs.map((x) => x * 2)}}');", "(" + ", ".join(str(2 * x) for x in xs) + ")", "A lazy Iterable keeps its round brackets in a string."


def s_lazy_list(r):
    xs = ints(r, 3, 1, 9)
    return f"var xs = {xs};\nprint('${{xs.map((x) => x * 2).toList()}}');", "[" + ", ".join(str(2 * x) for x in xs) + "]", "toList() first, so the text has square brackets."


def s_ternary(r):
    a, b = ints(r, 2, 2, 9)
    return f"var a = {a}, b = {b};\nprint('${{a > b ? 'big' : 'small'}}');", "big" if a > b else "small", "A condition can sit inside the braces of an interpolation."


def s_escape(r):
    a = r.randint(2, 9)
    return f"var a = {a};\nprint('\\$a');", "$a", "A backslash before the dollar stops the interpolation."


def s_escape_value(r):
    a = r.randint(2, 9)
    return f"var a = {a};\nprint('cost: \\$$a');", f"cost: ${a}", "The first dollar is escaped, the second starts the interpolation."


def s_raw(r):
    a = r.randint(2, 9)
    return f"var a = {a};\nprint(r'$a');", "$a", "A raw string r'...' does not interpolate."


def s_raw_len(r):
    return "print(r'\\n'.length);", 2, "In a raw string the backslash and the n are two characters."


def s_nl_len(r):
    return "print('\\n'.length);", 1, "\\n is one newline character."


def s_repeat(r):
    k = r.randint(2, 4)
    w = words(r, 1)[0]
    return f"print('{w}' * {k});", w * k, "Multiplying a string repeats it."


def s_repeat_num(r):
    a, k = r.randint(2, 9), r.randint(2, 4)
    return f"var a = {a};\nprint('$a' * {k});", str(a) * k, "'3' * 2 is the text 33, not the number 6."


def s_dashes(r):
    k = r.randint(3, 8)
    return f"print('-' * {k} + '>');", "-" * k + ">", "* binds tighter than +: the dashes are made first."


def s_cap(r):
    w = words(r, 1)[0]
    return f"var w = '{w}';\nprint('${{w[0].toUpperCase()}}${{w.substring(1)}}');", w.capitalize(), "Two expressions in one string: the capital letter, then the rest."


def s_adjacent(r):
    w, v = words(r, 2)
    return f"print('{w}' '{v}');", w + v, "Two string literals side by side are joined."


def s_adjacent_concat_len(r):
    a, b = ints(r, 2, 2, 9)
    return f"var a = {a}, b = {b};\nprint('$a$b'.length);", len(f"{a}{b}"), "Two digits written side by side: a two-character string."


def s_null(r):
    a = r.randint(2, 9)
    return f"int? n = {a} > 5 ? {a} : null;\nprint('n=$n');", f"n={a}" if a > 5 else "n=null", "A null prints as the word null inside a string."


def s_bool(r):
    a, b = ints(r, 2, 2, 9)
    return f"var a = {a}, b = {b};\nprint('${{a > b && b > 3}}');", a > b and b > 3, "The expression gives true or false, written as text."


def s_max(r):
    xs = ints(r, 3, 1, 30)
    return f"var xs = {xs};\nprint('max=${{xs.reduce((x, y) => x > y ? x : y)}}');", f"max={max(xs)}", "The reduce is evaluated inside the braces."


def s_map_lookup(r):
    w, a = words(r, 1)[0], r.randint(2, 9)
    return f"var m = {{'{w}': {a}}};\nprint('${{m['{w}']}}');", a, "Quotes inside the braces of an interpolation are fine; the lookup gives the number."


def s_fold_total(r):
    xs = ints(r, 3, 1, 9)
    return f"var xs = {xs};\nprint('total ${{xs.fold<int>(0, (s, x) => s + x)}}');", f"total {sum(xs)}", "The sum is computed first, then written into the text."


def s_double_in(r):
    n, h = r.randint(10, 40), r.choice((2, 4, 5, 8))
    return f"print('${{({n} / {h}).toStringAsFixed(1)}}');", fixed(n / h, 1), "toStringAsFixed inside the braces rounds the quotient to one decimal."


REGEXES: list[Maker] = [R(f) for f in (
    x_hasmatch_yes, x_hasmatch_no, x_whole, x_partial, x_first, x_first_null, x_first_null_group, x_string_match,
    x_count, x_count_each, x_all_list, x_all_sum, x_all_start, x_start, x_end, x_replace_each, x_replace_run,
    x_replace_first, x_replace_letters, x_mapped, x_mapped_double, x_mapped_swap, x_title, x_group_in_text,
    x_split_space, x_split_plain, x_split_class, x_split_digits, x_group2, x_group1, x_group_count, x_group_sum,
    x_named, x_case, x_case_default, x_greedy, x_lazy, x_alt_count, x_vowel_idx, x_contains, x_quant, x_boundary,
    x_boundary_yes, x_backref, x_start_anchor, x_escape, x_dot_match, x_dot_literal, x_trim_ws,
    b_write2, b_write_num, b_length, b_writeall_sep, b_writeall_nosep, b_writeln_len, b_writeln_lines, b_charcode,
    b_empty, b_not_empty, b_clear, b_initial, b_null, b_bool, b_list, b_loop, b_loop_sep, b_cascade, b_stars,
    s_no_math, s_math, s_len_trap, s_len_ok, s_items, s_list_text, s_lazy_text, s_lazy_list, s_ternary, s_escape,
    s_escape_value, s_raw, s_raw_len, s_nl_len, s_repeat, s_repeat_num, s_dashes, s_cap, s_adjacent,
    s_adjacent_concat_len, s_null, s_bool, s_max, s_map_lookup, s_fold_total, s_double_in)]
