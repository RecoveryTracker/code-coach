"""SQL deeper queries, part 7: Date Math.

SQLite's date(), time(), datetime(), strftime() and julianday() on FIXED literals only (never 'now'): adding days, months and years
(with the end-of-month overflow), start of month / year, weekday numbers, day counts, day of year, formats, the unix epoch, and a
small table of dates to count, group and compare. Answers are worked out with Python's `datetime` (`_sqlquery_model.py`).
"""

from __future__ import annotations

import datetime as dt
import random
from typing import Callable

from ._model import Maker
from ._sql_model import NULL, Retry, Tbl, fit, sql_item
from ._sqlquery_model import (D, add_days, add_months, add_years, day_of_year, days_between, iso, last_day_of_month, next_weekday,
                              rand_date, start_of_month, start_of_year, week_of_year, weekday_w)

DATE: list[Maker] = []


def reg(f: Callable) -> Callable:
    DATE.append(fit(f))
    return f


def _d(rng: random.Random, late: bool = False) -> dt.date:
    """A random date, often near the end of a month (so month arithmetic overflows)."""
    d = rand_date(rng)
    if late and rng.random() < 0.7:
        d = last_day_of_month(d).replace(day=1)
        d = d.replace(day=last_day_of_month(d).day - rng.randint(0, 2))
    return d


def _jd(d: dt.date) -> float:
    """julianday(d) at midnight: a real ending in .5."""
    return d.toordinal() + 1721424.5


def _dates(rng: random.Random, n: int = 5) -> Tbl:
    ds = sorted(rng.sample([rand_date(rng, "2024-01-01", "2024-12-31") for _ in range(30)], n))
    rng.shuffle(ds)
    return Tbl("t", [("d", "TEXT")], [(iso(d),) for d in ds])


def DS(t: Tbl) -> list[dt.date]:
    return [D(d) for d in t.col("d")]


# ── Adding and subtracting ──────────────────────────────────────────────

@reg
def plus_days(rng):
    d, n = _d(rng), rng.randint(5, 90)
    return sql_item([], f"SELECT date('{d}', '+{n} days');", iso(add_days(d, n)), "Each modifier moves the date; days carry over into the next month or year.")


@reg
def minus_days(rng):
    d, n = _d(rng), rng.randint(5, 90)
    return sql_item([], f"SELECT date('{d}', '-{n} days');", iso(add_days(d, -n)), "A minus sign moves the date back, across month and year ends.")


@reg
def plus_month(rng):
    d, n = _d(rng), rng.randint(1, 14)
    return sql_item([], f"SELECT date('{d}', '+{n} months');", iso(add_months(d, n)), "The month number moves and the day stays; a day that does not exist overflows into the next month.")


@reg
def month_end_overflow(rng):
    y = rng.choice([2023, 2024, 2025])
    d = dt.date(y, 1, rng.choice([29, 30, 31]))
    return sql_item([], f"SELECT date('{d}', '+1 month');", iso(add_months(d, 1)), "February has no such day, so the extra days spill into March (SQLite does not clamp to the end of February).")


@reg
def minus_month_overflow(rng):
    y = rng.choice([2023, 2024, 2025])
    d = dt.date(y, 3, rng.choice([29, 30, 31]))
    return sql_item([], f"SELECT date('{d}', '-1 month');", iso(add_months(d, -1)), "One month back lands on a February day that does not exist, and the extra days spill into March.")


@reg
def plus_year(rng):
    d, n = _d(rng), rng.randint(1, 5)
    return sql_item([], f"SELECT date('{d}', '+{n} years');", iso(add_years(d, n)), "Years move the year and keep the month and day.")


@reg
def leap_day_year(rng):
    y = rng.choice([2020, 2024, 2028])
    d = dt.date(y, 2, 29)
    return sql_item([], f"SELECT date('{d}', '+1 year');", iso(add_years(d, 1)), "The next year has no 29 February, so the date overflows to 1 March.")


@reg
def leap_day_four_years(rng):
    y = rng.choice([2020, 2024])
    d = dt.date(y, 2, 29)
    return sql_item([], f"SELECT date('{d}', '+4 years');", iso(add_years(d, 4)), "Four years later is a leap year again, so 29 February exists.")


@reg
def month_then_day(rng):
    d = dt.date(rng.choice([2023, 2024]), 1, 31)
    return sql_item([], f"SELECT date('{d}', '+1 month', '-1 day');", iso(add_days(add_months(d, 1), -1)), "Modifiers run left to right: +1 month overflows into March first, then one day back.")


