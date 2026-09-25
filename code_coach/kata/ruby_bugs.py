"""Fix the bug, in Ruby: the method is written, and it is wrong.

The same exercise as the Python and Dart families, with Ruby's own traps
rather than theirs translated:

  the whole-number divide  `7 / 2` is 3 when both sides are Integers
  the three-dot range      `1...n` stops before n
  each, not map            `each` hands back the receiver, not the results
  zero is true             only nil and false are falsy, so 0 passes an if
  the bang method          `map!` rewrites the caller's array in place
  or-equals and false      `||=` replaces false as well as nil

Each one runs without a syntax error, because a start that does not
parse teaches the parser rather than the bug. And each one passes some
of its cases, because that is what makes a bug hard to see: it is right
on the inputs you thought of and wrong on the ones you did not.

The oracle is Python, as for every kata; the fixed code is kept in
`RUBY_BUG_ANSWERS` by kata id. The note in `bug` is shown once it passes.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Fix the bug: Ruby"


def _average_rating(ratings: list) -> float:
    if not ratings:
        return 0.0
    return sum(ratings) / len(ratings)


def _squares_up_to(n: int) -> list:
    return [i * i for i in range(1, n + 1)]


def _double_each(nums: list) -> list:
    return [n * 2 for n in nums]


def _stock_status(counts: dict, item: str) -> str:
    return "in stock" if counts.get(item, 0) > 0 else "sold out"


def _shout_all(words: list) -> list:
    return [word.upper() for word in words]


def _with_defaults(prefs: dict) -> dict:
    return {"sound": True, "volume": 5, **prefs}


RUBY_BUGS: tuple[Kata, ...] = (
    Kata(
        id="rb-bug-average-rating",
        level=1,
        language="ruby",
        family=FAMILY,
        name="average_rating",
        brief=(
            "Return the mean of the ratings as a Float - 3.5 for [3, 4] - "
            "or 0.0 when there are none."
        ),
        params=("ratings",),
        example="average_rating([3, 4]) is 3.5",
        hint="Try [3, 4]. What is 7 / 2 in Ruby when both sides are Integers?",
        start="""\
def average_rating(ratings)
  return 0.0 if ratings.empty?

  ratings.sum / ratings.size
end
""",
        bug=(
            "Integer / Integer is whole-number division in Ruby: 7 / 2 is "
            "3, with the half thrown away. It only showed when the mean was "
            "not whole. fdiv (or to_f on either side) divides as Floats."
        ),
        cases=(([3, 4],), ([],), ([5],), ([4, 4],), ([1, 2, 2],), ([5, 4, 3, 2],),
               ([2, 4, 6],)),
        solve=_average_rating,
        checks=((([3, 4],), 3.5), (([],), 0.0), (([5],), 5.0),
                (([5, 4, 3, 2],), 3.5)),
    ),
    Kata(
        id="rb-bug-squares-up-to",
        level=1,
        language="ruby",
        family=FAMILY,
        name="squares_up_to",
        brief=(
            "Return the squares of 1, 2, ... n, in order, n included. For n "
            "below 1 there are none."
        ),
        params=("n",),
        example="squares_up_to(3) is [1, 4, 9]",
        hint="squares_up_to(1) should be [1]. What does (1...1) contain?",
        start="""\
def squares_up_to(n)
  (1...n).map { |i| i * i }
end
""",
        bug=(
            "Three dots make an exclusive range: 1...n stops at n - 1. Two "
            "dots, 1..n, include the end. Both are empty when n is below 1, "
            "which is why those cases passed."
        ),
        cases=((3,), (0,), (1,), (-2,), (5,), (2,)),
        solve=_squares_up_to,
        checks=(((3,), [1, 4, 9]), ((0,), []), ((1,), [1]), ((-2,), [])),
    ),
    Kata(
        id="rb-bug-double-each",
        level=2,
        language="ruby",
        family=FAMILY,
        name="double_each",
        brief="Return a new array with every number in nums doubled.",
        params=("nums",),
        example="double_each([1, 5]) is [2, 10]",
        hint="What does each return when the block is done?",
        start="""\
def double_each(nums)
  nums.each { |n| n * 2 }
end
""",
        bug=(
            "each runs the block for its side effects and returns the "
            "array it was called on, so the doubled values were computed "
            "and thrown away. map collects what the block returns. It "
            "looked right only where doubling changes nothing: [] and 0."
        ),
        cases=(([1, 5],), ([],), ([0],), ([-3, 4],), ([0, 0],), ([10, 20, 30],)),
        solve=_double_each,
        checks=((([1, 5],), [2, 10]), (([],), []), (([-3, 4],), [-6, 8])),
    ),
    Kata(
        id="rb-bug-stock-status",
        level=2,
        language="ruby",
        family=FAMILY,
        name="stock_status",
        brief=(
            "counts is a hash from item name to how many are left. Return "
            "\"in stock\" when there is at least one of item, otherwise "
            "\"sold out\" - including when item is not in the hash at all."
        ),
        params=("counts", "item"),
        example='stock_status({"pen" => 0}, "pen") is "sold out"',
        hint="Which values are false in an if in Ruby? Is 0 one of them?",
        start="""\
