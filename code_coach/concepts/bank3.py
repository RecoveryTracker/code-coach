"""One topic per language: what that language is doing behind the syntax.

The shared topics are about the machine, so everybody gets them. These are
about the language on screen, so you get exactly one of them — the one you
are writing. They sit at the front of the list because the language question
is the one an interviewer opens with.

The C++ topic lives in `bank` for historical reasons and is tagged the same
way; from the outside it is one of these.
"""

from __future__ import annotations

from code_coach.concepts import Topic, _q

_PYTHON = Topic(
    id="python-semantics",
    name="Python Semantics",
    order=1,
    languages=("python",),
    blurb="Names, objects and the interpreter underneath — where the convenience is paid for.",
    questions=(
        _q(
            "What is the difference between `is` and `==`?",
            "`==` asks the objects whether they consider themselves equal, by "
            "calling __eq__. `is` asks whether they are the same object, by "
            "comparing identity. The reason it matters is that small ints and "
            "short strings are interned, so `is` appears to work on them and "
            "then stops working the moment the values get bigger. Use `is` "
            "only for None, True and False, where identity is the guarantee.",
            "Why does `a is b` return True for 256 but False for 257?",
        ),
        _q(
            "Why is a mutable default argument a trap?",
            "The default is evaluated once, when the function is defined, and "
            "the same object is reused on every call that does not pass one. "
            "So a list default accumulates across calls, and the bug shows up "
            "as state leaking between callers who share nothing else. The fix "
            "is to default to None and build the list inside the body, which "
            "gives you a fresh one per call.",
            "When is a mutable default actually the behaviour you want?",
        ),
        _q(
            "What does the GIL actually prevent?",
            "It prevents more than one thread executing Python bytecode at "
            "once, so pure-Python CPU work does not scale across cores with "
            "threads. It does not prevent concurrency: a thread releases the "
            "lock around blocking I/O, so I/O-bound work threads perfectly "
            "well. And it does not make your code thread-safe, because the "
            "interpreter can switch threads between any two bytecodes.",
            "Does the GIL make `x += 1` atomic across threads?",
        ),
        _q(
            "How does attribute lookup actually resolve?",
            "For an instance, Python checks the type for a data descriptor "
            "first, then the instance __dict__, then the type and its MRO for "
            "anything else, then falls back to __getattr__. That ordering is "
            "why a property on the class beats a value set on the instance, "
            "and why __getattr__ only fires when everything else has already "
            "failed to find the name.",
            "Why does __getattribute__ get called even when the attribute exists?",
        ),
        _q(
            "What makes a generator different from a list comprehension?",
            "A generator holds a suspended frame instead of a result: it "
            "computes each value when asked and keeps only its own local "
            "state, so memory is constant rather than proportional to the "
            "output. The cost is that it is single-pass and has no length. "
            "Reach for it when the sequence is large, unbounded, or fed "
            "straight into something that consumes it once.",
            "What happens if you iterate the same generator twice?",
        ),
        _q(
            "What does a decorator do to the function it wraps?",
            "It replaces the name with whatever the decorator returns, which "
            "is usually a new function closing over the original. That is why "
            "the wrapped function loses its __name__ and docstring unless you "
            "copy them across with functools.wraps, and why stacked "
            "decorators apply bottom-up: the one nearest the def wraps first "
            "and the one on top wraps the result.",
            "How would you write a decorator that takes arguments of its own?",
        ),
        _q(
            "Why does CPython use reference counting and a cycle collector?",
            "Reference counting frees an object the moment its last reference "
            "goes away, which is prompt and predictable, and it is why "
            "CPython can guarantee __del__ runs at a sensible time. What it "
            "cannot do is reclaim cycles, because two objects pointing at each "
            "other never reach zero. The generational collector exists solely "
            "to find those.",
            "What does a __del__ on an object in a cycle do to collection?",
        ),
        _q(
            "What is the difference between __slots__ and a normal class?",
            "__slots__ replaces the per-instance __dict__ with a fixed array "
            "of descriptors, so instances get smaller and attribute access "
            "gets slightly faster, but you can no longer add attributes that "
            "were not declared. It is worth reaching for when you have "
            "millions of small objects and worth ignoring otherwise, because "
            "it interacts badly with multiple inheritance.",
            "What happens to __slots__ when a subclass does not declare any?",
        ),
        _q(
            "How does a context manager guarantee cleanup?",
            "The with statement calls __enter__, runs the body, and calls "
            "__exit__ in a finally, so the exit runs whether the body "
            "returned, raised or broke out. __exit__ receives the exception "
            "and can swallow it by returning true, which is how "
            "contextlib.suppress works. The guarantee is the finally, not the "
            "syntax.",
            "What does yielding inside contextlib.contextmanager correspond to?",
        ),
        _q(
            "Why is string concatenation in a loop a problem?",
            "Strings are immutable, so each concatenation allocates a new one "
            "and copies everything so far, making the loop quadratic in the "
            "total length. CPython has a special case that sometimes extends "
            "in place, but it only applies when the old string has exactly one "
            "reference, so it is not something to rely on. Build a list and "
            "join it once.",
            "Why does join need the whole sequence before it starts?",
        ),
        _q(
            "What does asyncio actually give you over threads?",
            "One thread, one event loop, and switching only at an await — so "
            "there is no preemption and far less state can be interleaved "
            "unexpectedly. Tasks are cheap enough to have tens of thousands, "
            "which threads are not. The price is that any blocking call stalls "
            "everything, so every library on the path has to be async or "
            "pushed to an executor.",
            "What happens to the loop if you call time.sleep inside a coroutine?",
        ),
        _q(
            "How does the method resolution order get decided?",
            "By C3 linearisation, which produces an order that keeps each "
            "class before its own bases and preserves the order the bases were "
            "written in. If no such order exists, the class statement raises "
            "at definition time rather than silently picking one. That is what "
            "makes cooperative super() calls reach every class in a diamond "
            "exactly once.",
            "Why does super() need the MRO rather than just the parent class?",
        ),
    ),
)

