"""Kata: write a function, and it gets called with inputs you did not choose.

Everything else in this app asks a program to print something and compares
what came out. That is the right check for a drill — there are several
ways to print the numbers one to five and all of them should pass — but it
trains only one thing, because the program is only ever run on the single
input the prompt named.

Codewars and freeCodeCamp work the other way round, and the difference is
not cosmetic. A function called with ten inputs is a function whose empty
list, whose single element, whose zero and whose negative all have to
work. That is the part of problem solving a print-based exercise cannot
reach: you never meet the edge case, because you never run the edge case.

So a kata is a signature, a sentence, and a set of cases. Your code is run
with a driver appended that calls the function once per case and reports
each one. A failure says which input broke it, which is the only feedback
that actually moves you forward.

Two rules hold this together, and both are the ones the workbook already
lives by.

The expected answer is computed, never written down. Each kata carries a
reference solution in Python, and the cases carry only inputs — the
answers come from running the reference. Writing out `digital_root(99) ==
9` by hand for twelve cases is twelve chances to be wrong about the thing
you are marking against.

And the reference is executed, not trusted. The suite runs every kata's
own solution through the same driver a student's would go through, so a
reference that does not actually pass its own cases fails the build
rather than quietly marking correct answers wrong.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Kata:
    """One function to write, and the inputs it will be called with."""

    id: str
    #: The function the student must define.
    name: str
    #: What it has to do, in one sentence.
    brief: str
    #: The parameters, for the signature shown on screen.
    params: tuple[str, ...]
    #: The inputs. Each is the full argument tuple for one call.
    cases: tuple[tuple, ...]
    #: The answer, computed rather than written down. Takes the same
    #: arguments as the function being asked for.
    solve: Callable[..., Any]
    #: A worked example, shown before the first attempt.
    example: str = ""
    #: Which family this belongs to, for grouping on screen.
    family: str = ""
    #: Which language the student writes in.
    #:
    #: `solve` stays Python whatever this says, because it is the oracle
    #: rather than the answer: the expected values are numbers, strings
    #: and lists, which mean the same thing in both languages, so one
    #: implementation of the truth means the hand-written checks guard
    #: every language at once. What changes is the driver the code runs
    #: with, and which source Show answer hands over.
    language: str = "python"
    #: The worked answer in JavaScript, for a kata written in it.
    #:
    #: Checked by running rather than by being read: the suite puts this
    #: through the same driver a student's code goes through, which is
    #: also what proves it agrees with the Python oracle.
    js_answer: str = ""
    #: For Dart: one type per parameter, like "List<String>", and the
    #: return type. Dart is typed, so the driver has to turn the JSON
    #: inputs into those types - a List<dynamic> handed to a function
    #: that takes List<String> is a type error before a line of the
    #: student's code runs. Left empty, the arguments go in untyped.
    types: tuple[str, ...] = ()
    returns: str = ""
    #: The worked answer in Dart, for a kata written in it. Checked the
    #: same way as js_answer: run through the driver against the oracle.
    dart_answer: str = ""
    #: How hard this one is, 1 to 5, and the order a family is read in.
    #:
    #: A judgement rather than anything derivable — there is no measure
    #: of difficulty to compute — so what the suite can check is that
    #: the judgement was made: a family whose every kata is the same
    #: level is one where the field is saying nothing, and the order
    #: those katas appear in is then whatever order they were written,
    #: which is what this exists to stop.
    level: int = 2
    #: A hint that costs nothing to read and is not the answer.
    hint: str = ""
    #: Why this kata has no structurally awkward input, and what stands
    #: in for one.
    #:
    #: The suite insists every kata try something degenerate — an empty
    #: input, a single item, a zero, a negative — because a set of ten
    #: comfortable middles teaches nothing a printed exercise did not.
    #: Some shapes cannot have one: a function taking a clock time never
    #: gets an empty string, and one that swaps a pair always gets
    #: exactly two things. For those the boundary is in the meaning
    #: rather than the size — midnight, the wrap past a day — and this
    #: is where that has to be said out loud. Left empty, the structural
    #: rule applies and is enforced.
    edge_note: str = ""
    #: Whether this function is allowed to change what it was handed.
    #:
    #: Almost none are, and a function that quietly modifies its
    #: argument is one of the harder bugs to see: the value it returns
    #: is right, and the damage is somewhere else entirely. The marker
    #: compares the arguments before and after the call, so that damage
    #: fails the case rather than going unnoticed.
    mutates: bool = False
    #: Code that is already in the box and already wrong.
    #:
    #: An empty `start` is a kata: you write the function. A filled one
    #: is a broken exercise: the function is written, it fails some of
    #: its cases, and the job is to find out why. The machinery is
    #: identical, which is the point — the driver, the marker and the
    #: screen are the ones already in use and already tested.
    start: str = ""
    #: What the bug was, shown once it passes. Reading the name of your
    #: own mistake after finding it is what makes it the last time.
    bug: str = ""
    #: A few answers written out by hand, as (arguments, answer).
    #:
    #: These exist because the obvious test does not work. Running the
    #: reference against expectations computed from the reference proves
    #: only that it agrees with itself — it passes however wrong the
    #: reference is, which was discovered by breaking one and watching
    #: the suite stay green. An answer typed out by a person is the only
    #: thing in the file that did not come from the code being checked.
    checks: tuple[tuple[tuple, Any], ...] = field(default_factory=tuple)
    #: For a Change it drill: what the program does today, shown above
    #: the request. A change request means nothing without it.
    was: str = ""
    #: For a Change it drill: the old requirement, as an oracle. The
    #: starting code must pass every case under this - that is what
    #: makes it working code to change rather than broken code to fix.
    before: Callable[..., Any] | None = None
    #: For a Change it drill: the start with the change made, which is
    #: what Show answer hands over. Shown instead of `solve` because the
    #: lesson is the edit, and `solve` is written for the oracle, not
    #: as the smallest change to the code in the box.
    after: str = ""
    #: For a Change it drill: what the change was and why it had to be
    #: that way, shown once it passes - the same role `bug` plays for a
    #: broken one.
    change: str = ""

    @property
    def signature(self) -> str:
        """The line the screen shows and the box opens on.

        In the language being written, obviously — but it was not
        obvious until a JavaScript kata opened on `def uniqueOf(items):`
        and the box had to be emptied before a word could be typed.
        """
        joined = ", ".join(self.params)
        if self.language == "dart":
            typed = ", ".join(
                f"{kind} {name}" for kind, name in zip(self.types, self.params))
            return f"{self.returns or 'dynamic'} {self.name}({typed or joined}) {{"
        if self.language == "javascript":
            return f"function {self.name}({joined}) {{"
        return f"def {self.name}({joined}):"

    def answer(self, args) -> Any:
        """What the reference gives for one case.

        The arguments are copied first. A reference that appends to a
        list it was handed would otherwise change the kata's own cases
        as it went — asking twice gave different answers and the second
        set was nonsense, which is how this was found.
        """
        import copy

        return self.solve(*copy.deepcopy(tuple(args)))

    def expected(self) -> tuple[Any, ...]:
        """What the reference says each case should produce."""
        return tuple(self.answer(case) for case in self.cases)

    def reference(self) -> str:
        """The reference solution, as the student would write it.

        Renamed from the private name it has in the content file to the
        one the kata asks for, so what is shown is code that would pass
        if you typed it in. The suite runs this exact string through the
        driver rather than re-deriving it, which is what stops the
        answer on screen drifting from the answer that is checked.
        """
        import inspect
        import textwrap

        if self.after:
            return self.after.strip()
        if self.language == "javascript":
            return self.js_answer.strip()
        if self.language == "dart":
            return self.dart_answer.strip()
        source = textwrap.dedent(inspect.getsource(self.solve)).strip()
        return source.replace(
            f"def {self.solve.__name__}", f"def {self.name}", 1)


# ── Running one ──────────────────────────────────────────────
#
# The student's code and a driver, in one file. Nothing new executes it:
# this goes through the same runner as everything else, which means the
# same timeout, the same output cap and the same lack of surprises.


DRIVER = '''

# ── the marker ───────────────────────────────────────────────
import json as _json


def _main() -> None:
    # Naming it something else is a different mistake from getting it
    # wrong, and reporting it as ten failed cases sends you looking in
    # the wrong place entirely.
    target = globals().get("{name}")
    if not callable(target):
        print("<<<KATANAME>>>")
        return
    cases = _json.loads({cases!r})
    results = []
    for args in cases:
        # What the arguments looked like before the call, so a function
        # that changes them can be caught. The value it returns can be
        # perfectly right while the caller's list has been wrecked.
        before = _json.dumps(args)
        try:
            got = {name}(*args)
        except Exception as error:          # noqa: BLE001 - reported, not raised
            results.append({{"error": f"{{type(error).__name__}}: {{error}}"}})
            continue
        changed = _json.dumps(args) != before
        try:
            _json.dumps(got)
        except TypeError:
            got = repr(got)
        results.append({{"got": got, "changed": changed}})
    print("<<<KATA>>>" + _json.dumps(results))


_main()
'''


#: The same driver in JavaScript, for the katas written in it.
#:
#: Deliberately the same shape: the same marker, the same one entry per
#: case, the same record of what the arguments looked like before the
#: call. That means `judge` below reads both without knowing which
#: language produced the line, and the two cannot drift apart in what
#: they report.
JS_DRIVER = '''

// ── the marker ───────────────────────────────────────────────
(function () {{
  // Naming it something else is a different mistake from getting it
  // wrong, and reporting it as ten failed cases sends you looking in
  // the wrong place.
  if (typeof {name} !== "function") {{
    console.log("<<<KATANAME>>>");
    return;
  }}
  const cases = JSON.parse({cases!r});
  const results = [];
  for (const args of cases) {{
    const before = JSON.stringify(args);
    let got;
    try {{
      got = {name}(...args);
    }} catch (error) {{
      results.push({{ error: error.constructor.name + ": " + error.message }});
      continue;
    }}
    const changed = JSON.stringify(args) !== before;
    // undefined has no JSON spelling and would vanish from the object
    // entirely, which reads downstream as "no answer given" rather than
    // as the answer being undefined. null is the nearest honest thing
    // and matches what Python's None becomes.
    if (got === undefined) got = null;
    try {{
      JSON.stringify(got);
    }} catch (error) {{
      got = String(got);
    }}
    results.push({{ got: got, changed: changed }});
  }}
  console.log("<<<KATA>>>" + JSON.stringify(results));
}})();
'''


#: The same driver in Dart. Same marker, same one entry per case, same
#: before-and-after check on the arguments, so `judge` reads it without
#: knowing which language wrote the line.
#:
#: Two things differ, both because Dart is compiled and typed. The
#: function is called by name directly, so a missing one is a compile
#: error rather than a check at run time - `judge` recognises that
#: error and reports it the same way. And each argument is converted
#: from JSON into its declared type first.
DART_DRIVER = """

