/**
 * Concepts: the half of a systems interview that is not a coding problem.
 *
 * Answers are hidden until you ask for them, because reading a question and
 * its answer together teaches you that you knew it. The point is to try to
 * say it first and then find out.
 */

import { useEffect, useState } from "react";
import { fetchConcepts } from "../api";
import type { ConceptTopic } from "../types";

type Props = {
  /** Which language's topics to show. Changing it refetches. */
  language: string;
};

export default function Concepts({ language }: Props) {
  const [topics, setTopics] = useState<ConceptTopic[]>([]);
  const [openTopic, setOpenTopic] = useState<string | null>(null);
  const [shown, setShown] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  // Most of the bank is about the machine and is the same whatever you write,
  // but the topic on the language's own semantics follows the picker — so this
  // has to refetch rather than load once.
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const got = await fetchConcepts(language);
        if (cancelled) return;
        setTopics(got);
        // Keep the topic you were reading when it exists in both languages,
        // which is all but the language one.
        setOpenTopic((id) =>
          id && got.some((t) => t.id === id) ? id : (got[0]?.id ?? null),
        );
      } catch {
        if (!cancelled) setError("Couldn't load the concept questions.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [language]);

  const open = topics.find((t) => t.id === openTopic) ?? null;

  const reveal = (key: string) =>
    setShown((was) => {
      const next = new Set(was);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });

  const revealAll = () => {
    if (!open) return;
    setShown((was) => {
      const next = new Set(was);
      open.questions.forEach((_, i) => next.add(`${open.id}:${i}`));
      return next;
    });
  };

  const hideAll = () => {
    if (!open) return;
    setShown((was) => {
      const next = new Set(was);
      open.questions.forEach((_, i) => next.delete(`${open.id}:${i}`));
      return next;
    });
  };

  if (error) {
    // Not lessons-wrap: that is the two-column grid, and an error squeezed
    // into the 260px topic column is its own small bug.
    return <div className="lessons-empty">{error}</div>;
  }

  const total = topics.reduce((sum, t) => sum + t.questions.length, 0);

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Concepts</h2>
        <p className="lessons-intro">
          {total} questions an interview asks that no amount of LeetCode
          prepares you for. Try to answer out loud first.
        </p>
        {topics.map((topic) => (
          <button
            key={topic.id}
            type="button"
            className={`lessons-pick${topic.id === openTopic ? " on" : ""}`}
            onClick={() => setOpenTopic(topic.id)}
          >
            <span className="lessons-pick-name">{topic.name}</span>
            <span className="lessons-pick-blurb">
              {topic.questions.length} questions
            </span>
          </button>
        ))}
      </nav>

      {open ? (
        <article className="lessons-open">
          <header>
            <h3>{open.name}</h3>
            <p className="lessons-blurb">{open.blurb}</p>
            <div className="concept-controls">
              <button type="button" className="ws-btn" onClick={revealAll}>
                Show all answers
              </button>
              <button type="button" className="ws-btn" onClick={hideAll}>
                Hide all
              </button>
            </div>
          </header>

          <ol className="concept-list">
            {open.questions.map((question, i) => {
              const key = `${open.id}:${i}`;
              const isShown = shown.has(key);
              return (
                <li className="concept-item" key={key}>
                  <button
                    type="button"
                    className="concept-ask"
                    onClick={() => reveal(key)}
                    aria-expanded={isShown}
                  >
                    {question.ask}
                  </button>
                  {isShown ? (
                    <div className="concept-answer">
                      <p>{question.answer}</p>
                      {question.follow_up ? (
                        <p className="concept-follow">
                          <span className="concept-follow-tag">Then:</span>{" "}
                          {question.follow_up}
                        </p>
                      ) : null}
                    </div>
                  ) : (
                    <p className="concept-hint">
                      Answer it, then click to check.
                    </p>
                  )}
                </li>
              );
            })}
          </ol>
        </article>
      ) : null}
    </div>
  );
}