_JAVASCRIPT = Topic(
    id="javascript-semantics",
    name="JavaScript Semantics",
    order=2,
    languages=("javascript",),
    blurb="Coercion, closures and the event loop — the parts that bite in interviews.",
    questions=(
        _q(
            "What is the difference between var, let and const?",
            "var is function-scoped and hoisted as undefined, so it exists "
            "before its line runs. let and const are block-scoped and sit in "
            "the temporal dead zone until the declaration executes, so "
            "touching them early throws rather than giving you undefined. "
            "const binds the name, not the value, so a const object is still "
            "mutable.",
            "What does the temporal dead zone protect you from?",
        ),
        _q(
            "How is `this` determined at a call site?",
            "By how the function is called, not where it was written: a bare "
            "call gets undefined in strict mode, a method call gets the "
            "object before the dot, new gets the fresh object, and call, apply "
            "and bind set it explicitly. Arrow functions are the exception "
            "because they have no `this` of their own and close over the one "
            "in scope where they were defined.",
            "Why does passing a method as a callback usually lose `this`?",
        ),
        _q(
            "What is the event loop doing between microtasks and macrotasks?",
            "It runs one macrotask, then drains the entire microtask queue "
            "before rendering or taking the next macrotask. Promise callbacks "
            "are microtasks and setTimeout callbacks are macrotasks, which is "
            "why a resolved promise always runs before a zero-delay timeout. "
            "A microtask that keeps queueing microtasks starves the loop "
            "completely.",
            "What happens if a microtask schedules another microtask forever?",
        ),
        _q(
            "What is the prototype chain?",
            "Every object has a hidden link to another object, and a property "
            "lookup that misses walks that link until it finds the name or "
            "reaches null. Classes are syntax over the same mechanism: methods "
            "live on the prototype rather than on each instance, which is why "
            "adding one after the fact is visible to objects created earlier.",
            "What is the difference between __proto__ and prototype?",
        ),
        _q(
            "Why is == worth avoiding?",
            "Because it coerces before comparing, using a table of rules that "
            "nobody remembers correctly: null equals undefined but neither "
            "equals false, an empty string equals zero, and an array can equal "
            "a number. === compares without coercion and is what you almost "
            "always mean. The one useful exception is x == null as a check for "
            "either null or undefined.",
            "Why does an empty array compare equal to false?",
        ),
        _q(
            "What does a closure actually capture?",
            "The variable binding, not the value at the time of definition. So "
            "a closure created inside a var loop sees the loop variable's final "
            "value, because there was only ever one binding, while a let loop "
            "creates a fresh binding per iteration and each closure sees its "
            "own. The whole classic bug is the difference between one binding "
            "and many.",
            "How would you fix the var-loop closure bug without using let?",
        ),
        _q(
            "What does async/await compile down to?",
            "A state machine over promises. await suspends the function, "
            "registers a continuation as a microtask, and returns to the "
            "caller, so an async function returns a promise the moment it "
            "first awaits. That means the code after an await runs later than "
            "the code after the call, and awaiting in a loop serialises work "
            "that Promise.all would overlap.",
            "When is awaiting inside a loop the right thing rather than the wrong thing?",
        ),
        _q(
            "How does hoisting differ for functions and variables?",
            "Function declarations are hoisted whole, so you can call one "
            "above its definition. Variable declarations are hoisted without "
            "their initialiser, so a var is undefined until the assignment "
            "runs and a let throws. A function expression assigned to a const "
            "follows the const rules, which is why it is not callable earlier "
            "in the file.",
            "What happens when a function declaration and a var share a name?",
        ),
        _q(
            "What is the difference between null and undefined?",
            "undefined is the absence the language produces: an unassigned "
            "variable, a missing argument, a property that was never set. null "
            "is the absence a programmer writes on purpose. They are loosely "
            "equal to each other and to nothing else, and typeof null returns "
            "object, which is a bug old enough that fixing it would break the "
            "web.",
            "Which one does a missing function parameter get, and can a default fill it?",
        ),
        _q(
            "Why are objects compared by reference?",
            "Because the value of an object variable is the reference, so "
            "equality compares which object rather than what is in it. Two "
            "separately built objects with identical contents are never equal, "
            "and passing an object to a function shares it rather than copying "
            "it. Spread and Object.assign copy one level, so nested objects "
            "are still shared.",
            "What breaks when you deep-clone an object with JSON round-tripping?",
        ),
        _q(
            "What does the module system change about scope?",
            "A module has its own top-level scope rather than sharing the "
            "global one, it is always in strict mode, and its bindings are "
            "live: an imported name reflects later assignments in the "
            "exporting module rather than being a snapshot. Imports are also "
            "hoisted and resolved before any module body runs, which is what "
            "makes circular imports observable.",
            "What does an importing module see during a circular import?",
        ),
        _q(
            "What is the difference between map, forEach and reduce?",
            "map builds a new array of the same length from the return values, "
            "forEach returns nothing and exists purely for side effects, and "
            "reduce folds the sequence into one accumulated value. Using map "
            "for side effects allocates an array of undefined that nobody "
            "reads, which is the tell that forEach was meant.",
            "How would you express map and filter as a single reduce?",
        ),
    ),
)

