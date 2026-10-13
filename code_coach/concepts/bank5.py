"""Python interview questions, beyond the one semantics topic.

`python-semantics` in bank3 is the dozen questions every Python interview
opens with. This is the rest of what a Python interview asks, grouped by
the area a round is usually named after: names and mutability, scope and
decorators, iterators, the data model, exceptions, concurrency, memory,
typing, data structures, packaging, testing, web services, numerics, and the
gotchas that get asked as "what does this print".

Where an answer states an output, it is a real one: tests/
test_concepts_python_interview.py runs the example in the interpreter and
holds the answer to what came back. Version-dependent facts name the version.
The free-threaded build, the experimental JIT and the 3.14 changes are the
part most likely to move, so they are stated as of Python 3.14 and worded
to survive a point release.

Nothing here is copied: the facts come from the Python documentation and
the PEPs, and the choice of questions from what interview write-ups say
actually gets asked.
"""

from __future__ import annotations

from code_coach.concepts import Topic, _q

_PY = ("python",)

_NAMES = Topic(
    id="py-names-mutability",
    name="Python Names & Mutability",
    order=300,
    languages=_PY,
    blurb="Everything is a reference to an object; most bugs here are about which object.",
    questions=(
        _q(
            "Is Python pass by value or pass by reference?",
            "Neither, quite: the caller's reference is handed over and the "
            "parameter becomes a new name for the same object. So mutating "
            "the object inside the function is visible outside, but "
            "rebinding the parameter is not. `xs.append(1)` changes the "
            "caller's list; `xs = [9]` only points the local name somewhere "
            "else. The behaviour is the same as plain assignment, which is "
            "why it is sometimes called call by assignment.",
            "Why does `xs += [1]` inside a function change the caller's list?",
        ),
        _q(
            "What is the difference between copy.copy and copy.deepcopy?",
            "A shallow copy makes a new outer container but reuses the "
            "elements, so the two containers share their contents. Take "
            "`a = [[1], [2]]` and `b = copy.copy(a)`: after "
            "`a[0].append(9)`, b[0] is [1, 9]. deepcopy recurses and copies "
            "the elements too, using a memo table so cycles do not loop "
            "forever. Slicing and list() are shallow, and deepcopy costs "
            "real time on big structures.",
            "What does deepcopy do with an object that has a lock inside it?",
        ),
        _q(
            "Why can't a list be used as a dictionary key?",
            "A key's hash has to stay the same for as long as it is in the "
            "dictionary, otherwise it would sit in the wrong slot. A list "
            "is mutable and compares by contents, so Python sets its hash "
            "to None and `hash([])` raises TypeError. The rule reaches "
            "inside: a tuple is hashable only if everything in it is, so "
            "`hash((1, [2]))` fails with unhashable type: 'list'. Use a "
            "tuple or a frozenset instead.",
            "Is it a problem that a tuple of hashable things can hold a mutable one?",
        ),
        _q(
            "How is `a += b` different from `a = a + b` for a list?",
            "`+=` calls the in-place method, so a list is extended where "
            "it sits and the name stays bound to the same object. `a + b` "
            "builds a brand-new list and `a = ...` rebinds the name. If "
            "something else holds a reference to the original, the first "
            "form changes what it sees and the second does not. For "
            "immutable types like tuples and strings, `+=` quietly falls "
            "back to building a new object.",
            "What happens with `t[0] += [3]` when t is a tuple holding a list?",
        ),
        _q(
            "What does interning do for strings, and when would you call sys.intern?",
            "Interning keeps one shared copy of equal strings. CPython does "
            "it at compile time for short, identifier-like literals, which "
            "is why a literal can be `is` another literal while a string "
            "built at run time, such as one made with join, is a different "
            "object. sys.intern lets you opt in. It pays off when millions "
            "of repeated strings are used as keys, because lookups can "
            "succeed on identity before comparing characters.",
            "Why is it wrong to rely on `is` for strings even if it works today?",
        ),
        _q(
            "What does id() return, and what is it safe to do with it?",
            "An integer that identifies the object while it is alive, and "
            "in CPython it is the memory address. Two objects can only "
            "share an id if one of them is gone, so a freed object's id can "
            "be handed to the next new one. That makes it fine for a "
            "quick \"same object?\" check or a debugging label, and a bad "
            "choice for a dictionary key that outlives the objects.",
            "Why do two temporary objects often show the same id?",
        ),
        _q(
            "How do you build a grid without every row being the same list?",
            "`[[0] * 3] * 3` makes one inner list and repeats the "
            "reference, so `grid[0][0] = 1` shows up in every row and "
            "the result is [[1, 0, 0], [1, 0, 0], [1, 0, 0]]. A "
            "comprehension, `[[0] * 3 for _ in range(3)]`, runs the inner "
            "expression once per row and so makes separate lists. "
            "Multiplying is safe only when the repeated thing is "
            "immutable, like the 0 inside.",
            "Why is `[0] * 3` fine but `[[0]] * 3` is not?",
        ),
        _q(
            "Why does list.sort return None, and how is it different from sorted?",
            "sort changes the list in place and returns None on purpose: "
            "it is the convention that a method which mutates does not "
            "also return the object, so `x = x.sort()` fails loudly "
            "instead of looking fine. sorted takes any iterable and "
            "returns a new list. Both use the same stable algorithm and "
            "take a key function, so equal items keep their original "
            "order.",
            "Why does the stability matter when sorting by two fields?",
        ),
        _q(
            "A tuple is immutable, so how can its contents change?",
            "Immutability applies to which objects the tuple refers to, "
            "not to what those objects are. A tuple holding a list can't "
            "be given a different list, but the list can be appended to: "
            "`t = ([1], 2)` and `t[0].append(9)` leaves "
            "`([1, 9], 2)`. It is also why such a tuple is not hashable, "
            "since its value can change. If you need real immutability, "
            "freeze the contents as well.",
            "What does `t[0] += [3]` do to that tuple, step by step?",
        ),
        _q(
            "What does the del statement actually delete?",
            "A name binding, never the object itself. `del a` removes the "
            "name `a`, and the object is freed only if nothing else "
            "refers to it, which is why `b = a` followed by `del a` leaves "
            "b perfectly fine. `del xs[0]` and `del d[key]` are different: "
            "they call __delitem__ and remove an entry from the "
            "container. Reference counting does the actual freeing.",
            "What does `del` do to a name that is captured by a closure?",
        ),
        _q(
            "What is a weak reference and when would you use one?",
            "A reference that does not keep its target alive: "
            "`weakref.ref(obj)` returns something you call to get the "
            "object back, and it returns None once the object has been "
            "freed. It is the right tool for caches and observer lists, "
            "where the container should not be the reason an object "
            "survives. Plain classes support it; built-ins like list and "
            "dict do not, and a class using __slots__ needs a "
            "__weakref__ slot.",
            "How does WeakValueDictionary use that for a cache?",
        ),
    ),
)

_SCOPE = Topic(
    id="py-scope-decorators",
    name="Scope, Closures & Decorators",
    order=310,
    languages=_PY,
    blurb="Where a name is looked up, what a closure keeps alive, and what @ really means.",
    questions=(
        _q(
            "What is the LEGB rule?",
            "It is the order Python searches for a name: Local, then any "
            "Enclosing function, then Global (module), then Builtin, and the "
            "first hit wins. One consequence catches people: scope is "
            "decided when the function is compiled, so if a function "
            "assigns to `x` anywhere, `x` is local everywhere in it. "
            "Reading it before the assignment raises UnboundLocalError "
            "rather than falling back to a global.",
            "Why does `x += 1` fail in a function when x is a module-level number?",
        ),
        _q(
            "What do global and nonlocal do, and when are they needed?",
            "They are declarations that assignment should bind in a "
            "different scope: `global x` in the module scope, `nonlocal x` "
            "in the nearest enclosing function, where the name must "
            "already exist. They are only needed for rebinding. Reading "
            "a name, or mutating the object it points to, such as "
            "appending to a module-level list, needs no declaration. A "
            "counter closure is the usual reason to reach for nonlocal.",
            "How would you write a counter without nonlocal?",
        ),
        _q(
            "Why do lambdas made in a loop all return the last value?",
            "A closure captures the variable, not its value at that moment, "
            "and the lambdas are all looking at the same `i`, which the "
            "loop leaves at its final value: "
            "`[lambda: i for i in range(3)]` gives [2, 2, 2] when "
            "called. Bind the current value with a default argument, "
            "`lambda i=i: i`, or with functools.partial, because defaults "
            "are evaluated when the lambda is created.",
            "Why does the default-argument fix work when the closure does not?",
        ),
        _q(
            "What does functools.wraps do, and what breaks without it?",
            "It copies the wrapped function's __name__, __doc__, "
            "__module__ and other metadata onto the wrapper, and adds a "
            "__wrapped__ attribute pointing at the original. Without it "
            "every decorated function reports its name as `wrapper`, "
            "help() and docs show the wrong text, and frameworks that "
            "key on function names, such as Flask's endpoints, collide. "
            "It is one line and there is no reason to skip it.",
            "How would you get at the undecorated function afterwards?",
        ),
        _q(
            "How do you write a decorator that takes arguments?",
            "Add one more level: the outer function takes the arguments "
            "and returns the real decorator, which takes the function and "
            "returns the wrapper. `@repeat(3)` is evaluated first as a "
            "call, and its result is then applied to the function, so "
            "it is `repeat(3)(func)`. Forgetting the extra layer is why "
            "`@repeat` without brackets silently passes the function in "
            "as the count.",
            "How do you make one decorator work both with and without arguments?",
        ),
        _q(
            "How do you write a decorator that works on methods as well as functions?",
            "Have the wrapper take `*args, **kwargs` and pass them through "
            "unchanged: a method is just a function in the class, and "
            "`self` arrives as the first positional argument. That "
            "works because functions are descriptors that bind "
            "themselves on access. A decorator built as a class is "
            "different: its instance is not a function, so it needs its "
            "own __get__ to bind, or `self` goes missing.",
            "Why does a class-based decorator lose `self` on a method?",
        ),
        _q(
            "What does a Python closure actually capture, a value or a variable?",
            "Cells: when an inner function uses a variable from the "
            "enclosing function, Python keeps that variable alive in a "
            "cell that both functions share, rather than copying the "
            "value. So a later assignment in the outer function is seen "
            "by the inner one, and `make()()` returns \"bye\" if `msg` "
            "was rebound to \"bye\" after the inner function was defined. "
            "The cells are visible in `__closure__`.",
            "How would you find out what a function has closed over?",
        ),
        _q(
            "When does a decorator run: at import time or at call time?",
            "The decoration happens once, when the `def` statement is "
            "executed, which for module-level functions is import time. "
            "Only the wrapper it returns runs at call time. That is why "
            "route registration in Flask and test registration in pytest "
            "work: the decorator's side effect fires as the module loads. "
            "It also means a decorator that does expensive work is "
            "paid for at import, not when the function is first used.",
            "What does that imply for circular imports and decorators that register things?",
        ),
        _q(
            "What does functools.lru_cache give you, and what are its limits?",
            "Memoisation: results are stored by argument, so repeated "
            "calls become dictionary lookups. A naive recursive "
            "Fibonacci with the cache does 31 computations for fib(30), "
            "one per value from 0 to 30, instead of over a million. The "
            "limits: arguments must be hashable, the function should "
            "be pure, the default size is 128 entries, and on a method "
            "the cache holds `self` alive, which can leak memory.",
            "How do you clear it, and how do you check it is working?",
        ),
        _q(
            "What is a class decorator, and how is it different from inheritance?",
            "It is a function that receives a class and returns a class, "
            "usually the same one with something added. `@dataclass` is "
            "the standard example: it writes __init__, __repr__ and "
            "__eq__ onto your class without putting a base class in its "
            "hierarchy. Reach for it when you want to add behaviour "
            "without affecting the MRO or isinstance checks, and for "
            "inheritance when you want a real is-a relationship.",
            "When would you use a metaclass instead?",
        ),
        _q(
            "How can an object be used as a decorator?",
            "Any callable works, and an instance becomes callable by "
            "defining __call__. A class that stores the function in "
            "__init__ and calls it from __call__ can keep state between "
            "calls, such as a call counter: `hi.n` after two calls is 2. "
            "The usual catch is methods, because an instance is not a "
            "function and does not bind `self`, so decorating a method "
            "this way needs a __get__ as well.",
            "What would you add so it also works on methods?",
        ),
    ),
)

