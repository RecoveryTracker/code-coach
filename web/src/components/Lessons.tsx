import { useEffect, useMemo, useState } from "react";

import { fetchLessons } from "../api";
import type { LessonEntry } from "../types";

/**
 * Lessons: the reading, on its own.
 *
 * The same material is available beside the editor, attached to whichever line
 * you happen to be typing. That is the right place to glance at it and the
 * wrong place to learn from it — you cannot read ahead, you cannot compare two
 * patterns, and you only ever see the one the drill picked.
 *
 * So this is a place rather than a panel: the thirteen patterns down the side
 * in learning order, and one of them open at a time.
 */
export default function Lessons() {
  const [lessons, setLessons] = useState<LessonEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openId, setOpenId] = useState<string | null>(null);
  /** Collapsed by default: the point is to try it before reading the answer. */
  const [showStages, setShowStages] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const all = await fetchLessons();
        if (cancelled) return;
        setLessons(all);
        setOpenId((id) => id ?? all[0]?.id ?? null);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "API error");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const open = useMemo(
    () => lessons?.find((l) => l.id === openId) ?? null,
    [lessons, openId],
  );

  // Opening a different pattern starts it closed again, so the walkthrough is
  // always a deliberate reveal rather than something already on screen.
  useEffect(() => {
    setShowStages(false);
  }, [openId]);

  if (error) {
    return <div className="lessons-empty">Couldn't load the lessons: {error}</div>;
  }
  if (!lessons) {
    return <div className="lessons-empty">Loading lessons…</div>;
  }

  return (
    <div className="lessons">
      <nav className="lessons-list" aria-label="Patterns">
        {lessons.map((lesson, i) => (
          <button
            key={lesson.id}
            type="button"
            className={`lessons-item${lesson.id === openId ? " on" : ""}`}
            onClick={() => setOpenId(lesson.id)}
          >
            <span className="lessons-item-n">{i + 1}</span>
            <span className="lessons-item-body">
              <span className="lessons-item-name">{lesson.name}</span>
              <span className="lessons-item-tell">{lesson.tell}</span>
            </span>
          </button>
        ))}
      </nav>

      {open ? (
        <article className="lessons-read">
          <header className="lessons-head">
            <h2>{open.name}</h2>
            <p className="lessons-blurb">{open.summary}</p>
          </header>

          <section className="lessons-block">
            <h3>When it's this one</h3>
            <p>{open.when}</p>
          </section>

          {open.worked ? (
            <section className="lessons-block lessons-worked">
              <h3>
                Solving #{open.worked.problem} {open.worked.title}
              </h3>
              {open.worked.statement ? (
                <p className="lessons-statement">{open.worked.statement}</p>
              ) : null}

              <div className="lessons-note">
                <span className="lessons-note-tag">First thought</span>
                <p>{open.worked.naive}</p>
              </div>
              <div className="lessons-note">
                <span className="lessons-note-tag">Why that hurts</span>
                <p>{open.worked.why_not}</p>
              </div>
              <div className="lessons-note is-move">
                <span className="lessons-note-tag">The move</span>
                <p>{open.worked.insight}</p>
              </div>

              {/* Hidden until asked for. Reading a finished derivation feels
                  like understanding it, which is the trap this is trying to
                  avoid — have a go from the insight first. */}
              {showStages ? (
                <ol className="lessons-stages">
                  {open.worked.stages.map((stage, i) => (
                    <li key={i}>
                      <p>{stage.explain}</p>
                      {stage.code ? <pre>{stage.code}</pre> : null}
                    </li>
                  ))}
                </ol>
              ) : (
                <button
                  type="button"
                  className="lessons-reveal"
                  onClick={() => setShowStages(true)}
                >
                  Build it with me — {open.worked.stages.length} steps
                </button>
              )}
            </section>
          ) : null}

          <section className="lessons-block">
            <h3>The shape</h3>
            <pre className="lessons-template">{open.template}</pre>
            {open.steps.length > 0 ? (
              <ol className="lessons-steps">
                {open.steps.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ol>
            ) : null}
          </section>

          {open.pitfalls.length > 0 ? (
            <section className="lessons-block">
              <h3>Where it goes wrong</h3>
              <ul className="lessons-pitfalls">
                {open.pitfalls.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </section>
          ) : null}

          <section className="lessons-block">
            <h3>Practise it — {open.problems.length} problems</h3>
            <ul className="lessons-problems">
              {open.problems.map((p) => (
                <li key={p.number}>
                  <span className={`lessons-diff ${p.difficulty.toLowerCase()}`}>
                    {p.difficulty}
                  </span>
                  <span className="lessons-prob-name">
                    #{p.number} {p.title}
                  </span>
                  <span className="lessons-prob-idea">{p.idea}</span>
                </li>
              ))}
            </ul>
          </section>
        </article>
      ) : null}
    </div>
  );
}
