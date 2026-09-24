"""Bug hunts in Dart - the language Flutter apps are written in.

Chosen for mistakes that are Dart's own, or that Flutter code runs into
all the time, rather than ports of the Python and JavaScript hunts:

  / then .round()     Dart's / always gives a double; ~/ is the whole-
                      number division that was meant
  ''.split(',')       gives [''], so an empty post has one tag
  List.filled         puts the same list in every slot, so a week
                      planner adds each task to every day
  compareTo           sorts by character code, capitals first
  >= at the limit     a title exactly as long as allowed gets cut

The same rules hold as for the other hunts, and the suite checks them:
the bug is real, it hides on some inputs, the report's own input shows
it, and the fix changes one or two lines in place.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

DART = "Dart"


def _average_stars(ratings: list) -> int:
    return sum(ratings) // len(ratings) if ratings else 0


def _tag_count(text: str) -> int:
    return len([tag for tag in text.split(",") if tag.strip()])


def _plan_week(tasks: list, days: list) -> list:
    week = [[] for _ in range(7)]
    for task, day in zip(tasks, days):
        week[day].append(task)
    return week


def _sorted_names(names: list) -> list:
    return sorted((name.strip() for name in names), key=str.lower)


def _short_title(title: str) -> str:
    return title if len(title) <= 10 else title[:7] + "..."


EMPTY_WEEK = [[], [], [], [], [], [], []]

DART_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-dart-star-average",
        title="Four and five make five",
        family=DART,
        language="dart",
        level=1,
        report="A product with ratings of 4 and 5 shows a 5-star average. The "
               "shop always rounds averages down, so it should say 4.",
        name="averageStars",
        params=("ratings",),
        types=("List<int>",),
        returns="int",
        start=(
            "int total(List<int> ratings) {\n"
            "  var sum = 0;\n"
            "  for (final rating in ratings) {\n"
            "    sum += rating;\n"
            "  }\n"
            "  return sum;\n"
            "}\n"
            "\n"
            "int averageStars(List<int> ratings) {\n"
            "  if (ratings.isEmpty) return 0;\n"
            "  return (total(ratings) / ratings.length).round();\n"
            "}\n"
        ),
        fixed=(
            "int total(List<int> ratings) {\n"
            "  var sum = 0;\n"
            "  for (final rating in ratings) {\n"
            "    sum += rating;\n"
            "  }\n"
            "  return sum;\n"
            "}\n"
            "\n"
            "int averageStars(List<int> ratings) {\n"
            "  if (ratings.isEmpty) return 0;\n"
            "  return total(ratings) ~/ ratings.length;\n"
            "}\n"
        ),
        solve=_average_stars,
        reported=([4, 5],),
        cases=(([],), ([4, 5],), ([3, 3, 3],), ([1, 2],), ([5],), ([4, 4, 5],)),
        cause="averageStars divides with / and then rounds to the nearest "
              "whole number, so an average of 4.5 or more goes up.",
        decoys=(
            "total skips the last rating in the list.",
            "/ divides as whole numbers in Dart and throws the fraction away.",
            "The isEmpty check is the wrong way round.",
        ),
        lesson="In Dart, / always gives a double, and .round() goes to the "
               "nearest whole number. ~/ divides and drops the fraction - the "
               "whole-number division Python spells //.",
        hint="Try two ratings whose average is exactly a half: "
             "averageStars([4, 5]).",
        checks=((([4, 5],), 4), (([],), 0), (([1, 2],), 1), (([4, 4, 5],), 4)),
    ),
    Hunt(
        id="hunt-dart-empty-tags",
        title="No tags, one tag",
        family=DART,
        language="dart",
        level=1,
        report="A post with no tags at all says it has 1 tag.",
        name="tagCount",
        params=("text",),
        types=("String",),
        returns="int",
        start=(
            "List<String> tagsOf(String text) {\n"
            "  return text\n"
            "      .split(',')\n"
            "      .map((tag) => tag.trim())\n"
            "      .toList();\n"
            "}\n"
            "\n"
            "int tagCount(String text) {\n"
            "  final tags = tagsOf(text);\n"
            "  return tags.length;\n"
            "}\n"
        ),
        fixed=(
            "List<String> tagsOf(String text) {\n"
            "  return text\n"
            "      .split(',')\n"
            "      .map((tag) => tag.trim()).where((tag) => tag.isNotEmpty)\n"
            "      .toList();\n"
            "}\n"
            "\n"
            "int tagCount(String text) {\n"
            "  final tags = tagsOf(text);\n"
            "  return tags.length;\n"
            "}\n"
        ),
        solve=_tag_count,
        reported=("",),
        cases=(("",), ("flutter",), ("dart, flutter",), ("a,,b",),
               ("dart, flutter, ",)),
        cause="Splitting an empty string gives a list holding one empty "
              "string, and nothing throws the empty tags away.",
        decoys=(
            "tags.length counts from 0, so it is always one too high.",
            "trim() adds a space to each tag.",
            "split(',') drops the first tag.",
        ),
        lesson="''.split(',') is [''] - one empty string, not an empty list. "
               "Python and JavaScript do exactly the same. Filtering out the "
               "empty ones after the split fixes the empty post and the "
               "doubled comma in one go.",
        hint="What does a post with no tags send? tagCount(\"\").",
        checks=((("",), 0), (("a,,b",), 2), (("dart, flutter, ",), 2)),
    ),
    Hunt(
        id="hunt-dart-shared-days",
        title="Gym every day",
        family=DART,
        language="dart",
        level=2,
        report="I planned 'gym' for Monday - day 0 - and the planner shows gym "
               "on every day of the week.",
        name="planWeek",
        params=("tasks", "days"),
        types=("List<String>", "List<int>"),
        returns="List<List<String>>",
        start=(
            "List<List<String>> emptyWeek() {\n"
            "  return List.filled(7, <String>[]);\n"
            "}\n"
            "\n"
            "List<List<String>> planWeek(List<String> tasks, List<int> days) {\n"
            "  final week = emptyWeek();\n"
            "  for (var i = 0; i < tasks.length; i++) {\n"
            "    week[days[i]].add(tasks[i]);\n"
            "  }\n"
            "  return week;\n"
            "}\n"
        ),
        fixed=(
            "List<List<String>> emptyWeek() {\n"
            "  return List.generate(7, (_) => <String>[]);\n"
            "}\n"
            "\n"
            "List<List<String>> planWeek(List<String> tasks, List<int> days) {\n"
            "  final week = emptyWeek();\n"
            "  for (var i = 0; i < tasks.length; i++) {\n"
            "    week[days[i]].add(tasks[i]);\n"
            "  }\n"
            "  return week;\n"
            "}\n"
        ),
        solve=_plan_week,
        reported=(["gym"], [0]),
        cases=(([], []), (["gym"], [0]), (["read", "cook"], [2, 5]),
               (["a", "b", "c"], [6, 6, 0])),
        cause="List.filled puts the very same list in all seven slots, so "
              "adding a task to one day adds it to every day.",
        decoys=(
            "days count from 1, so Monday should be day 1.",
            "The loop adds each task seven times.",
            "List.filled makes a list that cannot grow, so add is ignored.",
        ),
        lesson="List.filled(n, value) uses that one value for every slot. "
               "For a number that is fine; for a list, all seven slots are "
               "one list. List.generate calls its function once per slot, so "
               "each day gets its own. It turns up in Flutter state a lot.",
        hint="Plan one task and look at the other days: "
             "planWeek([\"gym\"], [0]).",
        checks=(((["gym"], [0]), [["gym"], [], [], [], [], [], []]),
                (([], []), EMPTY_WEEK),
                ((["read", "cook"], [2, 5]), [[], [], ["read"], [], [], ["cook"], []])),
    ),
    Hunt(
        id="hunt-dart-sort-names",
        title="Zoe before adam",
        family=DART,
        language="dart",
        level=2,
        report="The contacts screen lists 'Zoe' above 'adam'. Names should be "
               "in alphabetical order whatever the capitals.",
        name="sortedNames",
        params=("names",),
        types=("List<String>",),
        returns="List<String>",
        start=(
            "List<String> tidy(List<String> names) {\n"
            "  return names.map((name) => name.trim()).toList();\n"
            "}\n"
            "\n"
            "List<String> sortedNames(List<String> names) {\n"
            "  final result = tidy(names);\n"
            "  result.sort((a, b) => a.compareTo(b));\n"
            "  return result;\n"
            "}\n"
        ),
        fixed=(
            "List<String> tidy(List<String> names) {\n"
            "  return names.map((name) => name.trim()).toList();\n"
            "}\n"
            "\n"
            "List<String> sortedNames(List<String> names) {\n"
            "  final result = tidy(names);\n"
            "  result.sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));\n"
            "  return result;\n"
            "}\n"
        ),
        solve=_sorted_names,
        reported=(["adam", "Zoe"],),
        cases=(([],), (["adam", "Zoe"],), (["bea", "al"],), (["Cy", "Al", "Bo"],),
               ([" dan", "Eve", "carl"],)),
        cause="compareTo orders by character code, and every capital letter "
              "comes before every lowercase one.",
        decoys=(
            "tidy trims the names, which changes their order.",
            "sort() sorts backwards unless it is told otherwise.",
            "compareTo gives true or false instead of a number.",
        ),
        lesson="String.compareTo compares character codes: 'Z' is 90 and 'a' "
               "is 97, so Zoe sorts before adam. Comparing lowercase copies "
               "sorts the way people read. Python and JavaScript sort the "
               "same way by default.",
        hint="Mix capitals and small letters: sortedNames([\"adam\", \"Zoe\"]).",
        checks=(((["adam", "Zoe"],), ["adam", "Zoe"]),
                (([" dan", "Eve", "carl"],), ["carl", "dan", "Eve"]),
                (([],), [])),
    ),
    Hunt(
        id="hunt-dart-short-title",
        title="It fits, but it's cut",
        family=DART,
        language="dart",
        level=3,
        report="The app bar cuts titles longer than 10 characters. 'Flutter UI' "
               "is exactly 10, and it comes out as 'Flutter...'.",
        name="shortTitle",
        params=("title",),
        types=("String",),
        returns="String",
        start=(
            "const maxLength = 10;\n"
            "\n"
            "bool tooLong(String title) {\n"
            "  return title.length >= maxLength;\n"
            "}\n"
            "\n"
            "String shortTitle(String title) {\n"
            "  if (!tooLong(title)) return title;\n"
            "  return '${title.substring(0, maxLength - 3)}...';\n"
            "}\n"
        ),
        fixed=(
            "const maxLength = 10;\n"
            "\n"
            "bool tooLong(String title) {\n"
            "  return title.length > maxLength;\n"
            "}\n"
            "\n"
            "String shortTitle(String title) {\n"
            "  if (!tooLong(title)) return title;\n"
            "  return '${title.substring(0, maxLength - 3)}...';\n"
            "}\n"
        ),
        solve=_short_title,
        reported=("Flutter UI",),
        cases=(("Dart",), ("Flutter UI",), ("Hello world!",), ("",),
               ("abcdefghij",)),
        cause="tooLong uses >=, so a title exactly the maximum length counts "
              "as too long.",
        decoys=(
            "substring includes its end index, so it keeps one character too many.",
            "maxLength should be 11, because lengths count from 0.",
            "shortTitle adds '...' to short titles as well.",
        ),
        lesson="Length checks break at the boundary. 'Longer than 10' is "
               "> 10. The input worth trying is the one exactly at the limit - "
               "it is the only one where > and >= disagree.",
        hint="Try a title exactly as long as the limit: "
             "shortTitle(\"Flutter UI\").",
        checks=((("Flutter UI",), "Flutter UI"), (("Hello world!",), "Hello w..."),
                (("",), "")),
    ),
)
