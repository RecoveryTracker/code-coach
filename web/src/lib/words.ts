/**
 * The "Words used" cards, the rules behind them: which card is open, which words
 * a "see also" chip can jump to and which it has to fetch, and how the
 * truthy/falsy lists become two columns.
 *
 * Pure on purpose (no React, no DOM), so tests/test_glossary.py can bundle it
 * with esbuild and run it in node, like web/src/lib/brainRound.ts.
 */

import type { Word } from "../types";

/** The cards open when a list first appears: just the first word, so a page of words never opens as a wall. */
export function initialOpen(words: Word[]): string[] {
  return words.length > 0 ? [words[0].id] : [];
}

/** Open the card if it is shut, shut it if it is open. */
export function toggleOpen(open: string[], id: string): string[] {
  return open.includes(id) ? open.filter((x) => x !== id) : [...open, id];
}

/** Make sure a card is open (a chip jumped to it). */
export function revealOpen(open: string[], id: string): string[] {
  return open.includes(id) ? open : [...open, id];
}

/** The listed words, then any fetched through a "see also" chip - no word twice. */
export function withExtras(words: Word[], extras: Word[]): Word[] {
  const seen = new Set(words.map((w) => w.id));
  const out = [...words];
  for (const w of extras) {
    if (!seen.has(w.id)) {
      seen.add(w.id);
      out.push(w);
    }
  }
  return out;
}

/** What a "see also" chip does: jump to a card that is already there, or fetch the word first. */
export function seeAlsoAction(shown: Word[], id: string): "show" | "fetch" {
  return shown.some((w) => w.id === id) ? "show" : "fetch";
}

/** The element id of one card, unique per list on the page (several can be on screen at once). */
export function cardDomId(scope: string, id: string): string {
  return `word-${scope}-${id}`.replace(/[^A-Za-z0-9_-]/g, "-");
}

/** Truthy and Falsy show two columns, "counts as false" and "counts as true"; every other word has none. */
export function columnsOf(word: Word): { title: string; tone: "false" | "true"; items: string[] }[] {
  if (word.counts_false.length === 0 && word.counts_true.length === 0) return [];
  return [
    { title: "Counts as false", tone: "false", items: word.counts_false },
    { title: "Counts as true", tone: "true", items: word.counts_true },
  ];
}

/** Whether the "Words in this question" line shows: only on a question you missed, and only if there are words. */
export function showsQuestionWords(missed: boolean, words: Word[] | null): boolean {
  return missed && words !== null && words.length > 0;
}
