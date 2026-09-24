/**
 * SQL case files: a small mystery, solved by querying real PostgreSQL.
 *
 * The query box is for exploring - run anything, as often as you like,
 * against the case's own tables. The answer box is for the one thing
 * each step asks. Steps open one at a time, because each question is
 * aimed by the answer before it.
 *
 * Which steps are solved is kept in this browser per case, so leaving
 * mid-case and coming back picks up where you were. The case itself
 * counts as done on the server when the last step is solved.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { answerCase, fetchCases, queryCase, revealCase } from "../api";
import { LAST_KEYS } from "../lastKeys";
import type { CaseInfo, CaseList } from "../types";

const LAST_KEY = LAST_KEYS.cases;
const SOLVED_KEY = "code-coach:cases-solved";

function nextUp<T extends { done: number; last: string }>(all: T[]): T | null {
  if (!all.length) return null;
  return all.reduce((best, item) => {
    if (item.done !== best.done) return item.done < best.done ? item : best;
    return item.last < best.last ? item : best;
  }, all[0]);
}

function readSolved(): Record<string, number> {
  try {
    const raw = JSON.parse(localStorage.getItem(SOLVED_KEY) ?? "{}");
    return raw && typeof raw === "object" ? raw : {};
  } catch {
    return {};
  }
}

function writeSolved(all: Record<string, number>): void {
  try {
    localStorage.setItem(SOLVED_KEY, JSON.stringify(all));
  } catch {
    /* a blocked store only costs the resume */
  }
}

type StepView = { typed: string; verdict: "" | "right" | "wrong"; lesson: string; hint: boolean };

