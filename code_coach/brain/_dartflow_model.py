"""Hand models for the Dart flow pack (Try Order, Which Exception, Promote Or Not, Await Order, Future Result,
Stream Sum, Control Flow, Error Message).

Nothing here asks Dart anything: the exception family tree is spelled out below, a "template" is a function of
random parameters, and `F` builds one from a prompt text and a hand-worked answer. tests/dart_oracle.py then runs
every item through the real `dart` (the oracle rule), so a wrong model is a failing test.

The extra holes `F` can fill beyond `_dart_model.P`: whatever `pre(p, rng)` puts in the parameter dict.
"""

from __future__ import annotations

import random
from string import Template
from typing import Any, Callable

from ._dart_model import P, show
from ._model import Maker
from .items import Item

# ── The exception family tree (dart:core) ───────────────────────────────

#: class -> everything it is, itself included (what an `on X` clause matches). Object is everything.
IS_A: dict[str, tuple[str, ...]] = {
    "FormatException": ("FormatException", "Exception", "Object"),
    "Exception": ("Exception", "Object"),
    "StateError": ("StateError", "Error", "Object"),
    "ArgumentError": ("ArgumentError", "Error", "Object"),
    "RangeError": ("RangeError", "ArgumentError", "Error", "Object"),
    "UnsupportedError": ("UnsupportedError", "Error", "Object"),
    "ConcurrentModificationError": ("ConcurrentModificationError", "Error", "Object"),
    "NoSuchMethodError": ("NoSuchMethodError", "Error", "Object"),
    "TypeError": ("TypeError", "Error", "Object"),
    "UnimplementedError": ("UnimplementedError", "UnsupportedError", "Error", "Object"),
    "IntegerDivisionByZeroException": ("IntegerDivisionByZeroException", "Exception", "Object"),
    "String": ("String", "Object"),
    "int": ("int", "num", "Object"),
    # user classes (declared in the template)
    "MyError": ("MyError", "Exception", "Object"),
    "BigError": ("BigError", "MyError", "Exception", "Object"),
}


def catches(thrown: str, clause: str) -> bool:
    """Does `on <clause>` catch a thrown value of class `thrown`? (`catch (e)` is `on Object`.)"""
    return clause in IS_A[thrown]


def first_clause(thrown: str, clauses: list[str]) -> int:
    """Index of the first `on` clause that catches `thrown`, or -1 (the exception goes on up)."""
    for i, c in enumerate(clauses):
        if catches(thrown, c):
            return i
    return -1


#: (Dart code that throws, its class). `$m` is a word; the values are all one-line expressions.
THROWS: list[tuple[str, str]] = [
    ("throw FormatException('$m')", "FormatException"),
    ("throw StateError('$m')", "StateError"),
    ("throw ArgumentError('$m')", "ArgumentError"),
    ("throw RangeError('$m')", "RangeError"),
    ("throw UnsupportedError('$m')", "UnsupportedError"),
    ("throw Exception('$m')", "Exception"),
    ("throw '$m'", "String"),
    ("throw $a", "int"),
]


def pick_throw(p: dict, rng: random.Random, key: str = "t", pool: list[tuple[str, str]] | None = None) -> None:
    """Fill p[key] with throwing code and p[key + 'c'] with its class (and p['m'], p['a'] it may use)."""
    p.setdefault("m", p["w"])
    code, cls = rng.choice(pool or THROWS)
    p[key] = Template(code).substitute(p)
    p[key + "c"] = cls


# ── Templates ───────────────────────────────────────────────────────────

def _join_statements(lines: list[str]) -> bool:
    """Put a `case x:` and its statement, or two neighbouring plain statements of the same indent, on one line
    (the last resort of `fit`)."""
    for i in range(len(lines) - 1):
        a, b = lines[i], lines[i + 1]
        if a.strip().startswith(("case ", "default:")) and a.rstrip().endswith(":") and b.rstrip().endswith(";") and "{" not in b and not b.strip().startswith(("case ", "default:")):
            lines[i:i + 2] = [a.rstrip() + " " + b.strip()]
            return True
    for i in range(len(lines) - 1):
        a, b = lines[i], lines[i + 1]
        plain = all(x.rstrip().endswith(";") and "{" not in x and "}" not in x for x in (a, b))
        if plain and len(a) - len(a.lstrip()) == len(b) - len(b.lstrip()) and not a.lstrip().startswith(("import", "print")):
            lines[i:i + 2] = [a.rstrip() + " " + b.strip()]
            return True
    return False


def fit(code: str, max_lines: int = 10, max_chars: int = 220) -> str:
    """Squeeze a prompt into the shape tests' limits (10 lines, 220 characters) by putting small blocks on one line:
    `{`, up to three plain statements, then a closing `}` become one line, the biggest block (then the shortest) first.
    The program means the same; only its layout changes."""
    lines = code.split("\n")
    while len(lines) > max_lines or len("\n".join(lines)) > max_chars:
        best = None
        for i, head in enumerate(lines):
            if not head.rstrip().endswith("{"):
                continue
            for n in (1, 2, 3):
                mid, close = lines[i + 1:i + 1 + n], lines[i + 1 + n:i + 2 + n]
                if len(mid) != n or not (mid[-1].rstrip().endswith(";") and "{" not in mid[-1] and "}" not in mid[-1]):
                    break
                if not close or close[0].strip() not in ("}", "});", "};"):
                    continue
                merged = head.rstrip() + " " + " ".join(m.strip() for m in mid) + " " + close[0].lstrip()
                if best is None or (-n, len(merged)) < best[0]:
                    best = ((-n, len(merged)), i, n, merged)
        if best is None:
            if len(lines) <= max_lines or not _join_statements(lines):
                break
            continue
        _, i, n, merged = best
        lines[i:i + n + 2] = [merged]
    return "\n".join(lines)


def F(fmt: str, solve: Callable[[dict], Any], why: str | Callable[[dict], str] = "", pre: Callable | None = None,
      check: str | None = None) -> Maker:
    """A template: `fmt` is the prompt (a string.Template over the holes of `_dart_model.P` plus whatever `pre`
    adds), `solve(p)` the hand-worked answer (shown the way Dart's print shows it), `why` the explanation.
    A template whose prompt differs from the program the oracle runs passes `check` (the same holes)."""
    def make(rng: random.Random) -> Item:
        p = P(rng)
        if pre:
            pre(p, rng)
        prompt = fit(Template(fmt).substitute(p))
        answer = show(solve(p))
        text = why(p) if callable(why) else Template(why).safe_substitute(p)
        return Item(prompt, answer, text, check=Template(check).substitute(p) if check else "")
    make.__name__ = "f_" + fmt[:24].replace("\n", " ")
    return make


def letters(p: dict, order: list) -> str:
    """The glued answer for a letters template: 1-5 mean p['s1']..p['s5'], a string goes in as it is."""
    return "".join(x if isinstance(x, str) else p[f"s{x}"] for x in order)


def L(fmt: str, order: list | Callable[[dict], list], why: str | Callable[[dict], str], pre: Callable | None = None) -> Maker:
    """A letters template (oracle `lines`): the answer is the printed letters in order, typed together.
    `order` lists what is printed: numbers 1-5 for $s1..$s5, or literal strings (a printed digit or word)."""
    return F(fmt, lambda p: letters(p, order(p) if callable(order) else order), why, pre)