@reg
def day_then_month(rng):
    d = dt.date(rng.choice([2023, 2024]), 1, 31)
    return sql_item([], f"SELECT date('{d}', '-1 day', '+1 month');", iso(add_months(add_days(d, -1), 1)), "The day goes back first (to 30 January), and then +1 month lands on 30 February, which overflows.")


@reg
def last_day_idiom(rng):
    d = _d(rng)
    return sql_item([], f"SELECT date('{d}', 'start of month', '+1 month', '-1 day');", iso(last_day_of_month(d)), "Start of month, to the next month, one day back: the last day of the month.")


@reg
def start_month(rng):
    d = _d(rng)
    return sql_item([], f"SELECT date('{d}', 'start of month');", iso(start_of_month(d)), "The first day of the same month.")


@reg
def start_year(rng):
    d = _d(rng)
    return sql_item([], f"SELECT date('{d}', 'start of year');", iso(start_of_year(d)), "1 January of the same year.")


@reg
def next_month_first(rng):
    d = _d(rng, late=True)
    return sql_item([], f"SELECT date('{d}', 'start of month', '+1 month');", iso(add_months(start_of_month(d), 1)), "Going to the start of the month first makes +1 month safe: no overflow.")


@reg
def next_weekday_mod(rng):
    d, w = _d(rng), rng.randint(0, 6)
    return sql_item([], f"SELECT date('{d}', 'weekday {w}');", iso(next_weekday(d, w)), "'weekday N' moves forward to the next day with that weekday number (0 is Sunday); the same day if it already is one.")


@reg
def monday_of_week(rng):
    d = _d(rng)
    got = add_days(next_weekday(d, 0), -6)
    return sql_item([], f"SELECT date('{d}', 'weekday 0', '-6 days');", iso(got), "Forward to the coming Sunday, then six days back: the Monday that starts this week.")


@reg
def invalid_day_normalised(rng):
    y, m = rng.choice([2023, 2025]), 2
    day = rng.choice([29, 30, 31])
    got = add_days(dt.date(y, m, 1), day - 1)
    return sql_item([], f"SELECT date('{y}-0{m}-{day}');", iso(got), "SQLite accepts a day number up to 31 in any month and rolls the extra days into the next month.")


@reg
def invalid_month_null(rng):
    y = rng.choice([2023, 2024])
    return sql_item([], f"SELECT date('{y}-13-05');", NULL, "There is no month 13: the text is not a date, and date() gives NULL.")


# ── Pieces of a date ───────────────────────────────────────────────────

@reg
def weekday_number(rng):
    d = _d(rng)
    return sql_item([], f"SELECT strftime('%w', '{d}');", str(weekday_w(d)), "%w is the weekday as a number with Sunday as 0 (the result is text).")


@reg
def weekday_known(rng):
    d = rng.choice([dt.date(2024, 1, 1), dt.date(2024, 2, 29), dt.date(2023, 12, 25), dt.date(2025, 7, 4), dt.date(2024, 7, 4)])
    return sql_item([], f"SELECT strftime('%w', '{d}');", str(weekday_w(d)), "Sunday is 0, Monday 1, ... Saturday 6.")


@reg
def year_piece(rng):
    d = _d(rng)
    return sql_item([], f"SELECT strftime('%Y', '{d}');", str(d.year), "%Y is the four-digit year.")


@reg
def month_piece(rng):
    d = _d(rng)
    return sql_item([], f"SELECT strftime('%m', '{d}');", f"{d.month:02d}", "%m is the month with a leading zero: March is 03.")


@reg
def day_piece(rng):
    d = _d(rng)
    return sql_item([], f"SELECT strftime('%d', '{d}');", f"{d.day:02d}", "%d is the day of the month with a leading zero.")


@reg
def month_piece_number(rng):
    d = _d(rng)
    return sql_item([], f"SELECT strftime('%m', '{d}') + 0;", d.month, "Adding 0 turns the text 03 into the number 3.")


@reg
def year_month(rng):
    d = _d(rng)
    return sql_item([], f"SELECT strftime('%Y-%m', '{d}');", f"{d.year}-{d.month:02d}", "A format string can mix pieces and punctuation: year-month.")


@reg
def day_of_year_piece(rng):
    d = _d(rng)
    return sql_item([], f"SELECT strftime('%j', '{d}');", f"{day_of_year(d):03d}", "%j is the day of the year, three digits: 1 January is 001.")


@reg
def week_piece(rng):
    d = _d(rng)
    return sql_item([], f"SELECT strftime('%W', '{d}');", f"{week_of_year(d):02d}", "%W is the week of the year with Monday as the first day; days before the first Monday are week 00.")


