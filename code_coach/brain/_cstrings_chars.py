"""C strings and memory pack, part 4: Char Class and Parse by Hand.

Only the four fixed headers are there, so there is no ctype.h (`isalpha`, `toupper`) and no stdlib.h (`atoi`, `strtol`):
classification is written with comparisons on the ASCII codes and parsing with loops, which is the point. Answers are
worked out with plain Python on the characters; characters that may be a space are printed inside `[ ]` or `| |` so the
answer never starts or ends with a blank.
"""

from __future__ import annotations

from ._cstrings_model import PF, T, CS, strcmp_sign
from ._model import Maker


def _lower(c: str) -> bool:
    return "a" <= c <= "z"


def _upper(c: str) -> bool:
    return "A" <= c <= "Z"


def _digit(c: str) -> bool:
    return "0" <= c <= "9"


def _alpha(c: str) -> bool:
    return _lower(c) or _upper(c)


def _b(x: bool) -> int:
    return 1 if x else 0


def _caesar(w: str, k: int) -> str:
    return "".join(chr(97 + (ord(c) - 97 + k) % 26) for c in w)


C = r"char c = '$ch';"

# ── 7. Char Class ───────────────────────────────────────────────────────

CLASSES: list[Maker] = [
    CS(T(C, PF("%d", "c >= 'a' && c <= 'z'")), lambda p: _b(_lower(p["ch"])), "Lower-case letters are the codes from 'a' to 'z'."),
    CS(T(C, PF("%d", "c >= 'A' && c <= 'Z'")), lambda p: _b(_upper(p["ch"])), "Capitals are the codes from 'A' to 'Z'."),
    CS(T(C, PF("%d", "c >= '0' && c <= '9'")), lambda p: _b(_digit(p["ch"])), "The digit characters are consecutive, '0' to '9'."),
    CS(T(C, PF("%d", "(c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')")), lambda p: _b(_alpha(p["ch"])), "A letter is either kind."),
    CS(T(C, PF("%d", "(c >= 'a' && c <= 'z') || (c >= '0' && c <= '9')")), lambda p: _b(_lower(p["ch"]) or _digit(p["ch"])),
       "Lower-case letters or digits (capitals do not count here)."),
    CS(T(C, PF("%d", "(c | 32) >= 'a' && (c | 32) <= 'z'")), lambda p: _b(_alpha(p["ch"])),
       "Setting bit 32 turns a capital into its lower-case letter, so one range test covers both cases."),
    CS(T(C, PF("%d", "c == ' ' || c == '\\t' || c == '\\n'")), lambda p: _b(p["ch"] == " "), "White space: a space, a tab or a newline."),
    CS(T(C, PF("%d", "c == 32")), lambda p: _b(p["ch"] == " "), "A space is the number 32."),
    CS(T(C, PF("%d", "c < 'A'")), lambda p: _b(ord(p["ch"]) < 65), "Spaces, digits and most punctuation come before 'A' in ASCII."),
    CS(T(C, PF("%d", "(uint8_t)(c - 'a') < 26")), lambda p: _b(_lower(p["ch"])),
       "Anything below 'a' wraps to a big uint8_t, so one comparison tests the whole range."),
    CS(T(C, PF("%d", "(uint8_t)(c - 'a')")), lambda p: (ord(p["ch"]) - 97) % 256,
       "A character below 'a' goes negative, which wraps around 256 in a uint8_t."),
    CS(T(C, PF("%d", "(unsigned)(c - '0') <= 9")), lambda p: _b(_digit(p["ch"])),
       "A negative int converted to unsigned is huge, so one comparison tests digits."),
    CS(T(C, PF("%d", "(c ^ '0') < 10")), lambda p: _b(_digit(p["ch"])), "XOR with '0' (48) leaves 0-9 only for the digit characters."),
    CS(T(C, r"if (c >= 'a' && c <= 'z')", r"    c -= 32;", PF("[%c]", "c")), lambda p: "[" + (p["ch"].upper() if _lower(p["ch"]) else p["ch"]) + "]",
       "Lower-case letters are 32 above their capitals; anything else is left alone."),
    CS(T(C, r"if (c >= 'A' && c <= 'Z')", r"    c += 32;", PF("[%c]", "c")), lambda p: "[" + (p["ch"].lower() if _upper(p["ch"]) else p["ch"]) + "]",
       "Capitals become lower-case by adding 32; everything else stays."),
    CS(T(C, r"if ((c | 32) >= 'a' && (c | 32) <= 'z')", r"    c ^= 32;", PF("[%c]", "c")),
       lambda p: "[" + (p["ch"].swapcase() if _alpha(p["ch"]) else p["ch"]) + "]", "XOR with 32 flips a letter's case."),
    CS(PF("%c", "'$x' ^ 32"), lambda p: p["X"], "Bit 32 is the difference between a letter and its capital."),
    CS(PF("%c", "'$X' | 32"), lambda p: p["x"], "OR with 32 forces lower case."),
    CS(PF("%c", "'$x' & 0xDF"), lambda p: p["X"], "0xDF is every bit but 32: AND clears it and makes a capital."),
    CS(PF("%d", "'$ch'"), lambda p: ord(p["ch"]), "The code of the character."),
    CS(PF("%d", "'$ch' - '$ch2'"), lambda p: ord(p["ch"]) - ord(p["ch2"]), "The difference of two codes."),
    CS(PF("%d", "'$ch' < '$ch2'"), lambda p: _b(ord(p["ch"]) < ord(p["ch2"])), "Characters compare as their ASCII codes."),
    CS(PF("%d", """'$ch' == '$ch2'"""), lambda p: _b(p["ch"] == p["ch2"]), "Equal only when they are the same character."),
    CS(PF("%d", """"$D"[$q] - '0'"""), lambda p: int(p["D"][p["q"]]), "A digit character minus '0' is the digit's value."),
    CS(T(r'const char *s = "$D";', r"int sum = 0;", r"for (; *s; s++)", r"    sum += *s - '0';", PF("%d", "sum")), lambda p: p["Dsum"],
       "Each digit character is turned into its value and added."),
    CS(PF("%d", """"$D"[0] & 15"""), lambda p: int(p["D"][0]), "The low four bits of a digit character are its value."),
    CS(PF("%d", """'$hd' >= 'A' ? '$hd' - 'A' + 10 : '$hd' - '0'"""), lambda p: p["hdv"],
       "A hex letter counts from 10; a digit counts from 0."),
    CS(PF("%d", """('$ch' >= '0' && '$ch' <= '9') || ('$ch' >= 'A' && '$ch' <= 'F') || ('$ch' >= 'a' && '$ch' <= 'f')"""),
       lambda p: _b(_digit(p["ch"]) or "A" <= p["ch"] <= "F" or "a" <= p["ch"] <= "f"), "A hex digit is 0-9, A-F or a-f."),
    CS(PF("%c", """'a' + ('$f' - 'a' + $s) % 26"""), lambda p: chr(97 + (ord(p["f"]) - 97 + p["s"]) % 26),
       "Shift along the alphabet and wrap round with % 26."),
    CS(PF("%c", """'a' + ('$f' - 'a' - $k + 26) % 26"""), lambda p: chr(97 + (ord(p["f"]) - 97 - p["k"]) % 26),
       "Shifting back: add 26 first so the % never sees a negative number."),
    CS(PF("%c", """'a' + ('z' - 'a' - $q + $a) % 26"""), lambda p: chr(97 + (25 - p["q"] + p["a"]) % 26),
       "Starting near the end of the alphabet, the shift wraps past z back to the front."),
    CS(T(r'char s[] = "$w";', r"for (char *p = s; *p; p++)", r"    *p = 'a' + (*p - 'a' + $s) % 26;", PF("%s", "s")),
       lambda p: _caesar(p["w"], p["s"]), "A Caesar cipher: every letter moves s places along the alphabet."),
    CS(T(r'char s[] = "$w";', r"for (int r = 0; r < 2; r++)", r"    for (char *p = s; *p; p++)", r"        *p = 'a' + (*p - 'a' + 13) % 26;", PF("%s", "s")),
       lambda p: p["w"], "13 twice is 26, a full turn of the alphabet: ROT13 undoes itself."),
    CS(T(r'char s[] = "$w";', r"for (char *p = s; *p; p++)", r"    *p = 'a' + (*p - 'a' + $s) % 26;", r"for (char *p = s; *p; p++)",
         r"    *p = 'a' + (*p - 'a' + 26 - $s) % 26;", PF("%s", "s")), lambda p: p["w"], "Shifting forward then back by the same amount returns the word."),
    CS(PF("%d", """'$f' == 'a' || '$f' == 'e' || '$f' == 'i' || '$f' == 'o' || '$f' == 'u'"""), lambda p: _b(p["f"] in "aeiou"),
       "A vowel test written with comparisons."),
    CS(T(r'const char *s = "$w";', r"int n = 0;", r"for (; *s; s++)", r"    if (*s == 'a' || *s == 'e' || *s == 'i' || *s == 'o' || *s == 'u')",
         r"        n++;", PF("%d", "n")), lambda p: sum(1 for c in p["w"] if c in "aeiou"), "The loop counts the vowels."),
    CS(T(r'const char *s = "$w";', r"int n = 0;", r"for (; *s; s++)", r"    if (*s != 'a' && *s != 'e' && *s != 'i' && *s != 'o' && *s != 'u')",
         r"        n++;", PF("%d", "n")), lambda p: sum(1 for c in p["w"] if c not in "aeiou"), "Every letter that is not a vowel is counted."),
    CS(PF("%d", """'$f' - 'a' + 1"""), lambda p: ord(p["f"]) - 96, "The place of the letter in the alphabet, counting a as 1."),
    CS(T(C, PF("%c", "c >= 'a' ? 'L' : c >= 'A' ? 'U' : c >= '0' ? 'D' : 'O'")),
       lambda p: "L" if ord(p["ch"]) >= 97 else "U" if ord(p["ch"]) >= 65 else "D" if ord(p["ch"]) >= 48 else "O",
       "Each test only looks at the bottom of a range: '_' and '~' sit above 'A' or 'a' without being those letters."),
    CS(T(r'char s[] = "$mix";', r"int n = 0;", r"for (int i = 0; s[i]; i++)", r"    if (s[i] >= 'a' && s[i] <= 'z')", r"        n++;", PF("%d", "n")),
       lambda p: sum(_lower(c) for c in p["mix"]), "Counting lower-case letters."),
    CS(T(r'char s[] = "$mix";', r"int n = 0;", r"for (int i = 0; s[i]; i++)", r"    if (s[i] >= 'A' && s[i] <= 'Z')", r"        n++;", PF("%d", "n")),
       lambda p: sum(_upper(c) for c in p["mix"]), "Counting capitals."),
    CS(T(r'char s[] = "$mix";', r"int n = 0;", r"for (int i = 0; s[i]; i++)", r"    if (s[i] >= '0' && s[i] <= '9')", r"        n++;", PF("%d", "n")),
       lambda p: sum(_digit(c) for c in p["mix"]), "Counting digit characters."),
    CS(T(r'char s[] = "$mix";', r"int n = 0;", r"for (int i = 0; s[i]; i++)", r"    if (s[i] == ' ')", r"        n++;", PF("%d", "n")),
       lambda p: p["mix"].count(" "), "Counting spaces."),
    CS(T(r'char s[] = "$mix";', r"int n = 0;", r"for (int i = 0; s[i]; i++)", r"    if (!((s[i] | 32) >= 'a' && (s[i] | 32) <= 'z'))", r"        n++;",
         PF("%d", "n")), lambda p: sum(not _alpha(c) for c in p["mix"]), "Counting everything that is not a letter."),
    CS(T(r'char s[] = "$mix";', r"for (int i = 0; s[i]; i++)", r"    if (s[i] >= 'a' && s[i] <= 'z')", r"        s[i] -= 32;", PF("[%s]", "s")),
       lambda p: "[" + "".join(c.upper() if _lower(c) else c for c in p["mix"]) + "]", "Every lower-case letter becomes a capital; digits and spaces are left."),
    CS(T(r'char s[] = "$mix";', r"for (int i = 0; s[i]; i++)", r"    if ((s[i] | 32) >= 'a' && (s[i] | 32) <= 'z')", r"        s[i] ^= 32;", PF("[%s]", "s")),
       lambda p: "[" + p["mix"].swapcase() + "]", "XOR 32 flips the case of each letter."),
    CS(T(r'const char *s = "$mix";', r"int k = -1;", r"for (int i = 0; s[i]; i++)", r"    if (s[i] >= '0' && s[i] <= '9') {", r"        k = i;",
         r"        break;", r"    }", PF("%d", "k")), lambda p: next((i for i, c in enumerate(p["mix"]) if _digit(c)), -1),
       "The position of the first digit, or -1 if there is none."),
    CS(T(r'const char *s = "$mix";', r"int sum = 0;", r"for (int i = 0; s[i]; i++)", r"    if (s[i] >= '0' && s[i] <= '9')", r"        sum += s[i] - '0';",
         PF("%d", "sum")), lambda p: sum(int(c) for c in p["mix"] if _digit(c)), "Only the digit characters are added."),
    CS(T(r"uint8_t c = '$ch';", r"c += 200;", PF("%d", "c")), lambda p: (ord(p["ch"]) + 200) % 256, "A uint8_t wraps around after 255."),
    CS(T(r"unsigned char c = '$ch';", r"c = c * 2;", PF("%d", "c")), lambda p: (ord(p["ch"]) * 2) % 256,
       "c * 2 is worked out as an int, then stored back into an unsigned char: modulo 256."),
]


