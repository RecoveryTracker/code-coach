"""Gotchas, Kotlin (second deck): kotlinc then the JVM; notes are in langs.py (the `kotlin` entry).

Cards use `mapOf`/`mutableMapOf` (insertion ordered), never hash containers or hash codes, and never read the
clock, random numbers or input. Doubles print like Java's `Double.toString`, which is the same everywhere.
"""

from __future__ import annotations

from .items import Item, make

q = make("kotlin")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics with a real trap ──────────────────────────────
    q("division-and-mod", r'''
        fun main() {
            println("${7 / 2} ${-7 / 2} ${-7 % 3} ${(-7).mod(3)} ${7 / 2.0}")
        }
    ''', "3 -3 -1 2 3.5",
      ["3 -4 2 2 3.5", "3.5 -3.5 -1 2 3.5", "3 -3 -1 -1 3.5"],
      "Int division truncates toward zero; % keeps the sign, mod() always lands in 0..n-1",
      """`-7 / 2` is cut toward zero to -3, and `-7 % 3` is the remainder of that, -1. `mod` is the floored
      version whose result has the sign of the divisor, so `(-7).mod(3)` is 2."""),

    q("template-simple-name", r'''
        fun main() {
            val s = "hey"
            println("$s.length ${s.length} ${'$'}s")
        }
    ''', "hey.length 3 $s", ["3 3 hey", "hey.length hey.length $s", "hey 3 $s"],
      "`$name` takes only the name; a property access needs braces",
      """In a string template `$s.length` inserts the variable `s` and then the literal text ".length". Use
      `${s.length}` for the property. A literal dollar sign is written `${'$'}`."""),

    q("range-forms", r'''
        fun main() {
            val r = 5 downTo 1 step 2
            println("${(1..5).sum()} ${(1 until 5).sum()} ${r.toList()} " +
                "${(5..1).count()}")
        }
    ''', "15 10 [5, 3, 1] 0",
      ["15 15 [5, 3, 1] 0", "15 10 [5, 4, 3, 2, 1] 0", "15 10 [5, 3, 1] 5"],
      "`..` includes the end, `until` stops before it, and `5..1` is empty",
      """`1..5` has five elements but `1 until 5` leaves out the 5, so its sum is 10. A range counts upward
      only: `5..1` is empty, and counting down needs `downTo`, with `step` applied to that."""),

    q("read-only-is-not-immutable", r'''
        fun main() {
            val list = mutableListOf(1)
            list.add(2)
            val view: List<Int> = list
            list.add(3)
            println("$list ${view.size}")
        }
    ''', "[1, 2, 3] 3", ["[1, 2, 3] 2", "[1, 2] 3", "[1] 1"],
      "A List reference only forbids changes through itself; the object may still change",
      """`val view: List<Int> = list` is the very same object seen through a read-only type, not a copy. When
      `list` grows, `view` sees it, so both show three elements. Use `toList()` to take a snapshot."""),

    q("int-wraps-silently", r'''
        fun main() {
            val x = Int.MAX_VALUE
            println("${x + 1} ${x.toLong() + 1} ${(x + 1).toLong()} ${x * 2}")
        }
    ''', "-2147483648 2147483648 -2147483648 -2",
      ["2147483648 2147483648 2147483648 4294967294", "-2147483648 2147483648 2147483648 -2",
       "-2147483648 2147483648 -2147483648 4294967294"],
      "Int arithmetic wraps around; widen to Long before the operation, not after",
      """`x + 1` is computed in 32 bits and wraps to the minimum value. Converting to Long afterwards just
      carries the already wrapped number, while `x.toLong() + 1` does the addition in 64 bits."""),

    q("null-safe-chain", r'''
        fun main() {
            val s: String? = null
            val a = s?.length
            val b = s?.length ?: -1
            println("$a $b ${s.orEmpty().length} ${(s ?: "x") + "y"}")
        }
    ''', "null -1 0 xy", ["0 -1 0 xy", "null null 0 xy", "null -1 0 y"],
      "?. gives null for a null receiver, ?: supplies a fallback, and a null prints as \"null\"",
      """`s?.length` is null (and prints as the word null) and the elvis operator turns it into -1. `orEmpty`
      swaps a null string for "", whose length is 0, and `s ?: "x"` becomes "x"."""),

    q("when-takes-the-first-match", r'''
        fun cls(n: Int) = when {
            n > 0 -> "pos"
            n > 10 -> "big"
            else -> "neg"
        }

        fun main() {
            println(cls(20) + " " + cls(0))
        }
    ''', "pos neg", ["big neg", "pos big", "big big"],
      "`when` stops at the first branch whose condition is true",
      """20 satisfies `n > 0`, which is checked first, so the later `n > 10` branch can never run. There is no
      fall-through between branches, and no `break` is needed."""),

    q("char-plus-int", r'''
        fun main() {
            val c = 'a'
            println("${c + 2} ${'d' - c} ${c.code + 1} ${"abc".first() + 1}")
        }
    ''', "c 3 98 b", ["99 3 98 b", "c 3 98 98", "c -3 98 b"],
      "Char + Int is a Char, Char - Char is an Int, and .code gives the number",
      """Kotlin keeps characters and numbers apart: `'a' + 2` moves two letters along to 'c', and the
      difference of two chars is a plain Int (3). Only `.code` turns a character into its numeric code."""),

    q("default-argument-per-call", r'''
        var n = 0

        fun next() = ++n

        fun f(a: Int = next()) = a

        fun main() {
            println("${f()} ${f()} ${f(10)} $n")
        }
    ''', "1 2 10 2", ["1 1 10 1", "1 2 10 3", "1 2 10 0"],
      "A default argument is computed again on each call that leaves it out",
      """The expression `next()` runs every time `f()` is called without an argument, giving 1 and then 2. When
      the argument is supplied, as in `f(10)`, the default is not evaluated at all, so `n` ends at 2."""),

    q("lambda-captures-var", r'''
        fun main() {
            val fs = (1..3).map { i -> { i * 10 } }
            var j = 1
            val g = { j }
            j = 5
            println("${fs.map { it() }} ${g()}")
        }
    ''', "[10, 20, 30] 5", ["[10, 20, 30] 1", "[30, 30, 30] 5", "[10, 20, 30] 0"],
      "A lambda captures the variable itself, so later assignments show through",
      """Each lambda in `fs` captures its own `i`, a new value per element. The lambda `g` captures the
      variable `j`, not the 1 it held, so it returns 5 after the assignment."""),

    q("remove-versus-remove-at", r'''
        fun main() {
            val l = mutableListOf(5, 6, 7)
            l.remove(1)
            l.removeAt(1)
            println("$l ${l.remove(9)}")
        }
    ''', "[5, 7] false", ["[5] false", "[6] false", "[5, 7] true"],
      "remove(x) deletes a value, removeAt(i) deletes an index",
      """`l.remove(1)` searches for the element 1 and finds none, so nothing changes. `removeAt(1)` removes the
      element at index 1, the 6. `remove(9)` finds nothing and returns false."""),

    q("string-immutable-builder-shared", r'''
        fun main() {
            var s = "a"
            val t = s
            s += "b"
            val sb = StringBuilder("a")
            val sb2 = sb
            sb.append("b")
            println("$s $t $sb2")
        }
    ''', "ab a ab", ["ab ab ab", "a a a", "ab a a"],
      "A String is never changed in place; a StringBuilder is one shared object",
      """`s += "b"` builds a new String and re-points `s`, leaving `t` as "a". `sb2` is another name for the
      same StringBuilder, so appending through `sb` shows up in both."""),

    # ── Medium ─────────────────────────────────────────────────────────────
    q("scope-function-results", r'''
        fun main() {
            val a = "ab".let { it + "c" }
            val b = "ab".also { it + "c" }
            val c = StringBuilder("ab").apply { append("c") }
            val d = "ab".run { length }
            println("$a $b $c $d")
        }
    ''', "abc ab abc 2", ["abc abc abc 2", "ab ab ab 2", "abc ab ab 2"],
      "let and run return the lambda's result; also and apply return the receiver",
      """`let` hands back whatever the lambda produces ("abc"), but `also` ignores the lambda's value and returns
      the original "ab". `apply` returns the StringBuilder it modified, and `run { length }` returns the
      lambda's result, 2."""),

    q("data-class-copy-is-shallow", r'''
        data class P(val x: Int, val l: MutableList<Int>)

        fun main() {
            val a = P(1, mutableListOf(1))
            val b = a.copy()
            b.l.add(2)
            val c = a.copy(x = 5)
            println("${a == b} ${a.l} ${a === b} $c")
        }
    ''', "true [1, 2] false P(x=5, l=[1, 2])",
      ["false [1] false P(x=5, l=[1])", "true [1] false P(x=5, l=[1])", "true [1, 2] true P(x=5, l=[1, 2])"],
      "copy() makes a new object but shares the objects inside it",
      """`b` is a different P, but its `l` is the same list as `a.l`, so adding through `b` changes both and they
      stay equal (data classes compare their properties). `copy(x = 5)` shares the list too."""),

    q("list-eager-sequence-lazy", r'''
        fun main() {
            val log = mutableListOf<String>()
            val r = (1..4).map { log.add("m$it"); it * 2 }.first { it > 2 }
            val s = (1..4).asSequence()
                .map { log.add("s$it"); it * 2 }
                .first { it > 2 }
            println("$r $s ${log.joinToString(" ")}")
        }
    ''', "4 4 m1 m2 m3 m4 s1 s2",
      ["4 4 m1 s1 m2 s2 m3 m4", "4 4 m1 m2 s1 s2", "4 4 m1 m2 m3 m4 s1 s2 s3 s4"],
      "A list maps every element first; a sequence stops as soon as `first` is satisfied",
      """On a list, `map` finishes all four elements before `first` looks at the results. The sequence is pulled
      one element at a time and `first { it > 2 }` is satisfied by the second, so only s1 and s2 are logged."""),

    q("swap-with-also", r'''
        fun main() {
            var a = 1
            var b = 2
            a = b.also { b = a }
            val (p, q) = Pair(a, b)
            println("$a $b ${p + q}")
        }
    ''', "2 1 3", ["2 2 4", "1 2 3", "1 1 2"],
      "`x.also { ... }` returns x as it was before the block changed anything",
      """`b.also { b = a }` first reads b (2) as the result, then the block sets b to 1. Assigning the result to
      `a` completes the swap. The destructuring `val (p, q)` then just unpacks the pair of final values."""),

    q("map-keys-is-a-live-view", r'''
        fun main() {
            val m = mutableMapOf("a" to 1)
            val keys = m.keys
            m["b"] = 2
            val snap = m.keys.toList()
            m["c"] = 3
            println("${keys.size} ${snap.size} $keys")
        }
    ''', "3 2 [a, b, c]", ["1 2 [a]", "2 2 [a, b]", "3 3 [a, b, c]"],
      "`keys` is a window onto the map; `toList()` is a copy",
      """`m.keys` does not copy anything, so `keys` reflects every later insertion and ends up with three
      entries. `snap` was taken after only two keys existed and never changes."""),

    q("sort-returns-unit", r'''
        fun main() {
            val a = mutableListOf(3, 1, 2)
            val r = a.sort()
            val b = listOf(3, 1, 2).sorted()
            val c = listOf(3, 1, 2)
            println("$r $a $b $c")
        }
    ''', "kotlin.Unit [1, 2, 3] [1, 2, 3] [3, 1, 2]",
      ["[1, 2, 3] [1, 2, 3] [1, 2, 3] [3, 1, 2]", "kotlin.Unit [3, 1, 2] [1, 2, 3] [3, 1, 2]",
       "null [1, 2, 3] [1, 2, 3] [3, 1, 2]"],
      "sort() orders in place and returns Unit; sorted() returns a new list",
      """`MutableList.sort()` rearranges the list itself and returns nothing useful, so the template shows
      `kotlin.Unit`. `sorted()` leaves its receiver alone and returns a new ordered list."""),

    q("equality-of-collections-and-arrays", r'''
        fun main() {
            val a = arrayOf(1, 2)
            val b = arrayOf(1, 2)
            println("${listOf(1, 2) == listOf(1, 2)} ${a == b} " +
                "${a.contentEquals(b)} ${setOf(1, 2) == setOf(2, 1)} " +
                "${listOf(1, 2) == listOf(2, 1)}")
        }
    ''', "true false true true false",
      ["true true true true false", "true false true false false", "false false true true false"],
      "Lists and sets compare by contents, arrays by identity",
      """Collections implement `equals` over their elements: lists must match in order, sets ignore order.
      Arrays use the JVM's default identity `equals`, so two arrays with the same items are different unless
      you call `contentEquals`."""),

    q("group-by-and-to-map", r'''
        fun main() {
            val g = listOf(1, 2, 3, 4, 5).groupBy { it % 2 }
            val m = listOf("a" to 1, "b" to 2, "a" to 3).toMap()
            println("$g $m")
        }
    ''', "{1=[1, 3, 5], 0=[2, 4]} {a=3, b=2}",
      ["{0=[2, 4], 1=[1, 3, 5]} {a=3, b=2}", "{1=[1, 3, 5], 0=[2, 4]} {a=1, b=2}",
       "{1=[1, 3, 5], 0=[2, 4]} {b=2, a=3}"],
      "groupBy keeps first-seen key order; toMap lets a later duplicate replace the value, not the position",
      """The first element is odd, so key 1 comes first in the result. In `toMap` the second "a" overwrites the
      value of the first one, but the key stays in its original place, giving a=3 before b=2."""),

    q("double-to-string", r'''
        fun main() {
            val xs = listOf(1.0, 1e3, 1e7, 1.0e-4, 0.1 + 0.2, 100.0 / 3, 1f / 3)
            println(xs.joinToString(" "))
        }
    ''', "1.0 1000.0 1.0E7 1.0E-4 0.30000000000000004 33.333333333333336 0.33333334",
      ["1 1000 10000000 0.0001 0.3 33.333333333333336 0.33333334",
       "1.0 1000.0 10000000.0 0.0001 0.30000000000000004 33.333333333333336 0.3333333333333333",
       "1.0 1000.0 1.0E7 1.0E-4 0.3 33.33333333333333 0.33333334"],
      "Doubles always show a decimal point, switch to E notation at 10^7 and 10^-3, and Float is shorter",
      """A Double always prints with at least one decimal, and values of 10^7 or more (or below 0.001) use E
      notation. It prints enough digits to be read back exactly, which exposes 0.30000000000000004. A Float
      prints fewer digits."""),

    q("spread-operator", r'''
        fun main() {
            val arr = arrayOf(1, 2)
            val one = listOf(arr).size
            println("$one ${listOf(*arr).size} ${listOf(*arr, 3).size}")
        }
    ''', "1 2 3", ["2 2 3", "1 1 2", "2 2 2"],
      "Passing an array to vararg gives one element; `*` spreads it into many",
      """`listOf(arr)` receives the array as a single argument, so the list has one element. The spread
      operator `*arr` unpacks it into the individual values, and extra arguments can follow."""),

    q("split-keeps-empty-pieces", r'''
        fun main() {
            val a = "a,,b".split(",")
            val n1 = "".split(",").size
            val n2 = "a b  c".split(" ").size
            val n3 = "a b  c".split(Regex("\\s+")).size
            println("$a $n1 $n2 $n3")
        }
    ''', "[a, , b] 1 4 3", ["[a, b] 0 3 3", "[a, , b] 0 4 3", "[a, , b] 1 3 3"],
      "split never drops empty pieces; an empty string still gives one piece",
      """Two commas in a row leave an empty string between them, and splitting "" gives a single empty string.
      Two spaces in a row also make an empty piece, which is why the regex `\\s+` is used to treat a whole run
      as one separator."""),

    q("get-or-put-versus-get-or-default", r'''
        fun main() {
            val m = mutableMapOf("a" to 1)
            val x = m.getOrPut("a") { 99 }
            val y = m.getOrPut("c") { 99 }
            val z = m.getOrDefault("z", 7)
            println("$x $y $m $z ${m.size}")
        }
    ''', "1 99 {a=1, c=99} 7 2",
      ["99 99 {a=99, c=99} 7 2", "1 99 {a=1, c=99, z=7} 7 3", "1 99 {a=1, c=99} 7 3"],
      "getOrPut stores a missing value; getOrDefault only reports one",
      """`getOrPut("a")` finds an existing value and returns it without calling the lambda. For the missing key
      "c" it runs the lambda and saves the result in the map. `getOrDefault` never modifies the map."""),

    q("safe-cast-and-parse", r'''
        fun main() {
            val x: Any = "5"
            val n = x as? Int
            val s = (x as? String)?.toInt()?.plus(1)
            println("$n $s ${x is String} ${x.toString() + 1}")
        }
    ''', "null 6 true 51", ["0 6 true 6", "null 6 true 6", "null 51 true 51"],
      "`as?` gives null instead of throwing; `+ 1` on a String appends text",
      """The value is really a String, so `as? Int` is null. The second cast works, `toInt()` gives 5 and
      `plus(1)` adds numerically to 6, but `x.toString() + 1` is string concatenation, "51"."""),

    q("take-and-drop-never-throw", r'''
        fun main() {
            val s = "hello"
            val t = s.take(10)
            println("${s.substring(1, 3)} $t [${s.drop(10)}] ${s.takeLast(2)} " +
                s.substring(2))
        }
    ''', "el hello [] lo llo", ["ell hello [] lo llo", "el hello [hello] lo llo", "el hello [] lo lo"],
      "substring(from, to) excludes `to`; take and drop clamp instead of failing",
      """`substring(1, 3)` stops before index 3, giving "el". `take(10)` simply returns the whole string, and
      `drop(10)` removes more characters than exist, so it returns "". Asking `substring` for an index out of
      range would throw."""),

    q("zip-chunked-windowed", r'''
        fun main() {
            val z = listOf(1, 2, 3).zip(listOf("a", "b"))
            println("$z ${(1..5).chunked(2)} ${(1..4).windowed(2)}")
        }
    ''', "[(1, a), (2, b)] [[1, 2], [3, 4], [5]] [[1, 2], [2, 3], [3, 4]]",
      ["[(1, a), (2, b), (3, null)] [[1, 2], [3, 4], [5]] [[1, 2], [2, 3], [3, 4]]",
       "[(1, a), (2, b)] [[1, 2], [3, 4]] [[1, 2], [2, 3], [3, 4]]",
       "[(1, a), (2, b)] [[1, 2], [3, 4], [5]] [[1, 2], [3, 4]]"],
      "zip stops at the shorter list, chunked keeps a short last chunk, windowed slides by one",
      """`zip` pairs elements only while both lists have one, so the 3 is dropped. `chunked(2)` splits into
      consecutive pieces and keeps the leftover [5]. `windowed(2)` produces overlapping pairs."""),

    q("enum-basics", r'''
        enum class C { R, G, B }

        fun main() {
            val names = C.entries.map { it.name.lowercase() }
            println("${C.B.ordinal} ${C.valueOf("G")} $names ${C.R < C.B}")
        }
    ''', "2 G [r, g, b] true", ["3 G [r, g, b] true", "2 1 [r, g, b] true", "2 G [R, G, B] false"],
      "An enum's ordinal starts at 0, valueOf takes the name, and entries compare by ordinal",
      """`B` is the third constant so its ordinal is 2. `valueOf("G")` returns the constant itself, which prints
      as its name, and enums are `Comparable` by declaration order, so `R < B`."""),

    q("sum-overflows-int", r'''
        fun main() {
            val l = listOf(Int.MAX_VALUE, 1)
            println("${l.sum()} ${l.sumOf { it.toLong() }} ${l.average()}")
        }
    ''', "-2147483648 2147483648 1.073741824E9",
      ["2147483648 2147483648 1.073741824E9", "-2147483648 -2147483648 -1.073741824E9",
       "-2147483648 2147483648 1073741824"],
      "sum() of Ints is an Int and wraps; average() always works in Double",
      """`sum()` adds in 32 bits, so Int.MAX_VALUE + 1 wraps to the minimum. `sumOf { it.toLong() }` adds in 64
      bits. `average()` returns a Double, here 1073741824.0, which prints in E notation."""),

    # ── Hard but legal ─────────────────────────────────────────────────────
    q("object-and-companion-init-order", r'''
        object O {
            init { print("O ") }
            val v = 1
        }
        class A {
            companion object { init { print("C ") } }
            init { print("I ") }
            constructor() { print("K ") }
        }
        fun main() {
            print("main ")
            A()
            A()
            println(O.v)
        }
    ''', "main C I K I K O 1",
      ["C O main I K I K 1", "main C I K C I K O 1", "main I K I K C O 1"],
      "Companions start with their class, objects on first use; init blocks run before the constructor",
      """Nothing starts before `main`. The companion's init runs once, when class A is first used, then each
      `A()` runs the `init` block before the constructor body. The object `O` starts only when `O.v` is read."""),

    q("open-property-in-base-init", r'''
        val log = mutableListOf<Int>()

        open class B {
            open val x = 1
            init { log.add(x) }
        }

        class D : B() {
            override val x = 2
        }

        fun main() {
            val d = D()
            log.add(d.x)
            println(log)
        }
    ''', "[0, 2]", ["[1, 2]", "[2, 2]", "[0, 1]"],
      "A base constructor that reads an overridden property sees it before the subclass set it",
      """`B`'s init block runs first, and `x` is virtual, so it reads D's property, whose backing field has not
      been assigned yet and still holds the default 0. Only after `B()` finishes does D's `x = 2` run."""),

    q("fold-and-reduce-direction", r'''
        fun main() {
            val l = listOf(10, 2, 3)
            val a = l.fold("") { acc, x -> "$x$acc" }
            val b = l.foldRight("") { x, acc -> "$x$acc" }
            val c = l.reduce { x, y -> x - y }
            val d = l.reduceRight { x, y -> x - y }
            println("$a $b $c $d")
        }
    ''', "3210 1023 5 11", ["1023 3210 5 11", "3210 1023 5 5", "3210 1023 -5 11"],
      "fold goes left to right, foldRight and reduceRight go from the end, and nest to the right",
      """`fold` prepends each element in turn, so the text builds up backwards: 3210. `foldRight` consumes the
      list from the end and gives 1023. `reduce` computes (10 - 2) - 3 = 5, but `reduceRight` computes
      10 - (2 - 3) = 11."""),

    q("int-and-long-are-never-equal-as-any", r'''
        fun main() {
            val a: Any = 1
            val b: Any = 1L
            println("${a == b} ${a == 1} ${(a as Int).toLong() == b} ${1L == 1L}")
        }
    ''', "false true true true",
      ["true true true true", "false false true true", "false true false true"],
      "Through Any, == is equals(), and an Int never equals a Long",
      """`a` and `b` are a boxed Int and a boxed Long; `Integer.equals(Long)` is always false, even for the same
      number. After converting `a` to a Long, the two boxed Longs are equal."""),

    q("nan-and-negative-zero-equality", r'''
        fun main() {
            val n = Double.NaN
            val anyN: Any = n
            val z: Any = -0.0
            println("${n == n} ${anyN == anyN} ${-0.0 == 0.0} ${z == (0.0 as Any)}")
        }
    ''', "false true true false",
      ["false false true true", "true true true false", "false true false false"],
      "On a Double, == follows IEEE; on an Any, == uses equals(), which does not",
      """With static type `Double`, NaN is not equal to itself and -0.0 equals 0.0. Once the values are typed
      `Any`, `==` calls `Double.equals`, which treats NaN as equal to itself and -0.0 and 0.0 as different."""),

    q("lazy-delegate-runs-once", r'''
        fun main() {
            var calls = 0
            val v by lazy { calls++; 42 }
            println("$calls ${v + v} $calls")
        }
    ''', "0 84 1", ["1 84 1", "0 84 2", "0 84 0"],
      "A lazy value is computed on the first read only, and templates run left to right",
      """Declaring `v by lazy` runs nothing, so the first `$calls` is still 0. The first use of `v` runs the
      initialiser, which bumps `calls`, and the second use reuses the saved 42, so the last `$calls` is 1."""),

    q("shifts-are-modulo-the-width", r'''
        fun main() {
            val a = 1 shl 31
            val b = 1L shl 31
            println("$a $b ${-8 shr 1} ${-8 ushr 28} ${1 shl 33}")
        }
    ''', "-2147483648 2147483648 -4 15 2",
      ["2147483648 2147483648 -4 15 2", "-2147483648 2147483648 -4 15 8589934592",
       "-2147483648 2147483648 -4 -1 2"],
      "Int shifts use only the low 5 bits of the count; shr keeps the sign, ushr does not",
      """`1 shl 31` lands on the sign bit of an Int, so it is negative. A shift count of 33 is taken modulo 32,
      so `1 shl 33` is `1 shl 1`. `shr` copies the sign bit, `ushr` fills with zeros: -8 ushr 28 is 15."""),

    q("list-of-the-same-list", r'''
        fun main() {
            val row = mutableListOf(0, 0)
            val shared = List(2) { row }
            val sep = List(2) { mutableListOf(0, 0) }
            shared[0][0] = 1
            sep[0][0] = 1
            println("$shared $sep")
        }
    ''', "[[1, 0], [1, 0]] [[1, 0], [0, 0]]",
      ["[[1, 0], [0, 0]] [[1, 0], [0, 0]]", "[[1, 0], [1, 0]] [[1, 0], [1, 0]]",
       "[[1, 0], [0, 0]] [[1, 0], [1, 0]]"],
      "The initialiser returns the same list twice, so the two rows are one object",
      """`List(2) { row }` calls the lambda twice, but it returns the same `row` each time, so both slots refer
      to one list. In `sep` the lambda creates a new list on every call, so the rows are independent."""),

    q("plus-picks-element-or-collection", r'''
        fun main() {
            val a = listOf(1, 2)
            println("${a + 3} ${a + listOf(3)} ${listOf(a) + listOf(3)} ${a - 1}")
        }
    ''', "[1, 2, 3] [1, 2, 3] [[1, 2], 3] [2]",
      ["[1, 2, 3] [1, 2, 3] [[1, 2], [3]] [2]", "[1, 2, 3] [1, 2, [3]] [[1, 2], 3] [2]",
       "[1, 2, 3] [1, 2, 3] [1, 2, 3] [2]"],
      "`list + collection` appends the items whenever the types allow it, even into a mixed list",
      """A List is covariant, so `listOf(a)` can be seen as a `List<Any>`, and then `+ listOf(3)` type-checks as
      "add all these items", giving [[1, 2], 3]. It does not wrap the second list as a single element.
      `a - 1` removes the value 1."""),

    q("to-int-or-null-edge-cases", r'''
        fun main() {
            val a = "12".toInt() + 1
            val b = "x".toIntOrNull()
            val c = "7".toIntOrNull()?.plus(1)
            println("$a $b $c ${" 7".toIntOrNull()} ${"+7".toIntOrNull()}")
        }
    ''', "13 null 8 null 7", ["13 0 8 7 7", "13 null 8 7 7", "13 null 8 null null"],
      "toIntOrNull accepts a leading + or -, but not spaces",
      """`toIntOrNull` returns null on anything that is not a clean integer, and it does not trim whitespace, so
      " 7" fails. A leading `+` is accepted, so "+7" is 7."""),

    q("and-or-versus-short-circuit", r'''
        fun main() {
            val log = StringBuilder()
            fun t(s: String, v: Boolean): Boolean { log.append(s); return v }
            val a = t("1", false) && t("2", true)
            val b = t("3", true) or t("4", true)
            val c = t("5", true) || t("6", false)
            println("$a $b $c $log")
        }
    ''', "false true true 1345",
      ["false true true 135", "false true true 123456", "false true true 1235"],
      "`and` / `or` always evaluate both sides; `&&` / `||` stop early",
      """`&&` stops after the first false, so "2" never runs, and `||` stops after the first true, so "6" never
      runs. The infix functions `and` and `or` are ordinary calls that evaluate both operands, so "3" and "4"
      are both logged."""),
)
