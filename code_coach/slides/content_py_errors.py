"""Errors and Exceptions: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 65

DECK = Deck(
    id="py-errors",
    title="Errors and Exceptions",
    language="python",
    blurb="What goes wrong and how to handle it: try, except, else, finally, raise, custom errors and the common mistakes.",
    slides=(
        Slide(
            title="Reading a traceback",
            text="When an error is not handled, Python stops and prints a traceback. Read it from the BOTTOM: the last line names the error type and message, and the lines above show the calls that led there, newest last.",
            point="Bottom line first: the error type, then the line number.",
        ),
        Slide(
            title="try / except",
            text="Put risky code in try. If it raises an error, Python jumps to the matching except block instead of crashing, and the program carries on after it.",
            code=r"""try:
    print(1 / 0)
except ZeroDivisionError:
    print("cannot divide by zero")
print("still running")""",
            output="cannot divide by zero\nstill running",
            point="The error is caught; the program lives on.",
        ),
        Slide(
            title="Catch a specific type",
            text="Name the error you expect. as e gives you the error object, and type(e).__name__ is its type's name. Anything else still crashes loudly, which is what you want.",
            code=r"""try:
    int("x")
except ValueError as e:
    print("bad:", type(e).__name__)""",
            output="bad: ValueError",
            point="Catch what you expect, nothing more.",
        ),
        Slide(
            title="Several except clauses",
            text="A try can have many except clauses. Python checks them top to bottom and runs the first one that matches. Only one of them runs.",
            code=r"""def f(x):
    try:
        return 10 / x
    except ZeroDivisionError:
        return "zero"
    except TypeError:
        return "type"
print(f(2), f(0), f("a"))""",
            output="5.0 zero type",
            point="Different mistakes, different handlers.",
        ),
        Slide(
            title="else and finally",
            text="else runs only if the try block raised nothing. finally runs always, error or not. With no error the order is try, else, finally.",
            code=r"""try:
    print("try")
except ValueError:
    print("except")
else:
    print("else")
finally:
    print("finally")""",
            output="try\nelse\nfinally",
            point="finally is for cleanup that must always happen.",
        ),
        Slide(
            title="raise with a message",
            text="Use raise to signal a problem yourself. Give the error a message that says what was wrong, so whoever catches it can tell.",
            code=r"""def check(n):
    if n < 0:
        raise ValueError("n must be >= 0")
    return n
try:
    check(-1)
except ValueError as e:
    print(e)""",
            output="n must be >= 0",
            point="raise TypeOfError('what went wrong')",
        ),
        Slide(
            title="Re-raise with a bare raise",
            text="Sometimes you want to do something (log it, clean up) and still let the error go on. A bare raise inside except passes the same error up to the caller.",
            code=r"""try:
    try:
        int("x")
    except ValueError:
        print("logging it")
        raise
except ValueError:
    print("caller sees it")""",
            output="logging it\ncaller sees it",
            point="Bare raise = not handled after all, pass it on.",
        ),
        Slide(
            title="Custom exception classes",
            text="Make your own error type by subclassing Exception. A clear name like OutOfStock tells the reader far more than a generic error does.",
            code=r"""class OutOfStock(Exception):
    pass
try:
    raise OutOfStock("no apples")
except OutOfStock as e:
    print(type(e).__name__, e)""",
            output="OutOfStock no apples",
            point="class MyError(Exception): pass is often all you need.",
        ),
        Slide(
            title="The exception hierarchy",
            text="Errors form a family tree. KeyError and IndexError are both kinds of LookupError, and almost everything is an Exception. Catching a parent type also catches its children.",
            code=r"""print(issubclass(KeyError, LookupError))
print(issubclass(ValueError, Exception))
try:
    {}["a"]
except LookupError:
    print("caught by parent")""",
            output="True\nTrue\ncaught by parent",
            point="except Parent catches every child of Parent too.",
        ),
        Slide(
            title="EAFP vs LBYL",
            text="LBYL is 'look before you leap': check first, then act. EAFP is 'easier to ask forgiveness': just try it and handle the failure. Python code often prefers EAFP.",
            code=r"""d = {"a": 1}
if "b" in d:
    v = d["b"]
else:
    v = 0
try:
    v = d["b"]
except KeyError:
    v = 0
print(v)""",
            output="0",
            point="Both work; EAFP avoids checking things that rarely fail.",
        ),
        Slide(
            title="with cleans up, even on error",
            text="A with block always runs its cleanup when the block ends, even if an error flies out of it. Here the door is closed first, then the error is handled outside.",
            code=r"""class Door:
    def __enter__(self):
        return self
    def __exit__(self, *a):
        print("closed")
try:
    with Door():
        raise ValueError("oops")
except ValueError:
    print("handled")""",
            output="closed\nhandled",
            point="Use with for anything you must close or release.",
        ),
        Slide(
            title="assert",
            text="assert checks something you believe is true and raises AssertionError, with your message, if it is not. It is meant for catching your own mistakes while developing.",
            code=r"""x = 5
assert x > 0, "x must be positive"
print("ok")
try:
    assert x < 0, "x must be negative"
except AssertionError as e:
    print(e)""",
            output="ok\nx must be negative",
            point="assert is a sanity check, not input validation.",
        ),
        Slide(
            title="The common three",
            text="int('x') raises ValueError: right type, wrong content. A missing dict key raises KeyError. An index past the end of a list raises IndexError.",
            code=r"""tests = (lambda: int("x"), lambda: {}["k"], lambda: [1][5])
for f in tests:
    try:
        f()
    except Exception as e:
        print(type(e).__name__)""",
            output="ValueError\nKeyError\nIndexError",
            point="ValueError: bad value. KeyError: bad key. IndexError: bad position.",
        ),
        Slide(
            title="The cost of catching too much",
            text="except Exception swallows every mistake, including your own typos and bugs. Below, a bad list quietly becomes 0 and nobody learns something is wrong.",
            code=r"""def total(xs):
    try:
        return sum(xs)
    except Exception:
        return 0
print(total([1, 2]))
print(total([1, "2"]))""",
            output="3\n0",
            point="Broad except hides bugs. Catch the narrowest type you can.",
        ),
        Slide(
            title="finally runs even on return",
            text="Even if the try block returns, the finally block still runs before the function really leaves. That makes it the safe place for cleanup.",
            code=r"""def f():
    try:
        return "try"
    finally:
        print("cleanup")
print(f())""",
            output="cleanup\ntry",
            point="return, error or neither: finally always runs.",
        ),
    ),
)
