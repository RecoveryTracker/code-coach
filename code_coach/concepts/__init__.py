"""Concept questions: the half of an interview that is not a coding problem.

Systems and quant interviews spend as long on "what actually happens when you
take a page fault" as they do on any algorithm, and no amount of LeetCode
prepares you for that. This is that material: short questions with answers
you could say out loud, grouped by the thing they are really about.

The answers are written to be *said*, not recited. Where there is a number
worth memorising it is given, and where the honest answer is "it depends", it
says what it depends on rather than hedging.

Nothing here is language-specific except the C++ topic, so unlike the code
banks this is offered to everyone.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Question:
    """One thing worth being able to answer without thinking about it."""

    ask: str
    answer: str
    # The follow-up an interviewer reaches for when you answer the first one
    # well. Optional, because not every question has an obvious one.
    follow_up: str = ""


@dataclass(frozen=True)
class Topic:
    id: str
    name: str
    blurb: str
    order: int
    questions: tuple[Question, ...] = field(default_factory=tuple)


def _q(ask: str, answer: str, follow_up: str = "") -> Question:
    return Question(ask=ask, answer=answer, follow_up=follow_up)


def topics() -> tuple[Topic, ...]:
    """Every topic, from both banks.

    The split is only so neither file has to be scrolled past to reach the
    other; from the outside it is one bank.
    """
    from code_coach.concepts.bank import TOPICS
    from code_coach.concepts.bank2 import MORE_TOPICS

    return TOPICS + MORE_TOPICS


def topic(topic_id: str) -> Topic | None:
    return next((t for t in topics() if t.id == topic_id), None)


def question_count() -> int:
    return sum(len(t.questions) for t in topics())


def payload() -> list[dict]:
    """Everything, for the Concepts screen."""
    return [
        {
            "id": t.id,
            "name": t.name,
            "blurb": t.blurb,
            "order": t.order,
            "questions": [
                {
                    "ask": q.ask,
                    "answer": q.answer,
                    "follow_up": q.follow_up,
                }
                for q in t.questions
            ],
        }
        for t in sorted(topics(), key=lambda t: t.order)
    ]
