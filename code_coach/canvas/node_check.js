// Play one Canvas step's check in node, against a stand-in canvas.
//
// Reads {"harness", "code", "check"} as JSON on stdin and prints one line
// of JSON: {"passed", "message"}. The learner's code and the check run as
// separate scripts in one context - the same as two <script> tags - so a
// top-level `let player` is visible to the check by name.
"use strict";
const vm = require("vm");

function stage() {
  const listeners = {};
  const on = (type, fn) => (listeners[type] = listeners[type] || []).push(fn);
  const off = (type, fn) => {
    listeners[type] = (listeners[type] || []).filter((f) => f !== fn);
  };
  const fire = (ev) => {
    for (const fn of (listeners[ev.type] || []).slice()) fn(ev);
    return true;
  };

  class MouseEvent {
    constructor(type, init) {
      this.type = type;
      Object.assign(this, init || {});
    }
    preventDefault() {}
  }

  class KeyboardEvent {
    constructor(type, init) {
      this.type = type;
      Object.assign(this, init || {});
      this.defaultPrevented = false;
    }
    preventDefault() {
      this.defaultPrevented = true;
    }
  }

  // A 2d context with the state a game sets and the calls it makes, doing
  // nothing: the harness writes each call down, and that is what is checked.
  const ctx = {
    fillStyle: "#000000",
    strokeStyle: "#000000",
    lineWidth: 1,
    font: "10px sans-serif",
    textAlign: "start",
    textBaseline: "alphabetic",
    globalAlpha: 1,
    measureText: (text) => ({ width: String(text).length * 6 }),
  };
  for (const name of [
    "fillRect", "clearRect", "strokeRect", "rect", "beginPath", "closePath",
    "moveTo", "lineTo", "arc", "ellipse", "fill", "stroke", "fillText",
    "strokeText", "save", "restore", "translate", "rotate", "scale",
    "setTransform", "resetTransform", "drawImage", "roundRect",
  ]) {
    ctx[name] = () => {};
  }

  const canvas = {
    width: 480,
    height: 320,
    getContext: (kind) => (kind === "2d" ? ctx : null),
    addEventListener: on,
    removeEventListener: off,
    dispatchEvent: fire,
    focus() {},
    // Drawn at twice its size and away from the corner of the page, as a
    // canvas in a real layout usually is: page pixels are not canvas pixels.
    getBoundingClientRect: () => ({ left: 100, top: 40, width: 960, height: 640, right: 1060, bottom: 680, x: 100, y: 40 }),
  };
  const document = {
    querySelector: (sel) => (String(sel).includes("canvas") ? canvas : null),
    getElementById: () => canvas,
    addEventListener: on,
    removeEventListener: off,
    dispatchEvent: fire,
    body: {},
  };

  const sandbox = {
    console,
    document,
    KeyboardEvent,
    MouseEvent,
    performance: { now: () => 0 },
    addEventListener: on,
    removeEventListener: off,
    dispatchEvent: fire,
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    Math,
  };
  sandbox.window = sandbox;
  sandbox.self = sandbox;
  sandbox.parent = sandbox;
  return vm.createContext(sandbox);
}

async function main() {
  let input = "";
  for await (const chunk of process.stdin) input += chunk;
  const { harness, code, check } = JSON.parse(input);
  const context = stage();
  const say = (result) => process.stdout.write(JSON.stringify(result) + "\n");

  vm.runInContext(harness, context, { filename: "harness.js" });
  vm.runInContext("__cc.boot('check', 1)", context);
  try {
    vm.runInContext(code, context, { filename: "game.js", timeout: 3000 });
  } catch (e) {
    const where = /game\.js:(\d+)/.exec(String(e && e.stack));
    say({
      passed: false,
      message: "Your code threw" + (where ? " on line " + where[1] : "") + ": " + (e && e.message ? e.message : String(e)),
    });
    return;
  }
  context.__ccBody = check;
  const result = await vm.runInContext("__cc.check(__ccBody)", context, { timeout: 5000 });
  say(result);
}

main().catch((e) => {
  process.stdout.write(JSON.stringify({ passed: false, message: "The check could not run: " + (e && e.message ? e.message : String(e)) }) + "\n");
});
