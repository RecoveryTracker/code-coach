"""Strings Pack, Python side: eight activities about text.

Case & Trim, Split & Join, Find It, Replace It, Format It, String Math,
Char Codes, Text Check. Every answer is modelled by hand - upper-casing is
arithmetic on character codes, a split is a search loop, a replace is a scan,
padding is counting, a base conversion is repeated division - and
tests/test_brain_packs.py then runs every template through the real
interpreter. The hand models (`lower`, `py_split`, `py_replace`...) are shared
with the JavaScript side (`_strings_js.py`), which only adds the places where
JavaScript differs.
"""

from __future__ import annotations

import random
from string import Template
from typing import Any, Callable

from ._model import WORDS, Maker, ipow, isort, py_show, upper, yes_no_py
from ._model import params as _int_params
from .items import Item

# ── Hand models of the string methods ───────────────────────────────────

LOWER = "abcdefghijklmnopqrstuvwxyz"
WS = " \t\n"
#: Every printable ASCII character, in code order from 32: ord is 32 + position, chr reads it back.
ASCII = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"


def is_alpha(ch: str) -> bool:
    return "a" <= ch <= "z" or "A" <= ch <= "Z"


def is_digit(ch: str) -> bool:
    return "0" <= ch <= "9"


def lower(text: str) -> str:
    return "".join(chr(ord(ch) + 32) if "A" <= ch <= "Z" else ch for ch in text)


def capitalize(text: str) -> str:
    return upper(text[:1]) + lower(text[1:])


def title(text: str) -> str:
    out, inside = [], False
    for ch in text:
        out.append((lower(ch) if inside else upper(ch)) if is_alpha(ch) else ch)
        inside = is_alpha(ch)
    return "".join(out)


def swapcase(text: str) -> str:
    return "".join(upper(ch) if "a" <= ch <= "z" else lower(ch) for ch in text)


def lstrip(text: str, chars: str = WS) -> str:
    i = 0
    while i < len(text) and text[i] in chars:
        i += 1
    return text[i:]


def rstrip(text: str, chars: str = WS) -> str:
    j = len(text)
    while j > 0 and text[j - 1] in chars:
        j -= 1
    return text[:j]


def strip(text: str, chars: str = WS) -> str:
    return lstrip(rstrip(text, chars), chars)


def find_in(text: str, sub: str, start: int = 0, end: int | None = None) -> int:
    """text.find(sub, start, end) with Python's rules for negative and oversized bounds."""
    n = len(text)
    lo = max(0, n + start) if start < 0 else start
    hi = n if end is None else (max(0, n + end) if end < 0 else min(end, n))
    for i in range(lo, hi - len(sub) + 1):
        if text[i:i + len(sub)] == sub:
            return i
    return -1


def rfind_in(text: str, sub: str) -> int:
    for i in range(len(text) - len(sub), -1, -1):
        if text[i:i + len(sub)] == sub:
            return i
    return -1


def count_sub(text: str, sub: str) -> int:
    """text.count(sub): separate (non-overlapping) matches, scanning left to right."""
    if sub == "":
        return len(text) + 1
    n, i = 0, 0
    while i + len(sub) <= len(text):
        if text[i:i + len(sub)] == sub:
            n += 1
            i += len(sub)
        else:
            i += 1
    return n


def py_replace(text: str, old: str, new: str, count: int = -1) -> str:
    """text.replace(old, new, count): left to right, matches do not overlap; an empty `old` matches between letters."""
    out, done = [], 0
    if old == "":
        for ch in text:
            if count < 0 or done < count:
                out.append(new)
                done += 1
            out.append(ch)
        if count < 0 or done < count:
            out.append(new)
        return "".join(out)
    i = 0
    while i < len(text):
        if (count < 0 or done < count) and text[i:i + len(old)] == old:
            out.append(new)
            i += len(old)
            done += 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def py_split(text: str, sep: str, maxsplit: int = -1) -> list[str]:
    """text.split(sep, maxsplit) for a non-empty sep."""
    out, start, cuts = [], 0, 0
    while maxsplit < 0 or cuts < maxsplit:
        i = find_in(text, sep, start)
        if i < 0:
            break
        out.append(text[start:i])
        start = i + len(sep)
        cuts += 1
    out.append(text[start:])
    return out


def py_rsplit(text: str, sep: str, maxsplit: int) -> list[str]:
    out, end, cuts = [], len(text), 0
    while cuts < maxsplit:
        i = rfind_in(text[:end], sep)
        if i < 0:
            break
        out.insert(0, text[i + len(sep):end])
        end = i
        cuts += 1
    out.insert(0, text[:end])
    return out


def py_split_ws(text: str) -> list[str]:
    """text.split() with no argument: runs of whitespace are one cut, and the ends do not make empty pieces."""
    out, cur = [], ""
    for ch in text:
        if ch in WS:
            if cur:
                out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def py_splitlines(text: str) -> list[str]:
    if text == "":
        return []
    pieces = py_split(text, "\n")
    if pieces[-1] == "":
        pieces.pop()
    return pieces


def partition(text: str, sep: str) -> tuple[str, str, str]:
    i = find_in(text, sep)
    return (text, "", "") if i < 0 else (text[:i], sep, text[i + len(sep):])


def join(sep: str, items: list[str]) -> str:
    out = ""
    for k, item in enumerate(items):
        out += (sep if k else "") + item
    return out


def lex_less(a: str, b: str) -> bool:
    """a < b for strings: the first differing character decides, else the shorter is smaller."""
    for x, y in zip(a, b):
        if x != y:
            return ord(x) < ord(y)
    return len(a) < len(b)


def reverse_text(text: str) -> str:
    return "".join(text[len(text) - 1 - i] for i in range(len(text)))


def sorted_chars(text: str) -> list[str]:
    return isort(list(text))


def ord_of(ch: str) -> int:
    return 32 + ASCII.index(ch)


def chr_of(code: int) -> str:
    return ASCII[code - 32]


def digits_in(n: int, base: int, big: bool = False) -> str:
    """n written in a base (2 to 16), by repeated division."""
    alphabet = "0123456789abcdef" if not big else "0123456789ABCDEF"
    if n == 0:
        return "0"
    out = ""
    while n > 0:
        out = alphabet[n % base] + out
        n //= base
    return out


def with_commas(n: int) -> str:
    s = str(n)
    out = ""
    for k, ch in enumerate(s):
        if k and (len(s) - k) % 3 == 0:
            out += ","
        out += ch
    return out


def pad_left(text: str, width: int, fill: str) -> str:
    return fill * (width - len(text)) + text if len(text) < width else text


def pad_right(text: str, width: int, fill: str) -> str:
    return text + fill * (width - len(text)) if len(text) < width else text


def pad_middle(text: str, width: int, fill: str) -> str:
    """format's ^: the extra fill, when the gap is odd, goes on the right."""
    gap = width - len(text)
    if gap <= 0:
        return text
    left = gap // 2
    return fill * left + text + fill * (gap - left)


def zero_pad(text: str, width: int) -> str:
    """str.zfill: zeros after any sign."""
    sign = text[0] if text[:1] in ("-", "+") else ""
    rest = text[len(sign):]
    return sign + "0" * (width - len(text)) + rest if len(text) < width else text


def decimal_text(whole: int, frac: str) -> str:
    return f"{whole}.{frac}" if frac else str(whole)


def fixed(whole: int, frac: str, places: int) -> str:
    """The decimal number whole.frac (no digit that decides the rounding is a lone 5) at `places` decimals, half up."""
    digits = [int(ch) for ch in (str(whole) + frac[:places].ljust(places, "0"))]
    if len(frac) > places and frac[places] >= "5":
        k = len(digits) - 1
        while k >= 0:
            if digits[k] == 9:
                digits[k] = 0
                k -= 1
            else:
                digits[k] += 1
                break
        else:
            digits.insert(0, 1)
    text = "".join(str(d) for d in digits)
    cut = len(text) - places
    return text[:cut] + ("." + text[cut:] if places else "")


# ── Random parameters ───────────────────────────────────────────────────

SHORT = tuple(w for w in WORDS if len(w) <= 5)
PALINDROMES = ("level", "radar", "noon", "civic", "kayak", "refer", "abba", "deed", "madam", "rotor")
PAIRS = (("listen", "silent"), ("evil", "vile"), ("night", "thing"), ("stone", "notes"), ("races", "cares"),
         ("below", "elbow"), ("angel", "glean"), ("study", "dusty"), ("listen", "silence"), ("stone", "stove"),
         ("night", "light"), ("races", "caves"), ("below", "blown"), ("study", "sturdy"), ("save", "saves"))