_TYPESCRIPT = Topic(
    id="typescript-semantics",
    name="TypeScript Semantics",
    order=3,
    languages=("typescript",),
    blurb="The type system's rules, and the line where it stops protecting you.",
    questions=(
        _q(
            "What does structural typing mean in practice?",
            "Compatibility is decided by shape rather than by declared name, "
            "so a value matches a type if it has the required members with "
            "compatible types, whether or not it was written to implement it. "
            "That makes interfaces cheap to satisfy and means two unrelated "
            "types with the same fields are interchangeable, which is "
            "sometimes exactly wrong.",
            "How would you make two structurally identical types incompatible?",
        ),
        _q(
            "What is the difference between any and unknown?",
            "any switches the checker off for that value, so every property "
            "access and call is allowed and every downstream inference is "
            "poisoned. unknown is the honest top type: you can hold it and "
            "pass it around, but you must narrow it before you can do anything "
            "with it. unknown is what you want at the boundary where data "
            "arrives.",
            "What does an `any` returned from a library do to the code that uses it?",
        ),
        _q(
            "How does type narrowing work?",
            "The checker follows control flow and shrinks the type of a name "
            "inside branches that prove something about it — typeof, "
            "instanceof, truthiness, an equality check against a literal, or "
            "a user-defined type predicate. The narrowing is discarded at any "
            "point the value could have changed, which is why it does not "
            "survive into a callback.",
            "Why does narrowing get lost inside a closure?",
        ),
        _q(
            "What is a discriminated union and why is it worth the extra field?",
            "It is a union whose members share a literal-typed field with a "
            "different value in each, so checking that one field narrows to "
            "exactly one member. The payoff is exhaustiveness: switch on the "
            "discriminant, assign the default case to never, and adding a new "
            "member turns every unhandled site into a compile error.",
            "How does assigning to never give you an exhaustiveness check?",
        ),
        _q(
            "What is the difference between an interface and a type alias?",
            "Interfaces describe object shapes, can be implemented and "
            "extended, and merge when declared twice, which is what makes "
            "them the right tool for augmenting external declarations. Type "
            "aliases can name anything — unions, tuples, conditional and "
            "mapped types — but do not merge. Prefer interface for objects "
            "and alias for everything else.",
            "When is declaration merging a feature rather than a hazard?",
        ),
        _q(
            "What do generics buy over just using a union?",
            "They preserve the relationship between inputs and output. A "
            "function taking a union can return the union, but a generic "
            "returns the specific type the caller passed, so the caller does "
            "not have to narrow afterwards. The rule of thumb is that a type "
            "parameter used only once is usually a union in disguise.",
            "Why is a type parameter that appears in only one position suspicious?",
        ),
        _q(
            "What does `readonly` actually enforce?",
            "Compile-time assignment checking and nothing else. The property "
            "is still writable at runtime, a readonly array is assignable "
            "from a mutable one, and a cast removes it entirely. It documents "
            "and catches accidental mutation in your own code; it is not a "
            "guarantee against code you do not control.",
            "Why can a mutable array be passed where a readonly array is expected?",
        ),
        _q(
            "What is the point of a const assertion?",
            "It stops widening. Without it a literal becomes its base type, so "
            "an object's fields become string and number and an array becomes "
            "a mutable array. With `as const` everything stays at its literal "
            "type and becomes readonly, which is what makes a lookup table "
            "usable as a source of union types.",
            "How do you derive a union of a const object's values as a type?",
        ),
        _q(
            "How do conditional types and infer work together?",
            "A conditional type picks a branch by asking whether one type "
            "extends another, and infer introduces a name for a piece of the "
            "matched shape so the true branch can use it. That is how "
            "ReturnType and Awaited are written: match the shape, capture the "
            "part you want, return it. Over a union, the conditional "
            "distributes across members.",
            "When does a conditional type distribute over a union and when does it not?",
        ),
        _q(
            "What does the compiler do at runtime?",
            "Nothing — it erases. Types, interfaces and type parameters are "
            "gone after compilation, so there is no runtime check on an API "
            "response, no reflection over a type, and no way to test a "
            "generic parameter. Anything you need at runtime has to exist as "
            "a value, which is why validation at the boundary is a separate "
            "job.",
            "How do you get a runtime check and a static type from one definition?",
        ),
        _q(
            "Why is strictNullChecks the setting that matters most?",
            "Without it null and undefined are members of every type, so the "
            "checker cannot tell you about the single most common runtime "
            "error in the language. With it they are separate types you have "
            "to admit into a signature and narrow before use, which turns "
            "every possible null dereference into a compile error.",
            "What does the non-null assertion operator give up?",
        ),
        _q(
            "What is the difference between a type guard and a type assertion?",
            "A guard is a runtime check whose signature tells the compiler "
            "what the check proves, so narrowing is earned. An assertion is a "
            "claim with no check behind it, so it silently converts a wrong "
            "belief into a runtime error somewhere later. Assertions belong "
            "where you genuinely know more than the checker and nowhere else.",
            "How would you write a predicate that validates a parsed JSON payload?",
        ),
    ),
)