// ── the marker ───────────────────────────────────────────────
void main() {{
  final cases = _kataJson.jsonDecode(r'''{cases}''') as List;
  final results = <Object?>[];
  for (final raw in cases) {{
    final args = raw as List;
{convert}
    final before = _kataJson.jsonEncode([{names}]);
    Object? got;
    try {{
      got = {name}({names});
    }} catch (error) {{
      // Most Dart errors already start with their type ("FormatException: ...");
      // some do not ("Bad state: No element"). Name it only when missing.
      final text = '$error';
      final kind = '${{error.runtimeType}}';
      results.add({{'error': text.startsWith(kind) ? text : '$kind: $text'}});
      continue;
    }}
    final changed = _kataJson.jsonEncode([{names}]) != before;
    try {{
      _kataJson.jsonEncode(got);
    }} catch (_) {{
      got = got.toString();
    }}
    results.add({{'got': got, 'changed': changed}});
  }}
  print('<<<KATA>>>' + _kataJson.jsonEncode(results));
}}
"""

#: Put on the same line as the student's first line, not above it, so
#: the line numbers in Dart's errors are the ones in the box.
DART_IMPORT = "import 'dart:convert' as _kataJson; "


def _dart_value(kind: str, expr: str) -> str:
    """A Dart expression turning decoded JSON `expr` into type `kind`."""
    kind = kind.strip()
    if kind in ("int", "String", "bool", "num"):
        return f"({expr} as {kind})"
    if kind == "double":
        return f"({expr} as num).toDouble()"
    if kind.startswith("List<") and kind.endswith(">"):
        inner = _dart_value(kind[5:-1], "e")
        return f"({expr} as List).map((e) => {inner}).toList()"
    if kind.startswith("Map<String,") and kind.endswith(">"):
        inner = _dart_value(kind[len("Map<String,"):-1], "v")
        return f"({expr} as Map).map((k, v) => MapEntry(k as String, {inner}))"
    return expr


def _dart_harness(kata: Kata, code: str) -> str:
    cases = json.dumps([list(case) for case in kata.cases])
    names = [f"_arg{i}" for i in range(len(kata.params))]
    kinds = list(kata.types) + [""] * (len(names) - len(kata.types))
    convert = "\n".join(
        f"    final {n} = {_dart_value(k, f'args[{i}]')};"
        for i, (n, k) in enumerate(zip(names, kinds)))
    return DART_IMPORT + code.strip() + "\n" + DART_DRIVER.format(
        cases=cases, convert=convert, names=", ".join(names), name=kata.name)


def harness(kata: Kata, code: str) -> str:
    """The student's code with a driver appended."""
    if kata.language == "dart":
        return _dart_harness(kata, code)
    driver = JS_DRIVER if kata.language == "javascript" else DRIVER
    return code.rstrip() + "\n" + driver.format(
        cases=json.dumps([list(case) for case in kata.cases]),
        name=kata.name,
    )


