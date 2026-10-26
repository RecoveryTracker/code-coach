"""C strings and memory pack, part 3: Buffer Fill and snprintf Says.

Buffer Fill is memset, memcpy and memmove on byte arrays and strings (the bytes are printed as numbers, or as `%02X`).
snprintf Says is snprintf into buffers of a given size: the return value (the length it WOULD have needed), the text that
fits and its strlen. Answers are worked out with `Buf` and `cfmt` (never by a compiler); buffers are always big enough
for what the C writes, and every string is terminated before it is read.
"""

from __future__ import annotations

from ._cstrings_model import PF, T, Buf, CS, cfmt
from ._model import Maker


def _sum(xs: list[int]) -> int:
    return sum(xs)


# ── 5. Buffer Fill ──────────────────────────────────────────────────────

def _ints(p: dict) -> list[int]:
    return [p["a"], p["b"], p["c"], p["d"]]


def _repeat_int(byte: int) -> int:
    return int.from_bytes(bytes([byte] * 4), "big")


def _mask_tail(p: dict) -> str:
    return p["w"][:p["i"]] + "*" * (p["L"] - p["i"])


def _grid(p: dict) -> str:
    rows = [list("..."), list("...")]
    rows[p["r"]][p["q"]] = "#"
    return " ".join("".join(r) for r in rows)


def _shift_right(p: dict) -> str:
    a = _ints(p) + [1]
    a[1:5] = a[0:4]
    return " ".join(map(str, a))


def _shift_left(p: dict) -> str:
    a = _ints(p) + [1]
    a[0:4] = a[1:5]
    return " ".join(map(str, a))


def _copy_two_into_middle(p: dict) -> str:
    b = [0, 0, 0, 0]
    b[1:3] = [p["a"], p["b"]]
    return " ".join(map(str, b))


def _delete_at(p: dict) -> str:
    b = Buf(16, p["w"])
    b.memmove(p["i"], p["i"] + 1, b.strlen() - p["i"])
    return b.text()


def _insert_front(p: dict) -> str:
    b = Buf(16, p["w"])
    b.memmove(1, 0, b.strlen() + 1)
    b.b[0] = ord(p["x"])
    return b.text()


def _rotate(p: dict) -> str:
    a = _ints(p)
    return " ".join(map(str, a[1:] + a[:1]))


def _alphabet(p: dict) -> str:
    return "".join(chr(97 + i) for i in range(p["a"]))


def _hexpair(p: dict) -> str:
    return f"{p['hx']} {p['hx']} 00"


def _bytes_sum(p: dict) -> int:
    return (p["u"] + p["u2"] + p["m"]) % 256


