"""Gotchas, Go, the third helping: fmt's odd corners, receivers and slices through functions, and the newer stdlib.

Same rules as content_go.py: package main, built with `go build`, one printed line, no map ranging without a sort.
The registry bans goroutines, `sync`, `select` and `time`, so the only channels here are buffered ones used from a
single goroutine. Fresh ground compared with the second deck: how fmt prints values and mistakes, which methods a
pointer or a value gets, how a slice passed to a function behaves, package initialisation, and the `slices` package.
"""

from __future__ import annotations

from .items import Item, make

q = make("go")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ───────────────────────────────────────────────────────
    q("tagless-switch-first-true", r'''
        package main

        import "fmt"

        func main() {
            x, r := 7, ""
            switch {
            case x > 1: r = "a"
            case x > 5: r = "b"
            default: r = "c"
            }
            fmt.Println(r)
        }
    ''', "a", ["b", "ab", "c"],
      "A switch with no tag takes the first case that is true, then stops",
      """Both `x > 1` and `x > 5` hold for 7, but Go checks the cases from the top and runs only the first
      match. There is no fallthrough unless you write the keyword."""),

    q("nil-values-print", r'''
        package main

        import "fmt"

        func main() {
            var p *int
            var s []int
            var m map[string]int
            var e error
            fmt.Println(p, s, m, e, len(s), len(m))
        }
    ''', "<nil> [] map[] <nil> 0 0",
      ["nil nil nil nil 0 0", "<nil> <nil> <nil> <nil> 0 0", "<nil> [] {} <nil> 0 0"],
      "Println shows a nil pointer and nil error as <nil>, but a nil slice and map as empty",
      """A nil slice prints like an empty one, `[]`, and a nil map like an empty map, `map[]`, and `len` of both is
      0. Only pointers and interfaces such as `error` print as `<nil>`."""),

    q("string-conversion-copies", r'''
        package main

        import "fmt"

        func main() {
            b := []byte("abc")
            s := string(b)
            b[0] = 'X'
            t := string(b)
            fmt.Println(s, t)
        }
    ''', "abc Xbc", ["Xbc Xbc", "abc abc", "Xbc abc"],
      "Converting between string and []byte copies the data",
      """Strings are immutable, so `string(b)` must take its own copy of the bytes. Changing `b` afterwards does
      not affect `s`, and the second conversion sees the new first byte."""),

    q("map-of-structs-copy", r'''
        package main

        import "fmt"

        type C struct{ n int }

        func main() {
            m := map[string]C{"a": {1}}
            c := m["a"]
            c.n = 5
            p := map[string]*C{"a": {1}}
            p["a"].n = 5
            fmt.Println(m["a"].n, p["a"].n)
        }
    ''', "1 5", ["5 5", "1 1", "5 1"],
      "Reading a struct from a map gives a copy; a pointer in a map shares the struct",
      """`c := m["a"]` copies the struct, so changing `c` leaves the map alone (and `m["a"].n = 5` would not even
      compile). With `*C` values the map holds pointers, and the assignment goes through to the shared struct."""),

    q("strings-cut", r'''
        package main

        import (
            "fmt"
            "strings"
        )

        func main() {
            b, a, f := strings.Cut("k=v=w", "=")
            b2, a2, f2 := strings.Cut("kvw", "=")
            fmt.Printf("%q %q %v %q %q %v\n", b, a, f, b2, a2, f2)
        }
    ''', '"k" "v=w" true "kvw" "" false',
      ['"k" "v" true "kvw" "" false', '"k" "v=w" true "" "" false', '"k" "v=w" true "kvw" "kvw" false'],
      "Cut splits at the first separator only, and a miss returns the whole string and false",
      """Everything after the first `=` stays together in `after`. When the separator is not found, `before` is the
      whole input, `after` is empty and the boolean is false."""),

    q("slice-print-forms", r'''
        package main

        import "fmt"

        func main() {
            s := []string{"a b", "c"}
            fmt.Println(s, []byte("hi"), [2]bool{true}, []string{})
        }
    ''', "[a b c] [104 105] [true false] []",
      ["[[a b] [c]] [104 105] [true false] []", "[a b c] hi [true false] []",
       "[a b c] [104 105] [true] []"],
      "%v prints elements separated by spaces, so strings with spaces blur together; bytes are numbers",
      """Println writes each element with `%v` and puts a space between them, with no quotes, so "a b" and "c" look
      like three words. A byte slice prints as numbers (use `%s` for text), and an array always shows every
      element, including the zero values."""),

    q("percent-t-of-constants", r'''
        package main

        import "fmt"

        func main() {
            fmt.Printf("%T %T %T %T\n", 1, 1.0, 'a', 2+3i)
        }
    ''', "int float64 int32 complex128",
      ["int float32 rune complex64", "int float64 rune complex128", "int float64 int32 complex64"],
      "Untyped constants default to int, float64, rune (int32) and complex128",
      """An untyped constant takes its default type when it has to become a value. `rune` is only another name for
      `int32`, so `%T` reports int32."""),

    q("init-functions-run-first", r'''
        package main

        import "fmt"

        var x = 1

        func init() { x *= 10 }

        func init() { x += 1 }

        func main() { fmt.Println(x) }
    ''', "11", ["1", "20", "10"],
      "init functions run in order, before main, after the package variables are set",
      """The variable `x` is initialised first. Then both `init` functions run, in the order they appear: 1 * 10
      is 10, plus 1 is 11. Only after that does `main` start."""),

    q("sprintf-width-and-flags", r'''
        package main

        import "fmt"

        func main() {
            fmt.Printf("[%5.1f|%-5d|%+d|%05d]\n", 3.14159, 42, 7, -42)
        }
    ''', "[  3.1|42   |+7|-0042]",
      ["[3.1  |   42|7|-0042]", "[  3.1|42   |+7|00-42]", "[  3.1|42|+7|-0042]"],
      "Width pads on the left unless - is given; 0 padding goes after the sign",
      """`%5.1f` rounds to one decimal and pads to five columns. `%-5d` left-aligns, `%+d` forces a sign, and
      `%05d` pads with zeros after the minus sign, giving -0042."""),

    q("buffered-channel-without-goroutines", r'''
        package main

        import "fmt"

        func main() {
            ch := make(chan int, 3)
            ch <- 1
            ch <- 2
            close(ch)
            n := len(ch)
            sum := 0
            for v := range ch {
                sum = sum*10 + v
            }
            fmt.Println(n, len(ch), cap(ch), sum)
        }
    ''', "2 0 3 12", ["0 0 3 12", "2 2 3 12", "2 0 2 21"],
      "A buffered channel is a FIFO queue: len counts what is waiting, cap is the buffer size",
      """Two values wait in the buffer, so `len` is 2 and `cap` is 3. `range` receives in order, 1 and then 2, and
      stops once the closed channel is empty, so `len` ends at 0."""),

    q("labelled-continue-and-break", r'''
        package main

        import "fmt"

        func main() {
            n := 0
        outer:
            for i := 0; i < 3; i++ {
                for j := 0; j < 3; j++ {
                    if j == 2 { continue outer }
                    if i == 2 { break outer }
                    n++
                }
            }
            fmt.Println(n)
        }
    ''', "4", ["6", "2", "5"],
      "continue outer skips the rest of the inner loop; break outer ends both",
      """For i = 0 and i = 1 the inner loop counts j = 0 and j = 1, then `continue outer` moves on at j = 2, giving
      4. At i = 2 the `break outer` fires on the first inner pass, before anything is counted."""),

    q("pointer-receiver-through-interface", r'''
        package main

        import "fmt"

        type Inc interface{ Inc() }
        type C struct{ n int }
        func (c *C) Inc()  { c.n++ }

        func main() {
            c := &C{}
            var i Inc = c
            i.Inc()
            v := *c
            i.Inc()
            fmt.Println(c.n, v.n)
        }
    ''', "2 1", ["2 2", "1 1", "1 2"],
      "An interface holding a pointer shares the struct; dereferencing makes a separate copy",
      """The interface stores the pointer `c`, so both `Inc` calls change the same struct and `c.n` is 2. `v := *c`
      copied the struct when n was 1, so `v` is not affected by the second call."""),

    q("huge-untyped-constant", r'''
        package main

        import "fmt"

        func main() {
            const huge = 1 << 100
            fmt.Println(huge>>98, float64(huge) > 1e30)
        }
    ''', "4 true", ["0 true", "4 false", "0 false"],
      "Untyped constants are exact and unbounded; they only have to fit when they become values",
      """The compiler works with `1 << 100` as a mathematical integer, so shifting it back by 98 gives exactly 4.
      Converting it to float64 is fine too, and 2^100 is about 1.27e30."""),

    q("unsigned-subtraction-wraps", r'''
        package main

        import "fmt"

        func main() {
            var a, b uint = 3, 4
            fmt.Println(a-b > 0, a-b == ^uint(0))
        }
    ''', "true true", ["false false", "true false", "false true"],
      "Unsigned subtraction below zero wraps to the largest value",
      """`3 - 4` cannot be negative for a `uint`, so it wraps around to the maximum, which is `^uint(0)` (all bits
      set). That is why comparing the difference with 0 says it is positive."""),

    q("number-literal-forms", r'''
        package main

        import "fmt"

        func main() {
            fmt.Println(010, 0x1p4, 1_000, 0b101, 0o17)
        }
    ''', "8 16 1000 5 15", ["10 16 1000 5 15", "8 16 1 5 15", "8 4 1000 5 17"],
      "A leading 0 means octal, p is a binary exponent for hex floats, and _ is just a separator",
      """`010` is octal, so it is 8. `0x1p4` is 1 times 2 to the 4th, the float 16, printed as 16. Underscores
      are ignored, and `0o17` is octal 15."""),

    q("stack-push-receivers", r'''
        package main

        import "fmt"

        type Stack []int

        func (s Stack) PushV(v int)  { s = append(s, v) }
        func (s *Stack) PushP(v int) { *s = append(*s, v) }

        func main() {
            var s Stack
            s.PushV(1); s.PushP(2)
            s.PushV(3); s.PushP(4)
            fmt.Println(s)
        }
    ''', "[2 4]", ["[1 2 3 4]", "[2]", "[1 2 4]"],
      "append returns a new slice header, so a value receiver cannot grow the caller's slice",
      """With a value receiver the method appends to its own copy of the header, and the caller's length never
      changes. Only the pointer receiver writes the new header back, so just 2 and 4 are kept."""),

    # ── Medium and hard ────────────────────────────────────────────────────
    q("fmt-bad-verbs", r'''
        package main

        import "fmt"

        func main() {
            a := fmt.Sprintf("%d|%s", 1)
            b := fmt.Sprintf("%d", "x")
            c := fmt.Sprintf("%d", 1, 2)
            fmt.Println(a, b, c)
        }
    ''', "1|%!s(MISSING) %!d(string=x) 1%!(EXTRA int=2)",
      ["1| x 1", "1|%!s(MISSING) x 1", "1|<nil> %!d(string=x) 1 2"],
      "fmt never panics on a bad format; it prints what went wrong inside the text",
      """A verb with no argument prints `%!s(MISSING)`, a verb of the wrong type prints `%!d(string=x)`, and a
      leftover argument is appended as `%!(EXTRA int=2)`. `go build` does not check this; only `go vet` does."""),

    q("stringer-and-other-verbs", r'''
        package main

        import "fmt"

        type Temp float64

        func (t Temp) String() string { return "T!" }

        func main() {
            t := Temp(2)
            fmt.Printf("%v|%s|%.1f|%q\n", t, t, t, t)
        }
    ''', 'T!|T!|2.0|"T!"', ['T!|T!|T!|"T!"', '2|2|2.0|"2"', 'T!|T!|2.0|T!'],
      "String() is used by %v, %s and %q, but a numeric verb like %.1f still sees the number",
      """Verbs that print text ask the value for its `String` method. `%.1f` wants a float, and a `Temp` is one
      underneath, so it formats the real value 2 and ignores the method."""),

    q("json-nil-slice-is-null", r'''
        package main

        import (
            "encoding/json"
            "fmt"
        )

        func main() {
            m := map[string]any{"b": 2.0, "a": []int(nil), "c": []int{}}
            out, _ := json.Marshal(m)
            fmt.Println(string(out))
        }
    ''', '{"a":null,"b":2,"c":[]}',
      ['{"a":[],"b":2,"c":[]}', '{"a":null,"b":2.0,"c":[]}', '{"b":2,"a":null,"c":[]}'],
      "A nil slice encodes as null, an empty one as [], and map keys come out sorted",
      """The encoder tells a nil slice from an empty one. The whole number 2.0 is written as 2, because JSON has
      only one number type, and map keys are sorted so the output is stable."""),

    q("copy-handles-overlap", r'''
        package main

        import "fmt"

        func main() {
            s := []int{1, 2, 3, 4}
            n := copy(s[1:], s)
            fmt.Println(s, n)
        }
    ''', "[1 1 2 3] 3", ["[1 1 1 1] 3", "[1 1 2 3] 4", "[2 3 4 4] 3"],
      "copy behaves as if the source were first saved, so overlapping ranges are safe",
      """The destination `s[1:]` has 3 slots and the source has 4 elements, so `copy` moves 3. It works like
      memmove: the source values 1, 2, 3 land in the later slots without being overwritten halfway."""),

    q("range-length-is-fixed", r'''
        package main

        import "fmt"

        func main() {
            s := []int{1, 2, 3}
            n := 0
            for range s {
                s = append(s, 0)
                n++
            }
            fmt.Println(n, len(s))
        }
    ''', "3 6", ["3 3", "6 6", "3 4"],
      "range evaluates the slice once, so appending inside the loop does not lengthen it",
      """The loop walks the original three-element slice header that `range` captured. Each pass appends, so `s`
      ends with six elements, but only three iterations happen."""),

    q("append-in-callee", r'''
        package main

        import "fmt"

        func add(s []int) {
            s = append(s, 9)
            s[0] = 7
        }

        func main() {
            s := make([]int, 1, 5)
            add(s)
            fmt.Println(s, len(s), s[:2])
        }
    ''', "[7] 1 [7 9]", ["[0] 1 [0 0]", "[7 9] 2 [7 9]", "[7] 1 [7 0]"],
      "The callee shares the array but not the length, so the caller sees edits but not growth",
      """`s[0] = 7` writes into the shared array, so the caller sees it. The append also wrote 9 into the spare
      room, but only the callee's copy of the header got length 2. Reslicing the caller's slice reveals the 9."""),

    q("method-value-binds-the-address", r'''
        package main

        import "fmt"

        type C struct{ n int }

        func (c *C) Inc()    { c.n++ }
        func (c C) Get() int { return c.n }

        func main() {
            c := C{1}
            inc, get := c.Inc, c.Get
            c.n = 10
            inc()
            fmt.Println(c.n, get())
        }
    ''', "11 1", ["2 1", "11 11", "2 2"],
      "A method value with a pointer receiver binds &c; with a value receiver it copies c now",
      """`c.Inc` is `(&c).Inc`, so it keeps working on the live variable and takes n from 10 to 11. `c.Get`
      copied `c` when the method value was made, when n was still 1, so it keeps answering 1."""),

    q("package-vars-follow-dependencies", r'''
        package main

        import "fmt"

        var order string
        var a = c + b
        var b = f("b", 1)
        var c = f("c", 2)

        func f(n string, v int) int { order += n; return v }

        func main() { fmt.Println(a, order) }
    ''', "3 bc", ["0 bc", "3 cb", "0 cb"],
      "Package-level variables are initialised by dependency, not by line order",
      """`a` needs `b` and `c`, so it waits. The initialiser repeatedly picks the earliest variable in the file
      that is ready, which is `b` and then `c`, and only then `a`. Written order would have given `a` zeros."""),

    q("interface-equality-needs-same-type", r'''
        package main

        import "fmt"

        func main() {
            var a any = 1
            var b any = int64(1)
            var c any = 1
            fmt.Println(a == b, a == c, a == 1)
        }
    ''', "false true true", ["true true true", "false false true", "false true false"],
      "Interface values are equal only when the types and the values both match",
      """`a` holds an int and `b` holds an int64, so they differ even though both are 1. `a == 1` converts the
      untyped constant to the default type, int, which matches."""),

    q("shift-count-beyond-the-width", r'''
        package main

        import "fmt"

        func main() {
            var s uint = 64
            var x uint64 = 1
            var one int8 = 1
            fmt.Println(x<<s, one<<7, -8>>1)
        }
    ''', "0 -128 -4", ["1 -128 -4", "0 128 -4", "0 -128 4"],
      "Shifting by the full width or more gives 0, and shifts never raise an error",
      """Go defines shifts for every count: moving all 64 bits out leaves 0, with no undefined behaviour. `1 << 7`
      in an int8 lands in the sign bit, which is -128, and `>>` on a negative number keeps the sign."""),

    q("string-index-is-a-byte", r'''
        package main

        import "fmt"

        func main() {
            s := "h\u00e9llo"
            fmt.Println(s[1], len(string(s[1])), len(s))
        }
    ''', "195 2 6", ["233 2 6", "195 1 6", "195 2 5"],
      "s[i] is one byte of the UTF-8 text, and string(byte) turns a number into a character",
      """The letter e-acute takes two bytes, 0xC3 and 0xA9, so `s[1]` is 195, not the character's code point 233.
      `string(195)` builds the character U+00C3, which itself needs two bytes, and the whole string is 6 bytes."""),

    q("defer-receiver-timing", r'''
        package main

        import "fmt"

        type T struct{ n int }
        var log []int
        func (t T) V()  { log = append(log, t.n) }
        func (t *T) P() { log = append(log, t.n) }

        func main() {
            defer func() { fmt.Println(log) }()
            t := T{1}
            defer t.V()
            defer t.P()
            t.n = 2
        }
    ''', "[2 1]", ["[2 2]", "[1 1]", "[1 2]"],
      "A deferred call copies a value receiver at the defer; a pointer receiver reads the live value",
      """Deferred calls run last in, first out, so `P` runs before `V`. `t.V` was evaluated with a copy of `t`
      when n was 1, while `t.P` holds `&t` and sees the later value 2. The printing closure was deferred first, so
      it runs last."""),

    q("recover-runtime-messages", r'''
        package main

        import "fmt"

        func try(f func()) (msg any) {
            defer func() { msg = recover() }()
            f()
            return nil
        }

        func main() {
            a := try(func() { var m map[string]int; m["a"] = 1 })
            b := try(func() { c := make(chan int, 1); close(c); c <- 1 })
            c := try(func() { z := 0; _ = 1 / z })
            fmt.Println(a, "|", b, "|", c)
        }
    ''', "assignment to entry in nil map | send on closed channel | runtime error: integer divide by zero",
      ["runtime error: assignment to entry in nil map | runtime error: send on closed channel"
       " | runtime error: integer divide by zero",
       "assignment to entry in nil map | send on closed channel | integer divide by zero",
       "<nil> | <nil> | runtime error: integer divide by zero"],
      "Runtime panics carry messages, and only some start with 'runtime error:'",
      """Writing to a nil map and sending on a closed channel panic with plain messages. Integer division by zero
      is reported as a runtime error with that prefix. The recovered value prints as its message."""),

    q("array-pointer-slicing", r'''
        package main

        import "fmt"

        func main() {
            arr := [3]int{1, 2, 3}
            p := &arr
            s := p[:2]
            s = append(s, 9)
            fmt.Println(len(p), cap(s), arr, p[1])
        }
    ''', "3 3 [1 2 9] 2", ["3 3 [1 2 3] 2", "3 2 [1 2 9] 2", "3 6 [1 2 3] 2"],
      "A pointer to an array can be indexed, sliced and measured; the slice shares the array",
      """`p[:2]` is a slice of `arr` with capacity 3, so the `append` has room and writes 9 into `arr[2]`. No new
      array is made. `len(p)` and `p[1]` work through the pointer without writing `*p`."""),

    q("grid-rows-shared-or-not", r'''
        package main

        import "fmt"

        func main() {
            row := make([]int, 2)
            grid := [][]int{row, row}
            grid[0][0] = 1
            other := make([][]int, 2)
            for i := range other {
                other[i] = make([]int, 2)
            }
            other[0][0] = 1
            fmt.Println(grid, other)
        }
    ''', "[[1 0] [1 0]] [[1 0] [0 0]]", ["[[1 0] [0 0]] [[1 0] [1 0]]",
                                       "[[1 0] [0 0]] [[1 0] [0 0]]", "[[1 0] [1 0]] [[1 0] [1 0]]"],
      "A slice of slices holds row headers; reusing one row makes every row the same memory",
      """`grid` stores the same `row` twice, so a write through one row shows in the other. `make([][]int, 2)`
      only makes the outer slice, which is why each row of `other` has to be allocated in the loop."""),

    q("tuple-assignment-order", r'''
        package main

        import "fmt"

        func main() {
            a, b := 1, 2
            a, b = b, a+b
            i, s := 0, []int{0, 0}
            i, s[i] = 1, 9
            fmt.Println(a, b, i, s)
        }
    ''', "2 3 1 [9 0]", ["2 4 1 [9 0]", "2 3 1 [0 9]", "2 3 1 [0 0]"],
      "In a tuple assignment all right sides and index operands are evaluated before any store",
      """`a, b = b, a+b` reads the old a and b first, giving 2 and 3 rather than 2 and 4. In `i, s[i] = 1, 9` the
      index `i` is also evaluated first, while it is still 0, so the 9 goes into `s[0]`."""),

    q("println-float-forms", r'''
        package main

        import "fmt"

        func main() {
            fmt.Println(1e6, 123456.0, 1234567.0, 1e-5, 0.0001, 1e20)
        }
    ''', "1e+06 123456 1.234567e+06 1e-05 0.0001 1e+20",
      ["1000000 123456 1234567 0.00001 0.0001 100000000000000000000",
       "1e+06 123456 1234567 1e-05 0.0001 1e+20", "1e6 123456 1.234567e6 1e-5 0.0001 1e20"],
      "%v prints floats in %g style: an exponent from 1e6 up, and below 1e-4",
      """With the shortest digits that round-trip, `%g` writes an exponent once the decimal exponent is below -4
      or at least 6. So 123456 stays plain, 1234567 becomes 1.234567e+06, and even 1e20 prints as 1e+20, unlike
      JavaScript."""),

    q("slices-delete-clears-the-tail", r'''
        package main

        import (
            "fmt"
            "slices"
        )

        func main() {
            s := []int{1, 2, 3, 4}
            t := slices.Delete(s, 1, 3)
            fmt.Println(t, s)
        }
    ''', "[1 4] [1 4 0 0]", ["[1 4] [1 4 3 4]", "[1 4] [1 2 3 4]", "[1 4 0 0] [1 4 0 0]"],
      "slices.Delete shifts the rest down in place and zeroes the freed elements",
      """The returned slice is the first two elements, but it shares the original array, which is edited: 4 moves
      into slot 1 and the two slots left over are set to zero. An old `append(s[:1], s[3:]...)` would leave the
      stale 3 and 4 behind."""),

    q("stringer-skips-unexported-fields", r'''
        package main

        import "fmt"

        type C int

        func (c C) String() string { return "C!" }

        type W struct {
            a C
            B C
        }

        func main() { fmt.Println(W{1, 2}, []C{3}) }
    ''', "{1 C!} [C!]", ["{C! C!} [C!]", "{1 2} [3]", "{1 C!} [3]"],
      "fmt cannot call methods on unexported struct fields, so they print as raw values",
      """The exported field `B` and the slice elements are reachable through reflection, so their `String` method
      is used. The unexported field `a` cannot be used that way, and `fmt` falls back to its underlying int."""),

    q("parse-int-out-of-range", r'''
        package main

        import (
            "fmt"
            "strconv"
        )

        func main() {
            v, err := strconv.ParseInt("300", 10, 8)
            fmt.Println(v, err)
        }
    ''', '127 strconv.ParseInt: parsing "300": value out of range',
      ['0 strconv.ParseInt: parsing "300": value out of range', "44 <nil>", "300 <nil>"],
      "On overflow ParseInt returns the nearest value that fits, along with the error",
      """With an 8-bit size, 300 does not fit, so the result is clamped to the largest int8, 127, and the error says
      the value is out of range. The number is never wrapped around to 44."""),

    q("range-over-invalid-utf8", r'''
        package main

        import "fmt"

        func main() {
            out := ""
            for i, r := range "a\xffb" {
                out += fmt.Sprintf("%d:%d ", i, r)
            }
            fmt.Println(out)
        }
    ''', "0:97 1:65533 2:98", ["0:97 1:255 2:98", "0:97 2:98", "0:97 1:0 2:98"],
      "A bad byte in a string is yielded as U+FFFD, one byte wide, and the loop carries on",
      """Ranging decodes UTF-8 as it goes. The byte 0xFF cannot start a character, so the loop gives the
      replacement character, 65533, and advances by one byte, which is why the next index is 2."""),

    q("nan-map-keys", r'''
        package main

        import (
            "fmt"
            "math"
        )

        func main() {
            m := map[float64]int{}
            m[math.NaN()] = 1
            m[math.NaN()] = 2
            _, ok := m[math.NaN()]
            fmt.Println(len(m), ok)
        }
    ''', "2 false", ["1 true", "2 true", "1 false"],
      "NaN is not equal to itself, so every NaN key is a new entry that can never be found",
      """Map lookup uses ==, and NaN == NaN is false. Each insert therefore adds a fresh entry, and a later lookup
      with another NaN finds nothing. The entries can only be removed with `clear(m)`."""),

    q("strings-with-an-empty-separator", r'''
        package main

        import (
            "fmt"
            "strings"
        )

        func main() {
            n := strings.Count("five", "")
            parts := len(strings.Split("abc", ""))
            i, l := strings.Index("abc", ""), strings.LastIndex("abc", "")
            fmt.Println(n, parts, i, l)
        }
    ''', "5 3 0 3", ["4 3 0 2", "0 1 -1 -1", "5 1 0 0"],
      "An empty string matches between every character, including both ends",
      """"five" has four characters and five gaps, so Count says 5. `Split` with an empty separator cuts after each
      character into 3 pieces. The empty string is found at index 0, and last at the very end, index 3."""),

    q("untyped-constants-pick-a-type", r'''
        package main

        import "fmt"

        func Which[T any](a, b T) string { return fmt.Sprintf("%T", a) }

        func main() {
            fmt.Println(Which(1, 2.5), Which(1, 'a'), Which(1, 2))
        }
    ''', "float64 int32 int", ["int float64 int", "float64 float64 int", "float64 int int"],
      "With mixed untyped constants, the inferred type is the 'largest' kind among them",
      """Since Go 1.21, when untyped constant arguments of different kinds share a type parameter, the one
      ranking highest is used: integer, then rune, then float. So `1` and `2.5` make float64, and `1` with `'a'`
      makes rune, shown as int32."""),
)
