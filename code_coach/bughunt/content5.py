"""More bug hunts in Dart - the third set.

The first two sets (content3, content4) cover ~/ against /, ''.split,
List.filled, compareTo and capitals, >= at a limit, lastIndexOf -1,
?? 0, removeWhere on the caller's list, toInt() on 28.999..., and dates
compared as unpadded text. These are five more, each one a mistake
Flutter code makes:

  quarters[month]     DateTime months run 1 to 12 but a List starts at
                      0, so March lands in Q2 and December throws
  padLeft             used for a name column that should be padRight,
                      so short names drift away from the column edge
  firstWhere orElse   a "not found" default that is a real element, so
                      a search with no match shows the first contact
  remove in for-in    taking keys out of a map while walking its keys
                      throws ConcurrentModificationError
  toInt() below 0     toInt() chops toward zero, so -0.5 becomes 0 and
                      the frost warning never goes off

As in the other sets, the report is about one function and the cause is
in another it calls, and the suite holds every hunt to the same rules:
the bug is real, it hides on some inputs, the report's own input shows
it, and the fix changes one or two lines in place.
"""

from __future__ import annotations

import datetime
import math

from code_coach.bughunt import Hunt

DART = "Dart"


def _filed_under(iso_date: str) -> str:
    date = datetime.date.fromisoformat(iso_date)
    return f"Q{(date.month - 1) // 3 + 1} {date.year}"


def _stock_row(name: str, qty: int) -> str:
    return f"{name.ljust(8)}|{str(qty).rjust(3)}"


def _search_result(contacts: list, query: str) -> str:
    q = query.lower()
    match = next((c for c in contacts if c.lower().startswith(q)), None)
    return f"Top result: {match}" if match else "No contacts found"


def _shelf_list(stock: dict) -> str:
    items = [item for item, count in stock.items() if count != 0]
    return ", ".join(items) if items else "Nothing on the shelf"


def _frost_check(readings: list) -> str:
    low = math.floor(sum(readings) / len(readings))
    return f"Frost warning ({low})" if low < 0 else f"No frost ({low})"


