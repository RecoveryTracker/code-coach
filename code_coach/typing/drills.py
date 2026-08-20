"""Typing drills: which keys are in play, and how you practise them.

A drill is a *section* (which keys) crossed with a *mode* (how they're put in
front of you). The same home-row keys can be whack-a-mole reflexes, drilled
sequences, or real words — and those train different things, so they're
separate modes over one set of keys rather than separate content.

Prompts are generated rather than hand-written wherever the point is coverage,
and hand-written where the point is that the text reads like English.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from code_coach.typing import english
from code_coach.typing.keys import (
    BOTTOM_ROW,
    HOME_ROW,
    NUMBER_ROW,
    TOP_ROW,
    name_for,
    needs_shift,
)
from code_coach.typing.texts import (
    AFFIRMATIONS,
    CHAPTERS,
    THEMED,
    CONSCIOUS_LINES,
    CONSCIOUS_WORDS,
    VERSES,
    Passage,
)
from code_coach.typing.vocab import GENERAL, TECHNICAL, meaning_for

# ── Sections: which characters a drill draws from ───────────


def _chars(rows, shifted: bool = False) -> tuple[str, ...]:
    return tuple(k.shifted if shifted else k.char for k in rows)


HOME_LETTERS = tuple(k.char for k in HOME_ROW if k.is_letter)
TOP_LETTERS = tuple(k.char for k in TOP_ROW if k.is_letter)
BOTTOM_LETTERS = tuple(k.char for k in BOTTOM_ROW if k.is_letter)
ALL_LETTERS = HOME_LETTERS + TOP_LETTERS + BOTTOM_LETTERS
DIGITS = tuple(k.char for k in NUMBER_ROW if k.char.isdigit())

# The shifted symbols — the row people never learn properly.
SHIFTED_SYMBOLS = tuple(
    k.shifted for k in NUMBER_ROW if not k.shifted.isalnum()
) + ("{", "}", "|", ":", '"', "<", ">", "?")

# Unshifted punctuation.
PLAIN_SYMBOLS = ("`", "-", "=", "[", "]", "\\", ";", "'", ",", ".", "/")

# What you actually reach for while writing code, in rough order of how often.
CODING_SYMBOLS = (
    "(", ")", "{", "}", "[", "]", ";", ":", "=", ".", ",", "\"", "'",
    "_", "-", ">", "<", "!", "&", "|", "*", "/", "+", "#", "$", "%",
    "@", "^", "~", "?", "\\", "`",
)


@dataclass(frozen=True)
class Section:
    id: str
    name: str
    description: str
    chars: tuple[str, ...]
    # Words drawn only from this section's letters, when that's possible.
    words: tuple[str, ...] = field(default_factory=tuple)
    # Longer lines, each with a reference shown beneath — scripture, lyrics,
    # affirmations. Used by the speed mode in place of the generic pangrams.
    passages: tuple[Passage, ...] = field(default_factory=tuple)
    # A definition lookup, for sections whose words carry meanings.
    meanings: dict[str, str] = field(default_factory=dict)


SECTIONS: tuple[Section, ...] = (
    Section(
        "home", "Home Row",
        "Where your fingers rest. Everything else is measured from here.",
        HOME_LETTERS,
        # Every one is typeable without leaving a s d f g h j k l.
        (
            "dad", "sad", "lad", "lads", "half", "hall", "halls", "flask",
            "gash", "shall", "salad", "salads", "glass", "flash", "alfalfa",
            "shad", "sash", "lash", "gall", "dash", "flag", "flags", "gala",
            "hags", "has", "gas", "all", "fall", "glad", "adds", "gash",
        ),
    ),
    Section(
        "top", "Top Row",
        "Reaching up. The row that holds most of English.",
        TOP_LETTERS,
        (
            "type", "quiet", "power", "your", "were", "quote", "puppet",
            "reporter", "tripwire", "otter", "peer", "route", "wrote",
            "utter", "petty", "output", "prettier", "typewriter", "require",
            "poetry", "tutor", "pewter", "torque", "riot",
        ),
    ),
    Section(
        "bottom", "Bottom Row",
        "Reaching down — the row that gets skipped, and the one that slows you.",
        BOTTOM_LETTERS,
        # No word list on purpose: z x c v b n m has no vowels, so nothing in
        # English is typeable from this row alone. Words mode is hidden here.
    ),
    Section(
        "letters", "All Letters",
        "The whole alphabet, mixed.",
        ALL_LETTERS,
    ),
    Section(
        "numbers", "Numbers",
        "The row you look down at. Stop looking.",
        DIGITS,
    ),
    Section(
        "symbols", "Symbols",
        "Shift plus the number row, and the punctuation nobody drills.",
        SHIFTED_SYMBOLS + PLAIN_SYMBOLS,
    ),
    Section(
        "coding", "Coding Punctuation",
        "Brackets, operators and quotes — the keys code is actually made of.",
        CODING_SYMBOLS,
    ),
    Section(
        "everything", "Everything",
        "Letters, numbers and symbols together, which is what real typing is.",
        ALL_LETTERS + DIGITS + SHIFTED_SYMBOLS + PLAIN_SYMBOLS,
    ),
    # The repetition has to happen anyway; these leave something behind.
    Section(
        "vocab", "Vocabulary",
        "Words worth knowing, with their meaning shown as you type them.",
        ALL_LETTERS,
        tuple(w.word for w in GENERAL),
    ),
    Section(
        "jargon", "Programming Words",
        "The vocabulary of documentation and code review.",
        ALL_LETTERS,
        tuple(w.word for w in TECHNICAL),
    ),
    Section(
        "scripture", "Scripture",
        "Verses and passages, King James Version. The reference shows with each one.",
        ALL_LETTERS,
        passages=VERSES + THEMED + CHAPTERS,
    ),
    Section(
        "affirmations", "Affirmations",
        "Lines worth repeating, since you're going to repeat something anyway.",
        ALL_LETTERS,
        passages=AFFIRMATIONS,
    ),
    Section(
        "conscious", "Conscious Words",
        "Roots, reasoning and livity — words from reggae and festival culture.",
        ALL_LETTERS,
        tuple(w for w, _ in CONSCIOUS_WORDS),
        passages=CONSCIOUS_LINES,
        meanings=dict(CONSCIOUS_WORDS),
    ),
)

SECTIONS_BY_ID = {s.id: s for s in SECTIONS}


def _named_chars(section: Section) -> tuple[str, ...]:
    """Keys with a spoken name distinct from the key, so "press the pipe" is
    a real test of recall rather than a restatement of the answer."""
    return tuple(c for c in section.chars if name_for(c) != c)


# ── English text, for the modes where reading matters ───────

SENTENCES: tuple[str, ...] = (
    "the quick brown fox jumps over the lazy dog",
    "pack my box with five dozen liquor jugs",
    "how vexingly quick daft zebras jump",
    "waltz nymph for quick jigs vex bud",
    "the five boxing wizards jump quickly",
    "sphinx of black quartz judge my vow",
    "we promptly judged antique ivory buckles",
    "a wizard's job is to vex chumps quickly in fog",
    "jackdaws love my big sphinx of quartz",
    "crazy Fredrick bought many very exquisite opal jewels",
)

# Longer prose, for measuring a real speed rather than a burst.
PARAGRAPHS: tuple[str, ...] = (
    "Typing well is mostly about not looking down. The keys do not move, so "
    "your hands can learn where they are and leave your eyes free to read "
    "what you are writing.",
    "Speed comes last. Accuracy comes first, because every mistake costs you "
    "the time to notice it, the time to delete it, and the time to type it "
    "again. Slow and correct is faster than quick and wrong.",
    "The hardest keys are the ones you use least. Most people are fluent "
    "across the letters and hunt for a brace, a pipe or a tilde, which is "
    "exactly where the time goes when you are writing code.",
)

# Real code fragments, for the punctuation that actually appears in code.
CODE_SNIPPETS: tuple[str, ...] = (
    "const { a, b } = obj;",
    "if (x !== y) return [];",
    "arr.map((n) => n * 2);",
    "print(f\"{name}: {count}\")",
    "for (let i = 0; i < n; i++) {",
    "seen[nums[i]] = i;",
    "return a?.b ?? c;",
    "counts[ch] = counts.get(ch, 0) + 1",
    "let x: number[] = [];",
    "while (left < right) {",
    "#include <stdio.h>",
    "SELECT * FROM users WHERE id = 1;",
    "grid[r][c] = '#';",
    "fn main() -> i32 { 0 }",
    "x = (a + b) * (c - d) / e;",
)

# Two- and three-character sequences that live in muscle memory or don't.
CODE_TOKENS: tuple[str, ...] = (
    "=>", "->", "!=", "==", "===", "!==", "<=", ">=", "&&", "||", "??",
    "::", ":=", "+=", "-=", "*=", "/=", "**", "//", "/*", "*/", "<>",
    "{}", "[]", "()", "<>", "();", "{};", "0x", "\\n", "\\t", "$_",
)


# ── Modes ───────────────────────────────────────────────────


@dataclass(frozen=True)
class Mode:
    id: str
    name: str
    description: str
    # Show only the current target, with nothing coming up next.
    hidden: bool = False
    # Prompt with the character's name rather than the character.
    by_name: bool = False


MODES: tuple[Mode, ...] = (
    Mode(
        "whack", "Whack-a-Key",
        "One key lights up. Hit it as fast as you can — you can't see what's next.",
        hidden=True,
    ),
    Mode(
        "recall", "Name to Key",
        "You're told the name — 'pipe', 'tilde' — and have to know where it lives.",
        hidden=True,
        by_name=True,
    ),
    Mode(
        "sweep", "Every Key Once",
        "Every key in this section, exactly once, in an order you've not seen.",
        hidden=True,
    ),
    Mode(
        "drill", "Key Runs",
        "Short bursts from this section, with what's coming up visible.",
    ),
    Mode(
        "pairs", "Key Pairs",
        "The combinations hands actually learn — th, er, ing, => and the rest.",
    ),
    Mode(
        "words", "Words",
        "Real words built from this section's keys.",
    ),
    Mode(
        "common", "Common Words",
        "The words that make up most of English. This is the ordinary practice.",
    ),
    Mode(
        "timed", "One Minute",
        "Sixty seconds of common words. The standard way to measure a speed.",
    ),
    Mode(
        "perfect", "No Mistakes",
        "One wrong key and the line starts again. Builds accuracy, tests nerve.",
    ),
    Mode(
        "speed", "Speed Run",
        "A full passage. Accuracy first — the speed follows.",
    ),
    Mode(
        "define", "Meaning to Word",
        "You get the definition and type the word — recall, not copying.",
        hidden=True,
        by_name=True,
    ),
)

MODES_BY_ID = {m.id: m for m in MODES}


@dataclass(frozen=True)
class Target:
    """One thing to type: a single key, a word, or a whole line."""

    text: str
    prompt: str
    # Set when the character needs Shift, so the trainer can say so.
    shift: bool = False
    # Shown beside the target — a definition, so the repetition teaches
    # something besides finger placement.
    note: str = ""


@dataclass
class TypingDrill:
    id: str
    section: str
    mode: str
    name: str
    description: str
    targets: list[Target]
    hidden: bool
    # A run of single keys is scored on reaction time; text on words a minute.
    scoring: str  # reaction | wpm


def _rng(seed: str) -> random.Random:
    return random.Random(seed)


def _no_repeats(rng: random.Random, pool: tuple[str, ...], count: int) -> list[str]:
    """Random draw that never asks for the same thing twice running.

    Back-to-back repeats make a reflex drill measure something else: you're no
    longer finding the key, just pressing it again.
    """
    out: list[str] = []
    for _ in range(count):
        choice = rng.choice(pool)
        if out and choice == out[-1] and len(pool) > 1:
            others = [c for c in pool if c != out[-1]]
            choice = rng.choice(others)
        out.append(choice)
    return out


def build_drill(
    section_id: str,
    mode_id: str,
    *,
    seed: str = "typing",
    count: int = 30,
) -> TypingDrill:
    section = SECTIONS_BY_ID.get(section_id) or SECTIONS[0]
    mode = MODES_BY_ID.get(mode_id) or MODES[0]
    rng = _rng(f"{section.id}:{mode.id}:{seed}")
    targets: list[Target] = []
    scoring = "reaction"

    if mode.id in ("whack", "recall"):
        pool = _named_chars(section) if mode.by_name else section.chars
        for ch in _no_repeats(rng, pool, count):
            prompt = name_for(ch) if mode.by_name else ch
            targets.append(Target(text=ch, prompt=prompt, shift=needs_shift(ch)))

    elif mode.id == "sweep":
        # Every key exactly once. A shuffle rather than a draw, so the run
        # covers the section completely and can't dwell on the easy keys —
        # and a fresh order each time means you can't learn the sequence
        # instead of the keys.
        pool = list(section.chars)
        rng.shuffle(pool)
        for position, ch in enumerate(pool, start=1):
            targets.append(
                Target(
                    text=ch,
                    prompt=ch,
                    shift=needs_shift(ch),
                    note=f"{position} of {len(pool)}",
                )
            )

    elif mode.id == "drill":
        # Short runs, so the hand learns a shape rather than one key.
        size = 4
        for _ in range(max(1, count // size)):
            run = "".join(_no_repeats(rng, section.chars, size))
            targets.append(Target(text=run, prompt=run))
        scoring = "wpm"

    elif mode.id == "pairs":
        for pair in _pairs_for(section, rng, max(8, count // 2)):
            targets.append(Target(text=pair, prompt=pair))
        scoring = "wpm"

    elif mode.id in ("common", "timed"):
        # "One Minute" is the same material with a clock over it; the timing
        # is the trainer's job, so all that changes here is how much is
        # queued up. Sixty seconds at a fast pace is a lot of words.
        pool = english.words_typeable_from(section.chars) or english.COMMON_WORDS
        wanted = 220 if mode.id == "timed" else max(12, count // 2)
        for word in _no_repeats(rng, pool, wanted):
            targets.append(Target(text=word, prompt=word))
        scoring = "wpm"

    elif mode.id == "perfect":
        # Fewer, longer targets: a restart has to cost something to matter,
        # but not so much that a slip near the end is punishing. Short
        # symbol tokens are excluded — restarting "->" tests nothing.
        long_enough = [p for p in _speed_passages(section, rng) if len(p.text) >= 18]
        if not long_enough:
            picks = rng.sample(CODE_SNIPPETS, k=min(4, len(CODE_SNIPPETS)))
            long_enough = [Passage(s, "code") for s in picks]
        for passage in long_enough[:4]:
            targets.append(
                Target(text=passage.text, prompt=passage.text, note=passage.source)
            )
        scoring = "wpm"

    elif mode.id == "words":
        for word in _no_repeats(rng, section.words, max(6, count // 3)):
            targets.append(
                Target(text=word, prompt=word, note=_meaning(section, word))
            )
        scoring = "wpm"

    elif mode.id == "define":
        # The definition is the prompt; the word is the answer.
        for word in _no_repeats(rng, section.words, max(6, count // 3)):
            targets.append(
                Target(text=word, prompt=_meaning(section, word), note=word)
            )
        scoring = "wpm"

    else:  # speed
        for passage in _speed_passages(section, rng):
            targets.append(
                Target(text=passage.text, prompt=passage.text, note=passage.source)
            )
        scoring = "wpm"

    return TypingDrill(
        id=f"typing-{section.id}-{mode.id}",
        section=section.id,
        mode=mode.id,
        name=f"{section.name} · {mode.name}",
        description=mode.description,
        targets=targets,
        hidden=mode.hidden,
        scoring=scoring,
    )


def _pairs_for(
    section: Section, rng: random.Random, wanted: int
) -> list[str]:
    """The combinations this section is actually made of.

    Real English bigrams where the section has the letters for them, real code
    digraphs where it has the symbols, and generated pairs only as a last
    resort — a made-up pair drills the transition without teaching anything
    you'll meet again.
    """
    allowed = set(section.chars)
    real = [
        p
        for p in (*english.BIGRAMS, *english.TRIGRAMS)
        if set(p) <= allowed
    ]
    code = [p for p in english.CODE_PAIRS if set(p) <= allowed]
    pool = real + code
    if len(pool) >= 6:
        return list(rng.sample(pool, k=min(wanted, len(pool))))
    # Sections of pure symbols or digits have no real combinations, so build
    # them from the section's own keys.
    made: list[str] = []
    for _ in range(wanted):
        made.append("".join(_no_repeats(rng, section.chars, 2)))
    return made


def _meaning(section: Section, word: str) -> str:
    """A section's own definitions win; the shared vocabulary is the fallback."""
    return section.meanings.get(word) or meaning_for(word)


