"""Which languages Code Coach can teach.

Scaffolding. Python is the only one that actually works today; the registry
exists so adding another is a matter of filling in the pieces listed on each
entry rather than hunting for every place the language is assumed.

What a language needs before `available` can flip to True:

  runner      execute a file and capture stdout/stderr (engine.run_file)
  checks      structural checks for build lessons — Python uses its `ast`
              module, so another language needs its own parser or a
              text-based fallback
  bank        the solutions themselves, per pattern
  tracer      step-by-step values for "Watch it run" (optional; the rest of
              the app works without it)

The verbatim type-along and the diff messages are language-agnostic — they
compare text and indentation, so they come for free.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Language:
    id: str
    name: str
    # Monaco's identifier for syntax highlighting.
    monaco: str
    extension: str
    # False until the pieces below actually exist.
    available: bool = False
    # What's still missing, shown in the picker so it isn't a mystery.
    note: str = ""
    # Which pieces are done — keeps the UI honest as work lands, and the
    # suite checks each claim rather than taking it on trust.
    #
    #   reference     has a cheat sheet
    #   fundamentals  has a taught course
    #   workbook      has workbook pages
    #   typing        has its own typing material
    #   runner        can execute what you write
    #   checks bank tracer explainer   the rest, as they land
    #
    # The nine added most recently claim workbook and typing and not
    # fundamentals, because that is what is true of them: they were added
    # for the drill screens rather than for the taught course, and saying
    # fundamentals here made the suite demand a course that does not exist.
    ready: tuple[str, ...] = field(default_factory=tuple)


LANGUAGES: tuple[Language, ...] = (
    Language(
        id="python",
        name="Python",
        monaco="python",
        extension="py",
        available=True,
        ready=("reference", "workbook", "typing", "fundamentals", "runner", "checks", "bank", "tracer", "explainer"),
    ),
    Language(
        id="dart",
        name="Dart (Flutter)",
        monaco="dart",
        extension="dart",
        available=True,
        note=(
            "Run and code tracing both need the Dart SDK on your PATH. "
            "Tracing starts two Dart VMs, so it takes a couple of seconds."
        ),
        ready=("reference", "workbook", "typing", "fundamentals", "runner", "checks", "bank", "tracer"),
    ),
    Language(
        id="javascript",
        name="JavaScript",
        monaco="javascript",
        extension="js",
        available=True,
        note=(
            "Run and code tracing both need Node on your PATH. Everything "
            "else works offline."
        ),
        ready=("reference", "workbook", "typing", "fundamentals", "runner", "checks", "bank", "tracer", "explainer"),
    ),
    Language(
        id="typescript",
        name="TypeScript",
        monaco="typescript",
        extension="ts",
        available=True,
        note=(
            "Run type-checks with tsc before executing, so a type error stops "
            "it. Watch it run is Python-only for now."
        ),
        ready=("reference", "workbook", "typing", "fundamentals", "runner", "checks", "bank"),
    ),
    Language(
        id="sql",
        name="SQL",
        monaco="sql",
        extension="sql",
        available=True,
        note=(
            "Fundamentals only. Run executes your query against a small "
            "sample database — users and orders — and prints the rows."
        ),
        ready=("reference", "workbook", "typing", "fundamentals", "runner"),
    ),
    Language(
        id="postgresql",
        name="PostgreSQL",
        monaco="pgsql",
        extension="sql",
        available=True,
        note=(
            "Run executes against a real PostgreSQL 17 on this machine, "
            "so RETURNING, ILIKE, ::casts, arrays and JSONB all work. "
            "Every go runs in a transaction that is rolled back, so a "
            "stray UPDATE shows you exactly what it did and then undoes "
            "it. Needs the local server — see tools/get_postgres.py."
        ),
        ready=("runner",),
    ),
    Language(
        id="c",
        name="C",
        monaco="c",
        extension="c",
        available=True,
        note=(
            "Fundamentals only. Run needs gcc or clang on your PATH; without "
            "one the drills still work, only Run won't."
        ),
        ready=("reference", "workbook", "typing", "fundamentals", "runner", "checks"),
    ),
    Language(
        id="cpp",
        name="C++",
        monaco="cpp",
        extension="cpp",
        available=True,
        note=(
            "Fundamentals only. Run needs g++ or clang++ on your PATH; "
            "without one the drills still work, only Run won't."
        ),
        ready=("reference", "workbook", "typing", "fundamentals", "runner", "checks"),
    ),
    Language(
        id="rust",
        name="Rust",
        monaco="rust",
        extension="rs",
        available=True,
        note=(
            "Fundamentals only. Run needs rustc on your PATH; without it the "
            "drills still work, only Run won't."
        ),
        ready=("reference", "workbook", "typing", "fundamentals", "runner", "checks"),
    ),
    Language(
        id="go",
        name="Go",
        monaco="go",
        extension="go",
        available=True,
        note=(
            "Workbook and typing only. The toolchain lives in ~/toolchains rather than on PATH, and go run builds on every exercise."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="php",
        name="PHP",
        monaco="php",
        extension="php",
        available=True,
        note=(
            "Workbook and typing only. Fast to run, so a whole page comes back in a couple of seconds."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="lua",
        name="Lua",
        monaco="lua",
        extension="lua",
        available=True,
        note=(
            "Workbook and typing only. The quickest of the lot: a page of twenty runs in under a second."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="ruby",
        name="Ruby",
        monaco="ruby",
        extension="rb",
        available=True,
        note=(
            "Workbook and typing only."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="zig",
        name="Zig",
        monaco="zig",
        extension="zig",
        available=True,
        note=(
            "Workbook and typing only. Every run rebuilds against the standard library, so a page takes about a minute."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="java",
        name="Java",
        monaco="java",
        extension="java",
        available=True,
        note=(
            "Workbook and typing only. Runs the source file directly, no separate compile step."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="csharp",
        name="C#",
        monaco="csharp",
        extension="cs",
        available=True,
        note=(
            "Workbook and typing only. The very first run after an update initialises the SDK and takes minutes; every run after is instant."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="kotlin",
        name="Kotlin",
        monaco="kotlin",
        extension="kt",
        available=True,
        note=(
            "Workbook and typing only, on the JDK that Java and Lisp "
            "already use. Run takes about five seconds, nearly all of it "
            "starting a JVM for the compiler."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="swift",
        name="Swift",
        monaco="swift",
        extension="swift",
        available=True,
        note=(
            "Workbook and typing only. Swift ships an installer rather "
            "than an archive, so it lives in Programs\\Swift rather than "
            "~/toolchains, and each exercise is compiled — `swift "
            "file.swift` on Windows uses a JIT that cannot resolve the "
            "standard library's array symbols."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="lisp",
        name="Common Lisp",
        monaco="lisp",
        extension="lisp",
        available=True,
        note=(
            "Workbook and typing only, running on ABCL, which is a Common "
            "Lisp on the JVM. SBCL would have been the obvious choice and "
            "ships only through SourceForge, which refused the download."
        ),
        ready=("workbook", "typing", "runner"),
    ),
    Language(
        id="odin",
        name="Odin",
        monaco="odin",
        extension="odin",
        available=True,
        note=(
            "Workbook and typing only."
        ),
        ready=("workbook", "typing", "runner"),
    ),
)

DEFAULT_LANGUAGE = "python"


def get_language(language_id: str | None) -> Language:
    """The named language, falling back to Python rather than failing —
    a stored id from a future version shouldn't brick the app."""
    for lang in LANGUAGES:
        if lang.id == language_id:
            return lang
    return LANGUAGES[0]


def is_available(language_id: str | None) -> bool:
    return get_language(language_id).available


def languages_payload() -> list[dict]:
    return [
        {
            "id": lang.id,
            "name": lang.name,
            "monaco": lang.monaco,
            "extension": lang.extension,
            "available": lang.available,
            "note": lang.note,
            "ready": list(lang.ready),
        }
        for lang in LANGUAGES
    ]
