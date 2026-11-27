"""More bug hunts in Dart - the fourth set.

The first three sets (content3, content4, content5) cover ~/ against /,
''.split, List.filled, compareTo and capitals, >= at a limit, lastIndexOf
-1, ?? 0, removeWhere on the caller's list, toInt() on 28.999..., dates
compared as text, a month used as a list index, padLeft for padRight, a
firstWhere orElse that is a real element, remove while iterating a map,
and toInt() below zero. These are eight more, each one a mistake Dart
code makes:

  '$guest.name'     interpolation stops at the identifier, so the object
                    prints as "Instance of 'Guest'" followed by ".name"
  replaceFirst      used where replaceAll was meant, so only the first
                    space of a title becomes a dash
  sublist(0, 3)     throws a RangeError when there are fewer than three
                    scores; take(3) just gives what there is
  isEmpty           used for "is blank", so a name of spaces is shown
  int.parse         on a price with a decimal point throws a
                    FormatException
  list == list      compares identity, so two schedules with the same days
                    are never the same
  reduce            throws StateError on an empty list
  DateTime(y, m, 0) the day before the 1st of month m, which is the end of
                    the month BEFORE; the end of m is DateTime(y, m + 1, 0)

As in the other sets, the report is about one function and the cause is
in another it calls (or a line above it), and the suite holds every hunt
to the same rules: the bug is real, it hides on some inputs, the report's
own input shows it, and the fix changes one or two lines in place.
"""

from __future__ import annotations

import calendar

from code_coach.bughunt import Hunt

DART = "Dart"


def _welcome(name: str, vip: bool) -> str:
    return f"Welcome back, {name}!" if vip else f"Welcome, {name}!"


def _slug(title: str) -> str:
    return title.strip().lower().replace(" ", "-")


def _top_three(scores: list) -> str:
    return ", ".join(str(s) for s in sorted(scores, reverse=True)[:3])


def _display_name(name: str) -> str:
    return name if name.strip() else "Anonymous"


def _parse_total(prices: list) -> str:
    return f"{sum(float(p) for p in prices):.2f}"


def _same_schedule(a: list, b: list) -> bool:
    return sorted(a) == sorted(b)


def _report(sales: list) -> str:
    return f"Best sale: {max(sales) if sales else 0}"


