"""Gotchas: an endless feed of trap questions, one at a time.

The kind of post that goes round social media as "Python Quiz": a short program on a dark card, four
answers, and an obvious reading that is wrong. This is the same thing, instant and endless: a built-in
deck of Python and JavaScript cards (`content_py.py`, `content_js.py`, then the later
`content_py2.py`, `content_js2.py`), plus cards the user types or
pastes in themselves (`user.py`), served by `store.GotchaStore`.

The oracle rule holds, and harder than elsewhere: the answer written in the content is never trusted.
tests/test_gotchas_content.py runs every card in the real interpreter and fails when what it prints is
not the marked answer; a card the user adds takes its answer from a real run the moment it is saved.
The browser is never sent the answer before it has answered (`GotchaStore.present`).
"""

from __future__ import annotations

from .content_js import ITEMS as _JS1
from .content_js2 import ITEMS as _JS2
from .content_py import ITEMS as _PY1
from .content_py2 import ITEMS as _PY2
from .items import Item
from .store import LANGUAGES, BadChoice, GotchaStore, UnknownCard, served_options

#: The first two Python cards (py-score-90, py-loop-var-list) must stay first: the store serves them first.
#: Later modules only ever come after the earlier ones.
_PY: tuple[Item, ...] = (*_PY1, *_PY2)
_JS: tuple[Item, ...] = (*_JS1, *_JS2)

DECKS: dict[str, tuple[Item, ...]] = {"python": _PY, "javascript": _JS}

#: The one the app uses: its files are found through the active progress store each time.
STORE = GotchaStore()


def builtin_deck(language: str) -> tuple[Item, ...]:
    return DECKS.get(language, ())


def title(language: str) -> str:
    return "Python Quiz" if language == "python" else "JavaScript Quiz"


__all__ = ["BadChoice", "DECKS", "GotchaStore", "Item", "LANGUAGES", "STORE", "UnknownCard",
           "builtin_deck", "served_options", "title"]
