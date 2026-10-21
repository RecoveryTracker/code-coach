"""Gotchas, C# (second deck): top-level statements run by `dotnet run`; notes are in langs.py (the `csharp` entry).

Printed doubles go through `FormattableString.Invariant` so no card depends on the machine's culture. Strings are
compared ordinally, nothing prints a hash code or a default `ToString()` of an object, and nothing races.
"""

from __future__ import annotations

from .items import Item, make

q = make("csharp")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics with a real trap ──────────────────────────────
    q("int-division-widening", r'''
        int a = 7;
        double r = a / 2;
        Console.WriteLine(FormattableString.Invariant(
            $"{r} {a / 2.0} {(double)(a / 2)} {(double)a / 2} {a % -3}"));
    ''', "3 3.5 3 3.5 1",
      ["3.5 3.5 3.5 3.5 1", "3 3.5 3 3.5 -2", "3 3.5 3.5 3.5 1"],
      "int / int is an int, whatever it is assigned to, and % keeps the left sign",
      """`a / 2` is integer division and gives 3 before it is widened to a double, and so does the cast around
      the whole division. Only an operand that is already a double, or a cast on `a` itself, makes it 3.5."""),

    q("plus-on-numbers-and-chars", r'''
        Console.WriteLine(1 + 2 + "3" + 4 + 5 + " " + 'a' + 'b'
            + " " + ('a' + 'b'));
    ''', "3345 ab 195", ["12345 ab 195", "3345 195 195", "3345 ab ab"],
      "+ adds until the first string appears, then it joins text",
      """`1 + 2` is still an int addition (3); the string "3" turns everything after it into concatenation. By
      the same rule `'a'` and `'b'` are appended as letters after the string, but `('a' + 'b')` in parentheses
      adds two chars as ints: 97 + 98."""),

    q("strings-are-immutable", r'''
        string s = "abc";
        s.ToUpper();
        string t = s.Replace("b", "x");
        s += "!";
        Console.WriteLine(s + " " + t);
    ''', "abc! axc", ["ABC! axc", "abc! abc", "ABC! AXC"],
      "String methods return a new string; they never change the original",
      """`s.ToUpper()` builds an upper-case copy that is thrown away, so `s` stays "abc". `Replace` also returns
      a new string, which is stored in `t`, and `s += "!"` makes a new string for `s` rather than editing it."""),

    q("string-equality-and-reference", r'''
        string a = "hi";
        string b = new string(new[] { 'h', 'i' });
        object o1 = a, o2 = b;
        Console.WriteLine((a == b) + " " + ReferenceEquals(a, b) + " "
            + a.Equals(b) + " " + (o1 == o2));
    ''', "True False True False",
      ["True True True True", "False False True False", "True False True True"],
      "== on strings compares text, but through `object` it compares references",
      """`string` overloads `==` to compare contents, and `Equals` does too. `o1 == o2` is typed as `object ==
      object`, which is plain reference equality, and `b` was built at run time as a different object."""),

    q("narrowing-casts-wrap", r'''
        int a = 300, b = 200, c = -1;
        Console.WriteLine((byte)a + " " + (sbyte)b + " " + (uint)c + " "
            + (char)(a - 235));
    ''', "44 -56 4294967295 A", ["300 200 4294967295 A", "44 -56 -1 A", "44 200 4294967295 65"],
      "An unchecked explicit cast keeps only the low bits",
      """By default C# does not check integer casts, so `(byte)300` keeps the low 8 bits (44), `(sbyte)200` reads
      the same bits as signed (-56), and `(uint)-1` is all ones. Casting 65 to `char` gives the letter A."""),

    q("checked-and-unchecked", r'''
        int x = int.MaxValue;
        int a = unchecked(x + 1);
        string b;
        try { b = checked(x + 1).ToString(); }
        catch (OverflowException) { b = "overflow"; }
        Console.WriteLine(a + " " + b + " " + (x + 1));
    ''', "-2147483648 overflow -2147483648",
      ["2147483648 overflow 2147483648", "-2147483648 overflow overflow", "-2147483648 -2147483648 -2147483648"],
      "Integer overflow wraps silently unless you ask for `checked`",
      """The default context is unchecked, so int.MaxValue + 1 wraps to the minimum value, with or without the
      explicit `unchecked`. Only the `checked(...)` expression throws OverflowException."""),

    q("foreach-gets-a-fresh-variable", r'''
        var fs = new List<Func<int>>();
        foreach (var i in new[] { 1, 2, 3 }) fs.Add(() => i);
        for (var j = 1; j <= 3; j++) fs.Add(() => j);
        Console.WriteLine(string.Join(",", fs.Select(f => f())));
    ''', "1,2,3,4,4,4", ["3,3,3,4,4,4", "1,2,3,1,2,3", "1,2,3,3,3,3"],
      "foreach makes a new variable per round; a for loop shares one",
      """Since C# 5 each `foreach` iteration has its own `i`, so the first three lambdas remember 1, 2 and 3. The
      `for` loop declares a single `j`, which the three lambdas share, and it is 4 when the loop stops."""),

    q("struct-copy-class-share", r'''
        var a = new S { X = 1 };
        var b = a;
        b.X = 2;
        var c = new K { X = 1 };
        var d = c;
        d.X = 2;
        Console.WriteLine(a.X + " " + c.X);

        struct S { public int X; }
        class K { public int X; }
    ''', "1 2", ["2 2", "1 1", "2 1"],
      "Assigning a struct copies it; assigning a class copies the reference",
      """`b = a` duplicates the struct, so changing `b.X` leaves `a.X` at 1. `d = c` only makes a second name
      for the same object, so the change shows through `c`."""),

    q("decimal-adds-exactly", r'''
        double a = 0.1, b = 0.2;
        decimal c = 0.1m, d = 0.2m;
        Console.WriteLine((a + b == 0.3) + " " + (c + d == 0.3m));
    ''', "False True", ["True True", "False False", "True False"],
      "double stores binary fractions; decimal stores decimal digits",
      """0.1 and 0.2 have no exact binary form, so their double sum is a hair off 0.3 and `==` fails. `decimal`
      keeps base-10 digits, so 0.1m + 0.2m is exactly 0.3m."""),

    q("cast-truncates-floor-rounds-down", r'''
        double d = -2.9;
        Console.WriteLine(FormattableString.Invariant(
            $"{(int)d} {(int)-d} {Math.Floor(d)} {Math.Ceiling(d)} {-7 / 2}"));
    ''', "-2 2 -3 -2 -3",
      ["-3 2 -3 -2 -4", "-2 2 -2 -2 -3", "-2 2 -3 -2 -4"],
      "Casting and integer division cut toward zero; Math.Floor goes down",
      """`(int)-2.9` drops the fraction and gives -2, and `-7 / 2` does the same and gives -3. `Math.Floor`
      always moves toward negative infinity, so `Math.Floor(-2.9)` is -3, while `Math.Ceiling` gives -2."""),

    q("lifted-nullable-operators", r'''
        int? a = null;
        int? b = 5;
        Console.WriteLine((a + b == null) + " " + (a < b) + " " + (a > b) + " "
            + (a == null) + " " + (a != b));
    ''', "True False False True True",
      ["False False False True True", "True True False True True", "True False True True False"],
      "Arithmetic with null gives null, and every ordering comparison with null is false",
      """The lifted `+` returns null when an operand is null, so `a + b == null` holds. `<` and `>` are false
      whenever a null is involved, but `==` and `!=` treat null as a value, so `a != b` is true."""),

    q("null-conditional-and-coalesce", r'''
        string? s = null;
        int n = s?.Length ?? -1;
        string t = s ?? "dflt";
        int? m = s?.Length + 1;
        Console.WriteLine(n + " " + t + " " + (m == null) + " [" + s + "]");
    ''', "-1 dflt True []", ["0 dflt False []", "-1 dflt True [null]", "-1 null True []"],
      "?. turns the whole chain into null, and a null string concatenates as empty",
      """`s?.Length` is null, so `?? -1` supplies -1, and adding 1 to a null `int?` is still null. Concatenating
      a null string adds nothing, so `s` shows as empty brackets, not the word null."""),

    q("range-and-index-operators", r'''
        string s = "hello";
        Console.WriteLine(s.Substring(1, 3) + " " + s[1..3] + " " + s[^1]
            + " " + s[..2] + " " + s[^3..]);
    ''', "ell el o he llo",
      ["ell ell o he llo", "ell el o hel llo", "ell el o he ell"],
      "Substring takes (start, length); a range takes [start..end) with the end excluded",
      """`Substring(1, 3)` is three characters from index 1: "ell". The range `1..3` stops before index 3, so
      it is "el". `^1` counts from the end (the last character), and `^3..` is the last three characters."""),

    q("named-and-default-arguments", r'''
        string F(int a, int b = 2, int c = 3) => $"{a}{b}{c}";
        Console.WriteLine(F(1) + " " + F(1, 8) + " " + F(1, c: 9) + " "
            + F(c: 7, a: 4));
    ''', "123 183 129 427", ["123 183 193 743", "123 813 129 427", "123 183 129 743"],
      "Positional arguments fill from the left; a name picks a parameter, whatever the order",
      """`F(1, 8)` gives the 8 to `b`, the second parameter, not to `c`. Named arguments may come in any order,
      and anything left out falls back to its default: `F(c: 7, a: 4)` is a=4, b=2, c=7."""),

    q("ref-versus-reference-parameter", r'''
        void Inc(int x) { x++; }
        void IncRef(ref int x) { x++; }
        void Fill(List<int> l) { l.Add(1); l = new List<int>(); l.Add(2); }
        int n = 1;
        var list = new List<int>();
        Inc(n); IncRef(ref n); Fill(list);
        Console.WriteLine(n + " " + list.Count + " " + list[0]);
    ''', "2 1 1", ["3 2 1", "2 2 1", "2 1 2"],
      "Arguments are passed by value; for a list that value is a reference to it",
      """`Inc` changes its own copy of the int, and only `ref` reaches the caller's variable, so `n` ends at 2.
      `Fill` can modify the caller's list through its copy of the reference, but assigning a new list to the
      parameter only changes that local copy."""),

    q("split-edge-cases", r'''
        Console.WriteLine("a,,b".Split(',').Length + " "
            + "a,,b".Split(',', StringSplitOptions.RemoveEmptyEntries).Length
            + " " + "".Split(',').Length + " " + "a b  c".Split(' ').Length
            + " " + ",".Split(',').Length);
    ''', "3 2 1 4 2", ["3 2 0 3 1", "2 2 0 4 0", "3 2 1 3 2"],
      "Split keeps empty pieces, and splitting an empty string still gives one piece",
      """"a,,b" has an empty field in the middle, so there are three pieces unless empty entries are removed.
      An empty string yields an array with a single empty string, and "," yields two empty strings."""),

    q("remove-versus-removeat", r'''
        var l = new List<int> { 5, 6, 7 };
        l.Remove(1);
        l.RemoveAt(1);
        bool r = l.Remove(9);
        Console.WriteLine(string.Join(",", l) + " " + r);
    ''', "5,7 False", ["5 False", "6 False", "5,7 True"],
      "Remove takes a value, RemoveAt takes an index",
      """`l.Remove(1)` looks for the value 1, finds none, and changes nothing. `RemoveAt(1)` removes the element
      at index 1, which is 6. `Remove(9)` finds nothing and returns false."""),

    q("tuple-assignment-is-simultaneous", r'''
        var (a, b) = (1, 2);
        (a, b) = (b, a + b);
        (a, b) = (b, a + b);
        Console.WriteLine(a + " " + b);
    ''', "3 5", ["4 8", "3 4", "2 3"],
      "The right-hand tuple is built from the old values before anything is assigned",
      """Both `b` and `a + b` are evaluated first, using the current values, and only then stored. So 1, 2
      becomes 2, 3 and then 3, 5. A one-by-one assignment would have changed `a` before `a + b` was read."""),

    q("boxed-equality", r'''
        int i = 5;
        object a = i, b = i;
        Console.WriteLine((a == b) + " " + a.Equals(b) + " "
            + ((int)a == (int)b) + " " + ReferenceEquals(a, a));
    ''', "False True True True",
      ["True True True True", "False False True True", "False True False True"],
      "Each boxing creates a new object, and == on object compares references",
      """Boxing `i` twice makes two separate heap objects, so `a == b` is false. `Equals` is overridden by
      `Int32` and compares the values, as does comparing after unboxing."""),

    q("linq-is-deferred", r'''
        var xs = new List<int> { 1, 2, 3 };
        var lazy = xs.Where(x => x > 1);
        var eager = xs.Where(x => x > 1).ToList();
        xs.Add(4);
        Console.WriteLine(lazy.Count() + " " + eager.Count);
    ''', "3 2", ["2 2", "3 3", "2 3"],
      "A LINQ query runs when it is enumerated, not where it is written",
      """`lazy` holds only the recipe, so it sees the 4 that was added afterwards and counts 2, 3 and 4.
      `ToList()` ran the query immediately, so `eager` is a snapshot of the two values at that moment."""),

    q("linq-captures-the-variable", r'''
        int min = 1;
        var q = new[] { 1, 2, 3 }.Where(x => x > min);
        min = 2;
        string first = string.Join(",", q);
        min = 0;
        Console.WriteLine(first + "|" + string.Join(",", q));
    ''', "3|1,2,3", ["2,3|2,3", "3|3", "2,3|1,2,3"],
      "The query reads `min` each time it runs, not when it was defined",
      """The lambda captures the variable itself, and the query is re-evaluated on every enumeration. At the
      first join `min` is 2, so only 3 passes; at the second `min` is 0, so everything does."""),

    q("yield-runs-on-demand", r'''
        IEnumerable<int> Gen() {
            Console.Write("a");
            yield return 1;
            Console.Write("b");
            yield return 2;
            Console.Write("c");
        }
        var g = Gen();
        Console.Write("x");
        foreach (var v in g) Console.Write(v);
        Console.WriteLine();
    ''', "xa1b2c", ["abcx12", "xabc12", "xa1b2"],
      "An iterator method does nothing until you start enumerating it",
      """Calling `Gen()` only creates the iterator, so "x" prints first. Each step of the `foreach` then runs
      the method up to the next `yield return`, and the final "c" runs when the loop asks for a third item."""),

    # ── Medium and hard ────────────────────────────────────────────────────
    q("static-initialisers-run-in-text-order", r'''
        Console.WriteLine(A.X + " " + A.Y);

        class A {
            public static int X = Y + 1;
            public static int Y = 5;
        }
    ''', "1 5", ["6 5", "1 0", "5 5"],
      "Static fields are initialised top to bottom, so an early one sees a late one as 0",
      """When `X` is initialised, `Y` has not run yet and still holds its default 0, so `X` becomes 1. Then
      `Y` is set to 5. Reordering the two lines would make X 6."""),

    q("readonly-struct-field-copy", r'''
        var h = new Holder();
        h.Field.Inc();
        h.Field.Inc();
        var arr = new[] { new Counter() };
        arr[0].Inc();
        Console.WriteLine(h.Field.N + " " + arr[0].N);

        struct Counter { public int N; public void Inc() { N++; } }
        class Holder { public readonly Counter Field = new Counter(); }
    ''', "0 1", ["2 1", "0 0", "2 0"],
      "Calling a mutating method on a readonly struct field changes a hidden copy",
      """A `readonly` field cannot be modified, so the compiler calls `Inc()` on a temporary copy and the field
      stays at 0. An array element is a real variable, so `arr[0].Inc()` changes the struct in place."""),

    q("string-interning", r'''
        string a = "hel" + "lo";
        string b = "hello";
        string h = "hel";
        string c = h + "lo";
        Console.WriteLine(ReferenceEquals(a, b) + " " + ReferenceEquals(c, b)
            + " " + ReferenceEquals(string.Intern(c), b) + " " + (c == b));
    ''', "True False True True",
      ["True True True True", "False False True True", "True False False True"],
      "Literals and constant expressions share one object; run-time strings do not",
      """`"hel" + "lo"` is folded into the literal "hello" at compile time and interned, so it is the same
      object as `b`. `h + "lo"` is built at run time as a fresh string, and `string.Intern` hands back the
      shared one."""),

    q("record-equality-and-arrays", r'''
        var a = new Item(1, new[] { 1 });
        var b = new Item(1, new[] { 1 });
        var c = a with { X = 1 };
        Console.WriteLine((a == b) + " " + (a == c) + " " + ReferenceEquals(a, c));

        record Item(int X, int[] Data);
    ''', "False True False", ["True True False", "False False False", "True True True"],
      "Records compare each member with Equals, and an array's Equals is reference equality",
      """`a` and `b` have the same X but different array objects, so they are not equal. `with` makes a new
      record that shares the same array reference, so `a == c` holds even though `ReferenceEquals` is false."""),

    q("division-by-zero-int-and-double", r'''
        int z = 0;
        string r;
        try { r = (1 / z).ToString(); }
        catch (DivideByZeroException) { r = "throws"; }
        Console.WriteLine(FormattableString.Invariant(
            $"{r} {1.0 / z} {-1.0 / z} {0.0 / z == 0.0 / z}"));
    ''', "throws Infinity -Infinity False",
      ["throws Infinity -Infinity True", "throws throws throws False", "0 Infinity -Infinity False"],
      "Integer division by zero throws; floating-point division by zero gives Infinity or NaN",
      """`1 / z` is int division and throws DivideByZeroException. With a double numerator the division follows
      IEEE rules and gives Infinity, -Infinity or NaN, and NaN is not equal to anything, even itself."""),

    q("decimal-keeps-its-scale", r'''
        Console.WriteLine(FormattableString.Invariant(
            $"{1.10m} {1.1m * 2} {3m / 2} {1m / 3} {2.50m + 2.5m}"));
    ''', "1.10 2.2 1.5 0.3333333333333333333333333333 5.00",
      ["1.1 2.2 1.5 0.3333333333333333 5", "1.10 2.20 1.50 0.33 5.00",
       "1.1 2.2 1.5 0.3333333333333333333333333333 5.0"],
      "A decimal remembers the trailing zeros it was written with",
      """`decimal` stores a scale, so 1.10m prints with two decimals and 2.50m + 2.5m keeps the larger scale and
      prints 5.00. Division uses as many of its 28 or so digits as it needs, which is why 1m / 3 is so long."""),

    q("float-widening-shows-error", r'''
        float f = 0.1f;
        Console.WriteLine(FormattableString.Invariant(
            $"{0.1 + 0.2} {f + 0.2f} {(double)f} {f == 0.1}"));
    ''', "0.30000000000000004 0.3 0.10000000149011612 False",
      ["0.3 0.3 0.1 True", "0.30000000000000004 0.30000000000000004 0.1 False",
       "0.3 0.3 0.10000000149011612 False"],
      "A float is not exactly the double with the same digits",
      """The float nearest to 0.1 is about 0.10000000149, and widening it to a double reveals that, so it no
      longer equals the double 0.1. Float and double each print the shortest text that reads back the same."""),

    q("interpolation-alignment-and-formats", r'''
        Console.WriteLine(FormattableString.Invariant(
            $"[{5,4}][{5,-4}]{3.14159:F2} {255:X} {255:x4} {1234.5:N1}"));
    ''', "[   5][5   ]3.14 FF 00ff 1,234.5",
      ["[   5][5   ]3.14 ff 00FF 1,234.5", "[   5][5   ]3.14 FF ff 1234.5",
       "[   5][5   ]3.1 FF 00ff 1,234.5"],
      "A positive width right-aligns, a negative one left-aligns; the format follows the colon",
      """`{5,4}` pads on the left to four columns and `{5,-4}` pads on the right. `F2` is two decimals, `X` is
      upper-case hex, `x4` is lower-case hex padded to four digits, and `N1` adds thousands separators."""),

    q("changing-a-list-inside-foreach", r'''
        var l = new List<int> { 1, 2, 3, 4 };
        try {
            foreach (var x in l) if (x == 2) l.Remove(x);
        } catch (InvalidOperationException) {
            Console.Write("caught ");
        }
        Console.WriteLine(string.Join(",", l));
    ''', "caught 1,3,4", ["1,2,3,4", "caught 1,2,3,4", "1,3,4"],
      "The exception comes on the next step, after the change has already happened",
      """`Remove` succeeds and bumps the list's version, and the enumerator notices only when `foreach` asks for
      the next item, throwing InvalidOperationException. Nothing is rolled back, so the 2 is gone."""),

    q("assignment-evaluates-left-first", r'''
        int i = 0;
        var arr = new int[3];
        arr[i++] = i;
        arr[i] = i++;
        Console.WriteLine(string.Join(",", arr) + " " + i);
    ''', "1,1,0 2", ["0,0,0 2", "0,1,0 2", "1,2,0 2"],
      "C# evaluates the target of an assignment, left to right, before the value",
      """In `arr[i++] = i` the index is taken first (0) and `i` becomes 1, so the stored value is 1. In
      `arr[i] = i++` the index 1 is read first, then `i++` produces 1, so `arr[1]` is 1 and `i` ends at 2."""),

    q("conditional-operator-types", r'''
        Console.WriteLine((true ? 'a' : 0) + " " + (true ? 'a' : 'b') + " "
            + (true ? 1 : 2.5));
    ''', "97 a 1", ["a a 1", "97 97 1", "97 a 1.0"],
      "The ?: result has one type for both branches, even for the branch not taken",
      """A constant int does not convert to `char` in C#, so `'a' : 0` is typed int and prints 97. With two
      chars the result stays a char. `1 : 2.5` is typed double, and the double 1 prints as "1"."""),

    q("flags-enum-text", r'''
        Console.WriteLine((F.A | F.C) + " " + (F)8 + " " + (F)3 + " "
            + F.A.HasFlag(F.B) + " " + (F.None == 0));

        [Flags] enum F { None = 0, A = 1, B = 2, C = 4 }
    ''', "A, C 8 A, B False True",
      ["5 8 3 False True", "A, C 8 A, B True True", "A, C 8 A, B False False"],
      "A [Flags] enum prints combinations by name and unknown bits as a number",
      """With `[Flags]`, `ToString` lists the named bits it finds: 5 is "A, C" and 3 is "A, B". The value 8 has
      no name, so it falls back to the number."""),

    q("lambda-captures-the-variable", r'''
        int x = 10;
        Func<int> f = () => x++;
        x = 20;
        Console.WriteLine(f() + " " + x);
    ''', "20 21", ["10 20", "10 11", "20 20"],
      "A lambda captures the variable itself, not its value at creation",
      """The lambda shares `x` with the surrounding code, so after `x = 20` the call returns 20 and then
      increments the same variable to 21. It does not work on a private copy of the 10."""),

    q("multicast-delegate-last-wins", r'''
        Func<int> f = () => 1;
        f += () => 2;
        f += () => 3;
        Console.WriteLine(f() + " " + f.GetInvocationList().Length);
    ''', "3 3", ["6 3", "1 3", "3 1"],
      "Calling a multicast delegate runs every target but returns only the last result",
      """`+=` chains the three lambdas into one delegate with three targets. All three run, in order, and the
      value of the call is the return value of the final one, 3. The earlier results are discarded."""),

    q("virtual-new-and-override", r'''
        B b = new D();
        Console.WriteLine(b.F() + b.G() + ((D)b).G());

        class B { public virtual string F() => "B"; public string G() => "B"; }
        class D : B {
            public override string F() => "D";
            public new string G() => "D";
        }
    ''', "DBD", ["DDD", "BBD", "DBB"],
      "override replaces a virtual method; `new` only hides one for callers who see the derived type",
      """`F` is virtual and overridden, so the call through a `B` variable runs D's version. `G` is hidden, not
      overridden, so a `B`-typed call picks B's method, while the cast to `D` picks D's."""),

    q("base-constructor-sees-half-built-object", r'''
        new D();

        class B {
            public B() { Console.WriteLine(Name()); }
            public virtual string Name() => "B";
        }
        class D : B {
            string a = "init";
            string? b;
            public D() { b = "ctor"; }
            public override string Name() => a + "," + (b ?? "null");
        }
    ''', "init,null", ["null,null", "init,ctor", "B"],
      "Field initialisers run before the base constructor; constructor bodies run after it",
      """Unlike C++, the call from `B()` is dispatched to D's override. D's field initialiser for `a` has
      already run, but the assignment inside `D()`'s body has not, so `b` is still null."""),

    q("static-constructor-order", r'''
        new A();
        new A();
        Console.WriteLine();

        class A {
            static int n = Log("field ");
            static A() { Console.Write("cctor "); }
            public A() { Console.Write("ctor "); }
            static int Log(string s) { Console.Write(s); return 1; }
        }
    ''', "field cctor ctor ctor",
      ["cctor field ctor ctor", "ctor field cctor ctor", "field cctor ctor"],
      "Static field initialisers run first, then the static constructor, once, before first use",
      """Creating the first A triggers the type initialiser: static field initialisers in text order, then the
      static constructor body. Each `new A()` then runs the instance constructor, and the static part is not
      repeated."""),

    q("dictionary-indexer-versus-add", r'''
        var d = new Dictionary<string, int>();
        d["a"] = 1;
        bool t = d.TryAdd("a", 2);
        d["a"] += 10;
        string r;
        try { d.Add("a", 0); r = "added"; }
        catch (ArgumentException) { r = "dup"; }
        Console.WriteLine(d["a"] + " " + t + " " + r);
    ''', "11 False dup", ["11 True dup", "1 False dup", "11 False added"],
      "The indexer sets or replaces; Add throws on a duplicate; TryAdd reports it",
      """`d["a"] = 1` creates the key. `TryAdd` leaves an existing key alone and returns false, and `+= 10`
      updates it to 11. `Add` refuses a duplicate key with an ArgumentException."""),

    q("array-covariance", r'''
        object[] objs = new string[1];
        string r;
        try { objs[0] = 1; r = "ok"; }
        catch (ArrayTypeMismatchException) { r = "mismatch"; }
        Console.WriteLine(r + " " + (objs is string[]));
    ''', "mismatch True", ["ok True", "mismatch False", "ok False"],
      "A string[] can be used as an object[], but the array still only holds strings",
      """Arrays are covariant in C#, so the assignment compiles, and `objs` really is a `string[]`. Storing an
      int into it is checked at run time and throws ArrayTypeMismatchException."""),

    q("three-valued-bool-logic", r'''
        bool? n = null;
        Console.WriteLine($"{n & false}|{n | true}|{n & true}|{n ^ true}|{!n}");
    ''', "False|True|||", ["False|False|||", "|True|||", "False|True|False|True|"],
      "With a null bool?, `&` and `|` can still decide the answer; the other operators give null",
      """`null & false` is false whatever the unknown is, and `null | true` is true for the same reason. For
      `& true`, `^` and `!` the result depends on the unknown value, so it stays null and prints as empty."""),

    q("multiply-then-widen", r'''
        int a = 100000;
        long p = a * a;
        long q = (long)a * a;
        int m = int.MinValue;
        Console.WriteLine(p + " " + q + " " + (-m == m));
    ''', "1410065408 10000000000 True",
      ["10000000000 10000000000 False", "1410065408 1410065408 True", "-1410065408 10000000000 True"],
      "The multiplication is done in int before the result is widened to long",
      """`a * a` is int times int, so it wraps around to 1410065408 before being stored in the long. Casting
      one operand first makes it a long multiplication. Negating `int.MinValue` wraps back to itself."""),

    q("surrogate-pairs", r'''
        string s = "a\U0001F600b";
        Console.WriteLine(s.Length + " " + s.EnumerateRunes().Count() + " "
            + char.IsSurrogate(s[1]) + " " + s[3]);
    ''', "4 3 True b", ["3 3 False b", "4 4 True b", "3 3 True b"],
      "Length counts UTF-16 code units; an emoji takes two of them",
      """U+1F600 is outside the 16-bit range, so a `string` stores it as a surrogate pair, two chars. `Length`
      is therefore 4, while `EnumerateRunes` counts whole characters. Index 3 is the final 'b'."""),

    q("convert-rounds-to-even", r'''
        Console.WriteLine(Convert.ToInt32(2.5) + " " + Convert.ToInt32(3.5) + " "
            + (int)3.5 + " " + Convert.ToInt32(-2.5) + " "
            + (int)Math.Round(2.5, MidpointRounding.AwayFromZero));
    ''', "2 4 3 -2 3", ["3 4 3 -3 3", "2 4 3 -3 3", "2 3 3 -2 3"],
      "Convert.ToInt32 rounds halves to even, while a cast truncates",
      """`Convert.ToInt32(double)` uses banker's rounding: 2.5 goes to the even 2 and 3.5 to the even 4, and
      -2.5 goes to -2. `(int)3.5` simply drops the fraction. Only `AwayFromZero` gives the school answer 3."""),

    q("await-on-a-finished-task", r'''
        async Task Run() {
            Console.Write("1");
            await Task.CompletedTask;
            Console.Write("2");
        }
        var t = Run();
        Console.Write("3");
        await t;
        Console.WriteLine();
    ''', "123", ["132", "312", "213"],
      "An async method runs synchronously until it awaits something that is not finished",
      """`Task.CompletedTask` is already complete, so `await` does not suspend and the method carries straight
      on to print 2 before it returns. Only an await on unfinished work would hand control back to the caller."""),

    q("orderby-is-stable", r'''
        var words = new[] { "bb", "a", "cc", "d", "ee" };
        Console.WriteLine(string.Join(",", words.OrderBy(w => w.Length)) + " "
            + string.Join(",", words.OrderByDescending(w => w.Length)));
    ''', "a,d,bb,cc,ee bb,cc,ee,a,d",
      ["a,d,bb,cc,ee ee,cc,bb,d,a", "d,a,bb,cc,ee bb,cc,ee,a,d", "a,d,bb,cc,ee bb,cc,ee,d,a"],
      "LINQ sorting is stable, in both directions; ties keep their original order",
      """Items with equal keys stay in the order they started in, for `OrderBy` and for `OrderByDescending`
      alike. A descending sort is therefore not just the reverse of the ascending result."""),

    q("stack-pops-last-queue-first", r'''
        var s = new Stack<int>(new[] { 1, 2, 3 });
        var q = new Queue<int>(new[] { 1, 2, 3 });
        Console.WriteLine(string.Join("", s) + " " + string.Join("", q) + " "
            + s.Pop() + q.Dequeue());
    ''', "321 123 31", ["123 123 11", "321 321 33", "321 123 13"],
      "A Stack built from a sequence has the last item on top, and enumerates top first",
      """The constructor pushes 1, 2, 3 in order, so 3 is on top and enumeration starts there. The queue keeps
      first-in, first-out order. `Pop` returns 3 and `Dequeue` returns 1."""),

    q("binary-search-complement", r'''
        var a = new[] { 1, 3, 5 };
        int i = Array.BinarySearch(a, 4);
        Console.WriteLine(i + " " + ~i + " " + Array.BinarySearch(a, 3) + " "
            + Array.IndexOf(a, 4));
    ''', "-3 2 1 -1", ["-1 -1 1 -1", "3 2 1 -1", "-3 3 1 -1"],
      "A missing item gives the bitwise complement of where it would be inserted",
      """`BinarySearch` returns a negative number for a miss: `~index`, where index is the insertion point
      (2 here), so ~2 is -3. Applying `~` again recovers the 2. `IndexOf` just returns -1 for a miss."""),

    q("params-and-array-covariance", r'''
        int C(params object[] a) => a.Length;
        Console.WriteLine(C(new[] { 1, 2, 3 }) + " " + C(new object[] { 1, 2, 3 })
            + " " + C(new[] { "a", "b" }) + " " + C());
    ''', "1 3 2 0", ["3 3 2 0", "1 3 1 0", "3 3 3 1"],
      "An array is passed as the params array if it converts to object[]; an int[] does not",
      """`object[]` is passed as-is (3 items). A `string[]` converts to `object[]` by array covariance, so it is
      also used as the array itself (2 items). An `int[]` is not an `object[]`, so it is wrapped as one single
      argument."""),

    q("nullable-boxing", r'''
        int? n = null;
        int? m = 5;
        object? a = n;
        Console.WriteLine((a == null) + " " + m.GetType().Name + " " + (m is int)
            + " " + n.HasValue);
    ''', "True Int32 True False",
      ["True Nullable`1 True False", "False Int32 True False", "True Int32 False False"],
      "Boxing a nullable gives null, or the plain value; there is no boxed Nullable<T>",
      """Boxing an `int?` with no value produces a null reference, and one with a value produces an ordinary
      boxed int. That is why `GetType()` reports Int32 and not Nullable, and why `m is int` is true."""),
)