_ITERATION = Topic(
    id="py-iterators-generators",
    name="Iterators, Generators & Comprehensions",
    order=320,
    languages=_PY,
    blurb="The protocol behind every for loop, and the lazy tools built on it.",
    questions=(
        _q(
            "What is the difference between an iterable and an iterator?",
            "An iterable can produce an iterator: it has __iter__. An "
            "iterator is the thing that does the walking: it has "
            "__next__, and its __iter__ returns itself. A list is "
            "iterable but not an iterator, so `next([1, 2])` is a "
            "TypeError, while `iter([1, 2])` gives a fresh iterator "
            "every time. Iterators are single-pass and remember their "
            "position, which is why a generator can only be used once.",
            "Why does `iter(it) is it` matter for a for loop?",
        ),
        _q(
            "What does a for loop do under the hood?",
            "It calls iter() once on the object, then calls next() on the "
            "result repeatedly, and stops cleanly when StopIteration is "
            "raised. Because it is the same iterator throughout, a loop "
            "picks up where the iterator already is: after one `next(it)`, "
            "`list(it)` on `iter([1, 2, 3])` gives [2, 3]. The same "
            "protocol is what list(), sum(), unpacking and `in` use.",
            "What happens if __next__ raises some other exception?",
        ),
        _q(
            "What does yield from do beyond looping and yielding?",
            "It delegates to a sub-generator: values come straight "
            "through, send() and throw() are forwarded to it, and the "
            "sub-generator's return value becomes the value of the "
            "yield from expression. A manual loop does the first part "
            "but drops the other two. In `v = yield from inner()`, "
            "if inner returns \"r\", then v is \"r\", which is how "
            "pre-async coroutines passed results back.",
            "Where does a generator's return value normally end up?",
        ),
        _q(
            "How does send() work on a generator?",
            "A yield is an expression, and send(value) resumes the "
            "generator with that value as the result of the yield. The "
            "generator has to be started first, with next() or "
            "send(None), so it is sitting at a yield to receive "
            "anything. With `x = yield` followed by `yield x * 2`, "
            "send(21) gives 42. This two-way channel is what "
            "coroutines were built from before async and await.",
            "What does throw() do?",
        ),
        _q(
            "Why can you only iterate a generator once, and how do you get around it?",
            "A generator is its own iterator, and it only moves forward "
            "and then stays exhausted, so `sum(g)` twice on the same "
            "generator gives the total and then 0. To go twice, make "
            "a list, call the generator function again for a fresh "
            "one, or give a class an __iter__ that returns a new "
            "generator each time. itertools.tee works but buffers "
            "everything one side is ahead by.",
            "What is the memory cost of itertools.tee?",
        ),
        _q(
            "Which itertools tools should you know before writing a loop?",
            "chain joins iterables, islice slices any iterator, product "
            "and combinations do the combinatorics, accumulate does "
            "running totals, and groupby groups consecutive equal keys, "
            "so `groupby(\"aabaa\")` yields three groups of sizes 2, 1 "
            "and 2, which is why it needs sorted input to group "
            "everything. pairwise (3.10) gives overlapping pairs and "
            "batched (3.12) gives chunks.",
            "Why did groupby not merge the two runs of a?",
        ),
        _q(
            "When would you write an iterator class instead of a generator?",
            "When it needs more than going forward: a peek method, a "
            "length, a reset, state that others can inspect, or to be "
            "picklable, which generators are not. A class is also "
            "clearer when the object is a reusable collection whose "
            "__iter__ hands out independent iterators. For a single "
            "pass, a generator is a few lines and the class is a "
            "page, so default to the generator.",
            "How would you make a class iterable more than once?",
        ),
        _q(
            "What happens to a generator when the consumer stops early?",
            "close() is called, either explicitly or when the generator is "
            "garbage collected, and it raises GeneratorExit at the "
            "paused yield. A try/finally or a with around that yield "
            "runs, so a file opened inside the generator is closed "
            "even if the loop broke out. After `next(it)` and "
            "`it.close()` on a generator with a finally, the cleanup "
            "message prints right away.",
            "What happens if the generator yields again while handling GeneratorExit?",
        ),
        _q(
            "What are the scoping rules of a comprehension?",
            "It has its own scope, so the loop variable does not leak: "
            "after `[x for x in range(3)]`, referring to x is a "
            "NameError, unlike a for loop, which leaves the variable "
            "behind. PEP 709 made comprehensions inline in 3.12 for "
            "speed but kept that behaviour. The one famous oddity is "
            "a class body, whose names a comprehension inside it "
            "cannot see except in the outermost iterable.",
            "Why can't a comprehension in a class body use a class variable?",
        ),
        _q(
            "How do you read a nested comprehension?",
            "The for clauses are in the same order as the nested "
            "loops you would write by hand, outer first. So "
            "`[x for row in m for x in row]` flattens "
            "[[1, 2], [3, 4]] to [1, 2, 3, 4], and the expression at "
            "the front is the innermost body. Beyond two clauses, or "
            "once there is a side effect, a plain loop is clearer and "
            "nobody will read it twice.",
            "How do you add a filter to only one of the loops?",
        ),
        _q(
            "How do map and filter in Python 3 differ from a list comprehension?",
            "They return lazy iterators, not lists, so nothing runs until "
            "you consume them, and consuming twice gives the results "
            "once and then nothing: `list(m)` a second time is []. "
            "A comprehension builds a list immediately, and a "
            "generator expression is the lazy equivalent. With a "
            "lambda, a comprehension is usually faster and clearer; "
            "with a built-in like str, map is neat.",
            "What does map do when the inputs are different lengths?",
        ),
    ),
)

