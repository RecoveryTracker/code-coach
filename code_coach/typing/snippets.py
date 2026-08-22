"""Real code to type, chosen because it's worth having in your fingers.

The Coding Punctuation section drills symbols in isolation, which trains the
reach but not the shape. These are whole lines: the things you write in a
first programming course, the one-liners experienced people reach for, and a
few short programs that draw something. Typing a working line puts both the
punctuation and the idiom in your hands at once.

Each snippet carries a note saying what it does, so a speed drill doubles as
reading practice — recognising code at a glance is its own skill, and it's the
one that makes reviewing someone else's work fast.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# ── The first things anyone writes ──────────────────────────
# Deliberately across several languages: the shapes are the point, and seeing
# the same idea in three syntaxes is how the shape becomes visible.

SCHOOL: tuple[Passage, ...] = (
    _s('print("Hello, world!")', "the first line, Python"),
    _s('console.log("Hello, world!");', "the first line, JavaScript"),
    _s("for i in range(1, 11): print(i)", "count to ten"),
    _s("for (let i = 1; i <= 10; i++) console.log(i);", "count to ten, JS"),
    _s("total = sum(numbers) / len(numbers)", "the average"),
    _s("if score >= 90: grade = 'A'", "a grading rule"),
    _s("while guess != answer:", "loop until it's right"),
    _s("def area(width, height): return width * height", "a function"),
    _s("celsius = (fahrenheit - 32) * 5 / 9", "temperature conversion"),
    _s("names = ['Ada', 'Alan', 'Grace']", "a list"),
    _s("for name in names: print(f'Hi, {name}')", "loop over a list"),
    _s("count = count + 1", "the line every program has"),
    _s("if n % 2 == 0: print('even')", "odd or even"),
    _s("largest = max(numbers)", "the biggest one"),
    _s("words = sentence.split(' ')", "break a sentence up"),
    _s("return factorial(n - 1) * n", "recursion, the whole idea"),
    _s("import random; roll = random.randint(1, 6)", "roll a die"),
    _s("with open('notes.txt') as f: text = f.read()", "read a file"),
    _s("except ValueError: value = 0", "handle bad input"),
    _s("students = {'Ada': 92, 'Alan': 88}", "a dictionary"),
)


# ── Things worth knowing ────────────────────────────────────

TRICKS: tuple[Passage, ...] = (
    _s("a, b = b, a", "swap two variables with no temporary"),
    _s("squares = [n * n for n in range(10)]", "a comprehension"),
    _s("flat = [x for row in grid for x in row]", "flatten a nested list"),
    _s("pairs = list(zip(names, scores))", "walk two lists together"),
    _s("for i, item in enumerate(items):", "index and value at once"),
    _s("counts = Counter(words).most_common(3)", "top three, counted"),
    _s("text[::-1]", "reverse anything sliceable"),
    _s("seen = set(); unique = [x for x in xs if not (x in seen or seen.add(x))]",
       "de-duplicate but keep the order"),
    _s("sorted(people, key=lambda p: (-p.score, p.name))",
       "sort by score, then break ties by name"),
    _s("value = config.get('retries', 3)", "a default that can't KeyError"),
    _s("const { a, b, ...rest } = props;", "pull fields out, keep the remainder"),
    _s("const unique = [...new Set(list)];", "de-duplicate, JavaScript"),
    _s("arr.reduce((sum, n) => sum + n, 0)", "add up a list"),
    _s("const debounced = () => clearTimeout(t) || (t = setTimeout(fn, 200));",
       "only fire after things go quiet"),
    _s("return cache[n] ??= compute(n);", "memoise in one line"),
    _s("x & (x - 1)", "clears the lowest set bit — zero means power of two"),
    _s("(low + high) // 2", "the midpoint, and half of all binary searches"),
    _s("if not head or not head.next: return head", "the base case of half of linked lists"),
    _s("left, right = 0, len(nums) - 1", "two pointers, opening move"),
    _s("seen[target - num] = i", "the line that makes Two Sum O(n)"),
)


# ── Programs that draw something ────────────────────────────
# Short enough to type in one go and long enough to produce a picture, which
# is a better reward for a drill than a green tick.

VISUALS: tuple[Passage, ...] = (
    _s("for i in range(1, 8): print('*' * i)", "a triangle"),
    _s("print('\\n'.join(' ' * (7 - i) + '*' * (2 * i - 1) for i in range(1, 8)))",
       "a centred pyramid"),
    _s("for r in range(8): print(''.join('##' if (r + c) % 2 else '  ' for c in range(8)))",
       "a chessboard"),
    _s("print('\\n'.join(''.join('*' if (x ^ y) % 5 else ' ' for x in range(40)) for y in range(20)))",
       "an XOR texture"),
    _s("for n in range(1, 21): print('Fizz' * (n % 3 == 0) + 'Buzz' * (n % 5 == 0) or n)",
       "FizzBuzz without a single if"),
    _s("print(' '.join(str(2 ** i) for i in range(12)))", "powers of two"),
    _s("bar = lambda n: '#' * n + '.' * (40 - n)", "a progress bar"),
    _s("print('\\n'.join('%3d' % (a * b) for a in range(1, 6) for b in range(1, 6)))",
       "a times table"),
)


FRACTALS: tuple[Passage, ...] = (
    _s("for y in range(32): print(''.join('*' if (x & y) == 0 else ' ' for x in range(32)))",
       "Sierpinski's triangle, from one AND"),
    _s("rule = lambda row: [int(a ^ (b | c)) for a, b, c in zip(row, row[1:], row[2:])]",
       "rule 30, a one-line cellular automaton"),
    _s("z = z * z + c", "the whole Mandelbrot set, one line"),
    _s("while abs(z) <= 2 and steps < 50: z = z * z + c; steps += 1",
       "the escape test — how long before it runs away"),
    _s("draw(length / 3, depth - 1); turn(-60); draw(length / 3, depth - 1)",
       "the Koch curve calling itself"),
    _s("def tree(n): return n if n < 2 else tree(n - 1) + tree(n - 2)",
       "Fibonacci, branching like a tree"),
    _s("angle = 137.5  # the golden angle, why sunflowers look like that",
       "phyllotaxis"),
    _s("points = [(r * cos(i * angle), r * sin(i * angle)) for i in range(500)]",
       "a spiral of seeds"),
)


# ── Lines you'll actually reuse ─────────────────────────────

USEFUL: tuple[Passage, ...] = (
    _s("if __name__ == '__main__': main()", "the Python entry point"),
    _s("from pathlib import Path", "the good way to handle files"),
    _s("data = json.loads(path.read_text(encoding='utf-8'))", "read a JSON file"),
    _s("path.write_text(json.dumps(data, indent=2), encoding='utf-8')", "write one back"),
    _s("git commit -m 'message' && git push", "the two commands"),
    _s("git checkout -b feature/name", "start a branch"),
    _s("npm install && npm run dev", "start a web project"),
    _s("python -m venv .venv", "a fresh environment"),
    _s("grep -rn 'pattern' src/", "find it in the tree"),
    _s("SELECT * FROM users WHERE created_at > '2025-01-01';", "a query"),
    _s("await Promise.all(items.map(fetchOne));", "run them all at once"),
    _s("export default function App() {", "a React component"),
    _s("const [value, setValue] = useState('');", "React state"),
    _s("useEffect(() => { load(); }, []);", "run once on mount"),
    _s("res.status(404).json({ error: 'not found' });", "an API error"),
    _s("logger.info('processed %d rows', count)", "a log line worth reading"),
    _s("assert result == expected, f'got {result}'", "a test that says what went wrong"),
    _s("docker compose up -d --build", "bring the stack up"),
)

# ── The same ideas, one language at a time ──────────────────
# The sets above are deliberately mixed, which is right for "some code". When
# you're learning one language you want that language's punctuation in your
# hands — its brackets, its terminators, the shapes it repeats.

PYTHON_CODE: tuple[Passage, ...] = (
    _s("if __name__ == '__main__':", "the entry point"),
    _s("def solve(nums: list[int]) -> int:", "a typed signature"),
    _s("for i, item in enumerate(items):", "index and value at once"),
    _s("for key, value in counts.items():", "walking a dictionary"),
    _s("squares = [n * n for n in range(10)]", "a list comprehension"),
    _s("pairs = {k: v for k, v in rows}", "a dict comprehension"),
    _s("total = sum(x for x in values if x > 0)", "a generator expression"),
    _s("with open(path, encoding='utf-8') as f:", "read a file safely"),
    _s("data = json.loads(path.read_text(encoding='utf-8'))", "load some JSON"),
    _s("counts = Counter(words).most_common(3)", "the top three"),
    _s("left, right = 0, len(nums) - 1", "two pointers, opening move"),
    _s("seen: dict[int, int] = {}", "an annotated dictionary"),
    _s("return sorted(items, key=lambda p: (-p.score, p.name))", "sort, then break ties"),
    _s("raise ValueError(f'unexpected {value!r}')", "an error worth reading"),
    _s("except (OSError, ValueError) as exc:", "catch two things at once"),
    _s("assert result == expected, f'got {result}'", "a test that says what broke"),
    _s("@dataclass(frozen=True)", "an immutable record"),
    _s("print(f'{name}: {count:>4}')", "formatted output"),
    _s("nums.sort(reverse=True)", "sort in place, descending"),
    _s("return [x for row in grid for x in row]", "flatten a grid"),
    _s("while left < right:", "the shrinking window"),
    _s("value = config.get('retries', 3)", "a default that can't fail"),
    _s("yield from children", "delegate to another generator"),
    _s("text = ' '.join(str(n) for n in nums)", "numbers into a line"),
)

JAVASCRIPT_CODE: tuple[Passage, ...] = (
    _s("const { a, b, ...rest } = props;", "pull fields out, keep the rest"),
    _s("const unique = [...new Set(list)];", "de-duplicate an array"),
    _s("for (let i = 0; i < nums.length; i++) {", "the counting loop"),
    _s("for (const [key, value] of map.entries()) {", "walk a Map"),
    _s("const seen = new Map();", "a lookup table"),
    _s("arr.map((n) => n * 2);", "transform every item"),
    _s("arr.filter((n) => n % 2 === 0);", "keep the even ones"),
    _s("arr.reduce((sum, n) => sum + n, 0);", "add them all up"),
    _s("const sorted = [...arr].sort((a, b) => a - b);", "sort a copy, numerically"),
    _s("if (seen.has(need)) return [seen.get(need), i];", "the Two Sum line"),
    _s("export default function App() {", "a React component"),
    _s("const [value, setValue] = useState('');", "React state"),
    _s("useEffect(() => { load(); }, []);", "run once on mount"),
    _s("await Promise.all(items.map(fetchOne));", "run them all at once"),
    _s("const data = await res.json();", "read a response"),
    _s("res.status(404).json({ error: 'not found' });", "an API error"),
    _s("try { run(); } catch (err) { console.error(err); }", "catch and report"),
    _s("return a?.b ?? c;", "optional chaining and a default"),
    _s("const debounced = () => clearTimeout(t);", "cancel a pending timer"),
    _s("document.querySelectorAll('.item').forEach(hide);", "act on every match"),
    _s("class ListNode { constructor(val) { this.val = val; } }", "a node type"),
    _s("module.exports = { parse, format };", "what this file offers"),
)

DART_CODE: tuple[Passage, ...] = (
    _s("void main() { runApp(const MyApp()); }", "where a Flutter app starts"),
    _s("final seen = <int, int>{};", "a typed empty map"),
    _s("for (var i = 0; i < nums.length; i++) {", "the counting loop"),
    _s("for (final item in items) {", "walk a collection"),
    _s("List<int> twoSum(List<int> nums, int target) {", "a typed signature"),
    _s("if (seen.containsKey(need)) return [seen[need]!, i];", "and the line inside it"),
    _s("class ListNode { int val; ListNode? next; }", "a nullable field"),
    _s("ListNode(this.val, [this.next]);", "a constructor that assigns for you"),
    _s("final name = person?.name ?? 'unknown';", "a default when null"),
    _s("Future<String> load() async { ... }", "something that finishes later"),
    _s("final data = await http.get(uri);", "wait for a response"),
    _s("setState(() { count += 1; });", "tell Flutter to rebuild"),
    _s("return Column(children: [Text(label)]);", "a widget with children"),
    _s("const EdgeInsets.symmetric(horizontal: 12)", "named parameters everywhere"),
    _s("items.where((n) => n.isEven).toList()", "filter, then materialise"),
    _s("items.map((n) => n * 2).toList()", "transform, then materialise"),
    _s("throw ArgumentError('value must be positive');", "reject bad input"),
    _s("late final Database db;", "set before first use"),
    _s("assert(index >= 0, 'index must not be negative');", "a development check"),
    _s("Widget build(BuildContext context) {", "the method every widget has"),
)

SQL_CODE: tuple[Passage, ...] = (
    _s("SELECT name, email FROM users WHERE active = 1;", "the shape of a query"),
    _s("SELECT COUNT(*) FROM orders WHERE total > 100;", "counting rows"),
    _s("SELECT user_id, SUM(total) FROM orders GROUP BY user_id;", "a total per user"),
    _s("HAVING SUM(total) > 500", "filtering after the grouping"),
    _s("ORDER BY created_at DESC LIMIT 10;", "the ten most recent"),
    _s("INNER JOIN orders ON orders.user_id = users.id", "matching rows in both"),
    _s("LEFT JOIN payments ON payments.order_id = orders.id", "keep rows with no match"),
    _s("INSERT INTO users (name, email) VALUES (?, ?);", "a parameterised insert"),
    _s("UPDATE users SET active = 0 WHERE last_seen < '2024-01-01';", "an update with a limit on it"),
    _s("DELETE FROM sessions WHERE expires_at < NOW();", "clearing out the stale"),
    _s("CREATE INDEX idx_orders_user ON orders (user_id);", "make the join fast"),
    _s("SELECT * FROM users WHERE email IS NULL;", "why you cannot write = NULL"),
    _s("WITH recent AS (SELECT * FROM orders LIMIT 100)", "a named subquery"),
    _s("COALESCE(nickname, name, 'anonymous')", "the first thing that isn't null"),
    _s("BEGIN; UPDATE accounts SET balance = balance - 10; COMMIT;", "all or nothing"),
)

ALL_SNIPPETS = (
    SCHOOL
    + TRICKS
    + VISUALS
    + FRACTALS
    + USEFUL
    + PYTHON_CODE
    + JAVASCRIPT_CODE
    + DART_CODE
    + SQL_CODE
)
