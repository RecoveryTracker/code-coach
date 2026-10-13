"""Interview questions: what JavaScript, front-end and full-stack rounds ask.

The first bank's JavaScript topic is the language's own semantics. This one is
the rest of the round: the classic questions an interviewer reaches for, the
way people actually ask them, grouped by the thing they are really about.

Written from what the interview-prep lists, the engineering blogs and the
references (MDN, javascript.info, the ECMAScript spec, the Node docs) agree is
asked, and every answer is in our own words. Anything with a testable result
is run in real node by tests/test_concepts_interview.py, so an answer cannot
say `[1, 2, 3].map(parseInt)` gives something it does not.

The language topics belong to JavaScript. HTTP, web security, rendering
performance and testing are about the platform rather than the language, so
those are offered to everyone.
"""

from __future__ import annotations

from code_coach.concepts import Topic, _q

_JS = ("javascript",)

_CLOSURES = Topic(
    id="js-closures-scope",
    name="Closures and Scope",
    order=100,
    languages=_JS,
    blurb="Counters, loops, memoize and private state: closures as they are asked.",
    questions=(
        _q(
            "Write a counter function whose count nobody outside can reset. How does it work?",
            "Return a function from a function that owns a local variable: "
            "makeCounter declares let n = 0 and returns something that adds one "
            "to n and gives it back. The returned function keeps a reference to "
            "the scope it was born in, so n lives as long as the function does "
            "and nothing else can name it. Each call to makeCounter makes a "
            "brand new scope, so two counters never share a count. Call the "
            "first one twice and you get 1 then 2, while a second counter "
            "starts again at 1.",
            "How would you write the same thing with a class and a private field, and what changes?",
        ),
        _q(
            "Can you name three ways to fix timers in a var loop, and which would you write today?",
            "The bug is that a var loop over 0, 1 and 2 that logs i from a "
            "setTimeout prints 3, 3, 3: the timers fire after the loop has "
            "ended and every callback shares the one function-scoped i. Use "
            "let, which gives each iteration its own binding and prints 0, 1, "
            "2. Or wrap the body in a function that takes i as a parameter, or "
            "pass i as the extra argument to setTimeout. Today I would write "
            "let, and use forEach or map if the loop only walks an array.",
            "What exactly does let create per iteration, and how does the value get into the new binding?",
        ),
        _q(
            "What is lexical scope, and how does a name get looked up?",
            "Scope is decided by where code is written, not where it is "
            "called from. The engine looks for a name in the current scope, "
            "then in the scope that physically encloses it, and outward until "
            "the global scope, where a miss is a ReferenceError. So a function "
            "defined at the top of a file reads the top-level value even when "
            "it is called from inside another function that has its own "
            "variable of the same name. Only this is looked up by call site "
            "instead, which is why it surprises people.",
            "What happens when the lookup finds the name in its temporal dead zone?",
        ),
        _q(
            "What is an IIFE and why did people write them?",
            "An immediately invoked function expression is a function that is "
            "defined and called in one go, wrapped in parentheses so the "
            "parser reads it as an expression. Before modules and let, a "
            "function was the only thing that made a scope, so wrapping a "
            "file's code in one stopped its var declarations leaking onto the "
            "global object. A variable declared inside is unreachable from "
            "outside, so typeof on it gives undefined. Bundlers still emit "
            "them for the same reason, and an async IIFE is the old way to "
            "get await at the top of a script.",
            "Does a block with let inside replace the need for an IIFE?",
        ),
        _q(
            "Why does typeof throw for one variable and not for another?",
            "typeof on a name that was never declared is safe and gives the "
            "string undefined, which is why old feature checks like typeof "
            "window worked. But typeof on a let or const that is still in its "
            "temporal dead zone throws a ReferenceError, because the name does "
            "exist and reading it early is a bug. The same zone covers class "
            "declarations and a default parameter that refers to a later "
            "parameter. The rule is that undeclared is tolerated while "
            "declared but not yet initialised is an error.",
            "Why was the temporal dead zone added rather than making let behave like var?",
        ),
        _q(
            "How can a closure cause a memory leak?",
            "A closure keeps its captured scope reachable for as long as the "
            "closure itself is reachable. If something long-lived, such as an "
            "event listener, a timer or a cache entry, holds the closure, "
            "everything it can see stays in memory, and engines commonly share "
            "one scope object between all the closures made by the same call, "
            "so a large array one closure uses can be kept alive by an "
            "unrelated sibling. Fix it by dropping the reference: remove the "
            "listener, clear the interval, null the big variable, or build the "
            "closure in a small function that captures only what it needs.",
            "How would you prove in DevTools that a particular closure is what is holding the memory?",
        ),
        _q(
            "Write memoize. What can go wrong with it?",
            "Keep a Map in a closure, look the argument up, return the cached "
            "result if there is one and otherwise call the function and store "
            "what it returns. Calling a memoized function with 2, 2 and 3 runs "
            "the original only twice. The traps: stringifying the arguments "
            "makes slow or colliding keys, object arguments never match by "
            "identity, an impure function returns stale answers, and the cache "
            "grows for ever unless you cap it or key it with a WeakMap.",
            "How would you key the cache for a function of two arguments without stringifying them?",
        ),
        _q(
            "What is currying, and how is it different from partial application?",
            "Currying turns a function of several arguments into a chain of "
            "functions that each take one, so add(2)(3) replaces add(2, 3) and "
            "gives 5. Partial application fixes some arguments now and leaves "
            "the rest for later, any number at a time. Both work because the "
            "inner function closes over the arguments already supplied. Fixing "
            "the first argument with add(5) gives a function you can hand "
            "straight to map, and bind does partial application for free.",
            "How would you write a generic curry for a function of known arity?",
        ),
        _q(
            "How do you make state private in JavaScript today?",
            "There are three real options. A closure hides a variable "
            "completely and costs a fresh function per instance. A class field "
            "with a hash prefix, like #balance, is enforced by the language: "
            "outside code gets undefined, Object.keys does not list it, and "
            "only the class body can touch it. An underscore name is only a "
            "request. WeakMaps keyed by the instance were the old way to get "
            "real privacy in classes. I would use hash fields unless the code "
            "must run on an engine that lacks them.",
            "Can a subclass or a test reach a hash-private field, and should it?",
        ),
        _q(
            "Write once(fn). Where does the state live?",
            "once returns a wrapper that calls fn the first time, remembers "
            "the result, and from then on returns the remembered result. The "
            "flag and the result live in variables of the closure, so they "
            "belong to that wrapper and nobody can reset them. Wrapping a "
            "function that increments a counter and calling the wrapper twice "
            "leaves the counter at 1. It is the tidy way to run initialisation "
            "exactly once, and the same shape sits underneath memoize and "
            "debounce.",
            "What should once do if fn throws the first time?",
        ),
    ),
)

_THIS = Topic(
    id="js-this-binding",
    name="this, call, apply and bind",
    order=110,
    languages=_JS,
    blurb="Losing this in a callback, binding it back, and where arrows help or hurt.",
    questions=(
        _q(
            "What is the difference between call, apply and bind?",
            "All three set this explicitly. call runs the function now with "
            "the arguments listed one by one, apply runs it now with the "
            "arguments in an array, and bind runs nothing but returns a new "
            "function with this, and optionally some leading arguments, fixed. "
            "For a function that adds this.n and two arguments, call(o, 2, 3), "
            "apply(o, [2, 3]) and bind(o, 2)(3) all give 6 when o.n is 1. "
            "Spread has made apply rare, since fn.call(o, ...args) says the "
            "same thing.",
            "What does bind give you when you call new on the result?",
        ),
        _q(
            "A callback logs the wrong this. How do you diagnose it and what are the fixes?",
            "Ask how the function was called, because that decides this. "
            "Writing setTimeout(obj.method, 100) passes the bare function, so "
            "the later call has no object before the dot and this is undefined "
            "in strict code, or the global object in sloppy code. Fix it with "
            "an arrow wrapper that calls obj.method() itself, with "
            "obj.method.bind(obj), or by making the method an arrow class "
            "field. In a test, g() gives undefined while o.get() gives 1 when "
            "g is the method pulled out of o.",
            "Why does the problem not exist for a function that never uses this?",
        ),
        _q(
            "How do arrow functions differ from normal functions beyond shorter syntax?",
            "An arrow has no this, no arguments object, no super and no "
            "prototype, so it picks all of those up from the surrounding "
            "scope. That also means it cannot be a constructor: calling new on "
            "one throws a TypeError. Because this is fixed when the arrow is "
            "created, call, apply and bind cannot change it. That is exactly "
            "why arrows suit callbacks inside methods, where a map callback "
            "can read this.n directly, and why they are wrong for methods "
            "that need the receiver.",
            "Why can you not rebind an arrow function with call?",
        ),
        _q(
            "When is an arrow function the wrong choice?",
            "When you need your own this or arguments. An arrow used as an "
            "object method does not receive the object: at the top of a "
            "CommonJS file this is the module's exports object, so this.n is "
            "undefined, and in an ES module this is undefined itself. The same "
            "goes for prototype methods, constructors, generators, which "
            "cannot be arrows at all, and DOM handlers that want this to be "
            "the element. Use method shorthand there. For callbacks and short "
            "helpers, arrows are the default.",
            "What would you change in a class that stores all its handlers as arrow properties?",
        ),
        _q(
            "What does the new operator do, step by step?",
            "It creates an empty object whose prototype is the constructor's "
            "prototype property, calls the constructor with this set to that "
            "object, and returns the object, unless the constructor itself "
            "returns a different object. A constructor that returns an object "
            "hands back that object instead, and the one new built is thrown "
            "away, while returning a primitive like 5 is ignored. Forgetting "
            "new in sloppy code runs the function with this as the global "
            "object, which is why classes refuse to be called without it.",
            "How can a function tell whether it was called with new?",
        ),
        _q(
            "How would you implement Function.prototype.bind?",
            "Return a new function that, when called, calls the original with "
            "this set to the saved value and the saved arguments followed by "
            "the new ones: fn.apply(thisArg, [...saved, ...later]). A complete "
            "version also handles new, because a bound function used as a "
            "constructor ignores the bound this and builds an instance of the "
            "original. So the instance has the constructor's properties, "
            "instanceof the original is true, and a property of the ignored "
            "bound object is undefined on it.",
            "What is the length of a bound function, and why?",
        ),
        _q(
            "What is this inside an event handler?",
            "For a normal function passed to addEventListener, this is the "
            "element the listener is attached to, the same object as "
            "event.currentTarget, which can differ from event.target when the "
            "event bubbled up from a child. An arrow function ignores that and "
            "keeps the enclosing this. Node's EventTarget follows the same "
            "rule, so with a regular function this === t prints true for the "
            "target the listener was added to. Inline onclick attributes "
            "behave like regular functions too.",
            "How does that change when the handler is a method of a class?",
        ),
        _q(
            "What is this at the top level, in a module, and in a plain function?",
            "It depends on the host and the mode. In a classic browser script "
            "it is window, in an ES module it is undefined, and in a CommonJS "
            "Node file it is module.exports, so this === module.exports is "
            "true there. Inside a plain function it is the global object in "
            "sloppy mode and undefined in strict mode: a function that returns "
            "this gives globalThis when sloppy and undefined after a use "
            "strict directive. Classes and modules are always strict, so it "
            "surprises people less there.",
            "What problem does globalThis exist to solve?",
        ),
        _q(
            "How do you keep this correct for a class method used as a callback?",
            "Three habits. Bind in the constructor, which keeps one shared "
            "prototype method and makes a bound copy per instance. Define the "
            "method as an arrow class field, which is shortest but creates a "
            "new function per instance and puts it on the instance rather "
            "than the prototype, so you cannot override it through super or "
            "spy on it from the prototype. Or wrap at the call site with an "
            "arrow. With none of them a destructured method throws a "
            "TypeError, because class code is strict and this is undefined.",
            "What is the cost of an arrow class field when you create ten thousand instances?",
        ),
        _q(
            "Can you change this on an arrow function or on an already bound function?",
            "No to both. call, apply and bind on an arrow function pass the "
            "arguments along but ignore the this you supply, because an arrow "
            "gets its this from where it was written. A bound function is "
            "similar: binding it again does not replace the first binding, so "
            "the first one wins. If f is bound to an object with n equal to 1 "
            "and the result is bound to another object, calling it still "
            "reports 1. The only way to change it is to bind the original "
            "function again.",
            "How do you borrow a method for a different object without binding?",
        ),
    ),
)

