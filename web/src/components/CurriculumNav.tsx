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

const LEVEL_OPTIONS = [
  { value: 1, label: "1 · Single lines" },
  { value: 2, label: "2 · Lines+" },
  { value: 3, label: "3 · Two-liners" },
  { value: 4, label: "4 · Blocks" },
  { value: 5, label: "5 · Functions" },
];

// Non-color status cue: color alone isn't enough (colorblind readers). A glyph
// carries the same good/bad/working meaning without relying on red vs green.
const STATUS_GLYPH: Record<string, string> = {
  good: "✓",
  bad: "✕",
  mid: "…",
  idle: "•",
};

type Props = {
  session: PracticeSession;
  curriculum: CurriculumClass[];
  exerciseIndex: number;
  exerciseTotal: number;
  statusText: string;
  statusClass: string;
  watching: boolean;
  chatOpen: boolean;
  onToggleChat: () => void;
  explainOpen: boolean;
  onToggleExplain: () => void;
  onClassDelta: (d: number) => void;
  onLessonDelta: (d: number) => void;
  onExerciseDelta: (d: number) => void;
  onSelectClass: (id: string) => void;
  onSelectLesson: (n: number) => void;
  onDictationLevel?: (level: number) => void;
};

/**
 * One compact row: Class · Lesson · Exercise + (endless difficulty) + status + Ask coach
 */
export function CurriculumNav({
  session,
  curriculum,
  exerciseIndex,
  exerciseTotal,
  statusText,
  statusClass,
  watching,
  chatOpen,
  onToggleChat,
  explainOpen,
  onToggleExplain,
  onClassDelta,
  onLessonDelta,
  onExerciseDelta,
  onSelectClass,
  onSelectLesson,
  onDictationLevel,
}: Props) {
  const classId = session.class_id ?? "foundations";
  const lessonNum = session.lesson_number ?? 1;
  const cls =
    curriculum.find((c) => c.id === classId) ?? curriculum[0] ?? null;
  const lessons = cls?.lessons ?? [];
  const totalEx = Math.max(1, exerciseTotal);
  const endless = Boolean(session.endless);
  const linesDone = session.lines_done ?? 0;
  const lifetime = linesDone + Math.min(exerciseIndex, totalEx - 1) + 1;
  const exDisplay = Math.min(exerciseIndex + 1, totalEx);
  const dLevel = session.dictation_level ?? 1;

  return (
    <div className="cur-nav" aria-label="Curriculum navigation">
      {/* Status lives on the LEFT so "Not yet / Got it" is the first thing
          you see, next to the code you're typing. */}
      <div className={`cur-nav-status ${statusClass}`}>
        <span className="cur-nav-status-glyph" aria-hidden>
          {STATUS_GLYPH[statusClass] ?? "•"}
        </span>
        <span className="cur-nav-status-text">{statusText}</span>
        {watching ? <span className="live-pulse">…</span> : null}
      </div>

      {/* Each stepper is a bordered pill so its arrows can't be mistaken
          for a neighbor's. Class uses « » (bigger jump) vs ‹ › elsewhere. */}
      <div className="cur-nav-row">
        <span className="cur-nav-kind">Class</span>
        <button
          type="button"
          className="cur-nav-arrow cur-nav-arrow-class"
          onClick={() => onClassDelta(-1)}
          aria-label="Previous class"
          title="Previous class"
        >
          «
        </button>
        <select
          className="cur-nav-select"
          value={classId}
          onChange={(e) => onSelectClass(e.target.value)}
          aria-label="Choose class"
        >
          {curriculum.map((c, i) => (
            <option key={c.id} value={c.id}>
              Class {c.number ?? i + 1} — {c.name}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="cur-nav-arrow cur-nav-arrow-class"
          onClick={() => onClassDelta(1)}
          aria-label="Next class"
          title="Next class"
        >
          »
        </button>
      </div>

      <div className="cur-nav-row">
        <span className="cur-nav-kind">Lesson</span>
        <button
          type="button"
          className="cur-nav-arrow"
          onClick={() => onLessonDelta(-1)}
          aria-label="Previous lesson"
          title="Previous lesson"
        >
          ‹
        </button>
        <select
          className="cur-nav-select"
          value={lessonNum}
          onChange={(e) => onSelectLesson(Number(e.target.value))}
          aria-label="Choose lesson"
        >
          {lessons.map((L) => (
            <option key={L.id} value={L.number}>
              Lesson {L.number} — {L.title}
              {L.role === "dictation" ? " (type)" : " (build)"}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="cur-nav-arrow"
          onClick={() => onLessonDelta(1)}
          aria-label="Next lesson"
          title="Next lesson"
        >
          ›
        </button>
      </div>

      <div className="cur-nav-row">
        <span className="cur-nav-kind">Exercise</span>
        <button
          type="button"
          className="cur-nav-arrow"
          onClick={() => onExerciseDelta(-1)}
          aria-label="Previous exercise"
          title="Previous exercise"
        >
          ‹
        </button>
        <span
          className="cur-nav-ex"
          title={
            endless
              ? `Exercise ${lifetime} · endless type-along (window ${exDisplay}/${totalEx})`
              : `Exercise ${exDisplay} of ${totalEx}`
          }
        >
          {endless ? (
            <>
              {lifetime} <span className="cur-nav-inf">∞</span>
            </>
          ) : (
            <>
              {exDisplay} of {totalEx}
            </>
          )}
        </span>
        <button
          type="button"
          className="cur-nav-arrow"
          onClick={() => onExerciseDelta(1)}
          aria-label="Next exercise"
          title="Next exercise"
        >
          ›
        </button>
      </div>

      {endless && onDictationLevel ? (
        <div className="cur-nav-row cur-nav-diff">
          <span className="cur-nav-kind">Difficulty</span>
          <button
            type="button"
            className="cur-nav-arrow"
            disabled={dLevel <= 1}
            onClick={() => onDictationLevel(dLevel - 1)}
            aria-label="Easier dictation"
            title="Easier"
          >
            ‹
          </button>
          <select
            className="cur-nav-select cur-nav-select-diff"
            value={dLevel}
            onChange={(e) => onDictationLevel(Number(e.target.value))}
            aria-label="Dictation difficulty"
            title="Turn up for multi-line and functions. Stay in type-along forever."
          >
            {LEVEL_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="cur-nav-arrow"
            disabled={dLevel >= 5}
            onClick={() => onDictationLevel(dLevel + 1)}
            aria-label="Harder dictation"
            title="Harder"
          >
            ›
          </button>
        </div>
      ) : null}

      <button
        type="button"
        className={`coach-chat-toggle push-right${explainOpen ? " active" : ""}`}
        onClick={onToggleExplain}
        title="The coach walks through your code line by line and explains the output"
      >
        {explainOpen ? "Hide explain" : "Explain my code"}
      </button>

      <button
        type="button"
        className="coach-chat-toggle"
        onClick={onToggleChat}
      >
        {chatOpen ? "Hide chat" : "Ask coach"}
      </button>
    </div>
  );
}
