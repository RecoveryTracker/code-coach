"""Gotchas, C: the built-in cards held to real compilers, and everything else C changes about the mode.

The oracle rule, strictly: the answer written in code_coach/gotchas/content_c.py is never trusted. Every card is
compiled and run here with this file's own subprocess calls (not the app's runner) and what it prints must be
exactly the marked answer. And because a C answer must be the same on every machine, each card is built many
ways - every compiler installed (clang, gcc, Visual Studio), at -O0 and -O2, with plain `char` forced signed and
forced unsigned, and once more with the undefined-behaviour (and, where it runs, address) sanitizers that abort
on the first undefined thing - and all of them must print the same thing, with nothing on stderr.

Compiler warnings are checked too: a card may only trigger the harmless kinds in BENIGN_WARNINGS (a stray `;`
after an `if` is the trap itself); a warning about anything that smells of undefined behaviour fails the test.

Everything that needs a compiler is skipped, with the reason stated, on a machine without one.
"""

from __future__ import annotations

import functools
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import pytest

from code_coach import engine, gotchas
from code_coach.gotchas import DECKS

C_ITEMS = DECKS["c"]
CLANG = shutil.which("clang")
GCC = shutil.which("gcc")
VCVARS = engine._find_vcvars()  # only to find out whether Visual Studio is installed
HAVE_COMPILER = bool(CLANG or GCC or VCVARS)
LIMIT = 5.0

needs_compiler = pytest.mark.skipif(
    not HAVE_COMPILER,
    reason="no C compiler (clang, gcc or Visual Studio) is installed, so the C cards cannot be compiled here")

#: Warnings a card may trigger. Each is the very trap the card is about, or noise about style - none of them is
#: about undefined behaviour. Anything else (sequence points, uninitialised reads, bounds, format mismatches,
#: bad conversions, missing returns...) fails the test.
BENIGN_WARNINGS = {
    "parentheses",              # `if (x = 0)`, `f & 2 == 2`, `a & b | a ^ b`, chained comparisons
    "logical-op-parentheses", "bitwise-op-parentheses", "shift-op-parentheses",
    "dangling-else",            # the dangling-else card
    "empty-body",               # `for (...);` and `if (x > 5);`
    "misleading-indentation",   # ...which is also why the indentation lies
    "implicit-fallthrough",     # the switch fallthrough cards
    "sign-compare",             # signed-versus-unsigned comparison cards
    "tautological-compare", "tautological-constant-out-of-range-compare", "tautological-unsigned-zero-compare",
    "array-compare",            # `a == b` on two arrays
    "sizeof-array-argument",    # the array-parameter card
    "unused-value", "unused-variable", "unused-but-set-variable", "unused-parameter",
    "comma",                    # clang's note on the comma operator card
    "unused-but-set-parameter",
    "unevaluated-expression",   # sizeof(i++) never runs i++: that is the card
    "literal-range",            # a float compared with 0.1: that is the card
    "missing-field-initializers",  # `struct Q q = {1};`: that is the card
    "format-truncation",        # snprintf cutting its text: that is the card
    "type-limits",              # unsigned char == -1: that is the card (gcc's name for it)
    "address",                  # gcc's name for comparing two arrays
    "deprecated-declarations",  # Microsoft's "strcat/strtok may be unsafe" note
}
#: Never allowed, even if a future edit adds them to the list above.
NEVER_BENIGN = {"unsequenced", "sequence-point", "uninitialized", "sometimes-uninitialized", "maybe-uninitialized",
                "array-bounds", "format", "return-type", "int-conversion", "incompatible-pointer-types",
                "implicit-function-declaration", "strict-aliasing", "shift-count-overflow", "shift-negative-value",
                "integer-overflow", "division-by-zero", "return-stack-address", "dangling-pointer", "overflow"}

STRICT = ("-std=c11", "-Wall", "-Wextra", "-pedantic")


@dataclass(frozen=True)
class Variant:
    toolchain: str  # "clang" | "gcc" | "msvc"
    name: str
    flags: tuple[str, ...]
    path: str = ""  # extra folder for the program's PATH (the sanitizer runtime on Windows)

    @property
    def label(self) -> str:
        return f"{self.toolchain} {self.name}"


@dataclass(frozen=True)
class Built:
    returncode: int  # the program's; -1000 if it never built
    stdout: str
    stderr: str
    seconds: float
    build_log: str
    warnings: tuple[str, ...]
    #: The same program run a second time: (exit code, stdout). It must match the first run.
    rerun: tuple[int, str] = (0, "")


def _bare_env(extra_path: str = "") -> dict[str, str]:
    env = {k: os.environ[k] for k in ("SYSTEMROOT", "SystemRoot", "TEMP", "TMP") if k in os.environ}
    if extra_path:
        env["PATH"] = extra_path
    return env


