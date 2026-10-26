"""Hand-built models of what C does, for the C packs (the sibling of `_model.py` and `_dart_model.py`).

Nothing here asks a runtime anything: integer promotion, the usual arithmetic conversions, wraparound of the fixed-width
types, `/` and `%` that cut toward zero, shifts and bit operations, and `printf`'s formats are all spelled out in Python.
tests/c_oracle.py then compiles every item with the real compilers (clang, and MSVC where installed) in more than one
way - `-O0` signed `char`, `-O2` unsigned `char`, MSVC `/Od` - and they must all print what the model says, so a wrong
model, or a program whose answer depends on the machine, is a failing test (the oracle rule).

PORTABLE C ONLY (the rules the Gotchas C cards follow, enforced by `tests/c_oracle.lint` and the sanitizer run):
nothing undefined (no signed overflow, no out-of-bounds, no unsequenced modification such as `x++ + x`, no shift by too
much, no `%d` for an `unsigned`...), nothing implementation-defined that differs between our compilers (plain `char`
holding 128+, right shift of a negative, `sizeof(long)`, `%p`, string-literal identity...), nothing random or timed.
`int` is 32 bits, `long long` 64, `char` 8 - true for every compiler here. The execution character set is ASCII.

THE ITEM CONVENTION (the same rule in `tests/c_oracle.full_program` and `cProgram` of web/src/lib/brainRound.ts):

* `stdio.h`, `stdint.h`, `string.h` and `stddef.h` are always included - an item never writes `#include`;
* the program is `item.check`, or the prompt when `check` is empty;
* if it mentions `main(` it is a COMPLETE program: globals and helper functions, then `int main(void) {...}`; otherwise
  it is the BODY of `main` (statements, which may declare locals and `static` locals);
* the program PRINTS ITS OWN ANSWER with `printf`, and the answer is its output with the whitespace at both ends cut
  off - so one starts and ends with a visible character (`|  42|`, not `  42`) and fits on one line;
* two items in one batch may declare the same function or global (the oracle makes each file-level name `static` and
  compiles each complete program on its own).

`C(fmt, ans, why)` builds a template (like `_model.row` and `_dart_model.D`): `fmt` is a string.Template over `P()`'s holes
- WRITE C IN A RAW STRING (`r'printf("%d\\n", $a);'`) so the backslashes stay - `ans` the hand-worked value (a function of
the parameters, or a value) shown with `show`, `why` one sentence (never a `$`). A model function may `raise Retry` to
make the template pick new parameters (a rounding tie, a value out of range).
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from string import Template
from typing import Any, Callable

from ._model import WORDS, Maker, tdiv, tmod
from .items import Item


class Retry(Exception):
    """A template's parameters do not suit it (a rounding tie, a value out of range): pick again."""


# ── The integer types ───────────────────────────────────────────────────

@dataclass(frozen=True)
class CType:
    name: str
    bits: int
    signed: bool

    @property
    def lo(self) -> int:
        return -(1 << (self.bits - 1)) if self.signed else 0

    @property
    def hi(self) -> int:
        return (1 << (self.bits - 1)) - 1 if self.signed else (1 << self.bits) - 1


I8, U8 = CType("int8_t", 8, True), CType("uint8_t", 8, False)
I16, U16 = CType("int16_t", 16, True), CType("uint16_t", 16, False)
I32, U32 = CType("int32_t", 32, True), CType("uint32_t", 32, False)
I64, U64 = CType("int64_t", 64, True), CType("uint64_t", 64, False)
INT, UINT = CType("int", 32, True), CType("unsigned", 32, False)
LLONG = CType("long long", 64, True)

#: sizeof of what is the same on every machine here.
SIZEOF = {"char": 1, "int8_t": 1, "uint8_t": 1, "int16_t": 2, "uint16_t": 2, "int32_t": 4, "uint32_t": 4,
          "int64_t": 8, "uint64_t": 8, "int": 4, "unsigned": 4, "float": 4, "double": 8, "long long": 8}


def wrap(v: int, t: CType) -> int:
    """v converted to an UNSIGNED type: modulo 2**bits (always defined). For a signed type the value must fit (what
    happens otherwise is implementation-defined, so no item does it)."""
    if t.signed:
        assert t.lo <= v <= t.hi, f"{v} does not fit {t.name}"
        return v
    return v % (1 << t.bits)


