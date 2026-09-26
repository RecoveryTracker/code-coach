"""Katas in Ruby: the Enumerable way of saying things.

Ruby's reputation is that the obvious loop is almost never the code you
should write. Nearly every small job on a collection has a method named
for it - `tally` counts, `group_by` buckets, `each_slice` chunks,
`minmax` finds both ends in one pass, `sort_by` with an array sorts on
one thing and breaks ties on another - and learning those names is most
of learning to read Ruby written by somebody else.

The oracle is Python, as for every kata: the answers are numbers,
strings, arrays, hashes and booleans, which mean the same in both. What
is Ruby is the worked answer, kept in `RUBY_ANSWERS` by kata id, and the
suite runs every one of them through the Ruby driver against the oracle.

One thing to keep in mind throughout: the inputs arrive as JSON, so a
hash always has string keys - `config["db"]`, never `config[:db]`. A
symbol and a string with the same letters are different keys in Ruby,
and looking one up with the other quietly gives nil.

Nothing here may change what it was handed. The driver compares the
arguments before and after, so `map!`, `sort!` and friends fail the case
even when the value returned is right.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Ruby"


def _acronym_of(phrase: str) -> str:
    return "".join(word[0].upper() for word in phrase.split())


def _sum_of_range(first: int, last: int) -> int:
    return sum(range(first, last + 1))


def _letter_tally(text: str) -> dict:
    counts: dict = {}
    for ch in text.lower():
        if "a" <= ch <= "z":
            counts[ch] = counts.get(ch, 0) + 1
    return counts


def _min_max_spread(nums: list):
    if not nums:
        return None
    return max(nums) - min(nums)


def _chunk_sums(nums: list, size: int) -> list:
    return [sum(nums[i:i + size]) for i in range(0, len(nums), size)]


def _dot_product(xs: list, ys: list) -> int:
    return sum(x * y for x, y in zip(xs, ys))


def _group_by_first(words: list) -> dict:
    groups: dict = {}
    for word in words:
        groups.setdefault(word[0].lower(), []).append(word)
    return groups


def _nested_setting(config: dict, section: str, key: str):
    part = config.get(section)
    value = part.get(key) if part is not None else None
    return "unset" if value is None else value


def _money_label(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    whole, part = divmod(abs(cents), 100)
    return f"{sign}${whole}.{part:02d}"


def _rank_players(scores: dict) -> list:
    return sorted(scores, key=lambda name: (-scores[name], name))


RUBY_KATAS: tuple[Kata, ...] = (
    Kata(
        id="rb-acronym-of",
        level=1,
        language="ruby",
        family=FAMILY,
        name="acronym_of",
        brief=(
            "Return the first letter of every word in phrase, capitalised "
            "and run together. Words are separated by any amount of "
            "whitespace; a phrase with no words gives an empty string."
        ),
        params=("phrase",),
        example='acronym_of("as soon as possible") is "ASAP"',
        hint=(
            "split with no argument splits on runs of whitespace and drops "
            "the empty pieces. Then map each word to one letter, and join."
        ),
        cases=(
            ("as soon as possible",), ("",), ("   ",), ("ruby",),
            ("  portable   network graphics ",), ("Hyper Text markup Language",),
            ("a b c",),
        ),
        solve=_acronym_of,
        checks=((("as soon as possible",), "ASAP"), (("",), ""),
                (("  portable   network graphics ",), "PNG")),
    ),
    Kata(
        id="rb-sum-of-range",
        level=1,
        language="ruby",
        family=FAMILY,
        name="sum_of_range",
        brief=(
            "Return the sum of every whole number from first to last, both "
            "included. If first is bigger than last there are no numbers, "
            "and the sum is 0."
        ),
        params=("first", "last"),
        example="sum_of_range(1, 4) is 10",
        hint=(
            "(first..last) is a Range, and a Range is Enumerable - it has "
            "sum. Two dots include the end; three leave it out."
        ),
        cases=((1, 4), (0, 0), (5, 5), (3, 1), (-2, 2), (-5, -1), (1, 100)),
        solve=_sum_of_range,
        checks=(((1, 4), 10), ((3, 1), 0), ((-2, 2), 0), ((1, 100), 5050)),
    ),
    Kata(
        id="rb-letter-tally",
        level=2,
        language="ruby",
        family=FAMILY,
        name="letter_tally",
        brief=(
            "Return a hash from each letter a-z in text to how many times "
            "it appears, ignoring case. Anything that is not a letter is "
            "not counted."
        ),
        params=("text",),
        example='letter_tally("Aha!") is {"a" => 2, "h" => 1}',
        hint=(
            "downcase, pick out the letters (scan with /[a-z]/ does it in "
            "one go), and tally turns an array into a hash of counts."
        ),
        cases=(("Aha!",), ("",), ("123 !?",), ("x",), ("Mississippi",),
               ("Hello, World",)),
        solve=_letter_tally,
        checks=((("Aha!",), {"a": 2, "h": 1}), (("",), {}),
                (("Mississippi",), {"m": 1, "i": 4, "s": 4, "p": 2})),
    ),
    Kata(
        id="rb-min-max-spread",
        level=2,
        language="ruby",
        family=FAMILY,
        name="min_max_spread",
        brief=(
            "Return the largest number in nums minus the smallest, or nil "
            "when nums is empty."
        ),
        params=("nums",),
        example="min_max_spread([4, 9, 1]) is 8",
        hint=(
            "minmax hands back [smallest, largest] in one pass, and you can "
            "take them apart with lo, hi = ... . On an empty array it gives "
            "[nil, nil], so decide about that first."
        ),
        cases=(([4, 9, 1],), ([],), ([7],), ([-3, -8, -1],), ([5, 5, 5],),
               ([-10, 10],)),
        solve=_min_max_spread,
        checks=((([4, 9, 1],), 8), (([],), None), (([7],), 0),
                (([-3, -8, -1],), 7)),
    ),
    Kata(
        id="rb-chunk-sums",
        level=2,
        language="ruby",
        family=FAMILY,
        name="chunk_sums",
        brief=(
            "Split nums into consecutive groups of size (the last group "
            "may be shorter) and return the sum of each group."
        ),
        params=("nums", "size"),
        example="chunk_sums([1, 2, 3, 4, 5], 2) is [3, 7, 5]",
        hint="each_slice(size) walks the array a group at a time; map each group to its sum.",
        cases=(([1, 2, 3, 4, 5], 2), ([], 3), ([9], 4), ([1, 2, 3], 1),
               ([-1, 1, -2, 2], 2), ([4, 4, 4, 4, 4, 4], 3)),
        solve=_chunk_sums,
        checks=((([1, 2, 3, 4, 5], 2), [3, 7, 5]), (([], 3), []),
                (([9], 4), [9]), (([-1, 1, -2, 2], 2), [0, 0])),
    ),
    Kata(
        id="rb-dot-product",
        level=2,
        language="ruby",
        family=FAMILY,
        name="dot_product",
        brief=(
            "xs and ys are the same length. Multiply them pair by pair - "
            "first with first, second with second - and return the total."
        ),
        params=("xs", "ys"),
        example="dot_product([1, 2, 3], [4, 5, 6]) is 32",
        hint=(
            "zip pairs them up. inject(0) { |total, (x, y)| ... } folds the "
            "pairs into one number - the brackets take each pair apart."
        ),
        cases=(([1, 2, 3], [4, 5, 6]), ([], []), ([7], [3]), ([2, -1], [3, 5]),
               ([0, 0, 0], [9, 9, 9]), ([-2, -3], [-4, -5])),
        solve=_dot_product,
        checks=((([1, 2, 3], [4, 5, 6]), 32), (([], []), 0),
                (([2, -1], [3, 5]), 1), (([-2, -3], [-4, -5]), 23)),
    ),
    Kata(
        id="rb-group-by-first",
        level=3,
        language="ruby",
        family=FAMILY,
        name="group_by_first",
        brief=(
            "Return a hash from each lowercase first letter to the words "
            "that start with it, in the order they came. Every word has at "
            "least one character."
        ),
        params=("words",),
        example='group_by_first(["ant", "Bee", "ape"]) is {"a" => ["ant", "ape"], "b" => ["Bee"]}',
        hint=(
            "group_by takes a block that returns the key for each item, and "
            "does the bucketing for you. The words keep their own case; only "
            "the key is lowercased."
        ),
        cases=((["ant", "Bee", "ape"],), ([],), (["solo"],),
               (["Cat", "cow", "Crab", "dog"],), (["x", "y", "x"],)),
        solve=_group_by_first,
        checks=(((["ant", "Bee", "ape"],), {"a": ["ant", "ape"], "b": ["Bee"]}),
                (([],), {}), ((["solo"],), {"s": ["solo"]})),
    ),
    Kata(
        id="rb-nested-setting",
        level=3,
        language="ruby",
        family=FAMILY,
        name="nested_setting",
        brief=(
            "config is a hash of sections, each a hash of settings. Return "
            "config[section][key], or \"unset\" when the section or the key "
            "is missing or the value is nil. An empty string is a real "
            "value and comes back as it is."
        ),
        params=("config", "section", "key"),
        example='nested_setting({"db" => {"host" => "local"}}, "db", "host") is "local"',
        hint=(
            "config[section] may be nil, and nil[key] raises. &. calls the "
            "method only when the receiver is not nil. Then || supplies the "
            "default - and in Ruby only nil and false are falsy, so \"\" "
            "survives it. The keys are strings, not symbols."
        ),
        cases=(
            ({"db": {"host": "local"}}, "db", "host"),
            ({}, "db", "host"),
            ({"db": {}}, "db", "host"),
            ({"db": {"host": "local"}}, "web", "host"),
            ({"db": {"host": None}}, "db", "host"),
            ({"web": {"path": ""}}, "web", "path"),
            ({"db": {"port": "5432"}, "web": {"port": "80"}}, "web", "port"),
        ),
        solve=_nested_setting,
        checks=((({"db": {"host": "local"}}, "db", "host"), "local"),
                (({}, "db", "host"), "unset"),
                (({"web": {"path": ""}}, "web", "path"), ""),
                (({"db": {"host": None}}, "db", "host"), "unset")),
    ),
    Kata(
        id="rb-money-label",
        level=3,
        language="ruby",
        family=FAMILY,
        name="money_label",
        brief=(
            "cents is an amount of money in cents. Return it as dollars "
            "with exactly two decimal places, like \"$12.05\", with a minus "
            "sign in front of the dollar sign when it is negative."
        ),
        params=("cents",),
        example='money_label(1205) is "$12.05", money_label(-50) is "-$0.50"',
        hint=(
            "divmod(100) gives dollars and cents together - but do it on the "
            "absolute value, or -50 comes out wrong. format(\"%d.%02d\", ...) "
            "pads the cents to two digits."
        ),
        cases=((1205,), (0,), (5,), (-50,), (100,), (-123456,), (99,)),
        solve=_money_label,
        checks=(((1205,), "$12.05"), ((0,), "$0.00"), ((-50,), "-$0.50"),
                ((-123456,), "-$1234.56")),
    ),
    Kata(
        id="rb-rank-players",
        level=4,
        language="ruby",
        family=FAMILY,
        name="rank_players",
        brief=(
            "scores is a hash from player name to score. Return the names "
            "from highest score to lowest; players on the same score go in "
            "alphabetical order."
        ),
        params=("scores",),
        example='rank_players({"cy" => 3, "al" => 5, "bo" => 3}) is ["al", "bo", "cy"]',
        hint=(
            "sort_by can return an array, and arrays compare element by "
            "element - so [-score, name] sorts by score descending and then "
            "by name. A hash yields |name, score| pairs; map(&:first) keeps "
            "the names."
        ),
        cases=(({"cy": 3, "al": 5, "bo": 3},), ({},), ({"solo": 1},),
               ({"b": -1, "a": -1, "c": 0},), ({"zed": 10, "amy": 2, "kim": 7},),
               ({"dee": 4, "eve": 1, "cal": 4, "ann": 4, "bob": 4},),
               ({"zed": 2, "yan": 2, "xia": 2},)),
        solve=_rank_players,
        checks=((({"cy": 3, "al": 5, "bo": 3},), ["al", "bo", "cy"]),
                (({},), []), (({"b": -1, "a": -1, "c": 0},), ["c", "a", "b"]),
                (({"zed": 2, "yan": 2, "xia": 2},), ["xia", "yan", "zed"])),
    ),
)


#: The worked answer for each kata, by id. Idiomatic rather than merely
#: correct: each is the one-liner (or near it) that the kata is there to
#: teach.
RUBY_ANSWERS: dict[str, str] = {
    "rb-acronym-of": """\
