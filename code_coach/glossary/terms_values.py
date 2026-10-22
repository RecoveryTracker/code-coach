"""Words about values: truthy and falsy, booleans, types, numbers, strings, copies."""

from __future__ import annotations

from .entry import Entry, both

# What Python and JavaScript each treat as false, as source expressions. tests/test_glossary.py runs
# every one through bool() / Boolean(), so a wrong item fails there.
PY_FALSE = ("False", "None", "0", "0.0", "0j", '""', "[]", "()", "{}", "set()", "range(0)")
PY_TRUE = ('"0"', '"False"', '" "', "[0]", "[[]]", "-1", "0.1", 'float("nan")')
JS_FALSE = ("false", "0", "-0", "0n", '""', "null", "undefined", "NaN")
JS_TRUE = ('"0"', '"false"', '" "', "[]", "{}", "-1", "Infinity", "() => {}")

_PY_TRUTHY_DETECT = (
    r"\b(?:if|elif|while)\s+(?:not\s+)?[A-Za-z_][\w.]*(?:\([^()]*\))?\s*:",
    r"\bnot\b",
    r"\bbool\(",
    r"\b(?:and|or)\b",
    r"\bif\s+[A-Za-z_][\w.]*\s+else\b",
)
_JS_TRUTHY_DETECT = (
    r"\b(?:if|while)\s*\(\s*!*\s*[A-Za-z_$][\w$.]*(?:\([^()]*\))?\s*\)",
    r"(?<![!=<>])!(?!=)",
    r"\bBoolean\(",
    r"&&|\|\|",
    r"[\w$.\])]\s*\?(?![?.])",
)

