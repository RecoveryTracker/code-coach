"""Objects and References: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 91

DECK = Deck(
    id="py-objects",
    title="Objects and References",
    language="python",
    blurb="Names point at objects: why assignment does not copy, what is and == compare, and how copies and arguments behave.",
    slides=(
        Slide(
            title="Names point to objects",
            text="A variable is a name stuck on an object, not a box that holds a value. Giving the object a second name does not copy it.",
            code=r"""a = [1, 2]
b = a
print(a is b)
b.append(3)
print(a)""",
            output="True\n[1, 2, 3]",
            point="b = a makes a second name for the same object.",
        ),
        Slide(
            title="Rebinding vs mutating",
            text="Mutating changes the object itself, and every name sees it. Assigning a new object to a name only moves that one name.",
            code=r"""a = [1, 2]
b = a
b = [9]
print(a, b)
a = a + [3]
print(a, b)""",
            output="[1, 2] [9]\n[1, 2, 3] [9]",
            point="name = something moves the name; name.append(...) changes the thing.",
        ),
        Slide(
            title="Mutation is seen through every name",
            text="Every name, and every container, that refers to the object sees a change made through any one of them.",
            code=r"""team = ["ann"]
alias = team
holder = {"people": team}
alias.append("bob")
print(team)
print(holder["people"])
print(holder["people"] is alias)""",
            output="['ann', 'bob']\n['ann', 'bob']\nTrue",
            point="One object, many references: change it once, see it everywhere.",
        ),
        Slide(
            title="is vs ==",
            text="== asks whether two objects have equal contents. is asks whether they are the very same object. Use is for None.",
            code=r"""a = [1, 2]
b = [1, 2]
c = a
print(a == b, a is b)
print(a == c, a is c)
x = None
print(x is None)""",
            output="True False\nTrue True\nTrue",
            point="== compares what is inside; is compares which object it is.",
        ),
        Slide(
            title="copy vs deepcopy",
            text="copy.copy makes a new outer list but shares the inner ones. copy.deepcopy copies all the way down.",
            code=r"""import copy
grid = [[1], [2]]
shallow = copy.copy(grid)
deep = copy.deepcopy(grid)
grid[0].append(9)
print(shallow)
print(deep)
print(shallow[0] is grid[0], shallow is grid)""",
            output="[[1, 9], [2]]\n[[1], [2]]\nTrue False",
            point="Shallow copies share the nested objects; deep copies do not.",
        ),
        Slide(
            title="Arguments are passed by reference",
            text="A function receives references to the caller's objects. Mutating a list changes the caller's list, but rebinding a number inside leaves the caller's number alone.",
            code=r"""def change(items, n):
    items.append(1)
    n += 1
nums, count = [], 0
change(nums, count)
print(nums, count)""",
            output="[1] 0",
            point="A function can mutate what it is given, but it cannot rebind your name.",
        ),
        Slide(
            title="Rebinding a parameter",
            text="Assigning a new object to a parameter only moves the function's own name. To change the caller's list, mutate it in place.",
            code=r"""def reset(items):
    items = []
    return items
nums = [1, 2]
reset(nums)
print(nums)
def clear(items):
    items.clear()
clear(nums)
print(nums)""",
            output="[1, 2]\n[]",
            point="items = [] does nothing outside; items.clear() does.",
        ),
        Slide(
            title="An immutable tuple holding a list",
            text="A tuple's slots cannot be reassigned, but if a slot holds a list, that list can still change. Immutable is only skin deep.",
            code=r"""t = (1, [2, 3])
t[1].append(4)
print(t)
try:
    t[0] = 9
except TypeError as e:
    print(type(e).__name__)""",
            output="(1, [2, 3, 4])\nTypeError",
            point="The tuple always holds the same objects; those objects may still change.",
        ),
        Slide(
            title="+= on lists vs ints",
            text="On a list, += changes the list in place, so every name sees it. On an int it builds a new number and rebinds the name.",
            code=r"""a = [1]
b = a
a += [2]
print(b)
x = 1
y = x
x += 1
print(x, y)""",
            output="[1, 2]\n2 1",
            point="+= mutates mutable objects and rebinds immutable ones.",
        ),
        Slide(
            title="Everything is an object",
            text="Numbers, functions, classes and even None are objects with a type. type() tells you which.",
            code=r"""print(type(3).__name__)
print(type(len).__name__)
print(type(type).__name__)
print(type(None).__name__)
print(isinstance(3, object), isinstance(len, object))""",
            output="int\nbuiltin_function_or_method\ntype\nNoneType\nTrue True",
            point="If you can name it, it is an object.",
        ),
        Slide(
            title="Even functions have attributes",
            text="Because a function is an object, you can attach data to it. Numbers carry methods too, even written in brackets like (255).",
            code=r"""def f():
    pass
f.note = "hi"
print(f.note)
print((255).bit_length())
print("abc".upper.__name__)""",
            output="hi\n8\nupper",
            point="Objects have attributes and methods: functions and numbers included.",
        ),
        Slide(
            title="Garbage collection",
            text="Python counts the references to each object. When the last name is gone, the object's memory is freed automatically, and a separate collector cleans up objects that only point at each other in a cycle.",
            point="You never free objects yourself: drop the last reference and Python tidies up.",
        ),
        Slide(
            title="Three ways to copy a list",
            text="A slice, list() and .copy() each make a new outer list. All three are shallow, which is fine for lists of numbers and strings.",
            code=r"""a = [1, 2]
b = a[:]
c = list(a)
d = a.copy()
a.append(3)
print(b, c, d)
print(b is c)""",
            output="[1, 2] [1, 2] [1, 2]\nFalse",
            point="a[:], list(a) and a.copy() give you a separate top-level list.",
        ),
        Slide(
            title="The same object in two places",
            text="Putting one list into a container twice stores two references to it, not two lists. A change through one slot shows in the other.",
            code=r"""row = [0, 0]
grid = [row, row]
grid[0][0] = 5
print(grid)
print(grid[0] is grid[1])""",
            output="[[5, 0], [5, 0]]\nTrue",
            point="Containers store references, so repeating an object repeats the reference.",
        ),
        Slide(
            title="== can be customised, is cannot",
            text="A class can define what == means, even to the point of saying yes to everything. is always asks the plain question: same object?",
            code=r"""class Always:
    def __eq__(self, other):
        return True
a = Always()
print(a == 1, a == "x")
print(a is None, a == None)""",
            output="True True\nFalse True",
            point="That is why we write 'is None' and not '== None'.",
        ),
    ),
)
