"""Hand models for the C pointers and structs pack (`_c_model.py` has the integers and printf; this file has memory).

Nothing here asks a compiler anything: a C array is a Python list of ints, a pointer is a `Ptr` (the list it points
into and an index), and a struct is a `Struct` whose copy is C's copy. Every operation checks what C would call
undefined - a pointer more than one past the end of its array, a read through the one-past-the-end pointer, two
pointers into different arrays subtracted or compared with `<` - and raises an AssertionError, so a template that would
be undefined behaviour cannot even compute its answer. tests/c_oracle.py then runs the real programs.

`Ptr` is a VALUE like a C pointer: `p + 1` is a new pointer, `p == q` is the same place, and a scalar variable is a
list of one element (`x = [5]`, `&x` is `Ptr(x)`), so a pointer to a variable and a pointer into an array are the same
thing, as in C.
"""

from __future__ import annotations

import copy
import random
from typing import Any, Callable

from ._c_model import P, Retry, show
from ._model import Maker
from .items import Item


class Ptr:
    """A pointer into a C array: `mem` (a list) and an index; `len(mem)` is the one-past-the-end pointer."""

    __slots__ = ("mem", "i")
    __hash__ = None  # type: ignore[assignment]

    def __init__(self, mem: list, i: int = 0) -> None:
        assert 0 <= i <= len(mem), f"pointer {i} outside an array of {len(mem)}: undefined behaviour"
        self.mem, self.i = mem, i

    def __add__(self, n: int) -> "Ptr":
        return Ptr(self.mem, self.i + n)

    def __sub__(self, other: Any) -> Any:
        if isinstance(other, Ptr):
            assert other.mem is self.mem, "subtracting pointers into different arrays: undefined"
            return self.i - other.i
        return Ptr(self.mem, self.i - other)

    def __eq__(self, other: object) -> bool:  # == between any two pointers is always defined
        return isinstance(other, Ptr) and self.mem is other.mem and self.i == other.i

    def _same(self, other: "Ptr") -> None:
        assert isinstance(other, Ptr) and other.mem is self.mem, "ordering pointers of different arrays: undefined"

    def __lt__(self, other: "Ptr") -> bool:
        self._same(other)
        return self.i < other.i

    def __le__(self, other: "Ptr") -> bool:
        self._same(other)
        return self.i <= other.i

    def __gt__(self, other: "Ptr") -> bool:
        self._same(other)
        return self.i > other.i

    def __ge__(self, other: "Ptr") -> bool:
        self._same(other)
        return self.i >= other.i

    def get(self) -> Any:
        assert self.i < len(self.mem), "reading through a one-past-the-end pointer: undefined"
        return self.mem[self.i]

    def set(self, v: Any) -> None:
        assert self.i < len(self.mem), "writing through a one-past-the-end pointer: undefined"
        self.mem[self.i] = v

    def __getitem__(self, k: int) -> Any:
        return (self + k).get()

    def __setitem__(self, k: int, v: Any) -> None:
        (self + k).set(v)


def var(v: Any) -> list:
    """A scalar variable: a one-element array, so `Ptr(var)` is `&var` and `var[0]` its value."""
    return [v]


def addr(x: list) -> Ptr:
    """&x for a variable made with `var`."""
    return Ptr(x, 0)


# ── Strings ─────────────────────────────────────────────────────────────

def cstr(s: str, size: int | None = None) -> list:
    """A char array holding `s` and its NUL (the rest, up to `size`, zero as `char b[size] = "..."` leaves it)."""
    out = [ord(c) for c in s] + [0]
    if size is not None:
        assert size >= len(out), "the string does not fit"
        out += [0] * (size - len(out))
    return out


def text(p: Ptr) -> str:
    """The string a `%s` or `strlen` sees from p: the characters up to the first NUL."""
    out = []
    i = p.i
    while True:
        assert i < len(p.mem), "no NUL before the end of the array: undefined"
        if p.mem[i] == 0:
            return "".join(out)
        out.append(chr(p.mem[i]))
        i += 1


def slen(p: Ptr) -> int:
    return len(text(p))


# ── Structs ─────────────────────────────────────────────────────────────

class Struct:
    """A C struct value. `copy()` is C's assignment: members copied one by one, an array member and a nested struct
    copied in full (they are part of the struct), a pointer member copied as the same pointer (it is only an address).
    Members are read and written as attributes: `s.x`, `s.x = 3`, `s.v[0]`."""

    def __init__(self, **members: Any) -> None:
        object.__setattr__(self, "_m", dict(members))

    def __getattr__(self, name: str) -> Any:
        try:
            return self._m[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name: str, value: Any) -> None:
        assert name in self._m, f"no member {name}"
        self._m[name] = value

    def copy(self) -> "Struct":
        out = {}
        for k, v in self._m.items():
            if isinstance(v, Ptr):
                out[k] = v  # a pointer member: same address
            elif isinstance(v, (list, Struct)):
                out[k] = copy.deepcopy(v) if isinstance(v, list) else v.copy()
            else:
                out[k] = v
        return Struct(**out)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Struct) and self._m == other._m

    __hash__ = None  # type: ignore[assignment]


def ints(*values: Any) -> str:
    """Several numbers as a printf("%d %d ...") line shows them."""
    return " ".join(str(show(v)) for v in values)


# ── A template written as a function ────────────────────────────────────

def custom(fn: Callable[[random.Random, dict], tuple[str, Any, str]]) -> Maker:
    """A template that needs more than a format string (a prompt built from the parameters in code): `fn(rng, p)`
    returns `(prompt, answer, why)` and may `raise Retry` to pick new parameters."""
    def make(rng: random.Random) -> Item:
        last: Retry | None = None
        for _ in range(60):
            p = P(rng)
            try:
                prompt, answer, why = fn(rng, p)
            except Retry as e:
                last = e
                continue
            return Item(prompt, show(answer), why)
        raise AssertionError(f"template {fn.__name__} never found parameters that suit it ({last})")
    make.__name__ = "cp_" + fn.__name__
    return make
