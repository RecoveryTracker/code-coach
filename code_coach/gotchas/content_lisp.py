"""Gotchas, Common Lisp: ABCL in --batch mode; portability notes are in langs.py (the `lisp` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("lisp")

ITEMS: tuple[Item, ...] = (
    q("mod-rem-floor", r'''
        (format t "~a ~a ~a~%" (mod -7 3) (rem -7 3) (floor -7 2))
    ''', "2 -1 -4", ["-1 -1 -3", "2 -1 -3", "-1 2 -4"],
      "mod follows floor division, rem follows truncation",
      """`mod` takes the sign of the divisor, so (mod -7 3) is 2, while `rem` takes the sign of the dividend and
      gives -1. `floor` rounds toward minus infinity, so -7/2 gives -4; it also returns the remainder as a
      second value, which `format` ignores."""),

    q("let-is-parallel", r'''
        (let ((x 1))
          (let ((x 2) (y x))
            (format t "~a ~a~%" x y)))
    ''', "2 1", ["2 2", "1 1", "1 2"],
      "In let, every init form is evaluated before any new binding exists",
      """The inner `let` evaluates `2` and `x` first, and the `x` in `(y x)` still refers to the outer x, which is
      1. Only then are the new x and y bound. Use `let*` if each binding should see the one before it."""),

    q("eq-equal-eql", r'''
        (format t "~a ~a ~a ~a~%"
                (eq (list 1) (list 1))
                (equal (list 1) (list 1))
                (eql 2.0 2)
                (= 2.0 2))
    ''', "NIL T NIL T", ["T T NIL T", "NIL T T T", "NIL NIL NIL T"],
      "eq is identity, equal is structure, eql is type-aware, = is numeric",
      """Two separately built lists are different objects, so `eq` says NIL, while `equal` compares the
      contents and says T. `eql` also compares type, so the float 2.0 and the integer 2 differ. `=` compares only
      the numeric value, so 2.0 and 2 are equal."""),
)
