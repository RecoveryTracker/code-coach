"""Python for making games: entities, vectors, the loop, collisions and tiles.

The lines are the ones a small pygame-style game is made of: entities as
dataclasses, pygame.math.Vector2 for positions and velocities, a fixed
timestep with an accumulator, delta time, clamp and lerp, box and circle
collision, a level drawn as a list of strings, a state machine built on
enum, a seeded random.Random so a level can be replayed, and the pygame
calls themselves (init, display, events, held keys, Rect.colliderect,
draw, Clock.tick).

The blocks are whole little programs that print their result, and the
tests run every one in the real interpreter and hold what it prints to an
answer worked out by hand. Because they have to run anywhere, they use only
the standard library: positions are tuples and plain numbers, distances come
from math, and pygame is a line-only matter - a block that opened a window
would be a block that fails on a machine without it. They read no clock
and roll no dice that are not seeded: the one block with random numbers uses
random.Random(seed) and prints only what holds for any seed.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

PYGAME_LINES: tuple[Passage, ...] = (
    # Entities as dataclasses
    _s("@dataclass(slots=True)",
       "a game object as a small record, with no per-instance dict"),
    _s("class Enemy(Entity):", "a kind of entity, keeping its position and speed"),
    _s("speed: float = 120.0", "pixels per second, with a default"),
    _s("pos: Vector2 = field(default_factory=Vector2)",
       "a fresh vector for each entity, never a shared default"),
    _s("def update(self, dt: float) -> None:", "every entity moves by delta time"),
    _s("self.pos += self.vel * dt", "velocity times seconds is the distance moved"),
    _s("return pygame.Rect(self.x, self.y, self.w, self.h)",
       "a Rect built on demand for the collision tests"),
    _s("entities = [e for e in entities if e.alive]",
       "drop the dead after the loop, not during it"),

    # Vectors
    _s("from pygame.math import Vector2", "the 2D vector class, with its operators"),
    _s("velocity = Vector2(1, 0) * speed", "a direction scaled to a speed"),
    _s("pos += velocity * dt", "units per second times seconds"),
    _s("direction = (target - pos).normalize()",
       "length one, pointing at the target"),
    _s("if offset.length_squared() > 0:",
       "check first: normalizing a zero vector raises an error"),
    _s("pos = pos.lerp(target, 0.1)", "close a tenth of the gap each frame"),
    _s("heading = Vector2(1, 0).rotate(angle_deg)", "rotate takes degrees, not radians"),
    _s("velocity.scale_to_length(max_speed)", "cap the speed and keep the direction"),

    # The loop and time
    _s("STEP = 1.0 / 60.0", "a fixed tick of sixty a second"),
    _s("frame_time = min(now - last, 0.25)",
       "cap it, so one long stall cannot snowball"),
    _s("accumulator += frame_time", "bank the real time that has passed"),
    _s("while accumulator >= STEP:", "run as many fixed steps as the time owes"),
    _s("world.update(STEP)", "the simulation always sees the same step"),
    _s("accumulator -= STEP", "spend one step's worth of banked time"),
    _s("alpha = accumulator / STEP", "how far into the next step, for smooth drawing"),
    _s("dt = clock.tick(60) / 1000", "milliseconds since the last call, as seconds"),

    # Clamp, lerp and motion
    _s("def clamp(value: float, low: float, high: float) -> float:",
       "keep a number between two limits"),
    _s("return max(low, min(high, value))", "the whole of clamp"),
    _s("def lerp(a: float, b: float, t: float) -> float:", "a blend from a to b"),
    _s("return a + (b - a) * t", "t of 0 gives a, and t of 1 gives b"),
    _s("smooth = t * t * (3 - 2 * t)", "smoothstep: an ease in and out"),
    _s("player.x = clamp(player.x, 0, WIDTH - player.w)", "stay on the screen"),
    _s("player.vy += GRAVITY * dt", "gravity speeds the fall"),
    _s("player.y += player.vy * dt", "and the speed moves the player"),
    _s("velocity *= 0.9 ** (dt * 60)", "friction that does not depend on frame rate"),

    # Collision
    _s("ax, ay, aw, ah = a", "unpack a box into its corner and size"),
    _s("return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah",
       "boxes overlap when they overlap on both axes"),
    _s("dx, dy = a.x - b.x, a.y - b.y", "the gap between two centres"),
    _s("hit = dx * dx + dy * dy <= (a.r + b.r) ** 2",
       "circles: compare squares and skip the root"),
    _s("if player.rect.colliderect(coin.rect):", "pygame's box test on two Rects"),
    _s("hits = [e for e in enemies if player.rect.colliderect(e.rect)]",
       "every enemy touching the player"),
    _s("index = player.rect.collidelist(walls)",
       "the first wall hit, or -1 for none"),

    # Tiles drawn as text
    _s("LEVEL = [\"#######\", \"#@..$.#\", \"#######\"]", "a level drawn as strings"),
    _s("cells = [(x, y, c) for y, r in enumerate(level) for x, c in enumerate(r)]",
       "every tile with its position"),
    _s("col, row = int(pos.x // TILE), int(pos.y // TILE)", "world pixels to a tile"),
    _s("def is_wall(level: list[str], col: int, row: int) -> bool:",
       "ask the map about one tile"),
    _s("if 0 <= col < cols and 0 <= row < rows:", "stay inside the map"),
    _s("level[y] = level[y][:x] + \".\" + level[y][x + 1:]",
       "replace one tile in a row of text"),
    _s("for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):", "the four neighbours"),

    # States with enum
    _s("class State(Enum):", "a fixed set of game states"),
    _s("PLAYING = auto()", "auto numbers the members for you"),
    _s("state = State.PAUSED if state is State.PLAYING else State.PLAYING",
       "the pause key flips between two states"),
    _s("match (state, event):", "decide on the state and the event together"),
    _s("case (State.PLAYING, \"pause\"):", "one arm per allowed move"),
    _s("if new_state in TRANSITIONS[state]:", "only the moves the table allows"),

    # Seeded random
    _s("rng = random.Random(seed)", "a generator of its own: same seed, same level"),
    _s("rng = random.Random(f\"{world}-{level}\")",
       "a text seed works too, and always gives the same stream"),
    _s("x = rng.randrange(0, WIDTH, TILE)", "a spawn column that sits on the grid"),
    _s("loot = rng.choices([\"coin\", \"gem\", \"key\"], weights=[8, 3, 1])[0]",
       "weighted: coins are common, keys are rare"),
    _s("rng.shuffle(deck)", "shuffle in place"),

    # pygame itself
    _s("screen = pygame.display.set_mode((800, 600))", "open the window"),
    _s("clock = pygame.time.Clock()", "the clock that paces the loop"),
    _s("for event in pygame.event.get():", "drain the event queue each frame"),
    _s("if event.type == pygame.QUIT:", "the window's close button"),
    _s("if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:",
       "a key that went down this frame"),
    _s("keys = pygame.key.get_pressed()", "which keys are held right now"),
    _s("dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]",
       "-1, 0 or 1: booleans subtract like numbers"),
    _s("screen.fill((20, 24, 38))", "clear the frame to a dark blue"),
    _s("pygame.draw.circle(screen, \"gold\", (int(x), int(y)), 8)",
       "a filled circle of radius 8"),
    _s("pygame.display.flip()", "show the frame that was just drawn"),
    _s("label = font.render(f\"Score {score}\", True, \"white\")",
       "text turned into a surface; True means smooth edges"),
    _s("screen.blit(label, (10, 10))", "copy one surface onto another"),
    _s("player.clamp_ip(screen.get_rect())", "keep a Rect inside the window"),
    _s("player = pygame.Rect(100, 100, 32, 32)", "left, top, width, height"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Python · {note}")


PYGAME_BLOCKS: tuple[Passage, ...] = (
    _b(r"""def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


