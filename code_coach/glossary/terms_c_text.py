"""C words, part 2: printing and text - printf and its format specifiers, escape sequences, strings as char arrays
with a terminator, the string.h functions, ctype and number parsing, and the buffer overflow.

Examples are the BODY of `main` unless they mention `main(` (then a complete program that may #include more); see
terms_c_core.py. C text is raw (r"...") because C is full of backslashes."""

from __future__ import annotations

from .entry import Entry, c

TERMS: list[Entry] = [
    *c(
        "printf",
        "printf",
        "The function that prints formatted text: printf(\"%d items\\n\", n). Its first argument is the format string; each % in it is replaced by the next argument.",
        see=("format-specifier", "padding", "precision", "escape-sequence", "puts"),
        priority=40,
        aka=("print", "printing", "output", "stdout", "fprintf", "print formatted", "format string", "stdio", "stdio.h", "console output"),
        detect=(r"\bprintf\b|\bfprintf\b",),
        rules=(
            r"printf does not add a newline: end the text with \n.",
            r"Each % conversion must match its argument's type; a wrong one is undefined behaviour, not an error message.",
            r"%% prints a percent sign. printf returns how many characters it printed.",
            r"Arguments of type char and short arrive as int, and float arrives as double, so %d, %c and %f cover them.",
        ),
        example=r"""
            int n = 3;
            printf("%d items, %s\n", n, "ok");
            printf("100%%\n");
            int len = printf("abc");
            printf(" -> %d\n", len);
        """,
        out=r"""3 items, ok
100%
abc -> 3""",
    ),
    *c(
        "format-specifier",
        "Format specifier",
        "The %-code inside a printf format string that says how to show the next argument: %d for an int, %u unsigned, %c a character, %s a string, %f a double, %x in hex.",
        see=("printf", "padding", "precision", "size-t", "hexadecimal"),
        priority=55,
        aka=("format specifiers", "conversion specifier", "format code", "%d", "%s", "%c", "%f", "%u", "%lld", "%ld", "conversion", "format character", "placeholder", "%i", "%e", "%g", "%p"),
        detect=(r"raw:%[-+ #0]*(?:\d+|\*)?(?:\.\d+)?(?:hh|h|ll|l|z|j|t|L)?[diuoxXfFeEgGcsp]",),
        rules=(
            r"%d int, %u unsigned int, %ld long, %lld long long, %zu size_t, %x or %X hex, %o octal, %c char, %s string, %f double, %e or %g double, %p pointer, %% a percent sign.",
            r"The specifier must match the argument: %d with a double, or %f with an int, is undefined behaviour (it prints garbage).",
            r"%c with the int 66 prints B and %d with 'B' prints 66: a char is just a small number.",
            r"%s needs a pointer to a string that ends in '\0'.",
        ),
        example=r"""
            printf("%d|%u|%c|%s|%f|%x\n", -5, 7u, 'A', "hi", 2.5, 255);
            printf("%c %d\n", 66, 'B');
            printf("%ld %zu\n", 123456789L, sizeof(int));
        """,
        out=r"""-5|7|A|hi|2.500000|ff
B 66
123456789 4""",
    ),
    *c(
        "padding",
        "Width and padding",
        "A number between % and the letter sets the minimum width of a printf field: %5d pads on the left to 5 characters, %-5d pads on the right, %05d fills with zeros.",
        see=("precision", "format-specifier", "printf", "hexadecimal", "struct-padding"),
        priority=45,
        aka=("width", "field width", "pad", "padded", "zero padding", "zero-padding", "left align", "right align", "justify", "%5d", "%-5d", "%05d", "flags", "printf padding", "fill"),
        detect=(r"raw:%[-+ #0]+\d+[dixXuscf]|raw:%\d+[dixXuscf]|raw:%\*d",),
        rules=(
            r"Width is a MINIMUM: %3d with 12345 still prints all five digits.",
            r"Flags go first: - left-aligns, 0 pads with zeros (numbers only), + always shows the sign, a space leaves room for a sign.",
            r'''%*d takes the width from the argument list: printf("%*d", 4, 9) prints 4 columns.''',
            r"%08.3f: zero-padded, 8 wide, 3 decimals.",
            r"In a struct, padding means something else: unused bytes between members (see struct padding).",
        ),
        example=r"""
            printf("[%5d][%-5d][%05d]\n", 42, 42, 42);
            printf("[%8.3f][%+d][%*d]\n", 3.14159, 7, 4, 9);
            printf("[%3d]\n", 12345);
        """,
        out=r"""[   42][42   ][00042]
[   3.142][+7][   9]
[12345]""",
    ),
    *c(
        "precision",
        "Precision",
        "The .N part of a printf specifier. For %f it is the number of digits after the decimal point (rounded); for %s the most characters to print; for integers the least digits.",
        see=("padding", "format-specifier", "floating-point", "printf"),
        priority=45,
        aka=("decimal places", "decimals", "rounding", "round", "%.2f", "%.1f", "digits after the point", "number of decimals", "significant digits"),
        detect=(r"raw:%[-+ #0]*\d*\.\d+[fFeEgGsdi]|raw:%\.\*[fs]",),
        rules=(
            r"%.2f rounds to two decimals: 3.14159 prints 3.14; the default is six (%f prints 2.500000).",
            r"%.3s prints at most three characters of a string; %.5d pads an integer to at least 5 digits.",
            r"Beware exact halves like 2.5 and 0.125: the rounding direction is not the same on every library.",
        ),
        example=r"""
            printf("%.2f %.1f\n", 3.14159, 2.96);
            printf("%.3s|%.5d\n", "abcdef", 42);
        """,
        out=r"""3.14 3.0
abc|00042""",
    ),
    *c(
        "escape-sequence",
        "Escape sequence",
        "A backslash plus a letter inside a string or character that stands for one special character: \\n newline, \\t tab, \\\\ a backslash, \\\" a quote, \\0 the zero byte.",
        see=("character", "string-literal", "null-terminator", "octal"),
        priority=45,
        aka=("escape", "escape character", "escape sequences", "backslash", "newline", "\\n", "\\t", "\\0", "tab", "special character", "backslash escape"),
        detect=(r"raw:\\[ntr0\\\"'abfv]|raw:\\x[0-9a-fA-F]|raw:\\[0-7]{1,3}",),
        rules=(
            r"\n is a newline (code 10), \t a tab (9), \0 the character with code 0, \\ one backslash, \" a double quote, \' a single quote.",
            r"\x41 and \101 are 'A' written in hex and octal; a hex escape swallows every hex digit after it, so use string joining to stop it.",
            r'''The escape is ONE character in the string: sizeof "a\n" is 3 (a, newline, terminator).''',
        ),
        example=r"""
            printf("a\\b\n");
            printf("say \"hi\"\n");
            printf("%d %d %d\n", '\n', '\0', '\t');
            printf("\x41\101\n");
        """,
        out=r"""a\b
say "hi"
10 0 9
AA""",
    ),
    *c(
        "string",
        "String",
        "In C a string is an array of char that ends with a zero byte, '\\0'. There is no string type: \"hi\" takes 3 bytes, h, i and the terminator.",
        see=("null-terminator", "string-length", "string-literal", "strcpy", "strcmp"),
        priority=40,
        aka=("strings", "char array", "char *", "c string", "cstring", "string type", "text", "char pointer", "string handling", "string.h", "string functions"),
        detect=(r"\bchar[ \t]+\**[A-Za-z_]\w*[ \t]*\[|\bchar[ \t]*\*|<string\.h>",),
        rules=(
            r'char s[] = "hi"; makes a changeable copy (3 bytes). const char *p = "hi"; points at the literal itself, which must not be changed.',
            r"== compares addresses, not text; use strcmp. s1 = s2 on arrays is an error; copy with strcpy or memcpy.",
            r"A string does not know its length: functions walk until they find the '\0'.",
            r"Most helpers live in <string.h>: strlen, strcpy, strcmp, strcat, strchr, strstr.",
        ),
        example=r"""
            char s[] = "hi";
            s[0] = 'H';
            printf("%s %d %d\n", s, (int)sizeof s, (int)strlen(s));
            const char *p = "hi";
            printf("%c %d\n", p[1], p[2]);
        """,
        out=r"""Hi 3 2
i 0""",
    ),
    *c(
        "string-literal",
        "String literal",
        "Text in double quotes in the source, such as \"hello\". It is a char array including the terminator, kept in read-only memory. Two literals side by side join into one.",
        see=("string", "escape-sequence", "null-terminator", "array-decay"),
        priority=35,
        aka=("string constant", "literal string", "concatenation", "string concatenation", "adjacent strings", "string joining", "quoted string", "double quotes"),
        detect=(r"\"\"[ \t\n]*\"\"",),
        rules=(
            r'Neighbouring literals are joined at compile time: "ab" "cd" is "abcd", even across lines (handy for long messages and macros).',
            r'sizeof "abc" is 4 (three letters and the terminator).',
            r"Changing a literal's characters is undefined behaviour: copy it into a char array first, or declare the pointer const char *.",
            r"The literal behaves like a pointer to its first char in most expressions.",
        ),
        example=r"""
            const char *s = "ab" "cd";
            printf("%s %d\n", s, (int)sizeof("abc"));
            printf("one "
                   "two\n");
        """,
        out=r"""abcd 4
one two""",
    ),
    *c(
        "null-terminator",
        "Null terminator",
        "The zero byte '\\0' that marks the end of a string. Every string function walks until it finds it, so a string of n characters needs n + 1 bytes.",
        see=("string", "string-length", "buffer-overflow", "strncpy"),
        priority=45,
        aka=("nul", "null character", "nul terminator", "null byte", "terminator", "end of string", "\\0", "zero byte", "null-terminated", "nul byte", "null terminated string"),
        detect=(r"'\\0'",),
        rules=(
            r'''strlen does not count the terminator; sizeof does: for "abc" they give 3 and 4.''',
            r"Putting a '\0' in the middle ends the string there for every function: s[2] = '\0'; shortens it to two characters.",
            r"A missing terminator is the classic bug: printing or copying runs on into whatever memory follows.",
            r"'\0' is the number 0, so while (*s) stops at it.",
        ),
        example=r"""
            char s[] = "hello";
            s[2] = '\0';
            printf("%s %d %d\n", s, (int)strlen(s), (int)sizeof s);
            printf("%c\n", s[3]);
        """,
        out=r"""he 2 6
l""",
    ),
    *c(
        "string-length",
        "String length",
        "strlen(s) counts the characters before the first '\\0' (it walks the string). sizeof on an array counts every byte, terminator and unused space included.",
        see=("sizeof", "null-terminator", "size-t", "string"),
        priority=50,
        aka=("strlen", "length", "len", "size of string", "string size", "length of a string", "count characters"),
        detect=(r"\bstrlen\b",),
        rules=(
            r'strlen("abc") is 3 but sizeof("abc") is 4. For char buf[20] = "hi", strlen is 2 and sizeof is 20.',
            r"sizeof a char pointer is the size of the pointer (usually 8), not the length of the text it points to.",
            r"strlen returns size_t (unsigned); it is slow on long strings, so do not call it in a loop condition.",
        ),
        example=r"""
            char buf[20] = "hi";
            const char *p = buf;
            printf("%d %d %d\n", (int)strlen(buf), (int)sizeof buf, (int)(sizeof p == sizeof(void *)));
            printf("%d %d\n", (int)strlen("abc"), (int)sizeof("abc"));
        """,
        out=r"""2 20 1
3 4""",
    ),
    *c(
        "strcpy",
        "strcpy",
        "strcpy(dest, src) copies the string src, terminator included, into dest. It does not check that dest is big enough.",
        see=("strncpy", "buffer-overflow", "snprintf", "memcpy"),
        priority=60,
        aka=("string copy", "copy a string", "copy string", "strcpy_s", "strlcpy"),
        detect=(r"\bstrcpy\b",),
        rules=(
            r"dest needs strlen(src) + 1 bytes; too small is a buffer overflow (undefined behaviour).",
            r"It returns dest. The two areas must not overlap.",
            r'''You cannot copy a string with = into an array: s = "x" is an error; use strcpy.''',
            r'''Prefer snprintf(dest, sizeof dest, "%s", src) when the size is not certain.''',
        ),
        example=r"""
            char dst[6];
            strcpy(dst, "hello");
            printf("%s %d\n", dst, (int)strlen(dst));
        """,
        out=r"hello 5",
    ),
    *c(
        "strncpy",
        "strncpy",
        "strncpy(dest, src, n) copies at most n characters. If src has n characters or more, dest gets NO terminator; if it has fewer, the rest of the n bytes are filled with zeros.",
        see=("strcpy", "null-terminator", "snprintf", "buffer-overflow"),
        priority=60,
        aka=("bounded copy", "limited copy", "safe copy"),
        detect=(r"\bstrncpy\b",),
        rules=(
            r"It is not a safe strcpy: after strncpy(d, s, n) set d[n - 1] = '\0' yourself.",
            r"A short source is padded with zeros up to n bytes (slow for big buffers).",
            r"n is a byte count for the destination, not the source.",
        ),
        example=r"""
            char dst[4];
            strncpy(dst, "abcdef", 3);
            dst[3] = '\0';
            printf("%s\n", dst);
            char tiny[5] = "xxxx";
            strncpy(tiny, "ab", 4);
            printf("%d %d %d\n", tiny[1], tiny[2], tiny[3]);
        """,
        out=r"""abc
98 0 0""",
    ),
    *c(
        "strcat",
        "strcat",
        "strcat(dest, src) appends the string src to the end of dest, overwriting dest's terminator. dest must already hold a string and have room for both texts and the terminator.",
        see=("strcpy", "buffer-overflow", "snprintf", "string-length"),
        priority=60,
        aka=("string concatenation", "append string", "concatenate", "concat", "join strings", "strncat"),
        detect=(r"\bstrn?cat\b",),
        rules=(
            r"dest must be a valid string already (an uninitialised array is not).",
            r"Room needed: strlen(dest) + strlen(src) + 1 bytes; otherwise it overflows.",
            r"It walks dest each time, so building a long string with many strcat calls is slow (quadratic).",
            r"It returns dest.",
        ),
        example=r"""
            char s[16] = "foo";
            strcat(s, "bar");
            strcat(s, "!");
            printf("%s %d\n", s, (int)strlen(s));
        """,
        out=r"foobar! 7",
    ),
    *c(
        "strcmp",
        "strcmp",
        "strcmp(a, b) compares two strings character by character. It returns 0 if they are equal, a negative number if a comes first and a positive number if a comes later. Only the sign is promised, not the size.",
        see=("comparison", "string", "memcmp", "ascii"),
        priority=60,
        aka=("string comparison", "compare strings", "strncmp", "string compare", "strcasecmp", "compare two strings", "lexicographic", "lexicographic order", "alphabetical order"),
        detect=(r"\bstrn?cmp\b",),
        rules=(
            r"Test equality with strcmp(a, b) == 0 (or !strcmp(a, b)); never with == , which compares addresses.",
            r"Do not compare the result with -1 or 1: libraries return other negative and positive numbers.",
            r'''It compares character codes, so it is case-sensitive and 'Z' (90) comes before 'a' (97): "Zebra" < "apple".''',
            r'''A prefix comes first: "ab" is less than "abc".''',
        ),
        example=r"""
            printf("%d %d %d\n", strcmp("a", "a") == 0, strcmp("a", "b") < 0, strcmp("b", "a") > 0);
            printf("%d %d\n", strcmp("Zebra", "apple") < 0, strcmp("ab", "abc") < 0);
        """,
        out=r"""1 1 1
1 1""",
    ),
    *c(
        "strchr",
        "strchr",
        "strchr(s, c) returns a pointer to the first c in the string s, or NULL if there is none. strrchr finds the last one.",
        see=("strstr", "null-pointer", "pointer-arithmetic", "string"),
        priority=55,
        aka=("find character", "search character", "strrchr", "find a character", "search a string", "find in string", "index of character"),
        detect=(r"\bstrr?chr\b",),
        rules=(
            r"Subtract the start to get the index: strchr(s, '=') - s.",
            r"Check for NULL before using the result.",
            r"Searching for '\0' returns a pointer to the terminator.",
        ),
        example=r"""
            const char *s = "a=b=c";
            const char *eq = strchr(s, '=');
            printf("%d %s\n", (int)(eq - s), eq + 1);
            printf("%d %d\n", (int)(strrchr(s, '=') - s), strchr(s, 'z') == NULL);
        """,
        out=r"""1 b=c
3 1""",
    ),
    *c(
        "strstr",
        "strstr",
        "strstr(haystack, needle) returns a pointer to the first place the text needle appears inside haystack, or NULL if it does not.",
        see=("strchr", "strcmp", "null-pointer", "string"),
        priority=55,
        aka=("find substring", "substring search", "search substring", "substring", "contains", "find text"),
        detect=(r"\bstrstr\b",),
        rules=(
            r"The search is case-sensitive; an empty needle matches at the very start.",
            r'''Subtract the start to get a position: strstr(s, "cat") - s.''',
            r"NULL means not found: check before dereferencing.",
        ),
        example=r"""
            const char *s = "find the needle here";
            const char *at = strstr(s, "needle");
            printf("%d %s\n", (int)(at - s), at);
            printf("%d\n", strstr(s, "NEEDLE") == NULL);
        """,
        out=r"""9 needle here
1""",
    ),
    *c(
        "memcpy",
        "memcpy",
        "memcpy(dest, src, n) copies n bytes from one block of memory to another - any type, not just text. The blocks must not overlap (memmove allows it).",
        see=("memset", "memcmp", "strcpy", "sizeof"),
        priority=55,
        aka=("memmove", "copy memory", "copy bytes", "copy array", "array copy", "memory copy"),
        detect=(r"\bmem(?:cpy|move)\b",),
        rules=(
            r"n is in BYTES: for an int array use n * sizeof(int), or simply sizeof array.",
            r"It stops for no terminator: it always copies exactly n bytes.",
            r"Overlapping blocks are undefined for memcpy; memmove handles them: memmove(a + 1, a, 3 * sizeof a[0]) shifts right.",
        ),
        example=r"""
            int a[3] = {1, 2, 3};
            int b[3];
            memcpy(b, a, sizeof a);
            b[0] = 9;
            printf("%d %d %d\n", a[0], b[0], b[2]);
        """,
        out=r"1 9 3",
    ),
    *c(
        "memset",
        "memset",
        "memset(p, value, n) sets n bytes starting at p to one byte value. Its main job is zeroing arrays and structs.",
        see=("memcpy", "initialization", "sizeof", "array"),
        priority=55,
        aka=("fill memory", "zero memory", "clear array", "set memory", "zero an array", "fill array"),
        detect=(r"\bmemset\b",),
        rules=(
            r"It writes BYTES: memset(a, 0, sizeof a) zeroes any array, but memset(ints, 1, ...) makes every int 0x01010101 (16843009), not 1.",
            r"Only 0 (and -1, all ones) mean the same thing for every integer type.",
            r"For a string, remember the terminator: memset(s, 'x', 4); s[4] = '\0';",
        ),
        example=r"""
            int a[3] = {7, 7, 7};
            memset(a, 0, sizeof a);
            char s[5];
            memset(s, 'x', 4);
            s[4] = '\0';
            printf("%d %d %s\n", a[0], a[2], s);
            int b[1];
            memset(b, 1, sizeof b);
            printf("%d\n", b[0]);
        """,
        out=r"""0 0 xxxx
16843009""",
    ),
    *c(
        "memcmp",
        "memcmp",
        "memcmp(a, b, n) compares n bytes of memory and returns 0, a negative or a positive number, like strcmp - but it does not stop at a '\\0'.",
        see=("strcmp", "memcpy", "struct-padding", "floating-point"),
        priority=55,
        aka=("compare memory", "compare bytes", "memory compare", "byte comparison"),
        detect=(r"\bmemcmp\b",),
        rules=(
            r"Bytes are compared as unsigned values; only the sign of the answer is meaningful.",
            r"Good for raw data; wrong for structs (padding bytes are unspecified) and for floating-point numbers (0.0 and -0.0 differ).",
            r"n is a byte count, and both blocks must really have n bytes.",
        ),
        example=r"""
            printf("%d %d\n", memcmp("abc", "abd", 3) < 0, memcmp("abc", "abd", 2));
            unsigned char x[2] = {1, 0}, y[2] = {1, 5};
            printf("%d\n", memcmp(x, y, 2) < 0);
        """,
        out=r"""1 0
1""",
    ),
    *c(
        "snprintf",
        "snprintf",
        "snprintf(buf, size, format, ...) works like printf but writes into a char buffer, never more than size bytes including the terminator. It returns how many characters it WANTED to write.",
        see=("printf", "buffer-overflow", "strcpy", "string-length"),
        priority=60,
        aka=("sprintf", "format into string", "string formatting", "format string into buffer", "string format", "sprintf_s"),
        detect=(r"\bs?n?printf[ \t]*\([ \t]*[A-Za-z_]\w*[ \t]*,[ \t]*(?:sizeof|\d)",),
        rules=(
            r"It always ends the text with '\0' (when size is at least 1) and silently cuts what does not fit.",
            r"A return value >= size means the text was truncated.",
            r"sprintf has no size limit and is a classic overflow: use snprintf instead.",
        ),
        example=r"""
            char buf[8];
            int n = snprintf(buf, sizeof buf, "id-%d", 12345);
            printf("%s %d\n", buf, n);
            n = snprintf(buf, sizeof buf, "%05d", 42);
            printf("%s %d\n", buf, n);
        """,
        out=r"""id-1234 8
00042 5""",
    ),
    *c(
        "puts",
        "puts and putchar",
        "puts(s) prints a string followed by a newline; putchar(c) prints one character. Both are simpler than printf when there is nothing to format.",
        see=("printf", "character", "string", "escape-sequence"),
        priority=35,
        aka=("putchar", "fputs", "print a string", "print a character", "putc", "print line"),
        detect=(r"\b(?:puts|putchar|fputs|putc)\b",),
        rules=(
            r"puts adds the newline itself; fputs(s, stdout) does not.",
            r"putchar takes an int (a char widens to it).",
            r'''puts("") prints just a newline.''',
        ),
        example=r"""
            puts("hello");
            putchar('A');
            putchar('\n');
            fputs("no newline", stdout);
            puts("|");
        """,
        out=r"""hello
A
no newline|""",
    ),
    *c(
        "character-functions",
        "Character functions (ctype)",
        "Functions from <ctype.h> that test or change one character: isdigit, isalpha, isspace, isupper, toupper, tolower.",
        see=("character", "ascii", "string-to-number", "string"),
        priority=50,
        aka=("ctype", "ctype.h", "isdigit", "isalpha", "isspace", "toupper", "tolower", "isalnum", "isupper", "islower", "is digit", "is letter", "uppercase", "lowercase", "letter case"),
        detect=(r"\b(?:isdigit|isalpha|isalnum|isspace|isupper|islower|ispunct|toupper|tolower)\b|<ctype\.h>",),
        rules=(
            r"The is... functions return non-zero for true, not necessarily 1: write isdigit(c) != 0, never == 1.",
            r"Pass an unsigned char value (or EOF): pass a negative char and it is undefined behaviour, so cast: isalpha((unsigned char)c).",
            r"They work on ONE character; to change a whole string loop over it.",
            r"toupper and tolower return the new character as an int and leave non-letters alone.",
        ),
        example=r"""
            #include <ctype.h>
            int main(void) {
                printf("%d %d %d\n", isdigit('7') != 0, isalpha('7') != 0, isspace(' ') != 0);
                printf("%c%c\n", toupper('q'), tolower('Q'));
                return 0;
            }
        """,
        out=r"""1 0 1
Qq""",
    ),
    *c(
        "string-to-number",
        "String to number",
        "Functions from <stdlib.h> that read a number out of text: atoi for an int, strtol for a long, strtod for a double. strtol also tells you where it stopped.",
        see=("string", "type-conversion", "null-pointer", "pointer"),
        priority=50,
        aka=("atoi", "strtol", "strtod", "atof", "parse int", "parse number", "convert string to int", "string to int", "text to number", "parse", "parsing", "strtoul"),
        detect=(r"\b(?:atoi|atol|atof|strtol|strtoul|strtod|strtoll)\b",),
        rules=(
            r'''atoi("12abc") is 12: it stops at the first non-digit. atoi("abc") is 0, the same as atoi("0"), so it cannot report an error.''',
            r"strtol(s, &end, 10) sets end to the first unread character: end == s means no digits at all, *end != '\0' means leftovers.",
            r"The last argument is the base: 10, 16 for hex, 2 for binary, 0 to detect 0x and 0 prefixes.",
            r"Leading spaces are skipped; a too-big number is undefined for atoi and gives LONG_MAX with errno set for strtol.",
        ),
        example=r"""
            #include <stdlib.h>
            int main(void) {
                char *end;
                long v = strtol("42xyz", &end, 10);
                printf("%ld %s %d\n", v, end, atoi("abc"));
                printf("%ld %.1f\n", strtol("ff", NULL, 16), strtod("2.5", NULL));
                return 0;
            }
        """,
        out=r"""42 xyz 0
255 2.5""",
    ),
    *c(
        "buffer-overflow",
        "Buffer overflow",
        "Writing past the end of an array or buffer. C does not check, so the extra bytes overwrite whatever lies next in memory: a classic crash and security hole.",
        see=("undefined-behavior", "strcpy", "snprintf", "off-by-one", "array"),
        priority=55,
        aka=("buffer overrun", "overrun", "out of bounds", "out-of-bounds", "bounds checking", "array bounds", "stack smashing", "overflow of buffer", "gets", "past the end"),
        detect=(r"\b(?:gets|sprintf)[ \t]*\(",),
        rules=(
            r"It is undefined behaviour: it may crash now, corrupt another variable, or look fine until it matters.",
            r"Before copying, check the room: strlen(src) + 1 <= sizeof dest. Prefer snprintf and check its return value.",
            r"An array does not know its own size, so every function that fills one needs the size.",
            r'''A string of n characters needs an array of n + 1: char s[5] = "hello" leaves no space for the terminator.''',
        ),
        example=r"""
            char buf[6];
            const char *src = "overflowing";
            if (strlen(src) + 1 <= sizeof buf) strcpy(buf, src);
            else snprintf(buf, sizeof buf, "%s", src);
            printf("%s\n", buf);
        """,
        out=r"overf",
    ),
]
