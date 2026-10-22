"""Errors and debugging, JavaScript side: the same eight activities with JavaScript's rules.

JavaScript fails differently from Python and the templates lean on that: dividing
by zero is Infinity, a missing array item is undefined, only reading a property OF
undefined throws, a `const` cannot be reassigned, and there is no `else` on a try.
Every answer is modelled by hand and tests/test_brain_packs.py runs every
template through the real node; each item's `check` program runs the shown code
and works the answer out from what really happened. The shared model of
try/catch/finally and the small helpers live in `_errors_py.py`.
"""

from __future__ import annotations

import json
import random
import re
from string import Template

from ._errors_py import (BODIES, EXCS, LETTERS, RAISE, RET, Flow, P, T, _BRK, _CALL, _CALLP, _CONT, _RERAISE, _ifi, _loop,
                         hrange, spaced)
from ._model import Maker, ints, params, reverse, row, upper
from .items import Item

# ── Oracle programs ─────────────────────────────────────────────────────


def _src(code: str) -> str:
    return json.dumps(code)


#: Wrapped round code that runs with console.log silenced (and put back after): the shown snippet must not
#: print anything when "Run it" runs the check in real node.
_QUIET_HEAD = "const keep = console.log; console.log = () => {}; "
_QUIET_TAIL = " finally { console.log = keep; }"


def _quiet(src: str) -> str:
    """A JavaScript expression that runs `src` with a recording console: gives the list of printed lines, or null if it threw."""
    return ("((s) => { const out = []; const con = { log: (...a) => out.push(a.map(String).join(' ')) };"
            " try { new Function('console', s)(con); } catch (e) { return [out, e]; } return [out, null]; })(" + _src(src) + ")")


def check_exc_name(code: str) -> str:
    return ("(() => { " + _QUIET_HEAD + "try { (0, eval)(" + _src(code) + "); } catch (e) { return e.name; }" + _QUIET_TAIL
            + " return 'none'; })()")


def check_exc_line(code: str) -> str:
    return ("(() => { " + _QUIET_HEAD + "try { (0, eval)(" + _src(code) + "); } catch (e) {"
            " const m = /, <anonymous>:(\\d+):\\d+\\)/.exec(String(e.stack)); return m ? m[1] : '?'; }" + _QUIET_TAIL
            + " return 'none'; })()")


def check_last_print(code: str) -> str:
    return "(() => { const [out] = " + _quiet(code) + "; return out.length ? out[out.length - 1] : 'nothing'; })()"


def check_joined_prints(code: str) -> str:
    return "(() => { const [out] = " + _quiet(code) + "; return out.join('') || 'nothing'; })()"


def check_message(code: str, shown: str, answer: str) -> str:
    return ("(() => { " + _QUIET_HEAD + "try { (0, eval)(" + _src(code) + "); } catch (e) { const msg = e.name + ': ' + e.message;"
            " return msg === " + _src(shown) + " ? " + _src(answer) + " : 'MISMATCH ' + msg; }" + _QUIET_TAIL
            + " return 'none'; })()")


def _two(first: str, second: str, want: str, sep: str) -> str:
    return ("(() => { const ok = (r) => r[1] === null && r[0].join(" + _src(sep) + ") === " + _src(want) + ";"
            " const a = ok(" + _quiet(first) + "), b = ok(" + _quiet(second) + ");"
            " if (a && !b) return '1'; if (b && !a) return '2'; return a ? 'both' : 'neither'; })()")


def check_two_programs(first: str, second: str, want: str) -> str:
    return _two(first, second, want, "\n")


def check_two_loops(first: str, second: str, want: str) -> str:
    return _two(first, second, want, " ")


def check_typo(code: str, typo: str, fixed: str) -> str:
    return ("(() => { " + _QUIET_HEAD + "try { const run = (s) => { try { (0, eval)(s); return null; } catch (e) { return e; } };"
            " const e = run(" + _src(code) + "), f = run(" + _src(fixed) + ");"
            " if (f) return 'REPAIR FAILS ' + f.name + ': ' + f.message; if (!e) return 'NO ERROR'; let m;"
            " if (e.name === 'ReferenceError' && (m = /^(\\w+) is not defined/.exec(e.message))) return m[1];"
            " if (e.name === 'TypeError' && (m = /\\.(\\w+) is not a function/.exec(e.message))) return m[1];"
            " if (e.name === 'SyntaxError') return " + _src(typo) + "; return 'OTHER ' + e.name; }" + _QUIET_TAIL + " })()")


# ── Code for the shared try/catch model ─────────────────────────────────

def _one(s) -> str | None:
    """A statement written on one line, or None when it needs a block of lines (a loop, or a try that holds one)."""
    k = s[0]
    if k == "p":
        return f'console.log("{s[1]}");'
    if k == "pi":
        return "console.log(i);"
    if k == "raise":
        return 'throw new Error("x");'
    if k == "reraise":
        return "throw e;"
    if k == "ret":
        return f'return "{s[1]}";'
    if k in ("break", "continue"):
        return f"{k};"
    if k == "call":
        return "console.log(g());" if s[1] else "g();"
    if k == "if":
        body = [_one(x) for x in s[2]]
        if None in body:
            return None
        return f"if (i === {s[1]}) " + (body[0] if len(body) == 1 else "{ " + " ".join(body) + " }")
    if k == "try":
        _, body, handlers, els, fin = s
        assert not els and len(handlers) <= 1
        parts = [("try", body)] + ([("catch (e)", handlers[0][1])] if handlers else []) + ([("finally", fin)] if fin else [])
        texts = []
        for head, stmts in parts:
            inner = [_one(x) for x in stmts]
            if None in inner or any(x[0] == "try" for x in stmts):
                return None
            texts.append(head + " { " + " ".join(inner) + " }")
        return " ".join(texts)
    return None


def js_lines(stmts, ind: int = 0) -> list[str]:
    """JavaScript for a statement list: one line where a statement fits on one, a block where it does not."""
    pad = "  " * ind
    out: list[str] = []
    for s in stmts:
        one = _one(s)
        if one is not None:
            out.append(pad + one)
        elif s[0] == "loop":
            out.append(f"{pad}for (let i = 1; i <= {s[1]}; i++) {{")
            out += js_lines(s[2], ind + 1)
            out.append(f"{pad}}}")
        elif s[0] == "if":
            out.append(f"{pad}if (i === {s[1]}) {{")
            out += js_lines(s[2], ind + 1)
            out.append(f"{pad}}}")
        else:
            _, body, handlers, els, fin = s
            out.append(f"{pad}try {{")
            out += js_lines(body, ind + 1)
            if handlers:
                out.append(f"{pad}}} catch (e) {{")
                out += js_lines(handlers[0][1], ind + 1)
            if fin:
                out.append(f"{pad}}} finally {{")
                out += js_lines(fin, ind + 1)
            out.append(f"{pad}}}")
    return out


