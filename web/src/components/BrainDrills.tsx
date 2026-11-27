/**
 * Brain Drills: short timed coding reflex drills, scored as a code age.
 *
 * After the DS brain-training games: each activity is about a minute,
 * answered as fast as you can from the keyboard, and scored as how old
 * your coding reflexes act - 20 at their sharpest, 80 at their slowest.
 * Training on a day stamps it; three activities in a row is a Code age
 * check, charted day by day.
 *
 * Everything is keyboard: type and Enter for typed answers, left/right
 * arrows (or F/J) for the two-way ones, Esc to leave a round. Alt+Left goes
 * back a question; "Questions" opens a grid to jump to any of them. An
 * answered question can be run and explained in place.
 *
 * A round in progress survives leaving the tab (and a page reload): lib/brainResume.ts keeps a snapshot per
 * language, and coming back picks the round up exactly where it was - see `Round`'s `resume`.
 */

import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";

import { fetchBrain, fetchBrainRound, fetchBrainShuffle, postBrainResult } from "../api";
import { award } from "../lib/momentum";
import {
  DRILL_APP_LANGUAGES,
  answeredCount,
  backTarget,
  brainLanguageFor,
  clockElapsed,
  clockFor,
  clockStart,
  forwardTarget,
  isComplete,
  jumpTo,
  missesOf,
  newRound,
  nextOpen,
  recordAnswer,
  resumeTarget,
  sameAnswer,
  type BrainItem,
  type BrainLang,
  type Clock,
  type RoundState,
} from "../lib/brainRound";
import {
  clearSnapshot,
  clockFromElapsed,
  loadResumable,
  makeSnapshot,
  resumeLabel,
  saveSnapshot,
  type RoundSnapshot,
} from "../lib/brainResume";
import "../styles/brain.css";
import BrainPicker from "./BrainPicker";
import BrainTools from "./BrainTools";
import { QuestionWords } from "./WordsUsed";

export type BrainLanguage = BrainLang;
const LANGUAGE_NAMES: Record<BrainLanguage, string> = {
  javascript: "JavaScript", python: "Python", dart: "Dart", c: "C", sql: "SQL", typescript: "TypeScript", rust: "Rust",
};

// Brain Drills follows the language picked at the top of the app: the mapping (brainLanguageFor) and the list of
// languages the "no drills yet" screen offers (DRILL_APP_LANGUAGES) live in lib/brainRound.ts, where a test runs them.
export { brainLanguageFor };

/** How the app's language ids read in a sentence (the picker's own names are not passed down). */
const APP_LANGUAGE_NAMES: Record<string, string> = {
  cpp: "C++", csharp: "C#", typescript: "TypeScript", javascript: "JavaScript", php: "PHP", sql: "SQL",
  postgresql: "PostgreSQL", lisp: "Common Lisp", tfwr: "The Farmer Was Replaced",
};

function languageLabel(id: string): string {
  return APP_LANGUAGE_NAMES[id] ?? id.charAt(0).toUpperCase() + id.slice(1);
}

type Result = { day: string; activity: string; seconds: number; errors: number; total: number; age: number };
type ActivityInfo = {
  id: string;
  title: string;
  blurb: string;
  question: string;
  count: number;
  kind: "type" | "pick";
  choices: string[];
  showSeconds: number;
  /** The heading the home screen files it under, and the glossary concepts it drills (from the server). */
  group?: string;
  concepts?: string[];
  best: Result | null;
  last: Result | null;
};
export type BrainSummary = {
  today: string;
  language: BrainLanguage;
  languages: BrainLanguage[];
  activities: ActivityInfo[];
  /** The home screen's headings, in order. */
  groups?: string[];
  check: string[];
  stamps: { day: string; trained: boolean }[];
  streak: number;
  checkAges: { day: string; age: number }[];
  trainedToday: boolean;
  /** Shuffle's own best and last, the headings it can draw from, and its question count. */
  shuffle?: { best: Result | null; last: Result | null; groups: string[]; count: number };
};
export type { BrainItem };

/** The id a Shuffle round is played and kept under (the server's brain.SHUFFLE_ID). */
export const SHUFFLE_ID = "shuffle";

/**
 * Shuffle is played through the same Round as an activity: this stands in for "the activity" (its title, and the
 * size the resume check allows), while every question uses the activity it came from.
 */
export function shuffleActivity(count = 16): ActivityInfo {
  return {
    id: SHUFFLE_ID, title: "Shuffle", blurb: "", question: "", count, kind: "type", choices: ["", ""],
    showSeconds: 0, group: "", concepts: [], best: null, last: null,
  } as unknown as ActivityInfo;
}

const SHUFFLE_GROUPS_KEY = (language: string) => `code-coach:brain-shuffle-groups:${language}`;

/** The headings last picked for Shuffle in this language (null: none saved, which means all). */
function readShuffleGroups(language: string): string[] | null {
  try {
    const raw = localStorage.getItem(SHUFFLE_GROUPS_KEY(language));
    const got = raw ? (JSON.parse(raw) as unknown) : null;
    return Array.isArray(got) && got.every((g) => typeof g === "string") ? got : null;
  } catch {
    return null;
  }
}

