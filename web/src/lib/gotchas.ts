/**
 * Gotchas, the parts that are rules rather than pixels: the streak, which key picks which
 * option, what the deck line says, which cards were just seen (so the server does not repeat
 * one), and how an error from the server reads. Pure TypeScript, so
 * tests/test_gotchas_ts.py can run it in node.
 *
 * The server is the authority for what is right, what was seen and the best streak; the client
 * only keeps the running streak itself so the counter moves the instant an answer comes back.
 */

import type { Syntax } from "./codeColors";

/** A language id from the server's registry ("python", "rust", "csharp"...). */
export type GotchaLang = string;

/** One language on offer: what the switch shows. The server sends these, in display order. */
export interface LangInfo {
  id: string;
  name: string;
  /** Cards in its deck, built in plus yours. */
  count: number;
  /** "Rust Quiz". */
  title: string;
}

/** How many languages get a button of their own; the rest are in the More menu. */
export const QUICK_LANGS = 4;

const FALLBACK: LangInfo[] = [
  { id: "python", name: "Python", count: 0, title: "Python Quiz" },
  { id: "javascript", name: "JavaScript", count: 0, title: "JavaScript Quiz" },
];

/**
 * The languages to offer, from what the server says it can run (`languages` in /api/gotchas): a language
 * whose toolchain is missing, or that has no cards yet, is not in the list. A server that says nothing
 * (an older one) offers Python and JavaScript; entries that are not language objects are ignored; a
 * repeated id counts once. The server's order (the registry's) is kept.
 */
export function offeredLanguages(available: readonly unknown[] | null | undefined): LangInfo[] {
  if (!Array.isArray(available)) return FALLBACK;
  const seen = new Set<string>();
  const out: LangInfo[] = [];
  for (const raw of available) {
    const l = raw as Partial<LangInfo> | null;
    if (!l || typeof l !== "object" || typeof l.id !== "string" || l.id === "" || seen.has(l.id)) continue;
    seen.add(l.id);
    const name = typeof l.name === "string" && l.name !== "" ? l.name : l.id;
    out.push({
      id: l.id,
      name,
      count: typeof l.count === "number" ? l.count : 0,
      title: typeof l.title === "string" && l.title !== "" ? l.title : `${name} Quiz`,
    });
  }
  return out.length > 0 ? out : FALLBACK.slice(0, 1);
}

/** The remembered language if it is on offer, else Python (a saved "c" on a machine with no compiler), else the first. */
export function chooseLanguage(saved: string | null | undefined, offered: readonly LangInfo[]): GotchaLang {
  const found = offered.find((l) => l.id === saved);
  return found?.id ?? offered.find((l) => l.id === "python")?.id ?? offered[0]?.id ?? "python";
}

/** The last-used languages, newest first, each once, at most `max` (default: the quick buttons). */
export function pushRecent(recent: readonly string[], id: string, max = QUICK_LANGS): string[] {
  return [id, ...recent.filter((r) => r !== id)].slice(0, Math.max(1, max));
}

/**
 * The languages that get their own button: the one on screen, then the last-used ones, topped up with the
 * first on offer (Python, JavaScript, ... in the registry's order) until there are `max`. They are shown in
 * the registry's order, so a button never jumps about when you switch.
 */
export function quickLanguages(
  offered: readonly LangInfo[],
  recent: readonly string[],
  current: string,
  max = QUICK_LANGS,
): LangInfo[] {
  const ids = new Set(offered.map((l) => l.id));
  const chosen: string[] = [];
  const take = (id: string) => {
    if (ids.has(id) && !chosen.includes(id) && chosen.length < max) chosen.push(id);
  };
  take(current);
  recent.forEach(take);
  offered.forEach((l) => take(l.id));
  return offered.filter((l) => chosen.includes(l.id));
}

/** The menu's list for what was typed: a name or id that starts with it first, then any that contains it. */
export function filterLanguages(offered: readonly LangInfo[], query: string): LangInfo[] {
  const q = query.trim().toLowerCase();
  if (q === "") return [...offered];
  const rank = (l: LangInfo): number => {
    const name = l.name.toLowerCase();
    const id = l.id.toLowerCase();
    if (name.startsWith(q) || id.startsWith(q)) return 0;
    if (name.includes(q) || id.includes(q)) return 1;
    return 2;
  };
  return offered
    .map((l, i) => ({ l, i, r: rank(l) }))
    .filter((x) => x.r < 2)
    .sort((a, b) => a.r - b.r || a.i - b.i)
    .map((x) => x.l);
}

/** The active item of a menu of `count` after a navigation key, wrapping; -1 means nothing is active yet. */
export function moveActive(active: number, key: string, count: number): number {
  if (count <= 0) return -1;
  if (key === "ArrowDown") return active < 0 ? 0 : (active + 1) % count;
  if (key === "ArrowUp") return active < 0 ? count - 1 : (active - 1 + count) % count;
  if (key === "Home") return 0;
  if (key === "End") return count - 1;
  return active;
}

