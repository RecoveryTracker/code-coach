"""Per-language lore for the languages the workbook does not run.

The workbook only carries a language it can execute, because every page
there is checked by running the reference answer. Typing has no such
requirement: a passage is text, and the only thing that has to be true
about it is that it is true.

So these are the languages worth knowing about before, or instead of,
writing them. Same shape as langlore: a fact per line, short enough to
type in one go, with the category as the note underneath.

Everything here is a claim about a language rather than a snippet to copy.
Where a line says what some code does, it is describing behaviour that is
documented and stable, not something measured on this machine — no
compiler for any of these is installed here, and a typing passage that
asserted a benchmark would be a claim I could not stand behind.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Passage:
    text: str
    source: str


def _p(text: str, source: str) -> Passage:
    return Passage(text, source)


# ── Go ───────────────────────────────────────────────────────

GO: tuple[Passage, ...] = (
    _p("Go was designed at Google by Robert Griesemer, Rob Pike and Ken "
       "Thompson, and the first goal was compile speed.", "Go design"),
    _p("There is one loop keyword. for covers the counted loop, the while "
       "loop and the infinite loop, and there is no other.", "Go syntax"),
    _p("An unused import is a compile error, not a warning. The language "
       "would rather stop than let a file drift out of date.", "Go design"),
    _p("gofmt settles formatting arguments by having no options. Everyone "
       "runs it, so every Go file looks the same.", "Go conventions"),
    _p("Errors are values you return, not exceptions you throw, so the "
       "handling sits where the failure happened.", "Go design"),
    _p("if err != nil is the most typed line in the language, and the "
       "verbosity is the point: nothing fails silently.", "Go conventions"),
    _p("A goroutine is started with the word go in front of a call, and "
       "costs a few kilobytes rather than a thread.", "Go concurrency"),
    _p("Channels pass values between goroutines. Do not communicate by "
       "sharing memory; share memory by communicating.", "Go concurrency"),
    _p("defer runs a call when the function returns, however it returns, "
       "which is where files get closed.", "Go syntax"),
    _p("A capital first letter exports a name. Visibility is spelling "
       "rather than a keyword.", "Go conventions"),
    _p("There are no classes. A struct plus methods with a receiver is "
       "what you have, and it is enough.", "Go design"),
    _p("Interfaces are satisfied implicitly. A type never declares that it "
       "implements one; it just has the methods.", "Go design"),
    _p("The zero value is meant to be useful. A declared struct is ready "
       "to use, and a nil map reads as empty.", "Go design"),
    _p("Writing to a nil map panics even though reading one does not, "
       "which is the asymmetry that catches people.", "Go gotchas"),
    _p("A slice is a view onto an array, so appending can either share the "
       "old memory or quietly copy it.", "Go internals"),
    _p("Generics arrived in 1.18, twelve years in, after a long argument "
       "about whether the cost was worth it.", "Go design"),
    _p("The standard library ships an HTTP server good enough for "
       "production, which is why so many Go programs have no framework.",
       "Go conventions"),
    _p("Compilation produces one static binary with no runtime to install, "
       "which is most of why it took over deployment.", "Go internals"),
    _p("panic is for programmer error and recover is rare. A library that "
       "panics across its own boundary is considered broken.",
       "Go conventions"),
    _p("The mascot is a gopher, drawn by Renee French, and it is on "
       "roughly every conference slide.", "Go design"),
)


# ── Java ─────────────────────────────────────────────────────

JAVA: tuple[Passage, ...] = (
    _p("Java was released by Sun in 1995 with the promise of write once, "
       "run anywhere, which the JVM mostly delivered.", "Java design"),
    _p("Source compiles to bytecode, and the JVM turns the hot parts into "
       "machine code while the program runs.", "Java internals"),
    _p("Everything lives in a class, which is why the shortest program is "
       "longer here than almost anywhere else.", "Java syntax"),
    _p("Primitives and objects are different kinds of thing. int is not "
       "Integer, and the boxing between them costs.", "Java internals"),
    _p("Comparing strings with == compares references. equals is what you "
       "meant, and the first bug everyone writes.", "Java gotchas"),
    _p("Checked exceptions must be declared or caught, an idea Java tried "
       "that almost no language since has copied.", "Java design"),
    _p("Generics are erased at compile time, so a List of String and a "
       "List of Integer are the same class at run time.", "Java internals"),
    _p("The garbage collector is the reason you rarely think about memory, "
       "and the reason you sometimes think about nothing else.",
       "Java performance"),
    _p("null was called a billion dollar mistake by Tony Hoare, who "
       "introduced it in 1965 and later apologised.", "Java design"),
    _p("Optional arrived in 8 to give a method a way of saying it might "
       "not return anything.", "Java conventions"),
    _p("Lambdas and streams arrived in 8 too, and turned loops into "
       "pipelines for a generation of code.", "Java syntax"),
    _p("var lets the compiler infer a local type, which is late but "
       "welcome in a language this ceremonious.", "Java syntax"),
    _p("A record declares data with no boilerplate: fields, constructor, "
       "equals and hashCode from one line.", "Java syntax"),
    _p("Override equals and you must override hashCode, or your object "
       "will vanish inside a HashMap.", "Java gotchas"),
    _p("The classpath decides which version of a class wins, and two "
       "copies of the same library is its own genre of bug.",
       "Java gotchas"),
    _p("String concatenation in a loop builds a new object each time, "
       "which is what StringBuilder exists for.", "Java performance"),
    _p("finally runs whether or not an exception was thrown, and "
       "try-with-resources closes things without it.", "Java syntax"),
    _p("The JVM runs Kotlin, Scala, Clojure and Groovy too, so the "
       "platform outgrew the language some time ago.", "Java design"),
    _p("public static void main is four keywords before the program "
       "starts, and every one of them means something.", "Java syntax"),
    _p("Interfaces gained default methods in 8 so an interface could grow "
       "without breaking everyone who implemented it.", "Java design"),
)


# ── Kotlin ───────────────────────────────────────────────────

KOTLIN: tuple[Passage, ...] = (
    _p("Kotlin came from JetBrains in 2011, named after an island near St "
       "Petersburg, and targets the JVM.", "Kotlin design"),
    _p("Null safety is in the type system: String and String? are "
       "different types and the compiler enforces it.", "Kotlin design"),
    _p("The safe call ?. returns null instead of throwing, and the elvis "
       "operator ?: supplies a value when it does.", "Kotlin syntax"),
    _p("!! asserts a value is not null and throws if it is, which is "
       "deliberately ugly so you notice writing it.", "Kotlin conventions"),
    _p("val is a read-only reference and var is not, and the convention is "
       "to reach for val first.", "Kotlin conventions"),
    _p("Data classes generate equals, hashCode, toString and copy from the "
       "constructor line.", "Kotlin syntax"),
    _p("A when expression replaces switch and returns a value, and the "
       "compiler checks a sealed type is covered.", "Kotlin syntax"),
    _p("Extension functions add a method to a type you do not own, "
       "resolved statically rather than by dispatch.", "Kotlin design"),
    _p("Coroutines make suspending functions look sequential, and suspend "
       "is a keyword the compiler rewrites around.", "Kotlin concurrency"),
    _p("Semicolons are optional, and the style guide says leave them out.",
       "Kotlin conventions"),
    _p("Everything is an expression, so if and when both hand back a "
       "value and there is no ternary operator.", "Kotlin syntax"),
    _p("Classes are final unless marked open, which is the opposite of "
       "Java and deliberately so.", "Kotlin design"),
    _p("Kotlin became Google's preferred language for Android in 2019, "
       "which decided its future.", "Kotlin design"),
    _p("Interoperability with Java was a design requirement, so a Kotlin "
       "file and a Java file can call each other.", "Kotlin design"),
    _p("Platform types are values from Java the compiler cannot vouch "
       "for, which is where a null still gets through.", "Kotlin gotchas"),
    _p("A single-expression function drops the braces and the return: fun "
       "double(n: Int) = n * 2.", "Kotlin syntax"),
    _p("Named arguments and defaults remove most of the reason to write "
       "overloads.", "Kotlin conventions"),
    _p("String templates put the value in the string with a dollar sign "
       "rather than concatenation.", "Kotlin syntax"),
    _p("let, run, apply, also and with are the scope functions, and "
       "choosing between them is half of learning the style.",
       "Kotlin conventions"),
    _p("Kotlin compiles to JVM bytecode, to JavaScript, and to native "
       "code, though the JVM is where nearly everyone is.",
       "Kotlin internals"),
)


# ── Ruby ─────────────────────────────────────────────────────

RUBY: tuple[Passage, ...] = (
    _p("Ruby was made by Yukihiro Matsumoto in 1995, and he says he "
       "designed it to make programmers happy.", "Ruby design"),
    _p("Everything is an object, including numbers, so 3.times is a method "
       "call on the number three.", "Ruby design"),
    _p("Blocks are passed to methods with do and end or braces, and are "
       "why iteration reads the way it does.", "Ruby syntax"),
    _p("A method name ending in a question mark returns a boolean, by "
       "convention rather than by rule.", "Ruby conventions"),
    _p("A method name ending in an exclamation mark changes the receiver "
       "or is otherwise the dangerous one of a pair.", "Ruby conventions"),
    _p("Parentheses are usually optional, which makes the language read "
       "like prose and parse in ways that surprise you.", "Ruby gotchas"),
    _p("Only nil and false are falsy. Zero and the empty string are both "
       "true, unlike almost every neighbouring language.", "Ruby gotchas"),
    _p("Classes are open: you can reopen String and add a method, which is "
       "powerful and is how monkey patching got its name.", "Ruby design"),
    _p("method_missing catches a call to something that does not exist, "
       "which is how much of Rails magic works.", "Ruby internals"),
    _p("Symbols are interned strings written with a leading colon, used "
       "for keys and names because they compare by identity.",
       "Ruby internals"),
    _p("The last expression is the return value, so an explicit return is "
       "usually a sign something unusual is happening.", "Ruby conventions"),
    _p("Rails arrived in 2004 and made Ruby famous, to the point where "
       "many people met one and thought it was the other.", "Ruby design"),
    _p("Modules give you mixins: include pulls methods into a class "
       "without inheritance.", "Ruby design"),
    _p("The spaceship operator returns minus one, zero or one, and is what "
       "sort_by is built on.", "Ruby syntax"),
    _p("String interpolation uses a hash and braces, and only works in "
       "double quotes.", "Ruby syntax"),
    _p("attr_accessor writes the getter and setter for you, and is itself "
       "just a method that defines methods.", "Ruby internals"),
    _p("The global interpreter lock means threads do not run Ruby code in "
       "parallel, which shaped how Ruby scales.", "Ruby internals"),
    _p("Ruby 3 set out to be three times faster than Ruby 2, and shipped a "
       "JIT compiler working toward it.", "Ruby performance"),
    _p("unless is if not, spelled so the common case reads forwards, and "
       "the style guide says never pair it with else.", "Ruby conventions"),
    _p("A range with three dots excludes its end and one with two does "
       "not, which is one character deciding a boundary.", "Ruby gotchas"),
)


# ── PHP ──────────────────────────────────────────────────────

PHP: tuple[Passage, ...] = (
    _p("PHP began in 1994 as Rasmus Lerdorf's set of CGI scripts for "
       "counting visits to his own page.", "PHP design"),
    _p("A file is HTML until it meets an opening tag, which is why the "
       "language spread through the early web so fast.", "PHP design"),
    _p("Variables start with a dollar sign, which makes them findable in a "
       "page of markup.", "PHP syntax"),
    _p("The double equals compares loosely and the triple equals does not, "
       "and using the wrong one is the classic PHP bug.", "PHP gotchas"),
    _p("In PHP 8 a string compared loosely to a number no longer converts "
       "the string first, which fixed a decade of surprises.",
       "PHP gotchas"),
    _p("An array is an ordered map. There is no separate list type, and "
       "the same structure does both jobs.", "PHP internals"),
    _p("Function names are case-insensitive and variable names are not, "
       "which is a fact worth knowing before it bites.", "PHP gotchas"),
    _p("Composer arrived in 2012 and gave PHP the dependency management "
       "the language had spent fifteen years without.", "PHP conventions"),
    _p("PSR standards settled autoloading and formatting arguments the "
       "community had been having since the beginning.", "PHP conventions"),
    _p("Type declarations became real in 7 and got stricter in 8, so "
       "modern PHP looks very little like the PHP people remember.",
       "PHP design"),
    _p("The null coalescing operator ?? returns the right side when the "
       "left is null or missing, without a warning.", "PHP syntax"),
    _p("Named arguments arrived in 8, so a function with six optional "
       "parameters is finally callable.", "PHP syntax"),
    _p("Match is like switch but compares strictly and returns a value, "
       "and does not fall through.", "PHP syntax"),
    _p("Attributes in 8 gave the language real annotations, replacing a "
       "generation of parsing them out of comments.", "PHP design"),
    _p("Most PHP runs per request and then throws everything away, which "
       "is why a memory leak rarely matters.", "PHP internals"),
    _p("JIT compilation arrived in 8 and helps computation far more than "
       "it helps the typical page that talks to a database.",
       "PHP performance"),
    _p("Arrow functions with fn capture the outer scope automatically, "
       "which the older closure syntax needed use for.", "PHP syntax"),
    _p("WordPress runs on PHP, which is a large part of why the language "
       "still serves a great deal of the web.", "PHP design"),
    _p("Enums arrived in 8.1, and before them the pattern was class "
       "constants and a good deal of hoping.", "PHP design"),
    _p("The elephant logo is called elePHPant, which tells you most of "
       "what you need to know about the community.", "PHP design"),
)


# ── Lua ──────────────────────────────────────────────────────

LUA: tuple[Passage, ...] = (
    _p("Lua came out of a Brazilian university in 1993, and the name means "
       "moon in Portuguese.", "Lua design"),
    _p("It was built to be embedded, so the whole interpreter is small "
       "enough to ship inside another program.", "Lua design"),
    _p("Tables are the only data structure. Arrays, dictionaries, objects "
       "and modules are all one thing.", "Lua design"),
    _p("Indices start at one rather than zero, which is the single fact "
       "that catches every visitor.", "Lua gotchas"),
    _p("There are no classes. Metatables let a table borrow behaviour from "
       "another, and that is how objects are built.", "Lua design"),
    _p("nil removes a key. Assigning nil to a table entry deletes it "
       "rather than storing an empty value.", "Lua internals"),
    _p("Only nil and false are falsy, so zero and the empty string are "
       "both true.", "Lua gotchas"),
    _p("Functions are values, can be stored in tables, and closures "
       "capture the variables around them.", "Lua design"),
    _p("Coroutines are built in and cooperative: one yields and another "
       "resumes, with no threads involved.", "Lua concurrency"),
    _p("The standard library is deliberately tiny, because whatever "
       "embeds Lua is expected to supply the rest.", "Lua design"),
    _p("Roblox, World of Warcraft and Neovim all take Lua as their "
       "scripting language, which is the niche it won.", "Lua design"),
    _p("LuaJIT is a separate implementation whose speed made Lua a serious "
       "choice for hot code.", "Lua performance"),
    _p("Variables are global unless declared local, which is the default "
       "everyone wishes were the other way round.", "Lua gotchas"),
    _p("The concatenation operator is two dots, because the plus sign is "
       "kept for arithmetic alone.", "Lua syntax"),
    _p("Not equal is written with a tilde rather than an exclamation "
       "mark.", "Lua syntax"),
    _p("A function can return several values, and the caller decides how "
       "many to keep.", "Lua syntax"),
    _p("The length operator on a table with a hole in it may stop at the "
       "hole, so a sparse array has no reliable length.", "Lua gotchas"),
    _p("There is no integer division operator until 5.3, and no integer "
       "type at all before it.", "Lua internals"),
    _p("pcall runs a function and catches its error, which is the whole "
       "of exception handling here.", "Lua syntax"),
    _p("The reference implementation is around thirty thousand lines of C, "
       "which is why it goes everywhere.", "Lua internals"),
)
