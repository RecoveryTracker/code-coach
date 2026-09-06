"""Code to type, in the sixteen newer languages.

The existing code themes draw their lines from the curriculum: the
solution bank and the fundamentals, split line by line. These sixteen
languages have neither, so their lines are written here.

Each is a real line of that language rather than a translation of the same
line sixteen times. The point of a code drill is the punctuation your hands
will actually meet, and that differs: Go's tab and its bare colon-equals,
Haskell's arrows, Lisp's parentheses, Zig's dot-brace, the sigils in PHP
and the ends in Ruby and Lua.

What is checked, and what is not. Go, PHP, Lua and Zig have toolchains on
this machine, so any line here that is a whole program has been run. Most
lines are fragments — that is what makes them typing practice rather than
programs — and a fragment cannot be executed by itself in any language. The
other twelve have no toolchain, so their lines are written from
documentation and read carefully, which is a weaker guarantee and worth
saying rather than glossing.
"""

from __future__ import annotations

from code_coach.typing.snippets import Passage, _s

# ── Go ───────────────────────────────────────────────────────

GO_CODE: tuple[Passage, ...] = (
    _s('package main', "every file starts here"),
    _s('import "fmt"', "the printing package"),
    _s("func main() {", "the entry point"),
    _s("items := []int{3, 1, 4}", "declare and infer at once"),
    _s("for i, n := range items {", "index and value"),
    _s("if err != nil {", "the most typed line in Go"),
    _s("return nil, fmt.Errorf(\"not found: %s\", name)", "an error with context"),
    _s("defer file.Close()", "runs when the function returns"),
    _s("counts := make(map[string]int)", "a map you can write to"),
    _s("value, ok := counts[key]", "the comma-ok lookup"),
    _s("go worker(jobs, results)", "start a goroutine"),
    _s("ch := make(chan int, 10)", "a buffered channel"),
    _s("type Point struct {", "a struct declaration"),
    _s("func (p Point) String() string {", "a method with a receiver"),
)


# ── PHP ──────────────────────────────────────────────────────

PHP_CODE: tuple[Passage, ...] = (
    _s("<?php", "where PHP begins"),
    _s("declare(strict_types=1);", "types actually enforced"),
    _s("$items = [3, 1, 4];", "an array literal"),
    _s("foreach ($rows as $key => $value) {", "walk with keys"),
    _s("function total(array $items): int {", "typed in and out"),
    _s("$name = $data['name'] ?? 'unknown';", "null coalescing"),
    _s("echo count($items), PHP_EOL;", "print with a newline"),
    _s("if ($a === $b) {", "strict comparison, always"),
    _s("$sorted = array_map(fn($n) => $n * 2, $items);", "an arrow function"),
    _s("public function __construct(private string $name) {}", "promoted property"),
    _s("match ($status) {", "returns a value and never falls through"),
    _s("throw new InvalidArgumentException('empty list');", "raise it"),
)


# ── Lua ──────────────────────────────────────────────────────

LUA_CODE: tuple[Passage, ...] = (
    _s("local items = {3, 1, 4}", "always declare local"),
    _s("for i, n in ipairs(items) do", "arrays start at one"),
    _s("for key, value in pairs(counts) do", "and this one is unordered"),
    _s("if total ~= 0 then", "not equal is a tilde"),
    _s("local name = data.name or 'unknown'", "or as a default"),
    _s("print(#items)", "the length operator"),
    _s("local function add(a, b)", "a local function"),
    _s("return a .. b", "two dots concatenates"),
    _s("counts[key] = (counts[key] or 0) + 1", "counting without a check"),
    _s("local ok, err = pcall(risky)", "the whole of error handling"),
    _s("setmetatable(obj, Account)", "how objects are made"),
    _s("table.insert(items, 9)", "append"),
)


# ── Zig ──────────────────────────────────────────────────────

