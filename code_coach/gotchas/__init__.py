"""Gotchas: an endless feed of trap questions, one at a time.

The kind of post that goes round social media as "Python Quiz": a short program on a dark card, four
answers, and an obvious reading that is wrong. This is the same thing, instant and endless: a built-in
deck for each language in the registry (`langs.py`), plus cards the user types or pastes in themselves
(`user.py`), served by `store.GotchaStore`.

Decks are found by name, not listed: for a language whose content stem is `<s>` (the registry says; it is the
id except for python = `py` and javascript = `js`), this package imports `content_<s>`, then `content_<s>2`,
`content_<s>3`... in that order, and each exposes `ITEMS`. So a content author adds cards by creating (or
extending) a file of their own and touches nothing else. A module that fails to import is skipped and recorded
in `LOAD_ERRORS` (the tests fail on it) rather than taking the whole app down. Every program is run for real:
Python and JavaScript straight away, the others compiled first where they compile (`runner.py`,
`toolchains.py`), and a language whose toolchain is missing, or that has no cards yet, is simply not offered.

The oracle rule holds, and harder than elsewhere: the answer written in the content is never trusted.
tests/test_gotchas_langs.py runs every card in the real toolchain and fails when what it prints is
not the marked answer; a card the user adds takes its answer from a real run the moment it is saved.
The browser is never sent the answer before it has answered (`GotchaStore.present`).
"""

from __future__ import annotations

import importlib
import pkgutil
import re

from . import langs
from .items import Item
from .store import LANGUAGES, BadChoice, GotchaStore, UnknownCard, served_options

#: module name -> why it could not be loaded (empty when every content module imported cleanly).
LOAD_ERRORS: dict[str, str] = {}
#: language id -> the content modules its deck was assembled from, in order.
MODULES: dict[str, tuple[str, ...]] = {}


def _modules_for(lang: langs.Lang) -> list[str]:
    """`content_<stem>`, `content_<stem>2`, `content_<stem>3`... as found on disk, in that order."""
    pattern = re.compile(rf"^content_{re.escape(lang.content)}(\d*)$")
    found = []
    for info in pkgutil.iter_modules(__path__):
        m = pattern.match(info.name)
        if m:
            found.append((int(m.group(1) or 0), info.name))
    return [name for _n, name in sorted(found)]


def _load(lang: langs.Lang) -> tuple[Item, ...]:
    cards: list[Item] = []
    used: list[str] = []
    for name in _modules_for(lang):
        try:
            module = importlib.import_module(f"{__name__}.{name}")
            items = tuple(module.ITEMS)
            wrong = [it.id for it in items if not isinstance(it, Item) or it.language != lang.id]
            if wrong:
                raise ValueError(f"cards that are not {lang.id} cards: {wrong[:3]}")
        except Exception as exc:  # noqa: BLE001 - one broken file must not take the app down
            LOAD_ERRORS[name] = f"{type(exc).__name__}: {exc}"
            continue
        used.append(name)
        cards.extend(items)
    MODULES[lang.id] = tuple(used)
    return tuple(cards)


#: Every registered language's built-in deck, in the order cards are served (the first two lead). A language
#: with no cards yet has an empty deck and is not offered.
_ALL: dict[str, tuple[Item, ...]] = {lang.id: _load(lang) for lang in langs.LANGS}
#: Only the languages that have cards.
DECKS: dict[str, tuple[Item, ...]] = {lang_id: deck for lang_id, deck in _ALL.items() if deck}

#: The one the app uses: its files are found through the active progress store each time.
STORE = GotchaStore()


def builtin_deck(language: str) -> tuple[Item, ...]:
    return DECKS.get(language, ())


def title(language: str) -> str:
    return langs.get(language).title if langs.known(language) else "Quiz"


def available_languages() -> list[str]:
    """The languages the app can offer on this machine: toolchain installed AND at least one card, in
    display order (a language whose compiler is missing is hidden, one with an empty deck is not ready)."""
    from .runner import available_languages as installed

    return [lang_id for lang_id in installed() if DECKS.get(lang_id)]


def languages_payload() -> list[dict]:
    """What the language switch shows: [{id, name, count, title}] for the available languages, in order."""
    ids = available_languages()
    counts = STORE.counts(ids)
    return [{"id": i, "name": langs.get(i).name, "count": counts.get(i, 0), "title": langs.get(i).title}
            for i in ids]


__all__ = ["BadChoice", "DECKS", "GotchaStore", "Item", "LANGUAGES", "LOAD_ERRORS", "MODULES", "STORE",
           "UnknownCard", "available_languages", "builtin_deck", "languages_payload", "served_options", "title"]
