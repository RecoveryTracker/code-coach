"""Per-language material: how each language is put together, and why.

Typing practice is twenty minutes of reading a line and reproducing it, so the
line may as well teach the language you're learning. These are facts about
syntax and design rather than snippets to copy — the code sections already
have the snippets, and knowing *why* a language insists on something is what
stops you fighting it.

The Zen of Python is quoted from PEP 20 by Tim Peters. It ships inside CPython
itself (`import this`) under the Python Software Foundation licence, which
permits redistribution with attribution, and it is attributed here.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _p(text: str, source: str) -> Passage:
    return Passage(text, source)


# ── Python ──────────────────────────────────────────────────

ZEN = (
    "Beautiful is better than ugly.",
    "Explicit is better than implicit.",
    "Simple is better than complex.",
    "Complex is better than complicated.",
    "Flat is better than nested.",
    "Sparse is better than dense.",
    "Readability counts.",
    "Special cases aren't special enough to break the rules.",
    "Although practicality beats purity.",
    "Errors should never pass silently.",
    "Unless explicitly silenced.",
    "In the face of ambiguity, refuse the temptation to guess.",
    "There should be one — and preferably only one — obvious way to do it.",
    "Now is better than never.",
    "Although never is often better than right now.",
    "If the implementation is hard to explain, it's a bad idea.",
    "If the implementation is easy to explain, it may be a good idea.",
    "Namespaces are one honking great idea — let's do more of those!",
)

PYTHON: tuple[Passage, ...] = tuple(
    _p(line, "the Zen of Python, PEP 20") for line in ZEN
) + (
    _p(
        "Python uses indentation for blocks because the indentation was going "
        "to be there anyway. Every other language expects you to indent "
        "correctly and then ignores whether you did.",
        "Python design",
    ),
    _p(
        "There is no ++ in Python, on purpose. It reads as an assignment "
        "pretending to be an expression, and the language would rather you "
        "wrote n += 1 and meant it.",
        "Python syntax",
    ),
    _p(
        "A list comprehension is a loop that produces a value instead of "
        "performing an action. [n * n for n in items] says what you want; the "
        "equivalent loop says how to get it.",
        "Python syntax",
    ),
    _p(
        "Everything in Python is an object, including functions and classes "
        "themselves. That is why you can pass a function as an argument "
        "without wrapping it in anything.",
        "Python design",
    ),
    _p(
        "Default arguments are evaluated once, when the function is defined. A "
        "mutable default like a list is therefore shared by every call, which "
        "is the classic Python surprise.",
        "Python gotchas",
    ),
    _p(
        "The colon at the end of a def or an if is not decoration. It marks "
        "the start of a block, and the indentation that follows says how far "
        "the block reaches.",
        "Python syntax",
    ),
    _p(
        "Tuples are not just immutable lists. The convention is that a list "
        "holds many of the same thing and a tuple holds a few different "
        "things, like a record.",
        "Python design",
    ),
    _p(
        "Slicing never raises for being out of range. items[5:9] on a "
        "three-item list gives you an empty list, where items[5] would raise — "
        "which is convenient and occasionally hides a bug.",
        "Python gotchas",
    ),
    _p(
        "The walrus operator lets you assign inside an expression, which "
        "Python spent decades refusing to allow. It exists for the case where "
        "you want the value and the test in one place.",
        "Python syntax",
    ),
    _p(
        "Dictionaries have kept insertion order since Python 3.7, and it is a "
        "guarantee rather than an accident of the implementation. Before that "
        "it was neither.",
        "Python versions",
    ),
    _p(
        "The underscore is a convention, not a keyword. A leading underscore "
        "means private by agreement, and two leading underscores make the "
        "interpreter rename the attribute to keep subclasses from colliding.",
        "Python conventions",
    ),
    _p(
        "with open(path) as f closes the file even if the block raises. The "
        "context manager exists so that cleanup is attached to the object "
        "rather than remembered by the programmer.",
        "Python syntax",
    ),
    _p(
        "Python has no switch statement, and after twenty years it gained "
        "match instead — which does structural pattern matching rather than "
        "simply comparing a value against a list of constants.",
        "Python versions",
    ),
    _p(
        "The name self is not special to the language. It is the first "
        "parameter of a method and could be called anything; it is a "
        "convention so strong that breaking it looks like a mistake.",
        "Python conventions",
    ),
    _p(
        "is and == ask different questions. == asks whether two things are "
        "equal, is asks whether they are the same object, and small integers "
        "confuse the issue by being cached.",
        "Python gotchas",
    ),
    _p(
        "Generators produce values one at a time and forget them afterwards. "
        "That is what lets you iterate over a file larger than memory without "
        "thinking about it.",
        "Python design",
    ),
    _p(
        "An f-string is formatted at the point it is written, which is why it "
        "reads so much better than the alternatives. The expression inside the "
        "braces is ordinary Python.",
        "Python syntax",
    ),
    _p(
        "PEP 8 asks for four spaces, not tabs, and lines under seventy-nine "
        "characters. The line length is the part everyone argues about and the "
        "indentation is the part that actually matters.",
        "Python conventions",
    ),
    _p(
        "Exceptions in Python are for control flow as well as errors. "
        "StopIteration ends a loop and KeyError is how a dictionary says no, "
        "which is why asking forgiveness is idiomatic here.",
        "Python design",
    ),
    _p(
        "The global interpreter lock means one thread runs Python bytecode at "
        "a time. Threads still help when waiting on files or the network, and "
        "processes are the answer when the work is arithmetic.",
        "Python internals",
    ),
)


# ── JavaScript ──────────────────────────────────────────────

JAVASCRIPT: tuple[Passage, ...] = (
    _p(
        "JavaScript was written in ten days in 1995, and we have been living "
        "with the deadline ever since. Most of its odder corners are decisions "
        "that were never meant to be permanent.",
        "JavaScript history",
    ),
    _p(
        "It has nothing to do with Java. The name was a marketing decision "
        "made while Java was the exciting thing, and it has confused people "
        "for thirty years.",
        "JavaScript history",
    ),
    _p(
        "Use === rather than ==. The double equals converts types before "
        "comparing, which is how you end up with an empty string equal to "
        "zero and an empty array equal to false.",
        "JavaScript gotchas",
    ),
    _p(
        "let and const are scoped to the block; var is scoped to the whole "
        "function and hoisted to the top of it. There is very little reason to "
        "write var in new code.",
        "JavaScript syntax",
    ),
    _p(
        "An arrow function does not have its own this. That is the point of "
        "it: inside a callback, this still means what it meant outside, which "
        "was the single most common source of bugs before arrows existed.",
        "JavaScript syntax",
    ),
    _p(
        "There is one number type, and it is a float. That is why 0.1 + 0.2 "
        "does not equal 0.3, and why BigInt had to be added later for integers "
        "beyond about nine quadrillion.",
        "JavaScript gotchas",
    ),
    _p(
        "null and undefined both mean nothing, differently. undefined is what "
        "you get when nobody set a value; null is what you get when somebody "
        "set it to nothing on purpose.",
        "JavaScript design",
    ),
    _p(
        "Semicolons are optional because the parser inserts them, and the "
        "rules for where it inserts them are not the rules you would guess. A "
        "line starting with a bracket is the usual casualty.",
        "JavaScript gotchas",
    ),
    _p(
        "The event loop is why JavaScript can be single-threaded and still "
        "responsive. Work that waits is handed away and its callback queued, "
        "so nothing blocks the one thread that draws the page.",
        "JavaScript internals",
    ),
    _p(
        "A Promise is a value that has not arrived yet. async and await are "
        "syntax over the same object, letting you write the sequence in the "
        "order it happens rather than as nested callbacks.",
        "JavaScript syntax",
    ),
    _p(
        "Objects are compared by identity, not contents. Two objects with "
        "identical fields are not equal, which catches out everyone who tries "
        "to check them with ===.",
        "JavaScript gotchas",
    ),
    _p(
        "Destructuring works on both sides of a call. const { a, b } = props "
        "pulls fields out, and writing the same shape in the parameter list "
        "does it as the function is entered.",
        "JavaScript syntax",
    ),
    _p(
        "Map is not the same as an object. Its keys can be any type, it keeps "
        "insertion order by specification, and it has a size rather than "
        "making you count.",
        "JavaScript design",
    ),
    _p(
        "The ?? operator is not the same as ||. Nullish coalescing only steps "
        "in for null and undefined, so a legitimate zero or empty string "
        "survives it.",
        "JavaScript syntax",
    ),
    _p(
        "Arrays are objects with numeric keys, which is why an array can have "
        "holes in it and why the length property can be assigned to in order "
        "to truncate one.",
        "JavaScript internals",
    ),
    _p(
        "Hoisting means a declaration is known before its line runs. A "
        "function declaration is fully hoisted and callable early; a const is "
        "hoisted but unusable until its line, which is the temporal dead "
        "zone.",
        "JavaScript internals",
    ),
    _p(
        "Closures are why a callback still knows about a variable from the "
        "function that created it. The function keeps the scope alive, which "
        "is a feature and occasionally a memory leak.",
        "JavaScript design",
    ),
    _p(
        "typeof null returns object. It is a bug from the first version that "
        "can never be fixed, because too much code now depends on the wrong "
        "answer.",
        "JavaScript gotchas",
    ),
    _p(
        "The spread operator copies one level deep. [...items] is a new array "
        "of the same objects, so changing an object inside it changes it in "
        "both.",
        "JavaScript gotchas",
    ),
    _p(
        "ECMAScript is the standard and JavaScript is the implementation. The "
        "yearly editions are why features are described as ES2015 or later "
        "rather than by a version of the language.",
        "JavaScript history",
    ),
    _p(
        "this depends on how a function is called, not where it is written. "
        "The same method pulled off its object and passed as a callback loses "
        "the object it came from.",
        "JavaScript gotchas",
    ),
    _p(
        "sort compares as strings by default. [10, 9, 1].sort() gives "
        "[1, 10, 9], and the fix is to pass (a, b) => a - b every time you "
        "sort numbers.",
        "JavaScript gotchas",
    ),
    _p(
        "Array methods split into two families: the ones that return "
        "something new, like map and filter, and the ones that change the "
        "array in place, like sort, reverse and splice.",
        "JavaScript conventions",
    ),
    _p(
        "slice copies and splice cuts. One letter apart, and one of them "
        "leaves the original alone while the other does not.",
        "JavaScript gotchas",
    ),
    _p(
        "reduce is the general case that map and filter are special cases of. "
        "Anything you can build by walking a list once, reduce can build.",
        "JavaScript design",
    ),
    _p(
        "forEach cannot be stopped early and ignores what you return. If you "
        "want to break out, or want a value back, it is the wrong loop.",
        "JavaScript conventions",
    ),
    _p(
        "for...in walks keys and for...of walks values. Using for...in on an "
        "array gives you index strings, and inherited properties along with "
        "them.",
        "JavaScript gotchas",
    ),
    _p(
        "Every object key is a string or a symbol. obj[1] and obj['1'] are "
        "the same slot, which is one of several reasons Map exists.",
        "JavaScript internals",
    ),
    _p(
        "Falsy is a short list: false, 0, -0, 0n, empty string, null, "
        "undefined and NaN. Everything else is truthy, including empty arrays "
        "and empty objects.",
        "JavaScript gotchas",
    ),
    _p(
        "NaN is the only value not equal to itself. That is why Number.isNaN "
        "exists, and why x !== x is a real test rather than a typo.",
        "JavaScript gotchas",
    ),
    _p(
        "typeof is unreliable for anything but primitives. Array.isArray "
        "exists because typeof [] is object, and so is typeof null.",
        "JavaScript gotchas",
    ),
    _p(
        "Default parameters are evaluated at call time, not once. A default "
        "of [] gives every call its own array, unlike the equivalent trap in "
        "some other languages.",
        "JavaScript design",
    ),
    _p(
        "Rest gathers and spread scatters, and both are three dots. In a "
        "parameter list it collects the remaining arguments; in a call it "
        "spreads a list into them.",
        "JavaScript syntax",
    ),
    _p(
        "Optional chaining short-circuits the whole chain. a?.b.c does not "
        "throw when a is null, because the rest of the chain is skipped "
        "rather than evaluated.",
        "JavaScript syntax",
    ),
    _p(
        "Labels on object literals and blocks look identical to the parser. "
        "That is why an arrow function returning an object needs the "
        "parentheses in () => ({ a: 1 }).",
        "JavaScript gotchas",
    ),
    _p(
        "Template literals can span lines and embed expressions. They also "
        "keep the indentation you typed, which is usually the reason a "
        "multi-line string looks wrong.",
        "JavaScript syntax",
    ),
    _p(
        "JSON.stringify drops undefined, functions and symbols. Round-tripping "
        "an object through JSON is a deep copy that quietly loses anything "
        "JSON has no word for.",
        "JavaScript gotchas",
    ),
    _p(
        "await inside a loop runs the requests one after another. "
        "Promise.all is how you start them together and wait once.",
        "JavaScript performance",
    ),
    _p(
        "Promise.all rejects as soon as any one does. Promise.allSettled "
        "waits for all of them and tells you how each went, which is usually "
        "what a batch of independent jobs wants.",
        "JavaScript syntax",
    ),
    _p(
        "An async function never throws to its caller directly. It returns a "
        "rejected Promise, which is why a try around a call without await "
        "catches nothing.",
        "JavaScript gotchas",
    ),
    _p(
        "Microtasks run before the next timer. A resolved Promise's callback "
        "is queued ahead of a setTimeout of zero, every time.",
        "JavaScript internals",
    ),
    _p(
        "Prototypes are the inheritance. class is syntax over the same "
        "mechanism, and a method lives on the prototype rather than on each "
        "instance.",
        "JavaScript internals",
    ),
    _p(
        "Modules are strict mode by default and have their own scope. A "
        "top-level const in a module is not global, which is the main "
        "difference from a plain script tag.",
        "JavaScript design",
    ),
    _p(
        "const does not make a value immutable, only the binding. You cannot "
        "reassign a const array, and you can push to it all day.",
        "JavaScript gotchas",
    ),
    _p(
        "Object.freeze is one level deep as well. Anything nested inside a "
        "frozen object is still perfectly writable.",
        "JavaScript gotchas",
    ),
    _p(
        "Getters look like properties and run like functions. Reading one can "
        "do arbitrary work, which is worth remembering when a simple-looking "
        "line is unexpectedly slow.",
        "JavaScript design",
    ),
    _p(
        "Generators pause. function* and yield hand a value back and resume "
        "where they left off, which is what makes lazy sequences possible "
        "without a callback.",
        "JavaScript syntax",
    ),
    _p(
        "Symbols are unique keys that cannot collide. That is how the "
        "language adds behaviour to objects, like Symbol.iterator, without "
        "risking a name you already used.",
        "JavaScript internals",
    ),
)


# ── Dart ────────────────────────────────────────────────────

DART: tuple[Passage, ...] = (
    _p(
        "Dart compiles two ways. It runs on a virtual machine while you "
        "develop, which is what makes hot reload possible, and compiles to "
        "native code or JavaScript when you ship.",
        "Dart design",
    ),
    _p(
        "Sound null safety means the compiler knows which values can be null. "
        "A String cannot hold null and a String? can, and the difference is "
        "checked before the program ever runs.",
        "Dart syntax",
    ),
    _p(
        "The ! operator tells the compiler you are certain a value is not "
        "null. It is a promise, not a check, and it throws if you were wrong.",
        "Dart syntax",
    ),
    _p(
        "final and const are not the same. final means set once at runtime; "
        "const means known at compile time, and a const value is shared rather "
        "than rebuilt.",
        "Dart syntax",
    ),
    _p(
        "Everything in Dart is an object, including numbers and null itself. "
        "There are no primitive types hiding underneath the way there are in "
        "Java.",
        "Dart design",
    ),
    _p(
        "Constructors can assign fields directly in their parameter list. "
        "ListNode(this.val, [this.next]) does the assignment for you, and the "
        "square brackets make the second one optional.",
        "Dart syntax",
    ),
    _p(
        "Dart was built for user interfaces, which shows in the details. Fast "
        "startup, predictable pauses and a garbage collector tuned for the "
        "many short-lived objects a widget tree produces.",
        "Dart design",
    ),
    _p(
        "A cascade lets you call several methods on one object without "
        "repeating its name. Two dots instead of one returns the object rather "
        "than the method's result.",
        "Dart syntax",
    ),
    _p(
        "Named parameters are ordinary in Dart and rare elsewhere. In a widget "
        "tree with a dozen arguments it is the difference between readable "
        "code and counting commas.",
        "Dart conventions",
    ),
    _p(
        "Futures and Streams are the two shapes of asynchrony. A Future is one "
        "value later; a Stream is many values over time, and async* is how you "
        "write one.",
        "Dart syntax",
    ),
    _p(
        "Dart has no public or private keyword. A leading underscore makes a "
        "name private to its library, which is the file it lives in.",
        "Dart conventions",
    ),
    _p(
        "Isolates do not share memory. Dart's answer to threads is separate "
        "workers passing messages, which removes an entire category of bug at "
        "the cost of copying data.",
        "Dart internals",
    ),
    _p(
        "Hot reload works by sending new code into the running virtual machine "
        "and rebuilding the widget tree. State survives, which is why you can "
        "adjust a screen without navigating back to it.",
        "Dart internals",
    ),
    _p(
        "The late keyword means a value will be set before it is read. It "
        "moves a null check from compile time to run time on purpose, for the "
        "cases where you know better than the analyser.",
        "Dart syntax",
    ),
    _p(
        "Collection if and for live inside the literal. You can write a "
        "conditional element directly in a list, which reads far better than "
        "building the list in pieces.",
        "Dart syntax",
    ),
    _p(
        "The ? in a type is part of the type. String and String? are two "
        "different things, and the compiler tracks which one you have at "
        "every line.",
        "Dart syntax",
    ),
    _p(
        "The ?? operator supplies a fallback and ??= assigns one only if the "
        "target is null. Both exist so a default does not need three lines of "
        "if.",
        "Dart syntax",
    ),
    _p(
        "?. stops the chain rather than throwing. user?.address?.city is null "
        "if anything along the way was, and nothing in between has to be "
        "checked by hand.",
        "Dart syntax",
    ),
    _p(
        "int and double are both num, and neither converts silently. Dividing "
        "two ints with / gives a double; ~/ is the one that gives you an int "
        "back.",
        "Dart gotchas",
    ),
    _p(
        "Dart compiles to JavaScript for the web, where there is only one "
        "number type. That is why integers behave slightly differently in a "
        "browser than on a phone.",
        "Dart internals",
    ),
    _p(
        "A List literal is growable and List.filled is not, unless you ask. "
        "Calling add on a fixed-length list is a runtime error rather than a "
        "compile one.",
        "Dart gotchas",
    ),
    _p(
        "const in Dart means built at compile time, so two identical const "
        "values are the same object. That is why const widgets are worth "
        "reaching for in a rebuild.",
        "Dart performance",
    ),
    _p(
        "A factory constructor does not have to return a new instance. It can "
        "hand back a cached one, which is how a class implements its own "
        "singleton without a separate function.",
        "Dart syntax",
    ),
    _p(
        "Named constructors give a class more than one way to be built. "
        "DateTime.now and DateTime.utc are the same class, entered by "
        "different doors.",
        "Dart conventions",
    ),
    _p(
        "required is a keyword, not a convention. A named parameter without a "
        "default and without required will not compile under null safety.",
        "Dart syntax",
    ),
    _p(
        "Positional optional parameters use square brackets and named ones "
        "use braces. A function cannot have both kinds of optional parameter "
        "at once.",
        "Dart syntax",
    ),
    _p(
        "Every class implicitly defines an interface. implements takes the "
        "shape without the code; extends takes both, and you can only extend "
        "one thing.",
        "Dart design",
    ),
    _p(
        "A mixin is code without a place in the hierarchy. with is how a "
        "class picks up behaviour from several places while still extending "
        "only one.",
        "Dart design",
    ),
    _p(
        "async does not mean parallel. An async function runs on the same "
        "isolate and simply gives up the turn at each await.",
        "Dart internals",
    ),
    _p(
        "await only works inside async, and an async function always returns "
        "a Future. Marking a function async changes its signature whether you "
        "meant it to or not.",
        "Dart syntax",
    ),
    _p(
        "An unawaited Future still runs. Forgetting the await does not cancel "
        "the work, it just means nothing is waiting to hear how it went, "
        "including the errors.",
        "Dart gotchas",
    ),
    _p(
        "Streams come in single-subscription and broadcast. Listening twice "
        "to the first kind throws, which is the usual cause of a stream that "
        "worked until it was reused.",
        "Dart internals",
    ),
    _p(
        "async* and yield build a Stream the way a generator builds a list. "
        "sync* and yield do the same for an Iterable, one value at a time and "
        "only when asked.",
        "Dart syntax",
    ),
    _p(
        "The spread operator works inside collection literals, and ...? skips "
        "a null instead of throwing. Both exist so building a list "
        "conditionally stays a single expression.",
        "Dart syntax",
    ),
    _p(
        "Records and patterns arrived in Dart 3. A function can return "
        "(int, String) without inventing a class, and destructuring pulls it "
        "apart at the call site.",
        "Dart syntax",
    ),
    _p(
        "switch is an expression as well as a statement now. Assigning the "
        "result of a switch is often clearer than four assignments to the "
        "same variable.",
        "Dart syntax",
    ),
    _p(
        "sealed classes make a switch exhaustive. Adding a subtype turns "
        "every switch over the family into a compile error, which is the "
        "point rather than the inconvenience.",
        "Dart design",
    ),
    _p(
        "Operator == and hashCode travel together. Overriding one without the "
        "other gives you objects that are equal but land in different buckets "
        "of a Set.",
        "Dart gotchas",
    ),
)


# ── SQL, C and Rust ─────────────────────────────────────────

SQL: tuple[Passage, ...] = (
    _p(
        "SQL describes what you want, not how to get it. The database plans "
        "the how, which is why the same query can be fast or slow depending on "
        "indexes you never mentioned.",
        "SQL design",
    ),
    _p(
        "WHERE filters rows before grouping and HAVING filters after. Using "
        "the wrong one is the most common mistake in any query with a GROUP BY "
        "in it.",
        "SQL syntax",
    ),
    _p(
        "NULL is not a value, it is the absence of one. That is why NULL = "
        "NULL is not true, and why you have to write IS NULL instead.",
        "SQL gotchas",
    ),
    _p(
        "A JOIN without a condition gives you every combination of both "
        "tables. On two tables of a thousand rows that is a million, which is "
        "how a missing ON clause takes down a server.",
        "SQL gotchas",
    ),
    _p(
        "An index is a sorted copy of one column, kept up to date for you. It "
        "makes reads faster and writes slower, which is the whole trade you "
        "are making.",
        "SQL performance",
    ),
    _p(
        "SELECT * is convenient and rarely right. It fetches columns you do "
        "not need, and it breaks quietly the moment somebody adds one.",
        "SQL conventions",
    ),
    _p(
        "The clauses run in a different order than they are written. FROM "
        "first, then WHERE, then GROUP BY, then HAVING, and SELECT nearly "
        "last — which is why you cannot use an alias in a WHERE.",
        "SQL internals",
    ),
    _p(
        "A transaction is all or nothing. If anything inside it fails, the "
        "database puts everything back, and that guarantee is most of what a "
        "database is for.",
        "SQL design",
    ),
    _p(
        "GROUP BY collapses rows into groups, so every column you select has "
        "to be either grouped by or aggregated. There is no sensible single "
        "answer for a column that varies within a group.",
        "SQL syntax",
    ),
    _p(
        "COUNT(*) counts rows and COUNT(column) counts non-NULL values in it. "
        "The difference is invisible until a column has gaps, and then it is "
        "the whole answer.",
        "SQL gotchas",
    ),
    _p(
        "A LEFT JOIN keeps every row on the left whether or not the right "
        "side matched, filling the gaps with NULL. That NULL is how you find "
        "the rows that had no match.",
        "SQL syntax",
    ),
    _p(
        "Putting a condition on the right table in the WHERE clause turns a "
        "LEFT JOIN back into an inner one, because NULL fails the test. Move "
        "it into the ON clause instead.",
        "SQL gotchas",
    ),
    _p(
        "DISTINCT is often a sign that a join is duplicating rows. It is "
        "worth finding out why before reaching for it, because the duplicates "
        "usually mean the join is wrong.",
        "SQL conventions",
    ),
    _p(
        "A primary key identifies a row and a foreign key points at one. "
        "Together they are what stops the database from holding a reference "
        "to something that was deleted.",
        "SQL design",
    ),
    _p(
        "An index makes reads faster and writes slower, because every write "
        "has to keep it up to date. Indexing every column is not free "
        "insurance, it is a tax on every insert.",
        "SQL performance",
    ),
    _p(
        "Wrapping a column in a function usually stops an index being used. "
        "WHERE created_at >= '2024-01-01' can use one, WHERE YEAR(created_at) "
        "= 2024 generally cannot.",
        "SQL performance",
    ),
    _p(
        "EXPLAIN shows the plan the database intends to use. It is the "
        "difference between guessing why a query is slow and reading the "
        "reason.",
        "SQL performance",
    ),
    _p(
        "A subquery in the SELECT list runs once per row returned. Rewriting "
        "it as a join often turns a query that scales badly into one that "
        "does not.",
        "SQL performance",
    ),
    _p(
        "IN with a list is fine, and IN with a subquery that returns a NULL "
        "is a trap. NOT IN against a set containing NULL returns nothing at "
        "all, because the comparison is unknown rather than false.",
        "SQL gotchas",
    ),
    _p(
        "COALESCE returns the first argument that is not NULL. It is how you "
        "give a missing value a default without an outer layer of CASE.",
        "SQL syntax",
    ),
    _p(
        "CASE WHEN is SQL's if. Inside an aggregate it becomes conditional "
        "counting: SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) counts "
        "only the paid ones.",
        "SQL syntax",
    ),
    _p(
        "A window function computes across rows without collapsing them. "
        "ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) numbers "
        "each user's rows separately and keeps every row.",
        "SQL syntax",
    ),
    _p(
        "The difference between GROUP BY and OVER is what you get back. GROUP "
        "BY gives one row per group; OVER gives every row, with the group's "
        "answer attached to each.",
        "SQL design",
    ),
    _p(
        "A common table expression names a subquery so the rest of the query "
        "can read like prose. WITH recent AS (...) SELECT * FROM recent is "
        "the same work, spelled so a person can follow it.",
        "SQL conventions",
    ),
    _p(
        "ORDER BY without LIMIT sorts the whole result. If you only want the "
        "top few, say so, or the database sorts a million rows to hand you "
        "ten.",
        "SQL performance",
    ),
    _p(
        "LIMIT without ORDER BY returns an arbitrary set of rows. There is no "
        "natural order in a table, so any order you saw last time was luck.",
        "SQL gotchas",
    ),
    _p(
        "OFFSET gets slower the deeper it goes, because the database still "
        "produces and discards every skipped row. Paging by a key you sorted "
        "on stays fast.",
        "SQL performance",
    ),
    _p(
        "UNION removes duplicates and UNION ALL does not. UNION ALL is the "
        "cheaper of the two, and is what you want unless you specifically "
        "need the deduplication.",
        "SQL syntax",
    ),
    _p(
        "Never build a query by pasting user input into a string. Parameters "
        "are not a style preference, they are the reason the input cannot "
        "become part of the statement.",
        "SQL conventions",
    ),
    _p(
        "An UPDATE without a WHERE updates every row. Writing the SELECT "
        "first and only then swapping the verb is a habit worth having.",
        "SQL conventions",
    ),
    _p(
        "ACID is four promises: a transaction is all or nothing, leaves the "
        "data valid, does not see other transactions half-finished, and "
        "survives a power cut once committed.",
        "SQL design",
    ),
    _p(
        "Isolation levels are a dial between correctness and concurrency. "
        "Read committed is the common default, and it still allows the same "
        "query in one transaction to return different answers.",
        "SQL internals",
    ),
    _p(
        "A deadlock is two transactions each holding what the other wants. "
        "The database picks one and kills it, which is why write code that "
        "can be retried.",
        "SQL internals",
    ),
    _p(
        "Normalisation is storing each fact once. Denormalisation is "
        "deliberately storing it twice for speed, and accepting that you now "
        "have two places to keep in step.",
        "SQL design",
    ),
    _p(
        "A view is a saved query, not saved data. It costs nothing to store "
        "and everything it selects is computed again each time you read it.",
        "SQL design",
    ),
    _p(
        "Storing money as a floating point number will eventually be wrong by "
        "a penny. DECIMAL exists because base ten fractions cannot be "
        "represented exactly in base two.",
        "SQL gotchas",
    ),
    _p(
        "Store timestamps in UTC and convert when you display them. Every "
        "other arrangement eventually meets a daylight saving change and "
        "loses an hour of data.",
        "SQL conventions",
    ),
    _p(
        "SQL is a standard that every database implements slightly "
        "differently. The core is portable, and the moment you use a "
        "function for dates or strings you are usually writing for one "
        "engine.",
        "SQL design",
    ),
)

C_LORE: tuple[Passage, ...] = (
    _p(
        "C is a portable assembler with types. Almost everything in it maps "
        "onto machine instructions in a way you can predict, which is why it "
        "is still used where predictability matters.",
        "C design",
    ),
    _p(
        "An array in C is a pointer wearing a hat. Passing one to a function "
        "passes the address, which is why the function has no way of knowing "
        "how long it is unless you tell it.",
        "C gotchas",
    ),
    _p(
        "Strings are arrays of characters ending in a zero byte. Every bug "
        "about buffer sizes in the history of the language comes back to that "
        "one decision.",
        "C design",
    ),
    _p(
        "malloc gives you memory and free gives it back, and nothing checks "
        "that you did. Modern C is largely a set of habits for keeping track "
        "of that by hand.",
        "C conventions",
    ),
    _p(
        "Undefined behaviour does not mean it will crash. It means the "
        "compiler is allowed to assume it cannot happen, and optimise on that "
        "assumption, which is far stranger than crashing.",
        "C internals",
    ),
    _p(
        "The header file is a promise and the source file is the delivery. "
        "Compilation is per-file, so each one has to be told separately what "
        "exists elsewhere.",
        "C design",
    ),
    _p(
        "sizeof is measured in chars, and a char is one byte by definition. "
        "That makes sizeof(char) always 1, whatever the machine thinks a byte "
        "is worth.",
        "C internals",
    ),
    _p(
        "sizeof on an array gives the whole array, and sizeof on a pointer "
        "gives the pointer. The same expression means different things either "
        "side of a function call, because the array decayed on the way in.",
        "C gotchas",
    ),
    _p(
        "Pointer arithmetic counts elements, not bytes. Adding one to an int "
        "pointer moves four bytes on most machines, and the compiler does "
        "that multiplication for you.",
        "C internals",
    ),
    _p(
        "Declaring a variable does not clear it. A local you never assigned "
        "holds whatever was on the stack a moment ago, which is why it often "
        "works in a debug build and not in a release one.",
        "C gotchas",
    ),
    _p(
        "The stack is automatic and the heap is yours to manage. Returning a "
        "pointer to a local is returning the address of something that has "
        "already gone.",
        "C gotchas",
    ),
    _p(
        "free does not clear the pointer, it only releases the memory. "
        "Setting it to NULL afterwards is what stops the second free from "
        "being a bug you cannot see.",
        "C conventions",
    ),
    _p(
        "malloc can return NULL. Checking it is not paranoia; it is the "
        "difference between a clean failure and a crash somewhere else "
        "entirely.",
        "C conventions",
    ),
    _p(
        "strlen walks the string counting until it finds the zero byte. "
        "Calling it inside a loop condition turns a linear loop into a "
        "quadratic one.",
        "C performance",
    ),
    _p(
        "strcpy will happily write past the end of the destination. The "
        "length it stops at belongs to the source, and the destination has no "
        "say in the matter.",
        "C gotchas",
    ),
    _p(
        "A string literal lives in read-only memory. Taking a char pointer to "
        "one and then writing through it compiles, and then crashes at "
        "runtime.",
        "C gotchas",
    ),
    _p(
        "The preprocessor runs before the compiler and only knows about text. "
        "A macro is a find and replace, which is why arguments get wrapped in "
        "parentheses so carefully.",
        "C internals",
    ),
    _p(
        "A macro that uses its argument twice evaluates it twice. MAX(i++, "
        "j) increments i more than once, and nothing in the call site hints "
        "at that.",
        "C gotchas",
    ),
    _p(
        "Header guards stop a file being included twice in one translation "
        "unit. Without them the second copy of every declaration is an error, "
        "not a no-op.",
        "C conventions",
    ),
    _p(
        "static at file scope means private to this file. static inside a "
        "function means the variable survives between calls. One keyword, two "
        "unrelated jobs.",
        "C syntax",
    ),
    _p(
        "extern says the thing exists somewhere else and the linker will find "
        "it. The compiler needs the declaration; the linker needs the "
        "definition.",
        "C internals",
    ),
    _p(
        "const on a pointer can mean two different things. const char *p is a "
        "pointer to constant characters, char *const p is a constant pointer. "
        "Read the declaration right to left.",
        "C syntax",
    ),
    _p(
        "Signed overflow is undefined behaviour and unsigned overflow wraps. "
        "The compiler is entitled to assume the signed one never happens, and "
        "optimises accordingly.",
        "C internals",
    ),
    _p(
        "Comparing a signed and an unsigned value promotes the signed one. "
        "That is how -1 > 1u ends up being true, which is correct by the "
        "rules and surprising every time.",
        "C gotchas",
    ),
    _p(
        "Integer division truncates towards zero. 7 / 2 is 3, and getting 3.5 "
        "means at least one side has to be a floating point number before the "
        "division, not after.",
        "C syntax",
    ),
    _p(
        "Everything in C is passed by value, pointers included. Passing a "
        "pointer copies the address, which is why changing the pointer inside "
        "a function does not change it outside.",
        "C design",
    ),
    _p(
        "To change a caller's pointer, pass its address. That is what the "
        "second star in char **argv is doing, and why so many C functions "
        "take one.",
        "C design",
    ),
    _p(
        "The order arguments are evaluated in is unspecified. f(i++, i++) has "
        "no defined meaning, and different compilers will disagree about it "
        "quite reasonably.",
        "C gotchas",
    ),
    _p(
        "A struct is a layout, not an object. The compiler may insert padding "
        "between members to keep them aligned, which is why sizeof is often "
        "more than the sum of the parts.",
        "C internals",
    ),
    _p(
        "A union stores one of its members at a time, all at the same "
        "address. It is the language's way of saying this memory means "
        "different things depending on context.",
        "C syntax",
    ),
    _p(
        "An enum is a set of named integers, and nothing stops you assigning "
        "a value outside the set. The names are for the reader; the type "
        "checking is thinner than it looks.",
        "C syntax",
    ),
    _p(
        "typedef names a type rather than creating one. Hiding a pointer "
        "inside a typedef is common and controversial, because the star "
        "disappears from every use.",
        "C conventions",
    ),
    _p(
        "Functions return one value, so C returns errors in it and results "
        "through pointers. That convention is why so many signatures end in "
        "an out parameter.",
        "C design",
    ),
    _p(
        "errno is set on failure and not cleared on success. Checking it "
        "without first knowing that the call failed reads whatever the last "
        "failure left behind.",
        "C conventions",
    ),
    _p(
        "The compiler turns source into object files and the linker joins "
        "them. Most confusing C errors are one or the other complaining, and "
        "telling them apart halves the search.",
        "C internals",
    ),
    _p(
        "C has no namespaces, so every non-static name is global to the whole "
        "program. That is why library functions carry a prefix in their name "
        "rather than around it.",
        "C design",
    ),
    _p(
        "The standard library is deliberately small. C gives you the "
        "machine and expects the rest to come from somewhere else, which is "
        "both the complaint and the reason it runs everywhere.",
        "C design",
    ),
    _p(
        "main returns an int and zero means success. It is backwards from "
        "every boolean you will write, and it is because there is one way to "
        "succeed and many ways to fail.",
        "C conventions",
    ),
)

RUST: tuple[Passage, ...] = (
    _p(
        "Rust's borrow checker enforces one rule with large consequences: many "
        "readers or one writer, never both. Most of the bugs it prevents are "
        "ones that only appear under load.",
        "Rust design",
    ),
    _p(
        "Ownership means every value has exactly one owner, and it is dropped "
        "when the owner goes out of scope. There is no garbage collector "
        "because there is nothing left to collect.",
        "Rust design",
    ),
    _p(
        "Rust has no null. Option<T> makes the absence of a value a thing you "
        "must handle, and match makes forgetting to handle it a compile "
        "error.",
        "Rust syntax",
    ),
    _p(
        "The question mark operator returns early on an error. It turns "
        "explicit error propagation into one character, without hiding that "
        "propagation is happening.",
        "Rust syntax",
    ),
    _p(
        "Lifetimes are not a runtime cost. They are notes to the compiler "
        "about how long a reference is valid, and they vanish entirely once "
        "the program is built.",
        "Rust internals",
    ),
    _p(
        "Fighting the borrow checker usually means the design has shared "
        "mutable state in it. The error is often pointing at a real problem "
        "rather than an inconvenience.",
        "Rust conventions",
    ),
    _p(
        "Assigning a value moves it unless the type is Copy. The original "
        "variable is not just unused afterwards, it is unusable, and the "
        "compiler will say so by name.",
        "Rust design",
    ),
    _p(
        "Integers and other small fixed-size types are Copy, so assigning "
        "them duplicates rather than moves. That is why the borrow checker "
        "seems to leave numbers alone.",
        "Rust internals",
    ),
    _p(
        "clone is explicit because copying can be expensive. Rust would "
        "rather make you type the cost than hide it inside an assignment.",
        "Rust design",
    ),
    _p(
        "A reference borrows without taking ownership. &T is a shared borrow "
        "and &mut T is an exclusive one, and the whole rule is that you never "
        "have both at once.",
        "Rust syntax",
    ),
    _p(
        "String is owned and growable, &str is a borrowed view of some text. "
        "Almost every function should take &str and let the caller decide who "
        "owns the data.",
        "Rust conventions",
    ),
    _p(
        "Indexing a String by number is not allowed, because Rust strings are "
        "UTF-8 and byte four may be the middle of a character. chars() is how "
        "you ask for characters.",
        "Rust gotchas",
    ),
    _p(
        "Vec<T> owns its contents and &[T] borrows them. A slice is a pointer "
        "and a length, which is why passing one costs nothing and cannot "
        "outlive what it points at.",
        "Rust design",
    ),
    _p(
        "Result<T, E> is a value, not an exception. Nothing unwinds past you "
        "silently, and the only way to ignore an error is to say so in the "
        "code.",
        "Rust design",
    ),
    _p(
        "unwrap says you are certain and will accept a panic if you are "
        "wrong. It is fine in a test and a decision worth justifying anywhere "
        "else.",
        "Rust conventions",
    ),
    _p(
        "expect is unwrap with a message. When it does fire, the difference "
        "between the two is the difference between a mystery and a "
        "sentence.",
        "Rust conventions",
    ),
    _p(
        "match must cover every case, and the compiler checks. Adding a "
        "variant to an enum turns every match on it into a compile error, "
        "which is the point rather than the cost.",
        "Rust design",
    ),
    _p(
        "if let is match for when you only care about one arm. It trades "
        "exhaustiveness for brevity, so reach for it when the other cases "
        "genuinely do not matter.",
        "Rust syntax",
    ),
    _p(
        "Almost everything is an expression, including if and match. That is "
        "why a function body can end in a match with no return and no "
        "semicolon.",
        "Rust syntax",
    ),
    _p(
        "A semicolon discards the value of an expression. Leaving it off the "
        "last line of a block is how the block evaluates to something, and "
        "adding one by habit is a common early error.",
        "Rust syntax",
    ),
    _p(
        "let bindings are immutable by default. mut is not an optimisation "
        "hint, it is a note to every later reader that this value changes.",
        "Rust design",
    ),
    _p(
        "Shadowing lets you reuse a name with a new type. let input = "
        "input.trim() is idiomatic rather than sloppy, because the old "
        "binding is genuinely finished with.",
        "Rust conventions",
    ),
    _p(
        "A trait is a set of behaviours a type can implement. It is closer to "
        "an interface than to inheritance, and Rust has no inheritance to "
        "confuse it with.",
        "Rust design",
    ),
    _p(
        "Generics are resolved at compile time, so a generic function costs "
        "nothing extra at runtime. The compiler writes one copy per concrete "
        "type it is used with.",
        "Rust internals",
    ),
    _p(
        "dyn Trait is the runtime version, dispatched through a pointer. You "
        "reach for it when the set of types is not known until the program "
        "runs.",
        "Rust internals",
    ),
    _p(
        "derive writes an implementation for you. #[derive(Debug, Clone, "
        "PartialEq)] is the line that turns a struct into something you can "
        "print, copy and compare.",
        "Rust conventions",
    ),
    _p(
        "Iterators are lazy. A chain of map and filter does nothing until "
        "something consumes it, which is why forgetting collect leaves you "
        "holding a description of work rather than a result.",
        "Rust design",
    ),
    _p(
        "Iterator chains compile down to roughly the loop you would have "
        "written. The abstraction is free, which is the claim zero-cost is "
        "making.",
        "Rust performance",
    ),
    _p(
        "A closure captures by reference until it needs not to. move forces "
        "it to take ownership, which is what threads and anything outliving "
        "the current scope require.",
        "Rust syntax",
    ),
    _p(
        "Send and Sync are what make data races a compile error. A type that "
        "cannot safely cross threads simply will not be allowed to, and you "
        "learn this before the program runs.",
        "Rust design",
    ),
    _p(
        "Rc is shared ownership for a single thread and Arc is the atomic "
        "version for many. Arc costs a little more, and using Rc across "
        "threads will not compile.",
        "Rust internals",
    ),
    _p(
        "RefCell moves the borrow check from compile time to runtime. The "
        "rule is the same; breaking it panics instead of failing to build.",
        "Rust internals",
    ),
    _p(
        "Box<T> puts a value on the heap. Recursive types need it, because a "
        "struct that directly contains itself has no finite size.",
        "Rust syntax",
    ),
    _p(
        "Lifetime annotations do not change how long anything lives. They "
        "describe a relationship that already exists so the compiler can "
        "check it.",
        "Rust syntax",
    ),
    _p(
        "The compiler elides most lifetimes for you. The ones you have to "
        "write are usually where a return value borrows from more than one "
        "argument and the compiler cannot guess which.",
        "Rust internals",
    ),
    _p(
        "Drop runs when a value goes out of scope, in reverse order of "
        "declaration. Files close and locks release without a finally block, "
        "because scope is the mechanism.",
        "Rust design",
    ),
    _p(
        "unsafe does not turn the checks off. It unlocks five specific "
        "abilities and moves the responsibility for proving them sound from "
        "the compiler to you.",
        "Rust design",
    ),
    _p(
        "Cargo is the build tool, package manager and test runner in one. "
        "cargo test finds and runs the tests, including the examples in your "
        "documentation comments.",
        "Rust conventions",
    ),
)


# ── Words about words ───────────────────────────────────────
# The dictionary-and-thesaurus rabbit hole. Where a word came from is usually
# a small story about what people needed to say at the time.

WORDS: tuple[Passage, ...] = (
    _p(
        "A thesaurus is not a list of synonyms. Almost no two words mean "
        "exactly the same thing, and choosing between them is choosing which "
        "shade of the meaning you wanted.",
        "on words",
    ),
    _p(
        "Sandwich is named after a man, who was named after a place. The Earl "
        "of Sandwich wanted to eat without leaving the table, and the town got "
        "its name from a harbour on sand.",
        "etymology",
    ),
    _p(
        "Clue used to be spelled clew and meant a ball of thread. It comes "
        "from the thread Theseus unwound in the labyrinth, which is why "
        "following one still means finding your way out.",
        "etymology",
    ),
    _p(
        "Deadline was a line around a prison camp. Crossing it got you shot, "
        "and the word softened into a date by which something must be "
        "finished.",
        "etymology",
    ),
    _p(
        "Nice meant foolish, then precise, then agreeable. Words drift, and "
        "the complaint that one is being used wrongly is usually a complaint "
        "about which decade you learned it in.",
        "on words",
    ),
    _p(
        "Muscle, mussel and mouse are all the same root. Somebody thought a "
        "flexing arm, a shellfish and a small grey animal all looked alike, "
        "and the language agreed.",
        "etymology",
    ),
    _p(
        "The word set has more distinct meanings in English than any other. "
        "The Oxford entry runs to tens of thousands of words, and almost none "
        "of them are hard to understand in context.",
        "on words",
    ),
    _p(
        "Bankrupt comes from banca rotta, a broken bench. Moneylenders worked "
        "at benches in the market, and one who could not pay had his bench "
        "broken in public.",
        "etymology",
    ),
    _p(
        "Salary, salad and sausage all come from salt. It was how food was "
        "kept, what soldiers were paid in, and important enough to leave its "
        "name on a dozen ordinary things.",
        "etymology",
    ),
    _p(
        "A dictionary describes rather than commands. Editors track how words "
        "are actually used and record it, which is why the entries change "
        "without anybody granting permission.",
        "on words",
    ),
    _p(
        "Quarantine means forty days. Ships arriving at Venice during the "
        "plague waited forty of them before anyone could land, and the number "
        "stayed in the word.",
        "etymology",
    ),
    _p(
        "Robot, quiz and gas were all invented rather than inherited. Most "
        "words drift in from somewhere; occasionally somebody simply makes one "
        "up and it sticks.",
        "on words",
    ),
    _p(
        "Avocado, chocolate and tomato all come from Nahuatl. Foods travel "
        "with their names attached, which is why a menu is often a map of who "
        "traded with whom.",
        "etymology",
    ),
    _p(
        "Curfew is couvre-feu, cover the fire. A bell rang and everyone damped "
        "their hearth, because a town of wooden houses could not survive one "
        "careless night.",
        "etymology",
    ),
    _p(
        "The longest word most people can name is a lung disease invented to "
        "be long. The longest ones in real use are chemical names, and they "
        "are really formulas written out.",
        "on words",
    ),
    _p(
        "Malaria means bad air. People named the disease after what they "
        "thought caused it, and the name outlived the theory by more than a "
        "century.",
        "etymology",
    ),
    _p(
        "A word can be its own opposite. To dust means to remove dust or to "
        "add it; to sanction means to permit or to punish. These are called "
        "contronyms, and context does all the work.",
        "on words",
    ),
    _p(
        "Silhouette was a finance minister. He was so notoriously mean that "
        "anything cheap was named after him, and the cheapest possible "
        "portrait was an outline cut from black paper.",
        "etymology",
    ),
    _p(
        "Alphabet is alpha and beta glued together. Plenty of words are simply "
        "the first items of a list, which is also where we get the scale doh "
        "re mi and the word gamut.",
        "etymology",
    ),
    _p(
        "English keeps borrowing and rarely gives anything back. That is why "
        "it has so many near-synonyms: one word from Old English, one from "
        "French, and a formal one from Latin.",
        "on words",
    ),
    _p(
        "Companion means the person you share bread with. Company, "
        "accompany and companionable all carry the same loaf in them.",
        "etymology",
    ),
    _p(
        "Spelling was standardised by printers, not scholars. Some of the odd "
        "letters in English words are there because a compositor needed to "
        "even up a line.",
        "on words",
    ),
    _p(
        "Disaster means bad star. Anything that went wrong was once assumed to "
        "have an astronomical explanation, and the assumption is still in the "
        "word.",
        "etymology",
    ),
    _p(
        "Assemble, resemble and dissemble share a root meaning to be alike. "
        "Once you notice a prefix pattern, a whole shelf of words stops "
        "needing to be memorised separately.",
        "on words",
    ),
    _p(
        "Muscat, musket and mosquito have unrelated origins that sound "
        "related. False friends are common enough that etymology is done with "
        "records rather than by ear.",
        "on words",
    ),
)
