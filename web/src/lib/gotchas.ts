/**
 * Gotchas, the parts that are rules rather than pixels: the streak, which key picks which
 * option, what the deck line says, which cards were just seen (so the server does not repeat
 * one), and how an error from the server reads. Pure TypeScript, so
 * tests/test_gotchas_ts.py can run it in node.
 *
 * The server is the authority for what is right, what was seen and the best streak; the client
 * only keeps the running streak itself so the counter moves the instant an answer comes back.
 */

export type GotchaLang = "python" | "javascript";

export const GOTCHA_LANGS: readonly GotchaLang[] = ["python", "javascript"];

export const LANG_LABEL: Record<GotchaLang, string> = { python: "Python", javascript: "JavaScript" };

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
