/**
 * Read Flutter widget code and say what it does.
 *
 * Flutter cannot draw a screen here, and a picture would not be a question
 * with one answer anyway. What can be asked is the part that decides the
 * picture: which widget is whose parent, what share of a Row each child gets,
 * which build methods run again after setState, what order a State is told
 * things in. All of it is readable off the code, and every answer is held to
 * what Flutter really does by the suite.
 *
 * Unlike Trace, a click only picks. Check is a separate step, so you can
 * change your mind before committing — the picked choice stays marked so it
 * is obvious what you are about to send.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkFlutter, fetchFlutter } from "../api";
import { LAST_KEYS } from "../lastKeys";
import type { FlutterCheck, FlutterList, FlutterQuestion } from "../types";

/** Which one you were on. Same shape as the keys in lastKeys.ts. */
const LAST_KEY = LAST_KEYS.flutter;

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

export default function FlutterMode() {
  const [list, setList] = useState<FlutterList | null>(null);
  const [chosen, setChosen] = useState("");
  const [picked, setPicked] = useState("");
  const [result, setResult] = useState<FlutterCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchFlutter()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families.flatMap((f) => f.questions);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* a blocked store is not worth interrupting practice for */
        }
        const start = all.find((q) => q.id === last) ?? nextUp(all);
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
    return () => {
      alive = false;
    };
  }, []);

  const item = useMemo(
    () =>
      list?.families
        .flatMap((f) => f.questions)
        .find((q) => q.id === chosen) ?? null,
    [list, chosen],
  );

  /* Keyed on the id, not the object: the list is rebuilt after a pass and
     an effect watching the object would clear the answer it just set. */
  useEffect(() => {
    if (!chosen) return;
    setPicked("");
    setResult(null);
    setError("");
    try {
      localStorage.setItem(LAST_KEY, chosen);
    } catch {
      /* same */
    }
  }, [chosen]);

  const check = useCallback(async () => {
    if (!item || !picked || checking) return;
    setChecking(true);
    setError("");
    try {
      const got = await checkFlutter(item.id, picked);
      setResult(got);
      if (got.passed) {
        setList((was) =>
          was
            ? {
                ...was,
                families: was.families.map((f) => ({
                  ...f,
                  questions: f.questions.map((q) =>
                    q.id === item.id
                      ? { ...q, done: got.done, last: new Date().toISOString() }
                      : q,
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
  }, [item, picked, checking]);

  const again = useCallback(() => {
    setPicked("");
    setResult(null);
    setError("");
  }, []);

  const leastDone = useMemo(
    () => nextUp(list?.families.flatMap((f) => f.questions) ?? []),
    [list],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !item) return <div className="lessons-empty">Loading…</div>;

  const answered = result !== null;
  const codeLines = item.code.split("\n");

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Flutter</h2>
        <p className="lessons-intro">
          Read the widget code and say what Flutter does with it — the tree,
          the layout rules, what rebuilds and when. No screen needed: every
          answer here follows from the code.
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
              <span className="wb-section-count">
                {family.questions.length}
              </span>
            </h4>
            {family.questions.map((q: FlutterQuestion) => (
              <button
                key={q.id}
                type="button"
                className={`lessons-pick${q.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(q.id)}
              >
                <span className="lessons-pick-name">{q.name}</span>
                {q.done ? (
                  <span className="lessons-pick-blurb">
                    right {q.done}&#215;
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
            {item.name}
            <span className="predict-lang">Flutter</span>
          </h3>
        </header>

        {/* Numbered and monospace, indentation kept: in a build method the
            nesting is the tree, so losing it loses the question. */}
        <ol className="err-code trace-code">
          {codeLines.map((text, i) => (
            <li key={i}>
              <div className="err-line trace-line">
                <span className="err-num">{i + 1}</span>
                <code>{text || " "}</code>
              </div>
            </li>
          ))}
        </ol>

        <p className="wb-prompt">{item.question}</p>

        <div className="css-choices">
          {item.choices.map((choice) => {
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
                aria-pressed={isPick}
                disabled={checking || answered}
                onClick={() => setPicked(choice)}
              >
                {choice}
              </button>
            );
          })}
        </div>

        <div className="wb-actions">
          <button
            type="button"
            className={`ws-btn primary${answered ? " on" : ""}`}
            onClick={() => (answered ? setResult(null) : void check())}
            disabled={checking || !picked}
            aria-pressed={answered}
            title={
              answered
                ? "Click again to hide the result"
                : picked
                  ? "Check your answer"
                  : "Pick an answer first"
            }
          >
            {checking ? "Checking…" : "Check"}
          </button>
          {answered ? (
            <button
              type="button"
              className="ws-btn"
              onClick={again}
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
                ? `Right. ${result.done}× now.`
                : `Not that — it is: ${result.expect}`}
            </p>
            <p className="kata-bug">
              <strong>Why:</strong> {result.why}
            </p>
          </div>
        ) : null}
      </article>
    </div>
  );
}
