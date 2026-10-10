"""JavaScript for Node.js: files, paths, arguments, events and a small server.

The lines are the ones a command-line tool or a small service is made of:
the path module, process.argv and process.env, reading and writing files
both ways (the synchronous calls and fs/promises), JSON on disk, listing a
folder, EventEmitter, a tiny http server and a fetch to it, readline and
streams, util.parseArgs, and the difference between require and import.

Everything uses the `node:` prefix for built-in modules, which is how
current Node documents them and keeps a built-in from being mistaken for a
package of the same name. A line is never an `import` declaration: each is
parsed as the body of an async function by the tests, and a static import
only belongs at the top of a file. The dynamic `await import(...)` is here
instead, and it works in both module systems.

The blocks are whole little programs that print their result, and the
tests run every one in Node and hold what it prints to an answer worked
out by hand. A block that touches the disk makes its own folder with
mkdtemp under the system temp folder and removes it again; the one with a
server listens on 127.0.0.1, port 0 (the system picks a free one), asks
itself a question and closes. No block prints a path or a port.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

JSNODE_LINES: tuple[Passage, ...] = (
    # The path module
    _s("const path = require('node:path');",
       "the node: prefix says it is built in, not a package"),
    _s("const file = path.join(__dirname, 'data', 'notes.json');",
       "join with this system's separator; __dirname is the script's folder"),
    _s("const abs = path.resolve('data', 'notes.json');",
       "resolve builds an absolute path, starting from the current folder"),
    _s("const ext = path.extname('track.final.mp3');",
       "'.mp3': from the last dot on"),
    _s("const base = path.basename('/music/mix.wav', '.wav');",
       "'mix': the last part, with the extension taken off"),
    _s("const { dir, name, ext } = path.parse(file);",
       "a path split into folder, name and extension"),
    _s("const backup = path.join(dir, `${name}.bak`);",
       "a sibling file in the same folder"),
    _s("const rel = path.relative('/srv/app', '/srv/app/logs/out.txt');",
       "'logs/out.txt': how to get from the first path to the second"),
    _s("const isAbs = path.isAbsolute(input);", "true for /srv/app, false for ./app"),
    _s("const here = pathToFileURL(file).href;",
       "a file:// address, which is what ESM imports and import.meta use"),

    # Arguments and the environment
    _s("const args = process.argv.slice(2);",
       "the first two entries are node and the script, so skip them"),
    _s("const [input, output = 'out.txt'] = process.argv.slice(2);",
       "positional arguments, the second with a default"),
    _s("const verbose = process.argv.includes('--verbose');", "a flag is just a string"),
    _s("const port = Number(process.env.PORT) || 3000;",
       "env values are strings; a missing one makes NaN, which falls through"),
    _s("const host = process.env.HOST ?? '127.0.0.1';",
       "?? only falls back on undefined or null, so an empty string survives"),
    _s("const isProd = process.env.NODE_ENV === 'production';",
       "the usual switch between a development and a live setup"),
    _s("if (!input) { console.error('usage: node app.js <file>'); process.exit(1); }",
       "the usage message goes to stderr, then a failing exit code"),
    _s("process.exitCode = 1;", "mark the run as failed, but let it finish cleanly"),
    _s("process.on('SIGINT', () => { console.log('bye'); process.exit(0); });",
       "Ctrl+C arrives as a signal you can catch"),
    _s("console.error(`failed: ${err.message}`);",
       "errors on stderr leave stdout clean for piping"),
    _s("const { heapUsed } = process.memoryUsage();", "bytes of memory the program holds"),

    # Files, the synchronous way
    _s("const fs = require('node:fs');", "the file system module"),
    _s("const text = fs.readFileSync(file, 'utf8');",
       "with an encoding you get a string; without one, a Buffer"),
    _s("const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));",
       "read a JSON file into an object"),
    _s("fs.writeFileSync('out.json', JSON.stringify(data, null, 2));",
       "two-space pretty-printed JSON; this replaces the whole file"),
    _s("fs.appendFileSync('app.log', `${line}\\n`);", "add to the end of a log"),
    _s("if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });",
       "make the folder and any parents it needs"),
    _s("const names = fs.readdirSync(dir).filter((f) => f.endsWith('.json'));",
       "just the JSON files in a folder"),
    _s("const entries = fs.readdirSync(dir, { withFileTypes: true });",
       "Dirent objects, which know if each one is a file or a folder"),
    _s("const folders = entries.filter((e) => e.isDirectory()).map((e) => e.name);",
       "the names of the sub-folders only"),
    _s("const { size, mtimeMs } = fs.statSync(file);",
       "size in bytes and the last modified time"),
    _s("const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'app-'));",
       "a fresh folder with a unique name, for scratch work"),
    _s("fs.rmSync(tmp, { recursive: true, force: true });",
       "delete a folder and everything in it, quietly if it is gone"),
    _s("fs.renameSync(`${file}.tmp`, file);",
       "write beside the file, then rename: a crash can't leave half a file"),

    # Files, the promise way
    _s("const fsp = require('node:fs/promises');", "the same calls, returning promises"),
    _s("const text = await fsp.readFile(file, 'utf8');", "read without blocking"),
    _s("await fsp.writeFile(file, JSON.stringify(state), 'utf8');",
       "save the state as JSON"),
    _s("const files = await fsp.readdir(dir);", "the names inside a folder"),
    _s("const stats = await Promise.all(files.map((f) => fsp.stat(path.join(dir, f))));",
       "stat every file at once"),
    _s("try { await fsp.access(file); } catch { console.log('missing'); }",
       "access throws when the file can't be reached"),
    _s("if (err.code === 'ENOENT') return null;",
       "the error code for 'no such file or directory'"),
    _s("const { readFile, writeFile } = require('node:fs/promises');",
       "pick the functions out directly"),
    _s("const safe = (s) => { try { return JSON.parse(s); } catch { return null; } };",
       "JSON.parse throws on bad text, so wrap it"),

    # Events
    _s("const { EventEmitter } = require('node:events');", "Node's publish and subscribe"),
    _s("const bus = new EventEmitter();", "one emitter to share"),
    _s("bus.on('save', (file) => console.log('saved', file));",
       "run this every time 'save' is emitted"),
    _s("bus.once('ready', () => console.log('first time only'));",
       "runs once, then removes itself"),
    _s("bus.emit('save', 'notes.json');",
       "listeners run at once, in the order they were added"),
    _s("bus.off('save', handler);", "unsubscribe the very same function"),
    _s("class Job extends EventEmitter {}", "an object that can announce its progress"),
    _s("const [value] = await once(bus, 'ready');",
       "events.once waits for an event, as a promise of its arguments"),

    # A small server, and a request to it
    _s("const http = require('node:http');", "the built-in http server"),
    _s("const server = http.createServer((req, res) => res.end('ok'));",
       "the smallest server there is"),
    _s("server.listen(3000, '127.0.0.1', () => console.log('up'));",
       "only this machine can reach it"),
    _s("const { pathname, searchParams } = new URL(req.url, 'http://localhost');",
       "req.url is only a path, so give URL a base"),
    _s("res.writeHead(200, { 'Content-Type': 'application/json' });",
       "status and headers, before the body"),
    _s("res.end(JSON.stringify({ ok: true, path: pathname }));", "reply with JSON"),
    _s("if (req.method !== 'GET') return res.writeHead(405).end();",
       "405: method not allowed"),
    _s("const reply = await fetch('http://127.0.0.1:3000/health');",
       "fetch is built into Node 18 and up"),
    _s("const body = await reply.json();", "reading the body is a promise as well"),
    _s("const { port } = server.address();", "after listen(0): which port we got"),
    _s("server.close(() => console.log('closed'));", "stop listening, then call back"),

    # Reading and streaming
    _s("const readline = require('node:readline');", "lines from a stream"),
    _s("const rl = readline.createInterface({ input: process.stdin });",
       "turn standard input into lines"),
    _s("for await (const line of rl) console.log(line.toUpperCase());",
       "one line at a time, however big the input"),
    _s("const { pipeline } = require('node:stream/promises');",
       "joins streams and cleans up when any fails"),
    _s("await pipeline(fs.createReadStream('in.txt'), fs.createWriteStream('out.txt'));",
       "copy a file without holding it all in memory"),
    _s("const stream = fs.createReadStream(file, { encoding: 'utf8' });",
       "chunks arrive as strings"),
    _s("for await (const chunk of stream) bytes += chunk.length;",
       "a stream is an async iterable"),
    _s("const { parseArgs } = require('node:util');",
       "built-in command line parsing, no package needed"),
    _s("const { values } = parseArgs({ options: { port: { type: 'string' } } });",
       "--port 8080 becomes values.port"),
    _s("const { promisify } = require('node:util');",
       "turn a callback function into a promise one"),
    _s("const { setTimeout: sleep } = require('node:timers/promises');",
       "a promise-returning setTimeout, renamed on the way in"),

    # Modules: require and import
    _s("module.exports = { load, save };", "CommonJS: what require('./store') gets back"),
    _s("const { load } = require('./store.js');", "CommonJS: loads synchronously"),
    _s("const mod = await import('node:crypto');",
       "dynamic import works in both module systems"),
    _s("const id = crypto.randomUUID();", "a random unique id, built in"),
    _s("const hash = crypto.createHash('sha256').update(text).digest('hex');",
       "a SHA-256 fingerprint as hex text"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"JavaScript · {note}")


JSNODE_BLOCKS: tuple[Passage, ...] = (
    _b(r"""const path = require('node:path').posix;