def _count(text: str) -> int:
    n = 0
    for _ in text:
        n += 1
    return n


# ── 1. Which Error ──────────────────────────────────────────────────────

def _we(code: str, answer: str, why: str) -> Maker:
    return row(code, answer, why, check=check_exc_name)


WHICH_ERROR = [
    _we("const nums = [$a, $b];\nconsole.log(nums.length());", "TypeError", "length is a number, not a function, so it cannot be called."),
    _we("let user;\nconsole.log(user.name);", "TypeError", "user is undefined, and reading a property of undefined throws."),
    _we("const user = null;\nconsole.log(user.name);", "TypeError", "null has no properties to read."),
    _we("console.log($w);", "ReferenceError", "$w was never declared, so JavaScript does not know the name."),
    _we("let count = $a;\nconsole.log(cont);", "ReferenceError", "cont is a typo: no such name exists."),
    _we("const x = $a;\nx = $b;", "TypeError", "A const cannot be assigned again."),
    _we("console.log(y);\nlet y = $a;", "ReferenceError", "A let cannot be read before the line that declares it."),
    _we("const f = $a;\nf();", "TypeError", "A number is not a function, so it cannot be called."),
    _we("const nums = [$a, $b];\nnums.push2($c);", "TypeError", "Arrays have push, not push2: that property is undefined, and undefined cannot be called."),
    _we('const s = "$w";\ns.foo();', "TypeError", "Strings have no foo method."),
    _we("new Array(-$a);", "RangeError", "An array cannot have a negative length."),
    _we('"$w".repeat(-$a);', "RangeError", "repeat does not accept a negative count."),
    _we("($a).toFixed(101);", "RangeError", "toFixed accepts 0 to 100 digits."),
    _we('JSON.parse("{bad");', "SyntaxError", "That text is not valid JSON."),
    _we('JSON.parse("");', "SyntaxError", "Empty text is not valid JSON."),
    _we('decodeURIComponent("%");', "URIError", "A lone % is not valid URI encoding."),
    _we("const o = {};\no.a.b = $a;", "TypeError", "o.a is undefined, so setting its b fails."),
    _we("const o = {};\nconsole.log(o.a.b);", "TypeError", "o.a is undefined, so reading its b fails."),
    _we("class A {}\nA();", "TypeError", "A class must be called with new."),
    _we("const [a] = null;", "TypeError", "null cannot be destructured."),
    _we("const { a } = undefined;", "TypeError", "undefined cannot be destructured."),
    _we("const n = $a;\nfor (const x of n) {}", "TypeError", "A number is not iterable, so for...of cannot loop over it."),
    _we("let v;\nv.x;", "TypeError", "v is undefined."),
    _we("BigInt(1.5);", "RangeError", "A fraction cannot become a BigInt."),
    _we("1n + 1;", "TypeError", "BigInt and number cannot be mixed in arithmetic."),
    _we("[].reduce((s, x) => s + x);", "TypeError", "reduce of an empty array needs a starting value."),
    _we("Object.keys(null);", "TypeError", "null cannot be turned into an object."),
    _we("new Set($a);", "TypeError", "A number is not iterable."),
    _we("const n = $a;\nn.toUpperCase();", "TypeError", "Numbers have no toUpperCase method."),
    _we("function f() { return f(); }\nf();", "RangeError", "A function that calls itself forever overflows the call stack."),
    _we('new Date("x").toISOString();', "RangeError", "An invalid date has no ISO string."),
    _we("const a = [$a];\na.length = -1;", "RangeError", "An array's length cannot be negative."),
    _we("total = missing + $a;", "ReferenceError", "missing was never declared."),
    _we('eval("if (");', "SyntaxError", "The text is not a complete JavaScript statement."),
    _we("Symbol() + '';", "TypeError", "A Symbol cannot be turned into a string that way."),
    _we("console.log(undefinedFunction());", "ReferenceError", "No function with that name exists."),
    _we("undefined();", "TypeError", "undefined is not a function."),
    _we("const m = new Map();\nm.get('k').size;", "TypeError", "get gives undefined for a missing key, and undefined has no size."),
    _we('"a" in "abc";', "TypeError", "The in operator needs an object on its right, not a string."),
]


# ── 2. Which Line ───────────────────────────────────────────────────────

def _wl(lines: list[str], bad: int, why: str) -> Maker:
    def make(rng: random.Random) -> Item:
        p = params(rng)
        src = [Template(line).substitute(p) for line in lines]
        at = bad
        if rng.random() < 0.5:
            src.insert(0, "const note = 'ok';")
            at += 1
        code = "\n".join(src)
        return Item(code, str(at), Template(why).safe_substitute(p), check=check_exc_line(code))
    make.__name__ = "line_" + lines[bad - 1].strip()[:20]
    return make


