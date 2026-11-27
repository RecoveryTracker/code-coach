"""C hunts: bugs the compiler lets through, all of them well-defined.

Every program here does exactly what it says on every compiler and every
build - integer division truncates, `%` keeps the sign of its left side,
unsigned subtraction wraps, `=` assigns, a `switch` falls through. None
of them is undefined behaviour, so the broken program misbehaves the same
way everywhere, and the fix is a line or two.

Run through kata/c_harness.py, so each hunt gives one C type per
parameter and its return type. The same rules hold as for every hunt,
checked by tests/test_bughunt.py.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

C = "C"


def _average(nums):
    return sum(nums) / len(nums) if nums else 0.0


def _power_of_two(n):
    return 2 ** n


def _ticket_price(age, is_member):
    price = 5 if age < 12 else 7 if age >= 65 else 10
    return price - 2 if is_member == 1 else price


def _day_after(today, offset):
    return (today + offset) % 7


def _count_words(text):
    return len([w for w in text.split(" ") if w])


def _shout(text):
    return "".join(c.upper() if "a" <= c <= "z" else c for c in text)


def _chars_over(text, limit):
    return max(0, len(text) - limit)


def _score(plays):
    return sum({"T": 6, "F": 3, "S": 2}.get(p, 0) for p in plays)


C_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-c-int-average",
        title="The average of 1 and 2 is 1",
        family=C,
        language="c",
        level=1,
        report="The class average is wrong by up to a whole point. Scores of 1 "
               "and 2 should average 1.5 and the report says 1. Lists that add "
               "up evenly, like 4 and 6, come out right.",
        name="average",
        params=("nums",),
        types=("int[]",),
        returns="double",
        start=(
            "// The average of a list of scores.\n"
            "static int total(const int *nums, int count) {\n"
            "    int sum = 0;\n"
            "    for (int i = 0; i < count; i++) {\n"
            "        sum += nums[i];\n"
            "    }\n"
            "    return sum;\n"
            "}\n"
            "\n"
            "double average(const int *nums, int nums_len) {\n"
            "    if (nums_len == 0) {\n"
            "        return 0;\n"
            "    }\n"
            "    return total(nums, nums_len) / nums_len;\n"
            "}\n"
        ),
        fixed=(
            "// The average of a list of scores.\n"
            "static int total(const int *nums, int count) {\n"
            "    int sum = 0;\n"
            "    for (int i = 0; i < count; i++) {\n"
            "        sum += nums[i];\n"
            "    }\n"
            "    return sum;\n"
            "}\n"
            "\n"
            "double average(const int *nums, int nums_len) {\n"
            "    if (nums_len == 0) {\n"
            "        return 0;\n"
            "    }\n"
            "    return (double)total(nums, nums_len) / nums_len;\n"
            "}\n"
        ),
        solve=_average,
        reported=([1, 2],),
        cases=(([],), ([7],), ([4, 6],), ([2, 3],), ([1, 2, 2, 2],), ([1, 2],)),
        cause="Both operands of the / are int, so C divides as integers and "
              "throws the fraction away: 3 / 2 is 1. The result is only "
              "converted to double after the division has happened.",
        decoys=(
            "The loop stops one score early, so the last score is left out.",
            "double cannot hold a value like 1.5 exactly.",
            "sum starts at the wrong value, so every total is off.",
        ),
        lesson="In C the types of the operands pick the kind of division, not "
               "the type you assign the answer to. Make one side a double "
               "BEFORE the / - `(double)total / count` - not after.",
        hint="Try two scores that do not add up to an even number: average([1, 2]).",
        checks=((([1, 2],), 1.5), (([4, 6],), 5.0), (([],), 0.0), (([1, 2, 2, 2],), 1.75)),
    ),
    Hunt(
        id="hunt-c-stray-semicolon",
        title="Every power of two is 2",
        family=C,
        language="c",
        level=1,
        report="power_of_two(5) should be 32 and it gives 2. So does power_of_two(8). "
               "power_of_two(1) is right.",
        name="power_of_two",
        params=("n",),
        types=("int",),
        returns="int",
        start=(
            "// 2 to the power of n, by doubling n times.\n"
            "static int twice(int x) {\n"
            "    return x * 2;\n"
            "}\n"
            "\n"
            "int power_of_two(int n) {\n"
            "    int result = 1;\n"
            "    int i;\n"
            "    for (i = 0; i < n; i++);\n"
            "        result = twice(result);\n"
            "    return result;\n"
            "}\n"
        ),
        fixed=(
            "// 2 to the power of n, by doubling n times.\n"
            "static int twice(int x) {\n"
            "    return x * 2;\n"
            "}\n"
            "\n"
            "int power_of_two(int n) {\n"
            "    int result = 1;\n"
            "    int i;\n"
            "    for (i = 0; i < n; i++)\n"
            "        result = twice(result);\n"
            "    return result;\n"
            "}\n"
        ),
        solve=_power_of_two,
        reported=(5,),
        cases=((0,), (1,), (3,), (5,), (8,), (10,)),
        cause="The `;` straight after the for's parentheses is the loop's whole "
              "body: an empty statement. The loop spins n times doing nothing, "
              "and the doubling underneath, only indented, runs once.",
        decoys=(
            "twice multiplies by 3 instead of 2, so the result is off.",
            "i starts at 0, so the loop runs one time too many.",
            "result is never returned, so the caller sees a leftover value.",
        ),
        lesson="C ignores indentation. A `;` right after `for (...)`, `while "
               "(...)` or `if (...)` ends the statement, and the line you "
               "meant as the body just runs on its own. Always use braces, "
               "and let the compiler's -Wall tell you about it.",
        hint="Compare a count of 1 with a count of 5: power_of_two(5).",
        checks=(((5,), 32), ((0,), 1), ((1,), 2), ((10,), 1024)),
    ),
    Hunt(
        id="hunt-c-assign-in-if",
        title="Non-members get the member price",
        family=C,
        language="c",
        level=2,
        report="Everyone is getting the member discount. A 30-year-old who is not "
               "a member (is_member 0) should pay 10 and is charged 8. Members "
               "pay the right amount.",
        name="ticket_price",
        params=("age", "is_member"),
        types=("int", "int"),
        returns="int",
        start=(
            "// Ticket price: by age, then 2 off for members.\n"
            "static int base_price(int age) {\n"
            "    if (age < 12) {\n"
            "        return 5;\n"
            "    }\n"
            "    if (age >= 65) {\n"
            "        return 7;\n"
            "    }\n"
            "    return 10;\n"
            "}\n"
            "\n"
            "int ticket_price(int age, int is_member) {\n"
            "    int price = base_price(age);\n"
            "    if (is_member = 1) {\n"
            "        price = price - 2;\n"
            "    }\n"
            "    return price;\n"
            "}\n"
        ),
        fixed=(
            "// Ticket price: by age, then 2 off for members.\n"
            "static int base_price(int age) {\n"
            "    if (age < 12) {\n"
            "        return 5;\n"
            "    }\n"
            "    if (age >= 65) {\n"
            "        return 7;\n"
            "    }\n"
            "    return 10;\n"
            "}\n"
            "\n"
            "int ticket_price(int age, int is_member) {\n"
            "    int price = base_price(age);\n"
            "    if (is_member == 1) {\n"
            "        price = price - 2;\n"
            "    }\n"
            "    return price;\n"
            "}\n"
        ),
        solve=_ticket_price,
        reported=(30, 0),
        cases=((30, 1), (8, 1), (30, 0), (8, 0), (70, 0), (70, 1)),
        cause="`=` assigns. `is_member = 1` stores 1 in is_member and the "
              "expression's value is that 1, which is true - so the "
              "discount applies to everyone, and the caller's flag is "
              "ignored.",
        decoys=(
            "base_price returns the wrong amount for adults.",
            "price - 2 should be price - 20 to match the discount.",
            "The age check uses >= where it should use >, so 65 is treated "
            "as a child.",
        ),
        lesson="`=` is assignment and `==` is comparison, and C lets you put "
               "an assignment inside a condition without complaint. Compile "
               "with -Wall: it warns about `if (x = 1)`. Some programmers "
               "write the constant first - `if (1 == x)` - so the typo "
               "will not compile.",
        hint="Call it as a non-member: ticket_price(30, 0).",
        checks=(((30, 0), 10), ((30, 1), 8), ((8, 0), 5), ((70, 0), 7), ((70, 1), 5)),
    ),
    Hunt(
        id="hunt-c-negative-modulo",
        title="Going back two days lands on day -1",
        family=C,
        language="c",
        level=2,
        report="Days are numbered 0 (Sunday) to 6 (Saturday). Going forward "
               "works: Saturday plus 1 is Sunday. Going back does not: from "
               "Monday (1), 2 days back should be Saturday (6) and the "
               "calendar says -1.",
        name="day_after",
        params=("today", "offset"),
        types=("int", "int"),
        returns="int",
        start=(
            "// Day of the week: 0 is Sunday, 6 is Saturday.\n"
            "static int week_length(void) {\n"
            "    return 7;\n"
            "}\n"
            "\n"
            "int day_after(int today, int offset) {\n"
            "    int days = week_length();\n"
            "    int moved = today + offset;\n"
            "    int result = moved % days;\n"
            "    return result;\n"
            "}\n"
        ),
        fixed=(
            "// Day of the week: 0 is Sunday, 6 is Saturday.\n"
            "static int week_length(void) {\n"
            "    return 7;\n"
            "}\n"
            "\n"
            "int day_after(int today, int offset) {\n"
            "    int days = week_length();\n"
            "    int moved = today + offset;\n"
            "    int result = (moved % days + days) % days;\n"
            "    return result;\n"
            "}\n"
        ),
        solve=_day_after,
        reported=(1, -2),
        cases=((0, 0), (3, 2), (6, 1), (2, 5), (0, -7), (1, -2), (2, -10)),
        cause="In C the result of % takes the sign of its LEFT operand, so "
              "-1 % 7 is -1, not 6. Moving back past day 0 makes `moved` "
              "negative and the remainder stays negative.",
        decoys=(
            "% divides instead of taking a remainder, so it rounds down.",
            "week_length returns 7 but the days only go up to 6.",
            "today + offset overflows when offset is negative.",
        ),
        lesson="`%` in C is a remainder that keeps the sign of the left "
               "side, unlike Python's. To wrap a possibly negative number "
               "into 0..n-1, add n and take % again: `(x % n + n) % n`.",
        hint="Move back: day_after(1, -2).",
        checks=(((1, -2), 6), ((6, 1), 0), ((2, -10), 6), ((0, -7), 0), ((3, 2), 5)),
    ),
    Hunt(
        id="hunt-c-last-word",
        title="The last word is never counted",
        family=C,
        language="c",
        level=3,
        report="The word counter is always one short. 'one two three' should "
               "be 3 words and it says 2; a single word says 0. Text that "
               "ends in a space ('hello ') is right.",
        name="count_words",
        params=("text",),
        types=("string",),
        returns="int",
        start=(
            "// Count the words: a word ends at a space or at the end of the text.\n"
            "static bool is_gap(char c) {\n"
            "    return c == ' ' || c == '\\0';\n"
            "}\n"
            "\n"
            "int count_words(const char *text) {\n"
            "    int len = (int)strlen(text);\n"
            "    int words = 0;\n"
            "    for (int i = 1; i < len; i++) {\n"
            "        if (is_gap(text[i]) && !is_gap(text[i - 1])) {\n"
            "            words++;\n"
            "        }\n"
            "    }\n"
            "    return words;\n"
            "}\n"
        ),
        fixed=(
            "// Count the words: a word ends at a space or at the end of the text.\n"
            "static bool is_gap(char c) {\n"
            "    return c == ' ' || c == '\\0';\n"
            "}\n"
            "\n"
            "int count_words(const char *text) {\n"
            "    int len = (int)strlen(text);\n"
            "    int words = 0;\n"
            "    for (int i = 1; i <= len; i++) {\n"
            "        if (is_gap(text[i]) && !is_gap(text[i - 1])) {\n"
            "            words++;\n"
            "        }\n"
            "    }\n"
            "    return words;\n"
            "}\n"
        ),
        solve=_count_words,
        reported=("one two three",),
        cases=(("",), ("hello",), ("hello ",), ("  ",), ("hello world",), ("a b c",),
               ("one two three",)),
        cause="The loop stops at `i < len`, so it never looks at the "
              "terminating '\\0' at text[len]. A word that ends the text "
              "ends there, not at a space, so the last word is never "
              "counted.",
        decoys=(
            "strlen counts the '\\0' too, so len is one too big.",
            "is_gap treats a space as part of a word.",
            "i starts at 1, so the first word is skipped.",
        ),
        lesson="A C string has len characters and then one more: the '\\0' at "
               "index len. Reading it is safe and often needed - `i <= len` "
               "- but reading index len + 1 would be out of bounds. "
               "Decide which index the loop must reach, and check both ends.",
        hint="Try a single word, then a sentence: count_words(\"hello\").",
        checks=((("one two three",), 3), (("hello",), 1), (("",), 0), (("hello ",), 1),
                (("a b c",), 3)),
    ),
    Hunt(
        id="hunt-c-char-range",
        title="Curly braces turn into square ones",
        family=C,
        language="c",
        level=3,
        report="shout() upper-cases text. 'hello' becomes 'HELLO', but the "
               "template 'hi {name}' comes out as 'HI [NAME]' - the curly "
               "braces turned into square brackets. Digits and spaces are fine.",
        name="shout",
        params=("text",),
        types=("string",),
        returns="string",
        start=(
            "// Upper-case every letter. The result is at most 63 characters.\n"
            "static char shift_up(char c) {\n"
            "    if (c >= 'a') {\n"
            "        return (char)(c - 32);\n"
            "    }\n"
            "    return c;\n"
            "}\n"
            "\n"
            "const char *shout(const char *text) {\n"
            "    static char buf[64];\n"
            "    int n = 0;\n"
            "    for (int i = 0; text[i] != '\\0' && n < 63; i++) {\n"
            "        buf[n++] = shift_up(text[i]);\n"
            "    }\n"
            "    buf[n] = '\\0';\n"
            "    return buf;\n"
            "}\n"
        ),
        fixed=(
            "// Upper-case every letter. The result is at most 63 characters.\n"
            "static char shift_up(char c) {\n"
            "    if (c >= 'a' && c <= 'z') {\n"
            "        return (char)(c - 32);\n"
            "    }\n"
            "    return c;\n"
            "}\n"
            "\n"
            "const char *shout(const char *text) {\n"
            "    static char buf[64];\n"
            "    int n = 0;\n"
            "    for (int i = 0; text[i] != '\\0' && n < 63; i++) {\n"
            "        buf[n++] = shift_up(text[i]);\n"
            "    }\n"
            "    buf[n] = '\\0';\n"
            "    return buf;\n"
            "}\n"
        ),
        solve=_shout,
        reported=("hi {name}",),
        cases=(("",), ("hello",), ("Hi there!",), ("room 101",), ("{x}",), ("a~b",),
               ("hi {name}",)),
        cause="The test only checks `c >= 'a'`, with no upper limit. Characters "
              "after 'z' in ASCII - { | } ~ - pass it too, and subtracting 32 "
              "turns them into [ \\ ] ^.",
        decoys=(
            "c - 32 is the wrong distance between lower and upper case.",
            "The buffer is static, so it keeps the text from an earlier call.",
            "char is signed, so the braces become negative numbers.",
        ),
        lesson="'a' to 'z' is a RANGE: it has a bottom and a top. A one-sided "
               "check lets every character past the other end through. "
               "Check both ends - `c >= 'a' && c <= 'z'` - or use the "
               "library's toupper.",
        hint="Give it characters that are not letters but sit near them: "
             "shout(\"{x}\").",
        checks=((("hi {name}",), "HI {NAME}"), (("hello",), "HELLO"), (("a~b",), "A~B"),
                (("room 101",), "ROOM 101"), (("",), "")),
    ),
    Hunt(
        id="hunt-c-unsigned-gap",
        title="A short post is 5 characters under",
        family=C,
        language="c",
        level=4,
        report="chars_over(text, limit) says how many characters a post is over "
               "its limit, 0 when it fits. A 5-character post with a limit of "
               "10 should be 0 and it says -5. Posts that are over the limit "
               "are right.",
        name="chars_over",
        params=("text", "limit"),
        types=("string", "int"),
        returns="int",
        start=(
            "// How many characters is the text over the limit? 0 if it fits.\n"
            "static size_t length_of(const char *text) {\n"
            "    return strlen(text);\n"
            "}\n"
            "\n"
            "int chars_over(const char *text, int limit) {\n"
            "    size_t len = length_of(text);\n"
            "    size_t cap = (size_t)limit;\n"
            "    if (len - cap > 0) {\n"
            "        return (int)len - limit;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
        fixed=(
            "// How many characters is the text over the limit? 0 if it fits.\n"
            "static size_t length_of(const char *text) {\n"
            "    return strlen(text);\n"
            "}\n"
            "\n"
            "int chars_over(const char *text, int limit) {\n"
            "    size_t len = length_of(text);\n"
            "    size_t cap = (size_t)limit;\n"
            "    if (len > cap) {\n"
            "        return (int)len - limit;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
        solve=_chars_over,
        reported=("hello", 10),
        cases=(("hello", 10), ("", 5), ("abc", 3), ("hello world!!", 10),
               ("abcdefghijkl", 5), ("abc", 0)),
        cause="size_t is unsigned, so `len - cap` never goes below zero: when "
              "len is smaller it wraps around to a huge positive number, "
              "which is > 0. Only an exact tie gives 0, so every short text "
              "takes the 'over the limit' branch.",
        decoys=(
            "strlen counts the terminating '\\0', so len is one too big.",
            "(int)len - limit should be limit - (int)len.",
            "The cast (size_t)limit turns a positive limit negative.",
        ),
        lesson="Unsigned arithmetic wraps instead of going negative, so "
               "`a - b > 0` is true for every a < b. Compare the two numbers "
               "directly - `a > b` - and only subtract once you know which "
               "is larger.",
        hint="Give it a short text and a long limit: chars_over(\"hello\", 10).",
        checks=((("hello", 10), 0), (("hello world!!", 10), 3), (("abc", 3), 0),
                (("", 5), 0), (("abcdefghijkl", 5), 7)),
    ),
    Hunt(
        id="hunt-c-switch-fallthrough",
        title="A touchdown is worth 9",
        family=C,
        language="c",
        level=4,
        report="score() totals a string of plays: T is a touchdown (6), F a "
               "field goal (3), S a safety (2). 'FTS' should be 11 and it says "
               "14. Strings with no touchdown add up correctly.",
        name="score",
        params=("plays",),
        types=("string",),
        returns="int",
        start=(
            "// T = touchdown (6), F = field goal (3), S = safety (2).\n"
            "int score(const char *plays) {\n"
            "    int total = 0;\n"
            "    for (int i = 0; plays[i] != '\\0'; i++) {\n"
            "        switch (plays[i]) {\n"
            "            case 'T': total += 6;\n"
            "            case 'F': total += 3; break;\n"
            "            case 'S': total += 2; break;\n"
            "            default: break;\n"
            "        }\n"
            "    }\n"
            "    return total;\n"
            "}\n"
        ),
        fixed=(
            "// T = touchdown (6), F = field goal (3), S = safety (2).\n"
            "int score(const char *plays) {\n"
            "    int total = 0;\n"
            "    for (int i = 0; plays[i] != '\\0'; i++) {\n"
            "        switch (plays[i]) {\n"
            "            case 'T': total += 6; break;\n"
            "            case 'F': total += 3; break;\n"
            "            case 'S': total += 2; break;\n"
            "            default: break;\n"
            "        }\n"
            "    }\n"
            "    return total;\n"
            "}\n"
        ),
        solve=_score,
        reported=("FTS",),
        cases=(("",), ("F",), ("S",), ("FSF",), ("xyz",), ("T",), ("TT",), ("FTS",)),
        cause="The 'T' case has no break, so C keeps running into the next "
              "case's code. A touchdown adds 6 and then the field goal's 3 as "
              "well - 9 in all.",
        decoys=(
            "The switch compares plays[i] to the wrong character, so 'T' "
            "matches 'F'.",
            "default: break; makes the loop stop at the first unknown play.",
            "total += 6 should be total = 6, so earlier plays are kept.",
        ),
        lesson="A `switch` case does not end at the next `case` label: "
               "execution falls through into it until a `break` (or return) "
               "stops it. Every case needs its own `break` unless the "
               "fall-through is deliberate - and then it deserves a comment.",
        hint="Score a string with a touchdown in it: score(\"T\").",
        checks=((("FTS",), 11), (("T",), 6), (("TT",), 12), (("FSF",), 8), (("",), 0),
                (("xyz",), 0)),
    ),
)
