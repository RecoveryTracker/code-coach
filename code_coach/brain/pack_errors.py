"""The Errors Pack: eight activities about what goes wrong and how to read it.

Which Error, Which Line, Read the Message, Try Flow, Fix It, Crash or Print,
Off by One Bug, Typo Hunt. Each has a JavaScript and a Python generator built
from many templates (Python's pool is the bigger: it is the language to
practise). The templates are in `_errors_py.py` and `_errors_js.py`; every
answer in them is modelled by hand, and each item's `check` program RUNS the
shown code in the real language and works the answer out from what happened
(the exception's name, the line of its traceback, what was printed, which of
two fixes passes), so tests/test_brain_packs.py holds the hand model to the
real node and the real Python. This file only wires the templates into
Activities - see pack_reading.py, the pattern for a pack.
"""

from __future__ import annotations

from . import _errors_js as js
from . import _errors_py as py
from ._model import Pool
from .items import Activity

ACTIVITIES: tuple[Activity, ...] = (
    Activity("err_which", "Which Error", "Run it in your head: which kind of error does it raise? Type its name.",
             "Which error does it raise?", 12, "type", 4.5, 16.0, Pool(js.WHICH_ERROR), make_py=Pool(py.WHICH_ERROR),
             question_py="Which exception does it raise?",
             group="Errors", concepts=("exception", "error", "traceback", "runtime error", "type error"), oracle="value"),
    Activity("err_line", "Which Line", "A few lines, one of them fails. Which line number does the error come from?",
             "Which line number raises the error?", 10, "type", 5.0, 20.0, Pool(js.WHICH_LINE), make_py=Pool(py.WHICH_LINE),
             group="Errors", concepts=("traceback", "exception", "line number", "call stack", "runtime error"), oracle="value"),
    Activity("err_message", "Read the Message", "Read the error message: is something missing, or is it the wrong kind of value? "
             "Left for missing, right for wrong.",
             "Is something missing, or is it the wrong kind of value?", 14, "pick", 2.5, 10.0, Pool(js.MESSAGE),
             ("missing", "wrong"), make_py=Pool(py.MESSAGE),
             group="Spot the problem", concepts=("error message", "exception", "type error", "name error", "index error"), oracle="value"),
    Activity("err_flow", "Try Flow", "Follow the try, catch and finally: what does it print, with nothing between the letters?",
             "What does it print, joined together?", 8, "type", 6.0, 24.0, Pool(js.WHICH_FLOW), make_py=Pool(py.WHICH_FLOW),
             blurb_py="Follow the try, except, else and finally: what does it print, with nothing between the letters?",
             group="Errors", concepts=("try", "except", "catch", "finally", "exception", "control flow"), oracle="value"),
    Activity("err_fix", "Fix It", "One line is the bug. Which replacement makes the program print what is wanted? "
             "Left for 1, right for 2.",
             "Which fix works?", 8, "pick", 5.0, 18.0, Pool(js.FIX), ("1", "2"), make_py=Pool(py.FIX),
             group="Spot the problem", concepts=("bug", "debugging", "fix", "exception", "return value"), oracle="value"),
    Activity("err_crash", "Crash or Print", "The program crashes part way. What is the last line it printed?",
             "What is the last line it prints?", 10, "type", 4.5, 18.0, Pool(js.CRASH), make_py=Pool(py.CRASH),
             group="Errors", concepts=("exception", "crash", "traceback", "output", "runtime error"), oracle="value"),
    Activity("err_offby", "Off by One Bug", "Two loops, one is off by one. Which prints the wanted output? "
             "Left for 1, right for 2.",
             "Which loop prints the wanted output?", 8, "pick", 5.0, 18.0, Pool(js.OFF_BY_ONE), ("1", "2"),
             make_py=Pool(py.OFF_BY_ONE),
             group="Spot the problem", concepts=("off-by-one", "loop", "range", "slice", "bounds"), oracle="value"),
    Activity("err_typo", "Typo Hunt", "One word is misspelled and makes it fail. Type the misspelled word.",
             "Which word is misspelled?", 12, "type", 3.5, 14.0, Pool(js.TYPO), make_py=Pool(py.TYPO),
             group="Spot the problem", concepts=("typo", "name error", "syntax error", "identifier", "keyword"), oracle="value"),
)