_PROTOTYPES = Topic(
    id="js-prototypes-classes",
    name="Prototypes, Classes and Inheritance",
    order=120,
    languages=_JS,
    blurb="Object.create, new, extends, instanceof and prototype pollution.",
    questions=(
        _q(
            "What do Object.create(null) and Object.create(proto) give you?",
            "Object.create(proto) makes a new empty object whose prototype "
            "link points at proto, so a lookup that misses falls through to "
            "it: an object made from a base with a hi method can call hi "
            "although hi is not an own property. Object.create(null) makes an "
            "object with no prototype at all, so no toString and no inherited "
            "keys. That makes a safe dictionary: 'toString' in it is false, "
            "while in a plain object it is true. The cost is losing the "
            "helper methods, so you call Object.hasOwn instead.",
            "Why is a Map usually a better dictionary than Object.create(null)?",
        ),
        _q(
            "Are JavaScript classes real classes?",
            "They are syntax over the same prototype machinery, with a few "
            "real differences. typeof a class is function, its methods are "
            "non-enumerable so Object.keys of the prototype is empty, the body "
            "is always strict, and calling it without new throws a TypeError "
            "instead of quietly running. Class declarations also sit in the "
            "temporal dead zone rather than being hoisted as usable "
            "functions. There is no separate class type underneath, so "
            "inheritance still means a prototype link.",
            "What would the same class look like written before ES2015?",
        ),
        _q(
            "What must a derived constructor do before it touches this?",
            "It must call super() first. In a derived class the object is "
            "created by the base constructor, not by the derived one, so "
            "until super returns there is no this, and touching it throws a "
            "ReferenceError. If you never call super and do not return an "
            "object, constructing the instance throws the same error at the "
            "end. super(...) is also how you pass arguments up, and a class "
            "with no constructor gets one that forwards everything to super.",
            "Why was it designed so the base class allocates the object?",
        ),
        _q(
            "What is the difference between static, prototype and instance members?",
            "A prototype method is defined once on the class's prototype and "
            "shared by every instance, which is where ordinary methods go. An "
            "instance field is created fresh on each object, so each gets its "
            "own copy. A static member lives on the class itself and is not "
            "visible through instances: for a class with a static s and a "
            "method m, typeof a.s is undefined and typeof A.m is undefined. "
            "Statics are inherited by subclasses through the constructor's own "
            "prototype link, a second chain beside the instance one.",
            "Where would you put a factory method, and why does it suit static?",
        ),
        _q(
            "How does instanceof work, and when does it give the wrong answer?",
            "x instanceof F asks whether F.prototype appears anywhere on x's "
            "prototype chain, so it checks the chain rather than who built the "
            "object. That has consequences: reassigning F.prototype after "
            "creating an object makes the check false for it, and an array "
            "from another frame or realm is not an instance of this realm's "
            "Array, so use Array.isArray there. A class can also customise the "
            "answer with a static Symbol.hasInstance method. For primitives "
            "it is always false.",
            "How would you check for a plain object without instanceof?",
        ),
        _q(
            "How do for...in, Object.keys and Object.hasOwn treat inherited properties?",
            "for...in walks own and inherited enumerable string keys, own ones "
            "first and then the prototype's. Object.keys lists only own "
            "enumerable ones, and Object.hasOwn tests one name against own "
            "properties only. If the prototype has a and the object has its "
            "own b, for...in sees b then a, while Object.keys sees only b. "
            "That is why for...in over an array or a dictionary is a bug "
            "waiting to happen, and why people add a hasOwn guard.",
            "Which properties does for...in skip even when they are inherited?",
        ),
        _q(
            "Inheritance or composition: how do you decide in JavaScript?",
            "Inheritance models is-a and is cheap when the hierarchy is "
            "shallow and stable, but every level couples the subclass to the "
            "parent's internals, and single inheritance forces you to pick one "
            "parent. Composition models can-do: you assemble behaviour from "
            "small objects or functions and mix abilities in without a "
            "hierarchy, for example by copying a fly method onto a prototype "
            "with Object.assign. I default to composition and keep "
            "inheritance to one level, usually a framework base class.",
            "What goes wrong with mixins that carry their own state?",
        ),
        _q(
            "How was inheritance written before the class keyword?",
            "The child constructor calls the parent constructor on this with "
            "call, then the child's prototype is set to an object made from "
            "the parent's prototype with Object.create, and its constructor "
            "property is put back by hand. Methods go on the prototype. The "
            "result behaves like extends: a new child has the parent's "
            "methods and instanceof the parent is true. The classic mistake "
            "was assigning a new parent instance as the child prototype, which "
            "runs the parent constructor at definition time and shares state.",
            "What breaks if you forget to restore the constructor property?",
        ),
        _q(
            "What do property descriptors control?",
            "Each property has attributes: writable, enumerable and "
            "configurable for data properties, or get and set for accessors. "
            "Object.defineProperty sets them, and they all default to false "
            "when you define a new property that way, unlike plain "
            "assignment. A property defined with only a value cannot be "
            "reassigned, so in sloppy code the assignment silently does "
            "nothing and in strict code it throws, it stays out of "
            "Object.keys, and it cannot be deleted. Freezing, sealing and "
            "class methods are built from these flags.",
            "What is the difference between Object.freeze, seal and preventExtensions?",
        ),
        _q(
            "Why should you not put an array on a prototype?",
            "Because the prototype is shared, so a property found there is one "
            "single object for every instance. Calling push on it mutates the "
            "shared array instead of creating the instance's own, and one "
            "object's change shows up in all the others. Assignment is "
            "different: assigning to the name on an instance creates an own "
            "property that shadows the prototype's. With an array on "
            "F.prototype, pushing through one instance makes the length 1 when "
            "read through another. Put mutable defaults in the constructor or "
            "a class field.",
            "Are class fields initialised per instance or shared, and why?",
        ),
        _q(
            "What is prototype pollution?",
            "An attacker-controlled key such as __proto__ reaches code that "
            "writes properties by path or merges objects recursively, so the "
            "write lands on Object.prototype and every object inherits the "
            "new property. A naive deep merge of parsed JSON carrying a "
            "__proto__ key can set admin to true, and a later empty object "
            "reads true. Defences: reject the __proto__, constructor and "
            "prototype keys, merge into Object.create(null), freeze the "
            "prototype, or use Map. JSON.parse itself only creates an own "
            "property of that name.",
            "Why does Object.assign not cause the same problem?",
        ),
    ),
)

_EVENT_LOOP = Topic(
    id="js-event-loop-timers",
    name="The Event Loop, Microtasks and Timers",
    order=130,
    languages=_JS,
    blurb="Output-order puzzles, long tasks, timers that lie and errors that escape.",
    questions=(
        _q(
            "Can you walk me through the output when a sync log, a zero-delay timer, a promise callback and another sync log run in that order?",
            "Say the logs are A, then a setTimeout of zero that prints B, then "
            "a promise callback that prints C, then D. The script is one "
            "task, so A and D print first. When it finishes the engine drains "
            "the microtask queue before anything else, so C prints. Only then "
            "can the timer, a separate task, fire. The output is A D C B. If "
            "you can say why a timer with zero delay still comes last, you "
            "have understood the loop.",
            "Where would a requestAnimationFrame callback land in that sequence?",
        ),
        _q(
            "Why is setTimeout with zero delay never really zero?",
            "The delay is a minimum, not a schedule. The callback joins the "
            "timer queue after at least that long and then waits for the "
            "current task and every microtask to finish. Browsers also clamp: "
            "once timers are nested more than five levels deep the minimum "
            "becomes 4 milliseconds, and background tabs throttle timers much "
            "harder. Node treats a delay of zero as 1 millisecond. So timers "
            "are fine for deferring work and no good for precise timing; "
            "measure with performance.now.",
            "How would you run something right after the current task but before rendering?",
        ),
        _q(
            "How can one long task make the page feel frozen, and how do you break it up?",
            "Input handling and rendering are tasks on the same thread, so "
            "while a long task runs the page can neither repaint nor react to "
            "a click. Anything over about 50 milliseconds counts as a long "
            "task, and the Interaction to Next Paint metric punishes it. You "
            "split the work into chunks and yield between them with "
            "setTimeout, scheduler.yield where it exists, or requestIdleCallback "
            "for low priority jobs, or you move it to a Web Worker. Chunking "
            "with microtasks does not help, because rendering still waits for "
            "the queue to drain.",
            "How would you choose the chunk size?",
        ),
        _q(
            "What order do the logs come out in around an await?",
            "Take an async function that logs 1, awaits null and then logs 3, "
            "called just before a synchronous log of 2. It runs synchronously "
            "up to the first await, so 1 prints. Then await hands control back "
            "to the caller and queues the rest as a microtask, so 2 prints, "
            "and 3 follows. That gives 1, 2, 3. Even awaiting a value that is "
            "already there defers the continuation by at least a microtask, "
            "so an async function never runs its remaining code in the same "
            "tick as the call.",
            "How many microtask ticks does awaiting a native promise take, compared with a thenable?",
        ),
        _q(
            "Two promise chains are started together. How do their callbacks interleave?",
            "A then callback is queued as a microtask only once the previous "
            "promise in its chain settles, so chains advance one step per "
            "round and take turns. With one chain logging 1 then 3 and the "
            "other logging 2 then 4, started in that order, the output is 1, "
            "2, 3, 4 rather than 1, 3, 2, 4. The first step of each chain is "
            "queued immediately and the second steps are queued as the first "
            "ones finish. It is a good check that you understand queues "
            "rather than a memorised answer.",
            "What changes if the first callback in one chain returns a promise instead of a plain value?",
        ),
        _q(
            "Is JavaScript single-threaded? What runs in parallel?",
            "Your code runs on one thread per realm, taking one task at a "
            "time, so ordinary variables have no data races. The environment "
            "is not single-threaded: the browser does networking, timers, "
            "decoding and rendering elsewhere and posts the results back as "
            "tasks. Web Workers add real parallelism, each with its own heap "
            "and its own event loop, and they talk by message passing, which "
            "copies data with structured clone unless you transfer it. "
            "SharedArrayBuffer with Atomics is the only shared mutable memory, "
            "and it needs cross-origin isolation.",
            "What would you move to a worker in a game, and what would you keep on the main thread?",
        ),
        _q(
            "Why does a recursive setTimeout let the page breathe when a recursive promise does not?",
            "Each timer callback is its own task, so between two of them the "
            "loop can render and handle input. A promise callback is a "
            "microtask, and the loop drains the whole microtask queue, "
            "including anything added while it drains, before it moves on. So "
            "a promise that schedules itself for ever never reaches the timer "
            "queue or a repaint. Take 1000 self-scheduled promise callbacks: "
            "the done message prints before a timer that was set at the start.",
            "How would you process a huge array without freezing the page?",
        ),
        _q(
            "Where does requestAnimationFrame fit into the loop?",
            "At each opportunity the browser decides whether to render, "
            "usually once per display refresh. When it does, it runs the "
            "animation frame callbacks first, then style, layout and paint. "
            "So the callback runs before the repaint, after the microtasks of "
            "the previous task, and it receives a timestamp for the frame. It "
            "is one-shot, so the callback must request the next frame itself, "
            "and it is paused in background tabs. At 60 Hz you have about "
            "16.7 milliseconds per frame for everything. Node has no "
            "equivalent.",
            "Why do two callbacks in the same frame see the same timestamp?",
        ),
        _q(
            "How would you write sleep(ms), and what does it not guarantee?",
            "Wrap a timer in a promise: new Promise with setTimeout calling "
            "resolve. Awaiting it pauses only that async function, not the "
            "thread. What it does not guarantee is precision. The delay is a "
            "minimum, because the continuation also waits for the current "
            "task and any queued microtasks, so a sleep of 50 takes at least "
            "roughly 50 and often a little more. It is not cancellable "
            "unless you wire in an AbortSignal, and a sleeping function keeps "
            "its scope alive.",
            "How would you make sleep cancellable?",
        ),
        _q(
            "Why can an error thrown inside a timer not be caught by a try around setTimeout?",
            "Because the callback runs later, in a different task, long after "
            "the try block has exited and the stack that contained it has "
            "gone. The try only covers code that runs during its own turn, so "
            "the call to setTimeout succeeds and the catch never fires. The "
            "error surfaces as an uncaught exception, which in a browser "
            "lands in window.onerror and in Node ends the process unless a "
            "handler is registered. Promises work the same way: put the catch "
            "on the promise, or await inside a try in an async function.",
            "Where should the top-level error handler live in a single-page app?",
        ),
        _q(
            "What does setInterval do if its callback takes longer than the interval?",
            "Callbacks never overlap, because the thread runs one task at a "
            "time. If the callback is slow, the next one starts as soon as "
            "the loop is free, so the effective period stretches and runs can "
            "land back to back. Intervals also drift, since each is "
            "scheduled through the timer queue rather than against a clock. "
            "For polling, call setTimeout at the end of each run so the delay "
            "always starts after the work finishes, and for animation use "
            "requestAnimationFrame. For a clock, compare against Date.now or "
            "performance.now instead of counting ticks.",
            "How would you stop an interval from running while the tab is hidden?",
        ),
    ),
)

