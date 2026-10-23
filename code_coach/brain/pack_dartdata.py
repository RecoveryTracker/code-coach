"""The Dart Data Pack: eight Dart-only activities about the data Dart code moves around - collection literals,
lazy iterables, sorting, numbers and parsing, loops, maps, Dart 3 patterns and text matching.

Spread and If, Iterable Chains, Sort and Compare, Number Parse, Loop Value, Map Moves, Pattern Match, RegExp and
Buffer. Like the Dart Core Pack (`pack_dartcore.py`, the model for this file) each has only a Dart generator
(`make_dart`), built from 45-110 templates, so they are played under the Dart language of the Brain Drills switch and
never listed under Python or JavaScript. The templates are in `_dartdata_*.py`; every answer is modelled by hand in
Python (`_dartdata_model.py` on top of `_dart_model.py`) and tests/test_brain_packs.py runs every template through the
real `dart` in batches (tests/dart_oracle.py). This file only wires the templates into Activities.

`oracle`: "value" - the program's printed line is the answer.
"""

from __future__ import annotations

from . import _dartdata_iter as iterables
from . import _dartdata_loop as loops
from . import _dartdata_map as maps
from . import _dartdata_num as numbers
from . import _dartdata_pattern as patterns
from . import _dartdata_regex as regexes
from . import _dartdata_sort as sorting
from . import _dartdata_spread as spread
from ._model import Pool
from .items import Activity

GROUP = "Dart data"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("dd_spread", "Spread and If", "Lists, maps and sets built with ..., if and for: what do they hold?",
             "What does print show?", 14, "type", 3.5, 14.0, make_dart=Pool(spread.SPREADS),
             group=GROUP, concepts=("spread", "list", "set", "dictionary", "conditional", "for-loop", "copy"),
             oracle="value"),
    Activity("dd_iter", "Iterable Chains", "where, map, take, skip and friends: lazy chains and what they give back.",
             "What does print show?", 14, "type", 4.0, 16.0, make_dart=Pool(iterables.ITERS),
             group=GROUP, concepts=("iterable", "lazy", "filter", "reduce", "generator", "side-effect"),
             oracle="value"),
    Activity("dd_sort", "Sort and Compare", "sort, compareTo and comparators: in what order do the items end up?",
             "What does print show?", 14, "type", 4.0, 16.0, make_dart=Pool(sorting.SORTS),
             group=GROUP, concepts=("sorting", "comparator", "comparison", "reverse", "string-comparison", "ascending"),
             oracle="value"),
    Activity("dd_num", "Number Parse", "Text to numbers and back: parse, round, remainder, overflow, NaN.",
             "What does print show?", 16, "type", 3.0, 12.0, make_dart=Pool(numbers.NUMS),
             group=GROUP, concepts=("type-conversion", "integer", "float", "modulo", "division", "rounding", "remainder",
                                    "precision", "bitwise", "truncate"),
             oracle="value"),
    Activity("dd_loop", "Loop Value", "Run the loop in your head: what is the value (or text) when it is over?",
             "What does print show?", 10, "type", 5.0, 20.0, make_dart=Pool(loops.LOOPS),
             group=GROUP, concepts=("loop", "for-loop", "while-loop", "break", "continue", "nested-loop", "accumulator",
                                    "closure", "counter"),
             oracle="value"),
    Activity("dd_map", "Map Moves", "putIfAbsent, update, remove, entries: what does the map hold afterwards?",
             "What does print show?", 12, "type", 4.5, 18.0, make_dart=Pool(maps.MAPS),
             group=GROUP, concepts=("dictionary", "key", "value", "default-value", "counter", "alias", "copy", "tally"),
             oracle="value"),
    Activity("dd_pattern", "Pattern Match", "Dart 3 records, destructuring and switch patterns: what comes out?",
             "What does print show?", 12, "type", 4.5, 18.0, make_dart=Pool(patterns.PATTERNS),
             group=GROUP, concepts=("destructuring", "unpacking", "rest", "conditional", "tuple", "switch"),
             oracle="value"),
    Activity("dd_regex", "RegExp and Buffer", "Regular expressions, StringBuffer and interpolation: what text results?",
             "What does print show?", 12, "type", 4.0, 16.0, make_dart=Pool(regexes.REGEXES),
             group=GROUP, concepts=("string-search", "search", "replace", "split", "format", "character", "string"),
             oracle="value"),
)
