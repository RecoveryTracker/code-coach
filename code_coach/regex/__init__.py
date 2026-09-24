"""Regex: write a pattern that finds these and leaves those alone.

The shape is RegexOne's, which is the right one: a handful of strings
the pattern must match, a handful it must skip, and sometimes a piece it
has to capture. A regular expression is a claim about which strings are
in and which are out, so a task that shows both sides is a task that
tests the claim. The examples here are this project's own.

Where the answers come from
---------------------------
The engine. Your pattern is run by the real regex engine of the language
you are learning - Python's re, or JavaScript's RegExp - never by a
translation of it, because the two differ in the corners and a pattern
that works in one is not promised to work in the other.

And it runs in a separate process, through the same runner as every
other exercise, with the same timeout. That matters more here than
anywhere: a pattern like (a+)+$ against a long string of a's takes
exponential time in a backtracking engine, and running it inside the
server would let one bad pattern freeze the app. In a child process it
is just a timeout.

The rules the suite holds every task to
---------------------------------------
* The reference pattern passes in both engines, so the task is about
  regular expressions and not about one engine's quirks.
* There is something to skip. A task with nothing on the skip side is
  passed by .* and teaches nothing.
* There is a pitfall - the tempting wrong pattern, such as the one
  without the anchor - and it must fail. That is what proves the task
  actually tests the idea it is named after, rather than being passable
  by something that misses the point.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

#: A pattern longer than this is not an answer, it is a list.
MAX_PATTERN = 300


@dataclass(frozen=True)
class RegexTask:
    """One pattern to write."""

    id: str
    title: str
    family: str
    level: int
    #: What to do, in one or two sentences.
    brief: str
    #: The pattern must be found somewhere in each of these.
    match: tuple[str, ...]
    #: The pattern must not be found anywhere in these.
    skip: tuple[str, ...]
    #: A worked answer, shown on request. Checked in both engines.
    answer: str
    #: The tempting wrong answers, which must fail. At least one.
    pitfalls: tuple[str, ...]
    #: A nudge that is not the answer.
    hint: str
    #: The idea this task is about, shown once it passes.
    lesson: str
    #: For capture tasks: (string, what group 1 should be). Every
    #: string here must also be in `match`.
    capture: tuple[tuple[str, str], ...] = field(default_factory=tuple)


# ── Running a pattern in a real engine ───────────────────────

MARKER = "<<<REGEX>>>"

PY_DRIVER = """
import json, re, sys
data = json.loads({payload!r})
try:
    pattern = re.compile(data["pattern"])
except re.error as exc:
    print({marker!r} + json.dumps({{"error": str(exc)}}))
    sys.exit(0)
out = []
for text in data["strings"]:
    m = pattern.search(text)
    group = None
    if m is not None and pattern.groups >= 1:
        group = m.group(1)
    out.append({{"found": m is not None, "group": group}})
print({marker!r} + json.dumps({{"results": out, "groups": pattern.groups}}))
"""

JS_DRIVER = """
const data = JSON.parse({payload});
let pattern;
try {{
  pattern = new RegExp(data.pattern);
}} catch (exc) {{
  console.log({marker} + JSON.stringify({{ error: String(exc.message) }}));
  process.exit(0);
}}
const groups = new RegExp("(?:" + data.pattern + ")|").exec("").length - 1;
const out = data.strings.map((text) => {{
  const m = pattern.exec(text);
  const group = m !== null && groups >= 1 && m[1] !== undefined ? m[1] : null;
  return {{ found: m !== null, group }};
}});
console.log({marker} + JSON.stringify({{ results: out, groups }}));
"""


def engine_for(language: str) -> str:
    """Which regex engine a language's learner is checked against.

    JavaScript and TypeScript share RegExp. Everything else is checked
    with Python's re, and the screen says so rather than pretending the
    pattern was tried in, say, Rust's regex crate.
    """
    return "javascript" if language in ("javascript", "typescript") else "python"


@dataclass(frozen=True)
class Verdict:
    """What one pattern did against one task."""

    passed: bool
    #: Compile error, timeout or crash - anything that stopped it running.
    broke: str = ""
    #: One row per string, in match-then-skip order:
    #: (string, should_match, found, group, want_group, right)
    rows: tuple[tuple, ...] = ()


def run_pattern(pattern: str, strings: list[str], engine: str) -> dict:
    """Search each string with the pattern in a real engine, in a child
    process. Returns {"results": [...], "groups": n} or {"error": text}.
    """
    from code_coach.engine import run_code

    payload = json.dumps({"pattern": pattern, "strings": list(strings)})
    if engine == "javascript":
        code = JS_DRIVER.format(payload=json.dumps(payload), marker=json.dumps(MARKER))
    else:
        code = PY_DRIVER.format(payload=payload, marker=MARKER)
    out, err, exit_code = run_code(code, language=engine)
    for line in out.splitlines():
        if line.startswith(MARKER):
            return json.loads(line[len(MARKER):])
    if "timed out" in (err or "").lower() or exit_code in (124, -9):
        # Two causes look identical from here, and only one is the
        # pattern's fault. It first said "your pattern is backtracking",
        # and was caught saying so about a correct answer on a machine
        # busy running the test suite - which would send a learner
        # looking for a bug that is not there. So it names both.
        return {"error": "Checking that took too long. If the pattern has "
                         "nested repeats like (a+)+, it can backtrack without "
                         "end - otherwise the computer was just busy, so try "
                         "again."}
    return {"error": (err or "The pattern did not run.").strip()[-300:]}


def check(task: RegexTask, pattern: str, engine: str) -> Verdict:
    """Judge a pattern against a task, in the given engine."""
    if not pattern:
        return Verdict(passed=False, broke="Write a pattern first.")
    if len(pattern) > MAX_PATTERN:
        return Verdict(passed=False, broke="That pattern is longer than any "
                                           "answer needs to be.")
    captures = dict(task.capture)
    strings = list(task.match) + list(task.skip)
    got = run_pattern(pattern, strings, engine)
    if "error" in got:
        return Verdict(passed=False, broke=got["error"])
    if captures and got.get("groups", 0) < 1:
        # A capture task answered with no group at all: say so plainly
        # rather than marking every capture row wrong without a reason.
        return Verdict(
            passed=False,
            broke="This one asks you to capture a part - put it in "
                  "parentheses so it becomes group 1.",
        )
    rows = []
    for text, result in zip(strings, got["results"]):
        should = text in task.match
        found = bool(result["found"])
        group = result.get("group")
        want_group = captures.get(text) if should else None
        right = found == should and (want_group is None or group == want_group)
        rows.append((text, should, found, group, want_group, right))
    return Verdict(passed=all(r[5] for r in rows), rows=tuple(rows))


# ── The collection ───────────────────────────────────────────


def tasks(family: str | None = None) -> tuple[RegexTask, ...]:
    """Every task in the order written, which is easiest first."""
    from code_coach.regex.content import TASKS

    if family is None:
        return TASKS
    return tuple(t for t in TASKS if t.family == family)


def families() -> tuple[str, ...]:
    seen: list[str] = []
    for t in tasks():
        if t.family not in seen:
            seen.append(t.family)
    return tuple(seen)


def task(task_id: str) -> RegexTask | None:
    return next((t for t in tasks() if t.id == task_id), None)