MARKER = "<<<KATA>>>"
#: Printed instead when there is no function by that name at all.
NO_FUNCTION = "<<<KATANAME>>>"


@dataclass(frozen=True)
class CaseResult:
    """One call, and whether it was right."""

    args: tuple
    want: Any
    got: Any = None
    error: str = ""
    passed: bool = False
    #: The function changed what it was handed, and was not meant to.
    changed: bool = False


@dataclass(frozen=True)
class Outcome:
    """What happened when the whole kata ran."""

    results: tuple[CaseResult, ...] = field(default_factory=tuple)
    #: Set when the file did not run at all — a syntax error, or no such
    #: function. Distinct from failing cases, because the fix is
    #: different and telling someone "0 of 10 passed" when they have a
    #: typo in a keyword is not help.
    broke: str = ""

    @property
    def passed(self) -> bool:
        return bool(self.results) and all(r.passed for r in self.results)

    @property
    def count(self) -> int:
        return sum(1 for r in self.results if r.passed)


def judge(kata: Kata, stdout: str, stderr: str, exit_code: int) -> Outcome:
    """Read what the driver printed and say which cases passed.

    The marker matters. A student's own print statements are a normal part
    of working something out, and they land on stdout in front of the
    driver's line — so the results are taken from the marker onwards
    rather than from the whole of stdout.
    """
    if NO_FUNCTION in stdout or _dart_missing(kata, stdout, stderr):
        return Outcome(
            broke=f"there is no function called {kata.name} — check the "
                  f"name against the signature above")

    if MARKER not in stdout:
        detail = _tidy((stderr or stdout).strip())
        if exit_code != 0 and not detail:
            detail = f"the program exited with status {exit_code}"
        return Outcome(broke=detail or "nothing was printed by the marker")

    _, _, tail = stdout.partition(MARKER)
    try:
        raw = json.loads(tail.splitlines()[0])
    except (ValueError, IndexError):
        return Outcome(broke="the results could not be read")

    wants = kata.expected()
    if len(raw) != len(wants):
        return Outcome(broke="the run stopped part way through")

    results = []
    for args, want, entry in zip(kata.cases, wants, raw):
        if "error" in entry:
            results.append(
                CaseResult(args=args, want=want, error=entry["error"]))
            continue
        got = entry["got"]
        # Changing the caller's list is a failure even when the answer
        # is right — that is the whole shape of the bug, and a marker
        # that only reads return values cannot see it.
        changed = bool(entry.get("changed")) and not kata.mutates
        # JSON has one sequence type and Python has two, so a function
        # that correctly returns a tuple comes back as a list. Compare
        # the shapes rather than the containers.
        results.append(
            CaseResult(args=args, want=want, got=got, changed=changed,
                       passed=_same(got, want) and not changed))
    return Outcome(results=tuple(results))


