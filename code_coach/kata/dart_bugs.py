"""Fix the bug, in Dart: the function is written, and it is wrong.

The same exercise as the Python family - working-looking code that fails
some of its cases, and the job is to find out why - but the bugs are
Dart's own, or the ones Flutter code runs into, rather than Python's
translated:

  the whole-number divide  `~/` where a part-filled row still counts
  the exclusive end        `substring(0, dot - 1)`, one short
  the empty split          `''.split(',')` is `['']`, not `[]`
  the empty string         `??` catches null, and '' is not null
  the in-place sort        `sort()` rearranging the caller's list
  the shared slot          `List.filled` with one list in every slot

Each one compiles and runs, because a start that does not compile
teaches the compiler rather than the bug. And each one passes some of
its cases, because that is what makes a bug hard to see: it is right on
the inputs you thought of and wrong on the ones you did not.

The expected answers come from the Python oracle, as for every kata. The
note in `bug` is shown once it passes.
"""

from __future__ import annotations

from code_coach.kata import Kata


def _grid_rows(item_count: int, per_row: int) -> int:
    return (item_count + per_row - 1) // per_row


def _strip_extension(file_name: str) -> str:
    dot = file_name.rfind(".")
    return file_name if dot == -1 else file_name[:dot]


def _parse_tags(csv: str) -> list:
    if not csv.strip():
        return []
    return [tag.strip() for tag in csv.split(",")]


def _display_name(user: dict) -> str:
    nickname = user.get("nickname")
    return nickname if nickname else user["name"]


def _top_scores(scores: list, n: int) -> list:
    return sorted(scores, reverse=True)[:n]


def _into_columns(items: list, columns: int) -> list:
    return [items[i::columns] for i in range(columns)]


