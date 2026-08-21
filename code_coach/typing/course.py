"""The course: a numbered path through the keyboard, in order.

The sections and modes are a workshop — every combination is available, which
is right for someone who already knows what they want to drill. It's the wrong
first screen. Somebody who just wants to learn to type shouldn't have to
decide whether Bottom Row Key Pairs is what they need today.

So this is the ordinary path: start on the home row, add a row at a time, then
the number row and the symbols, and finish on real text. Each lesson is one
section and one mode with a target to beat, and the targets rise as the
material gets easier to reach.

The order is the standard one for a reason. Fingers learn positions relative
to where they rest, so home row comes first and everything else is described
as a reach out of it — teaching the top row first would mean teaching a
position with nothing to measure it against.
"""

from __future__ import annotations

from dataclasses import dataclass

from code_coach.typing.drills import MODES_BY_ID, SECTIONS_BY_ID, THEMES_BY_ID


@dataclass(frozen=True)
class Lesson:
    number: int
    title: str
    section: str
    mode: str
    # What passing looks like. Reaction lessons are judged on accuracy and
    # speed of finding a key; text lessons on words a minute.
    target_wpm: int
    target_accuracy: int
    # One line on why this lesson exists, shown under the title.
    why: str
    # Which keys is the lesson; what the text says is separate. Most lessons
    # take ordinary English, and a few want their own material.
    theme: str = "mixed"


LESSONS: tuple[Lesson, ...] = (
    # ── Home row ────────────────────────────────────────────
    Lesson(
        0, "Warm up", "everything", "random", 0, 85,
        "A mixed run over the whole keyboard, to see where you're starting "
        "from. Nothing here is a test.",
    ),
    Lesson(
        1, "Find the home row", "home", "whack", 0, 90,
        "Your fingers rest on a s d f and j k l ;. Everything else is a reach "
        "out of here, so this is the position worth knowing cold.",
    ),
    Lesson(
        2, "Home row runs", "home", "drill", 12, 92,
        "Short bursts, so the hand learns a shape rather than one key at a time.",
    ),
    Lesson(
        3, "Home row words", "home", "words", 15, 93,
        "Real words, built from nothing but the keys under your fingers.",
    ),
    # ── Top row ─────────────────────────────────────────────
    Lesson(
        4, "Reach up", "top", "whack", 0, 88,
        "The top row holds most of English. Reach up, then come straight back "
        "to home — the return is the part people skip.",
    ),
    Lesson(
        5, "Top row runs", "top", "drill", 14, 90,
        "Same idea as before, one row higher.",
    ),
    Lesson(
        6, "Top row words", "top", "words", 18, 92,
        "Now the words get longer, because the vowels live up here.",
    ),
    # ── Bottom row ──────────────────────────────────────────
    Lesson(
        7, "Reach down", "bottom", "whack", 0, 85,
        "The row that gets skipped, and the one that slows people down. "
        "No words here — z x c v b n m has no vowels.",
    ),
    Lesson(
        8, "Bottom row runs", "bottom", "drill", 12, 88,
        "Awkward on purpose. These are the keys you'll hunt for later if you "
        "don't drill them now.",
    ),
    # ── All the letters ─────────────────────────────────────
    Lesson(
        9, "Every letter once", "letters", "sweep", 0, 90,
        "All twenty-six, each exactly once, in an order you haven't seen. "
        "Nowhere to hide.",
    ),
    Lesson(
        10, "Letter pairs", "letters", "pairs", 20, 92,
        "th, er, ing. Fast typing isn't produced one key at a time — the hand "
        "learns combinations, and these are the ones English is made of.",
    ),
    Lesson(
        11, "Common words", "letters", "common", 25, 93,
        "The words that make up most of what anyone writes.",
    ),
    Lesson(
        12, "Real sentences", "letters", "speed", 28, 94,
        "Whole lines. Accuracy first — the speed follows on its own.",
    ),
    # ── Numbers ─────────────────────────────────────────────
    Lesson(
        13, "The number row", "numbers", "whack", 0, 82,
        "The row everybody looks down at. It's a long reach, so it needs more "
        "repetitions than the letters did, not fewer.",
    ),
    Lesson(
        14, "Number runs", "numbers", "drill", 14, 88,
        "Digits in bursts, the way they actually turn up.",
    ),
    # ── Symbols ─────────────────────────────────────────────
    Lesson(
        15, "Name the symbol", "symbols", "recall", 0, 80,
        "You're told the name — pipe, tilde, caret — and have to know where it "
        "lives. The keyboard stays dark until you get one wrong.",
    ),
    Lesson(
        16, "Symbol reflexes", "symbols", "whack", 0, 85,
        "Now with the symbol shown. This is about the reach, not the name.",
    ),
    Lesson(
        17, "Symbol runs", "symbols", "drill", 12, 88,
        "Shift plus the number row, drilled properly for once.",
    ),
    # ── Code ────────────────────────────────────────────────
    Lesson(
        18, "Code punctuation", "coding", "recall", 0, 82,
        "Brackets, braces and operators by name. If you write code, this is "
        "where your time actually goes.",
    ),
    Lesson(
        19, "Operator pairs", "coding", "pairs", 16, 90,
        "=>, !==, ::, +=. Two keys that your hand should treat as one motion.",
    ),
    Lesson(
        20, "Type real code", "everything", "speed", 22, 92,
        "Whole working lines. The punctuation in the shapes it appears in.",
        theme="school",
    ),
    # ── Everything ──────────────────────────────────────────
    Lesson(
        21, "The whole board", "everything", "sweep", 0, 88,
        "Letters, numbers and symbols, each key once. The full sweep.",
    ),
    Lesson(
        22, "Mixed runs", "everything", "drill", 18, 90,
        "No warning which part of the board is next, which is what real typing "
        "is like.",
    ),
    Lesson(
        23, "One minute", "letters", "timed", 35, 95,
        "Sixty seconds, the standard measure. This is your number.",
    ),
    Lesson(
        24, "No mistakes", "everything", "perfect", 25, 98,
        "One wrong key and the line starts again. The last thing to learn is "
        "not needing to go back.",
    ),
)