def _speed_passages(section: Section, rng: random.Random) -> list[Passage]:
    # A section that brought its own text uses it — that text is the point.
    if section.passages:
        return list(rng.sample(section.passages, k=min(6, len(section.passages))))
    if section.id == "coding":
        picks = rng.sample(CODE_SNIPPETS, k=min(6, len(CODE_SNIPPETS)))
        return [Passage(s, "code") for s in picks]
    if section.id in ("symbols", "numbers"):
        picks = rng.sample(CODE_TOKENS, k=min(12, len(CODE_TOKENS)))
        return [Passage(t, "token") for t in picks]
    if section.id == "everything":
        return [Passage(rng.choice(PARAGRAPHS), "on typing")]
    picks = rng.sample(SENTENCES, k=min(4, len(SENTENCES)))
    return [Passage(s, "pangram") for s in picks]


def _mode_fits(mode: Mode, section: Section) -> bool:
    """Whether a mode makes sense for a section.

    Offering one that doesn't produces a drill that technically runs and
    teaches nothing — 'words' made of consonants, or being asked to recall
    where the letter K is by being told "k".
    """
    if mode.id in ("words", "define") and not section.words:
        return False
    # "Meaning to word" needs definitions to prompt with.
    if mode.id == "define" and not _meaning(section, section.words[0]):
        return False
    # "Name to key" needs a name that isn't simply the key — naming the letter
    # K tells you it's K, so it only makes sense for symbols.
    if mode.id == "recall" and len(_named_chars(section)) < 4:
        return False
    # The common-word modes are only honest where the section can actually
    # type common words. Home Row alone reaches about a dozen of them, which
    # is a word list, not a speed test.
    if mode.id in ("common", "timed"):
        if len(english.words_typeable_from(section.chars)) < 60:
            return False
    # A sweep has to be worth sweeping.
    if mode.id == "sweep" and len(section.chars) < 6:
        return False
    return True


def catalog() -> list[dict]:
    """Sections and modes, for building the picker."""
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "keys": list(s.chars),
            "modes": [
                {
                    "id": m.id,
                    "name": m.name,
                    "description": m.description,
                    "hidden": m.hidden,
                    "by_name": m.by_name,
                }
                for m in MODES
                if _mode_fits(m, s)
            ],
        }
        for s in SECTIONS
    ]
