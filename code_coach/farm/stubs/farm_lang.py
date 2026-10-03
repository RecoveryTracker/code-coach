"""The Farmer Was Replaced's own language, run the way the game runs it.

Run as:  python -u farm_lang.py <entry>     (the player's files are files/<name>.py)

The game's language looks like Python and mostly is: the same syntax, the
same lists, dictionaries, tuples and sets, the same import. Two things set
it apart, and they are why this is an interpreter rather than plain Python:

- Time. Every operation costs ticks - the wiki's Operation Costs and Timing
  pages: + costs one, entering an if costs one, a list literal one per item,
  a dictionary lookup by a long string more; variables, calls and return are
  free. The farm charges for drone commands itself; this counts everything
  else and sends the total with the next command (or on its own, every
  thousand ticks), so a slow loop really is slow in game time.
- Scope. A function reads globals, but every assignment inside it makes a
  local, and there is no `global`. A function sees its own locals and its
  file's globals - not the locals of a function it was defined in.

Lambdas, classes, try, with, comprehensions, f-strings, *args and keyword
arguments are not part of the game's language and are refused, on their
line, before anything runs.

It speaks the same line protocol as the other languages' libraries (see
code_coach/farm/protocol.py), with one addition: every command carries
"t", the ticks the language spent since the last one, and "__ticks__"
sends them on their own.
"""

import ast
import json
import os
import sys

MARK = "\x1eCC"
#: Ticks pile up to this before they are sent on their own.
FLUSH = 1000

# NAMES-START
DIRECTIONS = ["North", "East", "South", "West"]
GROUPS = {"Entities": [], "Items": [], "Grounds": [], "Unlocks": [], "Hats": []}
FUNCTIONS = []
# NAMES-END

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(HERE, "files")

_out = sys.stdout
_in = sys.stdin


# ── Errors ─────────────────────────────────────────────────────────────

class GameError(Exception):
    """Something the program did wrong, with where it happened."""

    def __init__(self, message, node=None, file=""):
        super().__init__(message)
        self.message = message
        self.line = getattr(node, "lineno", 0) or 0
        self.file = file


class _Return(Exception):
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value


class _Break(Exception):
    pass


class _Continue(Exception):
    pass


# ── Values ─────────────────────────────────────────────────────────────

class Value:
    """One of the game's named values: North, Entities.Bush, Items.Hay."""

    __slots__ = ("name",)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Value) and other.name == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)


_VALUES = {}


def value(name):
    if name not in _VALUES:
        _VALUES[name] = Value(name)
    return _VALUES[name]


class Group:
    """Entities, Items, ...: names that stand for values."""

    def __init__(self, title, members):
        self.title = title
        self.members = {m: value(title + "." + m) for m in members}

    def __repr__(self):
        return self.title


class Function:
    __slots__ = ("name", "params", "defaults", "body", "module", "node")

    def __init__(self, name, params, defaults, body, module, node):
        self.name = name
        self.params = params
        self.defaults = defaults
        self.body = body
        self.module = module
        self.node = node

    def __repr__(self):
        return f"<function {self.name}>"


class Builtin:
    __slots__ = ("name", "impl")

    def __init__(self, name, impl):
        self.name = name
        self.impl = impl

    def __repr__(self):
        return f"<builtin {self.name}>"


class Module:
    __slots__ = ("name", "globals", "loading")

    def __init__(self, name):
        self.name = name
        self.globals = {"__name__": name}
        self.loading = True

    def __repr__(self):
        return f"<module {self.name}>"


class Frame:
    """Where names live while code runs: a function's locals (None at the top
    of a file) and the file's globals."""

    __slots__ = ("locals", "module")

    def __init__(self, module, local=None):
        self.module = module
        self.locals = local


def wire(v):
    if isinstance(v, Value):
        return v.name
    if isinstance(v, (list, tuple, set, frozenset)):
        return [wire(x) for x in v]
    if isinstance(v, dict):
        return {str(wire(k)): wire(x) for k, x in v.items()}
    if isinstance(v, (Function, Builtin, Module, Group)):
        raise GameError(f"{show(v)} can't be sent to the farm.")
    return v


