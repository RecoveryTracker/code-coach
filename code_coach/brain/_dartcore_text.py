"""Dart core pack, part 3: String Surgery (the String methods) and Function Forms (parameters, arrows, closures).

Function bodies are written as local functions inside `main`, which Dart allows: the snippet is the body of `main`
and its last line prints (see the convention in `_dart_model.py`).
"""

from __future__ import annotations

from ._dart_model import (D, capitalise, dart_split, index_of, last_index_of, pad_left, pad_right, replace_all,
                          replace_first, to_upper)
from ._model import Maker

# ── 5. String Surgery ───────────────────────────────────────────────────


def _count(text: str, ch: str) -> int:
    return len(dart_split(text, ch)) - 1


STRINGS: list[Maker] = [
    D("print('$w'.substring(1));", lambda p: p["w"][1:], "substring(1) drops the first character."),
    D("print('$w'.substring(0, 2));", lambda p: p["w"][:2], "substring(0, 2) takes positions 0 and 1: the end is left out."),
    D("print('$w'.substring(1, 3));", lambda p: p["w"][1:3], "substring(1, 3) takes positions 1 and 2."),
    D("print('$w'.substring(2));", lambda p: p["w"][2:], "substring(2) takes everything from position 2."),
    D("print('$w'.substring($L - 2));", lambda p: p["w"][-2:], "Starting two from the end gives the last two characters."),
    D("print('$w'[0]);", lambda p: p["w"][0], "Index 0 is the first character."),
    D("print('$w'[$L - 1]);", lambda p: p["w"][-1], "The last index is length - 1."),
    D("print('$w $v'.split(' '));", lambda p: [p["w"], p["v"]], "split cuts at every separator and gives a list."),
    D("print('$a,$b,$c'.split(','));", lambda p: [str(p["a"]), str(p["b"]), str(p["c"])], "The pieces are strings, even the digits."),
    D("print('$w'.split(''));", lambda p: list(p["w"]), "Splitting on the empty string gives the letters."),
    D("print('$w-$v'.split('-').last);", lambda p: p["v"], "split gives a list; last is its final piece."),
    D("print('$w $v $x'.split(' ').length);", 3, "Two spaces make three pieces."),
    D("print('$a'.padLeft(3, '0'));", lambda p: pad_left(str(p["a"]), 3, "0"), "padLeft fills on the left until the text is 3 long."),
    D("print('$a'.padRight(4, '.'));", lambda p: pad_right(str(p["a"]), 4, "."), "padRight fills on the right until the text is 4 long."),
    D("print('$w'.padLeft(8, '*'));", lambda p: pad_left(p["w"], 8, "*"), "The stars fill the gap on the left."),
    D("print('$w'.padLeft($L + 2, '_'));", lambda p: "__" + p["w"], "The width is two more than the word, so two fillers go in."),
    D("print('  $w  '.trim());", lambda p: p["w"], "trim removes the spaces at both ends."),
    D("print('  $w  '.trim().length);", lambda p: p["L"], "After trim only the word is left."),
    D("print('  $w  '.length);", lambda p: p["L"] + 4, "Every space counts as a character."),
    D("print('$w  '.trimRight() + '|');", lambda p: p["w"] + "|", "trimRight removes the spaces on the right."),
    D("print('$w'.toUpperCase());", lambda p: to_upper(p["w"]), "toUpperCase makes every letter a capital."),
    D("print('$W'.toLowerCase());", lambda p: p["w"], "toLowerCase makes every letter small."),
    D("print('$w'.toUpperCase()[0]);", lambda p: to_upper(p["w"][0]), "Upper-case first, then take the first character."),
    D("print('$w'[0].toUpperCase() + '$w'.substring(1));", lambda p: capitalise(p["w"]), "Capitalise the first letter and join the rest: Dart has no capitalize()."),
    D("print('$w'.substring(1).toUpperCase());", lambda p: to_upper(p["w"][1:]), "substring first, then upper-case what is left."),
    D("print('$w'.replaceAll('$y', '*'));", lambda p: replace_all(p["w"], p["y"], "*"), "replaceAll swaps every match."),
    D("print('$w'.replaceFirst('$y', '*'));", lambda p: replace_first(p["w"], p["y"], "*"), "replaceFirst swaps only the first match."),
    D("print('$w $v'.replaceAll(' ', ''));", lambda p: p["w"] + p["v"], "Replacing the space with nothing deletes it."),
    D("print('$w'.replaceAll('$y', '').length);", lambda p: p["L"] - _count(p["w"], p["y"]), "Every match is deleted, so the text gets shorter by the number of matches."),
    D("print('$w'.replaceAll('a', 'A'));", lambda p: replace_all(p["w"], "a", "A"), "Only the letter a changes."),
    D("print('$w'.contains('$y'));", True, "The letter is one of the word's letters."),
    D("print('$w'.contains('$x'));", lambda p: p["x"] in p["w"], "contains is true when the text appears anywhere inside."),
    D("print('$w'.startsWith('$f'));", True, "The word does begin with its first letter."),
    D("print('$w'.endsWith('$f'));", lambda p: p["w"].endswith(p["f"]), "endsWith looks only at the end of the word."),
    D("print('$w'.indexOf('$y'));", lambda p: index_of(p["w"], p["y"]), "indexOf gives the first position, counting from 0."),
    D("print('$w'.lastIndexOf('$y'));", lambda p: last_index_of(p["w"], p["y"]), "lastIndexOf gives the last position."),
    D("print('$w'.indexOf('$x'));", lambda p: index_of(p["w"], p["x"]), "indexOf gives -1 when the text is not there."),
    D("print('$w'.indexOf('$y') + 1);", lambda p: index_of(p["w"], p["y"]) + 1, "The first position of the letter, plus one."),
    D("print('$w'.split('$y').length - 1);", lambda p: _count(p["w"], p["y"]), "Cutting at every match makes one piece more than the matches."),
    D("print('$w'.codeUnitAt(0));", lambda p: ord(p["w"][0]), "codeUnitAt gives the character's number: a is 97."),
    D("print('$w'.codeUnitAt(0) - 96);", lambda p: ord(p["w"][0]) - 96, "a is 97, so a small letter minus 96 is its place in the alphabet."),
    D("print(String.fromCharCode('$w'.codeUnitAt(0) + 1));", lambda p: chr(ord(p["w"][0]) + 1), "One more than the code is the next letter."),
    D("print(String.fromCharCode(97 + $a));", lambda p: chr(97 + p["a"]), "97 is a, so 97 + 2 is c, and so on."),
    D("print('$W'.codeUnitAt(0));", lambda p: ord(p["W"][0]), "Capital letters have smaller codes: A is 65."),
    D("print('$w'.toUpperCase().codeUnitAt(0) - '$w'.codeUnitAt(0));", -32, "A capital is always 32 below its small letter."),
    D("print('$w' * 2);", lambda p: p["w"] * 2, "* repeats the string."),
    D("print('-' * $n);", lambda p: "-" * p["n"], "* repeats the dash n times."),
    D("print(''.isEmpty);", True, "The empty string has no characters."),
    D("print(' '.isEmpty);", False, "A space is a character, so the string is not empty."),
    D("print(' '.trim().isEmpty);", True, "trim removes the space, leaving nothing."),
    D("print('$w'.isNotEmpty);", True, "The word has characters."),
    D("print('$w'.split('').reversed.join());", lambda p: p["w"][::-1], "Letters, backwards, glued together again."),
    D("print('$w'.split('').toSet().length);", lambda p: len(set(p["w"])), "A set keeps each letter once."),
    D("print('a-b-c'.replaceAll('-', ''));", "abc", "The dashes are deleted."),
    D("var w = '$w';\nprint('$${w.toUpperCase()}!');", lambda p: to_upper(p["w"]) + "!", "The braces after a dollar sign can hold any expression, a method call included."),
    D("print('Hello'.toLowerCase() == 'hello');", True, "After toLowerCase the two are the same."),
    D("print('Hello' == 'hello');", False, "Strings are compared letter by letter, capitals included."),
    D("print('$w $v'.split(' ').map((s) => s[0]).join());", lambda p: p["w"][0] + p["v"][0], "The first letter of each word, glued together."),
    D("print(String.fromCharCodes([72, 105]));", "Hi", "72 is H and 105 is i."),
    D("print('a1b2c3'.replaceAll(RegExp(r'[0-9]'), ''));", "abc", "The pattern matches every digit, and each is deleted."),
    D("print('x$a'.contains(RegExp(r'[0-9]')));", True, "The text has a digit in it."),
    D("print('a,b;c'.split(RegExp('[,;]')));", ["a", "b", "c"], "The pattern cuts at a comma or a semicolon."),
    D("print('$w'.length + '$v'.length);", lambda p: len(p["w"]) + len(p["v"]), "Add the two lengths."),
    D("print('$w'.compareTo('$v') < 0);", lambda p: p["w"] < p["v"], "Strings compare alphabetically: the earlier word is smaller."),
    D("print('$w'.toUpperCase().toLowerCase());", lambda p: p["w"], "Capitals first, then back to small: the word as it began."),
    D("print(' $w'.trim() == '$w');", True, "trim removes the leading space."),
    D("print('$w\\n'.length);", lambda p: p["L"] + 1, "\\n is one character, the newline."),
    D("print(r'$w\\n'.length);", lambda p: p["L"] + 2, "In a raw string r'...' a backslash is just a character, so \\n is two."),
]

