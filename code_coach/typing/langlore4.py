"""The systems languages, and the one underneath all of them.

Same rules as langlore2 and langlore3: a fact per line, true about the
language rather than measured here.
"""

from __future__ import annotations

from code_coach.typing.langlore2 import Passage, _p

# ── C# ───────────────────────────────────────────────────────

CSHARP: tuple[Passage, ...] = (
    _p("C# was designed at Microsoft by Anders Hejlsberg, who had already "
       "written Turbo Pascal and Delphi.", "C# design"),
    _p("It compiles to IL and runs on the CLR, which JIT compiles it to "
       "machine code as the program runs.", "C# internals"),
    _p("Generics are not erased. A List of int really is a list of ints at "
       "run time, unlike on the JVM.", "C# internals"),
    _p("LINQ put query syntax into the language in 2007, and the method "
       "form is what almost everyone actually writes.", "C# design"),
    _p("async and await began here and were copied into JavaScript, "
       "Python, Rust and most of the rest.", "C# design"),
    _p("A struct is a value type and a class is a reference type, and "
       "which one you chose changes what assignment means.",
       "C# internals"),
    _p("Nullable reference types arrived in 8 and are a compiler warning "
       "rather than a run-time guarantee.", "C# design"),
    _p("The null-conditional operator returns null instead of throwing, "
       "and the null-coalescing one supplies a default.", "C# syntax"),
    _p("var infers the type of a local, and the style debate about when to "
       "use it has run for nearly twenty years.", "C# conventions"),
    _p("Properties look like fields and are really methods, which is why "
       "adding logic to one breaks nothing.", "C# design"),
    _p("using declares a scope that disposes the object at the end, which "
       "is how files and connections get closed.", "C# syntax"),
    _p("Records arrived in 9 with value equality and a with expression for "
       "copying one that differs in a field.", "C# syntax"),
    _p("Pattern matching has grown every version since 7, and switch is "
       "now an expression that returns a value.", "C# syntax"),
    _p(".NET Core made the platform cross-platform and open source, which "
       "changed who the language was for.", "C# design"),
    _p("Span lets you work over a slice of memory without copying it, "
       "which is how modern C# gets fast without pointers.",
       "C# performance"),
    _p("unsafe blocks allow real pointers, and almost no application code "
       "ever needs one.", "C# design"),
    _p("Extension methods add a method to a type you do not own, which is "
       "the whole mechanism LINQ is built on.", "C# design"),
    _p("The default equality for a class is reference equality, so two "
       "identical objects are not equal until you say so.", "C# gotchas"),
    _p("Top-level statements in 9 removed the ceremony, so a program can "
       "be one line again.", "C# syntax"),
    _p("Value types on the stack and reference types on the heap is the "
       "usual summary, and the truth is more complicated.",
       "C# internals"),
)


# ── Swift ────────────────────────────────────────────────────

SWIFT: tuple[Passage, ...] = (
    _p("Swift was announced by Apple in 2014 as the replacement for "
       "Objective-C, and open sourced the year after.", "Swift design"),
    _p("Optionals are in the type system: String and String? are different "
       "types and the compiler enforces the difference.", "Swift design"),
    _p("if let and guard let unwrap an optional into a name, and guard "
       "leaves the scope when it fails.", "Swift syntax"),
    _p("The exclamation mark force unwraps and crashes when the value is "
       "nil, which is deliberately loud.", "Swift conventions"),
    _p("let is a constant and var is not, and the compiler suggests "
       "changing var to let whenever it can.", "Swift conventions"),
    _p("Structs are values and classes are references, and the guidance is "
       "to reach for a struct first.", "Swift design"),
    _p("Memory is managed by reference counting rather than a collector, "
       "so a reference cycle leaks until you break it.",
       "Swift internals"),
    _p("weak and unowned are how you break that cycle, and choosing "
       "between them is about whether nil is possible.", "Swift gotchas"),
    _p("Protocols with associated types are powerful and are also where "
       "the error messages get long.", "Swift design"),
    _p("Value types are copied on write, so passing a large array is cheap "
       "until someone changes it.", "Swift performance"),
    _p("Enums carry associated values, so a case can hold data and the "
       "switch can destructure it.", "Swift syntax"),
    _p("Errors are thrown and caught, but a throwing function must be "
       "marked and its call site must say try.", "Swift design"),
    _p("Trailing closure syntax moves the last argument outside the "
       "parentheses, which is why SwiftUI reads as it does.",
       "Swift syntax"),
    _p("SwiftUI describes the interface as a value and lets the framework "
       "work out the changes.", "Swift design"),
    _p("Async and await arrived in 5.5 along with actors, which protect "
       "their own state from concurrent access.", "Swift concurrency"),
    _p("String indices are not integers, because a character can be "
       "several bytes and Swift will not pretend otherwise.",
       "Swift gotchas"),
    _p("Protocol extensions provide default implementations, which is how "
       "the standard library shares behaviour.", "Swift design"),
    _p("Type inference is strong, and a long expression with several "
       "literals is where compile times go to die.", "Swift performance"),
    _p("defer runs a block when the scope exits, whichever way it "
       "exits.", "Swift syntax"),
    _p("The language grew a full evolution process in public, and every "
       "change since has a numbered proposal behind it.", "Swift design"),
)


