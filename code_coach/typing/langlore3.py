"""More per-language lore: the functional languages, and the systems ones.

Same rules as langlore2. A fact per line, short enough to type in one go,
true about the language rather than measured on this machine.
"""

from __future__ import annotations

from code_coach.typing.langlore2 import Passage, _p

# ── Haskell ──────────────────────────────────────────────────

HASKELL: tuple[Passage, ...] = (
    _p("Haskell was designed by committee from 1987 to unify the "
       "scattered lazy functional languages into one.", "Haskell design"),
    _p("Evaluation is lazy: nothing is computed until something asks, so "
       "an infinite list is an ordinary value.", "Haskell design"),
    _p("Functions are pure. Given the same arguments they return the same "
       "answer and change nothing else.", "Haskell design"),
    _p("Types are inferred, so most functions need no annotation, and most "
       "Haskell programmers write one anyway.", "Haskell conventions"),
    _p("The type signature is written on its own line above the "
       "definition, with two colons meaning has type.", "Haskell syntax"),
    _p("Every function of two arguments is really a function returning a "
       "function, which is what currying means.", "Haskell design"),
    _p("Pattern matching defines a function case by case, and the compiler "
       "warns when the cases do not cover everything.", "Haskell syntax"),
    _p("IO is a type, so a function that touches the world says so in its "
       "signature and cannot pretend otherwise.", "Haskell design"),
    _p("A monad is an interface for sequencing, and do notation is sugar "
       "over it rather than a special form.", "Haskell design"),
    _p("Maybe replaces null: a value is Just something or Nothing, and the "
       "compiler makes you handle both.", "Haskell design"),
    _p("Either carries an error on the left and a result on the right, "
       "which is how failure travels without exceptions.", "Haskell design"),
    _p("Lists are singly linked, so the head is cheap and the last element "
       "is not.", "Haskell internals"),
    _p("Laziness can hold onto memory: a thunk that is never forced keeps "
       "everything it referred to alive.", "Haskell gotchas"),
    _p("foldl' with the apostrophe is the strict one, and using foldl "
       "instead is the classic space leak.", "Haskell gotchas"),
    _p("Typeclasses group types by what they can do, which is where "
       "Rust's traits and Swift's protocols came from.", "Haskell design"),
    _p("The dollar sign applies a function and saves a pair of brackets, "
       "and the dot composes two functions.", "Haskell syntax"),
    _p("where attaches helper definitions to the function above them, "
       "which is how local names avoid the top level.", "Haskell syntax"),
    _p("GHC is the compiler everyone means, and its extensions have become "
       "the language in practice.", "Haskell internals"),
    _p("The logo is a lambda inside a bind operator, which is the language "
       "describing itself.", "Haskell design"),
    _p("Software transactional memory came from Haskell, because purity "
       "makes retrying a block of work safe.", "Haskell concurrency"),
)


# ── OCaml ────────────────────────────────────────────────────

OCAML: tuple[Passage, ...] = (
    _p("OCaml comes from INRIA in France and descends from ML, the "
       "language written to prove theorems in the 1970s.", "OCaml design"),
    _p("Evaluation is eager, unlike Haskell, so it is easier to reason "
       "about when a thing actually happens.", "OCaml design"),
    _p("It is functional first but not pure: mutation is available when "
       "you want it and marked when you use it.", "OCaml design"),
    _p("Type inference is complete, so a whole program can be written with "
       "no annotations and still be fully typed.", "OCaml design"),
    _p("Variants and pattern matching together are the core idea, and the "
       "compiler tells you which case you forgot.", "OCaml syntax"),
    _p("A record field is immutable unless declared mutable, and then it "
       "is assigned with an arrow rather than an equals.", "OCaml syntax"),
    _p("The module system is the famous part: modules take modules as "
       "arguments, which is what a functor is.", "OCaml design"),
    _p("Integers are 63 bits rather than 64, because one bit tells the "
       "collector whether a word is a pointer.", "OCaml internals"),
    _p("There are separate operators for integer and float arithmetic, so "
       "plus dot adds floats.", "OCaml gotchas"),
    _p("Equals compares structurally and double equals compares identity, "
       "which is the reverse of what most people guess.", "OCaml gotchas"),
    _p("Compilation is fast and the output is fast, which is why it turns "
       "up in compilers and trading systems.", "OCaml performance"),
    _p("Rust's first compiler was written in OCaml, before Rust could "
       "compile itself.", "OCaml design"),
    _p("Multicore support landed in OCaml 5 in 2022, after most of a "
       "decade of work on the runtime.", "OCaml concurrency"),
    _p("The pipe operator passes a value into a function and reads left to "
       "right, which is why chains are written with it.", "OCaml syntax"),
    _p("An option is Some or None, and the compiler will not let you "
       "unwrap one without saying what None means.", "OCaml design"),
    _p("Semicolons sequence expressions and double semicolons end a "
       "top-level phrase in the REPL, which is a common confusion.",
       "OCaml gotchas"),
    _p("Lists are immutable and singly linked; arrays are mutable and "
       "fixed length. The distinction is deliberate.", "OCaml internals"),
    _p("Labelled arguments let a caller name a parameter, and optional "
       "ones have defaults, both checked by the type system.",
       "OCaml syntax"),
    _p("The standard library is small on purpose, and most projects add "
       "one of the larger community replacements.", "OCaml conventions"),
    _p("Tail calls are optimised, so recursion is the ordinary way to "
       "loop rather than a risk.", "OCaml internals"),
)


