"""The TypeScript Core Pack: eight TypeScript-only activities about the language under `tsc --strict`.

TS Eval, Narrowing, Does tsc Accept It?, Generics, Classes & Interfaces, Typed Arrays & Tuples, Enums & Literals,
Null & Undefined. Each has only a TypeScript generator (`make_ts`), built from 30+ templates in `_tscore_basics.py`,
`_tscore_types.py` and `_tscore_data.py`. Every answer is worked out by hand in Python; tests/ts_oracle.py compiles every
template with the real `tsc --strict` and runs it with node. The item convention is in `_ts_model.py`.
"""

from __future__ import annotations

from . import _tscore_basics as basics
from . import _tscore_data as data
from . import _tscore_types as types
from ._model import Pool
from .items import Activity

GROUP = "TypeScript core"

NOTE = " The code runs under tsc --strict."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("ts_eval", "TS Eval", "Arithmetic, strings, templates, typeof, Math and conversions: what does console.log print?" + NOTE,
             "What does it print?", 16, "type", 3.0, 12.0, make_ts=Pool(basics.EVAL), group=GROUP,
             concepts=("expression", "operator", "precedence", "template literal", "type coercion", "typeof", "string"),
             oracle="value"),
    Activity("ts_narrow", "Narrowing", "A union goes in, the type check picks the branch: what prints?" + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_ts=Pool(types.NARROW), group=GROUP,
             concepts=("type-narrowing", "union type", "type guard", "instanceof", "discriminated union", "truthy", "null"),
             oracle="value"),
    Activity("ts_compile", "Does tsc Accept It?", "Fine, or an error? A type error or a crash at run time both count as error." + NOTE,
             "Does tsc --strict accept it, and does it run?", 16, "pick", 4.0, 16.0, make_ts=Pool(types.COMPILE),
             choices=("fine", "error"), group=GROUP,
             concepts=("type error", "interface", "readonly", "type-narrowing", "optional chaining", "unknown", "never"),
             oracle="error"),
    Activity("ts_generics", "Generics", "Type parameters, keyof, constraints and generic classes: what prints?" + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_ts=Pool(types.GENERICS), group=GROUP,
             concepts=("generics", "type parameter", "constraint", "keyof", "record", "class", "callback"),
             oracle="value"),
    Activity("ts_classes", "Classes & Interfaces", "Constructors, getters, statics, inheritance, interfaces and spread: what prints?" + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_ts=Pool(data.CLASSES), group=GROUP,
             concepts=("class", "inheritance", "interface", "constructor", "getter", "static method", "override", "super"),
             oracle="value"),
    Activity("ts_arrays", "Typed Arrays & Tuples", "map, filter, reduce, sort, slice, splice, tuples and destructuring: what prints?" + NOTE,
             "What does it print?", 14, "type", 4.0, 16.0, make_ts=Pool(data.ARRAYS), group=GROUP,
             concepts=("array", "tuple", "sorting", "destructuring", "spread", "reduce", "slice"),
             oracle="value"),
    Activity("ts_enum", "Enums & Literals", "Numeric and string enums, as const objects and literal unions: what prints?" + NOTE,
             "What does it print?", 12, "type", 4.0, 16.0, make_ts=Pool(data.ENUMS), group=GROUP,
             concepts=("enum", "literal type", "union type", "keyof", "object", "string"),
             oracle="value"),
    Activity("ts_null", "Null & Undefined", "Optional parameters, defaults, ?? against ||, ?. and the nothings: what prints?" + NOTE,
             "What does it print?", 14, "type", 3.5, 14.0, make_ts=Pool(basics.NULLS), group=GROUP,
             concepts=("null", "undefined", "optional chaining", "nullish coalescing", "default parameter", "falsy", "optional parameter"),
             oracle="value"),
)
