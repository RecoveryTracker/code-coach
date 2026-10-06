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
 *
 * The To-do track works a web page instead of a canvas: index.html and
 * style.css sit beside app.js, to read. A page's check needs a real DOM, so
 * it runs here in the browser, in a second sandboxed frame, hidden, which
 * loads the page the server builds with the check inside and posts back the
 * verdict; the server then counts the pass. The sandbox has no localStorage
 * of its own, so the preview's is kept here between Runs - Run is a reload.
 */

import Editor, { type BeforeMount, type OnMount } from "@monaco-editor/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { checkCanvas, fetchCanvas, fetchCanvasAnswer, fetchCanvasPage, recordCanvasPass } from "../api";
import { defineEditorThemes, editorThemeFor, useSkin } from "../skins";
import type { CanvasCheck, CanvasList, CanvasStep } from "../types";
import { EditorPane } from "./EditorPane";
import "../styles/canvas.css";

const LAST_KEY = "code-coach:canvas-last";
const DRAFT_KEY = (id: string) => `code-coach:canvas-draft:${id}`;
/** More than a game prints in a minute of play, fewer than slow the page. */
const MAX_LINES = 200;
/** Far longer than any page check takes; short enough to call a loop endless. */
const CHECK_TIMEOUT_MS = 10000;

type Line = { tone: "log" | "warn" | "error"; text: string };
type Verdict = { passed: boolean; message: string };
type PageFile = "app.js" | "index.html" | "style.css";

const PAGE_FILES: PageFile[] = ["app.js", "index.html", "style.css"];

const RELOAD_NOTE =
  "The form was submitted and nothing called event.preventDefault(), so the page "
  + "reloaded - and everything added since it loaded is gone.";
const TIMEOUT_NOTE =
  "The check ran out of time. Is there a loop that never ends - a while whose "
  + "condition never turns false?";

const VIEW_OPTIONS = {
  readOnly: true,
  domReadOnly: true,
  fontSize: 14,
  fontFamily: '"SF Mono", Menlo, Monaco, Consolas, ui-monospace, monospace',
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  wordWrap: "on" as const,
  automaticLayout: true,
  padding: { top: 12, bottom: 12 },
  renderLineHighlight: "none" as const,
};

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

