/**
 * What grows on the farm, as chunky flat-shaded shapes seen from the scene's
 * isometric camera (see farmSceneArt.ts for the axes). Every plant has a soft
 * shadow, a light face and a darker face; its size follows growth `p`
 * smoothly from a sapling (a quarter size) to ripe (full size, brighter, with
 * a gentle pulsing highlight). Plants sway a hair with `time`.
 *
 * Each function draws around the tile's centre point (cx, cy) on the ground.
 */

import type { FarmCell } from "../types";
import { TAU, at, dome, ell, geo, hash, quad, ramp, shadowAt, sick, tri, box, px, py } from "./farmSceneArt";

type Ctx = CanvasRenderingContext2D;
type Look = Pick<FarmCell, "p" | "n" | "s" | "i">;

/** The colour of what a crop throws up when it is harvested. */
export const CROP_COLOUR: Record<string, string> = {
  Grass: "#f0d85a",
  Carrot: "#f28c28",
  Pumpkin: "#f08a24",
  Bush: "#3ea34a",
  Cactus: "#4cc468",
  Tree: "#b07a42",
  Sunflower: "#ffd83a",
  Dead_Pumpkin: "#8a8272",
  Apple: "#e5484d",
};

const GRASS_D = ramp("#3f8a2f", "#4fae3a"), GRASS_L = ramp("#5aa83a", "#9be05a");
const BUSH_D = ramp("#2f7a35", "#238a3a"), BUSH_M = ramp("#3f9a3f", "#2faa48"), BUSH_L = ramp("#58b44c", "#5ed166");
const TREE_D = ramp("#2f7a33", "#1f8a3a"), TREE_L = ramp("#4aa642", "#47c25a");
const PUMPKIN_D = ramp("#6f9a35", "#d86f10"), PUMPKIN_M = ramp("#98bf4a", "#f28a1e"), PUMPKIN_L = ramp("#b4d466", "#ffab45");
const CACTUS_D = ramp("#4f9a55", "#2f9a4e"), CACTUS_L = ramp("#79bf6c", "#4fcd70");
const CARROT_LEAF_D = ramp("#3f8a35", "#2f9a3a"), CARROT_LEAF_L = ramp("#5fb14a", "#56cc55");
const SUN_PETAL = ramp("#9bbf4a", "#ffd83a");

function ripeGlint(c: Ctx, x: number, y: number, r: number, time: number, salt: number): void {
  c.globalAlpha = 0.12 + 0.1 * (0.5 + 0.5 * Math.sin(time * 2.1 + salt * TAU));
  c.fillStyle = "#ffffff";
  c.beginPath();
  c.ellipse(x - r * 0.3, y - r * 0.35, r * 0.3, r * 0.18, -0.6, 0, TAU);
  c.fill();
  c.globalAlpha = 1;
}

let SK = false;
function f(c: Ctx, col: string): void {
  c.fillStyle = SK ? sick(col) : col;
}
function lobe(c: Ctx, x: number, y: number, r: number, dark: string, lite: string, glint = false): void {
  dome(c, x, y, r, SK ? sick(dark) : dark, SK ? sick(lite) : lite, glint);
}

export function drawEntity(
  c: Ctx, e: string, t: Look, x: number, y: number, cx: number, cy: number, time: number, mul = 1,
): void {
  const hw = geo.hw;
  const p = t.p === undefined ? 1 : Math.max(0, Math.min(1, t.p));
  const s = (0.25 + 0.75 * p) * mul;
  const ripe = p >= 0.999;
  const salt = hash(x, y, 5);
  const sway = Math.sin(time * 1.4 + salt * TAU);
  SK = !!t.i;
  switch (e) {
    case "Grass": grass(c, cx, cy, hw, p, s, ripe, sway, x, y); break;
    case "Bush": bush(c, cx, cy, hw, p, s, ripe, sway, x, y, time, salt); break;
    case "Tree": tree(c, cx, cy, hw, p, s, ripe, sway, time, salt); break;
    case "Carrot": carrot(c, cx, cy, hw, p, s, ripe, sway, x, y); break;
    case "Pumpkin": pumpkin(c, cx, cy, hw * 0.52 * s, p, 1, 3, false, time, salt); break;
    case "Dead_Pumpkin": pumpkin(c, cx, cy, hw * 0.4, 1, 0.78, 3, true, time, salt); break;
    case "Sunflower": sunflower(c, cx, cy, hw, p, s, ripe, sway, t.n ?? 8, time, salt); break;
    case "Cactus": cactus(c, cx, cy, hw, p, s, ripe, t.n ?? 0, t.s === 1, time, salt); break;
    case "Apple": apple(c, cx, cy, hw, time, salt); break;
    default: break;
  }
  if (SK && e !== "") spores(c, cx, cy - hw * 0.9 * Math.max(0.5, s), hw, time, salt);
  SK = false;
}