function writeShuffleGroups(language: string, groups: string[]): void {
  try {
    localStorage.setItem(SHUFFLE_GROUPS_KEY(language), JSON.stringify(groups));
  } catch {
    /* the choice just won't be remembered */
  }
}
type Miss = { item: BrainItem; given: string };

type Screen =
  | { name: "home" }
  | {
      name: "play";
      activity: ActivityInfo;
      /** The language this round is in: a round never renders under another language's screen. */
      language: BrainLanguage;
      checkId: string;
      checkLeft: string[];
      checkAges: number[];
      /** Set when the round is picked up from a snapshot rather than started. */
      resume?: RoundSnapshot;
    }
  | {
      name: "done";
      activity: ActivityInfo;
      seconds: number;
      misses: Miss[];
      total: number;
      age: number;
      best: boolean;
      checkId: string;
      checkLeft: string[];
      checkAges: number[];
    };

/** The home screen's sections: the server's heading order, then any other group, "More" last. */
export function groupActivities(
  activities: ActivityInfo[],
  order: string[] = [],
): { name: string; items: ActivityInfo[] }[] {
  const nameOf = (a: ActivityInfo) => a.group || "More";
  const names = [...order];
  for (const a of activities) if (!names.includes(nameOf(a))) names.push(nameOf(a));
  names.sort((x, y) => Number(x === "More") - Number(y === "More"));
  return names
    .map((name) => ({ name, items: activities.filter((a) => nameOf(a) === name) }))
    .filter((g) => g.items.length > 0);
}

