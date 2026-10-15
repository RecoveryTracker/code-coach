/**
 * Making every drone ACTION visible: harvests pop their crop up and burst,
 * plants sprout, soil is tilled in a wipe of dust, water falls and ripples,
 * fertilizer sparkles, a swap swirls - each with a highlight on the tile it
 * acted on, and a quick dip of the drone that did it.
 *
 * The snapshot carries `events` (see FarmEvent in types.ts): the most recent
 * ones, oldest first, each with a unique rising `n`. This module remembers the
 * highest `n` it has seen and starts an animation exactly once for each newer
 * event, timed from the scene's own clock (`view.time`), so a snapshot drawn
 * a hundred times does not replay anything. Rules:
 *
 *   - the first snapshot that carries `events` (and any snapshot of a farm of
 *     a different size) is only a baseline: its old events are not replayed;
 *   - if `n` goes DOWN (a reset, another farm) all animations are dropped;
 *   - at most MAX_ANIMS animations play at once, the newest winning, while
 *     repeated "+N Item" labels for the same item merge into one growing label;
 *   - every animation is over after its `life` (at most 1.2 s).
 */

import type { FarmEvent, FarmSnapshot } from "../types";
import { drawEntity, CROP_COLOUR } from "./farmScenePlants";
import { TAU, ell, geo, hash, px, py, quad, diamondPath } from "./farmSceneArt";

type Ctx = CanvasRenderingContext2D;

export const MAX_ANIMS = 12;
const MAX_LABELS = 8;
const LABEL_LIFE = 1.2;
const ACT_LIFE = 0.25;
const HIGHLIGHT_LIFE = 0.6;

type Anim = { n: number; k: FarmEvent["k"]; x: number; y: number; e: string; ok: boolean; d: number; t0: number; life: number };
type Label = { item: string; count: number; x: number; y: number; t0: number; slot: number };

const fx = {
  inited: false,
  lastN: 0,
  w: 0,
  h: 0,
  anims: [] as Anim[],
  labels: [] as Label[],
  actT0: [] as number[],
};

const LIFE: Record<string, number> = { harvest: 1.0, plant: 0.8, till: 0.8, water: 0.9, fertilize: 0.9, swap: 0.8, hat: 0.7, unlock: 1.0 };

export function fxReset(): void {
  fx.inited = false;
  fx.lastN = 0;
  fx.anims.length = 0;
  fx.labels.length = 0;
  fx.actT0.length = 0;
}

export function fxCount(): number {
  return fx.anims.length;
}

export function fxUpdate(snap: FarmSnapshot, time: number): void {
  if (snap.w !== fx.w || snap.h !== fx.h) {
    fxReset();
    fx.w = snap.w;
    fx.h = snap.h;
  }
  // drop what is over (or from a clock that has run backwards)
  let j = 0;
  for (let i = 0; i < fx.anims.length; i++) {
    const a = fx.anims[i];
    const age = time - a.t0;
    if (age >= 0 && age <= a.life) fx.anims[j++] = a;
  }
  fx.anims.length = j;
  j = 0;
  for (let i = 0; i < fx.labels.length; i++) {
    const l = fx.labels[i];
    const age = time - l.t0;
    if (age >= 0 && age <= LABEL_LIFE) fx.labels[j++] = l;
  }
  fx.labels.length = j;
  for (let d = 0; d < fx.actT0.length; d++) if (time < fx.actT0[d]) fx.actT0[d] = -1e9;

  const ev = snap.events;
  if (!ev) return;
  let maxN = 0;
  for (let i = 0; i < ev.length; i++) if (ev[i].n > maxN) maxN = ev[i].n;
  if (!fx.inited) {
    fx.inited = true;
    fx.lastN = maxN;
    return;
  }
  if (maxN < fx.lastN) {
    fx.anims.length = 0;
    fx.labels.length = 0;
    fx.actT0.length = 0;
    fx.lastN = maxN;
    return;
  }
  const base = fx.lastN;
  fx.lastN = maxN;
  let fresh = 0;
  for (let i = 0; i < ev.length; i++) if (ev[i].n > base) fresh++;
  if (fresh === 0) return;
  let seen = 0;
  for (let i = 0; i < ev.length; i++) {
    const e = ev[i];
    if (e.n <= base) continue;
    seen++;
    const d = Math.max(0, Math.min(63, e.d | 0));
    fx.actT0[d] = time;
    if (e.k === "harvest" && e.ok && e.items) {
      for (const item in e.items) {
        const q = e.items[item];
        if (q > 0) addLabel(item, q, e.x, e.y, time);
      }
    }
    // only the newest MAX_ANIMS of a big batch get to play
    if (fresh - seen >= MAX_ANIMS) continue;
    if (fx.anims.length >= MAX_ANIMS) fx.anims.shift();
    fx.anims.push({ n: e.n, k: e.k, x: e.x, y: e.y, e: e.e ?? "", ok: e.ok, d, t0: time, life: LIFE[e.k] ?? 0.8 });
  }
}

