"""Projects: the ones where the rules interact.

Every other kata here is one rule applied carefully. These are three or
four rules at once, and the difficulty is not any of them — it is that
getting one right can break another. That is the step up from a kata to
something resembling work, and it is the shape of the freeCodeCamp
projects for the same reason.

`add_time` is the clearest example. Twelve-hour clocks, minutes carrying
into hours, hours carrying into days, and the two special names — noon
and midnight are both twelve — and each of those is easy alone. Written
together, the usual outcome is code that handles four of them and turns
11:59 PM plus one minute into 0:00 AM.

These three carry an `edge_note` rather than a structurally awkward
input, because they cannot have one: a clock time is never the empty
string and a price is never a negative number. The boundary is in the
meaning instead — midnight, exact money, a single column — and saying
that out loud is the price of the exemption.
"""

from __future__ import annotations

from code_coach.kata import Kata


def _add_time(start: str, duration: str) -> str:
    clock, meridiem = start.split()
    hour, minute = (int(part) for part in clock.split(":"))
    hour = hour % 12 + (12 if meridiem == "PM" else 0)
    add_hour, add_minute = (int(part) for part in duration.split(":"))

    total = hour * 60 + minute + add_hour * 60 + add_minute
    days, into_day = divmod(total, 24 * 60)
    new_hour, new_minute = divmod(into_day, 60)
    suffix = "AM" if new_hour < 12 else "PM"
    shown = new_hour % 12 or 12

    out = f"{shown}:{new_minute:02d} {suffix}"
    if days == 1:
        out += " (next day)"
    elif days > 1:
        out += f" ({days} days later)"
    return out


def _make_change(price: float, given: float) -> list:
    coins = (
        ("twenty", 2000), ("ten", 1000), ("five", 500), ("two", 200),
        ("one", 100), ("fifty", 50), ("twenty p", 20), ("ten p", 10),
        ("five p", 5), ("two p", 2), ("one p", 1),
    )
    # In whole pence from the start. Taking the difference in pounds
    # first and then converting leaves you subtracting numbers that
    # cannot be written exactly, and the change comes out a penny short
    # often enough to be a real bug in real tills.
    owed = round(given * 100) - round(price * 100)
    if owed < 0:
        return ["short"]
    if owed == 0:
        return ["exact"]
    out = []
    for name, worth in coins:
        count, owed = divmod(owed, worth)
        if count:
            out.append(f"{count} x {name}")
    return out


def _align(numbers: list) -> list:
    if not numbers:
        return []
    width = max(len(str(n)) for n in numbers)
    return [str(n).rjust(width) for n in numbers]


PROJECTS: tuple[Kata, ...] = (
    Kata(
        id="add-time",
        level=4,
        name="add_time",
        brief=(
            "Add a duration to a twelve-hour clock time. The start looks "
            "like '3:00 PM' and the duration like '3:10', meaning three "
            "hours and ten minutes. Return the new time the same way. If "
            "it lands on the next day add ' (next day)', and if it is "
            "further than that add ' (2 days later)' with the right "
            "number."
        ),
        params=("start", "duration"),
        family="Projects",
        example='add_time("3:00 PM", "3:10") is "6:10 PM"',
        hint=(
            "Turn everything into minutes past midnight, do the sum "
            "there, and turn it back at the end. Every carry then "
            "happens for free, and divmod by 1440 gives you the days and "
            "the time in one go."
        ),
        edge_note=(
            "A clock time is never the empty string and a duration is "
            "never negative, so there is no structurally degenerate "
            "input here. The boundaries are in the meaning instead and "
            "the cases cover them: midnight, noon, the minute that "
            "crosses into the next day, and a duration long enough to "
            "cross several."
        ),
        cases=(
            ("3:00 PM", "3:10"), ("11:30 AM", "2:32"), ("11:43 AM", "00:20"),
            ("10:10 PM", "3:30"), ("11:43 PM", "24:20"), ("6:30 PM", "205:12"),
            ("12:00 AM", "0:01"), ("12:00 PM", "12:00"), ("1:59 AM", "0:01"),
            ("11:59 PM", "0:01"),
        ),
        solve=_add_time,
        checks=(
            (("3:00 PM", "3:10"), "6:10 PM"),
            (("12:00 AM", "0:01"), "12:01 AM"),
            (("11:59 PM", "0:01"), "12:00 AM (next day)"),
            (("12:00 PM", "12:00"), "12:00 AM (next day)"),
            (("11:43 PM", "24:20"), "12:03 AM (2 days later)"),
            (("11:43 AM", "00:20"), "12:03 PM"),
        ),
    ),
    Kata(
        id="make-change",
        level=4,
        name="make_change",
        brief=(
            "Work out the change from a price and what was handed over. "
            "Return a list like ['1 x five', '2 x two p'], largest coin "
            "first, leaving out any coin you do not need. Return "
            "['exact'] when nothing is owed and ['short'] when it is not "
            "enough. The coins are 20, 10, 5, 2 and 1 pounds, then 50, "
            "20, 10, 5, 2 and 1 pence."
        ),
        params=("price", "given"),
        family="Projects",
        example='make_change(3.26, 10.0) starts ["1 x five", "1 x one", ...]',
        hint=(
            "Convert to whole pence before subtracting, not after. "
            "Taking the difference in pounds leaves you subtracting "
            "numbers binary cannot write exactly, and the change comes "
            "out a penny short."
        ),
        edge_note=(
            "A price is not a container and cannot be empty. Its "
            "boundaries are the money itself, and the cases hold them: "
            "paying exactly, paying too little, owing a single penny, "
            "and a total that needs nearly every coin."
        ),
        cases=(
            (1.0, 2.0), (2.5, 2.5), (5.0, 1.0), (0.0, 0.01), (3.26, 10.0),
            (19.5, 20.0), (0.99, 1.0), (0.01, 20.0), (7.77, 10.0), (1.0, 1.0),
        ),
        solve=_make_change,
        checks=(
            ((1.0, 2.0), ["1 x one"]),
            ((2.5, 2.5), ["exact"]),
            ((5.0, 1.0), ["short"]),
            ((0.0, 0.01), ["1 x one p"]),
            ((0.99, 1.0), ["1 x one p"]),
            ((19.5, 20.0), ["1 x fifty"]),
        ),
    ),
    Kata(
        id="align",
        level=2,
        name="align",
        brief=(
            "Right-align the numbers in a column. Return one string per "
            "number, every one as wide as the longest, padded on the "
            "left with spaces. No numbers gives an empty list."
        ),
        params=("numbers",),
        family="Projects",
        example="align([1, 22, 333]) is ['  1', ' 22', '333']",
        hint=(
            "The width is decided by the longest once, before any of "
            "them are padded. A minus sign counts towards the length, "
            "which is what makes -10 wider than 10."
        ),
        cases=(
            ([1, 22, 333],), ([],), ([5],), ([-1, 10],), ([0, 0],),
            ([100, 2],), ([7],), ([12, 345, 6],), ([-10, -2],), ([9, 99],),
        ),
        solve=_align,
        checks=(
            ((([1, 22, 333],)), ["  1", " 22", "333"]),
            ((([],)), []),
            ((([5],)), ["5"]),
            ((([-1, 10],)), ["-1", "10"]),
            ((([-10, -2],)), ["-10", " -2"]),
        ),
    ),
)
