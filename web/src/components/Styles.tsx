/**
 * Read the CSS, say what the browser computes.
 *
 * The same shape as Predict, for the cascade. You see the markup and the
 * stylesheet, you pick what you think the browser worked out, and only then
 * does the page render in front of you.
 *
 * Why the answer is a choice rather than a box to type in: a computed colour
 * is `rgb(0, 128, 0)` and a computed width is `240px`, and a text box would
 * be marking punctuation. Every wrong choice on offer is what you get if you
 * believe a particular wrong thing about the cascade, and the explanation
 * says which. They arrive sorted, so where the right one sits is decided by
 * the alphabet rather than by whoever wrote the question.
 *
 * "See it" is the CSS version of Watch it run. The same document that was
 * measured is rendered in an iframe, so what you look at after answering is
 * not a reconstruction of the question - it is the question. It stays
 * disabled until you have answered, for the reason the Run button is absent
 * from Predict: looking is answering.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkCss, fetchCssQuizzes } from "../api";
import type { CssCheck, CssList, CssQuiz } from "../types";

/** Which quiz you were on, so coming back lands where you left. */
const LAST_KEY = "code-coach:css-last";

/**
 * Which to offer next: fewest goes, and of those the longest ago.
 *
 * Same rule as the katas and the predict puzzles, and the same reason:
 * the count alone cannot separate two things done twice, and the one
 * from last week is worth more than the one from this morning.
 */
function nextUp<T extends { done: number; last: string }>(
  all: T[],
): T | null {
  if (!all.length) return null;
  return all.reduce((best, item) => {
    if (item.done !== best.done) return item.done < best.done ? item : best;
    return item.last < best.last ? item : best;
  }, all[0]);
}

/** What the question is asking for, in words rather than in API spelling. */
function asked(quiz: CssQuiz): string {
  if (quiz.prop === "rect.width") {
    return `How much horizontal room does ${quiz.target} actually take?`;
  }
  if (quiz.prop === "rect.height") {
    return `How much vertical room does ${quiz.target} actually take?`;
  }
  return `What is the computed ${quiz.prop} of ${quiz.target}?`;
}

export default function Styles() {
  const [list, setList] = useState<CssList | null>(null);
  const [chosen, setChosen] = useState("");
  const [picked, setPicked] = useState("");
  const [result, setResult] = useState<CssCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [showing, setShowing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchCssQuizzes()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families.flatMap((f) => f.quizzes);
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

  const quiz = useMemo(
    () =>
      list?.families.flatMap((f) => f.quizzes).find((q) => q.id === chosen) ??
      null,
    [list, chosen],
  );

  /* Keyed on the id rather than on the quiz object: the list is rebuilt
     after a correct answer, which changes the object's identity, and an
     effect watching the object would fire and wipe the result it just
     set. That exact bug cost an afternoon on the katas screen. */
  useEffect(() => {
    if (!chosen) return;
    setPicked("");
    setResult(null);
    setShowing(false);
    try {
      localStorage.setItem(LAST_KEY, chosen);
    } catch {
      /* same */
    }
  }, [chosen]);

  const check = useCallback(
    async (choice: string) => {
      if (!quiz || checking) return;
      setChecking(true);
      setError("");
      setPicked(choice);
      try {
        const got = await checkCss({ quiz_id: quiz.id, choice });
        setResult(got);
        if (got.passed) {
          setList((was) =>
            was
              ? {
                  ...was,
                  families: was.families.map((f) => ({
                    ...f,
                    quizzes: f.quizzes.map((q) =>
                      q.id === quiz.id
                        ? {
                            ...q,
                            done: got.done,
                            last: new Date().toISOString(),
                          }
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
    },
    [quiz, checking],
  );

  const leastDone = useMemo(
    () => nextUp(list?.families.flatMap((f) => f.quizzes) ?? []),
    [list],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !quiz) return <div className="lessons-empty">Loading…</div>;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Styles</h2>
        <p className="lessons-intro">
          Read the markup and the stylesheet, say what the browser worked
          out, then watch it render. Every answer here was measured in
          Chromium rather than reasoned about.
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
              <span className="wb-section-count">{family.quizzes.length}</span>
            </h4>
            {family.quizzes.map((q) => (
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
            {quiz.name}
            <span className="predict-lang">CSS</span>
          </h3>
        </header>

        {/* Read-only on purpose, both of them. Editing either would
            answer the question. */}
        <p className="wb-walkthrough-note">HTML</p>
        <pre className="predict-code">{quiz.html}</pre>
        {quiz.css ? (
          <>
            <p className="wb-walkthrough-note">CSS</p>
            <pre className="predict-code">{quiz.css}</pre>
          </>
        ) : null}

        <p className="wb-prompt">{asked(quiz)}</p>

        <div className="css-choices">
          {quiz.choices.map((choice) => {
            const isPick = picked === choice;
            const answered = result !== null;
            let tone = "";
            if (answered && choice === result.expect) tone = " ok";
            else if (answered && isPick) tone = " bad";
            return (
              <button
                key={choice}
                type="button"
                /* "on" only before answering. Afterwards the green and
                   the red are the information, and the selected-button
                   accent sits on top of them and hides it. */
                className={
                  `ws-btn css-choice${tone}` +
                  (isPick && !answered ? " on" : "")
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
            className={showing ? "ws-btn on" : "ws-btn"}
            onClick={() => setShowing((open) => !open)}
            // Only after answering, for the same reason Predict has no
            // Run button: looking at it is answering it.
            disabled={!result}
            title={
              result
                ? "Render the same document that was measured"
                : "Say what you think it computes first"
            }
          >
            {showing ? "Hide it" : "See it"}
          </button>
          {result ? (
            <button
              type="button"
              className="ws-btn"
              onClick={() => {
                setPicked("");
                setResult(null);
                setShowing(false);
              }}
              title="Clear the answer and go again — the whole point is reps"
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
                ? "That is what the browser computes."
                : `Not that — the browser says ${result.expect}.`}
            </p>
            <p className="kata-bug">
              <strong>Why:</strong> {result.why}
            </p>
          </div>
        ) : null}

        {showing && result ? (
          <div className="wb-viz css-render">
            <p className="wb-walkthrough-note">
              The same document that was measured, rendered here.
            </p>
            <iframe
              className="css-frame"
              title={`${quiz.name} rendered`}
              sandbox=""
              srcDoc={quiz.page}
            />
          </div>
        ) : null}
      </article>
    </div>
  );
}