def P(rng: random.Random) -> dict[str, Any]:
    """The names a Strings template can use. Numbers: $a $b $d (different, 2-9), $n (10-40), $k (1-3), $num (4 digits),
    $dg (a digit of it). Words: $w $v $u (different), $W $V (capitalised), $WU (upper), $ph ($w $v), $ph3, $mix (mixed
    case), $s1-$s3 (short words), $csv, $sp3, $z0 and $z1 (first and last letter of $w), $c (a letter of $w), $C
    (it in capitals), $q (a letter not in $w), $sub (two letters of $w), $x $y (different letters a-h), $L and $LU
    (any letter, small and capital), $an (letters and digits mixed), $dec1 $dec2 $dec3 (decimals with 1, 2, 3 places
    whose last digit is not 5, so rounding is never a tie), $big (5-7 digits), $code (the character code of $L),
    $cw (a width that centres $w with an even gap)."""
    p = _int_params(rng)
    w, v, u = rng.sample(WORDS, 3)
    s1, s2, s3 = rng.sample(SHORT, 3)
    p.update(w=w, v=v, u=u, W=capitalize(w), V=capitalize(v), WU=upper(w), ph=f"{w} {v}", ph3=f"{w} {v} {u}",
             s1=s1, s2=s2, s3=s3, csv=f"{s1},{s2},{s3}", sp3=f"{s1} {s2} {s3}", z0=w[0], z1=w[-1])
    p["y"] = rng.choice([ch for ch in "abcdefgh" if ch != p["x"]])
    p["c"] = rng.choice(w)
    p["C"] = upper(p["c"])
    p["q"] = rng.choice([ch for ch in "zxqjv" if ch not in w])
    i = rng.randrange(len(w) - 1)
    p["sub"] = w[i:i + 2]
    p["num"] = str(rng.randint(1000, 9999))
    p["dg"] = rng.choice(p["num"])
    p["L"] = rng.choice(LOWER)
    p["LU"] = upper(p["L"])
    chars = rng.sample(LOWER, 3) + [str(rng.randint(0, 9)) for _ in range(2)]
    rng.shuffle(chars)
    p["an"] = "".join(chars)
    while True:
        mixed = "".join(upper(ch) if rng.random() < 0.5 else ch for ch in w)
        if mixed != w and mixed != upper(w):
            break
    p["mix"] = mixed
    p["dw"] = rng.randint(1, 99)
    p["f1"] = rng.choice("012346789")
    p["f2"] = str(rng.randint(0, 9)) + rng.choice("012346789")
    p["f3"] = str(rng.randint(0, 99)).zfill(2) + rng.choice("012346789")
    p["dec1"], p["dec2"], p["dec3"] = (f"{p['dw']}.{p[f]}" for f in ("f1", "f2", "f3"))
    p["big"] = rng.randint(10000, 9999999)
    p["code"] = ord_of(p["L"])
    p["cw"] = len(w) + 2 * p["k"]
    return p


def show(value: Any) -> str:
    return value if isinstance(value, str) else py_show(value)


def S(fmt: str, ans: str | Callable[[dict], Any], why: str | Callable[[dict], str] = "",
      check: Callable[[str], str] | None = None) -> Maker:
    """A template: `fmt` (a string.Template with the holes of `P`) is the prompt; `ans` the hand-worked answer (a
    value or a function of the parameters; non-strings are printed the way Python prints them)."""
    def make(rng: random.Random) -> Item:
        p = P(rng)
        prompt = Template(fmt).substitute(p)
        got = show(ans(p) if callable(ans) else ans)
        why_text = why(p) if callable(why) else Template(why).safe_substitute(p)
        return Item(prompt, got, why_text, check=check(prompt) if check else "")
    make.__name__ = "s_" + fmt[:24].replace("\n", " ")
    return make


def Q(fmt: str, truth: bool | Callable[[dict], bool], why: str | Callable[[dict], str] = "") -> Maker:
    """A yes/no template."""
    return S(fmt, lambda p: "yes" if (truth(p) if callable(truth) else truth) else "no", why, check=yes_no_py)


# ── 1. Case & Trim ──────────────────────────────────────────────────────

UP = "upper() turns every letter into a capital and leaves the rest alone."
STR_NEW = "Strings never change: a method gives back a new string and the old one stays as it was."
SET = "The argument is a set of characters: any of them are removed from the end, in any order."

CASE: list[Maker] = [
    S('"$w".upper()', lambda p: upper(p["w"]), UP),
    S('"$W".lower()', lambda p: lower(p["W"]), "lower() turns every capital into a small letter."),
    S('"$ph".upper()', lambda p: upper(p["ph"]), UP),
    S('"$ph".title()', lambda p: title(p["ph"]), "title() raises the first letter of every word."),
    S('"$ph".capitalize()', lambda p: capitalize(p["ph"]), "capitalize() raises only the first letter of the whole string."),
    S('"$WU".capitalize()', lambda p: capitalize(p["WU"]), "capitalize() raises the first letter and lowers all the others."),
    S('"$W".swapcase()', lambda p: swapcase(p["W"]), "swapcase() flips every letter: capitals go small, small go capital."),
    S('"$mix".swapcase()', lambda p: swapcase(p["mix"]), "swapcase() flips every letter."),
    S('"$mix".lower()', lambda p: lower(p["mix"]), "lower() makes every letter small, whatever it was."),
    S('"$mix".title()', lambda p: title(p["mix"]), "title() capitalises the first letter of each word and lowers the rest."),
    S('"  $w  ".strip()', lambda p: p["w"], "strip() removes the spaces at both ends."),
    S('len("  $w  ")', lambda p: len(p["w"]) + 4, "Every space counts as a character: two each side."),
    S('len("  $w  ".strip())', lambda p: len(p["w"]), "strip() removes the four spaces, so only the word is left."),
    S('"--$w--".strip("-")', lambda p: p["w"], "strip(chars) removes those characters from both ends."),
    S('"--$w--".lstrip("-")', lambda p: p["w"] + "--", "lstrip() works on the left end only."),
    S('"--$w--".rstrip("-")', lambda p: "--" + p["w"], "rstrip() works on the right end only."),
    S('"xzx${w}zx".strip("xz")', lambda p: p["w"], SET),
    S('"xzx${w}zx".lstrip("xz")', lambda p: p["w"] + "zx", "lstrip stops at the first character not in the set, so the right end is untouched."),
    S('"$w".strip("$z1")', lambda p: strip(p["w"], p["z1"]),
      "strip keeps removing that letter from the end while the next character matches too."),
    S('"$w".strip("$z0")', lambda p: strip(p["w"], p["z0"]), "strip(chars) removes those characters from the ends, even when they are part of the word."),
    S('"$w".upper().lower()', lambda p: p["w"], "Capitals first, then back to small: the word as it began."),
    S('"$w".lower().upper()', lambda p: p["WU"], "The last method decides: upper()."),
    S('"  $ph  ".strip().upper()', lambda p: upper(p["ph"]), "strip first, then upper: the inner space stays."),
    S('"  $ph  ".strip().title()', lambda p: title(p["ph"]), "strip() takes the ends; title() capitalises both words."),
    S('"$ph".upper().title()', lambda p: title(p["ph"]), "title() lowers the rest of each word, so the earlier upper() does not show."),
    S('"$ph".title().swapcase()', lambda p: swapcase(title(p["ph"])), "title() first, then swapcase() flips it all."),
    S('"$w"[0].upper() + "$w"[1:]', lambda p: p["W"], "Capitalise the first letter and glue the rest back on."),
    S('"$w"[0].upper()', lambda p: upper(p["w"][0]), "Index 0 is the first letter; upper() capitalises it."),
    S('"$w".upper()[-1]', lambda p: upper(p["w"][-1]), "upper() first, then [-1] is the last character."),
    S('"$w".isupper()', "False", "isupper() is True only when every letter is a capital."),
    S('"$WU".isupper()', "True", "Every letter is a capital."),
    S('"$w".islower()', "True", "islower() is True when every letter is small."),
    S('"$W".islower()', "False", "The first letter is a capital, so not all are small."),
    S('"$W".istitle()', "True", "A capital first letter and small ones after: title case."),
    S('"$WU".istitle()', "False", "In title case only the first letter of a word is a capital."),
    S('"$mix".isupper()', "False", "Some letters are small."),
    S('"123".isupper()', "False", "isupper() needs at least one letter, and digits have no case."),
    S('"a1".islower()', "True", "Digits have no case, so only the letter counts: it is small."),
    S(r'"\t$w\n".strip()', lambda p: p["w"], "strip() removes tabs and newlines as well as spaces."),
    S(r'len("\t$w\n")', lambda p: len(p["w"]) + 2, r"\t and \n are one character each."),
    S(r'len("\t$w\n".strip())', lambda p: len(p["w"]), "Tab and newline count as whitespace for strip()."),
    S(r'len(" \t\n ".strip())', "0", "Nothing but whitespace: strip() leaves the empty string."),
    S('s = "$w"\ns.upper()\ns', lambda p: p["w"], STR_NEW),
    S('s = "$w"\ns = s.upper()\ns', lambda p: p["WU"], "s = s.upper() stores the new string under the old name."),
    S('s = "  $w  "\ns = s.strip()\nlen(s)', lambda p: len(p["w"]), "s now names the stripped string."),
    S('name = "$W"\nname.lower() == name', "False", "lower() makes a different string, so it is not equal to the original."),
    S('"$w".capitalize() == "$W"', "True", "capitalize() gives the capital first letter."),
    S('"  $w".strip() == "$w"', "True", "After strip() the spaces are gone."),
    S('" ".join(word.capitalize() for word in "$ph".split())', lambda p: title(p["ph"]),
      "Split into words, capitalise each, join with a space: what title() does."),
    S('"$ph".title().replace(" ", "")', lambda p: title(p["ph"]).replace(" ", ""),
      "title() first, then the space is removed: CamelCase."),
    S('"$ph".split()[0].capitalize()', lambda p: p["W"], "The first word, capitalised."),
    S('len("$w".upper())', lambda p: len(p["w"]), "Changing case never changes the length."),
    S('"[" + " $w ".rstrip() + "]"', lambda p: "[ " + p["w"] + "]", "rstrip() removes only the space on the right."),
    S('"[" + " $w ".lstrip() + "]"', lambda p: "[" + p["w"] + " ]", "lstrip() removes only the space on the left."),
]

