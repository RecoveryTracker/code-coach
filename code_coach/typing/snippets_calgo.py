"""C for algorithms: the shapes interview problems are built from.

The same moves as the Python, JavaScript and Dart sets, written the way C
writes them: arrays with a separate length, a stack as an array and a top
index, a queue as an array with a head and a tail, `counts[26]` for letters,
`lo + (hi - lo) / 2` for the midpoint, `memset` to clear a table, `qsort`
with a comparator that returns `(x > y) - (x < y)`, strings walked until
`'\\0'`, and unsigned integers for the bit tricks.

Every snippet is written in raw strings, so `\\n` and `'\\0'` are the
characters a person types. The blocks are whole portable programs with a
`main`: no undefined behaviour, nothing the compiler is free to decide, and
the tests build every one warning-free under `-std=c11 -Wall -Wextra
-pedantic`, run it, and hold what it prints to an answer worked out by hand.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

CALGO_LINES: tuple[Passage, ...] = (
    # two pointers and windows
    _s(r"""int lo = 0, hi = n - 1;""", "two pointers, one at each end"),
    _s(r"""while (lo < hi && nums[lo] + nums[hi] != want) {""", "closing in on a pair"),
    _s(r"""int tmp = nums[lo]; nums[lo] = nums[hi]; nums[hi] = tmp;""", "a swap, written out"),
    _s(r"""void swap_ints(int *a, int *b) { int t = *a; *a = *b; *b = t; }""",
       "a swap through two pointers"),
    _s(r"""sum += nums[i] - nums[i - k];""", "slide: add the new end, drop the old"),
    _s(r"""if (end - start + 1 > best) best = end - start + 1;""", "the widest window so far"),
    _s(r"""if (last[idx] >= start) start = last[idx] + 1;""", "a repeat inside the window"),
    # binary search
    _s(r"""int mid = lo + (hi - lo) / 2;""", "the midpoint that cannot overflow"),
    _s(r"""if (arr[mid] == key) return mid;""", "found it"),
    _s(r"""if (arr[mid] < key) lo = mid + 1; else hi = mid - 1;""", "go right or left"),
    # counting
    _s(r"""int counts[26] = { 0 };""", "one counter per letter, all starting at zero"),
    _s(r"""counts[word[i] - 'a']++;""", "a is slot 0, b is slot 1 and so on"),
    _s(r"""for (int k = 0; k < 26; k++) if (counts[k] > 0) distinct++;""", "how many letters appear"),
    _s(r"""if (counts[s[i] - 'a']-- == 0) return 0;""", "a letter used more than it was given"),
    _s(r"""int freq[256] = { 0 };""", "a counter for every byte value"),
    _s(r"""freq[(unsigned char)text[i]]++;""", "cast first so a negative char is no index"),
    _s(r"""memset(counts, 0, sizeof counts);""", "wipe the counters between words"),
    # stacks and queues
    _s(r"""int stack[64], top = 0;""", "an array and a top index make a stack"),
    _s(r"""stack[top++] = value;""", "push: store, then move the top up"),
    _s(r"""int popped = stack[--top];""", "pop: move the top down, then read"),
    _s(r"""while (top > 0 && temps[stack[top - 1]] < temps[i]) {""", "a monotonic stack"),
    _s(r"""if (top == 0 || stack[--top] != want) return 0;""", "the wrong closer, or none open"),
    _s(r"""int queue[100], head = 0, tail = 0;""", "a queue is an array with two indexes"),
    _s(r"""queue[tail++] = start;""", "enqueue at the tail"),
    _s(r"""int current = queue[head++];""", "dequeue from the head"),
    _s(r"""while (head < tail && dist[goal] < 0) {""", "until the queue runs dry"),
    _s(r"""if (!seen[next]) { seen[next] = 1; queue[tail++] = next; }""", "mark it when it goes in"),
    # grids
    _s(r"""const int dr[4] = { 1, -1, 0, 0 }, dc[4] = { 0, 0, 1, -1 };""", "the four neighbours"),
    _s(r"""int nr = r + dr[d], nc = c + dc[d];""", "the neighbour in direction d"),
    _s(r"""if (nr < 0 || nc < 0 || nr >= rows || nc >= cols) continue;""", "off the edge of the grid"),
    _s(r"""if (grid[nr][nc] == '#' || seen[nr][nc]) continue;""", "a wall, or already visited"),
    _s(r"""dist[nr][nc] = dist[r][c] + 1;""", "one step further than where it came from"),
    # memo and dynamic programming
    _s(r"""long long memo[50] = { 0 };""", "a cache for a recursive function"),
    _s(r"""if (memo[n] != 0) return memo[n];""", "already worked out"),
    _s(r"""return memo[n] = fib(n - 1) + fib(n - 2);""", "work it out once, keep it, return it"),
    _s(r"""int dp[100] = { 0 };""", "one slot per subproblem"),
    _s(r"""dp[i] = dp[i - 1] > dp[i - 2] + h[i] ? dp[i - 1] : dp[i - 2] + h[i];""", "skip it or take it"),
    _s(r"""int table[50][50] = { { 0 } };""", "a 2-D table, every cell zero"),
    _s(r"""table[i][j] = table[i - 1][j] + table[i][j - 1];""", "paths in from above and from the left"),
    _s(r"""ways[t] += ways[t - coins[c]];""", "the ways of making change"),
    _s(r"""ways[0] = 1;""", "one way to make nothing"),
    # prefix sums
    _s(r"""int prefix[101] = { 0 };""", "the empty prefix comes first"),
    _s(r"""prefix[i + 1] = prefix[i] + nums[i];""", "running totals"),
    _s(r"""int range_sum = prefix[j + 1] - prefix[i];""", "any slice's sum in one step"),
    # sorting
    _s(r"""static int cmp_int(const void *a, const void *b) {""", "the shape qsort wants"),
    _s(r"""int x = *(const int *)a, y = *(const int *)b;""", "turn the void pointers back into ints"),
    _s(r"""int order = (x > y) - (x < y);""", "-1, 0 or 1, and no subtraction to overflow"),
    _s(r"""qsort(nums, n, sizeof nums[0], cmp_int);""", "sort the array in place"),
    _s(r"""return strcmp(*(const char **)a, *(const char **)b);""", "compare two strings in an array"),
    # strings
    _s(r"""for (size_t i = 0; text[i] != '\0'; i++) {""", "walk until the terminator"),
    _s(r"""size_t len = strlen(text);""", "the length, without the terminator"),
    _s(r"""if (strcmp(a, b) == 0) puts("same");""", "strcmp is zero when equal"),
    _s(r"""memset(buf, 0, sizeof buf);""", "zero a whole array"),
    _s(r"""while (*p != '\0') p++;""", "walk a pointer to the end"),
    _s(r"""char *end = text + strlen(text) - 1;""", "the last real character"),
    _s(r"""char out = 'a' + (text[i] - 'a' + shift) % 26;""", "a Caesar shift"),
    _s(r"""if (text[i] >= 'a' && text[i] <= 'z') lower++;""", "a lowercase letter"),
    _s(r"""snprintf(copy, sizeof copy, "%s", text);""", "a copy that cannot overrun"),
    # bits
    _s(r"""if (n & 1u) odd_count++;""", "the lowest bit says odd"),
    _s(r"""word &= word - 1u;""", "clears the lowest set bit"),
    _s(r"""int power_of_two = n > 0 && (n & (n - 1)) == 0;""", "exactly one bit set"),
    _s(r"""unsigned int mask = 1u << bit;""", "unsigned, so the shift is safe"),
    _s(r"""single ^= nums[i];""", "pairs cancel out"),
    _s(r"""while (n != 0u) { n &= n - 1u; count++; }""", "count the set bits"),
    _s(r"""int is_set = (flags >> k) & 1u;""", "read bit k of an unsigned value"),
    # memory and linked lists
    _s(r"""int *buf = malloc(n * sizeof *buf);""", "sizeof the thing pointed at, not its type"),
    _s(r"""if (buf == NULL) return 1;""", "malloc can fail"),
    _s(r"""free(buf);""", "give it back"),
    _s(r"""struct node { int value; struct node *next; };""", "a linked list node"),
    _s(r"""struct node *head = NULL;""", "an empty list is a null head"),
    _s(r"""node->next = head; head = node;""", "push on the front"),
    _s(r"""struct node *next = cur->next; cur->next = prev; prev = cur; cur = next;""",
       "one step of reversing a list"),
    _s(r"""for (struct node *p = head; p != NULL; p = p->next) total += p->value;""", "walk the list"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"C · {note}")


CALGO_BLOCKS: tuple[Passage, ...] = (
    _b(r"""#include <stdio.h>

int main(void) {
    int nums[] = { 1, 3, 4, 6, 9, 11 };
    int lo = 0, hi = 5, target = 10;
    while (lo < hi && nums[lo] + nums[hi] != target) {
        if (nums[lo] + nums[hi] < target) lo++; else hi--;
    }
    printf("%d %d\n", lo, hi);
    return 0;
}""",
       "two pointers on a sorted array"),
    _b(r"""#include <stdio.h>

int search(const int *a, int n, int key) {
    int lo = 0, hi = n - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < key) lo = mid + 1; else hi = mid;
    }
    return a[lo] == key ? lo : -1;
}

int main(void) {
    int a[] = { 1, 3, 5, 7, 9 };
    printf("%d %d\n", search(a, 5, 7), search(a, 5, 4));
    return 0;
}""",
       "binary search"),
    _b(r"""#include <stdio.h>

int main(void) {
    const char *text = "([])";
    char stack[16];
    int top = 0, ok = 1;
    for (int i = 0; text[i] != '\0' && ok; i++) {
        char c = text[i];
        if (c == '(' || c == '[') stack[top++] = c;
        else if (top == 0 || stack[--top] != (c == ')' ? '(' : '[')) ok = 0;
    }
    printf("%d\n", ok && top == 0);
    return 0;
}""",
       "matching brackets with a stack"),
    _b(r"""#include <stdio.h>

int main(void) {
    int dist[21] = { 0 }, queue[21] = { 1 }, head = 0, tail = 1;
    while (head < tail && dist[10] == 0) {
        int n = queue[head++], nxt[2] = { n + 1, n * 2 };
        for (int k = 0; k < 2; k++) {
            if (nxt[k] > 20 || dist[nxt[k]] != 0 || nxt[k] == 1) continue;
            dist[nxt[k]] = dist[n] + 1;
            queue[tail++] = nxt[k];
        }
    }
    printf("%d %d\n", dist[10], tail);
    return 0;
}""",
       "breadth-first search with a head and a tail"),
    _b(r"""#include <stdio.h>

static long long memo[40];

long long climb(int n) {
    if (n <= 1) return 1;
    if (memo[n] == 0) memo[n] = climb(n - 1) + climb(n - 2);
    return memo[n];
}

int main(void) {
    printf("%lld %lld %lld\n", climb(1), climb(7), climb(30));
    return 0;
}""",
       "climbing stairs with a memo array"),
    _b(r"""#include <stdio.h>

int main(void) {
    int houses[] = { 2, 7, 9, 3, 1 }, take = 0, skip = 0;
    for (int i = 0; i < 5; i++) {
        int t = skip + houses[i];
        skip = take > skip ? take : skip;
        take = t;
    }
    printf("%d\n", take > skip ? take : skip);
    return 0;
}""",
       "house robber in two variables"),
    _b(r"""#include <stdio.h>
#include <stdlib.h>

static int by_value(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);
}

int main(void) {
    int nums[] = { 42, -7, 19, 0, -7, 3 };
    qsort(nums, 6, sizeof nums[0], by_value);
    for (int i = 0; i < 6; i++) printf("%d%c", nums[i], i < 5 ? ' ' : '\n');
    return 0;
}""",
       "qsort with a comparator"),
    _b(r"""#include <stdio.h>

int main(void) {
    int nums[] = { 3, 1, 4, 1, 5, 9 };
    int prefix[7] = { 0 };
    for (int i = 0; i < 6; i++) prefix[i + 1] = prefix[i] + nums[i];
    printf("%d %d\n", prefix[6], prefix[5] - prefix[2]);
    return 0;
}""",
       "prefix sums"),
    _b(r"""#include <stdio.h>
#include <string.h>

int main(void) {
    const char *a = "listen", *b = "silent";
    int counts[26] = { 0 }, same = 1;
    for (size_t i = 0; a[i] != '\0'; i++) counts[a[i] - 'a']++;
    for (size_t i = 0; b[i] != '\0'; i++) counts[b[i] - 'a']--;
    for (int k = 0; k < 26; k++) if (counts[k] != 0) same = 0;
    printf("%d %zu\n", same, strlen(a));
    return 0;
}""",
       "anagram check with letter counts"),
    _b(r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char word[] = "stressed", copy[16];
    memset(copy, 0, sizeof copy);
    memcpy(copy, word, strlen(word));
    for (int lo = 0, hi = (int)strlen(copy) - 1; lo < hi; lo++, hi--) {
        char t = copy[lo]; copy[lo] = copy[hi]; copy[hi] = t;
    }
    printf("%s %d\n", copy, strcmp(copy, word) == 0);
    return 0;
}""",
       "reversing a string in place"),
    _b(r"""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *buf = malloc(5 * sizeof *buf);
    if (buf == NULL) return 1;
    for (int i = 0; i < 5; i++) buf[i] = i * i;
    int total = 0;
    for (int i = 0; i < 5; i++) total += buf[i];
    printf("%d\n", total);
    free(buf);
    return 0;
}""",
       "a malloc'd buffer, used and freed"),
    _b(r"""#include <stdio.h>

struct node { int value; struct node *next; };

int main(void) {
    struct node c = { 3, NULL }, b = { 2, &c }, a = { 1, &b };
    struct node *prev = NULL, *cur = &a;
    while (cur != NULL) {
        struct node *next = cur->next;
        cur->next = prev;
        prev = cur;
        cur = next;
    }
    printf("%d %d %d\n", prev->value, prev->next->value, prev->next->next->value);
    return 0;
}""",
       "reversing a linked list"),
    _b(r"""#include <stdio.h>

int main(void) {
    unsigned int n = 0xB5u, p = 64u;
    int bits = 0, single = 0, vals[5] = { 4, 1, 2, 1, 2 };
    while (n != 0u) { n &= n - 1u; bits++; }
    for (int i = 0; i < 5; i++) single ^= vals[i];
    printf("%d %d %d\n", bits, p != 0u && (p & (p - 1u)) == 0u, single);
    return 0;
}""",
       "bit tricks with unsigned values"),
    _b(r"""#include <stdio.h>

int main(void) {
    int nums[] = { 2, 1, 5, 1, 3, 2 }, k = 3, sum = 0, best = 0;
    for (int i = 0; i < 6; i++) {
        sum += nums[i];
        if (i >= k) sum -= nums[i - k];
        if (i >= k - 1 && sum > best) best = sum;
    }
    printf("%d\n", best);
    return 0;
}""",
       "a sliding window of size k"),
    _b(r"""#include <stdio.h>

int main(void) {
    int coins[3] = { 1, 2, 5 };
    int ways[6] = { 1, 0, 0, 0, 0, 0 };
    for (int c = 0; c < 3; c++) {
        for (int total = coins[c]; total <= 5; total++) {
            ways[total] += ways[total - coins[c]];
        }
    }
    printf("%d\n", ways[5]);
    return 0;
}""",
       "counting the ways to make change"),
)

#: What each block prints, by its note - worked out by hand before the
#: compiler was asked, and held to the real run by tests/test_typing_calgo.py.
CALGO_PRINTS: dict[str, str] = {
    "two pointers on a sorted array": "0 4",
    "binary search": "3 -1",
    "matching brackets with a stack": "1",
    "breadth-first search with a head and a tail": "4 10",
    "climbing stairs with a memo array": "1 21 1346269",
    "house robber in two variables": "12",
    "qsort with a comparator": "-7 -7 0 3 19 42",
    "prefix sums": "23 10",
    "anagram check with letter counts": "1 6",
    "reversing a string in place": "desserts 0",
    "a malloc'd buffer, used and freed": "30",
    "reversing a linked list": "3 2 1",
    "bit tricks with unsigned values": "5 1 4",
    "a sliding window of size k": "9",
    "counting the ways to make change": "4",
}
