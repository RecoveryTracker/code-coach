"""Ruby bug hunts.

Six mistakes that are Ruby's own, each one a habit carried over from
another language or a method that does something slightly different
from what its name suggests:

  0 is truthy        only nil and false are false, so a zero count
                     reads as "in stock"
  each               hands back the array it was called on, not the
                     values the block worked out
  whole numbers      3 / 4 is 0 in Ruby, so a percentage worked out
                     part / whole * 100 is 0 until it is 100
  1...n              three dots leave the last number out
  sort!              sorts the caller's array in place, so asking for
                     a ranking reorders the scores you passed in
  Hash.new([])       every missing key shares that one array, and <<
                     on it never stores a key at all

In every one the report is about the method you call and the cause is
in a helper above it. The same rules hold as for the other hunts, and
tests/test_bughunt_ruby.py checks them: the bug is real, it hides on
some inputs, the report's own input shows it, and the fix changes one
line in place.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

RUBY = "Ruby"


def _shelf_labels(inventory: dict, items: list) -> list:
    return [
        f"{item}: in stock" if (inventory.get(item) or 0) > 0
        else f"{item}: sold out"
        for item in items
    ]


def _team_code(names: list) -> str:
    return "".join(name[0].upper() for name in names)


def _progress(done: int, total: int) -> str:
    percent = 0 if total == 0 else done * 100 // total
    return f"{percent}% done"


def _pagination(total_items: int, per_page: int) -> str:
    pages = (total_items + per_page - 1) // per_page
    return " | ".join(f"Page {n}" for n in range(1, pages + 1))


def _podium(scores: list) -> list:
    return sorted(scores, reverse=True)[:3]


def _index_lines(words: list) -> list:
    groups: dict = {}
    for word in words:
        groups.setdefault(word[0], []).append(word)
    return [f"{k}: {', '.join(groups[k])}" for k in sorted(groups)]


RUBY_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-rb-zero-in-stock",
        title="Sold out, but in stock",
        family=RUBY,
        language="ruby",
        level=1,
        report="The shelf says 'kettle: in stock', but we sold the last "
               "kettle this morning and the count is 0. Items we never "
               "carried correctly say sold out.",
        name="shelf_labels",
        params=("inventory", "items"),
        start=(
            "# How many are left, or nil if the shop never stocked it.\n"
            "def left(inventory, item)\n"
            "  inventory[item]\n"
            "end\n"
            "\n"
            "def available?(inventory, item)\n"
            "  left(inventory, item) ? true : false\n"
            "end\n"
            "\n"
            "def shelf_labels(inventory, items)\n"
            "  items.map do |item|\n"
            "    available?(inventory, item) ? \"#{item}: in stock\" : \"#{item}: sold out\"\n"
            "  end\n"
            "end\n"
        ),
        fixed=(
            "# How many are left, or nil if the shop never stocked it.\n"
            "def left(inventory, item)\n"
            "  inventory[item]\n"
            "end\n"
            "\n"
            "def available?(inventory, item)\n"
            "  left(inventory, item).to_i > 0\n"
            "end\n"
            "\n"
            "def shelf_labels(inventory, items)\n"
            "  items.map do |item|\n"
            "    available?(inventory, item) ? \"#{item}: in stock\" : \"#{item}: sold out\"\n"
            "  end\n"
            "end\n"
        ),
        solve=_shelf_labels,
        reported=({"kettle": 0, "mug": 4}, ["kettle", "mug"]),
        cases=(
            ({"mug": 4}, ["mug"]),
            ({"kettle": 0, "mug": 4}, ["kettle", "mug"]),
            ({"mug": 4}, ["teapot"]),
            ({"cup": 0}, ["cup"]),
            ({"cup": 2, "saucer": 7}, ["saucer", "cup"]),
            ({}, []),
        ),
        cause="In Ruby only nil and false are false. A count of 0 is "
              "truthy, so the helper answers true for it.",
        decoys=(
            "inventory[item] raises an error for an item that is not in "
            "the hash, so the sold-out branch never runs.",
            "The ternary in shelf_labels has its two labels the wrong way "
            "round.",
            "The keys arrive as strings but are looked up as symbols.",
        ),
        lesson="Coming from Python or JavaScript, 0 looks false. In Ruby "
               "it is not: only nil and false are. When a number decides "
               "a yes or no, say the comparison out loud - count > 0 - "
               "rather than leaning on truthiness.",
        hint="The report's shelf: kettle at 0, mug at 4. Then try an item "
             "the shop does not carry at all.",
        checks=(
            (({"kettle": 0, "mug": 4}, ["kettle", "mug"]),
             ["kettle: sold out", "mug: in stock"]),
            (({"mug": 4}, ["teapot"]), ["teapot: sold out"]),
            (({"mug": 4}, ["mug"]), ["mug: in stock"]),
        ),
    ),
    Hunt(
        id="hunt-rb-each-not-map",
        title="The team code is everyone's name",
        family=RUBY,
        language="ruby",
        level=1,
        report="The team code for ada, lin and grace came out as "
               "'adalingrace'. It should be 'ALG'. A one-person team "
               "called 'Q' got 'Q', which is right.",
        name="team_code",
        params=("names",),
        start=(
            "SEPARATOR = \"\"\n"
            "\n"
            "def initials(names)\n"
            "  names.each { |name| name[0].upcase }\n"
            "end\n"
            "\n"
            "def team_code(names)\n"
            "  initials(names).join(SEPARATOR)\n"
            "end\n"
        ),
        fixed=(
            "SEPARATOR = \"\"\n"
            "\n"
            "def initials(names)\n"
            "  names.map { |name| name[0].upcase }\n"
            "end\n"
            "\n"
            "def team_code(names)\n"
            "  initials(names).join(SEPARATOR)\n"
            "end\n"
        ),
        solve=_team_code,
        reported=(["ada", "lin", "grace"],),
        cases=((["Q"],), (["ada", "lin", "grace"],), ([],),
               (["Bo"],), (["X", "Y"],), (["mo", "Al"],)),
        cause="each runs the block but hands back the array it was called "
              "on, so the upcased initials are thrown away and the full "
              "names are joined.",
        decoys=(
            "name[0] is the whole name in Ruby, not its first letter.",
            "upcase changes the name in place, so the names themselves "
            "become capitals.",
            "join with an empty string joins nothing and returns the "
            "array unchanged.",
        ),
        lesson="each is for doing something with every item; its answer "
               "is the collection you started with. When you want the "
               "block's answers back, that is map. If a method ends in "
               "each, its return value is almost never what you meant.",
        hint="The report's team: team_code([\"ada\", \"lin\", \"grace\"]). "
             "Then a team whose names are already single capitals.",
        checks=(
            ((["ada", "lin", "grace"],), "ALG"),
            ((["Q"],), "Q"),
            (([],), ""),
            ((["mo", "Al"],), "MA"),
        ),
    ),
    Hunt(
        id="hunt-rb-whole-percent",
        title="Stuck at 0%",
        family=RUBY,
        language="ruby",
        level=2,
        report="The upload bar sat at '0% done' for 3 of 4 files and "
               "then jumped straight to '100% done'. An empty upload "
               "correctly shows 0%.",
        name="progress",
        params=("done", "total"),
        start=(
            "def percent(part, whole)\n"
            "  return 0 if whole.zero?\n"
            "\n"
            "  part / whole * 100\n"
            "end\n"
            "\n"
            "def progress(done, total)\n"
            "  \"#{percent(done, total)}% done\"\n"
            "end\n"
        ),
        fixed=(
            "def percent(part, whole)\n"
            "  return 0 if whole.zero?\n"
            "\n"
            "  part * 100 / whole\n"
            "end\n"
            "\n"
            "def progress(done, total)\n"
            "  \"#{percent(done, total)}% done\"\n"
            "end\n"
        ),
        solve=_progress,
        reported=(3, 4),
        cases=((0, 4), (3, 4), (4, 4), (0, 0), (1, 3), (5, 10), (9, 9)),
        cause="Both numbers are Integers, so part / whole is whole-number "
              "division: 3 / 4 is 0, and 0 * 100 is still 0.",
        decoys=(
            "whole.zero? is true for any number below 1, so the early "
            "return fires.",
            "Interpolating a number into a string rounds it down to the "
            "nearest ten.",
            "The * runs before the /, so it works out 4 * 100 first.",
        ),
        lesson="Integer divided by Integer is an Integer in Ruby - the "
               "fraction is dropped, not rounded. Multiply before you "
               "divide, or make one side a Float with to_f, whenever the "
               "answer should be a share of something.",
        hint="The report's upload: progress(3, 4). Then one that is "
             "finished.",
        checks=(((3, 4), "75% done"), ((0, 0), "0% done"),
                ((4, 4), "100% done"), ((1, 3), "33% done")),
    ),
    Hunt(
        id="hunt-rb-missing-last-page",
        title="The last page has no link",
        family=RUBY,
        language="ruby",
        level=2,
        report="25 results at 10 a page shows links for Page 1 and Page "
               "2, but there are three pages. With 5 results there is "
               "no link at all.",
        name="pagination",
        params=("total_items", "per_page"),
        start=(
            "def page_count(total_items, per_page)\n"
            "  (total_items + per_page - 1) / per_page\n"
            "end\n"
            "\n"
            "def page_numbers(count)\n"
            "  (1...count).to_a\n"
            "end\n"
            "\n"
            "def pagination(total_items, per_page)\n"
            "  pages = page_numbers(page_count(total_items, per_page))\n"
            "  pages.map { |n| \"Page #{n}\" }.join(\" | \")\n"
            "end\n"
        ),
        fixed=(
            "def page_count(total_items, per_page)\n"
            "  (total_items + per_page - 1) / per_page\n"
            "end\n"
            "\n"
            "def page_numbers(count)\n"
            "  (1..count).to_a\n"
            "end\n"
            "\n"
            "def pagination(total_items, per_page)\n"
            "  pages = page_numbers(page_count(total_items, per_page))\n"
            "  pages.map { |n| \"Page #{n}\" }.join(\" | \")\n"
            "end\n"
        ),
        solve=_pagination,
        reported=(25, 10),
        cases=((0, 10), (25, 10), (5, 10), (20, 10), (0, 3), (7, 2)),
        cause="1...count has three dots, which leaves count itself out, "
              "so the last page is never listed.",
        decoys=(
            "page_count rounds down, so 25 items at 10 a page counts as "
            "two pages.",
            "Ruby ranges start at 0, so the numbering is shifted by one.",
            "to_a turns the range into an array one shorter than the "
            "range.",
        ),
        lesson="Two dots include the end, three dots stop just before "
               "it: 1..3 is 1, 2, 3 and 1...3 is 1, 2. The extra dot is "
               "easy to miss when reading, so check the last value of any "
               "range against the case at the edge.",
        hint="The report's search: pagination(25, 10). Then try one "
             "page's worth, and none at all.",
        checks=(((25, 10), "Page 1 | Page 2 | Page 3"), ((5, 10), "Page 1"),
                ((0, 10), ""), ((7, 2), "Page 1 | Page 2 | Page 3 | Page 4")),
    ),
    Hunt(
        id="hunt-rb-sort-bang",
        title="The podium reorders the scoreboard",
        family=RUBY,
        language="ruby",
        level=3,
        report="After showing the podium for scores [40, 90, 70, 85], "
               "the scoreboard listed them in a different order from the "
               "one they were entered in. The podium itself is right.",
        name="podium",
        params=("scores",),
        start=(
            "PLACES = 3\n"
            "\n"
            "def ranked(scores)\n"
            "  scores.sort!.reverse\n"
            "end\n"
            "\n"
            "def podium(scores)\n"
            "  ranked(scores).first(PLACES)\n"
            "end\n"
        ),
        fixed=(
            "PLACES = 3\n"
            "\n"
            "def ranked(scores)\n"
            "  scores.sort.reverse\n"
            "end\n"
            "\n"
            "def podium(scores)\n"
            "  ranked(scores).first(PLACES)\n"
            "end\n"
        ),
        solve=_podium,
        reported=([40, 90, 70, 85],),
        cases=(([10, 20, 30],), ([40, 90, 70, 85],), ([],), ([5],),
               ([3, 1, 2],), ([1, 2, 3, 4],)),
        cause="sort! sorts the array it is called on, which is the "
              "caller's scores, instead of making a sorted copy.",
        decoys=(
            "reverse also reverses the caller's array, so the scores end "
            "up backwards.",
            "first(PLACES) removes the top three from the scores it was "
            "given.",
            "sort! returns nil when nothing moves, so the podium is "
            "empty for some inputs.",
        ),
        lesson="A ! on a Ruby method usually means it changes the thing "
               "it is called on. A helper handed someone else's array "
               "should use the plain version - sort, map, uniq - and "
               "leave the caller's data as it found it.",
        hint="The answer is right; the bug is what happens to the "
             "argument. Try the report's scores, then some already in "
             "order.",
        checks=(
            (([40, 90, 70, 85],), [90, 85, 70]),
            (([10, 20, 30],), [30, 20, 10]),
            (([],), []),
            (([5],), [5]),
        ),
    ),
    Hunt(
        id="hunt-rb-shared-default",
        title="An index with nothing in it",
        family=RUBY,
        language="ruby",
        level=3,
        report="The glossary index for apple, avocado and banana came "
               "out completely empty. It should have an 'a' line and a "
               "'b' line.",
        name="index_lines",
        params=("words",),
        start=(
            "def by_letter(words)\n"
            "  groups = Hash.new([])\n"
            "  words.each { |word| groups[word[0]] << word }\n"
            "  groups\n"
            "end\n"
            "\n"
            "def index_lines(words)\n"
            "  groups = by_letter(words)\n"
            "  groups.keys.sort.map { |k| \"#{k}: #{groups[k].join(\", \")}\" }\n"
            "end\n"
        ),
        fixed=(
            "def by_letter(words)\n"
            "  groups = Hash.new { |hash, key| hash[key] = [] }\n"
            "  words.each { |word| groups[word[0]] << word }\n"
            "  groups\n"
            "end\n"
            "\n"
            "def index_lines(words)\n"
            "  groups = by_letter(words)\n"
            "  groups.keys.sort.map { |k| \"#{k}: #{groups[k].join(\", \")}\" }\n"
            "end\n"
        ),
        solve=_index_lines,
        reported=(["apple", "avocado", "banana"],),
        cases=(([],), (["apple", "avocado", "banana"],), (["kiwi"],),
               (["fig", "date", "fern"],)),
        cause="Hash.new([]) hands back one shared array for every missing "
              "key without storing it, so << adds to that array and no "
              "key is ever created.",
        decoys=(
            "word[0] is a number in Ruby, so every word goes under the "
            "same key.",
            "each returns the words rather than the hash, so groups is "
            "thrown away.",
            "groups.keys.sort fails on string keys and returns an empty "
            "array.",
        ),
        lesson="Hash.new(x) returns x for a missing key but does not put "
               "it in the hash, and it is the same x every time. For a "
               "default you intend to change, use the block form - "
               "Hash.new { |h, k| h[k] = [] } - which makes and stores a "
               "fresh one per key.",
        hint="The report's words: index_lines([\"apple\", \"avocado\", "
             "\"banana\"]). Then think about which input has no lines "
             "to show anyway.",
        checks=(
            ((["apple", "avocado", "banana"],),
             ["a: apple, avocado", "b: banana"]),
            (([],), []),
            ((["fig", "date", "fern"],), ["d: date", "f: fig, fern"]),
        ),
    ),
)
