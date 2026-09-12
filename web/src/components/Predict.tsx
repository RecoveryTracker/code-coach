/**
 * Predict the output: read the code, say what it prints.
 *
 * The Katas screen asks you to write a function. This asks the other
 * question, and it is the one that finds out whether you know what the
 * language does rather than what you meant it to do.
 *
 * The whole design turns on one thing: you commit before you find out. The
 * answer is not in the payload, the Run button is not on screen, and the
 * only way to see what the snippet prints is to say what you think it prints
 * first. A guess you can check cheaply is not a guess.
 *
 * Then, if you were wrong, Watch it run steps through the same snippet and
 * shows the shared list, the loop variable that outlived its loop, the
 * generator that was already empty. Being wrong and then watching it happen
 * is the point of the mode, and it is the part neither Codewars nor
 * freeCodeCamp can do because neither has a tracer.
 *
 * The explanation arrives either way. Being told only that you were wrong
 * teaches you that you were wrong.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { checkPredict, fetchPredicts } from "../api";
import { VizPanel } from "./VizPanel";
import type { PredictCheck, PredictList, PredictPuzzle } from "../types";

/** What you guessed, per puzzle, so coming back does not lose it. */
const DRAFT_KEY = "code-coach:predict-drafts";

/** Which puzzle you were on. */
const LAST_KEY = "code-coach:predict-last";

function readDrafts(): Record<string, string> {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    return raw ? (JSON.parse(raw) as Record<string, string>) : {};
  } catch {
    return {};
  }
}

function writeDrafts(drafts: Record<string, string>): void {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(drafts));
  } catch {
    /* a blocked store is not worth interrupting practice for */
  }
}

export default function Predict() {
  const [list, setList] = useState<PredictList | null>(null);
  const [chosen, setChosen] = useState("");
  const [guess, setGuess] = useState("");
  const [result, setResult] = useState<PredictCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [watching, setWatching] = useState(false);
  const [error, setError] = useState("");
  const drafts = useRef<Record<string, string>>(readDrafts());

  useEffect(() => {
    let alive = true;
    fetchPredicts()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families.flatMap((f) => f.puzzles);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          last = "";
        }
        const start = all.find((p) => p.id === last) ?? all[0];
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) => {
        if (alive) setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      alive = false;
    };
  }, []);

  const puzzle: PredictPuzzle | null = useMemo(() => {
    if (!list) return null;
    for (const family of list.families) {
      const found = family.puzzles.find((p) => p.id === chosen);
      if (found) return found;
    }
    return null;
  }, [list, chosen]);

  useEffect(() => {
    if (!puzzle) return;
    setGuess(drafts.current[puzzle.id] ?? "");
    setResult(null);
    setWatching(false);
    try {
      localStorage.setItem(LAST_KEY, puzzle.id);
    } catch {
      /* not worth interrupting practice for */
    }
  }, [puzzle]);

  const onGuess = useCallback(
    (next: string) => {
      setGuess(next);
      if (puzzle) {
        drafts.current = { ...drafts.current, [puzzle.id]: next };
        writeDrafts(drafts.current);
      }
    },
    [puzzle],
  );

  const check = useCallback(async () => {
    if (!puzzle || checking) return;
    setChecking(true);
    setError("");
    try {
      setResult(await checkPredict({ puzzle_id: puzzle.id, guess }));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setChecking(false);
    }
  }, [puzzle, guess, checking]);

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !puzzle) return <div className="lessons-empty">Loading…</div>;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Predict</h2>
        <p className="lessons-intro">
          Read it, say what it prints, then find out. Every one of these is
          correct Python that does something most people get wrong first
          time.
        </p>
        {list.families.map((family) => (
          <div key={family.name} className="wb-section">
            <h4 className="wb-section-head">
              {family.name}
              <span className="wb-section-count">
                {family.puzzles.length} to try
              </span>
            </h4>
            {family.puzzles.map((p) => (
              <button
                key={p.id}
                type="button"
                className={`lessons-pick${p.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(p.id)}
              >
                <span className="lessons-pick-name">{p.name}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>{puzzle.name}</h3>
        </header>

        {/* Read-only on purpose. Editing it would answer the question. */}
        <pre className="predict-code">{puzzle.code}</pre>

        <p className="wb-prompt">What does this print?</p>
        <textarea
          className={
            "wb-code" + (result ? (result.passed ? " ok" : " bad") : "")
          }
          value={guess}
          spellCheck={false}
          autoCapitalize="off"
          autoCorrect="off"
          aria-label="What you think it prints"
          placeholder="One line per line of output…"
          onChange={(e) => {
            onGuess(e.target.value);
            // A verdict next to a changed guess says something untrue.
            if (result && !result.passed) setResult(null);
          }}
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
              e.preventDefault();
              void check();
            }
          }}
        />

        <div className="wb-actions">
          <button
            type="button"
            className="ws-btn primary"
            onClick={() => void check()}
            disabled={checking || !guess.trim()}
          >
            {checking ? "Checking…" : "Check"}
          </button>
          <span className="wb-chord">Ctrl+Enter</span>
          <button
            type="button"
            className={watching ? "ws-btn on" : "ws-btn"}
            onClick={() => setWatching((open) => !open)}
            // Only after answering. Stepping through it first is reading
            // the answer, which is the one thing this mode is not for.
            disabled={!result}
            title={
              result
                ? "Step through it and watch it happen"
                : "Say what you think it prints first"
            }
          >
            {watching ? "Hide run" : "Watch it run"}
          </button>
        </div>

        {error ? <p className="wb-verdict bad">{error}</p> : null}

        {result ? (
          <div className="kata-result">
            <p className={result.passed ? "wb-verdict ok" : "wb-verdict bad"}>
              {result.passed
                ? "That is what it prints."
                : "Not what it prints."}
            </p>
            {!result.passed ? (
              <div className="predict-compare">
                <div>
                  <p className="wb-walkthrough-note">You said</p>
                  <pre className="wb-stderr">{result.guess || "(nothing)"}</pre>
                </div>
                <div>
                  <p className="wb-walkthrough-note">It prints</p>
                  <pre className="wb-stderr">{result.expect}</pre>
                </div>
              </div>
            ) : null}
            {/* Either way: a right guess with no explanation leaves you
                unsure whether you knew it or guessed it. */}
            <p className="kata-bug">
              <strong>Why:</strong> {result.why}
            </p>
          </div>
        ) : null}

        {watching && result ? (
          <div className="wb-viz">
            <VizPanel
              getCode={() => puzzle.code}
              patternId={null}
              problemNumber={null}
              resetKey={puzzle.id}
            />
          </div>
        ) : null}
      </article>
    </div>
  );
}
