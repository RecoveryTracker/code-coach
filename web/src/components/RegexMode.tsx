/**
 * Regex: write a pattern that finds these and leaves those alone.
 *
 * Each task shows both sides - what the pattern must match and what it
 * must skip - because a regular expression is a claim about which
 * strings are in and which are out, and seeing only one side hides the
 * half of the claim that goes wrong.
 *
 * The pattern runs in the real engine of the language picked at the top:
 * Python's re, JavaScript's RegExp or Dart's RegExp. The screen says which, because the
 * engines differ in the corners and a pattern is only promised to work in
 * the engine it was checked in.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkRegex, fetchRegex, fetchRegexAnswer } from "../api";
import { LAST_KEYS } from "../lastKeys";
import { explainPattern } from "../lib/regexExplain";
import type { RegexCheck, RegexList, RegexTaskInfo } from "../types";

const LAST_KEY = LAST_KEYS.regex;
const PRIMER_KEY = "code-coach:regex-primer";

/** Every symbol the tasks use: [symbol, what it means, an example]. */
const PRIMER: [string, string, string][] = [
  ["abc", "letters and digits mean themselves", "cat finds \"cat\" in \"concat\""],
  [".", "any one character", "c.t finds cat, cot, c7t"],
  ["\\d", "one digit, 0 to 9", "\\d\\d finds 42 in \"room 42\""],
  ["\\w", "one letter, digit or _", "\\w finds the a in \"a!\""],
  ["\\s", "one space or tab", "a\\sb finds \"a b\""],
  ["[abc]", "one character from the list", "gr[ae]y finds gray and grey"],
  ["[a-z]", "one character in the range", "[0-9] is the same as \\d"],
  ["[^abc]", "one character NOT in the list", "[^aeiou] is any non-vowel"],
  ["+", "the thing before it, one or more times", "\\d+ finds 7, 42 and 2026"],
  ["*", "the thing before it, zero or more times", "ab*c finds ac, abc, abbbc"],
  ["?", "the thing before it is optional", "colou?r finds color and colour"],
  ["{3}", "the thing before it, exactly 3 times", "\\d{3} finds 123"],
  ["{2,4}", "between 2 and 4 times", "a{2,4} finds aa to aaaa"],
  ["^", "the start of the text", "^cat: text that begins with cat"],
  ["$", "the end of the text", "cat$: text that ends with cat"],
  ["|", "or", "cat|dog finds either"],
  ["( )", "a group - repeat it as one, or capture it", "(ab)+ finds ab, abab"],
  ["\\.", "a real dot (the backslash turns a symbol off)", "\\d\\.\\d finds 3.5"],
];

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
  // The primer starts open, and stays how you left it.
  const [primerOpen, setPrimerOpen] = useState(() => {
    try {
      return localStorage.getItem(PRIMER_KEY) !== "closed";
    } catch {
      return true;
    }
  });

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

  // Once a check has run, name the engine it really used: without Dart
  // installed, a Dart learner's pattern is checked in Python's re.
  const engine =
    result?.engine ||
    (language === "javascript" || language === "typescript"
      ? "javascript"
      : language === "dart"
        ? "dart"
        : "python");
  const engineName =
    engine === "javascript"
      ? "JavaScript's RegExp"
      : engine === "dart"
        ? "Dart's RegExp"
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

        <details
          className="rx-primer"
          open={primerOpen}
          onToggle={(e) => {
            const open = (e.currentTarget as HTMLDetailsElement).open;
            setPrimerOpen(open);
            try {
              localStorage.setItem(PRIMER_KEY, open ? "open" : "closed");
            } catch {
              /* it just opens again next time */
            }
          }}
        >
          <summary>Regex from zero - what every symbol means</summary>
          <p>
            A regular expression is a description of text. Most characters just
            mean themselves: <code>cat</code> finds the letters c, a, t in a row,
            anywhere. A few characters are symbols with a special job:
          </p>
          <table className="rx-primer-table">
            <tbody>
              {PRIMER.map(([sym, says, example]) => (
                <tr key={sym}>
                  <td><code>{sym}</code></td>
                  <td>{says}</td>
                  <td className="rx-primer-eg">{example}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            How to do a task: look at what every string on the left has in
            common, then at what the ones on the right lack. Build the pattern
            one piece at a time, and read the explanation under the box to check
            each piece says what you meant.
          </p>
        </details>

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
            className={`ws-btn primary${result ? " on" : ""}`}
            disabled={checking || !pattern}
            onClick={() => (result ? setResult(null) : void run())}
            aria-pressed={!!result}
            title={result ? "Click again to hide the result" : undefined}
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
        {pattern ? (
          <div className="rx-explain" aria-live="polite">
            <p className="wb-walkthrough-note">What your pattern says</p>
            <ol>
              {explainPattern(pattern).map((piece, i) => (
                <li key={i} style={{ marginLeft: `${piece.depth * 18}px` }}>
                  <code>{piece.text}</code>
                  <span>{piece.meaning}</span>
                </li>
              ))}
            </ol>
          </div>
        ) : null}
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
