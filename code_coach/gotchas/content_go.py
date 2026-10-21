"""Gotchas, Go: built with `go build` then run; portability notes are in langs.py (the `go` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("go")

ITEMS: tuple[Item, ...] = (
    q("append-shares-backing-array", r'''
        package main

        import "fmt"

        func main() {
            a := make([]int, 3, 10)
            b := append(a, 1)
            c := append(a, 2)
            fmt.Println(b[3], c[3], len(a))
        }
    ''', "2 2 3", ["1 2 3", "1 2 4", "2 2 4"],
      "Two appends to a slice with spare capacity write to the same memory",
      """`a` has length 3 but room for 10, so both appends fit without reallocating and `b` and `c` are views of
      the same array. The second append overwrites index 3, so `b[3]` reads 2 as well. `len(a)` never changed."""),

    q("defer-changes-named-result", r'''
        package main

        import "fmt"

        func f() (r int) {
            defer func() { r += 10 }()
            return 3
        }

        func main() {
            fmt.Println(f())
        }
    ''', "13", ["3", "10", "Error"],
      "return 3 sets the result variable, then the deferred function still runs",
      """With a named result, `return 3` first assigns 3 to `r`, then the deferred closure runs and adds 10 to the
      same variable, and only then does the function hand `r` back. That is how a defer can adjust what a
      function returns."""),

    q("range-copies-the-array", r'''
        package main

        import "fmt"

        func main() {
            arr := [3]int{1, 2, 3}
            for i, v := range arr {
                arr[2] = 10
                if i == 2 {
                    fmt.Println(v)
                }
            }
        }
    ''', "3", ["10", "2", "1"],
      "Ranging over an array walks a copy; ranging over a slice would not",
      """The range expression is evaluated once and, for an array, that means the whole array is copied. Writing
      `arr[2] = 10` changes the original but not the copy being walked, so `v` is still 3. With a slice (`arr[:]`)
      the loop would see the new 10."""),
)