def _dart_missing(kata: Kata, stdout: str, stderr: str) -> bool:
    """Dart's compile error for calling a function that is not there.

    Dart names it at compile time, so the check the other drivers make
    at run time happens here instead, from the error text.
    """
    if kata.language != "dart" or MARKER in stdout:
        return False
    return any(
        phrase in (stderr or "")
        for phrase in (f"Method not found: '{kata.name}'",
                       f"Undefined name '{kata.name}'"))


def _tidy(detail: str) -> str:
    """Take the temporary file out of a traceback.

    The file is a scratch path in the system temp directory, which is
    true and unhelpful: it is the student's own code, and naming it after
    wherever it happened to be written reads as though the error is
    somewhere they have never been.
    """
    import re

    # Python writes: File "<path>", line 4
    detail = re.sub(r'File "[^"]*", line', "Line", detail)

    # Node writes the path bare and then the line: <path>.js:39. Split
    # on the extension rather than on the first colon, because on
    # Windows the first colon is the drive letter — which is exactly
    # what the first attempt at this got wrong, leaving the whole path
    # on screen.
    out: list[str] = []
    for line in detail.splitlines():
        # Node's own frames, which are about Node and not about you.
        if line.lstrip().startswith("at "):
            continue
        # Dart's stack frames: "#0  main (file:///.../x.dart:5:3)".
        if re.match(r"\s*#\d+\s", line):
            continue
        # Dart puts the message on the same line as the place:
        # <path>.dart:3:10: Error: ... - keep the message.
        if ".dart:" in line:
            after = line.split(".dart:", 1)[1]
            found = re.match(r"(\d+):\d+: (.*)", after)
            if found:
                line = f"Line {found.group(1)}: {found.group(2)}"
                out.append(line)
                continue
        for suffix in (".js:", ".py:"):
            if suffix in line:
                after = line.split(suffix, 1)[1]
                number = after.split(":")[0].strip()
                line = f"Line {number}" if number.isdigit() else ""
                break
        out.append(line)
    return "\n".join(out).strip()


