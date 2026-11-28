"""Strings in Depth: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 40

DECK = Deck(
    id="py-strings",
    title="Strings in Depth",
    language="python",
    blurb="The everyday string methods, slicing tricks, f-string formats, escapes and comparisons.",
    slides=(
        Slide(
            title="split and join",
            text="split cuts a string into a list of pieces at a separator. With no separator it cuts at any run of spaces. join does the reverse: the string you call it on goes between the pieces.",
            code=r"""line = "a,b,c"
parts = line.split(",")
print(parts)
print("-".join(parts))
print("one  two".split())""",
            output="['a', 'b', 'c']\na-b-c\n['one', 'two']",
            point="split breaks text into a list; separator.join(list) glues it back.",
        ),
        Slide(
            title="strip and replace",
            text="strip removes spaces (and newlines) from both ends; lstrip and rstrip do one end. replace swaps every match for new text, or only the first few if you give a count. Each returns a new string.",
            code=r"""s = "  hi there  "
print(repr(s.strip()))
print(repr(s.lstrip()))
print("banana".replace("a", "o"))
print("banana".replace("a", "o", 1))""",
            output="'hi there'\n'hi there  '\nbonono\nbonana",
            point="strip cleans the ends, replace swaps text, and neither changes the original.",
        ),
        Slide(
            title="find, count, startswith",
            text="find gives the position of the first match, or -1 if there is none. count says how many times something appears without overlapping. startswith and endswith answer True or False.",
            code=r"""s = "banana"
print(s.find("na"))
print(s.find("x"))
print(s.count("a"))
print(s.startswith("ban"), s.endswith("a"))""",
            output="2\n-1\n3\nTrue True",
            point="find returns -1 when missing, so check for -1 before using the position.",
        ),
        Slide(
            title="Case methods",
            text="upper and lower change every letter. title capitalizes each word, while capitalize only fixes the very first letter and lowers the rest. swapcase flips each letter's case.",
            code=r"""s = "hello woRLD"
print(s.upper())
print(s.lower())
print(s.title())
print(s.capitalize())
print(s.swapcase())""",
            output="HELLO WORLD\nhello world\nHello World\nHello world\nHELLO WOrld",
            point="To compare text ignoring case, lower() both sides first.",
        ),
        Slide(
            title="in and the slicing tricks",
            text="'in' asks whether a piece of text appears inside another. A slice with a negative start takes from the end, and a step of -1 walks backwards, which reverses the string.",
            code=r"""s = "python"
print("th" in s)
print("z" not in s)
print(s[::-1])
print(s[-3:])
print(s[:-3])""",
            output="True\nTrue\nnohtyp\nhon\npyt",
            point="s[::-1] reverses; s[-3:] is the last three; s[:-3] is everything but those.",
        ),
        Slide(
            title="Immutable: build with join",
            text="You cannot change a string in place. To build a long one, collect the pieces in a list and join them once at the end, which is faster and tidier than adding to a string again and again.",
            code=r"""parts = []
for ch in "abc":
    parts.append(ch.upper())
print("".join(parts))
s = "abc"
try:
    s[0] = "X"
except TypeError as e:
    print(type(e).__name__)""",
            output="ABC\nTypeError",
            point="Strings cannot be edited; collect pieces in a list and ''.join them.",
        ),
        Slide(
            title="f-string alignment",
            text="After a colon inside the braces you can set a width and an alignment: < left, > right, ^ centre. Put a character before the alignment sign to fill the gap with it.",
            code=r"""name = "Ann"
print(f"[{name:>8}]")
print(f"[{name:<8}]")
print(f"[{name:^8}]")
print(f"[{name:*^9}]")""",
            output="[     Ann]\n[Ann     ]\n[  Ann   ]\n[***Ann***]",
            point="{value:>8} right-aligns in 8 columns; {value:*^9} centres with stars.",
        ),
        Slide(
            title="f-string number formats",
            text="For numbers, .2f means two decimals, a leading 0 pads with zeros, and a comma adds thousands separators. 03d pads a whole number to three digits, and .0% shows a fraction as a percent.",
            code=r"""x = 3.14159