# ── 2. Split & Join ─────────────────────────────────────────────────────

SPL = "split(sep) cuts at every separator and gives a list of the pieces."
EDGE = "Two separators in a row leave an empty piece between them."


def _l3(p: dict) -> list[str]:
    return [p["s1"], p["s2"], p["s3"]]


SPLIT: list[Maker] = [
    S('"$csv".split(",")', _l3, SPL),
    S('"$sp3".split(" ")', _l3, SPL),
    S('"$sp3".split()', _l3, "split() with no argument cuts at any run of whitespace."),
    S('"$csv".split(",")[1]', lambda p: p["s2"], "split gives a list; [1] is its second piece."),
    S('len("$csv".split(","))', "3", "Two commas make three pieces."),
    S('"$s1 $s2".split()[-1]', lambda p: p["s2"], "The last piece of the split."),
    S('"$csv".split(",", 1)', lambda p: [p["s1"], p["s2"] + "," + p["s3"]], "The second argument is the most cuts: one cut, two pieces, the rest stays together."),
    S('"$csv".rsplit(",", 1)', lambda p: [p["s1"] + "," + p["s2"], p["s3"]], "rsplit cuts from the right, so the one cut is the last comma."),
    S('"$csv".split(",", 1)[1]', lambda p: p["s2"] + "," + p["s3"], "After one cut, the second piece is everything that is left."),
    S('"$s1,,$s2".split(",")', lambda p: [p["s1"], "", p["s2"]], EDGE),
    S('len("$s1,,$s2".split(","))', "3", "Two commas always make three pieces, even when one is empty."),
    S('"$s1  $s2".split(" ")', lambda p: [p["s1"], "", p["s2"]], "split(' ') cuts at each single space, so two spaces leave an empty piece."),
    S('"$s1  $s2".split()', lambda p: [p["s1"], p["s2"]], "split() treats a whole run of spaces as one cut."),
    S('len("$s1  $s2".split(" "))', "3", "The empty piece between the two spaces counts."),
    S('len("$s1  $s2".split())', "2", "split() ignores the extra spaces, so just the two words."),
    S('"".split(",")', lambda p: [""], "Splitting the empty string on a separator gives one empty piece."),
    S('"".split()', lambda p: [], "split() on the empty string finds no words: an empty list."),
    S('len("".split(","))', "1", "One empty piece."),
    S('"$s1,$s2,".split(",")', lambda p: [p["s1"], p["s2"], ""], "A separator at the end leaves an empty piece after it."),
    S('"$s1".split(",")', lambda p: [p["s1"]], "No separator found: the whole string, as one piece."),
    S('"-".join(["$s1", "$s2", "$s3"])', lambda p: join("-", _l3(p)), "join puts the string between the items."),
    S('"".join(["$s1", "$s2"])', lambda p: p["s1"] + p["s2"], "An empty separator just glues the items together."),
    S('", ".join(["$s1", "$s2"])', lambda p: p["s1"] + ", " + p["s2"], "The separator goes between items, not at the ends."),
    S('" ".join("$csv".split(","))', lambda p: join(" ", _l3(p)), "Split on commas, then join with spaces."),
    S('"-".join("$s1")', lambda p: join("-", list(p["s1"])), "A string is a sequence of letters, so join puts a dash between each."),
    S('"$sp3".split()[::-1]', lambda p: _l3(p)[::-1], "[::-1] reverses the list."),
    S('" ".join("$sp3".split()[::-1])', lambda p: join(" ", _l3(p)[::-1]), "Reverse the word order, then join."),
    S('"".join(sorted("$w"))', lambda p: "".join(sorted_chars(p["w"])), "sorted() puts the letters in order; join glues them back."),
    S('"".join(reversed("$w"))', lambda p: reverse_text(p["w"]), "reversed() walks backwards; join glues the letters."),
    S('"$w".split("$x")', lambda p: py_split(p["w"], p["x"]), "The letter is the separator and is thrown away; a missing letter leaves the word whole."),
    S('len("$w".split("$x"))', lambda p: len(py_split(p["w"], p["x"])), "One more piece than there are separators."),
    S('list("$w")', lambda p: list(p["w"]), "list() on a string gives one item per letter."),
    S('"$a $b".split()[0] + "$a $b".split()[1]', lambda p: str(p["a"]) + str(p["b"]), "split gives strings, so + joins them instead of adding."),
    S('[int(x) for x in "$a $b $d".split()]', lambda p: [p["a"], p["b"], p["d"]], "int() turns each text piece into a number."),
    S('sum(int(x) for x in "$a,$b,$d".split(","))', lambda p: p["a"] + p["b"] + p["d"], "Split, convert each piece to a number, add them."),
    S('"$s1=$a".split("=")', lambda p: [p["s1"], str(p["a"])], "The number is still text, so it prints with quotes."),
    S('"$s1=$a".split("=")[1]', lambda p: str(p["a"]), "The piece after the = (as text)."),
    S('int("$s1=$a".split("=")[1]) + 1', lambda p: p["a"] + 1, "int() makes the piece a number, then add 1."),
    S(r'"$s1 $s2\n$s3".splitlines()', lambda p: [p["s1"] + " " + p["s2"], p["s3"]], r"splitlines() cuts at each newline (\n)."),
    S(r'"$s1\n$s2\n".split("\n")', lambda p: [p["s1"], p["s2"], ""], "The newline at the end leaves an empty piece."),
    S(r'len("$s1\n$s2\n".splitlines())', "2", "splitlines() does not make a last empty piece."),
    S('"$s1-$s2".partition("-")', lambda p: (p["s1"], "-", p["s2"]), "partition gives a tuple: before, the separator, after."),
    S('"$s1-$s2-$s3".partition("-")', lambda p: (p["s1"], "-", p["s2"] + "-" + p["s3"]), "partition cuts at the first separator only."),
    S('"$s1".partition("-")', lambda p: (p["s1"], "", ""), "No separator: the whole string and two empty strings."),
    S('words = "$sp3".split()\nwords[1]', lambda p: p["s2"], "words is the list of three; [1] is the middle."),
    S('words = "$sp3".split()\nlen(words)', "3", "Three words."),
    S('"$csv".split(",")[::-1]', lambda p: _l3(p)[::-1], "Split, then reverse the list."),
    S('",".join(["$s1", "$s2"]).split(",") == ["$s1", "$s2"]', "True", "join then split with the same separator gets the list back."),
    S('" ".join(["$s1", "$s2"]).split(" ")', lambda p: [p["s1"], p["s2"]], "join and split undo each other."),
    S('"-".join("$sp3".split())', lambda p: join("-", _l3(p)), "Words in, dashes between."),
    S('"$sp3".split()[0][0]', lambda p: p["s1"][0], "The first letter of the first word."),
    S('"$w".join(["a", "b", "c"])', lambda p: "a" + p["w"] + "b" + p["w"] + "c", "Whatever the string is, join puts it between the items."),
    S('"+".join(map(str, [$a, $b, $d]))', lambda p: f"{p['a']}+{p['b']}+{p['d']}", "join needs strings, so map(str, ...) first."),
    S('"$s1:$s2:$s3".split(":")[-1]', lambda p: p["s3"], "The last piece."),
    S('"$sp3".split(" ", 1)[1]', lambda p: p["s2"] + " " + p["s3"], "One cut at the first space: the rest stays as one piece."),
    S('"$x,$y".split(",")', lambda p: [p["x"], p["y"]], "Two letters, one comma: two pieces."),
    S('",".join("$x$y")', lambda p: p["x"] + "," + p["y"], "join walks over the letters of a string."),
]

