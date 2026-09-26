"""The Flutter questions.

Two halves. The content rules hold everywhere: ids, choices, levels, a
real explanation. The Flutter half only runs where a Flutter SDK is
installed, and it is the one the rest rests on:

- `test_every_snippet_analyzes_clean` puts every snippet into a
  throwaway Flutter project and runs the analyzer over it. An error or
  a warning fails; lints (infos) do not, because a few snippets are
  deliberately not written the way the linter wants — the non-const
  Label is the point of its question.
- `test_the_answer_is_what_flutter_does` runs each question's `verify`
  body as a `testWidgets` test with `flutter test`, so an answer that
  stops being true of the framework fails here.

The project lives in the system temp directory and is reused from run
to run — `flutter create` and the first compile are the slow part, and
neither needs repeating. Snippet and test files in it are rewritten
every run, so it never checks yesterday's code.
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from code_coach.flutter import WidgetQuestion, families, question, questions


# -- finding Flutter ------------------------------------------


def _flutter() -> Path | None:
    """The flutter launcher, or None where there is no SDK."""
    names = ("flutter.bat", "flutter") if os.name == "nt" else ("flutter",)
    roots = []
    if os.environ.get("FLUTTER_ROOT"):
        roots.append(Path(os.environ["FLUTTER_ROOT"]))
    found = shutil.which("flutter")
    if found:
        roots.append(Path(found).resolve().parent.parent)
    roots.append(Path("C:/Flutter/flutter"))
    for root in roots:
        for name in names:
            candidate = root / "bin" / name
            if candidate.is_file():
                return candidate
    return None


FLUTTER = _flutter()


def _dart() -> Path:
    assert FLUTTER is not None
    exe = "dart.exe" if os.name == "nt" else "dart"
    return FLUTTER.parent / "cache" / "dart-sdk" / "bin" / exe


def _file_stem(q: WidgetQuestion) -> str:
    return q.id.replace("-", "_")


@functools.lru_cache(maxsize=None)
def _project() -> Path:
    """The throwaway project, created once and reused across runs."""
    home = Path(tempfile.gettempdir()) / "code_coach_flutter_questions"
    project = home / "fq"
    if not (project / ".dart_tool" / "package_config.json").is_file():
        home.mkdir(parents=True, exist_ok=True)
        base = [str(FLUTTER), "create", "--platforms=windows", "-t", "app",
                "--project-name", "fq"]
        done = subprocess.run(
            [*base, "--offline", str(project)],
            capture_output=True, text=True, timeout=900)
        if done.returncode != 0:
            done = subprocess.run(
                [*base, str(project)],
                capture_output=True, text=True, timeout=900)
        if done.returncode != 0:
            raise RuntimeError(f"flutter create failed:\n{done.stdout}\n{done.stderr}")

    lib, test = project / "lib" / "q", project / "test" / "q"
    for folder in (lib, test):
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
    for q in questions():
        stem = _file_stem(q)
        (lib / f"{stem}.dart").write_text(q.code + "\n", encoding="utf-8")
        if q.verify:
            assert "'''" not in q.answer, q.id
            body = "\n".join("    " + line for line in q.verify.split("\n"))
            (test / f"{stem}_test.dart").write_text(
                "// ignore_for_file: unused_import\n"
                "import 'package:flutter/material.dart';\n"
                "import 'package:flutter_test/flutter_test.dart';\n"
                f"import 'package:fq/q/{stem}.dart';\n\n"
                "// The answer the question marks right. The body holds it\n"
                "// to what Flutter does, so a wrong answer fails here.\n"
                f"const answer = r'''{q.answer}''';\n\n"
                "void main() {\n"
                f"  testWidgets('{q.id}', (tester) async {{\n"
                f"{body}\n"
                "  });\n"
                "}\n",
                encoding="utf-8")
    return project


@functools.lru_cache(maxsize=None)
def _analysis() -> dict[str, list[str]]:
    """Errors and warnings per snippet file stem. Infos are left out."""
    project = _project()
    done = subprocess.run(
        [str(_dart()), "analyze", "--format=machine", "lib/q", "test/q"],
        cwd=project, capture_output=True, text=True, timeout=900)
    problems: dict[str, list[str]] = {}
    for line in (done.stdout + "\n" + done.stderr).splitlines():
        parts = line.split("|")
        if len(parts) < 8 or parts[0] not in ("ERROR", "WARNING"):
            continue
        stem = Path(parts[3]).stem.removesuffix("_test")
        problems.setdefault(stem, []).append(
            f"{Path(parts[3]).name}:{parts[4]} {parts[2]}: {parts[7]}")
    return problems


@functools.lru_cache(maxsize=None)
def _verification() -> tuple[dict[str, str], str]:
    """Each verified question's result from `flutter test`, by id, and
    the raw output for when something needs explaining."""
    project = _project()
    done = subprocess.run(
        [str(FLUTTER), "test", "--no-pub", "--reporter", "json", "test/q"],
        cwd=project, capture_output=True, text=True, timeout=1800,
        encoding="utf-8", errors="replace")
    names: dict[int, str] = {}
    results: dict[str, str] = {}
    errors: dict[int, list[str]] = {}
    for line in done.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if kind == "testStart":
            test = event.get("test", {})
            names[test.get("id")] = test.get("name", "")
        elif kind == "error":
            errors.setdefault(event.get("testID"), []).append(
                str(event.get("error", "")))
        elif kind == "print":
            # flutter_test prints the failed expectation here, and the
            # error event itself only says "see the logs above".
            errors.setdefault(event.get("testID"), []).append(
                str(event.get("message", "")))
        elif kind == "testDone" and not event.get("hidden"):
            tid = event.get("testID")
            result = event.get("result", "")
            if result != "success":
                result += ": " + " | ".join(errors.get(tid, []))
            results[names.get(tid, "")] = result
    return results, done.stdout[-4000:] + done.stderr[-4000:]


# -- content --------------------------------------------------


class ShapeTests(unittest.TestCase):
    def test_there_are_sixteen_in_three_or_four_families(self) -> None:
        self.assertEqual(len(questions()), 16)
        self.assertIn(len(families()), (3, 4))
        for family in families():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(questions(family)), 3)

    def test_ids_are_unique(self) -> None:
        ids = [q.id for q in questions()]
        self.assertEqual(len(ids), len(set(ids)))
        for q in questions():
            with self.subTest(question=q.id):
                self.assertTrue(q.id.startswith("fl-"))
                self.assertIs(question(q.id), q)
        self.assertIsNone(question("no-such-question"))

    def test_the_snippets_are_short_whole_libraries(self) -> None:
        for q in questions():
            with self.subTest(question=q.id):
                self.assertGreaterEqual(len(q.numbered), 8)
                self.assertLessEqual(len(q.numbered), 30)
                self.assertTrue(
                    q.code.startswith("import 'package:flutter/"),
                    "a snippet is a whole library, imports included")
                self.assertNotIn("\t", q.code)
                self.assertEqual(q.code, q.code.strip("\n"))

    def test_the_ranking_was_done(self) -> None:
        from code_coach.flutter.content import LAYOUT, LIFECYCLE, STATE, TREE

        for group in (TREE, LAYOUT, STATE, LIFECYCLE):
            family = group[0].family
            with self.subTest(family=family):
                written = [q.level for q in group]
                self.assertEqual(written, sorted(written),
                                 "written easiest first")
                self.assertTrue(all(q.family == family for q in group))
                levels = [q.level for q in questions(family)]
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)
                for level in levels:
                    self.assertIn(level, range(1, 6))

    def test_every_question_is_a_question(self) -> None:
        for q in questions():
            with self.subTest(question=q.id):
                self.assertTrue(q.question.strip().endswith("?"))
                self.assertTrue(q.name.strip())

    def test_the_why_is_an_explanation(self) -> None:
        """Right by luck teaches nothing, so the why has to carry the
        rule — a sentence or two of it at least."""
        for q in questions():
            with self.subTest(question=q.id):
                self.assertGreaterEqual(len(q.why), 200)
                self.assertGreaterEqual(q.why.count(". "), 2)


class ChoiceTests(unittest.TestCase):
    def test_there_is_something_to_choose_between(self) -> None:
        for q in questions():
            with self.subTest(question=q.id):
                self.assertGreaterEqual(len(q.choices), 3)
                self.assertEqual(len(q.choices), len(q.decoys) + 1)

    def test_the_answer_is_among_them(self) -> None:
        for q in questions():
            with self.subTest(question=q.id):
                self.assertIn(q.answer, q.choices)

    def test_the_decoys_are_not_the_answer(self) -> None:
        for q in questions():
            with self.subTest(question=q.id):
                self.assertNotIn(q.answer, q.decoys)
                self.assertEqual(len(set(q.decoys)), len(q.decoys))
                for d in q.decoys:
                    self.assertNotEqual(d.strip().lower(),
                                        q.answer.strip().lower())

    def test_the_order_gives_nothing_away(self) -> None:
        for q in questions():
            with self.subTest(question=q.id):
                self.assertEqual(list(q.choices), sorted(q.choices))
        firsts = sum(1 for q in questions() if q.choices[0] == q.answer)
        self.assertLess(firsts, len(questions()) * 0.6)

    def test_the_answer_is_not_always_the_longest(self) -> None:
        """The oldest tell in multiple choice: the careful, qualified
        option is the right one."""
        longest = sum(
            1 for q in questions()
            if all(len(q.answer) > len(d) for d in q.decoys))
        self.assertLessEqual(longest, len(questions()) // 2,
                             f"{longest} answers are the longest choice")

    def test_most_answers_are_held_to_flutter(self) -> None:
        verified = [q for q in questions() if q.verify]
        self.assertGreaterEqual(len(verified), 12)


# -- against Flutter itself -----------------------------------


@unittest.skipIf(FLUTTER is None, "Flutter is not installed here")
class FlutterTests(unittest.TestCase):
    def test_every_snippet_analyzes_clean(self) -> None:
        problems = _analysis()
        for q in questions():
            with self.subTest(question=q.id):
                self.assertEqual(problems.get(_file_stem(q), []), [])

    def test_the_answer_is_what_flutter_does(self) -> None:
        results, tail = _verification()
        for q in questions():
            if not q.verify:
                continue
            with self.subTest(question=q.id):
                self.assertIn(q.id, results, f"never ran:\n{tail}")
                self.assertEqual(results[q.id], "success")


if __name__ == "__main__":
    unittest.main()