_DATA_MODEL = Topic(
    id="py-data-model",
    name="Classes & the Data Model",
    order=330,
    languages=_PY,
    blurb="Dunder methods, descriptors, and how Python builds objects.",
    questions=(
        _q(
            "What are dunder methods, and what calls them?",
            "They are the hooks the interpreter calls to implement "
            "syntax and built-ins: len(x) runs type(x).__len__(x), `a + b` "
            "runs __add__, and `with` runs __enter__. The lookup goes "
            "through the type, not the instance, so a __len__ attached "
            "to a single object is ignored: the class's version is "
            "still the one used. You define them to make your objects "
            "behave like built-ins, and rarely call them directly.",
            "Why does the interpreter look them up on the type?",
        ),
        _q(
            "What is the difference between __str__ and __repr__?",
            "__repr__ is for developers: unambiguous, ideally something "
            "you could paste back to recreate the object. __str__ is "
            "for readers and is what print and f-strings use. "
            "Containers always show their items with repr, so a list "
            "of your objects displays using __repr__. If you only "
            "write one, write __repr__, because str falls back to it.",
            "What does an f-string's !r do?",
        ),
        _q(
            "If you define __eq__, what else do you have to think about?",
            "Hashing. A class that defines __eq__ and not __hash__ gets "
            "its __hash__ set to None, making instances unusable as set "
            "members or dictionary keys, because equal objects must "
            "have equal hashes and Python cannot guess how. Write a "
            "__hash__ built from the same fields as __eq__, and only "
            "if they cannot change. Return NotImplemented, not "
            "False, for types you do not understand.",
            "Why does returning NotImplemented rather than False matter?",
        ),
        _q(
            "How do properties work, and why prefer them to getters and setters?",
            "A property is a descriptor on the class that runs a function "
            "when the attribute is read, and optionally another when "
            "it is assigned. Callers use plain attribute syntax, so "
            "you can start with a bare attribute and add validation "
            "or computation later without changing any caller. With "
            "no setter the attribute is read-only, and assigning raises "
            "AttributeError.",
            "Why is a property a data descriptor and what does that change?",
        ),
        _q(
            "What is a descriptor, in brief?",
            "An object with __get__, and optionally __set__ and "
            "__delete__, stored as a class attribute. Python calls "
            "those methods when the attribute is accessed through an "
            "instance, so `C().d` returns 42 if d's __get__ does. It "
            "is the machinery under property, classmethod, "
            "staticmethod, and ordinary methods: a function is a "
            "descriptor whose __get__ binds `self`.",
            "What is the difference between a data and a non-data descriptor?",
        ),
        _q(
            "What is the difference between classmethod, staticmethod and a normal method?",
            "A normal method receives the instance, a classmethod "
            "receives the class, and a staticmethod receives "
            "nothing extra. Because a classmethod gets the class it "
            "was called on, `L.make()` on a subclass L sees L, "
            "which is what makes alternative constructors work with "
            "inheritance. A staticmethod is just a function that "
            "lives in the class for organisation, and is often "
            "better as a module-level function.",
            "Why would an alternative constructor be a classmethod?",
        ),
        _q(
            "What is the difference between __new__ and __init__?",
            "__new__ creates the object and is effectively a static "
            "method that returns it; __init__ then sets it up. "
            "Almost everything only needs __init__. __new__ is for "
            "immutable types like int, str and tuple, whose value is "
            "fixed at creation, for singletons, and for returning "
            "something else entirely. If __new__ returns an object "
            "that is not an instance of the class, __init__ is skipped.",
            "How would you make a subclass of int that is always positive?",
        ),
        _q(
            "What do dataclasses generate, and what are the sharp edges?",
            "From the annotated fields they write __init__, __repr__ "
            "and __eq__, and optionally ordering, a hash, frozen "
            "behaviour and __slots__, giving `P(x=1, y=0)` as the "
            "repr. The edges: a mutable default needs "
            "field(default_factory=...), eq without frozen makes "
            "instances unhashable, and fields are only the annotated "
            "ones. It is a normal class, just with the boilerplate "
            "written for you.",
            "What does __post_init__ add?",
        ),
        _q(
            "What is an abstract base class, and why use one instead of duck typing?",
            "An ABC declares methods subclasses must implement, using "
            "@abstractmethod, and instantiating a subclass that "
            "missed one raises TypeError. It turns a missing method "
            "from a late AttributeError into an early, clear error. "
            "The collections.abc classes also let isinstance ask "
            "about behaviour: `isinstance([], Iterable)` is True and "
            "for an int it is False, with no inheritance involved.",
            "How does a class become a virtual subclass of an ABC?",
        ),
        _q(
            "What is a mixin and how do you use one safely?",
            "A small class that adds one capability and is meant to "
            "be combined with others through multiple inheritance, "
            "such as a logging or serialisation mixin. It should "
            "not need to be instantiated alone or keep much state. "
            "List it before the main base so its methods win in "
            "the MRO, and have it call super() so the chain "
            "continues. Keep mixins few: more than two or three and "
            "the MRO becomes hard to reason about.",
            "Why does a mixin's __init__ usually take **kwargs?",
        ),
        _q(
            "How does Python decide whether an object is true or false?",
            "It calls __bool__ if the class defines it, otherwise "
            "__len__, treating zero as false, and otherwise the "
            "object is true. So a container class with a "
            "__len__ that returns 0 is false: `bool(B())` is False "
            "for a class that only defines __len__ returning 0. "
            "That is why `if items:` works for any collection, and "
            "why `is None` is the check when None is what you mean.",
            "What goes wrong with `if value:` when 0 is a legitimate value?",
        ),
        _q(
            "Why are class attributes shared between instances?",
            "A class attribute lives on the class, and instances only "
            "find it when their own dictionary has no such name. So "
            "a mutable one, like a list, is one object everyone "
            "mutates. Assignment behaves differently: `self.n = 1` "
            "creates an instance attribute that shadows the class's "
            "value, and `self.n += 1` reads the class value and then "
            "assigns an instance one. Put per-instance state in "
            "__init__.",
            "How can you tell from the instance whether an attribute is its own?",
        ),
    ),
)

_EXCEPTIONS = Topic(
    id="py-exceptions-context",
    name="Exceptions & Context Managers",
    order=340,
    languages=_PY,
    blurb="What gets caught, what gets chained, and what always runs.",
    questions=(
        _q(
            "What is the difference between `except Exception` and a bare `except`?",
            "A bare except catches BaseException, which includes "
            "KeyboardInterrupt and SystemExit, so it swallows Ctrl-C "
            "and sys.exit. `except Exception` leaves those alone, "
            "since they derive from BaseException and not from "
            "Exception: `issubclass(KeyboardInterrupt, Exception)` is "
            "False. Asyncio's cancellation is also a BaseException "
            "for the same reason. Catch the narrowest thing you can "
            "actually handle.",
            "Why is swallowing CancelledError a bug in async code?",
        ),
        _q(
            "What do try, except, else and finally each run, and when?",
            "try holds the code that might fail; except runs if it "
            "raised something that matches; else runs only if it "
            "finished without raising; finally runs in every case, "
            "last, including when the function returns or an "
            "exception is propagating. The else exists to keep code "
            "that must not be covered by the except out of the try, "
            "so you do not accidentally catch its errors.",
            "What happens if the finally block itself raises?",
        ),
        _q(
            "What does `raise ... from` do, and what is exception chaining?",
            "When you raise while handling another exception, Python "
            "records the first one in __context__ automatically and "
            "shows both tracebacks. `raise X from y` sets "
            "__cause__ explicitly, to say this error was caused by "
            "that one, and with `from None` the context is "
            "suppressed from the display. In a plain re-raise of a "
            "new error, __cause__ is None but __context__ is set.",
            "When would you use `from None`?",
        ),
        _q(
            "What does a return inside finally do?",
            "It replaces whatever the try was about to return or "
            "raise, so an exception in flight simply vanishes. It "
            "is almost always a mistake and linters flag it. A "
            "related subtlety: the return value is computed before "
            "the finally runs, so `return n` followed by `n = 2` in "
            "the finally still returns 1, though a mutation of a "
            "returned list would be visible.",
            "What happens to the exception if finally does a bare return?",
        ),
        _q(
            "How do you write your own context manager?",
            "Either a class with __enter__ and __exit__, or a generator "
            "decorated with @contextlib.contextmanager that yields "
            "once. The generator form is shorter, with one trap: "
            "code after the yield is skipped if the body raises, "
            "so cleanup has to sit in a try/finally around the "
            "yield. Without it the exit message never prints, and "
            "the exception propagates untouched.",
            "Which form would you choose if the manager needs to be reusable?",
        ),
        _q(
            "What happens when __exit__ returns a true value?",
            "The exception that was raised in the with body is "
            "suppressed, and execution continues after the with "
            "block as if nothing happened. __exit__ receives the "
            "exception type, value and traceback, or three Nones "
            "when all went well, and decides. contextlib.suppress "
            "is exactly that: `with suppress(KeyError): d['x']` "
            "carries on to the next line.",
            "Why should __exit__ usually return None rather than True?",
        ),
        _q(
            "When should you catch an exception and when should you let it propagate?",
            "Catch it where you can do something useful: retry, fall "
            "back, translate it into a more meaningful error, or add "
            "context. Otherwise let it travel up to a place that can "
            "handle or log it. Keep the try body small so you only "
            "catch what you meant to, never catch and silently pass, "
            "and re-raise with a bare `raise` to keep the original "
            "traceback when you only needed to log.",
            "Why is catching and re-raising different from not catching?",
        ),
        _q(
            "What is an ExceptionGroup and what is except* for?",
            "Python 3.11 added a way to raise several unrelated "
            "exceptions at once, used by asyncio's TaskGroup when "
            "more than one task fails. `except*` handles them by "
            "type, and each matching clause gets a group of just "
            "the matching ones, so with a ValueError and a TypeError "
            "inside, both a `except* ValueError` and an "
            "`except* TypeError` run. Plain `except` still works "
            "but sees the group as one exception.",
            "Can you mix except and except* in one try?",
        ),
        _q(
            "How should a library design its own exceptions?",
            "Define one base class for the package, derived from "
            "Exception, and have specific errors inherit from it, so "
            "callers can catch the family or a single member: a "
            "NotFound that derives from AppError is caught by "
            "`except AppError`. Put useful data on the exception "
            "rather than only in a string, name them for the "
            "problem, and don't use them for normal control flow "
            "in the common case.",
            "Should a library raise built-in exceptions like ValueError too?",
        ),
        _q(
            "What happens to the name after `except Exception as e`?",
            "Python deletes it at the end of the except block. "
            "Without that, the exception's traceback would keep "
            "the frame alive and, through the frame, the exception "
            "itself, forming a reference cycle. Deleting the name "
            "also removes any earlier variable called `e`, so "
            "using it afterwards raises NameError. If you need the "
            "exception later, assign it to another name inside "
            "the clause.",
            "How does that interact with exceptions stored in a list?",
        ),
        _q(
            "How do you add context to an exception without losing the traceback?",
            "Use a bare `raise` to re-raise the same exception with its "
            "traceback intact. To add a message, Python 3.11 gives "
            "exceptions add_note, which appends to __notes__ and is "
            "shown in the traceback. To wrap in a different type, "
            "use `raise NewError(...) from e` so the original "
            "stays attached as the cause.",
            "Why not just build a new exception with the old message?",
        ),
    ),
)

