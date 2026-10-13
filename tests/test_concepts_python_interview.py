"""The Python interview bank: shape, gating, and every stated output.

tests/test_concepts.py holds a topic to the rules of any concept answer:
long enough to say something, short enough to say out loud, prose, asked
once. This applies the same rules to PYTHON_INTERVIEW_TOPICS on its own, so
they hold whether or not the bank is registered in `concepts.topics()` yet
(the gating and payload checks patch it in for their duration).

And it does the thing prose cannot check for itself. Where an answer says
what a snippet prints, CLAIMS holds that snippet, the output typed out by
hand before it was ever run, and the key phrase the answer says it with.
Each one runs in the real interpreter and has to match, and the phrase has
to be in the answer - so an answer cannot be reworded into saying something
else, or a claim quietly kept after the sentence it backs is gone.
"""

from __future__ import annotations

import contextlib
import functools
import unittest
from unittest import mock

import code_coach.concepts as concepts_module
from code_coach.concepts import payload
from code_coach.concepts.bank5 import PYTHON_INTERVIEW_TOPICS
from code_coach.engine import run_code

_BY_ID = {t.id: t for t in PYTHON_INTERVIEW_TOPICS}

#: The languages a student can be viewing, none of which is Python.
OTHER_LANGUAGES = ("javascript", "typescript", "cpp", "c", "rust", "dart",
                   "sql", "ruby")


def _c(topic: str, phrase: str, code: str, expect: str) -> tuple:
    return (topic, phrase, code.strip("\n"), expect)


