import { useEffect, useState } from "react";
import { chatWithCoach, explainCode } from "../api";
import {
  CurriculumNav,
  type CurriculumClass,
} from "./CurriculumNav";
import type {
  CheckItem,
  DrillEvaluateResult,
  ExplainResult,
  PracticeSession,
  SupportLink,
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
  onReview: (skillId: string) => void;
  onBackFromReview: () => void;
  onDictationLevel?: (level: number) => void;
  watching: boolean;
  /** Current editor buffer — read fresh when the student asks for an explanation. */
  getCode: () => string;
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
  onReview,
  onBackFromReview,
  onDictationLevel,
  watching,
  getCode,
}: Props) {
  const total = session.steps.length || checks.length || 1;
  const endless = Boolean(session.endless);
  // Endless mode never "completes" the lesson — next window loads automatically
  const complete = !endless && exerciseIndex >= total;
  const step = exerciseIndex < total ? session.steps[exerciseIndex] : null;
  const isBuild = session.lesson_role === "build" || step?.kind === "build";
  const isReview = Boolean(session.is_review);
  const typeLine = step?.label ?? null;
  const multiLine = Boolean(typeLine && typeLine.includes("\n"));
  const hintLines = step?.hint_lines?.length
    ? step.hint_lines
    : typeLine
      ? typeLine.split("\n")
      : [];
  const supports: SupportLink[] = step?.supports ?? [];
  const tip = step?.tip ?? null;
  const keyboardTip =
    step?.keyboard_tip ?? "End of line: ⌘ →   ·   Down a line: ↓";
  const curriculum = (session.curriculum ?? []) as CurriculumClass[];

  const [chatOpen, setChatOpen] = useState(false);
  // Hint ladder: 0 closed → 1 nudge → 2 shape → 3 full solution.
  // Resets when the exercise changes so each problem starts un-spoiled.
  const [hintLevel, setHintLevel] = useState(0);
  useEffect(() => {
    setHintLevel(0);
  }, [exerciseIndex, session.drill_id]);
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
    statusText = endless ? "Got it — more coming…" : "Got it — next…";
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
        </div>
      ) : (
        <CurriculumNav
          session={session}
          curriculum={curriculum}
          exerciseIndex={exerciseIndex}
          exerciseTotal={total}
          statusText={statusText}
          statusClass={statusClass}
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
          onDictationLevel={onDictationLevel}
        />
      )}

      {complete ? (
        <div className="coach-banner-row">
          <span className="coach-banner-done">
            All exercises in this lesson done. Use Class / Lesson to move on.
          </span>
        </div>
      ) : (
        <>
          <div className="coach-banner-row">
            <span className="coach-banner-label">
              {isBuild
                ? "Exercise"
                : multiLine
                  ? "Type this block"
                  : "Type this"}
            </span>
            {isBuild ? (
              <div className="coach-banner-goal">{typeLine}</div>
            ) : (
              <pre
                className={`coach-banner-code${multiLine ? " multi" : ""}`}
              >
                {typeLine ?? "…"}
              </pre>
            )}
            {isBuild ? (
              <div className="hint-wrap">
                <button
                  type="button"
                  className={`coach-chat-toggle hint-btn${hintLevel > 0 ? " active" : ""}`}
                  onClick={() => setHintLevel((h) => (h + 1) % 4)}
                  title="Each click reveals a bit more"
                >
                  {hintLevel === 0
                    ? "Hint"
                    : hintLevel === 1
                      ? "More help"
                      : hintLevel === 2
                        ? "Show solution"
                        : "Hide hint"}
                </button>
                {hintLevel > 0 ? (
                  <div className="hint-popover">
                    <div className="hint-popover-title">Think about it</div>
                    <p className="hint-popover-text">
                      {tip || keyboardTip || "What tool from this class fits?"}
                    </p>
                    {hintLevel >= 2 && hintLines.length > 0 ? (
                      <>
                        <div className="hint-popover-title">
                          It starts like this
                        </div>
                        <pre className="hint-popover-code">
                          {hintLines[0] +
                            (hintLines.length > 1 ? "\n…" : "")}
                        </pre>
                      </>
                    ) : null}
                    {hintLevel >= 3 ? (
                      <>
                        <div className="hint-popover-title">Exact lines</div>
                        <pre className="hint-popover-code">
                          {hintLines.join("\n")}
                        </pre>
                      </>
                    ) : null}
                    {supports.length > 0 ? (
                      <div className="hint-supports">
                        <div className="hint-popover-title">
                          Practice the basics first (click)
                        </div>
                        {supports.map((s) => (
                          <button
                            key={s.skill_id + s.label}
                            type="button"
                            className="hint-support-link"
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => onReview(s.skill_id)}
                          >
                            {s.label}
                          </button>
                        ))}
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </div>
            ) : null}
          </div>
          {/* Build exercises: live checklist of the goal's pieces, so
              "what are they asking?" is answered right under the goal. */}
          {isBuild && result?.requirements?.length ? (
            <div className="req-list" aria-label="What this goal needs">
              <span className="req-list-label">Needs:</span>
              {result.requirements.map((r) => (
                <span
                  key={r.label}
                  className={`req-item ${r.passed ? "ok" : "todo"}`}
                >
                  <span aria-hidden>{r.passed ? "✓" : "○"}</span> {r.label}
                </span>
              ))}
            </div>
          ) : null}
          <div className="coach-tips-row">
            {/* Build lessons keep the tip behind the Hint ladder (level 1);
                showing it for free would spoil the first nudge. */}
            {tip && !isBuild ? (
              <span className="coach-tip">Tip: {tip}</span>
            ) : null}
            <span className="coach-kb">⌨ {keyboardTip}</span>
          </div>
        </>
      )}

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
