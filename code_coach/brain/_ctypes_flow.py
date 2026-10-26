"""C types and preprocessor pack, part 4: Switch Path (`ct_switch`), Recursion (`ct_recurse`) and Storage & Linkage
(`ct_storage`).

A switch is simulated by `sim`: find the first matching case label (or the `default`), then run the statements of that
case and of every case after it until a `break`. Recursion is spelled out as the same Python recursion; storage is a
Python closure over the state the C keeps in `static` variables and globals. Printed sequences use `printf("a")`
pieces and end with a `.` printed after the switch so that "no case matched" still has an answer. No template depends on
the order in which the arguments of a call are evaluated.
"""

from __future__ import annotations

from ._c_model import C
from ._ccore_numbers import T
from ._ccore_text import PF
from ._model import Maker

# ── 1. Switch Path ──────────────────────────────────────────────────────

#: A label: an int, a one-character string (a char constant) or (source, value) for `case 1 + 1:` / `case 010:`;
#: None is `default:`.
Case = tuple  # (labels, text, breaks)


def _src(label) -> str:
    if label is None:
        return "default:"
    if isinstance(label, tuple):
        return f"case {label[0]}:"
    if isinstance(label, str):
        return f"case '{label}':"
    return f"case {label}:"


def _val(label):
    if isinstance(label, tuple):
        return label[1]
    if isinstance(label, str):
        return ord(label)
    return label


def cases_c(cases: list[Case]) -> list[str]:
    out = []
    for labels, text, brk in cases:
        out.append("    " + " ".join(_src(label) for label in labels) + (f' printf("{text}");' if text else "") + (" break;" if brk else ""))
    return out


def sim(cases: list[Case], v: int) -> str:
    """The text a switch on the value v prints."""
    start = None
    for i, (labels, _, _) in enumerate(cases):
        if any(label is not None and _val(label) == v for label in labels):
            start = i
            break
    if start is None:
        for i, (labels, _, _) in enumerate(cases):
            if None in labels:
                start = i
                break
    out = ""
    if start is None:
        return out
    for labels, text, brk in cases[start:]:
        out += text
        if brk:
            break
    return out


def SW(setup: list[str], expr: str, cases: list[Case], value, why: str, after: str = '    printf(".");') -> Maker:
    """`setup`, then `switch (expr) { cases }`, then a printf of `.`; `value(p)` is what the switch expression is."""
    lines = list(setup) + [f"switch ({expr}) {{"] + cases_c(cases) + ["}", after.strip()]
    return C(T(*lines), lambda p: sim(cases, value(p)) + ".", why)


def L(*labels):
    return list(labels)


BREAKS = "execution starts at the matching case and stops at the first break"
RUNON = "with no break, execution runs on into the next case"