def promote(t: CType) -> CType:
    """The integer promotions: anything narrower than int becomes int."""
    return INT if t.bits < 32 else t


def common(a: CType, b: CType) -> CType:
    """The usual arithmetic conversions of two (already promoted) integer types."""
    a, b = promote(a), promote(b)
    if a.signed == b.signed:
        return a if a.bits >= b.bits else b
    s, u = (a, b) if a.signed else (b, a)
    if u.bits >= s.bits:
        return u
    return s  # the signed one is wider, so it holds every value of the unsigned one


@dataclass(frozen=True)
class V:
    """A value with its C type (after the integer promotions the type is at least int)."""
    v: int
    t: CType = INT


def lit(v: int, t: CType = INT) -> V:
    return V(wrap(v, t), t)


def cast(x: V, t: CType) -> V:
    return V(wrap(x.v, t), t)


def _arith(op: str, a: V, b: V) -> V:
    t = common(a.t, b.t)
    x, y = wrap(a.v, t), wrap(b.v, t)  # both converted to the common type
    if op == "+":
        r = x + y
    elif op == "-":
        r = x - y
    elif op == "*":
        r = x * y
    elif op == "/":
        assert y != 0, "division by zero"
        r = tdiv(x, y)
    elif op == "%":
        assert y != 0, "division by zero"
        r = tmod(x, y)
    elif op == "&":
        r = (x & y)
    elif op == "|":
        r = (x | y)
    elif op == "^":
        r = (x ^ y)
    else:
        raise ValueError(op)
    if t.signed:
        assert t.lo <= r <= t.hi, f"signed overflow in {x} {op} {y} ({t.name}): undefined behaviour"
        return V(r, t)
    return V(r % (1 << t.bits), t)


def add(a: V, b: V) -> V: return _arith("+", a, b)
def sub(a: V, b: V) -> V: return _arith("-", a, b)
def mul(a: V, b: V) -> V: return _arith("*", a, b)
def div(a: V, b: V) -> V: return _arith("/", a, b)
def mod(a: V, b: V) -> V: return _arith("%", a, b)


def band(a: V, b: V) -> V:
    """& on two's complement: a negative signed operand is converted with the other to the common type."""
    t = common(a.t, b.t)
    x, y = a.v % (1 << t.bits), b.v % (1 << t.bits)
    return _signed_back(x & y, t)


def bor(a: V, b: V) -> V:
    t = common(a.t, b.t)
    return _signed_back((a.v % (1 << t.bits)) | (b.v % (1 << t.bits)), t)


def bxor(a: V, b: V) -> V:
    t = common(a.t, b.t)
    return _signed_back((a.v % (1 << t.bits)) ^ (b.v % (1 << t.bits)), t)


def _signed_back(bits: int, t: CType) -> V:
    """A bit pattern read as type t."""
    if t.signed and bits >= 1 << (t.bits - 1):
        bits -= 1 << t.bits
    return V(bits, t)


def inv(a: V) -> V:
    """~a: the promoted type's bits flipped (so ~(uint8_t)5 is the int -6)."""
    t = promote(a.t)
    return _signed_back((~a.v) % (1 << t.bits), t)


def neg(a: V) -> V:
    t = promote(a.t)
    if t.signed:
        assert a.v != t.lo, "negating the smallest int is undefined"
        return V(-a.v, t)
    return V((-a.v) % (1 << t.bits), t)


def shl(a: V, n: int) -> V:
    t = promote(a.t)
    assert 0 <= n < t.bits, "shift count out of range: undefined"
    r = a.v << n
    if t.signed:
        assert a.v >= 0 and r <= t.hi, "left shift into the sign bit or of a negative: undefined"
        return V(r, t)
    return V(r % (1 << t.bits), t)


def shr(a: V, n: int) -> V:
    t = promote(a.t)
    assert 0 <= n < t.bits, "shift count out of range: undefined"
    assert a.v >= 0, "right shift of a negative is implementation-defined"
    return V(a.v >> n, t)


def _cmp(op: str, a: V, b: V) -> V:
    t = common(a.t, b.t)
    x, y = wrap(a.v, t) if not t.signed else a.v, wrap(b.v, t) if not t.signed else b.v
    r = {"<": x < y, ">": x > y, "<=": x <= y, ">=": x >= y, "==": x == y, "!=": x != y}[op]
    return V(1 if r else 0, INT)


