"""The C Core Pack: eight C-only activities about the language itself - integer arithmetic, printf, characters and
strings, bits, loops, arrays and pointers, operator order, scope and storage.

C Integer Math, printf Format, Char & String, Bits, Loop Trace, Array Reach, Operator Order, Scope & Storage.
Each has only a C generator (`make_c`), built from 40-55 templates, so they are played under the C language of the app's
picker and never listed under another one. The templates are in `_ccore_numbers.py`, `_ccore_text.py` and
`_ccore_flow.py`; every answer is modelled by hand with `_c_model.py`, and tests/test_brain_packs.py compiles every
template with the real compilers in batches (tests/c_oracle.py): clang `-O0` and `-O2` (and signed vs unsigned `char`),
MSVC `/Od` where installed, all of which must print the same thing, and the undefined-behaviour sanitizer must find
nothing. This file only wires the templates into Activities.

THE ITEM CONVENTION (see `_c_model.py`): `stdio.h stdint.h string.h stddef.h` are always included; the code is the BODY
of `main` unless it mentions `main(` (then it is a complete program: globals and helper functions first); it prints its
own answer with `printf`, and the answer is its output with the whitespace at both ends cut off. `oracle`: "value".
"""

from __future__ import annotations

from . import _ccore_flow as flow
from . import _ccore_numbers as numbers
from . import _ccore_text as text
from ._model import Pool
from .items import Activity

GROUP = "C core"

#: What every C blurb says about the program around the code.
NOTE = " The headers are included; the code is the body of main."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("c_int", "Integer Math", "Truncating division, wraparound, promotion: what does printf show?" + NOTE,
             "What does it print?", 16, "type", 3.5, 14.0, make_c=Pool(numbers.INTEGER), group=GROUP,
             concepts=("integer", "division", "modulo", "overflow", "unsigned", "type-conversion", "operator", "cast"),
             oracle="value"),
    Activity("c_printf", "printf Format", "Which exact line does printf write? Spaces count: type it as it is." + NOTE,
             "What exact line does it print?", 14, "type", 4.0, 16.0, make_c=Pool(numbers.PRINTF), group=GROUP,
             concepts=("printf", "format-specifier", "padding", "hexadecimal", "string", "character", "floating-point"),
             oracle="value"),
    Activity("c_string", "Char & String", "Characters are small numbers, strings end in a zero: what does it print?" + NOTE,
             "What does it print?", 14, "type", 4.0, 16.0, make_c=Pool(text.STRINGS), group=GROUP,
             concepts=("character", "string", "null-terminator", "escape-sequence", "array", "pointer", "string-length"),
             oracle="value"),
    Activity("c_bits", "Bits", "AND, OR, XOR, NOT and shifts: what does it print?" + NOTE,
             "What does it print?", 14, "type", 5.0, 20.0, make_c=Pool(numbers.BITS), group=GROUP,
             concepts=("bitwise-operator", "bit-shift", "bit-mask", "binary", "hexadecimal", "unsigned", "precedence"),
             oracle="value"),
    Activity("c_loop", "Loop Trace", "Follow the loop: the final value, or what it prints." + NOTE,
             "What does it print?", 10, "type", 6.0, 24.0, make_c=Pool(flow.LOOPS), group=GROUP,
             concepts=("loop", "for-loop", "while-loop", "break", "continue", "off-by-one", "iteration", "nested-loop"),
             oracle="value"),
    Activity("c_array", "Array Reach", "Arrays, sizeof and pointer arithmetic, strictly in bounds: what does it print?" + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_c=Pool(text.ARRAYS), group=GROUP,
             concepts=("array", "index", "pointer", "pointer-arithmetic", "sizeof", "multidimensional-array", "initialization"),
             oracle="value"),
    Activity("c_order", "Operator Order", "Precedence, associativity, short-circuit and side effects: what does it print?" + NOTE,
             "What does it print?", 14, "type", 4.0, 16.0, make_c=Pool(flow.ORDER), group=GROUP,
             concepts=("precedence", "associativity", "short-circuit", "ternary", "side-effect", "comma-operator", "expression"),
             oracle="value"),
    Activity("c_scope", "Scope & Storage", "Shadowing, static locals, globals, by value or by pointer: what prints?" + NOTE,
             "What does it print?", 10, "type", 6.0, 24.0, make_c=Pool(flow.SCOPE), group=GROUP,
             concepts=("scope", "static-variable", "global-variable", "local-variable", "pass-by-value", "pointer", "shadowing",
                       "function"),
             oracle="value"),
)
