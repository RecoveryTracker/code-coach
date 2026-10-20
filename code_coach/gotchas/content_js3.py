"""Gotchas, JavaScript, the third helping: a wider mix, with a lot of easy-looking cards.

Same rules as content_js.py: run by tests/test_gotchas_content.py in real node (CommonJS, sloppy mode); the
marked answer must be exactly what `console.log` printed, the wrong options are real misreads, and event-loop
programs collect their steps into an array and print once. Roughly a third of these look easy on purpose (a
beginner can get them right, but there is a real tempting wrong answer); the rest are the usual middle and
hard traps. They come after the earlier modules in the deck.
"""

from __future__ import annotations

from .items import Item, make

q = make("javascript")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics a beginner can get, with a real trap ──────────
    q("typeof-precedence", '''
        console.log(typeof 10 / 2, typeof (10 / 2), typeof "10" + 2);
    ''', "NaN number string2", ["5 number string2", "number number string2", "NaN number number2"],
      "typeof binds tighter than / and +",
      """`typeof 10 / 2` is `(typeof 10) / 2`, which is "number" divided by 2: NaN. With parentheses
      you get the type of the result, "number". And `typeof "10" + 2` joins the text "string" with 2."""),

    q("find-vs-filter", '''
        const n = [1, 2, 3, 4];
        console.log(n.filter((x) => x > 2), n.find((x) => x > 2),
          n.findIndex((x) => x > 9), n.some((x) => x > 3));
    ''', "[ 3, 4 ] 3 -1 true",
      ["[ 3, 4 ] [ 3 ] -1 true", "[ 3 ] 3 -1 true", "[ 3, 4 ] 3 undefined true"],
      "filter gives an array, find gives the first item, findIndex gives -1 for none",
      """`filter` keeps every match as a new array. `find` returns just the first matching item, not an
      array. `findIndex` answers with an index, and the 'nothing found' answer is -1, not undefined."""),

    q("reduce-initial-value", '''
        console.log([1, 2, 3].reduce((a, b) => a + b, 10),
          [[1], [2]].reduce((a, b) => a.concat(b)),
          ["a", "b"].reduce((a, b) => b + a));
    ''', "16 [ 1, 2 ] ba", ["6 [ 1, 2 ] ab", "16 [ [ 1 ], [ 2 ] ] ba", "16 [ 1, 2 ] ab"],
      "The second argument of reduce is where the total starts",
      """Starting at 10, the sum is 16. `concat` flattens one level, so the arrays join into one. The
      last callback does `b + a`, which puts each new letter in front: `ba`."""),

    q("includes-strict", '''
        console.log([1, 2, 3].includes("2"), ["a", "b"].indexOf("b"),
          "hello".indexOf("l"), "hello".lastIndexOf("l"), "hello".includes(""));
    ''', "false 1 2 3 true",
      ["true 1 2 3 true", "false 1 2 2 true", "false 1 2 3 false"],
      "includes uses strict equality, and indexOf finds only the first match",
      """The number 2 is not the string "2", so `includes` says false. `indexOf("l")` is the first `l`
      at 2, and `lastIndexOf` the last at 3. Every string includes the empty string."""),

    q("reverse-in-place", '''
        const a = [1, 2, 3];
        console.log(a.reverse() === a, a.join("-"), [1, [2, 3]].join(";"));
    ''', "true 3-2-1 1;2,3",
      ["false 1-2-3 1;2,3", "true 3-2-1 1;2;3", "false 3-2-1 1;2,3"],
      "reverse flips the array itself and returns that same array",
      """`reverse()` works in place and returns the very same array, so the comparison is true and the
      next `join` sees `[3, 2, 1]`. A nested array inside join becomes text with a comma."""),

    q("template-arith", '''
        const a = 2, b = 3;
        console.log(`${a + b}`, `${a}${b}`, `${a} * ${b} = ${a * b}`, `${"a" + b}`);
    ''', "5 23 2 * 3 = 6 a3",
      ["5 5 2 * 3 = 6 a3", "23 23 2 * 3 = 6 a3", "5 23 2 * 3 = 6 a + b"],
      "Every ${} is evaluated, and two next to each other just join as text",
      """`${a + b}` runs the addition first, giving 5. `${a}${b}` is two values glued into the string
      "23". Text outside the braces is copied as it is."""),

    q("const-reassign", '''
        const x = 1;
        try {
          x = 2;
        } catch (e) {
          console.log(e.name);
        }
    ''', "TypeError", ["SyntaxError", "ReferenceError", "2"],
      "Reassigning a const throws a TypeError at run time",
      """A `const` binding cannot point anywhere else, and trying to makes JavaScript throw a TypeError
      when that line runs. (Changing the inside of a const object is allowed; reassigning is not.)"""),

    q("spread-order", '''
        const a = { x: 1, y: 2 };
        console.log({ ...a, y: 3 }, { y: 3, ...a });
    ''', "{ x: 1, y: 3 } { y: 2, x: 1 }",
      ["{ x: 1, y: 3 } { y: 3, x: 1 }", "{ x: 1, y: 2 } { y: 3, x: 1 }", "{ x: 1, y: 3 } { x: 1, y: 2 }"],
      "Later properties win, and a key keeps the position where it first appeared",
      """In the first, `y: 3` comes after the spread and overrides it. In the second the spread comes
      last, so `y` goes back to 2, but it keeps its first position at the front."""),

    q("continue-break-string", '''
        let out = "";
        for (let i = 0; i < 5; i++) {
          if (i === 1) continue;
          if (i === 3) break;
          out += i;
        }
        console.log(out);
    ''', "02", ["012", "024", "2"],
      "continue skips one pass, break ends the loop",
      """`i` is 0 and gets added. It is 1 and `continue` skips it, 2 is added, and at 3 the loop breaks,
      so neither 3 nor 4 is looked at. The result is the string "02"."""),

    q("split-limit", '''
        console.log("Hello".toUpperCase().split("").reverse().join(""),
          "a,b,c".split(",", 2), " x ".trim().length);
    ''', "OLLEH [ 'a', 'b' ] 1",
      ["OLLEH [ 'a', 'b', 'c' ] 1", "HELLO [ 'a', 'b' ] 1", "OLLEH [ 'a', 'b' ] 3"],
      "split's second argument caps how many pieces you get back",
      """The classic reverse-a-string chain gives OLLEH. `split(",", 2)` stops after two pieces and
      drops the rest. `trim` removes the spaces, so only the `x` is left."""),

    q("tofixed-returns-string", '''
        const t = (1234.5678).toFixed(2);
        console.log(t, typeof t, t + 1, +t + 1, (5).toFixed(2));
    ''', "1234.57 string 1234.571 1235.57 5.00",
      ["1234.57 number 1235.57 1235.57 5.00", "1234.57 string 1235.57 1235.57 5.00",
       "1234.57 string 1234.571 1235.57 5"],
      "toFixed returns a string, so + joins instead of adding",
      """The rounded value is the text "1234.57", so `t + 1` is "1234.571". A unary `+` turns it back
      into a number first, and `(5).toFixed(2)` is the text "5.00"."""),

    q("optional-chain-null", '''
        const u = { name: "A", addr: null };
        console.log(u.addr?.city, u.addr?.city ?? "none", u.zip?.code);
    ''', "undefined none undefined",
      ["null none undefined", "undefined null undefined", "undefined none null"],
      "?. gives undefined, not null, when it stops",
      """When the left side is null or undefined, `?.` short-circuits to `undefined` (even if the value
      was `null`). `??` then replaces that with "none". A missing property like `zip` is undefined too."""),

    q("rest-spread-basics", '''
        const f = (a, ...r) => r.length;
        console.log(f(1, 2, 3), Math.max(...[1, 5, 3]), [..."hi"]);
    ''', "2 5 [ 'h', 'i' ]", ["3 5 [ 'h', 'i' ]", "2 NaN [ 'h', 'i' ]", "2 5 [ 'hi' ]"],
      "Rest collects what is left over; spread opens something up",
      """`a` takes the 1, so the rest array holds only 2 and 3: length 2. Spread turns the array into
      separate arguments for `Math.max`, and spreading a string gives its characters."""),

    q("object-keys-array-strings", '''
        console.log(Object.keys([7, 8]), Object.keys("ab"), Object.values("ab"));
    ''', "[ '0', '1' ] [ '0', '1' ] [ 'a', 'b' ]",
      ["[ 0, 1 ] [ 0, 1 ] [ 'a', 'b' ]", "[ 7, 8 ] [ 'a', 'b' ] [ 'a', 'b' ]",
       "[ '0', '1' ] [ 'a', 'b' ] [ 'a', 'b' ]"],
      "Object.keys gives the indexes, as strings",
      """Arrays and strings are objects whose keys are their index numbers, and object keys are always
      strings. So `keys` gives `'0'` and `'1'`, while `values` gives the items themselves."""),

    q("json-quotes", '''
        console.log(JSON.stringify({ a: [1, "2"], b: true, c: null }),
          JSON.stringify("hi"), JSON.stringify([undefined]));
    ''', '{"a":[1,"2"],"b":true,"c":null} "hi" [null]',
      ['{"a":[1,2],"b":true,"c":null} "hi" [null]', '{"a":[1,"2"],"b":true,"c":null} hi [null]',
       '{"a":[1,"2"],"b":true,"c":null} "hi" [undefined]'],
      "JSON keeps string quotes, and undefined in an array becomes null",
      """A string is written with its quotes, even on its own, and the number 1 and the string "2" stay
      different. JSON has no undefined, so inside an array it becomes null."""),

    q("set-add-size", '''
        const s = new Set([1, 2, 2, 3]);
        s.add(3);
        s.add(4);
        console.log(s.size, s.has(2), [...s]);
    ''', "4 true [ 1, 2, 3, 4 ]",
      ["6 true [ 1, 2, 2, 3, 3, 4 ]", "4 false [ 1, 2, 3, 4 ]", "5 true [ 1, 2, 3, 4 ]"],
      "A Set ignores a value it already holds, and keeps insertion order",
      """The repeated 2 and the second `add(3)` change nothing. That leaves 1, 2, 3, 4, in the order
      they were first added."""),

    q("map-set-overwrite", '''
        const m = new Map([["a", 1]]);
        m.set("a", 2).set("b", 3);
        console.log(m.size, m.get("a"), m.get("z"), [...m.keys()]);
    ''', "2 2 undefined [ 'a', 'b' ]",
      ["3 2 undefined [ 'a', 'a', 'b' ]", "2 1 undefined [ 'a', 'b' ]", "2 2 null [ 'a', 'b' ]"],
      "Setting an existing Map key replaces its value; a missing key reads undefined",
      """`set` returns the map, so the calls chain. The second `set("a", 2)` overwrites the value instead
      of adding a key, so the size is 2. `get` of an unknown key is `undefined`."""),

    q("class-static-getter", '''
        class Temp {
          static count = 0;
          constructor(c) { this.c = c; Temp.count++; }
          get f() { return this.c * 9 / 5 + 32; }
        }
        const a = new Temp(100);
        new Temp(0);
        console.log(a.f, Temp.count, a.count);
    ''', "212 2 undefined", ["212 2 2", "212 1 undefined", "[Function: f] 2 undefined"],
      "A static property lives on the class, not on its instances",
      """The getter `f` is read like a property, no parentheses, giving 212. `count` belongs to `Temp`
      itself, so `a.count` is undefined, and two objects were created so `Temp.count` is 2."""),

    q("push-returns-length", '''
        const a = [1, 2];
        console.log(a.push(3), a.unshift(0), a.pop(), a.shift(), a);
    ''', "3 4 3 0 [ 1, 2 ]",
      ["3 4 3 0 [ 0, 1, 2 ]", "2 3 3 0 [ 1, 2 ]", "3 4 0 3 [ 1, 2 ]"],
      "push and unshift return the new length; pop and shift return the removed item",
      """`push(3)` makes it 3 long and returns 3, then `unshift(0)` returns 4. `pop` removes and returns
      the 3, `shift` removes and returns the 0, and `[1, 2]` is left."""),

    q("delete-property", '''
        const o = { a: 1, b: 2 };
        console.log(delete o.a, o, "a" in o, o.a, delete o.zzz);
    ''', "true { b: 2 } false undefined true",
      ["false { b: 2 } false undefined true", "true { a: undefined, b: 2 } true undefined true",
       "true { b: 2 } false null false"],
      "delete removes the key completely, and deleting a missing key is still true",
      """After `delete`, the property is gone, not set to undefined, so `in` says false. `delete` returns
      true when nothing stopped it, including for a key that never existed."""),

    q("in-vs-includes", '''
        console.log("a" in { a: 1 }, 1 in [5, 6], 5 in [5, 6], [5, 6].includes(5));
    ''', "true true false true", ["true false true true", "false true true true", "true true true true"],
      "in checks keys (or indexes), includes checks values",
      """`1 in [5, 6]` asks whether index 1 exists, which it does. `5 in [5, 6]` asks for index 5, which
      does not exist. Only `includes` looks at the values."""),

    q("foreach-returns-undefined", '''
        const out = [];
        const r = [1, 2, 3].forEach((x) => {
          if (x === 2) return;
          out.push(x);
        });
        console.log(out, r);
    ''', "[ 1, 3 ] undefined", ["[ 1 ] undefined", "[ 1, 3 ] [ 1, 3 ]", "[ 1, 3 ] null"],
      "return inside forEach skips one item, it does not stop the loop",
      """The `return` only ends that one call of the callback, so 3 is still visited. And `forEach` itself
      always returns undefined."""),

    q("pad-repeat", '''
        console.log("ab".repeat(2), "5".padStart(3, "0"), "abc".padEnd(5, "xy"),
          "a".repeat(0) === "");
    ''', "abab 005 abcxy true",
      ["abab 500 abcxy true", "abab 005 abcxyxy true", "abab 005 abcxy false"],
      "Padding is cut to fit the target length",
      """`padStart` puts the zeros in front, giving `005`. `padEnd(5, "xy")` needs only two more
      characters, so it uses `xy` once. Repeating zero times gives the empty string."""),

    q("map-index-arg", '''
        console.log([..."abc"].map((c, i) => c + i), ["1", "2", "3"].map(Number));
    ''', "[ 'a0', 'b1', 'c2' ] [ 1, 2, 3 ]",
      ["[ 'a0', 'b1', 'c2' ] [ 1, NaN, NaN ]", "[ 'a', 'b', 'c' ] [ 1, 2, 3 ]",
       "[ '0a', '1b', '2c' ] [ 1, 2, 3 ]"],
      "map passes (item, index); Number ignores the extra arguments, parseInt does not",
      """The callback's second parameter is the index, so `c + i` gives `a0`. `Number` only uses its
      first argument, so `map(Number)` is safe, unlike `map(parseInt)`, where the index becomes a radix."""),

    q("dot-vs-bracket", '''
        const o = { key: 1, a: 2 };
        const key = "a";
        console.log(o.key, o[key], o["key"], o[1 + 1]);
    ''', "1 2 1 undefined", ["2 2 1 undefined", "1 2 1 2", "1 1 1 undefined"],
      "Dot means the literal name; brackets evaluate what is inside",
      """`o.key` always looks for a property called "key". `o[key]` uses the variable's value, "a". And
      `o[1 + 1]` looks for the property "2", which does not exist."""),

    q("object-identity", '''
        console.log({} === {}, [1] === [1], "a" === "a", [] == []);
    ''', "false false true false", ["true true true true", "false false true true", "true false true false"],
      "Objects and arrays are equal only to themselves",
      """Each `{}` or `[]` literal makes a brand new object, and `===` (and `==`) compare objects by
      identity. Strings are primitives and compare by content."""),

    q("swap-destructure", '''
        let a = 1, b = 2;
        [a, b] = [b, a];
        console.log(a, b);
    ''', "2 1", ["1 2", "2 2", "1 1"],
      "Destructuring assignment swaps without a temporary",
      """The right side `[b, a]` is built first as `[2, 1]`, and only then are the values stored into
      `a` and `b`. So they trade places. Plain `a = b; b = a` would give 2 2."""),

    q("loose-null-check", '''
        const f = (x) => x == null;
        console.log(f(null), f(undefined), f(0), f(""), f(NaN));
    ''', "true true false false false",
      ["true false false false false", "true true true true false", "true true false false true"],
      "== null is true only for null and undefined",
      """The loose comparison has a special rule: `null` and `undefined` equal each other and nothing
      else. 0, the empty string and NaN are falsy but are not `== null`."""),

    q("alias-vs-spread-copy", '''
        const a = [1, 2, 3];
        const b = a;
        const c = [...a];
        b.push(4);
        console.log(a.length, c.length, a === b, a === c);
    ''', "4 3 true false", ["3 3 true false", "4 4 true true", "3 4 false false"],
      "= copies the reference; spread copies the contents",
      """`b` is another name for the same array, so pushing to `b` grows `a` too. `c` is a new array
      made before the push, so it stays at three items."""),

    q("json-single-quotes", '''
        try {
          JSON.parse("{'a': 1}");
        } catch (e) {
          console.log(e.name);
        }
    ''', "SyntaxError", ["TypeError", "undefined", "{ a: 1 }"],
      "JSON needs double quotes",
      """JSON is stricter than JavaScript object literals: keys and strings must use double quotes.
      Single quotes make `JSON.parse` throw a SyntaxError."""),

    q("null-property-error", '''
        try {
          undefined.x;
        } catch (e) {
          console.log(e.constructor.name, e instanceof Error);
        }
    ''', "TypeError true", ["ReferenceError true", "undefined false", "TypeError false"],
      "Reading a property of undefined is a TypeError",
      """The name `undefined` exists, so it is not a ReferenceError. The failure is reading `.x` from
      a value that has no properties, which is a TypeError, and all errors are instances of Error."""),

    q("throw-string", '''
        try {
          throw "oops";
        } catch (e) {
          console.log(typeof e, e instanceof Error, e.length);
        }
    ''', "string false 4", ["object true undefined", "string true 4", "string false undefined"],
      "You can throw any value, and catch gets it unchanged",
      """`throw "oops"` throws a plain string, not an Error object, so it has no stack and is not an
      `instanceof Error`. It is still a string, so `.length` is 4."""),

    q("char-codes", '''
        console.log("a".charCodeAt(), String.fromCharCode(97 + 2),
          "z".charCodeAt() - "a".charCodeAt(), "b" > "a");
    ''', "97 c 25 true", ["a c 25 true", "97 99 25 true", "97 c 26 true"],
      "charCodeAt gives a number, fromCharCode turns a number back into a letter",
      """`"a"` has code 97, and 97 + 2 = 99 is `c`. The distance from `a` to `z` is 25, and letters
      compare by code, so `b` is greater than `a`."""),

    q("objects-by-reference-search", '''
        const a = { id: 1 };
        console.log([a].indexOf({ id: 1 }), [a].indexOf(a), [a].includes(a),
          [{ id: 1 }].some((x) => x.id === 1));
    ''', "-1 0 true true", ["0 0 true true", "-1 0 false true", "-1 0 true false"],
      "indexOf and includes find the same object, not a look-alike",
      """A fresh `{ id: 1 }` is a different object from `a`, so `indexOf` fails. Searching with the very
      same `a` works, and `some` with a test on the property finds it by content."""),

    q("boolean-arithmetic", '''
        console.log(true + true, true + "1", null + 1, undefined + 1, "5" * true);
    ''', "2 true1 1 NaN 5", ["true true1 1 NaN 5", "2 true1 NaN NaN 5", "2 true1 1 1 5"],
      "true is 1, null is 0, undefined is NaN in arithmetic",
      """`true + true` is 1 + 1, but `true + "1"` joins as text, "true1". `null` turns into 0 while
      `undefined` becomes NaN, and `"5" * true` is 5 * 1."""),

    q("executor-throw-rejects", '''
        new Promise(() => {
          throw new Error("x");
        }).catch((e) => console.log("caught", e.message));
    ''', "caught x", ["x", "caught undefined", "Error: x"],
      "An error thrown inside the Promise executor becomes a rejection",
      """The executor's throw does not escape: the promise is rejected with that error, and `catch`
      receives it. So it prints "caught" and the message."""),

    q("postfix-in-array", '''
        let i = 1;
        const a = [i++, i++, ++i];
        console.log(a, i);
    ''', "[ 1, 2, 4 ] 4", ["[ 1, 2, 3 ] 3", "[ 2, 3, 4 ] 4", "[ 1, 2, 4 ] 3"],
      "i++ gives the old value; ++i gives the new one",
      """The first two give 1 and 2 (the value before each increment). By then `i` is 3, and `++i`
      makes it 4 and gives 4. So the array is `[1, 2, 4]` and `i` ends at 4."""),

    # ── The middle: this, classes, arrays, objects, promises ───────────────
    q("short-circuit-assign", '''
        let x = 0;
        const r = x && x++;
        console.log(r, x, x || (x = 5), x);
    ''', "0 0 5 5", ["0 1 5 5", "0 0 0 5", "0 0 5 0"],
      "&& and || stop early, so the right side may never run",
      """`x && x++` stops at the falsy 0, so `x++` never runs and `r` is 0. In the log, the second `x`
      is still 0, then `x || (x = 5)` does assign 5, and the last `x` shows it."""),

    q("filter-boolean", '''
        console.log([0, "", "0", null, undefined, [], NaN, -1].filter(Boolean));
    ''', "[ '0', [], -1 ]", ["[ [], -1 ]", "[ '0', -1 ]", "[]"],
      "filter(Boolean) keeps truthy values, and '0', [] and -1 are all truthy",
      """Only 0, "", null, undefined and NaN are falsy here. The string "0" has a character in it, an
      empty array is an object, and -1 is not zero, so all three stay."""),

    q("destructure-skip-rest", '''
        const [a, , b = 5, ...r] = [1, 2, undefined, 4, 5];
        console.log(a, b, r);
    ''', "1 5 [ 4, 5 ]", ["1 2 [ 4, 5 ]", "1 undefined [ 4, 5 ]", "1 5 [ 2, 4, 5 ]"],
      "An empty slot skips an item, and a default fills in for undefined",
      """The double comma skips the 2. The third item is undefined, so `b` gets its default 5. `...r`
      collects whatever is left after that: 4 and 5."""),

    q("loose-equality-objects", '''
        console.log([1] == 1, [1, 2] == "1,2", ({}) == "[object Object]", [] == "");
    ''', "true true true true",
      ["false true true true", "true false true true", "false false false false"],
      "== turns an object into text or a number first",
      """When one side is a primitive, the object is converted: `[1]` becomes "1", then 1, and
      `{}` becomes "[object Object]". All four are true, which is why `===` is safer."""),

    q("math-corners", '''
        console.log(Math.sqrt(-1), 0 ** 0, Math.abs(-0), Math.sign(-3),
          Math.cbrt(27), Math.hypot(3, 4));
    ''', "NaN 1 0 -1 3 5",
      ["NaN 0 0 -1 3 5", "-1 1 0 -1 3 5", "NaN 1 -0 -1 3 5"],
      "The square root of -1 is NaN, and 0 ** 0 is 1",
      """JavaScript has no imaginary numbers, so `Math.sqrt(-1)` is NaN. By convention anything to the
      power 0 is 1, including 0. `Math.abs(-0)` is plain 0."""),

    q("number-string-formats", '''
        console.log(Number("1,000"), Number("1e3"), Number("0b11"), Number("12 "),
          Number("1 2"));
    ''', "NaN 1000 3 12 NaN",
      ["1000 1000 3 12 NaN", "NaN 1000 NaN 12 NaN", "NaN 1000 3 NaN 12"],
      "Number accepts exponent, binary and edge spaces, but not commas or inner spaces",
      """`Number` allows exponent notation, `0b` binary literals and spaces around the number. A comma
      or a space in the middle makes it NaN."""),

    q("arrow-this-object", '''
        const o = {
          n: 1,
          arrow: () => this.n,
          method() { return this.n; },
        };
        console.log(o.arrow(), o.method());
    ''', "undefined 1", ["1 1", "undefined undefined", "1 undefined"],
      "An arrow function does not get its own this",
      """The arrow uses the `this` of where it was written, which here is the module, not the object,
      so `this.n` is undefined. The shorthand method gets `this` from how it is called: `o`."""),

    q("setter-compound", '''
        const o = {
          _v: 1,
          get v() { return this._v; },
          set v(x) { this._v = x * 2; },
        };
        o.v = 5;
        o.v += 1;
        console.log(o.v, o._v);
    ''', "22 22", ["11 11", "6 6", "12 10"],
      "+= reads through the getter and writes through the setter",
      """`o.v = 5` runs the setter, storing 10. `o.v += 1` reads 10 through the getter, adds 1, and
      sets 11, which the setter doubles to 22."""),

    q("constructor-calls-override", '''
        class A {
          constructor() { this.init(); }
          init() { this.x = "A"; }
        }
        class B extends A {
          init() { super.init(); this.y = "B"; }
        }
        console.log(new B());
    ''', "B { x: 'A', y: 'B' }",
      ["A { x: 'A' }", "B { x: 'A' }", "B { y: 'B' }"],
      "A parent constructor calls the child's version of an overridden method",
      """`new B()` runs A's constructor, but `this` is a B, so `this.init()` finds B's `init`. That calls
      `super.init()` to set `x`, and then sets `y`."""),

    q("static-this", '''
        class A {
          static who() { return this.name; }
        }
        class B extends A {}
        console.log(A.who(), B.who());
    ''', "A B", ["A A", "B B", "B A"],
      "Inside a static method, this is the class it was called on",
      """`B` inherits `who`, but `B.who()` is called on `B`, so `this` is `B` and `this.name` is "B".
      The method's own definition does not fix `this`."""),

    q("this-in-nested-function", '''
        const o = {
          n: 2,
          run() {
            return [1, 2].map(function (x) { return x * this.n; });
          },
          runArrow() {
            return [1, 2].map((x) => x * this.n);
          },
        };
        console.log(o.run(), o.runArrow());
    ''', "[ NaN, NaN ] [ 2, 4 ]",
      ["[ 2, 4 ] [ 2, 4 ]", "[ 2, 4 ] [ NaN, NaN ]", "[ NaN, NaN ] [ NaN, NaN ]"],
      "A plain function inside a method loses this; an arrow keeps it",
      """The callback in `run` is an ordinary function called without an object, so its `this` is the
      global object, which has no `n`. The arrow in `runArrow` uses the method's `this`."""),

    q("promise-all-reject", '''
        Promise.all([Promise.resolve(1), Promise.reject("no"), 3])
          .then((v) => console.log("ok", v))
          .catch((e) => console.log("fail", e));
    ''', "fail no", ["ok [ 1, 'no', 3 ]", "ok [ 1, 3 ]", "fail undefined"],
      "Promise.all rejects as soon as any one input rejects",
      """One rejected promise is enough to reject the whole `Promise.all`, with that reason, and the
      other results are thrown away. `then` is skipped and `catch` runs."""),

    q("allsettled-statuses", '''
        Promise.allSettled([Promise.resolve(1), Promise.reject("no")])
          .then((r) => console.log(r.map((x) => x.status), r[1].reason));
    ''', "[ 'fulfilled', 'rejected' ] no",
      ["[ 'fulfilled' ] undefined", "[ 'resolved', 'rejected' ] no",
       "[ 'fulfilled', 'rejected' ] undefined"],
      "allSettled never rejects; it reports each outcome",
      """Each entry is an object with a `status` of "fulfilled" or "rejected" (not "resolved"). A
      rejected entry carries the error in `reason`, a fulfilled one in `value`."""),

    q("microtask-between-timers", '''
        const log = [];
        setTimeout(() => log.push("a"), 0);
        setTimeout(() => {
          log.push("b");
          Promise.resolve().then(() => log.push("c"));
        }, 0);
        setTimeout(() => log.push("d"), 0);
        setTimeout(() => console.log(log.join(" ")), 10);
    ''', "a b c d", ["a b d c", "a d b c", "c a b d"],
      "Microtasks run right after each timer callback",
      """Each timer callback is followed by a drain of the promise queue before the next timer starts,
      so `c` runs straight after `b` and before `d`."""),

    q("dedupe-string", '''
        console.log([...new Set("hello")].join(""), [...new Map([[1, "a"]])]);
    ''', "helo [ [ 1, 'a' ] ]",
      ["hello [ [ 1, 'a' ] ]", "helo [ 1, 'a' ]", "helo [ { 1: 'a' } ]"],
      "A Set drops repeats; spreading a Map gives [key, value] pairs",
      """Spreading a string into a Set keeps each letter once, in first-seen order: `helo`. Spreading a
      Map gives an array of two-item arrays."""),

    q("from-entries-map", '''
        const o = { a: 1, b: 2 };
        const doubled = Object.entries(o).map(([k, v]) => [k, v * 2]);
        console.log(Object.fromEntries(doubled), doubled);
    ''', "{ a: 2, b: 4 } [ [ 'a', 2 ], [ 'b', 4 ] ]",
      ["{ a: 1, b: 2 } [ [ 'a', 2 ], [ 'b', 4 ] ]",
       "[ { a: 2 }, { b: 4 } ] [ [ 'a', 2 ], [ 'b', 4 ] ]", "{ a: 2, b: 4 } { a: 2, b: 4 }"],
      "entries and fromEntries convert between objects and pairs",
      """`Object.entries` makes an array of `[key, value]` pairs, `map` returns new pairs without touching
      `o`, and `fromEntries` builds a fresh object from them."""),

    q("iife-getter-only", '''
        const bank = (() => {
          let bal = 0;
          return { dep(n) { bal += n; return this; }, get bal() { return bal; } };
        })();
        bank.dep(5).dep(10);
        bank.bal = 99;
        console.log(bank.bal, bank.dep(1).bal);
    ''', "15 16", ["99 100", "15 15", "99 16"],
      "A getter with no setter ignores assignment (silently, in sloppy mode)",
      """The balance lives in a closure, and the only way in is `dep`. Assigning `bank.bal = 99` does
      nothing because there is no setter, and sloppy mode does not even complain."""),

    q("call-apply-bind", '''
        function f(a, b) { return this.x + a + b; }
        console.log(f.call({ x: 1 }, 2, 3), f.apply({ x: 10 }, [2, 3]),
          f.bind({ x: 100 }, 2)(3));
    ''', "6 15 105", ["6 15 NaN", "NaN 15 105", "6 NaN 105"],
      "call takes arguments one by one, apply takes an array, bind returns a new function",
      """All three set `this`. `call` and `apply` run it immediately, with the arguments spread out or
      in an array. `bind` returns a new function with `this` and the 2 fixed, which you then call with 3."""),

    q("match-global-vs-first", '''
        console.log("a1b22".match(/\\d+/g), "a1b22".match(/\\d+/)[0],
          "abc".match(/\\d/g));
    ''', "[ '1', '22' ] 1 null",
      ["[ '1', '22' ] 1 []", "[ '1', '2', '2' ] 1 null", "[ '1' ] 1 null"],
      "match with g gives all matches, or null (not an empty array) when there are none",
      """The `g` flag returns every match as plain strings, and `\\d+` takes whole runs of digits, so
      22 stays together. Without `g` you get the first match and its details. No match at all is `null`."""),

    q("replace-groups", '''
        console.log("John Smith".replace(/(\\w+) (\\w+)/, "$2, $1"),
          "a-b".replace("-", "$&$&"), "x".replace("x", "$$"));
    ''', "Smith, John a--b $",
      ["$2, $1 a--b $", "Smith, John a-b $", "Smith, John a--b $$"],
      "$1, $& and $$ are special in a replacement string",
      """`$1` and `$2` are the captured groups, `$&` is the whole match, and `$$` is a single literal
      dollar sign. `$&$&` doubles the dash."""),

    q("sort-undefined-last", '''
        console.log([3, undefined, 1, 2].sort(), [3, null, 1].sort());
    ''', "[ 1, 2, 3, undefined ] [ 1, 3, null ]",
      ["[ undefined, 1, 2, 3 ] [ null, 1, 3 ]", "[ 1, 2, 3, undefined ] [ null, 1, 3 ]",
       "[ 1, 2, 3, undefined ] [ 1, null, 3 ]"],
      "sort always puts undefined last; null is sorted as the text 'null'",
      """Undefined items are moved to the end without being compared. `null` becomes the string "null",
      which sorts after "1" and "3" alphabetically."""),

    q("array-join-holes", '''
        console.log(Array(3).join("-"), Array(3).fill().length, [,].length,
          [, ,].length);
    ''', "-- 3 1 2", ["--- 3 1 2", "-- 3 0 1", "-- 3 1 1"],
      "Holes join as empty strings, and one trailing comma is ignored",
      """Three empty slots joined by `-` give two dashes with nothing between. In `[,]` the single comma
      only separates, so the length is 1, and `[, ,]` has length 2."""),

    q("array-keys-spread", '''
        console.log([...Array(3).keys()], [...Array(3)].map((_, i) => i * i),
          Array(3).map((_, i) => i));
    ''', "[ 0, 1, 2 ] [ 0, 1, 4 ] [ <3 empty items> ]",
      ["[ 0, 1, 2 ] [ 0, 1, 4 ] [ 0, 1, 2 ]",
       "[ 0, 1, 2 ] [ undefined, undefined, undefined ] [ <3 empty items> ]",
       "[ <3 empty items> ] [ 0, 1, 4 ] [ <3 empty items> ]"],
      "Spreading fills holes with undefined; map skips holes",
      """`Array(3)` is three holes. `keys()` and spread both visit every slot, so they give real
      values. `Array(3).map` skips holes, so nothing is produced."""),

    q("getter-not-own", '''
        class P {
          constructor() { this.a = 1; }
          get b() { return 2; }
        }
        const p = new P();
        console.log(JSON.stringify(p), Object.keys(p), p.b, "b" in p);
    ''', "{\"a\":1} [ 'a' ] 2 true",
      ["{\"a\":1,\"b\":2} [ 'a', 'b' ] 2 true", "{\"a\":1} [ 'a' ] 2 false",
       "{\"a\":1} [ 'a' ] undefined true"],
      "A class getter lives on the prototype, so it is not an own property",
      """`JSON.stringify` and `Object.keys` only see the object's own properties, and `b` is on the
      class. But it still works as `p.b`, and `in` also looks along the prototype chain."""),

    q("bitwise-truncate", '''
        console.log(7.9 | 0, -7.9 | 0, ~~"12.7", 2 ** 31 | 0);
    ''', "7 -7 12 -2147483648",
      ["8 -8 13 2147483648", "7 -8 12 2147483648", "7 -7 12 0"],
      "Bitwise operators truncate to a 32-bit signed integer",
      """`| 0` cuts the decimals toward zero, so -7.9 becomes -7, not -8. Bitwise operators work on 32-bit
      signed integers, so 2 ** 31 wraps around to the lowest negative number."""),

    q("tosorted-copies", '''
        const a = [3, 1, 2];
        console.log(a.toSorted(), a, a.toReversed(), a.with(0, 9));
    ''', "[ 1, 2, 3 ] [ 3, 1, 2 ] [ 2, 1, 3 ] [ 9, 1, 2 ]",
      ["[ 1, 2, 3 ] [ 1, 2, 3 ] [ 3, 2, 1 ] [ 9, 2, 3 ]",
       "[ 1, 2, 3 ] [ 3, 1, 2 ] [ 3, 2, 1 ] [ 9, 1, 2 ]",
       "[ 1, 2, 3 ] [ 3, 1, 2 ] [ 2, 1, 3 ] [ 9, 1, 2, 3 ]"],
      "toSorted, toReversed and with return copies and leave the original alone",
      """Unlike `sort` and `reverse`, these new methods build a new array. `a` stays `[3, 1, 2]`, the
      reversed copy is `[2, 1, 3]`, and `with(0, 9)` replaces index 0 rather than inserting."""),

    q("findlast", '''
        const n = [1, 2, 3, 4];
        console.log(n.findLast((x) => x % 2), n.findLastIndex((x) => x > 9),
          n.at(-2));
    ''', "3 -1 3", ["1 -1 3", "3 undefined 3", "3 -1 2"],
      "findLast searches from the end; at(-2) is the second last",
      """Searching from the right, the first odd number met is 3. `findLastIndex` says -1 when nothing
      matches, and `at(-2)` is the second-to-last item, 3."""),

    q("dot-regex-replace", '''
        console.log("a.b.c".replaceAll(".", "-"), "a.b.c".replace(/./g, "-"),
          "a.b.c".replace(".", "-"));
    ''', "a-b-c ----- a-b.c",
      ["a-b-c a-b-c a-b-c", "a-b-c a-b-c a-b.c", "a.b.c ----- a-b.c"],
      "In a regex a dot matches any character; in a string it is just a dot",
      """A string pattern is matched literally, so `replaceAll(".", ...)` hits only the dots. The regex
      `/./g` matches every character, giving five dashes. `replace` with a string changes only the first match."""),

    q("undefined-property", '''
        const o = { a: undefined };
        console.log("a" in o, o.a, o.hasOwnProperty("b"), Object.keys(o).length,
          o.b === o.a);
    ''', "true undefined false 1 true",
      ["false undefined false 0 true", "true undefined false 0 true", "true undefined true 1 true"],
      "A key set to undefined still exists, and a missing key also reads undefined",
      """`a` is a real key whose value is undefined, so `in` is true and it is counted by `Object.keys`.
      `b` does not exist, but reading it also gives undefined, so the two compare equal."""),

    q("in-vs-hasown", '''
        console.log("toString" in {}, {}.hasOwnProperty("toString"),
          Object.hasOwn({ a: 1 }, "a"));
    ''', "true false true", ["false false true", "true true true", "true false false"],
      "in follows the prototype chain; hasOwn only checks the object itself",
      """Every object inherits `toString` from `Object.prototype`, so `in` finds it. It is not one of
      the object's own properties, so `hasOwnProperty` says false."""),

    q("flatmap-filter", '''
        console.log([1, 2, 3].flatMap((x) => (x % 2 ? [x, x] : [])),
          [[1, 2], [3]].flatMap((x) => x), [[[1]]].flatMap((x) => x));
    ''', "[ 1, 1, 3, 3 ] [ 1, 2, 3 ] [ [ 1 ] ]",
      ["[ 1, 1, 3, 3 ] [ 1, 2, 3 ] [ 1 ]",
       "[ [ 1, 1 ], [], [ 3, 3 ] ] [ 1, 2, 3 ] [ [ 1 ] ]",
       "[ 1, 3 ] [ [ 1, 2 ], [ 3 ] ] [ [ 1 ] ]"],
      "flatMap flattens only one level, so returning [] removes an item",
      """Each returned array is spliced into the result, so an empty array removes the item and a
      two-item array duplicates it. Only one level is flattened, which leaves `[[1]]` as `[ [ 1 ] ]`."""),

    q("assign-mutates", '''
        const a = { x: 1 };
        const b = Object.assign(a, { y: 2 });
        const c = Object.assign({}, a, { x: 9 });
        console.log(a, a === b, c);
    ''', "{ x: 1, y: 2 } true { x: 9, y: 2 }",
      ["{ x: 1 } false { x: 9, y: 2 }", "{ x: 1, y: 2 } false { x: 9, y: 2 }",
       "{ x: 9, y: 2 } true { x: 9, y: 2 }"],
      "Object.assign changes its first argument and returns that same object",
      """`Object.assign(a, ...)` writes into `a` and gives `a` back, so `a === b`. Passing `{}` first
      builds a new object instead, so `c` can differ without touching `a`."""),

    q("do-while-postfix", '''
        let n = 0;
        do {
          n++;
        } while (n < 0);
        let m = 5;
        while (m-- > 3);
        console.log(n, m);
    ''', "1 2", ["0 3", "1 3", "0 2"],
      "do-while runs once before testing; m-- decrements even when the test fails",
      """The do block always runs once, so `n` is 1. In the while loop, `m` is compared and then
      decreased each time: 5, 4, then 3 fails the test but is still decremented, leaving 2."""),

    q("sequential-then-parallel", '''
        const log = [];
        const sleep = (ms, v) => new Promise((r) => {
          setTimeout(() => { log.push(v); r(); }, ms);
        });
        (async () => {
          await sleep(20, "a");
          await sleep(10, "b");
          await Promise.all([sleep(30, "c"), sleep(5, "d")]);
          console.log(log.join(""));
        })();
    ''', "abdc", ["abcd", "dbac", "bdac"],
      "Awaiting one after another is sequential; Promise.all starts them together",
      """`a` and `b` run one after the other, in that order. Then `c` and `d` start at the same time, and
      `d` needs only 5 ms, so it finishes first."""),

    q("logical-assignment", '''
        let a = null, b = 0, c = 1;
        a ??= 5;
        b ||= 6;
        c &&= 7;
        console.log(a, b, c);
    ''', "5 6 7", ["5 0 7", "null 6 7", "5 6 1"],
      "??= assigns on null/undefined, ||= on falsy, &&= on truthy",
      """`a` is null so it gets 5. `b` is 0, which is falsy, so `||=` replaces it with 6. `c` is truthy,
      so `&&=` assigns 7."""),

    q("group-by-reduce", '''
        const g = ["a", "bb", "cc"].reduce((acc, w) => {
          (acc[w.length] ||= []).push(w);
          return acc;
        }, {});
        console.log(g);
    ''', "{ '1': [ 'a' ], '2': [ 'bb', 'cc' ] }",
      ["{ 1: [ 'a' ], 2: [ 'bb', 'cc' ] }", "[ [ 'a' ], [ 'bb', 'cc' ] ]", "{ '1': 'a', '2': 'cc' }"],
      "Object keys are strings, so numeric keys are printed quoted",
      """`||=` creates the array the first time a length is seen, and `push` adds the word to it. The
      lengths become the string keys '1' and '2', which node prints in quotes."""),

    q("split-regex-capture", '''
        const s = "a1b2c";
        console.log(s.split(/\\d/), s.split(/(\\d)/), s.split(/\\d/, 2));
    ''', "[ 'a', 'b', 'c' ] [ 'a', '1', 'b', '2', 'c' ] [ 'a', 'b' ]",
      ["[ 'a', 'b', 'c' ] [ 'a', 'b', 'c' ] [ 'a', 'b' ]",
       "[ 'a', 'b', 'c' ] [ 'a', '1', 'b', '2', 'c' ] [ 'a', '1' ]",
       "[ 'a', 'b', 'c' ] [ '1', '2' ] [ 'a', 'b' ]"],
      "A capturing group in a split pattern keeps the separators",
      """Splitting on `\\d` drops the digits, but wrapping it in parentheses puts each separator back
      into the result. The limit counts pieces of the result, so 2 gives the first two letters."""),

    # ── Harder: the language's odd corners ─────────────────────────────────
    q("parseint-small-float", '''
        console.log(parseInt(0.0000005), parseInt(null), parseInt("  7  "),
          parseInt(15.99), parseInt("1e3"), Math.floor("7.9"));
    ''', "5 NaN 7 15 1 7",
      ["0 NaN 7 15 1000 7", "0 0 7 15 1 7", "5 NaN 7 16 1 7"],
      "parseInt reads the number as text, and 0.0000005 is the text '5e-7'",
      """`parseInt` first turns its argument into a string. `0.0000005` becomes "5e-7", and parsing stops
      at the `e`, giving 5. `null` becomes "null" (NaN), and "1e3" gives just the 1 before the `e`."""),

    q("generator-next-args", '''
        function* g() {
          const a = yield 1;
          const b = yield a + 1;
          return a + b;
        }
        const it = g();
        console.log(it.next(), it.next(10), it.next(5), it.next());
    ''', "{ value: 1, done: false } { value: 11, done: false } { value: 15, done: true } { value: undefined, done: true }",
      ["{ value: 1, done: false } { value: 11, done: false } { value: 5, done: true } { value: undefined, done: true }",
       "{ value: 1, done: false } { value: 10, done: false } { value: 15, done: true } { value: undefined, done: true }",
       "{ value: 1, done: false } { value: 11, done: false } { value: 15, done: true } { value: 15, done: true }"],
      "The argument of next() becomes the result of the yield that paused",
      """The first `next()` runs to the first `yield`, so any argument there is ignored. `next(10)` makes
      that yield evaluate to 10, so the next value is 11. `next(5)` sets `b`, and `return a + b` gives 15."""),

    q("tagged-template", '''
        function tag(s, ...v) {
          return s.raw.join("|") + v.join(",");
        }
        console.log(tag`a${1}b${2}c`);
    ''', "a|b|c1,2", ["a1b2c", "a|b|c12", "a|b|c|1,2"],
      "A tag function gets the text pieces and the values separately",
      """The first argument is the array of literal pieces `["a", "b", "c"]`, and the rest are the
      substituted values 1 and 2. The function decides how, or whether, to put them back together."""),

    q("json-clone-loses", '''
        const o = { d: new Date(0), u: undefined, n: NaN, r: /a/, f() {},
          k: [undefined] };
        console.log(JSON.parse(JSON.stringify(o)));
    ''', "{ d: '1970-01-01T00:00:00.000Z', n: null, r: {}, k: [ null ] }",
      ["{ d: 1970-01-01T00:00:00.000Z, u: undefined, n: NaN, r: /a/, f: [Function: f], k: [ undefined ] }",
       "{ d: '1970-01-01T00:00:00.000Z', n: null, r: {}, k: [ undefined ] }",
       "{ d: 0, n: null, r: {}, k: [ null ] }"],
      "A JSON round trip is not a faithful deep copy",
      """The Date becomes its ISO string, NaN becomes null, a regex becomes an empty object, and
      undefined and functions are dropped from objects (or turned into null inside arrays)."""),

    q("bitwise-int32", '''
        console.log(~5, 1 << 31, -1 >>> 0, 2 ** 32 | 0, -8 >> 1, -8 >>> 28);
    ''', "-6 -2147483648 4294967295 0 -4 15",
      ["-5 2147483648 -1 4294967296 -4 15", "-6 -2147483648 -1 0 -4 15",
       "-6 2147483648 4294967295 0 4 15"],
      "Bitwise operators see 32-bit signed integers, except >>> which gives unsigned",
      """`~5` is -6, and `1 << 31` sets the sign bit, making it negative. `-1 >>> 0` reinterprets all
      ones as unsigned, 4294967295, and `2 ** 32 | 0` wraps all the way to 0."""),

    q("groupby-null-prototype", '''
        const g = Object.groupBy([1, 2, 3, 4], (x) => (x % 2 ? "odd" : "even"));
        console.log(g, Object.getPrototypeOf(g));
    ''', "[Object: null prototype] { odd: [ 1, 3 ], even: [ 2, 4 ] } null",
      ["{ odd: [ 1, 3 ], even: [ 2, 4 ] } {}",
       "[Object: null prototype] { even: [ 2, 4 ], odd: [ 1, 3 ] } null",
       "Map(2) { 'odd' => [ 1, 3 ], 'even' => [ 2, 4 ] } null"],
      "Object.groupBy returns an object with no prototype, in first-seen key order",
      """The groups are keyed in the order they first appear, so `odd` comes first. The result is made
      with `Object.create(null)`, which is why node labels it and why its prototype is null."""),

    q("valueof-vs-tostring", '''
        const o = { valueOf() { return 42; }, toString() { return "str"; } };
        console.log(o + 1, `${o}`, o * 2, String(o), o + "");
    ''', "43 str 84 str 42",
      ["str1 str 84 str str", "43 str 84 str str", "43 42 84 42 42"],
      "Arithmetic and + prefer valueOf; templates and String() prefer toString",
      """With `+` and `*` the default hint is number, so `valueOf` is used, even for `o + ""`, which gives
      "42". Template literals and `String()` ask for text first, so they use `toString`."""),

    q("block-function-hoist", '''
        const r = [typeof f];
        {
          function f() {}
        }
        r.push(typeof f);
        console.log(r.join());
    ''', "undefined,function", ["function,function", "undefined,undefined", "function,undefined"],
      "In sloppy mode a function in a block also creates a var, filled in when the block runs",
      """Sloppy-mode code hoists the name `f` out of the block as a var, initially undefined. Only when
      execution reaches the block is the function assigned to it, so `typeof f` changes."""),

    q("object-create-this", '''
        const base = { n: 1, hi() { return "base " + this.n; } };
        const child = Object.create(base);
        child.n = 2;
        console.log(child.hi(), Object.keys(child), "hi" in child, base.n);
    ''', "base 2 [ 'n' ] true 1",
      ["base 1 [ 'n' ] true 1", "base 2 [ 'n', 'hi' ] true 1", "base 2 [ 'n' ] true 2"],
      "Assigning on a child creates its own property; this is whoever you call it on",
      """`hi` is found on the prototype, but it is called on `child`, so `this.n` is the child's own 2.
      The assignment `child.n = 2` never touches `base`, and `hi` is not an own key."""),

    q("private-field-hidden", '''
        class A {
          #x = 1;
          get x() { return this.#x; }
          static has(o) { return #x in o; }
        }
        console.log(new A().x, A.has(new A()), A.has({}), JSON.stringify(new A()));
    ''', "1 true false {}",
      ["1 true true {}", "1 true false {\"x\":1}", "undefined true false {}"],
      "Private fields are invisible to JSON and to everything outside the class",
      """`#x` is not a property in the usual sense, so `JSON.stringify` does not see it, even though a
      public getter `x` exists on the class. `#x in o` is a brand check that is true only for real instances."""),

    q("proxy-get-trap", '''
        const p = new Proxy({}, { get: (t, k) => String(k).length });
        console.log(p.abc, p.hello, p[12345], p.length);
    ''', "3 5 5 6", ["3 5 12345 6", "undefined 5 5 6", "3 5 5 0"],
      "A get trap answers every property read, and keys arrive as strings",
      """The trap runs for any property, even ones that were never set. `p[12345]` receives the key as
      the string "12345", which has length 5, and `p.length` is asking for the 6-letter name "length"."""),

    q("return-promise-extra-ticks", '''
        const log = [];
        Promise.resolve()
          .then(() => { log.push("a1"); return Promise.resolve(); })
          .then(() => log.push("a2"));
        Promise.resolve()
          .then(() => log.push("b1"))
          .then(() => log.push("b2"))
          .then(() => log.push("b3"))
          .then(() => log.push("b4"));
        setTimeout(() => console.log(log.join(" ")));
    ''', "a1 b1 b2 b3 a2 b4",
      ["a1 b1 a2 b2 b3 b4", "a1 b1 b2 a2 b3 b4", "a1 a2 b1 b2 b3 b4"],
      "Returning a promise from then costs extra microtask turns",
      """When a `then` callback returns a promise, the chain has to wait for that promise, which takes
      about two extra turns of the microtask queue. So `a2` is late and comes after `b3`."""),

    q("custom-iterator", '''
        const r = {
          from: 1,
          to: 3,
          [Symbol.iterator]() {
            let c = this.from;
            const t = this.to;
            return {
              next: () => (c <= t ? { value: c++, done: false } : { done: true }),
            };
          },
        };
        console.log([...r], Math.max(...r), Array.from(r, (x) => x * 2));
    ''', "[ 1, 2, 3 ] 3 [ 2, 4, 6 ]",
      ["[ 1, 2, 3 ] 3 [ 1, 2, 3 ]", "[ 1, 2, 3 ] NaN [ 2, 4, 6 ]", "[ 1, 2, 3 ] 3 [ 2, 4, 6, 8 ]"],
      "Any object with [Symbol.iterator] works with spread, for-of and Array.from",
      """The iterator protocol is just a `next()` that returns `{ value, done }`. Once an object has it,
      spread, `Math.max(...)` and `Array.from` all consume it, and `Array.from` can map as it goes."""),

    q("json-replacer-array", '''
        const o = { a: 1, b: { a: 2, c: 3 } };
        console.log(JSON.stringify(o, ["a", "b"]),
          JSON.stringify({ d: { toJSON() { return "X"; } } }));
    ''', "{\"a\":1,\"b\":{\"a\":2}} {\"d\":\"X\"}",
      ["{\"a\":1,\"b\":{\"a\":2,\"c\":3}} {\"d\":\"X\"}", "{\"a\":1} {\"d\":\"X\"}",
       "{\"a\":1,\"b\":{\"a\":2}} {\"d\":{}}"],
      "An array replacer is a whitelist of keys at every level; toJSON controls a value",
      """The list `["a", "b"]` keeps only those keys, including inside the nested object, so `c` is
      dropped. An object with a `toJSON` method is replaced by whatever that method returns."""),

    q("chained-assign-old-ref", '''
        let a = { n: 1 };
        const b = a;
        a.x = a = { n: 2 };
        console.log(a.x, b.x);
    ''', "undefined { n: 2 }", ["{ n: 2 } { n: 2 }", "undefined undefined", "{ n: 2 } undefined"],
      "The left-hand reference a.x is worked out before the assignments run",
      """JavaScript first resolves `a.x` against the old object, then does `a = { n: 2 }`, then stores that new
      object into the old object's `x`. So `b.x` is set, and the new `a` has no `x`."""),

    q("named-groups-strings", '''
        const { y, m } = "2024-05-06".match(/(?<y>\\d+)-(?<m>\\d+)/).groups;
        console.log(y, m, +m, m + 1);
    ''', "2024 05 5 051", ["2024 5 5 6", "2024 05 5 6", "2024 05 05 051"],
      "Captured groups are always strings",
      """`m` is the text "05", so it prints with its zero. A unary `+` turns it into the number 5, but
      `m + 1` is string joining, which gives "051"."""),

    q("regex-greedy", '''
        const s = "<a><b>";
        console.log(s.match(/<.+>/)[0], s.match(/<.+?>/)[0], s.match(/<[^>]+>/g));
    ''', "<a><b> <a> [ '<a>', '<b>' ]",
      ["<a> <a> [ '<a>' ]", "<a><b> <a><b> [ '<a>', '<b>' ]", "<a> <a> [ '<a>', '<b>' ]"],
      "+ is greedy; +? takes as little as possible",
      """`.+` grabs as much as it can and then backs off only as far as needed, so it spans both tags.
      `.+?` stops at the first `>`. `[^>]+` with the g flag finds each tag separately."""),

    q("await-rejected-order", '''
        const log = [];
        (async () => {
          try { await Promise.reject(new Error("x")); log.push("no"); }
          catch { log.push("caught"); }
          finally { log.push("finally"); }
          log.push("after");
        })();
        Promise.resolve().then(() => log.push("tick"));
        setTimeout(() => console.log(log.join(" ")));
    ''', "caught finally after tick",
      ["tick caught finally after", "no caught finally after tick", "caught tick finally after"],
      "After an await resumes, the rest of the async function runs in one go",
      """The `await` was queued before the `then`, so the async function resumes first, and then it
      runs `catch`, `finally` and the last line without another pause. Only after that does `tick` run."""),

    q("tostring-tag-call", '''
        const t = (v) => Object.prototype.toString.call(v);
        console.log(t([]), t(null), t(1), t(new Date(0)), t(/a/));
    ''', "[object Array] [object Null] [object Number] [object Date] [object RegExp]",
      ["[object Object] [object Null] [object Number] [object Date] [object RegExp]",
       "[object Array] [object undefined] [object Number] [object Date] [object RegExp]",
       "[object Array] [object Null] [object Object] [object Object] [object Object]"],
      "Object.prototype.toString.call names the real built-in type, even for null",
      """Called directly on `Object.prototype`, `toString` reports each value's internal type tag. Unlike
      `typeof`, it tells arrays, dates and regexes apart, and it even has a name for null."""),

    q("tofixed-20", '''
        console.log((0.1).toFixed(20), (0.5).toFixed(20).length,
          (1.005).toFixed(20));
    ''', "0.10000000000000000555 22 1.00499999999999989342",
      ["0.10000000000000000000 22 1.00500000000000000000",
       "0.10000000000000000555 22 1.00500000000000000000", "0.1 22 1.005"],
      "Asking for more digits shows the binary error hiding in a float",
      """0.1 and 1.005 are not stored exactly, and `toFixed(20)` writes out the digits that are really
      there. That is why `(1.005).toFixed(2)` rounds down to 1.00. 0.5 is exact, so it is zeros."""),

    q("toprecision", '''
        console.log((123.456).toPrecision(4), (0.00001234).toPrecision(2),
          (1234567).toPrecision(2), (5).toPrecision(3));
    ''', "123.5 0.000012 1.2e+6 5.00",
      ["123.4 0.000012 1.2e+6 5.00", "123.5 0.000012 1200000 5.00", "123.5 0.000012 1.2e+6 5"],
      "toPrecision counts significant digits, not decimals, and may use exponent form",
      """`toPrecision(4)` keeps four significant digits, rounding 123.456 to 123.5. When a number is too
      big for the digits asked, as with 1234567 and 2, it switches to exponent form: `1.2e+6`."""),

    q("sort-stable-objects", '''
        const people = [{ n: "b", a: 1 }, { n: "a", a: 1 }, { n: "c", a: 0 }];
        console.log(people.sort((x, y) => x.a - y.a).map((p) => p.n).join(""));
    ''', "cba", ["cab", "abc", "bac"],
      "sort is stable: equal items keep their original order",
      """Sorting by `a` puts the one with 0 first. `b` and `a` tie at 1, and since the sort is stable
      they stay as they were, `b` before `a`. The names do not break the tie."""),

    q("default-evaluated-each-call", '''
        let n = 0;
        const f = (a = ++n) => a;
        console.log(f(), f(), f(10), f(undefined), n);
    ''', "1 2 10 3 3", ["1 1 10 1 1", "1 2 10 2 2", "1 2 10 3 4"],
      "A default runs on every call where the argument is missing or undefined",
      """Unlike in Python, JavaScript evaluates the default expression freshly each time, so `++n` runs
      again. It is skipped for `f(10)`, but explicitly passing `undefined` still triggers it."""),

    q("number-literal-methods", '''
        console.log(1..toString(), 1.5.toFixed(), (1).constructor.name,
          5..toString(2));
    ''', "1 2 Number 101", ["1 1 Number 101", "1 2 number 101", "1 2 Number 5"],
      "A number literal can have methods; 1.toString() would be a syntax error but 1..toString() is fine",
      """The first dot belongs to the number (`1.`), so the second dot starts the method call. `1.5.toFixed()`
      has no digits asked, so it rounds to the whole number 2, and `5..toString(2)` is 5 in binary."""),

    q("computed-keys", '''
        const k = "x";
        const o = { [k + 1]: 1, k, [`${k}2`]: 2 };
        console.log(o, o.k, o.x1);
    ''', "{ x1: 1, k: 'x', x2: 2 } x 1",
      ["{ x1: 1, x: 'x', x2: 2 } undefined 1", "{ [k + 1]: 1, k: 'x', x2: 2 } x 1",
       "{ x1: 1, k: 'x', x2: 2 } x undefined"],
      "Brackets compute a key; a bare name is shorthand for name: name",
      """`[k + 1]` is evaluated to the key "x1". The shorthand `k` means `k: k`, so the key is literally
      "k" with the value "x", not a key called "x"."""),

    q("destructure-order", '''
        const log = [];
        const o = {
          get a() { log.push("a"); return 1; },
          get b() { log.push("b"); return 2; },
        };
        const { b, a } = o;
        console.log(log.join(""), a + b);
    ''', "ba 3", ["ab 3", "abab 3", "b 3"],
      "Destructuring reads properties in the order you list them in the pattern",
      """The pattern `{ b, a }` reads `b` first and `a` second, so the getters run in that order. The
      order of the keys in the object itself does not matter."""),

    q("array-from-forms", '''
        console.log(Array.from({ length: 2, 0: "a", 1: "b" }),
          Array.from("12", Number), Array.from({ length: 2 }));
    ''', "[ 'a', 'b' ] [ 1, 2 ] [ undefined, undefined ]",
      ["[ 'a', 'b' ] [ 1, 2 ] [ <2 empty items> ]", "[] [ 1, 2 ] [ undefined, undefined ]",
       "[ 'a', 'b' ] [ '1', '2' ] [ undefined, undefined ]"],
      "Array.from accepts any array-like with a length, and fills gaps with undefined",
      """An object with `length` and numbered keys counts as array-like, so it converts. With only a
      length, every slot reads as undefined and is a real value, not a hole. The second argument maps."""),

    q("for-await-order", '''
        async function* gen() {
          yield 1;
          yield 2;
        }
        const log = [];
        (async () => {
          for await (const x of gen()) log.push(x);
          log.push("done");
        })();
        log.push("sync");
        setTimeout(() => console.log(log.join(" ")));
    ''', "sync 1 2 done", ["1 2 done sync", "sync done 1 2", "done sync 1 2"],
      "An async function runs synchronously until its first await",
      """The async arrow starts, reaches the first `for await` step, and pauses, so the synchronous
      `log.push("sync")` goes first. The items and "done" are added in later microtasks."""),

    q("comma-loses-this", '''
        const o = { f() { return this === o; } };
        console.log(o.f(), (o.f)(), (0, o.f)(), (o.f || 0)());
    ''', "true true false false",
      ["true true true true", "true false false false", "true true true false"],
      "this comes from the call syntax, and the comma operator or || hands over a bare function",
      """Parentheses alone keep the reference, so `(o.f)()` still has `this` as `o`. But `(0, o.f)` and
      `(o.f || 0)` produce the function value alone, so the call has no object."""),

    q("let-loop-body-increment", '''
        const fns = [];
        for (let i = 0; i < 3; i++) {
          fns.push(() => i);
          i++;
        }
        console.log(fns.map((f) => f()));
    ''', "[ 1, 3 ]", ["[ 0, 1, 2 ]", "[ 0, 2 ]", "[ 1, 2 ]"],
      "Each pass has its own i, but the body's change to it is kept by the closure",
      """The first closure sees its own pass's `i`, which the body bumped from 0 to 1. The next pass starts
      from a copy of 1, the loop adds 1 (to 2), and the body bumps it to 3. There is no third pass."""),

    q("date-plus-minus", '''
        const a = new Date(5), b = new Date(2);
        console.log(a - b, typeof (a + b), typeof (a - b), a > b, a == new Date(5));
    ''', "3 string number true false",
      ["3 number number true false", "NaN string number true false", "3 string number true true"],
      "A Date turns into text for + but into a number for - and comparisons",
      """With `-` and `>` a Date is converted to its timestamp, so the difference is 3 and the comparison
      works. With `+` it becomes text, and `==` between two Date objects compares identity, which is false."""),

    q("thenable-await", '''
        const log = [];
        const t = { then(res) { res("T"); } };
        Promise.resolve(t).then((v) => log.push("p" + v));
        (async () => { log.push("a" + (await t)); })();
        setTimeout(() => console.log(log.join(" ")));
    ''', "pT aT", ["aT pT", "pundefined aT", "p[object Object] a[object Object]"],
      "Any object with a then method is treated like a promise",
      """Both `Promise.resolve(t)` and `await t` call `t.then`, which passes "T" along, so neither
      sees the object itself. They are queued in the order they were written, so `p` goes first."""),

    q("radix-conversions", '''
        console.log((0.5).toString(2), (255).toString(16).toUpperCase(),
          parseInt("ff", 16), parseInt("12", 2), (-255).toString(16));
    ''', "0.1 FF 255 1 -ff",
      ["0.1 FF 255 NaN -ff", "0.5 FF 255 1 -ff", "0.1 FF 255 1 ff"],
      "parseInt stops at the first digit that is invalid for the base",
      """`parseInt("12", 2)` reads the 1 and then hits a 2, which is not a binary digit, so it stops
      with 1. `toString(2)` also works on fractions, and the sign of a negative number stays in front."""),

    q("promise-any-aggregate", '''
        Promise.any([Promise.reject(1), Promise.reject(2)])
          .catch((e) => console.log(e.constructor.name, e.errors));
    ''', "AggregateError [ 1, 2 ]",
      ["Error [ 1, 2 ]", "AggregateError 1", "Error 1"],
      "Promise.any rejects with an AggregateError that holds every reason",
      """`any` waits for the first success, and if there is none it rejects with an `AggregateError`.
      The individual rejection reasons are in its `errors` array, in input order."""),

    q("unicode-normalize", '''
        const a = "e\\u0301", b = "\\u00e9";
        console.log(a.length, b.length, a === b, a.normalize() === b,
          [...a].length);
    ''', "2 1 false true 2", ["1 1 true true 1", "2 1 true true 2", "2 1 false false 2"],
      "The same-looking text can be different code points until it is normalised",
      """`a` is a plain `e` plus a combining accent, two code units, while `b` is one precomposed
      character. They look the same but are not `===` until `normalize()` joins `a` into one character."""),

    q("assign-eval-order", '''
        let i = 0;
        const a = [];
        a[i++] = i++;
        console.log(a, i);
    ''', "[ 1 ] 2", ["[ 0 ] 2", "[ <1 empty item>, 0 ] 2", "[ 1 ] 1"],
      "The target's index is worked out before the right-hand side runs",
      """JavaScript evaluates `a[i++]` first, taking index 0 and bumping `i` to 1. Then the right side
      `i++` produces 1 and bumps `i` to 2, so the 1 is stored at index 0."""),

    # ── END ──
)
