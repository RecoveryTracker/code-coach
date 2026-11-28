"""Modules and Imports: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 90

DECK = Deck(
    id="py-modules",
    title="Modules and Imports",
    language="python",
    blurb="How import works: modules as namespaces, from-imports, the __main__ idiom, caching, packages and the standard library.",
    slides=(
        Slide(
            title="import and use",
            text="import brings in a whole module. You reach what is inside it with a dot.",
            code=r"""import math
print(math.sqrt(16))
print(math.pi)""",
            output="4.0\n3.141592653589793",
            point="import math, then math.name.",
        ),
        Slide(
            title="from ... import",
            text="from-import copies chosen names straight into your file, so you use them without the module prefix.",
            code=r"""from math import sqrt, floor
print(sqrt(25))
print(floor(2.7))""",
            output="5.0\n2",
            point="from m import x lets you write x instead of m.x.",
        ),
        Slide(
            title="Renaming with as",
            text="as gives an import another name. It is handy for long names or to avoid a clash.",
            code=r"""import collections as c
from math import factorial as fact
print(c.Counter("aab")["a"])
print(fact(5))""",
            output="2\n120",
            point="import x as y: the module keeps working, under a new name.",
        ),
        Slide(
            title="A module is a namespace",
            text="A module is an object that holds names. Its own pi and your pi live in different namespaces, so they never collide.",
            code=r"""import math
print(type(math).__name__)
print(math.__name__)
pi = 3
print(pi, math.pi)""",
            output="module\nmath\n3 3.141592653589793",
            point="module.name keeps names from different files apart.",
        ),
        Slide(
            title="__name__ and the main idiom",
            text="Every module has a __name__. For the file you run it is '__main__'; when the file is imported it is the module's own name. The idiom below runs code only when run directly.",
            code=r"""def main():
    print("running main")
print(__name__)
if __name__ == "__main__":
    main()""",
            output="__main__\nrunning main",
            point="if __name__ == '__main__': runs only when the file is the script.",
        ),
        Slide(
            title="Using the standard library",
            text="Python ships with many modules. collections and math are two you will meet constantly.",
            code=r"""from collections import deque, namedtuple
from math import gcd, ceil
Pt = namedtuple("Pt", "x y")
print(Pt(1, 2))
print(gcd(12, 18), ceil(2.1))
print(deque([1, 2], maxlen=2))""",
            output="Pt(x=1, y=2)\n6 3\ndeque([1, 2], maxlen=2)",
            point="Batteries included: check the standard library before writing it yourself.",
        ),
        Slide(
            title="Imports are cached",
            text="The first import runs the module and stores it in sys.modules. Later imports just fetch the stored module, so the file's code runs only once.",
            code=r"""import sys
print("json" in sys.modules)
import json
print("json" in sys.modules)
import json
print(sys.modules["json"] is json)""",
            output="False\nTrue\nTrue",
            point="sys.modules is the cache: import twice, run once.",
        ),
        Slide(
            title="dir() of a module",
            text="dir() lists the names in a module. Real modules have dozens, so filter to the ones you care about.",
            code=r"""import math
names = [n for n in dir(math) if n in ("pi", "sqrt", "ceil", "hypot")]
print(names)
print(len(dir(math)) > 40)""",
            output="['ceil', 'hypot', 'pi', 'sqrt']\nTrue",
            point="dir(module) is a quick menu of what a module offers.",
        ),
        Slide(
            title="Packages and __init__.py",
            text="A package is a folder of modules, often with an __init__.py file inside. You reach its parts with dots, like collections.abc or os.path.",
            code=r"""import os.path
import collections.abc
print(os.path.basename("/x/y.txt"))
print(collections.abc.__name__)""",
            output="y.txt\ncollections.abc",
            point="A folder with modules in it is a package; dots walk down into it.",
        ),
        Slide(
            title="Relative imports",
            text="Inside a package, a leading dot means 'from here'. In a file of package shop, writing from . import cart pulls in the sibling module, and from ..util import tidy goes one level up.",
            point="One dot is the current package, two dots is its parent; they only work inside packages.",
        ),
        Slide(
            title="Circular imports",
            text="If a imports b while b imports a, one of them is only half-loaded when the other needs it, and you get an ImportError or a missing name. Fix it by moving shared code into a third module, or by importing inside the function that needs it.",
            point="Two modules that import each other are a design smell: pull the shared part out.",
        ),
        Slide(
            title="importlib.import_module",
            text="When a module's name is only known while the program runs, import_module loads it from a string.",
            code=r"""import importlib
m = importlib.import_module("math")
print(m.sqrt(9))
name = "json"
j = importlib.import_module(name)
print(j.dumps({"a": 1}))""",
            output='3.0\n{"a": 1}',
            point="import_module('name') is import with the name held in a variable.",
        ),
        Slide(
            title="A tour of the standard library",
            text="string has text constants, statistics has mean and median, textwrap tidies paragraphs. Others worth knowing: pathlib, json, datetime, itertools, functools, re, csv and argparse.",
            code=r"""import string, textwrap, statistics
print(string.ascii_lowercase[:5])
print(statistics.mean([1, 2, 3, 4]))
print(textwrap.shorten("hello big wide world", width=14))""",
            output="abcde\n2.5\nhello [...]",
            point="Skim the standard library index once; you will recognise needs later.",
        ),
        Slide(
            title="Virtual environments and pip",
            text="Outside libraries come from PyPI through pip. Give each project its own virtual environment (python -m venv .venv) so its packages never clash with another project's.",
            point="One project, one venv; pip install goes into whichever venv is active.",
        ),
        Slide(
            title="from x import * and why not",
            text="import * dumps every public name of a module into your file. You cannot tell where a name came from, and it can silently replace your own names.",
            code=r"""from math import *
print(sqrt(4), pi > 3)""",
            output="2.0 True",
            point="Import the names you use, one by one.",
        ),
    ),
)
