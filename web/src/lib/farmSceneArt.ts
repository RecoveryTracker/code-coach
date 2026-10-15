/**
 * Shared pieces of the farm scene: the isometric geometry, colours, and the
 * static parts of the picture (sky, slab, ground tiles, hedge walls).
 *
 * Axis mapping (the farm's own convention is that y grows north):
 *   screen x = ox + (gx + gy) * hw
 *   screen y = oy + (gx - gy) * hh - z          (hh = hw / 2: a 2:1 dimetric view)
 * so EAST is toward the bottom-right of the screen, NORTH toward the top-right,
 * WEST toward the top-left and SOUTH toward the bottom-left. The origin tile
 * (0, 0) is the farm's left-hand corner (south-west); the near, bottom corner
 * is the south-east one and the far, top corner the north-west one.
 * (gx, gy) are grid-corner coordinates: tile (x, y) spans gx x..x+1, gy y..y+1
 * and its centre is (x + .5, y + .5). z is pixels above the ground plane.
 *
 * Nothing here uses Math.random: the variation between tiles comes from hash().
 */

type Ctx = CanvasRenderingContext2D;

export const TAU = Math.PI * 2;

/** The current layout, set by drawScene before anything is drawn. */
export const geo = { hw: 16, hh: 8, ox: 0, oy: 0, thick: 12 };

export function px(gx: number, gy: number): number {
  return geo.ox + (gx + gy) * geo.hw;
}
export function py(gx: number, gy: number, z = 0): number {
  return geo.oy + (gx - gy) * geo.hh - z;
}

/** A deterministic number in [0, 1) for a tile and a purpose. */
export function hash(x: number, y: number, salt = 0): number {
  let h = Math.imul(x | 0, 374761393) ^ Math.imul(y | 0, 668265263) ^ Math.imul((salt | 0) + 7919, 1103515245);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}

// ---- colours -------------------------------------------------------------

function h2(n: number): string {
  return (n < 16 ? "0" : "") + n.toString(16);
}

export function mix(a: string, b: string, t: number): string {
  const ar = parseInt(a.slice(1, 3), 16), ag = parseInt(a.slice(3, 5), 16), ab = parseInt(a.slice(5, 7), 16);
  const br = parseInt(b.slice(1, 3), 16), bg = parseInt(b.slice(3, 5), 16), bb = parseInt(b.slice(5, 7), 16);
  return "#" + h2(Math.round(ar + (br - ar) * t)) + h2(Math.round(ag + (bg - ag) * t)) + h2(Math.round(ab + (bb - ab) * t));
}

/** f < 1 darkens, f > 1 lightens (1.2 is 20% of the way to white). */
export function shade(c: string, f: number): string {
  return f < 1 ? mix(c, "#000000", 1 - f) : mix(c, "#ffffff", Math.min(1, f - 1));
}

export function ramp(a: string, b: string, n = 8): string[] {
  const out: string[] = [];
  for (let i = 0; i <= n; i++) out.push(mix(a, b, i / n));
  return out;
}

export function at(r: string[], t: number): string {
  const k = !(t > 0) ? 0 : t >= 1 ? r.length - 1 : Math.round(t * (r.length - 1));
  return r[k];
}

const sickMemo = new Map<string, string>();
/** A plant's colour when it is infected: washed out toward pale lavender. */
export function sick(c: string): string {
  let s = sickMemo.get(c);
  if (s === undefined) {
    s = mix(c, "#e2d2f2", 0.62);
    sickMemo.set(c, s);
  }
  return s;
}

// ---- small drawing helpers ----------------------------------------------------

export function ell(c: Ctx, x: number, y: number, rx: number, ry: number, fill: string): void {
  c.fillStyle = fill;
  c.beginPath();
  c.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, ry), 0, 0, TAU);
  c.fill();
}

export function tri(c: Ctx, fill: string, x0: number, y0: number, x1: number, y1: number, x2: number, y2: number): void {
  c.fillStyle = fill;
  c.beginPath();
  c.moveTo(x0, y0);
  c.lineTo(x1, y1);
  c.lineTo(x2, y2);
  c.closePath();
  c.fill();
}

export function quad(
  c: Ctx, fill: string, x0: number, y0: number, x1: number, y1: number, x2: number, y2: number, x3: number, y3: number,
): void {
  c.fillStyle = fill;
  c.beginPath();
  c.moveTo(x0, y0);
  c.lineTo(x1, y1);
  c.lineTo(x2, y2);
  c.lineTo(x3, y3);
  c.closePath();
  c.fill();
}

