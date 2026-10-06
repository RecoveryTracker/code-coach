"""Canvas's To-do track: a web page instead of a canvas, checked in a browser.

A page step's check needs a real DOM, so here it runs where it runs in Code
Coach: in a sandboxed frame, in Chrome - headless, all the cases loaded at
once (dom.run_pages), in the very pages dom.page builds for the app. Held to
the usual three: each step's solution passes, its starter (the step before,
finished) fails, and the mistakes people really make at that step fail too,
with a message that names them; right programs written another way still
pass. The harness's own promises - line numbers, localStorage, a reload, a
form that would leave the page - are held to Chrome as well.

Without Chrome the browser tests skip; the rest still run.
"""

from __future__ import annotations

import re
import unittest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, step
from code_coach.canvas.content_dom import TODO_STEPS
from code_coach.canvas.dom import (
    CHECK_SANDBOX,
    PLAY_SANDBOX,
    check_pages,
    find_chrome,
    harness_source,
    page,
    run_pages,
    source_html,
)

HAS_CHROME = find_chrome() is not None


def _by_id(step_id: str):
    found = step(step_id)
    assert found is not None, step_id
    return found


def _apply(code: str, swaps: list[tuple[str, str]]) -> str:
    for old, new in swaps:
        assert code.count(old) == 1, f"not exactly once: {old!r}"
        code = code.replace(old, new)
    return code


def _line_of(code: str, text: str) -> int:
    """The 1-based line of `code` that holds `text`."""
    lines = code.split("\n")
    found = [i for i, line in enumerate(lines) if text in line]
    assert len(found) == 1, text
    return found[0] + 1


_TOGGLE_EACH = """
const items = document.querySelectorAll('#list li');
items.forEach((item) => {
  item.addEventListener('click', () => {
    item.classList.toggle('done');
  });
});
"""

_DELETE_EACH = """document.querySelectorAll('.delete').forEach((button) => {
  button.addEventListener('click', () => {
    button.closest('li').remove();
  });
});
"""

