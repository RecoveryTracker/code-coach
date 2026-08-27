"""Pieces shared by the C pattern files.

C is the language where the standard library stops helping. There is no map,
no set, no growable list — so a bank of solutions either hand-rolls those in
every problem, or shares them. This shares them, because eight copies of the
same hash table teaches nothing except that C is tiring.

The signatures are LeetCode's own, out-parameters and all: an array comes in
as a pointer plus its length, and an array goes out as something you malloc
with the length written through `returnSize`. That is the part of C LeetCode
that actually has to be practised, so it is not smoothed over.
"""

from __future__ import annotations

from code_coach.leetcode.problems import Problem, _src


def _p(
    number: int,
    title: str,
    difficulty: str,
    idea: str,
    complexity: str,
    code: str,
) -> Problem:
    return Problem(number, title, difficulty, idea, complexity, _src(code))


STDIO = "#include <stdio.h>"
STDLIB = "#include <stdlib.h>"
STRING_H = "#include <string.h>"
STDBOOL = "#include <stdbool.h>"
CTYPE = "#include <ctype.h>"
LIMITS = "#include <limits.h>"

# A chained hash map from int to int. Deliberately small and readable rather
# than clever: the point is that the solutions above it read like the
# algorithm, not like a memory-management exercise.
INT_MAP = _src(
    """
    #define MAP_BUCKETS 4096

    typedef struct MapNode {
        int key;
        int value;
        struct MapNode *next;
    } MapNode;

    typedef struct {
        MapNode *buckets[MAP_BUCKETS];
    } IntMap;

    static unsigned int mapHash(int key) {
        return ((unsigned int)key * 2654435761u) % MAP_BUCKETS;
    }

    static IntMap *mapNew(void) {
        return calloc(1, sizeof(IntMap));
    }

    static MapNode *mapFind(IntMap *map, int key) {
        for (MapNode *node = map->buckets[mapHash(key)]; node; node = node->next) {
            if (node->key == key) {
                return node;
            }
        }
        return NULL;
    }

    static bool mapGet(IntMap *map, int key, int *out) {
        MapNode *node = mapFind(map, key);
        if (!node) {
            return false;
        }
        *out = node->value;
        return true;
    }

    static void mapPut(IntMap *map, int key, int value) {
        MapNode *node = mapFind(map, key);
        if (node) {
            node->value = value;
            return;
        }
        unsigned int slot = mapHash(key);
        node = malloc(sizeof(MapNode));
        node->key = key;
        node->value = value;
        node->next = map->buckets[slot];
        map->buckets[slot] = node;
    }

    static void mapBump(IntMap *map, int key, int by) {
        int current = 0;
        mapGet(map, key, &current);
        mapPut(map, key, current + by);
    }

    static int mapCount(IntMap *map, int key) {
        int found = 0;
        mapGet(map, key, &found);
        return found;
    }

    static void mapFree(IntMap *map) {
        for (int i = 0; i < MAP_BUCKETS; i++) {
            MapNode *node = map->buckets[i];
            while (node) {
                MapNode *next = node->next;
                free(node);
                node = next;
            }
        }
        free(map);
    }
    """
)

# strdup is POSIX, not standard C17 — MSVC warns and wants _strdup. Doing it
# by hand is portable, and it shows a learner what strdup was doing anyway.
COPY_STRING = _src(
    """
    static char *copyString(const char *text) {
        size_t length = strlen(text);
        char *out = malloc(length + 1);
        memcpy(out, text, length + 1);
        return out;
    }
    """
)

LIST_NODE = _src(
    """
    struct ListNode {
        int val;
        struct ListNode *next;
    };
    """
)

TREE_NODE = _src(
    """
    struct TreeNode {
        int val;
        struct TreeNode *left;
        struct TreeNode *right;
    };
    """
)


# A binary min-heap over (key, a, b). C has no priority queue, and several
# Top-K solutions need one to hit the complexity the pattern claims — qsort
# would work but turns an O(n log k) answer into O(n log n).
#
# Min-heap only, because a max-heap is the same thing with a negated key, and
# one structure is easier to hold in your head than two.
INT_HEAP = _src(
    """
    typedef struct {
        long long key;
        int a;
        int b;
    } HeapItem;

    typedef struct {
        HeapItem *items;
        int size;
        int capacity;
    } Heap;

    static Heap *heapNew(int capacity) {
        Heap *heap = malloc(sizeof(Heap));
        heap->items = malloc(capacity * sizeof(HeapItem));
        heap->size = 0;
        heap->capacity = capacity;
        return heap;
    }

    static void heapPush(Heap *heap, long long key, int a, int b) {
        if (heap->size == heap->capacity) {
            heap->capacity *= 2;
            heap->items = realloc(heap->items,
                                  heap->capacity * sizeof(HeapItem));
        }
        int at = heap->size++;
        heap->items[at].key = key;
        heap->items[at].a = a;
        heap->items[at].b = b;
        while (at > 0) {
            int parent = (at - 1) / 2;
            if (heap->items[parent].key <= heap->items[at].key) {
                break;
            }
            HeapItem swap = heap->items[parent];
            heap->items[parent] = heap->items[at];
            heap->items[at] = swap;
            at = parent;
        }
    }

    static HeapItem heapPop(Heap *heap) {
        HeapItem top = heap->items[0];
        heap->items[0] = heap->items[--heap->size];
        int at = 0;
        while (1) {
            int left = at * 2 + 1;
            int right = left + 1;
            int smallest = at;
            if (left < heap->size &&
                heap->items[left].key < heap->items[smallest].key) {
                smallest = left;
            }
            if (right < heap->size &&
                heap->items[right].key < heap->items[smallest].key) {
                smallest = right;
            }
            if (smallest == at) {
                break;
            }
            HeapItem swap = heap->items[smallest];
            heap->items[smallest] = heap->items[at];
            heap->items[at] = swap;
            at = smallest;
        }
        return top;
    }

    static void heapFree(Heap *heap) {
        free(heap->items);
        free(heap);
    }
    """
)

# A flat array queue with head and tail indexes — what the tree and graph
# walks use in place of a deque.
QUEUE_NOTE = "#define MAX_NODES 4096"
