/**
 * Two-part puzzles: solve part one, and part two changes the rules.
 *
 * Part two opens once part one passes, and your part-one code comes with
 * it, with an empty part-two function added underneath. Whether the
 * helper you wrote for part one can be reused is the lesson, so the code
 * is never taken away.
 *
 * Follows the language picked at the top. Puzzles have answers in
 * Python and JavaScript; in anything else the screen says so rather than
 * quietly handing over a different language.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkPuzzle, fetchPuzzleAnswer, fetchPuzzles } from "../api";
import { LAST_KEYS } from "../lastKeys";
import type { KataCaseResult, PuzzleCheck, PuzzleInfo, PuzzleList } from "../types";

const LAST_KEY = LAST_KEYS.puzzles;
const OPENED_KEY = "code-coach:puzzles-part-two";

function nextUp<T extends { done: number; last: string }>(all: T[]): T | null {
  if (!all.length) return null;
  return all.reduce((best, item) => {
    if (item.done !== best.done) return item.done < best.done ? item : best;
    return item.last < best.last ? item : best;
  }, all[0]);
}

/** A value as it would be written in the language being practised. */
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

function stub(name: string, params: string[], language: string): string {
  return language === "python"
    ? `def ${name}(${params.join(", ")}):\n    pass\n`
    : `function ${name}(${params.join(", ")}) {\n}\n`;
}

/** Puzzles whose part two is open, per language: "id:language". */
function readOpened(): string[] {
  try {
    const raw = JSON.parse(localStorage.getItem(OPENED_KEY) ?? "[]");
    return Array.isArray(raw) ? raw : [];
  } catch {
    return [];
  }
}

