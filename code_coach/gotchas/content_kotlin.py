"""Gotchas, Kotlin: kotlinc then the JVM; portability notes are in langs.py (the `kotlin` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("kotlin")

ITEMS: tuple[Item, ...] = (
    q("structural-versus-referential", r'''
        fun main() {
            val a = "hello"
            val b = StringBuilder("hel").append("lo").toString()
            println("${a == b} ${a === b}")
        }
    ''', "true false", ["true true", "false false", "false true"],
      "== compares contents in Kotlin; === compares object identity",
      """`==` calls `equals`, so two strings with the same characters are equal. `===` asks whether they are the
      very same object, and `b` was built at run time as a new string, not taken from the constant pool like
      the literal `a`."""),

    q("sequences-are-lazy", r'''
        fun main() {
            val log = mutableListOf<String>()
            listOf(1, 2).asSequence()
                .map { log.add("m$it"); it }
                .filter { log.add("f$it"); it > 1 }
                .toList()
            println(log.joinToString(" "))
        }
    ''', "m1 f1 m2 f2", ["m1 m2 f1 f2", "f1 f2 m1 m2", "m2 f2"],
      "A sequence sends each element through the whole chain before the next",
      """A list would run `map` over everything, then `filter` over the results. A sequence is lazy and pulls one
      element at a time through every step, so the log reads m1 f1 m2 f2. Nothing at all would run without the
      final `toList()`."""),

    q("char-arithmetic", r'''
        fun main() {
            println('a' + 1 + "c" + 1)
        }
    ''', "bc1", ["98c1", "ac1", "bc2"],
      "Char plus Int is a Char; the string only starts at the first string",
      """`'a' + 1` is the next character, 'b', not the number 98 (Kotlin keeps Char and Int apart). Then `+ "c"`
      turns it into a String, and everything after that is concatenated as text, so the last `1` is appended,
      not added."""),
)