_RUST = Topic(
    id="rust-semantics",
    name="Rust Semantics",
    order=8,
    languages=("rust",),
    blurb="Ownership, lifetimes and what unsafe actually promises the compiler.",
    questions=(
        _q(
            "What are the borrowing rules, and what do they buy?",
            "At any moment a value may have either any number of shared "
            "references or exactly one mutable reference, never both. That "
            "single rule rules out use-after-free, data races and iterator "
            "invalidation at compile time, because every one of those requires "
            "aliasing and mutation at once. It also lets the compiler assume "
            "no aliasing and optimise accordingly.",
            "Which bug class does the rule eliminate that a garbage collector does not?",
        ),
        _q(
            "What is a lifetime actually annotating?",
            "A region of code over which a reference stays valid. The "
            "annotation does not change how long anything lives; it relates "
            "the lifetimes of inputs and outputs so the compiler can check "
            "that a returned reference cannot outlive what it points into. "
            "Elision fills in the common patterns, which is why most "
            "signatures need none.",
            "Why can a function not return a reference to its own local?",
        ),
        _q(
            "What is the difference between Copy, Clone and a move?",
            "A move transfers ownership and invalidates the source, which is "
            "the default for anything owning a resource. Clone is an explicit, "
            "possibly expensive duplicate. Copy marks types whose bitwise copy "
            "is a valid independent value, so assignment duplicates instead of "
            "moving. A type owning a heap allocation cannot be Copy, because "
            "two owners would both free it.",
            "Why can a type that implements Drop never be Copy?",
        ),
        _q(
            "What do Send and Sync mean?",
            "Send means the type can be moved to another thread; Sync means a "
            "shared reference to it can be. They are auto traits, derived "
            "structurally, and they are what makes the bound on thread::spawn "
            "enough to rule out data races. Rc is neither, because its count "
            "is not atomic, which is exactly why the compiler rejects sharing "
            "one across threads.",
            "Why is a type Sync exactly when a shared reference to it is Send?",
        ),
        _q(
            "What does interior mutability mean and why is it sound?",
            "It is mutation through a shared reference, which the borrowing "
            "rules otherwise forbid. Types built on UnsafeCell move the "
            "aliasing check somewhere the compiler can no longer do it: "
            "RefCell checks at runtime and panics, Mutex checks by blocking, "
            "and atomics make the operation indivisible. The invariant is "
            "upheld either way, just not statically.",
            "What does RefCell have to track that Cell does not?",
        ),
        _q(
            "What does the question-mark operator expand to?",
            "A match that returns the value on Ok or Some, and on the error "
            "path converts the error with From and returns it early. The "
            "conversion is the useful half: a function returning a boxed error "
            "or an enum of its own can propagate several error types without "
            "any mapping at the call site, as long as the From impls exist.",
            "Why does it sometimes fail to compile with an error type mismatch?",
        ),
        _q(
            "When is a trait object the right choice over generics?",
            "Generics monomorphise, so each concrete type gets its own copy: "
            "fastest, statically dispatched, and larger. A trait object is one "
            "copy behind a vtable, dynamically dispatched, and lets you hold a "
            "heterogeneous collection. Reach for dyn when the set of types is "
            "open or lives in one container, and for generics otherwise.",
            "What makes a trait not object-safe?",
        ),
        _q(
            "What exactly does the unsafe keyword turn off?",
            "Five things and nothing else: dereferencing a raw pointer, "
            "calling an unsafe function, implementing an unsafe trait, "
            "accessing a mutable static, and reading a union field. The borrow "
            "checker and the type system still apply. What the keyword really "
            "means is that you are now responsible for an invariant the "
            "compiler was checking for you.",
            "What is the difference between an unsafe block and an unsafe function?",
        ),
        _q(
            "How does Drop interact with moves and panics?",
            "Drop runs when a value goes out of scope still owning its "
            "resource, in reverse declaration order, and it runs during "
            "unwinding too, which is what makes cleanup exception-safe by "
            "default. A moved-from value is not dropped, because ownership "
            "went with the move. Forgetting a value with mem::forget skips the "
            "drop and is safe, just leaky.",
            "Why is leaking memory considered safe in Rust?",
        ),
        _q(
            "What is the difference between String and a string slice?",
            "String owns a growable heap buffer; a str slice is a borrowed "
            "view of UTF-8 bytes that could live anywhere, including in the "
            "binary. Taking the slice in a function accepts both and copies "
            "nothing, which is why it is the default parameter type. Indexing "
            "either by integer is refused, because a byte offset can land "
            "mid-character.",
            "Why does slicing a string panic rather than returning an error?",
        ),
        _q(
            "What does a closure capture, and what do the Fn traits mean?",
            "It captures each used variable by the weakest way that works — "
            "shared reference, then mutable reference, then by move — unless "
            "you write move to force ownership. The trait it implements "
            "follows: Fn if it only reads, FnMut if it mutates its captures, "
            "and FnOnce if calling it consumes them.",
            "Why does a closure passed to thread::spawn usually need move?",
        ),
        _q(
            "Why does Rust have no null, and what replaced it?",
            "Option, an ordinary enum, so absence is in the type and the "
            "compiler forces you to handle it before you can reach the value. "
            "It costs nothing for references and Box, because the compiler "
            "uses the impossible null value as the None discriminant, making "
            "an optional reference the same size as a pointer.",
            "Which types get the null-pointer optimisation and which do not?",
        ),
    ),
)