const file = '/home/ann/music/demo.final.mp3';

console.log(path.basename(file), path.extname(file));
console.log(path.basename(file, '.mp3'), path.dirname(file));
console.log(path.join('/a', 'b', '../c', 'd.txt'));
console.log(path.parse(file).name);""",
       "taking a path apart with path.posix"),
    _b(r"""const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cc-'));
const file = path.join(dir, 'config.json');
fs.writeFileSync(file, JSON.stringify({ port: 3000, debug: false }, null, 2));
const config = JSON.parse(fs.readFileSync(file, 'utf8'));
console.log(config.port + 1, config.debug);
console.log(fs.readFileSync(file, 'utf8').split('\n').length);
fs.rmSync(dir, { recursive: true });""",
       "JSON saved to disk and read back"),
    _b(r"""const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cc-'));
for (const name of ['b.txt', 'a.js', 'c.txt', 'notes.md']) {
  fs.writeFileSync(path.join(dir, name), name);
}
const txt = fs.readdirSync(dir).filter((f) => path.extname(f) === '.txt');
console.log(txt.sort().join(','), fs.readdirSync(dir).length);
fs.rmSync(dir, { recursive: true });""",
       "listing a folder and filtering by extension"),
    _b(r"""const { EventEmitter } = require('node:events');

