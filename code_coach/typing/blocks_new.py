"""Whole programs to type, in the ten languages with a toolchain here.

Every code theme except these had blocks and these had none, which meant
Blocks mode simply could not be driven by them. Lines drill punctuation;
blocks drill shape — what sits under what, and Enter as part of writing
code — and that is the half these languages were missing.

Where the other themes get their blocks is the curriculum: the solution
bank and the fundamentals, whole functions with their indentation. These
ten have neither, so the blocks are written here.

They are whole programs rather than excerpts, and that is the point of
the file. A fragment cannot be checked by anything; a program can be run.
Every block below was executed and its output read, so what you are
typing is known to work rather than known to look right.

Indented with spaces, including the two languages whose formatter uses
tabs. A drill target has to be typeable on the keyboard the app models,
and that keyboard has no Tab key — a block full of them is a block you
cannot type. Go and Odin will both retab this the moment you run their
formatter over it, which is the right place for that to happen.

The six languages without a toolchain on this machine — Kotlin, Scala,
Haskell, OCaml, Elixir and Assembly — get no blocks, because a block
written from documentation and never run is exactly the thing this file
exists to avoid. Their lines stay in `snippets2`, where the weaker
guarantee is stated.

Swift used to be the seventh and is not any more. It is the one of them
worth a 1.76 GB installer, and now that `swiftc` is here its blocks are
run like everyone else's.
"""

from __future__ import annotations

from code_coach.typing.snippets import Passage, _s

# ── Go ───────────────────────────────────────────────────────

GO_BLOCKS: tuple[Passage, ...] = (
    _s('package main\n'
       '\n'
       'import "fmt"\n'
       '\n'
       'func main() {\n'
       '    for i := 1; i <= 5; i++ {\n'
       '        fmt.Println(i * i)\n'
       '    }\n'
       '}',
       "the square of one to five"),
    _s('package main\n'
       '\n'
       'import "fmt"\n'
       '\n'
       'func sum(xs []int) int {\n'
       '    total := 0\n'
       '    for _, x := range xs {\n'
       '        total += x\n'
       '    }\n'
       '    return total\n'
       '}\n'
       '\n'
       'func main() {\n'
       '    fmt.Println(sum([]int{3, 5, 8}))\n'
       '}',
       "a function, and range over a slice"),
    _s('package main\n'
       '\n'
       'import (\n'
       '    "errors"\n'
       '    "fmt"\n'
       ')\n'
       '\n'
       'func half(n int) (int, error) {\n'
       '    if n%2 != 0 {\n'
       '        return 0, errors.New("not even")\n'
       '    }\n'
       '    return n / 2, nil\n'
       '}\n'
       '\n'
       'func main() {\n'
       '    v, err := half(7)\n'
       '    if err != nil {\n'
       '        fmt.Println("error:", err)\n'
       '        return\n'
       '    }\n'
       '    fmt.Println(v)\n'
       '}',
       "the error return, and the check that follows it"),
    _s('package main\n'
       '\n'
       'import "fmt"\n'
       '\n'
       'func main() {\n'
       '    counts := make(map[string]int)\n'
       '    for _, w := range []string{"a", "b", "a"} {\n'
       '        counts[w]++\n'
       '    }\n'
       '    fmt.Println(counts["a"], counts["b"])\n'
       '}',
       "a map, and the zero value you never have to check for"),
)


# ── PHP ──────────────────────────────────────────────────────

PHP_BLOCKS: tuple[Passage, ...] = (
    _s('<?php\n'
       'for ($i = 1; $i <= 5; $i++) {\n'
       '  echo $i * $i, PHP_EOL;\n'
       '}',
       "the square of one to five"),
    _s('<?php\n'
       'function sum(array $xs): int {\n'
       '  $total = 0;\n'
       '  foreach ($xs as $x) {\n'
       '    $total += $x;\n'
       '  }\n'
       '  return $total;\n'
       '}\n'
       '\n'
       'echo sum([3, 5, 8]), PHP_EOL;',
       "a typed function, and foreach"),
    _s('<?php\n'
       '$counts = [];\n'
       'foreach (["a", "b", "a"] as $w) {\n'
       '  $counts[$w] = ($counts[$w] ?? 0) + 1;\n'
       '}\n'
       'echo $counts["a"], " ", $counts["b"], PHP_EOL;',
       "the null-coalescing operator, doing real work"),
    _s('<?php\n'
       'try {\n'
       '  throw new RuntimeException("no");\n'
       '} catch (RuntimeException $e) {\n'
       '  echo "caught: ", $e->getMessage(), PHP_EOL;\n'
       '}',
       "throw, catch, and the arrow"),
)


