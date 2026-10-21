"""Gotchas, Ruby (second deck): run by ruby (4.x on this machine); portability notes are in langs.py.

Written so the answer does not depend on the Ruby version: Hash and Set are never printed with `inspect` (the
format changed in 3.4 and 3.5), string literals are never mutated (use `+""`, `dup` or `String.new`), and
every card prints one line.
"""

from __future__ import annotations

from .items import Item, make

q = make("ruby")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics a beginner can get, with a real trap ──────────
    q("interpolate-nil-and-array", r'''
        puts "#{nil}|#{[nil]}|#{nil.inspect}|#{[]}"
    ''', "|[nil]|nil|[]", ["nil|[nil]|nil|[]", "|nil|nil|", "|[nil]|nil|"],
      "Interpolating nil gives an empty string, but inside an array it shows as nil",
      """String interpolation calls `to_s`. `nil.to_s` is the empty string, while `Array#to_s` is `inspect`, which
      prints each element with `inspect`, so a nil inside an array shows up as the word nil. An empty array is
      still printed as []."""),

    q("string-times-integer", r'''
        puts "5" * 3 + 5.to_s
    ''', "5555", ["20", "515", "55"],
      "String * Integer repeats the text; it is not arithmetic",
      """`"5" * 3` is the string "555", and `5.to_s` is "5", so `+` joins them into "5555". Ruby does not
      convert between strings and numbers on its own: `"5" + 5` would raise a TypeError."""),

    q("integer-then-float-math", r'''
        p [10 / 3 * 3.0, 10 / 3.0 * 3, 10.fdiv(4), 7 / 2r]
    ''', "[9.0, 10.0, 2.5, (7/2)]", ["[10.0, 10.0, 2.5, 3.5]", "[9.0, 10.0, 2, (7/2)]",
                                      "[9.0, 10.0, 2.5, 3]"],
      "The integer division happens first when it comes first; a rational stays exact",
      """`10 / 3 * 3.0` is evaluated left to right: 10 / 3 is already 3 (integer division), then 3 * 3.0 is 9.0.
      With the float first, `10 / 3.0 * 3` keeps the fraction. `7 / 2r` divides by a Rational, so the result
      is the exact fraction 7/2, printed by `p` as (7/2)."""),

    q("range-inclusive-exclusive", r'''
        sizes = [(1..5).sum, (1...5).sum, ('a'..'e').to_a.size, (1...1).to_a.size]
        puts sizes.join(" ")
    ''', "15 10 5 0", ["10 10 4 0", "15 10 4 1", "15 15 5 0"],
      "Two dots include the end, three dots stop just before it",
      """`1..5` includes 5, so its sum is 15, while `1...5` excludes 5 and sums to 10. Letter ranges work the
      same way and `'a'..'e'` has five elements. `1...1` is empty."""),

    q("string-append-aliasing", r'''
        a = +"hi"
        b = a
        b << " there"
        c = a
        c += "!"
        puts [a, b, c].join("|")
    ''', "hi there|hi there|hi there!", ["hi|hi there|hi!", "hi there|hi there|hi there",
                                         "hi|hi|hi!"],
      "<< changes the shared string; += makes a new one and rebinds only that name",
      """`b = a` makes both names point at one string, so `b << " there"` is visible through `a`. `c += "!"`
      is `c = c + "!"`: it builds a new string for `c` and leaves the shared one alone."""),

    q("array-new-shared-default", r'''
        grid = Array.new(2, [])
        grid[0] << 1
        fresh = Array.new(2) { [] }
        fresh[0] << 1
        p [grid, fresh]
    ''', "[[[1], [1]], [[1], []]]", ["[[[1], []], [[1], []]]", "[[[1], [1]], [[1], [1]]]",
                                     "[[[1], []], [[1], [1]]]"],
      "Array.new(n, obj) fills every slot with the same object; the block form builds fresh ones",
      """The second argument is evaluated once, so both rows of `grid` are the very same array and one push
      shows up twice. `Array.new(2) { [] }` runs the block for every slot and makes independent rows."""),

    q("delete-return-values", r'''
        a = [3, 1, 2, 1]
        p [a.delete(1), a.delete(9), a.delete_at(0), a]
    ''', "[1, nil, 3, [2]]", ["[[1, 1], nil, 3, [2]]", "[1, 9, 3, [2]]", "[1, nil, 3, [1, 2]]"],
      "delete returns the deleted value (or nil), not the array, and removes every match",
      """`delete(1)` removes both 1s and returns the value 1; `delete(9)` finds nothing and returns nil.
      `delete_at(0)` removes by position and returns what was there, 3. The array is left as [2]."""),

    q("each-map-select-results", r'''
        p [[1, 2].each { |x| x * 2 }, [1, 2].map { |x| x * 2 },
           [1, 2].map { |x| x > 1 }, [1, 2].select { |x| x > 1 }]
    ''', "[[1, 2], [2, 4], [false, true], [2]]",
      ["[[2, 4], [2, 4], [false, true], [2]]", "[[1, 2], [2, 4], [2], [2]]",
       "[[1, 2], [2, 4], [false, true], [false, true]]"],
      "each returns the receiver, map returns the block values, select filters by them",
      """`each` ignores what the block returns and hands back the original array. `map` collects the block
      results, so a test like `x > 1` turns into booleans. `select` uses those booleans to decide which
      elements to keep."""),

    q("or-assign-and-falsy", r'''
        x = false
        x ||= 5
        y = 0
        y ||= 7
        z = nil
        z ||= []
        z << 1
        p [x, y, z]
    ''', "[5, 0, [1]]", ["[false, 0, [1]]", "[5, 7, [1]]", "[5, 0, []]"],
      "||= only assigns when the variable is nil or false; zero counts as set",
      """`a ||= b` means `a || a = b`. `false` and `nil` are falsy, so `x` and `z` are replaced, but `0` is
      truthy, so `y` keeps its zero."""),

    q("and-or-precedence-vs-symbols", r'''
        a = true && false
        b = true and false
        c = nil || "d"
        d = nil or "d"
        p [a, b, c, d]
    ''', '[false, true, "d", nil]', ['[false, false, "d", "d"]', '[false, true, "d", "d"]',
                                    '[true, true, "d", nil]'],
      "and / or bind looser than =, so `b = true and false` assigns true",
      """`&&` and `||` bind tighter than `=`, so `a` gets the whole `true && false`. `and` and `or` bind looser
      than the assignment: `b = true and false` is `(b = true) and false`, and `d = nil or "d"` is
      `(d = nil) or "d"`, which leaves d as nil."""),

    q("string-to-number-lenient", r'''
        p ["12abc".to_i, "abc".to_i, "3.7xyz".to_f, "0x1A".hex, "1_000".to_i,
           " 42 ".to_i]
    ''', "[12, 0, 3.7, 26, 1000, 42]", ["[12, 0, 3.7, 26, 1, 42]", "[0, 0, 3, 26, 1000, 42]",
                                         "[12, nil, 3.7, 26, 1000, 42]"],
      "to_i and to_f read what they can and quietly give 0 for the rest",
      """`to_i` parses the leading number and stops at the first character that does not fit, so "12abc" is
      12 and "abc" is 0 with no error. Underscores are allowed inside digits, which makes "1_000" 1000, and
      surrounding spaces are skipped."""),

    q("integer-strict-parsing", r'''
        p [Integer("010"), Integer("0b11"), Integer("08", 10),
           (Integer("08") rescue "bad"), Integer("z", 36)]
    ''', '[8, 3, 8, "bad", 35]', ['[10, 3, 8, "bad", 35]', '[10, 11, 8, 8, 35]', '[8, 3, 8, 8, 35]'],
      "Integer() honours prefixes: a leading 0 is octal, and 8 is not an octal digit",
      """Unlike `to_i`, `Integer()` is strict and reads Ruby-style prefixes. "010" is octal, so it is 8, "0b11"
      is binary 3, and "08" has an invalid octal digit, which raises (rescued here). Passing the base 10
      explicitly makes "08" legal."""),

    q("format-directives", r'''
        f = "%05.1f|%-5s|%+d|%x|%08.3f|%e"
        puts f % [3.14159, "ab", 5, 255, 3.14159, 12345.678]
    ''', "003.1|ab   |+5|ff|0003.142|1.234568e+04",
      ["3.1|ab   |5|ff|3.142|1.23e4", "003.1|   ab|+5|FF|0003.142|1.234568e+04",
       "003.1|ab   |+5|ff|0003.14|1.234568e+04"],
      "printf flags: 0 pads with zeros, - pads on the right, + forces a sign",
      """The width includes the decimal point and digits, so `%05.1f` makes `003.1`. `-` left-aligns,
      `+` prints the sign, `%x` is lowercase hexadecimal and `%e` always gives six decimals of mantissa."""),

    q("float-round-half-up", r'''
        p [2.5.round, 3.5.round, -2.5.round, 2.5.round(half: :even),
           1234.567.round(-2)]
    ''', "[3, 4, -3, 2, 1200]", ["[2, 4, -2, 2, 1200.0]", "[2, 4, -3, 2, 1200]", "[3, 4, -2, 2, 1230]"],
      "round goes half away from zero (not to even); a negative digit count rounds to hundreds",
      """Ruby's default is round half away from zero, so 2.5 becomes 3 and -2.5 becomes -3. Banker's rounding
      is opt in with `half: :even`. `round(-2)` rounds to the nearest hundred and returns an Integer."""),

    q("float-sums-and-equality", r'''
        a = [0.1] * 10
        p [0.1 + 0.2 == 0.3, (0.1 + 0.2).round(2) == 0.3, a.sum, a.inject(:+)]
    ''', "[false, true, 1.0, 0.9999999999999999]",
      ["[true, true, 1.0, 1.0]", "[false, true, 0.9999999999999999, 0.9999999999999999]",
       "[false, false, 1.0, 0.9999999999999999]"],
      "Float sums drift, but Array#sum compensates for it and inject(:+) does not",
      """`0.1 + 0.2` is 0.30000000000000004, so the direct comparison is false. `Array#sum` uses
      Kahan-Babuska summation and gets the tidy 1.0, while a plain `inject(:+)` accumulates every rounding
      error and ends at 0.9999999999999999."""),

    q("power-gives-rational-or-big", r'''
        p [2**64, 2**-1, 4**0.5, 2.0**-2, Rational(1, 2) + 0.5]
    ''', "[18446744073709551616, (1/2), 2.0, 0.25, 1.0]",
      ["[0, 0, 2.0, 0.25, 1.0]", "[18446744073709551616, 0.5, 2.0, 0.25, 1.0]",
       "[18446744073709551616, 0, 2, 0.25, (1/1)]"],
      "Integers never overflow, and an integer to a negative power is an exact Rational",
      """Ruby switches to big integers automatically, so 2**64 is exact. `2**-1` keeps the exactness by
      returning the Rational (1/2) rather than 0 or 0.5. Mixing a Rational with a Float produces a Float."""),

    q("symbols-and-strings-differ", r'''
        h = { "a" => 1, a: 2 }
        p [:a == "a", :a.to_s == "a", h["a"], h[:a], h.size]
    ''', "[false, true, 1, 2, 2]", ["[true, true, 1, 2, 2]", "[false, true, 1, 1, 1]", "[false, true, 2, 1, 2]"],
      "A symbol and a string with the same letters are different keys",
      """`:a` and `"a"` are unrelated objects and are never `==`. A hash keeps them as two separate keys, so
      both lookups succeed with different values and the size is 2."""),

    q("array-slice-edges", r'''
        a = [1, 2, 3, 4, 5]
        p [a[1..], a[-2..], a[5], a[5..], a[6..], a[1, 2], a[1...-1]]
    ''', "[[2, 3, 4, 5], [4, 5], nil, [], nil, [2, 3], [2, 3, 4]]",
      ["[[2, 3, 4, 5], [4, 5], nil, nil, nil, [2, 3], [2, 3, 4]]",
       "[[2, 3, 4, 5], [4, 5], nil, [], [], [2, 3], [2, 3, 4]]",
       "[[2, 3, 4, 5], [4, 5], nil, [], nil, [2, 3], [2, 3, 4, 5]]"],
      "A slice that starts exactly at the end is [], one that starts past it is nil",
      """`a[5]` is past the last index, so nil. But `a[5..]` starts at index 5, which equals the length, and
      Ruby treats that as an empty slice; `a[6..]` starts beyond the end and is nil. `1...-1` stops before
      the last element."""),

    q("any-all-none-empty", r'''
        p [[].all?, [].any?, [nil].all?, [nil, false].none?, [0].any?,
           [nil, 1].one?]
    ''', "[true, false, false, true, true, true]",
      ["[false, false, false, true, true, true]", "[true, false, true, true, true, true]",
       "[true, false, false, false, false, true]"],
      "all? of an empty list is true, and these predicates test truthiness, not zero",
      """With no elements nothing can fail, so `[].all?` is true while `[].any?` is false. Without a block the
      methods test each element for truthiness: nil and false fail, while 0 is truthy and counts."""),

    q("empty-reductions", r'''
        p [[].sum, [].inject(:+), [].max, [3].inject(10) { |a, b| a - b },
           [2, 3].inject(:*)]
    ''', "[0, nil, nil, 7, 6]", ["[0, 0, nil, 7, 6]", "[0, nil, 0, 7, 6]", "[nil, nil, nil, 7, 6]"],
      "sum starts at 0 but inject(:+) with no start value has nothing to return",
      """`Array#sum` defaults to 0, so an empty sum is 0. `inject` without an initial value uses the first
      element as the start, so an empty array gives nil, the same as `max`. With an initial value the block
      runs as 10 - 3 = 7."""),

    q("unrun-assignment-declares", r'''
        if false
          x = 1
        end
        p [x, defined?(x), defined?(y)]
    ''', '[nil, "local-variable", nil]', ['[nil, nil, nil]', '[1, "local-variable", nil]',
                                          '[nil, "local-variable", "local-variable"]'],
      "The parser creates a local at the assignment even if it never runs",
      """Ruby decides what is a local variable while parsing, not while running. After the dead `x = 1`,
      `x` exists and is nil, instead of being an undefined name. `y` was never assigned anywhere, so it
      stays undefined."""),

    q("if-without-else-is-nil", r'''
        x = (1 if false)
        y = [(2 unless true)]
        z = (3 if true)
        w = def helper; end
        p [x, y, z, w]
    ''', "[nil, [nil], 3, :helper]", ["[nil, [], 3, :helper]", "[false, [false], 3, nil]",
                                      "[nil, [nil], 3, nil]"],
      "Everything is an expression: a skipped if gives nil, and def gives a symbol",
      """An `if` whose branch does not run evaluates to nil, and `unless true` is the same, which leaves a
      nil element rather than an empty array. A method definition returns its name as a symbol."""),

    q("do-while-runs-once", r'''
        i = 10
        begin
          i += 1
        end while i < 5
        j = 10
        j += 1 while j < 5
        p [i, j]
    ''', "[11, 10]", ["[10, 10]", "[11, 11]", "[10, 11]"],
      "begin ... end while runs the body first; the plain modifier checks first",
      """A loop modifier on a `begin ... end` block is Ruby's do-while: the body runs once before the test, so
      `i` becomes 11. `j += 1 while j < 5` is an ordinary while, tests 10 < 5 first, and never runs."""),

    q("times-step-upto-results", r'''
        p [3.times { }, 1.step(10, 4).to_a, 10.step(1, -4).to_a, 1.upto(0).to_a,
           (1..10).step(4).to_a]
    ''', "[3, [1, 5, 9], [10, 6, 2], [], [1, 5, 9]]",
      ["[[0, 1, 2], [1, 5, 9], [10, 6, 2], [], [1, 5, 9]]", "[3, [1, 5, 9, 10], [10, 6, 2], [], [1, 5, 9]]",
       "[3, [1, 5, 9], [10, 6, 2], [1], [1, 5, 9]]"],
      "times returns the count; step and upto stay within their limit",
      """`Integer#times` returns the receiver (3), not the iterations. `step(10, 4)` stops at 9 because the next
      value would pass 10, a negative step counts down, and `1.upto(0)` produces nothing."""),

    q("escapes-and-bytes", r'''
        p ['a\nb'.length, "a\nb".length, 'it\'s'.length, "tab\t".length,
           '\\'.length,
           "\u00e9".bytesize, "\u00e9".length]
    ''', "[4, 3, 4, 4, 1, 2, 1]", ["[3, 3, 4, 4, 2, 2, 1]", "[4, 3, 5, 4, 1, 1, 1]", "[4, 3, 4, 3, 1, 2, 2]"],
      "Single quotes keep \\n as two characters; characters and bytes are different counts",
      r"""In single quotes only `\'` and `\\` are escapes, so `'a\nb'` is the four characters a, backslash, n, b.
      Double quotes turn `\n` and `\t` into one character each. The accented e is one character but two
      bytes in UTF-8."""),

    # ── Medium: scoping, blocks, methods, strings, collections ─────────────
    q("block-parameters-shadow", r'''
        x = 10
        [1, 2].each { |x| x += 1 }
        y = 5
        [1, 2].each { |i| y += i }
        z = 1
        [5].each { |i; z| z = i }
        p [x, y, z]
    ''', "[10, 8, 1]", ["[12, 8, 5]", "[10, 8, 5]", "[12, 5, 1]"],
      "A block parameter hides an outer variable of the same name; other outer variables are shared",
      """`|x|` declares a fresh `x` for the block, so the outer one is untouched. `y` is not a parameter,
      so the block closes over it and adds 1 and 2. A name after `;` (`|i; z|`) is a block-local variable that
      shadows the outer `z` on purpose."""),

    q("for-loop-closures", r'''
        a = []
        for j in 0..2 do a << -> { j } end
        b = []
        (0..2).each { |k| b << -> { k } }
        p [a.map(&:call), b.map(&:call), j]
    ''', "[[2, 2, 2], [0, 1, 2], 2]", ["[[0, 1, 2], [0, 1, 2], 2]", "[[2, 2, 2], [2, 2, 2], 2]",
                                       "[[0, 1, 2], [2, 2, 2], 2]"],
      "`for` does not open a scope, so its lambdas all share one variable; each does",
      """The body of a `for` loop runs in the surrounding scope, so every lambda captures the same `j`, which
      ends at 2 (and is still visible afterwards). A block passed to `each` gets a new `k` on every call,
      so those lambdas remember 0, 1 and 2."""),

    q("proc-vs-lambda-return", r'''
        def with_lambda
          -> { return 1 }.call
          2
        end

        def with_proc
          proc { return 1 }.call
          2
        end
        p [with_lambda, with_proc]
    ''', "[2, 1]", ["[1, 1]", "[2, 2]", "[1, 2]"],
      "return inside a lambda leaves the lambda; inside a proc it leaves the whole method",
      """A lambda behaves like a small method, so `return` just ends the lambda and the method carries on to
      2. A proc (or block) returns from the method where it was written, so `with_proc` stops at 1 and the
      line returning 2 is never reached."""),

    q("proc-lenient-lambda-strict", r'''
        pr = proc { |a, b| "#{a}-#{b}" }
        la = ->(a, b) { "#{a}-#{b}" }
        r = [pr.call(1), pr.call(1, 2, 3), pr.call([4, 5])]
        r << (la.call(1) rescue "arity")
        p r
    ''', '["1-", "1-2", "4-5", "arity"]',
      ['["1-", "1-2", "[4, 5]-", "arity"]', '["arity", "1-2", "4-5", "arity"]',
       '["1-", "1-2", "4-5", "1-"]'],
      "A proc fills missing arguments with nil and splats one array; a lambda counts strictly",
      """Procs ignore extra arguments, pad missing ones with nil, and unpack a single array argument across
      their parameters. Lambdas check the argument count like methods, so calling the two-parameter lambda
      with one argument raises ArgumentError, which the rescue modifier turns into "arity"."""),

    q("default-and-keyword-arguments", r'''
        def f(a, b = a * 2, *rest, k: b + 1)
          [a, b, rest, k].inspect
        end
        puts [f(1), f(1, 5, 6, k: 0)].join(" ")
    ''', "[1, 2, [], 3] [1, 5, [6], 0]", ["[1, nil, [], nil] [1, 5, [6], 0]",
                                         "[1, 2, [], 3] [1, 5, [], 0]",
                                         "[1, 2, [], 2] [1, 5, [6], 6]"],
      "Defaults can use earlier parameters; the keyword default sees the final b",
      """A default value is evaluated at call time and may refer to parameters on its left, so `b` becomes
      `a * 2` = 2 and the keyword default `b + 1` becomes 3. Extra positional arguments are gathered
      by the splat (6), while `k:` is taken by name."""),

    q("method-missing-without-respond-to", r'''
        class Ghost
          def method_missing(name, *args)
            name.to_s.start_with?("get_") ? name.to_s[4..] : super
          end
        end
        g = Ghost.new
        p [g.get_x, g.respond_to?(:get_x), (g.other rescue "boom")]
    ''', '["x", false, "boom"]', ['["x", true, "boom"]', '["x", false, nil]', '["x", true, nil]'],
      "method_missing answers the call but respond_to? knows nothing about it",
      """`get_x` is not a real method, so Ruby falls back to `method_missing`, which returns "x". `respond_to?`
      does not call `method_missing`; you have to also define `respond_to_missing?`. Anything not starting
      with get_ reaches `super` and raises NoMethodError."""),

    q("accessor-versus-local", r'''
        class Counter
          attr_accessor :n
          def initialize
            @n = 1
          end

          def bump
            n = 5
            self.n += 1
            n
          end
        end
        c = Counter.new
        p [c.bump, c.n]
    ''', "[5, 2]", ["[2, 2]", "[5, 6]", "[5, 1]"],
      "`n = 5` makes a local variable; only `self.n =` calls the setter",
      """Assigning to a bare name inside a method always creates a local variable, even when an
      accessor with that name exists. `self.n += 1` goes through the accessors and turns @n from 1 into 2,
      while the last line `n` now reads the local 5."""),

    q("to-s-versus-inspect", r'''
        class Point
          def to_s = "S"
          def inspect = "I"
        end
        puts "#{Point.new} #{[Point.new]} #{[Point.new].join}"
    ''', "S [I] S", ["S [S] S", "I [I] I", "S [S] [S]"],
      "Interpolation and join use to_s; an Array's own to_s uses inspect on its elements",
      """`"#{obj}"` calls `to_s`, giving S. An array's `to_s` is its `inspect`, which prints every element
      with *its* `inspect`, so the element appears as I. `join` converts each element with `to_s` again."""),

    q("array-kernel-method", r'''
        p [Array(nil), Array(1..3), Array("a\nb"), Array({ a: 1 }), nil.to_a,
           String(nil)]
    ''', '[[], [1, 2, 3], ["a\\nb"], [[:a, 1]], [], ""]',
      ['[[nil], [1, 2, 3], ["a", "b"], [[:a, 1]], [], ""]', '[[], [1..3], ["a\\nb"], [{a: 1}], [], nil]',
       '[[], [1, 2, 3], ["a", "b"], [[:a, 1]], [nil], ""]'],
      "Array() wraps a single value, expands ranges and hashes, and turns nil into []",
      r"""`Array(x)` returns arrays unchanged, calls `to_a` on ranges and hashes, and wraps anything else, so a
      string stays one element (Ruby no longer splits it into lines). `nil` becomes the empty array and
      `String(nil)` is the empty string, not nil."""),

    q("split-edge-cases", r'''
        csv = "a,b,,c,,"
        p [csv.split(",").size, csv.split(",", -1).size, " a  b ".split.size,
           " a b".split(/ /).size, "abc".split("").size]
    ''', "[4, 6, 2, 3, 3]", ["[6, 6, 2, 3, 3]", "[4, 6, 4, 2, 3]", "[4, 4, 2, 3, 1]"],
      "split drops trailing empty fields unless a negative limit is given",
      """Trailing empty strings are removed by default, so the first count is 4. A limit of -1 keeps them
      all (6 fields). Whitespace splitting skips leading blanks and collapses runs, while splitting on
      the regexp / / produces a leading empty field."""),

    q("chomp-chop-strip", r'''
        p ["a\n\n".chomp, "abc".chomp("c"), "abc".chop,
           "a\r\n".chomp, "  a ".lstrip]
    ''', '["a\\n", "ab", "ab", "a", "a "]', ['["a", "ab", "ab", "a", "a "]', '["a\\n", "ab", "abc", "a", "a"]',
                                             '["a\\n", "ab", "ab", "a\\r", "a "]'],
      "chomp removes one line ending, chop removes one character, lstrip only the left side",
      r"""`chomp` takes off a single trailing newline (or \r\n), so "a\n\n" keeps one. With an argument it
      removes that exact suffix. `chop` always drops the last character, and `lstrip` leaves the right side
      alone."""),

    q("gsub-literal-or-pattern", r'''
        puts ["a.b".gsub(".", "-"), "a.b".gsub(/./, "-"), "banana".sub("a", "o"),
              "banana".gsub("a") { |m| m.upcase }].join(" ")
    ''', "a-b --- bonana bAnAnA", ["--- --- bonana bAnAnA", "a-b a-b bonono bAnAnA", "a-b --- bonana banana"],
      "A string pattern is matched literally; a regexp . matches any character",
      """With a String pattern the dot is just a dot, so only that character is replaced. The regexp `/./`
      matches every character. `sub` replaces only the first match and `gsub` all of them; a block receives
      each match and returns its replacement."""),

    q("string-succ-carries", r'''
        p %w[az zz a9 Zz 1.9].map(&:succ)
    ''', '["ba", "aaa", "b0", "AAa", "2.0"]',
      ['["a{", "aaa", "b0", "AAa", "2.0"]', '["ba", "aaa", "b0", "AAa", "1.10"]', '["ba", "{{", "a10", "AAa", "2.0"]'],
      "succ counts like an odometer, carrying through letters and digits",
      """`String#succ` increments the rightmost alphanumeric and carries: "az" becomes "ba" and "zz" becomes
      "aaa". Case is preserved, so "Zz" becomes "AAa". Non-alphanumerics are skipped over, so "1.9" carries
      past the dot into "2.0"."""),

    q("array-assignment-slices", r'''
        a = [1, 2, 3, 4]
        a[1..2] = 9
        a[0, 0] = [7, 8]
        a[6] = 5
        p a
    ''', "[7, 8, 1, 9, 4, nil, 5]", ["[7, 8, 1, 9, 4, 5]", "[7, 8, 9, 3, 4, nil, 5]", "[1, 9, 7, 8, 4, nil, 5]"],
      "Assigning to a slice replaces it; assigning past the end pads with nil",
      """`a[1..2] = 9` swaps the two elements 2 and 3 for the single 9. `a[0, 0] = [...]` replaces a zero
      length slice, which means inserting at the front. Writing index 6 of a five element array fills the gap
      at index 5 with nil."""),

    q("insert-negative-index", r'''
        p [[1, 2, 3].insert(-2, :x), [1, 2, 3].insert(1, :a, :b),
           [1, 2, 3].insert(5, :z)]
    ''', "[[1, 2, :x, 3], [1, :a, :b, 2, 3], [1, 2, 3, nil, nil, :z]]",
      ["[[1, :x, 2, 3], [1, :a, :b, 2, 3], [1, 2, 3, nil, nil, :z]]",
       "[[1, 2, :x, 3], [1, :a, 2, :b, 3], [1, 2, 3, nil, nil, :z]]",
       "[[1, 2, :x, 3], [1, :a, :b, 2, 3], [1, 2, 3, :z]]"],
      "A negative index to insert places the item after that element, counting from the end",
      """For positive positions `insert` puts the new items before that index. A negative index counts from the
      end and inserts *after* that element, so -2 lands between 2 and 3. An
      index beyond the end pads with nil."""),

    q("hash-enumerable-results", r'''
        h = { a: 1, b: 2, c: 3 }
        p [h.select { |_, v| v > 1 }.keys, h.map { |_, v| v > 1 },
           h.find { |_, v| v > 1 }, h.count { |_, v| v > 1 }]
    ''', "[[:b, :c], [false, true, true], [:b, 2], 2]",
      ["[[:b, :c], [:b, :c], [:b, 2], 2]", "[[:b, :c], [false, true, true], [:b, :c], 2]",
       "[[:b, 2], [false, true, true], [:b, 2], 2]"],
      "select keeps a Hash, map always builds an Array, find returns the pair",
      """`Hash#select` returns a hash of the matching pairs, so `.keys` gives [:b, :c]. `map` collects the
      block values, here booleans. `find` returns the first matching key-value pair as a two-element array,
      and `count` just counts."""),

    q("hash-default-block-fetch", r'''
        h = Hash.new { |hash, k| hash[k] = k * 2 }
        a = h[2]
        b = h.fetch(5, :none)
        p [a, b, h.key?(5), h.size, h.fetch(2)]
    ''', "[4, :none, false, 1, 4]", ["[4, 10, true, 2, 4]", "[4, nil, false, 1, 4]", "[4, :none, true, 2, 4]"],
      "[] runs the default block (and stores); fetch and key? never do",
      """Reading a missing key with `[]` calls the block, which here also stores the result. `fetch` does not
      use the default block; it takes its own default or raises. `key?` only looks at what is stored,
      so key 5 is absent and the hash has just the one entry."""),

    q("hash-with-index-pairs", r'''
        h = { a: 1, b: 2 }
        p [h.map.with_index { |(k, v), i| "#{k}#{v}#{i}" },
           h.each_with_index.map { |pair, i| pair.size }]
    ''', '[["a10", "b21"], [2, 2]]', ['[["a10", "b21"], [1, 1]]', '[["a01", "b12"], [2, 2]]',
                                      '[["a1", "b2"], [2, 2]]'],
      "Hash iteration yields [key, value] pairs, so index-based helpers need (k, v), i",
      """With `with_index` or `each_with_index` the block gets the pair as one argument plus the index, so the
      pair must be destructured with `(k, v)`. Without the parentheses `pair` is the whole array,
      which has two elements."""),

    q("equality-flavours", r'''
        p [1 == 1.0, 1.eql?(1.0), 1.equal?(1), "a".equal?("a"), "a".eql?("a"),
           1 === 1.0]
    ''', "[true, false, true, false, true, true]", ["[true, true, true, false, true, true]",
                                                     "[true, false, true, true, true, true]",
                                                     "[false, false, true, false, true, false]"],
      "== converts numbers, eql? demands the same class, equal? demands the same object",
      """`1 == 1.0` is true because numbers compare by value, but `eql?` (the one used for hash keys) also
      requires the same type. `equal?` is object identity: small integers are the same object, two string
      literals are not. `===` for numbers behaves like `==`."""),

    q("hash-key-eql", r'''
        h = { 1 => :a }
        p [h[1.0], h[1], { 1.0 => :x }[1], h.key?(1.0), h.to_a.flatten]
    ''', "[nil, :a, nil, false, [1, :a]]", ["[:a, :a, :x, true, [1, :a]]", "[nil, :a, :x, false, [1, :a]]",
                                            "[nil, :a, nil, false, [1.0, :a]]"],
      "Hash keys compare with eql?, so 1 and 1.0 are different keys",
      """Hashes look keys up with `eql?` and `hash`, not `==`. The integer 1 and the float 1.0 are `==` but
      not `eql?`, so each lookup with the other type misses and returns nil."""),

    q("triple-equals-matrix", r'''
        p [Integer === 3, 3 === Integer, (1..3) === 2, /a/ === "cat",
           String === String, :a === :a]
    ''', "[true, false, true, true, false, true]", ["[true, true, true, true, true, true]",
                                                    "[true, false, true, true, true, true]",
                                                    "[true, false, false, true, false, true]"],
      "=== is the case-equality test; it is not symmetric",
      """`Class === obj` asks whether obj is an instance, so `Integer === 3` is true, but `3 === Integer`
      asks whether the class equals 3 and is false. Ranges test membership, regexps test for a match,
      and `String === String` is false because the class String is not a String instance."""),

    q("case-first-match-wins", r'''
        def kind(x)
          case x
          when Integer, Float then "num"
          when 5 then "five"
          when 1..10 then "small"
          when nil then "nil"
          else "other"
          end
        end
        p [kind(5), kind(5.5), kind(nil), kind("5"), kind(2r)]
    ''', '["num", "num", "nil", "other", "small"]',
      ['["five", "num", "nil", "other", "small"]', '["num", "num", "nil", "small", "small"]',
       '["num", "num", "nil", "other", "num"]'],
      "case checks the branches in order with ===; the first match wins",
      """Because Integer comes first, 5 is matched there and `when 5` can never fire for an integer. A
      Rational is neither Integer nor Float and 5 === 2r is false, but the range test succeeds, giving
      "small". The string "5" fails every test and falls to else."""),

    # ── Hard but legal: object model, ensure, patterns, dup/clone ──────────
    q("bare-super-passes-current-values", r'''
        class Base
          def hi(a, b = 2) = "#{a}#{b}"
        end
        class Kid < Base
          def hi(a, b = 9) = super
        end
        class Kid2 < Base
          def hi(a, b = 9) = super(a)
        end
        p [Kid.new.hi(1), Kid2.new.hi(1)]
    ''', '["19", "12"]',
      ['["12", "19"]', '["12", "12"]', '["19", "19"]'],
      "A bare `super` forwards the current values of the parameters, defaults included",
      """Zero-argument `super` passes along the method's parameters as they are now, so the default 9 that
      `Kid#hi` filled in is sent to `Base#hi`. `super(a)` sends exactly one argument, letting the parent use
      its own default of 2."""),

    q("include-versus-prepend", r'''
        module Loud; def hi = "M" + super; end
        class Animal; def hi = "A"; end
        class Dog < Animal; include Loud; def hi = "D" + super; end
        class Cat < Animal; prepend Loud; def hi = "C" + super; end
        p [Dog.new.hi, Cat.new.hi, Dog.ancestors.first(3), Cat.ancestors.first(3)]
    ''', '["DMA", "MCA", [Dog, Loud, Animal], [Loud, Cat, Animal]]',
      ['["MDA", "MCA", [Dog, Loud, Animal], [Loud, Cat, Animal]]',
       '["DMA", "CMA", [Dog, Loud, Animal], [Cat, Loud, Animal]]',
       '["DA", "MCA", [Dog, Animal, Loud], [Loud, Cat, Animal]]'],
      "include puts the module behind the class; prepend puts it in front",
      """The ancestor chain decides which method runs first. `include` inserts the module after the class, so
      `Dog#hi` runs, then Loud via super, then Animal: DMA. `prepend` inserts it before the class, so Loud
      runs first and its super reaches `Cat#hi`: MCA."""),

    q("constants-are-lexical", r'''
        X = 1
        class Parent
          X = 2
          def x = X
        end
        class Child < Parent
          X = 3
        end
        p [Parent.new.x, Child.new.x, Child::X, Parent::X]
    ''', "[2, 2, 3, 2]", ["[2, 3, 3, 2]", "[1, 1, 3, 2]", "[2, 2, 2, 2]"],
      "A constant in a method body is found from where the method was written",
      """Constants are looked up through the lexical scope (the class bodies around the code), not through the
      receiver's class. `x` is written inside `Parent`, so it sees `Parent::X` = 2 even when called on a
      `Child`, which has its own X that only `Child::X` reaches."""),

    q("bang-methods-return-nil", r'''
        s = +"abc"
        a = [1, 2, 2]
        p [s.upcase!, s.upcase!, s.sub!("x", "y"), s.squeeze!, a.uniq!, a.uniq!,
           a.compact!, a.reject! { |v| v > 5 }]
    ''', '["ABC", nil, nil, nil, [1, 2], nil, nil, nil]',
      ['["ABC", "ABC", "ABC", "ABC", [1, 2], [1, 2], [1, 2], [1, 2]]',
       '["ABC", nil, nil, nil, [1, 2], [1, 2], nil, nil]',
       '["ABC", "ABC", nil, nil, [1, 2], nil, nil, nil]'],
      "Many ! methods return nil when they changed nothing, so never chain on the result",
      """The bang methods mutate in place and return the receiver only if something changed. A second
      `upcase!` on "ABC", a `sub!` with no match and a `uniq!` on distinct elements all hand back nil.
      That is why `s.strip!.upcase` can blow up on a string that was already clean."""),

    q("begin-else-ensure-value", r'''
        a = begin; 1; rescue; 2; else; 3; ensure; 4; end
        b = begin; raise "x"; rescue; 2; else; 3; ensure; 4; end
        c = begin; 1; ensure; 4; end
        p [a, b, c]
    ''', "[3, 2, 1]", ["[4, 4, 4]", "[1, 2, 1]", "[3, 2, 4]"],
      "The value is the else clause when nothing is raised; ensure never changes it",
      """With no error, the body's value is replaced by the `else` clause, so `a` is 3. When something is
      raised, the matching `rescue` supplies the value, so `b` is 2. An `ensure` clause runs for its side
      effects only, and its value is discarded."""),

    q("ensure-with-return", r'''
        def swallow
          raise "boom"
        ensure
          return :quiet
        end

        def order(log)
          return log << :body
        ensure
          log << :ensure
        end
        log = []
        p [swallow, order(log), log]
    ''', "[:quiet, [:body, :ensure], [:body, :ensure]]",
      ["[:quiet, [:body], [:body, :ensure]]", "[:boom, [:body, :ensure], [:body, :ensure]]",
       "[:quiet, [:body], [:body]]"],
      "A return inside ensure cancels the exception; ensure also runs after a return",
      """The `return` in `ensure` replaces the pending RuntimeError, so `swallow` quietly returns :quiet.
      In `order`, the array is returned first and then `ensure` appends to that same array before the caller
      prints it, so both references show :ensure."""),

    q("float-to-s-notation", r'''
        puts [1e12, 1e20, 0.0001, 0.00001, 100.0.to_i, 1234567.0, 2.0e-7].join(" ")
    ''', "1000000000000.0 1.0e+20 0.0001 1.0e-05 100 1234567.0 2.0e-07",
      ["1.0e+12 1.0e+20 0.0001 1.0e-05 100 1234567.0 2.0e-07",
       "1000000000000.0 100000000000000000000.0 0.0001 0.00001 100 1234567.0 0.0000002",
       "1000000000000 1.0e+20 0.0001 1.0e-05 100.0 1234567.0 2.0e-07"],
      "Float#to_s switches to exponent form for very large and for tiny magnitudes",
      """Ruby prints ordinary-sized floats in plain decimal notation (1000000000000.0, 0.0001) and uses
      scientific notation with a signed two-digit exponent for huge or tiny ones (1.0e+20, 1.0e-05). Even
      whole floats keep a `.0`, but `to_i` turns 100.0 into the integer 100."""),

    q("string-range-cover", r'''
        r = ("a".."e")
        p [r.include?("cc"), r.cover?("cc"), r === "cc", (1..5).include?(2.5),
           (1..5).to_a.include?(2.5)]
    ''', "[false, true, true, true, false]",
      ["[true, true, true, true, false]", "[false, false, false, true, false]",
       "[false, true, true, false, false]"],
      "include? on a string range walks its elements; cover? and === only compare",
      """`("a".."e").include?("cc")` steps through a, b, c, d, e and "cc" is not one of them. `cover?` and `===`
      just check that "a" <= "cc" <= "e" by string order, which is true. A numeric range has no steps to
      walk, so 2.5 is included while a list built from it is not."""),

    q("dup-versus-clone", r'''
        s = +"a"
        def s.hi = "hi"
        t = s.dup
        u = s.clone
        f = "x".freeze
        p [s.respond_to?(:hi), t.respond_to?(:hi), u.respond_to?(:hi),
           f.dup.frozen?, f.clone.frozen?, f.clone(freeze: false).frozen?]
    ''', "[true, false, true, false, true, false]",
      ["[true, true, true, false, false, false]", "[true, false, true, true, true, false]",
       "[true, false, false, false, true, true]"],
      "clone keeps singleton methods and the frozen state; dup keeps neither",
      """Both make a shallow copy, but `clone` also copies the singleton methods and the frozen flag, while
      `dup` returns a plain unfrozen copy. `clone(freeze: false)` is the way to copy a frozen object and
      get an unfrozen one."""),

    q("freeze-is-shallow", r'''
        a = [+"x"].freeze
        a[0] << "y"
        b = (a << 1 rescue "frozen")
        p [a, b, 1.frozen?, :a.frozen?, nil.frozen?, [].frozen?, (1..2).frozen?]
    ''', '[["xy"], "frozen", true, true, true, false, true]',
      ['[["x"], "frozen", true, true, true, false, true]', '[["xy"], [1], true, true, true, false, true]',
       '[["xy"], "frozen", true, false, true, false, false]'],
      "freeze locks the array itself, not the objects inside it",
      """A frozen array refuses `<<`, which raises FrozenError (rescued here), but its elements are separate
      objects and can still be changed, so the string becomes "xy". Numbers, symbols, nil and range literals
      are always frozen; a new array is not."""),

    q("pattern-pin-and-rebind", r'''
        a = 5
        r = case 5
            in ^a then :pin
            end
        s = case 7
            in a then a
            end
        p [r, s, a]
    ''', "[:pin, 7, 7]", ["[:pin, 7, 5]", "[:pin, 5, 5]", "[5, 7, 7]"],
      "A bare name in a pattern binds (overwriting a local); ^name compares",
      """In `case/in`, an identifier is a binding, not a comparison, so `in a` matches anything and assigns 7
      to the existing variable `a`. To compare against the old value you must pin it with `^a`, as the first
      case does, which is why `a` is 7 by the time it is printed."""),

    q("keywords-versus-hash-argument", r'''
        def g(*args, **kw) = [args.size, kw.size]
        p [g({ a: 1 }), g(a: 1), g({ a: 1 }, b: 2)]
    ''', "[[1, 0], [0, 1], [1, 1]]", ["[[0, 1], [0, 1], [1, 1]]", "[[1, 0], [0, 1], [0, 2]]",
                                      "[[1, 0], [1, 0], [1, 1]]"],
      "Braces make a positional hash; bare key: value pairs are keywords",
      """Since Ruby 3 a literal hash in braces is an ordinary positional argument and goes into `args`, while
      bare `a: 1` pairs are keyword arguments and go into `kw`. The two kinds are no longer converted into
      each other, so the third call splits one of each."""),

    q("safe-navigation-chain", r'''
        s = nil
        p [s&.length, s&.length.to_i, s.to_a.size, s&.length.nil?]
    ''', "[nil, 0, 0, true]", ["[nil, nil, 0, true]", "[nil, 0, nil, true]", "[0, 0, 0, false]"],
      "&. only guards its own call: the rest of the chain still runs on nil",
      """`s&.length` returns nil when `s` is nil, and that is where the shortcut ends. A further `.to_i` is
      then called on nil and gives 0 instead of being skipped, unlike optional chaining in JavaScript, which
      skips the whole chain."""),
)
