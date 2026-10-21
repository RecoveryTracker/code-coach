"""Gotchas, Ruby: run by ruby; portability notes are in langs.py (the `ruby` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("ruby")

ITEMS: tuple[Item, ...] = (
    q("only-nil-and-false-are-falsy", r'''
        values = [0, "", [], nil, false]
        puts values.map { |v| v ? 1 : 0 }.join
    ''', "11100", ["00000", "00110", "10100"],
      "In Ruby 0, empty strings and empty arrays are all truthy",
      """Only `nil` and `false` count as false. Zero, "" and [] are real objects, so they are truthy; this is
      unlike Python, JavaScript or C, where zero and empty things are false."""),

    q("floor-division-and-modulo", r'''
        puts [7 / 2, -7 / 2, -7 % 3, 7.fdiv(2)].inspect
    ''', "[3, -4, 2, 3.5]", ["[3, -3, -1, 3.5]", "[3.5, -3.5, 2, 3.5]", "[3, -4, -1, 3.5]"],
      "Integer division rounds down, and % takes the sign of the divisor",
      """Ruby's `/` on integers floors, so -7 / 2 is -4, not -3. The modulo is consistent with it: -7 % 3 is 2,
      the same sign as 3. `fdiv` is the way to get a float without converting by hand."""),

    q("hash-default-shared", r'''
        h = Hash.new([])
        h[:a] << 1
        h[:b] << 2
        puts "#{h} #{h[:z]}"
    ''', "{} [1, 2]", ["{a: [1], b: [2]} []", "{a: [1], b: [2]} [1, 2]", "{} []"],
      "The default array is one shared object, and << never stores it in the hash",
      """`Hash.new([])` uses the same array as the default for every missing key. `h[:a] << 1` reads that default
      and pushes onto it without assigning anything, so the hash stays empty while the shared array becomes
      [1, 2]. Use `Hash.new { |hash, k| hash[k] = [] }` for a fresh array per key."""),
)
