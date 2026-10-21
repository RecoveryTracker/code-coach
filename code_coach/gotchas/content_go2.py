"""Gotchas, Go, the second helping: slices that share, values that copy, and the nil that is not nil.

Same rules as content_go.py: `package main` with `func main`, built with go (loop variables are per-iteration, as
since 1.22), one fmt line of output, no map ranging (printing a whole map is fine: fmt sorts the keys), no
goroutines, no clock, and nothing declared and left unused.
"""

from __future__ import annotations

from .items import Item, make

q = make("go")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics with a real trap ──────────────────────────────
    q("division-signs", r'''
        package main

        import "fmt"

        func main() {
            a, b := -7, 3
            fmt.Println(a/2, a%b, 7/-2, a/b)
        }
    ''', "-3 -1 -3 -2", ["-4 2 -4 -3", "-3 2 -3 -2", "-4 -1 -3 -3"],
      "Integer division truncates toward zero, and % takes the sign of the left operand",
      """Go cuts the quotient toward zero, so -7 / 2 is -3 (not -4) and -7 / 3 is -2. The remainder is whatever is
      left over with the sign of the dividend: -7 % 3 is -1."""),

    q("string-len-is-bytes", r'''
        package main

        import "fmt"

        func main() {
            s := "héllo"
            fmt.Println(len(s), len([]rune(s)), s[1], []rune(s)[1])
        }
    ''', "6 5 195 233", ["5 5 233 233", "6 6 195 233", "6 5 233 195"],
      "len and indexing work on bytes; converting to []rune works on characters",
      """The accented e takes two bytes in UTF-8 (195 and 169), so `len` is 6 and `s[1]` is just the first of
      those bytes. Converting to `[]rune` decodes the characters, giving 5 of them and the code point 233."""),

    q("range-string-byte-offsets", r'''
        package main

        import "fmt"

        func main() {
            var idx []int
            for i, r := range "aé\U0001F600b" {
                idx = append(idx, i)
                _ = r
            }
            fmt.Println(idx)
        }
    ''', "[0 1 3 7]", ["[0 1 2 3]", "[0 1 2 4]", "[0 2 4 8]"],
      "Ranging over a string yields runes, with the index of each rune's first byte",
      """The loop decodes UTF-8 as it goes, but the index is a byte position. "a" takes one byte, the accented e
      two, and the emoji four, so the runes start at 0, 1, 3 and 7."""),

    q("integer-wraparound", r'''
        package main

        import "fmt"

        func main() {
            var a int8 = 127
            var b uint8 = 0
            var c uint32 = 0
            a++
            b--
            c--
            fmt.Println(a, b, c)
        }
    ''', "-128 255 4294967295", ["127 0 0", "-128 0 4294967295", "128 255 4294967295"],
      "Fixed-size integers wrap around without any error",
      """Go defines overflow of signed and unsigned integers as modular arithmetic. 127 + 1 in an int8 becomes
      -128, and 0 - 1 in an unsigned type becomes the largest value of that type."""),

    q("float-to-int-and-rounding", r'''
        package main

        import (
            "fmt"
            "math"
        )

        func main() {
            f := 3.99
            fmt.Println(int(f), int(-f), math.Round(-2.5), math.RoundToEven(2.5))
        }
    ''', "3 -3 -3 2", ["4 -4 -2 3", "3 -4 -2 2", "4 -3 -3 3"],
      "int() truncates; Round goes away from zero on halves; RoundToEven goes to the even neighbour",
      """Converting a float to an int drops the fraction toward zero. `math.Round(-2.5)` rounds halves away from
      zero, giving -3, while `RoundToEven` picks the even neighbour, so 2.5 becomes 2."""),

    q("untyped-constant-division", r'''
        package main

        import "fmt"

        func main() {
            const x = 5 / 2
            const y = 5 / 2.0
            var f float64 = 5 / 2
            fmt.Println(x, y, f)
        }
    ''', "2 2.5 2", ["2.5 2.5 2.5", "2 2.5 2.5", "2 2 2"],
      "Constant arithmetic still follows the operand kinds: 5 / 2 is integer division",
      """`5` and `2` are untyped integer constants, so their quotient is the integer 2 even when it is later
      stored in a float64. Only `2.0` makes the expression a floating-point constant."""),

    q("float-constant-exactness", r'''
        package main

        import "fmt"

        func main() {
            a, b := 0.1, 0.2
            fmt.Println(0.1+0.2, a+b)
        }
    ''', "0.3 0.30000000000000004",
      ["0.3 0.3", "0.30000000000000004 0.30000000000000004", "0.30000000000000004 0.3"],
      "Constant expressions are computed exactly; the same sum of variables is not",
      """The compiler evaluates `0.1+0.2` with arbitrary precision and only then rounds the exact 0.3 to a
      double. With variables the sum is done in binary floating point, and lands on 0.30000000000000004."""),

    q("float-division-by-zero", r'''
        package main

        import "fmt"

        func main() {
            x := 0.0
            fmt.Println(1/x, -1/x, x/x)
        }
    ''', "+Inf -Inf NaN", ["Infinity -Infinity NaN", "panic", "0 0 0"],
      "Floating-point division by zero gives infinities and NaN, and Go prints them as +Inf and -Inf",
      """Only integer division by zero panics. For floats the IEEE rules apply, and `fmt` spells the values
      `+Inf`, `-Inf` and `NaN`."""),

    q("string-from-integer", r'''
        package main

        import (
            "fmt"
            "strconv"
        )

        func main() {
            n := 65
            fmt.Println(string(rune(n)) + "|" + strconv.Itoa(n) + "|" +
                fmt.Sprint(n))
        }
    ''', "A|65|65", ["65|65|65", "A|A|65", "A|A|A"],
      "Converting an integer to string gives the character with that code, not its digits",
      """`string(rune(65))` is the one-character string "A". To get the text "65" use `strconv.Itoa` or `Sprint`.
      That is why a bare `string(n)` on an int is flagged by `go vet`."""),

    q("bytes-and-strings", r'''
        package main

        import "fmt"

        func main() {
            s := "hi"
            b := []byte(s)
            b[0] = 'X'
            fmt.Println(s, string(b), b, s[0], string(s[0]))
        }
    ''', "hi Xi [88 105] 104 h", ["Xi Xi [88 105] 104 h", "hi Xi [88 105] h h", "hi Xi [X i] 104 h"],
      "Strings are immutable; converting to []byte copies, and a string index is a byte number",
      """`[]byte(s)` makes an independent copy, so changing it leaves `s` alone. Printing a byte slice shows
      numbers, and `s[0]` is the byte 104 (an unsigned number), not the character."""),

    q("closure-counter-state", r'''
        package main

        import "fmt"

        func counter() func() int {
            c := 0
            return func() int { c++; return c }
        }

        func main() {
            a, b := counter(), counter()
            a()
            a()
            fmt.Println(a(), b())
        }
    ''', "3 1", ["3 3", "1 1", "3 4"],
      "Each call to counter() makes a new variable that its closure keeps alive",
      """The returned function captures its own `c`, so two counters count separately. `a` has been called three
      times by the time it prints, and `b` once."""),

    q("loop-variable-per-iteration", r'''
        package main

        import "fmt"

        func main() {
            var fs []func() int
            for i := 0; i < 3; i++ {
                fs = append(fs, func() int { return i })
            }
            fmt.Println(fs[0](), fs[1](), fs[2]())
        }
    ''', "0 1 2", ["3 3 3", "2 2 2", "0 0 0"],
      "Since Go 1.22 each loop iteration has its own copy of the loop variable",
      """Older Go versions shared a single `i` and the closures would all see the final 3. The current rule gives
      each iteration a fresh `i`, so each closure keeps its own value."""),

    q("range-over-integer", r'''
        package main

        import "fmt"

        func main() {
            sum := 0
            for i := range 4 {
                sum += i
            }
            fmt.Println(sum)
        }
    ''', "6", ["10", "4", "3"],
      "range over an integer n counts 0 up to n-1",
      """Since Go 1.22, `range 4` yields 0, 1, 2, 3, so the sum is 6. The end value is excluded, just as in a
      `for i := 0; i < 4; i++` loop."""),

    q("switch-fallthrough-skips-test", r'''
        package main

        import "fmt"

        func main() {
            s := ""
            switch x := 2; x {
            case 2:
                s += "two "
                fallthrough
            case 3:
                s += "three "
            }
            fmt.Println(s)
        }
    ''', "two three", ["two", "two three four", "three"],
      "Go cases do not fall through, unless asked; fallthrough ignores the next case's condition",
      """After "two" the `fallthrough` jumps into case 3's body without testing whether x is 3, and then
      the switch ends. Without the `fallthrough`, only "two" would be printed."""),

    q("break-inside-switch", r'''
        package main

        import "fmt"

        func main() {
            n := 0
            for i := 0; i < 5; i++ {
                switch {
                case i == 2:
                    break
                default:
                    n += i
                }
            }
            fmt.Println(n)
        }
    ''', "8", ["1", "10", "6"],
      "break inside a switch leaves the switch, not the enclosing loop",
      """In Go, `break` always applies to the innermost for, switch or select. At i = 2 only the switch ends, the
      loop carries on, and n gets 0 + 1 + 3 + 4 = 8. A label on the loop would be needed to stop it."""),

    q("shadowed-err", r'''
        package main

        import "fmt"

        func get() (int, error) { return 7, fmt.Errorf("boom") }

        func main() {
            n := 0
            var err error
            if true {
                n, err := get()
                _, _ = n, err
            }
            fmt.Println(n, err)
        }
    ''', "0 <nil>", ["7 boom", "7 <nil>", "0 boom"],
      ":= inside a block declares new variables instead of assigning the outer ones",
      """Both `n` and `err` are new in the `if` block, so the call fills those shadows, which disappear at the
      closing brace. The outer variables keep their zero values. Using `=` with predeclared variables avoids it."""),

    q("operator-precedence", r'''
        package main

        import "fmt"

        func main() {
            fmt.Println(1+2<<3, 5&3+1, 2+3*4%5)
        }
    ''', "17 2 4", ["24 4 4", "17 6 3", "25 4 2"],
      "<< and & bind like multiplication, tighter than +",
      """Go's multiplicative level includes `* / % << >> & &^`, so `1+2<<3` is 1 + (2 << 3) = 17 and `5&3+1` is
      (5 & 3) + 1 = 2. At the same level operators group left to right: `3*4%5` is 12 % 5 = 2, then 2 + 2 = 4."""),

    q("bit-operators", r'''
        package main

        import "fmt"

        func main() {
            fmt.Println(6&^3, 5^1, ^5, -8>>1, 1<<3|1)
        }
    ''', "4 4 -6 -4 9", ["2 4 -5 -4 9", "4 5 5 4 9", "4 4 -6 4 16"],
      "&^ clears bits, ^ is XOR as a binary operator and NOT as a unary one",
      """`6 &^ 3` clears the low two bits of 6 (110), leaving 4. Binary `5 ^ 1` is XOR (4), while unary `^5` flips
      every bit, which is -6. Shifting a negative number right keeps its sign."""),

    q("nil-map-reads", r'''
        package main

        import "fmt"

        func main() {
            var m map[string]int
            v, ok := m["a"]
            fmt.Println(v, ok, len(m), m == nil)
        }
    ''', "0 false 0 true", ["panic", "0 true 0 false", "<nil> false 0 true"],
      "A nil map can be read from, but not written to",
      """Looking up a missing key returns the value type's zero value and `ok` false, and that works on a nil map
      too. Assigning to a nil map would panic, so a map must be made first."""),

    q("map-zero-value-and-ok", r'''
        package main

        import "fmt"

        func main() {
            m := map[string]int{"a": 0}
            v1, ok1 := m["a"]
            v2, ok2 := m["b"]
            fmt.Println(v1, ok1, v2, ok2, len(m))
        }
    ''', "0 true 0 false 1", ["0 true 0 true 2", "0 false 0 false 1", "0 true <nil> false 1"],
      "A missing key and a stored zero look the same; only the comma-ok form tells them apart",
      """Both lookups return 0, so the value alone cannot say whether the key exists. The second result `ok`
      does, and reading a missing key does not insert it, so the length stays 1."""),

    q("map-of-slices-append", r'''
        package main

        import "fmt"

        func main() {
            m := map[string][]int{}
            m["a"] = append(m["a"], 1, 2)
            fmt.Println(m["a"], len(m["b"]), len(m))
        }
    ''', "[1 2] 0 1", ["[1 2] 0 2", "panic", "[1 2] <nil> 1"],
      "The zero value of a missing slice entry is a nil slice, which append accepts",
      """`m["a"]` is missing at first, so it is nil, and `append(nil, 1, 2)` is fine and creates the slice. The
      read of `m["b"]` just yields a nil slice of length 0 and does not add the key."""),

    q("fmt-prints-maps-sorted", r'''
        package main

        import "fmt"

        func main() {
            m := map[string]int{"b": 1, "c": 3, "a": 2}
            fmt.Println(m)
        }
    ''', "map[a:2 b:1 c:3]", ["map[b:1 c:3 a:2]", "{a:2 b:1 c:3}", "map[c:3 b:1 a:2]"],
      "Ranging over a map is random, but fmt prints a map in sorted key order",
      """The `fmt` package sorts map keys when it formats one, so printing is deterministic. A `for range` over
      the same map would visit keys in an unspecified, deliberately varying order."""),

    q("comparing-values", r'''
        package main

        import "fmt"

        type T struct{ n int }

        func main() {
            p1, p2 := &T{1}, &T{1}
            fmt.Println([2]int{1, 2} == [2]int{1, 2}, p1 == p2, *p1 == *p2)
        }
    ''', "true false true", ["true true true", "false false true", "true false false"],
      "Arrays and structs compare by value; pointers compare by address",
      """`==` on arrays and on structs compares their contents. Two pointers are equal only when they point at the
      very same variable, and these were allocated separately."""),

    q("strings-split-and-fields", r'''
        package main

        import (
            "fmt"
            "strings"
        )

        func main() {
            fmt.Println(len(strings.Split("a,b,,", ",")),
                len(strings.Split("", ",")), len(strings.Fields("  a  b ")))
        }
    ''', "4 1 2", ["2 0 2", "4 0 2", "2 1 4"],
      "Split keeps empty pieces (and gives one for \"\"); Fields splits on runs of spaces",
      """Unlike some languages, Go's `Split` does not discard trailing empty strings, so "a,b,," has four pieces.
      Splitting the empty string returns a slice with one empty element. `Fields` collapses whitespace."""),

    q("trim-cutset-versus-prefix", r'''
        package main

        import (
            "fmt"
            "strings"
        )

        func main() {
            fmt.Println(strings.TrimLeft("abba-x", "ab"),
                strings.TrimPrefix("abba-x", "ab"))
        }
    ''', "-x ba-x", ["ba-x ba-x", "-x -x", "a-x abba-x"],
      "TrimLeft takes a set of characters; TrimPrefix takes a whole string",
      """`TrimLeft` removes any leading characters that appear in "ab", repeatedly, so it eats "abba". `TrimPrefix`
      removes the exact prefix "ab" once, leaving "ba-x"."""),

    q("sorting-strings", r'''
        package main

        import (
            "fmt"
            "sort"
        )

        func main() {
            words := []string{"b", "a", "C", "10", "9"}
            sort.Strings(words)
            fmt.Println(words)
        }
    ''', "[10 9 C a b]", ["[9 10 a b C]", "[10 9 a b C]", "[C a b 10 9]"],
      "String order is by bytes: digits, then capitals, then lower case",
      """Strings compare byte by byte, so "10" sorts before "9" and every capital precedes every lower-case
      letter. Code points of digits (48 to 57) are below those of upper case (65 to 90) and lower case (97 up)."""),

    q("iota-repeat", r'''
        package main

        import "fmt"

        const (
            A = iota
            B
            C = "x"
            D
            E = iota
        )

        func main() {
            fmt.Println(A, B, C, D, E)
        }
    ''', "0 1 x x 4", ["0 1 x x 0", "0 1 2 3 4", "0 1 x 3 4"],
      "A constant without a value repeats the previous expression; iota counts every line",
      """`D` repeats the expression `"x"`, not the counter. `iota` still advances on every line of the block, so
      when `E = iota` appears on the fifth line it is 4."""),

    q("type-assertion-comma-ok", r'''
        package main

        import "fmt"

        func main() {
            var i interface{} = "text"
            n, ok := i.(int)
            s, ok2 := i.(string)
            fmt.Println(n, ok, s, ok2)
        }
    ''', "0 false text true", ["panic", "<nil> false text true", "0 false  false"],
      "The comma-ok form of a type assertion returns the zero value instead of panicking",
      """Asserting the wrong type with the one-result form panics. With two results it just reports `ok = false`
      and the zero value of the target type, which for int is 0."""),

    q("printf-verbs-for-structs", r'''
        package main

        import "fmt"

        type P struct {
            X int
            Y string
        }

        func main() {
            p := P{1, "a"}
            fmt.Printf("%v %+v %#v %T\n", p, p, p, p)
        }
    ''', '{1 a} {X:1 Y:a} main.P{X:1, Y:"a"} main.P',
      ['{1 a} {1 a} {1 a} P', '{1 a} {X:1 Y:a} P{X:1, Y:"a"} P', '(1 a) {X:1 Y:a} main.P{1, "a"} main.P'],
      "%v, %+v and %#v show the same struct three different ways",
      """`%v` prints the bare values, `%+v` adds field names, and `%#v` prints Go syntax, including the package
      name and quoted strings. `%T` gives the type with its package."""),

    q("sprint-spacing", r'''
        package main

        import "fmt"

        func main() {
            fmt.Println(fmt.Sprint("a", 1, 2, "b"), fmt.Sprint(1, 2),
                fmt.Sprint("a", "b"))
        }
    ''', "a1 2b 1 2 ab", ["a 1 2 b 1 2 a b", "a1 2b 12 ab", "a 1 2 b 12 a b"],
      "Sprint adds a space only between operands when neither is a string; Println always does",
      """`Print`, `Sprint` and `Sprintf`'s relatives insert spaces between two operands only if neither of them is
      a string. So 1 and 2 get a space, while "a" and 1, or 2 and "b", do not. `Println` always separates."""),

    q("quote-and-char-verbs", r'''
        package main

        import "fmt"

        func main() {
            fmt.Printf("%q %v %x %c %U\n", "hi", 'a', "hi", 97, 0x1F600)
        }
    ''', '"hi" 97 6869 a U+1F600', ['hi a 6869 97 U+1F600', '"hi" a 68 a U+1F600', '"hi" 97 6869 97 1F600'],
      "A rune is a number: %v prints 97 and %c prints the character",
      """`'a'` is an integer constant, so `%v` shows 97, while `%c` shows the character for a code. `%x` on a
      string gives the hex of every byte, `%q` adds quotes, and `%U` gives the Unicode notation."""),

    q("strconv-atoi-error", r'''
        package main

        import (
            "fmt"
            "strconv"
        )

        func main() {
            n, err := strconv.Atoi("12a")
            fmt.Println(n, err)
        }
    ''', '0 strconv.Atoi: parsing "12a": invalid syntax',
      ['12 <nil>', '0 <nil>', '12 strconv.Atoi: parsing "12a": invalid syntax'],
      "Atoi parses the whole string or fails: it never reads a leading number",
      """Unlike C's `atoi`, this one returns an error for trailing junk, and the number is 0 in that case. The
      error text names the function, the input and the reason."""),

    q("generic-zero-value", r'''
        package main

        import "fmt"

        func Zero[T any]() T {
            var z T
            return z
        }

        func main() {
            fmt.Println(Zero[int](), Zero[string]() == "", Zero[*int]() == nil,
                Zero[[]int]() == nil)
        }
    ''', "0 true true true", ["0 false true true", "<nil> true true true", "0 true false true"],
      "var z T is the zero value of whatever T turns out to be",
      """Each instantiation gets the zero value of its type argument: 0, the empty string, a nil pointer, a nil
      slice. There is no single "null" that fits them all."""),

    # ── Slices, arrays and copies ──────────────────────────────────────────
    q("slice-three-index", r'''
        package main

        import "fmt"

        func main() {
            a := []int{1, 2, 3}
            b := a[:2]
            b = append(b, 99)
            c := a[:2:2]
            c = append(c, 7)
            fmt.Println(a, c)
        }
    ''', "[1 2 99] [1 2 7]", ["[1 2 3] [1 2 7]", "[1 2 99] [1 2 99]", "[1 2 3] [1 2 99]"],
      "append writes into the shared array when the slice has spare capacity",
      """`a[:2]` has capacity 3, so appending 99 overwrites a's third element. The full slice expression `a[:2:2]`
      caps the capacity at 2, forcing `append` to copy into a new array and leave `a` alone."""),

    q("copy-returns-min-length", r'''
        package main

        import "fmt"

        func main() {
            dst := make([]int, 2)
            n := copy(dst, []int{1, 2, 3})
            var empty []int
            m := copy(empty, []int{1})
            fmt.Println(n, dst, m)
        }
    ''', "2 [1 2] 0", ["3 [1 2 3] 1", "2 [1 2] 1", "3 [1 2] 0"],
      "copy moves as many elements as the shorter slice has room for",
      """`copy` never grows the destination. It copies min(len(dst), len(src)) elements and reports that number,
      so a destination of length 0 receives nothing."""),

    q("array-copy-versus-slice", r'''
        package main

        import "fmt"

        func main() {
            a := [3]int{1, 2, 3}
            b := a
            b[0] = 9
            s := a[:]
            s[1] = 7
            fmt.Println(a, b)
        }
    ''', "[1 7 3] [9 2 3]", ["[9 7 3] [9 2 3]", "[1 2 3] [9 2 3]", "[1 7 3] [1 7 3]"],
      "Assigning an array copies it; slicing it makes a view",
      """`b := a` copies all three elements, so changing b leaves a alone. `a[:]` is a slice over a's own memory,
      so writing through `s` changes a."""),

    q("range-value-copy", r'''
        package main

        import "fmt"

        type T struct{ n int }

        func main() {
            items := []T{{1}, {2}}
            for _, v := range items {
                v.n *= 10
            }
            for i := range items {
                items[i].n++
            }
            fmt.Println(items)
        }
    ''', "[{2} {3}]", ["[{10} {20}]", "[{11} {21}]", "[{1} {2}]"],
      "The range variable is a copy of the element",
      """Multiplying `v.n` changes only the loop's copy. The second loop indexes into the slice, which really
      modifies the elements, adding 1 to each."""),

    q("append-capacity-decides", r'''
        package main

        import "fmt"

        func main() {
            a := make([]int, 2, 2)
            b := make([]int, 2, 3)
            a2 := append(a, 5)
            b2 := append(b, 5)
            a2[0], b2[0] = 9, 9
            fmt.Println(a[0], b[0])
        }
    ''', "0 9", ["9 9", "0 0", "9 0"],
      "Whether append shares memory depends on the spare capacity",
      """`a` is full, so `append` allocates a new array and `a2` is independent. `b` has room for a third
      element, so `b2` reuses b's array, and writing to its first element shows through `b`."""),

    q("reslice-capacity", r'''
        package main

        import "fmt"

        func main() {
            s := []int{1, 2, 3, 4, 5}
            t := s[1:3]
            t = append(t, 100)
            fmt.Println(len(t), cap(t), s)
        }
    ''', "3 4 [1 2 3 100 5]", ["3 3 [1 2 3 4 5]", "3 4 [1 2 3 4 5]", "3 3 [1 2 3 100 5]"],
      "A subslice keeps the rest of the array as capacity, and append writes into it",
      """`s[1:3]` has length 2 but capacity 4 (it can reach the end of the array). Appending therefore overwrites
      `s[3]` with 100 instead of allocating."""),

    q("delete-with-append", r'''
        package main

        import "fmt"

        func main() {
            orig := []int{1, 2, 3, 4}
            s := append(orig[:1], orig[2:]...)
            fmt.Println(s, orig)
        }
    ''', "[1 3 4] [1 3 4 4]", ["[1 3 4] [1 2 3 4]", "[1 3 4] [1 3 4]", "[1 3] [1 3 3 4]"],
      "The delete-one-element idiom shifts the elements inside the original array",
      """`orig[2:]...` is copied down over index 1 in the same memory. The result `s` is a shorter slice of that
      array, and `orig` still has its old length, now with a duplicate 4 at the end."""),

    q("variadic-passes-the-slice", r'''
        package main

        import "fmt"

        func set(xs ...int) { xs[0] = 9 }

        func main() {
            a := []int{1, 2}
            set(a...)
            set(a[1], 5)
            fmt.Println(a)
        }
    ''', "[9 2]", ["[1 2]", "[9 5]", "[9 9]"],
      "f(a...) hands over the same slice; f(x, y) builds a new one",
      """Passing `a...` uses a's own backing array as the variadic parameter, so the write to `xs[0]` changes a.
      The second call makes a fresh slice from two separate values and affects nothing."""),

    q("struct-with-slice-copy", r'''
        package main

        import "fmt"

        type B struct{ xs []int }

        func main() {
            a := B{[]int{1, 2}}
            b := a
            b.xs[0] = 9
            b.xs = append(b.xs, 3)
            fmt.Println(a.xs, b.xs)
        }
    ''', "[9 2] [9 2 3]", ["[1 2] [9 2 3]", "[9 2 3] [9 2 3]", "[1 2] [1 2 3]"],
      "Copying a struct copies the slice header, not the elements",
      """`b` has its own slice header but points at the same array, so the element write shows in both. The
      append changes only b's header (length 3), so `a.xs` stays at length 2."""),

    q("nil-versus-empty-slice", r'''
        package main

        import "fmt"

        func main() {
            var a []int
            b := []int{}
            a = append(a, 1)
            fmt.Println(a, b == nil, len(b), cap(b))
        }
    ''', "[1] false 0 0", ["[1] true 0 0", "[] false 0 0", "panic"],
      "append works on a nil slice, and an empty slice literal is not nil",
      """A nil slice is a valid empty slice, and `append` simply allocates for it. `[]int{}` is empty but has a
      non-nil pointer, so comparing it with nil is false."""),

    q("copy-in-interface", r'''
        package main

        import "fmt"

        type S struct{ n int }

        func main() {
            s := S{1}
            var i interface{} = s
            s.n = 5
            fmt.Println(i.(S).n, s.n)
        }
    ''', "1 5", ["5 5", "1 1", "5 1"],
      "Storing a struct in an interface stores a copy",
      """The interface holds a snapshot made at the moment of assignment. Later changes to `s` do not reach it,
      and the asserted `i.(S)` shows the old value."""),

    # ── Methods, interfaces and embedding ──────────────────────────────────
    q("value-receiver-no-effect", r'''
        package main

        import "fmt"

        type C struct{ n int }

        func (c C) IncVal()  { c.n++ }
        func (c *C) IncPtr() { c.n++ }

        func main() {
            c := C{}
            c.IncVal()
            c.IncPtr()
            c.IncPtr()
            fmt.Println(c.n)
        }
    ''', "2", ["3", "1", "0"],
      "A value receiver works on a copy of the struct",
      """`IncVal` increments its own copy, which is thrown away. The pointer-receiver method modifies `c` itself,
      and it ran twice."""),

    q("method-value-snapshot", r'''
        package main

        import "fmt"

        type C struct{ n int }

        func (c C) Get() int { return c.n }

        func main() {
            c := C{1}
            f := c.Get
            c.n = 5
            fmt.Println(f(), c.Get())
        }
    ''', "1 5", ["5 5", "1 1", "5 1"],
      "A method value copies the receiver at the moment it is taken",
      """`f := c.Get` evaluates `c` right away and binds a copy of it, so the later change does not reach `f`. A
      fresh call `c.Get()` sees the current 5."""),

    q("stringer-pointer-receiver", r'''
        package main

        import "fmt"

        type P struct{ x, y int }

        func (p *P) String() string { return fmt.Sprintf("P(%d,%d)", p.x, p.y) }

        func main() {
            p := P{1, 2}
            fmt.Println(p, &p)
        }
    ''', "{1 2} P(1,2)", ["P(1,2) P(1,2)", "{1 2} &{1 2}", "&{1 2} P(1,2)"],
      "A String method on a pointer receiver is not used when printing the value",
      """The method set of `P` does not include methods with pointer receivers, so `fmt` finds no `Stringer` in
      the value and prints it raw. The pointer `&p` has the method and uses it."""),

    q("embedding-is-not-inheritance", r'''
        package main

        import "fmt"

        type Animal struct{}

        func (Animal) Name() string    { return "animal" }
        func (a Animal) Hello() string { return "I am " + a.Name() }

        type Dog struct{ Animal }

        func (Dog) Name() string { return "dog" }

        func main() {
            fmt.Println(Dog{}.Name(), Dog{}.Hello())
        }
    ''', "dog I am animal", ["dog I am dog", "animal I am animal", "animal I am dog"],
      "An embedded type's methods call back into the embedded type, never the outer one",
      """`Dog.Name` shadows the promoted `Animal.Name`, so `d.Name()` is "dog". But `Hello` is Animal's method with
      an Animal receiver, so inside it `a.Name()` is Animal's own. Go has no virtual dispatch through embedding."""),

    q("nil-pointer-in-interface", r'''
        package main

        import "fmt"

        type MyErr struct{}

        func (*MyErr) Error() string { return "my error" }

        func find() error {
            var p *MyErr
            return p
        }

        func main() {
            fmt.Println(find() == nil)
        }
    ''', "false", ["true", "panic", "<nil>"],
      "An interface holding a nil pointer is not itself nil",
      """An interface value is a (type, value) pair. Returning a nil `*MyErr` makes the pair (*MyErr, nil), and
      that is not equal to the nil interface, which has no type at all."""),

    q("errors-is-and-wrapping", r'''
        package main

        import (
            "errors"
            "fmt"
            "io"
        )

        func main() {
            w := fmt.Errorf("read: %w", io.EOF)
            v := fmt.Errorf("read: %v", io.EOF)
            fmt.Println(errors.Is(w, io.EOF), errors.Is(v, io.EOF), w)
        }
    ''', "true false read: EOF", ["true true read: EOF", "false false read: EOF", "true false EOF"],
      "Only %w wraps an error so that errors.Is can find it",
      """Both messages read the same, but `%v` only formats the text, while `%w` keeps the original error inside
      the new one for `errors.Is` and `errors.As` to unwrap."""),

    q("errors-new-identity", r'''
        package main

        import (
            "errors"
            "fmt"
        )

        func main() {
            a := errors.New("x")
            b := errors.New("x")
            c := a
            fmt.Println(a == b, a == c, a.Error() == b.Error())
        }
    ''', "false true true", ["true true true", "false false true", "true false true"],
      "Two errors with the same text are different errors",
      """`errors.New` returns a pointer to a fresh value each time, and comparing the interface values compares
      those pointers. Only `c`, a copy of the same pointer, is equal to `a`."""),

    q("json-struct-rules", r'''
        package main

        import (
            "encoding/json"
            "fmt"
        )

        func main() {
            v := struct {
                A int
                b int
                C string `json:"c,omitempty"`
            }{1, 2, ""}
            out, _ := json.Marshal(v)
            fmt.Println(string(out))
        }
    ''', '{"A":1}', ['{"A":1,"b":2,"c":""}', '{"A":1,"b":2}', '{"A":1,"c":""}'],
      "JSON ignores unexported fields, and omitempty drops zero values",
      """Only exported (capitalised) fields are visible to the encoder, so `b` never appears. `C` is the empty
      string and has `omitempty`, so it is left out as well."""),

    q("float32-precision", r'''
        package main

        import "fmt"

        func main() {
            var f float32 = 16777216
            var g float32 = 0.1
            fmt.Println(f+1 == f, float64(g) == 0.1)
        }
    ''', "true false", ["false true", "false false", "true true"],
      "A float32 has 24 bits of precision, so 2^24 + 1 is not representable",
      """Above 16777216 the spacing between float32 values is 2, so adding 1 rounds back to the same number. The
      float32 nearest 0.1, widened to a double, differs from the double nearest 0.1."""),

    q("minus-of-min-int", r'''
        package main

        import "fmt"

        func main() {
            var x int8 = -128
            y := int8(-1)
            fmt.Println(-x, x/y, x*y)
        }
    ''', "-128 -128 -128", ["128 128 128", "-128 128 128", "panic"],
      "The most negative number has no positive twin, so negating it wraps to itself",
      """In two's complement, +128 does not fit in an int8, so `-x`, `x / -1` and `x * -1` all wrap back to -128.
      The spec defines this overflow, and unlike dividing by zero it does not panic."""),

    q("closed-channel-receive", r'''
        package main

        import "fmt"

        func main() {
            ch := make(chan int, 1)
            ch <- 7
            close(ch)
            a, ok1 := <-ch
            b, ok2 := <-ch
            fmt.Println(a, ok1, b, ok2)
        }
    ''', "7 true 0 false", ["7 true 7 true", "7 true panic", "7 false 0 false"],
      "A closed channel still delivers its buffered values, then zero values with ok false",
      """The buffered 7 is received normally. After that, receiving from a closed, empty channel never blocks: it
      returns the zero value and `ok` is false, which is how `range` knows to stop."""),

    q("recover-sets-named-result", r'''
        package main

        import "fmt"

        func f() (r string) {
            defer func() {
                if e := recover(); e != nil {
                    r = fmt.Sprint("recovered: ", e)
                }
            }()
            a, i := []int(nil), 3
            _ = a[i]
            return "ok"
        }

        func main() { fmt.Println(f()) }
    ''', "recovered: runtime error: index out of range [3] with length 0",
      ["ok", "recovered: index out of range", "recovered: runtime error: index out of range [3]"],
      "A deferred recover stops the panic, and it can set the function's named result",
      """The out-of-range read panics before `return "ok"` is reached. The deferred function recovers the panic
      value, an error whose text names the index and the length, and stores it in the result."""),

    q("defer-lifo-per-iteration", r'''
        package main

        import "fmt"

        func f() (out []int) {
            for i := 0; i < 3; i++ {
                defer func() { out = append(out, i) }()
            }
            return nil
        }

        func main() { fmt.Println(f()) }
    ''', "[2 1 0]", ["[0 1 2]", "[3 3 3]", "[]"],
      "Deferred calls run in last-in-first-out order, each with its own i",
      """The three closures are queued in order and run in reverse when `f` returns, after `return nil` has set
      the result. Each captured its own per-iteration `i`, so they append 2, 1 and 0."""),

    q("defer-argument-timing", r'''
        package main

        import "fmt"

        func f() (s string) {
            x := 1
            defer func(v int) { s = fmt.Sprint(v, " ", x) }(x)
            x = 2
            return
        }

        func main() { fmt.Println(f()) }
    ''', "1 2", ["1 1", "2 2", "2 1"],
      "A deferred call's arguments are evaluated at the defer statement; the closure body runs later",
      """The argument `x` is evaluated when `defer` executes, so `v` is 1. The closure's reference to `x` itself,
      though, is read when it finally runs, after `x = 2`."""),

    q("range-over-func", r'''
        package main

        import "fmt"

        func seq(yield func(int) bool) {
            for i := 1; i <= 5 && yield(i*i); i++ {}
        }

        func main() {
            sum := 0
            for v := range seq {
                if v > 10 { break }
                sum += v
            }
            fmt.Println(sum)
        }
    ''', "14", ["55", "30", "10"],
      "A for loop over a function runs its body as the yield callback; break makes yield return false",
      """`seq` produces 1, 4, 9, 16, 25. The loop adds 1 + 4 + 9 and breaks at 16, which makes `yield` return
      false so `seq` stops. The total is 14."""),
    q("type-switch-nil-cases", r'''
        package main

        import "fmt"

        func kind(i interface{}) string {
            switch v := i.(type) {
            case nil: return "nil"
            case int: return fmt.Sprint("int", v+1)
            }
            return "other"
        }

        func main() {
            var p *int
            fmt.Println(kind(nil), kind(p), kind(41))
        }
    ''', "nil other int42", ["nil nil int42", "other other int42", "nil other int41"],
      "A nil pointer put in an interface does not match case nil",
      """`case nil` matches only an interface with no dynamic type. `p` is a nil `*int`, so the interface holds
      the type *int and falls through to "other". Inside `case int`, `v` has type int, so `v+1` works."""),

    q("min-max-builtins", r'''
        package main

        import "fmt"

        func main() {
            f := 1.5
            fmt.Println(min(3, 1, 2), max(2, f), min("b", "a"), max(2, 3.5))
        }
    ''', "1 2 a 3.5", ["1 1.5 a 3.5", "3 2 b 3", "1 2 a 3"],
      "min and max are built in, take any ordered type, and give untyped constants the other operand's type",
      """`max(2, f)` converts the constant 2 to float64 because `f` is one, and prints as 2. Strings compare in
      byte order, so "a" is the min. The all-constant `max(2, 3.5)` is an untyped float constant, 3.5."""),

    q("rune-constant-arithmetic", r'''
        package main

        import "fmt"

        func main() {
            c := 'a' + 1
            var b byte = 'z'
            b -= 25
            fmt.Println(c, string(rune(c)), b, string(b))
        }
    ''', "98 b 97 a", ["b b a a", "98 98 97 97", "98 b 97 97"],
      "A char literal is a number: arithmetic on it gives a number, not a letter",
      """`'a' + 1` is the rune value 98, and `fmt` prints runes and bytes as integers. Converting back with
      `string(...)` yields the character. The byte arithmetic `'z' - 25` is 97, which is 'a'."""),
)
