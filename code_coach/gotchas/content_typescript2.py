"""Gotchas, TypeScript, the second helping: what the types say versus what the program does.

Same rules as content_typescript.py: tsc --strict --target es2020, then node. Every card compiles, prints one line,
and the wrong options are real misreads. The theme is that types are erased: most of these are plain JavaScript
runtime traps that a type checker does not warn about, plus the places where TypeScript itself changes the
emitted code (enums, parameter properties, class fields).
"""

from __future__ import annotations

from .items import Item, make

q = make("typescript")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics with a real trap ──────────────────────────────
    q("parseint-in-map", r'''
        const out = ["1", "2", "3"].map(parseInt);
        console.log(out.join(","));
    ''', "1,NaN,NaN", ["1,2,3", "1,2,NaN", "NaN,NaN,NaN"],
      "map passes the index as a second argument, and parseInt reads it as the radix",
      """`map` calls its callback with (value, index, array), so this runs `parseInt("2", 1)` and `parseInt("3", 2)`.
      Radix 1 is invalid and "3" is not a binary digit, so both give NaN. Write `map(s => parseInt(s, 10))` or
      use `Number`."""),

    q("plus-left-to-right", r'''
        const r = 1 + 2 + "3" + 4 + 5;
        console.log(r);
    ''', "3345", ["15", "12345", "339"],
      "+ goes left to right: numbers add until the first string appears",
      """`1 + 2` is 3, then `3 + "3"` turns into the string "33", and after that every `+` is concatenation, giving
      "3345". Wrapping the tail in parentheses, `"3" + (4 + 5)`, would change that."""),

    q("sparse-array-length", r'''
        const a: number[] = [];
        a[3] = 1;
        console.log(a.length, a.filter(() => true).length);
    ''', "4 1", ["4 4", "1 1", "3 1"],
      "Assigning past the end leaves holes; length counts them, filter skips them",
      """Writing index 3 makes `length` 4 and leaves indexes 0 to 2 empty, not undefined. `filter`, `map` and
      `forEach` skip holes, so only the one real element is seen."""),

    q("typeof-oddities", r'''
        console.log(typeof null, typeof [], typeof NaN, typeof class {});
    ''', "object object number function",
      ["null array NaN class", "object array number function", "null object number class"],
      "typeof has no 'null', 'array' or 'class' answer",
      """`typeof null` is the old bug "object", arrays are objects, NaN is a number, and a class is just a
      function underneath. Use `Array.isArray` and `=== null` to tell those apart."""),

    q("loose-equality-unknown", r'''
        const a: unknown = 0;
        console.log(a == false, a == "", a === "", null == undefined);
    ''', "true true false true", ["false true false true", "true true true true", "true false false true"],
      "== converts types before comparing; === does not",
      """`0 == ""` and `0 == false` are true because everything is converted to the number 0, while `===` sees two
      different types and says false. `null == undefined` is true by a special rule."""),

    q("float-sum", r'''
        console.log(0.1 + 0.2 === 0.3, (0.1 + 0.2).toFixed(2));
    ''', "false 0.30", ["true 0.30", "false 0.3", "true 0.3"],
      "0.1 + 0.2 is 0.30000000000000004, so exact comparison fails",
      """Binary floating point cannot store 0.1 or 0.2 exactly, so the sum lands a hair above 0.3 and `===` says
      false. `toFixed(2)` rounds the display to "0.30", which hides the error but returns a string."""),

    q("tofixed-and-round", r'''
        console.log((1.005).toFixed(2), (2.5).toFixed(0),
            Math.round(-2.5), Math.round(2.5));
    ''', "1.00 3 -2 3", ["1.01 3 -3 3", "1.01 2 -2 3", "1.00 2 -3 2"],
      "1.005 is really 1.00499..., and Math.round rounds halves toward +Infinity",
      """The double nearest to 1.005 is slightly below it, so `toFixed(2)` gives "1.00". `Math.round` sends .5
      up, which means 2.5 becomes 3 but -2.5 becomes -2, not -3."""),

    q("slice-versus-substring", r'''
        const s = "abcdef";
        console.log(s.slice(-3, -1), s.substring(-3, 2));
    ''', "de ab", ["bc ab", "de de", "ef ab"],
      "slice counts negatives from the end; substring turns them into 0",
      """`slice(-3, -1)` means from the third-last to the last (exclusive): "de". `substring` treats a negative
      argument as 0, so `substring(-3, 2)` is `substring(0, 2)`, "ab"."""),

    q("string-length-emoji", r'''
        const s = "a\u{1F600}";
        console.log(s.length, [...s].length);
    ''', "3 2", ["2 2", "3 3", "2 1"],
      "length counts UTF-16 units; spreading counts code points",
      """The emoji lies outside the 16-bit range, so it is stored as a surrogate pair and counts as two units in
      `length`. Spreading a string iterates by code point, finding 2 characters."""),

    q("for-in-keys-are-strings", r'''
        const out: string[] = [];
        for (const k in ["x", "y"]) out.push(k + 1);
        console.log(out.join(","));
    ''', "01,11", ["1,2", "x1,y1", "1,3"],
      "for...in gives the keys, and keys are always strings",
      """`for...in` walks property names, not values, and an array's indexes are the strings "0" and "1". So
      `k + 1` is string concatenation: "01" and "11". Use `for...of` for values."""),

    q("var-in-loop-closures", r'''
        const a: (() => number)[] = [];
        const b: (() => number)[] = [];
        for (var i = 0; i < 3; i++) a.push(() => i);
        for (let j = 0; j < 3; j++) b.push(() => j);
        console.log(a.map(f => f()).join(""), b.map(f => f()).join(""));
    ''', "333 012", ["012 012", "333 333", "012 333"],
      "var is one variable for the whole function; let makes one per iteration",
      """All three closures from the `var` loop share the single `i`, which is 3 by the time they run. Each pass
      of the `let` loop gets a fresh `j`, so those closures remember 0, 1 and 2."""),

    q("spread-is-a-copy", r'''
        const a = [1, 2];
        const b = a;
        const c = [...a];
        b.push(3);
        c.push(4);
        console.log(a.length, c.length);
    ''', "3 3", ["2 3", "3 2", "2 2"],
      "Assignment shares the array; spread copies it",
      """`b = a` makes a second name for the same array, so pushing through `b` lengthens `a` to 3. The spread
      builds a new array, which then holds 1, 2, 4: also length 3, but separate."""),

    q("freeze-is-shallow", r'''
        const f = Object.freeze({ n: 1, list: [1] });
        f.list.push(2);
        console.log(f.list.length, Object.isFrozen(f.list));
    ''', "2 false", ["1 false", "1 true", "2 true"],
      "Object.freeze locks the object's own properties, not what they point at",
      """The frozen object cannot get a new `n` or swap its `list`, but the array it holds is an ordinary mutable
      object, so the push works and `isFrozen(list)` is false."""),

    q("nan-search", r'''
        const a = [NaN];
        console.log(a.includes(NaN), a.indexOf(NaN));
    ''', "true -1", ["true 0", "false -1", "false 0"],
      "includes treats NaN as equal to itself; indexOf uses ===",
      """`includes` uses the SameValueZero comparison, under which NaN equals NaN. `indexOf` uses strict equality,
      and `NaN === NaN` is false, so it reports -1."""),

    q("reverse-mutates", r'''
        const a = [1, 2, 3];
        const b = a.reverse();
        console.log(a === b, a.join(""));
    ''', "true 321", ["false 321", "true 123", "false 123"],
      "reverse (like sort) changes the array in place and returns the same array",
      """The result is not a new array: `b` and `a` are the same object, and it now holds 3, 2, 1. Copy first with
      `[...a].reverse()` if the original must survive."""),

    q("splice-versus-slice", r'''
        const a = [1, 2, 3, 4];
        const gone = a.splice(1, 2);
        console.log(a.join(""), gone.join(""), a.slice(1).join(""));
    ''', "14 23 4", ["1234 23 234", "14 23 14", "23 14 4"],
      "splice removes from the array and returns the removed part",
      """`splice(1, 2)` cuts two elements starting at index 1 out of `a`, leaving 1, 4, and hands back the cut
      pieces 2, 3. `slice(1)` is the harmless one: it copies from index 1, giving just 4."""),

    q("replace-first-only", r'''
        const s = "a-b-c";
        console.log(s.replace("-", "+"), s.split("-").join("+"));
    ''', "a+b-c a+b+c", ["a+b+c a+b+c", "a+b-c a+b-c", "a-b-c a+b+c"],
      "A string pattern in replace matches only the first occurrence",
      """`replace` with a plain string replaces one match; replacing all needs a regex with the g flag or the
      split-and-join trick. The original string is never changed."""),

    q("unary-plus", r'''
        console.log(+"", +" 12 ", +"12px", +[], +[5], +true);
    ''', "0 12 NaN 0 5 1", ["NaN 12 12 0 5 1", "0 12 NaN NaN 5 NaN", "0 12 12 0 NaN 1"],
      "Unary plus is Number(): blank is 0, trailing junk is NaN, [] is 0",
      """`Number("")` and `Number(" 12 ")` ignore whitespace, but "12px" must be wholly numeric, so it is NaN.
      An array becomes a string first: [] gives "" (0) and [5] gives "5", while true converts to 1."""),

    q("max-min-empty", r'''
        console.log(Math.max(), Math.min(), Math.max(1, NaN));
    ''', "-Infinity Infinity NaN", ["0 0 1", "-Infinity Infinity 1", "0 Infinity NaN"],
      "With no arguments Math.max is -Infinity and Math.min is +Infinity",
      """They start from the identity of the operation, so an empty list leaves them at the worst possible value.
      A single NaN anywhere poisons the whole result."""),

    q("fill-shares-one-object", r'''
        const grid = new Array<number[]>(3).fill([]);
        grid[0].push(1);
        console.log(grid.map(r => r.length).join());
    ''', "1,1,1", ["1,0,0", "0,0,0", "3,0,0"],
      "fill puts the same object in every slot",
      """`fill([])` evaluates the empty array once and stores that one reference three times, so a push through any
      row shows in all rows. `Array.from({ length: 3 }, () => [])` builds three separate rows."""),

    q("integer-division-none", r'''
        console.log(7 / 2, Math.floor(-7 / 2), -7 % 3, Math.trunc(-3.5));
    ''', "3.5 -4 -1 -3", ["3 -4 -1 -3", "3.5 -3 2 -4", "3.5 -4 2 -4"],
      "/ is always floating point, and % keeps the sign of the left side",
      """There is no integer division: `7 / 2` is 3.5. `Math.floor` rounds toward minus infinity (-4), `Math.trunc`
      toward zero (-3), and `-7 % 3` is -1 because the remainder takes the sign of the dividend."""),

    q("switch-falls-through", r'''
        let s = "";
        const k: number = 2;
        switch (k) {
            case 1: s += "a";
            case 2: s += "b";
            case 3: s += "c"; break;
            default: s += "d";
        }
        console.log(s);
    ''', "bc", ["b", "c", "bcd"],
      "A case without break keeps running into the next case",
      """Matching case 2 jumps in at that line and keeps executing downward: "b", then case 3's "c", where the
      `break` stops it. `default` is never reached because the match already happened."""),

    q("power-associativity", r'''
        console.log(2 ** 3 ** 2, (2 ** 3) ** 2);
    ''', "512 64", ["64 64", "512 512", "64 512"],
      "** groups right to left",
      """`2 ** 3 ** 2` is `2 ** (3 ** 2)` = 2 ** 9 = 512, unlike + and * which group left to right. Parentheses
      give the other grouping, 8 squared, 64."""),

    q("length-assignment", r'''
        const a = [1, 2, 3, 4];
        a.length = 2;
        a[4] = 9;
        console.log(a.length, a.join());
    ''', "5 1,2,,,9", ["3 1,2,9", "5 1,2,9", "5 1,2,undefined,undefined,9"],
      "Setting length truncates, and writing past the end leaves holes",
      """Shortening `length` deletes the tail. Writing index 4 then makes the length 5 with holes at 2 and 3, and
      `join` renders holes as empty strings, giving two empty slots between commas."""),

    q("falsy-string-narrowing", r'''
        function len(s: string | null): number {
            if (!s) return -1;
            return s.length;
        }
        console.log(len(""), len(null), len("ab"));
    ''', "-1 -1 2", ["0 -1 2", "-1 0 2", "0 0 2"],
      "if (!s) catches the empty string as well as null",
      """The check narrows `string | null` nicely for the type checker, but at runtime "" is falsy too, so the
      empty string takes the same early return as null. Use `s === null` when only null is meant."""),

    q("index-out-of-range-typed", r'''
        const a: number[] = [1, 2, 3];
        const x: number = a[5];
        console.log(x + 1, typeof x);
    ''', "NaN undefined", ["6 number", "NaN number", "undefined undefined"],
      "The type says number, the runtime says undefined",
      """Indexing an array is typed as `number` even when the index is out of range (unless the
      `noUncheckedIndexedAccess` option is on). The value is really undefined, and `undefined + 1` is NaN."""),

    q("string-index-misses", r'''
        const s = "abc";
        console.log(`${s[5]}|${s.charAt(5)}|${s.charCodeAt(5)}`);
    ''', "undefined||NaN", ["undefined|undefined|NaN", "||0", "undefined||0"],
      "Out of range: [] gives undefined, charAt gives \"\", charCodeAt gives NaN",
      """Three similar lookups, three different failure values. Bracket indexing treats the string as an object
      with no such property, `charAt` returns an empty string, and `charCodeAt` has no code to return."""),

    # ── Types are erased ───────────────────────────────────────────────────
    q("double-assertion-lies", r'''
        const n = "5" as unknown as number;
        console.log(n + 1, typeof n);
    ''', "51 string", ["6 number", "6 string", "51 number"],
      "A type assertion promises the compiler something; it converts nothing",
      """`as` changes only what the checker believes. The value is still the string "5", so `n + 1` is
      concatenation. Real conversion needs `Number(...)`."""),

    q("json-parse-trusted-type", r'''
        const o = JSON.parse('{"n":"5"}') as { n: number };
        console.log(o.n + 1, o.n * 2);
    ''', "51 10", ["6 10", "51 NaN", "6 6"],
      "JSON.parse returns whatever the text says, whatever type you assert",
      """The assertion claims `n` is a number, but the text holds the string "5". `+` then concatenates to "51"
      while `*` quietly coerces the string to a number and gives 10."""),

    q("non-null-assertion-lies", r'''
        const m = new Map<string, number>();
        const v = m.get("a")!;
        console.log(v, v + 1);
    ''', "undefined NaN", ["0 1", "undefined undefined", "null 1"],
      "The ! after an expression silences the checker, it does not check anything",
      """`Map.get` returns undefined for a missing key; the `!` tells the compiler to treat it as a number
      anyway. At runtime nothing is checked, so `v` is undefined and `v + 1` is NaN."""),

    q("excess-property-runtime", r'''
        const a = { x: 1, y: 2 };
        const p: { x: number } = a;
        console.log(JSON.stringify(p), Object.keys(p).length);
    ''', '{"x":1,"y":2} 2', ['{"x":1} 1', '{"x":1} 2', '{"x":1,"y":2} 1'],
      "Assigning to a narrower type hides properties from the checker, not from the object",
      """Excess property errors only apply to fresh object literals. Here `a` is first stored in a variable, so
      `p` is the same object with its extra `y` intact, and `JSON.stringify` prints everything."""),

    q("readonly-is-compile-time", r'''
        const ro: { readonly x: number } = { x: 1 };
        const rw: { x: number } = ro;
        rw.x = 2;
        console.log(ro.x);
    ''', "2", ["1", "undefined", "NaN"],
      "readonly vanishes when you assign to a mutable type of the same shape",
      """TypeScript lets `{ readonly x }` flow into `{ x }`, and the keyword leaves no trace in the emitted code.
      Both names point at one ordinary object, so the write through `rw` is visible through `ro`."""),

    q("as-const-not-frozen", r'''
        const arr = [1, 2] as const;
        (arr as unknown as number[]).push(3);
        console.log(arr.length);
    ''', "3", ["2", "Error", "undefined"],
      "as const makes the type readonly, not the array",
      """`as const` narrows the compile-time type to a readonly tuple, and then nothing is left of it at runtime.
      The array is a normal array and happily grows; only `Object.freeze` stops that."""),

    q("private-is-not-private", r'''
        class A {
            private a = 1;
            #b = 2;
            c = 3;
        }
        console.log(Object.keys(new A()).join());
    ''', "a,c", ["a,#b,c", "c", "a,b,c"],
      "TypeScript's private is a checker rule; #b is genuinely hidden",
      """A `private` field compiles to a normal property, so `Object.keys` lists it. A `#name` field is real
      JavaScript privacy and does not appear as a property at all."""),

    q("structural-instanceof", r'''
        class A { x = 1; }
        class B { x = 1; }
        const a: A = new B();
        console.log(a instanceof A, a instanceof B);
    ''', "false true", ["true true", "true false", "false false"],
      "Types match by shape, but instanceof checks the prototype chain",
      """Because `A` and `B` have the same shape, the assignment compiles. At runtime the object is a `B`, and
      `instanceof` follows prototypes, not shapes."""),

    q("array-covariance", r'''
        interface Animal { name: string }
        interface Dog extends Animal { bark: () => string }
        const dogs: Dog[] = [{ name: "d", bark: () => "woof" }];
        const animals: Animal[] = dogs;
        animals.push({ name: "cat" });
        console.log(dogs.length, typeof dogs[1].bark);
    ''', "2 undefined", ["1 function", "2 function", "1 undefined"],
      "A Dog[] can be used as an Animal[], and then anything animal-shaped goes in",
      """TypeScript treats arrays as covariant, so `animals` and `dogs` are the same array. Pushing a cat through
      the Animal view puts a non-Dog in what the Dog view still believes is all dogs."""),

    q("object-key-order", r'''
        const o = { b: 1, 2: 1, a: 1, 1: 1 };
        console.log(Object.keys(o).join(","));
    ''', "1,2,b,a", ["b,2,a,1", "b,a,2,1", "2,1,b,a"],
      "Integer-like keys come first in ascending order, then the rest in insertion order",
      """Property order is not simply the order written. Keys that look like array indexes are sorted numerically
      and listed before every other string key, which keep the order they were added."""),

    q("json-drops-values", r'''
        const o = { a: undefined, b: null, c: () => 1, d: NaN };
        console.log(JSON.stringify(o));
    ''', '{"b":null,"d":null}', ['{"b":null}', '{"a":null,"b":null,"d":null}', '{"b":null,"c":null,"d":null}'],
      "JSON skips undefined and functions, and writes NaN as null",
      """Properties whose value is undefined or a function are left out of the object entirely. `NaN` and
      `Infinity` have no JSON form, so they become `null`, which also looks like the genuine null of `b`."""),

    q("undefined-overrides-in-spread", r'''
        const over: { a?: number } = { a: undefined };
        const merged = { ...{ a: 1 }, ...over };
        console.log(merged.a);
    ''', "undefined", ["1", "null", "0"],
      "A later spread overwrites with undefined too",
      """Spread copies every own property, including ones whose value is undefined, and a later source wins. The
      optional `a?: number` in the type allows exactly this, which is why merging options this way surprises
      people."""),

    q("optional-in-operator", r'''
        const o: { x?: number } = { x: undefined };
        console.log("x" in o, o.x === undefined, Object.keys(o).length);
    ''', "true true 1", ["false true 0", "true false 1", "false false 0"],
      "A property set to undefined still exists",
      """`in` and `Object.keys` ask whether the property exists, and it does, holding the value undefined. Reading
      it and comparing with undefined cannot tell it apart from a missing property."""),

    q("optional-call-skips-arguments", r'''
        let n = 0;
        const o: { a?: number[] } = {};
        o.a?.push(n++);
        console.log(n);
    ''', "0", ["1", "undefined", "-1"],
      "Optional chaining short-circuits the whole call, arguments included",
      """When `o.a` is undefined, `?.` stops evaluating the rest of the chain, and the arguments of `push(n++)`
      are never computed. So `n` is still 0."""),

    q("destructuring-default-null", r'''
        const src: { a?: number; b: number | null } = { a: undefined, b: null };
        const { a = 5, b = 5 } = src;
        console.log(a, b);
    ''', "5 null", ["5 5", "undefined null", "undefined 5"],
      "A destructuring default replaces undefined, but not null",
      """Defaults apply only when the value is `undefined`. `null` counts as a real value and is kept, so `b`
      stays null while `a` gets its default."""),

    # ── Enums and classes: where TypeScript emits real code ────────────────
    q("numeric-enum-reverse", r'''
        enum Color { Red, Green = 5, Blue }
        console.log(Color[0], Color.Blue, Color[6], Object.keys(Color).length);
    ''', "Red 6 Blue 6", ["Red 2 Blue 3", "Red 6 undefined 3", "undefined 6 Blue 6"],
      "Numeric enums also map numbers back to names, doubling the keys",
      """A numeric enum compiles to an object with both `Color.Red = 0` and `Color[0] = "Red"`. Blue follows Green
      at 6, and the object has six keys: three names and three numbers."""),

    q("string-enum-no-reverse", r'''
        enum S { A = "a", B = "b" }
        console.log(Object.keys(S).length, (S as any)["a"]);
    ''', "2 undefined", ["4 A", "2 A", "4 undefined"],
      "String enums have no reverse mapping",
      """Only numeric members get the reverse entry. The string enum object has just the two names `A` and `B`, so
      looking up by value "a" finds nothing."""),

    q("this-arrow-versus-method", r'''
        class C {
            n = 1;
            m() { return this.n; }
            a = () => this.n;
        }
        const c = new C();
        const other = { n: 2 };
        console.log(c.m.call(other), c.a.call(other));
    ''', "2 1", ["1 1", "2 2", "1 2"],
      "A method takes its this from the call; an arrow field captured it at construction",
      """`call(other)` rebinds `this` for the prototype method, so it reads 2. The arrow function assigned in the
      field initialiser closed over the instance and ignores any new `this`, so it still reads 1."""),

    q("getter-spread-snapshot", r'''
        let n = 0;
        const o = { get v() { return ++n; } };
        const c = { ...o };
        console.log(o.v, o.v, c.v, c.v);
    ''', "2 3 1 1", ["1 2 3 4", "2 3 4 5", "1 1 1 1"],
      "Spreading reads a getter once and stores the plain value",
      """The spread calls the getter one time (making `n` 1) and `c.v` is a data property holding 1 from then on.
      The original `o.v` still runs the getter every time, so it gives 2 and then 3."""),

    q("field-initialiser-order", r'''
        class A {
            x = this.init();
            init(): string { return "A"; }
        }
        class B extends A {
            y = "B";
            init(): string { return this.y; }
        }
        const b = new B();
        console.log(b.x, b.y);
    ''', "undefined B", ["B B", "A B", "undefined undefined"],
      "The base class's initialisers run before the subclass's fields exist",
      """`new B()` runs A's field initialisers first, and A's `x = this.init()` calls B's override. B's own field
      `y` has not been assigned yet, so `this.y` is undefined and gets stored in `x`."""),

    q("static-inherited-write", r'''
        class A {
            static count = 0;
            static inc() { return ++this.count; }
        }
        class B extends A {}
        B.inc(); B.inc(); A.inc();
        console.log(A.count, B.count);
    ''', "1 2", ["3 3", "3 0", "1 1"],
      "A static inherited through extends is read through the parent, but a write creates its own",
      """`B.inc()` reads `this.count` from A (0) through the prototype chain, but `++` writes back to `B` itself,
      creating B's own `count`. From then on the two classes count separately."""),

    q("method-extracted-loses-this", r'''
        class Counter {
            n = 0;
            inc() { this.n++; return this.n; }
        }
        const c = new Counter();
        const f = c.inc.bind(c);
        const g = c.inc;
        f(); f();
        console.log(c.n, g.call({ n: 10 }));
    ''', "2 11", ["2 1", "0 11", "2 3"],
      "bind pins this; a bare reference to the method takes whatever this the call gives it",
      """`f` is bound to `c` and ran twice, so `c.n` is 2. `g` is just the function, and `g.call({ n: 10 })`
      runs it on that other object, which becomes 11."""),

    q("class-expression-name", r'''
        const Make = class Named {
            who() { return Named.name; }
        };
        console.log(Make.name, new Make().who());
    ''', "Named Named", ["Make Make", "Make Named", "Named Make"],
      "A named class expression keeps its own name, not the variable's",
      """The `name` of a class comes from its own identifier when it has one; the variable name is used only for
      anonymous classes. Inside the body, `Named` is visible even though outside only `Make` is."""),

    # ── Runtime semantics worth knowing ────────────────────────────────────
    q("default-arg-fresh-each-call", r'''
        function add(list: number[] = []): number {
            list.push(1);
            return list.length;
        }
        console.log(add(), add());
    ''', "1 1", ["1 2", "2 2", "0 0"],
      "A default value expression runs on every call",
      """Unlike languages that build the default once, JavaScript evaluates `= []` each time the argument is
      missing, so each call gets its own fresh empty array."""),

    q("default-arg-sees-earlier", r'''
        function f(a = 1, b = a + 1): string { return a + "," + b; }
        console.log([f(), f(10), f(undefined, 0), f(10, undefined)].join("|"));
    ''', "1,2|10,11|1,0|10,11", ["1,2|10,11|1,0|10,10", "1,2|10,2|1,0|10,2", "1,2|10,11|0,0|10,11"],
      "Defaults can use earlier parameters, and passing undefined triggers them",
      """`b = a + 1` is computed after `a` is settled. An explicit `undefined` argument counts as missing and
      takes the default, while an explicit 0 does not."""),

    q("generator-laziness", r'''
        const log: string[] = [];
        function* g() { log.push("a"); yield 1; log.push("b"); yield 2; }
        const it = g();
        log.push("created");
        it.next();
        log.push("first");
        it.next();
        log.push("second");
        console.log(log.join());
    ''', "created,a,first,b,second", ["a,created,b,first,second", "created,first,second,a,b", "a,b,created,first,second"],
      "Calling a generator runs nothing; each next() runs to the next yield",
      """The body does not start until the first `next()`, and it pauses at every `yield`. So "created" comes
      first, then "a" during the first next, and "b" only during the second."""),

    q("await-and-microtask-order", r'''
        const log: string[] = [];
        async function f() { log.push("f1"); await null; log.push("f2"); }
        f();
        log.push("main");
        Promise.resolve().then(() => log.push("p"))
            .then(() => console.log(log.join()));
    ''', "f1,main,f2,p", ["main,f1,f2,p", "f1,f2,main,p", "f1,main,p,f2"],
      "An async function runs synchronously until its first await",
      """`f()` pushes "f1" immediately and then pauses at `await`, handing control back, so "main" follows.
      The continuation of `f` was queued before the `.then` callback, so "f2" precedes "p"."""),

    q("timeout-after-promise", r'''
        const log: string[] = [];
        setTimeout(() => log.push("timeout"), 0);
        Promise.resolve().then(() => log.push("promise"));
        log.push("sync");
        setTimeout(() => console.log(log.join()), 20);
    ''', "sync,promise,timeout", ["sync,timeout,promise", "timeout,promise,sync", "promise,sync,timeout"],
      "Promise callbacks (microtasks) run before any timer callback",
      """The synchronous code finishes first. Then all pending microtasks, such as the promise callback, run before
      the event loop takes the next timer, even a 0 ms one."""),

    q("finally-overrides-return", r'''
        function a(): string { try { return "try"; } finally { return "finally"; } }
        function b(): number { let x = 1; try { return x; } finally { x = 2; } }
        console.log(a(), b());
    ''', "finally 1", ["try 1", "finally 2", "try 2"],
      "A return inside finally wins, but changing a variable after the return value is taken does not",
      """`finally` runs after the return value is chosen. A `return` there replaces it, so `a()` gives "finally".
      In `b` the value 1 was already captured, so setting `x = 2` afterwards changes nothing."""),

    q("hoisting-var-and-function", r'''
        function h(): string {
            const first = typeof k;
            var k: number | undefined = 1;
            return first + " " + typeof inner + " " + typeof k;
            function inner() {}
        }
        console.log(h());
    ''', "undefined function number", ["number function number", "undefined undefined number", "Error"],
      "var is declared at the top but assigned later; function declarations are fully hoisted",
      """`k` exists from the start of the function with the value undefined, and `typeof k` reads that before
      `var k = 1` runs. The nested function declaration is usable from line one."""),

    q("valueof-versus-tostring", r'''
        const o = { valueOf() { return 42; }, toString() { return "str"; } };
        console.log(`${o}`, o + "", (o as any) * 2, String(o));
    ''', "str 42 84 str", ["42 42 84 42", "str str 84 str", "str 42 str str"],
      "Template strings ask for text; + and * ask for the default or numeric value",
      """Template literals and `String()` prefer `toString`, giving "str". `+` uses the default hint, which tries
      `valueOf` first, so `o + ""` is "42"; `*` converts to a number from `valueOf` too, giving 84."""),

    q("date-month-overflow", r'''
        const d = new Date(Date.UTC(2020, 0, 31));
        d.setUTCMonth(1);
        console.log(d.toISOString().slice(0, 10));
    ''', "2020-03-02", ["2020-02-29", "2020-02-31", "2020-03-01"],
      "Setting the month keeps the day, and an impossible date rolls forward",
      """January 31 moved to February becomes February 31, and 2020 February has 29 days, so the date overflows by
      two days into March 2. `Date` never complains; it normalises."""),

    q("reduce-without-initial", r'''
        let calls = 0;
        const f = (a: number, b: number) => { calls++; return a + b; };
        console.log([7].reduce(f), [7].reduce(f, 0), calls);
    ''', "7 7 1", ["7 7 2", "7 7 0", "14 7 1"],
      "Without an initial value, a one-element reduce never calls the callback",
      """The first element is used as the starting accumulator, so with a single element there is nothing left to
      combine and the callback is skipped. Giving an initial value of 0 adds one call."""),

    q("set-and-map-same-value-zero", r'''
        const s = new Set([0, -0, NaN, NaN]);
        const m = new Map([[NaN, "x"]]);
        console.log(s.size, m.get(NaN), [NaN].indexOf(NaN));
    ''', "2 x -1", ["4 undefined -1", "3 x 0", "2 undefined 0"],
      "Set and Map use SameValueZero: NaN equals NaN and 0 equals -0",
      """The set keeps one zero and one NaN, so its size is 2, and the map finds its NaN key. `indexOf` still
      uses `===`, which is why the same lookup in an array fails."""),

    q("bitwise-int32", r'''
        console.log(1 << 31, (1 << 31) >>> 0, -5.9 | 0, 2 ** 32 + 5 | 0);
    ''', "-2147483648 2147483648 -5 5", ["2147483648 2147483648 -6 5", "-2147483648 -2147483648 -5 5", "2147483648 2147483648 -5 4294967301"],
      "Bitwise operators work on 32-bit signed integers",
      """Shifting a 1 into bit 31 makes the sign bit, so the result is negative. `>>> 0` reinterprets it as
      unsigned. `| 0` truncates toward zero and wraps modulo 2 to the 32nd power, so 2**32 + 5 becomes 5."""),

    q("typed-array-wrap-clamp", r'''
        const clamped = Array.from(new Uint8ClampedArray([300, -5, 1.5, 2.5]));
        console.log(clamped.join(), new Uint8Array([257, -1]).join());
    ''', "255,0,2,2 1,255", ["255,0,2,3 1,255", "44,0,1,2 1,255", "255,0,2,2 255,0"],
      "Uint8Array wraps around; Uint8ClampedArray clamps and rounds halves to even",
      """A plain Uint8Array stores the value modulo 256, so 257 is 1 and -1 is 255. The clamped one saturates at
      0 and 255, and rounds ties to the nearest even number: 1.5 to 2 and 2.5 to 2."""),

    q("number-is-always-double", r'''
        const big = 2 ** 53;
        console.log(big + 1 === big, big + 2);
    ''', "true 9007199254740994", ["false 9007199254740995", "true 9007199254740993", "false 9007199254740994"],
      "Above 2**53 a double cannot represent every integer",
      """Numbers are 64-bit floats with a 53-bit mantissa. From 2**53 up, the spacing is 2, so adding 1 rounds
      back to the same number and adding 2 lands on the next one."""),

    q("bigint-division", r'''
        console.log(String(7n / 2n), String(-7n / 2n), String(2n ** 64n),
            typeof 1n);
    ''', "3 -3 18446744073709551616 bigint",
      ["3.5 -3.5 18446744073709551616 number", "3 -4 18446744073709551616 bigint",
       "3 -3 0 bigint"],
      "BigInt division truncates toward zero, and BigInts never overflow",
      """Dividing two bigints gives an integer cut toward zero, so -7n / 2n is -3n. The power is exact, with all 20
      digits, because a bigint grows as needed."""),

    q("sort-default-uppercase-first", r'''
        console.log(["b", "a", "C", "B"].sort().join(""));
    ''', "BCab", ["abBC", "aBbC", "CBba"],
      "The default sort compares UTF-16 codes, so every capital precedes every lowercase letter",
      """Without a comparator, `sort` orders by code unit: uppercase letters are 65 to 90 and lowercase 97 to
      122. That gives B, C, a, b regardless of the alphabet."""),

    q("computed-key-coerces", r'''
        const a: any = {};
        a[{ x: 1 } as any] = 1;
        a[{ y: 2 } as any] = 2;
        console.log(Object.keys(a).length, a["[object Object]"]);
    ''', "1 2", ["2 2", "2 1", "1 1"],
      "Any object used as a property key becomes the string \"[object Object]\"",
      """Property names are strings or symbols, so each object key is converted with its `toString`, which gives
      the same text for both. The second assignment overwrites the first. A `Map` would keep them apart."""),

    q("numeric-keys-are-strings", r'''
        const o: Record<string, number> = {};
        o[1] = 1;
        o["1"] += 1;
        o["01"] = 5;
        o[0.5] = 7;
        console.log(Object.keys(o).join("|"), o[1]);
    ''', "1|01|0.5 2", ["1|1|01|0.5 1", "1|01|0.5 1", "1|0.5|01 2"],
      "o[1] and o[\"1\"] are the same property; \"01\" is a different one",
      """Every key is converted to its canonical string, so the number 1 and the text "1" meet at one property
      that ends at 2. "01" and "0.5" are different strings, kept in insertion order after the index-like key."""),

    q("loose-empty-array", r'''
        const e: any = [];
        console.log(e == false, !e, e + e === "");
    ''', "true false true", ["false false true", "true true true", "true false false"],
      "[] is truthy, yet == false, because == converts it to \"\" and then 0",
      """`!e` is false since every object is truthy. The loose comparison goes the other way: `[]` becomes the
      string "" and then 0, which equals false. Adding two arrays joins them as strings, giving ""."""),

    q("raw-string-escapes", r'''
        console.log("a\nb".length, String.raw`a\nb`.length);
    ''', "3 4", ["3 3", "4 4", "4 3"],
      "String.raw leaves backslash escapes uninterpreted",
      """A normal literal turns `\\n` into one newline character, so the length is 3. In the raw template the
      backslash and the n stay as two characters, making 4."""),

    q("number-radix", r'''
        console.log((255).toString(16), parseInt("ff", 16), parseInt("0x1f"),
            (0.5).toString(2), Number("0b101"), parseFloat("3.14abc"));
    ''', "ff 255 31 0.1 5 3.14",
      ["ff 255 0 0.1 5 3.14", "FF 255 31 0.1 5 NaN", "ff 255 31 0.5 101 3"],
      "Number conversion and parseInt differ in what they accept",
      """`parseInt` understands a 0x prefix on its own and stops reading at the first bad character, and so does
      `parseFloat`. `Number("0b101")` accepts binary literals as a whole string, giving 5."""),

    q("object-is-zero", r'''
        console.log(Object.is(-0, 0), Object.is(NaN, NaN), -0 === 0, 1 / -0);
    ''', "false true true -Infinity", ["true true true Infinity", "false false true -Infinity", "false true false -Infinity"],
      "-0 exists; === cannot see it, Object.is can",
      """`===` treats -0 and 0 as equal, but they are different values, and dividing by -0 gives minus infinity.
      `Object.is` compares by identity of value, so it separates the zeros and equates NaN with itself."""),

    q("shallow-spread-nested", r'''
        const a = { n: { v: 1 } };
        const b = { ...a };
        const c = JSON.parse(JSON.stringify(a)) as typeof a;
        b.n.v = 2;
        console.log(a.n.v, c.n.v);
    ''', "2 1", ["1 1", "1 2", "2 2"],
      "Spread copies one level: nested objects are still shared",
      """`b.n` is the very same inner object as `a.n`, so setting `v` through `b` changes `a`. The JSON
      round trip builds new objects at every level, which is why `c` is unaffected."""),

    q("labelled-continue", r'''
        let n = 0;
        outer: for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if (j === 1) continue outer;
                n += 10 + i;
            }
        }
        console.log(n);
    ''', "33", ["30", "9", "63"],
      "continue outer jumps to the next pass of the outer loop",
      """For each i only j = 0 does anything: it adds 10 + i, and at j = 1 the labelled `continue` skips the
      rest of the inner loop. That gives 10 + 11 + 12 = 33."""),

    q("swap-by-destructuring", r'''
        let a = 1, b = 2;
        [a, b] = [b, a + b];
        [a, b] = [b, a + b];
        console.log(a, b);
    ''', "3 5", ["2 3", "3 3", "5 8"],
      "The right side is fully evaluated before either variable is assigned",
      """The first line builds [2, 3] from the old values and then assigns both, so a is 2 and b is 3. The second
      does the same from there, ending with 3 and 5."""),

    q("delete-leaves-hole", r'''
        const a = [1, 2, 3];
        delete a[1];
        console.log(a.length, a.join("-"), 1 in a);
    ''', "3 1--3 false", ["2 1-3 false", "3 1-undefined-3 true", "3 1--3 true"],
      "delete removes the element but not the slot",
      """`delete` on an array element leaves a hole: the length stays 3, `join` prints an empty string for it, and
      the `in` test says index 1 no longer exists. `splice` is the call that closes the gap."""),
)
