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
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchBrain, fetchBrainRound, postBrainResult } from "../api";
import { award } from "../lib/momentum";
import {
  answeredCount,
  backTarget,
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
  type BrainItem,
  type Clock,
  type RoundState,
} from "../lib/brainRound";
import "../styles/brain.css";
import BrainPicker from "./BrainPicker";
import BrainTools from "./BrainTools";

export type BrainLanguage = "javascript" | "python";
const LANGUAGE_NAMES: Record<BrainLanguage, string> = { javascript: "JavaScript", python: "Python" };

function savedLanguage(): BrainLanguage {
  try {
    return window.localStorage.getItem("brain-language") === "python" ? "python" : "javascript";
  } catch {
    return "javascript";
  }
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
  best: Result | null;
  last: Result | null;
};
export type BrainSummary = {
  today: string;
  language: BrainLanguage;
  languages: BrainLanguage[];
  activities: ActivityInfo[];
  check: string[];
  stamps: { day: string; trained: boolean }[];
  streak: number;
  checkAges: { day: string; age: number }[];
  trainedToday: boolean;
};
export type { BrainItem };
type Miss = { item: BrainItem; given: string };

type Screen =
  | { name: "home" }
  | { name: "play"; activity: ActivityInfo; checkId: string; checkLeft: string[]; checkAges: number[] }
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