def unwire(v):
    if isinstance(v, str) and (v in DIRECTIONS or v.split(".", 1)[0] in GROUPS):
        return value(v)
    if isinstance(v, list):
        return tuple(unwire(x) for x in v)
    if isinstance(v, dict):
        return {unwire(k): unwire(x) for k, x in v.items()}
    return v


def show(v, inner=False):
    """A value written out the way the game prints it."""
    if v is None:
        return "None"
    if v is True:
        return "True"
    if v is False:
        return "False"
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() and abs(v) < 1e15 else repr(v)
    if isinstance(v, str):
        return repr(v) if inner else v
    if isinstance(v, list):
        return "[" + ", ".join(show(x, True) for x in v) + "]"
    if isinstance(v, tuple):
        if len(v) == 1:
            return "(" + show(v[0], True) + ",)"
        return "(" + ", ".join(show(x, True) for x in v) + ")"
    if isinstance(v, dict):
        return "{" + ", ".join(show(k, True) + ": " + show(x, True) for k, x in v.items()) + "}"
    if isinstance(v, (set, frozenset)):
        return "{" + ", ".join(show(x, True) for x in v) + "}" if v else "set()"
    if isinstance(v, range):
        return show(list(v))
    return repr(v)


def kind(v):
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "a boolean"
    if isinstance(v, (int, float)):
        return "a number"
    if isinstance(v, str):
        return "a string"
    if isinstance(v, list):
        return "a list"
    if isinstance(v, tuple):
        return "a tuple"
    if isinstance(v, dict):
        return "a dictionary"
    if isinstance(v, (set, frozenset)):
        return "a set"
    if isinstance(v, Value):
        return v.name
    if isinstance(v, (Function, Builtin)):
        return "a function"
    if isinstance(v, Module):
        return "a module"
    return type(v).__name__


# ── What operations cost (wiki: Operation Costs, Timing) ───────────────

def key_cost(k):
    if isinstance(k, str):
        return max(len(k) // 8, 1)
    if isinstance(k, tuple):
        return sum(key_cost(x) for x in k) or 1
    return 1


def compare_cost(a, b):
    if type(a) is not type(b):
        return 1
    if isinstance(a, (list, tuple)):
        if len(a) != len(b):
            return 1
        total = 1
        for x, y in zip(a, b):
            total += compare_cost(x, y)
            if x != y:
                break
        return total
    return 1


def contains_cost(item, container):
    if isinstance(container, (list, tuple)):
        for i, x in enumerate(container):
            if x == item:
                return 1 + i
        return 1 + len(container)
    if isinstance(container, (dict, set, frozenset)):
        return key_cost(item)
    return 1


_NOT_PART = {
    ast.Lambda: "lambda", ast.ListComp: "a list comprehension", ast.SetComp: "a set comprehension",
    ast.DictComp: "a dictionary comprehension", ast.GeneratorExp: "a generator expression",
    ast.JoinedStr: "an f-string", ast.Await: "await", ast.Yield: "yield", ast.YieldFrom: "yield",
    ast.NamedExpr: ":=", ast.Starred: "*", ast.ClassDef: "class", ast.Try: "try",
    ast.With: "with", ast.AsyncFunctionDef: "async", ast.AsyncFor: "async", ast.AsyncWith: "async",
    ast.Global: "global", ast.Nonlocal: "nonlocal", ast.Raise: "raise", ast.Assert: "assert",
    ast.Delete: "del", ast.AnnAssign: "a type annotation", ast.Match: "match",
}
if hasattr(ast, "TryStar"):
    _NOT_PART[ast.TryStar] = "try"


def check_language(tree, file):
    """Refuse what isn't the game's language, before any of it runs."""
    for node in ast.walk(tree):
        what = _NOT_PART.get(type(node))
        if what:
            extra = (" - functions can only read globals, and every assignment makes a local"
                     if what == "global" else "")
            raise GameError(f"{what} isn't part of the game's language{extra}.", node, file)
        if isinstance(node, (ast.FunctionDef,)):
            a = node.args
            if a.vararg or a.kwarg or a.kwonlyargs or a.posonlyargs or node.decorator_list:
                raise GameError("Functions here take plain parameters only (defaults are fine).", node, file)
        if isinstance(node, ast.Call) and node.keywords:
            raise GameError("Arguments are given in order here - keyword arguments aren't part of "
                            "the game's language.", node, file)
        if isinstance(node, (ast.While, ast.For)) and node.orelse:
            raise GameError("A loop's else isn't part of the game's language.", node, file)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
            raise GameError("~ isn't part of the game's language.", node, file)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor,
                                                                ast.LShift, ast.RShift, ast.MatMult)):
            raise GameError("Bitwise operators aren't part of the game's language.", node, file)


