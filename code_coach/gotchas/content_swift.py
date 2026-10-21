"""Gotchas, Swift: swiftc then run; portability notes are in langs.py (the `swift` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("swift")

ITEMS: tuple[Item, ...] = (
    q("characters-are-graphemes", r'''
        let s = "e\u{301}"
        print(s.count, s.unicodeScalars.count, s.utf8.count)
    ''', "1 2 3", ["2 2 3", "1 1 2", "1 2 2"],
      "One visible character can be several scalars and more bytes",
      """"e" followed by a combining acute accent draws as one letter, so Swift's `count` says 1. It is two
      Unicode scalars (the e and the accent), and the accent needs two bytes in UTF-8, so the string is 3 bytes
      long."""),

    q("struct-copies-class-shares", r'''
        class Box { var n = 1 }
        struct Pt { var n = 1 }

        let c = Box()
        let d = c
        d.n = 5
        var p = Pt()
        var q = p
        q.n = 5
        print(c.n, p.n)
    ''', "5 1", ["1 1", "5 5", "1 5"],
      "A class is shared by reference; a struct is copied on assignment",
      """`d = c` makes a second reference to the one Box, so changing `d.n` changes `c.n` too. `var q = p` copies the
      struct, so `q.n = 5` leaves `p.n` alone at 1."""),

    q("nil-coalescing-precedence", r'''
        let n: Int? = nil
        print(n ?? 0 + 5)
    ''', "5", ["0", "nil", "Error"],
      "?? binds more loosely than +, so the whole 0 + 5 is the fallback",
      """Addition binds tighter than the nil-coalescing operator, so the whole `0 + 5` is the fallback. `n` is
      nil, so the fallback 5 is used. To add 5 to a value that defaults to 0 you would put the parentheses
      around the left-hand side instead."""),
)
