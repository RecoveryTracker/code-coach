"""JavaScript for making games: the canvas, the loop, and the libraries.

`snippets_js_more` stays away from the DOM so every line means the same
thing in Node and in a browser. A game cannot: it lives on a canvas,
listens to a keyboard and asks the browser for the next frame. So the
lines here are the ones a browser game is made of - the draw calls, the
frame loop with its delta time, held keys, collisions, sprite and tile
arithmetic, sound and a saved high score.

`JSGAME_LIBRARY_LINES` are calls into the libraries people actually
reach for: Phaser 3, PixiJS v8, Three.js, Kaplay, Matter.js and
howler.js. Each note names the library, because `this.physics.add` means
nothing outside Phaser. Only calls from each library's current, documented
API are here; where v8 of PixiJS changed a call, the v8 spelling is used.

The blocks are whole little functions with a call after them, and the
tests run every one in Node - so they stick to the maths and the
bookkeeping, and leave the canvas to the lines.

`JSGAME_LORE` is the history, in the form the language lore uses: a fact
a line, with the category as the note. The same standard as
`langhistory`: a date or a name is only here when it is well established,
and anything that could not be stated plainly was left out.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

JSGAME_LINES: tuple[Passage, ...] = (
    # The canvas
    _s("const canvas = document.querySelector('canvas');",
       "the canvas element the game draws on"),
    _s("const ctx = canvas.getContext('2d');",
       "the 2D context every draw call goes through"),
    _s("canvas.width = window.innerWidth * devicePixelRatio;",
       "enough real pixels to stay sharp on a high-DPI screen"),
    _s("ctx.imageSmoothingEnabled = false;",
       "keep pixel art crisp when it is scaled up"),
    _s("ctx.clearRect(0, 0, canvas.width, canvas.height);",
       "wipe the last frame before drawing the next"),
    _s("ctx.fillStyle = '#1d2b53';", "the colour the next fill uses"),
    _s("ctx.fillRect(player.x, player.y, player.w, player.h);",
       "a solid rectangle, the first sprite anyone draws"),
    _s("ctx.drawImage(sheet, sx, sy, 16, 16, x, y, 32, 32);",
       "one 16x16 frame cut from a sheet, drawn at double size"),
    _s("ctx.save(); ctx.translate(ship.x, ship.y); ctx.rotate(ship.angle);",
       "remember the state, then move and turn the canvas to the ship"),
    _s("ctx.drawImage(shipImg, -16, -16); ctx.restore();",
       "draw centred on the new origin, then undo the transform"),
    _s("ctx.setTransform(1, 0, 0, 1, 0, 0);",
       "back to the identity transform, whatever came before"),
    _s("ctx.scale(-1, 1);", "mirror it, so one sprite can face both ways"),
    _s("ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);",
       "a full circle: zero to two pi radians"),
    _s("ctx.font = '16px monospace';", "the font for the score"),
    _s("ctx.fillText(`Score: ${score}`, 10, 24);",
       "text drawn at a point on the canvas"),
    _s("const img = new Image();", "an image to load the sprite sheet into"),
    _s("img.src = 'assets/player.png';", "setting src starts the download"),
    _s("img.onload = () => requestAnimationFrame(loop);",
       "start the loop once the art has arrived"),

    # The loop
    _s("let last = performance.now();", "when the previous frame ran"),
    _s("function loop(now) {",
       "requestAnimationFrame passes the time in milliseconds"),
    _s("const dt = Math.min((now - last) / 1000, 0.1);",
       "seconds since the last frame, capped after a stall"),
    _s("requestAnimationFrame(loop);",
       "ask for the next frame, once per display refresh"),
    _s("cancelAnimationFrame(frameId);", "stop the loop, on pause or game over"),
    _s("const STEP = 1 / 60;", "a fixed physics tick, sixty a second"),
    _s("accumulator += dt;", "bank the real time that has passed"),
    _s("while (accumulator >= STEP) {",
       "as many fixed ticks as the banked time pays for"),
    _s("accumulator -= STEP;", "spend one tick's worth of time"),
    _s("const alpha = accumulator / STEP;",
       "how far between two ticks this frame falls"),
    _s("const drawX = prev.x + (curr.x - prev.x) * alpha;",
       "draw between the last two ticks, so motion stays smooth"),
    _s("document.addEventListener('visibilitychange', () => { paused = document.hidden; });",
       "pause when the tab is hidden"),

    # Input
    _s("const keys = new Set();", "which keys are held down right now"),
    _s("window.addEventListener('keydown', (e) => keys.add(e.code));",
       "a key goes down: remember it"),
    _s("window.addEventListener('keyup', (e) => keys.delete(e.code));",
       "a key comes up: forget it"),
    _s("if (keys.has('ArrowLeft')) player.vx -= speed * dt;",
       "held input, scaled by the frame time"),
    _s("const dx = (keys.has('KeyD') ? 1 : 0) - (keys.has('KeyA') ? 1 : 0);",
       "left and right as -1, 0 or 1; code is the physical key"),
    _s("if (e.code === 'Space') e.preventDefault();",
       "stop Space from scrolling the page"),
    _s("canvas.addEventListener('pointerdown', (e) => shoot(e.offsetX, e.offsetY));",
       "mouse, pen and touch in one event"),
    _s("const rect = canvas.getBoundingClientRect();",
       "where the canvas sits on the page"),
    _s("const mx = (e.clientX - rect.left) * (canvas.width / rect.width);",
       "the pointer in canvas pixels, even on a scaled canvas"),
    _s("const pad = navigator.getGamepads()[0];",
       "the first controller, or null if none is connected"),
    _s("if (pad && pad.buttons[0].pressed) jump();",
       "the bottom face button in the standard mapping"),

    # Collision and movement
    _s("if (a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y) {",
       "AABB: two boxes overlap when they overlap on both axes"),
    _s("const touching = Math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r;",
       "circles touch when the centres are closer than the radii"),
    _s("const distSq = dx * dx + dy * dy;",
       "squared distance: compare it to r * r, skip the root"),
    _s("if (distSq < r * r) collect(coin);", "close enough to pick it up"),
    _s("player.x = Math.max(0, Math.min(player.x, WIDTH - player.w));",
       "keep the player on the screen"),
    _s("const lerp = (a, b, t) => a + (b - a) * t;",
       "linear interpolation: t of the way from a to b"),
    _s("camera.x += (target.x - camera.x) * (1 - Math.exp(-5 * dt));",
       "a camera that eases after its target at any frame rate"),
    _s("const angle = Math.atan2(target.y - y, target.x - x);",
       "the direction to the target, in radians"),
    _s("bullet.vx = Math.cos(angle) * speed;", "the x part of that direction"),
    _s("bullet.vy = Math.sin(angle) * speed;", "and the y part"),
    _s("const len = Math.hypot(vx, vy) || 1;",
       "a vector's length, never zero to divide by"),
    _s("const nx = vx / len, ny = vy / len;",
       "normalise, so moving diagonally is not faster"),
    _s("const rad = (deg * Math.PI) / 180;", "degrees into the radians canvas wants"),
    _s("player.vy += GRAVITY * dt;", "gravity changes the velocity"),
    _s("player.y += player.vy * dt;", "and velocity changes the position"),
    _s("x = ((x % WIDTH) + WIDTH) % WIDTH;",
       "wrap round the screen edge, negative numbers too"),
    _s("const roll = Math.floor(Math.random() * 6) + 1;", "a die roll, one to six"),
    _s("entities.sort((a, b) => a.y - b.y);",
       "draw what is lower on screen last, so it overlaps"),

    # Sprites and tiles
    _s("const frame = Math.floor(elapsed * FPS) % frameCount;",
       "the animation frame, worked out from time rather than counted"),
    _s("const sx = (frame % COLS) * TILE, sy = Math.floor(frame / COLS) * TILE;",
       "where that frame sits on the sprite sheet"),
    _s("const tile = map[row * MAP_W + col];",
       "a 2D tile map stored as one flat array"),
    _s("const col = Math.floor(x / TILE_SIZE);", "which tile column a pixel is in"),
    _s("if (tile === WALL) player.x = prevX;", "undo a move into a wall"),

    # Sound
    _s("const jumpSfx = new Audio('sfx/jump.wav');", "a sound effect, loaded once"),
    _s("jumpSfx.currentTime = 0;", "rewind, so quick jumps each make a sound"),
    _s("jumpSfx.play().catch(() => {});",
       "play returns a promise, rejected until the player interacts"),
    _s("const audioCtx = new AudioContext();",
       "Web Audio: sound as a graph of nodes"),
    _s("const osc = audioCtx.createOscillator();", "a generated tone, the classic bleep"),
    _s("osc.connect(audioCtx.destination);", "wire it to the speakers"),
    _s("osc.stop(audioCtx.currentTime + 0.1);", "a tenth of a second of beep"),
    _s("canvas.addEventListener('click', () => audioCtx.resume(), { once: true });",
       "unlock sound on the first click"),

    # Saving, pools and timing
    _s("const best = Number(localStorage.getItem('best') ?? 0);",
       "the saved high score, or zero"),
    _s("if (score > best) localStorage.setItem('best', String(score));",
       "only write it when it has been beaten"),
    _s("localStorage.setItem('save', JSON.stringify(state));",
       "a whole save game as text"),
    _s("const bullet = pool.find((b) => !b.active) ?? spawnBullet();",
       "reuse a spent bullet before making a new one"),
    _s("for (let i = enemies.length - 1; i >= 0; i--) {",
       "walk backwards, so a splice does not skip one"),
    _s("if (enemies[i].hp <= 0) enemies.splice(i, 1);", "remove the dead"),
    _s("const t0 = performance.now();", "a timer with sub-millisecond precision"),
    _s("console.log(`update took ${(performance.now() - t0).toFixed(2)} ms`);",
       "how long one update really took"),
    _s("const state = { mode: 'title', score: 0, lives: 3 };",
       "the whole game in one object"),
)


# -- Library lines --------------------------------------------

JSGAME_LIBRARY_LINES: tuple[Passage, ...] = (
    # Phaser 3
    _s("const config = { type: Phaser.AUTO, width: 800, height: 600, scene: MainScene };",
       "Phaser 3: WebGL when it can, canvas when it cannot"),
    _s("config.physics = { default: 'arcade', arcade: { gravity: { y: 300 } } };",
       "Phaser 3: arcade physics with gravity pulling down"),
    _s("const game = new Phaser.Game(config);", "Phaser 3: start the game"),
    _s("class MainScene extends Phaser.Scene {",
       "Phaser 3: a scene has preload, create and update"),
    _s("this.load.image('sky', 'assets/sky.png');",
       "Phaser 3: queue an image in preload, under a key"),
    _s("this.add.image(400, 300, 'sky');",
       "Phaser 3: place a loaded image by its centre"),
    _s("platforms = this.physics.add.staticGroup();",
       "Phaser 3: bodies that never move"),
    _s("player = this.physics.add.sprite(100, 450, 'dude');",
       "Phaser 3: a sprite with an arcade physics body"),
    _s("player.setCollideWorldBounds(true);", "Phaser 3: stay inside the world"),
    _s("this.physics.add.collider(player, platforms);",
       "Phaser 3: the two push against each other"),
    _s("this.physics.add.overlap(player, stars, collectStar, null, this);",
       "Phaser 3: a callback when they touch, and no push"),
    _s("cursors = this.input.keyboard.createCursorKeys();",
       "Phaser 3: the arrow keys, plus Space and Shift"),
    _s("if (cursors.up.isDown && player.body.touching.down) {",
       "Phaser 3: jump only while standing on something"),
    _s("player.setVelocityX(-160);", "Phaser 3: move left, in pixels a second"),
    _s("player.anims.play('left', true);",
       "Phaser 3: true means keep playing if it already is"),
    _s("this.cameras.main.startFollow(player);", "Phaser 3: the camera follows"),
    _s("this.time.addEvent({ delay: 1000, callback: spawnEnemy, loop: true });",
       "Phaser 3: a timer on the game clock"),
    _s("this.scene.start('GameOver');", "Phaser 3: switch to another scene"),

    # PixiJS v8
    _s("const app = new Application();", "PixiJS: make the app first"),
    _s("await app.init({ background: '#1099bb', resizeTo: window });",
       "PixiJS v8: init is async and takes the options"),
    _s("document.body.appendChild(app.canvas);",
       "PixiJS v8: the canvas is app.canvas"),
    _s("const texture = await Assets.load('bunny.png');",
       "PixiJS: load a texture before using it"),
    _s("const bunny = Sprite.from('bunny.png');",
       "PixiJS: a sprite from a texture Assets has loaded"),
    _s("bunny.anchor.set(0.5);", "PixiJS: position and rotate around the middle"),
    _s("app.stage.addChild(bunny);", "PixiJS: put it on the stage"),
    _s("app.ticker.add((time) => { bunny.rotation += 0.1 * time.deltaTime; });",
       "PixiJS v8: the ticker hands you itself, with deltaTime"),

    # Three.js
    _s("const scene = new THREE.Scene();", "Three.js: the world everything goes in"),
    _s("const camera = new THREE.PerspectiveCamera(75, innerWidth / innerHeight, 0.1, 1000);",
       "Three.js: field of view, aspect, near and far"),
    _s("const renderer = new THREE.WebGLRenderer({ antialias: true });",
       "Three.js: draws the scene with WebGL"),
    _s("renderer.setSize(window.innerWidth, window.innerHeight);",
       "Three.js: fill the window"),
    _s("const material = new THREE.MeshStandardMaterial({ color: 0x44aa88 });",
       "Three.js: a lit material, invisible without a light"),
    _s("const cube = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), material);",
       "Three.js: a mesh is a geometry plus a material"),
    _s("scene.add(new THREE.DirectionalLight(0xffffff, 3));",
       "Three.js: light, so the material shows"),
    _s("renderer.setAnimationLoop(() => renderer.render(scene, camera));",
       "Three.js: its own frame loop"),

    # Kaplay
    _s("kaplay({ width: 640, height: 480 });", "Kaplay: start it; it makes the canvas"),
    _s("loadSprite('bean', 'sprites/bean.png');", "Kaplay: load a sprite by name"),
    _s("const bean = add([sprite('bean'), pos(80, 40), area(), body()]);",
       "Kaplay: a game object is a list of components"),
    _s("onKeyPress('space', () => { if (bean.isGrounded()) bean.jump(); });",
       "Kaplay: jump, but only from the ground"),
    _s("bean.onCollide('tree', () => go('lose'));",
       "Kaplay: touch a tree, go to the lose scene"),

    # Matter.js
    _s("const { Engine, Bodies, Composite, Runner } = Matter;",
       "Matter.js: the modules you use most"),
    _s("const engine = Engine.create();", "Matter.js: the physics world"),
    _s("const box = Bodies.rectangle(400, 200, 80, 80);",
       "Matter.js: a body, positioned by its centre"),
    _s("const ground = Bodies.rectangle(400, 610, 810, 60, { isStatic: true });",
       "Matter.js: a floor that never moves"),
    _s("Composite.add(engine.world, [box, ground]);", "Matter.js: add them to the world"),
    _s("Engine.update(engine, 1000 / 60);",
       "Matter.js: step the world yourself, in milliseconds"),

    # howler.js
    _s("const music = new Howl({ src: ['music.webm', 'music.mp3'], loop: true });",
       "howler.js: the first format the browser can play wins"),
    _s("const sfx = new Howl({ src: ['sfx.mp3'], sprite: { coin: [0, 300] } });",
       "howler.js: an audio sprite, offset and length in ms"),
    _s("sfx.play('coin');", "howler.js: play one named part of the sprite"),
    _s("Howler.volume(0.5);", "howler.js: the master volume"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"JavaScript · {note}")


JSGAME_BLOCKS: tuple[Passage, ...] = (
    _b("function clamp(value, min, max) {\n"
       "  if (value < min) return min;\n"
       "  if (value > max) return max;\n"
       "  return value;\n"
       "}\n"
       "\n"
       "console.log(clamp(-5, 0, 100), clamp(250, 0, 100), clamp(42, 0, 100));",
       "clamp: keep a value inside its bounds"),
    _b("function lerp(a, b, t) {\n"
       "  return a + (b - a) * t;\n"
       "}\n"
       "\n"
       "let camX = 0;\n"
       "for (let frame = 0; frame < 5; frame++) camX = lerp(camX, 100, 0.5);\n"
       "console.log(camX);",
       "lerp: a camera closing half the gap each frame"),
    _b("function rectsOverlap(a, b) {\n"
       "  return (\n"
       "    a.x < b.x + b.w &&\n"
       "    a.x + a.w > b.x &&\n"
       "    a.y < b.y + b.h &&\n"
       "    a.y + a.h > b.y\n"
       "  );\n"
       "}\n"
       "\n"
       "const player = { x: 10, y: 10, w: 16, h: 16 };\n"
       "console.log(rectsOverlap(player, { x: 20, y: 20, w: 16, h: 16 }));",
       "AABB collision between two boxes"),
    _b("function circlesTouch(a, b) {\n"
       "  const dx = a.x - b.x;\n"
       "  const dy = a.y - b.y;\n"
       "  const radii = a.r + b.r;\n"
       "  return dx * dx + dy * dy <= radii * radii;\n"
       "}\n"
       "\n"
       "console.log(circlesTouch({ x: 0, y: 0, r: 5 }, { x: 8, y: 0, r: 4 }));",
       "circle collision, without a square root"),
    _b("function wrap(value, size) {\n"
       "  return ((value % size) + size) % size;\n"
       "}\n"
       "\n"
       "console.log(wrap(-10, 640), wrap(650, 640), wrap(320, 640));",
       "wrap round the screen edge, negatives included"),
    _b("function stepEntity(e, dt, gravity = 900) {\n"
       "  e.vy += gravity * dt;\n"
       "  e.x += e.vx * dt;\n"
       "  e.y += e.vy * dt;\n"
       "  return e;\n"
       "}\n"
       "\n"
       "const ball = { x: 0, y: 0, vx: 120, vy: -300 };\n"
       "for (let i = 0; i < 3; i++) stepEntity(ball, 1 / 60);\n"
       "console.log(ball.x.toFixed(1), ball.y.toFixed(1));",
       "move by velocity times delta time, under gravity"),
    _b("const transitions = {\n"
       "  title: { start: 'playing' },\n"
       "  playing: { die: 'gameover', pause: 'paused' },\n"
       "  paused: { pause: 'playing' },\n"
       "  gameover: { start: 'playing' },\n"
       "};\n"
       "\n"
       "function next(state, event) {\n"
       "  return transitions[state][event] ?? state;\n"
       "}\n"
       "\n"
       "console.log(['start', 'pause', 'pause', 'die'].reduce(next, 'title'));",
       "a game's screens as a tiny state machine"),
    _b("function makePool(create) {\n"
       "  const free = [];\n"
       "  return {\n"
       "    get: () => free.pop() ?? create(),\n"
       "    release: (item) => free.push(item),\n"
       "  };\n"
       "}\n"
       "\n"
       "const bullets = makePool(() => ({ x: 0, y: 0 }));\n"
       "const shot = bullets.get();\n"
       "bullets.release(shot);\n"
       "console.log(bullets.get() === shot);",
       "an object pool: reuse instead of allocating"),
    _b("function mulberry32(seed) {\n"
       "  return function () {\n"
       "    let t = (seed += 0x6d2b79f5);\n"
       "    t = Math.imul(t ^ (t >>> 15), t | 1);\n"
       "    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);\n"
       "    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;\n"
       "  };\n"
       "}\n"
       "\n"
       "const rand = mulberry32(42);\n"
       "console.log(rand().toFixed(4), rand().toFixed(4));",
       "mulberry32: a seeded random, the same run every time"),
    _b("function tileAt(map, px, py, size) {\n"
       "  const col = Math.floor(px / size);\n"
       "  const row = Math.floor(py / size);\n"
       "  if (row < 0 || row >= map.length || col < 0 || col >= map[0].length) return 1;\n"
       "  return map[row][col];\n"
       "}\n"
       "\n"
       "const level = [[1, 1, 1], [1, 0, 1], [1, 1, 1]];\n"
       "console.log(tileAt(level, 24, 20, 16), tileAt(level, 5, 5, 16));",
       "the tile under a pixel, and solid off the map"),
    _b("function simulate(frameTimes, step = 1 / 60) {\n"
       "  let acc = 0, ticks = 0;\n"
       "  for (const dt of frameTimes) {\n"
       "    acc += Math.min(dt, 0.25);\n"
       "    while (acc >= step) {\n"
       "      acc -= step;\n"
       "      ticks++;\n"
       "    }\n"
       "  }\n"
       "  return ticks;\n"
       "}\n"
       "\n"
       "console.log(simulate([1 / 30, 1 / 144, 1 / 60, 0.5]));",
       "a fixed timestep: uneven frames, even ticks"),
    _b("function makeSpawner(every, spawn) {\n"
       "  let timer = every;\n"
       "  return (dt) => {\n"
       "    for (timer -= dt; timer <= 0; timer += every) spawn();\n"
       "  };\n"
       "}\n"
       "\n"
       "let count = 0;\n"
       "const tick = makeSpawner(0.5, () => count++);\n"
       "for (let i = 0; i < 8; i++) tick(0.25);\n"
       "console.log(`${count} enemies spawned`);",
       "a spawner that fires every half second"),
    _b("function axis(held, negative, positive) {\n"
       "  return (held.has(positive) ? 1 : 0) - (held.has(negative) ? 1 : 0);\n"
       "}\n"
       "\n"
       "const held = new Set(['KeyD', 'KeyW']);\n"
       "const move = { x: axis(held, 'KeyA', 'KeyD'), y: axis(held, 'KeyW', 'KeyS') };\n"
       "console.log(move);",
       "held keys into a movement direction"),
    _b("function frameAt(anim, elapsed) {\n"
       "  const index = Math.floor(elapsed * anim.fps);\n"
       "  const frame = anim.loop\n"
       "    ? index % anim.frames.length\n"
       "    : Math.min(index, anim.frames.length - 1);\n"
       "  return anim.frames[frame];\n"
       "}\n"
       "\n"
       "const run = { frames: [4, 5, 6, 7], fps: 12, loop: true };\n"
       "console.log(frameAt(run, 0), frameAt(run, 0.25), frameAt(run, 1));",
       "pick a sprite frame from the time elapsed"),
    _b("function updateParticles(particles, dt) {\n"
       "  for (const p of particles) {\n"
       "    p.x += p.vx * dt;\n"
       "    p.life -= dt;\n"
       "  }\n"
       "  return particles.filter((p) => p.life > 0);\n"
       "}\n"
       "\n"
       "const spark = (vx, life) => ({ x: 0, vx, life });\n"
       "let sparks = [spark(50, 0.3), spark(-40, 1), spark(10, 2)];\n"
       "sparks = updateParticles(sparks, 0.5);\n"
       "console.log(sparks.length, sparks[0].x);",
       "move particles, then drop the ones that burned out"),
)


# -- Lore -----------------------------------------------------

JSGAME_LORE: tuple[Passage, ...] = (
    # The browser as a games machine
    _s("Apple introduced the canvas element in 2004, in WebKit, to draw "
       "Dashboard widgets. Other browsers followed, and it became part of "
       "HTML5.", "Browser games history"),
    _s("The canvas is immediate mode: fillRect paints pixels and forgets "
       "them. There is no sprite to move, which is why a game clears and "
       "redraws the whole frame.", "Canvas design"),
    _s("Canvas coordinates start at the top left and y grows downward, so "
       "gravity is a positive number and jumping means a negative "
       "velocity.", "Canvas design"),
    _s("requestAnimationFrame began as mozRequestAnimationFrame in Firefox 4 "
       "in 2011, and a webkit-prefixed version reached Chrome the same "
       "year.", "Browser games history"),
    _s("Before it, games ran on setInterval, which keeps firing in a hidden "
       "tab and has no idea when the screen is about to refresh.",
       "Game loop design"),
    _s("A frame is not always a sixtieth of a second. Screens run at 120 and "
       "144 hertz, so movement is multiplied by delta time or the game runs "
       "faster on them.", "Game loop design"),
    _s("Glenn Fiedler's article Fix Your Timestep! is where most game "
       "programmers meet the accumulator: physics steps at a fixed rate and "
       "drawing interpolates.", "Game loop design"),
    _s("WebGL 1.0 was released by the Khronos Group in 2011. It is OpenGL ES "
       "2.0 exposed to JavaScript, which is why its API reads like C.",
       "Browser games history"),
    _s("WebGL 2, based on OpenGL ES 3.0, shipped in Chrome and Firefox in "
       "2017. Safari did not turn it on by default until 2021.",
       "Browser games history"),
    _s("WebGPU shipped in Chrome 113 in 2023. It is modelled on Vulkan, Metal "
       "and Direct3D 12 rather than on OpenGL, and it brings compute shaders "
       "to the web.", "Browser games history"),
    _s("Adobe ended support for Flash Player on December 31, 2020, and "
       "blocked Flash content from running from January 12, 2021. A "
       "generation of browser games went with it.", "Browser games history"),
    _s("Ruffle is a Flash emulator written in Rust and compiled to "
       "WebAssembly, and it lets many old Flash games run in a modern "
       "browser again.", "Browser games history"),
    _s("The Web Audio API was designed by Chris Rogers at Google. Sound is a "
       "graph of nodes: sources, gain and filters, and the destination, "
       "which is the speakers.", "Web platform"),
    _s("Browsers will not let a page make sound before the player interacts "
       "with it. That is why an AudioContext starts suspended, and so many "
       "games open on Click to start.", "Web platform"),
    _s("The Gamepad API is polled rather than pushed: each frame the game "
       "calls navigator.getGamepads() and reads the buttons and axes for "
       "itself.", "Web platform"),
    _s("Pointer Events merged mouse, touch and pen into one set of events. "
       "Microsoft shipped them in Internet Explorer 10 and proposed them to "
       "the W3C, which made them a Recommendation in 2015.", "Web platform"),
    _s("localStorage holds strings only, a few megabytes a site, and the "
       "player can clear it. A high score fits well there; a save game worth "
       "keeping deserves an export.", "Web platform"),
    _s("WebAssembly shipped in all four major browsers in 2017. Engines "
       "compile to it, and JavaScript is left doing what it is good at: the "
       "glue and the page.", "Browser games history"),
    _s("In 2013 Mozilla and Epic ported Unreal Engine 3 to the browser with "
       "asm.js and Emscripten, and showed the Epic Citadel demo running in "
       "Firefox.", "Browser games history"),

    # The libraries
    _s("Richard Davey released Phaser in 2013 through his studio Photon "
       "Storm. Phaser 3, a rewrite from the ground up, came out in February "
       "2018.", "Game library history"),
    _s("Ricardo Cabello, known as mrdoob, published Three.js in 2010. It "
       "began life in ActionScript and became the usual way to put 3D on a "
       "web page.", "Game library history"),
    _s("PixiJS came out in 2013 from Goodboy Digital in London: a fast 2D "
       "renderer that used WebGL, and fell back to canvas where WebGL was "
       "missing.", "Game library history"),
    _s("PixiJS v8 arrived in 2024 with a WebGPU renderer, and app.init became "
       "asynchronous. That is why Pixi setup code now starts with an "
       "await.", "Game library history"),
    _s("Kaboom.js was a friendly game library from Replit. When Replit "
       "stepped away from it, the community forked it and carried on under "
       "the name KAPLAY.", "Game library history"),
    _s("Matter.js is a 2D rigid-body physics engine by Liam Brummitt. It "
       "knows nothing about drawing; its Render module is there to help you "
       "debug.", "Game library history"),
    _s("howler.js, by James Simpson of GoldFire Studios, wraps Web Audio and "
       "falls back to HTML5 Audio, hiding the format and unlock quirks of "
       "each browser.", "Game library history"),
    _s("Emscripten, by Alon Zakai, compiles C and C++ for the browser. Unity "
       "and Unreal web builds were made with it, first to asm.js and then "
       "to WebAssembly.", "Game library history"),
    _s("RPG Maker MV, released in 2015, moved the engine to JavaScript and "
       "PixiJS, so the games made with it run in a browser as well as on "
       "the desktop.", "Game library history"),

    # The games
    _s("js13kGames started in 2012, founded by Andrzej Mazur. A whole entry "
       "must fit in a 13 kilobyte zip, and the month of the competition "
       "starts on August 13.", "Browser games in use"),
    _s("CrossCode, by Radical Fish Games, runs on a heavily modified ImpactJS, "
       "a JavaScript engine. It came out on PC in 2018 and on the consoles "
       "after that.", "Browser games in use"),
    _s("ImpactJS was a commercial JavaScript game engine by Dominic "
       "Szablewski. It was later released for free as open source, under "
       "the MIT licence.", "Browser games in use"),
    _s("Vampire Survivors, by poncle, was built in JavaScript with Phaser. It "
       "became a hit in 2022, and in 2023 the game was ported over to "
       "Unity.", "Browser games in use"),
    _s("HexGL, a futuristic racer by Thibaut Despoulain built with Three.js, "
       "was an early proof that a browser could run a fast, good-looking 3D "
       "game in WebGL.", "Browser games in use"),
    _s("Gabriele Cirulli wrote 2048 in JavaScript over a weekend in 2014, "
       "when he was nineteen, and released it as open source on "
       "GitHub.", "Browser games in use"),
    _s("Cookie Clicker, by Orteil, came out in 2013 as a JavaScript browser "
       "game, and it is one of the games that made idle games a genre of "
       "their own.", "Browser games in use"),
    _s("A Dark Room, by Michael Townsend, is a text game written in plain "
       "JavaScript and HTML. It came out in the browser in 2013 and was "
       "later ported to iOS.", "Browser games in use"),
    _s("The dinosaur game Chrome shows when there is no connection is "
       "JavaScript on a canvas, and you can play it at any time by visiting "
       "chrome://dino.", "Browser games in use"),
    _s("Browser games reach Steam by being wrapped in NW.js or Electron, "
       "which bundle a copy of Chromium with the game so it runs as a "
       "desktop app.", "Browser games in use"),
)