/** A giant pumpkin covering n x n tiles, whose south-west tile is (gx, gy). */
export function drawGiant(c: Ctx, gx: number, gy: number, n: number, t: Look, time: number): void {
  const hw = geo.hw;
  const p = t.p === undefined ? 1 : Math.max(0, Math.min(1, t.p));
  const s = 0.45 + 0.55 * p;
  SK = !!t.i;
  const cx = px(gx + n / 2, gy + n / 2), cy = py(gx + n / 2, gy + n / 2);
  pumpkin(c, cx, cy, n * hw * 0.72 * s, p, 1, 5, false, time, hash(gx, gy, 9));
  SK = false;
}

function spores(c: Ctx, cx: number, cy: number, hw: number, time: number, salt: number): void {
  c.fillStyle = "rgba(214,190,240,0.85)";
  for (let k = 0; k < 3; k++) {
    const ph = time * 0.9 + salt * 3 + k * 0.33;
    const fr = ph - Math.floor(ph);
    c.beginPath();
    c.arc(cx + (k - 1) * hw * 0.22 + Math.sin(ph * 6 + k) * hw * 0.05, cy - fr * hw * 0.4, Math.max(0.8, hw * 0.045), 0, TAU);
    c.fill();
  }
}

function grass(c: Ctx, cx: number, cy: number, hw: number, p: number, s: number, ripe: boolean, sway: number, x: number, y: number): void {
  const tall = hw * 0.74 * s;
  shadowAt(c, cx, cy + hw * 0.03, hw * 0.36 * s + hw * 0.06);
  for (let pass = 0; pass < 2; pass++) {
    f(c, at(pass ? GRASS_L : GRASS_D, p));
    c.beginPath();
    for (let k = pass; k < 8; k += 2) {
      const bx = cx + (hash(x * 9 + k, y, 41) - 0.5) * hw * 0.62;
      const by = cy + (hash(x * 9 + k, y, 42) - 0.5) * hw * 0.2;
      const hgt = tall * (0.6 + 0.4 * hash(x * 9 + k, y, 43));
      const lean = (hash(x * 9 + k, y, 44) - 0.5) * hw * 0.3 * s + sway * hw * 0.06 * s;
      const wd = Math.max(0.8, hw * 0.07);
      c.moveTo(bx - wd, by);
      c.lineTo(bx + lean, by - hgt);
      c.lineTo(bx + wd, by);
      c.closePath();
    }
    c.fill();
  }
  if (ripe) ripeGlint(c, cx, cy - tall * 0.5, hw * 0.3, 0, hash(x, y, 7));
}

function bush(c: Ctx, cx: number, cy: number, hw: number, p: number, s: number, ripe: boolean, sway: number, x: number, y: number, time: number, salt: number): void {
  const R = hw * 0.5 * s;
  const sw = sway * hw * 0.015 * s;
  shadowAt(c, cx, cy + hw * 0.03, R * 1.2);
  lobe(c, cx - R * 0.6, cy - R * 0.55, R * 0.62, at(BUSH_D, p), at(BUSH_M, p));
  lobe(c, cx + R * 0.6, cy - R * 0.55, R * 0.62, at(BUSH_D, p), at(BUSH_M, p));
  lobe(c, cx + sw, cy - R * 0.95, R * 0.88, at(BUSH_D, p), at(BUSH_M, p));
  lobe(c, cx - R * 0.12 + sw, cy - R * 1.12, R * 0.6, at(BUSH_M, p), at(BUSH_L, p), true);
  if (p > 0.5) {
    const n = ripe ? 5 : 3;
    for (let k = 0; k < n; k++) {
      const bx = cx + (hash(x, y, 60 + k) - 0.5) * R * 1.5 + sw;
      const by = cy - R * (0.45 + hash(x, y, 70 + k) * 0.85);
      const br = Math.max(0.9, R * 0.12);
      ell(c, bx, by + br * 0.25, br, br, SK ? sick("#a82040") : "#a82040");
      ell(c, bx - br * 0.15, by, br * 0.85, br * 0.85, SK ? sick("#ee4863") : "#ee4863");
    }
  }
  if (ripe) ripeGlint(c, cx, cy - R, R, time, salt);
}

