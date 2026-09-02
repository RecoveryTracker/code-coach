"""Intermediate pages 91-100: functions in depth, and things going wrong.

Pages 27 to 29 taught what a function is. These teach what Python lets one
be — arguments the caller can leave out or name, as many as they like, or
one written inline with no name at all. Then the first pages in the whole
book about a program not going to plan.

Python only, same as 81-90.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

PYTHON = ("python",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=PYTHON,
        tier="intermediate",
    )


def _list(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


# ── 91. An argument you can leave out ────────────────────────

_DEFAULTS = (
    ("scale", "factor", 2, "n * factor", "the number times factor", [(5, None), (5, 3)]),
    ("add", "extra", 10, "n + extra", "the number plus extra", [(1, None), (1, 90)]),
    ("rep", "times", 3, "n * times", "the number times times", [(7, None), (7, 10)]),
    ("shift", "by", 1, "n - by", "the number minus by", [(20, None), (20, 15)]),
    ("power", "exp", 2, "n ** exp", "the number to the power of exp", [(3, None), (3, 3)]),
    ("chunk", "size", 5, "n % size", "the remainder of the number over size", [(23, None), (23, 10)]),
    ("grow", "step", 100, "n + step", "the number plus step", [(1, None), (1, 9)]),
    ("share", "people", 4, "n // people", "the number divided by people, rounded down", [(100, None), (100, 3)]),
    ("pad", "width", 2, "n * width", "the number times width", [(11, None), (11, 5)]),
    ("back", "amount", 1, "n - amount", "the number minus amount", [(50, None), (50, 50)]),
    ("mix", "other", 7, "n * other + n", "the number times other, plus itself", [(2, None), (2, 1)]),
    ("cut", "keep", 10, "n % keep", "the remainder of the number over keep", [(456, None), (456, 100)]),
)

_P91 = _page(
    "default-arg",
    91,
    "An argument you can leave out",
    "A default, so the common call is the short one.",
    "The default is written into the definition and used whenever the caller "
    "says nothing. Each of these is called twice — once letting the default "
    "stand and once overriding it — so you see both halves of why it is "
    "there.",
    "default_arg",
    [
        (
            f"Write a function called {name} that takes a number and a second "
            f"argument {param} defaulting to {default}, and returns "
            f"{described}. Print the result of calling it with "
            + " and then with ".join(
                str(v) if extra is None else f"{v} and {extra}"
                for v, extra in calls
            )
            + ".",
            {
                "name": name,
                "param": param,
                "default": default,
                "expr": expr,
                "calls": calls,
            },
        )
        for name, param, default, expr, described, calls in _DEFAULTS
    ],
)


# ── 92. Naming the arguments ─────────────────────────────────

_KEYWORDS = (
    ("box", "width", "height", "width * height", "width times height", [(4, 3), (10, 7)]),
    ("gap", "big", "small", "big - small", "big minus small", [(50, 20), (9, 9)]),
    ("mix", "first", "second", "first * 10 + second", "first times 10, plus second", [(3, 4), (9, 1)]),
    ("share", "total", "people", "total // people", "total divided by people, rounded down", [(100, 3), (7, 7)]),
    ("rest", "n", "d", "n % d", "the remainder of n over d", [(17, 5), (100, 9)]),
    ("both", "a", "b", "a + b", "a plus b", [(11, 22), (5, 0)]),
    ("scale", "value", "factor", "value * factor", "value times factor", [(6, 7), (12, 12)]),
    ("drop", "start", "amount", "start - amount", "start minus amount", [(90, 15), (1, 1)]),
    ("area", "w", "h", "w * h", "w times h", [(8, 9), (25, 4)]),
    ("stack", "rows", "each", "rows * each + 1", "rows times each, plus 1", [(3, 4), (10, 10)]),
    ("split", "whole", "parts", "whole % parts", "the remainder of whole over parts", [(31, 6), (40, 8)]),
    ("total", "x", "y", "x + y + x", "x plus y plus x again", [(2, 3), (10, 1)]),
)

_P92 = _page(
    "keyword-call",
    92,
    "Naming the arguments",
    "Keyword arguments, so the order at the call stops mattering.",
    "Every call here passes the second argument first and names both, which "
    "still works — the names decide, not the positions. Worth doing once "
    "deliberately, because it is how you read someone else's call to a "
    "function taking six things.",
    "keyword_call",
    [
        (
            f"Write a function called {name} that takes {p1} and {p2} and "
            f"returns {described}. Call it twice, naming both arguments and "
            f"passing {p2} first: with {p1}={x1} and {p2}={y1}, then "
            f"{p1}={x2} and {p2}={y2}.",
            {
                "name": name,
                "param1": p1,
                "param2": p2,
                "expr": expr,
                "calls": calls,
            },
        )
        for name, p1, p2, expr, described, calls in _KEYWORDS
        for (x1, y1), (x2, y2) in [calls]
    ],
)


# ── 93. As many as you give it ───────────────────────────────

_STARS = (
    ("total", "sum(nums)", "them all added up", [[1, 2, 3], [10, 20], [5]]),
    ("count", "len(nums)", "how many there were", [[1, 2, 3, 4], [9], [1, 1, 1, 1, 1]]),
    ("biggest", "max(nums)", "the biggest of them", [[3, 9, 4], [10, 2], [7]]),
    ("smallest", "min(nums)", "the smallest of them", [[3, 9, 4], [100, 50], [8]]),
    ("total", "sum(nums)", "them all added up", [[100, 200, 300], [7, 7]]),
    ("span", "max(nums) - min(nums)", "the biggest minus the smallest", [[3, 9, 4], [10, 10]]),
    ("doubled", "sum(nums) * 2", "twice their total", [[1, 2], [5, 5, 5]]),
    ("count", "len(nums)", "how many there were", [[1], [1, 2, 3, 4, 5, 6]]),
    ("total", "sum(nums) + 1", "their total plus 1", [[2, 3], [10, 20, 30]]),
    ("biggest", "max(nums)", "the biggest of them", [[1, 2, 3, 4, 5], [42]]),
    ("half", "sum(nums) % 10", "the last digit of their total", [[7, 8], [55, 45]]),
    ("total", "sum(nums)", "them all added up", [[1, 1, 1], [2, 4, 6, 8]]),
)

_P93 = _page(
    "star-args",
    93,
    "As many as you give it",
    "A star in front of the parameter, and the call decides how many.",
    "Inside the function the star turns them into one thing you can loop "
    "over or hand to sum. Each of these is called with different counts, "
    "which is the whole point — the function does not know or care.",
    "star_args",
    [
        (
            f"Write a function called {name} that takes any number of numbers "
            f"and returns {described}. Call it with "
            + ", then ".join(_list(g) for g in groups)
            + ".",
            {"name": name, "expr": expr, "calls": groups},
        )
        for name, expr, described, groups in _STARS
    ],
)


# ── 94. Ordering by a rule you write ─────────────────────────

_LAMBDA_SORTS = (
    ([15, 22, 31, 44], "n % 10", "their last digit"),
    ([5, 3, 8, 1], "-n", "biggest first"),
    ([12, 7, 25, 3], "n % 5", "the remainder when divided by 5"),
    ([100, 20, 3], "-n", "biggest first"),
    ([9, 18, 27, 36], "n % 7", "the remainder when divided by 7"),
    ([44, 33, 22, 11], "n % 6", "the remainder when divided by 6"),
    ([1, 2, 3, 4, 5], "-n", "biggest first"),
    ([17, 4, 29, 8], "n % 3", "the remainder when divided by 3"),
    ([50, 25, 75], "-n", "biggest first"),
    ([6, 13, 20, 27], "n % 4", "the remainder when divided by 4"),
    ([88, 45, 12, 91], "n % 10", "their last digit"),
    ([2, 4, 8, 16, 32], "-n", "biggest first"),
)

_P94 = _page(
    "sorted-lambda",
    94,
    "Ordering by a rule you write",
    "A lambda: a small function with no name, written where it is used.",
    "Page 90 sorted by length using len, which already existed. When the "
    "rule you want has no name, a lambda is how you say it in place. Ties "
    "keep the order they came in, so several of these depend on the sort "
    "being stable.",
    "sorted_lambda",
    [
        (
            f"Put the numbers {_list(items)} in a list. Print them sorted by "
            f"{described}.",
            {"items": items, "key": key},
        )
        for items, key, described in _LAMBDA_SORTS
    ],
)


# ── 95. map and filter ───────────────────────────────────────

_MAP_FILTER = (
    ([1, 2, 3, 4], "map", "n * n", "each one squared"),
    ([1, 2, 3, 4, 5, 6], "filter", "n % 2 == 0", "only the even ones"),
    ([10, 20, 30], "map", "n + 5", "each one plus 5"),
    ([5, 12, 8, 20], "filter", "n > 9", "only the ones over 9"),
    ([1, 2, 3], "map", "n * 100", "each one times 100"),
    ([7, 14, 21, 28], "filter", "n % 14 == 0", "only the ones dividing by 14"),
    ([9, 8, 7], "map", "n - 7", "each one minus 7"),
    ([1, 2, 3, 4, 5], "filter", "n > 100", "only the ones over 100"),
    ([2, 4, 6], "map", "n // 2", "each one halved"),
    ([15, 25, 35, 45], "filter", "n % 3 == 0", "only the ones dividing by 3"),
    ([1, 3, 5], "map", "n * n * n", "each one cubed"),
    ([100, 200, 50, 400], "filter", "n >= 100", "only the ones 100 or more"),
)

_P95 = _page(
    "map-filter",
    95,
    "map and filter",
    "The two oldest ways to say a comprehension.",
    "map turns every item into something else; filter keeps some and drops "
    "the rest. Both hand back something lazy, so list() around them is what "
    "makes it a list you can print. Comprehensions do the same job and are "
    "usually clearer — meet these because other people's code is full of "
    "them.",
    "map_filter",
    [
        (
            f"Put the numbers {_list(items)} in a list. Using {kind} with a "
            f"lambda, build a list of {described} and print it.",
            {"items": items, "kind": kind, "expr": expr},
        )
        for items, kind, expr, described in _MAP_FILTER
    ],
)


# ── 96. Any, or all ──────────────────────────────────────────

_ANY_ALL = (
    ([2, 4, 6], "all", "n % 2 == 0", "all of them are even"),
    ([2, 4, 7], "all", "n % 2 == 0", "all of them are even"),
    ([1, 3, 8], "any", "n % 2 == 0", "any of them are even"),
    ([1, 3, 5], "any", "n % 2 == 0", "any of them are even"),
    ([10, 20, 30], "all", "n >= 10", "all of them are 10 or more"),
    ([10, 5, 30], "all", "n >= 10", "all of them are 10 or more"),
    ([4, 9, 16], "any", "n > 15", "any of them are over 15"),
    ([4, 9, 14], "any", "n > 15", "any of them are over 15"),
    ([7, 14, 21], "all", "n % 7 == 0", "all of them divide by 7"),
    ([3, 6, 10], "all", "n % 3 == 0", "all of them divide by 3"),
    ([100, 1, 50], "any", "n == 1", "any of them are exactly 1"),
    ([5, 5, 5], "all", "n == 5", "all of them are exactly 5"),
)

_P96 = _page(
    "any-all",
    96,
    "Any, or all",
    "One yes-or-no answer about a whole list.",
    "These print True or False, which nothing in the book has done before — "
    "and note the capital letter, because that is Python's spelling and not "
    "every language's. Both stop as soon as they know: any at the first that "
    "qualifies, all at the first that does not.",
    "any_all",
    [
        (
            f"Put the numbers {_list(items)} in a list. Print whether "
            f"{described}.",
            {"items": items, "kind": kind, "cond": cond},
        )
        for items, kind, cond, described in _ANY_ALL
    ],
)


# ── 97. A function that calls itself ─────────────────────────

_RECURSIONS = (
    ("countdown", "<= 0", "0", "n + countdown(n - 1)", "adds every number from n down to 1", [5, 1]),
    ("factorial", "<= 1", "1", "n * factorial(n - 1)", "multiplies every number from n down to 1", [5, 3]),
    ("double_down", "<= 0", "0", "2 + double_down(n - 1)", "adds 2 for every step down to 0", [4, 10]),
    ("total", "<= 0", "0", "n + total(n - 1)", "adds every number from n down to 1", [10, 3]),
    ("factorial", "<= 1", "1", "n * factorial(n - 1)", "multiplies every number from n down to 1", [6, 1]),
    ("countdown", "<= 0", "0", "1 + countdown(n - 1)", "counts the steps down to 0", [7, 0]),
    ("powers", "<= 0", "1", "2 * powers(n - 1)", "doubles once for every step down to 0", [5, 8]),
    ("total", "<= 0", "0", "n * 2 + total(n - 1)", "adds double every number down to 1", [4, 6]),
    ("factorial", "<= 1", "1", "n * factorial(n - 1)", "multiplies every number from n down to 1", [7, 4]),
    ("steps", "<= 0", "0", "3 + steps(n - 1)", "adds 3 for every step down to 0", [5, 2]),
    ("powers", "<= 0", "1", "3 * powers(n - 1)", "triples once for every step down to 0", [4, 1]),
    ("total", "<= 0", "0", "n + total(n - 2)", "adds every other number down from n", [10, 9]),
)

_P97 = _page(
    "recursion",
    97,
    "A function that calls itself",
    "The base case first, then the step that gets closer to it.",
    "Two lines and an idea. The check at the top is what stops it; the call "
    "at the bottom must move towards that check or it never returns. Write "
    "the stopping line first, always — it is the half people leave until "
    "last and the half that matters.",
    "recursion",
    [
        (
            f"Write a function called {name} that takes a number and "
            f"{described}, calling itself to do it. Print the result for "
            + " and then ".join(str(v) for v in calls)
            + ".",
            {
                "name": name,
                "base": base,
                "stop": stop,
                "step": step,
                "calls": calls,
            },
        )
        for name, base, stop, step, described, calls in _RECURSIONS
    ],
)


# ── 98. Carrying on after a mistake ──────────────────────────

_TRIES = (
    ("10 // 0", "ZeroDivisionError", "cannot divide by zero"),
    ("10 // 2", "ZeroDivisionError", "cannot divide by zero"),
    ("100 // 0", "ZeroDivisionError", "no dividing by nothing"),
    ("100 // 4", "ZeroDivisionError", "no dividing by nothing"),
    ("7 % 0", "ZeroDivisionError", "the remainder needs a divisor"),
    ("7 % 3", "ZeroDivisionError", "the remainder needs a divisor"),
    ("1 // 0", "ZeroDivisionError", "that will not work"),
    ("9 // 3", "ZeroDivisionError", "that will not work"),
    ("50 // 0", "ZeroDivisionError", "divide by zero"),
    ("50 // 5", "ZeroDivisionError", "divide by zero"),
    ("8 % 0", "ZeroDivisionError", "no such remainder"),
    ("8 % 5", "ZeroDivisionError", "no such remainder"),
)

_P98 = _page(
    "try-except",
    98,
    "Carrying on after a mistake",
    "try and except: what to do instead when a line cannot work.",
    "These come in pairs — one that fails and one that does not — and the "
    "program prints something either way, which is the point. Catch the error "
    "you expected by name rather than catching everything, or you will one "
    "day swallow a typo and wonder where it went.",
    "try_except",
    [
        (
            f"Try to print the answer to {expr}. If that raises a "
            f'{error}, print "{message}" instead.',
            {"expr": expr, "error": error, "message": message},
        )
        for expr, error, message in _TRIES
    ],
)


# ── 99. Refusing to continue ─────────────────────────────────

_RAISES = (
    ("check", "n < 0", "negative not allowed", "n * 2", "double it", [3, -1]),
    ("age", "n > 130", "that is too old", "n + 1", "add a year", [40, 200]),
    ("half", "n % 2 == 1", "odd numbers do not halve", "n // 2", "halve it", [10, 7]),
    ("small", "n > 100", "too big", "n * 10", "times it by 10", [5, 500]),
    ("root", "n < 0", "no negative roots", "n * n", "square it", [4, -9]),
    ("share", "n == 0", "cannot share between nobody", "100 // n", "share 100 by it", [4, 0]),
    ("level", "n > 10", "level too high", "n * 100", "score it", [3, 11]),
    ("count", "n < 1", "must be at least 1", "n + 10", "add 10", [1, 0]),
    ("size", "n > 50", "will not fit", "n * n", "square it", [6, 60]),
    ("step", "n == 0", "a step of zero goes nowhere", "60 // n", "divide 60 by it", [5, 0]),
    ("year", "n < 1900", "before records began", "n - 1900", "years since 1900", [2026, 1850]),
    ("part", "n > 12", "there are only twelve", "n * 30", "days in that many months", [3, 13]),
)

_P99 = _page(
    "raise-error",
    99,
    "Refusing to continue",
    "raise, when the value you were given makes no sense.",
    "A function that quietly returns something wrong is worse than one that "
    "stops. raise says so out loud, and the caller decides what to do — here "
    "the loop catches it and prints the message, so both calls produce a "
    "line and neither is a lie.",
    "raise_error",
    [
        (
            f"Write a function called {name} that takes a number, raises a "
            f'ValueError saying "{message}" if {cond_text}, and otherwise '
            f"returns {described}. Loop over {_list(calls)}, printing the "
            f"result or the error message for each.",
            {
                "name": name,
                "cond": cond,
                "message": message,
                "expr": expr,
                "calls": calls,
            },
        )
        for name, cond, message, expr, described, calls in _RAISES
        for cond_text in [cond.replace("n ", "the number ")]
    ],
)


# ── 100. The biggest by a measure ────────────────────────────

_PICKS = (
    (["banana", "fig", "apple"], "max"),
    (["banana", "fig", "apple"], "min"),
    (["one", "three", "to"], "max"),
    (["one", "three", "to"], "min"),
    (["a", "bbb", "cc"], "max"),
    (["python", "go", "rust"], "min"),
    (["short", "much longer", "mid"], "max"),
    (["x", "yy", "zzz", "w"], "min"),
    (["cat", "horse", "ox"], "max"),
    (["north", "up", "east"], "min"),
    (["hello", "hi", "hey"], "max"),
    (["alpha", "be", "gamma", "pi"], "min"),
)

_P100 = _page(
    "min-max-key",
    100,
    "The biggest by a measure",
    "max and min with a key, instead of a loop that carries the best so far.",
    "Page 26 wrote this by hand and page 38 wrote it backwards. This is the "
    "same idea handed to the language. Two words the same length is a tie, "
    "and both max and min return the first one they met — which is worth "
    "knowing before it decides something for you.",
    "min_max_key",
    [
        (
            f"Put the words {_words(words)} in a list. Print the "
            + ("longest" if which == "max" else "shortest")
            + " one.",
            {"words": words, "which": which},
        )
        for words, which in _PICKS
    ],
)


INTERMEDIATE_PAGES_2: tuple[Page, ...] = (
    _P91,
    _P92,
    _P93,
    _P94,
    _P95,
    _P96,
    _P97,
    _P98,
    _P99,
    _P100,
)