# ── Lua ──────────────────────────────────────────────────────

LUA_BLOCKS: tuple[Passage, ...] = (
    _s('for i = 1, 5 do\n'
       '  print(i * i)\n'
       'end',
       "the square of one to five"),
    _s('local function sum(xs)\n'
       '  local total = 0\n'
       '  for _, x in ipairs(xs) do\n'
       '    total = total + x\n'
       '  end\n'
       '  return total\n'
       'end\n'
       '\n'
       'print(sum({3, 5, 8}))',
       "a local function, and ipairs"),
    _s('local counts = {}\n'
       'for _, w in ipairs({"a", "b", "a"}) do\n'
       '  counts[w] = (counts[w] or 0) + 1\n'
       'end\n'
       'print(counts["a"], counts["b"])',
       "or, standing in for a default"),
    _s('local Point = {}\n'
       'Point.__index = Point\n'
       '\n'
       'function Point.new(x, y)\n'
       '  return setmetatable({x = x, y = y}, Point)\n'
       'end\n'
       '\n'
       'function Point:show()\n'
       '  print(self.x, self.y)\n'
       'end\n'
       '\n'
       'Point.new(3, 4):show()',
       "the metatable, which is how Lua does objects"),
)


# ── Ruby ─────────────────────────────────────────────────────

RUBY_BLOCKS: tuple[Passage, ...] = (
    _s('(1..5).each do |i|\n'
       '  puts i * i\n'
       'end',
       "a range, and the block"),
    _s('def sum(xs)\n'
       '  xs.reduce(0) { |total, x| total + x }\n'
       'end\n'
       '\n'
       'puts sum([3, 5, 8])',
       "reduce, and the brace block"),
    _s('counts = Hash.new(0)\n'
       '\n'
       '%w[a b a].each do |w|\n'
       '  counts[w] += 1\n'
       'end\n'
       '\n'
       'counts.each do |word, n|\n'
       '  puts "#{word}: #{n}"\n'
       'end',
       "a hash with a default, and do-end twice"),
    _s('class Point\n'
       '  attr_reader :x, :y\n'
       '\n'
       '  def initialize(x, y)\n'
       '    @x = x\n'
       '    @y = y\n'
       '  end\n'
       '\n'
       '  def to_s\n'
       '    "(#{@x}, #{@y})"\n'
       '  end\n'
       'end\n'
       '\n'
       'puts Point.new(3, 4)',
       "a class, and the at-sign"),
)


# ── Java ─────────────────────────────────────────────────────

JAVA_BLOCKS: tuple[Passage, ...] = (
    _s('public class Main {\n'
       '    public static void main(String[] args) {\n'
       '        for (int i = 1; i <= 5; i++) {\n'
       '            System.out.println(i * i);\n'
       '        }\n'
       '    }\n'
       '}',
       "the square of one to five"),
    _s('public class Main {\n'
       '    static int sum(int[] xs) {\n'
       '        int total = 0;\n'
       '        for (int x : xs) {\n'
       '            total += x;\n'
       '        }\n'
       '        return total;\n'
       '    }\n'
       '\n'
       '    public static void main(String[] args) {\n'
       '        System.out.println(sum(new int[] {3, 5, 8}));\n'
       '    }\n'
       '}',
       "a static method, and the enhanced for"),
    _s('import java.util.HashMap;\n'
       'import java.util.Map;\n'
       '\n'
       'public class Main {\n'
       '    public static void main(String[] args) {\n'
       '        Map<String, Integer> counts = new HashMap<>();\n'
       '        for (String w : new String[] {"a", "b", "a"}) {\n'
       '            counts.merge(w, 1, Integer::sum);\n'
       '        }\n'
       '        System.out.println(counts.get("a") + " " + counts.get("b"));\n'
       '    }\n'
       '}',
       "merge and a method reference, instead of a get-or-zero"),
    _s('import java.util.List;\n'
       '\n'
       'public class Main {\n'
       '    public static void main(String[] args) {\n'
       '        List<String> names = List.of("ada", "grace", "alan");\n'
       '        names.stream()\n'
       '             .filter(n -> n.length() > 3)\n'
       '             .map(String::toUpperCase)\n'
       '             .forEach(System.out::println);\n'
       '    }\n'
       '}',
       "a stream, chained across lines"),
)


# ── C# ───────────────────────────────────────────────────────