_C = Topic(
    id="c-semantics",
    name="C Semantics",
    order=6,
    languages=("c",),
    blurb="What the standard actually promises, and the long list of things it does not.",
    questions=(
        _q(
            "What is undefined behaviour and why is it worse than a crash?",
            "It is a construct the standard places no requirement on at all, "
            "so the compiler is entitled to assume it never happens and "
            "optimise on that assumption. The consequence is not a reliable "
            "crash but code deleted or reordered elsewhere: a null check "
            "removed because you already dereferenced the pointer, a loop "
            "assumed to terminate because overflow cannot happen.",
            "Why can a signed overflow check written after the addition disappear?",
        ),
        _q(
            "What is the difference between an array and a pointer?",
            "An array is a block of objects with a size the compiler knows; a "
            "pointer is one address. An array decays to a pointer to its first "
            "element in almost every expression, which is why they feel alike "
            "and why sizeof stops working once it has been passed to a "
            "function. A parameter written as an array is a pointer.",
            "What does sizeof report for an array parameter, and why?",
        ),
        _q(
            "What does static mean in each place it can appear?",
            "At file scope it means internal linkage: the name is not visible "
            "to other translation units. On a local variable it means static "
            "storage duration, so the variable lives for the whole program and "
            "keeps its value across calls. On a function it is internal "
            "linkage again. One keyword, two unrelated meanings, decided by "
            "position.",
            "What is the initial value of a static local before it is assigned?",
        ),
        _q(
            "What does volatile guarantee, and what does it not?",
            "It tells the compiler that every read and write in the source "
            "must actually happen and must not be cached in a register or "
            "elided, which is what memory-mapped hardware and a signal-handler "
            "flag need. It does not make anything atomic and it does not order "
            "accesses against the processor's own reordering, so it is not a "
            "threading tool.",
            "What should you reach for instead of volatile to share between threads?",
        ),
        _q(
            "What is strict aliasing and how does it bite?",
            "The compiler may assume that pointers of incompatible types never "
            "refer to the same object, so it can keep a value in a register "
            "across a store through a different type. Reinterpreting a float "
            "as an integer by casting pointers breaks that assumption and the "
            "result changes with the optimisation level. Copying the bytes is "
            "the supported way.",
            "Why is a union-based type pun better defined in C than in C++?",
        ),
        _q(
            "What is the difference between a declaration and a definition?",
            "A declaration introduces the name and type so callers can be "
            "checked; a definition also allocates storage or provides a body. "
            "A header holds declarations because it is included many times, "
            "and putting a definition there gives a multiple-definition error "
            "at link time rather than at compile time, which is why the error "
            "arrives so late.",
            "What does extern change on a variable at file scope?",
        ),
        _q(
            "How does integer promotion change an expression?",
            "Anything narrower than int is promoted to int before arithmetic, "
            "so two unsigned chars add as ints and cannot wrap. Then the usual "
            "arithmetic conversions apply, and a mix of signed and unsigned of "
            "the same rank converts the signed one to unsigned, which is how a "
            "comparison against a negative number quietly becomes true.",
            "Why does comparing a negative int against an unsigned size fail?",
        ),
        _q(
            "What are the rules for struct padding and alignment?",
            "Each member is placed at an offset that satisfies its own "
            "alignment, and the struct is padded at the end so an array of "
            "them keeps every element aligned. So member order determines the "
            "size, largest-first usually packs tightest, and comparing two "
            "structs byte by byte can differ on the padding even when every "
            "member matches.",
            "Why is a byte-by-byte comparison of two structs an unreliable equality test?",
        ),
        _q(
            "What does the preprocessor do that trips people up?",
            "It substitutes text before the compiler sees any of it, so a "
            "macro has no scope, no types and no evaluation rules of its own. "
            "An argument used twice is evaluated twice, an unparenthesised "
            "body binds wrongly inside a larger expression, and a multi-line "
            "macro without a do-while wrapper breaks an unbraced if.",
            "Why do macro bodies get wrapped in a do-while that runs once?",
        ),
        _q(
            "How does a local differ from an allocation you asked for?",
            "A local lives until its block ends and costs one register "
            "adjustment; an allocation lives until you free it and costs a "
            "trip through the allocator. The consequence is ownership: "
            "returning a pointer to a local returns a pointer to reused space, "
            "while returning an allocated pointer transfers a duty to free "
            "that the type system will not remind anybody about.",
            "What does the allocator store next to your block, and why does that matter?",
        ),
        _q(
            "What makes a function safe to call from a signal handler?",
            "Only that it is on the async-signal-safe list, which is short: no "
            "allocation, no formatted output, no locks. A handler interrupts "
            "the thread wherever it was, possibly mid-allocation, so calling "
            "anything that takes the same lock deadlocks. The usual handler "
            "sets one flag or writes a byte to a pipe and returns.",
            "Why is writing to a self-pipe the standard way out of a handler?",
        ),
        _q(
            "How does const on a pointer differ from const on its target?",
            "Read the declaration outward from the name. A const before the "
            "star qualifies what is pointed at, so you cannot write through it "
            "but you can repoint it. A const after the star qualifies the "
            "pointer, so you can write through it but cannot repoint it. "
            "Neither makes the object immutable if somebody else holds a "
            "non-const path to it.",
            "Does casting away const and then writing have defined behaviour?",
        ),
    ),
)

