"""Gotchas, Java, the second helping: numbers that wrap, equals that is not ==, and order of initialisation.

Same rules as content_java.py: single file, `public class Main` first with a static main (JDK 21 source launcher),
one printed line, nothing from the clock, randomness, hashing or HashMap iteration order. Helper classes sit after
Main (or nest inside it) because the launcher runs the first class in the file.
"""

from __future__ import annotations

from .items import Item, make

q = make("java")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics with a real trap ──────────────────────────────
    q("division-and-remainder-signs", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println((-7 / 2) + " " + (-7 % 3) + " "
                    + Math.floorDiv(-7, 2) + " " + Math.floorMod(-7, 3));
            }
        }
    ''', "-3 -1 -4 2", ["-4 2 -4 2", "-3 2 -3 -1", "-4 -1 -3 2"],
      "/ truncates toward zero and % takes the sign of the left side",
      """Java cuts the quotient toward zero, so -7 / 2 is -3 and -7 % 3 is -1. `floorDiv` and `floorMod` round
      toward minus infinity instead, giving -4 and a remainder of 2 that is never negative for a positive
      divisor."""),

    q("int-overflow-wraps", r'''
        public class Main {
            public static void main(String[] args) {
                int max = Integer.MAX_VALUE;
                System.out.println((max + 1) + " " + Math.abs(Integer.MIN_VALUE)
                    + " " + (max * 2));
            }
        }
    ''', "-2147483648 -2147483648 -2", ["2147483648 2147483648 4294967294",
                                       "-2147483648 2147483648 -2", "Error"],
      "int arithmetic wraps around silently, and abs of the minimum stays negative",
      """Overflow throws nothing: MAX + 1 wraps to the minimum, and MAX * 2 is 0xFFFFFFFE, which is -2. There is no
      positive counterpart to the minimum value, so `Math.abs` returns it unchanged."""),

    q("int-product-before-long", r'''
        public class Main {
            public static void main(String[] args) {
                long wrong = 1000 * 1000 * 1000 * 10;
                long right = 1000L * 1000 * 1000 * 10;
                System.out.println(wrong + " " + right);
            }
        }
    ''', "1410065408 10000000000", ["10000000000 10000000000", "1410065408 1410065408",
                                    "-1 10000000000"],
      "The multiplication happens in int before the result is widened to long",
      """Assigning to a `long` does not make the arithmetic on its right use long. All four factors are ints, so
      the product overflows 32 bits first (10 billion mod 2^32 is 1410065408). One `L` literal is enough to make
      the whole chain long."""),

    q("char-arithmetic-types", r'''
        public class Main {
            public static void main(String[] args) {
                char c = 'A';
                c += 2;
                System.out.println(c + " " + (c + 1) + " " + (char) (c + 1));
            }
        }
    ''', "C 68 D", ["C C D", "67 68 D", "C 68 68"],
      "char plus int is an int; += quietly casts back, and + 1 does not",
      """`c += 2` has an implicit cast, so `c` is still a char and prints as C. `c + 1` is promoted to int (68),
      and only the explicit `(char)` turns it into the letter D."""),

    q("string-plus-order", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(1 + 2 + "x" + 1 + 2);
            }
        }
    ''', "3x12", ["12x12", "3x3", "3x1 2"],
      "Numbers are added until the first String, then everything is appended",
      """`+` associates left to right: `1 + 2` is 3, then `3 + "x"` is "3x", and from there each later `+` appends
      text, so 1 and 2 are written as digits."""),

    q("double-to-int-conversions", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println((int) 3.99 + " " + (int) -3.99 + " "
                    + Math.round(-2.5) + " " + Math.round(2.5));
            }
        }
    ''', "3 -3 -2 3", ["3 -4 -3 3", "4 -4 -3 3", "3 -3 -3 2"],
      "A cast truncates toward zero; Math.round rounds halves up",
      """`(int)` just drops the fraction, so -3.99 becomes -3. `Math.round` adds one half and takes the floor,
      which sends 2.5 to 3 and -2.5 to -2."""),

    q("float-equality", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println((0.1 + 0.2 == 0.3) + " " + (0.1f == 0.1) + " "
                    + (0.5f == 0.5) + " " + (double) 0.1f);
            }
        }
    ''', "false false true 0.10000000149011612",
      ["true true true 0.1", "false true true 0.1", "false false true 0.1"],
      "Most decimal fractions are not exact, and a float is not the same number as a double",
      """0.1 + 0.2 misses 0.3 in binary. `0.1f` is the float nearest 0.1, a different number from the double 0.1,
      so they differ once widened. 0.5 is a power of two and exact in both."""),

    q("ternary-numeric-promotion", r'''
        public class Main {
            public static void main(String[] args) {
                int zero = 0;
                System.out.println((true ? 1 : 2.0) + " " + (true ? 'a' : 0)
                    + " " + (true ? 'a' : zero));
            }
        }
    ''', "1.0 a 97", ["1 a a", "1.0 97 97", "1 97 97"],
      "The two branches of ?: are converted to a common type before the result is used",
      """With an int and a double branch, the int is promoted: 1.0. A char and the constant 0 (which fits in a
      char) stay char, so it prints a. A char and an int variable become int, so it prints 97."""),

    q("long-equals-integer", r'''
        public class Main {
            public static void main(String[] args) {
                Long l = 1L;
                System.out.println(l.equals(1) + " " + l.equals(1L) + " "
                    + (l == 1));
            }
        }
    ''', "false true true", ["true true true", "false false true", "true true false"],
      "equals checks the class first: a Long is never equal to an Integer",
      """`l.equals(1)` boxes the 1 as an Integer, and `Long.equals` returns false for any non-Long. The `==` on
      the last comparison unboxes `l` and compares plain numbers, which is true."""),

    q("short-circuit-versus-single", r'''
        public class Main {
            public static void main(String[] args) {
                int i = 0;
                boolean a = i++ > 0 && i++ > 0;
                boolean b = i++ > 5 & i++ > 0;
                System.out.println(a + " " + b + " " + i);
            }
        }
    ''', "false false 3", ["false true 3", "false false 2", "true true 4"],
      "&& skips the right side when it can; & always evaluates both",
      """In the first line `i++ > 0` is false (0 > 0), so `&&` never runs the second `i++`; i is 1. The `&` in
      the next line evaluates both sides (1 > 5 is false, 2 > 0 is true), so i reaches 3, and false & true is
      still false."""),

    q("compound-assignment-casts", r'''
        public class Main {
            public static void main(String[] args) {
                byte b = 120;
                b += 10;
                int x = 5;
                x *= 1.5;
                System.out.println(b + " " + x);
            }
        }
    ''', "-126 7", ["130 7", "-126 8", "130 7.5"],
      "Compound assignment includes a hidden cast back to the variable's type",
      """`b += 10` is `b = (byte) (b + 10)`, so 130 wraps to -126, and `x *= 1.5` is `x = (int) (x * 1.5)`, which
      truncates 7.5 to 7. A plain `b = b + 10` would not even compile."""),

    q("split-drops-trailing-empties", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println("a.b.c".split(".").length + " "
                    + "a,b,,".split(",").length + " "
                    + "a,b,,".split(",", -1).length);
            }
        }
    ''', "0 2 4", ["3 2 4", "0 4 4", "3 4 4"],
      "split takes a regex and throws away trailing empty strings",
      """`.` as a regex matches every character, so every piece between matches is empty and all of them are
      trailing: the result is empty. `"a,b,,"` loses its two trailing empties unless a negative limit says to
      keep them."""),

    q("int-division-into-double", r'''
        public class Main {
            public static void main(String[] args) {
                int total = 7;
                double half = total / 2;
                System.out.println(half + " " + total / 2.0 + " " + 1 / 2 * 4.0);
            }
        }
    ''', "3.0 3.5 0.0", ["3.5 3.5 2.0", "3.0 3.5 2.0", "3.5 3.5 0.0"],
      "Integer division happens before the result is stored in the double",
      """`total / 2` is an int division giving 3, widened to 3.0 afterwards. Only an operand that is itself a
      double, like `2.0`, makes the division fractional. In `1 / 2 * 4.0` the `1 / 2` is done first and is 0."""),

    q("array-default-values", r'''
        public class Main {
            public static void main(String[] args) {
                int[] a = new int[2];
                String[] s = new String[2];
                boolean[] b = new boolean[2];
                double[] d = new double[2];
                System.out.println(a[0] + " " + s[0] + " " + b[0] + " " + d[0]);
            }
        }
    ''', "0 null false 0.0", ["0 \"\" false 0", "0 null 0 0.0", "null null false 0.0"],
      "Array elements start at the type's zero value; objects start as null",
      """Java initialises every array slot: 0 for numbers, false for booleans, and null for references such as
      String. The empty string is a real object and is never the default."""),

    q("final-reference-mutable", r'''
        public class Main {
            public static void main(String[] args) {
                final int[] a = {1, 2};
                final StringBuilder sb = new StringBuilder("x");
                a[0] = 9;
                sb.append("y");
                System.out.println(a[0] + sb.toString() + a.length);
            }
        }
    ''', "9xy2", ["1xy2", "9x2", "Error"],
      "final fixes the reference, not the object it points to",
      """`final` only forbids re-assigning `a` or `sb`. The array's elements and the builder's contents are
      ordinary mutable state, so the writes work."""),

    q("string-versus-builder-argument", r'''
        public class Main {
            static void add(String s) { s += "x"; }
            static void add(StringBuilder sb) { sb.append("x"); }
            public static void main(String[] args) {
                String s = "a";
                StringBuilder sb = new StringBuilder("a");
                add(s);
                add(sb);
                System.out.println(s + " " + sb);
            }
        }
    ''', "a ax", ["ax ax", "a a", "ax a"],
      "Java passes references by value: reassigning a parameter is invisible to the caller",
      """Inside `add(String)`, `s += "x"` builds a new String and rebinds the local parameter only. The
      StringBuilder overload mutates the object the caller also holds, so that change is visible."""),

    q("pre-and-post-increment", r'''
        public class Main {
            public static void main(String[] args) {
                int i = 5;
                int r = i++ + ++i;
                int j = 5;
                j = j++;
                System.out.println(r + " " + i + " " + j);
            }
        }
    ''', "12 7 5", ["11 7 6", "12 6 6", "10 7 5"],
      "i++ yields the old value; ++i the new one; j = j++ undoes itself",
      """`i++ + ++i` is 5 (then i becomes 6) plus 7 (i becomes 7), so 12. In `j = j++` the old value 5 is
      remembered, j is incremented, and then the assignment writes the old 5 back."""),

    q("float-special-values", r'''
        public class Main {
            public static void main(String[] args) {
                double nan = 0.0 / 0;
                System.out.println(1.0 / 0 + " " + -1.0 / 0 + " "
                    + (nan == nan) + " " + (int) nan);
            }
        }
    ''', "Infinity -Infinity false 0", ["Error Error true 0", "Infinity -Infinity true 0",
                                       "Infinity -Infinity false NaN"],
      "Floating-point division by zero is Infinity or NaN, not an exception",
      """Only integer division by zero throws. For doubles the result is an infinity or NaN, NaN is not equal to
      anything including itself, and casting NaN to int gives 0."""),

    q("shift-distances", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println((1 << 33) + " " + (1L << 33) + " "
                    + (-8 >> 1) + " " + (-8 >>> 28));
            }
        }
    ''', "2 8589934592 -4 15", ["0 8589934592 -4 15", "8589934592 8589934592 4 15",
                                "2 8589934592 -4 -1"],
      "An int shift distance is taken modulo 32; >> keeps the sign, >>> does not",
      """`1 << 33` is `1 << 1`, which is 2, because only the low five bits of the distance count for an int. `>>`
      is an arithmetic shift, so -8 >> 1 is -4, while `>>>` shifts in zeros: 0xFFFFFFF8 >>> 28 is 15."""),

    q("string-compare-to", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println("apple".compareTo("banana") + " "
                    + "a".compareTo("c") + " " + "Z".compareTo("a") + " "
                    + "abc".compareTo("ab"));
            }
        }
    ''', "-1 -2 -7 1", ["-1 -1 -1 1", "-1 -2 7 -1", "-1 -2 -7 3"],
      "compareTo returns the difference of the first differing chars, or of the lengths",
      """It subtracts the first pair of characters that differ: a - b is -1, a - c is -2, and Z (90) minus a
      (97) is -7. If one string is a prefix of the other, the result is the length difference, 3 - 2 = 1."""),

    q("substring-bounds", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println("hello".substring(1, 3) + "|"
                    + "abc".substring(3) + "|" + "hello".indexOf("z"));
            }
        }
    ''', "el||-1", ["ell||-1", "el|c|-1", "el||0"],
      "substring's end is exclusive, and starting at length gives an empty string",
      """`substring(1, 3)` returns indexes 1 and 2: "el". Starting at index 3 of a 3-letter string is legal and
      empty, not an error. `indexOf` signals "absent" with -1."""),

    q("list-remove-overloads", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> l = new ArrayList<>(List.of(10, 20, 30));
                l.remove(1);
                l.remove(Integer.valueOf(10));
                System.out.println(l);
            }
        }
    ''', "[30]", ["[20, 30]", "[10, 30]", "[20]"],
      "remove(int) removes by position; remove(Object) removes by value",
      """`l.remove(1)` picks the int overload and deletes the element at index 1 (the 20). Wrapping the number in
      `Integer.valueOf` selects `remove(Object)`, which deletes the value 10, leaving only 30."""),

    q("as-list-views", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Integer[] boxed = {1, 2, 3};
                List<Integer> view = Arrays.asList(boxed);
                boxed[0] = 9;
                System.out.println(view.get(0) + " "
                    + Arrays.asList(new int[] {1, 2, 3}).size());
            }
        }
    ''', "9 1", ["1 3", "9 3", "1 1"],
      "Arrays.asList is a window onto the array, and an int[] is a single element",
      """The list does not copy the array, so a write to `boxed[0]` shows in the list. A primitive `int[]` is
      not an `Object[]`, so `asList` treats the whole array as one element and the list has size 1."""),

    q("remove-in-foreach", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> list = new ArrayList<>(List.of("a", "b", "c"));
                for (String s : list) {
                    if (s.equals("b")) list.remove(s);
                }
                System.out.println(list);
            }
        }
    ''', "[a, c]", ["[a, b]", "[a, b, c]", "[c]"],
      "Removing the second-to-last element inside a for-each loop does not throw",
      """Removing "b" shrinks the list to 2 while the iterator's cursor is also 2, so `hasNext()` says there is
      nothing more and the concurrent-modification check never runs. Remove the first element or the last and it
      would throw."""),

    q("string-concat-null", r'''
        public class Main {
            public static void main(String[] args) {
                String s = null;
                s += "x";
                s += null;
                System.out.println(s + " " + s.length());
            }
        }
    ''', "nullxnull 9", ["x 1", "xnull 5", "nullxnull 5"],
      "A null String is appended as the four letters \"null\"",
      """String concatenation converts null to the text "null" instead of failing, so `null + "x"` is "nullx" and
      appending another null gives "nullxnull", 9 characters long."""),

    q("equals-between-types", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                int[] a = {1};
                int[] b = {1};
                System.out.println("a".equals('a') + " " + a.equals(b) + " "
                    + Arrays.equals(a, b));
            }
        }
    ''', "false false true", ["true true true", "false true true", "true false true"],
      "equals is only true for the same kind of object; arrays inherit identity equals",
      """A String never equals a Character, even when they look alike. Arrays do not override `equals`, so it
      compares references and two arrays with the same content differ; `Arrays.equals` compares the elements."""),

    q("treemap-string-keys", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<String, String> m = new TreeMap<>();
                m.put("9", "a");
                m.put("10", "b");
                m.put("2", "c");
                System.out.println(m);
            }
        }
    ''', "{10=b, 2=c, 9=a}", ["{2=c, 9=a, 10=b}", "{9=a, 10=b, 2=c}", "{9=a, 2=c, 10=b}"],
      "A TreeMap of Strings sorts as text, not as numbers",
      """Keys compare with `String.compareTo`, so "10" sorts before "2" and "9" because '1' comes before '2'.
      Use Integer keys for numeric order."""),

    q("treeset-uses-comparator", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Set<String> s = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
                s.add("a");
                s.add("A");
                s.add("b");
                System.out.println(s.size() + " " + s.contains("B") + " " + s);
            }
        }
    ''', "2 true [a, b]", ["3 false [A, a, b]", "3 true [a, A, b]", "2 false [a, b]"],
      "A sorted set decides equality by its comparator, not by equals",
      """"A" compares as 0 against "a", so the set considers it a duplicate and keeps the first one added. For
      the same reason `contains("B")` is true even though no element equals "B"."""),

    q("bigdecimal-scale", r'''
        import java.math.BigDecimal;

        public class Main {
            public static void main(String[] args) {
                BigDecimal a = new BigDecimal("1.10");
                BigDecimal b = new BigDecimal("1.1");
                System.out.println(a.equals(b) + " " + a.compareTo(b) + " "
                    + new BigDecimal("2.50").stripTrailingZeros());
            }
        }
    ''', "false 0 2.5", ["true 0 2.50", "false 1 2.5", "true 0 2.5"],
      "BigDecimal.equals compares scale too: 1.10 is not equal to 1.1",
      """The two numbers have the same value but different scales (2 and 1 decimal places), and `equals` demands
      both match. `compareTo` ignores scale and returns 0. `stripTrailingZeros` drops the extra zero."""),

    q("math-rounding-functions", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(Math.floor(-1.5) + " " + Math.ceil(-1.5) + " "
                    + Math.round(-1.5) + " " + Math.rint(2.5));
            }
        }
    ''', "-2.0 -1.0 -1 2.0", ["-1.0 -2.0 -2 3.0", "-2.0 -1.0 -2 3.0", "-2.0 -1.0 -1 3.0"],
      "floor, ceil and rint return doubles; round returns a long and rounds halves up",
      """`floor` goes down to -2.0, `ceil` up to -1.0. `Math.round(-1.5)` is floor(-1.5 + 0.5), which is -1, a
      long without a decimal point. `rint` rounds halves to the even neighbour: 2.5 becomes 2.0."""),

    q("format-rounding-half-up", r'''
        import java.util.Locale;

        public class Main {
            public static void main(String[] args) {
                System.out.println(String.format(Locale.ROOT, "%.0f %.0f %.1f",
                    0.5, 1.5, 0.25));
            }
        }
    ''', "1 2 0.3", ["0 2 0.2", "1 2 0.2", "0 1 0.3"],
      "String.format rounds halves up, unlike C's printf, which rounds them to even",
      """Java's `%f` uses the HALF_UP rounding mode on the exact decimal value, so 0.5 becomes 1 and 0.25 becomes
      0.3. 0.5, 1.5 and 0.25 are exact in binary, so there is no representation error to hide behind."""),

    q("format-flags", r'''
        import java.util.Locale;

        public class Main {
            public static void main(String[] args) {
                System.out.println(String.format(Locale.ROOT, "|%5.1f|%-4d|%04d|%x",
                    3.14159, 7, 42, 255));
            }
        }
    ''', "|  3.1|7   |0042|ff", ["|3.1|7|42|ff", "|  3.1|   7|0042|FF", "|  3.2|7   |0042|ff"],
      "Width, '-', '0' and the precision each mean something different",
      """`%5.1f` pads to width 5 with one decimal, `%-4d` left-aligns in 4 columns, `%04d` zero-pads, and `%x`
      prints lowercase hexadecimal."""),

    q("integer-radix-strings", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(Integer.toBinaryString(-1).length() + " "
                    + Integer.toHexString(255) + " "
                    + Integer.parseInt("-ff", 16) + " " + Long.toBinaryString(5));
            }
        }
    ''', "32 ff -255 101", ["1 ff 255 101", "32 FF -255 101", "32 ff 255 5"],
      "toBinaryString shows the raw 32 bits of a negative int",
      """-1 is thirty-two 1 bits in two's complement, so its binary string is 32 characters long. `parseInt` takes
      an optional sign and a radix, so "-ff" in base 16 is -255."""),

    q("digit-character-values", r'''
        public class Main {
            public static void main(String[] args) {
                char c = '7';
                System.out.println(Character.getNumericValue(c) + " " + (c - '0')
                    + " " + (int) c);
            }
        }
    ''', "7 7 55", ["55 7 7", "7 55 55", "7 7 7"],
      "The character '7' is the number 55; subtract '0' to get the digit",
      """A char holds its code point, and the digit characters start at '0' = 48. `Character.getNumericValue`
      and `c - '0'` both convert to the digit; a plain `(int) c` gives the code."""),

    q("labelled-break", r'''
        public class Main {
            public static void main(String[] args) {
                int n = 0;
                outer:
                for (int i = 0; i < 4; i++) {
                    for (int j = 0; j < 4; j++) {
                        if (i * j == 4) break outer;
                        n++;
                    }
                }
                System.out.println(n);
            }
        }
    ''', "10", ["14", "16", "12"],
      "break outer leaves both loops, not just the inner one",
      """Rows 0 and 1 count 4 each, and row 2 counts j = 0 and 1 before reaching i * j == 4 at j = 2. The labelled
      break ends the whole nest there, so n is 4 + 4 + 2 = 10. A plain `break` would only end row 2 and the
      count would go on to 14."""),

    q("loop-with-division-step", r'''
        public class Main {
            public static void main(String[] args) {
                int sum = 0;
                for (int i = 10; i > 0; i /= 3) {
                    sum += i;
                }
                System.out.println(sum);
            }
        }
    ''', "14", ["13", "24", "10"],
      "The update clause can be any statement: 10, 3, 1, then 0 stops the loop",
      """`i /= 3` is integer division, so i goes 10, 3, 1 and then 0, where `i > 0` fails. The body runs for 10,
      3 and 1 only, adding up to 14."""),

    q("octal-literal", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(010 + " " + Integer.parseInt("010") + " "
                    + 0x10 + " " + 0b101);
            }
        }
    ''', "8 10 16 5", ["10 10 16 5", "8 8 16 5", "10 10 10 5"],
      "A leading zero in source code means octal; the same text parsed at runtime is decimal",
      """The literal `010` is base 8, so it is 8, while `Integer.parseInt("010")` reads ordinary decimal and
      gives 10. `0x` and `0b` prefixes mean hex and binary."""),

    q("narrowing-casts", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println((int) 3_000_000_000L + " " + (byte) 200 + " "
                    + (short) 70000 + " " + (int) (char) -1);
            }
        }
    ''', "-1294967296 -56 4464 65535", ["3000000000 200 70000 -1", "-1294967296 -56 4464 -1",
                                       "-1294967296 56 4464 65535"],
      "Casting to a narrower integer keeps the low bits; char is unsigned",
      """Each cast keeps only as many low bits as the target holds: 200 as a byte is 200 - 256 = -56, and 70000
      as a short is 70000 - 65536 = 4464. A char has 16 unsigned bits, so (char) -1 is 65535."""),

    q("generics-are-erased", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> a = new ArrayList<>();
                List<Integer> b = new ArrayList<>();
                System.out.println(a.getClass() == b.getClass());
            }
        }
    ''', "true", ["false", "Error", "null"],
      "Type parameters do not exist at runtime",
      """Generics are checked by the compiler and then erased. A `List<String>` and a `List<Integer>` are both
      plain `ArrayList` objects, so their classes are identical."""),

    q("array-store-exception", r'''
        public class Main {
            public static void main(String[] args) {
                Object[] objs = new String[1];
                try {
                    objs[0] = 1;
                    System.out.println("stored");
                } catch (ArrayStoreException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', "java.lang.Integer", ["stored", "java.lang.String", "null"],
      "Arrays are covariant: the compiler allows it and the runtime checks the real element type",
      """A `String[]` may be used as an `Object[]`, but the array remembers it holds Strings. Storing an Integer
      compiles and then fails at runtime, with the offending class name as the exception message."""),

    q("ternary-unboxing-npe", r'''
        public class Main {
            public static void main(String[] args) {
                Integer n = null;
                try {
                    int r = true ? n : 0;
                    System.out.println(r);
                } catch (NullPointerException e) {
                    Integer s = true ? n : Integer.valueOf(0);
                    System.out.println("NPE " + s);
                }
            }
        }
    ''', "NPE null", ["0", "null", "NPE 0"],
      "A ?: with an Integer and an int unboxes the Integer, even for the branch taken",
      """When one operand is a primitive int, the other (the null Integer) is unboxed to match, and that throws
      a NullPointerException. If both operands are `Integer`, no unboxing happens and null passes through."""),

    q("double-equals-versus-equals", r'''
        public class Main {
            public static void main(String[] args) {
                Double nan = Double.NaN;
                System.out.println((Double.NaN == Double.NaN) + " "
                    + nan.equals(nan) + " " + (0.0 == -0.0) + " "
                    + Double.valueOf(0.0).equals(-0.0));
            }
        }
    ''', "false true true false", ["false false true true", "true true true false",
                                    "false true false false"],
      "== on double primitives and equals on Double boxes disagree about NaN and -0.0",
      """The primitive comparison follows IEEE rules: NaN differs from itself and 0.0 equals -0.0. `Double.equals`
      compares the underlying bits so that it is consistent with hashing, so NaN equals NaN and 0.0 differs from
      -0.0."""),

    q("subtraction-comparator-overflow", r'''
        public class Main {
            public static void main(String[] args) {
                int a = Integer.MAX_VALUE;
                int b = -1;
                System.out.println((a - b > 0) + " " + (Integer.compare(a, b) > 0));
            }
        }
    ''', "false true", ["true true", "false false", "true false"],
      "Comparing by subtraction breaks when the difference overflows",
      """MAX - (-1) is 2147483648, which does not fit in an int and wraps to a negative number, so the
      subtraction claims a is smaller. `Integer.compare` never subtracts, so it is right."""),

    q("sort-uppercase-first", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                String[] words = {"b", "a", "C", "B"};
                Arrays.sort(words);
                System.out.println(Arrays.toString(words));
            }
        }
    ''', "[B, C, a, b]", ["[a, b, B, C]", "[a, B, b, C]", "[C, B, b, a]"],
      "The natural String order compares char codes, so capitals come first",
      """Upper-case letters have smaller codes than lower-case ones, so all of B and C sort before a and b.
      `String.CASE_INSENSITIVE_ORDER` gives dictionary-style order."""),

    q("unicode-escape-in-comment", r'''
        public class Main {
            public static void main(String[] args) {
                int x = 1; // reset it \u000a x = 2;
                System.out.println(x);
            }
        }
    ''', "2", ["1", "Error", "0"],
      "Unicode escapes are translated before the code is parsed, even inside comments",
      """`\\u000a` is turned into a real line break before the lexer runs, which ends the `//` comment early and
      leaves `x = 2;` as live code on a new line."""),

    q("map-put-merge", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<String, Integer> m = new TreeMap<>();
                m.put("a", 1);
                Integer old = m.put("a", 2);
                m.putIfAbsent("a", 9);
                m.merge("a", 5, Integer::sum);
                System.out.println(old + " " + m);
            }
        }
    ''', "1 {a=7}", ["null {a=7}", "1 {a=5}", "2 {a=9}"],
      "put returns the previous value; putIfAbsent does nothing for an existing key",
      """The second `put` replaces 1 with 2 and returns the old 1. `putIfAbsent` leaves the existing 2 alone, and
      `merge` combines the existing 2 with 5 using sum, giving 7."""),

    q("print-char-array", r'''
        public class Main {
            public static void main(String[] args) {
                char[] c = {'h', 'i'};
                System.out.println(c);
            }
        }
    ''', "hi", ["[C@1b6d3586", "[h, i]", "h i"],
      "println has a char[] overload that prints the characters",
      """Most arrays print as a type tag and a hash, but `PrintStream.println(char[])` is special and writes the
      characters. Concatenating the array with a String, `"" + c`, would give the unhelpful tag instead."""),

    q("stringbuilder-char-constructor", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(new StringBuilder('a').append("b"));
            }
        }
    ''', "b", ["ab", "97b", "a"],
      "new StringBuilder('a') passes a char to the int capacity constructor",
      """There is no char constructor, so 'a' widens to the int 97 and means an initial capacity of 97 characters.
      The builder starts empty, and only the appended "b" is in it."""),

    q("string-pool-constants", r'''
        public class Main {
            public static void main(String[] args) {
                String a = "ab";
                String b = "a" + "b";
                String c = "a";
                String d = c + "b";
                final String e = "a";
                System.out.println((a == b) + " " + (a == d) + " "
                    + (a == e + "b"));
            }
        }
    ''', "true false true", ["true true true", "false false false", "true false false"],
      "Compile-time constant concatenation is interned; runtime concatenation is not",
      """`"a" + "b"` and a `final` variable with a constant value are folded by the compiler into the pooled "ab".
      `c + "b"` uses a non-final variable, so the join happens at runtime and creates a new object."""),

    q("record-equality", r'''
        public class Main {
            record P(int x, int y) {}

            public static void main(String[] args) {
                P p = new P(1, 2);
                P q = new P(1, 2);
                System.out.println(p + " " + p.equals(q) + " " + (p == q));
            }
        }
    ''', "P[x=1, y=2] true false", ["P@1b6d3586 false false", "P[x=1, y=2] true true",
                                    "P[x=1, y=2] false false"],
      "A record gets equals and toString from its components; == is still identity",
      """The compiler generates `equals` and `toString` for a record, so equal components mean equal records and
      a readable text form. `==` compares the references, and `new` made two separate objects."""),

    q("field-hiding-and-static-hiding", r'''
        public class Main {
            static class A {
                String n = "A";
                String get() { return n; }
                static String who() { return "A"; }
            }
            static class B extends A {
                String n = "B";
                String get() { return n; }
                static String who() { return "B"; }
            }
            public static void main(String[] args) {
                A x = new B();
                System.out.println(x.n + x.get() + x.who());
            }
        }
    ''', "ABA", ["BBB", "ABB", "AAA"],
      "Methods are chosen by the object, fields and static methods by the declared type",
      """`get()` is overridden, so the call finds B's version, which reads B's own `n`. The field access `x.n` and
      the static call `x.who()` are resolved by the variable's type, A, at compile time."""),

    q("private-method-not-overridden", r'''
        public class Main {
            static class A {
                private String f() { return "A"; }
                String call() { return f(); }
            }
            static class B extends A {
                String f() { return "B"; }
            }
            public static void main(String[] args) {
                System.out.println(new B().call() + new B().f());
            }
        }
    ''', "AB", ["BB", "AA", "BA"],
      "A private method cannot be overridden, so the base class keeps calling its own",
      """`A.call()` invokes `f()` and, since A's `f` is private, that call is bound to A's version. B's `f` is a
      new, unrelated method that only a call through B can see."""),

    q("constructor-and-initialiser-order", r'''
        public class Main {
            static StringBuilder sb = new StringBuilder();
            static class A {
                { sb.append("1"); }
                A() { sb.append("2"); }
            }
            static class B extends A {
                { sb.append("3"); }
                B() { sb.append("4"); }
            }
            public static void main(String[] args) {
                new B();
                System.out.println(sb);
            }
        }
    ''', "1234", ["3412", "1324", "2143"],
      "Superclass initialisers and constructor first, then the subclass's",
      """Constructing B first runs A completely: its instance initialiser block (1) and then its constructor body
      (2). Only afterwards do B's initialiser block (3) and constructor body (4) run."""),

    q("overridden-call-in-constructor", r'''
        public class Main {
            static class A {
                A() { show(); }
                void show() {}
            }
            static class B extends A {
                int x = 5;
                void show() { System.out.print(x + " "); }
            }
            public static void main(String[] args) {
                B b = new B();
                System.out.println(b.x);
            }
        }
    ''', "0 5", ["5 5", "null 5", "0 0"],
      "A constructor that calls an overridable method sees the subclass half-built",
      """`new B()` starts with A's constructor, which calls B's `show()` before B's field initialiser `x = 5`
      has run, so it sees the default 0. Afterwards x is 5."""),

    q("static-initialisation-order", r'''
        public class Main {
            static int a = f();
            static int b = 5;
            static int f() { return b + 1; }

            public static void main(String[] args) {
                System.out.println(a + " " + b);
            }
        }
    ''', "1 5", ["6 5", "0 5", "6 0"],
      "Static fields are initialised in textual order, so b is still 0 when a is computed",
      """`a = f()` runs first, while `b` has only its default value 0, so `f()` returns 1. Then `b = 5` is
      assigned. A forward reference through a method hides the problem from the compiler."""),

    q("null-overload-most-specific", r'''
        public class Main {
            static String f(Object o) { return "obj"; }
            static String f(String s) { return "str"; }

            public static void main(String[] args) {
                System.out.println(f(null) + " " + f((Object) null));
            }
        }
    ''', "str obj", ["obj obj", "str str", "Error"],
      "With null, the most specific applicable overload wins; the static type decides otherwise",
      """Both overloads accept null, and String is more specific than Object, so `f(null)` picks the String
      one. The cast `(Object) null` changes the static type, which selects the Object overload."""),

    q("overload-widening-before-boxing", r'''
        public class Main {
            static String f(long x) { return "long"; }
            static String f(Integer x) { return "Integer"; }
            static String f(int... x) { return "varargs"; }
            static String g(long x) { return "long"; }
            static String g(Object x) { return "Object"; }

            public static void main(String[] args) {
                System.out.println(f(1) + " " + g(Integer.valueOf(1)));
            }
        }
    ''', "long Object", ["Integer Object", "long long", "varargs Integer"],
      "Overload resolution tries widening before boxing, and boxing before varargs",
      """For `f(1)` the first phase allows widening only, so `long` wins over boxing to Integer. For
      `g(Integer)`, phase one also allows subtyping (an Integer is an Object), so it beats the unboxing that the
      `long` version would need."""),

    q("varargs-null-and-arrays", r'''
        public class Main {
            static int count(Object... a) { return a == null ? -1 : a.length; }

            public static void main(String[] args) {
                System.out.println(count() + " " + count((Object[]) null) + " "
                    + count((Object) null) + " " + count(new Object[] {1, 2})
                    + " " + count(new int[] {1, 2}));
            }
        }
    ''', "0 -1 1 2 1", ["0 0 1 2 2", "0 -1 0 2 2", "1 -1 1 2 1"],
      "A varargs call may pass an array directly, but only an Object[] counts as the array",
      """No arguments make an empty array. A null cast to `Object[]` is the array itself, so it is null, while a
      null cast to Object is one element. An `int[]` is not an `Object[]`, so it is wrapped as a single
      element."""),

    q("finally-return-rules", r'''
        public class Main {
            static int a() { try { return 1; } finally { return 2; } }
            static int b() { int x = 1; try { return x; } finally { x = 3; } }
            @SuppressWarnings("finally")
            static int c() {
                try { throw new RuntimeException(); } finally { return 4; }
            }

            public static void main(String[] args) {
                System.out.println(a() + " " + b() + " " + c());
            }
        }
    ''', "2 1 4", ["1 3 4", "2 3 4", "1 1 Error"],
      "A return in finally replaces the pending return or exception",
      """`a` returns 2 because the `finally` return wins. In `b` the value 1 is already saved when `finally`
      runs, so changing x does nothing. In `c` the return in `finally` even swallows the exception."""),

    q("exception-messages", r'''
        public class Main {
            public static void main(String[] args) {
                int zero = 0;
                try {
                    System.out.println(5 / zero);
                } catch (ArithmeticException e) {
                    System.out.println(e.getMessage() + " " + 5.0 / zero);
                }
            }
        }
    ''', "/ by zero Infinity", ["Infinity Infinity", "/ by zero NaN", "NaN Infinity"],
      "Integer division by zero throws; double division does not",
      """Both lines divide by the same variable, but only the int division raises an `ArithmeticException` with the
      message "/ by zero". The double division quietly produces Infinity."""),

    q("sublist-is-a-view", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> l = new ArrayList<>(List.of(1, 2, 3, 4));
                List<Integer> s = l.subList(1, 3);
                s.set(0, 9);
                s.clear();
                System.out.println(l);
            }
        }
    ''', "[1, 4]", ["[1, 9, 3, 4]", "[1, 2, 3, 4]", "[9, 4]"],
      "subList is a window onto the original list, not a copy",
      """Writing through the view changes the parent, and `clear()` on the view removes its two elements from the
      parent. Wrap it, `new ArrayList<>(l.subList(1, 3))`, for an independent copy."""),

    q("stream-element-at-a-time", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                List<String> log = new ArrayList<>();
                List.of(1, 2, 3).stream()
                    .filter(x -> { log.add("f" + x); return x % 2 == 1; })
                    .map(x -> { log.add("m" + x); return x; })
                    .collect(Collectors.toList());
                System.out.println(log);
            }
        }
    ''', "[f1, m1, f2, f3, m3]", ["[f1, f2, f3, m1, m3]", "[f1, m1, f2, m2, f3, m3]",
                                  "[m1, f1, f2, m3, f3]"],
      "A stream sends one element at a time through the whole pipeline",
      """The stages are fused, not run one after another over the whole list. Element 1 passes the filter and goes
      straight to map; 2 is rejected by the filter and never reaches map; then 3 goes through both."""),

    q("stream-without-terminal", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> log = new ArrayList<>();
                var s = List.of(1, 2).stream().peek(x -> log.add("p" + x));
                log.add("built");
                s.forEach(x -> log.add("e" + x));
                System.out.println(log);
            }
        }
    ''', "[built, p1, e1, p2, e2]", ["[p1, p2, built, e1, e2]", "[built, p1, p2, e1, e2]",
                                     "[p1, e1, p2, e2, built]"],
      "Nothing in a stream pipeline runs until a terminal operation is called",
      """`peek` is an intermediate step, so building the stream only records it; "built" is logged first. When
      `forEach` finally pulls elements, each one flows through peek and then the consumer, one at a time."""),
)
