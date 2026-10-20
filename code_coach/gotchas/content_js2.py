"""Gotchas, JavaScript, the second helping: more programs where the obvious reading is a trap.

Same rules as content_js.py: every answer is held to a real node run by tests/test_gotchas_content.py,
the wrong options are real misreads, nothing depends on randomness, the clock or identity, and each
program prints one line (console.log once; event-loop programs collect their steps and print at the end).
Programs are CommonJS scripts, so no top-level `var` globals and no `window`. These cards come after the
first module in the deck.
"""

from __future__ import annotations

from .items import Item, make

q = make("javascript")

ITEMS: tuple[Item, ...] = (
    # ── Arrays and strings ─────────────────────────────────────────────────
    q("array-from-fill", '''
        const a = Array.from({ length: 3 }, (_, i) => i * 2);
        console.log(a, Array(3).fill(0), [...Array(2)]);
    ''', "[ 0, 2, 4 ] [ 0, 0, 0 ] [ undefined, undefined ]",
      ["[ <3 empty items> ] [ 0, 0, 0 ] [ <2 empty items> ]", "[ 0, 1, 2 ] [ 0, 0, 0 ] [ undefined, undefined ]",
       "[ 0, 2, 4 ] [ <3 empty items> ] [ <2 empty items> ]"],
      "Array.from, fill and spread all turn holes into real values",
      """`Array.from({ length: 3 })` builds three real slots and runs the mapper on each. `fill` writes into
      the holes, and spreading `Array(2)` reads each hole as `undefined`, unlike `map`, which skips them."""),

    q("fill-shared-array", '''
        const a = Array(2).fill([]);
        a[0].push(1);
        console.log(a);
    ''', "[ [ 1 ], [ 1 ] ]", ["[ [ 1 ], [] ]", "[ [], [] ]", "[ 1, [] ]"],
      "fill puts the same object in every slot",
      """`fill([])` creates one empty array and stores that single reference in every position, so pushing
      through one slot shows in the other. Use `Array.from({ length: 2 }, () => [])` for separate arrays."""),

    q("spread-string-object", '''
        console.log({ ..."ab" }, [..."ab"]);
    ''', "{ '0': 'a', '1': 'b' } [ 'a', 'b' ]", ["[ 'a', 'b' ] [ 'a', 'b' ]", "{ a: 'a', b: 'b' } [ 'a', 'b' ]",
                                               "TypeError"],
      "Spreading a string into an object uses its indexes as keys",
      """In an array, `...` walks the string's characters. In an object, it copies the string's own
      enumerable properties, which are the indexes "0" and "1"."""),

    q("array-constructor", '''
        const len = (a) => a.length;
        console.log(len(new Array(3)), len(new Array(3, 4)), len(Array.of(3)),
          len(new Array("3")));
    ''', "3 2 1 1", ["1 2 1 1", "3 2 3 1", "3 1 1 3"],
      "A lone number makes an empty array of that length",
      """`new Array(3)` means "three empty slots" but `new Array(3, 4)` means the two items 3 and 4. `Array.of`
      and a lone string always make an array that holds what you gave."""),

    q("array-delete-hole", '''
        const a = [1, 2, 3];
        delete a[1];
        console.log(a, a.length);
    ''', "[ 1, <1 empty item>, 3 ] 3", ["[ 1, 3 ] 2", "[ 1, undefined, 3 ] 3", "[ 1, <1 empty item>, 3 ] 2"],
      "delete leaves a hole and keeps the length",
      """`delete a[1]` removes the property, but the array does not shift or shrink; slot 1 is now empty. Use
      `splice(1, 1)` when you want the later items to move down."""),

    q("push-vs-concat", '''
        const a = [1];
        const n = a.push(2, 3);
        const c = a.concat([4], 5, [[6]]);
        console.log(n, c);
    ''', "3 [ 1, 2, 3, 4, 5, [ 6 ] ]", ["[ 1, 2, 3 ] [ 1, 2, 3, 4, 5, 6 ]", "3 [ 1, 2, 3, 4, 5, 6 ]",
                                         "3 [ 1, 2, 3, [ 4 ], 5, [ 6 ] ]"],
      "push returns the new length; concat flattens one level",
      """`push` returns the new length (3), not the array. `concat` spreads the arrays you pass directly, but
      the `[[6]]` is an array containing an array, so one `[6]` is left standing."""),

    q("slice-splice-args", '''
        const a = [1, 2, 3, 4, 5];
        console.log(a.slice(-2), a.slice(1, -1), a.splice(1, 1), a);
    ''', "[ 4, 5 ] [ 2, 3, 4 ] [ 2 ] [ 1, 3, 4, 5 ]", ["[ 4, 5 ] [ 2, 3, 4 ] [ 2 ] [ 1, 2, 3, 4, 5 ]",
      "[ 4, 5 ] [ 2, 3, 4 ] [ 3 ] [ 1, 2, 4, 5 ]", "[ 3, 4, 5 ] [ 2, 3, 4 ] [ 2 ] [ 1, 3, 4, 5 ]"],
      "slice copies, splice changes the array - and the log happens last",
      """`slice` never changes `a`. `splice(1, 1)` removes the 2, and because all the arguments are worked out
      before anything is printed, the final `a` already shows the removal."""),

    q("sort-negative-default", '''
        console.log([-1, -10, 5, 25, 1].sort());
    ''', "[ -1, -10, 1, 25, 5 ]", ["[ -10, -1, 1, 5, 25 ]", "[ 25, 5, 1, -1, -10 ]", "[ -1, -10, 5, 25, 1 ]"],
      "The default sort compares the text of the numbers",
      """Without a comparator, items are turned into strings and compared. "-1" sorts before "-10", and "25"
      comes before "5". Use `(a, b) => a - b`."""),

    q("at-and-negative-index", '''
        const a = [1, 2, 3];
        console.log(a[-1], a.at(-1), a.slice(-1));
    ''', "undefined 3 [ 3 ]", ["3 3 [ 3 ]", "undefined undefined [ 3 ]", "undefined 3 3"],
      "Square brackets do not count from the end",
      """`a[-1]` asks for a property called "-1", which an array does not have. `at(-1)` was added to count
      from the end, and `slice(-1)` returns an array of the last item."""),

    q("substring-vs-slice", '''
        const s = "abcdef";
        console.log(s.substring(4, 1), s.slice(4, 1) === "",
          s.substring(-2), s.slice(-2));
    ''', "bcd true abcdef ef", ["'' true ef ef", "bcd true ef ef", "bcd false abcdef ef"],
      "substring swaps its arguments and treats negatives as 0",
      """`substring(4, 1)` quietly swaps to (1, 4), and `substring(-2)` clamps -2 to 0, so it returns the whole
      string. `slice` keeps the order, which gives an empty string, and counts negatives from the end."""),

    q("replace-first-only", '''
        console.log("aaa".replace("a", "b"), "aaa".replace(/a/g, "b"),
          "abc".replace("b", "[$&]"));
    ''', "baa bbb a[b]c", ["bbb bbb a[b]c", "baa bbb a[$&]c", "baa baa a[b]c"],
      "A string pattern replaces only the first match",
      """With a plain string, `replace` stops after one match; add the `g` flag in a regex or use
      `replaceAll`. In the replacement text, `$&` stands for the matched text."""),

    q("regex-lastindex", '''
        const re = /a/g;
        console.log(re.test("a"), re.test("a"), re.test("a"));
    ''', "true false true", ["true true true", "true false false", "false false false"],
      "A global regex remembers where it stopped",
      """With the `g` flag, `test` starts searching at `lastIndex`, which the first success moves past the
      string. The second call fails and resets it to 0, so the third succeeds again."""),

    q("match-null", '''
        console.log("abc".match(/x/), "abc".match(/x/g), "abab".match(/a/g).length);
    ''', "null null 2", ["[] [] 2", "null [] 2", "[] null 2"],
      "match returns null, not an empty array, when nothing matches",
      """`.match(/x/g).length` would crash on a miss, because null has no length. Check the result, or use
      `?? []`, before you use it."""),

    q("template-literal-values", '''
        console.log(`${[1, 2]} ${{}} ${null} ${undefined} ${() => 1}`);
    ''', "1,2 [object Object] null undefined () => 1", ["[1,2] {} null undefined () => 1", "1,2 {} null  1",
                                                      "1,2 [object Object] null undefined 1"],
      "Template literals call String() on everything",
      """Arrays join with commas, a plain object becomes "[object Object]", and null and undefined print
      their names. A function prints its own source text."""),

    q("template-eval-order", '''
        let i = 0;
        console.log(`${i++} ${i++} ${i}`, i);
    ''', "0 1 2 2", ["0 1 1 2", "1 2 2 2", "0 0 0 2"],
      "Placeholders are evaluated left to right",
      """Each `${}` runs in order, so the `i` in the third is already 2. The text is built before the second
      argument is read, and that is 2 as well."""),

    q("array-reduce-empty", '''
        console.log([].reduce((a, b) => a + b));
    ''', "TypeError", ["0", "undefined", "NaN"],
      "reduce on an empty array needs a starting value",
      """With no initial value, reduce uses the first item as the start, and there is no first item. Pass `0`
      as the second argument and you get 0 back instead.""", raises=True),

    q("every-some-empty", '''
        const add = (a, b) => a + b;
        console.log([].every(Boolean), [].some(Boolean), [].reduce(add, "x"));
    ''', "true false x", ["false false x", "true true x", "false false undefined"],
      "every of nothing is true; some of nothing is false",
      """`every` asks "is there a counter-example?", and in an empty array there isn't. `some` asks "is
      there an example?", and there isn't one either. `reduce` returns its starting value untouched."""),

    q("set-of-arrays", '''
        const size = (x) => new Set(x).size;
        console.log(size([[1], [1]]), size([{}, {}]), size("aab"));
    ''', "2 2 2", ["1 1 2", "1 2 3", "2 1 2"],
      "Sets compare objects by identity",
      """Two separate `[1]` arrays are different objects, so both stay in the set. A string is spread into
      its characters, so "aab" has two different ones."""),

    q("flat-depth", '''
        console.log([1, [2, [3, [4]]]].flat(),
          [[1], [2, [3]]].flat(Infinity).length);
    ''', "[ 1, 2, [ 3, [ 4 ] ] ] 3", ["[ 1, 2, 3, 4 ] 3", "[ 1, 2, [ 3, [ 4 ] ] ] 2", "[ 1, [ 2, [ 3, [ 4 ] ] ] ] 3"],
      "flat() goes one level deep by default",
      """Only the outermost brackets are removed unless you give a depth. `Infinity` flattens everything,
      which leaves 1, 2 and 3 in the second array."""),

    # ── Numbers, types and equality ────────────────────────────────────────
    q("number-conversions", '''
        console.log(Number(""), Number(" "), Number(null), Number(undefined),
          Number([]), Number([5]), Number([1, 2]));
    ''', "0 0 0 NaN 0 5 NaN", ["NaN NaN 0 NaN 0 5 NaN", "0 0 NaN NaN 0 5 NaN", "0 0 0 NaN NaN NaN NaN"],
      "Number() of nothing is 0, but of undefined is NaN",
      """An empty or blank string and null all become 0. `undefined` has no number form, so it is NaN. An
      array is turned into text first: `[5]` is "5", `[]` is "" (so 0), and `[1, 2]` is "1,2" (NaN)."""),

    q("loose-equality-row", '''
        console.log("0" == false, 0 == "", "0" == "", [] == 0, [0] == false);
    ''', "true true false true true", ["false true false true true", "true true true true true",
                                       "true false false true true"],
      "== is not transitive",
      """Each pair is converted to numbers: "0" and false both become 0, "" becomes 0, but "0" == "" compares
      two strings and they differ. That is why `==` cannot be chained in your head."""),

    q("number-checks", '''
        console.log(Number.isInteger(5.0), Number.isInteger("5"),
          isFinite("5"), Number.isFinite("5"));
    ''', "true false true false", ["true true true true", "false false true false", "true false false false"],
      "The Number.* checks do not convert; the globals do",
      """`5.0` is the integer 5. `Number.isInteger` and `Number.isFinite` refuse a string, but the older
      global `isFinite("5")` converts it to a number first and says true."""),

    q("number-parsing-bases", '''
        console.log(parseFloat("1.2.3"), parseInt("08"),
          parseInt("0x1f"), Number("0x1f"));
    ''', "1.2 8 31 31", ["1.2 0 0 NaN", "1.23 8 31 NaN", "NaN 8 31 31"],
      "parseFloat stops at the second dot; 0x means hex",
      """`parseFloat` reads as much as it can, "1.2", and stops. `parseInt` and `Number` both recognise the
      `0x` prefix as hexadecimal, and a leading 0 in "08" is just a zero these days."""),

    q("number-tostring", '''
        console.log((255).toString(16), (-5).toString(2),
          String(1e21), String(1e-7), 0.000001);
    ''', "ff -101 1e+21 1e-7 0.000001", ["255 -101 1e+21 1e-7 0.000001", "ff 1011 1000000000000000000000 1e-7 0.000001",
                                        "ff -101 1e+21 0.0000001 1e-6"],
      "Very large and very small numbers print in exponent form",
      """`toString(radix)` writes in that base, keeping the minus sign. Numbers from 1e21 up, and below
      0.000001, switch to exponent notation when printed."""),

    q("tofixed-rounding", '''
        console.log((1.005).toFixed(2), (2.5).toFixed(0),
          (1.45).toFixed(1), (0.5).toFixed(0));
    ''', "1.00 3 1.4 1", ["1.01 2 1.5 0", "1.01 3 1.5 1", "1.00 2 1.4 0"],
      "toFixed rounds the stored value, not the one you typed",
      """1.005 is really 1.00499999999999989..., so it rounds down to 1.00, and 1.45 is a hair below too.
      The exact halves 2.5 and 0.5 round up, not to even like Python."""),

    q("math-floor-trunc", '''
        console.log(Math.floor(-0.5), Math.trunc(-0.5),
          Math.ceil(-0.5), Math.round(-0.4));
    ''', "-1 -0 -0 -0", ["-1 0 0 0", "0 -0 -0 -0", "-1 -1 0 0"],
      "Rounding a small negative gives negative zero",
      """`floor` goes down to -1. `trunc`, `ceil` and `round` all end at zero, but a zero that came from a
      negative number is -0, which `console.log` shows with its sign."""),

    q("negative-zero-text", '''
        console.log(String(-0), `${-0}`, JSON.stringify(-0), -0);
    ''', "0 0 0 -0", ["-0 -0 -0 -0", "0 0 0 0", "-0 0 0 -0"],
      "Only console.log shows the sign of -0",
      """Converting -0 to text, in a template or in JSON drops the sign. Node's `console.log` formats numbers
      for inspection and prints `-0`, so the same value looks different."""),

    q("unary-plus-chain", '''
        console.log(1 + - + + + - + 1);
    ''', "2", ["0", "1", "SyntaxError"],
      "Plus and minus signs stack as unary operators",
      """Every sign after the first `+` is a unary operator on the next one. The two minus signs among them
      cancel out, so what is left is `1 + 1`."""),

    q("typeof-undeclared", '''
        console.log(typeof nope, typeof null === "object",
          typeof Symbol(), typeof 10n);
    ''', "undefined true symbol bigint", ["ReferenceError", "undefined false symbol number",
                                         "undefined true object bigint"],
      "typeof is safe on a name that was never declared",
      """Using an undeclared variable throws ReferenceError, but `typeof nope` is allowed and says
      "undefined". Symbols and BigInts have their own type names."""),

    q("bigint-mixing", '''
        console.log(1n + 1);
    ''', "TypeError", ["2n", "2", "NaN"],
      "BigInt and Number cannot be mixed in arithmetic",
      """JavaScript refuses to guess which kind of number you want, so `1n + 1` throws. Convert one side:
      `1n + BigInt(1)` or `Number(1n) + 1`.""", raises=True),

    q("map-set-samevaluezero", '''
        const m = new Map([[NaN, "x"]]);
        console.log(m.get(NaN), new Set([0, -0]).size, [NaN].indexOf(NaN));
    ''', "x 1 -1", ["undefined 2 -1", "x 2 0", "undefined 1 0"],
      "Map and Set treat NaN as equal to itself",
      """Maps and sets use "SameValueZero": NaN matches NaN, and 0 matches -0. `indexOf` still uses `===`,
      so it cannot find NaN, while `includes` can."""),

    q("function-length", '''
        const f = (a, b = 1, c) => {};
        const g = (...r) => {};
        console.log(f.length, g.length, (function (x, y) {}).length);
    ''', "1 0 2", ["3 1 2", "2 0 2", "1 1 2"],
      "length counts the parameters before the first default or rest",
      """A function's `length` stops at the first parameter with a default value and ignores the rest
      parameter. So `(a, b = 1, c)` counts only `a`."""),

    q("string-methods-return", '''
        const s = "  hi  ";
        s.trim();
        console.log(s.length, s.trim().length, "hi".padStart(5, "ab"));
    ''', "6 2 abahi", ["2 2 abahi", "6 2 ababi", "2 6 abahi"],
      "String methods never change the string",
      """`s.trim()` builds a new string that was thrown away, so `s` keeps its six characters. `padStart` adds
      the repeating filler to the front until the total is five long."""),

    q("number-wrapper-eq", '''
        console.log(new Number(1) == 1, new Number(1) == new Number(1),
          typeof Number("1"));
    ''', "true false number", ["false false object", "true true number", "true false object"],
      "A Number object equals the number, but not another Number object",
      """`==` turns the wrapper into a primitive when the other side is a number, so it matches 1. Two
      wrappers are two objects and are compared by identity. `Number("1")` without `new` is a primitive."""),

    q("var-for-leaks", '''
        for (var i = 0; i < 3; i++) {}
        console.log(i);
    ''', "3", ["2", "undefined", "ReferenceError"],
      "var is not scoped to the loop",
      """A `var` belongs to the whole function, so `i` is still there after the loop, and it is 3 because the
      loop only stops once the test `i < 3` fails. With `let` this line would throw ReferenceError."""),

    q("iife-fixes-var", '''
        const fs = [];
        for (var i = 0; i < 3; i++) {
          fs.push((function (j) { return () => j; })(i));
        }
        console.log(fs.map((f) => f()).join());
    ''', "0,1,2", ["3,3,3", "2,2,2", "0,0,0"],
      "An IIFE copies the loop variable for each closure",
      """The function called right away receives the current `i` as its own `j`, so each closure keeps a
      separate value. This was the standard fix before `let` gave every loop pass its own variable."""),

    q("default-param-scope", '''
        const x = "outer";
        function f(a = x) {
          const x = "inner";
          return a;
        }
        console.log(f());
    ''', "outer", ["inner", "undefined", "ReferenceError"],
      "Default values are evaluated before the body's own names exist",
      """The default `a = x` runs in the parameter scope, which looks outward to the `outer` constant. The
      inner `const x` lives in the body and cannot be seen from the default."""),

    q("comma-operator", '''
        console.log((1, 2, 3), [10, 20, 30][(0, 2)], void 0);
    ''', "3 30 undefined", ["1 10 undefined", "[ 1, 2, 3 ] 10 null", "3 20 undefined"],
      "The comma operator evaluates everything and keeps the last value",
      """In `(1, 2, 3)` the first two are computed and dropped. The same happens inside the index brackets,
      so it indexes 2. `void` always gives `undefined`."""),

    # ── Objects, classes, this and JSON ────────────────────────────────────
    q("destructure-defaults", '''
        const { a = 1, b = 2, c = 3 } = { a: undefined, b: null, c: 0 };
        console.log(a, b, c);
    ''', "1 null 0", ["1 2 3", "1 null 3", "undefined null 0"],
      "A default only replaces undefined",
      """Destructuring defaults apply when the value is exactly `undefined`. `null` and `0` are real values,
      so they are kept, unlike with `||`."""),

    q("optional-chain-skips", '''
        const o = {};
        let n = 0;
        o.x?.[n++];
        o.f?.(n++);
        console.log(n, o.a?.b.c.d);
    ''', "0 undefined", ["2 undefined", "1 undefined", "0 TypeError"],
      "?. skips the rest, including the arguments",
      """When the thing before `?.` is null or undefined, the whole chain stops, so `n++` never runs.
      `o.a?.b.c.d` also stops at once; it does not try `.b` on undefined."""),

    q("define-property-readonly", '''
        const o = {};
        Object.defineProperty(o, "x", { value: 1 });
        o.x = 2;
        console.log(o.x, Object.keys(o), delete o.x);
    ''', "1 [] false", ["2 [ 'x' ] true", "1 [ 'x' ] true", "TypeError"],
      "defineProperty makes a hidden, read-only, undeletable property",
      """The omitted flags default to false, so `x` cannot be changed, listed or deleted. In sloppy mode
      the failed assignment is silently ignored; in strict mode it would throw."""),

    q("getter-each-read", '''
        let n = 0;
        const o = { get seq() { return ++n; } };
        console.log(o.seq, o.seq, JSON.stringify(o));
    ''', "1 2 {\"seq\":3}", ["1 1 {\"seq\":1}", "1 2 {}", "1 2 {\"seq\":2}"],
      "A getter runs on every read, including inside JSON.stringify",
      """`o.seq` is not stored; it is a function that runs each time. Serializing the object reads it a
      third time, so the JSON contains 3."""),

    q("class-field-vs-method", '''
        class A { x = 1; getX() { return this.x; } }
        const a = new A();
        console.log(Object.keys(a), "getX" in a, a.hasOwnProperty("getX"));
    ''', "[ 'x' ] true false", ["[ 'x', 'getX' ] true true", "[ 'x' ] false false", "[ 'x' ] true true"],
      "Methods live on the prototype; fields live on the instance",
      """The field `x` is an own property of each instance. `getX` sits once on `A.prototype`, so `in` finds it
      but `hasOwnProperty` and `Object.keys` do not."""),

    q("field-overrides-init", '''
        class A { constructor() { this.init(); } init() { this.v = "A"; } }
        class B extends A {
          v = "field";
          init() { this.v = "B"; }
        }
        console.log(new B().v);
    ''', "field", ["B", "A", "undefined"],
      "Subclass fields are set after the parent constructor finishes",
      """`A`'s constructor calls `init`, which sets "B". Only after `super()` returns do `B`'s field
      initialisers run, so `v = "field"` overwrites it."""),

    q("this-before-super", '''
        class A {}
        class B extends A {
          constructor() { this.x = 1; super(); }
        }
        new B();
    ''', "ReferenceError", ["TypeError", "undefined", "1"],
      "A derived class cannot use this before super()",
      """In a subclass the object does not exist until `super()` has built it. Touching `this` earlier throws
      ReferenceError.""", raises=True),

    q("class-method-detached", '''
        class C {
          n = 5;
          arrow = () => this.n;
          method() { return this.n; }
        }
        const { arrow, method } = new C();
        arrow();
        console.log(method());
    ''', "TypeError", ["5", "undefined", "ReferenceError"],
      "A detached method loses this; an arrow field does not",
      """Pulling `method` out of the object leaves it with no `this`, and class code is always strict, so
      `this` is undefined and `this.n` throws. The arrow field, which captured `this`, would have been fine.""",
      raises=True),

    q("bind-twice", '''
        function who() { return this.name; }
        const bound = who.bind({ name: "A" });
        console.log(bound.call({ name: "B" }), who.call({ name: "C" }),
          bound.bind({ name: "D" })());
    ''', "A C A", ["B C D", "A C D", "B C A"],
      "bind fixes this for good",
      """A bound function ignores a different `this` given to `call` or to another `bind`. Only the very
      first `bind` counts, which is why `bound` stays "A"."""),

    q("arguments-and-arrows", '''
        function f() {
          const inner = () => arguments.length;
          return inner(9, 9, 9, 9);
        }
        console.log(f(1, 2));
    ''', "2", ["4", "0", "1"],
      "An arrow function has no arguments of its own",
      """`arguments` inside the arrow is the outer function's, so it counts the 2 values given to `f`, not
      the 4 given to `inner`. Use rest parameters in an arrow."""),

    q("for-in-inherited", '''
        const o = Object.create({ inherited: 1 });
        o.own = 2;
        const keys = [];
        for (const k in o) keys.push(k);
        console.log(keys, Object.keys(o));
    ''', "[ 'own', 'inherited' ] [ 'own' ]", ["[ 'own' ] [ 'own' ]", "[ 'inherited', 'own' ] [ 'own' ]",
                                            "[ 'own', 'inherited' ] [ 'own', 'inherited' ]"],
      "for...in includes inherited properties",
      """`for...in` walks the prototype chain as well, listing own keys first. `Object.keys` only returns the
      object's own enumerable keys."""),

    q("symbol-keys-hidden", '''
        const s = Symbol("id");
        const o = { a: 1, [s]: 2 };
        console.log(Object.keys(o), JSON.stringify(o), s in o);
    ''', "[ 'a' ] {\"a\":1} true", ["[ 'a', 'id' ] {\"a\":1,\"id\":2} true", "[ 'a' ] {\"a\":1,\"id\":2} true",
                                    "[ 'a' ] {\"a\":1} false"],
      "Symbol keys are skipped by keys(), for...in and JSON",
      """Symbol-keyed properties are hidden from the usual enumeration, which makes them handy for private
      metadata. They are still real, as the `in` check shows."""),

    q("map-vs-object-keys", '''
        const m = new Map();
        m.set(1, "n");
        m.set("1", "s");
        const o = {};
        o[1] = "n";
        o["1"] = "s";
        console.log(m.size, Object.keys(o).length);
    ''', "2 1", ["1 1", "2 2", "1 2"],
      "A Map keeps types apart; an object turns keys into strings",
      """A Map treats 1 and "1" as different keys. An object converts both to the string "1", so the second
      assignment overwrites the first."""),

    q("weakmap-not-iterable", '''
        const w = new WeakMap();
        console.log([...w]);
    ''', "TypeError", ["[]", "undefined", "ReferenceError"],
      "WeakMaps cannot be iterated or counted",
      """Entries may disappear whenever the garbage collector runs, so a WeakMap offers no size, no keys and
      no iteration. Spreading it throws TypeError.""", raises=True),

    q("structured-clone", '''
        const a = { d: { n: 1 }, f: [1] };
        const deep = structuredClone(a);
        const shallow = { ...a };
        deep.d.n = 2;
        shallow.f.push(2);
        console.log(a.d.n, a.f);
    ''', "1 [ 1, 2 ]", ["2 [ 1, 2 ]", "1 [ 1 ]", "2 [ 1 ]"],
      "structuredClone copies deeply; spread copies one level",
      """Changing the deep clone cannot touch `a`. The spread copy still shares the array under `f`, so the
      push shows up in the original."""),

    q("const-mutation", '''
        const o = { n: 1 };
        o.n = 2;
        try { o = {}; } catch (e) { console.log(e.name, o.n); }
    ''', "TypeError 2", ["TypeError 1", "SyntaxError 2", "2 2"],
      "const stops reassignment, not mutation",
      """`o.n = 2` changes the object, which const allows. `o = {}` tries to rebind the name and throws a
      TypeError, leaving `o` as it was."""),

    q("freeze-shallow", '''
        const o = Object.freeze({ a: 1, inner: { b: 1 } });
        o.a = 2;
        o.inner.b = 2;
        o.c = 3;
        console.log(o);
    ''', "{ a: 1, inner: { b: 2 } }", ["{ a: 1, inner: { b: 1 } }", "{ a: 2, inner: { b: 2 }, c: 3 }",
                                       "TypeError"],
      "Object.freeze is only one level deep",
      """The frozen object ignores changes to `a` and refuses the new `c` (silently, outside strict mode).
      The object held in `inner` is not frozen, so its `b` can still be changed."""),

    q("json-stringify-values", '''
        const d = new Date(Date.UTC(2020, 0, 1));
        console.log(JSON.stringify([undefined, () => 1, NaN, d, Infinity]));
    ''', "[null,null,null,\"2020-01-01T00:00:00.000Z\",null]", ["[null,null,null,1577836800000,null]",
      "[,,NaN,\"2020-01-01T00:00:00.000Z\",Infinity]", "[null,null,null,{},null]"],
      "JSON has no undefined, functions, NaN or Infinity",
      """Inside an array those all become `null`. A Date is turned into its ISO text by its `toJSON`
      method, not into a number."""),

    q("json-map-set", '''
        const o = { m: new Map([[1, 2]]), s: new Set([1]) };
        console.log(JSON.stringify(o));
    ''', "{\"m\":{},\"s\":{}}", ["{\"m\":[[1,2]],\"s\":[1]}", "{\"m\":{\"1\":2},\"s\":{\"1\":1}}", "{}"],
      "Maps and Sets stringify as empty objects",
      """They keep their data in internal slots, not as properties, and JSON only sees properties. Convert
      them first, for example with `[...map]` or `Object.fromEntries(map)`."""),

    q("static-own-property", '''
        class A { static x = 1; }
        class B extends A {}
        B.x = 2;
        console.log(A.x, B.x, Object.hasOwn(B, "x"));
    ''', "1 2 true", ["2 2 true", "1 2 false", "1 1 true"],
      "Assigning on a subclass creates its own property",
      """Reading `B.x` before the assignment would find A's through inheritance. The assignment makes a new
      own property on `B`, and `A.x` stays 1."""),

    q("asi-parenthesis", '''
        const x = 1
        const y = x
        (function () {})()
        console.log(y)
    ''', "TypeError", ["1", "undefined", "SyntaxError"],
      "A line starting with ( is joined to the line above",
      """JavaScript does not insert a semicolon before the `(`, so this parses as `x(function () {})()`.
      Calling the number 1 as a function is a TypeError.""", raises=True),

    # ── Promises, async and the event loop ─────────────────────────────────
    q("foreach-async-not-awaited", '''
        const out = [];
        async function main() {
          [1, 2, 3].forEach(async (n) => { await null; out.push(n); });
          out.push("done");
          console.log(out.join(" "));
        }
        main();
    ''', "done", ["1 2 3 done", "done 1 2 3", "1 done"],
      "forEach does not wait for async callbacks",
      """`forEach` starts three async functions and moves straight on; each one pauses at its `await`. The
      log runs before any of them resumes, so only "done" is there. Use `for...of` with `await`."""),

    q("promise-all-order", '''
        const wait = (ms, v) => new Promise((r) => setTimeout(() => r(v), ms));
        Promise.all([wait(30, "slow"), wait(10, "fast")])
          .then((r) => console.log(r.join(" ")));
    ''', "slow fast", ["fast slow", "slow", "fast"],
      "Promise.all keeps the order you gave, not the finishing order",
      """The results array lines up with the input array, however long each promise takes. The "fast" one
      finishes first but still sits in the second place."""),

    q("promise-race-first", '''
        const wait = (ms, v) => new Promise((r) => setTimeout(() => r(v), ms));
        Promise.race([wait(30, "slow"), wait(10, "fast")])
          .then((v) => console.log(v));
    ''', "fast", ["slow", "slow fast", "fast slow"],
      "Promise.race settles with whoever finishes first",
      """`race` gives the value of the first promise to settle, and the other result is simply ignored. Here
      that is the 10 ms one."""),

    q("then-without-return", '''
        Promise.resolve(1)
          .then((v) => { v + 1; })
          .then((v) => console.log(v));
    ''', "undefined", ["2", "1", "NaN"],
      "A then callback with braces needs an explicit return",
      """`v + 1;` computes a value and discards it, so the callback returns undefined and that is what the
      next `then` receives. An arrow function without braces would have returned it."""),

    q("finally-passthrough", '''
        Promise.resolve("a")
          .finally(() => "b")
          .then((v) => console.log(v));
    ''', "a", ["b", "undefined", "ab"],
      "finally cannot change the value passing through",
      """`finally` is for cleanup, so its return value is ignored and the original result carries on. Only a
      throw or a rejected promise from inside it would change the outcome."""),

    q("catch-recovers", '''
        Promise.reject(1)
          .catch((v) => v + 1)
          .then((v) => console.log("then", v));
    ''', "then 2", ["catch 2", "then 1", "UnhandledPromiseRejection"],
      "A catch that returns a value makes the chain succeed again",
      """The rejection is handled by `catch`, whose return value of 2 becomes the next promise's successful
      result. The following `then` runs normally."""),

    q("executor-runs-sync", '''
        const log = [];
        new Promise((r) => { log.push("executor"); r(); })
          .then(() => log.push("then"));
        log.push("after");
        setTimeout(() => console.log(log.join(" ")));
    ''', "executor after then", ["after executor then", "executor then after", "after then executor"],
      "The Promise constructor's function runs immediately",
      """Only the `then` callbacks are delayed, to a microtask. The executor passed to `new Promise` is
      called synchronously, before the next line."""),

    q("nexttick-before-promise", '''
        const log = [];
        Promise.resolve().then(() => log.push("promise"));
        process.nextTick(() => log.push("tick"));
        setTimeout(() => console.log(log.join(" ")));
    ''', "tick promise", ["promise tick", "tick", "promise"],
      "In Node, nextTick callbacks run before promise callbacks",
      """When the current script ends, Node empties the `nextTick` queue first, then the promise microtasks.
      Both run before any timer."""),

    q("immediate-inside-timer", '''
        const log = [];
        setTimeout(() => {
          setTimeout(() => log.push("timeout"), 0);
          setImmediate(() => log.push("immediate"));
        }, 0);
        setTimeout(() => console.log(log.join(" ")), 30);
    ''', "immediate timeout", ["timeout immediate", "immediate", "timeout"],
      "Inside a timer, setImmediate comes before the next timeout",
      """After the timers phase, Node moves on to the check phase, where `setImmediate` callbacks run. The new
      0 ms timer has to wait for the next loop. (At the top level of a script, the order is not fixed.)"""),

    q("zero-vs-one-ms", '''
        const log = [];
        setTimeout(() => log.push("1ms"), 1);
        setTimeout(() => log.push("0ms"), 0);
        setTimeout(() => console.log(log.join(" ")), 30);
    ''', "1ms 0ms", ["0ms 1ms", "0ms", "1ms"],
      "setTimeout 0 is really 1 ms",
      """Node treats a delay of 0 as 1, so both timers wait the same time and fire in the order they were
      created. The 1 ms one was created first."""),

    q("async-error-no-await", '''
        const log = [];
        async function f() { throw new Error("boom"); }
        process.on("unhandledRejection", () => {});
        async function main() {
          try { f(); log.push("no await"); } catch (e) { log.push("caught"); }
          try { await f(); } catch (e) { log.push("caught " + e.message); }
          console.log(log.join(" | "));
        }
        main();
    ''', "no await | caught boom", ["caught | caught boom", "no await | no await", "caught boom"],
      "try/catch only catches a rejection you await",
      """Without `await`, calling `f()` just returns a rejected promise, and nothing is thrown at that point.
      The first `catch` never fires; the second does, because `await` rethrows the error."""),

    q("async-return-await", '''
        async function f() { return 1; }
        async function g() { return f(); }
        g().then((v) => console.log(typeof v, v));
    ''', "number 1", ["object Promise", "object [object Promise]", "number undefined"],
      "An async function flattens a returned promise",
      """Returning a promise from an async function does not nest it; the result promise follows it, so the
      caller receives the plain number."""),

    q("await-in-promise-order", '''
        const log = [];
        (async () => {
          log.push(1);
          await null;
          log.push(3);
        })();
        log.push(2);
        Promise.resolve().then(() => console.log(log.join("")));
    ''', "123", ["132", "213", "1 2 3"],
      "Code after await runs later, but before the next macrotask",
      """The async function runs synchronously up to its first `await`, giving 1, then 2 from the main script.
      The continuation is queued first, so it pushes 3 before the final `then` logs."""),

    # ── Control flow ───────────────────────────────────────────────────────
    q("switch-fallthrough", '''
        function f(n) {
          let out = "";
          switch (n) {
            case 1: out += "a";
            case 2: out += "b"; break;
            case 3: out += "c";
            default: out += "d";
          }
          return out;
        }
        console.log(f(1), f(2), f(3), f(9));
    ''', "ab b cd d", ["a b c d", "ab b c d", "a b cd d"],
      "Without break, a switch runs on into the next case",
      """Case 1 falls through into case 2's code until the `break`. Case 3 has no break, so it runs into
      `default`, which is also where unmatched values land."""),

    q("switch-strict", '''
        let r = "";
        switch (1) {
          case "1": r += "str"; break;
          case true: r += "bool"; break;
          default: r += "default";
        }
        console.log(r);
    ''', "default", ["str", "bool", "strbool"],
      "switch compares with ===",
      """The cases are tested with strict equality, so neither "1" nor `true` matches the number 1, even
      though `==` would accept both."""),

    q("labelled-continue", '''
        let n = 0;
        outer: for (let i = 0; i < 3; i++) {
          for (let j = 0; j < 3; j++) {
            if (j === 1) continue outer;
            if (i === 2) break outer;
            n += 10;
          }
        }
        console.log(n);
    ''', "20", ["30", "60", "10"],
      "A label lets continue and break reach the outer loop",
      """For i = 0 and i = 1 only j = 0 adds 10, then `continue outer` jumps to the next i. On i = 2 the
      `break outer` ends both loops before anything is added: 20 in all."""),

    q("finally-overrides-return", '''
        function f() { try { return "a"; } finally { return "b"; } }
        function g() { let x = 1; try { return x; } finally { x = 2; } }
        console.log(f(), g());
    ''', "b 1", ["a 2", "a 1", "b 2"],
      "A return in finally wins; a change in finally comes too late",
      """`f` returns "b" because the later return replaces the pending one. In `g`, the value 1 was already
      taken for the return, so setting `x = 2` in `finally` does not change it."""),

    q("reduce-no-init-shape", '''
        const a = [1, 2, 3];
        const r = a.reduce((acc, n) => acc + n * 2);
        console.log(r);
    ''', "11", ["12", "6", "NaN"],
      "Without an initial value, reduce starts with the first item untouched",
      """The first call has `acc` = 1 and `n` = 2, so the 1 is never doubled: 1 + 4 + 6 is 11. With a starting
      value of 0 every item would be doubled, giving 12."""),

    # ── Dates (fixed UTC dates, so every run agrees) and sorting ───────────
    q("date-zero-based-month", '''
        const d = new Date(Date.UTC(2024, 11, 25));
        console.log(d.getUTCMonth(), d.getUTCDate(), d.getUTCDay(),
          d.getUTCFullYear());
    ''', "11 25 3 2024", ["12 25 3 2024", "11 25 25 2024", "12 25 4 2024"],
      "Months count from 0, days of the month from 1, weekdays from Sunday = 0",
      """December is month 11, but 25 is just the 25th. `getUTCDay` gives the weekday with Sunday as 0, so
      Wednesday is 3. Easy to mix up because only the month and weekday start at zero."""),

    q("date-month-overflow", '''
        const d = new Date(Date.UTC(2024, 1, 30));
        console.log(d.toISOString().slice(0, 10));
    ''', "2024-03-01", ["2024-01-30", "2024-02-30", "RangeError"],
      "Month 1 is February, and an out-of-range day rolls over",
      """February 2024 has 29 days, so day 30 spills into the next month and the date becomes 1 March. The
      Date constructor adjusts silently instead of rejecting it."""),

    q("date-setmonth-rollover", '''
        const d = new Date(Date.UTC(2024, 0, 31));
        d.setUTCMonth(1);
        console.log(d.toISOString().slice(0, 10));
    ''', "2024-03-02", ["2024-02-29", "2024-02-28", "2024-03-01"],
      "Setting the month keeps the day number, even when it does not fit",
      """31 January with the month set to February is "31 February", which is two days past the end of a
      29-day month: 2 March. The date does not clamp to the last day."""),

    q("date-equality", '''
        const a = new Date(Date.UTC(2024, 0, 1));
        const b = new Date(Date.UTC(2024, 0, 1));
        console.log(a == b, a < b, a <= b, +a === +b);
    ''', "false false true true", ["true false true true", "false true true true", "true true true true"],
      "Dates compare with < but not with ==",
      """`==` on two objects checks identity, so two equal dates are not equal. The relational operators
      convert them to numbers, and `+a === +b` does the same on purpose."""),

    q("sort-boolean-comparator", '''
        console.log([5, 1, 4, 2, 3].sort((a, b) => a > b));
    ''', "[ 5, 1, 4, 2, 3 ]", ["[ 1, 2, 3, 4, 5 ]", "[ 5, 4, 3, 2, 1 ]", "TypeError"],
      "A comparator must return a number, negative, zero or positive",
      """`a > b` gives true or false, which become 1 and 0, never a negative number, so the sort never learns
      that anything should go first. The array comes out unchanged in modern engines."""),
)