WHICH_LINE = [
    _wl(["const nums = [$a, $b, $c];", "let total = 0;", "for (const n of nums) {", "  total += n;", "}", "console.log(nums.foo.bar);"], 6,
        "The loop is fine; nums.foo is undefined, so reading .bar fails."),
    _wl(["let user;", "const name = 'x';", "console.log(name);", "console.log(user.age);", "console.log('end');"], 4,
        "user is undefined, so reading its age throws."),
    _wl(["const price = $a;", "const qty = 0;", "const avg = price / qty;", "console.log(avg);", "console.log(missing);"], 5,
        "Dividing by 0 does not throw in JavaScript (it gives Infinity); the unknown name does."),
    _wl(["function show(o) {", "  return o.name.length;", "}", "console.log(show({ name: '$w' }));", "console.log(show({}));"], 2,
        "The error happens inside show, where o.name is undefined."),
    _wl(["const f = $a;", "console.log('start');", "f();", "console.log('end');"], 3, "A number cannot be called."),
    _wl(["console.log($a);", "console.log(b);", "const b = $b;"], 2, "b is read before its const line has run."),
    _wl(["const x = $a;", "x = x + 1;", "console.log(x);"], 2, "A const cannot be assigned again."),
    _wl(["const items = [$a, $b];", "for (let i = 0; i < 3; i++) {", "  console.log(items[i].toFixed(1));", "}"], 3,
        "On the third turn items[2] is undefined, and undefined has no toFixed."),
    _wl(["function a() {", "  return b();", "}", "function b() {", "  return null.x;", "}", "a();"], 5,
        "The error is raised inside b, on the line that reads null.x."),
    _wl(["const o = { a: { b: $a } };", "console.log(o.a.b);", "console.log(o.c.d);", "console.log('end');"], 3, "o.c is undefined, so .d fails."),
    _wl(["const arr = [$a, $b];", "arr.push($c);", "arr.pop2();", "console.log(arr);"], 3, "Arrays have pop, not pop2."),
    _wl(["const s = '$w';", "console.log(s.toUpperCase());", "console.log(s.shout());", "console.log('end');"], 3, "Strings have no shout method."),
    _wl(["new Array($a);", "new Array(-1);", "console.log('ok');"], 2, "A negative length is a RangeError."),
    _wl(["console.log('$w'.repeat($a));", "console.log('$w'.repeat(-1));", "console.log('done');"], 2, "repeat refuses a negative count."),
    _wl(["const data = '{\"a\": 1}';", "console.log(JSON.parse(data).a);", "console.log(JSON.parse('{bad').a);"], 3,
        "The first text is valid JSON; the second is not."),
    _wl(["class Dog {", "  bark() { return 'woof'; }", "}", "const d = new Dog();", "console.log(d.bark());", "console.log(d.meow());"], 6,
        "Dog has no meow method."),
    _wl(["const [first] = [$a];", "console.log(first);", "const { x } = null;", "console.log(x);"], 3, "null cannot be destructured."),
    _wl(["let n = $a;", "while (n >= 0) {", "  console.log(10 / n);", "  n--;", "}", "null.y;"], 6,
        "10 / 0 gives Infinity without an error, so the loop finishes; the error comes from null.y."),
    _wl(["const list = [$a, $b, $c];", "console.log(list[5]);", "console.log(list[5].x);"], 3,
        "list[5] is just undefined (no error); reading .x of it is what throws."),
    _wl(["function check(age) {", "  if (age < 0) throw new Error('negative');", "  return age;", "}", "console.log(check($a));",
         "console.log(check(-$b));"], 2, "The throw statement inside check is where the error is raised."),
    _wl(["const total = 0;", "for (let i = 1; i <= $a; i++) {", "  total += i;", "}", "console.log(total);"], 3,
        "total is a const, so the first += fails."),
    _wl(["const nums = [$a, $b];", "const sum = nums.reduce((s, x) => s + x);", "console.log(sum);", "console.log([].reduce((s, x) => s + x));"], 4,
        "reduce of an empty array with no starting value throws."),
    _wl(["const a = 1n;", "console.log(a);", "console.log(a + 1);"], 3, "A BigInt and a number cannot be mixed."),
    _wl(["setup();", "function setup() { console.log('hi'); }", "tidy();"], 3,
        "setup is hoisted, so calling it first works; tidy does not exist."),
    _wl(["const n = $a;", "console.log(n.toFixed(2));", "console.log(n.toFixed(101));"], 3, "toFixed accepts only 0 to 100 digits."),
    _wl(["const o = {};", "o.list = [];", "o.list.push($a);", "o.items.push($b);"], 4, "o.items was never created."),
    _wl(["const m = new Map();", "m.set('a', $a);", "console.log(m.get('a'));", "console.log(m.get('b').x);"], 4,
        "get('b') is undefined, and .x of undefined throws."),
    _wl(["const t = '$w';", "console.log(t.length);", "console.log(t.size);", "console.log(t.size.x);"], 4,
        "t.size is undefined (no error); reading .x of it throws."),
    _wl(["let i = 0;", "while (true) {", "  i++;", "  if (i > $a) undefinedFn();", "}"], 4, "undefinedFn does not exist."),
    _wl(["function f(n) {", "  return n.toUpperCase();", "}", "console.log(f('$w'));", "console.log(f($a));"], 2,
        "A number has no toUpperCase: the error is inside f."),
    _wl(["const user = { name: '$w' };", "console.log(user.name);", "console.log(user.address.city);"], 3, "user.address is undefined."),
]


# ── 3. Read the Message ─────────────────────────────────────────────────

def _msg(code: str, shown: str, answer: str, why: str) -> Maker:
    def make(rng: random.Random) -> Item:
        p = params(rng)
        src, text = Template(code).substitute(p), Template(shown).substitute(p)
        return Item(text, answer, Template(why).safe_substitute(p), check=check_message(src, text, answer))
    make.__name__ = "msg_" + shown[:24]
    return make


def _gone(code: str, shown: str, why: str) -> Maker:
    return _msg(code, shown, "missing", why)


def _bad(code: str, shown: str, why: str) -> Maker:
    return _msg(code, shown, "wrong", why)


MESSAGE = [
    _gone("console.log($w);", "ReferenceError: $w is not defined", "The code uses a name that was never declared: something is missing."),
    _gone("let count = $a;\nconsole.log(cont);", "ReferenceError: cont is not defined", "A typo leaves a name that does not exist."),
    _gone("console.log(y);\nlet y = $a;", "ReferenceError: Cannot access 'y' before initialization", "y has no value yet when this line runs."),
    _gone("undefinedFn();", "ReferenceError: undefinedFn is not defined", "No function with that name exists."),
    _gone("console.log(window.x);", "ReferenceError: window is not defined", "window exists in a browser, not here."),
    _gone("document.title;", "ReferenceError: document is not defined", "document exists in a browser, not here."),
    _gone("let user;\nconsole.log(user.name);", "TypeError: Cannot read properties of undefined (reading 'name')", "user is undefined: there is no object to read from."),
    _gone("let user;\nconsole.log(user.$w);", "TypeError: Cannot read properties of undefined (reading '$w')", "There is no object to read from."),
    _gone("const user = null;\nconsole.log(user.name);", "TypeError: Cannot read properties of null (reading 'name')", "user is null: nothing is there."),
    _gone("const o = {};\nconsole.log(o.a.b);", "TypeError: Cannot read properties of undefined (reading 'b')", "o.a was never set, so it is undefined."),
    _gone("const o = {};\no.a.b = $a;", "TypeError: Cannot set properties of undefined (setting 'b')", "o.a is missing, so nothing can be set on it."),
    _gone("const v = null;\nv.x = $a;", "TypeError: Cannot set properties of null (setting 'x')", "v is null: there is nothing to set a property on."),
    _gone("const list = [$a];\nconsole.log(list[3].x);", "TypeError: Cannot read properties of undefined (reading 'x')", "list[3] does not exist, so it is undefined."),
    _gone("const obj = { a: 1 };\nobj.b.c;", "TypeError: Cannot read properties of undefined (reading 'c')", "obj.b is missing."),
    _gone("const m = new Map();\nm.get('k').size;", "TypeError: Cannot read properties of undefined (reading 'size')", "get gives undefined for a key that is not there."),
    _gone("const { a } = undefined;", "TypeError: Cannot destructure property 'a' of 'undefined' as it is undefined.", "There is no object to take a from."),
    _bad("const x = $a;\nx = $b;", "TypeError: Assignment to constant variable.", "A const cannot be given a new value."),
    _bad("new Array(-$a);", "RangeError: Invalid array length", "A negative number is the wrong length for an array."),
    _bad('"$w".repeat(-$a);', "RangeError: Invalid count value: -$a", "repeat needs a count of 0 or more."),
    _bad("($a).toFixed(101);", "RangeError: toFixed() digits argument must be between 0 and 100", "101 digits is outside the allowed range."),
    _bad('decodeURIComponent("%");', "URIError: URI malformed", "A lone % is not valid encoding."),
    _bad("1n + 1;", "TypeError: Cannot mix BigInt and other types, use explicit conversions", "A BigInt and a number are the wrong mix."),
    _bad("BigInt(1.5);", "RangeError: The number 1.5 cannot be converted to a BigInt because it is not an integer", "A fraction is the wrong value for BigInt."),
    _bad("class A {}\nA();", "TypeError: Class constructor A cannot be invoked without 'new'", "A class is not an ordinary function."),
    _bad("const n = $a;\nfor (const x of n) {}", "TypeError: n is not iterable", "A number cannot be looped over."),
    _bad("new Set($a);", "TypeError: number $a is not iterable (cannot read property Symbol(Symbol.iterator))", "A number is the wrong kind of value for a Set."),
    _bad("[].reduce((s, x) => s + x);", "TypeError: Reduce of empty array with no initial value", "reduce needs something to start from."),
    _bad("Object.keys(null);", "TypeError: Cannot convert undefined or null to object", "null is the wrong kind of value here."),
    _bad('new Date("x").toISOString();', "RangeError: Invalid time value", "The date was never valid."),
    _bad("Symbol() + '';", "TypeError: Cannot convert a Symbol value to a string", "A Symbol is the wrong kind of value to join."),
    _bad("function f() { return f(); }\nf();", "RangeError: Maximum call stack size exceeded", "The calls never stop."),
    _bad("const a = [$a];\na.length = -1;", "RangeError: Invalid array length", "A length cannot be negative."),
    _bad("String.fromCodePoint(-1);", "RangeError: Invalid code point -1", "-1 is not a valid code point."),
    _bad("JSON.stringify(1n);", "TypeError: Do not know how to serialize a BigInt", "JSON has no way to write a BigInt."),
    _bad('"a" in "abc";', "TypeError: Cannot use 'in' operator to search for 'a' in abc", "in works on objects, not strings."),
    _bad("Object.defineProperty(1, 'a', {});", "TypeError: Object.defineProperty called on non-object", "A number is not an object."),
]


