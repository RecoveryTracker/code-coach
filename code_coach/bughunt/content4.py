"""More bug hunts in Dart - the second set, again Flutter-flavoured.

The first set (content3) covers ~/ against /, ''.split, List.filled,
compareTo and capitals, and >= at a limit. These are different
mistakes, each one an app bug people actually ship:

  lastIndexOf -1      "not found" is -1, and -1 + 1 is 0, so a file
                      with no extension gets its whole name as one
  ?? 0                turns "no score" into a score of 0, and then a
                      real 0 looks like no score at all
  removeWhere         changes the caller's list, so the total it is
                      compared with shrinks too
  (price * 100)       0.29 is stored just under 0.29, and toInt()
    .toInt()          chops 28.999... down to 28 cents
  '2026-9-30'         dates compared as text without zero padding, so
                      October comes before September

In every one the report is about one function and the cause is in
another it calls, because following a value back is the job. The same
rules hold as for the other hunts, and the suite checks them: the bug is
real, it hides on some inputs, the report's own input shows it, and the
fix changes one or two lines in place.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

DART = "Dart"


def _file_label(file_name: str) -> str:
    dot = file_name.rfind(".")
    ext = "" if dot == -1 else file_name[dot + 1:]
    return f"{ext.upper()} file" if ext else "File"


def _player_card(scores: dict, name: str) -> str:
    if name not in scores:
        return f"{name}: Not played yet"
    return f"{name}: {scores[name]} pts"


def _summary(scores: list) -> str:
    passed = sum(1 for score in scores if score >= 50)
    return f"{passed} of {len(scores)} passed"


def _cart_total(prices: list) -> str:
    # Rounded to the nearest cent one price at a time, the way a till
    # does it - which is what the fixed program does too.
    cents = sum(round(price * 100) for price in prices)
    return f"${cents // 100}.{cents % 100:02d}"


def _is_overdue(due: list, today: list) -> bool:
    # Lists compare element by element, year then month then day.
    return list(due) < list(today)


DART_HUNTS_2: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-dart-no-extension",
        title="README file",
        family=DART,
        language="dart",
        level=1,
        report="Attachments with no extension are labelled with their whole "
               "name - a file called 'README' shows as 'README file'. It "
               "should just say 'File'.",
        name="fileLabel",
        params=("fileName",),
        types=("String",),
        returns="String",
        start=(
            "String extensionOf(String fileName) {\n"
            "  final dot = fileName.lastIndexOf('.');\n"
            "  return fileName.substring(dot + 1);\n"
            "}\n"
            "\n"
            "String fileLabel(String fileName) {\n"
            "  final ext = extensionOf(fileName);\n"
            "  if (ext.isEmpty) return 'File';\n"
            "  return '${ext.toUpperCase()} file';\n"
            "}\n"
        ),
        fixed=(
            "String extensionOf(String fileName) {\n"
            "  final dot = fileName.lastIndexOf('.');\n"
            "  return dot == -1 ? '' : fileName.substring(dot + 1);\n"
            "}\n"
            "\n"
            "String fileLabel(String fileName) {\n"
            "  final ext = extensionOf(fileName);\n"
            "  if (ext.isEmpty) return 'File';\n"
            "  return '${ext.toUpperCase()} file';\n"
            "}\n"
        ),
        solve=_file_label,
        reported=("README",),
        cases=(("photo.jpg",), ("README",), ("archive.tar.gz",), ("",),
               ("notes.",), ("Makefile",)),
        cause="lastIndexOf gives -1 when there is no dot, and -1 + 1 is 0, so "
              "substring hands back the whole name as the extension.",
        decoys=(
            "substring throws a RangeError when there is no dot in the name.",
            "substring(dot + 1) skips the first letter of the extension.",
            "lastIndexOf finds the first dot, so 'archive.tar.gz' is read as "
            "'tar'.",
        ),
        lesson="indexOf and lastIndexOf say 'not found' with -1 - and -1 is a "
               "perfectly good number to do sums with, so nothing crashes; the "
               "answer is just wrong. substring(0, -1) would throw, but "
               "substring(-1 + 1) quietly gives the whole string. Check for -1 "
               "before you use the index.",
        hint="Try a file name with no dot in it at all: fileLabel(\"README\").",
        checks=((("README",), "File"), (("photo.jpg",), "JPG file"),
                (("archive.tar.gz",), "GZ file"), (("",), "File"),
                (("notes.",), "File")),
    ),
    Hunt(
        id="hunt-dart-zero-score",
        title="Played, scored nothing",
        family=DART,
        language="dart",
        level=2,
        report="Sam played one game and scored 0, and his card says 'Sam: Not "
               "played yet'. Players who scored something show fine.",
        name="playerCard",
        params=("scores", "name"),
        types=("Map<String, int>", "String"),
        returns="String",
        start=(
            "String scoreLabel(int? score) {\n"
            "  final points = score ?? 0;\n"
            "  if (points == 0) return 'Not played yet';\n"
            "  return '$points pts';\n"
            "}\n"
            "\n"
            "String playerCard(Map<String, int> scores, String name) {\n"
            "  final score = scores[name];\n"
            "  return '$name: ${scoreLabel(score)}';\n"
            "}\n"
        ),
        fixed=(
            "String scoreLabel(int? score) {\n"
            "  final points = score ?? 0;\n"
            "  if (score == null) return 'Not played yet';\n"
            "  return '$points pts';\n"
            "}\n"
            "\n"
            "String playerCard(Map<String, int> scores, String name) {\n"
            "  final score = scores[name];\n"
            "  return '$name: ${scoreLabel(score)}';\n"
            "}\n"
        ),
        solve=_player_card,
        reported=({"Sam": 0}, "Sam"),
        cases=(({"Sam": 0}, "Sam"), ({"Ana": 12}, "Ana"), ({"Ana": 12}, "Sam"),
               ({}, "Kai"), ({"Ana": 3, "Bo": 0}, "Bo"),
               ({"Ana": 3, "Bo": 0}, "Ana")),
        cause="scoreLabel turns a missing score into 0 with ??, then treats 0 "
              "as missing - so a real score of 0 looks like no score at all.",
        decoys=(
            "scores[name] throws when the name is not in the map.",
            "?? swaps in its default for 0 as well as for null, like || in "
            "JavaScript.",
            "playerCard passes the name to scoreLabel instead of the score.",
        ),
        lesson="?? only steps in for null - unlike JavaScript's ||, it leaves "
               "0 alone. The trouble is what comes after: once a missing value "
               "has been turned into 0, nothing further on can tell 'no score' "
               "from 'scored nothing'. Check for null while you still have it; "
               "that difference is what int? is for.",
        hint="The report is about a real score of zero: "
             "playerCard({\"Sam\": 0}, \"Sam\").",
        checks=((({"Sam": 0}, "Sam"), "Sam: 0 pts"),
                (({"Ana": 12}, "Sam"), "Sam: Not played yet"),
                (({"Ana": 12}, "Ana"), "Ana: 12 pts"),
                (({}, "Kai"), "Kai: Not played yet")),
    ),
    Hunt(
        id="hunt-dart-remove-where",
        title="One of one passed",
        family=DART,
        language="dart",
        level=2,
        report="Two students sat the quiz - one scored 40, the other 60 - and "
               "the results say '1 of 1 passed'. It should be 1 of 2.",
        name="summary",
        params=("scores",),
        types=("List<int>",),
        returns="String",
        start=(
            "const passMark = 50;\n"
            "\n"
            "List<int> passing(List<int> scores) {\n"
            "  scores.removeWhere((score) => score < passMark);\n"
            "  return scores;\n"
            "}\n"
            "\n"
            "String summary(List<int> scores) {\n"
            "  final passed = passing(scores).length;\n"
            "  return '$passed of ${scores.length} passed';\n"
            "}\n"
        ),
        fixed=(
            "const passMark = 50;\n"
            "\n"
            "List<int> passing(List<int> scores) {\n"
            "  final kept = scores.where((score) => score >= passMark);\n"
            "  return kept.toList();\n"
            "}\n"
            "\n"
            "String summary(List<int> scores) {\n"
            "  final passed = passing(scores).length;\n"
            "  return '$passed of ${scores.length} passed';\n"
            "}\n"
        ),
        solve=_summary,
        reported=([40, 60],),
        cases=(([40, 60],), ([70, 80],), ([],), ([50],), ([10, 20, 90],),
               ([55, 45, 65],)),
        cause="passing removes the failed scores from the very list it was "
              "handed, so by the time summary reads scores.length the failures "
              "are gone from it too.",
        decoys=(
            "Dart hands functions a copy of a list, so passing never sees the "
            "real scores.",
            "removeWhere keeps the scores that match the test and removes the "
            "rest.",
            "A score of exactly 50 counts as a fail.",
        ),
        lesson="removeWhere, sort, add and clear change the list itself, and a "
               "function that is handed a list gets the caller's list, not a "
               "copy. where(...).toList() builds a new list and leaves the "
               "original alone. In Flutter this is how state changes behind "
               "your back - or how a widget fails to rebuild because the "
               "'new' list is the old one.",
        hint="Include a score that fails as well as one that passes: "
             "summary([40, 60]).",
        checks=((([40, 60],), "1 of 2 passed"), (([],), "0 of 0 passed"),
                (([50],), "1 of 1 passed"), (([10, 20, 90],), "1 of 3 passed")),
    ),
    Hunt(
        id="hunt-dart-lost-cent",
        title="The missing cent",
        family=DART,
        language="dart",
        level=3,
        report="A cart holding a single 29-cent sticker shows a total of $0.28. "
               "Most carts add up fine.",
        name="cartTotal",
        params=("prices",),
        types=("List<double>",),
        returns="String",
        start=(
            "int toCents(double price) {\n"
            "  return (price * 100).toInt();\n"
            "}\n"
            "\n"
            "int cartCents(List<double> prices) {\n"
            "  var total = 0;\n"
            "  for (final price in prices) {\n"
            "    total += toCents(price);\n"
            "  }\n"
            "  return total;\n"
            "}\n"
            "\n"
            "String cartTotal(List<double> prices) {\n"
            "  final cents = cartCents(prices);\n"
            "  final pennies = (cents % 100).toString().padLeft(2, '0');\n"
            "  return '\\$${cents ~/ 100}.$pennies';\n"
            "}\n"
        ),
        fixed=(
            "int toCents(double price) {\n"
            "  return (price * 100).round();\n"
            "}\n"
            "\n"
            "int cartCents(List<double> prices) {\n"
            "  var total = 0;\n"
            "  for (final price in prices) {\n"
            "    total += toCents(price);\n"
            "  }\n"
            "  return total;\n"
            "}\n"
            "\n"
            "String cartTotal(List<double> prices) {\n"
            "  final cents = cartCents(prices);\n"
            "  final pennies = (cents % 100).toString().padLeft(2, '0');\n"
            "  return '\\$${cents ~/ 100}.$pennies';\n"
            "}\n"
        ),
        solve=_cart_total,
        reported=([0.29],),
        cases=(([],), ([0.29],), ([1.5],), ([2.25, 0.75],), ([19.99, 5.0],),
               ([9.99, 3.1],), ([1.15, 0.57],)),
        cause="0.29 is stored as a binary fraction just under 0.29, so price * "
              "100 comes out as 28.999..., and toInt() chops the fraction off "
              "instead of rounding.",
        decoys=(
            "toInt() rounds to the nearest whole number, and 28.5 rounds down.",
            "~/ drops the fraction from the cents, which loses a penny.",
            "padLeft puts the zero on the wrong side, so 29 cents prints as 28.",
        ),
        lesson="Most prices cannot be stored exactly as a double: 0.29 is "
               "really 0.28999999999999998, and times 100 that is "
               "28.999999999999996. toInt() drops everything after the point; "
               "round() goes to the nearest whole cent. Better still, keep "
               "money as whole cents in an int from the start - which is what "
               "payment APIs do.",
        hint="Round prices like 1.50 come out right. Try one that does not: "
             "cartTotal([0.29]).",
        checks=((([0.29],), "$0.29"), (([],), "$0.00"),
                (([19.99, 5.0],), "$24.99"), (([2.25, 0.75],), "$3.00"),
                (([1.15, 0.57],), "$1.72")),
    ),
    Hunt(
        id="hunt-dart-overdue",
        title="Overdue before it's due",
        family=DART,
        language="dart",
        level=3,
        report="Today is 30 September 2026 and a task due on 5 October is "
               "already marked overdue.",
        name="isOverdue",
        params=("due", "today"),
        types=("List<int>", "List<int>"),
        returns="bool",
        start=(
            "String dateKey(int year, int month, int day) {\n"
            "  return '$year-$month-$day';\n"
            "}\n"
            "\n"
            "String keyOf(List<int> date) {\n"
            "  return dateKey(date[0], date[1], date[2]);\n"
            "}\n"
            "\n"
            "bool isOverdue(List<int> due, List<int> today) {\n"
            "  final dueKey = keyOf(due);\n"
            "  final todayKey = keyOf(today);\n"
            "  return dueKey.compareTo(todayKey) < 0;\n"
            "}\n"
        ),
        fixed=(
            "String dateKey(int year, int month, int day) {\n"
            "  return '$year-${month.toString().padLeft(2, '0')}-"
            "${day.toString().padLeft(2, '0')}';\n"
            "}\n"
            "\n"
            "String keyOf(List<int> date) {\n"
            "  return dateKey(date[0], date[1], date[2]);\n"
            "}\n"
            "\n"
            "bool isOverdue(List<int> due, List<int> today) {\n"
            "  final dueKey = keyOf(due);\n"
            "  final todayKey = keyOf(today);\n"
            "  return dueKey.compareTo(todayKey) < 0;\n"
            "}\n"
        ),
        solve=_is_overdue,
        reported=([2026, 10, 5], [2026, 9, 30]),
        cases=(([2026, 10, 5], [2026, 9, 30]), ([2026, 9, 5], [2026, 9, 8]),
               ([2026, 9, 8], [2026, 9, 8]), ([2026, 3, 1], [2026, 2, 28]),
               ([2025, 12, 31], [2026, 1, 1]), ([2026, 9, 10], [2026, 9, 9]),
               ([2026, 9, 9], [2026, 11, 2])),
        cause="dateKey writes months and days without a leading zero, and "
              "text compares one character at a time - so '2026-10-5' comes "
              "before '2026-9-30', because '1' comes before '9'.",
        decoys=(
            "Months count from 0 in Dart, so October is month 9.",
            "isOverdue has the comparison the wrong way round; it should be "
            "> 0.",
            "keyOf reads the date back to front and takes the day as the "
            "year.",
        ),
        lesson="Dates compared as text only sort right when every part is the "
               "same width: '2026-09-30' < '2026-10-05', but '2026-9-30' > "
               "'2026-10-5'. That is why ISO 8601 dates are zero-padded. In "
               "Dart, comparing DateTime values with isBefore avoids the "
               "question entirely. (Months count from 1 in Dart; it is "
               "JavaScript's Date that counts them from 0.)",
        hint="Try a due date in a two-digit month when today is in a one-digit "
             "month: isOverdue([2026, 10, 5], [2026, 9, 30]).",
        checks=((([2026, 10, 5], [2026, 9, 30]), False),
                (([2026, 9, 5], [2026, 9, 8]), True),
                (([2026, 9, 8], [2026, 9, 8]), False),
                (([2025, 12, 31], [2026, 1, 1]), True),
                (([2026, 9, 10], [2026, 9, 9]), False)),
    ),
)
