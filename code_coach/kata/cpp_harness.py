"""The kata driver for C++.

Like the C driver, this one is generated: one block of C++ per case, with
that case's arguments written out as C++ literals, the call, and a line
printing the result as JSON. The wire format is the C one - a CASE-marked
line per case, then DONE - and `unpack` turns those lines back into the
single results line `judge` reads, so the runner needs no C++-specific
parsing beyond that.

What a C++ kata can take and give
---------------------------------
Types, one per parameter in `Kata.types` and one in `Kata.returns`
(a leading `std::` is accepted and ignored):

  int, long long, double, bool        the value as it is
  string                              std::string
  vector<int>, vector<long long>      std::vector of those
  vector<double>, vector<bool>
  vector<string>                      std::vector<std::string>

`int[]` and `string[]` are accepted as other names for the two common
vectors. Every argument is an lvalue, so the function may take it by
value, by const reference or by reference - whichever the code needs.

Failures
--------
A C++ function that throws is caught per case and reported against that
case, like an exception in the other languages. A crash (a bad index
into a vector's data, a null pointer) kills the whole program instead;
each case prints its line as soon as it has run, so `unpack` can say
which input crashed it, and that the rest were not run.

Mutation is checked as in C: each container or string argument is copied
before the call and compared after, so a function that sorts the vector
it was given fails even when its answer is right.
"""

from __future__ import annotations

import json
import re

#: Same wire format as the C driver.
CASE = "<<<KATACASE>>>"
DONE = "<<<KATADONE>>>"

SCALARS = {"int", "long long", "double", "bool"}
VECTORS = {"vector<int>", "vector<long long>", "vector<double>",
           "vector<bool>", "vector<string>"}
ALIASES = {"int[]": "vector<int>", "string[]": "vector<string>",
           "long": "long long"}


def norm(kind: str) -> str:
    """One spelling per type: `std::vector< int >` and `vector<int>` agree."""
    kind = (kind or "int").strip().replace("std::", "")
    kind = re.sub(r"\s+", " ", kind)
    kind = re.sub(r"\s*<\s*", "<", kind)
    kind = re.sub(r"\s*>", ">", kind)
    return ALIASES.get(kind, kind)


def cpp_type(kind: str) -> str:
    """The type as written in C++."""
    kind = norm(kind)
    if kind == "string":
        return "std::string"
    if kind.startswith("vector<"):
        inner = kind[len("vector<"):-1]
        return f"std::vector<{cpp_type(inner)}>"
    return kind


def param_decl(kind: str, name: str) -> str:
    kind = norm(kind)
    if kind == "string" or kind.startswith("vector<"):
        return f"const {cpp_type(kind)} &{name}"
    return f"{kind} {name}"


def signature(kata) -> str:
    """The line the box opens on, e.g. `int sumOf(const std::vector<int> &nums) {`."""
    kinds = list(kata.types) + ["int"] * (len(kata.params) - len(kata.types))
    parts = [param_decl(k, p) for k, p in zip(kinds, kata.params)]
    return f"{cpp_type(kata.returns or 'int')} {kata.name}({', '.join(parts)}) {{"


# ── Writing values as C++ ────────────────────────────────────


def _cpp_string(value: str) -> str:
    """A string literal. Printable ASCII is written as itself; every other
    byte of the UTF-8 is a three-digit octal escape, so the literal means
    the same bytes whatever the compiler thinks the source encoding is."""
    out = ['"']
    for byte in str(value).encode("utf-8"):
        ch = chr(byte)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "?":
            out.append("\\?")  # never a trigraph
        elif 0x20 <= byte < 0x7F:
            out.append(ch)
        else:
            out.append(f"\\{byte:03o}")
    out.append('"')
    return "".join(out)


def _literal(kind: str, value) -> str:
    kind = norm(kind)
    if kind == "bool":
        return "true" if value else "false"
    if kind == "long long":
        return f"{int(value)}LL"
    if kind == "double":
        return repr(float(value))
    if kind == "string":
        return _cpp_string(value)
    return str(int(value))


def _value(kind: str, value) -> str:
    kind = norm(kind)
    if kind.startswith("vector<"):
        inner = kind[len("vector<"):-1]
        items = ", ".join(_value(inner, v) for v in value)
        return f"{cpp_type(kind)}{{{items}}}"
    if kind == "string":
        return f"std::string({_cpp_string(value)})"
    return _literal(kind, value)


def _setup(kind: str, name: str, value):
    """(lines before the call, lines after it, the argument text)."""
    kind = norm(kind)
    if kind == "string" or kind.startswith("vector<"):
        t = cpp_type(kind)
        before = [f"{t} {name} = {_value(kind, value)};", f"const {t} {name}_was = {name};"]
        after = [f"if ({name} != {name}_was) changed = true;"]
        return before, after, name
    return [], [], _literal(kind, value)


