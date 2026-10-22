"""Words the Brain Drills string packs teach: whitespace, case, strip, split, join, search, replace, format,
padding, characters and codes, palindromes, anagrams, comparing strings.

Written so every concept an activity lists in `Activity.concepts` resolves in both languages.
"""

from __future__ import annotations

from .entry import Entry, both

TERMS: list[Entry] = [
    *both(
        "whitespace",
        "Whitespace",
        "The characters you cannot see: spaces, tabs and line breaks. They take up room in a string even though nothing is drawn.",
        see=("strip", "split", "string"),
        priority=30,
        aka=("blank", "spaces", "space", "tab", "newline", "line break"),
        python=dict(
            rules=(
                "A space, a tab ('\\t') and a line break ('\\n') are all whitespace, and each counts as one character.",
                "strip() removes whitespace from the two ends only, never from the middle.",
                "split() with no argument splits on any run of whitespace and throws the empty pieces away.",
            ),
            example="""
                s = "  a b\\t"
                print(len(s), len(s.strip()), s.split())
            """,
            out="6 3 ['a', 'b']",
        ),
        javascript=dict(
            rules=(
                "A space, a tab ('\\t') and a line break ('\\n') are all whitespace, and each counts as one character.",
                "trim() removes whitespace from the two ends only, never from the middle.",
                "In a regular expression \\s matches one whitespace character, so split(/\\s+/) splits on runs of it.",
            ),
            example="""
                const s = "  a b\\t";
                console.log(s.length, s.trim().length, s.split(/\\s+/).filter(Boolean));
            """,
            out="6 3 [ 'a', 'b' ]",
        ),
    ),
    *both(
        "letter-case",
        "Letter case",
        "Whether a letter is a capital (upper case) or a small letter (lower case). To a computer 'A' and 'a' are different characters.",
        see=("string", "immutable", "string-comparison"),
        priority=35,
        aka=("case", "uppercase", "lowercase", "upper case", "lower case", "capital letters", "capitalize"),
        python=dict(
            rules=(
                "upper() and lower() give a new string in that case; title() capitalises every word; capitalize() only the first letter.",
                "They do not change the original string: strings are immutable.",
                "'a' == 'A' is False. To compare without caring about case, lower() both sides first.",
            ),
            detect=(r"\.(?:upper|lower|title|capitalize|swapcase|casefold)\(",),
            example="""
                s = "Hello World"
                print(s.upper(), s.lower(), s.title(), s)
            """,
            out="HELLO WORLD hello world Hello World Hello World",
        ),
        javascript=dict(
            rules=(
                "toUpperCase() and toLowerCase() give a new string in that case. There is no built-in title case.",
                "They do not change the original string: strings are immutable.",
                "'a' === 'A' is false. To compare without caring about case, lower-case both sides first.",
            ),
            detect=(r"\.(?:toUpperCase|toLowerCase|toLocaleUpperCase|toLocaleLowerCase)\(",),
            example="""
                const s = "Hello World";
                console.log(s.toUpperCase(), s.toLowerCase(), s);
            """,
            out="HELLO WORLD hello world Hello World",
        ),
    ),
    *both(
        "strip",
        "Strip (trim)",
        "Cutting the whitespace off the start and end of a string, so '  hi  ' becomes 'hi'.",
        see=("whitespace", "immutable", "split"),
        priority=40,
        aka=("trim", "lstrip", "rstrip", "trimstart", "trimend", "trim whitespace"),
        python=dict(
            rules=(
                "strip() cuts both ends, lstrip() only the left end, rstrip() only the right end.",
                "Given text, strip('x') removes any run of those characters from the ends: 'xxhixx'.strip('x') is 'hi'.",
                "It returns a new string and the original is unchanged. The middle is never touched.",
            ),
            detect=(r"\.(?:strip|lstrip|rstrip)\(",),
            example="""
                print(repr("  hi  ".strip()), repr("xxhixx".strip("x")), repr(" a b ".strip()))
            """,
            out="'hi' 'hi' 'a b'",
        ),
        javascript=dict(
            rules=(
                "trim() cuts both ends, trimStart() only the start, trimEnd() only the end.",
                "Unlike Python's strip, trim takes no argument: it only removes whitespace.",
                "It returns a new string and the original is unchanged. The middle is never touched.",
            ),
            detect=(r"\.(?:trim|trimStart|trimEnd)\(",),
            example="""
                console.log("[" + "  hi  ".trim() + "]", "[" + "  hi  ".trimEnd() + "]");
            """,
            out="[hi] [  hi]",
        ),
    ),
    *both(
        "split",
        "Split",
        "Cutting a string into pieces at every separator (the text between the pieces, such as a comma or a space) and getting the pieces as a list.",
        see=("join", "whitespace", "string"),
        priority=45,
        aka=("splitting", "separator", "delimiter", "sep", "tokenize a string"),
        python=dict(
            rules=(
                "'a,b,c'.split(',') is ['a', 'b', 'c']. Two separators in a row leave an empty piece: 'a,,b'.split(',') is ['a', '', 'b'].",
                "split() with no argument splits on whitespace and drops empty pieces; 'a  b'.split() is ['a', 'b'].",
                "split(',', 1) splits at most once: the second number is how many cuts to make.",
            ),
            detect=(r"\.(?:split|rsplit|splitlines)\(",),
            example="""
                print("a,b,c".split(","), "a  b".split(), "a,,b".split(","))
            """,
            out="['a', 'b', 'c'] ['a', 'b'] ['a', '', 'b']",
        ),
        javascript=dict(
            rules=(
                "'a,b,c'.split(',') is ['a', 'b', 'c']. Two separators in a row leave an empty piece: 'a,,b'.split(',') is ['a', '', 'b'].",
                "split('') cuts between every character: 'abc'.split('') is ['a', 'b', 'c'].",
                "A second number is a limit on how many pieces to keep, not how many cuts: 'a,b,c'.split(',', 2) is ['a', 'b'].",
            ),
            detect=(r"\.split\(",),
            example="""
                console.log("a,b,c".split(","), "a,,b".split(","), "abc".split(""));
            """,
            out="[ 'a', 'b', 'c' ] [ 'a', '', 'b' ] [ 'a', 'b', 'c' ]",
        ),
    ),
    *both(
        "join",
        "Join",
        "Gluing a list of strings into one string, with a separator (the text put between the pieces) in between.",
        see=("split", "concatenation", "string"),
        priority=45,
        aka=("joining", "glue strings"),
        python=dict(
            rules=(
                "The separator comes first: '-'.join(['a', 'b']) is 'a-b'. Use '' to join with nothing in between.",
                "Every item must already be a string; join([1, 2]) is a TypeError. Convert first: ', '.join(str(n) for n in nums).",
                "It is the opposite of split: ','.join('a,b,c'.split(',')) gives back 'a,b,c'.",
            ),
            detect=(r"\.join\(",),
            example="""
                print("-".join(["a", "b", "c"]), "".join(["x", "y"]), ", ".join(str(n) for n in [1, 2, 3]))
            """,
            out="a-b-c xy 1, 2, 3",
        ),
        javascript=dict(
            rules=(
                "The separator is the argument: ['a', 'b'].join('-') is 'a-b'. With no argument the separator is a comma.",
                "Items are turned into text on the way: [1, 2, 3].join('') is '123'; null and undefined become empty text.",
                "It is the opposite of split: 'a,b,c'.split(',').join(',') gives back 'a,b,c'.",
            ),
            detect=(r"\.join\(",),
            example="""
                console.log(["a", "b", "c"].join("-"), [1, 2, 3].join(), [1, null, 3].join("-"));
            """,
            out="a-b-c 1,2,3 1--3",
        ),
    ),
    *both(
        "string-search",
        "Searching a string",
        "Asking whether a piece of text appears inside a string, and where. The answer is true or false, or the position where it starts.",
        see=("index", "slice"),
        priority=40,
        aka=("search", "find", "indexof", "index of", "contains", "includes", "startswith", "endswith", "substring search"),
        python=dict(
            see=("index", "slice", "in-operator"),
            rules=(
                "'nan' in 'banana' is True. s.find('na') gives the position of the first match, or -1 when there is none.",
                "s.index('z') does the same but raises a ValueError when the text is missing, so find is the safe one.",
                "s.count('a') counts the matches; s.startswith('ba') and s.endswith('na') test the two ends.",
            ),
            detect=(r"\.(?:find|rfind|index|rindex|count|startswith|endswith)\(",),
            example="""
                s = "banana"
                print("nan" in s, s.find("na"), s.find("z"), s.count("a"))
            """,
            out="True 2 -1 3",
        ),
        javascript=dict(
            rules=(
                "s.includes('nan') is true or false. s.indexOf('na') gives the position of the first match, or -1 when there is none.",
                "s.lastIndexOf('a') looks from the end; s.startsWith('ba') and s.endsWith('na') test the two ends.",
                "Positions start at 0, so a match at the very start has indexOf 0, which is falsy: write indexOf(x) !== -1, not if (indexOf(x)).",
            ),
            detect=(r"\.(?:includes|indexOf|lastIndexOf|startsWith|endsWith|search)\(",),
            example="""
                const s = "banana";
                console.log(s.includes("nan"), s.indexOf("na"), s.indexOf("z"), s.lastIndexOf("a"));
            """,
            out="true 2 -1 5",
        ),
    ),
    *both(
        "replace",
        "Replace",
        "Making a new string where every copy of some text is swapped for other text.",
        see=("immutable", "string-search", "string"),
        priority=40,
        aka=("replacing", "substitute", "replaceall"),
        python=dict(
            rules=(
                "s.replace(old, new) replaces EVERY match. A third number limits how many: 'aaa'.replace('a', 'b', 2) is 'bba'.",
                "It returns a new string; s itself is unchanged because strings are immutable. Forgetting to keep the result is a classic bug.",
                "If old is not found, the result is just the same text.",
            ),
            detect=(r"\.replace\(",),
            example="""
                s = "a-b-c"
                print(s.replace("-", "+"), s.replace("-", "+", 1), s)
            """,
            out="a+b+c a+b-c a-b-c",
        ),
        javascript=dict(
            rules=(
                "With a text argument, replace changes only the FIRST match; replaceAll changes every one.",
                "A regular expression with the g flag also replaces every match: s.replace(/-/g, '+').",
                "Both return a new string; s itself is unchanged because strings are immutable.",
            ),
            detect=(r"\.(?:replace|replaceAll)\(",),
            example="""
                const s = "a-b-c";
                console.log(s.replace("-", "+"), s.replaceAll("-", "+"), s);
            """,
            out="a+b-c a+b+c a-b-c",
        ),
    ),
    *both(
        "format",
        "Formatting text",
        "Turning values into text laid out the way you want: how many decimal places, how wide, aligned left or right.",
        see=("padding", "rounding", "string"),
        priority=45,
        aka=("formatting", "string formatting", "format spec", "format specifier", "number formatting", "decimal places", "precision"),
        python=dict(
            rules=(
                "After a colon inside an f-string braces comes the layout: {x:.2f} is two decimal places, {x:>8} right-aligns in 8 characters, {x:05d} pads with zeros.",
                "{n:,} puts commas in thousands and {x:.1%} shows a fraction as a percentage.",
                "'{:.2f}'.format(x) and the % operator do the same job in older code.",
            ),
            detect=(r"raw:\{[^{}\n]*:[<>^=+,.\d%a-z]+\}", r"\.format\("),
            example="""
                x = 3.14159
                print(f"{x:.2f}|{7:>4}|{7:<4}|{7:04d}|{1234567:,}")
            """,
            out="3.14|   7|7   |0007|1,234,567",
        ),
        javascript=dict(
            rules=(
                "x.toFixed(2) gives a string with exactly two decimal places. It is a string, not a number.",
                "String(7).padStart(4) right-aligns in 4 characters and padStart(4, '0') pads with zeros; padEnd pads on the right.",
                "toFixed rounds the stored binary value, so (1.005).toFixed(2) is '1.00' and not '1.01'.",
            ),
            detect=(r"\.(?:toFixed|toPrecision|padStart|padEnd|toLocaleString)\(",),
            example="""
                console.log([(3.14159).toFixed(2), String(7).padStart(4), String(7).padStart(4, "0")].join("|"));
            """,
            out="3.14|   7|0007",
        ),
    ),
    *both(
        "padding",
        "Padding",
        "Adding filler characters (spaces, zeros, dots) to a string until it reaches a width, so columns line up.",
        see=("format", "string", "immutable"),
        priority=40,
        aka=("pad", "pad left", "pad right", "zfill", "ljust", "rjust", "center", "padstart", "padend", "zero padding"),
        python=dict(
            rules=(
                "s.rjust(5) pads on the left (right-aligns), s.ljust(5) pads on the right, s.center(5) both sides; a second argument is the filler.",
                "'7'.zfill(3) is '007'. In an f-string: f'{s:>5}' right-aligns and f'{s:<5}' left-aligns.",
                "Padding never cuts: a string already longer than the width comes back unchanged.",
            ),
            detect=(r"\.(?:ljust|rjust|center|zfill)\(",),
            example="""
                print("[" + "7".rjust(3) + "]", "7".zfill(3), "ab".ljust(4, "."), "ab".center(6, "*"))
            """,
            out="[  7] 007 ab.. **ab**",
        ),
        javascript=dict(
            rules=(
                "s.padStart(5) pads on the left (right-aligns) and s.padEnd(5) on the right; the second argument is the filler, a space by default.",
                "'7'.padStart(3, '0') is '007'. The width counts the whole result, not just the filler.",
                "Padding never cuts: a string already longer than the width comes back unchanged.",
            ),
            detect=(r"\.(?:padStart|padEnd)\(",),
            example="""
                console.log("7".padStart(3, "0"), "ab".padEnd(5, ".") + "|", "abcdef".padStart(3));
            """,
            out="007 ab...| abcdef",
        ),
    ),
    *both(
        "character",
        "Character",
        "One single letter, digit, space or symbol: the smallest piece of a string.",
        see=("string", "index", "ascii"),
        priority=30,
        aka=("char", "characters", "letter", "glyph"),
        python=dict(
            rules=(
                "Python has no separate character type: a character is just a string of length 1.",
                "s[0] is the first character and looping over a string gives one character at a time.",
                "len() counts characters, so len('é') is 1 and len('😀') is 1.",
            ),
            example="""
                print(list("hey"), "hey"[1], len("é"), len("😀"))
            """,
            out="['h', 'e', 'y'] e 1 1",
        ),
        javascript=dict(
            rules=(
                "JavaScript has no separate character type: a character is a string of length 1.",
                "s[0] is the first character, and [...s] or for...of gives one character at a time.",
                "length counts UTF-16 units, not what you see: '😀'.length is 2, while [...'😀'].length is 1.",
            ),
            example="""
                console.log([..."hey"], "hey"[1], "é".length, "😀".length);
            """,
            out="[ 'h', 'e', 'y' ] e 1 2",
        ),
    ),
    *both(
        "ascii",
        "ASCII and character codes",
        "Every character is stored as a number, its code: 'A' is 65, 'a' is 97 and '0' is 48. ASCII is the old table of the first 128 of them.",
        see=("character", "string-comparison", "modulo"),
        priority=45,
        aka=("character code", "char code", "unicode", "code point", "ord", "chr", "charcodeat", "fromcharcode", "character codes"),
        python=dict(
            rules=(
                "ord('A') gives the number 65 and chr(65) gives back 'A'.",
                "Letters are in alphabetical order: ord('b') - ord('a') is 1. Capitals come before lower case, and ord('a') - ord('A') is 32.",
                "To shift a letter inside a..z wrap with %: chr((ord(c) - ord('a') + 3) % 26 + ord('a')).",
            ),
            detect=(r"\b(?:ord|chr)\(",),
            example="""
                print(ord("A"), chr(97), ord("a") - ord("A"), chr(ord("a") + 1))
            """,
            out="65 a 32 b",
        ),
        javascript=dict(
            rules=(
                "'A'.charCodeAt(0) gives the number 65 and String.fromCharCode(65) gives back 'A'.",
                "Letters are in alphabetical order: the code of 'b' is one more than the code of 'a'. Capitals come before lower case, 32 apart.",
                "To shift a letter inside a..z wrap with %: (code - 97 + 3) % 26 + 97.",
            ),
            detect=(r"\.(?:charCodeAt|codePointAt)\(|\bString\.fromCharCode\(|\bString\.fromCodePoint\(",),
            example="""
                console.log("A".charCodeAt(0), String.fromCharCode(97), "a".charCodeAt(0) - "A".charCodeAt(0), String.fromCharCode("a".charCodeAt(0) + 1));
            """,
            out="65 a 32 b",
        ),
    ),
    *both(
        "palindrome",
        "Palindrome",
        "A word or number that reads the same forwards and backwards, like 'level' or 12321.",
        see=("slice", "string-comparison", "letter-case"),
        priority=40,
        aka=("palindromes", "reads the same backwards"),
        python=dict(
            rules=(
                "The test is s == s[::-1]: compare the string with its reverse.",
                "Case matters unless you lower() first: 'Level' is not a palindrome but 'level' is.",
                "Spaces and punctuation count too; to ignore them filter them out before comparing.",
            ),
            example="""
                for w in ("level", "hello"):
                    print(w, w == w[::-1])
            """,
            out="level True\nhello False",
        ),
        javascript=dict(
            rules=(
                "There is no string reverse, so the test is s === [...s].reverse().join(''): split into characters, reverse, glue back.",
                "Case matters unless you toLowerCase() first: 'Level' is not a palindrome but 'level' is.",
                "Spaces and punctuation count too; to ignore them filter them out before comparing.",
            ),
            example="""
                for (const w of ["level", "hello"]) {
                  console.log(w, w === [...w].reverse().join(""));
                }
            """,
            out="level true\nhello false",
        ),
    ),
    *both(
        "anagram",
        "Anagram",
        "A word made from the same letters as another in a different order: 'listen' and 'silent'.",
        see=("sorting", "palindrome", "string-comparison"),
        priority=40,
        aka=("anagrams", "same letters"),
        python=dict(
            rules=(
                "Two words are anagrams when their letters, sorted, are the same list: sorted(a) == sorted(b).",
                "They must have the same length, and case and spaces count unless you remove them first.",
                "A word is an anagram of itself, but 'abc' and 'abd' are not anagrams: one letter differs.",
            ),
            example="""
                print(sorted("listen") == sorted("silent"), sorted("abc") == sorted("abd"))
            """,
            out="True False",
        ),
        javascript=dict(
            rules=(
                "Two words are anagrams when their letters, sorted, are the same: [...a].sort().join('') === [...b].sort().join('').",
                "They must have the same length, and case and spaces count unless you remove them first.",
                "A word is an anagram of itself, but 'abc' and 'abd' are not anagrams: one letter differs.",
            ),
            example="""
                const key = (s) => [...s].sort().join("");
                console.log(key("listen") === key("silent"), key("abc") === key("abd"));
            """,
            out="true false",
        ),
    ),
    *both(
        "string-comparison",
        "Comparing strings",
        "Strings are compared character by character using each character's code, so the order is not always the one a dictionary uses.",
        see=("comparison", "ascii", "sorting"),
        priority=45,
        aka=("string comparison", "compare strings", "alphabetical order", "dictionary order", "lexicographic", "lexicographical"),
        python=dict(
            rules=(
                "The first differing character decides: 'apple' < 'banana' is True.",
                "Capitals come before lower case: 'Z' < 'a' is True.",
                "Digits are text here, so '10' < '9' is True. A shorter string that is the start of a longer one is smaller: 'ab' < 'abc'.",
            ),
            example="""
                print("apple" < "banana", "Z" < "a", "10" < "9", "ab" < "abc")
            """,
            out="True True True True",
        ),
        javascript=dict(
            rules=(
                "The first differing character decides: 'apple' < 'banana' is true. Comparing two strings never turns them into numbers.",
                "Capitals come before lower case: 'Z' < 'a' is true. Digits are text here, so '10' < '9' is true.",
                "a.localeCompare(b) compares the way a person would, ignoring that capitals come first: 'a'.localeCompare('B') is -1.",
            ),
            example="""
                console.log("apple" < "banana", "Z" < "a", "10" < "9", "ab" < "abc");
            """,
            out="true true true true",
        ),
    ),
]
