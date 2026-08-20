"""Vocabulary for the typing drills.

Typing practice is repetitive by nature, so the repetition may as well leave
something behind. Each word carries a short definition shown while you type it,
and the "define" mode reverses it: you get the meaning and have to produce the
word, so you're recalling rather than copying.

Words are chosen to be worth knowing and pleasant to type — nothing so obscure
it feels like a spelling bee, nothing so common it teaches nothing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Word:
    word: str
    meaning: str


def _w(word: str, meaning: str) -> Word:
    return Word(word, meaning)


# Everyday-useful words most people half-know.
GENERAL: tuple[Word, ...] = (
    _w("candid", "honest, even when it's awkward"),
    _w("prudent", "careful about the consequences"),
    _w("astute", "quick to see what's really going on"),
    _w("nuance", "a small difference that changes the meaning"),
    _w("succinct", "said in few words, and none wasted"),
    _w("tangible", "solid enough to touch or measure"),
    _w("ambiguous", "open to more than one reading"),
    _w("meticulous", "careful about every small detail"),
    _w("pragmatic", "concerned with what actually works"),
    _w("resilient", "recovers quickly from difficulty"),
    _w("scrutinise", "examine closely and critically"),
    _w("coherent", "hangs together and makes sense"),
    _w("arbitrary", "chosen for no particular reason"),
    _w("plausible", "believable, though not proven"),
    _w("redundant", "more than is needed"),
    _w("robust", "keeps working under strain"),
    _w("concise", "short and complete at once"),
    _w("implicit", "meant but never actually said"),
    _w("explicit", "stated outright, leaving no doubt"),
    _w("obsolete", "superseded, no longer in use"),
    _w("intuitive", "understood without being explained"),
    _w("volatile", "liable to change suddenly"),
    _w("tedious", "dull because it goes on too long"),
    _w("elegant", "solves the problem with nothing spare"),
    _w("candour", "frankness, even when unflattering"),
    _w("diligent", "steady and careful in effort"),
    _w("adept", "highly skilled at something"),
    _w("brevity", "shortness of expression"),
    _w("cogent", "clear and convincing"),
    _w("discern", "make out something not obvious"),
    _w("emulate", "match by imitating"),
    _w("feasible", "possible to actually do"),
    _w("inherent", "part of the thing's nature"),
    _w("mitigate", "make less severe"),
    _w("novel", "new and unlike what came before"),
    _w("obscure", "hard to see or understand"),
    _w("rigorous", "thorough and exacting"),
    _w("salient", "standing out as important"),
    _w("viable", "able to work or survive"),
    _w("candidly", "openly and honestly"),
)

# Words a programmer meets in documentation and code review.
TECHNICAL: tuple[Word, ...] = (
    _w("idempotent", "doing it twice changes nothing more than once did"),
    _w("deterministic", "same input, same output, every time"),
    _w("recursive", "defined in terms of itself"),
    _w("immutable", "cannot be changed once made"),
    _w("asynchronous", "not waiting for it to finish before moving on"),
    _w("concurrent", "several things in progress at once"),
    _w("latency", "the delay before something responds"),
    _w("throughput", "how much gets done per unit of time"),
    _w("cache", "a copy kept close by, to save fetching it again"),
    _w("heuristic", "a rule of thumb that's usually right"),
    _w("refactor", "restructure code without changing what it does"),
    _w("regression", "something that used to work and now doesn't"),
    _w("boilerplate", "code you must write but nobody reads"),
    _w("idiomatic", "written the way this language is normally written"),
    _w("abstraction", "hiding detail behind a simpler idea"),
    _w("invariant", "something that stays true throughout"),
    _w("mutable", "able to be changed in place"),
    _w("overhead", "cost paid on top of the useful work"),
    _w("parity", "being equivalent across two things"),
    _w("throttle", "deliberately slow something down"),
    _w("traversal", "visiting every part of a structure"),
    _w("serialise", "turn a structure into something storable"),
    _w("ephemeral", "short-lived by design"),
    _w("orthogonal", "independent — changing one doesn't affect the other"),
    _w("canonical", "the one agreed, standard form"),
    _w("granular", "broken into small, separately handled pieces"),
    _w("provenance", "the record of where something came from"),
    _w("stochastic", "governed by chance rather than a fixed rule"),
    _w("contiguous", "next to each other with no gaps"),
    _w("amortised", "an occasional big cost spread over many cheap ones"),
)

ALL_WORDS: tuple[Word, ...] = GENERAL + TECHNICAL

BY_WORD: dict[str, Word] = {w.word: w for w in ALL_WORDS}


def meaning_for(word: str) -> str:
    found = BY_WORD.get(word)
    return found.meaning if found else ""
