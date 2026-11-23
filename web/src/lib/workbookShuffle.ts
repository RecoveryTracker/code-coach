/**
 * Workbook shuffle: random exercises from a range of pages.
 *
 * Pure so tests/test_workbook_shuffle.py can run it in node. The screen keeps
 * a deck of {pageId, exerciseId} and walks it; when it runs out a new deck is
 * dealt, so the shuffle never ends and nothing repeats until every exercise
 * in the range has come up once.
 */

export type ShufflePage = { id: string; number: number; exercises: { id: string }[] };
export type Card = { pageId: string; exerciseId: string };
export type Range = { from: number; to: number };

/**
 * The furthest page you have got to: the highest-numbered page with a solved
 * exercise, or the page you are on, whichever is further. Page 1 before you
 * have started, so "up to where I am" always has something in it.
 */
export function reachedPage(pages: ShufflePage[], done: Iterable<string>, atPageId: string | null | undefined): number {
  const solved = new Set(done);
  let best = 0;
  for (const p of pages) {
    if (p.id === atPageId || p.exercises.some((e) => solved.has(e.id))) best = Math.max(best, p.number);
  }
  if (best === 0) best = Math.min(...pages.map((p) => p.number).filter(Number.isFinite), Infinity);
  return Number.isFinite(best) ? best : 1;
}

/** The lowest and highest page numbers in the book. */
export function bounds(pages: ShufflePage[]): Range {
  const n = pages.map((p) => p.number);
  return n.length ? { from: Math.min(...n), to: Math.max(...n) } : { from: 1, to: 1 };
}

/**
 * A range the book can deal from: whole numbers, inside the book, from <= to
 * (typed backwards, "35 to 28", is taken to mean 28 to 35).
 */
export function cleanRange(range: Range, pages: ShufflePage[]): Range {
  const b = bounds(pages);
  const fix = (v: number, fallback: number) =>
    Number.isFinite(v) ? Math.min(b.to, Math.max(b.from, Math.round(v))) : fallback;
  const a = fix(range.from, b.from);
  const z = fix(range.to, b.to);
  return a <= z ? { from: a, to: z } : { from: z, to: a };
}

/** Every exercise on the pages numbered from..to (both included), in book order. */
export function poolFor(pages: ShufflePage[], range: Range): Card[] {
  return pages
    .filter((p) => p.number >= range.from && p.number <= range.to)
    .flatMap((p) => p.exercises.map((e) => ({ pageId: p.id, exerciseId: e.id })));
}

/**
 * The pool in a random order (Fisher-Yates with the given random source), then
 * nudged so two cards from the same page do not sit side by side where that
 * can be avoided - twelve goes at one page in a row is the page, not a shuffle.
 * `avoidFirst` is the page the last deck ended on, so a new deck does not open
 * with it either.
 */
export function deal(pool: Card[], random: () => number = Math.random, avoidFirst = ""): Card[] {
  const rest = pool.slice();
  for (let i = rest.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [rest[i], rest[j]] = [rest[j], rest[i]];
  }
  // Then laid out one card at a time: the first card (in the shuffled order)
  // not from the page just shown. Swapping clumps apart afterwards can leave
  // one at the end; this cannot, because when one page holds so many of the
  // cards left that it must go now or end up side by side, it goes now.
  const deck: Card[] = [];
  let before = avoidFirst;
  while (rest.length > 0) {
    const counts = new Map<string, number>();
    for (const c of rest) counts.set(c.pageId, (counts.get(c.pageId) ?? 0) + 1);
    let forced = "";
    for (const [pageId, n] of counts) {
      if (pageId !== before && 2 * n > rest.length) forced = pageId;
    }
    let at = rest.findIndex((c) => (forced ? c.pageId === forced : c.pageId !== before));
    if (at === -1) at = 0; // only the page just shown is left: nothing to avoid
    const [next] = rest.splice(at, 1);
    deck.push(next);
    before = next.pageId;
  }
  return deck;
}

/** How the range is said on screen: "Pages 1-21", "Page 7". */
export function rangeLabel(range: Range): string {
  return range.from === range.to ? `Page ${range.from}` : `Pages ${range.from}–${range.to}`;
}

const KEY = (language: string) => `code-coach:workbook-shuffle:${language}`;

/** The last range used in this language, so the boxes open where you left them. Null when none or unreadable. */
export function readRange(language: string, storage: Pick<Storage, "getItem"> | null = safeStorage()): Range | null {
  try {
    const raw = storage?.getItem(KEY(language));
    if (!raw) return null;
    const got = JSON.parse(raw) as Partial<Range>;
    return typeof got.from === "number" && typeof got.to === "number" ? { from: got.from, to: got.to } : null;
  } catch {
    return null;
  }
}

export function writeRange(language: string, range: Range, storage: Pick<Storage, "setItem"> | null = safeStorage()): void {
  try {
    storage?.setItem(KEY(language), JSON.stringify(range));
  } catch {
    /* the range just won't be remembered */
  }
}

function safeStorage(): Storage | null {
  try {
    return typeof localStorage === "undefined" ? null : localStorage;
  } catch {
    return null;
  }
}
