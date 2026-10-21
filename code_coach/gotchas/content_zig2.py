"""Gotchas, Zig (second deck): defer, casts, optionals, slices, formatting. Same rules as content_zig.py."""

from __future__ import annotations

from .items import Item, make

q = make("zig")

ITEMS: tuple[Item, ...] = (
    # ── defer and errdefer ─────────────────────────────────────────────────
    q("defer-lifo-order", r'''
        const std = @import("std");

        pub fn main() void {
            defer std.debug.print("a\n", .{});
            {
                defer std.debug.print("b ", .{});
                defer std.debug.print("c ", .{});
                std.debug.print("d ", .{});
            }
            std.debug.print("e ", .{});
        }
    ''', "d c b e a", ["d b c e a", "a d c b e", "d c b a e"],
      "Deferred statements run last-in first-out when their block ends",
      """The inner block prints d, then leaves, running its defers in reverse order: c, then b. The outer defer
      waits for the end of `main`, so a comes last, after e."""),

    q("defer-in-loop", r'''
        const std = @import("std");

        pub fn main() void {
            var i: u32 = 0;
            while (i < 3) : (i += 1) {
                defer std.debug.print("d{} ", .{i});
                if (i == 1) continue;
                std.debug.print("b{} ", .{i});
            }
            std.debug.print("\n", .{});
        }
    ''', "b0 d0 d1 b2 d2", ["b0 b2 d0 d1 d2", "b0 d0 b1 d1 b2 d2", "d0 b0 d1 d2 b2"],
      "A defer in a loop body runs on every iteration, even when it continues",
      """The loop body is a block, so its defer fires each time the block is left, including through `continue`.
      Iteration 1 skips the `b1` print but still runs `d1`."""),

    q("defer-reads-at-exit", r'''
        const std = @import("std");

        pub fn main() void {
            var x: i32 = 1;
            defer std.debug.print("{}\n", .{x});
            x = 2;
            x += 40;
        }
    ''', "42", ["1", "2", "41"],
      "The deferred call evaluates its arguments when it runs, not when it is written",
      """A defer postpones the whole statement, including reading `x`. By the time the block ends, x holds 42, so
      that is what gets printed. This differs from Go, where a deferred call's arguments are fixed at the
      `defer` line."""),

    q("defer-is-block-scoped", r'''
        const std = @import("std");

        fn run(go: bool) void {
            if (go) {
                defer std.debug.print("1 ", .{});
                std.debug.print("2 ", .{});
            }
            std.debug.print("3\n", .{});
        }

        pub fn main() void {
            run(true);
        }
    ''', "2 1 3", ["2 3 1", "1 2 3", "3 2 1"],
      "defer runs when its own block ends, not when the function returns",
      """The `defer` sits inside the `if` block, so it fires as soon as that block closes: after the 2, before the
      3. In Go or Swift's function-level view you might expect it to wait for the function's end."""),

    q("errdefer-only-on-error", r'''
        const std = @import("std");

        fn work(fail: bool) !u8 {
            errdefer std.debug.print("undo ", .{});
            defer std.debug.print("close ", .{});
            if (fail) return error.Boom;
            return 7;
        }

        pub fn main() void {
            const a = work(false) catch 0;
            const b = work(true) catch 1;
            std.debug.print("{} {}\n", .{ a, b });
        }
    ''', "close close undo 7 1", ["close close 7 1", "close undo close 7 1",
      "close undo close undo 7 1"],
      "errdefer runs only when the function returns an error, in reverse order with defer",
      """The first call succeeds: only the plain `defer` runs, printing close. The second fails: both run, last
      registered first, so close comes before undo. Then `a` is 7, and `b` falls back to 1 through `catch`."""),

    # ── Integers ───────────────────────────────────────────────────────────
    q("string-literal-bytes", r'''
        const std = @import("std");

        pub fn main() void {
            const s = "héllo";
            std.debug.print("{} {} {} {c}\n", .{ s.len, s[1], "abc"[1], "abc"[1] });
        }
    ''', "6 195 98 b", ["5 233 98 b", "6 233 98 b", "6 195 98 98"],
      "A string literal is a byte array: len counts bytes, indexing gives a u8",
      """The `é` takes two UTF-8 bytes (195 and 169), so the length is 6 and `s[1]` is the first of them, 195.
      `"abc"[1]` is the byte 98, which `{}` prints as a number and `{c}` as the character b."""),

    q("for-range-and-index", r'''
        const std = @import("std");

        pub fn main() void {
            const a = [_]u32{ 10, 20, 30 };
            var sum: u32 = 0;
            for (a, 0..) |v, i| sum += v * @as(u32, @intCast(i));
            for (1..3) |i| sum += @as(u32, @intCast(i));
            std.debug.print("{}\n", .{sum});
        }
    ''', "83", ["86", "143", "80"],
      "A range a..b stops before b, and a second capture counts from 0",
      """The first loop pairs each value with its index: 0 + 20 + 60 = 80. `1..3` covers 1 and 2 only, adding 3
      more, which makes 83. Neither loop starts counting at 1 unless you ask for it."""),

    q("widen-before-multiply", r'''
        const std = @import("std");

        fn wide(a: u8, b: u8) u16 {
            return @as(u16, a) * b;
        }

        fn wrap(a: u8, b: u8) u8 {
            return a *% b;
        }

        pub fn main() void {
            std.debug.print("{} {}\n", .{ wide(200, 2), wrap(200, 2) });
        }
    ''', "400 144", ["400 400", "144 144", "400 255"],
      "Widen first to keep the whole product; *% keeps only the low 8 bits",
      """Casting one operand to u16 makes the multiplication happen in 16 bits, giving 400. `*%` stays in u8 and
      wraps: 400 - 256 = 144. A plain `a * b` on two u8 would panic in a Debug build."""),

    q("truncate-and-bitcast", r'''
        const std = @import("std");

        fn low(x: u16) u8 {
            return @truncate(x);
        }

        fn same(x: i8) u8 {
            return @bitCast(x);
        }

        pub fn main() void {
            const t: i8 = @bitCast(@as(u8, 200));
            std.debug.print("{} {} {}\n", .{ low(0x1234), same(-1), t });
        }
    ''', "52 255 -56", ["18 255 -56", "52 -1 200", "4660 255 -56"],
      "@truncate keeps the low bits, and @bitCast reinterprets them without converting",
      """`@truncate` keeps the low byte of 0x1234, which is 0x34 = 52, not the high byte 0x12. `@bitCast` of -1 as
      a u8 gives the same bits read as unsigned, 255; likewise the bits of 200 read as signed are -56."""),

    q("saturating-and-wrapping-ops", r'''
        const std = @import("std");

        pub fn main() void {
            var x: u32 = 10;
            x -%= 11;
            var s: i8 = -100;
            s = s -| 100;
            const r = std.math.add(u8, 250, 10) catch 99;
            std.debug.print("{} {} {}\n", .{ x, s, r });
        }
    ''', "4294967295 -128 99", ["-1 -128 99", "4294967295 -200 99", "4294967295 -128 4"],
      "-% wraps below zero, -| stops at the minimum, and std.math.add reports overflow",
      """Subtracting past zero with `-%=` wraps to the largest u32. `-|` saturates at the smallest i8, -128, rather
      than reaching -200. `std.math.add` does not wrap; it returns an error, so `catch` supplies 99."""),

    q("overflow-builtin-tuple", r'''
        const std = @import("std");

        fn add(a: u8, b: u8) struct { u8, u1 } {
            return @addWithOverflow(a, b);
        }

        pub fn main() void {
            const r = add(250, 10);
            const k = add(100, 10);
            std.debug.print("{} {} {} {}\n", .{ r[0], r[1], k[0], k[1] });
        }
    ''', "4 1 110 0", ["260 1 110 0", "4 0 110 0", "4 1 110 1"],
      "@addWithOverflow returns the wrapped result and a one-bit overflow flag",
      """The builtin does not panic: it gives back a tuple of the truncated sum and a flag. 250 + 10 wraps to 4
      with the flag set to 1; 100 + 10 fits, so 110 with flag 0."""),

    q("bit-counting-builtins", r'''
        const std = @import("std");

        pub fn main() void {
            const a = @popCount(@as(u8, 0b1011));
            const b = @clz(@as(u8, 1));
            const c = @ctz(@as(u8, 8));
            std.debug.print("{} {} {}\n", .{ a, b, c });
        }
    ''', "3 7 3", ["4 0 3", "3 0 8", "3 7 8"],
      "Count set bits, leading zeros of the type's width, and trailing zeros",
      """`@popCount(0b1011)` is 3 ones. For a u8 holding 1, there are 7 zero bits in front of the single 1, so
      `@clz` is 7. 8 is 0b1000 with 3 zeros after the 1, so `@ctz` is 3."""),

    q("sizes-in-bytes-and-bits", r'''
        const std = @import("std");

        pub fn main() void {
            std.debug.print("{} {} {} {}\n", .{
                @sizeOf([3]u16), @sizeOf(u7), @bitSizeOf(u7), @sizeOf(bool),
            });
        }
    ''', "6 1 7 1", ["3 1 7 1", "6 7 7 1", "6 1 1 1"],
      "@sizeOf counts whole bytes, @bitSizeOf counts the exact bits",
      """An array of three u16 takes 6 bytes. A u7 is stored in a whole byte, so `@sizeOf(u7)` is 1 while its
      `@bitSizeOf` is 7. A bool also occupies one byte."""),

    q("shift-keeps-the-width", r'''
        const std = @import("std");

        fn shl(x: u8, n: u3) u8 {
            return x << n;
        }

        pub fn main() void {
            const m: i8 = -128;
            const x = shl(0b1000_0001, 1);
            std.debug.print("{} {} {}\n", .{ x, shl(1, 7), m >> 7 });
        }
    ''', "2 128 -1", ["258 128 -1", "2 128 1", "0 128 -1"],
      "<< drops the bits that fall off the type, and >> on a signed number copies the sign",
      """The result of a shift has the operand's type, so 0b10000001 << 1 loses its top bit and leaves 2, not
      258. Shifting a negative i8 right keeps the sign bit, so -128 >> 7 is -1, not 1."""),

    q("arithmetic-shift-floors", r'''
        const std = @import("std");

        pub fn main() void {
            var a: i32 = -5;
            a += 0;
            const r = .{ a >> 1, @divTrunc(a, 2), @divFloor(a, 2) };
            std.debug.print("{} {} {}\n", r);
        }
    ''', "-3 -2 -3", ["-2 -2 -3", "-3 -3 -3", "-2 -3 -2"],
      "Shifting right rounds down, so for negatives it matches @divFloor, not @divTrunc",
      """-5 in binary shifted right once gives -3 because the shift rounds toward minus infinity, exactly as
      `@divFloor(-5, 2)` does. `@divTrunc` cuts toward zero and gives -2."""),

    q("integer-literal-forms", r'''
        const std = @import("std");

        pub fn main() void {
            const sum = 0b101 + 0o17 + 0xA + 1_000;
            std.debug.print("{} {}\n", .{ sum, 0x7f ^ 0b11 });
        }
    ''', "1030 124", ["1032 124", "1030 3", "1030 130"],
      "0o is octal, _ is only a separator, and ^ is bitwise XOR",
      """Binary 101 is 5, octal 17 is 15, hex A is 10 and the underscore in 1_000 is ignored: 5 + 15 + 10 + 1000 =
      1030. `^` is exclusive or, so 0111 1111 xor 0000 0011 is 0111 1100, which is 124."""),

    q("char-arithmetic", r'''
        const std = @import("std");

        pub fn main() void {
            var c: u8 = 'a';
            c += 2;
            const d = 'z' - 'a';
            std.debug.print("{c} {} {} {c}\n", .{ c, c, d, c - 32 });
        }
    ''', "c 99 25 C", ["c c 25 C", "c 99 25 c", "c 99 122 C"],
      "A character is just a number: {} prints it as one, {c} as a letter",
      """`'a'` is the number 97, so adding 2 gives 99, the letter c. `'z' - 'a'` is 25. Subtracting 32 turns a
      lower-case ASCII letter into the upper-case one, and `{c}` prints the byte 67 as C."""),

    # ── Optionals, errors and control flow ─────────────────────────────────
    q("optional-compare", r'''
        const std = @import("std");

        pub fn main() void {
            const a: ?u8 = 5;
            const b: ?u8 = null;
            const c = a orelse 9;
            std.debug.print("{} {} {} {}\n", .{ a == 5, b == null, b == 0, c });
        }
    ''', "true true false 5", ["true true true 5", "false true false 5", "true false false 9"],
      "An optional can be compared with a plain value, and null is not zero",
      """`a == 5` unwraps for the comparison and is true. A null optional equals null but not 0, so `b == 0` is
      false. `orelse` only supplies its default when the optional is null, and `a` holds 5."""),

    q("catch-and-if-error", r'''
        const std = @import("std");

        fn f(x: i32) !i32 {
            return if (x < 0) error.Bad else x * 2;
        }

        pub fn main() void {
            const a = f(2) catch -1;
            const b = f(-2) catch -1;
            if (f(-5)) |v| {
                std.debug.print("{} ", .{v});
            } else |e| {
                std.debug.print("{s} ", .{@errorName(e)});
            }
            std.debug.print("{} {}\n", .{ a, b });
        }
    ''', "Bad 4 -1", ["-10 4 -1", "Bad -1 -1", "Bad 4 4"],
      "if (x) |v| else |e| splits an error union into value and error",
      """`f(-5)` fails, so the else branch runs with the error captured as `e`, and `@errorName` turns it into
      the text Bad. `f(2)` is 4. `f(-2)` fails and `catch -1` replaces it."""),

    q("switch-ranges-and-labeled-block", r'''
        const std = @import("std");

        fn cls(n: u8) []const u8 {
            return switch (n) {
                1...9 => "digit",
                10, 20, 30 => "round",
                else => "big",
            };
        }
        pub fn main() void {
            const v: usize = blk: {
                if (cls(9).len > 4) break :blk 100;
                break :blk 200;
            };
            std.debug.print("{s} {s} {s} {}\n", .{ cls(9), cls(20), cls(25), v });
        }
    ''', "digit round big 100", ["digit big big 100", "digit round big 200", "big round big 100"],
      "A switch prong can be a range or a list, and a labeled block yields a value",
      """`1...9` includes both ends, so 9 is a digit. 20 matches the list `10, 20, 30`, and 25 falls to `else`.
      The labeled block breaks out with 100 because 'digit' has five letters, more than 4."""),

    q("for-else-break-value", r'''
        const std = @import("std");

        pub fn main() void {
            const a = [_]i32{ 1, 3, 4, 7 };
            const first_even = for (a) |x| {
                if (@mod(x, 2) == 0) break x;
            } else -1;
            const first_big = for (a) |x| {
                if (x > 10) break x;
            } else -1;
            std.debug.print("{} {}\n", .{ first_even, first_big });
        }
    ''', "4 -1", ["3 -1", "4 7", "1 -1"],
      "A loop can produce a value with break, and else runs when it never breaks",
      """The first loop breaks at 4 and that is the value of the whole loop expression. The second finds nothing
      above 10, so it finishes normally and its `else` value, -1, is used."""),

    q("labeled-continue-outer", r'''
        const std = @import("std");

        pub fn main() void {
            var count: u32 = 0;
            outer: for (0..4) |i| {
                for (0..4) |j| {
                    if (j > i) continue :outer;
                    if (i == 3) break :outer;
                    count += 1;
                }
            }
            std.debug.print("{}\n", .{count});
        }
    ''', "6", ["10", "7", "5"],
      "continue :label restarts the outer loop; break :label ends it",
      """Row i counts i + 1 steps before `j > i` jumps to the next row: 1 + 2 + 3 = 6 for rows 0 to 2. On row 3
      the first inner step hits `break :outer` before counting, so nothing more is added."""),

    q("while-optional-iterator", r'''
        const std = @import("std");

        const Countdown = struct {
            n: u32,
            fn next(self: *Countdown) ?u32 {
                if (self.n == 0) return null;
                self.n -= 1;
                return self.n;
            }
        };
        pub fn main() void {
            var it = Countdown{ .n = 3 };
            var sum: u32 = 0;
            while (it.next()) |v| sum = sum * 10 + v;
            std.debug.print("{} {}\n", .{ sum, it.n });
        }
    ''', "210 0", ["321 0", "210 3", "21 0"],
      "while (iter.next()) |v| stops at the first null and the capture is the unwrapped value",
      """`next` returns the counter after decrementing it, so the values are 2, 1, 0 and the loop ends when it
      returns null. The digits build 210, and the struct has been used up, so `it.n` is 0."""),

    # ── Structs, slices and values ─────────────────────────────────────────
    q("struct-assignment-copies", r'''
        const std = @import("std");
        const P = struct { x: i32 };

        fn bump(p: P) P {
            return .{ .x = p.x + 1 };
        }

        pub fn main() void {
            var a = P{ .x = 1 };
            var b = a;
            b.x = 9;
            const c = bump(a);
            const d = &a;
            d.x += 10;
            std.debug.print("{} {} {}\n", .{ a.x, b.x, c.x });
        }
    ''', "11 9 2", ["1 9 2", "11 9 12", "11 1 2"],
      "Assigning or passing a struct copies it; only a pointer shares it",
      """`b = a` makes an independent copy, and so does passing `a` by value to `bump`, so neither changes `a`.
      Only `bumpPtr(&a)` reaches the original and adds 10 to its 1."""),

    q("struct-default-fields", r'''
        const std = @import("std");

        const Cfg = struct {
            w: u32 = 80,
            h: u32 = 24,
            title: []const u8 = "none",
        };

        pub fn main() void {
            const a: Cfg = .{ .h = 50 };
            const b = Cfg{ .title = "x", .w = a.h };
            const out = .{ a.w, a.h, a.title, b.w, b.h, b.title };
            std.debug.print("{} {} {s} {} {} {s}\n", out);
        }
    ''', "80 50 none 50 24 x", ["0 50 none 50 0 x", "80 50 none 80 24 x", "80 50 none 50 50 x"],
      "Fields you leave out take their declared defaults",
      """`a` overrides only `h`, so `w` and `title` keep 80 and 'none'. `b` takes its `w` from `a.h` (50) and
      leaves `h` at the default 24; field order in the literal does not matter."""),

    q("slice-writes-through", r'''
        const std = @import("std");

        pub fn main() void {
            var arr = [_]u8{ 1, 2, 3, 4, 5 };
            const s = arr[1..4];
            s[0] = 9;
            const t = s[1..];
            std.debug.print("{} {} {} {}\n", .{ arr[1], s.len, t.len, t[0] });
        }
    ''', "9 3 2 3", ["9 4 3 3", "2 3 2 3", "9 3 2 4"],
      "arr[a..b] excludes b, and a slice of a slice still points at the same memory",
      """`arr[1..4]` holds the elements at indexes 1, 2 and 3, so its length is 3, and writing `s[0]` changes
      `arr[1]` to 9. `s[1..]` drops one more element, leaving 2, and its first element is the 3."""),

    q("pointer-to-array-and-slice", r'''
        const std = @import("std");

        pub fn main() void {
            var arr = [_]i32{ 1, 2, 3, 4 };
            const p = &arr;
            const q: []i32 = p;
            q[0] = 50;
            std.debug.print("{} {} {} {}\n", .{ p.len, q.len, arr[0], p[1] });
        }
    ''', "4 4 50 2", ["4 4 1 2", "8 4 50 2", "4 1 50 2"],
      "A pointer to an array knows its length, and a slice made from it shares memory",
      """`&arr` has type `*[4]i32`, so `.len` is 4 and indexing works without a dereference. Converting it to a
      slice keeps the same four elements, and writing `q[0]` changes the array itself."""),

    q("array-concat-repeat", r'''
        const std = @import("std");

        pub fn main() void {
            const a = [_]u8{ 1, 2 } ++ [_]u8{3};
            const b = [_]u8{0} ** 3;
            const s = "ab" ** 2 ++ "!";
            std.debug.print("{} {} {s} {}\n", .{ a.len, b.len, s, s.len });
        }
    ''', "3 3 abab! 5", ["4 3 ab2! 4", "3 1 abab! 5", "3 3 ab! 3"],
      "++ joins and ** repeats arrays at compile time, and ** binds tighter than ++",
      """`[_]u8{1, 2} ++ [_]u8{3}` is a three-element array and `[_]u8{0} ** 3` has three zeros. In the string,
      `"ab" ** 2` is evaluated first to 'abab', then `++ "!"` appends, for a length of 5."""),

    q("sentinel-terminated-string", r'''
        const std = @import("std");

        pub fn main() void {
            const s: [:0]const u8 = "abc";
            const p: [*:0]const u8 = s;
            const n = std.mem.len(p);
            std.debug.print("{} {} {} {}\n", .{ s.len, s[3], n, p[1] });
        }
    ''', "3 0 3 98", ["4 0 4 98", "3 0 3 b", "3 3 3 98"],
      "A [:0] slice's length excludes the 0 byte, but the 0 is there to read",
      """The sentinel is stored after the data and is not counted: `len` is 3, and `s[3]` is that 0. A `[*:0]`
      pointer has no length at all, so `std.mem.len` walks to the sentinel and finds 3. Indexing gives the byte
      98 for 'b', and `{}` prints it as a number."""),

    q("bufprint-returns-slice", r'''
        const std = @import("std");

        pub fn main() void {
            var buf = [_]u8{0} ** 8;
            const s = std.fmt.bufPrint(&buf, "{d}-{d}", .{ 12, 3 }) catch "x";
            std.debug.print("{s} {} {} {}\n", .{ s, s.len, buf.len, buf[4] });
        }
    ''', "12-3 4 8 0", ["12-3 4 4 0", "12-3 8 8 0", "12-3 4 8 51"],
      "bufPrint returns a slice of just the text it wrote, not of the whole buffer",
      """The buffer stays 8 bytes long, but the returned slice covers only the 4 characters written. The bytes
      after them are untouched, so `buf[4]` is still the 0 it started with."""),

    # ── Enums, unions and optionals ────────────────────────────────────────
    q("enum-explicit-values", r'''
        const std = @import("std");

        const Color = enum(u8) { red, green = 5, blue, _ };

        pub fn main() void {
            const c: Color = .blue;
            const n = @intFromEnum(c) + @intFromEnum(Color.red);
            const g = @intFromEnum(Color.green);
            std.debug.print("{} {} {s}\n", .{ n, g, @tagName(c) });
        }
    ''', "6 5 blue", ["7 5 blue", "1 5 blue", "6 5 green"],
      "After an explicit value the next enum field counts up from it",
      """`red` is 0 and `green` is set to 5, so `blue` continues as 6. The sum 6 + 0 is 6. `@tagName` gives the
      name of the value, blue, not a number."""),

    q("tagged-union-switch", r'''
        const std = @import("std");

        const Shape = union(enum) { circle: u32, rect: struct { w: u32, h: u32 } };

        fn area(s: Shape) u32 {
            return switch (s) {
                .circle => |r| 3 * r * r,
                .rect => |r| r.w * r.h,
            };
        }

        pub fn main() void {
            const a = Shape{ .rect = .{ .w = 3, .h = 4 } };
            const c = Shape{ .circle = 2 };
            std.debug.print("{} {s} {}\n", .{ area(a), @tagName(a), area(c) });
        }
    ''', "12 rect 12", ["12 rect 6", "7 rect 12", "12 circle 12"],
      "A tagged union holds one variant at a time, and switch captures its payload",
      """`a` was built as a rect, so the switch takes the second prong with the payload (3, 4) and gives 12.
      The circle with radius 2 uses the first prong: 3 * 2 * 2 = 12. `@tagName(a)` is the active variant."""),

    q("find-optional-orelse", r'''
        const std = @import("std");

        fn find(s: []const u8, t: u8) ?usize {
            for (s, 0..) |c, i| {
                if (c == t) return i;
            }
            return null;
        }

        pub fn main() void {
            const a = find("hello", 'l');
            const b = find("hello", 'z');
            const c = (find("hello", 'o') orelse 99) + 1;
            std.debug.print("{?} {?} {}\n", .{ a, b, c });
        }
    ''', "2 null 5", ["3 null 5", "2 -1 5", "2 null 100"],
      "An optional keeps null apart from every number, and orelse unwraps it",
      """`find` returns the first match, index 2, wrapped as an optional; no match is null, not -1. For 'o' the
      index is 4, so `orelse` is not used and 4 + 1 gives 5. `{?}` prints a null optional as the word null."""),

    # ── Strings, parsing and floats ────────────────────────────────────────
    q("split-versus-tokenize", r'''
        const std = @import("std");

        pub fn main() void {
            var it = std.mem.splitScalar(u8, "a,,b", ',');
            var n: usize = 0;
            while (it.next()) |_| n += 1;
            var t = std.mem.tokenizeScalar(u8, "a,,b", ',');
            var m: usize = 0;
            while (t.next()) |_| m += 1;
            std.debug.print("{} {}\n", .{ n, m });
        }
    ''', "3 2", ["2 2", "3 3", "2 3"],
      "split keeps empty pieces between neighbouring delimiters; tokenize drops them",
      """`a,,b` has two commas next to each other, so `splitScalar` returns three pieces: 'a', an empty one, and
      'b'. `tokenizeScalar` treats any run of delimiters as one and skips empties, giving only 'a' and 'b'."""),

    q("parse-int-edge-cases", r'''
        const std = @import("std");

        pub fn main() void {
            const a = std.fmt.parseInt(u8, "0xff", 0) catch 0;
            const b = std.fmt.parseInt(i32, " 12", 10) catch -1;
            const c = std.fmt.parseInt(u8, "300", 10) catch 0;
            const d = std.fmt.parseInt(i32, "-12", 10) catch 0;
            std.debug.print("{} {} {} {}\n", .{ a, b, c, d });
        }
    ''', "255 -1 0 -12", ["0 12 0 -12", "255 12 255 -12", "255 -1 44 -12"],
      "parseInt is strict: no spaces, no overflow, and base 0 reads the prefix",
      """With base 0 the `0x` prefix selects hexadecimal, so "0xff" is 255. A leading space is not allowed, and
      300 does not fit a u8; both are errors, so `catch` supplies -1 and 0. A minus sign is fine for a signed
      type."""),

    q("float-format-rounding", r'''
        const std = @import("std");

        pub fn main() void {
            std.debug.print("{d:.0} {d:.0} {d:.0} {d:.1} {d:.1}\n", .{
                0.5, 1.5, 2.5, 2.25, 0.35,
            });
        }
    ''', "1 2 3 2.3 0.4", ["0 2 2 2.2 0.3", "1 2 3 2.2 0.3", "0 2 2 2.3 0.4"],
      "Zig rounds the shortest decimal form half up; C-style printf rounds the exact binary value",
      """Zig first finds the shortest digits that identify the float, such as 0.35, and rounds those half up. So 0.5
      becomes 1, 2.5 becomes 3 and 0.35 becomes 0.4, even though the stored number is slightly below 0.35 and
      printf would show 0.3. Ties do not go to the even neighbour."""),

    q("f32-versus-f64", r'''
        const std = @import("std");

        fn third(comptime T: type, n: T) T {
            return n / 3;
        }

        pub fn main() void {
            const a = third(f32, 1);
            const b = third(f64, 1);
            std.debug.print("{d} {d} {d}\n", .{ a, b, third(f64, 2) });
        }
    ''', "0.33333334 0.3333333333333333 0.6666666666666666", ["0.3333333 0.3333333333333333 0.6666666666666666",
      "0.33333334 0.33333334 0.6666667", "0.33 0.33 0.67"],
      "{d} prints the shortest digits that identify the type, so f32 prints fewer",
      """Both results are the nearest float to a third, but an f32 only needs eight digits to be told apart from
      its neighbours, while an f64 needs sixteen. The longer f64 text is not more correct, just a more precise
      type."""),

    q("float-to-int-conversions", r'''
        const std = @import("std");

        fn cut(x: f64) i32 {
            return @intFromFloat(x);
        }

        pub fn main() void {
            std.debug.print("{} {} {} {}\n", .{
                cut(3.9), cut(-3.9), cut(@round(3.5)), cut(@floor(-3.1)),
            });
        }
    ''', "3 -3 4 -4", ["4 -4 4 -3", "3 -4 3 -4", "3 -3 3 -3"],
      "@intFromFloat truncates toward zero; rounding takes a separate builtin",
      """The conversion simply drops the fraction, so 3.9 becomes 3 and -3.9 becomes -3. `@round(3.5)` rounds
      away from zero to 4, and `@floor(-3.1)` goes down to -4 before the conversion."""),

    q("abs-returns-unsigned", r'''
        const std = @import("std");

        fn mag(x: i8) u8 {
            return @abs(x);
        }

        pub fn main() void {
            const t = @typeName(@TypeOf(@abs(@as(i8, -3))));
            std.debug.print("{} {} {s}\n", .{ mag(-128), mag(5), t });
        }
    ''', "128 5 u8", ["-128 5 i8", "128 5 i8", "127 5 u8"],
      "@abs of a signed integer returns the unsigned type, so even -128 fits",
      """The absolute value of the smallest i8, -128, is 128, which cannot be an i8 but fits a u8. Zig's `@abs`
      therefore returns the unsigned counterpart of its argument's type."""),

    # ── Control flow and comptime ──────────────────────────────────────────
    q("while-continue-expression", r'''
        const std = @import("std");

        pub fn main() void {
            var i: u32 = 0;
            var sum: u32 = 0;
            while (i < 6) : (i += 2) {
                if (i == 2) continue;
                sum += i;
            }
            std.debug.print("{} {}\n", .{ i, sum });
        }
    ''', "6 4", ["4 4", "6 6", "6 2"],
      "The expression after the colon runs after every pass, even on continue",
      """On the pass with i = 2 the `continue` skips the sum, but `i += 2` still happens, so the loop goes on to
      4. The passes add 0 and 4, giving 4, and the loop ends when i reaches 6."""),

    q("comptime-int-is-unbounded", r'''
        const std = @import("std");

        pub fn main() void {
            const big = 1 << 100;
            const x = big >> 98;
            var y: u8 = 5;
            y += x;
            std.debug.print("{} {s} {}\n", .{ x, @typeName(@TypeOf(x)), y });
        }
    ''', "4 comptime_int 9", ["4 i32 9", "4 u8 9", "4 comptime_int 5"],
      "Integer literals are comptime_int, which has no size limit until it meets a real type",
      """`1 << 100` is fine because a comptime integer can be as big as needed. After shifting back it is 4 and
      still has the type `comptime_int`; only when it is added to a u8 is it checked to fit. So y is 5 + 4."""),
)