CSHARP_BLOCKS: tuple[Passage, ...] = (
    _s('for (int i = 1; i <= 5; i++) {\n'
       '  System.Console.WriteLine(i * i);\n'
       '}',
       "top-level statements, and no class needed"),
    _s('int Sum(int[] xs) {\n'
       '  int total = 0;\n'
       '  foreach (int x in xs) {\n'
       '    total += x;\n'
       '  }\n'
       '  return total;\n'
       '}\n'
       '\n'
       'System.Console.WriteLine(Sum(new int[] {3, 5, 8}));',
       "a local function, declared beside the code that calls it"),
    _s('var counts = new System.Collections.Generic.Dictionary<string, int>();\n'
       'foreach (string w in new[] {"a", "b", "a"}) {\n'
       '  counts[w] = counts.GetValueOrDefault(w) + 1;\n'
       '}\n'
       'System.Console.WriteLine($"{counts["a"]} {counts["b"]}");',
       "GetValueOrDefault, and the interpolated string"),
    _s('using System.Linq;\n'
       '\n'
       'var names = new[] {"ada", "grace", "alan"};\n'
       'foreach (var n in names.Where(n => n.Length > 3)\n'
       '                       .Select(n => n.ToUpperInvariant())) {\n'
       '  System.Console.WriteLine(n);\n'
       '}',
       "LINQ, and the lambda arrow"),
)


# ── Odin ─────────────────────────────────────────────────────

ODIN_BLOCKS: tuple[Passage, ...] = (
    _s('package main\n'
       '\n'
       'import "core:fmt"\n'
       '\n'
       'main :: proc() {\n'
       '    for i := 1; i <= 5; i += 1 {\n'
       '        fmt.println(i * i)\n'
       '    }\n'
       '}',
       "the square of one to five"),
    _s('package main\n'
       '\n'
       'import "core:fmt"\n'
       '\n'
       'sum :: proc(xs: []int) -> int {\n'
       '    total := 0\n'
       '    for x in xs {\n'
       '        total += x\n'
       '    }\n'
       '    return total\n'
       '}\n'
       '\n'
       'main :: proc() {\n'
       '    fmt.println(sum([]int{3, 5, 8}))\n'
       '}',
       "the double colon, which declares everything"),
    _s('package main\n'
       '\n'
       'import "core:fmt"\n'
       '\n'
       'Point :: struct {\n'
       '    x: int,\n'
       '    y: int,\n'
       '}\n'
       '\n'
       'main :: proc() {\n'
       '    p := Point{x = 3, y = 4}\n'
       '    fmt.printf("%d %d\\n", p.x, p.y)\n'
       '}',
       "a struct, and naming the fields as you fill them"),
    _s('package main\n'
       '\n'
       'import "core:fmt"\n'
       '\n'
       'main :: proc() {\n'
       '    counts := make(map[string]int)\n'
       '    defer delete(counts)\n'
       '    words := []string{"a", "b", "a"}\n'
       '    for w in words {\n'
       '        counts[w] += 1\n'
       '    }\n'
       '    fmt.println(counts["a"], counts["b"])\n'
       '}',
       "make and defer delete, because Odin does not collect for you"),
)


# ── Zig ──────────────────────────────────────────────────────

ZIG_BLOCKS: tuple[Passage, ...] = (
    _s('const std = @import("std");\n'
       '\n'
       'pub fn main() !void {\n'
       '    var threaded: std.Io.Threaded = .init(std.heap.page_allocator, .{});\n'
       '    defer threaded.deinit();\n'
       '    const io = threaded.io();\n'
       '    var buf: [256]u8 = undefined;\n'
       '    var w = std.Io.File.stdout().writer(io, &buf);\n'
       '    const out = &w.interface;\n'
       '    var i: i32 = 1;\n'
       '    while (i <= 5) : (i += 1) {\n'
       '        try out.print("{d}\\n", .{i * i});\n'
       '    }\n'
       '    try out.flush();\n'
       '}',
       "the whole of a Zig program that prints"),
    _s('const std = @import("std");\n'
       '\n'
       'fn sum(xs: []const i32) i32 {\n'
       '    var total: i32 = 0;\n'
       '    for (xs) |x| {\n'
       '        total += x;\n'
       '    }\n'
       '    return total;\n'
       '}\n'
       '\n'
       'test "it adds" {\n'
       '    try std.testing.expectEqual(@as(i32, 16), sum(&[_]i32{3, 5, 8}));\n'
       '}',
       "a function and the test that lives beside it"),
    _s('const std = @import("std");\n'
       '\n'
       'const Point = struct {\n'
       '    x: i32,\n'
       '    y: i32,\n'
       '\n'
       '    fn sum(self: Point) i32 {\n'
       '        return self.x + self.y;\n'
       '    }\n'
       '};\n'
       '\n'
       'test "a struct with a method" {\n'
       '    const p = Point{ .x = 3, .y = 4 };\n'
       '    try std.testing.expectEqual(@as(i32, 7), p.sum());\n'
       '}',
       "the dot-brace, and a method that takes self"),
    _s('const std = @import("std");\n'
       '\n'
       'fn half(n: i32) !i32 {\n'
       '    if (@rem(n, 2) != 0) return error.NotEven;\n'
       '    return @divTrunc(n, 2);\n'
       '}\n'
       '\n'
       'test "the error set" {\n'
       '    try std.testing.expectError(error.NotEven, half(7));\n'
       '    try std.testing.expectEqual(@as(i32, 4), try half(8));\n'
       '}',
       "an error union, and the try that unwraps it"),
)


