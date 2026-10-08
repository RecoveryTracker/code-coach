"""The one drill item, shared by the JavaScript and Python templates."""

from __future__ import annotations

from dataclasses import dataclass


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