TERMS: list[Entry] = [
    *both(
        "falsy",
        "Falsy",
        "A value that counts as false when the language needs a yes-or-no answer (in an if or a while), "
        "even though it is not the actual false value.",
        see=("truthy", "boolean", "condition"),
        priority=90,
        aka=("falsey", "false-y"),
        python=dict(
            rules=(
                "These are falsy: False, None, 0, 0.0, 0j, '' (the empty string), [] (an empty list), "
                "() (an empty tuple), {} (an empty dict), set() (an empty set) and range(0).",
                "Nothing else built in is falsy. 'False' and '0' are not empty, so they are truthy.",
                "A class you write can decide for itself with __bool__, or else with __len__ (a length of 0 is falsy).",
                "bool(x) shows which side a value is on; 'not x' flips it.",
            ),
            counts_false=PY_FALSE,
            counts_true=PY_TRUE,
            detect=_PY_TRUTHY_DETECT + (r"\bNone\b",),
            example="""
                items = []
                if not items:
                    print("nothing in the list")
                print(bool(0), bool("0"))
            """,
            out="nothing in the list\nFalse True",
        ),
        javascript=dict(
            rules=(
                "There are exactly eight falsy values: false, 0, -0, 0n (a zero BigInt), '' (an empty "
                "string), null, undefined and NaN.",
                "Everything else is truthy - including '0', 'false', [] (an empty array) and {} (an empty "
                "object). That is different from Python, where empty containers are falsy.",
                "Boolean(x) or !!x shows which side a value is on; !x flips it.",
                "One old browser leftover, document.all, is falsy too. You will never need it.",
            ),
            counts_false=JS_FALSE,
            counts_true=JS_TRUE,
            detect=_JS_TRUTHY_DETECT + (r"\b(?:null|undefined)\b",),
            example="""
                const items = [];
                if (!items.length) {
                  console.log("nothing in the array");
                }
                console.log(Boolean(0), Boolean("0"), Boolean([]));
            """,
            out="nothing in the array\nfalse true true",
        ),
    ),
    *both(
        "truthy",
        "Truthy",
        "A value that counts as true when the language needs a yes-or-no answer (in an if or a while), "
        "even though it is not the actual true value.",
        see=("falsy", "boolean", "condition"),
        priority=90,
        aka=("truthiness", "truthy-ness"),
        python=dict(
            rules=(
                "Every value is truthy unless it is on the falsy list: False, None, zero, and anything empty.",
                "That means '0', 'False', [0], any non-empty container, any non-zero number (negative ones "
                "too) and even float('nan') are truthy.",
                "'if x:' means the same as 'if bool(x):'.",
            ),
            counts_false=PY_FALSE,
            counts_true=PY_TRUE,
            detect=_PY_TRUTHY_DETECT,
            example="""
                print(bool("0"), bool([0]), bool(-1), bool(float("nan")))
            """,
            out="True True True True",
        ),
        javascript=dict(
            rules=(
                "Every value is truthy unless it is one of the eight falsy values: false, 0, -0, 0n, '', "
                "null, undefined, NaN.",
                "So '0', 'false', [], {}, -1, Infinity and every function are truthy.",
                "'if (x)' means the same as 'if (Boolean(x))'.",
            ),
            counts_false=JS_FALSE,
            counts_true=JS_TRUE,
            detect=_JS_TRUTHY_DETECT,
            example="""
                console.log(Boolean("0"), Boolean([]), Boolean({}), Boolean(-1), Boolean(NaN));
            """,
            out="true true true true false",
        ),
    ),
    *both(
        "boolean",
        "Boolean",
        "A value that is either true or false, and nothing else. Comparisons give booleans, and an "
        "if decides with one.",
        see=("truthy", "falsy", "comparison"),
        priority=60,
        aka=("bool",),
        python=dict(
            rules=(
                "The two values are written True and False, with a capital letter.",
                "bool is a kind of int: True counts as 1 and False as 0, so True + True is 2.",
                "bool(x) turns any value into True or False by the truthy and falsy rules.",
            ),
            detect=(r"\b(?:True|False)\b", r"\bbool\("),
            example="""
                print(3 > 2, 3 < 2, True + True)
            """,
            out="True False 2",
        ),
        javascript=dict(
            rules=(
                "The two values are written true and false, all lowercase.",
                "Comparisons give a boolean; other values are only truthy or falsy until you ask "
                "Boolean(x).",
                "In arithmetic, true counts as 1 and false as 0: true + true is 2.",
            ),
            detect=(r"\b(?:true|false)\b", r"\bBoolean\("),
            example="""
                console.log(3 > 2, 3 < 2, typeof true, true + true);
            """,
            out="true false boolean 2",
        ),
    ),
    *both(
        "value",
        "Value",
        "A piece of data your program can hold and use, such as 5, 'hello' or a list. Variables store "
        "values, and expressions produce them.",
        see=("variable", "type", "expression"),
        priority=35,
        python=dict(
            rules=(
                "Every value has a type (int, str, list ...) that decides what you can do with it.",
                "Several names can point at the same value.",
            ),
            example="""
                x = 5
                print(x, type(x).__name__)
            """,
            out="5 int",
        ),
        javascript=dict(
            rules=(
                "Every value has a type (number, string, object ...) that decides what you can do with it.",
                "Several names can point at the same value.",
            ),
            example="""
                const x = 5;
                console.log(x, typeof x);
            """,
            out="5 number",
        ),
    ),
    *both(
        "type",
        "Type",
        "The kind a value is, which decides what you can do with it. Numbers can be added; text can "
        "be joined; lists can be looped over.",
        see=("type-conversion", "value", "string"),
        priority=60,
        aka=("data type", "datatype"),
        python=dict(
            rules=(
                "The basic types are int, float, str, bool, list, tuple, dict, set and NoneType.",
                "type(x) tells you a value's type; isinstance(x, int) asks whether it is one.",
                "Python does not guess: '5' + 3 is a TypeError, not 8 and not '53'.",
            ),
            detect=(r"\b(?:type|isinstance)\(",),
            example="""
                print(type(5).__name__, type("5").__name__, type([]).__name__, type(None).__name__)
            """,
            out="int str list NoneType",
        ),
        javascript=dict(
            rules=(
                "typeof gives 'number', 'string', 'boolean', 'undefined', 'object', 'function', 'bigint' or 'symbol'.",
                "typeof null is 'object' - an old mistake that was kept so old code would not break.",
                "Arrays are objects too, so typeof [] is 'object'; Array.isArray(x) tells arrays apart.",
            ),
            detect=(r"\btypeof\b", r"\binstanceof\b", r"\bArray\.isArray\("),
            example="""
                console.log(typeof 5, typeof "5", typeof [], typeof null, Array.isArray([]));
            """,
            out="number string object object true",
        ),
    ),
    *both(
        "type-conversion",
        "Type conversion",
        "Changing a value from one type to another, such as the text '5' to the number 5.",
        see=("type", "string", "concatenation"),
        priority=75,
        aka=("casting", "cast", "convert"),
        python=dict(
            aka=("casting", "cast", "convert", "type coercion", "coercion", "implicit conversion"),
            rules=(
                "You convert on purpose: int('5'), float('2.5'), str(5), bool(x), list('abc').",
                "Python mostly refuses to guess: '5' + 3 raises a TypeError. (Whole numbers mix with "
                "floats, and True counts as 1.)",
                "int('x') or int('2.5') raises a ValueError; int(2.9) cuts off the decimals and gives 2.",
            ),
            detect=(r"\b(?:int|float|str|bool|list|tuple|set|dict)\(",),
            example="""
                print(int("5") + 3, str(5) + "3", int(2.9), float("2.5"))
            """,
            out="8 53 2 2.5",
        ),
        javascript=dict(
            term="Coercion",
            definition="JavaScript quietly converting a value to another type to make an operation work, "
            "such as the text '5' to the number 5. (Doing it yourself, as in Number('5'), is type conversion.)",
            rules=(
                "+ with any string joins text: '5' + 3 is '53'.",
                "-, * and / turn strings into numbers: '5' - 3 is 2, and 'abc' - 3 is NaN.",
                "== converts before comparing ('5' == 5 is true); === never does.",
                "To convert yourself, use Number('5'), String(5), Boolean(x), parseInt('5px') or parseFloat('2.5').",
            ),
            aka=("type coercion", "implicit conversion", "type conversion", "casting"),
            detect=(
                r"\b(?:Number|String|Boolean|parseInt|parseFloat)\(",
                r"(?:\"\"|'')\s*[-*/+]\s*[\w(]|[\w)]\s*[-*/+]\s*(?:\"\"|'')",
            ),
            example="""
                console.log("5" + 3, "5" - 3, Number("5") + 3, "abc" - 3);
            """,
            out="53 2 8 NaN",
        ),
    ),
    *both(
        "string",
        "String",
        "A piece of text: letters, digits and symbols between quotes.",
        see=("concatenation", "index", "immutable"),
        priority=30,
        aka=("str", "text"),
        python=dict(
            rules=(
                "Single and double quotes mean the same: 'hi' and \"hi\". Triple quotes can span lines.",
                "len(s) counts characters; s[0] is the first one. Strings cannot be changed in place.",
                "Methods such as s.upper() and s.replace() give back a new string.",
            ),
            detect=(r"\"\"|''", r"\bstr\("),
            example="""
                s = "farm"
                print(len(s), s[0], s.upper(), s * 2)
            """,
            out="4 f FARM farmfarm",
        ),
        javascript=dict(
            rules=(
                "Single, double and backtick quotes all make strings; only backticks allow ${...} and "
                "several lines.",
                "s.length counts characters; s[0] is the first one. Strings cannot be changed in place.",
                "Methods such as s.toUpperCase() and s.replace() give back a new string.",
            ),
            detect=(r"\"\"|''|``", r"\bString\("),
            example="""
                const s = "farm";
                console.log(s.length, s[0], s.toUpperCase(), s.repeat(2));
            """,
            out="4 f FARM farmfarm",
        ),
    ),
    *both(
        "concatenation",
        "Concatenation",
        "Joining strings end to end to make one longer string.",
        see=("string", "type-conversion"),
        priority=55,
        aka=("concatenate", "joining strings"),
        python=dict(
            rules=(
                "'a' + 'b' is 'ab'. Both sides must be strings: 'a' + 1 is a TypeError (use str(1) or an f-string).",
                "A string times a whole number repeats it: 'ab' * 3 is 'ababab'.",
                "', '.join(list_of_strings) joins many strings with a separator.",
            ),
            see=("string", "type-conversion", "f-string"),
            detect=(
                r"(?:\"\"|'')\s*\+|\+\s*(?:\"\"|'')|\bstr\([^)]*\)\s*\+",
                r"\.join\(",
            ),
            example="""
                print("farm" + "er", "ab" * 3, ", ".join(["a", "b"]))
            """,
            out="farmer ababab a, b",
        ),
        javascript=dict(
            rules=(
                "'a' + 'b' is 'ab'. If either side is a string, + joins, so '5' + 3 is '53' and 1 + 2 + '3' is '33'.",
                "'ab'.repeat(3) is 'ababab'; * does not repeat strings.",
                "array.join(', ') joins many strings with a separator. A template literal is often neater.",
            ),
            see=("string", "type-conversion", "template-literal"),
            detect=(
                r"(?:\"\"|''|``)\s*\+|\+\s*(?:\"\"|''|``)",
                r"\.join\(",
            ),
            example="""
                console.log("farm" + "er", "5" + 3, 1 + 2 + "3", ["a", "b"].join(", "));
            """,
            out="farmer 53 33 a, b",
        ),
    ),
    *both(
        "integer",
        "Integer",
        "A whole number with no decimal part: 7, 0 or -3.",
        see=("float", "floor-division", "type"),
        priority=25,
        aka=("int",),
        python=dict(
            rules=(
                "Python integers have no size limit: 2 ** 100 works exactly.",
                "int(x) converts to an integer, cutting off any decimals (int(-2.9) is -2).",
                "A / B always gives a float; use // for a whole-number answer.",
            ),
            detect=(r"\bint\(", r"//"),
            example="""
                print(2 ** 70, int(-2.9), type(7).__name__)
            """,
            out="1180591620717411303424 -2 int",
        ),
        javascript=dict(
            rules=(
                "JavaScript has no separate integer type: 7 and 7.0 are the same number, stored as a float.",
                "Whole numbers are exact only up to 2 ** 53 - 1 (Number.MAX_SAFE_INTEGER); beyond that use BigInt, written 10n.",
                "Number.isInteger(x) asks whether x is a whole number; parseInt('7px') reads one from text.",
            ),
            detect=(r"\bparseInt\(", r"\bNumber\.isInteger\(", r"\d+n\b"),
            example="""
                console.log(7 === 7.0, 2 ** 53 + 1, 2n ** 70n, Number.isInteger(7.5));
            """,
            out="true 9007199254740992 1180591620717411303424n false",
        ),
    ),
    *both(
        "float",
        "Float",
        "A number with a decimal point, stored approximately. The name comes from 'floating-point'.",
        see=("float-precision", "integer", "rounding"),
        priority=35,
        aka=("floating point", "decimal", "double"),
        python=dict(
            rules=(
                "3.0 is a float even though it looks whole, and 3.0 == 3 is True.",
                "/ always gives a float, even when it divides exactly: 4 / 2 is 2.0.",
                "Floats are stored in binary, so most decimals are stored slightly off (see float precision).",
            ),
            detect=(r"\d\.\d|\bfloat\(", r"[\w)]\s*/(?!/)\s*[\w(]"),
            example="""
                print(4 / 2, type(4 / 2).__name__, 3.0 == 3)
            """,
            out="2.0 float True",
        ),
        javascript=dict(
            rules=(
                "Every number is a float: there is one number type, so 3.0 === 3 is true.",
                "4 / 2 is 2, printed without '.0', because JavaScript does not show the point on whole values.",
                "Floats are stored in binary, so most decimals are stored slightly off (see float precision).",
            ),
            detect=(r"\d\.\d|\bparseFloat\(|\.toFixed\(", r"[\w)]\s*/(?!/)\s*[\w(]"),
            example="""
                console.log(4 / 2, 3.0 === 3, 7 / 2);
            """,
            out="2 true 3.5",
        ),
    ),
    *both(
        "float-precision",
        "Float precision",
        "Computers store decimals in binary, which cannot hold most of them exactly, so tiny errors "
        "appear: 0.1 + 0.2 is not exactly 0.3.",
        see=("float", "rounding", "comparison"),
        priority=70,
        aka=("floating point error", "precision"),
        python=dict(
            rules=(
                "Never test floats with ==. Compare with a tolerance: math.isclose(a, b), or round both first.",
                "Whole numbers (ints) are exact, so count money in cents rather than dollars.",
                "The decimal module and fractions.Fraction give exact decimal and fraction maths when you need it.",
            ),
            detect=(r"\d\.\d+\s*[-+*/]\s*\d*\.?\d+", r"\d\.\d+[^\n]*==|==[^\n]*\d\.\d+"),
            example="""
                import math
                print(0.1 + 0.2, 0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))
            """,
            out="0.30000000000000004 False True",
        ),
        javascript=dict(
            rules=(
                "Never test floats with ===. Compare with a tolerance: Math.abs(a - b) < 1e-9.",
                "Whole numbers are exact up to 2 ** 53, so count money in cents rather than dollars.",
                "x.toFixed(2) rounds for display but returns a string.",
            ),
            detect=(r"\d\.\d+\s*[-+*/]\s*\d*\.?\d+", r"\d\.\d+[^\n]*===?|===?[^\n]*\d\.\d+"),
            example="""
                console.log(0.1 + 0.2, 0.1 + 0.2 === 0.3, Math.abs(0.1 + 0.2 - 0.3) < 1e-9);
            """,
            out="0.30000000000000004 false true",
        ),
    ),
    *both(
        "rounding",
        "Rounding",
        "Replacing a number with a nearby simpler one, such as dropping its decimals.",
        see=("float", "floor-division", "float-precision"),
        priority=55,
        aka=("round", "truncate", "floor", "ceil"),
        python=dict(
            rules=(
                "round(x) rounds half-way cases to the nearest EVEN number: round(2.5) is 2 and round(3.5) is 4.",
                "int(x) cuts off the decimals toward zero (int(-2.9) is -2); math.floor goes down (-3) and math.ceil goes up (-2).",
                "round(x, 2) keeps two decimals, and floats' tiny errors can still show.",
            ),
            detect=(r"\bround\(", r"\bmath\.(?:floor|ceil|trunc)\(", r"\bint\("),
            example="""
                import math
                print(round(2.5), round(3.5), int(-2.9), math.floor(-2.9), math.ceil(-2.1))
            """,
            out="2 4 -2 -3 -2",
        ),
        javascript=dict(
            rules=(
                "Math.round(x) rounds half-way cases UP toward positive infinity: Math.round(2.5) is 3 and Math.round(-2.5) is -2.",
                "Math.trunc cuts off the decimals (-2.9 gives -2); Math.floor goes down (-3); Math.ceil goes up (-2).",
                "x.toFixed(2) keeps two decimals but returns a string.",
            ),
            detect=(r"\bMath\.(?:round|floor|ceil|trunc)\(", r"\.toFixed\(", r"\bparseInt\("),
            example="""
                console.log(Math.round(2.5), Math.round(-2.5), Math.trunc(-2.9), Math.floor(-2.9), (3.14159).toFixed(2));
            """,
            out="3 -2 -2 -3 3.14",
        ),
    ),
    *both(
        "floor-division",
        "Floor division",
        "Dividing and rounding the answer down to the next whole number at or below it.",
        see=("modulo", "integer", "rounding"),
        priority=70,
        aka=("//", "integer division"),
        python=dict(
            rules=(
                "7 // 2 is 3. Floor division goes DOWN, so -7 // 2 is -4, not -3.",
                "It pairs with %: (a // b) * b + a % b is always a.",
                "With a float on either side the answer is a float: 7.5 // 2 is 3.0.",
            ),
            detect=(r"//",),
            example="""
                print(7 // 2, -7 // 2, 7 / 2, 7.5 // 2)
            """,
            out="3 -4 3.5 3.0",
        ),
        javascript=dict(
            definition="Dividing and rounding the answer down to the next whole number at or below it. "
            "JavaScript has no operator for it: write Math.floor(a / b).",
            rules=(
                "Math.floor(7 / 2) is 3, and Math.floor(-7 / 2) is -4 (it goes down).",
                "Math.trunc cuts toward zero instead, so Math.trunc(-7 / 2) is -3.",
                "// in JavaScript starts a comment; it is not division.",
            ),
            detect=(r"\bMath\.(?:floor|trunc)\(",),
            example="""
                console.log(Math.floor(7 / 2), Math.floor(-7 / 2), Math.trunc(-7 / 2), 7 / 2);
            """,
            out="3 -4 -3 3.5",
        ),
    ),
    *both(
        "modulo",
        "Modulo",
        "The % operator: the remainder left over after dividing. 7 % 3 is 1 because 3 goes into 7 twice, leaving 1.",
        see=("floor-division", "operator"),
        priority=65,
        aka=("%", "remainder"),
        python=dict(
            rules=(
                "The result has the same sign as the number on the RIGHT: -7 % 3 is 2.",
                "n % 2 == 0 tests for an even number; n % 10 is the last digit.",
                "x % 0 raises a ZeroDivisionError.",
            ),
            detect=(r"%",),
            example="""
                print(7 % 3, -7 % 3, 10 % 5, 8 % 2 == 0)
            """,
            out="1 2 0 True",
        ),
        javascript=dict(
            rules=(
                "The result has the same sign as the number on the LEFT: -7 % 3 is -1 (Python gives 2).",
                "n % 2 === 0 tests for an even number; n % 10 is the last digit.",
                "x % 0 is NaN.",
            ),
            detect=(r"%",),
            example="""
                console.log(7 % 3, -7 % 3, 10 % 5, 8 % 2 === 0, 5 % 0);
            """,
            out="1 -1 0 true NaN",
        ),
    ),
    *both(
        "exponent",
        "Exponent",
        "The ** operator: raise a number to a power. 2 ** 3 is 2 times itself three times, which is 8.",
        see=("operator", "precedence"),
        priority=50,
        aka=("**", "power"),
        python=dict(
            rules=(
                "** goes right to left: 2 ** 3 ** 2 is 2 ** 9, which is 512.",
                "** binds tighter than a minus in front of it: -2 ** 2 is -4.",
                "^ is NOT a power in Python: it is bitwise XOR, so 2 ^ 3 is 1.",
            ),
            detect=(r"\*\*", r"\bpow\("),
            example="""
                print(2 ** 10, 2 ** 3 ** 2, -2 ** 2, 2 ^ 3)
            """,
            out="1024 512 -4 1",
        ),
        javascript=dict(
            rules=(
                "** goes right to left: 2 ** 3 ** 2 is 2 ** 9, which is 512.",
                "-2 ** 2 is a SyntaxError; write (-2) ** 2 or -(2 ** 2).",
                "^ is NOT a power in JavaScript: it is bitwise XOR, so 2 ^ 3 is 1. Math.pow(2, 3) also works.",
            ),
            detect=(r"\*\*", r"\bMath\.pow\("),
            example="""
                console.log(2 ** 10, 2 ** 3 ** 2, (-2) ** 2, 2 ^ 3);
            """,
            out="1024 512 4 1",
        ),
    ),
    *both(
        "mutable",
        "Mutable",
        "Able to be changed in place. Changing a mutable value (mutating it) changes it for every name that points at it.",
        see=("immutable", "reference"),
        priority=75,
        aka=("mutate", "mutation", "mutating", "in place"),
        python=dict(
            rules=(
                "Mutable: list, dict and set (and objects you make).",
                "Methods like append, pop, sort, update and item assignment (a[0] = 1) mutate the value.",
                "Two names pointing at one list see each other's changes.",
            ),
            detect=(r"\.(?:append|extend|insert|pop|remove|sort|reverse|clear|update|add|discard|setdefault)\(",
                    r"\w\[[^\]\n]+\]\s*=(?!=)"),
            example="""
                a = [1]
                b = a
                b.append(2)
                print(a)
            """,
            out="[1, 2]",
        ),
        javascript=dict(
            rules=(
                "Mutable: arrays and objects.",
                "Methods like push, pop, sort and splice, and assigning to a property (o.x = 1), mutate the value.",
                "const only stops the NAME being reassigned; a const array can still be mutated.",
            ),
            detect=(r"\.(?:push|pop|shift|unshift|splice|sort|reverse|fill|set|add|delete|clear)\(",
                    r"[\w$\])]\s*\[[^\]\n]+\]\s*=(?!=)|[\w$]\.[\w$]+\s*=(?!=)"),
            example="""
                const a = [1];
                const b = a;
                b.push(2);
                console.log(a);
            """,
            out="[ 1, 2 ]",
        ),
    ),
    *both(
        "immutable",
        "Immutable",
        "Not able to be changed once made. To get a different value you make a new one.",
        see=("mutable", "string"),
        priority=60,
        aka=("immutability", "unchangeable"),
        python=dict(
            rules=(
                "Immutable: int, float, bool, str, tuple, frozenset and None.",
                "s.upper() or s.replace() leave s alone and return a new string.",
                "Trying s[0] = 'H' on a string is a TypeError.",
            ),
            detect=(r"\btuple\(|\bfrozenset\(", r"\.(?:upper|lower|strip|replace|title|capitalize)\("),
            example="""
                s = "hi"
                s.upper()
                print(s)
                try:
                    s[0] = "H"
                except TypeError:
                    print("strings cannot change")
            """,
            out="hi\nstrings cannot change",
        ),
        javascript=dict(
            rules=(
                "Immutable: numbers, strings, booleans, null, undefined, bigints and symbols.",
                "s.toUpperCase() or s.replace() leave s alone and return a new string.",
                "Object.freeze(obj) makes an object's own properties unchangeable (one level deep).",
            ),
            detect=(r"\.(?:toUpperCase|toLowerCase|trim|replace|replaceAll)\(", r"\bObject\.freeze\("),
            example="""
                let s = "hi";
                s.toUpperCase();
                console.log(s);
            """,
            out="hi",
        ),
    ),
    *both(
        "reference",
        "Reference",
        "How a variable holds a list, dict or object: not a copy of it, but a pointer to the one value. "
        "Assigning it to another name makes a second pointer to the same thing, not a copy.",
        see=("mutable", "assignment", "variable"),
        priority=65,
        aka=("alias", "copy", "pointer", "shallow copy"),
        python=dict(
            rules=(
                "b = a on a list or dict makes b and a the SAME object; change one and the other changes.",
                "Make a real (shallow) copy with a.copy(), list(a) or a[:].",
                "Numbers and strings can't change, so sharing them never causes this surprise.",
            ),
            detect=(
                r"^\s*[A-Za-z_]\w*\s*=\s*(?!None\b|True\b|False\b)[A-Za-z_]\w*\s*$",
                r"\.copy\(|\bcopy\.\w*copy\(",
            ),
            example="""
                a = [1, 2]
                b = a
                c = a.copy()
                a.append(3)
                print(b, c)
            """,
            out="[1, 2, 3] [1, 2]",
        ),
        javascript=dict(
            rules=(
                "const b = a on an array or object makes b and a the SAME object; change one and the other changes.",
                "Make a real (shallow) copy with [...a], a.slice() or { ...obj }.",
                "Numbers and strings can't change, so sharing them never causes this surprise.",
            ),
            detect=(
                r"^\s*(?:(?:let|const|var)\s+)?[A-Za-z_$][\w$]*\s*=\s*(?!null\b|true\b|false\b|undefined\b)[A-Za-z_$][\w$]*;?\s*$",
                r"\.slice\(\)|\[\s*\.\.\.\w+\s*\]|structuredClone\(",
            ),
            example="""
                const a = [1, 2];
                const b = a;
                const c = [...a];
                a.push(3);
                console.log(b, c);
            """,
            out="[ 1, 2, 3 ] [ 1, 2 ]",
        ),
    ),
]
