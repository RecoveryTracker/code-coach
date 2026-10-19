"""Gotchas, JavaScript: short programs where the obvious reading is a trap.

Run by tests/test_gotchas_content.py in real node (CommonJS, sloppy mode, like the app's own
"Run it"); the marked answer must be exactly what `console.log` printed. Event-loop programs
collect their steps into an array and print once at the end, so the answer is one line.
Nothing here may use randomness, the clock or anything that differs between runs.
"""

from __future__ import annotations

from .items import Item, make

q = make("javascript")

ITEMS: tuple[Item, ...] = (
    # ── Types and coercion ─────────────────────────────────────────────────
    q("typeof-null", '''
        console.log(typeof null, typeof undefined, typeof NaN);
    ''', "object undefined number", ["null undefined NaN", "object object number", "null undefined number"],
      "typeof null is 'object'",
      """`typeof null` says "object", a mistake from the first version of JavaScript that can never be
      fixed without breaking the web. NaN is a number too, as the type of "not a number"."""),

    q("empty-array-eq-not", '''
        console.log([] == ![]);
    ''', "true", ["false", "TypeError", "undefined"],
      "== converts both sides before comparing",
      """`![]` is false (an array is truthy). Then `[] == false` converts both to numbers: the empty
      array becomes "" and then 0, and false becomes 0. 0 == 0, so it is true. Use `===`."""),

    q("null-compare", '''
        console.log(null == undefined, null === undefined, null == 0, null >= 0);
    ''', "true false false true", ["true false false false", "false false false true",
                                    "true false true true"],
      "null is loosely equal only to undefined, but >= converts it to 0",
      """`==` has a special rule: null equals undefined and nothing else, so `null == 0` is false.
      But `>=` converts null to the number 0, so `null >= 0` is true."""),

    q("plus-minus-strings", '''
        console.log("5" + 3, "5" - 3, "5" * "2");
    ''', "53 2 10", ["8 2 10", "53 53 10", "8 8 10"],
      "+ joins when a string is involved; - and * always do maths",
      """`+` means 'join' if either side is a string, so "5" + 3 is "53". `-` and `*` only mean
      arithmetic, so they turn the strings into numbers first."""),

    q("plus-order", '''
        console.log(1 + 2 + "3", "1" + 2 + 3);
    ''', "33 123", ["123 123", "6 123", "33 6"],
      "+ works left to right",
      """`1 + 2 + "3"` adds the numbers first (3) and then joins "3", giving "33". `"1" + 2 + 3` is
      a string from the start, so everything joins: "123"."""),

    q("array-plus", '''
        console.log([1, 2] + [3], [] + 1, {} + 1);
    ''', "1,23 1 [object Object]1", ["[ 1, 2, 3 ] 1 1", "6 1 NaN", "1,2,3 1 [object Object]1"],
      "+ turns arrays and objects into strings",
      """Arrays become text with a comma between items: "1,2", and joining "3" gives "1,23". An empty array
      is "", and a plain object is "[object Object]". None of them are added numerically."""),

    q("unary-plus", '''
        console.log(+[], +{}, +"");
    ''', "0 NaN 0", ["NaN NaN NaN", "0 0 0", "0 NaN NaN"],
      "Unary + converts to a number",
      """An empty array becomes "" and then 0, an empty string is 0, but a plain object becomes
      "[object Object]", which is not a number."""),

    q("number-parse", '''
        console.log(Number("12px"), parseInt("12px"), parseFloat(".5.5"));
    ''', "NaN 12 0.5", ["12 12 0.5", "NaN NaN 0.5", "NaN 12 0"],
      "Number() is strict, parseInt/parseFloat read as far as they can",
      """`Number` fails on any junk, giving NaN. `parseInt` reads digits until it hits something else.
      `parseFloat(".5.5")` reads ".5" and stops at the second dot."""),

    q("parseint-map", '''
        console.log(["1", "2", "3"].map(parseInt));
    ''', "[ 1, NaN, NaN ]", ["[ 1, 2, 3 ]", "[ 1, 2, NaN ]", "[ 1, NaN, 1 ]"],
      "map passes the index as the second argument",
      """`map` calls `parseInt("2", 1)` and `parseInt("3", 2)`. The second argument is the number base:
      base 1 is invalid, and "3" is not a digit in base 2, so both give NaN."""),

    q("parseint-odd", '''
        console.log(parseInt(0.0000005), parseInt(null), parseInt("Infinity"));
    ''', "5 NaN NaN", ["0 NaN NaN", "0 0 Infinity", "5 0 NaN"],
      "parseInt converts to a string first",
      """0.0000005 becomes the text "5e-7", and parseInt reads the 5 and stops. `null` becomes "null",
      which has no digits, and "Infinity" has none either."""),

    q("nan-checks", '''
        console.log(NaN === NaN, [NaN].includes(NaN), [NaN].indexOf(NaN));
    ''', "false true -1", ["true true 0", "false false -1", "false true 0"],
      "NaN is not equal to itself",
      """`===` says NaN is never equal to anything, itself included, and `indexOf` uses it, so it finds
      nothing. `includes` uses the SameValueZero rule, which treats NaN as equal to NaN."""),

    q("isnan-global", '''
        console.log(isNaN("abc"), Number.isNaN("abc"), isNaN(""));
    ''', "true false false", ["false false false", "true true false", "true false true"],
      "Global isNaN converts first; Number.isNaN does not",
      """`isNaN("abc")` converts the text to a number first (NaN), so it is true. `Number.isNaN` only
      says true for the actual NaN value. And "" converts to 0, so it is not NaN."""),

    q("divide-by-zero", '''
        console.log(1 / 0, -1 / 0, 0 / 0);
    ''', "Infinity -Infinity NaN", ["Infinity -Infinity 0", "Infinity Infinity NaN", "Error Error Error"],
      "Division by zero does not throw",
      """Numbers follow floating-point rules: a non-zero number over zero is plus or minus Infinity, and
      0 / 0 is NaN. Nothing is thrown."""),

    q("truthiness-row", '''
        console.log(!!"false", !!"0", !!0, !![], !!{}, !!NaN);
    ''', "true true false true true false", ["true false false true true false",
                                              "true true false false true false",
                                              "false true false true true false"],
      "Non-empty strings and every object, even [], are truthy",
      """"false" and "0" are non-empty strings, so truthy. An empty array and an empty object are
      objects, so truthy too. Only 0, NaN, "", null, undefined and false are falsy."""),

    q("truthy-vs-equal", '''
        console.log([] ? "truthy" : "falsy", [] == false ? "equal" : "not equal");
    ''', "truthy equal", ["falsy equal", "truthy not equal", "falsy not equal"],
      "An array is truthy, yet loosely equal to false",
      """In an `if`, any object is truthy. But `==` converts the empty array to "" and then to 0, and
      false to 0, so the comparison says equal. Truthiness and `==` are different questions."""),

    q("wrapper-boolean", '''
        console.log(Boolean(new Boolean(false)));
    ''', "true", ["false", "undefined", "null"],
      "Wrapper objects are always truthy",
      """`new Boolean(false)` is an object that holds false, and every object is truthy. Only the plain
      value false is falsy."""),

    q("wrapper-typeof", '''
        const s = new String("a");
        console.log(typeof s, typeof String("a"), s === "a");
    ''', "object string false", ["string string true", "object object false", "string string false"],
      "new String makes an object, not a string",
      """`String("a")` gives the plain string, but `new String("a")` is a wrapper object. `===` between an
      object and a string is never true."""),

    q("typeof-typeof", '''
        console.log(typeof typeof 1, typeof (() => {}), typeof class {});
    ''', "string function function", ["number function object", "string function object",
                                      "string object function"],
      "typeof always returns a string",
      """`typeof 1` is the string "number", so `typeof typeof 1` is "string". Functions, and classes (which
      are functions underneath), report "function"."""),

    q("typeof-array", '''
        console.log(typeof [], Array.isArray([]), [] instanceof Object);
    ''', "object true true", ["array true true", "array true false", "object false true"],
      "Arrays are objects",
      """There is no "array" type for typeof: arrays are objects, and `Array.isArray` is the way to tell
      them apart. They are instances of Object too."""),

    q("string-compare", '''
        console.log("2" > "12", 2 > "12", "a" > "B");
    ''', "true false true", ["false false true", "true true true", "false false false"],
      "Two strings compare as text, a number and a string compare as numbers",
      """`"2" > "12"` compares character by character: '2' comes after '1'. With a number on one side
      the text is converted, so 2 > 12 is false. And lowercase letters sort after capitals."""),

    q("chained-compare", '''
        console.log(1 < 2 < 3, 3 > 2 > 1);
    ''', "true false", ["true true", "false false", "false true"],
      "Comparisons do not chain in JavaScript",
      """`3 > 2 > 1` is `(3 > 2) > 1`, which is `true > 1`, and true becomes 1, so 1 > 1 is false.
      The first one only works by luck: `true < 3`."""),

    q("math-max-min", '''
        console.log(Math.max(), Math.min(), Math.max([]), Math.max([1, 2]));
    ''', "-Infinity Infinity 0 NaN", ["0 0 0 2", "NaN NaN 0 2", "-Infinity Infinity NaN 2"],
      "Math.max of nothing, and of an array",
      """With no arguments Math.max starts from -Infinity and Math.min from Infinity. An array is
      turned into text and then a number: [] is 0 but [1, 2] is "1,2", which is NaN."""),

    q("or-nullish", '''
        console.log(0 || "a", 0 ?? "a", null ?? "c", undefined ?? 0);
    ''', "a 0 c 0", ["a a c 0", "0 0 c 0", "a 0 c undefined"],
      "|| replaces any falsy value, ?? only null and undefined",
      """`0 || "a"` treats 0 as missing and gives "a". `??` only reacts to null and undefined, so
      `0 ?? "a"` keeps the 0."""),

    q("plus-nan-word", '''
        console.log("b" + "a" + +"a" + "a");
    ''', "baNaNa", ["baaa", "bana", "baNaN"],
      "A unary + turns the middle 'a' into NaN",
      """`+"a"` is a number conversion, which fails and gives NaN. Then joining it as text gives
      "NaN", so the result is "ba" + "NaN" + "a"."""),

    q("string-minus-minus", '''
        console.log("5" - - "2", "5" + - "2", "5" - + "2");
    ''', "7 5-2 3", ["7 3 3", "3 5-2 7", "7 5-2 7"],
      "Unary signs next to a string",
      """`"5" - -"2"` is 5 minus negative 2, which is 7. `"5" + -"2"` joins the text "5" with the
      number -2 turned into "-2". `"5" - +"2"` is 5 minus 2."""),

    # ── Numbers ────────────────────────────────────────────────────────────
    q("float-sum", '''
        console.log(0.1 + 0.2 === 0.3, 0.1 + 0.2);
    ''', "false 0.30000000000000004", ["true 0.3", "false 0.3", "true 0.30000000000000004"],
      "Floating-point sums are not exact",
      """0.1 and 0.2 have no exact binary form, and their sum is a hair above 0.3. The same happens in
      every language that uses doubles."""),

    q("big-integer", '''
        console.log(9007199254740993);
    ''', "9007199254740992", ["9007199254740993", "9.007199254740993e+15", "NaN"],
      "Numbers above 2^53 lose precision",
      """All JavaScript numbers are 64-bit floats, which can only hold whole numbers exactly up to
      9007199254740992 (2^53). The next odd number is rounded to the nearest even one. BigInt avoids this."""),

    q("math-round", '''
        console.log(Math.round(-0.5), Math.round(2.5), Math.round(-2.5));
    ''', "-0 3 -2", ["-1 3 -3", "0 3 -3", "-0 2 -2"],
      "Math.round rounds halves toward positive infinity",
      """Halves always go up, not away from zero, so -2.5 becomes -2 and 2.5 becomes 3. -0.5 rounds to
      negative zero, which console.log shows as -0."""),

    q("negative-zero", '''
        console.log(Object.is(-0, 0), -0 === 0, 1 / -0);
    ''', "false true -Infinity", ["true true Infinity", "false false -Infinity", "true false Infinity"],
      "There are two zeros",
      """JavaScript has both +0 and -0. `===` treats them as equal, `Object.is` does not, and dividing
      by -0 gives negative infinity."""),

    q("increment-order", '''
        let a = 1;
        let b = a++ + ++a;
        console.log(a, b);
    ''', "3 4", ["3 3", "2 3", "3 5"],
      "Post-increment returns the old value, pre-increment the new one",
      """`a++` gives 1 and then a becomes 2. `++a` makes a 3 and gives 3. So b is 1 + 3 = 4, and a is 3."""),

    # ── Hoisting, scope, closures ──────────────────────────────────────────
    q("var-hoisting", '''
        console.log(x);
        var x = 5;
    ''', "undefined", ["5", "ReferenceError", "null"],
      "var is hoisted, but its value is not",
      """The declaration `var x` is moved to the top of the scope and starts as undefined. Only the
      assignment `= 5` stays where it is, below the log."""),

    q("tdz", '''
        console.log(typeof x);
        let x = 1;
    ''', "ReferenceError", ["undefined", "number", "null"],
      "The temporal dead zone: let exists but cannot be touched yet",
      """A `let` variable is in scope from the start of its block but unusable until its line runs. Even
      `typeof`, which is safe for undeclared names, throws a ReferenceError here.""",
      raises=True),

    q("function-vs-var", '''
        console.log(typeof f);
        var f = 1;
        function f() {}
    ''', "function", ["undefined", "number", "object"],
      "Function declarations are hoisted whole, and win over var",
      """The function is hoisted with its body, and the `var f` declaration adds nothing new. The
      `f = 1` assignment has not run yet at the log, so f is still the function."""),

    q("var-shadow-in-function", '''
        var x = 1;
        function f() {
          console.log(x);
          var x = 2;
        }
        f();
    ''', "undefined", ["1", "2", "ReferenceError"],
      "A hoisted var hides the outer variable of the same name",
      """Inside `f`, `var x` is hoisted to the top of the function as undefined, so the log sees that
      local x and not the global 1."""),

    q("block-scope", '''
        if (true) {
          var v = 1;
          let l = 2;
        }
        console.log(typeof v, typeof l);
    ''', "number undefined", ["undefined undefined", "number number", "undefined number"],
      "var ignores blocks; let respects them",
      """`var` is scoped to the whole function, so `v` is still there after the if. `let` lives only
      inside the braces, so `l` is not defined out here, and typeof gives "undefined"."""),

    q("var-loop-timeout", '''
        const out = [];
        for (var i = 0; i < 3; i++) {
          setTimeout(() => out.push(i), 0);
        }
        setTimeout(() => console.log(out.join(" ")), 0);
    ''', "3 3 3", ["0 1 2", "0 0 0", "2 2 2"],
      "var in a loop is one shared variable",
      """There is only one `i`, and the timers run after the loop has finished, when it is 3. Each
      callback reads that same variable."""),

    q("let-loop-closures", '''
        const fns = [];
        for (let i = 0; i < 3; i++) {
          fns.push(() => i);
        }
        console.log(fns.map(f => f()).join());
    ''', "0,1,2", ["3,3,3", "2,2,2", "0,0,0"],
      "let gives each loop pass its own variable",
      """A `let` in a for header is created fresh for every pass, so each closure keeps its own i.
      With `var` this would print 3,3,3."""),

    q("counter-closures", '''
        function makeCounter() {
          let n = 0;
          return () => ++n;
        }
        const a = makeCounter(), b = makeCounter();
        a(); a();
        console.log(a(), b());
    ''', "3 1", ["3 3", "1 1", "2 1"],
      "Every call of the outer function makes a new private variable",
      """Each `makeCounter()` call creates its own `n`. `a` has been called three times, `b` only once,
      and they never share anything."""),

    q("lexical-scope", '''
        const x = 10;
        function f() { return x; }
        {
          const x = 20;
          console.log(f());
        }
    ''', "10", ["20", "undefined", "ReferenceError"],
      "Scope depends on where a function is written, not where it is called",
      """`f` looks up `x` where it was defined, in the outer scope, so it finds 10. The inner block's 20
      is invisible to it."""),

    q("leaked-global", '''
        function f() { leaked = 1; }
        f();
        console.log(typeof leaked);
    ''', "number", ["undefined", "ReferenceError", "object"],
      "Assigning to an undeclared name creates a global (outside strict mode)",
      """Without var, let or const, sloppy-mode JavaScript quietly makes a global variable. In strict
      mode the same line throws a ReferenceError."""),

    # ── this ───────────────────────────────────────────────────────────────
    q("lost-this", '''
        const obj = {
          label: "obj",
          regular() { return this.label; },
          arrow: () => typeof this,
        };
        const f = obj.regular;
        console.log(f(), obj.arrow());
    ''', "undefined object", ["obj object", "undefined undefined", "obj undefined"],
      "`this` depends on how a function is called",
      """`f` is called on its own, so `this` is not `obj` and `this.label` is undefined. An arrow
      function ignores how it is called and uses the `this` of the code around it, here the module's."""),

    q("strict-this", '''
        function sloppy() { return typeof this; }
        function strict() { "use strict"; return typeof this; }
        console.log(sloppy(), strict());
    ''', "object undefined", ["undefined undefined", "object object", "undefined object"],
      "'use strict' changes what `this` is in a plain call",
      """In sloppy mode a plain call gets the global object as `this`. Strict mode leaves it undefined,
      so mistakes such as calling a method detached from its object fail loudly."""),

    # ── Arrays, objects, copies ────────────────────────────────────────────
    q("sort-default", '''
        console.log([10, 9, 1, 100].sort());
    ''', "[ 1, 10, 100, 9 ]", ["[ 1, 9, 10, 100 ]", "[ 100, 10, 9, 1 ]", "[ 10, 9, 1, 100 ]"],
      "sort() with no function sorts as text",
      """The default sort turns the numbers into strings, so "10" and "100" come before "9". Pass
      `(a, b) => a - b` for numeric order."""),

    q("sort-in-place", '''
        const a = [3, 1, 2];
        const b = a.sort();
        console.log(a === b);
    ''', "true", ["false", "undefined", "[ 1, 2, 3 ]"],
      "sort() sorts in place and returns the same array",
      """`sort` changes `a` itself and hands back that very array, so `b` is not a copy. `toSorted()`
      is the version that makes a new one."""),

    q("array-holes", '''
        const a = [1, , 3];
        console.log(a.length, a[1], 1 in a);
    ''', "3 undefined false", ["2 undefined true", "3 undefined true", "2 null false"],
      "A hole is not the same as undefined",
      """The gap still counts towards the length, and reading it gives undefined, but there is no
      property at index 1 at all, so `1 in a` is false."""),

    q("array-length-write", '''
        const a = [1, 2, 3];
        a.length = 1;
        a[3] = 4;
        console.log(a.length, a);
    ''', "4 [ 1, <2 empty items>, 4 ]", ["2 [ 1, 4 ]", "4 [ 1, 2, 3, 4 ]", "4 [ 1, undefined, undefined, 4 ]"],
      "Setting length truncates, and writing past the end leaves holes",
      """Setting length to 1 throws away 2 and 3 for good. Writing index 3 then stretches the array to
      length 4 and leaves two empty slots in between."""),

    q("map-holes", '''
        console.log(Array(3).map((_, i) => i));
    ''', "[ <3 empty items> ]", ["[ 0, 1, 2 ]", "[ undefined, undefined, undefined ]", "[ null, null, null ]"],
      "map skips the holes of an empty array",
      """`Array(3)` has length 3 but no actual items, and `map` only visits items that exist. Use
      `Array.from({ length: 3 }, (_, i) => i)` or `.fill()` first."""),

    q("arrow-no-return", '''
        console.log([1, 2, 3].map(n => { n * 2 }));
    ''', "[ undefined, undefined, undefined ]", ["[ 2, 4, 6 ]", "[ 1, 2, 3 ]", "[ NaN, NaN, NaN ]"],
      "Curly braces make an arrow function body that needs a return",
      """With `{ }` the arrow function runs statements and returns undefined unless you write `return`.
      Without the braces, `n => n * 2` would return the value."""),

    q("arrow-object-literal", '''
        const f = () => ({ a: 1 });
        const g = () => { a: 1 };
        console.log(f(), g());
    ''', "{ a: 1 } undefined", ["{ a: 1 } { a: 1 }", "undefined undefined", "{ a: 1 } 1"],
      "Braces after => are a block, not an object",
      """In `g`, `{ a: 1 }` is parsed as a block containing a label `a:` and the expression 1, so nothing
      is returned. Wrapping the object in parentheses, as in `f`, makes it an object."""),

    q("foreach-reassign", '''
        const nums = [1, 2, 3];
        nums.forEach(n => { n = n * 2; });
        console.log(nums);
    ''', "[ 1, 2, 3 ]", ["[ 2, 4, 6 ]", "undefined", "[ 2, 3, 4 ]"],
      "Reassigning the callback's parameter does not change the array",
      """`n` is a copy of each number, so `n = n * 2` only changes that local copy. `forEach` also
      returns nothing and never builds a new array."""),

    q("forof-objects", '''
        const people = [{ age: 1 }, { age: 2 }];
        for (const p of people) p.age += 10;
        console.log(people.map(p => p.age).join());
    ''', "11,12", ["1,2", "11,2", "10,10"],
      "Changing an object through the loop variable does change it",
      """`p` points at the same object that is in the array, so `p.age += 10` changes it. A `const`
      only stops you from reassigning `p`, not from changing what it points at."""),

    q("reassign-param-object", '''
        function reset(o) { o = { n: 0 }; }
        const a = { n: 5 };
        reset(a);
        console.log(a.n);
    ''', "5", ["0", "undefined", "null"],
      "Reassigning a parameter does not change the caller's object",
      """The parameter `o` starts as a copy of the reference to `a`. Pointing it at a new object only
      changes the local name; the caller's object is untouched. `o.n = 0` would have worked."""),

    q("spread-shallow", '''
        const a = { n: { v: 1 } };
        const b = { ...a };
        b.n.v = 2;
        console.log(a.n.v);
    ''', "2", ["1", "undefined", "null"],
      "Spread makes a shallow copy",
      """`{ ...a }` copies the top level only, so `b.n` and `a.n` are the same inner object. Use
      `structuredClone(a)` for a deep copy."""),

    q("splice-return", '''
        const a = [1, 2, 3, 4];
        const r = a.splice(1, 2);
        console.log(a, r);
    ''', "[ 1, 4 ] [ 2, 3 ]", ["[ 1, 2, 3, 4 ] [ 2, 3 ]", "[ 2, 3 ] [ 1, 4 ]", "[ 1, 4 ] [ 2 ]"],
      "splice changes the array and returns what it removed",
      """`splice(1, 2)` removes two items starting at index 1, leaving [1, 4], and returns the removed
      ones, [2, 3]. `slice` is the harmless one that copies."""),

    q("for-in-array", '''
        const out = [];
        for (const i in [10, 20]) out.push(i + 1);
        console.log(out);
    ''', "[ '01', '11' ]", ["[ 1, 2 ]", "[ 11, 21 ]", "[ '1', '2' ]"],
      "for...in gives string keys, not values",
      """`for...in` loops over property names, which are strings: "0" and "1". Adding 1 joins text,
      giving "01" and "11". Use `for...of` for values."""),

    q("key-order", '''
        console.log(Object.keys({ b: 1, 2: 1, a: 1, 1: 1 }));
    ''', "[ '1', '2', 'b', 'a' ]", ["[ 'b', '2', 'a', '1' ]", "[ '1', '2', 'a', 'b' ]",
                                    "[ 'b', 'a', '2', '1' ]"],
      "Integer-like keys come first, in numeric order",
      """Objects list integer-like keys first in ascending order, then the other keys in the order they
      were added. It is not insertion order, and not alphabetical."""),

    q("key-coercion", '''
        const o = {};
        o[1] = "a";
        o["1"] = "b";
        console.log(Object.keys(o).length, o[1]);
    ''', "1 b", ["2 a", "2 b", "1 a"],
      "Object keys are always strings",
      """The number 1 becomes the key "1", the same key as the string "1". The second assignment
      overwrites the first, leaving one key with the value "b"."""),

    q("object-as-key", '''
        const m = {};
        const k1 = {}, k2 = {};
        m[k1] = 1;
        m[k2] = 2;
        console.log(Object.keys(m).length);
    ''', "1", ["2", "0", "3"],
      "Objects used as keys become '[object Object]'",
      """Both keys are turned into the same text, "[object Object]", so the second write replaces the
      first. A `Map` is what keeps objects as keys."""),

    q("set-uniqueness", '''
        console.log(new Set([1, "1", 1.0, NaN, NaN]).size);
    ''', "3", ["5", "4", "2"],
      "A Set uses strict equality, except NaN equals NaN",
      """1 and 1.0 are the same number, and the string "1" is a different value, and the two NaNs
      count as one. So the set holds 1, "1" and NaN."""),

    q("string-index-length", '''
        console.log("😀".length, [..."😀"].length);
    ''', "2 1", ["1 1", "2 2", "1 2"],
      "length counts UTF-16 units, not characters",
      """An emoji takes two UTF-16 code units, which is what `length` counts. Spreading the string walks
      by whole characters, so it finds one."""),

    q("split-no-args", '''
        console.log([..."abc"].reverse().join(""), "abc".split().length);
    ''', "cba 1", ["cba 3", "abc 1", "cba 0"],
      "split() with no separator does not split",
      """Without a separator, `split()` returns the whole string as the only item. Use `split("")` to
      get single characters."""),

    q("string-immutable", '''
        const s = "abc";
        s[0] = "z";
        console.log(s);
    ''', "abc", ["zbc", "TypeError", "z"],
      "Strings cannot be changed by index",
      """In sloppy mode the assignment is silently ignored. (In strict mode it throws a TypeError.) Strings
      are immutable, so build a new one instead."""),

    q("includes-vs-indexof", '''
        console.log([1, 2, 3].indexOf(4) ? "found" : "missing");
    ''', "found", ["missing", "true", "undefined"],
      "indexOf returns -1, which is truthy",
      """-1 is the 'not found' answer, and any non-zero number is truthy, so the condition passes. Use
      `includes`, or compare with -1."""),

    q("out-of-range-index", '''
        const a = [1, 2, 3];
        console.log(a[a.length]);
    ''', "undefined", ["3", "null", "Error"],
      "Reading past the end gives undefined, not an error",
      """The last index is `length - 1`. Index 3 does not exist, and JavaScript quietly returns
      undefined instead of throwing."""),

    q("default-params", '''
        function f(a, b = a * 2) { return b; }
        console.log(f(2), f(2, undefined), f(2, null));
    ''', "4 4 null", ["4 4 0", "4 undefined null", "4 4 4"],
      "Defaults apply only for undefined, not for null",
      """Passing `undefined` (or nothing) triggers the default. Passing `null` is a real value and is
      used as is."""),

    q("json-stringify", '''
        console.log(JSON.stringify({ a: undefined, b: () => 1, c: NaN }));
    ''', '{"c":null}', ['{"a":null,"b":null,"c":null}', '{"c":"NaN"}', "{}"],
      "JSON.stringify drops undefined and functions, and turns NaN into null",
      """Properties whose value is undefined or a function are left out entirely. NaN has no JSON form,
      so it is written as null."""),

    # ── Control flow ───────────────────────────────────────────────────────
    q("de-morgan", '''
        const x = 1;
        console.log(x !== 1 || x !== 2 ? "other" : "one or two");
    ''', "other", ["one or two", "undefined", "1"],
      "A condition that is always true",
      """No number can equal both 1 and 2, so at least one of `x !== 1` and `x !== 2` is always
      true. To mean 'neither', use `&&`."""),

    q("asi-return", '''
        function f() {
          return
          42;
        }
        console.log(f());
    ''', "undefined", ["42", "null", "SyntaxError"],
      "A line break after return ends the statement",
      """Automatic semicolon insertion adds a `;` right after `return`, so the function returns
      undefined and the 42 below is never reached. Keep the value on the same line."""),

    # ── Event loop and async ───────────────────────────────────────────────
    q("microtask-before-timeout", '''
        const log = [];
        setTimeout(() => log.push("timeout"), 0);
        Promise.resolve().then(() => log.push("promise"));
        log.push("sync");
        setTimeout(() => console.log(log.join(" ")), 0);
    ''', "sync promise timeout", ["sync timeout promise", "timeout promise sync", "promise sync timeout"],
      "Promises run before timers, even a 0 ms timer",
      """The running code always finishes first ("sync"). Then all queued promise callbacks (microtasks)
      run, and only after that do timers fire, however short their delay."""),

    q("await-order", '''
        const log = [];
        async function f() {
          log.push("f1");
          await null;
          log.push("f2");
        }
        f();
        log.push("main");
        Promise.resolve().then(() => console.log(log.join(" ")));
    ''', "f1 main f2", ["f1 f2 main", "main f1 f2", "f1 main"],
      "await pauses the function and lets the caller carry on",
      """`f` runs synchronously up to its first `await`, then hands control back, so "main" is logged
      next. The continuation of `f` was queued before the final `.then`, so "f2" is logged first."""),

    q("promise-chains", '''
        const log = [];
        Promise.resolve().then(() => log.push(1)).then(() => log.push(3));
        Promise.resolve().then(() => log.push(2)).then(() => log.push(4));
        setTimeout(() => console.log(log.join("")));
    ''', "1234", ["1324", "1342", "2143"],
      "Two promise chains take turns",
      """Each `.then` queues the next step only after it finishes, so the two chains interleave: both
      first steps (1, 2) run, then both second steps (3, 4)."""),

    q("async-returns-promise", '''
        async function f() { return 1; }
        console.log(f());
    ''', "Promise { 1 }", ["1", "undefined", "Promise { <pending> }"],
      "An async function always returns a promise",
      """Whatever an async function returns is wrapped in a promise. Here it is already resolved with 1,
      so you see `Promise { 1 }`. You need `await` or `.then` to get at the 1."""),
)
