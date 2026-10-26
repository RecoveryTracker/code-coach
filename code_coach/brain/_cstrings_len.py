"""C strings and memory pack, part 1: strlen vs sizeof, and Copy & Cat.

Every answer is worked out by hand (`Buf` in `_cstrings_model.py` is `char b[n]` in Python) and held to the real compilers
by tests/c_oracle.py. Prompts are the BODY of `main` unless they define `main`; every buffer is a fixed char array that is
always large enough, set before it is read, and ends in a NUL.
"""

from __future__ import annotations

from ._cstrings_model import PF, T, Buf, CS, Retry
from ._model import Maker

S = r'char s[] = "$w";'

# ── 1. strlen vs sizeof ─────────────────────────────────────────────────

LENGTHS: list[Maker] = [
    CS(T(r'char s[$L + 1] = "$w";', PF("%zu %zu", "strlen(s), sizeof(s)")), lambda p: f"{p['L']} {p['L'] + 1}",
       "The array is exactly as big as the word and its NUL: sizeof counts both, strlen only the letters."),
    CS(T(r'char s[$n] = "$w";', PF("%zu %zu", "strlen(s), sizeof(s)")), lambda p: f"{p['L']} {p['n']}",
       "sizeof is the size you declared; strlen stops at the first NUL after the word."),
    CS(T(r'char s[$n] = "$w";', PF("%zu", "sizeof(s) - strlen(s)")), lambda p: p["n"] - p["L"],
       "The bytes in the array minus the letters used: the room left, including the NUL."),
    CS(T(r'char s[] = "$w$z";', PF("%zu %zu", "strlen(s), sizeof(s)")), lambda p: f"{p['L'] + p['M']} {p['L'] + p['M'] + 1}",
       "One literal, so one NUL: sizeof is the letters plus 1."),
    CS(T(r"char s[] = {'$x', '$y', '\0'};", PF("%zu %zu", "strlen(s), sizeof(s)")), "2 3",
       "Two letters and a NUL written out by hand: strlen sees 2, sizeof sees 3."),
    CS(T(r"char s[] = {'$x', '$y', '$x'};", PF("%zu", "sizeof(s)")), 3,
       "Three characters were listed and no NUL: sizeof counts exactly those three (it is not a string, so no strlen)."),
    CS(T(r'char s[20] = "$w";', r'strcat(s, "$z");', PF("%zu %zu", "strlen(s), sizeof(s)")),
       lambda p: f"{p['L'] + p['M']} 20", "strcat grows the string; the array stays 20 bytes."),
    CS(T(r'char s[16] = "$w";', r"s[$i] = '\0';", PF("%zu %zu", "strlen(s), sizeof(s)")), lambda p: f"{p['i']} 16",
       "A NUL written at position i ends the string there; sizeof does not change."),
    CS(T(r'char s[16] = "$w";', r"s[strlen(s)] = '!';", PF("%zu", "strlen(s)")), lambda p: p["L"] + 1,
       "The '!' replaced the NUL, but the next byte is still the 0 from the initialiser, so the string is one longer."),
    CS(T(r'char s[16] = "$w";', r"s[strlen(s) - 1] = '\0';", PF("%zu", "strlen(s)")), lambda p: p["L"] - 1,
       "Writing a NUL over the last letter chops it off."),
    CS(T(r'char s[16] = "$w";', r"s[0] = '\0';", PF("%zu %zu", "strlen(s), sizeof(s)")), "0 16",
       "A NUL first makes the empty string; the array is still 16 bytes."),
    CS(T(r'char s[16] = "$w";', r"s[$L + 3] = 'x';", PF("%zu", "strlen(s)")), lambda p: p["L"],
       "The 'x' is far past the NUL that ends the word, so strlen never gets there."),
    CS(T(r'char s[16] = "$w";', r"s[$L] = 'x';", r"s[$L + 1] = 'y';", PF("%zu", "strlen(s)")), lambda p: p["L"] + 2,
       "Both writes land on zeros: the NUL is overwritten and the string grows by two."),
    CS(T(S, PF("%zu", "strlen(s + $i)")), lambda p: p["L"] - p["i"],
       "s + i is the string starting i letters in, so it is i letters shorter."),
    CS(PF("%d", 'strlen("$w") - strlen("$z") > 0'), lambda p: 1 if p["L"] != p["M"] else 0,
       "strlen is unsigned: a negative difference wraps to a huge number, so only equal lengths give 0."),
    CS(PF("%d", '(int)strlen("$w") - (int)strlen("$z")'), lambda p: p["L"] - p["M"],
       "Casting to int first lets the difference go negative."),
    CS(T(S, r"int n = 0;", r"while (s[n] != 0)", r"    n++;", PF("%d", "n")), lambda p: p["L"],
       "The loop stops at the NUL, which is the number 0: n counts the letters."),
    CS(T(r"char s[12];", r"memset(s, '$x', $a);", r"s[$a] = 0;", PF("%zu", "strlen(s)")), lambda p: p["a"],
       "memset wrote a letters and the NUL went right after them."),
    CS(T(r'char names[3][8] = {"$w", "$z", "$v"};', PF("%zu %zu %zu", "sizeof(names), sizeof(names[0]), strlen(names[1])")),
       lambda p: f"24 8 {p['M']}", "Three rows of 8 bytes is 24; strlen of a row is its word."),
    CS(T(r'const char *a[] = {"$w", "$z", "$v"};', PF("%zu %zu", "sizeof(a) / sizeof(a[0]), strlen(a[2])")),
       lambda p: f"3 {len(p['v'])}", "The count of pointers is 3 whatever their size is; strlen measures the third word."),
    CS(PF("%d", 'sizeof("$w") - 1 == strlen("$w")'), 1, "A literal's sizeof is its letters plus the NUL."),
    CS(PF("%d", 'sizeof("$w") == strlen("$w")'), 0, "sizeof counts the NUL and strlen does not, so they never match."),
    CS(T(S, PF("%c", "s[sizeof(s) - 2]")), lambda p: p["w"][-1],
       "sizeof(s) - 1 is the NUL, so one before that is the last letter."),
    CS(PF("%zu", 'strlen("$w") + sizeof("$z")'), lambda p: p["L"] + p["M"] + 1,
       "strlen leaves the NUL out and sizeof of a literal counts it."),
    CS(PF("%zu %zu %zu", 'sizeof(char), sizeof(""), strlen("")'), "1 1 0",
       "The empty string is one byte, the NUL, and has no letters."),
    CS(T(r'char t[] = "$w" "$z";', PF("%zu", "sizeof(t)")), lambda p: p["L"] + p["M"] + 1,
       "Neighbouring literals are joined into one string with one NUL."),
    CS(T(r'char s[20] = "";', r'strncpy(s, "$w", $i);', PF("%zu", "strlen(s)")), lambda p: p["i"],
       "strncpy copied i letters into an all-zero array, so the string ends right after them."),
    CS(T(r'char s[16] = "$w";', r"size_t n = strlen(s);", r"s[n] = '-';", r"s[n + 1] = 0;", PF("%zu %zu", "n, strlen(s)")),
       lambda p: f"{p['L']} {p['L'] + 1}", "n was taken before the dash was added; strlen after sees one more."),
    CS(T(r"size_t mylen(const char *s) {", r"    size_t n = 0;", r"    while (s[n])", r"        n++;", r"    return n;", r"}",
         r"int main(void) {", r'    printf("%zu %zu\n", mylen("$w"), mylen(""));', r"}"), lambda p: f"{p['L']} 0",
       "A hand-written strlen counts until the NUL; the empty string has none before it."),
    CS(T(r'char s[] = "$D";', PF("%zu %zu", "strlen(s), sizeof(s)")), lambda p: f"{len(p['D'])} {len(p['D']) + 1}",
       "Digits in quotes are ordinary characters: one byte each, plus the NUL."),
    CS(T(S, r"char *p = s + $i;", PF("%zu %zu", "strlen(p), strlen(s)")), lambda p: f"{p['L'] - p['i']} {p['L']}",
       "p points into the same string i letters in, so it sees a shorter one."),
    CS(T(r'const char *p = "$w";', r"p++;", r"p++;", PF("%zu", "strlen(p)")), lambda p: p["L"] - 2,
       "Each p++ steps past one letter."),
    CS(T(S, PF("%zu", "sizeof(s) / sizeof(s[0])")), lambda p: p["L"] + 1,
       "The elements of a char array are its bytes: the letters and the NUL."),
    CS(T(r'char a[8] = "$w", b[8] = "$z";', PF("%zu %zu", "strlen(a) + strlen(b), sizeof(a) + sizeof(b)")),
       lambda p: f"{p['L'] + p['M']} 16", "The letters add up to the two lengths; the arrays are 8 bytes each."),
    CS(PF("%zu", r'strlen("$w\t$z")'), lambda p: p["L"] + 1 + p["M"],
       r"\t is one character, so it counts once."),
    CS(T(S, r"s[$j] = 0;", PF("%zu %zu", "strlen(s), sizeof(s)")), lambda p: f"{p['j']} {p['L'] + 1}",
       "A NUL at position j gives a string of j letters; sizeof is untouched."),
    CS(T(S, r"int n = 0;", r"for (int i = 0; s[i]; i++)", r"    if (s[i] == '$f')", r"        n++;", PF("%d", "n")),
       lambda p: p["w"].count(p["f"]), "The loop stops at the NUL and counts the matching letters."),
    CS(T(S, r"s[strlen(s) / 2] = '\0';", PF("%s %zu", "s, strlen(s)")), lambda p: f"{p['w'][:p['L'] // 2]} {p['L'] // 2}",
       "strlen(s) / 2 is a whole number of letters; the NUL goes there and the word is cut."),
    CS(T(S, PF("%zu", "strlen(s) * sizeof(s)")), lambda p: p["L"] * (p["L"] + 1), "strlen is L and sizeof is L + 1."),
    CS(T(r'char big[32] = "";', r'strcat(big, "$w");', r'strcat(big, "$z");', r'strcat(big, "$v");', PF("%zu", "strlen(big)")),
       lambda p: p["L"] + p["M"] + len(p["v"]), "Each strcat adds its letters; the NULs in between are overwritten."),
    CS(T(r'size_t n = sizeof("$w") + sizeof("$z");', PF("%zu", "n")), lambda p: p["L"] + p["M"] + 2,
       "Each literal counts its own NUL."),
    CS(T(S, PF("%d", "(int)sizeof(s) - (int)strlen(s)")), 1, "The NUL is always the one byte that sizeof counts and strlen does not."),
    CS(T(r"char s[16];", r'strcpy(s, "$w");', r'strcpy(s, "$z");', PF("%zu", "strlen(s)")), lambda p: p["M"],
       "The second strcpy overwrote the first and put a NUL after its own letters."),
    CS(T(r'char s[16] = "$w";', r'strncat(s, "$z", 2);', PF("%zu", "strlen(s)")), lambda p: p["L"] + min(2, p["M"]),
       "strncat adds at most 2 letters."),
]