function addLabel(item: string, q: number, x: number, y: number, time: number): void {
  for (let i = 0; i < fx.labels.length; i++) {
    const l = fx.labels[i];
    if (l.item === item) {
      l.count += q;
      l.t0 = time;
      l.x = x;
      l.y = y;
      return;
    }
  }
  let slot = 0;
  for (let i = 0; i < fx.labels.length; i++) if (fx.labels[i].x === x && fx.labels[i].y === y) slot++;
  if (fx.labels.length >= MAX_LABELS) fx.labels.shift();
  fx.labels.push({ item, count: q, x, y, t0: time, slot });
}

/** 0..1: how far into its action dip the drone with this index is. */
export function fxAct(d: number, time: number): number {
  const t0 = fx.actT0[d];
  if (t0 === undefined) return 0;
  const age = time - t0;
  if (age < 0 || age > ACT_LIFE) return 0;
  return Math.sin((Math.PI * age) / ACT_LIFE);
}

export function fxActive(): boolean {
  return fx.anims.length > 0;
}

/** Sideways pixels to shake the tile's plant by (a failed harvest). */
export function fxShake(x: number, y: number, time: number): number {
  for (let i = 0; i < fx.anims.length; i++) {
    const a = fx.anims[i];
    if (a.x === x && a.y === y && a.k === "harvest" && !a.ok) {
      const age = time - a.t0;
      if (age >= 0 && age < 0.35) return Math.sin(age * 70) * geo.hw * 0.05 * (1 - age / 0.35);
    }
  }
  return 0;
}

/** Scale to draw the tile's plant at (a plant just put in grows up from nothing). */
export function fxSprout(x: number, y: number, time: number): number {
  for (let i = 0; i < fx.anims.length; i++) {
    const a = fx.anims[i];
    if (a.x === x && a.y === y && a.k === "plant" && a.ok) {
      const age = time - a.t0;
      if (age >= 0 && age < 0.5) {
        const q = age / 0.5 - 1;
        return Math.max(0.02, 1 + 2.70158 * q * q * q + 1.70158 * q * q);
      }
    }
  }
  return 1;
}

function colourOf(a: Anim): string {
  if (!a.ok && a.k !== "swap" && a.k !== "hat" && a.k !== "unlock") return "#ff5a4a";
  switch (a.k) {
    case "harvest": return "#ffe27a";
    case "plant": return "#9be26a";
    case "till": return "#d9a066";
    case "water": return "#6fb8ff";
    case "fertilize": return "#b6f06a";
    case "swap": return "#cfe8ff";
    case "unlock": return "#ffd23a";
    default: return "#ffffff";
  }
}

/** On the ground, under the plants: the target highlight, and the tilling wipe. */
export function fxGround(c: Ctx, time: number): void {
  const hw = geo.hw;
  for (let i = 0; i < fx.anims.length; i++) {
    const a = fx.anims[i];
    const age = time - a.t0;
    if (a.k === "hat" || age < 0 || age > HIGHLIGHT_LIFE) continue;
    const fade = 1 - age / HIGHLIGHT_LIFE;
    const col = colourOf(a);
    const cx = px(a.x + 0.5, a.y + 0.5), cy = py(a.x + 0.5, a.y + 0.5);
    // a soft beam from above, then the tile itself
    c.globalAlpha = 0.16 * fade;
    quad(c, col, cx - hw * 0.12, cy - hw * 1.7, cx + hw * 0.12, cy - hw * 1.7, cx + hw * 0.5, cy, cx - hw * 0.5, cy);
    c.globalAlpha = 0.3 * fade;
    c.fillStyle = col;
    diamondPath(c, a.x, a.y, 0.03);
    c.fill();
    c.globalAlpha = Math.min(1, fade * 1.4);
    c.strokeStyle = col;
    c.lineWidth = Math.max(1.5, hw * 0.1);
    c.lineJoin = "round";
    diamondPath(c, a.x, a.y, 0.05);
    c.stroke();
    if (a.k === "till" && a.ok) {
      // the old ground wiped away to the new, left to right
      const q = Math.min(1, age / 0.5);
      const lx = px(a.x, a.y), rx = px(a.x + 1, a.y + 1);
      const cut = lx + q * (rx - lx);
      c.save();
      c.beginPath();
      c.rect(cut, cy - hw, Math.max(0, rx - cut + 1), hw * 2);
      c.clip();
      c.globalAlpha = 0.55 * (1 - q * 0.5);
      c.fillStyle = "#d9b98a";
      diamondPath(c, a.x, a.y, 0.0);
      c.fill();
      c.restore();
    }
    c.globalAlpha = 1;
  }
}

