"""The Rust Core Pack: eight Rust-only activities about the language itself - integer and float evaluation, ownership
(move, copy, clone), the borrow checker, match and Option, iterator chains, strings and formatting, structs / enums /
traits, and Vec and maps.

Rust Eval, Move Copy Clone, Borrow Check, Match & Option, Iterator Chains, Strings & Formatting, Structs Enums & Traits,
Vec & Maps. Each has only a Rust generator (`make_rs`), built from 30 or more templates, so they are played under the Rust
language of the app's picker and never listed under another one. The templates are in `_rustcore_basics.py`,
`_rustcore_own.py`, `_rustcore_data.py` and `_rustcore_types.py`; every answer is modelled by hand in Python, and
tests/test_brain_packs.py builds every template with the real rustc twice (tests/rust_oracle.py): debug (overflow
checks on) and -O, which must print the same thing. This file only wires the templates into Activities.

THE ITEM CONVENTION (see `_rs_model.py`): the code is the BODY of `fn main()` unless it mentions `fn main(` (then it is a
complete program); it prints its own answer with `println!` and the answer is its output with the whitespace at both ends
cut off. Rust answers are compared exactly. Borrow Check is a fine-or-error pick (`oracle="error"`): "error" when rustc
refuses the code or it panics when run. `oracle`: "value" for the rest.
"""

from __future__ import annotations

from . import _rustcore_basics as basics
from . import _rustcore_data as data
from . import _rustcore_own as own
from . import _rustcore_types as types
from ._model import Pool
from .items import Activity

GROUP = "Rust core"

#: What every Rust blurb says about the program around the code.
NOTE = " The code is the body of main unless it shows fn main."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("rs_eval", "Rust Eval", "Integer division and remainder, casts, float printing, wrapping and checked arithmetic: what does println! show?" + NOTE,
             "What does it print?", 16, "type", 3.5, 14.0, make_rs=Pool(basics.EVAL), group=GROUP,
             concepts=("integer", "division", "type-conversion", "cast", "integer overflow", "floating-point", "shadowing", "expression"),
             oracle="value"),
    Activity("rs_own", "Move, Copy, Clone", "Programs that compile: who owns the value after a move, a copy, a clone or a borrow? What does it print?" + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_rs=Pool(own.OWN), group=GROUP,
             concepts=("ownership", "move semantics", "clone", "borrowing", "reference", "reference counting", "copy"),
             oracle="value"),
    Activity("rs_borrow", "Borrow Check", "Would rustc accept it and would it run without a panic? Use after move, overlapping borrows, out-of-range indexes." + NOTE,
             "Does it compile and run without a panic?", 16, "pick", 4.5, 18.0, make_rs=Pool(own.BORROW), group=GROUP,
             choices=("fine", "error"),
             concepts=("borrow checker", "ownership", "borrowing", "move semantics", "mutability", "lifetime", "panic"),
             oracle="error"),
    Activity("rs_match", "Match & Option", "match, if let, let else, Option and Result: what does it print? Debug output shows Some(3), None, Ok(2)." + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_rs=Pool(data.MATCH), group=GROUP,
             concepts=("pattern matching", "option", "result", "enum", "guard", "error handling", "unwrap"),
             oracle="value"),
    Activity("rs_iter", "Iterator Chains", "map, filter, sum, fold, zip, windows and friends, and iterators that do nothing until consumed: what does it print?" + NOTE,
             "What does it print?", 14, "type", 5.0, 20.0, make_rs=Pool(data.ITER), group=GROUP,
             concepts=("iterator", "closure", "lazy evaluation", "range", "vector", "collect", "fold"),
             oracle="value"),
    Activity("rs_string", "Strings & Formatting", "len counts bytes, padding and precision, hex and binary: what exact line does println! write?" + NOTE,
             "What exact line does it print?", 14, "type", 4.0, 16.0, make_rs=Pool(basics.STRINGS), group=GROUP,
             concepts=("string", "formatting", "padding", "hexadecimal", "character", "slice", "byte"),
             oracle="value"),
    Activity("rs_struct", "Structs, Enums & Traits", "Small complete programs: impl blocks, traits, Display, derive, comparisons and generics. What does it print?" + " The code is a complete program with fn main.",
             "What does it print?", 12, "type", 6.0, 24.0, make_rs=Pool(types.STRUCT), group=GROUP,
             concepts=("struct", "enum", "trait", "method", "generic", "derive", "implementation"),
             oracle="value"),
    Activity("rs_collect", "Vec & Maps", "Vec, slices, BTreeMap, BTreeSet and VecDeque operations: what does it print? Map output is sorted." + NOTE,
             "What does it print?", 14, "type", 5.0, 20.0, make_rs=Pool(data.COLLECT), group=GROUP,
             concepts=("vector", "slice", "map", "set", "sorting", "collection", "deque"),
             oracle="value"),
)
