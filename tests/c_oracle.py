"""The C oracle for Brain Drills: hold a batch of C snippets to the real compilers, in a handful of processes.

A C pack has thousands of items and a compile costs 0.15-0.7 s, so the items are batched like the Dart ones
(tests/dart_oracle.py) - and then built MORE THAN ONE WAY, because a C answer must be the same on every machine:

* every item whose program has no `main` is the BODY of its own `static void iN(void)` in ONE source, `batch.c`
  (a `#line 1 "itemN.c"` before each body makes every compiler message name the item and the line inside it);
* every item that is a COMPLETE program (it mentions `main(`: it has globals, helper functions or `static` locals) is
  its own translation unit `itemN.c` with `#define main iN_main` in front, so two items may both declare `counter()`
  or `int total;`; these are compiled in parallel;
* `batch.c` also holds a generated `main` that calls the items one after the other, each between the marker lines
  `@@S<id>@@` and `@@E<id>@@` (flushed, so a crash loses only the item it happened in), and takes the position to
  start from as its argument: an item that crashes or runs for ever is named, skipped (`start = position + 1`) and the
  rest still run, with no recompile. Then there is ONE compile (plus the parallel ones), ONE link and ONE run;
* an item that does not compile is named by file and line, removed, and the batch compiled again; an error that names
  no item is bisected. A compile failure is that item's value, never an exception.

The builds (`DEFAULT_BUILDS`): the first compiler found of clang, gcc at `-O0 -fsigned-char`, again at
`-O2 -funsigned-char`, and - when Visual Studio is installed - MSVC at `/Od`. All of them print the same thing for
every item, or the item's value is `BUILDS DIFFER: ...` (so the oracle test fails and names it). Strict flags:
`-std=c11 -Wall -Wextra -pedantic`; the warnings of the gnu builds are kept per item (`Checked.warnings`) and
`bad_warnings` says which are not the harmless kinds of tests/test_gotchas_c.py (BENIGN_WARNINGS, NEVER_BENIGN).
`ub_findings` builds once more with clang's undefined-behaviour sanitizer (in its recovering mode, so one run
reports every item that did something undefined) and names the items.

What a C item is (one rule, shared with "Run it" - `cProgram` in web/src/lib/brainRound.ts - and the `check`
field): the program is `item.check`, or the prompt when `check` is empty. The four headers `stdio.h stdint.h
string.h stddef.h` are always in front (`HEADERS`: an item never writes `#include`). If the program mentions `main(` it
is a complete program (globals, functions, `int main(void) {...}`), else it is the BODY of `main` and gets
`int main(void) { ... }` around it. The program prints its own answer with `printf`; the value is its standard
output with the whitespace at both ends cut off (so an answer starts and ends with a visible character: `|  42|`).

Use from a test:

    from tests.c_oracle import c_values
    got = c_values([item.check or item.prompt for item in items])

Without a C compiler on the machine `HAVE_COMPILER` is False and tests skip.
"""

from __future__ import annotations

import itertools
import os
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from code_coach import engine

CLANG = shutil.which("clang")
GCC = shutil.which("gcc")
GNU = CLANG or GCC
VCVARS = engine._find_vcvars()
HAVE_COMPILER = bool(GNU or VCVARS)

#: In front of every program ("Run it" puts the same text there: `C_HEADERS` in brainRound.ts, held equal by a test).
HEADERS = "#include <stdio.h>\n#include <stdint.h>\n#include <string.h>\n#include <stddef.h>\n"
STRICT = ("-std=c11", "-Wall", "-Wextra", "-pedantic")
MAIN = re.compile(r"\bmain\s*\(")
RUN_SECONDS = 15.0
#: Complete programs are compiled this many at a time.
WORKERS = max(2, min(8, os.cpu_count() or 2))


@dataclass(frozen=True)
class Build:
    """One way to build a batch: a gnu-style compiler with flags, or MSVC."""
    name: str
    kind: str  # "gnu" | "msvc"
    flags: tuple[str, ...]


def default_builds() -> tuple[Build, ...]:
    out: list[Build] = []
    if GNU:
        label = "clang" if CLANG else "gcc"
        out += [Build(f"{label} -O0 -fsigned-char", "gnu", ("-O0", "-fsigned-char")),
                Build(f"{label} -O2 -funsigned-char", "gnu", ("-O2", "-funsigned-char"))]
    if VCVARS:
        out.append(Build("msvc /Od", "msvc", ("/Od",)))
    return tuple(out)


