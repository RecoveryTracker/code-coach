"""The Dart Core Pack: eight Dart-only activities about the language itself - expressions, null safety, final and
const, collections, strings, functions, classes and the order of async code.

Dart Eval, Null or Not, Final or Const, List Map Set, String Surgery, Function Forms, Class Check, Async Order.
Each has only a Dart generator (`make_dart`), built from 45-70 templates, so they are played under the Dart
language of the Brain Drills switch and never listed under Python or JavaScript. The templates are in
`_dartcore_basics.py`, `_dartcore_data.py`, `_dartcore_text.py`, `_dartcore_classes.py` and `_dartcore_async.py`;
every answer is modelled by hand with `_dart_model.py`, and tests/test_brain_packs.py runs every template through
the real `dart` in batches (tests/dart_oracle.py). This file only wires the templates into Activities.

`oracle`: "value" - the program's printed line is the answer; "lines" - the printed lines glued together (Async
Order's letters); "error" - the snippet as shown either runs quietly ("fine") or does not compile or throws ("error").
"""

from __future__ import annotations

from . import _dartcore_async as aio
from . import _dartcore_basics as basics
from . import _dartcore_classes as classes
from . import _dartcore_data as data
from . import _dartcore_text as text
from ._model import Pool
from .items import Activity

GROUP = "Dart core"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("dart_eval", "Dart Eval", "What does print show? Twenty quick ones.",
             "What does print() show?", 20, "type", 2.5, 10.0, make_dart=Pool(basics.EVAL),
             group=GROUP, concepts=("expression", "operator", "precedence", "division", "modulo", "float", "integer"),
             oracle="value"),
    Activity("dart_null", "Null or Not", "Null safety: what does it print when a value might be null?",
             "What does it print?", 16, "type", 3.0, 12.0, make_dart=Pool(basics.NULLS),
             group=GROUP, concepts=("short-circuit", "default-value", "optional-chaining", "ternary", "string"),
             oracle="value"),
    Activity("dart_final", "Final or Const", "Does it compile and run? Left for fine, right for error.",
             "Does it compile and run without an error?", 14, "pick", 2.5, 10.0, make_dart=Pool(data.FINALS),
             choices=("fine", "error"), group=GROUP,
             concepts=("immutable", "mutable", "reassign", "variable", "runtime-error", "syntax-error"), oracle="error"),
    Activity("dart_lms", "List Map Set", "Lists, maps and sets: what do they print after the call?",
             "What does it print?", 16, "type", 3.5, 14.0, make_dart=Pool(data.COLLECTIONS),
             group=GROUP, concepts=("set", "map", "filter", "reduce", "index", "iterable", "sorting", "join"),
             oracle="value"),
    Activity("dart_str", "String Surgery", "Cut, pad, search and swap text: what does it print?",
             "What does it print?", 16, "type", 3.0, 12.0, make_dart=Pool(text.STRINGS),
             group=GROUP, concepts=("string", "split", "join", "padding", "replace", "string-search", "letter-case", "character"),
             oracle="value"),
    Activity("dart_func", "Function Forms", "Optional and named parameters, arrows and closures: what comes out?",
             "What does it print?", 10, "type", 4.0, 16.0, make_dart=Pool(text.FUNCS),
             group=GROUP, concepts=("function", "parameter", "argument", "default-parameter", "return", "closure", "recursion", "scope"),
             oracle="value"),
    Activity("dart_class", "Class Check", "Small Dart classes: constructors, getters, inheritance. What prints?",
             "What does it print?", 10, "type", 5.0, 20.0, make_dart=Pool(classes.CLASSES),
             group=GROUP, concepts=("class", "instance", "inheritance", "override", "super", "method", "static-method", "string-representation"),
             oracle="value"),
    Activity("dart_async", "Async Order", "In what order do the prints happen? Type the letters in order.",
             "Which letters print, in order?", 10, "type", 5.0, 20.0, make_dart=Pool(aio.ORDERS),
             group=GROUP, concepts=("async-await", "callback", "call-stack", "control-flow", "side-effect"),
             oracle="lines"),
)
