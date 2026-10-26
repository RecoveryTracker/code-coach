"""C words, part 4: control flow, functions, scope and the preprocessor - loops, break/continue, switch, functions,
pass by value, recursion, the stack, scope, static and global variables, headers, macros and conditional compilation.

Examples are the BODY of `main` unless they mention `main(` (then a complete program); see terms_c_core.py."""

from __future__ import annotations

from .entry import Entry, c

TERMS: list[Entry] = [
    *c(
        "loop",
        "Loop",
        "Code that repeats. C has three: for, while and do...while. break leaves a loop early and continue skips to its next round.",
        see=("for-loop", "while-loop", "do-while-loop", "break", "continue", "off-by-one"),
        priority=30,
        aka=("loops", "looping", "repeat", "repetition", "repeating", "iterate", "loop construct", "infinite loop"),
        detect=(r"\b(?:for|while|do)\b[ \t]*[({]",),
        rules=(
            r"for suits a counted repeat, while a repeat until something happens, do...while one that must run at least once.",
            r"for (;;) and while (1) repeat for ever until a break, return or exit.",
            r"The body can be one statement without braces, but always use braces: adding a second line later then goes wrong.",
        ),
        example=r"""
            int sum = 0;
            for (int i = 1; i <= 4; i++) sum += i;
            printf("%d\n", sum);
        """,
        out=r"10",
    ),
    *c(
        "for-loop",
        "for loop",
        "for (start; test; step) body - runs start once, then repeats: test, body, step, until the test is false.",
        see=("loop", "while-loop", "comma-operator", "off-by-one", "scope"),
        priority=45,
        aka=("for", "for loops", "counting loop", "counter loop", "for statement", "for each", "foreach", "counted loop"),
        detect=(r"\bfor[ \t]*\(",),
        rules=(
            r"The test runs BEFORE every round, so a false test the first time means the body never runs.",
            r"Each of the three parts may be empty: for (;;) is an endless loop.",
            r"A variable declared in the start part (for (int i = 0; ...)) exists only inside the loop (C99).",
            r"After the loop ends normally the counter holds the first value that failed the test.",
        ),
        example=r"""
            int i;
            for (i = 0; i < 3; i++) printf("%d ", i);
            printf("| %d\n", i);
        """,
        out=r"0 1 2 | 3",
    ),
    *c(
        "while-loop",
        "while loop",
        "while (test) body - checks the test first and runs the body as long as it stays true; if the test is false at once, the body never runs.",
        see=("loop", "for-loop", "do-while-loop", "break"),
        priority=45,
        aka=("while", "while loops", "while statement", "conditional loop", "sentinel", "loop condition", "loop until"),
        detect=(r"\bwhile[ \t]*\(",),
        rules=(
            r"Something inside must change the test, or the loop never ends.",
            r"The test is 0-or-not: while (n) runs until n becomes 0.",
            r"A semicolon straight after while (...); is an empty body: the loop spins and the block below runs once after it.",
        ),
        example=r"""
            int n = 6, steps = 0;
            while (n != 1) {
                n = (n % 2 == 0) ? n / 2 : 3 * n + 1;
                steps++;
            }
            printf("%d\n", steps);
        """,
        out=r"8",
    ),
    *c(
        "do-while-loop",
        "do...while loop",
        "do body while (test); - runs the body first and checks the test after, so the body always runs at least once.",
        see=("while-loop", "loop", "for-loop", "break"),
        priority=50,
        aka=("do while", "do-while", "do..while", "do while loop", "post-test loop", "repeat until"),
        detect=(r"\bdo[ \t\n]*\{|\}[ \t]*while[ \t]*\([^)\n]{0,60}\)[ \t]*;",),
        rules=(
            r"The semicolon after while (...) is required.",
            r"Use it when the first round must happen before there is anything to test (read, then check).",
            r"continue jumps to the test, not to the top of the body.",
        ),
        example=r"""
            int n = 10;
            do { printf("%d ", n); n++; } while (n < 3);
            printf("| %d\n", n);
        """,
        out=r"10 | 11",
    ),
    *c(
        "break",
        "break",
        "break leaves the innermost loop or switch at once and carries on after it.",
        see=("continue", "loop", "switch", "nested-loop"),
        priority=50,
        aka=("break statement", "exit loop", "leave loop", "stop loop", "early exit", "break out"),
        detect=(r"\bbreak[ \t]*;",),
        rules=(
            r"It leaves only ONE level: in nested loops the outer loop carries on.",
            r"In a switch it ends the case (without it execution falls into the next case).",
            r"After a for loop that was broken, the counter keeps its value from that round.",
        ),
        example=r"""
            int i;
            for (i = 0; i < 10; i++) {
                if (i * i > 20) break;
            }
            printf("%d\n", i);
        """,
        out=r"5",
    ),
    *c(
        "continue",
        "continue",
        "continue skips the rest of this round of the loop. A for loop then runs its step and test; a while loop goes straight to its test.",
        see=("break", "loop", "for-loop", "while-loop"),
        priority=50,
        aka=("continue statement", "skip iteration", "skip", "next iteration", "skip a round"),
        detect=(r"\bcontinue[ \t]*;",),
        rules=(
            r"In a for loop the step (i++) still happens.",
            r"Trap: in a while loop, a continue placed before the i++ skips the increment and may loop for ever.",
            r"It affects only the innermost loop.",
        ),
        example=r"""
            int sum = 0;
            for (int i = 1; i <= 6; i++) {
                if (i % 2 == 0) continue;
                sum += i;
            }
            printf("%d\n", sum);
        """,
        out=r"9",
    ),
    *c(
        "off-by-one",
        "Off-by-one error",
        "Being wrong by exactly one: a loop that runs one time too many or too few, or an index one past the end. The usual cause is <= where < belongs.",
        see=("index", "for-loop", "buffer-overflow", "null-terminator"),
        priority=40,
        aka=("off by one", "fencepost", "fence post", "fencepost error", "one too many", "boundary error", "obo", "boundary"),
        rules=(
            r"n elements have indexes 0 to n - 1: for (i = 0; i <= n; i++) reads one past the end.",
            r"The count of items from a to b inclusive is b - a + 1.",
            r"A string of n characters needs n + 1 bytes for the terminator.",
        ),
        example=r"""
            int count = 0;
            for (int i = 0; i < 5; i++) count++;
            int count2 = 0;
            for (int i = 0; i <= 5; i++) count2++;
            printf("%d %d\n", count, count2);
        """,
        out=r"5 6",
    ),
    *c(
        "iteration",
        "Iteration",
        "One pass through the body of a loop. A loop that runs 4 times has 4 iterations.",
        see=("loop", "for-loop", "off-by-one", "nested-loop"),
        priority=25,
        aka=("iterations", "iterate", "iterating", "round", "pass", "each time", "loop count", "how many times", "loop counter", "counter"),
        rules=(
            r"for (i = a; i < b; i += s) runs ceil((b - a) / s) times when b > a.",
            r"With i < n and a step of 1 starting from 0, it runs n times.",
            r"A test that is false at the start means zero iterations.",
        ),
        example=r"""
            int count = 0;
            for (int i = 2; i < 12; i += 3) count++;
            printf("%d\n", count);
        """,
        out=r"4",
    ),
    *c(
        "nested-loop",
        "Nested loop",
        "A loop inside another loop. The inner one runs completely for each iteration of the outer one.",
        see=("loop", "break", "multidimensional-array", "iteration"),
        priority=45,
        aka=("nested loops", "loop inside a loop", "inner loop", "outer loop", "double loop", "nesting", "nested for"),
        detect=(r"\bfor[ \t]*\([^)\n]{0,60}\)[ \t\n]*\{?[ \t\n]*for[ \t]*\(",),
        rules=(
            r"Two independent loops of a and b rounds give a * b runs of the inner body.",
            r"break and continue affect only the inner loop.",
            r"If the inner loop starts from the outer counter (j = i), the total is a triangle: 3 + 2 + 1 for n = 3.",
        ),
        example=r"""
            int count = 0;
            for (int i = 0; i < 3; i++)
                for (int j = i; j < 3; j++)
                    count++;
            printf("%d\n", count);
        """,
        out=r"6",
    ),
    *c(
        "switch",
        "switch",
        "Compares an integer or character against constant case labels and jumps to the match. Without a break at the end of a case, the next case runs too.",
        see=("fallthrough", "break", "enum", "condition"),
        priority=55,
        aka=("switch statement", "case", "case label", "default", "switch case", "switch-case", "multiway branch"),
        detect=(r"\bswitch[ \t]*\(",),
        rules=(
            r"It works on integers, characters and enums only - not strings or floating-point numbers.",
            r"Each case label must be a constant; default catches everything else (and may sit anywhere).",
            r"break ends a case. Forgetting it is the classic bug: execution falls through into the next case.",
            r"Declare variables inside braces { } if a case needs them.",
        ),
        example=r"""
            int n = 2;
            switch (n) {
                case 1: printf("one\n"); break;
                case 2: printf("two\n");
                case 3: printf("three\n"); break;
                default: printf("other\n");
            }
        """,
        out=r"""two
three""",
    ),
    *c(
        "fallthrough",
        "Fallthrough",
        "When a switch case has no break, execution carries on into the next case's code instead of leaving the switch.",
        see=("switch", "break", "condition", "compiler-warning"),
        priority=45,
        aka=("fall through", "fall-through", "falls through", "missing break", "case fallthrough"),
        rules=(
            r"It is sometimes wanted: case 1: case 2: shares one body, or a total adds up across cases.",
            r"Compilers warn about accidental ones (-Wimplicit-fallthrough); say it is intended with a comment or [[fallthrough]] in C23.",
            r"Only the code from the matching case DOWN runs, never the cases above it.",
        ),
        example=r"""
            int grade = 3, points = 0;
            switch (grade) {
                case 3: points += 3;
                case 2: points += 2;
                case 1: points += 1; break;
                case 0: points = 100;
            }
            printf("%d\n", points);
        """,
        out=r"6",
    ),
    *c(
        "condition",
        "Condition",
        "An expression that decides which way the program goes, in if, while, for and ?:. Zero is false and any other value is true.",
        see=("boolean", "comparison", "short-circuit", "ternary", "switch"),
        priority=30,
        aka=("conditions", "if", "if statement", "else", "if else", "else if", "conditional", "branch", "branching", "if-else", "decision", "test", "dangling else"),
        detect=(r"\bif[ \t]*\(|\belse\b",),
        rules=(
            r"else belongs to the NEAREST if, whatever the indentation says (the dangling else).",
            r"Always use braces: if (x) a(); b(); runs b() every time.",
            r"A stray semicolon, if (x); , makes an empty body.",
            r"Chains of else if are tested in order; the first true one wins and the rest are skipped.",
        ),
        example=r"""
            int x = 7;
            if (x > 10) printf("big\n");
            else if (x > 5) printf("medium\n");
            else printf("small\n");
            if (x) printf("nonzero is true\n");
        """,
        out=r"""medium
nonzero is true""",
    ),
    *c(
        "function",
        "Function",
        "A named block of code that takes values in (parameters), may give one value back (return) and is run by calling its name. Every C function states its return type; void means none.",
        see=("parameter", "argument", "return", "function-declaration", "pass-by-value"),
        priority=30,
        aka=("functions", "method", "procedure", "subroutine", "routine", "function definition", "define a function", "function call", "call", "function name", "helper function"),
        detect=(r"^[ \t]*(?:static[ \t]+)?(?:int|void|char|double|float|long|unsigned|size_t|u?int\d+_t)[ \t]+\**[A-Za-z_]\w*[ \t]*\([^;{]*\)[ \t\n]*\{",),
        rules=(
            r"A function must be declared (or defined) before it is called.",
            r"C has no overloading: one name, one function. At most one value is returned (use a struct or pointers for more).",
            r"Falling off the end of a non-void function and using its result is undefined behaviour (main is the exception).",
            r"Arguments are copied into the parameters (see pass by value).",
        ),
        example=r"""
            static int square(int n) { return n * n; }
            int main(void) {
                printf("%d\n", square(7));
                return 0;
            }
        """,
        out=r"49",
    ),
    *c(
        "parameter",
        "Parameter",
        "A variable in a function's definition that receives a value when the function is called: in int add(int a, int b), a and b are parameters.",
        see=("argument", "function", "pass-by-value", "array-decay"),
        priority=25,
        aka=("parameters", "formal parameter", "formal", "param", "function parameter", "function arguments", "args", "parameter list"),
        rules=(
            r"Each parameter is a local copy: assigning to it never changes the caller's variable.",
            r"An array parameter is really a pointer (array decay), so pass the length too.",
            r"int f() leaves the parameters unspecified in C; write int f(void) for none.",
        ),
        example=r"""
            static double half(double x) { return x / 2; }
            int main(void) {
                printf("%.1f\n", half(5));
                return 0;
            }
        """,
        out=r"2.5",
    ),
    *c(
        "argument",
        "Argument",
        "The actual value you put between the brackets when you call a function: in add(2, 3), 2 and 3 are the arguments. Each is converted to the parameter's type.",
        see=("parameter", "function", "evaluation-order", "pass-by-value"),
        priority=25,
        aka=("arguments", "actual argument", "call arguments", "argc", "argv", "passing", "pass", "call by value"),
        rules=(
            r"The number and types must match the declaration; a mismatch is a compile error (with a prototype).",
            r"The order in which the arguments are worked out is not specified: f(i++, i++) is a bug.",
            r"An int passed where a double is expected is converted: half(5) passes 5.0.",
        ),
        example=r"""
            static int add(int a, int b) { return a + b; }
            int main(void) {
                int x = 2;
                printf("%d %d\n", add(x, 3), add(add(1, 2), x));
                return 0;
            }
        """,
        out=r"5 5",
    ),
    *c(
        "return",
        "return",
        "return value; ends the function at once and hands value back to the caller. In main, the value is the program's exit status.",
        see=("function", "main-function", "void", "recursion"),
        priority=35,
        aka=("return value", "returns", "return statement", "returning", "return type", "exit status", "give back"),
        detect=(r"\breturn\b",),
        rules=(
            r"The value is converted to the function's return type.",
            r"A function may have several returns; the first reached ends it.",
            r"Return a pointer to a local variable and you have a dangling pointer.",
            r"To give back more than one thing, return a struct or pass pointers.",
        ),
        example=r"""
            static int sign(int n) {
                if (n < 0) return -1;
                if (n > 0) return 1;
                return 0;
            }
            int main(void) {
                printf("%d %d %d\n", sign(-9), sign(0), sign(4));
                return 0;
            }
        """,
        out=r"-1 0 1",
    ),
    *c(
        "pass-by-value",
        "Pass by value",
        "C always copies the arguments into the parameters, so a function cannot change the caller's variables - unless it is given their addresses (pointers).",
        see=("pointer", "swap", "array-decay", "parameter"),
        priority=50,
        aka=("by value", "call by value", "pass by reference", "by reference", "pass by pointer", "copy of the argument", "value semantics", "call-by-value", "pass-by-reference", "copies"),
        rules=(
            r"void bump(int n) { n++; } leaves the caller's variable alone; void bump(int *n) { (*n)++; } changes it when called bump(&x).",
            r"A whole struct is copied too (all its members); a pointer is copied, but the thing it points at is shared.",
            r"Arrays behave as if passed by reference only because the pointer is what gets copied.",
            r"Reassigning a pointer parameter does not change the caller's pointer; use a pointer to pointer for that.",
        ),
        example=r"""
            static void bump(int n) { n++; }
            static void bump_ptr(int *n) { (*n)++; }
            int main(void) {
                int x = 1;
                bump(x);
                printf("%d ", x);
                bump_ptr(&x);
                printf("%d\n", x);
                return 0;
            }
        """,
        out=r"1 2",
    ),
    *c(
        "function-declaration",
        "Function declaration",
        "A line that names a function's return type and parameters without its body (int twice(int);). It lets code call a function that is defined later or in another file.",
        see=("function", "header", "extern", "void"),
        priority=45,
        aka=("prototype", "function prototype", "forward declaration", "declaration", "declare a function", "signature", "function signature", "implicit declaration"),
        detect=(r"^[ \t]*(?:extern[ \t]+)?(?:int|void|char|double|float|long|unsigned|size_t)[ \t]+\**[A-Za-z_]\w*[ \t]*\([^{};]*\)[ \t]*;",),
        rules=(
            r"Headers (.h files) are mostly lists of declarations; the definitions live in .c files.",
            r"Calling a function with no declaration in sight is an error in modern C (implicit declaration).",
            r"int f(); is an old-style declaration with unspecified parameters; int f(void); means none.",
        ),
        example=r"""
            int twice(int);
            int main(void) {
                printf("%d\n", twice(4));
                return 0;
            }
            int twice(int n) { return 2 * n; }
        """,
        out=r"8",
    ),
    *c(
        "void",
        "void",
        "The type with no values. A function returning void gives nothing back; (void) in a parameter list means no parameters; void * is a pointer to unknown type.",
        see=("function", "return", "void-pointer", "main-function"),
        priority=35,
        aka=("void function", "void return", "returns nothing", "no return value", "void type"),
        detect=(r"\bvoid\b",),
        rules=(
            r"You cannot declare a variable of type void or use the result of a void function.",
            r"(void)expr; explicitly throws a value away (used to silence unused-value warnings).",
            r"A void function may end with a bare return; or just reach its closing brace.",
        ),
        example=r"""
            static void hello(void) { printf("hi\n"); }
            int main(void) {
                hello();
                return 0;
            }
        """,
        out=r"hi",
    ),
    *c(
        "main-function",
        "main",
        "The function where a C program starts: int main(void), or int main(int argc, char *argv[]) to receive command-line arguments. Its return value is the exit status; 0 means success.",
        see=("return", "function", "void", "header"),
        priority=40,
        aka=("main", "entry point", "main function", "program start", "exit code", "exit status", "argc", "argv", "command line arguments", "exit", "start of the program"),
        detect=(r"\bmain[ \t]*\(",),
        rules=(
            r"Return 0 (or EXIT_SUCCESS) for success and a non-zero value (EXIT_FAILURE) for failure; the shell and build tools read it.",
            r"Reaching the closing brace of main counts as return 0 (C99 and later), the only function with that rule.",
            r"argv[0] is the program's name and argv[argc] is NULL; exit(n) ends the program from anywhere.",
        ),
        example=r"""
            int main(void) {
                printf("done\n");
                return 0;
            }
        """,
        out=r"done",
    ),
    *c(
        "recursion",
        "Recursion",
        "A function that calls itself. Each call works on a smaller version of the problem until it reaches a base case, which returns without calling again.",
        see=("call-stack", "function", "return", "condition"),
        priority=50,
        aka=("recursive", "recursive function", "base case", "recurse", "calls itself", "self-call", "factorial", "fibonacci", "stack overflow"),
        detect=(r"\b(\w+)[ \t]*\([^;{}]{0,60}\)[ \t\n]*\{[^{}]{0,200}\b\1[ \t]*\(",),
        rules=(
            r"Without a base case (or with one that is never reached) it recurses until the stack overflows and the program crashes.",
            r"Every call has its own parameters and local variables; the caller's are untouched.",
            r"The work after the recursive call happens as the calls come back (see the call stack).",
        ),
        example=r"""
            static int fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }
            int main(void) {
                printf("%d %d\n", fact(5), fact(1));
                return 0;
            }
        """,
        out=r"120 1",
    ),
    *c(
        "call-stack",
        "Call stack",
        "The block of memory where each function call keeps its parameters and local variables. A call adds a frame on top; a return removes it.",
        see=("recursion", "storage-duration", "local-variable", "dangling-pointer"),
        priority=40,
        aka=("stack", "stack frame", "frame", "stack memory", "stack overflow", "call stack frame", "the stack", "stack and heap"),
        rules=(
            r"It is small (typically 1-8 MB), so very deep recursion or huge local arrays crash with a stack overflow.",
            r"Frames vanish on return: a pointer to a local variable is dangling afterwards.",
            r"Last in, first out: the function called last finishes first.",
        ),
        example=r"""
            static void down(int n) {
                if (n == 0) { printf("bottom\n"); return; }
                printf("%d ", n);
                down(n - 1);
                printf("%d ", n);
            }
            int main(void) {
                down(2);
                printf("\n");
                return 0;
            }
        """,
        out=r"""2 1 bottom
1 2""",
    ),
    *c(
        "scope",
        "Scope",
        "The part of the code where a name can be used. A variable declared inside braces { } is visible from its declaration to the closing brace; one outside every function is visible to the rest of the file.",
        see=("local-variable", "global-variable", "shadowing", "storage-duration"),
        priority=40,
        aka=("block scope", "file scope", "visibility", "lifetime", "variable scope", "scoping", "where a variable is visible", "block", "local scope", "curly braces", "braces"),
        rules=(
            r"An inner block can see the outer block's variables, not the other way round.",
            r"A variable declared in a for header lives only inside that loop (C99).",
            r"Using a name outside its scope is a compile error; scope is about where a name is visible, lifetime about when its memory exists.",
        ),
        example=r"""
            int x = 1;
            {
                int y = 2;
                x = x + y;
            }
            printf("%d\n", x);
        """,
        out=r"3",
    ),
    *c(
        "local-variable",
        "Local variable",
        "A variable declared inside a function or block. It is created when the code runs, holds garbage until you set it, and disappears when the block ends.",
        see=("scope", "static-variable", "call-stack", "initialization"),
        priority=40,
        aka=("local", "locals", "automatic variable", "auto variable", "local variables", "auto", "stack variable", "function variable"),
        rules=(
            r"Each call (and each recursive call) gets fresh locals, so they do not remember anything between calls.",
            r"They are not initialised automatically: int n; contains garbage, int n = 0; does not.",
            r"Never return or store the address of a local beyond the function.",
        ),
        example=r"""
            static int count(void) { int n = 0; n++; return n; }
            int main(void) {
                count();
                count();
                printf("%d\n", count());
                return 0;
            }
        """,
        out=r"1",
    ),
    *c(
        "global-variable",
        "Global variable",
        "A variable declared outside every function. It lives for the whole run, starts at zero, and every function after the declaration can use it.",
        see=("static-variable", "scope", "extern", "local-variable"),
        priority=40,
        aka=("global", "globals", "global variables", "file-scope variable", "file scope variable", "shared variable", "global state", "global scope"),
        rules=(
            r"It starts at 0 (or NULL) if you give it no value.",
            r"A local variable with the same name hides it (shadowing).",
            r"Without static, other files can reach it with extern; prefer parameters and return values to globals.",
        ),
        example=r"""
            int total = 10;
            static void add(int n) { total += n; }
            int main(void) {
                add(5);
                add(1);
                printf("%d\n", total);
                return 0;
            }
        """,
        out=r"16",
    ),
    *c(
        "static-variable",
        "Static variable",
        "A variable declared with static. Inside a function it keeps its value between calls and is set up only once; at file level it is private to that file.",
        see=("local-variable", "global-variable", "storage-duration", "extern"),
        priority=55,
        aka=("static", "static local", "static keyword", "persistent variable", "remembers its value", "static storage", "static function", "internal linkage"),
        detect=(r"\bstatic\b",),
        rules=(
            r"static int n = 0; inside a function is initialised once, before the program runs, and then keeps its value.",
            r"Its initialiser must be a constant; without one it starts at 0.",
            r"static on a global variable or function means other files cannot see it.",
            r"All calls share the one variable, so it is not safe with threads or recursion without care.",
        ),
        example=r"""
            static int next(void) { static int n = 0; n++; return n; }
            int main(void) {
                next();
                next();
                printf("%d\n", next());
                return 0;
            }
        """,
        out=r"3",
    ),
    *c(
        "storage-duration",
        "Storage duration",
        "How long a variable's memory lasts. Automatic: until its block ends (ordinary locals). Static: the whole run (globals and static variables). Allocated: from malloc until free.",
        see=("static-variable", "local-variable", "dynamic-memory", "scope"),
        priority=40,
        aka=("lifetime", "automatic storage", "static storage duration", "allocated storage", "variable lifetime", "how long a variable lives", "storage class", "auto"),
        rules=(
            r"Automatic variables are uninitialised; static ones start at zero.",
            r"Scope and lifetime differ: a static local is visible only in its function but lives for the whole run.",
            r"Memory from malloc outlives the function that asked for it, and you must free it.",
        ),
        example=r"""
            static int counter(void) {
                int a = 0;
                static int s = 0;
                a++;
                s++;
                return a * 10 + s;
            }
            int main(void) {
                counter();
                counter();
                printf("%d\n", counter());
                return 0;
            }
        """,
        out=r"13",
    ),
    *c(
        "shadowing",
        "Shadowing",
        "Declaring a variable with the same name as one in an outer scope. Inside the inner block the new one hides the old one, which is untouched.",
        see=("scope", "local-variable", "global-variable", "for-loop"),
        priority=45,
        aka=("shadow", "shadowed", "name hiding", "hiding", "variable shadowing", "same name", "hides", "name clash"),
        rules=(
            r"The outer variable keeps its value and is visible again after the inner block ends.",
            r"A local that hides a global makes the global unreachable by that name in that function.",
            r"-Wshadow makes the compiler warn about it.",
            r"A for loop's int i hides an outer i for the loop's duration.",
        ),
        example=r"""
            int x = 1;
            {
                int x = 2;
                printf("%d ", x);
            }
            printf("%d\n", x);
        """,
        out=r"2 1",
    ),
    *c(
        "extern",
        "extern",
        "extern int total; declares that a variable exists but is defined somewhere else (another file, or later in this one). It reserves no memory; the one definition does.",
        see=("global-variable", "function-declaration", "static-variable", "header"),
        priority=50,
        aka=("external", "external variable", "linkage", "external linkage", "declaration vs definition", "definition", "multiple files", "translation unit"),
        detect=(r"\bextern\b",),
        rules=(
            r"A declaration says a name exists; a definition creates it. A program has exactly one definition of each global.",
            r"Functions are extern by default; static makes a function or variable private to its file.",
            r"Put extern declarations in a header so every file sees the same one.",
        ),
        example=r"""
            int shared = 7;
            static void show(void) {
                extern int shared;
                printf("%d\n", shared);
            }
            int main(void) {
                show();
                return 0;
            }
        """,
        out=r"7",
    ),
    *c(
        "header",
        "Header file",
        "A .h file of declarations (functions, types, macros) that #include pastes into your code. printf lives in <stdio.h>, strlen in <string.h>, malloc in <stdlib.h>.",
        see=("preprocessor", "function-declaration", "conditional-compilation", "macro"),
        priority=40,
        aka=("include", "#include", "stdio.h", "header files", "h file", "include file", "include guard", "include guards", "library", "libraries", "import", "stdio"),
        detect=(r"^[ \t]*#[ \t]*include\b",),
        rules=(
            r'''#include <name.h> searches the system folders; #include "name.h" searches your own project first.''',
            r"Using a function without its header is an error (or a dangerous guess) in modern C.",
            r"An include guard (#ifndef X / #define X / ... / #endif) stops a header being pasted twice.",
        ),
        example=r"""
            #include <stdio.h>
            #include <string.h>
            int main(void) {
                printf("%d\n", (int)strlen("header"));
                return 0;
            }
        """,
        out=r"6",
    ),
    *c(
        "preprocessor",
        "Preprocessor",
        "A step that runs before the compiler and handles the lines starting with #: #include pastes a file, #define replaces text, #if keeps or drops code. It works on plain text and knows nothing about types.",
        see=("macro", "header", "conditional-compilation", "stringify"),
        priority=45,
        aka=("preprocessing", "preprocessor directive", "directive", "#define", "cpp", "predefined macro", "__LINE__", "__FILE__"),
        detect=(r"^[ \t]*#[ \t]*(?:define|undef|if|ifdef|ifndef|pragma|error)\b|\b__(?:LINE|FILE|func)__\b",),
        rules=(
            r"A directive occupies one line and needs no semicolon.",
            r"Everything it does happens before compiling; the compiler never sees the macro names.",
            r"Predefined macros: __LINE__ (the line number), __FILE__ (the file name), __func__ (the function name).",
        ),
        example=r"""
            #define SIDES 4
            #define DOUBLE(x) ((x) * 2)
            int main(void) {
                printf("%d %d\n", SIDES, DOUBLE(SIDES + 1));
                printf("%d\n", __LINE__ > 0);
                return 0;
            }
        """,
        out=r"""4 10
1""",
    ),
    *c(
        "macro",
        "Macro",
        "A name defined with #define that the preprocessor replaces with other text before compiling. A function-like macro takes arguments, but it is only text substitution.",
        see=("preprocessor", "constant", "stringify", "side-effect"),
        priority=55,
        aka=("macros", "#define", "define", "function-like macro", "macro definition", "parentheses trap", "macro parentheses", "text substitution", "macro argument", "object-like macro"),
        detect=(r"^[ \t]*#[ \t]*define\b",),
        rules=(
            r"#define BAD(x) x * x makes BAD(1 + 2) into 1 + 2 * 1 + 2, which is 5; wrap every parameter and the whole body: ((x) * (x)).",
            r"A macro argument is pasted wherever it appears, so BAD(i++) increments twice.",
            r"No semicolon at the end of a #define (it would become part of the text).",
            r"Macros have no type and no scope; prefer const variables, enums and static functions when you can.",
        ),
        example=r"""
            #define BAD(x) x * x
            #define GOOD(x) ((x) * (x))
            int main(void) {
                printf("%d %d\n", BAD(1 + 2), GOOD(1 + 2));
                return 0;
            }
        """,
        out=r"5 9",
    ),
    *c(
        "stringify",
        "Stringify and paste",
        "Inside a macro, #x turns the argument into a string literal of its own text, and a ## b glues two pieces of text into one name.",
        see=("macro", "preprocessor", "string-literal", "printf"),
        priority=50,
        aka=("stringification", "token pasting", "##", "# operator", "stringizing", "paste tokens", "stringize", "string of macro argument"),
        detect=(r"#[ \t]*[a-z]\w*[ \t]*\"|\w[ \t]*##[ \t]*\w",),
        rules=(
            r'''#x gives the exact text written for x: SHOW(total * 2) makes "total * 2".''',
            r'''It joins with neighbouring string literals: #x " = %d\n" is one string.''',
            r"a ## b makes one token: VAR(count) can build count_1.",
        ),
        example=r"""
            #define SHOW(x) printf(#x " = %d\n", x)
            int main(void) {
                int total = 12;
                SHOW(total);
                SHOW(total * 2);
                return 0;
            }
        """,
        out=r"""total = 12
total * 2 = 24""",
    ),
    *c(
        "conditional-compilation",
        "Conditional compilation",
        "#if, #ifdef, #ifndef, #else and #endif keep or drop whole pieces of code before compiling, depending on whether a name is defined.",
        see=("preprocessor", "macro", "header", "constant"),
        priority=50,
        aka=("#ifdef", "#ifndef", "#if", "#endif", "ifdef", "ifndef", "include guard", "debug flag", "conditional", "#else", "feature flag", "platform check"),
        detect=(r"^[ \t]*#[ \t]*(?:ifdef|ifndef|if|elif|else|endif)\b",),
        rules=(
            r"#ifdef NAME asks whether NAME is defined at all; #if NAME asks whether its value is non-zero.",
            r"The dropped code is never compiled, so it can mention things that do not exist on this machine.",
            r"Every #if needs its #endif. Include guards are the #ifndef / #define / #endif trio around a header.",
        ),
        example=r"""
            #define DEBUG 1
            int main(void) {
            #if DEBUG
                printf("debug on\n");
            #else
                printf("debug off\n");
            #endif
            #ifndef MISSING
                printf("MISSING is not defined\n");
            #endif
                return 0;
            }
        """,
        out=r"""debug on
MISSING is not defined""",
    ),
    *c(
        "compiler-warning",
        "Compiler warning",
        "A message from the compiler about code that is legal but probably wrong. The program still builds, but nearly every warning is a real bug; build with -Wall -Wextra and fix them all.",
        see=("undefined-behavior", "condition", "assignment", "fallthrough"),
        priority=35,
        aka=("warning", "warnings", "-Wall", "compiler error", "compile error", "compilation error", "syntax error", "compiler", "gcc", "clang", "build error", "error message"),
        rules=(
            r"-Wall -Wextra -pedantic turn on the useful ones; -Werror makes them errors.",
            r"Typical: assignment in a condition (if (x = 5)), unused variables, missing return, format mismatches in printf.",
            r"Extra brackets say 'I meant it': if ((y = x)) silences the assignment warning.",
        ),
        example=r"""
            int x = 5, y = 0;
            if ((y = x)) printf("assigned %d\n", y);
        """,
        out=r"assigned 5",
    ),
]