_PROMISES = Topic(
    id="js-promises-async",
    name="Promises and async/await",
    order=140,
    languages=_JS,
    blurb="Settling, chaining, the combinators, escaping errors and bounded concurrency.",
    questions=(
        _q(
            "How does a promise settle, and what happens if you resolve it twice?",
            "A promise starts pending and moves exactly once to fulfilled or "
            "rejected, after which it is frozen. Extra calls to resolve or "
            "reject are ignored without an error, so a promise that calls "
            "resolve with 1, then reject, then resolve with 3, delivers 1 to "
            "its then handler. Resolving with another promise or thenable does "
            "not fulfil it directly: it locks onto that other one and adopts "
            "its eventual state. Handlers attached after settlement still "
            "run, as a microtask.",
            "Does a promise run its executor immediately or later?",
        ),
        _q(
            "How do Promise.all, allSettled, race and any compare?",
            "all fulfils with every result in input order and rejects with the "
            "first rejection. allSettled never rejects and gives an array of "
            "status objects, so it is the one for independent jobs where you "
            "want every outcome. race settles the way whichever input settles "
            "first does, win or lose. any fulfils with the first success and "
            "rejects only when everything rejected, with an AggregateError "
            "whose errors array holds each reason. None of them cancel the "
            "losers, which keep running; their results are just ignored.",
            "How would you cancel the losing requests in a race?",
        ),
        _q(
            "What does then return, and how does chaining flatten?",
            "then always returns a new promise. If the callback returns a "
            "plain value the new promise fulfils with it; if it returns a "
            "promise or thenable the new promise follows that one, which is "
            "why chains stay flat; if it throws, the new promise rejects. A "
            "catch that returns a value recovers the chain, so a rejection "
            "followed by a catch returning ok and then a log prints ok. To "
            "keep an error flowing after logging it, rethrow. Forgetting to "
            "return inside a then is the commonest chaining bug.",
            "What does finally receive, and what does it return?",
        ),
        _q(
            "Where do errors go in async functions, and why can return await matter?",
            "An async function turns a throw into a rejected promise, and "
            "try/catch only catches what is awaited inside the try. Returning "
            "a rejected promise without await hands it to the caller, so the "
            "catch block inside never runs and the rejection escapes the "
            "handler. With return await the rejection is thrown inside the "
            "try and caught there, which turns the function into one that "
            "returns a rescued value. Outside a try block the two forms are "
            "nearly equivalent, and many linters allow the shorter one.",
            "What do you lose in stack traces if you leave out the await?",
        ),
        _q(
            "Why does forEach with an async callback not wait?",
            "forEach ignores whatever its callback returns, so the promises an "
            "async callback returns are dropped and nothing waits for them. "
            "The code after the call runs while the callbacks are still "
            "suspended at their first await: with a callback that awaits and "
            "then pushes to an array, the array still has length 0 right "
            "after forEach. To run one after another use for...of with await, "
            "and to run all in parallel and wait, map to promises and await "
            "Promise.all. Errors from those callbacks become unhandled "
            "rejections.",
            "How does for...of with await compare with Promise.all for total time?",
        ),
        _q(
            "When should awaits be sequential and when parallel?",
            "Sequential when each step needs the previous result, or when "
            "order or rate limits matter, and parallel when the operations are "
            "independent. Two awaited 60 millisecond sleeps take about 120, "
            "while the same two started together and awaited with "
            "Promise.all take about 60. The common mistake is an await in a "
            "loop over independent items. The opposite mistake is firing "
            "everything at once, which can overwhelm a server, so cap the "
            "concurrency. Starting the promises first and awaiting them "
            "later is the middle ground.",
            "How would you limit that to five at a time?",
        ),
        _q(
            "How do you add a timeout or cancellation to an async operation?",
            "Promise.race with a timer only stops you waiting; the slow work "
            "carries on in the background. Real cancellation needs the "
            "operation to listen: pass an AbortSignal, which fetch and many "
            "APIs understand, and call abort on the controller. "
            "AbortSignal.timeout(ms) gives a signal that aborts itself, with a "
            "reason whose name is TimeoutError. Aborting a fetch rejects its "
            "promise with an AbortError, so your catch must tell it apart from "
            "real failures. Your own functions should check signal.aborted or "
            "listen for the abort event.",
            "What happens to the request on the wire when you abort it?",
        ),
        _q(
            "What is the explicit promise construction anti-pattern?",
            "Wrapping something that already returns a promise inside new "
            "Promise for no benefit, which adds noise and tends to lose "
            "errors: forget a reject path and the promise stays pending for "
            "ever. Use new Promise only to wrap a callback API, and make "
            "sure every callback path settles. A throw inside the executor is "
            "turned into a rejection, so it still lands in catch with the "
            "message. For ordinary callback APIs prefer util.promisify, and "
            "inside async functions just return or await.",
            "How would you promisify setTimeout, and why is it a safe case?",
        ),
        _q(
            "What is an unhandled rejection, and what happens to it?",
            "It is a rejected promise that nobody has attached a rejection "
            "handler to by the time the microtask queue drains. Browsers log "
            "an error and fire an unhandledrejection event on window. Node, "
            "since version 15, treats it like an uncaught exception and ends "
            "the process by default, unless you listen for "
            "unhandledRejection. A handler attached late still receives the "
            "rejection but the warning has already fired. The habit that "
            "prevents it is to end every chain with catch, or await it inside "
            "a try block.",
            "Should an application catch these globally and carry on?",
        ),
        _q(
            "How would you run a hundred requests but only five at a time?",
            "Start five workers, each an async loop that takes the next index "
            "from a shared counter, awaits the job and goes back for more "
            "until the list is empty, then await Promise.all of the workers. "
            "Because JavaScript runs one task at a time, the shared counter "
            "needs no lock. A pool over eight items with a limit of three "
            "never has more than three jobs in flight. Add per-job error "
            "handling so one failure does not leave the others running "
            "unobserved, and retry with backoff for transient errors.",
            "How does that change if the jobs must start in a fixed order?",
        ),
        _q(
            "What is a thenable, and what does await do with a plain value?",
            "A thenable is any object with a then method, and promise "
            "resolution and await both adopt it by calling then with their own "
            "resolve function. So awaiting an object whose then calls its "
            "callback with a string gives that string. Awaiting a plain value, "
            "such as null, works too: it is wrapped in a resolved promise and "
            "still suspends the function for a microtask. That is why library "
            "code can accept either a value or a promise and treat both the "
            "same by awaiting.",
            "What goes wrong if a user object accidentally has a then method?",
        ),
    ),
)

_TYPES = Topic(
    id="js-types-coercion",
    name="Types, Coercion and Equality",
    order=150,
    languages=_JS,
    blurb="typeof, the plus operator, parseInt in map and the table behind ==.",
    questions=(
        _q(
            "What are JavaScript's primitive types, and what does typeof say for each?",
            "There are seven primitives: string, number, bigint, boolean, "
            "undefined, symbol and null. typeof reports the type name for all "
            "of them except null, where it says object, a bug from the first "
            "version that was never fixed because the web depends on it. "
            "Everything else is an object, and typeof a function says function "
            "even though functions are objects too. So typeof null, an arrow "
            "function, 1n and a symbol gives object, function, bigint and "
            "symbol. Primitives are immutable and compared by value.",
            "How do you reliably tell an array, a date and a plain object apart?",
        ),
        _q(
            "What do 0.1 + 0.2 and 9007199254740993 print in JavaScript, and why?",
            "Every number is a 64-bit double with a 53-bit significand, so 0.1 "
            "and 0.2 are stored as slightly wrong binary fractions and their "
            "sum prints as 0.30000000000000004. Integers are exact only up to "
            "2 to the 53 minus 1, which Number.MAX_SAFE_INTEGER names: "
            "9007199254740991. Past that the spacing is two, so the literal "
            "9007199254740993 is stored as 9007199254740992. Compare floats "
            "with a tolerance, keep money in integer cents, and reach for "
            "BigInt for large integers.",
            "What does Number.EPSILON actually give you, and when is it the wrong tolerance?",
        ),
        _q(
            "What do [] + {}, [] + [] and [1] + [2] give, and what is the rule?",
            "The plus operator first converts both sides to primitives. "
            "Objects, arrays included, do that through valueOf and then "
            "toString, and an array's toString joins its elements, so [] "
            "becomes the empty string and [1] becomes the string 1. If either "
            "side is then a string, plus concatenates. So [] + {} is the "
            "string [object Object], [] + [] is an empty string and [1] + [2] "
            "is the string 12. Only when neither side is a string does plus "
            "convert both to numbers and add.",
            "Why can {} + [] at the start of a statement give a different answer?",
        ),
        _q(
            "What does [1, 2, 3].map(parseInt) return, and why?",
            "It returns [1, NaN, NaN]. map calls the callback with three "
            "arguments, the value, the index and the array, and parseInt takes "
            "a string and a radix, so the index becomes the radix. A radix of "
            "0 means ten, so the first gives 1. A radix of 1 is invalid, so "
            "the second is NaN, and 3 is not a binary digit, so the third is "
            "NaN as well. Wrap it in an arrow that passes 10, or use Number, "
            "which ignores the extra arguments.",
            "Which other built-ins bite when you pass them straight to map?",
        ),
        _q(
            "How does Object.is differ from ===?",
            "=== has two oddities: NaN is not equal to itself, and 0 equals "
            "-0. Object.is fixes both, so Object.is(NaN, NaN) is true and "
            "Object.is(0, -0) is false, and is otherwise the same as ===. "
            "React's check for changed state uses it. Map and Set use a close "
            "cousin, SameValueZero, which also treats NaN as equal but treats "
            "0 and -0 as the same. To test for NaN, Number.isNaN is clearer. "
            "Objects compare by identity under all of them.",
            "Why does includes find NaN when indexOf cannot?",
        ),
        _q(
            "What are the falsy values, and why does it matter?",
            "There are eight: false, 0, -0, 0n, the empty string, null, "
            "undefined and NaN. Everything else is truthy, including the "
            "string 0, an empty array and an empty object. That is why a check "
            "like if (count) treats a legitimate zero as missing, and why [] "
            "being truthy surprises people. Filtering a list of 0, an empty "
            "string, null, undefined, NaN, 0n, [], {} and the string 0 with "
            "Boolean keeps exactly three, the last three. Use ?? to default "
            "only null and undefined.",
            "What does ?? do differently from || when the left side is 0?",
        ),
        _q(
            "How does plus decide between adding and concatenating, and what do the other operators do?",
            "Plus concatenates if either operand is a string after conversion "
            "to a primitive, and otherwise adds numerically. Minus, times and "
            "divide have no string meaning, so they always convert to "
            "numbers. That makes 1 + '2' the string 12, but '3' - 1 is 2 and "
            "'3' * '4' is 12. Booleans become 1 and 0, so true + 1 is 2, null "
            "becomes 0 so null + 1 is 1, and undefined becomes NaN, so "
            "undefined + 1 is NaN. A unary plus is the short way to convert "
            "to a number.",
            "What does plus do to a Date?",
        ),
        _q(
            "How does an object turn into a primitive?",
            "Through a conversion called ToPrimitive, which takes a hint of "
            "string, number or default. An object can define Symbol.toPrimitive "
            "to control it; otherwise the engine calls valueOf and toString in "
            "an order the hint picks, valueOf first for number and default, "
            "toString first for string. So an object whose valueOf returns 42 "
            "and whose toString returns 'str' gives 43 when you add 1 and "
            "'str' inside a template literal or String(o). Date is the "
            "exception that treats the default hint as string.",
            "What do plus and a template literal do with a Date, and why?",
        ),
        _q(
            "What is the difference between isNaN and Number.isNaN?",
            "The global isNaN converts its argument to a number first, so "
            "isNaN('abc') is true and isNaN('') is false because the empty "
            "string converts to 0. Number.isNaN does no conversion and is true "
            "only for the actual value NaN, so Number.isNaN('abc') is false. "
            "Prefer Number.isNaN, and Number.isFinite over the global isFinite, "
            "for the same reason. NaN is the only value not equal to itself, "
            "which is the old trick for detecting it, and typeof NaN is "
            "number.",
            "What do Number('12px') and parseInt('12px') give?",
        ),
        _q(
            "Can you walk me through why [] == ![] is true?",
            "The right side is evaluated first: ![] is false, because an array "
            "is truthy. Now it is [] == false. A boolean is converted to a "
            "number, so the right is 0. Then an object against a number "
            "converts the object to a primitive, [] becomes the empty string, "
            "and that converts to 0. 0 == 0 is true. In the same family "
            "null == 0 is false, null >= 0 is true, and null == undefined is "
            "true, because relational operators convert with ToNumber while "
            "== has a special rule for null.",
            "Which comparisons would you ban with a lint rule?",
        ),
        _q(
            "How do BigInt and Number differ, and can you mix them?",
            "BigInt is an arbitrary-precision integer, written with an n "
            "suffix, for values beyond Number.MAX_SAFE_INTEGER such as ids and "
            "exact large counts. You cannot mix it with Number in arithmetic: "
            "1n + 1 throws a TypeError, so you convert explicitly. 2n ** 64n "
            "is exactly 18446744073709551616n. There are no fractions, Math "
            "functions reject it, and JSON.stringify throws on it. Comparison "
            "across the types works, so 1n < 2 and 1n == 1 are true, but "
            "1n === 1 is false.",
            "What happens when you JSON.stringify an object with a BigInt in it?",
        ),
    ),
)

