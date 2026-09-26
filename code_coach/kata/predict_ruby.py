"""Predict the output, in Ruby.

Ruby is built to read like English, and most of what surprises people
about it is the English being more literal than they expected. `p` and
`puts` both print, but only one of them shows you what the value is.
Every value is an object, `nil` included, so `nil` has methods. Only
`nil` and `false` are false — 0 and the empty string are true, which is
the opposite of Python and JavaScript. A method hands back its last
expression whether you meant it to or not, and a block written with
`do ... end` attaches itself to whichever call is furthest out.

Strings are the other trap. A Ruby string is mutable, `<<` changes it in
place, and two names for one string both see the change. Ruby 4 has not
made string literals frozen by default: a plain literal is "chilled",
which still lets `<<` through without a word unless deprecation warnings
are switched on. The `# frozen_string_literal: true` comment is what
freezes them, and the puzzle that uses it says so.

Every expected output was typed out first and then checked against
Ruby 4.0.6, and the suite keeps checking — the same way round as the
rest of predict.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p


RUBY_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-ruby-puts-p-print",
        level=1,
        language="ruby",
        name="Three ways to print",
        family="Ruby",
        code=(
            'x = puts("hi")\n'
            "p x\n"
            'p "hi"\n'
            'print "a", "b"\n'
            "puts\n"
            "puts [1, [2, 3]]"
        ),
        expect='hi\nnil\n"hi"\nab\n1\n2\n3',
        why=(
            "`puts` writes a value for a person to read and returns nil, "
            "so `x` is nil — and `p` shows it as the word nil rather than "
            "a blank line. `p` prints what the value is, quotes and all, "
            "which is why it is the one to debug with. `print` adds no "
            "newline, so the bare `puts` supplies it. And `puts` given an "
            "array prints every element on its own line, flattening the "
            "nested one on the way."
        ),
    ),
    _p(
        id="predict-ruby-truthiness",
        level=2,
        language="ruby",
        name="What counts as false",
        family="Ruby",
        code=(
            '[0, "", nil, false].each do |v|\n'
            '  puts(v ? "true" : "false")\n'
            "end\n"
            "a = 0\n"
            "a ||= 5\n"
            "b = nil\n"
            "b ||= 5\n"
            "p a, b"
        ),
        expect="true\ntrue\nfalse\nfalse\n0\n5",
        why=(
            "Only two values are false in Ruby: nil and false. Zero and "
            "the empty string are true, the reverse of Python, JavaScript "
            "and C. `||=` follows the same rule — it assigns only when the "
            "variable is nil or false — so the 0 survives and the nil is "
            "replaced. Code ported from Python that writes `count ||= 1` "
            "expecting to replace a zero never does."
        ),
    ),
    _p(
        id="predict-ruby-division",
        level=2,
        language="ruby",
        name="Whole numbers, divided",
        family="Ruby",
        code=(
            "p 7 / 2\n"
            "p(-7 / 2)\n"
            "p 7 % -3\n"
            "p 7.fdiv(2)\n"
            "p 7 / 2.0"
        ),
        expect="3\n-4\n-2\n3.5\n3.5",
        why=(
            "Two Integers divide to an Integer, so 7 / 2 loses the half. "
            "Ruby rounds down, not towards zero, so -7 / 2 is -4 (C and "
            "Java say -3), and the remainder takes the sign of the right-"
            "hand side, so 7 % -3 is -2. For the true quotient, make one "
            "side a Float or ask for it with `fdiv`."
        ),
    ),
    _p(
        id="predict-ruby-ranges",
        level=2,
        language="ruby",
        name="Two dots or three",
        family="Ruby",
        code=(
            "a = (1..4).to_a\n"
            "b = (1...4).to_a\n"
            "p a, b\n"
            's = "abcdef"\n'
            "p s[1..3], s[1...3], s[-2..]"
        ),
        expect='[1, 2, 3, 4]\n[1, 2, 3]\n"bcd"\n"bc"\n"ef"',
        why=(
            "Two dots include the end and three dots leave it out — the "
            "extra dot is the one that pushes the last value off. The "
            "same ranges slice strings and arrays, counting from zero, "
            "and a range with no end runs to the end: `s[-2..]` is the "
            "last two characters."
        ),
    ),
    _p(
        id="predict-ruby-symbol-keys",
        level=2,
        language="ruby",
        name="The same key, twice",
        family="Ruby",
        code=(
            'h = { a: 1, "a" => 2 }\n'
            'p h[:a], h["a"], h.size\n'
            "p h\n"
            'g = { "b": 3 }\n'
            'p g[:b], g["b"]'
        ),
        expect='1\n2\n2\n{a: 1, "a" => 2}\n3\nnil',
        why=(
            "`a:` is the symbol :a and `\"a\" =>` is the string \"a\", and "
            "to a Hash those are two different keys — so the hash holds "
            "both. The trap is the third one: `\"b\":` looks like a string "
            "key, but a colon after the quotes still makes a symbol, so "
            "looking it up by the string finds nothing. Rails hides this "
            "with a hash that treats both alike; plain Ruby does not."
        ),
    ),
    _p(
        id="predict-ruby-everything-object",
        level=2,
        language="ruby",
        name="Even nothing is an object",
        family="Ruby",
        code=(
            "p nil.to_a, nil.to_s, nil.to_i\n"
            "p nil.class, 5.class\n"
            "p 1.+(2), 1.send(:*, 3)\n"
            "p 3.times.to_a"
        ),
        expect='[]\n""\n0\nNilClass\nInteger\n3\n3\n[0, 1, 2]',
        why=(
            "nil is the one instance of NilClass, and it has methods like "
            "anything else: an empty array, an empty string and zero are "
            "its conversions. Operators are method calls too — `1 + 2` is "
            "`1.+(2)`, which is why `send(:*, 3)` works. And `3.times` "
            "with no block hands back something you can turn into the "
            "numbers it would have counted."
        ),
    ),
    _p(
        id="predict-ruby-each-returns",
        level=3,
        language="ruby",
        name="The last line answers",
        family="Ruby",
        code=(
            "def tens(nums)\n"
            "  nums.each { |n| n * 10 }\n"
            "end\n"
            "def grade(n)\n"
            '  "pass" if n > 50\n'
            "end\n"
            "p tens([1, 2]), [1, 2].map { |n| n * 10 }\n"
            "p grade(80), grade(20)"
        ),
        expect='[1, 2]\n[10, 20]\n"pass"\nnil',
        why=(
            "A Ruby method returns its last expression, no `return` "
            "needed. In `tens` that is the `each`, and `each` returns the "
            "array it walked, not what the block worked out — the block's "
            "answers are thrown away. `map` is the one that collects them. "
            "In `grade` the last expression is an `if` with no else, "
            "which is nil when the test fails."
        ),
    ),
    _p(
        id="predict-ruby-shared-string",
        level=3,
        language="ruby",
        name="Appending to a borrowed string",
        family="Ruby",
        code=(
            'a = "ab"\n'
            "b = a\n"
            'b << "c"\n'
            'b += "d"\n'
            'b << "e"\n'
            "p a, b\n"
            'p "ab" * 2'
        ),
        expect='"abc"\n"abcde"\n"abab"',
        why=(
            "Ruby strings can change, and `b = a` copies nothing: both "
            "names hold one string, so `<<` through b is seen through a. "
            "`+=` is different — it builds a new string and points b at "
            "it, so from then on the two are apart and the last `<<` "
            "reaches only b. `*` on a string repeats it."
        ),
    ),
    _p(
        id="predict-ruby-array-new-shared",
        level=4,
        language="ruby",
        name="Three empty lists, or one",
        family="Ruby",
        code=(
            "grid = Array.new(3, [])\n"
            "grid[0] << 1\n"
            "fresh = Array.new(3) { [] }\n"
            "fresh[0] << 1\n"
            "p grid, fresh\n"
            "grid[1] = [9]\n"
            "p grid"
        ),
        expect="[[1], [1], [1]]\n[[1], [], []]\n[[1], [9], [1]]",
        why=(
            "`Array.new(3, [])` evaluates `[]` once and puts that one "
            "array in all three slots, so pushing into one pushes into "
            "all of them. The block form runs the block per slot and gets "
            "three arrays. Assigning `grid[1] = [9]` does not change the "
            "shared array — it replaces what the middle slot points at, "
            "so the other two still share."
        ),
    ),
    _p(
        id="predict-ruby-bang-frozen",
        level=4,
        language="ruby",
        name="Shouting at a frozen string",
        family="Ruby",
        code=(
            "# frozen_string_literal: true\n"
            's = "HELLO"\n'
            "t = s.downcase\n"
            "p t.downcase!, t.upcase!, t\n"
            "begin\n"
            "  s.downcase!\n"
            "rescue FrozenError\n"
            '  puts "frozen"\n'
            "end\n"
            'p s, "#{s}!".frozen?'
        ),
        expect='nil\n"HELLO"\n"HELLO"\nfrozen\n"HELLO"\nfalse',
        why=(
            "A `!` method changes the string in place, and returns nil "
            "when there was nothing to change — so `t.downcase!` on a "
            "lower-case string is nil, and chaining off it breaks. The "
            "magic comment on the first line freezes every plain literal "
            "in the file, so the `!` on s raises. Without it Ruby 4 still "
            "lets literals change. `downcase` without the bang made a new, "
            "unfrozen string, and so does interpolation."
        ),
    ),
    _p(
        id="predict-ruby-yield-do-block",
        level=4,
        language="ruby",
        name="Whose block is it",
        family="Ruby",
        code=(
            "def twice\n"
            '  return "no block" unless block_given?\n'
            "  yield(1) + yield(2)\n"
            "end\n"
            "p twice { |n| n * 10 }\n"
            "p twice\n"
            "p twice do |n| n * 10 end"
        ),
        expect='30\n"no block"\n"no block"',
        why=(
            "`yield` calls the block the method was given, once per "
            "yield, so the first call adds 10 and 20. Braces bind to the "
            "nearest call and `do ... end` binds to the outermost one, so "
            "on the last line the block goes to `p`, which ignores it, "
            "and `twice` runs with no block at all. `puts list.map do "
            "... end` prints an Enumerator for the same reason."
        ),
    ),
    _p(
        id="predict-ruby-send-defined",
        level=5,
        language="ruby",
        name="Private, unless you insist",
        family="Ruby",
        code=(
            "class Safe\n"
            "  private\n"
            '  def secret = "shh"\n'
            "end\n"
            "s = Safe.new\n"
            "p s.respond_to?(:secret)\n"
            "p s.send(:secret)\n"
            "p defined?(s), defined?(nope), defined?(puts), defined?(String)"
        ),
        expect=(
            'false\n"shh"\n"local-variable"\nnil\n"method"\n"constant"'
        ),
        why=(
            "Private in Ruby means you cannot call it with a dot, and "
            "`respond_to?` agrees, but `send` calls any method by name "
            "and skips the check. `defined?` is not a method but a "
            "keyword: it never evaluates its argument, it describes it — "
            "as a string, or nil for something that does not exist. A "
            "class name is a constant, and it says so."
        ),
    ),
)
