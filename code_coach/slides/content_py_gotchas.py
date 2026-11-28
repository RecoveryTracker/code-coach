"""Python Gotchas: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 70

DECK = Deck(
    id="py-gotchas",
    title="Python Gotchas",
    language="python",
    blurb="Traps that catch everyone once: shared defaults, closures in loops, is vs ==, rounding, aliasing and more.",
    slides=(
        Slide(
            title="Mutable default arguments",
            text="A default value is made ONCE, when the function is defined, not on each call. A default list is therefore shared by every call that does not pass its own.",
            code=r"""def add(x, bag=[]):
    bag.append(x)
    return bag
print(add(1))
print(add(2))""",
            output="[1]\n[1, 2]",
            point="Use bag=None and make the list inside the function.",
        ),
        Slide(
            title="Late-binding closures in a loop",
            text="A function made in a loop looks up the loop variable when it is CALLED, by which time the loop has finished. Binding the value as a default argument freezes it.",
            code=r"""fs = [lambda: i for i in range(3)]
print([f() for f in fs])
gs = [lambda i=i: i for i in range(3)]
print([g() for g in gs])""",
            output="[2, 2, 2]\n[0, 1, 2]",
            point="Closures see the variable, not its value at the time.",
        ),
        Slide(
            title="is vs ==",
            text="== asks 'do they hold equal contents?'. is asks 'are they the very same object?'. Two equal lists are different objects. Use is for None, and == for values.",
            code=r"""a = [1, 2]
b = [1, 2]
c = a
print(a == b, a is b, a is c)
x = None
print(x is None)""",
            output="True False True\nTrue",
            point="is None, but == for everything else.",
        ),
        Slide(
            title="Division with negatives",
            text="// rounds DOWN toward minus infinity, not toward zero, so -7 // 2 is -4. The % result then takes the sign of the right side. int() on a float just cuts off the decimals.",
            code=r"""print(-7 // 2, -7 % 2, 7 // 2)
print(int(-7 / 2))""",
            output="-4 1 3\n-3",
            point="// floors. For 'cut off the decimals' use int(a / b).",
        ),
        Slide(
            title="Floats and round()",
            text="Computers store most decimals in binary, so 0.1 + 0.2 is a hair off 0.3. And round() sends exact halves to the nearest EVEN number, so 2.5 becomes 2.",
            code=r"""print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(round(2.5), round(3.5))""",
            output="0.30000000000000004\nFalse\n2 4",
            point="Never compare floats with ==; round() rounds halves to even.",
        ),
        Slide(
            title="Changing a list while looping",
            text="Removing items from a list as you loop over it makes the loop skip the item after each removal. Build a new list instead.",
            code=r"""nums = [2, 4, 6, 7]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)
print([n for n in [2, 4, 6, 7] if n % 2])""",
            output="[4, 7]\n[7]",
            point="Loop over a copy, or build a new list.",
        ),
        Slide(
            title="[[]] * 3 shares one list",
            text="Multiplying a list repeats the SAME inner object, it does not copy it. All three rows are one list. A comprehension builds a fresh list each time.",
            code=r"""g = [[]] * 3
g[0].append("x")
print(g)
h = [[] for _ in range(3)]
h[0].append("x")
print(h)""",
            output="[['x'], ['x'], ['x']]\n[['x'], [], []]",
            point="For a grid of lists, use a comprehension.",
        ),
        Slide(
            title="Strings cannot be changed",
            text="A string is immutable: you cannot assign to one of its letters. To 'change' it, build a new string from pieces of the old one.",
            code=r"""s = "cat"
try:
    s[0] = "b"
except TypeError:
    print("cannot change")
print("b" + s[1:])""",
            output="cannot change\nbat",
            point="Strings are read-only; make a new one instead.",
        ),
        Slide(
            title="One-item tuples need a comma",
            text="It is the comma that makes a tuple, not the brackets. (5) is just the number 5 in brackets, while (5,) is a tuple of one item.",
            code=r"""a = (5)
b = (5,)
print(type(a).__name__, type(b).__name__)
print(len(b))""",
            output="int tuple\n1",
            point="One item: write (x,) with the comma.",
        ),
        Slide(
            title="and / or return an operand",
            text="and and or do not return True or False. They return one of the two values they were given: or gives the first truthy one, and gives the first falsy one, or the last.",
            code=r"""print(0 or "default")
print("a" and "b")
print([] and "x")
print(3 or 4)""",
            output="default\nb\n[]\n3",
            point="x or default is a handy way to fill in an empty value.",
        ),
        Slide(
            title="Chained comparisons",
            text="Python lets you chain comparisons like in mathematics: 1 < x < 5 means 1 < x and x < 5. It is neat, but the same rule applies to any chain.",
            code=r"""x = 3
print(1 < x < 5)
x = 7
print(1 < x < 5)
print(x == 7 > 2)""",
            output="True\nFalse\nTrue",
            point="a < b < c reads like maths and works like maths.",
        ),
        Slide(
            title="list.sort() returns None",
            text="Methods that change a list in place return None, so nums = nums.sort() throws your list away. sorted() makes and returns a new sorted list.",
            code=r"""nums = [3, 1, 2]
print(nums.sort())
print(nums)
print(sorted([3, 1, 2]))""",
            output="None\n[1, 2, 3]\n[1, 2, 3]",
            point="In place means it returns None.",
        ),
        Slide(
            title="Shadowing a builtin",
            text="Naming your own variable list, str or max hides the builtin of that name, and later calls to it fail in confusing ways. Deleting your name brings the builtin back.",
            code=r"""list = [1, 2]
try:
    list("ab")
except TypeError:
    print("list is no longer the type")
del list
print(list("ab"))""",
            output="list is no longer the type\n['a', 'b']",
            point="Do not name variables list, str, dict, sum, max or input.",
        ),
        Slide(
            title="+= on a list changes the caller's list",
            text="For a list, xs += [9] extends the same list in place, so the caller sees it. xs = xs + [9] builds a new list and only changes the local name.",
            code=r"""def f(xs):
    xs += [9]
def g(xs):
    xs = xs + [9]
a = [1]
f(a)
g(a)
print(a)""",
            output="[1, 9]",
            point="+= mutates a list; + makes a new one.",
        ),
        Slide(
            title="Empty containers are falsy",
            text="An empty list, dict or string, the number 0 and None all count as False in an if. A list holding even a single 0 is not empty, so it counts as True.",
            code=r"""print([bool(v) for v in ([], {}, "", 0, None, [0])])""",
            output="[False, False, False, False, False, True]",
            point="if items: means 'items is not empty'.",
        ),
    ),
)