_DATA = Topic(
    id="js-objects-arrays-immutability",
    name="Objects, Arrays and Immutability",
    order=160,
    languages=_JS,
    blurb="Copying, freezing, sorting, Map and Set, WeakMap and updating state without mutating it.",
    questions=(
        _q(
            "What is the difference between a shallow and a deep copy? What do spread and structuredClone do?",
            "Spread and Object.assign copy only the top level: nested objects "
            "are still shared between the copy and the original. "
            "structuredClone makes a deep copy, so changing a nested value in "
            "the original afterwards leaves the clone alone. With a nested x "
            "changed from 1 to 2 in the original, the spread copy reads 2 and "
            "the structuredClone copy reads 1. Arrays split the same way: "
            "slice, concat and spread are shallow. Deep copies are rarely "
            "needed if you update immutably instead.",
            "What happens to a cyclic reference in structuredClone, and in JSON.stringify?",
        ),
        _q(
            "What can structuredClone not copy, and what does a JSON round trip lose?",
            "structuredClone handles Date, Map, Set, regular expressions, "
            "typed arrays and cycles, but it throws a DataCloneError on "
            "functions and DOM nodes, and a class instance comes back as a "
            "plain object, so instanceof is false. A JSON round trip loses "
            "more: undefined, functions and symbols are dropped, NaN becomes "
            "null, a Date becomes a string, and Map and Set become empty "
            "objects. A stringified object holding undefined, a function, a "
            "Date and NaN keeps only the Date as a string and the NaN as null.",
            "Which would you choose to deep-copy state: structuredClone, JSON or a library?",
        ),
        _q(
            "What does Object.freeze do and not do?",
            "freeze makes an object's own properties read-only and stops "
            "properties being added or removed. It is shallow: freezing an "
            "object with a nested one and then changing the nested value "
            "works, because the inner object was never frozen. In sloppy code "
            "a write to a frozen property is silently ignored, and in strict "
            "code and modules it throws a TypeError. Object.isFrozen reports "
            "the state, and deep freezing means recursing. It is a guardrail "
            "for constants and reducers, not a security feature.",
            "What is the difference between a const binding and a frozen object?",
        ),
        _q(
            "Which array methods mutate, and what is toSorted for?",
            "push, pop, shift, unshift, splice, sort, reverse, fill and "
            "copyWithin change the array in place, while map, filter, slice "
            "and concat return new ones. The mutating ones are a common source "
            "of bugs in state code, because sorting an array you were handed "
            "reorders the caller's copy too. ES2023 added non-mutating "
            "versions: toSorted, toReversed, toSpliced and with. After toSorted "
            "on 3, 1, 2 the original still reads 3,1,2 and the result is "
            "1,2,3.",
            "What does toSorted cost compared with sort on a large array?",
        ),
        _q(
            "Why does [10, 9, 1].sort() give 1, 10, 9?",
            "With no comparator, sort converts the elements to strings and "
            "compares them by UTF-16 code units, so the numbers are ordered as "
            "text: 1 comes before 10, which comes before 9. The result is "
            "1,10,9. Pass a comparator that returns a negative, zero or "
            "positive number, such as a minus b, and you get 1,9,10. The sort "
            "is stable in modern engines, so equal elements keep their order, "
            "but the comparator must be consistent or the order is "
            "implementation-defined.",
            "How do you sort strings correctly for a language, accents included?",
        ),
        _q(
            "When would you use a Map instead of a plain object?",
            "When the keys are not known in advance or are not strings. A Map "
            "accepts any value as a key, remembers insertion order, has a size, "
            "iterates directly and has no inherited keys to collide with. A "
            "plain object turns keys into strings or symbols and lists "
            "integer-like keys first, ascending, before the rest in insertion "
            "order. So keys b, 2, a and 1 list as 1,2,b,a on an object, while "
            "a Map built in that order gives b,2,a,1. Objects win for fixed "
            "shapes, JSON and ergonomic syntax.",
            "How do you serialise a Map to JSON?",
        ),
        _q(
            "How does a Set compare values, and how do you remove duplicates from an array?",
            "A Set uses SameValueZero: values match like strict equality "
            "except that NaN matches NaN, and 0 and -0 count as one. Spread a "
            "Set built from the array to dedupe, keeping first-seen order. "
            "Deduping 1, 1, the string 1, NaN, NaN, 0 and -0 leaves four "
            "values, because the string is a different type. Objects compare "
            "by reference, so two equal-looking objects both stay; for those, "
            "key a Map on an id. Sets also give constant-time membership "
            "checks.",
            "How would you compute the intersection of two arrays efficiently?",
        ),
        _q(
            "What is a WeakMap for, and why can you not iterate it?",
            "A WeakMap holds its keys weakly: when nothing else references a "
            "key object, the entry can be garbage collected. That makes it the "
            "right place for private data or caches attached to objects you do "
            "not own, such as DOM elements, without leaking them. Keys must be "
            "objects or non-registered symbols, and a string key throws a "
            "TypeError. It has no size and no iteration, because which entries "
            "exist depends on when the collector ran, and exposing that would "
            "make programs non-deterministic.",
            "How would you cache a computed result per DOM element without leaking it?",
        ),
        _q(
            "How do you update nested state without mutating it?",
            "Copy every object along the path to the changed value and reuse "
            "everything else. With spread that is one spread per level: the new "
            "top object takes the old fields and overrides the one nested "
            "object, which was itself copied with an override. The untouched "
            "branches are the same references, so a cheap identity check says "
            "what changed, which is what memoised components and selectors "
            "rely on. After such an update the sibling is still the same "
            "object, the changed branch is new, and the old state is "
            "unchanged. Immer automates this.",
            "What does an immutable update cost on a large array, and how do persistent structures help?",
        ),
        _q(
            "What do destructuring defaults apply to?",
            "A default applies only when the value is undefined, not for null "
            "or other falsy values. Destructuring a default of 1 for a and 2 "
            "for b from an object whose a is undefined and whose b is null "
            "gives a as 1 and b as null. Defaults are evaluated lazily, only "
            "when needed, and may refer to earlier names. Default parameters "
            "follow the same rule. If you also want to replace null, use the "
            "nullish coalescing operator, which treats null and undefined "
            "alike, rather than ||, which also swallows 0 and the empty string.",
            "How do you destructure with a rename and a default in one pattern?",
        ),
        _q(
            "How would you transform every value in an object?",
            "Turn it into entries, map them, and build it back: "
            "Object.fromEntries of the mapped Object.entries. For an object "
            "with a as 1 and b as 2, doubling the values gives a as 2 and b as "
            "4. Object.entries lists own enumerable string keys in order, and "
            "fromEntries accepts any iterable of pairs, so it also converts a "
            "Map to an object. Keys, values and entries all skip inherited and "
            "symbol keys. A for...of over the entries is the readable "
            "alternative when you need side effects or an early exit.",
            "What do you lose with this approach for symbol keys or getters?",
        ),
        _q(
            "Why does Array(3).map not do what you expect?",
            "Array(3) makes an array of length 3 with holes: the indexes do "
            "not exist at all. map, forEach and the other iteration methods "
            "skip holes, so the callback never runs and the result is still "
            "three holes. Array.from with a length object and a mapper builds "
            "a real array, giving 0, 1, 2, and so does filling first. Holes "
            "also make arrays slower, because engines fall back to a more "
            "generic representation. Avoid the Array constructor with a single "
            "number for the same reason.",
            "How do holes differ from undefined elements in for...in and forEach?",
        ),
    ),
)

_MODULES = Topic(
    id="js-modules-bundling",
    name="Modules, Bundling and Tree Shaking",
    order=170,
    languages=_JS,
    blurb="ESM versus CommonJS, dynamic import, what bundlers do and what defeats tree shaking.",
    questions=(
        _q(
            "How do ES modules differ from CommonJS?",
            "ES modules are static: import and export are declarations the "
            "engine can read before running anything, so the dependency graph "
            "and unused exports are known in advance. Their bindings are live, "
            "so an importer sees later changes in the exporter, while "
            "CommonJS require runs at call time and hands back whatever the "
            "exports held. ES modules load asynchronously and are always "
            "strict, with no require, module or __dirname. After an exporter "
            "increments a counter, the importer reads 1 before and 2 after.",
            "Can you require an ES module from CommonJS?",
        ),
        _q(
            "What does dynamic import do, and when would you use it?",
            "import() is a function-like expression that returns a promise for "
            "the module namespace, so it can be called conditionally, with a "
            "computed path, or long after load. Bundlers treat each one as a "
            "split point and emit a separate chunk fetched on demand. Use it "
            "for routes, for heavy libraries such as a chart or an editor "
            "behind a click, and for locale data. A default export comes back "
            "under the key default, so awaiting the import of a module that "
            "exports 5 gives m.default equal to 5.",
            "How do you stop a split chunk causing a visible loading flash?",
        ),
        _q(
            "What is tree shaking and what stops it?",
            "Tree shaking drops exports nothing imports, which works because "
            "import and export are static and a bundler can see which names "
            "are used. It stops when the analysis cannot prove removal is "
            "safe: modules with top-level side effects, CommonJS, which is "
            "dynamic, whole-namespace imports read with computed keys, and "
            "some barrel-file setups. Library authors help with the "
            "sideEffects field in package.json, which declares which files "
            "can be dropped whole, and by shipping ES modules. Check the "
            "bundle analyser rather than trusting it.",
            "Why can a barrel file make a bundle larger?",
        ),
        _q(
            "What does a bundler actually do, and why bundle if HTTP/2 exists?",
            "It starts from the entry points, follows the import graph, "
            "transforms files such as TypeScript, JSX and CSS, removes dead "
            "code, minifies, splits the result into chunks and names them with "
            "content hashes. HTTP/2 makes many requests cheap, but it does not "
            "remove the waterfall of discovering imports one level at a time, "
            "it compresses many small files worse than one, and it cannot do "
            "the transforms. So you still bundle, but into several "
            "well-cached chunks rather than one lump.",
            "What is the difference between a bundler and a dev server that serves native modules?",
        ),
        _q(
            "What is the difference between a default export and named exports?",
            "A default export is one unnamed value per module that the "
            "importer names itself; named exports are listed by name and must "
            "be imported by that name. Named exports are easier to "
            "tree-shake, give better editor auto-import and rename support, "
            "and stop two files calling the same thing different names. "
            "Defaults suit a module with one obvious job and are what lazy "
            "routes expect. The namespace object lists keys alphabetically, so "
            "a module exporting a and a default gives a then default.",
            "Why do some style guides ban default exports?",
        ),
        _q(
            "What are a transpiler and a polyfill, and how do they differ?",
            "A transpiler rewrites syntax the target does not understand into "
            "syntax it does, such as turning optional chaining or JSX into "
            "older code. A polyfill adds a missing runtime feature, such as "
            "Promise.allSettled, by defining it in JavaScript where the engine "
            "lacks it. Syntax cannot be polyfilled and runtime features cannot "
            "be transpiled, so a build usually needs both, driven by a list of "
            "the engines you support. Serving modern code to modern browsers "
            "and a legacy bundle to the rest keeps most users on the small one.",
            "How do you decide which browsers to support?",
        ),
        _q(
            "How does Node decide whether a file is an ES module or CommonJS?",
            "By extension and configuration: .mjs is always an ES module, "
            ".cjs is always CommonJS, and for a plain .js file the nearest "
            "package.json type field decides, which means CommonJS when it is "
            "absent. Recent Node versions will also detect module syntax in an "
            "ambiguous file, and can load a synchronous ES module with "
            "require. Mixing is the usual pain: an ES module can import "
            "CommonJS easily, but CommonJS loading an ES module needs import() "
            "or the newer require support, and __dirname is missing in ES "
            "modules.",
            "What replaces __dirname in an ES module?",
        ),
        _q(
            "What is a source map and what are the risks of shipping one?",
            "A source map is a file that maps positions in the minified or "
            "transpiled output back to the original files, lines and names, so "
            "DevTools and error trackers can show readable stack traces. The "
            "risk is that anyone who can fetch it can read your original "
            "source, comments included. Teams either upload maps privately to "
            "the error tracker and keep them off the public server, or accept "
            "the exposure for open code. Hidden maps are referenced by tooling "
            "rather than by a public comment in the bundle.",
            "How does an error tracker use a source map on an uploaded stack trace?",
        ),
        _q(
            "Why do content hashes in filenames plus chunk splitting speed up repeat visits?",
            "A file named from a hash of its contents never changes under that "
            "name, so it can be cached for a year as immutable. When you "
            "deploy, only files whose contents changed get new names, and the "
            "rest stay in the cache. Splitting vendor code from app code, and "
            "per-route code from the shared core, keeps most chunks stable "
            "between releases, so a small edit invalidates one small file. The "
            "entry HTML is the one thing not hashed, so it is revalidated and "
            "points at the current names.",
            "What goes wrong if two deploys overlap and an old page asks for a deleted chunk?",
        ),
        _q(
            "What does type=module change for a script in a page?",
            "The script is fetched and parsed as a module: deferred by "
            "default so it runs after the document is parsed, strict, with its "
            "own scope instead of making globals, able to import others, and "
            "fetched with CORS rules. A given module URL runs once however "
            "many places import it, so two imports of the same address leave "
            "a shared counter at 1. Import maps let you map bare names like "
            "lodash to URLs without a bundler. A nomodule script is the "
            "fallback for old browsers.",
            "What is the difference between defer and async on a classic script?",
        ),
        _q(
            "Why does importing a CSS file or a polyfill matter to tree shaking?",
            "Because importing for the effect, such as a stylesheet or a "
            "polyfill file, names no export the bundler can see being used, so "
            "it cannot tell whether dropping the file is safe. If a library "
            "says its files are free of side effects, the bundler can skip any "
            "module whose exports are unused, but a file that registers "
            "something on import must stay. That is why sideEffects lists the "
            "CSS and polyfill files rather than being set to false for the "
            "whole package. Marking a file wrongly shows up only in production "
            "builds.",
            "How would you notice that a build dropped a file that mattered?",
        ),
    ),
)

