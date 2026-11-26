"""The code magnet puzzles in Python.

The same puzzle as the other languages: the lines of a program that
works, jumbled, to be put back in an order that prints the right thing.

Python is the one language here where a magnet carries half its own
answer. Each line keeps its indentation, and the indentation IS the
block structure: a line indented under the `for` is in the loop, and the
same text at the left margin would not be. So the question is mostly
which block a line belongs to and in what order the blocks run.

Like Ruby, Python runs a file top to bottom, `def` and `class` included.
A function exists once its `def` line has run, so a call above it is a
NameError rather than a different right answer. Two functions can still
go either way round, as long as both are defined before the first call
reaches them: a function body looks its names up when it runs, not when
it is defined.

The expected output beside each was typed out by a person and is held
to what Python actually prints by tests/test_magnets_python.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "Python"

PY_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-py-loop-total",
        plan=(
            ("Start with the prices and two counters", 3),
            ("Walk the prices and keep the big ones", 4),
            ("Report what was kept", 2),
        ),
        level=1,
        name="Add up the big ones in a loop",
        family=FAMILY,
        language="python",
        note=(
            "The counters have to be set before the loop, or the first "
            "`total += price` has nothing to add to. The two lines indented "
            "under the `if` only run for prices over 5, and the two prints at "
            "the left margin run once, after the loop has finished. Put a "
            "print inside the loop and it reports a running total instead."
        ),
        code=(
            "prices = [4, 10, 3, 8]\n"
            "total = 0\n"
            "count = 0\n"
            "for price in prices:\n"
            "    if price > 5:\n"
            "        total += price\n"
            "        count += 1\n"
            'print(count, "items over 5")\n'
            'print("total", total)'
        ),
        expect="2 items over 5\ntotal 18",
    ),
    _m(
        id="magnet-py-define-before-call",
        plan=(
            ("A function that shouts a word", 2),
            ("A greeting that uses the shout", 3),
            ("A wave that uses the greeting", 2),
            ("Greet one person and wave at another", 2),
        ),
        level=1,
        name="A function exists once its def has run",
        family=FAMILY,
        language="python",
        note=(
            "Python runs `def` like any other line: it makes the function "
            "when it gets there. So a call above all three defs is a "
            "NameError. The three defs can go in any order, though: `greet` "
            "only looks up `shout` when it is called, and by the time the "
            "prints at the bottom call it, every def has run."
        ),
        code=(
            "def shout(word):\n"
            '    return word.upper() + "!"\n'
            "def greet(name):\n"
            '    message = "Hello, " + shout(name)\n'
            "    return message\n"
            "def wave(name):\n"
            '    return greet(name) + " *waves*"\n'
            'print(greet("ann"))\n'
            'print(wave("bo"))'
        ),
        expect="Hello, ANN!\nHello, BO! *waves*",
    ),
    _m(
        id="magnet-py-dict-count",
        plan=(
            ("Split a sentence into words", 1),
            ("Count each word", 3),
            ("Find the most common one", 2),
            ("List the words seen more than once", 3),
        ),
        level=2,
        name="Count words with a dict",
        family=FAMILY,
        language="python",
        note=(
            "`counts.get(word, 0)` is the whole trick: a word not seen yet "
            "counts from 0 instead of raising a KeyError. `max(counts, "
            "key=counts.get)` walks the keys and picks the one whose count is "
            "biggest. The counting loop has to finish before either of the "
            "questions after it is asked, or they are answered about half a "
            "sentence."
        ),
        code=(
            'words = "the cat and the hat and the bat".split()\n'
            "counts = {}\n"
            "for word in words:\n"
            "    counts[word] = counts.get(word, 0) + 1\n"
            "best = max(counts, key=counts.get)\n"
            "print(best, counts[best])\n"
            "for word, n in sorted(counts.items()):\n"
            "    if n > 1:\n"
            "        print(word, n)"
        ),
        expect="the 3\nand 2\nthe 3",
    ),
    _m(
        id="magnet-py-class",
        plan=(
            ("Start the class", 1),
            ("Give each dog a name and no tricks", 3),
            ("Teach a trick and hand the dog back", 3),
            ("Make a dog and teach it twice", 2),
            ("Say what it knows", 2),
        ),
        level=2,
        name="A class whose method hands itself back",
        family=FAMILY,
        language="python",
        note=(
            "`__init__` runs when `Dog(\"Rex\")` is called, and the list made "
            "there belongs to that one dog. `learn` ends with `return self`, "
            "which is what lets `.learn(\"sit\").learn(\"roll\")` chain: the "
            "second call is made on whatever the first one returned. Leave "
            "the return out and the second call is made on None."
        ),
        code=(
            "class Dog:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "        self.tricks = []\n"
            "    def learn(self, trick):\n"
            "        self.tricks.append(trick)\n"
            "        return self\n"
            'rex = Dog("Rex")\n'
            'rex.learn("sit").learn("roll")\n'
            'print(rex.name, "knows", len(rex.tricks))\n'
            'print(", ".join(rex.tricks))'
        ),
        expect="Rex knows 2\nsit, roll",
    ),
    _m(
        id="magnet-py-try-except",
        plan=(
            ("Try turning the text into a number", 3),
            ("When it is not a number", 3),
            ("When it is", 2),
            ("Whatever happened", 2),
            ("Parse one good and one bad", 2),
        ),
        level=3,
        name="try, except, else and finally",
        family=FAMILY,
        language="python",
        note=(
            "Only the line that can fail goes under `try`. `except` runs when "
            "it failed, `else` when it did not, and `finally` runs either way "
            "- even after a `return`. That is why \"checked 21\" prints before "
            "42: the function has decided to return 42, then runs `finally` "
            "on the way out, and only then does the print outside get the "
            "value."
        ),
        code=(
            "def parse(text):\n"
            "    try:\n"
            "        number = int(text)\n"
            "    except ValueError:\n"
            '        print("not a number:", text)\n'
            "        return 0\n"
            "    else:\n"
            "        return number * 2\n"
            "    finally:\n"
            '        print("checked", text)\n'
            'print(parse("21"))\n'
            'print(parse("x"))'
        ),
        expect="checked 21\n42\nnot a number: x\nchecked x\n0",
    ),
    _m(
        id="magnet-py-generator",
        plan=(
            ("Open the generator and announce it", 2),
            ("Hand out each number on the way down", 3),
            ("Announce the end", 1),
            ("Make one, then say so", 2),
            ("Pull every number out", 2),
        ),
        level=3,
        name="A generator runs when it is asked",
        family=FAMILY,
        language="python",
        note=(
            "Calling `countdown(3)` runs none of its body: it hands back a "
            "generator and waits. That is why \"made it\" prints before "
            "\"start\". Each turn of the `for` runs the body up to the next "
            "`yield` and pauses there. Put `n -= 1` above the `yield` and it "
            "hands out 2, 1, 0 instead of 3, 2, 1."
        ),
        code=(
            "def countdown(n):\n"
            '    print("start")\n'
            "    while n > 0:\n"
            "        yield n\n"
            "        n -= 1\n"
            '    print("liftoff")\n'
            "gen = countdown(3)\n"
            'print("made it")\n'
            "for value in gen:\n"
            "    print(value)"
        ),
        expect="made it\nstart\n3\n2\n1\nliftoff",
    ),
    _m(
        id="magnet-py-closure",
        plan=(
            ("Open the factory with its own count", 2),
            ("An inner function that bumps that count", 4),
            ("Hand the inner function back", 1),
            ("Make two separate counters", 2),
            ("Bump one three times and the other once", 2),
        ),
        level=4,
        name="A closure keeps its own count",
        family=FAMILY,
        language="python",
        note=(
            "Each call to `make_counter` makes a new `count` and a new `bump` "
            "that remembers it, so `a` and `b` count separately. `nonlocal` "
            "is what lets `bump` change the outer `count`: without it, "
            "`count += 1` makes a new local `count` and fails because that "
            "one has no value yet. The `return bump` sits at the factory's "
            "level, not inside `bump`."
        ),
        code=(
            "def make_counter():\n"
            "    count = 0\n"
            "    def bump():\n"
            "        nonlocal count\n"
            "        count += 1\n"
            "        return count\n"
            "    return bump\n"
            "a = make_counter()\n"
            "b = make_counter()\n"
            "print(a(), a(), a())\n"
            "print(b())"
        ),
        expect="1 2 3\n1",
    ),
    _m(
        id="magnet-py-decorator",
        plan=(
            ("Open the decorator", 1),
            ("A wrapper that reports before and after", 5),
            ("Hand the wrapper back", 1),
            ("A function to be wrapped", 3),
            ("Call it and use the answer", 1),
        ),
        level=4,
        name="A decorator wraps a function",
        family=FAMILY,
        language="python",
        note=(
            "`@logged` above `def add` means `add = logged(add)`: the name "
            "`add` ends up pointing at `wrapper`, which reports, calls the "
            "real `add`, reports again and passes the answer back. The "
            "decorator line has to sit directly above the def it decorates, "
            "and `logged` has to be defined before that line runs. Forget "
            "`return result` and the caller gets None."
        ),
        code=(
            "def logged(func):\n"
            "    def wrapper(*args):\n"
            '        print("calling", func.__name__, args)\n'
            "        result = func(*args)\n"
            '        print("got", result)\n'
            "        return result\n"
            "    return wrapper\n"
            "@logged\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "print(add(2, 3) * 10)"
        ),
        expect="calling add (2, 3)\ngot 5\n50",
    ),
    _m(
        id="magnet-py-context-manager",
        plan=(
            ("Bring in the helper", 1),
            ("A section that opens and closes around a body", 5),
            ("Run a body inside the section", 2),
            ("Carry on after it", 1),
        ),
        level=5,
        name="A context manager from a generator",
        family=FAMILY,
        language="python",
        note=(
            "`@contextmanager` turns a generator into something `with` can "
            "use. Everything above the `yield` runs on the way in, the value "
            "yielded is what `as name` receives, the indented body runs while "
            "the generator is paused, and everything below the `yield` runs "
            "on the way out. The import has to come first, before the "
            "decorator line that uses it."
        ),
        code=(
            "from contextlib import contextmanager\n"
            "@contextmanager\n"
            "def section(title):\n"
            '    print("<" + title + ">")\n'
            "    yield title.upper()\n"
            '    print("</" + title + ">")\n'
            'with section("menu") as name:\n'
            '    print("inside", name)\n'
            'print("after")'
        ),
        expect="<menu>\ninside MENU\n</menu>\nafter",
    ),
)
