"""Momentum: one sense of progress across every mode.

Every screen reports a real success with `award(kind, key)` (through
POST /api/momentum/award). The server owns the prices (`rules.XP`), pays a kind
and key once a day, builds a combo for awards close together, rolls the odd
lucky bonus, and keeps the XP, level, day streak (with freezes), three daily
quests and a chest in `momentum.json` beside the progress file. A few things only
the server can see (the Farm's milestones and welcome-back) are paid by the server
itself (`SERVER_XP`, `Momentum.award_server`), never on the browser's word.

It rewards and never punishes: a day you miss costs nothing but a freeze you
may or may not have, and there is nothing to lose and nothing to compare.
See `rules.py` for the numbers and `engine.py` for how it is kept.
"""

from __future__ import annotations

from . import rules
from .engine import Momentum, UnknownKind, save_path
from .rules import MICRO_KINDS, SERVER_XP, UNUSED_KINDS, XP

#: The one the app uses: its file is found through the active progress store each time.
MOMENTUM = Momentum()


def award(kind: str, key: str) -> dict:
    return MOMENTUM.award(kind, key)


def summary() -> dict:
    return MOMENTUM.summary()


def claim_chest() -> dict:
    return MOMENTUM.claim_chest()


__all__ = [
    "MICRO_KINDS", "MOMENTUM", "Momentum", "SERVER_XP", "UNUSED_KINDS", "UnknownKind", "XP",
    "award", "claim_chest", "rules", "save_path", "summary",
]
