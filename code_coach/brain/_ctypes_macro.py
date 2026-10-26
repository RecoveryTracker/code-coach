"""C types and preprocessor pack, part 1: Macro Trap (`ct_macro`).

Every program is COMPLETE (macros need `#define` lines before `main`, and a `#define` inside a batch body would leak
into the next item), so each is its own translation unit in the oracle. The answers are worked out with a hand-made
preprocessor and expression evaluator (`_ctypes_model.expand` / `ceval`): the arguments are pasted in as TEXT, then the
precedence rules of C are applied to what is left. No template relies on a macro argument with a side effect being
evaluated in an unspecified order: the double evaluation traps put the argument in the condition of `?:`, which is
sequenced.
"""

from __future__ import annotations

from string import Template

from ._c_model import C
from ._ccore_numbers import T
from ._ccore_text import PF
from ._ctypes_model import macro_text, macro_value
from ._model import Maker


def _sub(p: dict, text: str) -> str:
    return Template(text).substitute(p)


def _sentence(why: str) -> str:
    """A `why` that starts with the expansion written out in letters ("a+1*a+1: the * goes first.") loses that start (the
    explanation shows the real expansion) and starts with a capital."""
    head, sep, tail = why.rpartition(": ")
    if sep and not any(len(w) >= 4 for w in head.replace("(", " ").replace(")", " ").split()) and any(c in head for c in "+-*/%<>=!?"):
        return tail[:1].upper() + tail[1:]
    return why


def MC(defs: list[str], vars_: list[tuple[str, str]], expr: str, why: str, fmt: str = "%d") -> Maker:
    """A macro item: the `#define` lines, `int name = value, ...;` in main, and `printf` of `expr`. The answer is the
    expression's value after the macros are expanded as text; the explanation shows that expansion."""
    lines = list(defs) + ["int main(void) {"]
    if vars_:
        lines.append("    int " + ", ".join(f"{n} = {v}" for n, v in vars_) + ";")
    lines += ["    " + PF(fmt, expr), "}"]

    def env(p: dict) -> dict:
        return {n: int(_sub(p, v)) for n, v in vars_}

    def ans(p: dict) -> int:
        return macro_value([_sub(p, d) for d in defs], _sub(p, expr), env(p))

    sentence = _sentence(why)

    def explain(p: dict) -> str:
        return f"It expands to {macro_text([_sub(p, d) for d in defs], _sub(p, expr))}. {sentence}"

    return C(T(*lines), ans, explain)


AB = [("a", "$a"), ("b", "$b")]
ABC = [("a", "$a"), ("b", "$b"), ("c", "$c")]
ABCD = [("a", "$a"), ("b", "$b"), ("c", "$c"), ("d", "$d")]
PASTE = "The arguments are pasted in as text, not worked out first, so the brackets that were never written are missing."

SQ = "#define SQ(x) x*x"
SQP = "#define SQ(x) (x)*(x)"
SQF = "#define SQ(x) ((x)*(x))"
MAXF = "#define MAX(a, b) ((a) > (b) ? (a) : (b))"
MAXB = "#define MAX(a, b) a > b ? a : b"


def _double_max(p: dict) -> str:
    # int i = a, j = b; int m = MAX(i++, j): the condition runs i++ once; the chosen (a) runs it again
    i, j = p["a"], p["b"]
    cond = i > j
    i += 1
    if cond:
        m = i
        i += 1
    else:
        m = j
    return f"{m} {i}"


def _double_abs(start: int) -> str:
    i = start
    cond = i < 0
    i -= 1
    if cond:
        m = -i
        i -= 1
    else:
        m = i
        i -= 1
    return f"{m} {i}"


