"""C words, part 5: the words the pointer, string and type packs added - truncation, out-parameters, end pointers,
linked lists, buffers, bytes and strtok. Examples as in terms_c_core.py."""

from __future__ import annotations

from .entry import Entry, c

TERMS: list[Entry] = [
    *c(
        "truncation",
        "Truncation",
        "Cutting a value short. Converting a double to int drops the fraction, integer division drops the remainder, a narrow type keeps only the low bits, and snprintf cuts text that does not fit.",
        see=("type-conversion", "division", "cast", "snprintf"),
        priority=40,
        aka=("truncate", "truncated", "truncating", "cut off", "narrowing", "narrowing conversion", "lost precision", "lose the fraction", "rounds toward zero"),
        rules=(
            r"7.9 stored in an int is 7 and -7.9 is -7: C cuts toward zero, it does not round.",
            r"300 stored in a uint8_t is 44 (only the low 8 bits survive).",
            r'''snprintf(buf, 4, "%s", "abcdef") keeps "abc" and the terminator; the return value says it was cut.''',
            r"7 / 2 is 3: integer division truncates too.",
        ),
        example=r"""
            double d = 7.9;
            int n = d;
            int big = 300;
            uint8_t low = big;
            char buf[4];
            snprintf(buf, sizeof buf, "%s", "abcdef");
            printf("%d %d %s %d\n", n, low, buf, 7 / 2);
        """,
        out=r"7 44 abc 3",
    ),
    *c(
        "out-parameter",
        "Out-parameter",
        "A pointer parameter a function writes its result through, so the caller gets values back without a return. It is how C returns more than one value: divmod(17, 5, &q, &r).",
        see=("pass-by-value", "pointer", "address-of", "swap"),
        priority=45,
        aka=("output parameter", "out param", "return through pointer", "return multiple values", "by-reference parameter", "result parameter", "pointer parameter"),
        rules=(
            r"The caller passes &variable; the function assigns through *parameter.",
            r"The variable must already exist in the caller (and should be set before you read it if the function can fail).",
            r"Document which parameters are inputs and which are outputs; const marks the inputs.",
        ),
        example=r"""
            static void divmod(int a, int b, int *q, int *r) { *q = a / b; *r = a % b; }
            int main(void) {
                int q, r;
                divmod(17, 5, &q, &r);
                printf("%d %d\n", q, r);
                return 0;
            }
        """,
        out=r"3 2",
    ),
    *c(
        "end-pointer",
        "End pointer",
        "A pointer to the position just after the last element of an array (a + n). A loop runs while the walking pointer is below it. Forming and comparing it is allowed; reading through it is not.",
        see=("pointer-arithmetic", "array", "off-by-one", "dereference"),
        priority=45,
        aka=("one past the end", "past-the-end pointer", "end of array", "sentinel pointer", "pointer loop", "pointer range", "end marker"),
        rules=(
            r"for (int *p = a; p < end; p++) visits every element once; the end pointer itself points at nothing valid.",
            r"end - a is the number of elements.",
            r"Anything beyond a + n is undefined behaviour even to form.",
        ),
        example=r"""
            int a[4] = {1, 2, 3, 4};
            int *end = a + 4;
            int sum = 0;
            for (int *p = a; p < end; p++) sum += *p;
            printf("%d %d\n", sum, (int)(end - a));
        """,
        out=r"10 4",
    ),
    *c(
        "linked-list",
        "Linked list",
        "A chain of structs, each holding a value and a pointer to the next one; the last one points to NULL. You walk it by following the pointers.",
        see=("struct", "arrow-operator", "null-pointer", "dynamic-memory"),
        priority=50,
        aka=("list", "linked lists", "node", "nodes", "next pointer", "singly linked list", "self-referential struct", "chain", "head pointer", "list node", "linked"),
        detect=(r"\bstruct[ \t]+\w+[ \t]*\*[ \t]*next\b|->[ \t]*next\b",),
        rules=(
            r"struct Node { int value; struct Node *next; }; may point to itself because it is a pointer.",
            r"Walk: for (p = head; p != NULL; p = p->next).",
            r"Nodes usually come from malloc and must each be freed; insert and remove by changing next pointers, with no shifting.",
            r"No random access: reaching the 10th item means following 9 links.",
        ),
        example=r"""
            struct Node { int value; struct Node *next; };
            struct Node c = {3, NULL};
            struct Node b = {2, &c};
            struct Node a = {1, &b};
            int sum = 0;
            for (struct Node *p = &a; p != NULL; p = p->next) sum += p->value;
            printf("%d\n", sum);
        """,
        out=r"6",
    ),
    *c(
        "buffer",
        "Buffer",
        "A block of memory, usually a char array, that holds data on its way somewhere. Its capacity (sizeof) is fixed; how much is used right now is a separate number you must track.",
        see=("buffer-overflow", "snprintf", "null-terminator", "memset"),
        priority=35,
        aka=("buffers", "char buffer", "byte buffer", "capacity", "buf", "scratch space", "storage", "memory block"),
        rules=(
            r"sizeof buf is the capacity; strlen(buf) is the length of the text inside it, which can be much smaller.",
            r"Every function that fills a buffer needs the capacity; going past it is a buffer overflow.",
            r"Leave one byte for the terminator when the buffer holds a string.",
        ),
        example=r"""
            char buf[16];
            int used = snprintf(buf, sizeof buf, "%s-%d", "item", 42);
            printf("%s %d %d\n", buf, used, (int)sizeof buf);
        """,
        out=r"item-42 7 16",
    ),
    *c(
        "byte",
        "Byte",
        "A group of 8 bits, the smallest piece of memory C can address. A char is exactly one byte; unsigned char and uint8_t hold a byte as the number 0 to 255.",
        see=("fixed-width-integer", "sizeof", "unsigned", "memcpy"),
        priority=35,
        aka=("bytes", "octet", "8 bits", "byte value", "unsigned char", "byte array", "raw bytes"),
        rules=(
            r"sizeof(char) is 1 by definition, and CHAR_BIT (from limits.h) is 8.",
            r"A byte as a number wraps at 256: an unsigned char holding 255 becomes 0 after ++.",
            r"memcpy, memset and memcmp count in bytes.",
        ),
        example=r"""
            unsigned char b = 255;
            b++;
            printf("%d %d %d\n", (int)sizeof(char), (int)sizeof(uint8_t), b);
        """,
        out=r"1 1 0",
    ),
    *c(
        "strtok",
        "strtok",
        "strtok(s, delimiters) splits a string into pieces. The first call gets the string; each later call gets NULL and returns the next piece, until NULL. It writes '\\0' into the string, so the string is changed.",
        see=("strchr", "string", "null-terminator", "string-to-number"),
        priority=55,
        aka=("tokenize", "split a string", "split string", "tokenizer", "string split", "strsep", "split", "token"),
        detect=(r"\bstrtok\b",),
        rules=(
            r'''Pass the string only the first time, then NULL: strtok(NULL, ",").''',
            r"The string must be a changeable char array, not a string literal.",
            r'''Runs of delimiters count as one, so empty fields are skipped ("a,b,,c" gives a, b, c).''',
            r"It remembers its place in hidden state: not thread-safe, and you cannot split two strings at once.",
        ),
        example=r"""
            char line[] = "a,b,,c";
            int n = 0;
            for (char *t = strtok(line, ","); t != NULL; t = strtok(NULL, ",")) n++;
            printf("%d\n", n);
        """,
        out=r"3",
    ),
]
