"""Gotchas, Dart: run by `dart run` on the VM; portability notes are in langs.py (the `dart` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("dart")

ITEMS: tuple[Item, ...] = (
    q("division-operators", r'''
        void main() {
          print('${7 / 2} ${7 ~/ 2} ${-7 ~/ 2}');
        }
    ''', "3.5 3 -3", ["3 3 -3", "3.5 3 -4", "3 3 -4"],
      "/ always gives a double; ~/ is the integer division and truncates",
      """In Dart `7 / 2` is 3.5 even when both sides are ints. The `~/` operator divides and truncates toward zero,
      so 7 ~/ 2 is 3 and -7 ~/ 2 is -3 (not the floor, -4)."""),

    q("list-equality-is-identity", r'''
        void main() {
          var plain = [1, 2] == [1, 2];
          var same = const [1, 2] == const [1, 2];
          print('$plain $same');
        }
    ''', "false true", ["true true", "false false", "true false"],
      "== on two lists compares identity; equal const lists are one object",
      """`List` does not override `==`, so two separately built lists are never equal, however alike their
      contents. Compile-time constants are canonicalised: both `const [1, 2]` are literally the same object, so
      they are equal."""),

    q("lists-are-references", r'''
        void main() {
          final a = [1, 2];
          a.add(3);
          var b = a;
          b.add(4);
          print('${a.length} ${identical(a, b)}');
        }
    ''', "4 true", ["3 true", "4 false", "3 false"],
      "Assigning a list copies the reference, not the list",
      """`final` only stops `a` from being pointed somewhere else; it does not freeze the list, so `add` works.
      `var b = a` makes a second name for the same list, so the add through `b` is visible through `a`, and
      `identical` says so."""),
)
