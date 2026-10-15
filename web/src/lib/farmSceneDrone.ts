/**
 * The drone: a small flat-grey hovering machine with two blurred rotors, a
 * soft shadow that shrinks as it bobs up, and a hat on top. Plus the speech
 * puffs it prints into.
 */

import { TAU, ell, geo, quad, roundRect, tri } from "./farmSceneArt";

type Ctx = CanvasRenderingContext2D;

/** How high the drone hovers above its tile, in pixels. `act` (0 to 1) is the action dip. */
export function droneLift(time: number, id: number, act: number): number {
  const u = Math.max(geo.hw, 9);
  return u * (0.62 + 0.07 * Math.sin(time * 2.3 + id * 1.7)) - u * 0.34 * act;
}

export function drawDroneShadow(c: Ctx, cx: number, cy: number, time: number, id: number, act: number): void {
  const u = Math.max(geo.hw, 9);
  const lift = droneLift(time, id, act);
  const r = u * 0.4 * (1 - lift / (u * 3));
  c.globalAlpha = 0.34;
  c.fillStyle = "#1b2b16";
  c.beginPath();
  c.ellipse(cx, cy + u * 0.03, Math.max(0.5, r), Math.max(0.25, r * 0.5), 0, 0, TAU);
  c.fill();
  c.globalAlpha = 1;
}

/**
 * cx, cy: the ground point under the drone (the tile's centre). `lean` is -1..1
 * (forward = right on screen), `act` the action pose 0..1.
 */
export function drawDrone(c: Ctx, cx: number, cy: number, time: number, id: number, hat: string, lean: number, act: number): void {
  const u = Math.max(geo.hw, 9);
  const by = cy - droneLift(time, id, act) - u * 0.15;
  const bx = cx;
  const lx = lean * u * 0.1;
  // arms and rotors
  const spin = time * 38 + id * 1.3;
  for (let side = -1; side <= 1; side += 2) {
    const rx = bx + side * u * 0.46;
    const ry = by - u * 0.08 + side * lean * u * 0.05;
    c.strokeStyle = "#6e7782";
    c.lineWidth = Math.max(1, u * 0.06);
    c.beginPath();
    c.moveTo(bx + side * u * 0.2, by);
    c.lineTo(rx, ry);
    c.stroke();
    // the spinning disc: a faint ellipse plus a few blades at different angles
    const blur = 0.2 + 0.25 * act;
    c.globalAlpha = blur;
    ell(c, rx, ry - u * 0.05, u * 0.27, u * 0.09, "#4b5560");
    c.globalAlpha = 0.28 + 0.4 * act;
    c.strokeStyle = "#39424c";
    c.lineWidth = Math.max(1, u * 0.045);
    c.beginPath();
    for (let k = 0; k < 3; k++) {
      const a = spin * (side > 0 ? 1 : -1) + k * (TAU / 3);
      const ex = Math.cos(a) * u * 0.27, ey = Math.sin(a) * u * 0.09;
      c.moveTo(rx - ex, ry - u * 0.05 - ey);
      c.lineTo(rx + ex, ry - u * 0.05 + ey);
    }
    c.stroke();
    c.globalAlpha = 1;
    ell(c, rx, ry, u * 0.05, u * 0.05, "#39424c");
  }
  // hull: darker belly, light flat dome
  ell(c, bx, by + u * 0.07, u * 0.34, u * 0.13, "#7d8793");
  ell(c, bx, by, u * 0.34, u * 0.14, "#aab3bd");
  c.fillStyle = "#d3dae1";
  c.beginPath();
  c.ellipse(bx + lx * 0.5, by - u * 0.02, u * 0.27, u * 0.16, 0, Math.PI, TAU);
  c.closePath();
  c.fill();
  ell(c, bx - u * 0.1 + lx * 0.5, by - u * 0.1, u * 0.1, u * 0.04, "rgba(255,255,255,0.5)");
  // a small camera eye on the front
  ell(c, bx + u * 0.12, by + u * 0.02, u * 0.06, u * 0.045, "#2a3440");
  ell(c, bx + u * 0.13, by + u * 0.015, u * 0.025, u * 0.02, "#6fd8ff");
  drawHat(c, hat, bx + lx, by - u * 0.12, u, lean);
}

