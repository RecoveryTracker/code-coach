/*
The farm's commands, for a JavaScript program.

Run as:  node farm_api.cjs <the file to run, by name>

(render.py writes this file out as farm_api.cjs: it is CommonJS, and the
package.json beside your files makes every .js file there an ES module.)

Your program is one or more files - main.js, utils.js ... - beside this
one, and it runs from the one named on the command line. They are ES
modules, so they import each other the way JavaScript does:

    import { harvestColumn } from "./utils.js";   // the .js is needed, as in any ES module
    import * as utils from "./utils.js";
    export function harvestColumn() { ... }

and each runs its top level once, the first time it is imported. The
farm's names are globals, so every file sees them without importing
anything.

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

More drones: spawnDrone(f) starts a new run of this same program in drone
mode (FARM_DRONE holds the job). That run reads the file you run with
TypeScript's parser - the farm says where it is, in FARM_TS - and runs
only its imports and its definitions: functions, classes, and variables
whose values are written out plainly. A file it imports runs as any import
does. Then it runs f, and sends back what f returned.

Simulation: simulate(filename, simUnlocks, simItems, simGlobals, seed,
speedup) runs one of your files as a new program on a fresh farm of its
own, and answers with the game seconds it took. A whole group stands for
all of its values - simulate("f1", Unlocks, ...) is every unlock - and so
does an array of them, or an object of levels, { [Unlocks.Speed]: 2 }. The
new program is an ordinary run of that file, not a drone: FARM_GLOBALS
holds the globals it was given, and they are set on globalThis before any
file of yours runs, so every file reads them as it reads North.

The block between the NAMES markers is filled in by render.py from
code_coach/farm/data.py, so the names here can never drift from the farm.
*/

"use strict";

const childProcess = require("child_process");
const fs = require("fs");
const Module = require("module");
const path = require("path");
const { fileURLToPath, pathToFileURL } = require("url");
const util = require("util");