/** Forgive what a person types: spaces, case, and quotes round a string. */
function same(given: string, answer: string): boolean {
  // Python prints lists as "[1, 2]": spaces inside brackets don't matter.
  const clean = (s: string) => {
    const t = s.trim().replace(/^(['"`])(.*)\1$/s, "$2").trim().toLowerCase();
    return /^[[({]/.test(t) ? t.replace(/\s+/g, "") : t;
  };
  return clean(given) === clean(answer);
}

export default function BrainDrills() {
  const [summary, setSummary] = useState<BrainSummary | null>(null);
  const [screen, setScreen] = useState<Screen>({ name: "home" });
  const [error, setError] = useState("");
  const [language, setLanguage] = useState<BrainLanguage>(savedLanguage);

  const load = useCallback(() => {
    fetchBrain(language)
      .then(setSummary)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, [language]);
  useEffect(load, [load]);

  const pickLanguage = useCallback((next: BrainLanguage) => {
    setLanguage(next);
    try {
      window.localStorage.setItem("brain-language", next);
    } catch {
      /* a remembered choice is only a convenience */
    }
  }, []);

  const byId = useMemo(() => new Map((summary?.activities ?? []).map((a) => [a.id, a])), [summary]);

  const start = useCallback((activity: ActivityInfo) => {
    setScreen({ name: "play", activity, checkId: "", checkLeft: [], checkAges: [] });
  }, []);

  const startCheck = useCallback(() => {
    if (!summary) return;
    const [first, ...rest] = summary.check;
    const activity = byId.get(first);
    if (!activity) return;
    const checkId = `${summary.today}/${Date.now()}`;
    setScreen({ name: "play", activity, checkId, checkLeft: rest, checkAges: [] });
  }, [summary, byId]);

  const finished = useCallback(
    async (activity: ActivityInfo, seconds: number, misses: Miss[], total: number, s: Screen) => {
      if (s.name !== "play") return;
      try {
        const got = await postBrainResult({
          activity: activity.id, seconds, errors: misses.length, total, checkId: s.checkId, language,
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
        setScreen({ name: "home" });
      }
    },
    [load, language],
  );

  if (error && !summary) return <div className="lessons-empty">Could not load Brain Drills: {error}</div>;
  if (!summary) return <div className="lessons-empty">Loading…</div>;

  if (screen.name === "play") {
    return (
      <Round
        key={`${screen.activity.id}-${screen.checkId}`}
        activity={screen.activity}
        language={language}
        checkStep={screen.checkId ? summary.check.length - screen.checkLeft.length : 0}
        checkSize={summary.check.length}
        onQuit={() => setScreen({ name: "home" })}
        onDone={(seconds, misses, total) => void finished(screen.activity, seconds, misses, total, screen)}
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
            name: "play", activity: next, checkId: screen.checkId,
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
      <header className="brain-head">
        <div>
          <h2>Brain Drills</h2>
          <p className="brain-sub">
            Quick {LANGUAGE_NAMES[language]} reflexes, timed. Your code age: 20 is as sharp as it gets.
          </p>
          <div className="brain-lang" role="group" aria-label="Language">
            {(summary.languages ?? ["javascript", "python"]).map((l) => (
              <button
                key={l}
                type="button"
                className={`brain-lang-btn${l === language ? " on" : ""}`}
                aria-pressed={l === language}
                onClick={() => pickLanguage(l)}
              >
                {LANGUAGE_NAMES[l]}
              </button>
            ))}
          </div>
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

      <section className="brain-grid">
        {summary.activities.map((a) => (
          <button key={a.id} type="button" className="brain-card" onClick={() => start(a)}>
            <strong>{a.title}</strong>
            <span>{a.blurb}</span>
            <span className="brain-card-best">
              {a.best ? `best: age ${a.best.age} · ${a.best.seconds.toFixed(1)}s` : "not tried yet"}
            </span>
          </button>
        ))}
      </section>
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
  checkStep,
  checkSize,
  onQuit,
  onDone,
}: {
  activity: ActivityInfo;
  language: BrainLanguage;
  checkStep: number;
  checkSize: number;
  onQuit: () => void;
  onDone: (seconds: number, misses: Miss[], total: number) => void;
}) {
  const [items, setItems] = useState<BrainItem[] | null>(null);
  const [count, setCount] = useState(3);
  const [rs, setRs] = useState<RoundState>(() => newRound(0));
  const [typed, setTyped] = useState("");
  const [flash, setFlash] = useState(false);
  const [showing, setShowing] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [picker, setPicker] = useState(false);
  const clock = useRef<Clock | null>(null);
  // Set while a right answer's flash is on screen, so nothing else moves you.
  const busy = useRef(false);
  const finishing = useRef(false);
  // This round's own name, for Momentum: every round's questions are new, so each
  // answer is its own thing to be paid for once.
  const roundId = useRef(Date.now().toString(36));
  // A fast typist's keystrokes must not skip a miss before it has been read.
  const guard = useRef(0);
  const input = useRef<HTMLInputElement | null>(null);
  const nextBtn = useRef<HTMLButtonElement | null>(null);
  const questionsBtn = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    let alive = true;
    fetchBrainRound(activity.id, language).then((r) => {
      if (!alive) return;
      setItems(r.items);
      setRs(newRound(r.items.length));
    });
    return () => {
      alive = false;
    };
  }, [activity.id, language]);

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

  // Variable Recall: show what to remember, then hide it. Landing on an
  // unanswered one - by answering, Back or the picker - shows it again; an
  // answered one is only reviewed, with the variables in view.
  useEffect(() => {
    if (count > 0 || !item?.show || reviewing) {
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
      onDone(seconds, missesOf(state, items), items.length);
    },
    [items, onDone],
  );

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
      const right = same(given, item.answer);
      const next = recordAnswer(rs, rs.index, given, right);
      if (right) {
        award("brain_item", `${activity.id}:${roundId.current}:${rs.index}`);
        busy.current = true;
        setFlash(true);
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
    [items, item, rs, showing, reviewing, count, finish, commit, activity.id],
  );

  const onKeyRef = useRef<(e: KeyboardEvent) => void>(() => {});
  onKeyRef.current = (e: KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      if (picker) {
        setPicker(false);
        questionsBtn.current?.focus();
      } else {
        onQuit();
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
    if (activity.kind !== "pick") return;
    const left = e.key === "ArrowLeft" || e.key.toLowerCase() === "f";
    const right = e.key === "ArrowRight" || e.key.toLowerCase() === "j";
    if (left || right) {
      e.preventDefault();
      answer(activity.choices[left ? 0 : 1]);
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
          <button type="button" className="ws-btn" onClick={onQuit} title="Esc">
            Quit
          </button>
        </div>
      </div>
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
            <p className="brain-question">{showing ? "Remember these:" : activity.question}</p>
            <pre className="brain-code">{showing ? item?.show : item?.prompt}</pre>
            {reviewing && item && record ? (
              <div className={`brain-miss${record.right ? " brain-hit" : ""}`} role="status">
                <p className="brain-correct">{record.right ? `Right: ${item.answer}` : `It's ${item.answer}`}</p>
                {record.right && record.given.trim() === item.answer ? null : (
                  <p className="brain-given">You said {record.given || "nothing"}</p>
                )}
                {item.explain ? <p className="brain-why">{item.explain}</p> : null}
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
            ) : showing ? null : activity.kind === "type" ? (
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
                {activity.choices.map((choice, k) => (
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
              activityId={activity.id}
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
