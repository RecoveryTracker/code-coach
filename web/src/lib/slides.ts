/**
 * Slides: the pure rules of a passive deck (no React, no DOM).
 *
 * Which slide comes next, how long autoplay stays on a slide, what a key does, how the chosen speed is
 * read back. tests/test_slides_ts.py bundles this file with esbuild and runs it in node.
 */

import type { Syntax } from "./codeColors";

export interface SlideDeckInfo {
  id: string;
  title: string;
  blurb: string;
  count: number;
}

export interface SlideList {
  language: string;
  decks: SlideDeckInfo[];
}

export interface SlideItem {
  title: string;
  text: string;
  code: string;
  output: string;
  point: string;
}

export interface SlideDeck {
  id: string;
  title: string;
  language: string;
  blurb: string;
  syntax: Syntax | null;
  slides: SlideItem[];
}

// ── Moving about ───────────────────────────────────────────────────────

/** The nearest real slide index (0 .. count-1); 0 when there are none. */
export function clampIndex(index: number, count: number): number {
  if (count <= 0 || !Number.isFinite(index)) return 0;
  return Math.min(count - 1, Math.max(0, Math.trunc(index)));
}

export function nextIndex(index: number, count: number): number {
  return clampIndex(index + 1, count);
}

export function prevIndex(index: number, count: number): number {
  return clampIndex(index - 1, count);
}

export function isLast(index: number, count: number): boolean {
  return count <= 0 || index >= count - 1;
}

/** Where autoplay goes after a slide: the next index, or null at the end (it stops there; it never loops). */
export function autoStep(index: number, count: number): number | null {
  return isLast(index, count) ? null : index + 1;
}

/** "slide 3 of 14" (index counts from 0). */
export function progressLabel(index: number, count: number): string {
  return `slide ${clampIndex(index, count) + 1} of ${count}`;
}

// ── Timing ─────────────────────────────────────────────────────────────

export const SPEEDS = [0.5, 0.75, 1, 1.5, 2] as const;
export const DEFAULT_SPEED = 1;
export const SPEED_KEY = "code-coach:slides-speed";

/** Milliseconds at 1x: a base, then time to read each word and to take in each line of code, plus the output. */
export const BASE_MS = 2500;
export const WORD_MS = 300;
export const CODE_LINE_MS = 700;
export const OUTPUT_MS = 1200;

/** How long the output waits after the code appears, at 1x. */
export const OUTPUT_DELAY_MS = 1000;

export function countWords(text: string): number {
  const found = text.trim().match(/\S+/g);
  return found ? found.length : 0;
}

export function countLines(code: string): number {
  return code.trim() === "" ? 0 : code.replace(/\n+$/, "").split("\n").length;
}

/** The speed to use for a stored value: one of SPEEDS, else 1x. */
export function parseSpeed(raw: string | null | undefined): number {
  const n = Number(raw);
  return (SPEEDS as readonly number[]).includes(n) ? n : DEFAULT_SPEED;
}

export function speedLabel(speed: number): string {
  return `${speed}x`;
}

/** How long autoplay stays on one slide: grows with the words (text and point) and the code lines, shrinks as speed rises. */
export function slideDurationMs(
  slide: Pick<SlideItem, "text" | "code" | "output" | "point">,
  speed: number,
): number {
  const s = (SPEEDS as readonly number[]).includes(speed) ? speed : DEFAULT_SPEED;
  const words = countWords(slide.text) + countWords(slide.point);
  const base =
    BASE_MS + words * WORD_MS + countLines(slide.code) * CODE_LINE_MS + (slide.output ? OUTPUT_MS : 0);
  return Math.round(base / s);
}

/** The pause between the code appearing and its output appearing. */
export function outputDelayMs(speed: number): number {
  const s = (SPEEDS as readonly number[]).includes(speed) ? speed : DEFAULT_SPEED;
  return Math.round(OUTPUT_DELAY_MS / s);
}

// ── Keys ───────────────────────────────────────────────────────────────

export interface KeyContext {
  /** The focused element's tag name, upper case ("" when none). */
  tag: string;
  /** Focus is in a contenteditable element. */
  editable: boolean;
  ctrl: boolean;
  alt: boolean;
  meta: boolean;
}

export type KeyAction = "next" | "prev" | "toggle" | "none";

export function isTypingTarget(tag: string, editable: boolean): boolean {
  return editable || tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT";
}

