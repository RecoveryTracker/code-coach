"""Gotchas, Java: run with the source launcher; portability notes are in langs.py (the `java` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("java")

ITEMS: tuple[Item, ...] = (
    q("integer-cache", r'''
        public class Main {
            public static void main(String[] args) {
                Integer a = 127, b = 127;
                Integer c = 128, d = 128;
                System.out.println((a == b) + " " + (c == d));
            }
        }
    ''', "true false", ["true true", "false false", "false true"],
      "== on boxed Integers compares objects, and only -128..127 are shared",
      """Autoboxing uses `Integer.valueOf`, which hands back the same cached object for values from -128 to 127 and
      a new object for anything else. So `a == b` is true by luck of the cache and `c == d` is false. Compare
      boxed numbers with `equals`."""),

    q("char-addition", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println('a' + 'b' + "c");
            }
        }
    ''', "195c", ["abc", "a98c", "97bc"],
      "Two chars added are an int; only then does the string join in",
      """`+` works left to right. `'a' + 'b'` is numeric addition of the char codes 97 and 98, giving the int 195,
      and only then is `195 + "c"` string concatenation. Start with an empty string, `"" + 'a' + 'b'`, to get
      letters."""),

    q("string-identity", r'''
        public class Main {
            public static void main(String[] args) {
                String a = "hi";
                String b = new String("hi");
                System.out.println((a == b) + " " + a.equals(b) + " "
                    + (a == b.intern()));
            }
        }
    ''', "false true true", ["true true true", "false true false", "false false true"],
      "== compares references; equals compares contents",
      """The literal "hi" lives in the string pool, while `new String("hi")` always makes a separate object, so
      `a == b` is false even though the characters match. `intern()` returns the pooled copy, which is the very
      object `a` points at."""),
)
