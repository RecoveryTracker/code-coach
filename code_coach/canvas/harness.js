// The Canvas harness. Loaded before the learner's code, in two places:
//
//   - the browser preview, where it drives requestAnimationFrame from the
//     real one and passes errors and console.log up to the page, and
//   - node (node_check.js), against a stand-in canvas, where a step's check
//     plays the game by hand: so many frames, this key held, then looks.
//
// It is one file so the game the check plays is the game you watched.
// Everything it adds to the page lives on `__cc`; the learner's own names
// (canvas, ctx, player...) are left alone.
(function () {
  "use strict";
  const W = globalThis;
  const realRaf = W.requestAnimationFrame ? W.requestAnimationFrame.bind(W) : null;

  let clock = 0; // milliseconds of game time
  let manual = true; // true until boot('play') hands the frames to the browser
  let queue = []; // requestAnimationFrame callbacks waiting for the next frame
  let timers = []; // setTimeout / setInterval, run on game time while manual
  let nextId = 1;
  let calls = []; // what was drawn since the current frame began
  let codeStart = 1; // the document line the learner's code starts on

  // ── Time ──────────────────────────────────────────────────────────
  // Game time, not wall time, so a check of "120 pixels a second" means
  // the same thing on a slow machine and a fast one.
  W.requestAnimationFrame = function (cb) {
    const id = nextId++;
    queue.push({ id, cb });
    return id;
  };
  W.cancelAnimationFrame = function (id) {
    queue = queue.filter((q) => q.id !== id);
  };
  try {
    W.performance.now = () => clock;
  } catch (e) {
    /* a frozen performance object: the timestamp argument still works */
  }

  const realSetTimeout = W.setTimeout;
  const realClearTimeout = W.clearTimeout;
  function addTimer(fn, ms, repeat) {
    const id = nextId++;
    timers.push({ id, fn, at: clock + Math.max(0, Number(ms) || 0), every: repeat ? Math.max(1, Number(ms) || 0) : 0 });
    return id;
  }
  function removeTimer(id) {
    timers = timers.filter((t) => t.id !== id);
  }

  function step(dt) {
    clock += dt;
    // Timers due by now, in the order they come due.
    for (;;) {
      timers.sort((a, b) => a.at - b.at);
      const t = timers[0];
      if (!t || t.at > clock) break;
      if (t.every) t.at += t.every;
      else timers.shift();
      t.fn();
    }
    const run = queue;
    queue = [];
    calls = [];
    for (const q of run) q.cb(clock);
  }

  // ── Drawing ───────────────────────────────────────────────────────
  // The context is wrapped so every call is written down with the colour
  // it was made in. getContext hands back the wrapped one.
  function record(ctx) {
    return new Proxy(ctx, {
      get(target, name) {
        const value = target[name];
        if (typeof value !== "function") return value;
        return function (...args) {
          calls.push({
            name: String(name),
            args,
            fill: String(target.fillStyle),
            stroke: String(target.strokeStyle),
          });
          return value.apply(target, args);
        };
      },
      set(target, name, value) {
        target[name] = value;
        return true;
      },
    });
  }

  function wrapCanvas(el) {
    if (!el || el.__ccWrapped) return;
    const own = el.getContext.bind(el);
    let wrapped = null;
    el.getContext = function (kind, ...rest) {
      if (kind !== "2d") return own(kind, ...rest);
      if (!wrapped) wrapped = record(own("2d", ...rest));
      return wrapped;
    };
    el.__ccWrapped = true;
  }

  // ── Keys ──────────────────────────────────────────────────────────
  const CODES = { " ": "Space", Enter: "Enter", Escape: "Escape", Shift: "ShiftLeft" };
  function codeFor(key) {
    if (CODES[key]) return CODES[key];
    if (/^[a-z]$/i.test(key)) return "Key" + key.toUpperCase();
    if (/^[0-9]$/.test(key)) return "Digit" + key;
    return key; // ArrowLeft and friends are their own code
  }
  function send(type, key) {
    const ev = new W.KeyboardEvent(type, { key, code: codeFor(key), bubbles: true });
    W.document.dispatchEvent(ev);
  }

  // ── Reporting to the page ─────────────────────────────────────────
  function post(message) {
    try {
      if (W.parent && W.parent !== W) W.parent.postMessage({ cc: true, ...message }, "*");
    } catch (e) {
      /* nowhere to report to - node, or a detached frame */
    }
  }
  function lineOf(lineno) {
    const n = Number(lineno) - codeStart + 1;
    return n > 0 ? n : 0;
  }
  if (W.addEventListener && W.parent && W.parent !== W) {
    W.addEventListener("error", (e) => {
      post({ type: "error", message: String(e.message || e), line: lineOf(e.lineno) });
    });
    for (const level of ["log", "warn", "error"]) {
      const own = W.console[level].bind(W.console);
      W.console[level] = (...args) => {
        own(...args);
        post({ type: "log", level, text: args.map(show).join(" ") });
      };
    }
  }
  function show(v) {
    if (typeof v === "string") return v;
    try {
      return JSON.stringify(v);
    } catch (e) {
      return String(v);
    }
  }

  // A small seeded random, so a check that spawns enemies spawns the same
  // ones every time and a pass is not luck.
  function mulberry32(seed) {
    return function () {
      seed |= 0;
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // ── What a check can use ──────────────────────────────────────────
  const cc = {
    get time() {
      return clock;
    },
    /** Run n frames of dt milliseconds each (60 a second by default). */
    frames(n, dt = 1000 / 60) {
      for (let i = 0; i < n; i++) step(dt);
    },
    press(key) {
      send("keydown", key);
    },
    release(key) {
      send("keyup", key);
    },
    /** Every drawing call made since the current frame began. */
    drawn() {
      return calls.slice();
    },
    /** The filled rectangles of the current frame. */
    rects() {
      return calls
        .filter((c) => c.name === "fillRect")
        .map((c) => ({ x: c.args[0], y: c.args[1], w: c.args[2], h: c.args[3], fill: c.fill }));
    },
    /** The circles drawn this frame: arc(x, y, r, ...) calls. */
    arcs() {
      return calls
        .filter((c) => c.name === "arc")
        .map((c) => ({ x: c.args[0], y: c.args[1], r: c.args[2], fill: c.fill }));
    },
    /**
     * Move the mouse to (x, y) in canvas pixels. The event carries page
     * pixels, as a real one does - and in node the canvas is drawn at twice
     * its size, so code that forgets to scale is caught here, not later.
     */
    pointer(x, y = 0) {
      const el = W.document.querySelector("canvas");
      const box = el.getBoundingClientRect();
      const sx = box.width / el.width;
      const sy = box.height / el.height;
      const init = {
        clientX: box.left + x * sx,
        clientY: box.top + y * sy,
        offsetX: x * sx,
        offsetY: y * sy,
        bubbles: true,
      };
      for (const type of ["pointermove", "mousemove"]) el.dispatchEvent(new W.MouseEvent(type, init));
    },
    /** The text written this frame. */
    texts() {
      return calls.filter((c) => c.name === "fillText" || c.name === "strokeText").map((c) => String(c.args[0]));
    },
  };

  function fail(message) {
    const e = new Error(message);
    e.ccMessage = true;
    return e;
  }
  function expect(ok, message) {
    if (!ok) throw fail(message);
  }
  function near(a, b, within) {
    return typeof a === "number" && Math.abs(a - b) <= within;
  }

  W.__cc = {
    api: cc,
    /** 'play' hands the frames to the browser; 'check' keeps them manual. */
    boot(mode, startLine) {
      codeStart = startLine || 1;
      wrapCanvas(W.document && W.document.querySelector && W.document.querySelector("canvas"));
      if (mode === "check") {
        Math.random = mulberry32(20260926);
        W.setTimeout = (fn, ms) => addTimer(fn, ms, false);
        W.setInterval = (fn, ms) => addTimer(fn, ms, true);
        W.clearTimeout = removeTimer;
        W.clearInterval = removeTimer;
        return;
      }
      manual = false;
      let before = null;
      const tick = (now) => {
        // Capped, so coming back to a hidden tab is not one giant leap.
        const dt = before === null ? 1000 / 60 : Math.min(100, now - before);
        before = now;
        if (!manual) step(dt);
        realRaf(tick);
      };
      if (realRaf) realRaf(tick);
      else realSetTimeout(() => tick(0), 16);
      void realClearTimeout;
    },
    /** Run one step's check. Resolves to { passed, message }. */
    async check(body) {
      try {
        const run = new Function("cc", "expect", "near", '"use strict"; return (async () => {\n' + body + "\n})();");
        await run(cc, expect, near);
        return { passed: true, message: "" };
      } catch (e) {
        if (e && e.ccMessage) return { passed: false, message: e.message };
        return { passed: false, message: "Your code threw: " + (e && e.message ? e.message : String(e)) };
      }
    },
  };
})();
