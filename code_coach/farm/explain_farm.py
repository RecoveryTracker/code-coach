"""Plain-English walkthrough of a program in The Farmer Was Replaced's own language.

The game's language is Python's syntax with a drone's commands in it, so
this reads the program with Python's `ast` and says what each line does -
the way `explain.py` does for Python - but it knows the farm: `move(North)`
is a step across the field, `harvest()` cuts a plant, and `range(get_world_size())`
is a walk along one side of the field.

Three things keep it honest:

- A name that is neither a game command, nor a game word (North, Entities,
  Items...), nor made somewhere in the file, is flagged rather than guessed at.
- What the game's language refuses (`stubs/farm_lang.py` holds the list: lambda,
  comprehensions, f-strings, try, class, keyword arguments...) is said to be
  refused, in the interpreter's own words, because the interpreter is asked.
- The program is run once on a throwaway farm (`scratch.py`) and the notes say
  what really happened: what it printed, how many ticks it took, what it
  harvested, where the drone ended, and the error and its line if it stopped.

`explain_farm(code, ran=None)` returns the same shape as the other explainers:
{ok, summary, lines: [{line, source, depth, text}], output_notes, error_note}.
"""

from __future__ import annotations

import ast
from typing import Any

from code_coach.farm import data
from code_coach.farm.protocol import FUNCTIONS_BY_PY

# ── The game's words ────────────────────────────────────────────────────

_GROUP_MEMBERS: dict[str, tuple[str, ...]] = {
    "Entities": data.ENTITIES,
    "Items": data.ITEMS,
    "Grounds": data.GROUNDS,
    "Hats": data.HATS,
    "Unlocks": tuple(data.UNLOCKS),
}
#: What the interpreter has besides the drone's commands.
_LANGUAGE_NAMES = ("len", "range", "list", "set", "dict")
#: Ordinary Python that the game's language does not have.
_PYTHON_ONLY = frozenset({
    "str", "int", "float", "bool", "tuple", "sum", "round", "sorted", "enumerate", "zip", "map",
    "filter", "input", "open", "reversed", "any", "all", "pow", "divmod", "isinstance", "type",
    "chr", "ord", "hex", "bin", "format", "repr", "id", "iter", "next", "slice", "print_function",
})

_ITEM_WORDS = {
    "Hay": "hay", "Wood": "wood", "Carrot": "carrots", "Pumpkin": "pumpkins", "Power": "power",
    "Cactus": "cactus", "Bone": "bones", "Gold": "gold", "Weird_Substance": "weird substance",
    "Water": "water", "Fertilizer": "fertilizer",
}
_ENTITY_WORDS = {
    "Grass": "grass", "Bush": "a bush", "Tree": "a tree", "Carrot": "a carrot", "Pumpkin": "a pumpkin",
    "Dead_Pumpkin": "a dead pumpkin", "Sunflower": "a sunflower", "Cactus": "a cactus",
    "Hedge": "a hedge", "Treasure": "the treasure", "Apple": "an apple", "Dinosaur": "a dinosaur",
}
_GROUND_WORDS = {"Grassland": "grassland", "Soil": "soil"}
_COMPARE = {
    ast.Eq: "is", ast.NotEq: "isn't", ast.Lt: "is less than", ast.LtE: "is at most",
    ast.Gt: "is more than", ast.GtE: "is at least", ast.Is: "is", ast.IsNot: "is not",
    ast.In: "is in", ast.NotIn: "is not in",
}
_ARITH = {
    ast.Add: "plus", ast.Sub: "minus", ast.Mult: "times", ast.Div: "divided by",
    ast.FloorDiv: "divided by (dropping the fraction)", ast.Mod: "remainder after dividing by",
    ast.Pow: "to the power of",
}


def _words(member: str) -> str:
    return member.replace("_", " ").lower()


def _direction_word(name: str) -> str:
    return name.lower()


# ── What each command does ──────────────────────────────────────────────
#
# Written for this explainer, with the facts taken from the farm itself
# (world.py) rather than guessed: harvest() on an unripe plant destroys it,
# plant() quietly does nothing when it cannot, till() flips the ground.