function hash(text: string): number {
  let h = 2166136261;
  for (let i = 0; i < text.length; i++) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/** The salt the hash is seeded with: picked so the languages in the registry land at least 7 degrees apart. */
const HUE_SALT = "3828:";

/** A language's stable hue, 0-359, from its id alone. */
export function hueOf(id: string): number {
  return hash(HUE_SALT + id) % 360;
}

const ACCENT_FIXED: Record<string, string> = { python: "#7cc4ff", javascript: "#ffd166", c: "#5eead4" };

/** HSL (h 0-359, s and l 0-1) as [r, g, b], each 0-255. */
export function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  const k = (n: number) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n: number) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  return [Math.round(255 * f(0)), Math.round(255 * f(8)), Math.round(255 * f(4))];
}

/** The saturation and lightness every derived accent uses: bright on the dark card at every hue (>= 4.5:1). */
export const ACCENT_S = 0.85;
export const ACCENT_L = 0.72;

/** A language's title colour as [r, g, b]: the first three keep theirs, the rest get a hue from their id. */
export function accentRgb(id: string): [number, number, number] {
  const fixed = ACCENT_FIXED[id];
  if (fixed) return [1, 3, 5].map((i) => parseInt(fixed.slice(i, i + 2), 16)) as [number, number, number];
  return hslToRgb(hueOf(id), ACCENT_S, ACCENT_L);
}

/** The inline style that gives a card its accent: `--gq-accent` and `--gq-accent-rgb`. */
export function accentStyle(id: string): Record<string, string> {
  const [r, g, b] = accentRgb(id);
  return { "--gq-accent": `rgb(${r}, ${g}, ${b})`, "--gq-accent-rgb": `${r}, ${g}, ${b}` };
}

/** What to tell someone adding a quiz in this language (a whole program, a main...). */
export function addHint(id: string): string {
  const hints: Record<string, string> = {
    c: " For C that means a whole program, with its #include lines and a main, that compiles and returns 0.",
    cpp: " For C++ that means a whole program with its #include lines and a main that compiles.",
    java: " For Java that means a class with a static main method.",
    csharp: " For C# top-level statements are enough, or a class with a Main.",
    go: " For Go that means package main with its imports and func main.",
    rust: " For Rust that means a program with fn main that compiles.",
    kotlin: " For Kotlin that means a file with fun main().",
    swift: " For Swift the statements are the program; it is compiled before it runs.",
    dart: " For Dart that means a program with void main().",
    zig: " For Zig that means pub fn main(), printing with std.debug.print.",
    odin: " For Odin that means package main and a main :: proc().",
    php: " For PHP start the file with <?php.",
    lisp: " For Common Lisp print with (format t ...).",
    sql: " For SQL the statements run on a fresh in-memory SQLite database; end with one SELECT, and its rows print as a|b; c|d.",
    typescript: " For TypeScript the types are checked first (strict), then it runs on node.",
  };
  return hints[id] ?? "";
}