DEFAULT_BUILDS = default_builds()
#: The build the others are compared with, and that the answers are held to.
BASELINE = DEFAULT_BUILDS[0] if DEFAULT_BUILDS else None


# ── What an item's program is ───────────────────────────────────────────

def is_complete(code: str) -> bool:
    return bool(MAIN.search(code))


def full_program(code: str) -> str:
    """The program "Run it" runs for an item's code: the headers, then the code as is when complete, else wrapped
    in `int main(void)`."""
    code = code.rstrip("\n")
    if is_complete(code):
        return HEADERS + code + "\n"
    body = "\n".join("    " + ln if ln.strip() else ln for ln in code.split("\n"))
    return HEADERS + "int main(void) {\n" + body + "\n}\n"


def lint(code: str) -> str:
    """The first thing in the program that can differ between machines (tests/test_gotchas_c.BANNED), else ''.
    Also: an `#include` of the item's own, and a plain `char` holding a value that is signed on some machines."""
    from tests.test_gotchas_c import BANNED

    found = BANNED.search(code)
    if found:
        return found.group(0)
    if re.search(r"^\s*#\s*include", code, re.M):
        return "#include (the four headers are already there)"
    for m in re.finditer(r"(?<!unsigned )(?<!signed )\bchar\s+(\w+)\s*=\s*(\d+)\s*;", code):
        if int(m.group(2)) >= 128:
            return f"char {m.group(1)} = {m.group(2)}"
    return ""


# ── The result of one item ──────────────────────────────────────────────

@dataclass(frozen=True)
class CRun:
    #: What the item printed (the whole of it); None when it did not compile or did not finish.
    output: str | None = None
    #: The compiler's first complaint ("did not compile": file and line inside the item), "".
    compile_error: str = ""
    #: "crashed" or "ran for too long" - the item started and never finished.
    stopped: str = ""
    #: Warning flags the gnu build gave for it (`unused-variable`...).
    warnings: tuple[str, ...] = ()

    def value(self) -> str:
        if self.compile_error:
            return "COMPILE ERROR: " + self.compile_error
        if self.stopped:
            return "STOPPED: " + self.stopped
        return (self.output or "").strip()


@dataclass(frozen=True)
class Checked:
    """One item through every build."""
    #: The baseline's value, or `BUILDS DIFFER: ...` when the builds disagree.
    value: str
    #: Warning flags of the gnu builds, not repeated.
    warnings: tuple[str, ...]
    #: build name -> value
    builds: dict = field(default_factory=dict, compare=False)


# ── Compiling ───────────────────────────────────────────────────────────

_GNU_DIAG = re.compile(r"^(?:.*?[\\/])?item(\d+)\.c:(\d+):(\d+): (error|warning|fatal error): (.*)$", re.M)
_MSVC_DIAG = re.compile(r"^(?:.*?[\\/])?item(\d+)\.c\((\d+)(?:,\d+)?\) ?: (?:fatal )?error (C\d+): (.*)$", re.M)
_FLAG = re.compile(r"\[-W([\w=+-]+)\]\s*$")


_COUNTER = itertools.count()


def _text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", "replace").replace("\r\n", "\n") if path.exists() else ""


def _run_process(argv: list[str], cwd: Path, timeout: float, env: dict | None = None) -> tuple[int, str]:
    """(exit code, stdout + stderr) of a tool run to the end; -9 and a note on a timeout."""
    from code_coach.canvas.pyharness.session import child_flags, kill_tree

    out_path = cwd / ("log%d.txt" % next(_COUNTER))
    with open(out_path, "wb") as out:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=out,
                                stderr=subprocess.STDOUT, creationflags=child_flags())
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_tree(proc)
            return -9, "TIMEOUT after %ss" % timeout
    return code, _text(out_path)


