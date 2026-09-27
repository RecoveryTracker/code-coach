"""Still more JavaScript to type: everyday lines and small whole functions.

`snippets.JAVASCRIPT_CODE` and `snippets_more.JAVASCRIPT_MORE` cover the
first shapes - destructuring, a fetch, find and some, a lookup built with
fromEntries. These are the next layer: the lines that fill a real file
once the data is an array of objects, the strings come from users, and
the network can fail. No DOM, so every line here means the same thing in
Node and in a browser.

The lines follow the same two rules as `snippets_more`: something a person
would really write, and a note that says what it is for.

The blocks are complete little functions, each followed by a call so the
block runs on its own. Every one is executed by the tests, so what you are
typing is known to work rather than known to look right. Two-space
indentation, matching the JavaScript blocks the curriculum already serves.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

JAVASCRIPT_LINES_MORE: tuple[Passage, ...] = (
    # Arrays of objects
    _s("const admin = users.find((u) => u.role === 'admin');",
       "the first admin, or undefined if there is none"),
    _s("const hasOverdue = invoices.some((inv) => inv.dueDate < today);",
       "is anything past its due date"),
    _s("const allPaid = orders.every((o) => o.status === 'paid');",
       "true only when every order is paid"),
    _s("const byRole = users.reduce((acc, u) => ({ ...acc, [u.role]: u }), {});",
       "an object keyed by each user's role"),
    _s("const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);",
       "the cart total, price times quantity"),
    _s("const names = users.map((u) => u.name).sort((a, b) => a.localeCompare(b));",
       "just the names, in alphabetical order"),
    _s("const tags = posts.flatMap((post) => post.tags ?? []);",
       "every tag from every post in one flat list"),
    _s("const emails = users.filter((u) => u.active).map((u) => u.email);",
       "the email of each active user"),
    _s("const newest = [...posts].sort((a, b) => b.createdAt - a.createdAt);",
       "newest first, without reordering the original"),
    _s("const cheapest = products.reduce((min, p) => (p.price < min.price ? p : min));",
       "the lowest-priced product"),
    _s("const ids = new Set(selected.map((item) => item.id));",
       "the chosen ids, ready for fast lookups"),
    _s("const remaining = todos.filter((t) => !ids.has(t.id));",
       "everything except the chosen ones"),
    _s("const last = items.at(-1);", "the last item, no length minus one"),
    _s("for (const w of words) counts[w] = (counts[w] ?? 0) + 1;",
       "tally how often each word appears"),
    _s("const byCity = Object.groupBy(people, (p) => p.city);",
       "bucket people by city (newer runtimes)"),
    _s("const pairs = keys.map((key, i) => [key, values[i]]);",
       "zip two arrays into pairs"),
    _s("const top3 = [...scores].sort((a, b) => b - a).slice(0, 3);",
       "the three highest scores"),
    _s("if (!list.includes(value)) list.push(value);",
       "add it only if it is not there yet"),
    _s("const unique = [...new Map(users.map((u) => [u.id, u])).values()];",
       "de-duplicate objects by their id"),
    _s("const range = Array.from({ length: n }, (_, i) => i + 1);",
       "the numbers one to n"),

    # Strings
    _s("if (email.includes('@')) {", "a rough check that it looks like an email"),
    _s("const isSecure = url.startsWith('https://');",
       "does the address use https"),
    _s("if (file.name.endsWith('.json')) {", "only the JSON files"),
    _s("const mm = String(minutes).padStart(2, '0');", "5 becomes 05"),
    _s("const clean = text.replaceAll('\\t', '  ');", "tabs into two spaces"),
    _s("const words = sentence.trim().split(/\\s+/);",
       "split on any run of whitespace"),
    _s("const csvLine = row.map(String).join(',');", "one row as a CSV line"),
    _s("const price = `$${amount.toFixed(2)}`;", "money with two decimals"),
    _s("const percent = `${((done / total) * 100).toFixed(1)}%`;",
       "progress as a percentage"),
    _s("const initials = name.split(' ').map((part) => part[0]).join('');",
       "Ada Lovelace becomes AL"),
    _s("const capitalized = word.charAt(0).toUpperCase() + word.slice(1);",
       "capitalise the first letter"),
    _s("const row = `${name.padEnd(12)}${String(score).padStart(5)}`;",
       "a table row in fixed-width columns"),
    _s("const short = text.length > 40 ? `${text.slice(0, 37)}...` : text;",
       "cut long text off with an ellipsis"),
    _s("const lines = input.split('\\n').filter(Boolean);",
       "the non-empty lines of some input"),

    # Objects
    _s("const settings = { ...defaults, ...saved, theme: 'dark' };",
       "layer the saved settings, then force one field"),
    _s("const copy = structuredClone(state);", "a deep copy, nested objects too"),
    _s("const highest = Math.max(...Object.values(scores));",
       "the biggest value in an object"),
    _s("const doubled = Object.fromEntries(entries.map(([k, v]) => [k, v * 2]));",
       "change every value, keep the keys"),
    _s("const city = user.address?.city ?? 'Unknown';",
       "a nested field with a fallback"),
    _s("const port = Number(process.env.PORT ?? 3000);",
       "config from the environment, with a default"),
    _s("const isEmpty = Object.keys(obj).length === 0;",
       "does the object have no own properties"),
    _s("const updated = { ...todo, done: !todo.done };",
       "flip one field in a new object"),
    _s("const next = items.map((it) => (it.id === id ? { ...it, qty: it.qty + 1 } : it));",
       "update one item without mutating the list"),
    _s("const seenCount = counts.get(key) ?? 0;", "read a Map with a default"),
    _s("user.settings ??= {};", "create it only if it is missing"),
    _s("handlers[event.type]?.(event);", "call the handler only if there is one"),
    _s("delete draft.tempId;", "remove a property from an object"),

    # Async
    _s("const res = await fetch(`/api/users/${id}`);", "request one user by id"),
    _s("const users = await (await fetch('/api/users')).json();",
       "fetch and parse in one line"),
    _s("const results = await Promise.allSettled(tasks);",
       "wait for all of them, failures included"),
    _s("const winner = await Promise.race([request, timeout(5000)]);",
       "whichever finishes first"),
    _s("const body = JSON.stringify({ name, email });",
       "an object into request text"),
    _s("const reply = await fetch(url, { method: 'POST', headers, body });",
       "send data to a server"),
    _s("for (const url of urls) results.push(await fetch(url));",
       "one request at a time, in order"),
    _s("const pages = await Promise.all(ids.map((id) => getPage(id)));",
       "every page at once, results in order"),
    _s("console.error('Load failed:', err.message);", "log what went wrong"),
    _s("setTimeout(() => controller.abort(), 5000);",
       "give up on the request after five seconds"),
    _s("const config = JSON.parse(await readFile('config.json', 'utf8'));",
       "read a JSON file and parse it"),
    _s("if (err.name === 'AbortError') return null;",
       "a cancelled request is not a failure"),

    # Small regexes
    _s("const isEmail = /^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(input);",
       "a reasonable email check"),
    _s("const digits = phone.replace(/\\D/g, '');", "keep only the digits"),
    _s("const found = text.match(/\\w+/g) ?? [];", "every word, or an empty list"),
    _s("const [, year, month] = date.match(/(\\d{4})-(\\d{2})/);",
       "pull the parts out with groups"),
    _s("const snake = name.replace(/([A-Z])/g, '_$1').toLowerCase();",
       "camelCase into snake_case"),
    _s("const collapsed = text.replace(/\\s+/g, ' ').trim();",
       "squeeze runs of whitespace to one space"),
    _s("if (/^\\d+$/.test(value)) {", "only when it is all digits"),

    # Numbers and dates
    _s("const clamp = (n, lo, hi) => Math.min(Math.max(n, lo), hi);",
       "keep a number inside its bounds"),
    _s("const today = new Date().toISOString().slice(0, 10);",
       "today as YYYY-MM-DD"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"JavaScript · {note}")


JAVASCRIPT_BLOCKS_MORE: tuple[Passage, ...] = (
    _b("function debounce(fn, wait) {\n"
       "  let timer;\n"
       "  return (...args) => {\n"
       "    clearTimeout(timer);\n"
       "    timer = setTimeout(() => fn(...args), wait);\n"
       "  };\n"
       "}\n"
       "\n"
       "const save = debounce((text) => console.log('saved', text), 50);\n"
       "save('a');\n"
       "save('ab');",
       "debounce: only the last call in a burst runs"),
    _b("function groupBy(items, key) {\n"
       "  const groups = {};\n"
       "  for (const item of items) {\n"
       "    (groups[item[key]] ??= []).push(item);\n"
       "  }\n"
       "  return groups;\n"
       "}\n"
       "\n"
       "console.log(groupBy([{ t: 'a' }, { t: 'b' }, { t: 'a' }], 't'));",
       "group an array of objects by one field"),
    _b("function tally(words) {\n"
       "  const counts = new Map();\n"
       "  for (const word of words) {\n"
       "    counts.set(word, (counts.get(word) ?? 0) + 1);\n"
       "  }\n"
       "  return counts;\n"
       "}\n"
       "\n"
       "console.log(tally(['red', 'blue', 'red']));",
       "count how often each value appears"),
    _b("async function getJson(url) {\n"
       "  try {\n"
       "    const res = await fetch(url);\n"
       "    if (!res.ok) throw new Error(`HTTP ${res.status}`);\n"
       "    return await res.json();\n"
       "  } catch (err) {\n"
       "    console.error(`Failed to load ${url}:`, err.message);\n"
       "    return null;\n"
       "  }\n"
       "}",
       "fetch JSON, and return null instead of throwing"),
    _b("class Cart {\n"
       "  items = [];\n"
       "\n"
       "  add(name, price) {\n"
       "    this.items.push({ name, price });\n"
       "  }\n"
       "\n"
       "  get total() {\n"
       "    return this.items.reduce((sum, item) => sum + item.price, 0);\n"
       "  }\n"
       "}\n"
       "\n"
       "const cart = new Cart();\n"
       "cart.add('pen', 2);\n"
       "console.log(cart.total);",
       "a class whose total is a getter"),
    _b("function byLastThenFirst(people) {\n"
       "  return [...people].sort(\n"
       "    (a, b) => a.last.localeCompare(b.last) || a.first.localeCompare(b.first),\n"
       "  );\n"
       "}\n"
       "\n"
       "console.log(byLastThenFirst([{ first: 'B', last: 'X' }, { first: 'A', last: 'X' }]));",
       "sort a copy by two fields"),
    _b("class Emitter {\n"
       "  #handlers = {};\n"
       "\n"
       "  on(event, fn) {\n"
       "    (this.#handlers[event] ??= []).push(fn);\n"
       "  }\n"
       "\n"
       "  emit(event, ...args) {\n"
       "    for (const fn of this.#handlers[event] ?? []) fn(...args);\n"
       "  }\n"
       "}\n"
       "\n"
       "const bus = new Emitter();\n"
       "bus.on('ping', (n) => console.log('pong', n));\n"
       "bus.emit('ping', 1);",
       "a tiny event emitter"),
    _b("function chunk(items, size) {\n"
       "  const out = [];\n"
       "  for (let i = 0; i < items.length; i += size) {\n"
       "    out.push(items.slice(i, i + size));\n"
       "  }\n"
       "  return out;\n"
       "}\n"
       "\n"
       "console.log(chunk([1, 2, 3, 4, 5], 2));",
       "split an array into groups of a fixed size"),
    _b("function memoize(fn) {\n"
       "  const cache = new Map();\n"
       "  return (n) => {\n"
       "    if (!cache.has(n)) cache.set(n, fn(n));\n"
       "    return cache.get(n);\n"
       "  };\n"
       "}\n"
       "\n"
       "const square = memoize((n) => n * n);\n"
       "console.log(square(9), square(9));",
       "memoize: work each answer out once"),
    _b("function parseQuery(query) {\n"
       "  const result = {};\n"
       "  for (const pair of query.replace(/^\\?/, '').split('&')) {\n"
       "    if (!pair) continue;\n"
       "    const [key, value = ''] = pair.split('=');\n"
       "    result[decodeURIComponent(key)] = decodeURIComponent(value);\n"
       "  }\n"
       "  return result;\n"
       "}\n"
       "\n"
       "console.log(parseQuery('?page=2&sort=name'));",
       "a query string into an object"),
    _b("function formatMoney(cents) {\n"
       "  const sign = cents < 0 ? '-' : '';\n"
       "  const dollars = Math.floor(Math.abs(cents) / 100);\n"
       "  const rest = String(Math.abs(cents) % 100).padStart(2, '0');\n"
       "  return `${sign}$${dollars.toLocaleString('en-US')}.${rest}`;\n"
       "}\n"
       "\n"
       "console.log(formatMoney(123456));",
       "whole cents into a dollar string"),
    _b("async function retry(task, attempts = 3) {\n"
       "  for (let i = 1; i <= attempts; i++) {\n"
       "    try {\n"
       "      return await task();\n"
       "    } catch (err) {\n"
       "      if (i === attempts) throw err;\n"
       "    }\n"
       "  }\n"
       "}\n"
       "\n"
       "retry(async () => 'done').then(console.log);",
       "try an async task again before giving up"),
    _b("function pick(obj, keys) {\n"
       "  return Object.fromEntries(\n"
       "    keys.filter((key) => key in obj).map((key) => [key, obj[key]]),\n"
       "  );\n"
       "}\n"
       "\n"
       "console.log(pick({ a: 1, b: 2, c: 3 }, ['a', 'c']));",
       "copy only the fields you name"),
    _b("function withTimeout(promise, ms) {\n"
       "  const timeout = new Promise((_, reject) => {\n"
       "    setTimeout(() => reject(new Error('timed out')), ms);\n"
       "  });\n"
       "  return Promise.race([promise, timeout]);\n"
       "}\n"
       "\n"
       "withTimeout(Promise.resolve('fast'), 100).then(console.log);",
       "give a promise a deadline"),
    _b("function get(obj, path, fallback) {\n"
       "  const value = path.split('.').reduce((acc, key) => acc?.[key], obj);\n"
       "  return value ?? fallback;\n"
       "}\n"
       "\n"
       "console.log(get({ a: { b: { c: 1 } } }, 'a.b.c'));\n"
       "console.log(get({}, 'a.b', 'none'));",
       "read a nested field by a dotted path"),
    _b("function uniqueBy(items, key) {\n"
       "  const seen = new Set();\n"
       "  return items.filter((item) => {\n"
       "    if (seen.has(item[key])) return false;\n"
       "    seen.add(item[key]);\n"
       "    return true;\n"
       "  });\n"
       "}\n"
       "\n"
       "console.log(uniqueBy([{ id: 1 }, { id: 1 }, { id: 2 }], 'id'));",
       "keep the first object for each key"),
    _b("function slugify(title) {\n"
       "  return title\n"
       "    .toLowerCase()\n"
       "    .trim()\n"
       "    .replace(/[^a-z0-9]+/g, '-')\n"
       "    .replace(/^-|-$/g, '');\n"
       "}\n"
       "\n"
       "console.log(slugify('  Hello, World!  '));",
       "a title into a URL slug"),
)
