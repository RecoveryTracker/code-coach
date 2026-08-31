"""Systems and low-level implementation practice.

LeetCode teaches you to recognise an algorithm. It does not teach you what a
mutex actually is, why false sharing costs you an order of magnitude, or what
`shared_ptr` is doing with that control block. Quant and systems interviews
ask for the second kind of thing, and the way to learn it is to write the
primitive yourself, small enough to hold in your head.

So these are implementations rather than puzzles: a spinlock, a ring buffer,
an arena, an optional. Each is the honest core of the real thing — short
enough to type from memory, complete enough to run.

The material reuses the LeetCode bank's Pattern and Problem shapes, so it
inherits the type-along, the difficulty windows, the study panel and the
lesson links without any of that being written twice.
"""

from __future__ import annotations

from code_coach.leetcode.problems import Pattern

SYSTEMS_PREFIX = "sys-"


def is_systems_class(class_id: str) -> bool:
    return class_id.startswith(SYSTEMS_PREFIX)


def patterns_for_language(language: str) -> tuple[Pattern, ...]:
    """The systems bank in the chosen language, or nothing.

    Unlike the LeetCode bank this does NOT fall back to another language.
    There is no sensible Python answer to "write a lock-free queue", and
    handing one over would be worse than saying the material isn't there.
    """
    if language == "cpp":
        from code_coach.systems.problems_cpp import PATTERNS

        return PATTERNS
    return ()


def has_systems(language: str) -> bool:
    return bool(patterns_for_language(language))


def class_ids(language: str = "cpp") -> tuple[str, ...]:
    return tuple(p.id for p in patterns_for_language(language))
