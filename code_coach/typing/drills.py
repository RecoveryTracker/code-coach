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
import re
from dataclasses import dataclass, field

from code_coach.typing import english, langlore, thesaurus
from code_coach.typing.keys import (
    BOTTOM_ROW,
    HOME_ROW,
    NUMBER_ROW,
    TOP_ROW,
    name_for,
    needs_shift,
)
from code_coach.typing.curriculum import code_blocks_for, code_lines_for
from code_coach.typing.texts import (
    AFFIRMATIONS,
    CHAPTERS,
    THEMED,
    CONSCIOUS_LINES,
    CONSCIOUS_WORDS,
    PROSE,
    TYPING_LINES,
    VERSES,
    Passage,
)
from code_coach.typing.snippets import (
    DART_CODE,
    FRACTALS,
    JAVASCRIPT_CODE,
    PYTHON_CODE,
    SCHOOL,
    SQL_CODE,
    TRICKS,
    USEFUL,
    VISUALS,
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


# Everything a code snippet can contain, so the code sections aren't gated to
# a subset of the board.
EVERYTHING_CHARS = ALL_LETTERS + DIGITS + SHIFTED_SYMBOLS + PLAIN_SYMBOLS

# What an unthemed drill types. Passages about typing and about improving at
# something, plus the affirmations, because the repetition happens either way
# and it may as well leave something behind.
DEFAULT_LINES: tuple[Passage, ...] = TYPING_LINES + PROSE + AFFIRMATIONS

# Every annotated code line there is. The Code section reads as continuous
# code rather than punctuation in isolation, and each line's note says what it
# does — reading code at a glance is its own skill, and the one that makes
# reviewing someone else's work fast.
CODE_LINES: tuple[Passage, ...] = SCHOOL + TRICKS + USEFUL + VISUALS + FRACTALS


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
    # First and default: the whole keyboard is what typing actually is, and
    # everything below it is a narrower slice for when you want one.
    Section(
        "everything", "All",
        "The whole keyboard — letters, numbers and symbols, which is what "
        "real typing is.",
        ALL_LETTERS + DIGITS + SHIFTED_SYMBOLS + PLAIN_SYMBOLS,
    ),
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
        "coding", "Code Symbols",
        "Brackets, operators and quotes on their own — the reach, drilled.",
        CODING_SYMBOLS,
    ),
    Section(
        "code", "Code",
        "Whole lines of real code, each with a note saying what it does.",
        EVERYTHING_CHARS,
        # Its own material rather than the generic text: a code section that
        # served pangrams would be a letters section with a different name.
        passages=CODE_LINES,
    ),
)

SECTIONS_BY_ID = {s.id: s for s in SECTIONS}


# ── Themes: what the words and lines are *about* ────────────
#
# Which keys you're drilling and what text you're drilling them on are two
# different choices, and they were tangled together as one list. "Scripture"
# isn't a step in learning the keyboard the way "Top Row" is — it's what the
# sentences say. Separating them means the sections read as a curriculum, and
# the passages you'd actually like in your head can turn up in any of them.


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    description: str
    words: tuple[str, ...] = field(default_factory=tuple)
    passages: tuple[Passage, ...] = field(default_factory=tuple)
    meanings: dict[str, str] = field(default_factory=dict)
    # Whole functions and solutions, newlines and indentation included. A line
    # at a time drills the punctuation; a block drills the shape — what sits
    # under what, and Enter as part of writing code.
    blocks: tuple[Passage, ...] = field(default_factory=tuple)