_DART = Topic(
    id="dart-semantics",
    name="Dart Semantics",
    order=4,
    languages=("dart",),
    blurb="Null safety, isolates and the async model Flutter is built on.",
    questions=(
        _q(
            "What does sound null safety actually guarantee?",
            "That a variable whose type is not nullable can never hold null, "
            "checked at compile time and relied on at runtime — so the "
            "compiler can drop null checks rather than merely warn you. "
            "Soundness is why the migration was disruptive: one unsound hole "
            "would make the guarantee worthless everywhere.",
            "What does the late keyword trade away to defer initialisation?",
        ),
        _q(
            "How does an isolate differ from a thread?",
            "It has its own memory and its own event loop and shares nothing, "
            "so there is no locking and no data races by construction. "
            "Communication is by message passing over ports, and the messages "
            "are copied rather than shared. That is why moving work off the UI "
            "isolate costs a serialisation rather than a synchronisation.",
            "What kinds of object can and cannot be sent through a SendPort?",
        ),
        _q(
            "What is the difference between a Future and a Stream?",
            "A Future is one value that arrives later, or an error. A Stream is "
            "zero or more values over time, plus a completion. await works on a "
            "Future; await for iterates a Stream. Choosing wrongly usually "
            "shows up as either a callback that only ever fires once or a "
            "subscription nobody cancels.",
            "What happens to a stream subscription that is never cancelled?",
        ),
        _q(
            "What is the difference between const and final in Dart?",
            "final means assigned once at runtime; const means the value is "
            "computed at compile time and canonicalised, so two identical const "
            "values are the same object. A const constructor lets a widget be "
            "built once and reused, which is the reason const shows up "
            "everywhere in Flutter trees.",
            "Why does a const widget constructor help rebuild performance?",
        ),
        _q(
            "What does the Dart event loop do with microtasks?",
            "It drains the entire microtask queue before taking the next event "
            "from the event queue, so a scheduled microtask always runs before "
            "the next timer or I/O callback. Future callbacks land on the "
            "microtask queue, and a microtask that keeps scheduling microtasks "
            "starves everything else including rendering.",
            "Which queue does a Timer with zero duration land on?",
        ),
        _q(
            "What is a mixin and how does it resolve conflicts?",
            "A way to reuse a body of members in classes that do not share a "
            "base. Mixins are applied in order and each one is linearised over "
            "the previous, so the last mixin listed wins for a name declared "
            "more than once, and super inside a mixin refers to whatever came "
            "before it in that chain.",
            "How does the order of the with clause change which method runs?",
        ),
        _q(
            "What does the cascade operator buy?",
            "It lets a sequence of calls target the same object without "
            "repeating the receiver and without the object needing to return "
            "itself, because the cascade evaluates to the receiver rather than "
            "to each call's result. It is the reason builder-style APIs in Dart "
            "do not have to be written to chain.",
            "What does a cascade evaluate to when the last call returns a value?",
        ),
        _q(
            "What is the difference between == and identical?",
            "== calls the operator, which classes may override to compare "
            "contents, and identical asks whether two references are the same "
            "object. Overriding == without overriding hashCode breaks every "
            "hash-based collection, because two equal objects can then land in "
            "different buckets.",
            "What contract must hashCode satisfy relative to ==?",
        ),
        _q(
            "How do Dart generics behave at runtime?",
            "They are reified, unlike Java's: a List of int knows its own type "
            "argument, so it is available for checks and casts and a wrong "
            "insert fails rather than passing silently. Generics are covariant "
            "by default, which is convenient and lets a list of int flow where "
            "a list of num is expected, at the cost of a runtime check.",
            "What can go wrong because Dart generics are covariant?",
        ),
        _q(
            "What does async* do that async does not?",
            "It makes the function return a Stream and lets it yield values "
            "one at a time, suspending between them, where async returns a "
            "single Future. yield adds one value and yield* splices in another "
            "stream. The generator only runs while somebody is listening, so "
            "nothing happens before subscription.",
            "When does the body of an async* function start executing?",
        ),
        _q(
            "What is the point of the ?? and ?. operators?",
            "?. short-circuits the whole access chain to null instead of "
            "throwing when the receiver is null, and ?? supplies a value when "
            "the left side is null. Together they replace the nested null "
            "checks that null safety would otherwise force at every step, "
            "without weakening the type.",
            "How does ??= differ from a plain assignment with a null check?",
        ),
        _q(
            "Why does Flutter care whether a widget is stateless or stateful?",
            "A widget is a description, rebuilt cheaply and often. A stateless "
            "one holds nothing across rebuilds; a stateful one keeps a "
            "separate State object that the framework preserves as the widget "
            "objects are replaced. State is where anything that must survive a "
            "rebuild has to live.",
            "What decides whether the framework reuses an existing State object?",
        ),
    ),
)

