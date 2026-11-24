/**
 * Brain Drills, picking a round up where you left it.
 *
 * Leaving the Brain Drills tab (to Free mode, anywhere) unmounts the screen, and a round in progress used to go with
 * it. This keeps one snapshot per language of the round being played - the same generated questions, the answers and
 * marks, the half-typed text, where you were, what the clock had counted - and hands it back when you return.
 *
 * Pure on purpose (no React, no timers): tests/test_brain_resume.py bundles it with esbuild and runs it in node. The
 * only impure part is the storage at the bottom: a module-level Map (survives tab switches in the same page) and
 * sessionStorage (survives a reload of the same browser tab), both optional and both wrapped in try/catch.
 *
 * What is kept: the activity and its questions (never regenerated), the round id (so Momentum's per-answer keys stay the
 * same and nothing is paid twice), the Code age check chain (checkId / checkLeft / checkAges), every answer and mark,
 * the question you were on, the text typed into the box, and the clock as a number of seconds (time away is not
 * counted: it is rebuilt as a clock that starts running - or stays paused on an answered question - from that value).
 * What is not: the 3-2-1 countdown (not replayed), an open Questions grid, Run it / Explain output, a Done screen.
 */

import {
  clockElapsed,
  clockFor,
  type BrainItem,
  type BrainLang,
  type Clock,
  type RoundState,
} from "./brainRound";

/** Bumped when the snapshot's shape changes: an older one is dropped rather than guessed at. */
export const SNAPSHOT_VERSION = 1;
/** A snapshot older than this is a different day's round: dropped. */
export const MAX_AGE_MS = 12 * 60 * 60 * 1000;

export type RoundSnapshot = {
  v: number;
  language: BrainLang;
  activityId: string;
  /** Code age check chain; "" and [] for a single activity. */
  checkId: string;
  checkLeft: string[];
  checkAges: number[];
  /** The round's own name for Momentum's per-answer keys. */
  roundId: string;
  items: BrainItem[];
  rs: RoundState;
  /** What was typed into the answer box for the question being looked at. */
  typed: string;
  /** Seconds the clock had counted when it was saved. */
  elapsed: number;
  /** Was the Variable Recall "Remember these" phase on screen? (It is shown again from the start if so.) */
  showing: boolean;
  /** Date.now() when saved. */
  savedAt: number;
};

/** The slice of the home screen's data that says what an activity is today. */
export type ActivityShape = { id: string; title: string; count: number; kind: "type" | "pick"; choices: string[] };

export type ResumeContext = {
  language: BrainLang;
  activities: ActivityShape[];
  now: number;
};

export function resumeKey(language: string): string {
  return `code-coach:brain-round:${language}`;
}

export function makeSnapshot(a: {
  language: BrainLang;
  activityId: string;
  checkId: string;
  checkLeft: string[];
  checkAges: number[];
  roundId: string;
  items: BrainItem[];
  rs: RoundState;
  typed: string;
  clock: Clock | null;
  showing: boolean;
  now: number;
  /** performance.now() for the clock's reading. */
  perfNow: number;
}): RoundSnapshot {
  return {
    v: SNAPSHOT_VERSION,
    language: a.language,
    activityId: a.activityId,
    checkId: a.checkId,
    checkLeft: [...a.checkLeft],
    checkAges: [...a.checkAges],
    roundId: a.roundId,
    items: a.items,
    rs: { answers: a.rs.answers.map((x) => (x ? { given: x.given, right: x.right } : null)), index: a.rs.index },
    typed: a.typed,
    elapsed: a.clock ? clockElapsed(a.clock, a.perfNow) : 0,
    showing: a.showing,
    savedAt: a.now,
  };
}

/**
 * The clock of a resumed round: it reads `seconds` at `now` and runs on from there (the time away is not in it), then
 * is brought in line with where you are looking - stopped on an answered question, running on an open one.
 */
export function clockFromElapsed(seconds: number, now: number, rs: RoundState): Clock {
  const c: Clock = { t0: now - Math.max(0, seconds) * 1000, pausedAt: null, lost: 0 };
  return clockFor(c, rs, now);
}

export function serialize(s: RoundSnapshot): string {
  return JSON.stringify(s);
}

const isStr = (x: unknown): x is string => typeof x === "string";
const isObj = (x: unknown): x is Record<string, unknown> => typeof x === "object" && x !== null && !Array.isArray(x);

function isItem(x: unknown): x is BrainItem {
  return (
    isObj(x) && isStr(x.prompt) && isStr(x.answer) && isStr(x.explain) && isStr(x.show) &&
    (x.check === undefined || x.check === null || isStr(x.check))
  );
}

