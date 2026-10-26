"""The C Strings and Memory Pack: eight C-only activities about char arrays and the string.h functions that work on them.

strlen vs sizeof, Copy & Cat, Compare, Find in String, Buffer Fill, snprintf Says, Char Class, Parse by Hand.
Each has only a C generator (`make_c`), built from 40+ templates, so they are played under the C language of the app's
picker and never listed under another one. The templates are in `_cstrings_len.py`, `_cstrings_compare.py`,
`_cstrings_memory.py` and `_cstrings_chars.py`; every answer is modelled by hand (`_cstrings_model.py`: a `Buf` that behaves
like `char b[n]`, plus `_c_model.py`'s printf) and tests/test_brain_packs.py compiles every template with the real
compilers in batches (tests/c_oracle.py): clang -O0 / -O2 with signed and unsigned `char`, MSVC /Od where installed, all of
which must print the same, with the undefined-behaviour sanitizer finding nothing.

Only the four fixed headers are there (`stdio.h stdint.h string.h stddef.h`), so there is no `toupper`, `isdigit`, `atoi` or
`strtol` in this pack: classification and parsing are written out by hand, which is the point of the last two activities.
The buffers are always big enough and NUL-terminated, nothing is read before it is written, and no copy overlaps (memmove
is the only function used on overlapping bytes). Same item convention as the C core pack (see `_c_model.py`).
"""

from __future__ import annotations

from . import _cstrings_chars as chars
from . import _cstrings_compare as compare
from . import _cstrings_len as length
from . import _cstrings_memory as memory
from ._model import Pool
from .items import Activity

GROUP = "C strings and memory"

#: What every C blurb says about the program around the code.
NOTE = " The headers are included; the code is the body of main."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("cs_len", "strlen vs sizeof", "Letters or bytes? strlen stops at the NUL, sizeof counts the whole array." + NOTE,
             "What does it print?", 14, "type", 5.0, 20.0, make_c=Pool(length.LENGTHS), group=GROUP,
             concepts=("string-length", "sizeof", "null-terminator", "string", "array", "buffer", "character"),
             oracle="value"),
    Activity("cs_copy", "Copy & Cat", "What is in the buffer after strcpy, strncpy, strcat, strncat, memcpy and memmove?" + NOTE,
             "What does it print?", 12, "type", 6.0, 24.0, make_c=Pool(length.COPIES), group=GROUP,
             concepts=("strcpy", "strcat", "strncpy", "memcpy", "memmove", "buffer", "null-terminator", "string"),
             oracle="value"),
    Activity("cs_compare", "Compare", "strcmp, strncmp and memcmp: below, equal or above? Only the sign counts: -1, 0 or 1." + NOTE,
             "What does it print?", 12, "type", 5.0, 20.0, make_c=Pool(compare.COMPARE), group=GROUP,
             concepts=("strcmp", "string-comparison", "ascii", "lexicographic-order", "memcmp", "pointer", "string"),
             oracle="value"),
    Activity("cs_find", "Find in String", "Where is it? strchr, strstr, strspn and friends, as an offset, never an address." + NOTE,
             "What does it print?", 12, "type", 6.0, 24.0, make_c=Pool(compare.FIND), group=GROUP,
             concepts=("strchr", "strstr", "pointer-arithmetic", "null-pointer", "strtok", "string", "index"),
             oracle="value"),
    Activity("cs_fill", "Buffer Fill", "memset, memcpy and memmove on bytes: what is in the array afterwards?" + NOTE,
             "What does it print?", 12, "type", 6.0, 24.0, make_c=Pool(memory.FILLS), group=GROUP,
             concepts=("memset", "memcpy", "memmove", "buffer", "byte", "array", "initialization"),
             oracle="value"),
    Activity("cs_snprintf", "snprintf Says", "snprintf into a buffer of a given size: what does it return, and what is in the buffer?" + NOTE,
             "What exact line does it print?", 12, "type", 6.0, 24.0, make_c=Pool(memory.SNPRINTF), group=GROUP,
             concepts=("snprintf", "printf", "format-specifier", "buffer", "truncation", "padding", "string-length"),
             oracle="value"),
    Activity("cs_class", "Char Class", "No ctype.h here: is it a letter, a digit, which case? ASCII arithmetic by hand." + NOTE,
             "What does it print?", 14, "type", 5.0, 20.0, make_c=Pool(chars.CLASSES), group=GROUP,
             concepts=("ascii", "character", "char-arithmetic", "unsigned", "bitwise-operator", "bit-mask", "overflow"),
             oracle="value"),
    Activity("cs_parse", "Parse by Hand", "Loops over a char array: parse a number, count, reverse, check. What comes out?" + NOTE,
             "What does it print?", 10, "type", 7.0, 28.0, make_c=Pool(chars.PARSES), group=GROUP,
             concepts=("string", "loop", "ascii", "parsing", "null-terminator", "array", "pointer"),
             oracle="value"),
)
