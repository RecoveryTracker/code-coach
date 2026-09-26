"""The code magnet puzzles in Ruby.

The same puzzle as the other languages: the lines of a program that
works, jumbled, to be put back in an order that prints the right thing.
The shapes are the ones a Ruby course reaches first — a class with
`initialize` and `attr_reader`, two methods and their callers, a loop
with `each_with_index`, a method that yields to a block, a hash built up
and walked, and `begin`/`rescue`/`ensure`.

Ruby runs a file top to bottom, and that includes `def`. A method does
not exist until the line defining it has run, so a call placed above
its `def` is a NoMethodError rather than a different right answer —
JavaScript hoists its functions and Dart reads every declaration first,
but Ruby does neither. Two methods can still go either way round, as
long as both are defined before the first call reaches them.

Most of the rest is `end`. Every `class`, `def`, `do`, `while` and
`begin` closes with one, and they all look the same, so which `end`
belongs where is most of what a jumble asks.

The expected output beside each was typed out by a person and is held
to what Ruby actually prints by tests/test_magnets_ruby.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m


RUBY_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-ruby-class",
        plan=(
            ("Open the class and let the name be read", 2),
            ("Keep the name when a dog is made", 3),
            ("A method that speaks using the name", 3),
            ("Close the class", 1),
            ("Make a dog and hear from it", 3),
        ),
        level=1,
        name="A class with a reader and a method",
        family="Ruby",
        language="ruby",
        note=(
            "`initialize` is what `Dog.new` calls, and `@name` is the "
            "instance variable it fills. `attr_reader :name` writes the "
            "method that reads it back, which is why `speak` can say "
            "`name` with no @ at all. The class has to be finished — its "
            "own `end` placed — before `Dog.new` runs, because until the "
            "class body has run there is no Dog to make. Three `end`s "
            "close three things here, and the last one closes the class."
        ),
        code=(
            "class Dog\n"
            "  attr_reader :name\n"
            "  def initialize(name)\n"
            "    @name = name\n"
            "  end\n"
            "  def speak\n"
            '    "#{name} says woof"\n'
            "  end\n"
            "end\n"
            'rex = Dog.new("Rex")\n'
            "puts rex.speak\n"
            "puts rex.name.upcase"
        ),
        expect="Rex says woof\nREX",
    ),
    _m(
        id="magnet-ruby-define-before-call",
        plan=(
            ("A method that shouts a word", 3),
            ("A method that greets using the shout", 3),
            ("Greet someone, then shout on its own", 2),
        ),
        level=2,
        name="A method exists once its def has run",
        family="Ruby",
        language="ruby",
        note=(
            "Ruby runs `def` like any other line: it defines the method "
            "at the moment it is reached. So both calls at the bottom "
            "have to come after both defs — move `puts greet` to the top "
            "and Ruby stops with a NoMethodError, because greet does not "
            "exist yet. The two defs can go either way round, though. "
            "`greet` only calls `shout` when greet itself is called, and "
            "by then both have been defined."
        ),
        code=(
            "def shout(word)\n"
            '  word.upcase + "!"\n'
            "end\n"
            "def greet(name)\n"
            '  shout("hi") + " " + name\n'
            "end\n"
            'puts greet("Ann")\n'
            'puts shout("bye")'
        ),
        expect="HI! Ann\nBYE!",
    ),
    _m(
        id="magnet-ruby-each-with-index",
        plan=(
            ("Start with the fruit and an empty list", 2),
            ("Number each long enough fruit", 4),
            ("Print the list and a count", 2),
        ),
        level=2,
        name="Numbering with each_with_index",
        family="Ruby",
        language="ruby",
        note=(
            "`each_with_index` hands the block each item and its "
            "position, counting from zero, so the label adds one. `next` "
            "inside a block skips to the next item, the way `continue` "
            "does in a loop — and it has to come before the `<<`, or the "
            "short fruit is added first and skipped after. The index "
            "still counts the skipped fig, which is why kiwi is number 3. "
            "`puts` given an array prints one line per element."
        ),
        code=(
            'fruits = ["apple", "fig", "kiwi"]\n'
            "lines = []\n"
            "fruits.each_with_index do |fruit, i|\n"
            "  next if fruit.size < 4\n"
            '  lines << "#{i + 1}. #{fruit}"\n'
            "end\n"
            "puts lines\n"
            'puts "#{lines.size} of #{fruits.size}"'
        ),
        expect="1. apple\n3. kiwi\n2 of 3",
    ),
    _m(
        id="magnet-ruby-yield",
        plan=(
            ("Start counting from nothing", 2),
            ("Count up and hand each number over", 4),
            ("Say how far it got", 2),
            ("Run it with a block and print the result", 2),
        ),
        level=3,
        name="A method that yields to its block",
        family="Ruby",
        language="ruby",
        note=(
            "`yield` runs the block the caller attached, handing it a "
            "value — here, once per trip round the loop. The count goes "
            "up before the yield, so the block sees 1, 2 and 3; swap "
            "those two lines and it sees 0, 1 and 2. The string on the "
            "method's last line is its return value, because Ruby "
            "returns the last expression, and the block's own puts lines "
            "all come out before it is printed."
        ),
        code=(
            "def repeat(times)\n"
            "  count = 0\n"
            "  while count < times\n"
            "    count += 1\n"
            "    yield count\n"
            "  end\n"
            '  "done #{count}"\n'
            "end\n"
            'result = repeat(3) { |n| puts "go #{n}" }\n'
            "puts result"
        ),
        expect="go 1\ngo 2\ngo 3\ndone 3",
    ),
    _m(
        id="magnet-ruby-hash-count",
        plan=(
            ("The words and a tally that starts at zero", 2),
            ("Count every word", 3),
            ("Print the tally, biggest first", 3),
            ("Say how many different words", 1),
        ),
        level=3,
        name="Counting into a hash",
        family="Ruby",
        language="ruby",
        note=(
            "`Hash.new(0)` makes a hash whose missing keys read as 0, so "
            "`counts[w] += 1` works the first time a word turns up. A "
            "plain `{}` would give nil there, and nil + 1 is an error. "
            "The tally has to be complete before it is sorted and "
            "printed — put the printing loop above the counting one and "
            "it walks an empty hash. `sort_by` on a hash yields each key "
            "and value as a pair, and the minus sorts biggest first."
        ),
        code=(
            "words = %w[red blue red green blue red]\n"
            "counts = Hash.new(0)\n"
            "words.each do |w|\n"
            "  counts[w] += 1\n"
            "end\n"
            "counts.sort_by { |w, n| -n }.each do |w, n|\n"
            '  puts "#{w}: #{n}"\n'
            "end\n"
            "puts counts.size"
        ),
        expect="red: 3\nblue: 2\ngreen: 1\n3",
    ),
    _m(
        id="magnet-ruby-rescue-ensure",
        plan=(
            ("Start a method that reads a number", 2),
            ("Try to read it and report it", 2),
            ("Say so if it was not a number", 2),
            ("Always say it was checked", 2),
            ("Close the attempt and the method", 2),
            ("Try one good and one bad", 2),
        ),
        level=4,
        name="begin, rescue and ensure",
        family="Ruby",
        language="ruby",
        note=(
            "`Integer(text)` raises an ArgumentError for anything that "
            "is not a whole number, and the raise jumps straight to the "
            "matching `rescue` — the line after it in the begin block is "
            "skipped, which is why \"got\" never appears for 4x. `ensure` "
            "runs either way, after whichever of the two ran. The order "
            "is fixed: begin, then rescue, then ensure, then end; a "
            "rescue after the ensure does not parse."
        ),
        code=(
            "def parse(text)\n"
            "  begin\n"
            "    value = Integer(text)\n"
            '    puts "got #{value}"\n'
            "  rescue ArgumentError\n"
            '    puts "not a number: #{text}"\n'
            "  ensure\n"
            '    puts "checked #{text}"\n'
            "  end\n"
            "end\n"
            'parse("42")\n'
            'parse("4x")'
        ),
        expect="got 42\nchecked 42\nnot a number: 4x\nchecked 4x",
    ),
)