# ── 4. Try Flow ─────────────────────────────────────────────────────────

def _flow(shape, why: str) -> Maker:
    def make(rng: random.Random) -> Item:
        letters = rng.sample(LETTERS, 7)
        x, y = rng.sample(EXCS, 2)
        as_func, main, g = shape(*letters, x, y, rng.random() < 0.5)
        lines: list[str] = []
        if g:
            lines += ["function g() {"] + js_lines(g, 1) + ["}"]
        if as_func:
            lines += ["function f() {"] + js_lines(main, 1) + ["}", "console.log(f());"]
        else:
            lines += js_lines(main)
        code = "\n".join(lines)
        answer = Flow(g).program(main, as_func)
        return Item(code, answer, why, check=check_joined_prints(code))
    make.__name__ = "flow_" + why[:20]
    return make


_ANY = None

FLOW_SHAPES = [
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(X) if B else P(b)], [(_ANY, [P(c)])], [], [P(d)])], ()),
     "catch runs only if the try threw; finally runs either way."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(X)], [(_ANY, [P(b)])], [], [P(c)]), P(d)], ()),
     "After the error is caught and finally has run, the program carries on below."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(X), P(b)], [], [], [P(c)])], ()),
     "With no catch the error stops the program, but finally runs first."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(X), P(a)], [(_ANY, [P(b)])], [], [P(c)])], ()),
     "The throw comes first, so the try's print never happens."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [(_ANY, [P(a), RAISE(Y)])], [], [P(b)])], [(_ANY, [P(c)])], [], [P(d)])], ()),
     "A throw inside a catch still lets that try's finally run before the outer catch sees it."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([P(a)], [], [], [P(b)])], [], [], [P(c)])], ()),
     "Inner finally first, then the outer one."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [], [], [P(a)])], [(_ANY, [P(b)])], [], [P(c)])], ()),
     "The error passes through the inner finally on its way to the outer catch."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [(_ANY, [P(a), _RERAISE])], [], [P(b)])], [(_ANY, [P(c)])], [], [P(d)])], ()),
     "throw e inside a catch sends the same error on, after the inner finally."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([RET(a)], [], [], [P(b)]), RET(c)], ()),
     "finally runs before the function really returns, so B prints before the returned A."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([RAISE(X)], [(_ANY, [RET(a)])], [], [P(b)]), RET(c)], ()),
     "A return inside catch still runs finally first."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([RET(a)], [], [], [RET(b)]), RET(c)], ()),
     "A return inside finally replaces the one from the try."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([RAISE(X)], [], [], [RET(a)]), RET(b)], ()),
     "A return in finally swallows the error that was on its way out."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, _CONT), P(a)], [], [], [P(b)]), P(c))], ()),
     "continue skips the rest of that turn, but finally still runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, _BRK), P(a)], [], [], [P(b)])), P(c)], ()),
     "break leaves the loop, but finally runs first."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, RAISE(X)), P(a)], [(_ANY, [P(b), _CONT])], [], []), P(c))], ()),
     "continue in the catch jumps to the next turn, skipping the line after the try."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, ("pi",), T([_ifi(2, RAISE(X))], [(_ANY, [P(a)])], [], []))], ()),
     "Turn 2 prints its number, then the error is caught and A is printed; the loop goes on."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(3, RAISE(X)), ("pi",)], [], [], [P(a)]))], ()),
     "Turn 3 throws with no catch: finally runs, then the program stops."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(X)], [(_ANY, [P(a)])]), T([P(b)], [(_ANY, [P(c)])], [], [P(d)])], ()),
     "Two separate tries run one after the other."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([_CALL, P(c)], [(_ANY, [P(d)])], [], [P(e)])], [P(a), RAISE(X), P(b)]),
     "The error is thrown inside g, so the rest of g and the line after the call are skipped."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([_CALL, P(c)], [(_ANY, [P(d)])], [], [P(e)])], [T([P(a), RAISE(X)], [], [], [P(b)])]),
     "g's own finally runs while the error leaves g, before the caller's catch."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_CALLP, P(d)], [T([P(a), RET(b)], [], [], [P(c)])]),
     "The finally prints C before the return value B reaches the caller's console.log."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(X)], [(_ANY, [P(a), RAISE(Y)])], [], [P(b)])], ()),
     "The catch throws a new error: finally runs, then the program stops."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_CALLP, P(c)], [T([RAISE(X)], [(_ANY, [RET(a)])], [], [P(b)])]),
     "g's finally runs before its return value gets back to the caller."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(4, T([_ifi(2, _CONT), _ifi(3, _BRK), ("pi",)], [], [], [P(a)]))], ()),
     "Turn 2 continues, turn 3 breaks; finally runs on every turn, even those."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_CALLP], [_loop(3, T([_ifi(2, RET(a))], [], [], [P(b)])), RET(c)]),
     "Turn 2 returns, but finally still prints B before the function leaves."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(X)], [(_ANY, [T([RAISE(Y)], [(_ANY, [P(a)])], [], [P(b)])])], [], [P(c)])], ()),
     "A try inside a catch handles its own error first; then the outer finally runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [(_ANY, [P(a)])], [], [P(b), RAISE(Y)])], [(_ANY, [P(c)])])], ()),
     "A throw in finally replaces everything and goes to the outer catch."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [_loop(3, T([_ifi(2, RET(a))], [], [], [P(b)])), RET(c)], ()),
     "The return on turn 2 waits for finally, which also ran on turn 1."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([T([RET(a)], [], [], [P(b)])], [], [], [P(c)]), RET(d)], ()),
     "A return passes through both finallys, inner first."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(2, T([RAISE(X)], [(_ANY, [P(a)])], [], [P(b)]), ("pi",))], ()),
     "Each turn catches its own error, runs finally, and then prints its number."),
]