def _same(got: Any, want: Any) -> bool:
    """Whether two answers agree, allowing for the round trip through JSON."""
    if isinstance(want, tuple):
        want = list(want)
    if isinstance(want, list) and isinstance(got, list):
        return len(got) == len(want) and all(
            _same(g, w) for g, w in zip(got, want))
    if isinstance(want, dict) and isinstance(got, dict):
        return got.keys() == want.keys() and all(
            _same(got[k], want[k]) for k in want)
    # True == 1 in Python, and a function that returns 1 where the answer
    # is True is not right. The workbook has been bitten by exactly this
    # once already, in a Lisp verification harness.
    if isinstance(want, bool) != isinstance(got, bool):
        return False
    return got == want


def katas(family: str | None = None) -> tuple[Kata, ...]:
    from code_coach.kata.bugs import BUGS
    from code_coach.kata.bugs2 import BUGS2
    from code_coach.kata.content import KATAS
    from code_coach.kata.content2 import MORE
    from code_coach.engine import if_dart
    from code_coach.kata.dart_bugs import DART_BUGS
    from code_coach.kata.dart_katas import DART_KATAS
    from code_coach.kata.dart_katas2 import DART_KATAS_2
    from code_coach.kata.dart_modify import DART_MODIFY
    from code_coach.kata.js import JS_KATAS
    from code_coach.kata.js_odin import ODIN
    from code_coach.kata.js_stubs import STUBS
    from code_coach.kata.modify import JAVASCRIPT_MODIFY, PYTHON_MODIFY
    from code_coach.kata.projects import PROJECTS
    from code_coach.kata.projects2 import PROJECTS2

    everything = (
        KATAS + MORE + PROJECTS + PROJECTS2 + BUGS + BUGS2 + PYTHON_MODIFY
        + JS_KATAS + STUBS + ODIN + JAVASCRIPT_MODIFY
        + if_dart(DART_KATAS + DART_KATAS_2 + DART_BUGS + DART_MODIFY)
    )
    # Easiest first, and stable within a level so the order inside one
    # is still the order it was curated in rather than an accident of
    # sorting.
    everything = tuple(sorted(everything, key=lambda k: k.level))
    if family is None:
        return everything
    return tuple(k for k in everything if k.family == family)


