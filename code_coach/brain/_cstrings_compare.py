"""C strings and memory pack, part 2: Compare and Find in String.

strcmp, strncmp and memcmp are always shown as their SIGN (-1, 0 or 1): the size of what they return is not portable, only
the sign is. Searches never print an address: they print an OFFSET from the start (a pointer difference cast to int), the
rest of the string, or whether the result is NULL. Every answer is worked out by hand and held to the real compilers by
tests/c_oracle.py.
"""

from __future__ import annotations

from ._cstrings_model import PF, SGN, T, CS, Retry, sgn, strcmp_sign
from ._model import Maker


def SIGN(call: str) -> str:
    """`int r = <call>;` then the sign of r."""
    return T(f"int r = {call};", SGN)


def _cmp_bytes(a: list[int], b: list[int], n: int) -> int:
    a, b = a[:n], b[:n]
    return (a > b) - (a < b)


def _high_byte(p: dict) -> int:
    if p["hxv"] < 0x80:
        raise Retry
    return 1


def _sorted_pair(p: dict) -> str:
    a, b = sorted((p["w"], p["z"]))
    return f"{a} {b}"


def _min3(p: dict) -> str:
    return min(p["w"], p["z"], p["v"])


def _same_diff(p: dict) -> str:
    return "same" if p["r"] else "diff"


def _flip_one(p: dict) -> int:
    w = p["w"]
    return strcmp_sign(w, w[:p["j"]] + p["x"] + w[p["j"] + 1:])


def _starts_with(p: dict) -> int:
    return 1 if p["z"].startswith(p["w"]) else 0


# ── 3. Compare ──────────────────────────────────────────────────────────