# ── 2. Copy & Cat ───────────────────────────────────────────────────────

def _leftover(p: dict) -> int:
    """strcpy of a shorter string leaves the old tail: the byte at index M + 1 (needs M + 1 < L)."""
    b = Buf(16, "")
    b.strcpy(p["w"])
    b.strcpy(p["z"])
    if p["M"] + 1 >= p["L"]:
        raise Retry
    return b.b[p["M"] + 1]


def _safe_copy(p: dict) -> str:
    b = Buf(4, "")
    b.strncpy(p["w"], 3)
    b.b[3] = 0
    return b.text()


def _strncpy_dots(p: dict) -> str:
    b = Buf.filled(8, ".")
    b.b[7] = 0
    b.strncpy(p["w"], p["i"])
    return b.text()


def _strncpy_zero_count(p: dict) -> int:
    b = Buf.filled(8, "~")
    b.strncpy(p["w"], 8)
    return b.count(0)


def _mid_memcpy(p: dict) -> str:
    b = Buf(16, p["z"])
    b.memcpy(p["i"], [ord(c) for c in p["w"][:2]])
    return b.text()


def _copy_from_middle(p: dict) -> str:
    b = Buf(8, "")
    src = [ord(c) for c in p["w"]] + [0]
    b.memcpy(0, src[p["i"]:p["i"] + 2])
    b.b[2] = 0
    return b.text()


