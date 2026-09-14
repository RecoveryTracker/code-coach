/**
 * Stop the program mid-run and say what a variable holds.
 *
 * Predict asks what a program prints, which is the whole program at once.
 * This asks the smaller and harder question — at this exact moment, what is
 * in `total`? — which is the one you have to answer in your head to debug
 * anything, and the one nobody practises, because checking yourself means
 * running it, and once you have run it you have the answer and have learned
 * nothing.
 *
 * So you commit first and the step table is the reward. Watch it run is
 * disabled until you have answered, same as on Predict and for the same
 * reason: stepping through it first is reading the answer.
 *
 * The line the question is about is marked in the listing, because "line 4"
 * and counting down four lines are different jobs and only one of them is
 * the exercise.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkTrace, fetchTraces } from "../api";
import { VizPanel } from "./VizPanel";
import type { TraceCheck, TraceList, TraceMoment } from "../types";
import { LAST_KEYS } from "../lastKeys";

/** Which one you were on. */
const LAST_KEY = LAST_KEYS.trace;

/** Fewest goes, and of those the longest ago. Same rule as everywhere. */
function nextUp<T extends { done: number; last: string }>(
  all: T[],
): T | null {
  if (!all.length) return null;
  return all.reduce((best, item) => {
    if (item.done !== best.done) return item.done < best.done ? item : best;
    return item.last < best.last ? item : best;
  }, all[0]);
}

export default function TraceValue() {
  const [list, setList] = useState<TraceList | null>(null);
  const [chosen, setChosen] = useState("");
  const [picked, setPicked] = useState("");
  const [result, setResult] = useState<TraceCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [watching, setWatching] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchTraces()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families.flatMap((f) => f.traces);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* a blocked store is not worth interrupting practice for */
        }
        const start = all.find((t) => t.id === last) ?? nextUp(all);
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
    return () => {
      alive = false;
    };
  }, []);

  const moment = useMemo(
    () =>
      list?.families.flatMap((f) => f.traces).find((t) => t.id === chosen) ??
      null,
    [list, chosen],
  );

  /* Keyed on the id, not the object: the list is rebuilt after a pass and
     an effect watching the object would clear the answer it just set. */
  useEffect(() => {
    if (!chosen) return;
    setPicked("");
    setResult(null);
    setWatching(false);
    try {
      localStorage.setItem(LAST_KEY, chosen);
    } catch {
      /* same */
    }
  }, [chosen]);

  const check = useCallback(
    async (answer: string) => {
      if (!moment || checking) return;
      setChecking(true);
      setError("");
      setPicked(answer);
      try {
        const got = await checkTrace({ trace_id: moment.id, answer });
        setResult(got);
        if (got.passed) {
          setList((was) =>
            was
              ? {
                  ...was,
                  families: was.families.map((f) => ({
                    ...f,
                    traces: f.traces.map((t) =>
                      t.id === moment.id
                        ? {
                            ...t,
                            done: got.done,
                            last: new Date().toISOString(),
                          }
                        : t,
                    ),
                  })),
                }
              : was,
          );
        }
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setChecking(false);
      }
    },
    [moment, checking],
  );

  const leastDone = useMemo(
    () => nextUp(list?.families.flatMap((f) => f.traces) ?? []),
    [list],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !moment) return <div className="lessons-empty">Loading…</div>;

  const answered = result !== null;
  const codeLines = moment.code.split("\n");

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Trace</h2>
        <p className="lessons-intro">
          Stop the program part way and say what a variable holds. Answer
          first, then step through it and watch the value arrive.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button
            type="button"
            className="ws-btn kata-next"
            onClick={() => setChosen(leastDone.id)}
            title={
              leastDone.done
                ? `${leastDone.name} — right ${leastDone.done} so far, and `
                  + `the longest ago of those`
                : `${leastDone.name} — not tried yet`
            }
          >
            Next up: {leastDone.name}
          </button>
        ) : null}
        {list.families.map((family) => (
          <div key={family.name} className="wb-section">
            <h4 className="wb-section-head">
              {family.name}
              <span className="wb-section-count">{family.traces.length}</span>
            </h4>
            {family.traces.map((t: TraceMoment) => (
              <button
                key={t.id}
                type="button"
                className={`lessons-pick${t.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(t.id)}
              >
                <span className="lessons-pick-name">{t.name}</span>
                {t.done ? (
                  <span className="lessons-pick-blurb">
                    right {t.done}&#215;
                  </span>
                ) : null}
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {moment.name}
            <span className="predict-lang">
              {moment.language === "javascript" ? "JavaScript" : "Python"}
            </span>
          </h3>
        </header>

        {/* The line in question is marked. Counting down four lines is a
            different job from the one being practised. */}
        <ol className="err-code trace-code">
          {codeLines.map((text, i) => {
            const n = i + 1;
            const here = n === moment.at_line;
            return (
              <li key={n}>
                <div className={`err-line trace-line${here ? " here" : ""}`}>
                  <span className="err-num">{n}</span>
                  <code>{text || " "}</code>
                  {here ? (
                    <span className="trace-marker" aria-hidden="true">
                      ← about to run
                    </span>
                  ) : null}
                </div>
              </li>
            );
          })}
        </ol>

        <p className="wb-prompt">{moment.question}</p>

        <div className="css-choices">
          {moment.choices.map((choice) => {
            const isPick = picked === choice;
            let tone = "";
            if (answered && choice === result.expect) tone = " ok";
            else if (answered && isPick) tone = " bad";
            return (
              <button
                key={choice}
                type="button"
                className={
                  `ws-btn css-choice${tone}`
                  + (isPick && !answered ? " on" : "")
                }
                disabled={checking || answered}
                onClick={() => void check(choice)}
              >
                {choice}
              </button>
            );
          })}
        </div>

        <div className="wb-actions">
          <button
            type="button"
            className={watching ? "ws-btn on" : "ws-btn"}
            onClick={() => setWatching((open) => !open)}
            // Only after answering. Stepping through it first is reading
            // the answer, which is the one thing this mode is not for.
            disabled={!answered}
            title={
              answered
                ? "Step through it and watch the value arrive"
                : "Say what you think it holds first"
            }
          >
            {watching ? "Hide run" : "Watch it run"}
          </button>
          {answered ? (
            <button
              type="button"
              className="ws-btn"
              onClick={() => {
                setPicked("");
                setResult(null);
                setWatching(false);
              }}
              title="Clear it and go again — the next go is the point"
            >
              Again
            </button>
          ) : null}
        </div>

        {error ? <p className="wb-verdict bad">{error}</p> : null}

        {result ? (
          <div className="kata-result">
            <p className={result.passed ? "wb-verdict ok" : "wb-verdict bad"}>
              {result.passed
                ? `That is what it holds. Right ${result.done}×.`
                : `Not that — ${moment.variable} is ${result.expect} there.`}
            </p>
            <p className="kata-bug">
              <strong>Why:</strong> {result.why}
            </p>
          </div>
        ) : null}

        {watching && answered ? (
          <div className="wb-viz">
            <VizPanel
              getCode={() => moment.code}
              patternId={null}
              problemNumber={null}
              resetKey={moment.id}
              language={moment.language}
            />
          </div>
        ) : null}
      </article>
    </div>
  );
}
