"""Gotchas, Java, the third helping: modern syntax, collection details and a few surprising library corners.

Same rules as content_java.py: single file, `public class Main` first with a static main (JDK 21 source launcher),
one printed line, nothing from the clock, randomness, hashing or HashMap iteration order. Helper classes nest inside
Main or sit after it, because the launcher runs the first class in the file. New ground compared with the second
deck: switch expressions and patterns, records, try-with-resources, text blocks, stream barriers, TreeMap and
LinkedHashMap behaviour, and the regex-flavoured String methods.
"""

from __future__ import annotations

from .items import Item, make

q = make("java")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ───────────────────────────────────────────────────────
    q("arrow-switch-no-fallthrough", r'''
        public class Main {
            public static void main(String[] args) {
                int n = 1;
                StringBuilder sb = new StringBuilder();
                switch (n) {
                    case 1 -> sb.append("a");
                    case 2 -> sb.append("b");
                    default -> sb.append("c");
                }
                System.out.println(sb);
            }
        }
    ''', "a", ["abc", "ab", "c"],
      "A switch with arrows runs one branch and never falls through",
      """The classic `case 1:` form runs on into the next label unless there is a `break`. The arrow form is a
      different construct: only the matching branch executes, so nothing needs a `break`."""),

    q("put-returns-previous-value", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<String, Integer> m = new TreeMap<>();
                System.out.println(m.put("a", 1) + " " + m.put("a", 2) + " "
                    + m.putIfAbsent("a", 3) + " " + m.get("a"));
            }
        }
    ''', "null 1 2 2", ["null 1 3 3", "1 2 2 2", "null null null 2"],
      "put and putIfAbsent return the old value, not the new one",
      """The first `put` finds nothing and returns null, the second returns the 1 it replaced. `putIfAbsent` leaves
      the existing 2 in place and returns it, so the final `get` is still 2."""),

    q("unmodifiable-view-versus-copy", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> base = new ArrayList<>(List.of(1));
                List<Integer> view = Collections.unmodifiableList(base);
                List<Integer> copy = List.copyOf(base);
                base.add(2);
                System.out.println(view.size() + " " + copy.size());
            }
        }
    ''', "2 1", ["1 1", "2 2", "1 2"],
      "unmodifiableList is a read-only view of the original; copyOf is a snapshot",
      """The view only blocks writes through itself and still reflects changes made to `base`, so it sees 2
      elements. `List.copyOf` made an independent immutable copy while the list still had one."""),

    q("sort-keeps-ties-in-order", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> l = Arrays.asList("bb", "a", "cc", "d", "ab");
                l.sort(Comparator.comparingInt(String::length));
                System.out.println(l);
            }
        }
    ''', "[a, d, bb, cc, ab]", ["[a, d, ab, bb, cc]", "[d, a, bb, cc, ab]", "[a, d, ab, cc, bb]"],
      "List.sort is stable: equal keys keep their original order",
      """Only the length is compared, so "a" and "d" tie, and so do "bb", "cc" and "ab". A stable sort leaves each
      tied group in the order it started in; it does not fall back to alphabetical."""),

    q("string-chars-are-ints", r'''
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                String s = "ab";
                System.out.println(s.chars().mapToObj(c -> String.valueOf(c))
                    .collect(Collectors.joining(",")) + " " + s.chars().sum());
            }
        }
    ''', "97,98 195", ["a,b 195", "97,98 98", "a,b ab"],
      "String.chars() is an IntStream of code units, not of chars",
      """The elements are ints, so `String.valueOf(c)` picks the `valueOf(int)` overload and prints the numbers 97
      and 98. Their sum is 195. A `(char) c` cast would be needed to get letters back."""),

    q("enum-sorts-by-ordinal", r'''
        import java.util.*;

        public class Main {
            enum L {
                LOW(5), MID(1), HIGH(3);
                final int w;
                L(int w) { this.w = w; }
            }

            public static void main(String[] args) {
                Set<L> s = new TreeSet<>(List.of(L.HIGH, L.LOW, L.MID));
                System.out.println(s);
            }
        }
    ''', "[LOW, MID, HIGH]", ["[MID, HIGH, LOW]", "[HIGH, LOW, MID]", "[HIGH, MID, LOW]"],
      "An enum's natural order is its declaration order, whatever fields it has",
      """Enums implement `Comparable` by ordinal, the position in the declaration. The weights 5, 1 and 3 play no
      part, and neither does the order the values were inserted."""),

    q("optional-orelse-is-eager", r'''
        import java.util.*;

        public class Main {
            static int calls = 0;
            static String fallback() { calls++; return "d"; }

            public static void main(String[] args) {
                Optional<String> o = Optional.of("x");
                String a = o.orElse(fallback());
                String b = o.orElseGet(Main::fallback);
                System.out.println(a + b + " " + calls);
            }
        }
    ''', "xx 1", ["xx 0", "xx 2", "xd 1"],
      "orElse evaluates its argument even when the Optional has a value",
      """Arguments are evaluated before the call, so `fallback()` runs for `orElse` although its result is thrown
      away. `orElseGet` takes a supplier and only calls it for an empty Optional, so the count is 1."""),

    q("double-to-string-forms", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(1e7 + " " + 1e6 + " " + 0.001 + " " + 0.0001);
            }
        }
    ''', "1.0E7 1000000.0 0.001 1.0E-4",
      ["10000000.0 1000000.0 0.001 0.0001", "1.0E7 1.0E6 0.001 1.0E-4",
       "1.0E7 1000000.0 1.0E-3 1.0E-4"],
      "Double.toString switches to scientific notation at 10^7 and below 10^-3",
      """Values from 0.001 up to but not including 10,000,000 print in plain decimal form. Outside that window the
      text is like 1.0E7, with the capital E and the mantissa always showing a decimal point."""),

    q("add-exact-reports-overflow", r'''
        public class Main {
            public static void main(String[] args) {
                int big = Integer.MAX_VALUE;
                String msg;
                try {
                    msg = "" + Math.addExact(big, 1);
                } catch (ArithmeticException e) {
                    msg = e.getMessage();
                }
                System.out.println((big + 1) + " " + msg);
            }
        }
    ''', "-2147483648 integer overflow",
      ["-2147483648 -2147483648", "2147483648 integer overflow", "integer overflow integer overflow"],
      "Plain + wraps silently; Math.addExact throws instead",
      """`big + 1` wraps around to the minimum int with no warning. The `*Exact` methods check the result and throw
      an `ArithmeticException` whose message is "integer overflow"."""),

    q("record-compact-constructor", r'''
        public class Main {
            record P(int x, int y) {
                P {
                    if (x < 0) x = 0;
                }
            }

            public static void main(String[] args) {
                P p = new P(-5, 2);
                System.out.println(p + " " + p.equals(new P(0, 2)));
            }
        }
    ''', "P[x=0, y=2] true", ["P[x=-5, y=2] false", "P[x=0, y=2] false", "P[x=-5, y=2] true"],
      "A compact constructor can reassign its parameters before the fields are set",
      """The body runs first, with `x` and `y` as ordinary parameters, and the fields are assigned from them at the
      end. Assigning `x = 0` therefore changes what is stored, and equality compares the stored fields."""),

    q("stringbuilder-edit-chain", r'''
        public class Main {
            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder("abcde");
                sb.insert(2, "XY").reverse().deleteCharAt(0);
                System.out.println(sb);
            }
        }
    ''', "dcYXba", ["XYabcde", "edcYXba", "dcXYba"],
      "StringBuilder edits in place, and each step sees the result of the one before",
      """insert gives "abXYcde". reverse flips the whole thing, so XY becomes YX and the text is "edcYXba". The
      last call removes the first character, the e."""),

    q("insert-char-plus-int", r'''
        public class Main {
            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder("ab");
                sb.insert(0, 'c' + 1).append((char) ('c' + 1));
                System.out.println(sb);
            }
        }
    ''', "100abd", ["dabd", "100ab100", "cabd"],
      "'c' + 1 is an int, so insert adds the number 100; the cast keeps it a char",
      """Adding an int to a char gives an int, and `insert(int, int)` writes the decimal digits "100". For
      `append`, the explicit `(char)` cast picks the char overload and adds the letter d."""),

    q("inner-class-shadowing", r'''
        public class Main {
            int x = 1;

            class In {
                int x = 2;
                int sum(int x) { return x + this.x * 10 + Main.this.x * 100; }
            }

            public static void main(String[] args) {
                Main m = new Main();
                System.out.println(m.new In().sum(3));
            }
        }
    ''', "123", ["6", "321", "33"],
      "Three variables called x: the parameter, this.x and Outer.this.x",
      """A bare `x` is the parameter, `this.x` is the inner object's field and `Main.this.x` is the field of the
      enclosing object. That is 3 + 2 * 10 + 1 * 100, which is 123."""),

    q("array-class-names", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(new int[0].getClass().getName() + " "
                    + new String[0][0].getClass().getSimpleName());
            }
        }
    ''', "[I String[][]", ["int[] String[][]", "[I [[String", "[I String[]"],
      "getName gives the JVM's internal array name; getSimpleName reads like source",
      """The binary name of `int[]` is "[I", one bracket per dimension plus a type letter. `getSimpleName` prints
      the source-like `String[][]`."""),

    q("compound-plus-groups-first", r'''
        public class Main {
            public static void main(String[] args) {
                String a = "a";
                a += 1 + 2;
                String b = "a" + 1 + 2;
                System.out.println(a + " " + b);
            }
        }
    ''', "a3 a12", ["a12 a12", "a3 a3", "a12 a3"],
      "In s += expr, the whole right side is computed first",
      """`a += 1 + 2` means `a = a + (1 + 2)`, so the numbers are added to 3 before they meet the string. In the
      second line the `+` operators run left to right, so each digit is appended as text."""),

    # ── Medium and hard ────────────────────────────────────────────────────
    q("old-switch-default-in-the-middle", r'''
        public class Main {
            static String f(int n) {
                String s = "";
                switch (n) {
                    case 1: s += "1";
                    default: s += "d";
                    case 2: s += "2"; break;
                    case 3: s += "3";
                }
                return s;
            }

            public static void main(String[] args) {
                System.out.println(f(1) + " " + f(5) + " " + f(2) + " " + f(3));
            }
        }
    ''', "1d2 d2 2 3", ["1d2 d 2 3", "1 d 2 3", "1d2 d2 2 3d2"],
      "default may sit anywhere; it runs when nothing matches, and then falls through",
      """The labels are checked first and `default` is taken only if none match, but execution continues from
      wherever it jumped in. So 5 starts at `default`, adds "d", falls into case 2, adds "2" and hits `break`."""),

    q("interface-diamond-most-specific", r'''
        public class Main {
            interface A { default String hi() { return "A"; } }
            interface B extends A { default String hi() { return "B"; } }
            interface C extends A {}
            static class D implements B, C {}

            public static void main(String[] args) {
                System.out.println(new D().hi());
            }
        }
    ''', "B", ["A", "AB", "Error"],
      "With default methods, the most specific interface wins; no conflict arises here",
      """B overrides A's default, and C simply inherits A's. Because B is more specific than A, B's version is the
      only candidate left, so D compiles and uses it. An error needs two unrelated interfaces with the same default."""),

    q("try-with-resources-order", r'''
        public class Main {
            static StringBuilder log = new StringBuilder();

            static class R implements AutoCloseable {
                final String n;
                R(String n) { this.n = n; log.append("open" + n + " "); }
                public void close() { log.append("close" + n + " "); }
            }

            public static void main(String[] args) {
                try (R a = new R("A"); R b = new R("B")) {
                    log.append("body ");
                }
                System.out.println(log.toString().trim());
            }
        }
    ''', "openA openB body closeB closeA",
      ["openA openB body closeA closeB", "openA openB closeB closeA body",
       "openA body closeA openB closeB"],
      "Resources open in order and close in reverse, after the body",
      """Like nested try blocks, the last resource opened is the first closed. The close calls happen when the
      body finishes, so `body` is logged before either of them."""),

    q("treemap-floor-and-ceiling", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                TreeMap<Integer, String> m = new TreeMap<>();
                m.put(10, "a"); m.put(20, "b"); m.put(30, "c");
                System.out.println(m.floorKey(25) + " " + m.ceilingKey(25) + " "
                    + m.floorKey(5) + " " + m.headMap(20).size() + " "
                    + m.headMap(20, true).size());
            }
        }
    ''', "20 30 null 1 2", ["30 20 null 1 2", "20 30 5 1 2", "20 30 null 2 2"],
      "floorKey is the greatest key <= x, ceilingKey the least key >= x; headMap excludes the bound",
      """For 25 the neighbours are 20 below and 30 above. Nothing is at or below 5, so `floorKey` returns null.
      `headMap(20)` is exclusive and holds only 10, while `headMap(20, true)` includes 20 as well."""),

    q("sorted-is-a-barrier", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                List<String> log = new ArrayList<>();
                Stream.of(3, 1, 2)
                    .peek(x -> log.add("p" + x))
                    .sorted()
                    .forEach(x -> log.add("f" + x));
                System.out.println(String.join(" ", log));
            }
        }
    ''', "p3 p1 p2 f1 f2 f3",
      ["p3 f3 p1 f1 p2 f2", "p1 p2 p3 f1 f2 f3", "p3 p1 p2 f3 f1 f2"],
      "Streams process one element at a time, except at sorted(), which needs them all",
      """Elements normally flow through the whole pipeline one by one. `sorted()` cannot emit anything until it
      has seen every element, so all three `peek` calls run first, and then `forEach` gets the sorted values."""),

    q("linkedhashmap-access-order", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<String, Integer> m = new LinkedHashMap<>(16, 0.75f, true);
                m.put("a", 1); m.put("b", 2); m.put("c", 3);
                m.get("a");
                m.put("b", 9);
                System.out.println(m.keySet());
            }
        }
    ''', "[c, a, b]", ["[a, b, c]", "[b, c, a]", "[a, c, b]"],
      "With accessOrder true, every get and put of an existing key moves it to the end",
      """The map starts as a, b, c. `get("a")` moves a to the back, giving b, c, a, and updating b with `put`
      counts as an access too, which leaves c, a, b. This is how an LRU cache is built."""),

    q("text-block-indentation", r'''
        public class Main {
            public static void main(String[] args) {
                String t = """
                    a
                      b
                  """;
                System.out.println(t.length());
            }
        }
    ''', "10", ["6", "5", "14"],
      "A text block strips the indentation common to all lines, the closing delimiter included",
      """The closing quotes sit two columns left of the text, and that line counts when the common indentation is
      worked out. So only 10 spaces are removed, leaving "  a\\n    b\\n", which is 10 characters."""),

    q("pattern-switch-guards", r'''
        public class Main {
            static String f(Object o) {
                return switch (o) {
                    case null -> "nil";
                    case Integer i when i > 3 -> "big";
                    case Integer i -> "small";
                    case String s -> "str" + s.length();
                    default -> "other";
                };
            }

            public static void main(String[] args) {
                System.out.println(f(7) + " " + f(3) + " " + f("hey")
                    + " " + f(null));
            }
        }
    ''', "big small str3 nil", ["big big str3 nil", "big small str3 other", "big small str3 NPE"],
      "Cases are tried in order, a guard can reject a match, and case null must be written out",
      """3 is an Integer but fails `i > 3`, so it falls to the next case and is "small". A pattern switch throws a
      NullPointerException on null unless it has a `case null`, which this one does."""),

    q("array-rows-shared-by-fill", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                int[][] a = new int[2][2];
                int[][] b = new int[2][];
                Arrays.fill(b, new int[2]);
                a[0][0] = 1;
                b[0][0] = 1;
                System.out.println(a[1][0] + " " + b[1][0]);
            }
        }
    ''', "0 1", ["0 0", "1 1", "1 0"],
      "Arrays.fill stores the same array object in every slot",
      """`new int[2][2]` allocates a separate row for each slot. `Arrays.fill(b, new int[2])` evaluates `new int[2]`
      once and stores that one row in both slots, so writing through row 0 changes row 1."""),

    q("strip-versus-trim", r'''
        public class Main {
            public static void main(String[] args) {
                String s = "\u2003a\u2003";
                System.out.println(s.trim().length() + " " + s.strip().length());
            }
        }
    ''', "3 1", ["1 1", "3 3", "1 3"],
      "trim removes characters up to U+0020; strip removes all Unicode whitespace",
      """An em space (U+2003) is whitespace by Unicode but is above U+0020, so `trim` leaves it. `strip`, added in
      Java 11, uses `Character.isWhitespace` and removes both."""),

    q("byte-compound-unsigned-shift", r'''
        public class Main {
            public static void main(String[] args) {
                byte b = (byte) 0xF0;
                int c = (b & 0xFF) >>> 4;
                b >>>= 4;
                System.out.println(b + " " + c);
            }
        }
    ''', "-1 15", ["15 15", "-1 -1", "0 15"],
      ">>> works on the promoted int, so a negative byte shifts in 1-bits before narrowing",
      """The byte -16 is first widened to the int 0xFFFFFFF0. Shifting that right by 4 gives 0x0FFFFFFF, and the
      compound assignment narrows it back to a byte, keeping only 0xFF, which is -1. Masking with `& 0xFF` first
      gives the unsigned 15."""),

    q("try-with-resources-suppressed", r'''
        public class Main {
            static class R implements AutoCloseable {
                public void close() { throw new IllegalStateException("close"); }
            }

            public static void main(String[] args) {
                try (R r = new R()) {
                    throw new RuntimeException("body");
                } catch (Exception e) {
                    Throwable[] sup = e.getSuppressed();
                    System.out.println(e.getMessage() + " " + sup.length + " "
                        + sup[0].getMessage());
                }
            }
        }
    ''', "body 1 close", ["close 0 body", "body 0 close", "close 1 body"],
      "An exception from close() is attached to the body's exception, not thrown over it",
      """If the body already failed, the resource's own failure would hide it, so Java keeps the first exception
      and records the second in `getSuppressed()`. The `catch` therefore sees "body"."""),

    q("list-of-rejects-null-queries", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                String a;
                try {
                    a = "" + List.of(1, 2).contains(null);
                } catch (NullPointerException e) {
                    a = "NPE";
                }
                System.out.println(a + " " + Arrays.asList(1, 2).contains(null));
            }
        }
    ''', "NPE false", ["false false", "NPE NPE", "false true"],
      "The immutable List.of collections throw even when you merely ask whether null is inside",
      """`List.of` forbids null elements, and its `contains` enforces that by throwing a NullPointerException for
      a null argument. `Arrays.asList` is an ordinary list and answers false."""),

    q("to-map-duplicate-key", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                try {
                    Stream.of("a", "bb", "c")
                        .collect(Collectors.toMap(String::length, s -> s));
                } catch (IllegalStateException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', "Duplicate key 1 (attempted merging values a and c)",
      ["Duplicate key 1", "Duplicate key 1 (attempted merging values c and a)", "Duplicate key 2"],
      "Collectors.toMap throws on a repeated key unless you give it a merge function",
      """"a" and "c" both have length 1, so the second one collides with the first. The message names the key and
      the two values, old first, new second. A third argument such as `(x, y) -> y` would resolve it."""),

    q("sharp-s-uppercases-to-two", r'''
        import java.util.Locale;

        public class Main {
            public static void main(String[] args) {
                String up = "\u00df".toUpperCase(Locale.ROOT);
                int c = Character.toUpperCase('\u00df');
                System.out.println(up.length() + " " + c);
            }
        }
    ''', "2 223", ["1 223", "1 7838", "2 7838"],
      "String.toUpperCase can change the length; Character.toUpperCase maps one char to one char",
      """The German sharp s has no single-character capital in the Unicode case mapping used here, so the String
      method gives "SS", two characters. The char method cannot do that and returns the character unchanged."""),

    q("collections-rotate-direction", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> l = new ArrayList<>(List.of(1, 2, 3, 4));
                Collections.rotate(l, 1);
                String a = l.toString();
                Collections.rotate(l, -2);
                System.out.println(a + " " + l);
            }
        }
    ''', "[4, 1, 2, 3] [2, 3, 4, 1]",
      ["[2, 3, 4, 1] [4, 1, 2, 3]", "[2, 3, 4, 1] [3, 4, 1, 2]", "[4, 1, 2, 3] [3, 4, 1, 2]"],
      "A positive rotation moves elements toward the end; a negative one toward the front",
      """`rotate(l, 1)` pushes the last element round to the front, giving 4, 1, 2, 3. Rotating that by -2 moves
      two elements from the front to the back, which leaves 2, 3, 4, 1."""),

    q("binary-search-not-found", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                int[] a = {1, 3, 5};
                System.out.println(Arrays.binarySearch(a, 3) + " "
                    + Arrays.binarySearch(a, 4) + " " + Arrays.binarySearch(a, 0)
                    + " " + Arrays.binarySearch(a, 9));
            }
        }
    ''', "1 -3 -1 -4", ["1 -1 -1 -1", "1 -2 -1 -3", "1 -3 0 -4"],
      "A miss returns -(insertion point) - 1, so it is never 0 or positive",
      """4 would be inserted at index 2, giving -3. 0 belongs at index 0, giving -1, and 9 at index 3, giving -4.
      The minus one is there so that a miss at index 0 cannot be confused with a hit at index 0."""),

    q("split-takes-a-regex", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println("a.b.c".split(".").length + " "
                    + "a.b.c".split("\\.").length + " " + "a|b".split("|").length);
            }
        }
    ''', "0 3 3", ["3 3 2", "1 3 2", "0 3 2"],
      "split's argument is a regular expression: '.' matches everything and '|' matches nothing",
      """With the pattern `.` every character is a separator, leaving only empty strings, which `split` drops, so
      the length is 0. `\\\\.` is a literal dot. The pattern `|` is two empty alternatives, so it splits between
      every character: a, |, b."""),

    q("short-set-remove-misses", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Set<Short> s = new LinkedHashSet<>();
                for (short i = 0; i < 5; i++) {
                    s.add(i);
                    s.remove(i - 1);
                }
                System.out.println(s.size());
            }
        }
    ''', "5", ["1", "0", "4"],
      "i - 1 is an int, so remove looks for an Integer that no Short ever equals",
      """`add(i)` boxes a Short, but `remove(Object)` receives the boxed result of the int expression `i - 1`.
      A `Short` is never equal to an `Integer`, so nothing is removed and all five stay."""),

    q("lambda-this-versus-anonymous", r'''
        public class Main {
            String got = "";

            void go() {
                Runnable a = new Runnable() {
                    public void run() { got += this.getClass().getName() + " "; }
                };
                Runnable l = () -> got += this.getClass().getName();
                a.run();
                l.run();
                System.out.println(got);
            }

            public static void main(String[] args) { new Main().go(); }
        }
    ''', "Main$1 Main", ["Main Main", "Main$1 Main$1", "Main$1 Main$$Lambda"],
      "Inside a lambda, this is the enclosing object; inside an anonymous class it is the new object",
      """An anonymous class is a class of its own, named Main$1 by the compiler, so its `this` is an instance of
      that. A lambda does not introduce a new `this`, so it still means the `Main` that called `go`."""),

    q("parse-int-accepts-plus", r'''
        public class Main {
            public static void main(String[] args) {
                String r;
                try {
                    r = "" + Integer.parseInt(" 5");
                } catch (NumberFormatException e) {
                    r = e.getMessage();
                }
                int p = Integer.parseInt("+5");
                System.out.println(p + " " + Integer.parseInt("-0") + " " + r);
            }
        }
    ''', '5 0 For input string: " 5"', ['5 0 5', '5 -0 For input string: " 5"', '5 0 For input string: 5'],
      "parseInt takes a leading + but not spaces",
      """A sign of either kind is allowed, and `-0` is just the int 0. Whitespace is not trimmed, so " 5" fails
      and the exception message quotes the input."""),

    q("array-index-evaluated-first", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                int i = 0;
                int[] a = {0, 0, 0};
                a[i] = i = 2;
                System.out.println(Arrays.toString(a) + " " + i);
            }
        }
    ''', "[2, 0, 0] 2", ["[0, 0, 2] 2", "[0, 0, 0] 2", "[2, 0, 0] 0"],
      "Java evaluates the array and index on the left before the right side runs",
      """The left operand `a[i]` is resolved first, with i still 0. Then `i = 2` runs and yields 2, which is stored
      in `a[0]`. Unlike C, this order is fixed by the language."""),

    q("round-float-versus-double", r'''
        public class Main {
            public static void main(String[] args) {
                Object f = Math.round(2.5f);
                Object d = Math.round(2.5);
                System.out.println(f.getClass().getSimpleName() + " "
                    + d.getClass().getSimpleName() + " " + Math.round(-2.5));
            }
        }
    ''', "Integer Long -2", ["Integer Integer -3", "Long Long -2", "Integer Long -3"],
      "Math.round returns int for a float and long for a double, and rounds halves up",
      """The two overloads differ in return type, which shows once the result is boxed. Half values round toward
      positive infinity, so 2.5 becomes 3 but -2.5 becomes -2."""),

    q("double-remainder", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(5.5 % 2 + " " + -5.5 % 2 + " " + 5 % 0.0);
            }
        }
    ''', "1.5 -1.5 NaN", ["1.5 0.5 NaN", "1.5 -1.5 Infinity", "1.5 -1.5 ArithmeticException"],
      "% works on doubles, takes the sign of the left side, and gives NaN for a zero divisor",
      """The remainder keeps the sign of the dividend, so -5.5 % 2 is -1.5. Unlike int `%`, a floating-point
      remainder by zero does not throw; it is NaN."""),

    q("nulls-first-then-reversed", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Comparator<String> nat = Comparator.naturalOrder();
                List<String> x = Arrays.asList("b", null, "a");
                List<String> y = Arrays.asList("b", null, "a");
                x.sort(Comparator.nullsLast(nat).reversed());
                y.sort(Comparator.nullsLast(nat.reversed()));
                System.out.println(x + " " + y);
            }
        }
    ''', "[null, b, a] [b, a, null]", ["[b, a, null] [null, b, a]", "[b, a, null] [b, a, null]",
                                       "[null, b, a] [null, b, a]"],
      "reversed() flips the whole comparator, including where the nulls go",
      """`nullsLast(nat).reversed()` reverses the null rule as well, so null comes first. Reversing only the inner
      comparator, `nullsLast(nat.reversed())`, keeps the nulls at the end."""),
)