/** Text back into a snapshot, or null for anything that is not one (corrupt JSON, wrong shape, another version). */
export function parseSnapshot(text: string | null | undefined): RoundSnapshot | null {
  if (!text) return null;
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    return null;
  }
  if (!isObj(raw) || raw.v !== SNAPSHOT_VERSION) return null;
  const rs = raw.rs;
  if (
    !isStr(raw.language) || !isStr(raw.activityId) || !isStr(raw.checkId) || !isStr(raw.roundId) || !isStr(raw.typed) ||
    !Array.isArray(raw.checkLeft) || !raw.checkLeft.every(isStr) ||
    !Array.isArray(raw.checkAges) || !raw.checkAges.every((n) => typeof n === "number" && Number.isFinite(n)) ||
    !Array.isArray(raw.items) || raw.items.length === 0 || !raw.items.every(isItem) ||
    typeof raw.elapsed !== "number" || !Number.isFinite(raw.elapsed) || raw.elapsed < 0 ||
    typeof raw.savedAt !== "number" || !Number.isFinite(raw.savedAt) ||
    typeof raw.showing !== "boolean" ||
    !isObj(rs) || !Array.isArray(rs.answers) || rs.answers.length !== raw.items.length ||
    typeof rs.index !== "number" || !Number.isInteger(rs.index) || rs.index < 0 || rs.index >= raw.items.length ||
    !rs.answers.every((a) => a === null || (isObj(a) && isStr(a.given) && typeof a.right === "boolean"))
  ) {
    return null;
  }
  return raw as unknown as RoundSnapshot;
}

/**
 * Why a parsed snapshot cannot be used now, or "" when it can: too old, another language, or an activity that is gone,
 * is not played in this language, or no longer matches the questions it was saved with (a new code version: a different
 * number of questions, or a pick activity whose answers are no longer one of its two choices).
 */
export function staleReason(s: RoundSnapshot, ctx: ResumeContext): string {
  if (s.language !== ctx.language) return "another language";
  const age = ctx.now - s.savedAt;
  if (age > MAX_AGE_MS) return "expired";
  if (age < -60_000) return "saved in the future";
  const byId = new Map(ctx.activities.map((a) => [a.id, a]));
  const act = byId.get(s.activityId);
  if (!act) return "activity not played in this language";
  if (s.items.length > act.count) return "the activity's questions changed";
  if (act.kind === "pick" && !s.items.every((i) => act.choices.includes(i.answer))) {
    return "the activity's choices changed";
  }
  // A Shuffle round's questions each name their own activity: each must still be here and still fit.
  for (const i of s.items) {
    if (!i.activity) continue;
    const own = byId.get(i.activity);
    if (!own) return "a shuffled question's activity is gone";
    if (own.kind === "pick" && !own.choices.includes(i.answer)) return "the activity's choices changed";
  }
  if (s.checkLeft.some((id) => !byId.has(id))) return "the check changed";
  return "";
}

/** The home screen's button: "Resume Eval - question 7 of 16". */
export function resumeLabel(s: Pick<RoundSnapshot, "rs" | "items">, title: string): string {
  return `Resume ${title} - question ${s.rs.index + 1} of ${s.items.length}`;
}

// ── Where it is kept ────────────────────────────────────────────────────

/** The part of Storage this needs (so a test can hand in a fake, or one that throws). */
export type TextStore = Pick<Storage, "getItem" | "setItem" | "removeItem">;

const memory = new Map<string, RoundSnapshot>();

/** For tests: forget the module-level copies (a page reload does this for real). */
export function forgetMemory(): void {
  memory.clear();
}

function sessionStore(): TextStore | null {
  try {
    return typeof window !== "undefined" && window.sessionStorage ? window.sessionStorage : null;
  } catch {
    return null;
  }
}

export function saveSnapshot(s: RoundSnapshot, store: TextStore | null = sessionStore()): void {
  memory.set(resumeKey(s.language), s);
  try {
    store?.setItem(resumeKey(s.language), serialize(s));
  } catch {
    /* storage full, blocked or unavailable: the module copy still serves a tab switch */
  }
}

export function clearSnapshot(language: string, store: TextStore | null = sessionStore()): void {
  memory.delete(resumeKey(language));
  try {
    store?.removeItem(resumeKey(language));
  } catch {
    /* quiet */
  }
}

/** The snapshot kept for a language, unchecked: the module copy first, else what sessionStorage holds. */
export function readSnapshot(language: string, store: TextStore | null = sessionStore()): RoundSnapshot | null {
  const mem = memory.get(resumeKey(language));
  if (mem) return mem;
  try {
    const text = store?.getItem(resumeKey(language));
    const parsed = parseSnapshot(text);
    if (parsed && parsed.language === language) return parsed;
  } catch {
    /* quiet */
  }
  return null;
}

/**
 * The snapshot a language can resume right now, or null. One that has gone stale (see staleReason) or is corrupt is
 * dropped from both places on the way, silently.
 */
export function loadResumable(
  ctx: ResumeContext,
  store: TextStore | null = sessionStore(),
): RoundSnapshot | null {
  const s = readSnapshot(ctx.language, store);
  if (!s) {
    // Something unreadable may still sit in storage under the key: take it away.
    try {
      if (store?.getItem(resumeKey(ctx.language))) store.removeItem(resumeKey(ctx.language));
    } catch {
      /* quiet */
    }
    return null;
  }
  if (staleReason(s, ctx)) {
    clearSnapshot(ctx.language, store);
    return null;
  }
  return s;
}
