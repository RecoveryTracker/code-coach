"""Hand models and template helpers for the Dart data pack (`pack_dartdata.py`).

Everything here is plain Python that spells out what Dart does - `%` is never negative, `~/` cuts toward zero,
`round()` goes away from zero, an `int` wraps at 64 bits, `toRadixString` is lower-case - so that no answer is ever
asked of a runtime; tests/dart_oracle.py then holds every item to the real `dart`.

Two ways to write a template:

* `_dart_model.D(fmt, answer, why)` for a prompt with the usual holes (`$a $b $c $d` ints 2-9, `$n`, `$w $v` ...);
  `V("a", "b")` is a handy answer: the list of those holes.
* `R(fn)` for a template that wants its own random lists: `fn(rng)` returns `(prompt, answer, why)`; the prompt is
  written as real Dart (a `$` in it is Dart's own), the answer is shown the way `print` shows it.
"""

from __future__ import annotations

import math
import random
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Callable

from ._dart_model import DIter, DSet, dceil, dfloor, dround, lit, show  # noqa: F401  (re-exported for the templates)
from ._model import WORDS, Maker
from .items import Item

INT_MAX = 2**63 - 1
INT_MIN = -(2**63)


def R(fn: Callable[[random.Random], tuple]) -> Maker:
    """A template from `fn(rng) -> (prompt, answer, why[, check])`; the answer is shown as Dart's print shows it."""
    def make(rng: random.Random) -> Item:
        out = fn(rng)
        prompt, ans, why = out[0], out[1], out[2]
        return Item(prompt, show(ans), why, check=out[3] if len(out) > 3 else "")
    make.__name__ = "r_" + fn.__name__
    return make


def V(*keys: str) -> Callable[[dict], list]:
    """An answer for `D`: the list of the named holes."""
    return lambda p: [p[k] for k in keys]


def N(key: str, f: Callable[[int], Any]) -> Callable[[dict], Any]:
    """An answer for `D`: f applied to one hole."""
    return lambda p: f(p[key])


# ── Random data ─────────────────────────────────────────────────────────

def ints(r: random.Random, n: int, lo: int = 1, hi: int = 30) -> list[int]:
    """n different ints between lo and hi."""
    return r.sample(range(lo, hi + 1), n)


def words(r: random.Random, n: int) -> list[str]:
    return r.sample(WORDS, n)


def distinct_length_words(r: random.Random, n: int) -> list[str]:
    """n words of n different lengths (3 to 7), in a random order: a sort by length has no ties."""
    by_len = {3: ["key"], 4: ["farm", "loop", "code", "grid", "tree", "seed", "corn", "barn", "lamp"],
              5: ["drone", "array", "wheat", "field", "stone", "river", "cloud", "brick", "robot", "maple"],
              6: ["carrot"], 7: ["pumpkin"]}
    lengths = r.sample(sorted(by_len), n)
    out = [r.choice(by_len[k]) for k in lengths]
    r.shuffle(out)
    return out


# ── Numbers ─────────────────────────────────────────────────────────────

def wrap64(n: int) -> int:
    """A Dart VM int: two's complement, 64 bits."""
    n &= 2**64 - 1
    return n - 2**64 if n >= 2**63 else n


def trunc(x: float) -> int:
    """num.truncate() / toInt(): cut toward zero."""
    return int(x)


def sign(x: int | float) -> int:
    return (x > 0) - (x < 0)


def dfmod(x: float, y: float) -> float:
    """Dart's double a % b: like the int one, the result is never negative."""
    r = math.fmod(x, y)
    return r + abs(y) if r < 0 else r


def to_radix(n: int, radix: int) -> str:
    """n.toRadixString(radix): lower-case digits."""
    assert n >= 0
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while True:
        out = digits[n % radix] + out
        n //= radix
        if n == 0:
            return out


def _decimal_digits(x: float | int, digits: int) -> tuple[str, int]:
    """x rounded (half up, on its exact value) to `digits` significant digits: (the digit string, the exponent of
    the first one)."""
    d = Decimal(x)
    exp = d.adjusted()
    q = Decimal(1).scaleb(exp - digits + 1)
    rounded = d.quantize(q, rounding=ROUND_HALF_UP)
    if rounded.adjusted() != exp:  # 9.996 -> 10.00: the model is not meant for these
        raise AssertionError("keep the value away from a rounding carry")
    return str(abs(rounded.scaleb(-exp + digits - 1).to_integral_value())), exp


def to_exponential(x: float | int, digits: int) -> str:
    """x.toStringAsExponential(digits) for digits >= 1 and x > 0: `1.2e+4`."""
    ds, exp = _decimal_digits(x, digits + 1)
    return f"{ds[0]}.{ds[1:]}e{'+' if exp >= 0 else '-'}{abs(exp)}"


def to_precision(x: float | int, digits: int) -> str:
    """x.toStringAsPrecision(digits) for 0 <= exponent < digits (so it never switches to e-notation)."""
    ds, exp = _decimal_digits(x, digits)
    assert 0 <= exp < digits, "this model covers the fixed notation only"
    return ds[:exp + 1] + ("." + ds[exp + 1:] if exp + 1 < digits else "")


def rec(*parts: Any) -> str:
    """How print shows a record of two or more positional fields: (1, a, true)."""
    assert len(parts) >= 2
    return "(" + ", ".join(show(x) for x in parts) + ")"


def lazy(items) -> DIter:
    return DIter(items)