#: (topic id, a phrase the answer says it with, snippet, what it prints).
CLAIMS: tuple[tuple[str, str, str, str], ...] = (
    # ── names and mutability ──
    _c("py-names-mutability", "rebinding the parameter is not", r"""
def f(xs):
    xs.append(1)
def g(xs):
    xs = [9]
a = []
f(a)
g(a)
print(a)
""", "[1]"),
    _c("py-names-mutability", "b[0] is [1, 9]", r"""
import copy
a = [[1], [2]]
b = copy.copy(a)
a[0].append(9)
print(b[0])
""", "[1, 9]"),
    _c("py-names-mutability", "unhashable type: 'list'", r"""
try:
    hash((1, [2]))
except TypeError as e:
    print(e)
""", "unhashable type: 'list'"),
    _c("py-names-mutability", "the name stays bound to the same object", r"""
a = [1]
b = a
a += [2]
print(b)
a = a + [3]
print(b)
""", "[1, 2]\n[1, 2]"),
    _c("py-names-mutability",
       "a string built at run time, such as one made with join, is a "
       "different object", r"""
import sys
a = "hello"
b = "".join(["hel", "lo"])
print(a is b, a is sys.intern(b))
""", "False True"),
    _c("py-names-mutability", "[[1, 0, 0], [1, 0, 0], [1, 0, 0]]", r"""
g = [[0] * 3] * 3
g[0][0] = 1
print(g)
""", "[[1, 0, 0], [1, 0, 0], [1, 0, 0]]"),
    _c("py-names-mutability", "returns None on purpose",
       "print([3, 1, 2].sort())", "None"),
    _c("py-names-mutability", "([1, 9], 2)", r"""
t = ([1], 2)
t[0].append(9)
print(t)
""", "([1, 9], 2)"),
    _c("py-names-mutability", "leaves b perfectly fine", r"""
a = [1]
b = a
del a
print(b)
""", "[1]"),
    _c("py-names-mutability", "returns None once the object has been freed", r"""
import weakref
class A:
    pass
a = A()
r = weakref.ref(a)
print(r() is a)
del a
print(r())
""", "True\nNone"),
    # ── scope, closures, decorators ──
    _c("py-scope-decorators", "raises UnboundLocalError", r"""
x = 1
def f():
    print(x)
    x = 2
try:
    f()
except UnboundLocalError as e:
    print(type(e).__name__)
""", "UnboundLocalError"),
    _c("py-scope-decorators", "gives [2, 2, 2] when called", r"""
fs = [lambda: i for i in range(3)]
print([f() for f in fs])
""", "[2, 2, 2]"),
    _c("py-scope-decorators", "`lambda i=i: i`", r"""
fs = [lambda i=i: i for i in range(3)]
print([f() for f in fs])
""", "[0, 1, 2]"),
    _c("py-scope-decorators", "reports its name as `wrapper`", r"""
def deco(f):
    def wrapper(*a, **k):
        return f(*a, **k)
    return wrapper
@deco
def hello():
    pass
print(hello.__name__)
""", "wrapper"),
    _c("py-scope-decorators", "copies the wrapped function's __name__", r"""
from functools import wraps
def deco(f):
    @wraps(f)
    def wrapper(*a, **k):
        return f(*a, **k)
    return wrapper
@deco
def hello():
    pass
print(hello.__name__, hello.__wrapped__.__name__)
""", "hello hello"),
    _c("py-scope-decorators", 'and `make()()` returns "bye"', r"""
def make():
    msg = "hi"
    def say():
        return msg
    msg = "bye"
    return say
print(make()())
print(make().__closure__[0].cell_contents)
""", "bye\nbye"),
    _c("py-scope-decorators",
       "The decoration happens once, when the `def` statement", r"""
def d(f):
    print("decorating")
    return f
@d
def g():
    pass
print("defined")
""", "decorating\ndefined"),
    _c("py-scope-decorators", "does 31 computations for fib(30)", r"""
from functools import lru_cache
@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
fib(30)
print(fib.cache_info().misses)
""", "31"),
    _c("py-scope-decorators", "`hi.n` after two calls is 2", r"""
class Count:
    def __init__(self, f):
        self.f = f
        self.n = 0
    def __call__(self, *a):
        self.n += 1
        return self.f(*a)
@Count
def hi():
    pass
hi()
hi()
print(hi.n)
""", "2"),
    # ── iterators, generators, comprehensions ──
    _c("py-iterators-generators", "`next([1, 2])` is a TypeError", r"""
try:
    next([1, 2])
except TypeError:
    print("TypeError")
it = iter([1, 2])
print(iter(it) is it)
""", "TypeError\nTrue"),
    _c("py-iterators-generators",
       "`list(it)` on `iter([1, 2, 3])` gives [2, 3]", r"""
it = iter([1, 2, 3])
next(it)
print(list(it))
""", "[2, 3]"),
    _c("py-iterators-generators", 'then v is "r"', r"""
def inner():
    yield 1
    return "r"
def outer():
    v = yield from inner()
    yield v
print(list(outer()))
""", "[1, 'r']"),
    _c("py-iterators-generators", "send(21) gives 42", r"""
def echo():
    x = yield
    yield x * 2
g = echo()
next(g)
print(g.send(21))
""", "42"),
    _c("py-iterators-generators", "gives the total and then 0", r"""
g = (i for i in range(3))
print(sum(g), sum(g))
""", "3 0"),
    _c("py-iterators-generators", "yields three groups of sizes 2, 1", r"""
from itertools import groupby
print([len(list(g)) for _, g in groupby("aabaa")])
""", "[2, 1, 2]"),
    _c("py-iterators-generators", "pairwise (3.10) gives overlapping pairs", r"""
from itertools import pairwise
print(list(pairwise([1, 2, 3])))
""", "[(1, 2), (2, 3)]"),
    _c("py-iterators-generators", "the cleanup message prints right away", r"""
def g():
    try:
        yield 1
        yield 2
    finally:
        print("cleanup")
it = g()
next(it)
it.close()
print("after")
""", "cleanup\nafter"),
    _c("py-iterators-generators", "referring to x is a NameError", r"""
[x for x in range(3)]
try:
    print(x)
except NameError:
    print("NameError")
""", "NameError"),
    _c("py-iterators-generators", "to [1, 2, 3, 4]", r"""
m = [[1, 2], [3, 4]]
print([x for row in m for x in row])
""", "[1, 2, 3, 4]"),
    _c("py-iterators-generators", "`list(m)` a second time is []", r"""
m = map(str, [1, 2])
print(list(m), list(m))
""", "['1', '2'] []"),
    # ── classes and the data model ──
    _c("py-data-model", "a __len__ attached to a single object is ignored", r"""
class A:
    def __len__(self):
        return 7
a = A()
a.__len__ = lambda: 1
print(len(a))
""", "7"),
    _c("py-data-model", "so a list of your objects displays using __repr__", r"""
class T:
    def __repr__(self):
        return "repr"
print(T(), [T()])
""", "repr [repr]"),
    _c("py-data-model", "gets its __hash__ set to None", r"""
class P:
    def __eq__(self, other):
        return True
print(P.__hash__)
""", "None"),
    _c("py-data-model", "assigning raises AttributeError", r"""
class C:
    @property
    def x(self):
        return 1
try:
    C().x = 2
except AttributeError:
    print("read-only")
""", "read-only"),
    _c("py-data-model", "`C().d` returns 42", r"""
class D:
    def __get__(self, obj, owner):
        return 42
class C:
    d = D()
print(C().d)
""", "42"),
    _c("py-data-model", "`L.make()` on a subclass L sees L", r"""
class K:
    @classmethod
    def make(cls):
        return cls.__name__
class L(K):
    pass
print(L.make())
""", "L"),
    _c("py-data-model", "`P(x=1, y=0)` as the repr", r"""
from dataclasses import dataclass
@dataclass
class P:
    x: int
    y: int = 0
print(P(1))
""", "P(x=1, y=0)"),
    _c("py-data-model", "`isinstance([], Iterable)` is True", r"""
from collections.abc import Iterable
print(isinstance([], Iterable), isinstance(5, Iterable))
""", "True False"),
    _c("py-data-model", "instantiating a subclass that missed one raises TypeError", r"""
from abc import ABC, abstractmethod
class A(ABC):
    @abstractmethod
    def f(self): ...
try:
    A()
except TypeError:
    print("TypeError")
""", "TypeError"),
    _c("py-data-model", "`bool(B())` is False", r"""
class B:
    def __len__(self):
        return 0
print(bool(B()))
""", "False"),
    _c("py-data-model", "`self.n += 1` reads the class value", r"""
class C:
    items = []
    n = 0
a, b = C(), C()
a.items.append(1)
a.n += 1
print(b.items, b.n, a.n)
""", "[1] 0 1"),
    # ── exceptions and context managers ──
    _c("py-exceptions-context",
       "`issubclass(KeyboardInterrupt, Exception)` is False", r"""
print(issubclass(KeyboardInterrupt, Exception),
      issubclass(ValueError, Exception))
""", "False True"),
    _c("py-exceptions-context", "else runs only if it finished without raising", r"""
try:
    x = 1
except ValueError:
    print("e")
else:
    print("else")
finally:
    print("fin")
""", "else\nfin"),
    _c("py-exceptions-context",
       "In a plain re-raise of a new error, __cause__ is None but "
       "__context__ is set", r"""
try:
    try:
        1 / 0
    except ZeroDivisionError:
        raise ValueError("bad")
except ValueError as e:
    print(type(e.__context__).__name__, e.__cause__)
""", "ZeroDivisionError None"),
    _c("py-exceptions-context",
       "`return n` followed by `n = 2` in the finally still returns 1", r"""
def f():
    n = 1
    try:
        return n
    finally:
        n = 2
print(f())
""", "1"),
    _c("py-exceptions-context", "Without it the exit message never prints", r"""
from contextlib import contextmanager
@contextmanager
def tag():
    print("enter")
    yield
    print("exit")
try:
    with tag():
        raise ValueError
except ValueError:
    print("caught")
""", "enter\ncaught"),
    _c("py-exceptions-context",
       "`with suppress(KeyError): d['x']` carries on to the next line", r"""
from contextlib import suppress
d = {}
with suppress(KeyError):
    d["x"]
print("after")
""", "after"),
    _c("py-exceptions-context",
       "both a `except* ValueError` and an `except* TypeError` run", r"""
try:
    raise ExceptionGroup("g", [ValueError(1), TypeError(2)])
except* ValueError as eg:
    print("value", len(eg.exceptions))
except* TypeError:
    print("type")
""", "value 1\ntype"),
    _c("py-exceptions-context",
       "a NotFound that derives from AppError is caught by `except AppError`",
       r"""
class AppError(Exception):
    pass
class NotFound(AppError):
    pass
try:
    raise NotFound("x")
except AppError as e:
    print(type(e).__name__, e)
""", "NotFound x"),
    _c("py-exceptions-context", "using it afterwards raises NameError", r"""
try:
    1 / 0
except ZeroDivisionError as e:
    pass
try:
    print(e)
except NameError:
    print("NameError")
""", "NameError"),
    _c("py-exceptions-context", "appends to __notes__", r"""
e = ValueError("x")
e.add_note("note")
print(e.__notes__)
""", "['note']"),
    # ── GIL, threads, processes, asyncio ──
    _c("py-gil-concurrency",
       "four threads doing a thousand increments each reliably reach 4000", r"""
import threading
n = 0
lock = threading.Lock()
def work():
    global n
    for _ in range(1000):
        with lock:
            n += 1
ts = [threading.Thread(target=work) for _ in range(4)]
for t in ts:
    t.start()
for t in ts:
    t.join()
print(n)
""", "4000"),
    _c("py-gil-concurrency",
       "`ex.map` returns results in the order of the inputs", r"""
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(2) as ex:
    print(list(ex.map(str, [3, 1, 2])))
""", "['3', '1', '2']"),
    _c("py-gil-concurrency", "a 0, b 0, a 1, b 1", r"""
import asyncio
async def ticker(name):
    for i in range(2):
        print(name, i)
        await asyncio.sleep(0)
async def main():
    await asyncio.gather(ticker("a"), ticker("b"))
asyncio.run(main())
""", "a 0\nb 0\na 1\nb 1"),
    _c("py-gil-concurrency", "`sum([1, 2, 3])` giving 6", r"""
import asyncio
async def main():
    print(await asyncio.to_thread(sum, [1, 2, 3]))
asyncio.run(main())
""", "6"),
    _c("py-gil-concurrency",
       "return_exceptions=True puts errors in the list", r"""
import asyncio
async def ok():
    await asyncio.sleep(0.01)
    return 1
async def bad():
    raise ValueError("boom")
async def main():
    print(await asyncio.gather(ok(), bad(), return_exceptions=True))
asyncio.run(main())
""", "[1, ValueError('boom')]"),
    _c("py-gil-concurrency", "`task.cancelled()` is then True", r"""
import asyncio
async def main():
    t = asyncio.create_task(asyncio.sleep(10))
    await asyncio.sleep(0)
    t.cancel()
    try:
        await t
    except asyncio.CancelledError:
        print("cancelled")
    print(t.cancelled())
asyncio.run(main())
""", "cancelled\nTrue"),
    # ── memory and performance ──
    _c("py-memory-performance",
       "changes only a handful of times over a hundred appends", r"""
import sys
a = []
sizes = set()
for i in range(100):
    a.append(i)
    sizes.add(sys.getsizeof(a))
print(len(sizes) < 20)
""", "True"),
    _c("py-memory-performance", "is a few hundred bytes", r"""
import sys
print(sys.getsizeof(x for x in range(10**6)) < 1000)
""", "True"),
    _c("py-memory-performance", "24 bytes in CPython on a 64-bit build", r"""
import sys
print(sys.getsizeof(1.0))
""", "24"),
    _c("py-memory-performance",
       "`999 in set(range(1000))` is True and 1000 is False",
       "print(999 in set(range(1000)), 1000 in set(range(1000)))",
       "True False"),
    _c("py-memory-performance", "list of 100000 items as hundreds of kilobytes",
       r"""
import tracemalloc
tracemalloc.start()
data = [0] * 100000
current, _ = tracemalloc.get_traced_memory()
print(current > 100_000)
""", "True"),
    # ── types and typing ──
    _c("py-typing", 'gives "xy"', r"""
def add(a: int, b: int) -> int:
    return a + b
print(add("x", "y"))
""", "xy"),
    _c("py-typing", "`Optional[int]` equals `int | None`", r"""
from typing import Optional
print(Optional[int] == (int | None))
""", "True"),
    _c("py-typing", "only checks that the names exist, not their signatures", r"""
from typing import Protocol, runtime_checkable
@runtime_checkable
class Closer(Protocol):
    def close(self) -> None: ...
class F:
    def close(self, x, y):
        pass
print(isinstance(F(), Closer))
""", "True"),
    _c("py-typing", "but not usable with isinstance", r"""
try:
    isinstance([], list[int])
except TypeError:
    print("TypeError")
""", "TypeError"),
    _c("py-typing", "`P(1, 2)` prints P(x=1, y=2)", r"""
from typing import NamedTuple
class P(NamedTuple):
    x: int
    y: int
p = P(1, 2)
print(p)
print(p._replace(x=5))
""", "P(x=1, y=2)\nP(x=5, y=2)"),
    _c("py-typing", "`f.__annotations__` shows {'x': 'Undefined'}", r"""
from __future__ import annotations
def f(x: Undefined):
    pass
print(f.__annotations__)
""", "{'x': 'Undefined'}"),
    _c("py-typing", 'so `cast(int, "x")` returns "x"', r"""
from typing import cast, TYPE_CHECKING
print(cast(int, "x"), TYPE_CHECKING)
""", "x False"),
    _c("py-typing", "`A(1)` prints A(x=1)", r"""
from dataclasses import dataclass
from typing import ClassVar
@dataclass
class A:
    x: int
    n: ClassVar[int] = 0
print(A(1))
""", "A(x=1)"),
    # ── data structures in practice ──
    _c("py-data-structures", "collections.OrderedDict compares order too", r"""
from collections import OrderedDict
print({"a": 1, "b": 2} == {"b": 2, "a": 1},
      OrderedDict(a=1, b=2) == OrderedDict(b=2, a=1))
""", "True False"),
    _c("py-data-structures",
       "so is a frozenset's regardless of the order it was built in",
       "print(hash(frozenset([1, 2])) == hash(frozenset([2, 1])))", "True"),
    _c("py-data-structures",
       "a stored `nan` is found with the same object but a fresh NaN is not",
       r"""
nan = float("nan")
d = {nan: 1}
print(nan in d, float("nan") in d)
""", "True False"),
    _c("py-data-structures",
       "a deque with maxlen=2 that has seen 1, 2, 3 holds 2 and 3", r"""
from collections import deque
d = deque(maxlen=2)
d.extend([1, 2, 3])
print(d)
""", "deque([2, 3], maxlen=2)"),
    _c("py-data-structures", "on [1, 2, 2, 3] they give 1 and 3", r"""
from bisect import bisect_left, bisect_right
a = [1, 2, 2, 3]
print(bisect_left(a, 2), bisect_right(a, 2))
""", "1 3"),
    _c("py-data-structures", "gives [('l', 2)]", r"""
from collections import Counter
print(Counter("hello").most_common(1))
""", "[('l', 2)]"),
    _c("py-data-structures", "leaves {'x': 0} behind", r"""
from collections import defaultdict
d = defaultdict(int)
d["x"]
print(dict(d))
""", "{'x': 0}"),
    _c("py-data-structures", "`{1, 2, 3} & {2, 3, 4}` is {2, 3}",
       "print({1, 2, 3} & {2, 3, 4}, {1, 2, 3} ^ {2, 3, 4})",
       "{2, 3} {1, 4}"),
    _c("py-data-structures", "gives {'a': [1], 'b': [1]}", r"""
d = dict.fromkeys("ab", [])
d["a"].append(1)
print(d)
""", "{'a': [1], 'b': [1]}"),
    _c("py-data-structures", "the repr is `P(x=1, y=2)`", r"""
from collections import namedtuple
P = namedtuple("P", "x y")
p = P(1, 2)
x, y = p
print(x + y, p)
""", "3 P(x=1, y=2)"),
    _c("py-data-structures",
       "a reversed sort of lengths still lists bb before cc",
       'print(sorted(["bb", "a", "cc", "d"], key=len, reverse=True))',
       "['bb', 'cc', 'a', 'd']"),
    _c("py-data-structures", "index 0 is always the smallest", r"""
import heapq
h = [5, 1, 3]
heapq.heapify(h)
print(h[0], heapq.nlargest(2, [4, 9, 1, 7]))
""", "1 [9, 7]"),
    # ── packaging, environments, imports ──
    _c("py-packaging-imports",
       "which the standard library reads with tomllib since 3.11", r"""
import tomllib
print(tomllib.loads('[project]\nname = "x"\n')["project"]["name"])
""", "x"),
    _c("py-packaging-imports",
       "`import json as j2` gives you the very same module object", r"""
import json
import json as j2
import sys
print(json is j2, "json" in sys.modules)
""", "True True"),
    _c("py-packaging-imports",
       '__name__ is the string "__main__" in the file',
       "print(__name__)", "__main__"),
    _c("py-packaging-imports",
       "with an ImportError saying there is no known parent package", r"""
try:
    from . import x
except ImportError as e:
    print(e)
""", "attempted relative import with no known parent package"),
    # ── testing ──
    _c("py-testing",
       "`Mock(return_value=3)` returns 3 and remembers `call(1)`", r"""
from unittest.mock import Mock
m = Mock(return_value=3)
print(m(1), m.call_args)
""", "3 call(1)"),
    _c("py-testing",
       "with os.path.exists patched to return True, any path appears to exist",
       r"""
import os
from unittest.mock import patch
with patch("os.path.exists", return_value=True):
    print(os.path.exists("/no/such/path"))
""", "True"),
    _c("py-testing", "calling it with the wrong arguments raises TypeError", r"""
from unittest.mock import create_autospec
def f(a, b):
    pass
m = create_autospec(f)
try:
    m(1)
except TypeError:
    print("bad call")
""", "bad call"),
    _c("py-testing",
       "two generators built with the same seed produce the same numbers",
       "import random\nprint(random.Random(1).random() == "
       "random.Random(1).random())", "True"),
    _c("py-testing", "it raises AssertionError with only your message", r"""
try:
    assert 1 == 2, "nope"
except AssertionError as e:
    print(e)
""", "nope"),
    _c("py-testing",
       "`asyncio.run(m())` returns whatever return_value was set", r"""
import asyncio
from unittest.mock import AsyncMock
m = AsyncMock(return_value=5)
print(asyncio.run(m()))
""", "5"),
    # ── web and APIs ──
    _c("py-web-apis",
       "sending messages such as http.response.start and "
       "http.response.body", r"""
import asyncio
async def app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"hi"})
async def send(message):
    print(message["type"])
asyncio.run(app({"type": "http"}, None, send))
""", "http.response.start\nhttp.response.body"),
    _c("py-web-apis", '`os.environ.get("NAME", "fallback")`', r"""
import os
print(os.environ.get("CC_SURELY_UNSET_VARIABLE", "fallback"))
""", "fallback"),
    _c("py-web-apis", "a KeyError on os.environ", r"""
import os
try:
    os.environ["CC_SURELY_UNSET_VARIABLE"]
except KeyError:
    print("KeyError")
""", "KeyError"),
    _c("py-web-apis", 'so id="123" becomes the int 123', r"""
from pydantic import BaseModel
class U(BaseModel):
    id: int
u = U(id="123")
print(u.id, type(u.id).__name__)
""", "123 int"),
    # ── data and numerics ──
    _c("py-data-numerics", "1267650600228229401496703205376",
       "print(2 ** 100)", "1267650600228229401496703205376"),
    _c("py-data-numerics", "by default at 4300 digits", r"""
try:
    int("1" * 5000)
except ValueError:
    print("too long")
""", "too long"),
    _c("py-data-numerics",
       '`Decimal("0.1") + Decimal("0.2")` is exactly 0.3', r"""
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"), Decimal(0.1) == Decimal("0.1"))
""", "0.3 False"),
    _c("py-data-numerics", "where 1/3 plus 1/6 is exactly 1/2", r"""
from fractions import Fraction
print(Fraction(1, 3) + Fraction(1, 6))
""", "1/2"),
    _c("py-data-numerics",
       "so comparing 1e-10 to 0 is False unless you pass abs_tol", r"""
import math
print(math.isclose(0.1 + 0.2, 0.3), math.isclose(1e-10, 0),
      math.isclose(1e-10, 0, abs_tol=1e-9))
""", "True False True"),
    _c("py-data-numerics", "`nan == nan` is False", r"""
import math
nan = float("nan")
print(nan == nan, nan != nan, math.isnan(nan))
""", "False True True"),
    _c("py-data-numerics", "with ROUND_HALF_UP gives 2.68", r"""
from decimal import Decimal, ROUND_HALF_UP
print(round(2.675, 2),
      Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
""", "2.67 2.68"),
    _c("py-data-numerics", "`-7 // 2` is -4",
       "print(-7 // 2, -7 % 2, divmod(-7, 2))", "-4 1 (-4, 1)"),
    _c("py-data-numerics", "`next(rows)` returning the header", r"""
import csv, io
rows = csv.reader(io.StringIO("a,b\n1,2\n"))
print(next(rows), next(rows))
""", "['a', 'b'] ['1', '2']"),
    # ── tricky outputs ──
    _c("py-tricky-outputs", "False, True, False.",
       "print([] == False, not [], bool([]))", "False True False"),
    _c("py-tricky-outputs", "0, 2 and 2.",
       "print(round(0.5), round(1.5), round(2.5))", "0 2 2"),
    _c("py-tricky-outputs", "After `a.append(1)`, b shows [1] as well", r"""
a = b = []
a.append(1)
print(b)
""", "[1]"),
    _c("py-tricky-outputs", "2, True and True.",
       "print(True + True, True == 1, isinstance(True, int))",
       "2 True True"),
    _c("py-tricky-outputs", "\"apple\" and ['B', 'a', 'b'].",
       'print(max("apple", "Banana"), sorted(["b", "B", "a"]))',
       "apple ['B', 'a', 'b']"),
    _c("py-tricky-outputs", "True, False and True.",
       "print(1 < 2 < 3, 3 > 2 > 2, 1 == 1 in [1])", "True False True"),
    _c("py-tricky-outputs", "<class 'int'> and <class 'tuple'>.",
       "print(type((1)), type((1,)))", "<class 'int'> <class 'tuple'>"),
    _c("py-tricky-outputs", "['ab', 'c'].",
       'print(["a" "b", "c"], len(["a" "b" "c"]))', "['ab', 'c'] 1"),
    _c("py-tricky-outputs", "leaves a as 2 and b as 3", r"""
a, b = 1, 2
a, b = b, a + b
print(a, b)
""", "2 3"),
    _c("py-tricky-outputs", '"default", 0 and None.',
       'print("" or "default", 0 and 1, [] or None)', "default 0 None"),
    _c("py-tricky-outputs", "3, -3, -4 and 42.",
       'print(int(3.9), int(-3.9), round(-3.9), int("42"))', "3 -3 -4 42"),
    _c("py-tricky-outputs", "setting `A.x = 5` makes `B.x` 5 as well", r"""
class A:
    x = 1
class B(A):
    pass
A.x = 5
print(B.x)
B.x = 7
print(A.x, B.x)
""", "5\n5 7"),
)


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    return run_code(code, language="python", timeout=60)


