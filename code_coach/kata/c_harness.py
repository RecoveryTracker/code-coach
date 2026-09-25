"""The kata driver for C.

The other drivers call the student's function from a loop over JSON
cases. C cannot read JSON without a library, so this driver is
generated instead: one block of C per case, with that case's arguments
written out as C literals, the call, and a line printing the result.

What a C kata can take and give
-------------------------------
Parameter types, one per parameter in `Kata.types`:

  int, long long, double, bool, char     the value as it is
  string                                 const char *
  int[]                                  const int *name, int name_len
  string[]                               const char **name, int name_len

An array arrives as a pointer and a length, because that is how C
passes one - there is no other way to know how long it is.

Return types, in `Kata.returns`:

  int, long long, double, bool, char     printed as they are
  string                                 const char *; NULL is null
  int[]                                  the function writes into an
                                         extra `int *out` parameter and
                                         returns how many it wrote -
                                         the usual C shape for "give me
                                         a list"

Crashes
-------
A C function cannot raise an exception the driver catches: reading past
an array or through NULL kills the whole program. So each case prints
its own line as soon as it has run, and `unpack` turns those lines back
into the one results list `judge` reads. When the lines stop early, the
case after the last one printed is the one that crashed, and it is
reported against that input - which is the most useful thing to know
about a crash.

Mutation is checked as in the other languages: an int[] argument is
copied before the call and compared after, so a function that sorts the
array it was given fails even when its answer is right.
"""

from __future__ import annotations

import json
import re

#: One of these per case, printed as soon as the case has run.
CASE = "<<<KATACASE>>>"
#: Printed once every case has run.
DONE = "<<<KATADONE>>>"
#: The most an int[] result can hold.
OUT_MAX = 256

SCALARS = {"int", "long long", "double", "bool", "char"}


def param_decl(kind: str, name: str) -> str:
    """How one parameter is written in the signature."""
    kind = kind.strip()
    if kind == "string":
        return f"const char *{name}"
    if kind == "int[]":
        return f"const int *{name}, int {name}_len"
    if kind == "string[]":
        return f"const char **{name}, int {name}_len"
    return f"{kind} {name}"


def return_decl(kind: str) -> str:
    kind = (kind or "int").strip()
    if kind == "string":
        return "const char *"
    if kind == "int[]":
        return "int"
    return kind


def signature(kata) -> str:
    """The line the box opens on, e.g. `int sumOf(const int *nums, int nums_len) {`."""
    parts = [param_decl(k, p) for k, p in zip(kata.types, kata.params)]
    if (kata.returns or "").strip() == "int[]":
        parts.append("int *out")
    returns = return_decl(kata.returns)
    space = "" if returns.endswith("*") else " "
    return f"{returns}{space}{kata.name}({', '.join(parts)}) {{"


# ── Writing values as C ──────────────────────────────────────


def _c_string(value: str) -> str:
    # JSON's escapes are C's escapes for everything a test case uses:
    # \" \\ \n \t, and \uXXXX, which C accepts as a universal character.
    return json.dumps(value, ensure_ascii=True)


def _literal(kind: str, value) -> str:
    kind = kind.strip()
    if kind == "bool":
        return "true" if value else "false"
    if kind == "long long":
        return f"{int(value)}LL"
    if kind == "double":
        return repr(float(value))
    if kind == "char":
        return str(ord(value)) if isinstance(value, str) else str(int(value))
    if kind == "string":
        return _c_string(value)
    return str(int(value))


def _setup(kind: str, name: str, value) -> tuple[list[str], list[str], str]:
    """(lines before the call, lines after it, the argument text)."""
    kind = kind.strip()
    if kind == "int[]":
        items = ", ".join(str(int(v)) for v in value) or "0"
        size = max(len(value), 1)
        before = [
            f"int {name}[{size}] = {{{items}}};",
            f"int {name}_was[{size}];",
            f"memcpy({name}_was, {name}, sizeof {name});",
        ]
        after = [f"if (memcmp({name}_was, {name}, sizeof {name}) != 0) changed = 1;"]
        return before, after, f"{name}, {len(value)}"
    if kind == "string[]":
        items = ", ".join(_c_string(v) for v in value) or "NULL"
        size = max(len(value), 1)
        return [f"const char *{name}[{size}] = {{{items}}};"], [], f"{name}, {len(value)}"
    return [], [], _literal(kind, value)