SWITCHES: list[Maker] = [
    SW(["int x = $a;"], "x", [(L(2), "a", True), (L(3), "b", True), (L(4), "c", True), (L(5), "d", True)], lambda p: p["a"], f"Only the matching case runs: {BREAKS}."),
    SW(["int x = $a;"], "x", [(L(6), "w", True), (L(7), "x", True), (L(8), "y", True), (L(9), "z", True)], lambda p: p["a"], f"Only the matching case runs: {BREAKS}."),
    SW(["int x = $a;"], "x", [(L(2), "e", True), (L(4), "f", True), (L(6), "g", True), (L(8), "h", True), (L(None), "o", True)], lambda p: p["a"], "An odd x matches no case, so the default runs."),
    SW(["int x = $a;"], "x", [(L(2, 3), "L", True), (L(4, 5, 6), "M", True), (L(7, 8, 9), "H", True)], lambda p: p["a"], "Stacked labels share one body: any of 2-3, 4-6 or 7-9 picks its letter."),
    SW(["int x = $a;"], "x", [(L(None), "d", False), (L(2), "a", True), (L(3), "b", True)], lambda p: p["a"], "default is first: for 4 and up it runs and then falls into case 2's body. x of 2 or 3 jumps straight to its case."),
    SW(["int x = $a;"], "x", [(L(2), "a", True), (L(None), "d", False), (L(3), "c", True)], lambda p: p["a"], "default sits in the middle without a break: when it is chosen it runs on into case 3."),
    SW(["int x = $a;"], "x", [(L(2), "a", True), (L(3), "b", True), (L(None), "d", False)], lambda p: p["a"], "default is last, so falling off the end of the switch changes nothing."),
    SW(["int x = $a;"], "x", [(L(2), "a", False), (L(3), "b", False), (L(4), "c", False), (L(5), "d", False)], lambda p: p["a"], f"No case breaks: {RUNON}, to the end."),
    SW(["int x = $a;"], "x", [(L(6), "a", False), (L(7), "b", False), (L(8), "c", False), (L(9), "d", False)], lambda p: p["a"], f"No case breaks: {RUNON}, to the end."),
    SW(["int x = $a;"], "x", [(L(2), "a", False), (L(3), "b", True), (L(4), "c", False), (L(5), "d", False)], lambda p: p["a"], "The break in case 3 stops the run-on there."),
    SW(["int x = $a;"], "x", [(L(2), "a", False), (L(None), "d", True)], lambda p: p["a"], "case 2 has no break, so it runs on into the default."),
    SW(["int x = $a;"], "x", [(L(2), "a", True), (L(3, None), "d", True)], lambda p: p["a"], "default can share a body with a case label: both 3 and every non-match print d."),
    SW(["int x = $a;"], "x % 3", [(L(0), "z", True), (L(1), "o", True), (L(2), "t", True)], lambda p: p["a"] % 3, "The switch tests the remainder of x divided by 3."),
    SW(["int n = $n;"], "n / 10", [(L(1), "a", True), (L(2), "b", True), (L(3), "c", True), (L(None), "d", True)], lambda p: p["n"] // 10, "n / 10 is the tens digit: 1, 2, 3 or 4."),
    SW(["int x = $a;"], "x & 1", [(L(0), "even", True), (L(1), "odd", True)], lambda p: p["a"] & 1, "x & 1 is the last bit: 0 for even, 1 for odd."),
    SW(["int x = $a;"], "x / 5", [(L(0), "low", True), (L(1), "high", True)], lambda p: p["a"] // 5, "x / 5 cuts to 0 for 2 to 4 and 1 for 5 to 9."),
    SW(["int x = $a;"], "x * 2", [(L(4), "a", True), (L(8), "b", True), (L(12), "c", True), (L(None), "-", True)], lambda p: p["a"] * 2, "The expression is worked out first: x * 2."),
    SW(["int x = $a;"], "x - 2", [(L(0), "a", False), (L(1), "b", False), (L(2), "c", True)], lambda p: p["a"] - 2, "x - 2 picks the entry point; from there it runs on to the first break."),
    SW(["int x = $a;"], "x % 4", [(L(3), "c", False), (L(2), "b", False), (L(1), "a", False)], lambda p: p["a"] % 4, "Counting down: it enters at x % 4 and falls through the rest."),
    SW(["char c = '$x';"], "c", [(L("a"), "1", True), (L("b"), "2", True), (L("c"), "3", True), (L(None), "?", True)], lambda p: ord(p["x"]), "Case labels can be character constants."),
    SW(["char c = '$x';"], "c", [(L("a", "e", "i"), "V", True), (L(None), "C", True)], lambda p: ord(p["x"]), "a and e are vowels; the other letters from a to h fall to the default."),
    SW(["char c = '$x';"], "c - 'a'", [(L(0), "A", True), (L(1), "B", True), (L(2), "C", True), (L(None), "-", True)], lambda p: ord(p["x"]) - 97, "c - 'a' is the letter's position in the alphabet."),
    SW(["char c = '$x';"], "c", [(L("a", "b", "c"), "1", True), (L("d", "e", "f"), "2", True), (L("g", "h"), "3", True)], lambda p: ord(p["x"]), "Stacked character labels give each group its own digit."),
    SW(["int x = $a;"], "x", [(L(("1 + 1", 2)), "a", True), (L(("2 * 2", 4)), "b", True), (L(("3 * 2", 6)), "c", True), (L(None), "-", True)], lambda p: p["a"], "A case label may be any constant expression: 2, 4 and 6 here."),
    SW(["int x = $a;"], "x", [(L(10), "a", True), (L(("010", 8)), "b", True), (L(None), "c", True)], lambda p: p["a"], "A leading 0 makes 010 an octal number: it is 8, not 10."),
    SW(["int x = $a;"], "x", [(L(2), "a", True), (L(3), "b", True), (L(None), "", True)], lambda p: p["a"], "An empty default prints nothing: only 2 and 3 print a letter before the dot."),
]

# the next ones add to a number instead of printing, or are more than a switch: written out by hand


def _sum_fall(k: int) -> int:
    s, started = 0, False
    for c in (4, 3, 2, 1):
        if c == k:
            started = True
        if started:
            s += c
    return s


def _fall_hundreds(k: int) -> int:
    n, started = 0, False
    for c, add in ((3, 100), (2, 10), (1, 1)):
        if c == k:
            started = True
        if started:
            n += add
    return n


def _loop_switch(a: int) -> str:
    out = ""
    for i in range(a + 2):
        out += ["a", "b", "c"][i % 3]
    return out


def _loop_fall(a: int) -> str:
    out = ""
    for i in range(1, a + 1):
        if i == 1:
            out += "ab"
        elif i == 2:
            out += "b"
        elif i == 3:
            out += "cd"
        else:
            out += "d"
    return out


def _vowels(w: str) -> int:
    return sum(1 for ch in w if ch in "aeiou")


def _continue_loop(a: int) -> str:
    out = ""
    for i in range(a):
        if i % 2 == 0:
            continue
        out += str(i)
        out += "."
    return out


def _break_loop(a: int) -> int:
    n = 0
    for i in range(a):
        if i != 2:
            n += 10
        n += 1
    return n


def _nested(x: int, y: int) -> str:
    out = ""
    if x == 2:
        out += "a" if y == 1 else "b"
        out += "c"
    elif x == 3:
        out += "d"
    return out


def _machine(s: int) -> int:
    n = 0
    while s != 3:
        s = {0: 2, 2: 1, 1: 3}[s]
        n += 1
    return n


SWITCHES += [
    C(T("int x = $k + 1, s = 0;", "switch (x) {", "    case 4: s += 4;", "    case 3: s += 3;", "    case 2: s += 2;", "    case 1: s += 1;", "}", PF("%d", "s")),
      lambda p: _sum_fall(p["k"] + 1), "No breaks: it enters at x and adds every case from there down to 1."),
    C(T("int x = $k, n = 0;", "switch (x) {", "    case 3: n += 100;", "    case 2: n += 10;", "    case 1: n += 1;", "}", PF("%d", "n")),
      lambda p: _fall_hundreds(p["k"]), "It enters at x and runs on through every case below it."),
    C(T("for (int i = 0; i < $a + 2; i++)", "    switch (i % 3) {", '    case 0: printf("a"); break;', '    case 1: printf("b"); break;', '    default: printf("c");', "    }"),
      lambda p: _loop_switch(p["a"]), "The loop turns the switch over again and again: a, b, c, a, b, c..."),
    C(T("for (int i = 1; i <= $a; i++)", "    switch (i) {", '    case 1: printf("a");', '    case 2: printf("b"); break;', '    case 3: printf("c");', '    default: printf("d");', "    }"),
      lambda p: _loop_fall(p["a"]), "Each i enters the switch afresh: 1 falls into 2, 3 falls into the default, anything above 3 is the default."),
    C(T('const char *s = "$w";', "int v = 0;", "for (int i = 0; s[i]; i++)", "    switch (s[i]) {", "    case 'a': case 'e': case 'i': case 'o': case 'u': v++;", "    }", PF("%d", "v")),
      lambda p: _vowels(p["w"]), "Every vowel enters the switch and adds 1; consonants match nothing."),
    C(T("for (int i = 0; i < $a; i++) {", "    switch (i % 2) {", "    case 0: continue;", '    case 1: printf("%d", i);', "    }", '    printf(".");', "}"),
      lambda p: _continue_loop(p["a"]), "continue skips the rest of the loop body, even from inside a switch; an odd i prints itself and a dot."),
    C(T("int n = 0;", "for (int i = 0; i < $a; i++) {", "    switch (i) {", "    case 2: break;", "    default: n += 10;", "    }", "    n++;", "}", PF("%d", "n")),
      lambda p: _break_loop(p["a"]), "break only leaves the switch: the loop goes on and n++ still runs for i = 2."),
    C(T("int x = $k + 1, y = $k;", "switch (x) {", "case 2:", '    switch (y) { case 1: printf("a"); break; default: printf("b"); }', '    printf("c");', "    break;", 'case 3: printf("d");', "}", 'printf(".");'),
      lambda p: _nested(p["k"] + 1, p["k"]) + ".", "The inner break leaves only the inner switch, so the c after it still prints."),
    C(T("int f(int x) {", "    switch (x) {", "    case 2: return 20;", "    case 3: return 30;", "    }", "    return -1;", "}", "int main(void) {", PF("%d", "f($a)"), "}"),
      lambda p: {2: 20, 3: 30}.get(p["a"], -1), "return leaves the function at once; with no match it reaches the return -1."),
    C(T("int f(int n) {", "    int s = 0;", "    switch (n) { case 3: s += 1; case 2: s += 2; case 1: s += 4; }", "    return s;", "}", "int main(void) {", PF("%d", "f($k)"), "}"),
      lambda p: {3: 7, 2: 6, 1: 4}[p["k"]], "f(3) adds 1 + 2 + 4, f(2) adds 2 + 4, f(1) adds 4."),
    C(T("int x = $a;", "switch (x) {", '    printf("never");', 'case 2: printf("a"); break;', 'default: printf("d");', "}", 'printf(".");'),
      lambda p: ("a" if p["a"] == 2 else "d") + ".", "A statement before the first case is never reached: execution jumps straight to a label."),
    C(T("int x = $a;", "switch (x) {", "case 2: {", "    int t = x * 3;", '    printf("%d", t);', "    break;", "}", 'default: printf("d");', "}", 'printf(".");'),
      lambda p: (str(p["a"] * 3) if p["a"] == 2 else "d") + ".", "A case may open a block with its own variable; only x of 2 enters it."),
    C(T("int x = $a, y = $k;", "switch (x) {", 'case 2: if (y > 1) break; printf("a");', 'case 3: printf("b");', "}", 'printf(".");'),
      lambda p: (("" if p["k"] > 1 else "ab") if p["a"] == 2 else ("b" if p["a"] == 3 else "")) + ".", "A break inside an if still leaves the switch; without it case 2 runs on into case 3."),
    C(T("int s = $q, n = 0;", "while (s != 3) {", "    switch (s) {", "    case 0: s = 2; break;", "    case 2: s = 1; break;", "    case 1: s = 3;", "    }", "    n++;", "}", PF("%d", "n")),
      lambda p: _machine(p["q"]), "A small state machine: 0 goes to 2, 2 to 1, 1 to 3. Count the turns until 3."),
    C(T("int x = $a;", "switch (x++) {", 'case 2: printf("a"); break;', 'default: printf("d");', "}", 'printf("%d", x);'),
      lambda p: ("a" if p["a"] == 2 else "d") + str(p["a"] + 1), "x++ gives the old value to the switch, then x grows."),
    C(T('const char *s = "$w";', "switch (s[$i]) {", "case 'a': case 'e': case 'i': case 'o': case 'u': printf(\"V\"); break;", 'default: printf("C");', "}"),
      lambda p: "V" if p["w"][p["i"]] in "aeiou" else "C", "The switch tests one letter of the word: a vowel or not."),
]
