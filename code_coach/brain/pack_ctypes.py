"""The C types and preprocessor pack: eight C-only activities about what the compiler does BEFORE and AROUND the
arithmetic - macros, the sizes of types, conversions, enums, typedefs, switch, recursion, storage and linkage.

Macro Trap, Type Size, Convert It, Enum Value, Typedef Reads, Switch Path, Recursion, Storage & Linkage.
Each has only a C generator (`make_c`), built from 40+ templates (`_ctypes_*.py`, the models `_ctypes_model.py` and
`_c_model.py`), so they are played under the C language of the app's picker and never listed under another one. Every
answer is modelled by hand and tests/test_brain_packs.py compiles every template with the real compilers (clang
`-O0` signed `char`, clang `-O2` unsigned `char`, MSVC `/Od`, all must agree, the warnings are linted and the
undefined-behaviour sanitizer must find nothing: tests/c_oracle.py).

THE ITEM CONVENTION is the C core pack's (see `_c_model.py`): `stdio.h stdint.h string.h stddef.h` are always included;
the code is the BODY of `main` unless it mentions `main(` (then a complete program); it prints its own answer with
`printf` and the answer is its output with the whitespace at both ends cut off. `oracle`: "value". Anything that needs
a `#define` is a complete program, so it is its own translation unit.
"""

from __future__ import annotations

from . import _ctypes_enum as enum
from . import _ctypes_flow as flow
from . import _ctypes_macro as macro
from . import _ctypes_size as size
from . import _ctypes_store as store
from ._model import Pool
from .items import Activity

GROUP = "C types and preprocessor"

#: What every C blurb says about the program around the code.
NOTE = " The headers are included; the code is the body of main unless it has its own main."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("ct_macro", "Macro Trap", "Macros paste text, they do not calculate: what does it print?" + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_c=Pool(macro.MACROS), group=GROUP,
             concepts=("macro", "preprocessor", "define", "stringify", "token-pasting", "conditional-compilation",
                       "precedence", "side-effect"),
             oracle="value"),
    Activity("ct_sizeof", "Type Size", "How many bytes? sizeof of types, arrays, strings and expressions." + NOTE,
             "What does it print?", 14, "type", 3.5, 14.0, make_c=Pool(size.SIZES), group=GROUP,
             concepts=("sizeof", "byte", "fixed-width-integer", "array", "string-length", "null-terminator", "struct",
                       "padding", "integer-promotion"),
             oracle="value"),
    Activity("ct_convert", "Convert It", "Implicit conversions and casts: what does printf show?" + NOTE,
             "What does it print?", 14, "type", 4.5, 18.0, make_c=Pool(size.CONVERT), group=GROUP,
             concepts=("type-conversion", "cast", "integer-promotion", "truncation", "unsigned", "floating-point", "character",
                       "integer-division"),
             oracle="value"),
    Activity("ct_enum", "Enum Value", "Enumerators are numbered constants: what number is it, and what does it print?" + NOTE,
             "What does it print?", 14, "type", 4.0, 16.0, make_c=Pool(enum.ENUMS), group=GROUP,
             concepts=("enum", "enumerator", "constant", "switch", "bit-flag", "array", "index"),
             oracle="value"),
    Activity("ct_typedef", "Typedef Reads", "A typedef is another name for a type: read it, then say what prints." + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_c=Pool(enum.TYPEDEFS), group=GROUP,
             concepts=("typedef", "struct", "function-pointer", "pointer", "array", "sizeof", "callback", "pass-by-value"),
             oracle="value"),
    Activity("ct_switch", "Switch Path", "Follow the switch: which cases run? No break means the next case runs too." + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_c=Pool(flow.SWITCHES), group=GROUP,
             concepts=("switch", "case", "default", "fallthrough", "break", "continue", "loop"),
             oracle="value"),
    Activity("ct_recurse", "Recursion", "A function that calls itself: what value comes back, or what gets printed?" + NOTE,
             "What does it print?", 10, "type", 6.0, 24.0, make_c=Pool(store.RECURSE), group=GROUP,
             concepts=("recursion", "base-case", "call-stack", "function", "factorial", "fibonacci", "static-variable"),
             oracle="value"),
    Activity("ct_storage", "Storage & Linkage", "Static locals, globals, extern, prototypes and _Bool: what prints?" + NOTE,
             "What does it print?", 10, "type", 6.0, 24.0, make_c=Pool(store.STORAGE), group=GROUP,
             concepts=("static-variable", "global-variable", "extern", "linkage", "function-prototype", "shadowing", "initialization",
                       "boolean"),
             oracle="value"),
)