# ── 6. Function Forms ───────────────────────────────────────────────────


def _fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _fact(n: int) -> int:
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out


FUNCS: list[Maker] = [
    D("int sq(int x) => x * x;\nprint(sq($a));", lambda p: p["a"] ** 2, "=> is shorthand for { return ...; }."),
    D("int add(int a, [int b = $b]) => a + b;\nprint(add($a));", lambda p: p["a"] + p["b"], "Square brackets make b optional; its default is used when left out."),
    D("int add(int a, [int b = $b]) => a + b;\nprint(add($a, $c));", lambda p: p["a"] + p["c"], "The second argument is given, so the default is not used."),
    D("String greet({String name = '$w'}) => 'Hi $$name';\nprint(greet());", lambda p: "Hi " + p["w"], "Curly brackets make named parameters; name falls back to its default."),
    D("String greet({String name = '$w'}) => 'Hi $$name';\nprint(greet(name: '$v'));", lambda p: "Hi " + p["v"], "A named argument is given with its name: name: value."),
    D("int area({required int w, required int h}) => w * h;\nprint(area(h: $a, w: $b));", lambda p: p["a"] * p["b"], "Named arguments can come in any order."),
    D("int f({int a = 0, int b = 0}) => a - b;\nprint(f(b: $a, a: $b));", lambda p: p["b"] - p["a"], "Each value goes to the name it carries, not by position."),
    D("String join(String a, [String? b]) => a + (b ?? '!');\nprint(join('$w'));", lambda p: p["w"] + "!", "b was left out, so it is null and ?? supplies the !."),
    D("String join(String a, [String? b]) => a + (b ?? '!');\nprint(join('$w', '$v'));", lambda p: p["w"] + p["v"], "b was given, so the fallback is not used."),
    D("var count = 0;\nvoid inc() => count++;\ninc();\ninc();\ninc();\nprint(count);", 3, "The function changes the variable it was written next to."),
    D("int Function() counter() {\n  var c = 0;\n  return () => ++c;\n}\nvar f = counter();\nf();\nprint(f());", 2, "The returned function remembers c: the second call gives 2."),
    D("int Function() counter() {\n  var c = 0;\n  return () => ++c;\n}\nvar g = counter();\nvar h = counter();\ng();\ng();\nprint(h());", 1, "Each call to counter() makes a new c, so h starts at 1."),
    D("var fs = <Function>[];\nfor (var i = 0; i < 3; i++) {\n  fs.add(() => i);\n}\nprint(fs[0]());", 0, "Each turn of the loop has its own i, so the first closure keeps 0."),
    D("var fs = <Function>[];\nfor (var i = 0; i < 3; i++) {\n  fs.add(() => i);\n}\nprint(fs.map((f) => f()).toList());", [0, 1, 2], "Each closure kept the i of its own turn."),
    D("f() {}\nprint(f());", None, "A function with no return gives null."),
    D("String sign(int n) {\n  if (n < 0) return 'neg';\n  if (n == 0) return 'zero';\n  return 'pos';\n}\nprint(sign($a - $b));", lambda p: "neg" if p["a"] < p["b"] else "pos", "The first return that is reached ends the function."),
    D("String sign(int n) {\n  if (n < 0) return 'neg';\n  if (n == 0) return 'zero';\n  return 'pos';\n}\nprint(sign($a - $a));", "zero", "a - a is 0, which stops at the second return."),
    D("int fact(int n) => n <= 1 ? 1 : n * fact(n - 1);\nprint(fact($k + 2));", lambda p: _fact(p["k"] + 2), "A function that calls itself: n * (n-1) * ... * 1."),
    D("int fib(int n) => n < 2 ? n : fib(n - 1) + fib(n - 2);\nprint(fib($n % 10));", lambda p: _fib(p["n"] % 10), "Each Fibonacci number is the sum of the two before it: 0, 1, 1, 2, 3, 5, 8, 13..."),
    D("int sum(int n) => n == 0 ? 0 : n + sum(n - 1);\nprint(sum($a));", lambda p: p["a"] * (p["a"] + 1) // 2, "The sum 1 + 2 + ... + n."),
    D("int apply(int Function(int) f, int x) => f(x);\nprint(apply((n) => n * $a, $b));", lambda p: p["a"] * p["b"], "A function can be passed in as an argument."),
    D("var twice = (int x) => x * 2;\nprint(twice($a));", lambda p: 2 * p["a"], "A function can be stored in a variable and called with ()."),
    D("var inc = (int x) => x + 1;\nvar dbl = (int x) => x * 2;\nprint(dbl(inc($a)));", lambda p: (p["a"] + 1) * 2, "inc runs first, then dbl on its result."),
    D("var inc = (int x) => x + 1;\nvar dbl = (int x) => x * 2;\nprint(inc(dbl($a)));", lambda p: p["a"] * 2 + 1, "dbl runs first, then inc on its result."),
    D("int Function(int) f = (x) => x + 1;\nf = (x) => x * $a;\nprint(f($b));", lambda p: p["a"] * p["b"], "f was given a new function, and that is the one called."),
    D("int f([int x = $a]) => x * 2;\nprint(f());", lambda p: 2 * p["a"], "No argument, so x is its default."),
    D("int f([int x = $a]) => x * 2;\nprint(f($b));", lambda p: 2 * p["b"], "The argument replaces the default."),
    D("String f(String a, [String b = 'B', String c = 'C']) => a + b + c;\nprint(f('x', 'y'));", "xyC", "Optional positional parameters fill from the left."),
    D("String f(String a, [String b = 'B', String c = 'C']) => a + b + c;\nprint(f('x'));", "xBC", "Both optional ones use their defaults."),
    D("void bump(int n) {\n  n++;\n}\nvar x = $a;\nbump(x);\nprint(x);", lambda p: p["a"], "The function changed its own copy of the number."),
    D("void add9(List<int> xs) => xs.add(9);\nvar a = [$a];\nadd9(a);\nprint(a);", lambda p: [p["a"], 9], "A list is passed by reference, so add9 changed the caller's list."),
    D("void reset(List<int> xs) {\n  xs = [];\n}\nvar a = [$a];\nreset(a);\nprint(a);", lambda p: [p["a"]], "xs = [] points the parameter at a new list; the caller's list is untouched."),
    D("int Function(int) adder(int n) => (x) => x + n;\nprint(adder($a)($b));", lambda p: p["a"] + p["b"], "adder(a) returns a function that adds a; calling it with b gives the sum."),
    D("String f({String? name}) => name ?? 'anon';\nprint(f());", "anon", "name was not given, so it is null and ?? supplies the fallback."),
    D("String f({String? name}) => name ?? 'anon';\nprint(f(name: '$w'));", lambda p: p["w"], "name was given, so the fallback is not used."),
    D("T first<T>(List<T> xs) => xs[0];\nprint(first([$a, $b]));", lambda p: p["a"], "A generic function works for any type: here it gives the first item."),
    D("T first<T>(List<T> xs) => xs[0];\nprint(first(['$w', '$v']));", lambda p: p["w"], "The same function, now with strings."),
    D("print((() => $a)());", lambda p: p["a"], "The function is written and called at once."),
    D("print(((int x) => x * $a)($b));", lambda p: p["a"] * p["b"], "The anonymous function is called straight away with b."),
    D("bool isEven(int n) => n % 2 == 0;\nprint([$a, $b, $c, $d].where(isEven).toList());", lambda p: [x for x in (p["a"], p["b"], p["c"], p["d"]) if x % 2 == 0], "A function's name can be passed as the test."),
    D("int sq(int x) => x * x;\nprint([$a, $b, $c].map(sq).toList());", lambda p: [x * x for x in (p["a"], p["b"], p["c"])], "map calls sq on every item."),
    D("var total = 0;\n[$a, $b, $c].forEach((x) => total += x);\nprint(total);", lambda p: p["a"] + p["b"] + p["c"], "The function adds each item to the outer variable."),
    D("String f(int n) => switch (n) { 1 => 'one', 2 => 'two', _ => 'many' };\nprint(f($k));", lambda p: {1: "one", 2: "two"}.get(p["k"], "many"), "A switch expression picks the first case that matches; _ matches anything."),
    D("int f(int a, int b) => a - b;\nprint(f($a, $b));", lambda p: p["a"] - p["b"], "Positional arguments go in order."),
    D("int f(int a, int b) => a - b;\nprint(f($b, $a));", lambda p: p["b"] - p["a"], "Swapped arguments, swapped result."),
    D("String hello() => 'hi';\nprint(hello() + hello());", "hihi", "Each call gives hi."),
    D("int f(int a, {int b = 10}) => a + b;\nprint(f($a));", lambda p: p["a"] + 10, "b is left at its default of 10."),
    D("int f(int a, {int b = 10}) => a + b;\nprint(f($a, b: $b));", lambda p: p["a"] + p["b"], "The named argument replaces the default."),
    D("int f(int n) {\n  if (n > $c) return n;\n  return f(n + 1);\n}\nprint(f($a));", lambda p: max(p["a"], p["c"] + 1), "It counts up until n is bigger than the limit."),
    D("int total(List<int> l) => l.fold(0, (s, x) => s + x);\nprint(total([$a, $b, $c]));", lambda p: p["a"] + p["b"] + p["c"], "fold adds up the items, starting from 0."),
    D("String describe(int n) {\n  if (n.isEven) return 'even';\n  return 'odd';\n}\nprint(describe($a));", lambda p: "even" if p["a"] % 2 == 0 else "odd", "An even number returns early."),
    D("var f = (int a, int b) => a * b;\nprint(f($a, $b));", lambda p: p["a"] * p["b"], "An anonymous function with two parameters."),
    D("var x = $a;\nvar f = () => x;\nx = $b;\nprint(f());", lambda p: p["b"], "A closure keeps the variable itself, not the value it had."),
    D("int x = $a;\nvoid change() {\n  x = $b;\n}\nchange();\nprint(x);", lambda p: p["b"], "The function assigns the outer x."),
    D("var x = $a;\nvoid f() {\n  var x = $b;\n  x++;\n}\nf();\nprint(x);", lambda p: p["a"], "The x inside f is a different variable that hides the outer one."),
    D("int count(String s, String ch) => s.split(ch).length - 1;\nprint(count('$w', '$y'));", lambda p: _count(p["w"], p["y"]), "split makes one piece more than there are matches."),
    D("String rep(String s, [int n = 2]) => s * n;\nprint(rep('$w'));", lambda p: p["w"] * 2, "n is its default of 2."),
    D("String rep(String s, [int n = 2]) => s * n;\nprint(rep('$w', $k));", lambda p: p["w"] * p["k"], "n is the argument given."),
    D("var greet = (String n) => 'Hi $$n';\nprint(greet('$w'));", lambda p: "Hi " + p["w"], "An anonymous function that builds a string."),
    D("void Function(int) show = (x) => print(x + $a);\nshow($b);", lambda p: p["a"] + p["b"], "The function prints instead of returning; calling it shows the sum."),
]