function tree(c: Ctx, cx: number, cy: number, hw: number, p: number, s: number, ripe: boolean, sway: number, time: number, salt: number): void {
  const tw = Math.max(1.2, hw * 0.09 * (0.6 + 0.4 * s));
  const th = hw * 0.62 * s;
  const R = hw * 0.62 * s;
  const sw = sway * hw * 0.03 * s;
  shadowAt(c, cx + hw * 0.1, cy + hw * 0.03, R * 1.1);
  f(c, "#a8703f");
  c.fillRect(cx - tw, cy - th, tw, th);
  f(c, "#7f512b");
  c.fillRect(cx, cy - th, tw, th);
  ell(c, cx, cy, tw * 1.5, tw * 0.75, SK ? sick("#6d4524") : "#6d4524");
  const top = cy - th;
  lobe(c, cx - R * 0.5 + sw * 0.5, top - R * 0.35, R * 0.7, at(TREE_D, p), at(TREE_L, p));
  lobe(c, cx + R * 0.52 + sw * 0.5, top - R * 0.3, R * 0.66, at(TREE_D, p), at(TREE_L, p));
  lobe(c, cx + sw, top - R * 0.85, R * 0.85, at(TREE_D, p), at(TREE_L, p), true);
  if (ripe) ripeGlint(c, cx + sw, top - R * 0.95, R, time, salt);
}

function carrot(c: Ctx, cx: number, cy: number, hw: number, p: number, s: number, ripe: boolean, sway: number, x: number, y: number): void {
  shadowAt(c, cx, cy + hw * 0.02, hw * 0.28);
  ell(c, cx, cy, hw * 0.3, hw * 0.15, SK ? sick("#6f4528") : "#6f4528");
  ell(c, cx, cy - hw * 0.02, hw * 0.24, hw * 0.115, SK ? sick("#8a5a35") : "#8a5a35");
  if (p > 0.3) {
    const r = hw * 0.15 * s * (ripe ? 1.15 : 1);
    ell(c, cx, cy - hw * 0.03, r, r * 0.5, SK ? sick("#e07a1a") : "#e07a1a");
    ell(c, cx - r * 0.15, cy - hw * 0.045, r * 0.8, r * 0.38, SK ? sick("#ff9d3a") : "#ff9d3a");
  }
  const L = hw * 0.62 * s;
  for (let pass = 0; pass < 2; pass++) {
    f(c, at(pass ? CARROT_LEAF_L : CARROT_LEAF_D, p));
    c.beginPath();
    const n = pass ? 2 : 3;
    for (let k = 0; k < n; k++) {
      const a = (pass ? (k - 0.5) * 0.7 : (k - 1) * 0.95) + (hash(x, y, 80 + k + pass * 5) - 0.5) * 0.25 + sway * 0.06;
      const len = L * (0.75 + 0.25 * hash(x, y, 90 + k));
      const bx = cx, by = cy - hw * 0.03;
      const tx = bx + Math.sin(a) * len * 0.75, ty = by - Math.cos(a) * len;
      const wd = Math.max(0.8, hw * 0.07 * (0.5 + 0.5 * s));
      c.moveTo(bx - wd, by);
      c.lineTo(tx, ty);
      c.lineTo(bx + wd, by);
      c.closePath();
    }
    c.fill();
  }
}