def _out(stdout: str) -> str:
    return stdout.replace("\r\n", "\n").rstrip("\n")


def _all_questions():
    return [(t, q) for t in PYTHON_INTERVIEW_TOPICS for q in t.questions]


@contextlib.contextmanager
def _registered():
    """concepts.topics() as it will be once the bank is registered."""
    real = concepts_module.topics

    def with_python(language=None):
        base = real(language)
        have = {t.id for t in base}
        extra = tuple(t for t in PYTHON_INTERVIEW_TOPICS
                      if t.id not in have
                      and (language is None or t.belongs_to(language)))
        return tuple(sorted((*base, *extra), key=lambda t: (t.order, t.name)))

    with mock.patch.object(concepts_module, "topics", with_python):
        yield


def _others_than_mine():
    """Every topic that is not ours, registered or not."""
    mine = {t.id for t in PYTHON_INTERVIEW_TOPICS}
    out = [t for t in concepts_module.topics() if t.id not in mine]
    try:  # the JavaScript bank, which is written beside this one
        from code_coach.concepts.bank4 import INTERVIEW_TOPICS
    except ImportError:
        INTERVIEW_TOPICS = ()
    seen = {t.id for t in out}
    out.extend(t for t in INTERVIEW_TOPICS if t.id not in seen)
    return out