# ── 3. Find It ──────────────────────────────────────────────────────────

FIRST = "find gives the position of the first match, counting from 0."
MISS = "find gives -1 when there is no match."


def _before(rng: random.Random) -> Item:
    p = P(rng)
    while rfind_in(p["w"], p["c"]) < 1:
        p = P(rng)
    w, c = p["w"], p["c"]
    return Item(f'"{w}"[:"{w}".rfind("{c}")]', w[:rfind_in(w, c)], "rfind gives the position of the last match; [:i] keeps what is before it.")


FIND: list[Maker] = [
    S('"$w".find("$c")', lambda p: find_in(p["w"], p["c"]), FIRST),
    S('"$w".find("$q")', "-1", MISS),
    S('"$w".index("$c")', lambda p: find_in(p["w"], p["c"]), "index is find's twin: the first match, from 0."),
    S('"$w".rfind("$c")', lambda p: rfind_in(p["w"], p["c"]), "rfind searches from the right: the last match."),
    S('"$w".count("$c")', lambda p: count_sub(p["w"], p["c"]), "count says how many times it appears."),
    S('"$w".count("$q")', "0", "It never appears, so 0."),
    S('"$w".find("$sub")', lambda p: find_in(p["w"], p["sub"]), "Two letters in a row are found as a unit."),
    S('"$ph".find(" ")', lambda p: len(p["w"]), "The space comes right after the first word, so its position is that word's length."),
    S('"$ph".find("$v")', lambda p: find_in(p["ph"], p["v"]), "The second word starts after the first and the space."),
    S('"$ph".count("$c")', lambda p: count_sub(p["ph"], p["c"]), "Count over both words."),
    S('"$ph".rfind("$c")', lambda p: rfind_in(p["ph"], p["c"]), "The last match in the whole text."),
    S('"$w".find("$c") == -1', "False", "It is found, so find is not -1."),
    S('"$w".find("$q") < 0', "True", "Not found gives -1, which is below 0."),
    S('"$w".find("$c", 1)', lambda p: find_in(p["w"], p["c"], 1), "The second argument is where to start looking."),
    S('"$w".find("$c", 2)', lambda p: find_in(p["w"], p["c"], 2), "Start looking at position 2: earlier matches are skipped."),
    S('"$w".find("$c", $k)', lambda p: find_in(p["w"], p["c"], p["k"]), "Searching begins at that position."),
    S('"$w".find("$c", -2)', lambda p: find_in(p["w"], p["c"], -2), "A negative start counts from the end: -2 begins at the second to last letter."),
    S('"$w".find("$c", 0, 2)', lambda p: find_in(p["w"], p["c"], 0, 2), "The third argument is where to stop: only positions 0 and 1 are searched."),
    S('"aaaa".count("aa")', "2", "count does not overlap matches: aa, then aa."),
    S('"aaa".count("aa")', "1", "After the first aa, only one a is left."),
    S('"banana".count("an")', "2", "ba-an-an-a: two separate an."),
    S('"banana".find("na")', "2", FIRST),
    S('"banana".rfind("na")', "4", "rfind finds the last one."),
    S('"banana".count("a")', "3", "Three a's."),
    S('"$x$x$x$x".count("$x$x")', "2", "Matches do not overlap: two pairs in four."),
    S('"$w".count("")', lambda p: len(p["w"]) + 1, "The empty string matches between every letter and at both ends."),
    S('"$w".find("")', "0", "The empty string is found at once, at position 0."),
    S('"$w".find("$w")', "0", "The whole word is found at the start."),
    S('"$w".find("${w}s")', "-1", "The longer text is not inside the shorter."),
    S('"$w"["$w".find("$c"):]', lambda p: p["w"][find_in(p["w"], p["c"]):], "From the first match to the end."),
    _before,
    S('s = "$ph"\ns[:s.find(" ")]', lambda p: p["w"], "Everything before the first space: the first word."),
    S('s = "$ph"\ns[s.find(" ") + 1:]', lambda p: p["v"], "Everything after the first space: the second word."),
    S('len("$w") - "$w".rfind("$c") - 1', lambda p: len(p["w"]) - rfind_in(p["w"], p["c"]) - 1, "How many letters come after the last match."),
    S('"$w".find("$c") == "$w".rfind("$c")', lambda p: find_in(p["w"], p["c"]) == rfind_in(p["w"], p["c"]), "Equal only when the letter appears just once."),
    S('"$W".find("$z0")', lambda p: find_in(p["W"], p["z0"]), "Searching is case sensitive: f is not F."),
    S('"$w".find("$C")', "-1", "The capital is a different character: not found."),
    S('"$W".lower().count("$c")', lambda p: count_sub(lower(p["W"]), p["c"]), "Lower-case it first, then count."),
    S('"$w".count("$c") + "$v".count("$c")', lambda p: count_sub(p["w"], p["c"]) + count_sub(p["v"], p["c"]), "Add the two counts."),
    S('"$ph3".count(" ") + 1', "3", "Two spaces between three words: spaces + 1 is the number of words."),
    S('"$ph".count(" ")', "1", "One space."),
    S('str($num).count("$dg")', lambda p: count_sub(p["num"], p["dg"]), "str() makes it text, so you can count digits."),
    S('str($num).find("$dg")', lambda p: find_in(p["num"], p["dg"]), "The position of the first such digit."),
    S('"$ph".find("$c") + "$ph".rfind("$c")', lambda p: find_in(p["ph"], p["c"]) + rfind_in(p["ph"], p["c"]), "First position plus last position."),
    S('"$w$v".find("$v")', lambda p: find_in(p["w"] + p["v"], p["v"]), "The second word starts where the first ends."),
    S('"$w$w".count("$w")', lambda p: count_sub(p["w"] + p["w"], p["w"]), "The word appears twice."),
    S('"$w$w".find("$w", 1)', lambda p: find_in(p["w"] + p["w"], p["w"], 1), "Skip the match at 0: the next one starts after the first word."),
    S('"$ph".count("$w")', lambda p: count_sub(p["ph"], p["w"]), "The word is in the text once."),
    S('"$w-$v".find("-")', lambda p: len(p["w"]), "The dash follows the first word."),
]

# ── 4. Replace It ───────────────────────────────────────────────────────

REP = "replace(old, new) swaps every match for the new text."


def _rp(p: dict, old: str, new: str, count: int = -1, text: str = "") -> str:
    return py_replace(text or p["w"], old, new, count)