DART_BUGS: tuple[Kata, ...] = (
    Kata(
        id="dart-bug-grid-rows",
        level=1,
        name="gridRows",
        brief=(
            "Return how many rows a grid needs to show itemCount tiles, "
            "perRow to a row. A part-filled last row is still a row, and "
            "no tiles need no rows."
        ),
        params=("itemCount", "perRow"),
        types=("int", "int"),
        returns="int",
        family="Fix the bug: Dart",
        language="dart",
        example="gridRows(10, 3) is 4: three full rows and one with a single tile",
        hint="Try 10 tiles at 3 a row. What does ~/ do with the one left over?",
        cases=(
            (10, 3), (0, 3), (9, 3), (1, 4), (4, 4), (5, 4), (7, 1),
            (12, 5), (2, 5), (6, 2),
        ),
        solve=_grid_rows,
        checks=(((10, 3), 4), ((0, 3), 0), ((9, 3), 3), ((1, 4), 1),
                ((5, 4), 2)),
        start=(
            "int gridRows(int itemCount, int perRow) {\n"
            "  // One row for every perRow tiles.\n"
            "  return itemCount ~/ perRow;\n"
            "}"
        ),
        bug="`~/` is whole-number division and throws the remainder away, "
            "so the part-filled last row is lost whenever the tiles do not "
            "divide evenly. `/` gives a double, and `.ceil()` rounds it up "
            "to the int you wanted.",
        dart_answer=(
            "int gridRows(int itemCount, int perRow) {\n"
            "  // One row for every perRow tiles, and one more for any left over.\n"
            "  return (itemCount / perRow).ceil();\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-strip-extension",
        level=2,
        name="stripExtension",
        brief=(
            "Return the file name without its extension: everything before "
            "the last dot. A name with no dot comes back unchanged."
        ),
        params=("fileName",),
        types=("String",),
        returns="String",
        family="Fix the bug: Dart",
        language="dart",
        example=(
            "stripExtension('photo.jpg') is 'photo', and "
            "stripExtension('archive.tar.gz') is 'archive.tar'"
        ),
        hint="In substring(start, end), is the character at end part of "
             "what comes back?",
        cases=(
            ("photo.jpg",), ("",), ("README",), ("a.b",), ("x",),
            ("archive.tar.gz",), ("notes.txt",), (".env",), ("v1.2",),
            ("Makefile",),
        ),
        solve=_strip_extension,
        checks=((("photo.jpg",), "photo"), (("",), ""), (("README",), "README"),
                (("archive.tar.gz",), "archive.tar"), ((".env",), "")),
        start=(
            "String stripExtension(String fileName) {\n"
            "  final dot = fileName.lastIndexOf('.');\n"
            "  if (dot == -1) return fileName;\n"
            "  // Everything up to the character before the dot.\n"
            "  return fileName.substring(0, dot - 1);\n"
            "}"
        ),
        bug="The end index of substring is already left out - "
            "substring(0, dot) stops just before the dot - so `dot - 1` "
            "cuts off the last letter of the name as well. On '.env' it "
            "asks for an end of -1, which is a RangeError.",
        dart_answer=(
            "String stripExtension(String fileName) {\n"
            "  final dot = fileName.lastIndexOf('.');\n"
            "  if (dot == -1) return fileName;\n"
            "  // Everything before the dot: the end index is left out.\n"
            "  return fileName.substring(0, dot);\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-parse-tags",
        level=2,
        name="parseTags",
        brief=(
            "Split a comma-separated string of tags into a list, trimming "
            "the spaces around each tag. An empty or blank string has no "
            "tags, so it gives an empty list."
        ),
        params=("csv",),
        types=("String",),
        returns="List<String>",
        family="Fix the bug: Dart",
        language="dart",
        example="parseTags('dart, flutter') is ['dart', 'flutter'], and "
                "parseTags('') is []",
        hint="Run ''.split(',') on its own and look at how long the list "
             "it gives back is.",
        cases=(
            ("dart, flutter",), ("",), ("solo",), ("a,b,c",), ("   ",),
            (" ui , state ",), ("x",), ("widgets,  layout",),
            ("one, two, three, four",), ("null safety, streams",),
        ),
        solve=_parse_tags,
        checks=((("dart, flutter",), ["dart", "flutter"]), (("",), []),
                (("solo",), ["solo"]), (("   ",), []),
                ((" ui , state ",), ["ui", "state"])),
        start=(
            "List<String> parseTags(String csv) {\n"
            "  return csv.split(',').map((tag) => tag.trim()).toList();\n"
            "}"
        ),
        bug="Splitting an empty string does not give an empty list: "
            "''.split(',') is [''], one tag with nothing in it, and a row "
            "of chips built from that shows one blank chip. Nothing to "
            "split has to be caught before the split.",
        dart_answer=(
            "List<String> parseTags(String csv) {\n"
            "  if (csv.trim().isEmpty) return [];\n"
            "  return csv.split(',').map((tag) => tag.trim()).toList();\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-display-name",
        level=3,
        name="displayName",
        brief=(
            "Return the name to show for a user decoded from JSON: their "
            "nickname if they have one, otherwise their name. A nickname "
            "that is missing, null or empty does not count."
        ),
        params=("user",),
        types=("Map<String, dynamic>",),
        returns="String",
        family="Fix the bug: Dart",
        language="dart",
        example=(
            "displayName({'name': 'Ada', 'nickname': 'Countess'}) is "
            "'Countess', and with 'nickname': '' it is 'Ada'"
        ),
        hint="?? steps in when the left side is null. Is an empty string "
             "null?",
        cases=(
            ({"name": "Ada", "nickname": "Countess"},),
            ({"name": "Ada"},),
            ({"name": "Ada", "nickname": None},),
            ({"name": "Ada", "nickname": ""},),
            ({"name": "Grace", "nickname": "Amazing Grace"},),
            ({"name": "Linus", "nickname": ""},),
            ({"name": "Alan", "nickname": "Al"},),
            ({"name": "Margaret", "nickname": None},),
            ({"name": "Tim"},),
            ({"name": "Barbara", "nickname": "B"},),
        ),
        solve=_display_name,
        checks=(
            (({"name": "Ada", "nickname": "Countess"},), "Countess"),
            (({"name": "Ada"},), "Ada"),
            (({"name": "Ada", "nickname": None},), "Ada"),
            (({"name": "Ada", "nickname": ""},), "Ada"),
        ),
        start=(
            "String displayName(Map<String, dynamic> user) {\n"
            "  final String? nickname = user['nickname'];\n"
            "  return nickname ?? user['name'];\n"
            "}"
        ),
        bug="`??` only steps in for null, and an empty string is not null "
            "- it is a String that happens to hold nothing - so '' went "
            "straight through and the screen showed a blank. APIs send "
            "both, so check for each.",
        dart_answer=(
            "String displayName(Map<String, dynamic> user) {\n"
            "  final String? nickname = user['nickname'];\n"
            "  if (nickname == null || nickname.isEmpty) return user['name'];\n"
            "  return nickname;\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-top-scores",
        level=4,
        name="topScores",
        brief=(
            "Return the n highest scores, highest first. The list you were "
            "given must not change: the screen that passed it in is still "
            "showing it in its own order."
        ),
        params=("scores", "n"),
        types=("List<int>", "int"),
        returns="List<int>",
        family="Fix the bug: Dart",
        language="dart",
        example=(
            "topScores([40, 90, 70], 2) is [90, 70], and the list passed in "
            "is still [40, 90, 70]"
        ),
        hint="Every answer it gives is right. Look at what happened to the "
             "list that was passed in.",
        cases=(
            ([40, 90, 70], 2), ([], 3), ([5], 1), ([90, 70, 40], 2),
            ([1, 2, 3], 5), ([3, 1, 2], 0), ([-5, 0, 5], 1), ([7, 7, 3], 2),
            ([10, 30, 20, 40], 3), ([2, 2], 1),
        ),
        solve=_top_scores,
        checks=((([40, 90, 70], 2), [90, 70]), (([], 3), []), (([5], 1), [5]),
                (([1, 2, 3], 5), [3, 2, 1]), (([3, 1, 2], 0), [])),
        start=(
            "List<int> topScores(List<int> scores, int n) {\n"
            "  scores.sort((a, b) => b.compareTo(a));\n"
            "  return scores.take(n).toList();\n"
            "}"
        ),
        bug="List.sort() sorts the list in place, so it rearranged the "
            "caller's own list - the answer was right and the damage was "
            "somewhere else. Sort a copy: [...scores] makes one, and the "
            "cascade `..sort()` sorts it and hands the copy back.",
        dart_answer=(
            "List<int> topScores(List<int> scores, int n) {\n"
            "  final sorted = [...scores]..sort((a, b) => b.compareTo(a));\n"
            "  return sorted.take(n).toList();\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-into-columns",
        level=5,
        name="intoColumns",
        brief=(
            "Deal the items into columns, like a masonry grid: the first "
            "item to column 0, the next to column 1, and round again. Each "
            "column is its own list, and there is always at least one."
        ),
        params=("items", "columns"),
        types=("List<String>", "int"),
        returns="List<List<String>>",
        family="Fix the bug: Dart",
        language="dart",
        example="intoColumns(['a', 'b', 'c'], 2) is [['a', 'c'], ['b']]",
        hint="How many lists does List.filled actually make? Deal one item "
             "and look at every column.",
        cases=(
            (["a", "b", "c"], 2), ([], 3), (["a"], 1), (["a", "b", "c", "d"], 1),
            (["a", "b"], 3), (["x"], 2), (["a", "b", "c", "d"], 2),
            (["p", "q", "r", "s", "t"], 3), ([], 1),
            (["one", "two", "three", "four", "five", "six"], 4),
        ),
        solve=_into_columns,
        checks=(((["a", "b", "c"], 2), [["a", "c"], ["b"]]),
                (([], 3), [[], [], []]), ((["x"], 2), [["x"], []]),
                ((["a", "b"], 3), [["a"], ["b"], []])),
        start=(
            "List<List<String>> intoColumns(List<String> items, int columns) {\n"
            "  final result = List.filled(columns, <String>[]);\n"
            "  for (var i = 0; i < items.length; i++) {\n"
            "    result[i % columns].add(items[i]);\n"
            "  }\n"
            "  return result;\n"
            "}"
        ),
        bug="List.filled puts the same value in every slot, and here that "
            "value is one list - so every column was that one list, and "
            "every item landed in all of them. List.generate calls its "
            "function once per slot, which gives each column a list of "
            "its own.",
        dart_answer=(
            "List<List<String>> intoColumns(List<String> items, int columns) {\n"
            "  final result = List.generate(columns, (_) => <String>[]);\n"
            "  for (var i = 0; i < items.length; i++) {\n"
            "    result[i % columns].add(items[i]);\n"
            "  }\n"
            "  return result;\n"
            "}"
        ),
    ),
)