/** A flat-shaded ball: dark body, lighter cap toward the sun (up-left), a glint. */
export function dome(c: Ctx, x: number, y: number, r: number, dark: string, lite: string, glint = true): void {
  r = Math.max(0.3, r);
  c.fillStyle = dark;
  c.beginPath();
  c.arc(x, y, r, 0, TAU);
  c.fill();
  c.fillStyle = lite;
  c.beginPath();
  c.arc(x - r * 0.08, y - r * 0.1, r * 0.88, 0, TAU);
  c.fill();
  if (glint && r > 3) {
    c.fillStyle = "rgba(255,255,255,0.26)";
    c.beginPath();
    c.ellipse(x - r * 0.3, y - r * 0.4, r * 0.24, r * 0.14, -0.6, 0, TAU);
    c.fill();
  }
}

export function shadowAt(c: Ctx, x: number, y: number, rx: number): void {
  c.fillStyle = "rgba(24, 48, 18, 0.24)";
  c.beginPath();
  c.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, rx * 0.5), 0, 0, TAU);
  c.fill();
}

/** An axis-aligned block in grid units, z in pixels; draws its three visible faces. */
export function box(
  c: Ctx, gx0: number, gy0: number, gx1: number, gy1: number, z0: number, z1: number,
  top: string, left: string, right: string,
): void {
  // top
  quad(c, top, px(gx0, gy0), py(gx0, gy0, z1), px(gx1, gy0), py(gx1, gy0, z1),
    px(gx1, gy1), py(gx1, gy1, z1), px(gx0, gy1), py(gx0, gy1, z1));
  // the face looking south (front-left)
  quad(c, left, px(gx0, gy0), py(gx0, gy0, z0), px(gx1, gy0), py(gx1, gy0, z0),
    px(gx1, gy0), py(gx1, gy0, z1), px(gx0, gy0), py(gx0, gy0, z1));
  // the face looking east (front-right)
  quad(c, right, px(gx1, gy0), py(gx1, gy0, z0), px(gx1, gy1), py(gx1, gy1, z0),
    px(gx1, gy1), py(gx1, gy1, z1), px(gx1, gy0), py(gx1, gy0, z1));
}

export function roundRect(c: Ctx, x: number, y: number, w: number, h: number, r: number): void {
  r = Math.min(r, w / 2, h / 2);
  c.beginPath();
  c.moveTo(x + r, y);
  c.lineTo(x + w - r, y);
  c.arc(x + w - r, y + r, r, -Math.PI / 2, 0);
  c.lineTo(x + w, y + h - r);
  c.arc(x + w - r, y + h - r, r, 0, Math.PI / 2);
  c.lineTo(x + r, y + h);
  c.arc(x + r, y + h - r, r, Math.PI / 2, Math.PI);
  c.lineTo(x, y + r);
  c.arc(x + r, y + r, r, Math.PI, Math.PI * 1.5);
  c.closePath();
}

/** The outline of one tile's top face as a path (not filled). */
export function diamondPath(c: Ctx, x: number, y: number, inset = 0): void {
  const a = inset, b = 1 - inset;
  c.beginPath();
  c.moveTo(px(x + a, y + a), py(x + a, y + a));
  c.lineTo(px(x + b, y + a), py(x + b, y + a));
  c.lineTo(px(x + b, y + b), py(x + b, y + b));
  c.lineTo(px(x + a, y + b), py(x + a, y + b));
  c.closePath();
}

// ---- the sky -------------------------------------------------------------------

export function drawBackground(c: Ctx, W: number, H: number): void {
  const g = c.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, "#86cdee");
  g.addColorStop(0.6, "#bfe6f3");
  g.addColorStop(1, "#e6f5ee");
  c.fillStyle = g;
  c.fillRect(0, 0, W, H);
  // a few soft clouds, kept wholly on the canvas
  const m = Math.min(W, H);
  c.fillStyle = "#ffffff";
  c.globalAlpha = 0.33;
  for (let k = 0; k < 6; k++) {
    const r = m * (0.03 + hash(k, 3, 50) * 0.035);
    const cx = r * 2.4 + hash(k, 1, 50) * Math.max(0, W - r * 4.8);
    const cy = r * 1.2 + hash(k, 2, 50) * Math.max(0, H * 0.75 - r * 2.4);
    c.beginPath();
    c.ellipse(cx, cy, r * 1.7, r * 0.5, 0, 0, TAU);
    c.ellipse(cx - r * 0.7, cy - r * 0.2, r * 0.9, r * 0.45, 0, 0, TAU);
    c.ellipse(cx + r * 0.6, cy - r * 0.28, r, r * 0.5, 0, 0, TAU);
    c.fill();
  }
  c.globalAlpha = 1;
  const v = c.createRadialGradient(W / 2, H / 2, m * 0.3, W / 2, H / 2, Math.hypot(W, H) * 0.55);
  v.addColorStop(0, "rgba(255,255,255,0)");
  v.addColorStop(1, "rgba(38,92,134,0.30)");
  c.fillStyle = v;
  c.fillRect(0, 0, W, H);
}

