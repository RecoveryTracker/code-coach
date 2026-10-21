"""Gotchas, Common Lisp (second deck): numbers, equality, lists, loop, format. Same rules as content_lisp.py."""

from __future__ import annotations

from .items import Item, make

q = make("lisp")

ITEMS: tuple[Item, ...] = (
    # ── Numbers ────────────────────────────────────────────────────────────
    q("ratios-and-floats", r'''
        (format t "~a ~a ~a ~a~%"
                (/ 1 3) (/ 6 3) (/ 1.0 3) (+ 1/2 1/3))
    ''', "1/3 2 0.33333334 5/6", ["0.3333333 2.0 0.33333334 0.8333333",
      "1/3 2 0.3333333333333333 5/6", "0 2 0.33333334 0"],
      "Dividing integers gives an exact ratio; one float makes the result a float",
      """`(/ 1 3)` is the exact fraction 1/3, and `(/ 6 3)` reduces to the integer 2. Adding fractions stays
      exact: 1/2 + 1/3 is 5/6. Only the float 1.0 turns the result into a single-float, 0.33333334."""),

    q("double-float-contagion", r'''
        (format t "~a ~a ~a ~a~%"
                1.5d0 (/ 1 3.0d0) (* 1.0 1.5d0) (+ 1/2 0.25))
    ''', "1.5d0 0.3333333333333333d0 1.5d0 0.75", ["1.5 0.3333333333333333 1.5 0.75",
      "1.5d0 0.33333334 1.5 0.75", "1.5d0 0.3333333333333333d0 1.5 3/4"],
      "A double prints with a d0 marker, and mixing floats picks the bigger format",
      """The default float format is single, so a double-float is printed with `d0` to say it is different.
      Multiplying a single by a double produces a double, and a ratio plus a float is a float, 0.75."""),

    q("float-printing-ranges", r'''
        (format t "~a ~a ~a ~a~%"
                1234567.0 12345678.0 0.001 0.0001)
    ''', "1234567.0 1.2345678E7 0.001 1.0E-4", ["1234567.0 12345678.0 0.001 0.0001",
      "1234567.0 1.2345678E7 1.0E-3 1.0E-4", "1.234567E6 1.2345678E7 0.001 0.0001"],
      "Floats switch to scientific notation at 10 million and below one thousandth",
      """The printer uses plain digits for values from 10^-3 up to but not including 10^7, so 1234567.0 and
      0.001 print as written. 12345678.0 is above the range and becomes 1.2345678E7, and 0.0001 is below it and
      becomes 1.0E-4."""),

    q("round-half-even", r'''
        (format t "~a~%"
                (list (round 0.5) (round 1.5) (round 2.5) (round 7/2)))
    ''', "(0 2 2 4)", ["(1 2 3 4)", "(0 2 3 4)", "(1 2 3 3)"],
      "round sends exact halves to the nearest even integer",
      """0.5 is exactly between 0 and 1 and goes to the even 0; 1.5 goes to 2 and 2.5 goes to 2. The ratio 7/2
      is 3.5, which goes to the even neighbour 4. This is banker's rounding, so it is not 'half up'."""),

    q("floor-truncate-both-values", r'''
        (format t "~a ~a~%"
                (multiple-value-list (floor -7 2))
                (multiple-value-list (truncate -7 2)))
    ''', "(-4 1) (-3 -1)", ["(-3 -1) (-4 1)", "(-4 -1) (-3 1)", "(-3 1) (-4 -1)"],
      "floor and truncate each return a quotient and a remainder that match each other",
      """`floor` rounds the quotient down to -4, so the remainder 1 makes -4 * 2 + 1 = -7 work out. `truncate`
      rounds toward zero to -3, so its remainder is -1. Normally only the first value is used, as in `format`."""),

    q("sqrt-and-expt-surprises", r'''
        (format t "~a ~a ~a ~a~%"
                (sqrt 16) (sqrt -4) (expt 2 -1) (expt 2 100))
    ''', "4.0 #C(0.0 2.0) 1/2 1267650600228229401496703205376",
      ["4 #C(0.0 2.0) 0.5 1267650600228229401496703205376",
       "4.0 error 1/2 1267650600228229401496703205376",
       "4.0 #C(0.0 2.0) 0.5 1.2676506E30"],
      "sqrt returns a float (even for 16), may return a complex, and integers never overflow",
      """`(sqrt 16)` is the float 4.0, not the integer 4. The root of a negative number is the complex number
      #C(0.0 2.0). A negative integer power gives an exact ratio, and `expt` on integers grows into a bignum."""),

    q("number-equality-family", r'''
        (format t "~a~%"
                (list (eql 1 1.0) (equal 1 1.0) (equalp 1 1.0)
                      (= 1 1.0) (eql 1/2 0.5) (= 1/2 0.5)))
    ''', "(NIL NIL T T NIL T)", ["(T T T T T T)", "(NIL NIL NIL T NIL T)", "(NIL NIL T T T T)"],
      "= compares values, eql and equal also compare type, and equalp compares like =",
      """The integer 1 and the float 1.0 are different types, so `eql` and `equal` say NIL. `equalp` and `=` only
      look at the numeric value. The same holds for the ratio 1/2 and the float 0.5."""),

    q("bit-and-integer-functions", r'''
        (format t "~a~%"
                (list (ash 1 10) (ash -8 -1) (logand 12 10) (logxor 5 3)
                      (integer-length 255) (gcd 12 18) (lcm 4 6) (isqrt 17)))
    ''', "(1024 -4 8 6 8 6 12 4)", ["(1024 4 8 6 8 6 12 4)", "(1024 -4 8 6 255 6 12 4)",
      "(1024 -4 8 7 8 6 24 4)"],
      "ash shifts left for positive counts and right for negative ones, keeping the sign",
      """`(ash 1 10)` shifts left by 10: 1024. `(ash -8 -1)` shifts right by one, which keeps the sign and gives -4.
      `logand` of 1100 and 1010 is 1000 (8), `logxor` of 101 and 011 is 110 (6), and 255 needs 8 bits. `isqrt`
      is the integer square root, 4."""),

    q("parse-integer-rules", r'''
        (format t "~a~%"
                (list (parse-integer "42")
                      (parse-integer "12abc" :junk-allowed t)
                      (parse-integer "  7 ")
                      (parse-integer "x" :junk-allowed t)))
    ''', "(42 12 7 NIL)", ["(42 12 NIL NIL)", "(42 0 7 0)", "(42 12 7 0)"],
      "parse-integer ignores surrounding spaces, and :junk-allowed returns NIL when nothing parses",
      """Whitespace around the digits is allowed, so "  7 " is 7. With `:junk-allowed t` the parser stops at the
      first non-digit and returns what it has, 12 for "12abc"; if there are no digits at all the result is NIL,
      not 0."""),

    # ── Equality, truth and structure ──────────────────────────────────────
    q("equality-on-strings", r'''
        (format t "~a~%"
                (list (equal "ab" "ab") (equal "ab" "AB")
                      (equalp "ab" "AB") (string= "ab" "AB")
                      (string-equal "ab" "AB")))
    ''', "(T NIL T NIL T)", ["(T T T T T)", "(T NIL NIL NIL T)", "(T NIL T NIL NIL)"],
      "equal and string= care about case; equalp and string-equal do not",
      """Two strings with the same letters are `equal`, but case matters for `equal` and `string=`. `equalp` and
      `string-equal` ignore case, so "ab" and "AB" match there."""),

    q("eq-needs-the-same-object", r'''
        (let ((s (copy-seq "ab")))
          (format t "~a~%"
                  (list (eq s "ab") (equal s "ab") (eql 'a 'a)
                        (eq 'abc 'ABC))))
    ''', "(NIL T T T)", ["(T T T T)", "(NIL T T NIL)", "(NIL NIL T T)"],
      "eq asks whether two things are one object; symbols are, case-folded, but strings are not",
      """`copy-seq` makes a fresh string, so it is never `eq` to the literal even though the letters match.
      `equal` compares the contents and is true. The reader turns `abc` into ABC, so both spellings are the one
      symbol."""),

    q("truthiness", r'''
        (format t "~a~%"
                (list (if '() 'yes 'no) (if 0 'yes 'no) (if "" 'yes 'no)
                      (and 1 2 3) (or nil 0) (or nil nil)))
    ''', "(NO YES YES 3 0 NIL)", ["(NO NO NO 3 0 NIL)", "(NO YES YES T T NIL)", "(NO YES YES 3 NIL NIL)"],
      "Only NIL is false; 0 and the empty string are true, and and/or return a value",
      """The empty list is NIL, so it is false, but 0 and "" are true. `and` returns the last value if all are
      true, 3. `or` returns the first true value, and `(or nil 0)` is 0 because 0 counts as true."""),

    q("nil-is-everything", r'''
        (format t "~a~%"
                (list (null nil) (listp nil) (atom nil) (consp nil)
                      (symbolp nil) (eq nil '())))
    ''', "(T T T NIL T T)", ["(T T NIL NIL T T)", "(T T T T T T)", "(T NIL T NIL T T)"],
      "NIL is a symbol, the empty list, and an atom all at once",
      """NIL is the empty list, so it is a list and `null`. It is also a symbol and an atom, because it is not a
      cons cell, and `nil` and `'()` are the very same object. Only `consp` says no."""),

    q("conses-and-dots", r'''
        (format t "~a~%"
                (list (cons 1 2) (cons 1 '(2)) (cons '(1) '(2))
                      (append '(1 2) 3) (list* 1 2 '(3))))
    ''', "((1 . 2) (1 2) ((1) 2) (1 2 . 3) (1 2 3))",
      ["((1 2) (1 2) (1 2) (1 2 3) (1 2 3))", "((1 . 2) (1 2) (1 2) (1 2 3) (1 2 3))",
       "((1 . 2) (1 2) ((1) 2) (1 2 3) (1 2 3))"],
      "A cons whose second part is not a list prints with a dot",
      """`(cons 1 2)` is a pair whose second half is not a list, so a dot separates the halves. Consing onto a
      list extends it, but a list as the first part stays nested. `append` accepts any value as its last
      argument, so `(append '(1 2) 3)` ends with a dotted tail."""),

    q("list-accessors", r'''
        (format t "~a~%"
                (list (last '(1 2 3)) (butlast '(1 2 3)) (nth 5 '(1 2))
                      (nthcdr 2 '(a b c d)) (car nil) (cddr '(1 2 3))
                      (length '(1 (2 3) 4))))
    ''', "((3) (1 2) NIL (C D) NIL (3) 3)", ["(3 (1 2) NIL (C D) NIL (3) 4)",
      "((3) (1 2) 0 (C D) NIL 3 3)", "((3) (1 2) NIL (D) NIL (3) 3)"],
      "last returns the last cons, not the last element, and running off the end gives NIL",
      """`(last '(1 2 3))` is the list (3). Asking for an element past the end gives NIL, and `car` of NIL is NIL.
      `nthcdr 2` returns the rest of the list starting at the third element. The nested list counts as one
      element, so the length is 3."""),

    q("member-returns-the-tail", r'''
        (format t "~a~%"
                (list (member 2 '(1 2 3)) (member 5 '(1 2 3))
                      (position 3 '(1 2 3)) (find 2 '(1 2 3))
                      (find 'x '(a))))
    ''', "((2 3) NIL 2 2 NIL)", ["(T NIL 2 2 NIL)", "((2 3) NIL 3 2 NIL)", "(2 NIL 2 2 NIL)"],
      "member gives back the rest of the list starting at the match, position the index",
      """A found `member` returns the tail beginning with the item, (2 3), which is true but not just T.
      `position` counts from zero, so 3 sits at index 2. `find` returns the item itself."""),

    q("assoc-uses-eql", r'''
        (format t "~s~%"
                (list (assoc 'b '((a . 1) (b . 2)))
                      (assoc "b" '(("a" . 1) ("b" . 2)))
                      (assoc "b" '(("a" . 1) ("b" . 2)) :test #'string=)
                      (cdr (assoc 'z '((a . 1))))))
    ''', '((B . 2) NIL ("b" . 2) NIL)', ['((B . 2) ("b" . 2) ("b" . 2) NIL)', '(2 NIL 2 NIL)',
      '((B . 2) NIL ("b" . 2) 0)'],
      "assoc and member compare with eql, so string keys need :test",
      """Symbols are single objects, so `eql` finds `b`. Two strings with the same letters are different
      objects, so `(assoc "b" ...)` finds nothing and returns NIL until you pass `:test #'string=`. A missing
      key gives NIL, and the `cdr` of NIL is NIL."""),

    q("remove-duplicates-keeps-last", r'''
        (format t "~a~%"
                (list (remove-duplicates '(1 2 1 3 2))
                      (remove-duplicates '(1 2 1 3 2) :from-end t)
                      (remove 2 '(1 2 3 2))))
    ''', "((1 3 2) (1 2 3) (1 3))", ["((1 2 3) (1 2 3) (1 3))", "((1 3 2) (1 3 2) (1 3))",
      "((1 2 3) (1 3 2) (1 3))"],
      "remove-duplicates keeps the last copy of each item unless you say :from-end",
      """By default earlier duplicates are the ones removed, so the survivors are 1 (the second one), 3 and 2,
      in that order. With `:from-end t` the first copy of each is kept: (1 2 3). `remove` takes out every 2."""),

    q("reduce-direction", r'''
        (format t "~a~%"
                (list (reduce #'- '(10 3 2))
                      (reduce #'- '(10 3 2) :from-end t)
                      (reduce #'+ '() :initial-value 5)
                      (reduce #'list '(1 2 3))))
    ''', "(5 9 5 ((1 2) 3))", ["(9 5 5 (1 (2 3)))", "(5 9 0 ((1 2) 3))", "(5 9 5 (1 2 3))"],
      "reduce folds from the left unless :from-end is given",
      """From the left, 10 - 3 - 2 is 5. From the right it is 10 - (3 - 2) = 9. An empty list returns the
      :initial-value. `(reduce #'list '(1 2 3))` nests to the left: (list (list 1 2) 3)."""),

    q("mapcar-stops-at-the-shortest", r'''
        (format t "~a~%"
                (list (mapcar #'+ '(1 2 3) '(10 20))
                      (mapcar #'list '(1 2) '(a b c))
                      (mapcar #'1+ nil)
                      (map 'vector #'* #(1 2 3) #(4 5))))
    ''', "((11 22) ((1 A) (2 B)) NIL #(4 10))", ["((11 22 3) ((1 A) (2 B) (NIL C)) NIL #(4 10 3))",
      "((11 22) ((1 A) (2 B)) NIL (4 10))", "((11 22) ((1 A) (2 B)) 0 #(4 10))"],
      "Mapping over several sequences stops when the shortest one runs out",
      """With lists of different lengths, `mapcar` and `map` use only as many elements as the shortest has: two
      for the first and second, two again for the vectors. `map 'vector` builds a vector, while `mapcar`
      always builds a list. Mapping over NIL gives NIL."""),

    q("conses-share-structure", r'''
        (let* ((a (list 1 2))
               (b (cons 0 a))
               (c (append a '(3))))
          (setf (car a) 9)
          (format t "~a~%" (list b c)))
    ''', "((0 9 2) (1 2 3))", ["((0 1 2) (1 2 3))", "((0 9 2) (9 2 3))", "((0 1 2) (9 2 3))"],
      "cons shares its tail, while append copies every list but the last",
      """`b` is a new cons cell pointing at the same list `a`, so changing the first element of `a` shows up in
      b. `append` made a fresh copy of `a` before adding 3, so `c` still has the original 1."""),

    q("sort-vector-in-place", r'''
        (let* ((v (vector 3 1 2))
               (w (reverse v)))
          (format t "~a~%" (list v w (sort v #'<) v)))
    ''', "(#(1 2 3) #(2 1 3) #(1 2 3) #(1 2 3))", ["(#(3 1 2) #(2 1 3) #(1 2 3) #(1 2 3))",
      "(#(3 1 2) #(2 1 3) #(1 2 3) #(3 1 2))", "(#(1 2 3) #(2 1 3) #(1 2 3) #(3 1 2))"],
      "sort rearranges its argument, so every earlier mention of the vector sees it sorted",
      """`sort` on a vector works in place and returns that same vector. The list is only printed after all its
      elements were computed, so both `v` entries show the sorted contents. `reverse` made a separate copy
      earlier, and that copy is untouched."""),

    q("stable-sort-ties", r'''
        (format t "~a~%"
                (stable-sort (list '(b 2) '(a 2) '(c 1) '(d 1))
                             #'< :key #'cadr))
    ''', "((C 1) (D 1) (B 2) (A 2))", ["((C 1) (D 1) (A 2) (B 2))", "((D 1) (C 1) (A 2) (B 2))",
      "((B 2) (A 2) (C 1) (D 1))"],
      "stable-sort keeps equal items in their original order; it sorts by the key, not by name",
      """The key `cadr` picks the number, so the items with 1 come first. Items with equal keys stay as they
      were, B before A and C before D. Plain `sort` gives no such promise."""),

    q("backquote-splice", r'''
        (let ((x '(a b)))
          (format t "~a~%" `(x ,x ,@x ,(length x))))
    ''', "(X (A B) A B 2)", ["((A B) (A B) A B 2)", "(X (A B) (A B) 2)", "(X A B A B 2)"],
      "Inside a backquote, a comma inserts a value and ,@ splices a list's elements",
      """Without a comma the symbol `x` is just itself. `,x` inserts the list as one element, `,@x` pours its
      elements into the surrounding list, and `,(length x)` inserts the number 2."""),

    # ── Control flow and scope ─────────────────────────────────────────────
    q("do-versus-do-star", r'''
        (format t "~a~%"
                (list (do ((i 0 (1+ i)) (acc nil (cons i acc)))
                          ((= i 3) acc))
                      (do* ((i 0 (1+ i)) (acc nil (cons i acc)))
                           ((= i 3) acc))))
    ''', "((2 1 0) (3 2 1))", ["((0 1 2) (1 2 3))", "((2 1 0) (2 1 0))", "((3 2 1) (3 2 1))"],
      "do updates all its variables at once; do* updates them one after another",
      """In `do` every step form sees the old values, so `acc` collects the old `i`: 0, 1, 2, giving (2 1 0). In
      `do*` the steps run in order, so `acc` already sees the new `i`, and collects 1, 2, 3."""),

    q("defvar-does-not-reassign", r'''
        (defvar *n* 10)
        (defvar *n* 20)
        (defun show () *n*)
        (format t "~a ~a~%" (let ((*n* 2)) (show)) (show))
    ''', "2 10", ["2 20", "20 20", "10 10"],
      "defvar sets a variable only once, and let on a special variable rebinds it for callees",
      """The second `defvar` does nothing because `*n*` already has a value, so it stays 10. Special variables
      are dynamically scoped: inside the `let`, `show` sees the 2. After it ends the old value is back."""),

    q("closure-sees-later-changes", r'''
        (defun make-counter ()
          (let ((n 0))
            (lambda () (incf n))))
        (let ((a (make-counter)) (b (make-counter)) (x 1))
          (let ((f (lambda () x)))
            (setq x 2)
            (funcall a)
            (funcall a)
            (format t "~a ~a ~a~%" (funcall a) (funcall b) (funcall f))))
    ''', "3 1 2", ["3 3 1", "1 1 1", "3 1 1"],
      "A closure captures the variable, not its value, and each call to the maker has its own",
      """The counters `a` and `b` each close over their own `n`, so `a` has counted to 3 while `b` is at 1. The
      function `f` captured `x` itself, and `setq` changed that same variable to 2 before `f` was called."""),

    q("incf-push-pop-values", r'''
        (let ((x 5) (l (list 1 2 3)))
          (format t "~a~%"
                  (list (incf x) (prog1 x (incf x 10)) x
                        (pop l) l (push 0 l))))
    ''', "(6 6 16 1 (2 3) (0 2 3))", ["(5 5 15 1 (2 3) (0 2 3))", "(6 16 16 1 (2 3) (0 2 3))",
      "(6 6 16 1 (1 2 3) (0 1 2 3))"],
      "incf returns the new value, prog1 the old one, pop the removed element and push the new list",
      """`(incf x)` returns 6. `prog1` returns its first form's value (6) before running the rest, which raises x
      to 16. `(pop l)` returns 1 and shortens l, so the next `l` shows (2 3). `push` returns the longer list."""),

    q("case-keys-use-eql", r'''
        (format t "~a~%"
                (list (case 'a ((a b) 1) (t 2))
                      (case "a" ("a" 1) (t 2))
                      (case 1.0 (1 'int) (t 'other))
                      (case 5 ((1 2 3) 'low) ((4 5) 'high))
                      (case 9 (1 'one))))
    ''', "(1 2 OTHER HIGH NIL)", ["(1 1 INT HIGH NIL)", "(1 2 INT HIGH 0)", "(A 2 OTHER HIGH NIL)"],
      "case compares keys with eql, so strings and mixed number types never match",
      """A key list like `(a b)` matches either symbol. A string key is a different object from the string being
      tested, and the integer 1 is not `eql` to 1.0, so those fall through to `t`. With no matching clause and
      no `t`, `case` returns NIL."""),

    q("cond-clause-without-body", r'''
        (format t "~a~%"
                (list (cond ((> 1 2) 'a) ((+ 1 2)) (t 'c))
                      (when nil 1) (unless nil 1 2) (if nil 1)))
    ''', "(3 NIL 2 NIL)", ["(C NIL 2 NIL)", "(T NIL 2 NIL)", "(3 NIL 1 0)"],
      "A cond clause with only a test returns the test's own value when it is true",
      """The second clause `((+ 1 2))` has no body, so when its test is true, cond returns that test's value: 3.
      `when nil` and `if` without an else return NIL, and `unless` returns its last body form."""),

    q("return-leaves-the-nearest-block", r'''
        (format t "~a~%"
                (list (dolist (x '(1 2 3))
                        (when (> x 1) (return (* x 10))))
                      (dotimes (i 5) (when (= i 2) (return i)))
                      (block outer
                        (dolist (x '(1 2)) (return-from outer 'out))
                        'after)))
    ''', "(20 2 OUT)", ["(10 2 AFTER)", "(20 2 AFTER)", "(30 2 OUT)"],
      "return leaves the closest block named NIL; return-from names the block to leave",
      """`dolist` and `dotimes` wrap their body in a block called NIL, so `return` ends just that loop with a
      value: 20 from the first element above 1. In the third form `return-from outer` jumps out of the
      whole named block, so 'after is never reached."""),

    q("dolist-result-and-push", r'''
        (format t "~a ~a~%"
                (let ((acc nil))
                  (dolist (x '(1 2 3) acc)
                    (push (* x x) acc)))
                (dotimes (i 3 'done)))
    ''', "(9 4 1) DONE", ["(1 4 9) DONE", "(9 4 1) NIL", "NIL DONE"],
      "push adds to the front, and the third form of dolist or dotimes is the result",
      """Each square is pushed onto the front, so the list ends up in reverse: (9 4 1). A `dolist` or `dotimes`
      normally returns NIL, but its result form here gives back `acc` and the symbol DONE."""),

    # ── loop ───────────────────────────────────────────────────────────────
    q("loop-ranges", r'''
        (format t "~a~%"
                (list (loop for i from 1 to 5 sum i)
                      (loop for i below 5 collect i)
                      (loop for i from 10 downto 7 collect i)
                      (loop for i from 0 to 10 by 5 collect i)))
    ''', "(15 (0 1 2 3 4) (10 9 8 7) (0 5 10))", ["(15 (1 2 3 4 5) (10 9 8 7) (0 5 10))",
      "(15 (0 1 2 3 4) (10 9 8) (0 5 10))", "(15 (0 1 2 3 4 5) (10 9 8 7) (0 5))"],
      "to includes its limit, below does not, and downto counts down to its limit",
      """`for i below 5` starts at 0 and stops before 5, but `from 1 to 5` includes 5. `downto 7` includes 7, and
      `by 5` steps by five, reaching the limit 10 exactly."""),

    q("loop-for-in-parallel", r'''
        (format t "~a~%"
                (list (loop for x in '(1 2 3) for y in '(a b)
                            collect (list x y))
                      (loop for x = 1 then (* x 2) repeat 5 collect x)
                      (loop for x in '(1 2 3 4) when (evenp x) collect x)))
    ''', "(((1 A) (2 B)) (1 2 4 8 16) (2 4))", ["(((1 A) (2 B) (3 NIL)) (1 2 4 8 16) (2 4))",
      "(((1 A) (2 B)) (1 2 4 8 16 32) (2 4))", "(((1 A) (2 B)) (1 1 1 1 1) (2 4))"],
      "Two for clauses step together and end when the first runs out",
      """The loop over (1 2 3) and (a b) stops when `y` runs out, after two pairs. `for x = 1 then (* x 2)`
      starts at 1 and doubles it, and `repeat 5` limits it to five values."""),

    q("loop-over-nothing", r'''
        (format t "~a~%"
                (list (loop for x in '(3 1 4 1 5) maximize x)
                      (loop for x in '(3 1 4) count (oddp x))
                      (loop for x in '() sum x)
                      (loop for x in '() collect x)
                      (loop for x in '() always (> x 0))
                      (loop for x in '() thereis (> x 0))))
    ''', "(5 2 0 NIL T NIL)", ["(5 2 NIL NIL NIL NIL)", "(5 3 0 NIL T NIL)", "(5 2 0 NIL NIL T)"],
      "Over an empty list sum is 0, collect is NIL, always is true and thereis is false",
      """`count (oddp x)` counts the odd numbers 3 and 1: 2. With no elements, `sum` starts and stays at 0 and
      `collect` gives NIL. `always` is true if no element fails, so it holds for an empty list, while `thereis`
      needs one element to succeed and gives NIL."""),
    # ── Symbols, strings and format ────────────────────────────────────────
    q("symbol-case", r'''
        (format t "~s~%"
                (list (eq 'abc 'ABC) (symbol-name 'abc)
                      (eq (intern "abc") 'abc) (eq :a 'a) (string 'abc)))
    ''', '(T "ABC" NIL NIL "ABC")', ['(T "abc" T NIL "abc")', '(T "ABC" T NIL "ABC")',
      '(NIL "ABC" NIL NIL "ABC")'],
      "The reader upcases names, and intern does not, so intern \"abc\" is a different symbol",
      """`abc` is read as ABC, so `'abc` and `'ABC` are one symbol and its name is "ABC". `(intern "abc")` makes
      a symbol named exactly "abc", lower-case, which is not the same one. A keyword like `:a` lives in another
      package from `a`."""),

    q("format-a-versus-s", r'''
        (format t "~a|~s|~a|~s|~a~%"
                "hi" "hi" #\x '(#\y "z") nil)
    ''', '''hi|"hi"|x|(#\\y "z")|NIL''', ['''hi|hi|x|(y z)|NIL''', '''"hi"|"hi"|#\\x|(#\\y "z")|NIL''',
      '''hi|"hi"|x|(#\\y "z")|'''],
      "~a prints for people and ~s prints so that it can be read back",
      """`~a` leaves out the quotation marks and the #\\ of characters, while `~s` keeps them. This also applies
      inside lists. NIL is an ordinary symbol and prints as NIL with `~a`."""),

    q("format-padding-and-bases", r'''
        (format t "[~5d|~5a|~5@a|~,2f|~x|~b|~o]~%"
                42 "ab" "ab" 3.14159 255 5 8)
    ''', "[   42|ab   |   ab|3.14|FF|101|10]",
      ["[42|ab|ab|3.14|ff|101|10]", "[   42|   ab|ab   |3.14|FF|101|10]",
       "[   42|ab   |   ab|3.14|FF|101|8]"],
      "A number before the letter sets the width; the @ flag pads on the left instead of the right",
      """`~5d` right-aligns the number in 5 columns. `~5a` pads a string on the right, and `~5@a` on the left.
      `~,2f` keeps two decimals, `~x` prints upper-case hexadecimal, `~b` binary and `~o` octal, where 8 is
      written 10."""),
    q("format-iteration", r'''
        (format t "~{~a~^, ~}|~{(~a ~a)~}|~(~a~)|~r~%"
                '(1 2 3) '(1 2 3 4) "HeLLo" 12)
    ''', "1, 2, 3|(1 2)(3 4)|hello|twelve", ["1, 2, 3,|(1 2)(3 4)|hello|twelve",
      "1, 2, 3|(1 2 3 4)|hello|12", "1, 2, 3|(1 2)(3 4)|HELLO|twelve"],
      "~{ ... ~} loops over a list, ~^ leaves out the separator at the end, and ~( ... ~) lowers case",
      """The first loop prints each number, with `~^` stopping the comma after the last one. The second loop body
      uses two items per round, giving two pairs. `~(` ... `~)` turns its text to lower case, and `~r` spells
      the number out."""),

    q("string-function-results", r'''
        (format t "~s~%"
                (list (subseq "hello" 1 3) (search "lo" "hello")
                      (position #\a "banana" :from-end t)
                      (count #\a "banana") (remove #\a "banana")
                      (string-trim " " "  a b  ")))
    ''', '("el" 3 5 3 "bnn" "a b")', ['("ell" 3 5 3 "bnn" "a b")', '("el" 3 1 3 "bnn" "ab")',
      '("el" 2 5 3 "bnn" "a b")'],
      "subseq stops before the end index, and trim removes only the ends",
      """`(subseq "hello" 1 3)` takes the letters at index 1 and 2: "el". `search` gives the index of the match,
      3. `:from-end t` finds the last "a", at index 5. `string-trim` leaves the space between a and b alone."""),

    q("gethash-two-values", r'''
        (let ((h (make-hash-table)))
          (setf (gethash 'a h) nil)
          (setf (gethash "k" h) 1)
          (multiple-value-bind (v found) (gethash 'a h)
            (format t "~a~%" (list v found (gethash 'b h 'dflt)
                                   (gethash "k" h) (hash-table-count h)))))
    ''', "(NIL T DFLT NIL 2)", ["(NIL NIL DFLT NIL 2)", "(NIL T DFLT 1 2)", "(NIL T NIL NIL 1)"],
      "gethash returns a found flag too, and the default test is eql, which fails for strings",
      """A key stored with the value NIL still counts as found, which only the second value reveals. `'b` is
      missing, so the default `DFLT` is returned. The table compares keys with `eql`, so looking up another
      "k" string finds nothing."""),

    q("optional-key-defaults", r'''
        (defun f (a &optional (b (* a 2)) &key (c 1) d)
          (list a b c d))
        (format t "~a~%" (list (f 1) (f 1 5) (f 1 5 :d 9) (f 1 5 :c 7)))
    ''', "((1 2 1 NIL) (1 5 1 NIL) (1 5 1 9) (1 5 7 NIL))",
      ["((1 1 1 NIL) (1 5 1 NIL) (1 5 1 9) (1 5 7 NIL))", "((1 2 1 NIL) (1 5 1 NIL) (1 5 9 NIL) (1 5 7 NIL))",
       "((1 2 NIL NIL) (1 5 NIL NIL) (1 5 NIL 9) (1 5 7 NIL))"],
      "An optional parameter's default may use earlier parameters; keywords start where the optionals end",
      """When `b` is not passed it defaults to twice `a`, which is 2 for `(f 1)`. Keyword arguments are named, so
      `:d 9` fills only `d` and `:c 7` fills only `c`. The unmentioned keyword `d` is NIL, and `c` keeps its
      default 1."""),

    q("multiple-values-dropped", r'''
        (format t "~a ~a ~a~%"
                (floor 17 5) (values 1 2)
                (multiple-value-bind (q r) (floor 17 5) (list q r)))
    ''', "3 1 (3 2)", ["3 2 (3 2)", "(3 2) (1 2) (3 2)", "3 1 3"],
      "Only the first of several values is passed on unless you ask for the rest",
      """As an ordinary argument, `(floor 17 5)` contributes just the quotient 3 and `(values 1 2)` just 1.
      `multiple-value-bind` receives all of them, so it sees both the quotient 3 and the remainder 2."""),
)
