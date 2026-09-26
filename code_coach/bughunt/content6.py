"""A third set of JavaScript bug hunts.

The first two sets cover a weekday numbered 7, quantities joined as
text, a loop that returns too early, a discount times ten, sort() on
numbers, != deciding 0 is blank, fill() sharing one array and parseInt
stopping at a comma. These are different mistakes, each one a
JavaScript habit that bites people who know the language:

  getUTCMonth()     months count from 0, so April is 3 and lands in Q1
  indexOf > 0       "found" is >= 0, so the first item never counts
  toFixed(2)        hands back text, and number + text joins them
  reduce()          with no starting value it throws on an empty array
  Object.keys       integer-like keys come out in numeric order, not
                    the order they were added
  { ...profile }    copies the object but not the array inside it, so
                    the caller's profile changes too

In every one the report is about the function you call and the cause is
in a helper it uses. The same rules hold as for the other hunts, and the
suite checks them: the bug is real, it hides on some inputs, the
report's own input shows it, and the fix changes one or two lines in
place.
"""

from __future__ import annotations

import math

from code_coach.bughunt import Hunt

JAVASCRIPT = "JavaScript"


def _quarter_label(iso_date: str) -> str:
    year, month = int(iso_date[0:4]), int(iso_date[5:7])
    return f"Q{math.ceil(month / 3)} {year}"


def _titles_tagged(posts: list, tag: str) -> list:
    return [post["title"] for post in posts if tag in post["tags"]]


def _total_with_tip(bill, percent):
    # The tip is rounded to the cent the way toFixed does it (from the
    # exact binary value), then added as a number.
    tip = 0 if percent <= 0 else float(f"{bill * percent / 100:.2f}")
    return bill + tip


_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def _week_summary(sessions: list) -> list:
    return [f"{_DAYS[i]}: {sum(day)} min" for i, day in enumerate(sessions)]


def _check_in_order(rooms: list) -> list:
    seen: list = []
    for room in rooms:
        if room not in seen:
            seen.append(room)
    return [f"Room {room}" for room in seen]


def _add_tag(profile: dict, tag: str) -> dict:
    tags = list(profile["tags"])
    if len(tags) < 5 and tag not in tags:
        tags.append(tag)
    return {**profile, "tags": tags}


