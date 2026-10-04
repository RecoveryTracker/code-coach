"""The farm's commands, for a Python program.

Run as:  python -u farm/farm_api.py <the file to run, by name>

Your program is one or more files - main.py, utils.py ... - in the folder
above this one, and it runs from the one named on the command line. This
library sits a folder down so that no file of yours can stand in for a
module it imports itself: a json.py or a random.py of yours is yours alone.

Every command writes one line to the farm and waits for one line back (see
code_coach/farm/protocol.py). The names, values and defaults are the
game's own: move(North), plant(Entities.Bush), num_items(Items.Hay).

Your files import each other as Python files do - import utils, from utils
import harvest_column, import utils as u - and each runs its top level
once, the first time it is imported. The farm's names are builtins in every
one of them, as print and range are, so no file has to import them. When a
file of yours imports a name, the file of yours by that name comes first;
anything else is Python's own import. The file you run is __main__, as a
script is.

The block between the NAMES markers is filled in by the runner from
code_coach/farm/data.py, so the values here can never drift from the farm.

More drones: spawn_drone(f) starts a new run of this same program in drone
mode (FARM_DRONE holds the job). That run defines the functions, classes
and imports of the file you run without running anything else at its top
level - a file it imports runs as any import does - takes a copy of the
globals you had when you spawned it, runs f, and sends back what f
returned.

Simulation: simulate(filename, sim_unlocks, sim_items, sim_globals, seed,
speedup) runs one of your files as a new program on a fresh farm of its
own, and answers with the game seconds it took. A whole group stands for
all of its values - simulate("f1", Unlocks, ...) is every unlock - and so
does a list of them, or a dictionary of levels, {Unlocks.Speed: 2}. The
new program is an ordinary run of that file, not a drone: FARM_GLOBALS
holds the globals it was given, and they are its globals before its first
line runs.
"""

import ast
import builtins
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

#: Python's own import, for every module that is not a file of yours.
_python_import = builtins.__import__

#: Python's own modules, by name. A file of yours is a module everywhere
#: when its name is free; with one of these names it is yours alone, so
#: that Python's own code still finds Python's own module.
_STDLIB = frozenset(getattr(sys, "stdlib_module_names", ()))


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
    if isinstance(value, _Group):
        # A whole group is all of its values, as the game reads it:
        # simulate("f1", Unlocks, ...) is every unlock there is.
        return [v.name for v in value]
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


# ── Your files ──────────────────────────────────────────────────────────

_FIRST = "abcdefghijklmnopqrstuvwxyz_"
_REST = _FIRST + "0123456789"


def _is_file_name(name):
    """What a file of yours can be called: lowercase letters, digits and _,
    not starting with a digit (render.FILE_NAME, without needing re)."""
    return bool(name) and name[0] in _FIRST and all(c in _REST for c in name)


