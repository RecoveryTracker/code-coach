"""Read the error, find the line, say what it means.

The thing that stops a beginner is almost never the concept. It is
sitting in front of eleven lines of red text that turn out to say one
short sentence, and not knowing that they say a sentence at all.

    TypeError: Cannot read properties of undefined (reading 'name')

That message names the exact fault: the thing immediately before
`.name` was undefined. Not the array, not the function, not the server
— that one value, on that one line. A person who can read it fixes
their own bug in a minute. A person who cannot pastes it into a search
box and hopes, and stays a beginner at it for years, because nothing
ever teaches this on purpose. It is assumed.

So each of these is a short program that crashes, shown with the
message it produced, and two questions: which line caused it, and what
does it actually say. The second one is the exercise — the first is
just how you prove you followed the message back.

Where the answers come from
---------------------------
The engine. Node reports the message and the line number itself, so
both halves of the answer are facts rather than opinions: the suite
runs every one of these and holds the recorded message and line to
what actually came back. A crash that stops crashing, or that starts
failing on a different line, fails the suite rather than quietly
marking people wrong.

The plain-words reading is the one part a person writes, and the wrong
options are the misreadings people actually make — "the array was
empty" for a message that never mentions the array, "the function does
not exist" for one about the value it returned.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Crash:
    """A program that fails, and what its message is telling you."""

    id: str
    name: str
    family: str
    #: The program. Short enough that the line numbers stay in your head.
    code: str
    #: The error line exactly as the engine prints it, without the stack
    #: frames under it. Typed out by a person; the suite holds it to
    #: what the engine really says.
    message: str
    #: Which line, 1-based, the engine blames. Also held to the engine.
    line: int
    #: What the message means, in words. The answer to the real question.
    meaning: str
    #: Misreadings people actually make. Sorted in with the answer, so
    #: the order gives nothing away.
    decoys: tuple[str, ...]
    #: What to do about it, shown once answered. A message you can read
    #: and not act on is half a lesson.
    fix: str
    language: str = "javascript"
    #: 1 to 5, easiest first within a family.
    level: int = 2

    @property
    def numbered(self) -> tuple[tuple[int, str], ...]:
        """The program with line numbers, which is how it is shown and
        how the line question is answered."""
        return tuple(
            (i + 1, text) for i, text in enumerate(self.code.split("\n"))
        )

    @property
    def choices(self) -> tuple[str, ...]:
        """Every reading on offer, in an order that says nothing."""
        return tuple(sorted({self.meaning, *self.decoys}))


def _c(**kw) -> Crash:
    return Crash(**kw)


def engine_report(code: str, language: str = "javascript") -> tuple[str, int]:
    """What the engine says went wrong, and where.

    Used by the suite to check every crash against reality, and kept
    here rather than in the test so that the parsing the suite trusts
    is the parsing the module documents.

    Returns the message line and the 1-based line number, or ("", 0) if
    the program did not actually fail.
    """
    from code_coach.engine import run_code

    out, err, exit_code = run_code(code, language=language)
    if exit_code == 0:
        return "", 0

    message, line = "", 0
    previous = ""
    for raw in err.splitlines():
        text = raw.strip()
        if not text:
            continue
        # Dart prints "Unhandled exception:" on a line of its own and the
        # message on the next, and its messages need not say Error at all.
        if not message and previous == "Unhandled exception:":
            message = text
        previous = text
        # Node prints the offending file and line before the message,
        # then the message, then its own stack frames. Python prints the
        # frames first and the message last. Taking the first line that
        # names an error and is not a stack frame works for both.
        if not message and "Error" in text and not text.startswith("at "):
            message = text
        # Dart's first frames can be the SDK's own - (dart:collection/...)
        # - which are not a line of the program.
        if not line and "(dart:" not in text:
            for suffix in (".js:", ".py\", line ", ".py:", ".dart:"):
                if suffix in text:
                    after = text.split(suffix, 1)[1]
                    digits = ""
                    for ch in after:
                        if ch.isdigit():
                            digits += ch
                        else:
                            break
                    if digits:
                        line = int(digits)
                    break
    return message, line


def crashes(family: str | None = None) -> tuple[Crash, ...]:
    """Every one, or one family's, easiest first within the family."""
    from code_coach.errors.content import MISSING, NAMES, WRONG_KIND
    from code_coach.engine import if_dart
    from code_coach.errors.content_dart import DART_CRASHES

    everything = (*MISSING, *NAMES, *WRONG_KIND, *if_dart(DART_CRASHES))
    if family is not None:
        everything = tuple(c for c in everything if c.family == family)
    return tuple(sorted(everything, key=lambda c: c.level))


def crash_families() -> tuple[str, ...]:
    from code_coach.errors.content import MISSING, NAMES, WRONG_KIND
    from code_coach.engine import if_dart
    from code_coach.errors.content_dart import DART_CRASHES

    seen: list[str] = []
    for c in (*MISSING, *NAMES, *WRONG_KIND, *if_dart(DART_CRASHES)):
        if c.family not in seen:
            seen.append(c.family)
    return tuple(seen)


def crash(crash_id: str) -> Crash | None:
    return next((c for c in crashes() if c.id == crash_id), None)