_DOM = Topic(
    id="js-dom-events",
    name="The DOM, Events and Delegation",
    order=180,
    languages=_JS,
    blurb="Bubbling, delegation, passive listeners, live versus static collections and script loading.",
    questions=(
        _q(
            "What are the capture and bubble phases of an event?",
            "An event travels in three steps: down from the window towards "
            "the target in the capture phase, then the target itself, then back "
            "up through the ancestors in the bubble phase. Listeners are on "
            "the bubble phase by default; pass capture: true to listen on the "
            "way down, which lets an ancestor see the event before the target "
            "does. Most events bubble, so a click on a child also reaches its "
            "parents, which is what delegation relies on. event.target is "
            "where it started and event.currentTarget is whose listener is "
            "running.",
            "Which common events do not bubble?",
        ),
        _q(
            "What is event delegation, and why use it?",
            "Attach one listener to a common ancestor instead of one per "
            "child, then use event.target to find which child was hit, "
            "typically with closest to cope with clicks on inner elements. It "
            "uses less memory for long lists, and it keeps working for "
            "elements added later, because the listener lives on a parent that "
            "never changes. The limits: the event must bubble, so focus and "
            "blur need focusin and focusout, a stopPropagation in a child "
            "breaks it, and you must check the match is inside the container.",
            "How does closest help when the click lands on an icon inside a button?",
        ),
        _q(
            "What is the difference between stopPropagation, stopImmediatePropagation and preventDefault?",
            "preventDefault cancels the browser's own action, such as "
            "following a link or submitting a form, but the event keeps "
            "travelling. stopPropagation stops the event reaching other "
            "elements on its path, but other listeners on the same element "
            "still run. stopImmediatePropagation also stops the remaining "
            "listeners on the same element. They are independent, and "
            "returning false from an addEventListener handler does nothing. "
            "Overusing stopPropagation breaks analytics and delegation, and "
            "preventDefault only works on cancelable events.",
            "What do you need to know about preventDefault in a passive listener?",
        ),
        _q(
            "Which events do not bubble, and how do you delegate them?",
            "focus, blur, load, mouseenter, mouseleave and scroll on elements "
            "do not bubble. For focus there are focusin and focusout, which do "
            "bubble, and mouseover and mouseout stand in for the enter and "
            "leave pair. Alternatively listen in the capture phase on an "
            "ancestor, because capture happens whether or not the event "
            "bubbles. An event's bubbles property says which kind you have, and "
            "a custom event only bubbles if you ask for it in its options.",
            "Why does mouseover fire again as the pointer moves over children?",
        ),
        _q(
            "What is a passive event listener?",
            "A listener registered with passive: true promises not to call "
            "preventDefault, so the browser can scroll or zoom immediately "
            "without waiting for your code. Without that promise a touch or "
            "wheel listener forces the browser to wait and see whether the "
            "page will cancel the scroll, which shows up as scroll jank. If a "
            "passive listener calls preventDefault anyway the call is ignored "
            "and the console warns. Browsers make wheel and touch listeners on "
            "the window, document and body passive by default, but not "
            "elsewhere.",
            "When would you need a non-passive touchmove handler?",
        ),
        _q(
            "How do you remove an event listener correctly, and what is AbortController's role?",
            "removeEventListener needs the same function reference and the "
            "same capture flag you added with, so an inline arrow cannot be "
            "removed. Adding the same function twice registers it once. "
            "Options help: once removes a listener after its first call, and a "
            "signal option removes it when an AbortController aborts, which "
            "cleans up many listeners with one call. On an EventTarget, adding "
            "the same function twice, dispatching, removing it and "
            "dispatching again prints hit only once.",
            "What leaks if a component adds a window listener in its setup and never removes it?",
        ),
        _q(
            "What is the difference between querySelectorAll and getElementsByClassName?",
            "querySelectorAll returns a static NodeList, a snapshot of the "
            "matches at that moment, and takes any CSS selector. "
            "getElementsByClassName and getElementsByTagName return a live "
            "HTMLCollection that updates as the document changes, so a loop "
            "that adds or removes matching elements skips or repeats items. "
            "The live collection is cheap to create and the static one is "
            "easier to reason about. Neither is an array, so spread them or "
            "use Array.from to get map and filter.",
            "What bug can appear when you remove elements while looping over a live collection?",
        ),
        _q(
            "textContent, innerText or innerHTML: which do you use?",
            "textContent sets or reads raw text and never parses markup, so it "
            "is the safe default and the fastest. innerText respects styling, "
            "so it skips hidden text and triggers layout, and is rarely what "
            "you want. innerHTML parses a string as HTML, which is an XSS hole "
            "if any part came from a user, and it replaces the whole subtree, "
            "dropping listeners on the children. For structured output build "
            "nodes with createElement, template elements or a framework, and "
            "sanitise any HTML you must accept.",
            "Is a script tag set through innerHTML dangerous, and what about an image with onerror?",
        ),
        _q(
            "What is the difference between DOMContentLoaded and load, and between defer and async?",
            "DOMContentLoaded fires when the HTML is parsed and deferred "
            "scripts have run, without waiting for images or stylesheets; load "
            "fires after everything has loaded. A classic script blocks the "
            "parser while it downloads and runs. async downloads in parallel "
            "and runs as soon as it arrives, in no guaranteed order, which "
            "suits independent scripts such as analytics. defer downloads in "
            "parallel and runs in order after parsing, before "
            "DOMContentLoaded, which suits app code. Module scripts are "
            "deferred by default.",
            "Where does a script at the bottom of the body fit compared with defer?",
        ),
        _q(
            "How do custom events let components talk without knowing each other?",
            "A component dispatches a CustomEvent with a name and a detail "
            "payload, and anyone who cares listens for it on the element or an "
            "ancestor. The dispatcher knows nothing about the listener, which "
            "keeps coupling low. The event only bubbles if you pass bubbles, "
            "and crosses a shadow DOM boundary only if composed is set too. A "
            "listener reading event.detail gets exactly the payload, so a "
            "dispatched detail of 42 arrives as 42. EventTarget works without "
            "any DOM, which makes it a tiny event bus.",
            "When would you choose a custom event over passing a callback prop?",
        ),
        _q(
            "What does the browser do between receiving HTML and showing something, and what blocks it?",
            "It parses the HTML into the DOM incrementally, and a preload "
            "scanner looks ahead to start fetching resources early. A classic "
            "script without defer or async stops the parser until it has been "
            "fetched and run, and it also waits for any stylesheets before it, "
            "because it might read styles. CSS blocks rendering, though not "
            "parsing, since showing unstyled content would flash. So the fixes "
            "are small critical CSS, defer on scripts, and the resources that "
            "matter early in the HTML.",
            "What is the difference between preload and prefetch?",
        ),
    ),
)

_RENDERING = Topic(
    id="web-rendering-performance",
    name="Rendering and Web Performance",
    order=190,
    blurb="Reflow, compositing, requestAnimationFrame, debounce, Core Web Vitals and leaks.",
    questions=(
        _q(
            "Can you walk me through the critical rendering path?",
            "The browser parses HTML into the DOM and CSS into the CSSOM, "
            "combines them into a render tree of visible boxes, then runs "
            "layout to work out each box's size and position, paint to fill in "
            "pixels, and compositing to stack layers on the GPU. Scripts can "
            "block parsing, and CSS blocks rendering. Optimising it means fewer "
            "and smaller blocking resources, a little critical CSS first, and "
            "avoiding forced layouts so that later frames only need the "
            "cheaper steps.",
            "Which steps does a change to transform skip, compared with a change to width?",
        ),
        _q(
            "What is the difference between reflow and repaint, and what triggers a reflow?",
            "Reflow, or layout, recomputes geometry: the sizes and positions "
            "of the affected elements and often their children and "
            "neighbours. Repaint redraws pixels when only appearance "
            "changes, such as a colour. Changing width, adding an element or "
            "changing font size triggers layout and then paint, while a "
            "colour change triggers only paint. Reading geometry such as "
            "offsetHeight right after a write forces layout immediately, so "
            "interleaving reads and writes in a loop is layout thrashing: "
            "batch all the reads, then all the writes.",
            "How would you find which line of code causes forced layouts?",
        ),
        _q(
            "Why are transform and opacity cheap to animate?",
            "They can be applied by the compositor on the GPU to an already "
            "painted layer, without redoing layout or paint and without the "
            "main thread once the animation starts. Animating width, top or "
            "margin forces layout every frame, and animating a colour forces "
            "repaints. So move things with transform and fade with opacity. "
            "will-change hints that a layer is coming, but each layer costs "
            "memory, so use it sparingly and remove it afterwards. Prefer CSS "
            "animations or the Web Animations API.",
            "When is a compositing layer a cost rather than a win?",
        ),
        _q(
            "Why use requestAnimationFrame instead of setTimeout for animation?",
            "requestAnimationFrame runs just before the next repaint, in step "
            "with the display, so you do work once per frame and never produce "
            "frames that are not shown. A timer fires at its own pace and "
            "drifts against the refresh, so frames are dropped or computed "
            "twice. It also pauses in background tabs, saving battery, and "
            "passes a timestamp you can use to scale movement by elapsed time. "
            "Do your DOM writes in the callback after reading layout. It is "
            "one-shot, so request again each frame.",
            "How does the callback behave on a 144 Hz display, and how do you stay frame-rate independent?",
        ),
        _q(
            "What is the difference between debounce and throttle, and how would you implement both?",
            "Debounce waits for quiet: each call resets a timer, and the "
            "function runs once after calls stop, so three rapid calls produce "
            "one run. It suits search boxes and resize handlers. Throttle "
            "limits the rate: the function runs at most once per interval "
            "however many calls arrive, which suits scroll and mousemove. A "
            "leading-edge throttle runs the first call straight away and "
            "ignores the rest until the window passes. Both are closures over a "
            "timer or a timestamp, and both need cancelling when the "
            "component goes away.",
            "What do you do about the trailing call that a leading-edge throttle drops?",
        ),
        _q(
            "What are the Core Web Vitals, and what are good values?",
            "Three field metrics for user experience. Largest Contentful Paint "
            "measures when the main content appears, and 2.5 seconds or less "
            "is good. Cumulative Layout Shift measures unexpected movement of "
            "the page, and 0.1 or less is good. Interaction to Next Paint "
            "measures how fast the page responds to clicks, taps and keys over "
            "the whole visit, and 200 milliseconds or less is good, all at the "
            "75th percentile of real page loads. INP replaced First Input "
            "Delay in 2024, because that only looked at the first interaction.",
            "Why can a lab test pass while the field data fails?",
        ),
        _q(
            "How do memory leaks happen in a browser app, and how do you find one?",
            "A leak is memory that stays reachable though nothing needs it. "
            "The usual causes are event listeners and timers never removed, "
            "closures holding big objects, detached DOM nodes still referenced "
            "from a variable or cache, and ever-growing global arrays or maps. "
            "To find one, take a heap snapshot, repeat the action a few times, "
            "take another and compare, looking for detached elements and "
            "objects whose count keeps growing. A memory graph that never "
            "returns to its baseline is the symptom. AbortController, WeakMap "
            "and cleanup functions prevent most of them.",
            "Why does a leak matter more in a single-page app than on a traditional site?",
        ),
        _q(
            "How would you render a list of ten thousand rows?",
            "Do not render them all. Virtualise: keep only the rows near the "
            "viewport in the DOM, inside a container with the full scroll "
            "height, and move them as the user scrolls. With 40 pixel rows and "
            "a 600 pixel window scrolled to 1234, the first visible row is 30 "
            "and about 16 rows are needed counting a spare. Add overscan to "
            "avoid blank flashes. Alternatives are pagination, infinite scroll "
            "with an IntersectionObserver, or content-visibility: auto to skip "
            "offscreen sections. Variable heights need measuring and caching.",
            "What breaks for Ctrl+F and accessibility in a virtualised list?",
        ),
        _q(
            "How do you load images and fonts without hurting the page?",
            "Give images a width and height, or an aspect ratio, so the layout "
            "does not shift when they arrive. Serve the right size with srcset "
            "and modern formats, lazy-load below-the-fold images, and never "
            "lazy-load the main hero, which should be prioritised with "
            "fetchpriority or a preload. For fonts, subset them, preload the "
            "ones used above the fold, and use font-display swap or optional to "
            "avoid invisible text. The hero is about LCP and the dimensions are "
            "about CLS.",
            "What is the trade-off between font-display swap and optional?",
        ),
        _q(
            "How do you keep heavy work off the main thread?",
            "Move it to a Web Worker, which has its own thread and "
            "communicates by messages. Messages are copied with structured "
            "clone, which is slow for large data, so transfer buffers "
            "instead: after transferring an ArrayBuffer of 8 bytes its length "
            "on the sender is 0 and on the receiver 8, because ownership "
            "moved. OffscreenCanvas lets a worker draw. For work that must "
            "touch the DOM, chunk it and yield, or use requestIdleCallback. "
            "Libraries such as Comlink hide the messaging. Do not spawn a "
            "worker for tiny jobs.",
            "When does SharedArrayBuffer beat transferring, and what does it require?",
        ),
        _q(
            "How do you measure performance honestly?",
            "Use both lab and field data. Lab tools such as Lighthouse and the "
            "DevTools Performance panel give repeatable traces on a throttled "
            "device and tell you why something is slow. Field data from real "
            "users, collected with PerformanceObserver or a monitoring "
            "service, tells you whether it matters to people on slow phones "
            "and bad networks, and is what the Core Web Vitals are judged on. "
            "Look at the 75th percentile, not the mean, test on a mid-range "
            "device, and time code with performance.now rather than Date.now.",
            "How would you set a performance budget and enforce it in CI?",
        ),
    ),
)

