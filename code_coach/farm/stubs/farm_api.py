"""The farm's commands, for a Python program.

Run as:  python -u farm_api.py <your file>

Every command writes one line to the farm and waits for one line back (see
code_coach/farm/protocol.py). The names, values and defaults are the
game's own: move(North), plant(Entities.Bush), num_items(Items.Hay).

The block between the NAMES markers is filled in by the runner from
code_coach/farm/data.py, so the values here can never drift from the farm.

More drones: spawn_drone(f) starts a new run of this same file in drone
mode (FARM_DRONE holds the job). That run defines your functions, classes
and imports without running anything else at the top level, takes a copy
of the globals you had when you spawned it, runs f, and sends back what f
returned.
"""

import ast
import json
import os
import sys
import types

MARK = "\x1eCC"

# NAMES-START
DIRECTIONS = ["North", "East", "South", "West"]
GROUPS = {"Entities": [], "Items": [], "Grounds": [], "Unlocks": [], "Hats": []}
FUNCTIONS = []
# NAMES-END

_out = sys.stdout
_in = sys.stdin


class FarmError(Exception):
    """The farm said no: a command that is not unlocked, or used wrongly."""


class _Value:
    """One of the game's named values - North, Entities.Bush, Items.Hay."""

    __slots__ = ("name",)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    __str__ = __repr__

    def __eq__(self, other):
        return isinstance(other, _Value) and other.name == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)


_VALUES = {}


def _value(name):
    if name not in _VALUES:
        _VALUES[name] = _Value(name)
    return _VALUES[name]


class _Group:
    """Entities, Items, ...: a namespace of values, like the game's."""

    def __init__(self, title, members):
        self._title = title
        for member in members:
            setattr(self, member, _value(title + "." + member))

    def __repr__(self):
        return self._title

    def __iter__(self):
        return iter([v for k, v in vars(self).items() if not k.startswith("_")])


