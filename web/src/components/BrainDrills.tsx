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
 * arrows (or F/J) for the two-way ones, Esc to leave a round.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchBrain, fetchBrainRound, postBrainResult } from "../api";
import "../styles/brain.css";

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
export type BrainItem = { prompt: string; answer: string; explain: string; show: string };
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

/** One activity, start to finish: countdown, items, then onDone. */
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
  const [index, setIndex] = useState(0);
  const [typed, setTyped] = useState("");
  const [flash, setFlash] = useState<"" | "ok" | "bad">("");
  const [showing, setShowing] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const misses = useRef<Miss[]>([]);
  const started = useRef(0);
  const busy = useRef(false);
  const input = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    let alive = true;
    fetchBrainRound(activity.id, language).then((r) => alive && setItems(r.items));
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
    if (count === 0 && items && !started.current) started.current = performance.now();
  }, [count, items]);
  useEffect(() => {
    if (count > 0) return;
    const id = window.setInterval(() => setElapsed((performance.now() - started.current) / 1000), 100);
    return () => window.clearInterval(id);
  }, [count]);

  const item = items?.[index];

  // Variable Recall: show what to remember, then hide it.
  useEffect(() => {
    if (count > 0 || !item?.show) return;
    setShowing(true);
    const id = window.setTimeout(() => setShowing(false), activity.showSeconds * 1000);
    return () => window.clearTimeout(id);
  }, [count, item, activity.showSeconds]);

  useEffect(() => {
    if (count === 0 && !showing) input.current?.focus();
  }, [count, showing, index]);

  const answer = useCallback(
    (given: string) => {
      if (!items || !item || busy.current || showing) return;
      busy.current = true;
      const right = same(given, item.answer);
      if (!right) misses.current.push({ item, given });
      setFlash(right ? "ok" : "bad");
      window.setTimeout(
        () => {
          setFlash("");
          setTyped("");
          busy.current = false;
          if (index + 1 >= items.length) {
            onDone((performance.now() - started.current) / 1000, misses.current, items.length);
          } else {
            setIndex(index + 1);
          }
        },
        right ? 120 : 700,
      );
    },
    [items, item, index, showing, onDone],
  );

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onQuit();
        return;
      }
      if (count > 0 || activity.kind !== "pick") return;
      const left = e.key === "ArrowLeft" || e.key.toLowerCase() === "f";
      const right = e.key === "ArrowRight" || e.key.toLowerCase() === "j";
      if (left || right) {
        e.preventDefault();
        answer(activity.choices[left ? 0 : 1]);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [count, activity, answer, onQuit]);

  return (
    <div className="brain-wrap brain-play">
      <div className="brain-play-top">
        <strong>{activity.title}</strong>
        {checkSize && checkStep ? <span className="brain-check-step">Code age check · {checkStep} of {checkSize}</span> : null}
        <span className="brain-progress">
          {Math.min(index + 1, activity.count)} / {activity.count}
        </span>
        <span className="brain-clock">{count > 0 ? "" : `${elapsed.toFixed(1)}s`}</span>
        <button type="button" className="ws-btn" onClick={onQuit} title="Esc">
          Quit
        </button>
      </div>
      {!items ? (
        <div className="brain-stage">Getting ready…</div>
      ) : count > 0 ? (
        <div className="brain-stage brain-count">{count}</div>
      ) : (
        <div className={`brain-stage${flash ? ` ${flash}` : ""}`}>
          <p className="brain-question">{showing ? "Remember these:" : activity.question}</p>
          <pre className="brain-code">{showing ? item?.show : item?.prompt}</pre>
          {flash === "bad" && item ? <p className="brain-correct">It's {item.answer}</p> : null}
          {showing ? null : activity.kind === "type" ? (
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
      )}
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
