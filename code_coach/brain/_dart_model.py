"""Hand-built models of what Dart does, for the Dart packs (the sibling of `_model.py`, which stays as it is).

Nothing here asks a runtime anything: a Dart `int` is a Python int, a Dart `double` is a Python float, and the
rules that differ - `/` always makes a double, `~/` cuts toward zero, `%` is never negative, a list prints as
`[1, 2, 3]` with its strings BARE, a map as `{a: 1}`, a set as `{1, 2}` - are spelled out. tests/dart_oracle.py
then runs every item through the real `dart` (the oracle rule), so a wrong model is a failing test.

Values: ints, floats, bools, `None` (Dart's null), str, list, `DSet` (a Dart set: insertion-ordered), `DIter` (a
lazy Iterable such as `xs.map(...)` before `.toList()`: it prints in PARENTHESES) and dict (a Dart map:
insertion-ordered). `show(v)` prints a value as Dart's `print` does.

`D(fmt, answer, why)` builds a template (like `_model.row`): `fmt` is a string.Template with the holes of `P()`
($a $b $c $d $n $w $v $k $x and a few more), `answer` the hand-worked value (shown with `show`), `why` the
sentence of explanation. Templates of the activities that need their own random choices are plain functions
`(rng) -> Item`.

THE ITEM CONVENTION (what the oracle and "Run it" run - the same rule in `dart_oracle.dart_parts` and in
`runnableFor` of web/src/lib/brainRound.ts):

* the program is `item.check`, or the prompt when `check` is empty;
* if it mentions `main(` it is a COMPLETE program (declarations, classes, `void main() => print(...)`), run as is;
* otherwise it is the BODY of `main`: its last line, when it is a bare expression (it does not start with `print(`
  and does not end in `;` or `}`), is printed with `print(...)`; a last line that is a statement runs as it is.
  Local functions are fine in a body; classes and `await` need a complete program (`Future<void> main() async`).
"""

from __future__ import annotations

import random
from decimal import ROUND_HALF_UP, Decimal
from string import Template
from typing import Any, Callable

from ._model import WORDS, Maker, decimal_div, tdiv, tmod
from .items import Item

NULL = None


class DSet(list):
    """A Dart `Set`: a list of distinct items in the order they were added (Dart's default set keeps it)."""

    def __init__(self, items=()):
        super().__init__()
        for x in items:
            self.add(x)

    def add(self, x) -> bool:
        if x in self:
            return False
        self.append(x)
        return True


class DIter(list):
    """A Dart Iterable that is not a List (map(), where(), take(), skip(), keys...): `print` writes `(1, 2, 3)`."""


# ── Numbers ─────────────────────────────────────────────────────────────

def dmod(a: int, b: int) -> int:
    """Dart's int a % b: never negative (it is the Euclidean remainder), whatever the signs."""
    r = tmod(a, b)
    return r + abs(b) if r < 0 else r


def tdiv_(a: int, b: int) -> int:
    """Dart's a ~/ b: cut toward zero."""
    return tdiv(a, b)


def ddiv(a: int, b: int) -> str:
    """How Dart prints a / b for ints whose quotient terminates: always a double, so `6 / 3` is `2.0`."""
    s = decimal_div(a, b)
    return s if "." in s else s + ".0"


def dstr(x: float) -> str:
    """double.toString for ordinary magnitudes: `2.0`, `2.5`, `0.30000000000000004` (never an exponent)."""
    assert x == x and abs(x) != float("inf"), "keep NaN and infinity out of the model"
    assert x == 0 or 1e-4 <= abs(x) < 1e15, "outside the range where Dart and Python print a double alike"
    if x == int(x):
        return f"{int(x)}.0"
    return repr(x)


def fixed(x: float | int, digits: int) -> str:
    """x.toStringAsFixed(digits): the exact value of the double, rounded half away from zero."""
    q = Decimal(1).scaleb(-digits)
    out = format(Decimal(x).quantize(q, rounding=ROUND_HALF_UP), "f")
    return "0" + out[1:] if out.startswith(".") else out


