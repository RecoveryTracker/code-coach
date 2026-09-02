"""Concept questions: the half of an interview that is not a coding problem.

Systems and quant interviews spend as long on "what actually happens when you
take a page fault" as they do on any algorithm, and no amount of LeetCode
prepares you for that. This is that material: short questions with answers
you could say out loud, grouped by the thing they are really about.

The answers are written to be *said*, not recited. Where there is a number
worth memorising it is given, and where the honest answer is "it depends", it
says what it depends on rather than hedging.

Most of it is language-agnostic — a page fault is a page fault — so those
topics are offered to everyone. The exception is the one topic per language
about that language's own semantics, which is shown only to whoever is
writing it. Otherwise the first thing a Python student saw was the rule of
five, which is true and not theirs.
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
    # Which languages this topic belongs to. Empty means all of them, which
    # is the common case: most of this material is about the machine rather
    # than about any language written on it.
    languages: tuple[str, ...] = field(default_factory=tuple)

    def belongs_to(self, language: str | None) -> bool:
        if not self.languages:
            return True
        return language in self.languages


def _q(ask: str, answer: str, follow_up: str = "") -> Question:
    return Question(ask=ask, answer=answer, follow_up=follow_up)


def topics(language: str | None = None) -> tuple[Topic, ...]:
    """Every topic, from all three banks, in the order they are read.

    The split across files is only so none of them has to be scrolled past to
    reach the next; from the outside it is one bank.

    Pass a language to get the topics that student should see: the shared
    ones plus that language's own. Pass nothing to get all of them, which is
    what the tests and the counts want.
    """
    from code_coach.concepts.bank import TOPICS
    from code_coach.concepts.bank2 import MORE_TOPICS
    from code_coach.concepts.bank3 import LANGUAGE_TOPICS

    everything = TOPICS + MORE_TOPICS + LANGUAGE_TOPICS
    if language is None:
        chosen = everything
    else:
        chosen = tuple(t for t in everything if t.belongs_to(language))
    return tuple(sorted(chosen, key=lambda t: (t.order, t.name)))


def topic(topic_id: str) -> Topic | None:
    return next((t for t in topics() if t.id == topic_id), None)


def question_count(language: str | None = None) -> int:
    return sum(len(t.questions) for t in topics(language))


def languages_with_topics() -> tuple[str, ...]:
    """Which languages have a semantics topic of their own."""
    return tuple(sorted({lang for t in topics() for lang in t.languages}))


def payload(language: str | None = None) -> list[dict]:
    """Everything this student should see, for the Concepts screen."""
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
        for t in topics(language)
    ]