type HatLook = { brim: string; brimEdge: string; crown: string; band: string; wide: number; tall: number; flat: boolean };
const HATS: Record<string, HatLook> = {
  Straw_Hat: { brim: "#e3c262", brimEdge: "#bf9c3c", crown: "#f2d98a", band: "#b5651d", wide: 0.46, tall: 0.26, flat: false },
  Brown_Hat: { brim: "#7d4f27", brimEdge: "#5d3a1c", crown: "#9a6532", band: "#4d3018", wide: 0.4, tall: 0.3, flat: false },
  Gray_Hat: { brim: "#9aa2ab", brimEdge: "#7a838c", crown: "#bcc3ca", band: "#5b636b", wide: 0.38, tall: 0.28, flat: true },
  Green_Hat: { brim: "#3fa04f", brimEdge: "#2d7c3b", crown: "#5fc572", band: "#e8c66a", wide: 0.4, tall: 0.3, flat: false },
  Purple_Hat: { brim: "#7c4cc4", brimEdge: "#5d36a0", crown: "#9d72e0", band: "#f2d98a", wide: 0.36, tall: 0.36, flat: true },
};

function drawHat(c: Ctx, name: string, hx: number, hy: number, u: number, lean: number): void {
  const look = HATS[name];
  const tip = lean * u * 0.06;
  if (look) {
    ell(c, hx, hy, u * look.wide, u * look.wide * 0.32, look.brimEdge);
    ell(c, hx, hy - u * 0.015, u * look.wide, u * look.wide * 0.3, look.brim);
    const cw = u * (look.flat ? 0.22 : 0.26), ch = u * look.tall;
    c.fillStyle = look.crown;
    c.beginPath();
    if (look.flat) {
      c.moveTo(hx - cw, hy - u * 0.02);
      c.lineTo(hx - cw * 0.92 + tip, hy - ch);
      c.lineTo(hx + cw * 0.92 + tip, hy - ch);
      c.lineTo(hx + cw, hy - u * 0.02);
      c.closePath();
      c.fill();
      ell(c, hx + tip, hy - ch, cw * 0.92, cw * 0.3, look.crown);
      ell(c, hx + tip, hy - ch, cw * 0.92, cw * 0.3, "rgba(255,255,255,0.18)");
    } else {
      c.moveTo(hx - cw, hy - u * 0.02);
      c.ellipse(hx + tip * 0.5, hy - u * 0.02, cw, ch, 0, Math.PI, TAU);
      c.closePath();
      c.fill();
    }
    c.fillStyle = look.band;
    c.fillRect(hx - cw * 0.98, hy - u * 0.085, cw * 1.96, u * 0.06);
    return;
  }
  if (name === "Traffic_Cone") {
    ell(c, hx, hy - u * 0.01, u * 0.2, u * 0.065, "#d9560f");
    tri(c, "#ff7a1a", hx - u * 0.16, hy - u * 0.02, hx + u * 0.16, hy - u * 0.02, hx + tip, hy - u * 0.5);
    quad(c, "#ffffff", hx - u * 0.1, hy - u * 0.18, hx + u * 0.1, hy - u * 0.18, hx + u * 0.065 + tip * 0.4, hy - u * 0.3, hx - u * 0.065 + tip * 0.4, hy - u * 0.3);
    tri(c, "#e8680f", hx + u * 0.02, hy - u * 0.02, hx + u * 0.16, hy - u * 0.02, hx + tip, hy - u * 0.5);
    return;
  }
  if (name === "Wizard_Hat") {
    ell(c, hx, hy, u * 0.4, u * 0.13, "#3a2f94");
    ell(c, hx, hy - u * 0.015, u * 0.4, u * 0.12, "#5a4ad0");
    c.fillStyle = "#4b3fb8";
    c.beginPath();
    c.moveTo(hx - u * 0.22, hy - u * 0.02);
    c.quadraticCurveTo(hx - u * 0.1 + tip, hy - u * 0.5, hx + u * 0.18 + tip * 1.5, hy - u * 0.7);
    c.quadraticCurveTo(hx + u * 0.12 + tip, hy - u * 0.4, hx + u * 0.22, hy - u * 0.02);
    c.closePath();
    c.fill();
    c.fillStyle = "#3a2f94";
    c.beginPath();
    c.moveTo(hx + u * 0.03, hy - u * 0.02);
    c.quadraticCurveTo(hx + u * 0.08 + tip, hy - u * 0.4, hx + u * 0.18 + tip * 1.5, hy - u * 0.7);
    c.quadraticCurveTo(hx + u * 0.12 + tip, hy - u * 0.4, hx + u * 0.22, hy - u * 0.02);
    c.closePath();
    c.fill();
    ell(c, hx - u * 0.02, hy - u * 0.2, u * 0.035, u * 0.035, "#ffd23a");
    ell(c, hx + u * 0.08 + tip * 0.5, hy - u * 0.38, u * 0.03, u * 0.03, "#ffd23a");
    return;
  }
  if (name === "Dinosaur_Hat") {
    // a green dino head with a snout, an eye and back spikes
    tri(c, "#2f8a3f", hx - u * 0.2, hy - u * 0.2, hx - u * 0.12, hy - u * 0.4, hx - u * 0.04, hy - u * 0.24);
    tri(c, "#2f8a3f", hx - u * 0.06, hy - u * 0.26, hx + u * 0.02, hy - u * 0.46, hx + u * 0.1, hy - u * 0.28);
    ell(c, hx, hy - u * 0.12, u * 0.27, u * 0.17, "#4aaa50");
    ell(c, hx + u * 0.2, hy - u * 0.07, u * 0.17, u * 0.1, "#5fc468");
    ell(c, hx - u * 0.04, hy - u * 0.15, u * 0.2, u * 0.11, "#6bd073");
    ell(c, hx + u * 0.04, hy - u * 0.19, u * 0.055, u * 0.06, "#ffffff");
    ell(c, hx + u * 0.055, hy - u * 0.19, u * 0.026, u * 0.03, "#1b2b16");
    ell(c, hx + u * 0.3, hy - u * 0.1, u * 0.02, u * 0.015, "#2f7a38");
    return;
  }
  // an unknown hat: a plain cap
  ell(c, hx, hy, u * 0.3, u * 0.1, "#8a6b3a");
  ell(c, hx, hy - u * 0.1, u * 0.2, u * 0.12, "#a98550");
}

