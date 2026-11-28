"""Python Data Types: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

DECK = Deck(
    id="py-types",
    title="Python Data Types",
    language="python",
    blurb="Numbers, text, True and False, None, and the four containers - what each one is and how it behaves.",
    slides=(
        Slide(
            title="Numbers: / and // and %",
            text="A whole number is an int. Dividing with / always gives a decimal answer; // throws the remainder away; % gives only the remainder.",
            code=r"""print(7 + 2)
print(7 / 2)
print(7 // 2)
print(7 % 2)""",
            output="9\n3.5\n3\n1",
            point="/ gives a decimal, // gives the whole part, % gives what is left over.",
        ),
        Slide(
            title="Whole numbers and decimals",
            text="A number with a decimal point is a float. Mix an int with a float and the answer is a float; ** means 'to the power of'.",
            code=r"""print(3 * 2)
print(3 * 2.0)
print(2 ** 10)""",
            output="6\n6.0\n1024",
            point="6 and 6.0 look alike but are different types.",
        ),
        Slide(
            title="str: text",
            text="A str is a piece of text in quotes. You can pick a letter by its position, counting from 0; a negative position counts from the end.",
            code=r"""word = "python"
print(word[0])
print(word[-1])
print(len(word))
print(word.upper())""",
            output="p\nn\n6\nPYTHON",
            point="Positions start at 0, and -1 is the last one.",
        ),
        Slide(
            title="str: slices and immutability",
            text="A slice [a:b] takes the letters from a up to, but not including, b. A str can never be changed in place - writing word[0] = 'J' is an error - so you build a new one.",
            code=r"""word = "python"
print(word[1:4])
print(word[:2])
print(word[::-1])
word = "J" + word[1:]
print(word)""",
            output="yth\npy\nnohtyp\nJython",
            point="Strings are immutable: make a new string instead of editing one.",
        ),
        Slide(
            title="bool and truthiness",
            text="A bool is True or False. Other values count as false when they are empty or zero, and as true otherwise; bool() shows which.",
            code=r"""print(True and False)
print(bool(0), bool(""), bool([]))
print(bool(5), bool("hi"), bool([0]))""",
            output="False\nFalse False False\nTrue True True",
            point="Zero and empty things are falsy; everything else is truthy.",
        ),
        Slide(
            title="None: nothing here",
            text="None is Python's way to say 'no value'. Check for it with 'is None', not with ==.",
            code=r"""result = None
print(result)
print(result is None)
print(bool(result))""",
            output="None\nTrue\nFalse",
            point="Test for None with 'is None'.",
        ),
        Slide(
            title="list: an ordered, changeable row",
            text="A list holds items in order and can be changed. append adds to the end, insert adds at a position, and pop removes and returns the last item.",
            code=r"""nums = [3, 1, 2]
nums.append(4)
nums.insert(0, 9)
last = nums.pop()
print(nums, last)""",
            output="[9, 3, 1, 2] 4",
            point="Lists are mutable: these methods change the list itself.",
        ),
        Slide(
            title="tuple: a fixed bundle",
            text="A tuple is like a list that cannot change after it is made. Packing puts values into one tuple; unpacking pulls them back out into names.",
            code=r"""point = (3, 4)
x, y = point
print(x, y)
pair = 1, 2
print(pair)""",
            output="3 4\n(1, 2)",
            point="Tuples are immutable; unpack them to name the parts.",
        ),
        Slide(
            title="dict: look things up by key",
            text="A dict pairs keys with values. dict[key] fetches a value and fails if the key is missing; .get(key) gives None instead, or a default you choose.",
            code=r"""ages = {"ann": 30, "bob": 25}
print(ages["ann"])
print(ages.get("cy"))
print(ages.get("cy", 0))
ages["cy"] = 41
print(ages)""",
            output="30\nNone\n0\n{'ann': 30, 'bob': 25, 'cy': 41}",
            point="Use .get() when a key might not be there.",
        ),
        Slide(
            title="dict: items and order",
            text="A dict remembers the order its keys were added. .items() hands you each key with its value, and .keys() gives just the keys.",
            code=r"""ages = {"ann": 30, "bob": 25}
for name, age in ages.items():
    print(name, age)
print(list(ages.keys()))""",
            output="ann 30\nbob 25\n['ann', 'bob']",
            point="Loop over .items() to get key and value together.",
        ),
        Slide(
            title="set: unique things",
            text="A set keeps one copy of each item and has no position. Asking 'is it in there?' with 'in' is quick; sorted() turns a set into an ordered list.",
            code=r"""tags = {"a", "b", "a", "c"}
print(len(tags))
print("b" in tags)
print(sorted(tags))""",
            output="3\nTrue\n['a', 'b', 'c']",
            point="A set drops duplicates and answers 'in' fast.",
        ),
        Slide(
            title="type() and isinstance()",
            text="type() tells you what kind of value you have. isinstance(value, kind) answers yes or no; True counts as an int because a bool is a special kind of int.",
            code=r"""print(type(42))
print(type("hi"))
print(isinstance(3.5, float))
print(isinstance(True, int))""",
            output="<class 'int'>\n<class 'str'>\nTrue\nTrue",
            point="Prefer isinstance() when you need to check a type.",
        ),
        Slide(
            title="Mutable or immutable?",
            text="An immutable value (int, str, tuple) never changes - an 'edit' makes a new value. A mutable one (list, dict, set) can be changed in place.",
            code=r"""s = "hi"
t = s
t = t + "!"
print(s, t)""",
            output="hi hi!",
            point="Changing t made a new string, so s stayed 'hi'.",
        ),
        Slide(
            title="Aliasing: two names, one list",
            text="b = a does not copy a list; both names point at the same one. Change it through either name and both see it - use .copy() for a separate list.",
            code=r"""a = [1, 2]
b = a
b.append(3)
print(a)
c = a.copy()
c.append(4)
print(a, c)""",
            output="[1, 2, 3]\n[1, 2, 3] [1, 2, 3, 4]",
            point="Assignment shares mutable things; copy when you need your own.",
        ),
        Slide(
            title="Converting between types",
            text="int(), str(), float() and list() build a new value of that kind from another one. int() of a float cuts off the decimals rather than rounding.",
            code=r"""print(int("3") + 4)
print(str(3) + "4")
print(list("abc"))
print(int(3.9))
print(float("2.5"))""",
            output="7\n34\n['a', 'b', 'c']\n3\n2.5",
            point="Convert on purpose: '3' + 4 is an error, int('3') + 4 is 7.",
        ),
    ),
)