_CONCURRENCY = Topic(
    id="py-gil-concurrency",
    name="The GIL, Threads, Processes & Asyncio",
    order=350,
    languages=_PY,
    blurb="What the lock protects, what the alternatives cost, and where 3.13 and 3.14 changed it.",
    questions=(
        _q(
            "Why does the GIL exist, and why hasn't it simply been removed?",
            "CPython's reference counts are plain integers, so "
            "without a lock two threads could corrupt them, and "
            "extension modules were written assuming one thread "
            "at a time. One big lock was the simple, fast, "
            "compatible answer. Removing it costs single-thread "
            "speed and breaks extension assumptions, so it took "
            "PEP 703 and years to make an opt-in free-threaded "
            "build, rather than a switch for everyone.",
            "What did the free-threaded build have to change to be safe?",
        ),
        _q(
            "What is the free-threaded build of Python, and should you use it?",
            "A separate build, introduced as experimental in 3.13 and "
            "officially supported but still optional from 3.14, "
            "in which threads can run Python code in parallel. "
            "Importing an extension not marked as safe turns "
            "the GIL back on, and single-threaded code runs "
            "somewhat slower, around 5 to 10 percent in 3.14's "
            "notes. Worth trying for thread-parallel CPU work; "
            "for most services, processes and asyncio still win "
            "on maturity.",
            "How would you check whether your interpreter has the GIL on?",
        ),
        _q(
            "When do threads help in Python, and when do they not?",
            "They help when threads spend their time waiting: the GIL "
            "is released during blocking I/O and in many C "
            "extensions, so downloads, disk and database calls "
            "overlap well. They do not help CPU-bound pure Python on "
            "the default build, where only one thread runs "
            "bytecode at a time and extra threads add switching "
            "cost. NumPy and hashing often release the GIL, so "
            "they can scale anyway.",
            "Can threads make a CPU-bound program slower?",
        ),
        _q(
            "Is `counter += 1` thread-safe?",
            "No. It compiles to a read, an add and a write as separate "
            "steps, and the interpreter can switch threads between "
            "any of them, so two threads can read the same value and "
            "both write back one more, losing an update. The fix is "
            "a threading.Lock around the update, or a queue, or "
            "giving each thread its own count and combining. With "
            "a lock, four threads doing a thousand increments "
            "each reliably reach 4000.",
            "Does the free-threaded build make this better or worse?",
        ),
        _q(
            "How does multiprocessing get around the GIL, and what does it cost?",
            "Each process is a separate interpreter with its own GIL "
            "and memory, so CPU work spreads across cores. The costs "
            "are start-up time and communication: arguments and "
            "results are pickled and copied between processes, "
            "and shared state needs shared_memory or a manager. "
            "On Windows and macOS processes are spawned, so the "
            "entry point needs an `if __name__ == \"__main__\"` guard "
            "or the children re-run it.",
            "What changed about the default start method in 3.14?",
        ),
        _q(
            "What is the difference between ThreadPoolExecutor and ProcessPoolExecutor?",
            "Same interface, different workers: threads share memory "
            "and suit I/O waits, processes bypass the GIL and suit "
            "CPU work but pay for pickling. `ex.map` returns "
            "results in the order of the inputs, not completion "
            "order, while as_completed gives you them as they "
            "finish. An exception in a worker is stored and "
            "re-raised when you ask the future for its result.",
            "How do you stop a thread pool task that is already running?",
        ),
        _q(
            "What does await actually do?",
            "It suspends the current coroutine and hands control "
            "back to the event loop, which resumes it when the "
            "thing awaited is ready. That is the only place a "
            "switch can happen, so two tasks that each await "
            "between prints interleave, a 0, b 0, a 1, b 1, and a "
            "task that never awaits holds the loop until it "
            "finishes. Cooperative switching makes ordering "
            "predictable, and blocking dangerous.",
            "What does `await asyncio.sleep(0)` do?",
        ),
        _q(
            "How do you call blocking code from async code?",
            "Hand it to a thread so the loop stays free: "
            "`await asyncio.to_thread(func, *args)` (3.9) or "
            "run_in_executor on the loop. It returns the function's "
            "result, `sum([1, 2, 3])` giving 6, without freezing "
            "other tasks. This helps for blocking I/O and for "
            "C code that releases the GIL, but not for CPU-bound "
            "Python, which needs a process pool.",
            "How would you notice that something was blocking the loop?",
        ),
        _q(
            "What is the difference between asyncio.gather and a TaskGroup?",
            "gather runs awaitables together and returns results "
            "in argument order. If one raises, the exception "
            "reaches the caller immediately but the others carry "
            "on unless you cancel them, and "
            "return_exceptions=True puts errors in the list "
            "instead. TaskGroup (3.11) is structured: leaving the "
            "block waits for every task, a failure cancels the "
            "siblings, and errors arrive together in an "
            "ExceptionGroup.",
            "Which would you use for a request that fans out to three services?",
        ),
        _q(
            "Why can a fire-and-forget asyncio task just disappear?",
            "The event loop keeps only weak references to tasks, so "
            "a task nothing else refers to can be garbage collected "
            "while it is still running. Keep a strong reference, "
            "such as a set you add the task to and remove it from in "
            "a done callback, or use a TaskGroup, which holds them "
            "for you. Also remember that a task nobody awaits "
            "hides its exception until it is collected.",
            "Where does an exception from an un-awaited task end up?",
        ),
        _q(
            "How do you cancel an asyncio task, and what must your code do about it?",
            "task.cancel() asks the loop to raise CancelledError inside "
            "the task at its next await. Code should let it "
            "propagate, using finally for cleanup, because "
            "swallowing it makes the task impossible to stop; it "
            "is a BaseException for that reason. Awaiting a "
            "cancelled task raises CancelledError and "
            "`task.cancelled()` is then True. asyncio.timeout "
            "(3.11) builds on this and converts it to TimeoutError.",
            "Where do you catch the TimeoutError from asyncio.timeout?",
        ),
    ),
)

_MEMORY = Topic(
    id="py-memory-performance",
    name="Memory & Performance",
    order=360,
    languages=_PY,
    blurb="Where the time and bytes go in CPython, and how to find out instead of guessing.",
    questions=(
        _q(
            "Why is list.append amortized O(1)?",
            "A list keeps a block of pointers with spare room at the end, "
            "and when it fills, it reallocates a bigger one, growing "
            "by a proportion rather than by one. Most appends just fill "
            "a free slot, and the occasional copy is spread over "
            "many appends. You can see it: the list's size in bytes "
            "changes only a handful of times over a hundred appends, "
            "not on every one.",
            "Why does inserting at the front cost so much more?",
        ),
        _q(
            "When do generators save memory, and when do they not?",
            "A generator holds one frame and one value at a time, so "
            "a pipeline of them uses constant memory however long "
            "the data is: a generator expression over a million "
            "numbers is a few hundred bytes. The saving disappears "
            "the moment something materialises it, such as list(), "
            "sorted() or a second pass that needs the values "
            "again. Use them for streaming, not for data you will "
            "reuse.",
            "Why does sorted() on a generator defeat the point?",
        ),
        _q(
            "How would you profile a slow Python program?",
            "Measure before changing anything. cProfile, run as "
            "`python -m cProfile -s cumtime script.py`, shows which "
            "functions the time goes to; line_profiler narrows it "
            "to lines; a sampling profiler like py-spy attaches "
            "to a live process with little overhead. timeit settles "
            "a micro-benchmark, and tracemalloc covers memory. "
            "Most slow code has one hot function, and it is "
            "rarely the one you suspected.",
            "Why is a sampling profiler better for a production service?",
        ),
        _q(
            "What are the time complexities of the common container operations?",
            "List: index and append are O(1), insert or pop at the "
            "front and `in` are O(n). Dict and set: lookup, insert "
            "and delete are O(1) on average, with a worst case of "
            "O(n) if many keys collide. deque: appends and pops at "
            "both ends are O(1), but indexing the middle is not. "
            "Sorting is O(n log n). Check the TimeComplexity page "
            "rather than trusting memory for the rest.",
            "Why is the worst case of a dict lookup O(n)?",
        ),
        _q(
            "Why is `x in some_list` slow inside a loop, and what is the fix?",
            "Each test scans the list, so a loop of n checks against "
            "n items is quadratic. Build a set once, which costs "
            "O(n), and then every membership test is a hash lookup "
            "on average: `999 in set(range(1000))` is True and "
            "1000 is False, each in constant time. The trade is "
            "memory, the need for hashable items, and losing order "
            "and duplicates.",
            "When is a list still the better choice for membership?",
        ),
        _q(
            "Why are local variables faster to use than globals?",
            "Locals live in a fixed array indexed by position, while "
            "a global or builtin is a dictionary lookup by name. "
            "That is the origin of the old trick of binding "
            "`append = out.append` before a hot loop. The "
            "adaptive interpreter in 3.11 and later narrows the "
            "gap by caching lookups, so the trick matters less "
            "now, and clarity usually beats it unless a profiler "
            "says otherwise.",
            "Why can that trick even make code worse?",
        ),
        _q(
            "What is the specializing adaptive interpreter?",
            "From 3.11 (PEP 659) CPython watches which types flow "
            "through each piece of bytecode as it runs and rewrites "
            "hot instructions into versions specialised for those "
            "types, for example integer addition, falling back if "
            "the types change. It made typical programs about a "
            "quarter faster on average. The practical advice "
            "is that stable, boring types in hot paths now "
            "run measurably faster than ones that vary.",
            "What kind of code does it not help?",
        ),
        _q(
            "Does CPython have a JIT?",
            "Python 3.13 added an experimental one, a copy-and-patch "
            "JIT (PEP 744), but it is off by default and needs a "
            "special build flag, with modest gains so far. "
            "Treat it as something to watch, not something to "
            "plan around. For real speed-ups today the usual "
            "answers are better algorithms, vectorising with "
            "NumPy, a compiled extension, or PyPy where the "
            "dependencies allow.",
            "What would make you choose PyPy?",
        ),
        _q(
            "How would you find a memory leak in a Python service?",
            "Take tracemalloc snapshots a while apart and compare "
            "them to see which lines allocated memory that is still "
            "alive, or use objgraph to see what keeps an object "
            "referenced. The usual causes are an unbounded "
            "cache or module-level list, lru_cache on a method "
            "keeping self alive, callbacks never unregistered, "
            "and closures holding large objects. tracemalloc "
            "will show a list of 100000 items as hundreds of "
            "kilobytes immediately.",
            "Why would memory climb in a long-running process without a true leak?",
        ),
        _q(
            "Why is a list of a million floats much bigger than a NumPy array of them?",
            "Each Python float is a full object, 24 bytes in "
            "CPython on a 64-bit build, and the list adds an "
            "8-byte pointer to each, so around 32 bytes per number. "
            "A NumPy array, or the standard library's "
            "array('d'), stores the raw 8-byte values side by "
            "side, with no per-item object. That also makes it "
            "cache-friendly, which is a large part of why "
            "vectorised code is fast.",
            "What would a list of a million small ints cost?",
        ),
        _q(
            "How can the cyclic garbage collector be tuned or disabled?",
            "The gc module exposes it: gc.disable stops automatic "
            "collections, gc.collect forces one, and "
            "gc.set_threshold changes how often it runs. "
            "gc.freeze moves existing objects out of "
            "consideration, which suits a web server that forks "
            "workers, since it avoids copy-on-write pages being "
            "dirtied by the collector. Only disable it if you "
            "are certain there are no cycles; the details of "
            "generations changed between recent releases.",
            "Why does freezing before a fork reduce memory use?",
        ),
    ),
)