COMPARE: list[Maker] = [
    CS(SIGN('strcmp("$w", "$z")'), lambda p: strcmp_sign(p["w"], p["z"]),
       "strcmp looks at the first letters that differ: the one earlier in the alphabet makes the result negative."),
    CS(SIGN('strcmp("$z", "$w")'), lambda p: strcmp_sign(p["z"], p["w"]),
       "Swapping the two strings flips the sign."),
    CS(SIGN('strcmp("$w", "$w")'), 0, "Identical strings compare as 0."),
    CS(SIGN('strcmp("$w", "$w$x")'), -1, "The first string ends (a NUL, 0) where the second still has a letter, so it is smaller."),
    CS(SIGN('strcmp("$w$x", "$w")'), 1, "A longer string with the same start is bigger."),
    CS(SIGN('strncmp("$w", "$z", $k)'), lambda p: strcmp_sign(p["w"][:p["k"]], p["z"][:p["k"]]),
       "strncmp looks at no more than k characters: the rest of the words cannot change the result."),
    CS(SIGN('strncmp("$w$z", "$w$v", $L)'), 0, "The first L characters are the same word in both."),
    CS(SIGN('strncmp("$w", "$z", 1)'), lambda p: strcmp_sign(p["w"][:1], p["z"][:1]),
       "With n = 1 only the first letters count."),
    CS(SIGN('memcmp("$w", "$z", $k)'), lambda p: strcmp_sign(p["w"][:p["k"]], p["z"][:p["k"]]),
       "memcmp compares k bytes one by one; the first difference decides."),
    CS(SIGN('strcmp("$Wc", "$w")'), -1, "Capital letters come before lower-case ones in ASCII, so the capitalised word is smaller."),
    CS(SIGN('strcmp("$w", "$Wc")'), 1, "A lower-case letter is bigger than its capital."),
    CS(SIGN('strcmp("$n", "$a")'), lambda p: strcmp_sign(str(p["n"]), str(p["a"])),
       "Digits in a string compare as characters, not as numbers: only the first digits are looked at first."),
    CS(SIGN('strcmp("", "$w")'), -1, "The empty string is smaller than any other."),
    CS(SIGN('strcmp("$w", "")'), 1, "Any non-empty string is bigger than the empty one."),
    CS(SIGN('strcmp("$w $z", "$w$z")'), -1, "A space (32) is smaller than any letter, so the first string is smaller."),
    CS(SIGN(r'strcmp("\x$hx", "$w")'), _high_byte,
       "strcmp compares the bytes as unsigned, so a byte above 127 is bigger than any letter."),
    CS(T(r'char a[] = "$w";', r"char *p = a;", PF("%d %d", "p == a, strcmp(p, a) == 0")), "1 1",
       "p holds the address of a, so the two are equal as pointers and as strings."),
    CS(T(r'char a[] = "$w", b[] = "$w";', PF("%d %d", "a == b, strcmp(a, b) == 0")), "0 1",
       "== compares the two addresses: they differ. strcmp compares the letters: they match."),
    CS(T(r'char a[] = "$w";', r'const char *p = "$w";', PF("%d %d", "p == a, strcmp(p, a) == 0")), "0 1",
       "p and a are in different places, so == is 0; the letters are the same, so strcmp is 0."),
    CS(PF("%s", 'strcmp("$w", "$z") < 0 ? "$w" : "$z"'), lambda p: min(p["w"], p["z"]),
       "The smaller string, in dictionary order, is picked."),
    CS(T(r'const char *m = "$w";', r'if (strcmp("$z", m) < 0)', r'    m = "$z";', r'if (strcmp("$v", m) < 0)', r'    m = "$v";',
         PF("%s", "m")), _min3, "m is kept as the smallest word seen so far."),
    CS(T(r'const char *a[] = {"$w", "$z", "$w", "$v"};', r"int n = 0;", r"for (int i = 0; i < 4; i++)", r'    if (strcmp(a[i], "$w") == 0)',
         r"        n++;", PF("%d", "n")), 2, "The word appears twice in the list; strcmp finds each."),
    CS(T(r'char a[] = "$w", b[] = "$w";', r"b[$j] = '$x';", r"int r = strcmp(a, b);", SGN), _flip_one,
       "Only position j differs now (or nothing, if the letter was already there)."),
    CS(T(r'char a[] = "$w", b[] = "$w";', r"a[$i] = 0;", r"int r = strcmp(a, b);", SGN), -1,
       "a now ends early, so it is a shorter prefix of b: smaller."),
    CS(T(r'char a[10] = "$w", b[10] = "$w";', PF("%d %d", "memcmp(a, b, 10) == 0, strcmp(a, b) == 0")), "1 1",
       "Both arrays hold the same word and the same zeros after it."),
    CS(T(r'char a[10] = "$w", b[10] = "$w";', r"b[9] = 'x';", PF("%d %d", "memcmp(a, b, 10) == 0, strcmp(a, b) == 0")), "0 1",
       "memcmp looks at all 10 bytes and sees the 'x'; strcmp stops at the NUL after the word."),
    CS(PF("%s", 'strcmp("$w", $r ? "$w" : "$z") ? "diff" : "same"'), _same_diff,
       "strcmp gives 0 for equal strings, which is false, so the other branch is taken."),
    CS(PF("%d", '!strcmp("$w", "$w")'), 1, "! of 0 is 1: equal strings."),
    CS(PF("%d", '!strcmp("$w", "$z")'), 0, "The words differ, so strcmp is not 0 and ! of it is 0."),
    CS(PF("%d", '(strcmp("$w", "$z") < 0) == (strcmp("$z", "$w") > 0)'), 1,
       "If a is below b then b is above a, whichever way round they are asked."),
    CS(PF("%d %d", 'strcmp("$w", "$z") < 0, strlen("$w") < strlen("$z")'),
       lambda p: f"{1 if strcmp_sign(p['w'], p['z']) < 0 else 0} {1 if p['L'] < p['M'] else 0}",
       "Dictionary order and length are different questions: the first looks at letters, the second at counting."),
    CS(PF("%d", 'strncmp("$w$z", "$w", strlen("$w")) == 0'), 1, "The combined string starts with the word, so the first strlen letters match."),
    CS(PF("%d", 'strncmp("$z$w", "$w", strlen("$w")) == 0'), _starts_with,
       "A starts-with test: only the first strlen(prefix) characters are compared."),
    CS(T(r'const char *a[] = {"$w", "$z", "$v"};', r"int i = 0;", r'while (strcmp(a[i], "$z") != 0)', r"    i++;", PF("%d", "i")), 1,
       "The loop walks the list until strcmp finds the match: index 1."),
    CS(T(r'const char *a[] = {"$w", "$z", "$v"};', r"int i = 0;", r'while (strcmp(a[i], a[$q]) != 0)', r"    i++;", PF("%d", "i")),
       lambda p: p["q"], "The loop stops at the element equal to a[q]: all three words differ, so it is q itself."),
    CS(T(r'char a[] = "$w", b[] = "$w";', r"b[0] -= 32;", r"int r = strcmp(a, b);", SGN), 1,
       "b now starts with a capital, which sorts before the lower-case a: so a is bigger."),
    CS(T(r"unsigned char a[] = {$a, $b, $c}, b[] = {$a, $d, $c};", r"int r = memcmp(a, b, 3);", SGN),
       lambda p: sgn(p["b"] - p["d"]), "The first byte that differs decides: the second one."),
    CS(T(r"unsigned char a[] = {$a, $b, $c}, b[] = {$a, $d, $c};", r"int r = memcmp(a, b, $k);", SGN),
       lambda p: _cmp_bytes([p["a"], p["b"], p["c"]], [p["a"], p["d"], p["c"]], p["k"]),
       "Only the first k bytes are compared; the difference is in the second byte."),
    CS(T(r"unsigned char a[] = {$u}, b[] = {$a};", r"int r = memcmp(a, b, 1);", SGN), 1,
       "memcmp compares unsigned bytes: a number over 200 is bigger than a single digit."),
    CS(SIGN('memcmp("$w", "$z", 0)'), 0, "Comparing no bytes at all gives 0."),
    CS(SIGN('strncmp("$w", "$z", 0)'), 0, "Comparing no characters at all gives 0."),
    CS(T(r'const char *a = "$w";', r"int r = strcmp(a, a + $i);", SGN), lambda p: strcmp_sign(p["w"], p["w"][p["i"]:]),
       "a + i is the same word without its first i letters: compare the two."),
    CS(T(r'char a[16] = "$w", b[16] = "$w";', r'strcat(a, "$x");',r"int r = strcmp(a, b);", SGN), 1,
       "a is b plus one more letter: it is the longer, so the bigger."),
    CS(T(r'const char *a = "$w", *b = "$z";', r"if (strcmp(a, b) > 0) {", r"    const char *t = a;", r"    a = b;", r"    b = t;", r"}",
         PF("%s %s", "a, b")), _sorted_pair, "After the swap, a is the one that comes first in the dictionary."),
    CS(SIGN('strcmp("$D", "$n")'), lambda p: strcmp_sign(p["D"], str(p["n"])),
       "Digits are compared character by character, never as a number."),
]


