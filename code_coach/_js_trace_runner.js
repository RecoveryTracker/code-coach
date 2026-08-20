/**
 * Run a student's JavaScript under the debugger and print JSON snapshots.
 *
 * The Python tracer uses sys.settrace, which hands you the frame and its
 * locals directly. JavaScript has no equivalent from inside the language —
 * you cannot enumerate the variables of a scope you are standing in. What it
 * does have is Node's own inspector, the same machinery a debugger uses, and
 * that can be driven in-process: pause on each statement, read the scope
 * chain, step, repeat.
 *
 * The alternative would be rewriting the source to record variables as it
 * goes, which means parsing JavaScript, and a half-parser would quietly
 * mis-trace exactly the clever code worth watching.
 *
 * Output shape matches _trace_runner.py exactly, so one set of diagrams draws
 * both languages.
 */

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const inspector = require("node:inspector");

const SENTINEL = "<<<CODE_COACH_TRACE>>>";

// Same ceilings as the Python tracer: the point is a readable picture, not a
// complete memory dump.
const MAX_STEPS = 400;
const MAX_ITEMS = 60;
const MAX_FIELDS = 12;
const MAX_DEPTH = 8;
const MAX_STRING = 120;

const target = process.argv[2];
const source = fs.readFileSync(target, "utf8");
const scriptName = path.resolve(target);

const session = new inspector.Session();
session.connect();

/**
 * Post an inspector command and return its result.
 *
 * The callback runs synchronously while the debugger is paused, which is what
 * makes this whole approach possible — we can interrogate a scope from inside
 * the pause handler without letting the program run on.
 */
function post(method, params) {
  let out = null;
  let failed = null;
  session.post(method, params || {}, (err, result) => {
    failed = err;
    out = result;
  });
  if (failed) throw failed;
  return out;
}

// ── Value encoding ─────────────────────────────────────────
// Mirrors _encode in the Python runner: primitives inline, everything else
// into a heap keyed by reference, so shared and cyclic structures terminate.

function primOf(remote) {
  const t = remote.type;
  if (t === "undefined") return { k: "prim", t: "none", v: null };
  if (t === "boolean") return { k: "prim", t: "bool", v: remote.value };
  if (t === "number") {
    // Infinity and NaN arrive as descriptions rather than values.
    if (remote.unserializableValue !== undefined) {
      return { k: "prim", t: "float", v: String(remote.unserializableValue) };
    }
    const v = remote.value;
    return { k: "prim", t: Number.isInteger(v) ? "int" : "float", v };
  }
  if (t === "string") {
    const v = remote.value == null ? "" : String(remote.value);
    return {
      k: "prim",
      t: "str",
      v: v.slice(0, MAX_STRING),
      clipped: v.length > MAX_STRING,
    };
  }
  if (t === "object" && remote.subtype === "null") {
    return { k: "prim", t: "none", v: null };
  }
  return null;
}

/** Own enumerable properties of a remote object, in order. */
function propsOf(objectId) {
  const res = post("Runtime.getProperties", {
    objectId,
    ownProperties: true,
    generatePreview: false,
  });
  return (res.result || []).filter((p) => p.enumerable && p.value);
}

