/*
The farm's commands, for a JavaScript program.

Run as:  node farm_api.js <your file>

Every command writes one line to the farm and waits for one line back (see
code_coach/farm/protocol.py). The names are the game's, spelled the way
JavaScript spells things: move(North), plant(Entities.Bush),
numItems(Items.Hay), canHarvest().

The values are the game's own names, as plain strings: North is "North" and
Entities.Bush is "Entities.Bush". So getEntityType() === Entities.Bush
works, and the cost getCost() hands back - { "Items.Hay": 5 } - is read
with cost[Items.Hay]. A tuple from the farm is an array, and None is null.

Waiting for the answer is synchronous, as it is in the game: fs.writeSync
and fs.readSync on the process's own stdout and stdin, no promises, no
event loop. Your program never needs await.

The block between the NAMES markers is filled in by render.py from
code_coach/farm/data.py, so the names here can never drift from the farm.
*/

"use strict";

const fs = require("fs");
const util = require("util");
const vm = require("vm");

const MARK = "\x1eCC";

// Your file runs under this name, so its errors say farm.js:LINE.
const CODE_NAME = "farm.js";

// NAMES-START
const DIRECTIONS = ["North", "East", "South", "West"];
const GROUPS = { Entities: {}, Items: {}, Grounds: {}, Unlocks: {}, Hats: {} };
const FUNCTIONS = [];
// NAMES-END

// Kept from the start, so a program that reassigns process.exit still
// stops when the farm says stop.
const exit = process.exit.bind(process);

// The farm said no: a command that is not unlocked, or used wrongly.
// A global, so a program can catch it: `catch (e) { if (e instanceof FarmError) ... }`.
class FarmError extends Error {
  constructor(message) {
    super(message);
    this.name = "FarmError";
  }
}

// ── The pipe ────────────────────────────────────────────────────────────

// Sleeping for a moment without an event loop. Atomics.wait is the one
// synchronous sleep JavaScript has, and Node lets the main thread use it.
const napCell = new Int32Array(new SharedArrayBuffer(4));
function nap() {
  Atomics.wait(napCell, 0, 0, 1);
}

// EAGAIN means the pipe is not ready yet (a non-blocking pipe, which some
// systems hand a child); it is ready a moment later, so try again.
// EPIPE or EOF on writing means the farm has gone, and so do we, quietly.
function writeAll(text) {
  const bytes = Buffer.from(text, "utf8");
  let sent = 0;
  while (sent < bytes.length) {
    try {
      sent += fs.writeSync(1, bytes, sent, bytes.length - sent);
    } catch (error) {
      if (error.code === "EAGAIN") {
        nap();
        continue;
      }
      if (error.code === "EPIPE" || error.code === "EOF") exit(0);
      throw error;
    }
  }
}

// Bytes read past the end of the last line. The farm sends one line per
// command, so this is nearly always empty, but a pipe may hand over a line
// in pieces and the pieces are put back together here - as bytes, so a
// character split between two reads is not broken in half.
let unread = Buffer.alloc(0);
const chunk = Buffer.alloc(1 << 16);

// One line from the farm, or null when the farm has closed the pipe.
function readLine() {
  for (;;) {
    const end = unread.indexOf(10);
    if (end >= 0) {
      const line = unread.subarray(0, end).toString("utf8");
      unread = unread.subarray(end + 1);
      return line;
    }
    let got;
    try {
      got = fs.readSync(0, chunk, 0, chunk.length, null);
    } catch (error) {
      if (error.code === "EAGAIN") {
        nap();
        continue;
      }
      if (error.code === "EOF") return null;
      throw error;
    }
    if (got === 0) return null;
    unread = Buffer.concat([unread, chunk.subarray(0, got)]);
  }
}

