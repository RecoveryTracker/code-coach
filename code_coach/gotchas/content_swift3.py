"""Gotchas, Swift (third deck): swiftc then the exe; notes are in langs.py (the `swift` entry).

Same rules as content_swift2.py: standard library only (never `import Foundation`: its first build takes ~90 s),
never a Set or Dictionary, nothing that traps, and cards that need a log keep it in a global `var log = ""` and
print it once. Optionals are printed through `as Any` so the answer shows `Optional(2)` and `nil` honestly. This
deck is pattern matching and enums, initialisers and observers, the Sequence and String library, and numerics.
"""

from __future__ import annotations

from .items import Item, make

q = make("swift")

ITEMS: tuple[Item, ...] = (
    # ── Batch 1: patterns, initialisers, strings, defer ────────────────────
    q("where-applies-to-the-last-pattern-only", r'''
        enum E { case a(Int), b(Int) }

        func f(_ e: E) -> String {
            switch e {
            case .a(let x), .b(let x) where x > 5: return "big-or-a"
            default: return "other"
            }
        }
        print(f(.a(1)), f(.b(1)), f(.b(9)), f(.a(9)))
    ''', "big-or-a other big-or-a big-or-a",
    ["other other big-or-a big-or-a", "big-or-a big-or-a big-or-a big-or-a",
     "other other big-or-a other"],
      "A `where` after a comma-separated list of patterns belongs to the last pattern only",
      """The first pattern, `.a(let x)`, has no condition of its own, so every `.a` matches. Only
      `.b(let x)` carries `where x > 5`. To restrict both you would need two separate cases."""),

    q("memberwise-init-skips-defaulted-properties", r'''
        struct P {
            var x = 1
            var y = 2
        }
        print(P(y: 5).x, P(x: 3).y, P().x, P(x: 7, y: 8).y)
    ''', "1 2 1 8", ["5 3 1 8", "1 2 0 8", "1 5 1 8"],
      "The memberwise initialiser has a default for every property that has one",
      """Each argument can be left out when its property has a default value, but the ones given
      must stay in declaration order and keep their labels. `P(y: 5)` keeps the default x = 1."""),

    q("observers-do-not-fire-in-init", r'''
        var log = ""
        struct T {
            var v = 0 { didSet { log += "d" } }
            init() { v = 5 }
        }
        var t = T()
        let a = log
        t.v = 1
        print("[\(a)] [\(log)] \(t.v)")
    ''', "[] [d] 1", ["[d] [dd] 1", "[d] [d] 1", "[] [] 1"],
      "Setting a property inside its own type's init does not call willSet or didSet",
      """While the object is still being initialised, assignments are plain stores, so `v = 5` in the
      init runs no observer. The later `t.v = 1` is an ordinary assignment, and fires `didSet` once."""),

    q("class-func-dispatches-on-the-dynamic-type", r'''
        class A {
            class func who() -> String { "A" }
            func call() -> String { Self.who() + "/" + A.who() }
        }
        class B: A {
            override class func who() -> String { "B" }
        }
        print(B().call(), A().call())
    ''', "B/A A/A", ["A/A A/A", "B/B A/A", "B/A B/A"],
      "`Self.who()` looks at the real type of the object; `A.who()` always means A",
      """Inside `call`, `Self` is the dynamic type, B for a B instance, so the overridden class method
      runs. Writing the class name `A.who()` is a fixed choice and always gives "A"."""),

    q("prefix-suffix-and-drop-never-trap", r'''
        let s = "hello"
        print(s.prefix(10), s.suffix(2), s.dropFirst(10).isEmpty, s.dropLast(2),
              s.prefix(0).count)
    ''', "hello lo true hel 0",
    ["hel lo true hel 0", "hello lo true hell 0", "hello llo true hel 0"],
      "These ask for at most that many characters, so asking for too many is not an error",
      """`prefix(10)` gives the whole string, since only five exist, and `dropFirst(10)` leaves nothing.
      `suffix(2)` is the last two characters, `dropLast(2)` removes them, and `prefix(0)` is empty."""),

    q("split-drops-empty-pieces-by-default", r'''
        let s = "a,,b,"
        let kept = s.split(separator: ",")
        let all = s.split(separator: ",", omittingEmptySubsequences: false)
        print(kept.count, all.count, kept.joined(separator: "+"), "|",
              all.joined(separator: "+"))
    ''', "2 4 a+b | a++b+", ["4 4 a++b+ | a++b+", "2 3 a+b | a++b", "3 4 a+b+ | a++b+"],
      "split throws away empty pieces unless you pass omittingEmptySubsequences: false",
      """By default only the non-empty pieces "a" and "b" remain. With the flag off, the empty piece
      between the commas and the one after the last comma are kept too, giving four pieces."""),

    q("first-index-is-an-optional", r'''
        let a = [10, 20, 30]
        print(a.firstIndex(of: 30) as Any, a.firstIndex(of: 99) as Any,
              a.firstIndex(of: 30)! + 1)
    ''', "Optional(2) nil 3", ["2 -1 3", "Optional(2) Optional(-1) 3", "Optional(30) nil 3"],
      "firstIndex(of:) returns an optional index, nil when the value is missing, never -1",
      """The value 30 is at index 2, wrapped in an Optional. A missing value gives `nil`, and the
      force-unwrapped `! + 1` adds one to the index (not to the element)."""),

    q("int-exactly-and-truncation", r'''
        let h = 2.5
        print(Int(2.9), Int(-2.9), Int(exactly: h) as Any,
              Int(exactly: 3.0) as Any, Int(h.rounded(.up)))
    ''', "2 -2 nil Optional(3) 3",
    ["3 -3 nil Optional(3) 3", "2 -2 Optional(2) Optional(3) 3", "2 -3 nil 3 3"],
      "Int(double) cuts toward zero; Int(exactly:) gives nil unless the value is a whole number",
      """`Int(-2.9)` drops the fraction and gives -2. `Int(exactly: 2.5)` refuses, returning nil, while
      `Int(exactly: 3.0)` works. `rounded(.up)` makes 2.5 into 3.0 first, so Int then gives 3."""),

    q("print-separator-and-terminator", r'''
        print(1, 2, separator: "-", terminator: "|")
        print("x", terminator: "")
        print("y")
    ''', "1-2|xy", ["1-2|x y", "1 2|xy", "1-2xy"],
      "separator goes between the items of one print; terminator replaces its closing newline",
      """The first call joins 1 and 2 with a dash and ends with `|` instead of a newline. The second
      ends with nothing at all, so the last print continues on the same line."""),

    q("defer-runs-before-the-catch", r'''
        var log = ""
        enum E: Error { case boom }
        func f() throws {
            defer { log += "1" }
            defer { log += "2" }
            log += "a"
            throw E.boom
        }
        do { try f(); log += "x" } catch { log += "c" }
        print(log)
    ''', "a21c", ["a12c", "ac21", "a21cx"],
      "Deferred blocks run, last first, as the function is left, before the caller's catch",
      """The function logs "a" and throws. As it exits, its defers run in reverse order of writing,
      "2" then "1". Only after that does the `catch` block in the caller run, adding "c"."""),

    # ── Batch 2: closures, operators, sequences ────────────────────────────
    q("autoclosure-delays-the-argument", r'''
        var n = 0
        func bump() -> Bool { n += 1; return true }
        func both(_ a: Bool, _ b: @autoclosure () -> Bool) -> Bool { a && b() }
        _ = both(false, bump())
        _ = both(true, bump())
        _ = both(true, bump())
        print(n)
    ''', "2", ["3", "0", "1"],
      "An @autoclosure argument is only evaluated if the function actually calls it",
      """`bump()` is wrapped in a closure instead of being run at the call. Because `false && ...`
      short-circuits, the first call never runs it, and only the other two calls do: n is 2."""),

    q("enum-comparable-by-declaration-order", r'''
        enum Level: Comparable { case low, mid, high }
        let sorted = [Level.high, .low, .mid].sorted()
        print(sorted.map { "\($0)" }.joined(separator: " "), Level.mid < .high,
              Level.high > .mid, Level.low == .low)
    ''', "low mid high true true true",
    ["high low mid true true true", "low mid high false true true", "low mid high true false true"],
      "An enum without payloads can be Comparable, ordered by where each case is declared",
      """Swift synthesises `<` from the declaration order, not from the names, so low < mid < high.
      Sorting an array of them therefore gives low, mid, high, not alphabetical high, low, mid."""),

    q("zip-stops-at-the-shorter-sequence", r'''
        let z = Array(zip([1, 2, 3], ["a", "b"]))
        let joined = z.map { "\($0.0)\($0.1)" }.joined(separator: ",")
        print(z.count, joined, zip("abc", 1...2).map { String($0.0) }.count)
    ''', "2 1a,2b 2", ["3 1a,2b,3 3", "2 1a,2b 3", "3 1a,2b 2"],
      "zip makes pairs only as long as both sequences have an element",
      """The first sequence has three items but the second has two, so two pairs come out and the 3 is
      ignored. The same happens for the letters "abc" and the range 1...2."""),

    q("enumerated-offsets-are-not-indices", r'''
        let s = [10, 20, 30, 40][1...]
        print(s.enumerated().map { $0.offset }, Array(s.indices), s[1], s.first!)
    ''', "[0, 1, 2] [1, 2, 3] 20 20",
    ["[1, 2, 3] [1, 2, 3] 20 20", "[0, 1, 2] [0, 1, 2] 10 20", "[0, 1, 2] [1, 2, 3] 10 20"],
      "enumerated() counts from 0, but an array slice keeps the indices of the original",
      """The slice holds 20, 30, 40 and remembers their positions 1, 2, 3 in the big array. So `s[1]`
      is 20 (not 10), while the `offset` from `enumerated()` is a fresh counter starting at 0."""),

    q("custom-operator-groups-left-by-default", r'''
        infix operator ^^: MultiplicationPrecedence
        func ^^ (a: Int, b: Int) -> Int {
            var r = 1
            for _ in 0..<b { r *= a }
            return r
        }
        print(2 ^^ 3 ^^ 2, 2 ^^ (3 ^^ 2), 2 + 3 ^^ 2, 2 * 3 ^^ 2)
    ''', "64 512 11 36", ["512 512 11 18", "64 512 11 18", "512 512 11 36"],
      "A custom operator takes the precedence group you give it, and that group is left-associative",
      """MultiplicationPrecedence groups from the left, so `2 ^^ 3 ^^ 2` is `(2 ^^ 3) ^^ 2` = 64, and
      it ties with `*`: `2 * 3 ^^ 2` is `(2 * 3) ^^ 2` = 36. It still binds tighter than `+`."""),

    q("multiline-literal-indent-follows-the-closing-quotes", r'''
        let s = """
            a
              b
            """
        print(s.split(separator: "\n").joined(separator: "/"), s.count)
    ''', "a/  b 5", ["a/b 3", "    a/      b 13", "a/  b 6"],
      "A multi-line literal removes the indentation of its closing delimiter from every line",
      """The closing quotes are indented four spaces, so four spaces are stripped from each line. "b" was
      indented two more, so it keeps them, and there is no final newline: "a", newline, two spaces, "b" is 5."""),

    q("type-of-the-library-results", r'''
        let s = "hello"
        print(type(of: s.prefix(2)), type(of: Array(s)), type(of: s.reversed()),
              type(of: s.count))
    ''', "Substring Array<Character> ReversedCollection<String> Int",
    ["String Array<String> String Int", "Substring Array<Character> String Int",
     "String Array<Character> ReversedCollection<String> Int"],
      "prefix gives a Substring and reversed() a lazy view, not a new String",
      """A String is a collection of Characters, so `Array(s)` is an array of Characters. `prefix`
      returns a Substring that shares the original's storage, and `reversed()` returns a wrapper over
      the string, which only becomes a String if you convert it."""),

    q("max-and-min-by-return-the-first-of-equals", r'''
        struct K { let k: Int; let tag: Character }
        let a = [K(k: 1, tag: "a"), K(k: 3, tag: "b"), K(k: 3, tag: "c"),
                 K(k: 1, tag: "d")]
        let hi = a.max { $0.k < $1.k }!
        let lo = a.min { $0.k < $1.k }!
        print(hi.tag, lo.tag)
    ''', "b a", ["c d", "b d", "c a"],
      "With ties, max(by:) and min(by:) both keep the earliest element, not the latest",
      """A later element replaces the current best only when it is strictly better. So of the two 3s the
      first, "b", wins, and of the two 1s the first, "a", wins."""),

    q("reduce-folds-from-the-left", r'''
        let v = [10, 2, 3]
        print(v.reduce(100) { $0 - $1 }, v.reduce(into: "") { $0 = "\($1)" + $0 },
              v.reduce(1, *))
    ''', "85 3210 60", ["85 1023 60", "-15 3210 60", "85 3210 6"],
      "reduce starts from the initial value and combines it with each element, first to last",
      """With 100 as the start it computes ((100 - 10) - 2) - 3 = 85. The string version puts each new
      number in front of what it has, giving "3210". And `reduce(1, *)` is 1 x 10 x 2 x 3 = 60."""),

    q("is-number-is-unicode-aware", r'''
        let c: Character = "\u{0663}"
        print(c.isNumber, c.wholeNumberValue as Any, c.asciiValue as Any,
              Character("5").wholeNumberValue as Any, c.isLetter)
    ''', "true Optional(3) nil Optional(5) false",
    ["false nil nil Optional(5) false", "true Optional(3) Optional(99) Optional(5) false",
     "true Optional(3) nil Optional(53) false"],
      "Character.isNumber and wholeNumberValue understand digits of other scripts",
      """U+0663 is the Arabic-Indic digit three: it is a number with value 3 and is not a letter. It is
      not ASCII, so `asciiValue` is nil. For "5" the whole-number value is 5, not its code 53."""),

    # ── Batch 3: closures, numerics, wrappers, printing ────────────────────
    q("each-call-makes-its-own-captured-variable", r'''
        func make() -> () -> Int {
            var n = 0
            return { n += 1; return n }
        }
        let c1 = make()
        let c2 = make()
        _ = c1()
        _ = c1()
        print(c1(), c2(), c1())
    ''', "3 1 4", ["3 3 4", "1 1 1", "3 1 3"],
      "Every call to make() creates a new `n`, which its closure keeps alive and shares only with itself",
      """`c1` and `c2` each captured their own variable, so `c2` starts from scratch. The closure's
      count survives between calls: `c1` has been called twice already, so it gives 3 and then 4."""),

    q("smart-shifts-do-not-trap", r'''
        let one = 1, neg = -8, eight = 8
        print(one << 70, neg >> 70, eight >> -1, one &<< 65, neg >> 1)
    ''', "0 -1 16 2 -4",
    ["0 -1 4 2 -4", "0 0 16 2 -4", "1 -1 16 2 -4"],
      "Swift's << and >> are 'smart': too big a count shifts everything out, and a negative one reverses",
      """Shifting `1` left by 70 pushes it off the end and leaves 0; shifting a negative number right by
      70 leaves -1 (the sign bits). `8 >> -1` is really a left shift by 1: 16. The masking `&<<` uses
      65 & 63 = 1."""),

    q("nan-is-not-equal-to-itself-even-in-contains", r'''
        let n = Double.nan
        print(n == n, n != n, n < 1, n > 1, [n].contains(n), n.isNaN)
    ''', "false true false false false true",
    ["true false false false true true", "false true false false true true",
     "false true true false false true"],
      "NaN compares unequal to everything, itself included, so even `contains` cannot find it",
      """Every ordering comparison with NaN is false, and `!=` is true. `contains` uses `==`, so an
      array holding NaN does not contain NaN. `isNaN` is the only way to ask."""),

    q("optional-bool-comparisons", r'''
        let t: Bool? = true, f: Bool? = false, n: Bool? = nil
        print(t == true, f == true, n == true, n == false, n != true, f ?? true)
    ''', "true false false false true false",
    ["true false false true true false", "true false false false false false",
     "true false false false true true"],
      "A nil Bool is neither == true nor == false, and `??` only replaces nil",
      """Comparing an optional with a plain value gives false for nil both ways, so `n == false` is
      false, and `n != true` is true. `f ?? true` keeps the real value false, since f is not nil."""),

    q("property-wrapper-init-skips-the-clamp", r'''
        @propertyWrapper struct Clamped {
            private var value: Int
            var wrappedValue: Int {
                get { value }
                set { value = min(max(newValue, 0), 10) }
            }
            init(wrappedValue: Int) { value = wrappedValue }
        }
        struct S { @Clamped var level = 50 }
        var s = S()
        let first = s.level
        s.level = 50
        print(first, s.level)
    ''', "50 10", ["10 10", "50 50", "10 50"],
      "The initial value goes through the wrapper's init, which stored it without clamping",
      """The `= 50` default calls `init(wrappedValue:)`, which assigns the private storage directly, so
      the setter's clamp never runs. The later assignment `s.level = 50` does use the setter: 10."""),

    q("static-let-initialises-once-on-first-use", r'''
        var log = ""
        struct C {
            static let shared: Int = { log += "i"; return 5 }()
        }
        let a = log.count
        _ = C.shared
        _ = C.shared
        print(a, log.count, C.shared + 1)
    ''', "0 1 6", ["1 2 6", "0 0 6", "0 2 6"],
      "A static let is computed lazily, once, the first time it is read",
      """Declaring the property runs nothing, so the log is still empty (0). The first read runs the
      closure and logs one "i"; the later reads reuse the stored 5. So the log has one character."""),

    q("reversed-then-enumerated-versus-the-other-way", r'''
        let v = [1, 2, 3]
        let a = v.reversed().enumerated().map { $0.offset * 10 + $0.element }
        let b = v.enumerated().reversed().map { $0.offset * 10 + $0.element }
        print(a, b)
    ''', "[3, 12, 21] [23, 12, 1]",
    ["[3, 12, 21] [3, 12, 21]", "[23, 12, 1] [3, 12, 21]", "[1, 12, 23] [3, 12, 21]"],
      "The order of the calls matters: the counter goes with the elements or with the positions",
      """`reversed().enumerated()` numbers the reversed list 0, 1, 2 against the elements 3, 2, 1.
      `enumerated().reversed()` pairs first (0, 1), (1, 2), (2, 3) and then reverses the pairs, so the
      counters run 2, 1, 0 against 3, 2, 1."""),

    q("for-case-let-skips-nil-and-filters", r'''
        var s = 0
        var seen = ""
        for case let x? in [1, nil, 3] { s += x; seen += "\(x)" }
        for case 2...5 in [1, 3, 7] { seen += "!" }
        print(s, seen)
    ''', "4 13!", ["4 13", "4 13!!", "4 1nil3!"],
      "`for case` runs the body only for the elements that match the pattern",
      """`let x?` matches only the non-nil elements, so 1 and 3 are added and the nil is skipped. The
      pattern `2...5` matches only 3 of the second array, so exactly one "!" is added."""),

    q("convenience-init-delegates-before-it-finishes", r'''
        var log = ""
        class C {
            init(a: Int) { log += "D" }
            convenience init() { log += "c1"; self.init(a: 5); log += "c2" }
        }
        _ = C()
        print(log)
    ''', "c1Dc2", ["Dc1c2", "c1c2D", "Dc2"],
      "A convenience init may run code first, must call self.init, and then carries on",
      """The statements before `self.init` run first (as long as they do not touch `self`), then the
      designated init runs and logs "D", and the rest of the convenience body finishes after it."""),

    q("nested-arrays-are-independent-values", r'''
        var g = Array(repeating: Array(repeating: 0, count: 2), count: 2)
        g[0][0] = 1
        var h = g
        h[1][1] = 9
        print(g, h)
    ''', "[[1, 0], [0, 0]] [[1, 0], [0, 9]]",
    ["[[1, 0], [1, 0]] [[1, 0], [1, 9]]", "[[1, 0], [0, 9]] [[1, 0], [0, 9]]",
     "[[1, 0], [0, 0]] [[1, 0], [0, 0]]"],
      "The rows are separate array values, and `var h = g` copies the whole grid",
      """Unlike Python's `[[0] * 2] * 2`, repeating an array stores independent copies, so changing
      `g[0][0]` leaves the second row alone. `h` is a value copy of `g`, so its change stays in `h`."""),
)
