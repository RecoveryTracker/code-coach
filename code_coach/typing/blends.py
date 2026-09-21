"""Several themes typed as one pool.

The picker used to be one choice at a time, which is right for most of
what is in it — you do not want the Zen of Python shuffled into a
scripture drill. It is wrong for the case it was asked for: somebody
learning Python wants Python code and Python lore in the same sitting,
and somebody working on two languages wants both.

So a theme id may now name several themes, joined with commas:
"python,pycode" is Python's lore and Python's code drawn from one pool.
A single id behaves exactly as it did, which matters more than it
sounds — every stored setting, every deep link and every test that was
written before this still means what it meant.

What a blend is, and what it is not
-----------------------------------
A blend is a Theme like any other, built by concatenating the parts.
That is the whole trick: nothing downstream knows a blend from a plain
theme, so the mode logic, the fallbacks, the dealing and the note
handling all keep working without a second code path to maintain.

Order is the order you picked, and the draw is random over the result,
so a blend of a 66-line lore theme and an 854-line code theme is mostly
code. That is arithmetic rather than a decision, and it is the right
arithmetic: the bigger pool is bigger because there is more to learn in
it. Somebody who wants an even split can pick the two lore themes.

Duplicates are dropped, keeping the first note, because the same line
appearing in two themes is one line to type and two chances to be told
different things about it.
"""

from __future__ import annotations

#: What separates the parts of a blended id. A comma survives a URL
#: query string, a JSON settings file and a React key without escaping,
#: and no theme id contains one.
SEPARATOR = ","

#: How many themes may be blended at once. Not a technical limit: past
#: this the picker is a wall of ticks and the pool is so mixed that no
#: single sitting covers any of it, which is the opposite of practice.
MAX_PARTS = 6


def split_id(theme_id: str) -> list[str]:
    """The parts of a theme id, in the order they were given.

    Blank parts are dropped rather than looked up, so a trailing comma
    from a settings file that was edited by hand does not become a
    404.
    """
    return [part.strip() for part in theme_id.split(SEPARATOR) if part.strip()]


def join_ids(parts: list[str]) -> str:
    return SEPARATOR.join(parts)


def is_blend(theme_id: str) -> bool:
    return len(split_id(theme_id)) > 1


def blend(themes: list, *, joined_name: str | None = None):
    """One Theme holding every part's material, in order.

    Takes the Theme class from its first argument rather than importing
    it, because drills.py imports this module and the reverse would be
    a cycle.
    """
    if not themes:
        raise ValueError("a blend needs at least one theme")
    if len(themes) == 1:
        return themes[0]

    kind = type(themes[0])
    ids = [t.id for t in themes]
    names = [t.name for t in themes]

    words: list[str] = []
    passages: list = []
    blocks: list = []
    meanings: dict[str, str] = {}
    seen_words: set[str] = set()
    seen_passages: set[str] = set()
    seen_blocks: set[str] = set()

    for theme in themes:
        for word in theme.words:
            if word not in seen_words:
                seen_words.add(word)
                words.append(word)
        for passage in theme.passages:
            if passage.text not in seen_passages:
                seen_passages.add(passage.text)
                passages.append(passage)
        for block in theme.blocks:
            if block.text not in seen_blocks:
                seen_blocks.add(block.text)
                blocks.append(block)
        # First definition wins, to match the first-note-wins rule above.
        for word, meaning in theme.meanings.items():
            meanings.setdefault(word, meaning)

    name = joined_name or " + ".join(names)
    return kind(
        id=join_ids(ids),
        name=name,
        description=(
            "Everything from " + " and ".join(names) + ", drawn from one pool."
        ),
        words=tuple(words),
        passages=tuple(passages),
        meanings=meanings,
        blocks=tuple(blocks),
    )
