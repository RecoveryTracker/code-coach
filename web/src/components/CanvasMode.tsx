/**
 * Canvas: write JavaScript that draws, moves and plays.
 *
 * Every other screen runs code where nothing can be seen, which is right
 * for learning the language and wrong for learning games: a game is a
 * picture that changes sixty times a second, and you learn it by watching
 * it. So here the code runs in a canvas beside the editor, and the steps
 * build one small game - Dodge - from a single square to a restart.
 *
 * The preview is a sandboxed iframe with no access to this page: it gets
 * scripts and nothing else, and talks back only by postMessage (errors and
 * console.log). Check does not use it. The server plays the same program in
 * node against the same harness, holding keys and stepping frames, so a
 * check cannot freeze this tab and passes the same way every time.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { checkCanvas, fetchCanvas, fetchCanvasAnswer } from "../api";
import type { CanvasCheck, CanvasList, CanvasStep } from "../types";
import { EditorPane } from "./EditorPane";
import "../styles/canvas.css";

const LAST_KEY = "code-coach:canvas-last";
const DRAFT_KEY = (id: string) => `code-coach:canvas-draft:${id}`;
/** More than a game prints in a minute of play, fewer than slow the page. */
const MAX_LINES = 200;

type Line = { tone: "log" | "warn" | "error"; text: string };

function readStore(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStore(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    /* a blocked store only means the draft is not kept */
  }
}

/**
 * The preview document: the canvas, the harness, then your code in a script
 * of its own. Your code's first line is `start`, so an error the browser
 * reports against the whole document can be given back as your line number.
 */
function previewPage(harness: string, code: string, world = ""): string {
  const safe = (s: string) => s.replace(/<\/script/gi, "<\\/script");
  const before = (start: number) =>
    "<!doctype html><html><head><meta charset=\"utf-8\"><style>"
    + "html,body{margin:0;height:100%;background:#0b0e14;overflow:hidden}"
    + "body{display:flex;align-items:center;justify-content:center}"
    + "canvas{display:block;max-width:100%;max-height:100%;outline:none}"
    + "</style></head><body>"
    + "<canvas width=\"480\" height=\"320\" tabindex=\"0\"></canvas>\n"
    + `<script>${safe(harness)}</script>\n`
    + `<script>__cc.boot('play', ${start});`
    + "document.querySelector('canvas').focus();</script>\n"
    // A track's game, when you program it rather than write it (Farm).
    + (world ? `<script>${safe(world)}</script>\n` : "")
    + "<script>\n";
  // Line numbers do not depend on the number written in, so measure once.
  const start = before(0).split("\n").length;
  return before(start) + safe(code) + "\n</script></body></html>";
}

