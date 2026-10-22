"""Gotchas, Odin (third deck): odin build, then run; portability notes are in langs.py (the `odin` entry).

New angles on the first two decks: how fmt prints (width flags that zero-pad, bad enum values, composites),
procedures (named and default parameters, groups, polymorphism, multiple returns, or_continue), unions, enumerated
arrays and swizzles, core:math and core:strings helpers. Maps are only looked up, never iterated.
"""

from __future__ import annotations

from .items import Item, make

q = make("odin")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ──────────────────────────────────────────────────────
    q("numeric-width-pads-with-zeros", r'''
        package main

        import "core:fmt"

        main :: proc() {
            fmt.printf("[%5d][%-5d][%5s][%-5s][%5v][%3d][%+d]\n",
                       42, 42, "ab", "ab", 42, 12345, 5)
        }
    ''', "[00042][42   ][   ab][ab   ][00042][12345][+5]",
      ["[   42][42   ][   ab][ab   ][   42][12345][+5]", "[00042][00042][   ab][ab   ][00042][12345][+5]",
       "[00042][42   ][00ab][ab   ][00042][ 12345][+5]"],
      "In Odin's printf a width on a number pads with zeros, while a width on a string pads with spaces",
      """Unlike C, `%5d` is zero-padded: 42 prints as 00042. A `-` flag switches to left alignment with trailing
      spaces. Strings are padded with spaces on either side, and a width never cuts a longer value (12345 stays whole).
      The same applies to `%v` of a number."""),

    q("rune-arithmetic-prints-as-character", r'''
        package main

        import "core:fmt"

        main :: proc() {
            r := 'a'
            r += 2
            fmt.println(r, int(r), 'a' + 1, rune(66), u8('c'))
        }
    ''', "c 99 b B 99", ["99 99 98 66 99", "c 99 98 B c", "c c b B 99"],
      "A rune prints as its character, and converting it to an integer type shows the code",
      """`r` is a rune, a distinct integer type that `println` shows as text, so adding 2 to 'a' prints c.
      `int(r)` is the number 99. `'a' + 1` is still a rune (b), `rune(66)` is B, and `u8('c')` is a byte, which
      prints as the number 99."""),

    q("if-init-is-visible-in-else", r'''
        package main

        import "core:fmt"

        main :: proc() {
            if v := 3; v > 5 {
                fmt.println("big", v)
            } else {
                fmt.println("small", v + 100)
            }
        }
    ''', "small 103", ["big 3", "small 3", "small 103 3"],
      "A variable declared in an if statement's init is in scope in every branch, including else",
      """`v := 3` is created before the condition and lives through the whole if/else chain. The condition is false,
      so the else branch runs and uses the same `v`: 3 + 100 = 103."""),

    q("float-to-int-truncates", r'''
        package main

        import "core:fmt"
        import "core:math"

        main :: proc() {
            f := -3.99
            fmt.println(int(f), int(math.floor(f)), int(math.round(f)),
                        int(math.ceil(f)))
        }
    ''', "-3 -4 -4 -3", ["-4 -4 -4 -3", "-3 -3 -4 -3", "-3 -4 -3 -3"],
      "Converting a float to an integer cuts off the fraction toward zero",
      """`int(-3.99)` drops the .99, so -3, and not the floor. `math.floor` goes down to -4, `math.round` goes to the
      nearest integer, -4, and `math.ceil` goes up to -3. The conversion is applied after those functions."""),

    q("labelled-break-and-continue", r'''
        package main

        import "core:fmt"

        main :: proc() {
            n := 0
            outer: for i in 0..<4 {
                for j in 0..<4 {
                    if j > i { continue outer }
                    if i == 3 { break outer }
                    n += 1
                }
            }
            fmt.println(n)
        }
    ''', "6", ["10", "3", "9"],
      "continue outer skips the rest of the inner loop and starts the next outer pass; break ends both",
      """For i = 0 only j = 0 counts, then j = 1 jumps to the next i. For i = 1 two pass, for i = 2 three pass: 1 + 2 + 3
      = 6. When i is 3 the first test passes for j = 0 and the `break outer` stops everything before anything is
      added."""),

    q("defer-in-a-loop-body", r'''
        package main

        import "core:fmt"

        main :: proc() {
            for i in 0..<2 {
                defer fmt.printf("d%d ", i)
                defer fmt.printf("e%d ", i)
                fmt.printf("b%d ", i)
            }
            fmt.println()
        }
    ''', "b0 e0 d0 b1 e1 d1", ["b0 b1 e1 d1 e0 d0", "b0 d0 e0 b1 d1 e1", "d0 e0 b0 d1 e1 b1"],
      "A defer in a loop body runs at the end of each pass, in last-in-first-out order",
      """The body is a scope of its own, left once per iteration, so its deferred calls run each time around
      and not at the end of the whole loop. Within one pass they run in reverse order: the later `defer`
      (`e`) before the earlier one (`d`)."""),

    # ── Medium ───────────────────────────────────────────────────────────
    q("type-switch-on-a-union", r'''
        package main

        import "core:fmt"

        V :: union { int, string }
        size :: proc(v: V) -> int {
            switch x in v {
            case int:    return x * 2
            case string: return len(x)
            case:        return -1
            }
        }

        main :: proc() {
            fmt.println(size(5), size("abc"), size(V{}), size(nil))
        }
    ''', "10 3 -1 -1", ["10 3 0 0", "5 3 -1 -1", "10 3 -1 3"],
      "In a type switch, x has the type of the matching case, and a case with no type matches nil",
      """`switch x in v` unwraps the union: inside `case int` the name `x` is an int, and inside `case string` it is a
      string. A case with no type is the nil case. `V{}` and `nil` are both the empty union, so both give -1."""),

    q("polymorphic-proc-keeps-the-type", r'''
        package main

        import "core:fmt"

        double :: proc(x: $T) -> T {
            return x * 2
        }

        main :: proc() {
            fmt.println(double(3), double(1.5), double(u8(200)))
        }
    ''', "6 3 144", ["6 3 400", "6 3.0 144", "6 3 200"],
      "$T is whatever type was passed, so the result wraps like that type; a whole float prints without .0",
      """For a u8 argument `T` is u8, so 200 * 2 wraps to 144 instead of growing to 400. For 1.5, T is a float and the
      result 3 is printed without a decimal part, as Odin does for whole-number floats."""),

    q("multiple-returns-spread-into-a-call", r'''
        package main

        import "core:fmt"

        pair :: proc() -> (int, int) { return 3, 4 }
        add :: proc(a, b: int) -> int { return a + b }

        main :: proc() {
            fmt.println(add(pair()), pair())
        }
    ''', "7 3 4", ["7 (3, 4)", "3 3 4", "7 7"],
      "A call that returns several values can be passed on as all the arguments of another call",
      """`add(pair())` spreads both results into the two parameters of `add`: 3 + 4. The last argument of
      `println` is another `pair()` call, which also spreads, so it contributes 3 and 4 as separate values."""),

    q("default-and-named-parameters", r'''
        package main

        import "core:fmt"

        f :: proc(a: int, b := 10, c := 20) -> int {
            return a + b * c
        }

        main :: proc() {
            fmt.println(f(1), f(1, c = 5), f(c = 1, a = 2), f(1, 2))
        }
    ''', "201 51 12 41", ["201 21 12 41", "201 51 12 61", "201 51 22 41"],
      "A named argument skips the parameters before it, and the others keep their defaults",
      """`f(1)` is 1 + 10 * 20. `f(1, c = 5)` keeps b = 10: 1 + 10 * 5 = 51. Named arguments may come in any order, so
      `f(c = 1, a = 2)` is 2 + 10 * 1. `f(1, 2)` sets b positionally and leaves c = 20: 1 + 2 * 20 = 41."""),

    q("procedure-group-picks-by-type", r'''
        package main

        import "core:fmt"

        add_i :: proc(a, b: int) -> string { return "int" }
        add_f :: proc(a, b: f64) -> string { return "f64" }
        add :: proc{add_i, add_f}

        main :: proc() {
            x := 2.0
            fmt.println(add(1, 2), add(1.5, 2), add(1, 2.5), add(1, int(x)))
        }
    ''', "int f64 f64 int", ["int int f64 int", "f64 f64 f64 int", "int f64 int int"],
      "A procedure group is resolved at compile time from the argument types",
      """Both literals in `add(1, 2)` fit an int, so the int version wins. `1.5` or `2.5` cannot be an int, so the
      float version is chosen even when the other argument is a whole number. `int(x)` is an int, so the first
      version is chosen again."""),

    q("enumerated-array-indexed-by-enum", r'''
        package main

        import "core:fmt"

        Color :: enum { Red, Green, Blue }

        main :: proc() {
            counts: [Color]int
            counts[.Blue] += 2
            counts[.Red] += 1
            fmt.println(counts, len(counts), counts[.Green])
        }
    ''', "[.Red = 1, .Green = 0, .Blue = 2] 3 0", ["[1, 0, 2] 3 0", "[.Red = 1, .Blue = 2] 2 0",
                                                   "[.Red = 1, .Green = 0, .Blue = 2] 3 1"],
      "An array indexed by an enum has one zeroed slot per case, and it prints with the case names",
      """`[Color]int` is an array with exactly three elements, one for each enum value, all starting at zero. It is
      indexed with the cases themselves, and printing shows each slot as `.Name = value`. Its length is the
      number of cases."""),

    q("array-swizzle-and-field-names", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a := [3]int{1, 2, 3}
            fmt.println(a.x, a.zx, a.zyx, a.r, a.xyz == a)
        }
    ''', "1 [3, 1] [3, 2, 1] 1 true", ["1 [3, 1] [3, 2, 1] 1 false", "1 [1, 3] [1, 2, 3] 1 true",
                                      "1 3 [3, 2, 1] 1 true"],
      "Small arrays have .x .y .z .w (and .r .g .b .a) fields, and several letters make a new array",
      """For arrays up to four elements, `x`, `y`, `z`, `w` name the elements by position, and `r`, `g`, `b`, `a` are
      aliases. Naming several at once, like `zx`, builds a new array in that order: [3, 1]. `a.xyz` is a copy of the
      whole array, so it is equal to `a`."""),

    q("offset-of-and-alignment", r'''
        package main

        import "core:fmt"

        S :: struct { a: u8, b: u32, c: u8 }

        main :: proc() {
            fmt.println(offset_of(S, a), offset_of(S, b), offset_of(S, c),
                        size_of(S), align_of(S))
        }
    ''', "0 4 8 12 4", ["0 1 5 6 1", "0 4 5 6 4", "0 1 5 12 4"],
      "Fields are aligned to their own size, so padding appears between them and at the end",
      """The u32 must start at a multiple of 4, so three padding bytes follow `a` and `b` lands at offset 4. `c` follows
      the four bytes of `b`, at 8. The struct's alignment is the largest field's (4), so its size is rounded up
      from 9 to 12."""),

    q("min-and-max-of-a-type", r'''
        package main

        import "core:fmt"

        main :: proc() {
            x := min(i8)
            y: u8 = 200
            fmt.println(max(u8), x, -x, max(i32), -y, ~y)
        }
    ''', "255 -128 -128 2147483647 56 55", ["255 -128 128 2147483647 56 55", "256 -128 -128 2147483647 56 55",
                                          "255 -128 -128 2147483647 -200 55"],
      "min(T) and max(T) give a type's limits, and negating the smallest value or an unsigned one wraps",
      """`max(u8)` is 255, and `min(i8)` is -128. Negating -128 would be +128, which an i8 cannot hold, so it wraps
      back to -128. Negating the u8 200 wraps to 256 - 200 = 56, and `~y` flips all bits: 255 - 200 = 55."""),

    q("math-mod-versus-remainder", r'''
        package main

        import "core:fmt"
        import "core:math"

        main :: proc() {
            fmt.println(math.mod(-7.5, 2.0), math.remainder(7.5, 2.0),
                        math.floor(2.7), math.pow(2.0, 10))
        }
    ''', "-1.5 -0.5 2 1024", ["0.5 -0.5 2 1024", "-1.5 1.5 2 1024", "-1.5 -0.5 3 1024"],
      "mod keeps the dividend's sign, like C's fmod, while remainder rounds the quotient to the nearest",
      """`math.mod(-7.5, 2.0)` truncates the quotient (-3.75 to -3), leaving -7.5 + 6 = -1.5. `math.remainder` rounds
      the quotient to the nearest whole number instead: 7.5 / 2 is 3.75, which rounds to 4, leaving 7.5 - 8 =
      -0.5. Whole-number floats print without a decimal part."""),

    q("bit-counting-helpers", r'''
        package main

        import "core:fmt"
        import "core:math/bits"

        main :: proc() {
            fmt.println(bits.count_ones(u8(0b1011)), bits.leading_zeros(u8(1)),
                        bits.trailing_zeros(u8(8)), bits.count_zeros(u8(0b1011)))
        }
    ''', "3 7 3 5", ["3 0 3 5", "4 7 3 5", "3 7 3 3"],
      "The helpers count bits within the width of the type given",
      """0b1011 has three bits set. A u8 holding 1 has seven zeros before the lowest bit, and 8 (0b1000) has
      three zeros after the highest one. Counting zeros uses all eight bits of the byte, so 8 - 3 = 5."""),

    q("strings-split-and-fields-edges", r'''
        package main

        import "core:fmt"
        import "core:strings"

        main :: proc() {
            parts := strings.split("a,,b", ",")
            empty := strings.split("", ",")
            words := strings.fields("  a  b ")
            defer delete(parts)
            defer delete(empty)
            defer delete(words)
            fmt.println(len(parts), len(empty), len(words), parts)
        }
    ''', '3 1 2 ["a", "", "b"]', ['2 0 2 ["a", "b"]', '3 0 2 ["a", "", "b"]', '3 1 3 ["a", "", "b"]'],
      "split keeps empty pieces, an empty string splits into one empty piece, and fields drops blanks",
      """`strings.split` cuts at every separator, so "a,,b" has an empty middle piece, and "" has exactly one piece,
      the empty string. `strings.fields` splits on runs of whitespace and ignores leading and trailing spaces, giving
      two words. The results are allocated, so they are freed with `delete`."""),

    q("slice-sort-and-reverse", r'''
        package main

        import "core:fmt"
        import "core:slice"

        main :: proc() {
            arr := [?]int{3, 1, 2}
            slice.sort(arr[:])
            before := arr
            slice.reverse(arr[:])
            fmt.println(before, arr, slice.contains(arr[:], 2))
        }
    ''', "[1, 2, 3] [3, 2, 1] true", ["[3, 2, 1] [3, 2, 1] true", "[1, 2, 3] [1, 2, 3] true",
                                      "[3, 1, 2] [2, 1, 3] true"],
      "Sorting a slice changes the array under it, and assigning a fixed array copies it",
      """`arr[:]` is a slice of the array, so `slice.sort` and `slice.reverse` work on the array's own elements.
      `before := arr` makes a separate copy at that moment, so it keeps the sorted order while `arr` is then
      reversed."""),

    q("println-of-composite-values", r'''
        package main

        import "core:fmt"

        Color :: enum { Red, Green, Blue }
        P :: struct { x, y: int }

        main :: proc() {
            p := P{y = 2}
            fmt.println([2][2]int{{1, 2}, {3, 4}}, Color.Green, &p, []int{1, 2})
        }
    ''', "[[1, 2], [3, 4]] Green &P{x = 0, y = 2} [1, 2]",
      ["[[1, 2], [3, 4]] 1 &P{x = 0, y = 2} [1, 2]", "[1, 2, 3, 4] Green P{x = 0, y = 2} [1, 2]",
       "[[1, 2], [3, 4]] Green 0xC000 [1, 2]"],
      "println shows enum case names, struct fields by name, and a pointer to a struct as &Struct{...}",
      """Nested arrays print as nested brackets, an enum value as its name, and a struct as `Name{field = value}`
      with unset fields zero. A pointer to a struct is not printed as an address but as `&` followed by the struct
      it points to."""),

    q("bad-enum-value-prints-a-marker", r'''
        package main

        import "core:fmt"

        Color :: enum { Red, Green, Blue }

        main :: proc() {
            c := Color.Red
            c = Color(int(c) + 1)
            fmt.println(c, Color(7), int(Color.Blue), c == .Green)
        }
    ''', "Green %!(BAD ENUM VALUE=7) 2 true", ["Green Color(7) 2 true", "Green 7 2 true",
                                              "1 %!(BAD ENUM VALUE=7) 2 true"],
      "Casting an integer to an enum is not checked, and printing a value that is no case shows a marker",
      """`Color(int(c) + 1)` steps from Red to Green, which prints by name. `Color(7)` is accepted, since the enum is
      just an integer underneath, but there is no case 7, so `println` writes `%!(BAD ENUM VALUE=7)` instead of a
      name."""),

    q("pop-clear-and-inject-at", r'''
        package main

        import "core:fmt"

        main :: proc() {
            dyn: [dynamic]int
            defer delete(dyn)
            append(&dyn, 1, 2, 3)
            last := pop(&dyn)
            inject_at(&dyn, 0, 9)
            n := len(dyn)
            clear(&dyn)
            fmt.println(last, n, len(dyn), dyn)
        }
    ''', "3 3 0 []", ["3 2 0 []", "1 3 0 []", "3 3 3 [9, 1, 2]"],
      "pop removes and returns the last element; inject_at inserts and shifts; clear only resets the length",
      """After appending 1, 2, 3, `pop` takes the 3, leaving two elements. `inject_at(&dyn, 0, 9)` inserts 9 at the front, so
      there are three again: [9, 1, 2]. `clear` sets the length to zero, which makes the array print as empty."""),

    q("or-continue-skips-the-pass", r'''
        package main

        import "core:fmt"

        half :: proc(n: int) -> (int, bool) {
            if n % 2 != 0 { return 0, false }
            return n / 2, true
        }
        main :: proc() {
            sum := 0
            for i in 1..=6 {
                h := half(i) or_continue
                sum += h
            }
            fmt.println(sum)
        }
    ''', "6", ["21", "9", "3"],
      "or_continue goes to the next loop pass when the call's last result is false or an error",
      """`half(i)` returns an extra bool. When it is false (for odd i) `or_continue` skips the rest of the loop body,
      and when it is true the first result is kept. Only 2, 4 and 6 contribute: 1 + 2 + 3 = 6."""),

    q("switch-range-cases", r'''
        package main

        import "core:fmt"

        cls :: proc(v: int) -> string {
            switch v {
            case 0:     return "zero"
            case 1..=5: return "low"
            case 6..<10: return "mid"
            case:       return "high"
            }
        }

        main :: proc() {
            fmt.println(cls(0), cls(5), cls(9), cls(10))
        }
    ''', "zero low mid high", ["zero low mid mid", "zero low low high", "zero mid mid high"],
      "..= includes the end of a case range and ..< excludes it; a case with no value is the default",
      """`1..=5` covers 1 through 5, so 5 is "low", while `6..<10` stops before 10, so 9 is "mid" and 10 falls through to
      the default case. The empty `case:` matches everything not listed."""),

    q("map-compound-assignment-creates-the-entry", r'''
        package main

        import "core:fmt"

        main :: proc() {
            m := make(map[string]int)
            defer delete(m)
            m["a"] += 5
            m["a"] += 1
            _, found := m["b"]
            m["b"] -= 1
            a, n := m["a"], len(m)
            delete_key(&m, "a")
            fmt.println(a, m["b"], n, found, "a" in m, len(m))
        }
    ''', "6 -1 2 false false 1",
      ["5 -1 2 false false 1", "6 -1 2 true false 1", "6 -1 1 false true 1"],
      "Assigning with += to a missing key starts from zero and creates the entry; merely reading does not",
      """`m["a"] += 5` reads the zero value for the missing key, adds 5 and stores it, so entries appear as soon as they are
      written. The lookup `m["b"]` before writing found nothing (found is false), but the `-=` afterwards creates
      it as -1, so the map has two entries. `delete_key` then removes `"a"`, leaving one."""),

    q("complex-numbers-are-built-in", r'''
        package main

        import "core:fmt"

        main :: proc() {
            z := complex(1, 2)
            fmt.println(z * z, real(z), imag(z), abs(complex(3, 4)))
        }
    ''', "-3+4i 1 2 5", ["3+4i 1 2 5", "-3+4i 1 2 25", "(-3+4i) 1 2 5"],
      "complex is a built-in type: (1+2i) squared is -3+4i, and abs gives the length",
      """Multiplying `1+2i` by itself gives 1 + 2i + 2i + 4i², which is -3 + 4i. `real` and `imag` read the two parts,
      and `abs` returns the magnitude, the square root of 3² + 4², which is 5. Whole-number floats print without
      a decimal point."""),

    q("unsigned-arithmetic-wraps", r'''
        package main

        import "core:fmt"

        main :: proc() {
            x: u8 = 200
            fmt.println(x / 3, x % 7, -x, ~x, x << 1, x >> 1)
        }
    ''', "66 4 56 55 144 100", ["66 4 -200 55 400 100", "66 4 56 55 400 100", "67 4 56 55 144 100"],
      "Every operation on a u8 stays inside 0 to 255, so negation and shifts wrap",
      """Integer division and remainder act as usual: 200 / 3 is 66 and 200 % 7 is 4. Negation wraps to 256 - 200 = 56,
      and `~x` flips the bits to give 55. Shifting left drops the bit that falls off the end: 400 - 256 = 144."""),
)