def acronym_of(phrase)
  phrase.split.map { |word| word[0].upcase }.join
end
""",
    "rb-sum-of-range": """\
def sum_of_range(first, last)
  (first..last).sum
end
""",
    "rb-letter-tally": """\
def letter_tally(text)
  text.downcase.scan(/[a-z]/).tally
end
""",
    "rb-min-max-spread": """\
def min_max_spread(nums)
  return nil if nums.empty?

  lo, hi = nums.minmax
  hi - lo
end
""",
    "rb-chunk-sums": """\
def chunk_sums(nums, size)
  nums.each_slice(size).map(&:sum)
end
""",
    "rb-dot-product": """\
def dot_product(xs, ys)
  xs.zip(ys).inject(0) { |total, (x, y)| total + x * y }
end
""",
    "rb-group-by-first": """\
def group_by_first(words)
  words.group_by { |word| word[0].downcase }
end
""",
    "rb-nested-setting": """\
def nested_setting(config, section, key)
  config[section]&.fetch(key, nil) || "unset"
end
""",
    "rb-money-label": """\
def money_label(cents)
  dollars, rest = cents.abs.divmod(100)
  sign = cents.negative? ? "-" : ""
  format("%s$%d.%02d", sign, dollars, rest)
end
""",
    "rb-rank-players": """\
def rank_players(scores)
  scores.sort_by { |name, score| [-score, name] }.map(&:first)
end
""",
}


def _with_answers():
    from dataclasses import replace

    return tuple(replace(k, ruby_answer=RUBY_ANSWERS[k.id]) for k in RUBY_KATAS)


RUBY_KATAS = _with_answers()
