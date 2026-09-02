"""Python-only shapes, second batch: functions in depth, and errors.

Same rules as `emit_python`. One language, so the emitter is one function per
shape and the output may be whatever Python really prints — which here means
booleans and error messages as well as lists.

Determinism needs one new care in this batch: `max` and `min` with a key
return the *first* item that ties, and `sorted` is stable, so every exercise
that could tie has one right answer rather than a plausible one.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("default_arg", "an argument the caller may leave out"),
    Shape("keyword_call", "naming the arguments at the call"),
    Shape("star_args", "a function that takes as many as you give it"),
    Shape("sorted_lambda", "ordering by something you write on the spot"),
    Shape("map_filter", "map and filter, with a lambda"),
    Shape("any_all", "asking whether any, or all, of them qualify"),
    Shape("recursion", "a function that calls itself"),
    Shape("try_except", "carrying on after something goes wrong"),
    Shape("raise_error", "refusing to continue, on purpose"),
    Shape("min_max_key", "the biggest by a measure of your choosing"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(repr(n) for n in items) + "]"


def _strs(items) -> str:
    return "[" + ", ".join(_q(w) for w in items) + "]"


def _python(shape: str, a: dict) -> str:
    if shape == "default_arg":
        calls = [
            f"print({a['name']}({v}))"
            if extra is None
            else f"print({a['name']}({v}, {extra}))"
            for v, extra in a["calls"]
        ]
        return _lines(
            f"def {a['name']}(n, {a['param']}={a['default']}):",
            f"    return {a['expr']}",
            "",
            *calls,
        )
    if shape == "keyword_call":
        calls = [
            f"print({a['name']}({a['param2']}={y}, {a['param1']}={x}))"
            for x, y in a["calls"]
        ]
        return _lines(
            f"def {a['name']}({a['param1']}, {a['param2']}):",
            f"    return {a['expr']}",
            "",
            *calls,
        )
    if shape == "star_args":
        calls = [
            f"print({a['name']}({', '.join(str(v) for v in group)}))"
            for group in a["calls"]
        ]
        return _lines(
            f"def {a['name']}(*nums):",
            f"    return {a['expr']}",
            "",
            *calls,
        )
    if shape == "sorted_lambda":
        return _lines(
            f"nums = {_nums(a['items'])}",
            f"print(sorted(nums, key=lambda n: {a['key']}))",
        )
    if shape == "map_filter":
        if a["kind"] == "map":
            call = f"list(map(lambda n: {a['expr']}, nums))"
        else:
            call = f"list(filter(lambda n: {a['expr']}, nums))"
        return _lines(f"nums = {_nums(a['items'])}", f"print({call})")
    if shape == "any_all":
        return _lines(
            f"nums = {_nums(a['items'])}",
            f"print({a['kind']}({a['cond']} for n in nums))",
        )
    if shape == "recursion":
        return _lines(
            f"def {a['name']}(n):",
            f"    if n {a['base']}:",
            f"        return {a['stop']}",
            f"    return {a['step']}",
            "",
            *[f"print({a['name']}({v}))" for v in a["calls"]],
        )
    if shape == "try_except":
        return _lines(
            "try:",
            f"    print({a['expr']})",
            f"except {a['error']}:",
            f"    print({_q(a['message'])})",
        )
    if shape == "raise_error":
        return _lines(
            f"def {a['name']}(n):",
            f"    if {a['cond']}:",
            f"        raise ValueError({_q(a['message'])})",
            f"    return {a['expr']}",
            "",
            f"for n in {_nums(a['calls'])}:",
            "    try:",
            f"        print({a['name']}(n))",
            "    except ValueError as err:",
            "        print(err)",
        )
    if shape == "min_max_key":
        return _lines(
            f"words = {_strs(a['words'])}",
            f"print({a['which']}(words, key=len))",
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "python":
        return None
    return _python(shape, args)


# ── What each of them prints ─────────────────────────────────


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "default_arg":
        lines = [
            str(
                value(
                    a["expr"],
                    {"n": v, a["param"]: a["default"] if extra is None else extra},
                )
            )
            for v, extra in a["calls"]
        ]
    elif shape == "keyword_call":
        lines = [
            str(value(a["expr"], {a["param1"]: x, a["param2"]: y}))
            for x, y in a["calls"]
        ]
    elif shape == "star_args":
        lines = [
            str(
                value(
                    a["expr"],
                    # The builtins these expressions are allowed to reach.
                    # `_value` runs with no builtins at all, so anything a
                    # star-args body may call has to be handed in by name.
                    {
                        "nums": tuple(group),
                        "sum": sum,
                        "len": len,
                        "max": max,
                        "min": min,
                    },
                )
            )
            for group in a["calls"]
        ]
    elif shape == "sorted_lambda":
        lines = [
            repr(sorted(a["items"], key=lambda n: value(a["key"], {"n": n})))
        ]
    elif shape == "map_filter":
        if a["kind"] == "map":
            built = [value(a["expr"], {"n": n}) for n in a["items"]]
        else:
            built = [n for n in a["items"] if value(a["expr"], {"n": n})]
        lines = [repr(built)]
    elif shape == "any_all":
        got = (any if a["kind"] == "any" else all)(
            value(a["cond"], {"n": n}) for n in a["items"]
        )
        lines = [str(got)]
    elif shape == "recursion":
        def run(n):
            if value("n " + a["base"], {"n": n}):
                return value(a["stop"], {"n": n})
            return value(
                a["step"], {"n": n, a["name"]: run}
            )

        lines = [str(run(v)) for v in a["calls"]]
    elif shape == "try_except":
        try:
            lines = [str(value(a["expr"], {}))]
        except ZeroDivisionError:
            lines = [a["message"]]
    elif shape == "raise_error":
        for n in a["calls"]:
            if value(a["cond"], {"n": n}):
                lines.append(a["message"])
            else:
                lines.append(str(value(a["expr"], {"n": n})))
    elif shape == "min_max_key":
        pick = max if a["which"] == "max" else min
        lines = [pick(a["words"], key=len)]
    else:
        raise KeyError(shape)
    return NL.join(lines)