export default function Puzzles({ language }: { language: string }) {
  const [list, setList] = useState<PuzzleList | null>(null);
  const [chosen, setChosen] = useState("");
  const [opened, setOpened] = useState<string[]>(readOpened);
  const [part, setPart] = useState<1 | 2>(1);
  const [code, setCode] = useState("");
  const [result, setResult] = useState<PuzzleCheck | null>(null);
  const [running, setRunning] = useState(false);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");

  const supported = list ? list.languages.includes(language) : true;
  const names = list?.names[language] ?? ["", ""];

  useEffect(() => {
    let alive = true;
    fetchPuzzles()
      .then((data) => {
        if (!alive) return;
        setList(data);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* same */
        }
        const start = data.puzzles.find((p) => p.id === last) ?? nextUp(data.puzzles);
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, []);

  const item: PuzzleInfo | null = useMemo(
    () => list?.puzzles.find((p) => p.id === chosen) ?? null,
    [list, chosen],
  );

  const key = `${chosen}:${language}`;
  const twoOpen = opened.includes(key);

  // A new puzzle or a new language starts at part one with a fresh stub.
  useEffect(() => {
    if (!item || !supported) return;
    setPart(1);
    setCode(stub(names[0], item.parts[0].params, language));
    setResult(null);
    setAnswer("");
    setError("");
    try {
      localStorage.setItem(LAST_KEY, item.id);
    } catch {
      /* same */
    }
    // names follows language, so language is the dependency that matters
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [item, language, supported]);

  const goToPartTwo = (from: string) => {
    if (!item) return;
    setPart(2);
    setResult(null);
    setAnswer("");
    const already = from.includes(names[1]);
    setCode(already ? from : `${from.trimEnd()}\n\n\n${stub(names[1], item.parts[1].params, language)}`);
  };

  const run = useCallback(async () => {
    if (!item || running) return;
    setRunning(true);
    setError("");
    try {
      const got = await checkPuzzle(item.id, part, code, language);
      setResult(got);
      if (got.passed && part === 1 && !opened.includes(key)) {
        const next = [...opened, key];
        setOpened(next);
        try {
          localStorage.setItem(OPENED_KEY, JSON.stringify(next));
        } catch {
          /* same */
        }
      }
      if (got.passed && part === 2) {
        setList((was) =>
          was
            ? {
                ...was,
                puzzles: was.puzzles.map((p) =>
                  p.id === item.id ? { ...p, done: got.done, last: new Date().toISOString() } : p,
                ),
              }
            : was,
        );
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }, [item, part, code, language, running, opened, key]);

  const leastDone = useMemo(() => nextUp(list?.puzzles ?? []), [list]);

  if (error && !list) return <div className="lessons-empty">Could not load these: {error}</div>;
  if (!list) return <div className="lessons-empty">Loading…</div>;
  if (!supported) {
    return (
      <div className="lessons-empty">
        No puzzles in this language yet. There are puzzles in Python and
        JavaScript — switch the language at the top to try them.
      </div>
    );
  }
  if (!item) return <div className="lessons-empty">Loading…</div>;

  const brief = item.parts[part - 1];
  const name = names[part - 1];
  const lines = code.split("\n").length;

  const caseLine = (c: KataCaseResult) =>
    c.passed
      ? `→ ${show(c.want, language)}`
      : c.error
        ? `raised ${c.error}`
        : `gave ${show(c.got, language)}, wanted ${show(c.want, language)}`;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Puzzles</h2>
        <p className="lessons-intro">
          Two parts each. Solve part one and part two opens — same input, a
          new question, and your code is still there to change.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button type="button" className="ws-btn kata-next" onClick={() => setChosen(leastDone.id)}>
            Next up: {leastDone.title}
          </button>
        ) : null}
        {list.puzzles.map((p) => (
          <button
            key={p.id}
            type="button"
            className={`lessons-pick${p.id === chosen ? " on" : ""}`}
            onClick={() => setChosen(p.id)}
          >
            <span className="lessons-pick-name">{p.title}</span>
            <span className="lessons-pick-blurb">
              {"★".repeat(p.done ? 2 : opened.includes(`${p.id}:${language}`) ? 1 : 0) || "not started"}
              {p.done ? ` · solved ${p.done}×` : ""}
            </span>
          </button>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {item.title}
            <span className="predict-lang">{language === "python" ? "Python" : "JavaScript"}</span>
          </h3>
        </header>
        <p className="lessons-blurb">{item.story}</p>

        <div className="pz-tabs" role="tablist">
          {[1, 2].map((n) => (
            <button
              key={n}
              type="button"
              role="tab"
              aria-selected={part === n}
              className={`pz-tab${part === n ? " on" : ""}`}
              disabled={n === 2 && !twoOpen}
              onClick={() => (n === 1 ? setPart(1) : goToPartTwo(code))}
              title={n === 2 && !twoOpen ? "Solve part one to open part two" : undefined}
            >
              Part {n === 1 ? "one" : "two"}
              {n === 2 && !twoOpen ? " 🔒" : ""}
            </button>
          ))}
        </div>

        <section className="hunt-panel">
          <p className="wb-prompt">{brief.brief}</p>
          <pre className="pz-example">{brief.example}</pre>
          <p className="wb-walkthrough-note">
            Write <code>{name}({brief.params.join(", ")})</code>.
          </p>
          <textarea
            className="wb-code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
            rows={Math.max(10, lines + 1)}
            aria-label={`Your ${name}`}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                void run();
              }
            }}
          />
          <div className="wb-actions">
            <button type="button" className="ws-btn primary" disabled={running} onClick={() => void run()}>
              {running ? "Running…" : `Run part ${part === 1 ? "one" : "two"}`}
            </button>
            <button
              type="button"
              className="ws-btn"
              onClick={() =>
                void fetchPuzzleAnswer(item.id, part, language).then((got) => setAnswer(got.code))
              }
            >
              Show an answer
            </button>
          </div>
          {answer ? (
            <div className="kata-answer">
              <p className="wb-walkthrough-note">One way to write it:</p>
              <pre className="wb-stderr">{answer}</pre>
            </div>
          ) : null}

          {result ? (
            result.broke ? (
              <div className="kata-result">
                <p className="wb-verdict bad">This did not run:</p>
                <pre className="wb-stderr">{result.broke}</pre>
              </div>
            ) : (
              <div className="kata-result">
                <p className={result.passed ? "wb-verdict ok" : "wb-verdict bad"}>
                  {result.passed
                    ? `All ${result.total} cases pass.`
                    : `${result.count} of ${result.total} cases pass.`}
                </p>
                <ul className="kata-cases">
                  {result.results.map((c, i) => (
                    <li key={i} className={`kata-case${c.passed ? " ok" : " bad"}`}>
                      <code className="mono">
                        {name}({c.args.map((a) => show(a, language)).join(", ")})
                      </code>
                      <span className="kata-case-got">{caseLine(c)}</span>
                    </li>
                  ))}
                </ul>
                {result.passed && part === 1 ? (
                  <button type="button" className="ws-btn primary" onClick={() => goToPartTwo(code)}>
                    On to part two →
                  </button>
                ) : null}
                {result.passed && part === 2 ? (
                  <p className="kata-bug">
                    <strong>The idea:</strong> {result.lesson}
                  </p>
                ) : null}
              </div>
            )
          ) : null}
        </section>
        {error ? <p className="wb-verdict bad">{error}</p> : null}
      </article>
    </div>
  );
}