_TYPING = Topic(
    id="py-typing",
    name="Types & Typing",
    order=370,
    languages=_PY,
    blurb="Hints that nobody enforces at run time, and the tools that do.",
    questions=(
        _q(
            "Are Python type hints enforced?",
            "Not by the interpreter. Annotations are stored on the "
            "function and otherwise ignored, so passing strings to "
            "a function annotated as taking ints runs fine and "
            "`add(\"x\", \"y\")` gives \"xy\". They are for readers "
            "and tools: mypy and pyright check them statically, "
            "and libraries such as pydantic, dataclasses and "
            "FastAPI read them at run time to do real work.",
            "Which tools do enforce types at run time?",
        ),
        _q(
            "What does Optional[int] mean?",
            "It is shorthand for `int | None`, a value that may be "
            "None, and says nothing about whether the argument "
            "can be left out. A parameter with a default does "
            "not need Optional, and one that defaults to None "
            "does. The two are the same type at run time: "
            "`Optional[int]` equals `int | None`, and the pipe "
            "syntax works from 3.10.",
            "What would make a checker complain about `x.upper()` on an Optional[str]?",
        ),
        _q(
            "What is the difference between a Protocol and an abstract base class?",
            "An ABC is nominal: a class has to inherit from it. A "
            "Protocol is structural: any class with the right "
            "methods matches, with no inheritance, which is "
            "duck typing that a static checker can verify. At "
            "run time, a Protocol marked runtime_checkable "
            "supports isinstance, but only checks that the "
            "names exist, not their signatures.",
            "When would you still choose an ABC?",
        ),
        _q(
            "When do you need generics and TypeVar?",
            "When the type of the output depends on the type of the "
            "input, such as a first() that returns whatever the "
            "sequence holds. A TypeVar links the two so the "
            "checker knows `first([1, 2])` is an int. From 3.12 "
            "you write it inline, `def first[T](xs: "
            "Sequence[T]) -> T`. Builtins like list[int] are "
            "subscriptable since 3.9, but not usable with "
            "isinstance.",
            "Why does isinstance([], list[int]) raise an error?",
        ),
        _q(
            "What is the difference between Any and object?",
            "Any switches checking off: it is compatible with "
            "everything in both directions, so errors pass "
            "silently. object means every value is accepted, but "
            "the checker then refuses operations that are not on "
            "object, so you have to narrow with isinstance first. "
            "Use object when you truly accept anything and "
            "Any as a deliberate, visible escape hatch.",
            "Why is Any contagious through a codebase?",
        ),
        _q(
            "When would you choose NamedTuple, TypedDict or a dataclass?",
            "NamedTuple is an immutable, tuple-like record you can "
            "unpack and index: `P(1, 2)` prints P(x=1, y=2), "
            "and `_replace` makes a modified copy. A dataclass is "
            "a mutable class with behaviour and defaults. "
            "TypedDict describes the keys of a dict for "
            "the checker only: at run time it is an ordinary "
            "dict, which suits JSON-shaped data.",
            "Which one would you use for rows decoded from JSON?",
        ),
        _q(
            "What does `from __future__ import annotations` do, and what changed in 3.14?",
            "It stops annotations being evaluated, keeping them as "
            "strings, so forward references need no quotes: "
            "`f.__annotations__` shows {'x': 'Undefined'} for "
            "an undefined name. Python 3.14 (PEP 649 and 749) made "
            "deferred evaluation the default without the "
            "import, computing annotations when first asked, "
            "with the annotationlib module to inspect them "
            "in different formats.",
            "Why does a library that reads annotations care?",
        ),
        _q(
            "How would you adopt type hints in an untyped codebase?",
            "Gradually. Start with public function signatures and "
            "module boundaries, turn on a checker in CI with a "
            "lenient config, and make new or fully annotated "
            "modules strict one at a time. Use `# type: "
            "ignore[code]` sparingly with a reason, install stub "
            "packages for untyped dependencies, and track the "
            "Any count. The aim is catching real bugs, not "
            "a number.",
            "How do you stop Any creeping back in?",
        ),
        _q(
            "What do typing.cast and TYPE_CHECKING do at run time?",
            "cast does nothing: it returns its argument "
            "unchanged and exists only to tell the checker what "
            "to believe, so `cast(int, \"x\")` returns \"x\". "
            "TYPE_CHECKING is False when the program runs and "
            "True for the checker, which makes it the guard for "
            "imports needed only in annotations, a common cure "
            "for circular imports. Both are promises you make, "
            "not checks.",
            "What can go wrong when a cast is wrong?",
        ),
        _q(
            "What is ClassVar for, and how does it interact with dataclasses?",
            "ClassVar marks an annotated name as a class attribute "
            "rather than per-instance state. Dataclass skips such "
            "names when building fields, so `n: ClassVar[int] = 0` "
            "does not appear in __init__ or the repr: "
            "`A(1)` prints A(x=1). Without it, an annotated "
            "attribute with a value becomes a field with a "
            "default, which surprises people.",
            "How does Final differ from ClassVar?",
        ),
    ),
)

_STRUCTURES = Topic(
    id="py-data-structures",
    name="Data Structures in Practice",
    order=380,
    languages=_PY,
    blurb="The built-ins and the standard-library containers worth reaching for.",
    questions=(
        _q(
            "Is a dict ordered, and since when is that guaranteed?",
            "It keeps insertion order. That began as a CPython 3.6 "
            "implementation detail and became a language guarantee "
            "in 3.7. Reinserting a deleted key puts it at the end. "
            "Dict equality ignores order, so `{'a': 1, 'b': 2}` "
            "equals the same pairs reversed, while "
            "collections.OrderedDict compares order too and "
            "reports them unequal.",
            "What does OrderedDict still offer that dict does not?",
        ),
        _q(
            "What makes an object hashable?",
            "A __hash__ that never changes for the object's life and "
            "agrees with __eq__, so equal objects hash equally. "
            "The immutable built-ins qualify, a tuple does if "
            "its items do, and frozenset exists so a set-like "
            "thing can be a key: `hash((1, 2))` is stable, and "
            "so is a frozenset's regardless of the order it "
            "was built in. Lists, dicts and sets are not.",
            "What goes wrong if you mutate an object after using it as a key?",
        ),
        _q(
            "How does a dict find a key, and what happens on a collision?",
            "It hashes the key to pick a starting slot in an array, "
            "and on a hit compares identity first and equality "
            "second; on a mismatch it probes other slots in a "
            "deterministic sequence. That identity check has a "
            "consequence for NaN: a stored `nan` is found "
            "with the same object but a fresh NaN is not, because "
            "nan != nan. The table is resized well before it "
            "fills.",
            "Why does the identity shortcut exist?",
        ),
        _q(
            "When would you use collections.deque instead of a list?",
            "When you add or remove at both ends: appendleft and "
            "popleft are O(1), while list.pop(0) shifts every "
            "element. With maxlen it becomes a sliding window "
            "that discards the oldest item: a deque with "
            "maxlen=2 that has seen 1, 2, 3 holds 2 and 3. The "
            "price is that indexing near the middle is "
            "O(n), so it is not a drop-in list.",
            "Why is a list a poor queue?",
        ),
        _q(
            "How do you use heapq, and how do you get a max-heap or a top-k?",
            "heapq treats a plain list as a min-heap: heapify is "
            "O(n), push and pop are O(log n), and index 0 is "
            "always the smallest. For a max-heap, push negated "
            "values; for top-k, nlargest does it without sorting "
            "everything. With tuples as `(priority, item)`, "
            "equal priorities compare the items next, which can "
            "raise TypeError, so add a counter as a tie-break.",
            "Why does a tie in priority sometimes raise a TypeError?",
        ),
        _q(
            "What does bisect give you?",
            "Binary search on a sorted list: bisect_left returns the "
            "position before any equal items and bisect_right the "
            "position after, so on [1, 2, 2, 3] they give 1 and 3 "
            "for the value 2, and their difference counts the "
            "copies. insort inserts while keeping order. Search "
            "is O(log n), but inserting into a list is still "
            "O(n), and since 3.10 both accept a key function.",
            "How would you use bisect for a range lookup table?",
        ),
        _q(
            "What does Counter do beyond counting?",
            "It is a dict of counts with extras: most_common(n), "
            "arithmetic between counters with + and -, and "
            "missing keys reading as 0 rather than raising. "
            "`Counter(\"hello\").most_common(1)` gives "
            "[('l', 2)]. Ties keep the order the keys were first "
            "seen. It is the natural first tool for frequency "
            "questions and anagram checks.",
            "How do you check whether one word is an anagram of another with it?",
        ),
        _q(
            "When do you use defaultdict, setdefault or get?",
            "defaultdict calls a factory when a missing key is "
            "indexed and stores the result, so a plain read "
            "grows the dict. setdefault does the same for one "
            "call but builds its default every time, even when "
            "unused. get returns a default without storing "
            "anything. A read such as `d['x']` on "
            "defaultdict(int) leaves {'x': 0} behind, which is "
            "convenient and also easy to trigger by accident.",
            "How do you stop a defaultdict creating keys on a lookup?",
        ),
        _q(
            "What are sets good for, and what do the operators mean?",
            "Fast membership, deduplication and comparison of "
            "collections: `&` is intersection, `|` union, `-` "
            "difference and `^` the items in exactly one. So "
            "`{1, 2, 3} & {2, 3, 4}` is {2, 3} and the `^` of "
            "the same pair is {1, 4}. Sets are unordered and "
            "hold only hashable items, and intersection costs "
            "about the size of the smaller one.",
            "How do you deduplicate a list while keeping its order?",
        ),
        _q(
            "Why does dict.fromkeys(keys, []) bite?",
            "The default value is one object, so every key refers "
            "to the same list, and appending through one key "
            "shows up under all of them: "
            "`dict.fromkeys('ab', [])` followed by an append to "
            "'a' gives {'a': [1], 'b': [1]}. Use a "
            "comprehension, `{k: [] for k in keys}`, to get "
            "separate lists. fromkeys is perfect with an "
            "immutable value like None or 0.",
            "How can dict.fromkeys deduplicate in order?",
        ),
        _q(
            "How do you choose between namedtuple, dataclass and a plain dict?",
            "namedtuple is lightweight and immutable, and unpacks "
            "like a tuple: `x, y = p` works and the repr is "
            "`P(x=1, y=2)`. A dataclass is mutable, can have "
            "methods and defaults, and is the better default "
            "for a record with behaviour. A dict suits "
            "data whose keys are not known up front. Validation "
            "on input is a job for something like pydantic, "
            "not any of these.",
            "What would make you pick a frozen dataclass over a namedtuple?",
        ),
        _q(
            "How do you sort by more than one key, and why does stability help?",
            "Give key a tuple, `key=lambda r: (r.team, -r.score)`, "
            "or sort twice, least significant key first, "
            "relying on the sort being stable: items that "
            "compare equal keep their earlier order, even "
            "with reverse=True, so a reversed sort of lengths "
            "still lists bb before cc if bb came first. "
            "operator.itemgetter and attrgetter are the "
            "faster spelling of the key.",
            "How would you sort descending on one key and ascending on another?",
        ),
    ),
)