/** index.html or style.css, to read beside app.js - highlighted, not editable. */
function FileView({ text, language }: { text: string; language: string }) {
  const skin = useSkin();
  const beforeMount: BeforeMount = (monaco) => defineEditorThemes(monaco);
  // Sized at once: automaticLayout waits for the next frame to measure, and
  // a tab opened in a window that isn't drawing would stay a 5px square.
  const onMount: OnMount = (editor) => editor.layout();
  return (
    <Editor
      height="100%"
      language={language}
      theme={editorThemeFor(skin)}
      value={text}
      beforeMount={beforeMount}
      onMount={onMount}
      options={VIEW_OPTIONS}
    />
  );
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
  // Page steps only: the file on show, the preview's localStorage, and the
  // hidden page a check is playing.
  const [file, setFile] = useState<PageFile>("app.js");
  const [stored, setStored] = useState<Record<string, string>>({});
  const [checkPage, setCheckPage] = useState("");
  const [checkRuns, setCheckRuns] = useState(0);
  const frameRef = useRef<HTMLIFrameElement | null>(null);
  const checkFrameRef = useRef<HTMLIFrameElement | null>(null);
  const codeRef = useRef("");
  codeRef.current = code;
  // Read by run(), which the step-change effect calls in the same pass as
  // the step changes - before a re-render could hand it the new step.
  const chosenRef = useRef("");
  chosenRef.current = chosen;
  /** Each page step's localStorage, as the preview last left it. */
  const storageRef = useRef<Record<string, Record<string, string>>>({});
  /** Hands the hidden check page's verdict to the check waiting for it. */
  const verdictRef = useRef<((v: Verdict) => void) | null>(null);
  /** Only the newest Run's page is shown, if two are fetched at once. */
  const runTicket = useRef(0);

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
  const onPage = item?.kind === "dom";

  const run = useCallback(
    (source?: string, keepLines = false) => {
      if (!list) return;
      if (!keepLines) setLines([]);
      const step = list.steps.find((s) => s.id === chosenRef.current);
      const program = source ?? codeRef.current;
      const ticket = ++runTicket.current;
      if (step?.kind === "dom") {
        // The server builds a page step's page, so the preview loads the
        // same page a check does.
        fetchCanvasPage(step.id, program, "play", storageRef.current[step.id] ?? {})
          .then((got) => {
            if (ticket !== runTicket.current) return;
            setPage(got.page);
            setRuns((n) => n + 1);
          })
          .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
        return;
      }
      setPage(previewPage(list.harness, program, step?.world ?? ""));
      setRuns((n) => n + 1);
    },
    [list],
  );
  const runRef = useRef(run);
  runRef.current = run;

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
    setFile("app.js");
    setStored(storageRef.current[step.id] ?? {});
    writeStore(LAST_KEY, step.id);
    run(start);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chosen, list === null]);

  // What the preview says - console lines, errors, its localStorage, a
  // form that would have reloaded it - and the hidden check page's verdict.
  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      const data = event.data as {
        cc?: boolean;
        type?: string;
        level?: string;
        text?: string;
        message?: string;
        line?: number;
        passed?: boolean;
        items?: Record<string, string>;
      };
      if (!data || !data.cc) return;
      if (checkFrameRef.current && event.source === checkFrameRef.current.contentWindow) {
        if (data.type === "result") {
          verdictRef.current?.({ passed: Boolean(data.passed), message: String(data.message ?? "") });
        }
        return;
      }
      if (event.source !== frameRef.current?.contentWindow) return;
      if (data.type === "storage") {
        const items = data.items ?? {};
        storageRef.current[chosenRef.current] = items;
        setStored(items);
        return;
      }
      if (data.type === "reload") {
        setLines((was) => [...was, { tone: "warn", text: RELOAD_NOTE }]);
        runRef.current(undefined, true);
        return;
      }
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

  /** Load a page step's check page in the hidden frame and wait for its verdict. */
  const checkInBrowser = useCallback(async (stepId: string, program: string): Promise<Verdict> => {
    const built = await fetchCanvasPage(stepId, program, "check");
    try {
      return await new Promise<Verdict>((resolve) => {
        const timer = window.setTimeout(() => resolve({ passed: false, message: TIMEOUT_NOTE }), CHECK_TIMEOUT_MS);
        verdictRef.current = (v) => {
          window.clearTimeout(timer);
          resolve(v);
        };
        setCheckPage(built.page);
        setCheckRuns((n) => n + 1);
      });
    } finally {
      verdictRef.current = null;
      setCheckPage("");
    }
  }, []);

  const check = useCallback(async () => {
    if (!item || checking) return;
    const id = item.id;
    setChecking(true);
    setError("");
    try {
      let got: CanvasCheck;
      if (item.kind === "dom") {
        const verdict = await checkInBrowser(id, codeRef.current);
        got = verdict.passed ? await recordCanvasPass(id) : { ...verdict, done: 0 };
      } else {
        got = await checkCanvas(id, codeRef.current);
      }
      if (got.passed) {
        setList((was) =>
          was ? { ...was, steps: was.steps.map((s) => (s.id === id ? { ...s, done: got.done } : s)) } : was,
        );
      }
      // Moved on while it ran: the count is kept, the verdict isn't shown.
      if (chosenRef.current === id) setResult(got);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setChecking(false);
    }
  }, [item, checking, checkInBrowser]);

  const reset = useCallback(() => {
    if (!item) return;
    writeStore(DRAFT_KEY(item.id), null);
    setCode(item.starter);
    setRevision((r) => r + 1);
    setResult(null);
    run(item.starter);
  }, [item, run]);

  /** Empty the preview's localStorage - a first visit, as far as the page knows. */
  const clearStorage = useCallback(() => {
    if (!item) return;
    delete storageRef.current[item.id];
    setStored({});
    run();
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

  const storedKeys = Object.keys(stored).length;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Canvas</h2>
        <p className="lessons-intro">
          JavaScript you can watch. Each step is one change to the same
          program, and Check runs it - holding keys and counting frames, or
          clicking and typing on the page - to see that it does what the
          step asks.
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
          <div className={`canvas-editor${onPage ? " has-files" : ""}`}>
            {onPage ? (
              <div className="canvas-files" role="tablist" aria-label="Files">
                {PAGE_FILES.map((f) => (
                  <button
                    key={f}
                    type="button"
                    role="tab"
                    aria-selected={file === f}
                    className={`canvas-file${file === f ? " on" : ""}`}
                    onClick={() => setFile(f)}
                  >
                    {f}
                  </button>
                ))}
                <span className="canvas-file-note">
                  {file === "app.js" ? "your code" : "to read - your code goes in app.js"}
                </span>
              </div>
            ) : null}
            <div className="canvas-editor-body" hidden={onPage && file !== "app.js"}>
              <EditorPane
                code={code}
                revision={revision}
                onChange={onChange}
                onRun={() => run()}
                language="javascript"
                fileName={onPage ? "app.js" : "game.js"}
              />
            </div>
            {onPage && file !== "app.js" ? (
              <div className="canvas-editor-body">
                <FileView
                  key={file}
                  text={file === "index.html" ? item.page : item.css}
                  language={file === "index.html" ? "html" : "css"}
                />
              </div>
            ) : null}
          </div>
          <div className="canvas-side">
            <iframe
              key={runs}
              ref={frameRef}
              className={`canvas-frame${onPage ? " page" : ""}`}
              title={onPage ? "Your page" : "Your game"}
              sandbox={onPage ? "allow-scripts allow-forms" : "allow-scripts"}
              srcDoc={page}
              onLoad={() => {
                if (!onPage) frameRef.current?.focus();
              }}
            />
            {onPage ? (
              <p className="canvas-tip">
                The page is live: click and type in it. Run reloads it.
                {storedKeys ? (
                  <>
                    {" "}
                    localStorage holds {storedKeys} {storedKeys === 1 ? "key" : "keys"}.{" "}
                    <button type="button" className="canvas-link" onClick={clearStorage}>
                      Clear it
                    </button>
                  </>
                ) : null}
              </p>
            ) : (
              <p className="canvas-tip">Click the game to give it the keyboard.</p>
            )}
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

        {checkPage ? (
          <iframe
            key={`check-${checkRuns}`}
            ref={checkFrameRef}
            className="canvas-check-frame"
            title="Check"
            aria-hidden="true"
            tabIndex={-1}
            sandbox="allow-scripts"
            srcDoc={checkPage}
          />
        ) : null}

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
              title={
                result
                  ? "Click again to hide the result"
                  : onPage
                    ? "Use the page and see if it does what the step asks"
                    : "Play it and see if it does what the step asks"
              }
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
