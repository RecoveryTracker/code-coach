"""Python crashes.

Same rules as `content.py`: every message and line was copied from what
Python 3.13 printed, and tests/test_errors_python.py holds them to a real
run. They make one family of their own, "Python", the way the Dart and
Ruby sets did.

Python prints the traceback the other way up from Node: the calls first,
outermost at the top, and the message LAST. So the habit to build is
reading from the bottom. The last line is the sentence - the class of
error, a colon, what went wrong - and the frame just above it is where.
When the crash is inside a function, that bottom frame is the line in
the function, not the call at the end of the file, and that is the line
each of these blames.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c

PYTHON = "Python"


PY_CRASHES: tuple[Crash, ...] = (
    _c(
        id="err-py-name-typo",
        level=1,
        name="A name spelled two ways",
        family=PYTHON,
        language="python",
        code=(
            "scores = [70, 85, 90]\n"
            "total = sum(scores)\n"
            "print(total / len(score))"
        ),
        message="NameError: name 'score' is not defined. Did you mean: 'scores'?",
        line=3,
        meaning="There is no variable called score; the list is called scores",
        decoys=(
            "len cannot be used on a list of numbers, only on strings and other text",
            "total has not been given a value yet",
            "Division needs both sides to be whole numbers",
        ),
        fix=(
            "A NameError means Python looked a name up and found nothing by "
            "that name. Nothing is wrong with the list: the name asked for is "
            "one letter short of it. Python 3.12 and later add 'Did you "
            "mean' when a close match exists, and it is almost always right. "
            "Use the name as it was defined: len(scores)."
        ),
    ),
    _c(
        id="err-py-str-plus-int",
        level=1,
        name="Joining text and a number",
        family=PYTHON,
        language="python",
        code=(
            "name = \"Ada\"\n"
            "age = 36\n"
            "print(name + \" is \" + age)"
        ),
        message='TypeError: can only concatenate str (not "int") to str',
        line=3,
        meaning="A string can only be joined to another string, and age is an int",
        decoys=(
            "age has to be declared as a string before it can be printed with anything else",
            "print takes only one argument",
            "name was changed to a number on line 2",
        ),
        fix=(
            "'concatenate' is joining with +. Python will not turn the number "
            "into text for you the way JavaScript does: + between a str and "
            "an int is a mistake rather than a guess. Turn it into text "
            "yourself - str(age) - or, better, let an f-string do it: "
            "print(f\"{name} is {age}\")."
        ),
    ),
    _c(
        id="err-py-index-out-of-range",
        level=1,
        name="One past the end",
        family=PYTHON,
        language="python",
        code=(
            "colors = [\"red\", \"green\", \"blue\"]\n"
            "print(colors[0])\n"
            "print(colors[3])"
        ),
        message="IndexError: list index out of range",
        line=3,
        meaning="The list has 3 items, so its last index is 2, not 3",
        decoys=(
            "Lists in Python start counting at 1",
            "colors[0] removed the first item",
            "Strings cannot be stored in a list",
        ),
        fix=(
            "Indexes run from 0 to len - 1, so a three-item list has 0, 1 and "
            "2. Line 2 worked, which proves counting starts at 0. For the "
            "last item, ask for colors[-1] (or colors[len(colors) - 1]): "
            "negative indexes count from the end and never overshoot."
        ),
    ),
    _c(
        id="err-py-missing-key",
        level=1,
        name="A key the dict does not have",
        family=PYTHON,
        language="python",
        code=(
            "user = {\"name\": \"Ada\", \"city\": \"London\"}\n"
            "print(user[\"name\"])\n"
            "print(user[\"email\"])"
        ),
        message="KeyError: 'email'",
        line=3,
        meaning="The dict has no 'email' key, and square brackets insist on one",
        decoys=(
            "user stopped being a dict after line 2",
            "Keys have to be numbers, not strings",
            "The email is stored under a capital E",
        ),
        fix=(
            "A KeyError's message is just the key, in quotes - that is the "
            "whole sentence. Square brackets mean 'this key is there', so a "
            "missing one is an error, not None. When a key may be missing, "
            "ask with user.get(\"email\") (None if absent) or "
            "user.get(\"email\", \"none given\") for a default."
        ),
    ),
    _c(
        id="err-py-forgot-return",
        level=2,
        name="A function that forgot to return",
        family=PYTHON,
        language="python",
        code=(
            "def full_name(first, last):\n"
            "    name = first + \" \" + last\n"
            "\n"
            "who = full_name(\"Ada\", \"Lovelace\")\n"
            "print(who.upper())"
        ),
        message="AttributeError: 'NoneType' object has no attribute 'upper'",
        line=5,
        meaning="full_name returned None, because it has no return line",
        decoys=(
            "upper only works on single words, and the name has a space in the middle of it",
            "who has to be declared before the call",
            "Strings built with + cannot be made upper case",
        ),
        fix=(
            "'NoneType' is the clue: the value that .upper() was asked of was "
            "None. A function with no return line hands back None, so who "
            "was None, and the crash appears on the line that used it rather "
            "than in the function that forgot. Add return name as the last "
            "line of full_name."
        ),
    ),
    _c(
        id="err-py-int-of-word",
        level=2,
        name="A number that is not a number",
        family=PYTHON,
        language="python",
        code=(
            "answers = [\"12\", \"7\", \"twelve\", \"3\"]\n"
            "total = 0\n"
            "for answer in answers:\n"
            "    total += int(answer)\n"
            "print(total)"
        ),
        message="ValueError: invalid literal for int() with base 10: 'twelve'",
        line=4,
        meaning="int() was given the text 'twelve', which is not written in digits",
        decoys=(
            "total cannot be added to inside a loop",
            "int() can only take one character at a time, so a two-digit string like 12 breaks it",
            "The list has too many items for int()",
        ),
        fix=(
            "A ValueError is the right type with a wrong value: int() does "
            "take strings, just not that one. The message even quotes the "
            "bad value, so you know which item it was without printing "
            "anything. Clean the data, or skip what does not convert with "
            "try: ... except ValueError: continue."
        ),
    ),
    _c(
        id="err-py-average-of-nothing",
        level=2,
        name="An average of an empty list",
        family=PYTHON,
        language="python",
        code=(
            "def average(numbers):\n"
            "    return sum(numbers) / len(numbers)\n"
            "\n"
            "print(average([4, 6]))\n"
            "print(average([]))"
        ),
        message="ZeroDivisionError: division by zero",
        line=2,
        meaning="The list was empty, so len was 0 and the sum was divided by 0",
        decoys=(
            "sum cannot add up an empty list, so it fails before the division is even tried",
            "average can only be called once",
            "Dividing two whole numbers is not allowed",
        ),
        fix=(
            "Read the bottom frame: the crash is on line 2, inside average, "
            "and the line above it in the traceback (line 5) says which call "
            "got there. The first call worked, so the formula is fine; the "
            "second gave it nothing. Decide what an empty average means and "
            "say so: if not numbers: return 0."
        ),
    ),
    _c(
        id="err-py-missing-argument",
        level=2,
        name="A call one argument short",
        family=PYTHON,
        language="python",
        code=(
            "def greet(name, greeting):\n"
            "    return greeting + \", \" + name\n"
            "\n"
            "print(greet(\"Ann\", \"Hi\"))\n"
            "print(greet(\"Bo\"))"
        ),
        message="TypeError: greet() missing 1 required positional argument: 'greeting'",
        line=5,
        meaning="The second call gave greet a name but no greeting",
        decoys=(
            "greet cannot be called twice in one program",
            "The arguments are in the wrong order, so the greeting went into the name parameter",
            "Bo is not a valid name",
        ),
        fix=(
            "The message names the function, how many were missing and which "
            "parameter went without - everything except the fix. Either pass "
            "it - greet(\"Bo\", \"Hello\") - or give the parameter a default "
            "so it can be left out: def greet(name, greeting=\"Hello\")."
        ),
    ),
    _c(
        id="err-py-list-push",
        level=3,
        name="A method from another language",
        family=PYTHON,
        language="python",
        code=(
            "queue = []\n"
            "queue.append(\"first\")\n"
            "queue.push(\"second\")\n"
            "print(queue)"
        ),
        message="AttributeError: 'list' object has no attribute 'push'",
        line=3,
        meaning="Python lists have no push method; the word is append",
        decoys=(
            "queue became None after the first append",
            "A list can only hold one string",
            "push only works on lists made with list()",
        ),
        fix=(
            "Compare with the NoneType one: here the object is a real list, "
            "so the value is fine and the method name is the problem. push "
            "is JavaScript's word. Python's list grows with append (one "
            "item) or extend (many); pop takes from the end in both."
        ),
    ),
    _c(
        id="err-py-unbound-local",
        level=3,
        name="Changing a global inside a function",
        family=PYTHON,
        language="python",
        code=(
            "count = 0\n"
            "\n"
            "def bump():\n"
            "    count += 1\n"
            "\n"
            "bump()\n"
            "print(count)"
        ),
        message=(
            "UnboundLocalError: cannot access local variable 'count' where it is "
            "not associated with a value"
        ),
        line=4,
        meaning="Assigning to count inside bump made count local, and that local has no value yet",
        decoys=(
            "Functions cannot read any variable defined outside them, not even to look at its value",
            "count += 1 only works on floats",
            "bump has to be called before count is defined",
        ),
        fix=(
            "Any assignment to a name inside a function - += included - makes "
            "that name local to the whole function, so count += 1 tries to "
            "read a local count that was never set. Reading a global is "
            "fine; changing one needs global count at the top of bump. "
            "Better still: pass the value in and return the new one."
        ),
    ),
    _c(
        id="err-py-sort-returns-none",
        level=3,
        name="Using what sort() hands back",
        family=PYTHON,
        language="python",
        code=(
            "scores = [70, 95, 85]\n"
            "ranked = scores.sort(reverse=True)\n"
            "print(\"winner:\", ranked[0])"
        ),
        message="TypeError: 'NoneType' object is not subscriptable",
        line=3,
        meaning="sort() sorts the list in place and returns None, so ranked is None",
        decoys=(
            "reverse=True emptied the list",
            "Lists of numbers cannot be indexed",
            "ranked[0] has to be written ranked(0)",
        ),
        fix=(
            "'subscriptable' means 'can be indexed with [ ]', and None cannot. "
            "list.sort() changes the list itself and returns None on purpose, "
            "so nobody mistakes it for a copy. Either sort and keep using "
            "scores, or use sorted(scores, reverse=True), which returns a "
            "new sorted list."
        ),
    ),
    _c(
        id="err-py-unhashable",
        level=4,
        name="A list as a dict key",
        family=PYTHON,
        language="python",
        code=(
            "visited = {}\n"
            "spot = [2, 3]\n"
            "visited[spot] = True\n"
            "print(len(visited))"
        ),
        message="TypeError: unhashable type: 'list'",
        line=3,
        meaning="A dict key must be unchangeable, and a list can change",
        decoys=(
            "visited has to be created with dict()",
            "True cannot be stored as a value",
            "A key cannot hold more than one number",
        ),
        fix=(
            "A dict finds keys by their hash, which has to stay the same for "
            "as long as the key is in there - so keys must be immutable, and "
            "a list is not. A tuple holds the same two numbers and cannot "
            "change: visited[(2, 3)] = True, or spot = (2, 3). Sets have the "
            "same rule."
        ),
    ),
    _c(
        id="err-py-dict-changed",
        level=4,
        name="Deleting while looping",
        family=PYTHON,
        language="python",
        code=(
            "stock = {\"apples\": 3, \"pears\": 0, \"plums\": 5}\n"
            "for fruit in stock:\n"
            "    if stock[fruit] == 0:\n"
            "        del stock[fruit]\n"
            "print(stock)"
        ),
        message="RuntimeError: dictionary changed size during iteration",
        line=2,
        meaning="The loop deleted from the dict it was walking, which Python does not allow",
        decoys=(
            "del cannot remove a key whose value is 0, because 0 counts as nothing being there",
            "stock[fruit] is read before fruit has a value",
            "A dict cannot be printed after a del",
        ),
        fix=(
            "The blamed line is the for, not the del: the del worked, and the "
            "loop noticed on its next step that the dict it was walking had "
            "changed size. Walk a copy - for fruit in list(stock): - or build "
            "the dict you want instead: stock = {k: v for k, v in "
            "stock.items() if v}."
        ),
    ),
    _c(
        id="err-py-generator-used-up",
        level=5,
        name="A generator read twice",
        family=PYTHON,
        language="python",
        code=(
            "squares = (n * n for n in range(4))\n"
            "print(sum(squares))\n"
            "biggest = max(squares)\n"
            "print(biggest)"
        ),
        message="ValueError: max() iterable argument is empty",
        line=3,
        meaning="sum used the generator up, so there was nothing left for max",
        decoys=(
            "max cannot take a generator, only a list or a tuple that already holds its values",
            "range(4) makes an empty sequence",
            "squares was overwritten by the sum",
        ),
        fix=(
            "A generator hands its values out once. sum took all four, so "
            "max got a generator with nothing left in it - and max of nothing "
            "has no answer. Make a list when you need the values more than "
            "once: squares = [n * n for n in range(4)]. Square brackets, not "
            "round ones."
        ),
    ),
)
