"""The Reading Pack: eight activities about reading code - what a line gives, whether it raises, what changed.

Index It, Slice It, What Type, Equal or Not, Mutate or Copy, Error or Fine,
Return Value, Number Crunch. Each has a JavaScript and a Python generator
built from many templates (Python's pool is the bigger: it is the language to
practise). The templates are in `_reading_py.py`, `_reading_py2.py` and
`_reading_js.py`; every answer in them is modelled by hand, and
tests/test_brain_packs.py runs every template through the real node and the
real Python. This file only wires the templates into Activities - it is the
pattern for a pack (see the package docstring in __init__.py).
"""

from __future__ import annotations

from . import _reading_js as js
from . import _reading_py as py
from . import _reading_py2 as py2
from ._model import Pool
from .items import Activity

ACTIVITIES: tuple[Activity, ...] = (
    Activity("index", "Index It", "Which item sits at that position? Counting starts at 0.",
             "What is the value?", 20, "type", 2.0, 8.0, Pool(js.INDEX), make_py=Pool(py.INDEX),
             group="Quick reads", concepts=("index", "list", "string", "negative index"), oracle="value"),
    Activity("slice", "Slice It", "Cut the list or string: what is left?",
             "What is the result?", 16, "type", 3.0, 12.0, Pool(js.SLICE), make_py=Pool(py.SLICE),
             group="Quick reads", concepts=("slice", "index", "list", "string", "step"), oracle="value"),
    Activity("type", "What Type", "Name the type of each value.",
             "What type name does this give?", 20, "type", 2.0, 8.0, Pool(js.TYPE), make_py=Pool(py.TYPE),
             group="Quick reads", concepts=("type", "integer", "float", "string", "boolean", "none"), oracle="value"),
    Activity("equal", "Equal or Not", "Is the comparison true? Left for no, right for yes.",
             "Is it true?", 16, "pick", 1.4, 6.0, Pool(js.EQUAL), ("no", "yes"), make_py=Pool(py.EQUAL),
             group="Predict the result", concepts=("equality", "comparison", "identity", "operator", "type coercion"),
             oracle="value"),
    Activity("mutate", "Mutate or Copy", "Did the original change? Left for no, right for yes.",
             "Does a end up changed?", 10, "pick", 3.0, 12.0, Pool(js.MUTATE), ("no", "yes"), make_py=Pool(py2.MUTATE),
             group="Spot the problem", concepts=("mutation", "alias", "copy", "reference", "immutable"), oracle="value"),
    Activity("error", "Error or Fine", "Does it crash when it runs? Left for fine, right for error.",
             "Does it raise an error?", 12, "pick", 2.5, 10.0, Pool(js.ERROR), ("fine", "error"), make_py=Pool(py2.ERROR),
             group="Spot the problem", concepts=("exception", "runtime error", "error"), oracle="value",
             question_py="Does it raise an exception?"),
    Activity("return", "Return Value", "What does the call give back?",
             "What does the last line give?", 10, "type", 4.0, 16.0, Pool(js.RETURN), make_py=Pool(py2.RETURN),
             group="Predict the result", concepts=("function", "return value", "parameter", "default parameter", "argument"),
             oracle="value"),
    Activity("number", "Number Crunch", "Work out the number: division, remainders, rounding.",
             "What is the result?", 16, "type", 3.0, 12.0, Pool(js.NUMBER), make_py=Pool(py2.NUMBER),
             group="Predict the result", concepts=("integer", "float", "division", "modulo", "rounding", "operator", "power"),
             oracle="value"),
)