const bus = new EventEmitter();
const log = [];
bus.on('ping', (n) => log.push(`first ${n}`));
bus.once('ping', (n) => log.push(`once ${n}`));
bus.prependListener('ping', (n) => log.push(`early ${n}`));
bus.emit('ping', 1);
bus.emit('ping', 2);
console.log(log.join(' | '));
console.log(bus.listenerCount('ping'), bus.emit('nobody'));""",
       "listener order, once and prependListener"),
    _b(r"""const args = process.argv.slice(2);
const port = Number(process.env.CC_NO_SUCH_PORT ?? 8080);
const name = process.env.CC_NO_SUCH_NAME || 'world';
const verbose = args.includes('--verbose');

console.log(args.length, port + 1, `hello ${name}`);
console.log(verbose);""",
       "arguments and environment variables with defaults"),
    _b(r"""const { parseArgs } = require('node:util');

const { values, positionals } = parseArgs({
  args: ['-v', '--port', '4000', 'input.txt', 'out.txt'],
  options: {
    verbose: { type: 'boolean', short: 'v' },
    port: { type: 'string', default: '3000' },
  },
  allowPositionals: true,
});
console.log(values.verbose, Number(values.port) + 1);
console.log(positionals);""",
       "parsing a command line with util.parseArgs"),
    _b(r"""const readline = require('node:readline');
const { Readable } = require('node:stream');

async function main() {
  const input = Readable.from(['3 apples\n', '5 pears\nfig\n']);
  const rl = readline.createInterface({ input });
  let total = 0;
  for await (const line of rl) total += parseInt(line, 10) || 0;
  console.log('total', total);
}
main();""",
       "readline over a stream, adding up the numbers"),
    _b(r"""const { Readable, Transform, Writable } = require('node:stream');
const { pipeline } = require('node:stream/promises');

const upper = new Transform({
  transform(chunk, enc, cb) { cb(null, chunk.toString().toUpperCase()); },
});
const out = [];
const sink = new Writable({
  write(chunk, enc, cb) { out.push(chunk.toString()); cb(); },
});
pipeline(Readable.from(['ab', 'cd']), upper, sink)
  .then(() => console.log(out.join('-')));""",
       "a pipeline of a source, a transform and a sink"),
    _b(r"""const fsp = require('node:fs/promises');
const os = require('node:os');

async function main() {
  const dir = await fsp.mkdtemp(`${os.tmpdir()}/cc-`);
  const file = `${dir}/log.txt`;
  await fsp.writeFile(file, 'one\n');
  await fsp.appendFile(file, 'two\n');
  const text = await fsp.readFile(file, 'utf8');
  console.log(text.trim().split('\n'), (await fsp.stat(file)).size);
  await fsp.rm(dir, { recursive: true });
}
main();""",
       "fs/promises: write, append, read and measure"),
    _b(r"""const http = require('node:http');

const server = http.createServer((req, res) => {
  if (req.url !== '/hello') return res.writeHead(404).end('nope');
  res.end(JSON.stringify({ msg: 'hi', method: req.method }));
});
server.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${server.address().port}`;
  const ok = await (await fetch(`${base}/hello`)).json();
  const missing = await fetch(`${base}/other`);
  console.log(ok, missing.status, await missing.text());
  server.close();
});""",
       "a server that answers its own fetch"),
)