#: Wrong programs, each a real mistake at that step: (changes, words the
#: message must contain). The check must fail them all.
MISTAKES: dict[str, list[tuple[list[tuple[str, str]], str]]] = {
    "todo-01-text": [
        ([("title.textContent = 'To-do';", "title.textContent == 'To-do';")], "still says"),
        # No #: that's the <title> in the <head>, not the heading.
        ([("document.querySelector('#title')", "document.querySelector('title')")], "still says"),
        ([("document.querySelector('#title')", "document.querySelector('.title')")], "querySelector found nothing"),
    ],
    "todo-02-classes": [
        ([("first.classList.add('done');", "first.classList.add('.done');")], "no dot"),
        ([("tip.classList.remove('hidden');", "tip.className = '';")], "lost its class tip"),
        (
            [(
                "const first = document.querySelector('#list li');\nfirst.classList.add('done');",
                "document.querySelectorAll('#list li').classList.add('done');",
            )],
            "threw",
        ),
    ],
    "todo-03-click": [
        ([("    item.classList.toggle('done');", "    item.classList.add('done');")], "toggle, not add"),
        # The listener called straight away instead of passed.
        (
            [(
                "  item.addEventListener('click', () => {\n    item.classList.toggle('done');\n  });",
                "  item.addEventListener('click', item.classList.toggle('done'));",
            )],
            "straight away",
        ),
        (
            [(
                _TOGGLE_EACH,
                "\nconst first = document.querySelector('#list li');\n"
                "first.addEventListener('click', () => first.classList.toggle('done'));\n",
            )],
            "Walk the dog",
        ),
        (
            [(
                "tip.classList.remove('hidden');\n",
                "tip.classList.remove('hidden');\ndocument.querySelector('#list li').classList.add('done');\n",
            )],
            "line from step 2",
        ),
    ],
    "todo-04-value": [
        ([("console.log(input.value);", "console.log(input.textContent);")], "empty line"),
        # Read once, at the top, before anyone typed.
        (
            [
                (
                    "const addButton = document.querySelector('#add');\n",
                    "const addButton = document.querySelector('#add');\nconst typed = input.value;\n",
                ),
                ("console.log(input.value);", "console.log(typed);"),
            ],
            "empty line",
        ),
        ([("console.log(input.value);", "console.log(input);")], "<input> itself"),
    ],
    "todo-05-append": [
        ([("li.textContent = input.value;", "li.innerHTML = input.value;")], "innerHTML"),
        ([("  input.value = '';\n", "")], "Empty the box"),
        ([("list.append(li);", "list.prepend(li);")], "end of the list"),
        # One <li>, made once, that only moves.
        (
            [(
                "addButton.addEventListener('click', () => {\n  const li = document.createElement('li');\n",
                "const li = document.createElement('li');\naddButton.addEventListener('click', () => {\n",
            )],
            "new <li> each time",
        ),
        (
            [(
                "  const li = document.createElement('li');\n  li.textContent = input.value;\n  list.append(li);\n",
                "  list.append(input.value);\n",
            )],
            "createElement",
        ),
    ],
    "todo-06-trim": [
        (
            [(
                "  const text = input.value.trim();\n  if (!text) return;\n",
                "  if (!input.value) return;\n  const text = input.value.trim();\n",
            )],
            "trim first",
        ),
        ([("const text = input.value.trim();", "const text = input.value;")], "Trim the text"),
        ([("  if (!text) return;\n", "")], "nothing typed"),
    ],
    "todo-07-form": [
        ([("  event.preventDefault();\n", "")], "preventDefault"),
        # Called after the early return: an empty box still reloads the page.
        (
            [(
                "  event.preventDefault();\n  const text = input.value.trim();\n  if (!text) return;\n",
                "  const text = input.value.trim();\n  if (!text) return;\n  event.preventDefault();\n",
            )],
            "preventDefault",
        ),
        # The old click listener kept beside the new submit one.
        (
            [(
                "const list = document.querySelector('#list');\n",
                "const list = document.querySelector('#list');\n\n"
                "document.querySelector('#add').addEventListener('click', () => {\n"
                "  const li = document.createElement('li');\n"
                "  li.textContent = input.value.trim();\n"
                "  list.append(li);\n"
                "});\n",
            )],
            "twice",
        ),
        # Enter caught by hand, and the form left to submit.
        (
            [(
                "form.addEventListener('submit', (event) => {\n  event.preventDefault();\n",
                "input.addEventListener('keydown', (event) => {\n  if (event.key !== 'Enter') return;\n",
            )],
            "preventDefault",
        ),
    ],
    "todo-08-delete": [
        ([("del.addEventListener('click', () => li.remove());", "del.addEventListener('click', () => list.remove());")], "only"),
        ([("del.addEventListener('click', () => li.remove());", "del.addEventListener('click', () => li.remove);")], "remove that to-do"),
        ([(_DELETE_EACH, "")], "already in the page"),
        ([("span.className = 'text';", "span.classList.add('.text');")], "span class"),
        ([("    button.closest('li').remove();", "    list.lastElementChild.remove();")], 'only "Walk the dog"'),
    ],
    "todo-09-delegation": [
        ([("    li.classList.toggle('done');", "    event.target.classList.toggle('done');")], "closest('li')"),
        ([("    li.remove();", "    event.target.remove();")], "removed only itself"),
        # The step 3 listeners left in: the old to-dos toggle twice.
        (
            [(
                "list.addEventListener('click', (event) => {",
                "document.querySelectorAll('#list li').forEach((item) => {\n"
                "  item.addEventListener('click', () => item.classList.toggle('done'));\n"
                "});\n\n"
                "list.addEventListener('click', (event) => {",
            )],
            "two listeners",
        ),
        ([("  const li = event.target.closest('li');", "  const li = event.target.parentElement;")], "wherever on the to-do"),
    ],
    "todo-10-count": [
        ([("li:not(.done)", "li")], "without the class done"),
        ([("li:not(.done)", "li.done")], "start at"),
        ([("});\n\nupdateCount();\n", "});\n")], "#left is empty"),
        ([("  }\n  updateCount();\n});", "  }\n});")], "Crossing off"),
        # Counted before the to-do has gone.
        (
            [(
                "  if (event.target.closest('.delete')) {\n    li.remove();\n  } else {\n"
                "    li.classList.toggle('done');\n  }\n  updateCount();\n",
                "  if (event.target.closest('.delete')) {\n    updateCount();\n    li.remove();\n  } else {\n"
                "    li.classList.toggle('done');\n    updateCount();\n  }\n",
            )],
            "once the to-do is gone",
        ),
    ],
    "todo-11-storage": [
        ([("localStorage.setItem('todos', JSON.stringify(todos));", "localStorage.setItem('todos', todos);")], "JSON"),
        ([("for (const todo of JSON.parse(saved))", "for (const todo of saved)")], "just as it was"),
        # Saved on add only: toggles and deletes are lost.
        ([("  updateCount();\n  save();\n});\n\nload();", "  updateCount();\n});\n\nload();")], "toggle and delete"),
        ([("  list.replaceChildren();\n", "")], "replaceChildren"),
        ([("load();\nupdateCount();\n", "updateCount();\nload();\n")], "after loading"),
        ([("addTodo(todo.text, todo.done)", "addTodo(todo.text, false)")], "which ones were done"),
    ],
}