export default function BrainDrills({
  appLanguage = "python",
  appLanguageName = "",
  onChangeLanguage,
}: {
  /** The app's language (the picker at the top): the drills follow it. */
  appLanguage?: string;
  appLanguageName?: string;
  /** Switch the app's language (the same switch the top picker makes). */
  onChangeLanguage?: (languageId: string) => void;
}) {
  const [summary, setSummary] = useState<BrainSummary | null>(null);
  const [screen, setScreen] = useState<Screen>({ name: "home" });
  const [error, setError] = useState("");
  const drillLanguage = brainLanguageFor(appLanguage);
  // Past the check below this is never null, so the rest reads as before.
  const language: BrainLanguage = drillLanguage ?? "python";

  const load = useCallback(() => {
    if (!drillLanguage) return;
    fetchBrain(language)
      .then(setSummary)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, [language, drillLanguage]);
  useEffect(load, [load]);

  // A different app language is a different set of drills: back to its home.
  useEffect(() => {
    setSummary(null);
    setScreen({ name: "home" });
  }, [language]);

  const shuffleInfo = useMemo(() => shuffleActivity(summary?.shuffle?.count ?? 16), [summary]);
  const byId = useMemo(
    () => new Map([...(summary?.activities ?? []), shuffleInfo].map((a) => [a.id, a])),
    [summary, shuffleInfo],
  );
  /** Which headings Shuffle draws from (the chips on its card); all of them unless you chose otherwise. */
  const [shuffleGroups, setShuffleGroups] = useState<string[] | null>(null);
  useEffect(() => {
    setShuffleGroups(readShuffleGroups(language));
  }, [language]);
  const allShuffleGroups = summary?.shuffle?.groups ?? [];
  const pickedGroups = (shuffleGroups ?? allShuffleGroups).filter((g) => allShuffleGroups.includes(g));
  const toggleShuffleGroup = useCallback(
    (g: string) => {
      const now = pickedGroups.includes(g) ? pickedGroups.filter((x) => x !== g) : [...pickedGroups, g];
      // Never none: turning the last one off leaves it on.
      if (now.length === 0) return;
      setShuffleGroups(now);
      writeShuffleGroups(language, now);
    },
    [pickedGroups, language],
  );

  // A round saved for this language, offered on the home screen. Coming back to the Brain Drills tab resumes it
  // straight away (below); this is for arriving at the home screen some other way (the language picker).
  const homeResume = useMemo(() => {
    if (screen.name !== "home" || !summary || !drillLanguage || summary.language !== language) return null;
    const snap = loadResumable({ language, activities: [...summary.activities, shuffleInfo], now: Date.now() });
    const act = snap ? byId.get(snap.activityId) : undefined;
    return snap && act ? { snap, act } : null;
  }, [screen.name, summary, drillLanguage, language, byId, shuffleInfo]);

  const resumeRound = useCallback(
    (snap: RoundSnapshot, activity: ActivityInfo) => {
      setScreen({
        name: "play", activity, language, checkId: snap.checkId, checkLeft: snap.checkLeft, checkAges: snap.checkAges,
        resume: snap,
      });
    },
    [language],
  );

  // Back on the Brain Drills tab with a round saved: straight into it, before the home screen paints. Only the first
  // load of the first language: a language picked later shows its home with a "Resume" button instead.
  const firstLanguage = useRef(language);
  const autoResumed = useRef(false);
  useLayoutEffect(() => {
    if (!summary || !drillLanguage || summary.language !== language) return;
    if (autoResumed.current || language !== firstLanguage.current) return;
    autoResumed.current = true;
    const snap = loadResumable({ language, activities: [...summary.activities, shuffleInfo], now: Date.now() });
    const act = snap ? byId.get(snap.activityId) : undefined;
    if (snap && act) resumeRound(snap, act);
  }, [summary, drillLanguage, language, byId, resumeRound, shuffleInfo]);

  const start = useCallback(
    (activity: ActivityInfo) => {
      // Starting something else replaces a saved round (it asks nothing).
      clearSnapshot(language);
      setScreen({ name: "play", activity, language, checkId: "", checkLeft: [], checkAges: [] });
    },
    [language],
  );

  const startCheck = useCallback(() => {
    if (!summary) return;
    const [first, ...rest] = summary.check;
    const activity = byId.get(first);
    if (!activity) return;
    const checkId = `${summary.today}/${Date.now()}`;
    clearSnapshot(language);
    setScreen({ name: "play", activity, language, checkId, checkLeft: rest, checkAges: [] });
  }, [summary, byId, language]);

  const finished = useCallback(
    async (
      activity: ActivityInfo,
      seconds: number,
      misses: Miss[],
      total: number,
      s: Screen,
      final: RoundSnapshot | null,
    ) => {
      if (s.name !== "play") return;
      try {
        const got = await postBrainResult({
          activity: activity.id, seconds, errors: misses.length, total, checkId: s.checkId, language,
          // A Shuffle round's age is held to the par times of the activities its questions came from.
          activities: activity.id === SHUFFLE_ID ? (final?.items ?? []).map((i) => i.activity ?? "") : undefined,
        });
        // Momentum, apart from the stamps and code age above: the round, and the whole check.
        award("brain_round", `${activity.id}:${s.checkId || "solo"}:${Date.now().toString(36)}`);
        if (s.checkId && s.checkLeft.length === 0) award("check_age", s.checkId);
        setScreen({
          name: "done", activity, seconds, misses, total, age: got.age, best: got.best,
          checkId: s.checkId, checkLeft: s.checkLeft, checkAges: [...s.checkAges, got.age],
        });
        load();
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
        // The result did not go through: keep the finished round, so "Resume" offers its Finish again.
        if (final) saveSnapshot(final);
        setScreen({ name: "home" });
      }
    },
    [load, language],
  );

  // The app's language has no drills yet: say so, and offer the languages that do
  // (it switches the app's language, the same switch as the picker at the top).
  if (!drillLanguage) {
    return (
      <div className="brain-wrap">
        <header className="brain-head">
          <div>
            <h2>Brain Drills</h2>
            <p className="brain-sub">
              There are no Brain Drills for {appLanguageName || languageLabel(appLanguage)} yet. They follow the language
              picked at the top of the app, and cover these so far:
            </p>
            <div className="brain-lang" role="group" aria-label="Languages with drills">
              {DRILL_APP_LANGUAGES.map((l) => (
                <button
                  key={l.id}
                  type="button"
                  className="brain-lang-btn"
                  onClick={() => onChangeLanguage?.(l.id)}
                  disabled={!onChangeLanguage}
                >
                  Switch to {l.name}
                </button>
              ))}
            </div>
          </div>
        </header>
      </div>
    );
  }

  if (error && !summary) return <div className="lessons-empty">Could not load Brain Drills: {error}</div>;
  if (!summary) return <div className="lessons-empty">Loading…</div>;

  // (A round of another language is not drawn: the effect above is about to send the screen home, and the Round that
  // was on screen has already saved itself under its own language when it unmounted.)
  if (screen.name === "play" && screen.language === language) {
    return (
      <Round
        key={`${screen.language}-${screen.activity.id}-${screen.checkId}`}
        activity={screen.activity}
        language={language}
        checkId={screen.checkId}
        checkLeft={screen.checkLeft}
        checkAges={screen.checkAges}
        checkStep={screen.checkId ? summary.check.length - screen.checkLeft.length : 0}
        checkSize={summary.check.length}
        resume={screen.resume}
        activities={byId}
        shuffleGroups={pickedGroups}
        onQuit={() => setScreen({ name: "home" })}
        onDone={(seconds, misses, total, final) =>
          void finished(screen.activity, seconds, misses, total, screen, final)
        }
      />
    );
  }

  if (screen.name === "done") {
    const next = screen.checkLeft.length ? byId.get(screen.checkLeft[0]) : undefined;
    const checkDone = screen.checkId && !screen.checkLeft.length;
    const checkAge = checkDone
      ? Math.round(screen.checkAges.reduce((a, b) => a + b, 0) / screen.checkAges.length)
      : 0;
    return (
      <Done
        screen={screen}
        checkAge={checkAge}
        next={next}
        onNext={() =>
          next &&
          setScreen({
            name: "play", activity: next, language, checkId: screen.checkId,
            checkLeft: screen.checkLeft.slice(1), checkAges: screen.checkAges,
          })
        }
        onAgain={() => start(screen.activity)}
        onHome={() => setScreen({ name: "home" })}
      />
    );
  }

  const latest = summary.checkAges[summary.checkAges.length - 1];
  return (
    <div className="brain-wrap">
      {homeResume ? (
        <section className="brain-resume" aria-label="A round in progress">
          <button
            type="button"
            className="ws-btn primary brain-resume-btn"
            data-testid="brain-resume"
            onClick={() => resumeRound(homeResume.snap, homeResume.act)}
          >
            {resumeLabel(homeResume.snap, homeResume.act.title)}
          </button>
          <span className="brain-resume-note">Saved just as you left it; the clock was not running while you were away.</span>
        </section>
      ) : null}
      <header className="brain-head">
        <div>
          <h2>Brain Drills</h2>
          <p className="brain-sub">
            Quick {LANGUAGE_NAMES[language]} reflexes, timed. Your code age: 20 is as sharp as it gets.
          </p>
          <p className="brain-lang-note">The language follows the picker at the top of the app.</p>
        </div>
        <div className="brain-age-box">
          <span className="brain-age-label">Code age</span>
          <span className="brain-age">{latest ? latest.age : "–"}</span>
          <button type="button" className="ws-btn primary" onClick={startCheck}>
            {latest ? "Check again" : "Take the check"}
          </button>
        </div>
      </header>

      <section className="brain-row">
        <div className="brain-stamps" aria-label="Days trained">
          {summary.stamps.map((s) => (
            <span
              key={s.day}
              className={`brain-stamp${s.trained ? " on" : ""}${s.day === summary.today ? " today" : ""}`}
              title={`${s.day}${s.trained ? " - trained" : ""}`}
            />
          ))}
        </div>
        <p className="brain-streak">
          {summary.streak ? `${summary.streak}-day streak` : "Train today to start a streak"}
          {summary.trainedToday ? " · today's stamp is in" : ""}
        </p>
      </section>

      {summary.checkAges.length > 1 ? <AgeChart points={summary.checkAges} /> : null}

      {allShuffleGroups.length ? (
        <section className="brain-shuffle" aria-labelledby="brain-shuffle-title">
          <div className="brain-shuffle-main">
            <h3 className="brain-group-title" id="brain-shuffle-title">
              Shuffle
            </h3>
            <p className="brain-shuffle-blurb">
              {summary.shuffle?.count ?? 16} questions from all over the drills you pick, one after another.
            </p>
            <div className="brain-shuffle-groups" role="group" aria-label="Which drills to shuffle">
              {allShuffleGroups.map((g) => {
                const on = pickedGroups.includes(g);
                return (
                  <button
                    key={g}
                    type="button"
                    className={on ? "ws-btn brain-chip on" : "ws-btn brain-chip"}
                    aria-pressed={on}
                    onClick={() => toggleShuffleGroup(g)}
                    title={on && pickedGroups.length === 1 ? "At least one stays on" : undefined}
                  >
                    {g}
                  </button>
                );
              })}
              {pickedGroups.length < allShuffleGroups.length ? (
                <button
                  type="button"
                  className="ws-btn brain-chip brain-chip-all"
                  onClick={() => {
                    setShuffleGroups(allShuffleGroups);
                    writeShuffleGroups(language, allShuffleGroups);
                  }}
                >
                  All
                </button>
              ) : null}
            </div>
          </div>
          <div className="brain-shuffle-side">
            <button type="button" className="ws-btn primary" data-testid="brain-shuffle-start" onClick={() => start(shuffleInfo)}>
              Start shuffle
            </button>
            <span className="brain-card-best">
              {summary.shuffle?.best
                ? `best: age ${summary.shuffle.best.age} · ${summary.shuffle.best.seconds.toFixed(1)}s`
                : "not tried yet"}
            </span>
          </div>
        </section>
      ) : null}

      <div className="brain-groups">
        {groupActivities(summary.activities, summary.groups).map((g) => {
          const slug = `brain-group-${g.name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
          return (
            <section key={g.name} className="brain-group" aria-labelledby={slug}>
              <h3 className="brain-group-title" id={slug}>
                {g.name}
                <span className="brain-group-count">{g.items.length}</span>
              </h3>
              <div className="brain-grid">
                {g.items.map((a) => (
                  <button key={a.id} type="button" className="brain-card" data-activity={a.id} onClick={() => start(a)}>
                    <strong>{a.title}</strong>
                    <span>{a.blurb}</span>
                    <span className="brain-card-best">
                      {a.best ? `best: age ${a.best.age} · ${a.best.seconds.toFixed(1)}s` : "not tried yet"}
                    </span>
                    {a.last ? (
                      <span className="brain-card-last">{`last: age ${a.last.age} · ${a.last.seconds.toFixed(1)}s`}</span>
                    ) : null}
                  </button>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}

/**
 * One activity, start to finish: countdown, questions, then onDone.
 *
 * You can go Back, open the question picker and jump anywhere (see
 * lib/brainRound.ts for the rules): an answered question is shown read-only,
 * with its code to run and explain, and the clock waits while you look.
 */
function Round({
  activity,
  language,
  checkId,
  checkLeft,
  checkAges,
  checkStep,
  checkSize,
  resume,
  activities,
  shuffleGroups,
  onQuit,
  onDone,
}: {
  activity: ActivityInfo;
  /** Every activity by id: a Shuffle round's questions each use the one they came from. */
  activities: Map<string, ActivityInfo>;
  /** A Shuffle round: the headings to draw from. */
  shuffleGroups: string[];
  language: BrainLanguage;
  /** The Code age check this round belongs to (blank for a single activity); kept in the snapshot. */
  checkId: string;
  checkLeft: string[];
  checkAges: number[];
  checkStep: number;
  checkSize: number;
  /** A saved round to pick up: its questions, answers, typed text and clock; no fetch, no countdown. */
  resume?: RoundSnapshot;
  onQuit: () => void;
  /** `final` is the finished round's snapshot, handed back so a failed post can keep it for another try. */
  onDone: (seconds: number, misses: Miss[], total: number, final: RoundSnapshot | null) => void;
}) {
  const [items, setItems] = useState<BrainItem[] | null>(resume?.items ?? null);
  const [count, setCount] = useState(resume ? 0 : 3);
  const [rs, setRs] = useState<RoundState>(() => resume?.rs ?? newRound(0));
  const [typed, setTyped] = useState(resume?.typed ?? "");
  const [flash, setFlash] = useState(false);
  const [showing, setShowing] = useState(false);
  const [elapsed, setElapsed] = useState(resume?.elapsed ?? 0);
  const [picker, setPicker] = useState(false);
  // "Picked up where you left off": a quiet note for a few seconds after a resume.
  const [resumedNote, setResumedNote] = useState(!!resume);
  // The resumed clock reads exactly what it read when you left, and runs on from now (the time away is not in it).
  const [seedClock] = useState<Clock | null>(() =>
    resume ? clockFromElapsed(resume.elapsed, performance.now(), resume.rs) : null,
  );
  const clock = useRef<Clock | null>(seedClock);
  // Set while a right answer's flash is on screen, so nothing else moves you.
  const busy = useRef(false);
  const finishing = useRef(false);
  // This round's own name, for Momentum: every round's questions are new, so each
  // answer is its own thing to be paid for once.
  // A resumed round keeps its id, so an answer given before leaving is never paid for a second time.
  const roundId = useRef(resume?.roundId ?? Date.now().toString(36));
  // A fast typist's keystrokes must not skip a miss before it has been read.
  const guard = useRef(0);
  const input = useRef<HTMLInputElement | null>(null);
  const nextBtn = useRef<HTMLButtonElement | null>(null);
  const questionsBtn = useRef<HTMLButtonElement | null>(null);
  // Variable Recall: leaving mid-answer (the variables already hidden) comes back mid-answer, not shown again;
  // leaving during "Remember these" shows them again from the start. This is the question that skips its show phase.
  const noShowFor = useRef<number | null>(resume && !resume.showing ? resume.rs.index : null);
  // Saving: `live` is what the latest render held; `pending` is a right answer's state during its 120 ms flash
  // (the answer is already given, the screen has not moved yet); `ended` is set when the round is over (finished or
  // quit), after which nothing may save it again.
  const live = useRef({ items, rs, typed, showing, count });
  live.current = { items, rs, typed, showing, count };
  const pending = useRef<RoundState | null>(null);
  const ended = useRef(false);

  const snapshotNow = useCallback(
    (state?: RoundState): RoundSnapshot | null => {
      const L = live.current;
      if (!L.items || L.count > 0) return null;
      const rsNow = state ?? pending.current ?? L.rs;
      return makeSnapshot({
        language, activityId: activity.id, checkId, checkLeft, checkAges, roundId: roundId.current,
        items: L.items, rs: rsNow, typed: rsNow === L.rs ? L.typed : "", clock: clock.current, showing: L.showing,
        now: Date.now(), perfNow: performance.now(),
      });
    },
    [language, activity.id, checkId, checkLeft, checkAges],
  );
  const persist = useCallback(() => {
    if (ended.current) return;
    const snap = snapshotNow();
    if (snap) saveSnapshot(snap);
  }, [snapshotNow]);

  // Save on every meaningful change (an answer, a move, the countdown ending), the typed text a beat after you stop,
  // when the page is hidden or reloaded, and when this screen unmounts (leaving the tab).
  useEffect(() => {
    persist();
  }, [rs, count, items, persist]);
  useEffect(() => {
    const id = window.setTimeout(persist, 300);
    return () => window.clearTimeout(id);
  }, [typed, persist]);
  useEffect(() => {
    window.addEventListener("pagehide", persist);
    return () => {
      window.removeEventListener("pagehide", persist);
      persist();
    };
  }, [persist]);

  useEffect(() => {
    if (!resumedNote) return;
    const id = window.setTimeout(() => setResumedNote(false), 3000);
    return () => window.clearTimeout(id);
  }, [resumedNote]);

  useEffect(() => {
    if (resume) return; // the questions are the saved ones: never fetched again
    let alive = true;
    (activity.id === SHUFFLE_ID ? fetchBrainShuffle(language, shuffleGroups) : fetchBrainRound(activity.id, language)).then((r) => {
      if (!alive) return;
      setItems(r.items);
      setRs(newRound(r.items.length));
    });
    return () => {
      alive = false;
    };
  }, [activity.id, language]); // eslint-disable-line react-hooks/exhaustive-deps

  // 3, 2, 1 - then the clock starts.
  useEffect(() => {
    if (!items || count <= 0) return;
    const id = window.setTimeout(() => setCount((c) => c - 1), 500);
    return () => window.clearTimeout(id);
  }, [items, count]);
  useEffect(() => {
    if (count === 0 && items && !clock.current) clock.current = clockStart(performance.now());
  }, [count, items]);
  useEffect(() => {
    if (count > 0) return;
    const id = window.setInterval(() => {
      const c = clock.current;
      if (c && c.pausedAt === null) setElapsed(clockElapsed(c, performance.now()));
    }, 100);
    return () => window.clearInterval(id);
  }, [count]);

  const total = items?.length ?? 0;
  const item = items?.[rs.index];
  const record = rs.answers[rs.index] ?? null;
  const reviewing = record !== null;
  const answered = answeredCount(rs);
  // The activity this question belongs to: the round's own, or in a Shuffle the one the question came from.
  const cur = (item?.activity && activities.get(item.activity)) || activity;

  // Variable Recall: show what to remember, then hide it. Landing on an
  // unanswered one - by answering, Back or the picker - shows it again; an
  // answered one is only reviewed, with the variables in view.
  useEffect(() => {
    const skip = noShowFor.current === rs.index;
    if (!skip) noShowFor.current = null;
    if (count > 0 || !item?.show || reviewing || skip) {
      setShowing(false);
      return;
    }
    setShowing(true);
    const id = window.setTimeout(() => setShowing(false), activity.showSeconds * 1000);
    return () => window.clearTimeout(id);
  }, [count, rs.index, reviewing, item?.show, activity.showSeconds]);

  useEffect(() => {
    if (count !== 0 || picker) return;
    if (reviewing) nextBtn.current?.focus();
    else if (!showing) input.current?.focus();
  }, [count, showing, rs.index, reviewing, picker]);

  // Move to a new round state, keeping the clock in line with it: stopped
  // while you look at an answered question, running on an open one.
  const commit = useCallback((next: RoundState) => {
    const now = performance.now();
    pending.current = null;
    setRs(next);
    setTyped("");
    setFlash(false);
    if (clock.current) {
      clock.current = clockFor(clock.current, next, now);
      setElapsed(clockElapsed(clock.current, now));
    }
  }, []);

  const finish = useCallback(
    (state: RoundState) => {
      if (!items || finishing.current || !isComplete(state)) return;
      finishing.current = true;
      const seconds = clock.current ? clockElapsed(clock.current, performance.now()) : 0;
      // The round is over: nothing saves it again. The caller gets the finished round's snapshot, to keep only if
      // the result cannot be posted (so there is something to Finish again); a posted round leaves nothing behind.
      const final = snapshotNow(state);
      ended.current = true;
      clearSnapshot(language);
      onDone(seconds, missesOf(state, items), items.length, final);
    },
    [items, onDone, snapshotNow, language],
  );

  // Quit (the button or Escape) ends the round for good: the saved copy goes too.
  const quit = useCallback(() => {
    ended.current = true;
    clearSnapshot(language);
    onQuit();
  }, [language, onQuit]);

  const go = useCallback(
    (i: number) => {
      setPicker(false);
      if (!items || count > 0 || busy.current || finishing.current || i < 0) return;
      if (i !== rs.index) commit(jumpTo(rs, i));
    },
    [items, count, rs, commit],
  );

  const back = useCallback(() => go(backTarget(rs)), [go, rs]);

  // Next: on from the question you are reading; from the end of a finished
  // round, that is the end of the round.
  const forward = useCallback(() => {
    if (!items || busy.current) return;
    if (isComplete(rs) && rs.index + 1 >= rs.answers.length) {
      finish(rs);
      return;
    }
    const t = forwardTarget(rs);
    if (t >= 0) go(t);
  }, [items, rs, go, finish]);

  const answer = useCallback(
    (given: string) => {
      if (!items || !item || busy.current || showing || reviewing || count > 0) return;
      const right = sameAnswer(given, item.answer, language);
      const next = recordAnswer(rs, rs.index, given, right);
      if (right) {
        award("brain_item", `${cur.id}:${roundId.current}:${rs.index}`);
        busy.current = true;
        setFlash(true);
        // Leaving inside this 120 ms must still keep the answer just given.
        pending.current = isComplete(next) ? next : jumpTo(next, nextOpen(next, rs.index));
        window.setTimeout(() => {
          busy.current = false;
          if (isComplete(next)) finish(next);
          else commit(jumpTo(next, nextOpen(next, rs.index)));
        }, 120);
        return;
      }
      // Wrong: it is now an answered question, shown with the right answer
      // until you say you have read it - and the clock is stopped, so
      // reading it costs no score.
      guard.current = performance.now() + 300;
      commit(next);
    },
    [items, item, rs, showing, reviewing, count, finish, commit, cur.id, language],
  );

  const onKeyRef = useRef<(e: KeyboardEvent) => void>(() => {});
  onKeyRef.current = (e: KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      if (picker) {
        setPicker(false);
        questionsBtn.current?.focus();
      } else {
        quit();
      }
      return;
    }
    if (picker || count > 0) return;
    if (e.altKey && (e.key === "ArrowLeft" || e.key === "ArrowRight")) {
      e.preventDefault();
      if (e.key === "ArrowLeft") back();
      else forward();
      return;
    }
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    if (reviewing) {
      if (e.repeat || (e.key !== "Enter" && e.key !== " ")) return;
      // On some other button, Enter or Space is that button's.
      const el = e.target as HTMLElement | null;
      const control = el?.closest?.("button, a, input, select, textarea");
      if (control && !(control as HTMLElement).dataset.primary) return;
      e.preventDefault();
      if (performance.now() >= guard.current) forward();
      return;
    }
    if (cur.kind !== "pick") return;
    const left = e.key === "ArrowLeft" || e.key.toLowerCase() === "f";
    const right = e.key === "ArrowRight" || e.key.toLowerCase() === "j";
    if (left || right) {
      e.preventDefault();
      answer(cur.choices[left ? 0 : 1]);
    }
  };
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => onKeyRef.current(e);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const ready = !!items && count === 0;
  const lastOne = !!items && isComplete(rs) && rs.index + 1 >= rs.answers.length;
  const skipTo = reviewing && !isComplete(rs) ? resumeTarget(rs) : -1;
  const plain = forwardTarget(rs);

  return (
    <div className="brain-wrap brain-play">
      <div className="brain-play-top">
        <strong>{activity.title}</strong>
        {cur !== activity ? <span className="brain-from">{cur.title}</span> : null}
        {checkSize && checkStep ? <span className="brain-check-step">Code age check · {checkStep} of {checkSize}</span> : null}
        <span className="brain-progress" title={`${answered} of ${total} answered`}>
          {total ? `${rs.index + 1} / ${total}` : ""}
          {answered ? ` · ${answered} answered` : ""}
        </span>
        <span className="brain-clock">
          {count > 0 ? "" : `${elapsed.toFixed(1)}s`}
          {ready && reviewing && !flash ? " · paused" : ""}
        </span>
        <div className="brain-play-nav">
          <button
            type="button"
            className="ws-btn"
            onClick={back}
            disabled={!ready || backTarget(rs) < 0}
            title="Back to the previous question (Alt+Left)"
          >
            ← Back
          </button>
          <button
            type="button"
            className="ws-btn"
            ref={questionsBtn}
            onClick={() => setPicker(true)}
            disabled={!ready}
            aria-haspopup="dialog"
            title="All the questions in this round - jump to any"
          >
            Questions
          </button>
          <button type="button" className="ws-btn" onClick={quit} title="Esc">
            Quit
          </button>
        </div>
      </div>
      {resumedNote ? (
        <p className="brain-resumed" role="status">
          Picked up where you left off
        </p>
      ) : null}
      {!items ? (
        <div className="brain-stage">Getting ready…</div>
      ) : count > 0 ? (
        <div className="brain-stage brain-count">{count}</div>
      ) : (
        <>
          <div className={`brain-stage${flash ? " ok" : reviewing ? (record?.right ? " ok" : " bad") : ""}`}>
            {reviewing && item?.show ? (
              <>
                <p className="brain-question">You were shown:</p>
                <pre className="brain-code">{item.show}</pre>
              </>
            ) : null}
            <p className="brain-question">{showing ? "Remember these:" : cur.question}</p>
            <pre className="brain-code">{showing ? item?.show : item?.prompt}</pre>
            {reviewing && item && record ? (
              <div className={`brain-miss${record.right ? " brain-hit" : ""}`} role="status">
                <p className="brain-correct">{record.right ? `Right: ${item.answer}` : `It's ${item.answer}`}</p>
                {record.right && record.given.trim() === item.answer ? null : (
                  <p className="brain-given">You said {record.given || "nothing"}</p>
                )}
                {item.explain ? <p className="brain-why">{item.explain}</p> : null}
                {record.right ? null : (
                  <QuestionWords key={`${rs.index}-${cur.id}`} activityId={cur.id} language={language} scope="miss" />
                )}
                <div className="brain-review-actions">
                  <button type="button" className="ws-btn brain-go" onClick={forward} ref={nextBtn} data-primary="true">
                    {lastOne ? "Finish (Enter)" : plain >= 0 ? `Next: ${plain + 1} (Enter)` : "Next (Enter)"}
                  </button>
                  {skipTo >= 0 && skipTo !== plain ? (
                    <button type="button" className="ws-btn" onClick={() => go(skipTo)}>
                      Next unanswered: {skipTo + 1}
                    </button>
                  ) : null}
                </div>
                <span className="brain-paused">clock paused</span>
              </div>
            ) : showing ? null : cur.kind === "type" ? (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (typed.trim()) answer(typed);
                }}
              >
                <input
                  ref={input}
                  className="brain-input"
                  value={typed}
                  onChange={(e) => setTyped(e.target.value)}
                  autoComplete="off"
                  spellCheck={false}
                  aria-label="Your answer"
                />
              </form>
            ) : (
              <div className="brain-picks">
                {cur.choices.map((choice, k) => (
                  <button key={choice} type="button" className="ws-btn brain-pick" onClick={() => answer(choice)}>
                    {k === 0 ? "← " : ""}
                    {choice}
                    {k === 1 ? " →" : ""}
                  </button>
                ))}
              </div>
            )}
          </div>
          {item ? (
            <BrainTools
              key={rs.index}
              activityId={cur.id}
              item={item}
              language={language}
              unlocked={reviewing}
            />
          ) : null}
        </>
      )}
      {picker && items ? (
        <BrainPicker
          state={rs}
          onPick={go}
          onClose={() => {
            setPicker(false);
            questionsBtn.current?.focus();
          }}
        />
      ) : null}
    </div>
  );
}

