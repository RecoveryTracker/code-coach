/**
 * Brain Drills, the round's bookkeeping: what you answered, where you are,
 * what the clock has counted - and the snippet each question can be run as.
 *
 * Pure on purpose (no React, no DOM, no timers), so tests/test_brain_round.py
 * can bundle it with esbuild and run it in node. The rules it keeps:
 *
 *  - Every question is answered once. Reviewing an answered question is
 *    read-only: it adds no miss, changes no score and costs no time.
 *  - You may jump to any question. A question you haven't answered is simply
 *    "open" and, when you land on it, you answer it. The round is finished
 *    when every question has an answer; there is no finishing early.
 *  - The clock runs only while you are on a question you have yet to answer.
 *    Looking at an answered one (reading a miss, going Back, a jump to a
 *    finished cell) pauses it, and it picks up where it stopped.
 *
 * The score is still the server's code_age(seconds, errors, total); the round
 * is posted only when it is complete.
 */

export type BrainItem = {
  prompt: string;
  answer: string;
  explain: string;
  show: string;
  /** Code that works the answer out (loops, final values); blank when the prompt itself is the program. */
  check?: string;
};

export type BrainLang = "javascript" | "python" | "dart";

/** What you said to one question, and whether it was right. */
export type Answer = { given: string; right: boolean };

export type RoundState = {
  /** One slot per question: null until it is answered. */
  answers: (Answer | null)[];
  /** The question being looked at. */
  index: number;
};

export type CellStatus = "right" | "missed" | "open";

export function newRound(total: number): RoundState {
  return { answers: Array.from({ length: Math.max(0, total) }, () => null), index: 0 };
}

export function isAnswered(s: RoundState, i: number): boolean {
  return i >= 0 && i < s.answers.length && s.answers[i] !== null;
}

export function answeredCount(s: RoundState): number {
  return s.answers.filter((a) => a !== null).length;
}

export function isComplete(s: RoundState): boolean {
  return s.answers.length > 0 && answeredCount(s) === s.answers.length;
}

/** Are you looking at an answered question (so: reading, not answering)? */
export function isReviewing(s: RoundState): boolean {
  return isAnswered(s, s.index);
}

/** Write down an answer. The first answer to a question stands: a second one
 *  (a stray double-submit, a replay) changes nothing, so nothing is counted twice. */
export function recordAnswer(s: RoundState, i: number, given: string, right: boolean): RoundState {
  if (i < 0 || i >= s.answers.length || s.answers[i] !== null) return s;
  const answers = s.answers.slice();
  answers[i] = { given, right };
  return { ...s, answers };
}

/** Look at question i (clamped to the round). */
export function jumpTo(s: RoundState, i: number): RoundState {
  if (!s.answers.length) return s;
  const index = Math.min(s.answers.length - 1, Math.max(0, Math.trunc(i)));
  return index === s.index ? s : { ...s, index };
}

/** The first open question after `from`, wrapping round to the start; -1 when none is left. */
export function nextOpen(s: RoundState, from: number): number {
  const n = s.answers.length;
  for (let k = 1; k <= n; k++) {
    const i = (((from + k) % n) + n) % n;
    if (s.answers[i] === null) return i;
  }
  return -1;
}

/** Where "Next" goes: the following question, or - from the last one - the first still open. */
export function forwardTarget(s: RoundState): number {
  if (s.index + 1 < s.answers.length) return s.index + 1;
  return nextOpen(s, s.index);
}

/** Where "Back" goes, or -1 from the first question. */
export function backTarget(s: RoundState): number {
  return s.index > 0 ? s.index - 1 : -1;
}

/** Where answering (or Resume) leaves you: the next open question after this one. */
export function resumeTarget(s: RoundState): number {
  return nextOpen(s, s.index);
}

export function cellStatus(s: RoundState, i: number): CellStatus {
  const a = s.answers[i];
  return a === null || a === undefined ? "open" : a.right ? "right" : "missed";
}

/** Spoken name of a grid cell, e.g. "Question 7, missed" or "Question 3, not answered yet, current". */
export function cellLabel(s: RoundState, i: number): string {
  const status = cellStatus(s, i);
  const word = status === "open" ? "not answered yet" : status;
  return `Question ${i + 1}, ${word}${i === s.index ? ", current" : ""}`;
}