# ── The interpreter ────────────────────────────────────────────────────

_BINOPS = {
    ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b, ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}
_SYMBOL = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//",
           ast.Mod: "%", ast.Pow: "**"}
_ORDER = {ast.Lt: lambda a, b: a < b, ast.LtE: lambda a, b: a <= b,
          ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b}


class Interp:
    def __init__(self):
        self.pending = 0
        self.modules = {}
        self.file = ""
        self.builtins = self._builtins()

    # ── Talking to the farm ─────────────────────────────────────────────

    def tick(self, n=1):
        self.pending += n
        if self.pending >= FLUSH:
            self.command("__ticks__")

    def command(self, name, *args):
        payload = {"f": name, "a": [wire(a) for a in args], "t": self.pending}
        self.pending = 0
        _out.write(MARK + json.dumps(payload) + "\n")
        _out.flush()
        line = _in.readline()
        if not line:
            os._exit(0)
        reply = json.loads(line)
        if reply.get("stop"):
            _out.flush()
            os._exit(0)
        if "e" in reply:
            raise GameError(reply["e"])
        return unwire(reply.get("r"))

    def send(self, name, *args):
        """A line that wants no answer: the program is ending."""
        _out.write(MARK + json.dumps({"f": name, "a": list(args), "t": self.pending}) + "\n")
        _out.flush()
        self.pending = 0

    # ── Built-in functions ──────────────────────────────────────────────

    def _builtins(self):
        names = {}
        for d in DIRECTIONS:
            names[d] = value(d)
        for title, members in GROUPS.items():
            names[title] = Group(title, members)
        for fname in FUNCTIONS:
            names[fname] = Builtin(fname, self._farm(fname))
        names["print"] = Builtin("print", self._printer("print"))
        names["quick_print"] = Builtin("quick_print", self._printer("quick_print"))
        names["min"] = Builtin("min", self._extreme("min"))
        names["max"] = Builtin("max", self._extreme("max"))
        names["spawn_drone"] = Builtin("spawn_drone", self._spawn)
        names["len"] = Builtin("len", self._len)
        names["range"] = Builtin("range", self._range)
        names["list"] = Builtin("list", self._make(list))
        names["set"] = Builtin("set", self._make(set))
        names["dict"] = Builtin("dict", self._make(dict))
        return names

    def _farm(self, fname):
        def call(args, node):
            return self.command(fname, *args)
        return call

    def _printer(self, fname):
        def call(args, node):
            return self.command(fname, " ".join(show(a) for a in args))
        return call

    def _extreme(self, fname):
        def call(args, node):
            if len(args) == 1 and isinstance(args[0], (list, tuple, set, range, dict)):
                return self.command(fname, list(args[0]))
            return self.command(fname, *args)
        return call

    def _len(self, args, node):
        self.tick(1)
        if len(args) != 1:
            raise GameError("len() takes one thing to measure.", node, self.file)
        try:
            return len(args[0])
        except TypeError:
            raise GameError(f"{kind(args[0])} has no length.", node, self.file) from None

    def _range(self, args, node):
        self.tick(1)
        if not 1 <= len(args) <= 3:
            raise GameError("range() takes an end, or a start and an end, and maybe a step.", node, self.file)
        whole = []
        for a in args:
            if not isinstance(a, (int, float)) or isinstance(a, bool) or int(a) != a:
                raise GameError("range() needs whole numbers.", node, self.file)
            whole.append(int(a))
        if len(whole) == 3 and whole[2] == 0:
            raise GameError("range()'s step can't be 0.", node, self.file)
        return range(*whole)

    def _make(self, maker):
        def call(args, node):
            if not args:
                self.tick(1)
                return maker()
            if len(args) != 1:
                raise GameError(f"{maker.__name__}() takes one collection.", node, self.file)
            try:
                self.tick(1 + len(args[0]))
                return maker(args[0])
            except TypeError:
                raise GameError(f"{maker.__name__}() can't be made from {kind(args[0])}.", node, self.file) from None
        return call

    def _spawn(self, args, node):
        if not args or not isinstance(args[0], Function):
            raise GameError("spawn_drone needs one of your functions, like spawn_drone(harvest_column).",
                            node, self.file)
        fn = args[0]
        module = fn.module
        if module.globals.get(fn.name) is not fn:
            raise GameError("spawn_drone needs a function defined at the top of a file.", node, self.file)
        name = fn.name if module.name == "__main__" else f"{module.name}.{fn.name}"
        snapshot = {}
        main = self.modules.get("__main__")
        if main is not None:
            for k, v in main.globals.items():
                if k.startswith("__"):
                    continue
                try:
                    json.dumps(wire(v))
                except (GameError, TypeError, ValueError):
                    continue
                if isinstance(v, (Function, Builtin, Module, Group)):
                    continue
                snapshot[k] = wire(v)
        return self.command("spawn_drone", name, [wire(a) for a in args[1:]], snapshot)

    # ── Files ───────────────────────────────────────────────────────────

    def parse(self, name):
        path = os.path.join(FILES, name + ".py")
        if not os.path.exists(path):
            raise GameError(f"There is no file called {name}.")
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        try:
            tree = ast.parse(source, filename=name + ".py")
        except SyntaxError as error:
            err = GameError(f"SyntaxError: {error.msg}", file=name)
            err.line = error.lineno or 0
            raise err from None
        check_language(tree, name)
        return tree

    def load(self, name, node=None, as_main=False, definitions_only=False):
        key = "__main__" if as_main else name
        if key in self.modules:
            return self.modules[key]
        tree = self.parse(name)
        module = Module("__main__" if as_main else name)
        module.globals["__file_name__"] = name
        self.modules[key] = module
        outer = self.file
        self.file = name
        try:
            body = tree.body
            if definitions_only:
                body = [s for s in body if isinstance(s, (ast.FunctionDef, ast.Import, ast.ImportFrom))]
            self.block(body, Frame(module))
        finally:
            self.file = outer
            module.loading = False
        return module

    # ── Statements ──────────────────────────────────────────────────────

    def block(self, body, frame):
        for stmt in body:
            self.stmt(stmt, frame)

    def stmt(self, s, frame):
        t = type(s)
        if t is ast.Expr:
            self.expr(s.value, frame)
        elif t is ast.Assign:
            v = self.expr(s.value, frame)
            for target in s.targets:
                self.assign(target, v, frame)
        elif t is ast.AugAssign:
            current = self.expr(self._as_load(s.target), frame)
            v = self.binop(s.op, current, self.expr(s.value, frame), s)
            self.assign(s.target, v, frame)
        elif t is ast.If:
            self.tick(1)
            if self.truth(self.expr(s.test, frame), s):
                self.block(s.body, frame)
            elif s.orelse:
                self.block(s.orelse, frame)
        elif t is ast.While:
            self.tick(1)
            while self.truth(self.expr(s.test, frame), s):
                try:
                    self.block(s.body, frame)
                except _Break:
                    break
                except _Continue:
                    continue
        elif t is ast.For:
            self.tick(1)
            seq = self.expr(s.iter, frame)
            for item in self.iterate(seq, s):
                self.assign(s.target, item, frame)
                try:
                    self.block(s.body, frame)
                except _Break:
                    break
                except _Continue:
                    continue
        elif t is ast.Pass:
            self.tick(1)
        elif t is ast.Break:
            raise _Break()
        elif t is ast.Continue:
            raise _Continue()
        elif t is ast.Return:
            raise _Return(None if s.value is None else self.expr(s.value, frame))
        elif t is ast.FunctionDef:
            self.tick(1)
            params = [a.arg for a in s.args.args]
            defaults = [self.expr(d, frame) for d in s.args.defaults]
            self.store(s.name, Function(s.name, params, defaults, s.body, frame.module, s), frame)
        elif t is ast.Import:
            for alias in s.names:
                if "." in alias.name:
                    raise GameError("Files have plain names here, like import utils.", s, self.file)
                module = self.load(alias.name, s)
                self.store(alias.asname or alias.name, module, frame)
        elif t is ast.ImportFrom:
            if s.level or not s.module or "." in s.module:
                raise GameError("Files have plain names here, like from utils import f.", s, self.file)
            module = self.load(s.module, s)
            for alias in s.names:
                if alias.name == "*":
                    for k, v in list(module.globals.items()):
                        if not k.startswith("__"):
                            self.store(k, v, frame)
                elif alias.name in module.globals:
                    self.store(alias.asname or alias.name, module.globals[alias.name], frame)
                else:
                    raise GameError(f"{s.module} has no {alias.name}.", s, self.file)
        else:
            raise GameError(f"{type(s).__name__} isn't part of the game's language.", s, self.file)

    @staticmethod
    def _as_load(target):
        if isinstance(target, ast.Name):
            return ast.Name(id=target.id, ctx=ast.Load(), lineno=target.lineno)
        if isinstance(target, ast.Subscript):
            return ast.Subscript(value=target.value, slice=target.slice, ctx=ast.Load(), lineno=target.lineno)
        if isinstance(target, ast.Attribute):
            return ast.Attribute(value=target.value, attr=target.attr, ctx=ast.Load(), lineno=target.lineno)
        raise GameError("That can't be changed with an operator and =.", target)

    def store(self, name, v, frame):
        if frame.locals is not None:
            frame.locals[name] = v
        else:
            frame.module.globals[name] = v

    def assign(self, target, v, frame):
        t = type(target)
        if t is ast.Name:
            self.store(target.id, v, frame)
        elif t in (ast.Tuple, ast.List):
            items = list(self.iterate(v, target))
            if len(items) != len(target.elts):
                raise GameError(f"{len(target.elts)} names, but {len(items)} values to unpack.", target, self.file)
            for sub, item in zip(target.elts, items):
                self.assign(sub, item, frame)
        elif t is ast.Subscript:
            container = self.expr(target.value, frame)
            if isinstance(target.slice, ast.Slice):
                raise GameError("Slices can be read but not assigned to.", target, self.file)
            key = self.expr(target.slice, frame)
            if isinstance(container, list):
                self.tick(1)
                container[self.index(key, container, target)] = v
            elif isinstance(container, dict):
                self.tick(key_cost(key))
                self.hashable(key, target)
                container[key] = v
            elif isinstance(container, tuple):
                raise GameError("Tuples can't be changed once made.", target, self.file)
            else:
                raise GameError(f"{kind(container)} can't be changed with [ ].", target, self.file)
        elif t is ast.Attribute:
            owner = self.expr(target.value, frame)
            if isinstance(owner, Module):
                owner.globals[target.attr] = v
            else:
                raise GameError(f"{kind(owner)} has no {target.attr} to set.", target, self.file)
        else:
            raise GameError("That can't be assigned to.", target, self.file)

    # ── Expressions ─────────────────────────────────────────────────────

    def truth(self, v, node):
        return bool(v)

    def lookup(self, name, frame, node):
        if frame.locals is not None and name in frame.locals:
            return frame.locals[name]
        g = frame.module.globals
        if name in g:
            return g[name]
        if name in self.builtins:
            return self.builtins[name]
        raise GameError(f"{name} isn't defined.", node, self.file)

    def expr(self, e, frame):
        t = type(e)
        if t is ast.Constant:
            if isinstance(e.value, (bytes, complex)) or e.value is Ellipsis:
                raise GameError("That kind of value isn't part of the game's language.", e, self.file)
            return e.value
        if t is ast.Name:
            return self.lookup(e.id, frame, e)
        if t is ast.BinOp:
            return self.binop(e.op, self.expr(e.left, frame), self.expr(e.right, frame), e)
        if t is ast.UnaryOp:
            v = self.expr(e.operand, frame)
            if isinstance(e.op, ast.Not):
                return not v
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                raise GameError(f"Only numbers have a sign, not {kind(v)}.", e, self.file)
            return -v if isinstance(e.op, ast.USub) else +v
        if t is ast.BoolOp:
            is_and = isinstance(e.op, ast.And)
            v = self.expr(e.values[0], frame)
            for nxt in e.values[1:]:
                self.tick(1)
                if is_and and not v:
                    return v
                if not is_and and v:
                    return v
                v = self.expr(nxt, frame)
            return v
        if t is ast.Compare:
            left = self.expr(e.left, frame)
            for op, right_node in zip(e.ops, e.comparators):
                right = self.expr(right_node, frame)
                if not self.compare(op, left, right, e):
                    return False
                left = right
            return True
        if t is ast.Call:
            return self.call(e, frame)
        if t is ast.Attribute:
            owner = self.expr(e.value, frame)
            if isinstance(owner, Group):
                if e.attr in owner.members:
                    return owner.members[e.attr]
                raise GameError(f"There is no {owner.title}.{e.attr}.", e, self.file)
            if isinstance(owner, Module):
                if e.attr in owner.globals:
                    return owner.globals[e.attr]
                raise GameError(f"{owner.name} has no {e.attr}.", e, self.file)
            raise GameError(f"{kind(owner)} has no {e.attr}.", e, self.file)
        if t is ast.Subscript:
            container = self.expr(e.value, frame)
            if isinstance(e.slice, ast.Slice):
                return self.slice(container, e.slice, frame, e)
            key = self.expr(e.slice, frame)
            if isinstance(container, (list, tuple, str)):
                self.tick(1)
                return container[self.index(key, container, e)]
            if isinstance(container, dict):
                self.tick(key_cost(key))
                self.hashable(key, e)
                if key not in container:
                    raise GameError(f"{show(key, True)} isn't a key of this dictionary.", e, self.file)
                return container[key]
            raise GameError(f"{kind(container)} can't be indexed with [ ].", e, self.file)
        if t is ast.List:
            items = [self.expr(x, frame) for x in e.elts]
            self.tick(len(items) or 1)
            return items
        if t is ast.Tuple:
            items = tuple(self.expr(x, frame) for x in e.elts)
            self.tick(1)
            return items
        if t is ast.Dict:
            out = {}
            for k_node, v_node in zip(e.keys, e.values):
                if k_node is None:
                    raise GameError("** isn't part of the game's language.", e, self.file)
                k = self.expr(k_node, frame)
                self.hashable(k, e)
                out[k] = self.expr(v_node, frame)
            self.tick(1 + len(e.keys))
            return out
        if t is ast.Set:
            out = set()
            for x in e.elts:
                v = self.expr(x, frame)
                self.hashable(v, e)
                out.add(v)
            self.tick(1 + len(e.elts))
            return out
        if t is ast.IfExp:
            self.tick(1)
            return self.expr(e.body if self.truth(self.expr(e.test, frame), e) else e.orelse, frame)
        raise GameError(f"{type(e).__name__} isn't part of the game's language.", e, self.file)

    def hashable(self, k, node):
        try:
            hash(k)
        except TypeError:
            raise GameError(f"{kind(k)} can't be a dictionary key or set member - a tuple can.",
                            node, self.file) from None

    def index(self, key, container, node):
        if isinstance(key, bool) or not isinstance(key, (int, float)) or int(key) != key:
            raise GameError(f"A list is indexed by a whole number, not {kind(key)}.", node, self.file)
        i = int(key)
        if not -len(container) <= i < len(container):
            raise GameError(f"Index {i} is outside a {len(container)}-long {kind(container)[2:]}.",
                            node, self.file)
        return i

    def slice(self, container, sl, frame, node):
        if not isinstance(container, (list, tuple, str)):
            raise GameError(f"{kind(container)} can't be sliced.", node, self.file)
        parts = []
        for part in (sl.lower, sl.upper, sl.step):
            v = None if part is None else self.expr(part, frame)
            if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or int(v) != v):
                raise GameError("A slice needs whole numbers.", node, self.file)
            parts.append(None if v is None else int(v))
        if parts[2] == 0:
            raise GameError("A slice's step can't be 0.", node, self.file)
        out = container[slice(*parts)]
        self.tick(1 + len(out))
        return out

    def binop(self, op, a, b, node):
        t = type(op)
        if t is ast.Add and isinstance(a, (list, str, tuple)) and type(a) is type(b):
            self.tick(len(a) + len(b))
            return a + b
        self.tick(1)
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b)):
            if t is ast.Mult and isinstance(a, (str, list)) and isinstance(b, int) and not isinstance(b, bool):
                return a * b
            raise GameError(f"Can't {_SYMBOL[t]} {kind(a)} and {kind(b)}.", node, self.file)
        try:
            return _BINOPS[t](a, b)
        except ZeroDivisionError:
            raise GameError("Division by zero.", node, self.file) from None
        except OverflowError:
            raise GameError("That number is too big.", node, self.file) from None

    def compare(self, op, a, b, node):
        t = type(op)
        if t in (ast.In, ast.NotIn):
            if not isinstance(b, (list, tuple, dict, set, frozenset, str, range)):
                raise GameError(f"Can't look inside {kind(b)} with in.", node, self.file)
            self.tick(contains_cost(a, b))
            if isinstance(b, (dict, set, frozenset)):
                self.hashable(a, node)
            found = a in b
            return found if t is ast.In else not found
        if t in (ast.Is, ast.IsNot):
            self.tick(1)
            same = a is b or (a is None and b is None)
            return same if t is ast.Is else not same
        self.tick(compare_cost(a, b))
        if t is ast.Eq:
            return a == b
        if t is ast.NotEq:
            return a != b
        numbers = all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b))
        if not numbers:
            raise GameError(f"<, >, <= and >= compare numbers, not {kind(a)} and {kind(b)}.", node, self.file)
        return _ORDER[t](a, b)

    def iterate(self, seq, node):
        if isinstance(seq, (list, tuple, range, str)):
            return list(seq) if isinstance(seq, list) else seq
        if isinstance(seq, (dict, set, frozenset)):
            return list(seq)
        raise GameError(f"Can't go through {kind(seq)} with for.", node, self.file)

    # ── Calls ───────────────────────────────────────────────────────────

    def call(self, e, frame):
        func_node = e.func
        if isinstance(func_node, ast.Attribute):
            owner = self.expr(func_node.value, frame)
            if isinstance(owner, (list, dict, set)):
                args = [self.expr(a, frame) for a in e.args]
                return self.method(owner, func_node.attr, args, e)
            f = self.expr(func_node, frame) if not isinstance(owner, (Group, Module)) else (
                owner.members.get(func_node.attr) if isinstance(owner, Group) else
                owner.globals.get(func_node.attr))
            if f is None:
                raise GameError(f"{show(owner)} has no {func_node.attr}.", e, self.file)
        else:
            f = self.expr(func_node, frame)
        args = [self.expr(a, frame) for a in e.args]
        if isinstance(f, Builtin):
            try:
                return f.impl(args, e)
            except GameError as error:
                if not error.line:
                    error.line = e.lineno
                    error.file = self.file
                raise
        if isinstance(f, Function):
            direct = isinstance(func_node, ast.Name) and func_node.id == f.name
            direct = direct or (isinstance(func_node, ast.Attribute) and func_node.attr == f.name)
            if not direct:
                self.tick(1)
            return self.run_function(f, args, e)
        raise GameError(f"{show(f)} can't be called.", e, self.file)

    def run_function(self, f, args, node):
        n, given = len(f.params), len(args)
        first_default = n - len(f.defaults)
        if not first_default <= given <= n:
            want = str(n) if not f.defaults else f"{first_default} to {n}"
            raise GameError(f"{f.name}() takes {want} arguments, not {given}.", node, self.file)
        local = dict(zip(f.params, args))
        for i in range(given, n):
            local[f.params[i]] = f.defaults[i - first_default]
        outer = self.file
        self.file = f.module.globals.get("__file_name__", outer)
        try:
            self.block(f.body, Frame(f.module, local))
        except _Return as r:
            return r.value
        except (_Break, _Continue):
            raise GameError("break and continue belong inside a loop.", node, self.file) from None
        finally:
            self.file = outer
        return None

    def method(self, owner, name, args, node):
        try:
            if isinstance(owner, list):
                if name == "append" and len(args) == 1:
                    self.tick(1)
                    owner.append(args[0])
                    return None
                if name == "pop" and len(args) <= 1:
                    if not owner:
                        raise GameError("pop() from an empty list.", node, self.file)
                    i = self.index(args[0], owner, node) if args else len(owner) - 1
                    self.tick(max(1, len(owner) - i))
                    return owner.pop(i)
                if name == "insert" and len(args) == 2:
                    i = self.index(args[0], owner + [None], node) if owner else 0
                    self.tick(1 + len(owner) - i)
                    owner.insert(i, args[1])
                    return None
                if name == "remove" and len(args) == 1:
                    self.tick(max(1, len(owner)))
                    if args[0] not in owner:
                        raise GameError(f"{show(args[0], True)} isn't in the list.", node, self.file)
                    owner.remove(args[0])
                    return None
            elif isinstance(owner, dict):
                if name == "pop" and len(args) == 1:
                    self.tick(key_cost(args[0]))
                    if args[0] not in owner:
                        raise GameError(f"{show(args[0], True)} isn't a key of this dictionary.", node, self.file)
                    return owner.pop(args[0])
            elif isinstance(owner, set):
                if name == "add" and len(args) == 1:
                    self.hashable(args[0], node)
                    self.tick(key_cost(args[0]))
                    owner.add(args[0])
                    return None
                if name == "remove" and len(args) == 1:
                    self.tick(key_cost(args[0]))
                    if args[0] not in owner:
                        raise GameError(f"{show(args[0], True)} isn't in the set.", node, self.file)
                    owner.remove(args[0])
                    return None
        except TypeError:
            raise GameError(f"That doesn't work on {kind(owner)}.", node, self.file) from None
        known = {list: "append, pop, insert and remove", dict: "pop", set: "add and remove"}[type(owner)]
        raise GameError(f"{kind(owner)} has no {name}() here - the game's {kind(owner)[2:]}s have {known}.",
                        node, self.file)