#: Right programs written another way, which the check must still pass.
OTHER_WAYS: dict[str, list[list[tuple[str, str]]]] = {
    "todo-02-classes": [
        [("first.classList.add('done');", "first.className = 'done';")],
        [("tip.classList.remove('hidden');", "tip.classList.toggle('hidden');")],
    ],
    "todo-03-click": [
        [(_TOGGLE_EACH, "\nfor (const item of document.querySelectorAll('#list li')) {\n"
                        "  item.onclick = () => item.classList.toggle('done');\n}\n")],
        # Delegation, before it is taught, works too.
        [(_TOGGLE_EACH, "\ndocument.querySelector('#list').addEventListener('click', (event) => {\n"
                        "  event.target.closest('li').classList.toggle('done');\n});\n")],
    ],
    "todo-04-value": [
        [("console.log(input.value);", "console.log('Adding:', input.value);")],
    ],
    "todo-05-append": [
        [("list.append(li);", "list.appendChild(li);")],
        [("list.append(li);", "list.insertAdjacentElement('beforeend', li);")],
    ],
    "todo-06-trim": [
        [("if (!text) return;", "if (text.length === 0) return;")],
    ],
    "todo-07-form": [
        [("form.addEventListener('submit', (event) => {", "form.onsubmit = (event) => {"),
         ("  input.value = '';\n});", "  input.value = '';\n};")],
        # A click listener that adds, and a submit listener that only stops
        # the reload: Enter clicks the form's button, so Enter adds too.
        [("form.addEventListener('submit', (event) => {\n  event.preventDefault();\n",
          "form.addEventListener('submit', (event) => event.preventDefault());\n"
          "document.querySelector('#add').addEventListener('click', () => {\n")],
    ],
    "todo-08-delete": [
        [("button.closest('li').remove();", "button.parentElement.remove();")],
        [("  li.append(span, del);\n", "  li.appendChild(span);\n  li.appendChild(del);\n")],
    ],
    "todo-09-delegation": [
        [("if (event.target.closest('.delete')) {", "if (event.target.classList.contains('delete')) {")],
        [("if (event.target.closest('.delete')) {", "if (event.target.matches('.delete')) {")],
    ],
    "todo-10-count": [
        [("  const count = list.querySelectorAll('li:not(.done)').length;",
          "  const count = [...list.children].filter((li) => !li.classList.contains('done')).length;")],
        [("  left.textContent = `${count} left`;", "  left.textContent = count + ' left';")],
    ],
    "todo-11-storage": [
        # localStorage as properties, as a real one allows.
        [("  const saved = localStorage.getItem('todos');\n  if (saved === null) return;",
          "  const saved = localStorage.todos;\n  if (!saved) return;"),
         ("localStorage.setItem('todos', JSON.stringify(todos));", "localStorage.todos = JSON.stringify(todos);")],
        # Saved once, on the way out, as a reload leaves.
        [("  updateCount();\n  save();\n});\n\nlist.addEventListener", "  updateCount();\n});\n\nlist.addEventListener"),
         ("  updateCount();\n  save();\n});\n\nload();", "  updateCount();\n});\n\nwindow.addEventListener('beforeunload', save);\n\nload();")],
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in TODO_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(TODO_STEPS), 12)
        for s in TODO_STEPS:
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith("todo-"))
                self.assertEqual(s.track, "To-do")
                self.assertEqual(s.kind, "dom")
                self.assertTrue(s.title)
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))
                self.assertTrue(s.html.strip() and s.css.strip())

    def test_the_track_is_served_with_the_others(self) -> None:
        ids = [s.id for s in ALL_STEPS]
        for s in TODO_STEPS:
            self.assertIn(s.id, ids)
        # The other tracks are all drawn on a canvas.
        self.assertEqual({s.kind for s in ALL_STEPS if s.track != "To-do"}, {"canvas"})

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(TODO_STEPS, TODO_STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in TODO_STEPS if not s.check], [TODO_STEPS[-1].id])

    def test_every_mistake_and_other_way_names_a_real_step(self) -> None:
        for step_id in list(MISTAKES) + list(OTHER_WAYS):
            self.assertIn(step_id, [s.id for s in TODO_STEPS])

    def test_every_id_the_code_looks_for_is_on_its_page(self) -> None:
        for s in TODO_STEPS:
            for wanted in re.findall(r"querySelector(?:All)?\('#([\w-]+)", s.solution):
                with self.subTest(step=s.id, id=wanted):
                    self.assertIn(f'id="{wanted}"', s.html)

    def test_node_does_not_check_a_page_step(self) -> None:
        got = check_step(TODO_STEPS[0].id, TODO_STEPS[0].solution)
        self.assertIsNotNone(got)
        self.assertFalse(got.passed)
        self.assertIn("browser", got.message)