function encode(remote, heap, seen, depth) {
  depth = depth || 0;
  const leaf = primOf(remote);
  if (leaf) return leaf;

  if (depth >= MAX_DEPTH) {
    return { k: "prim", t: "str", v: "…", clipped: true };
  }
  if (remote.type === "function") {
    return { k: "prim", t: "str", v: `function ${remote.description || ""}`.trim() };
  }
  const objectId = remote.objectId;
  if (!objectId) {
    return { k: "prim", t: "str", v: remote.description || String(remote.type) };
  }
  if (seen.has(objectId)) return { k: "ref", id: seen.get(objectId) };

  const ref = seen.size + 1;
  seen.set(objectId, ref);
  const entry = {};
  heap[ref] = entry;

  const subtype = remote.subtype;
  try {
    if (subtype === "array") {
      const items = propsOf(objectId)
        .filter((p) => /^\d+$/.test(p.name))
        .slice(0, MAX_ITEMS)
        .map((p) => encode(p.value, heap, seen, depth + 1));
      const n = Number(
        (remote.description || "").replace(/^\w*\((\d+)\)$/, "$1"),
      );
      entry.k = "list";
      entry.tuple = false;
      entry.n = Number.isFinite(n) ? n : items.length;
      entry.items = items;
    } else if (subtype === "map") {
      entry.k = "dict";
      entry.pairs = entriesOfCollection(objectId, heap, seen, depth, true);
      entry.n = entry.pairs.length;
    } else if (subtype === "set") {
      entry.k = "set";
      entry.items = entriesOfCollection(objectId, heap, seen, depth, false);
      entry.n = entry.items.length;
    } else {
      const props = propsOf(objectId).slice(0, MAX_FIELDS);
      const cls = className(remote);
      if (cls === "Object") {
        // A plain object in JavaScript is what a dict is in Python — the
        // hash-map diagram is the right picture for it.
        entry.k = "dict";
        entry.n = props.length;
        entry.pairs = props.map((p) => [
          { k: "prim", t: "str", v: p.name },
          encode(p.value, heap, seen, depth + 1),
        ]);
      } else {
        const fields = {};
        for (const p of props) fields[p.name] = encode(p.value, heap, seen, depth + 1);
        entry.k = "obj";
        entry.cls = cls;
        entry.fields = fields;
      }
    }
  } catch (err) {
    entry.k = "opaque";
    entry.cls = className(remote);
    entry.v = String(remote.description || "").slice(0, MAX_STRING);
  }
  return { k: "ref", id: ref };
}

function className(remote) {
  return remote.className || remote.description || "Object";
}

/**
 * Map and Set hide their contents behind internal slots, so they're read by
 * asking the runtime to spread them into a plain array.
 */
function entriesOfCollection(objectId, heap, seen, depth, asPairs) {
  const res = post("Runtime.callFunctionOn", {
    objectId,
    functionDeclaration: asPairs
      ? "function () { return Array.from(this.entries()).slice(0, 60); }"
      : "function () { return Array.from(this.values()).slice(0, 60); }",
    returnByValue: false,
  });
  const arrayId = res.result && res.result.objectId;
  if (!arrayId) return [];
  const items = propsOf(arrayId).filter((p) => /^\d+$/.test(p.name));
  if (!asPairs) {
    return items.map((p) => encode(p.value, heap, seen, depth + 1));
  }
  return items.map((p) => {
    const pair = propsOf(p.value.objectId).filter((q) => /^\d+$/.test(q.name));
    return [
      encode(pair[0].value, heap, seen, depth + 1),
      encode(pair[1].value, heap, seen, depth + 1),
    ];
  });
}

// ── Stepping ───────────────────────────────────────────────

const steps = [];
let truncated = false;
let emitted = false;

/** Write the payload exactly once, however we got here. */
function emit() {
  if (emitted) return;
  emitted = true;
  process.stdout.write(
    SENTINEL +
      JSON.stringify({
        steps,
        truncated,
        stdout: out.join("\n"),
        stderr: err.join("\n"),
        error,
        source,
      }),
  );
}

/**
 * Variables visible where we're paused.
 *
 * Block scope matters as much as local: `for (let i ...)` and a `const` inside
 * a loop body live there, and those are exactly the variables you're watching.
 * Closure scope is included because a callback reading an outer `left` or
 * `count` is the other case worth seeing. Global is excluded — it would dump
 * every built-in into the picture.
 *
 * The scope chain runs innermost first, so the first definition of a name
 * wins, which is what shadowing means.
 */
const SHOWN_SCOPES = new Set(["local", "closure", "block", "catch"]);

// Loading the file as a module wraps it in a function whose parameters are
// these. They're real variables in scope, and showing them would put Node's
// module object in the picture next to the student's `seen` and `left`.
const WRAPPER_NAMES = new Set([
  "exports",
  "require",
  "module",
  "__filename",
  "__dirname",
  "this",
  "arguments",
]);

