"""Hand-built models for the C strings and memory pack (`pack_cstrings.py`): a byte buffer that behaves like a C char
array, and the string and memory functions worked out on it in plain Python (never by asking a compiler).

`Buf` is `char b[size]`: a fixed number of bytes, all of which a template has set (the C is always `= ""`, `= {0}`, a
literal, or a memset first, so nothing is ever read uninitialised). `strcpy`, `strcat`, `strncpy`, `strncat`, `memcpy`,
`memmove` and `memset` do what the C library does - including the parts people forget (strncpy pads with zeros, does not
terminate a truncated copy; strcpy of a short string leaves the old tail behind) - and ASSERT that every write fits the
buffer, so a template that would overflow is a failing test rather than undefined behaviour in a drill.

`CS(fmt, ans, why)` is `_c_model.C` with extra holes for strings (see `holes`): the C goes in a RAW string.
"""

from __future__ import annotations

import random
import re
from string import Template
from typing import Any, Callable

from ._c_model import P, Retry, cfmt, fixed, show, strcmp_sign  # noqa: F401  (re-exported for the templates)
from ._model import Maker
from .items import Item

__all__ = ["Buf", "CS", "PF", "T", "Retry", "cfmt", "fixed", "show", "strcmp_sign", "sgn", "SGN", "holes"]


def T(*lines: str) -> str:
    return "\n".join(lines)


def PF(conv: str, rest: str) -> str:
    """`printf("<conv>\\n", <rest>);` as C text."""
    return 'printf("' + conv + '\\n", ' + rest + ');'


def sgn(x: int) -> int:
    return (x > 0) - (x < 0)


#: Two lines of C: the strcmp result `r` (whose SIZE is not portable) reduced to -1, 0 or 1.
SGN = T(PF("%d", "(r > 0) - (r < 0)"))


# ── A char array ────────────────────────────────────────────────────────

class Buf:
    """`char b[size]`, as bytes (ints 0-255). Everything starts as `text` then zeros, like `char b[n] = "text";`."""

    def __init__(self, size: int, text: str = "") -> None:
        assert len(text) + 1 <= size, "the initialiser does not fit"
        self.b = [0] * size
        for i, ch in enumerate(text):
            self.b[i] = ord(ch)

    @classmethod
    def filled(cls, size: int, ch: str) -> "Buf":
        """Every byte `ch`, with no NUL at all (the caller terminates it or never reads it as a string)."""
        out = cls(size)
        out.b = [ord(ch)] * size
        return out

    @property
    def size(self) -> int:
        return len(self.b)

    def text(self) -> str:
        """What `%s` prints: the bytes before the first NUL (the buffer must hold one)."""
        out = []
        for v in self.b:
            if v == 0:
                return "".join(out)
            out.append(chr(v))
        raise AssertionError("no NUL in the buffer: %s would run off the end")

    def strlen(self) -> int:
        return len(self.text())

    def _put(self, at: int, data: list[int]) -> None:
        assert 0 <= at and at + len(data) <= self.size, "write past the end of the buffer"
        self.b[at:at + len(data)] = data

    def strcpy(self, src: str, at: int = 0) -> None:
        self._put(at, [ord(c) for c in src] + [0])

    def strcat(self, src: str) -> None:
        self.strcpy(src, self.strlen())

    def strncpy(self, src: str, n: int) -> None:
        """Copies at most n characters and PADS with zeros up to n; a source of n or more characters leaves no NUL."""
        data = [ord(c) for c in src[:n]]
        self._put(0, data + [0] * (n - len(data)))

    def strncat(self, src: str, n: int) -> None:
        """Appends at most n characters and ALWAYS a NUL."""
        self._put(self.strlen(), [ord(c) for c in src[:n]] + [0])

    def memcpy(self, at: int, data: list[int]) -> None:
        self._put(at, list(data))

    def memmove(self, dst: int, src: int, n: int) -> None:
        assert 0 <= src and src + n <= self.size
        self._put(dst, self.b[src:src + n])  # a slice is a copy, so overlap is fine, like memmove

    def memset(self, at: int, value: int, n: int) -> None:
        self._put(at, [value % 256] * n)

    def count(self, value: int) -> int:
        return self.b.count(value)


def lit(s: str) -> list[int]:
    """The bytes of a string literal, NUL included."""
    return [ord(c) for c in s] + [0]


