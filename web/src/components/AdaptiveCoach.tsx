import { useState, type ReactNode } from "react";
import { chatWithCoach, explainCode } from "../api";
import { VizPanel } from "./VizPanel";
import {
  CurriculumNav,
  type CurriculumClass,
} from "./CurriculumNav";
import type {
  CheckItem,
  DrillEvaluateResult,
  ExplainResult,
  PracticeSession,
} from "../types";

type Props = {
  session: PracticeSession;
  result: DrillEvaluateResult | null;
  checks: CheckItem[];
  exerciseIndex: number;
  exerciseDone: boolean;
  onClassDelta: (d: number) => void;
  onLessonDelta: (d: number) => void;
  onExerciseDelta: (d: number) => void;
  onSelectClass: (id: string) => void;
  onSelectLesson: (n: number) => void;
  /** Advance to the next exercise — only offered once the check passes. */
  onContinue: () => void;
  /** Begin dragging the explain panel's bottom edge. */
  onExplainDragStart: () => void;
  /** Begin dragging the message box's bottom edge. */
  onMsgDragStart: () => void;
  /** Message box folded to a single line. */
  msgCollapsed: boolean;
  onToggleMsg: () => void;
  /** Begin dragging the "Watch it run" panel's bottom edge. */
  onVizDragStart: () => void;
  onBackFromReview: () => void;
  watching: boolean;
  /** Current editor buffer — read fresh when the student asks for an explanation. */
  getCode: () => string;
  /** App title, centred on the coach line (there's no header row anymore). */
  brand: ReactNode;
  /** Save / Load / Progress / Free mode / Start over / Run. */
  toolbar: ReactNode;
};

