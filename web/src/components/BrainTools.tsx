/**
 * Run it / Explain my code, under a Brain Drills question.
 *
 * Both are for after the answer is in (or when reviewing a question): running
 * the snippet would hand over the answer mid-clock. They are the same things
 * Free mode offers - /api/visualize runs the code, /api/explain reads it - but
 * told which language the drill is in, since that is not necessarily the one
 * the app is set to. Each question gets a fresh copy of this (the parent keys
 * it by question), so nothing carries over when you move on.
 */

import { useEffect, useRef, useState } from "react";

import { explainCode, runBrainCode, visualizeCode } from "../api";
import { canExplain, cleanError, explainSource, isSyntaxError, runnableFor, runsOnTheRunner, type BrainItem, type BrainLang } from "../lib/brainRound";
import type { ExplainResult, VisualizeResult } from "../types";
import { WordsUsed } from "./WordsUsed";

type Props = {
  activityId: string;
  item: BrainItem;
  language: BrainLang;
  /** The question has been answered (or is being reviewed). */
  unlocked: boolean;
};

const LOCKED = "Answer the question first - running or explaining it would give the answer away.";
/** Shown only for a language with no explainer (none of the five drill languages today; the server says which have one). */
const NO_EXPLAIN = "Explain my code does not read this language yet";

export default function BrainTools({ activityId, item, language, unlocked }: Props) {
  const what = runnableFor(activityId, item, language);
  const [ran, setRan] = useState<VisualizeResult | "busy" | "down" | null>(null);
  const [explained, setExplained] = useState<ExplainResult | "busy" | "down" | null>(null);
  const [runOpen, setRunOpen] = useState(true);
  const [explainOpen, setExplainOpen] = useState(true);
  const alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);

  const disabledWhy = !what.ok ? what.reason : unlocked ? "" : LOCKED;

  const run = () => {
    if (!what.ok || !unlocked || ran === "busy") return;
    // Like every other toggle in the app: pressing it again turns it off.
    if (ran) {
      setRan(null);
      return;
    }
    setRan("busy");
    setRunOpen(true);
    // Dart, C and SQL have no tracer, so they are run by the Brain Drills runner instead (a real `dart`, a real C
    // compiler or SQLite, in a throwaway folder).
    (runsOnTheRunner(language)
      ? runBrainCode(what.run || what.code, language as "dart" | "c" | "sql")
      : visualizeCode({ code: what.run || what.code, language }))
      .then((r) => alive.current && setRan(r))
      .catch(() => alive.current && setRan("down"));
  };

  const source = explainSource(activityId, item, language);
  const explainOff = !canExplain(language);
  // Explain has its own reason to be off: it needs code to read, not a program that can run (Flutter widgets cannot run
  // here, but they can be read).
  const explainWhy = explainOff ? NO_EXPLAIN : !source ? "There is no code to explain here." : unlocked ? "" : LOCKED;
  const explain = () => {
    if (explainOff || !source || !unlocked || explained === "busy") return;
    if (explained) {
      setExplained(null);
      return;
    }
    setExplained("busy");
    setExplainOpen(true);
    // The activity id is the glossary's context: it always teaches that drill's words first.
    explainCode(source, language, activityId)
      .then((r) => alive.current && setExplained(r))
      .catch(() => alive.current && setExplained("down"));
  };

  return (
    <section className="brain-tools" aria-label="Run and explain this question's code">
      <div className="brain-tools-bar">
        <button
          type="button"
          className={ran && ran !== "busy" ? "ws-btn on" : "ws-btn"}
          aria-pressed={!!ran && ran !== "busy"}
          onClick={run}
          disabled={!!disabledWhy || ran === "busy"}
          title={
            disabledWhy ||
            (ran && ran !== "busy" ? "Hide the output" : "Run this code for real and show what it prints")
          }
        >
          {ran === "busy" ? "Running…" : ran ? "Hide output" : "Run it"}
        </button>
        <button
          type="button"
          className={explained && explained !== "busy" ? "ws-btn on" : "ws-btn"}
          aria-pressed={!!explained && explained !== "busy"}
          onClick={explain}
          disabled={!!explainWhy || explained === "busy"}
          title={
            explainWhy ||
            (explained && explained !== "busy" ? "Hide the explanation" : "A plain-English walkthrough of this code")
          }
        >
          {explained === "busy" ? "Reading…" : explained ? "Hide explain" : "Explain my code"}
        </button>
        {disabledWhy || explainWhy ? <span className="brain-tools-why">{disabledWhy && explainWhy ? (unlocked ? disabledWhy : LOCKED) : disabledWhy || explainWhy}</span> : null}
      </div>

      {ran && ran !== "busy" ? (
        <div className="brain-tool">
          <button
            type="button"
            className="brain-tool-head"
            aria-expanded={runOpen}
            onClick={() => setRunOpen((o) => !o)}
          >
            <span aria-hidden="true">{runOpen ? "▾" : "▸"}</span> Output
          </button>
          {runOpen ? <RunOutput result={ran} parse={what.ok && what.parseIsTheAnswer} /> : null}
          {runOpen && what.ok && what.code !== item.prompt ? (
            <details className="brain-prog">
              <summary>The program that ran</summary>
              <pre className="brain-run-out">{what.code}</pre>
            </details>
          ) : null}
        </div>
      ) : null}

      {explained && explained !== "busy" ? (
        <div className="brain-tool">
          <button
            type="button"
            className="brain-tool-head"
            aria-expanded={explainOpen}
            onClick={() => setExplainOpen((o) => !o)}
          >
            <span aria-hidden="true">{explainOpen ? "▾" : "▸"}</span> What your code does
          </button>
          {explainOpen ? <ExplainView result={explained} /> : null}
        </div>
      ) : null}
    </section>
  );
}