# ── Scala ────────────────────────────────────────────────────

SCALA: tuple[Passage, ...] = (
    _p("Scala was created by Martin Odersky in 2004, who had already "
       "written the Java compiler generics went into.", "Scala design"),
    _p("It set out to join object orientation and functional programming "
       "rather than choose between them.", "Scala design"),
    _p("Scala 3 arrived in 2021 and made indentation significant, "
       "optional braces and all.", "Scala syntax"),
    _p("val is immutable and var is not, and the community reaches for "
       "val to the point that var reads as a warning.",
       "Scala conventions"),
    _p("Case classes give you equality, a constructor without new, and "
       "pattern matching, from one line.", "Scala syntax"),
    _p("Pattern matching destructures as it branches, so match does the "
       "work of switch, cast and unpack at once.", "Scala syntax"),
    _p("Traits are interfaces that can carry implementation, and a class "
       "can mix in several.", "Scala design"),
    _p("Implicits were the most powerful and most complained about "
       "feature, and Scala 3 split them into named pieces.",
       "Scala design"),
    _p("given and using replaced implicit, so what is being passed "
       "invisibly is at least written down.", "Scala syntax"),
    _p("Option, Try and Either are the three ways a value can be absent or "
       "wrong, and each is a type rather than a convention.",
       "Scala design"),
    _p("Everything is an expression, so if returns a value and there is no "
       "need for a ternary.", "Scala syntax"),
    _p("The collections library is famously large, and every method on it "
       "returns a new collection rather than changing one.",
       "Scala conventions"),
    _p("for comprehensions are sugar over map, flatMap and filter, which "
       "is why they work on anything that has them.", "Scala design"),
    _p("Type inference is strong locally and deliberately weaker at "
       "public boundaries, where you write the type down.",
       "Scala conventions"),
    _p("Compilation is slow, and it is the first complaint of everyone "
       "who works in a large Scala codebase.", "Scala performance"),
    _p("Spark is written in Scala, which is most of why the language "
       "arrived in data engineering.", "Scala design"),
    _p("Higher-kinded types let you abstract over things like List "
       "itself, not just over what is inside it.", "Scala design"),
    _p("An underscore is a placeholder for an argument, so a plus b can "
       "be written with two of them and no names.", "Scala syntax"),
    _p("Scala runs on the JVM, and also compiles to JavaScript and to "
       "native code through LLVM.", "Scala internals"),
    _p("Enums became a first-class declaration in 3, replacing a sealed "
       "trait and a set of case objects.", "Scala syntax"),
)


# ── Elixir ───────────────────────────────────────────────────