THEMES: tuple[Theme, ...] = (
    Theme(
        "mixed", "Mixed",
        "Ordinary English, plus whatever suits the keys you picked.",
    ),
    Theme(
        "vocab", "Vocabulary",
        "Words worth knowing, with their meaning shown as you type them.",
        tuple(w.word for w in GENERAL),
    ),
    Theme(
        "jargon", "Programming Words",
        "The vocabulary of documentation and code review.",
        tuple(w.word for w in TECHNICAL),
    ),
    Theme(
        "scripture", "Scripture",
        "Verses and passages, King James Version, each with its reference.",
        passages=VERSES + THEMED + CHAPTERS,
    ),
    Theme(
        "affirmations", "Affirmations",
        "Lines worth repeating, since you're going to repeat something anyway.",
        passages=AFFIRMATIONS,
    ),
    Theme(
        "conscious", "Conscious Words",
        "Roots, reasoning and livity — words from reggae and festival culture.",
        tuple(w for w, _ in CONSCIOUS_WORDS),
        passages=CONSCIOUS_LINES,
        meanings=dict(CONSCIOUS_WORDS),
    ),
    Theme(
        "facts", "Facts",
        "Short pieces about how things work, from bees to bridges.",
        passages=PROSE,
    ),
    Theme(
        "typinglore", "About Typing",
        "Technique, practice and what actually makes anyone faster.",
        passages=TYPING_LINES,
    ),
    Theme(
        "wordlore", "Word Origins",
        "Where words came from, and why English has so many of them.",
        passages=langlore.WORDS,
    ),
    # Per-language material: syntax, design decisions, and the traps.
    Theme(
        "python", "Python Lore",
        "How Python is put together — including the Zen, which it ships with.",
        passages=langlore.PYTHON,
    ),
    Theme(
        "javascript", "JavaScript Lore",
        "Ten days in 1995, and everything that followed from it.",
        passages=langlore.JAVASCRIPT,
    ),
    Theme(
        "dart", "Dart Lore",
        "Null safety, isolates, and a language built for interfaces.",
        passages=langlore.DART,
    ),
    Theme(
        "sql", "SQL Lore",
        "Describing what you want and letting the database plan the how.",
        passages=langlore.SQL,
    ),
    Theme(
        "clang", "C Lore",
        "A portable assembler with types, and the habits it demands.",
        passages=langlore.C_LORE,
    ),
    Theme(
        "rust", "Rust Lore",
        "Ownership, borrowing, and errors you cannot forget to handle.",
        passages=langlore.RUST,
    ),
    # Which language's code you're typing. Picking Code for the keys and then
    # one of these is how you drill the punctuation of the language you're
    # actually learning, rather than an average of several.
    #
    # Each pool is the hand-picked lines followed by everything the curriculum
    # teaches in that language — the solution bank and the fundamentals
    # snippets, line by line. They were twenty-odd curated lines each, which
    # two drills used up, and adding a language meant writing a second list
    # here as well as in the curriculum.
    Theme(
        "pycode", "Python Code",
        "Real Python lines, plus every solution the curriculum teaches.",
        passages=code_lines_for("python", curated=PYTHON_CODE),
        blocks=code_blocks_for("python"),
    ),
    Theme(
        "jscode", "JavaScript Code",
        "Destructuring, arrows and promises, plus the JavaScript solutions.",
        passages=code_lines_for("javascript", curated=JAVASCRIPT_CODE),
        blocks=code_blocks_for("javascript"),
    ),
    Theme(
        "tscode", "TypeScript Code",
        "Typed signatures, generics and the solutions written out in them.",
        passages=code_lines_for("typescript"),
        blocks=code_blocks_for("typescript"),
    ),
    Theme(
        "dartcode", "Dart Code",
        "Null-safe declarations and futures, plus the Dart solutions.",
        passages=code_lines_for("dart", curated=DART_CODE),
        blocks=code_blocks_for("dart"),
    ),
    Theme(
        "sqlcode", "SQL Code",
        "Selects, joins, grouping and the odd transaction.",
        passages=code_lines_for("sql", curated=SQL_CODE),
        blocks=code_blocks_for("sql"),
    ),
    Theme(
        "ccode", "C Code",
        "Pointers, structs and the loops they hang off.",
        passages=code_lines_for("c"),
        blocks=code_blocks_for("c"),
    ),
    Theme(
        "cppcode", "C++ Code",
        "The standard library shapes, and the punctuation that comes with them.",
        passages=code_lines_for("cpp"),
        blocks=code_blocks_for("cpp"),
    ),
    Theme(
        "rustcode", "Rust Code",
        "Ownership, matches and the question mark.",
        passages=code_lines_for("rust"),
        blocks=code_blocks_for("rust"),
    ),
    Theme(
        "school", "First Code",
        "The lines everyone writes first — loops, conditions, a function.",
        passages=SCHOOL,
    ),
    Theme(
        "tricks", "Code Tricks",
        "One-liners worth stealing: swaps, comprehensions, the good defaults.",
        passages=TRICKS,
    ),
    Theme(
        "visuals", "Drawings",
        "Short programs that print a picture. Type one, then go run it.",
        passages=VISUALS,
    ),
    Theme(
        "fractals", "Fractals",
        "The famous ones are shorter than you think. z = z * z + c is all of it.",
        passages=FRACTALS,
    ),
    Theme(
        "useful", "Useful Bits",
        "Lines and commands you'll type for the rest of your career.",
        passages=USEFUL,
    ),
)

