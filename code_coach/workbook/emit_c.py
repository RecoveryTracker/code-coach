"""C: the memory model the C pages never taught.

An audit of the solution bank against the workbook found C in the worst
state of the seven languages. The C solutions call malloc fifty times,
sizeof fifty times and free forty times, and reach through a pointer with
-> on nearly every linked-list and tree problem. The seventy-two C pages
covered four of the forty-nine constructs they use, and none of those.

That is not a missing method. Allocation is most of what C is, and a C
curriculum that never allocates anything has taught you the syntax of a
language you still cannot write. So these pages are that: malloc and the
free that has to match it, sizeof and the count idiom built on it, calloc
and memcpy, the out-parameter that LeetCode signatures in C are made of,
then struct ListNode and struct TreeNode and the arrow.

C only, because none of it has an equivalent to share with. The rule that
every language prints the same characters applies to shared pages, and
there is nothing here to share.

Sizes in bytes are deliberately never printed. They are a property of the
compiler rather than of the program, and a page whose answer changes with
the toolchain is a page that will one day be wrong for no reason. What is
printed instead is what sizeof is *for*: counts that come out the same
everywhere.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("c",)

SHAPES: tuple[Shape, ...] = (
    Shape("c_malloc", "asking for memory and giving it back"),
    Shape("c_sizeof", "how many, when nothing records how many"),
    Shape("c_calloc", "zeroed memory, and copying a block"),
    Shape("c_out_param", "returning a count through a pointer"),
    Shape("c_list_node", "a struct, a pointer, and the arrow"),
    Shape("c_list_ops", "rebuilding a chain that you also have to free"),
    Shape("c_tree_node", "two pointers per node"),
    Shape("c_qsort", "handing a function to a function"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _ints(items) -> str:
    return ", ".join(str(n) for n in items)


def _strs(items) -> str:
    return ", ".join(f'"{s}"' for s in items)


_HEAD = ("#include <stdio.h>", "#include <stdlib.h>", "")
_HEAD_STR = ("#include <stdio.h>", "#include <stdlib.h>",
             "#include <string.h>", "")


def _print_ints(name: str, count: str) -> tuple[str, ...]:
    """Print an int array space separated, with no trailing space.

    Written out rather than hidden behind a helper the student does not
    have, because building the line by hand is what C printing is.
    """
    return (
        f"  for (int i = 0; i < {count}; i++) {{",
        '    if (i > 0) printf(" ");',
        f'    printf("%d", {name}[i]);',
        "  }",
        '  printf("\\n");',
    )


# ── 342. malloc and free ─────────────────────────────────────


def _malloc(a: dict) -> str:
    n, start, step = a["n"], a["start"], a["step"]
    return _lines(
        *_HEAD,
        "int main(void) {",
        f"  int n = {n};",
        "  int *items = malloc(n * sizeof(int));",
        "  if (items == NULL) return 1;",
        "  int total = 0;",
        "  for (int i = 0; i < n; i++) {",
        f"    items[i] = {start} + i * {step};",
        "    total += items[i];",
        "  }",
        *_print_ints("items", "n"),
        '  printf("%d\\n", total);',
        "  free(items);",
        "  return 0;",
        "}",
    )


# ── 343. Counting without a length ───────────────────────────


def _sizeof(a: dict) -> str:
    values = a["values"]
    return _lines(
        *_HEAD,
        "int countHere(int items[]) {",
        "  /* items is a pointer now, not an array: the length did not",
        "     come with it, and sizeof answers about the pointer. */",
        "  return (int)(sizeof(items) / sizeof(items[0]));",
        "}",
        "",
        "int main(void) {",
        f"  int items[] = {{{_ints(values)}}};",
        "  int n = (int)(sizeof(items) / sizeof(items[0]));",
        '  printf("%d\\n", n);',
        '  printf("%d\\n", countHere(items) == n);',
        "  int total = 0;",
        "  for (int i = 0; i < n; i++) total += items[i];",
        '  printf("%d\\n", total);',
        "  return 0;",
        "}",
    )


# ── 344. calloc and memcpy ───────────────────────────────────


def _calloc(a: dict) -> str:
    values = a["values"]
    n = len(values)
    return _lines(
        *_HEAD_STR,
        "int main(void) {",
        f"  int n = {n};",
        "  int *zeroed = calloc(n, sizeof(int));",
        "  if (zeroed == NULL) return 1;",
        "  int before = 0;",
        "  for (int i = 0; i < n; i++) before += zeroed[i];",
        '  printf("%d\\n", before);',
        f"  int source[] = {{{_ints(values)}}};",
        "  memcpy(zeroed, source, n * sizeof(int));",
        *_print_ints("zeroed", "n"),
        "  free(zeroed);",
        "  return 0;",
        "}",
    )


# ── 345. The out-parameter ───────────────────────────────────


def _out_param(a: dict) -> str:
    values, over = a["values"], a["over"]
    return _lines(
        *_HEAD,
        "int *pick(int *nums, int numsSize, int over, int *returnSize) {",
        "  int *out = malloc(numsSize * sizeof(int));",
        "  int kept = 0;",
        "  for (int i = 0; i < numsSize; i++) {",
        "    if (nums[i] > over) out[kept++] = nums[i];",
        "  }",
        "  *returnSize = kept;",
        "  return out;",
        "}",
        "",
        "int main(void) {",
        f"  int nums[] = {{{_ints(values)}}};",
        "  int n = (int)(sizeof(nums) / sizeof(nums[0]));",
        "  int count = 0;",
        f"  int *kept = pick(nums, n, {over}, &count);",
        '  printf("%d\\n", count);',
        *_print_ints("kept", "count"),
        "  free(kept);",
        "  return 0;",
        "}",
    )


# ── 346-347. Chains ──────────────────────────────────────────

_LIST_NODE = (
    "struct ListNode {",
    "  int val;",
    "  struct ListNode *next;",
    "};",
    "",
    "struct ListNode *makeNode(int val) {",
    "  struct ListNode *node = malloc(sizeof(struct ListNode));",
    "  node->val = val;",
    "  node->next = NULL;",
    "  return node;",
    "}",
    "",
)

_FREE_CHAIN = (
    "void freeChain(struct ListNode *head) {",
    "  while (head != NULL) {",
    "    struct ListNode *next = head->next;",
    "    free(head);",
    "    head = next;",
    "  }",
    "}",
    "",
)

_PRINT_CHAIN = (
    "void printChain(struct ListNode *head) {",
    "  for (struct ListNode *n = head; n != NULL; n = n->next) {",
    '    if (n != head) printf(" -> ");',
    '    printf("%d", n->val);',
    "  }",
    '  printf("\\n");',
    "}",
    "",
)


def _build_chain(values) -> tuple[str, ...]:
    return (
        f"  int values[] = {{{_ints(values)}}};",
        "  int n = (int)(sizeof(values) / sizeof(values[0]));",
        "  struct ListNode *head = NULL, *tail = NULL;",
        "  for (int i = 0; i < n; i++) {",
        "    struct ListNode *node = makeNode(values[i]);",
        "    if (head == NULL) head = node;",
        "    else tail->next = node;",
        "    tail = node;",
        "  }",
    )


def _list_node(a: dict) -> str:
    want = a["want"]
    tail: tuple[str, ...]
    if want == "sum":
        tail = (
            "  int total = 0;",
            "  for (struct ListNode *n = head; n != NULL; n = n->next)",
            "    total += n->val;",
            '  printf("%d\\n", total);',
        )
    elif want == "count":
        tail = (
            "  int count = 0;",
            "  for (struct ListNode *n = head; n != NULL; n = n->next)",
            "    count++;",
            '  printf("%d\\n", count);',
        )
    else:
        tail = (
            "  int best = head->val;",
            "  for (struct ListNode *n = head; n != NULL; n = n->next)",
            "    if (n->val > best) best = n->val;",
            '  printf("%d\\n", best);',
        )
    return _lines(
        *_HEAD,
        *_LIST_NODE,
        *_FREE_CHAIN,
        *_PRINT_CHAIN,
        "int main(void) {",
        *_build_chain(a["values"]),
        "  printChain(head);",
        *tail,
        "  freeChain(head);",
        "  return 0;",
        "}",
    )


def _list_ops(a: dict) -> str:
    if a["want"] == "reverse":
        return _lines(
            *_HEAD,
            *_LIST_NODE,
            *_FREE_CHAIN,
            *_PRINT_CHAIN,
            "int main(void) {",
            *_build_chain(a["values"]),
            "  struct ListNode *prev = NULL;",
            "  struct ListNode *cur = head;",
            "  while (cur != NULL) {",
            "    struct ListNode *next = cur->next;",
            "    cur->next = prev;",
            "    prev = cur;",
            "    cur = next;",
            "  }",
            "  printChain(prev);",
            "  freeChain(prev);",
            "  return 0;",
            "}",
        )
    left, right = a["left"], a["right"]
    return _lines(
        *_HEAD,
        *_LIST_NODE,
        *_FREE_CHAIN,
        *_PRINT_CHAIN,
        "int main(void) {",
        f"  int leftValues[] = {{{_ints(left)}}};",
        f"  int rightValues[] = {{{_ints(right)}}};",
        "  int leftSize = (int)(sizeof(leftValues) / sizeof(leftValues[0]));",
        "  int rightSize = (int)(sizeof(rightValues) / sizeof(rightValues[0]));",
        "  struct ListNode dummy;",
        "  dummy.next = NULL;",
        "  struct ListNode *tail = &dummy;",
        "  int i = 0, j = 0;",
        "  while (i < leftSize && j < rightSize) {",
        "    if (leftValues[i] <= rightValues[j]) tail->next = makeNode(leftValues[i++]);",
        "    else tail->next = makeNode(rightValues[j++]);",
        "    tail = tail->next;",
        "  }",
        "  while (i < leftSize) { tail->next = makeNode(leftValues[i++]); tail = tail->next; }",
        "  while (j < rightSize) { tail->next = makeNode(rightValues[j++]); tail = tail->next; }",
        "  printChain(dummy.next);",
        "  freeChain(dummy.next);",
        "  return 0;",
        "}",
    )


# ── 348. Trees ───────────────────────────────────────────────

_TREE_NODE = (
    "struct TreeNode {",
    "  int val;",
    "  struct TreeNode *left;",
    "  struct TreeNode *right;",
    "};",
    "",
    "struct TreeNode *makeNode(int val) {",
    "  struct TreeNode *node = malloc(sizeof(struct TreeNode));",
    "  node->val = val;",
    "  node->left = NULL;",
    "  node->right = NULL;",
    "  return node;",
    "}",
    "",
    "void freeTree(struct TreeNode *node) {",
    "  if (node == NULL) return;",
    "  freeTree(node->left);",
    "  freeTree(node->right);",
    "  free(node);",
    "}",
    "",
    "int depth(struct TreeNode *node) {",
    "  if (node == NULL) return 0;",
    "  int a = depth(node->left);",
    "  int b = depth(node->right);",
    "  return 1 + (a > b ? a : b);",
    "}",
    "",
    "int total(struct TreeNode *node) {",
    "  if (node == NULL) return 0;",
    "  return node->val + total(node->left) + total(node->right);",
    "}",
    "",
)


def _tree_node(a: dict) -> str:
    """The tree is built by hand, node by node.

    A level-order builder needs a queue, and C has no queue: writing one
    would make the page about the queue. Naming every link is also closer
    to what the solutions do.
    """
    values = a["values"]
    lines = [f"  struct TreeNode *n{i} = makeNode({v});"
             for i, v in enumerate(values)]
    for i in range(len(values)):
        left, right = 2 * i + 1, 2 * i + 2
        if left < len(values):
            lines.append(f"  n{i}->left = n{left};")
        if right < len(values):
            lines.append(f"  n{i}->right = n{right};")
    return _lines(
        *_HEAD,
        *_TREE_NODE,
        "int main(void) {",
        *lines,
        '  printf("%d\\n", n0->val);',
        '  printf("%d\\n", depth(n0));',
        '  printf("%d\\n", total(n0));',
        "  freeTree(n0);",
        "  return 0;",
        "}",
    )


# ── 349. qsort ───────────────────────────────────────────────


def _qsort(a: dict) -> str:
    if a["want"] == "ints":
        return _lines(
            *_HEAD,
            "static int byValue(const void *a, const void *b) {",
            "  return *(const int *)a - *(const int *)b;",
            "}",
            "",
            "int main(void) {",
            f"  int items[] = {{{_ints(a['values'])}}};",
            "  int n = (int)(sizeof(items) / sizeof(items[0]));",
            "  qsort(items, n, sizeof(int), byValue);",
            *_print_ints("items", "n"),
            "  return 0;",
            "}",
        )
    return _lines(
        *_HEAD_STR,
        "static int byLength(const void *a, const void *b) {",
        "  const char *x = *(const char *const *)a;",
        "  const char *y = *(const char *const *)b;",
        "  int diff = (int)strlen(x) - (int)strlen(y);",
        "  return diff != 0 ? diff : strcmp(x, y);",
        "}",
        "",
        "int main(void) {",
        f"  const char *words[] = {{{_strs(a['words'])}}};",
        "  int n = (int)(sizeof(words) / sizeof(words[0]));",
        "  qsort(words, n, sizeof(const char *), byLength);",
        "  for (int i = 0; i < n; i++) {",
        '    if (i > 0) printf(" ");',
        '    printf("%s", words[i]);',
        "  }",
        '  printf("\\n");',
        "  return 0;",
        "}",
    )


_BUILDERS = {
    "c_malloc": _malloc,
    "c_sizeof": _sizeof,
    "c_calloc": _calloc,
    "c_out_param": _out_param,
    "c_list_node": _list_node,
    "c_list_ops": _list_ops,
    "c_tree_node": _tree_node,
    "c_qsort": _qsort,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def _joined(items) -> str:
    return " ".join(str(n) for n in items)


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out in Python, never by reading the C back.

    Nothing here prints a size in bytes, so nothing here depends on the
    compiler. The one place a byte size could leak in is page 343, where
    the decayed count is compared rather than printed, and the guard keeps
    the data away from the length where that comparison could be true by
    accident.
    """
    a = args
    if shape == "c_malloc":
        n, start, step = a["n"], a["start"], a["step"]
        if n < 2:
            raise ValueError("allocating one int does not show a size")
        if step == 0:
            raise ValueError("a step of zero makes every element the same")
        items = [start + i * step for i in range(n)]
        return NL.join([_joined(items), str(sum(items))])
    if shape == "c_sizeof":
        values = list(a["values"])
        n = len(values)
        if n < 3:
            # A pointer over an int is two on this target and one on a
            # 32-bit one. At three or more the decayed count cannot equal
            # the real one on any platform, so the comparison stays false
            # for the reason the page is about rather than by luck.
            raise ValueError(
                "fewer than three elements and the decayed count could "
                "match the real one by accident"
            )
        return NL.join([str(n), "0", str(sum(values))])
    if shape == "c_calloc":
        values = list(a["values"])
        if not values:
            raise ValueError("copying nothing shows nothing")
        return NL.join(["0", _joined(values)])
    if shape == "c_out_param":
        values, over = list(a["values"]), a["over"]
        kept = [v for v in values if v > over]
        if not kept:
            raise ValueError("the filter must keep something")
        if len(kept) == len(values):
            raise ValueError(
                "the filter must drop something, or the count written "
                "through the pointer is just the input size"
            )
        return NL.join([str(len(kept)), _joined(kept)])
    if shape == "c_list_node":
        values = list(a["values"])
        if len(values) < 2:
            raise ValueError("a chain needs more than one node")
        chain = " -> ".join(str(v) for v in values)
        want = a["want"]
        if want == "max" and values[0] == max(values):
            raise ValueError("the largest must not be the head")
        got = {"sum": sum(values), "count": len(values),
               "max": max(values)}[want]
        return NL.join([chain, str(got)])
    if shape == "c_list_ops":
        if a["want"] == "reverse":
            values = list(a["values"])
            if values == values[::-1]:
                raise ValueError("a chain that reads the same both ways")
            return " -> ".join(str(v) for v in reversed(values))
        left, right = list(a["left"]), list(a["right"])
        for side in (left, right):
            if side != sorted(side):
                raise ValueError("each chain must already be sorted")
        merged = sorted(left + right)
        if merged in (left + right, right + left):
            raise ValueError("the two chains must interleave")
        return " -> ".join(str(v) for v in merged)
    if shape == "c_tree_node":
        values = list(a["values"])
        if len(values) < 4:
            raise ValueError("a tree this small has nothing to recurse into")
        # Depth of a complete tree laid out by index: the deepest filled
        # position decides it.
        depth = 0
        while (1 << depth) - 1 < len(values):
            depth += 1
        return NL.join([str(values[0]), str(depth), str(sum(values))])
    if shape == "c_qsort":
        if a["want"] == "ints":
            values = list(a["values"])
            if values == sorted(values):
                raise ValueError("the data must not already be sorted")
            return _joined(sorted(values))
        words = list(a["words"])
        order = sorted(words, key=lambda w: (len(w), w))
        if order == words:
            raise ValueError("the words must not already be in order")
        if len({len(w) for w in words}) < 2:
            raise ValueError(
                "the words must differ in length, or sorting by length is "
                "indistinguishable from sorting alphabetically"
            )
        return " ".join(order)
    raise KeyError(shape)
