"""C core pack, part 2: Char & String and Array Reach.

Every answer is worked out by hand (`_c_model.py`), and tests/test_brain_packs.py compiles every template with the real
compilers in batches (tests/c_oracle.py). Prompts are the BODY of `main` unless they define `main` (then a complete
program with helper functions); both print their own answer.
"""

from __future__ import annotations

from ._c_model import C, c_strchr, c_strrchr, strcmp_sign
from ._model import Maker
from ._ccore_numbers import T


def PF(conv: str, rest: str) -> str:
    """`printf("<conv>\\n", <rest>);` as C text (so a template stays readable)."""
    return 'printf("' + conv + '\\n", ' + rest + ');'


# ── 1. Char & String ────────────────────────────────────────────────────

STRINGS: list[Maker] = [
    C(PF("%d", "'$x' - 'a'"), lambda p: ord(p["x"]) - 97, "A char is a small number: the letters are numbered in order, so x - 'a' counts from a."),
    C(PF("%c", "'$x' + $k"), lambda p: chr(ord(p["x"]) + p["k"]), "Adding to a letter moves along the alphabet: the letters have consecutive codes."),
    C(PF("%c", "'$X' + $a"), lambda p: chr(ord(p["X"]) + p["a"]), "Capital letters have consecutive codes too."),
    C(PF("%c", "'$x' - 32"), lambda p: chr(ord(p["x"]) - 32), "A lower-case letter is 32 above its capital."),
    C(PF("%c", "'$x' - 'a' + 'A'"), lambda p: p["x"].upper(), "x - 'a' is the letter's place in the alphabet; adding 'A' lands on the capital."),
    C(PF("%d", "'9' - '0'"), 9, "The digits have consecutive codes, so a digit minus '0' is its value."),
    C(PF("%d", "'0' + $a"), lambda p: 48 + p["a"], "'0' is the number 48, so '0' + a is 48 + a."),
    C(PF("%c", "'0' + $a"), lambda p: str(p["a"]), "'0' + a is the code of the digit a, and %c prints that character."),
    C(T("char c = '$x';", "c += $a;", PF("%c", "c")), lambda p: chr(ord(p["x"]) + p["a"]), "Adding to a char moves along the alphabet."),
    C(PF("%d", "'A' < 'a'"), 1, "Capitals have smaller codes than lower-case letters."),
    C(PF("%d", "'a' - 'A'"), 32, "A lower-case letter is 32 above its capital."),
    C(PF("%d", '(int)strlen("$w")'), lambda p: len(p["w"]), "strlen counts the characters before the terminating NUL."),
    C(PF("%zu", 'strlen("$w") + $a'), lambda p: len(p["w"]) + p["a"], "strlen gives the length; then a is added."),
    C(T('char s[] = "$w";', PF("%zu %zu", "strlen(s), sizeof(s)")), lambda p: f"{len(p['w'])} {len(p['w']) + 1}",
      "sizeof counts the NUL that ends the string, so it is one more than strlen."),
    C(T('char s[10] = "$w";', PF("%zu %zu", "strlen(s), sizeof(s)")), lambda p: f"{len(p['w'])} 10",
      "strlen stops at the NUL after the word; sizeof is the size of the whole array."),
    C(T('char s[] = "$w";', PF("%d", "s[sizeof(s) - 1]")), 0, "The last element of a string array is the NUL terminator: the number 0."),
    C(T('const char *s = "$w";', PF("%c", "s[$j]")), lambda p: p["w"][p["j"]], "Indexing counts from 0."),
    C(PF("%c", '"$w"[$j]'), lambda p: p["w"][p["j"]], "A string literal can be indexed directly; the first character is at 0."),
    C(T('const char *s = "$w";', PF("%s", "s + $i")), lambda p: p["w"][p["i"]:], "s + i points i characters in: %s prints the rest of the string."),
    C(T('char s[] = "$w";', PF("%s", "&s[$i]")), lambda p: p["w"][p["i"]:], "&s[i] is the address of character i: %s prints from there to the end."),
    C(PF("%d", 'strcmp("$w", "$w") == 0'), 1, "strcmp returns 0 for equal strings."),
    C(PF("%d", 'strcmp("$w", "$z") < 0'), lambda p: 1 if strcmp_sign(p["w"], p["z"]) < 0 else 0,
      "strcmp is negative when the first string comes first in dictionary order."),
    C(PF("%d", 'strcmp("$w", "$z") > 0'), lambda p: 1 if strcmp_sign(p["w"], p["z"]) > 0 else 0,
      "strcmp is positive when the first string comes later in dictionary order."),
    C(PF("%s", '"$w" "$z"'), lambda p: p["w"] + p["z"], "Two string literals side by side are joined at compile time."),
    C(PF("%zu", 'sizeof("$w")'), lambda p: len(p["w"]) + 1, "A literal's size includes the NUL terminator."),
    C(PF("%zu", r'strlen("$w\0$z")'), lambda p: len(p["w"]), r"The \0 in the middle ends the string for strlen."),
    C(PF("%zu", r'sizeof("$w\0$z")'), lambda p: len(p["w"]) + 1 + len(p["z"]) + 1, r"sizeof counts every character of the literal, the \0 and the final NUL too."),
    C(PF("%d", r"'\n'"), 10, r"\n is the character number 10."),
    C(PF("%d", r"'\0'"), 0, r"\0 is the NUL character: the number 0."),
    C(PF("%d", r"'\\'"), 92, r"\\ is a single backslash character, number 92."),
    C(PF("%d", r"'\''"), 39, r"\' is a single quote character, number 39."),
    C(PF("%d", r"'\x41'"), 65, r"\x41 is the character with hexadecimal code 41: 65, an A."),
    C(PF("%d", r"'\101'"), 65, r"\101 is an octal escape: 101 in octal is 65, an A."),
    C(PF("%s", r'"a\\b$w"'), lambda p: "a\\b" + p["w"], r"\\ in a string prints one backslash."),
    C(PF("%zu", r'sizeof("a\n")'), 3, "The characters are a, the newline and the NUL."),
    C(PF("%zu", r'strlen("a\nb")'), 3, r"\n is one character."),
    C(PF("%zu", r'strlen("a\\nb")'), 4, r"\\ is one backslash, so the four characters are a, backslash, n and b."),
    C(T('const char *p = "$w";', "int n = 0;", "while (*p++)", "    n++;", PF("%d", "n")), lambda p: len(p["w"]), "The loop counts characters until it reaches the NUL, which is 0."),
    C(T("int n = 0;", 'for (const char *p = "$w"; *p; p++)', "    if (*p == '$f')", "        n++;", PF("%d", "n")), lambda p: p["w"].count(p["f"]), "The loop counts how many characters equal the letter."),
    C(T('char s[] = "$w";', "s[$j] = '$x';", PF("%s", "s")), lambda p: p["w"][:p["j"]] + p["x"] + p["w"][p["j"] + 1:], "An array of chars can be changed in place."),
    C(T('char s[] = "$w";', r"s[$i] = '\0';", PF("%s %zu", "s, strlen(s)")), lambda p: f"{p['w'][:p['i']]} {p['i']}", r"A \0 written into the string ends it there."),
    C(T('char s[8] = "$w";', PF("%d", "s[7]")), 0, "What the initial string does not fill is set to 0."),
    C(T('char s[20] = "$w";', 'strcat(s, "$z");', PF("%s %zu", "s, strlen(s)")), lambda p: f"{p['w']}{p['z']} {len(p['w']) + len(p['z'])}", "strcat adds the second string to the end of the first."),
    C(T("char s[20];", 'strcpy(s, "$w");', PF("%zu", "strlen(s)")), lambda p: len(p["w"]), "strcpy copies the characters and the NUL."),
    C(PF("%s", """strchr("$w", '$f')"""), lambda p: c_strchr(p["w"], p["f"]), "strchr gives the string from the first occurrence of the letter."),
    C(PF("%s", """strrchr("$w", '$f')"""), lambda p: c_strrchr(p["w"], p["f"]), "strrchr gives the string from the last occurrence of the letter."),
    C(T('const char *s = "$w";', PF("%d", "(int)(strchr(s, '$f') - s)")), lambda p: p["w"].index(p["f"]), "Subtracting two pointers into the same string gives the position."),
    C(PF("%d", 'strncmp("$w", "$z", 1) == 0'), lambda p: 1 if p["w"][0] == p["z"][0] else 0, "strncmp with 1 compares only the first character."),
    C(T('char a[] = "$w", b[] = "$w";', PF("%d", "a == b")), 0, "== on two arrays compares their addresses, and two arrays are in different places."),
    C(T('char a[] = "$w", b[] = "$w";', PF("%d", "strcmp(a, b) == 0")), 1, "strcmp compares the characters, which are the same."),
    C(PF("%c", '"$w"[0] - 32'), lambda p: p["w"][0].upper(), "The first letter minus 32 is its capital."),
    C(T('char s[] = "$w";', "int i = 0;", "while (s[i] != '$f')", "    i++;", PF("%d", "i")), lambda p: p["w"].index(p["f"]), "The loop stops at the first position holding the letter."),
    C(PF("%c", "'A' + $n % 26"), lambda p: chr(65 + p["n"] % 26), "n % 26 is a place in the alphabet; adding it to 'A' gives the letter."),
    C(PF("%s", '$a > $b ? "$w" : "$z"'), lambda p: p["w"] if p["a"] > p["b"] else p["z"], "The conditional picks the first string when the test is true."),
    C(PF("%c", '"abcdefgh"[$a - 2]'), lambda p: "abcdefgh"[p["a"] - 2], "Indexing counts from 0."),
    C(PF("%c", '$a["abcdefghij"]'), lambda p: "abcdefghij"[p["a"]], "a[i] means *(a + i), which is the same as *(i + a): so i[a] works too."),
]