/** The misses, in question order, as the Done screen lists them. */
export function missesOf<T extends BrainItem>(s: RoundState, items: T[]): { item: T; given: string }[] {
  const out: { item: T; given: string }[] = [];
  s.answers.forEach((a, i) => {
    if (a && !a.right && items[i]) out.push({ item: items[i], given: a.given });
  });
  return out;
}

// ── The clock ───────────────────────────────────────────────────────────
// A stopwatch that can be paused. `lost` is time spent paused, which is
// taken off; pausing twice or resuming a running clock changes nothing.

export type Clock = { t0: number; pausedAt: number | null; lost: number };

export function clockStart(now: number): Clock {
  return { t0: now, pausedAt: null, lost: 0 };
}

export function clockPause(c: Clock, now: number): Clock {
  return c.pausedAt === null ? { ...c, pausedAt: now } : c;
}

export function clockResume(c: Clock, now: number): Clock {
  return c.pausedAt === null ? c : { t0: c.t0, pausedAt: null, lost: c.lost + (now - c.pausedAt) };
}

export function clockElapsed(c: Clock, now: number): number {
  return Math.max(0, ((c.pausedAt ?? now) - c.t0 - c.lost) / 1000);
}

/** Bring the clock in line with where you are looking: stopped on an
 *  answered question, running on an open one. */
export function clockFor(c: Clock, s: RoundState, now: number): Clock {
  return isReviewing(s) ? clockPause(c, now) : clockResume(c, now);
}

// ── Running a question's code ───────────────────────────────────────────

export type Runnable =
  | {
      ok: true;
      /** The program as the learner would read it - what Explain looks at. */
      code: string;
      /** What actually runs, when that has to differ from `code` (blank: `code`). */
      run: string;
      /** Syntax Snap and Bracket Check: whether it parses IS the answer, so say so. */
      parseIsTheAnswer: boolean;
      /** Error or Fine: whether running it raises IS the answer (the program is the snippet as shown). */
      raisesIsTheAnswer?: boolean;
    }
  | { ok: false; reason: string };

const IDENT = /^[A-Za-z_$][\w$]*$/;

function printer(lang: BrainLang, expr: string): string {
  const e = expr.trim().replace(/;+$/, "");
  if (lang === "dart") return `print(${e});`;
  return lang === "python" ? `print(${e})` : `console.log(${e});`;
}

/** Everything but the last line, then that last line printed. */
function printLast(code: string, lang: BrainLang): string {
  const lines = code.replace(/\s+$/, "").split("\n");
  const last = lines.pop() ?? "";
  return [...lines, printer(lang, last)].join("\n");
}

/**
 * The Dart program behind an item's code (the same rule as `full_program` in tests/dart_oracle.py, which a test holds
 * this to): code that mentions `main(` is already a whole program; anything else is the body of `main`, whose last
 * line is printed when it is a bare expression (it does not start with `print(` and does not end in `;` or `}`).
 */
