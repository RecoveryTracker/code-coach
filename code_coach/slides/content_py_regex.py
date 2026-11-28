"""Regular Expressions: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 102

DECK = Deck(
    id="py-regex",
    title="Regular Expressions",
    language="python",
    blurb="Pattern matching with the re module: search, groups, quantifiers, sub, split, flags and lookahead.",
    slides=(
        Slide(
            title="search, match and fullmatch",
            text="re.search looks anywhere in the text. re.match only looks at the very start. re.fullmatch needs the whole text to fit the pattern.",
            code=r"""import re
s = "cat and dog"
print(bool(re.search("dog", s)))
print(bool(re.match("dog", s)))
print(bool(re.match("cat", s)))
print(bool(re.fullmatch("cat", s)))""",
            output="True\nFalse\nTrue\nFalse",
            point="search = anywhere, match = from the start, fullmatch = the whole string.",
        ),
        Slide(
            title="Raw strings for patterns",
            text="In a normal string, backslash-n is one newline character. A raw string r'...' keeps the backslash, so the pattern reaches re exactly as you typed it. Always write patterns as raw strings.",
            code=r"""import re
print(len("\n"), len(r"\n"))
print(re.findall(r"\d+", "a1 b22 c333"))
print(re.findall("\\d+", "a1 b22"))""",
            output="1 2\n['1', '22', '333']\n['1', '22']",
            point="Use r'...' for every pattern, so you never double your backslashes.",
        ),
        Slide(
            title="Character classes",
            text="[a-z] matches one lowercase letter. \\d is a digit, \\w is a letter, digit or underscore, and \\s is any whitespace. Add + to take a whole run of them.",
            code=r"""import re
s = "Ab 12_x!"
print(re.findall(r"[a-z]", s))
print(re.findall(r"\d", s))
print(re.findall(r"\w+", s))
print(re.findall(r"\s", s))""",
            output="['b', 'x']\n['1', '2']\n['Ab', '12_x']\n[' ']",
            point="[..] is a set of allowed characters; \\d \\w \\s are shortcuts for common sets.",
        ),
        Slide(
            title="Quantifiers: * + ? {m,n}",
            text="* means zero or more, + means one or more, ? means zero or one, and {m,n} means between m and n. Each one applies to the thing just before it.",
            code=r"""import re
t = "a ab abb"
print(re.findall(r"ab*", t))
print(re.findall(r"ab+", t))
print(re.findall(r"ab?", t))
print(re.findall(r"b{2,3}", "b bb bbbb"))""",
            output="['a', 'ab', 'abb']\n['ab', 'abb']\n['a', 'ab', 'ab']\n['bb', 'bbb']",
            point="* = 0 or more, + = 1 or more, ? = 0 or 1, {m,n} = a range.",
        ),
        Slide(
            title="Greedy vs lazy",
            text="By default a quantifier is greedy: it grabs as much as it can. Add a ? after it to make it lazy, so it stops at the first place the rest of the pattern fits.",
            code=r"""import re
html = "<b>hi</b><i>yo</i>"
print(re.findall(r"<.*>", html))
print(re.findall(r"<.*?>", html))""",
            output="['<b>hi</b><i>yo</i>']\n['<b>', '</b>', '<i>', '</i>']",
            point="Greedy .* takes the most; lazy .*? takes the least.",
        ),
        Slide(
            title="Anchors: ^ $ and \\b",
            text="^ means the start and $ means the end of the text. \\b is a word boundary, the edge between a word character and a non-word character, so it finds whole words only.",
            code=r"""import re
print(re.findall(r"^\w+", "one two"))
print(re.findall(r"\w+$", "one two"))
print(re.findall(r"\bcat\b", "cat concat cat."))
print(re.findall(r"cat", "cat concat cat."))""",
            output="['one']\n['two']\n['cat', 'cat']\n['cat', 'cat', 'cat']",
            point="Wrap a word in \\b...\\b to stop it matching inside longer words.",
        ),
        Slide(
            title="Groups and group(1)",
            text="Parentheses make a group that remembers the part it matched. group(0) is the whole match, group(1) is the first set of parentheses, and groups() gives them all.",
            code=r"""import re
m = re.search(r"(\d+)-(\d+)", "tel 555-1234 ok")
print(m.group(0))
print(m.group(1), m.group(2))
print(m.groups())
print(m.span())""",
            output="555-1234\n555 1234\n('555', '1234')\n(4, 12)",
            point="Groups are numbered by their opening parenthesis, starting at 1.",
        ),
        Slide(
            title="Named groups",
            text="Write (?P<name>...) to give a group a name. Then you ask for it by name instead of counting parentheses, and groupdict() returns them all as a dict.",
            code=r"""import re