def lt(a: V, b: V) -> V: return _cmp("<", a, b)
def gt(a: V, b: V) -> V: return _cmp(">", a, b)
def le(a: V, b: V) -> V: return _cmp("<=", a, b)
def ge(a: V, b: V) -> V: return _cmp(">=", a, b)
def eq(a: V, b: V) -> V: return _cmp("==", a, b)
def ne(a: V, b: V) -> V: return _cmp("!=", a, b)


def popcount(x: int) -> int:
    n = 0
    while x:
        n += x & 1
        x >>= 1
    return n


# ── Strings ─────────────────────────────────────────────────────────────

def c_strlen(s: str) -> int:
    """strlen: the characters before the first NUL."""
    n = 0
    while n < len(s) and s[n] != "\0":
        n += 1
    return n


def strcmp_sign(a: str, b: str) -> int:
    """The SIGN of strcmp (its size is not portable): -1, 0 or 1, by the first differing character."""
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    ca = ord(a[i]) if i < len(a) else 0
    cb = ord(b[i]) if i < len(b) else 0
    return -1 if ca < cb else (1 if ca > cb else 0)


def c_strchr(s: str, ch: str) -> str:
    """The rest of s from the first ch."""
    i = s.index(ch)
    return s[i:]


def c_strrchr(s: str, ch: str) -> str:
    return s[s.rindex(ch):]


# ── printf, spelled out ─────────────────────────────────────────────────

_SPEC = re.compile(r"%([-+ 0#]*)(\*|\d+)?(?:\.(\*|\d+))?(hh|h|ll|l|z|t|j)?([diuxXocsf%])")


def fixed(x: float, digits: int) -> str:
    """%.Nf of a double: the EXACT value of the double, rounded. A value exactly half way between two results is
    refused (`Retry`): C libraries have broken those ties in different ways over the years."""
    d = Decimal(x)
    q = Decimal(1).scaleb(-digits)
    scaled = d / q
    if scaled == scaled.to_integral_value() + Decimal("0.5") or scaled == scaled.to_integral_value() - Decimal("0.5"):
        raise Retry
    out = format(d.quantize(q, rounding=ROUND_HALF_EVEN), "f")
    if out.startswith("-") and float(out) == 0.0:
        return out  # C prints "-0.00" for a small negative: keep it (callers avoid it)
    return out


def _pad(text: str, width: int | None, left: bool, zero: bool) -> str:
    if width is None or len(text) >= width:
        return text
    if left:
        return text + " " * (width - len(text))
    if zero:
        sign = text[0] if text[:1] in "+- " else ""
        prefix = text[len(sign):len(sign) + 2] if text[len(sign):len(sign) + 2].lower() in ("0x",) else ""
        body = text[len(sign) + len(prefix):]
        return sign + prefix + "0" * (width - len(text)) + body
    return " " * (width - len(text)) + text


def cfmt(fmt: str, *args: Any) -> str:
    """What `printf(fmt, args...)` writes, without the trailing newline an item prints (the oracle cuts the whitespace
    at both ends anyway). Arguments: ints (`V` is unwrapped), strings for %s, floats for %f."""
    args_i = iter(args)
    out, pos = [], 0
    for m in _SPEC.finditer(fmt):
        out.append(fmt[pos:m.start()])
        pos = m.end()
        flags, width, prec, _, conv = m.groups()
        if conv == "%":
            out.append("%")
            continue
        if width == "*":
            w = int(next(args_i))
            if w < 0:
                flags += "-"
                w = -w
            width = str(w)
        if prec == "*":
            prec = str(int(next(args_i)))
        arg = next(args_i)
        arg = arg.v if isinstance(arg, V) else arg
        w = int(width) if width else None
        left = "-" in flags
        zero = "0" in flags and not left and (prec is None or conv == "f") and conv != "s" and conv != "c"
        if conv in "di":
            n = int(arg)
            digits = str(abs(n))
            if prec is not None:
                digits = digits.rjust(int(prec), "0")
            sign = "-" if n < 0 else ("+" if "+" in flags else (" " if " " in flags else ""))
            text = sign + digits
        elif conv in "uxXo":
            n = int(arg)
            assert n >= 0, "an unsigned conversion of a negative number: pass an unsigned value"
            digits = {"u": str(n), "x": format(n, "x"), "X": format(n, "X"), "o": format(n, "o")}[conv]
            if prec is not None:
                digits = digits.rjust(int(prec), "0")
            prefix = ""
            if "#" in flags and n != 0:
                prefix = {"x": "0x", "X": "0X", "o": "0"}.get(conv, "")
                if conv == "o" and digits.startswith("0"):
                    prefix = ""
            text = prefix + digits
        elif conv == "c":
            text = chr(int(arg))
        elif conv == "s":
            text = str(arg)
            if prec is not None:
                text = text[:int(prec)]
        else:  # f
            digits_after = int(prec) if prec is not None else 6
            body = fixed(float(arg), digits_after)
            neg_ = body.startswith("-")
            body = body.lstrip("-")
            if digits_after == 0 and "#" in flags:
                body += "."
            sign = "-" if neg_ else ("+" if "+" in flags else (" " if " " in flags else ""))
            text = sign + body
        out.append(_pad(text, w, left, zero))
    out.append(fmt[pos:])
    return "".join(out)