#: Statement form. {0}, {1} are the arguments, in words.
_DOES: dict[str, str] = {
    "harvest": "the drone cuts what is under it. A ripe plant gives its crop; an unripe one is just destroyed "
               "and gives nothing, so check can_harvest() first if that matters",
    "plant": "tries to plant {0} under the drone. It only works on an empty square with the right ground "
             "(carrots, pumpkins, sunflowers and cacti need soil) when you can pay for it; otherwise it quietly "
             "does nothing",
    "move": "the drone moves one square {0}; at the edge of the farm it wraps round to the far side",
    "till": "turns the ground under the drone over: grassland becomes soil, and soil goes back to grassland "
            "(it flips each time)",
    "swap": "swaps the plant under the drone with the one to the {0} (this is how cacti get sorted)",
    "use_item": "uses {1} of {0} on the square under the drone",
    "do_a_flip": "the drone does a flip. It achieves nothing but takes a full second",
    "pet_the_piggy": "pets the piggy. It achieves nothing but takes a full second",
    "print": "writes {*} in smoke above the drone and into the output (takes a second of game time)",
    "quick_print": "writes {*} to the output only, and instantly",
    "clear": "wipes the whole farm back to grass and sends the drone back to (0, 0)",
    "change_hat": "puts on {0}",
    "set_execution_speed": "slows the drone to speed {0} so you can watch it (1 is the speed with no upgrades)",
    "set_world_size": "shrinks the farm to {0} by {0} squares for this run (and clears it)",
    "spawn_drone": "starts another drone running {0}; it works at the same time as this one but shares no "
                   "variables with it - it gets copies. You get its handle back, or None if every drone is out",
    "wait_for": "waits until that drone has finished, and gets back what its function returned",
    "unlock": "buys the {0} upgrade, as the research button would",
    "simulate": "runs one of your files on a separate pretend farm and gets back the game seconds it took "
                "(the real farm is left alone)",
    "has_finished": "asks whether that drone's function has returned, but nothing uses the answer",
}

#: Value form, as a phrase that goes inside a longer sentence.
_GIVES: dict[str, str] = {
    "harvest": "whether anything was harvested (True or False)",
    "plant": "whether planting worked (True or False)",
    "move": "whether the move worked (True or False)",
    "use_item": "whether the item could be used (True or False)",
    "swap": "nothing (None)",
    "till": "nothing (None)",
    "can_harvest": "whether the plant under the drone is ripe",
    "can_move": "whether the drone can move {0}",
    "measure": "a measurement of what is under the drone (a sunflower's petals, a cactus's size, a pumpkin's id, "
               "or where the treasure or apple is)",
    "get_pos_x": "the drone's x position (0 at the west edge)",
    "get_pos_y": "the drone's y position (0 at the south edge)",
    "get_world_size": "the size of the farm (squares along one side)",
    "get_entity_type": "what is growing under the drone",
    "get_ground_type": "the ground under the drone (grassland or soil)",
    "get_time": "the game seconds since the farm began",
    "get_tick_count": "the ticks this program has used so far",
    "get_water": "how wet the ground under the drone is (0 to 1)",
    "random": "a random number from 0 up to (not including) 1",
    "num_items": "your stock of {0}",
    "get_cost": "what {0} costs",
    "get_companion": "the neighbour the plant here wants, and where it should go",
    "num_unlocked": "how many levels of {0} you have",
    "num_drones": "how many drones are out",
    "max_drones": "how many drones you may have at once",
    "has_finished": "whether that drone has finished",
    "wait_for": "what that drone's function returned",
    "spawn_drone": "the new drone's handle (or None if every drone is out)",
    "min": "the smallest of {*}",
    "max": "the largest of {*}",
    "abs": "{0} without its minus sign",
    "len": "how many items are in {0}",
    "range": "the numbers from {range}",
    "list": "a list made from {0}",
    "set": "a set made from {0}",
    "dict": "a dictionary",
    "simulate": "the game seconds that simulation took",
    "unlock": "whether the upgrade was bought",
    "do_a_flip": "nothing (None)",
    "pet_the_piggy": "nothing (None)",
    "print": "nothing (None)",
    "quick_print": "nothing (None)",
    "clear": "nothing (None)",
    "change_hat": "nothing (None)",
}

#: Questions that read well as a condition ("if can_harvest():").
_TRUE_WHEN: dict[str, str] = {
    "can_harvest": "the plant under the drone is ripe",
    "can_move": "the drone can move {0}",
}
_FALSE_WHEN: dict[str, str] = {
    "can_harvest": "the plant under the drone is not ripe yet",
    "can_move": "the drone cannot move {0}",
}


def _unsupported() -> dict[type, str]:
    """What the game's language does not have, as its interpreter lists it."""
    from code_coach.farm.stubs import farm_lang

    return dict(farm_lang._NOT_PART)


def _refusal(tree: ast.AST) -> tuple[int, str] | None:
    """The first thing the interpreter would refuse before running anything."""
    from code_coach.farm.stubs import farm_lang

    try:
        farm_lang.check_language(tree, "main")
    except farm_lang.GameError as error:
        return error.line, error.message
    return None