ELIXIR: tuple[Passage, ...] = (
    _p("Elixir was written by Jose Valim in 2011 to put a friendlier "
       "language on top of the Erlang virtual machine.", "Elixir design"),
    _p("The BEAM runs millions of lightweight processes, each with its own "
       "heap, scheduled by the runtime rather than the OS.",
       "Elixir concurrency"),
    _p("Processes share nothing and communicate by message, which is why a "
       "crash in one does not corrupt another.", "Elixir concurrency"),
    _p("Let it crash is the actual advice: a supervisor restarts the "
       "process rather than the code defending against everything.",
       "Elixir conventions"),
    _p("Data is immutable, so a function that appears to change a list is "
       "returning a new one.", "Elixir design"),
    _p("The pipe operator threads a value through a chain of functions and "
       "is the most characteristic thing in the language.",
       "Elixir syntax"),
    _p("Pattern matching is what the equals sign does. It asserts a shape "
       "rather than assigning a value.", "Elixir design"),
    _p("A function can be defined several times with different patterns, "
       "and the first that matches runs.", "Elixir syntax"),
    _p("Atoms are constants that are their own name, written with a "
       "leading colon, and used everywhere as tags.", "Elixir syntax"),
    _p("The convention is to return a tuple tagged ok or error, and to "
       "match on it rather than raise.", "Elixir conventions"),
    _p("A bang at the end of a function name means it raises instead of "
       "returning an error tuple.", "Elixir conventions"),
    _p("Macros run at compile time and can generate code, which is how "
       "much of Phoenix and Ecto is built.", "Elixir internals"),
    _p("Hot code upgrades are possible on the BEAM: a running system can "
       "be given new code without stopping.", "Elixir internals"),
    _p("Phoenix LiveView keeps a process per connection and sends "
       "diffs, which is why it needs no client framework.",
       "Elixir design"),
    _p("Erlang was built at Ericsson for telephone switches, so nine nines "
       "of uptime is the tradition Elixir inherited.", "Elixir design"),
    _p("Strings are UTF-8 binaries and charlists are lists of code points, "
       "and confusing them is the usual beginner error.", "Elixir gotchas"),
    _p("There are no loops. Recursion, comprehensions and the Enum module "
       "cover everything a loop would do.", "Elixir syntax"),
    _p("Enum is eager and Stream is lazy, and swapping one for the other "
       "is how a pipeline stops building intermediate lists.",
       "Elixir performance"),
    _p("with chains several matches and gives one place for the failure, "
       "which is the answer to nested case statements.", "Elixir syntax"),
    _p("mix is the build tool, the test runner and the task runner, and "
       "ships with the language.", "Elixir conventions"),
)


# ── Lisp ─────────────────────────────────────────────────────

LISP: tuple[Passage, ...] = (
    _p("Lisp was specified by John McCarthy in 1958, making it the second "
       "oldest high level language still in use.", "Lisp design"),
    _p("Code is written as lists, and lists are the data structure, so a "
       "program is a value the program can build.", "Lisp design"),
    _p("The parentheses everyone complains about are what make that true: "
       "there is no syntax to get in the way.", "Lisp design"),
    _p("Macros run at compile time and take code as an argument, so the "
       "language can be extended from inside it.", "Lisp design"),
    _p("Garbage collection was invented for Lisp, because a language that "
       "builds lists constantly needed it first.", "Lisp internals"),
    _p("car and cdr are named after registers on an IBM 704 from the "
       "1950s, and the names never went away.", "Lisp design"),
    _p("The read-eval-print loop came from Lisp, and so did the habit of "
       "developing a program while it is running.", "Lisp design"),
    _p("Common Lisp was standardised in 1994 to unify a scattered family, "
       "and the standard has not changed since.", "Lisp design"),
    _p("Scheme took the other path: a tiny core, tail calls guaranteed, "
       "and one namespace instead of two.", "Lisp design"),
    _p("Common Lisp has separate namespaces for functions and variables, "
       "which is why funcall and sharp-quote exist.", "Lisp gotchas"),
    _p("nil is the empty list and also false, which is elegant until it is "
       "confusing.", "Lisp gotchas"),
    _p("The condition system can resume from an error rather than only "
       "unwinding, which almost no other language offers.", "Lisp design"),
    _p("CLOS dispatches on all the arguments, not just the first, so "
       "methods belong to no single class.", "Lisp design"),
    _p("Clojure put a Lisp on the JVM in 2007 with immutable data and "
       "brackets that mean different things.", "Lisp design"),
    _p("quote stops evaluation, and backquote with commas builds a list "
       "with holes filled in, which is how macros are written.",
       "Lisp syntax"),
    _p("Emacs is configured in a Lisp, which is why it has outlived "
       "almost every editor written since.", "Lisp design"),
    _p("SBCL compiles to native code and is fast enough that the "
       "interpreted reputation is decades out of date.", "Lisp performance"),
    _p("A symbol is a first-class object with a name, a value and a "
       "function slot, rather than only an identifier.", "Lisp internals"),
    _p("loop is a small language of its own inside Common Lisp, and "
       "opinions about it are strongly held.", "Lisp conventions"),
    _p("Paul Graham wrote that Lisp is what you get when you keep taking "
       "things away, which is why it aged so well.", "Lisp design"),
)
