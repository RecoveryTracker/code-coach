"""Hand models for the C types and preprocessor pack (`pack_ctypes.py`): what `_c_model.py` does not have.

* a tiny C PREPROCESSOR (`expand`): `#define` of object-like and function-like macros, arguments expanded first,
  a macro never re-expanded inside its own expansion - on TOKENS, so `-` `-3` stays two tokens;
* a tiny C EXPRESSION evaluator (`ceval`): ints with C's precedence, `/` and `%` that cut toward zero, `?:`, `&&`, `||`,
  comparisons, unary `- ! ~`; it asserts that nothing overflows an `int` (that would be undefined);
* `macro_value`: the two together (the text of the `#define` lines and of an expression -> the number);
* `stringify`: what `#x` makes of an argument;
* the printed form of a `float` (`f32`) and `%.Nf` of one.

Nothing here asks a C compiler anything; tests/c_oracle.py compiles every item for real.
"""

from __future__ import annotations

import re
import struct
from decimal import ROUND_HALF_EVEN, Decimal

from ._c_model import Retry
from ._model import tdiv, tmod

INT_MIN, INT_MAX = -(1 << 31), (1 << 31) - 1

_TOKEN = re.compile(r"\s*(\d+|[A-Za-z_]\w*|<<|>>|<=|>=|==|!=|&&|\|\||[-+*/%<>!?:(),&|^~])")


def tokens(text: str) -> list[str]:
    """The preprocessing tokens of a line of C (numbers, names, operators and punctuation)."""
    out, pos = [], 0
    text = text.strip()
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        assert m, f"cannot read {text[pos:]!r}"
        out.append(m.group(1))
        pos = m.end()
    return out


# ── The preprocessor ────────────────────────────────────────────────────

Macros = dict  # name -> (parameters or None, body tokens)

_DEFINE = re.compile(r"#\s*define\s+(\w+)(\(([^)]*)\))?\s*(.*)$")


def parse_defines(lines: list[str]) -> Macros:
    """`#define NAME body` and `#define NAME(a, b) body` lines. (`#undef` is handled by the caller.)"""
    macros: Macros = {}
    for line in lines:
        m = _DEFINE.match(line.strip())
        assert m, f"not a #define: {line!r}"
        name, has_params, params, body = m.groups()
        macros[name] = ([p.strip() for p in params.split(",")] if has_params and params.strip() else
                        ([] if has_params else None), tokens(body))
    return macros


def _split_args(toks: list[str], start: int) -> tuple[list[list[str]], int]:
    """The arguments of a call whose `(` is toks[start]: (list of token lists, index after the `)`)."""
    depth, args, cur, i = 0, [], [], start
    while i < len(toks):
        t = toks[i]
        if t == "(":
            depth += 1
            if depth > 1:
                cur.append(t)
        elif t == ")":
            depth -= 1
            if depth == 0:
                args.append(cur)
                return args, i + 1
            cur.append(t)
        elif t == "," and depth == 1:
            args.append(cur)
            cur = []
        else:
            cur.append(t)
        i += 1
    raise AssertionError("unterminated macro call")


def expand(toks: list[str], macros: Macros, hidden: frozenset = frozenset()) -> list[str]:
    """Macro-expand a token list: a function-like macro's arguments are expanded first and then substituted for the
    parameters; the result is rescanned, but never expands the macro it came from again."""
    out: list[str] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in macros and t not in hidden:
            params, body = macros[t]
            if params is None:
                out += expand(body, macros, hidden | {t})
                i += 1
                continue
            if i + 1 < len(toks) and toks[i + 1] == "(":
                args, i = _split_args(toks, i + 1)
                if params == [] and args == [[]]:
                    args = []
                assert len(args) == len(params), f"{t} takes {len(params)} arguments"
                args = [expand(a, macros, hidden) for a in args]
                sub: list[str] = []
                for b in body:
                    sub += args[params.index(b)] if b in params else [b]
                out += expand(sub, macros, hidden | {t})
                continue
        out.append(t)
        i += 1
    return out


# ── Expressions ─────────────────────────────────────────────────────────

