"""Printing, in sixteen more languages.

The workbook's first page is one shape: print this line. It is the only
shape here, because a language earns its second page by having a toolchain
that can prove the first one right, and most of these do not have one on
this machine yet.

Four of them do. Go, PHP, Lua and Zig were installed with their published
checksums checked, and every exercise they serve is run and compared the
same way every other page in the book is. The other twelve are written and
switched off: `RUNNABLE` is the list the workbook is told about, and a
language absent from it is offered no pages at all, however complete its
emitter looks below.

That split is deliberate. A reference answer that has never executed is
worse than a missing language, because the app would tell someone their
correct program was wrong and neither of you could say which was at fault.
When a toolchain arrives, add the name to RUNNABLE, run the suite, and the
page appears.

The Zig ceremony is not an accident of style. Zig 0.16 rewrote its IO, so
reaching stdout now needs an allocator, a threaded IO instance, a buffer, a
writer and an explicit flush. std.debug.print is three lines shorter and
writes to stderr, which would leave stdout empty and every exercise
silently failing. This is what printing costs in that version.
"""

from __future__ import annotations

#: Languages whose toolchain is present and whose answers are executed by
#: the suite. Everything else in this file is written but not offered.
RUNNABLE: tuple[str, ...] = ("go", "php", "lua", "zig")

#: Written, checked by eye, never executed here. Moving a name into
#: RUNNABLE is a claim that the suite can now prove it.
UNVERIFIED: tuple[str, ...] = (
    "java", "kotlin", "ruby", "csharp", "swift", "scala",
    "haskell", "ocaml", "elixir", "lisp", "odin", "assembly",
)

LANGUAGES: tuple[str, ...] = RUNNABLE + UNVERIFIED

SHAPE = "print_text"

_NL = chr(92) + "n"          # a backslash and an n, for languages that want one
_Q = '"'


def _escaped(text: str) -> str:
    """The text as a double-quoted literal, for the C-like majority."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _single(text: str) -> str:
    """The text as a single-quoted literal, for Lisp and the shells of PHP."""
    return text.replace("\\", "\\\\").replace("'", "\\'")


def _go(text: str) -> str:
    return (
        "package main\n"
        "\n"
        'import "fmt"\n'
        "\n"
        "func main() {\n"
        f'\tfmt.Println("{_escaped(text)}")\n'
        "}\n"
    )


def _php(text: str) -> str:
    return "<?php\n" f'echo "{_escaped(text)}{_NL}";\n'


def _lua(text: str) -> str:
    return f'print("{_escaped(text)}")\n'


def _zig(text: str) -> str:
    return (
        'const std = @import("std");\n'
        "\n"
        "pub fn main() !void {\n"
        "    var threaded: std.Io.Threaded = "
        ".init(std.heap.page_allocator, .{});\n"
        "    defer threaded.deinit();\n"
        "    const io = threaded.io();\n"
        "    var buf: [256]u8 = undefined;\n"
        "    var w = std.Io.File.stdout().writer(io, &buf);\n"
        "    const out = &w.interface;\n"
        f'    try out.print("{_escaped(text)}{_NL}", .{{}});\n'
        "    try out.flush();\n"
        "}\n"
    )


def _java(text: str) -> str:
    return (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        f'        System.out.println("{_escaped(text)}");\n'
        "    }\n"
        "}\n"
    )


def _kotlin(text: str) -> str:
    return "fun main() {\n" f'    println("{_escaped(text)}")\n' "}\n"


def _ruby(text: str) -> str:
    return f'puts "{_escaped(text)}"\n'


def _csharp(text: str) -> str:
    return f'System.Console.WriteLine("{_escaped(text)}");\n'


def _swift(text: str) -> str:
    return f'print("{_escaped(text)}")\n'


def _scala(text: str) -> str:
    return "@main def run(): Unit =\n" f'  println("{_escaped(text)}")\n'


def _haskell(text: str) -> str:
    return "main :: IO ()\n" f'main = putStrLn "{_escaped(text)}"\n'


def _ocaml(text: str) -> str:
    return f'let () = print_endline "{_escaped(text)}"\n'


def _elixir(text: str) -> str:
    return f'IO.puts("{_escaped(text)}")\n'


def _lisp(text: str) -> str:
    return f'(format t "~a~%" "{_escaped(text)}")\n'


def _odin(text: str) -> str:
    return (
        'package main\n\nimport "core:fmt"\n\n'
        "main :: proc() {\n"
        f'\tfmt.println("{_escaped(text)}")\n'
        "}\n"
    )


def _assembly(text: str) -> str:
    """x86-64 Linux, NASM syntax, writing straight to file descriptor one.

    Assembly has no println, so the whole of it is here: the bytes in a
    data section, their length worked out by the assembler, and a write
    syscall followed by an exit one.
    """
    body = _escaped(text)
    return (
        "section .data\n"
        f'    msg db "{body}", 10\n'
        "    len equ $ - msg\n"
        "\n"
        "section .text\n"
        "    global _start\n"
        "\n"
        "_start:\n"
        "    mov rax, 1\n"
        "    mov rdi, 1\n"
        "    mov rsi, msg\n"
        "    mov rdx, len\n"
        "    syscall\n"
        "\n"
        "    mov rax, 60\n"
        "    xor rdi, rdi\n"
        "    syscall\n"
    )


_BUILDERS = {
    "go": _go,
    "php": _php,
    "lua": _lua,
    "zig": _zig,
    "java": _java,
    "kotlin": _kotlin,
    "ruby": _ruby,
    "csharp": _csharp,
    "swift": _swift,
    "scala": _scala,
    "haskell": _haskell,
    "ocaml": _ocaml,
    "elixir": _elixir,
    "lisp": _lisp,
    "odin": _odin,
    "assembly": _assembly,
}


def handles(shape: str) -> bool:
    return shape == SHAPE


def solution(language: str, shape: str, args: dict) -> str | None:
    """The reference answer, but only for a language the suite can check.

    UNVERIFIED languages return None on purpose, which is what keeps their
    pages out of the book: `pages()` drops any page whose first exercise
    has no answer in the language asked for.
    """
    if shape != SHAPE or language not in RUNNABLE:
        return None
    build = _BUILDERS.get(language)
    return build(args["text"]) if build else None


def draft(language: str, text: str) -> str | None:
    """What the answer would be, verified or not.

    Separate from `solution` so that nothing can serve an unchecked
    program by accident, while the drafts stay readable and testable as
    text.
    """
    build = _BUILDERS.get(language)
    return build(text) if build else None
