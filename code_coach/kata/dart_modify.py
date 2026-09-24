"""Change it: Dart - working Flutter-shaped code, and a change request.

The same exercise as the Python and JavaScript drills in `modify.py`,
under the same four rules, and the suite checks all four here too: the
start passes every case under the old requirement (`before`), it fails
the new one (`solve`), some cases keep their answer so a rewrite that
breaks what worked fails, and the model answer (`after`) is a few lines
from the start.

What is different is the kind of change. These are the tickets a
Flutter app actually gets in its first months: the cart badge says
'1 items', the price shows '$3.5', the tag cloud counts 'Flutter' and
'flutter' twice, tied players swap places between screens. Each one is a
small edit to code that was fine yesterday, and each one leans on a
piece of Dart worth knowing - an expression inside interpolation,
toStringAsFixed, where(), a validator that returns null, a map read with
??, a comparator that asks a second question.

The oracles are Python for the reason every kata gives: the answers are
strings, numbers, lists, maps and null, which mean the same in both
languages. Every Dart string here - the start and the answer - is
compiled and run against them.
"""

from __future__ import annotations

from code_coach.kata import Kata

DART = "Change it: Dart"


def _cart_label_before(count: int) -> str:
    return f"{count} items"


def _cart_label(count: int) -> str:
    return f"{count} item" if count == 1 else f"{count} items"


def _price_tag_before(cents: int) -> str:
    # A Dart double prints the shortest digits that name it, and so does
    # Python's, so str() here is what '${cents / 100}' gives there.
    return "$" + str(cents / 100)


def _price_tag(cents: int) -> str:
    return "$" + f"{cents / 100:.2f}"


def _visible_files_before(names: list) -> list:
    return [n for n in names if not n.startswith(".")]


def _visible_files(names: list) -> list:
    return [n for n in names if not n.startswith(".") and not n.endswith(".tmp")]


def _password_error_before(password: str):
    if password == "":
        return "Enter a password"
    if len(password) < 8:
        return "Use at least 8 characters"
    return None


def _password_error(password: str):
    if password == "":
        return "Enter a password"
    if len(password) < 8:
        return "Use at least 8 characters"
    if not any(ch in "0123456789" for ch in password):
        return "Add at least one number"
    return None


def _tag_counts_before(tags: list) -> dict:
    counts: dict = {}
    for tag in tags:
        counts[tag] = counts.get(tag, 0) + 1
    return counts


def _tag_counts(tags: list) -> dict:
    counts: dict = {}
    for tag in tags:
        key = tag.lower()
        counts[key] = counts.get(key, 0) + 1
    return counts


def _leaderboard_before(scores: dict) -> list:
    # Ties stay in the order they were added. Python's sort promises
    # that; Dart's does not, but on a list this short it keeps them too -
    # which is exactly the kind of order nobody should lean on.
    return sorted(scores, key=lambda name: -scores[name])


def _leaderboard(scores: dict) -> list:
    return sorted(scores, key=lambda name: (-scores[name], name))


