"""The Strings Pack: eight activities about text - case, splitting, finding, replacing, formatting, string maths.

Case & Trim, Split & Join, Find It, Replace It, Format It, String Math, Char
Codes, Text Check. Each has a Python and a JavaScript generator built from
many templates (Python's pool is the bigger: it is the language to practise).
The templates are in `_strings_py.py` and `_strings_js.py`; every answer in
them is modelled by hand, and tests/test_brain_packs.py runs every template
through the real Python and the real node. This file only wires the templates
into Activities (see the package docstring in __init__.py).
"""

from __future__ import annotations

from . import _strings_js as js
from . import _strings_py as py
from ._model import Pool
from .items import Activity

GROUP = "Strings"

ACTIVITIES: tuple[Activity, ...] = (
    Activity("str_case", "Case & Trim", "Capitals, small letters and stray spaces: what is left?",
             "What is the result?", 16, "type", 3.0, 12.0, Pool(js.CASE), make_py=Pool(py.CASE),
             group=GROUP, concepts=("string", "method", "case", "whitespace", "strip", "immutable"), oracle="value"),
    Activity("str_split", "Split & Join", "Cut text into pieces, or glue pieces together: what comes out?",
             "What is the result?", 14, "type", 3.5, 14.0, Pool(js.SPLIT), make_py=Pool(py.SPLIT),
             group=GROUP, concepts=("string", "split", "join", "list", "array", "separator"), oracle="value"),
    Activity("str_find", "Find It", "Where is it in the text, and how many times? Counting starts at 0.",
             "What is the result?", 16, "type", 3.0, 12.0, Pool(js.FIND), make_py=Pool(py.FIND),
             group=GROUP, concepts=("string", "index", "search", "substring", "method"), oracle="value"),
    Activity("str_replace", "Replace It", "Swap pieces of text for others: what does the string become?",
             "What is the result?", 16, "type", 3.0, 12.0, Pool(js.REPLACE), make_py=Pool(py.REPLACE),
             group=GROUP, concepts=("string", "replace", "substring", "method", "immutable"), oracle="value"),
    Activity("str_format", "Format It", "Pad, round and fill text into shape: what does it print?",
             "What is the result?", 12, "type", 4.0, 16.0, Pool(js.FORMAT), make_py=Pool(py.FORMAT),
             group=GROUP, concepts=("string", "format", "f-string", "padding", "precision", "rounding"),
             oracle="value"),
    Activity("str_math", "String Math", "Count, repeat and join text: how long, how many, what is left?",
             "What is the result?", 16, "type", 3.0, 12.0, Pool(js.MATH), make_py=Pool(py.MATH),
             group=GROUP, concepts=("string", "length", "concatenation", "operator", "type coercion"), oracle="value"),
    Activity("str_codes", "Char Codes", "Every character is a number: work with the codes and shift letters.",
             "What is the result?", 12, "type", 4.0, 16.0, Pool(js.CODES), make_py=Pool(py.CODES),
             group=GROUP, concepts=("character", "ascii", "string", "modulo", "function"), oracle="value"),
    Activity("str_check", "Text Check", "Is the statement about the text true? Left for no, right for yes.",
             "Is it true?", 16, "pick", 1.6, 6.5, Pool(js.CHECK), ("no", "yes"), make_py=Pool(py.CHECK),
             group=GROUP, concepts=("string", "comparison", "palindrome", "anagram", "boolean", "method"),
             oracle="value"),
)
