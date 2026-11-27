"""The Rust oracle for Brain Drills: hold a batch of Rust snippets to the real rustc, in a handful of processes.

A Rust pack has a thousand-odd items and a rustc build costs about a second, so items are batched into crates (like
the C ones in tests/c_oracle.py) and every crate is built TWO ways, because "Run it" builds with `-O` (release: integer
overflow wraps) while a debug build panics on it - an answer must be the same in both:

* every item becomes a module of one crate: `mod iN { pub fn main() { <body> } }` for a BODY item, `mod iN { <program> }`
  for a COMPLETE program (it mentions `fn main(`: structs, impls, helper functions, then main), whose `fn main(` is made
  `pub fn main(`. So two items may both declare `struct Point` or `fn helper`;
* the crate's own `main` calls the items one after the other inside `catch_unwind`, each between the marker lines
  `@@S<id>@@` and `@@E<id>@@`; a panic is the item's value (`PANIC: <message>`), and an item that runs for ever is
  named (`HANG`), skipped (the exe takes the position to start from) and the rest still run, with no rebuild;
* an item that does not compile is named by its line range, removed, and the crate checked again
  (`rustc --emit=metadata`, which runs the borrow checker, the way `cargo check` does) until it is clean - borrow errors
  only show once the type errors are gone, hence the loop. An item that failed in the batch is then checked ON ITS OWN,
  so its verdict never depends on its neighbours. A compile failure is the item's value (`COMPILE ERROR: ...`), never an
  exception;
* the crates are built in parallel, debug (`-C debug-assertions`, overflow checks on) and `-O`; when the two print
  different things the value is `BUILDS DIFFER: ...`.

`#![allow(warnings)]` is on (a warning is never an error, and "Run it" never shows them either); deny-by-default lints
such as `arithmetic_overflow` stay errors, as they are in "Run it".

What a Rust item is (one rule, shared with "Run it" - `rustProgram` in web/src/lib/brainRound.ts - and the `check`
field): the program is `item.check`, or the prompt when `check` is empty; if it mentions `fn main(` it is a complete
program, else it is the BODY of `fn main()`. It prints its own answer with `println!`; the value is its standard output
with the whitespace at both ends cut off.

    from tests.rust_oracle import rust_results, rust_values
    got = rust_values([item.check or item.prompt for item in items])

Without rustc on the machine `HAVE_RUSTC` is False and tests skip.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

RUSTC = shutil.which("rustc")
HAVE_RUSTC = RUSTC is not None
EDITION = ("--edition", "2021")
MAIN = re.compile(r"\bfn\s+main\s*\(")
CHUNK = 220
WORKERS = max(2, min(6, os.cpu_count() or 2))
RUN_SECONDS = 20.0
BUILD_SECONDS = 600.0


def is_complete(code: str) -> bool:
    return bool(MAIN.search(code))


def full_program(code: str) -> str:
    """The program "Run it" builds (rustProgram in brainRound.ts)."""
    body = code.rstrip()
    if is_complete(body):
        return body + "\n"
    return "fn main() {\n" + "\n".join("    " + ln if ln.strip() else ln for ln in body.split("\n")) + "\n}\n"


@dataclass(frozen=True)
class RustRun:
    #: did it compile (on its own when the batch said no)
    compiled: bool
    #: the first error, when it did not compile
    compile_error: str = ""
    #: what it printed, trimmed (both builds agreeing), or "PANIC: ...", "HANG", "BUILDS DIFFER: ..."
    out: str = ""
    panicked: bool = False

    @property
    def value(self) -> str:
        if not self.compiled:
            return "COMPILE ERROR: " + self.compile_error
        return self.out

    @property
    def verdict(self) -> str:
        """For a fine-or-error question: "error" when it does not compile or panics, else "fine"."""
        return "error" if (not self.compiled or self.panicked) else "fine"


_DRIVER = r'''
fn __cc_payload(e: &Box<dyn std::any::Any + Send>) -> String {
    if let Some(s) = e.downcast_ref::<&str>() { return s.to_string(); }
    if let Some(s) = e.downcast_ref::<String>() { return s.clone(); }
    String::from("panic")
}
fn main() {
    use std::io::Write;
    std::panic::set_hook(Box::new(|_| {}));
    let start: usize = std::env::args().nth(1).and_then(|s| s.parse().ok()).unwrap_or(0);
    let items: Vec<(usize, fn())> = vec![%ITEMS%];
    for (pos, (id, f)) in items.iter().enumerate() {
        if pos < start { continue; }
        println!("@@S{}@@", id);
        std::io::stdout().flush().ok();
        let r = std::panic::catch_unwind(*f);
        std::io::stdout().flush().ok();
        if let Err(e) = r { println!("\n@@P@@{}", __cc_payload(&e).replace('\n', " ")); }
        println!("\n@@E{}@@", id);
        std::io::stdout().flush().ok();
    }
}
'''


def _module(idx: int, code: str) -> str:
    if is_complete(code):
        inner = MAIN.sub("pub fn main(", code.rstrip(), count=1)
    else:
        inner = "pub fn main() {\n" + code.rstrip() + "\n}"
    return f"mod i{idx} {{\n#[allow(unused_imports)]\nuse super::*;\n" + inner + "\n}\n"


def _crate(programs: dict[int, str]) -> tuple[str, dict[int, tuple[int, int]]]:
    """The crate source and, per item, its (first, last) line in it (1-based)."""
    parts = ["#![allow(warnings)]\n"]
    line = 2
    spans: dict[int, tuple[int, int]] = {}
    for idx, code in programs.items():
        text = _module(idx, code)
        n = text.count("\n")
        spans[idx] = (line, line + n - 1)
        parts.append(text)
        line += n
    order = ", ".join(f"({i}, i{i}::main as fn())" for i in programs)
    parts.append(_DRIVER.replace("%ITEMS%", order))
    return "".join(parts), spans


_DIAG = re.compile(r"^(error(?:\[E\d+\])?: .*)\n\s*--> [^\n]*?:(\d+):\d+", re.M)


def _rustc(argv: list[str], cwd: Path, timeout: float = BUILD_SECONDS) -> tuple[int, str]:
    try:
        done = subprocess.run([RUSTC, *argv], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return 1, "error: rustc timed out"
    return done.returncode, done.stdout + done.stderr


def _check_alone(folder: Path, code: str) -> str:
    """'' when the program compiles on its own (with the borrow checker), else its first error."""
    src = folder / "alone.rs"
    src.write_text("#![allow(warnings)]\n" + full_program(code), encoding="utf-8")
    rc, text = _rustc([*EDITION, "--crate-type", "bin", "--emit=metadata", "-o", str(folder / "alone.rmeta"),
                       str(src)], folder, 120)
    if rc == 0:
        return ""
    for ln in text.splitlines():
        if ln.startswith("error"):
            return ln.strip()
    return text.strip().splitlines()[0] if text.strip() else "error"


def _which_item(spans: dict[int, tuple[int, int]], line: int) -> int | None:
    for idx, (a, b) in spans.items():
        if a <= line <= b:
            return idx
    return None


_ITEM_OUT = re.compile(r"@@S(\d+)@@\n(.*?)\n@@E\1@@\n", re.S)


def _execute(exe: Path, order: list[int]) -> dict[int, str]:
    """{id: raw output} for every item, restarting past an item that hangs."""
    got: dict[int, str] = {}
    start = 0
    while start < len(order):
        try:
            done = subprocess.run([str(exe), str(start)], capture_output=True, timeout=RUN_SECONDS)
            text = done.stdout.decode("utf-8", "replace").replace("\r\n", "\n")
            hung = False
        except subprocess.TimeoutExpired as e:
            text = (e.stdout or b"").decode("utf-8", "replace").replace("\r\n", "\n")
            hung = True
        for m in _ITEM_OUT.finditer(text):
            got[int(m.group(1))] = m.group(2)
        nxt = start
        while nxt < len(order) and order[nxt] in got:
            nxt += 1
        if nxt >= len(order):
            break
        # the item at `nxt` never finished: it hung or took the process down
        got[order[nxt]] = "HANG" if hung else "CRASH"
        start = nxt + 1
    return got


def _value(raw: str) -> tuple[str, bool]:
    if raw in ("HANG", "CRASH"):
        return raw, True
    if "\n@@P@@" in raw or raw.startswith("@@P@@"):
        before, _, msg = raw.partition("@@P@@")
        return "PANIC: " + msg.strip(), True
    return raw.strip(), False


def _chunk(programs: dict[int, str]) -> dict[int, RustRun]:
    folder = Path(tempfile.mkdtemp(prefix="cc_rust_oracle_"))
    try:
        live = dict(programs)
        errors: dict[int, str] = {}
        for _ in range(12):
            if not live:
                break
            source, spans = _crate(live)
            src = folder / "main.rs"
            src.write_text(source, encoding="utf-8")
            rc, text = _rustc([*EDITION, "--crate-type", "bin", "--emit=metadata", "-o", str(folder / "m.rmeta"),
                               str(src)], folder)
            if rc == 0:
                break
            bad = {}
            for m in _DIAG.finditer(text):
                idx = _which_item(spans, int(m.group(2)))
                if idx is not None:
                    bad.setdefault(idx, m.group(1).strip())
            if not bad:
                # an error that names no item: check them one by one
                for idx in list(live):
                    why = _check_alone(folder, live[idx])
                    if why:
                        bad[idx] = why
                if not bad:
                    raise RuntimeError("the batch does not build but every item does on its own:\n" + text[-3000:])
            for idx, why in bad.items():
                errors[idx] = why
                del live[idx]
        # an item the batch refused is judged on its own, so a neighbour can never make it fail
        for idx in list(errors):
            why = _check_alone(folder, programs[idx])
            if not why:
                live[idx] = programs[idx]
                del errors[idx]
            else:
                errors[idx] = why
        # Some errors only come with code generation (deny-by-default lints such as `unconditional_panic` on a constant
        # index out of range or a constant division by zero): a build that fails names its items, they are compile
        # errors (the "Run it" build, -O, refuses them too, or the debug build does), and the builds start again.
        builds = (("debug", ["-C", "debug-assertions=on", "-C", "overflow-checks=on"]), ("release", ["-O"]))
        outs: list[dict[int, str]] = []
        for _ in range(12):
            if not live:
                break
            live = dict(sorted(live.items()))
            source, spans = _crate(live)
            (folder / "main.rs").write_text(source, encoding="utf-8")
            outs, refused = [], {}
            for name, flags in builds:
                exe = folder / f"{name}.exe"
                rc, text = _rustc([*EDITION, *flags, "-o", str(exe), str(folder / "main.rs")], folder)
                if rc != 0:
                    for m in _DIAG.finditer(text):
                        idx = _which_item(spans, int(m.group(2)))
                        if idx is not None:
                            refused.setdefault(idx, f"{m.group(1).strip()} ({name} build)")
                    if not refused:
                        raise RuntimeError(f"the checked batch failed its {name} build naming no item:\n" + text[-3000:])
                    break
                outs.append(_execute(exe, list(live)))
            if not refused:
                break
            for idx, why in refused.items():
                errors[idx] = why
                del live[idx]
        results: dict[int, RustRun] = {idx: RustRun(False, why) for idx, why in errors.items()}
        if live:
            for idx in live:
                (a, pa), (b, pb) = _value(outs[0][idx]), _value(outs[1][idx])
                if a != b:
                    results[idx] = RustRun(True, out=f"BUILDS DIFFER: debug {a!r}, release {b!r}", panicked=pa or pb)
                else:
                    results[idx] = RustRun(True, out=a, panicked=pa)
        return results
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def rust_results(programs: list[str]) -> list[RustRun]:
    """One RustRun per program, in order."""
    if not HAVE_RUSTC:
        raise RuntimeError("rustc is not installed")
    indexed = list(enumerate(programs))
    chunks = [dict(indexed[k:k + CHUNK]) for k in range(0, len(indexed), CHUNK)]
    out: dict[int, RustRun] = {}
    with ThreadPoolExecutor(WORKERS) as pool:
        for part in pool.map(_chunk, chunks):
            out.update(part)
    return [out[i] for i in range(len(programs))]


def rust_values(programs: list[str]) -> list[str]:
    return [r.value for r in rust_results(programs)]
