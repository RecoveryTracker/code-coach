"""
C patterns 9 to 13, the last of them. `problems_c.PATTERNS` stitches all
thirteen together.

Two things C makes you bring yourself show up here. Top-K needs a priority
queue, so `c_common` supplies a binary min-heap — qsort would work but turns
an O(n log k) answer into O(n log n), and the pattern is about the heap.
Backtracking has to return an array of arrays, so every solution in it also
hands back the row count and the width of each row.
"""

from __future__ import annotations

from code_coach.leetcode.c_common import (
    CTYPE,
    INT_HEAP,
    INT_MAP,
    LIMITS,
    STDBOOL,
    STDLIB,
    STRING_H,
    _p,
)
from code_coach.leetcode.problems import Pattern

# ── 9. Graphs and grids ─────────────────────────────────────

_GRAPH = Pattern(
    id="lc-graph",
    name="Graphs & Grids",
    order=9,
    blurb="Same DFS/BFS as trees, but you must mark visited - graphs have cycles.",
    tell="A grid of cells, or nodes with edges/neighbours.",
    preamble=(STDLIB, STRING_H, STDBOOL, LIMITS),
    problems=(
        _p(
            733, "Flood Fill", "Easy",
            "Recurse to the four neighbours, stopping when the colour doesn't "
            "match. The grid's width travels beside it, as always.",
            "O(n) time, O(n) space",
            """
            static void fillFrom(int **image, int rows, int cols, int r, int c,
                                 int start, int color) {
                if (r < 0 || r >= rows || c < 0 || c >= cols) {
                    return;
                }
                if (image[r][c] != start) {
                    return;
                }
                image[r][c] = color;
                fillFrom(image, rows, cols, r + 1, c, start, color);
                fillFrom(image, rows, cols, r - 1, c, start, color);
                fillFrom(image, rows, cols, r, c + 1, start, color);
                fillFrom(image, rows, cols, r, c - 1, start, color);
            }

            int **floodFill(int **image, int imageSize, int *imageColSize,
                            int sr, int sc, int color, int *returnSize,
                            int **columnSizes) {
                int start = image[sr][sc];
                if (start != color) {
                    fillFrom(image, imageSize, imageColSize[0], sr, sc, start,
                             color);
                }
                *returnSize = imageSize;
                *columnSizes = imageColSize;
                return image;
            }
            """,
        ),
        _p(
            200, "Number of Islands", "Medium",
            "Each unvisited land cell starts an island; sink the whole thing.",
            "O(rows * cols) time, O(rows * cols) space",
            """
            static void sink(char **grid, int rows, int cols, int r, int c) {
                if (r < 0 || r >= rows || c < 0 || c >= cols) {
                    return;
                }
                if (grid[r][c] != '1') {
                    return;
                }
                grid[r][c] = '0';
                sink(grid, rows, cols, r + 1, c);
                sink(grid, rows, cols, r - 1, c);
                sink(grid, rows, cols, r, c + 1);
                sink(grid, rows, cols, r, c - 1);
            }

            int numIslands(char **grid, int gridSize, int *gridColSize) {
                if (gridSize == 0) {
                    return 0;
                }
                int cols = gridColSize[0];
                int count = 0;
                for (int r = 0; r < gridSize; r++) {
                    for (int c = 0; c < cols; c++) {
                        if (grid[r][c] == '1') {
                            count++;
                            sink(grid, gridSize, cols, r, c);
                        }
                    }
                }
                return count;
            }
            """,
        ),
        _p(
            994, "Rotting Oranges", "Medium",
            "Multi-source BFS - every rotten orange starts in the queue at "
            "minute 0.",
            "O(rows * cols) time, O(rows * cols) space",
            """
            int orangesRotting(int **grid, int gridSize, int *gridColSize) {
                int rows = gridSize;
                int cols = gridColSize[0];
                int *queue = malloc(rows * cols * sizeof(int));
                int head = 0;
                int tail = 0;
                int fresh = 0;
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
                        if (grid[r][c] == 2) {
                            queue[tail++] = r * cols + c;
                        } else if (grid[r][c] == 1) {
                            fresh++;
                        }
                    }
                }
                int minutes = 0;
                int dr[] = {1, -1, 0, 0};
                int dc[] = {0, 0, 1, -1};
                while (head < tail && fresh > 0) {
                    minutes++;
                    int size = tail - head;
                    for (int i = 0; i < size; i++) {
                        int cell = queue[head++];
                        int r = cell / cols;
                        int c = cell % cols;
                        for (int d = 0; d < 4; d++) {
                            int nr = r + dr[d];
                            int nc = c + dc[d];
                            if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) {
                                continue;
                            }
                            if (grid[nr][nc] == 1) {
                                grid[nr][nc] = 2;
                                fresh--;
                                queue[tail++] = nr * cols + nc;
                            }
                        }
                    }
                }
                free(queue);
                return fresh > 0 ? -1 : minutes;
            }
            """,
        ),
        _p(
            133, "Clone Graph", "Medium",
            "A lookup from original node to its copy doubles as the visited set "
            "- and must be filled BEFORE recursing, or a cycle never ends.",
            "O(n + e) time, O(n) space",
            """
            struct GraphNode {
                int val;
                int numNeighbors;
                struct GraphNode **neighbors;
            };

            static struct GraphNode *copyNode(struct GraphNode *cur,
                                              struct GraphNode **seen,
                                              struct GraphNode **clones) {
                if (!cur) {
                    return NULL;
                }
                for (int i = 0; seen[i]; i++) {
                    if (seen[i] == cur) {
                        return clones[i];
                    }
                }
                int at = 0;
                while (seen[at]) {
                    at++;
                }
                struct GraphNode *clone = malloc(sizeof(struct GraphNode));
                clone->val = cur->val;
                clone->numNeighbors = cur->numNeighbors;
                clone->neighbors =
                    malloc(cur->numNeighbors * sizeof(struct GraphNode *));
                seen[at] = cur;
                clones[at] = clone;
                for (int i = 0; i < cur->numNeighbors; i++) {
                    clone->neighbors[i] =
                        copyNode(cur->neighbors[i], seen, clones);
                }
                return clone;
            }

            struct GraphNode *cloneGraph(struct GraphNode *node) {
                struct GraphNode *seen[128] = {NULL};
                struct GraphNode *clones[128] = {NULL};
                return copyNode(node, seen, clones);
            }
            """,
        ),
        _p(
            695, "Max Area of Island", "Medium",
            "Same flood fill, but the walk returns a size instead of just "
            "marking cells.",
            "O(m * n) time, O(m * n) space",
            """
            static int islandArea(int **grid, int rows, int cols, int r, int c) {
                if (r < 0 || c < 0 || r >= rows || c >= cols) {
                    return 0;
                }
                if (grid[r][c] != 1) {
                    return 0;
                }
                grid[r][c] = 0;
                return 1 + islandArea(grid, rows, cols, r + 1, c) +
                       islandArea(grid, rows, cols, r - 1, c) +
                       islandArea(grid, rows, cols, r, c + 1) +
                       islandArea(grid, rows, cols, r, c - 1);
            }

            int maxAreaOfIsland(int **grid, int gridSize, int *gridColSize) {
                if (gridSize == 0) {
                    return 0;
                }
                int cols = gridColSize[0];
                int best = 0;
                for (int r = 0; r < gridSize; r++) {
                    for (int c = 0; c < cols; c++) {
                        int area = islandArea(grid, gridSize, cols, r, c);
                        if (area > best) {
                            best = area;
                        }
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            547, "Number of Provinces", "Medium",
            "Every walk that starts somewhere unvisited is one more connected "
            "group.",
            "O(n * n) time, O(n) space",
            """
            static void visitCity(int **isConnected, int n, bool *seen,
                                  int city) {
                seen[city] = true;
                for (int other = 0; other < n; other++) {
                    if (isConnected[city][other] && !seen[other]) {
                        visitCity(isConnected, n, seen, other);
                    }
                }
            }

            int findCircleNum(int **isConnected, int isConnectedSize,
                              int *isConnectedColSize) {
                bool *seen = calloc(isConnectedSize, sizeof(bool));
                int groups = 0;
                for (int city = 0; city < isConnectedSize; city++) {
                    if (!seen[city]) {
                        visitCity(isConnected, isConnectedSize, seen, city);
                        groups++;
                    }
                }
                free(seen);
                return groups;
            }
            """,
        ),
        _p(
            542, "01 Matrix", "Medium",
            "Start the queue from every zero at once, and the first visit is the "
            "nearest one. -1 marks unreached, so no second grid is needed.",
            "O(m * n) time, O(m * n) space",
            """
            int **updateMatrix(int **mat, int matSize, int *matColSize,
                               int *returnSize, int **columnSizes) {
                int rows = matSize;
                int cols = matColSize[0];
                int **out = malloc(rows * sizeof(int *));
                int *sizes = malloc(rows * sizeof(int));
                int *queue = malloc(rows * cols * sizeof(int));
                int head = 0;
                int tail = 0;
                for (int r = 0; r < rows; r++) {
                    out[r] = malloc(cols * sizeof(int));
                    sizes[r] = cols;
                    for (int c = 0; c < cols; c++) {
                        if (mat[r][c] == 0) {
                            out[r][c] = 0;
                            queue[tail++] = r * cols + c;
                        } else {
                            out[r][c] = -1;
                        }
                    }
                }
                int dr[] = {1, -1, 0, 0};
                int dc[] = {0, 0, 1, -1};
                while (head < tail) {
                    int cell = queue[head++];
                    int r = cell / cols;
                    int c = cell % cols;
                    for (int d = 0; d < 4; d++) {
                        int nr = r + dr[d];
                        int nc = c + dc[d];
                        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) {
                            continue;
                        }
                        if (out[nr][nc] == -1) {
                            out[nr][nc] = out[r][c] + 1;
                            queue[tail++] = nr * cols + nc;
                        }
                    }
                }
                free(queue);
                *returnSize = rows;
                *columnSizes = sizes;
                return out;
            }
            """,
        ),
        _p(
            417, "Pacific Atlantic Water Flow", "Medium",
            "Walk uphill from each ocean instead of downhill from each cell; the "
            "answer is the overlap.",
            "O(m * n) time, O(m * n) space",
            """
            static void climb(int **heights, int rows, int cols, int r, int c,
                              bool *seen) {
                seen[r * cols + c] = true;
                int dr[] = {1, -1, 0, 0};
                int dc[] = {0, 0, 1, -1};
                for (int d = 0; d < 4; d++) {
                    int nr = r + dr[d];
                    int nc = c + dc[d];
                    if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) {
                        continue;
                    }
                    if (!seen[nr * cols + nc] &&
                        heights[nr][nc] >= heights[r][c]) {
                        climb(heights, rows, cols, nr, nc, seen);
                    }
                }
            }

            int **pacificAtlantic(int **heights, int heightsSize,
                                  int *heightsColSize, int *returnSize,
                                  int **columnSizes) {
                if (heightsSize == 0) {
                    *returnSize = 0;
                    *columnSizes = NULL;
                    return NULL;
                }
                int rows = heightsSize;
                int cols = heightsColSize[0];
                bool *pacific = calloc(rows * cols, sizeof(bool));
                bool *atlantic = calloc(rows * cols, sizeof(bool));
                for (int c = 0; c < cols; c++) {
                    climb(heights, rows, cols, 0, c, pacific);
                    climb(heights, rows, cols, rows - 1, c, atlantic);
                }
                for (int r = 0; r < rows; r++) {
                    climb(heights, rows, cols, r, 0, pacific);
                    climb(heights, rows, cols, r, cols - 1, atlantic);
                }
                int **both = malloc(rows * cols * sizeof(int *));
                int *sizes = malloc(rows * cols * sizeof(int));
                int total = 0;
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
                        if (pacific[r * cols + c] && atlantic[r * cols + c]) {
                            both[total] = malloc(2 * sizeof(int));
                            both[total][0] = r;
                            both[total][1] = c;
                            sizes[total] = 2;
                            total++;
                        }
                    }
                }
                free(pacific);
                free(atlantic);
                *returnSize = total;
                *columnSizes = sizes;
                return both;
            }
            """,
        ),
    ),
)


# ── 10. Subsets and backtracking ────────────────────────────

_SUBSETS = Pattern(
    id="lc-backtracking",
    name="Subsets & Backtracking",
    order=10,
    blurb="Choose, recurse, un-choose - explore every combination without repeating work.",
    tell="'All subsets / permutations / combinations that ...'",
    preamble=(STDLIB, STRING_H, STDBOOL),
    problems=(
        _p(
            78, "Subsets", "Medium",
            "Every prefix of the walk is already a valid subset - record on "
            "entry. There are 2^n of them, so the answer array can be sized up "
            "front.",
            "O(n * 2^n) time, O(n) recursion depth",
            """
            static void collectSubsets(int *nums, int numsSize, int start,
                                       int *current, int depth, int **result,
                                       int *sizes, int *total) {
                result[*total] = malloc((depth ? depth : 1) * sizeof(int));
                memcpy(result[*total], current, depth * sizeof(int));
                sizes[*total] = depth;
                (*total)++;
                for (int i = start; i < numsSize; i++) {
                    current[depth] = nums[i];
                    collectSubsets(nums, numsSize, i + 1, current, depth + 1,
                                   result, sizes, total);
                }
            }

            int **subsets(int *nums, int numsSize, int *returnSize,
                          int **columnSizes) {
                int capacity = 1 << numsSize;
                int **result = malloc(capacity * sizeof(int *));
                int *sizes = malloc(capacity * sizeof(int));
                int *current = malloc((numsSize ? numsSize : 1) * sizeof(int));
                int total = 0;
                collectSubsets(nums, numsSize, 0, current, 0, result, sizes,
                               &total);
                free(current);
                *returnSize = total;
                *columnSizes = sizes;
                return result;
            }
            """,
        ),
        _p(
            90, "Subsets II", "Medium",
            "Sort first, then skip a duplicate unless it's the first pick at "
            "this level - the guard is i > start, not i > 0.",
            "O(n * 2^n) time, O(n) recursion depth",
            """
            static int ascendingInts(const void *a, const void *b) {
                int x = *(const int *)a;
                int y = *(const int *)b;
                return (x > y) - (x < y);
            }

            static void collectUnique(int *nums, int numsSize, int start,
                                      int *current, int depth, int **result,
                                      int *sizes, int *total) {
                result[*total] = malloc((depth ? depth : 1) * sizeof(int));
                memcpy(result[*total], current, depth * sizeof(int));
                sizes[*total] = depth;
                (*total)++;
                for (int i = start; i < numsSize; i++) {
                    if (i > start && nums[i] == nums[i - 1]) {
                        continue;
                    }
                    current[depth] = nums[i];
                    collectUnique(nums, numsSize, i + 1, current, depth + 1,
                                  result, sizes, total);
                }
            }

            int **subsetsWithDup(int *nums, int numsSize, int *returnSize,
                                 int **columnSizes) {
                qsort(nums, numsSize, sizeof(int), ascendingInts);
                int capacity = 1 << numsSize;
                int **result = malloc(capacity * sizeof(int *));
                int *sizes = malloc(capacity * sizeof(int));
                int *current = malloc((numsSize ? numsSize : 1) * sizeof(int));
                int total = 0;
                collectUnique(nums, numsSize, 0, current, 0, result, sizes,
                              &total);
                free(current);
                *returnSize = total;
                *columnSizes = sizes;
                return result;
            }
            """,
        ),
        _p(
            46, "Permutations", "Medium",
            "Order matters, so track which indexes are already used - and clear "
            "the flag on the way back out.",
            "O(n * n!) time, O(n) recursion depth",
            """
            static void collectPermutations(int *nums, int numsSize, bool *used,
                                            int *current, int depth,
                                            int **result, int *sizes,
                                            int *total) {
                if (depth == numsSize) {
                    result[*total] = malloc(numsSize * sizeof(int));
                    memcpy(result[*total], current, numsSize * sizeof(int));
                    sizes[*total] = numsSize;
                    (*total)++;
                    return;
                }
                for (int i = 0; i < numsSize; i++) {
                    if (used[i]) {
                        continue;
                    }
                    used[i] = true;
                    current[depth] = nums[i];
                    collectPermutations(nums, numsSize, used, current, depth + 1,
                                        result, sizes, total);
                    used[i] = false;
                }
            }

            int **permute(int *nums, int numsSize, int *returnSize,
                          int **columnSizes) {
                int capacity = 1;
                for (int i = 2; i <= numsSize; i++) {
                    capacity *= i;
                }
                int **result = malloc(capacity * sizeof(int *));
                int *sizes = malloc(capacity * sizeof(int));
                bool *used = calloc(numsSize, sizeof(bool));
                int *current = malloc(numsSize * sizeof(int));
                int total = 0;
                collectPermutations(nums, numsSize, used, current, 0, result,
                                    sizes, &total);
                free(used);
                free(current);
                *returnSize = total;
                *columnSizes = sizes;
                return result;
            }
            """,
        ),
        _p(
            39, "Combination Sum", "Medium",
            "Reuse allowed, so recurse with i (not i + 1) and shrink the "
            "remainder.",
            "O(n^(target/min)) time, O(target) depth",
            """
            #define MAX_COMBINATIONS 1024

            static void collectSums(int *candidates, int candidatesSize,
                                    int start, int remaining, int *current,
                                    int depth, int **result, int *sizes,
                                    int *total) {
                if (remaining == 0) {
                    result[*total] = malloc((depth ? depth : 1) * sizeof(int));
                    memcpy(result[*total], current, depth * sizeof(int));
                    sizes[*total] = depth;
                    (*total)++;
                    return;
                }
                if (remaining < 0) {
                    return;
                }
                for (int i = start; i < candidatesSize; i++) {
                    current[depth] = candidates[i];
                    collectSums(candidates, candidatesSize, i,
                                remaining - candidates[i], current, depth + 1,
                                result, sizes, total);
                }
            }

            int **combinationSum(int *candidates, int candidatesSize,
                                 int target, int *returnSize,
                                 int **columnSizes) {
                int **result = malloc(MAX_COMBINATIONS * sizeof(int *));
                int *sizes = malloc(MAX_COMBINATIONS * sizeof(int));
                int *current = malloc((target + 1) * sizeof(int));
                int total = 0;
                collectSums(candidates, candidatesSize, 0, target, current, 0,
                            result, sizes, &total);
                free(current);
                *returnSize = total;
                *columnSizes = sizes;
                return result;
            }
            """,
        ),
        _p(
            79, "Word Search", "Medium",
            "Backtracking on a grid - blank out the cell, recurse, then restore it.",
            "O(rows * cols * 4^len(word)) time, O(len(word)) depth",
            """
            static bool searchFrom(char **board, int rows, int cols,
                                   const char *word, int r, int c, int i) {
                if (word[i] == '\\0') {
                    return true;
                }
                if (r < 0 || r >= rows || c < 0 || c >= cols) {
                    return false;
                }
                if (board[r][c] != word[i]) {
                    return false;
                }
                char saved = board[r][c];
                board[r][c] = '#';
                bool found = searchFrom(board, rows, cols, word, r + 1, c, i + 1) ||
                             searchFrom(board, rows, cols, word, r - 1, c, i + 1) ||
                             searchFrom(board, rows, cols, word, r, c + 1, i + 1) ||
                             searchFrom(board, rows, cols, word, r, c - 1, i + 1);
                board[r][c] = saved;
                return found;
            }

            bool exist(char **board, int boardSize, int *boardColSize,
                       char *word) {
                int cols = boardColSize[0];
                for (int r = 0; r < boardSize; r++) {
                    for (int c = 0; c < cols; c++) {
                        if (searchFrom(board, boardSize, cols, word, r, c, 0)) {
                            return true;
                        }
                    }
                }
                return false;
            }
            """,
        ),
        _p(
            77, "Combinations", "Medium",
            "Only ever pick numbers after the last one taken, so no pair is "
            "built twice.",
            "O(k * C(n, k)) time, O(k) space",
            """
            static void collectCombinations(int n, int k, int start,
                                            int *picked, int depth,
                                            int **out, int *sizes,
                                            int *total) {
                if (depth == k) {
                    out[*total] = malloc(k * sizeof(int));
                    memcpy(out[*total], picked, k * sizeof(int));
                    sizes[*total] = k;
                    (*total)++;
                    return;
                }
                for (int value = start; value <= n; value++) {
                    picked[depth] = value;
                    collectCombinations(n, k, value + 1, picked, depth + 1, out,
                                        sizes, total);
                }
            }

            int **combine(int n, int k, int *returnSize, int **columnSizes) {
                int capacity = 1;
                for (int i = 0; i < k; i++) {
                    capacity = capacity * (n - i) / (i + 1);
                }
                if (capacity < 1) {
                    capacity = 1;
                }
                int **out = malloc(capacity * sizeof(int *));
                int *sizes = malloc(capacity * sizeof(int));
                int *picked = malloc((k ? k : 1) * sizeof(int));
                int total = 0;
                collectCombinations(n, k, 1, picked, 0, out, sizes, &total);
                free(picked);
                *returnSize = total;
                *columnSizes = sizes;
                return out;
            }
            """,
        ),
        _p(
            17, "Letter Combinations of a Phone Number", "Medium",
            "One digit is one level of the tree, and its letters are that "
            "level's branches.",
            "O(4 ** n) time, O(n) space",
            """
            static const char *KEYPAD[10] = {
                "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
            };

            static void walkDigits(const char *digits, int index, char *built,
                                   char **out, int *total) {
                if (digits[index] == '\\0') {
                    built[index] = '\\0';
                    out[*total] = malloc(index + 1);
                    memcpy(out[*total], built, index + 1);
                    (*total)++;
                    return;
                }
                const char *letters = KEYPAD[digits[index] - '0'];
                for (int i = 0; letters[i]; i++) {
                    built[index] = letters[i];
                    walkDigits(digits, index + 1, built, out, total);
                }
            }

            char **letterCombinations(char *digits, int *returnSize) {
                int length = (int)strlen(digits);
                if (length == 0) {
                    *returnSize = 0;
                    return NULL;
                }
                int capacity = 1;
                for (int i = 0; i < length; i++) {
                    capacity *= 4;
                }
                char **out = malloc(capacity * sizeof(char *));
                char *built = malloc(length + 1);
                int total = 0;
                walkDigits(digits, 0, built, out, &total);
                free(built);
                *returnSize = total;
                return out;
            }
            """,
        ),
        _p(
            131, "Palindrome Partitioning", "Medium",
            "Cut after every position whose prefix reads the same both ways, "
            "then solve the rest.",
            "O(n * 2 ** n) time, O(n) space",
            """
            static bool readsBothWays(const char *text, int from, int to) {
                while (from < to) {
                    if (text[from] != text[to]) {
                        return false;
                    }
                    from++;
                    to--;
                }
                return true;
            }

            static void walkCuts(const char *text, int length, int start,
                                 char **built, int depth, char ***out,
                                 int *sizes, int *total) {
                if (start == length) {
                    out[*total] = malloc(depth * sizeof(char *));
                    for (int i = 0; i < depth; i++) {
                        out[*total][i] = built[i];
                        built[i] = NULL;
                    }
                    sizes[*total] = depth;
                    (*total)++;
                    return;
                }
                for (int end = start; end < length; end++) {
                    if (!readsBothWays(text, start, end)) {
                        continue;
                    }
                    int size = end - start + 1;
                    char *piece = malloc(size + 1);
                    memcpy(piece, text + start, size);
                    piece[size] = '\\0';
                    built[depth] = piece;
                    walkCuts(text, length, end + 1, built, depth + 1, out,
                             sizes, total);
                    free(built[depth]);
                    built[depth] = NULL;
                }
            }

            char ***partition(char *text, int *returnSize, int **columnSizes) {
                int length = (int)strlen(text);
                int capacity = 1 << length;
                char ***out = malloc(capacity * sizeof(char **));
                int *sizes = malloc(capacity * sizeof(int));
                char **built = calloc(length + 1, sizeof(char *));
                int total = 0;
                walkCuts(text, length, 0, built, 0, out, sizes, &total);
                free(built);
                *returnSize = total;
                *columnSizes = sizes;
                return out;
            }
            """,
        ),
    ),
)


# ── 11. Top K (heaps) ───────────────────────────────────────

_HEAP = Pattern(
    id="lc-heap",
    name="Top K (Heaps)",
    order=11,
    blurb="A size-k heap keeps the best k items without sorting everything.",
    tell="'K largest / K closest / K most frequent'.",
    preamble=(STDLIB, STRING_H, STDBOOL, LIMITS, INT_MAP, INT_HEAP),
    problems=(
        _p(
            215, "Kth Largest Element in an Array", "Medium",
            "Hold a min-heap of size k; its root is the kth largest. The heap "
            "here is a min-heap, so this needs no inversion at all.",
            "O(n log k) time, O(k) space",
            """
            int findKthLargest(int *nums, int numsSize, int k) {
                Heap *heap = heapNew(k + 1);
                for (int i = 0; i < numsSize; i++) {
                    heapPush(heap, nums[i], nums[i], 0);
                    if (heap->size > k) {
                        heapPop(heap);
                    }
                }
                int answer = heap->items[0].a;
                heapFree(heap);
                return answer;
            }
            """,
        ),
        _p(
            347, "Top K Frequent Elements", "Medium",
            "Count first, then a min-heap keyed on the count keeps only k.",
            "O(n log k) time, O(n) space",
            """
            int *topKFrequent(int *nums, int numsSize, int k, int *returnSize) {
                IntMap *counts = mapNew();
                for (int i = 0; i < numsSize; i++) {
                    mapBump(counts, nums[i], 1);
                }
                Heap *heap = heapNew(k + 1);
                IntMap *done = mapNew();
                for (int i = 0; i < numsSize; i++) {
                    int seen = 0;
                    if (mapGet(done, nums[i], &seen)) {
                        continue;
                    }
                    mapPut(done, nums[i], 1);
                    heapPush(heap, mapCount(counts, nums[i]), nums[i], 0);
                    if (heap->size > k) {
                        heapPop(heap);
                    }
                }
                int *out = malloc(k * sizeof(int));
                int total = 0;
                while (heap->size > 0) {
                    out[total++] = heapPop(heap).a;
                }
                heapFree(heap);
                mapFree(done);
                mapFree(counts);
                *returnSize = total;
                return out;
            }
            """,
        ),
        _p(
            973, "K Closest Points to Origin", "Medium",
            "Key the heap on the NEGATED distance so the furthest sits on top "
            "of a min-heap, which is the one to evict.",
            "O(n log k) time, O(k) space",
            """
            int **kClosest(int **points, int pointsSize, int *pointsColSize,
                           int k, int *returnSize, int **columnSizes) {
                Heap *heap = heapNew(k + 1);
                for (int i = 0; i < pointsSize; i++) {
                    long long x = points[i][0];
                    long long y = points[i][1];
                    heapPush(heap, -(x * x + y * y), points[i][0],
                             points[i][1]);
                    if (heap->size > k) {
                        heapPop(heap);
                    }
                }
                int **out = malloc(k * sizeof(int *));
                int *sizes = malloc(k * sizeof(int));
                int total = 0;
                while (heap->size > 0) {
                    HeapItem item = heapPop(heap);
                    out[total] = malloc(2 * sizeof(int));
                    out[total][0] = item.a;
                    out[total][1] = item.b;
                    sizes[total] = 2;
                    total++;
                }
                heapFree(heap);
                *returnSize = total;
                *columnSizes = sizes;
                return out;
            }
            """,
        ),
        _p(
            1046, "Last Stone Weight", "Easy",
            "The two heaviest stones are wanted, and the heap is a min-heap, so "
            "the weights go in negated.",
            "O(n log n) time, O(n) space",
            """
            int lastStoneWeight(int *stones, int stonesSize) {
                Heap *heap = heapNew(stonesSize + 1);
                for (int i = 0; i < stonesSize; i++) {
                    heapPush(heap, -stones[i], stones[i], 0);
                }
                while (heap->size > 1) {
                    int first = heapPop(heap).a;
                    int second = heapPop(heap).a;
                    if (first != second) {
                        heapPush(heap, -(first - second), first - second, 0);
                    }
                }
                int answer = heap->size ? heap->items[0].a : 0;
                heapFree(heap);
                return answer;
            }
            """,
        ),
        _p(
            692, "Top K Frequent Words", "Medium",
            "Most frequent first, then alphabetical. Two orderings pulling "
            "opposite ways, so a qsort comparator says it more plainly.",
            "O(n log n) time, O(n) space",
            """
            typedef struct {
                char *word;
                int count;
            } WordCount;

            static int byCountThenWord(const void *a, const void *b) {
                const WordCount *x = a;
                const WordCount *y = b;
                if (x->count != y->count) {
                    return y->count - x->count;
                }
                return strcmp(x->word, y->word);
            }

            char **topKFrequentWords(char **words, int wordsSize, int k,
                                     int *returnSize) {
                WordCount *entries = malloc(wordsSize * sizeof(WordCount));
                int total = 0;
                for (int i = 0; i < wordsSize; i++) {
                    int at = -1;
                    for (int j = 0; j < total; j++) {
                        if (strcmp(entries[j].word, words[i]) == 0) {
                            at = j;
                            break;
                        }
                    }
                    if (at < 0) {
                        entries[total].word = words[i];
                        entries[total].count = 1;
                        total++;
                    } else {
                        entries[at].count++;
                    }
                }
                qsort(entries, total, sizeof(WordCount), byCountThenWord);
                char **out = malloc(k * sizeof(char *));
                int taken = k < total ? k : total;
                for (int i = 0; i < taken; i++) {
                    out[i] = entries[i].word;
                }
                free(entries);
                *returnSize = taken;
                return out;
            }
            """,
        ),
        _p(
            451, "Sort Characters By Frequency", "Medium",
            "Only 128 characters, so counting is an array and ordering them is "
            "a sort over at most 128 entries.",
            "O(n) time, O(1) space",
            """
            typedef struct {
                unsigned char ch;
                int count;
            } CharCount;

            static int byCountDescending(const void *a, const void *b) {
                const CharCount *x = a;
                const CharCount *y = b;
                return y->count - x->count;
            }

            char *frequencySort(char *s) {
                CharCount counts[128];
                for (int i = 0; i < 128; i++) {
                    counts[i].ch = (unsigned char)i;
                    counts[i].count = 0;
                }
                int length = (int)strlen(s);
                for (int i = 0; i < length; i++) {
                    counts[(unsigned char)s[i]].count++;
                }
                qsort(counts, 128, sizeof(CharCount), byCountDescending);
                char *out = malloc(length + 1);
                int at = 0;
                for (int i = 0; i < 128; i++) {
                    for (int n = 0; n < counts[i].count; n++) {
                        out[at++] = (char)counts[i].ch;
                    }
                }
                out[at] = '\\0';
                return out;
            }
            """,
        ),
        _p(
            378, "Kth Smallest Element in a Sorted Matrix", "Medium",
            "Seed the heap with each row's head, then keep pulling the smallest "
            "and refilling from its row.",
            "O(k log n) time, O(n) space",
            """
            int kthSmallest(int **matrix, int matrixSize, int *matrixColSize,
                            int k) {
                Heap *heap = heapNew(matrixSize + 1);
                int rows = matrixSize < k ? matrixSize : k;
                for (int row = 0; row < rows; row++) {
                    heapPush(heap, matrix[row][0], row, 0);
                }
                int value = 0;
                for (int i = 0; i < k; i++) {
                    HeapItem item = heapPop(heap);
                    value = (int)item.key;
                    int row = item.a;
                    int col = item.b;
                    if (col + 1 < matrixColSize[row]) {
                        heapPush(heap, matrix[row][col + 1], row, col + 1);
                    }
                }
                heapFree(heap);
                return value;
            }
            """,
        ),
        _p(
            767, "Reorganize String", "Medium",
            "Always place the most common letter left, holding the one you just "
            "used aside for a turn.",
            "O(n log n) time, O(n) space",
            """
            char *reorganizeString(char *s) {
                int length = (int)strlen(s);
                int counts[26] = {0};
                for (int i = 0; i < length; i++) {
                    counts[s[i] - 'a']++;
                }
                Heap *heap = heapNew(27);
                for (int i = 0; i < 26; i++) {
                    if (counts[i] > 0) {
                        heapPush(heap, -counts[i], i, 0);
                    }
                }
                char *out = malloc(length + 1);
                int at = 0;
                bool holding = false;
                HeapItem held = {0, 0, 0};
                while (heap->size > 0) {
                    HeapItem item = heapPop(heap);
                    out[at++] = (char)('a' + item.a);
                    if (holding) {
                        heapPush(heap, held.key, held.a, 0);
                        holding = false;
                    }
                    if (item.key + 1 < 0) {
                        held.key = item.key + 1;
                        held.a = item.a;
                        holding = true;
                    }
                }
                out[at] = '\\0';
                if (at != length) {
                    out[0] = '\\0';
                }
                heapFree(heap);
                return out;
            }
            """,
        ),
    ),
)


# ── 12. Topological sort ────────────────────────────────────

_TOPOLOGICAL = Pattern(
    id="lc-topological",
    name="Topological Sort",
    order=12,
    blurb="Repeatedly take whatever has no unmet prerequisites (indegree 0).",
    tell="Dependencies, ordering, 'can this schedule be completed?'",
    preamble=(STDLIB, STRING_H, STDBOOL),
    problems=(
        _p(
            207, "Course Schedule", "Medium",
            "If a cycle exists you can never drain the queue - count what you "
            "took. The graph is an adjacency matrix, which is enough here.",
            "O(v * v) time, O(v * v) space",
            """
            bool canFinish(int numCourses, int **prerequisites,
                           int prerequisitesSize, int *prerequisitesColSize) {
                bool *edges = calloc(numCourses * numCourses, sizeof(bool));
                int *indegree = calloc(numCourses, sizeof(int));
                for (int i = 0; i < prerequisitesSize; i++) {
                    int course = prerequisites[i][0];
                    int prereq = prerequisites[i][1];
                    if (!edges[prereq * numCourses + course]) {
                        edges[prereq * numCourses + course] = true;
                        indegree[course]++;
                    }
                }
                int *queue = malloc(numCourses * sizeof(int));
                int head = 0;
                int tail = 0;
                for (int i = 0; i < numCourses; i++) {
                    if (indegree[i] == 0) {
                        queue[tail++] = i;
                    }
                }
                int taken = 0;
                while (head < tail) {
                    int node = queue[head++];
                    taken++;
                    for (int next = 0; next < numCourses; next++) {
                        if (edges[node * numCourses + next] &&
                            --indegree[next] == 0) {
                            queue[tail++] = next;
                        }
                    }
                }
                free(edges);
                free(indegree);
                free(queue);
                return taken == numCourses;
            }
            """,
        ),
        _p(
            210, "Course Schedule II", "Medium",
            "Same peel, but keep the order you took things in.",
            "O(v * v) time, O(v * v) space",
            """
            int *findOrder(int numCourses, int **prerequisites,
                           int prerequisitesSize, int *prerequisitesColSize,
                           int *returnSize) {
                bool *edges = calloc(numCourses * numCourses, sizeof(bool));
                int *indegree = calloc(numCourses, sizeof(int));
                for (int i = 0; i < prerequisitesSize; i++) {
                    int course = prerequisites[i][0];
                    int prereq = prerequisites[i][1];
                    if (!edges[prereq * numCourses + course]) {
                        edges[prereq * numCourses + course] = true;
                        indegree[course]++;
                    }
                }
                int *order = malloc(numCourses * sizeof(int));
                int head = 0;
                int tail = 0;
                for (int i = 0; i < numCourses; i++) {
                    if (indegree[i] == 0) {
                        order[tail++] = i;
                    }
                }
                while (head < tail) {
                    int node = order[head++];
                    for (int next = 0; next < numCourses; next++) {
                        if (edges[node * numCourses + next] &&
                            --indegree[next] == 0) {
                            order[tail++] = next;
                        }
                    }
                }
                free(edges);
                free(indegree);
                *returnSize = tail == numCourses ? numCourses : 0;
                return order;
            }
            """,
        ),
        _p(
            310, "Minimum Height Trees", "Medium",
            "Peel leaves layer by layer; the last 1 or 2 left are the centres.",
            "O(v + e) time, O(v + e) space",
            """
            int *findMinHeightTrees(int n, int **edges, int edgesSize,
                                    int *edgesColSize, int *returnSize) {
                if (n == 1) {
                    int *only = malloc(sizeof(int));
                    only[0] = 0;
                    *returnSize = 1;
                    return only;
                }
                int *degree = calloc(n, sizeof(int));
                bool *linked = calloc(n * n, sizeof(bool));
                for (int i = 0; i < edgesSize; i++) {
                    int a = edges[i][0];
                    int b = edges[i][1];
                    linked[a * n + b] = true;
                    linked[b * n + a] = true;
                    degree[a]++;
                    degree[b]++;
                }
                int *leaves = malloc(n * sizeof(int));
                int total = 0;
                for (int i = 0; i < n; i++) {
                    if (degree[i] == 1) {
                        leaves[total++] = i;
                    }
                }
                int remaining = n;
                while (remaining > 2) {
                    remaining -= total;
                    int *next = malloc(n * sizeof(int));
                    int nextTotal = 0;
                    for (int i = 0; i < total; i++) {
                        int leaf = leaves[i];
                        degree[leaf] = 0;
                        for (int other = 0; other < n; other++) {
                            if (linked[leaf * n + other]) {
                                linked[leaf * n + other] = false;
                                linked[other * n + leaf] = false;
                                if (--degree[other] == 1) {
                                    next[nextTotal++] = other;
                                }
                            }
                        }
                    }
                    free(leaves);
                    leaves = next;
                    total = nextTotal;
                }
                free(degree);
                free(linked);
                *returnSize = total;
                return leaves;
            }
            """,
        ),
        _p(
            802, "Find Eventual Safe States", "Medium",
            "Reverse every edge, then peel from the terminal nodes - whatever "
            "drains is safe.",
            "O(v * v) time, O(v * v) space",
            """
            int *eventualSafeNodes(int **graph, int graphSize,
                                   int *graphColSize, int *returnSize) {
                int n = graphSize;
                bool *reversed = calloc(n * n, sizeof(bool));
                int *outdegree = calloc(n, sizeof(int));
                for (int node = 0; node < n; node++) {
                    outdegree[node] = graphColSize[node];
                    for (int i = 0; i < graphColSize[node]; i++) {
                        reversed[graph[node][i] * n + node] = true;
                    }
                }
                int *safe = malloc(n * sizeof(int));
                int head = 0;
                int tail = 0;
                for (int i = 0; i < n; i++) {
                    if (outdegree[i] == 0) {
                        safe[tail++] = i;
                    }
                }
                while (head < tail) {
                    int node = safe[head++];
                    for (int prev = 0; prev < n; prev++) {
                        if (reversed[node * n + prev] &&
                            --outdegree[prev] == 0) {
                            safe[tail++] = prev;
                        }
                    }
                }
                for (int i = 1; i < tail; i++) {
                    int value = safe[i];
                    int j = i - 1;
                    while (j >= 0 && safe[j] > value) {
                        safe[j + 1] = safe[j];
                        j--;
                    }
                    safe[j + 1] = value;
                }
                free(reversed);
                free(outdegree);
                *returnSize = tail;
                return safe;
            }
            """,
        ),
        _p(
            1462, "Course Schedule IV", "Medium",
            "Peel in order, and let each course inherit the prerequisite set of "
            "everything before it. A bit matrix holds the sets.",
            "O(v * e) time, O(v * v) space",
            """
            bool *checkIfPrerequisite(int numCourses, int **prerequisites,
                                      int prerequisitesSize,
                                      int *prerequisitesColSize, int **queries,
                                      int queriesSize, int *queriesColSize,
                                      int *returnSize) {
                bool *edges = calloc(numCourses * numCourses, sizeof(bool));
                bool *needs = calloc(numCourses * numCourses, sizeof(bool));
                int *indegree = calloc(numCourses, sizeof(int));
                for (int i = 0; i < prerequisitesSize; i++) {
                    int prereq = prerequisites[i][0];
                    int course = prerequisites[i][1];
                    if (!edges[prereq * numCourses + course]) {
                        edges[prereq * numCourses + course] = true;
                        indegree[course]++;
                    }
                }
                int *queue = malloc(numCourses * sizeof(int));
                int head = 0;
                int tail = 0;
                for (int i = 0; i < numCourses; i++) {
                    if (indegree[i] == 0) {
                        queue[tail++] = i;
                    }
                }
                while (head < tail) {
                    int node = queue[head++];
                    for (int next = 0; next < numCourses; next++) {
                        if (!edges[node * numCourses + next]) {
                            continue;
                        }
                        needs[next * numCourses + node] = true;
                        for (int earlier = 0; earlier < numCourses; earlier++) {
                            if (needs[node * numCourses + earlier]) {
                                needs[next * numCourses + earlier] = true;
                            }
                        }
                        if (--indegree[next] == 0) {
                            queue[tail++] = next;
                        }
                    }
                }
                bool *answers = malloc(queriesSize * sizeof(bool));
                for (int i = 0; i < queriesSize; i++) {
                    answers[i] =
                        needs[queries[i][1] * numCourses + queries[i][0]];
                }
                free(edges);
                free(needs);
                free(indegree);
                free(queue);
                *returnSize = queriesSize;
                return answers;
            }
            """,
        ),
        _p(
            2115, "Find All Possible Recipes from Given Supplies", "Medium",
            "Ingredients are prerequisites: a recipe unlocks once its count of "
            "missing items hits zero, and then becomes an ingredient itself.",
            "O(v * e) time, O(v + e) space",
            """
            char **findAllRecipes(char **recipes, int recipesSize,
                                  char ***ingredients, int ingredientsSize,
                                  int *ingredientsColSize, char **supplies,
                                  int suppliesSize, int *returnSize) {
                int *missing = malloc(recipesSize * sizeof(int));
                for (int i = 0; i < recipesSize; i++) {
                    missing[i] = ingredientsColSize[i];
                }
                char **available =
                    malloc((suppliesSize + recipesSize) * sizeof(char *));
                int head = 0;
                int tail = 0;
                for (int i = 0; i < suppliesSize; i++) {
                    available[tail++] = supplies[i];
                }
                char **made = malloc(recipesSize * sizeof(char *));
                int total = 0;
                while (head < tail) {
                    char *item = available[head++];
                    for (int r = 0; r < recipesSize; r++) {
                        if (missing[r] == 0) {
                            continue;
                        }
                        for (int i = 0; i < ingredientsColSize[r]; i++) {
                            if (strcmp(ingredients[r][i], item) == 0) {
                                if (--missing[r] == 0) {
                                    made[total++] = recipes[r];
                                    available[tail++] = recipes[r];
                                }
                                break;
                            }
                        }
                    }
                }
                free(missing);
                free(available);
                *returnSize = total;
                return made;
            }
            """,
        ),
        _p(
            1136, "Parallel Courses", "Medium",
            "Every drained layer of the queue is one semester - count the "
            "layers, not the courses.",
            "O(v * v) time, O(v * v) space",
            """
            int minimumSemesters(int n, int **relations, int relationsSize,
                                 int *relationsColSize) {
                bool *edges = calloc((n + 1) * (n + 1), sizeof(bool));
                int *indegree = calloc(n + 1, sizeof(int));
                for (int i = 0; i < relationsSize; i++) {
                    int prereq = relations[i][0];
                    int course = relations[i][1];
                    if (!edges[prereq * (n + 1) + course]) {
                        edges[prereq * (n + 1) + course] = true;
                        indegree[course]++;
                    }
                }
                int *queue = malloc((n + 1) * sizeof(int));
                int head = 0;
                int tail = 0;
                for (int i = 1; i <= n; i++) {
                    if (indegree[i] == 0) {
                        queue[tail++] = i;
                    }
                }
                int studied = 0;
                int semesters = 0;
                while (head < tail) {
                    semesters++;
                    int size = tail - head;
                    for (int i = 0; i < size; i++) {
                        int node = queue[head++];
                        studied++;
                        for (int next = 1; next <= n; next++) {
                            if (edges[node * (n + 1) + next] &&
                                --indegree[next] == 0) {
                                queue[tail++] = next;
                            }
                        }
                    }
                }
                free(edges);
                free(indegree);
                free(queue);
                return studied == n ? semesters : -1;
            }
            """,
        ),
        _p(
            269, "Alien Dictionary", "Hard",
            "Adjacent words give one letter order each; the first difference is "
            "the only edge they prove. 26 letters, so the graph is a matrix.",
            "O(c) time, O(1) space",
            """
            char *alienOrder(char **words, int wordsSize) {
                bool present[26] = {false};
                bool edges[26][26] = {{false}};
                int indegree[26] = {0};
                for (int i = 0; i < wordsSize; i++) {
                    for (int j = 0; words[i][j]; j++) {
                        present[words[i][j] - 'a'] = true;
                    }
                }
                for (int i = 0; i + 1 < wordsSize; i++) {
                    char *first = words[i];
                    char *second = words[i + 1];
                    int j = 0;
                    while (first[j] && second[j] && first[j] == second[j]) {
                        j++;
                    }
                    if (first[j] && second[j]) {
                        int a = first[j] - 'a';
                        int b = second[j] - 'a';
                        if (!edges[a][b]) {
                            edges[a][b] = true;
                            indegree[b]++;
                        }
                    } else if (first[j] && !second[j]) {
                        char *empty = malloc(1);
                        empty[0] = '\\0';
                        return empty;
                    }
                }
                int letters = 0;
                for (int i = 0; i < 26; i++) {
                    if (present[i]) {
                        letters++;
                    }
                }
                char *order = malloc(letters + 1);
                int head = 0;
                int tail = 0;
                for (int i = 0; i < 26; i++) {
                    if (present[i] && indegree[i] == 0) {
                        order[tail++] = (char)('a' + i);
                    }
                }
                while (head < tail) {
                    int node = order[head++] - 'a';
                    for (int next = 0; next < 26; next++) {
                        if (edges[node][next] && --indegree[next] == 0) {
                            order[tail++] = (char)('a' + next);
                        }
                    }
                }
                if (tail != letters) {
                    tail = 0;
                }
                order[tail] = '\\0';
                return order;
            }
            """,
        ),
    ),
)


# ── 13. Dynamic programming ─────────────────────────────────

_DP = Pattern(
    id="lc-dp",
    name="Dynamic Programming",
    order=13,
    blurb="Solve small cases once, store them, and build the big answer from them.",
    tell="Overlapping subproblems - the naive recursion recomputes the same thing.",
    preamble=(STDLIB, STRING_H, STDBOOL, CTYPE),
    problems=(
        _p(
            70, "Climbing Stairs", "Easy",
            "Ways to reach step n = ways to n-1 plus ways to n-2. It's Fibonacci.",
            "O(n) time, O(1) space",
            """
            int climbStairs(int n) {
                int prev = 1;
                int cur = 1;
                for (int i = 0; i < n - 1; i++) {
                    int next = prev + cur;
                    prev = cur;
                    cur = next;
                }
                return cur;
            }
            """,
        ),
        _p(
            198, "House Robber", "Medium",
            "At each house: best so far if you skip it, or (best before last) "
            "plus it. Bank the old skip before overwriting it.",
            "O(n) time, O(1) space",
            """
            int rob(int *nums, int numsSize) {
                int skip = 0;
                int take = 0;
                for (int i = 0; i < numsSize; i++) {
                    int nextSkip = skip > take ? skip : take;
                    take = skip + nums[i];
                    skip = nextSkip;
                }
                return skip > take ? skip : take;
            }
            """,
        ),
        _p(
            322, "Coin Change", "Medium",
            "Build up every amount from 1 to target, trying each coin as the "
            "last one.",
            "O(amount * coins) time, O(amount) space",
            """
            int coinChange(int *coins, int coinsSize, int amount) {
                int *best = malloc((amount + 1) * sizeof(int));
                for (int i = 0; i <= amount; i++) {
                    best[i] = amount + 1;
                }
                best[0] = 0;
                for (int value = 1; value <= amount; value++) {
                    for (int i = 0; i < coinsSize; i++) {
                        if (coins[i] <= value &&
                            best[value - coins[i]] + 1 < best[value]) {
                            best[value] = best[value - coins[i]] + 1;
                        }
                    }
                }
                int answer = best[amount] <= amount ? best[amount] : -1;
                free(best);
                return answer;
            }
            """,
        ),
        _p(
            300, "Longest Increasing Subsequence", "Medium",
            "Keep the smallest possible tail for each length; binary search its "
            "slot.",
            "O(n log n) time, O(n) space",
            """
            int lengthOfLIS(int *nums, int numsSize) {
                int *tails = malloc(numsSize * sizeof(int));
                int total = 0;
                for (int i = 0; i < numsSize; i++) {
                    int low = 0;
                    int high = total;
                    while (low < high) {
                        int mid = low + (high - low) / 2;
                        if (tails[mid] < nums[i]) {
                            low = mid + 1;
                        } else {
                            high = mid;
                        }
                    }
                    tails[low] = nums[i];
                    if (low == total) {
                        total++;
                    }
                }
                free(tails);
                return total;
            }
            """,
        ),
        _p(
            746, "Min Cost Climbing Stairs", "Easy",
            "The cost of a step is its own plus the cheaper of the two ways off it.",
            "O(n) time, O(1) space",
            """
            int minCostClimbingStairs(int *cost, int costSize) {
                int one = 0;
                int two = 0;
                for (int i = 2; i <= costSize; i++) {
                    int fromOne = one + cost[i - 1];
                    int fromTwo = two + cost[i - 2];
                    int next = fromOne < fromTwo ? fromOne : fromTwo;
                    two = one;
                    one = next;
                }
                return one;
            }
            """,
        ),
        _p(
            1143, "Longest Common Subsequence", "Medium",
            "Matching letters extend the diagonal; otherwise take the better of "
            "dropping one.",
            "O(m * n) time, O(m * n) space",
            """
            int longestCommonSubsequence(char *first, char *second) {
                int rows = (int)strlen(first);
                int cols = (int)strlen(second);
                int *grid = calloc((rows + 1) * (cols + 1), sizeof(int));
                for (int i = rows - 1; i >= 0; i--) {
                    for (int j = cols - 1; j >= 0; j--) {
                        int here = i * (cols + 1) + j;
                        if (first[i] == second[j]) {
                            grid[here] = 1 + grid[(i + 1) * (cols + 1) + j + 1];
                        } else {
                            int down = grid[(i + 1) * (cols + 1) + j];
                            int across = grid[i * (cols + 1) + j + 1];
                            grid[here] = down > across ? down : across;
                        }
                    }
                }
                int answer = grid[0];
                free(grid);
                return answer;
            }
            """,
        ),
        _p(
            139, "Word Break", "Medium",
            "A position is reachable when some word ends there and its start was "
            "reachable too.",
            "O(n * n * w) time, O(n) space",
            """
            bool wordBreak(char *text, char **words, int wordsSize) {
                int length = (int)strlen(text);
                bool *reachable = calloc(length + 1, sizeof(bool));
                reachable[0] = true;
                for (int end = 1; end <= length; end++) {
                    for (int w = 0; w < wordsSize; w++) {
                        int size = (int)strlen(words[w]);
                        int start = end - size;
                        if (start < 0 || !reachable[start]) {
                            continue;
                        }
                        if (memcmp(text + start, words[w], size) == 0) {
                            reachable[end] = true;
                            break;
                        }
                    }
                }
                bool answer = reachable[length];
                free(reachable);
                return answer;
            }
            """,
        ),
        _p(
            152, "Maximum Product Subarray", "Medium",
            "Track the smallest product too - a negative turns the worst into "
            "the best.",
            "O(n) time, O(1) space",
            """
            int maxProduct(int *nums, int numsSize) {
                int best = nums[0];
                int high = nums[0];
                int low = nums[0];
                for (int i = 1; i < numsSize; i++) {
                    int n = nums[i];
                    int byHigh = high * n;
                    int byLow = low * n;
                    int nextHigh = n;
                    int nextLow = n;
                    if (byHigh > nextHigh) {
                        nextHigh = byHigh;
                    }
                    if (byLow > nextHigh) {
                        nextHigh = byLow;
                    }
                    if (byHigh < nextLow) {
                        nextLow = byHigh;
                    }
                    if (byLow < nextLow) {
                        nextLow = byLow;
                    }
                    high = nextHigh;
                    low = nextLow;
                    if (high > best) {
                        best = high;
                    }
                }
                return best;
            }
            """,
        ),
    ),
)
