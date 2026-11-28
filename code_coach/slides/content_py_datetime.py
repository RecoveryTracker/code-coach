"""Dates and Times: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree.
Only fixed dates are used, never the current time."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 104

DECK = Deck(
    id="py-datetime",
    title="Dates and Times",
    language="python",
    blurb="The datetime module with fixed dates: date, datetime, timedelta, formats, parsing, months, leap years and ranges.",
    slides=(
        Slide(
            title="date: a day on the calendar",
            text="date(year, month, day) builds a calendar date with no time of day. It prints in year-month-day order, and you read its parts as attributes.",
            code=r"""from datetime import date
d = date(2026, 3, 1)
print(d)
print(d.year, d.month, d.day)""",
            output="2026-03-01\n2026 3 1",
            point="A date is year, month and day, and nothing more.",
        ),
        Slide(
            title="datetime: a date and a time",
            text="datetime adds hour, minute and second. Its .date() method drops the time again.",
            code=r"""from datetime import datetime
dt = datetime(2026, 3, 1, 14, 30, 5)
print(dt)
print(dt.hour, dt.minute)
print(dt.date())""",
            output="2026-03-01 14:30:05\n14 30\n2026-03-01",
            point="datetime(y, m, d, h, mi, s) is a date plus a clock time.",
        ),
        Slide(
            title="timedelta arithmetic",
            text="A timedelta is a length of time. Add it to a date to move forward, or subtract it to move back; Python handles month ends for you.",
            code=r"""from datetime import date, timedelta
d = date(2026, 3, 1)
print(d + timedelta(days=45))
print(d - timedelta(days=1))
print(timedelta(hours=36))""",
            output="2026-04-15\n2026-02-28\n1 day, 12:00:00",
            point="date + timedelta gives a date; the calendar math is done for you.",
        ),
        Slide(
            title="Days between two dates",
            text="Subtracting one date from another gives a timedelta. Its .days attribute is the number of whole days between them.",
            code=r"""from datetime import date