# ── Parameters and templates ────────────────────────────────────────────

#: Characters that are safe in a C char literal inside a template (no quote, no backslash, no percent).
SAFE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !#+-_~"
PALINDROMES = ("level", "radar", "noon", "civic", "refer", "kayak", "abba", "madam", "rotor", "deed", "peep", "tenet")
NEAR = ("levee", "radio", "noun", "civil", "refit", "kayaks", "abbey", "madame", "rotors", "dead", "peek", "tent")


def holes(rng: random.Random) -> dict[str, Any]:
    """The holes of `_c_model.P`, plus the ones strings want:

    $M (len of $z), $v (a third word), $Wc and $Zc (capitalised), $sub (two letters of $w) and $o (where they start),
    $ch and $ch2 (a safe character each), $D (a 4-5 digit number as text, no leading zero), $Dsum (its digit sum),
    $bin (5-6 bits as text) and $binv, $hd (one hex digit, capital) and $hdv, $mix (6-8 characters of letters, digits
    and a space), $dm (letters and digits like a7b2c9) and $dmsum, $rl (runs of letters, like aaabcc), $pal (a
    palindrome, or a near miss) and $ispal, $hh and $mm (two digits each: a time of day), $e (a short file extension)."""
    p = P(rng)
    w, z = p["w"], p["z"]
    from ._model import WORDS

    p["M"] = len(z)
    p["v"] = rng.choice([x for x in WORDS if x not in (w, z)])
    p["Wc"], p["Zc"] = w.capitalize(), z.capitalize()
    p["o"] = rng.randint(0, len(w) - 2)
    p["sub"] = w[p["o"]:p["o"] + 2]
    p["ch"] = rng.choice(SAFE_CHARS)
    p["ch2"] = rng.choice(SAFE_CHARS)
    p["D"] = str(rng.randint(1000, 99999))
    p["Dsum"] = sum(int(c) for c in p["D"])
    p["bin"] = "1" + "".join(rng.choice("01") for _ in range(rng.randint(4, 5)))
    p["binv"] = int(p["bin"], 2)
    p["hd"] = rng.choice("0123456789ABCDEF")
    p["hdv"] = int(p["hd"], 16)
    p["mix"] = "".join(rng.choice("abcdeXYZ12345 ") for _ in range(rng.randint(6, 8)))
    p["dm"] = "".join(rng.choice("abcdefgh") + str(rng.randint(1, 9)) for _ in range(rng.randint(3, 4)))
    p["dmsum"] = sum(int(c) for c in p["dm"] if c.isdigit())
    runs = [(rng.choice("abcdefgh"), rng.randint(1, 4)) for _ in range(3)]
    while runs[0][0] == runs[1][0] or runs[1][0] == runs[2][0]:
        runs = [(rng.choice("abcdefgh"), rng.randint(1, 4)) for _ in range(3)]
    p["rl"] = "".join(c * n for c, n in runs)
    i = rng.randrange(len(PALINDROMES))
    ispal = rng.randrange(2)
    p["pal"] = PALINDROMES[i] if ispal else NEAR[i]
    p["ispal"] = ispal
    p["hh"], p["mm"] = "%02d" % rng.randint(1, 23), "%02d" % rng.randint(0, 59)
    p["e"] = rng.choice(("txt", "png", "csv", "pdf", "log", "zip"))
    return p


def CS(fmt: str, ans: Any, why: str | Callable[[dict], str] = "") -> Maker:
    """A template over `holes`: `fmt` the C (a RAW string), `ans` the hand-worked value (a function of the holes, or a
    value), `why` one sentence. A model function may `raise Retry` to pick new parameters."""
    def make(rng: random.Random) -> Item:
        last: Retry | None = None
        for _ in range(200):
            p = holes(rng)
            try:
                value = ans(p) if callable(ans) else ans
            except Retry as e:
                last = e
                continue
            prompt = Template(fmt).substitute(p)
            why_text = why(p) if callable(why) else Template(why).safe_substitute(p)
            return Item(prompt, show(value), why_text)
        raise AssertionError(f"template {fmt[:40]!r} never found parameters that suit it ({last})")
    make.__name__ = "cs_" + re.sub(r"\W+", "_", fmt[:24])
    return make
