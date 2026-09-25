"""Stop the program mid-run and say what a variable holds.

Predict asks what a program prints, which is the whole program at once.
This asks a smaller and harder question: at this exact moment, before
this line runs, what is in `total`? It is the question you have to be
able to answer in your head to debug anything, and the one nobody
practises, because the only way to check yourself is to run it — and
once you have run it you have the answer and have learned nothing.

This app has a tracer, so it can ask the question, take your answer,
and then show you the run. That is the shape the whole mode turns on:
you commit first, and the step table is the reward rather than the
source.

The moment is exact on purpose
------------------------------
"After line 3" is ambiguous the moment there is a loop in the program.
The tracer models states as "about to run line L", so that is what is
asked, and for a line inside a loop the question also says which time
round. Vague questions about loops are how people come away thinking
they understand loops.

Where the answers come from
---------------------------
The tracer. Every expected value here is checked against what it
reports, so a puzzle whose answer has quietly stopped being true fails
the suite rather than marking somebody wrong.

One thing the tracer still cannot show, which is why no puzzle depends
on it: in JavaScript it reports undefined and null identically. The
Errors mode covers that distinction instead.

It could not show aliasing either when this mode was written — two
names for one array came back as two separate heap entries, because
the encoder keyed on the handle CDP gave it and CDP mints a fresh
handle every time. The runner asks the program for identity now, so
one array is drawn as one array with two names on it. These puzzles
ask for values rather than identity and did not change, but Watch it
run afterwards is worth more than it was: the picture now agrees with
the answer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Trace:
    """One program, one moment in it, one variable."""

    id: str
    name: str
    family: str
    #: The program, short enough that the line numbers stay put.
    code: str
    #: The line execution is about to run when the question is asked.
    at_line: int
    #: Which time round, for a line inside a loop. 1 for straight-line
    #: code, which is most of them.
    occurrence: int
    #: The variable being asked about.
    variable: str
    #: What it holds at that moment, written the way the language would
    #: write it. Held to the tracer by the suite.
    expect: str
    #: What people say instead. Usually the value one step earlier, or
    #: the value if the language worked the way they assume.
    decoys: tuple[str, ...]
    #: Shown either way, because being right by luck teaches nothing.
    why: str
    language: str = "javascript"
    level: int = 2

    @property
    def numbered(self) -> tuple[tuple[int, str], ...]:
        return tuple(
            (i + 1, text) for i, text in enumerate(self.code.split("\n"))
        )

    @property
    def choices(self) -> tuple[str, ...]:
        """Everything on offer, in an order that says nothing."""
        return tuple(sorted({self.expect, *self.decoys}))

    @property
    def question(self) -> str:
        """The moment, in words, exactly as the tracer means it."""
        when = (
            f"line {self.at_line}"
            if self.occurrence == 1
            else f"line {self.at_line} for the {_nth(self.occurrence)} time"
        )
        return f"Execution is about to run {when}. What is {self.variable}?"


def _nth(n: int) -> str:
    """1st, 2nd, 3rd, 4th — including the teens, which are all th."""
    if n % 100 in (11, 12, 13):
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _t(**kw) -> Trace:
    return Trace(**kw)


def render(value: Any, heap: dict) -> str:
    """One of the tracer's values, as the language would write it.

    Kept here rather than in the test so the rendering the suite trusts
    is the rendering the module documents — and so a puzzle's expected
    value is written in the same notation the screen shows.
    """
    kind = value.get("k")
    if kind == "prim":
        t, v = value.get("t"), value.get("v")
        if t == "bool":
            return "true" if v else "false"
        if t == "none":
            return "null"
        if t == "str":
            return "'" + str(v) + "'"
        return str(v)
    if kind == "ref":
        return render_heap(heap.get(str(value.get("id")), {}), heap)
    return "?"


def render_heap(thing: dict, heap: dict) -> str:
    kind = thing.get("k")
    if kind == "list":
        inner = ", ".join(render(x, heap) for x in thing.get("items", []))
        return "[" + inner + "]"
    if kind == "dict":
        pairs = thing.get("pairs", [])
        inner = ", ".join(
            f"{_key(k)}: {render(v, heap)}" for k, v in pairs
        )
        return "{ " + inner + " }" if inner else "{}"
    return "?"


def _key(k: dict) -> str:
    """An object key, unquoted the way JavaScript writes it."""
    if k.get("k") == "prim" and k.get("t") == "str":
        return str(k.get("v"))
    return render(k, {})


def value_at(
    code: str,
    at_line: int,
    occurrence: int,
    variable: str,
    language: str = "javascript",
) -> str:
    """What the tracer says the variable holds at that moment.

    Returns "" when the moment never happens — a line that is never
    reached, or a loop that does not go round that many times — which
    is a broken puzzle rather than an answer, and the suite says so.
    """
    from code_coach.visualize import trace_code

    result = trace_code(code, language=language)
    seen = 0
    for step in result.get("steps") or []:
        if step.get("line") != at_line:
            continue
        seen += 1
        if seen < occurrence:
            continue
        found = (step.get("vars") or {}).get(variable)
        if found is None:
            return ""
        return render(found, step.get("heap") or {})
    return ""


def traces(family: str | None = None) -> tuple[Trace, ...]:
    from code_coach.trace.content import ALIASING, LOOPS, SCOPE
    from code_coach.engine import if_dart
    from code_coach.trace.content_dart import DART_TRACES
    from code_coach.trace.content_dart2 import DART_TRACES_2

    everything = (*ALIASING, *LOOPS, *SCOPE, *if_dart(DART_TRACES + DART_TRACES_2))
    if family is not None:
        everything = tuple(t for t in everything if t.family == family)
    return tuple(sorted(everything, key=lambda t: t.level))


def trace_families() -> tuple[str, ...]:
    from code_coach.trace.content import ALIASING, LOOPS, SCOPE
    from code_coach.engine import if_dart
    from code_coach.trace.content_dart import DART_TRACES
    from code_coach.trace.content_dart2 import DART_TRACES_2

    seen: list[str] = []
    for t in (*ALIASING, *LOOPS, *SCOPE, *if_dart(DART_TRACES + DART_TRACES_2)):
        if t.family not in seen:
            seen.append(t.family)
    return tuple(seen)


def one_trace(trace_id: str) -> Trace | None:
    return next((t for t in traces() if t.id == trace_id), None)
