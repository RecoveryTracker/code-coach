"""Lesson definitions (waypoints + suggestions)."""

from code_coach.lessons.day01 import LESSON as DAY01

LESSONS = {
    1: DAY01,
    "day-01": DAY01,
    "day01": DAY01,
}


class UnknownLessonError(KeyError):
    """Raised when a lesson day/id is not registered."""


def get_lesson(day: int | str):
    try:
        return LESSONS[day]
    except KeyError as exc:
        known = ", ".join(str(k) for k in LESSONS if isinstance(k, int))
        raise UnknownLessonError(
            f"Unknown lesson {day!r}. Known days: {known}"
        ) from exc