WHICH_FLOW = [_flow(shape, why) for shape, why in FLOW_SHAPES]


# ── 5. Fix It ───────────────────────────────────────────────────────────

def _fix(lines: list[str], bad: int, want, good: str, wrong: str, why: str) -> Maker:
    def make(rng: random.Random) -> Item:
        p = params(rng)
        src = [Template(x).substitute(p) for x in lines]
        w = want(p) if callable(want) else Template(want).substitute(p)
        indent = src[bad][:len(src[bad]) - len(src[bad].lstrip())]
        g, b = Template(good).substitute(p), Template(wrong).substitute(p)
        first, second = (g, b) if rng.random() < 0.5 else (b, g)

        def program(fix: str) -> str:
            fixed = list(src)
            fixed[bad] = indent + fix
            return "\n".join(fixed)

        marked = list(src)
        marked[bad] = src[bad] + "  // bug"
        prompt = "\n".join(marked + [f"// want: {w}", f"// 1) {first}", f"// 2) {second}"])
        return Item(prompt, "1" if first == g else "2", Template(why).safe_substitute(p),
                    check=check_two_programs(program(first), program(second), w))
    make.__name__ = "fix_" + lines[bad].strip()[:20]
    return make


def _sum_to(n: int) -> int:
    total = 0
    for k in range(1, n + 1):
        total += k
    return total


FIX = [
    _fix(["const nums = [$a, $b, $c];", "console.log(nums[nums.length]);"], 1, "$c", "console.log(nums[nums.length - 1]);",
         "console.log(nums[nums.length - 2]);", "The last item sits at length - 1; length itself is one past the end."),
    _fix(["const total = 0;", "for (let i = 1; i <= $a; i++) {", "  total += i;", "}", "console.log(total);"], 0, lambda p: str(_sum_to(p["a"])),
         "let total = 0;", "let total;", "A const cannot be changed; let can. Without 0 the total would start as undefined."),
    _fix(["const a = $a;", "const b = $b;", "console.log('Total: ' + a + b);"], 2, lambda p: f"Total: {p['a'] + p['b']}",
         "console.log('Total: ' + (a + b));", "console.log('Total: ' + a * b);", "Once a string is involved + joins; brackets make the numbers add first."),
    _fix(["const user = { name: '$w' };", "console.log(user.nam);"], 1, "$w", "console.log(user.name);", "console.log(user['nam']);",
         "nam is a typo: the property is called name."),
    _fix(["const nums = [30, 4, 100];", "nums.sort();", "console.log(nums[0]);"], 1, "4", "nums.sort((x, y) => x - y);", "nums.sort((x, y) => y - x);",
         "sort() compares as text, so 100 comes before 4; a compare function sorts by number."),
    _fix(["let x = $a;", "if (x = $b) {", "  console.log('yes');", "} else {", "  console.log('no');", "}"], 1, "no", "if (x === $b) {",
         "if (x = $a) {", "A single = assigns, and the assigned number is truthy. === compares."),
    _fix(["const list = [$a, $b];", "list.push($c);", "console.log(list.length());"], 2, "3", "console.log(list.length);", "console.log(list.size);",
         "length is a property, not a method."),
    _fix(["const n = '$a';", "console.log(n + 1);"], 1, lambda p: str(p["a"] + 1), "console.log(Number(n) + 1);", "console.log(String(n) + 1);",
         "n is text, so + joins; Number() makes it a number first."),
    _fix(["function add(a, b) {", "  a + b;", "}", "console.log(add($a, $b));"], 1, lambda p: str(p["a"] + p["b"]), "return a + b;",
         "console.log(a + b);", "Without return the function gives back undefined."),
    _fix(["let word = '$w';", "word.toUpperCase();", "console.log(word);"], 1, lambda p: upper(p["w"]), "word = word.toUpperCase();",
         "word.toUpperCase().trim();", "Strings do not change: the new string must be kept."),
    _fix(["const n = [$a, $b, $c];", "let t = 0;", "for (let i = 0; i <= n.length; i++) {", "  t += n[i];", "}", "console.log(t);"], 2,
         lambda p: str(p["a"] + p["b"] + p["c"]), "for (let i = 0; i < n.length; i++) {", "for (let i = 0; i <= n.length - 2; i++) {",
         "The last position is length - 1, so the loop must stop before length."),
    _fix(["console.log(0.1 + 0.2 === 0.3);"], 0, "true", "console.log(Math.abs(0.1 + 0.2 - 0.3) < 0.0001);", "console.log(0.1 + 0.2 == 0.3);",
         "Decimal fractions are not exact in binary, so compare with a small tolerance."),
    _fix(["const count = $a;", "console.log('Count: ' + cnt);"], 1, "Count: $a", "console.log('Count: ' + count);", "console.log('Count: ' + 'count');",
         "cnt is a typo for the variable count."),
    _fix(["const items = ['$w', '$v'];", "console.log(items[2]);"], 1, "$v", "console.log(items[1]);", "console.log(items[0]);",
         "Two items sit at positions 0 and 1."),
    _fix(["let total = 0;", "for (const n of [$a, $b, $c]) {", "  total + n;", "}", "console.log(total);"], 2,
         lambda p: str(p["a"] + p["b"] + p["c"]), "total += n;", "total = n;", "total + n works out a sum and throws it away."),
    _fix(["const s = '$w';", "console.log(s.length());"], 1, lambda p: str(_count(p["w"])), "console.log(s.length);", "console.log(s.length - 1);",
         "length is a property, not a method."),
    _fix(["const nums = [$a, $b, $c];", "console.log(Math.max(nums));"], 1, lambda p: str(max(p["a"], p["b"], p["c"])),
         "console.log(Math.max(...nums));", "console.log(Math.min(...nums));", "Math.max wants separate numbers: spread the array."),
    _fix(["const o = { a: $a };", "console.log(o.b.c);"], 1, "none", "console.log(o.b?.c ?? 'none');", "console.log(o.b?.c);",
         "?. stops at undefined, and ?? supplies the fallback."),
    _fix(["const arr = [$a, $b, $c];", "console.log(arr[-1]);"], 1, "$c", "console.log(arr.at(-1));", "console.log(arr[arr.length]);",
         "arr[-1] is a property named -1; .at(-1) counts from the end."),
    _fix(["let a = $a;", "let b = $b;", "a = b; b = a;", "console.log(a, b);"], 2, "$b $a", "[a, b] = [b, a];", "b = a; a = b;",
         "The first assignment overwrites a, so b gets the new a. A destructuring swap does both at once."),
    _fix(["const nums = [$a, $b];", "const doubled = nums.map(n => { n * 2 });", "console.log(doubled[0]);"], 1, lambda p: str(p["a"] * 2),
         "const doubled = nums.map(n => n * 2);", "const doubled = nums.map(n => { return n; });",
         "Braces need an explicit return; without them the arrow gives undefined."),
    _fix(["const scores = [$a, $b, $c];", "let best = 0;", "for (const s of scores) {", "  if (s > best) best == s;", "}", "console.log(best);"], 3,
         lambda p: str(max(p["a"], p["b"], p["c"])), "if (s > best) best = s;", "if (s < best) best = s;", "== compares; = assigns."),
    _fix(["const str = '$w';", "console.log(str.reverse());"], 1, lambda p: reverse(p["w"]), "console.log([...str].reverse().join(''));",
         "console.log(str.split('').join(''));", "Only arrays have reverse: split the text into letters first."),
    _fix(["const price = '$a.5';", "console.log(parseInt(price));"], 1, lambda p: f"{p['a']}.5", "console.log(parseFloat(price));",
         "console.log(Number(price) + 1);", "parseInt stops at the decimal point; parseFloat keeps it."),
    _fix(["const s = 'a-b-c';", "console.log(s.replace('-', '+'));"], 1, "a+b+c", "console.log(s.replaceAll('-', '+'));",
         "console.log(s.replace('-', '+', 'g'));", "replace changes only the first match; replaceAll changes every one."),
    _fix(["const n = $a;", "console.log(n === '$a');"], 1, "true", "console.log(n == '$a');", "console.log(n === '$a' + 0);",
         "=== also compares types, so a number is never === a string; == converts first."),
]


