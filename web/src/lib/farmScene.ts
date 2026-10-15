/**
 * The farm as a scene: drawn at any width and height, with a clock for the
 * little things that move (the drone hovering, plants swaying, the actions the
 * drones just did).
 *
 * This is the contract between the picture and the screen around it:
 *
 *   drawScene(ctx, snapshot, { width, height, time })
 *
 * `width` and `height` are the canvas's size in CSS pixels (the canvas may be
 * any shape, and the farm any size from 1x1 to 22x22), `time` is seconds since
 * the screen opened. It paints the whole canvas, every call. The caller does
 * the devicePixelRatio scaling (a transform on `ctx`); this file only uses CSS
 * pixels, and reads that transform to keep its cached ground sharp.
 *
 * THE LOOK: a bright, clean low-poly diorama. The farm is a raised slab with
 * thick soil-and-stone edges floating in a soft sky, seen from an angled
 * isometric (2:1 dimetric) camera; grass in two alternating greens, tilled soil
 * with furrows, plants as chunky flat-shaded shapes, hedge walls for the maze,
 * a flat-grey hovering drone with a hat.
 *
 * AXES (the farm's y grows north):
 *   EAST is toward the bottom-right of the screen, NORTH toward the top-right,
 *   WEST toward the top-left, SOUTH toward the bottom-left. Tile (0, 0) is the
 *   left-hand corner of the diamond (south-west); the bottom corner is the
 *   south-east one, the top corner the north-west one, the right corner the
 *   north-east one. (Exact formulas: farmSceneArt.ts.)
 *
 * SIZE: the whole slab plus headroom for tall plants, the drone and its hat is
 * fitted to the canvas with a margin of max(6 px, 3% of the short side). A
 * tile is at most 144 x 72 px (hw 72), so a 1x1 farm is one big, centred tile
 * and not a close-up; a tile is an even whole number of half-widths when it is
 * large enough, so edges stay crisp. Everything stays inside the canvas apart
 * from the fill of the sky itself (the tests allow a 4 px slack).
 *
 * DRAWING: painter's algorithm, back to front: the cached sky + slab + ground,
 * then ground overlays (water, infection, maze floor, action highlights), the
 * drones' shadows, then the tiles by diagonals from the far (north-west)
 * corner to the near (south-east) one - each tile's back hedge walls, its
 * plant or thing, its front hedge walls - then action effects, the drones
 * (nearest last), "+4 Hay" labels, and the speech puffs.
 *
 * CACHING: the sky, shadow, slab edges and ground tiles (with their tufts and
 * furrows) are drawn once to an offscreen canvas at device resolution, keyed
 * by the farm's size, the layout, the canvas size and the ground of every
 * tile; only the changing parts are drawn each frame. No Math.random: the
 * variety between tiles comes from a position hash.
 *
 * EVENTS: see farmSceneFx.ts - each drone action in `snapshot.events` is
 * animated once, the first time it is seen.
 */

import type { FarmSnapshot } from "../types";
import { diamondPath, drawStatic, drawWall, geo, hash, px, py } from "./farmSceneArt";
import { drawDino, drawEntity, drawGiant, drawHedgeBlock, drawTreasure } from "./farmScenePlants";
import { drawDrone, drawDroneShadow, drawSmoke, droneLift } from "./farmSceneDrone";
import { fxAbove, fxAct, fxActive, fxGround, fxLabels, fxReset, fxShake, fxSprout, fxUpdate } from "./farmSceneFx";

export type SceneView = { width: number; height: number; time: number };

type Ctx = CanvasRenderingContext2D;
type Surface = { getContext(kind: "2d"): Ctx | null; width: number; height: number };

const MAX_HW = 90;

// ---- layout -----------------------------------------------------------------------

function layout(w: number, h: number, W: number, H: number): void {
  const pad = Math.max(6, Math.min(W, H) * 0.03);
  const unitsW = w + h + 1;
  const unitsH = (w + h) / 2 + 3.4;
  let hw = Math.min(MAX_HW, (W - 2 * pad) / unitsW, (H - 2 * pad) / unitsH);
  hw = hw >= 4 ? Math.floor(hw / 2) * 2 : Math.max(0.5, hw);
  const hh = hw / 2;
  const thick = Math.round(hw * 0.8 * 2) / 2;
  const head = hw * 1.6;
  const total = (w + h) * hh + head + thick + hw;
  geo.hw = hw;
  geo.hh = hh;
  geo.thick = thick;
  geo.ox = Math.round((W - (w + h) * hw) / 2);
  geo.oy = Math.round((H - total) / 2 + head + h * hh);
}