JAVASCRIPT_HUNTS_3: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-js-april-in-q1",
        title="April is in Q1",
        family=JAVASCRIPT,
        language="javascript",
        level=1,
        report="An invoice dated 2026-04-01 was filed under 'Q1 2026'. It "
               "should be Q2. March invoices look right.",
        name="quarterLabel",
        params=("isoDate",),
        start=(
            "const MONTHS_PER_QUARTER = 3;\n"
            "\n"
            "function dateParts(isoDate) {\n"
            "  const d = new Date(isoDate);\n"
            "  return { year: d.getUTCFullYear(), month: d.getUTCMonth() };\n"
            "}\n"
            "\n"
            "function quarterLabel(isoDate) {\n"
            "  const { year, month } = dateParts(isoDate);\n"
            "  return \"Q\" + Math.ceil(month / MONTHS_PER_QUARTER) + \" \" + year;\n"
            "}\n"
        ),
        fixed=(
            "const MONTHS_PER_QUARTER = 3;\n"
            "\n"
            "function dateParts(isoDate) {\n"
            "  const d = new Date(isoDate);\n"
            "  return { year: d.getUTCFullYear(), month: d.getUTCMonth() + 1 };\n"
            "}\n"
            "\n"
            "function quarterLabel(isoDate) {\n"
            "  const { year, month } = dateParts(isoDate);\n"
            "  return \"Q\" + Math.ceil(month / MONTHS_PER_QUARTER) + \" \" + year;\n"
            "}\n"
        ),
        solve=_quarter_label,
        reported=("2026-04-01",),
        cases=(("2026-03-15",), ("2026-04-01",), ("2025-12-31",),
               ("2026-01-15",), ("2026-08-20",), ("2026-07-04",)),
        cause="getUTCMonth() counts months from 0, so April comes back as 3 "
              "and 3 / 3 rounds up to quarter 1.",
        decoys=(
            "new Date reads the date in local time, so the 1st of the month "
            "becomes the last day of the month before.",
            "Math.ceil should be Math.floor - quarters round down.",
            "getUTCFullYear() gives the year minus 1900.",
        ),
        lesson="In a JavaScript Date the month is the odd one out: "
               "getMonth() and getUTCMonth() run 0 to 11 while the day runs "
               "1 to 31. Add 1 as soon as you read it, in one place, so no "
               "other code has to remember.",
        hint="The report's date: quarterLabel(\"2026-04-01\"). Then try "
             "January.",
        checks=((("2026-04-01",), "Q2 2026"), (("2026-01-15",), "Q1 2026"),
                (("2026-03-15",), "Q1 2026"), (("2025-12-31",), "Q4 2025"),
                (("2026-07-04",), "Q3 2026")),
    ),
    Hunt(
        id="hunt-js-first-tag",
        title="Pancakes are not breakfast",
        family=JAVASCRIPT,
        language="javascript",
        level=1,
        report="Filtering recipes by 'breakfast' leaves out Pancakes, which "
               "is tagged breakfast and sweet. The Omelette, tagged eggs and "
               "breakfast, shows up fine.",
        name="titlesTagged",
        params=("posts", "tag"),
        start=(
            "function hasTag(post, tag) {\n"
            "  return post.tags.indexOf(tag) > 0;\n"
            "}\n"
            "\n"
            "function titlesTagged(posts, tag) {\n"
            "  const titles = [];\n"
            "  for (const post of posts) {\n"
            "    if (hasTag(post, tag)) titles.push(post.title);\n"
            "  }\n"
            "  return titles;\n"
            "}\n"
        ),
        fixed=(
            "function hasTag(post, tag) {\n"
            "  return post.tags.indexOf(tag) >= 0;\n"
            "}\n"
            "\n"
            "function titlesTagged(posts, tag) {\n"
            "  const titles = [];\n"
            "  for (const post of posts) {\n"
            "    if (hasTag(post, tag)) titles.push(post.title);\n"
            "  }\n"
            "  return titles;\n"
            "}\n"
        ),
        solve=_titles_tagged,
        reported=([{"title": "Pancakes", "tags": ["breakfast", "sweet"]},
                   {"title": "Omelette", "tags": ["eggs", "breakfast"]}],
                  "breakfast"),
        cases=(
            ([], "breakfast"),
            ([{"title": "Omelette", "tags": ["eggs", "breakfast"]}],
             "breakfast"),
            ([{"title": "Pancakes", "tags": ["breakfast", "sweet"]},
              {"title": "Omelette", "tags": ["eggs", "breakfast"]}],
             "breakfast"),
            ([{"title": "Soup", "tags": ["lunch"]}], "breakfast"),
            ([{"title": "Toast", "tags": ["breakfast"]}], "breakfast"),
            ([{"title": "Salad", "tags": ["lunch", "green", "quick"]}],
             "quick"),
        ),
        cause="indexOf gives 0 when the tag is the first one, and 0 > 0 is "
              "false, so a post whose first tag matches is left out.",
        decoys=(
            "indexOf compares with ==, so 'breakfast' does not match itself.",
            "The for...of loop skips the first post in the list.",
            "titles.push runs before the check, so the wrong titles are kept.",
        ),
        lesson="indexOf says 'not found' with -1, and 0 is a real position - "
               "the first one. The test for found is >= 0 or !== -1, never "
               "> 0. Better still, includes() answers the question you meant "
               "to ask.",
        hint="Try a recipe with the tag you want listed first, then one with "
             "it listed second.",
        checks=(
            (([{"title": "Pancakes", "tags": ["breakfast", "sweet"]},
               {"title": "Omelette", "tags": ["eggs", "breakfast"]}],
              "breakfast"), ["Pancakes", "Omelette"]),
            (([], "breakfast"), []),
            (([{"title": "Soup", "tags": ["lunch"]}], "breakfast"), []),
            (([{"title": "Toast", "tags": ["breakfast"]}], "breakfast"),
             ["Toast"]),
        ),
    ),
    Hunt(
        id="hunt-js-tip-as-text",
        title="A $20 bill comes to 203",
        family=JAVASCRIPT,
        language="javascript",
        level=2,
        report="A $20 bill with a 15% tip comes to 203.00. With no tip it "
               "correctly comes to 20.",
        name="totalWithTip",
        params=("bill", "percent"),
        start=(
            "function roundCents(amount) {\n"
            "  return amount.toFixed(2);\n"
            "}\n"
            "\n"
            "function tipFor(bill, percent) {\n"
            "  if (percent <= 0) return 0;\n"
            "  return roundCents(bill * percent / 100);\n"
            "}\n"
            "\n"
            "function totalWithTip(bill, percent) {\n"
            "  return bill + tipFor(bill, percent);\n"
            "}\n"
        ),
        fixed=(
            "function roundCents(amount) {\n"
            "  return Number(amount.toFixed(2));\n"
            "}\n"
            "\n"
            "function tipFor(bill, percent) {\n"
            "  if (percent <= 0) return 0;\n"
            "  return roundCents(bill * percent / 100);\n"
            "}\n"
            "\n"
            "function totalWithTip(bill, percent) {\n"
            "  return bill + tipFor(bill, percent);\n"
            "}\n"
        ),
        solve=_total_with_tip,
        reported=(20, 15),
        cases=((20, 0), (20, 15), (100, 0), (12, 20), (48, 10), (7, -5)),
        cause="toFixed(2) returns text, not a number, so bill + tip joins "
              "'20' and '3.00' into '203.00' instead of adding them.",
        decoys=(
            "bill * percent / 100 works out a 150% tip, not 15%.",
            "toFixed(2) rounds 3 up to 300 by moving the decimal point.",
            "tipFor returns 0 whenever there is a tip, so only the bill is "
            "counted.",
        ),
        lesson="toFixed is for showing a number, and what it gives back is a "
               "string. The moment a string meets +, JavaScript joins instead "
               "of adding. Round with Number(x.toFixed(2)) or "
               "Math.round(x * 100) / 100 if you still need to do sums.",
        hint="The report's bill: totalWithTip(20, 15). Then the same bill "
             "with a tip of 0.",
        checks=(((20, 15), 23.0), ((20, 0), 20), ((12, 20), 14.4),
                ((100, 0), 100), ((48, 10), 52.8)),
    ),
    Hunt(
        id="hunt-js-empty-day",
        title="A rest day crashes the week",
        family=JAVASCRIPT,
        language="javascript",
        level=2,
        report="The weekly summary crashes for any week where I skipped a "
               "day. Weeks where I trained every day are fine.",
        name="weekSummary",
        params=("sessions",),
        start=(
            "const DAYS = [\"Mon\", \"Tue\", \"Wed\", \"Thu\", \"Fri\", \"Sat\", \"Sun\"];\n"
            "\n"
            "function total(minutes) {\n"
            "  return minutes.reduce((sum, m) => sum + m);\n"
            "}\n"
            "\n"
            "function weekSummary(sessions) {\n"
            "  return sessions.map((day, i) => DAYS[i] + \": \" + total(day) + \" min\");\n"
            "}\n"
        ),
        fixed=(
            "const DAYS = [\"Mon\", \"Tue\", \"Wed\", \"Thu\", \"Fri\", \"Sat\", \"Sun\"];\n"
            "\n"
            "function total(minutes) {\n"
            "  return minutes.reduce((sum, m) => sum + m, 0);\n"
            "}\n"
            "\n"
            "function weekSummary(sessions) {\n"
            "  return sessions.map((day, i) => DAYS[i] + \": \" + total(day) + \" min\");\n"
            "}\n"
        ),
        solve=_week_summary,
        reported=([[30, 15], [], [45]],),
        cases=(([],), ([[30]],), ([[30, 15], [20]],), ([[30, 15], [], [45]],),
               ([[], [10]],), ([[5, 5, 5], [60]],)),
        cause="reduce with no starting value uses the first element to start, "
              "and an empty day has no first element, so it throws a "
              "TypeError.",
        decoys=(
            "DAYS[i] runs off the end of the array for the second day.",
            "map skips empty arrays, so the days after a rest day shift left.",
            "sum + m joins the minutes as text, so 30 and 15 become 3015.",
        ),
        lesson="reduce without a starting value is a promise the array is "
               "never empty. Give it one - reduce((sum, m) => sum + m, 0) - "
               "and an empty list quietly totals 0 instead of crashing.",
        hint="Try a week with an empty day in it: weekSummary([[30], []]).",
        checks=((([[30, 15], [], [45]],), ["Mon: 45 min", "Tue: 0 min",
                                           "Wed: 45 min"]),
                (([],), []),
                (([[30]],), ["Mon: 30 min"]),
                (([[], [10]],), ["Mon: 0 min", "Tue: 10 min"])),
    ),
    Hunt(
        id="hunt-js-room-order",
        title="Room 12 checked in first",
        family=JAVASCRIPT,
        language="javascript",
        level=3,
        report="Room 305 checked in before room 12, but the check-in list "
               "puts Room 12 first. Rooms like B4 stay where they should.",
        name="checkInOrder",
        params=("rooms",),
        start=(
            "function firstSeen(items) {\n"
            "  const order = {};\n"
            "  items.forEach((item, i) => {\n"
            "    if (!(item in order)) order[item] = i;\n"
            "  });\n"
            "  return Object.keys(order);\n"
            "}\n"
            "\n"
            "function checkInOrder(rooms) {\n"
            "  return firstSeen(rooms).map((room) => \"Room \" + room);\n"
            "}\n"
        ),
        fixed=(
            "function firstSeen(items) {\n"
            "  const order = {};\n"
            "  items.forEach((item, i) => {\n"
            "    if (!(item in order)) order[item] = i;\n"
            "  });\n"
            "  return Object.keys(order).sort((a, b) => order[a] - order[b]);\n"
            "}\n"
            "\n"
            "function checkInOrder(rooms) {\n"
            "  return firstSeen(rooms).map((room) => \"Room \" + room);\n"
            "}\n"
        ),
        solve=_check_in_order,
        reported=(["305", "12", "305", "B4"],),
        cases=(([],), (["A1", "B2", "A1"],), (["1", "2"],),
               (["305", "12", "305", "B4"],), (["10", "9"],),
               (["B4", "A1", "B4"],)),
        cause="Object.keys lists keys that look like whole numbers in numeric "
              "order first, whatever order they were added in, so '12' comes "
              "before '305'.",
        decoys=(
            "The in check lets a room that is seen twice in, so 305 is "
            "listed at its second position.",
            "forEach runs through the rooms from the end.",
            "Object.keys sorts every key alphabetically, so B4 should have "
            "moved as well.",
        ),
        lesson="A plain object is not an ordered list. Keys like '12' and "
               "'305' are treated as array indexes and come out smallest "
               "first; only other keys keep the order they were added. When "
               "order matters, use a Map or a Set - they remember insertion "
               "order for every key.",
        hint="Try rooms whose numbers go down: checkInOrder([\"10\", \"9\"]). "
             "Then rooms with letters in.",
        checks=(((["305", "12", "305", "B4"],),
                 ["Room 305", "Room 12", "Room B4"]),
                (([],), []),
                ((["10", "9"],), ["Room 10", "Room 9"]),
                ((["A1", "B2", "A1"],), ["Room A1", "Room B2"])),
    ),
    Hunt(
        id="hunt-js-shared-tags",
        title="Tagging the copy tags the original",
        family=JAVASCRIPT,
        language="javascript",
        level=3,
        report="addTag is supposed to return a new profile and leave the one "
               "I pass in alone. After addTag({name: 'Ada', tags: "
               "['admin']}, 'editor') the original profile has 'editor' in "
               "its tags too.",
        name="addTag",
        params=("profile", "tag"),
        start=(
            "const MAX_TAGS = 5;\n"
            "\n"
            "function copyProfile(profile) {\n"
            "  return { ...profile };\n"
            "}\n"
            "\n"
            "function addTag(profile, tag) {\n"
            "  const copy = copyProfile(profile);\n"
            "  if (copy.tags.length >= MAX_TAGS || copy.tags.includes(tag)) return copy;\n"
            "  copy.tags.push(tag);\n"
            "  return copy;\n"
            "}\n"
        ),
        fixed=(
            "const MAX_TAGS = 5;\n"
            "\n"
            "function copyProfile(profile) {\n"
            "  return { ...profile, tags: [...profile.tags] };\n"
            "}\n"
            "\n"
            "function addTag(profile, tag) {\n"
            "  const copy = copyProfile(profile);\n"
            "  if (copy.tags.length >= MAX_TAGS || copy.tags.includes(tag)) return copy;\n"
            "  copy.tags.push(tag);\n"
            "  return copy;\n"
            "}\n"
        ),
        solve=_add_tag,
        reported=({"name": "Ada", "tags": ["admin"]}, "editor"),
        cases=(
            ({"name": "Ada", "tags": ["admin"]}, "admin"),
            ({"name": "Ada", "tags": ["admin"]}, "editor"),
            ({"name": "Bo", "tags": []}, "new"),
            ({"name": "Cy", "tags": ["a", "b", "c", "d", "e"]}, "f"),
            ({"name": "Di", "tags": ["x", "y"]}, "z"),
        ),
        cause="{ ...profile } copies the object but not the tags array inside "
              "it, so the copy and the original share one array and push "
              "adds the tag to both.",
        decoys=(
            "const copy cannot be changed, so push has to write through to "
            "the original.",
            "includes(tag) adds the tag while it checks for it.",
            "Spreading an object copies it lazily, so it only becomes a real "
            "copy once addTag returns.",
        ),
        lesson="Spread copies one level deep. Every array or object inside "
               "is the same one, shared, so changing it through the copy "
               "changes the original. Copy the parts you are about to change "
               "- tags: [...profile.tags] - or use structuredClone for the "
               "whole thing.",
        hint="Add a tag the profile does not have yet, and watch whether the "
             "profile you passed in changes.",
        checks=(
            (({"name": "Ada", "tags": ["admin"]}, "editor"),
             {"name": "Ada", "tags": ["admin", "editor"]}),
            (({"name": "Ada", "tags": ["admin"]}, "admin"),
             {"name": "Ada", "tags": ["admin"]}),
            (({"name": "Bo", "tags": []}, "new"), {"name": "Bo", "tags": ["new"]}),
            (({"name": "Cy", "tags": ["a", "b", "c", "d", "e"]}, "f"),
             {"name": "Cy", "tags": ["a", "b", "c", "d", "e"]}),
        ),
    ),
)
