"""Change it: C - working C, and a change request.

The same exercise and the same four rules as the Python, JavaScript and
Dart drills: the start passes every case under the old requirement
(`before`), it fails the new one (`solve`), some cases keep their answer
so a rewrite that breaks what worked fails, and the answer (`after`) is
a few lines from the start.

The changes lean on the C worth knowing: a condition joined with &&, a
sentinel for "there was nothing", a new branch in an if-else ladder that
has to go in the right place, tolower and the unsigned char cast it
needs, a filter that writes into `out`, and a counter whose last word is
counted after the loop - so a change to the rule has to be made twice.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Change it: C"


def _deposit_total_before(amounts: list) -> int:
    return sum(amounts)


def _deposit_total(amounts: list) -> int:
    return sum(a for a in amounts if a > 0)


def _highest_score_before(scores: list) -> int:
    return max(scores) if scores else 0


def _highest_score(scores: list) -> int:
    return max(scores) if scores else -1


def _letter_grade_before(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    return "F"


def _letter_grade(score: int) -> str:
    if score >= 60 and score < 70:
        return "D"
    return _letter_grade_before(score)


def _count_letter_before(text: str, letter: str) -> int:
    return text.count(letter)


def _count_letter(text: str, letter: str) -> int:
    return text.lower().count(letter.lower())


def _valid_readings_before(readings: list) -> list:
    return [r for r in readings if r != -1]


def _valid_readings(readings: list) -> list:
    return [r for r in readings if r != -1 and r != 0]


def _title_word_count_before(text: str) -> int:
    return len(text.split())


def _title_word_count(text: str) -> int:
    return sum(1 for w in text.split() if len(w) >= 3)


C_MODIFY: tuple[Kata, ...] = (
    Kata(
        id="c-change-deposit-total",
        name="depositTotal",
        family=FAMILY,
        language="c",
        level=1,
        params=("amounts",),
        types=("int[]",),
        returns="int",
        was="It adds up every amount on the statement: depositTotal({10, -5, 20}, 3) is 25.",
        brief=(
            "The screen is headed 'Money in', and withdrawals - the negative "
            "amounts - are being subtracted from it. Add up only the "
            "deposits, the amounts above 0."
        ),
        example="depositTotal({10, -5, 20}, 3) → 30   depositTotal({-3}, 1) → 0",
        hint="The loop sees every amount already. Which ones should reach total?",
        change=(
            "An if around the += lets only the positive amounts through: "
            "if (amounts[i] > 0). Everything else - the loop, the starting "
            "0, the return - stays, which is the point of a small change. "
            "A statement with no withdrawals gives the same total as before."
        ),
        cases=(([10, 20],), ([10, -5, 20],), ([],), ([-3],), ([0, 5],),
               ([-1, -2, -3],), ([100],), ([7, -7, 7],)),
        before=_deposit_total_before,
        solve=_deposit_total,
        start=(
            "int depositTotal(const int *amounts, int amounts_len) {\n"
            "  int total = 0;\n"
            "  for (int i = 0; i < amounts_len; i++) {\n"
            "    total += amounts[i];\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        after=(
            "int depositTotal(const int *amounts, int amounts_len) {\n"
            "  int total = 0;\n"
            "  for (int i = 0; i < amounts_len; i++) {\n"
            "    if (amounts[i] > 0) {\n"
            "      total += amounts[i];\n"
            "    }\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        checks=((([10, -5, 20],), 30), (([],), 0), (([-3],), 0), (([7, -7, 7],), 14)),
    ),
    Kata(
        id="c-change-highest-score",
        name="highestScore",
        family=FAMILY,
        language="c",
        level=1,
        params=("scores",),
        types=("int[]",),
        returns="int",
        was=(
            "It returns the highest score in the list, and 0 when the list "
            "is empty: highestScore({40, 90}, 2) is 90."
        ),
        brief=(
            "A player who scored 0 and a game nobody played both show 0 on "
            "the board. Scores are never negative, so return -1 for an "
            "empty list, and the screen will say 'no games yet'."
        ),
        example="highestScore({}, 0) → -1   highestScore({0}, 1) → 0   "
                "highestScore({40, 90}, 2) → 90",
        hint="Only one line knows about the empty list.",
        change=(
            "The early return for the empty list is the only place the "
            "answer for 'nothing' is decided, so the change is that one "
            "number. -1 works as 'nothing' only because a real score can "
            "never be negative - a sentinel has to be a value the real "
            "answers cannot take."
        ),
        cases=(([40, 90],), ([],), ([0],), ([55],), ([3, 3],), ([0, 0, 0],),
               ([12, 99, 45],), ([100, 1],)),
        before=_highest_score_before,
        solve=_highest_score,
        start=(
            "int highestScore(const int *scores, int scores_len) {\n"
            "  if (scores_len == 0) {\n"
            "    return 0;\n"
            "  }\n"
            "  int best = scores[0];\n"
            "  for (int i = 1; i < scores_len; i++) {\n"
            "    if (scores[i] > best) {\n"
            "      best = scores[i];\n"
            "    }\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        after=(
            "int highestScore(const int *scores, int scores_len) {\n"
            "  if (scores_len == 0) {\n"
            "    return -1;\n"
            "  }\n"
            "  int best = scores[0];\n"
            "  for (int i = 1; i < scores_len; i++) {\n"
            "    if (scores[i] > best) {\n"
            "      best = scores[i];\n"
            "    }\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        checks=((([],), -1), (([0],), 0), (([40, 90],), 90), (([0, 0, 0],), 0)),
    ),
    Kata(
        id="c-change-letter-grade",
        name="letterGrade",
        family=FAMILY,
        language="c",
        level=2,
        params=("score",),
        types=("int",),
        returns="string",
        was=(
            "It turns a score out of 100 into a grade: 90 and up is \"A\", "
            "80 and up \"B\", 70 and up \"C\", and anything lower \"F\"."
        ),
        brief=(
            "The school has added a D: a score from 60 to 69 is now \"D\". "
            "Every other score keeps its grade."
        ),
        example='letterGrade(65) → "D"   letterGrade(59) → "F"   letterGrade(72) → "C"',
        hint="The ladder is checked top to bottom. Where does a new rung for 60 have to go?",
        change=(
            "One more rung, if (score >= 60) return \"D\";, placed after "
            "the 70 check and before the fall-through to \"F\". Because "
            "each rung returns, reaching it already means the score is "
            "below 70, so it needs no upper bound - and put anywhere "
            "higher, it would catch the Bs and Cs too."
        ),
        cases=((95,), (90,), (85,), (72,), (70,), (69,), (65,), (60,), (59,), (0,), (100,)),
        before=_letter_grade_before,
        solve=_letter_grade,
        start=(
            "const char *letterGrade(int score) {\n"
            "  if (score >= 90) {\n"
            "    return \"A\";\n"
            "  }\n"
            "  if (score >= 80) {\n"
            "    return \"B\";\n"
            "  }\n"
            "  if (score >= 70) {\n"
            "    return \"C\";\n"
            "  }\n"
            "  return \"F\";\n"
            "}\n"
        ),
        after=(
            "const char *letterGrade(int score) {\n"
            "  if (score >= 90) {\n"
            "    return \"A\";\n"
            "  }\n"
            "  if (score >= 80) {\n"
            "    return \"B\";\n"
            "  }\n"
            "  if (score >= 70) {\n"
            "    return \"C\";\n"
            "  }\n"
            "  if (score >= 60) {\n"
            "    return \"D\";\n"
            "  }\n"
            "  return \"F\";\n"
            "}\n"
        ),
        checks=(((65,), "D"), ((60,), "D"), ((69,), "D"), ((59,), "F"),
                ((0,), "F"), ((70,), "C"), ((100,), "A")),
    ),
    Kata(
        id="c-change-count-letter",
        name="countLetter",
        family=FAMILY,
        language="c",
        level=2,
        params=("text", "letter"),
        types=("string", "char"),
        returns="int",
        was=(
            "It counts how many times letter appears in text, exactly as "
            "typed: countLetter(\"Anna\", 'a') is 1."
        ),
        brief=(
            "Search results say \"Anna\" has one a. Make the count ignore "
            "case, so 'a' and 'A' both count, whichever one letter is."
        ),
        example="countLetter(\"Anna\", 'a') → 2   countLetter(\"Aa\", 'A') → 2   "
                "countLetter(\"Banana\", 'a') → 3",
        hint="<ctype.h> has a function that turns 'A' into 'a' and leaves 'a' alone.",
        change=(
            "Compare both sides lowered: tolower(text[i]) == tolower(letter), "
            "with #include <ctype.h> at the top. The (unsigned char) casts "
            "are not decoration - tolower is only defined for values an "
            "unsigned char can hold, and a plain char can be negative. "
            "Lowering both sides means the caller can pass either case."
        ),
        cases=(("Banana", "a"), ("Anna", "a"), ("", "a"), ("xyz", "a"), ("AAA", "a"),
               ("Mississippi", "s"), ("Aa", "A"), ("b", "B")),
        before=_count_letter_before,
        solve=_count_letter,
        start=(
            "int countLetter(const char *text, char letter) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; text[i] != '\\0'; i++) {\n"
            "    if (text[i] == letter) {\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        after=(
            "#include <ctype.h>\n"
            "\n"
            "int countLetter(const char *text, char letter) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; text[i] != '\\0'; i++) {\n"
            "    if (tolower((unsigned char)text[i]) == tolower((unsigned char)letter)) {\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        checks=((("Anna", "a"), 2), (("", "a"), 0), (("AAA", "a"), 3),
                (("Aa", "A"), 2), (("Mississippi", "s"), 4)),
    ),
    Kata(
        id="c-change-valid-readings",
        name="validReadings",
        family=FAMILY,
        language="c",
        level=3,
        params=("readings",),
        types=("int[]",),
        returns="int[]",
        was=(
            "The thermometer sends -1 when it could not take a reading. "
            "validReadings copies every other reading into out, in order, "
            "and returns how many it wrote."
        ),
        brief=(
            "It turns out the sensor also sends 0 for a moment after it "
            "resets, and the chart dips to the floor every morning. Leave "
            "out the 0s as well as the -1s. Other negatives are real "
            "winter readings and stay."
        ),
        example="validReadings({7, 0, -1, 0, 2}, 5, out) writes {7, 2} and returns 2",
        hint="The if already decides what gets copied. What else has to be true of a reading to be kept?",
        change=(
            "The test that lets a reading into out gets a second condition "
            "joined with &&: readings[i] != -1 && readings[i] != 0. count "
            "still only moves when something is written, so out stays "
            "packed from index 0 and the return is still how many it "
            "wrote. -5 stays: only the two values the sensor uses as "
            "signals are dropped."
        ),
        cases=(([3, -1, 5],), ([0, 4],), ([],), ([-1],), ([0],), ([7, 0, -1, 0, 2],),
               ([-5, 6],), ([-1, -1, 9],)),
        before=_valid_readings_before,
        solve=_valid_readings,
        start=(
            "int validReadings(const int *readings, int readings_len, int *out) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; i < readings_len; i++) {\n"
            "    if (readings[i] != -1) {\n"
            "      out[count] = readings[i];\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        after=(
            "int validReadings(const int *readings, int readings_len, int *out) {\n"
            "  int count = 0;\n"
            "  for (int i = 0; i < readings_len; i++) {\n"
            "    if (readings[i] != -1 && readings[i] != 0) {\n"
            "      out[count] = readings[i];\n"
            "      count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        checks=((([7, 0, -1, 0, 2],), [7, 2]), (([],), []), (([0],), []),
                (([-5, 6],), [-5, 6]), (([3, -1, 5],), [3, 5])),
    ),
    Kata(
        id="c-change-title-word-count",
        name="titleWordCount",
        family=FAMILY,
        language="c",
        level=4,
        params=("text",),
        types=("string",),
        returns="int",
        was=(
            "It counts the words in a title, where words are separated by "
            "spaces: titleWordCount(\"a tale of two cities\") is 5."
        ),
        brief=(
            "Search ranks titles by how many real words they have, and "
            "'a', 'of' and 'to' are padding. Count only the words at least "
            "3 letters long."
        ),
        example='titleWordCount("a tale of two cities") → 3   titleWordCount("go") → 0',
        hint="There are two places a word can end. Read both.",
        change=(
            "A word is counted when it ends, and len already holds its "
            "length, so the rule becomes len >= 3 instead of len > 0. It "
            "has to change in both places: at a space inside the loop, and "
            "after the loop, where the last word ends with the string "
            "rather than a space. Change only the first and every title "
            "whose last word is short still counts it."
        ),
        cases=(("the cat sat",), ("a tale of two cities",), ("",), ("go",),
               ("  big  red  ",), ("I am here",), ("war and peace",), ("up to it",)),
        before=_title_word_count_before,
        solve=_title_word_count,
        start=(
            "int titleWordCount(const char *text) {\n"
            "  int count = 0;\n"
            "  int len = 0;\n"
            "  for (int i = 0; text[i] != '\\0'; i++) {\n"
            "    if (text[i] == ' ') {\n"
            "      if (len > 0) {\n"
            "        count++;\n"
            "      }\n"
            "      len = 0;\n"
            "    } else {\n"
            "      len++;\n"
            "    }\n"
            "  }\n"
            "  if (len > 0) {\n"
            "    count++;\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        after=(
            "int titleWordCount(const char *text) {\n"
            "  int count = 0;\n"
            "  int len = 0;\n"
            "  for (int i = 0; text[i] != '\\0'; i++) {\n"
            "    if (text[i] == ' ') {\n"
            "      if (len >= 3) {\n"
            "        count++;\n"
            "      }\n"
            "      len = 0;\n"
            "    } else {\n"
            "      len++;\n"
            "    }\n"
            "  }\n"
            "  if (len >= 3) {\n"
            "    count++;\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        checks=((("a tale of two cities",), 3), (("",), 0), (("go",), 0),
                (("  big  red  ",), 2), (("I am here",), 1), (("the cat sat",), 3)),
    ),
)
