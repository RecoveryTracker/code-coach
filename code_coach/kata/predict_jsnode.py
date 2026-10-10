"""Predict the output, in JavaScript, for code that runs under Node.js.

Node adds its own sharp edges to the language's: process.argv carries two
entries before yours, environment variables are always strings, reading a
file without an encoding gives a Buffer rather than text, JSON.parse is
stricter than a JavaScript object literal, path.join and path.resolve
disagree about an absolute second argument, an EventEmitter runs its
listeners in a fixed order, and what runs first - the synchronous code,
process.nextTick, a promise or a file callback - is a rule to know rather
than something to read off the page.

Every snippet runs in plain Node with no arguments and no network, and
none touches the disk except the one that makes a folder under the system
temp directory and removes it again. Every expected output was worked out
by hand first and then checked against what Node printed, and
tests/test_predict_jsnode_music_cooking.py keeps checking.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

NODE = "Node"


JS_NODE_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-jsnd-argv-indexes",
        level=1,
        name="Where the arguments start",
        family=NODE,
        language="javascript",
        code=(
            "const args = process.argv.slice(2);\n"
            "console.log(args.length, args[0]);\n"
            "console.log(process.argv.length, process.argv[2]);\n"
            "const [first = 'none'] = args;\n"
            "console.log(first);"
        ),
        expect="0 undefined\n2 undefined\nnone",
        why=(
            "process.argv always begins with two entries that are not "
            "yours: the path of the node program at index 0 and the path "
            "of the script at index 1. The first real argument is at "
            "index 2, which is why everyone writes slice(2). Run with "
            "nothing after the script name, the array has exactly those "
            "two entries, so index 2 is past the end and reads as "
            "undefined. A default in the destructuring catches it: "
            "defaults apply to undefined, which is exactly what a missing "
            "argument is."
        ),
    ),
    _p(
        id="predict-jsnd-json-parse-strict",
        level=1,
        name="JSON is not a JavaScript object",
        family=NODE,
        language="javascript",
        code=(
            "const texts = ['{\"a\": 1}', '{\"a\": 1,}', \"{'a': 1}\", '{a: 1}'];\n"
            "for (const t of texts) {\n"
            "  try {\n"
            "    console.log(JSON.parse(t).a);\n"
            "  } catch (e) {\n"
            "    console.log(e.name);\n"
            "  }\n"
            "}"
        ),
        expect="1\nSyntaxError\nSyntaxError\nSyntaxError",
        why=(
            "JSON looks like a JavaScript object literal and is much "
            "stricter. A trailing comma, single quotes and an unquoted "
            "key are all fine in a literal and all errors in JSON: keys "
            "and strings need double quotes, and nothing may follow the "
            "last item. JSON.parse throws a SyntaxError on any of them, "
            "so a config file read from disk and edited by hand needs a "
            "try/catch around the parse - a missing comma is one "
            "keystroke away."
        ),
    ),
    _p(
        id="predict-jsnd-join-vs-resolve",
        level=1,
        name="Join or resolve",
        family=NODE,
        language="javascript",
        code=(
            "const path = require('node:path').posix;\n"
            "console.log(path.join('/srv', 'app', '../logs', 'out.txt'));\n"
            "console.log(path.resolve('/srv', '/etc', 'conf'));\n"
            "console.log(path.join('/srv', '/etc', 'conf'));\n"
            "console.log(path.join('a', '..', '..', 'b'));"
        ),
        expect="/srv/logs/out.txt\n/etc/conf\n/srv/etc/conf\n../b",
        why=(
            "path.join just glues its parts together with the separator "
            "and tidies the result, so '../logs' climbs out of 'app', and "
            "an absolute-looking '/etc' is simply another part: "
            "'/srv/etc/conf'. path.resolve works like cd, from left to "
            "right: a part that starts with '/' throws away everything "
            "before it, so the answer is '/etc/conf'. The last line "
            "shows join climbing above where it started. (path.posix is "
            "used so the output is the same on Windows.)"
        ),
    ),
    _p(
        id="predict-jsnd-buffer-concat",
        level=2,
        name="What readFileSync gives back",
        family=NODE,
        language="javascript",
        code=(
            "const fs = require('node:fs');\n"
            "const os = require('node:os');\n"
            "const path = require('node:path');\n"
            "const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cc-'));\n"
            "const file = path.join(dir, 'n.txt');\n"
            "fs.writeFileSync(file, 'hi');\n"
            "const raw = fs.readFileSync(file);\n"
            "console.log(raw, raw.length, 'got ' + raw, typeof fs.readFileSync(file, 'utf8'));\n"
            "fs.rmSync(dir, { recursive: true });"
        ),
        expect="<Buffer 68 69> 2 got hi string",
        why=(
            "Without an encoding, readFileSync returns a Buffer - the "
            "raw bytes - and console.log shows it as hex: 68 and 69 are "
            "the codes for h and i. Its length counts bytes. Gluing it "
            "onto a string does not print '<Buffer ...>', though: "
            "concatenation calls its toString, which decodes the bytes "
            "as UTF-8, so 'got ' + raw reads 'got hi'. That is why the "
            "mistake survives for so long: it works until the file holds "
            "a character that is more than one byte, when length and "
            "string length part ways. Pass 'utf8' and get a string."
        ),
    ),
    _p(
        id="predict-jsnd-emitter-order",
        level=2,
        name="Who answers first",
        family=NODE,
        language="javascript",
        code=(
            "const { EventEmitter } = require('node:events');\n"
            "const e = new EventEmitter();\n"
            "e.on('go', () => console.log('A'));\n"
            "e.once('go', () => console.log('B'));\n"
            "e.prependListener('go', () => console.log('C'));\n"
            "e.emit('go');\n"
            "console.log('--');\n"
            "e.emit('go');"
        ),
        expect="C\nA\nB\n--\nC\nA",
        why=(
            "An emitter calls its listeners synchronously, in the order "
            "they were registered - except that prependListener puts one "
            "at the front, so C comes first, then A, then B. The B "
            "listener was added with once, so it removes itself after "
            "its first call, and the second emit runs only C and A. "
            "Nothing is queued or delayed: the emit call does not return "
            "until every listener has finished."
        ),
    ),
    _p(
        id="predict-jsnd-sync-vs-async-fs",
        level=2,
        name="Sync first, file last",
        family=NODE,
        language="javascript",
        code=(
            "const fs = require('node:fs');\n"
            "fs.readFile(__filename, () => console.log('file read'));\n"
            "Promise.resolve().then(() => console.log('microtask'));\n"
            "process.nextTick(() => console.log('tick'));\n"
            "console.log('sync', fs.readFileSync(__filename).length > 0);\n"
            "console.log('end');"
        ),
        expect="sync true\nend\ntick\nmicrotask\nfile read",
        why=(
            "All the plain synchronous code runs first, to the end of "
            "the script - including readFileSync, which blocks until "
            "it has the file, so 'sync true' comes before the "
            "asynchronous read has even been answered. Then Node empties "
            "its queues in order: process.nextTick callbacks first, "
            "then promise callbacks, and only afterwards does it go back "
            "to the event loop where the callback of the asynchronous "
            "readFile finally runs. Asynchronous file work always "
            "finishes after the current code does."
        ),
    ),
    _p(
        id="predict-jsnd-env-strings",
        level=2,
        name="Environment variables are strings",
        family=NODE,
        language="javascript",
        code=(
            "process.env.WORKERS = 4;\n"
            "process.env.DEBUG_FLAG = false;\n"
            "console.log(typeof process.env.WORKERS, process.env.WORKERS + 1);\n"
            "console.log(process.env.DEBUG_FLAG ? 'debug on' : 'debug off');\n"
            "console.log(process.env.CC_NOT_SET ?? 'default', Number(process.env.WORKERS) + 1);"
        ),
        expect="string 41\ndebug on\ndefault 5",
        why=(
            "Everything stored in process.env becomes a string, whatever "
            "was assigned: 4 turns into '4', so adding 1 glues rather "
            "than adds, giving '41'. False becomes the text 'false', "
            "and a non-empty string is truthy, so the flag reads as on "
            "- the classic way for 'turn it off' to turn it on. Compare "
            "with the text (=== 'true') and convert numbers on the way "
            "in. A variable that was never set is undefined, and ?? "
            "supplies the default."
        ),
    ),
    _p(
        id="predict-jsnd-json-roundtrip",
        level=3,
        name="What JSON drops on the way",
        family=NODE,
        language="javascript",
        code=(
            "const state = { n: undefined, f() {}, bad: NaN, set: new Set([1]), list: [undefined, 2] };\n"
            "const copy = JSON.parse(JSON.stringify(state));\n"
            "console.log(copy);\n"
            "console.log(JSON.stringify(state));"
        ),
        expect=(
            "{ bad: null, set: {}, list: [ null, 2 ] }\n"
            "{\"bad\":null,\"set\":{},\"list\":[null,2]}"
        ),
        why=(
            "JSON can only describe objects, arrays, strings, numbers, "
            "booleans and null, and stringify quietly adapts anything "
            "else. A property whose value is undefined or a function is "
            "left out of an object; in an array, undefined becomes null "
            "to keep the positions. NaN becomes null as well, and a Set "
            "has no enumerable properties, so it comes out as {}. "
            "Nothing is thrown, so saving state to disk this way "
            "silently loses data. For copying inside one program, "
            "structuredClone keeps Sets and Maps."
        ),
    ),
    _p(
        id="predict-jsnd-foreach-async",
        level=3,
        name="forEach does not wait",
        family=NODE,
        language="javascript",
        code=(
            "const names = [];\n"
            "async function main() {\n"
            "  [3, 1, 2].forEach(async (n) => { await null; names.push(n); });\n"
            "  console.log('after forEach', names.length);\n"
            "  for (const n of [6, 5]) { await null; names.push(n); }\n"
            "  console.log(names.join(','));\n"
            "}\n"
            "main();"
        ),
        expect="after forEach 0\n3,1,2,6,5",
        why=(
            "forEach ignores what its callback returns, and an async "
            "callback returns a promise, so forEach starts the three "
            "callbacks and moves on without waiting for any of them: "
            "nothing has been pushed when 'after forEach' prints. Each "
            "callback then resumes in the order it paused, 3, 1, 2. "
            "The for...of loop in main does wait at each await, so its "
            "pushes come after - 6, then 5. To wait for a batch, "
            "use for...of, or Promise.all over a map."
        ),
    ),
    _p(
        id="predict-jsnd-emitter-error",
        level=3,
        name="An error nobody is listening for",
        family=NODE,
        language="javascript",
        code=(
            "const { EventEmitter } = require('node:events');\n"
            "const e = new EventEmitter();\n"
            "try {\n"
            "  e.emit('error', new Error('disk full'));\n"
            "} catch (err) {\n"
            "  console.log('thrown:', err.message);\n"
            "}\n"
            "e.on('error', (err) => console.log('handled:', err.message));\n"
            "console.log(e.emit('error', new Error('again')), e.emit('quiet'));"
        ),
        expect="thrown: disk full\nhandled: again\ntrue false",
        why=(
            "'error' is the one event name an EventEmitter treats "
            "specially: with no listener for it, emit throws the error "
            "instead of returning, which is how an unhandled stream "
            "error can crash a program. Once a listener exists, emit "
            "calls it and returns true, meaning somebody heard. The "
            "last line also shows why 'handled: again' comes first: the "
            "arguments of console.log are worked out - and the listener "
            "runs - before console.log prints anything. An ordinary "
            "event nobody listens to returns false and does nothing."
        ),
    ),
    _p(
        id="predict-jsnd-exports-reassign",
        level=3,
        name="exports is only a shortcut",
        family=NODE,
        language="javascript",
        code=(
            "function load(factory) {\n"
            "  const module = { exports: {} };\n"
            "  const exports = module.exports;\n"
            "  factory(module, exports);\n"
            "  return module.exports;\n"
            "}\n"
            "const one = load((module, exports) => { exports.x = 1; });\n"
            "const two = load((module, exports) => { exports = { x: 2 }; });\n"
            "const three = load((module, exports) => { module.exports = { x: 3 }; });\n"
            "console.log(one, two, three);"
        ),
        expect="{ x: 1 } {} { x: 3 }",
        why=(
            "This is a miniature of what Node does around every "
            "CommonJS file: it hands the file a module object and a "
            "variable, exports, that starts out pointing at "
            "module.exports. What require gives back is always "
            "module.exports. Adding a property to exports changes the "
            "object they share, so `one` has x. But assigning a new "
            "object to exports only repoints the local variable - "
            "module.exports is untouched, so `two` is still the empty "
            "object. To replace the whole export, assign to "
            "module.exports itself."
        ),
    ),
)