export function dartProgram(code: string): string {
  if (/\bmain\s*\(/.test(code)) return code;
  const lines = code.replace(/\s+$/, "").split("\n");
  const last = (lines[lines.length - 1] ?? "").trim();
  if (!(last.startsWith("print(") || last.endsWith(";") || last.endsWith("}"))) lines[lines.length - 1] = `print(${last});`;
  return "void main() {\n" + lines.map((ln) => (ln.trim() ? "  " + ln : ln)).join("\n") + "\n}";
}

/** Why Flutter-widget questions have no "Run it": the browser has no Flutter. */
export const FLUTTER_CANNOT_RUN =
  "Flutter widgets cannot run here: this answer was measured with Flutter itself (the explanation says how it is worked out).";

/**
 * A Flutter-widget activity (oracle "flutter" in code_coach/brain). Its id starts with one of the Flutter
 * families (fl_ layout, fs_ state, fw_ widgets), which tests/test_brain_packs.py holds equal to the oracle.
 */
export function isFlutterActivity(activityId: string): boolean {
  return /^f[lsw]_/.test(activityId);
}

/** The program behind one question, ready to run and show something. */
export function runnableFor(activityId: string, item: BrainItem, lang: BrainLang): Runnable {
  if (lang === "dart" && isFlutterActivity(activityId)) return { ok: false, reason: FLUTTER_CANNOT_RUN };
  if (lang === "dart") {
    // Every Dart activity is a pack (see code_coach/brain/__init__.py): the program is `check` when the item has one,
    // else the prompt, and `code` is the whole program that runs. Fine-or-error items are judged by whether it throws.
    const source = item.check || item.prompt;
    if (!source.trim()) return { ok: false, reason: "There is no code to run here." };
    return {
      ok: true, code: dartProgram(source), run: "", parseIsTheAnswer: false,
      ...(item.answer === "fine" || item.answer === "error" ? { raisesIsTheAnswer: true } : {}),
    };
  }
  const js = lang === "javascript";
  // (raisesIsTheAnswer is only present when it is true, so the other activities' shapes stay as they were.)
  const fine = (code: string, run = "", parseIsTheAnswer = false, raisesIsTheAnswer = false): Runnable => ({
    ok: true, code, run, parseIsTheAnswer, ...(raisesIsTheAnswer ? { raisesIsTheAnswer } : {}),
  });
  switch (activityId) {
    case "eval":
      return fine(printer(lang, item.prompt));
    case "truthy":
      return fine(
        js
          ? `console.log((${item.prompt}) ? "truthy" : "falsy");`
          : `print("truthy" if (${item.prompt}) else "falsy")`,
      );
    case "loops":
      // A loop that shows its own counting runs as shown; a while loop leaves
      // the counting out of the picture, and the check is what adds it.
      if (js && /\bcount\b/.test(item.prompt)) return fine(`let count = 0;\n${item.prompt}\nconsole.log(count);`);
      return fine(printLast(item.check || `count = 0\n${item.prompt}\ncount`, lang));
    case "trace":
      return fine(printLast(item.check || item.prompt, lang));
    case "recall": {
      const name = item.prompt.trim().replace(/\?+$/, "").trim();
      if (!IDENT.test(name) || !item.show) return { ok: false, reason: "There is no code to run here." };
      return fine(`${item.show}\n${printer(lang, name)}`);
    }
    case "brackets":
      if (js) {
        // Just brackets, not a program: "balanced" has nothing to do with "parses".
        return { ok: false, reason: "These are only brackets, not a program, so there is nothing to run." };
      }
      return fine(item.prompt, "", true);
    case "syntax":
      // A script's rules, as the drill's answer uses: no top-level return, no
      // top-level await. An indirect eval parses as a script, a module would not.
      return js
        ? fine(item.prompt, `(0, eval)(${JSON.stringify(item.prompt)});`, true)
        : fine(item.prompt, "", true);
    case "error":
      // Error or Fine: run the snippet as shown - the traceback (or the quiet) is the answer.
      return item.prompt ? fine(item.prompt, "", false, true) : { ok: false, reason: "There is no code to run here." };
    default:
      // Every pack activity (see code_coach/brain/__init__.py): the program is `check` when the item has one
      // (it prints the answer: "yes"/"no" for the picks), else the prompt itself, and its last line is printed.
      if (!item.prompt) return { ok: false, reason: "There is no code to run here." };
      return item.check ? fine(item.prompt, printLast(item.check, lang)) : fine(printLast(item.prompt, lang));
  }
}

/** The tracer's traceback without the tracer: only the learner's own frames, file named "snippet". */
export function cleanError(text: string): string {
  const lines = text.replace(/\r/g, "").split("\n");
  const out: string[] = [];
  let skipping = false;
  for (const line of lines) {
    if (/^\s*File "/.test(line)) {
      skipping = /_trace_runner\.py/.test(line);
      if (skipping) continue;
      out.push(line.replace(/File "[^"]*"/, 'File "snippet"'));
      continue;
    }
    // The source line (and caret marks) under a File line stay with it.
    if (skipping && /^\s/.test(line)) continue;
    skipping = false;
    out.push(line);
  }
  return out.join("\n").trim();
}

/** Did the error say the code does not parse (as opposed to failing while running)? */
export function isSyntaxError(error: string | null | undefined): boolean {
  return !!error && /(^|\n)\s*(Syntax|Indentation|Tab)Error\b/.test(error);
}