// ---- the cached ground ------------------------------------------------------------

type Cache = {
  surface: Surface | null;
  W: number; H: number; w: number; h: number; hw: number; ox: number; oy: number; scale: number;
  g: Uint8Array;
};
const caches = new WeakMap<object, Cache>();
const looseCache: Cache = { surface: null, W: -1, H: -1, w: -1, h: -1, hw: -1, ox: -1, oy: -1, scale: -1, g: new Uint8Array(0) };

function makeSurface(w: number, h: number): Surface | null {
  try {
    if (typeof OffscreenCanvas !== "undefined") return new OffscreenCanvas(w, h) as unknown as Surface;
    if (typeof document !== "undefined") {
      const cv = document.createElement("canvas");
      cv.width = w;
      cv.height = h;
      return cv as unknown as Surface;
    }
  } catch {
    /* fall through to drawing directly */
  }
  return null;
}

function cacheFor(ctx: Ctx): Cache {
  const key = (ctx as unknown as { canvas?: object }).canvas;
  if (!key || typeof key !== "object") return looseCache;
  let c = caches.get(key);
  if (!c) {
    c = { surface: null, W: -1, H: -1, w: -1, h: -1, hw: -1, ox: -1, oy: -1, scale: -1, g: new Uint8Array(0) };
    caches.set(key, c);
  }
  return c;
}

function deviceScale(ctx: Ctx): number {
  const m = typeof ctx.getTransform === "function" ? ctx.getTransform() : null;
  let s = m ? Math.hypot(m.a, m.b) : 1;
  if (!(s > 0) || !Number.isFinite(s)) s = 1;
  return Math.min(3, Math.max(1, Math.round(s * 4) / 4));
}

function groundDrawn(ctx: Ctx, snap: FarmSnapshot, W: number, H: number): void {
  const { w, h } = snap;
  const cache = cacheFor(ctx);
  const scale = deviceScale(ctx);
  let same = cache.surface !== null && cache.W === W && cache.H === H && cache.w === w && cache.h === h &&
    cache.hw === geo.hw && cache.ox === geo.ox && cache.oy === geo.oy && cache.scale === scale && cache.g.length === w * h;
  if (same) {
    const tiles = snap.tiles;
    const g = cache.g;
    for (let i = 0; i < g.length; i++) {
      if (g[i] !== (tiles[i] && tiles[i].g === "S" ? 1 : 0)) { same = false; break; }
    }
  }
  if (!same) {
    cache.W = W; cache.H = H; cache.w = w; cache.h = h; cache.hw = geo.hw; cache.ox = geo.ox; cache.oy = geo.oy; cache.scale = scale;
    cache.g = new Uint8Array(w * h);
    for (let i = 0; i < w * h; i++) cache.g[i] = snap.tiles[i] && snap.tiles[i].g === "S" ? 1 : 0;
    cache.surface = null;
    const pw = Math.ceil(W * scale), ph = Math.ceil(H * scale);
    if (pw <= 4096 && ph <= 4096) {
      const s = makeSurface(pw, ph);
      const sc = s ? s.getContext("2d") : null;
      if (s && sc) {
        sc.setTransform(scale, 0, 0, scale, 0, 0);
        drawStatic(sc, snap.tiles, w, h, W, H);
        cache.surface = s;
      }
    }
  }
  if (cache.surface) {
    ctx.drawImage(cache.surface as unknown as CanvasImageSource, 0, 0, W, H);
  } else {
    drawStatic(ctx, snap.tiles, w, h, W, H);
  }
}

// ---- the drones' positions --------------------------------------------------------------

type DroneState = { fx: number; fy: number; tx: number; ty: number; t0: number; lean: number };
const droneStates: DroneState[] = [];
const drawn = { gx: 0, gy: 0, lean: 0 };

/** Where drone `i` is drawn at `time`: it slides between tiles over a moment. */
function droneAt(i: number, x: number, y: number, time: number): void {
  let s = droneStates[i];
  if (!s) {
    s = { fx: x, fy: y, tx: x, ty: y, t0: -1e9, lean: 0 };
    droneStates[i] = s;
  }
  if (time < s.t0) s.t0 = -1e9;
  if (x !== s.tx || y !== s.ty) {
    const near = Math.abs(x - s.tx) + Math.abs(y - s.ty) <= 1.5;
    if (near) {
      evalDrone(s, time);
      s.fx = drawn.gx;
      s.fy = drawn.gy;
      s.lean = Math.max(-1, Math.min(1, (x - s.tx) + (y - s.ty)));
    } else {
      s.fx = x;
      s.fy = y;
      s.lean = 0;
    }
    s.tx = x;
    s.ty = y;
    s.t0 = time;
  }
  evalDrone(s, time);
}

