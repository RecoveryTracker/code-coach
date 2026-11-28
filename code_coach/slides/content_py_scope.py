"""Scope and Namespaces: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 89

DECK = Deck(
    id="py-scope",
    title="Scope and Namespaces",
    language="python",
    blurb="Where a name lives and how Python finds it: local, enclosing, global, built-in, and the keywords that change the rules.",
    slides=(
        Slide(
            title="Local vs global",
            text="A name made inside a function is local to it. A name made at the top of the file is global. Two names can match without being the same variable.",
            code=r"""x = "global"
def f():
    x = "local"
    print(x)
f()
print(x)""",
            output="local\nglobal",
            point="Assigning inside a function makes a new local name.",
        ),
        Slide(
            title="LEGB: the lookup order",
            text="Python looks for a name in four places in order: Local, Enclosing functions, Global, then Built-in. The first place that has it wins.",
            code=r"""y = "global y"
def outer():
    x = "enclosing x"
    def inner():
        print(x)
        print(y)
        print(len("ab"))
    inner()
outer()""",
            output="enclosing x\nglobal y\n2",
            point="Local, Enclosing, Global, Built-in - in that order.",
        ),
        Slide(
            title="Reading a global vs assigning to it",
            text="Reading a global from inside a function works. But if the function assigns to the same name anywhere, that name is local for the whole function.",
            code=r"""count = 0
def bump():
    count = count + 1
try:
    bump()
except UnboundLocalError as e:
    print(type(e).__name__)
print(count)""",
            output="UnboundLocalError\n0",
            point="Assign anywhere in a function and the name is local everywhere in it.",
        ),
        Slide(
            title="The global keyword",
            text="Declare a name global inside a function to change the module-level variable instead of making a local one.",
            code=r"""count = 0
def bump():
    global count
    count += 1
bump()
bump()
print(count)""",
            output="2",
            point="global count means: this name is the top-level one.",
        ),
        Slide(
            title="nonlocal in a closure",
            text="nonlocal lets an inner function change a variable of the function around it. Without it, the assignment would make a new local.",
            code=r"""def counter():
    n = 0
    def tick():
        nonlocal n
        n += 1
        return n
    return tick
t = counter()
print(t(), t(), t())""",
            output="1 2 3",
            point="nonlocal reaches one level out; the variable lives on between calls.",
        ),
        Slide(
            title="Closures capture variables, not values",
            text="A function remembers the variable, not the value it had. Lambdas made in a loop all see the loop variable's last value, unless you freeze it with a default.",
            code=r"""fs = [lambda: i for i in range(3)]
print([f() for f in fs])
fs = [lambda i=i: i for i in range(3)]
print([f() for f in fs])
x = 1
def show():
    return x
x = 2
print(show())""",
            output="[2, 2, 2]\n[0, 1, 2]\n2",
            point="Closures look the variable up when called, not when defined.",
        ),
        Slide(
            title="Loop variables leak out",
            text="A for loop does not have its own scope. Its variable stays alive after the loop, but only if the loop ran at least once.",
            code=r"""for i in range(3):
    pass
print(i)
for name in []:
    pass
try:
    print(name)
except NameError as e:
    print(type(e).__name__)""",
            output="2\nNameError",
            point="After a for loop, the loop variable still holds its last value.",
        ),
        Slide(
            title="Comprehension variables do not leak",
            text="A comprehension has a scope of its own, so its variable disappears once the comprehension is done.",
            code=r"""squares = [n * n for n in range(3)]
print(squares)
try:
    print(n)
except NameError:
    print("n is gone")""",
            output="[0, 1, 4]\nn is gone",
            point="Comprehensions keep their variable to themselves; for loops do not.",
        ),
        Slide(
            title="Builtins can be shadowed",
            text="Built-in names are the last place Python looks, so your own global with the same name hides them. del removes yours and the built-in is back.",
            code=r"""print(len("abc"))
len = 99
try:
    print(len("abc"))
except TypeError as e:
    print(type(e).__name__)
del len
print(len("abc"))""",
            output="3\nTypeError\n3",
            point="Do not name variables len, list, sum or max.",
        ),
        Slide(
            title="del removes a name",
            text="del deletes the name, not the object it pointed at. Using the name afterwards raises NameError.",
            code=r"""x = 5
print("x" in globals())
del x
print("x" in globals())
try:
    print(x)
except NameError:
    print("gone")""",
            output="True\nFalse\ngone",
            point="del unbinds a name; the object may live on if other names hold it.",
        ),
        Slide(
            title="globals() and locals()",
            text="A scope is really a dict from names to values. globals() and locals() show them. Printing a filtered, sorted view keeps the output readable.",
            code=r"""a = 1
b = 2
def f(p, q):
    r = p + q
    return sorted(locals())
print(f(1, 2))
names = sorted(k for k in globals() if not k.startswith("__"))
print(names)""",
            output="['p', 'q', 'r']\n['a', 'b', 'f']",
            point="A namespace is a dict: names on the left, objects on the right.",
        ),
        Slide(
            title="Class body scope",
            text="Names set in a class body are class attributes. Methods cannot see them as bare names, so they must use self or the class name.",
            code=r"""class A:
    x = 10
    y = x + 1
    def get(self):
        return x
print(A.y)
try:
    A().get()
except NameError as e:
    print(type(e).__name__)""",
            output="11\nNameError",
            point="Inside a method, write self.x, never just x.",
        ),
        Slide(
            title="Default arguments: evaluated once",
            text="A default value is worked out when the def runs, not on each call. Changing the variable afterwards does not change the default.",
            code=r"""x = "first"
def show(v=x):
    return v
x = "second"
print(show())
print(show(x))""",
            output="first\nsecond",
            point="Defaults are frozen at definition time.",
        ),
        Slide(
            title="Each call gets fresh locals",
            text="Local variables are created anew every time a function is called and disappear when it returns. Nothing is carried between calls.",
            code=r"""def f():
    total = 0
    total += 1
    return total
print(f(), f(), f())""",
            output="1 1 1",
            point="To remember something between calls, use a global, a closure or an object.",
        ),
        Slide(
            title="Changing a global without global",
            text="global is only needed to rebind a name. Calling a method that changes a global list in place needs no declaration.",
            code=r"""log = []
def add(x):
    log.append(x)
add("a")
add("b")
print(log)""",
            output="['a', 'b']",
            point="Rebinding needs global; mutating does not.",
        ),
    ),
)