export default function CanvasMode() {
  const [list, setList] = useState<CanvasList | null>(null);
  const [chosen, setChosen] = useState("");
  const [code, setCode] = useState("");
  const [revision, setRevision] = useState(0);
  const [page, setPage] = useState("");
  const [runs, setRuns] = useState(0);
  const [lines, setLines] = useState<Line[]>([]);
  const [result, setResult] = useState<CanvasCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [error, setError] = useState("");
  const frameRef = useRef<HTMLIFrameElement | null>(null);
  const codeRef = useRef("");
  codeRef.current = code;
  // Read by run(), which the step-change effect calls in the same pass as
  // the step changes - before a re-render could hand it the new step.
  const chosenRef = useRef("");
  chosenRef.current = chosen;

  useEffect(() => {
    let alive = true;
    fetchCanvas()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const last = readStore(LAST_KEY) ?? "";
        const start =
          data.steps.find((s) => s.id === last)
          ?? data.steps.find((s) => s.checked && !s.done)
          ?? data.steps[0];
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, []);

  const item: CanvasStep | null = useMemo(
    () => list?.steps.find((s) => s.id === chosen) ?? null,
    [list, chosen],
  );
  const index = list && item ? list.steps.indexOf(item) : -1;
  const nextStep = list && index >= 0 ? list.steps[index + 1] ?? null : null;
  // Numbered within their own track: Breakout starts again at 1.
  const trackSteps = list && item ? list.steps.filter((s) => s.track === item.track) : [];
  const number = item ? trackSteps.indexOf(item) + 1 : 0;
  const tracks = list ? [...new Set(list.steps.map((s) => s.track))] : [];

  const run = useCallback(
    (source?: string) => {
      if (!list) return;
      setLines([]);
      const step = list.steps.find((s) => s.id === chosenRef.current);
      setPage(previewPage(list.harness, source ?? codeRef.current, step?.world ?? ""));
      setRuns((n) => n + 1);
    },
    [list],
  );

  // A new step: its draft if there is one, else its starter, and run it.
  // Keyed on the id so a pass (which rebuilds the list) does not reload it.
  useEffect(() => {
    if (!list || !chosen) return;
    const step = list.steps.find((s) => s.id === chosen);
    if (!step) return;
    const start = readStore(DRAFT_KEY(step.id)) ?? step.starter;
    setCode(start);
    setRevision((r) => r + 1);
    setResult(null);
    setShowHint(false);
    setAnswer(null);
    setError("");
    writeStore(LAST_KEY, step.id);
    run(start);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chosen, list === null]);

  // What the preview says: console lines and errors, from our frame only.
  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      if (event.source !== frameRef.current?.contentWindow) return;
      const data = event.data as { cc?: boolean; type?: string; level?: string; text?: string; message?: string; line?: number };
      if (!data || !data.cc) return;
      let line: Line | null = null;
      if (data.type === "log") {
        const tone = data.level === "warn" || data.level === "error" ? data.level : "log";
        line = { tone, text: String(data.text ?? "") };
      } else if (data.type === "error") {
        line = {
          tone: "error",
          text: (data.line ? `Line ${data.line}: ` : "") + String(data.message ?? "error"),
        };
      }
      if (line) {
        const add = line;
        setLines((was) => (was.length >= MAX_LINES ? was : [...was, add]));
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  const onChange = useCallback(
    (value: string) => {
      setCode(value);
      if (item) writeStore(DRAFT_KEY(item.id), value === item.starter ? null : value);
    },
    [item],
  );

  const check = useCallback(async () => {
    if (!item || checking) return;
    setChecking(true);
    setError("");
    try {
      const got = await checkCanvas(item.id, codeRef.current);
      setResult(got);
      if (got.passed) {
        setList((was) =>
          was
            ? { ...was, steps: was.steps.map((s) => (s.id === item.id ? { ...s, done: got.done } : s)) }
            : was,
        );
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setChecking(false);
    }
  }, [item, checking]);

  const reset = useCallback(() => {
    if (!item) return;
    writeStore(DRAFT_KEY(item.id), null);
    setCode(item.starter);
    setRevision((r) => r + 1);
    setResult(null);
    run(item.starter);
  }, [item, run]);

  const toggleAnswer = useCallback(async () => {
    if (!item) return;
    if (answer !== null) {
      setAnswer(null);
      return;
    }
    try {
      const got = await fetchCanvasAnswer(item.id);
      setAnswer(got.solution);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [item, answer]);

  if (error && !list) {
    return <div className="lessons-empty">Could not load Canvas: {error}</div>;
  }
  if (!list || !item) return <div className="lessons-empty">Loading…</div>;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Canvas</h2>
        <p className="lessons-intro">
          JavaScript you can watch. Each step is one change to the same game,
          and Check plays it - holding keys, counting frames - to see that it
          does what the step asks.
        </p>
        {tracks.map((track) => {
          const steps = list.steps.filter((s) => s.track === track);
          const passed = steps.filter((s) => s.checked && s.done).length;
          const checked = steps.filter((s) => s.checked).length;
          return (
            <div key={track} className="wb-section">
              <h4 className="wb-section-head">
                {track}
                <span className="wb-section-count">
                  {passed}/{checked}
                </span>
              </h4>
              {steps.map((s, i) => (
                <button
                  key={s.id}
                  type="button"
                  className={`lessons-pick${s.id === chosen ? " on" : ""}`}
                  onClick={() => setChosen(s.id)}
                >
                  <span className="lessons-pick-name">
                    {i + 1}. {s.title}
                  </span>
                  {s.done ? <span className="lessons-pick-blurb">passed {s.done}&#215;</span> : null}
                </button>
              ))}
            </div>
          );
        })}
      </nav>

      <article className="lessons-open wb canvas-open">
        <header>
          <h3>
            {item.track} {number}. {item.title}
            <span className="predict-lang">JavaScript</span>
          </h3>
        </header>
        <p className="canvas-teaches">{item.teaches}</p>
        <p className="wb-prompt canvas-goal">
          <strong>Your turn:</strong> {item.goal}
        </p>

        <div className="canvas-split">
          <div className="canvas-editor">
            <EditorPane
              code={code}
              revision={revision}
              onChange={onChange}
              onRun={() => run()}
              language="javascript"
              fileName="game.js"
            />
          </div>
          <div className="canvas-side">
            <iframe
              key={runs}
              ref={frameRef}
              className="canvas-frame"
              title="Your game"
              sandbox="allow-scripts"
              srcDoc={page}
              onLoad={() => frameRef.current?.focus()}
            />
            <p className="canvas-tip">Click the game to give it the keyboard.</p>
            <div className="canvas-console" aria-live="polite">
              {lines.length === 0 ? (
                <span className="canvas-console-empty">console.log output and errors show here</span>
              ) : (
                lines.map((l, i) => (
                  <div key={i} className={`canvas-line ${l.tone}`}>
                    {l.text}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="wb-actions">
          <button type="button" className="ws-btn" onClick={() => run()} title="Run it again from the start (Ctrl+Enter)">
            Run
          </button>
          {item.checked ? (
            <button
              type="button"
              className={`ws-btn primary${result ? " on" : ""}`}
              onClick={() => (result ? setResult(null) : void check())}
              disabled={checking}
              aria-pressed={result !== null}
              title={result ? "Click again to hide the result" : "Play it and see if it does what the step asks"}
            >
              {checking ? "Checking…" : "Check"}
            </button>
          ) : null}
          {item.hint ? (
            <button
              type="button"
              className={`ws-btn${showHint ? " on" : ""}`}
              onClick={() => setShowHint((v) => !v)}
              aria-pressed={showHint}
            >
              Hint
            </button>
          ) : null}
          {item.checked ? (
            <button
              type="button"
              className={`ws-btn${answer !== null ? " on" : ""}`}
              onClick={() => void toggleAnswer()}
              aria-pressed={answer !== null}
              title="One way to write it - after you've had a go"
            >
              Answer
            </button>
          ) : null}
          <button type="button" className="ws-btn" onClick={reset} title="Put back the code this step started with">
            Start over
          </button>
          {nextStep && result?.passed ? (
            <button type="button" className="ws-btn primary" onClick={() => setChosen(nextStep.id)}>
              Next: {nextStep.title} →
            </button>
          ) : null}
        </div>

        {error ? <p className="wb-verdict bad">{error}</p> : null}
        {result ? (
          <p className={result.passed ? "wb-verdict ok" : "wb-verdict bad"}>
            {result.passed ? `It works. Passed ${result.done}× now.` : result.message}
          </p>
        ) : null}
        {showHint && item.hint ? (
          <p className="canvas-hint">
            <strong>Hint:</strong> <code>{item.hint}</code>
          </p>
        ) : null}
        {answer !== null ? <pre className="canvas-answer">{answer}</pre> : null}
      </article>
    </div>
  );
}
