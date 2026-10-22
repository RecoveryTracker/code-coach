"""Gotchas, Lua (third deck): run by Lua 5.4; portability notes are in langs.py (the `lua` entry).

New angles on the first two decks: the pattern language, string.format and the number edge cases, the metamethods
that are easy to misremember, coroutine states and protected calls. No card iterates with pairs()/next() or prints
a table or function address, and every card prints one line.
"""

from __future__ import annotations

from .items import Item, make

q = make("lua")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ──────────────────────────────────────────────────────
    q("string-indexing-is-not-characters", r'''
        local s = "hello"
        print(tostring(s[1]) .. " " .. s:sub(1, 1) .. " " ..
              tostring(s.len == string.len) .. " " .. #s)
    ''', "nil h true 5", ["h h true 5", "nil h false 5", "nil nil true 5"],
      "A string has no integer keys: s[1] looks in the string library, finds nothing and gives nil",
      """Indexing a string goes through the string metatable, whose `__index` is the `string` table. So `s.len` is
      the library function, but `s[1]` is a lookup of the key 1 in that table, which is nil. Use `s:sub(1, 1)` for a
      character."""),

    q("dot-versus-colon-call", r'''
        local o = { n = 1, get = function(self) return self.n end }
        local f = o.get
        local ok = pcall(o.get)
        print(o.get(o) .. " " .. o:get() .. " " .. f({ n = 7 }) .. " " ..
              tostring(ok))
    ''', "1 1 7 false", ["1 1 1 true", "1 nil 7 false", "1 1 7 true"],
      "obj:m() passes obj as the first argument; obj.m() passes nothing",
      """`o:get()` is shorthand for `o.get(o)`, so `self` is the table. `f({ n = 7 })` calls the same function with
      another table, so it reads 7. `pcall(o.get)` calls it with no argument at all, `self` is nil and
      `self.n` raises an error, which makes `pcall` return false."""),

    q("param-reassign-versus-mutate", r'''
        local function f(t)
          t.x = 1
          t = { x = 2 }
          return t.x
        end
        local a = {}
        local r = f(a)
        print(a.x .. " " .. r)
    ''', "1 2", ["2 2", "nil 2", "1 1"],
      "A table argument is shared until the parameter is assigned a new table",
      """`t.x = 1` changes the table the caller passed in. `t = { x = 2 }` only rebinds the local parameter to a
      different table, so the caller's table is untouched and still has x = 1, while the function returns the new
      one's x."""),

    q("closures-per-iteration-state", r'''
        local fs = {}
        for i = 1, 2 do
          local n = 0
          fs[i] = { inc = function() n = n + 1 return n end,
                    get = function() return n end }
        end
        fs[1].inc(); fs[1].inc(); fs[2].inc()
        print(fs[1].get() .. fs[2].get())
    ''', "21", ["33", "12", "22"],
      "Each pass through the loop body makes a fresh local, shared by the two closures made in that pass",
      """`local n = 0` runs once per iteration and creates a new variable each time. The `inc` and `get` closures
      from the same pass share that variable, but closures from different passes do not: the first table
      counted twice and the second once."""),

    q("multiple-assignment-swaps", r'''
        local t = { "a", "b", "c" }
        t[1], t[3] = t[3], t[1]
        local a, b, c = 1, 2, 3
        a, b, c = c, a, b
        local x, y = 1, 2
        x, y = y
        print(table.concat(t) .. " " .. a .. b .. c .. " " .. x .. tostring(y))
    ''', "cba 312 2nil", ["abc 312 2nil", "cba 231 2nil", "cba 312 22"],
      "All right-hand sides are evaluated before any assignment, and a missing value becomes nil",
      """The values `t[3]` and `t[1]` are read first and then stored, which swaps them without a temporary. The
      same rule rotates three variables at once. In `x, y = y` there is one value for two targets, so `x`
      gets 2 and `y` is set to nil."""),

    q("decimal-escapes-and-zero", r'''
        local r = { "\65\066\x43\u{44}", "\1234", #"a\z
                    b", #"\0", #"\\n" }
        print(table.concat(r, " "))
    ''', "ABCD {4 2 1 2", ["ABCD \\1234 3 1 3", "ABCD {4 3 0 2", "ABCD 1234 2 1 2"],
      "A decimal escape takes up to three digits, and \\z skips the whitespace that follows it",
      """`\\65` and `\\066` are decimal character codes, and `\\x43` and `\\u{44}` are hex and Unicode. `"\\1234"`
      reads three digits (123, a brace) and leaves the 4 as text. `\\z` removes the line break and indentation
      after it, so the string is just "ab". `"\\0"` is a one-character string, and `"\\\\n"` is a backslash
      and an n."""),

    q("table-remove-edges", r'''
        local r = {
          tostring(table.remove({})), table.remove({ 1, 2, 3 }),
          table.remove({ 1, 2, 3 }, 1), tostring(table.remove({ 1, 2, 3 }, 4)),
          #{ table.remove({ 5 }) },
        }
        print(table.concat(r, " "))
    ''', "nil 3 1 nil 1", ["nil 1 3 nil 0", "0 3 1 nil 1", "nil 3 1 3 1"],
      "table.remove takes the last element by default, and removing from an empty list gives nil",
      """Without a position `table.remove` pops the last element (3). With position 1 it takes the first. Position
      `#t + 1` is allowed and returns nil, because that slot is empty, and an empty table also gives nil. The last
      call returns the removed 5, so the constructor around it holds one value."""),

    # ── Medium ───────────────────────────────────────────────────────────
    q("lazy-dash-matches-empty", r'''
        local s = "aaab"
        local r = { s:match("a-"), s:match("a-b"), s:match("a*"),
                    ("aaa"):match("^a-$"), ("x-y"):match("x-y"),
                    ("x-y"):match("x%-y"), s:match("(a-)b") }
        print("[" .. table.concat(r, "][") .. "]")
    ''', "[][aaab][aaa][aaa][y][x-y][aaa]",
      ["[a][aaab][aaa][aaa][x-y][x-y][aaa]", "[][aaab][aaa][aaa][x-y][x-y][a]",
       "[][aaab][aaab][aaa][y][x-y][aaa]"],
      "In a pattern, - after an item means 'as few as possible', not a literal dash",
      """`a-` is a lazy repeat, so by itself it matches the empty string, but it grows when something after it
      needs more, as in `a-b`. `x-y` therefore means "any number of x, lazily, then y" and matches just the "y" at
      the end of "x-y". A literal dash needs the escape `%-`."""),

    q("find-captures-and-init", r'''
        local function j(...) return table.concat({ ... }, ",") end
        print(j(("key=val"):find("(%w+)=(%w+)")) .. " " ..
              j(("hello"):match("()ll()")) .. " " .. j(("abc"):find("c", -1)) ..
              " " .. tostring(("abc"):find("b", -1)) .. " " ..
              j(("abc"):find("", 4)) .. " " .. tostring(("abc"):find("", 5)))
    ''', "1,7,key,val 3,5 3,3 nil 4,3 nil", ["1,7 3,5 3,3 nil 4,3 nil",
                                             "1,7,key,val 2,4 3,3 2,2 4,3 nil",
                                             "1,7,key,val 3,5 3,3 nil 4,3 4,3"],
      "find gives start and end, then captures; () captures a position; a negative init counts from the end",
      """With captures, `find` returns the two indexes and then each capture. An empty `()` capture returns the
      position instead of text, so `match("()ll()")` gives 3 and 5. A negative start counts from the end, so
      looking for "b" from the last character fails. An empty pattern matches at length + 1 and not beyond it."""),

    q("gsub-captures-and-anchor", r'''
        local r = {
          (("hello world"):gsub("(%w+) (%w+)", "%2 %1")),
          (("abc"):gsub("%w", "%0%0")), (("aaa"):gsub("^a", "b")),
          (("a.b"):gsub("%.", "%%.")), (("aaa"):gsub("a", "b", 2)),
          (("abc"):gsub("(b)", "[%1]")),
        }
        print(table.concat(r, " "))
    ''', "world hello aabbcc baa a%.b bba a[b]c",
      ["world hello abc baa a.b bba a[b]c", "world hello aabbcc bbb a%.b bba a[b]c",
       "world hello aabbcc baa a%.b bbb a[b]c"],
      "In a replacement string %1 is a capture, %0 the whole match, and %% a literal percent",
      """`%1` and `%2` insert captures and `%0` the entire match. A `^` anchor only matches at the very start, so
      only the first "a" is replaced, and the optional fourth argument limits the number of replacements. To put a
      real percent sign in the replacement you must write `%%`. Parentheses around each call keep just the string,
      not the count."""),

    q("balanced-and-frontier-patterns", r'''
        local r = {
          ("f(a(b)c) d"):match("%b()"),
          (("THE (quick) fox"):gsub("%f[%a]%a", string.lower)),
          ("[[x]]"):match("%[(.-)%]"),
          ("hello world"):match("^(%w+)"),
        }
        print(table.concat(r, " "))
    ''', "(a(b)c) tHE (quick) fox [x hello", ["(a(b) tHE (quick) fox [x hello",
                                             "(a(b)c) tHE (quick) fox x hello",
                                             "(a(b)c) the (quick) fox [x hello"],
      "%b() matches balanced brackets, and %f[set] matches a transition into the set",
      """`%b()` pairs each opening bracket with its matching closing one, so it takes the whole "(a(b)c)". The
      frontier `%f[%a]` matches the point where a letter follows a non-letter, so `%f[%a]%a` is the first letter of
      each word. In "[[x]]" the lazy capture stops at the first `]` but starts after the first `[`, so it
      includes the second bracket: "[x"."""),

    q("format-q-and-conversions", r'''
        local r = {
          string.format("%s %s %s", 1, 1.0, "x"), string.format("%q", 'say "hi"'),
          string.format("%.3s|%5s|%-5s|", "abcdef", "ab", "ab"),
          string.format("%c%c%c", 76, 117, 97),
          string.format("%o %X %e", 8, 255, 12345.678), string.format("%d%%", "10"),
        }
        print(table.concat(r, " ; "))
    ''', '1 1.0 x ; "say \\"hi\\"" ; abc|   ab|ab   | ; Lua ; 10 FF 1.234568e+04 ; 10%',
      ['1 1 x ; "say \\"hi\\"" ; abc|   ab|ab   | ; Lua ; 10 FF 1.234568e+04 ; 10%',
       '1 1.0 x ; say "hi" ; abc|ab   |   ab| ; Lua ; 10 FF 1.234568e+04 ; 10%',
       '1 1.0 x ; "say \\"hi\\"" ; abc|   ab|ab   | ; 76117 ; 8 ff 12345.678 ; 10%'],
      "%s keeps 1.0 as 1.0, %q writes a string back as Lua source, and %c takes a character code",
      """`%s` uses `tostring`, so the float 1.0 stays "1.0". `%q` adds quotes and escapes the inner ones so the text
      could be pasted back into a program. A precision on `%s` cuts the string, a width pads it, and `-` pads on the
      right. `%c` turns codes into characters, and `%d` accepts the string "10" because it converts to a
      number."""),

    q("rep-reverse-byte-char", r'''
        local r = {
          ("ab"):rep(0) .. "|", ("ab"):rep(3, ","), ("abc"):reverse(),
          table.concat({ ("abc"):byte(1, -1) }, "+"), #string.char(),
          ("A"):lower() .. ("b"):upper(),
          ("abc"):byte(10) == nil and "none" or "some",
        }
        print(table.concat(r, " "))
    ''', "| ab,ab,ab cba 97+98+99 0 aB none", [" ab,ab,ab cba 97+98+99 0 aB none",
                                              "| ababab cba 97+98+99 0 aB none",
                                              "| ab,ab,ab cba 97 0 aB some"],
      "rep(0) is an empty string, byte can return several values, and a byte out of range returns nothing",
      """`rep(3, ",")` puts the separator between copies only. `byte(1, -1)` returns one number per character, so
      wrapping the call in a table constructor collects them all. `string.char()` with no arguments is the empty
      string, and `byte` past the end returns no value at all, which compares equal to nil."""),

    q("integer-literal-overflow", r'''
        local r = { 0xffffffffffffffff, 9223372036854775807,
                    9223372036854775808, math.type(9223372036854775808),
                    tonumber("9223372036854775808"), 0x7fffffffffffffff + 1,
                    0xA.8p0 }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "-1 9223372036854775807 9.2233720368548e+18 float 9.2233720368548e+18 -9223372036854775808 10.5",
      ["18446744073709551615 9223372036854775807 9.2233720368548e+18 float 9.2233720368548e+18 -9223372036854775808 10.5",
       "-1 9223372036854775807 9223372036854775808 integer 9223372036854775808 9223372036854775808 10.5",
       "-1 9223372036854775807 9.2233720368548e+18 float 9.2233720368548e+18 9.2233720368548e+18 10.5"],
      "A decimal literal too big for 64 bits becomes a float, but a hex literal wraps around",
      """Decimal numerals that do not fit in an integer silently turn into floats, and `tonumber` follows the same
      rule. Hexadecimal integers wrap modulo 2^64, so `0xffffffffffffffff` is -1. Arithmetic on integers wraps
      too: `maxinteger + 1` is the minimum. A hex numeral with a point and a `p` exponent is a float."""),

    q("math-results-float-or-int", r'''
        local r = { math.sqrt(16), math.abs(-3), math.max(1, 2), math.max(1, 2.0),
                    math.max(2, 1.0), math.log(8, 2), math.exp(0), math.ceil(-0.5),
                    math.abs(-0.0) }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "4.0 3 2 2.0 2 3.0 1.0 0 0.0", ["4 3 2 2 2 3 1 0 0", "4.0 3 2 2.0 2.0 3.0 1.0 -0 0.0",
                                        "4.0 3 2 2 2 3.0 1.0 0 0"],
      "sqrt, log and exp return floats; max keeps its winner's type; ceil and floor return integers",
      """`math.sqrt(16)` is the float 4.0, as are `log` and `exp`. `max` returns the winning argument with its own
      type, so a float wins as 2.0 and an integer as 2. `math.ceil` and `floor` convert to an integer when the result
      fits, which is why `ceil(-0.5)` prints 0 and not -0.0, while `abs(-0.0)` stays a float."""),

    q("math-floor-and-integer-limits", r'''
        local r = { math.type(math.floor(2 ^ 62)), math.type(math.floor(2 ^ 70)),
                    math.abs(math.mininteger) == math.mininteger, math.ult(1, -1),
                    math.maxinteger // -1, math.mininteger // -1,
                    tostring(math.tointeger(2 ^ 63)) }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "integer float true true -9223372036854775807 -9223372036854775808 nil",
      ["integer integer true true -9223372036854775807 -9223372036854775808 nil",
       "integer float false false -9223372036854775807 9223372036854775808 nil",
       "integer float true true -9223372036854775807 -9223372036854775808 9223372036854775808"],
      "floor gives a float if the result does not fit an integer, and integer overflow wraps",
      """`math.floor(2^62)` fits in 64 bits and is an integer; `2^70` does not, so it stays a float. The most
      negative integer has no positive twin, so `abs` and division by -1 wrap back to it. `math.ult` compares as
      unsigned numbers, where -1 is the largest, and `tointeger` returns nil for 2^63, which is just out of range."""),

    q("which-comparisons-raise", r'''
        local function ok(f) return tostring((pcall(f))) end
        local r = { ok(function() return 1 < "2" end),
                    ok(function() return "1" < "2" end),
                    ok(function() return 1 == "1" end),
                    ok(function() return {} < {} end),
                    ok(function() return 1 < 2 < 3 end),
                    ok(function() return nil == false end),
                    ok(function() return "a" < "b" end),
                    ok(function() return #5 end) }
        print(table.concat(r, " "))
    ''', "false true true false false true true false",
      ["true true true false false true true false", "false true false false false true true false",
       "false true true false true true true false"],
      "Equality never raises an error, but ordering needs two numbers or two strings",
      """`==` can compare any two values and simply answers false for different types. `<` between a number and a
      string raises an error, as does `<` between two plain tables. `1 < 2 < 3` is `(1 < 2) < 3`, which compares
      a boolean with a number, and `#5` has no length."""),

    q("vararg-in-the-middle", r'''
        local function f(...) return ..., "end" end
        local function g(...) return "start", ... end
        local function h(...) return (...) end
        print(select("#", f(1, 2, 3)) .. select("#", g(1, 2, 3)) ..
              select("#", h(1, 2, 3)) .. select("#", f()) .. select("#", g()))
    ''', "24121", ["24131", "44121", "23121"],
      "... only expands fully as the last item of a list; elsewhere it gives exactly one value",
      """In `return ..., "end"` the vararg is not last, so it is cut down to its first value (nil when there are none):
      two results. In `return "start", ...` it is last and expands, so three arguments give four results and none
      gives one. `(...)` in parentheses is always one value."""),

    q("float-step-loop-count", r'''
        local n, last = 0, 0
        for i = 0, 1, 0.1 do n = n + 1; last = i end
        local m = 0
        for i = 1, 0, -0.25 do m = m + 1 end
        print(n .. " " .. m .. " " .. string.format("%.17g", last))
    ''', "11 5 0.99999999999999989", ["10 5 1", "11 5 1", "10 4 0.99999999999999989"],
      "A float loop adds the step each time, so rounding error decides the last pass",
      """Adding 0.1 ten times gives 0.9999999999999999, which is still below the limit of 1, so there is an eleventh
      pass and the loop variable never reaches 1.0 exactly; the next sum would be above 1. A step of 0.25 is exact
      in binary, so counting down from 1 to 0 takes five passes."""),

    q("metatable-field-protects-it", r'''
        local t = setmetatable({}, { __metatable = "locked" })
        local ok = pcall(setmetatable, t, {})
        print(getmetatable(t) .. " " .. tostring(ok) .. " " ..
              tostring(getmetatable("abc").__index == string) .. " " ..
              tostring(getmetatable({})))
    ''', "locked false true nil", ["table false true nil", "locked true true nil", "locked false false nil"],
      "A __metatable field is what getmetatable returns, and it blocks setmetatable",
      """When the metatable has a `__metatable` field, `getmetatable` returns that value instead of the table itself
      and `setmetatable` refuses to change it, so `pcall` reports a failure. Strings share a metatable whose
      `__index` is the `string` library, and an ordinary table has no metatable, so the answer is nil."""),

    q("arithmetic-metamethods-either-operand", r'''
        local mt = {}
        mt.__add = function(a, b)
          local x = type(a) == "table" and a.n or a
          return x + (type(b) == "table" and b.n or b)
        end
        mt.__call = function(self, x) return self.n * x end
        mt.__len = function(self) return self.n end
        mt.__unm = function(self) return -self.n end
        local o = setmetatable({ n = 5 }, mt)
        print((o + 1) .. " " .. (1 + o) .. " " .. o(3) .. " " .. #o .. " " ..
              -o .. " " .. rawlen(o))
    ''', "6 6 15 5 -5 0", ["6 1 15 5 -5 0", "6 6 15 5 -5 5", "6 6 15 0 -5 0"],
      "A metamethod is tried for either operand, __call receives the object first, and rawlen skips __len",
      """For `1 + o` the first operand has no `__add`, so Lua looks at the second and calls the same function with
      the arguments in the original order. `o(3)` calls `__call(o, 3)`. `#o` uses `__len`, but `rawlen` ignores
      metamethods and measures the actual table, which has no array part: 0."""),

    q("concat-ignores-tostring", r'''
        local o = setmetatable({}, { __tostring = function() return "T" end })
        local ok = pcall(function() return "x" .. o end)
        print(tostring(ok) .. " " .. tostring(o) .. " " ..
              string.format("%s|%5s", o, o) .. " " .. #tostring(o))
    ''', "false T T|    T 1", ["true T T|    T 1", "false T T|T 1", "false table T|    T 1"],
      "print, tostring and %s use __tostring, but .. does not",
      """`tostring(o)` and the `%s` format directive call `__tostring`, so the object shows up as "T". The `..`
      operator only converts strings and numbers: for anything else it looks for `__concat`, finds none, and
      raises an error, so `pcall` returns false."""),

    q("ipairs-respects-index", r'''
        local t = setmetatable({}, { __index = function(_, i)
          if i <= 3 then return i * 10 end
        end })
        local n, sum = 0, 0
        for _, v in ipairs(t) do
          n = n + 1
          sum = sum + v
        end
        print(n .. " " .. sum .. " " .. #t .. " " .. rawlen(t))
    ''', "3 60 0 0", ["0 0 0 0", "3 60 3 3", "3 60 3 0"],
      "ipairs reads through __index, but the length operator and rawlen see an empty table",
      """Since Lua 5.3 `ipairs` uses normal indexing, so the `__index` function supplies 10, 20 and 30 and stops when
      it returns nil at 4. The table itself holds nothing, so `#t` and `rawlen(t)` are both 0."""),

    q("eq-metamethod-needs-two-tables", r'''
        local a = setmetatable({}, { __eq = function() return true end })
        local r = { a == 1, a == {}, {} == a, a ~= {}, rawequal(a, {}), a == "x" }
        for i = 1, #r do r[i] = tostring(r[i]) end
        print(table.concat(r, " "))
    ''', "false true true false false false", ["true true true false false true",
                                               "false true false false false false",
                                               "false true true true false false"],
      "__eq is only consulted when both operands are tables, and either one may supply it",

      """Comparing a table with a number or a string never calls `__eq`: the types differ, so the answer is false.
      Between two tables Lua tries the first operand's `__eq`, then the second's, so both `a == {}` and `{} == a`
      are true. `~=` is the negation, and `rawequal` ignores the metamethod."""),

    q("lt-metamethod-without-le", r'''
        local mt = { __lt = function(a, b)
          local x = type(a) == "table" and a.n or a
          local y = type(b) == "table" and b.n or b
          return x < y
        end }
        local o = setmetatable({ n = 5 }, mt)
        local ok = pcall(function() return o <= 5 end)
        print(tostring(o < 9) .. tostring(1 < o) .. tostring(o > 9) ..
              tostring(ok))
    ''', "truetruefalsefalse", ["truetruetruefalse", "truetruefalsetrue", "truefalsefalsefalse"],
      "__lt works with a number on either side, > swaps the operands, and <= no longer falls back to __lt",
      """`o < 9` and `1 < o` both call `__lt`, which works as long as either operand has it. `o > 9` is rewritten as
      `9 < o`, giving false. Lua 5.4 no longer emulates `<=` with `not (b < a)`, so without an `__le` the
      comparison `o <= 5` raises an error."""),

    q("coroutine-status-states", r'''
        local log = {}
        local outer
        local inner = coroutine.create(function()
          log[#log + 1] = coroutine.status(outer)
        end)
        outer = coroutine.create(function()
          log[#log + 1] = coroutine.status(outer)
          coroutine.resume(inner)
          coroutine.yield()
        end)
        log[#log + 1] = coroutine.status(outer)
        coroutine.resume(outer)
        log[#log + 1] = coroutine.status(outer)
        log[#log + 1] = coroutine.status(inner)
        print(table.concat(log, " "))
    ''', "suspended running normal suspended dead",
      ["suspended running running suspended dead", "suspended running suspended suspended suspended",
       "dead running normal suspended dead"],
      "A coroutine that resumed another one is 'normal', not 'running' or 'suspended'",
      """A new coroutine is suspended, and the one currently executing is running. While `outer` has resumed
      `inner`, `outer` is in the normal state: alive but not the one that is running. After `outer` yields it is
      suspended again, and `inner` has finished and is dead."""),

    q("coroutine-errors-and-dead", r'''
        local co = coroutine.create(function() error("oops", 0) end)
        local ok1, m1 = coroutine.resume(co)
        local ok2, m2 = coroutine.resume(co)
        print(tostring(ok1) .. " " .. m1 .. " " .. tostring(ok2) .. " " .. m2 ..
              " " .. coroutine.status(co) .. " " ..
              tostring(coroutine.isyieldable()))
    ''', "false oops false cannot resume dead coroutine dead false",
      ["false oops true nil dead false", "false oops false cannot resume dead coroutine suspended false",
       "false oops false cannot resume dead coroutine dead true"],
      "An error inside a coroutine kills it; resume returns false and the message instead of raising",
      """`coroutine.resume` never throws: a failure comes back as `false` plus the error value, and the coroutine is
      dead from then on. Resuming a dead coroutine fails with "cannot resume dead coroutine". In the main program
      nothing can be yielded, so `isyieldable` is false."""),

    q("wrap-as-for-iterator", r'''
        local gen = coroutine.wrap(function()
          coroutine.yield(1)
          coroutine.yield(2)
          coroutine.yield(nil)
          coroutine.yield(4)
        end)
        local out = {}
        for v in gen do out[#out + 1] = v end
        print(table.concat(out, ",") .. " " .. tostring(gen()))
    ''', "1,2 4", ["1,2,4 nil", "1,2,nil,4 dead", "1,2 nil"],
      "A for loop stops at the first nil it receives, even if the generator has more to give",
      """The generic `for` ends when the iterator returns nil as its first value. The third `yield(nil)` therefore
      stops the loop, leaving the coroutine suspended; calling `gen()` once more resumes it and returns 4."""),

    q("local-function-recursion", r'''
        local f = function(n)
          if n == 0 then return 0 end
          return n + (f and f(n - 1) or 100)
        end
        local function g(n)
          if n == 0 then return 0 end
          return n + g(n - 1)
        end
        print(f(3) .. " " .. g(3))
    ''', "103 6", ["6 6", "103 103", "3 6"],
      "local f = function ... does not see f inside its own body; local function f does",
      """In `local f = function ... end` the new local only comes into scope after the whole statement, so the `f`
      inside the body is the global `f`, which is nil: the function adds 100 and stops. `local function g` declares
      `g` first, so the recursion works and gives 3 + 2 + 1."""),

    q("xpcall-handler-and-arguments", r'''
        local function show(...)
          local t = { ... }
          for i = 1, #t do t[i] = tostring(t[i]) end
          return table.concat(t, ",")
        end
        print(show(xpcall(function(a, b) error(a .. b, 0) end,
                          function(m) return "H" .. m end, "x", "y")) .. " " ..
              show(xpcall(function(...) return select("#", ...) end, print,
                          1, nil)))
    ''', "false,Hxy true,2", ["false,xy true,2", "false,Hxy true,1", "true,Hxy true,2"],
      "xpcall passes extra arguments to the function, and the handler's result replaces the error",
      """After the function and the handler, `xpcall` takes arguments for the protected function, here "x" and "y".
      When it fails, the handler receives the error value and its return value ("Hxy") replaces it in the results.
      Counting the arguments of the second call shows that a trailing nil is passed on: 2."""),

    q("pcall-of-error-without-a-message", r'''
        local a = select("#", pcall(error))
        local ok, e = pcall(error, nil)
        local ok2, e2 = pcall(error, false)
        print(a .. " " .. tostring(ok) .. tostring(e) .. " " .. tostring(e2) ..
              " " .. type(select(2, pcall(error, 5))))
    ''', "2 falsenil false number", ["1 falsenil false number", "2 falsenil nil string",
                                     "2 truenil false number"],
      "error accepts any value, even nil or false, and pcall still reports a failure",
      """`error()` with no argument raises nil, so `pcall` returns two results: `false` and nil. `false` and a number
      are raised unchanged too: only string messages get a position prefix, and only when the level says so. The
      first result tells you that the call failed, never the type of the error value."""),

    q("utf8-codepoints-and-offsets", r'''
        local s = "h\u{e9}llo"
        local r = { utf8.codepoint(s, 1, -1) }
        r[#r + 1] = utf8.offset(s, 3)
        r[#r + 1] = utf8.len(s)
        r[#r + 1] = tostring(utf8.len(s, 3))
        r[#r + 1] = #utf8.char(8364)
        print(table.concat(r, " "))
    ''', "104 233 108 108 111 4 5 nil 3", ["104 233 108 108 111 3 5 nil 3",
                                          "104 195 169 108 108 111 4 5 nil 3",
                                          "104 233 108 108 111 4 6 3 3"],
      "utf8.offset returns a byte position; utf8.len fails when it starts inside a character",
      """The string has five characters but six bytes, because the accented letter takes two. `codepoint(s, 1, -1)`
      returns one number per character, and `utf8.offset(s, 3)` gives the byte where the third character starts,
      byte 4. Starting `utf8.len` at byte 3, the middle of a character, returns nil, and the euro sign encodes
      as three bytes."""),

    q("lazy-cache-with-rawset", r'''
        local calls = 0
        local sq = setmetatable({}, { __index = function(t, k)
          calls = calls + 1
          local v = k * k
          rawset(t, k, v)
          return v
        end })
        local r = { sq[3], sq[3], sq[4], rawget(sq, 5) == nil and "no5" or "has5" }
        print(table.concat(r, " ") .. " " .. calls)
    ''', "9 9 16 no5 2", ["9 9 16 no5 3", "9 9 16 has5 2", "9 9 16 no5 4"],
      "__index only runs for keys that are missing, so a rawset cache turns later reads into plain lookups",
      """The first `sq[3]` finds nothing, runs the function, stores 9 with `rawset` and returns it. The second
      read finds the stored value and never calls the function, so only 3 and 4 count. `rawget` shows that 5 was
      never computed, because a raw read does not trigger `__index`."""),

    q("newindex-runs-only-for-new-keys", r'''
        local log = {}
        local t = setmetatable({}, { __newindex = function(t, k, v)
          log[#log + 1] = k
          rawset(t, k, v)
        end })
        t.a = 1
        t.a = 2
        t.b = 3
        rawset(t, "c", 4)
        t.c = 5
        print(table.concat(log, ",") .. " " .. t.a .. t.c)
    ''', "a,b 25", ["a,a,b 25", "a,b,c 25", "a,b 15"],
      "__newindex is only called when the key is absent from the table itself",
      """The first assignment to `a` finds no key and calls the function, which stores the value with `rawset`. From
      then on `a` exists, so `t.a = 2` is a plain overwrite with no call. `rawset` bypasses the metamethod, so
      `c` is already present and its later assignment is also silent."""),

    q("overlapping-matches-with-find", r'''
        local s, n, pos = "aaaa", 0, 1
        while true do
          local i, j = s:find("aa", pos, true)
          if not i then break end
          n = n + 1
          pos = j + 1
        end
        local m, p = 0, 1
        while s:find("aa", p, true) do
          m = m + 1
          p = s:find("aa", p, true) + 1
        end
        print(n .. " " .. m .. " " .. select(2, s:gsub("aa", "")))
    ''', "2 3 2", ["3 3 2", "2 2 2", "2 3 3"],
      "Resuming the search after a match finds separate hits; start + 1 finds overlapping ones",

      """Moving the search position to just after the previous match (`j + 1`) skips over the shared letters, giving
      two matches in "aaaa". Moving it by one from where the match started lets matches overlap and finds three.
      `gsub` replaces matches from left to right without overlap, so it counts two."""),

)