THEMES_BY_ID = {t.id: t for t in THEMES}
DEFAULT_THEME = THEMES[0]


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
        "random", "Random",
        "An ordinary mix from these keys — words, runs and lines, shuffled.",
    ),
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
        "blocks", "Whole Functions",
        "A whole solution at a time — Enter for the next line, indentation and all.",
    ),
    Mode(
        "chain", "Word Chain",
        "A word and its meaning, then one close to it, and on down the trail.",
    ),
    Mode(
        "define", "Guess the Word",
        "A definition and a row of blanks: work out the word, then type it.",
        hidden=True,
        by_name=True,
    ),
)

MODES_BY_ID = {m.id: m for m in MODES}


# Characters that turn up in written English but are on no keyboard, and what
# to type instead. Prose is written with em dashes and curly quotes without
# anyone thinking about it, and a target containing one cannot be completed.
UNTYPEABLE = {
    "—": "-",  # em dash
    "–": "-",  # en dash
    "‘": "'",  # left single quote
    "’": "'",  # right single quote / apostrophe
    "“": '"',  # left double quote
    "”": '"',  # right double quote
    "…": "...",  # ellipsis
    " ": " ",  # non-breaking space
    "­": "",  # soft hyphen
}


def typeable(text: str) -> str:
    """Swap characters that aren't on the keyboard for ones that are."""
    for wrong, right in UNTYPEABLE.items():
        if wrong in text:
            text = text.replace(wrong, right)
    return text


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

    def __post_init__(self) -> None:
        # Normalised here rather than at each of the dozen places a Target is
        # made, because the one that gets forgotten is the one that ships an
        # em dash to somebody trying to find it on their keyboard.
        object.__setattr__(self, "text", typeable(self.text))
        object.__setattr__(self, "prompt", typeable(self.prompt))


