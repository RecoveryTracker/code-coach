"""Gotchas, PHP (third deck): run by php (8.5 on this machine); portability notes are in langs.py.

New angles on the first two decks: the array function family (keys kept or dropped), string helpers, numeric and
cast corners, magic methods, traits, enums, generators and references. A card never triggers a warning or a
deprecation (PHP 8.5 prints those to stdout) and every card prints one line.
"""

from __future__ import annotations

from .items import Item, make

q = make("php")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ──────────────────────────────────────────────────────
    q("sort-family-key-handling", r'''
        <?php
        $a = ["b" => 2, "a" => 3, "c" => 1];
        $s = $a;
        sort($s);
        $as = $a;
        asort($as);
        $k = $a;
        ksort($k);
        $r = $a;
        arsort($r);
        echo json_encode([$s, $as, $k, array_keys($r)]);
    ''', '[[1,2,3],{"c":1,"b":2,"a":3},{"a":3,"b":2,"c":1},["a","b","c"]]',
      ['[{"c":1,"b":2,"a":3},{"c":1,"b":2,"a":3},{"a":3,"b":2,"c":1},["a","b","c"]]',
       '[[1,2,3],{"c":1,"b":2,"a":3},{"a":3,"b":2,"c":1},["c","b","a"]]',
       '[[1,2,3],[1,2,3],{"a":3,"b":2,"c":1},["a","b","c"]]'],
      "sort throws the keys away; asort, ksort and arsort keep them",
      """`sort` reorders the values and renumbers from 0, so the string keys are lost. `asort` sorts by value
      but keeps each key with its value, `ksort` sorts by key, and `arsort` is `asort` from high to low, which here
      puts `a` (3) first."""),

    q("array-reverse-and-slice-keys", r'''
        <?php
        echo json_encode([array_reverse([1, 2, 3]),
                          array_reverse(["a" => 1, 2, 3]),
                          array_reverse([5 => "a", 6 => "b"], true),
                          array_slice([5 => "a", 6 => "b", 7 => "c"], 1),
                          array_slice([5 => "a", 6 => "b", 7 => "c"], 1, null,
                                      true),
                          array_slice(["x" => 1, "y" => 2, "z" => 3], 1)]);
    ''', '[[3,2,1],{"0":3,"1":2,"a":1},{"6":"b","5":"a"},["b","c"],{"6":"b","7":"c"},{"y":2,"z":3}]',
      ['[[3,2,1],{"a":1,"0":3,"1":2},{"6":"b","5":"a"},["b","c"],{"6":"b","7":"c"},{"y":2,"z":3}]',
       '[[3,2,1],{"0":3,"1":2,"a":1},["b","a"],["b","c"],{"6":"b","7":"c"},{"y":2,"z":3}]',
       '[[3,2,1],{"0":3,"1":2,"a":1},{"6":"b","5":"a"},{"6":"b","7":"c"},{"6":"b","7":"c"},[2,3]]'],
      "Integer keys are renumbered unless preserve_keys is true; string keys always survive",
      """`array_reverse` and `array_slice` renumber integer keys from 0 by default, but string keys are kept as
      they are. Passing `true` (the fourth argument of `array_slice`, the second of `array_reverse`) keeps the
      original numbers, which is why a reversed array can print as an object: its keys are no longer 0, 1, 2."""),

    q("generator-body-is-lazy", r'''
        <?php
        function g() {
            echo "a";
            yield 1;
            echo "b";
            yield 2;
            echo "c";
        }
        $g = g();
        echo "s";
        foreach ($g as $v) {
            echo $v;
        }
    ''', "sa1b2c", ["a1b2cs", "s1a2bc", "sab12c"],
      "Calling a generator function runs nothing until the first value is requested",
      """`g()` only creates the generator object. The body starts when `foreach` asks for the first value, runs up to
      the first `yield`, and pauses there, so `s` comes first and the echoes interleave with the loop. The last `c`
      prints when the loop asks for a third value and the body runs off its end."""),

    q("class-constant-self-versus-static", r'''
        <?php
        class A {
            const X = "A";
            function s() { return self::X; }
            function t() { return static::X; }
        }
        class B extends A {
            const X = "B";
        }
        $b = new B;
        echo $b->s(), $b->t(), B::X, constant("A::X");
    ''', "ABBA", ["BBBA", "AAAB", "ABBB"],
      "self:: is fixed where the code is written; static:: follows the object's class",
      """`self::X` inside `A` always means `A::X`, even when called on a `B`. `static::X` is resolved at run time
      to the class of the object, so it finds the overriding `B::X`. A direct `B::X` is "B" and `A::X` is
      still "A"."""),

    q("static-property-shared-and-redeclared", r'''
        <?php
        class A {
            public static $n = 0;
        }
        class B extends A {}
        class C extends A {
            public static $n = 10;
        }
        B::$n++;
        C::$n++;
        echo A::$n, B::$n, C::$n;
    ''', "1111", ["0111", "1011", "1110"],
      "A subclass shares its parent's static property unless it redeclares it",
      """`B` does not declare its own `$n`, so `B::$n` is the very same variable as `A::$n`, and incrementing it
      shows through both names: 1 and 1. `C` redeclares `$n`, which makes a separate property starting at 10, so
      its increment gives 11 and leaves `A` alone."""),

    q("trim-character-ranges", r'''
        <?php
        echo implode("|", [trim("abcHELLOcba", "a..c"), trim("--x--", "-"),
                           rtrim("1.500", "0"), rtrim("a.0.0", ".0"),
                           trim("  x "), ltrim("007", "0"), trim("[x]", "[]"),
                           str_pad("5", 4, "ab", STR_PAD_BOTH)]);
    ''', "HELLO|x|1.5|a|x|7|x|a5ab",
      ["abcHELLOcba|x|1.5|a|x|7|x|a5ab", "HELLO|x|1.500|a|x|7|x|a5ab", "HELLO|x|1.5|a.|x|7|x|5ab"],
      "The second argument of trim is a set of characters, and a..c is a range inside it",
      """`trim` removes any of the listed characters from both ends, in any order, and `a..c` stands for a, b and c.
      `rtrim("a.0.0", ".0")` strips every trailing dot or zero, not the text ".0". `str_pad` with `STR_PAD_BOTH`
      puts the extra character on the right, here "a" on the left and "ab" on the right."""),

    q("substr-negative-and-out-of-range", r'''
        <?php
        echo json_encode([substr("hello", -3, 2), substr("abc", 1, -1),
                          substr("abc", 5), substr("abc", -5),
                          substr("abc", 0, -5), substr("abc", 3),
                          substr("abc", 1, 0), substr("abc", -1, 5)]);
    ''', '["ll","b","","abc","","","","c"]',
      ['["ll","b",false,"abc","","","","c"]', '["he","b","","abc","","","","c"]',
       '["ll","b","","c","","","a","c"]'],
      "A negative start counts from the end; a negative length stops before the end; no false any more",
      """Since PHP 8 `substr` always returns a string: a start past the end gives "", not false. A start before the
      beginning is clamped to 0, so `substr("abc", -5)` is the whole string. A negative length drops that many
      characters from the end, and when that leaves nothing the result is empty."""),

    q("strstr-family", r'''
        <?php
        $m = "user@host.com";
        echo json_encode([strstr($m, "@"), strstr($m, "@", true),
                          strrchr("a/b/c", "/"), strstr("abc", "x"),
                          stristr("HeLLo", "ll"), strpos("abcabc", "c", 3),
                          strrpos("abcabc", "b"), substr_count("a,b,c", ",")]);
    ''', '["@host.com","user","\\/c",false,"LLo",5,4,2]',
      ['["@host.com","user","\\/c","","LLo",5,4,2]', '["host.com","user","c",false,"LLo",5,4,2]',
       '["@host.com","user","\\/c",false,"LLo",2,4,2]'],
      "strstr returns the text from the match on, and false when there is none",
      """`strstr` returns the haystack from the first match to the end, or the part before it with `true`; `strrchr`
      does the same from the last match. A miss is `false`, not an empty string. `strpos` with an offset starts
      looking there, so the c at index 2 is skipped. (`json_encode` writes the slash in "/c" as `\\/`.)"""),

    q("wordwrap-and-cut", r'''
        <?php
        echo implode(" ", [wordwrap("The quick brown fox", 10, "|"),
                           wordwrap("A very long woooooooooooord.", 8, "|", true),
                           wordwrap("A very long woooooooooooord.", 8, "|"),
                           wordwrap("short", 10, "|")]);
    ''', "The quick|brown fox A very|long|wooooooo|ooooord. A very|long|woooooooooooord. short",
      ["The quick brown|fox A very|long|wooooooo|ooooord. A very|long|woooooooooooord. short",
       "The quick|brown fox A very|long|woooooooooooord.|woooooooooooord. short",
       "The quick|brown fox A very|long|wooooooo|ooooord. A very long woooooooooooord. short"],
      "wordwrap breaks only at spaces unless the fourth argument says to cut long words",
      """`wordwrap` inserts the break string at the last space that fits in the width. A word longer than the width
      is left whole by default and only split when `$cut_long_words` is true. Text that already fits comes
      back unchanged."""),

    q("similar-text-and-levenshtein", r'''
        <?php
        similar_text("World", "Word", $p1);
        echo implode("|", [similar_text("World", "Word"), round($p1, 1),
                           levenshtein("kitten", "sitting"),
                           levenshtein("a", "b", 1, 5, 1), soundex("Robert"),
                           soundex("Rupert")]);
    ''', "4|88.9|3|2|R163|R163", ["4|80|3|5|R163|R163", "4|88.9|3|2|R163|R130",
                                  "5|88.9|3|1|R163|R163"],
      "similar_text counts shared characters and the percentage is 2 * common / total length",
      """`similar_text("World", "Word")` finds 4 common characters, so the percentage is 2 * 4 / 9 = 88.9. The
      Levenshtein distance counts edits (3 for kitten and sitting). The three optional arguments price an
      insert, a replace and a delete, and the result is the cheapest way: replacing "a" with "b" costs 5, but
      deleting it and inserting "b" costs only 1 + 1, so the answer is 2. `soundex` gives equal codes to words
      that sound alike."""),

    q("heredoc-strips-closing-indent", r'''
        <?php
        $n = 3;
        $a = ["k" => "v"];
        $s = <<<EOT
            n=$n {$a['k']} $a[k]
              indented \$n
            EOT;
        $t = <<<'RAW'
        n=$n\n
        RAW;
        echo str_replace(["\r\n", " ", "\n"], ["|", ".", "|"], $s . "#" . $t);
    ''', 'n=3.v.v|..indented.$n#n=$n\\n',
      ["....n=3.v.v|......indented.$n#n=$n\\n", "n=3.v.v|..indented.3#n=$n\\n",
       "n=3.v.v|..indented.$n#n=3\\n"],
      "A heredoc drops as much indentation as its closing marker has; a nowdoc does not interpolate",
      """The body of a `<<<EOT` heredoc loses the same number of leading spaces as the closing marker is indented,
      so the second line keeps its two extra spaces (shown here as dots). Variables and `{$a['k']}` expand, `\\$n` is an escaped
      dollar sign, and the quoted `<<<'RAW'` form (a nowdoc) keeps `$n` and `\\n` exactly as typed."""),

    # ── Medium ───────────────────────────────────────────────────────────
    q("array-filter-modes", r'''
        <?php
        $a = [10, 20, 30, 40];
        echo json_encode([array_filter($a, fn($k) => $k % 2,
                                       ARRAY_FILTER_USE_KEY),
                          array_filter($a, fn($v, $k) => $v > 15 && $k < 3,
                                       ARRAY_FILTER_USE_BOTH),
                          array_filter($a, fn($v) => $v > 25),
                          array_values(array_filter(["a", "", "0", "b"],
                                                    "strlen"))]);
    ''', '[{"1":20,"3":40},{"1":20,"2":30},{"2":30,"3":40},["a","0","b"]]',
      ['[{"0":10,"2":30},{"1":20,"2":30},{"2":30,"3":40},["a","0","b"]]',
       '[[20,40],[20,30],[30,40],["a","0","b"]]', '[{"1":20,"3":40},{"1":20,"2":30},{"2":30,"3":40},["a","b"]]'],
      "array_filter passes the callback the value unless asked for the key; survivors keep their keys",
      """By default the callback receives each value; `ARRAY_FILTER_USE_KEY` passes the key instead, and
      `ARRAY_FILTER_USE_BOTH` passes value then key. The survivors keep their keys. With `"strlen"` as the
      callback, "0" survives because its length is 1, whereas a plain truthiness filter would drop it."""),

    q("array-fill-chunk-pad", r'''
        <?php
        echo json_encode([array_fill(5, 2, "x"), array_chunk([1, 2, 3], 2),
                          array_chunk(["a" => 1, "b" => 2, "c" => 3], 2, true),
                          array_pad([1], 3, 0), array_pad([1], -3, 0),
                          array_fill_keys(["a", "b"], 0)]);
    ''', '[{"5":"x","6":"x"},[[1,2],[3]],[{"a":1,"b":2},{"c":3}],[1,0,0],[0,0,1],{"a":0,"b":0}]',
      ['[["x","x"],[[1,2],[3]],[{"a":1,"b":2},{"c":3}],[1,0,0],[0,0,1],{"a":0,"b":0}]',
       '[{"5":"x","6":"x"},[[1,2],[3]],[[1,2],[3]],[1,0,0],[0,0,1],{"a":0,"b":0}]',
       '[{"5":"x","6":"x"},[[1,2],[3]],[{"a":1,"b":2},{"c":3}],[0,0,1],[1,0,0],{"a":0,"b":0}]'],
      "array_fill starts at your key; array_chunk drops keys unless told not to; a negative pad goes left",
      """`array_fill(5, 2, "x")` numbers its keys 5 and 6. `array_chunk` renumbers each group from 0 unless the third
      argument is true. `array_pad` adds to the end for a positive size and to the start for a negative one, so
      `[1]` becomes [1, 0, 0] or [0, 0, 1]."""),

    q("array-combine-and-flip-collisions", r'''
        <?php
        echo json_encode([array_combine(["a", "b", "a"], [1, 2, 3]),
                          array_flip(["x", "y", "x"]),
                          array_flip([1, 2, 1.5 > 1 ? 1 : 0]),
                          array_combine([], []),
                          array_unique([3, "3", 1, 3.0])]);
    ''', '[{"a":3,"b":2},{"x":2,"y":1},{"1":2,"2":1},[],{"0":3,"2":1}]',
      ['[{"a":1,"b":2},{"x":0,"y":1},{"1":0,"2":1},[],{"0":3,"2":1}]',
       '[{"a":3,"b":2},{"x":2,"y":1},{"1":2,"2":1},[],[3,1]]',
       '[{"a":3,"b":2,"a2":1},{"x":2,"y":1},{"1":2,"2":1},[],{"0":3,"2":1}]'],
      "When keys repeat the later value wins, but the key keeps its first position",
      """`array_combine` and `array_flip` both build an array by assigning, so a repeated key is overwritten by the
      last value while its place in the order stays where it first appeared. `array_unique` keeps the first of
      each loose-equal group and keeps its original key, which is why the result has keys 0 and 2."""),

    q("array-column-forms", r'''
        <?php
        $rows = [["id" => 7, "n" => "a"], ["id" => 9, "n" => "b"],
                 ["id" => 7, "n" => "c"], ["n" => "d"]];
        echo json_encode([array_column($rows, "n"),
                          array_column($rows, "n", "id"),
                          array_column($rows, "id"),
                          array_column($rows, null, "id")[9]]);
    ''', '[["a","b","c","d"],{"7":"c","9":"b","10":"d"},[7,9,7],{"id":9,"n":"b"}]',
      ['[["a","b","c","d"],{"7":"a","9":"b","10":"d"},[7,9,7],{"id":9,"n":"b"}]',
       '[["a","b","c","d"],{"7":"c","9":"b","0":"d"},[7,9,7,null],{"id":9,"n":"b"}]',
       '[["a","b","c","d"],{"7":"c","9":"b","10":"d"},[7,9,7],{"n":"b"}]'],
      "array_column skips rows that lack the column, and a repeated index key is overwritten",
      """Rows without an `id` are left out of `array_column($rows, "id")`, not turned into null. With an index
      column the later row for id 7 replaces the earlier one, and a row without that index key is appended with the
      next free integer key, here 10 (after 9). Passing `null` as the column returns whole rows."""),

    q("array-replace-and-merge-recursive", r'''
        <?php
        echo json_encode([array_replace([1, 2, 3], [1 => "b"], [3 => "d"]),
                          array_merge_recursive(["a" => 1], ["a" => 2]),
                          array_merge_recursive(["a" => [1]],
                                                ["a" => [2], "b" => 3]),
                          array_replace_recursive(["a" => [1, 2]],
                                                  ["a" => [1 => "x"]]),
                          array_merge()]);
    ''', '[[1,"b",3,"d"],{"a":[1,2]},{"a":[1,2],"b":3},{"a":[1,"x"]},[]]',
      ['[[1,"b",3,"d"],{"a":2},{"a":[1,2],"b":3},{"a":[1,"x"]},[]]',
       '[["b","d"],{"a":[1,2]},{"a":[1,2],"b":3},{"a":[1,"x"]},[]]',
       '[[1,"b",3,"d"],{"a":[1,2]},{"a":[2],"b":3},{"a":["x"]},[]]'],
      "array_replace works by key, and array_merge_recursive turns repeated scalar keys into lists",
      """`array_replace` overwrites by key, including numeric ones, so `[1 => "b"]` replaces the second element.
      `array_merge_recursive` collects clashing values into an array, even for plain numbers, whereas
      `array_replace_recursive` goes into nested arrays and replaces only the keys given."""),

    q("usort-with-array-spaceship", r'''
        <?php
        $p = [["n" => "bo", "a" => 30], ["n" => "al", "a" => 25],
              ["n" => "cy", "a" => 30], ["n" => "di", "a" => 25]];
        usort($p, fn($x, $y) => [$y["a"], $x["n"]] <=> [$x["a"], $y["n"]]);
        echo implode(",", array_column($p, "n"));
    ''', "bo,cy,al,di", ["cy,bo,di,al", "al,di,bo,cy", "bo,cy,di,al"],
      "Comparing arrays with <=> compares element by element, so swapping one side reverses just that key",
      """The left array is `[age of y, name of x]` and the right is `[age of x, name of y]`. Putting y first in the
      age slot sorts the ages from high to low, while the name slot stays x against y, which sorts the names
      from low to high within the same age."""),

    q("array-map-two-arrays-and-keys", r'''
        <?php
        echo json_encode([array_map(null, [1, 2, 3], ["a"]),
                          array_map(fn($a, $b) => $a . $b, ["x" => 1], ["y" => 2]),
                          array_map(fn($a) => $a * 2, ["x" => 1, "y" => 2]),
                          array_map(null, [1, 2]),
                          array_map("strtoupper", [3 => "a", 1 => "b"])]);
    ''', '[[[1,"a"],[2,null],[3,null]],["12"],{"x":2,"y":4},[1,2],{"3":"A","1":"B"}]',
      ['[[[1,"a"]],["12"],{"x":2,"y":4},[1,2],{"3":"A","1":"B"}]',
       '[[[1,"a"],[2,null],[3,null]],{"x":"12"},{"x":2,"y":4},[1,2],{"3":"A","1":"B"}]',
       '[[[1,"a"],[2,null],[3,null]],["12"],[2,4],[1,2],["A","B"]]'],
      "One array keeps its keys; with several the keys are dropped and short ones are padded with null",
      """With a single array, `array_map` preserves the keys, string or integer. Given several arrays it walks
      them in step and returns a list, filling the shorter ones with null, so the string keys vanish. A null
      callback zips the arrays into rows."""),

    q("math-function-return-types", r'''
        <?php
        $r = [floor(5), abs(-5), abs(-5.5), max(1, 2.0), max(2, 1.0),
              array_sum([1, 2]), array_sum([1, 2.0]), sqrt(16), pow(2, 3),
              pow(2, -1), 2 ** 63, 7 <=> 7.0];
        echo implode(",", array_map("gettype", $r));
    ''', "double,integer,double,double,integer,integer,double,double,integer,double,double,integer",
      ["integer,integer,double,double,integer,integer,double,double,integer,double,double,integer",
       "double,integer,double,integer,integer,integer,double,integer,integer,double,integer,integer",
       "double,integer,double,double,double,integer,double,double,double,double,double,integer"],
      "floor, round, ceil and sqrt return floats; max keeps the type of the winner",
      """`floor(5)` is the float 5.0, even though it prints as 5. `max` returns the winning argument as it was
      given, so `max(1, 2.0)` is a float and `max(2, 1.0)` is an int. `pow` with ints and a non-negative
      exponent stays an int, `2 ** 63` overflows to a float, and the spaceship operator always gives an int."""),

    q("int-min-negation-overflows", r'''
        <?php
        $r = [-PHP_INT_MIN, PHP_INT_MIN, abs(PHP_INT_MIN), PHP_INT_MAX + 1,
              PHP_INT_MAX * 1, PHP_INT_MIN - 1, intdiv(PHP_INT_MAX, 2),
              -PHP_INT_MAX - 1];
        echo implode(",", array_map("get_debug_type", $r));
    ''', "float,int,float,float,int,float,int,int",
      ["int,int,int,float,int,float,int,int", "float,int,float,float,int,int,int,int",
       "float,float,float,float,int,float,int,float"],
      "Negating the smallest integer has no int result, so PHP switches to float",
      """The range of a 64-bit integer has one more negative number than positive, so `-PHP_INT_MIN` and
      `abs(PHP_INT_MIN)` do not fit and become floats, as does `PHP_INT_MAX + 1`. `-PHP_INT_MAX - 1` stays inside
      the range at every step and is still an int."""),

    q("numeric-string-arithmetic", r'''
        <?php
        echo json_encode([" 5" + 1, "5 " + 1, "1e2" + 0, "10" + "5.5", "0.0" + 0,
                          "9" + "1", "3" * "4", "7" / "2", "2" ** "3", "10" % "3"],
                         JSON_PRESERVE_ZERO_FRACTION);
    ''', '[6,6,100.0,15.5,0.0,10,12,3.5,8,1]',
      ['[6,"5 1",100,15.5,0,10,12,3.5,8,1]', '[6,6,100,15.5,0.0,91,12,3.5,8,1]',
       '[6,6,100.0,15.5,0,10,12,3,8,1]'],
      "Numeric strings become int or float by their look, and leading or trailing spaces are allowed",
      """A string that looks like an integer becomes an int in arithmetic, one with a dot or exponent becomes a
      float: "1e2" + 0 is 100.0 and "0.0" + 0 is 0.0. Both leading and trailing whitespace are accepted since PHP 8.
      Division gives an int only when the result is exact, so "7" / "2" is 3.5."""),

    q("string-casts", r'''
        <?php
        echo json_encode([(string)false, (string)null, (string)1.0,
                          (string)true, strval(7.0 / 2), (string)1e25,
                          (string)0.00001, (string)-0.0,
                          (string)123456789012345678, (string)1.5e3]);
    ''', '["","","1","1","3.5","1.0E+25","1.0E-5","-0","123456789012345678","1500"]',
      ['["false","null","1.0","true","3.5","1.0E+25","1.0E-5","-0","123456789012345678","1500"]',
       '["","","1","1","3.5","1.0e+25","0.00001","0","123456789012345678","1500"]',
       '["","","1","1","3.5","1.0E+25","1.0E-5","-0","1.2345678901235E+17","1.5E+3"]'],
      "false and null become '', a whole float loses its .0, and extreme floats use E notation",
      """`true` is "1" and `false` is "". A float with no fractional part prints without `.0`, and floats at the
      extremes use scientific notation such as `1.0E+25`. Negative zero prints as "-0". A large integer is exact:
      it is still an int, so no precision is lost."""),

    q("null-comparisons", r'''
        <?php
        echo json_encode([null < -1, null == [], null <=> 0, null < "a", [] < [1],
                          "abc" < "abd", [1, 2, 3] > [4, 5], null == "0"]);
    ''', '[true,true,0,true,true,true,true,false]',
      ['[false,true,0,true,true,true,false,false]', '[true,true,0,false,true,true,true,true]',
       '[true,false,0,true,true,true,true,false]'],
      "null compares as false with numbers, as an empty string with strings, as [] with arrays",
      """Against a number, null turns both sides into booleans, so `null < -1` is `false < true`. Against a
      string it becomes "" and "" sorts before "a", but "" is not equal to "0". Arrays compare by length first, so
      an empty array is smaller than any non-empty one and a longer array is greater regardless of its contents."""),

    q("sprintf-positions-and-widths", r'''
        <?php
        echo implode("|", [sprintf('%2$s-%1$s-%2$s', "a", "b"),
                           sprintf("[%s%s%s]", true, false, null),
                           sprintf("%5.1f", 9.96), sprintf("%-4d", 7),
                           sprintf("%5s", "toolong"), sprintf("%.3s", "abcdef"),
                           sprintf("%03d", 7)]);
    ''', "b-a-b|[1]| 10.0|7   |toolong|abc|007",
      ["a-b-a|[1]| 10.0|7   |toolong|abc|007", "b-a-b|[1]|  9.9|7   |toolong|abc|007",
       "b-a-b|[1truenull]| 10.0|   7|too|abc|007"],
      "%1$s picks arguments by position, and a width is a minimum while .N on %s is a maximum",
      """`%2$s` takes the second argument and may be repeated. `true` prints "1" while `false` and `null` print
      nothing. `%5.1f` rounds 9.96 up to 10.0 and pads it to five characters. A width never cuts a longer string,
      but a precision on `%s` does: `%.3s` keeps three characters."""),

    # ── Harder ───────────────────────────────────────────────────────────
    q("magic-get-set-isset", r'''
        <?php
        class M {
            private $d = ["a" => 1];
            function __get($k) { return $this->d[$k] ?? "none"; }
            function __set($k, $v) { $this->d[$k] = $v * 2; }
            function __isset($k) { return isset($this->d[$k]); }
        }
        $m = new M;
        $m->b = 5;
        $m->b += 1;
        echo $m->b, $m->a, $m->zz, isset($m->b) ? "Y" : "N",
             isset($m->q) ? "Y" : "N", empty($m->a) ? "E" : "F";
    ''', "221noneYNF", ["6", "61noneYNF", "221noneYNE"],
      "Compound assignment reads through __get and then writes through __set",
      """`$m->b = 5` calls `__set`, which stores 10. `$m->b += 1` reads 10 with `__get`, adds 1, and calls `__set` with
      11, which doubles it to 22. `isset` and `empty` ask `__isset` first, so `$m->q` is not set, and `empty($m->a)`
      is false because `__get` returns 1."""),

    q("magic-call-and-private-method", r'''
        <?php
        class C {
            function __call($n, $a) { return "call:$n "; }
            static function __callStatic($n, $a) { return "static:$n "; }
            function real() { return $this->hidden() . " "; }
            private function hidden() { return "hid"; }
            function __invoke($x) { return $x * 2; }
        }
        $c = new C;
        echo $c->foo(), C::bar(), $c->real(), $c->hidden(),
             implode(",", array_map($c, [1, 2]));
    ''', "call:foo static:bar hid call:hidden 2,4", ["call:foo static:bar hid hid 2,4",
                                                     "call:foo call:bar hid call:hidden 2,4",
                                                     "call:foo static:bar call:hidden call:hidden 2,4"],
      "Calling an inaccessible method from outside falls through to __call",
      """Inside the class `hidden()` is private but reachable, so `real()` works. From outside, the private method
      is invisible and PHP calls `__call("hidden")` instead of raising an error. `__callStatic` handles the static
      form, and `__invoke` lets the object itself be used as a callable."""),

    q("trait-versus-class-versus-parent", r'''
        <?php
        class P {
            function who() { return "P"; }
            function a() { return "Pa"; }
        }
        trait T {
            function who() { return "T" . parent::who(); }
            function a() { return "Ta"; }
            function b() { return "Tb"; }
        }
        class C extends P {
            use T;
            function a() { return "Ca"; }
        }
        $c = new C;
        echo $c->who(), $c->a(), $c->b();
    ''', "TPCaTb", ["PPaTb", "TPTaTb", "TPCaPb"],
      "A class's own method beats a trait's, and a trait's beats the inherited one",
      """The order is class, then trait, then parent. `C::a` wins over `T::a`, while `T::who` replaces `P::who`
      and can still call the parent's version with `parent::who()`, giving "TP". `b` exists only in the trait."""),

    q("trait-conflict-resolution", r'''
        <?php
        trait A { function hi() { return "A"; } function n() { return "An"; } }
        trait B { function hi() { return "B"; } function n() { return "Bn"; } }
        class C {
            use A, B {
                A::hi insteadof B;
                B::n insteadof A;
                B::hi as protected bye;
                A::n as an;
            }
            function x() { return $this->bye(); }
        }
        $c = new C;
        echo $c->hi(), $c->n(), $c->an(), $c->x();
    ''', "ABnAnB", ["ABnBnB", "AAnAnB", "ABnAnA"],
      "insteadof picks the winner of a clash; as gives the loser another name",
      """Both traits define `hi` and `n`, so one must be chosen: `A::hi` and `B::n` win. `as` adds an alias without
      removing anything: `B::hi as bye` keeps B's `hi` reachable (here as a protected method called from inside
      the class), and `A::n as an` keeps A's `n`."""),

    q("readonly-array-and-object", r'''
        <?php
        class P {
            function __construct(public readonly array $a,
                                 public readonly stdClass $o) {}
        }
        $p = new P([1], new stdClass);
        $p->o->x = 5;
        try {
            $p->a[] = 2;
        } catch (Error $e) {
            echo get_class($e), ":", $e->getMessage(), ":", $p->o->x;
        }
    ''', "Error:Cannot indirectly modify readonly property P::$a:5",
      ["Error:Cannot indirectly modify readonly property P::$a:",
       "TypeError:Cannot indirectly modify readonly property P::$a:5",
       "Error:Cannot indirectly modify readonly property P::$o:5"],
      "readonly freezes the property itself, not the object it points to",
      """Appending to a readonly array is an indirect modification of the property, which throws an `Error`. A readonly property

      that holds an object only fixes which object it is: `$p->o->x = 5` changes that object's own property, which
      is allowed, and it still holds 5 afterwards."""),

    q("enum-methods-and-constants", r'''
        <?php
        enum S: int {
            case A = 1;
            case B = 2;
            const DEF = self::B;
            static function big(): self { return self::B; }
            function label(): string {
                return ucfirst(strtolower($this->name)) . $this->value;
            }
        }
        echo S::DEF->label(), S::big() === S::B ? "same" : "diff",
             S::from(1)->name, count(S::cases()),
             S::A instanceof BackedEnum ? "B" : "-";
    ''', "B2sameA2B", ["b2sameA2B", "B2diffA2B", "B2sameA2-"],
      "An enum case is a single object, so cases compare with ===, and enums can have constants and methods",
      """Each case exists exactly once, so `S::big() === S::B` is true however you reach it. Constants can refer to
      cases and methods can read `name` and `value`. Backed enums also implement `BackedEnum`, which `instanceof`
      confirms."""),

    q("first-class-callable-syntax", r'''
        <?php
        class K {
            function dbl($x) { return $x * 2; }
            static function neg($x) { return -$x; }
            function all() { return array_map($this->dbl(...), [1, 2]); }
        }
        $f = strlen(...);
        $up = strtoupper(...);
        echo $f("abc"), $up("x"),
             implode(",", array_map(strrev(...), ["ab", "cd"])),
             implode(",", (new K)->all()),
             implode(",", array_map(K::neg(...), [1, 2]));
    ''', "3Xba,dc2,4-1,-2", ["3xba,dc2,4-1,-2", "abcXba,dc2,4-1,-2", "3Xab,cd2,4-1,-2"],
      "f(...) with a literal ... makes a closure of the function; it does not call it",
      """`strlen(...)` is a closure for `strlen`, not a call with a spread argument; it works for plain
      functions, methods (`$this->dbl(...)`) and static methods (`K::neg(...)`). The closures can be passed to
      `array_map` or called directly."""),

    q("variadic-collects-named-arguments", r'''
        <?php
        function f(...$args) {
            return json_encode($args);
        }
        function g($a, ...$rest) {
            return json_encode([$a, $rest]);
        }
        echo f(1, 2, x: 3), f(), g(1, 2, 3), g(a: 1), g(1, k: 2);
    ''', '{"0":1,"1":2,"x":3}[][1,[2,3]][1,[]][1,{"k":2}]',
      ['[1,2,3][][1,[2,3]][1,[]][1,{"k":2}]', '{"0":1,"1":2,"x":3}[][1,[2,3]][1,[]][1,[2]]',
       '{"0":1,"1":2,"x":3}{}[1,[2,3]][1,{}][1,{"k":2}]'],
      "A variadic parameter also collects unknown named arguments, keyed by name",
      """Extra positional arguments get the keys 0, 1, ...; an unknown named argument is added under its own name,
      so the array becomes a JSON object. With nothing collected the array is empty and encodes as `[]`."""),

    q("static-variable-shared-with-inheriting-class", r'''
        <?php
        class A {
            static function c() {
                static $n = 0;
                return ++$n;
            }
        }
        class B extends A {}
        class C extends A {
            static function c() { return parent::c(); }
        }
        A::c();
        B::c();
        C::c();
        echo A::c(), B::c();
    ''', "45", ["22", "24", "44"],
      "An inherited method shares its static variables with the parent's, and so does parent::",
      """Since PHP 8.1 `B::c` is the very same method as `A::c`, with the same static `$n`. `C::c` has its own code but
      calls `parent::c()`, which is again `A`'s method and counter. After three calls, `A::c()` gives 4 and
      `B::c()` gives 5."""),

    q("closure-bind-to-reach-private", r'''
        <?php
        class S {
            private $v = 42;
            private static $w = 7;
        }
        $peek = function () { return $this->v; };
        $stat = static function () { return self::$w; };
        echo Closure::bind($peek, new S, S::class)(), $peek->call(new S),
             Closure::bind($stat, null, S::class)(),
             (fn() => $this->v)->bindTo(new S, S::class)();
    ''', "4242742", ["42", "424242", "42427"],
      "Binding a closure to an object and a class scope gives it access to private members",
      """A closure written outside the class cannot read `$this->v`, but `Closure::bind($peek, $obj, S::class)`
      makes it run as if it were a method of `S`, so private properties are visible. `call` binds and calls in one
      step, and a static closure can be given a class scope with a null object to read a private static."""),

    q("reference-creates-the-element", r'''
        <?php
        function inc(&$x) {
            $x++;
        }
        $a = [];
        inc($a["k"]);
        $r = &$a["z"];
        $o = new stdClass;
        inc($o->p);
        echo json_encode([$a, count($a), array_key_exists("z", $a), $o]);
    ''', '[{"k":1,"z":null},2,true,{"p":1}]',
      ['[{"k":1},1,false,{"p":1}]', '[[],0,false,{}]', '[{"k":1,"z":null},2,false,{"p":1}]'],
      "Passing or taking a reference to a missing key creates it as null",
      """A by-reference parameter forces the array element to exist, starting as null, so `inc` turns it into 1.
      Just writing `$r = &$a["z"]` also creates the key `z` with a null value, and the same happens for an object
      property."""),

    q("foreach-destructuring-leaks", r'''
        <?php
        $rows = [["id" => 1, "t" => "a"], ["id" => 2, "t" => "b"]];
        $o = [];
        foreach ($rows as ["id" => $id, "t" => $t]) {
            $o[] = "$t$id";
        }
        foreach ([[1, [2, 3]], [4, [5, 6]]] as [$p, [$q, $r]]) {
        }
        echo implode(",", $o), $id, $t, $p, $q, $r;
    ''', "a1,b22b456", ["a1,b2", "a1,b21a123", "a1,b22b123"],
      "Loop variables, including destructured ones, are still set after the loop",
      """PHP has no block scope: `$id`, `$t`, `$p`, `$q` and `$r` keep the values from the last pass. The list
      syntax may name array keys and nest, so `[$p, [$q, $r]]` unpacks 4, then 5 and 6 from the last row."""),

    q("catch-order-and-multi-catch", r'''
        <?php
        function f() {
            try {
                throw new InvalidArgumentException("x");
            } catch (RuntimeException $e) {
                return "rt";
            } catch (LogicException | TypeError $e) {
                return get_class($e);
            } finally {
                echo "F";
            }
        }
        echo f();
    ''', "FInvalidArgumentException", ["Frt", "InvalidArgumentExceptionF", "FLogicException"],
      "The first matching clause wins, and finally runs before the returned value is echoed",
      """`InvalidArgumentException` extends `LogicException`, not `RuntimeException`, so it is caught by the second
      clause, whose union type matches subclasses. The `finally` block prints F while `f()` is still being
      evaluated, so it appears before the echoed return value, and `get_class` reports the actual class."""),

    q("destructor-timing", r'''
        <?php
        class D {
            function __construct(public $n) {}
            function __destruct() { echo "~{$this->n} "; }
        }
        $a = new D("a");
        $b = $a;
        unset($a);
        echo "1 ";
        $b = null;
        echo "2 ";
        $c = new D("c");
        $c = new D("d");
        echo "3";
    ''', "1 ~a 2 ~c 3~d", ["~a 1 2 ~c ~d 3", "1 2 3~a ~c ~d", "1 ~a 2 3~c ~d"],
      "An object is destroyed when its last reference goes; survivors at the end of the script",

      """`unset($a)` leaves `$b` pointing at the object, so nothing happens until `$b = null` drops the last
      reference and `~a` prints. In `$c = new D("d")` the new object is built first and assigned second, which frees
      the old one; the remaining object is destroyed when the script ends, after the 3."""),

    q("tostring-and-loose-comparison", r'''
        <?php
        class T {
            function __toString(): string { return "T"; }
        }
        $o = new T;
        echo json_encode([$o == "T", $o === "T", "T" . $o, strlen($o),
                          str_contains($o, "T"), in_array("T", [$o]),
                          $o instanceof Stringable, (string)$o === "T"]);
    ''', '[true,false,"TT",1,true,true,true,true]',
      ['[false,false,"TT",1,true,false,true,true]', '[true,false,"T",1,true,true,true,true]',
       '[true,true,"TT",1,true,true,false,true]'],
      "An object with __toString equals a string loosely, but never strictly",
      """A loose comparison between an object and a string converts the object with `__toString`, so `==` and
      `in_array` find a match, while `===` compares types and fails. Declaring `__toString` also makes the class
      implement `Stringable` automatically, and string functions accept the object."""),

    q("filter-var-conversions", r'''
        <?php
        echo json_encode([filter_var("12", FILTER_VALIDATE_INT),
                          filter_var("12.0", FILTER_VALIDATE_INT),
                          filter_var(" 12 ", FILTER_VALIDATE_INT),
                          filter_var("007", FILTER_VALIDATE_INT),
                          filter_var("on", FILTER_VALIDATE_BOOLEAN),
                          filter_var("maybe", FILTER_VALIDATE_BOOLEAN),
                          filter_var("maybe", FILTER_VALIDATE_BOOLEAN,
                                     FILTER_NULL_ON_FAILURE),
                          filter_var("1e3", FILTER_VALIDATE_FLOAT)]);
    ''', '[12,false,12,false,true,false,null,1000]',
      ['[12,12,12,7,true,false,null,1000]', '[12,false,false,false,true,null,null,1000]',
       '[12,false,12,false,true,false,false,1000]'],
      "filter_var is strict about the format: no decimals, no leading zeros, and false on failure",
      """`FILTER_VALIDATE_INT` trims blanks but rejects "12.0" and the leading zeros of "007", returning `false`.
      The boolean filter returns `false` for anything it does not know, which cannot be told from a real
      "no" unless `FILTER_NULL_ON_FAILURE` is passed, and then it returns null. "1e3" is a valid float string."""),

    q("json-encode-list-versus-object", r'''
        <?php
        echo json_encode([[1 => "a"], [0 => "a", 1 => "b"], [], new stdClass,
                          (object)[], "a/b", "\u{e9}", 10.0, 0.1 + 0.2, [[]]]);
    ''', '[{"1":"a"},["a","b"],[],{},{},"a\\/b","\\u00e9",10,0.30000000000000004,[[]]]',
      ['[["a"],["a","b"],[],{},{},"a\\/b","\\u00e9",10,0.30000000000000004,[[]]]',
       '[{"1":"a"},["a","b"],{},{},{},"a/b","é",10,0.30000000000000004,[[]]]',
       '[{"1":"a"},["a","b"],[],{},{},"a\\/b","\\u00e9",10.0,0.3,[[]]]'],
      "An array is a JSON list only if its keys are 0, 1, 2...; [] stays a list and an empty object is {}",
      """`[1 => "a"]` does not start at 0, so it becomes an object. An empty PHP array is encoded as `[]`, while an
      empty object is `{}`. By default slashes and non-ASCII characters are escaped, and a float is written with its
      shortest exact digits: 10.0 loses its `.0` (unless JSON_PRESERVE_ZERO_FRACTION is used) while 0.1 + 0.2
      shows its error."""),

    q("string-functions-count-bytes", r'''
        <?php
        $e = "\u{e9}";
        echo json_encode([strlen($e), ord($e[0]), strtoupper($e) === $e,
                          ucfirst($e . "a") === $e . "a",
                          strlen(substr($e . "a", 0, 1)), substr($e, 0, 1) === $e,
                          strlen("\u{65e5}\u{672c}"), strrev("ab")]);
    ''', '[2,195,true,true,1,false,6,"ba"]',
      ['[1,233,true,true,1,true,2,"ba"]', '[2,195,false,false,1,false,6,"ba"]',
       '[2,195,true,true,2,false,2,"ba"]'],
      "PHP strings are bytes: strlen, substr and ord see the UTF-8 encoding, not characters",
      """The letter e-acute is two bytes in UTF-8, so `strlen` is 2, `ord` reads only the first byte (195) and
      `substr($e, 0, 1)` cuts the character in half. `strtoupper` and `ucfirst` only change ASCII letters in
      PHP 8, leaving the accented one alone. The two Japanese characters at the end take three bytes each, six
      in all."""),

)
