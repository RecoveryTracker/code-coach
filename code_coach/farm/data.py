"""Everything the farm knows that is not a rule: names, costs, timings, the tree.

The game is The Farmer Was Replaced, rebuilt so you can play it in Python,
JavaScript or Dart. The numbers here - what each unlock costs, how long
each plant takes to grow, how many ticks an action takes - are the game's
own, from the community wiki (thefarmerwasreplaced.wiki.gg). Where the
wiki does not say (the exact shape of the research tree, the farm size
after each Expand, yields after upgrades) the values are a careful guess
in the game's spirit, and marked so.

Names are the game's Python names ("can_harvest", "Entities.Bush"). They
are also the wire format between your program and the farm: JavaScript
and Dart spell them their own way (canHarvest, Entities.bush) and their
libraries translate.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ── Time ────────────────────────────────────────────────────────────────

#: Ticks a second with no upgrades: one action (200 ticks) is half a second.
BASE_TICKS_PER_SECOND = 400
#: Each Speed level multiplies the drone's speed by this.
SPEED_STEP = 1.5
#: Ticks for an action that did something, and for one that failed.
ACTION_TICKS = 200
FAILED_TICKS = 1
QUESTION_TICKS = 1
#: print, do_a_flip and pet_the_piggy take a fixed second, whatever the speed.
FIXED_SECONDS = 1.0
#: One power lasts this many ticks of running code; power doubles the speed.
TICKS_PER_POWER = 6000

# ── Names ───────────────────────────────────────────────────────────────

DIRECTIONS = ("North", "East", "South", "West")
#: y grows towards the North: (0, 0) is the bottom-left corner.
DELTA = {"North": (0, 1), "East": (1, 0), "South": (0, -1), "West": (-1, 0)}

ENTITIES = (
    "Grass", "Bush", "Tree", "Carrot", "Pumpkin", "Dead_Pumpkin", "Sunflower",
    "Cactus", "Hedge", "Treasure", "Apple", "Dinosaur",
)
ITEMS = (
    "Hay", "Wood", "Carrot", "Pumpkin", "Power", "Cactus", "Bone", "Gold",
    "Weird_Substance", "Water", "Fertilizer",
)
GROUNDS = ("Grassland", "Soil")
HATS = (
    "Straw_Hat", "Brown_Hat", "Gray_Hat", "Green_Hat", "Purple_Hat",
    "Traffic_Cone", "Wizard_Hat", "Dinosaur_Hat",
)

# ── Plants ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Plant:
    name: str
    #: Seconds to grow, uniformly random between these.
    grow: tuple[float, float]
    #: The item a harvest gives, and how many before upgrades.
    item: str
    base_yield: int
    #: Which unlock's level multiplies the yield and the planting cost.
    level_of: str
    #: Planting cost before upgrades; doubles with each upgrade level.
    base_cost: dict[str, int] = field(default_factory=dict)
    needs_soil: bool = False


PLANTS: dict[str, Plant] = {
    p.name: p
    for p in (
        Plant("Grass", (0.5, 0.5), "Hay", 1, "Grass"),
        Plant("Bush", (3.2, 4.8), "Wood", 1, "Trees"),
        Plant("Tree", (5.6, 8.4), "Wood", 5, "Trees"),
        Plant("Carrot", (4.8, 7.2), "Carrot", 1, "Carrots", {"Hay": 1, "Wood": 1}, True),
        Plant("Pumpkin", (0.2, 3.8), "Pumpkin", 1, "Pumpkins", {"Carrot": 1}, True),
        Plant("Sunflower", (5.6, 8.4), "Power", 1, "Sunflowers", {"Carrot": 1}, True),
        Plant("Cactus", (1.0, 1.0), "Cactus", 1, "Cactus", {"Pumpkin": 2}, True),
    )
}

#: The plants that keep a companion preference (Polyculture).
COMPANION_PLANTS = ("Grass", "Bush", "Tree", "Carrot")
#: The yield multiplier for a plant whose companion is in place, before
#: Polyculture upgrades; each upgrade past the first doubles it.
COMPANION_MULTIPLIER = 5
#: A pumpkin dies as it ripens this often.
PUMPKIN_DEATH_CHANCE = 0.2
#: Sunflowers: petals between these, and the bonus for the biggest.
PETALS = (7, 15)
SUNFLOWER_BONUS = 8
SUNFLOWER_BONUS_MIN_COUNT = 10
#: Cactus sizes run 0 to 9.
CACTUS_SIZES = 10

# ── Water and fertilizer ────────────────────────────────────────────────

#: One tank raises the water level this much (the level runs 0 to 1).
TANK_WATER = 0.25
#: A level of 1 grows five times as fast as dry ground.
WATER_GROWTH_BONUS = 4.0
#: The ground loses this share of its water each second.
EVAPORATION = 0.01
#: Water and fertilizer arrive this often (seconds), doubling per upgrade.
SUPPLY_SECONDS = 10.0
#: Fertilizer takes this many seconds off the growing time.
FERTILIZER_SECONDS = 2.0

# ── Dinosaurs ───────────────────────────────────────────────────────────

DINO_MOVE_TICKS = 400
#: Each apple eaten takes this share off the hat's move cost (rounded down).
DINO_SPEEDUP = 0.03
APPLE_BASE_COST = {"Cactus": 2}

# ── The farm ────────────────────────────────────────────────────────────

#: (width, height) after each Expand level. The first Expand makes a column
#: of three; the second, the first square. Later sizes are a guess.
FARM_SIZES = (
    (1, 1), (1, 3), (3, 3), (4, 4), (6, 6), (8, 8), (10, 10), (12, 12),
    (16, 16), (22, 22),
)

# ── The research tree ───────────────────────────────────────────────────

#: Parts of the language the tree unlocks, by the name gate.py checks for.
LANGUAGE_FEATURES = (
    "while", "if", "for", "operators", "variables", "functions", "lists",
    "dicts", "import",
)


@dataclass(frozen=True)
class Unlock:
    name: str
    #: The cost of each level in turn; one entry is a single unlock.
    costs: tuple[dict[str, int], ...]
    #: Unlocks that must be bought before this one is offered.
    needs: tuple[str, ...]
    #: Our words for what it does.
    about: str
    #: Functions (by their Python name) it makes available, per level reached.
    functions: dict[int, tuple[str, ...]] = field(default_factory=dict)
    #: Language features, per level reached.
    features: dict[int, tuple[str, ...]] = field(default_factory=dict)
    #: Level you start with (Grass starts unlocked, at level 1).
    starts_at: int = 0
    #: Not built in Code Coach yet: shown, but cannot be bought.
    missing: bool = False


def _c(*items: tuple[str, int]) -> dict[str, int]:
    return dict(items)


def _ladder(item: str, *amounts: int) -> tuple[dict[str, int], ...]:
    return tuple({item: a} for a in amounts)


UNLOCKS: dict[str, Unlock] = {
    u.name: u
    for u in (
        Unlock("Loops", _ladder("Hay", 5), (), "A while loop, so the drone keeps going on its own.",
               features={1: ("while",)}),
        Unlock("Speed", (_c(("Hay", 20)), _c(("Wood", 20)), _c(("Wood", 50), ("Carrot", 50)),
                         _c(("Carrot", 500)), _c(("Carrot", 1000))), ("Loops",),
               "The drone works half as fast again with every level. The first level also "
               "brings if and can_harvest(), so it can wait for a plant to be ready.",
               functions={1: ("can_harvest",)}, features={1: ("if",)}),
        Unlock("Expand", (_c(("Hay", 30)), _c(("Wood", 20)), _c(("Wood", 30), ("Carrot", 20)),
                          _c(("Wood", 100), ("Carrot", 50))) + _ladder("Pumpkin", 1000, 8000, 64000, 512000, 4100000),
               ("Loops",),
               "More farm. The first level gives a column of three squares and move(); the "
               "second makes a square, with for loops and get_world_size(). Every level clears "
               "the farm.",
               functions={1: ("move",), 2: ("get_world_size",)}, features={2: ("for",)}),
        Unlock("Grass", _ladder("Hay", 100, 300) + _ladder("Wood", 500, 2500, 12500, 62500, 312000,
                                                            1560000, 7810000, 39100000),
               ("Speed",), "More hay from every harvest of grass.", starts_at=1),
        Unlock("Plant", _ladder("Hay", 50), ("Expand",),
               "plant(Entities.Bush) - bushes grow wood. clear() puts the farm back to grass.",
               functions={1: ("plant", "clear")}),
        Unlock("Senses", _ladder("Hay", 100), ("Plant",),
               "The drone can tell where it is and what is under it: get_pos_x(), get_pos_y(), "
               "get_entity_type(), get_ground_type(), num_items(), num_unlocked(), and None.",
               functions={1: ("get_pos_x", "get_pos_y", "get_entity_type", "get_ground_type",
                              "num_items", "num_unlocked")}),
        Unlock("Operators", (_c(("Hay", 150), ("Wood", 10)),), ("Senses",),
               "Arithmetic, comparisons and logic: + - * / // % ** == != < <= > >= and or not.",
               features={1: ("operators",)}),
        Unlock("Debug", (_c(("Hay", 50), ("Wood", 50)),), ("Plant",),
               "print() writes above the drone (it takes a second); quick_print() writes to the "
               "output only, and takes no time.",
               functions={1: ("print", "quick_print")}),
        Unlock("Hats", _ladder("Hay", 50), ("Plant",), "change_hat(): your drone deserves a hat.",
               functions={1: ("change_hat",)}),
        Unlock("Carrots", _ladder("Wood", 50, 250, 1250, 6250, 31200, 156000, 781000, 3910000,
                                  19500000, 97700000),
               ("Plant",),
               "till() turns grass into soil, and carrots grow in soil. They cost hay and wood "
               "to plant. Each upgrade doubles both the yield and the cost.",
               functions={1: ("till",)}),
        Unlock("Variables", _ladder("Carrot", 35), ("Carrots",), "Give values a name: x = 3.",
               features={1: ("variables",)}),
        Unlock("Functions", _ladder("Carrot", 40), ("Variables",), "Define your own functions.",
               features={1: ("functions",)}),
        Unlock("Import", _ladder("Carrot", 80), ("Functions",),
               "Import from other files.", features={1: ("import",)}, missing=True),
        Unlock("Lists", _ladder("Carrot", 500), ("Functions",), "Lists, to keep many values in order.",
               features={1: ("lists",)}),
        Unlock("Trees", (_c(("Wood", 50), ("Carrot", 70)),) + _ladder("Hay", 300, 1200, 4800, 19200,
                                                                         76800, 307000, 1230000,
                                                                         4920000, 19700000),
               ("Carrots",),
               "Trees give five times the wood of a bush, but grow twice as slowly for every tree "
               "right next to them. Upgrades double the wood from bushes and trees.",
               functions={}),
        Unlock("Watering", _ladder("Wood", 50, 200, 800, 3200, 12800, 51200, 205000, 819000, 3280000),
               ("Carrots",),
               "A tank of water arrives every 10 seconds (twice as many per upgrade). "
               "use_item(Items.Water) waters the ground under the drone; get_water() reads it. "
               "Wet ground grows plants up to five times as fast, and dries out slowly.",
               functions={1: ("use_item", "get_water")}),
        Unlock("Sunflowers", _ladder("Carrot", 500), ("Carrots",),
               "Sunflowers give power, and power doubles the drone's speed. measure() counts "
               "petals; harvest the one with the most (with at least 10 on the farm) for 8 times "
               "the power.",
               functions={1: ("measure",)}),
        Unlock("Pumpkins", (_c(("Wood", 500), ("Carrot", 200)),) + _ladder(
            "Carrot", 1000, 4000, 16000, 64000, 256000, 1020000, 4100000, 16400000, 65500000),
               ("Carrots",),
               "Pumpkins grow in soil and cost carrots. Ripe pumpkins in a square grow into one "
               "giant pumpkin, worth far more - but one in five dies as it ripens.",
               functions={1: ("measure",)}),
        Unlock("Fertilizer", _ladder("Wood", 500, 1500, 9000, 54000), ("Trees",),
               "Fertilizer arrives every 10 seconds. use_item(Items.Fertilizer) takes 2 seconds "
               "off a plant's growing - and infects it: half of an infected plant's yield comes "
               "out as Weird Substance.",
               functions={1: ("use_item",)}),
        Unlock("Utilities", _ladder("Pumpkin", 1000), ("Pumpkins",), "min(), max(), abs() and random().",
               functions={1: ("min", "max", "abs", "random")}),
        Unlock("Timing", _ladder("Pumpkin", 1000), ("Pumpkins",),
               "get_time() and get_tick_count(), to measure your code.",
               functions={1: ("get_time", "get_tick_count")}),
        Unlock("Costs", _ladder("Pumpkin", 2500), ("Pumpkins",),
               "get_cost() tells you what a plant or an unlock costs.", functions={1: ("get_cost",)}),
        Unlock("Dictionaries", _ladder("Pumpkin", 2500), ("Pumpkins",),
               "Dictionaries and sets.", features={1: ("dicts",)}),
        Unlock("Auto_Unlock", _ladder("Pumpkin", 5000), ("Costs",),
               "unlock() buys research from your code.", functions={1: ("unlock",)}),
        Unlock("Polyculture", (_c(("Pumpkin", 3000)),) + _ladder("Bone", 10000, 50000, 250000, 1250000),
               ("Pumpkins",),
               "Every grass, bush, tree and carrot wants a particular neighbour somewhere near "
               "it. get_companion() says which, and where; plant it there and the harvest is "
               "five times bigger, doubling with each upgrade.",
               functions={1: ("get_companion",)}),
        Unlock("Cactus", _ladder("Pumpkin", 5000, 20000, 120000, 720000, 4320000, 25900000),
               ("Pumpkins",),
               "Cacti come in sizes 0 to 9. Sort them - bigger to the North and East - and "
               "harvesting one harvests the whole sorted patch, n cacti giving n squared. "
               "swap() moves them; measure() reads their size.",
               functions={1: ("swap", "measure")}),
        Unlock("Mazes", (_c(("Weird_Substance", 1000)),) + _ladder("Cactus", 12000, 72000, 432000,
                                                                     2590000, 15600000),
               ("Fertilizer", "Cactus"),
               "Weird Substance on a bush grows a hedge maze with treasure inside: gold equal to "
               "the maze's area. can_move() checks for walls; measure() points at the treasure.",
               functions={1: ("can_move", "measure")}),
        Unlock("Dinosaurs", _ladder("Cactus", 2000, 12000, 72000, 432000, 2590000, 15600000),
               ("Cactus",),
               "The dinosaur hat drags a tail behind the drone and buys apples with cactus. "
               "Eat apples, grow the tail; take the hat off for bones - the tail's length squared.",
               functions={1: ("change_hat", "measure")}),
        Unlock("Debug_2", _ladder("Gold", 500), ("Mazes",),
               "set_execution_speed() and set_world_size(), to watch your code at a pace and size "
               "you can follow.",
               functions={1: ("set_execution_speed", "set_world_size")}),
        Unlock("Megafarm", _ladder("Gold", 2000, 8000, 32000, 128000, 512000), ("Mazes",),
               "More drones, working at once: spawn_drone().", missing=True),
        Unlock("Simulation", _ladder("Gold", 5000), ("Megafarm",),
               "Run your code in a simulation, faster and repeatable.", missing=True),
        Unlock("Leaderboard", (_c(("Bone", 2000000), ("Gold", 1000000)),), ("Dinosaurs", "Megafarm"),
               "Race the clock.", missing=True),
    )
}

#: Functions you have from the start.
STARTING_FUNCTIONS = ("harvest", "do_a_flip", "pet_the_piggy")
#: Language that needs no unlock: calling functions, True and False, comments.
STARTING_FEATURES: tuple[str, ...] = ()


def level_cost(base: dict[str, int], level: int) -> dict[str, int]:
    """A planting cost at an upgrade level: doubles with each level past the first."""
    factor = 2 ** max(0, level - 1)
    return {item: amount * factor for item, amount in base.items()}


def all_function_names() -> tuple[str, ...]:
    """Every function the farm answers to, by its Python name."""
    names = set(STARTING_FUNCTIONS)
    for u in UNLOCKS.values():
        for fs in u.functions.values():
            names.update(fs)
    return tuple(sorted(names))
