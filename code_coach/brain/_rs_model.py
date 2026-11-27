"""Hand-built models for the Rust packs (the sibling of `_c_model.py` and `_dart_model.py`).

Nothing here asks a runtime anything. tests/rust_oracle.py builds every item with the real rustc twice - debug (overflow
checks on) and `-O` (what "Run it" builds) - and both must print the model's answer (the oracle rule).

THE ITEM CONVENTION (the same rule in `tests/rust_oracle.full_program` and `rustProgram` of web/src/lib/brainRound.ts):

* the program is `item.check`, or the prompt when `check` is empty; if it mentions `fn main(` it is a COMPLETE program
  (structs, enums, impls, traits, helper functions, then `fn main()`), else it is the BODY of `fn main()`;
* it PRINTS ITS OWN ANSWER with `println!`, and the answer is its output with the whitespace at both ends cut off (so
  a padding question prints `|  42|`, never `  42`); Rust answers are compared EXACTLY (`sameAnswer`: only the spaces at
  the ends are forgiven), so `{:?}` quotes, `1.0` against `1` and `{:>4}` are real questions;
* nothing that differs between the two builds: no integer overflow that is not explicit (`wrapping_add`,
  `checked_mul`, `overflowing_sub`, `saturating_*` are fine and good questions), no HashMap/HashSet iteration order
  (sort first, or use BTreeMap / BTreeSet), no addresses, time or randomness;
* a fine-or-error activity (`oracle="error"`, choices `("fine", "error")`) asks whether rustc accepts it and it runs
  without panicking: "error" when it does not compile (type error, borrow checker, a deny lint) OR it panics.

`RS(fmt, ans, why, check=None)` builds a template: `fmt` is a string.Template over `P()`'s holes (the C pack's holes, see
`_c_model.P`: `$a $b $c $d` distinct ints 2-9, `$n` 10-40, `$m` 50-99, `$k` 1-3, `$x $y` letters, `$w $z` words, `$L $i
$j $f`...). Rust's `{}` placeholders need no escaping, but a literal `$` must be written `$$`. `ans` is the hand-worked
value (a function of the parameters, or a value) shown with `show` (a str is used as it is), `why` one sentence (never a
`$`). A model function may `raise Retry`.
"""

from __future__ import annotations

import random
import re
from string import Template
from typing import Any, Callable

from ._c_model import P, Retry
from ._model import Maker
from .items import Item

__all__ = ["RS", "P", "Retry", "show", "debug", "fmt_float", "lines"]


def show(v: Any) -> str:
    """`{}` (Display): ints plain, bools `true`/`false`, strings bare, floats with Rust's shortest form (`2` prints
    `2` for an i32 but `2.0` is never Display of an int: pass floats through `fmt_float`)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return fmt_float(v)
    return str(v)


def fmt_float(x: float) -> str:
    """Display (`{}`) of an f64: a whole number prints with NO `.0` (`2.0_f64` prints `2`; Debug `{:?}` keeps it,
    `2.0`), anything else in the shortest digits that read back the same (`0.30000000000000004`), never an exponent
    (`1e21` prints all 22 digits)."""
    if x == int(x) and abs(x) < 1e16:
        return str(int(x))
    return repr(x)


def debug(v: Any) -> str:
    """`{:?}` (Debug): strings `"quoted"`, chars `'c'` (pass a 1-tuple ('c',) for a char), vectors `[1, 2]`, tuples
    `(1, "a")`, Option as `Some(3)` / `None` (pass ("Some", x) or None), bools `true`."""
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, tuple) and len(v) == 1 and isinstance(v[0], str) and len(v[0]) == 1:
        return "'" + v[0] + "'"
    if isinstance(v, tuple) and len(v) == 2 and v[0] in ("Some", "Ok", "Err"):
        return f"{v[0]}({debug(v[1])})"
    if isinstance(v, list):
        return "[" + ", ".join(debug(x) for x in v) + "]"
    if isinstance(v, tuple):
        inner = ", ".join(debug(x) for x in v)
        return "(" + inner + ("," if len(v) == 1 else "") + ")"
    if isinstance(v, float):
        return fmt_float_debug(v)
    return str(v)


def fmt_float_debug(x: float) -> str:
    """Debug of an f64 keeps the `.0`: `{:?}` of 2.0 is `2.0`."""
    if x == int(x) and abs(x) < 1e16:
        return f"{int(x)}.0"
    return repr(x)


def RS(fmt: str, ans: Any, why: str | Callable[[dict], str] = "",
       check: Callable[[str], str] | str | None = None) -> Maker:
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
            return Item(prompt, value if isinstance(value, str) else show(value), why_text, check=program)
        raise AssertionError(f"template {fmt[:40]!r} never found parameters that suit it ({last})")
    make.__name__ = "rs_" + re.sub(r"\W+", "_", fmt[:24])
    return make


def lines(*rows: str) -> str:
    """Lines joined into a prompt."""
    return "\n".join(rows)
