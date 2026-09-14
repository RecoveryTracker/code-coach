/**
 * Read the error, find the line, say what it means.
 *
 * The thing that stops a beginner is almost never the concept. It is eleven
 * lines of red text that turn out to say one short sentence, and not knowing
 * that they say a sentence at all.
 *
 * So the program is shown with line numbers, the message is shown as the
 * engine printed it, and there are two questions: which line, and what does
 * it actually say. The second is the exercise; the first is how you show you
 * followed the message back to something.
 *
 * The two halves are marked separately on purpose. "Wrong" when one of your
 * two answers was right tells you nothing about which half you cannot do
 * yet, and the halves are genuinely different skills — following a line
 * number is mechanical, reading what the message blames is not.
 *
 * The line is picked by clicking the line itself rather than typing a
 * number. Reading a stack trace is an act of pointing at code, and making
 * you translate that into a number in a box adds a step that teaches
 * nothing.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkError, fetchErrors } from "../api";
import type { ErrorCheck, ErrorCrash, ErrorList } from "../types";

/** Which one you were on. */
const LAST_KEY = "code-coach:error-last";

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

export default function Errors() {
  const [list, setList] = useState<ErrorList | null>(null);
  const [chosen, setChosen] = useState("");
  const [line, setLine] = useState(0);
  const [meaning, setMeaning] = useState("");
  const [result, setResult] = useState<ErrorCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchErrors()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families.flatMap((f) => f.crashes);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* a blocked store is not worth interrupting practice for */
        }
        const start = all.find((c) => c.id === last) ?? nextUp(all);
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
      list?.families.flatMap((f) => f.crashes).find((c) => c.id === chosen) ??
      null,
    [list, chosen],
  );

  /* Keyed on the id, not the object: the list is rebuilt after a pass,
     which changes identity, and an effect watching the object would fire
     and clear the answer it just recorded. */
  useEffect(() => {
    if (!chosen) return;
    setLine(0);
    setMeaning("");
    setResult(null);
    try {
      localStorage.setItem(LAST_KEY, chosen);
    } catch {
      /* same */
    }
  }, [chosen]);

  const check = useCallback(async () => {
    if (!item || checking || !line || !meaning) return;
    setChecking(true);
    setError("");
    try {
      const got = await checkError({
        crash_id: item.id,
        line,
        meaning,
      });
      setResult(got);
      if (got.passed) {
        setList((was) =>
          was
            ? {
                ...was,
                families: was.families.map((f) => ({
                  ...f,
                  crashes: f.crashes.map((c) =>
                    c.id === item.id
                      ? { ...c, done: got.done, last: new Date().toISOString() }
                      : c,
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
  }, [item, line, meaning, checking]);

  const again = useCallback(() => {
    setLine(0);
    setMeaning("");
    setResult(null);
  }, []);

  const leastDone = useMemo(
    () => nextUp(list?.families.flatMap((f) => f.crashes) ?? []),
    [list],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !item) return <div className="lessons-empty">Loading…</div>;

  const codeLines = item.code.split("\n");
  const answered = result !== null;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Errors</h2>
        <p className="lessons-intro">
          A program that crashed, and the message it printed. Which line
          caused it, and what is the message actually telling you? Both
          answers come from the engine, not from an opinion.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button
            type="button"
            className="ws-btn kata-next"
            onClick={() => setChosen(leastDone.id)}
            title={
              leastDone.done
                ? `${leastDone.name} — read ${leastDone.done} so far, and `
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
              <span className="wb-section-count">{family.crashes.length}</span>
            </h4>
            {family.crashes.map((c: ErrorCrash) => (
              <button
                key={c.id}
                type="button"
                className={`lessons-pick${c.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(c.id)}
              >
                <span className="lessons-pick-name">{c.name}</span>
                {c.done ? (
                  <span className="lessons-pick-blurb">read {c.done}&#215;</span>
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
            <span className="predict-lang">
              {item.language === "javascript" ? "JavaScript" : "Python"}
            </span>
          </h3>
        </header>

        {/* The message first. It is what you would see in a terminal, and
            the whole point is that you read it before the code. */}
        <p className="wb-walkthrough-note">What it printed</p>
        <pre className="err-message">{item.message}</pre>

        <p className="wb-prompt">Which line caused it?</p>
        <ol className="err-code">
          {codeLines.map((text, i) => {
            const n = i + 1;
            const picked = line === n;
            let tone = "";
            if (answered && n === result.line) tone = " ok";
            else if (answered && picked) tone = " bad";
            return (
              <li key={n}>
                <button
                  type="button"
                  className={`err-line${tone}${picked ? " on" : ""}`}
                  disabled={answered}
                  onClick={() => {
                    setLine(n);
                    setResult(null);
                  }}
                  aria-pressed={picked}
                >
                  <span className="err-num">{n}</span>
                  <code>{text || " "}</code>
                </button>
              </li>
            );
          })}
        </ol>

        <p className="wb-prompt">And what is it telling you?</p>
        <div className="css-choices err-choices">
          {item.choices.map((choice) => {
            const picked = meaning === choice;
            let tone = "";
            if (answered && choice === result.meaning) tone = " ok";
            else if (answered && picked) tone = " bad";
            return (
              <button
                key={choice}
                type="button"
                className={`ws-btn css-choice err-choice${tone}`
                  + (picked && !answered ? " on" : "")}
                disabled={answered}
                onClick={() => {
                  setMeaning(choice);
                  setResult(null);
                }}
              >
                {choice}
              </button>
            );
          })}
        </div>

        <div className="wb-actions">
          <button
            type="button"
            className="ws-btn primary"
            onClick={() => void check()}
            disabled={checking || !line || !meaning || answered}
            title={
              !line
                ? "Pick the line first"
                : !meaning
                  ? "Pick what the message means"
                  : "Check both"
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
                ? `Both right. Read ${result.done}×.`
                : result.line_right
                  ? "Right line, but that is not what the message says."
                  : result.meaning_right
                    ? "Right reading — but it happened on a different line."
                    : "Neither half yet."}
            </p>
            {/* Marked separately, and said separately. Which half you got
                is the useful information. */}
            <ul className="err-halves">
              <li className={result.line_right ? "ok" : "bad"}>
                Line: {result.line_right ? "yours" : `line ${result.line}`}
              </li>
              <li className={result.meaning_right ? "ok" : "bad"}>
                Meaning: {result.meaning_right ? "yours" : result.meaning}
              </li>
            </ul>
            <p className="kata-bug">
              <strong>What to do about it:</strong> {result.fix}
            </p>
          </div>
        ) : null}
      </article>
    </div>
  );
}