class PageTests(unittest.TestCase):
    def test_the_harness_keeps_its_names_off_the_page(self) -> None:
        text = harness_source()
        self.assertTrue(text.lstrip().startswith("//"))
        self.assertIn("(function () {", text)
        self.assertIn("W.__ccDom =", text)

    def test_a_play_page_carries_its_storage_and_no_check(self) -> None:
        s = _by_id("todo-11-storage")
        doc = page(s, "let x = 1;", mode="play", storage={"todos": "[]"})
        self.assertIn('"storage": {"todos": "[]"}', doc)
        self.assertIn('"check": ""', doc)
        self.assertIn(s.html, doc)

    def test_a_check_page_carries_the_check_and_starts_empty(self) -> None:
        s = _by_id("todo-11-storage")
        doc = page(s, "let x = 1;", mode="check", storage={"todos": "[]"})
        self.assertIn('"storage": {}', doc)
        self.assertIn("cc.reload()", doc)

    def test_code_cannot_close_the_script_it_is_in(self) -> None:
        s = TODO_STEPS[0]
        doc = page(s, "console.log('</script><b>out</b>');")
        self.assertEqual(doc.count("</script>"), 2)  # the harness's and the boot call's
        self.assertIn("\\u003c/script>", doc)

    def test_index_html_reads_as_a_page_written_by_hand(self) -> None:
        text = source_html(TODO_STEPS[6])
        self.assertTrue(text.startswith("<!doctype html>"))
        self.assertIn('<link rel="stylesheet" href="style.css">', text)
        self.assertIn('<script src="app.js"></script>', text)
        self.assertIn('<form id="new" class="new">', text)
        self.assertIn("<title>My list</title>", text)


