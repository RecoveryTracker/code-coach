"""More Python crashes: the second set.

Same rules as content_python.py - message from the bottom of the traceback,
line from its last frame, both held to a real run by
tests/test_errors_python.py - on mistakes the first fourteen do not cover:
calling a method on the class instead of an instance, a tuple that cannot
be changed, unpacking the wrong number of values, a string where an index
goes, `self` forgotten in a method, a file that is not there, a None
compared with a number, and iterating over a number.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c

PYTHON = "Python"


PY_CRASHES_2: tuple[Crash, ...] = (
    _c(
        id="err-py-tuple-assign",
        level=1,
        name="Changing a tuple",
        family=PYTHON,
        language="python",
        code=(
            "point = (3, 4)\n"
            "print(point[0])\n"
            "point[0] = 5\n"
            "print(point)"
        ),
        message="TypeError: 'tuple' object does not support item assignment",
        line=3,
        meaning="A tuple cannot be changed once made, so point[0] cannot be given a new value",
        decoys=(
            "point[0] does not exist, because a tuple counts its items from 1 rather than from 0",
            "5 is too large to fit in a point",
            "Tuples can only hold strings",
        ),
        fix=(
            "Round brackets make a tuple, and a tuple is immutable: reading "
            "point[0] works (line 2 proves it), changing it does not. Make a "
            "new tuple - point = (5, point[1]) - or use a list, [3, 4], if it "
            "really needs to change."
        ),
    ),
    _c(
        id="err-py-unpack-count",
        level=1,
        name="Unpacking into too few names",
        family=PYTHON,
        language="python",
        code=(
            "row = \"Ada,36,London\"\n"
            "name, age = row.split(\",\")\n"
            "print(name, age)"
        ),
        message="ValueError: too many values to unpack (expected 2)",
        line=2,
        meaning="split gave three values and there are only two names to put them in",
        decoys=(
            "split cannot split on a comma",
            "age has to be turned into a number with int() before it can be unpacked from the text",
            "row is too long to be split in one go",
        ),
        fix=(
            "`a, b = something` needs something to hold exactly two values. "
            "The row has three fields, so Python does not know where London "
            "goes. Name all three - name, age, city = ... - or keep the rest "
            "together with a star: name, *rest = row.split(\",\")."
        ),
    ),
    _c(
        id="err-py-str-index",
        level=2,
        name="A string where an index goes",
        family=PYTHON,
        language="python",
        code=(
            "names = [\"ann\", \"bo\", \"cy\"]\n"
            "pick = \"1\"\n"
            "print(names[pick])"
        ),
        message="TypeError: list indices must be integers or slices, not str",
        line=3,
        meaning="pick is the text \"1\", and a list position must be the number 1",
        decoys=(
            "names has no item at position 1",
            "A list of strings cannot be indexed",
            "print cannot show one item of a list",
        ),
        fix=(
            "Anything typed in or read from a file arrives as a string, and "
            "Python will not treat \"1\" as 1 for you. The message even names "
            "the type it got: str. Convert first - names[int(pick)] - and "
            "expect a ValueError if the text was not a number."
        ),
    ),
    _c(
        id="err-py-forgot-self",
        level=2,
        name="A method without self",
        family=PYTHON,
        language="python",
        code=(
            "class Counter:\n"
            "    def __init__(self):\n"
            "        self.n = 0\n"
            "    def bump():\n"
            "        return 1\n"
            "\n"
            "c = Counter()\n"
            "print(c.bump())"
        ),
        message="TypeError: Counter.bump() takes 0 positional arguments but 1 was given",
        line=8,
        meaning="Calling c.bump() passes c itself as the first argument, and bump has no parameter for it",
        decoys=(
            "bump was called before __init__ had finished setting self.n, so the object was not ready yet",
            "Methods cannot return a number",
            "c has to be made with Counter(0)",
        ),
        fix=(
            "'1 was given' when you passed nothing is the clue: Python hands "
            "the object to every method as its first argument. That is what "
            "self is for. Write def bump(self): - every method on an instance "
            "needs it, even one that never uses it."
        ),
    ),
    _c(
        id="err-py-missing-file",
        level=2,
        name="Opening a file that is not there",
        family=PYTHON,
        language="python",
        code=(
            "name = \"scores_2026.txt\"\n"
            "with open(name) as f:\n"
            "    print(f.read())"
        ),
        message="FileNotFoundError: [Errno 2] No such file or directory: 'scores_2026.txt'",
        line=2,
        meaning="There is no file called scores_2026.txt where the program is running",
        decoys=(
            "open needs a second argument, \"r\" or \"t\", saying that it is a text file to be read",
            "Files cannot be read inside a with block",
            "f.read() can only read files shorter than one line",
        ),
        fix=(
            "The file name is in the message, so first check the spelling - "
            "then check WHERE Python is looking. A bare name is looked for in "
            "the folder the program was started from, which is not always the "
            "folder the script is in. Use a full path, or catch "
            "FileNotFoundError and say so."
        ),
    ),
    _c(
        id="err-py-none-compare",
        level=3,
        name="Comparing nothing with a number",
        family=PYTHON,
        language="python",
        code=(
            "def best(scores):\n"
            "    for s in scores:\n"
            "        if s > 90:\n"
            "            return s\n"
            "\n"
            "top = best([70, 80])\n"
            "print(top > 50)"
        ),
        message="TypeError: '>' not supported between instances of 'NoneType' and 'int'",
        line=7,
        meaning="No score was over 90, so best fell off the end and returned None",
        decoys=(
            "scores cannot be compared with > inside a loop",
            "top is the whole list of scores, and a list cannot be compared with a single number",
            "50 has to be written as 50.0 to be compared",
        ),
        fix=(
            "A function that returns only from inside an if returns None when "
            "the if never comes true - here, no score beat 90. The crash is on "
            "the line that USED the result, a long way from the cause. Decide "
            "what best should give when nothing matches, and return it after "
            "the loop."
        ),
    ),
    _c(
        id="err-py-iterate-int",
        level=3,
        name="Looping over a number",
        family=PYTHON,
        language="python",
        code=(
            "count = 3\n"
            "for i in count:\n"
            "    print(\"go\", i)"
        ),
        message="TypeError: 'int' object is not iterable",
        line=2,
        meaning="A for loop needs something with items, and 3 is a single number",
        decoys=(
            "i has to be declared before the loop",
            "count must be bigger than 3 to loop over",
            "print cannot take two arguments",
        ),
        fix=(
            "'iterable' means 'something a for loop can walk through': a list, "
            "a string, a range. A bare int is not one. To loop three times, "
            "walk a range of that size: for i in range(count):."
        ),
    ),
    _c(
        id="err-py-class-not-instance",
        level=4,
        name="Calling a method on the class",
        family=PYTHON,
        language="python",
        code=(
            "class Dog:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def speak(self):\n"
            "        return self.name + \" says woof\"\n"
            "\n"
            "print(Dog.speak())"
        ),
        message="TypeError: Dog.speak() missing 1 required positional argument: 'self'",
        line=7,
        meaning="speak was called on the class Dog, not on a dog, so there is no self to pass",
        decoys=(
            "Dog has no method called speak",
            "speak has to be defined above __init__ in the class, or Python cannot find it when called",
            "A method cannot add strings together",
        ),
        fix=(
            "Dog is the class - the blueprint. A method needs an actual dog, "
            "made with Dog(\"Rex\"), to be self. Make one first: "
            "rex = Dog(\"Rex\"); print(rex.speak()). The message says 'self' "
            "is missing, which is Python's way of saying 'which dog?'."
        ),
    ),
)