function Done({
  screen,
  checkAge,
  next,
  onNext,
  onAgain,
  onHome,
}: {
  screen: Extract<Screen, { name: "done" }>;
  checkAge: number;
  next: ActivityInfo | undefined;
  onNext: () => void;
  onAgain: () => void;
  onHome: () => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (next) onNext();
        else onAgain();
      } else if (e.key === "Escape") {
        onHome();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [next, onNext, onAgain, onHome]);

  return (
    <div className="brain-wrap brain-done">
      <h2>{screen.activity.title}</h2>
      <div className="brain-done-row">
        <div className="brain-age-box">
          <span className="brain-age-label">This round</span>
          <span className="brain-age">{screen.age}</span>
          {screen.best ? <span className="brain-best">A new best!</span> : null}
        </div>
        <div className="brain-stats">
          <span>{screen.seconds.toFixed(1)} seconds</span>
          <span>
            {screen.total - screen.misses.length} of {screen.total} right
          </span>
        </div>
        {checkAge ? (
          <div className="brain-age-box check">
            <span className="brain-age-label">Your code age</span>
            <span className="brain-age">{checkAge}</span>
          </div>
        ) : null}
      </div>
      {screen.misses.length ? (
        <section className="brain-misses">
          <h3>Worth another look</h3>
          {screen.misses.map((m, i) => (
            <div key={i} className="brain-miss">
              <pre>{m.item.prompt}</pre>
              <span>
                You said <code>{m.given || "nothing"}</code>, it's <code>{m.item.answer}</code>.{" "}
                {m.item.explain}
              </span>
            </div>
          ))}
        </section>
      ) : (
        <p className="brain-perfect">Not a single mistake.</p>
      )}
      <div className="brain-actions">
        {next ? (
          <button type="button" className="ws-btn primary" onClick={onNext}>
            Next: {next.title} (Enter)
          </button>
        ) : (
          <button type="button" className="ws-btn primary" onClick={onAgain}>
            Again (Enter)
          </button>
        )}
        <button type="button" className="ws-btn" onClick={onHome}>
          Home (Esc)
        </button>
      </div>
    </div>
  );
}

/** The code age checks, day by day: lower is better, so lower is drawn higher up. */
function AgeChart({ points }: { points: { day: string; age: number }[] }) {
  const w = 560;
  const h = 120;
  const x = (i: number) => 20 + (i * (w - 40)) / Math.max(1, points.length - 1);
  const y = (age: number) => 10 + ((age - 20) / 60) * (h - 20);
  const line = points.map((p, i) => `${x(i)},${y(p.age)}`).join(" ");
  return (
    <svg className="brain-chart" viewBox={`0 0 ${w} ${h}`} role="img" aria-label="Code age by day">
      <line x1="20" x2={w - 20} y1={y(20)} y2={y(20)} className="brain-chart-ref" />
      <line x1="20" x2={w - 20} y1={y(80)} y2={y(80)} className="brain-chart-ref" />
      <polyline points={line} className="brain-chart-line" />
      {points.map((p, i) => (
        <circle key={p.day} cx={x(i)} cy={y(p.age)} r="3.5" className="brain-chart-dot">
          <title>{`${p.day}: ${p.age}`}</title>
        </circle>
      ))}
    </svg>
  );
}