class ShapeTests(unittest.TestCase):
    def test_a_whole_bank(self) -> None:
        self.assertGreaterEqual(len(PYTHON_INTERVIEW_TOPICS), 14)
        self.assertGreaterEqual(len(_all_questions()), 130)

    def test_every_topic_is_a_full_set(self) -> None:
        """test_concepts.py asks ten of every topic once it is registered."""
        for t in PYTHON_INTERVIEW_TOPICS:
            with self.subTest(topic=t.id):
                self.assertGreaterEqual(len(t.questions), 10)
                self.assertLessEqual(len(t.questions), 14)

    def test_the_areas_a_python_interview_names(self) -> None:
        have = set(_BY_ID)
        for wanted in (
            "py-names-mutability", "py-scope-decorators",
            "py-iterators-generators", "py-data-model",
            "py-exceptions-context", "py-gil-concurrency",
            "py-memory-performance", "py-typing", "py-data-structures",
            "py-packaging-imports", "py-testing", "py-web-apis",
            "py-data-numerics", "py-tricky-outputs",
        ):
            with self.subTest(topic=wanted):
                self.assertIn(wanted, have)

    def test_ids_and_orders_are_unique_and_new(self) -> None:
        ids = [t.id for t in PYTHON_INTERVIEW_TOPICS]
        orders = [t.order for t in PYTHON_INTERVIEW_TOPICS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(orders), len(set(orders)))
        others = _others_than_mine()
        self.assertFalse(set(ids) & {t.id for t in others})
        self.assertFalse(set(orders) & {t.order for t in others})

    def test_they_come_after_the_semantics_topic(self) -> None:
        """python-semantics (order 1) is the opener; these are the rest."""
        for t in PYTHON_INTERVIEW_TOPICS:
            with self.subTest(topic=t.id):
                self.assertGreater(t.order, 1)

    def test_every_topic_says_what_it_is(self) -> None:
        for t in PYTHON_INTERVIEW_TOPICS:
            with self.subTest(topic=t.id):
                self.assertTrue(t.name.strip())
                self.assertGreater(len(t.blurb), 20)
                self.assertGreater(t.order, 0)

    def test_every_question_asks_something(self) -> None:
        for t, q in _all_questions():
            with self.subTest(ask=q.ask[:40]):
                self.assertGreater(len(q.ask), 15)
                self.assertTrue(q.ask.rstrip().endswith("?"))

    def test_an_answer_says_a_mechanism_not_a_definition(self) -> None:
        for t, q in _all_questions():
            with self.subTest(ask=q.ask[:40]):
                self.assertGreater(len(q.answer), 120)
                self.assertLess(len(q.answer), 700)
                self.assertIn(q.answer.strip()[-1], ".?")

    def test_a_follow_up_is_a_question_when_there_is_one(self) -> None:
        for t, q in _all_questions():
            if not q.follow_up:
                continue
            with self.subTest(ask=q.ask[:40]):
                self.assertTrue(q.follow_up.rstrip().endswith("?"))
                self.assertGreater(len(q.follow_up), 15)

    def test_most_questions_carry_a_follow_up(self) -> None:
        with_one = sum(1 for _, q in _all_questions() if q.follow_up)
        self.assertGreaterEqual(with_one, len(_all_questions()) // 2)

    def test_answers_are_written_as_prose(self) -> None:
        for t, q in _all_questions():
            with self.subTest(ask=q.ask[:40]):
                self.assertNotIn("\n", q.answer)
                self.assertNotIn("```", q.answer)
                self.assertNotIn("  ", q.answer)
                self.assertNotIn("\n-", q.answer)

    def test_no_question_is_asked_twice_anywhere(self) -> None:
        mine = [q.ask for _, q in _all_questions()]
        self.assertEqual(len(mine), len(set(mine)))
        elsewhere = {q.ask for t in _others_than_mine() for q in t.questions}
        self.assertFalse(set(mine) & elsewhere)

    def test_no_answer_is_reused_anywhere(self) -> None:
        mine = [q.answer for _, q in _all_questions()]
        self.assertEqual(len(mine), len(set(mine)))
        elsewhere = {q.answer for t in _others_than_mine()
                     for q in t.questions}
        self.assertFalse(set(mine) & elsewhere)

    def test_no_topic_repeats_the_semantics_topic(self) -> None:
        """python-semantics already has its dozen. The same question put
        another way is padding, so no ask here may be one of those."""
        semantics = next(
            t for t in _others_than_mine() if t.id == "python-semantics")
        theirs = {q.ask.lower() for q in semantics.questions}
        for _, q in _all_questions():
            with self.subTest(ask=q.ask[:40]):
                self.assertNotIn(q.ask.lower(), theirs)


class GatingTests(unittest.TestCase):
    def test_every_topic_belongs_to_python_only(self) -> None:
        """Language-agnostic ground (floating point, concurrency in the
        abstract) is already in the shared banks, so each of these is about
        Python itself and is shown to whoever is writing Python."""
        for t in PYTHON_INTERVIEW_TOPICS:
            with self.subTest(topic=t.id):
                self.assertEqual(t.languages, ("python",))
                self.assertTrue(t.belongs_to("python"))
                for language in OTHER_LANGUAGES:
                    self.assertFalse(t.belongs_to(language), language)
                self.assertFalse(t.belongs_to(None))

    def test_registered_python_sees_them_and_nobody_else_does(self) -> None:
        mine = {t.id for t in PYTHON_INTERVIEW_TOPICS}
        with _registered():
            python_ids = {e["id"] for e in payload("python")}
            self.assertTrue(mine <= python_ids)
            for language in OTHER_LANGUAGES:
                with self.subTest(language=language):
                    self.assertFalse(
                        mine & {e["id"] for e in payload(language)})
            self.assertTrue(mine <= {e["id"] for e in payload()})

    def test_registered_the_route_serves_them_to_python(self) -> None:
        from code_coach.api import server

        mine = {t.id for t in PYTHON_INTERVIEW_TOPICS}
        with _registered():
            served = server.concepts("python")
            other = server.concepts("javascript")
        self.assertTrue(mine <= {e["id"] for e in served})
        self.assertFalse(mine & {e["id"] for e in other})
        for entry in served:
            if entry["id"] in mine:
                self.assertTrue(entry["questions"])

    def test_registered_the_whole_bank_still_meets_the_shared_rules(self) -> None:
        """Order unique across everything, and every topic ten or more:
        what tests/test_concepts.py asks once this is registered."""
        with _registered():
            everything = concepts_module.topics()
            orders = [t.order for t in everything]
            self.assertEqual(len(orders), len(set(orders)))
            asked = [q.ask for t in everything for q in t.questions]
            self.assertEqual(len(asked), len(set(asked)))
            answers = [q.answer for t in everything for q in t.questions]
            self.assertEqual(len(answers), len(set(answers)))
            for t in everything:
                self.assertGreaterEqual(len(t.questions), 10, t.id)


class ClaimTests(unittest.TestCase):
    def test_there_are_enough_claims(self) -> None:
        self.assertGreaterEqual(len(CLAIMS), 30)

    def test_every_claim_names_a_topic_and_is_spread_across_them(self) -> None:
        spoken_for = set()
        for topic, phrase, code, expect in CLAIMS:
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(topic, _BY_ID)
                self.assertTrue(code.strip())
                self.assertTrue(expect.strip())
            spoken_for.add(topic)
        self.assertEqual(spoken_for, set(_BY_ID))

    def test_every_claim_phrase_is_in_its_topics_answers(self) -> None:
        for topic, phrase, _, _ in CLAIMS:
            with self.subTest(phrase=phrase[:50]):
                answers = [q.answer for q in _BY_ID[topic].questions]
                self.assertTrue(
                    any(phrase in a for a in answers),
                    f"no answer in {topic} says {phrase!r}")

    def test_every_claim_phrase_is_in_exactly_one_answer(self) -> None:
        """A phrase that appears in two answers backs neither of them."""
        for topic, phrase, _, _ in CLAIMS:
            with self.subTest(phrase=phrase[:50]):
                hits = [q.ask for q in _BY_ID[topic].questions
                        if phrase in q.answer]
                self.assertEqual(len(hits), 1, hits)

    def test_every_snippet_prints_what_the_answer_says(self) -> None:
        for topic, phrase, code, expect in CLAIMS:
            with self.subTest(phrase=phrase[:50]):
                stdout, stderr, status = _run(code)
                self.assertEqual(status, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    _out(stdout), expect,
                    f"python prints {stdout.rstrip()!r} and the claim "
                    f"for {phrase!r} says {expect!r}")

    def test_nothing_is_said_on_stderr(self) -> None:
        for _, phrase, code, _ in CLAIMS:
            with self.subTest(phrase=phrase[:50]):
                self.assertEqual(_run(code)[1].strip(), "")

    def test_no_claim_depends_on_the_clock_or_the_dice(self) -> None:
        for _, phrase, code, _ in CLAIMS:
            with self.subTest(phrase=phrase[:50]):
                for word in ("import time", "datetime", "perf_counter",
                             "uuid", "os.urandom", "random.random()"):
                    self.assertNotIn(word, code)


if __name__ == "__main__":
    unittest.main()