def _run_exe(exe: Path, folder: Path, extra_path: str = "") -> tuple[int, str, str, float]:
    started = time.monotonic()
    done = subprocess.run([str(exe)], cwd=folder, env=_bare_env(extra_path), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=LIMIT * 3, stdin=subprocess.DEVNULL)
    return done.returncode, done.stdout.replace("\r\n", "\n"), done.stderr, time.monotonic() - started


def _sanitizer(cc: str) -> tuple[tuple[str, ...], str]:
    """The strongest sanitizer switches that build AND run a tiny program here, and the PATH folder they need."""
    folder = Path(tempfile.mkdtemp(prefix="gotcha_san_"))
    try:
        src = folder / "p.c"
        src.write_text('#include <stdio.h>\n#include <stdlib.h>\nint main(void) {\n'
                       '    int *a = malloc(4 * sizeof *a);\n    a[0] = 1;\n    printf("%d\\n", a[0]);\n'
                       '    free(a);\n}\n', encoding="utf-8")
        runtime = ""
        if os.name == "nt" and cc == "clang":
            found = subprocess.run([CLANG, "-print-runtime-dir"], capture_output=True, text=True)
            runtime = found.stdout.strip() if found.returncode == 0 else ""
        for kinds in ("address,undefined", "undefined"):
            flags = (f"-fsanitize={kinds}", "-fno-sanitize-recover=undefined", "-fno-omit-frame-pointer")
            exe = folder / "p.exe"
            exe.unlink(missing_ok=True)
            built = subprocess.run([shutil.which(cc), *STRICT, *flags, str(src), "-o", str(exe)], cwd=folder,
                                   capture_output=True, text=True, timeout=120)
            if built.returncode != 0 or not exe.exists():
                continue
            try:
                code, out, err, _ = _run_exe(exe, folder, runtime)
            except (OSError, subprocess.TimeoutExpired):
                continue
            if code == 0 and out.strip() == "1" and not err.strip():
                return flags, runtime
        return (), ""
    finally:
        shutil.rmtree(folder, ignore_errors=True)


@functools.cache
def variants() -> tuple[Variant, ...]:
    """Every way a card is built here. The first is the baseline the marked answers are held to."""
    out: list[Variant] = []
    for cc, found in (("clang", CLANG), ("gcc", GCC)):
        if not found:
            continue
        out += [Variant(cc, "O0 signed-char", (*STRICT, "-O0", "-fsigned-char")),
                Variant(cc, "O2", (*STRICT, "-O2")),
                Variant(cc, "O1 unsigned-char", (*STRICT, "-O1", "-funsigned-char"))]
        flags, runtime = _sanitizer(cc)
        if flags:
            out.append(Variant(cc, "sanitized", (*STRICT, "-O1", *flags), path=runtime))
    if VCVARS:
        out += [Variant("msvc", "Od", ("/Od",)), Variant("msvc", "O2 unsigned-char", ("/O2", "/J"))]
    return tuple(out)


_WARNING_FLAG = re.compile(r"warning:.*\[-W([\w=+-]+)\]")


def _gnu_one(variant: Variant, item) -> Built:
    folder = Path(tempfile.mkdtemp(prefix="gotcha_c_oracle_"))
    try:
        src, exe = folder / "card.c", folder / "card.exe"
        src.write_text(item.code + "\n", encoding="utf-8", newline="\n")
        cc = shutil.which(variant.toolchain)
        libm = [] if os.name == "nt" else ["-lm"]
        built = subprocess.run([cc, *variant.flags, str(src), "-o", str(exe), *libm], cwd=folder,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        log = (built.stderr + built.stdout).strip()
        warnings = tuple(_WARNING_FLAG.findall(log))
        if built.returncode != 0 or not exe.exists():
            return Built(-1000, "", "", 0.0, log, warnings)
        code, out, err, secs = _run_exe(exe, folder, variant.path)
        code2, out2, _, _ = _run_exe(exe, folder, variant.path)
        return Built(code, out, err, secs, log, warnings, (code2, out2))
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def _msvc_all(variant: Variant, items) -> list[Built]:
    """One cmd session for the whole deck: starting the Visual Studio tools takes seconds, compiling does not."""
    folder = Path(tempfile.mkdtemp(prefix="gotcha_c_msvc_"))
    try:
        lines = ["@echo off", f'call "{VCVARS}" >nul']
        for i, item in enumerate(items):
            (folder / f"{i}.c").write_text(item.code + "\n", encoding="utf-8", newline="\n")
            lines.append(f'cl /nologo /std:c11 /W3 {" ".join(variant.flags)} "{folder / f"{i}.c"}" '
                         f'/Fo"{folder / f"{i}.obj"}" /Fe"{folder / f"{i}.exe"}" > "{folder / f"{i}.log"}" 2>&1')
        bat = folder / "build.bat"
        bat.write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))
        subprocess.run(["cmd", "/c", str(bat)], cwd=folder, capture_output=True, timeout=900)

        def one(i: int) -> Built:
            log_path, exe = folder / f"{i}.log", folder / f"{i}.exe"
            log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
            if not exe.exists():
                return Built(-1000, "", "", 0.0, log, ())
            code, out, err, secs = _run_exe(exe, folder)
            code2, out2, _, _ = _run_exe(exe, folder)
            return Built(code, out, err, secs, log, (), (code2, out2))

        with ThreadPoolExecutor(4) as pool:
            return list(pool.map(one, range(len(items))))
    finally:
        shutil.rmtree(folder, ignore_errors=True)


