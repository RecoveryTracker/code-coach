"""TypeScript answers for the two-part puzzles.

Each is the JavaScript answer with the types the Dart answer already
declares - so a puzzle's TypeScript and Dart signatures always agree - plus
the few annotations `tsc --strict` asks for inside the body (an empty object
used as a lookup table needs a Record type). tests/test_puzzles_ts.py runs
every one through the TypeScript driver against the puzzle's cases.
"""

from __future__ import annotations

#: Puzzle id -> (part one, part two).
TS: dict[str, tuple[str, str]] = {
    'pz-night-shift': (
        'function partOne(log: string[]): number {\n  let inside = 0;\n  for (const line of log) {\n    const [kind, count] = line.split(" ");\n    inside += kind === "IN" ? Number(count) : -Number(count);\n  }\n  return inside;\n}\n',
        'function partTwo(log: string[]): number {\n  let inside = 0;\n  let most = 0;\n  for (const line of log) {\n    const [kind, count] = line.split(" ");\n    inside += kind === "IN" ? Number(count) : -Number(count);\n    most = Math.max(most, inside);\n  }\n  return most;\n}\n',
    ),
    'pz-sorting-station': (
        'function partOne(parcels: string[]): number {\n  return parcels.filter((p) => Number(p.slice(1)) > 10).length;\n}\n',
        'function partTwo(parcels: string[]): string {\n  const totals: Record<string, number> = {};\n  for (const p of parcels) {\n    totals[p[0]] = (totals[p[0]] || 0) + Number(p.slice(1));\n  }\n  let best = "";\n  for (const zone of Object.keys(totals).sort()) {\n    if (best === "" || totals[zone] > totals[best]) best = zone;\n  }\n  return best;\n}\n',
    ),
    'pz-the-lift': (
        'function partOne(moves: string[]): number {\n  let floor = 0;\n  for (const move of moves) {\n    const amount = Number(move.slice(1));\n    floor += move[0] === "U" ? amount : -amount;\n  }\n  return floor;\n}\n',
        'function partTwo(moves: string[]): number {\n  let floor = 0;\n  for (let i = 0; i < moves.length; i++) {\n    const amount = Number(moves[i].slice(1));\n    floor += moves[i][0] === "U" ? amount : -amount;\n    if (floor < 0) return i + 1;\n  }\n  return 0;\n}\n',
    ),
    'pz-class-vote': (
        'function partOne(votes: string[]): number {\n  const counts = new Map();\n  for (const name of votes) counts.set(name, (counts.get(name) || 0) + 1);\n  return counts.size ? Math.max(...counts.values()) : 0;\n}\n',
        'function partTwo(votes: string[]): string {\n  const counts = new Map();\n  for (const name of votes) counts.set(name, (counts.get(name) || 0) + 1);\n  const most = counts.size ? Math.max(...counts.values()) : 0;\n  const seen = new Map();\n  for (const name of votes) {\n    seen.set(name, (seen.get(name) || 0) + 1);\n    if (seen.get(name) === most) return name;\n  }\n  return "";\n}\n',
    ),
    'pz-password-rules': (
        'function partOne(passwords: string[]): number {\n  return passwords.filter((p) => p.length >= 8 && /\\d/.test(p)).length;\n}\n',
        'function partTwo(passwords: string[]): number {\n  return passwords.filter(\n    (p) => p.length >= 8 && /\\d/.test(p) && !/(.)\\1\\1/.test(p),\n  ).length;\n}\n',
    ),
    'pz-garden-grid': (
        'function partOne(grid: string[]): number {\n  let count = 0;\n  for (const row of grid) {\n    for (const cell of row) if (cell === "#") count++;\n  }\n  return count;\n}\n',
        'function partTwo(grid: string[]): number {\n  const steps = [[1, 0], [-1, 0], [0, 1], [0, -1]];\n  let count = 0;\n  for (let r = 0; r < grid.length; r++) {\n    for (let c = 0; c < grid[r].length; c++) {\n      if (grid[r][c] !== "#") continue;\n      const shaded = steps.some(([dr, dc]) => {\n        const rr = r + dr;\n        const cc = c + dc;\n        return rr >= 0 && rr < grid.length && cc >= 0\n          && cc < grid[rr].length && grid[rr][cc] === "#";\n      });\n      if (shaded) count++;\n    }\n  }\n  return count;\n}\n',
    ),
    'pz-brackets': (
        'function partOne(text: string): boolean {\n  const pairs: Record<string, string> = { ")": "(", "]": "[", "}": "{" };\n  const stack: string[] = [];\n  for (const ch of text) {\n    if ("([{".includes(ch)) stack.push(ch);\n    else if (stack.length === 0 || stack.pop() !== pairs[ch]) return false;\n  }\n  return stack.length === 0;\n}\n',
        'function partTwo(text: string): string {\n  const pairs: Record<string, string> = { ")": "(", "]": "[", "}": "{" };\n  const stack: string[] = [];\n  for (const ch of text) {\n    if ("([{".includes(ch)) stack.push(ch);\n    else if (stack.length === 0 || stack.pop() !== pairs[ch]) return ch;\n  }\n  return "";\n}\n',
    ),
    'pz-seat-map': (
        'function partOne(rows: string[]): number {\n  let free = 0;\n  for (const row of rows) {\n    for (const seat of row) if (seat === ".") free++;\n  }\n  return free;\n}\n',
        'function partTwo(rows: string[]): number {\n  let total = 0;\n  for (const row of rows) {\n    for (let i = 0; i < row.length; i++) {\n      const left = i > 0 ? row[i - 1] : ".";\n      const right = i + 1 < row.length ? row[i + 1] : ".";\n      if (row[i] === "." && left === "." && right === ".") total++;\n    }\n  }\n  return total;\n}\n',
    ),
    'pz-traffic-light': (
        'function partOne(log: string[]): number {\n  return log.filter((colour) => colour === "green").length;\n}\n',
        'function partTwo(log: string[]): number {\n  let best = 0;\n  let run = 0;\n  for (let i = 0; i < log.length; i++) {\n    run = i > 0 && log[i - 1] === log[i] ? run + 1 : 1;\n    best = Math.max(best, run);\n  }\n  return best;\n}\n',
    ),
    'pz-last-bus': (
        'function minutes(clock: string): number {\n  const [h, m] = clock.split(":");\n  return Number(h) * 60 + Number(m);\n}\n\nfunction partOne(departures: string[], now: string): number {\n  const later = departures\n    .map((d) => minutes(d) - minutes(now))\n    .filter((wait) => wait >= 0);\n  return later.length ? Math.min(...later) : -1;\n}\n',
        'function minutes(clock: string): number {\n  const [h, m] = clock.split(":");\n  return Number(h) * 60 + Number(m);\n}\n\nfunction partTwo(departures: string[], now: string): number {\n  if (!departures.length) return -1;\n  const day = 24 * 60;\n  return Math.min(\n    ...departures.map((d) => (((minutes(d) - minutes(now)) % day) + day) % day),\n  );\n}\n',
    ),
    'pz-word-chain': (
        'function partOne(words: string[]): boolean {\n  for (let i = 1; i < words.length; i++) {\n    const before = words[i - 1];\n    if (before[before.length - 1] !== words[i][0]) return false;\n  }\n  return true;\n}\n',
        'function partTwo(words: string[]): number {\n  if (!words.length) return 0;\n  let best = 1;\n  let run = 1;\n  for (let i = 1; i < words.length; i++) {\n    const before = words[i - 1];\n    run = before[before.length - 1] === words[i][0] ? run + 1 : 1;\n    best = Math.max(best, run);\n  }\n  return best;\n}\n',
    ),
    'pz-meeting-rooms': (
        'function partOne(meetings: string[]): number {\n  let total = 0;\n  for (const slot of meetings) {\n    const [start, end] = slot.split("-").map(Number);\n    total += end - start;\n  }\n  return total;\n}\n',
        'function partTwo(meetings: string[]): number {\n  const slots = meetings.map((slot) => slot.split("-").map(Number));\n  let most = 0;\n  for (let hour = 0; hour < 24; hour++) {\n    let busy = 0;\n    for (const [start, end] of slots) if (start <= hour && hour < end) busy++;\n    most = Math.max(most, busy);\n  }\n  return most;\n}\n',
    ),
    'pz-walking-robot': (
        'function partOne(commands: string): number {\n  const steps = [[0, 1], [1, 0], [0, -1], [-1, 0]];\n  let x = 0, y = 0, facing = 0;\n  for (const c of commands) {\n    if (c === "R") facing = (facing + 1) % 4;\n    else if (c === "L") facing = (facing + 3) % 4;\n    else {\n      x += steps[facing][0];\n      y += steps[facing][1];\n    }\n  }\n  return Math.abs(x) + Math.abs(y);\n}\n',
        'function partTwo(commands: string): number {\n  const steps = [[0, 1], [1, 0], [0, -1], [-1, 0]];\n  let x = 0, y = 0, facing = 0;\n  const seen = new Set(["0,0"]);\n  for (const c of commands) {\n    if (c === "R") facing = (facing + 1) % 4;\n    else if (c === "L") facing = (facing + 3) % 4;\n    else {\n      x += steps[facing][0];\n      y += steps[facing][1];\n      const key = x + "," + y;\n      if (seen.has(key)) return Math.abs(x) + Math.abs(y);\n      seen.add(key);\n    }\n  }\n  return -1;\n}\n',
    ),
    'pz-shopping-list': (
        'function partOne(lines: string[]): number {\n  let total = 0;\n  for (const line of lines) {\n    const [, count] = line.split(" x");\n    total += Number(count);\n  }\n  return total;\n}\n',
        'function partTwo(lines: string[]): string[] {\n  const totals = new Map();\n  for (const line of lines) {\n    const [name, count] = line.split(" x");\n    totals.set(name, (totals.get(name) || 0) + Number(count));\n  }\n  return [...totals.keys()].sort().map((name) => `${name} x${totals.get(name)}`);\n}\n',
    ),
    'pz-warming-up': (
        'function partOne(readings: number[]): number {\n  let best = 0;\n  for (let i = 1; i < readings.length; i++) {\n    best = Math.max(best, readings[i] - readings[i - 1]);\n  }\n  return best;\n}\n',
        'function partTwo(readings: number[]): number {\n  let best = 0;\n  let run = 0;\n  for (let i = 0; i < readings.length; i++) {\n    run = i > 0 && readings[i - 1] < readings[i] ? run + 1 : 1;\n    best = Math.max(best, run);\n  }\n  return best;\n}\n',
    ),
    'pz-step-counter': (
        'function partOne(days: number[]): number {\n  return days.reduce((a, b) => a + b, 0);\n}\n',
        'function partTwo(days: number[]): number {\n  let stars = 0;\n  for (let i = 1; i < days.length; i++) {\n    if (days[i] > days[i - 1]) stars++;\n  }\n  return stars;\n}\n',
    ),
    'pz-car-park': (
        'function partOne(log: string[]): number {\n  return log.filter((e) => e === "in").length;\n}\n',
        'function partTwo(log: string[]): number {\n  let now = 0;\n  let best = 0;\n  for (const e of log) {\n    now += e === "in" ? 1 : -1;\n    best = Math.max(best, now);\n  }\n  return best;\n}\n',
    ),
    'pz-temperatures': (
        'function partOne(readings: number[]): number {\n  return Math.max(...readings);\n}\n',
        'function partTwo(readings: number[]): number {\n  let best = 0;\n  for (let i = 1; i < readings.length; i++) {\n    best = Math.max(best, readings[i] - readings[i - 1]);\n  }\n  return best;\n}\n',
    ),
    'pz-receipts': (
        'function partOne(lines: string[]): number {\n  return lines.reduce((sum, line) => sum + Number(line.split(":")[1]), 0);\n}\n',
        'function partTwo(lines: string[]): string {\n  let bestName = "";\n  let best = -1;\n  for (const line of lines) {\n    const [name, price] = line.split(":");\n    if (Number(price) > best) {\n      bestName = name;\n      best = Number(price);\n    }\n  }\n  return bestName;\n}\n',
    ),
    'pz-digit-string': (
        'function partOne(text: string): number {\n  return [...text].reduce((sum, ch) => sum + Number(ch), 0);\n}\n',
        'function partTwo(text: string): number {\n  let total = 0;\n  for (let i = 1; i < text.length; i++) {\n    if (text[i] > text[i - 1]) total += Number(text[i]);\n  }\n  return total;\n}\n',
    ),
    'pz-stock-room': (
        'function partOne(log: string[]): number {\n  let total = 0;\n  for (const line of log) {\n    const [verb, , count] = line.split(" ");\n    total += verb === "add" ? Number(count) : -Number(count);\n  }\n  return total;\n}\n',
        'function partTwo(log: string[]): string[] {\n  const stock: Record<string, number> = {};\n  for (const line of log) {\n    const [verb, name, count] = line.split(" ");\n    const change = verb === "add" ? Number(count) : -Number(count);\n    stock[name] = (stock[name] ?? 0) + change;\n  }\n  return Object.keys(stock).filter((name) => stock[name] > 0).sort();\n}\n',
    ),
}