# ── 6. Crash or Print ───────────────────────────────────────────────────

def _cp(lines: list[str], answer, why: str) -> Maker:
    def make(rng: random.Random) -> Item:
        p = params(rng)
        code = "\n".join(Template(x).substitute(p) for x in lines)
        got = answer(p) if callable(answer) else Template(answer).substitute(p)
        return Item(code, got, Template(why).safe_substitute(p), check=check_last_print(code))
    make.__name__ = "crash_" + lines[0][:20]
    return make


CRASH = [
    _cp(["console.log('start');", "const nums = [$a, $b, $c];", "console.log(nums[2]);", "console.log(nums[3].x);", "console.log('done');"], "$c",
        "nums[3] is undefined; reading .x of it crashes before anything prints."),
    _cp(["let user;", "console.log('hi');", "console.log(user.name);"], "hi", "user is undefined, so reading its name crashes."),
    _cp(["const d = { a: $a };", "console.log(d.a);", "console.log(d.b.c);", "console.log('end');"], "$a", "d.b is undefined, and .c of it throws."),
    _cp(["console.log(1);", "console.log(2);", "console.log(nope);", "console.log(3);"], "2", "nope is not defined: the argument fails before log runs."),
    _cp(["let n = $a;", "console.log(n);", "n();", "console.log('done');"], "$a", "A number cannot be called."),
    _cp(["const x = $a;", "console.log(x);", "x = $b;", "console.log(x);"], "$a", "A const cannot be assigned again."),
    _cp(["console.log('loading');", "const r = JSON.parse('{bad');", "console.log('parsed');"], "loading", "The text is not valid JSON."),
    _cp(["const nums = [$a, $b, $c];", "for (let i = 0; i < 5; i++) {", "  console.log(nums[i].toFixed(1));", "}"], lambda p: f"{p['c']}.0",
        "The fourth turn has nums[3], which is undefined."),
    _cp(["console.log(10 / 0);", "console.log(null.x);", "console.log('end');"], "Infinity", "Dividing by zero is Infinity, not a crash; null.x is."),
    _cp(["console.log('a');", "console.log('b'.toUpperCase());", "console.log('c'.shout());", "console.log('d');"], "B", "Strings have no shout method."),
    _cp(["function f(o) {", "  console.log('got', o.name);", "}", "f({ name: '$w' });", "f(null);"], lambda p: "got " + p["w"],
        "f(null) crashes while the arguments of log are worked out."),
    _cp(["let total = 0;", "for (const n of [$a, $b]) {", "  total += n;", "  console.log(total);", "}", "total();"], lambda p: str(p["a"] + p["b"]),
        "The loop prints its totals; calling a number crashes."),
    _cp(["console.log('x');", "undefinedFn();", "console.log('y');"], "x", "undefinedFn does not exist."),
    _cp(["const a = [$a];", "console.log(a.length);", "a.length = -1;", "console.log('ok');"], "1", "A negative length is a RangeError."),
    _cp(["console.log('one');", "console.log([].reduce((s, x) => s + x));", "console.log('two');"], "one", "reduce of an empty array throws."),
    _cp(["class A {}", "console.log('before');", "A();", "console.log('after');"], "before", "A class must be called with new."),
    _cp(["let i = 3;", "while (i >= 0) {", "  console.log(12 / i);", "  i--;", "}", "i.x.y;"], "Infinity",
        "12 / 0 is Infinity, so the loop never crashes; i.x.y does, after it."),
    _cp(["const s = '$w';", "console.log(s.length);", "console.log(s.size.x);"], lambda p: str(_count(p["w"])), "s.size is undefined, and .x of it throws."),
    _cp(["const o = {};", "o.a = $a;", "console.log(o.a);", "o.b.c = 1;"], "$a", "o.b is undefined, so setting .c fails."),
    _cp(["console.log('A');", "const [x] = null;", "console.log('B');"], "A", "null cannot be destructured."),
    _cp(["console.log('go');", "try {", "  null.x;", "} finally {", "  console.log('cleanup');", "}", "console.log('never');"], "cleanup",
        "finally runs on the way out, and then the crash goes on."),
    _cp(["function a() { b(); }", "function b() { console.log('in b'); c(); }", "console.log('start');", "a();"], "in b", "c does not exist."),
    _cp(["console.log(typeof missing);", "console.log(missing);"], "undefined", "typeof on an unknown name is safe; reading it is not."),
    _cp(["const nums = [];", "console.log(nums[0]);", "console.log(nums[0].x);"], "undefined", "Out of range gives undefined; reading a property of it throws."),
    _cp(["const t = [$a, $b];", "console.log(t.length);", "t.push2($a);"], "2", "Arrays have push, not push2."),
    _cp(["console.log('a' + 1);", "console.log('a' - 1);", "console.log(x.y);"], "NaN", "'a' - 1 is NaN, which is fine; x does not exist."),
    _cp(["const o = { n: $a };", "console.log(o.n);", "console.log(o.m);", "console.log(o.m.k);"], "undefined", "A missing property is undefined; reading its .k throws."),
    _cp(["console.log('x');", "new Array(-1);"], "x", "A negative length is a RangeError."),
    _cp(["console.log(Number('abc'));", "console.log(nothing);"], "NaN", "Number('abc') is NaN, not an error; nothing does not exist."),
    _cp(["const x = y;", "console.log('done');"], "nothing", "y does not exist, so the program stops before printing."),
    _cp(["const t = '$w';", "console.log(t.toUpperCase());", "console.log(t.toUpperCase().foo());"], lambda p: upper(p["w"]), "foo is not a method of strings."),
]


