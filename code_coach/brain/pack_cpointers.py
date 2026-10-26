"""The C Pointers and Structs Pack: eight C-only activities about the part of C that makes it C - addresses, what a
pointer lets you write, arrays walked by pointer, pointers to pointers, structs copied and initialised, strings as
pointers into char arrays, and pointers to functions.

Pointer Says, Swap & Out, Walk the Array, Pointer to Pointer, Struct Copy, Struct Init, String Pointers, Function
Pointers. Each has only a C generator (`make_c`), built from 40 or more templates (`_cpointers_basics.py`,
`_cpointers_walk.py`, `_cpointers_structs.py`, `_cpointers_text.py`; the memory models are in `_cpointers_model.py`, the
integers and printf in `_c_model.py`). Every answer is modelled by hand, and tests/test_brain_packs.py compiles every
template with the real compilers (tests/c_oracle.py): clang `-O0` and `-O2` (signed and unsigned `char`), MSVC `/Od`
where installed, which must all print the same, and the undefined-behaviour sanitizer must find nothing. So nothing
here prints an address, reads out of bounds, uses a dangling pointer, or asks for `sizeof` of a struct (padding).

THE ITEM CONVENTION (see `_c_model.py`): `stdio.h stdint.h string.h stddef.h` are always included; the code is the BODY
of `main` unless it mentions `main(` (then a complete program: types, helper functions, `int main(void)`); it prints
its own answer with `printf`, and the answer is its output with the whitespace at both ends cut off. `oracle`: "value".
"""

from __future__ import annotations

from . import _cpointers_basics as basics
from . import _cpointers_structs as structs
from . import _cpointers_text as strings
from . import _cpointers_walk as walk
from ._model import Pool
from .items import Activity

GROUP = "C pointers and structs"

#: What every blurb says about the program around the code.
NOTE = " The headers are included; without a main, the code is the body of main."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("cp_says", "Pointer Says", "&x, *p, p = &y: what do the variables hold after writing through a pointer?" + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_c=Pool(basics.SAYS), group=GROUP,
             concepts=("pointer", "dereference", "address", "alias", "null-pointer", "const"),
             oracle="value"),
    Activity("cp_swap", "Swap & Out", "Functions that take addresses: what do the caller's variables hold afterwards?" + NOTE,
             "What does it print?", 10, "type", 7.0, 28.0, make_c=Pool(basics.OUTS), group=GROUP,
             concepts=("pointer", "pass-by-reference", "out-parameter", "pass-by-value", "function", "address"),
             oracle="value"),
    Activity("cp_walk", "Walk the Array", "Pointer arithmetic inside one array: p++, p - a, *p++, end pointers, rows." + NOTE,
             "What does it print?", 12, "type", 6.0, 24.0, make_c=Pool(walk.WALK), group=GROUP,
             concepts=("pointer", "pointer-arithmetic", "array", "index", "dereference", "end-pointer"),
             oracle="value"),
    Activity("cp_pp", "Pointer to Pointer", "int **, arrays of pointers, tables of strings, const placement: what prints?" + NOTE,
             "What does it print?", 12, "type", 6.0, 24.0, make_c=Pool(walk.PTRPTR), group=GROUP,
             concepts=("pointer", "pointer-to-pointer", "array-of-pointers", "dereference", "string", "const"),
             oracle="value"),
    Activity("cp_copy", "Struct Copy", "Struct assignment copies, -> follows a pointer, structs go in and out of functions." + NOTE,
             "What does it print?", 12, "type", 6.0, 24.0, make_c=Pool(structs.COPY), group=GROUP,
             concepts=("struct", "member", "struct-copy", "arrow-operator", "pointer", "pass-by-value", "linked-list"),
             oracle="value"),
    Activity("cp_init", "Struct Init", "Partial and designated initialisers, compound literals, arrays inside structs." + NOTE,
             "What does it print?", 12, "type", 6.0, 24.0, make_c=Pool(structs.INIT), group=GROUP,
             concepts=("struct", "initialization", "designated-initializer", "compound-literal", "member", "array", "zero-initialization"),
             oracle="value"),
    Activity("cp_str", "String Pointers", "A char * into a char array or a literal: p++, *p++, a NUL in the middle, strchr." + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_c=Pool(strings.STR), group=GROUP,
             concepts=("string", "pointer", "char-array", "null-terminator", "string-length", "pointer-arithmetic", "string-literal"),
             oracle="value"),
    Activity("cp_fptr", "Function Pointers", "Tables of functions, callbacks, a function that returns a function: what prints?" + NOTE,
             "What does it print?", 10, "type", 7.0, 28.0, make_c=Pool(strings.FPTR), group=GROUP,
             concepts=("function-pointer", "callback", "function", "pointer", "typedef", "array", "struct"),
             oracle="value"),
)