DART_MODIFY: tuple[Kata, ...] = (
    Kata(
        id="dart-change-cart-label",
        name="cartLabel",
        family=DART,
        language="dart",
        level=1,
        params=("count",),
        types=("int",),
        returns="String",
        was="It labels the cart badge with how many things are in it: "
            "cartLabel(3) is '3 items'.",
        brief="The badge says '1 items' and a customer has sent a "
              "screenshot. When there is exactly one, it should say "
              "'1 item'. Every other count stays as it is.",
        example="cartLabel(1) → '1 item'   cartLabel(0) → '0 items'   "
                "cartLabel(2) → '2 items'",
        hint="Only one number is singular. What does English do with 0, "
             "and with 21?",
        change="A conditional expression can go straight inside the "
               "interpolation: ${count == 1 ? 'item' : 'items'}. The test "
               "is exactly 1 - English says '0 items' and '21 items' - and "
               "a real app with more than one language would hand this to "
               "the intl package, because other languages disagree.",
        cases=((0,), (1,), (2,), (11,), (21,), (100,)),
        before=_cart_label_before,
        solve=_cart_label,
        start=(
            "String cartLabel(int count) {\n"
            "  return '$count items';\n"
            "}\n"
        ),
        after=(
            "String cartLabel(int count) {\n"
            "  return '$count ${count == 1 ? 'item' : 'items'}';\n"
            "}\n"
        ),
        checks=(((1,), "1 item"), ((0,), "0 items"), ((21,), "21 items")),
    ),
    Kata(
        id="dart-change-price-tag",
        name="priceTag",
        family=DART,
        language="dart",
        level=1,
        params=("cents",),
        types=("int",),
        returns="String",
        was="It turns a price in cents into dollars by dividing by 100: "
            "priceTag(1999) is '$19.99' - and priceTag(350) is '$3.5'.",
        brief="Design wants every price with exactly two decimals, the way "
              "a receipt prints them: 350 should be '$3.50' and 1200 "
              "should be '$12.00'.",
        example="priceTag(350) → '$3.50'   priceTag(1200) → '$12.00'   "
                "priceTag(1999) → '$19.99'",
        hint="A double prints as few digits as it needs. Dart numbers have "
             "a method that prints a fixed number of decimals instead.",
        change="toStringAsFixed(2) turns the number into a String with "
               "exactly two decimals, so it wraps the division inside the "
               "interpolation. A plain double prints the shortest digits "
               "that name it, which is why 3.5 lost its zero - and why "
               "19.99 already looked right and hid the problem.",
        cases=((1999,), (350,), (1200,), (0,), (5,), (1,), (10,), (1234,)),
        before=_price_tag_before,
        solve=_price_tag,
        start=(
            "String priceTag(int cents) {\n"
            "  return '\\$${cents / 100}';\n"
            "}\n"
        ),
        after=(
            "String priceTag(int cents) {\n"
            "  return '\\$${(cents / 100).toStringAsFixed(2)}';\n"
            "}\n"
        ),
        checks=(((350,), "$3.50"), ((1200,), "$12.00"), ((0,), "$0.00"),
                ((5,), "$0.05"), ((1999,), "$19.99")),
    ),
    Kata(
        id="dart-change-visible-files",
        name="visibleFiles",
        family=DART,
        language="dart",
        level=2,
        params=("names",),
        types=("List<String>",),
        returns="List<String>",
        was="The file picker hides dotfiles - any name starting with '.', "
            "like '.env' or '.git' - and lists everything else in order.",
        brief="Editors leave temporary files behind and people keep tapping "
              "them. Hide any name ending in '.tmp' too, as well as the "
              "dotfiles.",
        example="visibleFiles(['a.dart', '.git', 'b.tmp']) → ['a.dart']",
        hint="The where() test already says what to keep. What else has to "
             "be true of a name for it to stay?",
        change="where() keeps the names its test is true for, so a new "
               "exclusion is one more condition that must also hold, joined "
               "with &&. endsWith and not contains: 'notes.tmp.txt' is a "
               "text file, and it stays.",
        cases=(([],), ([".env"],), (["main.dart"],),
               (["a.dart", ".git", "b.tmp"],), (["notes.tmp.txt"],),
               ([".cache.tmp", "pubspec.yaml"],),
               (["build.tmp", "README.md", ".gitignore", "draft.tmp"],),
               (["tmp"],)),
        before=_visible_files_before,
        solve=_visible_files,
        start=(
            "List<String> visibleFiles(List<String> names) {\n"
            "  return names.where((name) => !name.startsWith('.')).toList();\n"
            "}\n"
        ),
        after=(
            "List<String> visibleFiles(List<String> names) {\n"
            "  return names\n"
            "      .where((name) => !name.startsWith('.') && !name.endsWith('.tmp'))\n"
            "      .toList();\n"
            "}\n"
        ),
        checks=(((["a.dart", ".git", "b.tmp"],), ["a.dart"]),
                ((["notes.tmp.txt"],), ["notes.tmp.txt"]),
                ((["build.tmp", "README.md", ".gitignore", "draft.tmp"],),
                 ["README.md"]),
                (([],), [])),
    ),
    Kata(
        id="dart-change-password-error",
        name="passwordError",
        family=DART,
        language="dart",
        level=2,
        params=("password",),
        types=("String",),
        returns="String?",
        was="It is the validator on the sign-up form's password field: it "
            "returns a message when something is wrong and null when the "
            "password is fine. Today it checks that there is one and that "
            "it is at least 8 characters long.",
        brief="Security wants a number in every password. After the checks "
              "that are already there, a password with no digit in it "
              "should get 'Add at least one number'.",
        example="passwordError('abcdefgh') → 'Add at least one number'   "
                "passwordError('abcdefg1') → null",
        hint="A validator answers with the first problem it finds. Where "
             "does the new question go so that a short password still "
             "hears about its length first?",
        change="One new line, between the last check and return null. The "
               "order is the rule: the form shows one message at a time, so "
               "'short1' still hears 'Use at least 8 characters', and the "
               "digit check only speaks to passwords that got past the "
               "others. Returning null is how a Flutter validator says "
               "'fine', which is why the return type is String? and not "
               "String.",
        cases=(("",), ("a",), ("short1",), ("abcdefgh",), ("abcdefg1",),
               ("12345678",), ("correct horse",), ("Tr0ub4dor",)),
        before=_password_error_before,
        solve=_password_error,
        start=(
            "String? passwordError(String password) {\n"
            "  if (password.isEmpty) return 'Enter a password';\n"
            "  if (password.length < 8) return 'Use at least 8 characters';\n"
            "  return null;\n"
            "}\n"
        ),
        after=(
            "String? passwordError(String password) {\n"
            "  if (password.isEmpty) return 'Enter a password';\n"
            "  if (password.length < 8) return 'Use at least 8 characters';\n"
            "  if (!password.contains(RegExp(r'[0-9]'))) {\n"
            "    return 'Add at least one number';\n"
            "  }\n"
            "  return null;\n"
            "}\n"
        ),
        checks=((("abcdefgh",), "Add at least one number"),
                (("abcdefg1",), None),
                (("short1",), "Use at least 8 characters"),
                (("",), "Enter a password"),
                (("correct horse",), "Add at least one number")),
    ),
    Kata(
        id="dart-change-tag-counts",
        name="tagCounts",
        family=DART,
        language="dart",
        level=3,
        params=("tags",),
        types=("List<String>",),
        returns="Map<String, int>",
        was="It counts how many times each tag appears across a user's "
            "posts, keyed by the tag exactly as it was typed.",
        brief="The tag cloud shows 'Flutter' and 'flutter' as two different "
              "tags. Count tags without caring about case, and key each one "
              "in lower case.",
        example="tagCounts(['Dart', 'dart', 'UI']) → {'dart': 2, 'ui': 1}",
        hint="The key is used twice on the counting line - read on the "
             "right of the =, written on the left. Decide it once, before "
             "either.",
        change="The lower-cased key goes in a variable and is used on both "
               "sides. Lower-case only the one being written and "
               "['dart', 'Dart'] reads the count for 'Dart', finds null, and "
               "writes 1 over the 1 already there.",
        cases=(([],), (["dart"],), (["Flutter"],),
               (["dart", "flutter", "dart"],), (["dart", "Dart"],),
               (["UI", "ui", "Ui"],), (["state", "State", "widget"],),
               (["a", "b", "A", "c"],)),
        before=_tag_counts_before,
        solve=_tag_counts,
        start=(
            "Map<String, int> tagCounts(List<String> tags) {\n"
            "  final counts = <String, int>{};\n"
            "  for (final tag in tags) {\n"
            "    counts[tag] = (counts[tag] ?? 0) + 1;\n"
            "  }\n"
            "  return counts;\n"
            "}\n"
        ),
        after=(
            "Map<String, int> tagCounts(List<String> tags) {\n"
            "  final counts = <String, int>{};\n"
            "  for (final tag in tags) {\n"
            "    final key = tag.toLowerCase();\n"
            "    counts[key] = (counts[key] ?? 0) + 1;\n"
            "  }\n"
            "  return counts;\n"
            "}\n"
        ),
        checks=(((["dart", "Dart"],), {"dart": 2}),
                ((["UI", "ui", "Ui"],), {"ui": 3}),
                (([],), {}),
                ((["Flutter"],), {"flutter": 1}),
                ((["state", "State", "widget"],), {"state": 2, "widget": 1})),
    ),
    Kata(
        id="dart-change-leaderboard",
        name="leaderboard",
        family=DART,
        language="dart",
        level=4,
        params=("scores",),
        types=("Map<String, int>",),
        returns="List<String>",
        was="It lists the players from highest score to lowest. Players on "
            "the same score come out in whatever order the sort leaves "
            "them - today, the order they joined.",
        brief="Players on the same score keep swapping places between "
              "screens, and they have noticed. When scores tie, put those "
              "names in alphabetical order.",
        example="leaderboard({'max': 4, 'ada': 4, 'bo': 9}) → "
                "['bo', 'ada', 'max']",
        hint="A compare function can ask a second question when the first "
             "one comes out equal - and equal is 0.",
        change="The comparator asks two questions in order: score first, "
               "and only when that gives 0 - a tie - the names. Dart's sort "
               "does not promise to keep tied items in their old order, so "
               "the order before was one nobody wrote down and nobody could "
               "rely on; the tie-break makes it a rule. Players with "
               "different scores come out exactly where they did.",
        cases=(({},), ({"zoe": 7},), ({"ann": 3, "bo": 5},),
               ({"max": 4, "ada": 4},), ({"cy": 2, "bea": 9, "al": 2},),
               ({"kim": 0, "lee": -1, "jo": 0},), ({"a": 1, "b": 1, "c": 1},),
               ({"dan": 10, "eve": 20, "fay": 30},)),
        before=_leaderboard_before,
        solve=_leaderboard,
        start=(
            "List<String> leaderboard(Map<String, int> scores) {\n"
            "  final names = scores.keys.toList();\n"
            "  names.sort((a, b) => scores[b]!.compareTo(scores[a]!));\n"
            "  return names;\n"
            "}\n"
        ),
        after=(
            "List<String> leaderboard(Map<String, int> scores) {\n"
            "  final names = scores.keys.toList();\n"
            "  names.sort((a, b) {\n"
            "    final byScore = scores[b]!.compareTo(scores[a]!);\n"
            "    if (byScore != 0) return byScore;\n"
            "    return a.compareTo(b);\n"
            "  });\n"
            "  return names;\n"
            "}\n"
        ),
        checks=((({"max": 4, "ada": 4},), ["ada", "max"]),
                (({"cy": 2, "bea": 9, "al": 2},), ["bea", "al", "cy"]),
                (({"kim": 0, "lee": -1, "jo": 0},), ["jo", "kim", "lee"]),
                (({},), []),
                (({"dan": 10, "eve": 20, "fay": 30},), ["fay", "eve", "dan"])),
    ),
)
