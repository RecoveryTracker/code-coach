"""Gotchas, Ruby (third deck): run by ruby (4.x on this machine); portability notes are in langs.py.

New angles on the first two decks: Enumerable one-liners, string and number helpers, the object model's corners,
exceptions and pattern matching. Hash and Set are never printed with `inspect`, string literals are never mutated,
and every card prints one line.
"""

from __future__ import annotations

from .items import Item, make

q = make("ruby")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ──────────────────────────────────────────────────────
    q("unary-minus-and-power", r'''
        p [-2 ** 2, (-2) ** 2, 2 ** 3 ** 2, -2.abs, -2.0 ** 2]
    ''', "[-4, 4, 512, 2, -4.0]", ["[4, 4, 64, 2, 4.0]", "[-4, 4, 64, -2, -4.0]",
                                  "[-4, -4, 512, 2, 4.0]"],
      "** binds tighter than a minus sign, and it groups to the right",
      """`-2 ** 2` is `-(2 ** 2)`, so -4, and so is `-2.0 ** 2`; the parentheses in `(-2) ** 2` make 4. A chain
      `2 ** 3 ** 2` is `2 ** (3 ** 2)`, which is 512. A minus glued to an integer literal belongs to the number,
      so `-2.abs` is 2."""),

    q("hash-reinsert-moves-to-end", r'''
        h = { a: 1, b: 2, c: 3 }
        h[:a] = 9
        h.delete(:b)
        h[:b] = 4
        p [h.keys, h.values]
    ''', "[[:a, :c, :b], [9, 3, 4]]", ["[[:a, :b, :c], [9, 4, 3]]", "[[:a, :c, :b], [1, 3, 4]]",
                                       "[[:b, :a, :c], [4, 9, 3]]"],
      "Overwriting keeps a key's place; deleting and adding it again puts it last",
      """A hash remembers insertion order. Assigning to an existing key only changes its value, so `:a` stays
      first. Deleting `:b` forgets its position, and the new `:b` is appended at the end."""),

    q("digits-come-least-first", r'''
        n = 1234
        p [n.digits, n.digits.sum, n.to_s(2).size, "ff".to_i(16), "12".to_i(2),
           10.gcd(4), 10.lcm(4), Integer.sqrt(17)]
    ''', "[[4, 3, 2, 1], 10, 11, 255, 1, 2, 20, 4]",
      ["[[1, 2, 3, 4], 10, 11, 255, 1, 2, 20, 4]", "[[4, 3, 2, 1], 10, 11, 255, 12, 2, 20, 4]",
       "[[4, 3, 2, 1], 10, 10, 255, 1, 2, 40, 4.12]"],
      "digits lists the least significant digit first, and to_i(base) stops at a bad digit",
      """`1234.digits` is [4, 3, 2, 1]: the ones place comes first. `"12".to_i(2)` reads the 1, hits the 2 that is
      not a binary digit and stops, giving 1. 1234 in binary has 11 digits, and `Integer.sqrt` rounds down to a
      whole number."""),

    q("tap-versus-then", r'''
        a = 5.then { |x| x + 1 }
        b = 5.tap { |x| x + 1 }
        c = [1, 2].tap { |l| l << 3 }.size
        d = [3, 1, 2].sort.then { |l| l.first(2) }
        p [a, b, c, d]
    ''', "[6, 5, 3, [1, 2]]", ["[6, 6, 3, [1, 2]]", "[5, 5, 2, [1, 2]]", "[6, 5, 3, [1, 2, 3]]"],
      "tap returns the receiver; then returns the block's value",
      """`then` passes the object on and gives back whatever the block returns. `tap` ignores the block's result
      and returns the original object, so `5.tap { |x| x + 1 }` is still 5. A `<<` inside a tap block does change
      the array, because it is the same object."""),

    q("instance-of-versus-is-a", r'''
        p [3.is_a?(Comparable), 3.instance_of?(Numeric), 3.kind_of?(Numeric),
           Integer.is_a?(Class), Class.is_a?(Module), nil.class,
           NilClass.superclass, Integer.instance_of?(Class)]
    ''', "[true, false, true, true, true, NilClass, Object, true]",
      ["[true, true, true, true, true, NilClass, Object, true]",
       "[false, false, true, true, true, NilClass, Object, true]",
       "[true, false, true, false, true, nil, Object, false]"],
      "instance_of? needs the exact class; is_a? and kind_of? also accept ancestors and mixed-in modules",
      """3 is an Integer, so `instance_of?(Numeric)` is false while `is_a?(Numeric)` is true. Comparable is a
      module that Integer includes, so `is_a?(Comparable)` is true too. Classes are objects: Integer is an
      instance of Class, and Class itself descends from Module."""),

    q("string-append-integer-is-a-codepoint", r'''
        s = +"a"
        s << 98
        p [s, "a".ord, 98.chr, "abc".sum, "abc".bytes.sum, "a".succ.ord]
    ''', "[\"ab\", 97, \"b\", 294, 294, 98]",
      ["[\"a98\", 97, \"b\", 294, 294, 98]", "[\"ab\", 97, \"98\", 294, 294, 98]",
       "[\"ab\", 97, \"b\", 3, 294, 98]"],
      "<< with an Integer appends the character with that code point",
      """For a string, `<<` given an integer appends `98.chr`, which is "b", not the text "98". `"abc".sum` is the
      sum of the bytes (97 + 98 + 99 = 294), the same as summing `bytes`."""),

    q("partition-when-missing", r'''
        p ["a.b.c".partition("."), "a.b.c".rpartition("."), "abc".partition("x"),
           "abc".rpartition("x"), "x=1=2".split("=", 2)]
    ''', "[[\"a\", \".\", \"b.c\"], [\"a.b\", \".\", \"c\"], [\"abc\", \"\", \"\"], [\"\", \"\", \"abc\"], [\"x\", \"1=2\"]]",
      ["[[\"a\", \".\", \"b.c\"], [\"a.b\", \".\", \"c\"], [\"abc\", \"\", \"\"], [\"abc\", \"\", \"\"], [\"x\", \"1=2\"]]",
       "[[\"a\", \".\", \"b.c\"], [\"a\", \".\", \"b.c\"], [\"abc\"], [\"abc\"], [\"x\", \"1\", \"2\"]]",
       "[[\"a\", \"b.c\"], [\"a.b\", \"c\"], [\"abc\", \"\", \"\"], [\"\", \"\", \"abc\"], [\"x\", \"1=2\"]]"],
      "partition always returns three parts; when the separator is missing rpartition puts the text last",
      """`partition` splits at the first match and `rpartition` at the last, both into [before, separator, after].
      With no match, `partition` returns the whole string, then two empty strings, and `rpartition` returns two
      empty strings, then the whole string. `split("=", 2)` stops after two pieces."""),

    q("each-with-index-forms", r'''
        a = %w[a b c]
        p [a.each_with_index.map { |x, i| x * (i + 1) },
           a.map.with_index(1) { |x, i| "#{i}#{x}" },
           a.each.with_index(1).to_a.last,
           a.each_with_index.select { |x, i| i.odd? }]
    ''', "[[\"a\", \"bb\", \"ccc\"], [\"1a\", \"2b\", \"3c\"], [\"c\", 3], [[\"b\", 1]]]",
      ["[[\"a\", \"bb\", \"ccc\"], [\"1a\", \"2b\", \"3c\"], [3, \"c\"], [\"b\"]]",
       "[[\"a\", \"bb\", \"ccc\"], [\"0a\", \"1b\", \"2c\"], [\"c\", 2], [[\"b\", 1]]]",
       "[[\"\", \"b\", \"cc\"], [\"1a\", \"2b\", \"3c\"], [\"c\", 3], [[\"b\", 1]]]"],
      "with_index(1) shifts only the number, and select keeps the [element, index] pair",
      """`each_with_index` starts at 0, so "a" is repeated once, "b" twice. `with_index(1)` starts counting from 1
      and gives the pair as [element, index]. Selecting on `each_with_index` returns the pairs that passed, not
      just the elements."""),

    q("enumerator-next-and-peek", r'''
        e = [1, 2].each
        r = [e.next, e.peek, e.next]
        r << (begin; e.next; rescue StopIteration => x; x.class; end)
        r << e.rewind.next
        p r
    ''', "[1, 2, 2, StopIteration, 1]", ["[1, 2, 2, nil, 1]", "[1, 1, 2, StopIteration, 1]",
                                         "[1, 2, 2, StopIteration, 2]"],
      "peek looks without moving; running off the end raises StopIteration until you rewind",
      """`next` moves the enumerator on, `peek` shows the following element without consuming it, so the second
      `next` returns the same 2. When the elements run out the next call raises StopIteration rather than
      returning nil. `rewind` starts again from the first element."""),

    # ── Medium ───────────────────────────────────────────────────────────
    q("each-slice-and-cons", r'''
        a = (1..5).to_a
        p [a.each_slice(2).to_a, a.each_cons(2).count, a.each_slice(2).map(&:sum),
           a.each_cons(3).to_a.last]
    ''', "[[[1, 2], [3, 4], [5]], 4, [3, 7, 5], [3, 4, 5]]",
      ["[[[1, 2], [3, 4]], 4, [3, 7], [3, 4, 5]]", "[[[1, 2], [3, 4], [5]], 5, [3, 7, 5], [3, 4, 5]]",
       "[[[1, 2], [3, 4], [5]], 4, [3, 7, 5], [4, 5]]"],
      "each_slice keeps a short last group; each_cons only makes full windows",
      """`each_slice(2)` cuts the array into pieces of two and keeps the leftover [5]. `each_cons(2)` slides a
      window one step at a time, so five elements give four windows, and `each_cons(3)` stops at [3, 4, 5]."""),

    q("inject-is-a-left-fold", r'''
        p [[10, 2, 3].inject(:-), [2, 3, 2].inject(:**),
           [1, 2, 3].inject { |a, b| a * 10 + b }, [5].inject(:-),
           [].inject(1, :*), [1, 2, 3].inject(10, :+)]
    ''', "[5, 64, 123, 5, 1, 16]", ["[-15, 64, 123, 5, 1, 16]", "[5, 512, 123, 5, 1, 16]",
                                    "[5, 64, 123, nil, 1, 6]"],
      "inject folds from the left, and a single element is returned untouched",
      """`inject(:-)` computes (10 - 2) - 3 = 5, and `inject(:**)` computes (2 ** 3) ** 2 = 64, not 2 ** (3 ** 2).
      With one element there is nothing to combine, so the element itself comes back. An initial value
      goes first: `inject(10, :+)` is 10 + 1 + 2 + 3."""),

    q("each-with-object-immutable-memo", r'''
        a = (1..4).each_with_object(0) { |x, sum| sum += x }
        b = (1..4).each_with_object([]) { |x, acc| acc += [x] }
        c = (1..4).each_with_object([]) { |x, acc| acc << x }
        p [a, b, c.size]
    ''', "[0, [], 4]", ["[10, [1, 2, 3, 4], 4]", "[0, [1, 2, 3, 4], 4]", "[10, [], 4]"],
      "each_with_object hands every step the same object, so += only rebinds a local",
      """The memo is passed to each iteration unchanged, and the block's result is thrown away. `sum += x` makes a
      new integer for the block's own variable, so the memo stays 0, and `acc += [x]` builds a new array and
      drops it. Only a mutating call such as `<<` changes the shared object. (`inject` is the one that carries the
      block's result forward.)"""),

    q("lazy-runs-element-by-element", r'''
        log = []
        r = (1..Float::INFINITY).lazy
              .map { |x| log << "m#{x}"; x * 2 }
              .select { |x| log << "s#{x}"; x % 4 == 0 }
              .first(2)
        puts "#{r} #{log.join(' ')}"
    ''', "[4, 8] m1 s2 m2 s4 m3 s6 m4 s8",
      ["[4, 8] m1 m2 m3 m4 s2 s4 s6 s8", "[4, 8] m1 s2 m2 s4 m3 s6 m4 s8 m5",
       "[4, 8] m1 s2 m2 s4 m3 s6 m4 s8 m5 s10"],
      "A lazy chain pushes one element all the way through before touching the next",
      """Each number goes through `map` and then `select` before the next number starts, and the chain stops as
      soon as `first(2)` has two results. So the log interleaves m and s steps and ends at m4 and s8: nothing is
      computed for 5."""),

    q("take-while-stops-at-first-miss", r'''
        a = [1, 3, 5, 6, 7, 8]
        p [a.take_while(&:odd?), a.drop_while(&:odd?), a.select(&:odd?),
           a.slice_when { |x, y| y.odd? != x.odd? }.to_a.size,
           a.chunk_while { |x, y| y == x + 2 }.to_a]
    ''', "[[1, 3, 5], [6, 7, 8], [1, 3, 5, 7], 4, [[1, 3, 5], [6], [7], [8]]]",
      ["[[1, 3, 5, 7], [6, 8], [1, 3, 5, 7], 4, [[1, 3, 5], [6], [7], [8]]]",
       "[[1, 3, 5], [6, 7, 8], [1, 3, 5, 7], 3, [[1, 3, 5], [6, 7], [8]]]",
       "[[1, 3, 5], [6, 7, 8], [1, 3, 5, 7], 4, [[1, 3, 5, 7], [6, 8]]]"],
      "take_while and drop_while act on the leading run only; select looks at everything",
      """`take_while(&:odd?)` stops at the first even number (6) and never looks at the 7. `drop_while` removes the
      same leading run and keeps everything after it. `slice_when` cuts between neighbours where the parity
      changes, giving four groups, and `chunk_while` joins neighbours that are exactly 2 apart."""),

    q("flat-map-flattens-one-level", r'''
        p [[[1, 2], [3]].flat_map { |x| x }, [[1, [2]], [3]].flat_map { |x| x },
           [1, 2].flat_map { |x| [[x]] }, [[1, [2, [3]]]].flatten(1),
           [[1, [2, [3]]]].flatten]
    ''', "[[1, 2, 3], [1, [2], 3], [[1], [2]], [1, [2, [3]]], [1, 2, 3]]",
      ["[[1, 2, 3], [1, 2, 3], [[1], [2]], [1, [2, [3]]], [1, 2, 3]]",
       "[[1, 2, 3], [1, [2], 3], [1, 2], [1, [2, [3]]], [1, 2, 3]]",
       "[[1, 2, 3], [1, [2], 3], [[1], [2]], [1, 2, [3]], [1, 2, 3]]"],
      "flat_map removes exactly one level of nesting from what the block returns",
      """`flat_map` is `map` followed by `flatten(1)`. A nested array two levels deep keeps its inner level, and
      `[[x]]` loses only its outer array. `flatten(1)` on `[[1, [2, [3]]]]` unwraps the outer array and leaves the
      rest, while a plain `flatten` goes all the way down."""),

    q("zip-pads-with-nil", r'''
        a = [1, 2, 3]
        p [a.zip([4, 5]), [4, 5].zip(a), a.zip([4, 5, 6], [7]),
           [[1, 2], [3, 4]].transpose]
    ''', "[[[1, 4], [2, 5], [3, nil]], [[4, 1], [5, 2]], [[1, 4, 7], [2, 5, nil], [3, 6, nil]], [[1, 3], [2, 4]]]",
      ["[[[1, 4], [2, 5]], [[4, 1], [5, 2]], [[1, 4, 7]], [[1, 3], [2, 4]]]",
       "[[[1, 4], [2, 5], [3, nil]], [[4, 1], [5, 2], [nil, 3]], [[1, 4, 7], [2, 5, nil], [3, 6, nil]], [[1, 3], [2, 4]]]",
       "[[[1, 4], [2, 5], [3, nil]], [[4, 1], [5, 2]], [[1, 4, 7], [2, 5, nil], [3, 6, nil]], [[1, 2], [3, 4]]]"],
      "zip follows the receiver's length and fills the gaps with nil",
      """The result has one entry per element of the array you call `zip` on. A shorter partner is padded with
      nil; a longer one is cut off, so `[4, 5].zip(a)` has two pairs. `transpose` swaps rows and columns."""),

    q("max-by-takes-the-first-tie", r'''
        w = %w[bb aa c]
        p [w.max_by(&:size), w.min_by(&:size), w.reverse.max_by(&:size), w.max,
           [[1, :a], [1, :b]].max_by(&:first)]
    ''', "[\"bb\", \"c\", \"aa\", \"c\", [1, :a]]",
      ["[\"aa\", \"c\", \"bb\", \"c\", [1, :b]]", "[\"bb\", \"c\", \"bb\", \"c\", [1, :b]]",
       "[\"bb\", \"c\", \"aa\", \"bb\", [1, :a]]"],
      "When several elements tie, max_by and min_by return the first one they met",
      """`max_by` keeps the first element whose key is the largest, so equal keys never replace it: "bb" before
      "aa", but "aa" before "bb" when the order is swapped. Plain `max` compares the text itself, not the length, so
      "c" is the largest of the three."""),

    q("sum-needs-an-initial-value-for-text", r'''
        p [(["a", "b"].sum rescue "TypeError"), %w[a b].sum(""), [[1], [2]].sum([]),
           [1, 2.5].sum, [1r, 2].sum, [].sum(0.0)]
    ''', "[\"TypeError\", \"ab\", [1, 2], 3.5, (3/1), 0.0]",
      ["[\"ab\", \"ab\", [1, 2], 3.5, (3/1), 0.0]", "[\"TypeError\", \"ab\", [1, 2], 3.5, 3, 0]",
       "[\"TypeError\", \"ab\", [1, 2], 3, (3/1), 0.0]"],
      "sum starts from the integer 0, so text and arrays need their own starting value",
      """`["a", "b"].sum` tries `0 + "a"` and raises a TypeError; passing `""` or `[]` as the start makes it
      concatenate. Mixed numbers follow normal contagion: an integer and a float give a float, and a rational with
      an integer stays a rational, printed as (3/1)."""),

    q("comparable-from-spaceship", r'''
        class V
          include Comparable
          attr_reader :n
          def initialize(n)
            @n = n
          end

          def <=>(other)
            n <=> other.n
          end
        end
        a = V.new(1)
        p [a == V.new(1), a.equal?(V.new(1)), V.new(3).between?(a, V.new(5)),
           V.new(9).clamp(a, V.new(5)).n, [V.new(2), a].min.n]
    ''', "[true, false, true, 5, 1]", ["[false, false, true, 5, 1]", "[true, false, true, 9, 1]",
                                      "[true, true, true, 5, 2]"],
      "Including Comparable gives == and the ordering helpers from just <=>",
      """Comparable defines `==`, `<`, `between?` and `clamp` in terms of `<=>`, so two different objects with
      equal numbers are `==` (while `equal?` still checks identity). `clamp(a, V.new(5))` pulls 9 down to the
      upper bound, and `min` on an array uses `<=>` as well."""),

    q("string-center-tr-squeeze", r'''
        puts ["ab".center(7, "*"), "hello".tr("el", "ip"), "hello".tr("a-y", "b-z"),
              "aaabbb".squeeze, "mississippi".squeeze("sp"), "hello".delete("l"),
              "banana".count("an")].join(" ")
    ''', "**ab*** hippo ifmmp ab misisipi heo 5",
      ["***ab** hippo ifmmp ab misisipi heo 5", "**ab*** hippo ifmmp ab misisippi heo 5",
       "**ab*** hippo ifmmp ab misisipi heo 2"],
      "center puts the extra pad on the right; count takes a set of characters, not a substring",
      """Five pad characters split as two on the left and three on the right. `tr` maps character by character, and
      `"a-y"` to `"b-z"` shifts every letter by one. `squeeze("sp")` collapses only runs of s and p, leaving
      the double letters elsewhere, and `count("an")` counts every a and every n: 3 + 2."""),

    q("string-index-edge-slices", r'''
        s = "hello world"
        p [s[1..3], s[1, 3], s[-5..], s[20], s[11], s[11, 2], s[12, 2], s["wor"],
           s[/o\s?w/]]
    ''', "[\"ell\", \"ell\", \"world\", nil, nil, \"\", nil, \"wor\", \"o w\"]",
      ["[\"ell\", \"ell\", \"world\", nil, \"\", \"\", nil, \"wor\", \"o w\"]",
       "[\"ell\", \"el\", \"world\", nil, nil, \"\", \"\", \"wor\", \"o w\"]",
       "[\"ell\", \"ell\", \"world\", nil, nil, nil, nil, \"wor\", \"o w\"]"],
      "A single index at the length is nil, but a start at the length gives an empty string",
      """With a start and a length, a start equal to the length is still valid and returns "", while one past it
      returns nil. A lone index at the length (`s[11]`) has no character to give, so it is nil. A string argument
      returns itself when found, and a regexp returns the matched text."""),

    q("spaceship-and-casecmp", r'''
        p ["a" <=> "b", "b" <=> "a", "a" <=> "a", "a" <=> 1, "A" <=> "a",
           "abc" <=> "abd", "Z".casecmp("a"), "Z".casecmp?("z")]
    ''', "[-1, 1, 0, nil, -1, -1, 1, true]", ["[-1, 1, 0, -1, 1, -1, -1, true]",
                                              "[-1, 1, 0, nil, 1, -1, 1, true]",
                                              "[-1, 1, 0, nil, -1, -1, -1, false]"],
      "Uppercase sorts before lowercase, and comparing with a non-string gives nil",
      """`<=>` compares bytes: "A" (65) comes before "a" (97), so the result is -1. Comparing a string with an
      integer is not an error, it just returns nil. `casecmp` ignores case, so "Z" is greater than "a" (1), and
      `casecmp?` is true for "Z" and "z"."""),

    q("scan-and-match-groups", r'''
        s = "a1b22c333"
        p [s.scan(/\d+/), s.scan(/([a-z])(\d+)/).last, s =~ /\d{2}/,
           Regexp.last_match(0), s.match(/(?<ch>[a-z])3/)[:ch], s[/b(\d)/, 1]]
    ''', "[[\"1\", \"22\", \"333\"], [\"c\", \"333\"], 3, \"22\", \"c\", \"2\"]",
      ["[[\"1\", \"22\", \"333\"], \"c333\", 3, \"22\", \"c\", \"2\"]",
       "[[\"1\", \"22\", \"333\"], [\"c\", \"333\"], 2, \"22\", \"c\", \"22\"]",
       "[[\"1\", \"22\", \"333\"], [\"c\", \"333\"], 3, \"22\", \"b\", \"2\"]"],
      "scan returns a flat list without groups and a list of group arrays with them",
      """Without capture groups `scan` returns the matched strings; with groups it returns one array of captures
      per match. `=~` returns the index of the match (3 for the first "22"), and `Regexp.last_match` is the
      match it just made. `s[/b(\\d)/, 1]` returns only the first group, "2", not the whole "b2"."""),

    q("gsub-with-hash-and-backrefs", r'''
        puts ["cat".gsub(/[a-z]/, "a" => "4"), "heLlo".gsub(/l/i, "l" => "_"),
              "john smith".gsub(/(\w+) (\w+)/, '\2, \1'),
              "john smith".gsub(/(\w+) (\w+)/, "\\2 \\1")].join("|")
    ''', "4|he_o|smith, john|smith john",
      ["c4t|he_o|smith, john|smith john", "4|he_o|john, smith|smith john",
       "4|he_o|smith, john|\\2 \\1"],
      "A hash replaces matches by lookup, and a key that is missing becomes an empty string",
      """In `gsub(pattern, hash)` each matched text is looked up in the hash, and a miss gives nil, which is
      replaced by nothing: "c" and "t" vanish and only the "a" becomes "4". "L" is not a key of the second hash
      either, so it disappears. `'\\2, \\1'` and `"\\\\2 \\\\1"` are the same back-references: the double quotes just
      need the backslashes doubled."""),

    q("range-step-and-percent", r'''
        r = (1..10)
        p [r.step(3).to_a, (r % 4).to_a, (1.0..2.0).step(0.5).to_a,
           (1..).first(3), (r % 4).class, (1...10).step(3).to_a]
    ''', "[[1, 4, 7, 10], [1, 5, 9], [1.0, 1.5, 2.0], [1, 2, 3], Enumerator::ArithmeticSequence, [1, 4, 7]]",
      ["[[1, 4, 7, 10], [1, 5, 9], [1.0, 1.5, 2.0], [1, 2, 3], Array, [1, 4, 7, 10]]",
       "[[1, 4, 7], [1, 5, 9], [1.0, 1.5], [1, 2, 3], Enumerator::ArithmeticSequence, [1, 4, 7]]",
       "[[3, 6, 9], [4, 8], [1.0, 1.5, 2.0], [1, 2, 3], Enumerator::ArithmeticSequence, [1, 4, 7]]"],
      "Range#% is step; an exclusive range still excludes its end, and a float range includes it",
      """`range % n` is another name for `step(n)` and returns a lazy arithmetic sequence rather than an array.
      Stepping starts at the first element: 1, 4, 7, 10. The three-dot range stops before 10, so 10 is
      missing from the last list. An endless range with `first(3)` stops after three elements."""),

    q("integer-and-float-conversions", r'''
        p [Float("1e3"), Float("1_0.5"), Float("1.5abc", exception: false),
           Float(" 2 "), Integer("0x1f", 16), Integer(" 42\n"),
           Integer("4 2", exception: false), Integer(3.99), Integer("-0b11")]
    ''', "[1000.0, 10.5, nil, 2.0, 31, 42, nil, 3, -3]",
      ["[1000, 10.5, nil, 2.0, 31, 42, nil, 3, -3]", "[1000.0, 105.0, 1.5, 2.0, 31, 42, 42, 4, -3]",
       "[1000.0, 10.5, nil, 2.0, 31, 42, nil, 4, 3]"],
      "Float() and Integer() are strict about junk but allow underscores, surrounding blanks and prefixes",
      """Unlike `to_f` and `to_i`, the capitalised conversions raise (or give nil with `exception: false`) on
      trailing junk, so "1.5abc" and "4 2" are rejected. They do accept `_` between digits, surrounding whitespace and
      `0x`/`0b` prefixes. `Integer(3.99)` truncates toward zero to 3."""),

    q("rational-and-complex-basics", r'''
        p [Rational(3, 6), 1/3r + 1/6r, 0.5.to_r, Rational("0.75"),
           Complex(1, 2) * Complex(0, 1), Complex(3, 4).abs]
    ''', "[(1/2), (1/2), (1/2), (3/4), (-2+1i), 5.0]",
      ["[(3/6), (1/2), (1/2), (3/4), (-2+1i), 5.0]", "[(1/2), 0.5, (1/2), (3/4), (-2+1i), 5.0]",
       "[(1/2), (1/2), (1/2), (3/4), (2+1i), 5]"],
      "Rationals reduce themselves and add exactly; i squared is minus one",
      """`Rational(3, 6)` is stored reduced as (1/2), and 1/3 + 1/6 is exactly 1/2 with no rounding. A float like
      0.5 converts to its exact fraction, and a decimal string gives the exact decimal. In complex multiplication
      (1+2i)(i) = i + 2i² = -2 + 1i, and the absolute value is a float."""),

    q("divmod-sign-conventions", r'''
        p [7.divmod(2), -7.divmod(2), 7.divmod(-2), -7.remainder(2), 7.5.divmod(2),
           7.pow(2, 5)]
    ''', "[[3, 1], [-4, 1], [-4, -1], -1, [3, 1.5], 4]",
      ["[[3, 1], [-3, -1], [-3, 1], -1, [3, 1.5], 4]", "[[3, 1], [-4, 1], [-4, -1], 1, [3.0, 1.5], 4]",
       "[[3, 1], [-4, 1], [-4, -1], -1, [3, 1.5], 49]"],
      "divmod floors, so the remainder takes the divisor's sign; remainder truncates",
      """`divmod` returns the floored quotient and the matching modulo, so -7 divides into -4 remainder 1, and
      7 by -2 into -4 remainder -1. `remainder` is the C-style one with the sign of the dividend: -1. With a float
      the quotient is still an integer, and `pow(2, 5)` is 7 squared modulo 5."""),

    q("product-rotate-combination", r'''
        a = [1, 2, 3]
        p [a.product([4, 5]).last, a.rotate, a.rotate(-1), a.rotate(4),
           a.combination(2).to_a.last, [[1, 2], [3]].product([0]).size]
    ''', "[[3, 5], [2, 3, 1], [3, 1, 2], [2, 3, 1], [2, 3], 2]",
      ["[[3, 5], [2, 3, 1], [3, 1, 2], [4, 1, 2], [2, 3], 2]",
       "[[3, 5], [3, 1, 2], [2, 3, 1], [2, 3, 1], [2, 3], 3]",
       "[[5, 3], [2, 3, 1], [3, 1, 2], [2, 3, 1], [1, 3], 2]"],
      "rotate wraps around, and a count larger than the size wraps again",
      """`rotate` moves the first element to the end; a negative count rotates the other way, and `rotate(4)` on
      three elements is the same as `rotate(1)`. `product` pairs every element with every other, in order, so
      the last pair is [3, 5]. The last 2-combination of [1, 2, 3] is [2, 3]."""),

    q("flatten-compact-uniq-block", r'''
        a = [3, nil, [1, nil, [2, nil]], 3, 4]
        p [a.flatten.compact, a.flatten(1).compact.size, a.compact.flatten.uniq,
           [1, 2, 3, 4].uniq { |x| x % 2 }, %w[a B A b].uniq(&:downcase)]
    ''', "[[3, 1, 2, 3, 4], 5, [3, 1, nil, 2, 4], [1, 2], [\"a\", \"B\"]]",
      ["[[3, 1, 2, 3, 4], 6, [3, 1, 2, 4], [1, 2], [\"a\", \"B\"]]",
       "[[3, 1, 2, 3, 4], 5, [3, 1, nil, 2, 4], [1, 2, 3, 4], [\"a\", \"B\"]]",
       "[[3, 1, 2, 4], 5, [3, 1, nil, 2, 4], [1, 2], [\"a\", \"B\", \"A\", \"b\"]]"],
      "compact only removes top-level nils; uniq with a block keeps the first of each key",
      """After `compact` the nils nested inside the inner arrays survive, so flattening later brings one back.
      `flatten(1)` leaves [2, nil] as a single element, which `compact` keeps. `uniq` with a block compares the
      block's results and keeps the first element for each, so only one odd and one even number remain."""),

    q("dig-and-fetch", r'''
        cfg = [{ a: [10, { b: 20 }] }, nil]
        p [cfg.dig(0, :a, 1, :b), cfg.dig(1, :a), cfg.dig(5, :a),
           (cfg.dig(0, :a, 0, :b) rescue "TypeError"), cfg.fetch(5, :d),
           cfg.fetch(1, :d), cfg.fetch(5) { |i| i * 2 }]
    ''', "[20, nil, nil, \"TypeError\", :d, nil, 10]",
      ["[20, nil, nil, nil, :d, :d, 10]", "[20, nil, nil, \"TypeError\", :d, :d, 10]",
       "[20, nil, nil, \"TypeError\", nil, nil, 5]"],
      "dig stops quietly at nil but raises on a value that cannot dig; fetch defaults only past the end",
      """`dig` returns nil as soon as an element is nil, and also for an index that does not exist. Reaching the
      integer 10 and asking it to dig further raises a TypeError. `fetch(1, :d)` finds a real element, which
      happens to be nil, so the default is not used; `fetch(5)` is out of range and calls the block with 5."""),

    q("slice-bang-removes-and-returns", r'''
        a = [1, 2, 3, 4, 5, 6]
        x = a.slice!(1, 2)
        y = a.slice!(-1)
        z = a.slice!(9)
        w = a.slice!(1..)
        p [x, y, z, w, a]
    ''', "[[2, 3], 6, nil, [4, 5], [1]]", ["[[2, 3], [6], nil, [4, 5], [1]]",
                                           "[[2, 3], 6, nil, [4, 5], [1, 4, 5]]",
                                           "[[2, 3], 6, [], [4, 5], [1]]"],
      "slice! cuts the elements out and returns them; a single index returns the element itself",
      """`slice!(1, 2)` removes two elements and returns them as an array, while `slice!(-1)` with one index
      returns the bare element. An index past the end returns nil and changes nothing. The final
      `slice!(1..)` takes everything from index 1 on."""),

    q("merge-with-block-and-bang", r'''
        a = { x: 1, y: 2 }
        b = { y: 10, z: 3 }
        m = a.merge(b) { |_k, old, new| old + new }
        n = a.merge!(b) { |_, old, _| old }.size
        p [m.to_a, a.merge(b).values_at(:x, :y, :z), n, a[:y], a.to_a.last]
    ''', "[[[:x, 1], [:y, 12], [:z, 3]], [1, 10, 3], 3, 2, [:z, 3]]",
      ["[[[:x, 1], [:y, 12], [:z, 3]], [1, 2, 3], 3, 2, [:z, 3]]",
       "[[[:x, 1], [:y, 10], [:z, 3]], [1, 10, 3], 3, 10, [:z, 3]]",
       "[[[:x, 1], [:y, 12], [:z, 3]], [1, 10, 3], 2, 2, [:y, 2]]"],
      "Without a block merge lets the argument win; the block is only called for keys both hashes have",
      """The block runs only for the clashing key `:y`, and its result (2 + 10) is stored. Without a block the
      second hash wins, so `a.merge(b)[:y]` is 10. `merge!` changes `a` in place: the block keeps the old value
      for `:y`, and the new key `:z` is added at the end."""),

    q("default-proc-and-identity-hash", r'''
        h = Hash.new { |_hash, k| "no #{k}" }
        a = h[:x]
        s1 = +"k"
        s2 = +"k"
        i = {}.compare_by_identity
        i[s1] = 1
        i[s2] = 2
        i[s1] = 3
        p [a, h.size, h.key?(:x), i.size, i[s1], i[+"k"], i.compare_by_identity?]
    ''', "[\"no x\", 0, false, 2, 3, nil, true]",
      ["[\"no x\", 1, true, 2, 3, nil, true]", "[\"no x\", 0, false, 1, 3, 3, true]",
       "[\"no x\", 0, false, 2, 2, 3, true]"],
      "A default block stores nothing unless it assigns; an identity hash tells equal strings apart",
      """This default block only returns a string, so the hash stays empty. In a hash that compares by identity,
      two separate strings with the same text are different keys, so the size is 2, assigning through `s1` again
      replaces only that entry, and a third equal string finds nothing."""),

    # ── Harder: the object model, blocks and errors ─────────────────────────
    q("protected-versus-private", r'''
        class Acct
          def initialize(b)
            @b = b
          end

          def >(other) = bal > other.bal
          def peek(other) = other.secret
          def own = self.secret

          protected def bal = @b
          private def secret = 42
        end
        a = Acct.new(5)
        b = Acct.new(3)
        p [a > b, (a.bal rescue "NoMethodError"),
           (a.peek(b) rescue "NoMethodError"), a.own]
    ''', "[true, \"NoMethodError\", \"NoMethodError\", 42]",
      ["[true, 5, \"NoMethodError\", 42]", "[true, \"NoMethodError\", 42, 42]",
       "[true, \"NoMethodError\", \"NoMethodError\", \"NoMethodError\"]"],
      "protected allows calls on other instances from inside the class; private only allows self",
      """A protected method can be called with an explicit receiver by another object of the same class, which is
      how `>` reads `other.bal`, but not from outside. A private method cannot be called on another object even
      from inside the class, so `other.secret` fails. Since Ruby 2.7 `self.secret` is allowed for private methods,
      so `own` works."""),

    q("define-method-and-instance-variables", r'''
        class K
          [:a, :b].each_with_index do |n, i|
            define_method("get_#{n}") { i * 10 }
            define_method("set_#{n}") { |v| instance_variable_set("@#{n}", v) }
          end
        end
        k = K.new
        k.set_b(7)
        p [k.get_a, k.get_b, k.instance_variable_get(:@b),
           k.instance_variable_get(:@a), k.instance_variables,
           K.instance_methods(false).size]
    ''', "[0, 10, 7, nil, [:@b], 4]",
      ["[0, 10, 7, nil, [:@a, :@b], 4]", "[0, 10, 7, 0, [:@b], 4]", "[0, 0, 7, nil, [:@b], 2]"],
      "define_method blocks close over the loop variables; unset instance variables are nil and unlisted",
      """Each `define_method` block remembers the `i` of its own iteration, so `get_b` returns 10. Setting `@b` creates
      that variable only; `@a` was never assigned, so reading it gives nil and it is missing from
      `instance_variables`. Four methods were defined by the loop."""),

    q("struct-equality-and-splat", r'''
        P = Struct.new(:x, :y)
        a = P.new(1, 2)
        x, y = *a
        p [a == P.new(1, 2), a.equal?(P.new(1, 2)), a.to_a, x + y,
           a.eql?(P.new(1, 2.0)), a == P.new(1, 2.0), P.new(1).y,
           (P.new(1, 2, 3) rescue "ArgumentError")]
    ''', "[true, false, [1, 2], 3, false, true, nil, \"ArgumentError\"]",
      ["[false, false, [1, 2], 3, false, true, nil, \"ArgumentError\"]",
       "[true, false, [1, 2], 3, true, true, nil, \"ArgumentError\"]",
       "[true, false, [1, 2], 3, false, false, 0, \"ArgumentError\"]"],
      "Structs compare by value, == converts numbers but eql? does not, and missing members are nil",
      """Two structs of the same class with equal members are `==`. `==` compares members with `==`, so 2 and 2.0
      match, while `eql?` compares with `eql?` and rejects them. Members you leave out are nil, and too many
      arguments raise an ArgumentError ("struct size differs")."""),

    q("frozen-error-details", r'''
        begin
          "abc".freeze << "d"
        rescue => e
          puts [e.class, e.class.superclass, e.message, e.receiver].join("|")
        end
    ''', "FrozenError|RuntimeError|can't modify frozen String: \"abc\"|abc",
      ["RuntimeError|StandardError|can't modify frozen String|abc",
       "FrozenError|StandardError|can't modify frozen String: \"abc\"|abc",
       "FrozenError|RuntimeError|can't modify frozen String: \"abcd\"|abcd"],
      "Modifying a frozen object raises FrozenError, a RuntimeError that remembers the receiver",
      """`FrozenError` is a subclass of `RuntimeError`, and its message includes the inspected object. The
      string was not changed because the check happens before the append, and `receiver` returns the original
      frozen "abc"."""),

    q("class-instance-variable-versus-class-variable", r'''
        class A
          class << self
            attr_accessor :n
          end
          @n = 5
          @@shared = 0
          def self.shared = @@shared
          def self.bump = @@shared += 1
        end
        class B < A; end
        B.bump
        p [A.n, B.n, A.shared, B.shared]
    ''', "[5, nil, 1, 1]", ["[5, 5, 1, 1]", "[5, nil, 0, 1]", "[5, nil, 1, 0]"],
      "A class-level @variable belongs to one class object; a @@variable is shared by the subclasses",
      """`@n` set in the class body is an instance variable of the class object `A`; the subclass `B` is a different
      object and has none, so `B.n` is nil. `@@shared` is one variable that `A` and `B` both see, so bumping it
      through `B` is visible from `A`."""),

    q("retry-runs-ensure-once", r'''
        log = []
        n = 0
        begin
          n += 1
          log << "try#{n}"
          raise "fail" if n < 3
          log << "done"
        rescue
          log << "rescued"
          retry if n < 3
        ensure
          log << "ensure"
        end
        puts log.join(",")
    ''', "try1,rescued,try2,rescued,try3,done,ensure",
      ["try1,rescued,ensure,try2,rescued,ensure,try3,done,ensure", "try1,rescued,try2,rescued,try3,ensure",
       "try1,rescued,try2,rescued,try3,done,rescued,ensure"],
      "retry jumps back to the start of begin, and ensure runs only when the whole block is left",
      """`retry` re-runs the `begin` body without leaving the block, so the `ensure` clause is not triggered by
      it. Only the third pass finishes normally; then `done` is logged and `ensure` runs once. The rescue clause
      is skipped on that pass because nothing was raised."""),

    q("raise-inside-rescue-sets-cause", r'''
        begin
          begin
            Integer("x")
          rescue ArgumentError
            raise TypeError, "wrapped"
          end
        rescue => e
          puts [e.class, e.message, e.cause.class, e.cause.message].join("|")
        end
    ''', "TypeError|wrapped|ArgumentError|invalid value for Integer(): \"x\"",
      ["TypeError|wrapped||", "ArgumentError|invalid value for Integer(): \"x\"|NilClass|",
       "TypeError|wrapped|ArgumentError|wrapped"],
      "An exception raised while handling another one keeps the first as its cause",
      """When `raise` runs inside a `rescue` clause, Ruby sets the new exception's `cause` to the one being handled.
      The outer rescue sees the TypeError, and `e.cause` still holds the original ArgumentError with its own
      message."""),

    q("exception-message-and-to-s", r'''
        class E1 < StandardError; end
        class E2 < StandardError
          def message = "custom"
        end
        r = [E1.new.message, E1.new("m").message, E2.new("m").message,
             E2.new("m").to_s, (raise E2, "x" rescue $!.message)]
        puts r.join("|")
    ''', "E1|m|custom|m|custom",
      ["|m|custom|m|custom", "E1|m|m|m|x", "E1|m|custom|custom|custom"],
      "An exception without a message reports its class name, and overriding message does not change to_s",
      """`StandardError.new` with no argument has the class name as its message, so `E1.new.message` is "E1".
      `message` just calls `to_s`, but overriding `message` leaves `to_s` alone: it still returns the "m" given
      to the constructor, while `message` itself answers "custom" everywhere, even for a raised E2."""),

    q("rescue-clause-order", r'''
        def t(x)
          r = [:start]
          begin
            Integer(x)
          rescue TypeError then r << :type
          rescue ArgumentError, RangeError then r << :arg
          rescue StandardError then r << :std
          else r << :else
          ensure r << :ens
          end
          r.join(",")
        end
        puts [t("1"), t(nil), t("z")].join(" ")
    ''', "start,else,ens start,type,ens start,arg,ens",
      ["start,ens start,type,ens start,arg,ens", "start,else,ens start,std,ens start,arg,ens",
       "start,else,ens start,type,ens start,arg,std,ens"],
      "The first matching rescue wins; else runs only when nothing was raised; ensure always runs",
      """`Integer(nil)` raises a TypeError, and `Integer("z")` an ArgumentError; each is taken by the first clause
      that names it, so the general `StandardError` clause is never reached. A successful conversion skips every
      rescue and runs `else`. `ensure` is added last in all three cases."""),

    q("catch-and-throw", r'''
        r = catch(:found) do
          [1, 2, 3].each do |i|
            [10, 20].each { |j| throw :found, i * j if i * j > 25 }
          end
          :none
        end
        p [r, catch(:x) { 5 }, catch { |tag| throw tag, 7 },
           catch(:a) { catch(:b) { throw :a, 1 }; 2 }]
    ''', "[40, 5, 7, 1]", ["[:none, 5, 7, 1]", "[60, 5, 7, 2]", "[40, 5, 7, 2]"],
      "throw unwinds all the way to the catch with the same tag, skipping code in between",
      """`throw :found, 40` leaves both loops and makes the `catch` block return 40, so `:none` is never
      reached. A block that finishes normally returns its last value. An inner `catch(:b)` does not catch
      `:a`: the throw passes through it and ends the outer catch, so the trailing `2` never runs."""),

    q("case-in-patterns", r'''
        def m(x)
          case x
          in [Integer => a, *rest] if rest.empty? then "one #{a}"
          in [Integer, Integer] then "pair"
          in { name: String => n, age: } then "#{n}/#{age}"
          in [] then "empty"
          in nil then "nil"
          else "other"
          end
        end
        h = { name: "a", age: 3, x: 1 }
        puts [m([1]), m([1, 2]), m(h), m([]), m([1, 2, 3])].join(" ")
    ''', "one 1 pair a/3 empty other",
      ["one 1 one 1 a/3 empty other", "one 1 pair other empty other", "one 1 pair a/3 empty pair"],
      "Array patterns match the whole array, hash patterns ignore extra keys, and a guard can reject",
      """`[1]` matches the first pattern and its guard. `[1, 2]` binds `rest` to [2], the guard fails and the next
      pattern, an exact two-integer array, matches. A hash pattern checks only the keys it lists, so the extra
      `x:` is fine. `[1, 2, 3]` has three elements and fits nothing."""),

    q("yield-with-several-values", r'''
        def two
          yield 1, 2
        end

        def arr
          yield [1, 2]
        end
        a = []
        two { |x| a << x }
        two { |x, y, z| a << [x, y, z] }
        arr { |x| a << x }
        arr { |x, y| a << y }
        two { |*x| a << x }
        p a
    ''', "[1, [1, 2, nil], [1, 2], 2, [1, 2]]",
      ["[[1, 2], [1, 2, nil], [1, 2], 2, [1, 2]]", "[1, [1, 2, nil], 1, 2, [1, 2]]",
       "[1, [1, 2], [1, 2], 2, 1]"],
      "A block takes extra yielded values away and unpacks one array into several parameters",
      """A one-parameter block receiving `yield 1, 2` gets only the first value, and a three-parameter block gets
      nil for the missing one. A single yielded array is spread over several parameters, but a single parameter
      receives it whole. A splat parameter collects everything."""),

    q("arity-and-curry", r'''
        add = ->(a, b, c) { a + b + c }
        c = add.curry
        p [add.arity, proc { |a, b| }.arity, proc { |*a| }.arity,
           ->(a, b = 1) {}.arity, c[1][2][3], c.(1, 2).(3), :upcase.to_proc.arity]
    ''', "[3, 2, -1, -2, 6, 6, -2]", ["[3, 2, 0, -2, 6, 6, -2]", "[3, 2, -1, 2, 6, 6, 1]",
                                      "[3, 3, -1, -2, 6, 6, -2]"],
      "A negative arity means optional arguments: it is minus one minus the required count",
      """`arity` is the number of required arguments, or `-(required + 1)` when some are optional or splatted: a
      lone splat is -1 and one required plus one optional is -2. A curried lambda collects arguments one at
      a time or in groups until it has all three. A symbol turned into a proc needs the receiver and accepts more
      arguments, which gives -2."""),

    q("proc-composition", r'''
        inc = ->(x) { x + 1 }
        dbl = ->(x) { x * 2 }
        p [(inc >> dbl).(3), (inc << dbl).(3), [1, 2].map(&(inc >> dbl)),
           [1, 2].map(&10.method(:+)), %w[1 2].map(&:to_i).sum]
    ''', "[8, 7, [4, 6], [11, 12], 3]", ["[7, 8, [4, 6], [11, 12], 3]", "[8, 7, [3, 5], [11, 12], 3]",
                                         "[8, 7, [4, 6], [10, 20], 3]"],
      ">> runs the left function first; << runs the right one first",
      """`inc >> dbl` means "inc, then dbl": (3 + 1) * 2 = 8. `inc << dbl` is the other order, doubling first:
      3 * 2 + 1 = 7. A method object can be passed with `&`, so `10.method(:+)` adds 10 to every element."""),

    q("array-spaceship-and-times", r'''
        p [[1, 2] <=> [1, 3], [1, 2] <=> [1], [1, 2] <=> [1, "a"], [1, 2] * ",",
           [1, 2] * 2, [[1, 2], [1]].max, [3, 1] <=> 5]
    ''', "[-1, 1, nil, \"1,2\", [1, 2, 1, 2], [1, 2], nil]",
      ["[-1, 1, -1, \"1,2\", [1, 2, 1, 2], [1, 2], nil]", "[-1, 1, nil, \"1,2\", [2, 4], [1, 2], 1]",
       "[-1, 1, nil, \"12\", [1, 2, 1, 2], [1], nil]"],
      "Arrays compare element by element, a longer array wins ties, and * joins or repeats",
      """`[1, 2] <=> [1, 3]` stops at the first difference. When one array is a prefix of the other the longer is
      greater. If two elements cannot be compared (2 against "a") the result is nil, and so is a comparison with a
      non-array. Multiplying by a string joins; multiplying by an integer repeats the array."""),

    q("custom-equals-without-hash", r'''
        class P
          attr_reader :x
          def initialize(x)
            @x = x
          end

          def ==(other) = x == other.x
        end
        a = [P.new(1), P.new(1)]
        p [a.uniq.size, a.include?(P.new(1)), a.index(P.new(1)),
           { P.new(1) => :v }.key?(P.new(1)), a.first.eql?(a.last)]
    ''', "[2, true, 0, false, false]", ["[1, true, 0, true, true]", "[2, true, 0, true, false]",
                                        "[2, false, nil, false, false]"],
      "== is used by include? and index, while uniq and hash keys need eql? and hash",
      """Defining `==` makes `include?` and `index` treat two P objects with the same number as equal. `uniq` and
      hash lookups use `eql?` and `hash` instead, which still compare identity here, so the two objects stay
      distinct and the key lookup misses."""),
)
