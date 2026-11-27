"""Hand-built models for the TypeScript packs (the sibling of `_c_model.py` and `_dart_model.py`).

Nothing here asks a runtime anything. tests/ts_oracle.py compiles every item with the real `tsc --strict` (the flags
"Run it" uses) and runs it with node, and the printed output must be the model's answer (the oracle rule).

THE ITEM CONVENTION (the same rule in `tests/ts_oracle.full_program` and `tsProgram` of web/src/lib/brainRound.ts):

* the program is `item.check`, or the prompt when `check` is empty: top-level TypeScript statements, compiled as a
  module (`export {};` is added), so a top-level `const name` is fine;
* it PRINTS ITS OWN ANSWER with `console.log`, and the answer is its output with the whitespace at both ends cut off -
  console.log prints the way node's `util.inspect` does: arrays `[ 1, 2 ]` (more than 6 items are printed in columns:
  keep them short), objects `{ a: 1 }`, strings bare at the top and `'quoted'` inside, `true`, `null`, `undefined`;
* no `await`, promises or timers (the oracle does not run the event loop), no node typings (`require`, `process`), and
  the library is ES2020: `xs.at(-1)` (ES2022), `"a".replaceAll` (ES2021) and `Object.hasOwn` do NOT compile;
* a fine-or-error activity (`oracle="error"`, choices `("fine", "error")`) asks whether `tsc --strict` accepts the code
  and it runs without throwing: "error" when tsc refuses it OR it throws.

`TS(fmt, ans, why, check=None)` builds a template: `fmt` is a string.Template over `P()`'s holes (the C pack's holes, see
`_c_model.P`: `$a $b $c $d` distinct ints 2-9, `$n` 10-40, `$m` 50-99, `$k` 1-3, `$h` 2/4/5, `$x $y` letters, `$X`, `$w $z`
words, `$L $i $j $f`, `$r` 0/1, `$q` 0-2...). Write TypeScript's own `${...}` template-literal holes as `$${...}`. `ans` is
the hand-worked value (a function of the parameters, or a value), shown with `js_show` (or given as a str), `why` one
sentence (never a `$`). A model function may `raise Retry`.
"""

from __future__ import annotations

import random
import re
from string import Template
from typing import Any, Callable

from ._c_model import P, Retry
from ._model import NULL, UNDEF, Maker, js_show
from .items import Item

__all__ = ["TS", "P", "Retry", "NULL", "UNDEF", "js_show", "lines", "line_of"]


def line_of(*values: Any) -> str:
    """console.log(a, b, c): each value shown as console.log shows it, joined by spaces."""
    return " ".join(js_show(v) for v in values)


def TS(fmt: str, ans: Any, why: str | Callable[[dict], str] = "",
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
            return Item(prompt, value if isinstance(value, str) else js_show(value), why_text, check=program)
        raise AssertionError(f"template {fmt[:40]!r} never found parameters that suit it ({last})")
    make.__name__ = "ts_" + re.sub(r"\W+", "_", fmt[:24])
    return make


def lines(*rows: str) -> str:
    """Lines joined into a prompt."""
    return "\n".join(rows)
