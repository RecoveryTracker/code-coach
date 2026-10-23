"""Dart words, part 1: null safety, the basic types, operators and functions.

Every example is run by tests/test_glossary.py with the real `dart` (all of them in one batch, through
tests/dart_oracle.py). An example without `main(` is the BODY of main (the same convention as Brain Drills);
one with `main(` is a whole program. Dart 3.7 is the version on this machine."""

from __future__ import annotations

from .entry import Entry, dart

TERMS: list[Entry] = [
    # ── Null safety ─────────────────────────────────────────────────────
    *dart(
        "null-safety",
        "Null safety",
        "Dart's rule that a variable can hold null only if its type says so, with a ? after it. The compiler checks "
        "this before the program runs, so a forgotten null cannot crash it later.",
        see=("null", "nullable-type", "type-promotion"),
        priority=45,
        aka=("sound null safety", "non-nullable", "non-nullable type"),
        rules=(
            "int and String can never be null. int? and String? can.",
            "Using a nullable value as if it had a value (n.isEven when n is int?) does not compile.",
            "Check first (if (n != null)), or use ?., ?? or ! to say what should happen.",
        ),
        example="""
            String a = 'x';
            String? b;
            print(a.length);
            print(b?.length ?? 0);
        """,
        out="1\n0",
    ),
    *dart(
        "null",
        "null",
        "Dart's value for 'no value here'. Only a nullable type such as String? can hold it, and a nullable variable "
        "with no value yet starts as null.",
        see=("nullable-type", "null-coalescing", "null-aware-access"),
        priority=60,
        aka=("none", "nil", "nothing", "null value"),
        detect=(r"\bnull\b",),
        rules=(
            "x == null tests for it. print(null) shows null.",
            "int x = null; does not compile: plain types never hold null.",
            "null is not 0, '' or false: Dart has no 'falsy' values, so if (null) does not compile either.",
        ),
        example="""
            String? name;
            print(name);
            print(name == null);
            name = 'Ann';
            print(name);
        """,
        out="null\ntrue\nAnn",
    ),
    *dart(
        "nullable-type",
        "Nullable type (?)",
        "A type with a ? after it, like int? or String?. It holds the normal value or null.",
        see=("null", "null-safety", "null-assertion"),
        priority=60,
        aka=("nullable", "optional type", "question mark type"),
        detect=(r"\b(?:int|double|num|bool|String|List|Map|Set|Object|dynamic|[A-Z]\w*)(?:<[^<>\n]*>)?\?\s+[a-z_]\w*\s*[=;,)]",),
        rules=(
            "int is never null; int? may be. List<int?> is a list whose items may be null; List<int>? is a list that may itself be null.",
            "You cannot use a nullable value directly: n + 1 does not compile when n is int?.",
            "Ways in: an if check, n ?? 0, n?.method(), or n! when you are sure.",
        ),
        example="""
            int? age;
            print(age?.isEven);
            age = 3;
            print(age.isOdd);
        """,
        out="null\ntrue",
    ),
    *dart(
        "null-assertion",
        "Null assertion (!)",
        "A ! after an expression tells Dart 'this is not null'. If it is null after all, the program throws an error.",
        see=("nullable-type", "null-coalescing", "type-promotion"),
        priority=70,
        aka=("bang operator", "!", "null check operator", "null-check", "not null assertion"),
        detect=(r"[\w)\]]!(?!=)\s*[.\[)\];,]",),
        rules=(
            "name! has the non-null type, so name!.length compiles when name is String?.",
            "If the value is null, it throws a TypeError: 'Null check operator used on a null value'.",
            "Prefer an if check, ?? or ?. when the value might really be missing; use ! only when you can prove it is there.",
        ),
        example="""
            String? pick(bool ok) => ok ? 'hi' : null;
            print(pick(true)!.length);
            try {
              print(pick(false)!.length);
            } catch (e) {
              print(e);
            }
        """,
        out="2\nNull check operator used on a null value",
    ),
    *dart(
        "null-coalescing",
        "Null-coalescing (??)",
        "a ?? b means a, unless a is null, and then b. It is Dart's way of giving a default to a value that may be missing.",
        see=("null-aware-assignment", "null-aware-access", "default-value"),
        priority=75,
        aka=("??", "if null", "if-null operator", "null coalescing", "elvis"),
        detect=(r"\?\?(?!=)",),
        rules=(
            "Only null triggers it: 0, '' and false are real values and are kept.",
            "The right side is worked out only when the left is null (short-circuit).",
            "It chains from the left: a ?? b ?? c is the first one that is not null.",
        ),
        example="""
            String? name;
            int? zero = 0;
            print(name ?? 'guest');
            print(zero ?? 5);
        """,
        out="guest\n0",
    ),
    *dart(
        "null-aware-access",
        "Null-aware access (?.)",
        "a?.b reads b from a, but gives null instead of an error when a itself is null.",
        see=("null-coalescing", "nullable-type", "null-assertion"),
        priority=75,
        aka=("?.", "optional chaining", "optional-chaining", "null-aware operator", "null shorting", "safe call", "?[]"),
        detect=(r"\?\.(?!\.)", r"\?\["),
        rules=(
            "The result is nullable: s?.length is int?.",
            "If a is null, the rest of the chain is skipped too: a?.b.c is null, not an error.",
            "Also for calls (a?.run()) and indexing (list?[0]). Pair it with ?? for a default: s?.length ?? 0.",
        ),
        example="""
            int? lengthOf(String? s) => s?.length;
            print(lengthOf(null));
            print(lengthOf('hello'));
        """,
        out="null\n5",
    ),
    *dart(
        "null-aware-assignment",
        "Null-aware assignment (??=)",
        "a ??= b stores b in a only when a is currently null. Otherwise a is left alone.",
        see=("null-coalescing", "null", "default-value"),
        priority=80,
        aka=("??=", "assign if null", "null aware assignment"),
        detect=(r"\?\?=",),
        rules=(
            "The right side is not even worked out when a already has a value.",
            "Handy for defaults and caches: cache[key] ??= compute(key).",
            "m['k'] ??= 0 on a Map adds the key only if it is missing (or its value is null).",
        ),
        example="""
            int? count;
            count ??= 10;
            count ??= 99;
            print(count);
            final m = <String, int>{};
            m['a'] ??= 1;
            m['a'] ??= 2;
            print(m);
        """,
        out="10\n{a: 1}",
    ),
    *dart(
        "late",
        "late",
        "Marks a variable that has no value yet but will be given one before anyone reads it. With an initializer, "
        "the value is worked out only the first time the variable is read.",
        see=("null-safety", "final", "nullable-type"),
        priority=70,
        aka=("late variable", "late final", "lazy initialization", "lazy variable"),
        detect=(r"\blate\b",),
        rules=(
            "Reading a late variable that was never given a value throws a LateError ('has not been initialized').",
            "late final can be set once, later, after the declaration.",
            "late int v = compute(); does not call compute() until v is first read (and only once).",
        ),
        example="""
            int calls = 0;
            late int value = ++calls * 10;
            print(calls);
            print(value);
            print(value);
            print(calls);
        """,
        out="0\n10\n10\n1",
    ),
    *dart(
        "final",
        "final",
        "Declares a variable that can be set only once. After that it always refers to the same value, though an object "
        "inside it may still change.",
        see=("const", "var", "immutable"),
        priority=50,
        aka=("final variable", "final field", "single assignment"),
        detect=(r"\bfinal\b",),
        rules=(
            "final x = 1; x = 2; does not compile.",
            "The value can be worked out at run time: final now = DateTime.now(); is fine.",
            "final list = [1]; list.add(2); is allowed: the variable is fixed, the list it holds is not frozen.",
            "const is stricter: the value must be known before the program runs.",
        ),
        example="""
            final items = [1, 2];
            items.add(3);
            print(items);
        """,
        out="[1, 2, 3]",
    ),
    *dart(
        "const",
        "const",
        "A compile-time constant: a value fully known before the program runs, and never changeable. A const list or "
        "map cannot be added to or edited.",
        see=("final", "immutable", "const-constructor"),
        priority=60,
        aka=("constant", "compile-time constant", "const list", "constants"),
        detect=(r"\bconst\b",),
        rules=(
            "const needs a value Dart can work out at compile time: const t = DateTime.now(); does not compile.",
            "Changing a const collection throws an UnsupportedError: const [1, 2].add(3) fails when it runs.",
            "Equal const values are one shared object: identical(const [1], const [1]) is true.",
            "A const object needs a const constructor.",
        ),
        example="""
            const nums = [1, 2];
            try {
              nums.add(3);
            } catch (e) {
              print('cannot add');
            }
            print(identical(const [1], const [1]));
        """,
        out="cannot add\ntrue",
    ),
    *dart(
        "var",
        "var",
        "Declares a variable and lets Dart work out its type from the first value. The type is then fixed.",
        see=("variable", "dynamic", "final"),
        priority=40,
        aka=("type inference", "inferred type", "type-inference", "inference"),
        detect=(r"\bvar\b",),
        rules=(
            "var n = 3; makes n an int; n = 'three'; then does not compile.",
            "var x; with no value has type dynamic, which turns type checking off. Give it a type or a value.",
            "The type is worked out when you write the code, not each time it runs.",
        ),
        example="""
            var n = 3;
            var s = 'three';
            var xs = [1, 2];
            print(n.runtimeType);
            print(s.runtimeType);
            print(xs.runtimeType);
        """,
        out="int\nString\nList<int>",
    ),
    *dart(
        "type-promotion",
        "Type promotion",
        "After a check such as x != null or x is String, Dart treats the variable as the narrower type for the rest of "
        "that branch, so you can use it without !.",
        see=("null-assertion", "type-check", "null-safety"),
        priority=65,
        aka=("promotion", "flow analysis", "type promotion", "smart cast", "type narrowing", "narrowing"),
        detect=(r"\bif\s*\(\s*\w+\s*(?:!=\s*null|is\s+!?\w)",),
        rules=(
            "Works for local variables and parameters: if (s != null) { s.length } compiles when s is String?.",
            "Does not work for ordinary fields of a class (another piece of code could change them): copy the field into a local variable first.",
            "An early exit promotes the rest of the function: if (s == null) return; then s is non-null below.",
        ),
        example="""
            String describe(Object? v) {
              if (v is String) return 'text of ${v.length}';
              if (v is int && v > 5) return 'big int';
              return 'other';
            }
            print(describe('abc'));
            print(describe(9));
            print(describe(null));
        """,
        out="text of 3\nbig int\nother",
    ),
    *dart(
        "dynamic",
        "dynamic",
        "A type that turns type checking off: any member can be used on it, and a mistake only shows up when the program "
        "runs. Object? also accepts anything but only lets you use what every object has.",
        see=("var", "type", "type-check"),
        priority=55,
        aka=("object type", "any", "any type"),
        detect=(r"\bdynamic\b", r"\bObject\??\s+\w+"),
        rules=(
            "dynamic d = 'hi'; d.length works; after d = 5 the same d.length fails at run time with a NoSuchMethodError.",
            "A value from jsonDecode is dynamic (or Object?): check its type before relying on it.",
            "Prefer a real type or Object?; dynamic hides mistakes the compiler would catch.",
        ),
        example="""
            dynamic d = 'hi';
            print(d.length);
            d = 5;
            try {
              print(d.length);
            } on NoSuchMethodError {
              print('no length on an int');
            }
        """,
        out="2\nno length on an int",
    ),
    # ── The basic types ─────────────────────────────────────────────────
    *dart(
        "type",
        "Type",
        "What kind of value something is: int, double, String, bool, List... Dart checks types before the program runs.",
        see=("class", "var", "type-check"),
        priority=35,
        aka=("types", "data type", "static type", "data types"),
        rules=(
            "Every value has a type, and a variable's type limits what can be stored in it.",
            "x.runtimeType tells you the type a value really has.",
            "Types can carry other types in <>: List<int> is a list of ints, Map<String, int> maps text to ints.",
        ),
        example="""
            print(3.runtimeType);
            print('3'.runtimeType);
            print(3.0.runtimeType);
            print(true.runtimeType);
            print([3].runtimeType);
        """,
        out="int\nString\ndouble\nbool\nList<int>",
    ),
    *dart(
        "integer",
        "int (integer)",
        "The type for whole numbers, with no decimal point: -3, 0, 42.",
        see=("float", "division", "num"),
        priority=35,
        aka=("int", "ints", "integers", "whole number"),
        detect=(r"\bint\b",),
        rules=(
            "int / int always gives a double: 7 / 2 is 3.5. Use ~/ (7 ~/ 2 is 3) for a whole-number answer.",
            "On the Dart VM an int is 64 bits: 9223372036854775807 + 1 wraps around to a huge negative number.",
            "An int literal can fill a double variable (double d = 3; holds 3.0), but a double never fits an int variable.",
        ),
        example="""
            int a = 7;
            print(a / 2);
            print(a ~/ 2);
            print(a % 2);
            double d = 3;
            print(d);
        """,
        out="3.5\n3\n1\n3.0",
    ),
    *dart(
        "float",
        "double (floating point)",
        "The type for numbers with a decimal point, like 2.5. Dart has just one kind, double (no separate float).",
        see=("integer", "float-precision", "num"),
        priority=35,
        aka=("double", "doubles", "floating point", "floating-point", "decimal"),
        detect=(r"\bdouble\b",),
        rules=(
            "A whole double still prints with .0: 4 / 2 is 2.0.",
            "Doubles are approximate: 0.1 + 0.2 is 0.30000000000000004.",
            "Dividing by zero does not throw: 1 / 0 is Infinity, and 0 / 0 is NaN.",
        ),
        example="""
            print(0.1 + 0.2);
            print(4 / 2);
            print(1 / 0);
            print(2.5.toInt());
        """,
        out="0.30000000000000004\n2.0\nInfinity\n2",
    ),
    *dart(
        "float-precision",
        "Floating-point precision",
        "Doubles store most decimals only approximately, so results can be a hair off. Never compare two computed doubles "
        "with ==; round for display with toStringAsFixed.",
        see=("float", "rounding", "comparison"),
        priority=45,
        aka=("precision", "rounding error", "decimal places", "tostringasfixed", "epsilon"),
        detect=(r"\btoStringAsFixed\b|\btoStringAsPrecision\b",),
        rules=(
            "0.1 + 0.2 == 0.3 is false.",
            "x.toStringAsFixed(2) gives TEXT with exactly 2 decimals, rounded: 3.14159.toStringAsFixed(2) is '3.14'.",
            "To compare, check the difference is tiny: (a - b).abs() < 1e-9.",
        ),
        example="""
            print(0.1 + 0.2 == 0.3);
            print((0.1 + 0.2 - 0.3).abs() < 1e-9);
            print(3.14159.toStringAsFixed(2));
            print(2.5.toStringAsFixed(0));
        """,
        out="false\ntrue\n3.14\n3",
    ),
    *dart(
        "num",
        "num",
        "The type that is either an int or a double. Use it when a number of either kind will do.",
        see=("integer", "float", "type"),
        priority=35,
        aka=("number", "numbers", "numeric"),
        detect=(r"\bnum\b",),
        rules=(
            "num n = 3; n = 2.5; is fine. n is int and n is double tell which it holds.",
            "Both kinds share the num methods: abs(), round(), toInt(), toDouble(), compareTo().",
            "int x = 2.5; does not compile: a num or double cannot go into an int variable.",
        ),
        example="""
            num n = 3;
            print(n);
            n = 2.5;
            print(n);
            print(n is double);
        """,
        out="3\n2.5\ntrue",
    ),
    *dart(
        "boolean",
        "bool (boolean)",
        "A yes-or-no value: true or false. Dart conditions must be a real bool; it has no truthy or falsy values.",
        see=("condition", "short-circuit", "comparison"),
        priority=30,
        aka=("bool", "booleans", "truthy", "falsy", "truthiness", "true", "false"),
        detect=(r"\bbool\b",),
        rules=(
            "if (1), if ('') and if (list) do not compile: write if (n != 0), if (s.isNotEmpty).",
            "Combine with && (and), || (or) and ! (not). && and || stop as soon as the answer is known.",
            "A bool cannot be null unless it is bool?.",
        ),
        example="""
            int n = 0;
            print(n == 0);
            print(!(n > 1));
            print(n == 0 && n < 5);
        """,
        out="true\ntrue\ntrue",
    ),
    *dart(
        "string",
        "String",
        "Text: a sequence of characters in quotes, 'like this' or \"like this\". A String cannot be changed; every method gives a new one.",
        see=("character", "string-interpolation", "string-comparison"),
        priority=30,
        aka=("strings", "str", "string literal"),
        detect=(r"\bString\b",),
        rules=(
            "Single and double quotes are the same; use the other kind inside, or a backslash: 'it\\'s'.",
            "s[0] reads a character (as a String); s[0] = 'x' does not compile.",
            "== compares the text itself: 'a' + 'b' == 'ab' is true.",
            "length counts UTF-16 code units, so an emoji can count as 2.",
        ),
        example="""
            String s = 'Dart';
            print(s.length);
            print(s[0]);
            print(s.toUpperCase());
            print(s == 'Da' + 'rt');
        """,
        out="4\nD\nDART\ntrue",
    ),
    *dart(
        "character",
        "Character",
        "One letter, digit or symbol. Dart has no separate char type: a character is a String of length 1.",
        see=("string", "letter-case", "string-comparison"),
        priority=35,
        aka=("char", "characters", "code unit", "rune", "runes", "code point", "ascii"),
        rules=(
            "s[i] is a String of length 1, so 'a' + 'b' joins them (it does not add numbers).",
            "'A'.codeUnitAt(0) is 65, the number behind the letter; String.fromCharCode(65) turns it back into 'A'.",
            "'😀'.length is 2 (two code units) but '😀'.runes.length is 1: one character can take several code units.",
        ),
        example="""
            print('A'.codeUnitAt(0));
            print(String.fromCharCode(66));
            print('a' + 'b');
            print('😀'.length);
            print('😀'.runes.length);
        """,
        out="65\nB\nab\n2\n1",
    ),
    *dart(
        "list",
        "List",
        "An ordered collection written in square brackets: [3, 1, 2]. Items are numbered from 0.",
        see=("index", "set", "dictionary", "spread"),
        priority=40,
        aka=("lists", "array", "arrays", "list literal", "growable list", "fixed-length list"),
        detect=(r"\bList\b", r"=\s*\["),
        rules=(
            "A list literal is growable: add, insert, remove and sort all work.",
            "List.filled(3, 0) makes a fixed-length list: its items can change but add throws.",
            "Reading outside the list (xs[9] with 3 items) throws a RangeError.",
            "print(list) shows [1, 2, 3], with commas.",
        ),
        example="""
            var nums = [3, 1, 2];
            nums.add(4);
            nums.sort();
            print(nums);
            print(nums.length);
        """,
        out="[1, 2, 3, 4]\n4",
    ),
    *dart(
        "set",
        "Set",
        "A collection with no duplicates, written in curly brackets: {1, 2, 3}. Adding an item it already has does nothing.",
        see=("list", "dictionary", "iterable"),
        priority=45,
        aka=("sets", "hashset", "set literal", "unique", "union", "intersection"),
        detect=(r"\bSet\b|\{\s*\d+\s*,\s*\d+", r"\.(?:union|intersection|difference)\("),
        rules=(
            "{} on its own is an empty Map, not a Set: write <int>{} or Set<int>().",
            "add returns false when the item was already there. Items stay in the order they were added.",
            "a.union(b), a.intersection(b) and a.difference(b) give new sets.",
        ),
        example="""
            var s = {3, 1, 3};
            print(s);
            print(s.add(1));
            print({1, 2}.intersection({2, 3}));
            print({} is Map);
        """,
        out="{3, 1}\nfalse\n{2}\ntrue",
    ),
    *dart(
        "dictionary",
        "Map (dictionary)",
        "A collection of key-value pairs, written {'a': 1, 'b': 2}. You look a value up by its key.",
        see=("key", "value", "list", "set"),
        priority=40,
        aka=("map type", "maps", "hash map", "hashmap", "dict", "dictionaries", "key-value", "map literal", "Map<K, V>"),
        detect=(r"\bMap\b", r"\{\s*['\"]\w*['\"]\s*:"),
        rules=(
            "Keys are unique; assigning to an existing key replaces its value.",
            "m['x'] for a missing key gives null, so the result type is nullable (V?).",
            "A Map remembers the order its keys were added, and prints as {a: 1, b: 2}.",
            "Loop with m.entries (e.key, e.value), m.keys or m.values.",
        ),
        example="""
            var ages = {'ann': 30, 'bo': 25};
            ages['cy'] = 41;
            print(ages['bo']);
            print(ages['zed']);
            print(ages);
        """,
        out="25\nnull\n{ann: 30, bo: 25, cy: 41}",
    ),
    *dart(
        "key",
        "Key",
        "The label you look an item up by in a Map. Each key appears once and has one value.",
        see=("dictionary", "value", "index"),
        priority=25,
        aka=("keys", "map key", "containskey"),
        rules=(
            "m.containsKey('a') says whether a key is there; m.keys lists them all.",
            "Keys are compared with ==, so 'a' written twice is one key.",
            "m.remove('a') deletes the key and its value.",
        ),
        example="""
            var m = {'a': 1, 'b': 2};
            print(m.containsKey('a'));
            print(m.keys);
            m.remove('a');
            print(m);
        """,
        out="true\n(a, b)\n{b: 2}",
    ),
    *dart(
        "value",
        "Value",
        "The actual data a variable holds or an expression works out to: 5, 'hi', [1, 2] or null.",
        see=("variable", "key", "type"),
        priority=25,
        aka=("values", "map value", "data"),
        rules=(
            "Every expression has a value; a variable's value is whatever was last stored in it.",
            "In a Map, m.values lists the values only.",
            "Numbers, strings and bools are compared by value with ==; most other objects need == written for them.",
        ),
        example="""
            var m = {'a': 1, 'b': 2};
            print(m.values);
            print(m.values.reduce((a, b) => a + b));
        """,
        out="(1, 2)\n3",
    ),
    *dart(
        "record",
        "Record",
        "A small fixed bundle of values written in round brackets: (1, 'a'), or with names: (x: 3, y: 4). New in Dart 3.",
        see=("pattern", "destructuring", "immutable"),
        priority=60,
        aka=("records", "tuple", "tuples", "named record", "record type"),
        detect=(r"\.\$[1-9]\b", r"\bRecord\b", r"^\s*\(\s*[A-Za-z]\w*\??\s*,[^()\n]*\)\s+\w+\s*[=;]"),
        rules=(
            "Positional fields are read with $1, $2... (counting from 1): pair.$1. Named ones by name: p.x.",
            "A record cannot be changed after it is made.",
            "Records are equal when their fields are: (1, 2) == (1, 2) is true.",
            "Return a record to hand back several values at once.",
        ),
        example="""
            (int, String) pair = (1, 'a');
            print(pair.$1);
            print(pair);
            print((1, 2) == (1, 2));
            var p = (x: 3, y: 4);
            print(p.x + p.y);
        """,
        out="1\n(1, a)\ntrue\n7",
    ),
    *dart(
        "enum",
        "enum",
        "A type with a fixed list of named values, such as Color.red, Color.green, Color.blue.",
        see=("switch", "class", "sealed-class"),
        priority=65,
        aka=("enums", "enumeration", "enumerated type", "enhanced enum"),
        detect=(r"^\s*enum\s+\w+",),
        rules=(
            "Color.values lists them all, in the order written.",
            "Each value has .index (counting from 0) and .name.",
            "A switch over an enum must handle every value (or have a default), or it does not compile.",
            "Enums may have fields, constructors and methods.",
        ),
        example="""
            enum Color { red, green, blue }
            void main() {
              print(Color.green.index);
              print(Color.blue.name);
              print(Color.values);
            }
        """,
        out="1\nblue\n[Color.red, Color.green, Color.blue]",
    ),
    *dart(
        "typedef",
        "typedef",
        "Gives a name to a type, most often a function type, so a long signature is written once.",
        see=("higher-order-function", "type", "function"),
        priority=70,
        aka=("type alias", "type aliases"),
        detect=(r"^\s*typedef\b",),
        rules=(
            "typedef Op = int Function(int, int); names 'a function taking two ints and returning an int'.",
            "It does not make a new type: it is another name for the same one.",
            "Function types are written ReturnType Function(ParamTypes).",
        ),
        example="""
            typedef Op = int Function(int, int);
            int apply(Op f, int a, int b) => f(a, b);
            void main() {
              print(apply((a, b) => a + b, 2, 3));
            }
        """,
        out="5",
    ),
    *dart(
        "type-conversion",
        "Type conversion",
        "Turning a value into another type, such as text into a number. Dart never does it silently: you ask for it.",
        see=("integer", "string", "format-exception"),
        priority=45,
        aka=("type conversion", "casting", "type coercion", "convert", "parse", "int.parse", "tryparse"),
        detect=(r"\b(?:int|double|num)\.(?:parse|tryParse)\(", r"\.(?:toInt|toDouble|toString)\(\)"),
        rules=(
            "int.parse('42') is 42; with text that is not a number it throws a FormatException.",
            "int.tryParse('x') gives null instead of throwing.",
            "n.toString() and '$n' make text; 3.7.toInt() is 3 (cuts the decimals).",
            "'5' + 1 does not compile: Dart will not guess.",
        ),
        example="""
            print(int.parse('42') + 1);
            print(int.tryParse('x'));
            print(double.parse('2.5') * 2);
            print(7.toString() + '!');
        """,
        out="43\nnull\n5.0\n7!",
    ),
    *dart(
        "rounding",
        "Rounding",
        "Turning a number with decimals into a whole one: round() goes to the nearest, floor() down, ceil() up, truncate() "
        "just cuts the decimals off.",
        see=("float", "division", "truncating-division"),
        priority=40,
        aka=("round", "floor", "ceil", "truncate", "truncation", "ceiling", "roundtoint"),
        detect=(r"\.(?:round|floor|ceil|truncate)\(\)",),
        rules=(
            "round() sends halves away from zero: 2.5.round() is 3 and (-2.5).round() is -3.",
            "floor() goes toward minus infinity, ceil() toward plus: (-2.5).floor() is -3, (-2.5).ceil() is -2.",
            "truncate() goes toward zero: (-2.5).truncate() is -2.",
            "They give an int; use roundToDouble() for a double.",
        ),
        example="""
            print(2.5.round());
            print((-2.5).round());
            print((-2.5).floor());
            print((-2.5).ceil());
            print((-2.5).truncate());
        """,
        out="3\n-3\n-3\n-2\n-2",
    ),
    *dart(
        "division",
        "Division",
        "Dart has two: / always gives a double (7 / 2 is 3.5), and ~/ gives a whole number (7 ~/ 2 is 3).",
        see=("truncating-division", "modulo", "float"),
        priority=40,
        aka=("divide", "divided", "quotient"),
        detect=(r"[\w)\]]\s*/\s*[\w(]",),
        rules=(
            "8 / 2 is 4.0, not 4: the result of / is always a double.",
            "7 ~/ 2 is 3; the remainder is 7 % 2, which is 1.",
            "Dividing a double by zero gives Infinity or NaN; a whole-number division with ~/ by zero throws an error.",
        ),
        example="""
            print(8 / 2);
            print(7 / 2);
            print(7 ~/ 2);
            print(7 % 2);
        """,
        out="4.0\n3.5\n3\n1",
    ),
    *dart(
        "truncating-division",
        "Truncating division (~/)",
        "a ~/ b divides and drops everything after the decimal point, giving an int.",
        see=("division", "modulo", "rounding"),
        priority=80,
        aka=("~/", "integer division", "floor division", "floor-division", "whole division"),
        detect=(r"~/",),
        rules=(
            "It cuts toward zero, not downward: -7 ~/ 2 is -3 (floor division would give -4).",
            "It is the same as (a / b).truncate().",
            "Pair it with %: (a ~/ b) * b + a % b is a when both are positive.",
        ),
        example="""
            print(7 ~/ 2);
            print(-7 ~/ 2);
            print((-7 / 2).floor());
            print(7 / 2);
        """,
        out="3\n-3\n-4\n3.5",
    ),
    *dart(
        "modulo",
        "Modulo (%)",
        "a % b is what is left over after dividing a by b. In Dart the answer is never negative.",
        see=("division", "truncating-division", "integer"),
        priority=50,
        aka=("%", "remainder", "mod", "modulus", "remainder operator"),
        detect=(r"[\w)\]]\s*%\s*[\w(]",),
        rules=(
            "-7 % 3 is 2 (not -1 as in some languages): the result is always 0 or more.",
            "For the version that keeps the sign of the left number, use (-7).remainder(3), which is -1.",
            "x % 2 == 0 tests for even numbers; x.isEven does the same.",
        ),
        example="""
            print(7 % 3);
            print(-7 % 3);
            print((-7).remainder(3));
            print(7 % -3);
        """,
        out="1\n2\n-1\n1",
    ),
    *dart(
        "bitwise",
        "Bitwise operators",
        "Operators that work on the individual binary digits (bits) of whole numbers: & (and), | (or), ^ (xor), ~ (flip) "
        "and the shifts << and >>.",
        see=("integer", "operator", "modulo"),
        priority=50,
        aka=("bit", "bits", "bitmask", "bit shift", "shift", "mask", "binary", "xor", "&", "|", "^", "<<", ">>"),
        detect=(r"[\w)]\s*(?:<<|>>>?)\s*[\w(]", r"\w\s*[&|^]\s*(?:0x[0-9a-fA-F]+|\d+)\b"),
        rules=(
            "6 & 3 is 2 (binary 110 and 011 gives 010); 6 | 3 is 7; 6 ^ 3 is 5.",
            "1 << 3 is 8: shifting left by n multiplies by 2 to the n. 8 >> 1 is 4.",
            "&, | and ^ also work on bools, where they do not skip the right side the way && and || do.",
        ),
        example="""
            print(6 & 3);
            print(6 | 3);
            print(6 ^ 3);
            print(1 << 3);
            print(8 >> 1);
        """,
        out="2\n7\n5\n8\n4",
    ),
    *dart(
        "cascade",
        "Cascade (..)",
        "a..b() calls b on a but hands back a itself, so you can chain several steps on the same object.",
        see=("method", "null-aware-access", "string-buffer"),
        priority=75,
        aka=("..", "?..", "cascade operator", "cascade notation", "double dot"),
        detect=(r"(?<![.\d])\.\.(?![.\d])", r"\?\.\.(?!\.)"),
        rules=(
            "The value of a..b().c() is a, not the result of b() or c().",
            "?.. does the same but does nothing when a is null.",
            "Good for setting up an object in one expression: StringBuffer()..write('a')..write('b').",
        ),
        example="""
            var list = <int>[]
              ..add(3)
              ..add(1)
              ..sort();
            print(list);
            final sb = StringBuffer()..write('a')..write('b');
            print(sb);
        """,
        out="[1, 3]\nab",
    ),
    *dart(
        "spread",
        "Spread (...)",
        "Writing ... before a collection inside a list, set or map literal pours its items in, one by one.",
        see=("collection-if-for", "list", "destructuring"),
        priority=75,
        aka=("...", "...?", "spread operator", "null-aware spread", "spread-rest", "star-args", "concatenate lists"),
        detect=(r"\.\.\.\??",),
        rules=(
            "[0, ...a, 3] makes a new list holding 0, all of a, then 3.",
            "...? skips the collection when it is null: [...?maybe] is [] if maybe is null.",
            "Works in lists, sets and maps: {...a, 'y': 2}. It is a shallow copy: the items themselves are shared.",
        ),
        example="""
            var a = [1, 2];
            List<int>? none;
            var b = [0, ...a, ...?none, 3];
            print(b);
            print({...{'x': 1}, 'y': 2});
        """,
        out="[0, 1, 2, 3]\n{x: 1, y: 2}",
    ),
    *dart(
        "collection-if-for",
        "Collection if and for",
        "Inside a list, set or map literal you can write if (...) and for (...) to decide which items go in, or to make several.",
        see=("spread", "list", "condition"),
        priority=70,
        aka=("collection if", "collection for", "conditional element", "if in a list"),
        detect=(r"[\[,]\s*(?:if|for)\s*\(",),
        rules=(
            "[ if (admin) 'users' ] adds 'users' only when admin is true; add else to choose between two items.",
            "[ for (var i = 1; i <= 3; i++) i * 2 ] adds one item per turn of the loop.",
            "They work in sets and maps too, and inside each other.",
        ),
        example="""
            var admin = false;
            var menu = [
              'home',
              if (admin) 'users' else 'help',
              for (var i = 1; i <= 2; i++) 'item$i',
            ];
            print(menu);
        """,
        out="[home, help, item1, item2]",
    ),
    *dart(
        "ternary",
        "Conditional expression (?:)",
        "condition ? a : b gives a when the condition is true and b when it is false.",
        see=("condition", "null-coalescing", "branch"),
        priority=45,
        aka=("ternary", "?:", "ternary operator", "conditional operator", "inline if", "if expression"),
        detect=(r"[\w)\]]\s*\?\s+[^?:\n]+\s:\s",),
        rules=(
            "It is an expression, so it can sit inside print(...) or a return.",
            "The condition must be a bool.",
            "For null, a ?? b is shorter than a != null ? a : b.",
        ),
        example="""
            int n = 7;
            print(n.isEven ? 'even' : 'odd');
            print(n > 5 ? 'big' : 'small');
        """,
        out="odd\nbig",
    ),
    *dart(
        "type-check",
        "Type test (is) and cast (as)",
        "x is T asks whether x is a T. x as T demands that it is, and throws an error if not.",
        see=("type-promotion", "type", "dynamic"),
        priority=60,
        aka=("is", "is!", "as", "isinstance", "instanceof", "type test", "type cast", "cast", "type check", "typeof", "runtimetype"),
        detect=(r"\bis\s*!?\s+[A-Z]\w*", r"\bas\s+[A-Z]\w*\??"),
        rules=(
            "x is! T is true when x is not a T.",
            "A subtype counts: 3 is num is true, and every value except null is an Object.",
            "After if (x is String), Dart lets you use x as a String inside the branch (type promotion).",
            "A failing as throws a TypeError, so test with is first when unsure.",
        ),
        example="""
            Object o = 3;
            print(o is int);
            print(o is! String);
            print(o is num);
            try {
              print((o as String).length);
            } catch (e) {
              print('bad cast');
            }
        """,
        out="true\ntrue\ntrue\nbad cast",
    ),
    # ── Functions ───────────────────────────────────────────────────────
    *dart(
        "function",
        "Function",
        "A named piece of code you can run again and again, with inputs (parameters) and an answer it gives back.",
        see=("parameter", "return", "arrow-function"),
        priority=35,
        aka=("functions", "func", "procedure", "subroutine", "call", "function call"),
        rules=(
            "The return type comes first: int twice(int n) { return n * 2; }. void means 'gives back nothing'.",
            "If the body is one expression, => is a shorthand: int twice(int n) => n * 2;",
            "Functions are values: you can store one in a variable or pass it to another function.",
            "Every Dart program starts by running main().",
        ),
        example="""
            int twice(int n) => n * 2;
            void hello() {
              print('hi');
            }
            hello();
            print(twice(4));
        """,
        out="hi\n8",
    ),
    *dart(
        "parameter",
        "Parameter",
        "A name in a function's definition that stands for a value the caller will supply.",
        see=("argument", "named-parameter", "optional-positional-parameter"),
        priority=35,
        aka=("parameters", "param", "params", "formal parameter", "positional parameter", "positional"),
        rules=(
            "Plain parameters are positional and required: the first argument goes to the first parameter.",
            "Put some in { } to make them named, or in [ ] to make them optional.",
            "A parameter's type is written before its name: int n.",
        ),
        example="""
            String label(String name, int age) => '$name is $age';
            print(label('Ann', 30));
        """,
        out="Ann is 30",
    ),
    *dart(
        "argument",
        "Argument",
        "The actual value you give a function when you call it. In label('Ann', 30) the arguments are 'Ann' and 30.",
        see=("parameter", "named-parameter", "function"),
        priority=30,
        aka=("arguments", "args", "actual argument"),
        rules=(
            "Too few or too many positional arguments is an error before the program runs.",
            "A named argument is written name: value, e.g. greet(name: 'Ann').",
            "Arguments are worked out first, then the function runs.",
        ),
        example="""
            int add(int a, int b) => a + b;
            print(add(2, 3));
            print(add(add(1, 2), 4));
        """,
        out="5\n7",
    ),
    *dart(
        "named-parameter",
        "Named parameter",
        "A parameter written inside { } in the definition. The caller gives it by name, in any order, and may leave it out unless it is required.",
        see=("required", "default-parameter", "optional-positional-parameter"),
        priority=60,
        aka=("named parameters", "named argument", "named arguments", "keyword argument", "keyword-argument", "keyword arguments", "options-object", "options object", "by name"),
        detect=(r"\(\s*(?:[^(){}\n]*,\s*)?\{[^(){}\n]*\}\s*\)",),
        rules=(
            "String greet({String greeting = 'Hello', required String name}) is called greet(name: 'Ann').",
            "Order does not matter: greet(name: 'Bo', greeting: 'Hi') works.",
            "A named parameter that is not required needs a default value or a nullable type.",
            "By convention, the positional arguments are written first and the named ones after.",
        ),
        example="""
            String greet({required String name, String greeting = 'Hello'}) => '$greeting, $name';
            print(greet(name: 'Ann'));
            print(greet(greeting: 'Hi', name: 'Bo'));
        """,
        out="Hello, Ann\nHi, Bo",
    ),
    *dart(
        "required",
        "required",
        "Marks a named parameter that the caller must give. Leaving it out is a compile error.",
        see=("named-parameter", "default-parameter", "nullable-type"),
        priority=70,
        aka=("required parameter", "required named parameter", "required keyword"),
        detect=(r"\brequired\b",),
        rules=(
            "required lets a named parameter have a non-nullable type and no default.",
            "It is used a lot in constructors: Point({required this.x, required this.y}).",
            "required is only for named parameters; positional ones are already required.",
        ),
        example="""
            class P {
              final String name;
              final int age;
              P({required this.name, this.age = 0});
            }
            void main() {
              var p = P(name: 'Ann');
              print('${p.name} ${p.age}');
            }
        """,
        out="Ann 0",
    ),
    *dart(
        "optional-positional-parameter",
        "Optional positional parameter ([ ])",
        "A parameter written inside [ ] in the definition. The caller may leave out these arguments, from the right.",
        see=("parameter", "named-parameter", "default-parameter"),
        priority=60,
        aka=("optional parameter", "optional parameters", "optional argument", "positional optional", "square bracket parameter"),
        detect=(r"\(\s*(?:[^()\[\]\n]*,\s*)?\[[^()\[\]\n]*\]\s*\)",),
        rules=(
            "String f(String a, [String b = '-']) can be called f('x') or f('x', 'y').",
            "Each needs a default value or a nullable type.",
            "You cannot mix [ ] and { } in one parameter list.",
        ),
        example="""
            String f(String a, [String b = '-']) => a + b;
            print(f('x'));
            print(f('x', 'y'));
        """,
        out="x-\nxy",
    ),
    *dart(
        "default-parameter",
        "Default parameter",
        "A named or optional parameter that already has a value, used when the caller leaves it out. It is written = value.",
        see=("named-parameter", "optional-positional-parameter", "default-value"),
        priority=45,
        aka=("default argument", "default parameters", "default arguments", "parameter default"),
        rules=(
            "void f({int n = 1}) and void f([int n = 1]) both give n the value 1 when it is left out.",
            "The default must be a compile-time constant: = const [] is allowed, = [] is not.",
            "The default is the same constant every call, so there is no 'shared mutable default' trap as in Python.",
            "A plain required positional parameter cannot have a default.",
        ),
        example="""
            int power(int base, [int exp = 2]) {
              var r = 1;
              for (var i = 0; i < exp; i++) {
                r *= base;
              }
              return r;
            }
            print(power(3));
            print(power(2, 5));
        """,
        out="9\n32",
    ),
    *dart(
        "default-value",
        "Default value",
        "A value used when nothing better is available: a parameter left out, or a variable or Map entry that is null.",
        see=("null-coalescing", "default-parameter", "null-aware-assignment"),
        priority=40,
        aka=("fallback", "default", "defaults", "orelse", "putifabsent"),
        rules=(
            "For null: value ?? fallback.",
            "For a Map entry: m[k] ?? 0, or m.putIfAbsent(k, () => 0) which also stores it.",
            "For a parameter: = value in the parameter list.",
        ),
        example="""
            var counts = <String, int>{'a': 2};
            print(counts['a'] ?? 0);
            print(counts['z'] ?? 0);
            counts['z'] = (counts['z'] ?? 0) + 1;
            print(counts);
        """,
        out="2\n0\n{a: 2, z: 1}",
    ),
    *dart(
        "arrow-function",
        "Arrow function (=>)",
        "=> is a shorthand for a function whose body is one expression: the value of the expression is returned.",
        see=("anonymous-function", "function", "switch-expression"),
        priority=55,
        aka=("=>", "fat arrow", "arrow", "arrow syntax", "expression body"),
        detect=(r"=>",),
        rules=(
            "int sq(int n) => n * n; means the same as int sq(int n) { return n * n; }",
            "Only a single expression fits: no statements such as if or for (use { } for those).",
            "The same arrow is used inside switch expressions to separate a pattern from its result.",
        ),
        example="""
            int square(int n) => n * n;
            var twice = (int n) => n * 2;
            print(square(4));
            print(twice(4));
        """,
        out="16\n8",
    ),
    *dart(
        "anonymous-function",
        "Anonymous function (lambda)",
        "A function with no name, written right where it is used: (a, b) => a + b. It is often passed to another function.",
        see=("arrow-function", "higher-order-function", "closure"),
        priority=50,
        aka=("lambda", "lambdas", "function literal", "anonymous", "inline function", "unnamed function"),
        detect=(r"[=,(:]\s*(?:async\s*)?\([\w\s,<>?]*\)\s*(?:async\s*)?(?:=>|\{)",),
        rules=(
            "(x) => x * 2 and (x) { return x * 2; } are the same function.",
            "Parameter types are usually left out when Dart can work them out from where it is used.",
            "It can use variables from around it (a closure).",
        ),
        example="""
            var nums = [3, 1, 2];
            nums.sort((a, b) => b - a);
            print(nums);
            print(nums.map((n) => n * 10).toList());
        """,
        out="[3, 2, 1]\n[30, 20, 10]",
    ),
    *dart(
        "higher-order-function",
        "Higher-order function",
        "A function that takes another function as an argument, or gives one back. map, where, fold and sort(compare) are examples.",
        see=("anonymous-function", "callback", "closure"),
        priority=45,
        aka=("higher order function", "higher order", "function as argument", "function type", "first-class function", "first class function"),
        rules=(
            "The parameter's type is a function type: void Function(int) or int Function(int, int).",
            "xs.where(test), xs.map(change) and xs.fold(start, combine) all take a function.",
            "A function's name without brackets is the function itself: xs.forEach(print).",
        ),
        example="""
            int applyTwice(int Function(int) f, int x) => f(f(x));
            print(applyTwice((n) => n + 3, 1));
            [1, 2].forEach(print);
        """,
        out="7\n1\n2",
    ),
    *dart(
        "callback",
        "Callback",
        "A function you hand to other code so it can call it later, when something happens or when it needs a decision.",
        see=("higher-order-function", "anonymous-function", "future"),
        priority=40,
        aka=("callbacks", "handler", "event handler", "then callback", "completion handler"),
        rules=(
            "In Flutter, onPressed: () { ... } is a callback: it runs when the button is pressed, not when the line is read.",
            "future.then((v) { ... }) is a callback that runs when the future completes.",
            "A callback given to something asynchronous (a future, a timer, a button) runs later, so the code after that line runs first.",
        ),
        example="""
            void repeat(int n, void Function(int) action) {
              for (var i = 1; i <= n; i++) {
                action(i);
              }
            }
            repeat(3, (i) => print('turn $i'));
        """,
        out="turn 1\nturn 2\nturn 3",
    ),
    *dart(
        "return",
        "return",
        "Ends a function and hands a value back to whoever called it.",
        see=("function", "side-effect", "arrow-function"),
        priority=30,
        aka=("returns", "return value", "return type", "returning", "void"),
        detect=(r"\breturn\b",),
        rules=(
            "Nothing after return in that function runs.",
            "The function's declared type says what it returns; void means it returns nothing useful.",
            "A function with a non-void return type must return on every path, or it does not compile.",
            "Dart 3 records let a function return several values: return (a, b);",
        ),
        example="""
            int firstBig(List<int> xs) {
              for (final x in xs) {
                if (x > 10) return x;
              }
              return -1;
            }
            print(firstBig([3, 12, 40]));
            print(firstBig([1, 2]));
        """,
        out="12\n-1",
    ),
    *dart(
        "main-function",
        "main()",
        "The function a Dart program starts in. When you run a Dart file, main() is called first.",
        see=("function", "import", "future"),
        priority=35,
        aka=("main", "entry point", "program start", "void main"),
        detect=(r"\bmain\s*\(",),
        rules=(
            "void main() is the usual form. Future<void> main() async lets you use await at the top level of the program.",
            "main may take a List<String> args to read command-line words.",
            "A Flutter app also starts in main(), which calls runApp(...).",
        ),
        example="""
            void main() {
              print('start');
              helper();
            }
            void helper() => print('helper ran');
        """,
        out="start\nhelper ran",
    ),
]