function RunOutput({ result, parse }: { result: VisualizeResult | "down"; parse: boolean }) {
  if (result === "down") {
    return <p className="explain-note bad">Couldn’t reach the coach - is the API running?</p>;
  }
  const out = (result.stdout ?? "").replace(/\s+$/, "");
  const err = cleanError(result.error ?? result.stderr ?? "");
  const syntax = isSyntaxError(result.error);
  return (
    <div className="brain-run" data-testid="brain-run">
      {parse ? (
        <p className="brain-verdict">
          {syntax ? "It does not parse - that is the whole answer." : "It parses - the parser took it."}
        </p>
      ) : null}
      {out ? <pre className="brain-run-out">{out}</pre> : null}
      {err ? <pre className="brain-run-err">{err}</pre> : null}
      {!out && !err ? <p className="explain-note">It ran and printed nothing.</p> : null}
      {parse && !syntax && err ? (
        <p className="explain-note">It stopped while running, not while parsing (a snippet on its own often lacks the names it uses).</p>
      ) : null}
    </div>
  );
}

/** Same rows as the coach's "What your code does" panel (components/ExplainPanel.tsx), without its refresh and resize chrome. */
function ExplainView({ result }: { result: ExplainResult | "down" }) {
  if (result === "down") {
    return <p className="explain-note bad">Couldn’t reach the coach - is the API running?</p>;
  }
  return (
    <div className="brain-explain" data-testid="brain-explain">
      <p className="explain-summary">{result.summary}</p>
      {result.error_note ? <p className="explain-note bad">{result.error_note}</p> : null}
      {result.lines.length > 0 ? (
        <div className="explain-lines">
          {result.lines.map((L, i) => (
            <div key={`${L.line}-${i}`} className="explain-row" style={{ paddingLeft: 10 + L.depth * 18 }}>
              <code className="explain-code">{L.source || " "}</code>
              <span className="explain-text">{L.text}</span>
            </div>
          ))}
        </div>
      ) : null}
      {result.output_notes.length > 0 ? (
        <div className="explain-output">
          <div className="explain-output-title">Why the output looks like this</div>
          {result.output_notes.map((n, i) => (
            <p key={i} className="explain-note">
              {n}
            </p>
          ))}
        </div>
      ) : null}
      <WordsUsed words={result.words} scope="brain" />
    </div>
  );
}