def isolate(code: str) -> str:
    """The program with `static` put in front of every function and variable it defines at file level (but `main`),
    so two complete programs linked into one executable cannot clash over a name (`counter()`, `int total;`).
    Types, typedefs, `extern`s and what is already `static` are left alone; anything unusual (a function declared over
    several lines, a variable declared with a struct that is defined in the same statement) is left alone too and,
    if it does clash, the link says so and the item is named."""
    out: list[str] = []
    depth = 0
    in_comment = False
    in_main = False
    at_start = True  # at file level, at the start of a declaration
    for line in code.split("\n"):
        stripped = line.strip()
        if depth == 0 and not in_comment and at_start and (line[:1].isalpha() or line[:1] == "_"):
            first = re.match(r"[A-Za-z_]\w*", line).group(0)
            head = line.split("{")[0]
            declares = bool(re.search(r"[(=;\[]", head))
            is_type = bool(re.match(r"(?:struct|union|enum)\s+\w*\s*(?:\{|;|$)", line))
            is_main = bool(re.search(r"\bmain\s*\(", head))
            if first not in ("static", "typedef", "extern", "return") and declares and not is_type and not is_main:
                line = "static " + line
            in_main = is_main
        elif depth == 1 and in_main and stripped.startswith("}"):
            # `main` is renamed, so falling off its end is no longer allowed: say what C says, `return 0;`
            previous = next((x.strip() for x in reversed(out) if x.strip()), "")
            if not previous.startswith("return"):
                out.append("    return 0;")
        out.append(line)
        i, n, last = 0, len(line), ""
        while i < n:  # braces, strings and comments of this line
            ch = line[i]
            if in_comment:
                if line.startswith("*/", i):
                    in_comment = False
                    i += 1
            elif line.startswith("/*", i):
                in_comment = True
                i += 1
            elif line.startswith("//", i):
                break
            elif ch in "\"'":
                j = i + 1
                while j < n and line[j] != ch:
                    j += 2 if line[j] == "\\" else 1
                i = j
                last = ch
            else:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                if not ch.isspace():
                    last = ch
            i += 1
        if not stripped or stripped.startswith("#"):
            continue
        at_start = depth == 0 and not in_comment and last in (";", "}")
    return "\n".join(out)


def _item_source(idx: int, code: str) -> str:
    """A complete program as its own translation unit."""
    return HEADERS + f"#define main i{idx}_main\n#line 1 \"item{idx}.c\"\n" + isolate(code.rstrip("\n")) + "\n"


def _batch_source(bodies: dict[int, str], complete: list[int]) -> str:
    parts = [HEADERS]
    for idx in complete:
        parts.append(f"extern int i{idx}_main(void);\nstatic void w{idx}(void) {{ (void)i{idx}_main(); }}\n")
    for idx, code in bodies.items():
        parts.append(f"static void i{idx}(void) {{\n#line 1 \"item{idx}.c\"\n{code.rstrip(chr(10))}\n}}\n")
    order = [(idx, f"i{idx}") for idx in bodies] + [(idx, f"w{idx}") for idx in complete]
    parts.append("#line 1 \"batch_main.c\"\n#include <stdlib.h>\n")
    parts.append("static void (*const fns[])(void) = {%s};\n" % ", ".join(fn for _, fn in order or [(0, "0")]))
    parts.append("static const int ids[] = {%s};\n" % ", ".join(str(i) for i, _ in order or [(0, 0)]))
    parts.append(f"enum {{ COUNT = {len(order)} }};\n")
    parts.append(
        "int main(int argc, char **argv) {\n"
        "    int k = argc > 1 ? atoi(argv[1]) : 0;\n"
        "    for (; k < COUNT; k++) {\n"
        "        printf(\"@@S%d@@\\n\", ids[k]); fflush(stdout);\n"
        "        fns[k]();\n"
        "        fflush(stdout);\n"
        "        printf(\"\\n@@E%d@@\\n\", ids[k]); fflush(stdout);\n"
        "    }\n"
        "    return 0;\n"
        "}\n")
    return "".join(parts), [idx for idx, _ in order]


def _gnu_compile(build: Build, folder: Path, name: str) -> tuple[bool, str]:
    cc = GNU
    argv = [cc, *STRICT, "-ferror-limit=0" if CLANG else "-fmax-errors=0", "-fno-color-diagnostics" if CLANG else "-fdiagnostics-color=never",
            *build.flags, "-c", name, "-o", name[:-2] + ".o"]
    code, text = _run_process(argv, folder, 240.0)
    return code == 0 and (folder / (name[:-2] + ".o")).exists(), text