m = re.match(r"(?P<y>\d{4})-(?P<m>\d\d)", "2026-03-01")
print(m.group("y"), m.group("m"))
print(m.groupdict())""",
            output="2026 03\n{'y': '2026', 'm': '03'}",
            point="Named groups make a pattern readable and survive adding new groups.",
        ),
        Slide(
            title="findall: with and without groups",
            text="With no groups, findall returns the whole matches. With one group it returns only what that group caught. With two or more groups it returns a tuple per match.",
            code=r"""import re
s = "a1 b2"
print(re.findall(r"[a-z]\d", s))
print(re.findall(r"([a-z])\d", s))
print(re.findall(r"([a-z])(\d)", s))""",
            output="['a1', 'b2']\n['a', 'b']\n[('a', '1'), ('b', '2')]",
            point="Adding parentheses to a pattern changes what findall returns.",
        ),
        Slide(
            title="finditer: matches with positions",
            text="finditer gives one match object at a time instead of a list of strings. Use it when you need where each match starts, or its groups.",
            code=r"""import re
for m in re.finditer(r"\d+", "a1 bb22 c333"):
    print(m.group(), m.start())""",
            output="1 1\n22 5\n333 9",
            point="finditer = findall plus the position and groups of each match.",
        ),
        Slide(
            title="sub with a function",
            text="re.sub replaces every match. Give it a string for a fixed replacement, or a function that receives the match and returns the replacement text.",
            code=r"""import re
def double(m):
    return str(int(m.group()) * 2)
print(re.sub(r"\d+", double, "3 apples, 10 pears"))
print(re.sub(r"\s+", " ", "a   b \n c"))""",
            output="6 apples, 20 pears\na b c",
            point="A function as the replacement lets you compute the new text.",
        ),
        Slide(
            title="split on a pattern",
            text="str.split only cuts on a fixed piece of text. re.split cuts on a pattern. Put the separator in a group to keep it in the result, and use maxsplit to limit the cuts.",
            code=r"""import re
print(re.split(r"[,;] *", "a, b;c,  d"))
print(re.split(r"(-)", "1-2-3"))
print(re.split(r"\s+", "a b  c", maxsplit=1))""",
            output="['a', 'b', 'c', 'd']\n['1', '-', '2', '-', '3']\n['a', 'b  c']",
            point="re.split handles messy separators that str.split cannot.",
        ),
        Slide(
            title="Flags: re.I and re.M",
            text="re.I ignores upper and lower case. Normally ^ and $ match only at the ends of the whole text; re.M makes them match at the start and end of every line.",
            code=r"""import re
print(re.findall(r"cat", "Cat CAT cat"))
print(re.findall(r"cat", "Cat CAT cat", re.I))
text = "one\ntwo"
print(re.findall(r"^\w+$", text))
print(re.findall(r"^\w+$", text, re.M))""",
            output="['cat']\n['Cat', 'CAT', 'cat']\n[]\n['one', 'two']",
            point="Pass flags as the last argument: re.I for case, re.M for lines.",
        ),
        Slide(
            title="compile and re.escape",
            text="re.compile builds the pattern once so you can reuse it. re.escape puts a backslash before special characters, so user text is matched literally instead of being read as a pattern.",
            code=r"""import re
pat = re.compile(r"\d+")
print(pat.findall("a1b22"))
price = "1.5+2"
print(re.escape(price))
print(bool(re.search(price, "1x52")))
print(bool(re.search(re.escape(price), "1x52")))""",
            output="['1', '22']\n1\\.5\\+2\nTrue\nFalse",
            point="Wrap any text that is not meant as a pattern in re.escape().",
        ),
        Slide(
            title="Lookahead: a password rule",
            text="(?=...) looks ahead and checks that something follows, without using up any characters. Stack several lookaheads at the start to demand a digit and a capital, then match the length.",
            code=r"""import re
rule = r"(?=.*\d)(?=.*[A-Z]).{8,}"
for pw in ["abc12345", "Abcdefg1", "Short1A"]:
    print(pw, bool(re.fullmatch(rule, pw)))""",
            output="abc12345 False\nAbcdefg1 True\nShort1A False",
            point="Each (?=...) is one extra rule the text must satisfy.",
        ),
    ),
)
