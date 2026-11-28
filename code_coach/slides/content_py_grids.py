"""Grids and Matrices: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 126

DECK = Deck(
    id="py-grids",
    title="Grids and Matrices",
    language="python",
    blurb="Lists of lists: neighbours, transpose, rotate, spiral, flood fill, prefix sums and Game of Life.",
    slides=(
        Slide(
            title="A grid is a list of lists",
            text="Each inner list is one row. grid[row][col] picks a cell: first choose the row, then the column in it. len(grid) is the number of rows and len(grid[0]) the number of columns.",
            code=r"""grid = [[1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]]
print(grid[1][2])
print(len(grid), len(grid[0]))""",
            output="6\n3 3",
            point="Row first, then column: grid[r][c].",
        ),
        Slide(
            title="Creating a grid correctly",
            text="Multiplying a list of lists copies the reference, not the row, so every row is the very same list. Build each row separately with a comprehension.",
            code=r"""bad = [[0] * 3] * 3
bad[0][0] = 1
print(bad)
good = [[0] * 3 for _ in range(3)]
good[0][0] = 1
print(good)""",
            output="[[1, 0, 0], [1, 0, 0], [1, 0, 0]]\n[[1, 0, 0], [0, 0, 0], [0, 0, 0]]",
            point="[[0]*3 for _ in range(3)] makes three separate rows; [[0]*3]*3 makes one row three times.",
        ),
        Slide(
            title="Rows and columns",
            text="A row is just grid[r]. A column has no shortcut, so collect the same index from every row with a comprehension. Sums per row and per column are two small loops.",
            code=r"""g = [[1, 2, 3], [4, 5, 6]]
print(g[1])
print([row[0] for row in g])
print([sum(row) for row in g])
print([sum(row[c] for row in g) for c in range(3)])""",
            output="[4, 5, 6]\n[1, 4]\n[6, 15]\n[5, 7, 9]",
            point="Rows are cheap lists; columns are built by reaching into every row.",
        ),
        Slide(
            title="Visiting every cell with enumerate",
            text="Loop over rows with enumerate to get the row number, then over each row with enumerate to get the column number. This is how you find a start cell or collect coordinates.",
            code=r"""g = ["S.#", "..E"]
for r, row in enumerate(g):
    for c, ch in enumerate(row):
        if ch in "SE": print(ch, "at", (r, c))""",
            output="S at (0, 0)\nE at (1, 2)",
            point="Two nested enumerate calls give you (r, c) and the value together.",
        ),
        Slide(
            title="Neighbours with direction tuples",
            text="List the four moves once as (row change, column change) pairs, then add each to the current cell. Always check the new position is inside the grid before reading it.",
            code=r"""g = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
def around(r, c):
    return [g[r + dr][c + dc] for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            if 0 <= r + dr < len(g) and 0 <= c + dc < len(g[0])]
print(around(0, 0))
print(around(1, 1))""",
            output="[4, 2]\n[2, 8, 4, 6]",
            point="Directions as data plus a bounds check: the same pattern drives BFS, DFS and flood fill.",
        ),
        Slide(
            title="Transposing with zip(*grid)",
            text="Unpacking the rows with * hands them to zip, which pairs up the first items, then the second items, and so on. Those pairs are the columns, so rows and columns swap.",
            code=r"""g = [[1, 2, 3], [4, 5, 6]]
print(list(zip(*g)))
print([list(col) for col in zip(*g)])""",
            output="[(1, 4), (2, 5), (3, 6)]\n[[1, 4], [2, 5], [3, 6]]",
            point="zip(*grid) turns rows into columns; wrap each in list() to get lists, not tuples.",
        ),
        Slide(
            title="Rotating 90 degrees",
            text="Clockwise: reverse the order of the rows, then transpose. Anticlockwise: transpose, then reverse the order of the rows. Each is one line.",
            code=r"""g = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print([list(r) for r in zip(*g[::-1])])
print([list(r) for r in zip(*g)][::-1])""",
            output="[[7, 4, 1], [8, 5, 2], [9, 6, 3]]\n[[3, 6, 9], [2, 5, 8], [1, 4, 7]]",
            point="Rotate clockwise = reverse rows, then transpose.",
        ),
        Slide(
            title="Spiral order",
            text="Peel the top row off, then rotate what is left anticlockwise so the next edge is on top, and repeat. When nothing is left, the list you collected is the spiral.",
            code=r"""def spiral(m):
    out = []
    while m:
        out += m.pop(0)
        m = [list(r) for r in zip(*m)][::-1]
    return out