# ── 4. Find in String ───────────────────────────────────────────────────

S = r'const char *s = "$w";'


def _first_or(p: dict) -> int:
    return p["w"].find(p["x"])


def _strstr_rest(p: dict) -> str:
    s = p["w"] + p["z"]
    return s[s.find(p["z"]):]


def _tail_after_sub(p: dict) -> str:
    return "[" + p["w"][p["w"].find(p["sub"]) + 2:] + "]"


def _spn(s: str, chars: str) -> int:
    n = 0
    while n < len(s) and s[n] in chars:
        n += 1
    return n


def _cspn(s: str, chars: str) -> int:
    n = 0
    while n < len(s) and s[n] not in chars:
        n += 1
    return n


def _count_overlap(s: str, sub: str) -> int:
    return sum(1 for i in range(len(s)) if s.startswith(sub, i))


def _find_from(p: dict) -> int:
    k = p["w"].find(p["f"], p["i"])
    if k < 0:
        raise Retry
    return k


def _cut_at_first(p: dict) -> str:
    return "[" + p["w"][:p["w"].index(p["f"])] + "]"


def _replace_first(p: dict) -> str:
    k = p["w"].index(p["f"])
    return p["w"][:k] + p["X"] + p["w"][k + 1:]


def _after_last(p: dict) -> str:
    return "[" + p["w"][p["w"].rindex(p["f"]) + 1:] + "]"


def _tokens(s: str, delims: str) -> list[str]:
    out, cur = [], ""
    for ch in s:
        if ch in delims:
            if cur:
                out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


