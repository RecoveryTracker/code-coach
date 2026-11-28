"""Type Hints: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 80

DECK = Deck(
    id="py-typehints",
    title="Type Hints",
    language="python",
    blurb="Notes about what kind of value goes where: for readers, editors and checkers, not for the running program.",
    slides=(
        Slide(
            title="Annotating parameters and returns",
            text="After a parameter write a colon and its type. After the brackets write -> and the type the function gives back. They are notes for the reader.",
            code=r"""def greet(name: str) -> str:
    return "hi " + name
print(greet("Ann"))""",
            output="hi Ann",
            point="def f(x: type) -> type:",
        ),
        Slide(
            title="Hints are not enforced",
            text="Python ignores hints when the program runs. Pass the 'wrong' type and the function still runs, doing whatever the code does with it.",
            code=r"""def double(n: int) -> int:
    return n * 2
print(double("ab"))
print(double(4))""",
            output="abab\n8",
            point="A hint is a promise to readers, not a check.",
        ),
        Slide(
            title="list[int] and dict[str, int]",
            text="Square brackets say what is inside a container: list[int] is a list of whole numbers, dict[str, int] maps text to whole numbers. Variables can carry hints too.",
            code=r"""def total(xs: list[int]) -> int:
    return sum(xs)
ages: dict[str, int] = {"ann": 30}
print(total([1, 2, 3]), ages)""",
            output="6 {'ann': 30}",
            point="container[inner type]",
        ),
        Slide(
            title="Optional and X | None",
            text="When a function sometimes gives back nothing, say so: int | None means 'a whole number or None'. The older spelling is Optional[int].",
            code=r"""def find(xs: list[int], t: int) -> int | None:
    return xs.index(t) if t in xs else None
print(find([5, 6], 6), find([5, 6], 9))""",
            output="1 None",
            point="X | None warns the reader to handle the None.",
        ),
        Slide(
            title="Union: one of several types",
            text="A | B means 'either type'. The older way is Union[A, B], and both mean the same. The function below accepts a number or a string.",
            code=r"""from typing import Union
def show(v: int | str) -> str:
    return str(v) + "!"
print(show(4), show("a"))
print(Union[int, str] == int | str)""",
            output="4! a!\nTrue",
            point="int | str is the modern spelling of Union[int, str].",
        ),
        Slide(
            title="tuple[int, ...]",
            text="A tuple hint can list each position, as in tuple[int, str]. Add ... to mean 'any number of items, all this type'.",
            code=r"""def total(t: tuple[int, ...]) -> int:
    return sum(t)
pair: tuple[int, str] = (1, "a")
print(total((1, 2, 3)), pair)""",
            output="6 (1, 'a')",
            point="tuple[int, str] is exactly two; tuple[int, ...] is any length.",
        ),
        Slide(
            title="Callable: a function as a value",
            text="Callable[[A, B], R] describes a function taking an A and a B and returning an R. It is how you hint a function that is passed in.",
            code=r"""from collections.abc import Callable
def apply(f: Callable[[int], int], x: int) -> int:
    return f(x)
print(apply(lambda n: n + 1, 4))""",
            output="5",
            point="Callable[[argument types], return type]",
        ),
        Slide(
            title="Type aliases",
            text="A long hint can be given a short name by assigning it to a variable. The name is then used wherever the long form would go.",
            code=r"""Point = tuple[float, float]
def norm1(p: Point) -> float:
    return abs(p[0]) + abs(p[1])
print(norm1((3.0, -4.0)))""",
            output="7.0",
            point="Point = tuple[float, float] names an idea once.",
        ),
        Slide(
            title="TypedDict: a dict with known keys",
            text="A TypedDict lists the keys a dict should have and each value's type. At run time it is still an ordinary dict; the list helps editors and checkers.",
            code=r"""from typing import TypedDict
class User(TypedDict):
    name: str
    age: int
u: User = {"name": "Ann", "age": 30}
print(u["name"], type(u).__name__)""",
            output="Ann dict",
            point="TypedDict describes the shape of a plain dict.",
        ),
        Slide(
            title="A dataclass with types",
            text="A dataclass needs its annotations: the typed names become its fields. This makes hints useful at run time too, though the types are still not checked.",
            code=r"""from dataclasses import dataclass
@dataclass
class P:
    x: int
    y: int = 0
print(P(1))""",
            output="P(x=1, y=0)",
            point="In a dataclass the annotations are how fields are declared.",
        ),
        Slide(
            title="__annotations__",
            text="Python keeps a function's hints in its __annotations__ dictionary. Tools read it, and so can you. The return hint is stored under the key 'return'.",
            code=r"""def f(a: int, b: str = "x") -> bool:
    return True
print(f.__annotations__)""",
            output="{'a': <class 'int'>, 'b': <class 'str'>, 'return': <class 'bool'>}",
            point="Hints are just data stored on the function.",
        ),
        Slide(
            title="Any: no promise at all",
            text="Any means 'could be anything', so a checker will not complain about what you do with it. Use it sparingly, when you really cannot say.",
            code=r"""from typing import Any
def show(x: Any) -> str:
    return str(x)
print(show(1), show([2]))""",
            output="1 [2]",
            point="Any switches the checking off for that value.",
        ),
        Slide(
            title="Generics with TypeVar",
            text="A TypeVar stands for 'some type, the same one throughout'. Below, first takes a list of T and gives back a T, whatever T is. It runs for any list.",
            code=r"""from typing import TypeVar
T = TypeVar("T")
def first(xs: list[T]) -> T:
    return xs[0]
print(first([7, 8]), first(["a"]))""",
            output="7 a",
            point="Same T in and out: a list of ints gives an int.",
        ),
        Slide(
            title="Why use type hints?",
            text="Editors use hints to autocomplete and warn about mistakes as you type. A checker such as mypy reads them to find bugs before you run anything. They also document what a function expects.",
            point="Hints cost nothing at run time and catch bugs early.",
        ),
        Slide(
            title="-> None for no result",
            text="A function that only does something, like printing, gives back None. Say so with -> None. Using its result is almost always a mistake.",
            code=r"""def log(msg: str) -> None:
    print(msg)
r = log("hi")
print(r)""",
            output="hi\nNone",
            point="-> None means 'do not use my result'.",
        ),
    ),
)