export function AdaptiveCoach({
  session,
  result,
  checks,
  exerciseIndex,
  exerciseDone,
  onClassDelta,
  onLessonDelta,
  onExerciseDelta,
  onSelectClass,
  onSelectLesson,
  onContinue,
  onExplainDragStart,
  onMsgDragStart,
  msgCollapsed,
  onToggleMsg,
  onVizDragStart,
  onBackFromReview,
  watching,
  getCode,
  brand,
  toolbar,
}: Props) {
  const total = session.steps.length || checks.length || 1;
  const endless = Boolean(session.endless);
  // Endless mode never "completes" the lesson — next window loads automatically
  const complete = !endless && exerciseIndex >= total;
  const step = exerciseIndex < total ? session.steps[exerciseIndex] : null;
  const isBuild = session.lesson_role === "build" || step?.kind === "build";
  const isReview = Boolean(session.is_review);
  const multiLine = Boolean(step?.label && step.label.includes("\n"));
  const curriculum = (session.curriculum ?? []) as CurriculumClass[];

  const [chatOpen, setChatOpen] = useState(false);
  const [vizOpen, setVizOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatLog, setChatLog] = useState<
    { role: "you" | "coach"; text: string }[]
  >([
    {
      role: "coach",
      text: endless
        ? "Endless type-along. Turn Difficulty up for multi-line and functions. You stay here until you change Lesson."
        : "Use Class / Lesson / Exercise to navigate. Exercises auto-advance when done.",
    },
  ]);
  const [chatBusy, setChatBusy] = useState(false);
  const [explainOpen, setExplainOpen] = useState(false);
  const [explainBusy, setExplainBusy] = useState(false);
  const [explanation, setExplanation] = useState<ExplainResult | null>(null);
  const [explainError, setExplainError] = useState(false);

  async function refreshExplanation() {
    if (explainBusy) return;
    setExplainBusy(true);
    setExplainError(false);
    try {
      const data = await explainCode(getCode());
      setExplanation(data);
    } catch {
      setExplainError(true);
    } finally {
      setExplainBusy(false);
    }
  }

  function toggleExplain() {
    setExplainOpen((open) => {
      if (!open) void refreshExplanation();
      return !open;
    });
  }

  let statusText: string;
  let statusClass: string;
  if (complete) {
    statusText = "Lesson done — change Class/Lesson to continue.";
    statusClass = "good";
  } else if (exerciseDone) {
    // No trailing "more coming…" — nothing advances until Continue is pressed.
    statusText = "Got it";
    statusClass = "good";
  } else if (result?.status === "error" || result?.tone === "error") {
    statusText = result.observation || "Error";
    statusClass = "bad";
  } else if (result?.status === "wrong" || result?.tone === "wrong") {
    statusText = result.observation || "Not yet";
    statusClass = "bad";
  } else if (watching) {
    statusText = "…";
    statusClass = "mid";
  } else {
    statusText = isBuild
      ? "Build this"
      : multiLine
        ? "Type this block"
        : "Type this";
    statusClass = "idle";
  }

  // The coach's "line 8 doesn't match / should be / you typed" note is
  // multi-line. The status strip is one line, so only the headline goes there
  // and the aligned detail renders below in a monospace block.
  const [statusHead, ...statusDetail] = statusText.split("\n");
  const diffText = statusClass === "bad" ? statusDetail.join("\n") : "";
  // Whatever the coach has to say when it isn't pointing at a bad line. The
  // slot below is always rendered at a fixed height, so this keeps it useful
  // rather than blank — and the editor never shifts when a message arrives.
  const restingNote =
    result?.guidance || step?.tip || session.prompt || "";

  async function sendChat() {
    const msg = chatInput.trim();
    if (!msg || chatBusy) return;
    setChatInput("");
    setChatLog((L) => [...L, { role: "you", text: msg }]);
    setChatBusy(true);
    try {
      const { reply } = await chatWithCoach(msg);
      setChatLog((L) => [...L, { role: "coach", text: reply }]);
    } catch {
      setChatLog((L) => [
        ...L,
        { role: "coach", text: "Chat unavailable — API down?" },
      ]);
    } finally {
      setChatBusy(false);
    }
  }

  return (
    <div className="coach-banner">
      {isReview ? (
        <div className="coach-banner-status good">
          <span className="live-dot" />
          <span className="coach-banner-status-text">Supporting practice</span>
          <button
            type="button"
            className="coach-banner-btn"
            onClick={onBackFromReview}
          >
            ← Back to lesson
          </button>
          <button
            type="button"
            className={`coach-chat-toggle${explainOpen ? " active" : ""}`}
            onClick={toggleExplain}
          >
            {explainOpen ? "Hide explain" : "Explain my code"}
          </button>
          {brand}
          {toolbar}
        </div>
      ) : (
        <CurriculumNav
          session={session}
          curriculum={curriculum}
          exerciseIndex={exerciseIndex}
          exerciseTotal={total}
          statusText={statusHead}
          statusClass={statusClass}
          exerciseDone={exerciseDone}
          onContinue={onContinue}
          watching={watching}
          chatOpen={chatOpen}
          onToggleChat={() => setChatOpen((o) => !o)}
          explainOpen={explainOpen}
          onToggleExplain={toggleExplain}
          onClassDelta={onClassDelta}
          onLessonDelta={onLessonDelta}
          onExerciseDelta={onExerciseDelta}
          onSelectClass={onSelectClass}
          onSelectLesson={onSelectLesson}
          vizOpen={vizOpen}
          onToggleViz={() => setVizOpen((o) => !o)}
          brand={brand}
          toolbar={toolbar}
        />
      )}

      {/* The "type this" block now lives in <TypeTarget/>, in its own column
          beside the editor, where a long solution has room to be seen. */}

      {/* Always present, always the same height. Messages scroll inside it
          instead of growing the strip and pushing the editor down. */}
      <div
        className={`coach-msg ${statusClass}${msgCollapsed ? " collapsed" : ""}`}
        aria-live="polite"
      >
        <button
          type="button"
          className="coach-msg-fold"
          onClick={onToggleMsg}
          title={
            msgCollapsed
              ? "Expand the coach's notes"
              : "Collapse to a single line"
          }
          aria-expanded={!msgCollapsed}
        >
          {msgCollapsed ? "▾" : "▴"}
        </button>

        {/* Content scrolls in here so the grip below stays put at the
            panel's bottom edge, the way the other panels' grips do. */}
        <div className="coach-msg-body">
          {msgCollapsed ? (
            <p className="coach-msg-oneline">{statusHead}</p>
          ) : statusClass === "bad" ? (
            // The full complaint goes here, where there's room. The one-line
            // status strip only ever shows its first line.
            diffText ? (
              <pre className="coach-msg-diff">{statusText}</pre>
            ) : (
              <p className="coach-msg-alert">{statusText}</p>
            )
          ) : (
            <p className="coach-msg-resting">{restingNote}</p>
          )}
        </div>

        {!msgCollapsed ? (
          <div
            className="coach-msg-grip"
            title="Drag to resize"
            onPointerDown={(e) => {
              e.preventDefault();
              onMsgDragStart();
            }}
          />
        ) : null}
      </div>

      {/* Sits alongside "Explain my code" — same shape of tool, same place.
          It was buried at the bottom of the Problem panel's scroll area,
          which is a ~95px box, so nobody ever found it. */}
      {vizOpen ? (
        <div className="coach-viz">
          <div className="coach-explain-head">
            <span className="coach-explain-title">Watch it run</span>
            <button
              type="button"
              className="coach-chat-toggle"
              onClick={() => setVizOpen(false)}
            >
              Hide
            </button>
          </div>
          <div className="coach-viz-body">
            <VizPanel
              getCode={getCode}
              patternId={step?.study?.lesson?.id ?? null}
              problemNumber={step?.study?.problem?.number ?? null}
              resetKey={`${session.drill_id}:${exerciseIndex}`}
            />
          </div>
          <div
            className="coach-explain-grip"
            title="Drag to resize"
            onPointerDown={(e) => {
              e.preventDefault();
              onVizDragStart();
            }}
          />
        </div>
      ) : null}

      {explainOpen ? (
        <div className="coach-explain">
          <div className="coach-explain-head">
            <span className="coach-explain-title">
              {explainBusy ? "Reading your code…" : "What your code does"}
            </span>
            <button
              type="button"
              className="coach-chat-toggle"
              onClick={() => void refreshExplanation()}
              disabled={explainBusy}
              title="Re-explain after you edit"
            >
              Refresh
            </button>
          </div>
          {explainError ? (
            <div className="coach-explain-body">
              <p className="explain-note bad">
                Couldn’t reach the coach — is the API running?
              </p>
            </div>
          ) : explanation ? (
            <div className="coach-explain-body">
              <p className="explain-summary">{explanation.summary}</p>
              {explanation.error_note ? (
                <p className="explain-note bad">{explanation.error_note}</p>
              ) : null}
              {explanation.lines.length > 0 ? (
                <div className="explain-lines">
                  {explanation.lines.map((L, i) => (
                    <div
                      key={`${L.line}-${i}`}
                      className="explain-row"
                      style={{ paddingLeft: 10 + L.depth * 18 }}
                    >
                      <code className="explain-code">{L.source || " "}</code>
                      <span className="explain-text">{L.text}</span>
                    </div>
                  ))}
                </div>
              ) : null}
              {explanation.output_notes.length > 0 ? (
                <div className="explain-output">
                  <div className="explain-output-title">
                    Why the output looks like this
                  </div>
                  {explanation.output_notes.map((n, i) => (
                    <p key={i} className="explain-note">
                      {n}
                    </p>
                  ))}
                </div>
              ) : null}
            </div>
          ) : (
            <div className="coach-explain-body">
              <p className="explain-note">…</p>
            </div>
          )}
          {/* Drag the bottom edge to size the panel. */}
          <div
            className="coach-explain-grip"
            title="Drag to resize"
            onPointerDown={(e) => {
              e.preventDefault();
              onExplainDragStart();
            }}
          />
        </div>
      ) : null}

      {chatOpen ? (
        <div className="coach-chat">
          <div className="coach-chat-log">
            {chatLog.map((m, i) => (
              <div key={i} className={`coach-chat-msg ${m.role}`}>
                <strong>{m.role === "you" ? "You" : "Coach"}:</strong> {m.text}
              </div>
            ))}
          </div>
          <form
            className="coach-chat-form"
            onSubmit={(e) => {
              e.preventDefault();
              void sendChat();
            }}
          >
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder='e.g. "end of a line?"'
            />
            <button type="submit" disabled={chatBusy}>
              Send
            </button>
          </form>
        </div>
      ) : null}
    </div>
  );
}