# ── 7. Off by One Bug ───────────────────────────────────────────────────

R_STOP = "< stops before the limit; <= includes it."

OB_SPECS = [
    (lambda p: ([], "for (let i = 1; i <= $a; i++)", "for (let i = 1; i < $a; i++)", "i", hrange(1, p["a"] + 1), hrange(1, p["a"]), R_STOP)),
    (lambda p: ([], "for (let i = 0; i < $a; i++)", "for (let i = 0; i <= $a; i++)", "i", hrange(0, p["a"]), hrange(0, p["a"] + 1), R_STOP)),
    (lambda p: ([], "for (let i = 0; i <= $a; i++)", "for (let i = 0; i < $a; i++)", "i", hrange(0, p["a"] + 1), hrange(0, p["a"]), R_STOP)),
    (lambda p: ([], "for (let i = $lo; i <= $hi; i++)", "for (let i = $lo; i < $hi; i++)", "i", hrange(p["lo"], p["hi"] + 1),
                hrange(p["lo"], p["hi"]), "<= $hi includes $hi itself.")),
    (lambda p: ([], "for (let i = $lo; i < $hi; i++)", "for (let i = $lo; i <= $hi; i++)", "i", hrange(p["lo"], p["hi"]),
                hrange(p["lo"], p["hi"] + 1), "< $hi stops before $hi.")),
    (lambda p: ([], "for (let i = $a; i > 0; i--)", "for (let i = $a; i > 1; i--)", "i", hrange(p["a"], 0, -1), hrange(p["a"], 1, -1),
                "i > 0 still runs when i is 1.")),
    (lambda p: ([], "for (let i = $a; i >= 0; i--)", "for (let i = $a; i > 0; i--)", "i", hrange(p["a"], -1, -1), hrange(p["a"], 0, -1),
                ">= 0 includes 0.")),
    (lambda p: ([], "for (let i = 0; i < $b * 2; i += 2)", "for (let i = 1; i < $b * 2; i += 2)", "i", hrange(0, p["b"] * 2, 2),
                hrange(1, p["b"] * 2, 2), "Starting at 0 and adding 2 gives the even numbers.")),
    (lambda p: ([], "for (let i = 0; i <= $b * 3; i += 3)", "for (let i = 0; i < $b * 3; i += 3)", "i", hrange(0, p["b"] * 3 + 1, 3),
                hrange(0, p["b"] * 3, 3), "<= includes $b * 3 itself.")),
    (lambda p: (["const xs = $xs;"], "for (const x of xs.slice(0, $k))", "for (const x of xs.slice(0, $k - 1))", "x", p["xs"][:p["k"]],
                p["xs"][:p["k"] - 1], "slice(0, $k) keeps the first $k items; the end index is not included.")),
    (lambda p: (["const xs = $xs;"], "for (const x of xs.slice($k))", "for (const x of xs.slice($k + 1))", "x", p["xs"][p["k"]:],
                p["xs"][p["k"] + 1:], "slice($k) starts at position $k.")),
    (lambda p: (["const xs = $xs;"], "for (const x of xs.slice(-$k))", "for (const x of xs.slice(-$k - 1))", "x", p["xs"][len(p["xs"]) - p["k"]:],
                p["xs"][len(p["xs"]) - p["k"] - 1:], "slice(-$k) is exactly the last $k items.")),
    (lambda p: (["const xs = $xs;"], "for (let i = 0; i < xs.length; i++)", "for (let i = 0; i < xs.length - 1; i++)", "xs[i]", p["xs"], p["xs"][:-1],
                "Positions 0 to length - 1 cover every item.")),
    (lambda p: (["const xs = $xs;"], "for (let i = 0; i < xs.length; i++)", "for (let i = 1; i < xs.length; i++)", "xs[i]", p["xs"], p["xs"][1:],
                "Counting starts at 0, so i = 1 skips the first item.")),
    (lambda p: (["const xs = $xs;"], "for (let i = xs.length - 1; i >= 0; i--)", "for (let i = xs.length - 1; i > 0; i--)", "xs[i]",
                [p["xs"][len(p["xs"]) - 1 - j] for j in range(len(p["xs"]))],
                [p["xs"][len(p["xs"]) - 1 - j] for j in range(len(p["xs"]) - 1)], "i >= 0 includes position 0.")),
    (lambda p: (["let n = $a;"], "while (n > 0)", "while (n > 1)", "n--", hrange(p["a"], 0, -1), hrange(p["a"], 1, -1),
                "n > 0 still runs when n is 1.")),
    (lambda p: (["let n = $a;"], "while (n >= 0)", "while (n > 0)", "n--", hrange(p["a"], -1, -1), hrange(p["a"], 0, -1), ">= 0 includes 0.")),
    (lambda p: (["let i = 1;"], "while (i <= $a)", "while (i < $a)", "i++", hrange(1, p["a"] + 1), hrange(1, p["a"]), R_STOP)),
    (lambda p: ([], "for (let i = 0; i < $a; i++)", "for (let i = 1; i <= $a; i++)", "i", hrange(0, p["a"]), hrange(1, p["a"] + 1),
                "Starting at 0 gives $a numbers, ending at $a - 1.")),
]


