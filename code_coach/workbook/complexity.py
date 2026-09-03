"""What each shape costs, and why — the workbook's answer to "how slow is
this once the numbers get big".

Complexity belongs to the shape rather than to the page, because a page is
twenty goes at one shape and they all cost the same. So this is keyed on
the shape id and every page carrying that shape gets the same note.

Three rules for what goes in here.

Say what grows, not just the letter. "O(n)" tells a beginner nothing;
"one pass, so ten times the numbers is ten times the work" is the thing
the letter is shorthand for. The letter is given as well, because it is
what everyone else will say to them.

Say what n is. Half the confusion about complexity is not knowing what is
being counted — the length of the list, the size of the number, the
number of characters. Each note names it.

Never claim a cost the exercise does not have, and leave out anything
there is nothing honest to say about. A shape with no entry shows no
panel, which is better than a panel that guesses.
"""

from __future__ import annotations

from typing import NamedTuple


class Cost(NamedTuple):
    """The shorthand, and the sentence that explains it."""

    label: str
    note: str


NOTES: dict[str, Cost] = {}


def _add(label: str, note: str, *shapes: str) -> None:
    for shape in shapes:
        NOTES[shape] = Cost(label, note)


# ── No loop: the work is the same however big the values are ──

_add(
    "O(1)",
    "Constant. There is no loop here, so this does the same amount of "
    "work whatever the values are — change 3 + 4 to 30000 + 40000 and it "
    "is still one addition and one line printed. That is what O(1) means: "
    "the cost does not depend on the size of anything.",
    "print_text",
    "print_expr",
    "quoted_text",
    "let_print",
    "let2_print",
    "say_value",
    "if_print",
    "if_else_print",
    "bigger_print",
    "and_or_print",
    "swap_print",
    "join_words",
    "func_print",
    "func_arg",
    "func_return",
    "func_two",
    "func_word",
)

_add(
    "O(1)",
    "Constant, and worth knowing why. Reaching into a list by position "
    "does not walk the list looking for the item — the computer works out "
    "where it is and goes straight there, so getting item 5000 costs "
    "exactly what getting item 0 costs. Same for asking a string its "
    "length: it already knows.",
    "list_index",
    "str_length",
)

_add(
    "O(1)",
    "Constant, on average, and that is the point of a lookup table. "
    "Finding a name in a dict does not check the entries one at a time; "
    "it works out where that key would be kept and looks there. A table "
    "of ten and a table of ten million cost about the same to read from, "
    "which is why this structure is everywhere.",
    "map_lookup",
)

# ── One pass over a range: the work follows the count ──

_add(
    "O(n)",
    "Linear. The loop body runs once per number in the range, so the work "
    "follows the size directly: ten numbers is ten passes, a thousand is "
    "a thousand. Double the range and you double the time. Here n is how "
    "many numbers the loop covers, and this is the commonest shape in all "
    "of programming.",
    "for_print",
    "for_range_print",
    "for_sum",
    "for_if_print",
    "for_down",
    "repeat_text",
    "step_loop",
    "while_count",
    "while_sum",
    "running_total",
    "label_each",
    "list_build",
)

# ── One pass over a list: the work follows its length ──

_add(
    "O(n)",
    "Linear in the length of the list. The loop visits each item once, so "
    "a list of ten takes ten steps and a list of a million takes a "
    "million. Note what n is here: the number of items, not how big the "
    "numbers in them are. A list of ten enormous numbers is still ten "
    "steps.",
    "list_loop",
    "list_sum",
    "list_filter",
    "list_max",
    "list_min",
    "list_reverse",
    "count_matches",
    "two_lists",
    "map_build",
    "join_list",
)

# ── One pass over the characters ──

_add(
    "O(n)",
    "Linear in the length of the text, where n is the number of "
    "characters. Searching a string, changing its case or taking a piece "
    "out of it all have to touch each character in turn — and the ones "
    "that hand back new text are also making a copy that size, so a long "
    "string costs twice over.",
    "str_loop",
    "str_upper",
    "str_contains",
    "str_find",
    "str_slice",
    "split_words",
    "count_words",
    "find_index",
    "char_at",
)

# ── Two loops deep: the work follows the square ──

_add(
    "O(n²)",
    "Quadratic. The inner loop runs all the way through for every single "
    "pass of the outer one, so the work is the two multiplied together — "
    "3 by 3 is 9 lines, 10 by 10 is 100, 100 by 100 is ten thousand. "
    "Doubling the size quadruples the work, which is why nested loops are "
    "the first thing to look at when a program is slow.",
    "for_nested",
    "times_table",
    "grid_print",
    "grid_sum",
)


def for_shape(shape: str) -> Cost | None:
    """The cost note for a shape, or None when there is nothing honest to
    say about it yet. Callers show no panel rather than a guess."""
    return NOTES.get(shape)
