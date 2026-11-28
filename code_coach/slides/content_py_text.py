"""Text Processing: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 106

DECK = Deck(
    id="py-text",
    title="Text Processing",
    language="python",
    blurb="Cleaning lines, counting words, translate, textwrap, aligned tables, unicode, bytes, difflib and templates.",
    slides=(
        Slide(
            title="Split and clean lines",
            text="splitlines cuts text at every line break. Strip each line and keep it only if something is left, which removes blank lines and stray spaces in one comprehension.",
            code=r"""raw = "  apple \n\nbanana\n  cherry  \n"
lines = [l.strip() for l in raw.splitlines() if l.strip()]
print(lines)""",
            output="['apple', 'banana', 'cherry']",
            point="strip each line, then filter out the empty ones.",
        ),
        Slide(
            title="Counting words with Counter",
            text="Split the text into words and hand the list to Counter. most_common(n) gives the n most frequent words, with their counts, biggest first.",
            code=r"""from collections import Counter
text = "the cat and the hat and the bat"
print(Counter(text.split()).most_common(2))""",
            output="[('the', 3), ('and', 2)]",
            point="Counter(words).most_common(n) is the whole word-frequency job.",
        ),
        Slide(
            title="translate and maketrans",
            text="str.maketrans builds a table of replacements, and translate applies it to every character in one pass. A three-argument maketrans deletes characters; string.punctuation lists all the punctuation.",
            code=r"""import string
s = "Hello, World! It's me."
table = str.maketrans("", "", string.punctuation)
print(s.translate(table).lower())
print(s.translate(str.maketrans("lo", "01")))""",
            output="hello world its me\nHe001, W1r0d! It's me.",
            point="maketrans(a, b) swaps characters; maketrans('', '', x) deletes x.",
        ),
        Slide(
            title="textwrap.wrap and fill",
            text="wrap breaks long text into a list of lines no wider than the width you give. fill does the same but joins them into one string with newlines.",
            code=r"""import textwrap
t = "the quick brown fox jumps over the lazy dog"
print(textwrap.wrap(t, 15))
print(textwrap.fill(t, 20))""",
            output="['the quick brown', 'fox jumps over', 'the lazy dog']\nthe quick brown fox\njumps over the lazy\ndog",
            point="wrap returns a list of lines; fill returns one string.",
        ),
        Slide(
            title="textwrap.dedent and shorten",
            text="dedent removes the indentation shared by all lines, which is handy for triple-quoted text inside a function. shorten cuts text to a width at a word boundary and adds [...] at the end.",
            code=r"""import textwrap
print(textwrap.dedent("    a\n      b\n    c"))
t = "the quick brown fox jumps over the lazy dog"
print(textwrap.shorten(t, 20))""",
            output="a\n  b\nc\nthe quick [...]",
            point="dedent strips common indentation; shorten makes a short preview.",
        ),
        Slide(
            title="str.format and column alignment",
            text="In a format spec, < left-aligns, > right-aligns, and a number sets the width. After the width, .2f means two decimals. Together they make neat columns.",
            code=r"""rows = [("apple", 3, 1.5), ("kiwi", 12, 0.25)]
for name, qty, price in rows:
    print("{:<8}{:>4}{:>8.2f}".format(name, qty, price))""",
            output="apple      3    1.50\nkiwi      12    0.25",
            point="{:<8} left, {:>4} right, {:>8.2f} right with two decimals.",
        ),
        Slide(
            title="A report with f-strings",
            text="The same format specs work inside an f-string. Build a header, a line of dashes and one row per item, then print a total, all with matching widths.",
            code=r"""items = {"tea": 2.5, "cake": 4.25}
print(f"{'Item':<6}|{'Price':>7}")
print("-" * 14)
for k, v in items.items():
    print(f"{k:<6}|{v:>7.2f}")
print(f"{'Total':<6}|{sum(items.values()):>7.2f}")""",
            output="Item  |  Price\n--------------\ntea   |   2.50\ncake  |   4.25\nTotal |   6.75",
            point="Use the same widths in the header and the rows so columns line up.",
        ),
        Slide(
            title="Unicode: characters vs bytes",
            text="len counts characters, so 'café' has 4. ord gives a character's code number, and é is 233. Encoding to UTF-8 gives bytes, and é takes two of them, so the byte count is 5.",
            code=r"""s = "café"
