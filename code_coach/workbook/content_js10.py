"""Pages 168-177: regular expressions from zero, in JavaScript.

The JavaScript book already had regex on pages 107 and 138 - named groups,
matchAll - and a learner who says they do not understand regex at all
arrives there with nothing to stand on. These ten pages are the ladder: one
symbol per page, twenty goes at it, easiest first.

They are numbered after the rest of the JavaScript book because the numbers
are append-only, so no page here says "as on the page before". Each one
explains its symbol from scratch and shows input, pattern and output.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JS_ONLY = ("javascript",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=JS_ONLY,
        tier="intermediate",
    )


def _quoted(words) -> str:
    q = [f'"{w}"' for w in words]
    if len(q) == 2:
        return f"{q[0]} and {q[1]}"
    return ", ".join(q[:-1]) + f" and {q[-1]}"


def _word_rows(rows):
    return tuple(
        (f"With the pattern /{p}/, print whether it is found in "
         f"{_quoted(words)}, one true or false per line.",
         {"pattern": p, "words": list(words)})
        for p, words in rows
    )


# ── 168. A pattern is a search ───────────────────────────────

_LITERALS = (
    ("cat", ("concat", "dog", "catalog")),
    ("sun", ("sunday", "moon", "unsung")),
    ("ear", ("heart", "eye", "bear")),
    ("top", ("stop", "pot", "laptop")),
    ("ring", ("string", "rang", "bring")),
    ("and", ("sandy", "hand", "end")),
    ("pie", ("pier", "pipe", "magpie")),
    ("low", ("yellow", "owl", "flower")),
    ("old", ("gold", "odd", "bold")),
    ("act", ("fact", "cat", "action")),
    ("red", ("bored", "read", "tired")),
    ("one", ("phone", "eon", "money")),
    ("ice", ("price", "ace", "nice")),
    ("art", ("party", "rat", "start")),
    ("own", ("brown", "won", "town")),
    ("eat", ("wheat", "tea", "great")),
    ("ink", ("think", "kin", "pink")),
    ("age", ("page", "gag", "stage")),
    ("all", ("small", "ale", "hallway")),
    ("net", ("planet", "ten", "network")),
)

LITERAL_PAGE = _page(
    "js-rx-literal", 168, "Regex from zero: a pattern is a search",
    "A regular expression (regex) is a pattern written between two slashes, "
    "like /cat/. It is not a string - it is a search. pattern.test(text) "
    "asks one question: can these letters, in this order, be found "
    "anywhere inside the text? It answers true or false. Plain letters "
    "mean exactly themselves, so /cat/ is found in \"concat\" (the last "
    "three letters) but not in \"act\", because the order matters.",
    "const pattern = /cat/;\n"
    "console.log(pattern.test(\"concat\"));  // true - c,a,t sits inside it\n"
    "console.log(pattern.test(\"dog\"));     // false - no c,a,t anywhere",
    "rx_literal",
    _word_rows(_LITERALS),
)


# ── 169. Case matters, and the i flag ────────────────────────

_CASES = (
    ("world", "Hello World"), ("cat", "My Cat Tom"), ("java", "I like JavaScript"),
    ("red", "RED ALERT"), ("dog", "hot dog stand"), ("apple", "Apple pie"),
    ("node", "Node and npm"), ("rain", "Rain, rain"), ("moon", "full MOON"),
    ("code", "Code Coach"), ("tea", "Green Tea"), ("sky", "blue sky"),
    ("fox", "Quick Brown Fox"), ("paris", "Trip to Paris"), ("ok", "OK then"),
    ("bus", "School Bus"), ("key", "KEYBOARD"), ("sea", "by the sea"),
    ("jazz", "Jazz Night"), ("star", "Rock STAR star"),
)

CASE_PAGE = _page(
    "js-rx-case", 169, "Regex from zero: capital letters matter, and the i flag",
    "A regex compares letters exactly, and to a computer \"W\" and \"w\" "
    "are different letters - so /world/ is NOT found in \"Hello World\". "
    "A letter written after the closing slash is a flag: it changes how "
    "the whole search behaves. The i flag means \"ignore case\": /world/i "
    "treats capital and small letters as the same, so now it is found. "
    "When the case already matches, both versions say true.",
    "const text = \"Hello World\";\n"
    "console.log(/world/.test(text));   // false - W is not w\n"
    "console.log(/world/i.test(text));  // true - i ignores case",
    "rx_case",
    tuple(
        (f"For the text \"{t}\", print whether /{p}/ is found, then whether "
         f"it is found when case is ignored.",
         {"pattern": p, "text": t})
        for p, t in _CASES
    ),
)


# ── 170. \d means a digit ────────────────────────────────────

_DIGITS = (
    "room 7", "flat 12", "no digits", "abc", "year 2026", "a1b2", "R2D2",
    "call 99", "one two", "x9", "5 apples", "page 100", "v8 engine",
    "e 3 4", "top10", "level", "7up", "b52", "hello", "area 51",
)

DIGIT_PAGE = _page(
    "js-rx-digit", 170, "Regex from zero: \\d means one digit",
    "Some patterns stand for a kind of character rather than one exact "
    "letter. \\d (a backslash then d) means \"any one digit\" - 0, 1, 2 up "
    "to 9. So /\\d/ is found in any text with at least one digit in it. "
    "Put two side by side and each needs its own digit, right next to the "
    "other: /\\d\\d/ asks for two digits in a row, so \"a1b2\" passes /\\d/ "
    "but fails /\\d\\d/ - its digits are not touching.",
    "const text = \"room 7\";\n"
    "console.log(/\\d/.test(text));    // true - 7 is a digit\n"
    "console.log(/\\d\\d/.test(text));  // false - no two digits together",
    "rx_digit",
    tuple(
        (f"For the text \"{t}\", print whether it has a digit, then whether "
         f"it has two digits in a row.",
         {"text": t})
        for t in _DIGITS
    ),
)


# ── 171. Sets, ranges, and not-these ─────────────────────────

_SETS = (
    ("[aeiou]", ("sky", "tree")), ("[xyz]", ("box", "cat")),
    ("[0-9]", ("abc", "a1")), ("[a-z]", ("ABC", "AbC")),
    ("[A-Z]", ("hello", "Hello")), ("[^0-9]", ("123", "12a")),
    ("[^a-z]", ("hello", "hello!")), ("[aeiou]", ("rhythm", "cloud")),
    ("[qz]", ("quiz", "hello")), ("[0-5]", ("789", "7a3")),
    ("[a-c]", ("dog", "cab")), ("[^aeiou]", ("aeiou", "aeiox")),
    ("[A-Z]", ("mcdonald", "McDonald")), ("[0-9]", ("route 66", "route")),
    ("[!?]", ("hi", "hi!")), ("[x-z]", ("zoo", "abc")),
    ("[^A-Z]", ("ABC", "ABc")), ("[aeiou]", ("gym", "gem")),
    ("[m-p]", ("cat", "map")), ("[^0-9]", ("2026", "20x6")),
)

SET_PAGE = _page(
    "js-rx-set", 171, "Regex from zero: [sets], [a-z] ranges, and [^not these]",
    "Square brackets hold a choice for ONE character. [aeiou] means \"one "
    "character that is a, e, i, o or u\". A dash inside makes a range, "
    "so [a-z] is any small letter, [A-Z] any capital and [0-9] any digit. "
    "A ^ straight after the opening bracket flips it to \"one character "
    "that is NOT any of these\": [^0-9] is found as soon as the text has a "
    "single non-digit. However long the list, a set is still only one "
    "character.",
    "const pattern = /[aeiou]/;\n"
    "console.log(pattern.test(\"sky\"));   // false - no vowel in it\n"
    "console.log(pattern.test(\"tree\"));  // true - e is in the set\n"
    "/[^0-9]/.test(\"123\") is false (all digits); "
    "/[^0-9]/.test(\"12a\") is true (a is not a digit)",
    "rx_set",
    _word_rows(_SETS),
)


# ── 172. + * ? ───────────────────────────────────────────────

_REPEATS = (
    ("go+al", ("goal", "gooooal", "gal")),
    ("colou?r", ("color", "colour", "colouur")),
    ("ab*c", ("ac", "abbbc", "adc")),
    ("ha+!", ("ha!", "haaaa!", "h!")),
    ("files?", ("file", "files", "fil")),
    ("\\d+ kg", ("5 kg", "250 kg", "kg")),
    ("bo*m", ("bm", "boooom", "bam")),
    ("x+y", ("xxy", "y", "xy")),
    ("hi+", ("hiiii", "hello", "hi")),
    ("cars?", ("car", "cars", "bus")),
    ("0+1", ("0001", "1", "01")),
    ("mo*n", ("mn", "moon", "man")),
    ("ye+s", ("yes", "yeees", "ys")),
    ("a\\d?b", ("ab", "a5b", "a55b")),
    ("z+", ("zzz", "buzz", "bee")),
    ("ok+", ("okkk", "ok", "oo")),
    ("bee*p", ("bep", "beeeep", "bp")),
    ("hel+o", ("helo", "hellllo", "heo")),
    ("sm?ile", ("sile", "smile", "mile")),
    ("ba*d", ("bd", "baaad", "bed")),
)

REPEAT_PAGE = _page(
    "js-rx-repeat", 172, "Regex from zero: + one or more, * zero or more, ? maybe",
    "These three symbols say how many times the thing just before them "
    "may appear. + means one or more: /go+al/ needs at least one o, so "
    "\"goal\" and \"gooooal\" pass and \"gal\" does not. * means zero or "
    "more: /ab*c/ allows no b at all, so \"ac\" passes. ? means maybe - "
    "zero or one: /colou?r/ matches both \"color\" and \"colour\". They "
    "only ever apply to the ONE character (or \\d, or [set]) right before "
    "them.",
    "const pattern = /go+al/;\n"
    "console.log(pattern.test(\"goal\"));     // true - one o\n"
    "console.log(pattern.test(\"gooooal\"));  // true - four o's\n"
    "console.log(pattern.test(\"gal\"));      // false - + needs at least one",
    "rx_repeat",
    _word_rows(_REPEATS),
)


# ── 173. {3} and {2,4} ───────────────────────────────────────

_COUNTS = (
    ("ab{2}c", ("abc", "abbc", "abbbc")),
    ("ho{2,3}t", ("hot", "hoot", "hoooot")),
    ("x{3}", ("xx", "xxx", "axxxb")),
    ("\\d{4}", ("year 2026", "year 26", "pin 0000")),
    ("a{2,4}h", ("ah", "aah", "aaaah")),
    ("\\d{2}:\\d{2}", ("12:30", "9:15", "07:05")),
    ("z{2}", ("pizza", "zoo", "buzz")),
    ("e{2}", ("tree", "ten", "bee")),
    ("q\\d{1,2}r", ("q5r", "q55r", "q555r")),
    ("o{3}", ("goooal", "good", "boo")),
    ("[a-z]{5}", ("tiny", "hello", "abc12")),
    ("\\d{3}-\\d{4}", ("555-1234", "55-1234", "555 1234")),
    ("#\\d{2,3}#", ("#7#", "#42#", "#123#")),
    ("l{2}", ("hello", "help", "ball")),
    ("[A-Z]{3}", ("USA", "Usa", "NASA rocks")),
    ("0{3}", ("1000", "100", "5000")),
    ("s{2}", ("glass", "gas", "miss")),
    ("\\d{1,2}%", ("5%", "50%", "%")),
    ("p{2}", ("apple", "ape", "happy")),
    ("r{2}y", ("berry", "very", "sorry")),
)

COUNT_PAGE = _page(
    "js-rx-count", 173, "Regex from zero: {3} exactly three, {2,4} between",
    "Curly braces give an exact count for the thing just before them. "
    "\\d{4} means four digits in a row - the same as writing \\d\\d\\d\\d. "
    "{2,4} means at least two and at most four, so /ho{2,3}t/ matches "
    "\"hoot\" and \"hooot\" but not \"hot\" (too few) or \"hoooot\" (too "
    "many, because the t has to come straight after). Remember test() "
    "searches anywhere inside the text; a later page shows how to say "
    "\"and nothing else\".",
    "const pattern = /ab{2}c/;\n"
    "console.log(pattern.test(\"abc\"));    // false - only one b\n"
    "console.log(pattern.test(\"abbc\"));   // true - exactly two b's\n"
    "console.log(pattern.test(\"abbbc\"));  // false - three is not two",
    "rx_count",
    _word_rows(_COUNTS),
)


# ── 174. ^ and $ ─────────────────────────────────────────────

_ANCHORS = (
    ("^\\d{4}$", ("1234", "12345", "12a4")),
    ("^[A-Z]{2}\\d{2}$", ("AB12", "ab12", "ABC12")),
    ("^[a-z]+$", ("hello", "Hello", "hi there")),
    ("^\\d{3}-\\d{4}$", ("555-1234", "5555-1234", "555-12345")),
    ("^[A-Z][a-z]+$", ("Alice", "alice", "ALICE")),
    ("^hello", ("hello world", "say hello", "hello")),
    ("world$", ("hello world", "world peace", "world")),
    ("^\\d+$", ("42", "4 2", "42a")),
    ("^[a-z]{3}\\d$", ("abc1", "abcd1", "ab1")),
    ("^#[0-9a-f]{6}$", ("#ff8800", "ff8800", "#ff880")),
    ("^\\d{2}:\\d{2}$", ("09:30", "9:30", "09:30pm")),
    ("^[A-Z]\\d[A-Z] \\d[A-Z]\\d$", ("K1A 0B1", "K1A0B1", "k1a 0b1")),
    ("^\\d{5}$", ("90210", "9021", "902100")),
    ("^[A-Z]{3}$", ("USD", "usd", "USDT")),
    ("\\d$", ("room 5", "5 rooms", "A4")),
    ("^[0-9]{3,4}$", ("123", "1234", "12")),
    ("^[a-z]+\\d*$", ("user", "user42", "42user")),
    ("^go", ("gopher", "ago", "go")),
    ("ing$", ("running", "ingot", "sing")),
    ("^[aeiou]", ("apple", "banana", "orange")),
)

ANCHOR_PAGE = _page(
    "js-rx-anchor", 174, "Regex from zero: ^ the start and $ the end",
    "On its own a pattern is found anywhere, so /\\d{4}/ happily finds four "
    "digits inside \"12345\". ^ at the front of a pattern means \"the text "
    "starts here\", and $ at the back means \"the text ends here\". Use "
    "both and the pattern must be the WHOLE text, with nothing before or "
    "after it: /^\\d{4}$/ is a 4-digit PIN check. ^ alone checks how a "
    "text starts; $ alone checks how it ends. (Inside [brackets] ^ means "
    "\"not\" - outside them it means \"start\".)",
    "const pattern = /^\\d{4}$/;\n"
    "console.log(pattern.test(\"1234\"));   // true - four digits, nothing else\n"
    "console.log(pattern.test(\"12345\"));  // false - a fifth digit\n"
    "console.log(pattern.test(\"12a4\"));   // false - a is not a digit",
    "rx_anchor",
    _word_rows(_ANCHORS),
)


# ── 175. . and \. ────────────────────────────────────────────

_DOTS = (
    ("a", "c", "abc"), ("a", "c", "a.c"), ("3", "5", "3.5"), ("3", "5", "3x5"),
    ("file", "txt", "file.txt"), ("file", "txt", "filetxt"),
    ("b", "t", "bat"), ("b", "t", "b.t"), ("x", "y", "xy"),
    ("1", "0", "1.0"), ("1", "0", "100"),
    ("index", "html", "index.html"), ("index", "html", "index-html"),
    ("e", "g", "e.g."), ("e", "g", "egg"),
    ("mr", "smith", "mr.smith"), ("mr", "smith", "mr smith"),
    ("v2", "1", "v2.1"), ("v2", "1", "v201"), ("dot", "com", "dot.com"),
)

DOT_PAGE = _page(
    "js-rx-dot", 175, "Regex from zero: . any character, \\. a real dot",
    "In a regex a dot does not mean a dot. . means \"any one character at "
    "all\" - a letter, a digit, a space, even a real dot. So /a.c/ matches "
    "\"abc\", \"a-c\" and \"a.c\", but not \"ac\", because the dot still "
    "needs exactly one character to stand on. To mean an actual full stop, "
    "put a backslash in front: \\. only matches \".\". Backslash in front "
    "of a symbol always means \"this symbol, literally\".",
    "const text = \"abc\";\n"
    "console.log(/a.c/.test(text));   // true - b counts as any character\n"
    "console.log(/a\\.c/.test(text));  // false - there is no real dot",
    "rx_dot",
    tuple(
        (f"For the text \"{t}\", print whether /{l}.{r}/ is found, then "
         f"whether /{l}\\.{r}/ (a real dot) is found.",
         {"left": l, "right": r, "text": t})
        for l, r, t in _DOTS
    ),
)


# ── 176. replace, and /g ─────────────────────────────────────

_REPLACES = (
    ("a1b2c3", "\\d", ""), ("hello big world", " ", "-"),
    ("banana", "a", "o"), ("2026-09-26", "-", "/"),
    ("free food", "[aeiou]", "*"), ("Hello World", "[A-Z]", "_"),
    ("room 12 and 345", "\\d+", "N"), ("a  b   c", " +", " "),
    ("x1y22z333", "\\d+", ""), ("mississippi", "ss", "SS"),
    ("cool moon", "o+", "0"), ("red, green, blue", ", ", "|"),
    ("A-B-C", "-", ""), ("2+2=4", "\\d", "n"),
    ("tip top tap", "t[aio]p", "T"), ("CamelCaseName", "[A-Z]", "."),
    ("one two three", "[^ ]+", "w"), ("aaa bbb", "a", "b"),
    ("7 11 42 5", "\\d{2}", "##"), ("hi there you", " ", "_"),
)


def _describe_with(w: str) -> str:
    return f"\"{w}\"" if w else "nothing (an empty string)"


REPLACE_PAGE = _page(
    "js-rx-replace", 176, "Regex from zero: replace, and /g for every match",
    "text.replace(pattern, newText) finds the pattern and swaps it for "
    "newText, giving back a new string. Without a flag it stops after the "
    "FIRST match. The g flag (written after the closing slash, like i) "
    "means \"global\": keep going and replace every match in the text. "
    "Replacing with \"\" deletes: text.replace(/\\d/g, \"\") strips every "
    "digit, and text.replace(/ /g, \"-\") turns every space into a dash.",
    "const text = \"a1b2c3\";\n"
    "console.log(text.replace(/\\d/, \"#\"));   // a#b2c3 - first digit only\n"
    "console.log(text.replace(/\\d/g, \"#\"));  // a#b#c# - g: every digit",
    "rx_replace",
    tuple(
        (f"In \"{t}\", replace the first match of /{p}/ with "
         f"{_describe_with(w)} and print it, then replace every match and "
         f"print that.",
         {"text": t, "pattern": p, "with": w})
        for t, p, w in _REPLACES
    ),
)


# ── 177. match with /g ───────────────────────────────────────

_MATCHES = (
    ("3 cats, 12 dogs, 7 fish", "\\d+"), ("banana", "a"),
    ("the cat sat on the mat", "[a-z]at"), ("Alice and Bob met Carol", "[A-Z]"),
    ("2026-09-26", "\\d+"), ("hello world", "o"),
    ("see you soon", "[aeiou]+"), ("a1 b22 c333", "\\d+"),
    ("Mississippi", "ss"), ("call 555-1234 now", "\\d{3,4}"),
    ("cool pool fool", "[a-z]ool"), ("Big Red Box", "[A-Z][a-z]+"),
    ("ab12cd3", "[a-z]+"), ("NASA and ESA", "[A-Z]{3,4}"),
    ("#tag1 and #tag2", "#[a-z]+\\d"), ("zz top buzz", "z+"),
    ("1.5 and 2.75", "\\d\\.\\d+"), ("rain in spain", "ain"),
    ("hmm mmm hm", "m+"), ("I am 30, you are 25", "\\d\\d"),
)

MATCH_PAGE = _page(
    "js-rx-match", 177, "Regex from zero: match with /g, every match as an array",
    "test() only says yes or no. text.match(pattern) hands back what was "
    "actually found. With the g flag it collects EVERY match into an "
    "array, in the order they appear, so .length is how many there were - "
    "the easy way to count digits, words or vowels. Printed with "
    "console.log an array looks like [ '3', '12', '7' ]. One warning: if "
    "nothing matches, match gives null rather than an empty array.",
    "const text = \"3 cats, 12 dogs, 7 fish\";\n"
    "const found = text.match(/\\d+/g);\n"
    "console.log(found);         // [ '3', '12', '7' ]\n"
    "console.log(found.length);  // 3",
    "rx_match",
    tuple(
        (f"In \"{t}\", collect every match of /{p}/, print the list of "
         f"matches, then print how many there are.",
         {"text": t, "pattern": p})
        for t, p in _MATCHES
    ),
)


JS10_PAGES: tuple[Page, ...] = (
    LITERAL_PAGE,
    CASE_PAGE,
    DIGIT_PAGE,
    SET_PAGE,
    REPEAT_PAGE,
    COUNT_PAGE,
    ANCHOR_PAGE,
    DOT_PAGE,
    REPLACE_PAGE,
    MATCH_PAGE,
)