DART_HUNTS_3: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-dart-month-index",
        title="March in Q2",
        family=DART,
        language="dart",
        level=1,
        report="An invoice dated 15 March 2026 is filed under 'Q2 2026'. "
               "March is in the first quarter. January and February invoices "
               "look fine.",
        name="filedUnder",
        params=("isoDate",),
        types=("String",),
        returns="String",
        start=(
            "const quarters = ['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2',\n"
            "    'Q3', 'Q3', 'Q3', 'Q4', 'Q4', 'Q4'];\n"
            "\n"
            "String quarterOf(DateTime date) {\n"
            "  return quarters[date.month];\n"
            "}\n"
            "\n"
            "String filedUnder(String isoDate) {\n"
            "  final date = DateTime.parse(isoDate);\n"
            "  return '${quarterOf(date)} ${date.year}';\n"
            "}\n"
        ),
        fixed=(
            "const quarters = ['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2',\n"
            "    'Q3', 'Q3', 'Q3', 'Q4', 'Q4', 'Q4'];\n"
            "\n"
            "String quarterOf(DateTime date) {\n"
            "  return quarters[date.month - 1];\n"
            "}\n"
            "\n"
            "String filedUnder(String isoDate) {\n"
            "  final date = DateTime.parse(isoDate);\n"
            "  return '${quarterOf(date)} ${date.year}';\n"
            "}\n"
        ),
        solve=_filed_under,
        reported=("2026-03-15",),
        cases=(("2026-03-15",), ("2026-01-10",), ("2026-02-28",),
               ("2026-05-01",), ("2026-06-30",), ("2025-11-02",),
               ("2026-12-24",)),
        cause="DateTime.month runs from 1 for January to 12 for December, but "
              "the list starts at index 0 - so every month reads the entry for "
              "the month after it, and December reads past the end.",
        decoys=(
            "DateTime.parse reads '2026-03-15' as day 3 of month 15.",
            "DateTime.month counts from 0, like JavaScript's Date, so March "
            "is 2.",
            "The quarters list has one 'Q1' too few, so everything after "
            "February shifts.",
        ),
        lesson="Dart's DateTime counts months the way people do, 1 to 12 - "
               "unlike JavaScript's Date. A List counts from 0. Whenever a "
               "month (or a weekday, which runs 1 to 7) indexes a list, it "
               "needs a - 1, and the month that gives it away is the last one: "
               "quarters[12] is a RangeError. The months that happen to share "
               "a quarter with their neighbour hide the bug.",
        hint="January and February come out right. Try the last month of a "
             "quarter: filedUnder(\"2026-03-15\").",
        checks=((("2026-03-15",), "Q1 2026"), (("2026-01-10",), "Q1 2026"),
                (("2026-06-30",), "Q2 2026"), (("2026-12-24",), "Q4 2026"),
                (("2025-11-02",), "Q4 2025")),
    ),
    Hunt(
        id="hunt-dart-pad-column",
        title="Names on the wrong side",
        family=DART,
        language="dart",
        level=1,
        report="In the stock table, short names sit over on the right of their "
               "column - the 'Tea' row reads '     Tea|  2' instead of starting "
               "at the edge. 'Biscuits' lines up fine.",
        name="stockRow",
        params=("name", "qty"),
        types=("String", "int"),
        returns="String",
        start=(
            "const nameWidth = 8;\n"
            "const qtyWidth = 3;\n"
            "\n"
            "String nameCell(String name) {\n"
            "  return name.padLeft(nameWidth);\n"
            "}\n"
            "\n"
            "String qtyCell(int qty) {\n"
            "  return qty.toString().padLeft(qtyWidth);\n"
            "}\n"
            "\n"
            "String stockRow(String name, int qty) {\n"
            "  return '${nameCell(name)}|${qtyCell(qty)}';\n"
            "}\n"
        ),
        fixed=(
            "const nameWidth = 8;\n"
            "const qtyWidth = 3;\n"
            "\n"
            "String nameCell(String name) {\n"
            "  return name.padRight(nameWidth);\n"
            "}\n"
            "\n"
            "String qtyCell(int qty) {\n"
            "  return qty.toString().padLeft(qtyWidth);\n"
            "}\n"
            "\n"
            "String stockRow(String name, int qty) {\n"
            "  return '${nameCell(name)}|${qtyCell(qty)}';\n"
            "}\n"
        ),
        solve=_stock_row,
        reported=("Tea", 2),
        cases=(("Tea", 2), ("Biscuits", 12), ("Marmalade", 1), ("Jam", 140),
               ("Porridge", 3), ("Oats", 7)),
        cause="nameCell pads the name with padLeft, which adds the spaces in "
              "front of it - text columns want padRight, which adds them "
              "after.",
        decoys=(
            "qtyCell should use padRight, because numbers line up on the left.",
            "padLeft(8) cuts names longer than 8 characters down to 8.",
            "The width counts from 0, so padLeft(8) makes the cell 9 "
            "characters wide.",
        ),
        lesson="padLeft and padRight are named for where the padding goes, not "
               "where the text ends up: padLeft pushes text right, padRight "
               "keeps it on the left. Text columns are usually left-aligned "
               "(padRight) and number columns right-aligned (padLeft) so the "
               "digits line up. Neither ever shortens a string, which is why a "
               "name as long as the column hides the mistake.",
        hint="A name exactly as wide as the column looks right. Try a short "
             "one: stockRow(\"Tea\", 2).",
        checks=((("Tea", 2), "Tea     |  2"), (("Biscuits", 12), "Biscuits| 12"),
                (("Marmalade", 1), "Marmalade|  1"), (("Jam", 140), "Jam     |140")),
    ),
    Hunt(
        id="hunt-dart-or-else",
        title="Searching for Zed finds Ada",
        family=DART,
        language="dart",
        level=2,
        report="I searched my contacts for 'zed' - there is nobody called Zed - "
               "and it said 'Top result: Ada'. Searches that match someone "
               "work.",
        name="searchResult",
        params=("contacts", "query"),
        types=("List<String>", "String"),
        returns="String",
        start=(
            "String firstMatch(List<String> contacts, String query) {\n"
            "  final q = query.toLowerCase();\n"
            "  return contacts.firstWhere(\n"
            "    (name) => name.toLowerCase().startsWith(q),\n"
            "    orElse: () => contacts.first,\n"
            "  );\n"
            "}\n"
            "\n"
            "String searchResult(List<String> contacts, String query) {\n"
            "  final match = firstMatch(contacts, query);\n"
            "  if (match.isEmpty) return 'No contacts found';\n"
            "  return 'Top result: $match';\n"
            "}\n"
        ),
        fixed=(
            "String firstMatch(List<String> contacts, String query) {\n"
            "  final q = query.toLowerCase();\n"
            "  return contacts.firstWhere(\n"
            "    (name) => name.toLowerCase().startsWith(q),\n"
            "    orElse: () => '',\n"
            "  );\n"
            "}\n"
            "\n"
            "String searchResult(List<String> contacts, String query) {\n"
            "  final match = firstMatch(contacts, query);\n"
            "  if (match.isEmpty) return 'No contacts found';\n"
            "  return 'Top result: $match';\n"
            "}\n"
        ),
        solve=_search_result,
        reported=(["Ada", "Grace", "Linus"], "zed"),
        cases=((["Ada", "Grace", "Linus"], "zed"), (["Ada", "Grace", "Linus"], "gr"),
               (["Ada", "Alan"], "AL"), (["Bo"], "b"), ([], "a"),
               (["Ada", "Grace"], "linus")),
        cause="When nothing matches, orElse hands back contacts.first - a real "
              "contact - so searchResult cannot tell 'no match' from a match, "
              "and on an empty list .first throws.",
        decoys=(
            "firstWhere returns the first element whenever its test fails on "
            "that element.",
            "startsWith is case-sensitive, so 'zed' is compared with 'Zed' and "
            "misses.",
            "firstWhere throws when nothing matches, and the error is shown as "
            "the first name.",
        ),
        lesson="firstWhere throws a StateError when nothing matches, so orElse "
               "is how you say what 'not found' looks like - and it has to be "
               "something that cannot be mistaken for a real answer. Returning "
               "an element of the list is the worst choice. In null-safe Dart "
               "the cleanest version is firstWhereOrNull from package:"
               "collection, or `where(...).firstOrNull`, which make 'not found' "
               "a null the type system makes you check.",
        hint="Searches that find someone are fine. Search for a name that is "
             "not there: searchResult([\"Ada\", \"Grace\", \"Linus\"], \"zed\").",
        checks=(((["Ada", "Grace", "Linus"], "zed"), "No contacts found"),
                ((["Ada", "Grace", "Linus"], "gr"), "Top result: Grace"),
                ((["Ada", "Alan"], "AL"), "Top result: Alan"),
                (([], "a"), "No contacts found")),
    ),
    Hunt(
        id="hunt-dart-remove-while-iterating",
        title="Sold out, then crashed",
        family=DART,
        language="dart",
        level=2,
        report="The shelf list crashes as soon as anything sells out - with "
               "tea 3, jam 0 and oats 5 it throws 'Concurrent modification "
               "during iteration' instead of listing tea and oats.",
        name="shelfList",
        params=("stock",),
        types=("Map<String, int>",),
        returns="String",
        start=(
            "Map<String, int> inStock(Map<String, int> stock) {\n"
            "  final left = Map.of(stock);\n"
            "  for (final item in left.keys) {\n"
            "    if (left[item] == 0) left.remove(item);\n"
            "  }\n"
            "  return left;\n"
            "}\n"
            "\n"
            "String shelfList(Map<String, int> stock) {\n"
            "  final items = inStock(stock).keys;\n"
            "  if (items.isEmpty) return 'Nothing on the shelf';\n"
            "  return items.join(', ');\n"
            "}\n"
        ),
        fixed=(
            "Map<String, int> inStock(Map<String, int> stock) {\n"
            "  final left = Map.of(stock);\n"
            "  for (final item in left.keys.toList()) {\n"
            "    if (left[item] == 0) left.remove(item);\n"
            "  }\n"
            "  return left;\n"
            "}\n"
            "\n"
            "String shelfList(Map<String, int> stock) {\n"
            "  final items = inStock(stock).keys;\n"
            "  if (items.isEmpty) return 'Nothing on the shelf';\n"
            "  return items.join(', ');\n"
            "}\n"
        ),
        solve=_shelf_list,
        reported=({"tea": 3, "jam": 0, "oats": 5},),
        cases=(({"tea": 3, "jam": 0, "oats": 5},), ({"tea": 3},), ({},),
               ({"jam": 0},), ({"tea": 1, "oats": 2},), ({"oats": 4, "jam": 0},)),
        cause="The loop walks left.keys, which is a live view of the map, and "
              "removes from the same map while it walks - so the next step "
              "of the loop throws ConcurrentModificationError.",
        decoys=(
            "Map.of(stock) is the same map as stock, so removing from it "
            "changes the caller's map.",
            "left[item] is an int?, and comparing it with 0 throws when it is "
            "null.",
            "remove(item) removes the entry by position rather than by key.",
        ),
        lesson="map.keys (and map.values, map.entries) is a view onto the map, "
               "not a copy, and a Dart for-in checks that its collection has "
               "not changed at every step. Adding or removing while you loop "
               "over it throws. Walk a copy - keys.toList() - or, better, say "
               "what you mean in one call: left.removeWhere((k, v) => v == 0). "
               "It only throws when something is removed, which is why a shelf "
               "with nothing sold out looks fine.",
        hint="Everything in stock works. Put something at zero: "
             "shelfList({\"tea\": 3, \"jam\": 0, \"oats\": 5}).",
        checks=((({"tea": 3, "jam": 0, "oats": 5},), "tea, oats"),
                (({"tea": 3},), "tea"), (({},), "Nothing on the shelf"),
                (({"jam": 0},), "Nothing on the shelf")),
    ),
    Hunt(
        id="hunt-dart-negative-toint",
        title="No frost at minus a half",
        family=DART,
        language="dart",
        level=3,
        report="Overnight the sensor read -1 and 0, and the app said 'No frost "
               "(0)'. The frost warning should have gone off. Warm nights and "
               "properly cold ones are reported fine.",
        name="frostCheck",
        params=("readings",),
        types=("List<int>",),
        returns="String",
        start=(
            "double average(List<int> readings) {\n"
            "  var total = 0;\n"
            "  for (final r in readings) {\n"
            "    total += r;\n"
            "  }\n"
            "  return total / readings.length;\n"
            "}\n"
            "\n"
            "// The whole degree at or below the value, so frost is never\n"
            "// rounded away.\n"
            "int wholeDegrees(double value) {\n"
            "  return value.toInt();\n"
            "}\n"
            "\n"
            "String frostCheck(List<int> readings) {\n"
            "  final low = wholeDegrees(average(readings));\n"
            "  if (low < 0) return 'Frost warning ($low)';\n"
            "  return 'No frost ($low)';\n"
            "}\n"
        ),
        fixed=(
            "double average(List<int> readings) {\n"
            "  var total = 0;\n"
            "  for (final r in readings) {\n"
            "    total += r;\n"
            "  }\n"
            "  return total / readings.length;\n"
            "}\n"
            "\n"
            "// The whole degree at or below the value, so frost is never\n"
            "// rounded away.\n"
            "int wholeDegrees(double value) {\n"
            "  return value.floor();\n"
            "}\n"
            "\n"
            "String frostCheck(List<int> readings) {\n"
            "  final low = wholeDegrees(average(readings));\n"
            "  if (low < 0) return 'Frost warning ($low)';\n"
            "  return 'No frost ($low)';\n"
            "}\n"
        ),
        solve=_frost_check,
        reported=([-1, 0],),
        cases=(([-1, 0],), ([2, 3],), ([-4, -2],), ([5],), ([0, -1, -1],),
               ([-3, -4],), ([1, 2, 2],)),
        cause="toInt() chops the fraction off toward zero, so an average of "
              "-0.5 becomes 0 rather than -1 - for a negative number that "
              "rounds up, not down.",
        decoys=(
            "total / readings.length does whole-number division, so -1 / 2 "
            "is 0.",
            "toInt() rounds to the nearest whole number, and -0.5 rounds to 0.",
            "low < 0 should be low <= 0, so 0 counts as frost.",
        ),
        lesson="toInt() and truncate() drop the fraction, which moves the "
               "number toward zero: down for positives, but up for negatives. "
               "floor() always goes down and ceil() always up; round() goes "
               "to the nearest. The same goes for ~/, which truncates too: "
               "-1 ~/ 2 is 0 in Dart, where Python's -1 // 2 is -1. Positive "
               "test data never shows the difference.",
        hint="Warm nights are fine and so are whole-number cold ones. Try an "
             "average between -1 and 0: frostCheck([-1, 0]).",
        checks=((([-1, 0],), "Frost warning (-1)"), (([2, 3],), "No frost (2)"),
                (([-4, -2],), "Frost warning (-3)"),
                (([-3, -4],), "Frost warning (-4)"),
                (([0, -1, -1],), "Frost warning (-1)")),
    ),
)
