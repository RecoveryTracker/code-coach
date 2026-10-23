"""The Dart Flow Pack: eight Dart-only activities about how a Dart program moves - exceptions, null-safety flow, the
event loop, Futures and Streams, loops and switches, and the words of runtime errors.

Try Order, Which Exception, Promote Or Not, Await Order, Future Result, Stream Sum, Control Flow, Error Message.
Each has only a Dart generator (`make_dart`), built from 40+ templates (`_dartflow_*.py`), so they are played under
the Dart language of the Brain Drills switch and never listed under Python or JavaScript. Every answer is modelled by
hand (`_dartflow_model.py` and `_dart_model.py`) and tests/test_brain_packs.py runs every template through the real
`dart` in batches (tests/dart_oracle.py). This file only wires the templates into Activities.

`oracle`: "value" - the program's one printed line is the answer; "lines" - the printed lines glued together (the
letters of Try Order and Await Order); "error" - the snippet as shown either runs quietly ("fine") or does not
compile or throws ("error").
"""

from __future__ import annotations

from . import _dartflow_await as aw
from . import _dartflow_control as ct
from . import _dartflow_error as er
from . import _dartflow_future as fu
from . import _dartflow_promote as pr
from . import _dartflow_stream as st
from . import _dartflow_try as tr
from . import _dartflow_which as wh
from ._model import Pool
from .items import Activity

GROUP = "Dart flow and async"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("df_try", "Try Order", "try, on, catch, finally: which letters print, in order?",
             "Which letters print, in order?", 10, "type", 6.0, 24.0, make_dart=Pool(tr.TRY),
             group=GROUP, concepts=("try", "catch", "finally", "exception", "throw", "control-flow"),
             oracle="lines"),
    Activity("df_which", "Which Exception", "Which exception does the line throw? Type its class name.",
             "What does it print?", 14, "type", 3.5, 14.0, make_dart=Pool(wh.WHICH),
             group=GROUP, concepts=("exception", "error", "type error", "index error", "runtime error", "throw"),
             oracle="value"),
    Activity("df_promote", "Promote Or Not", "Null safety flow: does it compile and run? Left for fine, right for error.",
             "Does it compile and run without an error?", 14, "pick", 4.0, 16.0, make_dart=Pool(pr.PROMOTE),
             choices=("fine", "error"), group=GROUP,
             concepts=("null", "type check", "conditional", "short-circuit", "default-value", "syntax-error"),
             oracle="error"),
    Activity("df_await", "Await Order", "Deeper async: in what order do the prints happen? Type the letters in order.",
             "Which letters print, in order?", 10, "type", 8.0, 32.0, make_dart=Pool(aw.AWAIT),
             group=GROUP, concepts=("async-await", "await", "callback", "execution order", "side-effect", "order of execution"),
             oracle="lines"),
    Activity("df_future", "Future Result", "What value (or error) comes out of the Future chain?",
             "What does it print?", 12, "type", 6.0, 24.0, make_dart=Pool(fu.FUTURE),
             group=GROUP, concepts=("async-await", "callback", "catch", "finally", "return", "handler"),
             oracle="value"),
    Activity("df_stream", "Stream Sum", "Streams, generators and controllers: what does the pipeline print?",
             "What does it print?", 12, "type", 6.0, 24.0, make_dart=Pool(st.STREAM),
             group=GROUP, concepts=("generator", "yield", "lazy", "iterable", "async-await", "filter"),
             oracle="value"),
    Activity("df_control", "Control Flow", "Loops, labels, switches and ternaries: what does it print?",
             "What does it print?", 14, "type", 5.0, 20.0, make_dart=Pool(ct.CONTROL),
             group=GROUP, concepts=("control-flow", "break-continue", "loop", "while-loop", "ternary", "conditional"),
             oracle="value"),
    Activity("df_error", "Error Message", "Read the error: what does Dart's message say?",
             "What does it print?", 14, "type", 4.0, 16.0, make_dart=Pool(er.ERROR),
             group=GROUP, concepts=("error-message", "exception", "message", "string-representation", "runtime-error", "throw"),
             oracle="value"),
)
