"""Context Managers: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 86

DECK = Deck(
    id="py-contexts",
    title="Context Managers",
    language="python",
    blurb="What with guarantees, how __enter__ and __exit__ work, and the contextlib tools for setup-and-cleanup.",
    slides=(
        Slide(
            title="What with guarantees",
            text="A with block runs set-up code before the body and clean-up code after it, even if the body fails. The object in charge is the context manager.",
            code=r"""class Door:
    def __enter__(self):
        print("open")
        return self
    def __exit__(self, *exc):
        print("close")
with Door():
    print("inside")
print("after")""",
            output="open\ninside\nclose\nafter",
            point="with = enter, body, then exit - always.",
        ),
        Slide(
            title="__enter__ and __exit__ order",
            text="The value returned by __enter__ is what 'as' gives you. __exit__ runs once the body is finished.",
            code=r"""class T:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        print("enter", self.name)
        return self.name.upper()
    def __exit__(self, *a):
        print("exit", self.name)
with T("a") as x:
    print("got", x)""",
            output="enter a\ngot A\nexit a",
            point="'as x' receives whatever __enter__ returns, not the manager itself.",
        ),
        Slide(
            title="Exit runs even on an error",
            text="If the body raises, __exit__ still runs and is told the exception type. Returning nothing lets the error carry on outward.",
            code=r"""class T:
    def __enter__(self):
        return self
    def __exit__(self, kind, val, tb):
        print("exit saw", kind.__name__)
try:
    with T():
        raise ValueError("bad")
except ValueError:
    print("caught outside")""",
            output="exit saw ValueError\ncaught outside",
            point="Clean-up happens first, then the exception keeps travelling.",
        ),
        Slide(
            title="Returning True swallows the error",
            text="If __exit__ returns True, Python treats the exception as handled and the program carries on after the with block.",
            code=r"""class Quiet:
    def __enter__(self):
        return self
    def __exit__(self, kind, val, tb):
        return True
with Quiet():
    raise ValueError("bad")
    print("never")
print("still running")""",
            output="still running",
            point="True from __exit__ hides the exception; use it sparingly.",
        ),
        Slide(
            title="@contextmanager with yield",
            text="A generator can be a context manager. Code before the yield is the set-up, the yield is the body, and code after is the clean-up.",
            code=r"""from contextlib import contextmanager
@contextmanager
def tag(name):
    print("<" + name + ">")
    yield
    print("</" + name + ">")
with tag("b"):
    print("text")""",
            output="<b>\ntext\n</b>",
            point="@contextmanager turns a short generator into a with-able object.",
        ),
        Slide(
            title="yield a value, finally to clean up",
            text="Whatever you yield becomes the 'as' value. Wrap the yield in try/finally so the clean-up runs even when the body raises.",
            code=r"""from contextlib import contextmanager
@contextmanager
def opened(name):
    try:
        yield name.upper()
    finally:
        print("close", name)
with opened("f") as f:
    print("using", f)""",
            output="using F\nclose f",
            point="try/finally around the yield makes clean-up certain.",
        ),
        Slide(
            title="Several managers in one with",
            text="Separate several managers with commas. They are entered left to right and left in the opposite order, like nested with blocks.",
            code=r"""from contextlib import contextmanager
@contextmanager
def m(n):
    print("in", n)
    yield
    print("out", n)
with m(1), m(2):
    print("body")""",
            output="in 1\nin 2\nbody\nout 2\nout 1",
            point="Last in, first out: the newest manager closes first.",
        ),
        Slide(
            title="contextlib.suppress",
            text="suppress(SomeError) skips the rest of the block if that error happens, and carries on after it. It is a tidy replacement for try/except/pass.",
            code=r"""from contextlib import suppress
data = {"a": 1}
with suppress(KeyError):
    print(data["a"])
    print(data["b"])
    print("skipped")
print("done")""",
            output="1\ndone",
            point="Everything after the error inside the block is skipped.",
        ),
        Slide(
            title="redirect_stdout into a StringIO",
            text="redirect_stdout sends everything print() writes into another file-like object for the length of the block. io.StringIO collects it as text.",
            code=r"""import io
from contextlib import redirect_stdout
buf = io.StringIO()
with redirect_stdout(buf):
    print("hidden")
print(repr(buf.getvalue()))""",
            output="'hidden\\n'",
            point="Capture a function's printing without changing the function.",
        ),
        Slide(
            title="ExitStack: a pile of managers",
            text="ExitStack lets you enter a number of managers decided at run time, such as one per item in a loop. They all close when the stack closes.",
            code=r"""from contextlib import ExitStack, contextmanager
@contextmanager
def m(n):
    print("in", n)
    yield
    print("out", n)
with ExitStack() as stack:
    for n in (1, 2, 3):
        stack.enter_context(m(n))
    print("body")""",
            output="in 1\nin 2\nin 3\nbody\nout 3\nout 2\nout 1",
            point="ExitStack is a with block whose managers you add as you go.",
        ),
        Slide(
            title="A manager that counts uses",
            text="A manager does not have to time or open anything. This one just counts how many times it has been entered, using a class attribute.",
            code=r"""class Counter:
    uses = 0
    def __enter__(self):
        Counter.uses += 1
    def __exit__(self, *exc):
        return False
for _ in range(3):
    with Counter():
        pass
print(Counter.uses)""",
            output="3",
            point="A manager is just two methods; you decide what they do.",
        ),
        Slide(
            title="Temporarily change a value",
            text="A common job for a manager: change a setting for the block and put the old value back afterwards. Add try/finally if the body might fail.",
            code=r"""from contextlib import contextmanager
cfg = {"mode": "normal"}
@contextmanager
def override(k, v):
    old, cfg[k] = cfg[k], v
    yield
    cfg[k] = old
with override("mode", "test"):
    print(cfg["mode"])
print(cfg["mode"])""",
            output="test\nnormal",
            point="Save the old value, set the new one, restore it on the way out.",
        ),
        Slide(
            title="contextlib.closing",
            text="Some objects have a close() method but are not context managers. closing() wraps one so that with calls close() for you.",
            code=r"""from contextlib import closing
class Conn:
    def close(self):
        print("closed")
with closing(Conn()) as c:
    print("using")""",
            output="using\nclosed",
            point="closing(x) means: call x.close() when the block ends.",
        ),
        Slide(
            title="io.StringIO as a file stand-in",
            text="StringIO behaves like a text file that lives in memory. It works with with, readline, read and for loops, which makes it ideal for examples and tests.",
            code=r"""import io
with io.StringIO("a\nb\n") as f:
    print(f.readline().strip())
    print(f.read().strip())
print(f.closed)""",
            output="a\nb\nTrue",
            point="StringIO is a file without a disk: handy for trying file code.",
        ),
        Slide(
            title="Handling an error inside the manager",
            text="In a @contextmanager generator you can catch the exception around the yield. Handling it there makes the with block finish normally.",
            code=r"""from contextlib import contextmanager
@contextmanager
def safe():
    try:
        yield
    except ValueError:
        print("handled")
with safe():
    raise ValueError
print("goes on")""",
            output="handled\ngoes on",
            point="An except around the yield turns the manager into an error handler.",
        ),
    ),
)
