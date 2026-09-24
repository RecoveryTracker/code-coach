/**
 * Where each mode remembers the item you were on.
 *
 * Every practice screen keeps a "last" key in localStorage so that coming
 * back lands where you left. The session queue uses the same keys the other
 * way round: to send you to a particular item, it writes the key and then
 * switches mode, and the mode picks it up on the way in.
 *
 * That only works while both sides agree on the spelling, so the spellings
 * live here and both sides import them. They were duplicated at first —
 * seven constants in seven components and a copy of the list in the session
 * — which is a rename away from a queue that silently sends you to whatever
 * you last looked at instead of what it says on the card.
 */

import type { Mode } from "./components/ModeBar";

export const LAST_KEYS = {
  forms: "code-coach:kata-last",
  predict: "code-coach:predict-last",
  styles: "code-coach:css-last",
  drills: "code-coach:drill-last",
  magnets: "code-coach:magnet-last",
  errors: "code-coach:error-last",
  trace: "code-coach:trace-last",
  bughunt: "code-coach:bughunt-last",
  regex: "code-coach:regex-last",
  puzzles: "code-coach:puzzles-last",
  cases: "code-coach:cases-last",
} as const;

export type Practice = keyof typeof LAST_KEYS;

/**
 * Which screen each kind of item lives on.
 *
 * Mostly one-to-one, with one exception: the typing drills are the second
 * half of the HTML & CSS screen rather than a mode of their own, so getting
 * to one means opening that screen on the right half as well.
 */
export const MODE_FOR: Record<Practice, Mode> = {
  forms: "katas",
  predict: "predict",
  styles: "styles",
  drills: "styles",
  magnets: "magnets",
  errors: "errors",
  trace: "trace",
  bughunt: "bughunt",
  regex: "regex",
  puzzles: "puzzles",
  cases: "cases",
};

/** The HTML & CSS screen's own tab, which the drills live behind. */
export const CSS_HALF_KEY = "code-coach:css-half";

/**
 * Point a mode at one item, and say which screen to open.
 *
 * Writing the key rather than passing the id through props is deliberate:
 * every screen already reads this on mount, so the queue needs no new way
 * in, and landing from the queue is the same code path as coming back to
 * what you were doing.
 */
export function aimAt(practice: Practice, itemId: string): Mode {
  try {
    localStorage.setItem(LAST_KEYS[practice], itemId);
    if (practice === "drills") localStorage.setItem(CSS_HALF_KEY, "type");
    if (practice === "styles") localStorage.setItem(CSS_HALF_KEY, "read");
  } catch {
    /* a blocked store means it opens on whatever it opened on last */
  }
  return MODE_FOR[practice];
}
