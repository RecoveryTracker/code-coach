"""Words that only JavaScript has (or that mean something different there): null, undefined, NaN, ===,
template literals, arrow functions, this, promises, the event loop ..."""

from __future__ import annotations

from .entry import Entry, js

TERMS: list[Entry] = [
    *js(
        "null",
        "null",
        "A value you set on purpose to mean 'nothing here'.",
        see=("undefined", "falsy", "strict-equality"),
        priority=70,
        aka=("nil", "none"),
        detect=(r"\bnull\b",),
        rules=(
            "null is falsy.",
            "typeof null is 'object' - an old mistake kept so old code would not break; it is not an object.",
            "null == undefined is true, but null === undefined is false. x == null catches both.",
            "In arithmetic null counts as 0: null + 1 is 1.",
        ),
        example="""
            console.log(null === undefined, null == undefined, typeof null, Boolean(null), null + 1);
        """,
        out="false true object false 1",
    ),
    *js(
        "undefined",
        "undefined",
        "The value JavaScript gives to anything that has no value yet: a variable never assigned, a missing argument, a missing property, a function that returns nothing.",
        see=("null", "falsy", "optional-chaining"),
        priority=70,
        detect=(r"\bundefined\b",),
        rules=(
            "undefined is falsy, and typeof undefined is 'undefined'.",
            "Reading a missing property gives undefined, not an error: obj.missing is undefined.",
            "Reading a property OF undefined is a TypeError: obj.missing.name throws.",
            "Prefer null when YOU mean 'empty on purpose', so the two stay distinguishable.",
        ),
        example="""
            let x;
            const o = { a: 1 };
            function f() {}
            console.log(x, o.b, f());
            try {
              o.b.c;
            } catch (e) {
              console.log(e.name);
            }
        """,
        out="undefined undefined undefined\nTypeError",
    ),
    *js(
        "nan",
        "NaN",
        "'Not a Number': what a number operation gives when it has no sensible numeric answer, such as 0 / 0 or 'abc' * 2.",
        see=("falsy", "type-conversion", "float"),
        priority=65,
        aka=("not a number", "isnan"),
        detect=(r"\bNaN\b|\bNumber\.isNaN\(|\bisNaN\(",),
        rules=(
            "typeof NaN is 'number', and NaN is falsy.",
            "NaN is not equal to anything, even itself: NaN === NaN is false. Test with Number.isNaN(x).",
            "Any arithmetic with NaN gives NaN, so one bad value spreads through a calculation.",
        ),
        example="""
            console.log(0 / 0, "abc" * 2, typeof NaN, NaN === NaN, Number.isNaN("abc" * 2));
        """,
        out="NaN NaN number false true",
    ),
    *js(
        "array",
        "Array",
        "An ordered collection of items that you can change, written in square brackets: [3, 1, 2].",
        see=("index", "mutable", "map", "length"),
        priority=40,
        aka=("arrays", "list"),
        detect=(r"(?:[=(,:]|\breturn|\bof|^)\s*\[|\bnew\s+Array\(|\.(?:push|pop|shift|unshift|splice)\(",),
        rules=(
            "Items keep their order and are numbered from 0; they can be of different types.",
            "Common methods: push(x), pop(), shift(), unshift(x), splice(), slice(), sort(), reverse().",
            "sort() with no function sorts as TEXT: [10, 9, 1].sort() is [1, 10, 9]. Give it (a, b) => a - b for numbers.",
            "An empty array [] is truthy; test array.length instead.",
        ),
        example="""
            const nums = [3, 1, 2];
            nums.push(4);
            nums.sort();
            console.log(nums, nums.length);
            console.log([10, 9, 1].sort());
        """,
        out="[ 1, 2, 3, 4 ] 4\n[ 1, 10, 9 ]",
    ),
    *js(
        "object",
        "Object",
        "A collection of named values, written in braces: { apple: 3, pear: 5 }. Each name is a key and its value is the property.",
        see=("key", "value", "mutable", "class"),
        priority=40,
        aka=("objects", "dictionary", "dict", "map"),
        detect=(r"\{\s*[A-Za-z_$][\w$]*\s*:", r"\bObject\.(?:keys|values|entries|assign)\(", r"\bnew\s+Object\("),
        rules=(
            "Read a property with obj.key or obj['key']; a missing one is undefined.",
            "Keys are strings (or symbols), even when written as numbers.",
            "An object is truthy even when empty: {} is truthy.",
            "Arrays and functions are objects too.",
        ),
        example="""
            const prices = { apple: 3, pear: 5 };
            prices.fig = 9;
            console.log(prices.apple, prices["pear"], prices.kiwi, Object.keys(prices).length);
        """,
        out="3 5 undefined 3",
    ),
    *js(
        "key",
        "Key",
        "In an object, the name you look an item up by. Each key goes with one value.",
        see=("object", "value"),
        priority=40,
        aka=("keys", "key-value", "property name"),
        detect=(r"\bObject\.(?:keys|entries)\(", r"\bfor\s*\(\s*(?:const|let|var)\s+[\w$]+\s+in\b"),
        rules=(
            "Keys in one object are unique: setting an existing key replaces its value.",
            "Object.keys(o), Object.values(o) and Object.entries(o) list the keys, the values or the pairs.",
            "'k' in o asks whether k is a KEY, not a value.",
        ),
        example="""
            const d = { a: 1, b: 2 };
            for (const [k, v] of Object.entries(d)) console.log(k, v);
            console.log("a" in d, 2 in d);
        """,
        out="a 1\nb 2\ntrue false",
    ),
    *js(
        "set",
        "Set",
        "A collection of unique values. Adding something already in it changes nothing.",
        see=("array", "iterable"),
        priority=45,
        aka=("sets", "new Set"),
        detect=(r"\bnew\s+Set\(|\bSet\b",),
        rules=(
            "Made with new Set(iterable): duplicates vanish.",
            "Use s.add(x), s.has(x), s.delete(x) and s.size (a property, not length).",
            "It remembers the order items were added; [...s] turns it into an array.",
        ),
        example="""
            const s = new Set([1, 2, 2, 3]);
            console.log(s.size, s.has(2), [...s]);
        """,
        out="3 true [ 1, 2, 3 ]",
    ),
    *js(
        "loose-equality",
        "Loose equality (==)",
        "== asks whether two values are equal after JavaScript converts them to a common type first. It gives surprising answers, so === is usually safer.",
        see=("strict-equality", "type-conversion", "null"),
        priority=80,
        aka=("==", "!=", "abstract equality", "equal", "equals", "equal to"),
        detect=(r"(?<![=!<>])==(?!=)|!=(?!=)",),
        rules=(
            "'5' == 5 is true (the text becomes a number), and 0 == '' is true.",
            "null == undefined is true, and null == 0 is false.",
            "It is not transitive: '0' == 0 and 0 == '' are true, but '0' == '' is false.",
            "x == null is the one common use: it catches both null and undefined.",
        ),
        example="""
            console.log("5" == 5, 0 == "", null == undefined, null == 0, "0" == "");
        """,
        out="true true true false false",
    ),
    *js(
        "strict-equality",
        "Strict equality (===)",
        "=== asks whether two values are the same type AND the same value, with no conversion. Use it by default instead of ==.",
        see=("loose-equality", "comparison", "nan"),
        priority=70,
        aka=("===", "!==", "identity", "strict", "equal", "equals", "equal to"),
        detect=(r"===|!==",),
        rules=(
            "'5' === 5 is false: different types.",
            "NaN === NaN is false. Use Number.isNaN(x).",
            "Objects and arrays are equal only if they are the very same object: [] === [] is false.",
            "!== is the opposite of ===.",
        ),
        example="""
            console.log("5" === 5, NaN === NaN, [] === [], 5 === 5, 5 !== "5");
        """,
        out="false false false true true",
    ),
    *js(
        "template-literal",
        "Template literal",
        "A string written with backticks (`like this`). Anything in ${ } is worked out and put into the text.",
        see=("string", "concatenation"),
        priority=55,
        aka=("template string", "backtick", "backticks", "string interpolation", "${}", "f-string", "string formatting"),
        detect=(r"raw:`",),
        rules=(
            "Any expression works inside ${ }: ${n * 2}, ${name.toUpperCase()}.",
            "A backtick string can run over several lines.",
            "Only backticks do this: 'total: ${n}' in ordinary quotes is just text.",
        ),
        example="""
            const name = "Ana";
            const n = 3;
            console.log(`${name} has ${n * 2} apples, ${(3.14159).toFixed(2)}`);
            console.log('${n}');
        """,
        out="Ana has 6 apples, 3.14\n${n}",
    ),
    *js(
        "arrow-function",
        "Arrow function",
        "A short way to write a function with =>: (x) => x * 2 means 'given x, give back x * 2'.",
        see=("function", "callback", "this", "return"),
        priority=60,
        aka=("arrow", "=>", "fat arrow", "lambda", "anonymous function"),
        detect=(r"=>",),
        rules=(
            "With no braces the value after => is returned automatically; with braces you must write return.",
            "To return an object literal wrap it in brackets: () => ({ ok: true }).",
            "An arrow function has no this of its own: it uses the one around it.",
        ),
        example="""
            const double = (x) => x * 2;
            const make = () => ({ ok: true });
            console.log(double(4), make(), [3, 1, 2].sort((a, b) => a - b));
        """,
        out="8 { ok: true } [ 1, 2, 3 ]",
    ),
    *js(
        "this",
        "this",
        "Inside a method, the object the method was called on - so the method can read and change that object's own data.",
        see=("class", "method", "arrow-function"),
        priority=65,
        aka=("self",),
        detect=(r"\bthis\b",),
        rules=(
            "What this is depends on HOW a function is called, not where it is written: obj.add() makes this the obj.",
            "A plain function call has no object: this is undefined in strict mode and modules.",
            "Passing obj.add as a callback loses its this - a classic bug. Arrow functions keep the surrounding this.",
        ),
        example="""
            const counter = {
              n: 0,
              add() {
                this.n += 1;
                return this.n;
              },
            };
            counter.add();
            console.log(counter.add());
        """,
        out="2",
    ),
    *js(
        "spread-rest",
        "Spread and rest (...)",
        "Three dots do two jobs. Spread opens an array or object out into separate items; rest gathers leftover items into one array.",
        see=("unpacking", "array", "parameter"),
        priority=60,
        aka=("...", "spread", "rest", "spread operator", "rest parameter"),
        detect=(r"\.\.\.[\w$\[({]",),
        rules=(
            "[...a, 3] makes a new array holding a's items and 3; { ...obj, x: 1 } copies an object with x set.",
            "function f(...nums) gathers all the arguments into the array nums.",
            "Spread makes a shallow copy: nested arrays and objects are still shared.",
        ),
        example="""
            const a = [1, 2];
            const b = [...a, 3];
            function sum(...n) {
              return n.reduce((s, v) => s + v, 0);
            }
            console.log(b, sum(1, 2, 3), Math.max(...b));
        """,
        out="[ 1, 2, 3 ] 6 3",
    ),
    *js(
        "promise",
        "Promise",
        "An object that stands for a result that is not ready yet. Later it is either fulfilled with a value or rejected with an error.",
        see=("async-await", "event-loop", "callback"),
        priority=60,
        aka=("promises", "then", "fulfilled", "rejected", "pending"),
        detect=(r"\bPromise\b|\.then\(|\.catch\(",),
        rules=(
            "promise.then(fn) runs fn with the value once it is ready; promise.catch(fn) runs fn if it failed.",
            "A promise is not the value itself: you cannot read the result on the next line without then or await.",
            "A then callback never runs immediately - not even if the promise is already done.",
        ),
        example="""
            Promise.resolve(5).then((v) => console.log("then", v));
            console.log("sync");
        """,
        out="sync\nthen 5",
    ),
    *js(
        "event-loop",
        "Event loop",
        "The way JavaScript handles waiting things (timers, promises, clicks): it runs the current code to the end first, then picks the next waiting job.",
        see=("promise", "callback", "async-await"),
        priority=60,
        aka=("microtask", "task queue", "settimeout", "single-threaded"),
        detect=(r"\bsetTimeout\(|\bsetInterval\(|\.then\(|\bawait\b|\bPromise\b|\bqueueMicrotask\(",),
        rules=(
            "All the plain code runs first. Then promise callbacks run. Then timers run, even setTimeout(fn, 0).",
            "Only one thing runs at a time: a long loop freezes timers and the page until it ends.",
            "setTimeout(fn, 0) means 'as soon as the current code is done', not 'now'.",
        ),
        example="""
            setTimeout(() => console.log("timeout"), 0);
            Promise.resolve().then(() => console.log("promise"));
            console.log("sync");
        """,
        out="sync\npromise\ntimeout",
    ),
    *js(
        "console-log",
        "console.log()",
        "The function that shows values in the console. It is how a program talks to you.",
        see=("function", "return", "string"),
        priority=25,
        aka=("console.log", "console", "print", "output", "log"),
        detect=(r"\bconsole\.\w+\(",),
        rules=(
            "Several values are separated by a space: console.log('a', 1) shows a 1.",
            "Strings show without quotes at top level but with quotes inside arrays and objects.",
            "It gives back undefined and does not return what it shows (see return value).",
        ),
        example="""
            console.log("a", 1, true);
            console.log(["a"], { k: "v" });
        """,
        out="a 1 true\n[ 'a' ] { k: 'v' }",
    ),
    *js(
        "length",
        "length",
        "A property that counts the items in an array or the characters in a string.",
        see=("index", "array", "off-by-one"),
        priority=25,
        aka=(".length",),
        detect=(r"\.length\b",),
        rules=(
            "It is a property, not a method: no parentheses. 'farm'.length is 4.",
            "The last valid index is length - 1.",
            "An empty array has length 0 but is still truthy: test items.length, not items.",
        ),
        example="""
            console.log("farm".length, [1, 2].length, [].length, "".length);
        """,
        out="4 2 0 0",
    ),
    *js(
        "let-const-var",
        "let, const and var",
        "The three keywords that create a variable. let can be reassigned, const cannot, and var is the older kind that you should avoid.",
        see=("variable", "scope", "reassign", "hoisting"),
        priority=40,
        aka=("let", "const", "var", "declare", "declaration"),
        detect=(r"\b(?:let|const|var)\b",),
        rules=(
            "Use const by default and let when the value must change.",
            "const stops reassignment only: a const array can still be pushed to.",
            "let and const stay inside their braces; var leaks out to the whole function.",
        ),
        example="""
            let a = 1;
            a = 2;
            const b = [1];
            b.push(2);
            console.log(a, b);
        """,
        out="2 [ 1, 2 ]",
    ),
    *js(
        "hoisting",
        "Hoisting",
        "JavaScript reads a scope's declarations before it runs the code, so some names already exist above the line that creates them.",
        see=("let-const-var", "scope", "function"),
        priority=55,
        aka=("hoisted", "hoist", "temporal dead zone"),
        detect=(r"\bvar\b",),
        rules=(
            "A function declaration can be called before its line.",
            "A var exists early but is undefined until its line runs.",
            "let and const exist early but cannot be used before their line: that is a ReferenceError (the temporal dead zone).",
        ),
        example="""
            console.log(add(2, 3), typeof later);
            function add(a, b) {
              return a + b;
            }
            var later = 1;
        """,
        out="5 undefined",
    ),
    *js(
        "nullish",
        "Nullish coalescing (??)",
        "a ?? b gives b only when a is null or undefined, and a in every other case, including 0 and ''.",
        see=("short-circuit", "null", "undefined"),
        priority=65,
        aka=("??", "nullish coalescing"),
        detect=(r"\?\?",),
        rules=(
            "It is the safe way to give a default: count ?? 10 keeps a real 0, but count || 10 replaces it.",
            "Only null and undefined count as 'missing'.",
        ),
        example="""
            const count = 0;
            console.log(count || 10, count ?? 10, null ?? "none", undefined ?? "none");
        """,
        out="10 0 none none",
    ),
    *js(
        "optional-chaining",
        "Optional chaining (?.)",
        "a?.b reads b only if a is not null or undefined; otherwise the whole thing is undefined instead of an error.",
        see=("undefined", "null", "nullish"),
        priority=60,
        aka=("?.", "optional chain", "safe navigation"),
        detect=(r"\?\.",),
        rules=(
            "It also works for calls (fn?.()) and indexes (a?.[0]).",
            "If a is null or undefined the rest of the chain is skipped, so a?.b.c is undefined. If a exists but b is undefined, .c still throws.",
            "Pair it with ?? for a default: user?.name ?? 'anonymous'.",
        ),
        example="""
            const user = { profile: null };
            console.log(user.profile?.name, user.address?.city, user.profile?.name ?? "anonymous");
        """,
        out="undefined undefined anonymous",
    ),
    *js(
        "increment",
        "Increment and decrement",
        "x++ adds one to x, and x-- subtracts one.",
        see=("augmented-assignment", "loop"),
        priority=40,
        aka=("++", "--", "plus plus"),
        detect=(r"\+\+|--",),
        rules=(
            "x++ gives back the OLD value and then adds one; ++x adds one and gives back the NEW value.",
            "On their own line the two are the same.",
        ),
        example="""
            let i = 5;
            const a = i++;
            const b = ++i;
            console.log(a, b, i);
        """,
        out="5 7 7",
    ),
    *js(
        "map",
        "map",
        "array.map(fn) builds a new array by running fn on every item and collecting the results.",
        see=("filter", "reduce", "callback", "arrow-function"),
        priority=55,
        aka=(".map", "array.map"),
        detect=(r"\.map\(",),
        rules=(
            "The new array is the same length as the old one; the old one is not changed.",
            "fn receives (item, index).",
            "It returns an array: use forEach if you only want side effects.",
        ),
        example="""
            const nums = [1, 2, 3];
            console.log(nums.map((n) => n * 2), nums);
        """,
        out="[ 2, 4, 6 ] [ 1, 2, 3 ]",
    ),
    *js(
        "filter",
        "filter",
        "array.filter(fn) builds a new array holding only the items for which fn gives something truthy.",
        see=("map", "reduce", "truthy", "callback"),
        priority=55,
        aka=(".filter", "array.filter"),
        detect=(r"\.filter\(",),
        rules=(
            "The new array can be shorter, even empty; the old one is not changed.",
            "fn only needs to return something truthy or falsy, not necessarily true or false.",
        ),
        example="""
            console.log([1, 2, 3, 4].filter((n) => n % 2 === 0), [0, 1, "", "a"].filter((x) => x));
        """,
        out="[ 2, 4 ] [ 1, 'a' ]",
    ),
    *js(
        "reduce",
        "reduce",
        "array.reduce(fn, start) boils an array down to a single value by combining the items one at a time.",
        see=("map", "filter", "callback"),
        priority=55,
        aka=(".reduce", "array.reduce", "fold", "accumulator"),
        detect=(r"\.reduce\(",),
        rules=(
            "fn receives (accumulator, item) and returns the new accumulator; start is its first value.",
            "Always give a start value: reduce on an empty array without one throws a TypeError.",
        ),
        example="""
            console.log([1, 2, 3].reduce((sum, n) => sum + n, 0), [].reduce((s, n) => s + n, 0));
        """,
        out="6 0",
    ),
    *js(
        "switch",
        "switch",
        "A statement that picks which code to run by comparing one value against a list of cases.",
        see=("branch", "strict-equality", "break-continue"),
        priority=45,
        aka=("default",),
        detect=(r"\bswitch\b",),
        rules=(
            "Cases are compared with ===.",
            "Without a break, execution falls through into the next case.",
            "default runs when no case matches.",
        ),
        example="""
            const day = 2;
            switch (day) {
              case 1:
                console.log("one");
                break;
              case 2:
                console.log("two");
              case 3:
                console.log("three (fell through)");
                break;
              default:
                console.log("other");
            }
        """,
        out="two\nthree (fell through)",
    ),
]