REPLACE: list[Maker] = [
    S('"$w".replace("$c", "$x")', lambda p: _rp(p, p["c"], p["x"]), REP),
    S('"$w".replace("$c", "")', lambda p: _rp(p, p["c"], ""), "Replacing with the empty string deletes the matches."),
    S('"$w".replace("$c", "-", 1)', lambda p: _rp(p, p["c"], "-", 1), "The third argument limits how many are replaced: just the first."),
    S('"$w".replace("$c", "-", 2)', lambda p: _rp(p, p["c"], "-", 2), "At most two replacements, from the left."),
    S('"$w".replace("$c", "-")', lambda p: _rp(p, p["c"], "-"), REP),
    S('"$w".replace("$c", "-", 0)', lambda p: p["w"], "A count of 0 means replace nothing."),
    S('"$W".replace("$z0", "-")', lambda p: _rp(p, p["z0"], "-", -1, p["W"]), "Case matters: a small letter does not match a capital."),
    S('"$w".replace("$C", "-")', lambda p: p["w"], "The capital never appears, so nothing changes."),
    S('"$w".upper().replace("$C", "-")', lambda p: _rp(p, p["C"], "-", -1, p["WU"]), "upper() first, so the capital does match."),
    S('"$w".replace("$w", "$v")', lambda p: p["v"], "The whole string matches, so it is replaced whole."),
    S('"$ph".replace(" ", "")', lambda p: p["w"] + p["v"], "Deleting the space glues the words."),
    S('"$ph".replace(" ", "_")', lambda p: p["w"] + "_" + p["v"], REP),
    S('"$ph3".replace(" ", "-", 1)', lambda p: _rp(p, " ", "-", 1, p["ph3"]), "Only the first space is replaced."),
    S('"$ph3".replace(" ", "-", 2)', lambda p: _rp(p, " ", "-", 2, p["ph3"]), "Both spaces: the count allows two."),
    S('"$s1,$s2,$s3".replace(",", ", ")', lambda p: join(", ", _l3(p)), "Each comma becomes a comma and a space."),
    S('"aaa".replace("aa", "b")', "ba", "Matches do not overlap: the first aa is replaced, one a is left."),
    S('"aaaa".replace("aa", "b")', "bb", "Two separate pairs."),
    S('"banana".replace("a", "o")', lambda p: py_replace("banana", "a", "o"), REP),
    S('"$w".replace("", "-")', lambda p: _rp(p, "", "-"), "The empty string matches between every letter and at both ends."),
    S('"$w".replace("$c", "X").count("X")', lambda p: count_sub(p["w"], p["c"]), "As many X as there were matches."),
    S('len("$w".replace("$c", ""))', lambda p: len(_rp(p, p["c"], "")), "The word, minus each match."),
    S('len("$w".replace("$c", "--"))', lambda p: len(_rp(p, p["c"], "--")), "Each match grows by one character."),
    S('"$x$y$x".replace("$x", "$y").replace("$y", "$x")', lambda p: py_replace(py_replace(p["x"] + p["y"] + p["x"], p["x"], p["y"]), p["y"], p["x"]),
      "Each replace sees the result of the one before, so this is not a swap."),
    S('s = "$w"\ns.replace("$c", "-")\ns', lambda p: p["w"], STR_NEW),
    S('s = "$w"\ns = s.replace("$c", "-")\ns', lambda p: _rp(p, p["c"], "-"), "s = s.replace(...) keeps the new string."),
    S('"$w".replace("$c", "-", 1).replace("$c", "+", 1)', lambda p: py_replace(py_replace(p["w"], p["c"], "-", 1), p["c"], "+", 1),
      "The first replace takes the first match; the second finds the next one."),
    S('"$a+$b".replace("+", "-")', lambda p: f"{p['a']}-{p['b']}", REP),
    S('str($num).replace("$dg", "0")', lambda p: py_replace(p["num"], p["dg"], "0"), "Every such digit becomes 0."),
    S('"$w".replace("$c", "$q") == "$w"', "False", "The letter was there, so the result is different."),
    S('"$w".replace("$q", "-") == "$w"', "True", "No match, so no change."),
    S('"$w".replace("$sub", "")', lambda p: _rp(p, p["sub"], ""), "The pair is deleted."),
    S('"$w".replace("$c", "$c$c")', lambda p: _rp(p, p["c"], p["c"] * 2), "Each match is doubled."),
    S('"$w".replace("$c", "$c" * 3)', lambda p: _rp(p, p["c"], p["c"] * 3), '"$c" * 3 is worked out first, then used as the new text.'),
    S('"$ph".replace(" ", "")[::-1]', lambda p: reverse_text(p["w"] + p["v"]), "Remove the space, then reverse."),
    S('"$ph".replace("$c", "").replace(" ", "")', lambda p: py_replace(py_replace(p["ph"], p["c"], ""), " ", ""), "Two replaces, one after the other."),
    S('"   $w   ".replace(" ", "")', lambda p: p["w"], "Deleting every space."),
    S('"1,234,567".replace(",", "")', "1234567", "Deleting the commas leaves the digits."),
    S('int("$a,$b".replace(",", "")) + 1', lambda p: int(str(p["a"]) + str(p["b"])) + 1, "Remove the comma, make it a number, add 1."),
    S('"$w".replace("e", "3").replace("o", "0")', lambda p: py_replace(py_replace(p["w"], "e", "3"), "o", "0"), "Two replaces: e first, then o."),
    S('"$w".replace("$c", "-").count("-")', lambda p: count_sub(p["w"], p["c"]), "One dash for each match."),
    S('"$ph".replace("$w", "").strip()', lambda p: strip(py_replace(p["ph"], p["w"], "")), "Remove the first word, then the leftover space with strip()."),
    S('"$w".replace("$c", "-").replace("-", "$c")', lambda p: p["w"], "The dashes go back to the letter: the word as it was."),
    S('"$x$x$x".replace("$x$x", "-")', lambda p: "-" + p["x"], "Only one pair fits; the third letter is left."),
]

# ── 5. Format It ────────────────────────────────────────────────────────

ZPAD = "0 as the fill with a width pads on the left with zeros."
ALIGN = "In a format spec, the fill character comes first, then < (left), > (right) or ^ (centre), then the width."
FIXED = "A .Nf spec rounds to N decimal places."
TIE = "Exactly halfway, Python rounds to the even digit (the way round() does)."


def _dec(p: dict, key: str, places: int) -> str:
    return fixed(p["dw"], p["f" + key[-1]], places)