@unittest.skipUnless(HAS_CHROME, "needs Google Chrome or Chromium")
class BrowserTests(unittest.TestCase):
    """Every case runs in one headless Chrome, loaded once for the class."""

    checks: dict[str, dict]
    played: dict[str, list[dict]]

    @classmethod
    def setUpClass(cls) -> None:
        cases: dict[str, tuple] = {}
        for s in TODO_STEPS:
            if not s.check:
                continue
            cases[f"{s.id}/solution"] = (s, s.solution)
            cases[f"{s.id}/starter"] = (s, s.starter)
        for step_id, mistakes in MISTAKES.items():
            s = _by_id(step_id)
            for n, (swaps, _) in enumerate(mistakes):
                cases[f"{step_id}/mistake{n}"] = (s, _apply(s.solution, swaps))
        for step_id, ways in OTHER_WAYS.items():
            s = _by_id(step_id)
            for n, swaps in enumerate(ways):
                cases[f"{step_id}/other{n}"] = (s, _apply(s.solution, swaps))
        for key, (step_id, code) in cls._harness_cases().items():
            cases[key] = (_by_id(step_id), code)
        cls.checks = check_pages(cases)

        # The preview's pages, sandboxed as the preview is.
        first, form = _by_id("todo-01-text"), _by_id("todo-07-form")
        cls.played = run_pages({
            "storage": (
                page(
                    first,
                    "localStorage.setItem('a', 1);\nlocalStorage.b = 'two';\n"
                    "console.log(typeof localStorage.getItem('a'), localStorage.getItem('zzz'), "
                    "localStorage.length, localStorage.key(0), Object.keys(localStorage).join(','), "
                    "localStorage.b, localStorage.getItem('seed'));\n",
                    mode="play",
                    storage={"seed": "kept"},
                    token="storage",
                ),
                PLAY_SANDBOX,
            ),
            "unstopped": (
                page(form, form.starter + "\ndocument.querySelector('#new').requestSubmit();\n", token="unstopped"),
                PLAY_SANDBOX,
            ),
            "stopped": (
                page(form, form.solution + "\ndocument.querySelector('#new').requestSubmit();\n", token="stopped"),
                PLAY_SANDBOX,
            ),
            "crash": (
                page(first, first.solution + "\nnope();\n", token="crash"),
                PLAY_SANDBOX,
            ),
        })

    @staticmethod
    def _harness_cases() -> dict[str, tuple[str, str]]:
        first = _by_id("todo-01-text")
        value = _by_id("todo-04-value")
        storage = _by_id("todo-11-storage")
        return {
            "harness/crash": ("todo-01-text", first.solution + "\nnope();\n"),
            "harness/syntax": ("todo-01-text", first.solution + "\nconst = 5;\n"),
            "harness/listener": (
                "todo-04-value",
                value.solution.replace("console.log(input.value);", "console.log(input.value.nope.deeper);"),
            ),
            "harness/after-reload": (
                "todo-11-storage",
                storage.solution.replace("JSON.parse(saved)", "JSON.parse(saved + ']')"),
            ),
        }

    def _check(self, key: str) -> dict:
        self.assertIn(key, self.checks)
        return self.checks[key]

    def test_every_solution_passes_its_check(self) -> None:
        for s in TODO_STEPS:
            if s.check:
                with self.subTest(step=s.id):
                    got = self._check(f"{s.id}/solution")
                    self.assertTrue(got["passed"], got["message"])

    def test_every_starter_fails_its_check(self) -> None:
        for s in TODO_STEPS:
            if s.check:
                with self.subTest(step=s.id):
                    got = self._check(f"{s.id}/starter")
                    self.assertFalse(got["passed"])
                    self.assertTrue(got["message"])
                    self.assertNotIn("never reported", got["message"])

    def test_real_mistakes_fail_and_say_what_is_wrong(self) -> None:
        for step_id, mistakes in MISTAKES.items():
            for n, (_, words) in enumerate(mistakes):
                with self.subTest(step=step_id, mistake=n):
                    got = self._check(f"{step_id}/mistake{n}")
                    self.assertFalse(got["passed"], "the check let this mistake through")
                    self.assertIn(words, got["message"])

    def test_other_right_answers_pass(self) -> None:
        for step_id, ways in OTHER_WAYS.items():
            for n, _ in enumerate(ways):
                with self.subTest(step=step_id, way=n):
                    got = self._check(f"{step_id}/other{n}")
                    self.assertTrue(got["passed"], got["message"])

    def test_a_crash_is_reported_with_its_line(self) -> None:
        got = self._check("harness/crash")
        self.assertFalse(got["passed"])
        self.assertIn("nope", got["message"])
        self.assertIn("line 5", got["message"])

    def test_a_syntax_error_is_reported_with_its_line(self) -> None:
        got = self._check("harness/syntax")
        self.assertFalse(got["passed"])
        self.assertIn("mistake on line 5", got["message"])
        self.assertNotIn("appendChild", got["message"])

    def test_a_crash_in_a_listener_names_what_set_it_off(self) -> None:
        code = _by_id("todo-04-value").solution
        line = _line_of(code, "console.log(input.value);")
        got = self._check("harness/listener")
        self.assertFalse(got["passed"])
        self.assertIn(f"Clicking #add made your code throw on line {line}", got["message"])

    def test_a_crash_after_a_reload_counts_lines_from_your_code(self) -> None:
        code = _by_id("todo-11-storage").solution
        line = _line_of(code, "JSON.parse(saved)")
        got = self._check("harness/after-reload")
        self.assertFalse(got["passed"])
        self.assertIn(f"After a reload your code threw on line {line}", got["message"])
        self.assertIn("JSON.stringify", got["message"])

    def test_the_preview_keeps_a_working_local_storage(self) -> None:
        posted = self.played.get("storage", [])
        logs = [m["text"] for m in posted if m.get("type") == "log"]
        self.assertEqual(logs, ["string null 3 seed seed,a,b two kept"])
        saved = [m["items"] for m in posted if m.get("type") == "storage"]
        self.assertEqual(saved[-1], {"seed": "kept", "a": "1", "b": "two"})

    def test_an_unstopped_form_reloads_the_preview(self) -> None:
        self.assertIn("reload", [m.get("type") for m in self.played.get("unstopped", [])])
        self.assertNotIn("reload", [m.get("type") for m in self.played.get("stopped", [])])

    def test_the_preview_reports_a_crash_with_its_line(self) -> None:
        errors = [m for m in self.played.get("crash", []) if m.get("type") == "error"]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["line"], 5)
        self.assertIn("nope", errors[0]["message"])

    def test_a_check_page_may_not_submit_a_form(self) -> None:
        # The frames the tests use are sandboxed as Code Coach's are.
        self.assertNotIn("allow-forms", CHECK_SANDBOX)
        self.assertIn("allow-forms", PLAY_SANDBOX)