def _ob_make(spec, body) -> Maker:
    fmt, fn = body

    def make(rng: random.Random) -> Item:
        for _ in range(50):
            p = params(rng)
            xs = ints(rng, 5, 1, 9)
            p.update(lo=min(p["a"], p["b"]), hi=max(p["a"], p["b"]), xs=xs, k=rng.randint(1, 3))
            pre, g_head, b_head, var, g_seq, b_seq, why = spec(p)
            g_out, b_out = [fn(v) for v in g_seq], [fn(v) for v in b_seq]
            if g_out and b_out and g_out != b_out:
                break
        else:
            raise AssertionError("no distinct pair")
        text = dict(p, xs=str(xs))
        # `n--` and `i++` print and step in one go: the loop value is what is printed.
        shown = Template(fmt).substitute(v=var)
        if var in ("n--", "i++"):
            shown = Template(fmt).substitute(v=var)
        good = Template(g_head).substitute(text) + f" console.log({shown});"
        bad = Template(b_head).substitute(text) + f" console.log({shown});"
        pre_lines = [Template(x).substitute(text) for x in pre]
        first, second = (good, bad) if rng.random() < 0.5 else (bad, good)
        want = spaced(g_out)
        prompt = "\n".join(pre_lines + [f"// want: {want}", "// 1)", first, "// 2)", second])
        return Item(prompt, "1" if first == good else "2", Template(why).safe_substitute(text),
                    check=check_two_loops("\n".join(pre_lines + [first]), "\n".join(pre_lines + [second]), want))
    make.__name__ = "ob_" + str(id(spec))
    return make


OFF_BY_ONE = [_ob_make(spec, body) for spec in OB_SPECS for body in BODIES]


# ── 8. Typo Hunt ────────────────────────────────────────────────────────

def _typo(code: str, typo: str, fix: str) -> Maker:
    def make(rng: random.Random) -> Item:
        p = params(rng)
        src = Template(code).substitute(p)
        fixed = re.sub(rf"\b{typo}\b", fix, src)
        assert fixed != src
        return Item(src, typo, f"{typo} is a misspelling of {fix}.", check=check_typo(src, typo, fixed))
    make.__name__ = "typo_" + typo
    return make


TYPO_ROWS = [
    ("const total = $a;\nconsole.log(totl);", "totl", "total"),
    ("let name = '$w';\nconsole.log(nmae);", "nmae", "name"),
    ("const price = $a;\nconst tax = price * 2;\nconsole.log(prcie + tax);", "prcie", "price"),
    ("const nums = [$a];\nnums.pusj($b);\nconsole.log(nums);", "pusj", "push"),
    ("const nums = [$a];\nnums.pushh($b);\nconsole.log(nums);", "pushh", "push"),
    ("const nums = [$a, $b];\nconsole.log(nums.mapp(n => n * 2));", "mapp", "map"),
    ("const nums = [$a, $b];\nconsole.log(nums.fliter(n => n > 1));", "fliter", "filter"),
    ("const nums = [$a, $b];\nnums.forEch(n => n);", "forEch", "forEach"),
    ("const nums = [$a, $b];\nconsole.log(nums.inclues($a));", "inclues", "includes"),
    ("const nums = [$a, $b];\nconsole.log(nums.indexof($b));", "indexof", "indexOf"),
    ("const nums = [$a, $b];\nconsole.log(nums.joinn('-'));", "joinn", "join"),
    ("const nums = [$a, $b, $c];\nconsole.log(nums.slcie(1));", "slcie", "slice"),
    ("const nums = [$a, $b, $c];\nconsole.log(nums.reduc((s, x) => s + x, 0));", "reduc", "reduce"),
    ("const nums = [$a, $b, $c];\nnums.spilce(0, 1);", "spilce", "splice"),
    ("const s = '$w';\nconsole.log(s.toUppercase());", "toUppercase", "toUpperCase"),
    ("const s = '$w';\nconsole.log(s.toLowerCas());", "toLowerCas", "toLowerCase"),
    ("const s = ' $w ';\nconsole.log(s.trimm());", "trimm", "trim"),
    ("const s = '$w';\nconsole.log(s.splitt(''));", "splitt", "split"),
    ("const s = '$w';\nconsole.log(s.repat(2));", "repat", "repeat"),
    ("const s = '$w';\nconsole.log(s.includs('o'));", "includs", "includes"),
    ("const s = '$w';\nconsole.log(s.startWith('f'));", "startWith", "startsWith"),
    ("const s = '$w';\nconsole.log(s.charAT(0));", "charAT", "charAt"),
    ("const s = '$w';\nconsole.log(s.padStar(8));", "padStar", "padStart"),
    ("consol.log($a);", "consol", "console"),
    ("console.lg($a);", "lg", "log"),
    ("console.log(Math.flor(7.5));", "flor", "floor"),
    ("console.log(Math.maxx($a, $b));", "maxx", "max"),
    ("console.log(Math.sqroot(9));", "sqroot", "sqrt"),
    ("console.log(Mathh.floor(2.5));", "Mathh", "Math"),
    ("console.log(JSON.pars('{}'));", "pars", "parse"),
    ("console.log(JSON.stringfy({}));", "stringfy", "stringify"),
    ("console.log(Object.keis({ a: $a }));", "keis", "keys"),
    ("console.log(Array.isarray([]));", "isarray", "isArray"),
    ("console.log(parseint('$a'));", "parseint", "parseInt"),
    ("console.log(parseFlot('$a.5'));", "parseFlot", "parseFloat"),
    ("console.log(Numbr('$a'));", "Numbr", "Number"),
    ("const m = new Mpa();\nm.set('a', $a);", "Mpa", "Map"),
    ("const s = new Sett([$a, $b]);\nconsole.log(s.size);", "Sett", "Set"),
    ("console.log(Arrray.from([$a]));", "Arrray", "Array"),
    ("console.log(Obect.keys({}));", "Obect", "Object"),
    ("console.log(Math.PI.toFixd(2));", "toFixd", "toFixed"),
    ("const ok = ture;\nconsole.log(ok);", "ture", "true"),
    ("const ok = flase;\nconsole.log(ok);", "flase", "false"),
    ("const x = nul;\nconsole.log(x);", "nul", "null"),
    ("const x = undefiend;\nconsole.log(x);", "undefiend", "undefined"),
    ("cosnt x = $a;\nconsole.log(x);", "cosnt", "const"),
    ("lte x = $a;\nconsole.log(x);", "lte", "let"),
    ("fucntion f() {\n  return $a;\n}\nconsole.log(f());", "fucntion", "function"),
    ("function f(n) {\n  retrun n * 2;\n}\nconsole.log(f($a));", "retrun", "return"),
    ("whlie (false) {\n  console.log($a);\n}", "whlie", "while"),
    ("const x = $a;\nif (x > 1) {\n  console.log(1);\n} esle {\n  console.log(2);\n}", "esle", "else"),
    ("fro (let i = 0; i < $a; i++) {\n  console.log(i);\n}", "fro", "for"),
    ("for (let i = 0; i < 3; i++) {\n  if (i > 0) brak;\n}", "brak", "break"),
    ("for (let i = 0; i < 3; i++) {\n  if (i === 0) continu;\n}", "continu", "continue"),
]

TYPO = [_typo(*r) for r in TYPO_ROWS]