FIND: list[Maker] = [
    CS(T(S, r"const char *p = strchr(s, '$x');", PF("%d", "p ? (int)(p - s) : -1")), lambda p: _first_or(p),
       "strchr gives NULL when the letter is missing; otherwise p - s is how far in it was found."),
    CS(T(S, PF("%d", "(int)(strrchr(s, '$f') - s)")), lambda p: p["w"].rindex(p["f"]),
       "strrchr finds the LAST occurrence: the position of the final one."),
    CS(T(S, PF("%d", r"(int)(strchr(s, '\0') - s)")), lambda p: p["L"],
       "The terminating NUL counts as part of the string, so strchr can find it: its position is the length."),
    CS(PF("%d", """strrchr("$w", '$x') == NULL"""), lambda p: 0 if p["x"] in p["w"] else 1,
       "NULL means the letter is not in the string at all."),
    CS(T(S, PF("%d", "strchr(s, '$f') == strrchr(s, '$f')")), lambda p: 1 if p["w"].count(p["f"]) == 1 else 0,
       "The first and last occurrence are the same place only when the letter appears once."),
    CS(T(S, PF("%d", "(int)(strrchr(s, '$f') - strchr(s, '$f'))")), lambda p: p["w"].rindex(p["f"]) - p["w"].index(p["f"]),
       "Last position minus first position: how far apart the first and last are."),
    CS(T(S, PF("%zu", "strlen(strchr(s, '$f'))")), lambda p: p["L"] - p["w"].index(p["f"]),
       "strchr points at the first occurrence; strlen of that is the letters from there to the end."),
    CS(T(r'const char *s = "$w$z";', PF("%s", 'strstr(s, "$z")')), _strstr_rest,
       "strstr finds the first place the second string appears and returns the rest from there."),
    CS(T(S, PF("%d", '(int)(strstr(s, "$sub") - s)')), lambda p: p["w"].find(p["sub"]),
       "The offset where the two-letter piece first appears."),
    CS(PF("%d", 'strstr("$w", $r ? "$sub" : "$z") != NULL'), lambda p: 1 if (p["sub"] if p["r"] else p["z"]) in p["w"] else 0,
       "A non-NULL result means the piece was found inside the word."),
    CS(T(S, PF("%d", 'strstr(s, "") == s')), 1, "The empty string is found at the very start of any string."),
    CS(T(S, PF("%s", 'strstr(s, "$sub")')), lambda p: p["w"][p["w"].find(p["sub"]):],
       "strstr returns the string starting at the match."),
    CS(T(S, PF("[%s]", 'strstr(s, "$sub") + 2')), _tail_after_sub,
       "Starting at the match and stepping over its two letters leaves what follows."),
    CS(PF("%zu", 'strspn("$D$w", "0123456789")'), lambda p: len(p["D"]),
       "strspn counts the leading characters that are all in the set: the digits."),
    CS(PF("%zu", 'strcspn("$w$z", "$x")'), lambda p: _cspn(p["w"] + p["z"], p["x"]),
       "strcspn counts the characters before the first one that IS in the set (all of them if none is)."),
    CS(PF("%zu", 'strcspn("$w", "aeiou")'), lambda p: _cspn(p["w"], "aeiou"), "The letters before the first vowel."),
    CS(T(S, PF("%d", '(int)(strpbrk(s, "aeiou") - s)')), lambda p: _cspn(p["w"], "aeiou"),
       "strpbrk finds the first character that is any of the set: here the first vowel."),
    CS(T(S, PF("%c", 'strpbrk(s, "aeiou")[0]')), lambda p: p["w"][_cspn(p["w"], "aeiou")],
       "The first vowel itself."),
    CS(PF("%zu", 'strspn("$w", "$w")'), lambda p: p["L"], "Every letter of the word is in the set, so the whole word is counted."),
    CS(PF("%zu", 'strspn("$w", "$x$y")'), lambda p: _spn(p["w"], p["x"] + p["y"]),
       "How many letters at the start are one of the two."),
    CS(PF("%zu", r'strcspn("$w\n", "\n")'), lambda p: p["L"],
       "The classic way to cut the newline off: the length before the first newline."),
    CS(PF("%zu", 'strcspn("$w", "")'), lambda p: p["L"], "Nothing is in the empty set, so nothing stops the count."),
    CS(T(S, r"int n = 0;", r"for (const char *p = strchr(s, '$f'); p; p = strchr(p + 1, '$f'))", r"    n++;", PF("%d", "n")),
       lambda p: p["w"].count(p["f"]), "Each pass looks again just after the last find; the count is how many there are."),
    CS(T(r'char s[] = "$w";', r"*strchr(s, '$f') = '\0';", PF("[%s]", "s")), _cut_at_first,
       "The first occurrence is overwritten by a NUL, which cuts the string there."),
    CS(T(r'char s[] = "$w";', r"char *p = strchr(s, '$f');", r"*p = '$X';", PF("%s", "s")), _replace_first,
       "Only the first occurrence of the letter is changed."),
    CS(PF("%s", 'strrchr("$w.$e", \'.\') + 1'), lambda p: p["e"], "strrchr finds the last dot; one past it is the extension."),
    CS(T(r'char s[] = "$w.$e";', r"*strrchr(s, '.') = '\0';", PF("%s", "s")), lambda p: p["w"],
       "The last dot becomes a NUL, which leaves the base name."),
    CS(PF("%s", 'strchr("$w $z $v", \' \') + 1'), lambda p: f"{p['z']} {p['v']}", "The first space found; one past it is the rest of the sentence."),
    CS(PF("%s", 'strrchr("$w $z $v", \' \') + 1'), lambda p: p["v"], "The last space found; one past it is the last word."),
    CS(T(r'const char *s = "$w $z";', PF("%d", "(int)(strchr(s, ' ') - s)")), lambda p: p["L"],
       "The space comes right after the first word."),
    CS(T(S, r"const char *p = memchr(s, '$f', $L);", PF("%d", "(int)(p - s)")), lambda p: p["w"].index(p["f"]),
       "memchr searches a given number of bytes; the offset is where the letter first is."),
    CS(T(S, PF("%d", "memchr(s, '$f', $i) == NULL")), lambda p: 1 if p["f"] not in p["w"][:p["i"]] else 0,
       "memchr looks at only the first i bytes: NULL if the letter is not among them."),
    CS(T(r'char s[] = "$w,$z,$v";', PF("%s", 'strtok(s, ",")')), lambda p: p["w"], "strtok returns the first piece before a comma."),
    CS(T(r'char s[] = "$w,$z,$v";', r'strtok(s, ",");', PF("%s", 'strtok(NULL, ",")')), lambda p: p["z"],
       "The second call carries on where the first stopped."),
    CS(T(r'char s[] = "$w,,$z,$v";', r"int n = 0;", r'for (char *t = strtok(s, ","); t; t = strtok(NULL, ","))', r"    n++;", PF("%d", "n")), 3,
       "strtok skips empty pieces: there are three words."),
    CS(T(r'char s[] = "$w $z $v";', r"int n = 0;", r'for (char *t = strtok(s, " "); t; t = strtok(NULL, " "))', r"    n += strlen(t);", PF("%d", "n")),
       lambda p: p["L"] + p["M"] + len(p["v"]), "The pieces are the three words, so their lengths add to the letters without the spaces."),
    CS(T(r'char s[] = "$w, $z";', r'strtok(s, ", ");', PF("%s", 'strtok(NULL, ", ")')), lambda p: p["z"],
       "Both a comma and a space separate pieces, so the second piece is the second word."),
    CS(T(r'char s[] = "$w $z";', r'strtok(s, " ");', PF("%s", "s")), lambda p: p["w"],
       "strtok wrote a NUL over the space, so the array now holds only the first word."),
    CS(PF("%s", 'strchr("$w:$z", \':\') + 1'), lambda p: p["z"], "One past the colon is the value."),
    CS(T(S, PF("%d", "(int)(strchr(s + $i, '$f') - s)")), _find_from,
       "Searching from position i reports the first match at or after it, still counted from the start."),
    CS(T(r'const char *s = "$w$z$w";', r"int n = 0;", r'for (const char *p = strstr(s, "$w"); p; p = strstr(p + 1, "$w"))', r"    n++;", PF("%d", "n")),
       lambda p: _count_overlap(p["w"] + p["z"] + p["w"], p["w"]), "The loop counts every place the word starts."),
    CS(T(S, PF("[%s]", "strrchr(s, '$f') + 1")), _after_last, "What follows the last occurrence (nothing, if it is the last letter)."),
    CS(T(S, PF("%zu", "strlen(strrchr(s, '$f'))")), lambda p: p["L"] - p["w"].rindex(p["f"]),
       "From the last occurrence to the end."),
    CS(PF("%d", """strchr("aeiou", '$f') != NULL"""), lambda p: 1 if p["f"] in "aeiou" else 0, "Searching a small set for the letter: a vowel test."),
    CS(PF("%d", r"""strchr("aeiou", '\0') != NULL"""), 1, "The NUL at the end of a string can be found too: a trap in vowel tests."),
    CS(T(S, r"int n = 0;", r"for (int i = 0; s[i]; i++)", r'    if (strchr("aeiou", s[i]))', r"        n++;", PF("%d", "n")),
       lambda p: sum(1 for c in p["w"] if c in "aeiou"), "Each letter is looked up in the vowel string; the count is the vowels."),
    CS(PF("%d", 'strpbrk("$w", "xyz") == NULL'), lambda p: 0 if any(c in "xyz" for c in p["w"]) else 1,
       "NULL when none of the letters is in the word."),
]