// ---- the slab -------------------------------------------------------------------

const GRASS_A = "#7ccf55", GRASS_B = "#72c44c";
const SOIL_A = "#8e5d38", SOIL_B = "#84552f";
const LIP_L = { G: "#5db240", S: "#7b4c2b" };
const LIP_R = { G: "#499a34", S: "#693f26" };
const EARTH_L = ["#a8744a", "#9f6c44"];
const EARTH_R = ["#8a5c3a", "#825535"];
const ROCK_L = ["#8d6a52", "#85634c"];
const ROCK_R = ["#6f5340", "#684d3b"];

type Tiles = { g: string }[];

function groundAt(tiles: Tiles, w: number, x: number, y: number): "G" | "S" {
  const t = tiles[y * w + x];
  return t && t.g === "S" ? "S" : "G";
}

/** Sky, the slab's soft shadow, its thick edges and every ground tile. */
export function drawStatic(c: Ctx, tiles: Tiles, w: number, h: number, W: number, H: number): void {
  const { hw, thick: T } = geo;
  drawBackground(c, W, H);

  // soft shadow on the void below the slab: nested ellipses, darker at the middle
  const midX = px(w / 2, h / 2);
  const midY = py(w / 2, h / 2) + T + hw * 0.9;
  const rx0 = ((w + h) / 2) * hw * 0.94;
  c.fillStyle = "#1d4a6b";
  c.globalAlpha = 0.055;
  for (let k = 0; k < 6; k++) {
    const f = 1 - k * 0.1;
    c.beginPath();
    c.ellipse(midX, midY, rx0 * f, rx0 * f * 0.5, 0, 0, TAU);
    c.fill();
  }
  c.globalAlpha = 1;

  // front-left edge (south side)
  for (let x = 0; x < w; x++) {
    const g = groundAt(tiles, w, x, 0);
    face(c, px(x, 0), py(x, 0), px(x + 1, 0), py(x + 1, 0), T, LIP_L[g], EARTH_L[x & 1], ROCK_L[x & 1]);
  }
  // front-right edge (east side)
  for (let y = 0; y < h; y++) {
    const g = groundAt(tiles, w, w - 1, y);
    face(c, px(w, y), py(w, y), px(w, y + 1), py(w, y + 1), T, LIP_R[g], EARTH_R[y & 1], ROCK_R[y & 1]);
  }

  // an underlay so the seams between tiles never show the sky
  quad(c, "#5aa83c", px(0, 0), py(0, 0), px(w, 0), py(w, 0), px(w, h), py(w, h), px(0, h), py(0, h));

  const detail = hw >= 6;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const soil = groundAt(tiles, w, x, y) === "S";
      const odd = (x + y) & 1;
      quad(c, soil ? (odd ? SOIL_B : SOIL_A) : odd ? GRASS_B : GRASS_A,
        px(x, y), py(x, y), px(x + 1, y), py(x + 1, y), px(x + 1, y + 1), py(x + 1, y + 1), px(x, y + 1), py(x, y + 1));
      if (!detail) continue;
      // a lit edge on the far sides, a shaded one on the near sides
      c.lineWidth = 1;
      c.strokeStyle = "rgba(255,255,255,0.13)";
      c.beginPath();
      c.moveTo(px(x, y), py(x, y));
      c.lineTo(px(x, y + 1), py(x, y + 1));
      c.lineTo(px(x + 1, y + 1), py(x + 1, y + 1));
      c.stroke();
      c.strokeStyle = "rgba(0,0,0,0.09)";
      c.beginPath();
      c.moveTo(px(x, y), py(x, y));
      c.lineTo(px(x + 1, y), py(x + 1, y));
      c.lineTo(px(x + 1, y + 1), py(x + 1, y + 1));
      c.stroke();
      if (soil) furrows(c, x, y);
      else tufts(c, x, y);
    }
  }
}

function face(
  c: Ctx, x0: number, y0: number, x1: number, y1: number, T: number, lip: string, earth: string, rock: string,
): void {
  const a = T * 0.26, b = T * 0.7;
  quad(c, lip, x0, y0, x1, y1, x1, y1 + a, x0, y0 + a);
  quad(c, earth, x0, y0 + a, x1, y1 + a, x1, y1 + b, x0, y0 + b);
  quad(c, rock, x0, y0 + b, x1, y1 + b, x1, y1 + T, x0, y0 + T);
}

