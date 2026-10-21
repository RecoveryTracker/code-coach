"""Gotchas, Odin (second deck): zero values, ranges, casts, defer, unions, bit_sets. Same rules as content_odin.py."""

from __future__ import annotations

from .items import Item, make

q = make("odin")

ITEMS: tuple[Item, ...] = (
    # ── Basics that look easy ──────────────────────────────────────────────
    q("zero-values", r'''
        package main

        import "core:fmt"

        P :: struct { n: int, s: string, ok: bool, f: f32 }

        main :: proc() {
            p: P
            a: [3]int
            q: ^int
            fmt.println(p, a, q == nil)
        }
    ''', 'P{n = 0, s = "", ok = false, f = 0} [0, 0, 0] true',
      ['P{n = 0, s = nil, ok = false, f = 0} [0, 0, 0] true',
       'P{n = 0, s = "", ok = false, f = 0} [0, 0, 0] false',
       'P{n = 0, s = "", ok = false, f = 0.0} [0, 0, 0] true'],
      "Every declaration without a value is zeroed, never left uninitialised",
      """Odin sets numbers to 0, bools to false, strings to the empty string, and pointers to nil. Arrays and
      structs are zeroed field by field. Note that a float zero prints as plain 0."""),

    q("range-inclusive-exclusive", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a, b, c := 0, 0, 0
            for i in 0..<4 { a += i }
            for i in 0..=4 { b += i }
            hi := 0
            for _ in 4..<hi { c += 1 }
            fmt.println(a, b, c)
        }
    ''', "6 10 0", ["10 10 0", "6 6 0", "6 10 4"],
      "..< stops before the end, ..= includes it, and neither counts downwards",
      """`0..<4` visits 0, 1, 2, 3 and adds up to 6, while `0..=4` also visits 4 and gives 10. A range whose
      start is above its end is simply empty, so `4..<0` runs zero times."""),

    q("slice-bounds", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a := [5]int{10, 20, 30, 40, 50}
            s := a[1:4]
            t := s[1:]
            u := a[:2]
            fmt.println(len(s), len(t), len(u), t[0], u[1])
        }
    ''', "3 2 2 30 20", ["4 3 2 30 20", "3 2 2 20 20", "3 2 3 30 10"],
      "a[lo:hi] excludes hi, and a slice of a slice is relative to the first one",
      """`a[1:4]` is the elements at 1, 2 and 3: 20, 30, 40. Slicing it again with `[1:]` starts at its own
      element 1, which is 30, and leaves two. `a[:2]` is 10 and 20."""),

    q("float-printing", r'''
        package main

        import "core:fmt"

        main :: proc() {
            x := 2.5
            fmt.println(x * 2, x + x / 5, 1e3, f32(0.1) + f32(0.2))
        }
    ''', "5 3 1000 0.3", ["5.0 3.0 1000.0 0.3", "5 3 1000 0.30000001", "5 3.0 1000 0.3"],
      "Odin prints a float that is a whole number without a decimal point",
      """Unlike most languages, `fmt.println` shows 5.0 as `5` and 1e3 as `1000`. The value is still a float. For
      an f32 the shortest text that identifies the result of 0.1 + 0.2 is 0.3."""),

    q("untyped-constant-division", r'''
        package main

        import "core:fmt"

        main :: proc() {
            x :: 5
            y: f32 = x / 2
            z: f32 = 5.0 / 2
            w: f32 = 5
            fmt.println(y, z, w / 2)
        }
    ''', "2 2.5 2.5", ["2.5 2.5 2.5", "2 2 2.5", "2.5 2.5 2"],
      "Constants divide as integers if both are integer constants, whatever they end up as",
      """`x` and `2` are untyped integer constants, so `x / 2` is folded to the integer 2 first and only then
      converted to an f32. Writing `5.0` or giving the variable a float type first makes the division
      floating point."""),

    q("integer-wraps-silently", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a: u8 = 250
            a += 10
            b: i8 = 127
            b += 1
            c: u8
            c -= 1
            fmt.println(a, b, c)
        }
    ''', "4 -128 255", ["260 128 -1", "4 -128 -1", "4 128 255"],
      "Fixed-size integers wrap around in Odin; there is no overflow panic",
      """250 + 10 does not fit in a u8, so only the low eight bits are kept: 4. Likewise 127 + 1 in an i8 becomes
      -128, and subtracting 1 from an unsigned 0 gives 255."""),

    q("shadowing-in-blocks", r'''
        package main

        import "core:fmt"

        main :: proc() {
            x := 10
            {
                x := 20
                x += 1
            }
            if x := 5; x > 1 {
                x += 100
            }
            fmt.println(x)
        }
    ''', "10", ["21", "11", "115"],
      "A := inside a nested block or an if header makes a new variable",
      """Both inner `x` variables are brand new names that hide the outer one until their block ends. The
      additions change those copies, and the outer x is still 10 afterwards."""),

    q("for-in-value-versus-reference", r'''
        package main

        import "core:fmt"

        main :: proc() {
            arr := [3]int{1, 2, 3}
            sum := 0
            for v in arr { sum += v }
            for &v in arr { v *= 2 }
            for v, i in arr { sum += v * i }
            fmt.println(sum, arr)
        }
    ''', "22 [2, 4, 6]", ["22 [1, 2, 3]", "16 [2, 4, 6]", "28 [2, 4, 6]"],
      "for v in x gives copies; only for &v can change the elements",
      """The first loop sums 1 + 2 + 3 = 6. The second uses `&v`, a reference, and doubles the array in place.
      The third multiplies each new value by its index: 0 + 4 + 12 = 16, so the total is 22."""),

    q("named-results-start-zeroed", r'''
        package main

        import "core:fmt"

        f :: proc(x: int) -> (n: int, ok: bool) {
            if x > 0 { n, ok = x * 2, true }
            return
        }

        main :: proc() {
            a, ok1 := f(3)
            b, ok2 := f(-3)
            fmt.println(a, ok1, b, ok2)
        }
    ''', "6 true 0 false", ["6 true -6 false", "6 true -3 false", "6 true 0 true"],
      "Named results start at zero, and a bare return hands back whatever they hold",
      """In the second call the `if` is skipped, so `n` and `ok` still have their zero values and the bare
      `return` returns them: 0 and false."""),

    q("map-missing-key", r'''
        package main

        import "core:fmt"

        main :: proc() {
            m := make(map[string]int)
            defer delete(m)
            m["a"] = 1
            v, ok := m["z"]
            fmt.println(m["z"], v, ok, len(m))
        }
    ''', "0 0 false 1", ["0 0 false 2", "0 0 true 1", "1 1 false 1"],
      "Reading a missing key gives the zero value and does not add the key",
      """A lookup of an absent key returns 0 for an int map, and the second result tells you it was not found.
      Only an assignment creates a key, so the map still has one entry."""),

    q("or-else-versus-zero-value", r'''
        package main

        import "core:fmt"

        main :: proc() {
            m := make(map[string]int)
            defer delete(m)
            m["a"] = 0
            x := m["a"] or_else 99
            y := m["b"] or_else 99
            fmt.println(x, y, len(m))
        }
    ''', "0 99 1", ["99 99 1", "0 99 2", "0 0 1"],
      "or_else looks at whether the key was found, not at whether the value is zero",
      """The key "a" exists and holds 0, so `or_else` keeps 0. Only the missing key "b" falls back to 99. The
      lookup itself does not insert anything, so the map still has one entry."""),

    q("switch-needs-fallthrough", r'''
        package main

        import "core:fmt"

        main :: proc() {
            n := 0
            switch 1 {
            case 1:
                n += 1
                fallthrough
            case 2: n += 10
            case 3: n += 100
            }
            fmt.println(n)
        }
    ''', "11", ["111", "1", "10"],
      "A case ends at its own end; only an explicit fallthrough enters the next one",
      """Odin cases do not run into each other by default, unlike C. The `fallthrough` makes case 1 continue into
      case 2 and no further, so n is 1 + 10 = 11."""),

    q("string-bytes-and-runes", r'''
        package main

        import "core:fmt"
        import "core:unicode/utf8"

        main :: proc() {
            s := "héllo"
            n := utf8.rune_count_in_string(s)
            fmt.println(len(s), n, s[1], s[1:3] == "é")
        }
    ''', "6 5 195 true", ["5 5 233 true", "6 5 195 false", "5 5 195 true"],
      "len counts bytes, indexing gives a byte, and slicing cuts at byte positions",
      """The accented letter takes two bytes, so `len` is 6 although there are 5 characters. `s[1]` is the first
      of those two bytes, 195, not a character. The slice `s[1:3]` covers both bytes, so it equals the whole
      letter."""),

    q("rune-iteration-indexes", r'''
        package main

        import "core:fmt"

        main :: proc() {
            s := "héllo"
            count, last := 0, 0
            for _, i in s {
                count += 1
                last = i
            }
            fmt.println(count, last, len(s))
        }
    ''', "5 5 6", ["6 5 6", "5 4 5", "5 4 6"],
      "Looping over a string visits runes, and the index is the byte offset",
      """`for r, i in s` decodes UTF-8, so the loop runs once per character: 5 times. The index counts bytes,
      so after the two-byte letter the offsets jump: 0, 1, 3, 4, 5. The last one is 5, and the string is 6 bytes
      long."""),

    # ── Defer ──────────────────────────────────────────────────────────────
    q("defer-only-after-its-line", r'''
        package main

        import "core:fmt"

        f :: proc(x: int) -> int {
            defer fmt.print("f ")
            if x > 0 { return 1 }
            defer fmt.print("g ")
            return 2
        }

        main :: proc() {
            a, b := f(1), f(0)
            fmt.println(a, b)
        }
    ''', "f g f 1 2", ["f f g 1 2", "f g f f 1 2", "f g 1 2"],
      "A defer counts only if execution reached it before the function returned",
      """For `f(1)` the early return happens before the second defer is registered, so only `f` runs. For
      `f(0)` both are registered and they run in reverse order: g, then f."""),

    q("defer-cannot-change-result", r'''
        package main

        import "core:fmt"

        f :: proc() -> (r: int) {
            defer r *= 2
            r = 5
            return r + 1
        }
        g :: proc() -> (r: int) {
            defer r += 100
            return
        }
        main :: proc() {
            fmt.println(f(), g())
        }
    ''', "6 0", ["12 100", "6 100", "12 0"],
      "In Odin the result is copied out before the deferred statements run",
      """Go would let a deferred statement change a named result, but Odin returns the values first and runs the
      defer afterwards. So `f` returns the 6 it computed, not 12, and `g` returns 0, not 100."""),

    # ── Operators and numbers ──────────────────────────────────────────────
    q("bitand-binds-like-multiply", r'''
        package main

        import "core:fmt"

        main :: proc() {
            n := 5
            a := 2 + 3 & 1
            b := n ~ 3
            c := 6 &~ 3
            d := 1 | 2 * 4
            fmt.println(a, b, c, d, ~n)
        }
    ''', "3 6 4 9 -6", ["1 6 4 9 -6", "3 6 2 9 -6", "3 6 4 9 -5"],
      "& ranks with *, | with +, ~ is xor, and &~ clears bits",
      """In Odin `&` binds tighter than `+`, so `2 + 3 & 1` is 2 + (3 & 1) = 3 (C reads it the other way). `5 ~ 3`
      is exclusive or, 6. `6 &~ 3` clears bits 0 and 1 of 6 and leaves 4. `|` ranks with `+`, so 1 | 8 is 9, and
      a lone `~5` flips every bit to give -6."""),

    q("shift-by-the-width", r'''
        package main

        import "core:fmt"

        main :: proc() {
            one: u8 = 1
            n: uint = 8
            m: int = -8
            fmt.println(one << n, one << 7, m >> 1)
        }
    ''', "0 128 -4", ["256 128 -4", "1 128 -4", "0 128 -3"],
      "Shifting by the full width of the type pushes every bit out, and >> keeps the sign",
      """A u8 has only 8 bits, so `1 << 8` leaves nothing and gives 0 rather than 256 or an undefined result.
      `1 << 7` is 128, and shifting a negative signed number right copies the sign bit, so -8 >> 1 is -4."""),

    q("cast-versus-transmute", r'''
        package main

        import "core:fmt"

        main :: proc() {
            f: f32 = 1.5
            x := 300
            fmt.println(int(f), transmute(u32)f, u8(x))
        }
    ''', "1 1069547520 44", ["2 1069547520 44", "1 1 44", "1 1069547520 255"],
      "A conversion changes the value; transmute keeps the bits",
      """`int(f)` converts 1.5 to the integer 1, dropping the fraction. `transmute` reinterprets the same 32 bits
      as an integer, giving the IEEE pattern 0x3FC00000 = 1069547520. `u8(300)` keeps only the low byte: 44."""),

    q("cast-before-divide", r'''
        package main

        import "core:fmt"

        main :: proc() {
            n := 7
            fmt.println(f64(n) / 2, f64(n / 2), n / 2 * 2, n / 2.0)
        }
    ''', "3.5 3 6 3", ["3.5 3 6 3.5", "3.5 3.5 6 3", "3 3 6 3"],
      "Where the conversion sits decides whether the division is integer or float",
      """`f64(n) / 2` converts first and divides as floats: 3.5. `f64(n / 2)` divides the integers first, so 3,
      and only then converts. The constant `2.0` is a whole number, so it converts to an int, and `n / 2.0`
      is still integer division: 3."""),

    q("untyped-expression-folding", r'''
        package main

        import "core:fmt"

        main :: proc() {
            fmt.println(7 / 2 * 2.0, 7.0 / 2 * 2)
        }
    ''', "6 7", ["7 7", "6 6", "7 6"],
      "Constant expressions fold step by step, and whole-number steps divide as integers",
      """In `7 / 2 * 2.0` the first step is a division of two integer constants, which gives 3; times 2.0 is 6.
      In `7.0 / 2 * 2` the first step is a float division, 3.5, and the product is 7. Both print without a
      decimal point."""),

    q("size-of-struct-padding", r'''
        package main

        import "core:fmt"

        S :: struct { a: u8, b: u32, c: u8 }
        T :: struct #packed { a: u8, b: u32, c: u8 }

        main :: proc() {
            fmt.println(size_of(S), size_of(T), size_of([3]i16), size_of(bool))
        }
    ''', "12 6 6 1", ["6 6 6 1", "8 6 6 1", "12 6 3 1"],
      "Fields stay in the order written, so padding adds up; #packed removes it",
      """Odin does not reorder fields. The u32 must start at a multiple of 4, so there are 3 bytes of padding
      after `a` and again after `c` to round the struct up to a multiple of 4: 12 bytes in all. `#packed` drops
      the padding and leaves 1 + 4 + 1 = 6."""),

    q("min-max-clamp-abs", r'''
        package main

        import "core:fmt"

        main :: proc() {
            lo := clamp(-4, 0, 10)
            hi := clamp(15, 0, 10)
            fmt.println(lo, hi, abs(-5), min(3, 1, 2), max(-3, -7))
        }
    ''', "0 10 5 1 -3", ["-4 15 5 1 -3", "0 10 5 3 -7", "10 0 5 1 -3"],
      "clamp(x, lo, hi) takes the value first, and min and max accept any number of arguments",
      """`clamp(-4, 0, 10)` pulls -4 up to the lower limit 0, and 15 down to 10. `min` and `max` are built in
      and take several arguments: the smallest of 3, 1, 2 is 1, and the largest of -3 and -7 is -3."""),

    q("float-edge-values", r'''
        package main

        import "core:fmt"

        main :: proc() {
            z := 0.0
            nan := z / z
            fmt.println(1 / z, -1 / z, nan == nan, nan != nan, nan < 1)
        }
    ''', "+Inf -Inf false true false", ["+Inf -Inf true false false",
      "+Inf -Inf false false false", "+Inf -Inf false true true"],
      "Float division by zero gives infinity, and NaN is not equal even to itself",
      """Dividing a non-zero float by zero is +Inf or -Inf, not a crash. 0.0 / 0.0 is NaN, which compares false
      with everything, including itself, so only `nan != nan` is true."""),

    q("round-floor-trunc", r'''
        package main

        import "core:fmt"
        import "core:math"

        main :: proc() {
            x := 2.5
            fmt.println(math.round(x), math.round(-x), math.floor(-x),
                        math.trunc(-x), math.ceil(-x))
        }
    ''', "3 -3 -3 -2 -2", ["2 -2 -3 -2 -2", "3 -3 -2 -2 -3", "3 -2 -3 -2 -2"],
      "round sends halves away from zero; floor, trunc and ceil differ only below zero",
      """`math.round` has no banker's rule: 2.5 becomes 3 and -2.5 becomes -3. For -2.5 `floor` goes down to -3,
      while `trunc` and `ceil` both go up toward zero to -2."""),

    q("parse-int-strictness", r'''
        package main

        import "core:fmt"
        import "core:strconv"

        main :: proc() {
            _, a := strconv.parse_int("12abc")
            _, b := strconv.parse_int("  7")
            d, ok := strconv.parse_int("0x1f", 0)
            e, ok2 := strconv.parse_int("1_000", 0)
            fmt.println(a, b, d, ok, e, ok2)
        }
    ''', "false false 31 true 1000 true", ["true false 31 true 1000 true",
      "false true 31 true 1000 true", "false false 0 false 1000 true"],
      "parse_int wants the whole string; base 0 reads prefixes and underscores",
      """Trailing junk and leading spaces make the second result false. With base 0 the `0x` prefix selects
      hexadecimal and underscores are allowed as separators, so "0x1f" is 31 and "1_000" is 1000."""),

    # ── Arrays, slices and collections ─────────────────────────────────────
    q("array-assignment-copies", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a := [3]int{1, 2, 3}
            b := a
            b[0] = 9
            c := a[:]
            c[1] = 7
            fmt.println(a, b, c)
        }
    ''', "[1, 7, 3] [9, 2, 3] [1, 7, 3]", ["[1, 2, 3] [9, 2, 3] [1, 7, 3]",
      "[9, 7, 3] [9, 2, 3] [9, 7, 3]", "[1, 7, 3] [9, 7, 3] [1, 7, 3]"],
      "A fixed array is a value that is copied on assignment; a slice shares the memory",
      """`b := a` copies all three elements, so changing b leaves a alone. `a[:]` is a slice that points at a's own
      elements, so writing through `c` changes `a`, and `c` always shows what a holds."""),

    q("array-programming", r'''
        package main

        import "core:fmt"

        main :: proc() {
            b := [?]int{1, 2, 3}
            c := b * 2 + b
            fmt.println(c, b == [3]int{1, 2, 3}, len(c))
        }
    ''', "[3, 6, 9] true 3", ["[3, 6, 9] false 3", "[2, 4, 6, 1, 2, 3] true 6", "[2, 4, 6] true 3"],
      "Arithmetic and == work on whole fixed arrays, element by element",
      """Operators on fixed arrays apply to each element: `b * 2` is [2, 4, 6] and adding b gives [3, 6, 9]. `==`
      compares all the elements and gives one bool. It does not concatenate, so the length stays 3."""),

    q("tuple-assignment-order", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a, b := 1, 2
            a, b = b, a + b
            a, b = b, a + b
            fmt.println(a, b)
        }
    ''', "3 5", ["4 8", "2 3", "5 8"],
      "In a, b = x, y both right-hand sides are evaluated before either variable changes",
      """Round one uses the old values: a becomes 2 and b becomes 1 + 2 = 3. Round two gives a = 3 and b = 2 + 3 =
      5. Doing the assignments one after another would have used the updated a for b."""),

    q("unordered-remove-moves-last", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a: [dynamic]int
            defer delete(a)
            append(&a, 1, 2, 3, 4)
            unordered_remove(&a, 1)
            first := len(a)
            ordered_remove(&a, 0)
            fmt.println(first, a)
        }
    ''', "3 [4, 3]", ["3 [3, 4]", "3 [1, 3]", "3 [2, 3]"],
      "unordered_remove fills the gap with the last element; ordered_remove shifts the rest",
      """Removing index 1 with `unordered_remove` copies the last element, 4, into that place: [1, 4, 3]. Then
      `ordered_remove(&a, 0)` removes the 1 and moves everything left, which gives [4, 3]."""),

    q("copy-returns-count", r'''
        package main

        import "core:fmt"

        main :: proc() {
            src := [?]int{1, 2, 3, 4, 5}
            dst: [3]int
            n := copy(dst[:], src[:])
            m := copy(dst[1:], src[3:])
            fmt.println(n, m, dst)
        }
    ''', "3 2 [1, 4, 5]", ["5 2 [1, 4, 5]", "3 2 [1, 2, 3]", "3 2 [4, 5, 3]"],
      "copy moves as many elements as the shorter slice has, and returns that number",
      """The destination holds 3 elements, so only 1, 2, 3 are copied and `n` is 3, not 5. The second copy puts
      the two elements 4 and 5 into the last two places of `dst`, leaving [1, 4, 5]."""),

    q("make-with-length", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a := make([dynamic]int, 3)
            b := make([dynamic]int, 0, 3)
            defer delete(a)
            defer delete(b)
            append(&a, 7)
            append(&b, 7)
            fmt.println(len(a), len(b), a[0], a[3])
        }
    ''', "4 1 0 7", ["1 1 7 7", "4 4 0 7", "3 1 0 7"],
      "make with one size creates that many zero elements; the second size is only capacity",
      """`make([dynamic]int, 3)` starts with 3 zeros, so appending makes it 4 long and the 7 lands at index 3.
      `make([dynamic]int, 0, 3)` reserves room for 3 but starts empty, so one append leaves it 1 long."""),

    q("reserve-versus-resize", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a: [dynamic]int
            defer delete(a)
            reserve(&a, 10)
            n := len(a)
            resize(&a, 3)
            fmt.println(n, cap(a) >= 10, len(a), a[2])
        }
    ''', "0 true 3 0", ["10 true 3 0", "0 true 10 0", "0 false 3 0"],
      "reserve only buys room; resize changes the length and fills with zeros",
      """After `reserve(&a, 10)` the capacity is at least 10 but the length is still 0. `resize(&a, 3)` then
      makes the array 3 long with new elements set to zero, so `a[2]` is 0."""),

    q("pointer-deref", r'''
        package main

        import "core:fmt"

        main :: proc() {
            x := 10
            p := &x
            p^ += 5
            q := p
            q^ *= 2
            y := p^
            y += 1
            fmt.println(x, y)
        }
    ''', "30 31", ["15 16", "30 30", "31 31"],
      "p^ is the variable itself, while y := p^ copies its value",
      """Both pointers refer to x, so adding 5 and then doubling gives 30. `y := p^` takes a copy, so adding 1 to
      y gives 31 and leaves x alone."""),

    q("using-field-promotion", r'''
        package main

        import "core:fmt"

        Vec :: struct { x, y: int }
        Entity :: struct { using pos: Vec, hp: int }

        main :: proc() {
            e := Entity{pos = {1, 2}, hp = 3}
            e.x += 10
            p := e.pos
            p.y = 99
            fmt.println(e.pos.x, e.y, p.y)
        }
    ''', "11 2 99", ["1 2 99", "11 99 99", "11 2 2"],
      "using makes the inner fields reachable directly, but it is still one embedded struct",
      """`e.x` is a shortcut for `e.pos.x`, so adding 10 changes the embedded vector to 11. `p := e.pos` is a
      copy of the vector, so setting `p.y` to 99 leaves `e.y` at 2."""),

    # ── Tagged values, enums and bit sets ──────────────────────────────────
    q("union-nil-and-assertion", r'''
        package main

        import "core:fmt"

        V :: union { int, string }

        main :: proc() {
            a: V
            b: V = 5
            c: V = "hi"
            n, ok := c.(int)
            m, ok2 := b.(int)
            fmt.println(a == nil, n, ok, m, ok2)
        }
    ''', "true 0 false 5 true", ["false 0 false 5 true", "true 0 true 5 true", "true 2 false 5 true"],
      "A union starts out nil, and v.(T), with two results, tests the variant without a crash",
      """With no initial value the union holds nothing, so it equals `nil`. Asking for the wrong variant with
      `c.(int)` returns that type's zero value and false instead of crashing, while `b.(int)` finds the 5."""),

    q("enum-explicit-values", r'''
        package main

        import "core:fmt"

        Color :: enum { Red, Green = 5, Blue }

        main :: proc() {
            c: Color
            d := Color.Blue
            fmt.println(c, int(d), Color(5), c == .Red)
        }
    ''', "Red 6 Green true", ["Red 2 Green true", "Red 6 Blue true", "0 6 Green true"],
      "An enum prints its name, and counting resumes after an explicit value",
      """An uninitialised enum is the value 0, which is `Red`. `Green` is given 5, so `Blue` is 6, not 2.
      Converting the integer 5 back gives `Green`, and `println` shows names, not numbers."""),

    q("bit-set-operations", r'''
        package main

        import "core:fmt"

        Flag :: enum { A, B, C }

        main :: proc() {
            f := bit_set[Flag]{.A, .C}
            g := f ~ {.A, .B}
            hasb := .B in f
            fmt.println(hasb, card(f), g, transmute(u8)f)
        }
    ''', "false 2 bit_set[Flag]{B, C} 5", ["true 2 bit_set[Flag]{B, C} 5",
      "false 2 bit_set[Flag]{B} 5", "false 2 bit_set[Flag]{B, C} 3"],
      "A bit_set is a set stored as bits: in tests membership, ~ is symmetric difference",
      """`.B in f` asks whether B is a member, and it is not. `card` counts the 2 members. `f ~ {.A, .B}` keeps
      the flags that are in exactly one of the sets, which are B and C. Memory holds bit 0 (A) and bit 2 (C),
      0b101 = 5."""),

    # ── Control flow and library ───────────────────────────────────────────
    q("three-clause-loop-modified", r'''
        package main

        import "core:fmt"

        main :: proc() {
            i, count := 0, 0
            for ; i < 3; i += 1 {
                i += 1
                count += 1
            }
            fmt.println(count, i)
        }
    ''', "2 4", ["3 3", "2 3", "3 4"],
      "The body can change the loop counter, and the post statement still runs",
      """Pass 1: i is 0, the body makes it 1, the post step makes it 2. Pass 2: i is 2 < 3, the body makes it 3,
      the post step makes it 4, and the test fails. That is 2 passes and a final i of 4."""),

    q("string-ordering", r'''
        package main

        import "core:fmt"

        main :: proc() {
            a, b, c := "10", "9", "Z"
            fmt.println(a < b, c < "a", "" < c, "ab" < "a", "abc" < "abd")
        }
    ''', "true true true false true", ["false true true false true", "true false true false true",
      "true true true true true"],
      "Strings compare byte by byte, so '10' < '9' and capitals come before lower case",
      """The first byte of '10' is '1', which is below '9', so the whole string is smaller. 'Z' is 90 and 'a' is
      97. An empty string is smaller than any other, and a longer string is larger than its own prefix."""),

    q("or-return-passes-failure-up", r'''
        package main

        import "core:fmt"
        half :: proc(n: int) -> (int, bool) {
            if n % 2 != 0 { return 0, false }
            return n / 2, true
        }
        quarter :: proc(n: int) -> (r: int, ok: bool) {
            h := half(n) or_return
            return half(h)
        }
        main :: proc() {
            a, ok1 := quarter(8)
            b, ok2 := quarter(6)
            fmt.println(a, ok1, b, ok2)
        }
    ''', "2 true 0 false", ["2 true 3 true", "2 true 3 false", "2 true 0 true"],
      "or_return exits with the failure; a plain return half(h) just passes the second call's pair on",
      """`quarter(8)` halves twice: 4, then 2. For 6 the first half succeeds with 3, but the second `half(3)`
      fails and `return half(h)` hands back its (0, false). The 3 never reaches the caller."""),

    q("strings-index-and-count", r'''
        package main

        import "core:fmt"
        import "core:strings"

        main :: proc() {
            i := strings.index("hello", "l")
            j := strings.index("hello", "z")
            n := strings.count("aaa", "aa")
            fmt.println(i, j, n, strings.contains("abc", ""))
        }
    ''', "2 -1 1 true", ["2 0 2 true", "2 -1 2 true", "2 -1 1 false"],
      "index returns -1 when nothing is found, and count does not overlap its matches",
      """`strings.index` reports the first position, 2, and -1 for a missing text, not 0. In "aaa" the pattern
      "aa" matches once; after consuming two letters only one is left, so the count is 1. Every string contains
      the empty string."""),
)