@functools.cache
def builds(variant: Variant) -> dict[str, Built]:
    items = list(C_ITEMS)
    if variant.toolchain == "msvc":
        results = _msvc_all(variant, items)
    else:
        with ThreadPoolExecutor(4) as pool:
            results = list(pool.map(lambda it: _gnu_one(variant, it), items))
    return {it.id: res for it, res in zip(items, results)}


def baseline() -> Variant:
    return variants()[0]


def _norm(text: str) -> str:
    return " ".join(text.split())


# ── The deck itself (no compiler needed) ────────────────────────────────


def test_there_are_enough_c_cards():
    assert len(C_ITEMS) >= 70


def test_c_ids_are_unique_prefixed_and_in_the_c_deck_only():
    ids = [it.id for d in DECKS.values() for it in d]
    assert len(ids) == len(set(ids)), "an id is used by two cards across the decks"
    assert all(it.id.startswith("c-") and it.language == "c" for it in C_ITEMS)
    assert not any(it.mine for it in C_ITEMS)
    assert not any(it.raises for it in C_ITEMS), "a C card prints its answer; a crash is not portable"


def test_every_c_card_is_complete_with_three_distinct_wrong_options():
    for it in C_ITEMS:
        assert it.code.strip() and "#include" in it.code and "int main(void)" in it.code, it.id
        assert len(it.wrong) == 3, it.id
        assert it.trap.strip() and len(it.trap) <= 100, it.id
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", it.why.strip()) if s]
        assert 1 <= len(sentences) <= 4, f"{it.id}: the explanation is {len(sentences)} sentences"
        assert it.answer.strip() and all(w.strip() for w in it.wrong), it.id
        assert len({_norm(o) for o in it.options}) == 4, f"{it.id}: options collide ignoring whitespace"
        assert all("\n" not in o for o in it.options), it.id


def test_each_c_card_is_one_short_program():
    for it in C_ITEMS:
        lines = it.code.splitlines()
        assert len(lines) <= 16, f"{it.id} is {len(lines)} lines"
        assert max(len(line) for line in lines) <= 76, f"{it.id} has a very wide line"


def test_a_c_card_uses_nothing_that_differs_between_machines():
    banned = re.compile(
        r"%p|\brand\b|\bsrand\b|\btime\b|\bclock\b|\bgetenv\b|\bargv\b|\bargc\b|\bscanf\b|\bgets\b|\bfgets\b"
        r"|\bgetchar\b|\b__\w+|#pragma|\basm\b|\bsizeof\s*\(\s*(?:long|short|void)\b"
        r"|\bINT_MAX\b|\bINT_MIN\b|\bLONG_MAX\b|\bLONG_MIN\b|\bmalloc\b|\bgoto\b|\bsignal\b|\bsetjmp\b|\bFILE\b"
        r"|\bfopen\b|\bsystem\b|\bunion\b|\boffsetof\b|\bpthread|\bthread_local\b|\b_Thread|\bwchar|\blocale")
    for it in C_ITEMS:
        found = banned.search(it.code)
        assert not found, f"{it.id} uses {found.group(0)!r}, which can differ between machines"
        # Plain `char` has a machine-defined signedness: it may only hold values every machine agrees on.
        for m in re.finditer(r"(?<!unsigned )(?<!signed )\bchar\s+(\w+)\s*=\s*(\d+)\s*;", it.code):
            assert int(m.group(2)) < 128, f"{it.id}: char {m.group(1)} holds a value that is signed on some machines"


def test_the_c_answers_do_not_look_like_a_machine_dependent_number():
    # a pointer or address printed as a long hex number is the one thing never to be in an answer
    for it in C_ITEMS:
        assert not re.search(r"\b0x[0-9a-f]{8,}\b", it.answer, re.I), it.id


# ── The oracle ──────────────────────────────────────────────────────────


