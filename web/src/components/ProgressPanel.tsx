import type { PracticeSession, ProgressInfo } from "../types";

type Props = {
  progress: ProgressInfo;
  session: PracticeSession;
  onClose: () => void;
  onGotoClass: (classId: string) => void;
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
export function ProgressPanel({ progress, session, onClose, onGotoClass }: Props) {
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
        </div>
      </div>
    </div>
  );
}
