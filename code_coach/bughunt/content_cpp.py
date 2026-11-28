"""C++ hunts: bugs the compiler lets through, all of them well-defined.

Every program here does exactly what it says on every compiler and every
build - an unsigned subtraction wraps, `operator[]` on a map inserts, a
`switch` falls through, a parameter taken by value is a copy. None of
them is undefined behaviour and none depends on the implementation, so
the broken program misbehaves the same way everywhere, and the fix is a
line or two.

Run through kata/cpp_harness.py, so each hunt gives one C++ type per
parameter (`string`, `vector<string>`, `vector<int>`, `int`...) and its
return type. The same rules hold as for every hunt, checked by
tests/test_bughunt.py.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

CPP = "C++"


def _index_of(text, word):
    return text.find(word)


def _grade_points(grades):
    return sum({"A": 4, "B": 3, "C": 2, "D": 1}.get(g, 0) for g in grades)


def _doubled_total(scores):
    return 2 * sum(scores)


def _repeat_count(words):
    return len(words) - len(set(words))


def _winner(rows):
    if not rows:
        return ""
    best = max(rows, key=lambda r: int(r.split(":")[1]))
    return best.split(":")[0]


def _equal_pairs(nums):
    if len(nums) < 2:
        return -1
    return sum(1 for i in range(1, len(nums)) if nums[i] == nums[i - 1])


CPP_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-cpp-find-npos",
        title="Words at the very start are never found",
        family=CPP,
        language="cpp",
        level=1,
        report="index_of(\"cat\", \"cat\") should be 0 and it says -1, so the "
               "search box claims a word is missing when the text starts with "
               "it. Words further in, like \"cat\" inside \"concatenate\", are "
               "found fine.",
        name="index_of",
        params=("text", "word"),
        types=("string", "string"),
        returns="int",
        start=(
            "// Where a word first appears in a text, or -1 if it does not.\n"
            "static bool present(std::size_t pos) {\n"
            "    return pos != std::string::npos && pos > 0;\n"
            "}\n"
            "\n"
            "int index_of(const std::string &text, const std::string &word) {\n"
            "    std::size_t pos = text.find(word);\n"
            "    if (!present(pos)) {\n"
            "        return -1;\n"
            "    }\n"
            "    return (int)pos;\n"
            "}\n"
        ),
        fixed=(
            "// Where a word first appears in a text, or -1 if it does not.\n"
            "static bool present(std::size_t pos) {\n"
            "    return pos != std::string::npos;\n"
            "}\n"
            "\n"
            "int index_of(const std::string &text, const std::string &word) {\n"
            "    std::size_t pos = text.find(word);\n"
            "    if (!present(pos)) {\n"
            "        return -1;\n"
            "    }\n"
            "    return (int)pos;\n"
            "}\n"
        ),
        solve=_index_of,
        reported=("cat", "cat"),
        cases=(("cat", "cat"), ("concatenate", "cat"), ("dog", "cat"), ("", "a"),
               ("catalog", "cat"), ("a cat", "cat")),
        cause="present() treats position 0 as 'not found': `pos > 0` is false "
              "for a match at the very start. A found position is anything "
              "except std::string::npos, and 0 is a perfectly good position.",
        decoys=(
            "std::string::find returns -1 when it fails, so comparing with "
            "npos is the wrong check.",
            "The cast (int)pos loses the position of long texts.",
            "find only looks for single characters, not whole words.",
        ),
        lesson="find reports 'not found' with one special value, "
               "std::string::npos, and nothing else. Compare against exactly "
               "that - never add `> 0` or `>= 1`, because 0 is the position of "
               "a match at the start.",
        hint="Try a word that is the whole text, or that the text starts with: "
             "index_of(\"cat\", \"cat\").",
        checks=((("cat", "cat"), 0), (("concatenate", "cat"), 3), (("dog", "cat"), -1),
                (("", "a"), -1), (("a cat", "cat"), 2)),
    ),
    Hunt(
        id="hunt-cpp-switch-break",
        title="A B counts as a C",
        family=CPP,
        language="cpp",
        level=2,
        report="grade_points(\"AB\") should be 7 (4 for the A, 3 for the B) and "
               "it gives 6. Every B seems to be worth 2, the same as a C. As, "
               "Cs and Ds are right.",
        name="grade_points",
        params=("grades",),
        types=("string",),
        returns="int",
        start=(
            "// Total grade points for a string of letter grades like \"ABD\".\n"
            "static int points(char grade) {\n"
            "    int p = 0;\n"
            "    switch (grade) {\n"
            "        case 'A': p = 4; break;\n"
            "        case 'B': p = 3;\n"
            "        case 'C': p = 2; break;\n"
            "        case 'D': p = 1; break;\n"
            "        default: p = 0; break;\n"
            "    }\n"
            "    return p;\n"
            "}\n"
            "\n"
            "int grade_points(const std::string &grades) {\n"
            "    int total = 0;\n"
            "    for (char g : grades) {\n"
            "        total += points(g);\n"
            "    }\n"
            "    return total;\n"
            "}\n"
        ),
        fixed=(
            "// Total grade points for a string of letter grades like \"ABD\".\n"
            "static int points(char grade) {\n"
            "    int p = 0;\n"
            "    switch (grade) {\n"
            "        case 'A': p = 4; break;\n"
            "        case 'B': p = 3; break;\n"
            "        case 'C': p = 2; break;\n"
            "        case 'D': p = 1; break;\n"
            "        default: p = 0; break;\n"
            "    }\n"
            "    return p;\n"
            "}\n"
            "\n"
            "int grade_points(const std::string &grades) {\n"
            "    int total = 0;\n"
            "    for (char g : grades) {\n"
            "        total += points(g);\n"
            "    }\n"
            "    return total;\n"
            "}\n"
        ),
        solve=_grade_points,
        reported=("AB",),
        cases=(("",), ("A",), ("AB",), ("CD",), ("BBB",), ("ACD",)),
        cause="The `case 'B'` has no break, so after setting p = 3 execution "
              "falls straight into the next case and sets p = 2. Every B ends "
              "up worth a C.",
        decoys=(
            "The switch compares the char with the wrong type, so 'B' never "
            "matches.",
            "total is an int, so the points are rounded down.",
            "The for loop skips the character after each B.",
        ),
        lesson="A C++ switch does not stop at the end of a case: it runs on "
               "into the next one until a break, return or the closing brace. "
               "End every case with break unless the fall-through is "
               "deliberate - and then say so in a comment.",
        hint="Score a single B: grade_points(\"B\"). Then compare it with \"C\".",
        checks=((("AB",), 7), (("",), 0), (("BBB",), 9), (("ACD",), 7), (("CD",), 3)),
    ),
    Hunt(
        id="hunt-cpp-vector-by-value",
        title="Doubling the scores changes nothing",
        family=CPP,
        language="cpp",
        level=2,
        report="doubled_total([1, 2, 3]) should be 12 and it gives 6, which is "
               "just the plain total - the doubling never happens. Empty lists "
               "and zeros come out right.",
        name="doubled_total",
        params=("scores",),
        types=("vector<int>",),
        returns="int",
        start=(
            "// Double every score, then add them up.\n"
            "static void double_all(std::vector<int> scores) {\n"
            "    for (std::size_t i = 0; i < scores.size(); i++) {\n"
            "        scores[i] *= 2;\n"
            "    }\n"
            "}\n"
            "\n"
            "int doubled_total(std::vector<int> scores) {\n"
            "    double_all(scores);\n"
            "    int sum = 0;\n"
            "    for (int s : scores) {\n"
            "        sum += s;\n"
            "    }\n"
            "    return sum;\n"
            "}\n"
        ),
        fixed=(
            "// Double every score, then add them up.\n"
            "static void double_all(std::vector<int> &scores) {\n"
            "    for (std::size_t i = 0; i < scores.size(); i++) {\n"
            "        scores[i] *= 2;\n"
            "    }\n"
            "}\n"
            "\n"
            "int doubled_total(std::vector<int> scores) {\n"
            "    double_all(scores);\n"
            "    int sum = 0;\n"
            "    for (int s : scores) {\n"
            "        sum += s;\n"
            "    }\n"
            "    return sum;\n"
            "}\n"
        ),
        solve=_doubled_total,
        reported=([1, 2, 3],),
        cases=(([],), ([0],), ([1, 2, 3],), ([5],), ([-4, 4],), ([2, 2],)),
        cause="double_all takes its vector by value, so it doubles a private "
              "copy that is thrown away when it returns. doubled_total's own "
              "vector is untouched.",
        decoys=(
            "The loop in double_all stops one element early, so the last score "
            "is never doubled.",
            "`scores[i] *= 2` multiplies the index instead of the value.",
            "sum starts at the wrong value, so every total is too small.",
        ),
        lesson="In C++ a parameter without & is a copy. A function that is "
               "meant to change what it was given must take it by reference "
               "(std::vector<int> &v); otherwise it edits a copy and the "
               "caller sees nothing.",
        hint="Call it on one score: doubled_total([5]) should be 10.",
        checks=((([1, 2, 3],), 12), (([],), 0), (([5],), 10), (([-4, 4],), 0)),
    ),
    Hunt(
        id="hunt-cpp-map-brackets",
        title="Every word is reported as a repeat",
        family=CPP,
        language="cpp",
        level=3,
        report="repeat_count([\"a\", \"b\"]) should be 0, since nothing repeats, "
               "and it says 2. A list of three different words says 3. Only the "
               "empty list is right.",
        name="repeat_count",
        params=("words",),
        types=("vector<string>",),
        returns="int",
        start=(
            "// How many words in the list already appeared earlier in it.\n"
            "int repeat_count(const std::vector<std::string> &words) {\n"
            "    std::map<std::string, int> seen;\n"
            "    int repeats = 0;\n"
            "    for (const std::string &w : words) {\n"
            "        int times = seen[w];\n"
            "        if (seen.count(w) > 0) {\n"
            "            repeats++;\n"
            "        }\n"
            "        seen[w] = times + 1;\n"
            "    }\n"
            "    return repeats;\n"
            "}\n"
        ),
        fixed=(
            "// How many words in the list already appeared earlier in it.\n"
            "int repeat_count(const std::vector<std::string> &words) {\n"
            "    std::map<std::string, int> seen;\n"
            "    int repeats = 0;\n"
            "    for (const std::string &w : words) {\n"
            "        int times = seen[w];\n"
            "        if (times > 0) {\n"
            "            repeats++;\n"
            "        }\n"
            "        seen[w] = times + 1;\n"
            "    }\n"
            "    return repeats;\n"
            "}\n"
        ),
        solve=_repeat_count,
        reported=(["a", "b"],),
        cases=(([],), (["a", "b"],), (["a", "a"],), (["x", "y", "x", "x"],), (["z"],)),
        cause="`seen[w]` on the line above INSERTS w with a value of 0 when it "
              "is missing, so by the time seen.count(w) runs every word is "
              "already in the map. The membership test is always true.",
        decoys=(
            "std::map::count returns the number of distinct keys, not "
            "whether this one exists.",
            "repeats is never reset, so it carries over between calls.",
            "The map is ordered, so words are compared in the wrong order.",
        ),
        lesson="operator[] on a std::map is not a read: a missing key is "
               "created on the spot. Check membership BEFORE you subscript "
               "(count, find or contains), or test the value you read - never "
               "ask 'is it in the map?' after indexing it.",
        hint="Try two different words: repeat_count([\"a\", \"b\"]). What does "
             "the map hold by the time each word is checked?",
        checks=(((["a", "b"],), 0), ((["a", "a"],), 1), ((["x", "y", "x", "x"],), 2),
                (([],), 0), ((["z"],), 0)),
    ),
    Hunt(
        id="hunt-cpp-sort-wrong-field",
        title="The winner is whoever is last in the alphabet",
        family=CPP,
        language="cpp",
        level=3,
        report="winner([\"ana:9\", \"bob:4\", \"cy:6\"]) should be \"ana\", who "
               "has the top score, and it says \"cy\". It looks as if it is "
               "going by names. A single entry, or an empty list, is fine.",
        name="winner",
        params=("rows",),
        types=("vector<string>",),
        returns="string",
        start=(
            "// The name with the highest score, from rows like \"ana:9\".\n"
            "struct Row {\n"
            "    std::string name;\n"
            "    int score;\n"
            "};\n"
            "\n"
            "static Row parse(const std::string &text) {\n"
            "    std::size_t colon = text.find(':');\n"
            "    return Row{text.substr(0, colon), std::stoi(text.substr(colon + 1))};\n"
            "}\n"
            "\n"
            "std::string winner(const std::vector<std::string> &rows) {\n"
            "    if (rows.empty()) {\n"
            "        return \"\";\n"
            "    }\n"
            "    std::vector<Row> all;\n"
            "    for (const std::string &r : rows) {\n"
            "        all.push_back(parse(r));\n"
            "    }\n"
            "    std::sort(all.begin(), all.end(), [](const Row &a, const Row &b) {\n"
            "        return a.name > b.name;\n"
            "    });\n"
            "    return all[0].name;\n"
            "}\n"
        ),
        fixed=(
            "// The name with the highest score, from rows like \"ana:9\".\n"
            "struct Row {\n"
            "    std::string name;\n"
            "    int score;\n"
            "};\n"
            "\n"
            "static Row parse(const std::string &text) {\n"
            "    std::size_t colon = text.find(':');\n"
            "    return Row{text.substr(0, colon), std::stoi(text.substr(colon + 1))};\n"
            "}\n"
            "\n"
            "std::string winner(const std::vector<std::string> &rows) {\n"
            "    if (rows.empty()) {\n"
            "        return \"\";\n"
            "    }\n"
            "    std::vector<Row> all;\n"
            "    for (const std::string &r : rows) {\n"
            "        all.push_back(parse(r));\n"
            "    }\n"
            "    std::sort(all.begin(), all.end(), [](const Row &a, const Row &b) {\n"
            "        return a.score > b.score;\n"
            "    });\n"
            "    return all[0].name;\n"
            "}\n"
        ),
        solve=_winner,
        reported=(["ana:9", "bob:4", "cy:6"],),
        cases=(([],), (["ana:9"],), (["ana:9", "bob:4", "cy:6"],), (["zed:1", "amy:8"],),
               (["bo:5", "al:2"],)),
        cause="The comparator sorts by name, not by score: `a.name > b.name` "
              "puts the alphabetically LAST name first. The sort itself and "
              "the parsing are fine; it is ordered by the wrong field.",
        decoys=(
            "std::sort puts the smallest element first, so it needs to be "
            "reversed with std::reverse.",
            "parse splits at the wrong colon, so the scores are read as names.",
            "all[0] is the last element after sorting, not the first.",
        ),
        lesson="A std::sort comparator decides everything about the order, "
               "and any comparator that compiles is accepted - even one that "
               "looks at the wrong field. Read the comparator aloud: 'a comes "
               "before b when a's ___ is greater than b's ___' and check the "
               "blank is the thing you meant.",
        hint="Give it two entries where the better score belongs to the name "
             "that comes first alphabetically, then the reverse.",
        checks=(((["ana:9", "bob:4", "cy:6"],), "ana"), ((["zed:1", "amy:8"],), "amy"),
                (([],), ""), ((["bo:5", "al:2"],), "bo")),
    ),
    Hunt(
        id="hunt-cpp-size-minus-one",
        title="An empty list is not 'too short'",
        family=CPP,
        language="cpp",
        level=4,
        report="equal_pairs is meant to return -1 when there are fewer than "
               "two readings to compare. A single reading does that, but an "
               "empty list gives 0 instead of -1.",
        name="equal_pairs",
        params=("nums",),
        types=("vector<int>",),
        returns="int",
        start=(
            "// How many neighbouring readings are equal; -1 if fewer than two.\n"
            "int equal_pairs(const std::vector<int> &nums) {\n"
            "    if (nums.size() - 1 < 1) {\n"
            "        return -1;\n"
            "    }\n"
            "    int count = 0;\n"
            "    for (std::size_t i = 1; i < nums.size(); i++) {\n"
            "        if (nums[i] == nums[i - 1]) {\n"
            "            count++;\n"
            "        }\n"
            "    }\n"
            "    return count;\n"
            "}\n"
        ),
        fixed=(
            "// How many neighbouring readings are equal; -1 if fewer than two.\n"
            "int equal_pairs(const std::vector<int> &nums) {\n"
            "    if (nums.size() < 2) {\n"
            "        return -1;\n"
            "    }\n"
            "    int count = 0;\n"
            "    for (std::size_t i = 1; i < nums.size(); i++) {\n"
            "        if (nums[i] == nums[i - 1]) {\n"
            "            count++;\n"
            "        }\n"
            "    }\n"
            "    return count;\n"
            "}\n"
        ),
        solve=_equal_pairs,
        reported=([],),
        cases=(([],), ([5],), ([1, 1],), ([1, 2, 2, 2],), ([1, 2, 3],)),
        cause="size() is unsigned. For an empty vector, `nums.size() - 1` does "
              "not give -1: it wraps around to the largest possible size_t, "
              "which is certainly not less than 1, so the early return is "
              "skipped and the empty loop reports 0.",
        decoys=(
            "The loop starts at i = 1, so the first pair is never compared.",
            "nums[i - 1] reads before the start of the vector when i is 1.",
            "-1 cannot be returned from a function that returns int.",
        ),
        lesson="size() is an unsigned number, and unsigned arithmetic wraps "
               "instead of going negative: 0 - 1 is a huge value. Never "
               "subtract from a size when it might be 0; rewrite the test so "
               "it only adds or compares (`size() < 2`, `i + 1 < size()`).",
        hint="Try the smallest inputs: [] and [5]. They should behave alike.",
        checks=((([],), -1), (([5],), -1), (([1, 1],), 1), (([1, 2, 2, 2],), 2),
                (([1, 2, 3],), 0)),
    ),
)