/** A short label for one of your own cards: its first line of code that says something (not an #include or main). */
export function codeLabel(code: string, max = 70): string {
  const lines = code.replace(/\r\n/g, "\n").split("\n");
  const boilerplate = /^\s*(#include\b|int\s+main\s*\(|package\s+\w+\s*$|import\s|using\s|use\s|<\?php|public\s+class\b)/;
  const real = lines.find((l) => l.trim() !== "" && !boilerplate.test(l));
  return (real ?? lines[0] ?? "").trim().slice(0, max);
}

export type DotState = "todo" | "right" | "wrong";

export interface GotchaDaily {
  day: string;
  total: number;
  done: number;
  complete: boolean;
  dots: DotState[];
}

export interface GotchaSummary {
  language: GotchaLang;
  total: number;
  seen: number;
  right: number;
  mine: number;
  streak: number;
  streak_best: number;
  daily: GotchaDaily;
  title?: string;
  /** The languages on offer on this machine, in display order; absent on an older server. */
  languages?: LangInfo[];
  /** Every language's colouring rules (only /api/gotchas sends them). */
  syntax?: Record<string, Syntax>;
}

/** A card as sent before answering: no answer, no trap, no explanation. */
export interface GotchaCard {
  id: string;
  language: GotchaLang;
  code: string;
  options: string[];
  mine: boolean;
  why_picked: "new" | "again" | "review" | "yours" | "daily";
  title: string;
  summary: GotchaSummary;
  languages?: LangInfo[];
}

export interface GotchaAnswer {
  correct: boolean;
  answer: string;
  answer_index: number;
  chosen: number;
  trap: string;
  why: string;
  mine: boolean;
  streak: number;
  streak_best: number;
  again_soon: boolean;
  daily: GotchaDaily & { just_completed: boolean };
  summary: GotchaSummary;
}

export interface GotchaRun {
  stdout: string;
  error: string;
  seconds: number;
  timed_out: boolean;
  /** A compiled language: the program did not build, and `error` is the compiler's words. */
  compile_error?: boolean;
}

export interface GotchaUserCard {
  id: string;
  language: GotchaLang;
  code: string;
  added: string;
  options: number;
  answer: string;
}

export interface GotchaUserResult {
  saved: boolean;
  id?: string;
  output: string;
  raises: boolean;
  matched: boolean | null;
  notes: string[];
  options: string[];
  answer: string;
  summary?: GotchaSummary;
}

// ── The streak ─────────────────────────────────────────────────────────

/** The running streak after an answer: one more when right, back to nothing when wrong. */
export function nextStreak(streak: number, correct: boolean): number {
  return correct ? Math.max(0, Math.floor(streak)) + 1 : 0;
}

/** What the counter says; nothing to say about no streak. */
export function streakLabel(streak: number): string {
  if (streak < 1) return "";
  return `${streak} in a row`;
}

/** How big a fuss to make: 0 none, 1 an ordinary right answer, 2 at 5, 3 at 10 and every 10 after. */
export function streakTier(streak: number): 0 | 1 | 2 | 3 {
  if (streak < 1) return 0;
  if (streak >= 10 && streak % 10 === 0) return 3;
  if (streak % 5 === 0) return 2;
  return 1;
}

// ── Keys ───────────────────────────────────────────────────────────────

/** 1-4 or A-D (either case) pick an option; anything else, or an option the card does not have, is -1. */
export function keyToIndex(key: string, count: number): number {
  if (key.length !== 1) return -1;
  const k = key.toLowerCase();
  let i = -1;
  if (k >= "1" && k <= "4") i = Number(k) - 1;
  else if (k >= "a" && k <= "d") i = k.charCodeAt(0) - 97;
  return i >= 0 && i < Math.min(count, 4) ? i : -1;
}

/** Enter, Space and the right arrow move on once a card is answered. */
export function isNextKey(key: string): boolean {
  return key === "Enter" || key === " " || key === "ArrowRight";
}

export function optionLetter(i: number): string {
  return "ABCD"[i] ?? String(i + 1);
}

export type OptionState = "idle" | "picked" | "right" | "wrong" | "reveal" | "dim";

/**
 * How one option button looks. Before an answer comes back only the picked one is marked; after it
 * the right one is green (`right` if you picked it, `reveal` if you did not), your wrong pick is
 * red, and the rest fade.
 */
export function optionState(i: number, chosen: number | null, answerIndex: number | null): OptionState {
  if (chosen === null) return "idle";
  if (answerIndex === null) return i === chosen ? "picked" : "idle";
  if (i === answerIndex) return i === chosen ? "right" : "reveal";
  if (i === chosen) return "wrong";
  return "dim";
}

// ── The deck and what was just seen ────────────────────────────────────

export function deckLine(seen: number, total: number, mine = 0): string {
  const base = `Deck: ${seen}/${total} seen`;
  return mine > 0 ? `${base} (${mine} yours)` : base;
}

/** The last few card ids, newest last, each once, at most `max` of them. */
export function recentIds(recent: readonly string[], id: string, max = 3): string[] {
  return [...recent.filter((r) => r !== id), id].slice(-Math.max(1, max));
}

export function excludeParam(recent: readonly string[]): string {
  return recent.join(",");
}

// ── The Daily 5 ────────────────────────────────────────────────────────

export function dailyLine(d: GotchaDaily): string {
  if (d.total === 0) return "Daily 5";
  return d.complete ? "Daily 5 - done today" : `Daily 5 - ${d.done} of ${d.total}`;
}

/** The Momentum key a finished day pays under: once a day per language. */
export function dailyAwardKey(language: GotchaLang, day: string): string {
  return `daily:${language}:${day}`;
}

export function cardAwardKey(language: GotchaLang, id: string): string {
  return `gotcha:${language}:${id}`;
}

// ── Reading what the server said ───────────────────────────────────────

/** A failed request's message: FastAPI's `{"detail": "..."}` when there is one, else the text. */
export function errorText(e: unknown): string {
  const raw = e instanceof Error ? e.message : String(e);
  try {
    const parsed = JSON.parse(raw) as { detail?: unknown };
    if (typeof parsed.detail === "string") return parsed.detail;
    if (Array.isArray(parsed.detail)) return "That did not look right; check the form and try again.";
  } catch {
    /* not JSON: plain text */
  }
  return raw || "Something went wrong.";
}

/** How many lines of code the form holds (a trailing newline is not a line), for the 60-line limit. */
export function lineCount(code: string): number {
  const text = code.replace(/\r\n/g, "\n").replace(/\n+$/, "");
  return text === "" ? 0 : text.split("\n").length;
}

export const MAX_LINES = 60;
