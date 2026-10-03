"""The farm's commands, for a Python program.

Run as:  python -u farm_api.py <your file>

Every command writes one line to the farm and waits for one line back (see
code_coach/farm/protocol.py). The names, values and defaults are the
game's own: move(North), plant(Entities.Bush), num_items(Items.Hay).

The block between the NAMES markers is filled in by the runner from
code_coach/farm/data.py, so the values here can never drift from the farm.
"""

import json
import os
import sys

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


def _unwire(value):
    if isinstance(value, str) and (value in DIRECTIONS or value.split(".", 1)[0] in GROUPS):
        return _value(value)
    if isinstance(value, list):
        return tuple(_unwire(v) for v in value)
    if isinstance(value, dict):
        return {_unwire(k): _unwire(v) for k, v in value.items()}
    return value


def _call(name, *args):
    _out.write(MARK + json.dumps({"f": name, "a": [_wire(a) for a in args]}) + "\n")
    _out.flush()
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
    names["FarmError"] = FarmError
    names["input"] = _no_keyboard
    return names


def _no_keyboard(*_args):
    # The farm's answers arrive on stdin; a program reading it would eat them.
    raise FarmError("There is no keyboard on the farm: input() can't be used here.")


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
        _out.write(MARK + json.dumps({"f": "__error__", "a": [message, line]}) + "\n")
        _out.flush()
    except OSError:
        pass


def main(path):
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    code_name = "farm.py"
    namespace = {"__name__": "__main__"}
    namespace.update(_api())
    try:
        exec(compile(source, code_name, "exec"), namespace)
    except SystemExit:
        raise
    except BaseException as error:  # noqa: BLE001 - every crash is reported
        _crash(error, code_name)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