# ── 8. Parse by Hand ────────────────────────────────────────────────────

def _title(p: dict) -> str:
    return f"{p['Wc']} {p['Zc']}"


def _no_vowels(p: dict) -> str:
    return "".join(c for c in p["w"] if c not in "aeiou")


def _rle(s: str) -> str:
    out, i = "", 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out += f"{s[i]}{j - i}"
        i = j
    return out


def _max_run(s: str) -> int:
    best = cur = 1
    for i in range(1, len(s)):
        cur = cur + 1 if s[i] == s[i - 1] else 1
        best = max(best, cur)
    return best


def _hash(w: str) -> int:
    h = 5381
    for c in w:
        h = (h * 33 + ord(c)) % (1 << 32)
    return h


def _longest(p: dict) -> int:
    return max(len(p["w"]), len(p["z"]), len(p["v"]))


def _word_count(p: dict) -> int:
    return 3


def _pal(p: dict) -> str:
    return "yes" if p["ispal"] else "no"


def _all_digits(p: dict) -> int:
    return p["r"]


def _weighted(p: dict) -> int:
    return sum((i + 1) * int(c) for i, c in enumerate(p["D"]))


PARSES: list[Maker] = [
    CS(T(r'const char *s = "$D";', r"int n = 0;", r"for (; *s; s++)", r"    n = n * 10 + (*s - '0');", PF("%d", "n")), lambda p: int(p["D"]),
       "Each digit pushes the number left a place (times 10) and adds its value."),
    CS(T(r'const char *s = "-$D";', r"int neg = 0, n = 0;", r"if (*s == '-') {", r"    neg = 1;", r"    s++;", r"}", r"for (; *s; s++)",
         r"    n = n * 10 + (*s - '0');", PF("%d", "neg ? -n : n")), lambda p: -int(p["D"]), "The sign is noted first, the digits parsed, then the sign applied."),
    CS(T(r'const char *s = "$n$w";', r"int n = 0;", r"while (*s >= '0' && *s <= '9') {", r"    n = n * 10 + (*s - '0');", r"    s++;", r"}", PF("%d", "n")),
       lambda p: p["n"], "Parsing stops at the first character that is not a digit."),
    CS(T(r"int a = 0, b = 0, *cur = &a;", r'for (const char *s = "$n,$m"; *s; s++) {', r"    if (*s == ',')", r"        cur = &b;", r"    else",
         r"        *cur = *cur * 10 + (*s - '0');", r"}", PF("%d", "a + b")), lambda p: p["n"] + p["m"],
       "Digits go into a until the comma, then into b."),
    CS(T(r'const char *s = "$hx";', r"int n = 0;", r"for (; *s; s++)", r"    n = n * 16 + (*s >= 'A' ? *s - 'A' + 10 : *s - '0');", PF("%d", "n")),
       lambda p: p["hxv"], "Base 16: multiply by 16 for each digit; letters count from 10."),
    CS(T(r'const char *s = "$bin";', r"int n = 0;", r"for (; *s; s++)", r"    n = n * 2 + (*s - '0');", PF("%d", "n")), lambda p: p["binv"],
       "Base 2: double and add the bit."),
    CS(T(r'const char *s = "$hh:$mm";', r"int h = (s[0] - '0') * 10 + (s[1] - '0');", r"int m = (s[3] - '0') * 10 + (s[4] - '0');", PF("%d", "h * 60 + m")),
       lambda p: int(p["hh"]) * 60 + int(p["mm"]), "Two digits at a time; the colon at index 2 is skipped."),
    CS(T(r'const char *s = "$D";', r"int n = 0;", r"for (; *s; s++)", r"    n = n * 10 + (*s - '0');", PF("%d", "n % $a")), lambda p: int(p["D"]) % p["a"],
       "Parse the number first, then take the remainder."),
    CS(T(r'const char *s = "  $w  $z $v ";', r"int n = 0, in = 0;", r"for (; *s; s++) {", r"    if (*s != ' ' && !in)", r"        n++;", r"    in = *s != ' ';", r"}",
         PF("%d", "n")), _word_count, "A word starts where a non-space follows a space."),
    CS(T(r'const char *s = "$w $z";', r"int n = 0;", r"for (; *s; s++)", r"    if (*s == 'a' || *s == 'e' || *s == 'i' || *s == 'o' || *s == 'u')",
         r"        n++;", PF("%d", "n")), lambda p: sum(1 for c in p["w"] + p["z"] if c in "aeiou"), "Vowels counted across both words."),
    CS(T(r'const char *s = "$w$z";', r"int n = 0;", r"for (; *s; s++)", r"    if (*s == '$f')", r"        n++;", PF("%d", "n")),
       lambda p: (p["w"] + p["z"]).count(p["f"]), "How many times the letter appears."),
    CS(T(r'const char *s = "$w $z $v";', r"int cur = 0, best = 0;", r"for (; *s; s++) {", r"    cur = *s == ' ' ? 0 : cur + 1;", r"    if (cur > best)",
         r"        best = cur;", r"}", PF("%d", "best")),
       _longest, "The length of the longest word."),
    CS(T(r'char s[] = "$w";', r"int n = strlen(s);", r"for (int i = 0; i < n / 2; i++) {", r"    char t = s[i];", r"    s[i] = s[n - 1 - i];", r"    s[n - 1 - i] = t;", r"}",
         PF("%s", "s")), lambda p: p["w"][::-1], "Swap the ends and move inwards until the middle."),
    CS(T(r'char s[] = "$w";', r"int n = strlen(s);", r"for (int i = 0; i < n / 2; i++) {", r"    char t = s[i];", r"    s[i] = s[n - 1 - i];", r"    s[n - 1 - i] = t;", r"}",
         PF("%c", "s[0]")), lambda p: p["w"][-1], "After reversing, the first letter is the old last one."),
    CS(T(r'const char *s = "$pal";', r"int i = 0, j = strlen(s) - 1, ok = 1;", r"while (i < j) {", r"    if (s[i] != s[j])", r"        ok = 0;", r"    i++;", r"    j--;", r"}",
         PF("%s", 'ok ? "yes" : "no"')), _pal, "Compare letters from both ends moving inwards: any mismatch means it is not a palindrome."),
    CS(T(r"int n = $big;", r"char b[12];", r"int i = 11;", r"b[i] = 0;", r"while (n > 0) {", r"    b[--i] = '0' + n % 10;", r"    n /= 10;", r"}", PF("%s", "b + i")),
       lambda p: str(p["big"]), "Digits come off the end with % 10 and are written from the back of the buffer."),
    CS(T(r"int n = $big, s = 0;", r"while (n > 0) {", r"    s += n % 10;", r"    n /= 10;", r"}", PF("%d", "s")), lambda p: sum(int(c) for c in str(p["big"])),
       "% 10 takes the last digit, / 10 drops it."),
    CS(T(r"int n = $n * $big, k = 0;", r"while (n > 0) {", r"    k++;", r"    n /= 10;", r"}", PF("%d", "k")), lambda p: len(str(p["n"] * p["big"])),
       "Counting how many times the number can be divided by 10."),
    CS(T(r'char s[] = "$w";', r"for (char *p = s; *p; p++)", r"    if (*p >= 'a' && *p <= 'z')", r"        *p -= 32;", PF("%s", "s")), lambda p: p["w"].upper(),
       "Every lower-case letter minus 32 is its capital."),
    CS(T(r'char s[] = "$w";', r"s[0] -= 32;", PF("%s", "s")), lambda p: p["Wc"], "Only the first letter."),
    CS(T(r'char s[] = "$w";', r"int w = 0;", r"for (int r = 0; s[r]; r++)", r"    if (!(s[r] == 'a' || s[r] == 'e' || s[r] == 'i' || s[r] == 'o' || s[r] == 'u'))",
         r"        s[w++] = s[r];", r"s[w] = 0;", PF("%s", "s")), _no_vowels, "Two indexes: r reads every letter, w writes only the consonants."),
    CS(T(r'const char *s = "$rl";', r"int i = 0, j;", r"while (s[i]) {", r"    j = i;", r"    while (s[j] == s[i])", r"        j++;", r'    printf("%c%d", s[i], j - i);', r"    i = j;", r"}",
         r'printf("\n");'), lambda p: _rle(p["rl"]), "Run-length encoding: each letter with how long its run is."),
    CS(T(r'const char *s = "$rl";', r"int n = 0;", r"for (int i = 1; s[i]; i++)", r"    if (s[i] == s[i - 1])", r"        n++;", PF("%d", "n")),
       lambda p: sum(1 for i in range(1, len(p["rl"])) if p["rl"][i] == p["rl"][i - 1]), "Counts the places where a letter repeats the one before it."),
    CS(T(r'const char *s = "$rl";', r"int cur = 1, best = 1;", r"for (int i = 1; s[i]; i++) {", r"    cur = s[i] == s[i - 1] ? cur + 1 : 1;", r"    if (cur > best)",
         r"        best = cur;", r"}", PF("%d", "best")), lambda p: _max_run(p["rl"]), "The longest run of one letter."),
    CS(T(r'const char *s = "$dm";', r"int sum = 0;", r"for (; *s; s++)", r"    if (*s >= '0' && *s <= '9')", r"        sum += *s - '0';", PF("%d", "sum")),
       lambda p: p["dmsum"], "The letters are skipped; the digits are added."),
    CS(T(r'const char *s = "$dm";', r"int best = 0;", r"for (; *s; s++)", r"    if (*s >= '0' && *s <= '9' && *s - '0' > best)", r"        best = *s - '0';", PF("%d", "best")),
       lambda p: max(int(c) for c in p["dm"] if c.isdigit()), "The biggest digit seen."),
    CS(T(r'const char *s = "$dm";', r"int d = 0, l = 0;", r"for (; *s; s++) {", r"    if (*s >= '0' && *s <= '9')", r"        d++;", r"    else", r"        l++;", r"}",
         PF("%d %d", "d, l")), lambda p: f"{sum(c.isdigit() for c in p['dm'])} {sum(not c.isdigit() for c in p['dm'])}", "Digits first, then letters."),
    CS(T(r"unsigned h = 5381;", r'for (const char *s = "$w"; *s; s++)', r"    h = h * 33 + *s;", PF("%u", "h")), lambda p: _hash(p["w"]),
       "A tiny hash: each letter is mixed in, and unsigned arithmetic wraps around 2^32."),
    CS(T(r'const char *s = "$w";', r"int sum = 0;", r"for (; *s; s++)", r"    sum += *s;", PF("%d", "sum")), lambda p: sum(ord(c) for c in p["w"]),
       "The ASCII codes of the letters, added."),
    CS(T(r'char s[] = "$w";', r"for (int i = 0; s[i]; i++)", r"    for (int j = i + 1; s[j]; j++)", r"        if (s[j] < s[i]) {",
         r"            char t = s[i];", r"            s[i] = s[j];", r"            s[j] = t;", r"        }", PF("%s", "s")), lambda p: "".join(sorted(p["w"])),
       "Each letter is swapped with any later one that is smaller, which leaves the letters in alphabetical order."),
    CS(T(r'char s[] = "$w   ";', r"int n = strlen(s);", r"while (n > 0 && s[n - 1] == ' ')", r"    n--;", r"s[n] = 0;", PF("[%s]", "s")), lambda p: f"[{p['w']}]",
       "Trailing spaces are chopped by moving the NUL back."),
    CS(T(r'const char *s = "$w\n$z\n$v";', r"int n = 1;", r"for (; *s; s++)", r"    if (*s == '\n')", r"        n++;", PF("%d", "n")), 3,
       "Two newlines make three lines."),
    CS(T(r"int cmp(const char *a, const char *b) {", r"    while (*a && *a == *b) {", r"        a++;", r"        b++;", r"    }", r"    return (*a > *b) - (*a < *b);", r"}",
         r"int main(void) {", r'    printf("%d\n", cmp("$w", "$z"));', r"}"), lambda p: strcmp_sign(p["w"], p["z"]),
       "A hand-written strcmp: walk while the letters match, then compare the first that differs."),
    CS(T(r"void cat(char *d, const char *s) {", r"    while (*d) d++;", r"    while ((*d++ = *s++))", r"        ;", r"}", r"int main(void) {",
         r'    char b[20] = "$w";', r'    cat(b, "$z");', r'    printf("%s\n", b);', r"}"), lambda p: p["w"] + p["z"],
       "Find the end of d, then copy s there, NUL included: strcat by hand."),
    CS(T(r'const char *s = $r ? "$D" : "$D$x";', r"int ok = 1;", r"for (; *s; s++)", r"    if (*s < '0' || *s > '9')", r"        ok = 0;", PF("%d", "ok")),
       _all_digits, "One non-digit character makes the whole string fail."),
    CS(T(r'const char *s = "$D";', r"int sum = 0;", r"for (int i = 0; s[i]; i++)", r"    sum += (i + 1) * (s[i] - '0');", PF("%d", "sum")), _weighted,
       "A weighted checksum: each digit counts times its 1-based position."),
    CS(T(r'const char *s = "$w";', r"char m = s[0];", r"for (int i = 1; s[i]; i++)", r"    if (s[i] < m)", r"        m = s[i];", PF("%c", "m")), lambda p: min(p["w"]),
       "The letter that comes first in the alphabet."),
    CS(T(r'const char *s = "$w$z";', r"int seen[26] = {0}, n = 0;", r"for (; *s; s++)", r"    seen[*s - 'a'] = 1;", r"for (int i = 0; i < 26; i++)", r"    n += seen[i];", PF("%d", "n")),
       lambda p: len(set(p["w"] + p["z"])), "A flag per letter: the sum is how many different letters appeared."),
    CS(T(r'const char *s = "$w$z";', r"int cnt[26] = {0};", r"for (; *s; s++)", r"    cnt[*s - 'a']++;", PF("%d", "cnt['$f' - 'a']")), lambda p: (p["w"] + p["z"]).count(p["f"]),
       "A counter per letter, indexed by the letter's place in the alphabet."),
    CS(T(r'char s[] = "$w $z";', r"for (int i = 0; s[i]; i++)", r"    if (i == 0 || s[i - 1] == ' ')", r"        s[i] -= 32;", PF("%s", "s")), _title,
       "A letter after a space (or at the start) is made a capital."),
    CS(T(r'char s[] = "$w $z $v";', r"for (char *p = s; *p; p++)", r"    if (*p == ' ')", r"        *p = '_';", PF("%s", "s")), lambda p: f"{p['w']}_{p['z']}_{p['v']}",
       "Every space is replaced."),
    CS(T(r"for (int i = 7; i >= 0; i--)", r'    printf("%d", ($u >> i) & 1);', r'printf("\n");'), lambda p: format(p["u"], "08b"),
       "Shift each bit down to the bottom and mask it: the eight bits, from the top."),
]
