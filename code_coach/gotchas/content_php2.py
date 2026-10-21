"""Gotchas, PHP (second deck): run by the php CLI (8.x; 8.5 on this machine); portability notes in langs.py.

Every program has to run without a single warning or deprecation notice, because the CLI prints those on
standard output, with the temp path in them. Floats are shown with `json_encode` (shortest round-trip) or
`echo` (the `precision` setting of 14) on purpose, and `json_encode(1.0)` is `1` unless the flag
JSON_PRESERVE_ZERO_FRACTION is given. Things that changed between 8.x versions (negative array keys, rounding
of halves like 1.005, strcmp's return values) are left out.
"""

from __future__ import annotations

from .items import Item, make

q = make("php")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics a beginner can get, with a real trap ──────────
    q("division-results", r'''
        <?php
        echo implode(" ", [10 / 4, 10 / 5, 7 % 3, intdiv(-7, 2), fdiv(1, 0),
                           2 ** -1]);
    ''', "2.5 2 1 -3 INF 0.5", ["2.5 2.0 1 -4 INF 0.5", "2 2 1 -3 INF 0", "2.5 2 1 -3.5 INF 0.5"],
      "/ gives an int when it divides evenly, intdiv truncates, fdiv never throws",
      """`10 / 5` is exactly 2, so PHP hands back the int 2, while `10 / 4` is the float 2.5. `intdiv(-7, 2)`
      truncates toward zero. `fdiv(1, 0)` returns INF instead of throwing like `1 / 0` would, and a negative
      exponent gives a float."""),

    q("loose-equality-table", r'''
        <?php
        $r = [0 == "", "0" == false, "0.0" == false, "" == null, null == 0,
              "1" == "01", "10" == "1e1", "abc" == "ABC"];
        echo json_encode($r);
    ''', "[false,true,false,true,true,true,true,false]",
      ["[true,true,false,true,true,true,true,false]", "[false,true,true,true,true,true,true,false]",
       "[false,true,false,true,true,false,false,false]"],
      "== converts between types; only the string \"0\" and \"\" are false-like strings",
      """Since PHP 8 `0 == ""` is false (the empty string is not numeric). The string "0" converts to false, but
      "0.0" is a different non-empty string and stays true. Two numeric strings compare as numbers, so "1" ==
      "01" and "10" == "1e1"."""),

    q("empty-isset-truthiness", r'''
        <?php
        $n = null;
        $z = "0";
        echo json_encode([empty("0"), empty("0.0"), empty([]), empty(0.0),
                          isset($n), isset($z), is_null($n), (bool)"false",
                          (bool)[0], (bool)0.0]);
    ''', "[true,false,true,true,false,true,true,true,true,false]",
      ["[true,true,true,true,false,true,true,false,true,false]",
       "[false,false,true,true,true,true,true,true,true,false]",
       "[true,false,true,true,false,true,false,true,false,false]"],
      "Falsy values: \"0\", \"\", 0, 0.0, [], null; but \"0.0\", \"false\" and [0] are true",
      """The string "0" is the one non-empty string that counts as false, and `empty` follows the same rule, so
      "0.0" is not empty. `isset` is about null, not falsiness: a variable holding "0" is set. A non-empty
      array is true even when its only element is 0."""),

    q("strpos-zero-versus-false", r'''
        <?php
        $p = strpos("hello", "h");
        echo json_encode([$p == false, $p === false,
                          strpos("hello", "z") === false, str_contains("hello", ""),
                          substr("abc", 3), substr("abc", -1)]);
    ''', '[true,false,true,true,"","c"]',
      ['[false,false,true,true,"","c"]', '[true,false,true,false,"","c"]', '[true,false,true,true,false,"c"]'],
      "strpos returns 0 for a match at the start, and 0 == false",
      """A match at the very start is index 0, which loosely equals false, so a test like `if (!strpos(...))` is
      wrong; compare with `=== false`. `str_contains` with an empty needle is true, and since PHP 8 `substr`
      returns an empty string (not false) when the start is at the end."""),

    q("array-plus-versus-merge", r'''
        <?php
        echo json_encode([[1, 2] + [5, 6, 7],
                          array_merge([1, 2], [5, 6, 7]),
                          ["a" => 1] + ["a" => 2, "b" => 3],
                          array_merge(["a" => 1], ["a" => 2, "b" => 3]),
                          array_merge([5 => "x"], [5 => "y"])]);
    ''', '[[1,2,7],[1,2,5,6,7],{"a":1,"b":3},{"a":2,"b":3},["x","y"]]',
      ['[[1,2,5,6,7],[1,2,5,6,7],{"a":2,"b":3},{"a":2,"b":3},["x","y"]]',
       '[[1,2,7],[1,2,5,6,7],{"a":1,"b":3},{"a":2,"b":3},{"5":"y"}]',
       '[[5,6,7],[1,2,5,6,7],{"a":2,"b":3},{"a":1,"b":3},["x","y"]]'],
      "+ keeps the left side's value for a shared key; array_merge renumbers integer keys",
      """The `+` operator unions by key and the left array wins, so index 2 is the only addition to [1, 2]. With
      string keys `array_merge` lets the later value win, but integer keys are never merged: they are
      appended and renumbered."""),

    q("array-key-coercion", r'''
        <?php
        $a = ["1" => "a", 1 => "b", true => "c", "01" => "d", false => "e",
              "" => "f"];
        echo count($a), json_encode(array_keys($a));
    ''', '4[1,"01",0,""]', ['6[1,"1",1,"01",0,""]', '5[1,"01",0,"",false]', '4["1","01","0",""]'],
      "Numeric strings, true and false become integer keys, so keys collide",
      """The key "1" is the integer 1, and `true` is also 1, so all three writes hit one slot and the last
      value wins. `false` becomes 0. "01" is not a canonical integer string and stays a string, and "" is its
      own key."""),

    q("foreach-value-and-reference", r'''
        <?php
        $a = [1, 2, 3]; $n = 0;
        foreach ($a as $v) { if ($n++ == 0) { $a[] = 4; } }
        $b = [1, 2, 3]; $m = 0;
        foreach ($b as &$w) { if ($m++ == 0) { $b[] = 4; } }
        echo "$n $m ", count($a);
    ''', "3 4 4", ["3 3 4", "4 4 4", "3 4 3"],
      "foreach by value walks a copy; foreach by reference walks the live array",
      """A by-value loop iterates over a snapshot, so appending inside it does not extend the loop: three passes.
      A by-reference loop works on the array itself and also visits the appended 4: four passes. In both
      cases the array ends with four elements."""),

    q("copy-on-assign-and-clone", r'''
        <?php
        $a = [1]; $b = $a; $b[] = 2;
        $o = new stdClass; $o->v = [1];
        $p = $o; $p->v[] = 2;
        $q = clone $o; $q->v[] = 3;
        echo count($a), count($o->v), count($q->v);
    ''', "123", ["122", "223", "113"],
      "Arrays are copied on assignment, objects are shared handles; clone is shallow",
      """`$b = $a` gives an independent array, so $a stays at one element. `$p = $o` copies the handle, so the
      push through `$p` shows in `$o`, which now has two. `clone` makes a new object whose `v` array starts as
      a copy of [1, 2], then grows to three."""),

    q("float-and-int-limits", r'''
        <?php
        echo json_encode([PHP_INT_MAX + 1, PHP_INT_MAX, 0.1 + 0.7,
                          (int)((0.1 + 0.7) * 10), (int)(0.1 + 0.7) * 10,
                          7.0 / 2]);
    ''', "[9.223372036854776e+18,9223372036854775807,0.7999999999999999,7,0,3.5]",
      ["[-9223372036854775808,9223372036854775807,0.8,8,0,3.5]",
       "[9.223372036854776e+18,9223372036854775807,0.8,8,8,3.5]",
       "[9.223372036854776e+18,9223372036854775807,0.7999999999999999,8,0,3.5]"],
      "Integers overflow into floats, 0.1 + 0.7 is not 0.8, and a cast binds tighter than *",
      """Adding 1 to PHP_INT_MAX silently produces a float. `0.1 + 0.7` is 0.7999999999999999, so `* 10` gives
      just under 8, and the cast truncates it to 7. In `(int)(0.1 + 0.7) * 10` the cast applies first, giving
      0 * 10."""),

    q("modulo-fmod-intdiv", r'''
        <?php
        echo implode(" ", [-7 % 3, 7 % -3, fmod(-7, 3), fmod(7.5, 2), -7 / 2,
                           intdiv(7, -2), 7 <=> 3]);
    ''', "-1 1 -1 1.5 -3.5 -3 1", ["2 -2 2 1.5 -3.5 -4 1", "-1 1 -1 1.5 -4 -3 1", "-1 -1 -1 1.5 -3.5 -3 1"],
      "% and intdiv truncate toward zero; the sign of % follows the left operand",
      """`%` works on integers and the remainder takes the sign of the dividend: -7 % 3 is -1 and 7 % -3 is 1.
      `fmod` does the same for floats. `intdiv(7, -2)` truncates to -3, while plain `/` keeps the fraction."""),

    q("round-and-casts-json", r'''
        <?php
        echo json_encode([round(2.5), round(-2.5), 10 / 5, intdiv(10, 5),
                          "5" + "5", "5" . "5", "1.5" + 1, (int)"12abc",
                          (int)"abc", (int)-12.9, (int)"1e3", (float)"1e3"],
                         JSON_PRESERVE_ZERO_FRACTION);
    ''', '[3.0,-3.0,2,2,10,"55",2.5,12,0,-12,1000,1000.0]',
      ['[2.0,-2.0,2.0,2,10,"55",2.5,12,0,-13,1000,1000.0]', '[3,-3,2,2,10,"55",2.5,12,0,-12,1000,1000]',
       '[3.0,-3.0,2,2,55,"55",2.5,12,0,-12,1000,1000.0]'],
      "round() returns a float, / may return an int, and casts stop at the first bad character",
      """`round` always returns a float (half away from zero), even for 2.5 giving 3.0, whereas `10 / 5` is an
      int. `+` on strings does arithmetic ("5" + "5" is 10) and `.` concatenates. `(int)` reads the leading
      number and ignores the rest, and in PHP 7.1 and later "1e3" is understood as 1000."""),

    q("null-coalescing-operators", r'''
        <?php
        $a = null; $b = 0; $arr = ["k" => null];
        echo json_encode([$a ?? "d", $b ?? "d", $b ?: "d", $arr["k"] ?? "d",
                          $undefined ?? "u", $arr["x"]["y"] ?? "deep",
                          isset($arr["k"]), array_key_exists("k", $arr)]);
    ''', '["d",0,"d","d","u","deep",false,true]',
      ['["d","d","d","d","u","deep",false,true]', '["d",0,0,"d","u","deep",false,true]',
       '["d",0,"d","d","u","deep",true,true]'],
      "?? tests for null/unset only; ?: tests for falsiness",
      """The null-coalescing operator keeps 0 because 0 is set and not null, while the short ternary `?:`
      replaces it, since 0 is false.
      `??` never warns about a missing variable or key, however deep the chain. `isset` is false for a key
      holding null, but `array_key_exists` is true."""),

    q("concat-and-plus-precedence", r'''
        <?php
        echo "Total: " . 1 + 2, "|", "Sum " . 1 + 2 . "!", "|", -2 ** 2, "|",
             !empty("a") + 1;
    ''', "Total: 3|Sum 3!|-4|2", ["Total: 12|Sum 12!|4|2", "Total: 3|Sum 3!|4|2", "Total: 3|Sum 12!|-4|1"],
      "Since PHP 8, + and - bind tighter than the dot; ** binds tighter than unary minus",
      """PHP 8 changed the precedence so arithmetic happens before concatenation: `"Total: ".1 + 2` is
      `"Total: ".(1 + 2)`. Earlier versions built "Total: 1" first and then tried to add 2. `-2 ** 2` is
      `-(2 ** 2)`, which is -4."""),

    q("string-interpolation-forms", r'''
        <?php
        $a = ["k" => "v", 2 => "two"];
        $n = 5;
        $f = fn($x) => $x * 2;
        $o = new stdClass;
        $o->p = "prop";
        echo "$n% {$n}th {$f(3)} $a[k] $a[2] {$a['k']} $o->p->x";
    ''', "5% 5th 6 v two v prop->x", ["5% 5th 6 v two v prop", "5% 5th 6 $a[k] two v prop->x",
                                        "5% {5}th 6 v two v prop->x"],
      "Simple interpolation takes one array index or one property, and no more",
      """In a double-quoted string `$a[k]` reads the key k without quotes, `{$expr}` accepts any expression
      including a call, and `$o->p->x` only reads the first property, so `->x` is printed as text."""),

    q("default-array-is-fresh", r'''
        <?php
        function add($item, $list = []) {
            $list[] = $item;
            return $list;
        }
        add(1);
        add(2);
        echo json_encode(add(3));
    ''', "[3]", ["[1,2,3]", "[2,3]", "[1,3]"],
      "A default value is rebuilt on every call and arrays are copied, so nothing accumulates",
      """Unlike Python, a PHP default is evaluated each time the function runs, and arrays are passed by value,
      so each call starts from an empty list. Only a `static` variable or a by-reference parameter would
      keep state between calls."""),

    q("integer-literal-forms", r'''
        <?php
        echo 0b101 + 017 + 0o17 + 0x1F + 1_000, " ", "017" + 1, " ",
             (int)"0x1A", " ", intval("0x1A", 16), " ", intval("012", 0), " ",
             octdec("17");
    ''', "1066 18 0 26 10 15", ["1060 18 0 26 12 15", "1066 18 26 26 10 15", "1066 16 0 26 10 15"],
      "A leading 0 in code means octal, but a numeric string with a leading 0 is just decimal",
      """In source code `017` is octal 15, and `0o17` is the same number spelled explicitly. The string "017"
      is plain decimal 17 when used as a number, and `(int)"0x1A"` stops at the x, giving 0. `intval` only
      honours the 0x and 0 prefixes when the base is 16 or 0."""),

    q("print-returns-one", r'''
        <?php
        echo "a" . print("b") . "c";
        $n = printf("xyz");
        echo " $n";
    ''', "bca1xyz 3", ["abc1xyz 3", "bcabc xyz 3", "a1bcxyz 3"],
      "print is an expression returning 1 and it swallows everything to its right",
      """`print` has very low precedence, so it takes everything to its right as its argument and prints "bc"
      first, then evaluates to 1. The echo then prints "a" joined with that 1. `printf` returns the length of
      what it printed."""),

    q("static-variable-in-method", r'''
        <?php
        class Box {
            function next() {
                static $n = 0;
                return ++$n;
            }
        }
        $a = new Box;
        $b = new Box;
        $a->next();
        $b->next();
        echo $a->next();
    ''', "3", ["1", "2", "0"],
      "A static variable in a method belongs to the method, not to each object",
      """`static $n` is initialised once and keeps its value between calls. In a method it is shared by every
      instance of the class, so the two calls through different objects count up one shared counter and the
      third call returns 3."""),

    q("destructuring-forms", r'''
        <?php
        [$a, $b] = [1, 2];
        [$a, $b] = [$b, $a];
        ["x" => $x, "y" => $y] = ["y" => 5, "x" => 6];
        [, $second, , $fourth] = [1, 2, 3, 4];
        [$p, [$q, $r]] = [1, [2, 3]];
        echo "$a$b $x$y $second$fourth $p$q$r";
    ''', "21 65 24 123", ["12 56 23 123", "21 56 24 123", "21 65 24 1[2,3]"],
      "Array destructuring swaps in one step; keyed patterns match names, not positions",
      """The right side is built completely before the assignment, so `[$a, $b] = [$b, $a]` is a safe swap.
      With string keys the pattern picks values by key regardless of order. Empty slots skip positions and
      nested patterns unpack inner arrays."""),

    q("spread-and-named-arguments", r'''
        <?php
        function f(int $a, int $b = 2, int ...$rest) {
            return $a . $b . count($rest);
        }
        echo implode(" ", [f(1), f(1, 3, 4, 5), f(b: 9, a: 1), f(...[1, 2, 3]),
                           f(...["b" => 7, "a" => 8])]);
    ''', "120 132 190 121 870", ["120 132 910 121 780", "120 132 190 123 870", "102 132 190 121 870"],
      "Named arguments can come in any order, and a string-keyed spread passes names",
      """Positional arguments after the declared ones are gathered by the variadic `...$rest`. Named arguments
      are matched by name, so `f(b: 9, a: 1)` sets a to 1 and b to 9. Spreading an array with string keys passes
      them by name too."""),

    q("array-function-return-values", r'''
        <?php
        $a = [3, 1, 2];
        echo json_encode([sort($a), $a, array_pop($a), array_shift($a), $a,
                          array_push($a, 9), array_unshift($a, 0)]);
    ''', "[true,[1,2,3],3,1,[2],2,3]", ["[[1,2,3],[1,2,3],3,1,[2],[2,9],[0,2,9]]",
                                        "[true,[1,2,3],3,1,[2],9,0]", "[true,[3,1,2],2,3,[1],2,3]"],
      "sort() and its relatives work in place and return true; push/unshift return the new length",
      """`sort` reorders the variable itself and returns a boolean. `array_pop` and `array_shift` return the
      removed element, and `array_push` and `array_unshift` return the new element count, not the array.
      Each argument is evaluated in order, so `$a` is printed in the state it had at that moment."""),

    q("sort-flags", r'''
        <?php
        $a = ["10", "9", "2", "1"];
        sort($a, SORT_STRING);
        $b = ["img12", "img10", "img2"];
        sort($b);
        $c = $b;
        sort($c, SORT_NATURAL);
        echo json_encode([$a, $b, $c]);
    ''', '[["1","10","2","9"],["img10","img12","img2"],["img2","img10","img12"]]',
      ['[["1","2","9","10"],["img10","img12","img2"],["img2","img10","img12"]]',
       '[["1","10","2","9"],["img2","img10","img12"],["img2","img10","img12"]]',
       '[["1","2","9","10"],["img2","img10","img12"],["img10","img12","img2"]]'],
      "Sorting uses PHP's comparison rules unless a flag says otherwise",
      """With SORT_STRING the numeric strings are compared as text, so "10" comes before "2". By default,
      "img12" and "img10" are not numeric, so they are also compared as strings and "img2" sorts last.
      SORT_NATURAL compares runs of digits as numbers."""),

    q("spaceship-compare", r'''
        <?php
        echo json_encode([1 <=> 2, "a" <=> "b", [1, 2] <=> [1, 3], "10" <=> "9",
                          "10" <=> "9a", true <=> false, null <=> false]);
    ''', "[-1,-1,-1,1,-1,1,0]", ["[-1,-1,-1,-1,-1,1,0]", "[-1,-1,-1,1,1,1,0]", "[-1,-1,-1,1,-1,1,-1]"],
      "<=> compares two numeric strings as numbers, but a non-numeric string forces a text compare",
      """"10" and "9" are both numeric, so the comparison is numeric and 10 is larger. "9a" is not numeric, so
      "10" and "9a" are compared character by character and "1" sorts before "9". null and false both
      convert to the boolean false, so they are equal."""),

    q("in-array-loose-and-strict", r'''
        <?php
        echo json_encode([in_array("abc", [0]), in_array("1e1", ["10"]),
                          in_array("1e1", ["10"], true),
                          array_search("1", [0, 1, "1"]), array_search("x", ["a"]),
                          array_search(0, ["x", "y"])]);
    ''', "[false,true,false,1,false,false]", ["[true,true,false,1,false,false]", "[false,true,false,2,false,false]",
                                              "[false,true,false,1,null,0]"],
      "in_array and array_search compare loosely unless strict is passed; search returns false",
      """Loose comparison treats the numeric strings "1e1" and "10" as equal, but PHP 8 no longer equates
      "abc" with 0. `array_search` returns the first matching key (1 for the integer 1) or false, never null,
      so use `=== false` when the key may be 0."""),

    q("string-function-grab-bag", r'''
        <?php
        echo implode("|", [ucwords("hello big-world"), strrev("abc"),
                           str_pad("5", 3, "0", STR_PAD_LEFT),
                           substr_count("aaa", "aa"), trim("xxhixx", "x"),
                           rtrim("1.000", ".0"), ltrim("0012", "0"),
                           str_word_count("a bc  d")]);
    ''', "Hello Big-world|cba|005|1|hi|1|12|3", ["Hello Big-World|cba|005|2|hi|1.|12|3",
                                                 "Hello Big-world|cba|500|1|hi|1|12|3",
                                                 "Hello Big-world|cba|005|1|hi|1.|12|4"],
      "rtrim takes a set of characters, so \".0\" strips every trailing dot and zero",
      """The second argument of the trim functions is a list of characters, not a suffix, so "1.000" loses the
      zeros and then the dot. `ucwords` only capitalises after whitespace by default, leaving the part after the
      hyphen alone. `substr_count` counts non-overlapping matches."""),

    q("explode-implode-edges", r'''
        <?php
        echo json_encode([explode(",", ""), explode(",", "a,,b"),
                          explode(",", "a,b,c", 2), explode(",", "a,b,c", -1),
                          str_split("abc", 2),
                          implode(",", [1, null, false, true, 2.0])]);
    ''', '[[""],["a","","b"],["a","b,c"],["a","b"],["ab","c"],"1,,,1,2"]',
      ['[[],["a","","b"],["a","b,c"],["a","b"],["ab","c"],"1,,,1,2"]', '[[""],["a","b"],["a","b,c"],["a","b"],["ab","c"],"1,,,1,2"]',
       '[[""],["a","","b"],["a","b,c"],["a","b"],["ab","c"],"1,null,false,1,2.0"]'],
      "explode of an empty string gives one empty element; null and false implode as nothing",
      """Splitting an empty string always returns an array with a single empty string, never an empty array.
      A positive limit caps the number of pieces, while a negative one drops that many from the end.
      `implode` converts values with string casts, so null and false vanish, true is 1 and 2.0 is "2"."""),

    q("closure-capture-modes", r'''
        <?php
        $x = 1;
        $f = function () use ($x) { return $x; };
        $x = 2;
        $g = fn() => $x;
        $x = 3;
        $h = function () use (&$x) { return ++$x; };
        $inc = fn() => $x++;
        $inc();
        echo $f(), $g(), $h(), $x;
    ''', "1244", ["1334", "3344", "1233"],
      "use () copies the value when the closure is made, arrow functions copy too, & shares",
      """`$f` captured 1 and `$g` captured 2 at the moment they were created. The arrow function `$inc`
      increments its own copy, so the outer `$x` stays 3. `$h` shares the variable by reference, so calling it
      makes `$x` 4, and that is the value echo shows after it."""),

    q("is-numeric-forms", r'''
        <?php
        echo json_encode([is_numeric("1e3"), is_numeric(" 1"), is_numeric("1 "),
                          is_numeric("."), is_numeric("0x1A"), is_numeric(""),
                          is_numeric("-.5"), is_numeric(null)]);
    ''', "[true,true,true,false,false,false,true,false]",
      ["[true,true,false,false,true,false,true,false]", "[true,false,false,false,false,false,true,false]",
       "[true,true,true,false,false,true,true,false]"],
      "Numeric strings may have surrounding whitespace (since PHP 8) and exponents, but not hex",
      """PHP 8 allows trailing whitespace as well as leading, so "1 " is numeric. Exponents and a bare leading
      decimal point like "-.5" are fine, while hex notation, the empty string and a lone dot are not."""),

    # ── Medium and hard: scope, references, generators, versions ───────────
    q("late-static-binding", r'''
        <?php
        class A {
            public static function make() { return new static; }
            public static function name() { return self::class; }
            public function who() { return static::class; }
        }
        class B extends A {}
        echo get_class(B::make()), B::name(), (new B)->who();
    ''', "BAB", ["AAB", "BBB", "AAA"],
      "static:: is the class that was called; self:: is the class where the code was written",
      """`new static` and `static::class` resolve to the class the call went through, so they say B. `self`
      is fixed at the class that contains the code, so `B::name()` still reports A. Use `static` for
      factory methods that subclasses inherit."""),

    q("reference-survives-array-copy", r'''
        <?php
        $x = [1, 2];
        $y = &$x[0];
        $z = $x;
        $z[0] = 99;
        echo $x[0], $z[1];
    ''', "992", ["12", "19", "9999"],
      "An element that is a reference stays shared when the array is copied",
      """Arrays are copied on assignment, but a slot that has been made a reference keeps pointing at the
      same value in the copy. Writing `$z[0]` therefore changes `$x[0]` as well. `$z[1]` is an ordinary slot
      and is just the copied 2."""),

    q("next-integer-key", r'''
        <?php
        $a = [5 => "a", 2 => "b"];
        $a[] = "c";
        $a["x"] = "d";
        $a[] = "e";
        $b = [1, 2, 3];
        array_pop($b);
        $b[] = "p";
        $c = [1, 2, 3];
        unset($c[2]);
        $c[] = "u";
        echo json_encode([array_keys($a), array_keys($b), array_keys($c)]);
    ''', '[[5,2,6,"x",7],[0,1,2],[0,1,3]]', ['[[5,2,0,"x",1],[0,1,2],[0,1,2]]',
                                            '[[5,2,6,"x",7],[0,1,3],[0,1,2]]',
                                            '[[5,2,3,"x",4],[0,1,2],[0,1,3]]'],
      "$a[] uses the largest integer key plus one; array_pop resets the counter, unset does not",
      """Appending takes the highest integer key ever used and adds 1, so after key 5 the next is 6, and
      string keys do not count. `array_pop` also rewinds that counter, so the popped slot is reused,
      whereas `unset` leaves the counter alone and the new element gets key 3."""),

    q("finally-overrides-return", r'''
        <?php
        function f() {
            try { return "try"; } finally { echo "F"; }
        }
        function g() {
            try { return 1; } finally { return 2; }
        }
        echo f(), g();
    ''', "Ftry2", ["tryF2", "Ftry1", "try2"],
      "finally always runs, and a return inside it replaces the pending return value",
      """In `f` the return value "try" is computed, then `finally` runs and prints F, and only then does the
      function hand the value back, so F comes first. A `return` inside `finally` discards the earlier one,
      which makes `g()` return 2."""),

    q("generator-send-and-return", r'''
        <?php
        function gen() {
            $r = yield 1;
            yield $r * 2;
            return 9;
        }
        $g = gen();
        $a = $g->current();
        $b = $g->send(5);
        $g->next();
        echo $a, $b, $g->getReturn();
    ''', "1109", ["1129", "1100", "1509"],
      "send() resumes the generator with a value for the yield and returns the next yielded value",
      """`current()` runs to the first yield and gives 1. `send(5)` makes that yield evaluate to 5, so `$r` is 5
      and the next yield produces 10, which `send` returns. The following `next()` finishes the function, and
      only then is the return value 9 available."""),

    q("yield-from-keys", r'''
        <?php
        function a() { yield 1; yield 2; }
        function b() { yield 0; yield from a(); yield 3; }
        echo json_encode(iterator_to_array(b())),
             json_encode(iterator_to_array(b(), false));
    ''', "[1,3][0,1,2,3]", ["[0,1,2,3][0,1,2,3]", "[0,1,2,3][1,3]", "[1,2,3][0,1,2,3]"],
      "yield from keeps the inner generator's keys, which then collide in iterator_to_array",
      """Each generator numbers its own yields from 0, and `yield from` passes the inner keys through. The
      keys 0 and 1 therefore occur twice, and `iterator_to_array` lets later values overwrite earlier ones,
      leaving [1, 3]. Passing false as the second argument discards the keys and keeps all four values."""),

    q("enum-lookup", r'''
        <?php
        enum Suit: string {
            case Hearts = "h";
            case Spades = "s";
        }
        echo Suit::from("h")->name, Suit::tryFrom("x")?->name ?? "none",
             count(Suit::cases()), Suit::Spades->value,
             Suit::Hearts === Suit::from("h");
    ''', "Heartsnone2s1", ["Hnone2s1", "heartsnone2s1", "Heartsnone2s"],
      "A backed enum looks up by value with from()/tryFrom(); name is the case label",
      """`from("h")` finds the case by its backing value, and `->name` is the case label "Hearts", not the
      value. `tryFrom` returns null for an unknown value, so the null-safe `?->` and `??` give the fallback.
      `cases()` lists both cases, and enum cases are singletons, so `===` is true."""),

    q("weak-mode-parameter-coercion", r'''
        <?php
        function i(int $x) { return $x; }
        function f(float $x) { return $x; }
        function s(string $x) { return $x; }
        echo json_encode([i("5"), i(5.0), i(true), f(5), s(12), s(1.5)],
                         JSON_PRESERVE_ZERO_FRACTION);
    ''', '[5,5,1,5.0,"12","1.5"]',
      ['["5",5,true,5,12,1.5]', '[5,5.0,1,5,"12","1.5"]', '[5,5,true,5.0,"12","1.5"]'],
      "Without strict_types, scalar arguments are converted to the declared type",
      """In the default weak mode PHP coerces compatible scalars: "5" becomes the int 5, 5.0 becomes 5, true
      becomes 1, and an int passed to a float parameter becomes a float. Numbers passed to a string
      parameter become strings. `declare(strict_types=1)` would turn most of these into TypeErrors."""),

    q("division-by-zero-family", r'''
        <?php
        $r = [];
        foreach ([fn() => 1 / 0, fn() => 1 % 0, fn() => intdiv(1, 0),
                  fn() => intdiv(PHP_INT_MIN, -1), fn() => fdiv(1, 0)] as $f) {
            try { $r[] = $f(); } catch (Throwable $e) { $r[] = get_class($e); }
        }
        echo implode(",", $r);
    ''', "DivisionByZeroError,DivisionByZeroError,DivisionByZeroError,ArithmeticError,INF",
      ["INF,0,0,ArithmeticError,INF", "DivisionByZeroError,0,DivisionByZeroError,ArithmeticError,INF",
       "DivisionByZeroError,DivisionByZeroError,DivisionByZeroError,INF,INF"],
      "Since PHP 8 dividing by zero throws; only fdiv gives INF",
      """The operators `/` and `%` and the function `intdiv` all throw DivisionByZeroError for a zero divisor.
      The one overflowing integer division, PHP_INT_MIN by -1, throws its parent class ArithmeticError.
      `fdiv` follows IEEE rules and returns INF."""),

    q("switch-loose-comparison", r'''
        <?php
        function kind($v) {
            switch ($v) {
                case 0: return "zero";
                case "a": return "a";
                case null: return "null";
                default: return "other";
            }
        }
        echo implode(",", [kind("a"), kind(0), kind(null), kind(""), kind("0"),
                           kind(false)]);
    ''', "a,zero,zero,null,zero,zero", ["a,zero,null,null,zero,zero", "zero,zero,zero,null,zero,zero",
                                        "a,zero,zero,other,zero,other"],
      "switch compares with ==, so null, false and \"0\" all match case 0",
      """Every `case` is tested with loose equality in order. null == 0 and false == 0 are true, so both
      land on "zero". In PHP 8 `"a" == 0` is false, so "a" reaches its own case, and "" == 0 is false too,
      but "" == null is true."""),

    q("match-is-strict", r'''
        <?php
        echo match ("1") { 1 => "int", "1" => "str", default => "none" },
             match (true) { 5 > 3 => "a", 2 > 1 => "b" },
             match (3) { 1, 2 => "low", 3, 4 => "mid", default => "hi" };
    ''', "stramid", ["intamid", "strbmid", "nonealow"],
      "match compares with ===, never falls through, and returns a value",
      """`match` uses strict comparison, so the string "1" does not match the integer arm. With `true` as the
      subject, the first arm whose condition is true wins, and the arms after it are not evaluated. An arm can
      list several values."""),

    q("nullsafe-chain-short-circuit", r'''
        <?php
        $o = null;
        echo json_encode([$o?->a->b, $o?->m(1)->n(), isset($o->a),
                          $o?->a ?? "dflt"]);
    ''', '[null,null,false,"dflt"]',
      ['[null,null,true,"dflt"]', '[null,null,false,null]', '[null,"error",false,"dflt"]'],
      "?-> short-circuits the whole rest of the chain, unlike Ruby's &.",
      """When the left side is null, the entire remaining chain is skipped and the result is null, so `->b` and
      `->n()` are never reached. `isset` on a null base simply returns false, and `??` then supplies the
      fallback."""),

    q("array-equality-order", r'''
        <?php
        echo json_encode([["a" => 1, "b" => 2] == ["b" => 2, "a" => 1],
                          ["a" => 1, "b" => 2] === ["b" => 2, "a" => 1],
                          [1, 2] == ["1", "2"], [1, 2] === ["1", "2"],
                          [0] == [false], [] == false, [[]] == [false]]);
    ''', "[true,false,true,false,true,true,true]", ["[false,false,true,false,true,true,true]",
                                                    "[true,true,true,false,true,true,true]",
                                                    "[true,false,true,false,true,true,false]"],
      "== on arrays ignores order but compares values loosely; === also demands order and types",
      """Two arrays are `==` when they have the same key/value pairs, in any order, and the values are
      compared with `==`. `===` needs the same pairs in the same order and of the same types. Because [] ==
      false, the nested comparison [[]] == [false] is true as well."""),

    q("sort-is-stable", r'''
        <?php
        $rows = [["n" => "b", "v" => 1], ["n" => "a", "v" => 1],
                 ["n" => "c", "v" => 0], ["n" => "d", "v" => 1]];
        usort($rows, fn($x, $y) => $x["v"] <=> $y["v"]);
        echo implode(array_column($rows, "n"));
    ''', "cbad", ["cabd", "cdab", "cbda"],
      "PHP 8 sorting is stable: equal elements keep their original order",
      """From PHP 8.0 `sort` and `usort` are stable, so the three elements with v = 1 stay in their original
      order b, a, d after the single v = 0 element moves to the front. Before 8.0 their order was
      unspecified."""),

    q("array-walk-versus-map", r'''
        <?php
        $a = [1, 2, 3];
        array_map(fn($x) => $x * 2, $a);
        array_walk($a, function (&$v) { $v += 1; });
        foreach ($a as $v) { $v = 0; }
        echo implode(",", $a);
    ''', "2,3,4", ["2,4,6", "0,0,0", "3,4,5"],
      "array_map returns a new array and array_walk edits only through a reference parameter",
      """The result of `array_map` is thrown away here, so it changes nothing. `array_walk` with `&$v` edits the
      elements in place, adding 1. A plain `foreach` assigns to a copy of each value, so zeroing it has no
      effect on the array."""),

    q("compact-extract-global", r'''
        <?php
        $a = 1; $b = 2;
        $r = compact("a", "b");
        extract(["c" => 3, "a" => 9]);
        function inside() { return isset($a) ? "set" : "unset"; }
        function viaGlobal() { global $a; return $a; }
        echo json_encode($r), $a, $c, inside(), viaGlobal(), $GLOBALS["b"];
    ''', '{"a":1,"b":2}93unset92', ['{"a":1,"b":2}13unset12', '{"a":1,"b":2}93set92', '{"a":9,"b":2}93unset92'],
      "Functions do not see outer variables; extract overwrites existing ones by default",
      """`compact` captures the values at that moment, so `$r` keeps a = 1. `extract` then overwrites `$a` with
      9 and creates `$c`. Inside a function the outer `$a` is invisible unless you declare it `global`
      or read `$GLOBALS`."""),

    q("string-offset-assignment", r'''
        <?php
        $s = "hello";
        $s[0] = "J";
        $s[1] = "E";
        $s[7] = "!";
        echo $s, "|", strlen($s), "|", $s[-1], "|", $s[2] . $s[3];
    ''', "JEllo  !|8|!|ll", ["JEllo!|6|!|ll", "JEllo !|7|!|ll", "JEllo  !|8|o|ll"],
      "Writing to a string offset past the end pads the gap with spaces",
      """A string can be changed one character at a time with an offset. Writing at index 7 of a five
      character string fills the missing indexes 5 and 6 with spaces, making the string 8 long. A negative
      offset counts from the end when reading."""),

    q("object-comparison", r'''
        <?php
        class P { public $x = 1; }
        $a = new P;
        $b = new P;
        $c = $a;
        $r = [$a == $b, $a === $b, $a === $c];
        $b->x = 2;
        $r[] = $a == $b;
        $r[] = $a < $b;
        echo json_encode($r);
    ''', "[true,false,true,false,true]", ["[true,true,true,false,true]", "[false,false,true,false,true]",
                                          "[true,false,true,true,false]"],
      "== compares class and properties; === means the very same object",
      """Two different objects of one class are `==` when all their properties are equal, but only `===` tests
      identity. After changing a property they are no longer `==`. Objects of one class are ordered by their
      properties, one by one, so `$a < $b` is true because 1 < 2."""),

    q("array-filter-keeps-keys", r'''
        <?php
        echo json_encode([array_filter([1, 0, 2, null, 3]),
                          array_values(array_filter([1, 0, 2])),
                          array_map(fn($x) => $x, [3 => "a", 5 => "b"]),
                          array_map(fn($x, $y) => $x . $y, [3 => "a", 5 => "b"],
                                    ["c", "d"]),
                          array_slice([1, 2, 3, 4], 1, 2),
                          array_slice(["a" => 1, 5 => 2, 6 => 3], 1)]);
    ''', '[{"0":1,"2":2,"4":3},[1,2],{"3":"a","5":"b"},["ac","bd"],[2,3],[2,3]]',
      ['[[1,2,3],[1,2],{"3":"a","5":"b"},["ac","bd"],[2,3],[2,3]]', '[{"0":1,"2":2,"4":3},[1,2],["a","b"],["ac","bd"],[2,3],[2,3]]',
       '[{"0":1,"2":2,"4":3},[1,2],{"3":"a","5":"b"},{"3":"ac","5":"bd"},[2,3],{"5":2,"6":3}]'],
      "array_filter keeps the original keys, which turns the JSON into an object",
      """`array_filter` removes values but leaves the surviving keys alone, so gaps appear and `json_encode`
      writes an object; wrap it in `array_values` for a clean list. `array_map` keeps keys for one array but
      renumbers when given several. `array_slice` renumbers integer keys unless asked to preserve them."""),

    q("unset-leaves-a-gap", r'''
        <?php
        $a = [1, 2, 3];
        unset($a[1]);
        $a[] = 4;
        $b = array_values($a);
        echo count($a), json_encode($a), json_encode($b),
             array_is_list($a) ? "L" : "M";
    ''', '3{"0":1,"2":3,"3":4}[1,3,4]M', ['3[1,3,4][1,3,4]L', '4{"0":1,"1":null,"2":3,"3":4}[1,3,4]M',
                                         '3{"0":1,"2":3,"1":4}[1,3,4]M'],
      "unset does not renumber, so the array stops being a list and encodes as an object",
      """Removing index 1 leaves keys 0, 2 and 3, and the appended 4 takes the next free index, 3. Because the
      keys are no longer 0..n-1, JSON writes an object. `array_values` re-indexes, and `array_is_list`
      tells the two shapes apart."""),

    q("sprintf-directives", r'''
        <?php
        echo sprintf("%05.1f|%-5s|%+d|%x|%'*6s|%b|%c|%5.1e|%03d|%u|%%",
                     3.14159, "ab", 5, 255, "ab", 5, 65, 12345.678, -5, 3);
    ''', "003.1|ab   |+5|ff|****ab|101|A|1.2e+4|-05|3|%",
      ["003.1|ab   |+5|ff|****ab|101|A|1.2e+04|-05|3|%", "3.1|ab   |5|FF|    ab|101|65|1.2e+4|-05|3|%",
       "003.1|   ab|+5|ff|****ab|101|A|1.2e+4|-05|3|"],
      "printf pads with 0 or any custom character; %e writes the exponent without padding",
      """The flags work as in C: `0` pads with zeros, `-` pads on the right and `+` forces a sign. A custom
      padding character is given after an apostrophe, as in `%'*6s`. PHP prints the exponent of `%e` with
      no leading zero, so it is e+4, not e+04."""),

    q("number-format-rounding", r'''
        <?php
        echo number_format(1234567.891), "|", number_format(1234567.891, 2), "|",
             number_format(1234.5678, 2, ",", "."), "|", number_format(0.5), "|",
             number_format(-0.4), "|", number_format(1234.5, 1, "", "");
    ''', "1,234,568|1,234,567.89|1.234,57|1|0|12345", ["1,234,567|1,234,567.89|1,234.57|0|-0|12345",
                                                       "1,234,568|1,234,567.89|1.234,57|1|-0|1234.5",
                                                       "1.234.568|1,234,567.89|1.234,57|1|0|12345"],
      "number_format rounds (not truncates) and with no argument keeps zero decimals",
      """With the default of zero decimals the value is rounded half away from zero, so 1234567.891 becomes
      1,234,568 and 0.5 becomes 1. The third and fourth arguments choose the decimal point and the thousands
      separator. Since PHP 8.0 a result that rounds to zero is never printed as -0."""),

    q("max-min-mixed-types", r'''
        <?php
        echo json_encode([array_sum(["1", "2.5", 3]), array_product([]),
                          max("10", "9"), max("10", "9a"), max(5, "apple"),
                          max([1, 2], [1, 3]), min("a", "B")]);
    ''', '[6.5,1,"10","9a","apple",[1,3],"B"]',
      ['[6.5,0,"10","9a","apple",[1,3],"B"]', '[6.5,1,"9","9a","apple",[1,3],"B"]', '[6.5,1,"10","10","5",[1,3],"a"]'],
      "max and min use the loose comparison rules, so numeric strings and text mix unevenly",
      """"10" and "9" are both numeric, so max compares them as numbers; "9a" is not numeric, so "10" and "9a"
      are compared as text and "9a" wins. A number against a non-numeric string compares as text too, and
      uppercase letters sort before lowercase ones. The product of an empty array is 1."""),

    q("echo-versus-json-floats", r'''
        <?php
        $f = 0.1 + 0.2;
        echo $f, " ", json_encode($f), " ", var_export($f, true), " ",
             $f == 0.3 ? "eq" : "ne", " ", round($f, 2) == 0.3 ? "eq" : "ne",
             " ", 1/3;
    ''', "0.3 0.30000000000000004 0.30000000000000004 ne eq 0.33333333333333",
      ["0.3 0.3 0.3 eq eq 0.33333333333333", "0.30000000000000004 0.30000000000000004 0.30000000000000004 ne eq 0.3333333333333333",
       "0.3 0.30000000000000004 0.3 ne ne 0.33333333333333"],
      "echo prints 14 significant digits, while json_encode and var_export print the exact shortest value",
      """The `precision` setting (14 by default) controls how `echo` and string conversion print floats, so
      the sum shows as 0.3. `json_encode` and `var_export` use the shortest representation that round-trips,
      0.30000000000000004. The comparison is made on the real value and is false."""),

    q("negative-zero-and-big-floats", r'''
        <?php
        echo implode("|", [round(-0.4), var_export(round(-0.4), true),
                           -0.0 == 0, floor(-0.5), 1.0, 1e15, 1e14, 2.50, 1e-7]);
    ''', "-0|-0.0|1|-1|1|1.0E+15|1.0E+14|2.5|1.0E-7",
      ["0|0.0|1|-1|1|1.0E+15|100000000000000|2.5|1.0E-7",
       "-0|-0.0|1|-1|1.0|1000000000000000|1.0E+14|2.5|0.0000001",
       "0|0|1|0|1|1.0E+15|1.0E+14|2.50|1.0E-7"],
      "Floats print without a trailing .0, round() can give -0, and big ones switch to E notation",
      """`round(-0.4)` rounds to the float negative zero, which `echo` prints as -0 even though it is `==` to
      0. The default `precision` of 14 digits means 1e14 already needs 15 digits and is printed as
      1.0E+14, and tiny values use E notation too. Whole floats lose their .0 when echoed."""),

    q("range-forms", r'''
        <?php
        echo json_encode([range(5, 1, 2), range("a", "e", 2), range(0, 1, 0.5),
                          range(10, 0, -5), range(3, 1), range(1, 2, 1)]);
    ''', '[[5,3,1],["a","c","e"],[0,0.5,1],[10,5,0],[3,2,1],[1,2]]',
      ['[[5,3,1],["a","c","e"],[0,0.5,1],[10,5,0],[],[1,2]]',
       '[[1,3,5],["a","c","e"],[0,0.5,1],[0,5,10],[3,2,1],[1,2]]',
       '[[5,3],["a","c"],[0,0.5],[10,5,0],[3,2,1],[1,2]]'],
      "range counts down if start > end, and the step is always positive",
      """Unlike a loop, `range(5, 1, 2)` goes downward on its own: 5, 3, 1, and the step must be written as a
      positive number. Letters work with a step too. A float step produces floats, which `json_encode` prints
      as 0, 0.5 and 1."""),

    q("array-unique-loose", r'''
        <?php
        echo json_encode([array_unique([4, "4", "3", 4, 3, "a", "A"]),
                          array_unique(["b", "b", "a"]),
                          array_flip(["a", "b", "a"]),
                          array_count_values(["x", "y", "x", 1, "1"])]);
    ''', '[{"0":4,"2":"3","5":"a","6":"A"},{"0":"b","2":"a"},{"a":2,"b":1},{"x":2,"y":1,"1":2}]',
      ['[[4,"3","a","A"],{"0":"b","2":"a"},{"a":2,"b":1},{"x":2,"y":1,"1":2}]',
       '[{"0":4,"2":"3","5":"a","6":"A"},{"0":"b","2":"a"},{"a":0,"b":1},{"x":2,"y":1,"1":2}]',
       '[{"0":4,"1":"4","2":"3","5":"a","6":"A"},{"0":"b","2":"a"},{"a":2,"b":1},{"x":2,"y":1,"1":1}]'],
      "array_unique compares loosely as strings and keeps the first key; flip keeps the last",
      """`array_unique` treats 4 and "4" as duplicates (it compares as strings) and keeps the first occurrence
      with its original key. `array_flip` swaps keys and values, and a repeated value keeps the later key.
      `array_count_values` counts 1 and "1" together."""),

    q("gettype-names", r'''
        <?php
        echo implode(",", [gettype(1.0), get_debug_type(1.0), gettype(null),
                           gettype(true), get_debug_type("a"), gettype(10 / 5),
                           gettype(10 / 4), gettype("5" + 5),
                           gettype("5" + "5.0"), gettype(1 <=> 2)]);
    ''', "double,float,NULL,boolean,string,integer,double,integer,double,integer",
      ["float,float,null,bool,string,int,float,int,float,int", "double,float,NULL,boolean,string,double,double,integer,double,integer",
       "double,float,NULL,boolean,string,integer,double,string,string,integer"],
      "gettype uses historical names (double, boolean, integer, NULL); get_debug_type uses modern ones",
      """`gettype` still reports "double", "boolean" and "integer" for compatibility, and "NULL" in capitals,
      while `get_debug_type` says float, bool and int. Arithmetic on numeric strings produces an int or a float
      by the shape of the text. `10 / 5` stays an integer because it divides exactly."""),

    q("array-splice-removes-and-inserts", r'''
        <?php
        $a = [1, 2, 3, 4];
        $r = array_splice($a, 1, 2, ["x"]);
        $b = ["a" => 1, "b" => 2, 3];
        array_splice($b, 1, 0, "new");
        echo json_encode([$r, $a, $b]);
    ''', '[[2,3],[1,"x",4],{"a":1,"0":"new","b":2,"1":3}]',
      ['[[2,3],[1,"x",4],["new",1,2,3]]', '[[1,2],[1,"x",4],{"a":1,"0":"new","b":2,"1":3}]',
       '[[2,3],[1,"x",2,3,4],{"a":1,"0":"new","b":2,"1":3}]'],
      "array_splice modifies the array in place, returns the removed part and renumbers integer keys",
      """`array_splice($a, 1, 2, ["x"])` cuts two elements starting at index 1, puts "x" in their place and
      returns the removed ones. Positions count elements, not keys, so inserting at 1 lands after "a".
      String keys survive but integer keys are renumbered from 0."""),

    q("str-replace-versus-strtr", r'''
        <?php
        echo str_replace(["a", "b"], ["b", "c"], "ab"),
             strtr("ab", ["a" => "b", "b" => "c"]),
             str_replace("l", "L", "hello", $n), $n,
             substr_replace("abcdef", "XY", 1, 3);
    ''', "ccbcheLLo2aXYef", ["bcbcheLLo2aXYef", "ccccheLLo2aXYef", "ccbcheLLo2aXYdef"],
      "str_replace applies its pairs one after another; strtr replaces all pairs at once",
      """`str_replace` with arrays works left to right on the result so far: a becomes b, then every b becomes
      c, giving "cc". `strtr` with an array looks at the original string only, so "ab" becomes "bc". The
      optional fourth argument of `str_replace` receives the number of replacements."""),

    q("and-or-versus-symbols", r'''
        <?php
        $a = true and false;
        $b = false or true;
        $c = true xor true;
        $d = (true and false);
        echo json_encode([$a, $b, $c, $d, true && false || true]);
    ''', "[true,false,true,false,true]", ["[false,true,false,false,true]", "[true,true,false,false,true]",
                                          "[true,false,false,false,true]"],
      "and, or and xor bind looser than =, so the assignment happens first",
      """`$a = true and false` is `($a = true) and false`, so `$a` is true. The same happens with `or`, which
      leaves `$b` as false and `xor` where `$c` is true. Parentheses or `&&` and `||` give the intuitive
      result."""),

    q("spread-merges-arrays", r'''
        <?php
        $x = [...[1, 2], ...[3], ...["a" => 1], ...["a" => 2, "b" => 3]];
        echo json_encode($x), count($x);
    ''', '{"0":1,"1":2,"2":3,"a":2,"b":3}5', ['[1,2,3,1,2,3]6', '{"0":1,"1":2,"2":3,"a":1,"b":3}5', '{"0":1,"1":2,"2":3,"a":2,"b":3}6'],
      "Spreading arrays renumbers integer keys and lets later string keys overwrite earlier ones",
      """Inside an array literal the spread operator behaves like `array_merge`: the integer keys are
      renumbered 0, 1, 2, while the string key "a" is overwritten by the later value. The result has five
      entries and is no longer a list, so it encodes as an object."""),
)