/** One bubble of text above (ax, top): speech/smoke puffs the drone has printed. */
export function drawSmoke(c: Ctx, texts: string[], ax: number, ay: number, W: number, H: number): void {
  const n = Math.min(3, texts.length);
  if (n === 0) return;
  c.font = "12px ui-monospace, monospace";
  c.textBaseline = "middle";
  c.textAlign = "left";
  let y = ay - 8;
  for (let k = 0; k < n; k++) {
    let text = texts[texts.length - 1 - k];
    if (text.length > 34) text = text.slice(0, 33) + "…";
    const w = c.measureText(text).width + 14;
    const bh = 20;
    const bx = Math.max(4, Math.min(W - w - 4, ax - w / 2));
    const by = Math.max(4, Math.min(H - bh - 4, y - bh));
    c.globalAlpha = k === 0 ? 0.96 : k === 1 ? 0.8 : 0.6;
    c.fillStyle = "#fbfdff";
    roundRect(c, bx, by, w, bh, 8);
    c.fill();
    c.strokeStyle = "#8aa0b3";
    c.lineWidth = 1;
    c.stroke();
    if (k === 0) {
      // little puffs trailing down to the drone
      ell(c, Math.max(4, Math.min(W - 4, ax)), by + bh + 3, 3, 2.4, "#fbfdff");
      ell(c, Math.max(4, Math.min(W - 4, ax)), by + bh + 8, 1.8, 1.4, "#fbfdff");
    }
    c.fillStyle = "#1b2430";
    c.fillText(text, bx + 7, by + bh / 2 + 0.5);
    y = by - 4;
  }
  c.globalAlpha = 1;
  c.textBaseline = "alphabetic";
}
