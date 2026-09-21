"""More hand-picked Python and JavaScript lines to type.

The curated lists in snippets.py are the first two dozen shapes each
language asks for. These are the next set: the lines you meet once you
are past the loop and the list comprehension and into code that opens
files, awaits things, and handles being wrong.

Why hand-picked lines exist at all, when the curriculum already supplies
hundreds: a curriculum line is real code, which is the larger kind of
useful, but it was written to solve a problem rather than to teach a
shape. A line here is chosen for the shape. Every one of them has a note
saying what the shape is for, so the drill teaches something even on the
repetitions where the fingers are on autopilot.

Two rules for adding to this file:

* It has to be a line somebody would really write. Not a demonstration
  of a feature, and nothing contrived to be awkward to type.
* The note says what the line is for, not what it says. "walk a
  dictionary" is a note; "calls items" is a restatement.

Python and JavaScript only, for now, and deliberately: repetition on two
languages beats a thin pass over seven.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Python --------------------------------------------------

PYTHON_MORE: tuple[Passage, ...] = (
    # Files and paths
    _s("path = Path(__file__).resolve().parent", "where this file lives"),
    _s("for line in path.read_text(encoding='utf-8').splitlines():",
       "read a file line by line"),
    _s("path.write_text(json.dumps(data, indent=2), encoding='utf-8')",
       "save some JSON"),
    _s("if not path.exists():", "the guard before the work"),
    _s("for child in sorted(folder.glob('*.py')):", "walk a folder"),

    # Dictionaries and sets
    _s("counts[word] = counts.get(word, 0) + 1", "count without a Counter"),
    _s("groups.setdefault(key, []).append(item)", "group into lists"),
    _s("merged = {**defaults, **overrides}", "one dict on top of another"),
    _s("missing = set(wanted) - set(have)", "what is not there yet"),
    _s("if key in cache:", "the cheapest check there is"),
    _s("for name in sorted(seen, key=seen.get, reverse=True):",
       "walk by value, not by key"),

    # Slices and unpacking
    _s("first, *rest = parts", "take the head, keep the tail"),
    _s("head, tail = text[:1], text[1:]", "split a string in two"),
    _s("if word == word[::-1]:", "the palindrome test"),
    _s("rows = [line.split(',') for line in lines[1:]]", "skip the header"),
    _s("a, b = b, a + b", "the Fibonacci step"),

    # Functions and structure
    _s("def __init__(self, name: str, score: int = 0) -> None:",
       "a constructor with a default"),
    _s("def __repr__(self) -> str:", "what it looks like when printed"),
    _s("@staticmethod", "a function that lives in a class"),
    _s("@property", "a method that reads like a field"),
    _s("@functools.lru_cache(maxsize=None)", "remember what it already worked out"),
    _s("def walk(node, depth=0):", "the recursive signature"),
    _s("return result if result is not None else default", "a careful fallback"),
    _s("kwargs.setdefault('timeout', 10)", "a default the caller can override"),

    # Errors
    _s("try:", "the line before the risk"),
    _s("except KeyError:", "the lookup that was not there"),
    _s("finally:", "the cleanup that always runs"),
    _s("raise RuntimeError('the server never started') from exc",
       "keep the original cause"),
    _s("if not isinstance(value, int):", "check before you trust it"),
    _s("warnings.warn('deprecated, use build() instead', stacklevel=2)",
       "tell the caller, not yourself"),

    # The standard library
    _s("for a, b in itertools.pairwise(values):", "every neighbouring pair"),
    _s("for key, group in itertools.groupby(rows, key=first):",
       "runs of the same thing"),
    _s("queue = collections.deque([start])", "the breadth-first queue"),
    _s("stamp = datetime.now(timezone.utc).isoformat()",
       "a time that means the same everywhere"),
    _s("digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()",
       "a fingerprint for some bytes"),
    _s(r"words = re.findall(r'[a-z]+', text.lower())", "pull the words out"),
    _s("parts = textwrap.dedent(body).strip().split('\\n\\n')",
       "tidy an indented string"),
    _s("done = subprocess.run(cmd, capture_output=True, text=True)",
       "run something and keep what it said"),

    # Shapes worth having in the fingers
    _s("return {name: score for name, score in pairs if score > 0}",
       "filter while you build"),
    _s("if any(item.failed for item in results):", "did anything go wrong"),
    _s("if all(c.isdigit() for c in text):", "is every character a digit"),
    _s("best = max(candidates, key=lambda c: c.score)", "pick the winner"),
    _s("index = bisect.bisect_left(values, target)",
       "binary search, already written"),
    _s("for attempt in range(1, retries + 1):", "counting from one"),
    _s("yield item", "hand one out and wait"),
)


# -- JavaScript ----------------------------------------------

JAVASCRIPT_MORE: tuple[Passage, ...] = (
    # Reaching into data that might not be there
    _s("const name = user?.profile?.name ?? 'anonymous';",
       "two guards in one line"),
    _s("const { id, tags = [] } = item;", "destructure with a default"),
    _s("const value = Object.hasOwn(config, key) ? config[key] : fallback;",
       "ask the object, not the prototype"),
    _s("for (const [key, value] of Object.entries(counts)) {",
       "walk a plain object"),
    _s("const merged = { ...defaults, ...overrides };",
       "one object on top of another"),
    _s("const byId = Object.fromEntries(rows.map((r) => [r.id, r]));",
       "an array into a lookup"),

    # Async
    _s("const response = await fetch(url, { signal: controller.signal });",
       "a request you can cancel"),
    _s("if (!response.ok) throw new Error(`HTTP ${response.status}`);",
       "a failed request is not an exception by itself"),
    _s("const data = await response.json();", "the body, parsed"),
    _s("const [users, posts] = await Promise.all([getUsers(), getPosts()]);",
       "two things at once"),
    _s("await new Promise((resolve) => setTimeout(resolve, 200));",
       "wait on purpose"),
    _s("export async function load(id) {", "an async export"),
    _s("} catch (error) {", "where the await went wrong"),
    _s("} finally {", "the cleanup that always runs"),

    # Arrays
    _s("const found = list.find((item) => item.id === id);",
       "the first one that matches"),
    _s("const index = list.findIndex((item) => item.id === id);",
       "where it is, or minus one"),
    _s("if (list.some((item) => item.failed)) {", "did anything go wrong"),
    _s("const ok = list.every((item) => item.valid);", "is all of it good"),
    _s("const flat = rows.flatMap((row) => row.cells);",
       "map and flatten in one go"),
    _s("const page = items.slice(start, start + size);", "one page of results"),
    _s("const totals = list.reduce((acc, item) => {", "fold into an object"),
    _s("const counts = Array.from({ length: 26 }, () => 0);",
       "an array of a known size"),
    _s("const sorted = [...items].sort((a, b) => a.name.localeCompare(b.name));",
       "sort names properly"),

    # Strings and numbers
    _s("const label = `${count} ${count === 1 ? 'item' : 'items'}`;",
       "plural without a library"),
    _s("const slug = title.trim().toLowerCase().replaceAll(' ', '-');",
       "a title into a URL"),
    _s("const rounded = Math.round(value * 100) / 100;", "two decimal places"),
    _s("const n = Number.parseInt(raw, 10);", "always pass the radix"),
    _s("if (Number.isNaN(n)) return null;", "the only safe NaN test"),

    # Classes, closures and modules
    _s("export class Store {", "something with state and rules"),
    _s("constructor(initial = {}) {", "a constructor with a default"),
    _s("#items = new Map();", "a field nobody outside can touch"),
    _s("get size() {", "a method that reads like a field"),
    _s("static from(rows) {", "a second way to build one"),
    _s("import { useEffect, useMemo } from 'react';", "a named import"),
    _s("export { parse, format };", "what this file offers"),
    _s("module.exports = { run };", "the older way, still everywhere"),

    # The browser
    _s("document.querySelector('#total').textContent = String(total);",
       "put a number on the page"),
    _s("button.addEventListener('click', () => {", "wire up a button"),
    _s("event.preventDefault();", "stop the form reloading the page"),
    _s("element.classList.toggle('active', isActive);",
       "a class that follows a boolean"),
    _s("localStorage.setItem('settings', JSON.stringify(settings));",
       "remember it for next time"),
    _s("const params = new URLSearchParams(window.location.search);",
       "read the query string"),
)
