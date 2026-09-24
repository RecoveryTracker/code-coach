/**
 * Regex: write a pattern that finds these and leaves those alone.
 *
 * Each task shows both sides - what the pattern must match and what it
 * must skip - because a regular expression is a claim about which
 * strings are in and which are out, and seeing only one side hides the
 * half of the claim that goes wrong.
 *
 * The pattern runs in the real engine of the language picked at the top:
 * Python's re, or JavaScript's RegExp. The screen says which, because the
 * two differ in the corners and a pattern is only promised to work in
 * the engine it was checked in.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkRegex, fetchRegex, fetchRegexAnswer } from "../api";
import { LAST_KEYS } from "../lastKeys";
import type { RegexCheck, RegexList, RegexTaskInfo } from "../types";

const LAST_KEY = LAST_KEYS.regex;

/** Fewest goes, and of those the longest ago. Same rule as everywhere. */
function nextUp<T extends { done: number; last: string }>(all: T[]): T | null {
  if (!all.length) return null;
  return all.reduce((best, item) => {
    if (item.done !== best.done) return item.done < best.done ? item : best;
    return item.last < best.last ? item : best;
  }, all[0]);
}

/** Whitespace made visible, so a tab in a test string is not invisible. */
function visible(text: string): string {
  return text.replace(/\t/g, "→").replace(/ /g, "·");
}

export default function RegexMode({ language }: { language: string }) {
  const [list, setList] = useState<RegexList | null>(null);
  const [chosen, setChosen] = useState("");
  const [pattern, setPattern] = useState("");
  const [result, setResult] = useState<RegexCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchRegex()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families.flatMap((f) => f.tasks);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* a blocked store is not worth interrupting practice for */
        }
        const start = all.find((t) => t.id === last) ?? nextUp(all);
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, []);

  const item = useMemo(
    () => list?.families.flatMap((f) => f.tasks).find((t) => t.id === chosen) ?? null,
    [list, chosen],
  );

  useEffect(() => {
    if (!chosen) return;
    setPattern("");
    setResult(null);
    setShowHint(false);
    setAnswer("");
    setError("");
    try {
      localStorage.setItem(LAST_KEY, chosen);
    } catch {
      /* same */
    }
  }, [chosen]);

  const run = useCallback(async () => {
    if (!item || checking || !pattern) return;
    setChecking(true);
    setError("");
    try {
      const got = await checkRegex(item.id, pattern, language);
      setResult(got);
      if (got.passed) {
        setList((was) =>
          was
            ? {
                ...was,
                families: was.families.map((f) => ({
                  ...f,
                  tasks: f.tasks.map((t) =>
                    t.id === item.id
                      ? { ...t, done: got.done, last: new Date().toISOString() }
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
  }, [item, pattern, language, checking]);

  const leastDone = useMemo(
    () => nextUp(list?.families.flatMap((f) => f.tasks) ?? []),
    [list],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !item) return <div className="lessons-empty">Loading…</div>;

  const engineName =
    language === "javascript" || language === "typescript"
      ? "JavaScript's RegExp"
      : "Python's re";
  const rowsFor = (should: boolean) =>
    result?.rows.filter((r) => r.should_match === should) ?? [];

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Regex</h2>
        <p className="lessons-intro">
          Write a pattern that finds the strings on the left and leaves the
          ones on the right alone. It runs in the real engine for your
          language.
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
        {list.families.map((family) => (
          <div key={family.name} className="wb-section">
            <h4 className="wb-section-head">
              {family.name}
              <span className="wb-section-count">{family.tasks.length}</span>
            </h4>
            {family.tasks.map((t: RegexTaskInfo) => (
              <button
                key={t.id}
                type="button"
                className={`lessons-pick${t.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(t.id)}
              >
                <span className="lessons-pick-name">{t.title}</span>
                {t.done ? (
                  <span className="lessons-pick-blurb">done {t.done}&#215;</span>
                ) : null}
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {item.title}
            <span className="predict-lang">{engineName}</span>
          </h3>
        </header>
        <p className="lessons-blurb">{item.brief}</p>

        <div className="rx-columns">
          <div className="rx-col">
            <p className="wb-walkthrough-note">Must match</p>
            <ul className="rx-strings">
              {item.match.map((s) => {
                const row = rowsFor(true).find((r) => r.text === s);
                const want = item.capture[s];
                return (
                  <li
                    key={s}
                    className={`rx-string${row ? (row.right ? " ok" : " bad") : ""}`}
                  >
                    <code>{visible(s)}</code>
                    {want !== undefined ? (
                      <span className="rx-capture">
                        capture <code>{want}</code>
                        {row && row.group !== null && row.group !== want ? (
                          <> — got <code>{row.group}</code></>
                        ) : null}
                      </span>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </div>
          <div className="rx-col">
            <p className="wb-walkthrough-note">Must skip</p>
            <ul className="rx-strings">
              {item.skip.map((s) => {
                const row = rowsFor(false).find((r) => r.text === s);
                return (
                  <li
                    key={s}
                    className={`rx-string${row ? (row.right ? " ok" : " bad") : ""}`}
                  >
                    <code>{visible(s)}</code>
                    {row && !row.right ? (
                      <span className="rx-capture">matched, and should not</span>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        <div className="rx-pattern-row">
          <code className="rx-slash">/</code>
          <input
            className="rx-pattern"
            value={pattern}
            onChange={(e) => setPattern(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") void run();
            }}
            placeholder="your pattern"
            aria-label="Your regular expression"
            spellCheck={false}
            autoComplete="off"
          />
          <code className="rx-slash">/</code>
          <button
            type="button"
            className="ws-btn primary"
            disabled={checking || !pattern}
            onClick={() => void run()}
          >
            {checking ? "Checking…" : "Check"}
          </button>
          <button type="button" className="ws-btn" onClick={() => setShowHint((v) => !v)}>
            Hint
          </button>
          <button
            type="button"
            className="ws-btn"
            onClick={() =>
              void fetchRegexAnswer(item.id).then((got) => setAnswer(got.answer))
            }
          >
            Show answer
          </button>
        </div>
        {showHint ? <p className="wb-answer">{item.hint}</p> : null}
        {answer ? (
          <p className="wb-answer">
            One answer: <code>{answer}</code>
          </p>
        ) : null}

        {result ? (
          result.broke ? (
            <p className="wb-verdict bad">{result.broke}</p>
          ) : result.passed ? (
            <>
              <p className="wb-verdict ok">Every string is right.</p>
              <p className="kata-bug">
                <strong>The idea:</strong> {result.lesson}
              </p>
            </>
          ) : (
            <p className="wb-verdict bad">
              {result.rows.filter((r) => r.right).length} of {result.rows.length}{" "}
              right — the red ones are what to look at.
            </p>
          )
        ) : null}
        {error ? <p className="wb-verdict bad">{error}</p> : null}
      </article>
    </div>
  );
}
