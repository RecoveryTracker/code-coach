"""The Collections Pack: eight activities about lists, dicts, sets and tuples (arrays, objects, Maps and Sets in JavaScript).

List After, How Many, Dict Lookup, Set Maths, Min Max Sum, Unpack It, Nested
Reach, Sort Order. Python's pools are the deeper ones (>= 40 templates each),
JavaScript's are wide (>= 25). The templates are in `_collections_py.py` and
`_collections_js.py`; every answer in them is modelled by hand, and
tests/test_brain_packs.py runs every template through the real Python and node.
This file only wires the templates into Activities, like pack_reading.py.
"""

from __future__ import annotations

from . import _collections_js as js
from . import _collections_py as py
from ._model import Pool
from .items import Activity

ACTIVITIES: tuple[Activity, ...] = (
    Activity("col_after", "List After", "Run the calls in order: what does the list hold at the end?",
             "What does the last line give?", 10, "type", 4.0, 16.0, Pool(js.AFTER), make_py=Pool(py.AFTER),
             group="Collections", concepts=("list", "array", "mutation", "method", "alias"), oracle="value"),
    Activity("col_howmany", "How Many", "Count the items, keys or letters after each change.",
             "How many?", 12, "type", 3.0, 12.0, Pool(js.HOW), make_py=Pool(py.HOW),
             group="Collections", concepts=("length", "list", "dictionary", "set", "key"), oracle="value"),
    Activity("col_lookup", "Dict Lookup", "What does the lookup give? When it fails, type the error's name.",
             "What does the last line give?", 12, "type", 3.5, 14.0, Pool(js.LOOKUP), make_py=Pool(py.LOOKUP),
             group="Collections", concepts=("dictionary", "object", "key", "map", "default value"), oracle="value"),
    Activity("col_sets", "Set Maths", "Union, intersection, difference: which members are left?",
             "What does the last line give?", 10, "type", 4.0, 16.0, Pool(js.SETS), make_py=Pool(py.SETS),
             group="Collections", concepts=("set", "union", "intersection", "difference", "membership"), oracle="value"),
    Activity("col_minmax", "Min Max Sum", "The smallest, the biggest, the total - with negatives, text and key functions.",
             "What does the last line give?", 12, "type", 3.0, 12.0, Pool(js.MINMAX), make_py=Pool(py.MINMAX),
             group="Collections", concepts=("minimum", "maximum", "sum", "key function", "negative number"), oracle="value"),
    Activity("col_unpack", "Unpack It", "Which value ends up in which name? Swaps, stars, defaults.",
             "What does the last line give?", 12, "type", 3.5, 14.0, Pool(js.UNPACK), make_py=Pool(py.UNPACK),
             group="Collections", concepts=("unpacking", "destructuring", "tuple", "swap", "default value", "rest"),
             oracle="value"),
    Activity("col_nested", "Nested Reach", "Reach into a list in a dict in a list: what is at the end of the path?",
             "What does the last line give?", 12, "type", 3.5, 14.0, Pool(js.NESTED), make_py=Pool(py.NESTED),
             group="Collections", concepts=("nested", "index", "key", "list", "dictionary", "copy"), oracle="value"),
    Activity("col_sort", "Sort Order", "Who comes first after the sort? Numbers, words, keys and ties.",
             "What does the last line give?", 12, "type", 3.5, 14.0, Pool(js.SORTS), make_py=Pool(py.SORTS),
             group="Collections", concepts=("sorting", "comparator", "stable sort", "key function", "string comparison"),
             oracle="value"),
)