const MARK = "\x1eCC";

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
  return json.replace(/[\u007f-\uffff]/g, (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
}

// The farm's own groups - Entities, Items ... - each as group() below made
// it. Only these go down the pipe as lists: any other object is a
// dictionary, however it was made.
const farmGroups = new WeakSet();

// A value as the farm reads it. Nearly everything already is one; a Set
// goes as a list and a Map as a dictionary, as they would in Python. A
// whole group is all of its values, as the game reads it:
// simulate("f1", Unlocks, ...) is every unlock there is.
function wire(value) {
  if (value === undefined) return null;
  if (typeof value === "bigint") return Number(value);
  if (Array.isArray(value)) return value.map(wire);
  if (value instanceof Set) return [...value].map(wire);
  if (farmGroups.has(value)) return [...value];
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
  farmGroups.add(named);
  return Object.freeze(named);
}

// ── Your files ──────────────────────────────────────────────────────────

// Your files are the .js files beside this one whose name a file of yours
// can have - lowercase letters, digits and _ - and the one that runs is
// named on the command line.
const HERE = __dirname;
const FILE_NAME = /^[a-z_][a-z0-9_]*$/;
let entry = "";

function fileOf(name) {
  return path.join(HERE, `${name}.js`);
}

function urlOf(name) {
  return pathToFileURL(fileOf(name)).href;
}

function yourFiles() {
  return fs
    .readdirSync(HERE)
    .filter((found) => found.endsWith(".js") && FILE_NAME.test(found.slice(0, -3)))
    .map((found) => found.slice(0, -3))
    .sort();
}

// A name the library can look up: one plain identifier, so looking it up
// as code can only ever look it up.
const IDENTIFIER = /^[\p{ID_Start}$_][\p{ID_Continue}$\u200c\u200d]*$/u;

// A module's names are its own: only code inside it can see them. So each
// of your files, as it starts to run, hands the library a way to look a
// name up at its top level - render.py puts the call that does it in front
// of your first line, on that same line, so every line keeps its number.
const lookups = new Map();
Object.defineProperty(globalThis, Symbol.for("farm.file"), {
  value: (name, lookup) => {
    lookups.set(name, lookup);
  },
});

// What a name means at the top level of one of your files - a function it
// declares, a const holding one, one it imports - or undefined.
function topLevel(file, name) {
  const lookup = lookups.get(file);
  if (typeof lookup !== "function" || typeof name !== "string" || !IDENTIFIER.test(name)) return undefined;
  try {
    return lookup(name);
  } catch {
    return undefined;
  }
}

// ── More drones ─────────────────────────────────────────────────────────

// How a new drone finds a function again: by its name, when the file you
// run has it under that name - it declares it, or imports it by name - and
// otherwise as utils.harvestColumn, by the file of yours that has it at its
// top level. Null when no file of yours has it at its top level.
function droneName(fn) {
  if (typeof fn !== "function" || /^class\b/.test(Function.prototype.toString.call(fn))) return null;
  if (topLevel(entry, fn.name) === fn) return fn.name;
  for (const file of lookups.keys()) {
    if (file !== entry && topLevel(file, fn.name) === fn) return `${file}.${fn.name}`;
  }
  return null;
}

// spawnDrone(harvestColumn, 3): start another drone here, running
// harvestColumn(3). Its handle, or null if every drone is already out.
// The new drone is a new run of your program that runs only that function,
// so it is sent by name - which is why it has to be one declared at the top
// level of a file of yours, where the new run will find it again. Its
// globals start from their declarations: nothing of yours is copied across
// but the arguments.
function spawnDrone(fn, ...args) {
  const name = droneName(fn);
  if (name === null) {
    throw new FarmError(
      "spawnDrone needs a function declared at the top level of your program, " +
        "like function harvestColumn() { ... }",
    );
  }
  return call("spawn_drone", [name, args, {}]);
}

// Everything your program sees: the directions, the groups, a function for
// every command (under its JavaScript name), range and FarmError.
function api() {
  const names = {};
  for (const direction of DIRECTIONS) names[direction] = direction;
  for (const [title, members] of Object.entries(GROUPS)) names[title] = group(members);
  const special = {
    print: printer,
    quick_print: printer,
    min: extreme,
    max: extreme,
    spawn_drone: () => spawnDrone,
  };
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

// ── When something goes wrong ───────────────────────────────────────────

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// Your files' folder, as a URL. A frame in one of your files reads
// "at tend (file:///C:/.../main.js:3:5)" or "at file:///C:/.../utils.js:2:1",
// and a failed import starts "file:///C:/.../main.js:3". (A drone's copy of
// the file you run, on a Node too old for hooks, is main.drone-1234.js.)
// This library is farm_api.cjs, so its own frames never match.
const FOLDER_URL = pathToFileURL(HERE).href.replace(/\/?$/, "/");
const YOUR_FRAME = new RegExp(escapeRegExp(FOLDER_URL) + "([a-z_][a-z0-9_]*)(?:\\.drone-\\d+)?\\.js:(\\d+)");

function samePath(a, b) {
  const [x, y] = [path.resolve(a), path.resolve(b)];
  return process.platform === "win32" ? x.toLowerCase() === y.toLowerCase() : x === y;
}

// A file of yours that does not compile stops the program before any of it
// runs, and V8 says what is wrong but not where. Node's own check says
// where, so each of your files is checked - the one you run first, as it
// is read first - and the one that fails with the same message is it.
// It costs a moment, and only when something is already wrong.
function syntaxErrorAt(error) {
  let first = null;
  for (const name of [entry, ...yourFiles().filter((file) => file !== entry)]) {
    const check = childProcess.spawnSync(process.execPath, ["--check", fileOf(name)], {
      encoding: "utf8",
      windowsHide: true,
      timeout: 20000,
    });
    if (check.error || check.status === 0 || typeof check.stderr !== "string") continue;
    const at = new RegExp(escapeRegExp(`${name}.js`) + ":(\\d+)\\s*$", "m").exec(check.stderr);
    const found = [at ? Number(at[1]) : 0, name];
    if (check.stderr.includes(String(error.message))) return found;
    if (first === null) first = found;
  }
  return first || [0, ""];
}

// An import of a file that is not there - "./utils" without its .js, say:
// on the line of the file of yours that imports it.
function missingImportAt(error) {
  const text = String(error.message);
  const from = /imported from (.+?)\s*(?:\n|$)/.exec(text);
  if (!from) return [0, ""];
  const importer = from[1].startsWith("file:") ? fileURLToPath(from[1]) : from[1];
  const name = path.basename(importer, ".js").replace(/\.drone-\d+$/, "");
  if (!FILE_NAME.test(name) || !samePath(path.dirname(importer), HERE)) return [0, ""];
  const missing = /Cannot find (?:module|package) '([^']+)'/.exec(text);
  let lines = [];
  try {
    lines = fs.readFileSync(importer, "utf8").split("\n");
  } catch {
    // Nothing to look in: the file, without a line.
  }
  for (let i = 0; missing && i < lines.length; i++) {
    for (const [, , spec] of lines[i].matchAll(/(["'])((?:(?!\1).)*)\1/g)) {
      const relative = spec.startsWith(".") || path.isAbsolute(spec);
      if (spec === missing[1] || (relative && samePath(path.resolve(HERE, spec), missing[1]))) {
        return [i + 1, name];
      }
    }
  }
  return [0, name];
}

// The line, and the file of yours, where an error happened: the deepest
// frame of its stack that is in one of your files - or, for a file that
// could not be loaded at all, the place that says why. [0, ""] if none.
function whereItWentWrong(error) {
  const stack = error instanceof Error && typeof error.stack === "string" ? error.stack : "";
  const found = YOUR_FRAME.exec(stack);
  if (found) return [Number(found[2]), found[1]];
  try {
    if (error instanceof SyntaxError) return syntaxErrorAt(error);
    if (error instanceof Error && error.code === "ERR_MODULE_NOT_FOUND") return missingImportAt(error);
  } catch {
    // Better an error without its line than no error at all.
  }
  return [0, ""];
}

// A message without the folder your files are in: "Cannot find module
// 'utils' imported from main.js" says all there is to say.
function tidy(message) {
  return message.split(FOLDER_URL).join("").split(HERE + path.sep).join("");
}

// Tell the farm what went wrong, in which file of yours and on which line,
// then stop.
function crash(error) {
  const [line, file] = whereItWentWrong(error);
  let message;
  if (error instanceof FarmError) message = error.message;
  else if (error instanceof Error) message = Error.prototype.toString.call(error);
  else message = "Uncaught " + (typeof error === "string" ? error : util.inspect(error));
  try {
    send("__error__", [tidy(message), line, file]);
  } catch {
    // The farm has gone; there is no one left to tell.
  }
  exit(1);
}

// ── Running one function, as a drone ────────────────────────────────────

// TypeScript's compiler, from where the farm says it is. It reads plain
// JavaScript too, and the web app already has it, so nothing is installed.
function typescript() {
  const where = process.env.FARM_TS;
  if (!where) {
    throw new FarmError(
      "A drone reads your program with TypeScript's parser, and the farm did not say where it is (FARM_TS).",
    );
  }
  return require(where);
}

// Every character but a line break: what blanks a statement out, so the
// lines after it keep their numbers.
const BLANK = /[^\r\n\u2028\u2029]/g;

// How the call render.py puts in front of your first line starts (see
// lookups above). A drone keeps it: it is how the drone finds its function.
const LEAD = 'globalThis[Symbol.for("farm.file")]';

// Your file with only its imports and definitions left: imports and
// re-exports, function and class declarations, let/const/var whose every
// value is a function, a class, or something written out plainly - a
// number, a string, true, null, North, Entities.Bush, or an array, object
// or template of those - an `export default` of such a value, and an
// `export { ... }` of names that are all still there. Every other
// statement is blanked to spaces, its newlines kept, so each line that is
// left is still on its own line number, and an error still names your line.
function definitionsOnly(source, fileName) {
  const ts = typescript();
  const K = ts.SyntaxKind;
  const sf = ts.createSourceFile(fileName, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  const PLAIN_NAMES = new Set(["undefined", "NaN", "Infinity", ...DIRECTIONS, ...Object.keys(GROUPS)]);
  const PLAIN_SIGNS = [K.MinusToken, K.PlusToken, K.ExclamationToken, K.TildeToken];

  function plain(node) {
    switch (node.kind) {
      case K.NumericLiteral:
      case K.BigIntLiteral:
      case K.StringLiteral:
      case K.NoSubstitutionTemplateLiteral:
      case K.RegularExpressionLiteral:
      case K.TrueKeyword:
      case K.FalseKeyword:
      case K.NullKeyword:
      case K.FunctionExpression:
      case K.ArrowFunction:
      case K.ClassExpression:
        return true;
      case K.Identifier:
        return PLAIN_NAMES.has(node.text);
      case K.ParenthesizedExpression:
        return plain(node.expression);
      case K.PrefixUnaryExpression:
        return PLAIN_SIGNS.includes(node.operator) && plain(node.operand);
      case K.TemplateExpression:
        return node.templateSpans.every((span) => plain(span.expression));
      case K.ArrayLiteralExpression:
        return node.elements.every((element) => {
          if (element.kind === K.OmittedExpression) return true;
          return plain(element.kind === K.SpreadElement ? element.expression : element);
        });
      case K.ObjectLiteralExpression:
        return node.properties.every(plainProperty);
      // Entities.Bush: a member of one of the farm's groups.
      case K.PropertyAccessExpression:
        return !node.questionDotToken && ts.isIdentifier(node.expression) && node.expression.text in GROUPS;
      default:
        return false;
    }
  }

  function plainProperty(property) {
    const computed = property.name && ts.isComputedPropertyName(property.name);
    if (computed && !plain(property.name.expression)) return false;
    switch (property.kind) {
      case K.PropertyAssignment:
        return plain(property.initializer);
      case K.ShorthandPropertyAssignment:
        return PLAIN_NAMES.has(property.name.text) && !property.objectAssignmentInitializer;
      case K.SpreadAssignment:
        return plain(property.expression);
      case K.MethodDeclaration:
      case K.GetAccessor:
      case K.SetAccessor:
        return true;
      default:
        return false;
    }
  }

  function isDefinition(statement) {
    if (statement.getStart(sf) === 0 && source.startsWith(LEAD)) return true;
    if (ts.isFunctionDeclaration(statement) || ts.isClassDeclaration(statement)) return true;
    if (ts.isImportDeclaration(statement)) return true;
    if (ts.isExportDeclaration(statement)) return Boolean(statement.moduleSpecifier);
    if (ts.isExportAssignment(statement)) return plain(statement.expression);
    if (!ts.isVariableStatement(statement)) return false;
    return statement.declarationList.declarations.every((d) => !d.initializer || plain(d.initializer));
  }

  // The names a kept statement declares, for an export list to name.
  function bindings(name, into) {
    if (ts.isIdentifier(name)) into.add(name.text);
    else for (const element of name.elements) if (!ts.isOmittedExpression(element)) bindings(element.name, into);
  }
  function declare(statement, into) {
    if ((ts.isFunctionDeclaration(statement) || ts.isClassDeclaration(statement)) && statement.name) {
      into.add(statement.name.text);
    } else if (ts.isVariableStatement(statement)) {
      for (const declaration of statement.declarationList.declarations) bindings(declaration.name, into);
    } else if (ts.isImportDeclaration(statement) && statement.importClause) {
      const clause = statement.importClause;
      if (clause.name) into.add(clause.name.text);
      const named = clause.namedBindings;
      if (named && ts.isNamespaceImport(named)) into.add(named.name.text);
      else if (named) for (const element of named.elements) into.add(element.name.text);
    }
  }

  const kept = new Set(sf.statements.filter(isDefinition));
  const declared = new Set();
  for (const statement of kept) declare(statement, declared);
  for (const statement of sf.statements) {
    const list = ts.isExportDeclaration(statement) && !statement.moduleSpecifier && statement.exportClause;
    if (list && ts.isNamedExports(list) && list.elements.every((e) => declared.has((e.propertyName || e.name).text))) {
      kept.add(statement);
    }
  }

  let out = "";
  let at = 0;
  for (const statement of sf.statements) {
    if (kept.has(statement)) continue;
    const start = statement.getStart(sf);
    out += source.slice(at, start) + source.slice(start, statement.end).replace(BLANK, " ");
    at = statement.end;
  }
  return out + source.slice(at);
}

// The drone's function has returned: say what with, and stop. The farm
// sends no answer to this one.
function finish(value) {
  send("__return__", [value]);
  exit(0);
}

function samePlace(href, url) {
  return href === url || (process.platform === "win32" && href.toLowerCase() === url.toLowerCase());
}

// The function a drone was sent to run, by the name droneName() gave it.
async function droneFunction(sent) {
  const dot = sent.indexOf(".");
  if (dot < 0) return topLevel(entry, sent);
  const file = sent.slice(0, dot);
  if (!lookups.has(file)) {
    if (!FILE_NAME.test(file) || !fs.existsSync(fileOf(file))) return undefined;
    await import(urlOf(file)); // as any import of it would: it runs its top level
  }
  return topLevel(file, sent.slice(dot + 1));
}

// Drone mode: FARM_DRONE names one of your functions and the arguments to
// give it. The file you run is its imports and definitions only - nothing
// else at its top level runs - and wherever it is imported from, even by a
// file of yours that imports it back, that is what it is. Then that
// function runs, and what it returns goes back for waitFor().
async function runDrone(text) {
  const job = JSON.parse(text);
  const kept = definitionsOnly(fs.readFileSync(fileOf(entry), "utf8"), `${entry}.js`);
  let url = urlOf(entry);
  let copy = null;
  if (typeof Module.registerHooks === "function") {
    Module.registerHooks({
      load(href, context, nextLoad) {
        if (samePlace(href, url)) return { format: "module", source: kept, shortCircuit: true };
        return nextLoad(href, context);
      },
    });
  } else {
    // A Node without module hooks (before 22.15): the definitions go in a
    // copy of their own beside your files. A file of yours that imports the
    // file you run back gets the whole of it there.
    copy = path.join(HERE, `${entry}.drone-${process.pid}.js`);
    fs.writeFileSync(copy, kept);
    url = pathToFileURL(copy).href;
  }
  try {
    await import(url);
  } finally {
    if (copy) fs.rmSync(copy, { force: true });
  }
  const name = String(job.fn);
  const fn = await droneFunction(name);
  if (typeof fn !== "function") {
    throw new FarmError(
      `This drone was to run ${name}(), but your program declares no function of that name at its top level.`,
    );
  }
  const value = fn(...(Array.isArray(job.args) ? job.args : []));
  // An async function hands back a promise: what it settles to is the answer.
  if (value instanceof Promise) value.then(finish, crash);
  else finish(value);
}

// ── Running your program ────────────────────────────────────────────────

// A simulation's starting globals. simulate() runs a file of yours as a new
// program, and FARM_GLOBALS holds the globals it was given as they went
// down the pipe - which is already how JavaScript has them, the game's
// names being strings here. Each is set on globalThis before any file of
// yours runs, so every file reads it by its name.
function startingGlobals() {
  const text = process.env.FARM_GLOBALS;
  if (!text) return;
  let given = null;
  try {
    given = JSON.parse(text);
  } catch {
    // Not JSON at all: said just below, rather than as a SyntaxError of yours.
  }
  if (given === null || typeof given !== "object" || Array.isArray(given)) {
    throw new FarmError("The farm sent this simulation its globals as something other than an object.");
  }
  for (const [name, value] of Object.entries(given)) {
    try {
      globalThis[name] = value;
    } catch {
      throw new FarmError(`A simulation can't start with a global called ${name}: JavaScript doesn't let it change.`);
    }
  }
}

function main(name) {
  // Room for a deep stack, so your line is still in it.
  Error.stackTraceLimit = Math.max(Error.stackTraceLimit, 50);
  Object.assign(globalThis, api());
  routeConsole();
  // Errors that happen later - in a timer, or a promise nobody caught -
  // are reported the same way.
  process.on("uncaughtException", crash);
  process.on("unhandledRejection", crash);
  entry = String(name || "main");
  const job = process.env.FARM_DRONE;
  let running;
  if (!FILE_NAME.test(entry) || !fs.existsSync(fileOf(entry))) {
    running = Promise.reject(new FarmError(`There is no file called ${entry} to run.`));
  } else {
    try {
      // A drone of a simulation starts from them too, as from its declarations.
      startingGlobals();
      running = job ? runDrone(job) : import(urlOf(entry));
    } catch (error) {
      running = Promise.reject(error);
    }
  }
  running.catch(crash);
}

if (require.main === module) main(process.argv[2]);