/** One pumpkin: ribbed lobes, a stem. `flat` squashes it; `lobes` is 3, or 5 for a giant. */
function pumpkin(c: Ctx, cx: number, cy: number, R: number, p: number, flat: number, lobes: number, dead: boolean, time: number, salt: number): void {
  R = Math.max(1, R);
  const dk = dead ? "#6d675a" : at(PUMPKIN_D, p);
  const md = dead ? "#847d6d" : at(PUMPKIN_M, p);
  const lt = dead ? "#968f7e" : at(PUMPKIN_L, p);
  shadowAt(c, cx, cy + R * 0.05, R * 1.15);
  const ry = R * 0.82 * flat;
  const by = cy - ry * 0.85;
  const rx = R * (lobes === 5 ? 0.42 : 0.56);
  const order = lobes === 5 ? [-2, 2, -1, 1, 0] : [-1, 1, 0];
  for (let i = 0; i < order.length; i++) {
    const k = order[i];
    const ox = k * (lobes === 5 ? R * 0.3 : R * 0.42);
    const m = Math.abs(k) === (lobes === 5 ? 2 : 1) ? dk : Math.abs(k) === 1 && lobes === 5 ? md : lt;
    const hh = k === 0 ? ry : ry * (1 - 0.1 * Math.abs(k));
    ell(c, cx + ox, by, rx, hh, SK ? sick(m) : m);
    if (k !== 0) {
      c.strokeStyle = "rgba(0,0,0,0.13)";
      c.lineWidth = Math.max(0.6, R * 0.04);
      c.beginPath();
      c.ellipse(cx + ox, by, rx, hh, 0, 0, TAU);
      c.stroke();
    }
  }
  // stem
  const sw = Math.max(1, R * 0.12);
  f(c, dead ? "#5b4a33" : "#4c8a3a");
  c.fillRect(cx - sw, by - ry - R * 0.18, sw * 2, R * 0.28);
  if (!dead && p >= 0.999) ripeGlint(c, cx, by, R, time, salt);
  if (dead) {
    c.strokeStyle = "rgba(40,36,28,0.55)";
    c.lineWidth = Math.max(0.8, R * 0.06);
    c.beginPath();
    c.moveTo(cx - R * 0.25, by - ry * 0.4);
    c.lineTo(cx - R * 0.05, by + ry * 0.05);
    c.lineTo(cx + R * 0.2, by - ry * 0.05);
    c.stroke();
  }
}

function sunflower(c: Ctx, cx: number, cy: number, hw: number, p: number, s: number, ripe: boolean, sway: number, petals: number, time: number, salt: number): void {
  const H = hw * 1.0 * s;
  const sw = sway * hw * 0.05 * s;
  shadowAt(c, cx, cy + hw * 0.03, hw * 0.24);
  // stem and two leaves
  c.strokeStyle = SK ? sick("#3f8a35") : "#3f8a35";
  c.lineWidth = Math.max(1, hw * 0.09 * (0.5 + 0.5 * s));
  c.beginPath();
  c.moveTo(cx, cy);
  c.quadraticCurveTo(cx + sw * 0.2, cy - H * 0.5, cx + sw, cy - H);
  c.stroke();
  const lw = hw * 0.2 * s;
  tri(c, SK ? sick("#55b04a") : "#55b04a", cx, cy - H * 0.3, cx - lw * 1.6, cy - H * 0.32 - lw * 0.5, cx, cy - H * 0.2);
  tri(c, SK ? sick("#47993e") : "#47993e", cx, cy - H * 0.42, cx + lw * 1.6, cy - H * 0.46 - lw * 0.5, cx, cy - H * 0.32);
  const hx = cx + sw, hy = cy - H - hw * 0.04;
  const Rh = hw * 0.42 * s;
  const pn = Math.max(3, Math.min(30, Math.round(petals)));
  const grow = Math.max(0, Math.min(1, (p - 0.2) / 0.8));
  // petals in one path: a fill and an outline, so each one can be counted
  const pr = Rh * (0.55 + 0.45 * grow);
  const col = at(SUN_PETAL, p);
  f(c, col);
  c.strokeStyle = SK ? sick("#c58a10") : "#c58a10";
  c.lineWidth = Math.max(0.6, hw * 0.025);
  c.beginPath();
  for (let k = 0; k < pn; k++) {
    const a = (k / pn) * TAU - Math.PI / 2;
    const ex = hx + Math.cos(a) * pr * 0.72, ey = hy + Math.sin(a) * pr * 0.72 * 0.88;
    c.moveTo(ex + Math.cos(a) * pr * 0.32, ey);
    c.ellipse(ex, ey, Math.max(0.5, pr * 0.34), Math.max(0.5, pr * 0.15), a, 0, TAU);
  }
  c.fill();
  if (hw >= 8 && grow > 0.4) c.stroke();
  const dr = Rh * 0.42;
  ell(c, hx, hy, dr, dr * 0.9, SK ? sick(p < 0.5 ? "#6aa04a" : "#5a381c") : p < 0.5 ? "#6aa04a" : "#5a381c");
  ell(c, hx - dr * 0.15, hy - dr * 0.12, dr * 0.72, dr * 0.64, SK ? sick(p < 0.5 ? "#86bd5e" : "#7a4e28") : p < 0.5 ? "#86bd5e" : "#7a4e28");
  if (ripe) ripeGlint(c, hx, hy, Rh, time, salt);
}