function evalDrone(s: DroneState, time: number): void {
  const q = Math.max(0, Math.min(1, (time - s.t0) / 0.14));
  const e = 1 - (1 - q) * (1 - q);
  drawn.gx = s.fx + (s.tx - s.fx) * e;
  drawn.gy = s.fy + (s.ty - s.fy) * e;
  const decay = 1 - Math.max(0, Math.min(1, (time - s.t0) / 0.5));
  drawn.lean = s.lean * decay;
}

/** Forget everything remembered between frames (drone motion, caches, event memory). */
export function resetSceneState(): void {
  droneStates.length = 0;
  looseCache.surface = null;
  looseCache.W = -1;
  fxReset();
}

// ---- the scene ----------------------------------------------------------------------------

let tailIdx = new Int16Array(0);
const order: number[] = [];
const dpos: { cx: number; cy: number; d: number; hat: string; lean: number }[] = [];

export function drawScene(ctx: Ctx, snap: FarmSnapshot, view: SceneView): void {
  const W = view.width, H = view.height;
  const time = Number.isFinite(view.time) ? view.time : 0;
  ctx.save();
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#bfe6f3";
  ctx.fillRect(0, 0, W, H);
  const w = Math.max(1, snap.w | 0), h = Math.max(1, snap.h | 0);
  if (!(W > 0) || !(H > 0) || !Number.isFinite(W) || !Number.isFinite(H)) {
    ctx.restore();
    return;
  }
  layout(w, h, W, H);
  const tiles = snap.tiles;
  const hw = geo.hw;

  fxUpdate(snap, time);
  const fxOn = fxActive();

  groundDrawn(ctx, snap, W, H);

  const maze = snap.maze;

  // ground overlays: water, infection, the maze floor, then action highlights
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const t = tiles[y * w + x];
      if (!t) continue;
      if (t.w) {
        const wl = Math.min(1, t.w);
        ctx.globalAlpha = 0.12 + 0.3 * wl;
        ctx.fillStyle = "#3b78d0";
        diamondPath(ctx, x, y, 0.02);
        ctx.fill();
        if (hw >= 8) {
          const k = 0.5 + 0.5 * Math.sin(time * 2 + hash(x, y, 77) * 6.28);
          ctx.globalAlpha = (0.25 + 0.3 * k) * wl;
          ctx.strokeStyle = "#e6f4ff";
          ctx.lineWidth = Math.max(1, hw * 0.06);
          ctx.beginPath();
          ctx.moveTo(px(x + 0.3, y + 0.62), py(x + 0.3, y + 0.62));
          ctx.lineTo(px(x + 0.46, y + 0.62), py(x + 0.46, y + 0.62));
          ctx.moveTo(px(x + 0.6, y + 0.3), py(x + 0.6, y + 0.3));
          ctx.lineTo(px(x + 0.7, y + 0.3), py(x + 0.7, y + 0.3));
          ctx.stroke();
        }
        ctx.globalAlpha = 1;
      }
      if (t.i) {
        ctx.globalAlpha = 0.42;
        ctx.fillStyle = "#efe2fa";
        diamondPath(ctx, x, y, 0.02);
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      if (maze && (t.e === "Hedge" || t.e === "Treasure")) {
        ctx.globalAlpha = 0.42;
        ctx.fillStyle = "#e8d9a8";
        diamondPath(ctx, x, y, 0.04);
        ctx.fill();
        ctx.globalAlpha = 1;
      }
    }
  }
  if (fxOn) fxGround(ctx, time);

  // the drones: where they are, nearest last; shadows go under everything
  const list = snap.drones && snap.drones.length ? snap.drones : snap.drone ? [snap.drone] : [];
  dpos.length = list.length;
  for (let i = 0; i < list.length; i++) {
    const d = list[i];
    droneAt(i, d.x, d.y, time);
    const act = fxAct(i, time);
    const cx = px(drawn.gx + 0.5, drawn.gy + 0.5), cy = py(drawn.gx + 0.5, drawn.gy + 0.5);
    let slot = dpos[i];
    if (!slot) slot = dpos[i] = { cx: 0, cy: 0, d: 0, hat: "", lean: 0 };
    slot.cx = cx;
    slot.cy = cy;
    slot.d = i;
    slot.hat = d.hat;
    slot.lean = drawn.lean;
    drawDroneShadow(ctx, cx, cy, time, i, act);
  }

  // dinosaur: which tile is which segment of the tail
  const tail = snap.tail;
  const hasTail = !!tail && tail.length > 0;
  if (hasTail) {
    if (tailIdx.length < w * h) tailIdx = new Int16Array(w * h);
    tailIdx.fill(-1, 0, w * h);
    for (let k = 0; k < tail.length; k++) {
      const p = tail[k];
      if (p[0] >= 0 && p[0] < w && p[1] >= 0 && p[1] < h) tailIdx[p[1] * w + p[0]] = k;
    }
  }

  // the tiles, back to front: diagonals from the north-west corner to the south-east
  for (let d = -(h - 1); d <= w - 1; d++) {
    const x0 = Math.max(0, d), x1 = Math.min(w - 1, d + h - 1);
    for (let x = x0; x <= x1; x++) {
      const y = x - d;
      const i = y * w + x;
      const t = tiles[i];
      const cx = px(x + 0.5, y + 0.5);
      const cy = py(x + 0.5, y + 0.5);
      let bits = 15;
      let mx = -1, my = -1;
      if (maze) {
        mx = x - maze.x0;
        my = y - maze.y0;
        if (mx >= 0 && mx < maze.m && my >= 0 && my < maze.m) bits = maze.sides[my * maze.m + mx];
        else mx = -1;
      }
      const inMaze = mx >= 0;
      // hedge walls behind the tile
      if (inMaze) {
        if (!(bits & 1)) drawWall(ctx, "N", x, y);
        if (mx === 0 && !(bits & 8)) drawWall(ctx, "W", x, y);
      }
      if (t) {
        const e = t.e;
        const ti = hasTail ? tailIdx[i] : -1;
        if (ti >= 0 || e === "Dinosaur") {
          drawSegment(ctx, snap, ti, cx, cy, hw);
        } else if (t.giant) {
          const gnt = t.giant;
          if (x === gnt[0] + gnt[2] - 1 && y === gnt[1]) drawGiant(ctx, gnt[0], gnt[1], gnt[2], t, time);
        } else if (e) {
          if (e === "Hedge") {
            if (!maze) drawHedgeBlock(ctx, x, y);
          } else if (e === "Treasure") {
            drawTreasure(ctx, x, y, time);
          } else {
            const shake = fxOn ? fxShake(x, y, time) : 0;
            const mul = fxOn ? fxSprout(x, y, time) : 1;
            drawEntity(ctx, e, t, x, y, cx + shake, cy, time, mul);
          }
        }
      }
      // hedge walls in front of it
      if (inMaze) {
        if (!(bits & 2)) drawWall(ctx, "E", x, y);
        if (my === 0 && !(bits & 4)) drawWall(ctx, "S", x, y);
      }
    }
  }

  if (fxOn) fxAbove(ctx, time);

  // drones, the one further from the camera first
  order.length = dpos.length;
  for (let i = 0; i < dpos.length; i++) {
    let j = i;
    while (j > 0 && dpos[order[j - 1]].cy > dpos[i].cy) {
      order[j] = order[j - 1];
      j--;
    }
    order[j] = i;
  }
  for (let k = 0; k < order.length; k++) {
    const s = dpos[order[k]];
    drawDrone(ctx, s.cx, s.cy, time, s.d, s.hat, s.lean, fxAct(s.d, time));
  }

  fxLabels(ctx, time, W);

  if (snap.smoke && snap.smoke.length && dpos.length) {
    const s = dpos[0];
    const u = Math.max(hw, 9);
    drawSmoke(ctx, snap.smoke, s.cx, s.cy - droneLift(time, 0, 0) - u * 0.95, W, H);
  }

  ctx.restore();
}

function drawSegment(ctx: Ctx, snap: FarmSnapshot, ti: number, cx: number, cy: number, hw: number): void {
  const tail = snap.tail;
  const len = Math.max(1, tail.length);
  const r = hw * (0.36 - 0.14 * (Math.max(0, ti) / len));
  let prev: [number, number] | null = null;
  let next: [number, number] | null = null;
  if (ti >= 0) {
    const a = ti === 0 ? snap.drone : null;
    const pp = a ? [a.x, a.y] : tail[ti - 1];
    if (pp) prev = [px(pp[0] + 0.5, pp[1] + 0.5), py(pp[0] + 0.5, pp[1] + 0.5)];
    const nn = tail[ti + 1];
    if (nn) next = [px(nn[0] + 0.5, nn[1] + 0.5), py(nn[0] + 0.5, nn[1] + 0.5)];
  }
  drawDino(ctx, cx, cy, r, prev, next, ti === tail.length - 1);
}