FORMAT: list[Maker] = [
    S('f"{$a:03d}"', lambda p: zero_pad(str(p["a"]), 3), ZPAD),
    S('n = $n\nf"{n:05d}"', lambda p: zero_pad(str(p["n"]), 5), ZPAD),
    S('f"{$a:*>5}"', lambda p: pad_left(str(p["a"]), 5, "*"), ALIGN),
    S('f"{$a:*<5}"', lambda p: pad_right(str(p["a"]), 5, "*"), ALIGN),
    S('f"{$n:-^8}"', lambda p: pad_middle(str(p["n"]), 8, "-"), "^ centres the value between the fill characters."),
    S('w = "$w"\nf"{w:*<8}"', lambda p: pad_right(p["w"], 8, "*"), ALIGN),
    S('w = "$w"\nf"{w:.>9}"', lambda p: pad_left(p["w"], 9, "."), ALIGN),
    S('w = "$w"\nf"{w:*^10}"', lambda p: pad_middle(p["w"], 10, "*"), "^ centres; when the gap is odd, the extra fill goes on the right."),
    S('f"{$dec2:.1f}"', lambda p: _dec(p, "dec2", 1), FIXED),
    S('f"{$dec3:.2f}"', lambda p: _dec(p, "dec3", 2), FIXED),
    S('f"{$dec1:.0f}"', lambda p: _dec(p, "dec1", 0), "A .0f spec rounds to a whole number."),
    S('f"{$dec3:08.2f}"', lambda p: zero_pad(_dec(p, "dec3", 2), 8), "Width 8 counts the whole text, point included; the 0 fills on the left."),
    S('f"{$dec3:*>9.2f}"', lambda p: pad_left(_dec(p, "dec3", 2), 9, "*"), "Align and width first, then the precision."),
    S('f"{$big:,}"', lambda p: with_commas(p["big"]), "A comma in the spec puts thousands separators in."),
    S('f"{$a:+d}"', lambda p: "+" + str(p["a"]), "+ always shows the sign."),
    S('f"{-$a:+d}"', lambda p: "-" + str(p["a"]), "A negative number shows its minus either way."),
    S('f"{$n:b}"', lambda p: digits_in(p["n"], 2), "b writes the number in binary."),
    S('f"{$n:08b}"', lambda p: zero_pad(digits_in(p["n"], 2), 8), "Binary, padded with zeros to 8 digits."),
    S('f"{$n:x}"', lambda p: digits_in(p["n"], 16), "x writes the number in hexadecimal."),
    S('f"{$n:#x}"', lambda p: "0x" + digits_in(p["n"], 16), "# adds the 0x prefix."),
    S('f"{$n:#b}"', lambda p: "0b" + digits_in(p["n"], 2), "# adds the 0b prefix."),
    S('f"{$n:o}"', lambda p: digits_in(p["n"], 8), "o writes the number in octal (base 8)."),
    S('f"{0.$n:.0%}"', lambda p: f"{p['n']}%", "% multiplies by 100 and adds a percent sign."),
    S('f"{0.0$a:.0%}"', lambda p: f"{p['a']}%", "0.0N is N percent."),
    S('f"{0.$n:.1%}"', lambda p: f"{p['n']}.0%", "One decimal in the percentage."),
    S('w = "$w"\nf"{w!r}"', lambda p: "'" + p["w"] + "'", "!r shows the repr: strings get quotes."),
    S('w = "$w"\nf"{w:.2}"', lambda p: p["w"][:2], "On a string, .N is the most characters to show."),
    S('w = "$w"\nf"{w:.$k}"', lambda p: p["w"][:p["k"]], "On a string, .N cuts it to N characters."),
    S('f"{$a} + {$b} = {$a + $b}"', lambda p: f"{p['a']} + {p['b']} = {p['a'] + p['b']}", "Anything in braces is worked out, so {a + b} is the sum."),
    S('f"{$a}{$b}"', lambda p: str(p["a"]) + str(p["b"]), "Each value becomes text, side by side."),
    S('f"{$a * $b}"', lambda p: str(p["a"] * p["b"]), "The braces hold an expression."),
    S('w = "$w"\nf"{w.upper()}"', lambda p: p["WU"], "You can call a method inside the braces."),
    S('w = "$w"\nf"{w[0]}"', lambda p: p["w"][0], "You can index inside the braces."),
    S('w = "$w"\nf"{w}s"', lambda p: p["w"] + "s", "Text outside the braces is kept as written."),
    S('w = "$w"\nf"{w}-{len(w)}"', lambda p: p["w"] + "-" + str(len(p["w"])), "Each brace is replaced by its value."),
    S('w = "$w"\nf"{{{w}}}"', lambda p: "{" + p["w"] + "}", "{{ and }} give literal braces; the middle pair is the value."),
    S('w = "$w"\nf"{{w}}"', "{w}", "Doubled braces are just braces: nothing is looked up."),
    S('f"{{{$a}}}"', lambda p: "{" + str(p["a"]) + "}", "Literal braces around a value."),
    S('f"{$a:02}:{$b:02}"', lambda p: f"0{p['a']}:0{p['b']}", "A leading 0 and a width: 2 pads each to two digits."),
    S('w = "$w"\nlen(f"{w:>8}")', "8", "The width is the total length of the field."),
    S('w = "$w"\nlen(f"{w:3}")', lambda p: len(p["w"]), "A width is a minimum: a longer text is never cut."),
    S('w = "$w"\nlen(f"{w:10}")', "10", "Shorter text is padded up to the width."),
    S('w = "$w"\nf"{w:<9}|"', lambda p: pad_right(p["w"], 9, " ") + "|", "< pads on the right with spaces up to the width, so the bar lands in column 10."),
    S('w = "$w"\nf"|{w:>9}"', lambda p: "|" + pad_left(p["w"], 9, " "), "> pads on the left with spaces."),
    S('"{}-{}".format("$w", $a)', lambda p: f"{p['w']}-{p['a']}", "Each {} is filled by the next argument, in order."),
    S('"{1} {0}".format("$w", "$v")', lambda p: p["v"] + " " + p["w"], "A number in the braces picks the argument by position."),
    S('"{:03d}".format($a)', lambda p: zero_pad(str(p["a"]), 3), ZPAD),
    S('"{:.2f}".format($dec3)', lambda p: _dec(p, "dec3", 2), FIXED),
    S('"{0}{0}".format("$w")', lambda p: p["w"] * 2, "The same argument can be used twice."),
    S('"{name}".format(name="$w")', lambda p: p["w"], "A name in the braces picks a keyword argument."),
    S('"{:*^9}".format("$w")', lambda p: pad_middle(p["w"], 9, "*"), ALIGN),
    S('"%s=%d" % ("$w", $a)', lambda p: f"{p['w']}={p['a']}", "%s takes text and %d a whole number, in order."),
    S('"%05d" % $a', lambda p: zero_pad(str(p["a"]), 5), "%05d pads with zeros to width 5."),
    S('"%.2f" % $dec3', lambda p: _dec(p, "dec3", 2), "%.2f is two decimal places."),
    S('"%x" % $n', lambda p: digits_in(p["n"], 16), "%x is hexadecimal."),
    S('"%d%%" % $n', lambda p: f"{p['n']}%", "%% is a literal percent sign."),
    S('"%s and %s" % ("$w", "$v")', lambda p: f"{p['w']} and {p['v']}", "Each %s takes the next value."),
    S('"%-9s|" % "$w"', lambda p: pad_right(p["w"], 9, " ") + "|", "A minus left-aligns in the width."),
    S('"%c" % $code', lambda p: p["L"], "%c turns a character code into its character."),
    S('"%r" % "$w"', lambda p: "'" + p["w"] + "'", "%r shows the repr, with quotes."),
    S('"%06.2f" % $dec3', lambda p: zero_pad(_dec(p, "dec3", 2), 6), "Width 6, zero fill, two decimals."),
    S('"$w".ljust(9, "*")', lambda p: pad_right(p["w"], 9, "*"), "ljust pads on the right up to the width."),
    S('"$w".rjust(9, "-")', lambda p: pad_left(p["w"], 9, "-"), "rjust pads on the left."),
    S('"$w".center($cw, "*")', lambda p: "*" * ((p["cw"] - len(p["w"])) // 2) + p["w"] + "*" * ((p["cw"] - len(p["w"])) // 2),
      "center puts the fill equally on both sides."),
    S('str($a).zfill(3)', lambda p: zero_pad(str(p["a"]), 3), "zfill pads with zeros to the width."),
    S('"-$a".zfill(4)', lambda p: zero_pad("-" + str(p["a"]), 4), "zfill keeps the sign in front and puts the zeros after it."),
    S('"$w".zfill(8)', lambda p: zero_pad(p["w"], 8), "zfill pads any string with zeros on the left."),
    S('"$w".ljust(2, "*")', lambda p: p["w"], "The width is smaller than the word: nothing to add."),
    S('str($a).rjust(3, "0")', lambda p: pad_left(str(p["a"]), 3, "0"), "rjust with a 0 fill."),
    S('"$w" + ": " + str($a)', lambda p: p["w"] + ": " + str(p["a"]), "+ joins strings, so the number needs str() first."),
    S('"Total: " + str($a + $b)', lambda p: "Total: " + str(p["a"] + p["b"]), "Add first, then make it text."),
    S('f"{2.5:.0f}"', "2", TIE),
    S('f"{3.5:.0f}"', "4", TIE),
    S('f"{0.5:.0f}"', "0", TIE),
    S('f"{0.25:.1f}"', "0.2", TIE),
    S('f"{0.75:.1f}"', "0.8", TIE),
    S('f"{0.125:.2f}"', "0.12", TIE),
    S('f"{1 / 3:.3f}"', "0.333", "A third is 0.3333..., cut to three places."),
    S('f"{2 / 3:.2f}"', "0.67", "Two thirds is 0.666..., which rounds up."),
]

# ── 6. String Math ──────────────────────────────────────────────────────

VOW = "aeiou"


def _count_vowels(text: str) -> int:
    return sum(1 for ch in text if ch in VOW)


def _max_char(text: str) -> str:
    return sorted_chars(text)[-1]


MATH: list[Maker] = [
    S('len("$w" + "$v")', lambda p: len(p["w"]) + len(p["v"]), "+ joins them, and the length is the sum."),
    S('len("$w" * $k)', lambda p: len(p["w"]) * p["k"], "Repeating k times multiplies the length by k."),
    S('len("$ph")', lambda p: len(p["w"]) + len(p["v"]) + 1, "Both words and the space between."),
    S('len("$w" * 2 + "$v")', lambda p: len(p["w"]) * 2 + len(p["v"]), "* first (two copies), then +."),
    S('len(str($num))', "4", "Four digits, four characters."),
    S('len(str($a * $b))', lambda p: len(str(p["a"] * p["b"])), "Work out the product, then count its digits."),
    S('len("$w"[1:])', lambda p: len(p["w"]) - 1, "[1:] drops the first letter."),
    S('len("$w"[:$k])', lambda p: p["k"], "[:k] keeps the first k letters."),
    S('len(" ")', "1", "A space is a character."),
    S(r'len("\n")', "1", r"\n is a single newline character."),
    S(r'len("a\tb")', "3", r"\t is one character: a tab."),
    S('len("it\'s")', "4", "The backslash is not in the string: it is just how the quote is written."),
    S('len("$ph".replace(" ", ""))', lambda p: len(p["w"]) + len(p["v"]), "Without the space, just the two words."),
    S('len("$ph".split())', "2", "Two words."),
    S('len("$w" * 0)', "0", "Zero copies: the empty string."),
    S('"$w" * 2', lambda p: p["w"] * 2, "* repeats a string."),
    S('"$x" * $a', lambda p: p["x"] * p["a"], "The letter, repeated."),
    S('"-" * $a + ">"', lambda p: "-" * p["a"] + ">", "Repeat first, then add the arrow."),
    S('"=" * $a + "$x"', lambda p: "=" * p["a"] + p["x"], "Repeat, then join."),
    S('"$w" + "$v"', lambda p: p["w"] + p["v"], "+ joins in the order written."),
    S('"$v" + "$w"', lambda p: p["v"] + p["w"], "Order matters when joining text."),
    S('"$w" + str($a)', lambda p: p["w"] + str(p["a"]), "str() makes the number text, then it joins."),
    S('"$w" + str($a + $b)', lambda p: p["w"] + str(p["a"] + p["b"]), "The sum is worked out first."),
    S('"$a" + "$b"', lambda p: str(p["a"]) + str(p["b"]), "Both are text, so + joins them."),
    S('$a + $b', lambda p: p["a"] + p["b"], "Both are numbers, so + adds them."),
    S('"$a" * 2', lambda p: str(p["a"]) * 2, "A string times a number repeats the text."),
    S('"$a" * $b', lambda p: str(p["a"]) * p["b"], "The text, repeated b times."),
    S('str($a) + str($b)', lambda p: str(p["a"]) + str(p["b"]), "Two pieces of text side by side."),
    S('int("$a") + int("$b")', lambda p: p["a"] + p["b"], "int() turns the text into numbers, which add."),
    S('int("$a" + "$b")', lambda p: int(str(p["a"]) + str(p["b"])), "Join the text first, then make it a number."),
    S('"$w" "$v"', lambda p: p["w"] + p["v"], "Two string literals side by side are joined."),
    S('"$w"[0] * $a', lambda p: p["w"][0] * p["a"], "The first letter, repeated."),
    S('"$w"[::-1] + "$w"', lambda p: reverse_text(p["w"]) + p["w"], "The reversed word, then the word."),
    S('"$x" + "$y" * $k', lambda p: p["x"] + p["y"] * p["k"], "* binds tighter than +: only the y repeats."),
    S('("$x" + "$y") * $k', lambda p: (p["x"] + p["y"]) * p["k"], "The brackets go first: the pair repeats."),
    S('("$w" + "$v")[$k]', lambda p: (p["w"] + p["v"])[p["k"]], "Join first, then pick the letter at that position."),
    S('"$w" + "$v"[0]', lambda p: p["w"] + p["v"][0], "Only the first letter of the second word is added."),
    S('sum(1 for ch in "$w" if ch in "aeiou")', lambda p: _count_vowels(p["w"]), "Count the letters that are vowels."),
    S('len("$w") - sum(1 for ch in "$w" if ch in "aeiou")', lambda p: len(p["w"]) - _count_vowels(p["w"]), "The letters that are not vowels."),
    S('sum(1 for ch in "$mix" if ch.isupper())', lambda p: sum(1 for ch in p["mix"] if "A" <= ch <= "Z"), "Count the capital letters."),
    S('sum(ch.isdigit() for ch in "$an")', lambda p: sum(1 for ch in p["an"] if is_digit(ch)), "True counts as 1, so the sum counts the digits."),
    S('"".join(ch for ch in "$an" if ch.isdigit())', lambda p: "".join(ch for ch in p["an"] if is_digit(ch)), "Keep only the digits, in order."),
    S('"".join(ch for ch in "$an" if ch.isalpha())', lambda p: "".join(ch for ch in p["an"] if is_alpha(ch)), "Keep only the letters, in order."),
    S('"".join(ch for ch in "$w" if ch not in "aeiou")', lambda p: "".join(ch for ch in p["w"] if ch not in VOW), "Drop the vowels."),
    S('"".join(ch for ch in "$w" if ch in "aeiou")', lambda p: "".join(ch for ch in p["w"] if ch in VOW), "Keep only the vowels."),
    S('max("$w")', lambda p: _max_char(p["w"]), "max of a string is its latest letter in the alphabet."),
    S('min("$w")', lambda p: sorted_chars(p["w"])[0], "min is the earliest letter in the alphabet."),
    S('sorted("$w")[0]', lambda p: sorted_chars(p["w"])[0], "sorted() orders the letters; [0] is the first."),
    S('sorted("$w")[-1]', lambda p: _max_char(p["w"]), "The last of the sorted letters."),
    S('max("$w", "$v")', lambda p: p["v"] if lex_less(p["w"], p["v"]) else p["w"], "Strings compare letter by letter, like a dictionary."),
    S('min("$w", "$v")', lambda p: p["w"] if lex_less(p["w"], p["v"]) else p["v"], "The one that comes first in the dictionary."),
    S('max("$w", "$v", key=len)', lambda p: p["v"] if len(p["v"]) > len(p["w"]) else p["w"], "key=len compares by length; a tie keeps the first."),
    S('sorted(["$w", "$v", "$u"])[0]', lambda p: isort([p["w"], p["v"], p["u"]])[0], "Sorted like a dictionary: the first one alphabetically."),
    S('len("$w") * $k', lambda p: len(p["w"]) * p["k"], "A number times a number."),
    S('len("$w") + len("$v")', lambda p: len(p["w"]) + len(p["v"]), "The two lengths added."),
    S('"$w".count("$c") * $k', lambda p: count_sub(p["w"], p["c"]) * p["k"], "The count is a number, so * multiplies."),
    S('len(str(2 ** $n))', lambda p: len(str(ipow(2, p["n"]))), "Work out the power, then count its digits."),
    S('sum(int(d) for d in "$num")', lambda p: sum(int(d) for d in p["num"]), "The digits of the number, added up."),
    S('"b" + "a" * 2 + "c"', "baac", "The repeat happens first: aa in the middle."),
]

# ── 7. Char Codes ───────────────────────────────────────────────────────

CODE = "Every character has a number: ord() gives it and chr() turns a number back into a character."
LETTERS = "The letters are in order, so a small letter's code is 97 plus its position from 0, and a capital's is 65 plus it."


def _shift(letter: str, base: int, by: int) -> str:
    return chr_of((ord_of(letter) - base + by) % 26 + base)


CODES: list[Maker] = [
    S('ord("$L")', lambda p: ord_of(p["L"]), CODE),
    S('ord("$LU")', lambda p: ord_of(p["LU"]), "Capitals have codes from 65 (A) to 90 (Z)."),
    S('chr($code)', lambda p: p["L"], CODE),
    S('chr(ord("a") + $a)', lambda p: chr_of(97 + p["a"]), LETTERS),
    S('chr(ord("A") + $a)', lambda p: chr_of(65 + p["a"]), LETTERS),
    S('ord("a")', "97", "A small a has code 97."),
    S('ord("A")', "65", "A capital A has code 65."),
    S('ord("z")', "122", "z is 25 after a: 97 + 25."),
    S('ord("0")', "48", "The digit characters start at 48."),
    S('ord(" ")', "32", "A space is character 32."),
    S('ord("$LU") - ord("$L")', "-32", "A small letter's code is 32 above its capital's, so the difference is -32."),
    S('ord("$L") - ord("a")', lambda p: ord_of(p["L"]) - 97, "The position in the alphabet, counting a as 0."),
    S('ord("$LU") - ord("A")', lambda p: ord_of(p["LU"]) - 65, "A is 0, B is 1..."),
    S('ord("$dg") - ord("0")', lambda p: int(p["dg"]), "The digit characters are in order, so this is the digit's value."),
    S('chr(ord("0") + $a)', lambda p: str(p["a"]), "48 plus a is the digit character for a."),
    S('chr(ord("$L") + 1)', lambda p: chr_of(ord_of(p["L"]) + 1), "The next character in the code table."),
    S('chr(ord("$L") - 32)', lambda p: p["LU"], "A small letter minus 32 is its capital."),
    S('chr(ord("$LU") + 32)', lambda p: p["L"], "A capital plus 32 is its small letter."),
    S('ord("$L") + 1', lambda p: ord_of(p["L"]) + 1, "One more than the code."),
    S('chr((ord("$L") - 97 + $k) % 26 + 97)', lambda p: _shift(p["L"], 97, p["k"]), "A Caesar shift: move k along the alphabet, wrapping round after z."),
    S('chr((ord("$LU") - 65 + $k) % 26 + 65)', lambda p: _shift(p["LU"], 65, p["k"]), "The same shift on a capital: wrap round after Z."),
    S('chr((ord("$L") - 97 - $k) % 26 + 97)', lambda p: _shift(p["L"], 97, -p["k"]), "Shifting back; % keeps the position between 0 and 25, so it wraps to z."),
    S('chr((ord("$L") - ord("a") + $a) % 26 + ord("a"))', lambda p: _shift(p["L"], 97, p["a"]), "Position from a, plus the shift, wrapped with % 26, back to a letter."),
    S('chr((ord("z") - 97 + $k) % 26 + 97)', lambda p: _shift("z", 97, p["k"]), "z shifted forward wraps round to the start of the alphabet."),
    S('"".join(chr(ord(c) + 1) for c in "$w")', lambda p: "".join(chr_of(ord_of(ch) + 1) for ch in p["w"]), "Every letter moves one along: a becomes b."),
    S('"".join(chr(ord(c) - 32) for c in "$w")', lambda p: p["WU"], "Each letter loses 32, which makes it a capital."),
    S('"".join(chr(ord(c) + $k) for c in "$s1")', lambda p: "".join(chr_of(ord_of(ch) + p["k"]) for ch in p["s1"]), "Every letter's code goes up by k."),
    S('sum(ord(c) for c in "$sub")', lambda p: sum(ord_of(ch) for ch in p["sub"]), "Add up the code of each letter."),
    S('[ord(c) for c in "$sub"]', lambda p: [ord_of(ch) for ch in p["sub"]], "A list with each letter's code."),
    S('list(map(ord, "$sub"))', lambda p: [ord_of(ch) for ch in p["sub"]], "map applies ord to every letter."),
    S('ord(max("$w"))', lambda p: ord_of(_max_char(p["w"])), "max picks the latest letter, ord gives its code."),
    S('ord("$w"[0])', lambda p: ord_of(p["w"][0]), "The code of the first letter."),
    S('chr(ord("a") + len("$w"))', lambda p: chr_of(97 + len(p["w"])), "Count that many letters after a."),
    S('ord(chr($code))', lambda p: p["code"], "chr and ord undo each other."),
    S('chr(ord("$L"))', lambda p: p["L"], "ord then chr gets the letter back."),
    S('chr(ord("z") + 1)', "{", "The code table goes on after z: next comes {."),
    S('chr(ord("Z") + 1)', "[", "After Z comes [."),
    S('chr(ord("9") + 1)', ":", "After the digits comes a colon."),
    S('chr(ord("A") - 1)', "@", "Before A comes @."),
    S('chr(ord("a") - 1)', "`", "Before a comes the backtick."),
    S('chr(ord("$L") ^ 32)', lambda p: p["LU"], "XOR with 32 flips the case bit: a small letter becomes a capital."),
    S('hex(ord("$L"))', lambda p: "0x" + digits_in(ord_of(p["L"]), 16), "hex() writes the code in base 16 with a 0x in front."),
    S('chr(0x41 + $a)', lambda p: chr_of(65 + p["a"]), "0x41 is 65, the code of A."),
    S('ord("$y") - ord("$x")', lambda p: ord_of(p["y"]) - ord_of(p["x"]), "The distance between the two letters in the alphabet."),
    S('ord("$x") < ord("$y")', lambda p: ord_of(p["x"]) < ord_of(p["y"]), "A comparison of codes: earlier letters have smaller codes."),
    S('chr(65 + $a) + chr(65 + $b)', lambda p: chr_of(65 + p["a"]) + chr_of(65 + p["b"]), "Two capitals from their positions."),
    S('ord("$L") - 96', lambda p: ord_of(p["L"]) - 96, "96 is just below a, so this counts a as 1."),
    S('chr(96 + $a + $b)', lambda p: chr_of(96 + p["a"] + p["b"]), "96 plus the position: a is 97."),
    S('"".join(chr(ord("a") + i) for i in range($k + 2))', lambda p: "".join(chr_of(97 + i) for i in range(p["k"] + 2)), "The first few letters of the alphabet."),
    S('ord("$mix"[0]) - ord("$w"[0])', lambda p: ord_of(p["mix"][0]) - ord_of(p["w"][0]), "0 if the first letter's case is the same, -32 if it became a capital."),
]

# ── 8. Text Check ───────────────────────────────────────────────────────


def _pal(rng: random.Random) -> Item:
    word = rng.choice(PALINDROMES + tuple(rng.sample(WORDS, 3)))
    return Item(f'"{word}" == "{word}"[::-1]', "yes" if word == reverse_text(word) else "no",
                "A palindrome reads the same backwards: compare it with its reverse.", check=yes_no_py(f'"{word}" == "{word}"[::-1]'))


def _anagram(rng: random.Random) -> Item:
    a, b = rng.choice(PAIRS)
    if rng.random() < 0.5:
        a, b = b, a
    code = f'sorted("{a}") == sorted("{b}")'
    return Item(code, "yes" if sorted_chars(a) == sorted_chars(b) else "no",
                "Anagrams have the same letters: sort both and compare.", check=yes_no_py(code))


def _distinct(text: str) -> bool:
    seen = ""
    for ch in text:
        if ch in seen:
            return False
        seen += ch
    return True


CHECK: list[Maker] = [
    Q('"$w" < "$v"', lambda p: lex_less(p["w"], p["v"]), "Strings compare letter by letter, like a dictionary."),
    Q('"$w" > "$v"', lambda p: lex_less(p["v"], p["w"]), "The one later in the dictionary is greater."),
    Q('"10" < "9"', True, "As text, '1' comes before '9', so '10' is smaller."),
    Q('"10" > "9"', False, "As text, '1' is before '9'."),
    Q('"$n" < "$a"', lambda p: lex_less(str(p["n"]), str(p["a"])), "Text compares first digit first, not by size."),
    Q('"Z" < "a"', True, "Capitals come before small letters in the code table."),
    Q('"a" < "B"', False, "A small a comes after every capital."),
    Q('"$W" < "$w"', True, "The capital is the earlier character, so Farm sorts first."),
    Q('"apple" < "apples"', True, "A prefix is smaller than the longer text."),
    Q('"" < "a"', True, "The empty string is smaller than any text."),
    Q('"b" > "abc"', True, "The first letters decide: b is after a."),
    Q('"abc" < "abd"', True, "The first difference is the third letter: c is before d."),
    Q('"apple" < "Banana"', False, "A capital B is before a small a, so Banana is first."),
    Q('"Zebra" < "apple"', True, "Capitals come before small letters."),
    Q('"apple".lower() < "banana".lower()', True, "With the case removed, a comes before b."),
    Q('int("10") > int("9")', True, "As numbers, ten is more than nine."),
    Q('"a" < "b" < "c"', True, "A chain means a < b and b < c."),
    Q('"B" < "a" < "b"', True, "Capitals first, then a, then b."),
    Q('"$w" + "$v" == "$v" + "$w"', lambda p: p["w"] + p["v"] == p["v"] + p["w"], "Joining in a different order gives a different text."),
    Q('"$w" == "$w".lower()', lambda p: p["w"] == lower(p["w"]), "The word is already in small letters."),
    Q('"$W" == "$w".capitalize()', True, "capitalize() gives the capital first letter."),
    Q('"$w" in "$ph"', True, "The first word is inside the text."),
    Q('"$c" in "$w"', True, "That letter is in the word."),
    Q('"$q" in "$w"', False, "That letter is not in the word."),
    Q('"$sub" in "$ph"', True, "The pair of letters is in the first word."),
    Q('"$v" in "$w"', lambda p: find_in(p["w"], p["v"]) >= 0, "in asks whether the whole text is somewhere inside."),
    Q('"$w".startswith("$z0")', True, "The word begins with its first letter."),
    Q('"$w".startswith("$c")', lambda p: p["w"][0] == p["c"], "Only the first letter counts for startswith."),
    Q('"$w".endswith("$z1")', True, "The word ends with its last letter."),
    Q('"$w".endswith("$c")', lambda p: p["w"][-1] == p["c"], "Only the last letter counts for endswith."),
    Q('"$w".startswith(("$z0", "$q"))', True, "A tuple means any of them: the first matches."),
    Q('"$w".startswith("$v")', lambda p: p["w"][:len(p["v"])] == p["v"], "Does the word begin with the other word?"),
    Q('"$ph".endswith("$v")', True, "The text ends with its second word."),
    Q('"$ph".startswith("$v")', lambda p: p["ph"][:len(p["v"])] == p["v"], "Only the beginning of the text counts: the first word is there, not the second."),
    Q('"$W".startswith("$z0")', False, "A capital F is not a small f: case matters."),
    Q('"$w".startswith("$c", 1)', lambda p: p["w"][1:2] == p["c"], "The second argument is where to start checking: position 1."),
    Q('"$w".endswith("$c", 0, 2)', lambda p: p["w"][1] == p["c"], "Only positions 0 and 1 are looked at, so it ends with the letter at 1."),
    Q('"$w".isalpha()', True, "Only letters."),
    Q('"$mix".isalpha()', True, "Capital or small, they are all letters."),
    Q('"$an".isalpha()', False, "There are digits in it."),
    Q('"$a".isdigit()', True, "One digit character."),
    Q('"$w".isdigit()', False, "Letters are not digits."),
    Q('"$num".isdigit()', True, "Every character is a digit."),
    Q('"-$a".isdigit()', False, "The minus sign is not a digit."),
    Q('"$a.5".isdigit()', False, "The point is not a digit."),
    Q('"$an".isalnum()', True, "Letters and digits are all fine for isalnum."),
    Q('"$ph".isalnum()', False, "The space is neither letter nor digit."),
    Q('"$ph".isalpha()', False, "The space is not a letter."),
    Q('"".isalpha()', False, "The empty string has no letters, so it is False."),
    Q('"".isdigit()', False, "The empty string has no digits: False."),
    Q('" ".isspace()', True, "Only whitespace."),
    Q('"$a$w".isidentifier()', False, "A name cannot start with a digit."),
    Q('"$w$a".isidentifier()', True, "Letters, then digits: a valid name."),
    _pal,
    _anagram,
    Q('sorted("$w") == sorted("$v")', lambda p: sorted_chars(p["w"]) == sorted_chars(p["v"]), "Same letters in some order? Sort and compare."),
    Q('len(set("$w")) == len("$w")', lambda p: _distinct(p["w"]), "A set drops repeats: the same length means no letter repeats."),
    Q('"$w"[0] == "$w"[-1]', lambda p: p["w"][0] == p["w"][-1], "Compare the first and last letters."),
    Q('"$w".count("$c") > 1', lambda p: count_sub(p["w"], p["c"]) > 1, "Does the letter appear more than once?"),
    Q('"$w" * 2 == "$w$w"', True, "Repeating twice is the same as joining twice."),
    Q('"abc" == "abc "', False, "The space makes it a different string."),
    Q('"$w".strip() == "$w"', True, "There was nothing to strip."),
    Q('" $w".strip() == "$w"', True, "strip removes the leading space."),
    Q('"$w".upper() == "$w"', False, "Capitals are different characters."),
    Q('"$W".lower() == "$w"', True, "lower() gives back the small word."),
    Q('"$w" != "$v"', True, "Different words."),
    Q('"$a" == $a', False, "Python never converts: text is not a number."),
    Q('str($a) == "$a"', True, "str() makes the same text."),
    Q('"$w".find("$c") >= 0', True, "The letter is found."),
]