def _last_day(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


DART_HUNTS_4: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-dart-interp-dot",
        title="Instance of 'Guest'",
        family=DART,
        language="dart",
        level=1,
        report="A new visitor named Ada is greeted with \"Welcome, Instance of "
               "'Guest'.name!\". Returning VIP visitors see their name fine.",
        name="welcome",
        params=("name", "vip"),
        types=("String", "bool"),
        returns="String",
        start=(
            "class Guest {\n"
            "  final String name;\n"
            "  Guest(this.name);\n"
            "}\n"
            "\n"
            "String welcome(String name, bool vip) {\n"
            "  final guest = Guest(name);\n"
            "  if (vip) {\n"
            "    return 'Welcome back, ${guest.name}!';\n"
            "  }\n"
            "  return 'Welcome, $guest.name!';\n"
            "}\n"
        ),
        fixed=(
            "class Guest {\n"
            "  final String name;\n"
            "  Guest(this.name);\n"
            "}\n"
            "\n"
            "String welcome(String name, bool vip) {\n"
            "  final guest = Guest(name);\n"
            "  if (vip) {\n"
            "    return 'Welcome back, ${guest.name}!';\n"
            "  }\n"
            "  return 'Welcome, ${guest.name}!';\n"
            "}\n"
        ),
        solve=_welcome,
        reported=("Ada", False),
        cases=(("Ada", False), ("Bo", True), ("Cy", False), ("Di", True),
               ("Eve", False)),
        cause="Inside a string, $guest.name interpolates only the variable "
              "guest - the interpolation stops at the dot - so the object's "
              "default text is printed and \".name\" is left as plain "
              "characters. A property needs braces: ${guest.name}.",
        decoys=(
            "The name field is final, so it cannot be read from outside the "
            "class.",
            "Guest needs a toString that returns the name, or nothing works.",
            "The vip branch is wrong: it should be the one without braces.",
        ),
        lesson="In a Dart string, $name takes just the identifier. The moment "
               "you want a property, a method call or any expression - "
               "${guest.name}, ${items.length}, ${a + b} - you need the braces. "
               "The mistake never crashes; it prints \"Instance of 'Guest'\" "
               "and carries on, which is how it hides until someone reads the "
               "screen. The lint unnecessary_brace_in_string_interps pulls the "
               "other way, but only for plain identifiers.",
        hint="The VIP greeting is fine, and so is a bare name. Try someone who "
             "is not a VIP: welcome(\"Ada\", false).",
        checks=((("Ada", False), "Welcome, Ada!"), (("Bo", True), "Welcome back, Bo!"),
                (("Eve", False), "Welcome, Eve!")),
    ),
    Hunt(
        id="hunt-dart-replace-first",
        title="Only the first dash",
        family=DART,
        language="dart",
        level=1,
        report="The post titled 'My First Blog Post' gets the address "
               "'my-first blog post'. One-word titles and two-word titles "
               "come out right.",
        name="slug",
        params=("title",),
        types=("String",),
        returns="String",
        start=(
            "String clean(String title) {\n"
            "  return title.trim().toLowerCase();\n"
            "}\n"
            "\n"
            "String slug(String title) {\n"
            "  final words = clean(title);\n"
            "  return words.replaceFirst(' ', '-');\n"
            "}\n"
        ),
        fixed=(
            "String clean(String title) {\n"
            "  return title.trim().toLowerCase();\n"
            "}\n"
            "\n"
            "String slug(String title) {\n"
            "  final words = clean(title);\n"
            "  return words.replaceAll(' ', '-');\n"
            "}\n"
        ),
        solve=_slug,
        reported=("My First Blog Post",),
        cases=(("My First Blog Post",), ("Hello",), ("Hello World",),
               ("  Trim Me  ",), ("Ten Tips For Gardens",)),
        cause="slug uses replaceFirst, which swaps only the first space it "
              "finds; replaceAll is the one that swaps every space.",
        decoys=(
            "clean lowercases the title too late, so the later words keep "
            "their capitals.",
            "trim removes the spaces between words as well as the ones at "
            "the ends.",
            "replaceFirst counts from the end of the string, so it misses "
            "the first word's space.",
        ),
        lesson="replaceFirst, replaceAll and replaceAllMapped sound alike and "
               "differ in exactly the way their names say. Unlike JavaScript's "
               "replace, which also only touches the first match, Dart's "
               "replaceAll with a plain String is the everyday one. Titles "
               "with one space give no warning: every test you write first "
               "has two words.",
        hint="Titles of one or two words come out right. Try three or more: "
             "slug(\"My First Blog Post\").",
        checks=((("My First Blog Post",), "my-first-blog-post"), (("Hello",), "hello"),
                (("Hello World",), "hello-world"), (("  Trim Me  ",), "trim-me")),
    ),
    Hunt(
        id="hunt-dart-sublist-short",
        title="The leaderboard of two",
        family=DART,
        language="dart",
        level=2,
        report="A game with only two players crashes the leaderboard with "
               "'RangeError (end): Invalid value'. With three or more "
               "players it is fine.",
        name="topThree",
        params=("scores",),
        types=("List<int>",),
        returns="String",
        start=(
            "List<int> ranked(List<int> scores) {\n"
            "  final copy = [...scores];\n"
            "  copy.sort((a, b) => b - a);\n"
            "  return copy;\n"
            "}\n"
            "\n"
            "String topThree(List<int> scores) {\n"
            "  final best = ranked(scores).sublist(0, 3);\n"
            "  return best.join(', ');\n"
            "}\n"
        ),
        fixed=(
            "List<int> ranked(List<int> scores) {\n"
            "  final copy = [...scores];\n"
            "  copy.sort((a, b) => b - a);\n"
            "  return copy;\n"
            "}\n"
            "\n"
            "String topThree(List<int> scores) {\n"
            "  final best = ranked(scores).take(3);\n"
            "  return best.join(', ');\n"
            "}\n"
        ),
        solve=_top_three,
        reported=([5, 9],),
        cases=(([5, 9],), ([4, 8, 1, 6],), ([2],), ([],), ([10, 30, 20],),
               ([7, 7, 7, 7],)),
        cause="sublist(0, 3) insists on three items and throws a RangeError "
              "when the list is shorter; take(3) hands back up to three and "
              "stops at the end.",
        decoys=(
            "ranked sorts the scores from lowest to highest, so the wrong "
            "ones are cut off.",
            "sublist counts its end from 1, so sublist(0, 3) asks for four "
            "items.",
            "copy is the same list as scores, so the sort corrupts the "
            "caller's scores.",
        ),
        lesson="sublist(start, end) is strict: an end past the length is a "
               "RangeError, and so is `first` on an empty list. take(n) and "
               "skip(n) are the forgiving pair - they give what is there. "
               "Whenever the count in your head is 'up to', reach for take. "
               "Bugs like this wait for the first small case: an empty "
               "league, a new user, one result.",
        hint="Three or more scores work. Try fewer than three: "
             "topThree([5, 9]).",
        checks=((([5, 9],), "9, 5"), (([4, 8, 1, 6],), "8, 6, 4"),
                (([2],), "2"), (([10, 30, 20],), "30, 20, 10")),
    ),
    Hunt(
        id="hunt-dart-blank-name",
        title="A name made of spaces",
        family=DART,
        language="dart",
        level=2,
        report="A user who typed three spaces as their name shows up with an "
               "empty heading instead of 'Anonymous'. An empty field is "
               "handled correctly.",
        name="displayName",
        params=("name",),
        types=("String",),
        returns="String",
        start=(
            "const fallback = 'Anonymous';\n"
            "\n"
            "bool isBlank(String text) {\n"
            "  return text.isEmpty;\n"
            "}\n"
            "\n"
            "String displayName(String name) {\n"
            "  return isBlank(name) ? fallback : name;\n"
            "}\n"
        ),
        fixed=(
            "const fallback = 'Anonymous';\n"
            "\n"
            "bool isBlank(String text) {\n"
            "  return text.trim().isEmpty;\n"
            "}\n"
            "\n"
            "String displayName(String name) {\n"
            "  return isBlank(name) ? fallback : name;\n"
            "}\n"
        ),
        solve=_display_name,
        reported=("   ",),
        cases=(("   ",), ("",), ("Ada",), (" Cy ",), ("  ",), ("Bo Li",)),
        cause="isBlank asks only whether the text has no characters at all; "
              "a name of spaces has characters, so it is not empty - it "
              "needs trim() first.",
        decoys=(
            "displayName returns the fallback for every name, because the "
            "condition is the wrong way round.",
            "isEmpty is true for a string of spaces, so the name is "
            "dropped.",
            "fallback is const, so it cannot be returned from a function.",
        ),
        lesson="isEmpty means length == 0, nothing cleverer. Text typed by a "
               "person is blank far more often than it is empty: a space, a "
               "tab, a pasted newline. For a form field the check is "
               "text.trim().isEmpty. The empty-field test you wrote first "
               "passes, which is exactly why this bug reaches users.",
        hint="The empty string is handled. Try something that looks empty but "
             "is not: displayName(\"   \").",
        checks=((("   ",), "Anonymous"), (("",), "Anonymous"),
                (("Ada",), "Ada"), ((" Cy ",), " Cy ")),
    ),
    Hunt(
        id="hunt-dart-int-parse-price",
        title="Two pounds fifty",
        family=DART,
        language="dart",
        level=2,
        report="Adding up the basket ['2.50', '1.25'] crashes with "
               "'FormatException: Invalid radix-10 number'. A basket of whole "
               "prices ['2', '3'] adds up fine.",
        name="parseTotal",
        params=("prices",),
        types=("List<String>",),
        returns="String",
        start=(
            "String parseTotal(List<String> prices) {\n"
            "  num total = 0;\n"
            "  for (final p in prices) {\n"
            "    total += lineValue(p);\n"
            "  }\n"
            "  return total.toStringAsFixed(2);\n"
            "}\n"
            "\n"
            "num lineValue(String text) {\n"
            "  return int.parse(text);\n"
            "}\n"
        ),
        fixed=(
            "String parseTotal(List<String> prices) {\n"
            "  num total = 0;\n"
            "  for (final p in prices) {\n"
            "    total += lineValue(p);\n"
            "  }\n"
            "  return total.toStringAsFixed(2);\n"
            "}\n"
            "\n"
            "num lineValue(String text) {\n"
            "  return num.parse(text);\n"
            "}\n"
        ),
        solve=_parse_total,
        reported=(["2.50", "1.25"],),
        cases=((["2.50", "1.25"],), (["2", "3"],), (["4"],), ([],),
               (["10", "0.5"],), (["7", "8", "9"],)),
        cause="lineValue reads each price with int.parse, which only accepts "
              "whole numbers and throws a FormatException on anything with a "
              "decimal point; num.parse accepts both.",
        decoys=(
            "toStringAsFixed(2) cannot format a num, so the total fails.",
            "total starts at 0, an int, so it can never hold 3.75.",
            "The for loop adds the first price twice before the crash.",
        ),
        lesson="int.parse is strict: '2.50' is a FormatException, not 2 and not "
               "2.5. double.parse takes whole and decimal text alike and "
               "always gives a double; num.parse gives an int when the text "
               "looks like one. tryParse is the same without the throw and "
               "gives null - the right one for anything a person typed.",
        hint="Whole prices work. Try one with a decimal point: "
             "parseTotal([\"2.50\", \"1.25\"]).",
        checks=(((["2.50", "1.25"],), "3.75"), ((["2", "3"],), "5.00"),
                (([],), "0.00"), ((["10", "0.5"],), "10.50")),
    ),
    Hunt(
        id="hunt-dart-list-equals",
        title="The same days, never equal",
        family=DART,
        language="dart",
        level=3,
        report="Two calendars both list days [1, 2, 3] - one typed in "
               "another order - and the app says the schedules are "
               "different. Comparing two clearly different schedules is "
               "right.",
        name="sameSchedule",
        params=("a", "b"),
        types=("List<int>", "List<int>"),
        returns="bool",
        start=(
            "List<int> normal(List<int> days) {\n"
            "  final copy = [...days];\n"
            "  copy.sort();\n"
            "  return copy;\n"
            "}\n"
            "\n"
            "bool sameSchedule(List<int> a, List<int> b) {\n"
            "  return normal(a) == normal(b);\n"
            "}\n"
        ),
        fixed=(
            "List<int> normal(List<int> days) {\n"
            "  final copy = [...days];\n"
            "  copy.sort();\n"
            "  return copy;\n"
            "}\n"
            "\n"
            "bool sameSchedule(List<int> a, List<int> b) {\n"
            "  return normal(a).join(',') == normal(b).join(',');\n"
            "}\n"
        ),
        solve=_same_schedule,
        reported=([3, 1, 2], [1, 2, 3]),
        cases=(([3, 1, 2], [1, 2, 3]), ([1, 2], [3]), ([], []), ([5], [5]),
               ([1, 2], [1, 3]), ([4, 4], [4, 4])),
        cause="== on two Lists asks whether they are the very same object, "
              "not whether they hold the same items, and normal builds a "
              "new list every call, so the answer is always false.",
        decoys=(
            "normal sorts the list in place, so a and b end up different "
            "lists.",
            "sort() without a comparator orders numbers as text, so 10 comes "
            "before 2.",
            "== on lists compares only the lengths.",
        ),
        lesson="In Dart a List has no value equality: [1, 2] == [1, 2] is false "
               "unless both sides are the same object. (Records and "
               "strings do compare by value, which is what makes this "
               "surprising.) Compare lengths and then every item, join to "
               "text, or use listEquals from Flutter's foundation library. "
               "It hides on every not-equal comparison, since false was the "
               "right answer anyway.",
        hint="Different schedules come out right. Try two that hold the same "
             "days: sameSchedule([3, 1, 2], [1, 2, 3]).",
        checks=((([3, 1, 2], [1, 2, 3]), True), (([1, 2], [3]), False),
                (([], []), True), (([1, 2], [1, 3]), False)),
    ),
    Hunt(
        id="hunt-dart-reduce-empty",
        title="No sales, no report",
        family=DART,
        language="dart",
        level=3,
        report="On a day with no sales the report page fails with 'Bad state: "
               "No element'. Days with one or more sales show the best sale "
               "correctly.",
        name="report",
        params=("sales",),
        types=("List<int>",),
        returns="String",
        start=(
            "int biggest(List<int> sales) {\n"
            "  return sales.reduce((a, b) => a > b ? a : b);\n"
            "}\n"
            "\n"
            "String report(List<int> sales) {\n"
            "  final top = biggest(sales);\n"
            "  return 'Best sale: $top';\n"
            "}\n"
        ),
        fixed=(
            "int biggest(List<int> sales) {\n"
            "  return sales.isEmpty ? 0 : sales.reduce((a, b) => a > b ? a : b);\n"
            "}\n"
            "\n"
            "String report(List<int> sales) {\n"
            "  final top = biggest(sales);\n"
            "  return 'Best sale: $top';\n"
            "}\n"
        ),
        solve=_report,
        reported=([],),
        cases=(([],), ([3, 9, 4],), ([7],), ([12, 5],), ([2, 2],)),
        cause="reduce has nothing to start from on an empty list, so it throws "
              "a StateError; biggest has to deal with the empty case itself.",
        decoys=(
            "The comparison a > b keeps the smaller number, so the wrong sale "
            "is reported.",
            "reduce skips the first element, so a one-item list has no "
            "answer.",
            "report must check the list is empty before calling anything.",
        ),
        lesson="reduce, first, last, single and max-style helpers all throw a "
               "StateError on an empty collection, because there is no right "
               "answer to give. fold takes a starting value and works on "
               "empty lists; firstOrNull (Dart 3) gives null. The empty "
               "list is the first input a real screen gets - before the data "
               "has loaded.",
        hint="Lists with items work. Try the quietest day: report([]).",
        checks=((([],), "Best sale: 0"), (([3, 9, 4],), "Best sale: 9"),
                (([7],), "Best sale: 7"), (([12, 5],), "Best sale: 12")),
    ),
    Hunt(
        id="hunt-dart-day-zero",
        title="February with 31 days",
        family=DART,
        language="dart",
        level=4,
        report="The month view for February 2026 draws 31 days. January and "
               "August are fine, and so is every other month that happens "
               "to be as long as the one before it.",
        name="lastDay",
        params=("year", "month"),
        types=("int", "int"),
        returns="int",
        start=(
            "DateTime monthEnd(int year, int month) {\n"
            "  return DateTime(year, month, 0);\n"
            "}\n"
            "\n"
            "int lastDay(int year, int month) {\n"
            "  final end = monthEnd(year, month);\n"
            "  return end.day;\n"
            "}\n"
        ),
        fixed=(
            "DateTime monthEnd(int year, int month) {\n"
            "  return DateTime(year, month + 1, 0);\n"
            "}\n"
            "\n"
            "int lastDay(int year, int month) {\n"
            "  final end = monthEnd(year, month);\n"
            "  return end.day;\n"
            "}\n"
        ),
        solve=_last_day,
        reported=(2026, 2),
        cases=((2026, 2), (2024, 2), (2026, 1), (2026, 4), (2026, 8),
               (2026, 12), (2026, 7)),
        cause="Day 0 of a month is the last day of the month before it, so "
              "DateTime(year, month, 0) is the end of the previous month; "
              "the end of this month is day 0 of the next one.",
        decoys=(
            "DateTime days count from 0, so day 0 is the first of the month.",
            "DateTime(year, month, 0) throws for a day of 0, and the app "
            "catches it and shows 31.",
            "end.day gives the day of the week, not of the month.",
        ),
        lesson="Dart's DateTime does not refuse out-of-range parts: it rolls "
               "over. Day 0 is the day before the 1st, month 13 is January of "
               "the next year. That is a handy trick - DateTime(y, m + 1, 0) "
               "is the last day of month m, leap years included - and an easy "
               "off-by-one: forget the + 1 and every month borrows its "
               "neighbour's length. The months that are as long as the one "
               "before them hide it.",
        hint="January and August come out right. Try a month whose "
             "predecessor has a different length: lastDay(2026, 2).",
        checks=(((2026, 2), 28), ((2024, 2), 29), ((2026, 1), 31),
                ((2026, 4), 30), ((2026, 12), 31)),
    ),
)
