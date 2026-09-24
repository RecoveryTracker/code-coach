"""Thirteen more regex tasks, merged into the list by level.

Two new families come in at the top: lazy matching and backreferences,
then lookarounds. Everything here uses only what Python's re and
JavaScript's RegExp agree on - no named groups, no inline flags - so the
same answer is right in both, which the suite checks.
"""

from __future__ import annotations

from code_coach.regex import RegexTask

BASICS = "Letters and digits"
REPEATS = "Sets and repeats"
SHAPE = "Anchors and groups"
REAL = "The real world"
LAZY = "Lazy and repeated"
LOOK = "Looking around"

MORE_TASKS: tuple[RegexTask, ...] = (
    # ── Level 1 ─────────────────────────────────────────────
    RegexTask(
        id="rx-case",
        title="Capitals count",
        family=BASICS,
        level=1,
        brief="Find lines that mention 'Cat' with a capital C - the name of "
              "the band, not the animal.",
        match=("Cat food tour", "The Cat live", "Catalog of Cat songs"),
        skip=("cat food", "the cat sat", "CAT"),
        answer="Cat",
        pitfalls=("cat", "[Cc]at", "[Cc][Aa][Tt]"),
        hint="A pattern cares about capital letters unless told otherwise.",
        lesson="Matching is case-sensitive: C and c are different "
               "characters. [Cc] is how you say either one, which is exactly "
               "what this task did not want.",
    ),
    RegexTask(
        id="rx-any-char",
        title="Any one character",
        family=BASICS,
        level=1,
        brief="Find b, then exactly one character of any kind, then g.",
        match=("bag", "b1g", "b-g"),
        skip=("bg", "b12g", "bang"),
        answer="b.g",
        pitfalls=("b.*g", r"b\wg"),
        hint="One symbol stands for any single character at all.",
        lesson=". is any one character - a letter, a digit, a dash. Exactly "
               "one: b.g needs something between b and g, and only one thing.",
    ),
    # ── Level 2 ─────────────────────────────────────────────
    RegexTask(
        id="rx-count-range",
        title="Between two and four",
        family=REPEATS,
        level=2,
        brief="Find lines that are a number of two, three or four digits - "
              "and nothing else.",
        match=("42", "100", "2026"),
        skip=("7", "12345", "4a"),
        answer=r"^\d{2,4}$",
        pitfalls=(r"\d{2,4}", r"^\d+$"),
        hint="{2,4} means 'between two and four of the thing before'. "
             "Then pin both ends of the line.",
        lesson=r"{2,4} sets a range of repeats. Without ^ and $, \d{2,4} "
               r"happily finds four digits inside 12345, so the length limit "
               r"only means something once the ends are pinned.",
    ),
    RegexTask(
        id="rx-trailing-space",
        title="Spaces at the end",
        family=SHAPE,
        level=2,
        brief="Find lines that end with whitespace - spaces or a tab - the "
              "kind a code review complains about.",
        match=("line ", "tabbed\t", "two  "),
        skip=("clean", "  leading", "mid dle"),
        answer=r"\s+$",
        pitfalls=(r"\s+", r" $"),
        hint=r"\s is any whitespace character. $ is the end of the line.",
        lesson=r"$ anchors to the end. \s+$ is whitespace that runs right up "
               r"to it - spaces in the middle or at the start do not count, "
               r"and \s catches the tab that a plain space would miss.",
    ),
    RegexTask(
        id="rx-not-comment",
        title="Not a comment",
        family=SHAPE,
        level=2,
        brief="Find lines that do not start with #.",
        match=("code()", "x = 1  # note", " # indented"),
        skip=("# comment", "#!shebang", "#"),
        answer="^[^#]",
        pitfalls=("[^#]", r"^\w"),
        hint="Inside [ ], a ^ at the front means 'not'. Outside, ^ means "
             "the start of the line. This task needs both.",
        lesson="^[^#] reads 'at the start, one character that is not #'. "
               "Same symbol, two jobs: outside brackets ^ anchors, inside "
               "them it negates.",
    ),
    # ── Level 3 ─────────────────────────────────────────────
    RegexTask(
        id="rx-ipv4",
        title="An IP address",
        family=REAL,
        level=3,
        brief="Find lines that are an IPv4 address: four groups of one to "
              "three digits, joined by dots.",
        match=("192.168.0.1", "10.0.0.255", "8.8.8.8"),
        skip=("192.168.0", "1.2.3.4.5", "1.2.3.a"),
        answer=r"^(\d{1,3}\.){3}\d{1,3}$",
        pitfalls=(r"^[\d.]+$", r"(\d{1,3}\.){3}\d{1,3}"),
        hint="A group can be repeated like a single character: ( ){3}. "
             "Three 'digits then a dot', then the last digits.",
        lesson="Putting a piece in parentheses lets a count apply to all of "
               "it. It checks the shape, not the values - 999.999.999.999 "
               "passes, and saying 0 to 255 is a job for code, not a regex.",
    ),
    RegexTask(
        id="rx-iso-date",
        title="A real date",
        family=REAL,
        level=3,
        brief="Find lines that are a date written YYYY-MM-DD, with a month "
              "from 01 to 12 and a day from 01 to 31.",
        match=("2026-09-24", "1999-12-31", "2000-01-01"),
        skip=("2026-13-01", "2026-9-24", "2026-00-10", "2026-02-32"),
        answer=r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$",
        pitfalls=(r"^\d{4}-\d{2}-\d{2}$", r"^\d{4}-\d{1,2}-\d{1,2}$"),
        hint="Split the month into the cases that are allowed: 0 then 1-9, "
             "or 1 then 0-2. The day works the same way.",
        lesson="A regex cannot count to 12, but it can list the shapes that "
               "are allowed: 0[1-9] or 1[0-2]. It still lets 02-31 through - "
               "whether February has 31 days is a question for code.",
    ),
    RegexTask(
        id="rx-24-hour",
        title="A 24-hour time",
        family=REAL,
        level=3,
        brief="Find lines that are a time on a 24-hour clock, like 09:30 or "
              "23:59. Hours go to 23, minutes to 59.",
        match=("09:30", "23:59", "00:00"),
        skip=("24:00", "9:30", "12:60", "12:3", "123:45"),
        answer=r"^([01]\d|2[0-3]):[0-5]\d$",
        pitfalls=(r"^\d\d:\d\d$", r"([01]\d|2[0-3]):[0-5]\d"),
        hint="Hours are 00-19 or 20-23: two cases joined with |. Minutes "
             "start with 0-5.",
        lesson="The | inside the group lists the hour shapes that are real. "
               "And without the anchors, 123:45 still contains 23:45 - a "
               "pattern that is right about the middle can be wrong about "
               "the whole line.",
    ),
    RegexTask(
        id="rx-lazy",
        title="Stop at the first",
        family=LAZY,
        level=3,
        brief="Capture the text inside the first pair of double quotes.",
        match=('say "hi" and "bye"', '"a" "b"', 'x "long one" y'),
        skip=("no quotes", 'one " only'),
        capture=(('say "hi" and "bye"', "hi"), ('"a" "b"', "a"),
                 ('x "long one" y', "long one")),
        answer=r'"(.*?)"',
        pitfalls=(r'"(.*)"', r'"(\w+)"'),
        hint="* grabs as much as it can. Adding ? after it makes it take "
             "as little as it can.",
        lesson=r'.* is greedy: it runs to the last quote on the line and '
               r'captures hi" and "bye. .*? is lazy and stops at the first '
               r'quote that lets the match finish.',
    ),
    RegexTask(
        id="rx-backreference",
        title="The same word twice",
        family=LAZY,
        level=3,
        brief="Find a word typed twice in a row, like 'the the', and capture "
              "the word.",
        match=("the the cat", "it was was fine", "a a"),
        skip=("the then", "one two", "thethe"),
        capture=(("the the cat", "the"), ("it was was fine", "was"),
                 ("a a", "a")),
        answer=r"\b(\w+) \1\b",
        pitfalls=(r"(\w+) \1", r"(\w+) (\w+)"),
        hint=r"\1 means 'whatever group 1 matched', exactly. Word "
             r"boundaries stop 'the' from matching the start of 'then'.",
        lesson=r"A backreference matches the same text again, not the same "
               r"pattern. Without \b at both ends, 'the then' passes, "
               r"because 'then' starts with 'the'.",
    ),
    # ── Level 4 ─────────────────────────────────────────────
    RegexTask(
        id="rx-negative-lookahead",
        title="Not followed by",
        family=LOOK,
        level=4,
        brief="Find 'cat' - but not when it is the start of 'catalog'.",
        match=("cat", "my cat sat", "cats"),
        skip=("catalog", "catalogue", "a catalog"),
        answer="cat(?!alog)",
        pitfalls=("cat", "cat[^a]"),
        hint="(?! ) looks ahead without using up anything: it only says "
             "what must not come next.",
        lesson="(?!alog) is a negative lookahead - a check on what follows, "
               "not part of the match. cat[^a] gets close, but it needs a "
               "character after cat, so a line that is just 'cat' fails.",
    ),
    RegexTask(
        id="rx-lookahead-rules",
        title="A letter and a digit, anywhere",
        family=LOOK,
        level=4,
        brief="Find passwords of at least eight characters that contain at "
              "least one digit and at least one lowercase letter, in any order.",
        match=("abc12345", "9lives-ok", "passw0rd"),
        skip=("abcdefgh", "12345678", "ab1"),
        answer=r"^(?=.*\d)(?=.*[a-z]).{8,}$",
        pitfalls=(r"^[a-z0-9]{8,}$", r"\d.*[a-z]"),
        hint="Each (?=.*something) checks the whole line from the start "
             "without moving along it, so you can stack them.",
        lesson=r"Lookaheads at the start are rules the whole line must meet. "
               r"\d.*[a-z] only finds a digit before a letter; two "
               r"lookaheads check for each in any order.",
    ),
    RegexTask(
        id="rx-lookbehind",
        title="After a dollar sign",
        family=LOOK,
        level=4,
        brief="Capture the amount of dollars - the digits straight after a $.",
        match=("$40", "costs $7 now", "$1200"),
        skip=("40", "€40", "$ 40"),
        capture=(("$40", "40"), ("costs $7 now", "7"), ("$1200", "1200")),
        answer=r"(?<=\$)(\d+)",
        pitfalls=(r"(\d+)", r"\$\d+"),
        hint=r"$ is special, so a real dollar sign is \$. (?<= ) checks "
             r"what comes before without including it.",
        lesson=r"(?<=\$) is a lookbehind: the $ must be there but is not part "
               r"of the match. \$(\d+) gets the same group here - the "
               r"lookbehind matters when the whole match, not a group, is "
               r"what you keep.",
    ),
)
