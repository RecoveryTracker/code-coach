"""One trap question: a short program, the real answer, and three tempting misreads."""

from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent


@dataclass(frozen=True)
class Item:
    id: str
    language: str  # "python" | "javascript"
    code: str
    #: What the program really prints (or, with `raises`, the name of the error it dies with).
    #: Written down by hand here and never trusted: tests/test_gotchas_content.py runs the
    #: code in the real interpreter and holds this to what it printed.
    answer: str
    #: The misreads: built-in cards have exactly three, a card the user added may have fewer.
    wrong: tuple[str, ...]
    #: One line naming the trap, shown after the answer.
    trap: str
    #: One to three plain sentences on why.
    why: str
    #: The program ends with an uncaught error and `answer` is its name (nothing printed first).
    raises: bool = False
    #: A card the user added themselves (the "Yours" badge); never part of the built-in deck.
    mine: bool = False
    #: When the user added it (an ISO date); "" for built-ins.
    added: str = ""

    @property
    def options(self) -> tuple[str, ...]:
        """The answer first, then the misreads - the canonical order, before serving shuffles it."""
        return (self.answer, *self.wrong)


def make(language: str):
    """A constructor for a content module: `q = make("python")`, then `q(id, code, answer, wrong, trap, why)`."""

    def build(id: str, code: str, answer: str, wrong: list[str], trap: str, why: str,
              raises: bool = False) -> Item:
        return Item(
            id=f"{'py' if language == 'python' else 'js'}-{id}",
            language=language,
            code=dedent(code).strip("\n"),
            answer=answer,
            wrong=tuple(wrong),
            trap=trap,
            why=" ".join(why.split()),
            raises=raises,
        )

    return build
