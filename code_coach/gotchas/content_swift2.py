"""Gotchas, Swift (second deck): swiftc then the exe; notes are in langs.py (the `swift` entry).

Standard library only (no Foundation: its first build takes ~90 s), never a Set or Dictionary, never anything
that traps (overflow uses `&+`, ranges are valid, nothing is force-unwrapped unless it is certainly there).
Cards that need a log keep it in a global `var log = ""` and print it once.
"""

from __future__ import annotations

from .items import Item, make

q = make("swift")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics with a real trap ──────────────────────────────
    q("integer-division-and-literals", r'''
        let d: Double = 7 / 2
        let n = 7
        print(n / 2, -n / 2, -n % 3, d, Double(n / 2))
    ''', "3 -3 -1 3.5 3.0",
      ["3 -4 2 3.5 3.0", "3 -3 -1 3.0 3.0", "3 -3 -1 3.5 3.5"],
      "Int variables divide as integers, but the literals in `7 / 2` become Doubles",
      """`n / 2` is Int division, truncated toward zero, and `%` keeps the sign of the left side. In
      `let d: Double = 7 / 2` both literals are typed as Double from the context, so the result is 3.5. Casting
      after an Int division, `Double(n / 2)`, is too late."""),

    q("arrays-copy-on-assignment", r'''
        var a = [1, 2, 3]
        var b = a
        b.append(4)
        a[0] = 9
        print(a, b)
    ''', "[9, 2, 3] [1, 2, 3, 4]",
      ["[9, 2, 3, 4] [9, 2, 3, 4]", "[1, 2, 3] [1, 2, 3, 4]", "[9, 2, 3] [9, 2, 3, 4]"],
      "Arrays are values: each variable behaves like it has its own copy",
      """`var b = a` gives `b` an independent array, so appending to `b` does not touch `a`, and changing
      `a[0]` does not touch `b`. (Swift copies lazily, only when one of them is first modified.)"""),

    q("coalesce-binds-looser-than-plus", r'''
        let a: Int? = nil
        let b: Int? = 3
        print(b ?? 0 + 1, (b ?? 0) + 1, a ?? 0 + 1, b.map { $0 * 2 } ?? -1)
    ''', "3 4 1 6", ["4 4 1 6", "3 4 0 6", "3 4 1 -1"],
      "`b ?? 0 + 1` is `b ?? (0 + 1)`: the fallback is only used when b is nil",
      """Because `+` binds tighter than `??`, a non-nil `b` is returned as it is (3), without the 1 added. Only
      the parenthesised version adds 1 to the value. `map` runs its closure only for a non-nil optional."""),

    q("closures-capture-for-and-while", r'''
        var fs: [() -> Int] = []
        for i in 1...3 { fs.append { i } }
        var k = 1
        while k <= 3 {
            fs.append { k }
            k += 1
        }
        print(fs.map { $0() })
    ''', "[1, 2, 3, 4, 4, 4]",
      ["[1, 2, 3, 1, 2, 3]", "[3, 3, 3, 4, 4, 4]", "[1, 2, 3, 3, 3, 3]"],
      "A for-in loop makes a fresh constant each round; a while loop shares one variable",
      """Each iteration of `for i in 1...3` has its own `i`, so those closures remember 1, 2 and 3. The `while`
      closures all capture the single variable `k`, which is 4 when the loop ends."""),

    q("tuples-compare-element-by-element", r'''
        print((1, "b") < (1, "a"), (1, 2) < (1, 3), (2, 0) < (1, 9),
              (1, 2) == (1, 2))
    ''', "false true false true",
      ["true true false true", "false true true true", "true true true true"],
      "Tuples compare lexicographically: the first differing element decides",
      """`(1, "b") < (1, "a")` ties on 1 and then compares "b" with "a", which is false. `(2, 0) < (1, 9)` is
      decided by the first elements alone, so the 9 never matters."""),

    q("stride-to-versus-through", r'''
        let up = Array(stride(from: 1, to: 10, by: 3))
        let through = Array(stride(from: 1, through: 10, by: 3))
        let down = Array(stride(from: 10, to: 0, by: -4))
        print(up, through, down, (0..<0).isEmpty)
    ''', "[1, 4, 7] [1, 4, 7, 10] [10, 6, 2] true",
      ["[1, 4, 7, 10] [1, 4, 7, 10] [10, 6, 2] true", "[1, 4, 7] [1, 4, 7, 10] [10, 6, 2, -2] true",
       "[1, 4, 7] [1, 4, 7, 10] [10, 6, 2] false"],
      "`to:` excludes the end value, `through:` includes it",
      """`stride(from:to:by:)` stops before reaching the end value, so 10 is left out of the first list.
      `through:` includes the end if the steps land on it. `0..<0` is an empty range, so `isEmpty` is true."""),

    q("string-slices-by-index", r'''
        let s = "hello world"
        let i = s.firstIndex(of: " ")!
        print(s[..<i], s[s.index(after: i)...], s[i...].count, s.prefix(3),
              s.suffix(3), s.dropFirst(8))
    ''', "hello world 6 hel rld rld",
      ["hello world 5 hel rld rld", "hello world 6 hel orl rld", "hello world 6 hel rld wor"],
      "Slicing starts from an index, and the slice from the space includes the space",
      """`s[..<i]` stops before the space and `s[s.index(after: i)...]` starts after it. But `s[i...]` starts at
      the space itself, so it has six characters, " world". `dropFirst(8)` removes the first eight."""),

    q("string-unicode-counts-and-equality", r'''
        let flag = "\u{1F1FA}\u{1F1F8}"
        let a = "caf\u{E9}"
        let b = "cafe\u{301}"
        print(flag.count, flag.unicodeScalars.count, flag.utf8.count,
              a == b, a.utf8.count, b.utf8.count)
    ''', "1 2 8 true 5 6",
      ["2 2 8 true 5 6", "1 2 8 false 5 6", "1 1 4 true 5 5"],
      "A Character is one visible symbol, however many scalars and bytes it takes",
      """A flag is two regional-indicator scalars of four bytes each, and Swift counts the pair as one
      Character. `a` and `b` are the same text in two spellings ("é" in one scalar, or e plus an accent), and
      Swift treats canonically equal strings as equal, even though their UTF-8 differs in length."""),

    # ── Medium ─────────────────────────────────────────────────────────────
    q("wrapping-truncating-clamping", r'''
        let m = Int8.max
        print(m &+ 1, m.addingReportingOverflow(1).overflow,
              UInt8(truncatingIfNeeded: 300), Int8(clamping: 300),
              UInt8.max &+ 1, Int8.min &- 1)
    ''', "-128 true 44 127 0 127",
      ["128 true 44 127 256 -129", "-128 false 44 127 0 127", "-128 true 300 127 0 127"],
      "Plain + traps on overflow; &+ wraps, truncatingIfNeeded keeps low bits, clamping saturates",
      """`&+` wraps around in two's complement, so Int8.max &+ 1 is -128. `UInt8(truncatingIfNeeded: 300)` keeps
      the low 8 bits (44), while `Int8(clamping: 300)` stops at the largest value, 127."""),

    q("double-printing", r'''
        let a = 5 / 2 * 2.0
        let f: Float = 1
        print(1.0, 0.1 + 0.2, 1e16, 1.5e-5, 100.0 / 3, f / 3, a)
    ''', "1.0 0.30000000000000004 1e+16 1.5e-05 33.333333333333336 0.33333334 5.0",
      ["1 0.3 10000000000000000 0.000015 33.333333333333336 0.33333334 4.0",
       "1.0 0.30000000000000004 1e+16 1.5e-05 33.333333333333336 0.3333333333333333 5.0",
       "1.0 0.30000000000000004 1e+16 1.5e-05 33.333333333333336 0.33333334 4.0"],
      "Doubles print the shortest exact text, with e-notation for big and tiny; literals share a type",
      """`5 / 2 * 2.0` mixes only literals, so all of them are Doubles and 5 / 2 is 2.5, giving 5.0, not the 4
      an Int division would. Doubles always show a decimal point, and Float prints fewer digits than Double."""),

    q("array-slice-keeps-indices", r'''
        let a = [10, 20, 30, 40]
        let sl = a[1...2]
        print(sl.startIndex, sl[1], sl.first!, Array(sl)[0], sl.count, sl.endIndex)
    ''', "1 20 20 20 2 3",
      ["0 20 20 20 2 2", "1 10 20 20 2 3", "0 10 10 10 2 2"],
      "A slice keeps the indices of the array it came from",
      """`a[1...2]` is an ArraySlice that still numbers its elements 1 and 2, so `sl[1]` is 20 and `sl[0]`
      would trap. Wrapping it in `Array(...)` makes a new array that starts again at 0."""),

    q("if-var-shadows", r'''
        var v: Int? = 5
        if var v = v { v += 1 }
        print(v as Any, v!, v.map { $0 + 1 } as Any)
    ''', "Optional(5) 5 Optional(6)",
      ["Optional(6) 6 Optional(7)", "5 5 6", "Optional(5) 5 6"],
      "`if var v = v` declares a new, local v; the original is untouched",
      """The unwrapped `v` inside the braces is a separate variable that disappears at the closing brace, so
      adding 1 to it changes nothing outside. An optional prints as `Optional(5)` when shown as Any, and `map`
      keeps the optional wrapper."""),

    q("fallthrough-skips-the-test", r'''
        var s = ""
        switch 1 {
        case 1: s += "a"; fallthrough
        case 2: s += "b"
        case 3: s += "c"
        default: s += "d"
        }
        print(s)
    ''', "ab", ["a", "abc", "abcd"],
      "Swift cases do not fall through, unless you write fallthrough, and then for one case only",
      """Case 1 runs and `fallthrough` enters the next case body without checking its pattern, so "b" is
      added. That case has no `fallthrough` of its own, so the switch ends there."""),

    q("property-observers-always-fire", r'''
        var log = ""
        struct T {
            var n = 0 {
                willSet { log += "w\(newValue) " }
                didSet { log += "d\(oldValue) " }
            }
        }
        var t = T()
        t.n = 5
        t.n = 5
        print(log)
    ''', "w5 d0 w5 d5", ["w5 d0", "w0 d5 w5 d5", "w5 d0 w5 d0"],
      "Observers fire on every assignment, even of the same value, and not during init",
      """`willSet` sees the incoming value and `didSet` the previous one. Assigning 5 a second time still
      triggers both, with the old value now 5. Setting the default `0` at creation triggers nothing."""),

    q("lazy-property-first-use", r'''
        var log = ""
        class C {
            lazy var v: Int = {
                log += "init "
                return 42
            }()
        }
        let c = C()
        log += "made "
        _ = c.v + c.v
        print(log)
    ''', "made init", ["init made", "init made init", "made init init"],
      "A lazy property is computed on first access, once",
      """Creating `C` does not run the closure, so "made" is logged first. The first read of `c.v` runs it and
      stores 42, and the second read reuses the stored value."""),

    q("string-ordering", r'''
        let a = "e\u{301}"
        print("Zebra" < "apple", "a" < "B", "10" < "9", "\u{E9}" == a,
              "\u{E9}" < "f")
    ''', "true false true true false",
      ["false false true true false", "true true false true false", "true false true false true"],
      "Strings compare by Unicode scalar values, so capitals, digits and accents sort oddly",
      """Capital letters sort before lowercase ones, so "Zebra" < "apple" and "a" < "B" is false. "10" < "9"
      compares character by character. Canonically equal spellings of é are equal, but é is the scalar U+00E9,
      far above f, so `"é" < "f"` is false."""),

    q("int-parsing", r'''
        print(Int("12")! + 1, Int("12.5") as Any, Int(" 7") as Any, Int("+7")!,
              Int(-3.99), Double("1e3")!)
    ''', "13 nil nil 7 -3 1000.0",
      ["13 0 0 7 -3 1000.0", "13 nil nil 7 -4 1000.0", "13 nil 7 7 -3 1000.0"],
      "Int(String) is nil for anything that is not exactly an integer; Int(Double) truncates",
      """The string initialisers return an optional: "12.5" and " 7" are rejected (no decimals, no spaces),
      but a leading + is fine. `Int(-3.99)` cuts toward zero to -3, and `Double("1e3")` understands exponents."""),

    q("rounded-rules", r'''
        print((2.5).rounded(), (3.5).rounded(), (-2.5).rounded(),
              (2.5).rounded(.toNearestOrEven), (2.5).rounded(.down),
              Int(2.9), Int(-2.9))
    ''', "3.0 4.0 -3.0 2.0 2.0 2 -2",
      ["2.0 4.0 -2.0 2.0 2.0 2 -2", "3.0 4.0 -3.0 3.0 2.0 2 -2", "3.0 4.0 -3.0 2.0 2.0 3 -3"],
      "rounded() rounds halves away from zero; banker's rounding must be asked for",
      """The default rule is the school one: 2.5 becomes 3.0 and -2.5 becomes -3.0. `.toNearestOrEven` gives 2.0
      and `.down` gives 2.0. `Int(2.9)` does not round at all, it truncates toward zero."""),

    q("optional-in-interpolation", r'''
        let x: Int? = 5
        let y: String? = nil
        print("\(x) \(y) \(x!) \(y ?? "none")")
    ''', "Optional(5) nil 5 none",
      ["5 nil 5 none", "Optional(5) Optional(nil) 5 none", "5 5 5 none"],
      "Interpolating an optional prints its debug form, including the word Optional",
      """String interpolation does not unwrap: a value of type `Int?` shows as `Optional(5)`, and a nil as
      `nil`. The compiler warns about it. Unwrap with `!`, or give a default with `??`."""),

    q("capture-list-snapshots", r'''
        var x = 1
        let f = { [x] in x }
        let g = { x }
        x = 2
        print(f(), g())
    ''', "1 2", ["2 2", "1 1", "2 1"],
      "A capture list copies the value now; without one the closure shares the variable",
      """`[x]` stores the current value 1 inside `f`, so later changes do not reach it. `g` captures the
      variable itself and sees 2."""),

    q("deinit-when-last-reference-goes", r'''
        var log = ""
        class T {
            let n: String
            init(_ n: String) { self.n = n; log += "+\(n)" }
            deinit { log += "-\(n)" }
        }
        var a: T? = T("a")
        var b = a
        a = nil
        log += "|"
        b = nil
        print(log)
    ''', "+a|-a", ["+a-a|", "|+a-a", "+a|"],
      "An object dies when its last strong reference goes, not when one name is cleared",
      """Setting `a = nil` only drops one of two references, because `b` still holds the object, so nothing is
      destroyed yet. The deinitialiser runs when `b` is cleared, after the "|" was logged."""),

    q("repeating-shares-a-reference", r'''
        class Box { var n = 0 }
        struct V { var n = 0 }
        let boxes = Array(repeating: Box(), count: 2)
        var vs = Array(repeating: V(), count: 2)
        boxes[0].n = 1
        vs[0].n = 1
        print(boxes[1].n, vs[1].n)
    ''', "1 0", ["0 0", "1 1", "0 1"],
      "Array(repeating:) copies the value once per slot: for a class that is the same reference",
      """The expression `Box()` is evaluated once, so both slots hold the same object and a change through one
      shows in the other. Structs are copied for every slot, so changing one leaves its neighbour alone."""),

    q("character-and-ascii-values", r'''
        let a: UInt8 = 97
        print(Character(UnicodeScalar(a + 1)), "a".unicodeScalars.first!.value,
              Character("a").asciiValue!, String(repeating: "ab", count: 2))
    ''', "b 97 97 abab", ["98 97 97 abab", "b 97 a abab", "b 97 97 aabb"],
      "Characters and numbers are separate types; convert through unicode scalars or asciiValue",
      """Swift has no `'a' + 1`; you add to the byte and build a scalar from it, which gives "b". `asciiValue` is
      an optional UInt8. `String(repeating:count:)` repeats the whole string, not each letter."""),

    q("enum-raw-values", r'''
        enum D: Int { case a = 1, b, c = 10, d }
        print(D.b.rawValue, D.d.rawValue, D(rawValue: 3) as Any, D(rawValue: 10)!)
    ''', "2 11 nil c", ["2 11 nil d", "1 11 nil c", "2 10 nil c"],
      "Raw values continue from the previous case, and init(rawValue:) is failable",
      """`b` follows `a = 1`, so it is 2, and `d` follows `c = 10`, so it is 11. No case has the raw value 3,
      so `D(rawValue: 3)` is nil. `D(rawValue: 10)` finds `c`, which prints by its case name."""),

    q("for-in-iterates-a-snapshot", r'''
        var a = [1, 2, 3, 4]
        for x in a where x % 2 == 0 {
            a.remove(at: a.firstIndex(of: x)!)
        }
        print(a)
    ''', "[1, 3]", ["[1, 3, 4]", "[1, 2, 3, 4]", "[1, 2, 4]"],
      "The loop walks a copy of the array, so removing from the original does not disturb it",
      """`for x in a` makes its own copy of the value (arrays are values), so both 2 and 4 are visited even
      though the real array shrinks as the loop runs. Both are found and removed."""),

    q("defer-runs-after-the-return-value", r'''
        var log = ""
        func f() -> Int {
            var x = 1
            defer { log += "a"; x += 10 }
            defer { log += "b" }
            log += "c"
            return x
        }
        print(f(), log)
    ''', "1 cba", ["11 cba", "1 abc", "11 abc"],
      "defer blocks run last-in first-out, after the return value has been worked out",
      """`return x` copies the value 1 first; the deferred blocks then run, the later one (b) before the earlier
      one (a), so their changes to `x` come too late to matter. The log reads c, b, a."""),

    q("defer-per-iteration", r'''
        var log = ""
        for i in 1...3 {
            defer { log += "d\(i) " }
            log += "b\(i) "
        }
        print(log)
    ''', "b1 d1 b2 d2 b3 d3",
      ["b1 b2 b3 d3 d2 d1", "b1 b2 b3 d1 d2 d3", "d1 b1 d2 b2 d3 b3"],
      "defer runs when its own scope ends, which for a loop body is every iteration",
      """The loop body is a scope that ends at the end of each iteration, so each `defer` runs right after
      that round's body. It does not wait for the whole loop to finish."""),

    q("sorted-orders", r'''
        let a = ["b", "A", "a", "B"].sorted()
        let b = ["10", "9", "2"].sorted()
        let c = ["bb", "a", "ccc"].sorted { $0.count > $1.count }
        print(a, b, [3, 1, 2].sorted(by: >), c)
    ''', "[\"A\", \"B\", \"a\", \"b\"] [\"10\", \"2\", \"9\"] [3, 2, 1] [\"ccc\", \"bb\", \"a\"]",
      ["[\"a\", \"A\", \"b\", \"B\"] [\"10\", \"2\", \"9\"] [3, 2, 1] [\"ccc\", \"bb\", \"a\"]",
       "[\"A\", \"B\", \"a\", \"b\"] [\"2\", \"9\", \"10\"] [3, 2, 1] [\"ccc\", \"bb\", \"a\"]",
       "[\"A\", \"B\", \"a\", \"b\"] [\"10\", \"2\", \"9\"] [1, 2, 3] [\"a\", \"bb\", \"ccc\"]"],
      "Strings sort by code point (capitals first, \"10\" before \"2\"); the closure says who goes first",
      """The default `sorted()` on strings compares scalar values, so "A" and "B" come before "a" and "b", and
      "10" comes before "2" because "1" < "2". A closure `$0.count > $1.count` puts longer strings first."""),

    # ── Hard but legal ─────────────────────────────────────────────────────
    q("protocol-extension-static-dispatch", r'''
        protocol P { func a() -> String }
        extension P {
            func a() -> String { "P.a" }
            func b() -> String { "P.b" }
        }
        struct S: P {
            func a() -> String { "S.a" }
            func b() -> String { "S.b" }
        }
        let s = S()
        let p: P = S()
        print(s.a(), s.b(), p.a(), p.b())
    ''', "S.a S.b S.a P.b",
      ["S.a S.b S.a S.b", "S.a S.b P.a P.b", "P.a P.b P.a P.b"],
      "Only methods declared in the protocol are dispatched dynamically; extension-only ones are not",
      """`a` is a protocol requirement, so even through the `P` type the call finds S's version. `b` exists
      only in the extension, so a call through `P` is bound at compile time to the extension's body, while a
      call on the concrete `S` finds S's own method."""),

    q("subclass-is-ready-before-super-init", r'''
        var log = ""
        class A {
            init() { log += "A "; setup() }
            func setup() { log += "A.setup " }
        }
        class B: A {
            var x = 1
            override init() { super.init(); log += "B" }
            override func setup() { log += "B.setup\(x) " }
        }
        _ = B()
        print(log)
    ''', "A B.setup1 B", ["A A.setup B", "A B.setup0 B", "B.setup1 A B"],
      "Swift sets the subclass's own properties before calling super.init",
      """In a designated initialiser, `x = 1` is assigned before `super.init()` runs. So when `A.init` calls the
      overridden `setup()`, it already sees 1 (Kotlin and Java would show 0 here)."""),

    q("optional-of-optional", r'''
        let n: Int?? = .some(nil)
        let m: Int?? = nil
        print(n == nil, m == nil, n == .some(nil), n != nil)
    ''', "false true true true",
      ["true true true false", "false true false true", "true true false false"],
      "An Int?? can be a present box holding nil, which is not the same as nil",
      """`n` is `.some(nil)`: there is an outer box, and it contains a nil Int. So `n == nil` is false and
      `n != nil` is true. Only `m`, which has no outer box, equals nil."""),

    q("range-contains-surprises", r'''
        print((1...5).contains(5), (1..<5).contains(5), ("a"..."e").contains("cc"),
              (1.0...2.0).contains(1.999), (1...5).clamped(to: 3...9))
    ''', "true false true true 3...5",
      ["true false false true 3...5", "true true true true 3...5", "true false true true 3...9"],
      "Ranges work on any Comparable, so a string range tests alphabetical position",
      """`1..<5` excludes 5. A range of strings is every string between "a" and "e" in order, so "cc" is
      inside it. `clamped(to:)` trims the range to the overlap, 3...5."""),

    q("radix-parsing-and-printing", r'''
        print(Int("ff", radix: 16)!, String(255, radix: 2), Int("0x1F") as Any,
              String(-255, radix: 16), Int("-0")!)
    ''', "255 11111111 nil -ff 0",
      ["255 11111111 31 -ff 0", "255 11111111 nil ff 0", "15 11111111 nil -ff 0"],
      "Int(_:radix:) takes digits only: no 0x prefix, and the sign goes in front of the result",
      """`Int("ff", radix: 16)` is 255, but the same call on "0x1F" would fail, since the prefix is not a
      digit, and the plain `Int("0x1F")` is nil. A negative number prints with a leading minus sign, even
      in hexadecimal."""),

    q("map-versus-flat-map", r'''
        let s: String? = "12"
        print(s.map { Int($0) } as Any, s.flatMap { Int($0) } as Any)
    ''', "Optional(Optional(12)) Optional(12)",
      ["Optional(12) Optional(12)", "Optional(12) 12", "Optional(Optional(12)) 12"],
      "map wraps the closure's result again; flatMap does not, so map can nest optionals",
      """`Int($0)` already returns an optional, and `map` wraps that result in one more, giving an
      `Int??`. `flatMap` flattens the two layers into a single `Int?`."""),

    q("tuples-are-values", r'''
        let t = (a: 1, b: 2)
        let (x, y) = t
        var u = t
        u.a = 9
        print(t, u, x + y)
    ''', "(a: 1, b: 2) (a: 9, b: 2) 3",
      ["(a: 9, b: 2) (a: 9, b: 2) 3", "(a: 1, b: 2) (a: 1, b: 2) 3", "(1, 2) (9, 2) 3"],
      "A tuple is copied on assignment and keeps its labels when printed",
      """`var u = t` makes an independent copy, so changing `u.a` leaves `t` alone. Labelled tuples print with
      their labels, and the destructured `x` and `y` are plain Ints."""),

    q("lazy-pipelines-interleave", r'''
        var log = ""
        func dbl(_ x: Int) -> Int { log += "m\(x) "; return x * 2 }
        let e = [1, 2, 3].map(dbl).first(where: { $0 > 2 })!
        log += "| "
        let l = [1, 2, 3].lazy.map(dbl).first(where: { $0 > 2 })!
        print(e, l, log)
    ''', "4 4 m1 m2 m3 | m1 m2",
      ["4 4 m1 m2 | m1 m2 m3", "4 4 m1 m2 m3 | m1 m2 m3", "4 6 m1 m2 m3 | m1 m2"],
      "An eager map finishes the whole array first; a lazy one stops when the search is satisfied",
      """On a plain array `map` doubles every element before `first(where:)` looks at any of them, so m1, m2 and
      m3 are all logged. With `.lazy`, each element is mapped only when the search asks for it, and the search
      ends at 4, so 3 is never mapped."""),

    q("inout-argument-evaluated-first", r'''
        func addTwice(_ a: inout [Int], _ x: Int) {
            a.append(x)
            a.append(x)
        }
        var arr = [1]
        addTwice(&arr, arr.count)
        print(arr)
    ''', "[1, 1, 1]", ["[1, 3, 3]", "[1, 2, 2]", "[1, 1]"],
      "Arguments are evaluated before the call, so `arr.count` is read before anything is appended",
      """`arr.count` is 1 at the moment the call is set up, and that value is passed in. Inside the function
      the array grows, but `x` keeps the 1 it was given, so both appended items are 1."""),

    q("remainders-of-doubles", r'''
        print((-7.0).truncatingRemainder(dividingBy: 3),
              8.0.remainder(dividingBy: 3),
              8.0.truncatingRemainder(dividingBy: 3),
              (-7).quotientAndRemainder(dividingBy: 2))
    ''', "-1.0 -1.0 2.0 (quotient: -3, remainder: -1)",
      ["2.0 -1.0 2.0 (quotient: -4, remainder: 1)", "-1.0 2.0 2.0 (quotient: -3, remainder: -1)",
       "-1.0 -1.0 -1.0 (quotient: -3, remainder: -1)"],
      "remainder(dividingBy:) rounds the quotient to nearest; truncatingRemainder cuts it",
      """`truncatingRemainder` behaves like `%`: the sign follows the dividend, so -7 gives -1 and 8 gives 2.
      The IEEE `remainder` picks the closest multiple, 9, so 8 - 9 is -1. `quotientAndRemainder` truncates
      toward zero."""),

    q("try-question-mark-flattens", r'''
        func g() throws -> Int? { return nil }
        let a = try? g()
        let b: Int?? = .some(nil)
        print(a == nil, a as Any, b == nil)
    ''', "true nil false",
      ["false Optional(nil) false", "true Optional(nil) true", "false nil true"],
      "Since Swift 5, try? does not add an extra optional layer",
      """`g()` already returns an optional, and `try?` merges its own wrapper into it, so `a` is a plain `Int?`
      that is nil. Before Swift 5 it would have been an `Int??` holding nil, which is what `b` still is."""),

    q("optional-chaining-does-nothing-on-nil", r'''
        var a: [Int]? = nil
        a?.append(1)
        var b: [Int]? = []
        b?.append(1)
        print(a as Any, b as Any, (a ?? []).count)
    ''', "nil Optional([1]) 0",
      ["Optional([1]) Optional([1]) 1", "nil nil 0", "nil Optional([1]) 1"],
      "`a?.append(1)` quietly does nothing when a is nil; it never creates the array",
      """Optional chaining stops at the first nil, so the append on `a` is skipped and `a` stays nil. `b` holds
      an empty array, so the append works and it prints as `Optional([1])`. `a ?? []` gives an empty
      array whose count is 0."""),
)
