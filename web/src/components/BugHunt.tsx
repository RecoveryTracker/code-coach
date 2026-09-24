/**
 * Bug Hunt: a bug report, a program, and the process of finding it.
 *
 * Four steps, in order, each one checked: reproduce the bug, find the
 * line, say what is wrong, fix it. The order is enforced on purpose.
 * The finding behind this mode is that debugging taught as explicit
 * steps is much better learned than debugging left to instinct, and a
 * screen that let you jump straight to editing would be teaching
 * instinct again.
 *
 * Every step can be shown rather than solved, though. Being stuck on
 * finding the line should not mean never getting to practise the fix,
 * and a step you were shown is still a step you have now seen done.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  checkBugHuntCause,
  checkBugHuntLine,
  fetchBugHuntAnswer,
  fetchBugHunts,
  fixBugHunt,
  tryBugHunt,
} from "../api";
import { LAST_KEYS } from "../lastKeys";
import type {
  BugHunt as Hunt,
  BugHuntFix,
  BugHuntList,
  BugHuntTry,
} from "../types";

const LAST_KEY = LAST_KEYS.bughunt;

type Step = 1 | 2 | 3 | 4;

const STEPS: { n: Step; name: string }[] = [
  { n: 1, name: "Reproduce" },
  { n: 2, name: "Locate" },
  { n: 3, name: "Explain" },
  { n: 4, name: "Fix" },
];

/** Fewest goes, and of those the longest ago. Same rule as everywhere. */
function nextUp<T extends { done: number; last: string }>(all: T[]): T | null {
  if (!all.length) return null;
  return all.reduce((best, item) => {
    if (item.done !== best.done) return item.done < best.done ? item : best;
    return item.last < best.last ? item : best;
  }, all[0]);
}

/**
 * A value as the hunt's own language writes it.
 *
 * Python says True, None and 'text'; JavaScript says true, null and
 * "text". Showing a JavaScript hunt's answer as `True` is a small wrong
 * thing that makes you doubt the rest of the panel.
 */
function show(value: unknown, language: string): string {
  const py = language === "python";
  if (value === null || value === undefined) return py ? "None" : "null";
  if (typeof value === "boolean") return py ? (value ? "True" : "False") : String(value);
  if (typeof value === "string") {
    if (!py) return JSON.stringify(value);
    return value.includes("'") ? JSON.stringify(value) : `'${value}'`;
  }
  if (Array.isArray(value)) return `[${value.map((v) => show(v, language)).join(", ")}]`;
  if (typeof value === "object") {
    const pairs = Object.entries(value as Record<string, unknown>).map(
      ([k, v]) => `${show(k, language)}: ${show(v, language)}`,
    );
    return `{${pairs.join(", ")}}`;
  }
  return String(value);
}

/**
 * Only the language picked in the top bar.
 *
 * It showed Python and JavaScript side by side at first, which is two
 * languages' worth of list for someone learning one. The picker at the
 * top is where the language is chosen for every other screen, so this
 * follows it rather than growing a picker of its own.
 */