const GHOST = { p: 1, n: 8, s: 0, i: 0 };

function burst(c: Ctx, cx: number, cy: number, age: number, life: number, count: number, col: string, speed: number, size: number, seed: number, up: number): void {
  const hw = geo.hw;
  const q = age / life;
  if (q >= 1) return;
  c.globalAlpha = 1 - q;
  c.fillStyle = col;
  c.beginPath();
  for (let i = 0; i < count; i++) {
    const a = hash(seed, i, 1) * TAU;
    const v = speed * (0.45 + hash(seed, i, 2) * 0.7);
    const x = cx + Math.cos(a) * v * age;
    const y = cy - hw * 0.2 + Math.sin(a) * v * age * 0.5 - up * age + hw * 1.6 * age * age;
    const s = size * (0.7 + hash(seed, i, 3) * 0.6);
    c.rect(x - s / 2, y - s / 2, s, s);
  }
  c.fill();
  c.globalAlpha = 1;
}

function puff(c: Ctx, cx: number, cy: number, age: number, life: number, col: string, big: number): void {
  const hw = geo.hw;
  const q = age / life;
  if (q >= 1) return;
  c.globalAlpha = 0.55 * (1 - q);
  for (let k = 0; k < 3; k++) {
    ell(c, cx + (k - 1) * hw * 0.16, cy - hw * 0.12 - q * hw * 0.5 - k * hw * 0.03,
      hw * (0.1 + big * q + k * 0.03), hw * (0.08 + big * q * 0.8 + k * 0.02), col);
  }
  c.globalAlpha = 1;
}

function sparkle(c: Ctx, x: number, y: number, r: number, col: string): void {
  quad(c, col, x - r, y, x, y - r * 1.5, x + r, y, x, y + r * 1.5);
  quad(c, col, x - r * 1.5, y, x, y - r * 0.5, x + r * 1.5, y, x, y + r * 0.5);
}

