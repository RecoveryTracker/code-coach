"""The one drill item, shared by the templates of every language (JavaScript, Python, Dart, C, SQL, TypeScript, Rust)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

#: Every language an activity can be played in, in the order the package lists them (`brain.LANGUAGES`).
LANGUAGES = ("python", "javascript", "dart", "c", "sql", "typescript", "rust")
#: Which fields of an Activity carry a language's generator and wording: (make, question, blurb). JavaScript is the
#: base (`make`, `question`, `blurb`); the rest hold a generator only when the activity is played in that language.
FIELDS = {
    "python": ("make_py", "question_py", "blurb_py"),
    "dart": ("make_dart", "question_dart", "blurb_dart"),
    "c": ("make_c", "question_c", "blurb_c"),
    "sql": ("make_sql", "question_sql", "blurb_sql"),
    "typescript": ("make_ts", "question_ts", "blurb_ts"),
    "rust": ("make_rs", "question_rs", "blurb_rs"),
}


@dataclass(frozen=True)
class Item:
    #: The code shown (for Variable Recall, the question).
    prompt: str
    #: The right answer, as typed - or one of the activity's two choices.
    answer: str
    #: Why, for the review after the round.
    explain: str = ""
    #: Variable Recall: what to remember, shown first and then hidden.
    show: str = ""
    #: The code an oracle test runs, in the item's own language, to check
    #: `answer` (empty: the prompt itself is what gets run).
    check: str = ""


@dataclass(frozen=True)
class Activity:
    id: str
    title: str
    blurb: str
    #: The question every item asks.
    question: str
    count: int
    #: "type" (type the answer) or "pick" (one of two keys).
    kind: str
    #: Seconds per item at the sharpest (age 20) and at the slowest (age 80).
    par: float
    slow: float
    #: The JavaScript generator. None for an activity that is not played in JavaScript (a Dart-only one).
    make: Callable[[random.Random], Item] | None = None
    #: For "pick": the two answers, left key first.
    choices: tuple[str, str] = ("", "")
    #: Variable Recall shows something first, for this many seconds.
    show_seconds: float = 0.0
    #: The Python version: its generator, and its wording where it differs.
    make_py: Callable[[random.Random], Item] | None = None
    question_py: str = ""
    blurb_py: str = ""
    #: The Dart version: its generator (None: the activity is not played in Dart), and its wording where it differs.
    make_dart: Callable[[random.Random], Item] | None = None
    question_dart: str = ""
    blurb_dart: str = ""
    #: The heading it sits under on the home screen (see GROUPS in the package).
    group: str = ""
    #: The C version and the SQL version: its generator (None: the activity is not played in that language), and its
    #: wording where it differs. (A language is playable exactly when it has a generator: `languages`.)
    make_c: Callable[[random.Random], Item] | None = None
    question_c: str = ""
    blurb_c: str = ""
    make_sql: Callable[[random.Random], Item] | None = None
    question_sql: str = ""
    blurb_sql: str = ""
    #: The TypeScript version and the Rust version (tests/ts_oracle.py, tests/rust_oracle.py): like C, the program
    #: prints its own answer (console.log / println!) and the answer is its output with the ends trimmed.
    make_ts: Callable[[random.Random], Item] | None = None
    question_ts: str = ""
    blurb_ts: str = ""
    make_rs: Callable[[random.Random], Item] | None = None
    question_rs: str = ""
    blurb_rs: str = ""
    #: Glossary term ids (plain lowercase words) this activity drills; the glossary maps them back to the
    #: activity, so this is the one place the mapping lives.
    concepts: tuple[str, ...] = ()
    #: How the generic oracle test checks an item against the real runtime: "value" runs `item.check`
    #: (or the prompt when it has none), takes the value of its last line and compares its printed form with
    #: the answer; "" means the activity has a test of its own (the original seven). A Dart-only activity says
    #: how the real `dart`'s printed lines become the value (tests/dart_oracle.py): "value" (the lines, one line is
    #: the answer), "lines" (the lines glued together: Async Order's letters) or "error" (a pick between "fine" and
    #: "error": did the snippet fail to compile or throw). C and SQL activities say "value" (tests/c_oracle.py and
    #: tests/sql_oracle.py).
    oracle: str = ""

    def generator(self, language: str) -> Callable[[random.Random], Item] | None:
        """The generator of one language (None when the activity is not played in it)."""
        if language == "javascript":
            return self.make
        return getattr(self, FIELDS[language][0]) if language in FIELDS else None

    @property
    def languages(self) -> tuple[str, ...]:
        """The languages this activity is played in, in the order of `brain.LANGUAGES` (an activity is playable in a
        language exactly when it has that language's generator)."""
        return tuple(lang for lang in LANGUAGES if self.generator(lang) is not None)