def _print_result() -> list[str]:
    return [
        'std::printf("{\\"got\\": ");',
        "_kata_out(result);",
        'std::printf(", \\"changed\\": %s}\\n", changed ? "true" : "false");',
    ]


HEADERS = (
    "#include <algorithm>\n#include <cctype>\n#include <climits>\n#include <cmath>\n"
    "#include <cstdint>\n#include <cstdio>\n#include <cstdlib>\n#include <cstring>\n"
    "#include <exception>\n#include <iostream>\n#include <map>\n#include <set>\n"
    "#include <sstream>\n#include <string>\n#include <unordered_map>\n"
    "#include <unordered_set>\n#include <utility>\n#include <vector>\n#line 1\n"
)

PRELUDE = r"""

// ── the marker ─────────────────────────────────────────────
static void _kata_out(bool v) { std::printf(v ? "true" : "false"); }
static void _kata_out(int v) { std::printf("%d", v); }
static void _kata_out(long long v) { std::printf("%lld", v); }
static void _kata_out(double v) {
    if (v != v || v - v != 0) std::printf("null");
    else std::printf("%.17g", v);
}
static void _kata_out(const std::string &s) {
    std::putchar('"');
    for (unsigned char c : s) {
        if (c == '"' || c == '\\') std::printf("\\%c", c);
        else if (c == '\n') std::printf("\\n");
        else if (c == '\t') std::printf("\\t");
        else if (c < 0x20) std::printf("\\u%04x", c);
        else std::putchar(c);
    }
    std::putchar('"');
}
template <typename T>
static void _kata_out(const std::vector<T> &items) {
    std::putchar('[');
    for (std::size_t i = 0; i < items.size(); i++) {
        if (i) std::printf(", ");
        _kata_out(static_cast<T>(items[i]));
    }
    std::putchar(']');
}
static void _kata_error(const std::string &why) {
    std::printf("\n<<<KATACASE>>>{\"error\": ");
    _kata_out(why);
    std::printf("}\n");
}

int main() {
    std::setvbuf(stdout, nullptr, _IONBF, 0);
"""


def harness(kata, code: str) -> str:
    """The student's code, then a main() that calls it once per case."""
    returns = norm(kata.returns or "int")
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
        lines = ["try {", "    bool changed = false;"]
        lines += ["    " + line for line in before]
        lines.append(f"    {cpp_type(returns)} result = {kata.name}({', '.join(args)});")
        lines += ["    " + line for line in after]
        # The marker is printed only once the call has returned, so a
        # crash leaves no half-written case line behind.
        lines.append(f'    std::printf("\\n{CASE}");')
        lines += ["    " + line for line in _print_result()]
        lines += [
            "} catch (const std::exception &e) {",
            '    _kata_error(std::string("threw an exception: ") + e.what());',
            "} catch (...) {",
            '    _kata_error("threw something that is not a std::exception");',
            "}",
        ]
        body.append("    {\n" + "\n".join("        " + line for line in lines) + "\n    }")
    return (HEADERS + code.rstrip() + "\n" + PRELUDE + "\n".join(body)
            + f'\n    std::printf("\\n{DONE}\\n");\n    return 0;\n}}\n')


# ── Reading it back ──────────────────────────────────────────

#: A crash as an exit code: SIGSEGV / SIGABRT on POSIX; an access
#: violation, a stack overflow, a fast-fail or abort() on Windows.
CRASH_CODES = {-11, 139, -6, 134, 3, 3221225477, -1073741819, 3221225725,
               -1073741571, 3221226505, -1073740791}


def missing(kata, stdout: str, stderr: str) -> bool:
    """The compiler saying there is no such function."""
    if CASE in stdout:
        return False
    text = stderr or ""
    name = kata.name
    return any(phrase in text for phrase in (
        f"'{name}' was not declared in this scope",
        f"use of undeclared identifier '{name}'",
        f"'{name}': identifier not found",
        f"undefined reference to `{name}(",
        f"unresolved external symbol {name}",
    ))


def unpack(kata, stdout: str, stderr: str, exit_code: int, marker: str):
    """Per-case lines back into the one results line `judge` reads.

    A program that never printed a case line - a compile error - is
    returned untouched, so judge reports it the ordinary way.
    """
    lines = [line[len(CASE):] for line in stdout.splitlines() if line.startswith(CASE)]
    if not lines and DONE not in stdout:
        if not (exit_code in CRASH_CODES
                or (exit_code != 0 and not re.search(r"error", stderr or "", re.I))):
            return stdout
    results = []
    for line in lines:
        try:
            results.append(json.loads(line))
        except ValueError:
            results.append({"error": "printed something the marker could not read"})
    if DONE not in stdout and len(results) < len(kata.cases):
        why = (f"crashed on this input (exit code {exit_code}) - most often "
               f"reading past the end of a vector or through a null pointer")
        results.append({"error": why})
        while len(results) < len(kata.cases):
            results.append({"error": "not run - the program had already crashed"})
    return stdout + "\n" + marker + json.dumps(results) + "\n"
