"""The Logic and Flow Pack: eight activities about what conditions give and which branch runs.

Which Value, Which Branch, Same Logic, Truth Table Row, Ternary Pick, Bit Ops,
In Range, Leap & Fizz. Each has a Python generator (>= 40 templates, the
language to practise) and a JavaScript one (>= 25). The templates are in
`_logic_py.py` (which also holds the hand models both languages share) and
`_logic_js.py`; every answer is modelled by hand, and
tests/test_brain_packs.py runs every template through the real interpreter and
the real node. This file only wires the templates into Activities.
"""

from __future__ import annotations

from . import _logic_js as js
from . import _logic_py as py
from ._model import Pool
from .items import Activity

GROUP = "Logic and flow"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("logic_value", "Which Value", "and, or and ?? hand back one of their sides: which value comes out?",
             "What value does it give?", 14, "type", 3.0, 12.0, Pool(js.JS_VALUE), make_py=Pool(py.PY_VALUE),
             group=GROUP, concepts=("short-circuit", "truthy", "falsy", "logical operator", "default value"),
             oracle="value"),
    Activity("logic_branch", "Which Branch", "Follow the if / elif / else: which label ends up in label?",
             "What is label at the end?", 10, "type", 4.0, 16.0, Pool(js.JS_BRANCH), make_py=Pool(py.PY_BRANCH),
             group=GROUP, concepts=("branch", "conditional", "condition", "if statement", "elif"), oracle="value"),
    Activity("logic_same", "Same Logic", "Two conditions: do they always give the same answer? Left for no, right for yes.",
             "Same result for every a, b, c (true or false) and every whole x from 0 to 11?", 10, "pick", 3.0, 12.0,
             Pool(js.JS_SAME), ("no", "yes"), make_py=Pool(py.PY_SAME),
             group=GROUP, concepts=("de morgan", "boolean", "equivalence", "logical operator", "negation"),
             oracle="value"),
    Activity("logic_table", "Truth Table Row", "Work out the whole condition for these values. Left for no, right for yes.",
             "Is the whole condition true?", 12, "pick", 2.5, 10.0, Pool(js.JS_TABLE), ("no", "yes"),
             make_py=Pool(py.PY_TABLE),
             group=GROUP, concepts=("boolean", "logical operator", "precedence", "truth table", "negation"),
             oracle="value"),
    Activity("logic_ternary", "Ternary Pick", "A one-line choice: which value does it give?",
             "What value does it give?", 14, "type", 3.0, 12.0, Pool(js.JS_TERNARY), make_py=Pool(py.PY_TERNARY),
             group=GROUP, concepts=("ternary", "conditional expression", "condition", "precedence", "nested"),
             oracle="value"),
    Activity("logic_bits", "Bit Ops", "Work out the bit operation: & | ^ ~ << >> on whole numbers.",
             "What is the result?", 12, "type", 4.0, 16.0, Pool(js.JS_BITS), make_py=Pool(py.PY_BITS),
             group=GROUP, concepts=("bitwise", "bit shift", "binary", "mask", "operator"), oracle="value"),
    Activity("logic_range", "In Range", "Between, in, not in: would the check pass? Left for no, right for yes.",
             "Would the check pass?", 14, "pick", 1.8, 7.0, Pool(js.JS_RANGE), ("no", "yes"), make_py=Pool(py.PY_RANGE),
             group=GROUP, concepts=("chained comparison", "membership", "comparison", "boundary", "range"),
             oracle="value"),
    Activity("logic_classic", "Leap & Fizz", "The classic checks: leap years, FizzBuzz, divisibility and primes.",
             "What does it give?", 10, "type", 4.0, 16.0, Pool(js.JS_CLASSIC), make_py=Pool(py.PY_CLASSIC),
             group=GROUP, concepts=("leap year", "fizzbuzz", "modulo", "divisibility", "prime"), oracle="value"),
)