_SECURITY = Topic(
    id="web-security-storage",
    name="Web Security, Cookies and CORS",
    order=200,
    blurb="Same-origin, CORS, XSS, CSRF, cookie flags, where to keep a token, CSP.",
    questions=(
        _q(
            "What is the same-origin policy?",
            "An origin is the scheme, host and port together, and the policy "
            "stops a page from one origin reading data from another: scripts "
            "cannot read cross-origin responses or reach into another origin's "
            "frames and storage. https://a.com and https://a.com:443 are the "
            "same origin, since 443 is the default, while http and https "
            "differ, as do a.com and sub.a.com. It restricts reading, not "
            "sending: a page can still make a cross-origin request or load an "
            "image, and only the response is hidden from its scripts. CORS is "
            "the controlled exception.",
            "What do site and origin mean differently for cookies?",
        ),
        _q(
            "What is CORS, and what does it not protect?",
            "Cross-Origin Resource Sharing is how a server tells the browser "
            "which other origins may read its responses, by sending "
            "Access-Control-Allow-Origin. The browser enforces it, not the "
            "server: a request from a disallowed origin can still arrive and "
            "run, and only the page's script is denied the answer. So CORS "
            "protects users' browsers, not your API. It does nothing against "
            "curl, and a form post still reaches the server, so you need CSRF "
            "defences and authentication anyway. Never reflect the Origin "
            "header blindly.",
            "Why does the error appear in the browser when the server logged a successful request?",
        ),
        _q(
            "What is a CORS preflight, and when does one happen?",
            "A preflight is an OPTIONS request the browser sends first to ask "
            "permission before a request that could have side effects. A "
            "request skips it only if it is simple: a GET, HEAD or POST with "
            "only safelisted headers and a content type of form-urlencoded, "
            "multipart or text/plain. A JSON POST, an Authorization header, or "
            "a PUT or DELETE triggers one. The server answers with the allowed "
            "methods and headers, and Access-Control-Max-Age lets the browser "
            "cache that. A credentialed request cannot use a wildcard origin.",
            "How would you reduce the preflight cost on a chatty API?",
        ),
        _q(
            "What is XSS, and how do you defend against it?",
            "Cross-site scripting is when attacker-supplied text ends up in "
            "your page as executable code, which then runs with your site's "
            "powers: it can read the DOM, call your API as the user and steal "
            "anything not HttpOnly. It comes in stored, reflected and "
            "DOM-based forms, the last being client code that writes input "
            "into a sink such as innerHTML. Defend in layers: encode output for "
            "its context, prefer textContent, sanitise any HTML you must "
            "allow, set a Content Security Policy, and mark session cookies "
            "HttpOnly. Frameworks escape by default, so watch their escape "
            "hatches.",
            "What is the difference between escaping on input and escaping on output?",
        ),
        _q(
            "What is CSRF, and how do SameSite cookies and tokens stop it?",
            "Cross-site request forgery makes the victim's browser send a "
            "request to your site from another page, and the browser attaches "
            "the user's cookies, so the server thinks the user did it. "
            "Defences: SameSite cookies, where Lax, the default in current "
            "browsers, withholds cookies from cross-site subrequests and "
            "non-GET navigations; an anti-forgery token that a forged page "
            "cannot read; and checking Origin or a custom header on "
            "state-changing requests. GET must never change state. Bearer "
            "tokens in headers are not sent automatically, so they are not "
            "CSRF-prone.",
            "Does CORS stop CSRF?",
        ),
        _q(
            "What do the HttpOnly, Secure and SameSite cookie attributes do?",
            "HttpOnly hides the cookie from document.cookie, so an XSS attack "
            "cannot read the session id, though it can still make requests "
            "that carry it. Secure sends the cookie only over HTTPS. SameSite "
            "controls cross-site sending: Strict only on same-site requests, "
            "Lax also on top-level navigations such as clicked links, and None "
            "on all requests but only together with Secure. Domain widens a "
            "cookie to subdomains, and omitting it keeps it to the exact host. "
            "A session cookie should be HttpOnly, Secure and at least Lax.",
            "Why is a cookie scoped to the parent domain riskier?",
        ),
        _q(
            "localStorage, sessionStorage, cookies or IndexedDB: how do you choose?",
            "Cookies travel with every request and are capped at roughly 4 KB, "
            "so they suit what the server needs, like a session id. "
            "localStorage keeps strings per origin until cleared, "
            "synchronously and readable by any script on the page, so it suits "
            "small preferences and never secrets. sessionStorage is the same "
            "but scoped to the tab and gone when it closes. IndexedDB is "
            "asynchronous and holds large structured data, blobs included, so "
            "it suits offline data. Storage can be cleared at any time, so "
            "treat it as a cache.",
            "Why is the synchronous API of localStorage a performance concern?",
        ),
        _q(
            "Should a JWT live in localStorage or in a cookie?",
            "It is a trade between two attacks. In localStorage any injected "
            "script can read the token and take it away, so XSS leaks the "
            "credential for good. In an HttpOnly cookie script cannot read "
            "it, but the browser attaches it automatically, so you need "
            "SameSite and CSRF protection. Most advice favours an HttpOnly, "
            "Secure, SameSite cookie, with short-lived access tokens and "
            "rotating refresh tokens, or a server-side session if you can "
            "afford one. A JWT is signed, not encrypted: anyone can read its "
            "payload, so keep secrets out.",
            "How do you revoke a JWT before it expires?",
        ),
        _q(
            "What is a Content Security Policy and how does a nonce work?",
            "CSP is a response header that tells the browser which sources of "
            "scripts, styles, images and frames it may use, so injected inline "
            "script is refused even if it reaches the page. A strict policy "
            "skips domain allowlists and instead gives each legitimate script "
            "a random nonce, regenerated on every response, so only tags "
            "carrying the matching nonce run. It also disables eval unless you "
            "opt in. Roll it out in report-only mode first, since inline "
            "handlers and third-party tags usually break. It limits the damage "
            "from XSS rather than replacing escaping.",
            "Why is allowlisting a CDN domain in script-src weaker than a nonce?",
        ),
        _q(
            "What is clickjacking and how do you prevent it?",
            "Clickjacking loads your page in a transparent iframe on the "
            "attacker's site, positioned so the user's click lands on one of "
            "your buttons while they think they are clicking something else. "
            "The defence is to tell browsers who may frame you: the "
            "Content-Security-Policy frame-ancestors directive, or the older "
            "X-Frame-Options header. Setting frame-ancestors to none or self "
            "blocks cross-site framing entirely. Sensitive actions can also "
            "demand re-authentication, though framing control is the main fix.",
            "How do you let one partner embed your widget while blocking everyone else?",
        ),
        _q(
            "How do you use third-party scripts safely?",
            "Treat each one as code with full access to your page. Load as "
            "few as possible, from sources you trust, and pin versions rather "
            "than pointing at latest. Use Subresource Integrity, an integrity "
            "attribute holding a hash of the expected file, so a tampered CDN "
            "copy is refused. Add a CSP that limits where scripts can load "
            "from, isolate untrusted widgets in a sandboxed iframe, load tags "
            "async so they cannot block the page, and review them regularly. "
            "Tag managers are a common way for scripts to arrive unreviewed.",
            "What happens to SRI when a third party updates the file in place?",
        ),
    ),
)

_HTTP = Topic(
    id="web-http-fetch-caching",
    name="HTTP, fetch and Caching",
    order=210,
    blurb="Methods and status codes, Cache-Control and ETag, fetch errors, HTTP versions and API design.",
    questions=(
        _q(
            "What happens when you type a URL into the browser and press Enter?",
            "The browser parses the URL and checks its caches, then resolves "
            "the host name to an IP address through DNS. It opens a TCP "
            "connection, or a QUIC one for HTTP/3, negotiates TLS, and sends "
            "an HTTP request. The server answers, possibly after redirects, "
            "and the browser starts parsing the HTML, fetching the CSS, "
            "scripts and images it finds, building the DOM and CSSOM, and "
            "rendering. Cached resources and connection reuse skip most of "
            "the early steps, and a CDN shortens the distance to the server.",
            "Which of those steps can you speed up from the front end, and how?",
        ),
        _q(
            "Which HTTP methods are safe and which are idempotent?",
            "Safe means it does not change server state: GET, HEAD and "
            "OPTIONS. Idempotent means repeating it has the same effect as "
            "doing it once: those, plus PUT and DELETE, because setting a "
            "value or deleting a thing twice leaves the same end state. POST "
            "is neither and PATCH need not be. It matters because a client or "
            "proxy may retry idempotent requests automatically after a "
            "timeout, whereas retrying a POST can create a duplicate order. "
            "Responses to GET can be cached; most others cannot.",
            "How do you make a POST safe to retry?",
        ),
        _q(
            "Which status codes should you know, and how do you choose between them?",
            "2xx is success: 200 for a body, 201 for a created resource, 204 "
            "for success with nothing to return. 3xx is redirects: 301 and "
            "308 are permanent, 302 and 307 temporary, with 307 and 308 "
            "keeping the method; 304 means use your cached copy. 4xx blames "
            "the client: 400 malformed, 401 missing or bad credentials, 403 "
            "known but not allowed, 404 not found, 409 conflict, 429 too many "
            "requests. 5xx blames the server: 500, 502 from a bad upstream, 503 "
            "for overload.",
            "When would you return 404 instead of 403 for something the user may not see?",
        ),
        _q(
            "What do the Cache-Control directives no-cache, no-store and max-age mean?",
            "max-age says a response is fresh for that many seconds, so the "
            "browser reuses it without asking. no-cache is badly named: the "
            "response may be stored but must be revalidated with the server "
            "before each reuse. no-store forbids keeping it at all, for "
            "sensitive data. private limits it to the user's own browser, "
            "public allows shared caches such as a CDN, and immutable says it "
            "will not change while fresh. Use no-cache for HTML so the page "
            "is always current, and a long max-age for fingerprinted assets.",
            "What is stale-while-revalidate and when does it help?",
        ),
        _q(
            "How do ETag and conditional requests work?",
            "The server labels a version of a resource with an ETag, a "
            "validator such as a hash. When the cached copy goes stale, the "
            "browser asks again with If-None-Match carrying that value. If "
            "nothing changed the server replies 304 Not Modified with no body, "
            "and the browser reuses what it has, saving the transfer but not "
            "the round trip. If it changed, the server sends 200 with the new "
            "body. Last-Modified with If-Modified-Since is the date-based "
            "version, and a strong ETag changes on any byte difference.",
            "Why might servers behind a load balancer break ETag caching?",
        ),
        _q(
            "How do you cache static assets and HTML together without serving stale pages?",
            "Fingerprint the assets: put a content hash in each filename, so "
            "a changed file gets a new URL. Then give those files a year-long "
            "max-age with immutable, because the URL itself tells the browser "
            "when it is new. Serve the HTML with no-cache, so it is "
            "revalidated cheaply every time and points at the current hashed "
            "names. Deploying then needs no purge: a new page references new "
            "URLs and old ones age out. Without hashing you must keep "
            "lifetimes short or purge CDNs.",
            "How do you handle a user whose open tab still references the old file names?",
        ),
        _q(
            "Why does fetch not reject on a 404, and how do you handle errors?",
            "fetch only rejects when the request itself fails, such as a "
            "network error, a blocked CORS response or an abort. An HTTP error "
            "status is a successful exchange, so the promise resolves with "
            "response.ok false and the status set. You check response.ok "
            "yourself and throw, then catch both kinds in one place. Parsing "
            "can fail separately, since json() rejects on a bad body. Against "
            "a local server that returns 404, ok is false and status is 404, "
            "and nothing rejected.",
            "How would you wrap fetch so every caller gets consistent errors?",
        ),
        _q(
            "How do you cancel a fetch, and what race does that prevent?",
            "Pass an AbortSignal in the options and call abort on its "
            "controller; the promise rejects with an AbortError. In "
            "search-as-you-type, responses can arrive out of order, so a slow "
            "answer for an old query overwrites a newer one. Aborting the "
            "previous request when a new keystroke arrives, or ignoring "
            "responses whose id is no longer the latest, makes the last "
            "request win. Aborting stops the client waiting and usually closes "
            "the connection, but the server may still do the work.",
            "What happens to the server's work when the client aborts?",
        ),
        _q(
            "What changed from HTTP/1.1 to HTTP/2 and HTTP/3?",
            "HTTP/1.1 handles one request at a time per connection, so "
            "browsers open several and work around it by bundling. HTTP/2 "
            "multiplexes many requests over one connection as binary frames "
            "and compresses headers, but it still rides on TCP, so one lost "
            "packet stalls every stream. HTTP/3 runs over QUIC on UDP, with "
            "streams that fail independently, a combined transport and TLS "
            "handshake that is quicker to set up, and connection migration "
            "when you change networks. The methods and status codes are the "
            "same throughout.",
            "Does HTTP/2 make bundling pointless?",
        ),
        _q(
            "Design a paginated list endpoint: offset or cursor?",
            "Offset pagination, with page and limit, is simple and lets users "
            "jump to page 40, but it gets slow deep into a table, and rows "
            "shift when items are inserted or deleted, so users see "
            "duplicates or skip items. Cursor pagination returns an opaque "
            "token for the position after the last item, and the next "
            "request asks for items after it; it is stable and fast with an "
            "index, but you cannot jump to a page. Return the cursor, a "
            "has-more flag and a stable sort order, and cap the limit.",
            "How does a cursor stay correct when the sort key is not unique?",
        ),
        _q(
            "How do you make a POST safe to retry?",
            "Have the client generate an idempotency key, a unique id sent in "
            "a header, and have the server store the key with the result of "
            "the first execution. A retry with the same key returns the stored "
            "result instead of repeating the work, so a payment timeout cannot "
            "charge twice. Keys need an expiry, scoping per user, and a check "
            "that the retried body matches. It matters because networks lose "
            "responses as well as requests, so a client cannot know whether "
            "the first attempt succeeded.",
            "What should happen if the same key arrives while the first request is still running?",
        ),
        _q(
            "WebSockets, server-sent events or polling: how do you choose?",
            "Polling asks repeatedly and is the simplest, but wastes requests "
            "and adds latency. Server-sent events keep one HTTP response open "
            "and let the server stream text events to the browser, with "
            "automatic reconnection; they are one-way and work through "
            "ordinary HTTP infrastructure. WebSockets give a full-duplex "
            "connection after an HTTP upgrade, suited to chat, games and "
            "collaborative editing, at the cost of handling reconnection, "
            "heartbeats and scaling stateful connections yourself. For "
            "notifications start with SSE; for low-latency two-way traffic, "
            "WebSockets.",
            "How do you scale WebSocket servers across several machines?",
        ),
    ),
)