# ── Describing expressions ──────────────────────────────────────────────


class _Reader:
    def __init__(self, tree: ast.AST, lines: list[str]) -> None:
        self.lines = lines
        self.unsupported = _unsupported()
        self.functions = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        self.defined = self._defined_names(tree)
        self.known = set(FUNCTIONS_BY_PY) | set(_LANGUAGE_NAMES) | set(data.DIRECTIONS) | set(_GROUP_MEMBERS)
        #: Game commands used, in the order first met.
        self.commands: list[str] = []
        self.counts = {"def": 0, "loop": 0, "if": 0, "assign": 0, "call": 0}
        self.items: list[dict[str, Any]] = []
        #: Names made at the top level, for the "assignment makes a local" warning.
        self.module_names = {
            t.id
            for s in getattr(tree, "body", [])
            if isinstance(s, (ast.Assign, ast.AugAssign, ast.For))
            for t in ast.walk(s.targets[0] if isinstance(s, ast.Assign) else s.target)
            if isinstance(t, ast.Name)
        }
        self.scopes: list[set[str]] = []
        self.seen_names: set[str] = set()
        self.flagged: set[tuple[str, int]] = set()

    @staticmethod
    def _defined_names(tree: ast.AST) -> set[str]:
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                names.add(node.name)
                names.update(a.arg for a in node.args.args)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
                names.add(node.id)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    names.add((alias.asname or alias.name).split(".")[0])
        return names

    # -- small helpers --

    def src(self, node: ast.AST) -> str:
        try:
            return ast.unparse(node)
        except Exception:  # noqa: BLE001
            return "..."

    def code(self, node: ast.AST) -> str:
        return f"`{self.src(node)}`"

    def _short(self, text: str, node: ast.AST) -> str:
        return text if len(text) <= 120 else self.code(node)

    # -- expressions --

    def ex(self, node: ast.AST) -> str:
        return self._short(self._ex(node), node)

    def _ex(self, n: ast.AST) -> str:
        if isinstance(n, ast.Constant):
            v = n.value
            if v is None:
                return "nothing (None)"
            if isinstance(v, str):
                return f'"{v}"'
            return str(v)
        if isinstance(n, ast.Name):
            if n.id in data.DIRECTIONS:
                return _direction_word(n.id)
            if n.id in _GROUP_MEMBERS:
                return f"the game's list of {n.id}"
            return f"`{n.id}`"
        if isinstance(n, ast.Attribute):
            return self._member(n)
        if isinstance(n, ast.Call):
            return self.call_value(n)
        if isinstance(n, ast.Compare):
            parts = [self.operand(n.left)]
            for op, right in zip(n.ops, n.comparators):
                parts.append(_COMPARE.get(type(op), "compares to"))
                parts.append(self.operand(right))
            return " ".join(parts)
        if isinstance(n, ast.BoolOp):
            joiner = " and " if isinstance(n.op, ast.And) else " or "
            return joiner.join(self.operand(v) for v in n.values)
        if isinstance(n, ast.UnaryOp):
            if isinstance(n.op, ast.Not):
                return f"not ({self.ex(n.operand)})"
            if isinstance(n.op, ast.USub):
                return f"minus {self.operand(n.operand)}"
            return self.operand(n.operand)
        if isinstance(n, ast.BinOp):
            word = _ARITH.get(type(n.op))
            if word:
                return f"{self.operand(n.left)} {word} {self.operand(n.right)}"
        if isinstance(n, ast.Subscript):
            if isinstance(n.slice, ast.Slice):
                return f"part of {self.operand(n.value)}"
            return f"item {self.operand(n.slice)} of {self.operand(n.value)}"
        if isinstance(n, ast.List):
            return "an empty list" if not n.elts else (
                "a list of " + ", ".join(self.operand(e) for e in n.elts[:4]) + (", ..." if len(n.elts) > 4 else ""))
        if isinstance(n, ast.Tuple):
            return "(" + ", ".join(self.operand(e) for e in n.elts[:4]) + (", ..." if len(n.elts) > 4 else "") + ")"
        if isinstance(n, ast.Dict):
            return "an empty dictionary" if not n.keys else "a dictionary"
        if isinstance(n, ast.Set):
            return "a set of values"
        what = self.unsupported.get(type(n))
        if what:
            return f"{what} (not part of the game's language)"
        return self.code(n)

    def operand(self, n: ast.AST) -> str:
        text = self.ex(n)
        if isinstance(n, (ast.BinOp, ast.BoolOp, ast.Compare)):
            return f"({text})"
        return text

    def _member(self, n: ast.Attribute) -> str:
        if isinstance(n.value, ast.Name) and n.value.id in _GROUP_MEMBERS:
            group, member = n.value.id, n.attr
            if group == "Entities":
                return _ENTITY_WORDS.get(member, _words(member))
            if group == "Items":
                return _ITEM_WORDS.get(member, _words(member))
            if group == "Grounds":
                return _GROUND_WORDS.get(member, _words(member))
            if group == "Hats":
                return f"the {_words(member)}"
            return f"the {member.replace('_', ' ')} upgrade"
        return self.code(n)

    def args_text(self, call: ast.Call) -> list[str]:
        return [self.ex(a) for a in call.args]

    def fill(self, template: str, call: ast.Call) -> str:
        args = self.args_text(call)
        out = template
        if "{range}" in out:
            if len(args) == 1:
                rng = f"0 up to {args[0]} minus 1"
            elif len(args) >= 2:
                rng = f"{args[0]} up to {args[1]} minus 1"
            else:
                rng = "..."
            out = out.replace("{range}", rng)
        if "{*}" in out:
            out = out.replace("{*}", ", ".join(args) if args else "nothing")
        for i in range(3):
            token = "{%d}" % i
            if token in out:
                default = "1" if i == 1 else "..."
                out = out.replace(token, args[i] if i < len(args) else default)
        return out

    def call_name(self, call: ast.Call) -> str:
        return call.func.id if isinstance(call.func, ast.Name) else ""

    def call_value(self, call: ast.Call) -> str:
        name = self.call_name(call)
        if name in self.functions:
            return f"what `{name}(...)` gives back"
        if name in _GIVES and (name in FUNCTIONS_BY_PY or name in _LANGUAGE_NAMES):
            return self.fill(_GIVES[name], call)
        if isinstance(call.func, ast.Attribute):
            return self.code(call)
        return self.code(call)

    # -- conditions --

    def cond(self, n: ast.AST) -> str:
        if isinstance(n, ast.Call):
            name = self.call_name(n)
            if name in _TRUE_WHEN:
                return self.fill(_TRUE_WHEN[name], n)
            if name in self.functions:
                return f"`{name}(...)` gives back True"
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not) and isinstance(n.operand, ast.Call):
            name = self.call_name(n.operand)
            if name in _FALSE_WHEN:
                return self.fill(_FALSE_WHEN[name], n.operand)
        if isinstance(n, ast.BoolOp):
            joiner = " and " if isinstance(n.op, ast.And) else " or "
            return joiner.join(self.cond(v) for v in n.values)
        if isinstance(n, ast.Constant) and n.value is True:
            return "it is always true"
        if isinstance(n, ast.Name):
            return f"`{n.id}` is true (not 0, False or None)"
        if isinstance(n, ast.Compare):
            return self._short(self._ex(n), n)
        return self._short(f"{self._ex(n)} is true", n)

    # -- bookkeeping --

    def add(self, node: ast.AST, depth: int, text: str, line: int | None = None) -> None:
        ln = line if line is not None else getattr(node, "lineno", 0)
        src = self.lines[ln - 1].strip() if 1 <= ln <= len(self.lines) else ""
        if any(it["line"] == ln for it in self.items):
            # A one-line compound (`for ...: harvest()`): show just this statement.
            src = self.src(node)
        self.items.append({"line": ln, "depth": depth, "source": src, "text": text})

    def note_commands(self, tree: ast.AST) -> None:
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        for node in sorted(calls, key=lambda n: (n.lineno, n.col_offset)):
            name = self.call_name(node)
            if name in FUNCTIONS_BY_PY and name not in self.commands:
                self.commands.append(name)

    # -- statements --

    def body(self, stmts: list[ast.stmt], depth: int) -> None:
        for s in stmts:
            self.statement(s, depth)

    def statement(self, s: ast.stmt, depth: int) -> None:
        method = getattr(self, "s_" + type(s).__name__, None)
        if method is not None:
            method(s, depth)
            return
        what = self.unsupported.get(type(s))
        if what:
            self.add(s, depth, f"uses {what}, which isn't part of the game's language - the game refuses it")
        else:
            self.add(s, depth, f"`{self.src(s).splitlines()[0]}` - a kind of statement this explainer doesn't describe")

    def s_Expr(self, s: ast.Expr, depth: int) -> None:
        v = s.value
        if isinstance(v, ast.Call):
            name = self.call_name(v)
            if name in self.functions:
                self.counts["call"] += 1
                self.add(s, depth, f"runs your function `{name}`: the program jumps to its `def`, does the indented "
                                   "lines there, then comes back here")
                return
            if name in _DOES and name in FUNCTIONS_BY_PY:
                self.add(s, depth, self.fill(_DOES[name], v) + ".")
                return
            if name in FUNCTIONS_BY_PY or name in _LANGUAGE_NAMES:
                what = self.call_value(v)
                self.add(s, depth, f"asks for {what}, but nothing uses the answer")
                return
            if isinstance(v.func, ast.Attribute):
                owner = self.ex(v.func.value)
                self.add(s, depth, self._method(v, owner))
                return
            self.add(s, depth, f"calls `{self.src(v.func)}` - {self.unknown_call(name)}")
            return
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            self.add(s, depth, "text on its own line - the game reads it and does nothing with it")
            return
        self.add(s, depth, f"works out {self.ex(v)} and throws the answer away")

    def unknown_call(self, name: str) -> str:
        if not name:
            return "not something this explainer can describe"
        return "this is not one of the game's commands and nothing in the file defines it"

    def _method(self, call: ast.Call, owner: str) -> str:
        attr = call.func.attr  # type: ignore[union-attr]
        args = ", ".join(self.args_text(call))
        return {
            "append": f"adds {args} to the end of {owner}",
            "pop": f"takes an item out of {owner}",
            "insert": f"puts {args} into {owner}",
            "remove": f"takes {args} out of {owner}",
            "add": f"puts {args} into the set {owner}",
        }.get(attr, f"calls `{attr}` on {owner}")

    def s_Assign(self, s: ast.Assign, depth: int) -> None:
        self.counts["assign"] += 1
        targets = [t for t in s.targets]
        value = self.ex(s.value)
        if len(targets) == 1 and isinstance(targets[0], ast.Name):
            name = targets[0].id
            warn = self._local_warning(name)
            first = name not in self.seen_names
            self.seen_names.add(name)
            if self.scopes:
                self.scopes[-1].add(name)
            if first:
                text = f"makes a variable `{name}` and stores {value} in it"
            elif name in {n.id for n in ast.walk(s.value) if isinstance(n, ast.Name)}:
                text = f"updates `{name}`: works out {value} and stores the result back in `{name}`"
            else:
                text = f"changes `{name}`: it now holds {value}"
            self.add(s, depth, text + warn)
            return
        if len(targets) == 1 and isinstance(targets[0], ast.Tuple):
            names = ", ".join(f"`{self.src(e)}`" for e in targets[0].elts)
            for e in targets[0].elts:
                if isinstance(e, ast.Name):
                    self.seen_names.add(e.id)
                    if self.scopes:
                        self.scopes[-1].add(e.id)
            self.add(s, depth, f"unpacks {value} into {names}, one value each")
            return
        if len(targets) == 1 and isinstance(targets[0], ast.Subscript):
            t = targets[0]
            self.add(s, depth, f"stores {value} at {self.ex(t.slice)} in {self.ex(t.value)}")
            return
        self.add(s, depth, f"stores {value} in {', '.join(self.code(t) for t in targets)}")

    def _local_warning(self, name: str) -> str:
        """The game has no `global`: assigning inside a function makes a new local."""
        if not self.scopes or name in self.scopes[-1] or name not in self.module_names:
            return ""
        return (f" (careful: inside a function this makes a new local `{name}` - it does not change the "
                f"`{name}` outside, because the game has no `global`)")

    def s_AugAssign(self, s: ast.AugAssign, depth: int) -> None:
        self.counts["assign"] += 1
        t = self.src(s.target)
        v = self.operand(s.value)
        verb = {
            ast.Add: f"adds {v} to", ast.Sub: f"takes {v} off", ast.Mult: f"multiplies by {v}:",
            ast.Div: f"divides by {v}:", ast.FloorDiv: f"divides by {v} (dropping the fraction):",
            ast.Mod: f"takes the remainder after dividing by {v}:",
        }.get(type(s.op), "changes")
        warn = ""
        if isinstance(s.target, ast.Name):
            warn = self._local_warning(s.target.id)
        self.add(s, depth, f"updates `{t}`: {verb} `{t}`" + warn)

    def s_Pass(self, s: ast.Pass, depth: int) -> None:
        self.add(s, depth, "does nothing - a placeholder (and it costs a tick)")

    def s_Break(self, s: ast.Break, depth: int) -> None:
        self.add(s, depth, "leaves the nearest loop at once")

    def s_Continue(self, s: ast.Continue, depth: int) -> None:
        self.add(s, depth, "skips the rest of this pass of the loop and goes straight on to the next one")

    def s_Return(self, s: ast.Return, depth: int) -> None:
        if s.value is None:
            self.add(s, depth, "leaves the function now, giving back nothing (None)")
        else:
            self.add(s, depth, f"leaves the function now, giving back {self.ex(s.value)}")

    def s_Import(self, s: ast.Import, depth: int) -> None:
        names = ", ".join(f"`{a.name}`" for a in s.names)
        self.add(s, depth, f"loads another of your files ({names}). A run here has just this one file, "
                           "so the game will stop with 'There is no file called ...'")

    def s_ImportFrom(self, s: ast.ImportFrom, depth: int) -> None:
        names = ", ".join(f"`{a.name}`" for a in s.names)
        self.add(s, depth, f"brings {names} in from your other file `{s.module}`. A run here has just this one "
                           "file, so the game will stop with 'There is no file called ...'")

    def s_FunctionDef(self, s: ast.FunctionDef, depth: int) -> None:
        self.counts["def"] += 1
        params = [a.arg for a in s.args.args]
        shown = ", ".join(params)
        text = f"defines your own function `{s.name}({shown})` - a named recipe. Nothing in it happens yet; "
        text += f"the lines under it run each time something calls `{s.name}(...)`"
        if params:
            text += f", with {', '.join(f'`{p}`' for p in params)} filled in by the call"
        self.add(s, depth, text)
        self.scopes.append(set(params))
        saved = set(self.seen_names)
        self.body(s.body, depth + 1)
        self.seen_names = saved
        self.scopes.pop()

    def s_For(self, s: ast.For, depth: int) -> None:
        self.counts["loop"] += 1
        var = self.src(s.target)
        it = s.iter
        nested = self._inside_world_loop
        text = ""
        world_loop = False
        if isinstance(it, ast.Call) and self.call_name(it) == "range":
            args = it.args
            if len(args) == 1 and isinstance(args[0], ast.Call) and self.call_name(args[0]) == "get_world_size":
                world_loop = True
                which = {"x": "column", "y": "row"}.get(var)
                if which:
                    text = (f"repeats the indented lines once for each {which} of the farm, with `{var}` counting "
                            f"0, 1, 2 ... up to the farm's size minus 1")
                else:
                    text = (f"repeats the indented lines once for each square along one side of the farm, with "
                            f"`{var}` counting 0, 1, 2 ... up to the farm's size minus 1")
                if nested:
                    text += ". Together with the loop around it, this visits every square of the farm"
            elif len(args) == 1:
                text = (f"repeats the indented lines {self.ex(args[0])} times, with `{var}` counting "
                        f"0, 1, 2 ... up to {self.ex(args[0])} minus 1")
            elif len(args) == 2:
                text = (f"repeats the indented lines with `{var}` counting from {self.ex(args[0])} up to "
                        f"{self.ex(args[1])} minus 1")
            elif len(args) == 3:
                text = (f"repeats the indented lines with `{var}` counting from {self.ex(args[0])} up to "
                        f"{self.ex(args[1])} minus 1, in steps of {self.ex(args[2])}")
        if not text:
            text = f"repeats the indented lines once for each item in {self.ex(it)}, calling the current item `{var}`"
        self.add(s, depth, text)
        if isinstance(s.target, ast.Name):
            self.seen_names.add(s.target.id)
            if self.scopes:
                self.scopes[-1].add(s.target.id)
        saved = self._inside_world_loop
        self._inside_world_loop = saved or world_loop
        self.body(s.body, depth + 1)
        self._inside_world_loop = saved

    _inside_world_loop = False

    def s_While(self, s: ast.While, depth: int) -> None:
        self.counts["loop"] += 1
        if isinstance(s.test, ast.Constant) and s.test.value is True:
            ends = any(isinstance(n, (ast.Break, ast.Return)) for st in s.body for n in ast.walk(st))
            text = ("repeats the indented lines for ever" +
                    (", until a `break` or `return` inside ends it" if ends else
                     " - nothing inside it can end it, so the program only stops when you stop it"))
        else:
            c = self.cond(s.test)
            text = f"keeps repeating the indented lines for as long as {c}"
            if isinstance(s.test, ast.UnaryOp) and isinstance(s.test.op, ast.Not):
                text = f"repeats the indented lines until the condition comes true: while {c}"
        self.add(s, depth, text)
        self.body(s.body, depth + 1)

    def s_If(self, s: ast.If, depth: int, first: bool = True) -> None:
        self.counts["if"] += 1
        c = self.cond(s.test)
        if first:
            self.add(s, depth, f"checks whether {c}; the indented lines run only when it is")
        else:
            self.add(s, depth, f"otherwise, checks whether {c}; the indented lines run only when it is")
        self.body(s.body, depth + 1)
        if not s.orelse:
            return
        if len(s.orelse) == 1 and isinstance(s.orelse[0], ast.If) and self._is_elif(s.orelse[0]):
            self.s_If(s.orelse[0], depth, first=False)
            return
        line = self._else_line(s.orelse[0].lineno)
        self.add(s.orelse[0], depth, "otherwise - when none of the checks above were true, the indented lines run",
                 line=line)
        self.body(s.orelse, depth + 1)

    def _is_elif(self, node: ast.If) -> bool:
        ln = node.lineno
        return 1 <= ln <= len(self.lines) and self.lines[ln - 1].strip().startswith("elif")

    def _else_line(self, first_line: int) -> int:
        for i in range(first_line - 2, -1, -1):
            if i < len(self.lines) and self.lines[i].strip().startswith("else"):
                return i + 1
        return first_line

    # -- flags --

    def flag_unknown(self, tree: ast.AST) -> None:
        """Names that are neither the game's, nor made in the file; and group members that don't exist."""
        notes: dict[int, list[str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                name = node.id
                if name in self.known or name in self.defined or name in ("True", "False", "None"):
                    continue
                key = (name, node.lineno)
                if key in self.flagged:
                    continue
                self.flagged.add(key)
                if name in _PYTHON_ONLY:
                    why = f"`{name}` is ordinary Python, but the game's language doesn't have it."
                else:
                    why = (f"`{name}` is not a game command and nothing in this file makes it - a typo, "
                           "or a name used before it is created?")
                notes.setdefault(node.lineno, []).append(why)
            elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                  and node.value.id in _GROUP_MEMBERS and node.attr not in _GROUP_MEMBERS[node.value.id]):
                key = (node.value.id + "." + node.attr, node.lineno)
                if key not in self.flagged:
                    self.flagged.add(key)
                    notes.setdefault(node.lineno, []).append(
                        f"`{node.value.id}.{node.attr}` doesn't exist - {node.value.id} has no {node.attr}.")
        for line, messages in sorted(notes.items()):
            text = "Heads-up: " + " ".join(messages)
            mine = [it for it in self.items if it["line"] == line]
            if mine:
                _append(mine[0], text)
            else:
                self.items.append({"line": line, "depth": 0,
                                   "source": self.lines[line - 1].strip() if line <= len(self.lines) else "",
                                   "text": text})


def _append(item: dict[str, Any], extra: str) -> None:
    """Add a sentence to a line's gloss, ending the one before it properly."""
    text = item["text"].rstrip()
    if not text.endswith((".", "?", "!")):
        text += "."
    item["text"] = f"{text} {extra}"


# ── Comments ────────────────────────────────────────────────────────────


def _comment_items(lines: list[str]) -> list[dict[str, Any]]:
    return [
        {"line": i, "depth": 0, "source": raw.strip(),
         "text": "a comment - a note for humans; the game skips it"}
        for i, raw in enumerate(lines, start=1) if raw.strip().startswith("#")
    ]


# ── The run ─────────────────────────────────────────────────────────────


def _error_note(ran: Any, refusal: tuple[int, str] | None) -> str | None:
    if ran is not None and ran.error:
        where = f" on line {ran.error_line}" if ran.error_line else ""
        message = ran.error.strip()
        if message.endswith(" isn't defined."):
            return (f"Your program stopped with a NameError{where}: {message} That is a name the game has never "
                    "seen - usually a typo, or using a variable before the line that makes it.")
        if message.startswith("SyntaxError"):
            return f"The game couldn't read the program{where}: {message}."
        if "isn't part of the game's language" in message or "aren't part of the game's language" in message:
            return (f"The game refused the program{where}: {message} Its language looks like Python but is a "
                    "smaller one, and it checks this before anything runs.")
        return f"Your program stopped{where}: {message}"
    if ran is None and refusal:
        line, message = refusal
        where = f" on line {line}" if line else ""
        return f"The game would refuse this program{where}: {message}"
    return None


def _run_notes(ran: Any) -> list[str]:
    notes: list[str] = []
    printed = list(ran.printed)
    for text in printed[:6]:
        notes.append(f"It printed: {text}")
    if len(printed) > 6:
        notes.append(f"...and {len(printed) - 6} more printed line{'s' if len(printed) - 6 != 1 else ''}.")
    if ran.stopped:
        limit = "ten seconds" if ran.stopped == "time" else "its limit on drone commands"
        notes.append(
            f"It never finished - it was stopped at {limit}. That usually means a `while True:` loop with "
            "no `break`, or a loop whose condition never comes true.")
    if ran.ticks:
        seconds = f"about {ran.game_seconds:g} seconds of game time" if ran.game_seconds else "almost no game time"
        notes.append(
            f"It used {ran.ticks} ticks, {seconds}. (Ticks are the game's clock: a successful move, harvest or plant "
            f"costs {data.ACTION_TICKS}, a question like get_pos_x() costs {data.QUESTION_TICKS}, and each "
            "operation in your own code costs a little too.)")
    gained = ran.gained
    if gained:
        from code_coach.farm.scratch import item_phrase

        notes.append(f"It harvested {item_phrase(gained)}.")
    spent = {k: -v for k, v in ran.changes.items() if v < 0 and k not in ("Water", "Fertilizer")}
    if spent:
        from code_coach.farm.scratch import item_phrase

        notes.append(f"It used up {item_phrase(dict(sorted(spent.items(), key=lambda kv: -kv[1])))} (seeds and the like).")
    if ran.commands and not ran.stopped:
        w, h = ran.size
        notes.append(f"The drone ended on square {ran.position} of a {w} by {h} farm "
                     "(0, 0 is the south-west corner; x grows east, y grows north).")
    if ran.drones > 1:
        notes.append(f"It used {ran.drones} drones in all (the first plus {ran.drones - 1} started with spawn_drone).")
    if not ran.error and not ran.stopped and not ran.ticks and not printed:
        notes.append("Running it changed nothing: it never gave the drone a command and printed nothing.")
    notes.append("This run was on a practice farm, not your saved one: every upgrade bought, the biggest field, "
                 "plenty of items, and every square starting as grass.")
    return notes


# ── Entry point ─────────────────────────────────────────────────────────


def _summary(reader: _Reader, ran: Any) -> str:
    c = reader.counts
    bits = []
    if c["def"]:
        bits.append(f"defines {c['def']} function{'s' if c['def'] != 1 else ''}")
    if c["loop"]:
        bits.append(f"uses {c['loop']} loop{'s' if c['loop'] != 1 else ''}")
    if c["if"]:
        bits.append(f"makes {c['if']} decision{'s' if c['if'] != 1 else ''}")
    if reader.commands:
        shown = ", ".join(reader.commands[:6]) + (", ..." if len(reader.commands) > 6 else "")
        bits.append(f"gives the drone these commands: {shown}")
    if not bits:
        body = "this is a short program"
    elif len(bits) == 1:
        body = f"this program {bits[0]}"
    else:
        body = "this program " + ", ".join(bits[:-1]) + f", and {bits[-1]}"
    tail = ""
    if ran is not None and ran.stopped:
        tail = " Right now it never finishes - see the note below."
    elif ran is not None and ran.error:
        tail = " Right now it stops on an error - explained below."
    return (f"Big picture: {body}. It is written in The Farmer Was Replaced's language - Python-looking code "
            f"that steers a drone around a farm, where every operation costs ticks of game time.{tail}")


def explain_farm(code: str, ran: Any = None) -> dict[str, Any]:
    """Explain a program in the game's language; `ran` is a scratch.Scratch, made here if left out."""
    lines = code.split("\n")
    if not code.strip() or all(not line.strip() or line.strip().startswith("#") for line in lines):
        comments = _comment_items(lines)
        return {
            "ok": True,
            "summary": ("There's no runnable code yet - just " + ("comments and " if comments else "") +
                        "blank space. Write a few lines for the drone and I'll walk you through them."),
            "lines": comments,
            "output_notes": [],
            "error_note": None,
        }

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        line = exc.lineno or 0
        at = f" on line {line}" if line else ""
        return {
            "ok": True,
            "summary": "The game can't read this yet - there's a syntax error.",
            "lines": [],
            "output_notes": [],
            "error_note": (f"SyntaxError{at}: {exc.msg or 'invalid syntax'}. Nothing runs until the program reads "
                           "as a whole - look for a missing colon, quote or bracket right around that spot."),
        }

    reader = _Reader(tree, lines)
    reader.body(tree.body, 0)
    reader.note_commands(tree)
    reader.flag_unknown(tree)
    refusal = _refusal(tree)
    if refusal:
        line, message = refusal
        mine = [it for it in reader.items if it["line"] == line]
        text = f"The game refuses this: {message}"
        if mine:
            _append(mine[0], text)
        elif line:
            reader.items.append({"line": line, "depth": 0,
                                 "source": lines[line - 1].strip() if line <= len(lines) else "", "text": text})

    if ran is None:
        from code_coach.farm.scratch import run_program

        ran = run_program(code)

    items = reader.items + _comment_items(lines)
    items.sort(key=lambda it: (it["line"], it["depth"]))
    return {
        "ok": True,
        "summary": _summary(reader, ran),
        "lines": items,
        "output_notes": _run_notes(ran),
        "error_note": _error_note(ran, refusal),
    }



