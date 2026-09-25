"""Change it: Dart - six more tickets for working Flutter-shaped code.

The same four rules as `dart_modify.py`: the start passes every case
under the old requirement (`before`) and fails the new one (`solve`),
some cases keep their answer, and the model answer (`after`) is a few
lines from the start.

The tickets: the badge that should cap at '99+', the list tile that
should prefer a phone number, the avatar that wants two initials, the
timer that needs hours, the checkout that adds delivery, and the search
box that should match words in any order.
"""

from __future__ import annotations

from code_coach.kata import Kata

DART = "Change it: Dart"


def _badge_text_before(unread: int) -> str:
    return str(unread)


def _badge_text(unread: int) -> str:
    return "99+" if unread > 99 else str(unread)


def _contact_subtitle_before(contact: dict) -> str:
    return contact["email"]


def _contact_subtitle(contact: dict) -> str:
    phone = contact.get("phone")
    return phone if phone is not None else contact["email"]


def _avatar_initials_before(full_name: str) -> str:
    return full_name.strip().split(" ")[0][0].upper()


def _avatar_initials(full_name: str) -> str:
    words = full_name.strip().split(" ")
    last = words[-1][0] if len(words) > 1 else ""
    return (words[0][0] + last).upper()


def _format_duration_before(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def _format_duration(seconds: int) -> str:
    hours, minutes = seconds // 3600, seconds % 3600 // 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds % 60:02d}"
    return f"{minutes}:{seconds % 60:02d}"


def _checkout_total_before(items: list) -> int:
    return sum(item["price"] * item["qty"] for item in items)


def _checkout_total(items: list) -> int:
    total = _checkout_total_before(items)
    if 0 < total < 5000:
        total += 499
    return total


def _search_products_before(names: list, query: str) -> list:
    q = query.lower()
    return [n for n in names if q in n.lower()]


def _search_products(names: list, query: str) -> list:
    words = query.lower().split(" ")
    return [n for n in names if all(w in n.lower() for w in words)]


DART_MODIFY_2: tuple[Kata, ...] = (
    Kata(
        id="dart-change-badge-text",
        name="badgeText",
        family=DART,
        language="dart",
        level=1,
        params=("unread",),
        types=("int",),
        returns="String",
        was="It puts the unread count on the notification badge: "
            "badgeText(7) is '7'.",
        brief="Someone with 1,284 unread messages has a badge wider than "
              "the icon. Above 99, the badge should say '99+'. Everything "
              "up to 99 stays as it is.",
        example="badgeText(7) → '7'   badgeText(99) → '99'   "
                "badgeText(100) → '99+'",
        hint="99 itself still fits. Which side of the line is 100 on?",
        change="A conditional expression chooses between the two Strings: "
               "unread > 99 ? '99+' : '$unread'. The line is drawn after "
               "99, so > 99 rather than >= 99 - the kind of boundary a "
               "ticket rarely spells out and a test should.",
        cases=((0,), (1,), (7,), (99,), (100,), (250,), (1284,)),
        before=_badge_text_before,
        solve=_badge_text,
        start=(
            "String badgeText(int unread) {\n"
            "  return '$unread';\n"
            "}\n"
        ),
        after=(
            "String badgeText(int unread) {\n"
            "  return unread > 99 ? '99+' : '$unread';\n"
            "}\n"
        ),
        checks=(((99,), "99"), ((100,), "99+"), ((0,), "0"),
                ((1284,), "99+")),
    ),
    Kata(
        id="dart-change-contact-subtitle",
        name="contactSubtitle",
        family=DART,
        language="dart",
        level=2,
        params=("contact",),
        types=("Map<String, dynamic>",),
        returns="String",
        was="It gives the grey subtitle under each name in the contacts "
            "ListTile, from the contact's JSON: always the email.",
        brief="Sales wants to call people, not email them. When a contact "
              "has a phone number, show that instead; a missing or null "
              "phone still falls back to the email.",
        example="{'email': 'ada@x.io', 'phone': '555-0101'} → '555-0101'   "
                "{'email': 'ada@x.io'} → 'ada@x.io'",
        hint="Reading a key that is not in a Map gives null, the same as a "
             "key that holds null. One operator handles both.",
        change="`??` gives its left side unless that is null, and a "
               "missing key reads as null just as a JSON null does - so "
               "contact['phone'] ?? contact['email'] covers both in one "
               "line.",
        cases=(
            ({"email": "ada@x.io"},),
            ({"email": "ada@x.io", "phone": "555-0101"},),
            ({"name": "Grace", "email": "grace@navy.mil", "phone": None},),
            ({"name": "Linus", "email": "linus@kernel.org",
              "phone": "555-0199"},),
            ({"name": "Alan", "email": "alan@bletchley.uk"},),
            ({"email": "tim@web.dev", "phone": "+44 20 7946 0000"},),
        ),
        before=_contact_subtitle_before,
        solve=_contact_subtitle,
        start=(
            "String contactSubtitle(Map<String, dynamic> contact) {\n"
            "  return contact['email'];\n"
            "}\n"
        ),
        after=(
            "String contactSubtitle(Map<String, dynamic> contact) {\n"
            "  return contact['phone'] ?? contact['email'];\n"
            "}\n"
        ),
        checks=(
            (({"email": "ada@x.io"},), "ada@x.io"),
            (({"email": "ada@x.io", "phone": "555-0101"},), "555-0101"),
            (({"name": "Grace", "email": "grace@navy.mil", "phone": None},),
             "grace@navy.mil"),
        ),
    ),
    Kata(
        id="dart-change-avatar-initials",
        name="avatarInitials",
        family=DART,
        language="dart",
        level=2,
        params=("fullName",),
        types=("String",),
        returns="String",
        was="It puts the first letter of a name in the CircleAvatar: "
            "avatarInitials('Ada Lovelace') is 'A'.",
        brief="Two people called Ada now share the same avatar. Use the "
              "first letters of the first and last words instead, upper "
              "case. A one-word name still gets one letter.",
        example="avatarInitials('Ada Lovelace') → 'AL'   "
                "avatarInitials('grace brewster hopper') → 'GH'   "
                "avatarInitials('Linus') → 'L'",
        hint="words.first and words.last are the same word when there is "
             "only one. Is that what you want there?",
        change="Keep the first letter, and add the last word's first letter "
               "only when there is more than one word - otherwise 'Linus' "
               "would become 'LL'. Upper-casing once, after joining, "
               "covers both letters.",
        cases=(
            ("Ada Lovelace",), ("ada",), ("grace brewster hopper",), ("x",),
            ("Linus",), ("alan turing",), ("Tim Berners-Lee",),
        ),
        before=_avatar_initials_before,
        solve=_avatar_initials,
        start=(
            "String avatarInitials(String fullName) {\n"
            "  final words = fullName.trim().split(' ');\n"
            "  return words.first[0].toUpperCase();\n"
            "}\n"
        ),
        after=(
            "String avatarInitials(String fullName) {\n"
            "  final words = fullName.trim().split(' ');\n"
            "  final last = words.length > 1 ? words.last[0] : '';\n"
            "  return (words.first[0] + last).toUpperCase();\n"
            "}\n"
        ),
        checks=((("Ada Lovelace",), "AL"), (("ada",), "A"),
                (("grace brewster hopper",), "GH"), (("x",), "X")),
    ),
    Kata(
        id="dart-change-format-duration",
        name="formatDuration",
        family=DART,
        language="dart",
        level=3,
        params=("seconds",),
        types=("int",),
        returns="String",
        was="It shows a podcast episode's length as 'm:ss': "
            "formatDuration(75) is '1:15'.",
        brief="Long episodes show as '62:05'. From one hour up, show "
              "'h:mm:ss' - '1:02:05' - with the minutes padded to two "
              "digits. Anything under an hour stays 'm:ss'.",
        example="formatDuration(75) → '1:15'   formatDuration(3725) → "
                "'1:02:05'   formatDuration(3599) → '59:59'",
        hint="Once hours are taken out, how many minutes can be left over? "
             "And what does 2 minutes look like between two colons?",
        change="Take the hours out first with ~/ 3600, and let the minutes "
               "be what is left: (seconds % 3600) ~/ 60. Under an hour the "
               "old line still does the job; from an hour up the minutes "
               "sit in the middle and need padLeft(2, '0') like the "
               "seconds.",
        cases=((0,), (5,), (75,), (3599,), (3600,), (3725,), (7384,),
               (36000,)),
        before=_format_duration_before,
        solve=_format_duration,
        start=(
            "String formatDuration(int seconds) {\n"
            "  final minutes = seconds ~/ 60;\n"
            "  final secs = (seconds % 60).toString().padLeft(2, '0');\n"
            "  return '$minutes:$secs';\n"
            "}\n"
        ),
        after=(
            "String formatDuration(int seconds) {\n"
            "  final hours = seconds ~/ 3600;\n"
            "  final minutes = (seconds % 3600) ~/ 60;\n"
            "  final secs = (seconds % 60).toString().padLeft(2, '0');\n"
            "  if (hours > 0) {\n"
            "    return '$hours:${minutes.toString().padLeft(2, '0')}:$secs';\n"
            "  }\n"
            "  return '$minutes:$secs';\n"
            "}\n"
        ),
        checks=(((75,), "1:15"), ((3725,), "1:02:05"), ((3599,), "59:59"),
                ((3600,), "1:00:00"), ((0,), "0:00")),
    ),
    Kata(
        id="dart-change-checkout-total",
        name="checkoutTotal",
        family=DART,
        language="dart",
        level=4,
        params=("items",),
        types=("List<Map<String, dynamic>>",),
        returns="int",
        was="It adds up the cart in cents, price times qty for each item: "
            "a 1200 item twice is 2400.",
        brief="Delivery now costs 499 cents, free on orders of 5000 cents "
              "or more. An empty cart is not an order and costs nothing.",
        example="[{'price': 1200, 'qty': 1}] → 1699   "
                "[{'price': 2500, 'qty': 2}] → 5000   [] → 0",
        hint="There are two edges: exactly 5000, and nothing at all. Which "
             "side of each is free?",
        change="The fee depends on the subtotal, so it goes after the loop, "
               "once the subtotal is known: if (total > 0 && total < 5000) "
               "total += 499. The 'free from 5000' wording means 5000 "
               "itself is free, hence < rather than <=.",
        cases=(
            ([],),
            ([{"price": 1200, "qty": 1}],),
            ([{"price": 2500, "qty": 2}],),
            ([{"price": 4999, "qty": 1}],),
            ([{"price": 100, "qty": 3}, {"price": 250, "qty": 2}],),
            ([{"price": 3000, "qty": 1}, {"price": 1999, "qty": 1},
              {"price": 1, "qty": 1}],),
            ([{"price": 899, "qty": 10}],),
            ([{"price": 1500, "qty": 0}],),
        ),
        before=_checkout_total_before,
        solve=_checkout_total,
        start=(
            "int checkoutTotal(List<Map<String, dynamic>> items) {\n"
            "  var total = 0;\n"
            "  for (final item in items) {\n"
            "    total += (item['price'] as int) * (item['qty'] as int);\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        after=(
            "int checkoutTotal(List<Map<String, dynamic>> items) {\n"
            "  var total = 0;\n"
            "  for (final item in items) {\n"
            "    total += (item['price'] as int) * (item['qty'] as int);\n"
            "  }\n"
            "  if (total > 0 && total < 5000) total += 499;\n"
            "  return total;\n"
            "}\n"
        ),
        checks=((([],), 0), (([{"price": 1200, "qty": 1}],), 1699),
                (([{"price": 2500, "qty": 2}],), 5000),
                (([{"price": 4999, "qty": 1}],), 5498)),
    ),
    Kata(
        id="dart-change-search-products",
        name="searchProducts",
        family=DART,
        language="dart",
        level=5,
        params=("names", "query"),
        types=("List<String>", "String"),
        returns="List<String>",
        was="It filters the product list as you type, ignoring case: "
            "'shoe' finds 'Red Shoe' and 'Blue Shoe'.",
        brief="Typing 'shoe red' finds nothing, because the words are not "
              "in that order in 'Red Shoe'. Match a product when every word "
              "of the query is somewhere in its name, in any order. "
              "Words are separated by single spaces.",
        example="(['Red Shoe', 'Red Hat'], 'shoe red') → ['Red Shoe']   "
                "(['Red Shoe', 'Red Hat'], 'red') → ['Red Shoe', 'Red Hat']",
        hint="Split the query into words first. Which list method asks "
             "whether a test holds for every element?",
        change="Split the lower-cased query on spaces, and keep a name when "
               "words.every(...) finds each word in it. A one-word query "
               "is a list of one word, so it behaves as before, and an "
               "empty query splits to [''] - which every name contains - "
               "so the full list still shows before anything is typed.",
        cases=(
            (["Red Shoe", "Blue Shoe", "Red Hat"], "shoe red"),
            (["Red Shoe", "Blue Shoe", "Red Hat"], "shoe"),
            (["Red Shoe", "Blue Shoe"], ""),
            ([], "red"),
            (["Running Shoe, Red"], "red running"),
            (["Wool Hat", "Wool Scarf", "Cotton Hat"], "hat wool"),
            (["Wool Hat", "Wool Scarf", "Cotton Hat"], "wool hat"),
            (["Phone Case"], "case"),
        ),
        before=_search_products_before,
        solve=_search_products,
        start=(
            "List<String> searchProducts(List<String> names, String query) {\n"
            "  final q = query.toLowerCase();\n"
            "  return names.where((name) => name.toLowerCase().contains(q)).toList();\n"
            "}\n"
        ),
        after=(
            "List<String> searchProducts(List<String> names, String query) {\n"
            "  final words = query.toLowerCase().split(' ');\n"
            "  return names\n"
            "      .where((name) => words.every((w) => name.toLowerCase().contains(w)))\n"
            "      .toList();\n"
            "}\n"
        ),
        checks=(
            ((["Red Shoe", "Blue Shoe", "Red Hat"], "shoe red"), ["Red Shoe"]),
            ((["Red Shoe", "Blue Shoe", "Red Hat"], "shoe"),
             ["Red Shoe", "Blue Shoe"]),
            ((["Red Shoe", "Blue Shoe"], ""), ["Red Shoe", "Blue Shoe"]),
            (([], "red"), []),
            ((["Wool Hat", "Wool Scarf", "Cotton Hat"], "hat wool"),
             ["Wool Hat"]),
        ),
    ),
)