def show(v: Any) -> str:
    """The answer as typed: ints plain, strings as they are, a V as its number."""
    if isinstance(v, V):
        return str(v.v)
    if isinstance(v, bool):
        return "1" if v else "0"
    return str(v)


# ── Parameters and templates ────────────────────────────────────────────

def P(rng: random.Random) -> dict[str, Any]:
    """Holes a template can use: $a $b $c $d (different ints 2-9), $n (10-40), $m (50-99), $u (200-250) and $u2
    (50-120): byte-sized values, $big (30000-60000), $k (1-3), $h (2, 4 or 5: a divisor that gives a short decimal),
    $x $y (different lowercase letters a-h), $X (the capital of $x), $w and $z (different words), $L (len of $w),
    $i (a position in $w, 1 to len-1), $j (any position in $w), $f (a letter of $w), $r (0 or 1), $q (0, 1 or 2),
    $s (a shift count, 3-15), $pw (a number, half of them powers of two), $hx and $hy (two-digit hex numbers as
    capitals, e.g. `A5`, to follow `0x`) and $hxv $hyv (their values)."""
    a, b, c, d = rng.sample(range(2, 10), 4)
    w, z = rng.sample(WORDS, 2)
    x, y = rng.sample("abcdefgh", 2)
    hx, hy = rng.randint(0x10, 0xFF), rng.randint(0x10, 0xFF)
    return {"a": a, "b": b, "c": c, "d": d, "n": rng.randint(10, 40), "m": rng.randint(50, 99),
            "u": rng.randint(200, 250), "u2": rng.randint(50, 120), "big": rng.randint(30000, 60000),
            "k": rng.randint(1, 3), "h": rng.choice((2, 4, 5)), "x": x, "y": y, "X": x.upper(),
            "w": w, "z": z, "L": len(w), "i": rng.randint(1, len(w) - 1), "j": rng.randrange(len(w)),
            "f": rng.choice(w), "r": rng.randrange(2), "q": rng.randrange(3), "s": rng.randint(3, 15),
            "pw": rng.choice((6, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 128)), "hxv": hx, "hyv": hy,
            "hx": format(hx, "X"), "hy": format(hy, "X")}


def C(fmt: str, ans: Any, why: str | Callable[[dict], str] = "", check: Callable[[str], str] | str | None = None) -> Maker:
    """A C template: `fmt` the prompt (a string.Template over `P`; write it as a RAW string), `ans` the hand-worked
    value (a function of the parameters, or a value) shown with `show`, `why` the explanation (a sentence, or a
    function of the parameters), `check` an optional oracle program (the prompt as run, when it differs)."""
    def make(rng: random.Random) -> Item:
        last: Retry | None = None
        for _ in range(60):
            p = P(rng)
            try:
                value = ans(p) if callable(ans) else ans
            except Retry as e:
                last = e
                continue
            prompt = Template(fmt).substitute(p)
            why_text = why(p) if callable(why) else Template(why).safe_substitute(p)
            if callable(check):
                program = check(prompt)
            elif isinstance(check, str):
                program = Template(check).substitute(p)
            else:
                program = ""
            return Item(prompt, show(value), why_text, check=program)
        raise AssertionError(f"template {fmt[:40]!r} never found parameters that suit it ({last})")
    make.__name__ = "c_" + re.sub(r"\W+", "_", fmt[:24])
    return make


def program(*lines: str) -> str:
    """Lines joined into a prompt."""
    return "\n".join(lines)
