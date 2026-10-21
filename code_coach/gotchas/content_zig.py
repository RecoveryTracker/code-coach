"""Gotchas, Zig: zig build-exe in Debug, output via std.debug.print (stderr); notes are in langs.py (`zig`)."""

from __future__ import annotations

from .items import Item, make

q = make("zig")

ITEMS: tuple[Item, ...] = (
    q("division-builtins", r'''
        const std = @import("std");

        pub fn main() void {
            const d = @divFloor(-7, 2);
            std.debug.print("{} {} {}\n", .{ 7 / 2, d, @rem(-7, 3) });
        }
    ''', "3 -4 -1", ["3 -3 -1", "3.5 -3.5 -1", "3 -4 2"],
      "Negative division needs a named builtin, and floor and truncate differ",
      """Dividing positive integers with `/` truncates, so 7 / 2 is 3. For values that can be negative Zig makes
      you choose: `@divFloor(-7, 2)` rounds down to -4. `@rem` is the remainder that follows the dividend's
      sign, so `@rem(-7, 3)` is -1."""),

    q("optional-orelse-and-slices", r'''
        const std = @import("std");

        pub fn main() void {
            const a: ?u8 = null;
            const b: u8 = a orelse 7;
            var arr = [_]u8{ 1, 2, 3 };
            const s = arr[1..];
            std.debug.print("{} {} {}\n", .{ b, s.len, s[0] });
        }
    ''', "7 2 2", ["7 3 1", "7 2 1", "0 2 2"],
      "orelse supplies the default, and arr[1..] starts at index 1",
      """`a` is null, so `a orelse 7` is 7. The slice `arr[1..]` runs from index 1 to the end: two elements,
      starting with the 2. Slices point into the original array; they do not copy it."""),

    q("wrapping-and-saturating-add", r'''
        const std = @import("std");

        pub fn main() void {
            const x: u8 = 250;
            const w = x +% 10;
            const s = x +| 10;
            const big = @as(u16, x) + 10;
            std.debug.print("{} {} {}\n", .{ w, s, big });
        }
    ''', "4 255 260", ["260 255 260", "4 4 260", "4 255 4"],
      "+% wraps, +| stops at the maximum, and widening first avoids both",
      """A plain `x + 10` on a u8 would panic in Debug builds because 260 does not fit. `+%` wraps around to
      260 - 256 = 4, and `+|` saturates at 255. Converting to a u16 before adding makes the sum fit, so it is
      260."""),
)