MACROS: list[Maker] = [
    # ── missing brackets around an argument ──
    MC([SQ], AB, "SQ(a+1)", "a+1*a+1: the multiplication happens before the additions."),
    MC([SQ], AB, "SQ(a+b)", "a+b*a+b: only b is multiplied by a."),
    MC([SQ], AB, "SQ(a-1)", "a-1*a-1: the minus signs are not grouped."),
    MC([SQ], AB, "SQ(a)", "With a plain name there is nothing to regroup: it is just a * a."),
    MC([SQ], [], "SQ($a+$b)", "The text a+b is pasted twice, with no brackets, so * goes first."),
    MC([SQ], [("a", "$a")], "SQ(-a)", "-a*-a: two unary minuses and a product, which is fine."),
    MC([SQ], AB, "$n / SQ(a)", "n / a * a: / and * share a rank and go left to right."),
    MC(["#define CUBE(x) x*x*x"], AB, "CUBE(a+1)", "a+1*a+1*a+1: only the last two terms are multiplied."),
    MC(["#define INC(x) x+1"], AB, "INC(a) * b", "a+1 * b: the * is not applied to the whole of INC(a)."),
    MC(["#define DOUBLE(x) x+x"], AB, "a * DOUBLE(b)", "a * b + b: the macro's own + has no brackets round it."),
    MC(["#define TWICE(x) 2*x"], AB, "TWICE(a+b)", "2*a+b: only a is doubled."),
    MC(["#define HALF(x) x/2"], [("a", "$a")], "HALF($n+a)", "n+a/2: only a is halved (and the division cuts)."),
    MC(["#define DIFF(x, y) x-y"], AB, "DIFF($n, a+b)", "n-a+b: the minus is not applied to the whole of a+b."),
    MC(["#define DIFF(x, y) (x)-(y)"], AB, "DIFF($n, a+b)", "The argument is bracketed, so the whole of a+b is subtracted."),
    MC(["#define NEG(x) -x"], AB, "NEG(a-b)", "-a-b: the minus is not applied to the whole of a-b."),
    MC(["#define NEG(x) -x"], [("a", "$a")], "NEG(-a)", "- -a: two separate minus signs, and they cancel."),
    MC(["#define ADD(x, y) x+y"], ABCD, "ADD(a, b) * ADD(c, d)", "a+b * c+d: each ADD is a bare sum, so * binds tighter."),
    MC(["#define MUL(x, y) x*y"], ABCD, "MUL(a+b, c+d)", "a+b*c+d: the sums are not grouped."),
    MC(["#define SUM3(x, y, z) x+y+z"], ABCD, "SUM3(a, b, c) * d", "a+b+c * d: only c is multiplied by d."),
    MC(["#define MOD(x, y) x%y"], AB, "MOD($n+a, b)", "n+a%b: % ranks above +."),
    MC(["#define IS_EVEN(x) x%2==0"], AB, "IS_EVEN(a+b)", "a+b%2==0: the % goes first, then the +, then the ==."),
    MC(["#define IS_EVEN(x) x%2==0"], [("a", "$a")], "!IS_EVEN(a)",
       "!a%2==0: the ! applies to a alone, giving 0, and 0 % 2 == 0 is true."),
    MC(["#define IS_EVEN(x) ((x)%2==0)"], AB, "IS_EVEN(a+b)", "Every use is bracketed, so the whole sum is tested."),
    MC(["#define IN_RANGE(x) x >= 2 && x <= $n"], [("v", "$a")], "!IN_RANGE(v)",
       "!v >= 2 && v <= n: the ! applies to v alone, giving 0, and 0 >= 2 is false."),
    # ── the repaired ones ──
    MC([SQP], AB, "$n / SQ(a)", "n / (a) * (a): the macro's own * is not bracketed, so / goes first."),
    MC([SQP], AB, "$n % SQ(a)", "n % (a) * (a): % and * go left to right."),
    MC([SQF], AB, "$n / SQ(a)", "Both the arguments and the whole result are bracketed: n / (a * a)."),
    MC([SQF], AB, "SQ(SQ(a))", "Fully bracketed macros nest safely: (a * a) squared."),
    MC(["#define SQ(x) (x*x)"], AB, "SQ(a+1)", "The result is bracketed but the argument is not: (a+1*a+1)."),
    MC(["#define TWICE(x) ((x) * 2)"], [("a", "$a")], "TWICE(TWICE(a))", "A safe macro nests: ((a * 2) * 2)."),
    # ── MAX, MIN, ABS ──
    MC([MAXF], ABCD, "MAX(a+b, c*d)", "Each argument sits in its own brackets, so the sums and products are compared whole."),
    MC([MAXF], ABCD, "MAX(MAX(a, b), MAX(c, d))", "Nested calls expand one inside the other: the biggest of four."),
    MC(["#define MIN(a, b) ((a) < (b) ? (a) : (b))"], ABC, "MIN(a, MIN(b, c))", "The inner MIN is the smaller of b and c, the outer one compares it with a."),
    MC([MAXB], ABC, "MAX(a, b) + c", "a > b ? a : b + c: the + c ends up inside the false branch only."),
    MC([MAXB], AB, "2 * MAX(a, b)", "2 * a > b ? a : b: the whole comparison 2*a > b is the condition."),
    MC(["#define ABS(x) ((x) < 0 ? -(x) : (x))"], AB, "ABS(a-b)", "The brackets keep a-b together, so this is |a - b|."),
    MC(["#define ABS(x) (x) < 0 ? -(x) : (x)"], AB, "ABS(a-b) + 1", "The + 1 lands in the false branch only: a negative a-b gets no +1."),
    # ── a macro argument that is evaluated twice ──
    C(T(MAXF, "int main(void) {", "    int i = $a, j = $b;", "    int m = MAX(i++, j);", '    printf("%d %d\\n", m, i);', "}"),
      _double_max, lambda p: "MAX(i++, j) pastes i++ in twice: once in the test and once more if it is chosen, so i can grow by 2."),
    C(T("#define ABS(x) ((x) < 0 ? -(x) : (x))", "int main(void) {", "    int i = -$a;", "    int m = ABS(i--);",
        '    printf("%d %d\\n", m, i);', "}"), lambda p: _double_abs(-p["a"]),
      "ABS(i--) pastes i-- in twice: the test runs it once and the chosen branch runs it again, so i drops by 2."),
    C(T("#define ABS(x) ((x) < 0 ? -(x) : (x))", "int main(void) {", "    int i = $a;", "    int m = ABS(i--);",
        '    printf("%d %d\\n", m, i);', "}"), lambda p: _double_abs(p["a"]),
      "ABS(i--) pastes i-- in twice: the test runs it once and the chosen branch runs it again, so i drops by 2."),
    # ── object-like macros inside expressions ──
    MC(["#define SIZE $a + $b"], [("c", "$c")], "SIZE * c", "a + b * c: an object-like macro is text too, so the * only reaches b."),
    MC(["#define SIZE ($a + $b)"], [("c", "$c")], "SIZE * c", "The brackets are part of the macro, so the sum is multiplied whole."),
    MC(["#define LIMIT $n", "#define DOUBLE_LIMIT LIMIT * 2"], [], "DOUBLE_LIMIT + 1", "Macros expand inside macros: n * 2 + 1."),
    MC(["#define A B + 1", "#define B $a"], [("b", "$b")], "A * b", "A becomes B + 1 and then a + 1, so the * only reaches the 1."),
    MC(["#define PI 3", "#define AREA(r) PI * r * r"], AB, "AREA(a+b)", "3 * a+b * a+b: the radius is not bracketed."),
    MC(["#define PI 3", "#define AREA(r) (PI * (r) * (r))"], AB, "AREA(a+b)", "Bracketed, it is 3 * (a+b) * (a+b)."),
    MC(["#define SCALE $k", "#define SCALED(x) ((x) * SCALE)"], AB, "SCALED(a+b)", "SCALE becomes the number k and the argument is bracketed."),
    C(T("#define SQ(x) ((x) * (x))", "int main(void) {", "    int SQ = $a;", '    printf("%d\\n", SQ + SQ(2));', "}"),
      lambda p: p["a"] + 4, "A function-like macro only expands when a ( follows its name: SQ alone is the variable."),
    # ── counting with macros ──
    C(T("#define N $n", "#define STEP $a", "int main(void) {", "    int c = 0;", "    for (int i = 0; i < N; i += STEP)", "        c++;",
        '    printf("%d\\n", c);', "}"), lambda p: len(range(0, p["n"], p["a"])), "The loop counts i = 0, a, 2a ... below n."),
    C(T("#define N $a + $b", "int main(void) {", "    int c = 0;", "    for (int i = 0; i < N * 2; i++)", "        c++;",
        '    printf("%d\\n", c);', "}"), lambda p: p["a"] + 2 * p["b"], "i < a + b * 2: the loop runs a + 2b times."),
    C(T("#define COUNT(arr) (sizeof(arr) / sizeof((arr)[0]))", "int main(void) {", "    int v[] = {$a, $b, $c, $d, 1};",
        '    printf("%zu\\n", COUNT(v));', "}"), 5, "sizeof the array over sizeof one element counts the elements."),
    C(T("#define COUNT(arr) (sizeof(arr) / sizeof((arr)[0]))", "int main(void) {", '    char s[] = "$w";',
        '    printf("%zu\\n", COUNT(s));', "}"), lambda p: p["L"] + 1, "An array of char counts the final zero byte too."),
    # ── statement macros ──
    C(T("#define SWAP(a, b) t = a; a = b; b = t", "int main(void) {", "    int x = $a, y = $b, t = 0, c = 0;", "    if (c)",
        "        SWAP(x, y);", '    printf("%d %d %d\\n", x, y, t);', "}"), lambda p: f"{p['b']} 0 0",
      "Only the first statement of the macro belongs to the if: t = x is skipped, but x = y and y = t both run."),
    C(T("#define SWAP(a, b) t = a; a = b; b = t", "int main(void) {", "    int x = $a, y = $b, t = 0, c = 1;", "    if (c)",
        "        SWAP(x, y);", '    printf("%d %d\\n", x, y);', "}"), lambda p: f"{p['b']} {p['a']}",
      "The test is true, so all three statements of the macro run and the values trade places."),
    C(T("#define SWAP(a, b) do { t = a; a = b; b = t; } while (0)", "int main(void) {", "    int x = $a, y = $b, t = 0, c = 0;",
        "    if (c)", "        SWAP(x, y);", '    printf("%d %d\\n", x, y);', "}"), lambda p: f"{p['a']} {p['b']}",
      "do { ... } while (0) turns the macro into one statement, so the false test skips all of it."),
    # ── # and ## ──
    C(T("#define STR(x) #x", "int main(void) {", '    printf("%s\\n", STR($w));', "}"), lambda p: p["w"], "# turns the argument's text into a string."),
    C(T("#define STR(x) #x", "int main(void) {", '    printf("%s\\n", STR($a+$b));', "}"), lambda p: f"{p['a']}+{p['b']}",
      "# makes a string of the text, not of its value: nothing is added."),
    C(T("#define STR(x) #x", "int main(void) {", '    printf("%s\\n", STR(  $a   +   $b ));', "}"), lambda p: f"{p['a']} + {p['b']}",
      "# cuts the white space at both ends and squeezes the middle runs to one space."),
    C(T("#define STR(x) #x", "#define XSTR(x) STR(x)", "#define N $a", "int main(void) {", '    printf("%s %s\\n", STR(N), XSTR(N));', "}"),
      lambda p: f"N {p['a']}", "STR(N) stringifies the name before N is expanded; XSTR expands N first and then STR sees the number."),
    C(T('#define SHOW(x) printf(#x " = %d\\n", x)', "int main(void) {", "    int v = $a;", "    SHOW(v * 2);", "}"),
      lambda p: f"v * 2 = {p['a'] * 2}", "#x prints the expression's text and x its value."),
    C(T('#define SHOW(x) printf(#x " = %d\\n", x)', "int main(void) {", "    int a = $a, b = $b;", "    SHOW(a - b);", "}"),
      lambda p: f"a - b = {p['a'] - p['b']}", "#x prints the expression's text and x its value."),
    C(T("#define CAT(a, b) a##b", "int main(void) {", "    int xy = $n;", '    printf("%d\\n", CAT(x, y));', "}"), lambda p: p["n"],
      "## glues the two tokens into one name: xy."),
    C(T("#define CAT(a, b) a##b", "int main(void) {", '    printf("%d\\n", CAT($a, $b) + 1);', "}"), lambda p: int(f"{p['a']}{p['b']}") + 1,
      "## glues the digits into one number, ab, before the + 1."),
    C(T("#define VAR(n) v##n", "int main(void) {", "    int v1 = $a, v2 = $b, v3 = $c;", '    printf("%d\\n", VAR($k));', "}"),
      lambda p: [p["a"], p["b"], p["c"]][p["k"] - 1], "VAR(k) glues v and k into the name v1, v2 or v3."),
    # ── #undef, order and conditional compilation ──
    C(T("#define N $a", "int main(void) {", "    int x = N;", "#undef N", "#define N $n", "    int y = N;", '    printf("%d %d\\n", x, y);', "}"),
      lambda p: f"{p['a']} {p['n']}", "A macro is replaced where it is used, with the definition in force at that line."),
    C(T("int main(void) {", "    int x = 1;", "#define N $a", "    x += N;", "#undef N", "#define N $n", "    x += N;", '    printf("%d\\n", x);', "}"),
      lambda p: 1 + p["a"] + p["n"], "Each use of N takes the value it had at that line."),
    C(T("#define DEBUG", "int main(void) {", "#ifdef DEBUG", '    printf("%d\\n", $a);', "#else", '    printf("%d\\n", $b);', "#endif", "}"),
      lambda p: p["a"], "DEBUG is defined (its value does not matter for #ifdef), so the first branch is compiled."),
    C(T("int main(void) {", "#ifdef DEBUG", '    printf("%d\\n", $a);', "#else", '    printf("%d\\n", $b);', "#endif", "}"),
      lambda p: p["b"], "DEBUG is never defined, so the #else branch is the one compiled."),
    C(T("#define DEBUG 0", "int main(void) {", "#ifdef DEBUG", '    printf("%d\\n", $a);', "#else", '    printf("%d\\n", $b);', "#endif", "}"),
      lambda p: p["a"], "#ifdef only asks whether DEBUG is defined, not what it is: defined as 0 still counts."),
    C(T("#define DEBUG 0", "int main(void) {", "#if DEBUG", '    printf("%d\\n", $a);', "#else", '    printf("%d\\n", $b);', "#endif", "}"),
      lambda p: p["b"], "#if tests the value: 0 is false."),
    C(T("#define LEVEL $a", "int main(void) {", "#if LEVEL > $b", '    printf("high\\n");', "#else", '    printf("low\\n");', "#endif", "}"),
      lambda p: "high" if p["a"] > p["b"] else "low", "The #if compares the two numbers while preprocessing."),
    C(T("#define X $a", "int main(void) {", "#if X > 7", '    printf("big\\n");', "#elif X > 4", '    printf("mid\\n");', "#else", '    printf("small\\n");', "#endif", "}"),
      lambda p: "big" if p["a"] > 7 else ("mid" if p["a"] > 4 else "small"), "The first true #if or #elif branch is the only one compiled."),
    C(T("#define A $a", "#define B $b", "int main(void) {", "#if A * B > 20", '    printf("%d\\n", 1);', "#else", '    printf("%d\\n", 0);', "#endif", "}"),
      lambda p: int(p["a"] * p["b"] > 20), "The #if works out A * B, a number, before it compares."),
    C(T("#ifndef SIZE", "#define SIZE $n", "#endif", "int main(void) {", '    printf("%d\\n", SIZE);', "}"), lambda p: p["n"],
      "SIZE is not defined yet, so #ifndef lets the #define through."),
    C(T("#define SIZE $a", "#ifndef SIZE", "#define SIZE $n", "#endif", "int main(void) {", '    printf("%d\\n", SIZE);', "}"), lambda p: p["a"],
      "SIZE already exists, so the #ifndef block is skipped and the first value stays."),
    C(T("#define A", "int main(void) {", "#if defined(A) && !defined(B)", '    printf("%d\\n", $a);', "#else", '    printf("%d\\n", $b);', "#endif", "}"),
      lambda p: p["a"], "A is defined and B is not, so the test is true."),
    C(T("int main(void) {", "#if 0", '    printf("%d ", $a);', "#endif", '    printf("%d\\n", $b);', "}"), lambda p: p["b"],
      "#if 0 removes the code before the compiler ever sees it."),
    C(T("#define FLAG $r", "int main(void) {", "#if FLAG", '    printf("%d\\n", $a);', "#else", '    printf("%d\\n", $b);', "#endif", "}"),
      lambda p: p["a"] if p["r"] else p["b"], "A nonzero FLAG makes the #if true, 0 makes it false."),
]