_TESTING = Topic(
    id="web-testing-tooling",
    name="Testing and Tooling",
    order=220,
    blurb="The pyramid, flaky tests, mocks, async and time, coverage, linters and CI.",
    questions=(
        _q(
            "What is the test pyramid, and where does the testing trophy disagree?",
            "The pyramid says to write many fast unit tests, fewer "
            "integration tests and very few slow end-to-end tests, because "
            "cost and flakiness rise as you go up. The trophy, popular in "
            "front-end work, argues that most of the value is in integration "
            "tests that render components together and use them as a user "
            "would, with static checks such as types and linting at the base "
            "and a few end-to-end tests on top. Both agree on the principle: "
            "the more a test resembles real usage, the more it proves, and "
            "the more it costs.",
            "Which layer would you add first to an untested application?",
        ),
        _q(
            "What makes a test flaky, and how do you fix it?",
            "A flaky test passes and fails with no code change, which means it "
            "depends on something it does not control: timing and sleeps, "
            "shared state left by another test, ordering, a real network or "
            "clock, randomness, or animations. Fix the cause rather than "
            "adding retries: wait for a condition, not a duration, reset "
            "state for every test, fake the clock and the network, and seed "
            "random data. Track flaky tests and quarantine them quickly, "
            "because a suite people do not trust gets ignored.",
            "How do you find which earlier test is polluting a later one?",
        ),
        _q(
            "What is the difference between a mock, a stub, a spy and a fake?",
            "A stub returns canned answers so the code under test can run. A "
            "spy wraps a real or fake function and records how it was "
            "called. A mock is a stub or spy with expectations built in, such "
            "as that it must be called once with certain arguments. A fake is "
            "a working but simplified implementation, such as an in-memory "
            "database. Prefer fakes and real code at the edges you own, and "
            "mock only what is slow or outside your control, because heavy "
            "mocking ties tests to implementation details.",
            "When does over-mocking let a test pass while the feature is broken?",
        ),
        _q(
            "How do you test code that depends on time or randomness?",
            "Make the dependency an input. Inject the clock, or use fake "
            "timers that let a test advance time instantly, and pass a "
            "seeded random generator, so the same seed gives the same "
            "sequence every run. Then a test can assert exact outcomes: a "
            "debounced function runs once after the delay, a retry waits the "
            "expected backoff, a shuffle with a fixed seed always gives the "
            "same order. Never sleep for real in a test, and avoid asserting "
            "on the current date.",
            "How would you test a debounce function without waiting for real time?",
        ),
        _q(
            "How do you test asynchronous code?",
            "Return or await the promise so the test runner waits for it; a "
            "test that does not will finish before the assertion runs. For "
            "events and timers, either wait for the specific condition with a "
            "polling helper that has a timeout, or use fake timers and advance "
            "them. Assert on rejections explicitly, with an await inside a try "
            "block or an assertion helper for rejects, since a silently "
            "unhandled one can hide the failure. Keep the timeout short, so a "
            "hung promise fails fast.",
            "Why can a test that forgets to await still appear green?",
        ),
        _q(
            "What should a component test check?",
            "Behaviour a user can see: render the component, interact with it "
            "the way a person would, finding elements by role, label or text "
            "rather than class names or internal state, and assert on what "
            "appears. That survives refactors, because it does not care how the "
            "component is built, and it nudges you towards accessible markup, "
            "since you find elements by their accessible role. Snapshot tests "
            "of large trees are brittle and tend to be approved without "
            "reading. Test internals only for logic worth isolating.",
            "What do you do about a component that calls the network?",
        ),
        _q(
            "What does code coverage tell you, and what does it not?",
            "Coverage shows which lines or branches ran during the tests. Low "
            "coverage in an area proves it is untested, which is useful. High "
            "coverage proves much less: a test can execute every line and "
            "assert nothing. It also cannot see missing code, such as an "
            "unhandled case. Treat it as a map of blind spots, not a target, "
            "because a hard percentage invites tests written to move the "
            "number. Mutation testing is a stronger check: it changes the code "
            "and sees whether any test fails.",
            "How does mutation testing expose a weak test that coverage approves?",
        ),
        _q(
            "What is the difference between a linter, a formatter and a type checker?",
            "A formatter such as Prettier only rearranges layout, so style "
            "arguments disappear. A linter such as ESLint reads the syntax "
            "tree for suspicious or inconsistent code, such as unused "
            "variables, missing awaits or assignment in a condition, with "
            "rules you configure and some it can fix. A type checker such as "
            "TypeScript reasons about values flowing through the program and "
            "catches mismatches before running it. They overlap little, so "
            "teams use all three, in the editor, in a pre-commit hook and in "
            "CI, which is the one that cannot be skipped.",
            "Which linter rules would you turn on for async code?",
        ),
        _q(
            "What is property-based testing, and when is it better than examples?",
            "Instead of hand-picked examples you state a rule that must always "
            "hold, and the framework generates many random inputs, then "
            "shrinks a failing one to the smallest case. Reversing an array "
            "twice must give back the original, whatever the array, so a "
            "test checks that over a hundred random arrays. It finds edge "
            "cases you did not think of, such as empty input, negative zero or "
            "odd unicode, and suits parsers, serialisers, sorting and "
            "anything with an inverse or an invariant. It is a poor fit for UI "
            "flows.",
            "What are good properties for a function that sorts?",
        ),
        _q(
            "What should a continuous integration pipeline run on every push?",
            "Fast checks first and in parallel: install from a cached "
            "lockfile, lint, type-check and unit tests, then build and "
            "integration tests, then the slower end-to-end suite, perhaps "
            "only on main or before merge. It should fail on the first red, "
            "run in a clean environment so it matches nobody's laptop "
            "quirks, and finish in minutes, because a slow pipeline trains "
            "people to batch changes. Add dependency audits, bundle size "
            "checks and preview deployments. The goal is that main is always "
            "releasable.",
            "How do you keep a slow end-to-end suite from blocking every pull request?",
        ),
        _q(
            "What does test-driven development give you, and when is it a poor fit?",
            "You write a failing test first, make it pass with the simplest "
            "code, then refactor, which keeps functions small, makes you "
            "design the interface before the implementation, and leaves a "
            "safety net. It works best for logic with clear inputs and "
            "outputs, for bug fixes, where the failing test reproduces the "
            "bug first, and for well-understood domains. It fits poorly for "
            "exploratory work, visual design and spikes where you do not yet "
            "know what to build. Many teams use it selectively.",
            "How do you write the first test when the interface is not obvious?",
        ),
    ),
)

_NODE = Topic(
    id="node-internals",
    name="Node.js Internals",
    order=230,
    languages=_JS,
    blurb="libuv and the thread pool, loop phases, nextTick, streams, workers and shutdown.",
    questions=(
        _q(
            "Node is single-threaded, so how does it handle thousands of connections?",
            "Your JavaScript runs on one thread, but it does not wait on I/O: "
            "network sockets are handed to the operating system's readiness "
            "mechanism, such as epoll, kqueue or IOCP, through libuv, and the "
            "thread picks up callbacks when data is ready. Work with no async "
            "OS interface, such as file system calls, DNS lookups and "
            "compression, runs on libuv's thread pool, which has four threads "
            "by default and can be changed with UV_THREADPOOL_SIZE. So "
            "I/O-bound servers scale well, while a CPU-bound handler blocks "
            "everyone.",
            "What happens to a second request while a first one runs a heavy loop?",
        ),
        _q(
            "What are the phases of Node's event loop?",
            "Each turn runs timers whose delay has expired, then pending "
            "callbacks for some system errors, then the poll phase, which "
            "fetches new I/O events, runs their callbacks and may block "
            "waiting for them, then the check phase for setImmediate "
            "callbacks, and finally close callbacks. Inside an I/O callback "
            "setImmediate always beats a zero-delay setTimeout, because check "
            "comes right after poll, while from the main module the order "
            "depends on process speed. process.nextTick and promise callbacks "
            "run between phases.",
            "Why is the order of setTimeout 0 and setImmediate not fixed from the main module?",
        ),
        _q(
            "What is the order of process.nextTick, promises and setImmediate?",
            "After the current operation finishes, Node drains the nextTick "
            "queue first, then the promise microtask queue, and only then "
            "moves on to the loop's phases, where setImmediate lives. So in "
            "the main script a synchronous log comes first, then nextTick, "
            "then the promise, then setImmediate. nextTick is Node-only and "
            "outranks promises, which is why a recursive nextTick can starve "
            "I/O. Prefer queueMicrotask or promises for ordinary deferral and "
            "keep nextTick for library code that needs exact ordering.",
            "What happens if a nextTick callback schedules another nextTick for ever?",
        ),
        _q(
            "What are streams, and what is backpressure?",
            "A stream processes data in chunks instead of loading it all, so a "
            "gigabyte file can be piped to a response using a few kilobytes of "
            "memory. There are readable, writable, duplex and transform "
            "streams. Backpressure is the signal that a consumer is slower "
            "than the producer: write returns false when its buffer is full, "
            "and the producer should pause until the drain event. pipeline "
            "handles that and cleans up on errors. Readable streams are async "
            "iterable, so a for await loop over one that yields a, b and c "
            "gives abc.",
            "What goes wrong if you ignore the return value of write?",
        ),
        _q(
            "When do you use worker threads, cluster or child processes?",
            "Worker threads run JavaScript in parallel inside one process, "
            "each with its own event loop and heap, and are the tool for "
            "CPU-heavy work such as image processing or parsing, passing "
            "messages or sharing memory. Cluster, or simply several processes "
            "behind a load balancer, copies the whole server to use every core "
            "for request throughput; the copies share nothing except what you "
            "put in a database or cache. A child process runs a different "
            "program, isolated, such as ffmpeg. A worker's message reaches the "
            "main thread as an ordinary event.",
            "How do you share state between cluster workers?",
        ),
        _q(
            "What does it mean to block the event loop, and how do you find it?",
            "Any synchronous work that takes long, such as a huge JSON.parse, "
            "synchronous file or crypto calls, a catastrophic regular "
            "expression or a big loop, stops the one thread serving anything "
            "else, so every request's latency rises together. A timer due in "
            "zero milliseconds cannot fire until a 50 millisecond busy loop "
            "finishes, so blocked prints before timer. Find it by measuring "
            "event loop delay with perf_hooks, profiling with the inspector, "
            "and watching p99 latency. Fix it by chunking, async APIs, "
            "workers, or a better algorithm.",
            "What is a ReDoS, and how would you defend against it?",
        ),
        _q(
            "How do strings, bytes and Buffers relate?",
            "A JavaScript string is a sequence of UTF-16 code units, while "
            "network and file data are bytes, so an encoding decides how you "
            "cross between them. In UTF-8 the letter e with an acute accent is "
            "one string character but two bytes, and the grinning face emoji "
            "is two code units, four bytes and one code point. So its length "
            "is 2, Buffer.byteLength gives 4, and spreading it gives one item. "
            "A Buffer is a fixed-size byte array, and a multi-byte character "
            "split across chunks is corrupted unless you use StringDecoder or "
            "setEncoding.",
            "What happens if you read a UTF-8 file in fixed-size chunks and decode each one?",
        ),
        _q(
            "How does EventEmitter handle errors, and what is the listener warning?",
            "emit calls listeners synchronously, in the order they were "
            "added. The error event is special: if you emit error and nothing "
            "listens, Node throws the error, which crashes the process if it "
            "is uncaught, so any emitter that can fail needs an error "
            "listener. The default limit is 10 listeners per event; adding "
            "more prints a warning that a leak is likely, because forgetting to "
            "remove listeners is a classic leak, and you raise the limit only "
            "when the count is intentional. once removes the listener after "
            "its first call.",
            "Is emit synchronous or asynchronous, and why does that matter?",
        ),
        _q(
            "How would you shut a Node server down gracefully?",
            "Listen for SIGTERM and SIGINT. On the signal, stop accepting new "
            "connections with server.close, let in-flight requests finish, "
            "close databases and queues, then exit with code 0, with a hard "
            "timer that forces exit if draining takes too long. Mark the "
            "instance unhealthy first so the load balancer stops sending "
            "traffic. Keep-alive connections can hold close open, so close "
            "idle ones too. Orchestrators send SIGTERM and then SIGKILL after "
            "a grace period, so your drain must fit inside it.",
            "What do you do on an uncaughtException, and why is carrying on dangerous?",
        ),
        _q(
            "How do you use all the cores on a machine with Node?",
            "One Node process uses one core for JavaScript, so run several. "
            "The cluster module forks workers that share a listening port, "
            "with the primary distributing connections. In practice many "
            "teams skip cluster and run one process per core or per container "
            "behind a load balancer or process manager, which also isolates "
            "crashes. This only works for stateless servers: sessions, caches "
            "and websocket state must live in shared stores such as Redis, "
            "because processes do not share memory. CPU-heavy tasks go in "
            "worker threads.",
            "Which state breaks when you go from one process to eight?",
        ),
        _q(
            "How do you find a memory leak in a Node service?",
            "Watch the heap over time; a steady upward line after garbage "
            "collection is a leak. Take heap snapshots through the inspector "
            "at two moments under load and diff them, looking for object "
            "types whose count keeps growing and following their retainer "
            "path. Typical culprits are unbounded caches or maps, listeners "
            "never removed, closures holding request objects, and global "
            "arrays. Raising the old-space limit with --max-old-space-size "
            "only moves the crash later. Bounded caches, WeakRef and cleanup "
            "code fix most of them.",
            "What is the difference between a leak and a service that simply uses a lot of memory?",
        ),
    ),
)

