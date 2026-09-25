"""Fix the bug, in Dart: six more, from the same Flutter screens.

The rules are the ones in `dart_bugs.py`: every start compiles and runs,
every start passes some of its cases and fails others, and the bug is
one Dart or Flutter code really runs into:

  the boundary          `<=` where the last page is exactly full
  the unused result     `input.trim();` - Strings never change in place
  the missing pad       '1:5' on a timer, where padLeft makes '1:05'
  the end of the list   sublist(length - n) when n is more than there are
  the JSON number       `as double` on a price that arrived as 4
  the identity check    `==` on two Lists asks if they are the same list

The expected answers come from the Python oracle, as for every kata.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Fix the bug: Dart"


def _has_next_page(page: int, per_page: int, total: int) -> bool:
    return page * per_page < total


def _normalize_email(text: str) -> str:
    return text.strip().lower()


def _format_timer(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def _recent_messages(messages: list, n: int) -> list:
    return messages[max(0, len(messages) - n):]


def _order_total(items: list) -> float:
    total = 0.0
    for item in items:
        total += item["price"] * item["qty"]
    return total


def _has_unsaved_changes(saved: list, edited: list) -> bool:
    return saved != edited


DART_BUGS_2: tuple[Kata, ...] = (
    Kata(
        id="dart-bug-has-next-page",
        level=1,
        name="hasNextPage",
        brief=(
            "An infinite-scroll list loads perPage items a page. Pages "
            "count from 1. Given the page just loaded and the total number "
            "of items on the server, say whether there is another page to "
            "fetch."
        ),
        params=("page", "perPage", "total"),
        types=("int", "int", "int"),
        returns="bool",
        family=FAMILY,
        language="dart",
        example="hasNextPage(1, 10, 25) is true, and hasNextPage(2, 10, 20) "
                "is false: both pages were full and nothing is left",
        hint="Try 20 items at 10 a page, on page 2. How many are shown, and "
             "how many are still on the server?",
        cases=(
            (1, 10, 25), (3, 10, 25), (2, 10, 20), (1, 10, 0), (1, 10, 10),
            (1, 1, 1), (2, 5, 11), (1, 20, 19), (4, 25, 100), (4, 25, 101),
        ),
        solve=_has_next_page,
        checks=(((1, 10, 25), True), ((2, 10, 20), False), ((1, 10, 0), False),
                ((1, 10, 10), False), ((4, 25, 101), True)),
        start=(
            "bool hasNextPage(int page, int perPage, int total) {\n"
            "  final shown = page * perPage;\n"
            "  // Keep fetching until we have shown past the end.\n"
            "  return shown <= total;\n"
            "}"
        ),
        bug="When the pages come out exactly full, shown equals total and "
            "everything is already on screen - but `<=` still says there is "
            "more, so the list fires one more request and gets back an "
            "empty page. There is more only while shown is strictly less "
            "than total.",
        dart_answer=(
            "bool hasNextPage(int page, int perPage, int total) {\n"
            "  final shown = page * perPage;\n"
            "  // More only while something is still left on the server.\n"
            "  return shown < total;\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-normalize-email",
        level=1,
        name="normalizeEmail",
        brief=(
            "Tidy what was typed into an email field before it is sent to "
            "the server: no spaces around it, and all lower case."
        ),
        params=("input",),
        types=("String",),
        returns="String",
        family=FAMILY,
        language="dart",
        example="normalizeEmail('  Ada@Example.com ') is 'ada@example.com'",
        hint="What does input.trim() give back - and where does that go?",
        cases=(
            ("ada@example.com",), ("  Ada@Example.com ",), ("",), ("a",),
            ("BOB@MAIL.COM",), ("x@y.io",), (" grace@navy.mil",),
            ("Linus@Kernel.org",), ("tim@web.dev  ",), ("m@h.io",),
        ),
        solve=_normalize_email,
        checks=((("  Ada@Example.com ",), "ada@example.com"), (("",), ""),
                (("BOB@MAIL.COM",), "bob@mail.com"),
                (("x@y.io",), "x@y.io")),
        start=(
            "String normalizeEmail(String input) {\n"
            "  // No spaces around it, all lower case.\n"
            "  input.trim();\n"
            "  input.toLowerCase();\n"
            "  return input;\n"
            "}"
        ),
        bug="A Dart String never changes: trim() and toLowerCase() each "
            "hand back a new String, and here both new Strings were thrown "
            "away, so the input came back exactly as typed. Keep the "
            "result - `return input.trim().toLowerCase();`.",
        dart_answer=(
            "String normalizeEmail(String input) {\n"
            "  // No spaces around it, all lower case.\n"
            "  return input.trim().toLowerCase();\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-format-timer",
        level=2,
        name="formatTimer",
        brief=(
            "Show a countdown timer's seconds as minutes and seconds, "
            "'m:ss', the way a workout or cooking timer does. The seconds "
            "always have two digits."
        ),
        params=("seconds",),
        types=("int",),
        returns="String",
        family=FAMILY,
        language="dart",
        example="formatTimer(75) is '1:15', and formatTimer(65) is '1:05'",
        hint="Look at the timer with 65 seconds left. How many digits does "
             "an int print when it is less than 10?",
        cases=(
            (75,), (65,), (0,), (600,), (59,), (3599,), (9,), (1,), (130,),
            (61,),
        ),
        solve=_format_timer,
        checks=(((75,), "1:15"), ((65,), "1:05"), ((0,), "0:00"),
                ((600,), "10:00"), ((3599,), "59:59")),
        start=(
            "String formatTimer(int seconds) {\n"
            "  return '${seconds ~/ 60}:${seconds % 60}';\n"
            "}"
        ),
        bug="An int prints only the digits it needs, so 5 seconds came out "
            "as '5' and the timer read '1:5'. Turn it into a String and pad "
            "it: `(seconds % 60).toString().padLeft(2, '0')` puts a 0 in "
            "front until it is two characters long.",
        dart_answer=(
            "String formatTimer(int seconds) {\n"
            "  final secs = (seconds % 60).toString().padLeft(2, '0');\n"
            "  return '${seconds ~/ 60}:$secs';\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-recent-messages",
        level=3,
        name="recentMessages",
        brief=(
            "A chat preview shows the last n messages, oldest first. When "
            "there are fewer than n, it shows all of them."
        ),
        params=("messages", "n"),
        types=("List<String>", "int"),
        returns="List<String>",
        family=FAMILY,
        language="dart",
        example="recentMessages(['a', 'b', 'c'], 2) is ['b', 'c'], and "
                "recentMessages(['hi'], 5) is ['hi']",
        hint="Try a chat with one message and ask for the last five. What "
             "start index does sublist get?",
        cases=(
            (["a", "b", "c"], 2), ([], 3), (["hi"], 1), (["hi"], 5),
            (["a", "b", "c"], 0), (["a", "b", "c"], 3), (["a", "b"], 10),
            (["see you", "ok", "on my way", "here"], 1),
            (["one", "two", "three", "four", "five"], 3), ([], 0),
        ),
        solve=_recent_messages,
        checks=(((["a", "b", "c"], 2), ["b", "c"]), (([], 3), []),
                ((["hi"], 5), ["hi"]), ((["a", "b", "c"], 0), []),
                ((["a", "b"], 10), ["a", "b"])),
        start=(
            "List<String> recentMessages(List<String> messages, int n) {\n"
            "  return messages.sublist(messages.length - n);\n"
            "}"
        ),
        bug="When the chat has fewer than n messages, length - n is "
            "negative, and sublist does not clamp it the way Python's "
            "slices do - it throws a RangeError. Work out the start first "
            "and keep it at 0 or more.",
        dart_answer=(
            "List<String> recentMessages(List<String> messages, int n) {\n"
            "  final start = n < messages.length ? messages.length - n : 0;\n"
            "  return messages.sublist(start);\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-order-total",
        level=4,
        name="orderTotal",
        brief=(
            "Add up an order decoded from JSON: each item is a map with a "
            "'price' in dollars and a 'qty'. The API sends prices as plain "
            "JSON numbers, so a whole-dollar price arrives as 4, not 4.0."
        ),
        params=("items",),
        types=("List<Map<String, dynamic>>",),
        returns="double",
        family=FAMILY,
        language="dart",
        example="orderTotal([{'price': 2.5, 'qty': 2}, {'price': 4, 'qty': 1}]) "
                "is 9.0",
        hint="jsonDecode('4') and jsonDecode('4.5') give back different "
             "types. What happens when you write `as double` on the first?",
        cases=(
            ([{"price": 2.5, "qty": 2}, {"price": 4, "qty": 1}],),
            ([],),
            ([{"price": 1.25, "qty": 4}],),
            ([{"price": 3, "qty": 2}],),
            ([{"price": 0.5, "qty": 3}, {"price": 9.75, "qty": 1}],),
            ([{"price": 10, "qty": 1}, {"price": 20, "qty": 1}],),
            ([{"price": 7.5, "qty": 0}],),
            ([{"price": 12.25, "qty": 2}, {"price": 0.75, "qty": 4}],),
        ),
        solve=_order_total,
        checks=(
            (([{"price": 2.5, "qty": 2}, {"price": 4, "qty": 1}],), 9.0),
            (([],), 0.0),
            (([{"price": 3, "qty": 2}],), 6.0),
            (([{"price": 1.25, "qty": 4}],), 5.0),
        ),
        start=(
            "double orderTotal(List<Map<String, dynamic>> items) {\n"
            "  var total = 0.0;\n"
            "  for (final item in items) {\n"
            "    final price = item['price'] as double;\n"
            "    final qty = item['qty'] as int;\n"
            "    total += price * qty;\n"
            "  }\n"
            "  return total;\n"
            "}"
        ),
        bug="JSON has one kind of number, and jsonDecode gives back an int "
            "when there is no decimal point - so a price of 4 is an int, "
            "and `as double` throws a TypeError. Cast to num, which both "
            "are, and convert: `(item['price'] as num).toDouble()`. Model "
            "classes written with fromJson need the same care.",
        dart_answer=(
            "double orderTotal(List<Map<String, dynamic>> items) {\n"
            "  var total = 0.0;\n"
            "  for (final item in items) {\n"
            "    final price = (item['price'] as num).toDouble();\n"
            "    final qty = item['qty'] as int;\n"
            "    total += price * qty;\n"
            "  }\n"
            "  return total;\n"
            "}"
        ),
    ),
    Kata(
        id="dart-bug-has-unsaved-changes",
        level=5,
        name="hasUnsavedChanges",
        brief=(
            "A profile form lets you pick interest tags. The Save button "
            "should light up only when the tags, in order, differ from the "
            "ones that were saved."
        ),
        params=("saved", "edited"),
        types=("List<String>", "List<String>"),
        returns="bool",
        family=FAMILY,
        language="dart",
        example="hasUnsavedChanges(['dart'], ['dart', 'ui']) is true, and "
                "hasUnsavedChanges(['dart'], ['dart']) is false",
        hint="Every answer where the tags differ is right. In Dart, what "
             "does == ask about two List objects?",
        cases=(
            (["dart"], ["dart", "ui"]), ([], []), (["a"], ["a"]),
            (["a"], ["b"]), (["a", "b"], ["b", "a"]), (["x"], []),
            (["dart", "flutter"], ["dart", "flutter"]),
            ([], ["new"]), (["ui", "state", "async"], ["ui", "state", "async"]),
            (["ui", "state"], ["ui", "State"]),
        ),
        solve=_has_unsaved_changes,
        checks=(((["dart"], ["dart", "ui"]), True), (([], []), False),
                ((["a"], ["a"]), False), ((["a", "b"], ["b", "a"]), True),
                ((["ui", "state"], ["ui", "State"]), True)),
        start=(
            "bool hasUnsavedChanges(List<String> saved, List<String> edited) {\n"
            "  return edited != saved;\n"
            "}"
        ),
        bug="For Lists, == asks whether both sides are the same list "
            "object, not whether they hold the same things - and the form's "
            "copy is never the saved list itself, so Save was always lit. "
            "Compare the lengths, then each element. Flutter's foundation "
            "library has listEquals for exactly this.",
        dart_answer=(
            "bool hasUnsavedChanges(List<String> saved, List<String> edited) {\n"
            "  if (saved.length != edited.length) return true;\n"
            "  for (var i = 0; i < saved.length; i++) {\n"
            "    if (saved[i] != edited[i]) return true;\n"
            "  }\n"
            "  return false;\n"
            "}"
        ),
    ),
)
