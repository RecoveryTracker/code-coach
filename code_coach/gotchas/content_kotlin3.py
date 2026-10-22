"""Gotchas, Kotlin (third deck): kotlinc then the JVM; notes are in langs.py (the `kotlin` entry).

Same rules as content_kotlin2.py: `mapOf`/`mutableMapOf` (insertion ordered) and never hash containers or hash
codes, no clock, no random numbers, no input, no printing of an object whose `toString` is its identity. Doubles
print like Java's `Double.toString`. This deck is the standard-library side (string and collection functions,
rounding and radix), scope functions and delegation, and the evaluation-order and operator-resolution traps.
"""

from __future__ import annotations

from .items import Item, make

q = make("kotlin")

ITEMS: tuple[Item, ...] = (
    # ── Batch 1: strings, ranges, scope functions, delegation ──────────────
    q("substring-before-after-missing-delimiter", r'''
        fun main() {
            val s = "a=b=c"
            println("${s.substringBefore("=")}|${s.substringAfter("=")}|" +
                "${s.substringBeforeLast("=")}|${s.substringAfterLast("=")}|" +
                "${"abc".substringAfter("=")}|" +
                "${"abc".substringBefore("=", "none")}")
        }
    ''', "a|b=c|a=b|c|abc|none",
    ["a|b|a|c|abc|none", "a|b=c|a=b|c||none", "a|b=c|a=b|c|abc|abc"],
      "These cut at the first or last delimiter; a missing one gives the whole string unless told otherwise",
      """`substringBefore` and `substringAfter` use the first `=`, the `Last` versions the last one. When
      the delimiter is absent, the default result is the original string, not an empty one; a second
      argument replaces that default."""),

    q("char-code-versus-digit-value", r'''
        fun main() {
            println("${'5'.code} ${'5'.digitToInt()} ${'5' - '0'} ${'a' - 'A'} " +
                "${'a'.uppercaseChar()}")
        }
    ''', "53 5 5 32 A", ["5 5 5 32 A", "53 53 5 32 A", "53 5 53 32 A"],
      "A digit character's code is not its value; Char minus Char gives an Int",
      """`'5'.code` is the character number, 53. `digitToInt()` and `'5' - '0'` give the value 5, and
      the difference of two chars is an Int: `'a' - 'A'` is 97 - 65 = 32."""),

    q("progression-step-need-not-reach-the-end", r'''
        fun main() {
            println("${(1..10 step 4).toList()} ${(10 downTo 1 step 4).toList()} " +
                "${(1 until 10 step 3).toList()} ${(1..10 step 3).last}")
        }
    ''', "[1, 5, 9] [10, 6, 2] [1, 4, 7] 10",
    ["[1, 5, 9] [10, 6, 2] [1, 4, 7, 10] 10", "[1, 5, 9] [10, 6, 2] [1, 4, 7] 9",
     "[1, 5] [10, 6] [1, 4] 10"],
      "A stepped range goes up in jumps from the start and stops at the last one that fits",
      """`1..10 step 4` gives 1, 5, 9 (13 is too far). `until` leaves out the 10, so 1, 4, 7. With
      `1..10 step 3` the values are 1, 4, 7, 10, and 10 happens to fit, so `last` is 10."""),

    q("let-and-elvis-when-the-block-returns-null", r'''
        fun main() {
            val a: Int? = 5
            val r1 = a?.let { if (it > 9) it else null } ?: -1
            val r2 = a?.let { it * 2 } ?: -1
            val b: Int? = null
            val r3 = b?.let { it * 2 } ?: -1
            println("$r1 $r2 $r3")
        }
    ''', "-1 10 -1", ["5 10 -1", "null 10 -1", "-1 10 null"],
      "`?:` cannot tell 'a was null' from 'the let block gave null'",
      """For r1, `a` is not null, so `let` runs, but its block returns null, and then the elvis
      operator supplies -1 anyway. r2 gets 10, and r3 is -1 because `b` really is null."""),

    q("takeif-returns-the-value-or-null", r'''
        fun main() {
            val a = 5.takeIf { it > 3 }
            val b = 5.takeUnless { it > 3 }
            val c = "".takeIf { it.isNotEmpty() } ?: "empty"
            println("$a $b $c ${"hi".takeIf { it.length == 2 }?.uppercase()}")
        }
    ''', "5 null empty HI", ["null 5 empty HI", "5 null empty hi", "5 null HI"],
      "takeIf keeps the value when the test is true; takeUnless keeps it when it is false",
      """5 passes `it > 3`, so `takeIf` returns it, while `takeUnless` returns null. The empty string
      fails its test, so the elvis gives "empty", and "hi" passes and is then upper-cased."""),

    q("delegation-forwards-to-the-delegate-itself", r'''
        interface A {
            fun a(): String
            fun b(): String = "b:" + a()
        }
        class Base : A { override fun a() = "base" }
        class D(x: A) : A by x { override fun a() = "derived" }

        fun main() {
            val d = D(Base())
            println(d.a() + " " + d.b())
        }
    ''', "derived b:base", ["derived b:derived", "base b:base", "derived derived"],
      "With `by`, the delegate's methods call each other, not the overrides in the wrapper",
      """`d.a()` is the wrapper's own override. `d.b()` is forwarded to the `Base` object, and inside it
      `a()` means `Base.a()`, because Base knows nothing about D. Delegation is not inheritance."""),

    q("extension-is-picked-by-the-declared-type", r'''
        open class P
        class C : P()
        class M { fun f() = "member" }

        fun P.who() = "P"
        fun C.who() = "C"
        fun M.f() = "ext"

        fun main() {
            val p: P = C()
            println("${p.who()} ${C().who()} ${M().f()}")
        }
    ''', "P C member", ["C C member", "P C ext", "C C ext"],
      "Extensions are chosen by the declared type, and a member always beats an extension",
      """Extensions are resolved at compile time, so `p` (declared P) uses `P.who` even though it holds a
      C. `C().who()` has the type C. A function with the same signature as a member is never called."""),

    q("named-arguments-run-in-call-order", r'''
        val log = StringBuilder()
        fun t(s: String): String { log.append(s); return s }
        fun f(a: String, b: String) = a + b

        fun main() {
            val r = f(b = t("B"), a = t("A"))
            println("$r $log")
        }
    ''', "AB BA", ["AB AB", "BA BA", "BA AB"],
      "Arguments are evaluated in the order they are written, whatever their parameter order",
      """The function sees a = "A" and b = "B", so the result is "AB". But the call site writes `b = ...`
      first, so `t("B")` runs first, and the log reads "BA"."""),

    q("associate-last-wins-but-keeps-first-position", r'''
        fun main() {
            val w = listOf("a1", "b1", "a2")
            println("${w.associate { it[0] to it }} " +
                "${w.associateBy { it.last() }} ${w.groupBy { it[0] }}")
        }
    ''', "{a=a2, b=b1} {1=b1, 2=a2} {a=[a1, a2], b=[b1]}",
    ["{a=a1, b=b1} {1=a1, 2=a2} {a=[a1, a2], b=[b1]}",
     "{b=b1, a=a2} {1=b1, 2=a2} {a=[a1, a2], b=[b1]}",
     "{a=[a1, a2], b=[b1]} {1=[a1, b1], 2=[a2]} {a=[a1, a2], b=[b1]}"],
      "associate keeps one value per key (the last), in the order the keys first appeared",
      """A repeated key replaces the value but not the position, so `a` stays first with "a2". In
      `associateBy` the key is the last digit, so "b1" replaces "a1" under 1. Only `groupBy` keeps everything."""),

    q("sorted-by-descending-keeps-ties-in-order", r'''
        fun main() {
            val w = listOf("bb", "a", "cc", "d")
            println("${w.sortedBy { it.length }} " +
                "${w.sortedByDescending { it.length }} " +
                "${w.sortedBy { it.length }.reversed()}")
        }
    ''', "[a, d, bb, cc] [bb, cc, a, d] [cc, bb, d, a]",
    ["[a, d, bb, cc] [cc, bb, d, a] [cc, bb, d, a]", "[d, a, cc, bb] [bb, cc, a, d] [cc, bb, d, a]",
     "[a, d, bb, cc] [bb, cc, a, d] [bb, cc, a, d]"],
      "The sort is stable in both directions: descending is not the same as ascending reversed",
      """Ties stay in their original order. Descending puts the long words first, still in the order
      bb, cc and a, d. Reversing the ascending list flips the ties too: cc, bb, d, a."""),

    # ── Batch 2: collections, strings, numbers ─────────────────────────────
    q("distinct-by-keeps-the-first-of-each-key", r'''
        fun main() {
            println("${listOf(3, 1, 3, 2, 1).distinct()} " +
                "${listOf(3, 1, 4, 2, 5).distinctBy { it % 2 }} " +
                "${listOf("a", "B", "b", "A").distinctBy { it.lowercase() }}")
        }
    ''', "[3, 1, 2] [3, 4] [a, B]",
    ["[1, 2, 3] [3, 4] [a, B]", "[3, 1, 2] [5, 2] [a, B]", "[3, 1, 2] [3, 4] [A, b]"],
      "distinct and distinctBy keep the first item of each kind, in the original order",
      """`distinct` does not sort: it drops later repeats, giving 3, 1, 2. `distinctBy { it % 2 }` keeps
      the first odd (3) and the first even (4). The case-insensitive key keeps "a" and "B"."""),

    q("flat-map-flattens-one-level", r'''
        fun main() {
            val r1 = listOf("a,b", "c").flatMap { it.split(",") }
            val r2 = listOf("a,b", "c").map { it.split(",") }
            val r3 = listOf(listOf(1, listOf(2)), listOf(3)).flatten()
            println("$r1 $r2 $r3")
        }
    ''', "[a, b, c] [[a, b], [c]] [1, [2], 3]",
    ["[a, b, c] [a, b, c] [1, 2, 3]", "[[a, b], [c]] [[a, b], [c]] [1, [2], 3]",
     "[a, b, c] [[a, b], [c]] [1, 2, 3]"],
      "flatMap and flatten remove exactly one level of nesting",
      """`map` keeps one list per string, while `flatMap` joins them into a single list. `flatten`
      also goes only one level deep, so the inner `listOf(2)` stays a list inside the result."""),

    q("take-while-stops-at-the-first-failure", r'''
        fun main() {
            val v = listOf(1, 2, 5, 1, 2)
            println("${v.takeWhile { it < 3 }} ${v.filter { it < 3 }} " +
                "${v.dropWhile { it < 3 }} ${v.takeLastWhile { it < 3 }}")
        }
    ''', "[1, 2] [1, 2, 1, 2] [5, 1, 2] [1, 2]",
    ["[1, 2, 1, 2] [1, 2, 1, 2] [5] [1, 2]", "[1, 2] [1, 2, 1, 2] [5] [1, 2]",
     "[1, 2] [1, 2] [5, 1, 2] [1, 2]"],
      "takeWhile and dropWhile only look at the unbroken run at the start (or end)",
      """`takeWhile` stops at the 5 and never sees the later 1, 2, while `filter` checks every item.
      `dropWhile` removes just that opening run and keeps everything from the 5 on."""),

    q("sublist-is-a-live-view", r'''
        fun main() {
            val l = mutableListOf(1, 2, 3, 4)
            val s = l.subList(1, 3)
            s[0] = 99
            val a = l.toString()
            s.clear()
            println("$a $l ${s.size}")
        }
    ''', "[1, 99, 3, 4] [1, 4] 0",
    ["[1, 2, 3, 4] [1, 4] 0", "[1, 99, 3, 4] [1, 99, 3, 4] 0", "[1, 99, 3, 4] [1, 2, 3, 4] 2"],
      "subList is a window onto the original list, not a copy",
      """Writing through the view changes the list underneath it (99), and clearing the view removes
      those two elements from the list itself, leaving [1, 4]."""),

    q("to-chains-nest-the-pairs", r'''
        fun main() {
            val a = 1 to 2 to 3
            val (x, y) = a
            println("$a $x $y ${a.first.second} ${Triple(1, 2, 3)}")
        }
    ''', "((1, 2), 3) (1, 2) 3 2 (1, 2, 3)",
    ["(1, 2, 3) 1 2 2 (1, 2, 3)", "((1, 2), 3) 1 2 2 (1, 2, 3)", "(1, 2, 3) (1, 2) 3 2 (1, 2, 3)"],
      "`to` makes a Pair, so `1 to 2 to 3` is a pair whose first part is a pair",
      """`to` is left-associative: `(1 to 2) to 3`. Destructuring it gives x = (1, 2) and y = 3.
      For three flat values you need a Triple."""),

    q("trim-indent-and-trim-margin", r'''
        fun main() {
            val t = """
                a
                  b
                c
            """.trimIndent()
            val m = """
                |x
                  |y
            """.trimMargin()
            println(t.replace("\n", "/") + " " + m.replace("\n", "/"))
        }
    ''', "a/  b/c x/y", ["a/b/c x/y", "/a/  b/c/ x/y", "a/  b/c |x/|y"],
      "trimIndent removes the common indent and the blank first and last lines; trimMargin cuts at |",
      """The shallowest line sets how much indent to remove, so "b" keeps its two extra spaces. The
      first and last blank lines vanish. `trimMargin` drops everything up to the `|` on each line."""),

    q("split-with-a-limit-or-several-delimiters", r'''
        fun main() {
            println("${"a-b-c-d".split("-", limit = 2)} " +
                "${"a-b_c".split("-", "_")} " +
                "${"a1b22c".split(Regex("[0-9]+"))} ${"x".split("-")}")
        }
    ''', "[a, b-c-d] [a, b, c] [a, b, c] [x]",
    ["[a, b] [a, b, c] [a, b, c] [x]", "[a, b-c-d] [a, b_c] [a, b, c] [x]",
     "[a, b-c-d] [a, b, c] [a, b, c] []"],
      "`limit` caps the number of pieces, and the last piece keeps the rest of the string",
      """With `limit = 2` the string is cut once, so the second piece is everything after the first
      dash. Several delimiters split at any of them, a Regex splits at each match, and a string without
      the delimiter comes back as a single piece."""),

    q("radix-conversions", r'''
        fun main() {
            println("${255.toString(16)} ${"ff".toInt(16)} ${"101".toInt(2)} " +
                "${(-255).toString(16)} ${255.toString(2).length} " +
                "${"FF".toInt(16)}")
        }
    ''', "ff 255 5 -ff 8 255",
    ["FF 255 5 -ff 8 255", "ff 255 5 -ff 8 0", "ff 15 5 -ff 8 255"],
      "toString(radix) writes lower-case digits and a minus sign; toInt(radix) reads either case",
      """255 is `ff` in hex and 11111111 in binary (8 digits). A negative number keeps its minus sign
      rather than showing two's complement. `toInt(16)` accepts both `ff` and `FF`."""),

    q("float-hides-what-double-shows", r'''
        fun main() {
            println("${0.1f + 0.2f} ${0.1 + 0.2} ${0.1f.toDouble()}")
        }
    ''', "0.3 0.30000000000000004 0.10000000149011612",
    ["0.30000001 0.30000000000000004 0.1", "0.3 0.3 0.1", "0.3 0.30000000000000004 0.1"],
      "A Float has fewer digits, so its sum looks clean; widening it exposes the stored value",
      """Float arithmetic rounds to about 7 digits, and `0.1f + 0.2f` lands exactly on the float nearest
      0.3. The double sum is the famous 0.30000000000000004. `0.1f.toDouble()` shows what 0.1f really is."""),

    q("round-to-int-ties-up-but-round-ties-even", r'''
        import kotlin.math.round
        import kotlin.math.roundToInt

        fun main() {
            println("${2.5.roundToInt()} ${(-2.5).roundToInt()} ${round(2.5)} " +
                "${round(3.5)} ${(-2.5).toInt()}")
        }
    ''', "3 -2 2.0 4.0 -2", ["3 -3 3.0 4.0 -2", "2 -2 2.0 4.0 -2", "3 -2 3.0 4.0 -3"],
      "roundToInt sends a tie toward positive infinity, but round() sends it to the even neighbour",
      """`2.5.roundToInt()` is 3 and `(-2.5).roundToInt()` is -2: halves go up. `round` gives a Double
      and uses banker's rounding: 2.5 becomes 2.0 and 3.5 becomes 4.0. `toInt()` just cuts, so -2.5 gives -2."""),

    # ── Batch 3: operators, data classes, control flow ─────────────────────
    q("plus-assign-on-a-list-var-or-val", r'''
        fun main() {
            var a = listOf(1)
            val b = a
            a += 2
            val m = mutableListOf(1)
            val n = m
            m += 2
            println("$a $b $m $n")
        }
    ''', "[1, 2] [1] [1, 2] [1, 2]",
    ["[1, 2] [1, 2] [1, 2] [1, 2]", "[1] [1] [1, 2] [1, 2]", "[1, 2] [1] [1, 2] [1]"],
      "`+=` on a var read-only list builds a new list; on a val mutable list it changes the same one",
      """For the `var`, `a += 2` means `a = a + 2`, a new list, so `b` still holds the old one. For the
      mutable `val`, `+=` calls `plusAssign`, which appends in place, so `n` sees the change."""),

    q("data-class-ignores-body-properties", r'''
        data class P(val x: Int) {
            var y = 0
        }

        fun main() {
            val a = P(1)
            val b = P(1).also { it.y = 5 }
            val c = b.copy()
            println("$a $b ${a == b} ${c.y}")
        }
    ''', "P(x=1) P(x=1) true 0",
    ["P(x=1, y=0) P(x=1, y=5) false 5", "P(x=1) P(x=1) false 5", "P(x=1) P(x=1) true 5"],
      "A data class only uses its constructor properties for toString, equals and copy",
      """`y` is declared in the body, so it is left out of `toString` and `==`, and `copy()` builds a
      new object from `x` alone, so `c.y` starts again at 0."""),

    q("generate-sequence-ends-on-null", r'''
        fun main() {
            val a = generateSequence(3) { if (it > 0) it - 1 else null }.toList()
            val b = generateSequence(1) { it * 2 }.takeWhile { it < 50 }.toList()
            val c = generateSequence(1) { it + 1 }.take(3).sum()
            println("$a $b $c")
        }
    ''', "[3, 2, 1, 0] [1, 2, 4, 8, 16, 32] 6",
    ["[3, 2, 1] [1, 2, 4, 8, 16, 32] 6", "[3, 2, 1, 0] [1, 2, 4, 8, 16, 32, 64] 6",
     "[3, 2, 1, 0] [2, 4, 8, 16, 32] 6"],
      "generateSequence stops when the step returns null, and an endless one needs a limit",
      """The seed 3 counts down, and the step returns null after 0, which ends the sequence with the 0
      included. The doubling one never ends by itself: `takeWhile` stops it before 50, and `take(3)` before 4."""),

    q("string-order-is-by-character-code", r'''
        fun main() {
            val w = listOf("banana", "Cherry", "apple")
            println("${w.sorted()} ${w.sortedBy { it.lowercase() }} ${"a" < "B"} " +
                "${"a".compareTo("B", ignoreCase = true) < 0}")
        }
    ''', "[Cherry, apple, banana] [apple, banana, Cherry] false true",
    ["[apple, banana, Cherry] [apple, banana, Cherry] true true",
     "[Cherry, apple, banana] [Cherry, apple, banana] false true",
     "[apple, banana, Cherry] [apple, banana, Cherry] false true"],
      "Strings compare by character code, so every capital letter sorts before every lower-case one",
      """'C' (67) is less than 'a' (97), so "Cherry" comes first in a plain sort, and `"a" < "B"` is
      false. Sorting by `lowercase()` or passing `ignoreCase = true` gives the dictionary order."""),

    q("return-in-finally-wins", r'''
        fun g(): Int {
            try { return 1 } finally { return 2 }
        }

        fun main() {
            val x = try { 1 } finally { 2 }
            println("$x ${g()}")
        }
    ''', "1 2", ["2 2", "1 1", "2 1"],
      "As an expression, the value of try is the try block's; a `return` in finally replaces it",
      """In `val x = try { 1 } finally { 2 }` the finally block runs but its value is discarded, so x is 1.
      A `return` inside finally, though, runs last and overrides the earlier `return 1`."""),

    q("build-string-append-overloads", r'''
        fun main() {
            val s = buildString {
                append('a')
                append('a' + 1)
                append(97)
                append('a'.code + 1)
                append(1.5f)
            }
            println(s)
        }
    ''', "ab97981.5", ["a98979981.5", "ab9798b1.5", "ab97981"],
      "append takes the argument's own type: a Char is added as a letter, an Int as its digits",
      """`'a' + 1` is a Char ('b'), so it is added as a letter. `97` and `'a'.code + 1` are Ints, so
      they are written as 97 and 98, and the Float is written as 1.5."""),

    q("put-and-remove-return-the-old-value", r'''
        fun main() {
            val m = mutableMapOf("a" to 1)
            println("${m.put("a", 2)} ${m.put("b", 3)} ${m.remove("a")} " +
                "${m.remove("zz")} $m")
        }
    ''', "1 null 2 null {b=3}",
    ["2 3 2 null {b=3}", "1 null 2 null {a=2, b=3}", "null null 1 null {b=3}"],
      "put and remove return what was there before, or null if nothing was",
      """The first `put` replaces the 1 and returns it; the second adds a new key, so it returns null.
      `remove("a")` returns the 2 that it deleted, and removing a missing key returns null."""),

    q("return-at-label-and-continue-at-label", r'''
        fun main() {
            val sb = StringBuilder()
            listOf(1, 2, 3).forEach {
                if (it == 2) return@forEach
                sb.append(it)
            }
            outer@ for (i in 1..3) for (j in 1..3) {
                if (j == 2) continue@outer
                sb.append(" $i$j")
            }
            println(sb)
        }
    ''', "13 11 21 31", ["1 11 21 31", "13 11 13 21 23 31 33", "13 11 12 21 22 31 32"],
      "`return@forEach` ends only that call of the lambda, so it acts like continue",
      """Returning from the lambda skips 2 but the loop goes on to 3, giving "13". The labelled
      `continue@outer` abandons the inner loop at j = 2, so only the pairs 11, 21 and 31 are added."""),

    q("regex-matches-needs-the-whole-string", r'''
        fun main() {
            val r = Regex("""\d+""")
            println("${r.matches("a12")} ${r.containsMatchIn("a12")} " +
                "${r.find("a12b345")?.value} " +
                "${r.findAll("a12b345").map { it.value }.toList()} " +
                "${r.matches("12")}")
        }
    ''', "false true 12 [12, 345] true",
    ["true true 12 [12, 345] true", "false true 345 [12, 345] true", "false true 12 [12] true"],
      "`matches` needs the pattern to cover the whole string; `find` looks for it anywhere",
      """"a12" is not made only of digits, so `matches` is false, but `containsMatchIn` is true.
      `find` returns the first match (12), and `findAll` yields every non-overlapping one."""),

    q("elvis-return-and-zero", r'''
        fun twice(s: String?): Int {
            val n = s?.toIntOrNull() ?: return -1
            return n * 2
        }

        fun main() {
            println("${twice("21")} ${twice("x")} ${twice(null)} ${twice("0")}")
        }
    ''', "42 -1 -1 0", ["42 0 0 0", "42 -1 -1 -1", "42 -1 0 0"],
      "`?: return` only triggers on null, and 0 is a perfectly good value",
      """`toIntOrNull` gives null for "x" and `s?.` gives null for a null string, so both leave the
      function early with -1. The string "0" parses to 0, which is not null, and doubles to 0."""),
)