ZIG_CODE: tuple[Passage, ...] = (
    _s('const std = @import("std");', "the standard library"),
    _s("pub fn main() !void {", "main can fail, and says so"),
    _s("const items = [_]i32{ 3, 1, 4 };", "the underscore counts for you"),
    _s("var total: i32 = 0;", "var is mutable, const is not"),
    _s("for (items) |n| total += n;", "the value goes in the pipes"),
    _s("for (items, 0..) |n, i| {", "value and index"),
    _s("if (maybe) |value| {", "unwrapping an optional"),
    _s("const file = try std.fs.cwd().openFile(path, .{});", "try propagates"),
    _s("defer file.close();", "at scope exit"),
    _s("errdefer allocator.free(buf);", "only when it goes wrong"),
    _s("var list = std.ArrayList(i32).init(allocator);", "an allocator, always"),
    _s("comptime { assert(size > 0); }", "run at compile time"),
)


# ── Java ─────────────────────────────────────────────────────

JAVA_CODE: tuple[Passage, ...] = (
    _s("public class Main {", "everything lives in a class"),
    _s("public static void main(String[] args) {", "four keywords, all meant"),
    _s("List<Integer> items = new ArrayList<>();", "the diamond infers it"),
    _s("Map<String, Integer> counts = new HashMap<>();", "a typed map"),
    _s("for (Map.Entry<String, Integer> e : counts.entrySet()) {", "walk a map"),
    _s("if (a.equals(b)) {", "never == on a String"),
    _s("counts.merge(key, 1, Integer::sum);", "count in one line"),
    _s("return items.stream().filter(n -> n > 0).toList();", "a stream pipeline"),
    _s("record Point(int x, int y) {}", "data without boilerplate"),
    _s("Optional<String> found = repo.findByName(name);", "might not be there"),
    _s("try (var reader = Files.newBufferedReader(path)) {", "closes itself"),
    _s("throw new IllegalStateException(\"already closed\");", "raise it"),
)


# ── Kotlin ───────────────────────────────────────────────────

KOTLIN_CODE: tuple[Passage, ...] = (
    _s("fun main() {", "no class needed"),
    _s("val items = listOf(3, 1, 4)", "read-only by default"),
    _s("var total = 0", "var only when it changes"),
    _s("for ((key, value) in counts) {", "destructuring in the loop"),
    _s("val name = data?.name ?: \"unknown\"", "safe call, then elvis"),
    _s("data class Point(val x: Int, val y: Int)", "equals and copy for free"),
    _s("fun double(n: Int) = n * 2", "single expression, no braces"),
    _s("items.filter { it > 0 }.map { it * 2 }", "it is the implicit name"),
    _s("when (status) {", "an expression, not a statement"),
    _s("suspend fun fetch(id: String): User {", "a coroutine"),
    _s("println(\"total is $total\")", "string template"),
    _s("requireNotNull(config) { \"config missing\" }", "fail loudly and early"),
)


# ── Ruby ─────────────────────────────────────────────────────

RUBY_CODE: tuple[Passage, ...] = (
    _s("def total(items)", "no types, no parentheses needed"),
    _s("items.each do |item|", "the block is the loop"),
    _s("items.map { |n| n * 2 }", "braces for a one-liner"),
    _s("counts = Hash.new(0)", "a default of zero"),
    _s("counts[word] += 1", "which makes counting one line"),
    _s("return unless valid?", "a guard, read forwards"),
    _s("puts \"total is #{total}\"", "interpolation, double quotes only"),
    _s("attr_accessor :name, :age", "getters and setters written for you"),
    _s("items.select { |n| n.positive? }", "the question mark is convention"),
    _s("raise ArgumentError, 'empty list'", "raise it"),
    _s("class Account < Record", "inheritance"),
    _s("include Comparable", "a mixin"),
)


# ── C# ───────────────────────────────────────────────────────

CSHARP_CODE: tuple[Passage, ...] = (
    _s("using System.Collections.Generic;", "bring the namespace in"),
    _s("var items = new List<int> { 3, 1, 4 };", "collection initialiser"),
    _s("public record Point(int X, int Y);", "value equality included"),
    _s("foreach (var (key, value) in counts)", "deconstruct as you go"),
    _s("var name = data?.Name ?? \"unknown\";", "null-conditional, then default"),
    _s("return items.Where(n => n > 0).ToList();", "LINQ, method form"),
    _s("public async Task<User> FetchAsync(string id)", "async all the way down"),
    _s("await using var conn = new SqlConnection(cs);", "disposed asynchronously"),
    _s("Console.WriteLine($\"total is {total}\");", "an interpolated string"),
    _s("throw new InvalidOperationException(\"already closed\");", "raise it"),
    _s("public int Count { get; init; }", "settable only while building"),
    _s("switch (status) {", "or the expression form, which returns"),
)