FILLS: list[Maker] = [
    CS(T(r"unsigned char b[6] = {0};", r"memset(b, $u, 3);", PF("%d %d", "b[0], b[3]")), lambda p: f"{p['u']} 0",
       "memset sets the first 3 bytes to the value; the others are still 0."),
    CS(T(r"char b[8];", r"memset(b, '$x', 5);", r"b[5] = 0;", PF("%s", "b")), lambda p: p["x"] * 5,
       "memset wrote five letters and the NUL ended the string."),
    CS(T(r"unsigned char b[4];", r"memset(b, 0, sizeof b);", r"b[$q] = $a;", PF("%d", "b[0] + b[1] + b[2] + b[3]")), lambda p: p["a"],
       "All four bytes were cleared, then one was set."),
    CS(T(r"int a[4] = {$a, $b, $c, $d};", r"memset(a, 0, sizeof a);", PF("%d", "a[0] + a[1] + a[2] + a[3]")), 0,
       "memset to 0 clears every byte of every int."),
    CS(T(r"int a[3];", r"memset(a, $a, sizeof a);", PF("%d", "a[1]")), lambda p: p["a"] * 16843009,
       "memset fills BYTES, not ints: each int becomes the byte four times, so a * 0x01010101."),
    CS(T(r"int a[4] = {$a, $b, $c, $d};", r"memset(a, 0, $k * sizeof a[0]);", PF("%d", "a[0] + a[1] + a[2] + a[3]")),
       lambda p: _sum(_ints(p)[p["k"]:]), "The first k ints are cleared; the rest are left."),
    CS(T(r"int a[4] = {$a, $b, $c, $d};", r"memset(a, 0, sizeof a / 2);", PF("%d", "a[0] + a[1] + a[2] + a[3]")),
       lambda p: p["c"] + p["d"], "Half of the 16 bytes is the first two ints."),
    CS(T(r"int a[4] = {$a, $b, $c, $d}, b[4] = {0};", r"memcpy(b, a, 2 * sizeof(int));", PF("%d %d %d", "b[0], b[1], b[2]")),
       lambda p: f"{p['a']} {p['b']} 0", "Two ints (8 bytes) were copied; b[2] is untouched."),
    CS(T(r"int a[4] = {$a, $b, $c, $d}, b[4] = {0};", r"memcpy(b + 1, a, 2 * sizeof(int));", PF("%d %d %d %d", "b[0], b[1], b[2], b[3]")),
       _copy_two_into_middle, "b + 1 is where the copy lands: the second and third ints."),
    CS(T(r"int a[5] = {$a, $b, $c, $d, 1};", r"memmove(a + 1, a, 4 * sizeof(int));", PF("%d %d %d %d %d", "a[0], a[1], a[2], a[3], a[4]")),
       _shift_right, "The four ints slide one place right (memmove copes with the overlap); a[0] keeps its old value."),
    CS(T(r"int a[5] = {$a, $b, $c, $d, 1};", r"memmove(a, a + 1, 4 * sizeof(int));", PF("%d %d %d %d %d", "a[0], a[1], a[2], a[3], a[4]")),
       _shift_left, "The four ints slide one place left; the last one is not touched."),
    CS(T(r"int a[4] = {$a, $b, $c, $d};", r"int t = a[0];", r"memmove(a, a + 1, 3 * sizeof(int));", r"a[3] = t;",
         PF("%d %d %d %d", "a[0], a[1], a[2], a[3]")), _rotate, "Rotate left: slide three down and put the saved first one at the end."),
    CS(T(r"unsigned char b[3] = {0};", r"memset(b, 0x$hx, 2);", PF("%02X %02X %02X", "b[0], b[1], b[2]")), _hexpair,
       "Two bytes are set; %02X prints each as two capital hex digits."),
    CS(T(r"unsigned char b[2] = {0};", r"b[0] = 0x$hx;", r"b[1] = 0x$hy;", PF("%02X%02X", "b[0], b[1]")), lambda p: p["hx"] + p["hy"],
       "Two bytes, two hex digits each."),
    CS(T(r'char b[$n] = "$w";', r"int z = 0;", r"for (size_t i = 0; i < sizeof b; i++)", r"    if (b[i] == 0)", r"        z++;", PF("%d", "z")),
       lambda p: p["n"] - p["L"], "A string initialiser fills the rest of the array with zeros: n minus the letters."),
    CS(T(r"char b[12] = {'$x', '$y'};", PF("%zu %d", "strlen(b), b[11]")), "2 0", "Two letters were given; every other element is 0."),
    CS(T(r"int a[5] = {$a, $b, [3] = $c};", PF("%d %d", "a[2], a[3]")), lambda p: f"0 {p['c']}",
       "The [3] sets element 3; element 2 was not mentioned, so it is 0."),
    CS(T(r"unsigned char b[3];", r"memset(b, 256 + $a, 3);", PF("%d", "b[1]")), lambda p: p["a"],
       "memset uses the value as an unsigned char: 256 + a wraps to a."),
    CS(T(r"unsigned char b[3];", r"memset(b, -$a, 2);", PF("%d", "b[0]")), lambda p: 256 - p["a"],
       "-a as an unsigned char is 256 - a."),
    CS(T(r"unsigned char b[5];", r"memset(b, $a, 5);", PF("%d", "b[0] + b[1] + b[2] + b[3] + b[4]")), lambda p: 5 * p["a"],
       "Five bytes of the same value."),
    CS(T(r"unsigned char s[4] = {$a, $b, $c, $d}, d[4] = {0};", r"memcpy(d, s, $k);", PF("%d", "d[0] + d[1] + d[2] + d[3]")),
       lambda p: _sum(_ints(p)[:p["k"]]), "Only the first k bytes were copied."),
    CS(T(r"unsigned char a[4], b[4];", r"memset(a, $a, 4);", r"memset(b, $r ? $a : $b, 4);", PF("%d", "memcmp(a, b, 4) == 0")),
       lambda p: p["r"], "Equal when the same byte was used for both."),
    CS(T(r'char s[] = "$w";', r"memmove(s + 1, s, 2);", PF("%s", "s")), lambda p: p["w"][0] + p["w"][0] + p["w"][1] + p["w"][3:],
       "Two bytes slid one place right: the first letter appears twice and the third is overwritten."),
    CS(T(r'char s[16] = "$w";', r"memmove(s + 1, s, strlen(s) + 1);", r"s[0] = '$x';", PF("%s", "s")), _insert_front,
       "Everything, NUL included, moves one place right to make room for a new first letter."),
    CS(T(r'char s[16] = "$w";', r"memmove(s, s + 1, strlen(s));", PF("%s", "s")), lambda p: p["w"][1:],
       "Moving the tail (and its NUL) one place left deletes the first letter."),
    CS(T(r'char s[16] = "$w";', r"memmove(s + $i, s + $i + 1, strlen(s + $i));", PF("%s", "s")), _delete_at,
       "The letters after position i, and the NUL, slide left over it."),
    CS(T(r'char s[] = "$w";', r"memset(s, '-', strlen(s));", PF("%s", "s")), lambda p: "-" * p["L"],
       "Every letter, but not the NUL, was overwritten."),
    CS(T(r'char s[] = "$w";', r"memset(s + $i, '*', $L - $i);", PF("%s", "s")), _mask_tail,
       "From position i to the end of the letters is starred out."),
    CS(T(r'char s[] = "$w";', r"memset(s + 1, '*', strlen(s) - 1);", PF("%s", "s")), lambda p: p["w"][0] + "*" * (p["L"] - 1),
       "All but the first letter."),
    CS(T(r'char s[] = "$w";', r"memset(s, 'x', 3);", PF("%s", "s")), lambda p: "xxx" + p["w"][3:], "Only the first three bytes."),
    CS(T(r"char b[8];", r"memset(b, 'a', 8);", r"b[7] = '\0';", PF("%zu", "strlen(b)")), 7,
       "The array was filled with letters and a NUL put in the last place: seven letters."),
    CS(T(r"char b[10];", r"memset(b, 'x', 10);", r"b[$n % 10] = 0;", PF("%zu", "strlen(b)")), lambda p: p["n"] % 10,
       "The NUL lands at index n % 10, so that many x's come before it."),
    CS(T(r"char g[2][4];", r"memset(g, '.', sizeof g);", r"g[0][3] = 0;", r"g[1][3] = 0;", r"g[$r][$q] = '#';", PF("%s %s", "g[0], g[1]")),
       _grid, "Each row is a 3-character string with a NUL; one dot became a #."),
    CS(T(r"unsigned char b[] = {$u, $u2, $m};", r"unsigned char s = 0;", r"for (int i = 0; i < 3; i++)", r"    s += b[i];", PF("%d", "s")),
       _bytes_sum, "The sum wraps around 256 because it is stored in an unsigned char."),
    CS(T(r"int x = $big;", r"memset(&x, 0, sizeof x);", PF("%d", "x")), 0, "Every byte of x is cleared."),
    CS(T(r"int x;", r"memset(&x, 1, sizeof x);", PF("%d", "x")), 16843009, "All four bytes are 1: 0x01010101."),
    CS(T(r"int a = $big, b = 0;", r"memcpy(&b, &a, sizeof a);", PF("%d", "b")), lambda p: p["big"],
       "All the bytes of a were copied into b."),
    CS(T(r"char b[12];", r"for (int i = 0; i < $a; i++)", r"    b[i] = 'a' + i;", r"b[$a] = 0;", PF("%s", "b")), _alphabet,
       "A loop writes consecutive letters, then the NUL."),
    CS(T(r'char b[16] = "$w";', r'memcpy(b + $L, "$z", $M + 1);', PF("%s", "b")), lambda p: p["w"] + p["z"],
       "Copying the second word and its NUL right after the first joins them."),
    CS(T(r"char b[6] = {'$x'};", PF("%d %c", "b[1], b[0]")), lambda p: f"0 {p['x']}", "Only the first element was given."),
    CS(T(r"char b[5] = {[2] = '$x'};", PF("%d %c %d", "b[0], b[2], b[4]")), lambda p: f"0 {p['x']} 0",
       "The designated initialiser sets index 2; everything else is 0."),
    CS(T(r"int a[3] = {$a, $b, $c};", r"memset(a, 0, sizeof a[0]);", PF("%d %d %d", "a[0], a[1], a[2]")), lambda p: f"0 {p['b']} {p['c']}",
       "sizeof a[0] is one int's bytes, so only the first int is cleared."),
]