export default function BugHunt({ language }: { language: string }) {
  const [list, setList] = useState<BugHuntList | null>(null);
  const [chosen, setChosen] = useState("");
  const [error, setError] = useState("");

  // Step 1
  const [args, setArgs] = useState("");
  const [tries, setTries] = useState<BugHuntTry[]>([]);
  const [trying, setTrying] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [reproduced, setReproduced] = useState<BugHuntTry | null>(null);
  // Step 2
  const [wrongLines, setWrongLines] = useState<number[]>([]);
  const [bugLines, setBugLines] = useState<number[]>([]);
  const [lineShown, setLineShown] = useState(false);
  // Step 3
  const [wrongCauses, setWrongCauses] = useState<string[]>([]);
  const [cause, setCause] = useState("");
  const [causeShown, setCauseShown] = useState(false);
  // Step 4
  const [code, setCode] = useState("");
  const [fix, setFix] = useState<BugHuntFix | null>(null);
  const [fixing, setFixing] = useState(false);
  const [answer, setAnswer] = useState("");

  useEffect(() => {
    let alive = true;
    fetchBugHunts()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families
          .flatMap((f) => f.hunts)
          .filter((h) => h.language === language);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* a blocked store is not worth interrupting practice for */
        }
        const start = all.find((h) => h.id === last) ?? nextUp(all);
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, []);

  /* The families as shown: only this language's hunts, and no empty
     headings for the languages that were filtered away. */
  const shown = useMemo(
    () =>
      (list?.families ?? [])
        .map((f) => ({ ...f, hunts: f.hunts.filter((h) => h.language === language) }))
        .filter((f) => f.hunts.length > 0),
    [list, language],
  );

  const hunt = useMemo(
    () => shown.flatMap((f) => f.hunts).find((h) => h.id === chosen) ?? null,
    [shown, chosen],
  );

  /* Switching language while a hunt is open: the open one is no longer
     on the list, so move to this language's next one rather than leave
     a hunt on screen that the list no longer admits to. */
  useEffect(() => {
    if (!list) return;
    const here = shown.flatMap((f) => f.hunts);
    if (!here.some((h) => h.id === chosen)) {
      setChosen(nextUp(here)?.id ?? "");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language, list]);

  /* Keyed on the id, not the object: the list is rebuilt after a pass,
     which changes identity, and resetting on that would wipe the result
     the pass just produced. */
  useEffect(() => {
    if (!chosen) return;
    setArgs("");
    setTries([]);
    setShowHint(false);
    setReproduced(null);
    setWrongLines([]);
    setBugLines([]);
    setLineShown(false);
    setWrongCauses([]);
    setCause("");
    setCauseShown(false);
    setFix(null);
    setAnswer("");
    setError("");
    try {
      localStorage.setItem(LAST_KEY, chosen);
    } catch {
      /* same */
    }
  }, [chosen]);

  useEffect(() => {
    if (hunt) setCode(hunt.code);
    // Only when the hunt changes - not on every list rebuild.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chosen, hunt?.id]);

  const step: Step = !reproduced ? 1 : !bugLines.length ? 2 : !cause ? 3 : 4;
  const solved = !!fix?.passed;

  const attempt = useCallback(async () => {
    if (!hunt || trying || !args.trim()) return;
    setTrying(true);
    setError("");
    try {
      const got = await tryBugHunt(hunt.id, args);
      setTries((was) => [got, ...was].slice(0, 8));
      if (got.reproduced) setReproduced(got);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setTrying(false);
    }
  }, [hunt, args, trying]);

  const pickLine = useCallback(
    async (n: number) => {
      if (!hunt || step !== 2) return;
      try {
        const got = await checkBugHuntLine(hunt.id, n);
        if (got.right) setBugLines([n]);
        else setWrongLines((was) => (was.includes(n) ? was : [...was, n]));
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [hunt, step],
  );

  const revealLine = useCallback(async () => {
    if (!hunt) return;
    const got = await checkBugHuntLine(hunt.id, 0);
    setBugLines(Array.isArray(got.reveal) ? (got.reveal as number[]) : []);
    setLineShown(true);
  }, [hunt]);

  const pickCause = useCallback(
    async (choice: string) => {
      if (!hunt || step !== 3) return;
      try {
        const got = await checkBugHuntCause(hunt.id, choice);
        if (got.right) setCause(choice);
        else setWrongCauses((was) => (was.includes(choice) ? was : [...was, choice]));
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [hunt, step],
  );

  const revealCause = useCallback(async () => {
    if (!hunt) return;
    const got = await checkBugHuntCause(hunt.id, "");
    if (typeof got.reveal === "string") setCause(got.reveal);
    setCauseShown(true);
  }, [hunt]);

  const runFix = useCallback(async () => {
    if (!hunt || fixing) return;
    setFixing(true);
    setError("");
    try {
      const got = await fixBugHunt(hunt.id, code);
      setFix(got);
      if (got.passed) {
        setList((was) =>
          was
            ? {
                ...was,
                families: was.families.map((f) => ({
                  ...f,
                  hunts: f.hunts.map((h) =>
                    h.id === hunt.id
                      ? { ...h, done: got.done, last: new Date().toISOString() }
                      : h,
                  ),
                })),
              }
            : was,
        );
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setFixing(false);
    }
  }, [hunt, code, fixing]);

  const showAnswer = useCallback(async () => {
    if (!hunt) return;
    const got = await fetchBugHuntAnswer(hunt.id);
    setAnswer(got.code);
  }, [hunt]);

  const leastDone = useMemo(
    () => nextUp(shown.flatMap((f) => f.hunts)),
    [shown],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list) return <div className="lessons-empty">Loading…</div>;
  if (!shown.length) {
    /* Say which languages do have hunts, rather than an empty screen
       that looks broken. The names come from the list itself, so this
       cannot fall out of step with what exists. */
    const have = list.families.map((f) => f.name).join(" and ");
    return (
      <div className="lessons-empty">
        No bug hunts in this language yet. There are hunts in {have} —
        switch the language at the top to try them.
      </div>
    );
  }
  if (!hunt) return <div className="lessons-empty">Loading…</div>;

  const lines = hunt.code.replace(/\n$/, "").split("\n");
  const lang = hunt.language;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Bug Hunt</h2>
        <p className="lessons-intro">
          A bug report and the program it is about. Reproduce it, find the
          line, say what is wrong, then fix it — in that order, because
          that order is the skill.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button
            type="button"
            className="ws-btn kata-next"
            onClick={() => setChosen(leastDone.id)}
          >
            Next up: {leastDone.title}
          </button>
        ) : null}
        {shown.map((family) => (
          <div key={family.name} className="wb-section">
            <h4 className="wb-section-head">
              {family.name}
              <span className="wb-section-count">{family.hunts.length}</span>
            </h4>
            {family.hunts.map((h: Hunt) => (
              <button
                key={h.id}
                type="button"
                className={`lessons-pick${h.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(h.id)}
              >
                <span className="lessons-pick-name">{h.title}</span>
                {h.done ? (
                  <span className="lessons-pick-blurb">fixed {h.done}&#215;</span>
                ) : null}
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {hunt.title}
            <span className="predict-lang">
              {lang === "javascript" ? "JavaScript" : "Python"}
            </span>
          </h3>
        </header>

        <ol className="hunt-steps">
          {STEPS.map((s) => (
            <li
              key={s.n}
              className={`hunt-step${s.n === step && !solved ? " now" : ""}${
                s.n < step || solved ? " done" : ""
              }`}
            >
              <span className="hunt-step-n">{s.n < step || solved ? "✓" : s.n}</span>
              {s.name}
            </li>
          ))}
        </ol>

        <p className="wb-walkthrough-note">The bug report</p>
        <blockquote className="hunt-report">{hunt.report}</blockquote>

        <p className="wb-walkthrough-note">The program</p>
        {step === 2 ? (
          <p className="wb-prompt">
            Which line causes it? <span className="err-tap">Click the line.</span>
          </p>
        ) : null}
        <ol className="err-code">
          {lines.map((text, i) => {
            const n = i + 1;
            const isBug = bugLines.includes(n);
            const isWrong = wrongLines.includes(n);
            const tone = isBug ? " ok" : isWrong ? " bad" : "";
            const live = step === 2;
            return (
              <li key={n}>
                <button
                  type="button"
                  className={`err-line${tone}`}
                  disabled={!live}
                  onClick={() => void pickLine(n)}
                >
                  <span className="err-num">{n}</span>
                  <code>{text || " "}</code>
                </button>
              </li>
            );
          })}
        </ol>

        {/* ── Step 1: reproduce ── */}
        <section className="hunt-panel">
          <h4 className="hunt-panel-head">1. Reproduce it</h4>
          {!reproduced ? (
            <>
              <p className="wb-prompt">
                Call <code>{hunt.signature}</code> with an input that shows the
                bug. Type the arguments the way you would in the code.
              </p>
              <div className="hunt-try">
                <code className="hunt-call">{hunt.name}(</code>
                <input
                  className="hunt-args"
                  value={args}
                  onChange={(e) => setArgs(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") void attempt();
                  }}
                  placeholder={hunt.arity > 1 ? "first, second" : "an argument"}
                  aria-label={`Arguments for ${hunt.name}`}
                  spellCheck={false}
                />
                <code className="hunt-call">)</code>
                <button
                  type="button"
                  className="ws-btn primary"
                  disabled={trying || !args.trim()}
                  onClick={() => void attempt()}
                >
                  {trying ? "Running…" : "Try it"}
                </button>
                <button
                  type="button"
                  className="ws-btn"
                  onClick={() => setShowHint((v) => !v)}
                >
                  Hint
                </button>
              </div>
              {showHint ? <p className="wb-answer">{hunt.hint}</p> : null}
            </>
          ) : (
            <p className="wb-verdict ok">
              Reproduced: <code>{reproduced.call}</code> gave{" "}
              <code>{reproduced.error ? `an error` : show(reproduced.got, lang)}</code>
              {" "}and should have given <code>{show(reproduced.want, lang)}</code>.
            </p>
          )}
          {tries.length && !reproduced ? (
            <ul className="hunt-tries">
              {tries.map((t, i) => (
                <li key={i} className={`hunt-try-row${t.problem ? " bad" : ""}`}>
                  {t.problem ? (
                    t.problem
                  ) : (
                    <>
                      <code>{t.call}</code> gave{" "}
                      <code>{t.error ? `an error: ${t.error}` : show(t.got, lang)}</code>
                      {" — "}
                      {t.reproduced
                        ? "that shows the bug."
                        : "that is right, so the bug is not here. Try another."}
                    </>
                  )}
                </li>
              ))}
            </ul>
          ) : null}
        </section>

        {/* ── Step 2: locate ── */}
        {step >= 2 ? (
          <section className="hunt-panel">
            <h4 className="hunt-panel-head">2. Find the line</h4>
            {bugLines.length ? (
              <p className={`wb-verdict ${lineShown ? "" : "ok"}`}>
                {lineShown ? "It was" : "Found it:"} line {bugLines.join(" and ")}.
                {wrongLines.length && !lineShown
                  ? " Following the wrong value back is exactly how."
                  : ""}
              </p>
            ) : (
              <>
                <p className="wb-prompt">
                  Click the line in the program above where it goes wrong.
                  {wrongLines.length
                    ? " Not that one — follow the wrong value back to where it was worked out."
                    : ""}
                </p>
                <button type="button" className="ws-btn" onClick={() => void revealLine()}>
                  Show me
                </button>
              </>
            )}
          </section>
        ) : null}

        {/* ── Step 3: explain ── */}
        {step >= 3 ? (
          <section className="hunt-panel">
            <h4 className="hunt-panel-head">3. What is wrong?</h4>
            <div className="css-choices err-choices">
              {hunt.choices.map((choice) => {
                const right = choice === cause;
                const wrong = wrongCauses.includes(choice);
                return (
                  <button
                    key={choice}
                    type="button"
                    className={`ws-btn css-choice err-choice${right ? " ok" : ""}${
                      wrong ? " bad" : ""
                    }`}
                    disabled={!!cause || wrong}
                    onClick={() => void pickCause(choice)}
                  >
                    {choice}
                  </button>
                );
              })}
            </div>
            {!cause ? (
              <button type="button" className="ws-btn" onClick={() => void revealCause()}>
                Show me
              </button>
            ) : causeShown ? (
              <p className="wb-verdict">That is what is wrong.</p>
            ) : null}
          </section>
        ) : null}

        {/* ── Step 4: fix ── */}
        {step >= 4 ? (
          <section className="hunt-panel">
            <h4 className="hunt-panel-head">4. Fix it</h4>
            <p className="wb-prompt">
              Change the program so the bug is gone. Every case runs — the
              ones that were already right have to stay right.
            </p>
            <textarea
              className="wb-code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              spellCheck={false}
              rows={Math.max(8, lines.length + 1)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                  e.preventDefault();
                  void runFix();
                }
              }}
            />
            <div className="wb-actions">
              <button
                type="button"
                className="ws-btn primary"
                disabled={fixing}
                onClick={() => void runFix()}
              >
                {fixing ? "Running…" : "Run the cases"}
              </button>
              <button type="button" className="ws-btn" onClick={() => setCode(hunt.code)}>
                Start over
              </button>
              <button type="button" className="ws-btn" onClick={() => void showAnswer()}>
                Show the fix
              </button>
            </div>
            {answer ? (
              <div className="kata-answer">
                <p className="wb-walkthrough-note">The program, fixed:</p>
                <pre className="wb-stderr">{answer}</pre>
              </div>
            ) : null}
            {fix ? (
              fix.broke ? (
                <div className="kata-result">
                  <p className="wb-verdict bad">This did not run:</p>
                  <pre className="wb-stderr">{fix.broke}</pre>
                </div>
              ) : (
                <div className="kata-result">
                  <p className={fix.passed ? "wb-verdict ok" : "wb-verdict bad"}>
                    {fix.passed
                      ? `All ${fix.total} cases pass.`
                      : `${fix.count} of ${fix.total} cases pass.`}
                  </p>
                  <ul className="kata-cases">
                    {fix.results.map((c, i) => (
                      <li key={i} className={`kata-case${c.passed ? " ok" : " bad"}`}>
                        <code className="mono">
                          {hunt.name}({c.args.map((a) => show(a, lang)).join(", ")})
                        </code>
                        <span className="kata-case-got">
                          {c.passed
                            ? `→ ${show(c.want, lang)}`
                            : c.error
                              ? `raised ${c.error}`
                              : `gave ${show(c.got, lang)}, wanted ${show(c.want, lang)}`}
                        </span>
                      </li>
                    ))}
                  </ul>
                  {fix.passed ? (
                    <>
                      <p className="kata-bug">
                        <strong>What was wrong:</strong> {fix.cause}
                      </p>
                      <p className="kata-bug">
                        <strong>The lesson:</strong> {fix.lesson}
                      </p>
                    </>
                  ) : null}
                </div>
              )
            ) : null}
          </section>
        ) : null}

        {error ? <p className="wb-verdict bad">{error}</p> : null}
      </article>
    </div>
  );
}
