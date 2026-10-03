/**
 * Drawing the farm on a canvas from the server's snapshot.
 *
 * North is up: the game's y grows northwards, so row y is drawn
 * (h - 1 - y) squares from the top. Everything is plain shapes - soil,
 * grass blades, a bush, a pumpkin - sized by how grown the plant is, so a
 * field you have just planted visibly fills in as it ripens.
 */

import type { FarmCell, FarmSnapshot } from "../types";

const GROUND = { G: "#3f6b2c", S: "#5e4029" };

const HAT_COLOURS: Record<string, string> = {
  Straw_Hat: "#e8c66a",
  Brown_Hat: "#7a4b2a",
  Gray_Hat: "#9aa3ad",
  Green_Hat: "#4caf50",
  Purple_Hat: "#9c6ade",
  Traffic_Cone: "#ff7a1a",
  Wizard_Hat: "#4b3fb8",
  Dinosaur_Hat: "#5fb85f",
};

export function drawFarm(ctx: CanvasRenderingContext2D, snap: FarmSnapshot, px: number): void {
  const { w, h } = snap;
  // Squares never grow past this, so a farm of one square looks like one
  // square of a farm rather than a close-up of the drone.
  const cell = Math.min(110, Math.floor(px / Math.max(w, h)));
  const left = Math.floor((px - cell * w) / 2);
  const top = Math.floor((px - cell * h) / 2);
  const sx = (x: number) => left + x * cell;
  const sy = (y: number) => top + (h - 1 - y) * cell;

  ctx.clearRect(0, 0, px, px);
  ctx.fillStyle = "#151a14";
  ctx.fillRect(0, 0, px, px);

  // Ground, water and infection first, then what grows on it.
  snap.tiles.forEach((t, i) => {
    const x = i % w;
    const y = Math.floor(i / w);
    ctx.fillStyle = GROUND[t.g] ?? GROUND.G;
    ctx.fillRect(sx(x) + 1, sy(y) + 1, cell - 2, cell - 2);
    if (t.w) {
      ctx.fillStyle = `rgba(70, 140, 255, ${Math.min(0.55, t.w * 0.55)})`;
      ctx.fillRect(sx(x) + 1, sy(y) + 1, cell - 2, cell - 2);
    }
  });

  const drawnGiants = new Set<string>();
  snap.tiles.forEach((t, i) => {
    const x = i % w;
    const y = Math.floor(i / w);
    if (t.giant) {
      const [gx, gy, n] = t.giant;
      const key = `${gx},${gy}`;
      if (drawnGiants.has(key)) return;
      drawnGiants.add(key);
      // One pumpkin across the whole square, drawn from its North-West corner.
      const cx = sx(gx) + (n * cell) / 2;
      const cy = sy(gy + n - 1) + (n * cell) / 2;
      pumpkin(ctx, cx, cy, n * cell * 0.46, t.i ? "#b06bd6" : "#f08a24");
      return;
    }
    drawEntity(ctx, t, sx(x), sy(y), cell);
  });

  // Maze walls: a hedge wherever a side of a cell is closed.
  if (snap.maze) {
    const m = snap.maze;
    ctx.strokeStyle = "#163d16";
    ctx.lineWidth = Math.max(2, cell * 0.12);
    ctx.lineCap = "square";
    for (let dy = 0; dy < m.m; dy++) {
      for (let dx = 0; dx < m.m; dx++) {
        const bits = m.sides[dy * m.m + dx];
        const x0 = sx(m.x0 + dx);
        const y0 = sy(m.y0 + dy);
        ctx.beginPath();
        if (!(bits & 1)) { ctx.moveTo(x0, y0); ctx.lineTo(x0 + cell, y0); }
        if (!(bits & 2)) { ctx.moveTo(x0 + cell, y0); ctx.lineTo(x0 + cell, y0 + cell); }
        if (!(bits & 4)) { ctx.moveTo(x0, y0 + cell); ctx.lineTo(x0 + cell, y0 + cell); }
        if (!(bits & 8)) { ctx.moveTo(x0, y0); ctx.lineTo(x0, y0 + cell); }
        ctx.stroke();
      }
    }
  }

  // The drone, with its hat and anything it has just printed.
  const { x, y, hat } = snap.drone;
  const cx = sx(x) + cell / 2;
  const cy = sy(y) + cell / 2;
  const r = cell * 0.3;
  ctx.fillStyle = "rgba(0,0,0,0.35)";
  ctx.beginPath();
  ctx.ellipse(cx, cy + r * 0.9, r * 0.9, r * 0.3, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#c9d1d9";
  ctx.fillRect(cx - r * 0.55, cy - r * 0.35, r * 1.1, r * 0.7);
  ctx.fillStyle = "#8b949e";
  for (const [ox, oy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
    ctx.beginPath();
    ctx.arc(cx + ox * r * 0.75, cy + oy * r * 0.55, r * 0.28, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.fillStyle = HAT_COLOURS[hat] ?? HAT_COLOURS.Straw_Hat;
  ctx.fillRect(cx - r * 0.4, cy - r * 0.75, r * 0.8, r * 0.4);
  ctx.fillRect(cx - r * 0.6, cy - r * 0.4, r * 1.2, r * 0.12);

  if (snap.smoke.length) {
    const text = snap.smoke[snap.smoke.length - 1];
    ctx.font = `${Math.max(11, Math.round(cell * 0.28))}px ui-monospace, monospace`;
    const width = ctx.measureText(text).width + 10;
    const bx = Math.min(Math.max(4, cx - width / 2), px - width - 4);
    const by = Math.max(4, cy - r * 1.6 - 18);
    ctx.fillStyle = "rgba(230,235,240,0.92)";
    ctx.fillRect(bx, by, width, 18);
    ctx.fillStyle = "#1b1f24";
    ctx.fillText(text, bx + 5, by + 13);
  }
}

function drawEntity(ctx: CanvasRenderingContext2D, t: FarmCell, x0: number, y0: number, cell: number): void {
  if (!t.e) return;
  const p = t.p ?? 1;
  const cx = x0 + cell / 2;
  const cy = y0 + cell / 2;
  const grown = 0.35 + 0.65 * p;
  const sick = !!t.i;
  switch (t.e) {
    case "Grass": {
      ctx.strokeStyle = p >= 1 ? "#9be15d" : "#6fb23d";
      ctx.lineWidth = Math.max(1, cell * 0.04);
      const tall = cell * 0.32 * grown;
      for (const dx of [-0.18, 0, 0.18]) {
        ctx.beginPath();
        ctx.moveTo(cx + dx * cell, cy + cell * 0.22);
        ctx.lineTo(cx + dx * cell * 1.4, cy + cell * 0.22 - tall);
        ctx.stroke();
      }
      break;
    }
    case "Bush":
      blob(ctx, cx, cy, cell * 0.3 * grown, sick ? "#8a5fb0" : p >= 1 ? "#2f9e44" : "#3c7f3a");
      break;
    case "Tree":
      ctx.fillStyle = "#6b4423";
      ctx.fillRect(cx - cell * 0.05, cy, cell * 0.1, cell * 0.32);
      blob(ctx, cx, cy - cell * 0.08, cell * 0.36 * grown, sick ? "#8a5fb0" : p >= 1 ? "#1f8a3c" : "#2f6e33");
      break;
    case "Carrot": {
      const s = cell * 0.3 * grown;
      ctx.fillStyle = sick ? "#b06bd6" : "#f28c28";
      ctx.beginPath();
      ctx.moveTo(cx - s * 0.5, cy - s * 0.3);
      ctx.lineTo(cx + s * 0.5, cy - s * 0.3);
      ctx.lineTo(cx, cy + s);
      ctx.fill();
      ctx.fillStyle = "#3fa34d";
      ctx.fillRect(cx - s * 0.25, cy - s * 0.8, s * 0.5, s * 0.5);
      break;
    }
    case "Pumpkin":
      pumpkin(ctx, cx, cy, cell * 0.34 * grown, sick ? "#b06bd6" : p >= 1 ? "#f08a24" : "#c9a13a");
      break;
    case "Dead_Pumpkin":
      pumpkin(ctx, cx, cy, cell * 0.26, "#6e6a60");
      break;
    case "Sunflower": {
      const petals = t.n ?? 8;
      const r = cell * 0.3 * grown;
      ctx.fillStyle = sick ? "#b06bd6" : "#f5d33b";
      for (let k = 0; k < petals; k++) {
        const a = (k / petals) * Math.PI * 2;
        ctx.beginPath();
        ctx.ellipse(cx + Math.cos(a) * r * 0.7, cy + Math.sin(a) * r * 0.7, r * 0.32, r * 0.14, a, 0, Math.PI * 2);
        ctx.fill();
      }
      blob(ctx, cx, cy, r * 0.38, "#6b4423");
      break;
    }
    case "Cactus": {
      const size = t.n ?? 0;
      const tall = cell * (0.25 + 0.05 * size) * grown;
      ctx.fillStyle = sick ? "#b06bd6" : p < 1 ? "#5f9c5a" : t.s === 0 ? "#9a6b3c" : "#3fae5a";
      ctx.fillRect(cx - cell * 0.1, cy + cell * 0.3 - tall, cell * 0.2, tall);
      ctx.fillStyle = "#0d1117";
      ctx.font = `${Math.max(9, Math.round(cell * 0.24))}px ui-monospace, monospace`;
      ctx.fillText(String(size), x0 + cell * 0.08, y0 + cell * 0.28);
      break;
    }
    case "Hedge":
      ctx.fillStyle = "#27552a";
      ctx.fillRect(x0 + 1, y0 + 1, cell - 2, cell - 2);
      break;
    case "Treasure":
      ctx.fillStyle = "#27552a";
      ctx.fillRect(x0 + 1, y0 + 1, cell - 2, cell - 2);
      ctx.fillStyle = "#f2c94c";
      ctx.fillRect(cx - cell * 0.22, cy - cell * 0.15, cell * 0.44, cell * 0.3);
      ctx.fillStyle = "#a0782c";
      ctx.fillRect(cx - cell * 0.22, cy - cell * 0.02, cell * 0.44, cell * 0.05);
      break;
    case "Apple":
      blob(ctx, cx, cy, cell * 0.22, "#e5484d");
      ctx.fillStyle = "#3fa34d";
      ctx.fillRect(cx, cy - cell * 0.3, cell * 0.06, cell * 0.1);
      break;
    case "Dinosaur":
      ctx.fillStyle = "#5fb85f";
      ctx.fillRect(x0 + cell * 0.15, y0 + cell * 0.15, cell * 0.7, cell * 0.7);
      ctx.fillStyle = "#3d8a3d";
      ctx.fillRect(x0 + cell * 0.3, y0 + cell * 0.3, cell * 0.4, cell * 0.4);
      break;
    default:
      break;
  }
}

function blob(ctx: CanvasRenderingContext2D, x: number, y: number, r: number, colour: string): void {
  ctx.fillStyle = colour;
  ctx.beginPath();
  ctx.arc(x, y, Math.max(1, r), 0, Math.PI * 2);
  ctx.fill();
}

function pumpkin(ctx: CanvasRenderingContext2D, x: number, y: number, r: number, colour: string): void {
  ctx.fillStyle = colour;
  ctx.beginPath();
  ctx.ellipse(x, y, Math.max(1, r), Math.max(1, r * 0.82), 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(0,0,0,0.18)";
  ctx.lineWidth = Math.max(1, r * 0.06);
  for (const k of [-0.45, 0, 0.45]) {
    ctx.beginPath();
    ctx.ellipse(x + k * r, y, r * 0.3, r * 0.8, 0, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.fillStyle = "#3fa34d";
  ctx.fillRect(x - r * 0.08, y - r * 1.05, r * 0.16, r * 0.3);
}