class _Parser:
    def __init__(self, toks: list[str], env: dict) -> None:
        self.t, self.i, self.env = toks, 0, env

    def peek(self) -> str:
        return self.t[self.i] if self.i < len(self.t) else ""

    def take(self) -> str:
        tok = self.t[self.i]
        self.i += 1
        return tok

    def ternary(self) -> int:
        cond = self.lor()
        if self.peek() == "?":
            self.take()
            a = self.ternary()
            assert self.take() == ":"
            b = self.ternary()
            return a if cond else b
        return cond

    def lor(self) -> int:
        v = self.land()
        while self.peek() == "||":
            self.take()
            r = self.land()  # (no side effects here, so no need to skip it)
            v = 1 if (v or r) else 0
        return v

    def land(self) -> int:
        v = self.equality()
        while self.peek() == "&&":
            self.take()
            r = self.equality()
            v = 1 if (v and r) else 0
        return v

    def equality(self) -> int:
        v = self.relation()
        while self.peek() in ("==", "!="):
            op = self.take()
            r = self.relation()
            v = int(v == r) if op == "==" else int(v != r)
        return v

    def relation(self) -> int:
        v = self.shift()
        while self.peek() in ("<", ">", "<=", ">="):
            op = self.take()
            r = self.shift()
            v = int({"<": v < r, ">": v > r, "<=": v <= r, ">=": v >= r}[op])
        return v

    def shift(self) -> int:
        v = self.additive()
        while self.peek() in ("<<", ">>"):
            op = self.take()
            r = self.additive()
            assert v >= 0 and 0 <= r < 31, "shift out of range"
            v = _fit(v << r) if op == "<<" else v >> r
        return v

    def additive(self) -> int:
        v = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            r = self.term()
            v = _fit(v + r if op == "+" else v - r)
        return v

    def term(self) -> int:
        v = self.unary()
        while self.peek() in ("*", "/", "%"):
            op = self.take()
            r = self.unary()
            if op == "*":
                v = _fit(v * r)
            else:
                assert r != 0, "division by zero"
                v = _fit(tdiv(v, r) if op == "/" else tmod(v, r))
        return v

    def unary(self) -> int:
        t = self.peek()
        if t == "-":
            self.take()
            return _fit(-self.unary())
        if t == "+":
            self.take()
            return self.unary()
        if t == "!":
            self.take()
            return int(not self.unary())
        if t == "~":
            self.take()
            return ~self.unary()
        return self.primary()

    def primary(self) -> int:
        t = self.take()
        if t == "(":
            v = self.ternary()
            assert self.take() == ")"
            return v
        if t.isdigit():
            return int(t)
        assert t in self.env, f"unknown name {t}"
        return self.env[t]


def _fit(v: int) -> int:
    assert INT_MIN <= v <= INT_MAX, f"int overflow ({v}): undefined behaviour"
    return v


def ceval(toks: list[str] | str, env: dict | None = None) -> int:
    """The value of an integer expression with C's precedence (names come from env)."""
    if isinstance(toks, str):
        toks = tokens(toks)
    p = _Parser(toks, env or {})
    v = p.ternary()
    assert p.i == len(toks), f"left over: {toks[p.i:]}"
    return v


def macro_value(defines: list[str], expr: str, env: dict | None = None) -> int:
    """What `expr` is after the `#define` lines: expand, then evaluate."""
    return ceval(expand(tokens(expr), parse_defines(defines)), env)


def macro_text(defines: list[str], expr: str) -> str:
    """The expansion itself, tokens joined with single spaces (for explanations)."""
    return " ".join(expand(tokens(expr), parse_defines(defines)))


def stringify(arg: str) -> str:
    """What `#x` makes of the argument `arg`: its text with the white space cut at both ends and squeezed to one space
    in the middle."""
    return " ".join(arg.split())


# ── float ───────────────────────────────────────────────────────────────

def f32(x: float) -> float:
    """x rounded to the nearest IEEE single (what a C `float` holds), as a double."""
    return struct.unpack("f", struct.pack("f", x))[0]


def fixed_exact(x: float, digits: int) -> str:
    """`%.Nf` of a double: its exact value rounded half-even (a tie raises Retry: libraries differ on those)."""
    d = Decimal(x)
    q = Decimal(1).scaleb(-digits)
    scaled = d / q
    frac = abs(scaled - scaled.to_integral_value(rounding="ROUND_FLOOR"))
    if frac == Decimal("0.5"):
        raise Retry
    out = format(d.quantize(q, rounding=ROUND_HALF_EVEN), "f")
    if out.startswith("-") and float(out) == 0.0:
        raise Retry  # "-0.00": keep such answers out
    return out