function cactus(c: Ctx, cx: number, cy: number, hw: number, p: number, s: number, ripe: boolean, size: number, sorted: boolean, time: number, salt: number): void {
  const n = Math.max(0, Math.min(12, size));
  const H = hw * (0.34 + 0.085 * n) * s;
  const W = hw * (0.15 + 0.012 * n) * (0.6 + 0.4 * s);
  shadowAt(c, cx, cy + hw * 0.03, W * 2.3 + hw * 0.08);
  const dk = sorted ? "#2fa656" : ripe ? "#3f8a48" : at(CACTUS_D, p);
  const lt = sorted ? "#58d97a" : ripe ? "#6bb35c" : at(CACTUS_L, p);
  // arms first, so the trunk overlaps their roots
  if (n >= 3) {
    const aw = W * 0.55, al = H * 0.3;
    capsule(c, cx - W * 1.2, cy - H * 0.5, aw, al * 0.5, dk, lt, SK);
    capsule(c, cx + W * 1.2, cy - H * 0.62, aw, al * 0.7, dk, lt, SK);
    f(c, dk);
    c.fillRect(cx - W * 1.2, cy - H * 0.5, W * 1.2, aw * 0.9);
    c.fillRect(cx, cy - H * 0.62, W * 1.2, aw * 0.9);
  }
  capsule(c, cx, cy, W, H, dk, lt, SK);
  // ribs
  c.strokeStyle = "rgba(0,0,0,0.12)";
  c.lineWidth = Math.max(0.6, hw * 0.025);
  c.beginPath();
  c.moveTo(cx + W * 0.05, cy - H + W * 0.4);
  c.lineTo(cx + W * 0.05, cy);
  c.stroke();
  if (ripe) {
    ell(c, cx, cy - H - W * 0.15, W * 0.5, W * 0.32, "#ff8fb3");
    ell(c, cx, cy - H - W * 0.2, W * 0.26, W * 0.17, "#ffd23a");
    if (sorted) ripeGlint(c, cx, cy - H * 0.6, W * 1.8, time, salt);
  }
  if (hw >= 24) {
    c.font = `bold ${Math.round(hw * 0.4)}px ui-monospace, monospace`;
    c.textAlign = "center";
    c.textBaseline = "middle";
    c.lineWidth = 3;
    c.lineJoin = "round";
    c.strokeStyle = "#1b3a22";
    c.strokeText(String(size), cx, cy + hw * 0.22);
    c.fillStyle = "#ffffff";
    c.fillText(String(size), cx, cy + hw * 0.22);
    c.textAlign = "start";
    c.textBaseline = "alphabetic";
  }
}

function capsule(c: Ctx, cx: number, cy: number, w: number, h: number, dark: string, lite: string, sk: boolean): void {
  const d = sk ? sick(dark) : dark, l = sk ? sick(lite) : lite;
  // right half darker, left half lighter, both with a rounded top
  c.fillStyle = d;
  c.beginPath();
  c.moveTo(cx - w, cy);
  c.lineTo(cx - w, cy - h + w);
  c.ellipse(cx, cy - h + w, w, w * 0.95, 0, Math.PI, 0);
  c.lineTo(cx + w, cy);
  c.ellipse(cx, cy, w, w * 0.5, 0, 0, Math.PI);
  c.closePath();
  c.fill();
  c.fillStyle = l;
  c.beginPath();
  c.moveTo(cx - w, cy);
  c.lineTo(cx - w, cy - h + w);
  c.ellipse(cx, cy - h + w, w, w * 0.95, 0, Math.PI, Math.PI * 1.5);
  c.lineTo(cx, cy + w * 0.5);
  c.ellipse(cx, cy, w, w * 0.5, 0, Math.PI / 2, Math.PI);
  c.closePath();
  c.fill();
}

export function apple(c: Ctx, cx: number, cy: number, hw: number, time: number, salt: number): void {
  const R = hw * 0.3;
  const bob = Math.sin(time * 2.4 + salt * TAU) * hw * 0.035;
  shadowAt(c, cx, cy + hw * 0.03, R * (1.1 - bob / hw));
  dome(c, cx, cy - R * 1.05 + bob, R, "#c2303c", "#ec4a52");
  c.strokeStyle = "#6d4524";
  c.lineWidth = Math.max(1, hw * 0.05);
  c.beginPath();
  c.moveTo(cx, cy - R * 2 + bob);
  c.lineTo(cx + R * 0.1, cy - R * 2.5 + bob);
  c.stroke();
  tri(c, "#4fb04a", cx + R * 0.1, cy - R * 2.3 + bob, cx + R * 0.75, cy - R * 2.6 + bob, cx + R * 0.35, cy - R * 2 + bob);
}

