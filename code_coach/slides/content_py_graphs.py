"""Graphs: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 123

G6 = 'g = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": ["F"], "F": []}\n'

DECK = Deck(
    id="py-graphs",
    title="Graphs",
    language="python",
    blurb="Adjacency lists, BFS and DFS, components, cycles, islands, topological order and Dijkstra.",
    slides=(
        Slide(
            title="A graph as an adjacency list",
            text="Store each node as a dict key whose value is the list of its neighbours. Looking up who a node connects to is then one dict access.",
            code=r"""graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
print(graph["A"])
print(graph["D"])
print("C" in graph["A"])""",
            output="['B', 'C']\n[]\nTrue",
            point="graph[node] gives the neighbours; a node with none maps to an empty list.",
        ),
        Slide(
            title="From an edge list to adjacency",
            text="Problems often give pairs like (1, 2). Loop over them and file each one under its nodes; setdefault creates the list the first time a node appears.",
            code=r"""edges = [(1, 2), (1, 3), (2, 3), (4, 5)]
adj = {}
for a, b in edges:
    adj.setdefault(a, []).append(b)
    adj.setdefault(b, []).append(a)
print(adj)""",
            output="{1: [2, 3], 2: [1, 3], 3: [1, 2], 4: [5], 5: [4]}",
            point="Undirected means two appends per edge, one for each direction.",
        ),
        Slide(
            title="Directed versus undirected",
            text="In a directed graph an edge a to b can only be followed one way. For an undirected graph you add the reverse edge too. Same input, two different dicts.",
            code=r"""edges = [("a", "b"), ("b", "c")]
d = {n: [] for n in "abc"}
u = {n: [] for n in "abc"}
for x, y in edges:
    d[x].append(y)
    u[x].append(y); u[y].append(x)
print(d)
print(u)""",
            output="{'a': ['b'], 'b': ['c'], 'c': []}\n{'a': ['b'], 'b': ['a', 'c'], 'c': ['b']}",
            point="Ask first: do edges have a direction? It changes how you build the graph.",
        ),
        Slide(
            title="BFS: visit order",
            text="Breadth-first search uses a queue: take the oldest node, add its unseen neighbours at the back. It visits everything one step away, then two steps away, and so on.",
            code=r"""from collections import deque
""" + G6 + r"""seen, q, order = {"A"}, deque("A"), []
while q:
    n = q.popleft(); order.append(n)
    for m in g[n]:
        if m not in seen: seen.add(m); q.append(m)
print(order)""",
            output="['A', 'B', 'C', 'D', 'E', 'F']",
            point="Mark a node seen when you put it in the queue, not when you take it out.",
        ),
        Slide(
            title="Shortest path in an unweighted graph",
            text="Because BFS reaches nodes in order of distance, the first time you reach a node is the shortest way. Store the distance as you discover each one.",
            code=r"""from collections import deque
""" + G6 + r"""dist, q = {"A": 0}, deque("A")
while q:
    n = q.popleft()
    for m in g[n]:
        if m not in dist: dist[m] = dist[n] + 1; q.append(m)
print(dist)""",
            output="{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 3}",
            point="BFS gives fewest edges. The dist dict doubles as the seen set.",
        ),
        Slide(
            title="DFS, recursive",
            text="Depth-first search goes as deep as it can along one path before backing up. Recursion does the backing up for you; a seen list stops it from revisiting.",
            code=G6 + r"""def dfs(n, seen):
    seen.append(n)
    for m in g[n]:
        if m not in seen: dfs(m, seen)
    return seen
print(dfs("A", []))""",
            output="['A', 'B', 'D', 'F', 'C', 'E']",
            point="DFS dives A, B, D, F, then returns and tries C and E.",
        ),
        Slide(
            title="DFS, iterative with a stack",
            text="Replace the recursion with your own stack and the same walk avoids the recursion limit. Push neighbours in reverse so the first one is popped first, matching the recursive order.",
            code=G6 + r"""stack, seen = ["A"], []
while stack:
    n = stack.pop()
    if n in seen: continue
    seen.append(n)
    stack.extend(reversed(g[n]))
print(seen)""",
            output="['A', 'B', 'D', 'F', 'C', 'E']",
            point="Stack = depth first, queue = breadth first. The rest of the code is almost identical.",
        ),
        Slide(
            title="Counting connected components",
            text="Start a search from every node not yet seen; each new start is a new component. Nodes joined by any chain of edges end up in the same one.",
            code=r"""g = {1: [2], 2: [1, 3], 3: [2], 4: [5], 5: [4], 6: []}
seen, count = set(), 0
for start in g:
    if start in seen: continue
    count += 1; stack = [start]
    while stack:
        n = stack.pop()
        if n not in seen: seen.add(n); stack += g[n]
