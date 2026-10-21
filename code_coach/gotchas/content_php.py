"""Gotchas, PHP: run by the php CLI (8.x); portability notes are in langs.py (the `php` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("php")

ITEMS: tuple[Item, ...] = (
    q("operator-precedence-and-modulo", r'''
        <?php
        echo implode(" ", [intdiv(7, 2), -7 % 3, 2 ** 3 ** 2]), "\n";
    ''', "3 -1 512", ["3.5 2 64", "3 2 64", "3 -1 64"],
      "% keeps the dividend's sign, and ** groups from the right",
      """`intdiv` truncates, giving 3. The remainder operator takes the sign of the left operand, so -7 % 3 is -1.
      `**` is right-associative: `2 ** 3 ** 2` is `2 ** (3 ** 2)`, which is 2 to the 9th power, 512."""),

    q("foreach-reference-leftover", r'''
        <?php
        $a = [1, 2, 3];
        foreach ($a as &$x) {
        }
        foreach ($a as $x) {
        }
        echo implode(",", $a), "\n";
    ''', "1,2,2", ["1,2,3", "3,3,3", "1,2,1"],
      "A reference left over from the first loop is overwritten by the second",
      """After the first loop `$x` is still a reference to the last element. The second loop assigns each value
      to `$x`, which writes straight into `$a[2]`: first 1, then 2, then whatever `$a[2]` now holds, which is
      2. Call `unset($x)` after a by-reference loop."""),

    q("loose-comparison", r'''
        <?php
        $r = [("10" == "1e1"), ("abc" == 0), (null == false), ("0" == false)];
        echo implode(" ", array_map(fn($b) => $b ? "t" : "f", $r)), "\n";
    ''', "t f t t", ["f f t t", "t t t t", "t f f t"],
      "== between numeric strings compares them as numbers",
      """Both "10" and "1e1" are numeric strings, so `==` compares the numbers 10 and 10 and calls them equal.
      Since PHP 8 a non-numeric string like "abc" is no longer converted to 0, so `"abc" == 0` is false (it was
      true in PHP 7). null and "0" are both loosely equal to false."""),
)