_GAMES = Topic(
    id="js-browser-game-dev",
    name="Game Development in the Browser",
    order=240,
    languages=_JS,
    blurb="Game loops, fixed timesteps, collision, ECS, canvas versus WebGL, input and determinism.",
    questions=(
        _q(
            "How do you build a game loop in the browser?",
            "Call requestAnimationFrame with a function that does one frame "
            "of work and then requests the next frame. Never use a while "
            "loop, which would freeze the page, and setInterval drifts and "
            "keeps running when nothing is visible. The callback receives a "
            "high-resolution timestamp; subtract the previous one to get the "
            "time since the last frame, called delta time. Each frame reads "
            "input, updates the simulation using that delta, and draws. The "
            "loop pauses in background tabs, so clamp the delta when the tab "
            "returns or the game jumps ahead.",
            "What happens to your game when the tab is hidden and then shown again?",
        ),
        _q(
            "What is delta time and why multiply by it?",
            "Delta time is how long the last frame took. If you move an object "
            "a fixed distance per frame, a 144 Hz monitor runs the game 2.4 "
            "times faster than a 60 Hz one. Movement should be speed times "
            "delta, so a speed of 100 pixels per second covers 100 pixels in a "
            "second however many frames share it: 60 steps of 1/60 and 30 "
            "steps of 1/30 both end at 100. It is not exact for physics, "
            "where variable steps change the results, which is why fixed "
            "steps exist.",
            "Why is clamping the delta important?",
        ),
        _q(
            "What is a fixed timestep with an accumulator?",
            "You advance the simulation in constant slices, say 10 "
            "milliseconds, however long the frame took. Each frame, add the "
            "elapsed time to an accumulator and run one update per slice "
            "while it holds at least a whole slice, subtracting each time, "
            "then draw once. The remainder carries over to the next frame. "
            "Three frames of 16 milliseconds add up to 48, which is four "
            "updates with 8 left over. It makes physics deterministic and "
            "independent of frame rate, which variable steps cannot do.",
            "Why is the remainder kept rather than discarded?",
        ),
        _q(
            "What is the spiral of death in a game loop, and how do you avoid it?",
            "If an update takes longer than the slice it simulates, each frame "
            "falls behind, so the next has more slices to catch up, which "
            "takes still longer, and the game freezes. The cure is to cap how "
            "much time one frame may add, or the number of updates per frame, "
            "and accept that the game slows down instead. With a backlog of "
            "1000 milliseconds and a cap of five updates, only five 10 "
            "millisecond steps run and 950 remain. Also make the update "
            "cheaper, so there is headroom.",
            "What should you do with the leftover backlog: keep it or drop it?",
        ),
        _q(
            "How do you stop movement looking choppy with a fixed timestep?",
            "The updates tick at one rate and the display at another, so the "
            "leftover in the accumulator means the screen is somewhere between "
            "two simulated states. Keep the previous and current state and "
            "draw a blend of them using alpha, the leftover divided by the "
            "slice. With the old position 0, the new one 10 and 8 of 10 "
            "milliseconds left over, you draw at 8. It costs one frame of "
            "visual latency but removes the stutter that shows when a 60 Hz "
            "simulation is drawn on a 144 Hz screen.",
            "What state do you need to store to interpolate rotation as well as position?",
        ),
        _q(
            "How does collision detection work, and how do you make it fast?",
            "Test two axis-aligned boxes by checking they overlap on both "
            "axes, so one box's left must be before the other's right, and so "
            "on. Boxes that only touch edges do not overlap: two ten-wide "
            "boxes at 0 and 10 give false, and at 0 and 9 give true. With many "
            "objects, testing every pair is quadratic, so split it: a broad "
            "phase uses a grid, quadtree or sweep and prune to find candidate "
            "pairs cheaply, and a narrow phase runs the exact test only on "
            "those.",
            "How does a spatial hash grid choose its cell size?",
        ),
        _q(
            "What is tunnelling and how do you prevent it?",
            "A fast object can move so far in one step that it is on one side "
            "of a thin wall before the step and the other side after, so a "
            "discrete overlap test never sees contact. A 30 pixel step jumps "
            "clean over a 5 pixel wall. Fixes: smaller steps or substeps, "
            "continuous collision detection that sweeps the shape along its "
            "path and finds the time of impact, a raycast from the old "
            "position to the new one, or thicker walls. Capping speed also "
            "helps.",
            "How would you do a swept test for a moving circle against a wall?",
        ),
        _q(
            "Entity component system versus object-oriented game objects: what is the difference?",
            "With classes, each game object is an instance with data and "
            "behaviour, and variety comes from inheritance, which gets "
            "awkward when a flying enemy that also shoots does not fit the "
            "tree. In an ECS an entity is just an id, components are plain "
            "data such as position or velocity attached to ids, and systems "
            "are functions that loop over every entity having certain "
            "components. You compose behaviour by adding components, and tight "
            "arrays of similar data are cache friendly and easy to save. A "
            "velocity system leaves the others untouched.",
            "When is ECS overkill for a small browser game?",
        ),
        _q(
            "Canvas 2D or WebGL: how do you choose?",
            "Canvas 2D is a simple immediate-mode drawing API, and it "
            "comfortably handles thousands of sprites on a modern machine, so "
            "it suits most 2D games. WebGL talks to the GPU through shaders, "
            "and wins when you need tens of thousands of sprites, 3D, "
            "particles or custom shading, by batching geometry into few draw "
            "calls, at the cost of far more code. WebGPU is the newer, "
            "lower-overhead option. For crisp output, size the canvas buffer "
            "by devicePixelRatio and the CSS size separately, or it looks "
            "blurry on dense screens.",
            "How would you reduce draw calls with a sprite atlas?",
        ),
        _q(
            "How do you load assets and handle audio in a browser game?",
            "Load everything before play starts, behind a loading screen: "
            "create Image objects and wait for their load events, fetch and "
            "decode audio, and wait for all of it with Promise.all, which "
            "returns results in the same order as the input whichever "
            "finished first. Pack sprites into an atlas to cut requests. "
            "Browsers refuse to start audio until a user gesture, so create "
            "or resume the AudioContext on the first click or key press, and "
            "use the Web Audio API for low latency and layering.",
            "How do you show an honest progress bar when file sizes are unknown?",
        ),
        _q(
            "How do you handle keyboard input in a game?",
            "Do not move the player inside the keydown handler. Record state "
            "instead: a set of held keys, added on keydown and removed on "
            "keyup, and read it in the update step, so movement is tied to the "
            "loop and not to the keyboard's repeat rate. Use event.code for "
            "physical positions, since WASD stays in place on any layout, and "
            "key for typed characters. Clear the set on window blur, or a key "
            "released while another window had focus stays stuck. Track "
            "presses separately from holds, and poll gamepads each frame.",
            "How do you handle left and right pressed in the same frame?",
        ),
        _q(
            "How do you make a game deterministic, and why would you?",
            "Determinism means the same inputs always give the same result, "
            "which buys replays, rollback netcode, reproducible bug reports "
            "and tests. You need a fixed timestep, all randomness from a "
            "seeded generator, since Math.random cannot be seeded, a stable "
            "order of updates and input, and no dependence on wall-clock "
            "time. Two generators built from the same seed, such as "
            "mulberry32 with 42, return identical values. Results of sin or "
            "cos can differ across engines, so cross-machine determinism may "
            "need fixed-point maths.",
            "What else can make a replay diverge, such as iteration order or asynchronous loading?",
        ),
    ),
)

_FRONTEND = Topic(
    id="frontend-system-design",
    name="Front-end System Design",
    order=250,
    languages=_JS,
    blurb="State, components, accessibility, i18n, offline, rendering strategies and monitoring.",
    questions=(
        _q(
            "How do you decide where state lives?",
            "Put each piece of state as close as possible to where it is used "
            "and lift it only as far as needed. Local UI state, such as a "
            "toggle, stays in the component. State shared by siblings lifts to "
            "their parent. State needed across the app, such as the current "
            "user or theme, goes in a context or store. Data owned by the "
            "server is not really client state: keep it in a cache keyed by "
            "the request. State like filters and the page belongs in the URL, "
            "so it can be shared and survives a reload. Derive values rather "
            "than storing copies.",
            "What goes wrong when the same fact is stored in two places?",
        ),
        _q(
            "What is the difference between client state and server state?",
            "Client state is created and owned by the UI, such as an open menu "
            "or a draft, so it is synchronous and always current. Server state "
            "is a copy of data owned elsewhere, so it can go stale, must be "
            "fetched, cached and invalidated, and can fail. Treating it as "
            "client state leads to hand-written loading flags, duplicate "
            "fetches and out-of-date screens. A server-state cache gives each "
            "query a key, serves stale data while it revalidates, "
            "deduplicates concurrent requests and retries; optimistic "
            "updates show the change at once and roll back on error.",
            "How do you invalidate cached data after a mutation?",
        ),
        _q(
            "How does a reducer-based store work, and why must reducers be pure?",
            "A reducer takes the current state and an action and returns the "
            "next state, with no mutation and no side effects. The store "
            "keeps the state, runs actions through the reducer and notifies "
            "subscribers. Purity makes updates predictable and testable, "
            "enables replay and time-travel debugging, and lets subscribers "
            "use an identity check to see what changed. With n at 0, an "
            "increment gives a new object with n at 1, the original is "
            "untouched, and an unknown action returns the same object. Side "
            "effects belong in middleware or effects.",
            "Where do asynchronous side effects like fetching belong in this model?",
        ),
        _q(
            "How do you design a reusable component?",
            "Start from the smallest useful contract: a few typed props, "
            "sensible defaults, and no knowledge of where it is used. Prefer "
            "composition over configuration, so children or slots let callers "
            "supply content instead of adding another boolean prop. Decide "
            "whether it is controlled, where the parent owns the value, or "
            "uncontrolled, where it keeps its own, and support both for a form "
            "control. Make it accessible by default, keep styling "
            "overridable, and avoid reaching into global state. Test it "
            "through its public behaviour.",
            "When do you split a component and when do you leave it large?",
        ),
        _q(
            "What does accessible front-end work involve, beyond adding alt text?",
            "Start with semantic HTML, because buttons, links, headings and "
            "form labels bring keyboard behaviour and screen reader meaning "
            "for free; ARIA is the last resort, and the first rule of ARIA is "
            "not to use it when a native element works. Everything must work "
            "by keyboard, with a visible focus indicator and a sensible tab "
            "order. Normal-size text needs a contrast ratio of at least 4.5 to "
            "1 under WCAG AA. Announce dynamic changes with live regions, "
            "label every input, and do not rely on colour alone.",
            "How would you test accessibility, both automated and by hand?",
        ),
        _q(
            "How do you build an accessible modal dialog?",
            "Use the native dialog element opened with showModal where you "
            "can: it traps focus inside, makes the rest of the page inert, "
            "closes on Escape and sits in the top layer. Otherwise you do "
            "those by hand: move focus into the dialog on open, keep Tab "
            "cycling within it, close on Escape, mark the background inert, "
            "label the dialog with aria-labelledby, and return focus to the "
            "element that opened it on close. Stop the page behind from "
            "scrolling, and make the close button reachable by keyboard.",
            "Why is returning focus to the trigger important?",
        ),
        _q(
            "How do you handle internationalisation in a front end?",
            "Never build sentences by joining strings, because word order "
            "differs by language: use message templates with named "
            "placeholders. Use the built-in Intl APIs for numbers, "
            "currencies, dates and plurals instead of hand-formatting: German "
            "writes a euro amount with a dot for thousands, a comma for "
            "decimals and the symbol after. Plural rules vary, English has "
            "one and other, while Arabic has six categories, including two. "
            "Plan for longer text and for right-to-left layouts with logical "
            "CSS properties, and load only the locale needed.",
            "How do you test a layout against translations you cannot read?",
        ),
        _q(
            "How would you make a web app work offline?",
            "Register a service worker, a script between the page and the "
            "network that can intercept requests and answer from a cache. "
            "Precache the app shell, the HTML, scripts and styles, at install "
            "time, and choose a strategy per request type: cache first for "
            "fingerprinted assets, network first for fresh API data with a "
            "cache fallback, and stale-while-revalidate where fast beats "
            "fresh. Keep user data in IndexedDB and queue writes to sync "
            "later. The hard parts are updates, since the old worker controls "
            "open pages until they close, and invalidation.",
            "How do users get a new version of the app once a service worker is installed?",
        ),
        _q(
            "How would you design a type-ahead search box?",
            "Debounce the input by roughly 150 to 300 milliseconds, so you do "
            "not query on every key. Cancel or ignore stale requests, by "
            "aborting the previous fetch or tagging each with an increasing "
            "id, so a slow response for ab cannot overwrite the answer for "
            "abc. If the first search takes 30 milliseconds and the second 5, "
            "only the latest, ab, is kept. Cache earlier results by query, show "
            "a loading state without flicker, and handle empty and error "
            "states. Accessibility needs the combobox pattern, with arrow-key "
            "navigation and announced result counts.",
            "How would you rank and highlight results on the client?",
        ),
        _q(
            "Infinite scroll or pagination: how do you choose and build it?",
            "Infinite scroll suits browsing feeds where the user is not "
            "looking for a specific place, and pagination suits tasks where "
            "position, bookmarking, the footer and going back matter. Build "
            "the scroll with an IntersectionObserver on a sentinel element "
            "near the end, which beats scroll handlers, and load by cursor. "
            "Keep memory bounded by virtualising rows, preserve scroll "
            "position when the user navigates away and back, and put the "
            "cursor or page in the URL. Offer a keyboard-reachable load more "
            "button as the accessible fallback.",
            "How do you keep the footer reachable on an infinite list?",
        ),
        _q(
            "Client-side rendering, server-side rendering, static generation: how do you choose?",
            "Client-side rendering ships a small HTML shell and builds the "
            "page in the browser, which is simple to host and fine for "
            "logged-in apps, but delays content until the JavaScript runs. "
            "Server-side rendering builds HTML per request, giving a fast "
            "first paint and good crawling at the cost of server work and "
            "hydration. Static generation builds pages at deploy time and "
            "serves them from a CDN, the cheapest and fastest for content that "
            "rarely changes, with incremental regeneration to refresh it. "
            "Hydration attaches the JavaScript to existing HTML, and islands "
            "hydrate only the interactive parts.",
            "What is a hydration mismatch and what causes one?",
        ),
        _q(
            "How do you find out about errors in a front-end app you have shipped?",
            "Capture them in the browser: window onerror and the "
            "unhandledrejection event for anything that escapes, error "
            "boundaries around component trees so one failure shows a "
            "fallback instead of a blank page, and explicit handling of failed "
            "requests. Send them to a monitoring service with the release, "
            "route, browser and a trail of user actions, and use source maps "
            "to read minified stacks. Sample and group them so noise does not "
            "hide real regressions. Roll out behind feature flags or "
            "canaries, so a bad release can be switched off without a deploy.",
            "What do you not log, and why?",
        ),
    ),
)

INTERVIEW_TOPICS: tuple[Topic, ...] = (
    _CLOSURES,
    _THIS,
    _PROTOTYPES,
    _EVENT_LOOP,
    _PROMISES,
    _TYPES,
    _DATA,
    _MODULES,
    _DOM,
    _RENDERING,
    _SECURITY,
    _HTTP,
    _TESTING,
    _NODE,
    _GAMES,
    _FRONTEND,
)
