"""
Practice drill bank.

Difficulty 1 = typing / single idea reps
Difficulty 5 = multi-step, nested, combine patterns

Examples are generic patterns — never personal data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from code_coach.checks import (
    assigns_dict,
    assigns_list,
    assigns_variable,
    calls_function,
    calls_method,
    defines_function,
    has_constant,
    prints_name,
    references_name,
    returns_value,
    subscripts_name,
    uses_and,
    uses_for,
    uses_if,
    uses_if_else,
    uses_loop,
    uses_nested_for,
    uses_subscript,
    uses_while,
)


@dataclass
class DrillStep:
    id: str
    label: str
    check: Callable[[str], bool]
    concept: str
    why: str
    hint: str
    example: str
    # Build exercises: the individual pieces the goal needs, each with a
    # beginner-readable label. Shown as a live ✓/✗ checklist so the student
    # can see exactly which part is still missing.
    requirements: list[tuple[str, Callable[[str], bool]]] | None = None
    # When the goal pins exact output ("Print the numbers 0, 1, 2"), the step
    # only completes once a Run produced exactly this stdout (whitespace
    # normalized). None = structure-only checking.
    expect_output: str | None = None


def requirements_check(
    reqs: list[tuple[str, Callable[[str], bool]]],
) -> Callable[[str], bool]:
    """A step check that passes when every named requirement passes."""

    def _check(code: str) -> bool:
        return all(fn(code) for _, fn in reqs)

    return _check


@dataclass
class Drill:
    id: str
    skill: str
    difficulty: int  # content complexity 1–5 (separate from coach style)
    title: str
    prompt: str
    starter: str
    steps: list[DrillStep]
    tags: list[str] = field(default_factory=list)
    # Progressive path order (unique-ish across catalog)
    path_order: int = 0
    # If False, only used in skill/reps practice — not the main progressive path
    in_progressive: bool = True


def _drill(
    id: str,
    skill: str,
    difficulty: int,
    title: str,
    prompt: str,
    starter: str,
    steps: list[DrillStep],
    path_order: int,
    tags: list[str] | None = None,
    *,
    in_progressive: bool = True,
) -> Drill:
    return Drill(
        id=id,
        skill=skill,
        difficulty=difficulty,
        title=title,
        prompt=prompt,
        starter=starter,
        steps=steps,
        tags=tags or [],
        path_order=path_order,
        in_progressive=in_progressive,
    )


def _class1_dictation() -> Drill:
    """Class 1 type-along — endless regenerable windows (see dictation.bank)."""
    from code_coach.dictation.bank import WINDOW_SIZE
    from code_coach.dictation.session import make_class1_batch

    return make_class1_batch(seed="default", batch=0, count=WINDOW_SIZE, level=1)


# Mutable registry so refill can swap Class 1 batches
_DYNAMIC: dict[str, Drill] = {}


def register_dynamic(drill: Drill) -> Drill:
    _DYNAMIC[drill.id] = drill
    return drill


DRILLS: list[Drill] = [
    # ── Class 1 endless-style dictation ───────────────────
    register_dynamic(_class1_dictation()),
    # ── Basics micro-reps (skill practice only) ───────────
    _drill(
        "basics-print-1",
        "basics",
        1,
        "Rep — Your first print",
        "Type a print line. Any message is fine.",
        "# Type one print line\n",
        [
            DrillStep(
                "print",
                "Call print(...)",
                lambda c: calls_function(c, "print"),
                "print shows output",
                "You need to see results when a program runs.",
                'Type print, then parentheses, then text in quotes inside.',
                'print("hello")',
            )
        ],
        path_order=10,
        tags=["typing", "print", "beginner"],
        in_progressive=False,
    ),
    _drill(
        "basics-var-1",
        "basics",
        1,
        "Rep — Store a number",
        "Save a number in score, then print score.",
        "# variable + print\n",
        [
            DrillStep(
                "score",
                "Assign score",
                lambda c: assigns_variable(c, "score"),
                "Variables hold values",
                "Names let you reuse data.",
                "score = some number (no quotes on the number)",
                "score = 10",
            ),
            DrillStep(
                "print_score",
                "Print score",
                lambda c: prints_name(c, "score"),
                "Print by name",
                "No quotes around the variable name.",
                "print(score)",
                "print(score)",
            ),
        ],
        path_order=20,
        tags=["typing", "variables", "beginner"],
        in_progressive=False,
    ),
    _drill(
        "basics-string-num-2",
        "basics",
        2,
        "Rep — Text vs number",
        "Store text (label) and a number (count), then print both.",
        "# text uses quotes, numbers do not\n",
        [
            DrillStep(
                "label",
                "Assign label (string)",
                lambda c: assigns_variable(c, "label"),
                "Strings use quotes",
                "Text and numbers are different types.",
                'label = "items"',
                'label = "items"',
            ),
            DrillStep(
                "count",
                "Assign count (number)",
                lambda c: assigns_variable(c, "count"),
                "Numbers usually have no quotes",
                '7 is a number; "7" is text.',
                "count = 3",
                "count = 3",
            ),
            DrillStep(
                "print_both",
                "Print both",
                lambda c: prints_name(c, "label") and prints_name(c, "count"),
                "Print each by name",
                "Two print lines is fine.",
                "print(label)\nprint(count)",
                "print(label)\nprint(count)",
            ),
        ],
        path_order=30,
        tags=["types"],
        in_progressive=False,
    ),
    # ── Conditionals ──────────────────────────────────────
    _drill(
        "cond-if-1",
        "conditionals",
        1,
        "Simple if",
        "If x is greater than 0, print ok. Set x yourself.",
        "x = 5\n# add an if that prints when x > 0\n",
        [
            DrillStep(
                "if",
                "Write an if",
                lambda c: uses_if(c),
                "if runs code only when a condition is true",
                "Programs need to make decisions.",
                "if x > 0:\n    print(\"ok\")",
                'if x > 0:\n    print("ok")',
            ),
        ],
        path_order=40,
        tags=["if", "typing"],
    ),
    _drill(
        "cond-else-2",
        "conditionals",
        2,
        "if / else",
        "If n is even print even, else print odd. (Hint: n % 2)",
        "n = 7\n# if/else for even vs odd\n",
        [
            DrillStep(
                "ifelse",
                "Use if and else",
                lambda c: uses_if_else(c),
                "else covers the other case",
                "Exactly one branch should run.",
                'if n % 2 == 0:\n    print("even")\nelse:\n    print("odd")',
                'if n % 2 == 0:\n    print("even")\nelse:\n    print("odd")',
            ),
        ],
        path_order=50,
        tags=["if", "else"],
    ),
    _drill(
        "cond-and-3",
        "conditionals",
        3,
        "Combine conditions",
        "Print ready only if age >= 18 and has_ticket is True.",
        "age = 20\nhas_ticket = True\n# print ready when both are true\n",
        [
            DrillStep(
                "and",
                "Use and in a condition",
                lambda c: uses_if(c) and uses_and(c),
                "and requires both sides true",
                "Real checks often need more than one fact.",
                'if age >= 18 and has_ticket:\n    print("ready")',
                'if age >= 18 and has_ticket:\n    print("ready")',
            ),
        ],
        path_order=60,
        tags=["boolean"],
    ),
    # ── Loops ─────────────────────────────────────────────
    _drill(
        "loops-for-1",
        "loops",
        1,
        "for + range",
        "Print the numbers 0, 1, 2 using a for loop and range.",
        "# for loop over range\n",
        [
            DrillStep(
                "for",
                "Write a for loop",
                lambda c: uses_for(c),
                "for repeats for each item",
                "Repetition without copy-paste.",
                "for i in range(3):\n    print(i)",
                "for i in range(3):\n    print(i)",
            ),
        ],
        path_order=70,
        tags=["for", "typing"],
    ),
    _drill(
        "loops-while-2",
        "loops",
        2,
        "while countdown",
        "Use while to count n down to 1, printing each time. Start n at 3.",
        "n = 3\n# while loop countdown\n",
        [
            DrillStep(
                "while",
                "Write a while loop",
                lambda c: uses_while(c),
                "while repeats until the condition is false",
                "Good when you don't know a fixed count in advance.",
                "while n > 0:\n    print(n)\n    n = n - 1",
                "while n > 0:\n    print(n)\n    n = n - 1",
            ),
        ],
        path_order=80,
        tags=["while"],
    ),
    _drill(
        "loops-accumulate-3",
        "loops",
        3,
        "Accumulate a total",
        "Sum numbers 1..5 into total using a loop, then print total.",
        "total = 0\n# add 1 through 5 into total\n",
        [
            DrillStep(
                "loop",
                "Use a loop",
                lambda c: uses_loop(c),
                "Accumulate pattern",
                "Keep a running total as you go.",
                "for i in range(1, 6):\n    total = total + i\nprint(total)",
                "for i in range(1, 6):\n    total = total + i\nprint(total)",
            ),
            DrillStep(
                "print_total",
                "Print total",
                lambda c: prints_name(c, "total"),
                "Show the result",
                "After the loop, print once.",
                "print(total)",
                "print(total)",
            ),
        ],
        path_order=90,
        tags=["accumulate", "patterns"],
    ),
    _drill(
        "loops-nested-4",
        "loops",
        4,
        "Nested loops",
        "Print a 3x3 grid of coordinates like (0,0) using nested loops.",
        "# nested for loops\n",
        [
            DrillStep(
                "nested",
                "Two for loops (nested)",
                lambda c: uses_nested_for(c),
                "Inner loop runs fully for each outer step",
                "Grids and pair-checks need nesting.",
                'for r in range(3):\n    for c in range(3):\n        print(r, c)',
                "for r in range(3):\n    for c in range(3):\n        print(r, c)",
            ),
        ],
        path_order=100,
        tags=["nested", "patterns"],
    ),
    # ── Lists ─────────────────────────────────────────────
    _drill(
        "lists-create-1",
        "lists",
        1,
        "Make a list",
        "Create a list called nums with at least 3 numbers. Print it.",
        "# list of numbers\n",
        [
            DrillStep(
                "list",
                "Assign a list to nums",
                lambda c: assigns_list(c, "nums"),
                "Lists hold ordered items",
                "This is Python's everyday array-like structure.",
                "nums = [10, 20, 30]",
                "nums = [10, 20, 30]",
            ),
            DrillStep(
                "print",
                "Print nums",
                lambda c: prints_name(c, "nums"),
                "Print the whole list",
                "print(nums)",
                "print(nums)",
                "print(nums)",
            ),
        ],
        path_order=110,
        tags=["list", "typing"],
    ),
    _drill(
        "lists-loop-2",
        "lists",
        2,
        "Loop a list",
        "Loop over colors and print each color.",
        'colors = ["red", "green", "blue"]\n# print each\n',
        [
            DrillStep(
                "for",
                "for item in list",
                lambda c: uses_for(c) and references_name(c, "colors"),
                "for x in collection walks each item",
                "The core list pattern.",
                "for color in colors:\n    print(color)",
                "for color in colors:\n    print(color)",
            ),
        ],
        path_order=120,
        tags=["list", "for"],
    ),
    _drill(
        "lists-filter-3",
        "lists",
        3,
        "Filter pattern",
        "From nums, print only values greater than 5.",
        "nums = [3, 8, 2, 10, 5]\n# print values > 5\n",
        [
            DrillStep(
                "filter",
                "Loop + if filter",
                lambda c: uses_for(c) and uses_if(c),
                "Filter keeps some items",
                "Combine loop + condition.",
                "for n in nums:\n    if n > 5:\n        print(n)",
                "for n in nums:\n    if n > 5:\n        print(n)",
            ),
        ],
        path_order=130,
        tags=["filter", "patterns"],
    ),
    _drill(
        "lists-index-4",
        "lists",
        4,
        "Index and update",
        "Print the first item of items, then set the last item to 99 and print items.",
        "items = [1, 2, 3]\n# first item, then last = 99\n",
        [
            DrillStep(
                "index",
                "Use indexing with [",
                lambda c: uses_subscript(c) and calls_function(c, "print"),
                "Index reads/writes by position",
                "0 is the first item; -1 is often the last.",
                "print(items[0])\nitems[-1] = 99\nprint(items)",
                "print(items[0])\nitems[-1] = 99\nprint(items)",
            ),
        ],
        path_order=140,
        tags=["index"],
    ),
    # ── Dicts ─────────────────────────────────────────────
    _drill(
        "dicts-create-2",
        "dicts",
        2,
        "Make a dict",
        'Create person with keys "name" and "age". Print person.',
        "# dict key -> value\n",
        [
            DrillStep(
                "dict",
                "Assign a dict",
                lambda c: assigns_dict(c, "person"),
                "Dicts map keys to values",
                "Lookup by name, not only position.",
                'person = {"name": "Ada", "age": 36}',
                'person = {"name": "Ada", "age": 36}',
            ),
        ],
        path_order=150,
        tags=["dict"],
    ),
    _drill(
        "dicts-lookup-3",
        "dicts",
        3,
        "Dict lookup",
        "Print the value for key score in grades.",
        'grades = {"score": 95, "late": False}\n# print grades["score"]\n',
        [
            DrillStep(
                "lookup",
                "Access with [key]",
                lambda c: subscripts_name(c, "grades"),
                "Lookup is O(1)-ish mental model",
                "Keys are the addresses.",
                'print(grades["score"])',
                'print(grades["score"])',
            ),
        ],
        path_order=160,
        tags=["dict"],
    ),
    # ── Functions ─────────────────────────────────────────
    _drill(
        "func-def-2",
        "functions",
        2,
        "Define a function",
        "Define greet that prints hi, then call greet().",
        "# def + call\n",
        [
            DrillStep(
                "def",
                "Write def greet",
                lambda c: defines_function(c, "greet"),
                "def names a reusable block",
                "Functions cut copy-paste.",
                'def greet():\n    print("hi")\n\ngreet()',
                'def greet():\n    print("hi")\n\ngreet()',
            ),
            DrillStep(
                "call",
                "Call greet()",
                lambda c: calls_function(c, "greet"),
                "Call runs the function",
                "Parentheses mean call.",
                "greet()",
                "greet()",
            ),
        ],
        path_order=170,
        tags=["function"],
    ),
    _drill(
        "func-return-3",
        "functions",
        3,
        "Return a value",
        "Write double(n) that returns n * 2. Print double(5).",
        "# return value\n",
        [
            DrillStep(
                "def",
                "def double with return",
                lambda c: defines_function(c, "double") and returns_value(c),
                "return sends a value back",
                "Print inside is different from return.",
                "def double(n):\n    return n * 2\n\nprint(double(5))",
                "def double(n):\n    return n * 2\n\nprint(double(5))",
            ),
        ],
        path_order=180,
        tags=["return"],
    ),
    _drill(
        "func-loop-4",
        "functions",
        4,
        "Function + loop",
        "Write sum_list(xs) that returns the total of a list. Print sum_list([1,2,3]).",
        "# function that loops\n",
        [
            DrillStep(
                "combo",
                "def + loop + return",
                lambda c: defines_function(c) and uses_loop(c) and returns_value(c),
                "Combine patterns inside functions",
                "Real code nests skills together.",
                "def sum_list(xs):\n    total = 0\n    for x in xs:\n        total = total + x\n    return total\n\nprint(sum_list([1, 2, 3]))",
                "def sum_list(xs):\n    total = 0\n    for x in xs:\n        total += x\n    return total\n\nprint(sum_list([1, 2, 3]))",
            ),
        ],
        path_order=190,
        tags=["function", "accumulate"],
    ),
    # ── Patterns ──────────────────────────────────────────
    _drill(
        "pat-search-3",
        "patterns",
        3,
        "Search pattern",
        "Set found True if 7 is in data (use a loop or `in`). Print found.",
        "data = [2, 4, 7, 9]\nfound = False\n# find 7\n",
        [
            DrillStep(
                "search",
                "Detect membership",
                lambda c: assigns_variable(c, "found") and has_constant(c, 7) and calls_function(c, "print"),
                "Search looks for a match",
                "Stop early or use `in`.",
                "found = 7 in data\nprint(found)",
                "found = 7 in data\nprint(found)",
            ),
        ],
        path_order=200,
        tags=["search"],
    ),
    _drill(
        "pat-count-4",
        "patterns",
        4,
        "Count with a dict",
        "Count how many times each letter appears in word using a dict. Print the dict.",
        'word = "banana"\ncounts = {}\n# count letters\n',
        [
            DrillStep(
                "count",
                "Loop + dict counts",
                lambda c: uses_for(c) and references_name(c, "counts") and calls_function(c, "print"),
                "Hash-count pattern",
                "Dicts are perfect frequency tables.",
                "for ch in word:\n    if ch not in counts:\n        counts[ch] = 0\n    counts[ch] = counts[ch] + 1\nprint(counts)",
                "for ch in word:\n    counts[ch] = counts.get(ch, 0) + 1\nprint(counts)",
            ),
        ],
        path_order=210,
        tags=["dict", "count"],
    ),
    # ── Structures (intro) ────────────────────────────────
    _drill(
        "struct-stack-4",
        "structures",
        4,
        "Stack with a list",
        "Use a list as a stack: push 1, push 2, pop once, print the stack.",
        "stack = []\n# push/pop with append and pop\n",
        [
            DrillStep(
                "stack",
                "append and pop",
                lambda c: calls_method(c, "append") and calls_method(c, "pop"),
                "Stack is LIFO",
                "Last in, first out — undo, matching parens.",
                "stack.append(1)\nstack.append(2)\nstack.pop()\nprint(stack)",
                "stack.append(1)\nstack.append(2)\nstack.pop()\nprint(stack)",
            ),
        ],
        path_order=220,
        tags=["stack"],
    ),
    _drill(
        "struct-queue-5",
        "structures",
        5,
        "Queue idea",
        "Simulate a queue with a list: enqueue 1 then 2 (append), dequeue once (pop(0)), print queue.",
        "queue = []\n# enqueue append, dequeue pop(0)\n",
        [
            DrillStep(
                "queue",
                "append + pop(0)",
                lambda c: calls_method(c, "append") and calls_method(c, "pop", arg0=0),
                "Queue is FIFO",
                "First in, first out — lines, BFS later.",
                "queue.append(1)\nqueue.append(2)\nqueue.pop(0)\nprint(queue)",
                "queue.append(1)\nqueue.append(2)\nqueue.pop(0)\nprint(queue)",
            ),
        ],
        path_order=230,
        tags=["queue"],
    ),
]

DRILLS_BY_ID: dict[str, Drill] = {d.id: d for d in DRILLS}


def get_drill(drill_id: str) -> Drill | None:
    if drill_id in _DYNAMIC:
        return _DYNAMIC[drill_id]
    # Back-compat alias
    if drill_id == "lesson-day-01":
        return _DYNAMIC.get("class-1-dictation") or DRILLS_BY_ID.get(drill_id)
    if drill_id == "foundations-l2":
        from code_coach.curriculum.foundations import foundations_l2_drill

        return register_dynamic(foundations_l2_drill())
    if drill_id.startswith("review-"):
        from code_coach.curriculum.foundations import review_drill_for_skill

        skill = drill_id[len("review-") :]
        d = review_drill_for_skill(skill)
        if d:
            return register_dynamic(d)
        return None
    return DRILLS_BY_ID.get(drill_id)


def set_class1_batch(seed: str, batch: int, level: int = 1) -> Drill:
    from code_coach.dictation.bank import WINDOW_SIZE
    from code_coach.dictation.session import make_class1_batch

    drill = make_class1_batch(
        seed=seed, batch=batch, count=WINDOW_SIZE, level=level
    )
    register_dynamic(drill)
    # keep progressive list head in sync
    if DRILLS and DRILLS[0].id == "class-1-dictation":
        DRILLS[0] = drill
    DRILLS_BY_ID[drill.id] = drill
    return drill


def list_drills(
    *,
    skill: str | None = None,
    skills: list[str] | None = None,
    difficulty: int | None = None,
    max_difficulty: int | None = None,
    min_difficulty: int | None = None,
) -> list[Drill]:
    out = list(DRILLS)
    if skill:
        out = [d for d in out if d.skill == skill]
    if skills:
        allowed = set(skills)
        out = [d for d in out if d.skill in allowed]
    if difficulty is not None:
        out = [d for d in out if d.difficulty == difficulty]
    if min_difficulty is not None:
        out = [d for d in out if d.difficulty >= min_difficulty]
    if max_difficulty is not None:
        out = [d for d in out if d.difficulty <= max_difficulty]
    return sorted(out, key=lambda d: (d.path_order, d.difficulty, d.id))
