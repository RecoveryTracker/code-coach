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

export const SPEEDS = [0.75, 1, 1.5, 2] as const;
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