# ── Swift ────────────────────────────────────────────────────

SWIFT_CODE: tuple[Passage, ...] = (
    _s("import Foundation", "the usual first line"),
    _s("let items = [3, 1, 4]", "let first, always"),
    _s("var total = 0", "var when it has to change"),
    _s("for (index, value) in items.enumerated() {", "both at once"),
    _s("guard let name = data.name else { return }", "leave early"),
    _s("if let value = maybe {", "unwrap into a name"),
    _s("struct Point { let x: Int; let y: Int }", "a value type"),
    _s("func double(_ n: Int) -> Int { n * 2 }", "the underscore drops the label"),
    _s("items.filter { $0 > 0 }.map { $0 * 2 }", "dollar zero is the argument"),
    _s("print(\"total is \\(total)\")", "interpolation with a backslash"),
    _s("enum Result { case ok(Int), failed(String) }", "cases carry values"),
    _s("try await session.data(from: url)", "both keywords, in that order"),
)


# ── Scala ────────────────────────────────────────────────────

SCALA_CODE: tuple[Passage, ...] = (
    _s("@main def run(): Unit =", "Scala 3, no object needed"),
    _s("val items = List(3, 1, 4)", "immutable by default"),
    _s("case class Point(x: Int, y: Int)", "equality and matching for free"),
    _s("items.filter(_ > 0).map(_ * 2)", "underscore is the argument"),
    _s("for (key, value) <- counts do", "significant indentation in 3"),
    _s("val name = data.name.getOrElse(\"unknown\")", "Option, not null"),
    _s("def double(n: Int): Int = n * 2", "one line, one equals"),
    _s("items match", "pattern match as an expression"),
    _s("case head :: tail =>", "destructure a list"),
    _s("given Ordering[Point] = Ordering.by(_.x)", "the new implicit"),
    _s("println(s\"total is $total\")", "the s prefix interpolates"),
    _s("Try(risky()).getOrElse(0)", "failure as a value"),
)


# ── Haskell ──────────────────────────────────────────────────

HASKELL_CODE: tuple[Passage, ...] = (
    _s("main :: IO ()", "the type comes first"),
    _s("main = putStrLn \"hello\"", "and the definition after"),
    _s("double :: Int -> Int", "one arrow per argument"),
    _s("double n = n * 2", "no parentheses, no return"),
    _s("total = sum [n | n <- items, n > 0]", "a list comprehension"),
    _s("map (* 2) items", "an operator section"),
    _s("filter (> 0) . map double $ items", "compose, then apply"),
    _s("case maybe of", "pattern match on a value"),
    _s("Just value -> value", "the present case"),
    _s("Nothing -> 0", "and the absent one"),
    _s("data Point = Point { x :: Int, y :: Int }", "a record"),
    _s("foldl' (+) 0 items", "the strict fold, with the tick"),
)


# ── OCaml ────────────────────────────────────────────────────

OCAML_CODE: tuple[Passage, ...] = (
    _s("let () = print_endline \"hello\"", "the entry point"),
    _s("let double n = n * 2", "no types written, all inferred"),
    _s("let rec length = function", "rec is required to recurse"),
    _s("| [] -> 0", "the empty case"),
    _s("| _ :: tail -> 1 + length tail", "head and tail"),
    _s("List.filter (fun n -> n > 0) items", "an anonymous function"),
    _s("items |> List.map double |> List.length", "the pipe reads forwards"),
    _s("type point = { x : int; y : int }", "a record type"),
    _s("match maybe with Some v -> v | None -> 0", "option, handled"),
    _s("let total = ref 0 in", "mutation is explicit"),
    _s("total := !total + n;", "assign and dereference"),
    _s("Printf.printf \"%d\\n\" total", "typed formatting"),
)


# ── Elixir ───────────────────────────────────────────────────

