"""C words, part 3: memory - arrays, pointers, dynamic memory, structs, unions, enums, typedefs and function pointers.

Examples are the BODY of `main` unless they mention `main(` (then a complete program that may #include more); see
terms_c_core.py."""

from __future__ import annotations

from .entry import Entry, c

TERMS: list[Entry] = [
    *c(
        "array",
        "Array",
        "A fixed row of values of one type stored side by side: int a[5]; holds five ints, a[0] to a[4]. The size is fixed when it is declared.",
        see=("index", "array-decay", "initialization", "multidimensional-array", "sizeof"),
        priority=40,
        aka=("arrays", "int array", "char array", "array of ints", "list", "vector", "subscript", "element", "elements", "fixed size array", "fixed-size array"),
        detect=(r"\b(?:int|char|float|double|long|short|size_t|u?int\d+_t)[ \t]+[A-Za-z_]\w*[ \t]*\[[ \t]*\w*[ \t]*\]",),
        rules=(
            r"Elements are numbered from 0; an array of n has indexes 0 to n - 1, and C never checks the index.",
            r"An array does not know its length: the element count is sizeof a / sizeof a[0], and only where the name is still an array (not a function parameter).",
            r"a[i] is the same as *(a + i). Arrays cannot be assigned or compared with == as a whole; copy with memcpy or a loop.",
            r"All elements are the same type and sit next to each other in memory.",
        ),
        example=r"""
            int a[4] = {10, 20, 30, 40};
            int sum = 0;
            for (int i = 0; i < 4; i++) sum += a[i];
            printf("%d %d %d\n", a[0], a[3], sum);
            printf("%d\n", (int)(sizeof a / sizeof a[0]));
        """,
        out=r"""10 40 100
4""",
    ),
    *c(
        "index",
        "Index",
        "The position number of an element in an array, counted from 0: a[0] is the first, a[n - 1] the last of n.",
        see=("array", "off-by-one", "buffer-overflow", "pointer-arithmetic"),
        priority=35,
        aka=("indexing", "indices", "indexes", "subscript", "position", "array index", "[]", "square brackets", "out of range", "bounds"),
        detect=(r"[\w\]][ \t]*\[[ \t]*[\w+*-]{1,12}[ \t]*\]",),
        rules=(
            r"Indexes start at 0, so the third element is a[2].",
            r"An index outside 0..n-1 is undefined behaviour - no error, just a read or write of someone else's memory. A negative index too.",
            r"a[i] means *(a + i), which is why even 1[a] works.",
            r"Loops over n elements use i < n, never i <= n.",
        ),
        example=r"""
            int a[3] = {5, 6, 7};
            printf("%d %d\n", a[0], a[2]);
            printf("%d %d\n", *(a + 1), 1[a]);
        """,
        out=r"""5 7
6 6""",
    ),
    *c(
        "array-decay",
        "Array decay",
        "In most expressions an array name turns into a pointer to its first element. Passing an array to a function therefore passes only a pointer, and sizeof inside the function gives the pointer's size.",
        see=("sizeof", "pointer", "pass-by-value", "pointer-arithmetic"),
        priority=50,
        aka=("decay", "array to pointer", "array parameter", "decays", "array as parameter", "decays to a pointer", "array name"),
        detect=(r"\(\s*(?:const[ \t]+)?(?:int|char|double|float|long)[ \t]+\w+\[\s*\w*\s*\]",),
        rules=(
            r"void f(int a[]) is exactly void f(int *a): the length is lost, so pass it as a second argument.",
            r"The exceptions where an array stays an array: sizeof a, &a, and a string-literal initialiser.",
            r"That is why sizeof a / sizeof a[0] works in the function that declares the array and not in the function it is passed to.",
            r"Changes to the elements inside the function are seen by the caller (it shares the same memory).",
        ),
        example=r"""
            static int count_in_function(int a[]) { return (int)(sizeof a / sizeof a[0]); }
            int main(void) {
                int a[10] = {0};
                int here = (int)(sizeof a / sizeof a[0]);
                int there = count_in_function(a);
                printf("%d %d\n", here, there == here);
                return 0;
            }
        """,
        out=r"10 0",
    ),
    *c(
        "multidimensional-array",
        "Two-dimensional array",
        "An array of arrays: int m[2][3]; is 2 rows of 3 ints. Element m[i][j] is row i, column j, and the rows are stored one after another in memory.",
        see=("array", "index", "nested-loop", "initialization"),
        priority=50,
        aka=("2d array", "2-d array", "two dimensional array", "matrix", "grid", "multidimensional", "multi-dimensional array", "array of arrays", "table", "rows and columns", "2d", "nested array"),
        detect=(r"\w[ \t]*\[[ \t]*\w*[ \t]*\][ \t]*\[[ \t]*\w*[ \t]*\]",),
        rules=(
            r"int m[2][3] = {{1, 2, 3}, {4, 5, 6}}; fills row by row; a flat list {1, 2, 3, 4, 5, 6} fills the same way (the compiler may warn about braces).",
            r"All sizes but the first must be given in a definition with initialiser and in a parameter: void f(int m[][3]).",
            r"sizeof m / sizeof m[0] is the number of rows; sizeof m[0] / sizeof m[0][0] the columns.",
            r"Memory order is row-major: m[0][2] is right before m[1][0].",
        ),
        example=r"""
            int m[2][3] = {{1, 2, 3}, {4, 5, 6}};
            int flat[2][2] = {1, 2, 3, 4};
            printf("%d %d\n", m[1][0], m[0][2]);
            printf("%d %d\n", flat[1][0], (int)(sizeof m / sizeof m[0]));
        """,
        out=r"""4 3
3 2""",
    ),
    *c(
        "array-of-strings",
        "Array of strings",
        "An array whose elements are char pointers, each pointing at a string: const char *names[] = {\"Ann\", \"Bob\"};. names[1] is a string, names[1][0] its first character.",
        see=("string", "array", "pointer", "pointer-to-pointer"),
        priority=45,
        aka=("string array", "array of pointers", "array-of-pointers", "pointer array", "array of char pointers", "char *argv[]", "list of strings", "strings array", "argv", "words array"),
        detect=(r"\bchar[ \t]*\*[ \t]*\w+[ \t]*\[[ \t]*\w*[ \t]*\]",),
        rules=(
            r"The strings can have different lengths: the array holds only pointers.",
            r"sizeof names / sizeof names[0] is the number of strings.",
            r"Two subscripts read letters: names[2][0] is the first letter of the third string.",
            r"char **argv in main is the same idea: argv[0] is the program's name.",
        ),
        example=r"""
            const char *days[] = {"Mon", "Tue", "Wed"};
            printf("%s %c %d\n", days[1], days[2][0], (int)(sizeof days / sizeof days[0]));
        """,
        out=r"Tue W 3",
    ),
    *c(
        "pointer",
        "Pointer",
        "A variable that holds the memory address of another value. int *p = &x; makes p point at x; *p is x itself.",
        see=("address-of", "dereference", "null-pointer", "pointer-arithmetic", "pass-by-value"),
        priority=50,
        aka=("pointers", "ptr", "int *", "reference", "points to", "pointer variable", "pointee", "pointer type", "char *", "int*"),
        detect=(r"\b(?:int|char|float|double|void|long|short|struct[ \t]+\w+|u?int\d+_t|size_t)[ \t]*\*+[ \t]*[A-Za-z_]\w*",),
        rules=(
            r"In int *p, the * says p is a pointer to an int; later, *p means the int p points at.",
            r"A pointer has its own size (8 bytes on a 64-bit machine) whatever it points to.",
            r"An uninitialised or dangling pointer points nowhere valid; initialise it to an address or to NULL.",
            r"Two pointers may point at the same object, so changing it through one is seen through the other.",
        ),
        example=r"""
            int x = 10;
            int *p = &x;
            *p = 25;
            printf("%d %d\n", x, *p);
            printf("%d\n", p == &x);
        """,
        out=r"""25 25
1""",
    ),
    *c(
        "address-of",
        "Address-of",
        "The & operator in front of a variable gives its memory address: &x is a pointer to x.",
        see=("pointer", "dereference", "array", "pass-by-value"),
        priority=45,
        aka=("address", "memory address", "addresses of", "&", "address operator", "reference operator", "take address", "address of", "memory address of", ),
        detect=(r"(?:[=(,]|return)[ \t]*&[ \t]*[A-Za-z_]\w*",),
        rules=(
            r"&x has type pointer-to-x's-type; it works on variables and elements, not on values (&5 is an error).",
            r"&a[i] is the same as a + i.",
            r"Printed addresses (%p) change from run to run, so a correct program never depends on them.",
            r"Pass &x to a function so it can change x (see pass by value).",
        ),
        example=r"""
            int a[3] = {1, 2, 3};
            int *p = &a[1];
            printf("%d %d\n", *p, (int)(&a[2] - &a[0]));
            printf("%d\n", &a[0] == a);
        """,
        out=r"""2 2
1""",
    ),
    *c(
        "dereference",
        "Dereference",
        "The * operator in front of a pointer: go to the address and use the value that lives there, to read it or to write it. *p is the thing p points at.",
        see=("pointer", "null-pointer", "arrow-operator", "pointer-arithmetic"),
        priority=45,
        aka=("dereferencing", "indirection", "*p", "follow a pointer", "deref", "indirection operator", "dereference operator", "value at address"),
        detect=(r"(?:^|[=(,;{][ \t]*)\*[ \t]*[A-Za-z_(]\w*",),
        rules=(
            r"*p = 5; writes through the pointer; int y = *p; reads through it.",
            r"Dereferencing NULL, a freed pointer or an out-of-range address is undefined behaviour (often a crash).",
            r"Unary * binds tighter than +: *p + 1 is (*p) + 1, and (*p)++ increments the target while *p++ moves the pointer.",
            r"(*p).x and p->x are the same.",
        ),
        example=r"""
            int x = 3;
            int *p = &x;
            *p = *p * 2;
            (*p)++;
            printf("%d\n", x);
            int *q = p;
            *q += 10;
            printf("%d %d\n", x, *p);
        """,
        out=r"""7
17 17""",
    ),
    *c(
        "null-pointer",
        "NULL pointer",
        "A pointer that points at nothing, written NULL (a macro for the null address 0). Dereferencing it is undefined behaviour, usually a crash.",
        see=("pointer", "dereference", "segmentation-fault", "dynamic-memory"),
        priority=55,
        aka=("null", "nullptr", "null pointer", "NULL", "null check", "check for null", "pointer is null", "empty pointer", "null address"),
        detect=(r"\bNULL\b",),
        rules=(
            r"NULL counts as false: if (p) means p != NULL, and !p means p == NULL.",
            r"Functions signal failure by returning NULL (malloc, strchr, strstr, fopen): check before you use the result.",
            r"A global or static pointer starts as NULL; a local one is garbage until you set it.",
            r"free(NULL) is allowed and does nothing.",
        ),
        example=r"""
            int *p = NULL;
            int x = 5;
            printf("%d\n", p == NULL);
            if (!p) p = &x;
            printf("%d\n", *p);
            printf("%d\n", strchr("abc", 'z') == NULL);
        """,
        out=r"""1
5
1""",
    ),
    *c(
        "pointer-arithmetic",
        "Pointer arithmetic",
        "Adding n to a pointer moves it n ELEMENTS (the compiler multiplies by the element size), not n bytes. Subtracting two pointers gives how many elements lie between them.",
        see=("pointer", "array", "index", "increment", "dereference"),
        priority=55,
        aka=("pointer math", "pointer arithmetics", "p + 1", "*p++", "pointer increment", "pointer addition", "pointer subtraction", "walk an array", "pointer walk", "pointer difference", "pointer comparison"),
        detect=(r"\*[ \t]*\(?[ \t]*\w+[ \t]*\+[ \t]*\w+[ \t]*\)|\*[ \t]*\w+[ \t]*(?:\+\+|--)|(?:\+\+|--)[ \t]*\w+\b[ \t]*;[ \t]*//|\bptrdiff_t\b|\b\w{1,40}[ \t]*\+[ \t]*\w{1,40}[ \t]*\)[ \t]*-[ \t]*\w+\b",),
        rules=(
            r"For int *p, p + 1 is the next int (4 bytes on); for char *p it is the next byte.",
            r"p[i] is *(p + i); p2 - p1 counts elements and has type ptrdiff_t.",
            r"*p++ means *(p++): use the value, then step the pointer on. (*p)++ changes the value instead.",
            r"Stay inside the array (one past the end is allowed for comparing, not for reading), otherwise it is undefined behaviour.",
        ),
        example=r"""
            int a[4] = {10, 20, 30, 40};
            int *p = a;
            printf("%d\n", *(p + 2));
            int first = *p++;
            printf("%d %d %d\n", first, *p, (int)((a + 3) - p));
        """,
        out=r"""30
10 20 2""",
    ),
    *c(
        "pointer-to-pointer",
        "Pointer to pointer",
        "A pointer that holds the address of another pointer: int **pp = &p;. *pp is the pointer p, **pp the int it points at.",
        see=("pointer", "dereference", "array-of-strings", "pass-by-value"),
        priority=50,
        aka=("double pointer", "pointer pointer", "int **", "char **", "double-pointer", "pointer to a pointer", "**", "multiple indirection"),
        detect=(r"\*\*[ \t]*[A-Za-z_]\w*|\w[ \t]*\*\*[ \t]*[,)]",),
        rules=(
            r"Use it to let a function change a pointer: pass &p and assign *pp inside.",
            r"Each * peels one level: pp, *pp, **pp.",
            r"char **argv (an array of strings) is the everyday example.",
        ),
        example=r"""
            int x = 1;
            int *p = &x;
            int **pp = &p;
            **pp = 42;
            int y = 7;
            *pp = &y;
            printf("%d %d %d\n", x, *p, **pp);
        """,
        out=r"42 7 7",
    ),
    *c(
        "void-pointer",
        "Void pointer",
        "void * is a pointer to a thing of unknown type. Any pointer converts to it and back without a cast, which is how malloc, memcpy and qsort handle any type.",
        see=("pointer", "cast", "dynamic-memory", "qsort"),
        priority=50,
        aka=("void *", "generic pointer", "void*", "untyped pointer", "pointer to void", "void star"),
        detect=(r"\bvoid[ \t]*\*",),
        rules=(
            r"You cannot dereference a void * or do arithmetic on it: convert it to a typed pointer first (int *back = v;).",
            r"In C (not C++) the conversion is automatic, so malloc needs no cast.",
            r"Converting back to the wrong type is undefined behaviour.",
        ),
        example=r"""
            int n = 5;
            void *v = &n;
            int *back = v;
            printf("%d\n", *back);
            printf("%d\n", *(int *)v + 1);
        """,
        out=r"""5
6""",
    ),
    *c(
        "const-pointer",
        "Const and pointers",
        "Where const sits changes its meaning: const int *p is a pointer to a constant int (the int cannot be changed through p), int *const p is a constant pointer (p cannot be pointed elsewhere).",
        see=("constant", "pointer", "dereference", "string-literal"),
        priority=55,
        aka=("pointer to const", "const pointer", "const char *", "const int *", "constant pointer", "read-only pointer", "int *const", "const correctness"),
        detect=(r"\bconst[ \t]+[A-Za-z_]\w*[ \t]*\*|\*[ \t]*const\b",),
        rules=(
            r"Read the declaration from the name outward: p is a pointer to const int; cp is a const pointer to int.",
            r"const int *pc: pc = &b; is fine, *pc = 5; is an error. int *const cp: *cp = 9; is fine, cp = &b; is an error.",
            r"const char * is the right type for a string literal and for a parameter the function only reads.",
        ),
        example=r"""
            int a = 1, b = 2;
            const int *pc = &a;
            pc = &b;
            int *const cp = &a;
            *cp = 9;
            printf("%d %d %d\n", *pc, a, b);
        """,
        out=r"2 9 2",
    ),
    *c(
        "dangling-pointer",
        "Dangling pointer",
        "A pointer to memory that is no longer yours: after free, or the address of a local variable whose function has returned. Using it is undefined behaviour.",
        see=("dynamic-memory", "null-pointer", "storage-duration", "undefined-behavior"),
        priority=50,
        aka=("dangling", "use after free", "use-after-free", "wild pointer", "stale pointer", "invalid pointer", "double free", "returning address of local", "memory leak"),
        rules=(
            r"After free(p), set p = NULL: a later free(p) is then harmless and if (p) tests are honest.",
            r"Never return &local from a function: the variable disappears on return.",
            r"A dangling pointer often still seems to work, which makes the bug hard to find (use -fsanitize=address).",
        ),
        example=r"""
            #include <stdlib.h>
            int main(void) {
                int *p = malloc(sizeof *p);
                if (p == NULL) return 1;
                *p = 8;
                printf("%d\n", *p);
                free(p);
                p = NULL;
                printf("%d\n", p == NULL);
                return 0;
            }
        """,
        out=r"""8
1""",
    ),
    *c(
        "dynamic-memory",
        "Dynamic memory",
        "Memory you ask for while the program runs with malloc (or calloc) and give back with free. It lives until you free it, not until the function ends.",
        see=("pointer", "null-pointer", "dangling-pointer", "storage-duration", "void-pointer"),
        priority=60,
        aka=("malloc", "calloc", "realloc", "free", "heap", "heap memory", "allocation", "memory allocation", "memory leak", "stdlib", "stdlib.h", "allocate memory", "new"),
        detect=(r"\b(?:malloc|calloc|realloc|free)[ \t]*\(|<stdlib\.h>",),
        rules=(
            r"malloc(n) gives n uninitialised bytes, or NULL if it fails; calloc(count, size) gives zeroed memory.",
            r"Write malloc(n * sizeof *p) so the size follows the type; check for NULL.",
            r"Every successful allocation needs exactly one free; forgetting it is a memory leak, freeing twice is undefined behaviour.",
            r"realloc may move the block and returns the new address: keep the old pointer until you know it did not fail.",
        ),
        example=r"""
            #include <stdlib.h>
            int main(void) {
                int n = 4;
                int *a = calloc((size_t)n, sizeof *a);
                if (a == NULL) return 1;
                for (int i = 0; i < n; i++) a[i] += i * i;
                printf("%d %d\n", a[0], a[3]);
                int *b = realloc(a, 8 * sizeof *a);
                if (b == NULL) { free(a); return 1; }
                b[7] = 5;
                printf("%d %d\n", b[3], b[7]);
                free(b);
                return 0;
            }
        """,
        out=r"""0 9
9 5""",
    ),
    *c(
        "struct",
        "Struct",
        "A bundle of named values, called members, of possibly different types stored together: struct Point { int x; int y; };. Each variable of that type has its own x and y.",
        see=("arrow-operator", "designated-initializer", "struct-padding", "typedef", "pass-by-value"),
        priority=55,
        aka=("structure", "structs", "member", "members", "field", "struct member", "dot operator", "member access", "record", "struct copy", "struct type", "object", "data structure", "struct pointer"),
        detect=(r"\bstruct\b",),
        rules=(
            r"Access a member with a dot: p.x. Through a pointer use p->x.",
            r"Assignment b = a copies every member (even an array inside); passing a struct to a function copies it too.",
            r"Structs cannot be compared with ==: compare member by member.",
            r"A struct may be larger than the sum of its members because of padding.",
        ),
        example=r"""
            struct Point { int x; int y; };
            struct Point a = {3, 4};
            struct Point b = a;
            b.x = 99;
            printf("%d %d %d\n", a.x, b.x, b.y);
        """,
        out=r"3 99 4",
    ),
    *c(
        "arrow-operator",
        "Arrow operator",
        "p->x reaches the member x of the struct that the pointer p points at. It is shorthand for (*p).x.",
        see=("struct", "pointer", "dereference", "pass-by-value"),
        priority=60,
        aka=("->", "arrow", "member through pointer", "pointer member access", "struct pointer access", "-> operator", "arrow notation"),
        detect=(r"\w[ \t]*->[ \t]*\w",),
        rules=(
            r"Use . on a struct and -> on a pointer to a struct; using the wrong one is a compile error.",
            r"-> binds tighter than the unary *: *p->x means *(p->x).",
            r"Passing a pointer to a struct lets a function change the caller's struct, and avoids copying a big one.",
        ),
        example=r"""
            struct Point { int x; int y; };
            struct Point pt = {1, 2};
            struct Point *p = &pt;
            p->x = 10;
            (*p).y += 5;
            printf("%d %d\n", pt.x, p->y);
        """,
        out=r"10 7",
    ),
    *c(
        "designated-initializer",
        "Designated initializer",
        "An initialiser that names what it sets: { .y = 5 } for a struct member, { [3] = 7 } for an array element. Anything not named becomes zero.",
        see=("initialization", "struct", "array", "compound-literal"),
        priority=55,
        aka=("designated initialiser", ".x =", "named initializer", "designated init", "initialiser by name", "named member initialization"),
        detect=(r"\{[^{}\n]{0,40}\.[A-Za-z_]\w*[ \t]*=|\[[ \t]*\d+[ \t]*\][ \t]*=[ \t]*\d",),
        rules=(
            r"struct Point p = { .z = 3, .x = 1 }; sets x and z and zeroes y; the order does not matter.",
            r"int a[] = { [3] = 7, [1] = 2 }; has 4 elements (the largest index plus one) and the others are 0.",
            r"Available since C99; C++ restricts them.",
        ),
        example=r"""
            struct Point { int x; int y; int z; };
            struct Point p = { .z = 3, .x = 1 };
            int a[] = { [3] = 7, [1] = 2 };
            printf("%d %d %d | %d %d\n", p.x, p.y, p.z, (int)(sizeof a / sizeof a[0]), a[3]);
        """,
        out=r"1 0 3 | 4 7",
    ),
    *c(
        "compound-literal",
        "Compound literal",
        "An unnamed value written in place with a type in brackets and a brace list: (struct Point){1, 2} or (int[]){4, 5, 6}.",
        see=("struct", "designated-initializer", "array", "function-pointer"),
        priority=55,
        aka=("compound literals", "(struct)", "anonymous struct", "temporary struct", "inline struct", "unnamed value"),
        detect=(r"\(\s*(?:struct\s+\w+|int|char|double|float|long)\s*(?:\[\s*\d*\s*\])?\s*\)\s*\{",),
        rules=(
            r"It lives until the end of the enclosing block, and can be changed (unless declared const).",
            r"Handy for passing a temporary struct or array to a function: f((struct Point){1, 2}).",
            r"A C99 feature; it is not the same as a cast.",
        ),
        example=r"""
            struct Point { int x; int y; };
            struct Point p = (struct Point){ 5, 6 };
            int *arr = (int[]){ 4, 5, 6 };
            printf("%d %d %d\n", p.y, arr[2], (int)(sizeof((int[]){1, 2, 3}) / sizeof(int)));
        """,
        out=r"6 6 3",
    ),
    *c(
        "struct-padding",
        "Struct padding",
        "Unused bytes the compiler leaves between members (and at the end) so each member sits at an address it prefers. A struct can be bigger than its members added up.",
        see=("struct", "sizeof", "memcmp", "union"),
        priority=50,
        aka=("padding bytes", "alignment", "struct alignment", "offsetof", "struct size", "memory layout", "alignment padding", "member order"),
        detect=(r"\boffsetof\b|\balignof\b|\b_Alignof\b",),
        rules=(
            r"struct { char c; int n; } is usually 8 bytes: c, 3 bytes of padding, then n.",
            r"Ordering members from largest to smallest wastes least space; sizeof tells the truth, and offsetof (in <stddef.h>) gives a member's position.",
            r"Do not compare or hash a struct with memcmp: the padding bytes can hold anything.",
        ),
        example=r"""
            struct A { char c; int n; };
            struct B { int n; char c; char d; };
            printf("%d %d\n", (int)sizeof(struct A), (int)sizeof(struct B));
            printf("%d\n", (int)offsetof(struct A, n));
        """,
        out=r"""8 8
4""",
    ),
    *c(
        "union",
        "Union",
        "Like a struct, but all members share the same memory, so a union is as big as its biggest member and holds one value at a time.",
        see=("struct", "enum", "struct-padding", "sizeof"),
        priority=55,
        aka=("unions", "tagged union", "variant", "shared memory", "type punning", "type-punning"),
        detect=(r"\bunion\b",),
        rules=(
            r"Writing one member overwrites the others: the bytes are reinterpreted if you read a different member.",
            r"sizeof(union) is at least the size of its largest member.",
            r"Keep track of which member is valid (often with an enum tag next to the union).",
        ),
        example=r"""
            union U { int i; float f; };
            union U u;
            u.i = 5;
            u.f = 1.5f;
            printf("%d %.1f\n", (int)sizeof(union U), u.f);
            printf("%d\n", u.i == 5);
        """,
        out=r"""4 1.5
0""",
    ),
    *c(
        "enum",
        "Enum",
        "A type with a few named integer constants: enum Color { RED, GREEN, BLUE };. The names are numbers starting at 0 unless you give values.",
        see=("typedef", "switch", "constant", "union"),
        priority=55,
        aka=("enumeration", "enumerations", "enums", "named constants", "enumerator", "enum constant", "enumerated type"),
        detect=(r"\benum\b",),
        rules=(
            r"enum Color { RED, GREEN = 5, BLUE }; makes RED 0, GREEN 5 and BLUE 6: each name continues from the previous one.",
            r"The names are plain ints and live in the surrounding scope, so two enums cannot reuse a name.",
            r"C does not check values: any int can be stored in an enum variable.",
            r"Enums pair well with switch (good compilers warn about a missing case).",
        ),
        example=r"""
            enum Color { RED, GREEN = 5, BLUE };
            enum Color c = BLUE;
            printf("%d %d %d\n", RED, GREEN, c);
            printf("%d\n", c == 6);
        """,
        out=r"""0 5 6
1""",
    ),
    *c(
        "typedef",
        "typedef",
        "Gives a new name to an existing type: typedef unsigned char byte; lets you write byte instead of unsigned char.",
        see=("struct", "enum", "fixed-width-integer", "function-pointer"),
        priority=55,
        aka=("type alias", "alias", "type definition", "typedef struct", "type name", "new type name"),
        detect=(r"\btypedef\b",),
        rules=(
            r"It makes an alias, not a new type: byte and unsigned char are interchangeable.",
            r"typedef struct { int x, y; } Point; lets you write Point p; without the word struct.",
            r"The new name goes where the variable name would: typedef int (*Op)(int, int); names a function-pointer type.",
        ),
        example=r"""
            typedef unsigned char byte;
            typedef struct { int x, y; } Point;
            byte b = 200;
            Point p = {1, 2};
            printf("%d %d %d\n", b, p.x + p.y, (int)sizeof(byte));
        """,
        out=r"200 3 1",
    ),
    *c(
        "function-pointer",
        "Function pointer",
        "A variable that holds the address of a function, so the function can be chosen or passed around: int (*op)(int, int) = add; then op(3, 4) calls add.",
        see=("callback", "typedef", "qsort", "function"),
        priority=60,
        aka=("function pointers", "pointer to function", "fn pointer", "function address", "int (*", "(*f)", "pointer to a function", "dispatch table", "jump table"),
        detect=(r"\([ \t]*\*[ \t]*\w+[ \t]*\)[ \t]*\(",),
        rules=(
            r"The brackets matter: int (*op)(int, int) is a pointer to a function; int *op(int, int) is a function returning an int pointer.",
            r"A function's name decays to its address, so op = add; and op = &add; are the same; calling op(3, 4) and (*op)(3, 4) are the same.",
            r"The function's parameter and return types must match the pointer's type.",
            r"A typedef makes them readable: typedef int (*Op)(int, int);",
        ),
        example=r"""
            static int add(int a, int b) { return a + b; }
            static int mul(int a, int b) { return a * b; }
            int main(void) {
                int (*op)(int, int) = add;
                printf("%d ", op(3, 4));
                op = mul;
                printf("%d\n", op(3, 4));
                return 0;
            }
        """,
        out=r"7 12",
    ),
    *c(
        "callback",
        "Callback",
        "A function handed to another function so that function can call it later. In C it is passed as a function pointer, as qsort does with its compare function.",
        see=("function-pointer", "qsort", "function", "parameter"),
        priority=45,
        aka=("callbacks", "call back", "handler", "event handler", "comparator", "higher-order function", "function parameter", "pass a function"),
        rules=(
            r"The receiving function declares a parameter of a function-pointer type: int apply(int x, int (*f)(int)).",
            r"The caller passes just the name: apply(21, twice) - no brackets, which would call it.",
            r"C has no closures: a callback cannot capture local variables, so APIs add a void * argument for your data.",
        ),
        example=r"""
            static int apply(int x, int (*f)(int)) { return f(x); }
            static int twice(int v) { return v * 2; }
            int main(void) {
                printf("%d\n", apply(21, twice));
                return 0;
            }
        """,
        out=r"42",
    ),
    *c(
        "qsort",
        "qsort",
        "The library function that sorts an array of anything: qsort(base, count, size, compare). You supply compare, a callback that says which of two elements comes first.",
        see=("callback", "function-pointer", "void-pointer", "array"),
        priority=55,
        aka=("sorting", "sort", "sort an array", "comparator", "compare function", "bsearch", "sorting algorithm", "bubble sort", "ordering"),
        detect=(r"\b(?:qsort|bsearch)\b",),
        rules=(
            r"The compare function takes two const void * and returns negative, zero or positive; cast them to the real type inside.",
            r"Do not return a - b: it can overflow. Return (a > b) - (a < b).",
            r"The size argument is the size of ONE element (sizeof a[0]); qsort is not guaranteed stable.",
        ),
        example=r"""
            #include <stdlib.h>
            static int cmp(const void *a, const void *b) {
                int x = *(const int *)a, y = *(const int *)b;
                return (x > y) - (x < y);
            }
            int main(void) {
                int a[5] = {3, 1, 4, 1, 5};
                qsort(a, 5, sizeof a[0], cmp);
                printf("%d %d %d %d %d\n", a[0], a[1], a[2], a[3], a[4]);
                return 0;
            }
        """,
        out=r"1 1 3 4 5",
    ),
    *c(
        "swap",
        "Swap",
        "Exchanging the values of two variables. In C a function can only do it through pointers, because it would otherwise swap copies.",
        see=("pass-by-value", "pointer", "dereference", "address-of"),
        priority=35,
        aka=("swapping", "exchange", "swap two variables", "temp variable", "temporary variable", "swap function"),
        rules=(
            r"Use a temporary: t = *a; *a = *b; *b = t;",
            r"Call it with addresses: swap(&x, &y).",
            r"A swap(int a, int b) cannot work: it only changes its own copies.",
        ),
        example=r"""
            static void swap(int *a, int *b) { int t = *a; *a = *b; *b = t; }
            int main(void) {
                int x = 1, y = 2;
                swap(&x, &y);
                printf("%d %d\n", x, y);
                return 0;
            }
        """,
        out=r"2 1",
    ),
    *c(
        "segmentation-fault",
        "Segmentation fault",
        "A crash the operating system causes when the program touches memory it may not use, such as dereferencing NULL or a wild pointer. It is a symptom of undefined behaviour, not a message saying which line is wrong.",
        see=("null-pointer", "undefined-behavior", "dangling-pointer", "buffer-overflow"),
        priority=45,
        aka=("segfault", "seg fault", "sigsegv", "access violation", "crash", "core dumped", "stack overflow", "memory error", "bus error"),
        rules=(
            r"Common causes: dereferencing NULL, a freed or uninitialised pointer, an index far outside an array, runaway recursion.",
            r"It is not guaranteed: many wrong accesses silently corrupt data instead of crashing.",
            r"Find the line with a debugger or by building with -fsanitize=address -g.",
        ),
        example=r"""
            int *p = NULL;
            if (p != NULL) printf("%d\n", *p);
            else printf("pointer is NULL, not dereferenced\n");
        """,
        out=r"pointer is NULL, not dereferenced",
    ),
]
