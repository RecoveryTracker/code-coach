/**
 * The row of module names that every screen has on top.
 *
 * The app grew the other way round. The LeetCode workspace was the whole
 * program, and each new thing — the workbook, the katas, the predict
 * puzzles, HTML and CSS — was bolted on as a full-screen takeover with a
 * "Back to code" button in the corner. That made the workspace the floor
 * everything else stood on: you could not go from the workbook to the
 * katas, only back to the editor and out again, and the editor was where
 * you landed whether or not it was what you came for.
 *
 * None of those modules is more fundamental than the others. LeetCode
 * practice is one of them, so it is one name in this row like the rest.
 *
 * The row is defined once, here, and rendered by every screen. That is
 * the part that has to be true: a module list assembled separately per
 * screen drifts within a week, and the whole value of a fixed row is
 * that the word you want is in the place you last saw it.
 */

import type { ReactNode } from "react";

/** Every module, in the order they sit in the row. */
export const MODES = [
  {
    id: "workbook",
    label: "Workbook",
    title: "Pages of small exercises you solve by typing",
  },
  {
    id: "lessons",
    label: "Lessons",
    title: "The patterns, taught — how to get from a question to a solution",
  },
  {
    /* The id stays "katas". It is written into saved progress and into
       the remembered-mode key, and renaming it would lose both for the
       sake of a word nobody sees. */
    id: "katas",
    label: "Forms",
    title:
      "Write the function, then walk it again — called with inputs you "
      + "haven't seen",
  },
  {
    id: "predict",
    label: "Predict",
    title: "Read the code and say what it prints, then watch it happen",
  },
  {
    id: "styles",
    label: "HTML & CSS",
    title: "Read the markup and styles, say what the browser makes of it",
  },
  {
    id: "leetcode",
    label: "LeetCode",
    title: "The interview problems, with the editor and the coach",
  },
  {
    id: "typing",
    label: "Typing",
    title: "Keyboard practice — key sections, symbols, speed and vocabulary",
  },
  {
    id: "concepts",
    label: "Concepts",
    title: "The questions an interview asks that aren't coding problems",
  },
  {
    id: "reference",
    label: "Reference",
    title: "Cheat sheet and flashcards for the language you're in",
  },
] as const;

export type Mode = (typeof MODES)[number]["id"];

/** Whether a string is one of the modules, for reading back saved state. */
export function isMode(value: string): value is Mode {
  return MODES.some((m) => m.id === value);
}

export function ModeButtons({
  mode,
  onPick,
}: {
  mode: Mode;
  onPick: (next: Mode) => void;
}): ReactNode {
  return (
    <>
      {MODES.map((m) => (
        <button
          key={m.id}
          type="button"
          /* The current one is marked rather than removed. A row that
             drops the module you are in is a row that changes width and
             moves every other name along with it. */
          className={`ws-btn mode-btn${m.id === mode ? " on" : ""}`}
          aria-current={m.id === mode ? "page" : undefined}
          title={m.title}
          onClick={() => onPick(m.id)}
        >
          {m.label}
        </button>
      ))}
    </>
  );
}
