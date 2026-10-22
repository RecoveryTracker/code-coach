"""Gotchas, Common Lisp (third deck): ABCL in --batch mode; portability notes are in langs.py (the `lisp` entry).

New angles on the first two decks: the sequence functions' :key and :test arguments, destructive and sharing
operations on freshly built lists, format directives, setf places, handlers and the many faces of loop. Hash tables
are only looked up (never walked) and nothing here depends on the order SORT leaves a list in.
"""

from __future__ import annotations

from .items import Item, make

q = make("lisp")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ──────────────────────────────────────────────────────
    q("flet-versus-labels", r'''
        (defun f (n) (declare (ignore n)) 100)
        (format t "~a ~a~%"
                (flet ((f (n) (if (= n 0) 0 (+ n (f (1- n))))))
                  (f 3))
                (labels ((f (n) (if (= n 0) 0 (+ n (f (1- n))))))
                  (f 3)))
    ''', "103 6", ["6 6", "103 103", "3 6"],
      "A function defined with flet cannot call itself; labels can",
      """Inside `flet`, the name `f` in the body of the new function still means the old global `f`, which returns 100,
      so `(f 3)` is 3 + 100. `labels` makes the new `f` visible inside its own definition, so the recursion works
      and gives 3 + 2 + 1."""),

    q("prog1-prog2-progn-values", r'''
        (let ((x 0))
          (format t "~a~%"
                  (list (prog1 1 2 3) (prog2 1 2 3) (progn 1 2 3)
                        (prog1 (incf x) (incf x 10)) x)))
    ''', "(1 2 3 1 11)", ["(3 2 1 1 11)", "(1 2 3 11 11)", "(1 2 3 1 1)"],
      "prog1 returns its first form, prog2 its second, progn its last",
      """All three evaluate every form in order, but they differ in which value they keep. `prog1` is handy for
      reading a value before changing it: `(prog1 (incf x) (incf x 10))` returns 1, though x ends at 11."""),

    q("member-of-nil-is-truthy", r'''
        (format t "~a~%"
                (list (if (member nil '(a nil)) 'yes 'no)
                      (if (find nil '(a nil)) 'yes 'no)
                      (position nil '(a nil))
                      (member nil '(nil))))
    ''', "(YES NO 1 (NIL))", ["(YES YES 1 (NIL))", "(NO NO 1 NIL)", "(YES NO NIL (NIL))"],
      "member returns a tail, so finding NIL is still true; find returns the item itself, which is NIL",
      """`(member nil '(a nil))` returns the tail `(NIL)`, which is a non-empty list and therefore true. `find` returns
      the element it found, here NIL, which looks the same as not finding anything. `position` returns the index,
      1."""),

    q("string-less-returns-an-index", r'''
        (format t "~a~%"
                (list (string< "abc" "abd") (string< "b" "a") (string< "ab" "abc")
                      (string= "a" "a") (string/= "abc" "abd")
                      (string-lessp "ABC" "abd")))
    ''', "(2 NIL 2 T 2 2)", ["(T NIL T T T T)", "(2 NIL 3 T 2 2)", "(2 0 2 T 2 2)"],
      "string< and friends return the position of the first difference, not just T",
      """When the first string is smaller, `string<` returns the index where the strings first differ: 2 for "abc"
      and "abd", and also 2 for "ab" and "abc", where the shorter one runs out. When it is not smaller the answer is
      NIL. `string/=` also returns the index, and `string-lessp` ignores case."""),

    q("multiple-value-bind-pads-with-nil", r'''
        (format t "~a~%"
                (list (multiple-value-bind (a b c) (values 1 2) (list a b c))
                      (multiple-value-bind (a) (values 1 2) a)
                      (multiple-value-list (values))
                      (let ((x (values))) x)
                      (list (values 1 2))
                      (nth-value 1 (floor 7 2))))
    ''', "((1 2 NIL) 1 NIL NIL (1) 1)", ["((1 2) 1 NIL NIL (1 2) 1)", "((1 2 NIL) 1 (NIL) NIL (1) 1)",
                                       "((1 2 NIL) 2 NIL NIL (1) 1)"],
      "Missing values become NIL, extra ones are dropped, and a form with no values counts as NIL",
      """`multiple-value-bind` binds as many variables as it is given: a third one gets NIL when only two values
      exist, and a single variable keeps just the first. `(values)` returns nothing at all, so the list of values is
      empty, and used as a single value it is NIL. `nth-value 1` picks the remainder of `floor`."""),

    q("pushnew-uses-eql", r'''
        (let ((a (list "a")) (b (list "a")) (c (list 1)) (d (list '(1))))
          (pushnew "a" a)
          (pushnew "a" b :test #'equal)
          (pushnew 1 c)
          (pushnew '(1) d :test #'equal)
          (format t "~a~%" (list (length a) (length b) (length c) (length d))))
    ''', "(2 1 1 1)", ["(1 1 1 1)", "(2 2 1 1)", "(2 1 2 1)"],
      "pushnew compares with eql unless told otherwise, and two equal strings are not eql",
      """`pushnew` only adds an item if it is not already present, but 'present' is decided by `eql`. Two separate
      "a" strings are not `eql`, so the first list grows to two, while with `:test #'equal` the second list stays
      at one. The integer 1 is `eql` to itself and so is not added again."""),

    q("hash-table-needs-equal-for-strings", r'''
        (let ((a (make-hash-table))
              (b (make-hash-table :test 'equal)))
          (setf (gethash "k" a) 1)
          (setf (gethash "k" b) 1)
          (setf (gethash '(1 2) b) 2)
          (format t "~a~%" (list (gethash "k" a) (gethash "k" b)
                                 (gethash (list 1 2) b) (remhash "k" b)
                                 (remhash "k" b) (hash-table-count b))))
    ''', "(NIL 1 2 T NIL 1)", ["(1 1 2 T NIL 1)", "(NIL 1 NIL T NIL 1)", "(NIL 1 2 T T 0)"],
      "A hash table compares keys with eql by default, which never matches two separate strings",
      """The default table uses `eql`, and the "k" used to look up is a different string object from the one stored,
      so nothing is found: NIL. A table made with `:test 'equal` compares contents, also for lists. `remhash`
      returns T when it removed something and NIL the second time."""),

    q("make-array-initial-element-is-shared", r'''
        (let ((a (make-array 2 :initial-element (list 0)))
              (b (make-array 2 :initial-contents (list (list 0) (list 0)))))
          (incf (car (aref a 0)))
          (incf (car (aref b 0)))
          (format t "~a ~a~%" a b))
    ''', "#((1) (1)) #((1) (0))", ["#((1) (0)) #((1) (0))", "#((1) (1)) #((1) (1))",
                                   "#((1) (0)) #((1) (1))"],
      "The initial element is one object stored in every slot, not a copy per slot",
      """`:initial-element` evaluates its form once, so both slots hold the very same list, and changing it through one
      slot shows up in the other. With `:initial-contents` each slot got its own list, so only the first one
      changed. (A `push` would not show this: it replaces the slot with a new cons instead of changing the list.)"""),

    q("single-float-sum-drifts", r'''
        (let ((s 0.0) (d 0.0d0))
          (dotimes (i 10) (incf s 0.1) (incf d 0.1d0))
          (format t "~a ~a ~a ~a~%" s (= s 1) d (< (abs (- s 1)) 1e-6)))
    ''', "1.0000001 NIL 0.9999999999999999d0 T", ["1.0 T 1.0d0 T", "1.0000001 NIL 1.0d0 T",
                                                 "1.0000001 NIL 0.9999999999999999d0 NIL"],
      "Adding 0.1 ten times does not give exactly 1, in single or double precision",
      """Floats cannot store 0.1 exactly, and the small errors add up: a single float ends at 1.0000001 and a double
      at 0.9999999999999999d0, so neither equals 1. The single-float drift is still far below one millionth,
      so a tolerance check passes."""),

    # ── Medium ───────────────────────────────────────────────────────────
    q("maplist-and-mapcan", r'''
        (format t "~a~%"
                (list (maplist #'length '(a b c))
                      (maplist #'identity '(1 2))
                      (mapcan (lambda (x) (list x x)) '(1 2))
                      (mapcan (lambda (x) (and (oddp x) (list x))) '(1 2 3))
                      (mapc #'identity '(7 8))))
    ''', "((3 2 1) ((1 2) (2)) (1 1 2 2) (1 3) (7 8))",
      ["((3 2 1) (1 2) (1 1 2 2) (1 3) (7 8))", "((1 1 1) ((1 2) (2)) (1 1 2 2) (1 3) (7 8))",
       "((3 2 1) ((1 2) (2)) ((1 1) (2 2)) (1 3) (7 8))"],
      "maplist gives the function each remaining tail; mapcan joins the lists the function returns",
      """`maplist` calls the function on the whole list, then on its cdr, and so on, so lengths come out as 3, 2, 1.
      `mapcan` appends the (fresh) lists the function returns, so a function that returns NIL for an element
      simply drops it, which makes it act as a filter. `mapc` returns its first list."""),

    q("reduce-cons-and-initial-value", r'''
        (format t "~a~%"
                (list (reduce #'cons '(1 2 3))
                      (reduce #'cons '(1 2 3) :from-end t)
                      (reduce #'list '(1 2) :initial-value 0)
                      (reduce #'list '(1 2) :from-end t :initial-value 0)
                      (reduce #'max '((1) (5) (3)) :key #'car)))
    ''', "(((1 . 2) . 3) (1 2 . 3) ((0 1) 2) (1 (2 0)) 5)",
      ["((1 2 . 3) (1 2 . 3) ((0 1) 2) (1 (2 0)) 5)", "(((1 . 2) . 3) (1 2 . 3) (0 1 2) (1 (2 0)) 5)",
       "(((1 . 2) . 3) (1 2 . 3) ((0 1) 2) ((0 1) 2) 5)"],
      "reduce folds from the left by default, the initial value comes first, and :from-end puts it last",
      """From the left, `cons` builds a left-nested pair structure, and from the right it builds a list whose last
      cell is a dotted pair. An initial value is the first element on a left fold, giving ((0 1) 2), and the last on
      a right fold, giving (1 (2 0)). `:key` is applied to each element before the function sees it."""),

    q("some-and-every-return-values", r'''
        (format t "~a~%"
                (list (some #'evenp '(1 3 4))
                      (some (lambda (x) (and (> x 2) (* x 10))) '(1 3 4))
                      (every #'evenp '()) (some #'evenp '())
                      (notany #'evenp '(1 3)) (notevery #'evenp '(2 3))
                      (find-if #'evenp '(1 4 6)) (position-if #'evenp '(1 4 6))))
    ''', "(T 30 T NIL T T 4 1)", ["(T 3 T NIL T T 4 1)", "(T 30 NIL NIL T T 4 1)", "(T 30 T NIL T T (4 6) 1)"],
      "some returns the first true value the predicate produced, and every is true for an empty sequence",
      """`some` stops at the first element where the predicate gives a true value and returns that value itself, so a
      predicate that returns 30 makes `some` return 30. On an empty list `every` is vacuously true and `some` is
      false. `find-if` returns the element and `position-if` its index."""),

    q("key-and-test-arguments", r'''
        (format t "~s~%"
                (list (find 2 '((1 a) (2 b)) :key #'car)
                      (member '(1) '((0) (1) (2)) :test #'equal)
                      (position 3 '(1 2 3 4) :test #'<)
                      (count 'a '((a 1) (b 2) (a 3)) :key #'car)
                      (rassoc 2 '((a . 1) (b . 2)))
                      (remove-if-not #'oddp '(1 2 3 4 5) :start 1)
                      (assoc 2.0 '((1 . a) (2 . b)) :test #'=)))
    ''', "((2 B) ((1) (2)) 3 2 (B . 2) (1 3 5) (2 . B))",
      ["((2 B) ((1)) 3 2 (B . 2) (1 3 5) (2 . B))", "((2 B) ((1) (2)) 2 2 (B . 2) (1 3 5) (2 . B))",
       "((2 B) ((1) (2)) 3 2 (A . 1) (1 3 5) NIL)"],
      "The test gets the item and then each element; :key changes what is compared; :start limits the range",
      """`(position 3 '(1 2 3 4) :test #'<)` asks for the first element x with `(< 3 x)`, which is the 4 at index 3.
      `:key #'car` compares the first part of each pair, and `rassoc` searches by the cdr. `:start 1` keeps the first
      element out of the test, so the 1 stays while the even numbers after it are removed. `:test #'=` lets 2.0
      match 2."""),

    q("append-shares-its-last-argument", r'''
        (let* ((a (list 1 2)) (b (list 3))
               (c (append a b)) (d (nconc (list 0) b)))
          (setf (car b) 9)
          (setf (car a) 7)
          (format t "~a ~a ~a ~a~%" c d a b))
    ''', "(1 2 9) (0 9) (7 2) (9)", ["(1 2 3) (0 3) (7 2) (9)", "(7 2 9) (0 9) (7 2) (9)", "(1 2 9) (0 3) (7 2) (9)"],
      "append copies every argument except the last, which it shares; nconc copies none",
      """`(append a b)` builds new cells for `a` but ends with the original list `b`, so changing `(car b)` shows up
      in `c`, while changing `(car a)` does not. `nconc` links the cells of its arguments together without copying,
      so `d` ends in the same `b` cell too."""),

    q("sort-key-and-strings", r'''
        (format t "~s~%"
                (list (sort (vector "bb" "a" "ccc") #'< :key #'length)
                      (sort (copy-seq "hello") #'char<)
                      (sort (vector 3 1 2) #'> :key #'-)
                      (sort (vector "b" "A" "c") #'string<)
                      (sort (list 3 1 2) #'>)))
    ''', '(#("a" "bb" "ccc") "ehllo" #(1 2 3) #("A" "b" "c") (3 2 1))',
      ['(#("bb" "a" "ccc") "ehllo" #(1 2 3) #("A" "b" "c") (3 2 1))', '(#("a" "bb" "ccc") "ehllo" #(3 1 2) #("A" "b" "c") (3 2 1))',
       '(#("a" "bb" "ccc") "ehllo" #(1 2 3) #("b" "A" "c") (3 2 1))'],
      "The predicate decides the order, :key is applied before comparing, and uppercase sorts first",
      """`:key #'length` sorts the strings by length. With `:key #'-` the keys are -3, -1 and -2, and `#'>` puts the
      largest key first, which is -1: the numbers come out as 1, 2, 3. In `string<` "A" (65) comes before "b"
      (98), and `(sort ... #'>)` on a list returns the numbers largest first."""),

    q("coerce-and-concatenate-types", r'''
        (format t "~s~%"
                (list (coerce "ab" 'list) (coerce '(#\x #\y) 'string)
                      (concatenate 'string "a" "b" "c")
                      (concatenate 'list "ab" '(1))
                      (concatenate 'vector '(1) #(2))
                      (coerce '(1 2) 'vector) (string #\a) (string 'abc)))
    ''', '((#\\a #\\b) "xy" "abc" (#\\a #\\b 1) #(1 2) #(1 2) "a" "ABC")',
      ['("ab" "xy" "abc" (#\\a #\\b 1) #(1 2) #(1 2) "a" "ABC")', '((#\\a #\\b) "xy" "abc" ("ab" 1) #(1 2) #(1 2) "a" "ABC")',
       '((#\\a #\\b) "xy" "abc" (#\\a #\\b 1) (1 2) #(1 2) "a" "abc")'],
      "concatenate takes the result type as its first argument, and a string is a sequence of characters",
      """A string is a vector of characters, so `coerce` can turn it into a list of characters and back, and
      `concatenate` can join strings, lists and vectors into whichever type you name. `(string 'abc)` gives the
      symbol's name, which the reader made uppercase."""),

    q("format-conditional-directives", r'''
        (format t "~{~a~^|~}~%"
                (list (format nil "~[zero~;one~;two~:;many~]" 1)
                      (format nil "~[zero~;one~;two~:;many~]" 7)
                      (format nil "~:[no~;yes~]" nil)
                      (format nil "~:[no~;yes~]" 0)
                      (format nil "~D file~:P" 1)
                      (format nil "~D file~:P" 3)
                      (format nil "~a~@[ (~a)~]" "x" nil)
                      (format nil "~a~@[ (~a)~]" "x" 5)))
    ''', "one|many|no|yes|1 file|3 files|x|x (5)", ["one|many|no|no|1 file|3 files|x|x (5)",
                                                    "one|many|no|yes|1 file|3 file|x|x (5)",
                                                    "one|many|no|yes|1 file|3 files|x|x ()"],
      "~[ picks a clause by number, ~:[ by truth, ~:P pluralises, and ~@[ prints only for a true value",
      """`~[...~;...~]` selects the clause whose index equals the argument, with `~:;` as the default. `~:[no~;yes~]`
      chooses `no` only for NIL, so 0 gives `yes`. `~:P` pluralises after a number, and `~@[ (~a)~]` prints its
      text only when the argument is not NIL (and then uses it)."""),

    q("format-fixed-and-money", r'''
        (format t "~a~%"
                (list (format nil "~$" 3.14159) (format nil "~,2f" 3.14159)
                      (format nil "~7,2f" 3.14159) (format nil "~,0f" 3.7)
                      (format nil "~f" 3.5) (format nil "~,3f" 2)
                      (format nil "~5,'0d" 42) (format nil "~,1f" 0.96)))
    ''', "(3.14 3.14    3.14 4. 3.5 2.000 00042 1.0)",
      ["(3.14 3.14 3.14 4 3.5 2.000 00042 1.0)", "(3.14 3.14    3.14 4. 3.5 2.000 42 1.0)",
       "(3.14 3.14    3.14 4. 3.5 2 00042 0.9)"],
      "~,2f fixes the decimals, ~,0f keeps a trailing dot, and ~5,'0d pads with zeros",
      """`~$` prints two decimals by default, and `~7,2f` pads to seven columns. With no decimal digits the number
      is shown with a trailing point, `4.`. An integer given to `~,3f` is printed as a float with three digits, and
      0.96 rounds to 1.0 at one digit. `~5,'0d` pads an integer to width 5 with zeros."""),

    q("digit-char-p-and-char-codes", r'''
        (format t "~s~%"
                (list (digit-char-p #\7) (digit-char-p #\a 16) (digit-char-p #\x)
                      (char-code #\A) (code-char 97) (char< #\a #\b #\c)
                      (char-equal #\a #\A) (char= #\a #\A)
                      (- (char-code #\7) (char-code #\0))))
    ''', '(7 10 NIL 65 #\\a T T NIL 7)', ['(7 10 NIL 65 97 T T NIL 7)', '(T 10 NIL 65 #\\a T T NIL 7)',
                                         '(7 10 NIL 65 #\\a T NIL NIL 7)'],
      "digit-char-p returns the digit's value (or NIL), not just true, and char< accepts several arguments",
      """`digit-char-p` answers with the numeric weight of the character in the given radix, 7 for `#\\7` and 10 for
      `#\\a` in base 16, and NIL when it is not a digit. `char<` can compare a whole chain at once. `char-equal`
      ignores case, but `char=` does not, and subtracting character codes gives a digit's value."""),

    q("negative-zero-is-a-different-float", r'''
        (format t "~s~%"
                (list (= 0.0 -0.0) (eql 0.0 -0.0) (minusp -0.0) -0.0
                      (equal 0.0 -0.0) (zerop -0.0) (float-sign -0.0)))
    ''', "(T NIL NIL -0.0 NIL T -1.0)", ["(T T NIL -0.0 T T -1.0)", "(NIL NIL NIL 0.0 NIL T 1.0)",
                                         "(T NIL T -0.0 NIL T -1.0)"],
      "Floating-point has two zeros; = treats them as equal but eql, equal and float-sign tell them apart",
      """`=` compares numeric values, and 0.0 and -0.0 are the same number, but they are different objects of the
      float type, so `eql` and `equal` say NIL. `minusp` is false for -0.0 because it is not less than zero, and
      `float-sign` still reads its sign bit and returns -1.0."""),

    q("float-is-an-exact-fraction", r'''
        (format t "~a~%"
                (list (rational 0.5) (rational 0.1) (= 1/2 0.5) (= 1/10 0.1)
                      (float 1/3) (coerce 1/3 'double-float)
                      (= (rational 0.1) (rational 0.1d0))))
    ''', "(1/2 13421773/134217728 T NIL 0.33333334 0.3333333333333333d0 NIL)",
      ["(1/2 1/10 T T 0.33333334 0.3333333333333333d0 NIL)",
       "(1/2 13421773/134217728 T T 0.33333334 0.3333333333333333d0 NIL)",
       "(1/2 13421773/134217728 T NIL 0.3333333 0.3333333333333333d0 T)"],
      "A float is the exact fraction it really stores, so 0.1 is not 1/10 and single and double 0.1 differ",
      """The single float nearest 0.1 is really 13421773/134217728, which `rational` reports exactly. Since `=` compares
      numbers exactly, 1/10 is not equal to 0.1, although 1/2 is equal to 0.5, which is stored exactly. The double
      0.1d0 is a different fraction again, so the two floats are not equal."""),

    q("setf-getf-adds-at-the-front", r'''
        (let ((p (list :a 1)) (l (list 1 2 3)) (a 1) (b 2))
          (setf (getf p :b) 2)
          (setf (getf p :a) 10)
          (setf (nth 1 l) 'x)
          (rotatef a b)
          (format t "~a ~a ~a ~a ~a~%" p l (list a b) (getf p :z 'none)
                  (getf p :b)))
    ''', "(B 2 A 10) (1 X 3) (2 1) NONE 2", ["(A 10 B 2) (1 X 3) (2 1) NONE 2",
                                            "(B 2 A 10) (1 X 3) (1 2) NONE 2",
                                            "(B 2 A 1) (1 X 3) (2 1) NONE 2"],
      "setf on a new getf key adds it at the front of the plist, and existing keys are updated in place",
      """`(setf (getf p :b) 2)` for a key that is missing pushes the pair onto the front of the list, giving
      `(:B 2 :A 1)`, while setting `:a` again changes its value where it is. `(setf (nth 1 l) ...)` replaces an
      element, `rotatef` swaps two places, and `getf` takes an optional default for a missing key."""),

    q("alist-first-match-shadows", r'''
        (let ((al '((a . 1))))
          (setf al (acons 'a 2 al))
          (setf al (acons 'b 3 al))
          (format t "~a~%" (list (cdr (assoc 'a al)) (length al)
                                 (cdr (assoc 'a (cdr (cdr al))))
                                 (assoc 'z al) (mapcar #'car al))))
    ''', "(2 3 1 NIL (B A A))", ["(1 3 1 NIL (B A A))", "(2 2 1 NIL (B A A))", "(2 3 2 NIL (A A B))"],
      "acons adds at the front, so an older pair with the same key is shadowed, not replaced",
      """`acons` returns a new list with the pair in front and leaves the old pairs in place, so `assoc` finds the
      newest `a` first (2). The old `(a . 1)` is still in the list, three pairs in all, and shows up again when you
      look past the front ones."""),

    q("fill-pointer-vector-push", r'''
        (let ((v (make-array 2 :fill-pointer 0 :adjustable t)))
          (format t "~a~%"
                  (list (vector-push 'a v) (vector-push 'b v) (vector-push 'c v)
                        (length v) (vector-push-extend 'c v) (length v)
                        (vector-pop v) v)))
    ''', "(0 1 NIL 2 2 3 C #(A B))", ["(0 1 2 2 2 3 C #(A B))", "(0 1 NIL 2 2 3 C #(A B C))",
                                     "(0 1 NIL 2 3 3 C #(A B))"],
      "vector-push returns the index it used, or NIL when the vector is full; vector-push-extend grows it",
      """With a fill pointer, `length` is the number of elements pushed so far, not the array size. `vector-push`
      returns the index where it stored the item (0, then 1), and NIL when the vector is full, without adding the
      item. `vector-push-extend` makes room and returns the index (2). `vector-pop` takes the last element off,
      reducing the length."""),

    q("defstruct-equalp-and-copy", r'''
        (defstruct pt x y)
        (let* ((a (make-pt :x 1 :y (list 2)))
               (b (copy-pt a)) (c (make-pt :x 1 :y (list 2)))
               (same (list (equal a c) (equalp a c))))
          (setf (pt-x b) 5)
          (setf (car (pt-y b)) 3)
          (format t "~a ~a ~a ~a~%" (pt-x a) (pt-y a) same (pt-y (make-pt))))
    ''', "1 (3) (NIL T) NIL", ["1 (2) (NIL T) NIL", "5 (3) (NIL T) NIL", "1 (3) (T T) NIL"],
      "copy-structure is shallow, and equalp compares slots while equal does not",
      """`copy-pt` creates a new struct whose slots point to the same objects. Changing a number slot of the copy
      leaves the original alone, but changing the shared list through the copy shows up in both. `equal` compares
      structures with `eq`, so two separate ones are not equal, while `equalp` compares their slots. A slot never
      given is NIL."""),

    q("supplied-p-parameters", r'''
        (defun f (a &optional (b 5 b-p) &key (c 7 c-p))
          (list a b b-p c c-p))
        (defun g (&rest args) (list (length args) args))
        (format t "~a ~a ~a ~a ~a~%"
                (f 1) (f 1 5) (f 1 2 :c 7) (g) (apply #'g 1 '(2 3)))
    ''', "(1 5 NIL 7 NIL) (1 5 T 7 NIL) (1 2 T 7 T) (0 NIL) (3 (1 2 3))",
      ["(1 5 NIL 7 NIL) (1 5 NIL 7 NIL) (1 2 T 7 T) (0 NIL) (3 (1 2 3))",
       "(1 5 NIL 7 NIL) (1 5 T 7 NIL) (1 2 T 7 NIL) (0 NIL) (3 (1 2 3))",
       "(1 5 NIL 7 NIL) (1 5 T 7 NIL) (1 2 T 7 T) (0 NIL) (2 (1 (2 3)))"],
      "A supplied-p variable says whether the argument was passed, even when it equals the default",
      """In `(f 1 5)` the value 5 equals the default, but `b-p` is T because the caller passed it. Likewise `c-p` is
      T for `:c 7` though 7 is the default. `apply` spreads its last argument into separate ones, so `&rest` collects
      three items, while `(g)` receives none."""),

    q("handler-case-picks-by-condition-type", r'''
        (format t "~s~%"
                (list (handler-case (/ 1 0) (division-by-zero () 'div0))
                      (handler-case (error "boom") (error (e) (format nil "~a" e)))
                      (handler-case 42 (error () 'err))
                      (handler-case (car 5) (type-error () 'type))
                      (handler-case (error "x") (warning () 'w) (error () 'e))
                      (ignore-errors (error "x"))
                      (typep (nth-value 1 (ignore-errors (error "x"))) 'error)))
    ''', '(DIV0 "boom" 42 TYPE E NIL T)',
      ['(DIV0 "boom" 42 TYPE W NIL T)', '(DIV0 "boom" ERR TYPE E NIL T)', '(DIV0 "boom" 42 TYPE E NIL NIL)'],
      "handler-case runs the first clause whose type matches, and returns the body's value if all is well",
      """Each clause names a condition type, and the first one that fits the signalled condition is used. A body that
      finishes normally just returns its value, so 42 stays 42. `ignore-errors` returns NIL for a failed body, and
      its second value is the condition object, which is of type `error`."""),

    q("unwind-protect-runs-on-exit", r'''
        (let ((log nil))
          (block b
            (unwind-protect
                (progn (push 'body log) (return-from b 1))
              (push 'cleanup log)))
          (push (catch 'tag
                  (unwind-protect (throw 'tag 'thrown)
                    (push 'cleanup2 log)))
                log)
          (format t "~a~%" (reverse log)))
    ''', "(BODY CLEANUP CLEANUP2 THROWN)", ["(BODY CLEANUP THROWN CLEANUP2)", "(BODY THROWN CLEANUP CLEANUP2)",
                                          "(BODY CLEANUP THROWN)"],
      "The cleanup forms of unwind-protect run on any exit, including return-from and throw",
      """`return-from` and `throw` both leave the protected form early, and the cleanup form runs on the way out,
      before control arrives at the block or the catch. In the second case the thrown value is pushed only after
      its cleanup has already been logged."""),

    q("typecase-first-match-and-nil", r'''
        (flet ((kind (x)
                 (typecase x
                   (null 'null) (integer 'int) (number 'num) (string 'str)
                   (symbol 'sym) (list 'list) (sequence 'seq) (t 'other))))
          (format t "~a~%" (mapcar #'kind (list nil 5 1.5 "s" 'a '(1) #(1) #\a))))
    ''', "(NULL INT NUM STR SYM LIST SEQ OTHER)", ["(LIST INT NUM STR SYM LIST SEQ OTHER)",
                                                  "(NULL NUM NUM STR SYM LIST SEQ OTHER)",
                                                  "(NULL INT NUM SEQ SYM LIST SEQ OTHER)"],
      "typecase takes the first matching clause; NIL is a symbol, a list and of type null all at once",
      """The clauses are tried in order, so the specific `null` must come before `symbol` and `list`, which NIL also
      belongs to. 5 is an integer and so is also a number, but the integer clause is first. Strings and vectors
      are sequences too, so the earlier `string` clause is what stops the string from reaching it."""),

    q("subst-sublis-and-flatten", r'''
        (labels ((fl (x)
                   (cond ((null x) nil)
                         ((atom x) (list x))
                         (t (append (fl (car x)) (fl (cdr x)))))))
          (format t "~a~%" (list (subst 'x 'a '(a (b a) a))
                                 (sublis '((a . 1) (b . 2)) '(a (b c)))
                                 (fl '(1 (2 (3)) () 4))
                                 (subst-if 0 #'numberp '(a 1 (2 b))))))
    ''', "((X (B X) X) (1 (2 C)) (1 2 3 4) (A 0 (0 B)))",
      ["((X (B A) X) (1 (2 C)) (1 2 3 4) (A 0 (0 B)))", "((X (B X) X) (1 (2 C)) (1 2 3 4 NIL) (A 0 (0 B)))",
       "((X (B X) X) (1 (B C)) (1 2 3 4) (A 0 (0 B)))"],
      "subst and sublis replace at any depth; a hand-made flatten must treat NIL as the empty list",
      """`subst` walks the whole tree, so it replaces `a` at every depth. `sublis` does the same with a table of
      replacements. The flatten function has to test `null` before `atom`, since NIL is both: otherwise the
      empty list inside would be kept as an element."""),

    q("loop-on-iterates-sublists", r'''
        (format t "~a~%"
                (list (loop for x on '(1 2 3) collect x)
                      (loop for x on '(1 2 3) by #'cddr collect x)
                      (loop for (a b) on '(1 2 3 4) by #'cddr collect (+ a b))
                      (loop for x across #(1 2 3) sum x)
                      (loop for (a b) on '(1 2 3) collect (list a b))))
    ''', "(((1 2 3) (2 3) (3)) ((1 2 3) (3)) (3 7) 6 ((1 2) (2 3) (3 NIL)))",
      ["((1 2 3) ((1 2 3) (3)) (3 7) 6 ((1 2) (2 3) (3 NIL)))", "(((1 2 3) (2 3) (3)) ((1 2 3) (3)) (3 7) 6 ((1 2) (2 3)))",
       "(((1 2 3) (2 3) (3)) ((1 2 3) (3)) (3 7) 3 ((1 2) (2 3) (3 NIL)))"],
      "for x on walks the tails of the list; by #'cddr steps two at a time; destructuring pads with NIL",
      """`for x on list` binds `x` to the whole list, then its cdr, and so on. `by #'cddr` skips ahead by two cells. With
      a destructuring pattern `(a b)`, each tail supplies its first two elements, and the last tail has only
      one, so `b` is NIL."""),

    q("loop-destructuring-patterns", r'''
        (format t "~a~%"
                (list (loop for (a b) in '((1 2) (3 4)) collect (+ a b))
                      (loop for (k . v) in '((a . 1) (b . 2))
                            collect (list v k))
                      (loop for (a b c) in '((1 2)) collect (list a b c))
                      (loop for (a nil c) in '((1 2 3)) collect (list a c))
                      (loop for i from 1 to 3 for (x . y) = (cons i (* i i))
                            collect y)))
    ''', "((3 7) ((1 A) (2 B)) ((1 2 NIL)) ((1 3)) (1 4 9))",
      ["((3 7) ((1 A) (2 B)) ((1 2)) ((1 3)) (1 4 9))", "((3 7) ((A 1) (B 2)) ((1 2 NIL)) ((1 3)) (1 4 9))",
       "((3 7) ((1 A) (2 B)) ((1 2 NIL)) ((1 2 3)) (1 4 9))"],
      "A loop variable can be a pattern: missing parts are NIL, and a NIL in the pattern skips a position",
      """`for (a b) in` takes each element apart, `(k . v)` splits a pair, and a pattern longer than the data gives NIL for
      the rest. Writing NIL in the pattern ignores that position, so `(a nil c)` takes the first and third. A `for`
      with `=` can destructure the value of a form too."""),

    q("loop-for-and-is-parallel", r'''
        (format t "~a~%"
                (list (loop for a = 1 then (+ a b) and b = 1 then a
                            repeat 6 collect a)
                      (loop for a = 1 then (+ a b) for b = 1 then a
                            repeat 6 collect a)))
    ''', "((1 2 3 5 8 13) (1 2 4 8 16 32))", ["((1 2 4 8 16 32) (1 2 3 5 8 13))",
                                              "((1 2 3 5 8 13) (1 2 3 5 8 13))", "((1 1 2 3 5 8) (1 2 4 8 16 32))"],
      "Consecutive for clauses update one after another; with and they update together",
      """In the second form `b` is updated after `a`, so `b = a` sees the new `a` and the values simply double. Joining
      the clauses with `and` makes both steps use the old values, which gives a Fibonacci-like sequence."""),

    q("loop-into-and-named-return", r'''
        (format t "~a~%"
                (list (loop for i from 1 to 3 collect (* i i) into sq
                            finally (return (reverse sq)))
                      (loop for x in '(1 2 3) sum x into s collect s)
                      (loop named outer for i below 3
                            do (loop for j below 3
                                     do (when (= (* i j) 2)
                                          (return-from outer (list i j)))))
                      (loop for x in '(1 2 3) do (when (> x 1) (return x)))))
    ''', "((9 4 1) (1 3 6) (1 2) 2)", ["((1 4 9) (1 3 6) (1 2) 2)", "((9 4 1) (6) (1 2) 2)", "((9 4 1) (1 3 6) (1 2) 3)"],
      "into names an accumulator, finally can return it, and return only leaves the nearest loop",
      """`collect ... into sq` fills a variable that `finally` can use, here reversed. `sum x into s collect s` collects the
      running total after each addition. A plain `return` leaves just the loop it is in, while `return-from` a
      named loop leaves the outer one, so the search stops at i = 1, j = 2."""),
)
