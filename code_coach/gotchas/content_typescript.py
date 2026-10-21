"""Gotchas, TypeScript: tsc --strict then node; portability notes are in langs.py (the `typescript` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("typescript")

ITEMS: tuple[Item, ...] = (
    q("sort-default-is-text", r'''
        const nums: number[] = [10, 9, 1, 100];
        nums.sort();
        console.log(nums.join(","));
    ''', "1,10,100,9", ["1,9,10,100", "100,10,9,1", "10,9,1,100"],
      "sort() with no comparator sorts as text, even for numbers",
      """The types say these are numbers, but `Array.prototype.sort` turns each element into a string and compares
      those, so "10" and "100" sort before "9". Types are erased before the program runs; pass `(a, b) => a - b`
      to sort numerically."""),

    q("or-versus-nullish", r'''
        type Box = { qty?: number };
        const box: Box = { qty: 0 };
        const shown = box.qty || 10;
        const kept = box.qty ?? 10;
        console.log(shown, kept);
    ''', "10 0", ["0 0", "10 10", "0 10"],
      "|| replaces every falsy value, ?? only null and undefined",
      """0 is falsy, so `box.qty || 10` throws the real zero away and picks 10. `??` only falls back when the left
      side is null or undefined, so it keeps the 0. `qty?: number` allows both 0 and undefined, which is why the
      two operators disagree."""),

    q("narrowing-is-compile-time", r'''
        const id: number | string = "42";
        console.log(typeof id, id + 1, Number(id) + 1);
    ''', "string 421 43", ["number 43 43", "string 43 43", "string 421 421"],
      "A union type does not change what the value is at runtime",
      """The assignment narrows `id` to string, so `id + 1` is allowed and it is string concatenation: "421". The
      declared type `number | string` is gone once the code runs; `typeof` sees the real value, a string, and only
      `Number(id)` makes it arithmetic."""),
)
