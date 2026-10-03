"""The farm itself: the ground, what grows on it, the drone, and the rules.

One World is one save: the field, the inventory, the research bought, and
the clock. Every drone command is `World.call(name, args)`, which does the
thing at once (the game's side effects happen at the start of a command),
then lets the time it took pass - plants grow, the ground dries, water and
fertilizer arrive - and says how many real seconds that was at the drone's
speed, so the runner can pace the program to it.

Coordinates are the game's: x grows East, y grows North, (0, 0) is the
South-West corner, and the field wraps at its edges.
"""

from __future__ import annotations

import math
import random as _random
from dataclasses import dataclass, field
from typing import Any

from code_coach.farm import data
from code_coach.farm.data import DELTA, PLANTS, UNLOCKS, level_cost
from code_coach.farm.protocol import FUNCTIONS_BY_PY, dart_member, js_member


class Refusal(Exception):
    """The farm will not do that - the message says why, in the player's language."""


# ── Spelling values and functions the way the player's language does ──

def spell_function(name: str, language: str) -> str:
    f = FUNCTIONS_BY_PY.get(name)
    if f is None:
        return name + "()"
    return {"javascript": f.js, "dart": f.dart}.get(language, f.py) + "()"


def spell_value(value: str, language: str) -> str:
    if value in data.DIRECTIONS:
        return value.lower() if language == "dart" else value
    group, _, member = value.partition(".")
    if not member:
        return value
    if language == "javascript":
        return f"{group}.{js_member(member)}"
    if language == "dart":
        return f"{group}.{dart_member(member)}"
    return value


# ── A square of the field ───────────────────────────────────────────────

@dataclass
class Tile:
    ground: str = "Grassland"
    entity: str | None = None
    #: Seconds of growing it needs, and has had (at 1x - water speeds it up).
    need: float = 0.0
    grown: float = 0.0
    water: float = 0.0
    infected: bool = False
    #: Sunflower petals, cactus size.
    petals: int = 0
    size: int = 0
    #: Polyculture: (entity, x, y) this plant would like nearby.
    companion: tuple[str, int, int] | None = None

    @property
    def ripe(self) -> bool:
        return self.entity is not None and self.grown >= self.need

    def to_json(self) -> list[Any]:
        return [
            self.ground, self.entity, round(self.need, 4), round(self.grown, 4),
            round(self.water, 4), int(self.infected), self.petals, self.size,
            list(self.companion) if self.companion else None,
        ]

    @classmethod
    def from_json(cls, raw: list[Any]) -> "Tile":
        t = cls(raw[0], raw[1], float(raw[2]), float(raw[3]), float(raw[4]), bool(raw[5]),
                int(raw[6]), int(raw[7]))
        if raw[8]:
            t.companion = (raw[8][0], int(raw[8][1]), int(raw[8][2]))
        return t


