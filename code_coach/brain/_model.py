"""Hand-built models of what the two languages do, shared by the packs.

Nothing here asks a runtime anything: floor division is a counting loop, a
sort is an insertion sort, a slice is index arithmetic, and a value is
printed the way each language prints it by spelling the format out. The
tests then run every item through the real node and the real Python (the
oracle rule), so a wrong model shows up as a failing test.

Packs (`pack_<name>.py`) use these to write answers by hand, and `Pool` to
turn a list of template functions into an Activity's generator.
"""

from __future__ import annotations

import random
from string import Template
from typing import Any, Callable

from .items import Item

#: One template: random parameters in, one Item out.
Maker = Callable[[random.Random], Item]

WORDS = ("farm", "drone", "carrot", "loop", "code", "pumpkin", "array", "key", "grid", "tree", "seed",
         "corn", "wheat", "barn", "field", "stone", "river", "cloud", "brick", "lamp", "robot", "maple")


class Pool:
    """An Activity's generator: one of its templates, chosen at random.

    `templates` is public so the tests can count them and run each one."""

    def __init__(self, templates: list[Maker] | tuple[Maker, ...]) -> None:
        self.templates: tuple[Maker, ...] = tuple(templates)

    def __call__(self, rng: random.Random) -> Item:
        return self.templates[rng.randrange(len(self.templates))](rng)


# ── Hand arithmetic ─────────────────────────────────────────────────────

def _count_div(x: int, y: int) -> int:
    """x // y for x >= 0 and y > 0, by counting."""
    q = 0
    while (q + 1) * y <= x:
        q += 1
    return q


def fdiv(a: int, b: int) -> int:
    """Python's a // b: rounds toward minus infinity."""
    q = _count_div(abs(a), abs(b))
    if (a < 0) != (b < 0):
        return -(q if q * abs(b) == abs(a) else q + 1)
    return q


def fmod(a: int, b: int) -> int:
    """Python's a % b: takes the sign of b."""
    return a - b * fdiv(a, b)


def tdiv(a: int, b: int) -> int:
    """a / b cut toward zero (JavaScript's Math.trunc(a / b))."""
    q = _count_div(abs(a), abs(b))
    return -q if (a < 0) != (b < 0) else q


def tmod(a: int, b: int) -> int:
    """JavaScript's a % b: takes the sign of a."""
    return a - b * tdiv(a, b)


def ipow(a: int, n: int) -> int:
    out = 1
    for _ in range(n):
        out *= a
    return out


def isort(xs: list) -> list:
    """A sorted copy, by insertion."""
    out: list = []
    for x in xs:
        k = len(out)
        while k > 0 and out[k - 1] > x:
            k -= 1
        out.insert(k, x)
    return out


def decimal_div(a: int, b: int) -> str:
    """a / b for a terminating decimal, by long division: '3.5', '2' (whole numbers have no '.0' here)."""
    sign = "-" if (a < 0) != (b < 0) else ""
    x, y = abs(a), abs(b)
    whole = _count_div(x, y)
    rest = x - whole * y
    digits = ""
    while rest and len(digits) < 12:
        rest *= 10
        d = _count_div(rest, y)
        digits += str(d)
        rest -= d * y
    assert rest == 0, "not a terminating decimal"
    out = str(whole) + ("." + digits if digits else "")
    return sign + out if out != "0" else out


def py_div(a: int, b: int) -> str:
    """How Python prints a / b: always with a '.0' when whole."""
    s = decimal_div(a, b)
    return s if "." in s else s + ".0"


def upper(text: str) -> str:
    return "".join(chr(ord(ch) - 32) if "a" <= ch <= "z" else ch for ch in text)


def reverse(seq):
    """A reversed copy of a str, list or tuple."""
    picks = [seq[len(seq) - 1 - i] for i in range(len(seq))]
    if isinstance(seq, str):
        return "".join(picks)
    return tuple(picks) if isinstance(seq, tuple) else picks


def find(hay: str | list, needle) -> int:
    """First position of needle in a string (a run of characters) or a list; -1 for none."""
    if isinstance(hay, str):
        for i in range(len(hay) - len(needle) + 1):
            if hay[i:i + len(needle)] == needle:
                return i
        return -1
    for i, x in enumerate(hay):
        if x == needle:
            return i
    return -1


# ── Slices, spelled out ─────────────────────────────────────────────────

def py_slice_positions(n: int, start: int | None, stop: int | None, step: int | None) -> list[int]:
    """Which positions seq[start:stop:step] visits, for a sequence of length n (Python's rules)."""
    step = 1 if step is None else step
    if step > 0:
        lo, hi = 0, n
        s = lo if start is None else (start + n if start < 0 else start)
        e = hi if stop is None else (stop + n if stop < 0 else stop)
        s = max(0, min(n, s))
        e = max(0, min(n, e))
        out, i = [], s
        while i < e:
            out.append(i)
            i += step
        return out
    s = n - 1 if start is None else (start + n if start < 0 else start)
    e = -1 if stop is None else (stop + n if stop < 0 else stop)
    s = max(-1, min(n - 1, s))
    e = max(-1, min(n - 1, e))
    out, i = [], s
    while i > e:
        out.append(i)
        i += step
    return out


def py_slice(seq, start=None, stop=None, step=None):
    """seq[start:stop:step] for a str, list or tuple."""
    picks = [seq[i] for i in py_slice_positions(len(seq), start, stop, step)]
    if isinstance(seq, str):
        return "".join(picks)
    return tuple(picks) if isinstance(seq, tuple) else picks


