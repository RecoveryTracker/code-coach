"""The Dart types and OOP pack: eight Dart-only activities about the type system and the object model - mixins,
extensions, abstract classes and interfaces, generics, enums, records, sealed classes with patterns, and constructors.

Mixin Order, Extension Says, Abstract and Implements, Generic Fit, Enum Facts, Record Facts, Sealed Switch, Ctor Order. Each has
only a Dart generator (`make_dart`), built from 40+ templates (`_darttypes_*.py`), so they are played under the Dart
language of the Brain Drills switch and never listed under Python or JavaScript. Every answer is modelled by hand
(`_dart_model.py`, `_darttypes_model.py`) and tests/test_brain_packs.py runs every template through the real `dart` in
batches (tests/dart_oracle.py). The prompts are complete programs (or the body of `main` for the small ones), kept
tiny: one-line members, at most 220 characters and 10 lines. This file only wires the templates into Activities.
"""

from __future__ import annotations

from . import _darttypes_abstract as abstract
from . import _darttypes_ctor as ctor
from . import _darttypes_enum as enums
from . import _darttypes_extension as extension
from . import _darttypes_generic as generic
from . import _darttypes_mixin as mixin
from . import _darttypes_record as record
from . import _darttypes_sealed as sealed
from ._model import Pool
from .items import Activity

GROUP = "Dart types and OOP"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("dt_mixin", "Mixin Order", "Stacked mixins: which method runs, and what do the super calls print?",
             "What does it print?", 10, "type", 7.0, 28.0, make_dart=Pool(mixin.MIXINS),
             group=GROUP, concepts=("inheritance", "override", "super", "method", "subclass"), oracle="value"),
    Activity("dt_extension", "Extension Says", "Extension methods: what does the call return, and which extension is found?",
             "What does it print?", 10, "type", 5.0, 20.0, make_dart=Pool(extension.EXTENSIONS),
             group=GROUP, concepts=("method", "operator", "static-method", "this", "type"), oracle="value"),
    Activity("dt_abstract", "Abstract and Implements", "Abstract classes, extends and implements: which code really runs?",
             "What does it print?", 10, "type", 6.0, 24.0, make_dart=Pool(abstract.ABSTRACTS),
             group=GROUP, concepts=("inheritance", "override", "subclass", "equality", "string-representation"), oracle="value"),
    Activity("dt_generic", "Generic Fit", "Generics and types: what is T, and what is `is` true for?",
             "What does it print?", 12, "type", 4.5, 18.0, make_dart=Pool(generic.GENERICS),
             group=GROUP, concepts=("type", "isinstance", "list", "map", "set"), oracle="value"),
    Activity("dt_enum", "Enum Facts", "Enums: index, name, values, fields and methods. What prints?",
             "What does it print?", 12, "type", 4.0, 16.0, make_dart=Pool(enums.ENUMS_ALL),
             group=GROUP, concepts=("index", "switch", "value", "method", "equality"), oracle="value"),
    Activity("dt_record", "Record Facts", "Dart 3 records: what do they hold, print and equal?",
             "What does it print?", 12, "type", 3.5, 14.0, make_dart=Pool(record.RECORDS),
             group=GROUP, concepts=("tuple", "destructuring", "equality", "unpacking", "immutable"), oracle="value"),
    Activity("dt_sealed", "Sealed Switch", "Sealed classes and patterns: which arm of the switch runs?",
             "What does it print?", 12, "type", 6.0, 24.0, make_dart=Pool(sealed.SEALED),
             group=GROUP, concepts=("switch", "destructuring", "isinstance", "branch", "subclass"), oracle="value"),
    Activity("dt_ctor", "Ctor Order", "Constructors: what runs first, what is lazy, and what is the same object?",
             "What does it print?", 10, "type", 6.0, 24.0, make_dart=Pool(ctor.CTORS),
             group=GROUP, concepts=("class", "instance", "static-method", "side-effect", "identity"), oracle="value"),
)
