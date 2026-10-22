"""Gotchas, JavaScript, the fourth helping: arrays, objects, strings, regex, classes, the event loop and more.

Same rules as content_js.py: run by tests/test_gotchas_content.py in real node (CommonJS, sloppy mode); the
marked answer must be exactly what `console.log` printed (or, with raises=True, the name of the error the
program dies with, having printed nothing), the wrong options are real misreads, and event-loop programs
collect their steps into an array and print once. About a third look easy on purpose, the rest are middle
and hard traps. They come after the earlier modules in the deck.
"""

from __future__ import annotations

from .items import Item, make

q = make("javascript")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: small things with a real trap ────────────────────────
    # E
    q("reduceright-order", '''
        const a = ["a", "b", "c"];
        const add = (acc, x) => acc + x;
        console.log(a.reduceRight(add), a.reduce(add, ">"));
    ''', "cba >abc", ["abc >abc", "cba >cba", "abc >cba"],
      "reduceRight walks from the end, and with no start value the last item starts it",
      """`reduceRight` starts with the last item as the accumulator and adds the earlier ones after it, so the
      string comes out reversed. `reduce` with a start value `">"` goes left to right."""),

    # E
    q("unshift-same-array", '''
        const a = [3];
        console.log(a.unshift(1, 2), a, a.push(4, 5), a);
    ''', "3 [ 1, 2, 3, 4, 5 ] 5 [ 1, 2, 3, 4, 5 ]",
      ["3 [ 1, 2, 3 ] 5 [ 1, 2, 3, 4, 5 ]", "3 [ 2, 1, 3, 4, 5 ] 5 [ 2, 1, 3, 4, 5 ]",
       "1 [ 1, 2, 3, 4, 5 ] 2 [ 1, 2, 3, 4, 5 ]"],
      "Both methods return the new length, and the array is printed after all the calls",
      """`unshift(1, 2)` inserts the items as a block at the front and returns the new length, 3. The arguments
      to `console.log` are all evaluated before anything prints, so the same array is shown in its final state
      twice."""),

    # E
    q("delete-and-readd-key", '''
        const o = { a: 1, b: 2, c: 3 };
        delete o.a;
        o.a = 9;
        o.b = 0;
        console.log(Object.keys(o).join(), JSON.stringify(o));
    ''', 'b,c,a {"b":0,"c":3,"a":9}',
      ['a,b,c {"a":9,"b":0,"c":3}', 'b,c,a {"b":2,"c":3,"a":9}', 'a,b,c {"b":0,"c":3,"a":9}'],
      "A deleted key that comes back goes to the end; changing a value keeps its place",
      """Deleting `a` removes it from the order, so the new `a` is added after `c`. Assigning to the existing
      `b` only changes its value and leaves it where it was."""),

    # E
    q("instanceof-primitives", '''
        console.log("a" instanceof String, new String("a") instanceof String,
          [] instanceof Object, Object.create(null) instanceof Object);
    ''', "false true true false", ["true true true true", "false false true false", "false true true true"],
      "instanceof is false for primitives and for objects with no prototype chain",
      """A string primitive is not an object, so it is not an instance of String; the wrapper made by
      `new String` is. An array is an Object through its prototype chain, but `Object.create(null)` has no
      chain at all."""),

    # E
    q("comma-in-for-header", '''
        let i, j;
        for (i = 0, j = 10; i < j; i += 3, j -= 3);
        console.log(i, j);
    ''', "6 4", ["3 7", "9 1", "6 7"],
      "The comma runs both updates, and the loop stops as soon as the test fails",
      """After each pass both counters move: (0, 10), (3, 7), (6, 4). At (6, 4) the test `i < j` is false, so
      the loop ends with those values. The semicolon at the end is an empty body."""),

    # E
    q("labelled-block-break", '''
        let s = "";
        blk: {
          s += "a";
          if (s) break blk;
          s += "b";
        }
        s += "c";
        console.log(s);
    ''', "ac", ["abc", "a", "ab"],
      "break label leaves a plain labelled block, not just loops",
      """`break blk` jumps to the end of the labelled block, skipping `s += "b"`. Execution then carries on
      after the block, so "c" is added."""),

    # E
    q("typeof-everything", '''
        console.log([class {}, Symbol(), 1n, /x/, new Date(0), async () => 1]
          .map((v) => typeof v).join());
    ''', "function,symbol,bigint,object,object,function",
      ["class,symbol,bigint,regexp,date,async", "function,symbol,number,object,object,object",
       "function,symbol,bigint,regexp,object,function"],
      "typeof has no class, regexp or date answer: classes and async functions are 'function'",
      """A class is a function under the hood, so `typeof` says "function". An async arrow is a function too.
      Regular expressions and dates are plain objects, and symbols and bigints have their own results."""),

    # E
    q("spread-sets-maps", '''
        console.log([...new Set("hello")].join(""), [...new Map([["a", 1]])],
          [...new Map([["a", 1]]).keys()]);
    ''', "helo [ [ 'a', 1 ] ] [ 'a' ]",
      ["hello [ [ 'a', 1 ] ] [ 'a' ]", "helo [ { a: 1 } ] [ 'a' ]", "helo [ [ 'a', 1 ] ] [ 'a', 1 ]"],
      "A Set drops repeats, and spreading a Map gives [key, value] pairs",
      """The string is iterated letter by letter and the Set keeps one `l`. Spreading a Map gives its
      entries, each a two-item array, while `.keys()` gives only the keys."""),

    # E
    q("exponent-right-assoc", '''
        console.log(2 ** 3 ** 2, (-2) ** 2, 2 ** -1, (-8) ** (1 / 3), 10 % 3 ** 2);
    ''', "512 4 0.5 NaN 1",
      ["64 4 0.5 NaN 1", "512 4 0.5 -2 1", "512 4 0 NaN 1"],
      "** groups from the right, and a negative base with a fractional power is NaN",
      """`2 ** 3 ** 2` is `2 ** (3 ** 2)`, which is 512. A real cube root of -8 would be -2, but `**` with a
      fractional exponent of a negative number gives NaN. `**` also binds tighter than `%`."""),

    # E
    q("timeout-args-and-clear", '''
        const log = [];
        const t = setTimeout(() => log.push("never"), 0);
        setTimeout((a, b) => log.push(a + b), 0, "x", "y");
        clearTimeout(t);
        setTimeout(() => console.log(log.join(",")), 5);
    ''', "xy", ["never,xy", "xundefined", "x,y"],
      "setTimeout passes extra arguments to the callback, and clearTimeout cancels a pending one",
      """The third and fourth arguments of `setTimeout` are handed to the callback, so `a + b` is "xy". The
      first timer is cleared before the event loop gets to run it."""),

    # E
    q("promise-settles-once", '''
        new Promise((resolve, reject) => {
          resolve(1);
          reject(2);
          resolve(3);
          throw new Error("late");
        }).then((v) => console.log("ok", v), (e) => console.log("err", e));
    ''', "ok 1", ["err 2", "ok 3", "err Error: late"],
      "A promise keeps the first resolve or reject; everything after is ignored",
      """Once it is settled with 1, later calls to `resolve` or `reject` do nothing. An error thrown after
      that is swallowed too, because the promise is already settled."""),

    # E
    q("lookbehind-match", '''
        const re = /(?<=\\$)\\d+/g;
        console.log("$10 E20 $30".match(re), "$10".match(re)[0]);
    ''', "[ '10', '30' ] 10", ["[ '$10', '$30' ] 10", "[ '10', '20', '30' ] 10", "[ '10', '30' ] $10"],
      "A lookbehind is checked but not included in the match",
      """`(?<=\\$)` requires a dollar sign right before the digits without making it part of the result. So
      only the numbers after a `$` match, and without the `$` in them."""),

    # E
    q("split-lengths", '''
        const n = (s, sep) => s.split(sep).length;
        console.log(n("bbb", "b"), n("a,b,", ","), n("", ","), n("", ""));
    ''', "4 3 1 0", ["3 2 0 0", "4 3 0 0", "3 3 1 1"],
      "Separators at the ends give empty pieces, and an empty string splits to one empty piece",
      """Three `b` characters make four pieces (all empty). A trailing comma leaves an empty last piece, and
      `"".split(",")` is `[""]`, one piece. Only splitting on the empty separator gives no pieces at all."""),

    # E
    q("generic-array-methods", '''
        console.log(Array.prototype.map.call("abc", (c) => c + c),
          Array.prototype.join.call({ length: 2, 0: "a", 1: "b" }, "-"));
    ''', "[ 'aa', 'bb', 'cc' ] a-b", ["TypeError", "aabbcc a-b", "[ 'aa', 'bb', 'cc' ] a,b"],
      "Array methods work on any array-like with a length and numbered keys",
      """`map` and `join` only need `length` and indexed access, so they run on a string or a plain object
      shaped like an array. `map` still returns a real array."""),

    # E
    q("string-props-ignored", '''
        const s = "abc";
        s.length = 1;
        s.extra = 2;
        console.log(s.length, s.extra);
    ''', "3 undefined", ["1 2", "3 2", "1 undefined"],
      "Writing to a string primitive silently does nothing (in sloppy mode)",
      """A primitive string has no own storage: `length` is read-only and a new property is lost with the
      temporary wrapper object. In strict mode the first assignment would throw a TypeError instead."""),

    # E
    q("infinity-arithmetic", '''
        console.log(Infinity - Infinity, 1 / Infinity, 0 * Infinity,
          Infinity > Number.MAX_VALUE, Math.min() > Math.max());
    ''', "NaN 0 NaN true true", ["0 0 0 true true", "NaN 0 0 true true", "NaN 0 NaN false false"],
      "Infinity minus itself is NaN, and Math.min() of nothing is Infinity",
      """Subtracting infinities and multiplying 0 by infinity are undefined, so they give NaN. With no
      arguments `Math.min()` is Infinity and `Math.max()` is -Infinity, so the last comparison is true."""),

    # E
    q("size-not-length", '''
        console.log(new Set([1, 2, 2]).length, new Set([1, 2, 2]).size,
          new Map([[1, 2]]).length, [1, 2].size);
    ''', "undefined 2 undefined undefined", ["3 2 1 2", "2 2 1 2", "undefined 2 1 undefined"],
      "Sets and Maps have size; arrays have length; the wrong one is just undefined",
      """Reading a property that does not exist gives `undefined`, not an error. `Set` and `Map` expose `.size`,
      while only arrays and strings have `.length`."""),

    # E
    q("return-inside-foreach", '''
        function f() {
          [1, 2, 3].forEach((x) => {
            if (x === 2) return "found";
          });
          return "none";
        }
        console.log(f());
    ''', "none", ["found", "undefined", "2"],
      "A return inside a forEach callback only leaves that callback",
      """The `return` belongs to the arrow function, which runs once per item. It ends that one call and
      does not stop the loop or `f`, so the function reaches `return "none"`."""),

    # E
    q("find-returns-falsy-item", '''
        const f = [0, 1].find((x) => x === 0);
        console.log(f, f || "none", f ?? "none");
    ''', "0 none 0", ["undefined none none", "0 0 0", "0 none none"],
      "find can legitimately return a falsy item; || treats it as missing, ?? does not",
      """The match is the number 0, so `find` returns 0, not undefined. `0 || "none"` treats it as empty and
      gives "none", while `??` only replaces null and undefined."""),

    # E
    q("indexof-zero-is-falsy", '''
        console.log(["a", "b"].indexOf("a") ? "found" : "missing",
          ["a", "b"].indexOf("z") ? "found" : "missing");
    ''', "missing found", ["found missing", "found found", "missing missing"],
      "indexOf returns 0 for the first item and -1 for none; -1 is truthy, 0 is not",
      """The first item is at index 0, which is falsy, so the first test says "missing". An absent item gives
      -1, which is truthy. Compare with `!== -1` or use `includes`."""),

    # ── Arrays, strings, JSON, dates, numbers ──────────────────────────────
    # E
    q("rest-destructure-copies", '''
        const a = [1, 2, 3];
        const [x, ...y] = a;
        y.push(4);
        console.log(a.length, y.length, x);
    ''', "3 3 1", ["4 4 1", "3 2 1", "4 3 1"],
      "A rest element is a new array, not a view of the original",
      """`...y` collects the leftover items into a fresh array `[2, 3]`. Pushing to it does not touch `a`,
      and `y` ends up with three items."""),

    # E
    q("array-to-string-forms", '''
        const r = [[null] + "", [undefined, null].join("-"), [[], []] + "",
          String(Array(3)), [1, [2, [3]]] + ""];
        console.log(JSON.stringify(r));
    ''', '["","-",",",",,","1,2,3"]',
      ['["null","undefined-null",",",",,","1,2,3"]', '["","-",",",",,","1,[2,[3]]"]',
       '["","undefined-null","","","1,2,3"]'],
      "Joining turns null, undefined and holes into empty text, and nested arrays join too",
      """`join` and `String` on an array treat `null`, `undefined` and empty slots as empty strings, so
      `[null]` is `""` and `Array(3)` is two commas. Nested arrays are converted the same way, which flattens
      them completely."""),

    # E
    q("function-name-inference", '''
        const f = () => {};
        const o = { g() {}, h: () => {}, i: function () {} };
        console.log(f.name, o.g.name, o.h.name, o.i.name, (() => {}).name === "");
    ''', "f g h i true",
      ["f g h i false", "f g anonymous anonymous true", "f g h function true"],
      "An anonymous function takes the name of the variable or key it is assigned to",
      """Engines infer a name from the binding or property when an anonymous function is assigned directly.
      A function that is never assigned, like the last one, has the empty name `""`."""),

    # E
    q("sort-arrays-as-text", '''
        const rows = [[10, "a"], [9, "b"], [2, "c"]];
        console.log(rows.sort().map((p) => p[0]).join());
    ''', "10,2,9", ["2,9,10", "10,9,2", "9,2,10"],
      "The default sort turns each item into text, and an array becomes '10,a'",
      """Without a comparator `sort` compares strings, so `[10, "a"]` becomes `"10,a"`. Text order puts `10,a`
      before `2,c` before `9,b`. Numbers inside pairs are not compared as numbers."""),

    # E
    q("sort-uppercase-first", '''
        const sorted = (s) => [...s].sort().join("");
        console.log(sorted("baCB"), sorted("zée"));
    ''', "BCab ezé", ["aBbC eéz", "BCab eéz", "abBC ezé"],
      "The default sort compares UTF-16 code units, so capitals come first and accents last",
      """Every capital letter has a smaller code than every lowercase letter, so `B` and `C` sort before
      `a`. The accented `é` is far above `z`, so it goes last. Use `localeCompare` for human ordering."""),

    # E
    q("fill-start-end", '''
        const f = (a, ...args) => a.fill(...args);
        console.log(f([1, 2, 3, 4], 9, 1, 3), f([1, 2, 3, 4], 0, -1), f([1, 2, 3]));
    ''', "[ 1, 9, 9, 4 ] [ 1, 2, 3, 0 ] [ undefined, undefined, undefined ]",
      ["[ 1, 9, 9, 9 ] [ 1, 2, 3, 0 ] [ undefined, undefined, undefined ]",
       "[ 1, 9, 9, 4 ] [ 0, 0, 0, 0 ] [ undefined, undefined, undefined ]",
       "[ 1, 9, 9, 4 ] [ 1, 2, 3, 0 ] [ 1, 2, 3 ]"],
      "fill(value, start, end) stops before end, counts negatives from the back, and defaults to undefined",
      """The end index is not included, so `fill(9, 1, 3)` changes indexes 1 and 2. A negative start of -1
      means the last position only. With no value at all it fills with `undefined`."""),

    # E
    q("string-access-out-of-range", '''
        const s = "abc";
        console.log([s.charAt(5), s[5], s.at(5), s.substring(5), s.charCodeAt(5)]);
    ''', "[ '', undefined, undefined, '', NaN ]",
      ["[ '', '', '', '', NaN ]", "[ undefined, undefined, undefined, '', NaN ]",
       "[ '', undefined, undefined, '', 0 ]"],
      "Past the end, charAt gives '' and bracket access gives undefined",
      """Each access method has its own idea of "nothing": `charAt` and `substring` give an empty string,
      `[]` and `at` give `undefined`, and `charCodeAt` gives NaN because there is no code."""),

    # E
    q("global-twins", '''
        console.log(Number.parseFloat === parseFloat, Number.isNaN === isNaN,
          Number.parseInt === parseInt, Number.isFinite === isFinite);
    ''', "true false true false", ["true true true true", "false false false false", "true false false false"],
      "parseInt and parseFloat are the very same functions, isNaN and isFinite are not",
      """`Number.parseInt` and `Number.parseFloat` were added as aliases of the globals. But `Number.isNaN` and
      `Number.isFinite` were made stricter, without coercing their argument, so they are different functions."""),

    # M
    q("copywithin-forms", '''
        const a = () => [1, 2, 3, 4, 5];
        console.log(a().copyWithin(0, 3).join(""), a().copyWithin(1, 0, 2).join(""),
          a().copyWithin(-2, 0).join(""));
    ''', "45345 11245 12312",
      ["45345 11145 12312", "34545 11245 12312", "45345 11245 34545"],
      "copyWithin(target, start, end) copies a block inside the array without changing its length",
      """`copyWithin(0, 3)` copies the items from index 3 to the end over the front, so the array stays five
      long. The `end` is not included, so `(1, 0, 2)` copies two items, 1 and 2, to index 1. A negative
      target counts from the end."""),

    # M
    q("splice-negative-insert", '''
        const a = [1, 2, 3, 4];
        const removed = a.splice(-2, 1, "x", "y");
        console.log(a, removed);
    ''', "[ 1, 2, 'x', 'y', 4 ] [ 3 ]",
      ["[ 1, 2, 'x', 'y', 3, 4 ] []", "[ 1, 2, 3, 'x', 'y' ] [ 4 ]", "[ 1, 'x', 'y', 3, 4 ] [ 2 ]"],
      "A negative start counts from the end; the second argument is how many to remove",
      """`-2` points at the item 3. One item is removed from there and replaced by the two new ones, so the
      array grows by one. `splice` returns the removed items, here `[3]`."""),

    # H
    q("surrogate-pair-lengths", '''
        const s = "a😀b";
        console.log(s.length, [...s].length, s.split("").length,
          s.codePointAt(1), s.codePointAt(2));
    ''', "4 3 4 128512 56832",
      ["3 3 3 128512 98", "4 4 4 128512 56832", "4 3 4 55357 56832"],
      "An emoji is two UTF-16 units: length and split see two, spread and codePointAt(1) see one",
      """`length` and `split("")` count UTF-16 code units, so the emoji counts twice. Spread iterates by code
      point, so it counts once. `codePointAt(2)` lands on the second half of the pair and returns just that
      half, 56832."""),

    # H
    q("getter-copied-once", '''
        let n = 0;
        const o = { get v() { return ++n; } };
        const c = { ...o };
        console.log(c.v, c.v, o.v, o.v, Object.assign({}, o).v);
    ''', "1 1 2 3 4", ["1 2 3 4 5", "1 1 1 1 1", "1 1 2 3 3"],
      "Spread and Object.assign call the getter once and copy its value as plain data",
      """Making `c` reads `o.v` one time (n becomes 1) and stores the number, so `c.v` stays 1. The original
      getter still runs on every access, giving 2 and 3, and `Object.assign` calls it once more for 4."""),

    # H
    q("json-reviver-order", '''
        const keys = [];
        JSON.parse('{"a":1,"b":{"c":2},"d":[3]}', (k, v) => {
          keys.push(k);
          return v;
        });
        console.log(keys.join());
    ''', "a,c,b,0,d,", ["a,b,c,d,0,", ",a,b,c,d,0", "a,c,b,0,d"],
      "The reviver sees children before their parent, and the root comes last with key ''",
      """JSON.parse revives from the inside out: the inner `c` before `b`, the array item `0` before `d`.
      The whole result is revived last under the empty-string key, which leaves the trailing comma."""),

    # M
    q("json-special-numbers", '''
        const j = JSON.stringify;
        console.log(j([-0, NaN, undefined]), Object.is(JSON.parse("-0"), -0),
          j({ a: undefined, b: -0 }));
    ''', '[0,null,null] true {"b":0}',
      ['[0,null,null] false {"b":0}', '[-0,null,null] true {"b":-0}', '[0,null,null] true {"a":null,"b":0}'],
      "stringify writes -0 as 0, NaN and undefined-in-arrays as null, and drops undefined properties",
      """JSON has no negative zero or NaN, so `stringify` writes 0 and `null`. An `undefined` property is
      skipped, but in an array it becomes `null` to keep the positions. `JSON.parse("-0")`, however,
      does give back a real -0."""),

    # M
    q("date-utc-month-end", '''
        const last = (y, m) => new Date(Date.UTC(y, m + 1, 0)).getUTCDate();
        console.log(last(2024, 1), last(2023, 1), last(2024, 11),
          new Date(Date.UTC(2024, 0, 1) - 1).toISOString());
    ''', "29 28 31 2023-12-31T23:59:59.999Z",
      ["28 28 31 2023-12-31T23:59:59.999Z", "29 28 30 2023-12-31T23:59:59.999Z",
       "29 28 31 2024-01-01T00:00:00.000Z"],
      "Day 0 of the next month is the last day of this one; Date arithmetic is in milliseconds",
      """Months are zero-based, so month 1 is February and `Date.UTC(y, 2, 0)` is day 0 of March, which rolls
      back to the last day of February: 29 in 2024. Subtracting 1 ms from January 1st lands on the final
      millisecond of the previous year."""),

    # H
    q("sticky-lastindex", '''
        const re = /a/y;
        re.lastIndex = 1;
        console.log(re.test("ba"), re.lastIndex, re.test("ba"), re.lastIndex);
    ''', "true 2 false 0", ["true 2 true 2", "false 0 false 0", "true 2 false 2"],
      "A sticky regex only matches exactly at lastIndex, and a failure resets it to 0",
      """The `y` flag does not search ahead. The first test starts at index 1, finds `a` there and moves
      `lastIndex` to 2. The second test must match at index 2, which is the end, so it fails and resets
      `lastIndex` to 0."""),

    # M
    q("replace-special-patterns", '''
        console.log("abc".replace("b", "[$&$&]"), "abc".replace("b", "$$"),
          "abc".replace("b", "[$`|$']"));
    ''', "a[bb]c a$c a[a|c]c",
      ["a[$&$&]c a$$c a[$`|$']c", "a[bb]c a$$c a[a|c]c", "a[bb]c a$c a[ac|c]c"],
      "The replacement string has codes: $& is the match, $$ a dollar, $` and $' the text around it",
      """Even a plain string replacement is scanned for `$` patterns. `$&` inserts the matched text, `$$`
      is one literal dollar sign, and the backtick and quote forms insert what comes before and after the
      match. Use a function to avoid all of them."""),

    # M
    q("string-raw-length", r'''
        console.log(String.raw`a\nb${1 + 1}`.length, `a\nb`.length);
    ''', "5 3", ["4 3", "5 5", "3 3"],
      "String.raw keeps backslash sequences as typed, but still fills ${} placeholders",
      """The raw text `a\\nb` is four characters: `a`, a backslash, `n` and `b`, plus the `2` from the
      placeholder, so 5. In an ordinary template `\\n` is one newline character, so the length is 3."""),

    # M
    q("number-underscore-parse", '''
        console.log([Number("1_000"), parseInt("1_000"), 1_000,
          Number("0b11"), Number("12px"), parseFloat("12px")]);
    ''', "[ NaN, 1, 1000, 3, NaN, 12 ]",
      ["[ 1000, 1000, 1000, 3, NaN, 12 ]", "[ NaN, 1000, 1000, 3, 12, 12 ]",
       "[ NaN, 1, 1000, NaN, NaN, 12 ]"],
      "Underscores work in literals but not when parsing text",
      """The numeric separator `_` is allowed in source code only. `Number("1_000")` is NaN, and `parseInt` stops
      reading at the underscore and returns 1."""),

    # M
    q("bigint-arithmetic", '''
        console.log(5n / 2n, -5n / 2n, 7n % -3n, 1n == 1, 1n === 1, 0n ? "t" : "f");
    ''', "2n -2n 1n true false f",
      ["3n -3n 1n true true f", "2n -3n -2n true false f", "2n -2n 1n false false t"],
      "BigInt division truncates toward zero, == compares by value, === compares the type",
      """BigInt `/` drops the fraction toward zero, so -5n / 2n is -2n, and `%` takes the sign of the left
      side. Loose equality converts, so `1n == 1`, but strict equality sees two types. `0n` is falsy."""),

    # ── Functions, classes, generators, the event loop ─────────────────────
    # M
    q("new-target-forms", '''
        function F() { return new.target === undefined ? "call" : "new"; }
        class A { constructor() { this.t = new.target.name; } }
        class B extends A {}
        console.log(F(), new F() instanceof F, new B().t);
    ''', "call true B", ["call false B", "new true A", "call true A"],
      "new.target is the class that new was called on, and a primitive return from a constructor is ignored",
      """Called plainly, `F` sees `new.target` as undefined. With `new`, the function's string return value is
      thrown away and the new object is returned, so `instanceof F` holds. In a base class constructor,
      `new.target` is still the derived class, `B`."""),

    # M
    q("class-init-order", '''
        const log = [];
        class A {
          a = log.push("A.field");
          constructor() { log.push("A.ctor"); }
        }
        class B extends A {
          b = log.push("B.field");
          constructor() { super(); log.push("B.ctor"); }
        }
        new B();
        console.log(log.join(" "));
    ''', "A.field A.ctor B.field B.ctor",
      ["A.ctor A.field B.ctor B.field", "A.field B.field A.ctor B.ctor", "A.field A.ctor B.ctor B.field"],
      "Base fields come first; derived fields are set when super() returns",
      """A base class sets its fields, then runs its constructor body. A derived class cannot set its own
      fields until `super()` has finished, so `B.field` is initialized right after `A.ctor`, before the rest
      of the `B` constructor."""),

    # M
    q("static-block-order", '''
        const log = [];
        class A {
          static x = log.push("x");
          static { log.push("block"); }
          static y = log.push("y");
          z = log.push("instance");
        }
        log.push("defined");
        new A();
        console.log(log.join(" "));
    ''', "x block y defined instance",
      ["defined x block y instance", "x y block defined instance", "instance x block y defined"],
      "Static fields and static blocks run in order as the class is defined",
      """When the class declaration is evaluated, its static fields and static blocks run top to bottom, so
      the log gets `x`, `block`, `y` before anything after the class. Instance fields run only when `new`
      creates an object."""),

    # M
    q("class-expression-name", '''
        const A = class B {
          who() { return typeof B; }
        };
        console.log(A.name, typeof B, new A().who());
    ''', "B undefined function", ["A undefined function", "B function function", "A function undefined"],
      "A named class expression's name exists only inside the class",
      """The class is called `B` (that is its `name`), but the binding `B` is visible only in the class body.
      Outside, `B` does not exist, and only the variable `A` refers to the class."""),

    # H
    q("getter-only-override-loses-setter", '''
        class A {
          get v() { return 1; }
          set v(x) { this._v = x; }
        }
        class B extends A {
          get v() { return 2; }
        }
        const b = new B();
        b.v = 5;
        console.log(b.v, b._v);
    ''', "2 undefined", ["5 5", "2 5", "5 undefined"],
      "Overriding only the getter in a subclass removes the setter",
      """`B.prototype.v` is a new accessor with a getter and no setter, which hides the one in `A`. The
      assignment at the end is silently ignored (it would throw in strict mode), so `_v` is never set."""),

    # H
    q("super-field-undefined", '''
        class A {
          x = 1;
          m() { return "A.m"; }
        }
        class B extends A {
          get() { return [super.x, this.x, super.m()]; }
        }
        console.log(new B().get());
    ''', "[ undefined, 1, 'A.m' ]",
      ["[ 1, 1, 'A.m' ]", "[ undefined, undefined, 'A.m' ]", "[ 1, 1, undefined ]"],
      "super.name looks on the parent's prototype, and fields live on the instance, not there",
      """`super.x` reads from `A.prototype`, which has the method `m` but not the field `x`: fields are
      created on each instance. So `super.x` is undefined while `this.x` is 1, and `super.m()` works."""),

    # H
    q("arguments-aliasing", '''
        function f(a) { arguments[0] = 9; return a; }
        function g(a) { "use strict"; arguments[0] = 9; return a; }
        function h(a = 0) { arguments[0] = 9; return a; }
        console.log(f(1), g(1), h(1));
    ''', "9 1 1", ["1 1 1", "9 9 9", "9 9 1"],
      "In sloppy functions with simple parameters, arguments and the parameters are linked",
      """In `f` writing `arguments[0]` also changes `a`, a leftover of old JavaScript. Strict mode removes
      the link, and so does any function with default values, rest or destructuring in its parameters."""),

    # H
    q("var-redeclare-param", '''
        function f(a) { var a; return a; }
        function g(a) { var a = 2; return a; }
        function h(a) { function a() {} return typeof a; }
        console.log(f(5), g(5), h(5));
    ''', "5 2 function", ["undefined 2 number", "5 2 number", "undefined 2 function"],
      "A bare var redeclaration keeps the parameter's value, but a function declaration replaces it",
      """`var a;` with no initializer does nothing to an existing parameter, so `f` still sees 5. `var a = 2`
      assigns. A function declaration named `a` is hoisted and overwrites the parameter, so `typeof a`
      is "function"."""),

    # M
    q("default-param-tdz", '''
        function f(a = b, b = 1) {
          return a;
        }
        console.log(f());
    ''', "ReferenceError", ["1", "undefined", "TypeError"],
      "A default can only use parameters to its left; the later one is still in its dead zone",
      """Parameters are initialized in order like `let`. While `a` is being given its default, `b` exists
      but is not initialized yet, so reading it throws ReferenceError instead of giving undefined.""",
      raises=True),

    # E
    q("class-needs-new", '''
        class A {}
        const a = A();
        console.log(a);
    ''', "TypeError", ["undefined", "A {}", "ReferenceError"],
      "A class constructor cannot be called like a plain function",
      """Unlike old-style constructor functions, a class throws `TypeError: Class constructor A cannot be
      invoked without 'new'` when it is called without `new`.""",
      raises=True),

    # H
    q("generator-return-finally", '''
        function* g() {
          try { yield 1; yield 2; } finally { yield "cleanup"; }
        }
        const it = g();
        it.next();
        console.log(it.return("r"), it.next(), it.next());
    ''', "{ value: 'cleanup', done: false } { value: 'r', done: true } { value: undefined, done: true }",
      ["{ value: 'r', done: true } { value: undefined, done: true } { value: undefined, done: true }",
       "{ value: 'cleanup', done: false } { value: 2, done: false } { value: 'r', done: true }",
       "{ value: 'cleanup', done: false } { value: undefined, done: true } { value: undefined, done: true }"],
      "return() runs the finally block, which can even yield, and the return value is delivered afterwards",
      """`it.return("r")` resumes the generator as if a `return` happened at the paused `yield`. The `finally`
      block still runs, so its `yield "cleanup"` answers the call. The next `next()` then finishes with the
      saved value `"r"`."""),

    # M
    q("symbol-basics", '''
        const s = Symbol("a");
        console.log(s === Symbol("a"), Symbol.for("a") === Symbol.for("a"),
          String(s), s.description, Symbol.keyFor(s));
    ''', "false true Symbol(a) a undefined",
      ["true true Symbol(a) a a", "false true a a undefined", "false false Symbol(a) Symbol(a) undefined"],
      "Every Symbol() is unique; Symbol.for shares one per key, and only those have a keyFor",
      """The text in `Symbol("a")` is only a description, so two of them are different. `Symbol.for` looks up
      a global registry. `keyFor` answers for registry symbols only, so for an ordinary symbol it is
      undefined."""),

    # H
    q("to-primitive-hints", '''
        const o = {
          [Symbol.toPrimitive](hint) {
            return hint === "number" ? 7 : hint === "string" ? "s" : "d";
          },
        };
        console.log(+o, `${o}`, o + "", o * 2, o == "d", [o] + "");
    ''', "7 s d 14 true s",
      ["7 s s 14 true s", "7 d d 14 false d", "NaN s d NaN true s"],
      "Symbol.toPrimitive is told the hint: number, string, or default (for + and ==)",
      """Unary `+` and `*` ask for a number, a template literal asks for a string, and `+` with a string and
      `==` use the default hint. An array joins its items as strings, so `[o] + ""` converts `o` with the
      string hint."""),

    # M
    q("queue-microtask-order", '''
        const log = [];
        queueMicrotask(() => log.push("q"));
        Promise.resolve().then(() => log.push("p"));
        process.nextTick(() => log.push("t"));
        log.push("sync");
        setTimeout(() => console.log(log.join(" ")));
    ''', "sync t q p", ["sync q p t", "t sync q p", "sync p q t"],
      "nextTick runs before the promise queue; queueMicrotask shares the queue, in call order",
      """The main script finishes first. Node then empties the `nextTick` queue, and after that the microtask
      queue, which holds the `queueMicrotask` callback and the promise reaction in the order they were added."""),

    # M
    q("empty-promise-combinators", '''
        const log = [];
        Promise.all([]).then((v) => log.push("all " + v.length));
        Promise.allSettled([]).then((v) => log.push("settled " + v.length));
        Promise.any([]).catch((e) => log.push(e.name + " " + e.errors.length));
        Promise.race([]).then(() => log.push("race"));
        setTimeout(() => console.log(log.join(" | ")), 5);
    ''', "all 0 | settled 0 | AggregateError 0",
      ["all 0 | settled 0 | race | AggregateError 0", "all 0 | settled 0", "all 0 | settled 0 | TypeError 0"],
      "With nothing to wait for, all and allSettled resolve, any rejects, and race never settles",
      """`Promise.all([])` and `allSettled([])` resolve at once with an empty array. `Promise.any([])` has no
      winner, so it rejects with an AggregateError, and `Promise.race([])` stays pending forever."""),

    # M
    q("then-ignores-non-functions", '''
        Promise.resolve(1)
          .then(2)
          .then((v) => v + 1)
          .then(Promise.resolve(10))
          .then((v) => console.log(v));
    ''', "2", ["10", "3", "1"],
      "A non-function passed to then() is ignored, and the value passes straight through",
      """`.then(2)` has no handler to run, so the value 1 goes on unchanged and `+ 1` makes 2. Passing a
      promise to `.then` is the same mistake: it is not a function, so it is ignored and the 2 is kept."""),

    # M
    q("optional-chain-parenthesis", '''
        const o = {};
        console.log((o.a?.b).c);
    ''', "TypeError", ["undefined", "null", "ReferenceError"],
      "Parentheses end the optional chain's short-circuit",
      """Without brackets, `o.a?.b.c` stops at `o.a` and gives undefined. Inside parentheses, `(o.a?.b)` is
      finished first and is undefined, and the outer `.c` then reads a property of undefined.""",
      raises=True),

    # M
    q("optional-call-not-a-function", '''
        const o = { f: 5 };
        console.log(o.f?.());
    ''', "TypeError", ["undefined", "5", "ReferenceError"],
      "?.() only guards null and undefined, not other values that are not functions",
      """The optional call skips the call when `o.f` is `null` or `undefined`. Here `o.f` is the number 5,
      which exists but is not callable, so the call still throws a TypeError.""",
      raises=True),

    # M
    q("json-circular", '''
        const a = { name: "a" };
        a.self = a;
        console.log(JSON.stringify(a));
    ''', "TypeError", ['{"name":"a"}', "RangeError", "undefined"],
      "JSON.stringify throws on a reference cycle",
      """The object contains itself, so the output would be infinite. `stringify` detects the cycle and
      throws `TypeError: Converting circular structure to JSON`.""",
      raises=True),

    # M
    q("template-literal-symbol", '''
        console.log(`${Symbol("a")}`);
    ''', "TypeError", ["Symbol(a)", "a", "undefined"],
      "Symbols are not converted to text implicitly, only by String() or .toString()",
      """A template literal converts with the abstract ToString, which refuses a Symbol and throws
      `Cannot convert a Symbol value to a string`. `String(sym)` is allowed, and gives `Symbol(a)`.""",
      raises=True),

    # ── Objects, scope, iterators, the odd corners ─────────────────────────
    # H
    q("proto-literal-vs-computed", '''
        const proto = { a: 1 };
        const x = { __proto__: proto };
        const y = { ["__proto__"]: proto };
        console.log(x.a, Object.keys(x).length, y.a, Object.keys(y).length);
    ''', "1 0 undefined 1",
      ["1 1 1 1", "1 0 1 1", "undefined 0 undefined 1"],
      "__proto__: in a literal sets the prototype; a computed key makes an ordinary property",
      """The plain `__proto__: value` form is special syntax that sets the prototype, so `x` inherits `a` and
      has no own keys. The computed form `["__proto__"]` just creates a normal own property with that name,
      so `y` inherits nothing."""),

    # H
    q("template-site-cached", '''
        const t = (s) => s;
        const site = () => t`x`;
        console.log(site() === site(), t`x` === t`x`, Object.isFrozen(site()),
          site().raw[0]);
    ''', "true false true x",
      ["false false false x", "true true true x", "true false false x"],
      "A tag call gets one frozen strings array per place in the source, reused on every run",
      """The strings array is created once for each tagged template expression and cached, so calling the
      same line twice gives the identical object. Two separate tagged templates are different sites, so they
      differ, and the array is frozen."""),

    # H
    q("math-max-coercion", '''
        console.log(Math.max([]), Math.max([5]), Math.max([1, 2]),
          Math.max(null, -1), Math.max(undefined, 1));
    ''', "0 5 NaN 0 NaN", ["-Infinity 5 2 -1 1", "0 5 2 0 1", "-Infinity 5 NaN -1 NaN"],
      "Math.max converts each argument to a number: [] is 0, [1, 2] is NaN, null is 0",
      """An empty array becomes the empty string and then 0. `[5]` becomes "5", but `[1, 2]` becomes "1,2",
      which is NaN. `null` is 0, so it beats -1, and `undefined` is NaN, which poisons the result."""),

    # H
    q("own-keys-kinds", '''
        const s = Symbol("s");
        const o = { b: 1, [s]: 2, 1: 3 };
        Object.defineProperty(o, "hidden", { value: 4 });
        console.log(Object.keys(o).join(), Reflect.ownKeys(o).length,
          Object.getOwnPropertyNames(o).join());
    ''', "1,b 4 1,b,hidden",
      ["1,b 3 1,b,hidden", "b,1 4 b,1,hidden", "1,b,hidden 4 1,b,hidden"],
      "keys() lists only enumerable string keys; ownKeys also has symbols and hidden ones",
      """`Object.keys` skips symbols and non-enumerable properties, and puts integer-like keys first.
      `getOwnPropertyNames` adds the hidden string key, and `Reflect.ownKeys` adds the symbol as well, which
      makes four."""),

    # H
    q("getter-throws-selectively", '''
        const o = { get x() { throw new Error("boom"); } };
        const t = (f) => { try { return f(); } catch (e) { return e.message; } };
        console.log(t(() => "x" in o), t(() => Object.keys(o).length),
          t(() => ({ ...o })));
    ''', "true 1 boom", ["boom boom boom", "true 1 {}", "true boom boom"],
      "Only operations that read the value run the getter; in and keys() just look at the names",
      """The `in` operator and `Object.keys` check that a property exists without reading it, so the getter
      never runs. Spreading the object has to read every value, so it triggers the getter and throws."""),

    # H
    q("epsilon-scale", '''
        const a = 0.1 + 0.2;
        const b = 1e6 + 0.1 + 0.2;
        console.log(Math.abs(a - 0.3) < Number.EPSILON,
          Math.abs(b - 1000000.3) < Number.EPSILON);
    ''', "true false", ["true true", "false false", "false true"],
      "Number.EPSILON only fits numbers near 1; larger numbers have larger rounding errors",
      """EPSILON is the gap between 1 and the next float. The error for 0.1 + 0.2 is about 5.5e-17, below it.
      Near a million the floats are spaced about 1e-10 apart, so the same kind of error is far bigger than
      EPSILON."""),

    # H
    q("catch-var-assignment", '''
        var e = "outer";
        try {
          throw "inner";
        } catch (e) {
          var e = "changed";
        }
        console.log(e);
    ''', "outer", ["changed", "inner", "undefined"],
      "A var with the catch parameter's name assigns to the parameter, not to the outer variable",
      """The `var e` is hoisted to the function, but the assignment `= "changed"` is resolved by scope, and
      the nearest `e` is the catch parameter. So the outer `e` is never touched and stays "outer"."""),

    # H
    q("global-regex-lastindex-replace", '''
        const re = /a/g;
        re.lastIndex = 2;
        const r = "aaa".replace(re, "b");
        console.log(r, re.lastIndex, re.test("aaa"), re.lastIndex);
    ''', "bbb 0 true 1", ["bba 0 true 1", "bbb 2 false 0", "bbb 0 true 3"],
      "replace with a global regex ignores and resets lastIndex; test() depends on it",
      """`replace` starts from the beginning and leaves `lastIndex` at 0. The following `test` then matches
      from index 0 and sets `lastIndex` to 1. A global regex used with `test` or `exec` carries that state
      between calls."""),

    # H
    q("switch-default-in-middle", '''
        function f(x) {
          const out = [];
          switch (x) {
            case 1: out.push(1);
            default: out.push("d");
            case 2: out.push(2); break;
            case 3: out.push(3);
          }
          return out.join("");
        }
        console.log(f(1), f(2), f(3), f(9));
    ''', "1d2 2 3 d2", ["1 2 3 d", "1d2 2 3 d", "1d2 2 d2 d2"],
      "default can sit anywhere; it is used only when no case matches, and then it falls through",
      """Matching tries every `case` first, wherever `default` is written. `f(9)` matches none, so execution
      starts at `default` and falls into `case 2`. `f(3)` matches `case 3` at the end and stops there."""),

    # H
    q("has-instance-hook", '''
        class Even {
          static [Symbol.hasInstance](n) { return n % 2 === 0; }
        }
        console.log(2 instanceof Even, 3 instanceof Even, "4" instanceof Even);
    ''', "true false true", ["true false false", "true true true", "false false false"],
      "instanceof can be redefined by a static Symbol.hasInstance method",
      """`x instanceof C` first calls `C[Symbol.hasInstance](x)` and uses its result, so any logic works,
      including accepting primitives. The string `"4"` is converted by `%`, so it counts as even."""),

    # M
    q("proxy-set-compound", '''
        const p = new Proxy({}, { set(t, k, v) { t[k] = v * 2; return true; } });
        p.a = 1;
        p.a += 1;
        console.log(p.a, Object.keys(p));
    ''', "6 [ 'a' ]", ["3 [ 'a' ]", "4 [ 'a' ]", "2 [ 'a' ]"],
      "p.a += 1 reads the stored value and then goes through the set trap again",
      """The first assignment stores 1 * 2 = 2. Then `p.a += 1` reads 2, adds 1 and assigns 3, which the trap
      doubles again, so 6 is stored."""),

    # M
    q("set-grows-while-iterating", '''
        const s = new Set([1, 2]);
        const seen = [];
        for (const x of s) {
          seen.push(x);
          if (x < 3) s.add(x + 2);
        }
        console.log(seen.join(), [...s].join());
    ''', "1,2,3,4 1,2,3,4", ["1,2 1,2,3,4", "1,2,3 1,2,3,4", "1,2,3,4 1,2"],
      "Items added to a Set during iteration are visited too",
      """A Set's iteration follows insertion order and notices later additions, so the 3 and 4 that were added
      are visited before the loop ends. Arrays do the same with `push`, which is why infinite loops are easy
      to create."""),

    # M
    q("matchall-needs-g", '''
        console.log([..."a1b2".matchAll(/[0-9]/)]);
    ''', "TypeError", ["[ '1', '2' ]", "[]", "RangeError"],
      "matchAll refuses a regex without the g flag",
      """`String.prototype.matchAll` is meant to return every match, so a non-global regex is a mistake and
      throws `TypeError: String.prototype.matchAll called with a non-global RegExp argument`.""",
      raises=True),

    # M
    q("class-getter-not-serialized", '''
        class C { x = 1; get y() { return 2; } }
        const c = new C();
        console.log(JSON.stringify(c), Object.keys(c).length, { ...c }.y, c.y);
    ''', '{"x":1} 1 undefined 2', ['{"x":1,"y":2} 2 2 2', '{"x":1} 1 2 2', '{"x":1,"y":2} 1 undefined 2'],
      "Class getters live on the prototype, so stringify, keys() and spread do not see them",
      """The field `x` is an own property of the instance. The getter `y` belongs to `C.prototype`, which JSON,
      `Object.keys` and spread all ignore, although `c.y` itself still works."""),

    # M
    q("finally-throw-replaces", '''
        try {
          try { throw new Error("a"); } finally { throw new Error("b"); }
        } catch (e) {
          console.log(e.message);
        }
    ''', "b", ["a", "Error: b", "b a"],
      "A throw inside finally replaces the error that was already in flight",
      """The first error is waiting to propagate when the `finally` block runs. Throwing again there discards
      it, so the outer `catch` only ever sees the second error."""),

    # M
    q("for-of-break-closes-iterator", '''
        const log = [];
        const it = {
          [Symbol.iterator]() {
            let i = 0;
            return {
              next: () => ({ value: i++, done: false }),
              return() { log.push("closed"); return {}; },
            };
          },
        };
        for (const x of it) if (x === 2) break;
        const [a, b] = it;
        console.log(log.join());
    ''', "closed,closed", ["closed", "never", "closed,closed,closed"],
      "Leaving early calls the iterator's return(), also after destructuring",
      """When a `for...of` loop is exited with `break`, the iterator's `return()` method is called to let it
      clean up. Array destructuring that takes fewer items than the iterator could give does the same."""),

    # M
    q("async-map-promises", '''
        console.log([1, 2].map(async (x) => x * 2));
    ''', "[ Promise { 2 }, Promise { 4 } ]",
      ["[ 2, 4 ]", "[ Promise { <pending> }, Promise { <pending> } ]", "[ Promise { 1 }, Promise { 2 } ]"],
      "An async callback makes map return promises, not values",
      """Each call of the `async` arrow returns a promise. Since it has no `await`, those promises are already
      resolved, and Node shows them with their values. Use `Promise.all` to get the numbers."""),

    # M
    q("date-invalid-iso", '''
        const d = new Date("not a date");
        console.log(d.toISOString());
    ''', "RangeError", ["Invalid Date", "NaN", "null"],
      "An invalid Date prints as 'Invalid Date' but toISOString() throws",
      """`new Date("not a date")` does not throw. It is a Date whose time is NaN, and most getters return NaN.
      Only `toISOString()` refuses it with `RangeError: Invalid time value`.""",
      raises=True),

    # M
    q("typed-array-wrapping", '''
        const u = new Uint8Array(2);
        u[0] = 257;
        u[1] = -1;
        console.log(u.join(), Uint8ClampedArray.of(300, -5).join());
    ''', "1,255 255,0", ["257,-1 255,0", "1,255 300,-5", "0,0 255,0"],
      "Uint8Array wraps around modulo 256, Uint8ClampedArray clamps to 0-255",
      """Typed arrays convert what you store to their element type. For `Uint8Array` the value wraps, so 257
      becomes 1 and -1 becomes 255. The clamped variant limits it to the range, so 300 gives 255 and -5 gives 0."""),

    # M
    q("structured-clone-types", '''
        class P { get d() { return 1; } }
        const copy = structuredClone(new Map([[1, 2]]));
        const plain = structuredClone(new P());
        const date = structuredClone(new Date(0));
        console.log(plain instanceof P, date instanceof Date, copy.get(1),
          "d" in structuredClone({ d: undefined }));
    ''', "false true 2 true", ["true true 2 true", "false false 2 false", "false true 2 false"],
      "structuredClone keeps Dates, Maps and undefined values, but not class prototypes",
      """It clones built-in types such as Date and Map properly and keeps keys whose value is `undefined`
      (unlike JSON). Instances of your own classes come back as plain objects, so `instanceof P` is false."""),
)