/**
 * What a key does: the right arrow and Space go to the next slide, the left arrow to the previous one, and
 * P plays or pauses. Nothing happens while you are typing in a text box or with Ctrl, Alt or Meta held. A
 * focused button keeps its own Space (it clicks).
 */
export function keyAction(key: string, c: KeyContext): KeyAction {
  if (c.ctrl || c.alt || c.meta || isTypingTarget(c.tag, c.editable)) return "none";
  if (key === "ArrowRight") return "next";
  if (key === "ArrowLeft") return "prev";
  if (key === " " || key === "Spacebar") {
    return c.tag === "BUTTON" || c.tag === "A" || c.tag === "SUMMARY" ? "none" : "next";
  }
  if (key === "p" || key === "P") return "toggle";
  return "none";
}

// ── Playing on: the next deck, loop, shuffle, resume ───────────────────

export const LOOP_KEY = "code-coach:slides-loop";
export const SHUFFLE_KEY = "code-coach:slides-shuffle";
export const RESUME_KEY = "code-coach:slides-resume";

/** A saved on/off switch: "1" or "0", anything else is the default. */
export function parseFlag(raw: string | null | undefined, fallback: boolean): boolean {
  return raw === "1" ? true : raw === "0" ? false : fallback;
}

export interface NextDeckOptions {
  /** After the last deck go back to the first (or, shuffling, start a new round of unseen decks). */
  loop: boolean;
  /** Pick a random deck not yet seen instead of the next in order. */
  shuffle: boolean;
  /** Deck ids already played this session (the current one counts as seen). */
  seen: readonly string[];
  /** Returns [0, 1); injectable so tests are exact. */
  rng: () => number;
}

/**
 * Which deck follows `current` when autoplay finishes it: the next in `order`, or a random unseen one when
 * shuffling. null when it should stop: the last deck without loop, every deck seen without loop, or no decks.
 * With loop on, a finished round starts again (in order: the first deck; shuffled: any deck but this one).
 */
export function nextDeckId(order: readonly string[], current: string, o: NextDeckOptions): string | null {
  if (order.length === 0) return null;
  const at = order.indexOf(current);
  if (!o.shuffle) {
    if (at >= 0 && at < order.length - 1) return order[at + 1];
    if (!o.loop) return null;
    return order.length === 1 && at === 0 ? null : order[0];
  }
  const seen = new Set(o.seen);
  seen.add(current);
  let pool = order.filter((id) => !seen.has(id));
  if (pool.length === 0) {
    if (!o.loop) return null;
    pool = order.filter((id) => id !== current);
  }
  if (pool.length === 0) return null;
  const r = o.rng();
  const k = Math.min(pool.length - 1, Math.max(0, Math.floor(Number.isFinite(r) ? r * pool.length : 0)));
  return pool[k];
}

/** "deck 4 of 20" (null when the deck is not in the list). */
export function deckPositionLabel(order: readonly string[], id: string): string | null {
  const at = order.indexOf(id);
  return at < 0 ? null : `deck ${at + 1} of ${order.length}`;
}

export interface Resume {
  deckId: string;
  index: number;
}

export function serializeResume(r: Resume): string {
  return JSON.stringify({ deckId: r.deckId, index: Math.max(0, Math.trunc(r.index)) });
}

/** A saved place, or null for nothing, junk, or a deck that no longer exists in `order`. */
export function parseResume(raw: string | null | undefined, order: readonly string[]): Resume | null {
  if (!raw) return null;
  try {
    const v = JSON.parse(raw) as { deckId?: unknown; index?: unknown };
    if (typeof v.deckId !== "string" || !order.includes(v.deckId)) return null;
    const n = typeof v.index === "number" && Number.isFinite(v.index) ? Math.max(0, Math.trunc(v.index)) : 0;
    return { deckId: v.deckId, index: n };
  } catch {
    return null;
  }
}

/** "Picked up at Types, slide 5". */
export function resumeLabel(title: string, index: number): string {
  return `Picked up at ${title}, slide ${Math.max(0, Math.trunc(index)) + 1}`;
}

/** The "Next deck: X" notice: only while playing the last slide, when a deck follows. */
export function upNextLabel(playing: boolean, atLast: boolean, nextTitle: string | null): string | null {
  return playing && atLast && nextTitle ? `Next deck: ${nextTitle}` : null;
}

/** Where a manual key press lands from `index`; applied one press at a time so several presses never collapse. */
export function pressTarget(action: "next" | "prev", index: number, count: number): number {
  return action === "next" ? nextIndex(index, count) : prevIndex(index, count);
}
