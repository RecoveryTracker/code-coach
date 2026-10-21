"""Gotchas, C#: top-level statements run by `dotnet run`; portability notes are in langs.py (the `csharp` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("csharp")

ITEMS: tuple[Item, ...] = (
    q("for-loop-closure", r'''
        var fs = new List<Func<int>>();
        for (int i = 0; i < 3; i++) fs.Add(() => i);
        Console.WriteLine(string.Join(",", fs.Select(f => f())));
    ''', "3,3,3", ["0,1,2", "1,2,3", "2,2,2"],
      "A for loop has one variable, and every lambda captures that same one",
      """The three lambdas share the single `i` the loop declared, and they run after the loop has finished, when
      `i` is 3. A `foreach` makes a fresh variable per iteration, so the same code with `foreach` would print
      0,1,2."""),

    q("bankers-rounding", r'''
        Console.WriteLine(Math.Round(2.5) + " " + Math.Round(3.5) + " "
            + Math.Round(-2.5));
    ''', "2 4 -2", ["3 4 -3", "2 3 -2", "3 4 -2"],
      "Math.Round rounds halves to the nearest even number",
      """The default mode is "banker's rounding": a value exactly halfway goes to the even neighbour, so 2.5 becomes
      2, 3.5 becomes 4 and -2.5 becomes -2. Pass `MidpointRounding.AwayFromZero` to get the 3, 4, -3 that school
      taught."""),

    q("int-then-double", r'''
        double a = 7 / 2 * 2.0;
        double b = 7 / 2.0 * 2;
        Console.WriteLine(a + " " + b);
    ''', "6 7", ["7 7", "6 6", "7 6"],
      "The integer division happens first, before the double is in play",
      """`7 / 2 * 2.0` is evaluated left to right: `7 / 2` is int / int, which is 3, and only then is it multiplied
      by 2.0 to make 6. In `7 / 2.0 * 2` the division already involves a double, so it is 3.5 and the result is
      7."""),
)