def js_slice_positions(n: int, start: int | None, end: int | None) -> list[int]:
    """Which positions slice(start, end) keeps: negatives count from the end, everything is clamped."""
    s = 0 if start is None else (max(0, n + start) if start < 0 else min(start, n))
    e = n if end is None else (max(0, n + end) if end < 0 else min(end, n))
    return list(range(s, e)) if s < e else []


def js_slice(seq, start=None, end=None):
    picks = [seq[i] for i in js_slice_positions(len(seq), start, end)]
    return "".join(picks) if isinstance(seq, str) else picks


def js_substring(text: str, a: int, b: int | None = None) -> str:
    """substring(a, b): negatives count as 0, the two swap if out of order, both clamp to the length."""
    n = len(text)
    lo = max(0, min(a, n))
    hi = n if b is None else max(0, min(b, n))
    if lo > hi:
        lo, hi = hi, lo
    return "".join(text[i] for i in range(lo, hi))


# ── Printing, spelled out ───────────────────────────────────────────────

def py_show(v: Any, nested: bool = False) -> str:
    """What print() shows: a str bare at the top, quoted inside a container."""
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, str):
        return "'" + v + "'" if nested else v
    if isinstance(v, list):
        return "[" + ", ".join(py_show(x, True) for x in v) + "]"
    if isinstance(v, tuple):
        inner = ", ".join(py_show(x, True) for x in v)
        return "(" + inner + ("," if len(v) == 1 else "") + ")"
    if isinstance(v, dict):
        return "{" + ", ".join(py_show(k, True) + ": " + py_show(x, True) for k, x in v.items()) + "}"
    return str(v)


class _Const:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


#: JavaScript's two nothings, for js_show.
UNDEF = _Const("undefined")
NULL = _Const("null")


def js_show(v: Any, nested: bool = False) -> str:
    """What console.log shows (node's inspect) for short values: arrays as `[ 1, 2 ]`, objects as `{ a: 1 }`."""
    if v is UNDEF:
        return "undefined"
    if v is NULL:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return "'" + v + "'" if nested else v
    if isinstance(v, list):
        assert len(v) <= 6, "node prints arrays of more than 6 items in grouped columns: keep answers shorter"
        return "[ " + ", ".join(js_show(x, True) for x in v) + " ]" if v else "[]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k}: " + js_show(x, True) for k, x in v.items()) + " }" if v else "{}"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def lit(v: Any) -> str:
    """Source text for ints, strings and lists of them - the same in both languages."""
    if isinstance(v, str):
        return '"' + v + '"'
    if isinstance(v, list):
        return "[" + ", ".join(lit(x) for x in v) + "]"
    return str(v)


# ── Random parameters ───────────────────────────────────────────────────

def ints(rng: random.Random, n: int, lo: int = 1, hi: int = 9) -> list[int]:
    """n different ints from lo..hi."""
    return rng.sample(range(lo, hi + 1), n)


def params(rng: random.Random) -> dict[str, Any]:
    """Names a table row can use: $a..$d (different ints 2-9), $n (10-40), $w and $v (different words),
    $k (1-3), $x (a single lowercase letter)."""
    a, b, c, d = rng.sample(range(2, 10), 4)
    w, v = rng.sample(WORDS, 2)
    return {"a": a, "b": b, "c": c, "d": d, "n": rng.randint(10, 40), "w": w, "v": v,
            "k": rng.randint(1, 3), "x": rng.choice("abcdefgh")}


def row(fmt: str, answer: str | Callable[[dict], str], why: str | Callable[[dict], str] = "",
        check: Callable[[str], str] | None = None) -> Maker:
    """A template from a table row: `fmt` (a string.Template with $a, $w... holes) is the prompt, `answer`
    the hand-worked result (a string, or a function of the parameters), `check` how to build the oracle
    program from the prompt (None: the prompt itself is run)."""
    def make(rng: random.Random) -> Item:
        p = params(rng)
        prompt = Template(fmt).substitute(p)
        got = answer(p) if callable(answer) else answer
        why_text = why(p) if callable(why) else Template(why).safe_substitute(p)
        return Item(prompt, got, why_text, check=check(prompt) if check else "")
    make.__name__ = "row_" + fmt[:24]
    return make


# ── Oracle programs for the yes/no activities ───────────────────────────

def _last_line(code: str) -> tuple[str, str]:
    head, _, last = code.rpartition("\n")
    return head, last


def yes_no_py(code: str) -> str:
    """A program that evaluates the prompt's last line and says "yes" or "no" - for the real interpreter."""
    head, last = _last_line(code)
    return (head + "\n" if head else "") + f'"yes" if ({last}) else "no"'


def yes_no_js(code: str) -> str:
    head, last = _last_line(code)
    return (head + "\n" if head else "") + f'({last.rstrip(";")}) ? "yes" : "no"'


def raises_py(code: str) -> str:
    """A program that runs the prompt and says "error" if it raises, "fine" if not."""
    body = "\n".join("        " + line if line else line for line in code.split("\n"))
    return ("def _try():\n    try:\n" + body + "\n    except Exception:\n        return \"error\"\n"
            "    return \"fine\"\n_try()")


def raises_js(code: str) -> str:
    return '(() => {\n  try {\n' + "\n".join("    " + line for line in code.split("\n")) + \
        '\n  } catch (e) {\n    return "error";\n  }\n  return "fine";\n})()'