# ── Zig ──────────────────────────────────────────────────────

ZIG: tuple[Passage, ...] = (
    _p("Zig was started by Andrew Kelley in 2015 as a language to replace "
       "C rather than to sit above it.", "Zig design"),
    _p("There is no hidden control flow. No exceptions, no operator "
       "overloading, no destructors running behind your back.",
       "Zig design"),
    _p("There are no hidden allocations either: a function that needs "
       "memory takes an allocator as an argument.", "Zig design"),
    _p("comptime runs ordinary Zig at compile time, and it is how generics "
       "work without a separate template language.", "Zig design"),
    _p("Errors are values in an error union, and try is shorthand for "
       "returning one up the chain.", "Zig syntax"),
    _p("An unused variable is a compile error, which keeps a file from "
       "drifting out of date quietly.", "Zig conventions"),
    _p("defer runs at scope exit and errdefer runs only when the scope is "
       "left because of an error.", "Zig syntax"),
    _p("Optionals are a question mark on the type and are separate from "
       "errors, so absence and failure do not get confused.",
       "Zig design"),
    _p("The compiler ships a C compiler, so zig cc is a working "
       "cross-compiling toolchain on its own.", "Zig internals"),
    _p("Cross compilation is the headline feature: any target from any "
       "host, without hunting for a toolchain.", "Zig internals"),
    _p("Build scripts are written in Zig rather than a separate build "
       "language.", "Zig conventions"),
    _p("Safety checks are on in debug and off in release-fast, and which "
       "build mode you chose changes what happens on overflow.",
       "Zig gotchas"),
    _p("Integer overflow is checked in debug and is undefined in "
       "release-fast, so the wrapping operators exist to say you meant "
       "it.", "Zig gotchas"),
    _p("Slices carry a pointer and a length together, which is the thing C "
       "arrays never did.", "Zig design"),
    _p("There is no preprocessor and no macros, because comptime already "
       "does what they were for.", "Zig design"),
    _p("The language is pre-1.0 and still changes, so code from two years "
       "ago often needs edits.", "Zig gotchas"),
    _p("Struct fields have no guaranteed order unless the struct is marked "
       "extern or packed.", "Zig internals"),
    _p("Testing is built into the language with test blocks, run by zig "
       "test with no framework.", "Zig conventions"),
    _p("Bun is written in Zig, which is a large part of how the language "
       "reached people outside systems work.", "Zig design"),
    _p("The mascot is a lizard named Zero, and the foundation is a "
       "non-profit funded by donations.", "Zig design"),
)


# ── Odin ─────────────────────────────────────────────────────