@needs_compiler
def test_every_c_card_builds_everywhere_and_prints_the_marked_answer():
    wrong = []
    for variant in variants():
        for it in C_ITEMS:
            b = builds(variant)[it.id]
            if b.returncode == -1000:
                wrong.append((variant.label, it.id, "did not compile", b.build_log[-300:]))
            elif b.returncode != 0 or b.stdout.strip() != it.answer:
                wrong.append((variant.label, it.id, it.answer, b.stdout.strip(), b.returncode, b.stderr[-200:]))
    assert wrong == []


@needs_compiler
def test_the_marked_answer_alone_on_the_baseline_build():
    # the same oracle, narrowed to one build, so a failure names a single compiler
    base = baseline()
    bad = [(it.id, it.answer, builds(base)[it.id].stdout.strip()) for it in C_ITEMS
           if builds(base)[it.id].stdout.strip() != it.answer]
    assert bad == []


@needs_compiler
def test_every_build_of_every_card_prints_the_same_bytes_and_nothing_on_stderr():
    base = baseline()
    differ = []
    for variant in variants()[1:]:
        for it in C_ITEMS:
            a, b = builds(base)[it.id], builds(variant)[it.id]
            if (a.stdout, a.returncode) != (b.stdout, b.returncode) or b.stderr.strip():
                differ.append((it.id, base.label, a.stdout.strip(), variant.label, b.stdout.strip(), b.stderr[-120:]))
    assert differ == []


@needs_compiler
def test_the_sanitizers_found_nothing_undefined():
    san = [v for v in variants() if v.name == "sanitized"]
    if not san:
        pytest.skip("this machine's compilers cannot build with the undefined-behaviour sanitizer")
    bad = []
    for variant in san:
        for it in C_ITEMS:
            b = builds(variant)[it.id]
            if b.returncode != 0 or "runtime error" in b.stderr or "ERROR: AddressSanitizer" in b.stderr:
                bad.append((variant.label, it.id, b.stderr[:300]))
    assert bad == []


@needs_compiler
def test_only_harmless_warnings_under_wall_wextra_pedantic():
    gnu = [v for v in variants() if v.toolchain != "msvc" and v.name == "O0 signed-char"]
    if not gnu:
        pytest.skip("warnings are checked with clang or gcc, and neither is installed")
    bad = []
    for variant in gnu:
        for it in C_ITEMS:
            for flag in builds(variant)[it.id].warnings:
                name = flag.split("=")[0]
                if name in NEVER_BENIGN or name not in BENIGN_WARNINGS:
                    bad.append((variant.label, it.id, flag))
    assert bad == []


@needs_compiler
def test_no_wrong_option_is_what_the_program_really_prints():
    for it in C_ITEMS:
        real = _norm(builds(baseline())[it.id].stdout)
        for wrong in it.wrong:
            assert _norm(wrong) != real, f"{it.id}: a 'wrong' option is the real output"


@needs_compiler
def test_every_c_card_prints_the_same_thing_every_run_and_is_quick():
    for variant in variants():
        for it in C_ITEMS:
            b = builds(variant)[it.id]
            assert (b.returncode, b.stdout) == b.rerun, f"{it.id} differs between two runs ({variant.label})"
            assert b.seconds < LIMIT, f"{it.id} took {b.seconds:.1f}s to run ({variant.label})"


@needs_compiler
def test_every_installed_compiler_really_took_part():
    # so the test cannot quietly compare fewer compilers than the machine has
    names = sorted({v.toolchain for v in variants()})
    expected = sorted({n for n, found in (("clang", CLANG), ("gcc", GCC), ("msvc", VCVARS)) if found})
    assert names == expected


# ── The app's runner for C ──────────────────────────────────────────────

SIX_TIMES_SEVEN = '#include <stdio.h>\nint main(void) {\n    printf("%d\\n", 6 * 7);\n}'


def real_c_output(code: str) -> str:
    """The oracle for a program of the user's: built and run with this file's own calls (the baseline build)."""
    from types import SimpleNamespace

    variant = baseline()
    item = SimpleNamespace(code=code)
    built = _msvc_all(variant, [item])[0] if variant.toolchain == "msvc" else _gnu_one(variant, item)
    assert built.returncode == 0, built.build_log or built.stderr
    return built.stdout.strip()


@pytest.fixture(params=[name for name, found in (("gcc", GCC), ("clang", CLANG), ("msvc", VCVARS)) if found] or [None])
def toolchain(request, monkeypatch):
    """Each installed toolchain in turn, forced as the one the app's runner picks."""
    if request.param is None:
        pytest.skip("no C compiler (clang, gcc or Visual Studio) is installed, so C cannot be run here")
    monkeypatch.setattr(engine, "c_toolchains", lambda: [request.param])
    return request.param


def test_the_runner_compiles_and_runs_a_program_on_each_installed_toolchain(toolchain):
    from code_coach.gotchas.runner import error_name, run_program

    got = run_program("c", SIX_TIMES_SEVEN)
    assert got.ok and got.stdout.strip() == "42" and got.returncode == 0, (toolchain, got)
    assert error_name("c", got) == ""
    assert got.stdout.strip() == real_c_output(SIX_TIMES_SEVEN)


