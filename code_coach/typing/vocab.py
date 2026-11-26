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

# A second helping of each: forty and thirty words were two sittings of the
# Define drill, and the point of it is coming back to them.
GENERAL_MORE: tuple[Word, ...] = (
    _w("ameliorate", "make a bad situation better"),
    _w("anomaly", "something that does not fit the pattern"),
    _w("benevolent", "kind, and meaning well"),
    _w("circumspect", "careful to think of what could go wrong"),
    _w("complacent", "too pleased with things to keep trying"),
    _w("conducive", "making something more likely to happen"),
    _w("conjecture", "a guess made without full evidence"),
    _w("corroborate", "confirm with further evidence"),
    _w("cursory", "quick and not thorough"),
    _w("deference", "respect shown by giving way"),
    _w("delineate", "describe or mark out exactly"),
    _w("deliberate", "done on purpose, after thought"),
    _w("diffident", "shy, and lacking confidence"),
    _w("discrepancy", "a difference where things should agree"),
    _w("eloquent", "fluent and persuasive in speech"),
    _w("empirical", "based on what is observed, not on theory"),
    _w("ephemera", "things meant to last only a short time"),
    _w("equanimity", "calm, especially under pressure"),
    _w("exacerbate", "make a problem worse"),
    _w("expedient", "convenient, even if not quite right"),
    _w("fastidious", "very careful about accuracy and detail"),
    _w("frugal", "careful not to waste money"),
    _w("gregarious", "fond of company"),
    _w("impartial", "treating every side the same"),
    _w("incisive", "clear and sharply to the point"),
    _w("indelible", "impossible to remove or forget"),
    _w("innocuous", "harmless, and unlikely to offend"),
    _w("laconic", "using very few words"),
    _w("lucid", "clear and easy to understand"),
    _w("magnanimous", "generous towards a rival"),
    _w("mundane", "ordinary and everyday"),
    _w("nonchalant", "calm and seeming not to care"),
    _w("onerous", "heavy with work or responsibility"),
    _w("ostensible", "stated, but perhaps not the real reason"),
    _w("paradigm", "a typical model or way of thinking"),
    _w("paramount", "more important than anything else"),
    _w("perfunctory", "done only because it has to be"),
    _w("pervasive", "spread throughout"),
    _w("precarious", "likely to fall or fail"),
    _w("proficient", "skilled from practice"),
    _w("prolific", "producing a great deal"),
    _w("reticent", "not saying much about oneself"),
    _w("sanguine", "hopeful, even when things look bad"),
    _w("sporadic", "happening now and then, irregularly"),
    _w("stoic", "enduring hardship without complaint"),
    _w("tenacious", "keeps hold and does not give up"),
    _w("ubiquitous", "found everywhere"),
    _w("unprecedented", "never done or seen before"),
    _w("verbose", "using more words than needed"),
    _w("vindicate", "show to have been right"),
)

TECHNICAL_MORE: tuple[Word, ...] = (
    _w("algorithm", "a step-by-step method for solving a problem"),
    _w("allocation", "setting aside memory for something to use"),
    _w("annotation", "a note attached to code, such as a type hint"),
    _w("argument", "a value handed to a function when it is called"),
    _w("assertion", "a check that stops the program if it is false"),
    _w("binding", "a name tied to a value"),
    _w("bottleneck", "the slowest part that holds everything up"),
    _w("buffer", "memory holding data on its way somewhere"),
    _w("callback", "a function handed over to be called later"),
    _w("closure", "a function that remembers the variables around it"),
    _w("compiler", "turns source code into something the machine runs"),
    _w("coupling", "how much one part depends on another"),
    _w("cohesion", "how closely the parts of one module belong together"),
    _w("declarative", "saying what you want, not how to get it"),
    _w("dependency", "something your code needs in order to work"),
    _w("deprecated", "still there, but on its way out"),
    _w("encapsulation", "keeping an object's insides hidden behind methods"),
    _w("enumerate", "go through one by one, counting as you go"),
    _w("exception", "an error raised to stop normal flow"),
    _w("fallback", "what is used when the first choice fails"),
    _w("generator", "a function that hands out values one at a time"),
    _w("hashable", "can be a dictionary key, because its hash never changes"),
    _w("imperative", "telling the machine each step to take"),
    _w("inheritance", "a class taking the behaviour of another"),
    _w("instance", "one particular object made from a class"),
    _w("interpreter", "runs source code line by line"),
    _w("iterable", "anything a for loop can walk through"),
    _w("lexical", "decided by where the code is written"),
    _w("literal", "a value written directly in the code"),
    _w("memoise", "remember results so they are not worked out twice"),
    _w("middleware", "code that sits between a request and its handler"),
    _w("namespace", "a space in which each name means one thing"),
    _w("nullable", "allowed to hold no value at all"),
    _w("operand", "a value an operator works on"),
    _w("parameter", "a name in a function's definition for an input"),
    _w("payload", "the data a message actually carries"),
    _w("polymorphism", "one interface, many kinds of object behind it"),
    _w("predicate", "a function that answers true or false"),
    _w("queue", "first in, first out"),
    _w("runtime", "while the program is running"),
    _w("scope", "where in the code a name can be seen"),
    _w("sentinel", "a special value that marks the end or a missing value"),
    _w("singleton", "the one and only instance of something"),
    _w("stack", "last in, first out"),
    _w("syntax", "the rules for how code must be written"),
    _w("thread", "one path of execution inside a program"),
    _w("tuple", "a fixed sequence of values"),
    _w("variadic", "taking any number of arguments"),
    _w("wrapper", "code that surrounds other code to add to it"),
    _w("yield", "hand back a value and pause until asked again"),
)

ALL_WORDS: tuple[Word, ...] = GENERAL + GENERAL_MORE + TECHNICAL + TECHNICAL_MORE

BY_WORD: dict[str, Word] = {w.word: w for w in ALL_WORDS}


def meaning_for(word: str) -> str:
    found = BY_WORD.get(word)
    return found.meaning if found else ""