def _in_file_order() -> tuple[Kata, ...]:
    from code_coach.kata.bugs import BUGS
    from code_coach.kata.bugs2 import BUGS2
    from code_coach.kata.content import KATAS
    from code_coach.kata.content2 import MORE
    from code_coach.engine import if_dart
    from code_coach.kata.dart_bugs import DART_BUGS
    from code_coach.kata.dart_katas import DART_KATAS
    from code_coach.kata.dart_katas2 import DART_KATAS_2
    from code_coach.kata.dart_modify import DART_MODIFY
    from code_coach.kata.js import JS_KATAS
    from code_coach.kata.js_odin import ODIN
    from code_coach.kata.js_stubs import STUBS
    from code_coach.kata.modify import JAVASCRIPT_MODIFY, PYTHON_MODIFY
    from code_coach.kata.projects import PROJECTS
    from code_coach.kata.projects2 import PROJECTS2

    return (
        KATAS + MORE + PROJECTS + PROJECTS2 + BUGS + BUGS2 + PYTHON_MODIFY
        + JS_KATAS + STUBS + ODIN + JAVASCRIPT_MODIFY
        + if_dart(DART_KATAS + DART_KATAS_2 + DART_BUGS + DART_MODIFY)
    )


def kata_language_of(family: str) -> str:
    """Which language a kata family is written in.

    A family never mixes them, so this belongs on the family rather
    than being repeated against every kata in it.
    """
    for k in _in_file_order():
        if k.family == family:
            return k.language
    return "python"


def languages() -> tuple[str, ...]:
    """Every language the katas are written in, in the order met."""
    seen: list[str] = []
    for k in _in_file_order():
        if k.language not in seen:
            seen.append(k.language)
    return tuple(seen)


def kata(kata_id: str) -> Kata | None:
    return next((k for k in katas() if k.id == kata_id), None)


def families() -> tuple[str, ...]:
    """The families, in the order they were written rather than sorted.

    Reading from `KATAS` and not from the sorted list: sorting by level
    interleaves the families, so the first kata seen would be whichever
    family happened to hold the easiest one.
    """
    seen: list[str] = []
    for k in _in_file_order():
        if k.family not in seen:
            seen.append(k.family)
    return tuple(seen)