def test_compiler_warnings_never_become_output(toolchain):
    from code_coach.gotchas.runner import run_program

    noisy = ('#include <stdio.h>\nint main(void) {\n    int unused = 3;\n    int x = 1;\n'
             '    if (x = 2) printf("two\\n");\n    printf("%d\\n", x);\n}')
    got = run_program("c", noisy)
    assert got.ok and got.stdout.split() == ["two", "2"] and got.stderr == "", (toolchain, got)


def test_a_compile_error_is_reported_as_one_with_the_first_error_and_no_temp_path(toolchain):
    from code_coach.gotchas.runner import error_name, last_error_line, run_program

    got = run_program("c", '#include <stdio.h>\nint main(void) {\n    printf("%d\\n", 5 / 2)\n    return 0;\n}')
    assert got.compile_error and not got.ok and got.stdout == ""
    assert error_name("c", got) == "CompileError"
    first = last_error_line(got)
    assert "error" in first.lower() and "gotcha_run_" not in first and "\n" not in first, (toolchain, first)
    assert "gotcha_run_" not in got.stderr
    assert "snippet.c" in got.stderr


def test_a_crash_or_a_bad_exit_is_reported_by_its_exit_code(toolchain):
    from code_coach.gotchas.runner import error_name, run_program

    exited = run_program("c", "int main(void) {\n    return 3;\n}")
    assert not exited.ok and not exited.compile_error and exited.returncode == 3
    assert error_name("c", exited) == "exit code 3"
    crashed = run_program("c", '#include <stdio.h>\nint main(void) {\n    int *p = 0;\n    printf("a\\n");\n'
                               '    return *p;\n}')
    assert not crashed.ok and not crashed.compile_error and crashed.returncode != 0
    assert error_name("c", crashed) == f"exit code {crashed.returncode}"


def test_a_c_program_that_runs_too_long_is_stopped(toolchain):
    from code_coach.gotchas.runner import error_name, run_program

    started = time.monotonic()
    got = run_program("c", "int main(void) {\n    for (;;) {}\n}", timeout=1.0)
    assert got.timed_out and not got.ok and error_name("c", got) == "timeout"
    assert time.monotonic() - started < 30, "the build has its own ceiling; the run itself stops at the timeout"
    assert got.seconds < 4, "the program's own clock does not include the build"


def test_the_program_gets_a_bare_environment_no_input_and_capped_output(toolchain, monkeypatch):
    from code_coach.gotchas.runner import MAX_OUTPUT, run_program

    monkeypatch.setenv("GOTCHA_C_SECRET", "hunter2")
    code = ('#include <stdio.h>\n#include <stdlib.h>\nint main(void) {\n'
            '    printf("%s %d\\n", getenv("GOTCHA_C_SECRET") ? "leak" : "clean", getchar() == EOF);\n}')
    got = run_program("c", code)
    assert got.stdout.strip() == "clean 1", got
    loud = run_program("c", '#include <stdio.h>\nint main(void) {\n    for (int i = 0; i < 200000; i++)\n'
                            '        putchar(\'x\');\n}')
    assert 0 < len(loud.stdout) <= MAX_OUTPUT


def test_the_builds_are_cleaned_up_and_nothing_is_left_in_the_temp_folder(toolchain):
    from code_coach.gotchas.runner import run_program

    temp = Path(tempfile.gettempdir())
    before = {p.name for p in temp.glob("gotcha_run_*")}
    run_program("c", SIX_TIMES_SEVEN)
    run_program("c", "int main(void) { oops }")
    run_program("c", "int main(void) {\n    for (;;) {}\n}", timeout=0.5)
    assert {p.name for p in temp.glob("gotcha_run_*")} == before


