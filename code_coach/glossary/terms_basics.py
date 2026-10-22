"""Words about how code is built: expressions, operators, variables, scope, syntax, brackets."""

from __future__ import annotations

from .entry import Entry, both

_ARITH = r"[\w)\]]\s*(?:\*\*|//|==|!=|<=|>=|[-+*/%<>])\s*[\w(\[]"

TERMS: list[Entry] = [
    *both(
        "expression",
        "Expression",
        "A piece of code that works out to one value, such as 2 + 3, a variable's name or a function call.",
        see=("evaluate", "statement", "operator"),
        priority=30,
        aka=("expr",),
        detect=(_ARITH,),
        python=dict(
            rules=(
                "Every expression has exactly one value (its result).",
                "Expressions nest: in (2 + 3) * 4 the part in brackets is an expression inside a bigger one.",
                "A lone value, a name and a call such as len(items) are all expressions.",
            ),
            example="""
                x = 5
                print(x * 2 + 1)
            """,
            out="11",
        ),
        javascript=dict(
            rules=(
                "Every expression has exactly one value (its result).",
                "Expressions nest: in (2 + 3) * 4 the part in brackets is an expression inside a bigger one.",
                "A lone value, a name and a call such as items.length are all expressions.",
            ),
            example="""
                const x = 5;
                console.log(x * 2 + 1);
            """,
            out="11",
        ),
    ),
    *both(
        "statement",
        "Statement",
        "One complete instruction, such as storing a value, an if or a loop. It does something, and it "
        "does not need to produce a value.",
        see=("expression", "assignment"),
        priority=20,
        python=dict(
            rules=(
                "Statements run one after another, from the top.",
                "x = 5 is a statement, not an expression: you cannot write y = (x = 5).",
                "An expression on its own line, like print(x), is allowed as a statement.",
            ),
            example="""
                x = 5
                if x > 3:
                    print("big")
            """,
            out="big",
        ),
        javascript=dict(
            rules=(
                "Statements run one after another, from the top. Most end with a semicolon.",
                "An expression on its own line, like console.log(x);, is allowed as a statement.",
                "if, for, while and return are statements; you cannot use one inside an expression.",
            ),
            example="""
                const x = 5;
                if (x > 3) {
                  console.log("big");
                }
            """,
            out="big",
        ),
    ),
    *both(
        "operator",
        "Operator",
        "A symbol or word that does something to values: + adds, == compares, and combines two yes-or-no answers.",
        see=("operand", "precedence", "expression"),
        priority=30,
        aka=("operators",),
        detect=(_ARITH,),
        python=dict(
            rules=(
                "Arithmetic: + - * / // % **. Comparison: == != < > <= >=.",
                "Words work as operators too: and, or, not, in, is.",
                "Some operators do two jobs: + adds numbers but joins strings, and * repeats a string.",
            ),
            example="""
                print(7 - 2, 7 > 2, not 7, "a" + "b")
            """,
            out="5 True False ab",
        ),
        javascript=dict(
            rules=(
                "Arithmetic: + - * / % **. Comparison: == != === !== < > <= >=. Logic: && || ! ??.",
                "typeof and instanceof are operators written as words.",
                "Some operators do two jobs: + adds numbers but joins strings.",
            ),
            example="""
                console.log(7 - 2, 7 > 2, !7, "a" + "b");
            """,
            out="5 true false ab",
        ),
    ),
    *both(
        "operand",
        "Operand",
        "A value an operator works on. In 7 - 2 the operator is - and the operands are 7 and 2.",
        see=("operator", "expression"),
        priority=20,
        rules=(
            "A binary operator (like +) has two operands; a unary one (like -x or not x) has one.",
            "An operand can itself be a whole expression: in 1 + 2 * 3 the right operand of + is 2 * 3.",
        ),
        python=dict(example="a = 7\nb = 2\nprint(a - b)", out="5"),
        javascript=dict(example="const a = 7;\nconst b = 2;\nconsole.log(a - b);", out="5"),
    ),
    *both(
        "precedence",
        "Operator precedence",
        "The order the operators in one expression are done in, when there are several. Higher precedence goes first, "
        "which is why 2 + 3 * 4 is 14, not 20.",
        see=("operator", "evaluate", "bracket"),
        priority=70,
        aka=("order of operations", "operator precedence", "pemdas", "bodmas"),
        detect=(
            r"[\w)]\s*[-+]\s*[\w.()]+\s*(?:\*\*|//|[*/%])\s*[\w(]",
            r"[\w)]\s*(?:\*\*|//|[*/%])\s*[\w.()]+\s*[-+]\s*[\w(]",
        ),
        python=dict(
            rules=(
                "Brackets always go first. Then, from first to last: **, then * / // %, then + -, then "
                "comparisons (== < > in is), then not, then and, then or.",
                "Operators on the same level go left to right, except ** which goes right to left.",
                "and goes before or, so True or False and False is True.",
                "When unsure, add brackets: they cost nothing and make the order obvious.",
            ),
            detect=(r"\band\b[^\n]*\bor\b|\bor\b[^\n]*\band\b",),
            example="""
                print(2 + 3 * 4, (2 + 3) * 4, 2 ** 3 ** 2, True or False and False)
            """,
            out="14 20 512 True",
        ),
        javascript=dict(
            rules=(
                "Brackets always go first. Then, from first to last: ! and a minus sign in front, then **, "
                "then * / %, then + -, then < > <= >=, then == ===, then &&, then ||, then ? : and =.",
                "Operators on the same level go left to right, except ** and = which go right to left.",
                "&& goes before ||, so true || false && false is true.",
                "When unsure, add brackets: they cost nothing and make the order obvious.",
            ),
            detect=(r"&&[^\n]*\|\||\|\|[^\n]*&&",),
            example="""
                console.log(2 + 3 * 4, (2 + 3) * 4, 2 ** 3 ** 2, true || false && false);
            """,
            out="14 20 512 true",
        ),
    ),
    *both(
        "evaluate",
        "Evaluate",
        "To work out the value of an expression, step by step, the way the computer does: brackets first, then "
        "the operators in precedence order.",
        see=("expression", "precedence", "short-circuit"),
        priority=30,
        aka=("evaluation", "evaluates", "evaluated", "work out"),
        rules=(
            "Evaluating an expression always ends in one value.",
            "1 + 2 * 3 becomes 1 + 6, which becomes 7.",
            "Names are replaced by their current values, and a call is replaced by what it returns.",
        ),
        python=dict(example="print(1 + 2 * 3)", out="7"),
        javascript=dict(example="console.log(1 + 2 * 3);", out="7"),
    ),
    *both(
        "variable",
        "Variable",
        "A name that holds a value so you can use it again later. After x = 5, the name x stands for 5.",
        see=("assignment", "value", "reassign", "scope"),
        priority=30,
        aka=("variables", "name", "identifier"),
        python=dict(
            rules=(
                "A variable is created the first time you assign to it; you do not declare it or give it a type.",
                "Names use letters, digits and underscores, cannot start with a digit, are case-sensitive (total and Total differ), and cannot be a keyword.",
                "The same name can hold a different type of value later.",
            ),
            detect=(r"^\s*[A-Za-z_]\w*\s*=(?!=)",),
            example="""
                score = 10
                score = score + 5
                print(score)
            """,
            out="15",
        ),
        javascript=dict(
            rules=(
                "You create one with let (can be reassigned) or const (cannot). Older code uses var.",
                "Names use letters, digits, _ and $, cannot start with a digit, are case-sensitive (total and Total differ), and cannot be a keyword.",
                "A let variable can hold a different type of value later.",
            ),
            detect=(r"^\s*(?:let|const|var)\s+[A-Za-z_$]", r"^\s*[A-Za-z_$][\w$]*\s*=(?!=)"),
            example="""
                let score = 10;
                score = score + 5;
                console.log(score);
            """,
            out="15",
        ),
    ),
    *both(
        "assignment",
        "Assignment",
        "Storing a value in a variable with =. The right side is worked out first, then the result is stored under the name on the left.",
        see=("variable", "reassign", "augmented-assignment"),
        priority=30,
        aka=("assign", "assigned", "=", "set a variable"),
        rules=(
            "= does not mean 'equals' like in maths; it means 'store this'. == (or ===) is the one that compares.",
            "x = x + 1 works: the right side is worked out with the old x, then stored back in x.",
            "Assigning one variable to another copies a number or string, but for a list, dict or object only a second pointer to the same one (see reference).",
        ),
        python=dict(
            detect=(r"^\s*[A-Za-z_]\w*\s*=(?!=)", r":="),
            example="""
                x = 4
                y = x
                x = 9
                print(x, y)
            """,
            out="9 4",
        ),
        javascript=dict(
            detect=(r"^\s*(?:let|const|var)\s+[A-Za-z_$]", r"^\s*[A-Za-z_$][\w$]*\s*=(?!=)"),
            example="""
                let x = 4;
                let y = x;
                x = 9;
                console.log(x, y);
            """,
            out="9 4",
        ),
    ),
    *both(
        "reassign",
        "Reassignment",
        "Giving a variable that already exists a new value. The name now points at the new value, and the old one is forgotten (by that name).",
        see=("assignment", "variable", "augmented-assignment"),
        priority=45,
        aka=("reassign", "reassigned", "reassigning", "overwrite", "update a variable"),
        python=dict(
            rules=(
                "Each assignment replaces the last: after x = 1 then x = 2, x is 2.",
                "The new value can be a different type.",
                "A reassignment can use the old value: x = x + 1.",
            ),
            detect=(
                r"^\s*([A-Za-z_]\w*)\s*(?:=(?!=)|[-+*/%]=)[^\n]*\n(?:[^\n]*\n){0,12}?\s*\1\s*(?:=(?!=)|[-+*/%]=)",
                r"\w\s*(?:\+|-|\*|/|//|%)=\s*\S",
            ),
            example="""
                x = 5
                x = x + 1
                x = "now text"
                print(x)
            """,
            out="now text",
        ),
        javascript=dict(
            rules=(
                "A let variable can be reassigned as often as you like.",
                "A const variable cannot: reassigning it throws a TypeError. (Its contents can still change if it holds an array or object.)",
                "A reassignment can use the old value: x = x + 1.",
            ),
            detect=(
                r"^\s*([A-Za-z_$][\w$]*)\s*(?:=(?!=)|[-+*/%]=)[^\n]*\n(?:[^\n]*\n){0,12}?\s*\1\s*(?:=(?!=)|[-+*/%]=)",
                r"[\w$]\s*(?:\+|-|\*|/|%)=\s*\S|\+\+|--",
            ),
            example="""
                let n = 1;
                n = 2;
                const c = 1;
                try {
                  c = 2;
                } catch (e) {
                  console.log(e.name);
                }
                console.log(n);
            """,
            out="TypeError\n2",
        ),
    ),
    *both(
        "augmented-assignment",
        "Augmented assignment",
        "A shortcut that changes a variable using its own value: x += 5 means x = x + 5.",
        see=("assignment", "reassign", "operator"),
        priority=45,
        aka=("+=", "-=", "*=", "compound assignment", "shorthand"),
        python=dict(
            rules=(
                "The shortcuts are += -= *= /= //= %= **=.",
                "Python has no ++ or --: write x += 1.",
                "On a list, += extends it in place; on a number or string it makes a new value.",
            ),
            detect=(r"(?:\*\*|//|[-+*/%])=",),
            example="""
                x = 10
                x += 5
                x *= 2
                x -= 1
                print(x)
            """,
            out="29",
        ),
        javascript=dict(
            rules=(
                "The shortcuts are += -= *= /= %= **= (and &&= ||= ??=).",
                "x++ and x-- add or subtract one.",
                "On a string, += joins text onto the end.",
            ),
            detect=(r"(?:\*\*|[-+*/%])=(?!=)",),
            example="""
                let x = 10;
                x += 5;
                x *= 2;
                x++;
                console.log(x);
            """,
            out="31",
        ),
    ),
    *both(
        "scope",
        "Scope",
        "The part of a program where a variable's name can be used. Outside its scope the name does not exist.",
        see=("local", "global", "variable"),
        priority=70,
        aka=("scoping", "namespace", "lexical scope", "visibility"),
        python=dict(
            rules=(
                "A variable made inside a function is local to it. A variable made outside every function is global.",
                "Python looks a name up inside-out: the function, any function around it, the file, then the built-ins.",
                "Functions, classes and comprehensions make a new scope; if, for and while blocks do not, so a variable made in a loop is still there after it.",
                "Assigning to a name inside a function makes a new local, unless you declare it with global or nonlocal first.",
            ),
            detect=(r"\b(?:global|nonlocal)\b", r"\bdef\b"),
            example="""
                x = "outside"
                def f():
                    x = "inside"
                    return x
                print(f(), x)
            """,
            out="inside outside",
        ),
        javascript=dict(
            rules=(
                "let and const belong to the nearest pair of braces { } around them (block scope).",
                "var belongs to the whole function instead, and ignores blocks - a good reason to avoid it.",
                "A name is looked up inside-out: the block, the blocks around it, the function, then the global scope.",
                "A function can use variables from where it was written (see closure).",
            ),
            detect=(r"\bvar\b", r"\b(?:let|const)\b", r"\bfunction\b|=>"),
            example="""
                let x = "outside";
                function f() {
                  let x = "inside";
                  return x;
                }
                console.log(f(), x);
            """,
            out="inside outside",
        ),
    ),
    *both(
        "local",
        "Local variable",
        "A variable made inside a function (or, in JavaScript, a block). It exists only while that code runs and cannot be seen outside it.",
        see=("global", "scope", "function"),
        priority=35,
        aka=("local scope", "local"),
        python=dict(
            rules=(
                "Local variables are made fresh each time the function is called.",
                "Parameters are local variables too.",
                "Using a local name outside its function is a NameError.",
            ),
            detect=(r"\bdef\b",),
            example="""
                def f():
                    inner = 1
                    return inner
                f()
                try:
                    print(inner)
                except NameError:
                    print("inner does not exist out here")
            """,
            out="inner does not exist out here",
        ),
        javascript=dict(
            rules=(
                "A let or const inside { } exists only inside those braces.",
                "Parameters are local to their function too.",
                "Reading a name that does not exist is a ReferenceError - but typeof name is 'undefined' without one.",
            ),
            detect=(r"\bfunction\b|=>",),
            example="""
                function f() {
                  const inner = 1;
                  return inner;
                }
                f();
                console.log(typeof inner);
            """,
            out="undefined",
        ),
    ),
    *both(
        "global",
        "Global variable",
        "A variable made outside every function, so the whole file can see it.",
        see=("local", "scope"),
        priority=40,
        aka=("global scope", "global"),
        python=dict(
            rules=(
                "A function can READ a global freely.",
                "To CHANGE one from inside a function you must write global name first; otherwise the assignment makes a new local.",
                "Too many globals make code hard to follow; passing arguments and returning values is clearer.",
            ),
            detect=(r"\bglobal\b",),
            example="""
                count = 0
                def bump():
                    global count
                    count += 1
                bump()
                bump()
                print(count)
            """,
            out="2",
        ),
        javascript=dict(
            rules=(
                "A function can read and change a global (unless it is const).",
                "Assigning to a name you never declared creates an accidental global in sloppy mode; always use let or const.",
                "Too many globals make code hard to follow; passing arguments and returning values is clearer.",
            ),
            detect=(r"^(?:let|const|var)\s",),
            example="""
                let count = 0;
                function bump() {
                  count += 1;
                }
                bump();
                bump();
                console.log(count);
            """,
            out="2",
        ),
    ),
    *both(
        "comment",
        "Comment",
        "A note in the code for people to read. The language ignores it completely.",
        see=("syntax", "token"),
        priority=20,
        python=dict(
            rules=(
                "# starts a comment that runs to the end of the line.",
                "Python has no block comment; a triple-quoted string under a def (a docstring) documents it.",
                "A # inside a string is just a character, not a comment.",
            ),
            detect=(r"raw:(?m)(?:^|\s)#",),
            example="""
                # this line is ignored
                print(1 + 1)  # shows 2
            """,
            out="2",
        ),
        javascript=dict(
            rules=(
                "// starts a comment that runs to the end of the line.",
                "/* ... */ comments out everything between, even across lines.",
                "// inside a string is just text (as in 'http://x').",
            ),
            detect=(r"raw:(?m)(?:^|\s)//|/\*",),
            example="""
                // this line is ignored
                console.log(1 + 1); /* shows 2 */
            """,
            out="2",
        ),
    ),
    *both(
        "syntax",
        "Syntax",
        "The spelling and punctuation rules of a language: what is allowed to be written where. Code that breaks them does not run at all.",
        see=("syntax-error", "keyword", "token"),
        priority=40,
        aka=("grammar",),
        python=dict(
            rules=(
                "Blocks end in a colon and are indented; the keywords are all lowercase except True, False and None.",
                "Correct syntax does not mean correct behaviour: a program can parse and still be wrong.",
                "Python checks the syntax of the whole file before it runs a single line.",
            ),
            example="""
                for line in ("x = 5", "x = = 5"):
                    try:
                        compile(line, "snippet", "exec")
                        print("valid:", line)
                    except SyntaxError:
                        print("invalid:", line)
            """,
            out="valid: x = 5\ninvalid: x = = 5",
        ),
        javascript=dict(
            rules=(
                "Statements end in semicolons (optional in many places), blocks use { }, and names are case-sensitive.",
                "Correct syntax does not mean correct behaviour: a program can parse and still be wrong.",
                "JavaScript checks the syntax of a whole script before it runs a single line.",
            ),
            example="""
                for (const line of ["x = 5", "x = = 5"]) {
                  try {
                    new Function(line);
                    console.log("valid:", line);
                  } catch (e) {
                    console.log("invalid:", line);
                  }
                }
            """,
            out="valid: x = 5\ninvalid: x = = 5",
        ),
    ),
    *both(
        "syntax-error",
        "Syntax error",
        "A message that the code breaks the language's writing rules, so it cannot run. It is found before any line runs.",
        see=("syntax", "token", "keyword", "exception"),
        priority=55,
        aka=("syntaxerror", "parse error", "parsing error"),
        python=dict(
            rules=(
                "Common causes: a missing colon, an unclosed bracket or quote, a misspelt keyword, a stray =, bad indentation.",
                "The reported line is where Python noticed the problem, which can be just after the real mistake.",
                "IndentationError is a kind of syntax error for lines that are indented wrongly.",
            ),
            example="""
                try:
                    compile("a = 1\\nb = = 2", "snippet", "exec")
                except SyntaxError as e:
                    print(type(e).__name__, "on line", e.lineno)
            """,
            out="SyntaxError on line 2",
        ),
        javascript=dict(
            rules=(
                "Common causes: an unclosed bracket, brace or quote, a misspelt keyword, a stray =, a name starting with a digit.",
                "The whole script is rejected: no earlier line runs either.",
                "It is different from a ReferenceError or TypeError, which happen while the program runs.",
            ),
            example="""
                try {
                  new Function("let 2x = 1;");
                } catch (e) {
                  console.log(e.name);
                }
            """,
            out="SyntaxError",
        ),
    ),
    *both(
        "token",
        "Token",
        "The smallest meaningful chunk the language reads: a word, a number, a string or a symbol. 'if x >= 10:' is the tokens if, x, >=, 10 and a colon.",
        see=("syntax", "keyword", "syntax-error"),
        priority=25,
        aka=("tokens", "lexer", "tokenize"),
        rules=(
            "Spaces separate tokens but are otherwise ignored (in Python, only the indentation at the start of a line counts).",
            "A misspelt token (cosnt for const) is read as a plain name, which usually causes an error a moment later.",
            "= and == are different tokens: the language reads the longest symbol it can.",
        ),
        python=dict(
            example="""
                import io, tokenize
                words = [t.string for t in tokenize.generate_tokens(io.StringIO("x >= 10").readline)]
                print([w for w in words if w.strip()])
            """,
            out="['x', '>=', '10']",
        ),
        javascript=dict(
            definition="The smallest meaningful chunk the language reads: a word, a number, a string or a symbol. "
            "'if (x >= 10)' is the tokens if, (, x, >=, 10 and ).",
            example="""
                console.log("x >= 10".match(/\\w+|[^\\s\\w]+/g));
            """,
            out="[ 'x', '>=', '10' ]",
        ),
    ),
    *both(
        "keyword",
        "Keyword",
        "A word the language has set aside for its own use, such as if, for or return. You cannot use one as a variable name.",
        see=("syntax", "token", "variable"),
        priority=35,
        aka=("reserved word", "reserved words", "keywords"),
        python=dict(
            rules=(
                "Examples: if, elif, else, for, while, def, return, class, import, in, is, not, and, or, True, False, None.",
                "print is not a keyword (it is a function you could overwrite).",
                "keyword.kwlist lists all of them.",
            ),
            example="""
                import keyword
                print("if" in keyword.kwlist, "None" in keyword.kwlist, "print" in keyword.kwlist)
            """,
            out="True True False",
        ),
        javascript=dict(
            rules=(
                "Examples: if, else, for, while, function, return, let, const, var, class, new, this, typeof, true, false, null.",
                "undefined, NaN and console are not keywords (they are ordinary names), though you should not reuse them.",
                "let let = 1 is a syntax error.",
            ),
            example="""
                for (const name of ["if", "total"]) {
                  try {
                    new Function("let " + name + " = 1;");
                    console.log(name, "ok");
                  } catch (e) {
                    console.log(name, "is reserved");
                  }
                }
            """,
            out="if is reserved\ntotal ok",
        ),
    ),
    *both(
        "indentation",
        "Indentation",
        "The spaces at the start of a line. In Python they are part of the syntax; in JavaScript they are only for readers.",
        see=("syntax", "nesting", "branch"),
        priority=40,
        aka=("indent", "indented"),
        python=dict(
            definition="The spaces at the start of a line. In Python they are part of the syntax: they decide "
            "which lines belong inside an if, a loop or a def.",
            rules=(
                "A line ending in a colon is followed by lines indented further; all lines of one block use the same indent.",
                "Four spaces per level is the convention. Do not mix tabs and spaces.",
                "Unindenting ends the block: the print below runs once, after the loop.",
            ),
            detect=(r"^[ \t]+\S",),
            example="""
                for i in range(2):
                    print("inside", i)
                print("outside")
            """,
            out="inside 0\ninside 1\noutside",
        ),
        javascript=dict(
            definition="The spaces at the start of a line. In JavaScript they do not change what the code does - "
            "braces { } mark the blocks - but they make the structure readable.",
            rules=(
                "The braces decide what is inside a loop or an if, not the indentation.",
                "A misleading indent is a classic bug: without braces only the first line after an if belongs to it.",
                "Two spaces per level is common.",
            ),
            example="""
                for (let i = 0; i < 2; i++) {
                  console.log("inside", i);
                }
                console.log("outside");
            """,
            out="inside 0\ninside 1\noutside",
        ),
    ),
    *both(
        "bracket",
        "Bracket",
        "A paired symbol that wraps part of the code: ( ) parentheses, [ ] square brackets and { } curly braces. "
        "Each opener needs its own closer.",
        see=("balanced", "nesting", "syntax-error"),
        priority=20,
        aka=("brackets", "parentheses", "parenthesis", "braces", "brace", "curly braces", "square brackets", "brackets"),
        python=dict(
            rules=(
                "( ) group a calculation, hold a call's arguments or make a tuple.",
                "[ ] make a list or pick an item by its index.",
                "{ } make a dict or a set.",
            ),
            detect=(r"[\[{]",),
            example="""
                values = [1, 2, 3]
                print(len(values), values[0], {"k": 1})
            """,
            out="3 1 {'k': 1}",
        ),
        javascript=dict(
            rules=(
                "( ) group a calculation or hold a call's arguments.",
                "[ ] make an array or pick an item by its index.",
                "{ } wrap a block of statements or make an object.",
            ),
            detect=(r"[\[{]",),
            example="""
                const values = [1, 2, 3];
                console.log(values.length, values[0], { k: 1 });
            """,
            out="3 1 { k: 1 }",
        ),
    ),
    *both(
        "balanced",
        "Balanced brackets",
        "Brackets are balanced when every opener has a closer of the same kind, and they close in the right order: the last opened is the first closed.",
        see=("bracket", "nesting", "syntax-error"),
        priority=50,
        aka=("balance", "matching brackets", "unbalanced"),
        rules=(
            "([]{}) is balanced; ([)] is not, because ] arrives while ( is the last one open.",
            "An extra closer ()) or a missing one ((() both make it unbalanced.",
            "The check is a stack: push each opener, and each closer must match the top one.",
        ),
        python=dict(
            example="""
                def balanced(text):
                    pairs = {")": "(", "]": "[", "}": "{"}
                    stack = []
                    for ch in text:
                        if ch in "([{":
                            stack.append(ch)
                        elif not stack or stack.pop() != pairs[ch]:
                            return False
                    return not stack
                print(balanced("([]{})"), balanced("([)]"), balanced("(()"))
            """,
            out="True False False",
        ),
        javascript=dict(
            example="""
                function balanced(text) {
                  const pairs = { ")": "(", "]": "[", "}": "{" };
                  const stack = [];
                  for (const ch of text) {
                    if ("([{".includes(ch)) stack.push(ch);
                    else if (stack.pop() !== pairs[ch]) return false;
                  }
                  return stack.length === 0;
                }
                console.log(balanced("([]{})"), balanced("([)]"), balanced("(()"));
            """,
            out="true false false",
        ),
    ),
    *both(
        "nesting",
        "Nesting",
        "Putting one structure inside another: an if inside a loop, brackets inside brackets, a list inside a list.",
        see=("bracket", "indentation", "loop"),
        priority=45,
        aka=("nested", "nest"),
        python=dict(
            rules=(
                "Each level of nesting is one more level of indentation.",
                "To reach into nested data, chain the indexes: grid[1][0] is item 0 of row 1.",
                "Deep nesting is hard to read; a function or an early return often flattens it.",
            ),
            detect=(r"^[ \t]+(?:if|elif|else|for|while|def|with|try)\b[^\n]*:\s*$", r"\[\s*\[|\]\["),
            example="""
                grid = [[1, 2], [3, 4]]
                print(grid[1][0])
            """,
            out="3",
        ),
        javascript=dict(
            rules=(
                "Each level of nesting is one more pair of braces or brackets.",
                "To reach into nested data, chain the indexes: grid[1][0] is item 0 of row 1.",
                "Deep nesting is hard to read; a function or an early return often flattens it.",
            ),
            detect=(r"^[ \t]+(?:if|for|while|switch|else)\b[^\n]*\{\s*$", r"\[\s*\[|\]\["),
            example="""
                const grid = [[1, 2], [3, 4]];
                console.log(grid[1][0]);
            """,
            out="3",
        ),
    ),
    *both(
        "import",
        "Import",
        "Loading code from another file or library so you can use it in this one. A file of code you load this way is called a module.",
        see=("function", "syntax"),
        priority=45,
        aka=("module", "modules", "library", "package", "require"),
        python=dict(
            rules=(
                "import math then math.sqrt(16); or from math import sqrt then just sqrt(16).",
                "Python comes with a large standard library (math, random, json, pathlib...).",
                "Each .py file is a module; import it by its file name without the .py.",
            ),
            detect=(r"^\s*(?:import|from\s+\S+\s+import)\b",),
            example="""
                import math
                from math import sqrt
                print(math.pi > 3, sqrt(16))
            """,
            out="True 4.0",
        ),
        javascript=dict(
            rules=(
                "In Node's classic style: const path = require('path'). In modern modules: import path from 'path'.",
                "Browsers load modules with import too, from a URL or relative path such as './util.js'.",
                "Each file has its own scope: it shares only what it exports.",
            ),
            detect=(r"^\s*import\b", r"\brequire\("),
            example="""
                const path = require("path");
                console.log(path.basename("/farm/crops.txt"));
            """,
            out="crops.txt",
        ),
    ),
]
