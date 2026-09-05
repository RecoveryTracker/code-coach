"""The harder variants: the moves that are one step past the pattern.

Pages 289-318 covered the thirteen interview patterns. These are the ones
that show up when a problem is a little more than its pattern — a window
that has to remember its maximum, a search that runs over answers rather
than over data, a structure built specifically because the obvious one is
too slow.

Four of these are worth the tier on their own. Binary search on the answer
is the trick nobody sees coming: the thing you search is not the input at
all. Union-find is almost cheating for connectivity questions. A trie turns
prefix questions from a scan into a walk. And the monotonic deque is the
one that makes sliding-window maximum linear when every obvious approach is
not.

Python only, and every program prints a definite answer worked out twice —
once by the emitted code and once here, independently.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("algo_grid_flood", "spreading out across a grid"),
    Shape("algo_window_max", "a window that remembers its largest"),
    Shape("algo_intervals_pick", "taking as many as will fit"),
    Shape("algo_lcs", "the longest run two sequences share"),
    Shape("algo_search_answer", "searching the answers, not the data"),
    Shape("algo_two_heaps", "the middle value, kept as things arrive"),
    Shape("algo_union_find", "joining groups and asking what is connected"),
    Shape("algo_trie", "a tree of prefixes"),
    Shape("algo_prefix_matrix", "totals over a rectangle"),
    Shape("algo_dijkstra", "the cheapest way, not the shortest"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _grid(rows) -> str:
    return "[\n" + "".join(f"    {list(r)!r},\n" for r in rows) + "]"


def _pairs(items) -> str:
    return "[" + ", ".join(f"({a}, {b})" for a, b in items) + "]"


# ── 319. Spreading across a grid ─────────────────────────────


def _grid_flood(a: dict) -> str:
    return _lines(
        f"grid = {_grid(a['grid'])}",
        "rows, cols = len(grid), len(grid[0])",
        "seen = set()",
        "",
        "def spread(start):",
        "    stack = [start]",
        "    size = 0",
        "    while stack:",
        "        r, c = stack.pop()",
        "        if (r, c) in seen:",
        "            continue",
        "        seen.add((r, c))",
        "        size += 1",
        "        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):",
        "            nr, nc = r + dr, c + dc",
        "            if 0 <= nr < rows and 0 <= nc < cols:",
        "                if grid[nr][nc] == 1 and (nr, nc) not in seen:",
        "                    stack.append((nr, nc))",
        "    return size",
        "",
        "islands = 0",
        "biggest = 0",
        "for r in range(rows):",
        "    for c in range(cols):",
        "        if grid[r][c] == 1 and (r, c) not in seen:",
        "            islands += 1",
        "            biggest = max(biggest, spread((r, c)))",
        "",
        "print(islands)",
        "print(biggest)",
    )


# ── 320. A window that remembers its largest ─────────────────


def _window_max(a: dict) -> str:
    return _lines(
        "from collections import deque",
        "",
        f"numbers = {_nums(a['items'])}",
        f"width = {a['width']}",
        "window = deque()",
        "answers = []",
        "for i, number in enumerate(numbers):",
        "    while window and numbers[window[-1]] <= number:",
        "        window.pop()",
        "    window.append(i)",
        "    if window[0] <= i - width:",
        "        window.popleft()",
        "    if i >= width - 1:",
        "        answers.append(numbers[window[0]])",
        "",
        'print(", ".join(str(n) for n in answers))',
        "print(max(answers))",
    )


# ── 321. Taking as many as will fit ──────────────────────────


def _intervals_pick(a: dict) -> str:
    return _lines(
        f"spans = {_pairs(a['spans'])}",
        "spans.sort(key=lambda span: span[1])",
        "taken = []",
        "last_end = None",
        "for start, end in spans:",
        "    if last_end is None or start >= last_end:",
        "        taken.append((start, end))",
        "        last_end = end",
        "",
        "print(len(taken))",
        'print(", ".join(f"{s}-{e}" for s, e in taken))',
    )


# ── 322. The longest run two sequences share ─────────────────


def _lcs(a: dict) -> str:
    return _lines(
        f"first = {a['first']!r}",
        f"second = {a['second']!r}",
        "rows, cols = len(first), len(second)",
        "table = [[0] * (cols + 1) for _ in range(rows + 1)]",
        "for i in range(1, rows + 1):",
        "    for j in range(1, cols + 1):",
        "        if first[i - 1] == second[j - 1]:",
        "            table[i][j] = table[i - 1][j - 1] + 1",
        "        else:",
        "            table[i][j] = max(table[i - 1][j], table[i][j - 1])",
        "",
        "print(table[rows][cols])",
        "print(rows * cols)",
    )


# ── 323. Searching the answers ───────────────────────────────


def _search_answer(a: dict) -> str:
    return _lines(
        f"weights = {_nums(a['weights'])}",
        f"days = {a['days']}",
        "",
        "def days_needed(capacity):",
        "    used, load = 1, 0",
        "    for weight in weights:",
        "        if load + weight > capacity:",
        "            used += 1",
        "            load = 0",
        "        load += weight",
        "    return used",
        "",
        "low, high = max(weights), sum(weights)",
        "while low < high:",
        "    mid = (low + high) // 2",
        "    if days_needed(mid) <= days:",
        "        high = mid",
        "    else:",
        "        low = mid + 1",
        "",
        "print(low)",
        "print(days_needed(low))",
    )


# ── 324. The middle value as things arrive ───────────────────


def _two_heaps(a: dict) -> str:
    return _lines(
        "import heapq",
        "",
        f"numbers = {_nums(a['items'])}",
        "low, high = [], []",
        "middles = []",
        "for number in numbers:",
        "    heapq.heappush(low, -number)",
        "    heapq.heappush(high, -heapq.heappop(low))",
        "    if len(high) > len(low):",
        "        heapq.heappush(low, -heapq.heappop(high))",
        "    if len(low) > len(high):",
        "        middles.append(-low[0])",
        "    else:",
        "        middles.append((-low[0] + high[0]) / 2)",
        "",
        'print(", ".join(str(m) for m in middles))',
        "print(middles[-1])",
    )


# ── 325. Joining groups ──────────────────────────────────────


def _union_find(a: dict) -> str:
    return _lines(
        f"count = {a['count']}",
        f"joins = {_pairs(a['joins'])}",
        "parent = list(range(count))",
        "",
        "def find(x):",
        "    while parent[x] != x:",
        "        parent[x] = parent[parent[x]]",
        "        x = parent[x]",
        "    return x",
        "",
        "def union(a, b):",
        "    ra, rb = find(a), find(b)",
        "    if ra == rb:",
        "        return False",
        "    parent[rb] = ra",
        "    return True",
        "",
        "merged = 0",
        "for a, b in joins:",
        "    if union(a, b):",
        "        merged += 1",
        "",
        "groups = len({find(i) for i in range(count)})",
        "print(groups)",
        "print(merged)",
        f"print(find({a['ask'][0]}) == find({a['ask'][1]}))",
    )


# ── 326. A tree of prefixes ──────────────────────────────────


def _trie(a: dict) -> str:
    words = ", ".join(repr(w) for w in a["words"])
    return _lines(
        f"words = [{words}]",
        "root = {}",
        "for word in words:",
        "    node = root",
        "    for letter in word:",
        "        node = node.setdefault(letter, {})",
        '    node["."] = True',
        "",
        "def starting(prefix):",
        "    node = root",
        "    for letter in prefix:",
        "        if letter not in node:",
        "            return 0",
        "        node = node[letter]",
        "    stack, found = [node], 0",
        "    while stack:",
        "        here = stack.pop()",
        "        for key, value in here.items():",
        '            if key == ".":',
        "                found += 1",
        "            else:",
        "                stack.append(value)",
        "    return found",
        "",
        f"print(starting({a['prefix']!r}))",
        f"print(starting({a['missing']!r}))",
        "print(len(root))",
    )


# ── 327. Totals over a rectangle ─────────────────────────────


def _prefix_matrix(a: dict) -> str:
    r1, c1, r2, c2 = a["box"]
    return _lines(
        f"grid = {_grid(a['grid'])}",
        "rows, cols = len(grid), len(grid[0])",
        "running = [[0] * (cols + 1) for _ in range(rows + 1)]",
        "for r in range(rows):",
        "    for c in range(cols):",
        "        running[r + 1][c + 1] = (",
        "            grid[r][c]",
        "            + running[r][c + 1]",
        "            + running[r + 1][c]",
        "            - running[r][c]",
        "        )",
        "",
        "def total(r1, c1, r2, c2):",
        "    return (",
        "        running[r2 + 1][c2 + 1]",
        "        - running[r1][c2 + 1]",
        "        - running[r2 + 1][c1]",
        "        + running[r1][c1]",
        "    )",
        "",
        f"print(total({r1}, {c1}, {r2}, {c2}))",
        "print(total(0, 0, rows - 1, cols - 1))",
    )


# ── 328. The cheapest way ────────────────────────────────────


def _dijkstra(a: dict) -> str:
    edges = ", ".join(f"({x!r}, {y!r}, {w})" for x, y, w in a["edges"])
    return _lines(
        "import heapq",
        "",
        f"edges = [{edges}]",
        "graph = {}",
        "for here, there, cost in edges:",
        "    graph.setdefault(here, []).append((there, cost))",
        "    graph.setdefault(there, []).append((here, cost))",
        "",
        f"start, goal = {a['start']!r}, {a['goal']!r}",
        "best = {start: 0}",
        "queue = [(0, start)]",
        "while queue:",
        "    so_far, here = heapq.heappop(queue)",
        "    if so_far > best.get(here, so_far + 1):",
        "        continue",
        "    for there, cost in graph.get(here, []):",
        "        stepped = so_far + cost",
        "        if stepped < best.get(there, stepped + 1):",
        "            best[there] = stepped",
        "            heapq.heappush(queue, (stepped, there))",
        "",
        "print(best[goal])",
        "print(len(best))",
    )


_BUILDERS = {
    "algo_grid_flood": _grid_flood,
    "algo_window_max": _window_max,
    "algo_intervals_pick": _intervals_pick,
    "algo_lcs": _lcs,
    "algo_search_answer": _search_answer,
    "algo_two_heaps": _two_heaps,
    "algo_union_find": _union_find,
    "algo_trie": _trie,
    "algo_prefix_matrix": _prefix_matrix,
    "algo_dijkstra": _dijkstra,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out here, independently of the emitted program.

    The guards on this tier are mostly about whether the harder structure
    was needed: a sliding-window maximum where the answer never changes, a
    union-find where everything was already connected, a Dijkstra where the
    cheapest route is also the one with fewest hops and a plain BFS would
    have done.
    """
    a = args
    lines: list[str] = []

    if shape == "algo_grid_flood":
        grid = [list(r) for r in a["grid"]]
        rows, cols = len(grid), len(grid[0])
        seen: set = set()

        def spread(start):
            stack, size = [start], 0
            while stack:
                r, c = stack.pop()
                if (r, c) in seen:
                    continue
                seen.add((r, c))
                size += 1
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] == 1 and (nr, nc) not in seen:
                            stack.append((nr, nc))
            return size

        islands = biggest = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 1 and (r, c) not in seen:
                    islands += 1
                    biggest = max(biggest, spread((r, c)))
        if islands < 2:
            raise ValueError("there must be more than one island to count")
        if biggest < 2:
            raise ValueError("some island must be bigger than a single cell")
        lines = [str(islands), str(biggest)]

    elif shape == "algo_window_max":
        items, width = list(a["items"]), a["width"]
        if width >= len(items):
            raise ValueError("the window must be narrower than the list")
        answers = [max(items[i:i + width])
                   for i in range(len(items) - width + 1)]
        if len(set(answers)) < 2:
            raise ValueError("the maximum must change as the window moves")
        lines = [", ".join(str(n) for n in answers), str(max(answers))]

    elif shape == "algo_intervals_pick":
        spans = sorted((tuple(s) for s in a["spans"]), key=lambda s: s[1])
        taken, last_end = [], None
        for start, end in spans:
            if last_end is None or start >= last_end:
                taken.append((start, end))
                last_end = end
        if len(taken) == len(spans):
            raise ValueError("some span must have to be turned away")
        if len(taken) < 2:
            raise ValueError("more than one must fit, or there is no choosing")
        lines = [str(len(taken)),
                 ", ".join(f"{s}-{e}" for s, e in taken)]

    elif shape == "algo_lcs":
        first, second = a["first"], a["second"]
        rows, cols = len(first), len(second)
        table = [[0] * (cols + 1) for _ in range(rows + 1)]
        for i in range(1, rows + 1):
            for j in range(1, cols + 1):
                if first[i - 1] == second[j - 1]:
                    table[i][j] = table[i - 1][j - 1] + 1
                else:
                    table[i][j] = max(table[i - 1][j], table[i][j - 1])
        best = table[rows][cols]
        if best == 0:
            raise ValueError("the two must share something")
        if best == min(rows, cols):
            raise ValueError(
                "one being contained in the other makes this a plain search"
            )
        lines = [str(best), str(rows * cols)]

    elif shape == "algo_search_answer":
        weights, days = list(a["weights"]), a["days"]

        def needed(capacity):
            used, load = 1, 0
            for w in weights:
                if load + w > capacity:
                    used += 1
                    load = 0
                load += w
            return used

        low, high = max(weights), sum(weights)
        if days < 2 or days >= len(weights):
            raise ValueError("the number of days must force real packing")
        while low < high:
            mid = (low + high) // 2
            if needed(mid) <= days:
                high = mid
            else:
                low = mid + 1
        if low == max(weights):
            raise ValueError("the answer must be more than the biggest item")
        if low == sum(weights):
            raise ValueError("the answer must be less than carrying everything")
        lines = [str(low), str(needed(low))]

    elif shape == "algo_two_heaps":
        items = list(a["items"])
        middles = []
        for i in range(1, len(items) + 1):
            window = sorted(items[:i])
            mid = len(window) // 2
            middles.append(
                window[mid] if len(window) % 2 else (window[mid - 1] + window[mid]) / 2
            )
        if len(set(middles)) < 3:
            raise ValueError("the middle must actually move as values arrive")
        lines = [", ".join(str(m) for m in middles), str(middles[-1])]

    elif shape == "algo_union_find":
        count, joins = a["count"], [tuple(j) for j in a["joins"]]
        parent = list(range(count))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        merged = 0
        for x, y in joins:
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[ry] = rx
                merged += 1
        groups = len({find(i) for i in range(count)})
        if groups < 2:
            raise ValueError("something must stay separate")
        if merged == len(joins):
            raise ValueError(
                "one join must be redundant, or nothing is being detected"
            )
        lines = [str(groups), str(merged),
                 str(find(a["ask"][0]) == find(a["ask"][1]))]

    elif shape == "algo_trie":
        words = list(a["words"])
        hits = sum(1 for w in words if w.startswith(a["prefix"]))
        if hits < 2:
            raise ValueError("the prefix must be shared by more than one word")
        if hits == len(words):
            raise ValueError("some word must not share the prefix")
        if any(w.startswith(a["missing"]) for w in words):
            raise ValueError("the missing prefix must really be missing")
        firsts = len({w[0] for w in words})
        lines = [str(hits), "0", str(firsts)]

    elif shape == "algo_prefix_matrix":
        grid = [list(r) for r in a["grid"]]
        r1, c1, r2, c2 = a["box"]
        rows, cols = len(grid), len(grid[0])
        if not (0 <= r1 <= r2 < rows and 0 <= c1 <= c2 < cols):
            raise ValueError("the rectangle must lie inside the grid")
        if (r1, c1, r2, c2) == (0, 0, rows - 1, cols - 1):
            raise ValueError("the rectangle must be smaller than the whole grid")
        box = sum(grid[r][c] for r in range(r1, r2 + 1)
                  for c in range(c1, c2 + 1))
        whole = sum(v for row in grid for v in row)
        lines = [str(box), str(whole)]

    elif shape == "algo_dijkstra":
        import heapq

        graph: dict = {}
        for here, there, cost in a["edges"]:
            graph.setdefault(here, []).append((there, cost))
            graph.setdefault(there, []).append((here, cost))
        start, goal = a["start"], a["goal"]
        best = {start: 0}
        queue = [(0, start)]
        while queue:
            so_far, here = heapq.heappop(queue)
            if so_far > best.get(here, so_far + 1):
                continue
            for there, cost in graph.get(here, []):
                stepped = so_far + cost
                if stepped < best.get(there, stepped + 1):
                    best[there] = stepped
                    heapq.heappush(queue, (stepped, there))
        if goal not in best:
            raise ValueError("the goal must be reachable")
        # Fewest-hops, to check the weights are doing something.
        from collections import deque

        hops = {start: 0}
        q = deque([start])
        while q:
            here = q.popleft()
            for there, _ in graph.get(here, []):
                if there not in hops:
                    hops[there] = hops[here] + 1
                    q.append(there)
        cheap_hops = _hops_of_cheapest(graph, start, goal, best)
        if cheap_hops == hops.get(goal):
            raise ValueError(
                "the cheapest route must differ from the one with fewest "
                "hops, or a plain breadth-first walk would have answered it"
            )
        lines = [str(best[goal]), str(len(best))]
    else:
        raise KeyError(shape)
    return NL.join(lines)


def _hops_of_cheapest(graph, start, goal, best) -> int:
    """How many edges the cheapest route uses, walked back from the goal."""
    here, steps = goal, 0
    while here != start:
        for there, cost in graph.get(here, []):
            if best.get(there, None) is not None and \
                    best[there] + cost == best[here]:
                here = there
                steps += 1
                break
        else:  # pragma: no cover - unreachable for a connected best map
            return -1
    return steps