def stock_status(counts, item)
  counts[item] ? "in stock" : "sold out"
end
""",
        bug=(
            "In Ruby only nil and false are falsy - 0 is true. So a count "
            "of 0 read as in stock; only a missing key (nil) read as sold "
            "out. Compare the number: counts.fetch(item, 0) > 0."
        ),
        cases=(({"pen": 0}, "pen"), ({}, "pen"), ({"pen": 3}, "pen"),
               ({"pen": 3}, "ink"), ({"ink": 0, "pen": 1}, "ink"),
               ({"cup": 12}, "cup")),
        solve=_stock_status,
        checks=((({"pen": 0}, "pen"), "sold out"), (({}, "pen"), "sold out"),
                (({"pen": 3}, "pen"), "in stock")),
    ),
    Kata(
        id="rb-bug-shout-all",
        level=2,
        language="ruby",
        family=FAMILY,
        name="shout_all",
        brief=(
            "Return the words in capitals, in a new array. The array you "
            "were given must not change."
        ),
        params=("words",),
        example='shout_all(["hi", "you"]) is ["HI", "YOU"]',
        hint="The answer comes back right. Look at what happened to words.",
        start="""\
def shout_all(words)
  words.map!(&:upcase)
end
""",
        bug=(
            "A method ending in ! changes its receiver: map! overwrote the "
            "caller's array with the capitalised words. The return value "
            "was right, and the damage was somewhere else. It only passed "
            "where there was nothing to change. map returns a new array."
        ),
        cases=((["hi", "you"],), ([],), (["OK"],), (["a"],), (["Mixed", "CASE"],)),
        solve=_shout_all,
        checks=(((["hi", "you"],), ["HI", "YOU"]), (([],), []), ((["a"],), ["A"])),
    ),
    Kata(
        id="rb-bug-with-defaults",
        level=3,
        language="ruby",
        family=FAMILY,
        name="with_defaults",
        brief=(
            "Return a new hash of settings: everything in prefs, plus "
            "\"sound\" => true and \"volume\" => 5 for whichever of those two "
            "is missing. A setting that is present keeps its value, even "
            "false or 0."
        ),
        params=("prefs",),
        example='with_defaults({"sound" => false}) is {"sound" => false, "volume" => 5}',
        hint="Try {\"sound\" => false}. When does ||= decide to assign?",
        start="""\
def with_defaults(prefs)
  out = prefs.dup
  out["sound"] ||= true
  out["volume"] ||= 5
  out
end
""",
        bug=(
            "a ||= b assigns whenever a is falsy, and false is falsy - so a "
            "player who turned the sound off had it turned back on. Volume "
            "0 survived only because 0 is true in Ruby. Merge the prefs "
            "over the defaults, or test with key? instead."
        ),
        cases=(({"sound": False},), ({},), ({"sound": True, "volume": 2},),
               ({"volume": 0},), ({"sound": False, "volume": 0},),
               ({"theme": "dark"},)),
        solve=_with_defaults,
        checks=((({"sound": False},), {"sound": False, "volume": 5}),
                (({},), {"sound": True, "volume": 5}),
                (({"volume": 0},), {"sound": True, "volume": 0})),
    ),
)


#: The fixed method for each broken one, by id: the smallest change to
#: the start that makes it right.
RUBY_BUG_ANSWERS: dict[str, str] = {
    "rb-bug-average-rating": """\
def average_rating(ratings)
  return 0.0 if ratings.empty?

  ratings.sum.fdiv(ratings.size)
end
""",
    "rb-bug-squares-up-to": """\
def squares_up_to(n)
  (1..n).map { |i| i * i }
end
""",
    "rb-bug-double-each": """\
def double_each(nums)
  nums.map { |n| n * 2 }
end
""",
    "rb-bug-stock-status": """\
def stock_status(counts, item)
  counts.fetch(item, 0) > 0 ? "in stock" : "sold out"
end
""",
    "rb-bug-shout-all": """\
def shout_all(words)
  words.map(&:upcase)
end
""",
    "rb-bug-with-defaults": """\
def with_defaults(prefs)
  { "sound" => true, "volume" => 5 }.merge(prefs)
end
""",
}
