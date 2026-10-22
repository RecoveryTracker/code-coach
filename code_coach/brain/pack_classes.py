"""The Classes and Objects Pack: eight activities about what a class gives back.

Attribute Value, Method Returns, Class or Instance, Inherit It, Is It, Same
Object, Counter Class, Default Printing. Each has a Python and a JavaScript
generator built from many templates (Python's pool is the bigger: it is the
language to practise). The templates are in `_classes_py.py` and
`_classes_js.py`; every answer in them is modelled by hand, and
tests/test_brain_packs.py runs every template through the real interpreter
and the real node. This file only wires the templates into Activities (see
pack_reading.py, the pattern for a pack).

Class snippets are longer to read than a line of arithmetic, so the par and
slow times here are higher than the Reading Pack's.
"""

from __future__ import annotations

from . import _classes_js as js
from . import _classes_py as py
from ._model import Pool
from .items import Activity

GROUP = "Classes and objects"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("cls_attr", "Attribute Value", "Build the object, call a few methods: what does the attribute hold?",
             "What does the last line give?", 10, "type", 5.0, 20.0, Pool(js.JATTR), make_py=Pool(py.ATTR),
             group=GROUP, concepts=("class", "object", "attribute", "constructor", "property"), oracle="value"),
    Activity("cls_method", "Method Returns", "Call the method: what does it give back?",
             "What does the last line give?", 10, "type", 6.0, 24.0, Pool(js.JMETH), make_py=Pool(py.METH),
             group=GROUP, concepts=("method", "class", "object", "return value", "self"), oracle="value"),
    Activity("cls_shared", "Class or Instance", "Does the object have its own, or does it share the class's?",
             "What does the last line give?", 10, "type", 6.0, 24.0, Pool(js.JSHARED), make_py=Pool(py.SHARED),
             group=GROUP, concepts=("class attribute", "instance attribute", "shadowing", "shared state", "class"),
             oracle="value"),
    Activity("cls_inherit", "Inherit It", "Which method runs, and what does super add?",
             "What does the last line give?", 10, "type", 6.0, 24.0, Pool(js.JINHERIT), make_py=Pool(py.INHERIT),
             group=GROUP, concepts=("inheritance", "override", "subclass", "super", "method resolution order"),
             oracle="value"),
    Activity("cls_isa", "Is It", "Is it an instance of that, or does it have that? Left for no, right for yes.",
             "Is it true?", 12, "pick", 2.5, 10.0, Pool(js.JISA), ("no", "yes"), make_py=Pool(py.ISA),
             group=GROUP, concepts=("isinstance", "instanceof", "subclass", "inheritance", "type"), oracle="value",
             question_py="Is it True?"),
    Activity("cls_same", "Same Object", "Two names, one object? Equal, or the very same? Left for no, right for yes.",
             "Is it true?", 12, "pick", 3.5, 14.0, Pool(js.JSAME), ("no", "yes"), make_py=Pool(py.SAME),
             group=GROUP, concepts=("identity", "equality", "reference", "alias", "copy"), oracle="value",
             question_py="Is it True?"),
    Activity("cls_counter", "Counter Class", "Count what the object remembers after a few calls.",
             "What does the last line give?", 10, "type", 5.0, 20.0, Pool(js.JCOUNT), make_py=Pool(py.COUNT),
             group=GROUP, concepts=("state", "counter", "instance", "static method", "class method"), oracle="value"),
    Activity("cls_print", "Default Printing", "What text does the object turn into?",
             "What text does the last line give?", 10, "type", 5.0, 20.0, Pool(js.JPRINT), make_py=Pool(py.PRINT),
             group=GROUP, concepts=("string representation", "tostring", "repr", "str", "printing"), oracle="value",
             question_py="What text does print(...) show?"),
)