for t in (0, 0.25, 0.5, 1.5):
    print(t, lerp(10, 20, clamp(t, 0, 1)))
print(clamp(-5, 0, 10), clamp(7, 0, 10), clamp(99, 0, 10))""",
       "clamp and lerp, with t kept in range"),
    _b(r"""STEP = 1 / 60
frame_times = [0.010, 0.020, 0.040, 0.016]
accumulator = 0.0
updates = 0
for frame_time in frame_times:
    accumulator += frame_time
    while accumulator >= STEP:
        accumulator -= STEP
        updates += 1
print(updates, round(accumulator * 1000, 2), round(accumulator / STEP, 2))""",
       "a fixed timestep fed uneven frames"),
    _b(r"""GRAVITY = 900.0
FLOOR = 300.0
y, vy, dt = 300.0, -300.0, 0.1
top = y
for frames in range(1, 20):
    vy += GRAVITY * dt
    y = min(y + vy * dt, FLOOR)
    top = min(top, y)
    if y >= FLOOR:
        break
print(frames, round(top, 1), vy)""",
       "a jump under gravity, stepped by delta time"),
    _b(r"""def overlaps(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


player = (10, 10, 20, 20)
coins = [(25, 25, 5, 5), (30, 10, 5, 5), (0, 0, 10, 10), (29, 29, 4, 4)]
print([overlaps(player, c) for c in coins])
print(sum(overlaps(player, c) for c in coins))""",
       "box collision: touching edges do not count"),
    _b(r"""import math


def circles_hit(a, b):
    (ax, ay, ar), (bx, by, br) = a, b
    return (ax - bx) ** 2 + (ay - by) ** 2 <= (ar + br) ** 2


print(circles_hit((0, 0, 5), (6, 8, 5)))
print(circles_hit((0, 0, 5), (6, 8, 4)))
print(round(math.hypot(3, 4), 1), math.dist((0, 0), (6, 8)))""",
       "circle collision without a square root"),
    _b(r"""LEVEL = ["#######", "#@..$.#", "#.#$..#", "#######"]
TILE = 16

cells = {c: [] for c in "#@$."}
for y, row in enumerate(LEVEL):
    for x, c in enumerate(row):
        cells[c].append((x, y))
print(len(cells["#"]), cells["@"], cells["$"])
col, row = int(40 // TILE), int(25 // TILE)
print((col, row), LEVEL[row][col])""",
       "a level read from strings, and a pixel found on it"),
    _b(r"""from enum import Enum

State = Enum("State", "MENU PLAYING PAUSED")
MOVES = {
    (State.MENU, "start"): State.PLAYING,
    (State.PLAYING, "pause"): State.PAUSED,
    (State.PAUSED, "pause"): State.PLAYING,
}
state = State.MENU
for event in ["pause", "start", "pause", "pause", "quit"]:
    state = MOVES.get((state, event), state)
    print(event, state.name)""",
       "a state machine as a table of moves"),
    _b(r"""from enum import Enum, auto


class Mode(Enum):
    PLAY = auto()
    PAUSE = auto()


def toggle(mode):
    match mode:
        case Mode.PLAY:
            return Mode.PAUSE
        case Mode.PAUSE:
            return Mode.PLAY


mode = Mode.PLAY
print(toggle(mode).name, toggle(toggle(mode)) is Mode.PLAY, Mode.PAUSE.value)""",
       "an enum and a match that flips it"),
    _b(r"""import random


def spawn_points(seed, count):
    rng = random.Random(seed)
    xs = [rng.randrange(0, 160, 16) for _ in range(count)]
    ys = [rng.randrange(0, 96, 16) for _ in range(count)]
    return list(zip(xs, ys))


same = spawn_points(42, 5) == spawn_points(42, 5)
other = spawn_points(43, 5) == spawn_points(42, 5)
points = spawn_points(42, 50)
print(same, other)
print(all(x % 16 == 0 and 0 <= x < 160 for x, _ in points), len(points))""",
       "a seeded generator replays the same spawns"),
    _b(r"""from dataclasses import dataclass


@dataclass
class Ship:
    x: float
    vx: float = 0.0

    def move(self, direction, dt):
        self.vx = direction * 100.0
        self.x += self.vx * dt


ship = Ship(10.0)
for direction in (1, 1, -1):
    ship.move(direction, 0.25)
print(ship)""",
       "a dataclass entity that moves by delta time"),
    _b(r"""scores = {"ana": 1200, "bo": 950, "cy": 1200, "di": 40}
ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
for rank, (name, score) in enumerate(ranked, start=1):
    print(f"{rank}. {name:<4}{score:>6}")""",
       "a high-score table, ties broken by name"),
    _b(r"""COOLDOWN_MS = 500
timer_ms = 0
fired = []
for frame in range(1, 13):
    timer_ms = max(0, timer_ms - 100)
    if frame % 2 == 0 and timer_ms == 0:
        fired.append(frame)
        timer_ms = COOLDOWN_MS
print(fired)""",
       "a weapon cooldown counted in whole milliseconds"),
)
