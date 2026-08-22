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
