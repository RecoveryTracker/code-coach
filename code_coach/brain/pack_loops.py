"""The Loops Pack: eight activities about what a loop leaves behind.

Range Output, Running Total, Nested Count, Break & Continue, While Trace,
Comprehension Result, Enumerate Zip, Loop Variable After. Loop Count (how many
times) and Final Value (follow assignments) already exist, so these look at
other things a loop does: the list it walks, the total it builds, how nested
loops multiply, where break and continue cut in, what a while loop ends on, what
a comprehension makes, how enumerate / zip / sorted walk, and what the loop
variable is afterwards. Python's pools are the bigger (it is the language to
practise). The templates are in `_loops_py.py` and `_loops_js.py`; every answer
is modelled by hand and tests/test_brain_packs.py runs every template through
the real Python and the real node. This file only wires them into Activities.
"""

from __future__ import annotations

from . import _loops_js as js
from . import _loops_py as py
from ._model import Pool
from .items import Activity

GROUP = "Loops and iteration"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("loop_range", "Range Output", "Which values does the loop or range hand out? Type the list.",
             "What does the last line give?", 12, "type", 3.0, 13.0, Pool(js.RANGE), make_py=Pool(py.RANGE),
             group=GROUP, concepts=("range", "list", "step", "loop", "off-by-one"), oracle="value"),
    Activity("loop_total", "Running Total", "What is the accumulator when the loop is done?",
             "What does the last line give?", 10, "type", 5.0, 20.0, Pool(js.TOTAL), make_py=Pool(py.TOTAL),
             group=GROUP, concepts=("accumulator", "loop", "sum", "variable", "augmented assignment"), oracle="value"),
    Activity("loop_nested", "Nested Count", "Loops inside loops: how much does the inner body add up to?",
             "What does the last line give?", 10, "type", 5.0, 20.0, Pool(js.NESTED), make_py=Pool(py.NESTED),
             group=GROUP, concepts=("nested loop", "iteration", "counter", "loop"), oracle="value"),
    Activity("loop_break", "Break & Continue", "Where does the loop stop or skip? Work out the result.",
             "What does the last line give?", 10, "type", 5.0, 20.0, Pool(js.BREAK), make_py=Pool(py.BREAK),
             group=GROUP, concepts=("break", "continue", "loop", "flag", "for else"), oracle="value"),
    Activity("loop_while", "While Trace", "Follow the while loop until its condition fails.",
             "What does the last line give?", 8, "type", 6.0, 22.0, Pool(js.WHILE), make_py=Pool(py.WHILE),
             group=GROUP, concepts=("while loop", "condition", "loop", "termination"), oracle="value"),
    Activity("loop_comp", "Comprehension Result", "What does the one-line loop build?",
             "What does the last line give?", 10, "type", 5.0, 18.0, Pool(js.COMP), make_py=Pool(py.COMP),
             group=GROUP, concepts=("comprehension", "map", "filter", "list", "dict", "set"), oracle="value",
             blurb_py="What does the comprehension build? Type the list, set size, dict or number."),
    Activity("loop_enum", "Enumerate Zip", "Walk things in pairs, backwards or sorted: what comes out?",
             "What does the last line give?", 10, "type", 5.0, 18.0, Pool(js.ENUM), make_py=Pool(py.ENUM),
             group=GROUP, concepts=("enumerate", "zip", "iteration", "sort", "reverse"), oracle="value"),
    Activity("loop_after", "Loop Variable After", "What is left behind once the loop has finished?",
             "What does the last line give?", 10, "type", 5.0, 18.0, Pool(js.AFTER), make_py=Pool(py.AFTER),
             group=GROUP, concepts=("loop variable", "scope", "closure", "mutation", "block scope"), oracle="value"),
)