_PACKAGING = Topic(
    id="py-packaging-imports",
    name="Packaging, Environments & Imports",
    order=390,
    languages=_PY,
    blurb="How code gets found, installed and isolated.",
    questions=(
        _q(
            "What is a virtual environment and what does it isolate?",
            "A directory with its own site-packages and a link to a "
            "base interpreter, described by a pyvenv.cfg file. "
            "Activating it just puts its bin directory first on "
            "PATH. It isolates installed packages between "
            "projects, not the Python version itself and not "
            "system libraries or tools. Create one per project "
            "with `python -m venv`, never install project "
            "dependencies into the system Python.",
            "How can code tell it is running inside one?",
        ),
        _q(
            "What does pip install do, and what is a wheel?",
            "It resolves the dependency tree, downloads each "
            "distribution, and installs it into the active "
            "environment. A wheel is a prebuilt zip with the "
            "files in their install layout plus metadata, so "
            "installing is a copy, while a source distribution "
            "must be built first through the project's "
            "build backend. Compiled packages ship wheels for "
            "each platform, which is why a missing wheel "
            "suddenly needs a compiler.",
            "What does `pip install -e .` do differently?",
        ),
        _q(
            "What goes in pyproject.toml?",
            "The standard configuration file. A [build-system] "
            "table says what builds the project, a [project] "
            "table holds the name, version, dependencies and "
            "entry-point scripts, and [tool.*] tables hold "
            "settings for tools like ruff or pytest. It "
            "largely replaces setup.py and setup.cfg. It is "
            "TOML, which the standard library reads with "
            "tomllib since 3.11.",
            "What does the build backend do?",
        ),
        _q(
            "What is the difference between requirements.txt, pyproject dependencies and a lock file?",
            "pyproject dependencies state what the project "
            "needs, usually as ranges. A lock file records "
            "the exact resolved versions, with hashes, so "
            "every install is the same. A pinned "
            "requirements.txt is a poor man's lock file. "
            "Libraries should keep ranges loose so others can "
            "resolve them, and applications should lock. "
            "Tools such as pip-tools, Poetry and uv generate "
            "the lock.",
            "Why shouldn't a library pin exact versions?",
        ),
        _q(
            "What happens when you write `import x`?",
            "Python first checks sys.modules, a cache of modules "
            "already imported, and returns the entry if there "
            "is one. Otherwise it asks the finders on "
            "sys.meta_path, which search sys.path, and the "
            "loader runs the module's code once, storing the "
            "result in sys.modules and binding the name. "
            "That is why a second import is nearly free, and "
            "why `import json as j2` gives you the very same "
            "module object.",
            "How would you force a module to be re-imported?",
        ),
        _q(
            "What is a circular import and how do you fix one?",
            "Module a imports b while b imports a, so one of them "
            "is used while only half-executed. `from a import "
            "name` then fails with an ImportError saying it is "
            "probably a circular import. Fixes, best first: "
            "move the shared code to a third module, import "
            "the module and use `a.name` at call time, import "
            "inside the function that needs it, or guard "
            "annotation-only imports with TYPE_CHECKING.",
            "Why does `import a` survive a cycle when `from a import x` does not?",
        ),
        _q(
            "What does `if __name__ == \"__main__\":` do?",
            "__name__ is the string \"__main__\" in the file "
            "Python was started on, and the module's own name "
            "when it is imported. So the guarded block runs "
            "when you execute the file and not when someone "
            "imports it, which lets one file be both a "
            "library and a script. It is also required with "
            "multiprocessing's spawn start method, where "
            "children import the main module.",
            "What does `python -m package` run?",
        ),
        _q(
            "How does Python decide where to find modules, and what is sys.path?",
            "sys.path is a list of directories searched in order: "
            "the script's directory first, then PYTHONPATH "
            "entries, the standard library and site-packages. "
            "The first match wins, so a file in your project "
            "named random.py or json.py shadows the real "
            "module and breaks things in confusing ways. "
            "Name your files so they cannot collide with the "
            "standard library.",
            "What does `python -I` change about this?",
        ),
        _q(
            "What is __init__.py for, and what are namespace packages?",
            "A directory with an __init__.py is a regular "
            "package, and that file runs when the package is "
            "first imported, so it can re-export a clean "
            "public API. Since 3.3, a directory without one "
            "can still be imported as a namespace package "
            "(PEP 420), which may be spread across several "
            "directories and is how plugins from separate "
            "distributions can share a prefix. Use "
            "__init__.py unless you need that.",
            "How can a missing __init__.py confuse a test runner?",
        ),
        _q(
            "Absolute or relative imports: which do you use?",
            "Absolute by default, as PEP 8 advises, because "
            "they read the same from anywhere. Relative "
            "imports, `from . import x`, are fine inside a "
            "package but fail when that file is run directly "
            "as a script, with an ImportError saying there "
            "is no known parent package. Run package code "
            "with `python -m package.module`, which "
            "gives it the context it needs.",
            "Why does a relative import fail when you run the file directly?",
        ),
        _q(
            "What is an entry point or console script?",
            "A declaration in pyproject.toml, under "
            "[project.scripts], that maps a command name to a "
            "function, as `name = \"package.module:main\"`. At "
            "install time pip generates a small executable "
            "that imports the module and calls the function, "
            "which works on every platform. It is how "
            "command-line tools such as pytest and black "
            "get their commands. `python -m` is the "
            "no-install equivalent.",
            "How does pipx use that to isolate command-line tools?",
        ),
    ),
)

_TESTING = Topic(
    id="py-testing",
    name="Testing",
    order=400,
    languages=_PY,
    blurb="Fixtures, mocks and the decisions about what to fake.",
    questions=(
        _q(
            "What is a pytest fixture, and how does scope work?",
            "A fixture is a function that supplies a test with "
            "something it needs, by naming it as a parameter. "
            "The default scope is function, so each test gets "
            "a fresh one, and wider scopes, class, module, "
            "package or session, build it once and share it. "
            "A fixture can only depend on fixtures of the same "
            "or wider scope. Code after a yield is the "
            "teardown, and conftest.py shares fixtures "
            "across files.",
            "What is the risk of widening a fixture's scope?",
        ),
        _q(
            "Why use parametrize instead of a loop inside a test?",
            "Each parameter set becomes its own test with its own "
            "id, so a failure names the case that broke and "
            "the rest still run. A loop stops at the first "
            "failure and reports one anonymous test. It also "
            "puts the cases in a table, which makes missing "
            "edge cases visible, and `indirect=True` can "
            "feed the values through a fixture instead.",
            "How do you give the cases readable ids?",
        ),
        _q(
            "What is the difference between a mock, a stub, a fake and a spy?",
            "A stub returns canned answers. A fake is a working "
            "lightweight version, such as an in-memory "
            "database. A mock also records how it was called so "
            "you can assert on it, and a spy wraps the real "
            "thing and records. In unittest.mock one object "
            "plays most roles: `Mock(return_value=3)` "
            "returns 3 and remembers `call(1)` for the call "
            "made with 1.",
            "When is a fake better than a mock?",
        ),
        _q(
            "Where do you patch with unittest.mock.patch?",
            "Where the name is looked up, not where it is "
            "defined. If orders.py does `from payments import "
            "charge`, it holds its own reference, so the "
            "target is `orders.charge`, and patching "
            "`payments.charge` changes nothing there. Inside "
            "the context the patched object is what the code "
            "sees: with os.path.exists patched to return "
            "True, any path appears to exist.",
            "Why does patching the defining module often fail silently?",
        ),
        _q(
            "What does autospec buy you?",
            "A mock that copies the real object's signature and "
            "attributes, so calling it with the wrong "
            "arguments raises TypeError and asking for a "
            "name that does not exist raises AttributeError. "
            "A plain Mock accepts anything, so tests stay "
            "green after the real function changes. "
            "create_autospec or patch(..., autospec=True) "
            "keeps the mock honest.",
            "What does a plain Mock fail to catch?",
        ),
        _q(
            "What should you not mock?",
            "The code under test, for a start. Beyond that, "
            "mock at the edges you do not control, the "
            "network, the clock, the filesystem, and prefer "
            "real or in-memory fakes for things you own. "
            "Mocking your own internals ties the test to "
            "how the code works rather than what it does, so "
            "every refactor breaks tests. If a test is mostly "
            "setup of mocks, it is probably checking nothing.",
            "How do you test code that wraps a third-party client?",
        ),
        _q(
            "How do you test Python code that depends on the clock or on randomness?",
            "Inject the dependency rather than reaching for it: "
            "pass in a clock function or a random.Random "
            "instance, so the test supplies a fixed one. "
            "Seeding makes randomness repeatable: two "
            "generators built with the same seed produce the "
            "same numbers. Otherwise patch the call, or use a "
            "library such as freezegun for time. Avoid "
            "sleeping in tests.",
            "Why is a seeded Random instance better than seeding the global one?",
        ),
        _q(
            "What are unit, integration and end-to-end tests, and how should they be balanced?",
            "A unit test checks one piece in isolation and is "
            "fast; an integration test checks several "
            "pieces working together, such as code and a real "
            "database; an end-to-end test drives the whole "
            "system from outside. The pyramid advice is many "
            "unit tests, fewer integration, very few "
            "end-to-end, since the slow ones are costly and "
            "flaky. It depends on the system: a thin "
            "service may want more integration tests.",
            "Which tests would you run on every commit?",
        ),
        _q(
            "How does pytest make a plain assert useful?",
            "It rewrites the assert statements in test modules "
            "as they are imported, so a failure shows the "
            "values of both sides and a diff, without "
            "assertEqual-style methods. The assert in your "
            "application code is different: it raises "
            "AssertionError with only your message, and "
            "python -O removes assert statements entirely, "
            "so never use them for validating input.",
            "Why is `assert` wrong for argument validation?",
        ),
        _q(
            "What does test coverage tell you, and what doesn't it?",
            "It tells you which lines, or with branch coverage "
            "which decisions, ran during the tests. It does "
            "not tell you the behaviour was checked: a "
            "test that calls a function and asserts nothing "
            "gives full coverage. It is best used to find "
            "code nobody tests rather than as a target. "
            "Mutation testing, which changes the code and "
            "sees whether tests notice, measures more.",
            "Why can chasing 100 percent make tests worse?",
        ),
        _q(
            "How do you test async code?",
            "You need something to run the event loop: "
            "pytest-asyncio or anyio for pytest, "
            "unittest.IsolatedAsyncioTestCase for unittest, or "
            "a plain asyncio.run inside a sync test. For "
            "collaborators use AsyncMock, whose call returns "
            "an awaitable: `asyncio.run(m())` returns "
            "whatever return_value was set. Test "
            "timeouts and cancellation explicitly, since "
            "those are where async bugs hide.",
            "How would you test that a task was cancelled cleanly?",
        ),
    ),
)