# ── 6. snprintf Says ────────────────────────────────────────────────────

def sn(size: int, fmt: str, *args) -> tuple[int, str]:
    """(the return value, the text stored) of snprintf into a buffer of `size` bytes."""
    full = cfmt(fmt, *args)
    return len(full), full[:size - 1] if size > 0 else ""


def _fmt1(size: int, fmt: str, *args) -> str:
    return sn(size, fmt, *args)[1]


SNPRINTF: list[Maker] = [
    CS(T(r"char b[32];", r'int r = snprintf(b, sizeof b, "%s-%d", "$w", $n);', PF("%d %s", "r, b")),
       lambda p: "%d %s" % (sn(32, "%s-%d", p["w"], p["n"])[0], sn(32, "%s-%d", p["w"], p["n"])[1]),
       "The buffer is big enough: r is the length of the text, and b holds all of it."),
    CS(T(r"char b[6];", r'int r = snprintf(b, sizeof b, "%s", "$w$z");', PF("%d %s", "r, b")),
       lambda p: "%d %s" % sn(6, "%s", p["w"] + p["z"]), "r is the length the text WOULD have had; b keeps only 5 letters and the NUL."),
    CS(T(r"char b[5];", r'int r = snprintf(b, sizeof b, "%d", $big);', PF("%d %s", "r, b")),
       lambda p: "%d %s" % sn(5, "%d", p["big"]), "Five digits needed, room for four: r says 5, b holds the first four."),
    CS(T(r"char b[6];", r'int r = snprintf(b, sizeof b, "%s", "$w$z");', PF("%d %zu", "r, strlen(b)")),
       lambda p: "%d 5" % (p["L"] + p["M"]), "A truncated buffer always holds size - 1 letters."),
    CS(T(r"char b[$n];", r'int r = snprintf(b, sizeof b, "%s%s", "$w", "$z");', PF("%d", "(size_t)r >= sizeof b")),
       lambda p: 1 if p["L"] + p["M"] >= p["n"] else 0, "r >= the buffer size is the test for 'it was cut'."),
    CS(PF("%d", 'snprintf(NULL, 0, "%d-%d", $n, $big)'), lambda p: sn(1, "%d-%d", p["n"], p["big"])[0],
       "With size 0 nothing is written: the return value just measures the text."),
    CS(PF("%d", 'snprintf(NULL, 0, "%5d", $a)'), 5, "The width of 5 counts: five characters."),
    CS(PF("%d", 'snprintf(NULL, 0, "%-8s", "$w")'), 8, "Padded out to width 8."),
    CS(T(r'char b[8] = "ab";', r'int r = snprintf(b, 0, "%s", "$w");', PF("%d %s", "r, b")), lambda p: f"{p['L']} ab",
       "Size 0 means b is not touched at all."),
    CS(T(r'char b[8] = "xyz";', r'int r = snprintf(b, 1, "%s", "$w");', PF("%d [%s]", "r, b")), lambda p: f"{p['L']} []",
       "Size 1 only has room for the NUL: b becomes the empty string."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%5d", $a);', PF("|%s|", "b")), lambda p: "|" + _fmt1(16, "%5d", p["a"]) + "|",
       "%5d pads on the left to width 5."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%-5d", $a);', PF("|%s|", "b")), lambda p: "|" + _fmt1(16, "%-5d", p["a"]) + "|",
       "The minus flag pads on the right."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%05d", $big);', PF("|%s|", "b")), lambda p: "|" + _fmt1(16, "%05d", p["big"]) + "|",
       "A 0 flag pads with zeros to the width: five digits already, so nothing to add."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%06d", $n);', PF("|%s|", "b")), lambda p: "|" + _fmt1(16, "%06d", p["n"]) + "|",
       "Zero padding to 6 digits."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%+d", $n);', PF("%s", "b")), lambda p: _fmt1(16, "%+d", p["n"]),
       "The plus flag shows the sign."),
    CS(T(r"char b[16];", r"""snprintf(b, sizeof b, "%c%d%c", '$x', $n, '$y');""", PF("%s", "b")),
       lambda p: f"{p['x']}{p['n']}{p['y']}", "%c prints one character, %d the number."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%5.1f", (double)$n / $h);', PF("|%s|", "b")),
       lambda p: "|" + _fmt1(16, "%5.1f", p["n"] / p["h"]) + "|", "One decimal, in a field 5 wide."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%.2f", (double)$n / $h);', PF("%s", "b")),
       lambda p: _fmt1(16, "%.2f", p["n"] / p["h"]), "Two decimals."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%.3s", "$w");', PF("%s", "b")), lambda p: p["w"][:3],
       "A precision on %s is the most letters printed."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%.*s", $i, "$w");', PF("%s", "b")), lambda p: p["w"][:p["i"]],
       "The * takes the precision from the arguments."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%*d", $b, $a);', PF("|%s|", "b")), lambda p: "|" + _fmt1(16, "%*d", p["b"], p["a"]) + "|",
       "The * takes the width from the arguments."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%d%%", $m);', PF("%s", "b")), lambda p: f"{p['m']}%", "%% prints one percent sign."),
    CS(T(r"char b[32];", r'int n = snprintf(b, sizeof b, "%s", "$w");', r'n += snprintf(b + n, sizeof b - n, "-%d", $n);', PF("%d %s", "n, b")),
       lambda p: "%d %s" % (len(f"{p['w']}-{p['n']}"), f"{p['w']}-{p['n']}"), "The return value says where to append next."),
    CS(T(r"char b[8];", r'int n = snprintf(b, sizeof b, "%s", "$w");', r'snprintf(b + n, sizeof b - n, "%s", "$z");', PF("%s", "b")),
       lambda p: (p["w"] + p["z"])[:7], "The second call only has what is left of the 8 bytes."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%d", $n * $big);', PF("%zu", "strlen(b)")), lambda p: len(str(p["n"] * p["big"])),
       "strlen of the printed number is its count of digits."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%d", $big);', PF("%c", "b[1]")), lambda p: str(p["big"])[1],
       "The number became text; b[1] is its second digit."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%s", "$w");', r"b[0] -= 32;", PF("%s", "b")), lambda p: p["Wc"],
       "The copy is changeable; its first letter becomes a capital."),
    CS(T(r"char b[16];", r"""snprintf(b, sizeof b, "%c", 'a' + $a);""", PF("%s", "b")), lambda p: chr(97 + p["a"]),
       "'a' + a is the code of a later letter, which %c prints."),
    CS(T(r"char b[16];", r"""snprintf(b, sizeof b, "%d", '$x');""", PF("%s", "b")), lambda p: str(ord(p["x"])),
       "A character is a number; %d prints its code."),
    CS(T(r"char b[24];", r'snprintf(b, sizeof b, "%s=%d", "$w", $n);', PF("%s", "b")), lambda p: f"{p['w']}={p['n']}", "Text, an equals sign, a number."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%d:%02d", $n % 12, $b);', PF("%s", "b")), lambda p: _fmt1(16, "%d:%02d", p["n"] % 12, p["b"]),
       "%02d pads the minutes with a zero."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%x", $big);', PF("%s", "b")), lambda p: format(p["big"], "x"), "%x prints lower-case hex."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%#X", $n);', PF("%s", "b")), lambda p: "0X" + format(p["n"], "X"), "# adds the 0X prefix."),
    CS(T(r"char b[16];", r'snprintf(b, sizeof b, "%o", $n);', PF("%s", "b")), lambda p: format(p["n"], "o"), "%o prints in base 8."),
    CS(T(r"char b[$L + 1];", r'int r = snprintf(b, sizeof b, "%s", "$w");', PF("%d %s", "r, b")), lambda p: f"{p['L']} {p['w']}",
       "The word and its NUL fit exactly: nothing is cut."),
    CS(T(r"char b[$L];", r'int r = snprintf(b, sizeof b, "%s", "$w");', PF("%d %s", "r, b")), lambda p: f"{p['L']} {p['w'][:-1]}",
       "One byte short: the last letter is cut but r still says L."),
    CS(T(r"char b[4];", r'snprintf(b, sizeof b, "%s", "$w");', PF("%zu", "strlen(b)")), lambda p: min(p["L"], 3),
       "At most 3 letters fit with the NUL."),
    CS(T(r"char b[8];", r'int r = snprintf(b, sizeof b, "%s", "");', PF("%d %zu", "r, strlen(b)")), "0 0", "Nothing printed: length 0."),
    CS(T(r"char b[32];", r'snprintf(b, sizeof b, "%s %s", "$w", "$z");', PF("%s", "b")), lambda p: f"{p['w']} {p['z']}", "Two words and a space."),
    CS(T(r"char b[32];", r'int r = snprintf(b, sizeof b, "%-8s|", "$w");', PF("%d [%s]", "r, b")),
       lambda p: "%d [%s]" % sn(32, "%-8s|", p["w"]), "Padded to 8 and the bar: 9 characters."),
    CS(T(r"char b[32];", r'snprintf(b, sizeof b, "%-6s%4d", "$w", $n);', PF("[%s]", "b")), lambda p: "[" + _fmt1(32, "%-6s%4d", p["w"], p["n"]) + "]", "A left-aligned name and a right-aligned number: a table row."),
    CS(T(r"char b[16];", r'int r = snprintf(b, sizeof b, "%d", $n);', PF("%c", "b[r - 1]")), lambda p: str(p["n"])[-1],
       "r is the length, so b[r - 1] is the last digit."),
    CS(T(r'char b[24] = "";', r"int n = 0;", r"for (int i = 0; i < $a; i++)", r'    n += snprintf(b + n, sizeof b - n, "%d", i);', PF("%s", "b")),
       lambda p: "".join(str(i) for i in range(p["a"])), "Each call writes where the last one stopped."),
    CS(T(r"char b[32];", r'int r = sprintf(b, "%s%d", "$w", $n);', PF("%d", "r")), lambda p: len(f"{p['w']}{p['n']}"),
       "sprintf, like snprintf, returns the number of characters written."),
    CS(PF("%d", 'snprintf(NULL, 0, "%d", $big)'), lambda p: len(str(p["big"])), "Measuring the digits without writing them."),
]