print(len(s), ord("é"))
print(len(s.encode("utf-8")))
print(s.encode())""",
            output="4 233\n5\nb'caf\\xc3\\xa9'",
            point="Characters and bytes are different counts once you leave ASCII.",
        ),
        Slide(
            title="bytes vs str",
            text="A str is text and a bytes object is raw numbers from 0 to 255. Indexing bytes gives an int, and the two types are never equal. Use encode to go from str to bytes and decode to come back.",
            code=r"""b = "hi".encode()
print(b, b[0])
print(b.decode())
print(bytes([72, 105]).decode())
print("hi" == b"hi")""",
            output="b'hi' 104\nhi\nHi\nFalse",
            point="encode: str to bytes. decode: bytes to str.",
        ),
        Slide(
            title="casefold vs lower",
            text="lower is fine for English, but casefold is the stronger tool for comparing text. The German letter ß folds to 'ss', so casefold finds a match that lower misses.",
            code=r"""s = "Straße"
print(s.lower() == "strasse")
print(s.casefold() == "strasse")
print(len(s.lower()), len(s.casefold()))""",
            output="False\nTrue\n6 7",
            point="Compare with casefold() when case should not matter.",
        ),
        Slide(
            title="startswith and endswith with a tuple",
            text="startswith and endswith accept a tuple of choices, and say True if any one matches. That replaces a chain of or checks.",
            code=r"""print("report.csv".endswith((".csv", ".tsv")))
print("ftp://x".startswith(("http://", "https://")))
files = ["a.py", "_tmp", ".git", "b.py"]
print([f for f in files if not f.startswith(("_", "."))])""",
            output="True\nFalse\n['a.py', 'b.py']",
            point="Pass a tuple, not a list, to startswith and endswith.",
        ),
        Slide(
            title="join with a generator",
            text="str.join accepts any iterable of strings, so you can feed it a generator expression and skip building a list. Items must already be str, so convert numbers first.",
            code=r"""print(", ".join(str(n * n) for n in range(5)))
print("".join(c for c in "a1b2c3" if c.isdigit()))
print("-".join(w.title() for w in "red green blue".split()))""",
            output="0, 1, 4, 9, 16\n123\nRed-Green-Blue",
            point="sep.join(x for x in items) builds a string in one step.",
        ),
        Slide(
            title="difflib: how similar are two strings?",
            text="SequenceMatcher(None, a, b).ratio() gives a similarity from 0 to 1. get_close_matches picks the best matches from a list, which is good for fixing typos.",
            code=r"""import difflib
sm = difflib.SequenceMatcher(None, "apple", "appel")
print(sm.ratio())
print(difflib.get_close_matches("appel", ["apple", "ladder", "zebra"]))""",
            output="0.8\n['apple']",
            point="ratio() is 1.0 for identical text and near 0 for unrelated text.",
        ),
        Slide(
            title="string.Template",
            text="A Template uses $name for the parts to fill in, and ${name} when letters follow right after. substitute needs every value, while safe_substitute leaves missing ones as they are.",
            code=r"""from string import Template
t = Template("Hi $name, total: ${n}USD")
print(t.substitute(name="Ann", n=5))
print(t.safe_substitute(name="Bo"))""",
            output="Hi Ann, total: 5USD\nHi Bo, total: ${n}USD",
            point="Templates are safe for text that users write, since they cannot run code.",
        ),
        Slide(
            title="A word-frequency pipeline",
            text="Lowercase the text, delete the punctuation with translate, split into words and count them. Words with equal counts keep the order they first appeared in.",
            code=r"""import string
from collections import Counter
text = "It's the end. The END, it's near!"
clean = text.lower().translate(str.maketrans("", "", string.punctuation))
print(clean)
print(Counter(clean.split()).most_common(3))""",
            output="its the end the end its near\n[('its', 2), ('the', 2), ('end', 2)]",
            point="lower, translate, split, Counter: four steps for most word counts.",
        ),
    ),
)