def _cat3(p: dict) -> str:
    b = Buf(24, p["w"])
    b.strcat("-")
    b.strcat(p["z"])
    return b.text()


def _strcat_room(p: dict) -> int:
    b = Buf(20, p["w"])
    b.strcat("!")
    return b.size - b.strlen()


def _chop_append(p: dict) -> str:
    b = Buf(p["L"] + 1, p["w"])
    b.strcpy(p["x"], p["i"])
    return b.text()


def _strncat_after_strncpy(p: dict) -> str:
    b = Buf(16, "")
    b.strncpy(p["w"], 3)
    b.strncat(p["z"], 2)
    return b.text()


COPIES: list[Maker] = [
    CS(T(r"char b[20];", r'strcpy(b, "$w");', PF("%s", "b")), lambda p: p["w"], "strcpy copies the letters and the NUL."),
    CS(T(r'char b[20] = "";', r'strcpy(b, "$w");', r'strcpy(b, "$z");', PF("%s", "b")), lambda p: p["z"],
       "The second strcpy starts at the beginning again: it replaces the first, it does not add to it."),
    CS(T(r'char b[20] = "$w";', r'strcat(b, "$z");', PF("%s", "b")), lambda p: p["w"] + p["z"], "strcat adds the second string after the last letter."),
    CS(T(r'char b[20] = "$w";', r'strcat(b, "$z");', PF("%zu", "strlen(b)")), lambda p: p["L"] + p["M"], "The length is both words' letters."),
    CS(T(r'char b[24] = "$w";', r'strcat(b, "-");', r'strcat(b, "$z");', PF("%s", "b")), _cat3, "Each strcat appends after what is already there."),
    CS(T(r'char b[24] = "";', r'strcpy(b, "$w");', r'strcat(b, ", ");', r'strcat(b, "$z");', PF("%s", "b")),
       lambda p: f"{p['w']}, {p['z']}", "Copy the first, then add the separator and the second."),
    CS(T(r'char b[16] = "";', r'strcpy(b, "$w");', r'strcpy(b, "$z");', PF("%d", "b[$M + 1]")), _leftover,
       "The short string's NUL stops a reader, but the old word's later letters are still in the array."),
    CS(T(r'char b[20] = "";', r'strncpy(b, "$w", $i);', PF("%s", "b")), lambda p: p["w"][:p["i"]],
       "strncpy copied only i letters; the zeros already in b end the string."),
    CS(T(r'char b[20];', r'strncpy(b, "$w", $i);', r"b[$i] = '\0';", PF("%s", "b")), lambda p: p["w"][:p["i"]],
       "strncpy does not add a NUL when it cuts a string short, so the code adds one."),
    CS(T(r"char b[8];", r"memset(b, '.', 7);", r"b[7] = 0;", r'strncpy(b, "$w", $i);', PF("%s", "b")), _strncpy_dots,
       "strncpy overwrote i bytes and added no NUL; the dots after them stay until the NUL that was already at 7."),
    CS(T(r"char b[8];", r"memset(b, '~', 7);", r"b[7] = 0;", r'strncpy(b, "$w", 8);', r"int z = 0;", r"for (int i = 0; i < 8; i++)",
         r"    if (b[i] == 0)", r"        z++;", PF("%d", "z")), _strncpy_zero_count,
       "When n is bigger than the string, strncpy pads the rest of the n bytes with zeros: 8 minus the letters."),
    CS(T(r"char b[4] = {0};", r'strncpy(b, "$w", sizeof(b) - 1);', PF("%s", "b")), _safe_copy,
       "The safe-copy idiom: at most sizeof - 1 letters, so the last byte stays 0."),
    CS(T(r'char b[20] = "$z";', r'strncat(b, "$w", $k);', PF("%s", "b")), lambda p: p["z"] + p["w"][:p["k"]],
       "strncat appends at most k letters of the source."),
    CS(T(r'char b[20] = "$z";', r'strncat(b, "$w", 20);', PF("%s", "b")), lambda p: p["z"] + p["w"],
       "The limit is only a maximum; a shorter source is appended whole."),
    CS(T(r'char b[20] = "$z";', r'strncat(b, "$w", 0);', PF("%s", "b")), lambda p: p["z"], "Zero letters are appended: nothing changes."),
    CS(T(r"char b[16] = {0};", r'strncpy(b, "$w", 3);', r'strncat(b, "$z", 2);', PF("%s", "b")), _strncat_after_strncpy,
       "Three letters of the first, then two of the second."),
    CS(T(r"char b[20];", r'memcpy(b, "$w", $L + 1);', PF("%s", "b")), lambda p: p["w"], "memcpy of the letters plus one byte takes the NUL too."),
    CS(T(r"char b[20] = {0};", r'memcpy(b, "$w", $L);', PF("%s %zu", "b, strlen(b)")), lambda p: f"{p['w']} {p['L']}",
       "memcpy copied the letters only; the zeros that were already there end the string."),
    CS(T(r'char b[16] = "$z";', r'memcpy(b + $i, "$w", 2);', PF("%s", "b")), _mid_memcpy,
       "Two bytes of the word overwrite the bytes of b from position i."),
    CS(T(r'char b[8] = "", s[] = "$w";', r'memcpy(b, s + $i, 2);', r"b[2] = 0;", PF("%s", "b")), _copy_from_middle,
       "Two bytes were copied from i letters into the word, then a NUL was put after them."),
    CS(T(r'char b[24] = "$z";', r'memcpy(b + strlen(b), "$w", $L + 1);', PF("%s", "b")), lambda p: p["z"] + p["w"],
       "Copying to the end of b, NUL included, is exactly what strcat does."),
    CS(T(r'char b[16] = "$w";', r"memmove(b + 1, b, $L + 1);", PF("%s", "b")), lambda p: p["w"][0] + p["w"],
       "Everything moved one place right, NUL included, and the first letter is left where it was: it shows twice."),
    CS(T(r'char b[16] = "$w";', r"memmove(b, b + $i, strlen(b + $i) + 1);", PF("%s", "b")), lambda p: p["w"][p["i"]:],
       "memmove copes with the overlap: the tail slides to the front."),
    CS(T(r'char b[20];', r'printf("%s\n", strcpy(b, "$w") + $i);'), lambda p: p["w"][p["i"]:],
       "strcpy returns its destination, so + i skips i letters of what was copied."),
    CS(T(r'char b[20] = "$w";', PF("%zu", "strlen(strcat(b, \"$z\"))")), lambda p: p["L"] + p["M"],
       "strcat returns the destination, which now holds both words."),
    CS(T(r'char a[8] = "$w", b[8];', r"strcpy(b, a);", r"a[0] = '$X';", PF("%s %s", "a, b")), lambda p: f"{p['X']}{p['w'][1:]} {p['w']}",
       "b is a separate copy: changing a does not touch it."),
    CS(T(r'char a[] = "$w";', r"char *p = a;", r"p[0] = '$X';", PF("%s", "a")), lambda p: p["X"] + p["w"][1:],
       "p is only another name for the same array, so the change shows in a."),
    CS(T(r'char b[20] = "$w";', r'strcpy(b + strlen(b), "$z");', PF("%s", "b")), lambda p: p["w"] + p["z"],
       "Copying to the end is the same as concatenating."),
    CS(T(r'char b[] = "$w";', r'strcpy(b + $i, "$x");', PF("%s", "b")), _chop_append,
       "strcpy at position i overwrites the rest of the word, and its NUL ends the string."),
    CS(T(r'char a[8] = "$w", b[8] = "$z", t[8];', r"strcpy(t, a);", r"strcpy(a, b);", r"strcpy(b, t);", PF("%s %s", "a, b")),
       lambda p: f"{p['z']} {p['w']}", "Three copies through t swap the two words."),
    CS(T(r'char b[20];', r'const char *s = "$w";', r"char *d = b;", r"while ((*d++ = *s++))", r"    ;", PF("%s", "b")), lambda p: p["w"],
       "The loop copies each character, and the assignment's value 0 (the NUL) is what ends it."),
    CS(T(r'char b[20] = "";', r'const char *s = "$w";', r"int i = 0;", r"while (s[i] != '\0') {", r"    b[i] = s[i];", r"    i++;", r"}", PF("%s", "b")),
       lambda p: p["w"], "A hand copy of every letter; the zeros already in b serve as the NUL."),
    CS(T(r'char b[20] = "$w";', r'strcat(b, "!");', PF("%zu", "sizeof(b) - strlen(b)")), _strcat_room,
       "The 20 bytes minus the letters in use: what is left including the NUL."),
    CS(T(r'char c[20] = "";', r'char b[10] = "$w";', r"strcpy(c, b);", r"strcat(c, b);", PF("%s", "c")), lambda p: p["w"] * 2,
       "c gets b, then b again."),
    CS(T(r'char b[20] = "$z";', r'strncpy(b, "$w", 0);', PF("%s", "b")), lambda p: p["z"], "Copying zero characters changes nothing."),
    CS(T(r'char b[20] = "";', r'strcat(b, "$w");', r'strcat(b, "$z");', r"b[$L] = '\0';", PF("%s", "b")), lambda p: p["w"],
       "Both were joined, then a NUL at position L cut the string back to the first word."),
    CS(T(r'char b[20] = "$w";', r'strcat(b, "$z");', r"b[strlen(b) - 1] = '\0';", PF("%s", "b")), lambda p: (p["w"] + p["z"])[:-1],
       "The last letter was replaced by a NUL."),
    CS(T(r"char b[8];", r"memset(b, '$x', 3);", r"b[3] = 0;", r'strcat(b, "$y");', PF("%s", "b")), lambda p: p["x"] * 3 + p["y"],
       "Three letters, a NUL, then strcat adds the next after the last letter."),
    CS(T(r"char b[16] = {0};", r'strcpy(b, "$w");', r"b[$j] = '$X';", r'strcat(b, "$x");', PF("%s", "b")),
       lambda p: p["w"][:p["j"]] + p["X"] + p["w"][p["j"] + 1:] + p["x"], "One letter was changed, then a letter was added at the end."),
    CS(T(r'char b[16] = "$w";', r'strncat(b, "$z", 0);', r'strncat(b, "$v", 1);', PF("%s", "b")), lambda p: p["w"] + p["v"][0],
       "The first strncat adds nothing, the second adds one letter."),
    CS(T(r'char b[16] = "";', r'strncat(b, "$w", $i);', r'strncat(b, "$z", $k);', PF("%s", "b")),
       lambda p: p["w"][:p["i"]] + p["z"][:p["k"]], "strncat on an empty string just copies up to n letters, twice."),
    CS(T(r'char b[20] = "";', r'strcpy(b, "$w");', r'strcat(b, "!");', PF("%s", "b")), lambda p: p["w"] + "!",
       "A one-character string is appended after the word."),
]