function furrows(c: Ctx, x: number, y: number): void {
  const { hw } = geo;
  const lw = Math.max(1, hw * 0.07);
  c.lineWidth = lw;
  c.lineCap = "round";
  c.strokeStyle = "#5b3720";
  c.beginPath();
  for (let k = 1; k <= 3; k++) {
    c.moveTo(px(x + 0.14, y + k / 4), py(x + 0.14, y + k / 4));
    c.lineTo(px(x + 0.86, y + k / 4), py(x + 0.86, y + k / 4));
  }
  c.stroke();
  c.strokeStyle = "rgba(190,130,84,0.55)";
  c.beginPath();
  for (let k = 1; k <= 3; k++) {
    c.moveTo(px(x + 0.14, y + k / 4), py(x + 0.14, y + k / 4) + lw);
    c.lineTo(px(x + 0.86, y + k / 4), py(x + 0.86, y + k / 4) + lw);
  }
  c.stroke();
  c.lineCap = "butt";
}

function tufts(c: Ctx, x: number, y: number): void {
  const { hw } = geo;
  const n = hash(x, y, 1) < 0.55 ? 1 : hash(x, y, 2) < 0.4 ? 2 : 0;
  for (let k = 0; k < n; k++) {
    const u = 0.22 + hash(x, y, 10 + k) * 0.56;
    const v = 0.22 + hash(x, y, 20 + k) * 0.56;
    const bx = px(x + u, y + v), by = py(x + u, y + v);
    const s = hw * (0.1 + hash(x, y, 30 + k) * 0.07);
    c.fillStyle = "#58a63a";
    c.beginPath();
    c.moveTo(bx - s * 0.5, by);
    c.lineTo(bx - s * 0.9, by - s * 1.5);
    c.lineTo(bx - s * 0.1, by);
    c.moveTo(bx - s * 0.2, by);
    c.lineTo(bx + s * 0.1, by - s * 2);
    c.lineTo(bx + s * 0.4, by);
    c.moveTo(bx + s * 0.2, by);
    c.lineTo(bx + s * 0.95, by - s * 1.4);
    c.lineTo(bx + s * 0.6, by);
    c.fill();
  }
  if (hash(x, y, 3) > 0.93) {
    const bx = px(x + 0.5, y + 0.5) + hw * 0.2, by = py(x + 0.5, y + 0.5);
    ell(c, bx, by, hw * 0.07, hw * 0.045, hash(x, y, 4) > 0.5 ? "#fff6c9" : "#ffd9e6");
    ell(c, bx, by, hw * 0.025, hw * 0.017, "#f2b134");
  }
}

// ---- hedge walls --------------------------------------------------------------------

const HEDGE_TOP = "#4fb04a", HEDGE_L = "#2f8f3f", HEDGE_R = "#226f32";

/**
 * A closed side of a maze cell: a thick, low hedge wall along the north (N),
 * east (E), south (S) or west (W) edge of tile (x, y).
 */
export function drawWall(c: Ctx, side: "N" | "E" | "S" | "W", x: number, y: number): void {
  const t = 0.16;
  const H = Math.max(2, geo.hw * 0.52);
  if (side === "N" || side === "S") {
    const gy = side === "N" ? y + 1 : y;
    box(c, x - t / 2, gy - t / 2, x + 1 + t / 2, gy + t / 2, 0, H, HEDGE_TOP, HEDGE_L, HEDGE_R);
  } else {
    const gx = side === "E" ? x + 1 : x;
    box(c, gx - t / 2, y - t / 2, gx + t / 2, y + 1 + t / 2, 0, H, HEDGE_TOP, HEDGE_L, HEDGE_R);
  }
  if (geo.hw >= 10) {
    // a few leaf specks on top
    const cx = side === "N" || side === "S" ? x + 0.5 : side === "E" ? x + 1 : x;
    const cy = side === "N" ? y + 1 : side === "S" ? y : y + 0.5;
    c.fillStyle = "#74cc63";
    const lx = px(cx, cy), ly = py(cx, cy, H);
    c.fillRect(lx - geo.hw * 0.25, ly - 1, Math.max(1, geo.hw * 0.1), Math.max(1, geo.hw * 0.05));
    c.fillRect(lx + geo.hw * 0.12, ly, Math.max(1, geo.hw * 0.1), Math.max(1, geo.hw * 0.05));
  }
}