_WEB = Topic(
    id="py-web-apis",
    name="Web & APIs in Python",
    order=410,
    languages=_PY,
    blurb="WSGI, ASGI, the frameworks, and what a service needs to survive production.",
    questions=(
        _q(
            "What is the difference between WSGI and ASGI?",
            "WSGI is the original synchronous interface: the "
            "server calls one function per request and gets "
            "the response back, so one request ties up a "
            "worker. ASGI is the asynchronous successor, a "
            "callable that takes scope, receive and send, "
            "sending messages such as http.response.start "
            "and http.response.body. That shape allows "
            "WebSockets and long-lived connections. "
            "Gunicorn is typical for WSGI and Uvicorn for ASGI.",
            "Why can't a WSGI app do WebSockets cleanly?",
        ),
        _q(
            "How would you choose between Flask, FastAPI and Django?",
            "It depends on what you are building. Django is "
            "batteries-included, with an ORM, migrations, "
            "admin and auth, and suits database-heavy "
            "sites. Flask is a small WSGI core where you pick "
            "the rest, good for small services. FastAPI is "
            "ASGI on Starlette, using type hints and "
            "pydantic for validation and OpenAPI docs, and "
            "suits typed APIs. Team knowledge counts as "
            "much as any of that.",
            "What would make you move off Flask?",
        ),
        _q(
            "Does using async make a web endpoint faster?",
            "Only in throughput, and only when requests spend "
            "time waiting on I/O. One request is not "
            "quicker; the server handles more at once because "
            "a waiting request does not hold a thread. "
            "Anything blocking inside an async def, like "
            "a synchronous database driver, stalls the "
            "whole loop. FastAPI runs plain def "
            "endpoints in a thread pool for this reason.",
            "What happens to a plain `def` endpoint in FastAPI?",
        ),
        _q(
            "What does pydantic validation do, and why is it popular with FastAPI?",
            "It parses input into typed models using the "
            "annotations, coercing where it can in its default "
            "mode, so id=\"123\" becomes the int 123, and "
            "raises a ValidationError listing every field "
            "that failed. The same models produce a JSON "
            "schema, which FastAPI turns into OpenAPI docs. "
            "Strict mode refuses coercion. Validation "
            "happens at the boundary, so the rest of the code "
            "can trust the types.",
            "Does pydantic check a value when you assign to an attribute later?",
        ),
        _q(
            "How do requests, httpx and aiohttp differ?",
            "requests is synchronous and has no default "
            "timeout, so a stalled server can hang your "
            "program forever unless you pass timeout=. "
            "httpx offers a similar API with both sync and "
            "async clients, optional HTTP/2, and a default "
            "timeout of five seconds. aiohttp is async-first "
            "and also a server framework. Always set "
            "explicit timeouts, and reuse a session or client "
            "for connection pooling.",
            "Why reuse a client instead of calling get each time?",
        ),
        _q(
            "What does it mean for an HTTP method to be idempotent?",
            "Repeating the request has the same effect as doing "
            "it once. GET, HEAD, PUT and DELETE are meant "
            "to be; POST is not, so retrying a POST after "
            "a timeout may create two orders. That is "
            "why payment-style APIs accept an "
            "idempotency key, letting the server recognise "
            "a retry. Retry logic has to know which calls "
            "are safe to repeat.",
            "How would you implement an idempotency key?",
        ),
        _q(
            "How should a Python API handle errors and status codes?",
            "Raise domain exceptions in the business code and "
            "translate them to HTTP at the edge with "
            "exception handlers, so the logic does not "
            "know about status codes. 4xx means the client "
            "can fix the request, 5xx means the server "
            "failed, and the body should have a consistent "
            "shape. Log the detail but never return "
            "stack traces or internals to the caller.",
            "What belongs in the logs but not the response?",
        ),
        _q(
            "Why shouldn't a database session be shared across requests?",
            "A session tracks one unit of work: its "
            "identity map, pending changes and "
            "transaction. Sharing it between concurrent "
            "requests mixes their changes and, in "
            "SQLAlchemy, it is not thread-safe. Create "
            "one per request, usually through a "
            "dependency that commits or rolls back and "
            "closes it, and let the connection pool "
            "do the sharing underneath.",
            "What should happen to the session when the request fails?",
        ),
        _q(
            "What is the N+1 query problem?",
            "Loading a list with one query and then touching a "
            "related object on each row, which triggers "
            "one more query per row, so 100 rows cost 101 "
            "round trips. It hides in ORMs because "
            "attribute access looks free. Fix it by "
            "fetching the relation up front: select_related "
            "or prefetch_related in Django, joinedload or "
            "selectinload in SQLAlchemy.",
            "How would you notice it in a running app?",
        ),
        _q(
            "How do you run a Python web app in production?",
            "Behind a real server and usually a reverse proxy, "
            "not the development server: Gunicorn with "
            "several worker processes for WSGI, Uvicorn "
            "workers for ASGI, nginx or a load balancer "
            "in front. Multiple worker processes use "
            "multiple cores despite the GIL, at the cost "
            "of separate memory. Add health checks, "
            "graceful shutdown and logging to stdout, "
            "and keep configuration outside the code.",
            "How many workers would you start with?",
        ),
        _q(
            "How should secrets and configuration reach a Python service?",
            "Through the environment, not the source code: "
            "`os.environ.get(\"NAME\", \"fallback\")` for "
            "optional settings, and a KeyError on "
            "os.environ[\"NAME\"] when a missing one should stop "
            "start-up. Load a .env file only in "
            "development, parse settings once into a typed "
            "object, as pydantic-settings does, and "
            "keep secrets out of git and logs.",
            "Why is failing at start-up better than failing on first use?",
        ),
        _q(
            "When is a task queue like Celery the right answer?",
            "When work must outlive the request, such as sending "
            "email, processing uploads or scheduled jobs. "
            "A broker holds the tasks and separate workers "
            "run them, with retries and results. An "
            "in-process background task dies with the "
            "process and is lost on deploy. Tasks should "
            "be idempotent, since at-least-once delivery means "
            "one can run twice. RQ, Dramatiq and arq are "
            "lighter options.",
            "What makes a task safe to retry?",
        ),
    ),
)

