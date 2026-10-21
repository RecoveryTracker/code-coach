"""Gotchas, Lua (second deck): run by lua 5.4; portability notes are in langs.py (the `lua` entry).

`print` with several arguments puts a TAB between them, so each card builds one string with `..`, `tostring`
or `table.concat`. Nothing prints inf or nan (the spelling depends on the C library), nothing relies on the
length of a table with holes, and error messages are never printed (they carry the script path).
"""

from __future__ import annotations

from .items import Item, make

q = make("lua")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics a beginner can get, with a real trap ──────────
    q("strings-and-numbers-mix", r'''
        local r = { "10" + 5, "3" * "4", 10 .. 5, "0x10" + 0 }
        print(table.concat(r, "|"))
    ''', "15|12|105|16", ["105|34|15|0", "15|12|15|16", "15.0|12.0|105|16"],
      "Arithmetic turns numeric strings into numbers; .. turns numbers into strings",
      """In `"10" + 5` the string becomes the integer 10, so the sum is the integer 15. The `..` operator
      converts numbers to text and joins them, giving "105". Hex strings convert as well."""),

    q("floor-division-and-modulo", r'''
        local parts = { -7 // 2, -7 % 3, 3.0 // 2, 7.5 // 2, 2 ^ 2, 1e2,
                        7 // 2 * 2.0 }
        print(table.concat(parts, " "))
    ''', "-4 2 1.0 3.0 4.0 100.0 6.0", ["-3 -1 1 3 4 100 6", "-4 2 1 3 4.0 100.0 6.0", "-3 2 1.0 3.0 4.0 100 6.0"],
      "// floors, % takes the divisor's sign, and any float operand makes the result a float",
      """`-7 // 2` rounds down to -4 and the modulo -7 % 3 is 2. Once one operand is a float, the result is a
      float too and prints with a `.0`: `3.0 // 2` is 1.0. The exponent operator and exponent notation always
      produce floats."""),

    q("math-type-and-conversion", r'''
        local t = { math.type(1), math.type(1.0), math.type("1"), math.type(2 ^ 31),
                    math.type(1 // 1), math.type(1 / 1), math.type(3 | 0) }
        for i = 1, #t do t[i] = tostring(t[i]) end
        print(table.concat(t, " "))
    ''', "integer float nil float integer float integer",
      ["integer integer nil integer integer integer integer", "integer float float float integer float integer",
       "integer float nil integer float float integer"],
      "^ and / always give floats; math.type of a string is nil because it is not a number",
      """Lua 5.4 has two number subtypes. `2 ^ 31` and `1 / 1` are floats even though their values are whole,
      while `//` and the bitwise operators keep integers. `math.type("1")` returns nil: only real numbers
      have a subtype, and a numeric string is still a string."""),

    q("string-length-is-bytes", r'''
        local s = "h\u{e9}llo"
        local r = { #s, utf8.len(s), #utf8.char(228, 8364), #"a\0b" }
        print(table.concat(r, " "))
    ''', "6 5 5 3", ["5 5 5 3", "6 6 5 3", "6 5 2 2"],
      "# counts bytes, not characters; utf8.len counts characters",
      """The accented letter takes two bytes in UTF-8, so `#s` is 6 while `utf8.len(s)` is 5. `utf8.char(228,
      8364)` produces a 2-byte and a 3-byte character, 5 bytes in all. A zero byte inside a Lua string
      counts like any other byte."""),

    q("insert-remove-positions", r'''
        local t = { 10, 20, 30 }
        table.insert(t, 2, 15)
        local r = table.remove(t, 1)
        table.insert(t, 99)
        print(table.concat(t, ",") .. "|" .. r .. "|" .. #t)
    ''', "15,20,30,99|10|4", ["10,15,20,30,99|10|5", "15,20,30,99|15|4", "10,15,99,20,30|10|5"],
      "insert(t, pos, v) shifts up from pos, insert(t, v) appends, remove returns the removed value",
      """After inserting 15 at position 2 the list is 10, 15, 20, 30. Removing position 1 returns 10 and shifts
      everything down. The two-argument insert appends at the end, which gives 15, 20, 30, 99."""),

    q("ipairs-stops-at-nil", r'''
        local t = { 1, 2, nil, 4 }
        local n = 0
        for _ in ipairs(t) do n = n + 1 end
        print(n .. " " .. select("#", table.unpack(t, 1, 4)))
    ''', "2 4", ["4 4", "2 2", "3 4"],
      "ipairs stops at the first nil; the element after the hole is still there",
      """`ipairs` walks 1, 2, 3 and so on until it meets a nil, so the hole at index 3 ends the loop after two
      iterations. The 4 is still stored, since unpacking indexes 1 to 4 gives four values. That is also why
      `#t` cannot be trusted on a table with holes."""),

    q("and-or-ternary-idiom", r'''
        local function pick(c, a, b) return c and a or b end
        local r = { tostring(pick(true, false, "b")), tostring(pick(true, 0, "b")),
                    tostring(pick(false, 1, nil)), tostring(nil and 1),
                    tostring(false or nil) }
        print(table.concat(r, "|"))
    ''', "b|0|nil|nil|nil", ["false|0|nil|nil|false", "b|b|b|nil|nil", "false|0|b|nil|nil"],
      "`c and a or b` is not a real ternary: a false value for a falls through to b",
      """`and` returns its first operand if it is false, else the second, and `or` returns its first operand
      if it is true, else the second. With `a` false the `and` part gives false, so `or` returns "b". Zero
      is truthy in Lua, so `pick(true, 0, "b")` keeps the 0."""),

    q("closures-fresh-per-iteration", r'''
        local fs, out = {}, {}
        for i = 1, 3 do fs[i] = function() return i end end
        for _, f in ipairs(fs) do out[#out + 1] = f() end
        local j, gs, out2 = 0, {}, {}
        while j < 3 do j = j + 1; gs[j] = function() return j end end
        for _, g in ipairs(gs) do out2[#out2 + 1] = g() end
        print(table.concat(out, ",") .. "|" .. table.concat(out2, ","))
    ''', "1,2,3|3,3,3", ["3,3,3|3,3,3", "1,2,3|1,2,3", "3,3,3|1,2,3"],
      "A for loop makes a new variable on each iteration; a variable declared outside is shared",
      """Each pass of a numeric `for` has its own copy of `i`, so every closure remembers a different value.
      In the `while` version all the closures capture the same outer `j`, which is 3 when the loop ends."""),

    q("shadowed-local-captured", r'''
        local x = 10
        local function f() return x end
        local x = 20
        do
          local x = x + 1
          x = x * 2
        end
        print(f() .. " " .. x)
    ''', "10 20", ["20 20", "10 42", "20 42"],
      "A second `local x` makes a new variable; earlier closures keep the first one",
      """Declaring `local x` again does not change the old variable, it creates a new one hiding it, so `f`
      still sees 10. The inner block's `x` is initialised from the outer 20, doubles its own copy and then
      disappears, which leaves the outer x as 20."""),

    q("find-pattern-versus-plain", r'''
        local a, b = ("a.b"):find(".")
        local c, d = ("a.b"):find(".", 1, true)
        local e = ("hello"):find("xyz")
        local f, g = ("hello"):find("l+")
        print(a .. b .. c .. d .. tostring(e) .. f .. g)
    ''', "1122nil34", ["2222nil33", "1122nil23", "1111nil34"],
      "find treats its argument as a pattern; the fourth argument makes it a plain search",
      """In a Lua pattern the dot matches any character, so the first find matches "a" at position 1. With the
      plain flag set to true the dot is a literal, found at position 2. A failed search returns nil, and
      `l+` matches the run "ll" at positions 3 to 4."""),

    q("gsub-returns-count", r'''
        local s1, n1 = ("a.b.c"):gsub(".", "-")
        local s2, n2 = ("a.b.c"):gsub("%.", "-")
        local s3, n3 = ("abc"):gsub("", "-")
        print(s1 .. n1 .. " " .. s2 .. n2 .. " " .. s3 .. n3)
    ''', "-----5 a-b-c2 -a-b-c-4", ["a-b-c5 a-b-c2 -a-b-c-4", "-----5 a-b-c2 abc0", "-----5 a-b-c2 -a-b-c-3"],
      "In a pattern . means any character, so a literal dot must be written %.",
      """Without the escape the dot matches every character, so all five are replaced, while `%.` matches only the
      real dots. An empty pattern matches at every position including both ends, four places in "abc". `gsub`
      returns the new string and the number of matches."""),

    q("multiple-results-truncated", r'''
        local function mr() return 1, 2, 3 end
        local function count(...) return select("#", ...) end
        local t = { mr(), mr() }
        local u = { mr(), (mr()) }
        local r = { #t, #u, count(mr(), mr()), count((mr())), count(mr(), nil) }
        print(table.concat(r, " "))
    ''', "4 2 4 1 2", ["6 2 6 1 2", "4 2 4 3 4", "3 2 4 1 3"],
      "Only the last expression in a list expands to all its results; others are cut to one",
      """In `{ mr(), mr() }` the first call is cut to one value and the last one gives all three, so the
      table has four items. Parentheses cut any call to one value, and a call followed by another
      expression (`mr(), nil`) is truncated as well."""),

    q("select-and-pack-nils", r'''
        print(select("#", nil, nil) .. " " .. table.pack(nil, 2, nil).n .. " " ..
              (select(2, "a", "b", "c")) .. " " .. select(-1, "a", "b", "c"))
    ''', "2 3 b c", ["0 2 b c", "2 3 b b c", "2 1 b a"],
      "select('#', ...) counts nils; select(n, ...) returns all values from n on; -1 is the last",
      """`select("#", ...)` and `table.pack(...).n` both count trailing nils, which `#` could not. `select(2,
      ...)` returns all values from the second on, so it is wrapped in parentheses to keep just the first.
      `select(-1, ...)` returns the last value."""),

    q("integer-wraparound", r'''
        local r = { math.maxinteger + 1 == math.mininteger, math.maxinteger * 2,
                    1 << 63, 1 << 64, -1 >> 1, math.huge == 1 / 0 }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "true -2 -9223372036854775808 0 9223372036854775807 true",
      ["false 1.844674407371e+19 9223372036854775808 0 -1 true", "true -2 -9223372036854775808 1 -1 true",
       "true -2 9223372036854775808 0 9223372036854775807 true"],
      "Integers wrap around silently at 64 bits, and >> is a logical shift",
      """Lua integers do not overflow into floats: adding 1 to the maximum gives the minimum, and doubling the
      maximum gives -2. `1 << 63` sets only the sign bit. Shifting by 64 or more gives 0, and `>>` shifts in
      zeros, so -1 >> 1 is the maximum integer."""),

    q("float-to-string", r'''
        local v = { 1e15, 2 ^ 53, 0.1 + 0.2, 3.0, -0.0, 1e14, 10 / 2, 1e2, math.pi }
        for i = 1, #v do v[i] = tostring(v[i]) end
        print(table.concat(v, " "))
    ''', "1e+15 9.007199254741e+15 0.3 3.0 -0.0 1e+14 5.0 100.0 3.1415926535898",
      ["1000000000000000 9007199254740992 0.30000000000000004 3 0 100000000000000 5 100 3.1415926535898",
       "1e+15 9.007199254741e+15 0.3 3 0.0 1e+14 5 100 3.1415926535898",
       "1e+15 9007199254740992.0 0.30000000000000004 3.0 -0.0 1e+14 5.0 100.0 3.141592653589793"],
      "Floats print with 14 significant digits (%.14g) and get \".0\" only when they look like integers",
      """Lua formats floats with `%.14g`, so 0.1 + 0.2 shows as 0.3 and 2^53 loses its last digits.
      Anything from 1e14 up needs exponent notation at 14 digits. When the text would look like an integer,
      Lua adds `.0`, which is why 3.0, 5.0 and 100.0 are not shown as plain integers."""),

    q("float-keys-normalised", r'''
        local t = {}
        t[1] = "a"
        t[1.0] = "b"
        t["1"] = "c"
        t[2 ^ 53] = "d"
        print(t[1] .. t["1"] .. tostring(t[1.5]) .. #t .. tostring(t[2 ^ 53 | 0]))
    ''', "bcnil1d", ["acnil1d", "bbnil1d", "bcnil2d"],
      "A float key with an integer value is converted to the integer key; \"1\" is a different key",
      """`t[1.0]` is the same slot as `t[1]`, so "b" overwrites "a". The string "1" is a distinct key. Whole
      floats are normalised to integers when used as keys, so `2^53` (a float) and the integer 2^53 reach the
      same entry."""),

    q("string-comparison-order", r'''
        local r = { "10" < "9", 10 < 9, "Z" < "a", "abc" < "abd", "" < "a",
                    "10" == 10 }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "true false true true true false", ["false false true true true false", "true false false true true false",
                                             "true false true true true true"],
      "Strings compare character by character, and \"10\" == 10 is false (no conversion for ==)",
      """Comparing two strings is alphabetical (by byte values), so "10" < "9" is true and uppercase letters
      come before lowercase ones. Two numbers compare numerically. `==` never converts types, so a string is
      never equal to a number."""),

    q("equality-flavours", r'''
        local a = {}
        local b = a
        local r = { {} == {}, a == b, 1 == 1.0, "1" == 1, 0.1 + 0.2 == 0.3,
                    0 == -0.0 }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "false true true false false true", ["true true true false false true", "false true false false false true",
                                              "false true true true false true"],
      "Tables are equal only if they are the same object; 1 == 1.0 compares the values",
      """Two table constructors create two different objects, so they are never equal; `b = a` is the same
      object. An integer and a float with the same value are equal. Floating-point sums such as 0.1 + 0.2 are
      not exactly 0.3, and negative zero equals zero."""),

    q("format-directives", r'''
        print(string.format("%d|%5.1f|%s|%s|%x|%-4s|%03d|%g|%g",
                            3.0, 3.14159, nil, true, 255, "ab", 7, 100000, 1e20))
    ''', "3|  3.1|nil|true|ff|ab  |007|100000|1e+20", ["3.0|3.1|nil|true|FF|ab|7|100000|1e+20",
                                                       "3|  3.1||true|ff|ab  |007|1e+05|1e+20",
                                                       "3|  3.1|nil|1|ff|   ab|007|100000|100000000000000000000"],
      "%d accepts a float with a whole value; %s works on any value; %g chooses the short form",
      """`%d` needs a number that fits an integer, so 3.0 is fine and prints as 3. `%s` runs `tostring`,
      so nil and true print as words. `%g` uses the shorter of fixed or exponent form, so 100000 stays
      plain and 1e20 turns into 1e+20."""),

    q("tonumber-forms", r'''
        local v = { tonumber("0x10"), tonumber("10", 2), tonumber("  5  "),
                    tonumber("5x"), tonumber("1e2"), tonumber(""),
                    tonumber("z", 36), tonumber("1_000") }
        for i = 1, 8 do v[i] = tostring(v[i]) end
        print(table.concat(v, " "))
    ''', "16 2 5 nil 100.0 nil 35 nil", ["16 2 5 5 100 nil 35 1000", "16 10 5 nil 100.0 0 35 nil", "0 2 5 nil 100.0 nil z nil"],
      "tonumber returns nil (not 0) for bad input, accepts hex, spaces and any base from 2 to 36",
      """`tonumber` is strict: a string must be wholly a number, apart from surrounding whitespace, so "5x" and
      "1_000" fail with nil. Hex strings are accepted, "1e2" gives the float 100.0, and a base argument
      reads digits and letters, so "z" in base 36 is 35."""),

    q("numeric-for-forms", r'''
        local out = {}
        for i = 1, 2.5 do out[#out + 1] = i end
        for i = 1.0, 2 do out[#out + 1] = i end
        for i = 3, 1, -1 do out[#out + 1] = i end
        for i = 1, 0 do out[#out + 1] = "x" end
        print(table.concat(out, ","))
    ''', "1,2,1.0,2.0,3,2,1", ["1,2,3,1,2,3,2,1", "1,2,1,2,3,2,1", "1,2,1.0,2.0,3,2,1,x"],
      "With an integer start and step the counter stays an integer, even if the limit is a float",
      """The first loop runs for 1 and 2: its limit 2.5 is rounded down, and the counter stays an integer. The
      second starts at 1.0 so every value is a float. A loop whose start is already past the limit does not
      run at all."""),

    q("loop-variable-is-a-copy", r'''
        local out = {}
        for i = 1, 3 do
          i = i * 2
          out[#out + 1] = i
        end
        local n = 0
        repeat local done = n >= 2; n = n + 1 until done
        print(table.concat(out, ",") .. " " .. n)
    ''', "2,4,6 3", ["2,6 3", "2,4,6 2", "2,4 3"],
      "Changing the loop variable does not change the iteration; locals in repeat are visible in until",
      """The counter of a numeric `for` is a fresh local copy each time, so assigning to it only affects that
      pass. In `repeat ... until` the condition can see the locals of the body, so the loop stops once `done`
      is true, after `n` has reached 3."""),

    # ── Medium: tables, patterns, metatables, errors ───────────────────────
    q("sort-default-orders", r'''
        local n = { 10, 9, 100, 1 }
        local s = { "10", "9", "100", "1" }
        local d = { 3, 1, 2 }
        table.sort(n)
        table.sort(s)
        table.sort(d, function(a, b) return a > b end)
        local function j(t) return table.concat(t, ",") end
        print(j(n) .. " " .. j(s) .. " " .. j(d))
    ''', "1,9,10,100 1,10,100,9 3,2,1", ["1,9,10,100 1,9,10,100 3,2,1", "1,10,100,9 1,10,100,9 1,2,3",
                                         "1,9,10,100 1,10,100,9 1,2,3"],
      "sort compares numbers as numbers and strings as text, so \"10\" sorts before \"9\"",
      """Without a comparison function `table.sort` uses `<`, which orders numbers numerically and strings
      alphabetically. As text, "10" and "100" come before "9" because the character "1" is smaller than "9".
      A custom function with `>` reverses the order."""),

    q("unpack-ranges", r'''
        local function count(...) return select("#", ...) end
        local r = { count(table.unpack({ 1, 2, 3 }, 2)),
                    count(table.unpack({}, 1, 3)),
                    count(table.unpack({ 1, nil, 3 }, 1, 3)),
                    (table.unpack({ 5, 6 })) }
        print(table.concat(r, " "))
    ''', "2 3 3 5", ["3 0 3 5", "2 0 2 5", "2 3 3 6"],
      "unpack(t, i, j) returns exactly j - i + 1 values, filling gaps with nil",
      """The second argument is the start and the third the end, so `unpack(t, 1, 3)` gives three values even if
      the table is empty. With only a start index the end defaults to `#t`. Wrapping the call in parentheses
      keeps just its first value."""),

    q("index-chain-and-rawget", r'''
        local base = { greet = function() return "hi" end }
        local obj = setmetatable({}, { __index = base })
        obj.x = 1
        print(obj.greet() .. tostring(rawget(obj, "greet")) .. obj.x ..
              tostring(obj.y))
    ''', "hinil1nil", ["hihi1nil", "hinil1", "nilnil1nil"],
      "__index is consulted only when the key is missing; rawget skips it",
      """`obj.greet` is not stored in `obj`, so Lua looks in the `__index` table and finds the function. `rawget`
      looks only at the object itself and returns nil. A key found nowhere in the chain is nil, without any
      error."""),

    q("comparison-metamethods", r'''
        local V = {}
        V.__eq = function(a, b) return a.n == b.n end
        V.__lt = function(a, b) return a.n < b.n end
        V.__le = function(a, b) return a.n <= b.n end
        V.__tostring = function(a) return "V" .. a.n end
        V.__concat = function(a, b) return tostring(a) .. tostring(b) end
        local function new(n) return setmetatable({ n = n }, V) end
        local a, b = new(1), new(1)
        local r = { a == b, a < b, a <= b, a ~= b, rawequal(a, b) }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, ",") .. " " .. (a .. new(2)) .. " " .. (a .. "x"))
    ''', "true,false,true,false,false V1V2 V1x", ["false,false,true,true,false V1V2 V1x",
                                                  "true,false,true,false,true V1V2 V1x",
                                                  "true,false,true,false,false V1V2 1x"],
      "__eq makes two different tables equal, but only rawequal asks if they are the same object",
      """Both operands are tables with the same `__eq`, so `a == b` calls it and compares the `n` fields. `a ~=
      b` is just the negation of that result, while `rawequal` ignores the metamethod. `__concat` is also
      used when only one side is the table."""),

    q("index-function-is-lazy", r'''
        local calls = 0
        local t = setmetatable({}, { __index = function(_, k)
          calls = calls + 1
          return k * 2
        end })
        local a, b = t[2], t[3]
        t[2] = "set"
        print(a .. " " .. b .. " " .. t[2] .. " " .. calls)
    ''', "4 6 set 2", ["4 6 set 3", "4 6 4 2", "4 6 set 0"],
      "An __index function runs only for missing keys; assigning stores a real value",
      """The two reads of missing keys call the function, so `calls` becomes 2. Assigning `t[2]` stores a
      normal entry in the table itself, and later reads find it directly without calling the function again."""),

    q("class-inheritance-chain", r'''
        local A = {}; A.__index = A
        function A.new(n) return setmetatable({ name = n }, A) end
        function A:hello() return "A:" .. self.name end
        local B = setmetatable({}, { __index = A }); B.__index = B
        function B.new(n) return setmetatable(A.new(n), B) end
        function B:hello() return "B>" .. A.hello(self) end
        print(B.new("x"):hello() .. " " .. A.new("y"):hello())
    ''', "B>A:x A:y", ["B>A:x B>A:y", "A:x A:y", "B>B>A:x A:y"],
      "A parent's method is called with the dot form and an explicit self",
      """`B` inherits from `A` through its metatable's `__index`, and `B:hello` overrides the method. To reach the
      parent version it calls `A.hello(self)` with the dot, passing the object by hand. The second object is a
      plain `A`, so it never sees the override."""),

    q("shared-class-table", r'''
        local C = { items = {} }
        C.__index = C
        local a, b = setmetatable({}, C), setmetatable({}, C)
        a.items[#a.items + 1] = "x"
        b.count = 1
        print(#b.items .. tostring(a.count) .. tostring(b.count))
    ''', "1nil1", ["0nil1", "11nil", "1nil0"],
      "A table stored in the class is shared by every instance; assigning a field creates a per-object one",
      """Reading `a.items` finds the one table stored in `C`, so pushing onto it is visible from every instance.
      `b.count = 1` creates a new field on `b` only. The instance `a` still has no `count` of its own, and
      nothing in the class has one either."""),

    q("colon-and-string-methods", r'''
        print(("ab"):rep(2, "-") .. ("%d+%d"):format(1, 2) .. ("x"):byte() ..
              string.char(72, 105) .. #("abc"):upper())
    ''', "ab-ab1+2120Hi3", ["abab1+2120Hi3", "ab-ab1+2x72Hi3", "ab-ab1+2120Hi"],
      "Strings share one metatable, so every string function can be called as a method",
      """`s:f(...)` is the same as `string.f(s, ...)`. `rep` takes an optional separator, `format` can be called
      on the format string itself, and `byte` returns a number. The length operator binds more tightly than the
      method call written after the parenthesis."""),

    q("pcall-results", r'''
        local ok, e = pcall(error, "boom", 0)
        local ok2, a, b = pcall(function() return 1, 2 end)
        local ok3, t = pcall(error, { code = 7 })
        local r = { tostring(ok), e, tostring(ok2), a, b, tostring(ok3), t.code }
        print(table.concat(r, " "))
    ''', "false boom true 1 2 false 7", ["true boom true 1 2 false 7", "false boom true 1 false 7",
                                        "false boom 1 2 true false 7"],
      "pcall returns true plus all results, or false plus the error value (any type)",
      """`pcall` puts a status first. On success the function's results follow, here 1 and 2. On failure the
      error value follows, and `error` can throw any value, such as a string or a table, and level 0 stops Lua from adding a position."""),

    q("assert-passes-values", r'''
        local ok, m = pcall(assert, false, "custom")
        local ok2, m2 = pcall(assert, nil)
        local r = { tostring(ok), m, m2, select("#", assert(1, 2, 3)), assert("v") }
        print(table.concat(r, " "))
    ''', "false custom assertion failed! 3 v", ["false custom nil 3 v", "false custom assertion failed! 1 v",
                                               "true custom assertion failed! 3 v"],
      "assert returns all its arguments when the first is truthy; otherwise it raises its message",
      """`assert(v, ...)` hands back every argument it was given on success, so it can wrap a call such as
      `assert(io.open(...))`. When the first value is false or nil it raises the second argument as the error,
      or "assertion failed!" if there is none."""),

    q("coroutine-resume-flow", r'''
        local co = coroutine.create(function(a, b)
          local c = coroutine.yield(a + b)
          local d, e = coroutine.yield(c * 2)
          return d + e
        end)
        local _, r1 = coroutine.resume(co, 1, 2)
        local _, r2 = coroutine.resume(co, 10)
        local _, r3 = coroutine.resume(co, 3, 4)
        print(r1 .. " " .. r2 .. " " .. r3 .. " " .. coroutine.status(co) .. " " ..
              tostring(coroutine.resume(co)))
    ''', "3 20 7 dead false", ["3 20 7 suspended false", "3 10 7 dead true", "3 20 7 dead true"],
      "resume passes values in, yield passes values out, and a finished coroutine cannot be resumed",
      """The first `resume` gives the arguments to the function, which yields 1 + 2. Each later `resume` becomes
      the return value of the `yield` that stopped it, so c is 10 and d + e is 7. After the function returns the
      status is dead, and resuming again returns false with an error message."""),

    q("coroutine-wrap-generator", r'''
        local gen = coroutine.wrap(function()
          for i = 1, 3 do coroutine.yield(i) end
        end)
        local a, b, c = gen(), gen(), gen()
        local d = gen()
        print(a .. b .. c .. tostring(d))
    ''', "123nil", ["123", "1233", "123false"],
      "When the function ends, the next call returns nothing (nil); calling again would raise an error",
      """Each call to the wrapped function resumes the coroutine until its next `yield`. After the third value
      the loop ends, and the fourth call runs to the end of the function, which returns no values, so `d` is
      nil. A fifth call would fail because the coroutine is dead."""),

    q("math-rounding-forms", r'''
        local r = { math.floor(-3.5), math.ceil(3.2), tostring(math.tointeger(3.5)),
                    math.fmod(-7, 3), math.max(1, 2.5), math.floor(3.0),
                    7 // 2 == 3.0 }
        r[7] = r[7] and "eq" or "ne"
        print(table.concat(r, " "))
    ''', "-4 4 nil -1 2.5 3 eq", ["-3 4 3 2 2.5 3.0 eq", "-4 4 nil 2 2.5 3.0 ne", "-4 3 nil -1 2.5 3 eq"],
      "floor and ceil return integers, fmod keeps the dividend's sign, tointeger fails with nil",
      """In Lua 5.4 `math.floor` and `math.ceil` return an integer when the result fits, so 3.0 floors to 3.
      `math.fmod` truncates, unlike `%`, so -7 and 3 give -1. `math.tointeger(3.5)` returns nil because 3.5 has
      no integer value."""),

    q("function-declared-after-use", r'''
        local function a() return b end
        local b = 5
        local function c() return d end
        d = 6
        print(tostring(a()) .. " " .. b .. " " .. c())
    ''', "nil 5 6", ["5 5 6", "nil 5 nil", "nil nil 6"],
      "A name is local only from the line after its declaration; earlier code sees a global",
      """When `a` was compiled there was no local `b` yet, so `b` inside it means the global, which is nil. The
      later `local b` does not change that. `c` refers to the global `d`, which is set before the call and
      therefore found."""),

    q("pattern-greedy-and-lazy", r'''
        local greedy = ("<a><b>"):match("<(.*)>")
        local lazy = ("<a><b>"):match("<(.-)>")
        local cnt = select(2, ("a1b22c333"):gsub("%d+", "#"))
        local k, v = ("key=val"):match("(%w+)=(%w+)")
        print(lazy .. "|" .. greedy .. "|" .. cnt .. "|" .. v .. k)
    ''', "a|a><b|3|valkey", ["a|a|3|valkey", "a><b|a|3|valkey", "a|a><b|5|keyval"],
      "* is greedy and - is its lazy version; captures come back in order",
      """The greedy `.*` runs to the last `>` and so captures `a><b`, while the lazy `.-` stops at the first one
      and captures `a`. `gsub` counts three runs of digits as three replacements. A match with two captures
      returns both, in the order they appear in the pattern."""),

    q("table-move-shifts", r'''
        local a = { 1, 2, 3 }
        table.move(a, 1, 3, 2)
        local b = table.move({ 1, 2, 3 }, 2, 3, 1, {})
        print(table.concat(a, ",") .. " " .. table.concat(b, ","))
    ''', "1,1,2,3 2,3", ["1,1,1,1 2,3", "1,2,3 2,3", "1,1,2,3 1,2,3"],
      "table.move copies a range like memmove, so overlapping moves are safe",
      """`table.move(a, 1, 3, 2)` copies elements 1 to 3 onto positions 2 to 4, handling the overlap correctly,
      which gives 1, 1, 2, 3. With a fifth argument the copy goes into another table, here `{}`, which
      receives elements 2 and 3 at positions 1 and 2."""),

    q("string-arithmetic-coercion", r'''
        local r = { "10" + 0, "0x10" + 0, "1e1" + 0, " 5 " * 2, "3" // 2,
                    "3.0" + 1 }
        print(table.concat(r, " "))
    ''', "10 16 10.0 10 1 4.0", ["10 16 10 10 1 4", "10 0 10.0 10 1.0 4.0", "10 16 10.0 5 1 4.0"],
      "String operands are converted by the number rules, so integer-looking text stays an integer",
      """A string that looks like an integer becomes an integer, so "10" + 0 is 10 and "3" // 2 is 1. Text with
      an exponent or a decimal point becomes a float. Surrounding spaces are ignored, and hex notation is
      understood."""),

    q("bitwise-operators", r'''
        local r = { 5 & 3, 5 | 3, 5 ~ 3, ~5, 1 << 4, 256 >> 4, 3.0 | 0, 2 ^ 3 | 0 }
        print(table.concat(r, " "))
    ''', "1 7 6 -6 16 16 3 8", ["1 7 6 -5 16 16 3.0 8.0", "1 7 125 -6 16 16 3 8", "1 7 6 -6 16 16 30 8"],
      "~ is both xor (binary) and not (unary); floats with a whole value are converted to integers",
      """Written between two operands `~` is exclusive or, while in front of one it is bitwise not, so `~5` is
      -6. Floats are accepted when they hold a whole number, so `3.0 | 0` is the integer 3 and `2 ^ 3 | 0` turns 8.0
      into 8."""),

    q("operator-precedence", r'''
        local r = { 2 ^ 3 ^ 2, -2 ^ 2, not 1 == 2, 1 .. 2 == "12", "a" .. 1 + 2 }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "512.0 -4.0 false true a3", ["64.0 4.0 true true a3", "512.0 -4.0 true true a3",
                                      "512.0 -4.0 false false a12"],
      "^ is right-associative and above unary minus; not binds tighter than ==; arithmetic beats ..",
      """`2 ^ 3 ^ 2` is `2 ^ (3 ^ 2)`, and `-2 ^ 2` is `-(2 ^ 2)`. `not 1 == 2` means `(not 1) == 2`, which compares
      false with 2. Concatenation binds looser than arithmetic but tighter than comparison, which gives "a3" and makes the
      joined "12" equal to the string."""),

    q("type-names", r'''
        local r = { type(nil), type(1), type("1"), type({}), type(print),
                    type(coroutine.create(print)), type(io.stdout), type(type(1)) }
        print(table.concat(r, " "))
    ''', "nil number string table function thread userdata string",
      ["nil integer string table function coroutine file string", "nil number string table function thread userdata nil",
       "nil number string array function thread table string"],
      "type returns a string, even for nil; there is no \"integer\" type name",
      """`type` always returns one of eight names as a string, so `type(nil)` is the string "nil", not the value.
      Integers and floats are both "number" (use `math.type` to tell them apart). Coroutines are "thread" and
      open files are "userdata"."""),

    q("float-accumulation", r'''
        local x = 0
        for i = 1, 10 do x = x + 0.1 end
        print(tostring(x) .. " " .. tostring(x == 1) .. " " .. tostring(x < 1) ..
              " " .. string.format("%.17g", x))
    ''', "1.0 false true 0.99999999999999989", ["1.0 true false 1", "0.9999999999999999 false true 0.99999999999999989",
                                                "1.0 false true 1.0"],
      "tostring shows 14 digits, so a value just below 1 prints as 1.0 but still differs from 1",
      """Ten additions of 0.1 give 0.99999999999999989. `tostring` rounds to 14 significant digits and shows
      1.0, but the comparisons use the exact value, so it is not equal to 1. `%.17g` reveals all the
      digits."""),

    q("for-loop-near-maxinteger", r'''
        local n = 0
        for i = math.maxinteger - 1, math.maxinteger do n = n + 1 end
        local m = 0
        for i = 1, 3 do for j = i, 3 do m = m + 1 end end
        print(n .. " " .. m)
    ''', "2 6", ["1 6", "2 9", "0 6"],
      "Lua 5.4 computes the iteration count first, so a loop to maxinteger cannot wrap around",
      """In C-style loops, incrementing past the maximum would overflow and loop forever. Lua 5.4 works out how
      many iterations there will be before starting, so the loop stops after two. The nested loops count 3 + 2
      + 1 = 6 pairs."""),

    q("exact-int-float-comparison", r'''
        local m = math.maxinteger
        local r = { m + 0.0 == m, m + 0.0 == 2 ^ 63, m < m + 0.0,
                    math.tointeger(2 ^ 53), 2 ^ 53 + 1 == 2 ^ 53 }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "false true true 9007199254740992 true",
      ["true true false 9007199254740992 true", "false true true 9007199254740993 false",
       "true true true 9.007199254741e+15 true"],
      "Lua compares an integer and a float exactly, not by converting the integer to a float",
      """Converting the largest 64-bit integer to a float would round it up to 2^63, but Lua compares the two
      exact values, so `m + 0.0 == m` is false and `m < m + 0.0` is true. Floats run out of precision above 2^53,
      which is why `2^53 + 1` is equal to `2^53`."""),

    q("short-circuit-side-effects", r'''
        local n = 0
        local function inc() n = n + 1; return true end
        local _ = false and inc()
        _ = true or inc()
        _ = nil or inc()
        _ = 1 and inc()
        _ = false or false or inc()
        print(n)
    ''', "3", ["5", "2", "4"],
      "and / or skip their right operand when the left one decides the result",
      """`false and inc()` and `true or inc()` never call `inc`. The remaining three expressions need their
      right-hand side, so `inc` runs three times in total."""),

    q("load-with-environment", r'''
        local env = {}
        local f = load("y = 7; return y + 1", "chunk", "t", env)
        local r = f()
        print(tostring(y) .. env.y .. r)
    ''', "nil78", ["77", "nil7", "778"],
      "load compiles a string; the env argument decides which table its globals belong to",
      """With `env` as the fourth argument, the chunk's global `y` is stored in that table, not in the real
      global table, so the outer `y` is still nil. The chunk itself sees its own `y` as 7 and returns 8."""),

    q("goto-continue", r'''
        local out = {}
        for i = 1, 3 do
          if i == 2 then goto continue end
          out[#out + 1] = i
          ::continue::
        end
        print(table.concat(out, ","))
    ''', "1,3", ["1,2,3", "1", "3"],
      "Lua has no continue statement; goto to a label at the end of the loop body does the job",
      """`goto continue` jumps to the label at the end of the loop body, skipping the append for i = 2 but
      starting the next iteration normally. A label can only be seen from inside the same block."""),

    q("close-variables-order", r'''
        local log = {}
        local function closer(name)
          return setmetatable({}, { __close = function() log[#log + 1] = name end })
        end
        do
          local a <close> = closer("a")
          local b <close> = closer("b")
          log[#log + 1] = "body"
        end
        print(table.concat(log, ","))
    ''', "body,b,a", ["a,b,body", "body,a,b", "a,b"],
      "To-be-closed variables are closed in reverse order when the block ends",
      """A local marked `<close>` has its `__close` metamethod called when its scope ends, like a destructor.
      The variables are closed in the opposite order of declaration, so `b` is closed before `a`, and both
      come after the body ran."""),

    q("multiple-assignment-order", r'''
        local i = 1
        local t = {}
        i, t[i] = i + 1, 20
        local a, b, c = 1, 2
        local x, y = 1, 2, 3
        local r = { i, tostring(t[1]), tostring(t[2]), tostring(c), y }
        print(table.concat(r, " "))
    ''', "2 20 nil nil 2", ["2 nil 20 nil 2", "2 20 nil 0 3", "1 20 nil nil 2"],
      "All expressions on both sides are evaluated before any assignment happens",
      """In `i, t[i] = i + 1, 20` the index `i` is read as 1 before `i` is assigned, so the 20 lands in `t[1]`.
      Missing values on the right are filled with nil, which is why `c` is nil, and extra values are thrown
      away, so `y` is 2."""),

    q("division-by-zero-forms", r'''
        local r = {
          pcall(function() return 1 // 0 end),
          pcall(function() return 1 // 0.0 end),
          pcall(function() return 1 % 0 end),
          pcall(function() return 1 / 0 end),
        }
        print(tostring(r[1]) .. tostring(r[2]) .. tostring(r[3]) .. tostring(r[4]))
    ''', "falsetruefalsetrue", ["truetruetruetrue", "falsefalsefalsetrue", "falsetruefalsefalse"],
      "Integer // and % by zero raise an error; float division by zero gives inf",
      """Dividing two integers by zero with `//` or `%` is an error, because there is no integer result. With a
      float operand, or with `/`, which always works on floats, the result is inf and nothing is thrown. The
      table keeps only the first value of each `pcall`, the status."""),

    q("table-concat-ranges", r'''
        local t = { 1, 2.5, 3.0, "x" }
        local r = { table.concat(t, "-"), table.concat(t, ",", 2, 3),
                    #table.concat({}, ","), table.concat({ "a" }, ",", 1, 1) }
        print(table.concat(r, "|"))
    ''', "1-2.5-3.0-x|2.5,3.0|0|a", ["1-2.5-3-x|2.5,3|0|a", "1-2.5-3.0-x|2.5,3.0||a", "1-2.5-3.0-x|2,3|0|a"],
      "table.concat accepts numbers and strings, takes a range, and gives \"\" for an empty list",
      """Numbers are converted the same way as by `tostring`, so 3.0 keeps its `.0`. The third and fourth
      arguments select positions i to j, not values. An empty table yields the empty string, whose length
      is 0."""),

    q("shallow-copy-nested", r'''
        local a = { 1, { 2 } }
        local b = { table.unpack(a) }
        b[2][1] = 9
        b[1] = 0
        print(a[1] .. a[2][1])
    ''', "19", ["09", "10", "02"],
      "Copying a table copies only the references to nested tables",
      """`b` is a new table, so changing `b[1]` leaves `a[1]` alone. But `b[2]` and `a[2]` are the same inner
      table, so setting `b[2][1]` changes what `a` sees as well."""),

    q("counter-closures", r'''
        local function counter()
          local n = 0
          return function() n = n + 1; return n end, function() return n end
        end
        local inc1, get1 = counter()
        local inc2 = counter()
        inc1(); inc1(); inc2()
        print(inc1() .. get1() .. inc2())
    ''', "332", ["131", "322", "333"],
      "Closures made by one call share its local variable; each call to counter() makes a new one",
      """`inc1` and `get1` came from the same call, so they share one `n`, which is 2 after two increments and
      3 after the third, and `get1` sees it. `inc2` came from a separate call with its own `n`, so its
      second increment gives 2."""),

    q("newindex-proxy", r'''
        local store = {}
        local proxy = setmetatable({}, {
          __index = store,
          __newindex = function(_, k, v) store[k] = v * 2 end,
        })
        proxy.a = 5
        proxy.a = 7
        print(tostring(rawget(proxy, "a")) .. proxy.a)
    ''', "nil14", ["nil7", "514", "nil10"],
      "__newindex runs for every write to an absent key, and the proxy itself stays empty",
      """The proxy never receives the value: each write calls `__newindex`, which stores double the value in
      `store`. Because the key never appears in `proxy`, the second write is intercepted again, replacing 10
      with 14, and reads go through `__index`."""),

    q("remove-while-iterating", r'''
        local t = { 1, 2, 2, 3, 2 }
        for i, v in ipairs(t) do
          if v == 2 then table.remove(t, i) end
        end
        print(table.concat(t, ","))
    ''', "1,2,3", ["1,3", "1,2,3,2", "1,3,2"],
      "Removing during a forward loop shifts later items down, so the next one is skipped",
      """After the first 2 is removed, the second 2 slides into index 2, but the loop moves on to index 3 and
      never examines it. The last 2 is reached and removed, so one of the three 2s survives."""),

    q("string-sub-bounds", r'''
        local s = "hello"
        local r = { s:sub(-3, -2), s:sub(0), s:sub(10), s:sub(2, 100), s:sub(3, 2),
                    s:sub(-100, 2) }
        print(table.concat(r, "|"))
    ''', "ll|hello||ello||he", ["l|hello|nil|ello||he", "ll|hello||ello|l|he", "ll|ello||ello||he"],
      "sub clamps its bounds instead of failing, and an empty range gives \"\"",
      """Negative positions count from the end, so -3 to -2 is "ll". A start of 0 is treated as 1, and an end
      beyond the string is cut at the end. A start past the end or a range with start > end returns the empty
      string, never nil."""),

    q("float-modulo-signs", r'''
        local r = { -7.5 // 2, -7.5 % 2, 5.5 % -2, 5 % 3.0, 2 ^ -1, 8 // 3.0 }
        print(table.concat(r, " "))
    ''', "-4.0 0.5 -0.5 2.0 0.5 2.0", ["-3.0 -1.5 1.5 2 0.5 2", "-4.0 1.5 -0.5 2.0 0.5 2.0", "-4 0.5 -0.5 2 0.5 2"],
      "// floors and % takes the sign of the divisor, also for floats",
      """The floor of -3.75 is -4.0, and the remainder is chosen so that `a == (a // b) * b + a % b`, which
      gives 0.5 for -7.5 % 2 and -0.5 for 5.5 % -2. A float operand keeps every result a float, as the `.0`
      in the output shows."""),

    q("gsub-replacement-table-or-function", r'''
        local env = { name = "Bob" }
        local s1 = ("$name is $age"):gsub("%$(%w+)", env)
        local s2 = ("a b"):gsub("%a", function(c)
          if c == "a" then return "X" end
        end)
        print(s1 .. "|" .. s2)
    ''', "Bob is $age|X b", ["Bob is nil|X nil", "Bob is |X ", "Bob is $age|X"],
      "When a table or function gives nil or false, gsub keeps the original text",
      """The table is looked up with the first capture, so `$name` is replaced and `$age`, which is not a key,
      stays as it was. A function that returns nothing for the letter b leaves it unchanged in the same
      way."""),

    q("length-and-append-idioms", r'''
        local t = {}
        for i = 1, 5 do t[#t + 1] = i * i end
        t[#t] = nil
        table.insert(t, 1, 0)
        t[#t + 1] = t[1]
        print(#t .. " " .. table.concat(t, ","))
    ''', "6 0,1,4,9,16,0", ["6 0,1,4,9,16,25,0", "5 0,1,4,9,16", "6 1,4,9,16,0,0"],
      "t[#t + 1] appends and t[#t] = nil removes the last item; both keep the table a proper sequence",
      """Appending at `#t + 1` and clearing the last slot with nil are the two cheap sequence operations. After
      the squares 1 to 25 are stored, the 25 is removed, then a 0 is inserted at the front and a copy of the
      new first element is appended, so there are six items."""),
)