def _fresh(folder: Path) -> Path:
    """A new empty folder inside the batch's (a tool of the last attempt may still hold files of the old one)."""
    sub = folder / ("a%d" % next(_COUNTER))
    sub.mkdir()
    return sub


def _gnu_attempt(build: Build, folder: Path, programs: dict[int, str]):
    """One try: compile (the batch, and the complete programs in parallel), link. Returns
    (exe or None, {item: first error}, {item: warning flags}, unattributed error text)."""
    folder = _fresh(folder)
    bodies = {i: c for i, c in programs.items() if not is_complete(c)}
    complete = [i for i, c in programs.items() if is_complete(c)]
    source, order = _batch_source(bodies, complete)
    (folder / "batch.c").write_text(source, encoding="utf-8", newline="\n")
    for idx in complete:
        (folder / f"item{idx}.c").write_text(_item_source(idx, programs[idx]), encoding="utf-8", newline="\n")
    jobs = ["batch.c"] + [f"item{i}.c" for i in complete]
    with ThreadPoolExecutor(min(WORKERS, len(jobs))) as pool:
        done = list(pool.map(lambda n: _gnu_compile(build, folder, n), jobs))
    errors: dict[int, str] = {}
    warnings: dict[int, list[str]] = {}
    unattributed = ""
    for (ok, log), job in zip(done, jobs):
        named = False
        for m in _GNU_DIAG.finditer(log):
            idx, line, _, kind, message = int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5).strip()
            if kind == "warning":
                flag = _FLAG.search(message)
                if flag:
                    warnings.setdefault(idx, []).append(flag.group(1))
            else:
                errors.setdefault(idx, f"{message} (line {line} of the item)")
                named = True
        if not ok and not named:
            unattributed += f"[{job}] " + log.strip()[:600] + "\n"
    if errors or unattributed:
        return None, errors, warnings, unattributed, order
    objs = ["batch.o"] + [f"item{i}.o" for i in complete]
    linked, log = _run_process([GNU, *objs, "-o", "batch.exe"], folder, 240.0)
    if linked != 0 or not (folder / "batch.exe").exists():
        return None, {}, warnings, "link: " + log.strip()[:600], order
    return folder / "batch.exe", {}, warnings, "", order


def _msvc_attempt(build: Build, folder: Path, programs: dict[int, str]):
    """The same for MSVC: ONE `cl` command for everything (/MP compiles the files in parallel)."""
    folder = _fresh(folder)
    bodies = {i: c for i, c in programs.items() if not is_complete(c)}
    complete = [i for i, c in programs.items() if is_complete(c)]
    source, order = _batch_source(bodies, complete)
    (folder / "batch.c").write_text(source, encoding="utf-8", newline="\n")
    for idx in complete:
        (folder / f"item{idx}.c").write_text(_item_source(idx, programs[idx]), encoding="utf-8", newline="\n")
    files = " ".join(["batch.c"] + [f"item{i}.c" for i in complete])
    bat = folder / "build.bat"
    std = engine._MSVC_STD[".c"]
    bat.write_bytes((f'@echo off\r\ncall "{VCVARS}" >nul\r\n'
                     f'cl /nologo {std} /W3 /MP {" ".join(build.flags)} /Fo"{folder}\\\\" /Fe"{folder}\\batch.exe" {files}\r\n'
                     ).encode("ascii"))
    code, log = _run_process(["cmd", "/c", str(bat)], folder, 900.0)
    errors: dict[int, str] = {}
    for m in _MSVC_DIAG.finditer(log):
        errors.setdefault(int(m.group(1)), f"{m.group(4).strip()} ({m.group(3)}, line {m.group(2)} of the item)")
    if errors:
        return None, errors, {}, "", order
    if code != 0 or not (folder / "batch.exe").exists():
        return None, {}, {}, "msvc: " + log.strip()[-600:], order
    return folder / "batch.exe", {}, {}, "", order


# ── Running ─────────────────────────────────────────────────────────────

_ITEM_OUT = re.compile(r"@@S(\d+)@@\n(.*?)\n@@E\1@@\n", re.S)


