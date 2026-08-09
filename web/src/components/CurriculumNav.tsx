import type { ReactNode } from "react";
import type { PracticeSession } from "../types";

export type CurriculumClass = {
  id: string;
  number?: number;
  name: string;
  description: string;
  lessons: {
    number: number;
    id: string;
    title: string;
    role: string;
    full_title: string;
  }[];
};

// Non-color status cue: color alone isn't enough (colorblind readers). A glyph
// carries the same good/bad/working meaning without relying on red vs green.
const STATUS_GLYPH: Record<string, string> = {
  good: "✓",
  bad: "✕",
  mid: "…",
  idle: "•",
};

/** Strip the redundant tail from "Type-along (endless)" etc. */
function lessonLabel(title: string): string {
  return title.replace(/\s*\(endless\)\s*$/i, "").trim();
}

type Props = {
  session: PracticeSession;
  curriculum: CurriculumClass[];
  exerciseIndex: number;
  exerciseTotal: number;
  statusText: string;
  statusClass: string;
  /** Check passed — light up Continue next to the status. */
  exerciseDone: boolean;
  onContinue: () => void;
  watching: boolean;
  chatOpen: boolean;
  onToggleChat: () => void;
  explainOpen: boolean;
  onToggleExplain: () => void;
  onExerciseDelta: (d: number) => void;
  onSelectClass: (id: string) => void;
  onSelectLesson: (n: number) => void;
  /** App title, centred on this line. */
  brand: ReactNode;
  /** Save / Load / Progress / Free mode / Start over / Run, right-aligned. */
  toolbar: ReactNode;
};

/**
 * Where am I, and how do I move?
 *
 * Class › Lesson › Exercise is a hierarchy, so it reads as one breadcrumb path
 * rather than three identical steppers competing for the same glance. Movement
 * is a single ‹ › pair that walks the curriculum in order — it rolls into the
 * next lesson (and class) at the end of one — so there's exactly one "forward".
 * Jumping anywhere is the dropdowns' job.
 */
export function CurriculumNav({
  session,
  curriculum,
  exerciseIndex,
  exerciseTotal,
  statusText,
  statusClass,
  exerciseDone,
  onContinue,
  watching,
  chatOpen,
  onToggleChat,
  explainOpen,
  onToggleExplain,
  onExerciseDelta,
  onSelectClass,
  onSelectLesson,
  brand,
  toolbar,
}: Props) {
  const classId = session.class_id ?? "foundations";
  const lessonNum = session.lesson_number ?? 1;
  const cls = curriculum.find((c) => c.id === classId) ?? curriculum[0] ?? null;
  const lessons = cls?.lessons ?? [];
  const totalEx = Math.max(1, exerciseTotal);
  const endless = Boolean(session.endless);
  const exDisplay = Math.min(exerciseIndex + 1, totalEx);
  const linesDone = session.lines_done ?? 0;

  // 17 classes in one flat list is a wall. Split the two things they actually
  // are: language fundamentals, and the LeetCode pattern set.
  const fundamentals = curriculum.filter((c) => !c.id.startsWith("lc-"));
  const leetcode = curriculum.filter((c) => c.id.startsWith("lc-"));

  return (
    <div className="cur-nav" aria-label="Curriculum navigation">
      {/* Coach tools + the Not yet / Got it status. */}
      <div className="cur-nav-line">
        <button
          type="button"
          className={`coach-chat-toggle${explainOpen ? " active" : ""}`}
          onClick={onToggleExplain}
          title="The coach walks through your code line by line and explains the output"
        >
          {explainOpen ? "Hide explain" : "Explain my code"}
        </button>

        <button type="button" className="coach-chat-toggle" onClick={onToggleChat}>
          {chatOpen ? "Hide chat" : "Ask coach"}
        </button>

        <div className={`cur-nav-status ${statusClass}`} title={statusText}>
          <span className="cur-nav-status-glyph" aria-hidden>
            {STATUS_GLYPH[statusClass] ?? "•"}
          </span>
          <span className="cur-nav-status-text">{statusText}</span>
          {watching ? <span className="live-pulse">…</span> : null}
          {exerciseDone ? (
            <button type="button" className="cur-nav-continue" onClick={onContinue}>
              Continue →
            </button>
          ) : null}
        </div>

        {brand}
        {toolbar}
      </div>

      {/* The path: Class › Lesson › Exercise, then one prev/next pair. */}
      <div className="cur-nav-line cur-nav-path-line">
        <nav className="cur-path" aria-label="Where you are">
          <span className="cur-crumb">
            <select
              className="cur-crumb-select"
              value={classId}
              onChange={(e) => onSelectClass(e.target.value)}
              aria-label="Choose class"
            >
              <optgroup label="Fundamentals">
                {fundamentals.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </optgroup>
              <optgroup label="LeetCode patterns">
                {leetcode.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name.replace(/^LeetCode\s*[—-]\s*/, "")}
                  </option>
                ))}
              </optgroup>
            </select>
          </span>

          <span className="cur-path-sep" aria-hidden>
            ›
          </span>

          <span className="cur-crumb">
            <select
              className="cur-crumb-select"
              value={lessonNum}
              onChange={(e) => onSelectLesson(Number(e.target.value))}
              aria-label="Choose lesson"
            >
              {lessons.map((L) => (
                <option key={L.id} value={L.number}>
                  {L.number}. {lessonLabel(L.title)}
                </option>
              ))}
            </select>
          </span>

          <span className="cur-path-sep" aria-hidden>
            ›
          </span>

          <span
            className="cur-path-ex"
            title={
              endless
                ? `Exercise ${exDisplay} of ${totalEx} in this set · ${linesDone + exDisplay} done overall · keeps going`
                : `Exercise ${exDisplay} of ${totalEx}`
            }
          >
            {exDisplay} / {totalEx}
            {endless ? <span className="cur-path-endless">keeps going</span> : null}
          </span>

          {/* Back / forward belong right after the thing they move. Pinned to
              the far right they read as unrelated to the path. */}
          <div
            className="cur-step"
            role="group"
            aria-label="Move through the curriculum"
          >
            <button
              type="button"
              className="cur-step-btn"
              onClick={() => onExerciseDelta(-1)}
              aria-label="Previous exercise"
              title="Back — rolls into the previous lesson at the start"
            >
              ‹
            </button>
            <button
              type="button"
              className="cur-step-btn"
              onClick={() => onExerciseDelta(1)}
              aria-label="Next exercise"
              title="Forward — rolls into the next lesson at the end"
            >
              ›
            </button>
          </div>
        </nav>
      </div>
    </div>
  );
}
