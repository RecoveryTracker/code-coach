"""The TypeScript oracle for Brain Drills: hold a batch of TypeScript snippets to the real `tsc --strict` and node.

Every item is its own MODULE file `itemN.ts` (the code + `export {};`, so two items may both declare `const total` or
`interface Point`), and the whole batch is ONE `tsc` program with the flags "Run it" uses (`--strict --target es2020
--module commonjs --skipLibCheck`), emitting even when some files have errors: an item whose file has an error is named
(`COMPILE ERROR: itemN.ts(2,7): error TS2322: ...`, the item's own line), the others are emitted. Then ONE node process
loads the emitted files one after the other, with `console.log` written into a buffer per item (through `util.format`,
which is what `console.log` prints with), and writes one JSON line per item: what it printed, or the error it threw.
An item that runs for ever is named (`HANG`), skipped (the runner takes the position to start from) and the rest run.

What a TypeScript item is (one rule, shared with "Run it" - `tsProgram` in web/src/lib/brainRound.ts - and the `check`
field): the program is `item.check`, or the prompt when `check` is empty, as a module of top-level statements. It prints
its own answer with `console.log`; the value is its standard output with the whitespace at both ends cut off. No
`await`, timers or promises (the runner does not wait for the event loop), no node typings (`require`, `process`).

    from tests.ts_oracle import ts_results, ts_values
    got = ts_values([item.check or item.prompt for item in items])

Without node and tsc (web/node_modules) `HAVE_TSC` is False and tests skip.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from code_coach import engine

NODE = engine._which("node")
TSC = engine._find_tsc()
HAVE_TSC = bool(NODE and TSC)
FLAGS = ("--strict", "--target", "es2020", "--module", "commonjs", "--skipLibCheck")
RUN_SECONDS = 30.0
_MODULE = re.compile(r"^\s*(import|export)\b", re.M)


def full_program(code: str) -> str:
    """The program "Run it" builds (tsProgram in brainRound.ts): the code as a module (`export {};` added)."""
    src = code.rstrip() + "\n"
    return src if _MODULE.search(src) else src + "export {};\n"


_as_module = full_program


@dataclass(frozen=True)
class TsRun:
    compiled: bool
    compile_error: str = ""
    out: str = ""
    threw: bool = False

    @property
    def value(self) -> str:
        if not self.compiled:
            return "COMPILE ERROR: " + self.compile_error
        return self.out

    @property
    def verdict(self) -> str:
        """For a fine-or-error question: "error" when tsc refuses it or it throws, else "fine"."""
        return "error" if (not self.compiled or self.threw) else "fine"


_RUNNER = r'''
const util = require("util");
const fs = require("fs");
const path = require("path");
const [dir, start] = [process.argv[2], Number(process.argv[3])];
const order = JSON.parse(fs.readFileSync(path.join(dir, "order.json"), "utf8"));
const realLog = console.log;
for (let pos = start; pos < order.length; pos++) {
  const id = order[pos];
  const buf = [];
  console.log = (...a) => { buf.push(util.format(...a)); };
  let error = null;
  fs.writeSync(1, JSON.stringify({ start: id }) + "\n");
  try {
    require(path.join(dir, "out", "item" + id + ".js"));
  } catch (e) {
    error = ((e && e.name) || "Error") + ": " + ((e && e.message) || String(e));
  }
  console.log = realLog;
  fs.writeSync(1, JSON.stringify({ id, out: buf.join("\n"), error }) + "\n");
}
'''

_DIAG = re.compile(r"^(?:.*?[\\/])?item(\d+)\.ts\((\d+),(\d+)\): error (TS\d+): (.*)$", re.M)


def ts_results(programs: list[str]) -> list[TsRun]:
    """One TsRun per program, in order."""
    if not HAVE_TSC:
        raise RuntimeError("TypeScript needs node and web/node_modules/typescript")
    folder = Path(tempfile.mkdtemp(prefix="cc_ts_oracle_"))
    try:
        files = []
        for i, code in enumerate(programs):
            f = folder / f"item{i}.ts"
            f.write_text(_as_module(code), encoding="utf-8")
            files.append(f.name)
        errors: dict[int, str] = {}
        # tsc reports NO type errors at all while any file of the program has a syntax error (TS1xxx), so files with
        # syntax errors are taken out and the rest compiled again until the program parses. The file list goes in a
        # tsconfig.json: thousands of names overflow the Windows command line.
        while True:
            live = [f for i, f in enumerate(files) if i not in errors]
            config = {"compilerOptions": {"strict": True, "target": "es2020", "module": "commonjs",
                                          "skipLibCheck": True, "outDir": "out"}, "files": live}
            (folder / "tsconfig.json").write_text(json.dumps(config), encoding="utf-8")
            done = subprocess.run([NODE, str(TSC), "-p", "tsconfig.json"], cwd=folder, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=900)
            found: dict[int, str] = {}
            syntax = False
            for m in _DIAG.finditer(done.stdout + done.stderr):
                idx = int(m.group(1))
                syntax = syntax or int(m.group(4)[2:]) < 2000
                found.setdefault(idx, f"item{idx}.ts({m.group(2)},{m.group(3)}): error {m.group(4)}: {m.group(5).strip()}")
            if done.returncode != 0 and not found:
                raise RuntimeError("tsc failed naming no item:\n" + (done.stdout + done.stderr)[-3000:])
            if syntax:
                errors.update({i: why for i, why in found.items() if int(why.split(" error TS")[1][:4]) < 2000})
                continue
            errors.update(found)
            break
        order = [i for i in range(len(programs)) if i not in errors]
        (folder / "order.json").write_text(json.dumps(order), encoding="utf-8")
        (folder / "runner.js").write_text(_RUNNER, encoding="utf-8")
        got: dict[int, tuple[str, str | None]] = {}
        start = 0
        while start < len(order):
            try:
                run = subprocess.run([NODE, "runner.js", str(folder), str(start)], cwd=folder, capture_output=True,
                                     timeout=RUN_SECONDS)
                text = run.stdout.decode("utf-8", "replace")
            except subprocess.TimeoutExpired as e:
                text = (e.stdout or b"").decode("utf-8", "replace")
            for line in text.splitlines():
                rec = json.loads(line)
                if "id" in rec:
                    got[rec["id"]] = (rec["out"], rec["error"])
            nxt = start
            while nxt < len(order) and order[nxt] in got:
                nxt += 1
            if nxt >= len(order):
                break
            got[order[nxt]] = ("HANG", "HANG")
            start = nxt + 1
        out = []
        for i in range(len(programs)):
            if i in errors:
                out.append(TsRun(False, errors[i]))
                continue
            printed, error = got[i]
            if error:
                out.append(TsRun(True, out=("THROWS " + error) if printed.strip() == "" else f"{printed.strip()} THROWS {error}",
                                 threw=True))
            else:
                out.append(TsRun(True, out=printed.strip()))
        return out
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def ts_values(programs: list[str]) -> list[str]:
    return [r.value for r in ts_results(programs)]