def _execute(exe: Path, order: list[int], env: dict | None = None) -> tuple[dict[int, str], dict[int, str], str]:
    """Run the batch, skipping past any item that crashes or hangs: (outputs, stopped, stderr)."""
    outputs: dict[int, str] = {}
    stopped: dict[int, str] = {}
    stderr_all = ""
    start = 0
    folder = exe.parent
    run_env = env if env is not None else {k: os.environ[k] for k in ("SYSTEMROOT", "SystemRoot", "TEMP", "TMP") if k in os.environ}
    while start < len(order):
        from code_coach.canvas.pyharness.session import child_flags, kill_tree

        out_path, err_path = folder / "run_out.txt", folder / "run_err.txt"
        with open(out_path, "wb") as out, open(err_path, "wb") as err:
            proc = subprocess.Popen([str(exe), str(start)], cwd=folder, env=run_env, stdin=subprocess.DEVNULL,
                                    stdout=out, stderr=err, creationflags=child_flags())
            timed_out = False
            try:
                proc.wait(timeout=RUN_SECONDS)
            except subprocess.TimeoutExpired:
                kill_tree(proc)
                timed_out = True
        text = _text(out_path)
        stderr_all += _text(err_path)
        done_here = 0
        for m in _ITEM_OUT.finditer(text):
            outputs[int(m.group(1))] = m.group(2)
            done_here += 1
        position = start + done_here
        if position >= len(order):
            break
        # the item at `position` started and did not finish
        if timed_out:
            stopped[order[position]] = "ran for too long"
        elif proc.returncode == 0:
            stopped[order[position]] = "ended the whole program (exit) before it finished"
        else:
            stopped[order[position]] = f"crashed (exit code {proc.returncode})"
        start = position + 1
    return outputs, stopped, stderr_all


def _sanitizer_env_path() -> str:
    """The folder with clang's sanitizer runtime (a DLL on Windows), which the batch's PATH needs."""
    if os.name == "nt" and CLANG:
        found = subprocess.run([CLANG, "-print-runtime-dir"], capture_output=True, text=True)
        return found.stdout.strip() if found.returncode == 0 else ""
    return ""


# ── The batch, on one build ─────────────────────────────────────────────

def run_batch(programs: list[str], build: Build | None = None) -> list[CRun]:
    """Build and run every program (an item's `check` or prompt, WITHOUT headers) as one batch on one build."""
    if not programs:
        return []
    build = build or BASELINE
    assert build is not None, "no C compiler on this machine"
    from code_coach.canvas.pyharness.session import remove_folder

    folder = Path(tempfile.mkdtemp(prefix="c_oracle_"))
    try:
        found = _batch(build, folder, dict(enumerate(programs)))
    finally:
        remove_folder(folder)
    return [found[i] for i in range(len(programs))]


def _batch(build: Build, folder: Path, programs: dict[int, str], extra_env: dict | None = None,
           sanitize_out: dict | None = None) -> dict[int, CRun]:
    results: dict[int, CRun] = {}
    todo = dict(programs)
    all_warnings: dict[int, list[str]] = {}
    attempt = _gnu_attempt if build.kind == "gnu" else _msvc_attempt
    for _ in range(8):
        if not todo:
            return results
        exe, errors, warnings, unattributed, order = attempt(build, folder, todo)
        for idx, flags in warnings.items():
            all_warnings.setdefault(idx, []).extend(flags)
        if exe is not None:
            outputs, stopped, stderr = _execute(exe, order, extra_env)
            if sanitize_out is not None:
                sanitize_out["stderr"] = sanitize_out.get("stderr", "") + stderr
            for idx in todo:
                w = tuple(dict.fromkeys(all_warnings.get(idx, ())))
                if idx in stopped:
                    results[idx] = CRun(stopped=stopped[idx], warnings=w)
                elif idx in outputs:
                    results[idx] = CRun(output=outputs[idx], warnings=w)
                else:
                    results[idx] = CRun(stopped="never ran", warnings=w)
            return results
        if errors:
            for idx, message in errors.items():
                if idx in todo:
                    results[idx] = CRun(compile_error=message)
                    del todo[idx]
            continue
        if re.search(r"batch(_main)?\.c[:(]\d+(?::\d+)?[:)]? ?:? ?(?:fatal )?error", unattributed):  # the harness itself
            raise AssertionError("the oracle's own batch.c does not build:\n" + unattributed[-2000:])
        # An error naming no item (a crash, a timeout, a link error): split the batch to find the culprit.
        if len(todo) == 1:
            (idx,) = todo
            results[idx] = CRun(compile_error="did not build: " + (unattributed.strip()[:300] or "no reason given"))
            return results
        keys = list(todo)
        half = len(keys) // 2
        for part in (keys[:half], keys[half:]):
            results.update(_batch(build, folder, {k: todo[k] for k in part}, extra_env, sanitize_out))
        return results
    for idx in todo:
        results[idx] = CRun(compile_error="did not build after removing the others that failed")
    return results