_SQL = Topic(
    id="sql-semantics",
    name="SQL Semantics",
    order=5,
    languages=("sql",),
    blurb="What the planner does with your query, and where three-valued logic bites.",
    questions=(
        _q(
            "In what order does a SELECT actually evaluate?",
            "Logically FROM and JOIN first, then WHERE, then GROUP BY, then "
            "HAVING, then SELECT, then DISTINCT, then ORDER BY, then LIMIT. "
            "That order explains the everyday errors: a SELECT alias is not "
            "visible in WHERE because the projection has not happened yet, and "
            "an aggregate cannot be filtered in WHERE because grouping comes "
            "later.",
            "Why can ORDER BY use a select alias when WHERE cannot?",
        ),
        _q(
            "What does NULL do to comparisons and aggregates?",
            "Any comparison with NULL yields unknown rather than true or "
            "false, so a row fails both a condition and its negation, and "
            "NOT IN against a list containing NULL matches nothing. Aggregates "
            "go the other way and skip NULLs, so COUNT of a column differs "
            "from COUNT of everything and AVG divides by the non-null count.",
            "Why does NOT IN with a NULL in the subquery return no rows?",
        ),
        _q(
            "What is the difference between WHERE and HAVING?",
            "WHERE filters rows before grouping and can use an index; HAVING "
            "filters groups after aggregation and sees the aggregate values. "
            "Putting a non-aggregate condition in HAVING usually still works "
            "and is slower, because rows that could have been discarded early "
            "were grouped first.",
            "When does a condition genuinely belong in HAVING?",
        ),
        _q(
            "What does an index actually let the planner skip?",
            "A sorted structure over the key columns lets it seek to a range "
            "rather than scanning, and if every column the query needs is in "
            "the index it can answer without touching the table at all. The "
            "leftmost-prefix rule follows from the sort order: a composite "
            "index helps a predicate on its first column, not on its second "
            "alone.",
            "What makes a query covered by an index, and why is that faster?",
        ),
        _q(
            "Why does wrapping a column in a function defeat an index?",
            "Because the index stores the column's values, not the function's "
            "results, so the planner cannot map a predicate on the output back "
            "to a range of the input and falls back to scanning every row. "
            "Rewriting the predicate to compare the bare column against a "
            "computed bound restores the seek, or you index the expression.",
            "How would you rewrite a date-truncation filter to stay sargable?",
        ),
        _q(
            "How does a LEFT JOIN differ from an INNER JOIN with a filter?",
            "A LEFT JOIN keeps unmatched left rows with NULLs on the right. "
            "Putting a condition on the right table in WHERE discards exactly "
            "those NULL rows and silently turns the outer join back into an "
            "inner one. The condition has to go in the ON clause to stay part "
            "of the match rather than the filter.",
            "What is the difference between a predicate in ON and the same one in WHERE?",
        ),
        _q(
            "What do the isolation levels actually trade?",
            "Higher levels remove anomalies at the cost of concurrency: read "
            "committed prevents dirty reads but allows a value to change "
            "between two reads, repeatable read pins the rows you have read, "
            "and serialisable makes the outcome equal to some serial order, "
            "usually by aborting transactions that would violate it.",
            "Which anomaly does repeatable read still permit, and how?",
        ),
        _q(
            "What is a window function and when does it beat a GROUP BY?",
            "It computes an aggregate over a set of rows related to the "
            "current one without collapsing them, so you keep every row and "
            "gain a total, a rank or a running sum beside it. GROUP BY is the "
            "right tool when you actually want fewer rows out than in.",
            "How do ROWS and RANGE differ in a window frame?",
        ),
        _q(
            "How does a correlated subquery differ from an uncorrelated one?",
            "An uncorrelated one is evaluated once and its result reused. A "
            "correlated one references the outer row, so conceptually it runs "
            "per row, and the planner will often rewrite it into a join or a "
            "semi-join instead. When it cannot, the cost grows with the outer "
            "row count.",
            "Why is EXISTS often better than IN for a correlated check?",
        ),
        _q(
            "What does a transaction guarantee, one letter at a time?",
            "Atomicity means all or nothing, consistency means declared "
            "constraints still hold at the end, isolation means concurrent "
            "transactions do not see each other's partial work to the degree "
            "the level promises, and durability means a committed change "
            "survives a crash. Only isolation is something you tune.",
            "Which of the four is the application's job rather than the engine's?",
        ),
        _q(
            "What is the difference between UNION and UNION ALL?",
            "UNION removes duplicates, which requires sorting or hashing the "
            "whole result and is often the most expensive step in the query. "
            "UNION ALL concatenates. If you know the branches are disjoint, "
            "ALL is both faster and more honest about what you meant.",
            "How does the duplicate removal in UNION treat NULLs?",
        ),
        _q(
            "How does a query planner choose between a scan and a seek?",
            "By estimated cost, driven by statistics about how many rows a "
            "predicate will keep. If the estimate says most of the table "
            "matches, a sequential scan beats a seek plus a random fetch per "
            "row. That is why stale statistics produce dramatically wrong "
            "plans, and why the estimated and actual row counts are the first "
            "thing to compare.",
            "What does a large gap between estimated and actual rows tell you?",
        ),
    ),
)

LANGUAGE_TOPICS: tuple[Topic, ...] = (
    _PYTHON,
    _JAVASCRIPT,
    _TYPESCRIPT,
    _DART,
    _SQL,
    _C,
    _RUST,
)
