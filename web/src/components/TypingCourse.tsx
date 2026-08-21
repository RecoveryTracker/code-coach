import { useEffect, useMemo, useState } from "react";

import { fetchTypingCourse } from "../api";
import type { TypingCourse as Course, TypingLesson } from "../types";

/**
 * The course list — the front door of the trainer.
 *
 * Sections crossed with modes is a workshop, and a workshop is the wrong
 * first screen: it asks you to decide what you need before you know. This is
 * the ordinary path instead, numbered, in order, with one button that carries
 * on from wherever you got to.
 *
 * Nothing is locked. A lesson you can't reach is a lesson you can't practise,
 * and someone who came here to drill the number row shouldn't have to earn it
 * first.
 */

type Props = {
  /** Bumped after a run so progress reloads without a remount. */
  revision: number;
  onStart: (section: string, mode: string, theme: string) => void;
};

function target(lesson: TypingLesson): string {
  const accuracy = `${lesson.target_accuracy}% accurate`;
  return lesson.target_wpm
    ? `${lesson.target_wpm} wpm · ${accuracy}`
    : accuracy;
}

export default function TypingCoursePanel({ revision, onStart }: Props) {
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTypingCourse()
      .then(setCourse)
      .catch((e: Error) => setError(e.message));
  }, [revision]);

  const current = useMemo(
    () => course?.lessons.find((l) => l.number === course.current) ?? null,
    [course],
  );

  if (error) {
    return <div className="typing-error">Couldn't load the course: {error}</div>;
  }
  if (!course) return <div className="typing-loading">Loading…</div>;

  const pct = Math.round((course.done / course.total) * 100);

  return (
    <div className="typing-course">
      <div className="tc-header">
        <div className="tc-headline">
          <h3>Learn to type</h3>
          <p>
            Twenty-four lessons, in order: the home row first, then a row at a
            time, then numbers, symbols and real text. Work straight through.
          </p>
        </div>
        <div className="tc-progress-block">
          <div className="tc-count">
            <strong>{course.done}</strong>
            <span>of {course.total} done</span>
          </div>
          <div className="tc-bar">
            <div className="tc-bar-fill" style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>

      {current && (
        <button
          type="button"
          className="tc-continue"
          onClick={() => onStart(current.section, current.mode, current.theme)}
        >
          <span className="tc-continue-label">
            {course.done === 0 ? "Start lesson 1" : `Continue — lesson ${current.number}`}
          </span>
          <span className="tc-continue-title">{current.title}</span>
        </button>
      )}

      <ol className="tc-list">
        {course.lessons.map((lesson) => (
          <li
            key={lesson.number}
            className={[
              "tc-lesson",
              lesson.done ? "done" : "",
              lesson.number === course.current ? "current" : "",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            <button
              type="button"
              onClick={() => onStart(lesson.section, lesson.mode, lesson.theme)}
            >
              <span className="tc-num">{lesson.done ? "✓" : lesson.number}</span>
              <span className="tc-body">
                <span className="tc-title">{lesson.title}</span>
                <span className="tc-why">{lesson.why}</span>
                <span className="tc-meta">
                  {lesson.section_name} · {lesson.mode_name}
                  {lesson.theme !== "mixed" ? ` · ${lesson.theme_name}` : ""} ·
                  goal {target(lesson)}
                  {lesson.runs > 0 && !lesson.done && (
                    <em>
                      {" "}
                      — best {lesson.best_wpm ? `${lesson.best_wpm} wpm, ` : ""}
                      {lesson.best_accuracy}%
                    </em>
                  )}
                </span>
              </span>
            </button>
          </li>
        ))}
      </ol>
    </div>
  );
}