# ── 2. Array Reach ──────────────────────────────────────────────────────

def _arr(p: dict) -> list[int]:
    return [p["a"], p["b"], p["c"], p["d"]]


ARR = r"int a[] = {$a, $b, $c, $d};"

ARRAYS: list[Maker] = [
    C(T(ARR, r'printf("%d\n", a[$q]);'), lambda p: _arr(p)[p["q"]], "Indexing counts from 0."),
    C(T(ARR, r'printf("%d\n", a[3]);'), lambda p: p["d"], "The last of four elements is at index 3."),
    C(T(ARR, r'printf("%d\n", a[$q] + a[3]);'), lambda p: _arr(p)[p["q"]] + p["d"], "Two elements added."),
    C(T(ARR, r'printf("%zu\n", sizeof(a) / sizeof(a[0]));'), 4, "The whole array's size divided by one element's size is the element count."),
    C(T(r'int a[$a] = {0};', r'printf("%zu\n", sizeof(a) / sizeof(a[0]));'), lambda p: p["a"], "Size of the array over size of one element: the number of elements."),
    C(T(r'int a[$a];', r'printf("%zu\n", sizeof(a));'), lambda p: 4 * p["a"], "Each int is 4 bytes."),
    C(T(r'uint16_t a[$a];', r'printf("%zu\n", sizeof(a));'), lambda p: 2 * p["a"], "Each uint16_t is 2 bytes."),
    C(T(r'char a[$n];', r'printf("%zu\n", sizeof(a));'), lambda p: p["n"], "Each char is 1 byte."),
    C(T(r'double a[$a];', r'printf("%zu\n", sizeof(a));'), lambda p: 8 * p["a"], "Each double is 8 bytes."),
    C(T(r'int a[5] = {$a, $b};', r'printf("%d\n", a[3]);'), 0, "The elements the braces do not mention are set to 0."),
    C(T(r'int a[5] = {$a, $b};', r'printf("%d\n", a[0] + a[1] + a[2] + a[3] + a[4]);'), lambda p: p["a"] + p["b"], "Only the first two were given; the rest are 0."),
    C(T(r'int a[4] = {0};', r'a[$q] = $a;', r'printf("%d\n", a[0] + a[1] + a[2] + a[3]);'), lambda p: p["a"], "Everything starts at 0; one element is set."),
    C(T(r'int a[5] = {[2] = $a, [4] = $b};', r'printf("%d %d %d\n", a[1], a[2], a[4]);'), lambda p: f"0 {p['a']} {p['b']}", "A designated initializer sets one position; the rest are 0."),
    C(T(r'int m[2][3] = {{$a, $b, $c}, {$d, 1, 2}};', r'printf("%d\n", m[$r][$q]);'), lambda p: [[p["a"], p["b"], p["c"]], [p["d"], 1, 2]][p["r"]][p["q"]], "m[row][column], both counting from 0."),
    C(T(r'int m[$k][$b];', r'printf("%zu %zu\n", sizeof(m) / sizeof(m[0]), sizeof(m[0]) / sizeof(m[0][0]));'), lambda p: f"{p['k']} {p['b']}", "sizeof(m) over sizeof(m[0]) is the rows; one row over one element is the columns."),
    C(T(r'int m[$k][$b];', r'printf("%zu\n", sizeof(m));'), lambda p: 4 * p["k"] * p["b"], "rows times columns times 4 bytes."),
    C(T(r'int m[2][3] = {{$a}, {$b, $c}};', r'printf("%d %d %d\n", m[0][1], m[1][1], m[1][2]);'), lambda p: f"0 {p['c']} 0", "Each inner brace starts a row; what it leaves out is 0."),
    C(T(r'int m[2][2] = {$a, $b, $c, $d};', r'printf("%d\n", m[1][0]);'), lambda p: p["c"], "Without inner braces the values fill the rows one after another."),
    C(T(r'int m[3][3] = {{$a, $b, $c}, {$d, $a, $b}, {$c, $d, $a}};', r'int s = 0;', r'for (int i = 0; i < 3; i++)', r'    s += m[i][i];', r'printf("%d\n", s);'), lambda p: 3 * p["a"], "m[i][i] is the diagonal: a, a, a."),
    C(T(ARR, r'int *p = a;', r'printf("%d\n", *(p + $q));'), lambda p: _arr(p)[p["q"]], "p + q points q elements along; * reads it."),
    C(T(ARR, r'int *p = a;', r'printf("%d\n", p[$q]);'), lambda p: _arr(p)[p["q"]], "p[q] is *(p + q)."),
    C(T(ARR, r'printf("%d\n", *(a + 3));'), lambda p: p["d"], "a + 3 points at the fourth element."),
    C(T(ARR, r'int *p = a + 1;', r'printf("%d\n", p[-1]);'), lambda p: p["a"], "p[-1] is the element before the one p points at."),
    C(T(ARR, r'int *p = a + 1;', r'printf("%d\n", p[1]);'), lambda p: p["c"], "p points at the second element, so p[1] is the third."),
    C(T(ARR, r'int *p = a;', r'int x = *p++;', r'printf("%d %d\n", x, *p);'), lambda p: f"{p['a']} {p['b']}", "*p++ reads where p points, then moves p on to the next element."),
    C(T(ARR, r'int *p = a;', r'(*p)++;', r'printf("%d %d\n", a[0], *p);'), lambda p: f"{p['a'] + 1} {p['a'] + 1}", "(*p)++ adds 1 to the element p points at; p does not move."),
    C(T(ARR, r'int *p = a;', r'printf("%d\n", *++p);'), lambda p: p["b"], "++p moves first, then * reads the new place."),
    C(T(ARR, r'int *p = a;', r'p += 2;', r'printf("%d\n", *p);'), lambda p: p["c"], "p += 2 moves two elements along."),
    C(T(ARR, r'int *q = &a[3];', r'int *p = &a[$r];', r'printf("%d\n", (int)(q - p));'), lambda p: 3 - p["r"], "Subtracting two pointers into one array counts the elements between them."),
    C(T(ARR, r'printf("%d\n", $q[a]);'), lambda p: _arr(p)[p["q"]], "a[q] is *(a + q), and + goes either way, so q[a] is the same."),
    C(T(ARR, r'int *p = &a[2];', r'printf("%d %d\n", *p, *(p - 1));'), lambda p: f"{p['c']} {p['b']}", "p points at the third element; p - 1 is the second."),
    C(T(ARR, r'printf("%d\n", &a[1] < &a[3]);'), 1, "A later element has a bigger address."),
    C(T(ARR, r'int s = 0;', r'for (int i = 0; i < 4; i++)', r'    s += a[i];', r'printf("%d\n", s);'), lambda p: sum(_arr(p)), "The loop adds all four elements."),
    C(T(ARR, r'int m = a[0];', r'for (int i = 1; i < 4; i++)', r'    if (a[i] > m)', r'        m = a[i];', r'printf("%d\n", m);'), lambda p: max(_arr(p)), "The loop keeps the biggest element seen."),
    C(T(r'int a[5] = {$a};', r'for (int i = 1; i < 5; i++)', r'    a[i] = a[i - 1] + i;', r'printf("%d\n", a[4]);'), lambda p: p["a"] + 1 + 2 + 3 + 4, "Each element is the one before plus its index."),
    C(T(ARR, r'for (int i = 0; i < 2; i++) {', r'    int t = a[i];', r'    a[i] = a[3 - i];', r'    a[3 - i] = t;', r'}', r'printf("%d %d\n", a[0], a[1]);'), lambda p: f"{p['d']} {p['c']}", "The loop swaps the ends moving inward: the array is reversed."),
    C(T(r'static int g[4];', r'printf("%d\n", g[$q] + g[3]);'), 0, "A static array starts as all zeros."),
    C(T(r'void fill(int *a, int n) {', r'    for (int i = 0; i < n; i++)', r'        a[i] = i * $a;', r'}', r'int main(void) {', r'    int a[4];', r'    fill(a, 4);', r'    printf("%d\n", a[3]);', r'}'), lambda p: 3 * p["a"], "The function receives the address of the array, so it fills the caller's array."),
    C(T(r'int sum(int a[], int n) {', r'    int s = 0;', r'    for (int i = 0; i < n; i++)', r'        s += a[i];', r'    return s;', r'}', r'int main(void) {', r'    int a[] = {$a, $b, $c};', r'    printf("%d\n", sum(a, 3));', r'}'), lambda p: p["a"] + p["b"] + p["c"], "The function walks the caller's array and adds it up."),
    C(T(r'void f(int a[]) {', r'    printf("%d\n", sizeof(a) == sizeof(int *));', r'}', r'int main(void) {', r'    int a[$a];', r'    f(a);', r'}'), 1, "An array parameter is really a pointer, so its sizeof is the size of a pointer."),
    C(T(r'void zero(int a[], int n) {', r'    for (int i = 0; i < n; i++)', r'        a[i] = 0;', r'}', r'int main(void) {', r'    int a[] = {$a, $b, $c};', r'    zero(a, 2);', r'    printf("%d\n", a[0] + a[1] + a[2]);', r'}'), lambda p: p["c"], "zero clears the first two elements of the caller's array."),
    C(T(r'void bump(int a[]) {', r'    a[0]++;', r'}', r'int main(void) {', r'    int a[] = {$a, $b};', r'    bump(a);', r'    printf("%d\n", a[0]);', r'}'), lambda p: p["a"] + 1, "An array is passed by address, so the change shows in the caller."),
]
