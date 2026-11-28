"""Decorators in Depth: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 87

DECK = Deck(
    id="py-decorators",
    title="Decorators in Depth",
    language="python",
    blurb="Wrappers around functions: how @ works, passing arguments through, factories, stacking, caching, and class decorators.",
    slides=(
        Slide(
            title="Functions are objects",
            text="A function can be stored in a variable, put in a list, and passed around like any value. Decorators depend on this.",
            code=r"""def hi():
    return "hi"
f = hi
print(f())
print(f is hi)
print(hi.__name__)
funcs = [hi, len]
print(funcs[1]("abc"))""",
            output="hi\nTrue\nhi\n3",
            point="A function name is just a variable that holds a function.",
        ),
        Slide(
            title="A wrapper function",
            text="A decorator takes a function and returns a new one that does extra work around the original. Here the wrapper shouts the result.",
            code=r"""def shout(fn):
    def wrapper():
        return fn().upper() + "!"
    return wrapper
def hi():
    return "hi"
loud = shout(hi)
print(loud())
print(hi())""",
            output="HI!\nhi",
            point="Decorator in, wrapped function out; the original is untouched.",
        ),
        Slide(
            title="@ is just f = deco(f)",
            text="Writing @shout above a def does the same as writing hi = shout(hi) right after it. The name hi now points at the wrapper.",
            code=r"""def shout(fn):
    def wrapper():
        return fn().upper() + "!"
    return wrapper
@shout
def hi():
    return "hi"
print(hi())""",
            output="HI!",
            point="@deco is shorthand for rebinding the name to deco(function).",
        ),
        Slide(
            title="*args and **kwargs pass-through",
            text="A wrapper should accept anything and hand it on, so it works for functions with any parameters.",
            code=r"""def logged(fn):
    def wrapper(*args, **kwargs):
        print("calling", fn.__name__)
        return fn(*args, **kwargs)
    return wrapper
@logged
def add(a, b=1):
    return a + b
print(add(2, b=5))""",
            output="calling add\n7",
            point="Use (*args, **kwargs) in the wrapper and pass them straight on.",
        ),
        Slide(
            title="functools.wraps keeps the name",
            text="Without help the decorated function's __name__ and docstring become the wrapper's. functools.wraps copies them back.",
            code=r"""from functools import wraps
def deco(fn):
    @wraps(fn)
    def wrapper(*a, **k):
        return fn(*a, **k)
    return wrapper
@deco
def add(a, b):
    '''Add two numbers.'''
print(add.__name__, add.__doc__)""",
            output="add Add two numbers.",
            point="Always put @wraps(fn) on the wrapper.",
        ),
        Slide(
            title="Decorators with arguments",
            text="To write @repeat(3), make repeat a factory: it takes the argument and returns the real decorator. That is three levels of function.",
            code=r"""def repeat(n):
    def deco(fn):
        def wrapper(*a):
            return [fn(*a) for _ in range(n)]
        return wrapper
    return deco
@repeat(3)
def hi(name):
    return "hi " + name
print(hi("Al"))""",
            output="['hi Al', 'hi Al', 'hi Al']",
            point="@repeat(3) first calls repeat(3), then applies what it returns.",
        ),
        Slide(
            title="Stacking decorators",
            text="With two decorators, the one nearest the def is applied first. The top one wraps the result.",
            code=r"""def tag(name):
    def deco(fn):
        print("apply", name)
        return lambda: name + "(" + fn() + ")"
    return deco
@tag("a")
@tag("b")
def f():
    return "x"
print(f())""",
            output="apply b\napply a\na(b(x))",
            point="Applied bottom to top, so f is a(b(f)).",
        ),
        Slide(
            title="A call counter",
            text="A wrapper is a function, so it can carry its own attributes. This one counts how many times it has been called.",
            code=r"""def counted(fn):
    def wrapper(*a):
        wrapper.calls += 1
        return fn(*a)
    wrapper.calls = 0
    return wrapper
@counted
def f(x):
    return x * 2
print(f(1), f(5), f.calls)""",
            output="2 10 2",
            point="State can live as an attribute on the wrapper.",
        ),
        Slide(
            title="A memoizer",
            text="A decorator can remember earlier answers in a dict. The first call does the work, and repeat calls with the same argument skip it.",
            code=r"""def memo(fn):
    seen = {}
    def wrapper(n):
        if n not in seen:
            print("miss", n)
            seen[n] = fn(n)
        return seen[n]
    return wrapper
sq = memo(lambda n: n * n)
print(sq(3), sq(3), sq(4))""",
            output="miss 3\nmiss 4\n9 9 16",
            point="A closure variable (seen) is the cache.",
        ),
        Slide(
            title="A validator that raises",
            text="A wrapper can check the arguments before calling the real function and raise an error if they are bad.",
            code=r"""def positive(fn):
    def wrapper(x):
        if x <= 0: raise ValueError("must be positive")
        return fn(x)
    return wrapper
try:
    print(positive(float)(4))
    positive(float)(-4)
except ValueError as e:
    print(e)""",
            output="4.0\nmust be positive",
            point="Put the checks in a decorator and every function gets them.",
        ),
        Slide(
            title="Class decorators",
            text="A decorator can also take a class and return it, perhaps with something added. @dataclass works exactly this way.",
            code=r"""def add_hello(cls):
    cls.hello = lambda self: "hello from " + cls.__name__
    return cls
@add_hello
class Dog:
    pass
print(Dog().hello())""",
            output="hello from Dog",
            point="A class decorator receives the class and returns a class.",
        ),
        Slide(
            title="Decorating methods",
            text="A method gets self as its first argument, so the wrapper must accept and pass it on like any other argument.",
            code=r"""def loud(fn):
    def wrapper(self, *a):
        return fn(self, *a).upper()
    return wrapper
class Greeter:
    name = "sam"
    @loud
    def greet(self):
        return "hi " + self.name
print(Greeter().greet())""",
            output="HI SAM",
            point="In a method wrapper, take self first, then *args.",
        ),
        Slide(
            title="functools.lru_cache and cache_info",
            text="lru_cache is a ready-made memoizer. cache_info() reports how often it found an answer already stored.",
            code=r"""from functools import lru_cache
@lru_cache(maxsize=None)
def sq(n):
    return n * n
print(sq(2), sq(2), sq(3))
print(sq.cache_info())""",
            output="4 4 9\nCacheInfo(hits=1, misses=2, maxsize=None, currsize=2)",
            point="Hits are answers reused, misses are answers computed.",
        ),
        Slide(
            title="property is a decorator",
            text="@property turns a method into an attribute you read without parentheses. The value is worked out each time you ask.",
            code=r"""class Circle:
    def __init__(self, r):
        self.r = r
    @property
    def area(self):
        return 3 * self.r ** 2
c = Circle(2)
print(c.area)
c.r = 3
print(c.area)""",
            output="12\n27",
            point="A property looks like data but runs code on every read.",
        ),
        Slide(
            title="A decorator that registers",
            text="A decorator does not have to wrap anything. It can note the function somewhere and hand it back unchanged.",
            code=r"""registry = []
def register(fn):
    registry.append(fn.__name__)
    return fn
@register
def a():
    return 1
print(registry, a())""",
            output="['a'] 1",
            point="Return the same function and a decorator becomes a hook.",
        ),
    ),
)