@reg
def quarter(rng):
    d = _d(rng)
    return sql_item([], f"SELECT (strftime('%m', '{d}') + 2) / 3;", (d.month + 2) // 3, "The month number plus 2, integer-divided by 3: the quarter, 1 to 4.")


@reg
def year_difference(rng):
    a, b = _d(rng), _d(rng)
    a, b = sorted([a, b])
    return sql_item([], f"SELECT strftime('%Y', '{b}') - strftime('%Y', '{a}');", b.year - a.year, "The texts are read as numbers and subtracted: the difference of the years only, ignoring the month and day.")


@reg
def last_feb_day(rng):
    y = rng.choice([2023, 2024, 2025, 2028, 2100])
    last = last_day_of_month(dt.date(y, 2, 1)).day
    return sql_item([], f"SELECT strftime('%d', date('{y}-03-01', '-1 day'));", f"{last}", "The day before 1 March is the last day of February: 28 or 29.")


@reg
def time_piece(rng):
    h, m = rng.randint(0, 23), rng.randint(0, 59)
    return sql_item([], f"SELECT strftime('%H:%M', '2024-05-01 {h:02d}:{m:02d}:30');", f"{h:02d}:{m:02d}", "%H and %M are the hours (24-hour clock) and minutes, with leading zeros.")


@reg
def time_add_minutes(rng):
    h, m, n = rng.randint(0, 20), rng.randint(0, 59), rng.randint(20, 200)
    t = dt.datetime(2024, 1, 1, h, m) + dt.timedelta(minutes=n)
    return sql_item([], f"SELECT time('{h:02d}:{m:02d}:00', '+{n} minutes');", t.strftime("%H:%M:%S"), "time() adds minutes and wraps past midnight, keeping only the clock part.")


@reg
def datetime_add_hours(rng):
    h, n = rng.randint(0, 23), rng.randint(5, 60)
    t = dt.datetime(2024, 2, 27, h, 0) + dt.timedelta(hours=n)
    return sql_item([], f"SELECT datetime('2024-02-27 {h:02d}:00:00', '+{n} hours');", t.strftime("%Y-%m-%d %H:%M:%S"), "datetime() carries hours over into days (and across the leap day).")


# ── Counting days ──────────────────────────────────────────────────────

@reg
def days_between_int(rng):
    a, b = sorted([_d(rng), _d(rng)])
    return sql_item([], f"SELECT CAST(julianday('{b}') - julianday('{a}') AS INTEGER);", days_between(a, b), "julianday gives a day count; the difference is the days between, and CAST makes it a whole number.")


@reg
def days_between_real(rng):
    a, b = sorted([_d(rng), _d(rng)])
    return sql_item([], f"SELECT julianday('{b}') - julianday('{a}');", float(days_between(a, b)), "Without CAST the difference is a real, so it prints with .0.")


@reg
def days_in_february(rng):
    y = rng.choice([2023, 2024, 2025, 2028])
    return sql_item([], f"SELECT CAST(julianday('{y}-03-01') - julianday('{y}-02-01') AS INTEGER);", days_between(dt.date(y, 2, 1), dt.date(y, 3, 1)), "From 1 February to 1 March: the length of February in that year.")


@reg
def julian_value(rng):
    d = _d(rng)
    return sql_item([], f"SELECT julianday('{d}');", _jd(d), "A Julian day number counts days since a very old origin; midnight is .5 because the Julian day starts at noon.")


@reg
def days_to_year_end(rng):
    d = _d(rng)
    end = add_years(start_of_year(d), 1)
    return sql_item([], f"SELECT CAST(julianday('{d}', 'start of year', '+1 year') - julianday('{d}') AS INTEGER);", days_between(d, end), "From the date to the next 1 January.")


@reg
def days_since_new_year(rng):
    d = _d(rng)
    return sql_item([], f"SELECT CAST(julianday('{d}') - julianday('{d}', 'start of year') AS INTEGER);", day_of_year(d) - 1, "The days since 1 January of that year: one less than the day of the year.")


@reg
def whole_years_old(rng):
    b = rand_date(rng, "1990-01-01", "2010-12-31")
    on = dt.date(2025, 6, 15)
    days = days_between(b, on)
    return sql_item([], f"SELECT CAST((julianday('{on}') - julianday('{b}')) / 365.25 AS INTEGER);", int(days / 365.25), "Days alive divided by 365.25, with the fraction cut off by CAST: the age in whole years.")


@reg
def epoch_seconds(rng):
    d = rand_date(rng, "1970-01-02", "2030-01-01")
    secs = (d - dt.date(1970, 1, 1)).days * 86400
    return sql_item([], f"SELECT strftime('%s', '{d}');", str(secs), "%s is the number of seconds since 1 January 1970 (as text).")


@reg
def from_epoch(rng):
    d = rand_date(rng, "1970-01-02", "2030-01-01")
    secs = (d - dt.date(1970, 1, 1)).days * 86400 + rng.randint(0, 80000)
    return sql_item([], f"SELECT date({secs}, 'unixepoch');", iso(d), "A count of seconds since 1970 turned back into a date; the leftover seconds fall inside that day.")


# ── A table of dates ───────────────────────────────────────────────────

@reg
def table_count_between(rng):
    t = _dates(rng, 6)
    a, b = sorted(rand_date(rng, "2024-01-01", "2024-12-31") for _ in range(2))
    n = sum(1 for d in DS(t) if a <= d <= b)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE d BETWEEN '{a}' AND '{b}';", n, "ISO dates sort correctly as plain text, so BETWEEN works on them directly.")


@reg
def table_max(rng):
    t = _dates(rng)
    return sql_item([t], "SELECT MAX(d) FROM t;", iso(max(DS(t))), "Because the year comes first, the biggest text is the latest date.")


@reg
def table_span(rng):
    t = _dates(rng)
    return sql_item([t], "SELECT CAST(julianday(MAX(d)) - julianday(MIN(d)) AS INTEGER) FROM t;", days_between(min(DS(t)), max(DS(t))), "The days from the earliest date to the latest.")


@reg
def table_earliest_plus(rng):
    t = _dates(rng)
    n = rng.randint(30, 120)
    return sql_item([t], f"SELECT date(MIN(d), '+{n} days') FROM t;", iso(add_days(min(DS(t)), n)), "Find the earliest date, then add days to it.")


@reg
def table_months(rng):
    t = _dates(rng, 6)
    n = len({(d.year, d.month) for d in DS(t)})
    return sql_item([t], "SELECT COUNT(DISTINCT strftime('%Y-%m', d)) FROM t;", n, "Turn each date into its year-month and count the different ones.")


@reg
def table_in_month(rng):
    t = _dates(rng, 6)
    m = rng.choice([d.month for d in DS(t)])
    n = sum(1 for d in DS(t) if d.month == m)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE strftime('%m', d) = '{m:02d}';", n, "%m gives text with a leading zero, so compare with '03', not 3.")


@reg
def table_weekend(rng):
    t = _dates(rng, 6)
    n = sum(1 for d in DS(t) if weekday_w(d) in (0, 6))
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE strftime('%w', d) IN ('0', '6');", n, "Sunday is 0 and Saturday is 6: the dates that fall on a weekend.")


@reg
def table_busiest_month(rng):
    t = _dates(rng, 6)
    counts: dict = {}
    for d in DS(t):
        counts[d.month] = counts.get(d.month, 0) + 1
    best = max(counts.values())
    top = [m for m, c in counts.items() if c == best]
    if len(top) != 1:
        raise Retry
    return sql_item([t], "SELECT strftime('%m', d) FROM t GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1;", f"{top[0]:02d}", "Group by the month piece; the biggest group's month number (text, so with its zero).")


@reg
def table_after_cutoff(rng):
    t = _dates(rng, 6)
    c = rand_date(rng, "2024-03-01", "2024-10-31")
    n = rng.randint(20, 90)
    cut = add_days(c, -n)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE d > date('{c}', '-{n} days');", sum(1 for d in DS(t) if d > cut), "The cutoff is worked out once; only later dates are counted.")


@reg
def table_days_after_first(rng):
    t = _dates(rng)
    first = min(DS(t))
    return sql_item([t], "SELECT MAX(CAST(julianday(d) - julianday((SELECT MIN(d) FROM t)) AS INTEGER)) FROM t;", days_between(first, max(DS(t))), "Each date's distance from the earliest, and the biggest of those.")


@reg
def table_same_weekday(rng):
    t = _dates(rng, 6)
    w = weekday_w(rng.choice(DS(t)))
    n = sum(1 for d in DS(t) if weekday_w(d) == w)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE strftime('%w', d) = '{w}';", n, "The dates that fall on that weekday.")


@reg
def table_last_day_count(rng):
    t = _dates(rng, 6)
    n = sum(1 for d in DS(t) if last_day_of_month(d) == d)
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE d = date(d, 'start of month', '+1 month', '-1 day');", n, "A date is the last of its month when it equals that month's computed last day.")
