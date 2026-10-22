"""Gotchas, TypeScript, the third helping: what the compiler emits (and what it quietly does not).

Same rules as content_typescript.py: tsc --strict --target es2020, then node. Every card compiles, prints one line,
and the wrong options are real misreads. The second deck was mostly plain JavaScript traps; this one leans on the
TypeScript features that leave something behind at runtime (enums, namespaces, parameter properties, accessors) and
on the ones that leave nothing (declare, overloads, type guards, generics, `this` parameters).
"""

from __future__ import annotations

from .items import Item, make

q = make("typescript")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ───────────────────────────────────────────────────────
    q("union-switch-fallthrough", r'''
        type S = { k: "a" } | { k: "b" } | { k: "c" };
        function f(s: S): string {
            let out = "";
            switch (s.k) {
                case "a": out += "A";
                case "b": out += "B"; break;
                case "c": out += "C";
            }
            return out;
        }
        console.log(f({ k: "a" }), f({ k: "b" }), f({ k: "c" }));
    ''', "AB B C", ["A B C", "AB AB C", "AB B BC"],
      "Narrowing by a discriminant does not stop a case from falling through",
      """The union is checked case by case, but the emitted code is a plain JavaScript switch. Case "a" has no
      `break`, so it runs on into case "b" and gives "AB"; `--strict` does not flag fallthrough."""),

    q("throw-a-string", r'''
        try {
            throw "boom";
        } catch (e) {
            console.log(e instanceof Error, typeof e, String(e));
        }
    ''', "false string boom", ["true object boom", "false object boom", "true string Error: boom"],
      "Anything can be thrown, so a caught value is not necessarily an Error",
      """JavaScript lets you throw a string, and the string arrives untouched. That is why `catch (e)` is typed
      `unknown` under `--strict`: you have to check with `instanceof Error` before using `.message`."""),

    q("declare-makes-nothing", r'''
        declare const VERSION: string;
        console.log(typeof VERSION);
    ''', "undefined", ["string", "object", "VERSION"],
      "declare only tells the compiler a name exists; it emits no variable",
      """`declare const VERSION: string` is erased completely, so nothing is defined at runtime. Reading the name
      itself would throw a ReferenceError, but `typeof` of an undeclared name is allowed and says "undefined"."""),

    q("nullish-chain-length", r'''
        const s: string | null = "";
        console.log(s?.length, s?.length ?? -1, s?.length || -1);
    ''', "0 0 -1", ["0 -1 -1", "undefined -1 -1", "0 0 0"],
      "?. only guards null and undefined; || also replaces a real 0",
      """The empty string is not null, so `s?.length` is 0, and `??` keeps it. `||` treats 0 as falsy and falls
      back to -1."""),

    q("all-settled-labels", r'''
        async function main() {
            const jobs = [Promise.resolve(1), Promise.reject("x"), 3];
            const r = await Promise.allSettled(jobs);
            const tags = r.map(x => x.status[0] +
                (x.status === "fulfilled" ? x.value : x.reason));
            console.log(tags.join());
        }
        main();
    ''', "f1,rx,f3", ["f1,r3", "f1,rx", "1,x,3"],
      "allSettled never rejects: every input becomes a status record",
      """Where `Promise.all` would reject on the first failure, `allSettled` waits for all three and reports each as
      `fulfilled` with a value or `rejected` with a reason. The plain value 3 counts as an already fulfilled
      promise."""),

    q("bigint-past-2-53", r'''
        const big = BigInt(2 ** 53) + 1n;
        console.log(`${big} ${2 ** 53 + 1}`);
    ''', "9007199254740993 9007199254740992", ["9007199254740992 9007199254740992",
                                              "9007199254740993 9007199254740993",
                                              "9007199254740993n 9007199254740992"],
      "BigInt keeps every digit; a double stops at 2 ** 53",
      """Doubles have 53 bits of precision, so 2 ** 53 + 1 rounds back to 2 ** 53. A BigInt is exact, and in a
      template literal it prints without the trailing `n` that `console.log` would show."""),

    q("never-check-at-runtime", r'''
        type Shape = { kind: "circle" } | { kind: "square" };
        function area(s: Shape): number {
            switch (s.kind) {
                case "circle": return 3;
                case "square": return 4;
                default:
                    const check: never = s;
                    return -1;
            }
        }
        console.log(area({ kind: "triangle" } as unknown as Shape));
    ''', "-1", ["0", "4", "NaN"],
      "Exhaustiveness checking with never is compile-time only",
      """The `never` assignment makes the compiler complain when a new variant is added. At runtime a value outside
      the union simply reaches the `default` branch, which here returns -1."""),

    q("unknown-typeof-ladder", r'''
        function show(v: unknown): string {
            if (typeof v !== "object") return typeof v;
            return v === null ? "null" : Array.isArray(v) ? "array" : "obj";
        }
        console.log([null, [], {}, () => 1, "a"].map(show).join());
    ''', "null,array,obj,function,string", ["object,array,obj,function,string",
                                           "null,object,object,function,string",
                                           "null,array,obj,object,string"],
      "typeof says 'object' for null and arrays, so test them first",
      """Narrowing `unknown` with `typeof v === "object"` includes null and arrays, which the code then separates
      by hand. A function is not an "object" to typeof; it has its own answer."""),

    q("namespace-private-state", r'''
        namespace Counter {
            let n = 0;
            export function next(): number { return ++n; }
        }
        console.log(Counter.next(), Counter.next(), Object.keys(Counter).join());
    ''', "1 2 next", ["1 2 n,next", "1 1 next", "1 2 "],
      "A namespace is an object built by a function; only exported names become properties",
      """The compiled namespace is an IIFE that closes over `n` and attaches `next` to an object. The counter is
      private state in the closure, so `Object.keys` lists only `next`."""),

    q("new-target-in-base", r'''
        abstract class Base {
            readonly kind: string;
            constructor() { this.kind = new.target.name.toLowerCase(); }
        }
        class Dog extends Base {}
        class Cat extends Base {}
        console.log(new Dog().kind, new Cat().kind);
    ''', "dog cat", ["base base", "Dog Cat", "dog base"],
      "new.target names the class that was actually constructed, not the one running",
      """Inside the base constructor, `this` is already a Dog or a Cat, and `new.target` is the class `new` was
      called on. `abstract` is erased, so the base class code runs like any other."""),

    q("optional-argument-count", r'''
        function f(a: number, b?: number): number { return arguments.length; }
        console.log(f(1), f(1, undefined), f.length);
    ''', "1 2 2", ["1 1 2", "1 2 1", "2 2 2"],
      "An optional parameter still counts in length; passing undefined still counts as passing",
      """`arguments.length` is how many values the caller wrote, so passing an explicit `undefined` makes it 2.
      The `?` is erased, so `f.length` counts both declared parameters."""),

    q("type-guard-number", r'''
        function isNum(x: unknown): x is number { return typeof x === "number"; }
        const list: unknown[] = [5, NaN, new Number(5), Infinity, "5"];
        console.log(list.filter(isNum).length);
    ''', "3", ["1", "2", "4"],
      "typeof 'number' is true for NaN and Infinity, false for a Number object",
      """NaN and Infinity are numbers, so they pass; `new Number(5)` is a wrapper object with typeof "object", and
      the string "5" is not a number. The guard only returns whatever the function body decides."""),

    q("definite-assignment-nan", r'''
        let total!: number;
        function add(): void { total += 1; }
        add();
        console.log(total);
    ''', "NaN", ["1", "0", "undefined"],
      "The ! after a name silences the checker; it does not initialise anything",
      """`let total!: number` promises the compiler that the variable is set before use, but nothing sets it. It
      stays undefined, and `undefined + 1` is NaN."""),

    q("enum-auto-increment", r'''
        enum Level { Low = 10, Mid, High = Low + 5, Top }
        console.log(`${Level.Mid} ${Level.Top} ${Level[12]}`);
    ''', "11 16 undefined", ["1 3 Mid", "11 16 Top", "11 15 undefined"],
      "An enum member without a value takes the previous member's value plus one",
      """Mid follows Low (10), so it is 11, and Top follows High (15), so it is 16, not 3. Nothing is called 12, so
      the reverse lookup gives undefined."""),

    # ── Medium: what the compiler emits ────────────────────────────────────
    q("enum-duplicate-values", r'''
        enum E { A = 1, B = 1, C }
        console.log(E[1], E.C, Object.keys(E).join());
    ''', "B 2 1,2,A,B,C", ["A 2 1,2,A,B,C", "B 2 A,B,C", "B 3 1,A,B,C,2"],
      "Two members with one value share a reverse entry, and the last writer wins",
      """The compiled enum assigns `E[E["A"] = 1] = "A"` and then the same for B, so the reverse entry for 1 ends up
      as "B". C follows B at 2, which also gets a reverse entry. Integer-like keys come first in `Object.keys`."""),

    q("enum-namespace-merge", r'''
        enum Color { Red, Green }
        namespace Color {
            export function parse(s: string): Color {
                return Color[s as "Red" | "Green"];
            }
        }
        console.log(Color.parse("Green"), Object.keys(Color).join());
    ''', "1 0,1,Red,Green,parse", ["1 Red,Green,parse", "Green 0,1,Red,Green,parse",
                                  "1 0,1,Red,Green"],
      "A namespace merged into an enum adds ordinary properties to the same object",
      """The enum and the namespace compile into one object, so `parse` becomes a key beside the names and the
      reverse-mapped numbers. `Color["Green"]` is the number 1."""),

    q("param-property-json", r'''
        class P {
            constructor(public x: number, private y = x * 2, z = 9) {}
        }
        console.log(JSON.stringify(new P(3)));
    ''', '{"x":3,"y":6}', ['{"x":3}', '{"x":3,"y":6,"z":9}', '{"x":3,"z":9}'],
      "Only parameters with a modifier become fields; private is still a field",
      """`public x` and `private y` each turn into `this.x = x` and `this.y = y` in the constructor, and the
      default `x * 2` is evaluated first. `z` has no modifier, so it stays a plain parameter and vanishes."""),

    q("param-property-key-order", r'''
        class A {
            z = 1;
            constructor(public x: number) {}
        }
        console.log(Object.keys(new A(5)).join());
    ''', "x,z", ["z,x", "x", "z"],
      "With this target, parameter properties are assigned before the field initialisers",
      """tsc emits `this.x = x` at the top of the constructor and then the field initialisers, so `x` is created
      first even though `z` is written first in the class. (With `useDefineForClassFields` the order would be
      different.)"""),

    q("uninitialised-fields-absent", r'''
        class A {
            x!: number;
            y?: string;
            z = undefined;
            w: number | undefined;
        }
        const a = new A();
        console.log(Object.keys(a).join(), "x" in a, "z" in a);
    ''', "z false true", ["x,y,z,w true true", "z true true", "x,z false true"],
      "A field with no initialiser leaves no property behind",
      """`x!`, `y?` and `w` are only types for the checker, so they emit nothing and `"x" in a` is false. Only
      `z = undefined` runs an assignment, so it is the one own property, even though its value is undefined."""),

    q("accessor-keys-and-json", r'''
        class T {
            private _c = 0;
            get c(): number { return this._c; }
            set c(v: number) { this._c = v < 0 ? 0 : v; }
        }
        const t = new T();
        t.c = -5;
        console.log(t.c, JSON.stringify(t), Object.keys(t).join());
    ''', '0 {"_c":0} _c', ['0 {"c":0} c', '-5 {"_c":-5} _c', '0 {"c":0,"_c":0} c,_c'],
      "Accessors live on the prototype, so only the backing field is an own property",
      """The setter clamps -5 to 0. `JSON.stringify` and `Object.keys` look at own enumerable properties, and `c`
      is defined on `T.prototype`, so they see the private-by-name field `_c` instead."""),

    q("setter-only-reads-undefined", r'''
        class A {
            private _v = 1;
            set v(x: number) { this._v = x; }
        }
        const a = new A();
        a.v = 5;
        console.log(a.v, (a as unknown as { _v: number })._v);
    ''', "undefined 5", ["5 5", "1 5", "undefined 1"],
      "A property with only a setter reads as undefined, and the checker does not mind",
      """With no getter there is nothing to run on a read, so `a.v` is undefined even though the type says number.
      The write did happen: the setter stored 5 in `_v`."""),

    q("record-prototype-keys", r'''
        const r: Record<string, number> = {};
        console.log(r["toString"] === undefined, typeof r["constructor"], "a" in r);
    ''', "false function false", ["true undefined false", "false number false", "true function false"],
      "A Record<string, number> still inherits from Object.prototype",
      """The type promises numbers for every string key, but an empty object literal has `toString` and
      `constructor` from its prototype, so those lookups find functions. Use a `Map`, or `Object.create(null)`, for
      arbitrary keys."""),

    q("function-length-defaults", r'''
        function f(a: number, b?: number) { return a + (b ?? 0); }
        function g(a: number, b = 2, c = 3) { return a + b + c; }
        function h(a = 1, b: number) { return a + b; }
        console.log(f.length, g.length, h.length);
    ''', "2 1 0", ["2 3 2", "1 1 1", "2 1 1"],
      "length counts parameters before the first default value",
      """`b?` is erased, so f has two parameters. For g, only `a` comes before the first default, and for h the
      very first parameter has one, so its length is 0 even though `b` is required."""),

    q("this-parameter-erased", r'''
        function f(this: { n: number }, k: number): number { return this.n + k; }
        const o = { n: 10, f };
        console.log(o.f(1), f.call({ n: 100 }, 1), f.length);
    ''', "11 101 1", ["11 101 2", "1 101 1", "11 11 1"],
      "A this parameter is checked and then erased; it is not a real argument",
      """The fake first parameter exists only for the checker, so the emitted function takes just `k` and
      `f.length` is 1. `this` comes from the call site: the object `o` for `o.f(1)`, the argument for `.call`."""),

    q("overload-signature-lies", r'''
        function twice(x: string): string;
        function twice(x: number): number;
        function twice(x: any): any {
            return typeof x === "string" ? x.length * 2 : x * 2;
        }
        const s: string = twice("abc");
        console.log(s + 1);
    ''', "7", ["abcabc1", "61", "NaN"],
      "Overload signatures are promises to the checker; the one body decides",
      """The body returns a number for a string input, but the overload says string, so `s` is typed string while
      holding 6. At runtime `+` sees two numbers and adds them. All the signatures are erased."""),

    q("symbol-keys", r'''
        const s = Symbol("k");
        const o = { [s]: 1, a: 2 };
        console.log(Object.keys(o).length, JSON.stringify(o), s in o,
            Symbol("k") === s);
    ''', '1 {"a":2} true false', ['2 {"a":2,"k":1} true false', '1 {"a":2} true true',
                                  '2 {"a":2} false false'],
      "Symbol keys are skipped by keys and JSON, and every Symbol() is unique",
      """Symbol-keyed properties are real, so `in` finds them, but `Object.keys` and `JSON.stringify` only look at
      string keys. A second `Symbol("k")` has the same description and is still a different symbol."""),

    q("json-round-trip-loses-types", r'''
        const src = { d: new Date(0), m: new Map([["a", 1]]) };
        const back = JSON.parse(JSON.stringify(src)) as typeof src;
        const n = Object.keys(back.m).length;
        console.log(back.d instanceof Date, typeof back.d, n);
    ''', "false string 0", ["true object 0", "false string 1", "true string 1"],
      "JSON.parse hands back plain data, whatever type you assert",
      """A Date is written as its ISO string and a Map has no own properties to write, so it becomes `{}`. The
      `as typeof src` cast changes only what the checker believes, not what the object is."""),

    q("array-spread-fills-holes", r'''
        const a = [...Array(3)].map((_, i) => i).join();
        const b = Array(3).map((_, i) => i).join();
        console.log(a + "|" + b);
    ''', "0,1,2|,,", ["0,1,2|0,1,2", ",,|,,", "0,1,2|"],
      "Spread turns holes into undefined; map skips holes",
      """`[...Array(3)]` reads each empty slot as undefined, so `map` has real elements to number. `Array(3).map`
      skips the holes and returns another hole-filled array, which joins as two commas."""),

    q("for-in-walks-the-prototype", r'''
        const base = { x: 1 };
        const o: Record<string, number> = Object.create(base);
        o.y = 2;
        const seen: string[] = [];
        for (const k in o) seen.push(k);
        console.log(seen.join(), Object.keys(o).join());
    ''', "y,x y", ["y y", "y,x y,x", "x,y y"],
      "for...in includes inherited enumerable keys; Object.keys does not",
      """`o` has one own property, `y`, and inherits `x` from `base`. `for...in` lists own keys first and then the
      inherited ones, while `Object.keys` stops at the own ones."""),

    q("frozen-write-throws", r'''
        const o = Object.freeze({ a: 1 });
        try {
            (o as { a: number }).a = 2;
            console.log("silent", o.a);
        } catch (e) {
            console.log((e as Error).name, o.a);
        }
    ''', "TypeError 1", ["silent 1", "silent 2", "TypeError 2"],
      "Writing to a frozen object fails silently in sloppy JS, but throws in strict code",
      """`--strict` makes tsc emit "use strict", and in strict mode a write to a frozen property is a TypeError.
      The cast gets past the `readonly` the checker had given `a`, but not past the freeze."""),

    q("generic-argument-is-not-a-value", r'''
        function zero<T>(): T { return 0 as unknown as T; }
        const s = zero<string>();
        console.log(typeof s, s.length, Object.is(zero<string>(), zero<number>()));
    ''', "number undefined true", ["string 0 true", "string undefined false", "number undefined false"],
      "The type argument is erased, so the function cannot behave differently for T",
      """Both calls run the identical code and return the number 0. The checker believes `s` is a string, but a
      number has no `length`, so that reads undefined."""),

    q("instantiation-expression-erased", r'''
        function id<T>(x: T): T { return x; }
        const idString = id<string>;
        console.log(idString === id, idString("a"));
    ''', "true a", ["false a", "true undefined", "false undefined"],
      "id<string> without a call is only a narrowed type for the same function",
      """An instantiation expression fixes the type parameter for the checker and then disappears, leaving the
      plain name `id`. Both constants refer to one function object."""),

    q("rest-tuple-length-zero", r'''
        function f(...[a, b]: [x: number, y: number]): number { return a * b; }
        const pair: [number, number] = [2, 3];
        console.log(f(...pair), f.length);
    ''', "6 0", ["6 2", "5 2", "6 1"],
      "A rest parameter with a tuple type reads like two parameters but counts as none",
      """The labelled tuple makes the call require exactly two numbers, but it is still a rest parameter in the
      emitted function, and rest parameters are not counted in `length`."""),

    q("static-initialiser-order", r'''
        class A {
            static a = 1;
            static b = A.a + 1;
            static { A.a = 10; }
            static c = A.a + A.b;
        }
        console.log(A.a, A.b, A.c);
    ''', "10 2 12", ["10 11 21", "1 2 3", "10 2 3"],
      "Static fields and static blocks run once, top to bottom, as the class is defined",
      """`b` is computed while `a` is still 1, so it is 2 and stays 2. The static block then sets `a` to 10, and
      `c` is created after it, so it sees both the new `a` and the old `b`."""),

    q("map-grows-while-iterating", r'''
        const m = new Map<number, string>([[1, "a"]]);
        let n = 0;
        for (const [k] of m) {
            if (k < 4) m.set(k + 1, "x");
            n++;
        }
        console.log(n, m.size);
    ''', "4 4", ["1 4", "1 1", "4 1"],
      "Entries added during iteration are visited later in the same loop",
      """A Map iterator follows insertion order and checks for new entries as it goes. Visiting 1 adds 2, then 3,
      then 4, and 4 adds nothing, so the loop body runs four times."""),

    q("bigint-wrap-and-truncate", r'''
        const a = BigInt.asUintN(8, 257n);
        const b = BigInt.asIntN(8, 255n);
        console.log(`${a} ${b} ${-7n / 2n} ${-7n % 2n}`);
    ''', "1 -1 -3 -1", ["1 -1 -4 1", "257 255 -3 -1", "1 255 -3 -1"],
      "BigInt division truncates toward zero, and asIntN/asUintN wrap to a bit width",
      """257 is 1 modulo 256, and 255 read as an 8-bit signed number is -1. BigInt `/` and `%` follow the sign of
      the dividend, as for Number, so -7 / 2 is -3 and -7 % 2 is -1."""),

    q("spread-instance-drops-methods", r'''
        class P {
            n = 1;
            m(): number { return 2; }
        }
        const c = { ...new P() };
        console.log(typeof (c as { m?: unknown }).m, c instanceof P);
    ''', "undefined false", ["function true", "function false", "undefined true"],
      "Object spread copies own enumerable properties, so methods and the class are lost",
      """Methods live on `P.prototype`, not on the instance, so the spread does not copy them. The result is a
      plain object with only `n`, which is not an instance of P."""),

    q("abstract-method-leaves-no-stub", r'''
        abstract class Shape {
            abstract area(): number;
        }
        const Loose = Shape as unknown as new () => Shape;
        const s = new Loose();
        console.log(typeof s.area, s instanceof Shape);
    ''', "undefined true", ["function true", "undefined false", "function false"],
      "abstract is erased: the class is a normal class and abstract methods emit nothing",
      """The compiler refuses `new Shape()`, but a cast gets round that, and the runtime then builds an ordinary
      instance. There is no `area` anywhere, because an abstract member has no body to emit."""),

    q("generator-closed-by-destructuring", r'''
        const log: string[] = [];
        function* g() {
            try { yield 1; yield 2; yield 3; } finally { log.push("closed"); }
        }
        const [a, b] = g();
        console.log(`${a}${b} ${log.join()}`);
    ''', "12 closed", ["12 ", "123 closed", "12 closed,closed"],
      "Array destructuring closes an iterator it did not use up",
      """Taking two values leaves the generator suspended. The destructuring then calls the iterator's `return()`,
      which runs the `finally` block and logs "closed", before the next line prints."""),

    q("enum-values-both-ways", r'''
        enum C { A, B }
        const names = Object.values(C).filter(v => typeof v === "string");
        console.log(Object.values(C).join(), names.length);
    ''', "A,B,0,1 2", ["0,1 2", "A,B 2", "A,B,0,1 4"],
      "Object.values on a numeric enum returns the names and the numbers",
      """The enum object holds `0: "A"` and `1: "B"` as well as `A: 0` and `B: 1`. Integer keys sort first, giving
      the names before the numbers, and a `typeof` filter is needed to pick one half."""),
)