@dataclass
class TypingDrill:
    id: str
    section: str
    mode: str
    theme: str
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
    theme_id: str = "mixed",
    seed: str = "typing",
    count: int = 30,
) -> TypingDrill:
    section = SECTIONS_BY_ID.get(section_id) or SECTIONS[0]
    mode = MODES_BY_ID.get(mode_id) or MODES[0]
    theme = THEMES_BY_ID.get(theme_id) or DEFAULT_THEME
    # A theme with nothing usable for this mode would give an empty drill, so
    # fall back rather than hand back a blank screen.
    if not _theme_fits(theme, mode):
        theme = _fallback_theme(mode)
    rng = _rng(f"{section.id}:{mode.id}:{theme.id}:{seed}")
    targets: list[Target] = []
    scoring = "reaction"

    if mode.id == "random":
        # The plain default: a shuffle of everything this section can offer,
        # so it reads like ordinary typing practice rather than an exercise in
        # one narrow thing. Nothing is hidden and nothing is a game.
        targets = _random_mix(section, theme, rng, count)
        scoring = "wpm"

    elif mode.id in ("whack", "recall"):
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
        available = _speed_passages(section, theme, rng)
        long_enough = [p for p in available if len(p.text) >= 18]
        if not long_enough and available:
            # A section whose material is all short tokens gets them strung
            # together instead. Borrowing code snippets here asked a
            # punctuation-only section for letters.
            # Grouped so every line is worth restarting for. Grouping by a
            # fixed size left a trailing line of one short token, and simply
            # dropping that left sections with nothing at all.
            joined: list[Passage] = []
            batch: list[str] = []
            for item in available:
                batch.append(item.text)
                if len(" ".join(batch)) >= 18:
                    joined.append(Passage(" ".join(batch), "tokens"))
                    batch = []
            if batch and joined:
                # Fold the remainder into the last line rather than losing it.
                last = joined[-1]
                joined[-1] = Passage(f"{last.text} {' '.join(batch)}", last.source)
            long_enough = joined
        for passage in long_enough[:4]:
            targets.append(
                Target(text=passage.text, prompt=passage.text, note=passage.source)
            )
        scoring = "wpm"

    elif mode.id == "words":
        # _mode_fits keeps this mode off sections that can't spell anything,
        # so the pool is non-empty; the guard is here because an empty draw
        # raises rather than returning nothing.
        pool = _words_for(section, theme) or english.COMMON_WORDS
        for word in _no_repeats(rng, pool, max(6, count // 3)):
            targets.append(
                Target(text=word, prompt=word, note=_meaning(theme, word))
            )
        scoring = "wpm"

    elif mode.id == "chain":
        # The rabbit hole you fall into with a thesaurus open on the desk:
        # each word links to the last by meaning, and the note says which.
        previous = ""
        for entry in thesaurus.walk(rng, max(8, count // 2)):
            line = _chain_line(entry, section)
            note = f"from {previous}" if previous else "starting here"
            targets.append(Target(text=line, prompt=line, note=note))
            previous = entry.word
        scoring = "wpm"

    elif mode.id == "define":
        # The definition is the prompt; the word is the answer — so only words
        # that actually have one can be asked about.
        defined = tuple(
            w for w in _words_for(section, theme) if _meaning(theme, w)
        ) or tuple(w for w in theme.words if _meaning(theme, w))
        for word in _no_repeats(rng, defined, max(6, count // 3)):
            targets.append(
                Target(text=word, prompt=_meaning(theme, word), note=word)
            )
        scoring = "wpm"

    elif mode.id == "blocks":
        # Few, because each one is a whole function. Four ten-line solutions
        # is already a longer run than any other mode here.
        key = f"{section.id}:{theme.id}:blocks"
        pool = theme.blocks or _fallback_theme(mode).blocks
        for passage in _deal(key, pool, rng, 3):
            targets.append(
                Target(text=passage.text, prompt=passage.text, note=passage.source)
            )
        scoring = "wpm"

    else:  # speed
        for passage in _speed_passages(section, theme, rng):
            targets.append(
                Target(text=passage.text, prompt=passage.text, note=passage.source)
            )
        scoring = "wpm"

    suffix = "" if theme.id == "mixed" else f"-{theme.id}"
    named = "" if theme.id == "mixed" else f" · {theme.name}"
    return TypingDrill(
        id=f"typing-{section.id}-{mode.id}{suffix}",
        section=section.id,
        mode=mode.id,
        theme=theme.id,
        name=f"{section.name} · {mode.name}{named}",
        description=mode.description,
        targets=targets,
        hidden=mode.hidden,
        scoring=scoring,
    )


def _random_mix(
    section: Section, theme: Theme, rng: random.Random, count: int
) -> list[Target]:
    """Ordinary typing: a run of full lines, drawn at random.

    Random means the *text* is unpredictable, not the format. Cycling between
    single words, two-key pairs and whole sentences within one run turns a
    plain drill into a tour of the other modes, and each switch costs you the
    rhythm you'd just settled into.

    So every target here is a line. Which lines depends on what the section
    and theme can supply, and the fallbacks in `_speed_passages` already know
    how to build one out of nothing but a row of keys.
    """
    wanted = max(6, count // 3)

    # Exactly what the run needs, in one draw. Over-drawing and trimming used
    # to mark three times as much material as served, which burned through the
    # pool and brought the reshuffle round three times too soon.
    lines: list[Passage] = []
    seen: set[str] = set()
    for passage in _speed_passages(section, theme, rng, wanted=wanted):
        if passage.text not in seen:
            seen.add(passage.text)
            lines.append(passage)

    # Only if the real material ran out. A line of shuffled words reads as
    # filler next to actual prose, so it's a last resort rather than variety.
    words = _words_for(section, theme)
    if len(lines) < wanted and words:
        while len(lines) < wanted:
            picked = _no_repeats(rng, words, rng.randint(6, 10))
            line = " ".join(picked)
            if line in seen:
                continue
            seen.add(line)
            lines.append(Passage(line, "from these keys"))

    rng.shuffle(lines)
    return [
        Target(text=p.text, prompt=p.text, note=p.source) for p in lines[:wanted]
    ]


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


def _meaning(theme: Theme, word: str) -> str:
    """A theme's own definitions win; the shared vocabulary is the fallback."""
    return theme.meanings.get(word) or meaning_for(word)


def _words_for(section: Section, theme: Theme) -> tuple[str, ...]:
    """Which word list to draw from.

    A theme's words are the whole point of picking it, but they only work if
    the section can type them — Home Row can't spell "idempotent". When it
    can't, the section's own list stands in rather than serving words with
    keys you haven't been taught yet.
    """
    allowed = set(section.chars)
    if theme.words:
        usable = tuple(w for w in theme.words if set(w.lower()) <= allowed)
        if len(usable) >= 6:
            return usable
    if section.words:
        return section.words
    # The Mixed theme has no list of its own, and neither does All Letters —
    # ordinary English is what "mixed" means. Empty when nothing fits, which
    # is the honest answer for the number row: falling back to the full word
    # list served "point" and "great" to a section made of digits.
    return english.words_typeable_from(section.chars)


def _theme_fits(theme: Theme, mode: Mode) -> bool:
    """Whether a theme has anything to offer this mode."""
    if mode.id == "define":
        # Prompting with a definition needs definitions. Ordinary English
        # words don't carry them, so "mixed" can't drive this mode.
        return any(_meaning(theme, word) for word in theme.words)
    if mode.id == "words":
        return bool(theme.words)
    if mode.id == "blocks":
        # Only the code themes have whole functions to give. Prose has
        # paragraphs, which is a different idea and not this one.
        return bool(theme.blocks)
    return True


def _fallback_theme(mode: Mode) -> Theme:
    """What to use when the chosen theme can't drive the chosen mode."""
    if mode.id == "define":
        return THEMES_BY_ID["vocab"]
    if mode.id == "blocks":
        return THEMES_BY_ID["pycode"]
    return DEFAULT_THEME


# What each pool has already handed out this deal, keyed by section + theme.
#
# Every request seeds a fresh RNG and samples the pool from scratch, so a line
# could come round three times in a dozen drills while most of the material
# was never served at all. Remembering the deal turns that into what it should
# be: the pool is worked through, and only reshuffled once it runs out.
_dealt: dict[str, set[str]] = {}


def _deal(
    key: str, pool: tuple[Passage, ...], rng: random.Random, wanted: int
) -> list[Passage]:
    """`wanted` passages, preferring ones this deal hasn't served yet."""
    served = _dealt.setdefault(key, set())
    fresh = [p for p in pool if p.text not in served]
    if len(fresh) < wanted:
        # Worked through the pool — start a new deal rather than repeat inside
        # this one. Whatever is left over goes out first so the last few lines
        # of a pool aren't skipped by the reshuffle.
        rest = fresh
        served.clear()
        seen = {p.text for p in rest}
        fresh = rest + [p for p in pool if p.text not in seen]
    picks = list(rng.sample(fresh, k=min(wanted, len(fresh))))
    served.update(p.text for p in picks)
    return picks


def reset_deals() -> None:
    """Forget what's been served. Tests need a clean pool to measure against."""
    _dealt.clear()


def _speed_passages(
    section: Section, theme: Theme, rng: random.Random, wanted: int = 6
) -> list[Passage]:
    key = f"{section.id}:{theme.id}"
    # A theme that brought its own text uses it — that text is the point of
    # having chosen it.
    if theme.passages:
        return _deal(key, theme.passages, rng, wanted)
    if section.passages:
        return _deal(key, section.passages, rng, wanted)
    if section.id in ("symbols", "coding"):
        # Tokens rather than whole code lines: these sections are punctuation
        # only, and `print(f"{name}")` would be asking for letters they don't
        # teach. Whole lines of code live in Everything with a code theme.
        # `\n`, `0x` and `$_` are filtered out for the same reason.
        allowed = set(section.chars)
        usable = [t for t in (*CODE_TOKENS, *english.CODE_PAIRS) if set(t) <= allowed]
        # Several tokens to a line. On their own they're two keystrokes each,
        # which is a key-pair drill wearing a line drill's name.
        return [
            Passage(" ".join(rng.sample(usable, k=min(6, len(usable)))), "tokens")
            for _ in range(6)
        ]
    if section.id == "numbers":
        # Numbers used to borrow the code tokens, which meant a digits drill
        # asked for `>=`. Generate digit strings instead — several to a line,
        # in the widths numbers actually come in, so a line here is the same
        # shape of thing as a line anywhere else.
        def _number(width: int) -> str:
            return "".join(rng.choice(DIGITS) for _ in range(width))

        return [
            Passage(
                " ".join(_number(rng.choice((2, 3, 4, 4, 5, 6))) for _ in range(5)),
                "numbers",
            )
            for _ in range(6)
        ]
    # The default material: passages about typing and about getting better at
    # things. Twenty minutes of this is twenty minutes of reading something
    # worth reading, where a pangram is twenty minutes of "quick brown fox".
    allowed = set(section.chars) | {" "}
    worthwhile = tuple(p for p in DEFAULT_LINES if set(p.text.lower()) <= allowed)
    if len(worthwhile) >= 4:
        return _deal(key, worthwhile, rng, wanted)

    # Pangrams need the whole alphabet by definition, so a row section can't
    # type one — Home Row was being handed "crazy Fredrick bought many very
    # exquisite opal jewels".
    usable = [s for s in SENTENCES if set(s.lower()) <= allowed]
    if usable:
        picks = rng.sample(usable, k=min(4, len(usable)))
        return [Passage(s, "pangram") for s in picks]

    # Lines made from the section's own words instead. Not English, but every
    # word is real and every key is one you've been taught.
    if section.words:
        lines = []
        for _ in range(4):
            words = _no_repeats(rng, section.words, 6)
            lines.append(Passage(" ".join(words), "from these keys"))
        return lines

    # Bottom Row has neither words nor sentences — z x c v b n m has no
    # vowels — so its lines are runs of its own keys, in groups.
    return [
        Passage(
            " ".join(
                "".join(_no_repeats(rng, section.chars, 4)) for _ in range(5)
            ),
            "from these keys",
        )
        for _ in range(4)
    ]


def _themes_typeable_in(section: Section) -> bool:
    """Whether any theme's words can be typed from this section's keys."""
    allowed = set(section.chars)
    for theme in THEMES:
        usable = [w for w in theme.words if set(w.lower()) <= allowed]
        if len(usable) >= 6:
            return True
    return False


def _mode_fits(mode: Mode, section: Section) -> bool:
    """Whether a mode makes sense for a section.

    Offering one that doesn't produces a drill that technically runs and
    teaches nothing — 'words' made of consonants, or being asked to recall
    where the letter K is by being told "k".
    """
    # Words and definitions can come from the section or from a theme, so a
    # section with no list of its own still offers them when a theme can fill
    # in — Bottom Row can't, because z x c v b n m has no vowels.
    if mode.id in ("words", "define"):
        if not section.words and not _themes_typeable_in(section):
            return False
    if mode.id == "define" and section.words:
        if not _meaning(DEFAULT_THEME, section.words[0]):
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
    # The word chain is definitions in English, so it needs the alphabet and
    # the punctuation those definitions are written with.
    if mode.id == "chain" and not _can_type_chain(section):
        return False
    # Whole solutions are real source: letters, digits and the punctuation the
    # language is written with. A row section has none of that, and offering
    # the mode there would serve a function it cannot type a line of.
    if mode.id == "blocks" and not _can_type_code(section):
        return False
    return True


def _can_type_code(section: Section) -> bool:
    """Enough of a keyboard for real source to be typed at all."""
    needed = set("abcdefghijklmnopqrstuvwxyz0123456789()[]{}=<>+-*/.,:;_\"'")
    return needed <= set(section.chars)


def _can_type_chain(section: Section) -> bool:
    """A chain is English definitions, so it needs the alphabet — and only
    the alphabet, because the punctuation is dropped where a section hasn't
    taught it."""
    return set("abcdefghijklmnopqrstuvwxyz") <= set(section.chars)


def _chain_line(entry: thesaurus.Entry, section: Section) -> str:
    """One rung of the chain, in characters this section actually teaches.

    All Letters can't type a hyphen or a comma, and refusing to offer the mode
    there would hide it on seven sections out of nine. So the punctuation goes
    where it can and the line reads as a sentence where it can't.
    """
    allowed = set(section.chars) | {" "}
    meaning = "".join(c for c in entry.meaning if c in allowed)
    meaning = re.sub(r"\s+", " ", meaning).strip()
    joiner = " - " if "-" in allowed else " is "
    return f"{entry.word}{joiner}{meaning}"


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


def theme_catalog() -> list[dict]:
    """Themes, and which modes each one can actually supply."""
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            # A theme with no word list can't drive Words or Meaning to Word,
            # so the picker can grey it out rather than serve a fallback the
            # reader didn't ask for.
            "has_words": bool(t.words),
            "has_passages": bool(t.passages),
            # Only the code themes have whole functions, so the picker can
            # offer exactly those rather than silently falling back.
            "has_blocks": bool(t.blocks),
        }
        for t in THEMES
    ]