LESSONS_BY_NUMBER = {lesson.number: lesson for lesson in LESSONS}


def _passes(lesson: Lesson, record: dict | None) -> bool:
    """Whether a lesson's best run met its target.

    Reaction lessons carry a target of zero words a minute on purpose: finding
    a key fast is measured in reaction time, and a wpm taken over single
    keypresses would say more about the drill's length than the typist.
    """
    if not record:
        return False
    if record.get("best_accuracy", 0) < lesson.target_accuracy:
        return False
    if lesson.target_wpm and record.get("best_wpm", 0) < lesson.target_wpm:
        return False
    return True


def course_payload(records: dict[str, dict]) -> dict:
    """The course with progress folded in.

    `records` is keyed "section:mode", the same key the record store uses.
    """
    lessons: list[dict] = []
    first_unfinished: int | None = None

    for lesson in LESSONS:
        record = records.get(f"{lesson.section}:{lesson.mode}")
        done = _passes(lesson, record)
        if not done and first_unfinished is None:
            first_unfinished = lesson.number

        section = SECTIONS_BY_ID.get(lesson.section)
        mode = MODES_BY_ID.get(lesson.mode)
        theme = THEMES_BY_ID.get(lesson.theme)
        lessons.append(
            {
                "number": lesson.number,
                "title": lesson.title,
                "why": lesson.why,
                "section": lesson.section,
                "mode": lesson.mode,
                "theme": lesson.theme,
                "section_name": section.name if section else lesson.section,
                "mode_name": mode.name if mode else lesson.mode,
                "theme_name": theme.name if theme else lesson.theme,
                "target_wpm": lesson.target_wpm,
                "target_accuracy": lesson.target_accuracy,
                "done": done,
                "best_wpm": (record or {}).get("best_wpm", 0),
                "best_accuracy": (record or {}).get("best_accuracy", 0),
                "runs": (record or {}).get("runs", 0),
            }
        )

    done_count = sum(1 for entry in lessons if entry["done"])
    return {
        "lessons": lessons,
        "total": len(lessons),
        "done": done_count,
        # Where to send someone who just wants to carry on. Everything is
        # always unlocked — a lesson you can't reach is a lesson you can't
        # practise, and people know what they need better than a gate does.
        #
        # Compared against None, not truthiness: the warm-up is lesson zero,
        # and `or` sent everyone to the end of the course instead.
        "current": (
            first_unfinished if first_unfinished is not None else LESSONS[-1].number
        ),
    }
