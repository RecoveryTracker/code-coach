"""The registry of languages the Gotchas quiz can ask about.

One entry per language: what the quiz is called, the file extension, the id prefix of its cards, which content
modules hold its deck, patterns that must not appear in a card (so the answer is the same on every machine and
on every run), a keyword set for the syntax colourer, and a line of advice for whoever writes its cards.

Nothing here knows how to *run* a program: that is `toolchains.py`. Nothing here lists the cards: the decks are
found by `gotchas/__init__.py`, which imports `content_<module>` and `content_<module>2`, `3`... by name, so a
content author adds a deck by creating a file and touching nothing else.

Adding a language: one `Lang(...)` below, one way to run it in `toolchains.py`, and its deck.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Syntax:
    """What the browser's colourer needs to know about a language (sent to it by /api/gotchas)."""

    keywords: tuple[str, ...] = ()
    types: tuple[str, ...] = ()
    consts: tuple[str, ...] = ()
    #: What starts a comment that runs to the end of the line.
    line_comments: tuple[str, ...] = ("//",)
    #: (open, close) pairs of comments that can span lines.
    block_comments: tuple[tuple[str, str], ...] = (("/*", "*/"),)
    #: Characters that open a string ("`" is a string that may span lines).
    quotes: str = "\"'"
    #: Python and friends: triple-quoted strings (and Python's f/r/b prefixes).
    triple: bool = False
    #: Python's string prefixes (rb"..", f'..').
    prefixes: bool = False
    #: Lines that start with # are directives (C, C++, C#), not comments.
    directives: bool = False
    #: A ' only opens a string when it closes again within a few characters ('a', '\n'), so Rust's
    #: lifetimes ('a) and Lisp's quote ('(1 2)) are not read as the start of a string.
    char_literals: bool = False
    #: Names are matched ignoring case (SQL).
    ignore_case: bool = False
    #: Lisp reads: a word is anything up to a space, bracket, quote or comment; the name after "(" is a call.
    lisp: bool = False

    def payload(self) -> dict:
        return {
            "keywords": list(self.keywords), "types": list(self.types), "consts": list(self.consts),
            "line": list(self.line_comments), "block": [list(p) for p in self.block_comments],
            "quotes": self.quotes, "triple": self.triple, "prefixes": self.prefixes,
            "directives": self.directives, "charLiterals": self.char_literals,
            "ignoreCase": self.ignore_case, "lisp": self.lisp,
        }


#: (regex, why) - a card whose program matches one of these is refused by the content test.
Banned = tuple[str, str]


@dataclass(frozen=True)
class Lang:
    id: str
    name: str
    #: The prefix of every card id of this language: py-score-90, rs-shadowing.
    prefix: str
    #: The source file's extension, without the dot.
    ext: str
    syntax: Syntax
    #: Patterns that make a program non-portable or non-deterministic. Checked against every built-in card.
    banned: tuple[Banned, ...] = ()
    #: One line for whoever writes this language's cards: what to avoid and why.
    notes: str = ""
    #: A regex for reading from stdin (a pasted card that does that is refused: nobody answers it).
    reads_input: str = ""
    #: Decks are the modules content_<module>, content_<module>2, content_<module>3... (default: the id).
    module: str = ""
    #: What the routes say when the toolchain is missing ("<this>, so the C quiz is not available..."); blank is
    #: "No <name> toolchain is installed".
    missing: str = ""
    #: Whether a card may be a `raises` card (the answer is the name of the uncaught error).
    raises: bool = False
    #: The language's easy way to print writes to stderr (Zig's std.debug.print): on a clean exit the runner
    #: reports what the program wrote there as its output.
    output_on_stderr: bool = False
    #: A second, free-form check on a card's program: returns the reason it is refused, or None.
    check: Callable[[str], str | None] | None = field(default=None, compare=False)

    @property
    def title(self) -> str:
        return f"{self.name} Quiz"

    @property
    def content(self) -> str:
        """The module name stem: content_<this>, content_<this>2..."""
        return self.module or self.id

    def problems(self, code: str) -> list[str]:
        """Why this program may not be a built-in card (empty: it may)."""
        found = [why for pattern, why in self.banned if re.search(pattern, code)]
        if self.check is not None:
            extra = self.check(code)
            if extra:
                found.append(extra)
        return found


def _words(text: str) -> tuple[str, ...]:
    return tuple(text.split())


# ── Banned patterns shared by many languages ─────────────────────────────

_ADDR = (r"0x[0-9a-fA-F]{8,}", "prints something that looks like a memory address")