# ── Common Lisp ──────────────────────────────────────────────

LISP_BLOCKS: tuple[Passage, ...] = (
    _s('(loop for i from 1 to 5 do\n'
       '  (format t "~a~%" (* i i))\n'
       '  (when (= i 3)\n'
       '    (format t "halfway~%")))',
       "loop, which is a language of its own"),
    _s('(defun total (xs)\n'
       '  (reduce (function +) xs))\n'
       '\n'
       '(format t "~a~%" (total (list 3 5 8)))',
       "reduce, and naming a function as a value"),
    _s('(defun classify (n)\n'
       '  (cond ((< n 0) "negative")\n'
       '        ((= n 0) "zero")\n'
       '        (t "positive")))\n'
       '\n'
       '(format t "~a~%" (classify -4))',
       "cond, and the t that catches the rest"),
    _s('(let ((counts (make-hash-table :test (function equal))))\n'
       '  (dolist (w (list "a" "b" "a"))\n'
       '    (incf (gethash w counts 0)))\n'
       '  (format t "~a ~a~%" (gethash "a" counts) (gethash "b" counts)))',
       "let, dolist, and incf on a place that is a lookup"),
)


# ── Swift ────────────────────────────────────────────────────
#
# Built rather than run as a script. `swift file.swift` on Windows goes
# through a JIT that cannot resolve the standard library's array symbols,
# so a program as small as the first one here fails there and compiles
# perfectly well.

SWIFT_BLOCKS: tuple[Passage, ...] = (
    _s('for i in 1...5 {\n'
       '    print(i * i)\n'
       '}',
       "a closed range, and the square of one to five"),
    _s('func sum(_ xs: [Int]) -> Int {\n'
       '    var total = 0\n'
       '    for x in xs {\n'
       '        total += x\n'
       '    }\n'
       '    return total\n'
       '}\n'
       '\n'
       'print(sum([3, 5, 8]))',
       "the underscore that drops the argument label"),
    _s('struct Point {\n'
       '    let x: Int\n'
       '    let y: Int\n'
       '\n'
       '    var total: Int { x + y }\n'
       '}\n'
       '\n'
       'let p = Point(x: 3, y: 4)\n'
       'print(p.total)',
       "a struct, its memberwise init, and a computed property"),
    _s('enum Shape {\n'
       '    case circle(Double)\n'
       '    case square(Double)\n'
       '}\n'
       '\n'
       'func describe(_ shape: Shape) -> String {\n'
       '    switch shape {\n'
       '    case .circle(let r):\n'
       '        return "circle of \\(r)"\n'
       '    case .square(let s):\n'
       '        return "square of \\(s)"\n'
       '    }\n'
       '}\n'
       '\n'
       'print(describe(.circle(2.0)))',
       "an enum with values, and the switch that must cover it"),
    _s('var counts: [String: Int] = [:]\n'
       'for w in ["a", "b", "a"] {\n'
       '    counts[w, default: 0] += 1\n'
       '}\n'
       'for key in counts.keys.sorted() {\n'
       '    print(key, counts[key]!)\n'
       '}',
       "a dictionary with a default, and the bang that unwraps"),
)


BY_LANGUAGE: dict[str, tuple[Passage, ...]] = {
    "go": GO_BLOCKS,
    "php": PHP_BLOCKS,
    "lua": LUA_BLOCKS,
    "ruby": RUBY_BLOCKS,
    "java": JAVA_BLOCKS,
    "csharp": CSHARP_BLOCKS,
    "odin": ODIN_BLOCKS,
    "zig": ZIG_BLOCKS,
    "lisp": LISP_BLOCKS,
    "swift": SWIFT_BLOCKS,
}