class _Program:
    """Your program: its files, the one that runs, and a module for each
    file once it has been imported."""

    def __init__(self, folder, entry):
        self.folder = folder
        self.entry = entry
        #: Each of your files, by name: where it is.
        self.paths = {}
        for found in sorted(os.listdir(folder)):
            name, extension = os.path.splitext(found)
            if extension == ".py" and _is_file_name(name):
                self.paths[name] = os.path.join(folder, found)
        #: ... and the other way round: which file of yours a path is.
        self.names = {path: name for name, path in self.paths.items()}
        #: Your files imported so far, by name, as sys.modules is for the rest.
        self.modules = {}
        #: The builtins of every file of yours: Python's, the farm's names,
        #: and an import that looks among your files first.
        self.api = _api()
        self.builtins = dict(vars(builtins))
        self.builtins.update(self.api)
        self.builtins["__import__"] = self._import
        #: The file you run, as Python runs a script: __main__.
        self.main = self._module(entry, "__main__")
        self.source = self.read(entry) if entry in self.paths else ""
        self._top_level = None

    def read(self, name):
        with open(self.paths[name], encoding="utf-8") as handle:
            return handle.read()

    def compile(self, name, source=None):
        """Your file as code, under its own path - so a traceback names the
        file and the line, and a SyntaxError says (utils.py, line 3)."""
        return compile(self.read(name) if source is None else source, self.paths[name], "exec",
                       dont_inherit=True)

    def _module(self, name, module_name):
        module = types.ModuleType(module_name)
        module.__file__ = self.paths.get(name, os.path.join(self.folder, name + ".py"))
        module.__package__ = ""
        module.__builtins__ = self.builtins
        return module

    def load(self, name):
        """Your file `name` as a module: run the first time it is imported,
        as Python does, and the same module every time after - even while it
        is still running, so two files can import each other."""
        module = self.modules.get(name)
        if module is not None:
            return module
        module = self._module(name, name)
        self.modules[name] = module
        shared = name not in sys.modules and name not in _STDLIB
        if shared:
            sys.modules[name] = module
        try:
            exec(self.compile(name), vars(module))
        except BaseException:
            # A file that failed to run has not been imported: the next
            # import tries it again, as in Python.
            if self.modules.get(name) is module:
                del self.modules[name]
            if shared and sys.modules.get(name) is module:
                del sys.modules[name]
            raise
        return module

    def _import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """import, in a file of yours: a file of yours by that name, or else
        Python's own import."""
        top, dot, _rest = name.partition(".")
        if level == 0 and top in self.paths:
            module = self.load(top)
            if dot:
                raise ModuleNotFoundError(f"No module named {name!r}; {top!r} is not a package",
                                          name=name)
            return module
        return _python_import(name, globals, locals, fromlist, level)

    def top_level(self):
        """The names the file you run gives functions at its top level: the
        ones it defines with def, and the ones it imports by name - the
        names a drone, which runs only its definitions and imports, has too."""
        if self._top_level is None:
            defined, imported = set(), set()
            for node in ast.parse(self.source, self.paths[self.entry]).body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defined.add(node.name)
                elif isinstance(node, ast.ImportFrom):
                    imported.update(alias.asname or alias.name for alias in node.names)
            self._top_level = defined, imported
        return self._top_level

    def drone_name(self, function):
        """How a new drone finds this function again: by its name, when the
        file you run has it under that name (it defines it, or imports it by
        name); otherwise as utils.harvest_column, by the file of yours that
        defines it. None if a drone can't find it again - anything but a
        function defined at the top level of a file of yours."""
        if not isinstance(function, types.FunctionType):
            return None
        name = function.__name__
        if function.__qualname__ != name:
            return None
        main = vars(self.main)
        defined, imported = self.top_level()
        home = function.__globals__  # the module it was defined in
        if home is main:
            return name if main.get(name) is function and name in defined else None
        file = next((file for file, module in self.modules.items() if vars(module) is home), None)
        if file is None or home.get(name) is not function:
            return None
        if main.get(name) is function and name in imported:
            return name
        return f"{file}.{name}"

    def drone_function(self, sent):
        """The function a drone was sent to run, by the name drone_name()
        gave it, or None."""
        file, dot, name = sent.rpartition(".")
        if not dot:
            return vars(self.main).get(name)
        if file not in self.paths:
            return None
        return vars(self.load(file)).get(name)

    def tidy(self, message):
        """A message without the folder your files are in: (utils.py), not
        (C:\\...\\utils.py)."""
        return message.replace(self.folder + os.sep, "")


#: The program that is running.
_program = None


# ── More drones ─────────────────────────────────────────────────────────

#: What a drone keeps of the file you run: the definitions, not the statements.
_DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)


def _globals_snapshot():
    """The globals of the file you run as they are now - the ones that can
    go down the pipe: numbers, text, lists, dictionaries and the game's
    values. The farm's own names stay behind (the drone has its own), and so
    does a group of them under a name of yours - it would arrive as a plain
    list - and so do functions, classes and modules (the drone defines its
    own from your files)."""
    api = _program.api
    snapshot = {}
    for name, value in list(vars(_program.main).items()):
        if name.startswith("__") and name.endswith("__"):
            continue
        if name in api and api[name] is value:
            continue
        if callable(value) or isinstance(value, (types.ModuleType, _Group)):
            continue
        wired = _travels(value)
        if wired is not _NO:
            snapshot[name] = wired
    return snapshot