delta = date(2026, 12, 25) - date(2026, 3, 1)
print(delta)
print(delta.days)
print(delta.days // 7)""",
            output="299 days, 0:00:00\n299\n42",
            point="date - date = timedelta, and .days is the answer you want.",
        ),
        Slide(
            title="weekday() and isoweekday()",
            text="weekday() counts Monday as 0 up to Sunday as 6. isoweekday() counts Monday as 1 up to Sunday as 7. March 1, 2026 is a Sunday and March 2 is a Monday.",
            code=r"""from datetime import date
a = date(2026, 3, 1)
b = date(2026, 3, 2)
print(a.weekday(), a.isoweekday())
print(b.weekday(), b.isoweekday())""",
            output="6 7\n0 1",
            point="weekday(): Mon=0 to Sun=6. isoweekday(): Mon=1 to Sun=7.",
        ),
        Slide(
            title="strftime: date to text",
            text="strftime formats a date with codes: %Y is the year, %m the month number, %d the day, %A the weekday name, %B the month name, %H the hour, %M the minute.",
            code=r"""from datetime import datetime
dt = datetime(2026, 3, 1, 14, 30, 5)
print(dt.strftime("%Y-%m-%d"))
print(dt.strftime("%A %B %d"))
print(dt.strftime("%H:%M"))
print(dt.strftime("%I:%M %p"))""",
            output="2026-03-01\nSunday March 01\n14:30\n02:30 PM",
            point="strftime: f for format, because the result is a string.",
        ),
        Slide(
            title="strptime: text to datetime",
            text="strptime reads text using the same codes and gives back a datetime. The format must describe the text exactly, or it raises ValueError.",
            code=r"""from datetime import datetime
dt = datetime.strptime("03/01/2026 09:15", "%m/%d/%Y %H:%M")
print(dt)
print(dt.strftime("%d %b %Y"))""",
            output="2026-03-01 09:15:00\n01 Mar 2026",
            point="strptime parses, strftime formats; the p is for parse.",
        ),
        Slide(
            title="isoformat and fromisoformat",
            text="isoformat writes the standard year-month-day form, with a T between date and time. fromisoformat reads it back, so it is the safest way to store a date as text.",
            code=r"""from datetime import date, datetime
dt = datetime(2026, 3, 1, 14, 30, 5)
print(dt.isoformat())
print(date.fromisoformat("2026-03-01"))
print(datetime.fromisoformat("2026-03-01T14:30:05") == dt)""",
            output="2026-03-01T14:30:05\n2026-03-01\nTrue",
            point="ISO text sorts correctly as plain text and round-trips exactly.",
        ),
        Slide(
            title="Comparing dates",
            text="Dates compare like numbers: earlier is smaller. You can use <, ==, min and max, and you can compare a timedelta to another timedelta.",
            code=r"""from datetime import date, timedelta
d1 = date(2026, 3, 1)
d2 = date(2026, 3, 15)
print(d1 < d2, d1 == date(2026, 3, 1))
print(max(d1, d2))
print(d2 - d1 > timedelta(days=10))""",
            output="True True\n2026-03-15\nTrue",
            point="Earlier dates are smaller, so sorting and max just work.",
        ),
        Slide(
            title="Adding months is not a timedelta",
            text="timedelta has no months, because months differ in length. Use calendar.monthrange(year, month), which gives the weekday of day 1 and the number of days, then clamp the day yourself.",
            code=r"""import calendar
from datetime import date
first, n = calendar.monthrange(2026, 2)
print(int(first), n)
last = calendar.monthrange(2026, 2)[1]
print(date(2026, 2, min(31, last)))""",
            output="6 28\n2026-02-28",
            point="Jan 31 plus one month has no clear answer; clamp to the month's last day.",
        ),
        Slide(
            title="Leap years with calendar.isleap",
            text="A leap year is divisible by 4, except century years, which must be divisible by 400. calendar.isleap applies that rule, and date handles February 29 correctly.",
            code=r"""import calendar
from datetime import date, timedelta
print(calendar.isleap(2024), calendar.isleap(2026))
print(calendar.isleap(1900), calendar.isleap(2000))
print(date(2024, 2, 29) + timedelta(days=1))""",
            output="True False\nFalse True\n2024-03-01",
            point="Divisible by 4, but 1900 was not a leap year and 2000 was.",
        ),
        Slide(
            title="Time zones and timezone.utc",
            text="A naive datetime has no zone. An aware one carries an offset, and timezone.utc is the built-in UTC zone. You cannot compare a naive and an aware datetime; Python raises TypeError.",
            code=r"""from datetime import datetime, timezone
dt = datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)
print(dt)
try:
    dt < datetime(2026, 3, 2)
except TypeError:
    print("cannot compare")""",
            output="2026-03-01 12:00:00+00:00\ncannot compare",
            point="Store times in UTC and convert to local time only for display.",
        ),
        Slide(
            title="Sorting dates",
            text="A list of dates sorts with sorted() or min() with no extra work. Convert to isoformat afterwards if you want plain text to print.",
            code=r"""from datetime import date
ds = [date(2026, 3, 15), date(2025, 12, 31), date(2026, 1, 5)]
print([d.isoformat() for d in sorted(ds)])
print(min(ds))""",
            output="['2025-12-31', '2026-01-05', '2026-03-15']\n2025-12-31",
            point="Dates sort in time order by themselves.",
        ),
        Slide(
            title="A date range with a loop",
            text="To visit every day between two dates, start at the first and keep adding one day with timedelta. Stop when you pass the end.",
            code=r"""from datetime import date, timedelta
d = date(2026, 2, 27)
end = date(2026, 3, 2)
while d <= end:
    print(d, d.strftime("%a"))
    d += timedelta(days=1)""",
            output="2026-02-27 Fri\n2026-02-28 Sat\n2026-03-01 Sun\n2026-03-02 Mon",
            point="Loop with d += timedelta(days=1) and compare with <=.",
        ),
        Slide(
            title="Counting weekdays in a month",
            text="Build every day of a month with a comprehension, then count the ones whose weekday() is below 5. March 2026 has 31 days.",
            code=r"""from datetime import date, timedelta
start = date(2026, 3, 1)
days = [start + timedelta(days=i) for i in range(31)]
print(sum(1 for d in days if d.weekday() < 5))
print(sum(1 for d in days if d.weekday() >= 5))""",
            output="22\n9",
            point="weekday() < 5 means Monday to Friday.",
        ),
    ),
)