export default function CaseFiles() {
  const [list, setList] = useState<CaseList | null>(null);
  const [chosen, setChosen] = useState("");
  const [solved, setSolved] = useState<Record<string, number>>(readSolved);
  const [sql, setSql] = useState("");
  const [out, setOut] = useState<{ out: string; err: string } | null>(null);
  const [running, setRunning] = useState(false);
  const [views, setViews] = useState<StepView[]>([]);
  const [reveal, setReveal] = useState<{ query: string } | null>(null);
  const [ending, setEnding] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchCases()
      .then((data) => {
        if (!alive) return;
        setList(data);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* same */
        }
        const start = data.cases.find((c) => c.id === last) ?? nextUp(data.cases);
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, []);

  const item: CaseInfo | null = useMemo(
    () => list?.cases.find((c) => c.id === chosen) ?? null,
    [list, chosen],
  );

  useEffect(() => {
    if (!item) return;
    setSql("");
    setOut(null);
    setReveal(null);
    setEnding("");
    setError("");
    setViews(item.steps.map(() => ({ typed: "", verdict: "", lesson: "", hint: false })));
    try {
      localStorage.setItem(LAST_KEY, item.id);
    } catch {
      /* same */
    }
  }, [item]);

  const reached = Math.min(solved[chosen] ?? 0, item?.steps.length ?? 0);

  const run = useCallback(async () => {
    if (!item || running || !sql.trim()) return;
    setRunning(true);
    try {
      setOut(await queryCase(item.id, sql));
    } catch (e: unknown) {
      setOut({ out: "", err: e instanceof Error ? e.message : String(e) });
    } finally {
      setRunning(false);
    }
  }, [item, sql, running]);

  const setView = (i: number, change: Partial<StepView>) =>
    setViews((was) => was.map((v, j) => (j === i ? { ...v, ...change } : v)));

  const submit = async (i: number) => {
    if (!item) return;
    const typed = views[i]?.typed ?? "";
    if (!typed.trim()) return;
    try {
      const got = await answerCase(item.id, i, typed);
      if (!got.right) {
        setView(i, { verdict: "wrong", lesson: "" });
        return;
      }
      setView(i, { verdict: "right", lesson: got.lesson });
      setReveal(null);
      const next = { ...solved, [item.id]: Math.max(solved[item.id] ?? 0, i + 1) };
      if (i + 1 >= item.steps.length) {
        setEnding(got.ending);
        next[item.id] = 0; // solved: a fresh go next time, for the reps
        setList((was) =>
          was
            ? {
                ...was,
                cases: was.cases.map((c) =>
                  c.id === item.id
                    ? { ...c, done: got.done, last: new Date().toISOString() }
                    : c,
                ),
              }
            : was,
        );
        setSolved(next);
        writeSolved(next);
        return;
      }
      setSolved(next);
      writeSolved(next);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const leastDone = useMemo(() => nextUp(list?.cases ?? []), [list]);

  if (error && !list) return <div className="lessons-empty">Could not load these: {error}</div>;
  if (!list || !item) return <div className="lessons-empty">Loading…</div>;

  // Once the last step is solved the stored count resets for the next go,
  // so the finished case is shown from this go's own verdicts instead.
  const open = ending ? item.steps.length : reached + 1;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Case files</h2>
        <p className="lessons-intro">
          A mystery in a database. Query the tables however you like, then
          answer each step. It runs on real PostgreSQL, and nothing you run
          changes the data for next time.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button type="button" className="ws-btn kata-next" onClick={() => setChosen(leastDone.id)}>
            Next up: {leastDone.title}
          </button>
        ) : null}
        {list.cases.map((c) => (
          <button
            key={c.id}
            type="button"
            className={`lessons-pick${c.id === chosen ? " on" : ""}`}
            onClick={() => setChosen(c.id)}
          >
            <span className="lessons-pick-name">{c.title}</span>
            <span className="lessons-pick-blurb">
              {c.steps.length} steps
              {c.done ? ` · solved ${c.done}×` : ""}
              {solved[c.id] ? ` · on step ${solved[c.id] + 1}` : ""}
            </span>
          </button>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {item.title}
            <span className="predict-lang">PostgreSQL</span>
          </h3>
        </header>
        <p className="lessons-blurb">{item.story}</p>

        <details className="case-tables" open>
          <summary>The tables</summary>
          <ul>
            {item.tables.map((t) => (
              <li key={t.name}>
                <code className="case-table-name">{t.name}</code>{" "}
                <span className="case-table-cols">
                  {t.columns.map((col) => `${col.name} ${col.type}`).join(", ")}
                </span>
              </li>
            ))}
          </ul>
        </details>

        <section className="hunt-panel">
          <h4 className="hunt-panel-head">Query</h4>
          <textarea
            className="wb-code"
            value={sql}
            onChange={(e) => setSql(e.target.value)}
            spellCheck={false}
            rows={5}
            placeholder={`SELECT * FROM ${item.tables[0]?.name ?? "people"};`}
            aria-label="Your query"
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                void run();
              }
            }}
          />
          <div className="wb-actions">
            <button
              type="button"
              className="ws-btn primary"
              disabled={running || !sql.trim()}
              onClick={() => void run()}
            >
              {running ? "Running…" : "Run (Ctrl+Enter)"}
            </button>
          </div>
          {out ? (
            out.err ? (
              <pre className="wb-stderr">{out.err}</pre>
            ) : (
              <pre className="case-result">{out.out}</pre>
            )
          ) : null}
        </section>

        {item.steps.slice(0, open).map((s, i) => {
          const v = views[i] ?? { typed: "", verdict: "", lesson: "", hint: false };
          const done = i < reached || v.verdict === "right";
          return (
            <section key={i} className={`hunt-panel${done ? " case-step-done" : ""}`}>
              <h4 className="hunt-panel-head">Step {i + 1}</h4>
              <p className="wb-prompt">{s.question}</p>
              {done && v.verdict !== "right" ? (
                <p className="wb-verdict ok">Solved.</p>
              ) : (
                <>
                  <div className="wb-actions">
                    <input
                      className="case-answer"
                      value={v.typed}
                      onChange={(e) => setView(i, { typed: e.target.value, verdict: "" })}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") void submit(i);
                      }}
                      placeholder="your answer"
                      aria-label={`Answer to step ${i + 1}`}
                      spellCheck={false}
                      autoComplete="off"
                      disabled={v.verdict === "right"}
                    />
                    {v.verdict === "right" ? null : (
                      <>
                        <button
                          type="button"
                          className="ws-btn primary"
                          disabled={!v.typed.trim()}
                          onClick={() => void submit(i)}
                        >
                          Answer
                        </button>
                        <button
                          type="button"
                          className="ws-btn"
                          onClick={() => setView(i, { hint: !v.hint })}
                        >
                          Hint
                        </button>
                        <button
                          type="button"
                          className="ws-btn"
                          onClick={() => void revealCase(item.id, i).then(setReveal)}
                        >
                          Show a query that finds it
                        </button>
                      </>
                    )}
                  </div>
                  {v.hint ? <p className="wb-answer">{s.hint}</p> : null}
                  {reveal && v.verdict !== "right" && i === open - 1 ? (
                    <div className="kata-answer">
                      <pre className="wb-stderr">{reveal.query}</pre>
                      <button type="button" className="ws-btn" onClick={() => setSql(reveal.query)}>
                        Put it in the query box
                      </button>
                    </div>
                  ) : null}
                  {v.verdict === "wrong" ? (
                    <p className="wb-verdict bad">Not that. Check the query - what else could it be?</p>
                  ) : null}
                  {v.verdict === "right" ? (
                    <>
                      <p className="wb-verdict ok">Right.</p>
                      <p className="kata-bug">
                        <strong>The idea:</strong> {v.lesson}
                      </p>
                    </>
                  ) : null}
                </>
              )}
            </section>
          );
        })}

        {ending ? (
          <section className="hunt-panel case-step-done">
            <h4 className="hunt-panel-head">Case closed</h4>
            <p className="wb-prompt">{ending}</p>
          </section>
        ) : null}
        {error ? <p className="wb-verdict bad">{error}</p> : null}
      </article>
    </div>
  );
}
