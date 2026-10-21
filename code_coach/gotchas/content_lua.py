"""Gotchas, Lua: run by lua 5.4; portability notes are in langs.py (the `lua` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("lua")

ITEMS: tuple[Item, ...] = (
    q("division-is-always-float", r'''
        local parts = { 10 / 2, 7 // 2, 7 % -3, 2 ^ 3 }
        print(table.concat(parts, " "))
    ''', "5.0 3 -2 8.0", ["5 3 1 8", "5.0 3.0 -2 8", "5.0 3 1 8.0"],
      "/ and ^ always give floats; // keeps integers; % follows the divisor's sign",
      """In Lua 5.4 the `/` and `^` operators always produce a float, so they print as 5.0 and 8.0. `//` is floor
      division on integers and gives the integer 3. The modulo result has the sign of the second operand, so
      7 % -3 is -2."""),

    q("zero-and-empty-are-true", r'''
        local a = 0 and "zero"
        local b = "" and "empty"
        local c = nil and "nil"
        print(tostring(a) .. "/" .. tostring(b) .. "/" .. tostring(c))
    ''', "zero/empty/nil", ["nil/nil/nil", "zero/nil/nil", "nil/empty/nil"],
      "Only nil and false are false; 0 and the empty string are true",
      """`x and y` gives y when x is truthy and x when x is falsy. In Lua 0 and "" are truthy, so `a` and `b` are
      the strings after `and`. `nil` is falsy, so `c` is nil itself."""),

    q("string-sub-is-one-based", r'''
        local s = "hello"
        print(s:sub(2, 3) .. s:sub(-2) .. #s)
    ''', "ello5", ["elllo5", "llo5", "elo5"],
      "Positions start at 1 and the end index is inclusive; negatives count from the end",
      """`s:sub(2, 3)` is the 2nd through 3rd characters, "el". `s:sub(-2)` is the last two, "lo". `#s` is the
      length, 5. Joined, they make "ello5"."""),
)