function scopeVars(callFrame, heap, seen) {
  const vars = {};
  for (const scope of callFrame.scopeChain || []) {
    if (!SHOWN_SCOPES.has(scope.type)) continue;
    if (!scope.object || !scope.object.objectId) continue;
    let props;
    try {
      props = propsOf(scope.object.objectId);
    } catch {
      continue;
    }
    for (const p of props) {
      if (WRAPPER_NAMES.has(p.name)) continue;
      if (Object.prototype.hasOwnProperty.call(vars, p.name)) continue;
      if (Object.keys(vars).length >= 40) break;
      try {
        vars[p.name] = encode(p.value, heap, seen, 0);
      } catch {
        vars[p.name] = { k: "prim", t: "str", v: "<unreadable>" };
      }
    }
  }
  return vars;
}

session.on("Debugger.paused", ({ params }) => {
  const frame = (params.callFrames || [])[0];
  if (!frame || !isOurs(frame)) {
    post("Debugger.resume");
    return;
  }
  if (steps.length >= MAX_STEPS) {
    // A tight loop can produce millions of line events. Stop here and hand
    // back what we have: resuming a loop that never ends would spin until the
    // subprocess timeout and the student would get an error instead of the
    // four hundred steps we already captured.
    truncated = true;
    emit();
    process.exit(0);
  }
  const heap = {};
  const seen = new Map();
  try {
    steps.push({
      line: frame.location.lineNumber + 1, // CDP is 0-based, we report 1-based
      func: frame.functionName || "<module>",
      vars: scopeVars(frame, heap, seen),
      heap,
    });
  } catch {
    /* a snapshot we can't read shouldn't stop the trace */
  }
  post("Debugger.resume");
});

const scriptIds = new Set();
function isOurs(frame) {
  return scriptIds.has(frame.location.scriptId);
}

// The URL the inspector reports is a file:// URL with forward slashes, which
// on Windows is not the path we were handed.
const scriptUrl = "file:///" + scriptName.replace(/\\/g, "/");

session.on("Debugger.scriptParsed", ({ params }) => {
  if (!params.url) return;
  if (params.url === scriptUrl || params.url === scriptName) {
    scriptIds.add(params.scriptId);
  }
});

// ── Run ────────────────────────────────────────────────────

const out = [];
const err = [];
const origLog = console.log;
const origErr = console.error;
console.log = (...args) => out.push(args.map(fmt).join(" "));
console.error = (...args) => err.push(args.map(fmt).join(" "));

function fmt(v) {
  if (typeof v === "string") return v;
  try {
    return require("node:util").inspect(v, { depth: 3, breakLength: 100 });
  } catch {
    return String(v);
  }
}

let error = null;
post("Debugger.enable");
post("Runtime.enable");

// A breakpoint on every line of the student's file, set before the file is
// even loaded — the inspector keeps them pending and binds them when the
// script is parsed.
//
// Breaking on every line rather than stepping is what makes this reliable.
// A single breakpoint on line 1 only binds if line 1 happens to be
// executable, and a file that opens with a function declaration silently
// traced nothing at all. Resuming from one breakpoint runs to the next,
// which is by construction the next line of their code that executes — so
// Node's internals are skipped without having to detect them.
//
// The limit of line breakpoints is that several statements crammed onto one
// line only break at the first, so a whole loop written on a single line
// traces once rather than every pass. Normally-formatted code isn't affected,
// and the subprocess timeout still catches the pathological case.
const urlRegex = scriptUrl.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const lineCount = source.split("\n").length;
for (let line = 0; line < lineCount; line++) {
  try {
    post("Debugger.setBreakpointByUrl", { lineNumber: line, urlRegex });
  } catch {
    /* a line with nothing executable on it simply never binds */
  }
}

try {
  require(scriptName);
} catch (e) {
  error = {
    type: (e && e.constructor && e.constructor.name) || "Error",
    message: String((e && e.message) || e),
    line: lineOf(e),
  };
} finally {
  try {
    post("Debugger.disable");
  } catch {
    /* already gone */
  }
  console.log = origLog;
  console.error = origErr;
  session.disconnect();
}

/** Pull the line number out of a stack trace pointing at the student's file. */
function lineOf(e) {
  const stack = (e && e.stack) || "";
  const escaped = scriptName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = new RegExp(`${escaped}:(\\d+):`).exec(stack);
  return match ? Number(match[1]) : null;
}

emit();
