"""Functions in Depth: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 50

DECK = Deck(
    id="py-functions",
    title="Functions in Depth",
    language="python",
    blurb="Parameters, defaults, *args, scope, closures, decorators and recursion.",
    slides=(
        Slide(
            title="Parameters vs arguments",
            text="Parameters are the names in the def line; arguments are the values you pass when calling. Arguments can go by position, or by name in any order.",
            code=r"""def greet(name, punct):
    return "Hi " + name + punct
print(greet("Ann", "!"))
print(greet(punct="?", name="Bo"))""",
            output="Hi Ann!\nHi Bo?",
            point="Parameter = the name in def; argument = the value you give.",
        ),
        Slide(
            title="Default values",
            text="A parameter with = has a default, used when the caller leaves it out. Careful: a default list is made ONCE, when the def runs, and is shared by every call, so it keeps growing.",
            code=r"""def power(x, n=2):
    return x ** n
print(power(5))
print(power(2, 10))
def add(item, box=[]):
    box.append(item)
    return box
print(add(1))
print(add(2))""",
            output="25\n1024\n[1]\n[1, 2]",
            point="Never use [] or {} as a default; use None and make the list inside.",
        ),
        Slide(
            title="Keyword-only with *",
            text="A bare * in the parameter list means everything after it must be given by name. This stops mix-ups with options like fill. Passing it by position raises a TypeError.",
            code=r"""def box(w, h, *, fill="#"):
    return (w, h, fill)
print(box(2, 3))
print(box(2, 3, fill="."))
try:
    box(2, 3, ".")
except TypeError:
    print("TypeError")""",
            output="(2, 3, '#')\n(2, 3, '.')\nTypeError",
            point="Parameters after a bare * can only be passed by name.",
        ),
        Slide(
            title="Positional-only with /",
            text="A / in the parameter list means everything before it must be given by position, never by name. Many built-in functions work this way. It lets you rename the parameter later without breaking callers.",
            code=r"""def half(x, /):
    return x / 2
print(half(8))
try:
    half(x=8)
except TypeError:
    print("TypeError")""",
            output="4.0\nTypeError",
            point="Parameters before / cannot be passed by name.",
        ),
        Slide(
            title="*args: any number of values",
            text="A parameter written *nums collects all extra positional arguments into a tuple, which may be empty. The name args is only a habit; the star does the work.",
            code=r"""def total(*nums):
    print(nums)
    return sum(nums)
print(total(1, 2, 3))
print(total())""",
            output="(1, 2, 3)\n6\n()\n0",
            point="*nums gathers extra positional arguments into a tuple.",
        ),
        Slide(
            title="**kwargs: any named values",
            text="A parameter written **opts collects extra named arguments into a dict. Together with *args it lets a function accept anything, which is handy when passing options along to another function.",
            code=r"""def show(**opts):
    print(opts)
    return len(opts)
print(show(a=1, b=2))
print(show())""",
            output="{'a': 1, 'b': 2}\n2\n{}\n0",
            point="**opts gathers extra named arguments into a dict.",
        ),
        Slide(
            title="Unpacking in a call",
            text="At the call, a * in front of a list spreads it into separate positional arguments, and ** in front of a dict spreads it into named arguments. It is the reverse of *args and **kwargs.",
            code=r"""def vol(a, b, c):
    return a * b * c
dims = [2, 3, 4]
print(vol(*dims))
named = {"a": 1, "b": 5, "c": 2}
print(vol(**named))
print(max(*[3, 9, 4]))""",
            output="24\n10\n9",
            point="f(*items) spreads a list; f(**opts) spreads a dict.",
        ),
        Slide(
            title="Returning several values",
            text="return a, b actually returns ONE tuple, which the caller can unpack into two names. It looks like many return values but is a single bundle.",
            code=r"""def min_max(xs):
    return min(xs), max(xs)
r = min_max([4, 1, 7])
print(r)
lo, hi = min_max([4, 1, 7])
print(lo, hi)
print(type(r).__name__)""",
            output="(1, 7)\n1 7\ntuple",
            point="'Several return values' is one tuple you unpack.",
        ),
        Slide(
            title="No return means None",
            text="A function that reaches its end without a return gives back None. So does a function whose if never reaches a return. Printing instead of returning is a common cause of surprise None values.",
            code=r"""def shout(s):
    print(s.upper())
r = shout("hi")
print(r)
def sign(n):
    if n > 0:
        return "pos"
print(sign(5), sign(-5))""",
            output="HI\nNone\npos None",
            point="print shows a value; only return hands it back to the caller.",
        ),
        Slide(
            title="Scope: Local, then Global",
            text="Python looks for a name in the Local scope first, then any enclosing function, then Global, then Built-in. Assigning a name inside a function makes a new local one; the global is untouched.",
            code=r"""x = "global"
def f():
    x = "local"
    return x
print(f())
print(x)
def g():
    return x
print(g())""",
            output="local\nglobal\nglobal",
            point="Looking up a name falls outward: Local, Enclosing, Global, Built-in.",
        ),
        Slide(
            title="The global keyword",
            text="To change a module-level variable from inside a function you must say global first. Without it, count += 1 would make a new local name and fail. Prefer returning values; reach for global rarely.",
            code=r"""count = 0
def bump():
    global count
    count += 1
bump()
bump()
print(count)""",
            output="2",
            point="global lets a function rebind a module-level name; reading needs no keyword.",
        ),
        Slide(
            title="Closures and nonlocal",
            text="An inner function remembers the variables of the function that made it, even after that function has finished. nonlocal lets the inner function change such a variable. Each call to the maker gets its own copy.",
            code=r"""def make_counter():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc
c = make_counter()
print(c(), c(), c())
print(make_counter()())""",
            output="1 2 3\n1",
            point="A closure carries its own private variables; nonlocal rebinds them.",
        ),
        Slide(
            title="Functions are objects, and lambda",
            text="A function is a value like any other: you can pass it to another function, store it in a list, or look at its name. A lambda is a tiny nameless function written on one line.",
            code=r"""def apply(f, x):
    return f(x)
def double(n):
    return n * 2
print(apply(double, 4))
print(apply(lambda n: n + 1, 4))
print(apply(str.upper, "ab"))
print(sorted(["bb", "a", "ccc"], key=len))
print(double.__name__)""",
            output="8\n5\nAB\n['a', 'bb', 'ccc']\ndouble",
            point="Pass a function by name WITHOUT parentheses: double, not double().",
        ),
        Slide(
            title="A simple decorator",
            text="A decorator is a function that takes a function and returns a wrapped version of it. Writing @loud above a def is shorthand for add = loud(add). The wrapper can run extra code before or after the original.",
            code=r"""def loud(fn):
    def wrapper(*args):
        print("calling", fn.__name__)
        return fn(*args)
    return wrapper

@loud
def add(a, b):
    return a + b
print(add(2, 3))""",
            output="calling add\n5",
            point="@decorator above a def means: name = decorator(name).",
        ),
        Slide(
            title="Recursion and docstrings",
            text="A recursive function calls itself on a smaller problem and needs a base case that stops it. The string right under the def line is the docstring, which tools and help() show to readers.",
            code=r'''def fact(n):
    """Return n factorial."""
    if n <= 1:
        return 1
    return n * fact(n - 1)
print(fact(5))
print(fact.__doc__)''',
            output="120\nReturn n factorial.",
            point="Every recursive function needs a base case, or it never stops.",
        ),
    ),
)