/** A gold chest with coins on top, glinting. */
export function drawTreasure(c: Ctx, x: number, y: number, time: number): void {
  const hw = geo.hw;
  const z1 = hw * 0.3;
  shadowAt(c, px(x + 0.5, y + 0.5), py(x + 0.5, y + 0.5) + hw * 0.04, hw * 0.45);
  box(c, x + 0.26, y + 0.3, x + 0.74, y + 0.7, 0, z1, "#b9783a", "#9c6430", "#77491f");
  // gold band and lid
  box(c, x + 0.26, y + 0.3, x + 0.74, y + 0.7, z1, z1 + hw * 0.12, "#ffe27a", "#f2c94c", "#c79a2c");
  box(c, x + 0.46, y + 0.28, x + 0.54, y + 0.32, z1 * 0.35, z1 * 0.75, "#fff0a8", "#ffd23a", "#c79a2c");
  // a heap of coins on the lid
  const cx = px(x + 0.5, y + 0.5), cy = py(x + 0.5, y + 0.5, z1 + hw * 0.12);
  const r = hw * 0.12;
  for (let k = 0; k < 5; k++) {
    const ox = (k - 2) * r * 0.85;
    const oy = -(k === 2 ? r * 0.9 : k % 2 ? r * 0.2 : r * 0.35);
    ell(c, cx + ox, cy + oy + r * 0.2, r, r * 0.55, "#c79a2c");
    ell(c, cx + ox, cy + oy, r, r * 0.55, "#ffd23a");
  }
  // glints
  for (let k = 0; k < 2; k++) {
    const ph = 0.5 + 0.5 * Math.sin(time * 3 + k * 2.4);
    if (ph < 0.35) continue;
    const gx = cx + (k ? 1 : -1) * hw * 0.2, gy = cy - hw * 0.12 - k * hw * 0.1;
    const a = hw * 0.1 * ph;
    c.fillStyle = "#ffffff";
    c.globalAlpha = ph;
    quad(c, "#ffffff", gx - a, gy, gx, gy - a * 1.4, gx + a, gy, gx, gy + a * 1.4);
    c.globalAlpha = 1;
  }
}

/** A cube of hedge, for a Hedge tile that has no maze around it. */
export function drawHedgeBlock(c: Ctx, x: number, y: number): void {
  box(c, x + 0.1, y + 0.1, x + 0.9, y + 0.9, 0, geo.hw * 0.6, "#4fb04a", "#2f8f3f", "#226f32");
}

/** A dinosaur segment: a green body with back spikes, joined to its neighbours. */
export function drawDino(
  c: Ctx, cx: number, cy: number, r: number, nbA: [number, number] | null, nbB: [number, number] | null, last: boolean,
): void {
  const hw = geo.hw;
  shadowAt(c, cx, cy + hw * 0.03, r * 1.2);
  const lift = r * 0.55;
  c.lineCap = "round";
  c.lineWidth = Math.max(1, r * 1.3);
  c.strokeStyle = "#4aa84f";
  for (const nb of [nbA, nbB]) {
    if (!nb) continue;
    c.beginPath();
    c.moveTo(cx, cy - lift);
    c.lineTo((cx + nb[0]) / 2, (cy + nb[1]) / 2 - lift);
    c.stroke();
  }
  c.lineCap = "butt";
  for (let k = -1; k <= 1; k += 2) {
    tri(c, "#2f8a3f", cx + k * r * 0.45, cy - lift - r * 0.65, cx + k * r * 0.1, cy - lift - r * 1.5 + (k > 0 ? 0 : r * 0.2), cx - k * r * 0.2, cy - lift - r * 0.7);
  }
  dome(c, cx, cy - lift, last ? r * 0.8 : r, "#3f9a45", "#6bd073");
  ell(c, cx - r * 0.3, cy - lift - r * 0.1, r * 0.17, r * 0.12, "#2f7a38");
  ell(c, cx + r * 0.25, cy - lift + r * 0.25, r * 0.14, r * 0.1, "#2f7a38");
}
