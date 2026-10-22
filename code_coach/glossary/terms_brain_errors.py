"""Words the Brain Drills errors pack teaches: runtime errors, error messages, the named error types in Python and
JavaScript, tracebacks and stack traces, line numbers, bugs, debugging and typos."""

from __future__ import annotations

from .entry import Entry, both, js, py

TERMS: list[Entry] = [
    *both(
        "runtime-error",
        "Runtime error",
        "A mistake that only shows up while the program is running, as opposed to a syntax error, which stops it before it starts.",
        see=("exception", "syntax-error", "error-message", "traceback"),
        priority=55,
        aka=("runtime errors", "run-time error", "run time error", "crash", "crashes", "crashing", "error at runtime"),
        python=dict(
            rules=(
                "Lines that ran BEFORE the error have already done their work (and printed); lines after it never run.",
                "A syntax error is found before anything runs, so nothing at all is printed.",
                "It is raised as an exception, so try/except can catch it and carry on.",
            ),
            example="""
                print("start")
                try:
                    print(1 / 0)
                except ZeroDivisionError as e:
                    print("error:", e)
            """,
            out="start\nerror: division by zero",
        ),
        javascript=dict(
            rules=(
                "Lines that ran BEFORE the error have already done their work (and printed); lines after it never run.",
                "A syntax error is found before anything runs, so nothing at all is printed.",
                "It is thrown as an error object, so try/catch can catch it and carry on.",
            ),
            example="""
                console.log("start");
                try {
                  null.length;
                } catch (e) {
                  console.log(e.name + ": " + e.message);
                }
            """,
            out="start\nTypeError: Cannot read properties of null (reading 'length')",
        ),
    ),
    *both(
        "error-message",
        "Error message",
        "The text the language prints when something goes wrong. It names the kind of error and says what was wrong; read it first.",
        see=("runtime-error", "traceback", "line-number", "exception"),
        priority=50,
        aka=("error messages", "message", "error text", "exception message", "error output"),
        python=dict(
            rules=(
                "The form is 'ErrorName: what happened', such as IndexError: list index out of range.",
                "The LAST line of a traceback is the message; the lines above it say where.",
                "A KeyError's message is the missing key itself, quoted: KeyError: 'b'.",
            ),
            example="""
                try:
                    [1, 2][5]
                except IndexError as e:
                    print(type(e).__name__, "-", e)
                try:
                    {"a": 1}["b"]
                except KeyError as e:
                    print(type(e).__name__, e)
            """,
            out="IndexError - list index out of range\nKeyError 'b'",
        ),
        javascript=dict(
            rules=(
                "The form is 'ErrorName: what happened', such as ReferenceError: x is not defined.",
                "e.name is the kind of error and e.message the text; e.stack has both plus where it happened.",
                "Some messages name the thing: 'x is not a function' says which name was not a function.",
            ),
            example="""
                try {
                  undefinedName;
                } catch (e) {
                  console.log(e.name, "-", e.message);
                }
            """,
            out="ReferenceError - undefinedName is not defined",
        ),
    ),
    *both(
        "type-error",
        "TypeError",
        "The error for using a value of the wrong kind for what you are doing, such as adding text to a number or calling something that is not a function.",
        see=("exception", "error-message", "type", "type-conversion"),
        priority=60,
        aka=("type error", "typeerror", "wrong type"),
        python=dict(
            detect=(r"\bTypeError\b",),
            rules=(
                "'1' + 1 is a TypeError: Python will not guess whether you meant text or a number.",
                "Common causes: len(5), calling a number as a function, indexing None, comparing text with a number using <.",
                "The fix is usually converting on purpose: int('1') + 1 or '1' + str(1).",
            ),
            example="""
                try:
                    "1" + 1
                except TypeError as e:
                    print(e)
            """,
            out='can only concatenate str (not "int") to str',
        ),
        javascript=dict(
            detect=(r"\bTypeError\b",),
            rules=(
                "The classic: reading or calling something on undefined or null, such as user.name when user is undefined.",
                "Calling something that is not a function: (5)() is 'is not a function'.",
                "JavaScript does NOT raise it for '1' + 1: that quietly gives the text '11'.",
            ),
            example="""
                const user = undefined;
                try {
                  user.name;
                } catch (e) {
                  console.log(e.name, e.message);
                }
                console.log("1" + 1);
            """,
            out="TypeError Cannot read properties of undefined (reading 'name')\n11",
        ),
    ),
    *py(
        "name-error",
        "NameError",
        "The error for using a name that Python does not know: never assigned, misspelled, or made in a scope you are not in.",
        see=("variable", "scope", "typo", "exception"),
        priority=60,
        aka=("name error", "nameerror", "not defined", "undefined name", "unboundlocalerror"),
        detect=(r"\bNameError\b",),
        rules=(
            "The message names the culprit: name 'totl' is not defined.",
            "The two usual causes are a typo and using a variable before the line that makes it.",
            "A name made inside a function is not visible outside it, so using it there is a NameError.",
        ),
        example="""
            total = 1
            try:
                print(totl)
            except NameError as e:
                print(e)
        """,
        out="name 'totl' is not defined",
    ),
    *js(
        "reference-error",
        "ReferenceError",
        "The error for using a name that JavaScript does not know: never declared, misspelled, or used before its let or const line.",
        see=("variable", "scope", "typo", "exception"),
        priority=60,
        aka=("name error", "nameerror", "referenceerror", "reference error", "not defined", "is not defined", "temporal dead zone"),
        detect=(r"\bReferenceError\b",),
        rules=(
            "The message names the culprit: totl is not defined.",
            "The two usual causes are a typo and using a variable outside the scope it was made in.",
            "A let or const used before its declaration line is a ReferenceError too: Cannot access 'x' before initialization.",
        ),
        example="""
            try {
              console.log(totl);
            } catch (e) {
              console.log(e.name + ": " + e.message);
            }
            try {
              x;
              let x = 1;
            } catch (e) {
              console.log(e.message);
            }
        """,
        out="ReferenceError: totl is not defined\nCannot access 'x' before initialization",
    ),
    *py(
        "index-error",
        "IndexError",
        "The error for asking a list, tuple or string for a position that does not exist.",
        see=("index", "slice", "off-by-one", "negative-index"),
        priority=60,
        aka=("index error", "indexerror", "index out of range", "list index out of range", "out of range"),
        detect=(r"\bIndexError\b",),
        rules=(
            "A list of n items has the positions 0 to n-1 (and -1 to -n); anything else is an IndexError.",
            "It is the usual sign of an off-by-one mistake, such as using len(a) as a position.",
            "Slices never raise it: a[3:] and a[1:10] quietly give a shorter list.",
        ),
        example="""
            a = [1, 2, 3]
            try:
                a[3]
            except IndexError as e:
                print(e)
            print(a[3:], a[1:10])
        """,
        out="list index out of range\n[] [2, 3]",
    ),
    *js(
        "index-error",
        "Index out of range",
        "JavaScript has no IndexError: asking an array or string for a position that does not exist quietly gives undefined.",
        see=("index", "undefined", "off-by-one", "negative-index"),
        priority=60,
        aka=("index error", "indexerror", "out of range", "index out of bounds", "out of bounds"),
        rules=(
            "arr[5] on a three-item array is undefined, with no error, and so are arr[-1] and 'abc'[9].",
            "The mistake usually shows up later, as a TypeError when you use the undefined: arr[3].x fails.",
            "Check with i < arr.length before reading.",
        ),
        example="""
            const a = [1, 2, 3];
            console.log(a[3], a[-1], "abc"[9], a.length);
        """,
        out="undefined undefined undefined 3",
    ),
    *py(
        "key-error",
        "KeyError",
        "The error for asking a dict for a key it does not have.",
        see=("dict", "key", "default-value", "exception"),
        priority=55,
        aka=("key error", "keyerror", "missing key"),
        detect=(r"\bKeyError\b",),
        rules=(
            "d['b'] raises it when 'b' is not a key; the message is the key itself.",
            "d.get('b') gives None (or a default you choose) instead of raising.",
            "'b' in d asks first.",
        ),
        example="""
            d = {"a": 1}
            try:
                d["b"]
            except KeyError as e:
                print("missing", e)
            print(d.get("b", 0))
        """,
        out="missing 'b'\n0",
    ),
    *py(
        "value-error",
        "ValueError",
        "The error for giving a function the right kind of value but a wrong one, such as int('abc').",
        see=("type-error", "type-conversion", "exception"),
        priority=55,
        aka=("value error", "valueerror", "invalid literal"),
        detect=(r"\bValueError\b",),
        rules=(
            "int('abc') is a ValueError; int(None) is a TypeError. Wrong kind of value is TypeError, right kind with a bad value is ValueError.",
            "Other causes: list.remove(x) when x is not in the list, and unpacking the wrong number of values.",
            "float('nan') is fine and is not an error: it is the float that means 'not a number'.",
        ),
        example="""
            try:
                int("abc")
            except ValueError as e:
                print(e)
        """,
        out="invalid literal for int() with base 10: 'abc'",
    ),
    *py(
        "zero-division-error",
        "ZeroDivisionError",
        "The error for dividing by zero. Python raises it for /, // and % alike.",
        see=("division", "modulo", "exception", "floor-division"),
        priority=55,
        aka=("zerodivisionerror", "zero division error", "division by zero", "divide by zero"),
        detect=(r"\bZeroDivisionError\b",),
        rules=(
            "1 / 0, 1 // 0 and 1 % 0 all raise it, as does 1.0 / 0.",
            "Check the divisor first, or catch the error.",
            "JavaScript does not raise this: there 1 / 0 is Infinity.",
        ),
        example="""
            for expr in ("1 / 0", "1 // 0", "1 % 0"):
                try:
                    eval(expr)
                except ZeroDivisionError as e:
                    print(expr, "->", type(e).__name__)
        """,
        out="1 / 0 -> ZeroDivisionError\n1 // 0 -> ZeroDivisionError\n1 % 0 -> ZeroDivisionError",
    ),
    *py(
        "attribute-error",
        "AttributeError",
        "The error for asking an object for an attribute or method it does not have, such as 'abc'.push(1).",
        see=("attribute", "method", "typo", "none"),
        priority=55,
        aka=("attribute error", "attributeerror", "no attribute", "has no attribute"),
        detect=(r"\bAttributeError\b",),
        rules=(
            "The message names the type and the missing name: 'str' object has no attribute 'push'.",
            "Common causes: a typo in a method name, using another language's method name, and a value that is None.",
            "hasattr(obj, 'name') asks first.",
        ),
        example="""
            try:
                "abc".push(1)
            except AttributeError as e:
                print(e)
        """,
        out="'str' object has no attribute 'push'",
    ),
    *js(
        "range-error",
        "RangeError",
        "The error for a number outside the range a function accepts, such as a negative array length or a recursion that goes too deep.",
        see=("call-stack", "exception", "recursion", "error-message"),
        priority=55,
        aka=("range error", "rangeerror", "invalid array length", "maximum call stack size exceeded"),
        detect=(r"\bRangeError\b",),
        rules=(
            "new Array(-1) is a RangeError: Invalid array length.",
            "So is (1).toFixed(101) and 'a'.repeat(-1).",
            "Infinite recursion ends in a RangeError: Maximum call stack size exceeded.",
        ),
        example="""
            try {
              new Array(-1);
            } catch (e) {
              console.log(e.name + ": " + e.message);
            }
        """,
        out="RangeError: Invalid array length",
    ),
    *both(
        "traceback",
        "Traceback (stack trace)",
        "The report printed when a program crashes: the chain of function calls that led to the error, with the file and line of each.",
        see=("call-stack", "error-message", "line-number", "exception"),
        priority=60,
        aka=("tracebacks", "stack trace", "stack traces", "stacktrace", "backtrace", "error report"),
        python=dict(
            detect=(r"\btraceback\b",),
            rules=(
                "It starts with 'Traceback (most recent call last):' and the calls are in order, the innermost last.",
                "The LAST line is the error type and message; the line just above it is where it happened. Read from the bottom.",
                "File names and line numbers in it are clickable in most editors.",
            ),
            example="""
                import traceback
                def f():
                    1 / 0
                try:
                    f()
                except ZeroDivisionError:
                    lines = traceback.format_exc().splitlines()
                    print(lines[0])
                    print(lines[-1])
            """,
            out="Traceback (most recent call last):\nZeroDivisionError: division by zero",
        ),
        javascript=dict(
            rules=(
                "An error's stack property starts with 'Name: message' and then has one 'at function (file:line:column)' line per call.",
                "The FIRST 'at' line is where the error happened; the lines below it are who called that.",
                "console.log(error.stack) prints it; an uncaught error prints it automatically.",
            ),
            example="""
                try {
                  null.x;
                } catch (e) {
                  const lines = e.stack.split("\\n");
                  console.log(lines[0]);
                  console.log(lines[1].trim().startsWith("at "));
                }
            """,
            out="TypeError: Cannot read properties of null (reading 'x')\ntrue",
        ),
    ),
    *both(
        "line-number",
        "Line number",
        "The position of a line in the file, counted from 1. Error messages quote it to show where something went wrong.",
        see=("traceback", "error-message", "syntax-error"),
        priority=45,
        aka=("line numbers", "line", "which line", "error line", "line of the error"),
        python=dict(
            rules=(
                "Lines are counted from 1, not 0, and blank lines and comments count.",
                "A traceback says File 'x.py', line 3: that is the line Python was running when it failed.",
                "For a syntax error the real mistake can be on an earlier line (an unclosed bracket), because Python only notices later.",
            ),
            example="""
                try:
                    a = 1
                    b = 1 / 0
                except ZeroDivisionError as e:
                    print(e.__traceback__.tb_lineno)
            """,
            out="3",
        ),
        javascript=dict(
            rules=(
                "Lines are counted from 1, not 0, and blank lines and comments count.",
                "A stack trace says file.js:3:9 : line 3, column 9 of that file.",
                "For a syntax error the real mistake can be on an earlier line (an unclosed bracket), because the engine only notices later.",
            ),
            example="""
                try {
                  const a = 1;
                  null.x;
                } catch (e) {
                  console.log(e.stack.match(/:(\\d+):\\d+/)[1]);
                }
            """,
            out="3",
        ),
    ),
    *both(
        "bug",
        "Bug",
        "A mistake in a program that makes it do something other than what you meant.",
        see=("debugging", "runtime-error", "syntax-error"),
        priority=40,
        aka=("bugs", "defect", "buggy", "logic error", "logic errors", "mistake"),
        python=dict(
            rules=(
                "A syntax error stops the program from starting; a runtime error stops it midway with a message.",
                "A logic error is the sneaky kind: nothing crashes, but the answer is wrong. Only checking the result finds it.",
                "In 'a + b / 2' the division happens first (precedence), so it is not the average of a and b.",
            ),
            example="""
                def average(a, b):
                    return a + b / 2
                print(average(4, 6))
            """,
            out="7.0",
        ),
        javascript=dict(
            rules=(
                "A syntax error stops the program from starting; a runtime error stops it midway with a message.",
                "A logic error is the sneaky kind: nothing crashes, but the answer is wrong. Only checking the result finds it.",
                "In 'a + b / 2' the division happens first (precedence), so it is not the average of a and b.",
            ),
            example="""
                function average(a, b) {
                  return a + b / 2;
                }
                console.log(average(4, 6));
            """,
            out="7",
        ),
    ),
    *both(
        "debugging",
        "Debugging",
        "Finding why a program does the wrong thing and fixing it.",
        see=("bug", "error-message", "traceback"),
        priority=45,
        aka=("debug", "debugger", "fix", "fixes", "fixing", "troubleshooting", "find the bug"),
        python=dict(
            rules=(
                "Read the error message first: it names the kind of error and the line.",
                "Print the values in between (print('total:', total)) to see where they stop being what you expected.",
                "Make the smallest input that still goes wrong, and change one thing at a time.",
            ),
            example="""
                def average(a, b):
                    total = a + b
                    print("total:", total)
                    return total / 2
                print(average(4, 6))
            """,
            out="total: 10\n5.0",
        ),
        javascript=dict(
            rules=(
                "Read the error message first: it names the kind of error and the line.",
                "Log the values in between (console.log('total:', total)) to see where they stop being what you expected.",
                "Make the smallest input that still goes wrong, and change one thing at a time.",
            ),
            example="""
                function average(a, b) {
                  const total = a + b;
                  console.log("total:", total);
                  return total / 2;
                }
                console.log(average(4, 6));
            """,
            out="total: 10\n5",
        ),
    ),
    *both(
        "typo",
        "Typo",
        "A spelling slip in a name, such as totl for total or apend for append. The computer takes names literally.",
        see=("variable", "debugging", "syntax-error"),
        priority=40,
        aka=("typos", "misspelling", "misspelled", "spelling mistake", "spelling error", "misspell"),
        python=dict(
            see=("name-error", "attribute-error", "debugging", "variable"),
            rules=(
                "A misspelled variable is a NameError; a misspelled method is an AttributeError.",
                "Names are case-sensitive: Total and total are different names.",
                "The message quotes the misspelled name, so compare it with what you meant.",
            ),
            example="""
                names = ["a"]
                try:
                    names.apend("b")
                except AttributeError as e:
                    print(e)
            """,
            out="'list' object has no attribute 'apend'",
        ),
        javascript=dict(
            see=("reference-error", "undefined", "debugging", "variable"),
            rules=(
                "A misspelled variable is a ReferenceError.",
                "A misspelled PROPERTY is not an error: user.nmae is just undefined, and the mistake shows up later as a TypeError.",
                "Names are case-sensitive: Total and total are different names.",
            ),
            example="""
                const user = { name: "A" };
                console.log(user.nmae);
                try {
                  user.nmae.length;
                } catch (e) {
                  console.log(e.name);
                }
            """,
            out="undefined\nTypeError",
        ),
    ),
]