// Python's json.dumps writes pure ASCII, and so does this: every character
// past ASCII becomes a \uXXXX escape, so the line means the same whatever
// encoding the farm reads the pipe with.
function ascii(json) {
  return json.replace(/[\u007f-￿]/g, (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
}

// A value as the farm reads it. Nearly everything already is one; a Set
// goes as a list and a Map as a dictionary, as they would in Python.
function wire(value) {
  if (value === undefined) return null;
  if (typeof value === "bigint") return Number(value);
  if (Array.isArray(value)) return value.map(wire);
  if (value instanceof Set) return [...value].map(wire);
  if (value instanceof Map) {
    const out = {};
    for (const [key, item] of value) out[String(wire(key))] = wire(item);
    return out;
  }
  if (value !== null && typeof value === "object") {
    const out = {};
    for (const [key, item] of Object.entries(value)) out[key] = wire(item);
    return out;
  }
  return value;
}

function send(name, args) {
  writeAll(MARK + ascii(JSON.stringify({ f: name, a: args.map(wire) })) + "\n");
}

// One command: ask, wait, and hand back the answer.
function call(name, args) {
  send(name, args);
  const line = readLine();
  if (line === null) exit(0);
  const reply = JSON.parse(line);
  if (reply.stop) exit(0);
  if ("e" in reply) throw new FarmError(String(reply.e));
  return reply.r === undefined ? null : reply.r;
}

// ── The commands ────────────────────────────────────────────────────────

function command(name) {
  return (...args) => call(name, args);
}

// print and quickPrint send one finished line of text, the values joined
// with spaces the way JavaScript turns them into strings: print(1, "a")
// says "1 a".
function printer(name) {
  return (...values) => call(name, [values.map((value) => String(value)).join(" ")]);
}

// A list to take the smallest or largest of: an array, a Set, a range().
// A string is not one, and neither is a Map, as in Python.
function isList(value) {
  return (
    value !== null &&
    typeof value === "object" &&
    !(value instanceof Map) &&
    typeof value[Symbol.iterator] === "function"
  );
}

// min and max: of several values, min(3, 1, 2), or of one list, min([3, 1, 2]).
function extreme(name) {
  return (...values) => {
    if (values.length === 1 && isList(values[0])) return call(name, [Array.from(values[0])]);
    return call(name, values);
  };
}

// range() is Python's, which the game's for loops are written with and
// JavaScript does not have: range(3) is [0, 1, 2], range(1, 7, 2) is
// [1, 3, 5], range(3, 0, -1) is [3, 2, 1]. Worked out here, so it costs
// the drone nothing.
function range(start, end, step = 1) {
  if (end === undefined) {
    end = start;
    start = 0;
  }
  for (const n of [start, end, step]) {
    if (!Number.isInteger(n)) throw new TypeError(`range() takes whole numbers, not ${util.inspect(n)}`);
  }
  if (step === 0) throw new RangeError("range() step must not be zero");
  const out = [];
  for (let i = start; step > 0 ? i < end : i > end; i += step) out.push(i);
  return out;
}

// Entities, Items, ...: each a frozen object of the game's names, so
// Items.WeirdSubstance is "Items.Weird_Substance". Frozen, so a program
// cannot change what a name means; iterable, so `for (const item of Items)`
// reads as it does in the game's Python.
function group(members) {
  const values = Object.values(members);
  const named = { ...members };
  Object.defineProperty(named, Symbol.iterator, { value: () => values[Symbol.iterator]() });
  return Object.freeze(named);
}

// Everything your program sees: the directions, the groups, a function for
// every command (under its JavaScript name), range and FarmError.
function api() {
  const names = {};
  for (const direction of DIRECTIONS) names[direction] = direction;
  for (const [title, members] of Object.entries(GROUPS)) names[title] = group(members);
  const special = { print: printer, quick_print: printer, min: extreme, max: extreme };
  for (const [py, js] of FUNCTIONS) {
    // Named, so console.log(move) shows [Function: move].
    names[js] = Object.defineProperty((special[py] || command)(py), "name", { value: js });
  }
  names.range = range;
  names.FarmError = FarmError;
  return names;
}

// console.log is the game's quick_print - instant, and only in the output -
// because that is what it is for. print() is the game's own print, which
// writes in smoke above the drone and takes a second; nobody reaching for
// console.log means that. It keeps console.log's own formatting, so
// console.log([1, 2]) shows [ 1, 2 ] as it does everywhere else, and it is
// still a farm command: before the Debug unlock the farm refuses it, the
// same as quickPrint.
function routeConsole() {
  const log = (...values) => {
    call("quick_print", [util.format(...values)]);
  };
  console.log = log;
  console.info = log;
  console.debug = log;
}

// ── Running your file ───────────────────────────────────────────────────

// The first line of your file in a stack, which is where it went wrong:
// a frame reads "at farm.js:3:1" or "at tend (farm.js:3:5)", and a syntax
// error starts with "farm.js:3". The library's own frames name the whole
// path of farm_api.js, so they never match.
const YOUR_LINE = new RegExp("(?:^|[\\s(])" + CODE_NAME.replace(".", "\\.") + ":(\\d+)", "m");

// Tell the farm what went wrong and on which of your lines, then stop.
function crash(error) {
  const stack = error instanceof Error && typeof error.stack === "string" ? error.stack : "";
  const found = YOUR_LINE.exec(stack);
  const line = found ? Number(found[1]) : 0;
  let message;
  if (error instanceof FarmError) message = error.message;
  else if (error instanceof Error) message = Error.prototype.toString.call(error);
  else message = "Uncaught " + (typeof error === "string" ? error : util.inspect(error));
  try {
    send("__error__", [message, line]);
  } catch {
    // The farm has gone; there is no one left to tell.
  }
  exit(1);
}

function main(path) {
  // Room for a deep stack, so your line is still in it.
  Error.stackTraceLimit = Math.max(Error.stackTraceLimit, 50);
  Object.assign(globalThis, api());
  routeConsole();
  // Errors that happen later - in a timer, or a promise nobody caught -
  // are reported the same way.
  process.on("uncaughtException", crash);
  process.on("unhandledRejection", crash);
  const source = fs.readFileSync(path, "utf8");
  try {
    vm.runInThisContext(source, { filename: CODE_NAME });
  } catch (error) {
    crash(error);
  }
}

if (require.main === module) main(process.argv[2]);