def test_a_pair_of_runs_builds_once(monkeypatch):
    if not HAVE_COMPILER:
        pytest.skip("no C compiler is installed")
    from code_coach.gotchas.runner import run_twice

    calls = []
    real = engine.compile_c

    def counting(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(engine, "compile_c", counting)
    first, second = run_twice("c", SIX_TIMES_SEVEN)
    assert first.stdout == second.stdout == "42\n" and len(calls) == 1


# ── The card the user adds: C ───────────────────────────────────────────

ODD = ('#include <stdio.h>\nint main(void) {\n    int i = 5;\n    int j = i++ * 2;\n'
       '    printf("%d %d\\n", i, j);\n}')


@needs_compiler
def test_a_c_card_takes_its_answer_from_a_real_run_and_gets_honest_misreads():
    from code_coach.gotchas import user

    built = user.build("c", ODD)
    assert built.answer == real_c_output(ODD) == "6 10"
    assert not built.raises and built.wrong, "a C card is never an error card"
    assert "6 10" not in built.wrong
    typed = user.build("c", ODD, ["5 10", "6 12", "6 10"], guess=0)
    assert typed.matched is True and typed.wrong[:2] == ["5 10", "6 12"] and "6 10" not in typed.wrong
    off = user.build("c", ODD, ["5 10", "6 12", "7 10"], guess=1)
    assert off.matched is False and "None of the options you typed match what it actually prints." in off.notes


@needs_compiler
def test_a_c_program_that_does_not_compile_is_refused_with_the_compilers_first_error():
    from code_coach.gotchas import user

    with pytest.raises(user.CardRefused) as caught:
        user.build("c", '#include <stdio.h>\nint main(void) {\n    int x = 5\n    printf("%d\\n", x);\n}')
    words = str(caught.value)
    assert "does not compile" in words and "error" in words.lower()
    assert "gotcha_run_" not in words and "\n" not in words


@needs_compiler
def test_c_programs_that_cannot_be_a_fair_question_are_refused():
    from code_coach.gotchas import user

    cases = {
        "ended with exit code 3": "#include <stdio.h>\nint main(void) {\n    printf(\"hi\\n\");\n    return 3;\n}",
        "printed nothing": "int main(void) {\n    int x = 1;\n    (void)x;\n}",
        "waits for input": '#include <stdio.h>\nint main(void) {\n    int n = 0;\n    scanf("%d", &n);\n'
                           '    printf("%d\\n", n);\n}',
        "different each time": '#include <stdio.h>\nint main(void) {\n    int x = 0;\n'
                               '    printf("%p\\n", (void *)&x);\n}',
        "longer than": "int main(void) {\n    for (;;) {}\n}",
        "too long": "\n".join(["int a;"] * 70),
    }
    for expected, code in cases.items():
        with pytest.raises(user.CardRefused) as caught:
            user.build("c", code)
        assert expected in str(caught.value), (expected, str(caught.value))


# ── Routes, per-language state, serving ─────────────────────────────────

from fastapi import HTTPException  # noqa: E402

from code_coach.api import server  # noqa: E402
from code_coach.api.schemas import (GotchaAnswerRequest, GotchaRunRequest, GotchaUserRequest,  # noqa: E402
                                    MomentumAwardRequest)
from code_coach.gotchas import GotchaStore, served_options  # noqa: E402
from tests.test_gotchas_store import Held, StoreCase, fake_deck  # noqa: E402


def status(call, *args, **kw) -> int:
    try:
        call(*args, **kw)
    except HTTPException as exc:
        return exc.status_code
    return 200


@needs_compiler
def test_the_c_deck_over_the_routes():
    summary = server.gotchas_summary("c")
    assert (summary["total"], summary["seen"], summary["title"]) == (len(C_ITEMS), 0, "C Quiz")
    assert {"id": "c", "name": "C", "count": len(C_ITEMS), "title": "C Quiz"} in summary["languages"]
    assert [d["id"] for d in server.gotchas_summary("python")["languages"]][:2] == ["python", "javascript"]
    first = server.gotchas_next("c")
    assert first["id"] in {it.id for it in C_ITEMS[:2]} and first["title"] == "C Quiz"
    assert first["language"] == "c" and len(first["options"]) == 4
    assert {"id": "c", "name": "C", "count": len(C_ITEMS), "title": "C Quiz"} in first["languages"]
    for secret in ("answer", "answer_index", "trap", "why"):
        assert secret not in first
    card = next(it for it in C_ITEMS if it.id == first["id"])
    right = first["options"].index(card.answer)
    got = server.gotchas_answer(GotchaAnswerRequest(id=card.id, language="c", chosen=right))
    assert got["correct"] and got["answer"] == card.answer and got["streak"] == 1
    assert server.gotchas_summary("c")["seen"] == 1
    assert server.gotchas_summary("python")["seen"] == 0, "C has its own counters"
    # Run it: the card's own program, compiled and run for real
    ran = server.gotchas_run(GotchaRunRequest(id=card.id, language="c"))
    assert ran["stdout"] == card.answer and ran["error"] == "" and ran["compile_error"] is False
    # The Momentum key a right C answer pays under
    paid = server.momentum_award(MomentumAwardRequest(kind="gotcha", key=f"gotcha:c:{card.id}"))
    assert paid["ok"] and paid["gained"] > 0
    again = server.momentum_award(MomentumAwardRequest(kind="gotcha", key=f"gotcha:c:{card.id}"))
    assert again["gained"] == 0


@needs_compiler
def test_the_daily_5_for_c_is_five_c_cards_and_its_own_award():
    summary = server.gotchas_summary("c")
    assert summary["daily"]["total"] == 5
    ids = []
    done = None
    for _ in range(5):
        card = server.gotchas_next("c", daily=True)
        assert card["why_picked"] == "daily" and card["id"].startswith("c-")
        ids.append(card["id"])
        done = server.gotchas_answer(GotchaAnswerRequest(id=card["id"], language="c", chosen=0))["daily"]
    assert len(set(ids)) == 5
    assert done["complete"] and done["just_completed"]
    got = server.momentum_award(MomentumAwardRequest(kind="gotcha_daily", key=f"daily:c:{done['day']}"))
    assert got["ok"] and got["gained"] > 0
    assert server.gotchas_summary("python")["daily"]["complete"] is False


@needs_compiler
def test_a_c_card_end_to_end_over_the_routes():
    added = server.gotchas_user_add(GotchaUserRequest(language="c", code=ODD))
    assert added["saved"] and added["answer"] == real_c_output(ODD)
    assert len(added["options"]) >= 3
    nxt = server.gotchas_next("c")
    assert nxt["id"] == added["id"] and nxt["mine"] and nxt["why_picked"] == "yours"
    for secret in ("answer", "answer_index", "trap", "why"):
        assert secret not in nxt
    ans = server.gotchas_answer(GotchaAnswerRequest(
        id=nxt["id"], language="c", chosen=nxt["options"].index(added["answer"])))
    assert ans["correct"] and ans["mine"] and ans["trap"] == "Added by you"
    assert server.gotchas_run(GotchaRunRequest(id=added["id"], language="c"))["stdout"] == added["answer"]
    assert [c["id"] for c in server.gotchas_user_list("c")["cards"]] == [added["id"]]
    assert server.gotchas_user_list("python")["cards"] == [], "your C cards are not Python cards"
    assert server.gotchas_summary("c")["mine"] == 1 and server.gotchas_summary("python")["mine"] == 0
    # one that compiles is a card; one that does not is a 400 that shows the compiler's first error
    bad = GotchaUserRequest(language="c", code='#include <stdio.h>\nint main(void) {\n    printf("x")\n}')
    with pytest.raises(HTTPException) as caught:
        server.gotchas_user_add(bad)
    assert caught.value.status_code == 400
    assert "does not compile" in str(caught.value.detail) and "error" in str(caught.value.detail).lower()
    with pytest.raises(HTTPException) as previewed:
        server.gotchas_user_preview(bad)
    assert previewed.value.status_code == 400
    assert server.gotchas_user_delete(added["id"], "c")["deleted"] == added["id"]


def test_c_is_hidden_and_refused_when_no_compiler_is_installed(monkeypatch):
    monkeypatch.setattr(engine, "c_available", lambda: False)
    assert "c" not in gotchas.available_languages() and gotchas.available_languages()[:2] == ["python", "javascript"]
    assert "c" not in [d["id"] for d in server.gotchas_summary("python")["languages"]]
    assert "c" not in [d["id"] for d in server.gotchas_next("javascript")["languages"]]
    refused = {
        "summary": (server.gotchas_summary, "c"),
        "next": (server.gotchas_next, "c"),
        "answer": (server.gotchas_answer, GotchaAnswerRequest(id="c-int-division", language="c", chosen=0)),
        "run": (server.gotchas_run, GotchaRunRequest(id="c-int-division", language="c")),
        "user list": (server.gotchas_user_list, "c"),
        "user preview": (server.gotchas_user_preview, GotchaUserRequest(language="c", code=SIX_TIMES_SEVEN)),
        "user add": (server.gotchas_user_add, GotchaUserRequest(language="c", code=SIX_TIMES_SEVEN)),
        "user delete": (server.gotchas_user_delete, "mine-1", "c"),
    }
    for name, (call, *args) in refused.items():
        with pytest.raises(HTTPException) as caught:
            call(*args)
        assert caught.value.status_code == 400, name
        assert "No C compiler" in str(caught.value.detail), name
    # Python and JavaScript carry on, and the C cards are still in the content (just not offered)
    assert server.gotchas_next("python")["id"] == "py-score-90"
    assert len(DECKS["c"]) >= 70
    from code_coach.gotchas import user
    from code_coach.gotchas.runner import RunnerUnavailable, run_program

    with pytest.raises(RunnerUnavailable):
        run_program("c", SIX_TIMES_SEVEN)
    with pytest.raises(user.CardRefused, match="No C compiler"):
        user.build("c", SIX_TIMES_SEVEN)


def test_a_compiler_makes_c_available_and_an_unknown_language_is_still_400(monkeypatch):
    monkeypatch.setattr(engine, "c_available", lambda: True)
    assert "c" in gotchas.available_languages()
    for call in (server.gotchas_summary, server.gotchas_next, server.gotchas_user_list):
        assert status(call, "cobol") == 400
        assert status(call, "C") == 400, "language names are lower case"
    assert status(server.gotchas_summary, "c") == 200


class ServingC(StoreCase):
    def store_c(self, n: int = 14, seed: int = 7) -> GotchaStore:
        return GotchaStore(self.dir / "gotchas.json", self.dir / "gotchas_user.json", clock=self.clock,
                           rng=random.Random(seed),
                           builtin=lambda lang: fake_deck(n, lang) if lang in ("python", "javascript", "c") else ())

    def test_the_first_two_c_cards_come_in_deck_order_then_it_goes_random(self) -> None:
        s = self.store_c()
        a, why = s.pick("c")
        self.assertEqual((a.id, why), ("t-0", "new"))
        self.play(s, a, True, "c")
        b, _ = s.pick("c")
        self.assertEqual(b.id, "t-1")
        self.play(s, b, True, "c")
        seen = {a.id, b.id}
        for _ in range(8):
            c, _ = s.pick("c", exclude=frozenset(seen))
            self.assertNotIn(c.id, seen)
            seen.add(c.id)
            self.play(s, c, True, "c")

    def test_a_missed_c_card_comes_back_after_five_to_ten_c_answers(self) -> None:
        s = self.store_c(30)
        first, _ = s.pick("c")
        self.play(s, first, False, "c")
        gaps = []
        for i in range(1, 14):
            card, why = s.pick("c")
            if why == "again":
                gaps.append(i)
                self.assertEqual(card.id, first.id)
                break
            self.play(s, card, True, "c")
        self.assertTrue(gaps and 5 <= gaps[0] <= 11, gaps)

    def test_c_keeps_its_own_ticks_streak_stats_and_daily(self) -> None:
        s = self.store_c()
        py, _ = s.pick("python")
        self.play(s, py, True, "python")
        self.assertEqual(s.summary("c")["seen"], 0)
        c1, _ = s.pick("c")
        self.assertEqual(c1.id, "t-0", "C has its own first card")
        got = self.play(s, c1, False, "c")
        self.assertEqual((got["streak"], got["summary"]["language"]), (0, "c"))
        self.assertEqual(s.summary("python")["streak"], 1)
        self.assertEqual(s.summary("c")["seen"], 1)
        plan_c, plan_py = s.summary("c")["daily"], s.summary("python")["daily"]
        self.assertEqual((plan_c["total"], plan_py["total"]), (5, 5))
        again = self.store_c()
        self.assertEqual(again.summary("c")["seen"], 1, "it all survives a restart")

    def test_c_cards_you_add_are_served_first_and_stay_in_c(self) -> None:
        s = self.store_c()
        item = s.add_card("c", "int main(void) { return 0; }", "x", ["y", "z"], False, "Added by you", "Because.")
        self.assertTrue(item.mine and item.language == "c")
        self.assertEqual(s.pick("c")[1], "yours")
        self.assertEqual(s.pick("python")[1], "new")
        self.assertEqual([c.id for c in s.my_cards("c")], [item.id])
        self.assertEqual(s.my_cards("javascript"), [])

    def test_an_old_gotchas_file_without_c_keys_still_loads(self) -> None:
        import json

        (self.dir / "gotchas.json").write_text(json.dumps({
            "version": 1,
            "stats": {"python:py-score-90": {"seen": 2, "right": 1, "last_day": "2026-10-19", "last_tick": 2,
                                             "due": None}},
            "ticks": {"python": 2, "javascript": 1},
            "streak": {"python": {"now": 1, "best": 3}},
            "daily": {"python": {"day": "2026-10-19", "ids": ["t-0"], "results": {"t-0": True}}},
        }), encoding="utf-8")
        s = self.store_c()
        self.assertEqual(s.summary("c")["seen"], 0)
        self.assertEqual((s.summary("c")["streak"], s.summary("c")["streak_best"]), (0, 0))
        self.assertEqual(s.summary("python")["streak_best"], 3)
        card, _ = s.pick("c")
        self.assertEqual(card.id, "t-0")
        self.play(s, card, True, "c")
        saved = json.loads((self.dir / "gotchas.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["ticks"]["c"], 1)
        self.assertEqual(saved["ticks"]["python"], 2, "the other languages' counters are untouched")
        self.assertIn("c:t-0", saved["stats"])
        self.assertIn("c", saved["streak"])

    def test_c_options_are_served_in_a_fixed_order_with_the_answer_where_it_says(self) -> None:
        for i, it in enumerate(DECKS["c"]):
            options, spot = served_options(it, i)
            self.assertEqual(served_options(it, i), (options, spot))
            self.assertEqual(options[spot], it.answer)
            self.assertEqual(sorted(options), sorted(it.options))


def test_the_held_clock_helper_is_the_one_the_other_tests_use():
    assert Held()().isoformat() == "2026-10-19"