@dataclass
class Maze:
    """A hedge maze grown from a bush: an m x m square of the field."""

    x0: int
    y0: int
    m: int
    #: Open passages, as frozensets of two cells; everything else is hedge.
    open: set[frozenset[tuple[int, int]]] = field(default_factory=set)
    treasure: tuple[int, int] = (0, 0)
    #: The substance it was grown with, needed again to move the treasure.
    substance: int = 0
    moved: int = 0

    def inside(self, x: int, y: int) -> bool:
        return self.x0 <= x < self.x0 + self.m and self.y0 <= y < self.y0 + self.m

    def passable(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        return frozenset((a, b)) in self.open

    def to_json(self) -> dict[str, Any]:
        return {
            "x0": self.x0, "y0": self.y0, "m": self.m,
            "open": [sorted(list(p)) for p in self.open],
            "treasure": list(self.treasure), "substance": self.substance, "moved": self.moved,
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "Maze":
        maze = cls(int(raw["x0"]), int(raw["y0"]), int(raw["m"]))
        maze.open = {frozenset((tuple(a), tuple(b))) for a, b in raw["open"]}
        maze.treasure = (int(raw["treasure"][0]), int(raw["treasure"][1]))
        maze.substance = int(raw.get("substance", 0))
        maze.moved = int(raw.get("moved", 0))
        return maze


# ── The world ───────────────────────────────────────────────────────────

class World:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = _random.Random(seed)
        self.unlocks: dict[str, int] = {name: u.starts_at for name, u in UNLOCKS.items()}
        self.items: dict[str, float] = {item: 0 for item in data.ITEMS}
        self.time = 0.0
        self.width, self.height = data.FARM_SIZES[0]
        #: A smaller field asked for by set_world_size, for this run only.
        self.shrunk: int | None = None
        self.tiles: list[Tile] = []
        self.x = 0
        self.y = 0
        self.hat = "Straw_Hat"
        self.tail: list[tuple[int, int]] = []
        self.apple_next: tuple[int, int] | None = None
        self.dino_move = data.DINO_MOVE_TICKS
        self.maze: Maze | None = None
        #: Seconds towards the next delivery of water and fertilizer.
        self.supply_clock = 0.0
        #: A sunflower harvested while a bigger one stood: the next gets no bonus.
        self.sunflower_spoiled = False
        #: Per run: ticks since it started, and the speed it is held to.
        self.run_ticks = 0
        self.speed_cap: float | None = None
        #: With more than one drone out, the clock of the drone acting now: each
        #: keeps its own, and the farm's time is the furthest any has got.
        self.clock: float | None = None
        #: Words printed above the drone: (text, game time it fades).
        self.smoke: list[tuple[str, float]] = []
        self._pumpkins: dict[tuple[int, int], tuple[int, int, int]] | None = None
        self._fill()

    # ── Size and squares ────────────────────────────────────────────────

    @property
    def w(self) -> int:
        return self.shrunk or self.width

    @property
    def h(self) -> int:
        return self.shrunk or self.height

    def _fill(self) -> None:
        self.tiles = [Tile() for _ in range(self.w * self.h)]
        for i in range(len(self.tiles)):
            self._grass(i)
        self.x = self.y = 0
        self._changed()

    def at(self, x: int, y: int) -> Tile:
        return self.tiles[(y % self.h) * self.w + (x % self.w)]

    def here(self) -> Tile:
        return self.at(self.x, self.y)

    def _index(self, x: int, y: int) -> int:
        return (y % self.h) * self.w + (x % self.w)

    def _coords(self, i: int) -> tuple[int, int]:
        return i % self.w, i // self.w

    def neighbours(self, x: int, y: int) -> dict[str, tuple[int, int]]:
        """The four squares next to (x, y) that are on the field - no wrapping."""
        out = {}
        for d, (dx, dy) in DELTA.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.w and 0 <= ny < self.h:
                out[d] = (nx, ny)
        return out

    def _changed(self) -> None:
        self._pumpkins = None

    # ── Planting helpers ────────────────────────────────────────────────

    def _grow_time(self, entity: str) -> float:
        lo, hi = PLANTS[entity].grow
        return lo if lo == hi else self.rng.uniform(lo, hi)

    def _grass(self, i: int) -> None:
        """Empty grassland grows grass by itself."""
        t = self.tiles[i]
        if t.ground == "Grassland" and t.entity is None:
            t.entity = "Grass"
            t.need = self._grow_time("Grass")
            t.grown = 0.0
            t.infected = False
            t.companion = self._pick_companion("Grass", *self._coords(i))

    def _empty(self, i: int) -> None:
        t = self.tiles[i]
        t.entity = None
        t.need = t.grown = 0.0
        t.infected = False
        t.petals = t.size = 0
        t.companion = None
        self._grass(i)
        self._changed()

    def _pick_companion(self, entity: str, x: int, y: int) -> tuple[str, int, int] | None:
        if entity not in data.COMPANION_PLANTS or self.w * self.h < 2:
            return None
        kind = self.rng.choice([p for p in data.COMPANION_PLANTS if p != entity])
        spots = [
            (x + dx, y + dy)
            for dx in range(-3, 4) for dy in range(-3, 4)
            if 0 < abs(dx) + abs(dy) <= 3 and 0 <= x + dx < self.w and 0 <= y + dy < self.h
        ]
        if not spots:
            return None
        cx, cy = self.rng.choice(spots)
        return kind, cx, cy

    # ── Research ────────────────────────────────────────────────────────

    def level(self, unlock: str) -> int:
        return self.unlocks.get(unlock, 0)

    def has_function(self, name: str) -> bool:
        if name in data.STARTING_FUNCTIONS:
            return True
        for u in UNLOCKS.values():
            for lvl, names in u.functions.items():
                if name in names and self.level(u.name) >= lvl:
                    return True
        return False

    def unlocked_features(self) -> set[str]:
        out = set(data.STARTING_FEATURES)
        for u in UNLOCKS.values():
            for lvl, names in u.features.items():
                if self.level(u.name) >= lvl:
                    out.update(names)
        return out

    def function_unlock(self, name: str) -> str:
        for u in UNLOCKS.values():
            for lvl, names in u.functions.items():
                if name in names:
                    return u.name if lvl == 1 else f"{u.name} (level {lvl})"
        return "the research tree"

    def next_cost(self, unlock: str) -> dict[str, int] | None:
        u = UNLOCKS[unlock]
        step = self.level(unlock) - u.starts_at
        return dict(u.costs[step]) if 0 <= step < len(u.costs) else None

    def available(self, unlock: str) -> bool:
        u = UNLOCKS[unlock]
        return (
            not u.missing
            and self.next_cost(unlock) is not None
            and all(self.level(n) >= 1 for n in u.needs)
        )

    def affordable(self, cost: dict[str, int]) -> bool:
        return all(self.items.get(item, 0) >= amount for item, amount in cost.items())

    def buy(self, unlock: str) -> bool:
        if unlock not in UNLOCKS or not self.available(unlock):
            return False
        cost = self.next_cost(unlock) or {}
        if not self.affordable(cost):
            return False
        for item, amount in cost.items():
            self.items[item] -= amount
        self.unlocks[unlock] += 1
        if unlock == "Expand":
            self.width, self.height = data.FARM_SIZES[min(self.level("Expand"), len(data.FARM_SIZES) - 1)]
            self.shrunk = None
            self.maze = None
            self.tail = []
            self._fill()
        return True

    def entity_unlocked(self, entity: str) -> bool:
        need = {
            "Grass": None, "Bush": "Plant", "Tree": "Trees", "Carrot": "Carrots",
            "Pumpkin": "Pumpkins", "Sunflower": "Sunflowers", "Cactus": "Cactus",
        }
        if entity not in need:
            return False
        return need[entity] is None or self.level(need[entity]) >= 1

    def plant_cost(self, entity: str) -> dict[str, int]:
        p = PLANTS.get(entity)
        if p is None:
            return {}
        return level_cost(p.base_cost, max(1, self.level(p.level_of)))

    # ── Time ────────────────────────────────────────────────────────────

    def speed_factor(self) -> float:
        factor = data.SPEED_STEP ** self.level("Speed")
        if self.items.get("Power", 0) > 0:
            factor *= 2
        if self.speed_cap is not None:
            factor = min(factor, self.speed_cap)
        return factor

    def spend_ticks(self, ticks: float) -> float:
        """Let `ticks` of drone time pass; returns the seconds that took."""
        self.run_ticks += int(ticks)
        powered = self.items.get("Power", 0) > 0
        seconds = ticks / (data.BASE_TICKS_PER_SECOND * self.speed_factor())
        if powered:
            self.items["Power"] = max(0.0, self.items["Power"] - ticks / data.TICKS_PER_POWER)
        self._pass(seconds)
        return seconds

    def _pass(self, seconds: float) -> None:
        """The acting drone spends `seconds`. With one drone the farm moves on with
        it; with several, only when this drone gets further than any has yet."""
        if self.clock is None:
            self.advance(seconds)
            return
        self.clock += seconds
        if self.clock > self.time:
            self.advance(self.clock - self.time)

    def max_drones(self) -> int:
        """Megafarm doubles the drones you may have, per level."""
        return 2 ** self.level("Megafarm")

    def advance(self, seconds: float) -> None:
        """Time passes: plants grow, ground dries, supplies arrive."""
        if seconds <= 0:
            return
        self.time += seconds
        # Supplies, every ten seconds, doubling with each upgrade.
        self.supply_clock += seconds
        while self.supply_clock >= data.SUPPLY_SECONDS:
            self.supply_clock -= data.SUPPLY_SECONDS
            if self.level("Watering"):
                self.items["Water"] += 2 ** (self.level("Watering") - 1)
            if self.level("Fertilizer"):
                self.items["Fertilizer"] += 2 ** (self.level("Fertilizer") - 1)
        dry = math.exp(-data.EVAPORATION * seconds)
        trees = {i for i, t in enumerate(self.tiles) if t.entity == "Tree"}
        for i, t in enumerate(self.tiles):
            if t.water:
                t.water *= dry
            if t.entity is None or t.entity in ("Hedge", "Treasure", "Apple", "Dinosaur", "Dead_Pumpkin"):
                continue
            if t.grown >= t.need:
                continue
            rate = 1.0 + data.WATER_GROWTH_BONUS * t.water
            if t.entity == "Tree":
                x, y = self._coords(i)
                crowd = sum(1 for nx, ny in self.neighbours(x, y).values() if self._index(nx, ny) in trees)
                rate /= 2 ** crowd
            t.grown = min(t.need, t.grown + seconds * rate)
            if t.grown >= t.need:
                self._ripened(i)

    def _ripened(self, i: int) -> None:
        t = self.tiles[i]
        if t.entity == "Pumpkin" and self.rng.random() < data.PUMPKIN_DEATH_CHANCE:
            t.entity = "Dead_Pumpkin"
        self._changed()

    # ── Pumpkins grow together ──────────────────────────────────────────

    def pumpkin_groups(self) -> dict[tuple[int, int], tuple[int, int, int]]:
        """Each ripe pumpkin's giant: (x0, y0, n), biggest squares first."""
        if self._pumpkins is not None:
            return self._pumpkins
        ripe = {
            self._coords(i) for i, t in enumerate(self.tiles)
            if t.entity == "Pumpkin" and t.ripe
        }
        # The largest all-ripe square with its bottom-left corner at each cell.
        best: dict[tuple[int, int], int] = {}
        for y in range(self.h - 1, -1, -1):
            for x in range(self.w - 1, -1, -1):
                if (x, y) not in ripe:
                    continue
                n = 1 + min(best.get((x + 1, y), 0), best.get((x, y + 1), 0), best.get((x + 1, y + 1), 0))
                best[(x, y)] = n
        groups: dict[tuple[int, int], tuple[int, int, int]] = {}
        for (x, y), n in sorted(best.items(), key=lambda kv: (-kv[1], kv[0][1], kv[0][0])):
            while n > 1 and any((x + dx, y + dy) in groups for dx in range(n) for dy in range(n)):
                n -= 1
            if (x, y) in groups:
                continue
            for dx in range(n):
                for dy in range(n):
                    groups[(x + dx, y + dy)] = (x, y, n)
        self._pumpkins = groups
        return groups

    # ── Cacti ───────────────────────────────────────────────────────────

    def cactus_sorted(self, x: int, y: int) -> bool:
        me = self.at(x, y)
        for d, (nx, ny) in self.neighbours(x, y).items():
            other = self.at(nx, ny)
            if other.entity != "Cactus":
                continue
            if not other.ripe:
                return False
            if d in ("North", "East") and other.size < me.size:
                return False
            if d in ("South", "West") and other.size > me.size:
                return False
        return True

    def _cactus_patch(self, x: int, y: int) -> list[tuple[int, int]]:
        patch = [(x, y)]
        seen = {(x, y)}
        for cx, cy in patch:
            if not self.cactus_sorted(cx, cy):
                continue
            around = [
                p for p in self.neighbours(cx, cy).values()
                if self.at(*p).entity == "Cactus"
            ]
            if not all(self.at(*p).ripe and self.cactus_sorted(*p) for p in around):
                continue
            for p in around:
                if p not in seen:
                    seen.add(p)
                    patch.append(p)
        return patch

    # ── Harvesting ──────────────────────────────────────────────────────

    def _gain(self, item: str, amount: float, infected: bool = False) -> None:
        if infected and amount > 0:
            weird = max(1, int(amount // 2))
            self.items["Weird_Substance"] += weird
            amount -= weird
        self.items[item] += max(0, amount)

    def _yield(self, entity: str) -> float:
        p = PLANTS[entity]
        return p.base_yield * 2 ** max(0, self.level(p.level_of) - 1)

    def _companion_bonus(self, t: Tile) -> float:
        if not t.companion:
            return 1.0
        kind, cx, cy = t.companion
        if self.at(cx, cy).entity != kind:
            return 1.0
        return data.COMPANION_MULTIPLIER * 2 ** max(0, self.level("Polyculture") - 1)

    def _harvest_here(self) -> bool:
        i = self._index(self.x, self.y)
        t = self.tiles[i]
        if self.maze and self.maze.inside(self.x, self.y):
            if (self.x, self.y) == self.maze.treasure:
                self.items["Gold"] += self.maze.m * self.maze.m * 2 ** max(0, self.level("Mazes") - 1)
            self._remove_maze()
            return True
        if t.entity is None or t.entity in ("Apple", "Dinosaur"):
            return False
        if not t.ripe or t.entity == "Dead_Pumpkin":
            self._empty(i)
            return True
        entity = t.entity
        if entity == "Pumpkin":
            x0, y0, n = self.pumpkin_groups().get((self.x, self.y), (self.x, self.y, 1))
            amount = (n ** 3 if n < 6 else n * n * 6) * self._yield("Pumpkin")
            infected = False
            for dx in range(n):
                for dy in range(n):
                    j = self._index(x0 + dx, y0 + dy)
                    infected = infected or self.tiles[j].infected
                    self._empty(j)
            self._gain("Pumpkin", amount, infected)
            return True
        if entity == "Cactus":
            patch = self._cactus_patch(self.x, self.y)
            infected = any(self.at(*p).infected for p in patch)
            for p in patch:
                self._empty(self._index(*p))
            self._gain("Cactus", len(patch) ** 2 * self._yield("Cactus"), infected)
            return True
        if entity == "Sunflower":
            flowers = [s for s in self.tiles if s.entity == "Sunflower"]
            biggest = max(s.petals for s in flowers)
            power = self._yield("Sunflower")
            if t.petals >= biggest and len(flowers) >= data.SUNFLOWER_BONUS_MIN_COUNT and not self.sunflower_spoiled:
                power *= data.SUNFLOWER_BONUS
            self.sunflower_spoiled = t.petals < biggest
            infected = t.infected
            self._empty(i)
            self._gain("Power", power, infected)
            return True
        amount = self._yield(entity) * self._companion_bonus(t)
        infected = t.infected
        self._empty(i)
        self._gain(PLANTS[entity].item, amount, infected)
        return True

    # ── Mazes ───────────────────────────────────────────────────────────

    def _grow_maze(self, size: int, substance: int) -> None:
        m = max(1, min(size, self.w, self.h))
        x0 = min(max(0, self.x - m // 2), self.w - m)
        y0 = min(max(0, self.y - m // 2), self.h - m)
        maze = Maze(x0, y0, m, substance=substance)
        # A random depth-first walk: every cell reachable, exactly one way.
        start = (self.x, self.y)
        seen = {start}
        stack = [start]
        while stack:
            cx, cy = stack[-1]
            options = [
                (nx, ny) for nx, ny in self.neighbours(cx, cy).values()
                if maze.inside(nx, ny) and (nx, ny) not in seen
            ]
            if not options:
                stack.pop()
                continue
            nxt = self.rng.choice(options)
            maze.open.add(frozenset(((cx, cy), nxt)))
            seen.add(nxt)
            stack.append(nxt)
        maze.treasure = (x0 + self.rng.randrange(m), y0 + self.rng.randrange(m))
        for dx in range(m):
            for dy in range(m):
                i = self._index(x0 + dx, y0 + dy)
                t = self.tiles[i]
                t.entity = "Hedge"
                t.need = t.grown = 0.0
                t.companion = None
                t.infected = False
        self.at(*maze.treasure).entity = "Treasure"
        self.maze = maze
        self._changed()

    def _move_treasure(self) -> None:
        maze = self.maze
        assert maze is not None
        self.items["Gold"] += maze.m * maze.m * 2 ** max(0, self.level("Mazes") - 1)
        maze.moved += 1
        self.at(*maze.treasure).entity = "Hedge"
        maze.treasure = (maze.x0 + self.rng.randrange(maze.m), maze.y0 + self.rng.randrange(maze.m))
        self.at(*maze.treasure).entity = "Treasure"
        # Some hedges fall each time, so an old maze grows loops.
        cells = [(maze.x0 + dx, maze.y0 + dy) for dx in range(maze.m) for dy in range(maze.m)]
        for _ in range(max(1, maze.m // 2)):
            cx, cy = self.rng.choice(cells)
            options = [p for p in self.neighbours(cx, cy).values() if maze.inside(*p)]
            if options:
                maze.open.add(frozenset(((cx, cy), self.rng.choice(options))))

    def _remove_maze(self) -> None:
        maze = self.maze
        if maze is None:
            return
        for dx in range(maze.m):
            for dy in range(maze.m):
                self._empty(self._index(maze.x0 + dx, maze.y0 + dy))
        self.maze = None

    # ── Moving ──────────────────────────────────────────────────────────

    def _target(self, direction: str) -> tuple[int, int] | None:
        """Where a move would land, or None if something is in the way."""
        dx, dy = DELTA[direction]
        nx, ny = self.x + dx, self.y + dy
        if self.hat == "Dinosaur_Hat":
            if not (0 <= nx < self.w and 0 <= ny < self.h):
                return None
            if (nx, ny) in self.tail[:-1]:
                return None
        nx, ny = nx % self.w, ny % self.h
        if self.maze and (self.maze.inside(self.x, self.y) or self.maze.inside(nx, ny)):
            if not self.maze.passable((self.x, self.y), (nx, ny)):
                return None
        return nx, ny

    def _move(self, direction: str) -> bool:
        target = self._target(direction)
        if target is None:
            return False
        old = (self.x, self.y)
        if self.hat == "Dinosaur_Hat":
            ate = self.here().entity == "Apple"
            self.tail.insert(0, old)
            if not ate and self.tail:
                gone = self.tail.pop()
                if self.at(*gone).entity == "Dinosaur":
                    self._empty(self._index(*gone))
            for p in self.tail:
                tile = self.at(*p)
                tile.entity = "Dinosaur"
                tile.need = tile.grown = 0.0
            self.x, self.y = target
            if ate:
                self.dino_move -= math.floor(self.dino_move * data.DINO_SPEEDUP)
                self._place_apple()
            return True
        self.x, self.y = target
        return True

    def _apple_cost(self) -> dict[str, int]:
        return level_cost(data.APPLE_BASE_COST, max(1, self.level("Dinosaurs")))

    def _free_spot(self) -> tuple[int, int] | None:
        spots = [
            self._coords(i) for i, t in enumerate(self.tiles)
            if t.entity in (None, "Grass") and self._coords(i) != (self.x, self.y)
            and self._coords(i) not in self.tail
        ]
        return self.rng.choice(spots) if spots else None

    def _place_apple(self) -> None:
        """Buy the next apple, if it can be afforded, where the last one said."""
        spot = self.apple_next or self._free_spot()
        cost = self._apple_cost()
        if spot is None or not self.affordable(cost):
            self.apple_next = None
            return
        tile = self.at(*spot)
        if tile.entity not in (None, "Grass") or spot in self.tail:
            spot = self._free_spot()
            if spot is None:
                return
            tile = self.at(*spot)
        for item, amount in cost.items():
            self.items[item] -= amount
        tile.entity = "Apple"
        tile.need = tile.grown = 0.0
        tile.companion = None
        self.apple_next = self._free_spot()

    def _take_off_dinosaur(self) -> None:
        length = len(self.tail)
        self.items["Bone"] += length * length * 2 ** max(0, self.level("Dinosaurs") - 1)
        for p in self.tail:
            self._empty(self._index(*p))
        for i, t in enumerate(self.tiles):
            if t.entity == "Apple":
                self._empty(i)
        self.tail = []
        self.apple_next = None
        self.dino_move = data.DINO_MOVE_TICKS

    # ── Clearing ────────────────────────────────────────────────────────

    def clear(self) -> None:
        if self.hat == "Dinosaur_Hat":
            self._take_off_dinosaur()
        self.hat = "Straw_Hat"
        self.maze = None
        self._fill()

    def end_run(self) -> None:
        """What a run's settings undo when it stops."""
        self.speed_cap = None
        if self.shrunk is not None:
            self.shrunk = None
            self.maze = None
            self.tail = []
            if self.hat == "Dinosaur_Hat":
                self.hat = "Straw_Hat"
            self._fill()

    # ── The commands ────────────────────────────────────────────────────

    def call(self, name: str, args: list[Any], language: str = "python") -> tuple[Any, float]:
        """Do one command. Returns its result and the real seconds it took."""
        self.require(name, language)
        handler = getattr(self, "_do_" + name)
        return handler(list(args), language)

    def require(self, name: str, language: str = "python") -> None:
        """Refuse a command the farm doesn't have, or that isn't unlocked yet."""
        if name not in FUNCTIONS_BY_PY:
            raise Refusal(f"There is no {spell_function(name, language)} on this farm.")
        if not self.has_function(name):
            raise Refusal(
                f"{spell_function(name, language)} isn't unlocked yet - research "
                f"{self.function_unlock(name)}."
            )

    # Each _do_ returns (result, seconds).

    def _act(self, ok: bool) -> float:
        return self.spend_ticks(data.ACTION_TICKS if ok else data.FAILED_TICKS)

    def _ask(self) -> float:
        return self.spend_ticks(data.QUESTION_TICKS)

    def _fixed(self, seconds: float = data.FIXED_SECONDS) -> float:
        self._pass(seconds)
        return seconds

    def _direction(self, args: list[Any], name: str, language: str, optional: bool = False) -> str | None:
        value = args[0] if args else None
        if value is None and optional:
            return None
        if value not in data.DIRECTIONS:
            dirs = ", ".join(spell_value(d, language) for d in data.DIRECTIONS)
            raise Refusal(f"{spell_function(name, language)} needs a direction: {dirs}.")
        return value

    def _member(self, value: Any, group: str, name: str, language: str) -> str:
        if not isinstance(value, str) or not value.startswith(group + "."):
            raise Refusal(f"{spell_function(name, language)} needs one of {group}, like "
                          f"{spell_value(group + '.' + self._example(group), language)}.")
        member = value.split(".", 1)[1]
        known = {"Entities": data.ENTITIES, "Items": data.ITEMS, "Grounds": data.GROUNDS,
                 "Hats": data.HATS, "Unlocks": tuple(UNLOCKS)}[group]
        if member not in known:
            raise Refusal(f"{value} is not something this farm knows.")
        return member

    @staticmethod
    def _example(group: str) -> str:
        return {"Entities": "Bush", "Items": "Hay", "Grounds": "Soil", "Hats": "Straw_Hat",
                "Unlocks": "Carrots"}[group]

    def _do_harvest(self, args, language):
        ok = self._harvest_here()
        return ok, self._act(ok)

    def _do_can_harvest(self, args, language):
        t = self.here()
        ok = t.ripe and t.entity not in ("Dead_Pumpkin", "Hedge", "Apple", "Dinosaur", None)
        if self.maze and self.maze.inside(self.x, self.y):
            ok = (self.x, self.y) == self.maze.treasure
        return ok, self._ask()

    def _do_plant(self, args, language):
        entity = self._member(args[0] if args else None, "Entities", "plant", language)
        if not self.entity_unlocked(entity):
            raise Refusal(f"{spell_value('Entities.' + entity, language)} can't be planted yet.")
        t = self.here()
        cost = self.plant_cost(entity)
        ok = (
            t.entity in (None, "Grass", "Dead_Pumpkin")
            and not (PLANTS[entity].needs_soil and t.ground != "Soil")
            and not (entity == "Grass" and t.ground != "Grassland")
            and self.affordable(cost)
            and not (self.maze and self.maze.inside(self.x, self.y))
        )
        if ok:
            for item, amount in cost.items():
                self.items[item] -= amount
            t.entity = entity
            t.need = self._grow_time(entity)
            t.grown = 0.0
            t.infected = False
            t.petals = self.rng.randint(*data.PETALS) if entity == "Sunflower" else 0
            t.size = self.rng.randrange(data.CACTUS_SIZES) if entity == "Cactus" else 0
            t.companion = self._pick_companion(entity, self.x, self.y)
            self._changed()
        return ok, self._act(ok)

    def _do_move(self, args, language):
        direction = self._direction(args, "move", language)
        # The hat's cost before this move: an apple eaten on the way makes
        # the NEXT move cheaper, not this one.
        heavy = self.dino_move if self.hat == "Dinosaur_Hat" else 0
        ok = self._move(direction)
        if ok and heavy:
            return ok, self.spend_ticks(heavy)
        return ok, self._act(ok)

    def _do_can_move(self, args, language):
        direction = self._direction(args, "can_move", language)
        return self._target(direction) is not None, self._ask()

    def _do_till(self, args, language):
        i = self._index(self.x, self.y)
        t = self.tiles[i]
        if self.maze and self.maze.inside(self.x, self.y):
            return None, self._act(False)
        t.ground = "Soil" if t.ground == "Grassland" else "Grassland"
        if t.ground == "Soil" and t.entity == "Grass":
            t.entity = None
            t.need = t.grown = 0.0
            t.companion = None
        self._grass(i)
        self._changed()
        return None, self._act(True)

    def _do_swap(self, args, language):
        direction = self._direction(args, "swap", language)
        dx, dy = DELTA[direction]
        a = self.here()
        b = self.at(self.x + dx, self.y + dy)
        fixed = ("Hedge", "Treasure", "Apple", "Dinosaur")
        if a.entity in fixed or b.entity in fixed:
            return None, self._act(False)
        for attr in ("entity", "need", "grown", "infected", "petals", "size", "companion"):
            va, vb = getattr(a, attr), getattr(b, attr)
            setattr(a, attr, vb)
            setattr(b, attr, va)
        self._changed()
        return None, self._act(True)

    def _do_measure(self, args, language):
        direction = self._direction(args, "measure", language, optional=True)
        x, y = self.x, self.y
        if direction:
            dx, dy = DELTA[direction]
            x, y = (x + dx) % self.w, (y + dy) % self.h
        t = self.at(x, y)
        result: Any = None
        if self.maze and self.maze.inside(x, y):
            result = list(self.maze.treasure)
        elif t.entity == "Sunflower":
            result = t.petals
        elif t.entity == "Cactus":
            result = t.size
        elif t.entity == "Pumpkin":
            gx, gy, _ = self.pumpkin_groups().get((x, y), (x, y, 1))
            result = gy * self.w + gx + 1
        elif t.entity == "Apple" and self.apple_next:
            result = list(self.apple_next)
        return result, self._ask()

    def _do_get_pos_x(self, args, language):
        return self.x, self._ask()

    def _do_get_pos_y(self, args, language):
        return self.y, self._ask()

    def _do_get_world_size(self, args, language):
        return self.h, self._ask()

    def _do_get_entity_type(self, args, language):
        t = self.here()
        return (f"Entities.{t.entity}" if t.entity else None), self._ask()

    def _do_get_ground_type(self, args, language):
        return f"Grounds.{self.here().ground}", self._ask()

    def _do_get_time(self, args, language):
        now = round(self.clock if self.clock is not None else self.time, 4)
        return now, self._ask()

    def _do_get_tick_count(self, args, language):
        return self.run_ticks, 0.0

    def _do_use_item(self, args, language):
        item = self._member(args[0] if args else None, "Items", "use_item", language)
        n = args[1] if len(args) > 1 else 1
        if not isinstance(n, (int, float)) or n < 1 or int(n) != n:
            raise Refusal(f"{spell_function('use_item', language)} uses a whole number of items, 1 or more.")
        n = int(n)
        t = self.here()
        ok = False
        if self.items.get(item, 0) >= n:
            if item == "Water" and self.level("Watering"):
                t.water = min(1.0, t.water + data.TANK_WATER * n)
                ok = True
            elif item == "Fertilizer" and self.level("Fertilizer") and t.entity in PLANTS and not t.ripe:
                t.grown = min(t.need, t.grown + data.FERTILIZER_SECONDS * n)
                t.infected = True
                if t.grown >= t.need:
                    self._ripened(self._index(self.x, self.y))
                ok = True
            elif item == "Weird_Substance":
                ok = self._weird(n)
        if ok:
            self.items[item] -= n
            self._changed()
        return ok, self._act(ok)

    def _weird(self, n: int) -> bool:
        t = self.here()
        per_level = 2 ** max(0, self.level("Mazes") - 1)
        if self.maze and (self.x, self.y) == self.maze.treasure:
            if n != self.maze.substance or self.maze.moved >= 300:
                return False
            self._move_treasure()
            return True
        if t.entity == "Bush" and self.level("Mazes") and n >= per_level:
            self._grow_maze(n // per_level, n)
            return True
        if t.entity in PLANTS:
            # Weird Substance flips the infection here and on every side.
            t.infected = not t.infected
            for p in self.neighbours(self.x, self.y).values():
                other = self.at(*p)
                if other.entity in PLANTS:
                    other.infected = not other.infected
            return True
        return False

    def _do_get_water(self, args, language):
        return round(self.here().water, 6), self._ask()

    def _do_do_a_flip(self, args, language):
        return None, self._fixed()

    def _do_pet_the_piggy(self, args, language):
        return None, self._fixed()

    def _do_print(self, args, language):
        text = str(args[0]) if args else ""
        self.smoke.append((text, self.time + 3.0))
        self.smoke = self.smoke[-6:]
        return None, self._fixed()

    def _do_quick_print(self, args, language):
        return None, 0.0

    def _do_num_items(self, args, language):
        item = self._member(args[0] if args else None, "Items", "num_items", language)
        amount = self.items.get(item, 0)
        return (int(amount) if float(amount).is_integer() else round(amount, 4)), self._ask()

    def _do_get_cost(self, args, language):
        thing = args[0] if args else None
        cost: dict[str, int] | None = {}
        if isinstance(thing, str) and thing.startswith("Entities."):
            cost = self.plant_cost(self._member(thing, "Entities", "get_cost", language))
            if thing == "Entities.Apple":
                cost = self._apple_cost()
        elif isinstance(thing, str) and thing.startswith("Unlocks."):
            cost = self.next_cost(self._member(thing, "Unlocks", "get_cost", language)) or {}
        else:
            raise Refusal(f"{spell_function('get_cost', language)} needs an entity or an unlock.")
        return {f"Items.{k}": v for k, v in cost.items()}, self._ask()

    def _do_clear(self, args, language):
        self.clear()
        return None, self._act(True)

    def _do_get_companion(self, args, language):
        t = self.here()
        if not t.companion:
            return None, self._ask()
        kind, cx, cy = t.companion
        return [f"Entities.{kind}", [cx, cy]], self._ask()

    def _do_unlock(self, args, language):
        name = self._member(args[0] if args else None, "Unlocks", "unlock", language)
        ok = self.buy(name)
        return ok, self._act(ok)

    def _do_num_unlocked(self, args, language):
        thing = args[0] if args else None
        if not isinstance(thing, str) or "." not in thing:
            raise Refusal(f"{spell_function('num_unlocked', language)} needs an unlock, entity, item or ground.")
        group, member = thing.split(".", 1)
        if group == "Unlocks":
            return self.level(member), self._ask()
        if group == "Entities":
            return int(self.entity_unlocked(member)), self._ask()
        if group == "Items":
            plantish = {"Hay": True, "Wood": self.level("Plant") >= 1, "Carrot": self.level("Carrots") >= 1,
                        "Pumpkin": self.level("Pumpkins") >= 1, "Power": self.level("Sunflowers") >= 1,
                        "Cactus": self.level("Cactus") >= 1, "Bone": self.level("Dinosaurs") >= 1,
                        "Gold": self.level("Mazes") >= 1, "Water": self.level("Watering") >= 1,
                        "Fertilizer": self.level("Fertilizer") >= 1,
                        "Weird_Substance": self.level("Fertilizer") >= 1}
            return int(plantish.get(member, False)), self._ask()
        if group == "Grounds":
            return int(member == "Grassland" or self.level("Carrots") >= 1), self._ask()
        if group == "Hats":
            ok = (member == "Dinosaur_Hat" and self.level("Dinosaurs") >= 1) or (
                member != "Dinosaur_Hat" and self.level("Hats") >= 1) or member == "Straw_Hat"
            return int(ok), self._ask()
        raise Refusal(f"{thing} is not something this farm knows.")

    def _do_change_hat(self, args, language):
        hat = self._member(args[0] if args else None, "Hats", "change_hat", language)
        if hat == "Dinosaur_Hat" and not self.level("Dinosaurs"):
            raise Refusal(f"{spell_value('Hats.Dinosaur_Hat', language)} needs Dinosaurs.")
        if hat == self.hat:
            return None, self._act(True)
        if self.hat == "Dinosaur_Hat":
            self._take_off_dinosaur()
        self.hat = hat
        if hat == "Dinosaur_Hat":
            self.tail = []
            self.dino_move = data.DINO_MOVE_TICKS
            here = self.here()
            cost = self._apple_cost()
            if here.entity in (None, "Grass") and self.affordable(cost):
                for item, amount in cost.items():
                    self.items[item] -= amount
                here.entity = "Apple"
                here.need = here.grown = 0.0
                here.companion = None
                self.apple_next = self._free_spot()
        self._changed()
        return None, self._act(True)

    def _do_set_execution_speed(self, args, language):
        speed = args[0] if args else 0
        if not isinstance(speed, (int, float)):
            raise Refusal(f"{spell_function('set_execution_speed', language)} needs a number.")
        self.speed_cap = None if speed <= 0 else float(speed)
        return None, self._act(True)

    def _do_set_world_size(self, args, language):
        size = args[0] if args else 0
        if not isinstance(size, (int, float)):
            raise Refusal(f"{spell_function('set_world_size', language)} needs a number.")
        size = int(size)
        full = min(self.width, self.height)
        self.shrunk = None if size < 3 or size >= full else size
        if self.hat == "Dinosaur_Hat":
            self._take_off_dinosaur()
            self.hat = "Straw_Hat"
        self.maze = None
        self._fill()
        return None, self._act(True)

    def _do_random(self, args, language):
        return self.rng.random(), self._ask()

    def _numbers(self, args: list[Any], name: str, language: str) -> list[Any]:
        values = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        if not values:
            raise Refusal(f"{spell_function(name, language)} needs something to compare.")
        return values

    def _do_min(self, args, language):
        values = self._numbers(args, "min", language)
        try:
            return min(values), self.spend_ticks(max(1, len(values) - 1))
        except TypeError:
            raise Refusal(f"{spell_function('min', language)} can only compare numbers or strings.") from None

    def _do_max(self, args, language):
        values = self._numbers(args, "max", language)
        try:
            return max(values), self.spend_ticks(max(1, len(values) - 1))
        except TypeError:
            raise Refusal(f"{spell_function('max', language)} can only compare numbers or strings.") from None

    # The drone commands proper are the runner's (it owns the processes);
    # these answer for a farm with only the one drone, as in a test.

    def _do_spawn_drone(self, args, language):
        return None, self._act(False)

    def _do_num_drones(self, args, language):
        return 1, self._ask()

    def _do_max_drones(self, args, language):
        return self.max_drones(), self._ask()

    def _do_has_finished(self, args, language):
        return True, self._ask()

    def _do_wait_for(self, args, language):
        return None, self._ask()

    def _do_abs(self, args, language):
        value = args[0] if args else None
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise Refusal(f"{spell_function('abs', language)} needs a number.")
        return abs(value), self._ask()

    # ── Saving ──────────────────────────────────────────────────────────

    def to_json(self) -> dict[str, Any]:
        state = self.rng.getstate()
        return {
            "version": 1,
            "rng": [state[0], list(state[1]), state[2]],
            "unlocks": dict(self.unlocks),
            "items": dict(self.items),
            "time": self.time,
            "width": self.width, "height": self.height, "shrunk": self.shrunk,
            "tiles": [t.to_json() for t in self.tiles],
            "x": self.x, "y": self.y, "hat": self.hat,
            "tail": [list(p) for p in self.tail],
            "apple_next": list(self.apple_next) if self.apple_next else None,
            "dino_move": self.dino_move,
            "maze": self.maze.to_json() if self.maze else None,
            "supply_clock": self.supply_clock,
            "sunflower_spoiled": self.sunflower_spoiled,
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "World":
        w = cls()
        rng = raw.get("rng")
        if rng:
            w.rng.setstate((rng[0], tuple(rng[1]), rng[2]))
        for name, level in raw.get("unlocks", {}).items():
            if name in w.unlocks:
                w.unlocks[name] = int(level)
        for item, amount in raw.get("items", {}).items():
            if item in w.items:
                w.items[item] = float(amount)
        w.time = float(raw.get("time", 0))
        w.width = int(raw.get("width", w.width))
        w.height = int(raw.get("height", w.height))
        w.shrunk = raw.get("shrunk")
        tiles = raw.get("tiles")
        if tiles and len(tiles) == w.w * w.h:
            w.tiles = [Tile.from_json(t) for t in tiles]
        else:
            w._fill()
        w.x = int(raw.get("x", 0)) % w.w
        w.y = int(raw.get("y", 0)) % w.h
        w.hat = raw.get("hat", "Straw_Hat")
        w.tail = [(int(a), int(b)) for a, b in raw.get("tail", [])]
        apple = raw.get("apple_next")
        w.apple_next = (int(apple[0]), int(apple[1])) if apple else None
        w.dino_move = int(raw.get("dino_move", data.DINO_MOVE_TICKS))
        w.maze = Maze.from_json(raw["maze"]) if raw.get("maze") else None
        w.supply_clock = float(raw.get("supply_clock", 0))
        w.sunflower_spoiled = bool(raw.get("sunflower_spoiled", False))
        return w

    # ── What the screen draws ───────────────────────────────────────────

    def snapshot(self) -> dict[str, Any]:
        groups = self.pumpkin_groups()
        tiles = []
        for i, t in enumerate(self.tiles):
            x, y = self._coords(i)
            cell: dict[str, Any] = {"g": t.ground[0]}
            if t.entity:
                cell["e"] = t.entity
                if t.need:
                    cell["p"] = round(min(1.0, t.grown / t.need), 3)
                elif t.entity in PLANTS:
                    cell["p"] = 1
            if t.water > 0.005:
                cell["w"] = round(t.water, 2)
            if t.infected:
                cell["i"] = 1
            if t.entity == "Sunflower":
                cell["n"] = t.petals
            if t.entity == "Cactus":
                cell["n"] = t.size
                if t.ripe:
                    cell["s"] = int(self.cactus_sorted(x, y))
            if (x, y) in groups and groups[(x, y)][2] > 1:
                gx, gy, n = groups[(x, y)]
                cell["giant"] = [gx, gy, n]
            tiles.append(cell)
        maze = None
        if self.maze:
            m = self.maze
            # For each cell, which sides are open: N=1, E=2, S=4, W=8.
            sides = []
            for dy in range(m.m):
                for dx in range(m.m):
                    cx, cy = m.x0 + dx, m.y0 + dy
                    bits = 0
                    for bit, d in ((1, "North"), (2, "East"), (4, "South"), (8, "West")):
                        ox, oy = DELTA[d]
                        if m.passable((cx, cy), (cx + ox, cy + oy)):
                            bits |= bit
                    sides.append(bits)
            maze = {"x0": m.x0, "y0": m.y0, "m": m.m, "sides": sides, "treasure": list(m.treasure)}
        return {
            "w": self.w, "h": self.h, "time": round(self.time, 3),
            "drone": {"x": self.x, "y": self.y, "hat": self.hat},
            "drones": [{"x": self.x, "y": self.y, "hat": self.hat}],
            "tiles": tiles, "maze": maze, "tail": [list(p) for p in self.tail],
            "smoke": [text for text, until in self.smoke if until > self.time],
            "speed": round(self.speed_factor(), 4),
        }