# ── Every build, compared ───────────────────────────────────────────────

def check_items(programs: list[str], builds: tuple[Build, ...] | None = None) -> list[Checked]:
    """Every program through every build: its value (the baseline's, or `BUILDS DIFFER`) and its warnings."""
    builds = builds or DEFAULT_BUILDS
    assert builds, "no C compiler on this machine"
    runs = [run_batch(programs, b) for b in builds]
    out: list[Checked] = []
    for i in range(len(programs)):
        values = {b.name: r[i].value() for b, r in zip(builds, runs)}
        base = values[builds[0].name]
        value = base
        if len(set(values.values())) > 1:
            value = "BUILDS DIFFER: " + " | ".join(f"{name}: {v!r}" for name, v in values.items())
        flags: list[str] = []
        for b, r in zip(builds, runs):
            for f in r[i].warnings:
                if f not in flags:
                    flags.append(f)
        out.append(Checked(value, tuple(flags), values))
    return out


def c_values(programs: list[str], builds: tuple[Build, ...] | None = None) -> list[str]:
    """The value of each program as the real compilers print it, identical on every build (see the module docstring)."""
    return [c.value for c in check_items(programs, builds)]


#: Warnings a Brain Drills item may trigger on top of the Gotchas list: each is the very trap the item asks about.
BRAIN_BENIGN = {
    "xor-used-as-pow",   # `2 ^ 2` is not a power: the Bits drills ask what it is
    "missing-braces",    # `int m[2][2] = {1, 2, 3, 4};` fills the rows one after another: an Array Reach question
    "logical-not-parentheses",  # `!a == b` is (!a) == b: an Operator Order question
    "bool-operation",    # `~!a`: an Operator Order question
}


def bad_warnings(flags: tuple[str, ...]) -> list[str]:
    """The warning flags that are not the harmless kinds (tests/test_gotchas_c.py's BENIGN_WARNINGS, plus `BRAIN_BENIGN`)."""
    from tests.test_gotchas_c import BENIGN_WARNINGS, NEVER_BENIGN

    allowed = BENIGN_WARNINGS | BRAIN_BENIGN
    return [f for f in flags if f.split("=")[0] in NEVER_BENIGN or f.split("=")[0] not in allowed]


# ── Undefined behaviour ─────────────────────────────────────────────────

_UBSAN = re.compile(r"(?:^|[\\/\s])item(\d+)\.c:(\d+):\d+: runtime error: (.*)$", re.M)


def sanitizer_available() -> bool:
    return bool(CLANG)


def ub_findings(programs: list[str]) -> dict[int, str]:
    """The items that did something undefined when built with clang's `-fsanitize=undefined` (recovering mode: one
    run reports them all): {index: first finding}. Empty when the sanitizer cannot be used here."""
    if not CLANG:
        return {}
    from code_coach.canvas.pyharness.session import remove_folder

    build = Build("clang -O1 ubsan", "gnu", ("-O1", "-fsanitize=undefined", "-fno-omit-frame-pointer"))
    folder = Path(tempfile.mkdtemp(prefix="c_oracle_ub_"))
    sink: dict = {}
    try:
        runtime = _sanitizer_env_path()
        env = {k: os.environ[k] for k in ("SYSTEMROOT", "SystemRoot", "TEMP", "TMP") if k in os.environ}
        if runtime:
            env["PATH"] = runtime
        _batch(build, folder, dict(enumerate(programs)), env, sink)
    finally:
        remove_folder(folder)
    found: dict[int, str] = {}
    for m in _UBSAN.finditer(sink.get("stderr", "")):
        found.setdefault(int(m.group(1)), f"{m.group(3).strip()} (line {m.group(2)} of the item)")
    return found