print(count)""",
            output="3",
            point="Components = how many times the outer loop has to start a fresh search.",
        ),
        Slide(
            title="Cycle in an undirected graph",
            text="While searching, remember which node you came from. Meeting an already-seen node that is not your parent means you found a second way around: a cycle.",
            code=r"""def has_cycle(g):
    seen = set()
    def go(n, p):
        seen.add(n)
        return any(m != p and (m in seen or go(m, n)) for m in g[n])
    return any(go(n, None) for n in g if n not in seen)
print(has_cycle({1: [2], 2: [1, 3], 3: [2]}))
print(has_cycle({1: [2, 3], 2: [1, 3], 3: [1, 2]}))""",
            output="False\nTrue",
            point="Skip the parent, or every edge looks like a cycle back to where you just were.",
        ),
        Slide(
            title="Number of islands on a grid",
            text="A grid is a graph where each cell touches its four neighbours. Walk the cells; each time you meet land, count one island and sink all connected land so it is not counted again.",
            code=r"""def islands(g):
    def sink(r, c):
        if 0 <= r < len(g) and 0 <= c < len(g[0]) and g[r][c] == "1":
            g[r][c] = "0"
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)): sink(r + dr, c + dc)
            return 1
        return 0
    return sum(sink(r, c) for r in range(len(g)) for c in range(len(g[0])))
grid = [list(row) for row in ("110", "010", "001")]
print(islands(grid))""",
            output="2",
            point="Sinking visited land is the 'seen' set; only the first cell of an island returns 1.",
        ),
        Slide(
            title="Topological order (DFS)",
            text="For tasks with 'a before b' rules, run a DFS and add each node to a list after all its followers are done. Reading that list backwards puts every node before the ones that depend on it.",
            code=r"""g = {"shirt": ["tie", "belt"], "tie": ["jacket"], "belt": ["jacket"], "pants": ["belt"], "jacket": []}
order, seen = [], set()
def dfs(n):
    seen.add(n)
    for m in g[n]:
        if m not in seen: dfs(m)
    order.append(n)
for n in g:
    if n not in seen: dfs(n)
print(order[::-1])""",
            output="['pants', 'shirt', 'belt', 'tie', 'jacket']",
            point="Finish-time order, reversed, is a valid topological order of a directed acyclic graph.",
        ),
        Slide(
            title="Dijkstra with heapq",
            text="With weighted edges, always expand the cheapest unfinished node. A heap of (distance, node) pairs hands you that node; the first time a node is popped, its distance is final.",
            code=r"""import heapq
g = {"A": [("B", 1), ("C", 4)], "B": [("C", 2), ("D", 5)], "C": [("D", 1)], "D": []}
dist, heap = {}, [(0, "A")]
while heap:
    d, n = heapq.heappop(heap)
    if n in dist: continue
    dist[n] = d
    for m, w in g[n]: heapq.heappush(heap, (d + w, m))
print(dist)""",
            output="{'A': 0, 'B': 1, 'C': 3, 'D': 4}",
            point="Dijkstra is BFS with a priority queue; it needs non-negative weights.",
        ),
        Slide(
            title="Bipartite check",
            text="Can the nodes be coloured with two colours so every edge joins different colours? Colour a start node, give its neighbours the opposite colour, and fail if an edge joins two equal ones.",
            code=r"""def bipartite(g, s):
    color, stack = {s: 0}, [s]
    while stack:
        n = stack.pop()
        for m in g[n]:
            if m not in color: color[m] = 1 - color[n]; stack.append(m)
            elif color[m] == color[n]: return False
    return True
square = {1: [2, 4], 2: [1, 3], 3: [2, 4], 4: [1, 3]}; tri = {1: [2, 3], 2: [1, 3], 3: [1, 2]}
print(bipartite(square, 1), bipartite(tri, 1))""",
            output="True False",
            point="A graph is bipartite exactly when it has no odd-length cycle (a triangle fails).",
        ),
        Slide(
            title="Graph as a dict of sets",
            text="If you need fast 'is there an edge?' checks and easy removal, store neighbours in sets. Adding twice does nothing, and discard removes without raising an error.",
            code=r"""g = {}
for a, b in [(1, 2), (2, 3), (1, 3)]:
    g.setdefault(a, set()).add(b)
    g.setdefault(b, set()).add(a)
print(3 in g[1], sorted(g[2]))
g[1].discard(3); g[3].discard(1)
print(sorted(g[1]), 2 in g[3])""",
            output="True [1, 3]\n[2] True",
            point="Sets give O(1) edge lookup and no duplicate edges; print them with sorted().",
        ),
        Slide(
            title="Tracing a path back with parents",
            text="During BFS, remember who discovered each node. To get the actual path, start at the target and follow parents back to the start, then reverse the list.",
            code=r"""from collections import deque
g = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": ["E"], "E": []}
parent, q = {"A": None}, deque("A")
while q:
    n = q.popleft()
    for m in g[n]:
        if m not in parent: parent[m] = n; q.append(m)
path, n = [], "E"
while n: path.append(n); n = parent[n]
print(path[::-1])""",
            output="['A', 'B', 'D', 'E']",
            point="A parent dict is both the seen set and the breadcrumb trail back to the start.",
        ),
    ),
)
