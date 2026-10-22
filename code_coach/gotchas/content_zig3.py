"""Gotchas, Zig (third deck): zig build-exe in Debug (0.16), output via std.debug.print (stderr); see langs.py.

New angles on the first two decks: bit patterns and integer conversions, std helpers (math, mem, ascii, fmt),
capture forms (by pointer, optional, tagged union), loops that yield values, vectors, packed structs and type
names. Values are passed through variables or parameters so nothing is folded at compile time.
"""

from __future__ import annotations

from .items import Item, make

q = make("zig")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ──────────────────────────────────────────────────────
    q("ascii-digit-value-and-case", r'''
        const std = @import("std");

        pub fn main() void {
            const text = "407";
            var n: u32 = 0;
            for (text) |c| n = n * 10 + (c - '0');
            const up = std.ascii.toUpper('q');
            const digit = std.ascii.isDigit('x');
            std.debug.print("{} {c} {} {}\n", .{ n, up, digit, text[0] - '0' });
        }
    ''', "407 Q false 4", ["407 q false 4", "407 Q false 52", "4 Q true 4"],
      "A character is a number: subtracting '0' turns a digit character into its value",
      """The byte for '4' is 52, and subtracting the byte for '0' (48) leaves 4. Doing this for each character and
      multiplying the running total by ten builds 407. `std.ascii.toUpper` works on a byte, and `{c}` prints it as a
      letter, while a plain `{}` would print its number."""),

    q("method-self-by-value-versus-pointer", r'''
        const std = @import("std");
        const C = struct {
            n: u32,
            fn bumped(self: C) C { var c = self; c.n += 1; return c; }
            fn bump(self: *C) void { self.n += 1; }
        };
        pub fn main() void {
            var a = C{ .n = 1 };
            const b = a.bumped();
            a.bump();
            a.bump();
            std.debug.print("{} {}\n", .{ a.n, b.n });
        }
    ''', "3 2", ["3 3", "1 2", "2 2"],
      "A method taking self by value works on a copy; only a *Self method changes the original",
      """`bumped` receives a copy of the struct, changes the copy and returns it, so `a` is untouched and `b` holds
      2. `bump` takes a pointer, and `a.bump()` passes the address of `a` automatically, so the two calls raise it
      from 1 to 3."""),

    q("optional-capture-by-pointer", r'''
        const std = @import("std");

        pub fn main() void {
            var o: ?u32 = 5;
            if (o) |*p| p.* *= 2;
            if (o) |p| {
                var q = p;
                q += 100;
            }
            const gone: ?u32 = null;
            std.debug.print("{} {}\n", .{ o.?, gone orelse 0 });
        }
    ''', "10 0", ["5 0", "110 0", "10 null"],
      "|p| captures a copy of the payload; |*p| captures a pointer into the optional",
      """In `if (o) |*p|` the capture is a pointer to the value stored inside the optional, so `p.* *= 2` changes `o`
      to 10. The plain `|p|` form copies the payload, and changing the copy leaves `o` alone. `orelse` supplies a
      default for the null one."""),

    q("while-else-runs-unless-break", r'''
        const std = @import("std");

        pub fn main() void {
            var i: u32 = 0;
            const r = while (i < 5) : (i += 1) {
                if (i * i > 5) break i;
            } else 99;
            const q: u32 = while (i < 3) : (i += 1) {} else 7;
            std.debug.print("{} {}\n", .{ r, q });
        }
    ''', "3 7", ["99 7", "3 99", "3 3"],
      "A while loop used as a value gives the break value, or its else value when the condition ends it",
      """The first loop breaks with `i` as soon as `i * i > 5`, at 3, so `else` is skipped and the result is 3. The
      second loop starts with `i` already 3, so its condition is false at once, the body never runs, and the loop
      produces its `else` value, 7."""),

    q("for-zips-slices", r'''
        const std = @import("std");

        pub fn main() void {
            const a = [_]u32{ 1, 2, 3 };
            const b = [_]u32{ 4, 5, 6 };
            var dot: u32 = 0;
            var idx: usize = 0;
            for (a, b, 0..) |x, y, i| {
                dot += x * y;
                idx += i;
            }
            for (0..3) |_| dot += 1;
            std.debug.print("{} {}\n", .{ dot, idx });
        }
    ''', "35 3", ["32 3", "35 6", "35 0"],
      "A for loop can walk several slices (and a range) in step, and _ ignores a capture",
      """`for (a, b, 0..)` pairs the elements in step: 1*4 + 2*5 + 3*6 = 32, and the index runs 0, 1, 2 for a total
      of 3. The second loop has no use for its counter, so it is captured as `_`, and it adds 1 three times:
      35."""),

    q("catch-switch-on-error", r'''
        const std = @import("std");
        fn f(n: u8) !u8 {
            if (n == 0) return error.NotFound;
            return if (n > 9) error.Bad else n;
        }
        fn g(n: u8) u8 {
            return f(n) catch |e| switch (e) {
                error.NotFound => 100,
                error.Bad => 200,
            };
        }
        fn h(n: u8) !u8 { return (try f(n)) + 1; }
        pub fn main() void {
            const r = .{ g(0), g(5), g(50), h(3) catch 77, h(0) catch 77 };
            std.debug.print("{} {} {} {} {}\n", r);
        }
    ''', "100 5 200 4 77", ["100 5 200 3 77", "100 5 200 4 0", "0 5 50 4 77"],
      "catch |e| switch handles each error by name, and try hands the error on to the caller",
      """`g` catches the error and switches on it, so `NotFound` gives 100 and `Bad` gives 200, while a good value
      passes through. `h` uses `try`: for 3 it returns 3 + 1, but for 0 the error leaves `h` immediately, and the
      caller's `catch 77` provides the fallback."""),

    # ── Medium ───────────────────────────────────────────────────────────
    q("float-bit-patterns", r'''
        const std = @import("std");

        pub fn main() void {
            var one: f32 = 1.0;
            one += 0.0;
            const neg: f32 = -2.0;
            const bits: u32 = @bitCast(one);
            const nbits: u32 = @bitCast(neg);
            std.debug.print("{} {} {x} {}\n", .{ bits, nbits, bits, nbits >> 31 });
        }
    ''', "1065353216 3221225472 3f800000 1", ["1 4294967294 1 1", "1065353216 3221225472 3f800000 0",
                                             "1065353216 1073741824 3f800000 1"],
      "@bitCast reinterprets the bits of a float as an integer instead of converting the value",
      """The 32 bits of the float 1.0 are 0x3f800000, which is 1065353216 as an integer: a reinterpretation, not
      the value 1. A negative float has its top (sign) bit set, so -2.0 is 0xc0000000 = 3221225472, and shifting it
      right by 31 leaves just that sign bit."""),

    q("maxint-minint-and-negation", r'''
        const std = @import("std");
        fn neg(x: i8) i8 { return -%x; }
        fn sneg(x: i8) i8 { return 0 -| x; }
        pub fn main() void {
            const lo = std.math.minInt(i8);
            const hi = std.math.maxInt(u8);
            const r = .{ hi, lo, neg(lo), sneg(lo), neg(5) };
            std.debug.print("{} {} {} {} {}\n", r);
        }
    ''', "255 -128 -128 127 -5", ["255 -128 128 127 -5", "255 -128 -128 -128 -5", "256 -128 -128 127 -5"],
      "Negating the smallest signed integer wraps back to itself; saturating negation stops at the maximum",
      """An i8 holds -128 to 127, so +128 does not exist. `-%x` wraps around and gives -128 again, whereas `0 -| x`
      saturates at the biggest value, 127. A plain `-x` would panic in a Debug build. `maxInt(u8)` is 255, not
      256."""),

    q("signed-to-unsigned-conversions", r'''
        const std = @import("std");

        pub fn main() void {
            var b: i32 = -7;
            b += 0;
            const bits: u32 = @bitCast(b);
            const wide: i64 = b;
            const sum = @as(u32, 5) +% bits;
            const back: i32 = @bitCast(sum);
            std.debug.print("{} {} {} {}\n", .{ bits, wide, sum, back });
        }
    ''', "4294967289 -7 4294967294 -2", ["7 -7 12 12", "4294967289 -7 4294967294 4294967294",
                                        "4294967289 4294967289 4294967294 -2"],
      "@bitCast keeps the bits of a negative number; widening with a plain assignment keeps its value",
      """-7 stored in 32 bits is 2^32 - 7 = 4294967289 when read as unsigned. Assigning an i32 to an i64 is a safe
      widening and keeps -7. Adding 5 with wrapping gives 2^32 - 2, which read back as signed is -2."""),

    q("std-math-integer-helpers", r'''
        const std = @import("std");

        pub fn main() void {
            const root = std.math.sqrt(@as(u32, 17));
            const ceil = std.math.divCeil(u32, 7, 2) catch 0;
            std.debug.print("{} {} {} {} {s}\n", .{
                std.math.pow(u32, 3, 4), root, ceil,
                std.math.clamp(@as(i32, 15), 0, 10), @typeName(@TypeOf(root)),
            });
        }
    ''', "81 4 4 10 u16", ["81 4 3 10 u32", "81 4.12 4 10 u16", "12 4 4 10 u16"],
      "Integer sqrt rounds down and returns a narrower type; divCeil rounds up and can fail",
      """`std.math.sqrt` on a u32 does an integer square root, 4 for 17, and its result type is the half-width u16.
      `divCeil` rounds 7 / 2 up to 4 and returns an error union, which `catch` unwraps. `pow(u32, 3, 4)` is 3 to the
      fourth power, and `clamp` limits 15 to 10."""),

    q("type-names-of-arrays-and-slices", r'''
        const std = @import("std");

        pub fn main() void {
            var arr = [_]u8{ 1, 2, 3, 4 };
            const s: []u8 = arr[0..2];
            std.debug.print("{s} {s} {s} {s}\n", .{
                @typeName(@TypeOf(arr)), @typeName(@TypeOf(&arr)),
                @typeName(@TypeOf(s)), @typeName(@TypeOf("hello")),
            });
        }
    ''', "[4]u8 *[4]u8 []u8 *const [5:0]u8", ["[4]u8 []u8 []u8 []const u8", "[4]u8 *[4]u8 []u8 [5]u8",
                                             "[4]u8 *[4]u8 [2]u8 *const [5:0]u8"],
      "The array length is part of the type; a string literal is a pointer to a null-terminated array",
      """`arr` has type `[4]u8`, and `&arr` is a pointer to that array. A slice `[]u8` carries its length at run time
      and has no length in its type. A string literal such as "hello" is a constant pointer to a five-byte array
      with a zero after it, `*const [5:0]u8`."""),

    q("std-mem-search-and-compare", r'''
        const std = @import("std");

        pub fn main() void {
            const s = "hello";
            const m = std.mem;
            std.debug.print("{any} {any} {any} {s} {s} {}\n", .{
                m.indexOf(u8, s, "ll"), m.lastIndexOfScalar(u8, s, 'l'),
                m.indexOf(u8, s, "z"), @tagName(m.order(u8, "abc", "abd")),
                @tagName(m.order(u8, "a", "ab")), m.eql(u8, "he", s[0..2]),
            });
        }
    ''', "2 3 null lt lt true", ["2 2 null lt lt true", "2 3 -1 lt gt true", "3 3 null gt lt false"],
      "indexOf gives an optional position, and order compares byte by byte, with a prefix sorting first",
      """`indexOf` returns where "ll" starts, 2, and `lastIndexOfScalar` the last l, 3; a missing needle gives
      null rather than -1. `order` returns `.lt`, `.eq` or `.gt`: "abc" is less than "abd", and "a" is less than "ab"
      because a shorter prefix sorts first. `eql` compares contents."""),

    q("sort-reverse-swap-in-place", r'''
        const std = @import("std");

        pub fn main() void {
            var arr = [_]i32{ 5, 2, 9, 1 };
            std.mem.sort(i32, &arr, {}, std.sort.asc(i32));
            const sorted = arr;
            std.mem.reverse(i32, &arr);
            std.mem.swap(i32, &arr[0], &arr[3]);
            std.debug.print("{any} {any}\n", .{ sorted, arr });
        }
    ''', "{ 1, 2, 5, 9 } { 1, 5, 2, 9 }", ["{ 1, 2, 5, 9 } { 9, 5, 2, 1 }", "{ 5, 2, 9, 1 } { 1, 5, 2, 9 }",
                                         "{ 1, 2, 5, 9 } { 1, 2, 5, 9 }"],
      "Sorting, reversing and swapping change the array itself; assigning an array copies it first",
      """`sort` rearranges the array in place, and `const sorted = arr` makes an independent copy of the sorted array.
      `reverse` then gives 9, 5, 2, 1, and swapping the first and last elements gives 1, 5, 2, 9, without
      touching the copy."""),

    q("errdefer-capture-and-defer-order", r'''
        const std = @import("std");

        fn work() !void {
            defer std.debug.print("A ", .{});
            errdefer |e| std.debug.print("E:{s} ", .{@errorName(e)});
            defer std.debug.print("B ", .{});
            return error.Boom;
        }

        pub fn main() void {
            work() catch std.debug.print("caught\n", .{});
        }
    ''', "B E:Boom A caught", ["A E:Boom B caught", "B A E:Boom caught", "caught B E:Boom A"],
      "defer and errdefer share one last-in-first-out stack, and errdefer can capture the error",
      """The deferred statements run in reverse order of their declaration when `work` returns: first `B`, then
      the `errdefer`, which only runs because an error is being returned and can capture it as `e`, then `A`. The
      caller's `catch` runs afterwards."""),

    q("union-capture-by-pointer-mutates", r'''
        const std = @import("std");

        const U = union(enum) { n: i32, f: f32 };

        pub fn main() void {
            var u = U{ .n = 1 };
            switch (u) {
                .n => |*p| p.* += 10,
                .f => {},
            }
            const copy = u;
            u.n += 1;
            std.debug.print("{} {} {s}\n", .{ u.n, copy.n, @tagName(u) });
        }
    ''', "12 11 n", ["11 11 n", "12 12 n", "12 1 n"],
      "|*p| in a switch edits the payload in place; assigning a union copies it",
      """The capture `|*p|` is a pointer into the union's payload, so `p.* += 10` changes `u.n` to 11. The line
      `const copy = u` copies the whole union at that moment, so the later `u.n += 1` makes `u.n` 12 but leaves
      `copy.n` at 11. The active tag stays `n`."""),

    q("string-to-enum-lookup", r'''
        const std = @import("std");

        const Color = enum { red, green, blue };

        pub fn main() void {
            const a = std.meta.stringToEnum(Color, "green");
            const b = std.meta.stringToEnum(Color, "purple");
            const c: Color = @enumFromInt(2);
            std.debug.print("{any} {any} {s} {} {}\n", .{
                a, b, @tagName(c), @intFromEnum(a.?), std.meta.fields(Color).len,
            });
        }
    ''', ".green null blue 1 3", [".green -1 blue 1 3", "green null blue 1 3", ".green null blue 2 3"],
      "stringToEnum returns an optional, and @enumFromInt and @intFromEnum convert by position",
      """The lookup returns the case `.green` for a known name and null for an unknown one; there is no error
      or -1. The integer 2 converts back to the third case, `blue`, and `green` has the number 1 because numbering
      starts at 0. `fields` lists the three cases at compile time."""),

    q("inline-for-over-a-tuple", r'''
        const std = @import("std");

        pub fn main() void {
            inline for (.{ u8, u16, i32 }) |T| {
                std.debug.print("{} ", .{@sizeOf(T)});
            }
            inline for (.{ 1, "a", 2.5 }) |v| {
                std.debug.print("{s} ", .{@typeName(@TypeOf(v))});
            }
            std.debug.print("\n", .{});
        }
    ''', "1 2 4 comptime_int *const [1:0]u8 comptime_float", ["1 2 4 i32 []const u8 f64",
                                                              "1 2 4 comptime_int []const u8 comptime_float",
                                                              "8 16 32 comptime_int *const [1:0]u8 comptime_float"],
      "inline for unrolls at compile time, so each pass can have a different type",
      """A tuple can mix types, and `inline for` expands the loop body once per element, so `T` is a different type each
      time and `@sizeOf` gives the byte sizes 1, 2 and 4. The literal values keep their compile-time types:
      `comptime_int`, a pointer to a one-byte string, and `comptime_float`."""),

    q("f32-sum-prints-shorter", r'''
        const std = @import("std");

        pub fn main() void {
            var x: f64 = 0.1;
            x += 0.2;
            var y: f32 = 0.1;
            y += 0.2;
            std.debug.print("{d} {d} {} {}\n", .{ y, x, x == 0.3, y == 0.3 });
        }
    ''', "0.3 0.30000000000000004 false true", ["0.3 0.3 true true", "0.30000001 0.30000000000000004 false false",
                                               "0.3 0.30000000000000004 false false"],
      "{d} prints the shortest text that round-trips; an f32 sum can land exactly on the f32 nearest 0.3",
      """In 64-bit floats 0.1 + 0.2 is the number just above 0.3, so it prints with all its digits and is not equal
      to 0.3. In 32-bit floats the sum rounds to exactly the same value as the literal 0.3, so `y == 0.3` is true and
      the shortest text that identifies it is just 0.3."""),

    q("min-max-builtin-narrow-types", r'''
        const std = @import("std");

        pub fn main() void {
            const a: u8 = 200;
            const m = @min(a, 1000);
            const big = @max(a, 1000);
            std.debug.print("{} {s} {} {s}\n", .{
                m, @typeName(@TypeOf(m)), big, @typeName(@TypeOf(big)),
            });
        }
    ''', "200 u8 1000 u10", ["200 comptime_int 1000 comptime_int", "200 u8 1000 u8", "200 u16 1000 u16"],
      "@min and @max pick the narrowest type that can hold the possible results",
      """The smaller of a u8 and 1000 can never exceed 255, so the result still fits in a u8. The larger might be
      as big as 1000, which needs 10 bits, so Zig gives that result the type u10 rather than a fixed width like
      u16."""),

    q("fmt-width-fill-and-alignment", r'''
        const std = @import("std");

        pub fn main() void {
            std.debug.print("|{d:>5}|{d:<5}|{d:^5}|{d:0>5}|{s:*^7}|{x:0>4}|\n", .{
                42, 42, 42, 42, "ab", 255,
            });
        }
    ''', "|   42|42   | 42  |00042|**ab***|00ff|", ["|42   |   42| 42  |00042|**ab***|00ff|",
                                                    "|   42|42   |  42 |00042|***ab**|00ff|",
                                                    "|   42|42   | 42  |42000|**ab***|ff00|"],
      "In {d:0>5}, 0 is the fill, > the alignment and 5 the width; ^ puts the extra space on the right",
      """After the colon come an optional fill character, an alignment (`<` left, `^` centre, `>` right) and a width.
      `{d:0>5}` right-aligns in five columns padded with zeros, and `{x:0>4}` does the same in hexadecimal.
      When centring leaves an odd number of spaces the extra one goes on the right, for example `**ab***`."""),

    q("any-format-of-arrays-and-optionals", r'''
        const std = @import("std");

        pub fn main() void {
            const a = [_]u8{ 1, 2 };
            const none: ?u8 = null;
            const some: ?u8 = 7;
            std.debug.print("{any} {any} {any} {any} {any} {any}\n", .{
                a, "hi", none, some, error.Boom, true,
            });
        }
    ''', "{ 1, 2 } { 104, 105 } null 7 error.Boom true", ["{ 1, 2 } hi null 7 error.Boom true",
                                                          "[1, 2] { 104, 105 } null Some(7) Boom true",
                                                          "{ 1, 2 } { 104, 105 } null 7 error.Boom 1"],
      "{any} prints a slice of bytes as numbers; {s} is what shows text",
      """With `{any}` an array is shown in braces, element by element, and a string is just an array of bytes, so
      "hi" appears as 104 and 105. An optional prints its payload or `null`, an error value prints as
      `error.Boom`, and a bool as `true`. Use `{s}` to print bytes as text."""),

    q("parse-int-underscores-and-signs", r'''
        const std = @import("std");

        pub fn main() void {
            const a = std.fmt.parseInt(u32, "1_000", 10) catch 0;
            const b = std.fmt.parseInt(u32, "1_000", 0) catch 0;
            const c = std.fmt.parseInt(i32, "+5", 10) catch 0;
            const d = std.fmt.parseInt(u8, "-1", 10) catch 99;
            const e = std.fmt.parseInt(i32, "-0x10", 0) catch 99;
            std.debug.print("{} {} {} {} {}\n", .{ a, b, c, d, e });
        }
    ''', "1000 1000 5 99 -16", ["0 1000 5 99 -16", "1000 1000 5 0 -16", "1000 1000 0 99 -16"],
      "parseInt accepts underscores and a leading +, and a minus sign is an error for an unsigned type",
      """Zig's number parser allows `_` between digits, so "1_000" is 1000 in either base mode. A leading `+` is fine.
      For an unsigned type "-1" is rejected, so `catch` supplies 99. With base 0 the prefix chooses the base, and
      "-0x10" is minus sixteen."""),

    q("vector-operations-are-elementwise", r'''
        const std = @import("std");

        pub fn main() void {
            const a = @Vector(3, i32){ 1, 2, 3 };
            const b = @Vector(3, i32){ 3, 2, 1 };
            const prod = a * b;
            const same = @reduce(.And, a == a);
            std.debug.print("{} {} {} {}\n", .{
                @reduce(.Add, prod), @reduce(.Max, a), same, (a + b)[2]
,
            });
        }
    ''', "10 3 true 4", ["14 3 true 4", "10 3 false 4", "10 6 true 3"],
      "Arithmetic on a @Vector works per element, and == gives a vector of booleans",
      """`a * b` multiplies lane by lane, giving 3, 4 and 3, and `@reduce(.Add, ...)` sums the lanes to 10.
      `@reduce(.Max, a)` is the largest lane, 3. Comparing vectors with `==` gives one bool per lane, and `.And`
      reduces them to true."""),

    q("many-pointer-indexing-and-slicing", r'''
        const std = @import("std");

        pub fn main() void {
            var arr = [_]u8{ 10, 20, 30, 40 };
            const p: [*]u8 = &arr;
            const q = p + 2;
            q[0] += 1;
            const mid = p[1..3];
            std.debug.print("{} {} {} {}\n", .{ q[0], mid.len, mid[1], arr[2] });
        }
    ''', "31 2 31 31", ["31 3 31 31", "30 2 30 31", "31 2 30 30"],
      "A [*]T pointer has no length: index it, add to it, and slice it with explicit bounds",
      """Adding 2 to the many-item pointer makes `q` point at the third element, so `q[0] += 1` changes the array itself
      and `arr[2]` is 31. Slicing a pointer needs both bounds, and `p[1..3]` is a two-element slice with a length
      of 2, whose second element is the same changed 31."""),

    q("packed-struct-bit-layout", r'''
        const std = @import("std");

        const F = packed struct(u8) { a: u4, b: u4 };

        pub fn main() void {
            const f = F{ .a = 1, .b = 2 };
            const raw: u8 = @bitCast(f);
            const g: F = @bitCast(@as(u8, 0xA5));
            std.debug.print("{} {} {} {}\n", .{ raw, @sizeOf(F), g.a, g.b });
        }
    ''', "33 1 5 10", ["18 1 10 5", "33 2 5 10", "33 1 10 5"],
      "In a packed struct the first field takes the lowest bits",
      """Fields are packed from the least significant bit up, so `a = 1` occupies the low four bits and `b = 2` the
      high four: 0x21, which is 33. The whole struct is one byte. Reading 0xA5 back, the low nibble 5 is `a` and the
      high nibble 10 is `b`."""),

    q("arraylist-with-a-fixed-buffer", r'''
        const std = @import("std");

        pub fn main() !void {
            var buf = [_]u8{0} ** 256;
            var fba = std.heap.FixedBufferAllocator.init(&buf);
            const al = fba.allocator();
            var list: std.ArrayList(u32) = .empty;
            try list.append(al, 1);
            try list.append(al, 2);
            try list.append(al, 3);
            const first = list.orderedRemove(0);
            const last = list.pop().?;
            try list.insert(al, 0, 9);
            const n = list.items.len;
            std.debug.print("{any} {} {} {}\n", .{ list.items, first, last, n });
        }
    ''', "{ 9, 2 } 1 3 2", ["{ 9, 2, 3 } 1 3 3", "{ 2, 9 } 1 3 2", "{ 9, 2 } 1 2 2"],
      "In current Zig an ArrayList starts empty and every call that may grow it takes the allocator",
      """The list is created with `.empty` and no allocator inside it, so `append` and `insert` need `al`.
      `orderedRemove(0)` removes and returns the first item (1), leaving 2 and 3. `pop` takes the last (3) and
      returns it as an optional, so `.?` unwraps it. Inserting 9 at the front gives { 9, 2 }."""),
)
