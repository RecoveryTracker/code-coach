import { useState } from "react";
import type { PracticeSession, ProgressInfo } from "../types";

type Props = {
  progress: ProgressInfo;
  session: PracticeSession;
  onClose: () => void;
  onGotoClass: (classId: string) => void;
  /** Throw away every saved editor buffer, everywhere. */
  onClearAll: () => void;
};

/** Map a skill to the class whose endless Lesson 1 practices it. */
const SKILL_TO_CLASS: Record<string, string> = {
  basics: "foundations",
  conditionals: "decisions",
  loops: "loops",
};

/**
 * Study overview: per-skill mastery, type-along lines per class, and
 * "due for review" skills (practiced before, but not in the last few days).
 */
export function ProgressPanel({
  progress,
  session,
  onClose,
  onGotoClass,
  onClearAll,
}: Props) {
  // Two-step: this wipes work you can't see from here, so it asks first.
  const [confirming, setConfirming] = useState(false);
  const skills = Object.entries(progress.by_skill ?? {});
  const lines = progress.dictation_lines ?? {};
  const due = progress.review_due ?? [];
  const classes = session.curriculum ?? [];
  const className = (id: string) =>
    classes.find((c) => c.id === id)?.name ?? id;

  return (
    <div className="progress-overlay" onClick={onClose}>
      <div
        className="progress-panel"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Your progress"
      >
        <div className="progress-head">
          <strong>Your progress</strong>
          <button type="button" className="coach-chat-toggle" onClick={onClose}>
            Close
          </button>
        </div>

        <div className="progress-body">
          {due.length > 0 ? (
            <section>
              <div className="progress-section-title">Due for review</div>
              <p className="progress-note">
                You haven’t practiced these in a while — a quick type-along
                keeps them fresh.
              </p>
              <div className="progress-due-row">
                {due.map((d) => {
                  const classId = SKILL_TO_CLASS[d.skill_id];
                  return classId ? (
                    <button
                      key={d.skill_id}
                      type="button"
                      className="progress-due-chip"
                      onClick={() => onGotoClass(classId)}
                      title={`Jump to the ${className(classId)} type-along`}
                    >
                      {d.name} · {d.days}d ago
                    </button>
                  ) : (
                    <span key={d.skill_id} className="progress-due-chip static">
                      {d.name} · {d.days}d ago
                    </span>
                  );
                })}
              </div>
            </section>
          ) : null}

          <section>
            <div className="progress-section-title">Skills</div>
            {skills.map(([id, s]) => {
              const pct = s.total > 0 ? Math.round((100 * s.done) / s.total) : 0;
              return (
                <div key={id} className="progress-skill">
                  <span className="progress-skill-name">{s.name}</span>
                  <div className="progress-bar">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="progress-skill-stat">
                    {s.done}/{s.total}
                    {s.xp > 0 ? ` · ${s.xp} xp` : ""}
                  </span>
                </div>
              );
            })}
          </section>

          <section>
            <div className="progress-section-title">Type-along lines</div>
            {Object.keys(lines).length === 0 ? (
              <p className="progress-note">
                Lines you finish in each class’s endless type-along count up
                here.
              </p>
            ) : (
              Object.entries(lines).map(([classId, n]) => (
                <div key={classId} className="progress-skill">
                  <span className="progress-skill-name">
                    {className(classId)}
                  </span>
                  <span className="progress-skill-stat">{n} lines</span>
                </div>
              ))
            )}
          </section>

          <p className="progress-note">
            {progress.total_completes} lesson completions overall.
          </p>

          <section className="progress-danger">
            <div className="progress-section-title">Start over</div>
            {confirming ? (
              <>
                <p className="progress-danger-warn">
                  This deletes the code you've typed in <strong>every</strong>{" "}
                  exercise, in every class and every chunk size. Saved scripts
                  (Load…) and your skill progress are kept. It can't be undone.
                </p>
                <div className="progress-danger-actions">
                  <button
                    type="button"
                    className="ws-btn danger"
                    onClick={() => {
                      onClearAll();
                      setConfirming(false);
                      onClose();
                    }}
                  >
                    Yes, delete all my typed code
                  </button>
                  <button
                    type="button"
                    className="ws-btn"
                    onClick={() => setConfirming(false)}
                  >
                    Cancel
                  </button>
                </div>
              </>
            ) : (
              <>
                <p className="progress-note">
                  Clears every saved editor buffer so you can start the whole
                  curriculum fresh. To clear just the exercise you're on, use{" "}
                  <strong>Clear editor</strong> on the toolbar.
                </p>
                <button
                  type="button"
                  className="ws-btn"
                  onClick={() => setConfirming(true)}
                >
                  Clear all typed code…
                </button>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
