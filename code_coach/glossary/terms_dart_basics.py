"""Dart words, part 4: the everyday words of programming in their Dart form - expression, variable, scope, closure,
loops, conditions. They have the same ids as Python's and JavaScript's so a drill's `concepts` resolve in all three,
but every rule here is about Dart (checked by tests/test_glossary.py).

Examples with `main(` are whole programs; the others are the body of main (see terms_dart_core.py)."""

from __future__ import annotations

from .entry import Entry, dart

TERMS: list[Entry] = [
    *dart(
        "expression",
        "Expression",
        "A piece of code that works out to one value, such as 2 + 3, a variable's name, a method call or a ? : choice.",
        see=("statement", "operator", "evaluate"),
        priority=30,
        aka=("expr", "expressions"),
        rules=(
            "Every expression has exactly one value and one type.",
            "Expressions nest: in (2 + 3) * 4 the bracketed part is an expression inside a bigger one.",
            "if and switch statements are not expressions, but a ? : choice, a switch expression and a function call are.",
        ),
        example="""
            var x = 5;
            print(x * 2 + 1);
            print(x > 3 ? 'big' : 'small');
        """,
        out="11\nbig",
    ),
    *dart(
        "statement",
        "Statement",
        "One complete instruction ending in a semicolon or a block, such as a declaration, an if or a loop. It does something and need not produce a value.",
        see=("expression", "assignment", "control-flow"),
        priority=20,
        aka=("statements", "instruction"),
        rules=(
            "Statements run one after another, from the top, and most end with a semicolon.",
            "A call such as print(x); is an expression used as a statement.",
            "A statement cannot be used where a value is needed: you cannot write var y = (if (x) 1);",
        ),
        example="""
            var x = 5;
            if (x > 3) {
              print('big');
            }
        """,
        out="big",
    ),
    *dart(
        "evaluate",
        "Evaluate",
        "To work out the value of an expression step by step, brackets first, then operators in precedence order.",
        see=("expression", "precedence", "short-circuit"),
        priority=30,
        aka=("evaluation", "evaluates", "evaluated", "work out"),
        rules=(
            "Evaluating an expression always ends in one value.",
            "Names are replaced by their current values and a call by what it returns.",
            "Arguments are evaluated before the function runs; && and || may skip their right side.",
        ),
        example="""
            print(1 + 2 * 3);
        """,
        out="7",
    ),
    *dart(
        "operator",
        "Operator",
        "A symbol that does something to values: + adds, == compares, && combines two yes-or-no answers.",
        see=("precedence", "expression", "null-coalescing"),
        priority=30,
        aka=("operators", "operand", "arithmetic", "plus", "minus", "multiplication"),
        rules=(
            "Arithmetic: + - * / ~/ %. Comparison: == != < > <= >=. Logic: && || !.",
            "Dart also has: ?? ?. ?: .. ... as is, and the compound forms += -= *= ??=.",
            "Some work on more than numbers: 'a' + 'b' joins text, 'ab' * 3 repeats it, [1] + [2] joins lists.",
        ),
        example="""
            print(7 - 2);
            print('a' + 'b');
            print('ab' * 3);
            print([1] + [2]);
            print(7 > 2 && !false);
        """,
        out="5\nab\nababab\n[1, 2]\ntrue",
    ),
    *dart(
        "precedence",
        "Operator precedence",
        "The order the operators in one expression are done in. Higher precedence goes first, which is why 2 + 3 * 4 is 14, not 20.",
        see=("operator", "evaluate", "short-circuit"),
        priority=65,
        aka=("order of operations", "operator precedence", "pemdas", "bodmas", "associativity"),
        detect=(
            r"[\w)]\s*[-+]\s*[\w.()]+\s*(?:~/|[*/%])\s*[\w(]",
            r"[\w)]\s*(?:~/|[*/%])\s*[\w.()]+\s*[-+]\s*[\w(]",
            r"&&[^\n]*\|\||\|\|[^\n]*&&",
        ),
        rules=(
            "Brackets first. Then: postfix (a.b, a[i], a()), unary (! -x), * / ~/ %, + -, shifts, & ^ |, comparisons (< > <= >= is as), == !=, &&, ||, ??, ? :, and finally assignment.",
            "Operators on the same level go left to right: 8 - 3 - 2 is 3.",
            "&& goes before ||, so true || false && false is true.",
            "A minus sign applies after a method call: -2.abs() is -2, not 2. When unsure, add brackets.",
        ),
        example="""
            print(2 + 3 * 4);
            print((2 + 3) * 4);
            print(8 - 3 - 2);
            print(true || false && false);
            print(-2.abs());
        """,
        out="14\n20\n3\ntrue\n-2",
    ),
    *dart(
        "assignment",
        "Assignment",
        "Storing a value in a variable with =. The right side is worked out first, then stored.",
        see=("variable", "reassign", "operator"),
        priority=25,
        aka=("assign", "assigning", "assigned", "compound assignment", "+=", "-=", "++", "--", "increment", "decrement"),
        rules=(
            "x += 2 means x = x + 2; x++ adds 1. The same idea works for -=, *=, /=, ~/=, %= and ??=.",
            "An assignment is itself an expression whose value is the stored value: a = b = 0 sets both.",
            "A final or const variable can be assigned only once.",
        ),
        example="""
            var x = 4;
            x += 3;
            x *= 2;
            x++;
            print(x);
            var a = 1, b = 1;
            a = b = 7;
            print('$a $b');
        """,
        out="15\n7 7",
    ),
    *dart(
        "variable",
        "Variable",
        "A name that holds a value so you can use it again later. After var x = 5; the name x stands for 5.",
        see=("assignment", "var", "final", "scope"),
        priority=30,
        aka=("variables", "name", "identifier", "declaration", "declare", "initialize", "naming"),
        detect=(r"^\s*(?:var|final|const|late|int|double|num|bool|String)\s+[a-z_]\w*\s*[=;]",),
        rules=(
            "Declare it before use, with var, final, const or a type: int count = 0;. Using a name that was never declared does not compile.",
            "Names use letters, digits, _ and $, cannot start with a digit, and are case-sensitive (total and Total differ).",
            "Style: lowerCamelCase for variables (userName), UpperCamelCase for types.",
            "A variable that is not nullable must be given a value before it is read.",
        ),
        example="""
            var score = 10;
            score = score + 5;
            int bonus = 2;
            print(score * bonus);
        """,
        out="30",
    ),
    *dart(
        "reassign",
        "Reassign",
        "Giving an existing variable a new value. The old value is lost, unless the variable is final or const, which forbids it.",
        see=("assignment", "final", "variable"),
        priority=30,
        aka=("reassignment", "reassigned", "reassigning", "overwrite", "update a variable", "change a variable"),
        rules=(
            "var n = 1; n = 2; is fine; final n = 1; n = 2; does not compile.",
            "The new value must fit the variable's type: var n = 1; n = 'a'; does not compile.",
            "Reassigning a variable does not change objects other variables still point at.",
        ),
        example="""
            var n = 1;
            var m = n;
            n = 99;
            print('$n $m');
        """,
        out="99 1",
    ),
    *dart(
        "mutable",
        "Mutable",
        "Able to be changed after it is made. Lists, Maps, Sets and ordinary objects with non-final fields are mutable.",
        see=("immutable", "identity", "final"),
        priority=35,
        aka=("mutability", "mutate", "mutation", "modify", "in place", "in-place", "change in place"),
        rules=(
            "xs.add(3), xs[0] = 9 and map[k] = v change the collection itself.",
            "Two names for one list see each other's changes (see identity).",
            "final does not make a list unchangeable; it only stops the variable being pointed elsewhere.",
        ),
        example="""
            var a = [1, 2];
            var b = a;
            b.add(3);
            a[0] = 9;
            print(a);
            print(b);
        """,
        out="[9, 2, 3]\n[9, 2, 3]",
    ),
    *dart(
        "immutable",
        "Immutable",
        "Cannot be changed once made. Strings, numbers, bools, records and const or unmodifiable collections are immutable.",
        see=("mutable", "const", "final"),
        priority=35,
        aka=("immutability", "unmodifiable", "read-only", "readonly", "frozen", "cannot be changed"),
        rules=(
            "String methods give back new strings: s.toUpperCase() leaves s alone; s[0] = 'x' does not compile.",
            "List.unmodifiable(xs) and const [1, 2] throw an UnsupportedError if you try to add or change.",
            "Records and final fields cannot be reassigned. Make a changed copy instead.",
        ),
        example="""
            var s = 'abc';
            var t = s.toUpperCase();
            print(s);
            print(t);
            var xs = List.unmodifiable([1, 2]);
            try {
              xs.add(3);
            } catch (e) {
              print('cannot change');
            }
        """,
        out="abc\nABC\ncannot change",
    ),
    *dart(
        "scope",
        "Scope",
        "The part of the code where a name can be used. A variable declared inside { } exists only until the closing brace.",
        see=("variable", "closure", "reassign"),
        priority=40,
        aka=("scoping", "block scope", "local variable", "local", "global variable", "global", "top-level", "top level", "shadowing", "shadow", "lexical scope", "visibility of a variable"),
        rules=(
            "A name is visible in its block and every block inside it, and nowhere outside.",
            "A top-level variable (outside every function) can be used in the whole file.",
            "An inner name can hide an outer one with the same name (shadowing); the outer one is back after the block.",
            "Using a local name before its declaration is a compile error.",
        ),
        example="""
            var x = 'outer';
            {
              var x = 'inner';
              print(x);
            }
            print(x);
        """,
        out="inner\nouter",
    ),
    *dart(
        "closure",
        "Closure",
        "A function that remembers the variables around the place where it was created, and keeps using them after that code has finished.",
        see=("scope", "anonymous-function", "callback"),
        priority=50,
        aka=("closures", "captured variable", "capture", "enclosing", "nonlocal", "lexical closure"),
        rules=(
            "It captures the variable itself, not a copy: later changes are seen.",
            "Each call of the maker builds its own variables, so two counters do not interfere.",
            "In for (var i = 0; ...) each pass has its own i, so functions made in a loop each remember their own number.",
        ),
        example="""
            int Function() makeCounter() {
              var n = 0;
              return () => ++n;
            }
            var a = makeCounter();
            var b = makeCounter();
            print('${a()} ${a()} ${b()}');
            var fns = <int Function()>[];
            for (var i = 0; i < 3; i++) {
              fns.add(() => i);
            }
            print(fns.map((f) => f()).toList());
        """,
        out="1 2 1\n[0, 1, 2]",
    ),
    *dart(
        "recursion",
        "Recursion",
        "A function that calls itself on a smaller version of the problem, until it reaches a case simple enough to answer directly (the base case).",
        see=("call-stack", "function", "return"),
        priority=45,
        aka=("recursive", "recurse", "base case", "recursive function", "recursive call", "fibonacci", "factorial"),
        rules=(
            "Every recursive function needs a base case that returns without calling itself again.",
            "Each call waits for the one below it: the calls pile up on the call stack.",
            "Dart has no tail-call optimisation, so a call that never reaches its base case ends with a StackOverflowError.",
        ),
        example="""
            int factorial(int n) => n <= 1 ? 1 : n * factorial(n - 1);
            int fib(int n) => n < 2 ? n : fib(n - 1) + fib(n - 2);
            print(factorial(5));
            print(fib(10));
        """,
        out="120\n55",
    ),
    *dart(
        "call-stack",
        "Call stack",
        "The pile of function calls that are in progress. A new call goes on top; when it returns, it comes off and the one below carries on.",
        see=("recursion", "stack-trace", "function"),
        priority=40,
        aka=("callstack", "stack frame", "stack overflow", "stackoverflow", "calls", "function calls", "stack of calls", "call order"),
        rules=(
            "The innermost call finishes first: the last function called is the first to return.",
            "A stack trace prints this pile when an error happens.",
            "Too many nested calls throw a StackOverflowError (an Error, not an Exception).",
        ),
        example="""
            void b() {
              print('b runs');
            }
            void a() {
              print('a start');
              b();
              print('a end');
            }
            a();
        """,
        out="a start\nb runs\na end",
    ),
    *dart(
        "side-effect",
        "Side effect",
        "Anything a function does besides giving back a value: printing, changing a list it was given, changing a variable outside itself.",
        see=("function", "return", "mutable"),
        priority=45,
        aka=("side effects", "pure function", "impure", "pure", "mutation of arguments"),
        rules=(
            "A function with no side effects and the same answer for the same arguments is called pure.",
            "Changing a list or map you were passed (xs.add(x)) is a side effect the caller can see.",
            "A side effect only happens if the code runs: false && f() never calls f.",
            "Lazy results (map, where) run their callbacks late, so their side effects happen late.",
        ),
        example="""
            var log = <String>[];
            int add(int a, int b) {
              log.add('called');
              return a + b;
            }
            print(add(1, 2));
            print(log);
        """,
        out="3\n[called]",
    ),
    *dart(
        "control-flow",
        "Control flow",
        "The order in which statements run. if, switch, loops, break, continue, return and throw choose or change that order.",
        see=("condition", "loop", "async-await"),
        priority=35,
        aka=("flow", "order", "program flow", "flow of control", "execution flow", "branching", "jump"),
        rules=(
            "By default code runs top to bottom.",
            "return leaves the function, break leaves the loop, continue skips to the next pass, throw jumps to a catch.",
            "await pauses just that function, so async code does not always run in the order it is written.",
        ),
        example="""
            for (var i = 1; i <= 4; i++) {
              if (i.isOdd) continue;
              if (i > 3) break;
              print(i);
            }
            print('end');
        """,
        out="2\nend",
    ),
    *dart(
        "condition",
        "Condition (if / else)",
        "A yes-or-no test that decides what runs. if (test) { ... } else { ... } runs the first block only when test is true.",
        see=("boolean", "branch", "ternary", "comparison"),
        priority=35,
        aka=("conditional", "conditions", "if", "else", "else if", "if else", "if statement", "conditional statement", "test"),
        detect=(r"\bif\s*\(",),
        rules=(
            "The test must be a real bool: if (list) or if (count) does not compile. Write if (list.isNotEmpty).",
            "Chain with else if; only the first true branch runs.",
            "Braces are optional for a single statement, but recommended.",
        ),
        example="""
            var n = 15;
            if (n % 15 == 0) {
              print('fizzbuzz');
            } else if (n % 3 == 0) {
              print('fizz');
            } else {
              print(n);
            }
        """,
        out="fizzbuzz",
    ),
    *dart(
        "branch",
        "Branch",
        "One of the separate paths code can take at a decision: the if part, the else part, or one case of a switch.",
        see=("condition", "switch", "control-flow"),
        priority=30,
        aka=("branches", "path", "case branch", "code path", "if branch"),
        rules=(
            "Only one branch of an if / else chain runs.",
            "A branch that never runs (because its test is never true) is dead code.",
            "A function that returns a value must return on every branch.",
        ),
        example="""
            String kind(int n) {
              if (n < 0) return 'negative';
              if (n == 0) return 'zero';
              return 'positive';
            }
            print(kind(-3));
            print(kind(0));
            print(kind(8));
        """,
        out="negative\nzero\npositive",
    ),
    *dart(
        "short-circuit",
        "Short-circuit evaluation",
        "&&, || and ?? stop as soon as the answer is known, so the right side may never run.",
        see=("boolean", "null-coalescing", "side-effect"),
        priority=45,
        aka=("short circuit", "short-circuiting", "lazy evaluation of operators", "skip the right side", "guard"),
        rules=(
            "a && b: if a is false, b is not evaluated. a || b: if a is true, b is not evaluated.",
            "a ?? b and a?.b also skip their right part when a decides it.",
            "Use it to guard: x != null && x.isEven only reads x if it is there.",
        ),
        example="""
            bool yes() {
              print('yes ran');
              return true;
            }
            bool no() {
              print('no ran');
              return false;
            }
            print(no() && yes());
            print(yes() || no());
        """,
        out="no ran\nfalse\nyes ran\ntrue",
    ),
    *dart(
        "comparison",
        "Comparison",
        "Operators that compare two values and give true or false: == != < > <= >=.",
        see=("equality", "boolean", "string-comparison"),
        priority=35,
        aka=("compare", "comparisons", "comparing", "relational", "greater than", "less than", "chained comparison"),
        rules=(
            "< > <= >= work on numbers (and anything with compareTo you wrap yourself), not on Strings.",
            "1 == 1.0 is true: numbers compare by value.",
            "a < b < c does not compile: write a < b && b < c.",
        ),
        example="""
            print(1 < 2);
            print(2 >= 2);
            print(3 != 3);
            print(1 == 1.0);
            var x = 5;
            print(1 < x && x < 10);
        """,
        out="true\ntrue\nfalse\ntrue\ntrue",
    ),
    *dart(
        "loop",
        "Loop",
        "Code that repeats: for, for-in, while and do-while are Dart's loops. Each time through the body is one pass (iteration).",
        see=("for-loop", "while-loop", "iteration", "off-by-one"),
        priority=35,
        aka=("loops", "looping", "repeat", "repetition", "forever", "infinite loop", "foreach", "forEach", "do while", "do-while"),
        detect=(r"\b(?:for|while)\s*\(",),
        rules=(
            "for (var i = 0; i < 3; i++) is the counting loop; for (final x in xs) goes through a collection.",
            "xs.forEach((x) { ... }) also repeats, but break and continue do not work in it (use for-in).",
            "A loop whose test never becomes false runs forever.",
        ),
        example="""
            var total = 0;
            for (final n in [1, 2, 3]) {
              total += n;
            }
            print(total);
        """,
        out="6",
    ),
    *dart(
        "iteration",
        "Iteration",
        "One pass through a loop's body. A loop that runs 3 times has 3 iterations.",
        see=("loop", "off-by-one", "iterable"),
        priority=30,
        aka=("iterations", "iterate", "iterating", "pass", "turn of the loop", "loop count"),
        rules=(
            "for (var i = 0; i < 3; i++) has 3 iterations, with i = 0, 1 and 2.",
            "'Iterate' also means 'go through the items of an Iterable'.",
            "The loop's test is checked before every iteration (after it for do-while).",
        ),
        example="""
            var passes = 0;
            for (var i = 2; i < 10; i += 3) {
              passes++;
            }
            print(passes);
        """,
        out="3",
    ),
    *dart(
        "off-by-one",
        "Off-by-one error",
        "Being wrong by exactly one, usually in a loop that runs one time too many or too few, or an index one past the end.",
        see=("loop", "index", "index-error"),
        priority=40,
        aka=("off by one", "fencepost", "fence post", "boundary", "boundary error", "one too many"),
        rules=(
            "A list with n items has positions 0 to n - 1. Looping to i <= xs.length reads one past the end.",
            "for (var i = 0; i < n; i++) runs n times; i <= n would run n + 1 times.",
            "The end of a range is excluded in Dart: [10, 20, 30].sublist(0, 2) is [10, 20].",
        ),
        example="""
            var xs = ['a', 'b', 'c'];
            var passes = 0;
            for (var i = 0; i < xs.length; i++) {
              passes++;
            }
            print(passes);
            try {
              for (var i = 0; i <= xs.length; i++) {
                passes += xs[i].length;
              }
            } on RangeError {
              print('one past the end');
            }
            print(passes);
        """,
        out="3\none past the end\n6",
    ),
    *dart(
        "for-loop",
        "for loop",
        "The loop for counting or for going through a collection: for (var i = 0; i < n; i++) { ... } or for (final x in items) { ... }.",
        see=("loop", "while-loop", "iterable"),
        priority=40,
        aka=("for loops", "for-in", "for in", "for each", "for-each", "counting loop", "for (;;)", "indexed"),
        detect=(r"\bfor\s*\(",),
        rules=(
            "Three parts in the brackets: set-up; test (checked before every pass); step (done after every pass).",
            "for (final x in xs) gives the items without an index; xs.indexed gives (index, item) pairs: for (final (i, x) in xs.indexed).",
            "Changing a list while looping over it with for-in throws a ConcurrentModificationError.",
        ),
        example="""
            var squares = <int>[];
            for (var i = 0; i < 4; i++) {
              squares.add(i * i);
            }
            print(squares);
            for (final (i, c) in ['a', 'b'].indexed) {
              print('$i$c');
            }
        """,
        out="[0, 1, 4, 9]\n0a\n1b",
    ),
    *dart(
        "while-loop",
        "while loop",
        "Repeats its body as long as a test stays true: while (test) { ... }. It is for 'until something happens' loops where you don't know the count.",
        see=("loop", "for-loop", "break-continue"),
        priority=40,
        aka=("while", "while loops", "do-while loop", "do while loop", "loop until"),
        detect=(r"\bwhile\s*\(",),
        rules=(
            "The test is checked first, so the body may run zero times; do { ... } while (test); runs the body at least once.",
            "Something inside must change the test, or the loop never ends.",
            "break leaves it early.",
        ),
        example="""
            var n = 10;
            var steps = 0;
            while (n > 1) {
              n ~/= 2;
              steps++;
            }
            print(steps);
        """,
        out="3",
    ),
    *dart(
        "nested-loop",
        "Nested loop",
        "A loop inside another loop. The inner one runs completely for every pass of the outer one.",
        see=("loop", "nesting", "break-continue"),
        priority=35,
        aka=("nested loops", "loop inside a loop", "double loop", "inner loop", "outer loop", "grid"),
        rules=(
            "Total passes of the inner body = outer passes x inner passes: 3 x 4 = 12.",
            "break and continue only affect the innermost loop (use a label such as outer: to leave both).",
            "The inner loop needs its own variable name.",
        ),
        example="""
            var count = 0;
            for (var i = 0; i < 3; i++) {
              for (var j = 0; j < 4; j++) {
                count++;
              }
            }
            print(count);
            outer:
            for (var i = 0; i < 3; i++) {
              for (var j = 0; j < 3; j++) {
                if (i * j == 2) break outer;
                count++;
              }
            }
            print(count);
        """,
        out="12\n17",
    ),
    *dart(
        "break-continue",
        "break and continue",
        "break leaves the loop completely. continue skips the rest of this pass and goes on with the next.",
        see=("loop", "control-flow", "nested-loop"),
        priority=45,
        aka=("break", "continue", "break statement", "continue statement", "exit a loop", "stop a loop"),
        detect=(r"\b(?:break|continue)\s*;",),
        rules=(
            "They only affect the innermost loop (or the switch) they are in; a label (outer:) aims at an outer loop.",
            "They work in for, while and do-while, but not inside xs.forEach((x) { ... }): there return is the way to skip.",
            "In a switch, break is optional because cases do not fall through.",
        ),
        example="""
            for (var i = 1; i <= 5; i++) {
              if (i == 2) continue;
              if (i == 4) break;
              print(i);
            }
        """,
        out="1\n3",
    ),
    *dart(
        "accumulator",
        "Accumulator",
        "A variable that collects a result over the passes of a loop: a running total, a growing list, a string being built.",
        see=("loop", "reduce", "counter"),
        priority=35,
        aka=("running total", "running sum", "total", "accumulate", "build up", "result variable"),
        rules=(
            "Start it before the loop (var total = 0;) and update it inside (total += n;).",
            "The start value is the answer for an empty input.",
            "fold does the same without the loop.",
        ),
        example="""
            var total = 0;
            var evens = <int>[];
            for (var n = 1; n <= 6; n++) {
              total += n;
              if (n.isEven) evens.add(n);
            }
            print(total);
            print(evens);
        """,
        out="21\n[2, 4, 6]",
    ),
    *dart(
        "counter",
        "Counter",
        "A variable that counts how many times something happened. A Map can count several things at once (a tally).",
        see=("accumulator", "dictionary", "default-value"),
        priority=35,
        aka=("count", "counting", "tally", "counts", "frequency", "histogram", "word count"),
        rules=(
            "count++ adds one each time.",
            "A tally: counts[word] = (counts[word] ?? 0) + 1;",
            "xs.where(test).length counts the matching items.",
        ),
        example="""
            var counts = <String, int>{};
            for (final w in ['a', 'b', 'a']) {
              counts[w] = (counts[w] ?? 0) + 1;
            }
            print(counts);
            print([1, 2, 3, 4].where((n) => n.isEven).length);
        """,
        out="{a: 2, b: 1}\n2",
    ),
    *dart(
        "index",
        "Index",
        "The number that says where an item is in a list or string. Counting starts at 0, so the first item is at index 0.",
        see=("list", "slice", "index-error"),
        priority=40,
        aka=("indexes", "indices", "indexing", "subscript", "zero-based", "indexof", "first", "last", "element at"),
        rules=(
            "xs[0] is the first item and xs[xs.length - 1] the last; xs.first and xs.last are shorter.",
            "A position that does not exist throws a RangeError, and negative positions are not allowed.",
            "xs.indexOf(x) finds the position of x, or -1.",
            "Strings are indexed too: 'abc'[1] is 'b'.",
        ),
        example="""
            var xs = ['a', 'b', 'c'];
            print(xs[0]);
            print(xs.last);
            print(xs.indexOf('c'));
            print(xs.indexOf('z'));
            print('abc'[1]);
        """,
        out="a\nc\n2\n-1\nb",
    ),
    *dart(
        "length",
        "length",
        "How many items a list, set or map holds, or how many characters (UTF-16 code units) a string has. In Dart it is a property: xs.length, with no brackets.",
        see=("index", "list", "string"),
        priority=35,
        aka=("size", "len", "lengths", "isempty", "isnotempty", "how many"),
        detect=(r"\.length\b|\.isEmpty\b|\.isNotEmpty\b",),
        rules=(
            "'abc'.length is 3, [1, 2].length is 2, and a Map's length is its number of keys.",
            "The last position of a list is xs.length - 1.",
            "To test for empty, xs.isEmpty and xs.isNotEmpty read better than xs.length == 0.",
        ),
        example="""
            print('abc'.length);
            print([1, 2].length);
            print({'a': 1}.length);
            print(<int>[].isEmpty);
        """,
        out="3\n2\n1\ntrue",
    ),
    *dart(
        "slice",
        "Slice (sublist, substring)",
        "A piece of a list or string. sublist(start, end) and substring(start, end) include start and leave out end.",
        see=("index", "off-by-one", "list"),
        priority=40,
        aka=("sublist", "substring", "slicing", "take", "skip", "getrange", "range of a list", "part of a list", "slices"),
        detect=(r"\.(?:sublist|substring|getRange|take|skip)\s*\(",),
        rules=(
            "[10, 20, 30, 40].sublist(1, 3) is [20, 30]; leave out the end to go to the end.",
            "take(n) is the first n items, skip(n) is all but the first n (both lazy Iterables).",
            "Negative positions and ends past the length throw a RangeError (take and skip are forgiving).",
        ),
        example="""
            var xs = [10, 20, 30, 40];
            print(xs.sublist(1, 3));
            print(xs.sublist(2));
            print('hello'.substring(1, 4));
            print(xs.take(2).toList());
            print(xs.skip(3).toList());
        """,
        out="[20, 30]\n[30, 40]\nell\n[10, 20]\n[40]",
    ),
    *dart(
        "nesting",
        "Nesting",
        "Putting one structure inside another of the same kind: a loop in a loop, a list of lists, brackets inside brackets, a widget inside a widget.",
        see=("nested-loop", "list", "scope"),
        priority=30,
        aka=("nested", "nest", "nested structure", "inner", "outer", "nested list", "2d list", "list of lists"),
        rules=(
            "Read from the inside out: the innermost brackets are worked out first.",
            "A list of lists is indexed twice: grid[1][0].",
            "Deep nesting is hard to read; give inner parts names or move them into functions.",
        ),
        example="""
            var grid = [
              [1, 2, 3],
              [4, 5, 6],
            ];
            print(grid[1][0]);
            print(grid.map((row) => row.length).toList());
        """,
        out="4\n[3, 3]",
    ),
]