def dround(x: float) -> int:
    """num.round(): halves round away from zero (Python's round() goes to the even one)."""
    return int(Decimal(x).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def dfloor(x: float) -> int:
    n = int(x)
    return n - 1 if x < 0 and n != x else n


def dceil(x: float) -> int:
    n = int(x)
    return n + 1 if x > 0 and n != x else n


# ── Printing ────────────────────────────────────────────────────────────

def show(v: Any) -> str:
    """What `print(v)` writes. Strings are bare everywhere, even inside a list or a map."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return dstr(v)
    if isinstance(v, str):
        return v
    if isinstance(v, DSet):
        return "{" + ", ".join(show(x) for x in v) + "}"
    if isinstance(v, DIter):
        return "(" + ", ".join(show(x) for x in v) + ")"
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(show(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{show(k)}: {show(x)}" for k, x in v.items()) + "}"
    return str(v)


def lit(v: Any) -> str:
    """Dart source for a value: strings in single quotes, lists `[1, 2]`, maps `{'a': 1}`, sets `{1, 2}`, null."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return dstr(v)
    if isinstance(v, str):
        return "'" + v + "'"
    if isinstance(v, DSet):
        return "{" + ", ".join(lit(x) for x in v) + "}"
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(lit(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{lit(k)}: {lit(x)}" for k, x in v.items()) + "}"
    return str(v)


# ── Strings (UTF-16 code units; every model string here is ASCII) ───────

def pad_left(s: str, width: int, fill: str = " ") -> str:
    """s.padLeft(width, fill) for a one-character fill."""
    assert len(fill) == 1, "keep the fill to one character"
    return fill * max(0, width - len(s)) + s


def pad_right(s: str, width: int, fill: str = " ") -> str:
    assert len(fill) == 1, "keep the fill to one character"
    return s + fill * max(0, width - len(s))


def dart_split(s: str, sep: str) -> list[str]:
    """s.split(sep): an empty separator gives the letters; otherwise every separator cuts (empty pieces stay)."""
    if sep == "":
        return list(s)
    out, cur, i = [], "", 0
    while i < len(s):
        if s.startswith(sep, i):
            out.append(cur)
            cur = ""
            i += len(sep)
        else:
            cur += s[i]
            i += 1
    out.append(cur)
    return out


def index_of(hay, needle, start: int = 0) -> int:
    """indexOf for a String (a run of characters) or a list; -1 when absent."""
    if isinstance(hay, str):
        for i in range(start, len(hay) - len(needle) + 1):
            if hay[i:i + len(needle)] == needle:
                return i
        return -1
    for i in range(start, len(hay)):
        if hay[i] == needle:
            return i
    return -1


def last_index_of(hay: str, needle: str) -> int:
    for i in range(len(hay) - len(needle), -1, -1):
        if hay[i:i + len(needle)] == needle:
            return i
    return -1


def replace_all(s: str, old: str, new: str) -> str:
    return new.join(dart_split(s, old)) if old else s


def replace_first(s: str, old: str, new: str) -> str:
    i = index_of(s, old)
    return s if i < 0 else s[:i] + new + s[i + len(old):]


def to_upper(s: str) -> str:
    return "".join(chr(ord(c) - 32) if "a" <= c <= "z" else c for c in s)


def to_lower(s: str) -> str:
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in s)


def capitalise(s: str) -> str:
    return to_upper(s[:1]) + s[1:]


# ── Parameters and templates ────────────────────────────────────────────

def P(rng: random.Random) -> dict[str, Any]:
    """Holes a template can use: $a $b $c $d (different ints 2-9), $n (10-40), $w $v (different words),
    $k (1-3), $x (a single lowercase letter), $W (the word $w capitalised), $L ($w's length), $h (2, 4, 5 or 8:
    a divisor that always gives a terminating decimal), $s1..$s5 (five different capital letters), $y (a letter
    of $w), $f and $e (the first and last letter of $w) and $z (a letter of $v)."""
    a, b, c, d = rng.sample(range(2, 10), 4)
    w, v = rng.sample(WORDS, 2)
    s1, s2, s3, s4, s5 = rng.sample("ABCDEFGHJKMNPQRSTWXYZ", 5)
    return {"a": a, "b": b, "c": c, "d": d, "n": rng.randint(10, 40), "w": w, "v": v,
            "k": rng.randint(1, 3), "x": rng.choice("abcdefgh"), "W": capitalise(w), "L": len(w),
            "h": rng.choice((2, 4, 5, 8)), "s1": s1, "s2": s2, "s3": s3, "s4": s4, "s5": s5,
            "y": rng.choice(w), "f": w[0], "e": w[-1], "z": rng.choice(v)}


def D(fmt: str, ans: Any, why: str | Callable[[dict], str] = "", check: Callable[[str], str] | str | None = None) -> Maker:
    """A Dart template: `fmt` the prompt (a string.Template over `P`), `ans` the hand-worked value (or a function
    of the parameters; shown as Dart's print shows it), `why` the explanation, `check` an optional oracle program
    (a function of the prompt, or text with the same holes)."""
    def make(rng: random.Random) -> Item:
        p = P(rng)
        prompt = Template(fmt).substitute(p)
        value = ans(p) if callable(ans) else ans
        why_text = why(p) if callable(why) else Template(why).safe_substitute(p)
        if callable(check):
            program = check(prompt)
        elif isinstance(check, str):
            program = Template(check).substitute(p)
        else:
            program = ""
        return Item(prompt, show(value), why_text, check=program)
    make.__name__ = "d_" + fmt[:24].replace("\n", " ")
    return make


def YN(fmt: str, truth: bool | Callable[[dict], bool], why: str | Callable[[dict], str] = "") -> Maker:
    """A yes/no template (the oracle prints "yes" or "no" for the prompt's last line)."""
    return D(fmt, lambda p: "yes" if (truth(p) if callable(truth) else truth) else "no", why, check=yes_no_dart)


def FE(fmt: str, errors: bool | Callable[[dict], bool], why: str | Callable[[dict], str] = "") -> Maker:
    """A fine/error template: the snippet as shown either compiles and runs quietly ("fine") or does not ("error":
    a compile error or an exception). The activity's `oracle` is "error" (see the module docstring)."""
    return D(fmt, lambda p: "error" if (errors(p) if callable(errors) else errors) else "fine", why)


def yes_no_dart(code: str) -> str:
    """A body that prints "yes"/"no" for the last line of `code` (an expression)."""
    head, _, last = code.rpartition("\n")
    last = last.strip().rstrip(";")
    return (head + "\n" if head else "") + f"print(({last}) ? 'yes' : 'no');"


def program(*lines: str) -> str:
    """Lines joined into a prompt."""
    return "\n".join(lines)


def ints(rng: random.Random, n: int, lo: int = 1, hi: int = 9) -> list[int]:
    return rng.sample(range(lo, hi + 1), n)
