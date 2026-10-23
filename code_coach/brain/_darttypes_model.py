"""Hand models for the Dart types and OOP pack (`pack_darttypes.py`): the pieces that `_dart_model.py` does not have.

Nothing here asks a runtime anything. The pieces:

* `chain` - Dart's mixin linearisation. `class B extends A with M, N` is read bottom-up: A, then M on top of A, then N
  on top of M, then B's own members on top. A call walks down from the top layer and stops at the first layer that
  does not call `super`.
* `ENUMS` - small enum shapes (name, constants) the Enum Facts templates choose from.
* `SHAPES` - a few tiny class families used by the sealed and abstract templates.
"""

from __future__ import annotations

import random

from ._dart_model import to_upper


def chain(layers: list[tuple[str, bool]]) -> str:
    """What a method that each layer answers with its tag (plus `super.f()` when it calls super) returns.

    `layers` run from the TOP (the class itself, or the last mixin) down to the bottom (the base class, whose flag is
    False because there is nothing under it): the tags are glued from the top until a layer stops calling super.
    """
    out = ""
    for tag, calls_super in layers:
        out += tag
        if not calls_super:
            break
    return out


def lin(base: str, mixins: list[tuple[str, bool]], own: tuple[str, bool] | None = None) -> str:
    """`chain` for `class B extends A with m1, m2`: `base` is A's tag, `mixins` the (tag, calls_super) of m1, m2 in the
    order written, `own` B's own (tag, calls_super) if B overrides the method."""
    layers = ([own] if own else []) + list(reversed(mixins)) + [(base, False)]
    return chain(layers)


#: (enum name, its constants), the shapes the Enum Facts templates choose from.
ENUMS: list[tuple[str, tuple[str, ...]]] = [
    ("Color", ("red", "green", "blue")),
    ("Dir", ("north", "east", "south", "west")),
    ("Size", ("small", "medium", "large")),
    ("Level", ("low", "mid", "high", "max")),
    ("Day", ("mon", "tue", "wed", "thu", "fri")),
    ("Coin", ("penny", "nickel", "dime", "quarter")),
    ("Mode", ("off", "on", "auto")),
    ("Suit", ("clubs", "hearts", "spades")),
]


def pick_enum(rng: random.Random) -> tuple[str, tuple[str, ...]]:
    return rng.choice(ENUMS)


def decl(name: str, names: tuple[str, ...]) -> str:
    """`enum Color { red, green, blue }`"""
    return f"enum {name} {{ {', '.join(names)} }}"


def upper(s: str) -> str:
    return to_upper(s)


def ordinal(n: int) -> str:
    """1 -> 1st, 2 -> 2nd, 3 -> 3rd, 4 -> 4th, 11 -> 11th, 21 -> 21st."""
    if n % 100 in (11, 12, 13):
        return f"{n}th"
    return f"{n}{({1: 'st', 2: 'nd', 3: 'rd'}).get(n % 10, 'th')}"
