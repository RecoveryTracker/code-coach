"""The Functions and Scope Pack: eight activities about what functions do with their names and values.

Which x (scope), Default Args, Count the Calls, Closure Counter, Args Count,
Recursion Result, Map Filter Reduce, Pass or Copy. Each has a Python and a
JavaScript generator built from many templates (Python's pool is the bigger
one: it is the language to practise). The templates are in `_functions_py.py`
and `_functions_js.py`; every answer in them is modelled by hand, and
tests/test_brain_packs.py runs every template through the real node and the
real Python. This file only wires the templates into Activities (see the
package docstring in __init__.py).
"""

from __future__ import annotations

from . import _functions_js as js
from . import _functions_py as py
from ._model import Pool
from .items import Activity

GROUP = "Functions and scope"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("fn_scope", "Which x", "Which x does the function see? Follow where each name lives.",
             "What does the last line give?", 10, "type", 4.0, 16.0, Pool(js.SCOPE), make_py=Pool(py.SCOPE),
             blurb_py="Which x does the function see? Follow local, global and nonlocal names.",
             group=GROUP, concepts=("scope", "local variable", "global variable", "shadowing", "block scope"),
             oracle="value"),
    Activity("fn_defaults", "Default Args", "What does a default value do on each call?",
             "What does the last line give?", 10, "type", 4.0, 16.0, Pool(js.DEFAULTS), make_py=Pool(py.DEFAULTS),
             group=GROUP, concepts=("default parameter", "parameter", "argument", "mutable default"),
             oracle="value"),
    Activity("fn_calls", "Count the Calls", "How many times does the function run, and in what order?",
             "What does the last line give?", 8, "type", 5.0, 20.0, Pool(js.CALLS), make_py=Pool(py.CALLS),
             group=GROUP, concepts=("function call", "recursion", "call stack", "short-circuit", "side effect"),
             oracle="value"),
    Activity("fn_closure", "Closure Counter", "What does a closure remember between calls?",
             "What does the last line give?", 8, "type", 5.0, 20.0, Pool(js.CLOSURE), make_py=Pool(py.CLOSURE),
             group=GROUP, concepts=("closure", "late binding", "nonlocal", "lambda", "arrow function"),
             oracle="value"),
    Activity("fn_args", "Args Count", "How many arguments arrive, and what do they add up to?",
             "What does the last line give?", 10, "type", 3.5, 14.0, Pool(js.ARGS), make_py=Pool(py.ARGS),
             blurb_py="How many arguments arrive? Count the *args, the **kwargs and the unpacking.",
             group=GROUP, concepts=("argument", "parameter", "rest parameter", "spread", "unpacking",
                                    "keyword argument"),
             oracle="value"),
    Activity("fn_recur", "Recursion Result", "A function that calls itself: what does it give back?",
             "What does the last line give?", 8, "type", 5.0, 20.0, Pool(js.RECUR), make_py=Pool(py.RECUR),
             group=GROUP, concepts=("recursion", "base case", "return value", "call stack"),
             oracle="value"),
    Activity("fn_mfr", "Map Filter Reduce", "What do map, filter and reduce make of the list?",
             "What does the last line give?", 10, "type", 4.0, 16.0, Pool(js.MFR), make_py=Pool(py.MFR),
             group=GROUP, concepts=("map", "filter", "reduce", "lambda", "arrow function", "callback",
                                    "higher-order function"),
             oracle="value"),
    Activity("fn_pass", "Pass or Copy", "Does the caller's variable change after the call? Left for no, right for yes.",
             "Does a end up changed?", 10, "pick", 3.0, 12.0, Pool(js.COPY), ("no", "yes"), make_py=Pool(py.COPY),
             group=GROUP, concepts=("argument", "parameter", "mutation", "reference", "immutable"),
             oracle="value"),
)