def _print_result(kind: str) -> list[str]:
    kind = (kind or "int").strip()
    if kind == "int[]":
        return [
            f"if (count < 0 || count > {OUT_MAX}) {{",
            f'  printf("{{\\"error\\": \\"returned a count of %d, which is not how '
            f'many it wrote\\"}}\\n", count);',
            "} else {",
            '  printf("{\\"got\\": [");',
            '  for (int i = 0; i < count; i++) printf(i ? ", %d" : "%d", out[i]);',
            '  printf("], \\"changed\\": %s}\\n", changed ? "true" : "false");',
            "}",
        ]
    formats = {
        "int": ('"%d"', "result"),
        "char": ('"%d"', "(int)result"),
        "long long": ('"%lld"', "result"),
        "double": ('"%.17g"', "result"),
        "bool": ('"%s"', 'result ? "true" : "false"'),
    }
    if kind == "string":
        return [
            'printf("{\\"got\\": ");',
            "_kata_str(result);",
            'printf(", \\"changed\\": %s}\\n", changed ? "true" : "false");',
        ]
    fmt, arg = formats.get(kind, formats["int"])
    return [
        'printf("{\\"got\\": ");',
        f"printf({fmt}, {arg});",
        'printf(", \\"changed\\": %s}\\n", changed ? "true" : "false");',
    ]


PRELUDE = r"""

/* ── the marker ─────────────────────────────────────────── */
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

static void _kata_str(const char *s) {
    if (s == NULL) { printf("null"); return; }
    putchar('"');
    for (; *s; s++) {
        unsigned char c = (unsigned char)*s;
        if (c == '"' || c == '\\') printf("\\%c", c);
        else if (c == '\n') printf("\\n");
        else if (c == '\t') printf("\\t");
        else if (c < 0x20) printf("\\u%04x", c);
        else putchar(c);
    }
    putchar('"');
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
"""


def harness(kata, code: str) -> str:
    """The student's code, then a main() that calls it once per case.

    The driver's includes come after the student's code, which C allows
    at file scope, so the student's line numbers are the compiler's.
    """
    returns = (kata.returns or "int").strip()
    kinds = list(kata.types) + ["int"] * (len(kata.params) - len(kata.types))
    body: list[str] = []
    for case in kata.cases:
        before: list[str] = []
        after: list[str] = []
        args: list[str] = []
        for i, (kind, value) in enumerate(zip(kinds, case)):
            b, a, text = _setup(kind, f"a{i}", value)
            before += b
            after += a
            args.append(text)
        call_args = ", ".join(args)
        lines = ["int changed = 0;", *before]
        if returns == "int[]":
            lines.append(f"int out[{OUT_MAX}];")
            call = f"{kata.name}({call_args}{', ' if call_args else ''}out)"
            lines.append(f"int count = {call};")
        else:
            lines.append(f"{return_decl(returns)} result = {kata.name}({call_args});")
        lines += after
        lines.append(f'printf("{CASE}");')
        lines += _print_result(returns)
        body.append("    {\n" + "\n".join("        " + line for line in lines) + "\n    }")
    return (code.rstrip() + "\n" + PRELUDE + "\n".join(body)
            + f'\n    printf("{DONE}\\n");\n    return 0;\n}}\n')


# ── Reading it back ──────────────────────────────────────────

#: What a crash looks like in an exit code: SIGSEGV on POSIX, an access
#: violation or a stack overflow on Windows.
CRASH_CODES = {-11, 139, 3221225477, -1073741819, 3221225725, -1073741571}


def missing(kata, stdout: str, stderr: str) -> bool:
    """The compiler or linker saying there is no such function."""
    if CASE in stdout:
        return False
    text = stderr or ""
    name = kata.name
    return any(phrase in text for phrase in (
        f"undeclared function '{name}'",
        f"implicit declaration of function '{name}'",
        f"undefined reference to `{name}'",
        f"unresolved external symbol {name}",
        f"undefined symbol: {name}",
    ))


def unpack(kata, stdout: str, stderr: str, exit_code: int, marker: str):
    """Per-case lines back into the one results line `judge` reads.

    Returns the stdout judge should see. A program that never printed a
    case line - a compile error - is returned untouched, so judge
    reports it the ordinary way.
    """
    lines = [line[len(CASE):] for line in stdout.splitlines() if line.startswith(CASE)]
    if not lines and DONE not in stdout:
        if exit_code in CRASH_CODES or (exit_code != 0 and not re.search(r"error", stderr or "", re.I)):
            lines = []  # crashed on the very first case - fall through
        else:
            return stdout
    results = []
    for line in lines:
        try:
            results.append(json.loads(line))
        except ValueError:
            results.append({"error": "printed something the marker could not read"})
    if DONE not in stdout and len(results) < len(kata.cases):
        why = (f"crashed on this input (exit code {exit_code}) - most often "
               f"reading past the end of an array or through a NULL pointer")
        results.append({"error": why})
        while len(results) < len(kata.cases):
            results.append({"error": "not run - the program had already crashed"})
    return stdout + "\n" + marker + json.dumps(results) + "\n"