def spawn_drone(function, *args):
    """Start another drone here, running function(*args): its handle, or None
    if every drone is already out.

    The new drone is a new run of your program that runs only that
    function, so it is sent by name - which is why it has to be one defined
    at the top level of a file of yours, where the new run will find it
    again. It starts with a copy of your globals as they are now; a tuple
    or a set among them arrives as a list.
    """
    name = _program.drone_name(function) if _program is not None else None
    if name is None:
        raise FarmError("spawn_drone needs a function defined at the top level of your program, "
                        "like def harvest_column():")
    sent = _travels(list(args))
    if sent is _NO:
        raise FarmError("spawn_drone can only hand a drone numbers, text, lists, dictionaries "
                        "and the game's values.")
    return _call("spawn_drone", name, sent, _globals_snapshot())


def _run_drone(job, program):
    """Drone mode: define the functions of the file you run, and do its
    imports, without running the rest of it; take the globals the spawning
    drone had, run the one function, and send back what it returned. The
    farm answers nothing to that."""
    path = program.paths[program.entry]
    tree = ast.parse(program.source, path)
    tree.body = [node for node in tree.body if isinstance(node, _DEFINITIONS)]
    namespace = vars(program.main)
    given = {name: _unwire(value, list) for name, value in job.get("globals", {}).items()}
    # Before the definitions, for a default value or a class body that reads
    # a global; after them, so a global wins over a definition, as it had.
    namespace.update(given)
    exec(compile(tree, path, "exec", dont_inherit=True), namespace)
    namespace.update(given)
    name = str(job.get("fn"))
    function = program.drone_function(name)
    if not isinstance(function, types.FunctionType):
        raise FarmError(f"This drone was to run {name}(), but your program defines no function "
                        "of that name at its top level.")
    value = function(*[_unwire(arg, list) for arg in job.get("args", [])])
    wired = _travels(value)
    if wired is _NO:
        raise FarmError(f"{name}() returned a {type(value).__name__}, which a drone can't hand "
                        "back: return numbers, text, lists, dictionaries or the game's values.")
    _send("__return__", wired)


# ── Running your program ────────────────────────────────────────────────


def _starting_globals():
    """The globals simulate() gave this run - FARM_GLOBALS holds them as
    they went down the pipe - as your own values again: a name back to its
    value, a list still a list. None of Python's own __names__, as a drone's
    globals have none. Empty when this run is not a simulation."""
    text = os.environ.get("FARM_GLOBALS")
    if not text:
        return {}
    given = json.loads(text)
    if not isinstance(given, dict):
        raise FarmError("The farm sent this simulation its globals as something other than a dictionary.")
    return {name: _unwire(value, list) for name, value in given.items()
            if not (name.startswith("__") and name.endswith("__"))}


def _crash(error, program):
    """Tell the farm what went wrong, in which file of yours and on which
    line: the deepest place in the traceback that is in a file of yours."""
    names = program.names if program is not None else {}
    line, file = 0, ""
    tb = error.__traceback__
    while tb is not None:
        found = names.get(tb.tb_frame.f_code.co_filename)
        if found is not None:
            line, file = tb.tb_lineno or 0, found
        tb = tb.tb_next
    if isinstance(error, SyntaxError) and error.filename in names:
        line, file = error.lineno or 0, names[error.filename]
    message = str(error) if isinstance(error, FarmError) else f"{type(error).__name__}: {error}"
    if program is not None:
        message = program.tidy(message)
    try:
        _send("__error__", message, line, file)
    except OSError:
        pass


def main(entry):
    global _program
    folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    program = None
    try:
        program = _Program(folder, entry)
        if entry not in program.paths:
            raise FarmError(f"There is no file called {entry} to run.")
        _program = program
        # The file you run is the program's __main__, as a script is.
        sys.modules["__main__"] = program.main
        job = os.environ.get("FARM_DRONE")
        if job:
            # A drone's globals are the ones it was spawned with, a
            # simulation's starting ones among them.
            _run_drone(json.loads(job), program)
        else:
            vars(program.main).update(_starting_globals())
            exec(program.compile(entry, program.source), vars(program.main))
    except SystemExit:
        raise
    except BaseException as error:  # noqa: BLE001 - every crash is reported
        _crash(error, program)
        sys.exit(1)


if __name__ == "__main__":
    #: This library, kept: the file you run takes its place as __main__.
    _library = sys.modules[__name__]
    main(sys.argv[1] if len(sys.argv) > 1 else "main")
