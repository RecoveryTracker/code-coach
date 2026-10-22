"""The one drill item, shared by the JavaScript and Python templates."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Item:
    #: The code shown (for Variable Recall, the question).
    prompt: str
    #: The right answer, as typed - or one of the activity's two choices.
    answer: str
    #: Why, for the review after the round.
    explain: str = ""
    #: Variable Recall: what to remember, shown first and then hidden.
    show: str = ""
    #: The code an oracle test runs, in the item's own language, to check
    #: `answer` (empty: the prompt itself is what gets run).
    check: str = ""


@dataclass(frozen=True)
class Activity:
    id: str
    title: str
    blurb: str
    #: The question every item asks.
    question: str
    count: int
    #: "type" (type the answer) or "pick" (one of two keys).
    kind: str
    #: Seconds per item at the sharpest (age 20) and at the slowest (age 80).
    par: float
    slow: float
    make: Callable[[random.Random], Item]
    #: For "pick": the two answers, left key first.
    choices: tuple[str, str] = ("", "")
    #: Variable Recall shows something first, for this many seconds.
    show_seconds: float = 0.0
    #: The Python version: its generator, and its wording where it differs.
    make_py: Callable[[random.Random], Item] | None = None
    question_py: str = ""
    blurb_py: str = ""
    #: The heading it sits under on the home screen (see GROUPS in the package).
    group: str = ""
    #: Glossary term ids (plain lowercase words) this activity drills; the glossary maps them back to the
    #: activity, so this is the one place the mapping lives.
    concepts: tuple[str, ...] = ()
    #: How the generic oracle test checks an item against the real runtime: "value" runs `item.check`
    #: (or the prompt when it has none), takes the value of its last line and compares its printed form with
    #: the answer; "" means the activity has a test of its own (the original seven).
    oracle: str = ""