n = 1234567
print(f"{x:.2f}")
print(f"{x:08.3f}")
print(f"{n:,}")
print(f"{7:03d}")
print(f"{0.25:.0%}")""",
            output="3.14\n0003.142\n1,234,567\n007\n25%",
            point=".2f rounds to 2 decimals, 08 zero-pads to width 8, a comma groups thousands.",
        ),
        Slide(
            title="f-strings: !r and =",
            text="{x!r} shows the repr of a value, which keeps the quotes and so reveals what is really inside. {x=} prints the name, an equals sign and the repr, handy for quick debugging. Double braces print a real brace.",
            code=r"""s = "hi"
print(f"{s}")
print(f"{s!r}")
print(f"{s=}")
print(f"{{braces}}")""",
            output="hi\n'hi'\ns='hi'\n{braces}",
            point="!r shows the quotes; {x=} prints 'x=value' for quick debugging.",
        ),
        Slide(
            title="ord and chr",
            text="Every character has a number. ord turns a character into its number and chr turns a number back into a character. Letters are numbered in order, so you can do arithmetic on them.",
            code=r"""print(ord("A"))
print(chr(97))
print(ord("b") - ord("a"))
print(chr(ord("a") + 2))""",
            output="65\na\n1\nc",
            point="ord(char) gives the number; chr(number) gives the character.",
        ),
        Slide(
            title="isdigit, isalpha and friends",
            text="These methods answer True only if every character in the string fits, and an empty string is always False. isdigit means all digits, isalpha all letters, isalnum letters or digits, isspace only whitespace.",
            code=r"""print("123".isdigit())
print("12a".isdigit())
print("abc".isalpha())
print("ab c".isalpha())
print("ab1".isalnum())
print("   ".isspace())""",
            output="True\nFalse\nTrue\nFalse\nTrue\nTrue",
            point="One wrong character makes the whole check False.",
        ),
        Slide(
            title="Multi-line strings, splitlines",
            text="Triple quotes let a string run over several lines, and the line break is part of the text. splitlines cuts a string into a list of its lines; a blank line becomes an empty string.",
            code=r'''poem = """roses
are red"""
print(poem)
print(len(poem))
print(poem.splitlines())
text = "a\nb\n\nc"
print(text.splitlines())''',
            output="roses\nare red\n13\n['roses', 'are red']\n['a', 'b', '', 'c']",
            point="Triple quotes keep line breaks; splitlines gives one list item per line.",
        ),
        Slide(
            title="Escapes and raw strings",
            text="A backslash starts an escape: \\n is a new line, \\t a tab, \\\" a quote and \\\\ one backslash. Put r before the quotes to make a raw string, where backslashes mean nothing special.",
            code=r"""print("line1\nline2")
print("say \"hi\"")
print("back\\slash")
print(r"C:\new\table")
print(len("\n"), len(r"\n"))
print(len("a\tb"))""",
            output="line1\nline2\nsay \"hi\"\nback\\slash\nC:\\new\\table\n1 2\n3",
            point="'\\n' is one character; r'\\n' is two. Use raw strings for file paths.",
        ),
        Slide(
            title="Comparing strings",
            text="Strings compare letter by letter by their character numbers, like a dictionary but not quite. Every capital letter comes before every lowercase one, and a shorter string that is a start of a longer one is smaller.",
            code=r"""print("apple" < "banana")
print("a" < "B")
print("Z" < "a")
print("abc" < "abd")
print("app" < "apple")
print("Hi".lower() == "hi")""",
            output="True\nFalse\nTrue\nTrue\nTrue\nTrue",
            point="Capitals sort before lowercase; lower() both sides for a fair comparison.",
        ),
        Slide(
            title="partition, zfill, center",
            text="partition cuts at the first separator only and always gives three parts: before, the separator, after. zfill pads a number string with zeros on the left; center and ljust pad with any character you choose.",
            code=r"""print("key=value=x".partition("="))
print("none".partition("="))
print("7".zfill(3))
print("hi".center(6, "-"))
print("ab".ljust(5, ".") + "|")""",
            output="('key', '=', 'value=x')\n('none', '', '')\n007\n--hi--\nab...|",
            point="partition always returns 3 parts, with empty strings when the separator is missing.",
        ),
    ),
)