# ── Running a program ──────────────────────────────────────────────────

def _report(error, interp):
    if isinstance(error, GameError):
        message, line, file = error.message, error.line, error.file or interp.file
    elif isinstance(error, RecursionError):
        message, line, file = "Too many calls inside calls - is a function calling itself for ever?", 0, interp.file
    else:
        message, line, file = f"{type(error).__name__}: {error}", 0, interp.file
    try:
        interp.send("__error__", message, line, file)
    except OSError:
        pass


def main(entry):
    sys.setrecursionlimit(4000)
    interp = Interp()
    job = os.environ.get("FARM_DRONE")
    try:
        if job:
            spec = json.loads(job)
            module = interp.load(entry, as_main=True, definitions_only=True)
            for k, v in (spec.get("globals") or {}).items():
                module.globals[k] = unwire(v)
            name = spec.get("fn", "")
            owner, _, fname = name.rpartition(".")
            source = interp.load(owner) if owner else module
            fn = source.globals.get(fname)
            if not isinstance(fn, Function):
                raise GameError(f"There is no function {name} to run on this drone.")
            args = [unwire(a) if not isinstance(a, list) else list(unwire(a)) for a in spec.get("args") or []]
            result = interp.run_function(fn, args, fn.node)
            interp.send("__return__", wire(result))
            return 0
        interp.load(entry, as_main=True)
        if interp.pending:
            interp.command("__ticks__")
        return 0
    except BaseException as error:  # noqa: BLE001 - every crash is reported, with its line
        if isinstance(error, SystemExit):
            raise
        _report(error, interp)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "main"))
