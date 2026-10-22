"""Gotchas, C# (third deck): top-level statements run by `dotnet run`; notes are in langs.py (the `csharp` entry).

Same rules as content_csharp2.py: warning-free (any compiler warning lands in stdout and breaks the card), doubles
and decimals printed through `FormattableString.Invariant`, strings compared ordinally, no hash codes, no clock, no
default `ToString()` of an object, nothing that races. This deck is the string and number library, patterns and
records, the LINQ operators, and the ordering rules for `finally`, `using` and property initialisers.
"""

from __future__ import annotations

from .items import Item, make

q = make("csharp")

ITEMS: tuple[Item, ...] = (
    # ── Batch 1: strings, numbers, patterns ────────────────────────────────
    q("substring-at-the-end-is-empty", r'''
        string s = "hello";
        Console.WriteLine("[" + s.Substring(5) + "] " + s.Substring(1, 3) + " "
            + s[^2..] + " " + s.Substring(2, 0).Length);
    ''', "[] ell lo 0", ["[o] ell lo 0", "[] ell lo 1", "[] el lo 0"],
      "Substring(start) with start equal to the length is legal and gives an empty string",
      """The start may be anywhere from 0 up to and including the length; only beyond it is an error.
      The second argument is a length, not an end index, so `Substring(1, 3)` is "ell". `[^2..]` is the last two."""),

    q("join-treats-null-as-empty", r'''
        Console.WriteLine(string.Join("-", "a", null, "c") + "|"
            + string.Join("-", new string?[] { null, null }) + "|"
            + string.Join("-", new List<int>()) + "|");
    ''', "a--c|-||", ["a-c|-||", "a--c|||", "a-null-c|null-null|"],
      "A null element joins as an empty string, but the separator is still written",
      """The null in the middle contributes no text, yet there is still one separator on each side of
      it, so you get "a--c". Two nulls give one lone separator, and an empty list gives an empty string."""),

    q("split-remove-empty-keeps-a-space", r'''
        string s = "a, ,b";
        var plain = s.Split(',', StringSplitOptions.RemoveEmptyEntries);
        var trimmed = s.Split(',', StringSplitOptions.RemoveEmptyEntries
            | StringSplitOptions.TrimEntries);
        Console.WriteLine(plain.Length + " " + trimmed.Length + " ["
            + string.Join("|", plain) + "]");
    ''', "3 2 [a| |b]", ["2 2 [a|b]", "3 3 [a| |b]", "3 2 [a|b]"],
      "RemoveEmptyEntries only removes truly empty pieces; a piece of spaces is not empty",
      """The middle piece is a single space, so it survives. Adding `TrimEntries` trims each piece first
      (the space becomes ""), and then the empty one is removed, leaving two pieces."""),

    q("padleft-never-truncates", r'''
        Console.WriteLine("abc".PadLeft(2) + "|" + "7".PadLeft(3, '0') + "|"
            + "xxhixx".Trim('x') + "|" + "x".PadRight(3, '.') + "|");
    ''', "abc|007|hi|x..|", ["ab|007|hi|x..|", "abc|700|hi|x..|", "abc|007|xxhixx|x..|"],
      "PadLeft pads up to a total width and never cuts a longer string",
      """The number is the total width wanted, so a string that is already longer is returned as it
      is. `Trim('x')` removes every leading and trailing x, and `PadRight` adds the dots after."""),

    q("replace-does-not-overlap-or-rescan", r'''
        Console.WriteLine("aaaa".Replace("aa", "b") + " " + "aaa".Replace("aa", "b")
            + " " + "abab".Replace("ab", "ba"));
    ''', "bb ba baba", ["bbb ba baba", "bb bb baba", "bb ba abab"],
      "Replace scans left to right, never overlaps matches, and never re-reads its own output",
      """In "aaa" the first two a's match and the last one is left over, giving "ba". "aaaa" has two
      separate matches, giving "bb". "abab" becomes "baba": the new text is not searched again."""),

    q("char-digit-arithmetic", r'''
        string d = "7";
        Console.WriteLine((d[0] - '0') + " " + (d[0] + 1) + " " + (char)(d[0] + 1)
            + " " + (d[0] == 7));
    ''', "7 56 8 False", ["7 8 8 True", "55 56 8 False", "7 56 56 False"],
      "A char is a number underneath: subtraction and addition give ints, and '7' is 55",
      """`'7' - '0'` is 55 - 48 = 7, an int. `'7' + 1` is the int 56, and only the cast turns it back into
      the character '8'. Comparing `'7'` with the int 7 compares 55 with 7."""),

    q("decimal-does-not-fix-thirds", r'''
        decimal d = 1m / 3m * 3m;
        double f = 1.0 / 3 * 3;
        Console.WriteLine(FormattableString.Invariant(
            $"{d} {f} {d == 1m} {f == 1.0}"));
    ''', "0.9999999999999999999999999999 1 False True",
    ["1 1 True True", "0.9999999999999999999999999999 0.9999999999999999 False False",
     "0.3333333333333333333333333333 1 False True"],
      "decimal is exact for decimal fractions, not for thirds; here the double happens to round to 1",
      """A decimal keeps 28 digits of 1/3, so multiplying back by 3 gives 28 nines, not 1. The double
      version looks exact only because the tiny error rounds away when it is multiplied by 3."""),

    q("null-coalescing-assignment-and-null-math", r'''
        int? a = null;
        a ??= 5;
        a ??= 9;
        int? b = null;
        b++;
        int? c = null;
        c += 2;
        Console.WriteLine(a + " " + (b is null) + " " + (c is null));
    ''', "5 True True", ["9 True True", "5 False False", "5 True False"],
      "`??=` assigns only when null, and arithmetic on a null int? stays null",
      """`a ??= 5` stores 5, and the second `??=` finds a value and does nothing. Incrementing or adding
      to a null `int?` does not make it 1 or 2: any arithmetic with null gives null."""),

    q("property-pattern-on-null-is-false", r'''
        string? s = null;
        string t = "";
        Console.WriteLine((s is { Length: 0 }) + " "
            + (s is not { Length: 0 }) + " " + (t is { Length: 0 }) + " "
            + (s?.Length == 0));
    ''', "False True True False", ["False False True False", "True True True False",
                                  "False True True True"],
      "A property pattern never matches null, so its `not` always does",
      """`{ Length: 0 }` needs a real object, so it is false for null; `is not` is its exact opposite,
      so it is true. For `s?.Length == 0` the null makes the left side null, which is not equal to 0."""),

    q("list-pattern-arms-match-in-order", r'''
        static string Show(int[] a) => a switch {
            [] => "empty",
            [var x] => "one:" + x,
            [_, _] => "two",
            [var f, .. var rest] => "first" + f + "+" + rest.Length,
        };
        Console.WriteLine(Show([]) + " " + Show([5]) + " " + Show([1, 2]) + " "
            + Show([1, 2, 3, 4]));
    ''', "empty one:5 two first1+3", ["empty one:5 two first1+4", "empty one:5 first1+1 first1+3",
                                      "empty one:5 two two"],
      "In a list pattern `.. var rest` takes the middle, and the first arm that fits is used",
      """`[1, 2]` fits the `[_, _]` arm before it ever reaches the general one. For four items, the
      last arm matches with `f` = 1 and the slice `rest` = {2, 3, 4}, which has 3 elements."""),

    # ── Batch 2: records, structs, spans, LINQ ─────────────────────────────
    q("record-with-and-tostring", r'''
        var a = new P(1, 2);
        var b = a with { Y = 5 };
        Console.WriteLine(a + " " + b + " " + (a == b) + " " + (a == new P(1, 2)));

        record P(int X, int Y);
    ''', "P { X = 1, Y = 2 } P { X = 1, Y = 5 } False True",
    ["P(1, 2) P(1, 5) False True", "P { X = 1, Y = 2 } P { X = 1, Y = 5 } False False",
     "P { X = 1, Y = 5 } P { X = 1, Y = 5 } True True"],
      "A record prints its members by name, `with` makes a changed copy, and == compares values",
      """`with` leaves `a` alone and returns a new record with Y changed. The generated ToString looks like
      `P { X = 1, Y = 2 }`, and `==` compares the members, so a fresh `new P(1, 2)` equals `a`."""),

    q("with-is-a-shallow-copy", r'''
        var a = new Box("x", new List<int> { 1 });
        var b = a with { Name = "y" };
        b.Items.Add(2);
        Console.WriteLine(a.Name + a.Items.Count + " " + b.Name + b.Items.Count);

        record Box(string Name, List<int> Items);
    ''', "x2 y2", ["x1 y2", "x1 y1", "y2 y2"],
      "`with` copies the fields, so a list inside is still the same list",
      """The new record gets its own Name, but its Items field holds the very same List object. Adding
      through `b.Items` is therefore visible through `a.Items`, and both report a count of 2."""),

    q("struct-in-an-array-versus-a-list", r'''
        var arr = new P[1];
        arr[0].X = 5;
        var list = new List<P> { new P() };
        var copy = list[0];
        copy.X = 5;
        Console.WriteLine(arr[0].X + " " + list[0].X + " " + copy.X);

        struct P { public int X; }
    ''', "5 0 5", ["5 5 5", "0 0 5", "5 0 0"],
      "An array element is a variable you can change in place; a list indexer returns a copy",
      """`arr[0].X = 5` edits the struct stored in the array. `list[0]` hands back a copy of the struct,
      so changing `copy` leaves the list's element at 0 (and `list[0].X = 5` would not even compile)."""),

    q("ref-local-aliases-the-element", r'''
        int[] a = { 1, 2, 3 };
        ref int r = ref a[1];
        r += 19;
        int v = a[2];
        v = 99;
        Console.WriteLine(string.Join(",", a) + " " + r);
    ''', "1,21,3 21", ["1,2,3 21", "1,21,99 21", "1,21,3 2"],
      "A `ref` local is another name for the element; an ordinary local is a copy of it",
      """`r` refers to the slot `a[1]`, so `r += 19` changes the array to 21. `v` was only a copy of
      `a[2]`, so setting it to 99 changes nothing in the array."""),

    q("span-slice-writes-through", r'''
        int[] a = { 1, 2, 3, 4 };
        Span<int> s = a.AsSpan(1, 2);
        s[0] = 99;
        Span<int> t = s.Slice(1);
        t[0] = 0;
        int[] copy = s.ToArray();
        copy[0] = -1;
        Console.WriteLine(string.Join(",", a));
    ''', "1,99,0,4", ["1,2,3,4", "1,99,3,4", "1,-1,0,4"],
      "A Span is a window onto the array: writes go through, and only ToArray makes a copy",
      """`s` covers a[1..2], so `s[0] = 99` changes a[1]. `s.Slice(1)` is a smaller window, and
      `t[0] = 0` changes a[2]. `ToArray()` is a real copy, so changing it does nothing to `a`."""),

    q("second-orderby-replaces-the-first", r'''
        var w = new[] { "b2", "a2", "b1", "a1" };
        var x = w.OrderBy(s => s[0]).ThenBy(s => s[1]);
        var y = w.OrderBy(s => s[0]).OrderBy(s => s[1]);
        Console.WriteLine(string.Join(" ", x) + " | " + string.Join(" ", y));
    ''', "a1 a2 b1 b2 | a1 b1 a2 b2",
    ["a1 a2 b1 b2 | a1 a2 b1 b2", "a1 a2 b1 b2 | a2 a1 b2 b1", "a1 b1 a2 b2 | a1 a2 b1 b2"],
      "A second OrderBy starts a new sort; only ThenBy refines the first one",
      """`OrderBy(letter).ThenBy(digit)` sorts by letter and breaks ties by digit. A second `OrderBy`
      sorts by digit alone; the sort is stable, so equal digits stay in the earlier (letter) order."""),

    q("groupby-keeps-first-seen-order", r'''
        var words = new[] { "banana", "apple", "blueberry", "avocado", "cherry" };
        var g = words.GroupBy(s => s[0]);
        Console.WriteLine(string.Join(" ", g.Select(x => x.Key + ":" + x.Count()))
            + " " + string.Join(",", g.First()));
    ''', "b:2 a:2 c:1 banana,blueberry",
    ["a:2 b:2 c:1 banana,blueberry", "b:2 a:2 c:1 apple,avocado", "a:2 b:2 c:1 apple,avocado"],
      "GroupBy does not sort: groups appear in the order their keys first showed up",
      """The first word starts with b, so the b group comes first, and inside each group the items
      keep their original order. To get a, b, c you would have to add an `OrderBy` on the key."""),

    q("zip-stops-at-the-shorter-list", r'''
        var z = new[] { 1, 2, 3 }.Zip(new[] { "a", "b" }, (n, s) => n + s);
        Console.WriteLine(string.Join(",", z) + " " + z.Count());
    ''', "1a,2b 2", ["1a,2b,3 3", "1a,2b 3", "1a,2b,3a 3"],
      "Zip pairs items one by one and quietly ignores the extras of the longer sequence",
      """There are only two strings, so only two pairs are made: (1, "a") and (2, "b"). The 3 has no
      partner and is dropped, and nothing fails."""),

    q("aggregate-folds-from-the-left", r'''
        var v = new[] { 10, 2, 3 };
        Console.WriteLine(v.Aggregate((a, b) => a - b) + " "
            + v.Aggregate(100, (a, b) => a - b) + " "
            + v.Aggregate("", (acc, n) => n + acc));
    ''', "5 85 3210", ["5 85 1023", "15 85 3210", "-5 85 3210"],
      "Aggregate runs from the left; without a seed the first item is the starting value",
      """Without a seed it is (10 - 2) - 3 = 5. With the seed 100 it is ((100 - 10) - 2) - 3 = 85. The
      last lambda puts each new number in front of the text so far: "10", "210", "3210"."""),

    q("skip-and-take-never-throw", r'''
        var v = new[] { 1, 2, 3 };
        Console.WriteLine(v.Take(10).Count() + " " + v.Skip(5).Count() + " "
            + v.Skip(-1).Count() + " " + v.Take(-2).Count() + " "
            + v.Take(..2).Count());
    ''', "3 0 3 0 2", ["3 0 2 0 2", "10 0 3 0 2", "3 0 3 0 3"],
      "Take and Skip clamp their count: too many, too few and negative are all fine",
      """`Take(10)` gives what there is (3) and `Skip(5)` leaves nothing. A negative `Skip` skips none and a
      negative `Take` takes none. `Take(..2)` is the range form and takes the first two."""),

    # ── Batch 3: types, enums, finally, using, parsing ─────────────────────
    q("list-capacity-constructor-is-not-a-size", r'''
        var a = new List<int>(5);
        var b = new List<int>(new[] { 5 });
        Console.WriteLine(a.Count + " " + b.Count + " " + new int[5].Length + " "
            + a.Capacity);
    ''', "0 1 5 5", ["5 1 5 5", "0 5 5 5", "5 5 5 5"],
      "A number passed to List's constructor is a capacity: the list is still empty",
      """`new List<int>(5)` reserves room for 5 but holds nothing, so Count is 0. Passing a collection
      copies its items, so `new[] { 5 }` gives one element. Only an array's size makes 5 slots."""),

    q("explicit-interface-member-needs-the-interface", r'''
        var c = new C();
        I i = c;
        Console.WriteLine(c.Hi() + " " + i.Hi() + " " + ((I)c).Hi());

        interface I { string Hi(); }
        class C : I {
            public string Hi() => "C";
            string I.Hi() => "I";
        }
    ''', "C I I", ["C C C", "I I I", "C C I"],
      "An explicit interface implementation is only reachable through the interface type",
      """`c.Hi()` sees the public method. Once the object is viewed as an `I`, by a variable or a cast,
      the explicit `I.Hi` is the one that is called, regardless of what the object really is."""),

    q("as-and-is-with-a-boxed-double", r'''
        object o = 3.5;
        Console.WriteLine((o as string ?? "null") + " " + (o is double) + " "
            + (o is int) + " " + (o is IComparable) + " "
            + (o is double d && d > 3));
    ''', "null True False True True",
    ["null True True True True", "3.5 True False True True", "null True False False True"],
      "`as` gives null on a type mismatch, and `is int` is false for a boxed double",
      """The boxed value is a double, not a string, so `as string` gives null and falls to "null". It
      is not an int either (no conversion is tried), but double implements IComparable."""),

    q("enum-values-outside-the-list", r'''
        Color c = (Color)3;
        Console.WriteLine(c + " " + Enum.Parse<Color>("green", true) + " "
            + (Color)0 + " " + Enum.IsDefined(c) + " " + (Color.Red | Color.Green));

        enum Color { Red = 1, Green = 2 }
    ''', "3 Green 0 False 3",
    ["3 Green 0 False Red, Green", "3 Green None False 3", "3 Green 0 True 3"],
      "An enum can hold any number; without [Flags] one with no name prints as that number",
      """Casting 3 compiles and is not checked, and with no name for 3 (or 0) the value prints as a number.
      `Enum.IsDefined` says false for it. Only a `[Flags]` enum would spell `Red | Green` as "Red, Green"."""),

    q("default-of-each-type", r'''
        Console.WriteLine(default(int) + " " + default(bool) + " "
            + ReferenceEquals(default(string), null) + " "
            + (int)default(char) + " " + default((int, string)) + " "
            + default(int?).HasValue);
    ''', "0 False True 0 (0, ) False",
    ["0 false null 0 (0, null) False", "0 False True 0 (0, 0) False", "0 False True 0 (0, ) True"],
      "default is zero bits: 0, False, null, the character zero, and an int? with no value",
      """A reference type's default is null, so the tuple's string part is null and prints as nothing
      between the comma and the bracket. A nullable int's default is 'no value', so HasValue is False."""),

    q("finally-cannot-change-a-returned-value", r'''
        Console.WriteLine(T.F() + " " + T.Log);

        static class T {
            public static string Log = "";
            public static int F() {
                int x = 1;
                try { Log += "t"; return x; }
                finally { x = 99; Log += "f"; }
            }
        }
    ''', "1 tf", ["99 tf", "1 t", "99 t"],
      "The return value is taken before finally runs, so finally cannot change it",
      """`return x` copies the 1 aside, then `finally` runs: it sets the local to 99 and logs an f, but
      the copy is what the caller receives. `finally` always runs, so the log reads "tf"."""),

    q("using-declarations-dispose-in-reverse", r'''
        {
            using var a = new D("a");
            using var b = new D("b");
            D.Log += "body ";
        }
        Console.WriteLine(D.Log);

        class D(string name) : IDisposable {
            public static string Log = "";
            public void Dispose() { Log += name + " "; }
        }
    ''', "body b a", ["body a b", "a b body", "b a body"],
      "Using declarations are disposed when the scope ends, last one first",
      """The body runs first. At the closing brace the variables are disposed in the reverse order of
      their declaration, so `b` goes before `a`, like objects being unstacked."""),

    q("goto-case-jumps-to-a-label", r'''
        int n = 1;
        string s = "";
        switch (n) {
            case 1: s += "a"; goto case 3;
            case 2: s += "b"; break;
            case 3: s += "c"; break;
            default: s += "d"; break;
        }
        Console.WriteLine(s);
    ''', "ac", ["abc", "acd", "a"],
      "C# has no fall-through, but `goto case` jumps to another case on purpose",
      """Case 1 adds "a" and then jumps straight to case 3, skipping case 2 in the middle. Case 3
      adds "c" and breaks, so the default never runs."""),

    q("doubled-braces-are-literal-braces", r'''
        int x = 5;
        Console.WriteLine($"{{{x}}} {{x}} {x}" + " "
            + string.Format("{{0}} {0} {{{0}}}", x));
    ''', "{5} {x} 5 {0} 5 {5}",
    ["{5} {5} 5 {0} 5 {5}", "{5} {x} 5 5 5 5", "{{5}} {{x}} 5 {{0}} 5 {{5}}"],
      "`{{` and `}}` print one brace; a single pair around a name is the hole",
      """In `{{{x}}}` the outer doubled braces are literal and the inner pair is the value, so it
      gives `{5}`. `{{x}}` has no hole at all and prints `{x}`. Format strings use the same rule."""),

    q("int-parse-allows-spaces-not-commas", r'''
        bool ok1 = int.TryParse(" 42 ", out int a);
        bool ok2 = int.TryParse("1,000", out int b);
        bool ok3 = int.TryParse("+7", out int c);
        bool ok4 = int.TryParse("4 2", out int d);
        Console.WriteLine($"{ok1}{a} {ok2}{b} {ok3}{c} {ok4}{d}");
    ''', "True42 False0 True7 False0",
    ["True42 True1000 True7 False0", "False0 False0 True7 False0", "True42 False0 False0 False0"],
      "By default TryParse accepts surrounding spaces and a sign, but not a thousands separator",
      """White space around the number and a leading + or - are allowed. A comma or a space inside the
      digits is not, so those fail, and the out variable is set to 0 when it fails."""),

    # ── Batch 4: numbers, properties, equality ─────────────────────────────
    q("timespan-parts-versus-totals", r'''
        var t = TimeSpan.FromMinutes(150);
        Console.WriteLine(FormattableString.Invariant(
            $"{t.Hours} {t.Minutes} {t.TotalMinutes} {t.TotalHours} {t.Days} {t}"));
    ''', "2 30 150 2.5 0 02:30:00",
    ["150 30 150 2.5 0 02:30:00", "2 150 150 2.5 0 02:30:00", "2 30 150 2.5 0 2:30"],
      "Hours and Minutes are the parts of the clock face; TotalHours and TotalMinutes are everything",
      """150 minutes is 2 hours and 30 minutes, which is what `Hours` and `Minutes` report. The `Total...`
      properties convert the whole span into one unit: 150 minutes or 2.5 hours."""),

    q("nan-equals-itself-through-equals", r'''
        double a = double.NaN, b = double.NaN;
        Console.WriteLine((a == b) + " " + a.Equals(b) + " " + (a < 1) + " "
            + (a > 1) + " " + (a != b) + " " + double.IsNaN(a));
    ''', "False True False False True True",
    ["True True False False False True", "False False False False True True",
     "False True True False True True"],
      "== says NaN is not equal to anything, but Equals says it is equal to itself",
      """The operators follow IEEE rules, so every comparison with NaN is false except `!=`. `Equals` is
      meant for sorting and hashing, so it must be reflexive, and NaN.Equals(NaN) is true."""),

    q("shift-count-is-masked", r'''
        int one = 1;
        long big = 1;
        Console.WriteLine((one << 32) + " " + (one << 33) + " " + (big << 65) + " "
            + (-8 >> 1) + " " + (-8 >>> 1));
    ''', "1 2 2 -4 2147483644",
    ["0 0 0 -4 2147483644", "1 2 2 -4 -4", "0 0 2 -4 2147483644"],
      "Only the low 5 (int) or 6 (long) bits of a shift count are used; >>> ignores the sign",
      """`one << 32` uses the count 32 & 31 = 0, so nothing moves; 33 acts as 1. For a long the count is
      masked with 63, so 65 acts as 1. `>>` keeps the sign (-4), while `>>>` fills with zeros."""),

    q("expression-body-runs-every-read", r'''
        var c = new C();
        Console.WriteLine(c.Calc + " " + c.Calc + " " + c.Cached + " " + c.Cached);

        class C {
            static int count;
            public int Calc => ++count;
            public int Cached { get; } = ++count;
        }
    ''', "2 3 1 1", ["1 2 1 1", "2 3 2 3", "2 2 1 1"],
      "`=>` is a getter that runs on every read; `{ get; } = x` runs x once, at construction",
      """`new C()` runs the initialiser once: Cached becomes 1 and count is 1. Each read of `Calc` runs
      `++count` again, giving 2 and then 3, while `Cached` keeps returning its stored 1."""),

    q("range-takes-a-count", r'''
        Console.WriteLine(string.Join(",", Enumerable.Range(5, 3)) + " "
            + string.Join(",", Enumerable.Range(1, 0)).Length + " "
            + string.Join(",", Enumerable.Repeat("ab", 2)));
    ''', "5,6,7 0 ab,ab", ["5,6,7,8,9 0 ab,ab", "5,6,7 1 ab,ab", "5,6,7 0 abab"],
      "Enumerable.Range(start, count): the second number is how many, not where to stop",
      """`Range(5, 3)` is three numbers from 5: 5, 6, 7. A count of 0 gives an empty sequence, so
      the joined text has length 0. `Repeat("ab", 2)` is two items, joined with a comma."""),

    q("remainder-and-ieee-remainder", r'''
        double ieee = Math.IEEERemainder(5, 3), neg = Math.IEEERemainder(-5, 3);
        Console.WriteLine(FormattableString.Invariant(
            $"{5.5 % 2} {ieee} {-5 % 3} {neg} {5 % -3}"));
    ''', "1.5 -1 -2 1 2", ["1.5 2 -2 -2 2", "1.5 -1 1 1 -2", "1 -1 -2 1 2"],
      "% works on doubles and follows the left sign; IEEERemainder uses the nearest quotient",
      """`5.5 % 2` is 1.5, and `-5 % 3` is -2 (the sign of the left side). IEEERemainder divides 5 by 3
      and rounds the quotient to the nearest whole number, 2, so the remainder is 5 - 6 = -1."""),

    q("composite-format-indexes", r'''
        Console.WriteLine(string.Format("{1}{0}{1}", "x", "y") + " "
            + string.Format("{0} {0:D3}", 7) + " " + string.Format("{0}", 1, 2));
    ''', "yxy 7 007 1", ["xyx 7 007 1", "yxy 7 7 1", "yxy 7 007 12"],
      "A {n} placeholder is an index into the arguments: reusable, reorderable, extras ignored",
      """`{1}{0}{1}` picks the second argument, the first, then the second again. `{0:D3}` pads the
      integer to three digits. An argument that no placeholder mentions is simply not printed."""),

    q("null-prints-as-nothing-in-text", r'''
        string? s = null;
        int? n = null;
        Console.WriteLine("[" + s + "][" + n + "][" + s?.Length + "]["
            + (s ?? "d") + "]" + $"[{s}]");
    ''', "[][][][d][]", ["[null][null][null][d][null]", "[][][0][d][]", "[][null][][d][]"],
      "A null string, a null int? and a null result all turn into empty text when concatenated",
      """Concatenation and interpolation call nothing on a null: it simply contributes no characters.
      `s?.Length` is a null `int?` (not 0) because `s` is null, so it is also empty."""),

    q("isdigit-accepts-other-scripts", r'''
        char three = '٣';
        Console.WriteLine(char.IsDigit(three) + " " + (three >= '0' && three <= '9')
            + " " + char.GetNumericValue(three) + " " + char.IsDigit('x'));
    ''', "True False 3 False", ["False False 3 False", "True True 3 False", "True False 0 False"],
      "char.IsDigit is true for digits of every script; a range test on '0'..'9' is not",
      """The character U+0663 is an Arabic-Indic three. `IsDigit` accepts it, and `GetNumericValue`
      knows it is 3, but its code is not between those of '0' and '9', so the manual range test fails."""),

    q("struct-equals-compares-fields-but-boxes-differ", r'''
        var p = new P(1);
        object x = p, y = p;
        Console.WriteLine(p.Equals(new P(1)) + " " + ReferenceEquals(x, y) + " "
            + new C(1).Equals(new C(1)));

        struct P(int x) { public int X = x; }
        class C(int x) { public int X = x; }
    ''', "True False False",
    ["True True True", "False False False", "True True False"],
      "A struct's default Equals compares its fields; a class's compares references",
      """Without an override, a struct is equal when all its fields are. Each assignment of `p` to an
      `object` boxes it into its own new object, so `x` and `y` are different references. Two separate
      class instances are never equal by default."""),
)
