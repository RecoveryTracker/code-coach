// The DOM harness. Loaded in the <head> of every page the To-do track
// makes, in two kinds of page:
//
//   - the preview, where you click around: it passes console.log and
//     errors up to Code Coach, and keeps localStorage between Runs, and
//   - the hidden page a check plays: it clicks, types and reloads the way
//     a person would, and reports whether the page did what the step asks.
//
// Both are a real browser's DOM - a sandboxed frame inside Code Coach, or
// headless Chrome in the tests - never a stand-in. The sandbox has no
// localStorage of its own (it has no origin to keep one for), so this file
// supplies one that lives as long as the page does. Everything it adds to
// the page lives on `__ccDom`; the learner's own names are left alone.
(function () {
  "use strict";
  const W = window;
  const D = document;
  const realAdd = EventTarget.prototype.addEventListener;
  const realRemove = EventTarget.prototype.removeEventListener;

  let data = { mode: "play", code: "", check: "", storage: {}, html: "", id: "" };
  let offset = 0; // lines added in front of your code by the harness (1 after a reload)
  const errors = []; // { message, line } for everything your code threw
  const logs = []; // console output, as the console shows it
  let reloadAsked = false; // a form was submitted and nothing stopped it

  // ── Reporting to Code Coach ───────────────────────────────────────
  function post(message) {
    try {
      if (W.parent && W.parent !== W) W.parent.postMessage({ cc: true, id: data.id, ...message }, "*");
    } catch (e) {
      /* nowhere to report to */
    }
  }

  function show(v) {
    if (typeof v === "string") return v;
    if (v instanceof Element) {
      const tag = v.outerHTML;
      return tag.length > 160 ? tag.slice(0, 157) + "..." : tag;
    }
    if (v instanceof NodeList || v instanceof HTMLCollection) {
      return v.constructor.name + "(" + v.length + ")";
    }
    try {
      const text = JSON.stringify(v);
      return text === undefined ? String(v) : text;
    } catch (e) {
      return String(v);
    }
  }

  for (const level of ["log", "info", "warn", "error"]) {
    const own = W.console[level].bind(W.console);
    W.console[level] = (...args) => {
      own(...args);
      const text = args.map(show).join(" ");
      logs.push(text);
      if (data.mode === "play") post({ type: "log", level: level === "info" ? "log" : level, text });
    };
  }

  // What the browser says, made plain: no "Uncaught", and not the name of
  // the call that ran your script.
  function plain(message) {
    return String(message || "error")
      .replace(/^Uncaught /, "")
      .replace(/Failed to execute 'appendChild' on 'Node': /, "");
  }

  // Which line of your code an error came from. Your code is a script put
  // in by hand, so its frames in a stack read "<anonymous>:line:column";
  // the stack is asked first because the error's own line can be somewhere
  // else entirely - JSON.parse reports the line of the JSON it choked on.
  // A check's frames are "eval at ..." and are passed over.
  function lineOf(error, lineno) {
    const stack = error && error.stack ? String(error.stack) : "";
    for (const row of stack.split("\n").slice(1)) {
      if (row.includes("eval at")) continue;
      const found = /<anonymous>:(\d+):\d+\)?\s*$/.exec(row);
      if (found) return Number(found[1]);
    }
    return Number(lineno || 0);
  }

  function noteError(message, error, lineno) {
    const line = Math.max(0, lineOf(error, lineno) - offset);
    const entry = { message: plain(message), line };
    errors.push(entry);
    if (data.mode === "play") post({ type: "error", message: entry.message, line });
  }

  realAdd.call(W, "error", (e) => noteError(e.message || (e.error && e.error.message), e.error, e.lineno));
  realAdd.call(W, "unhandledrejection", (e) => {
    const r = e.reason;
    noteError(r && r.message ? r.message : String(r), r, 0);
  });

  // A form submitted and not stopped would send the page off and load it
  // again, losing everything on it. In the preview that is what happens:
  // Code Coach loads the page again and says why. Last in line on the
  // window, so it sees what every listener of yours decided.
  realAdd.call(W, "submit", (e) => {
    if (data.mode !== "play" || e.defaultPrevented) return;
    e.preventDefault();
    post({ type: "reload", reason: "submit" });
  });

  // ── localStorage, kept in memory ──────────────────────────────────
  function makeStorage(initial, changed) {
    const items = new Map();
    for (const [k, v] of Object.entries(initial || {})) items.set(String(k), String(v));
    const api = {
      getItem(key) {
        key = String(key);
        return items.has(key) ? items.get(key) : null;
      },
      setItem(key, value) {
        items.set(String(key), String(value));
        changed(items);
      },
      removeItem(key) {
        items.delete(String(key));
        changed(items);
      },
      clear() {
        items.clear();
        changed(items);
      },
      key(index) {
        const keys = [...items.keys()];
        return index >= 0 && index < keys.length ? keys[index] : null;
      },
      get length() {
        return items.size;
      },
    };
    // localStorage.todos = '...' works on the real one, so it works here.
    return new Proxy(api, {
      get(target, name) {
        if (name in target) return target[name];
        if (typeof name === "string" && items.has(name)) return items.get(name);
        return undefined;
      },
      set(target, name, value) {
        if (name in target) return false;
        items.set(String(name), String(value));
        changed(items);
        return true;
      },
      deleteProperty(target, name) {
        items.delete(String(name));
        changed(items);
        return true;
      },
      has(target, name) {
        return name in target || items.has(String(name));
      },
      ownKeys() {
        return [...items.keys()];
      },
      getOwnPropertyDescriptor(target, name) {
        if (!items.has(String(name))) return undefined;
        return { value: items.get(String(name)), writable: true, enumerable: true, configurable: true };
      },
    });
  }

  function installStorage(initial) {
    const local = makeStorage(initial, (items) => {
      if (data.mode === "play") post({ type: "storage", items: Object.fromEntries(items) });
    });
    const session = makeStorage({}, () => {});
    Object.defineProperty(W, "localStorage", { configurable: true, enumerable: true, get: () => local });
    Object.defineProperty(W, "sessionStorage", { configurable: true, enumerable: true, get: () => session });
  }

  // ── What a reload has to undo ─────────────────────────────────────
  // Listeners on the window and the document outlive the page's elements,
  // and so do timers, so they are written down as they are made.
  const tracked = [];
  for (const target of [W, D]) {
    target.addEventListener = function (type, fn, options) {
      tracked.push([target, type, fn, options]);
      return realAdd.call(target, type, fn, options);
    };
  }
  const timers = [];
  const own = {
    setTimeout: W.setTimeout.bind(W),
    setInterval: W.setInterval.bind(W),
    clearTimeout: W.clearTimeout.bind(W),
    clearInterval: W.clearInterval.bind(W),
    requestAnimationFrame: W.requestAnimationFrame.bind(W),
    cancelAnimationFrame: W.cancelAnimationFrame.bind(W),
  };
  W.setTimeout = (...a) => {
    const id = own.setTimeout(...a);
    timers.push(() => own.clearTimeout(id));
    return id;
  };
  W.setInterval = (...a) => {
    const id = own.setInterval(...a);
    timers.push(() => own.clearInterval(id));
    return id;
  };
  W.requestAnimationFrame = (fn) => {
    const id = own.requestAnimationFrame(fn);
    timers.push(() => own.cancelAnimationFrame(id));
    return id;
  };

  function teardown() {
    for (const [target, type, fn, options] of tracked.splice(0)) realRemove.call(target, type, fn, options);
    for (const stop of timers.splice(0)) stop();
    for (const target of [W, D]) {
      for (const name in target) {
        if (name.startsWith("on") && typeof target[name] === "function") target[name] = null;
      }
    }
  }

  // Your code goes in as a script of its own at the end of the body, as
  // <script src="app.js"> would. Run again after a reload, it goes in a
  // block, so its const and let start fresh instead of clashing with the
  // ones the first run left behind.
  function inject(fresh) {
    offset = fresh ? 1 : 0;
    const script = D.createElement("script");
    script.text = fresh ? "{\n" + data.code + "\n}" : data.code;
    D.body.appendChild(script);
  }

  // A turn of the event loop that no timer throttling can stretch.
  function tick() {
    return new Promise((resolve) => {
      const channel = new MessageChannel();
      channel.port1.onmessage = () => resolve();
      channel.port2.postMessage(0);
    });
  }

  // ── What a check can use ──────────────────────────────────────────
  function fail(message) {
    const e = new Error(message);
    e.ccMessage = true;
    return e;
  }

  function expect(ok, message) {
    if (!ok) throw fail(message);
  }

  // How a message names what was clicked: the selector the check used,
  // else the element's id, classes or tag.
  function describe(target) {
    if (typeof target === "string") return target;
    if (!target || !target.tagName) return "it";
    if (target.id) return "#" + target.id;
    const tag = target.tagName.toLowerCase();
    return target.classList.length ? tag + "." + [...target.classList].join(".") : "an <" + tag + ">";
  }

  function find(target, doing) {
    const el = typeof target === "string" ? D.querySelector(target) : target;
    if (!el) throw fail(doing + " " + describe(target) + ": it isn't on the page.");
    return el;
  }

  function whereLine(line) {
    return line ? " on line " + line : "";
  }

  // A line more for the errors everyone meets first.
  function help(message) {
    if (/of null/.test(message)) {
      return " - document.querySelector found nothing, so check the selector against index.html.";
    }
    if (/JSON/.test(message)) {
      return " - JSON.parse was given something that isn't JSON. localStorage keeps strings: save JSON.stringify(...), load JSON.parse(...).";
    }
    if (/addEventListener.*parameter 2/.test(message)) {
      return " - addEventListener needs a function to call later, like () => ..., and was given what calling one straight away returned.";
    }
    return "";
  }

  // After each thing a check does: did your code throw, or did a form go
  // off unstopped?
  function settle(before, doing) {
    if (errors.length > before) {
      const e = errors[before];
      throw fail(doing + " made your code throw" + whereLine(e.line) + ": " + e.message + help(e.message));
    }
    if (reloadAsked) {
      throw fail(
        doing + " submitted the form, and nothing stopped it: the page would reload and lose " +
          "everything on it. Call event.preventDefault() in your submit listener, before anything " +
          "can return early.",
      );
    }
  }

  // The browser's own submit, done by hand. A check's frame may not submit
  // forms (nothing in it could survive a real one), so the events a real
  // submit fires are fired here, and an unstopped one is a failed check.
  function submit(form, submitter) {
    const init = { bubbles: true, cancelable: true };
    let event;
    try {
      event = new SubmitEvent("submit", { ...init, submitter: submitter || null });
    } catch (e) {
      event = new Event("submit", init);
    }
    if (form.dispatchEvent(event)) reloadAsked = true;
  }

  const BLOCKS_ENTER = /^(text|search|email|url|tel|password|date|month|week|time|datetime-local|number)$/;

  function isSubmitButton(el) {
    if (el instanceof HTMLButtonElement) return el.type === "submit";
    return el instanceof HTMLInputElement && (el.type === "submit" || el.type === "image");
  }

  function mouse(el, type) {
    const init = { bubbles: true, cancelable: true, composed: true, view: W, button: 0, detail: 1 };
    const Make = type.startsWith("pointer") && W.PointerEvent ? W.PointerEvent : W.MouseEvent;
    return el.dispatchEvent(new Make(type, type.startsWith("pointer") ? { ...init, pointerType: "mouse", isPrimary: true } : init));
  }

  function key(el, type, name) {
    const code = name === "Enter" ? "Enter" : name.length === 1 && /[a-z]/i.test(name) ? "Key" + name.toUpperCase() : name;
    const keyCode = name === "Enter" ? 13 : name.length === 1 ? name.toUpperCase().charCodeAt(0) : 0;
    return el.dispatchEvent(
      new KeyboardEvent(type, { key: name, code, keyCode, which: keyCode, charCode: type === "keypress" ? keyCode : 0, bubbles: true, cancelable: true, composed: true, view: W }),
    );
  }

  const cc = {
    /** Click an element (a selector or the element itself), as a mouse would. */
    click(target, label) {
      const el = find(target, "Clicking");
      const before = errors.length;
      const name = "Clicking " + (label || describe(target));
      if (el.disabled) return settle(before, name);
      mouse(el, "pointerdown");
      mouse(el, "mousedown");
      mouse(el, "pointerup");
      mouse(el, "mouseup");
      const go = mouse(el, "click");
      if (go && isSubmitButton(el) && el.form && !el.disabled) submit(el.form, el);
      settle(before, name);
    },
    /** Type text into a box, a key at a time, replacing what was there. */
    type(target, text) {
      const el = find(target, "Typing into");
      const before = errors.length;
      try {
        el.focus();
      } catch (e) {
        /* not focusable: typing still goes in */
      }
      el.value = "";
      for (const ch of String(text)) {
        if (key(el, "keydown", ch)) {
          el.value += ch;
          el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: ch }));
        }
        key(el, "keyup", ch);
      }
      el.dispatchEvent(new Event("change", { bubbles: true }));
      settle(before, "Typing into " + describe(target));
    },
    /** Press Enter in a box: in a form, that submits it, as a browser does. */
    enter(target) {
      const el = find(target, "Pressing Enter in");
      const before = errors.length;
      const name = "Pressing Enter in " + describe(target);
      if (key(el, "keydown", "Enter") && key(el, "keypress", "Enter")) {
        const form = el.form;
        if (form && el instanceof HTMLInputElement && BLOCKS_ENTER.test(el.type)) {
          const button = [...form.elements].find(isSubmitButton);
          if (button) {
            if (!button.disabled && mouse(button, "click")) submit(form, button);
          } else if ([...form.elements].filter((f) => f instanceof HTMLInputElement && BLOCKS_ENTER.test(f.type)).length === 1) {
            submit(form, null);
          }
        }
      }
      key(el, "keyup", "Enter");
      settle(before, name);
    },
    /**
     * Reload the page: everything goes but localStorage. The page's HTML
     * comes back as it was, and your code runs again from the top.
     */
    async reload() {
      const before = errors.length;
      // What a page hears as it goes: a save on the way out still counts.
      W.dispatchEvent(new Event("beforeunload", { cancelable: true }));
      W.dispatchEvent(new PageTransitionEvent("pagehide", { persisted: false }));
      W.dispatchEvent(new Event("unload"));
      teardown();
      const body = D.createElement("body");
      body.innerHTML = data.html;
      D.documentElement.replaceChild(body, D.body);
      inject(true);
      D.dispatchEvent(new Event("DOMContentLoaded", { bubbles: true }));
      W.dispatchEvent(new Event("load"));
      await tick();
      if (errors.length > before) {
        const e = errors[before];
        throw fail("After a reload your code threw" + whereLine(e.line) + ": " + e.message + help(e.message));
      }
    },
    /** Everything console.log printed, a line per call. */
    logs() {
      return logs.slice();
    },
    /** An element's text, trimmed; null when it isn't on the page. */
    text(target) {
      const el = typeof target === "string" ? D.querySelector(target) : target;
      return el ? el.textContent.trim() : null;
    },
    tick,
  };

  const $ = (selector) => D.querySelector(selector);
  const $$ = (selector) => [...D.querySelectorAll(selector)];

  async function runCheck() {
    await tick();
    if (errors.length) {
      const e = errors[0];
      const syntax = /^SyntaxError/.test(e.message);
      return {
        passed: false,
        message: (syntax ? "Your code has a mistake" : "Your code threw") + whereLine(e.line) + ": " + e.message + help(e.message),
      };
    }
    try {
      const body = new Function("cc", "expect", "$", "$$", '"use strict"; return (async () => {\n' + data.check + "\n})();");
      await body(cc, expect, $, $$);
      if (errors.length) {
        const e = errors[0];
        return { passed: false, message: "Your code threw" + whereLine(e.line) + ": " + e.message };
      }
      return { passed: true, message: "" };
    } catch (e) {
      if (e && e.ccMessage) return { passed: false, message: e.message };
      return { passed: false, message: "Your code threw: " + (e && e.message ? e.message : String(e)) };
    }
  }

  W.__ccDom = {
    /** Called at the end of the body: set up, then run your code. */
    boot(given) {
      data = { ...data, ...given };
      installStorage(data.mode === "check" ? {} : data.storage);
      inject(false);
      if (data.mode !== "check") return;
      realAdd.call(
        W,
        "load",
        () => {
          runCheck().then((result) => post({ type: "result", ...result }));
        },
        { once: true },
      );
    },
  };
})();