print(spiral([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))""",
            output="[1, 2, 3, 6, 9, 8, 7, 4, 5]",
            point="Take a row, rotate, repeat: a spiral is just 'top row' over and over.",
        ),
        Slide(
            title="Diagonals",
            text="The main diagonal has equal row and column, the other has row plus column equal to size minus 1. Cells on one diagonal all share the same r - c, so use that as a dict key to group them.",
            code=r"""g = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
n = 3
print([g[i][i] for i in range(n)])
print([g[i][n - 1 - i] for i in range(n)])
d = {}
for r in range(n):
    for c in range(n): d.setdefault(r - c, []).append(g[r][c])
print(d)""",
            output="[1, 5, 9]\n[3, 5, 7]\n{0: [1, 5, 9], -1: [2, 6], -2: [3], 1: [4, 8], 2: [7]}",
            point="Same r - c means same diagonal; same r + c means same anti-diagonal.",
        ),
        Slide(
            title="Flood fill",
            text="Starting from one cell, repaint every connected cell that has the same colour. Recurse into the four neighbours, but only into cells that are in bounds and still the old colour.",
            code=r"""def fill(g, r, c, new):
    old = g[r][c]
    def go(r, c):
        if 0 <= r < len(g) and 0 <= c < len(g[0]) and g[r][c] == old:
            g[r][c] = new
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)): go(r + dr, c + dc)
    if old != new: go(r, c)
g = [[1, 1, 0], [1, 0, 0], [1, 1, 1]]
fill(g, 0, 0, 7)
print(g)""",
            output="[[7, 7, 0], [7, 0, 0], [7, 7, 7]]",
            point="Repainting is the 'seen' marker. Guard old != new, or it recurses forever.",
        ),
        Slide(
            title="Counting cells that match",
            text="Flatten with a double loop inside a generator and count or sum. A comparison gives True or False, and True counts as 1.",
            code=r"""from collections import Counter
g = [[1, 0, 2], [2, 2, 0]]
print(sum(row.count(2) for row in g))
print(sum(v == 0 for row in g for v in row))
print(sorted(Counter(v for row in g for v in row).items()))""",
            output="3\n2\n[(0, 2), (1, 1), (2, 3)]",
            point="for row in g for v in row visits every cell in one expression.",
        ),
        Slide(
            title="2D prefix sums",
            text="Let P[r][c] hold the sum of everything above and left of that spot. Then the sum of any rectangle is four lookups: add the big corner, subtract the two strips, add back the overlap.",
            code=r"""g = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
P = [[0] * 4 for _ in range(4)]
for r in range(3):
    for c in range(3): P[r+1][c+1] = g[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]
def box(r1, c1, r2, c2): return P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
print(box(0, 0, 2, 2), box(1, 1, 2, 2))""",
            output="45 28",
            point="Build once in O(rows x cols), then answer any rectangle sum in O(1).",
        ),
        Slide(
            title="Searching a sorted matrix",
            text="If every row and every column is sorted, start at the top-right corner. Too big? Move left. Too small? Move down. Every step removes a whole row or column.",
            code=r"""def find(m, t):
    r, c = 0, len(m[0]) - 1
    while r < len(m) and c >= 0:
        if m[r][c] == t: return True
        r, c = (r + 1, c) if m[r][c] < t else (r, c - 1)
    return False
m = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
print(find(m, 5), find(m, 10))""",
            output="True False",
            point="The top-right corner is the biggest in its row and smallest in its column: it decides the move.",
        ),
        Slide(
            title="Printing a grid nicely",
            text="Turn each row into one string with join, and print it. Choose characters that make the picture easy to read, such as # for a wall and a dot for floor.",
            code=r"""g = [[1, 0, 1], [0, 1, 0]]
for row in g: print(" ".join(str(v) for v in row))
for row in g: print("".join("#" if v else "." for v in row))""",
            output="1 0 1\n0 1 0\n#.#\n.#.",
            point="join needs strings, so convert numbers first. A picture beats a nested list when debugging.",
        ),
        Slide(
            title="Game of Life: one step",
            text="Count each cell's eight neighbours. A cell is alive next step if it has exactly 3 live neighbours, or if it is alive now and has exactly 2. Build a new grid; do not edit the old one.",
            code=r"""def step(g):
    R, C = len(g), len(g[0])
    def n(r, c): return sum(g[r+dr][c+dc] for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                            if (dr or dc) and 0 <= r+dr < R and 0 <= c+dc < C)
    return [[int(n(r, c) == 3 or (g[r][c] and n(r, c) == 2)) for c in range(C)] for r in range(R)]
print(step([[0, 1, 0], [0, 1, 0], [0, 1, 0]]))""",
            output="[[0, 0, 0], [1, 1, 1], [0, 0, 0]]",
            point="Compute the next generation into a fresh grid, or half-updated cells corrupt the count.",
        ),
    ),
)