_NUMERICS = Topic(
    id="py-data-numerics",
    name="Data & Numerics",
    order=420,
    languages=_PY,
    blurb="Python's number types, and the habits the data libraries expect.",
    questions=(
        _q(
            "Why can a Python int be as large as you like, and what does it cost?",
            "It is stored as a variable-length array of digits, so "
            "it grows as needed and `2 ** 100` is simply "
            "1267650600228229401496703205376 with no overflow. "
            "The cost is memory and speed against a machine "
            "integer. NumPy's fixed-width integers do wrap "
            "silently. Since 3.11 converting a huge int to "
            "or from a string is capped, by default at 4300 "
            "digits, to block a denial-of-service.",
            "What happens when you convert a 5000-digit string with int()?",
        ),
        _q(
            "When do you use Decimal or Fraction instead of float?",
            "Decimal for money and anywhere decimal places are the "
            "spec: `Decimal(\"0.1\") + Decimal(\"0.2\")` is exactly 0.3, "
            "with a configurable precision and rounding mode. "
            "Fraction for exact rational arithmetic, where "
            "1/3 plus 1/6 is exactly 1/2. Both are far slower "
            "than float. Build a Decimal from a string, since "
            "Decimal(0.1) faithfully captures the float's error.",
            "Why does Decimal(0.1) not equal Decimal('0.1')?",
        ),
        _q(
            "How should you compare floats in Python?",
            "With math.isclose, which uses a relative tolerance of "
            "1e-9 by default, so `0.1 + 0.2` is close to 0.3. "
            "The relative tolerance means nothing near zero, "
            "so comparing 1e-10 to 0 is False unless you "
            "pass abs_tol. Pick tolerances from the "
            "problem, not by habit, and use Decimal or integer "
            "units for money.",
            "Why is a relative tolerance alone not enough?",
        ),
        _q(
            "What does vectorisation mean in NumPy, and why is it faster?",
            "An operation on a whole array runs as one loop "
            "inside compiled code, over contiguous, "
            "uniformly typed memory, instead of the "
            "interpreter doing one bytecode dispatch, one "
            "type check and one boxed object per element. "
            "That removes most of the overhead and lets the "
            "CPU use SIMD and the cache well. The habit is "
            "to express work on whole arrays and keep "
            "Python-level loops out of the hot path.",
            "When is a Python loop over a NumPy array still fine?",
        ),
        _q(
            "What is broadcasting?",
            "NumPy's rule for combining arrays of different "
            "shapes: line the shapes up from the right, and "
            "each pair of dimensions must be equal or one "
            "of them 1, in which case that dimension is "
            "stretched, without copying data. A column of "
            "shape (3, 1) plus a row of shape (4,) gives a "
            "(3, 4) result. Write down the shapes before "
            "the operation, since most NumPy bugs are "
            "shape bugs.",
            "What shape error do you get when the dimensions do not match?",
        ),
        _q(
            "What is the difference between a view and a copy in NumPy?",
            "A view shares memory with the original, so writing "
            "through it changes both, while a copy is "
            "independent. Basic slicing returns a view, so "
            "`a[1:3]` shares data with a, while fancy "
            "indexing with a list or a boolean mask returns "
            "a copy. reshape and ravel may return either, "
            "depending on layout, and .copy() is how you "
            "make sure.",
            "How can you check whether two arrays share memory?",
        ),
        _q(
            "Why did pandas warn about SettingWithCopy, and what changed in pandas 3?",
            "Chained indexing like `df[mask][\"col\"] = v` may be "
            "writing to a temporary copy, and pandas could not "
            "tell, so it warned. Pandas 3.0 made "
            "copy-on-write the only mode: every subset "
            "behaves as a copy, chained assignment never "
            "updates the original, and the warning is gone. "
            "The correct form is a single step, "
            "`df.loc[mask, \"col\"] = v`, which works in "
            "every version.",
            "Why were defensive .copy() calls common before?",
        ),
        _q(
            "When is iterating over DataFrame rows a smell, and what do you do instead?",
            "iterrows and a Python loop do per-row work in the "
            "interpreter, which is often orders of magnitude "
            "slower than the whole-column equivalent. Prefer "
            "vectorised column arithmetic, np.where for "
            "conditions, the .str and .dt accessors, merge "
            "and groupby aggregations. apply is a convenient "
            "loop but still a loop. Row iteration is "
            "acceptable for small data or side effects.",
            "How would you replace an if/else in a loop with np.where?",
        ),
        _q(
            "How does NaN behave in Python?",
            "It is not equal to anything, including itself: "
            "for `nan = float(\"nan\")`, `nan == nan` is False, "
            "`nan != nan` is True, and the reliable "
            "test is math.isnan. That has side effects "
            "in sets and sorting. In pandas, missing values "
            "are skipped by most aggregations by default, "
            "and nullable dtypes use pd.NA, which "
            "propagates through logic instead.",
            "Why can a NaN appear twice in a set?",
        ),
        _q(
            "Why does round(2.675, 2) give 2.67, and what should you do for money?",
            "The float nearest to 2.675 is very slightly less "
            "than 2.675, so rounding to two places "
            "correctly gives 2.67. Ties that are exactly "
            "representable round to even, in the same "
            "way. For money, hold Decimals and round "
            "explicitly: quantizing `Decimal(\"2.675\")` to "
            "two places with ROUND_HALF_UP gives 2.68, the "
            "rule most people mean.",
            "Why does banker's rounding exist at all?",
        ),
        _q(
            "How do // and % behave with negative numbers?",
            "// floors, rounding toward negative infinity, and % "
            "takes the sign of the divisor, so that "
            "`(a // b) * b + a % b == a` always holds. "
            "`-7 // 2` is -4, `-7 % 2` is 1 and "
            "`divmod(-7, 2)` returns (-4, 1). C and "
            "JavaScript truncate toward zero, which is "
            "where translated code goes wrong. Use "
            "math.fmod when you want the truncating "
            "behaviour.",
            "What do 7 // -2 and 7 % -2 give?",
        ),
        _q(
            "How do you read a CSV too big to fit in memory?",
            "Stream it. The csv module reads a row at a time, "
            "`next(rows)` returning the header and then "
            "each record, so memory stays flat. In pandas, "
            "pass chunksize to get an iterator of "
            "DataFrames, select only the columns you need "
            "with usecols, and give dtypes explicitly. If "
            "you will read it often, convert once to a "
            "columnar format such as Parquet.",
            "Why does specifying dtypes save memory?",
        ),
    ),
)

_TRICKY = Topic(
    id="py-tricky-outputs",
    name="Python Tricky Outputs",
    order=430,
    languages=_PY,
    blurb="The \"what does this print\" questions, each with the answer and the reason.",
    questions=(
        _q(
            "What do `[] == False`, `not []` and `bool([])` give?",
            "False, True, False. An empty list is falsy, so "
            "`not []` is True and `bool([])` is False, but "
            "that does not make it equal to False: `==` "
            "compares values, and a list and a bool are "
            "never equal. Truthiness is a separate test "
            "from equality, which is why `if x == False` "
            "and `if not x` behave differently.",
            "Why is `if x == True` a bad idea?",
        ),
        _q(
            "What do round(0.5), round(1.5) and round(2.5) print?",
            "0, 2 and 2. Python 3 rounds exact halves to the "
            "nearest even number, so 0.5 goes down to 0 "
            "and 2.5 goes down to 2 while 1.5 goes up to 2. "
            "The aim is to avoid a systematic upward bias "
            "over many values. Python 2 rounded halves "
            "away from zero, so old advice may say "
            "otherwise.",
            "How would you round half up in Python 3?",
        ),
        _q(
            "What does `a = b = []` do?",
            "It binds both names to one list, since the "
            "right-hand side is evaluated once. After "
            "`a.append(1)`, b shows [1] as well. "
            "`a, b = [], []` evaluates the expression twice "
            "and makes two lists. The same applies to "
            "`a = b = {}`, and it is the same trap as "
            "multiplying a list of lists.",
            "How would you check whether two names share an object?",
        ),
        _q(
            "What do `True + True`, `True == 1` and `isinstance(True, int)` give?",
            "2, True and True. bool is a subclass of int, with "
            "True equal to 1 and False to 0, so arithmetic "
            "just works and summing a list of booleans "
            "counts the true ones. It is also why a "
            "function that returns 1 can satisfy a check "
            "written for True, and why `True` and `1` "
            "are the same dictionary key.",
            "What does `{1: 'a', True: 'b'}` evaluate to?",
        ),
        _q(
            "What do max(\"apple\", \"Banana\") and sorted([\"b\", \"B\", \"a\"]) give?",
            "\"apple\" and ['B', 'a', 'b']. Strings compare by "
            "code point, and every capital letter sorts "
            "before every lowercase one, so \"B\" is less "
            "than \"a\" and \"apple\" is the larger of the "
            "two. For human ordering pass "
            "key=str.casefold, or use locale-aware "
            "collation if accents matter.",
            "What would sorting with key=str.casefold return?",
        ),
        _q(
            "What do `1 < 2 < 3`, `3 > 2 > 2` and `1 == 1 in [1]` evaluate to?",
            "True, False and True. A chained comparison means "
            "each pair joined by and, with the shared "
            "middle evaluated once: `3 > 2 > 2` is "
            "`3 > 2 and 2 > 2`, so False. The last is "
            "`1 == 1 and 1 in [1]`, which is True, and "
            "it surprises people because `in` is a "
            "comparison operator too.",
            "Does the middle operand get evaluated twice?",
        ),
        _q(
            "What do type((1)) and type((1,)) print?",
            "<class 'int'> and <class 'tuple'>. The comma makes the "
            "tuple, not the brackets, so `(1)` is just the "
            "number 1 in parentheses and `(1,)` has one "
            "element. A missing comma is how a "
            "one-element tuple quietly becomes its "
            "contents, such as a string in a "
            "function that expects a tuple of names.",
            "What is the empty tuple, and why does it need no comma?",
        ),
        _q(
            "What does `[\"a\" \"b\", \"c\"]` evaluate to?",
            "['ab', 'c']. Adjacent string literals are joined at "
            "compile time, so a missing comma silently merges "
            "two items instead of raising an error: "
            "`[\"a\" \"b\" \"c\"]` has length 1. It is a "
            "classic bug in long lists of strings, and "
            "it is why linters flag implicit concatenation "
            "inside collections.",
            "How is implicit concatenation useful for long strings?",
        ),
        _q(
            "What does `a, b = b, a + b` do?",
            "It evaluates the whole right-hand side first, into "
            "a tuple, and only then assigns to the targets "
            "left to right. Starting from a, b = 1, 2 it "
            "leaves a as 2 and b as 3, using the old a in the "
            "sum. Written as two separate assignments "
            "the second would see the new value, which "
            "is the usual bug. It is also how swaps and "
            "Fibonacci steps are written.",
            "What would `a = b; b = a + b` give instead?",
        ),
        _q(
            "What do `\"\" or \"default\"`, `0 and 1` and `[] or None` return?",
            "\"default\", 0 and None. `or` and `and` return one of "
            "their operands, not a bool: `or` gives the first "
            "truthy operand, or the last if none is, and "
            "`and` gives the first falsy one, or the last. "
            "That is why `x or default` is a common idiom, "
            "and why it is wrong when 0 or an empty "
            "string is a legitimate value.",
            "What would you write instead when 0 is valid?",
        ),
        _q(
            "What do int(3.9), int(-3.9), round(-3.9) and int(\"42\") give?",
            "3, -3, -4 and 42. int() truncates toward zero, "
            "which is neither floor nor round, so -3.9 "
            "becomes -3, whereas round goes to the nearest "
            "integer, -4. int() on a string parses it, and "
            "raises ValueError for something like \"3.5\", "
            "which you would have to float() first. Use "
            "math.floor when you mean rounding down.",
            "What does int(\"3.5\") do?",
        ),
        _q(
            "If B subclasses A, what happens to B.x when A.x changes?",
            "B reads x through A until it has its own, so setting "
            "`A.x = 5` makes `B.x` 5 as well. Assigning "
            "`B.x = 7` creates a new attribute on B and "
            "leaves A.x at 5, after which they are "
            "separate. Lookup goes through the class "
            "hierarchy at the time of access, not at "
            "definition, which is also why you can "
            "patch a base class and subclasses see it.",
            "How would you see which class an attribute comes from?",
        ),
    ),
)

PYTHON_INTERVIEW_TOPICS: tuple[Topic, ...] = (
    _NAMES,
    _SCOPE,
    _ITERATION,
    _DATA_MODEL,
    _EXCEPTIONS,
    _CONCURRENCY,
    _MEMORY,
    _TYPING,
    _STRUCTURES,
    _PACKAGING,
    _TESTING,
    _WEB,
    _NUMERICS,
    _TRICKY,
)
