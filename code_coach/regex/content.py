"""The regex tasks, easiest first.

The progression follows RegexOne's because it is the right one - literal
characters, then classes, sets, repetition, anchors, groups, and finally
the patterns people actually write - but the strings are this project's
own.

Every task carries at least one pitfall: the wrong answer a person
reaches for first. The suite runs each one and requires it to fail,
because a task whose skip list does not catch its own classic mistake is
not testing the idea it is named after.
"""

from __future__ import annotations

from code_coach.regex import RegexTask

BASICS = "Letters and digits"
REPEATS = "Sets and repeats"
SHAPE = "Anchors and groups"
REAL = "The real world"

TASKS: tuple[RegexTask, ...] = (
    # ── Letters and digits ──────────────────────────────────
    RegexTask(
        id="rx-literal",
        title="A word, anywhere",
        family=BASICS,
        level=1,
        brief="Find every line that mentions 'log'.",
        match=("error log", "logbook", "the log file"),
        skip=("loop", "leg day", "l o g"),
        answer="log",
        pitfalls=("lo", "l.g"),
        hint="Most characters stand for themselves.",
        lesson="Most characters match themselves: log finds those three "
               "letters in a row, anywhere in the text.",
    ),
    RegexTask(
        id="rx-digit",
        title="Any digit",
        family=BASICS,
        level=1,
        brief="Find lines that contain at least one digit.",
        match=("room 101", "v2", "7 apples"),
        skip=("room", "version", "seven apples"),
        answer=r"\d",
        pitfalls=(r"\d\d", r"\w"),
        hint="There is a two-character code that means 'any digit'.",
        lesson=r"\d is any digit, 0 to 9. One \d is enough to ask whether "
               r"there is a digit anywhere.",
    ),
    RegexTask(
        id="rx-escape-dot",
        title="A real full stop",
        family=BASICS,
        level=1,
        brief="Find prices written with a decimal point, like 3.50.",
        match=("3.50", "total 12.99", "0.05"),
        skip=("3,50", "350", "3x50"),
        answer=r"\d\.\d\d",
        pitfalls=(r"\d.\d\d", r"\d+"),
        hint="A dot on its own means something special. How do you mean "
             "just a dot?",
        lesson=r"A plain . matches any character at all. For an actual "
               r"full stop, escape it: \.",
    ),
    # ── Sets and repeats ────────────────────────────────────
    RegexTask(
        id="rx-set",
        title="One of these letters",
        family=REPEATS,
        level=1,
        brief="Match cat, hat and mat, but not bat, rat or sat.",
        match=("cat", "hat", "mat"),
        skip=("bat", "rat", "sat"),
        answer="[chm]at",
        pitfalls=(".at", "[a-z]at"),
        hint="Square brackets hold a choice of single characters.",
        lesson="[chm] matches exactly one character, and it has to be c, "
               "h or m.",
    ),
    RegexTask(
        id="rx-negated-set",
        title="Anything but this",
        family=REPEATS,
        level=1,
        brief="Match pin, pan and pun, but not pen.",
        match=("pin", "pan", "pun"),
        skip=("pen",),
        answer="p[^e]n",
        # Not "p[aiu]n": that is a correct answer, and the engine check
        # said so. [^e] on its own is the real mistake - p and n are not
        # e either, so it finds something in "pen".
        pitfalls=("p.n", "[^e]"),
        hint="A ^ as the first thing inside square brackets turns the "
             "choice around.",
        lesson="[^e] is any one character except e. The ^ only means 'not' "
               "when it is first inside the brackets.",
    ),
    RegexTask(
        id="rx-range",
        title="A range of letters",
        family=REPEATS,
        level=2,
        brief="Match codes that start with a capital A to F and then two "
              "digits.",
        match=("A12", "C07", "F99"),
        skip=("G12", "a12", "AB1"),
        answer=r"[A-F]\d\d",
        pitfalls=(r"[A-Z]\d\d", r"\w\d\d"),
        hint="Inside square brackets, a dash makes a range.",
        lesson="[A-F] is any one capital from A to F. Ranges are "
               "case-sensitive: lower-case a is not in A-F.",
    ),
    RegexTask(
        id="rx-exact-count",
        title="Exactly five",
        family=REPEATS,
        level=2,
        brief="Match US ZIP codes: five digits in a row.",
        match=("90210", "02134", "12345"),
        skip=("1234", "9021", "12-345"),
        answer=r"\d{5}",
        pitfalls=(r"\d{4}", r"\d+"),
        hint="Curly braces after something say how many times.",
        lesson=r"\d{5} is exactly five digits. {2,4} would mean two to four, "
               r"and {3,} three or more.",
    ),
    RegexTask(
        id="rx-plus",
        title="One or more",
        family=REPEATS,
        level=2,
        brief="Match goo, gooo, gooooal - a g and at least two o's - but not "
              "plain go.",
        match=("goo", "goooo", "gooooal"),
        skip=("go", "g", "gone"),
        answer="goo+",
        pitfalls=("go*", "go+"),
        hint="How many o's must there be at the very least?",
        lesson="+ means one or more of the thing before it, and * zero or "
               "more. go* even matches a g on its own.",
    ),
    RegexTask(
        id="rx-optional",
        title="Maybe a letter",
        family=REPEATS,
        level=2,
        brief="Match both spellings, color and colour.",
        match=("color", "colour", "colours"),
        skip=("colr", "coolor", "colouur"),
        answer="colou?r",
        pitfalls=("colou*r", "colo.r"),
        hint="One letter is optional. There is a character that says so.",
        lesson="? makes the thing before it optional: u? is one u or none, "
               "and never two.",
    ),
    RegexTask(
        id="rx-whitespace",
        title="Spaces and tabs",
        family=REPEATS,
        level=2,
        brief="Match numbered list lines: a number, a dot, then at least "
              "one space or tab before the text.",
        match=("1. milk", "2.\teggs", "10.   bread"),
        skip=("1.milk", "2.eggs", "3 butter"),
        answer=r"\d+\.\s+\w",
        pitfalls=(r"\d+\. \w", r"\d+\.\s*\w"),
        hint="There is a code for any whitespace, tabs included.",
        lesson=r"\s is any whitespace - a space, a tab, a newline. \s+ is at "
               r"least one of them.",
    ),
    # ── Anchors and groups ──────────────────────────────────
    RegexTask(
        id="rx-anchors",
        title="Nothing else on the line",
        family=SHAPE,
        level=2,
        brief="Match lines that are only a time like 09:30, with nothing "
              "before or after it.",
        match=("09:30", "23:59", "00:00"),
        skip=("at 09:30", "09:30pm", "109:30"),
        answer=r"^\d\d:\d\d$",
        pitfalls=(r"\d\d:\d\d", r"^\d\d:\d\d"),
        hint="Two characters pin a pattern to the start and the end.",
        lesson="^ pins the pattern to the start and $ to the end. Without "
               "them a pattern is happy to be found anywhere.",
    ),
    RegexTask(
        id="rx-alternation",
        title="This or that",
        family=SHAPE,
        level=2,
        brief="Match lines about cats or dogs, not other animals.",
        match=("I have a cat", "dog walker", "cats and dogs"),
        skip=("hamster", "parrot", "cod liver oil"),
        answer="cat|dog",
        pitfalls=("cat", "c|d"),
        hint="There is a character that means 'or'.",
        lesson="| means or, and it splits the whole pattern: cat|dog is "
               "either word, not 'ca' then t-or-d then 'og'.",
    ),
    RegexTask(
        id="rx-word-boundary",
        title="The word on its own",
        family=SHAPE,
        level=3,
        brief="Match the word cat by itself - not inside catalog or "
              "bobcat.",
        match=("a cat sat", "cat", "the cat."),
        skip=("catalog", "concatenate", "bobcat"),
        answer=r"\bcat\b",
        pitfalls=("cat", " cat "),
        hint="Spaces are not the answer - what about the start of a line, "
             "or a full stop?",
        lesson=r"\b is the edge of a word: between a letter and a non-letter. "
               r"It takes up no space, so \bcat\b is cat with no letters "
               r"touching it.",
    ),
    RegexTask(
        id="rx-capture-year",
        title="Pull out the year",
        family=SHAPE,
        level=3,
        brief="Match dates written 2024-03-15, and capture the year.",
        match=("2024-03-15", "1999-12-31", "2000-01-01"),
        skip=("15/03/2024", "2024", "24-03-15"),
        capture=(("2024-03-15", "2024"), ("1999-12-31", "1999"),
                 ("2000-01-01", "2000")),
        answer=r"(\d{4})-\d\d-\d\d",
        pitfalls=(r"\d{4}-\d\d-\d\d", r"(\d{4})"),
        hint="Match the whole date, and put parentheses around the part you "
             "want to keep.",
        lesson="Parentheses capture: whatever matches inside them is group "
               "1, which is how you pull one piece out of a match.",
    ),
    RegexTask(
        id="rx-capture-filename",
        title="The name without .png",
        family=SHAPE,
        level=3,
        brief="Match .png file names and capture the name without the "
              "extension. Names can contain dashes.",
        match=("cat.png", "photo_1.png", "my-logo.png"),
        skip=("cat.jpg", "png", "notes.png.txt"),
        capture=(("cat.png", "cat"), ("photo_1.png", "photo_1"),
                 ("my-logo.png", "my-logo")),
        answer=r"^([\w-]+)\.png$",
        pitfalls=(r"([\w-]+)\.png", r"(\w+)\.png$"),
        hint=r"\w covers letters, digits and underscore - but not a dash. "
             r"And where must the .png be?",
        lesson=r"\w does not include -, so a name with a dash needs [\w-]. "
               r"And $ is what stops notes.png.txt from passing.",
    ),
    # ── The real world ──────────────────────────────────────
    RegexTask(
        id="rx-phone",
        title="Phone numbers",
        family=REAL,
        level=3,
        brief="Match phone numbers written 555-123-4567 or (555) 123-4567.",
        match=("555-123-4567", "(555) 123-4567", "call 555-987-6543"),
        skip=("555-1234", "5551234567", "(555)123-45"),
        answer=r"(\(\d{3}\) |\d{3}-)\d{3}-\d{4}",
        pitfalls=(r"\d{3}-\d{3}-\d{4}", r"\d{3}-\d{4}"),
        hint="Two ways to write the area code - so an alternation, in a "
             "group, before the part they share.",
        lesson=r"A group can hold an alternation: (A|B) then the rest. And "
               r"brackets that are really in the text need escaping: \( \).",
    ),
    RegexTask(
        id="rx-email",
        title="Simple email addresses",
        family=REAL,
        level=3,
        brief="Match simple email addresses: name@domain.tld. Names may "
              "contain dots and underscores.",
        match=("ada@example.com", "g.hopper@navy.mil", "a_b@c.io"),
        skip=("ada@", "@example.com", "ada example.com", "ada@example"),
        answer=r"[\w.]+@\w+\.\w+",
        pitfalls=(r"\w+@\w+", r".+@.+"),
        hint="Three parts: something, an @, and a domain that has a dot in "
             "it.",
        lesson="Real email validation is famously hard; for finding "
               "addresses in text, a pattern this simple is what people "
               "actually use.",
    ),
    RegexTask(
        id="rx-hex-colour",
        title="Hex colours",
        family=REAL,
        level=3,
        brief="Match CSS hex colours: a # and then exactly 3 or exactly 6 "
              "hex digits.",
        match=("#fff", "#1a2B3c", "color: #09F;"),
        skip=("#ggg", "#12345", "#1234567"),
        answer=r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b",
        pitfalls=(r"#[0-9a-fA-F]{3}", r"#\w+"),
        hint="Two lengths, so an alternation - and something to stop a "
             "longer run from counting.",
        lesson=r"\b after the digits is what stops #12345 matching as "
               r"#123: there has to be a word edge there, not another digit.",
    ),
    RegexTask(
        id="rx-log-level",
        title="Log levels",
        family=REAL,
        level=3,
        brief="From log lines like '[ERROR] disk full', capture the level. "
              "Levels are capital letters at the very start.",
        match=("[ERROR] disk full", "[WARN] low memory", "[INFO] started"),
        skip=("ERROR disk full", "[] empty", "[error] lower case"),
        capture=(("[ERROR] disk full", "ERROR"), ("[WARN] low memory", "WARN"),
                 ("[INFO] started", "INFO")),
        answer=r"^\[([A-Z]+)\]",
        pitfalls=(r"\[(\w+)\]", r"\[(.*)\]"),
        hint="Square brackets in the text are special in a pattern, so "
             "they need escaping.",
        lesson=r"[A-Z]+ insists on capitals, which is what rejects [error]. "
               r"And .* would happily match nothing, which is what lets [] "
               r"through.",
    ),
)