/** Above the plants: ghost crops, bursts, puffs, drops, ripples, sparkles, swirls. */
export function fxAbove(c: Ctx, time: number): void {
  const hw = geo.hw;
  for (let i = 0; i < fx.anims.length; i++) {
    const a = fx.anims[i];
    const age = time - a.t0;
    if (age < 0 || age > a.life) continue;
    const cx = px(a.x + 0.5, a.y + 0.5), cy = py(a.x + 0.5, a.y + 0.5);
    const seed = a.n;
    switch (a.k) {
      case "harvest":
        if (a.ok) {
          if (age < 0.55 && a.e) {
            const q = age / 0.55;
            c.globalAlpha = 1 - q * q;
            drawEntity(c, a.e, GHOST, a.x, a.y, cx, cy - hw * 0.9 * (1 - (1 - q) * (1 - q)), time, 1 + 0.15 * q);
            c.globalAlpha = 1;
          }
          burst(c, cx, cy, age, 0.8, 9, CROP_COLOUR[a.e] ?? "#cfe27a", hw * 1.3, Math.max(1.5, hw * 0.13), seed, hw * 1.2);
        } else {
          puff(c, cx, cy, age, 0.7, "#b8bec4", 0.28);
        }
        break;
      case "plant":
        if (a.ok) {
          puff(c, cx, cy, age, 0.7, "#8a6038", 0.22);
          burst(c, cx, cy, age, 0.6, 6, "#7a5030", hw * 0.8, Math.max(1.2, hw * 0.1), seed, hw * 0.5);
        }
        break;
      case "till":
        puff(c, cx, cy, age, 0.8, "#dcc08e", 0.34);
        break;
      case "water": {
        c.fillStyle = "#58acff";
        c.beginPath();
        for (let k = 0; k < 7; k++) {
          const delay = hash(seed, k, 4) * 0.3;
          const q = (age - delay) / 0.35;
          if (q <= 0 || q >= 1) continue;
          const x = cx + (hash(seed, k, 5) - 0.5) * hw * 0.9;
          const y = cy - hw * 1.6 * (1 - q) - hw * 0.1;
          c.moveTo(x + hw * 0.04, y);
          c.ellipse(x, y, hw * 0.04, hw * 0.08, 0, 0, TAU);
        }
        c.fill();
        const rq = (age - 0.2) / 0.65;
        if (rq > 0 && rq < 1) {
          c.globalAlpha = 1 - rq;
          c.strokeStyle = "#e6f4ff";
          c.lineWidth = Math.max(1, hw * 0.06);
          c.beginPath();
          c.ellipse(cx, cy, hw * (0.1 + 0.5 * rq), hw * (0.05 + 0.25 * rq), 0, 0, TAU);
          c.stroke();
          c.globalAlpha = 1;
        }
        break;
      }
      case "fertilize":
      case "unlock":
      case "hat": {
        const n = a.k === "unlock" ? 12 : a.k === "hat" ? 5 : 9;
        const lift = a.k === "hat" ? hw * 1.1 : 0;
        for (let k = 0; k < n; k++) {
          const q = age / a.life;
          const tw = 0.5 + 0.5 * Math.sin(age * 14 + k * 2.1);
          const x = cx + (hash(seed, k, 6) - 0.5) * hw * (a.k === "unlock" ? 1.4 : 0.9);
          const y = cy - lift - hw * 0.1 - q * hw * 1.1 * (0.6 + hash(seed, k, 7) * 0.7);
          c.globalAlpha = (1 - q) * (0.4 + 0.6 * tw);
          sparkle(c, x, y, Math.max(1, hw * 0.07 * (0.6 + tw * 0.6)),
            a.k === "hat" ? "#ffffff" : a.k === "unlock" ? (k & 1 ? "#ffd23a" : "#fff3b0") : k & 1 ? "#ffd84a" : "#b6f06a");
        }
        c.globalAlpha = 1;
        break;
      }
      case "swap": {
        const q = age / a.life;
        c.globalAlpha = 1 - q * q;
        c.strokeStyle = "#e8f3ff";
        c.fillStyle = "#e8f3ff";
        c.lineWidth = Math.max(1.5, hw * 0.09);
        c.lineCap = "round";
        for (let side = 0; side < 2; side++) {
          const a0 = age * 12 + side * Math.PI;
          const r = hw * 0.5;
          const cyy = cy - hw * 0.25;
          c.beginPath();
          c.ellipse(cx, cyy, r, r * 0.5, 0, a0, a0 + 1.9);
          c.stroke();
          const ea = a0 + 1.9;
          const ex = cx + Math.cos(ea) * r, ey = cyy + Math.sin(ea) * r * 0.5;
          const tx = -Math.sin(ea) * r, ty = Math.cos(ea) * r * 0.5;
          const tl = Math.hypot(tx, ty) || 1;
          const ux = tx / tl, uy = ty / tl;
          const s = hw * 0.16;
          c.beginPath();
          c.moveTo(ex + ux * s, ey + uy * s);
          c.lineTo(ex - uy * s * 0.7 - ux * s * 0.2, ey + ux * s * 0.7 - uy * s * 0.2);
          c.lineTo(ex + uy * s * 0.7 - ux * s * 0.2, ey - ux * s * 0.7 - uy * s * 0.2);
          c.closePath();
          c.fill();
        }
        c.lineCap = "butt";
        c.globalAlpha = 1;
        break;
      }
      default:
        break;
    }
  }
}

const ITEM_COLOUR: Record<string, string> = {
  Hay: "#ffe27a", Wood: "#d9a066", Carrot: "#ff9a3a", Pumpkin: "#ffa030", Cactus: "#7fe08a", Bone: "#f4f0e0",
  Gold: "#ffd23a", Power: "#8fd0ff", Weird_Substance: "#d68fff", Water: "#7fc4ff", Fertilizer: "#9be26a",
};

/** The rising "+4 Hay" labels, drawn last so nothing covers them. */
export function fxLabels(c: Ctx, time: number, W: number): void {
  if (fx.labels.length === 0) return;
  c.font = "bold 13px ui-monospace, monospace";
  c.textAlign = "center";
  c.textBaseline = "middle";
  c.lineJoin = "round";
  c.lineWidth = 3.5;
  for (let i = 0; i < fx.labels.length; i++) {
    const l = fx.labels[i];
    const age = time - l.t0;
    if (age < 0 || age > LABEL_LIFE) continue;
    const q = age / LABEL_LIFE;
    const text = "+" + l.count + " " + l.item.replace(/_/g, " ");
    const w = c.measureText(text).width;
    const x = Math.max(w / 2 + 3, Math.min(W - w / 2 - 3, px(l.x + 0.5, l.y + 0.5)));
    const y = Math.max(10, py(l.x + 0.5, l.y + 0.5) - geo.hw * 0.9 - 30 * (1 - (1 - q) * (1 - q)) - l.slot * 16);
    c.globalAlpha = q < 0.65 ? 1 : 1 - (q - 0.65) / 0.35;
    c.strokeStyle = "#1d2b1a";
    c.strokeText(text, x, y);
    c.fillStyle = ITEM_COLOUR[l.item] ?? "#ffffff";
    c.fillText(text, x, y);
  }
  c.globalAlpha = 1;
  c.textAlign = "start";
  c.textBaseline = "alphabetic";
}
