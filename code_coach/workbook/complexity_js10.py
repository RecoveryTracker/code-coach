"""Complexity notes for the "Regex from zero" pages (168-177)."""

from __future__ import annotations

from code_coach.workbook.complexity import Cost

NOTES: dict[str, Cost] = {}


def _add(label: str, note: str, *shapes: str) -> None:
    for shape in shapes:
        NOTES[shape] = Cost(label, note)


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)


_add(
    "O(n)",
    "Linear in the length of the text, n. test() slides the pattern along "
    "the text one position at a time and stops at the first place it fits, "
    "so a yes can come early and a no has to look everywhere. Patterns this "
    "simple never go back and retry, so the cost stays proportional to n.",
    "rx_literal",
    "rx_case",
    "rx_digit",
    "rx_set",
    "rx_repeat",
    "rx_count",
    "rx_dot",
)

_add(
    "O(n)",
    "Linear in the length of the text, n - and with ^ and $ often much "
    "less: a pattern anchored to the start fails at the first character "
    "that does not fit, instead of trying again from every later position.",
    "rx_anchor",
)

_add(
    "O(n)",
    "Linear in the length of the text, n. With /g the search does not stop "
    "at the first match; it carries on from where each match ended, so the "
    "whole text is walked once. Building the result costs its own length "
    "on top, which is never more than n.",
    "rx_replace",
    "rx_match",
)
