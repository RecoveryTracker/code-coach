"""Gotchas, Odin: odin build then run; portability notes are in langs.py (the `odin` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("odin")

ITEMS: tuple[Item, ...] = (
    q("remainder-versus-modulo", r'''
        package main

        import "core:fmt"

        main :: proc() {
            fmt.println(7 / 2, -7 / 2, -7 % 3, -7 %% 3)
        }
    ''', "3 -3 -1 2", ["3 -4 -1 2", "3 -3 2 2", "3 -3 -1 -1"],
      "% is the truncated remainder; %% is the floored modulo",
      """Odin has both. `%` pairs with truncating division, so -7 / 2 is -3 and -7 % 3 is -1. `%%` is the modulo
      that always takes the divisor's sign, which is why -7 %% 3 is 2."""),

    q("slices-are-views", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a := [4]int{1, 2, 3, 4}
            s := a[1:3]
            s[0] = 99
            fmt.println(a, len(s))
        }
    ''', "[1, 99, 3, 4] 2", ["[1, 2, 3, 4] 2", "[1, 99, 3, 4] 3", "[99, 2, 3, 4] 2"],
      "A slice is a window onto the array, so writing through it changes the array",
      """`a[1:3]` holds elements 1 and 2 of `a` by reference, not copies. `s[0]` is `a[1]`, so setting it to 99
      shows up in the array, while the slice itself has length 2."""),

    q("defer-runs-at-scope-end", r'''
        package main

        import "core:fmt"

        main :: proc() {
            x := 1
            {
                defer x *= 10
                x += 1
            }
            fmt.println(x)
        }
    ''', "20", ["11", "2", "10"],
      "defer waits for the end of the enclosing block, not the end of the line",
      """The `defer` is registered first but runs when the braces close. By then `x += 1` has made it 2, and the
      deferred statement multiplies that to 20. Order of statements and order of execution differ."""),
)