def _wire(value):
    if isinstance(value, _Value):
        return value.name
    if isinstance(value, (list, tuple)):
        return [_wire(v) for v in value]
    if isinstance(value, dict):
        return {str(_wire(k)): _wire(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return [_wire(v) for v in value]
    return value


def _unwire(value, sequence=tuple):
    """A value from the pipe as Python's own: a name back to its value, and a
    list as a tuple - the farm's lists are the game's tuples. A drone's
    arguments and globals were your own lists, so they come back as lists."""
    if isinstance(value, str) and (value in DIRECTIONS or value.split(".", 1)[0] in GROUPS):
        return _value(value)
    if isinstance(value, list):
        return sequence(_unwire(v, sequence) for v in value)
    if isinstance(value, dict):
        return {_unwire(k, sequence): _unwire(v, sequence) for k, v in value.items()}
    return value


#: What _travels says about a value that cannot go down the pipe.
_NO = object()


def _travels(value):
    """The value as it goes down the pipe, or _NO if it can't go: a function,
    a module or an object of your own has no form there."""
    try:
        wired = _wire(value)
        json.dumps(wired)
    except (TypeError, ValueError, RecursionError):
        return _NO
    return wired


def _send(name, *args):
    """One line to the farm, without waiting for an answer."""
    _out.write(MARK + json.dumps({"f": name, "a": [_wire(a) for a in args]}) + "\n")
    _out.flush()


def _call(name, *args):
    _send(name, *args)
    line = _in.readline()
    if not line:
        os._exit(0)
    reply = json.loads(line)
    if reply.get("stop"):
        _out.flush()
        os._exit(0)
    if "e" in reply:
        raise FarmError(reply["e"])
    return _unwire(reply.get("r"))


def _command(name):
    def command(*args):
        return _call(name, *args)

    command.__name__ = name
    return command


def _printer(name):
    def printer(*values, sep=" ", end=""):
        return _call(name, sep.join(str(v) for v in values))

    printer.__name__ = name
    return printer


def _extreme(name):
    """min and max: of several values, or of one list (or range, or generator)."""

    def extreme(*values):
        if len(values) == 1 and not isinstance(values[0], (str, bytes, dict, _Value)):
            try:
                return _call(name, list(values[0]))
            except TypeError:
                pass
        return _call(name, *values)

    extreme.__name__ = name
    return extreme


def _api():
    names = {}
    for d in DIRECTIONS:
        names[d] = _value(d)
    for title, members in GROUPS.items():
        names[title] = _Group(title, members)
    for name in FUNCTIONS:
        names[name] = _command(name)
    names["min"] = _extreme("min")
    names["max"] = _extreme("max")
    names["print"] = _printer("print")
    names["quick_print"] = _printer("quick_print")
    names["spawn_drone"] = spawn_drone
    names["FarmError"] = FarmError
    names["input"] = _no_keyboard
    return names


def _no_keyboard(*_args):
    # The farm's answers arrive on stdin; a program reading it would eat them.
    raise FarmError("There is no keyboard on the farm: input() can't be used here.")


# ── More drones ─────────────────────────────────────────────────────────

#: The program main() is running: its namespace, the names _api() put in
#: it, and its source. spawn_drone reads all three.
_program = {"namespace": {}, "api": {}, "source": "", "functions": None}

#: What a drone keeps of your file: the definitions, not the statements.
_DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)


def _top_level_functions():
    """The names of the functions your file defines at its top level - the
    ones a drone, which runs only the definitions, will have."""
    if _program["functions"] is None:
        body = ast.parse(_program["source"], "farm.py").body
        _program["functions"] = {
            node.name for node in body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
    return _program["functions"]


def _globals_snapshot():
    """Your globals as they are now - the ones that can go down the pipe:
    numbers, text, lists, dictionaries and the game's values. The farm's
    own names stay behind (the drone has its own), and so do functions,
    classes and modules (the drone defines its own from your file)."""
    api = _program["api"]
    snapshot = {}
    for name, value in list(_program["namespace"].items()):
        if name.startswith("__") and name.endswith("__"):
            continue
        if name in api and api[name] is value:
            continue
        if callable(value) or isinstance(value, types.ModuleType):
            continue
        wired = _travels(value)
        if wired is not _NO:
            snapshot[name] = wired
    return snapshot


def spawn_drone(function, *args):
    """Start another drone here, running function(*args): its handle, or None
    if every drone is already out.

    The new drone is a new run of your file that runs only that function,
    so it is sent by name - which is why it has to be one your program
    defines at the top level, where the new run will find it again. It
    starts with a copy of your globals as they are now; a tuple or a set
    among them arrives as a list.
    """
    name = getattr(function, "__name__", None)
    if not (isinstance(function, types.FunctionType)
            and function.__qualname__ == name
            and _program["namespace"].get(name) is function
            and name in _top_level_functions()):
        raise FarmError("spawn_drone needs a function defined at the top level of your program, "
                        "like def harvest_column():")
    sent = _travels(list(args))
    if sent is _NO:
        raise FarmError("spawn_drone can only hand a drone numbers, text, lists, dictionaries "
                        "and the game's values.")
    return _call("spawn_drone", name, sent, _globals_snapshot())


def _run_drone(job, source, code_name, namespace):
    """Drone mode: define your functions without running the rest of your
    file, take the globals the spawning drone had, run the one function,
    and send back what it returned. The farm answers nothing to that."""
    tree = ast.parse(source, code_name)
    tree.body = [node for node in tree.body if isinstance(node, _DEFINITIONS)]
    given = {name: _unwire(value, list) for name, value in job.get("globals", {}).items()}
    # Before the definitions, for a default value or a class body that reads
    # a global; after them, so a global wins over a definition, as it had.
    namespace.update(given)
    exec(compile(tree, code_name, "exec"), namespace)
    namespace.update(given)
    name = job.get("fn")
    function = namespace.get(name)
    if not isinstance(function, types.FunctionType):
        raise FarmError(f"This drone was to run {name}(), but your program defines no function "
                        "of that name at its top level.")
    value = function(*[_unwire(arg, list) for arg in job.get("args", [])])
    wired = _travels(value)
    if wired is _NO:
        raise FarmError(f"{name}() returned a {type(value).__name__}, which a drone can't hand "
                        "back: return numbers, text, lists, dictionaries or the game's values.")
    _send("__return__", wired)


def _crash(error, code_name):
    """Tell the farm what went wrong and on which of your lines."""
    line = 0
    tb = error.__traceback__
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == code_name:
            line = tb.tb_lineno
        tb = tb.tb_next
    if isinstance(error, SyntaxError) and error.filename == code_name:
        line = error.lineno or 0
    message = str(error) if isinstance(error, FarmError) else f"{type(error).__name__}: {error}"
    try:
        _send("__error__", message, line)
    except OSError:
        pass


def main(path):
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    code_name = "farm.py"
    namespace = {"__name__": "__main__"}
    api = _api()
    namespace.update(api)
    _program.update(namespace=namespace, api=api, source=source)
    job = os.environ.get("FARM_DRONE")
    try:
        if job:
            _run_drone(json.loads(job), source, code_name, namespace)
        else:
            exec(compile(source, code_name, "exec"), namespace)
    except SystemExit:
        raise
    except BaseException as error:  # noqa: BLE001 - every crash is reported
        _crash(error, code_name)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