ODIN: tuple[Passage, ...] = (
    _p("Odin was started by Ginger Bill in 2016, aimed at data-oriented "
       "programming and games rather than general use.", "Odin design"),
    _p("It is deliberately a C alternative with modern ergonomics rather "
       "than a language with a large type system.", "Odin design"),
    _p("Allocators are part of the context, which is passed implicitly, so "
       "changing how a subtree allocates is one line.", "Odin design"),
    _p("The context system also carries the logger and the temporary "
       "allocator, which is unusual and very practical.", "Odin design"),
    _p("Arrays know their length, and slices carry pointer and length "
       "together as one value.", "Odin design"),
    _p("There are no classes and no inheritance. Structs and procedures "
       "are what you get.", "Odin design"),
    _p("Multiple return values are ordinary, and the second is usually an "
       "ok flag or an error.", "Odin syntax"),
    _p("defer runs at scope exit, in reverse order, the same idea Go and "
       "Zig both use.", "Odin syntax"),
    _p("Array programming is built in: adding two fixed arrays adds them "
       "element by element.", "Odin design"),
    _p("Swizzling lets you read v.xy from a four-component vector, which "
       "is a graphics idea in the base language.", "Odin design"),
    _p("The vendor collection ships bindings for OpenGL, Vulkan, SDL and "
       "raylib, because games are the target.", "Odin conventions"),
    _p("There is no package manager by design; you vendor what you need.",
       "Odin conventions"),
    _p("Declarations read name colon type, and the colon equals form "
       "infers the type.", "Odin syntax"),
    _p("A constant is declared with double colon, which also declares "
       "procedures and types.", "Odin syntax"),
    _p("Compilation is fast, which is a stated goal rather than a side "
       "effect.", "Odin performance"),
    _p("There is no built-in garbage collector, and the temporary "
       "allocator covers most of what one would be used for.",
       "Odin internals"),
    _p("Unions are tagged and matched on, rather than being the "
       "reinterpret-the-bytes kind C has.", "Odin design"),
    _p("or_return propagates an error upward, which is Odin's answer to "
       "the same problem try solves in Zig.", "Odin syntax"),
    _p("The standard library is called core, and the graphics and system "
       "bindings live separately in vendor.", "Odin conventions"),
    _p("The language is small enough to read the whole specification in an "
       "afternoon, which is the point.", "Odin design"),
)


# ── Assembly ─────────────────────────────────────────────────

ASSEMBLY: tuple[Passage, ...] = (
    _p("Assembly is a one-to-one naming of machine instructions, so an "
       "assembler translates rather than compiles.", "Assembly design"),
    _p("There is no one assembly language. Every architecture has its own, "
       "and x86 and ARM look nothing alike.", "Assembly design"),
    _p("Intel syntax puts the destination first and AT&T syntax puts it "
       "last, which is a lasting source of confusion.", "Assembly syntax"),
    _p("Registers are the fastest storage there is, and there are very few "
       "of them, which is what makes the work hard.",
       "Assembly internals"),
    _p("A label is just an address with a name, and a jump to it is how "
       "every loop and branch is built.", "Assembly syntax"),
    _p("The stack grows downward on x86, so pushing subtracts from the "
       "stack pointer.", "Assembly internals"),
    _p("A calling convention decides which registers carry arguments and "
       "who restores them, and it differs by platform.",
       "Assembly conventions"),
    _p("Flags are set as a side effect of arithmetic, and a conditional "
       "jump reads them rather than a comparison.", "Assembly design"),
    _p("cmp is a subtraction that throws away the answer and keeps the "
       "flags.", "Assembly syntax"),
    _p("There are no types. A register holds bits, and the instruction you "
       "chose decides what they mean.", "Assembly design"),
    _p("x86 is a variable-length instruction set, so you cannot tell where "
       "an instruction starts by counting backwards.",
       "Assembly internals"),
    _p("ARM is fixed width and load-store, so arithmetic happens only "
       "between registers.", "Assembly internals"),
    _p("Modern processors reorder instructions and execute them out of "
       "order, so the assembly you wrote is not the order it runs.",
       "Assembly performance"),
    _p("Hand-written assembly rarely beats a good compiler now, except "
       "where it uses instructions the compiler will not.",
       "Assembly performance"),
    _p("SIMD instructions work on several values at once, which is where "
       "hand-written assembly still earns its keep.",
       "Assembly performance"),
    _p("A system call is how a program asks the kernel to do something, "
       "and the number goes in a register.", "Assembly internals"),
    _p("The nop instruction does nothing and exists for alignment and for "
       "patching code in place.", "Assembly design"),
    _p("Reading disassembly is the practical skill: you meet it in a "
       "debugger far more often than you write it.",
       "Assembly conventions"),
    _p("The first assembler was written by Kathleen Booth around 1947, "
       "before most of the machines that would need one.",
       "Assembly design"),
    _p("Every language on this list becomes assembly eventually, which is "
       "the reason to be able to read it.", "Assembly design"),
)