ELIXIR_CODE: tuple[Passage, ...] = (
    _s("defmodule Counter do", "everything lives in a module"),
    _s("def total(items) do", "and def inside it"),
    _s("items |> Enum.filter(&(&1 > 0)) |> Enum.sum()", "the pipe, and capture"),
    _s("{:ok, value} = fetch(id)", "match, do not assign"),
    _s("case fetch(id) do", "branch on the shape"),
    _s("{:error, reason} -> Logger.warn(reason)", "the tagged tuple"),
    _s("for {key, value} <- counts, do: key", "a comprehension"),
    _s("Enum.reduce(items, 0, fn n, acc -> n + acc end)", "fold"),
    _s("%{name: name, age: age} = person", "destructure a map"),
    _s("IO.puts(\"total is #{total}\")", "interpolation"),
    _s("with {:ok, u} <- fetch(id) do", "chain the happy path"),
    _s("Task.async(fn -> work() end)", "a process, cheaply"),
)


# ── Lisp ─────────────────────────────────────────────────────

LISP_CODE: tuple[Passage, ...] = (
    _s("(defun double (n) (* n 2))", "define a function"),
    _s("(format t \"~a~%\" total)", "print with a newline"),
    _s("(let ((total 0))", "bind a local"),
    _s("(dolist (n items)", "walk a list"),
    _s("(setf total (+ total n))", "assignment"),
    _s("(mapcar (lambda (n) (* n 2)) items)", "map over a list"),
    _s("(remove-if-not #'plusp items)", "filter, and the sharp-quote"),
    _s("(if (null items) 0 (car items))", "the empty check"),
    _s("(cdr items)", "everything but the first"),
    _s("(defparameter *counts* (make-hash-table))", "earmuffs mean global"),
    _s("(gethash key counts 0)", "lookup with a default"),
    _s("(loop for n in items sum n)", "the little language inside"),
)


# ── Odin ─────────────────────────────────────────────────────

ODIN_CODE: tuple[Passage, ...] = (
    _s("package main", "one per directory"),
    _s('import "core:fmt"', "the standard collection"),
    _s("main :: proc() {", "double colon declares"),
    _s("items := [3]int{3, 1, 4}", "a fixed array"),
    _s("for n, i in items {", "value first, then index"),
    _s("total: int = 0", "name, colon, type"),
    _s("Point :: struct { x, y: int }", "a struct"),
    _s("value, ok := table[key]", "two returns"),
    _s("if !ok do return", "the do form for one line"),
    _s("defer delete(items)", "at scope exit"),
    _s("fmt.println(\"total is\", total)", "prints with spaces between"),
    _s("data, err := os.read_entire_file(path)", "error as a value"),
)


# ── Assembly ─────────────────────────────────────────────────

ASSEMBLY_CODE: tuple[Passage, ...] = (
    _s("section .data", "where the bytes live"),
    _s('msg db "hello", 10', "define bytes, then a newline"),
    _s("len equ $ - msg", "the assembler does the arithmetic"),
    _s("section .text", "where the code lives"),
    _s("global _start", "the entry point, exported"),
    _s("mov rax, 1", "the write syscall number"),
    _s("mov rdi, 1", "file descriptor one, stdout"),
    _s("syscall", "ask the kernel"),
    _s("cmp rbx, rcx", "subtract, keep only the flags"),
    _s("jne .loop", "jump if the flags say not equal"),
    _s("push rbp", "save the caller's frame"),
    _s("xor rdi, rdi", "the shortest way to zero"),
)


BY_LANGUAGE: dict[str, tuple[Passage, ...]] = {
    "go": GO_CODE,
    "php": PHP_CODE,
    "lua": LUA_CODE,
    "zig": ZIG_CODE,
    "java": JAVA_CODE,
    "kotlin": KOTLIN_CODE,
    "ruby": RUBY_CODE,
    "csharp": CSHARP_CODE,
    "swift": SWIFT_CODE,
    "scala": SCALA_CODE,
    "haskell": HASKELL_CODE,
    "ocaml": OCAML_CODE,
    "elixir": ELIXIR_CODE,
    "lisp": LISP_CODE,
    "odin": ODIN_CODE,
    "assembly": ASSEMBLY_CODE,
}