def _go_map_range(code: str) -> str | None:
    """Ranging over a map is in random order: only allowed when the program also sorts."""
    if re.search(r"\bmap\[", code) and re.search(r"\bfor\b[^\n]*\brange\b", code) and "sort." not in code:
        return "ranges over what may be a map (random order); sort the keys first"
    return None


def _swift_dictionary(code: str) -> str | None:
    if re.search(r"\[\s*(\"[^\"\n]*\"|\d+|\.\w+)\s*:\s*[^\]\n]", code) or re.search(r":\s*\[\s*\w+\s*:\s*\w+\s*\]", code):
        return "uses a Dictionary (its order is randomised for every run); print one key, or sort"
    return None


LANGS: tuple[Lang, ...] = (
    Lang(
        id="python", name="Python", prefix="py", ext="py", module="py", raises=True,
        syntax=Syntax(
            keywords=_words("and as assert async await break class continue def del elif else except finally for "
                            "from global if import in is lambda nonlocal not or pass raise return try while with "
                            "yield match case"),
            consts=_words("True False None"), line_comments=("#",), block_comments=(), triple=True, prefixes=True),
        banned=(
            (r"\brandom\b", "uses randomness"), (r"\btime\b|\bdatetime\b", "reads the clock"),
            (r"\bid\(|\bhash\(", "prints an identity or a hash (differs between runs)"),
            (r"\bos\.environ\b|\bsys\.argv\b", "reads the environment"), (r"\binput\(", "waits for input"),
        ),
        notes="No id(), hash(), set/dict-of-str order dependence (PYTHONHASHSEED varies), random, time or input; "
              "one print() line; raises=True cards must print nothing first.",
        reads_input=r"\binput\s*\(",
    ),
    Lang(
        id="javascript", name="JavaScript", prefix="js", ext="js", module="js", raises=True,
        syntax=Syntax(
            keywords=_words("async await break case catch class const continue default delete do else export "
                            "extends finally for from function if import in instanceof let new of return static "
                            "super switch this throw try typeof var void while with yield"),
            consts=_words("true false null undefined NaN Infinity"), quotes="\"'`"),
        banned=(
            (r"\bMath\.random\b", "uses randomness"),
            (r"\bDate\.now\b|\bnew Date\(\s*\)|\bDate\(\s*\)|\btime\b", "reads the clock"),
            (r"\bprocess\.argv\b|\bprocess\.env\b", "reads the environment"),
            (r"\bprompt\s*\(|\breadline\b", "waits for input"),
        ),
        notes="Runs as a CommonJS script on whatever node is installed (no top-level var, no window); event-loop "
              "cards collect steps into an array and print once; a fixed Date.UTC(...) is fine, Date.now() is not.",
        reads_input=r"\b(prompt|readline)\s*\(",
    ),
    Lang(
        id="typescript", name="TypeScript", prefix="ts", ext="ts",
        syntax=Syntax(
            keywords=_words("abstract as async await break case catch class const continue declare default delete "
                            "do else enum export extends finally for from function if implements import in "
                            "instanceof interface keyof let namespace new of private protected public readonly "
                            "return satisfies static super switch this throw try type typeof var void while "
                            "yield"),
            types=_words("string number boolean any unknown never object symbol bigint void Array Record Partial "
                         "Readonly Promise Map Set"),
            consts=_words("true false null undefined NaN Infinity"), quotes="\"'`"),
        banned=(
            (r"\bMath\.random\b", "uses randomness"),
            (r"\bDate\.now\b|\bnew Date\(\s*\)|\bDate\(\s*\)|\bperformance\.now\b", "reads the clock"),
            (r"\bprocess\.(argv|env|stdin)\b|\brequire\s*\(", "reads the environment / needs node typings"),
        ),
        notes="Compiled with tsc --strict --target es2020 (a type error is a compile error, and the library is "
              "ES2020: no Array.at, structuredClone, Object.hasOwn) then run by node; the file is a global script, "
              "so keep names out of the global scope (wrap in a function or end with `export {}`); console.log "
              "one line.",
        reads_input=r"\b(prompt|readline)\s*\(|process\.stdin",
    ),
    Lang(
        id="c", name="C", prefix="c", ext="c", module="c",
        missing="No C compiler is installed (gcc, clang or Visual Studio)",
        syntax=Syntax(
            keywords=_words("auto break case const continue default do else enum extern for goto if inline "
                            "register restrict return sizeof static struct switch typedef union volatile while"),
            types=_words("void char short int long float double signed unsigned bool _Bool size_t ssize_t "
                         "ptrdiff_t FILE int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t "
                         "intptr_t uintptr_t intmax_t uintmax_t"),
            consts=_words("NULL true false EOF UINT_MAX INT_MAX INT_MIN CHAR_BIT"), directives=True),
        banned=(
            (r"%p", "prints a pointer"), (r"\brand\b|\bsrand\b", "uses randomness"),
            (r"\btime\b|\bclock\b", "reads the clock"), (r"\bgetenv\b|\bargv\b|\bargc\b", "reads the environment"),
            (r"\bscanf\b|\bgets\b|\bfgets\b|\bgetchar\b", "waits for input"),
            (r"\b__\w+|#pragma|\basm\b", "compiler-specific"),
            (r"\bsizeof\s*\(\s*(?:long|short|void)\b", "a size that differs between systems"),
            (r"\bINT_MAX\b|\bINT_MIN\b|\bLONG_MAX\b|\bLONG_MIN\b", "a limit that differs between systems"),
            (r"\bmalloc\b|\bgoto\b|\bsignal\b|\bsetjmp\b|\bFILE\b|\bfopen\b|\bsystem\b|\bunion\b|\boffsetof\b",
             "not portable"),
            (r"\bpthread|\bthread_local\b|\b_Thread|\bwchar|\blocale", "not portable"),
        ),
        notes="Portable C only: no undefined behaviour (overflow, out-of-bounds, uninitialised, unsequenced), "
              "nothing implementation-defined (plain char signedness, sizeof(long), padding, %p), ONE printed "
              "line, no raises cards; it is built with clang/gcc/MSVC and must agree everywhere.",
        reads_input=r"\b(scanf|fscanf|getchar|getc|fgets|gets|fgetc)\s*\(",
    ),
    Lang(
        id="cpp", name="C++", prefix="cpp", ext="cpp",
        syntax=Syntax(
            keywords=_words("alignas alignof auto break case catch class const consteval constexpr continue "
                            "decltype default delete do else enum explicit export extern for friend goto if "
                            "inline mutable namespace new noexcept operator override private protected public "
                            "register return sizeof static static_assert struct switch template this throw try "
                            "typedef typeid typename union using virtual volatile while"),
            types=_words("void char short int long float double signed unsigned bool size_t string vector map "
                         "set array pair tuple optional unique_ptr shared_ptr int8_t int16_t int32_t int64_t "
                         "uint8_t uint16_t uint32_t uint64_t wchar_t char16_t char32_t"),
            consts=_words("nullptr NULL true false EOF"), directives=True),
        banned=(
            (r"%p|\(void\s*\*\)|<<\s*&", "prints a pointer"),
            (r"\brand\b|\bsrand\b|\bmt19937\b|\brandom_device\b|<random>", "uses randomness"),
            (r"\btime\b|\bclock\b|<chrono>|\bchrono::", "reads the clock"),
            (r"\bgetenv\b|\bargv\b|\bargc\b", "reads the environment"),
            (r"\bcin\b|\bscanf\b|\bgets\b|\bgetline\b|\bgetchar\b", "waits for input"),
            (r"\bunordered_(map|set|multimap|multiset)\b", "iteration order is unspecified; use map/set"),
            (r"\btypeid\b|\bstd::hash\b|\bfunction_name\b", "implementation-defined"),
            (r"\b__\w+|#pragma|\basm\b", "compiler-specific"),
            (r"\bsizeof\s*\(\s*(?:long|short|void|wchar_t|size_t|bool)\b", "a size that differs between systems"),
            (r"\bthread\b|\basync\b|\bmutex\b|\batomic\b|\bsignal\b|\bsetjmp\b|\bfopen\b|\bsystem\s*\(",
             "not portable"),
        ),
        notes="Built as C++17 (clang++/g++/MSVC) and run once: no undefined behaviour (signed overflow, "
              "out-of-bounds, dangling references, unsequenced writes), no unspecified order (function-argument "
              "evaluation, unordered_map iteration), no typeid names, no %p; print with std::cout and '\\n'.",
        reads_input=r"\b(cin|scanf|getline|getchar|gets)\b",
    ),
    Lang(
        id="java", name="Java", prefix="java", ext="java",
        syntax=Syntax(
            keywords=_words("abstract assert break case catch class continue default do else enum extends final "
                            "finally for if implements import instanceof interface native new package private "
                            "protected public return static strictfp super switch synchronized this throw "
                            "throws transient try var volatile while record sealed permits yield"),
            types=_words("void boolean byte char short int long float double String Integer Long Double Boolean "
                         "Character Object List ArrayList Map TreeMap LinkedHashMap Set TreeSet Arrays Math "
                         "StringBuilder System Optional"),
            consts=_words("true false null"), triple=True),
        banned=(
            (r"\bHashMap\b|\bHashSet\b|\bIdentityHashMap\b|\bHashtable\b",
             "iteration order is unspecified; use TreeMap/LinkedHashMap/List"),
            (r"\bhashCode\b|\bidentityHashCode\b", "hash values differ between runs"),
            (r"\bMath\.random\b|\bRandom\b|\bUUID\b|\bThreadLocalRandom\b", "uses randomness"),
            (r"System\.(currentTimeMillis|nanoTime|getenv|getProperty|in)\b|\bLocalDate(Time)?\.now|\bInstant\b",
             "reads the clock or the environment"),
            (r"\bScanner\b|\bBufferedReader\b|\bConsole\b", "waits for input"),
            (r"\bThread\b|\bExecutor|\bCompletableFuture\b|\bparallelStream\b", "threads are not deterministic"),
            (r"\bargs\s*(\.|\[)", "reads the command line"),
        ),
        notes="Single file, one public-or-package class with static main (the source launcher runs it); avoid "
              "HashMap/HashSet iteration, hashCode and default Object.toString (they print addresses/hashes); "
              "System.out.println one line; no Scanner.",
        reads_input=r"\b(Scanner|BufferedReader|System\.in|readLine)\b",
    ),
    Lang(
        id="csharp", name="C#", prefix="cs", ext="cs",
        syntax=Syntax(
            keywords=_words("abstract as base break case catch checked class const continue default delegate do "
                            "else enum event explicit extern finally fixed for foreach goto if implicit in "
                            "interface internal is lock namespace new operator out override params private "
                            "protected public readonly record ref return sealed sizeof stackalloc static struct "
                            "switch this throw try typeof unchecked unsafe using var virtual volatile while "
                            "yield async await when with init required"),
            types=_words("void bool byte sbyte char decimal double float int uint long ulong short ushort object "
                         "string dynamic List Dictionary HashSet Console Math String Array Enumerable"),
            consts=_words("true false null"), directives=True),
        banned=(
            (r"\bHashSet\b|\bHashtable\b|\bGetHashCode\b", "hash order/values differ between runs"),
            (r"\bRandom\b|\bGuid\b", "uses randomness"),
            (r"\bDateTime\.(Now|UtcNow|Today)\b|\bStopwatch\b|\bEnvironment\.|\bTickCount\b",
             "reads the clock or the environment"),
            (r"\bConsole\.(Read|In)\b|\bargs\b", "waits for input / reads the command line"),
            (r"\bThread\b|\bTask\.Run\b|\bParallel\b|\bGC\.", "threads / the collector are not deterministic"),
        ),
        notes="One file of top-level statements (implicit usings are on: List, Func, Linq work without `using`) or "
              "a class with Main; no HashSet/GetHashCode (string hashes are randomised per process), no "
              "Dictionary iteration unless insertion order is the point, no default ToString() of objects "
              "(type names), no clock; Console.WriteLine one line. dotnet run takes ~2 s a go.",
        reads_input=r"\bConsole\.(Read|ReadLine|ReadKey|In)\b",
    ),
    Lang(
        id="go", name="Go", prefix="go", ext="go",
        syntax=Syntax(
            keywords=_words("break case chan const continue default defer else fallthrough for func go goto if "
                            "import interface map package range return select struct switch type var"),
            types=_words("bool byte complex64 complex128 error float32 float64 int int8 int16 int32 int64 rune "
                         "string uint uint8 uint16 uint32 uint64 uintptr any"),
            consts=_words("true false nil iota"), quotes="\"'`"),
        banned=(
            (r"math/rand|\brand\.", "uses randomness"), (r"\btime\.", "reads the clock"),
            (r"\bos\.(Args|Getenv|Stdin)|\bbufio\.New(Reader|Scanner)|\bfmt\.Scan", "reads the environment / input"),
            (r"%p|\bunsafe\.|\bruntime\.", "prints an address / implementation detail"),
            (r"\bgo\s+(func|\w+\()|\bsync\.|\bselect\s*\{", "goroutine scheduling is not deterministic"),
        ),
        notes="package main with func main (go 1.27 here: loop variables are per-iteration since 1.22); ranging "
              "over a map is in random order (sort the keys, or print one key); no goroutine races, no %p; "
              "fmt.Println one line; an unused variable or import is a compile error, so every card must use "
              "everything it declares.",
        reads_input=r"\bfmt\.Scan|bufio\.New(Reader|Scanner)|os\.Stdin",
        check=_go_map_range,
    ),
    Lang(
        id="rust", name="Rust", prefix="rs", ext="rs",
        syntax=Syntax(
            keywords=_words("as async await break const continue crate dyn else enum extern fn for if impl in "
                            "let loop match mod move mut pub ref return self Self static struct super trait "
                            "type unsafe use where while"),
            types=_words("bool char str String i8 i16 i32 i64 i128 isize u8 u16 u32 u64 u128 usize f32 f64 Vec "
                         "Option Result Box Rc Arc HashMap BTreeMap HashSet BTreeSet"),
            consts=_words("true false None Some Ok Err"), char_literals=True),
        banned=(
            (r"\bHashMap\b|\bHashSet\b", "iteration order is random per process; use BTreeMap/BTreeSet/Vec"),
            (r"\{:p\}|\bas_ptr\b|\bas_mut_ptr\b|\*const\b|\*mut\b", "prints or uses a raw address"),
            (r"\brand\b|\bstd::time\b|\bInstant\b|\bSystemTime\b", "uses randomness or the clock"),
            (r"\bstd::env\b|\bio::stdin\b|\bstdin\s*\(", "reads the environment / input"),
            (r"\bthread::|\bmpsc\b|\bMutex\b|\bsize_of\b|\balign_of\b", "threads / layout are not portable"),
            (r"\bunsafe\b|\bstd::process\b", "not a safe, portable question"),
        ),
        notes="Edition 2021, built with rustc -O (overflow wraps silently in -O, so avoid integer overflow cards "
              "unless you use checked_/wrapping_); no HashMap/HashSet iteration, no {:p}, no size_of; println! "
              "one line; floats print without an exponent ({} of 1e21 is 1000000000000000000000), unlike most "
              "languages; warnings are not output.",
        reads_input=r"\bstdin\s*\(|io::stdin",
    ),
    Lang(
        id="dart", name="Dart", prefix="dart", ext="dart",
        syntax=Syntax(
            keywords=_words("abstract as assert async await break case catch class const continue covariant "
                            "default deferred do dynamic else enum export extends extension external factory "
                            "final finally for get if implements import in interface is late library mixin new "
                            "on operator part required rethrow return sealed set show static super switch sync "
                            "this throw try typedef var void while with yield"),
            types=_words("bool double int num String List Map Set Object Future Stream Iterable Function Null "
                         "Never dynamic Runes Symbol Type"),
            consts=_words("true false null"), triple=True),
        banned=(
            (r"\bRandom\b", "uses randomness"), (r"\bDateTime\.now\b|\bStopwatch\b", "reads the clock"),
            (r"\bPlatform\.|\bstdin\b", "reads the environment / input"),
            (r"\bhashCode\b|\bidentityHashCode\b", "hash values differ between runs"),
            (r"\bIsolate\b|\bTimer\b", "concurrency is not deterministic"),
        ),
        notes="Dart VM (not dart2js: int is 64-bit here and would be a double in a browser); void main() with "
              "print(); Map and Set literals are insertion-ordered (safe); avoid hashCode, Random, DateTime.now.",
        reads_input=r"\bstdin\b",
    ),
    Lang(
        id="kotlin", name="Kotlin", prefix="kt", ext="kt",
        syntax=Syntax(
            keywords=_words("abstract actual annotation as break by catch class companion const constructor "
                            "continue crossinline data do else enum expect external final finally for fun get if "
                            "import in infix init inline inner interface internal is lateinit noinline object "
                            "open operator out override package private protected public reified return sealed "
                            "set super suspend this throw try typealias val value var vararg when where while"),
            types=_words("Any Boolean Byte Char Double Float Int Long Nothing Short String Unit Array List "
                         "MutableList Map MutableMap Set MutableSet Pair Triple Sequence"),
            consts=_words("true false null"), triple=True),
        banned=(
            (r"\bhashMapOf\b|\bhashSetOf\b|\bHashMap\b|\bHashSet\b", "iteration order is unspecified; use "
             "mapOf/setOf (insertion ordered)"),
            (r"\bhashCode\b|\bidentityHashCode\b", "hash values differ between runs"),
            (r"\bRandom\b|\bUUID\b", "uses randomness"),
            (r"System\.(currentTimeMillis|nanoTime|getenv|`in`)|\bLocalDate\.now|\bInstant\b|measureTime",
             "reads the clock or the environment"),
            (r"\breadLine\b|\breadln\b|\bScanner\b|\bargs\b", "waits for input / reads the command line"),
            (r"\bThread\b|\bcoroutine|\blaunch\b|\bGlobalScope\b", "concurrency is not deterministic"),
        ),
        notes="A file with fun main(); built with kotlinc and run on the JVM; mapOf/setOf keep insertion order "
              "(safe), HashMap/HashSet do not; no hashCode, Random, readLine; println one line. A compile "
              "takes ~5 s.",
        reads_input=r"\b(readLine|readln|Scanner|System\.`?in`?)\b",
    ),
    Lang(
        id="swift", name="Swift", prefix="swift", ext="swift",
        syntax=Syntax(
            keywords=_words("actor any as associatedtype async await break case catch class continue default "
                            "defer deinit do else enum extension fallthrough fileprivate for func guard if "
                            "import in indirect init inout internal is let nil open operator private protocol "
                            "public repeat rethrows return self Self static struct subscript super switch "
                            "throw throws try typealias var weak where while willSet didSet get set lazy "
                            "mutating nonmutating some"),
            types=_words("Int Int8 Int16 Int32 Int64 UInt UInt8 UInt16 UInt32 UInt64 Double Float Bool String "
                         "Character Array Dictionary Set Optional Substring Void Any AnyObject Result Range"),
            consts=_words("true false nil"), triple=True),
        banned=(
            (r"\bSet\b|\bDictionary\b|\bhashValue\b|\bHasher\b|\.keys\b|\.values\b",
             "Set/Dictionary order is randomised for every run"),
            (r"\.random\b|SystemRandomNumberGenerator|\barc4random", "uses randomness"),
            (r"\bDate\(|\bDispatchTime\b|\bProcessInfo\b|\bCommandLine\b|\bClock\b", "reads the clock / environment"),
            (r"\breadLine\b|\bFileHandle\b", "waits for input"),
            (r"\bTask\b|\bDispatchQueue\b|\bThread\b", "concurrency is not deterministic"),
            (r"\bwithUnsafe|\bUnsafe\w*Pointer\b|\bObjectIdentifier\b|\bunsafeBitCast\b", "prints/uses an address"),
        ),
        notes="Compiled with swiftc (not the JIT) and run; never print or loop over a Set or Dictionary (the order "
              "is random per process) - use arrays, or sort the keys; no hashValue; print() one line; avoid "
              "`import Foundation` (the first build on a machine takes ~90 s to make the module cache, past the "
              "15 s compile limit, then ~1 s) and stay with the standard library.",
        reads_input=r"\breadLine\s*\(",
        check=_swift_dictionary,
    ),
    Lang(
        id="ruby", name="Ruby", prefix="rb", ext="rb",
        syntax=Syntax(
            keywords=_words("BEGIN END alias and begin break case class def defined? do else elsif end ensure for "
                            "if in module next not or redo rescue retry return self super then undef unless "
                            "until when while yield"),
            consts=_words("true false nil"), line_comments=("#",), block_comments=(), quotes="\"'`"),
        banned=(
            (r"\brand\b|\bsrand\b|\bRandom\b|\bshuffle\b|\bsample\b|\bSecureRandom\b", "uses randomness"),
            (r"\bTime\b|\bDate\.today\b|\bProcess\.clock", "reads the clock"),
            (r"\bENV\b|\bARGV\b|\bgets\b|\bSTDIN\b|\$stdin", "reads the environment / input"),
            (r"\bobject_id\b|\b__id__\b|\.hash\b|\bThread\b", "prints an identity / address"),
        ),
        notes="Hash and Set keep insertion order (safe); avoid object_id, #hash, default Object#inspect/to_s "
              "(#<Foo:0x..>), rand/shuffle/Time; puts/p/print one line; frozen string literals are not on by "
              "default.",
        reads_input=r"\b(gets|STDIN|readline|readlines)\b|\$stdin",
    ),
    Lang(
        id="php", name="PHP", prefix="php", ext="php",
        syntax=Syntax(
            keywords=_words("abstract and array as break callable case catch class clone const continue declare "
                            "default do echo else elseif empty enddeclare endfor endforeach endif endswitch "
                            "endwhile extends final finally fn for foreach function global goto if implements "
                            "include instanceof insteadof interface isset list match namespace new or print "
                            "private protected public readonly require return static switch throw trait try "
                            "unset use var while xor yield"),
            types=_words("int float string bool array object callable iterable mixed void never self parent"),
            consts=_words("true false null TRUE FALSE NULL PHP_EOL PHP_INT_MAX PHP_INT_MIN"),
            line_comments=("//", "#"), quotes="\"'"),
        banned=(
            (r"\b(m?t?_?rand|random_int|random_bytes|shuffle|array_rand|uniqid|lcg_value)\s*\(", "uses randomness"),
            (r"\b(time|microtime|date|hrtime|mktime|strtotime)\s*\(|\bDateTime", "reads the clock"),
            (r"\bgetenv\b|\$_SERVER|\$_ENV|\$argv|\$argc|\bSTDIN\b|\bfgets\b|\breadline\b|php://stdin",
             "reads the environment / input"),
            (r"\bspl_object_(id|hash)\b|\bmemory_get|\bPHP_VERSION|\bPHP_OS|\bPHP_INT_SIZE|\bphpversion",
             "prints an identity / build detail"),
        ),
        notes="The file must start with <?php; PHP 8 semantics (the `==` rules changed from 7: '0' == 'a' is "
              "false now) - pin to what `php -v` here prints; echo with PHP_EOL, one line; var_dump/print_r of "
              "floats prints at serialize_precision -1 (shortest round-trip).",
        reads_input=r"\b(fgets|fscanf|readline|stream_get_contents)\b|STDIN|php://stdin",
    ),
    Lang(
        id="lua", name="Lua", prefix="lua", ext="lua",
        syntax=Syntax(
            keywords=_words("and break do else elseif end for function goto if in local not or repeat return "
                            "then until while"),
            consts=_words("true false nil"), line_comments=("--",), block_comments=(("--[[", "]]"),)),
        banned=(
            (r"\bmath\.random|\bmath\.randomseed", "uses randomness"),
            (r"\bos\.(time|clock|date|getenv)\b", "reads the clock / environment"),
            (r"\bio\.(read|stdin|lines)\b|\barg\b", "waits for input / reads the command line"),
            (r"\bpairs\s*\(|\bnext\s*\(", "pairs()/next() order of non-array keys is unspecified (string hashes "
             "are seeded); use ipairs or sorted keys"),
            (r"%p|\btostring\s*\(\s*(function|\{)|\bprint\s*\(\s*\{", "prints an address"),
            (r"\bcollectgarbage\b|\bcoroutine\.running\b|\bdebug\.", "implementation detail"),
        ),
        notes="Lua 5.4: print(a, b) separates with a TAB, so join values with .. or table.concat(t, \" \") to "
              "print one space-separated line; never use pairs()/next() over string keys (random order) nor "
              "print a table or function (addresses); integers vs floats (1 vs 1.0, 3 // 2 vs 3 / 2) is "
              "trap material; os.* is off limits.",
        reads_input=r"\bio\.(read|lines|stdin)\b",
    ),
    Lang(
        id="zig", name="Zig", prefix="zig", ext="zig", output_on_stderr=True,
        syntax=Syntax(
            keywords=_words("addrspace align allowzero and anyframe anytype asm async await break callconv "
                            "catch comptime const continue defer else enum errdefer error export extern fn for "
                            "if inline linksection noalias nosuspend opaque or orelse packed pub resume return "
                            "struct suspend switch test threadlocal try union unreachable usingnamespace var "
                            "volatile while"),
            types=_words("bool void noreturn type anyerror comptime_int comptime_float i8 i16 i32 i64 i128 "
                         "isize u8 u16 u32 u64 u128 usize f16 f32 f64 f128 c_int c_uint"),
            consts=_words("true false null undefined"), char_literals=True),
        banned=(
            (r"std\.(crypto\.random|Random|Io\.Threaded)|\brandom\b|\bPrng\b", "uses randomness"),
            (r"std\.time|std\.Io\.Timestamp|\bTimer\b", "reads the clock"),
            (r"std\.process|std\.posix|\bstdin\b|\bargs\b|std\.os\.environ", "reads the environment / input"),
            (r"@ptrToInt|@intFromPtr|\{\*\}|\{p\}", "prints an address"),
            (r"std\.Thread|\basync\b|\bundefined\b\s*;", "concurrency / reading undefined memory"),
        ),
        notes="Zig 0.16 here, built in Debug (overflow panics, not wraps): print with std.debug.print, which writes to "
              "stderr - on a clean exit the runner takes stderr as the output, so a panic/trace is never "
              "an answer; trap material is comptime_int, @as, integer casts, optionals, slices; one line of "
              "output.",
        reads_input=r"\bstdin\b",
    ),
    Lang(
        id="odin", name="Odin", prefix="odin", ext="odin",
        syntax=Syntax(
            keywords=_words("package import foreign when if else for in not_in switch case break continue fallthrough "
                            "defer return proc struct union enum bit_set bit_field map dynamic using context "
                            "distinct cast transmute auto_cast or_else or_return or_break or_continue where "
                            "do"),
            types=_words("bool b8 b16 b32 b64 int i8 i16 i32 i64 i128 uint u8 u16 u32 u64 u128 uintptr f16 f32 "
                         "f64 complex64 complex128 quaternion128 rune string cstring rawptr typeid any byte"),
            consts=_words("true false nil"), quotes="\"'`"),
        banned=(
            (r"core:math/rand|\brand\.", "uses randomness"), (r"core:time|\btime\.", "reads the clock"),
            (r"os\.args|os\.get_env|os\.stdin|os\.read", "reads the environment / input"),
            (r"%p|\braw_data\b|\brawptr\b|\bcast\(\s*uintptr", "prints an address"),
            (r"core:thread|core:sync", "concurrency is not deterministic"),
        ),
        notes="package main + main :: proc(); fmt.println one line (import \"core:fmt\", separates arguments with "
              "a space); ranging a map is unordered - do not; nothing prints addresses; an untyped constant "
              "that does not fit an int (1e21) is a compile error; % is the truncated remainder, %% the floored "
              "modulo.",
        reads_input=r"os\.(stdin|read)",
    ),
    Lang(
        id="lisp", name="Common Lisp", prefix="lisp", ext="lisp",
        syntax=Syntax(
            keywords=_words("defun defvar defparameter defmacro defstruct defclass defmethod defgeneric "
                            "defconstant let let* flet labels lambda if cond when unless case ecase loop do "
                            "dolist dotimes progn prog1 setf setq push pop incf decf return return-from block "
                            "tagbody go the declare declaim quote function funcall apply multiple-value-bind "
                            "destructuring-bind handler-case ignore-errors unwind-protect and or not"),
            consts=_words("t nil"), line_comments=(";",), block_comments=(("#|", "|#"),), quotes="\"",
            char_literals=True, lisp=True, ignore_case=True),
        banned=(
            (r"\(random\b|\*random-state\*|make-random-state", "uses randomness"),
            (r"get-universal-time|get-internal-(real|run)-time|get-decoded-time|\bsleep\b", "reads the clock"),
            (r"\bgetenv\b|\(read\b|\(read-line\b|\(read-char\b|\*standard-input\*|posix-argv", "reads the environment / input"),
            (r"\bsxhash\b|\bmaphash\b|being the hash-(keys|values)", "hash iteration order is implementation defined"),
            (r"\bsb-|\bext:|\bsys:|\bjava:|\bjcall\b|\bjnew\b", "implementation specific (ABCL here)"),
        ),
        notes="Runs on ABCL (JVM) with --batch: print with (format t \"~a~%\" ...) or (princ ...)/(terpri), "
              "one line; floats are single-float by default (0.33333334 for (/ 1.0 3)) - the same on SBCL; "
              "hash-table iteration and SORT stability are implementation-defined (use stable-sort); no "
              "implementation extensions.",
        reads_input=r"\(read(-line|-char)?\b|\*standard-input\*",
    ),
    Lang(
        id="sql", name="SQL", prefix="sql", ext="sql",
        syntax=Syntax(
            keywords=_words("select from where group by having order limit offset insert into values update set "
                            "delete create table drop alter add index view as join inner left right outer cross "
                            "on using union all except intersect distinct case when then else end and or not "
                            "in is like between exists primary key default unique check with recursive over "
                            "partition asc desc"),
            types=_words("integer int text real blob numeric varchar char boolean date"),
            consts=_words("null true false"), line_comments=("--",), quotes="\"'", ignore_case=True),
        banned=(
            (r"(?i)\brandom\s*\(|\brandomblob\b|\bzeroblob\b", "uses randomness"),
            (r"(?i)\bdate\s*\(|\bdatetime\s*\(|\btime\s*\(|'now'|\bcurrent_(time|date|timestamp)\b|\bjulianday\b",
             "reads the clock"),
            (r"(?i)\bsqlite_version\b|\bchanges\s*\(|\blast_insert_rowid\b|\bPRAGMA\b|\bATTACH\b",
             "depends on the build / connection"),
        ),
        notes="Runs on SQLite (python's sqlite3) in a throwaway in-memory database: the program is CREATE/INSERT "
              "statements and ends with ONE SELECT, whose rows print as `a|b` per row, rows joined by `; `, "
              "NULL as NULL. Always ORDER BY when a SELECT returns several rows; SQLite's typing (affinity, "
              "'1' = 1, integer division, NULL logic) is the trap material, not the order of unordered rows.",
            ),
)

BY_ID: dict[str, Lang] = {lang.id: lang for lang in LANGS}
#: Display order (the registry's own order).
ORDER: tuple[str, ...] = tuple(lang.id for lang in LANGS)


def get(language: str) -> Lang:
    try:
        return BY_ID[language]
    except KeyError:
        raise KeyError(f"unknown language {language!r}") from None


def known(language: str) -> bool:
    return language in BY_ID


def syntax_payload() -> dict[str, dict]:
    """Every language's colouring rules, for the browser."""
    return {lang.id: lang.syntax.payload() for lang in LANGS}