class RouteTests(unittest.TestCase):
    def test_list_ships_the_page_but_not_the_check(self) -> None:
        from code_coach.api.server import canvas_list

        data = canvas_list()
        served = {s["id"]: s for s in data["steps"]}
        for s in TODO_STEPS:
            with self.subTest(step=s.id):
                got = served[s.id]
                self.assertEqual(got["kind"], "dom")
                self.assertIn('<script src="app.js"></script>', got["page"])
                self.assertEqual(got["css"], s.css)
                self.assertNotIn("check", got)
                self.assertNotIn("solution", got)
        self.assertEqual(served["dodge-01-square"]["kind"], "canvas")
        self.assertEqual(served["dodge-01-square"]["page"], "")

    def test_the_page_route_builds_pages_for_page_steps_only(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import CanvasPageRequest
        from code_coach.api.server import canvas_page

        s = _by_id("todo-03-click")
        got = canvas_page(CanvasPageRequest(step_id=s.id, code="let mine = 1;", mode="check"))
        self.assertIn("let mine = 1;", got["page"])
        self.assertIn("__ccDom.boot(", got["page"])
        with self.assertRaises(HTTPException) as raised:
            canvas_page(CanvasPageRequest(step_id="dodge-01-square", code=""))
        self.assertEqual(raised.exception.status_code, 400)
        with self.assertRaises(HTTPException) as raised:
            canvas_page(CanvasPageRequest(step_id="no-such-step", code=""))
        self.assertEqual(raised.exception.status_code, 404)

    def test_a_pass_seen_in_the_browser_is_counted(self) -> None:
        from code_coach.api.schemas import CanvasPassedRequest
        from code_coach.api.server import _store, canvas_passed

        s = _by_id("todo-02-classes")
        before = _store.load().canvas_counts().get(s.id, 0)
        got = canvas_passed(CanvasPassedRequest(step_id=s.id))
        self.assertTrue(got.passed)
        self.assertEqual(got.done, before + 1)
        self.assertEqual(_store.load().canvas_counts()[s.id], before + 1)

    def test_a_canvas_step_cannot_be_passed_from_the_browser(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import CanvasPassedRequest
        from code_coach.api.server import _store, canvas_passed

        before = _store.load().canvas_counts().get("dodge-01-square", 0)
        with self.assertRaises(HTTPException) as raised:
            canvas_passed(CanvasPassedRequest(step_id="dodge-01-square"))
        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(_store.load().canvas_counts().get("dodge-01-square", 0), before)
        with self.assertRaises(HTTPException):
            canvas_passed(CanvasPassedRequest(step_id=TODO_STEPS[-1].id))  # the open step

    def test_a_page_step_is_not_checked_in_node(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import CanvasCheckRequest
        from code_coach.api.server import canvas_check

        s = TODO_STEPS[0]
        with self.assertRaises(HTTPException) as raised:
            canvas_check(CanvasCheckRequest(step_id=s.id, code=s.solution))
        self.assertEqual(raised.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
