/**
 * One queue across every practice, so the session starts with practice
 * rather than with deciding what to practise.
 *
 * There are eleven screens. Each already knows which of its own items has
 * had fewest goes and longest ago, which is right and does not answer the
 * question you actually have when you sit down. Answering it eleven times
 * by hand is a cost paid before anything is learned.
 *
 * Clicking an item points that mode at it and opens the mode. It does that
 * by writing the same "last item" key the mode already reads when it starts
 * — so arriving from the queue takes the identical code path as coming back
 * to what you were doing yesterday, and there is no second way in to keep
 * working.
 *
 * The ticks are this screen's own memory of the visit, not a claim about
 * whether you got it right. The mode records that, and the queue is rebuilt
 * from the real counts whenever you come back — so something you opened and
 * did not finish is still cold, and will be offered again. A tick that
 * claimed more than that would be the only dishonest number in the app.
 */

import { useCallback, useEffect, useState } from "react";

import { fetchSession } from "../api";
import { aimAt } from "../lastKeys";
import type { Practice } from "../lastKeys";
import type { Mode } from "./ModeBar";
import type { SessionItem, SessionQueue } from "../types";

/** How many to line up. Twenty is about half an hour of short items. */
const SIZE_KEY = "code-coach:session-size";
const SIZES = [10, 20, 30];

/** Which ones have been opened this visit. */
const VISITED_KEY = "code-coach:session-visited";

function readVisited(): string[] {
  try {
    const raw = localStorage.getItem(VISITED_KEY);
    return raw ? (JSON.parse(raw) as string[]) : [];
  } catch {
    return [];
  }
}

function writeVisited(ids: string[]): void {
  try {
    localStorage.setItem(VISITED_KEY, JSON.stringify(ids));
  } catch {
    /* a blocked store costs the ticks and nothing else */
  }
}

export default function Session({ go }: { go: (mode: Mode) => void }) {
  const [queue, setQueue] = useState<SessionQueue | null>(null);
  const [size, setSize] = useState(() => {
    try {
      const saved = Number(localStorage.getItem(SIZE_KEY));
      return SIZES.includes(saved) ? saved : 20;
    } catch {
      return 20;
    }
  });
  const [visited, setVisited] = useState<string[]>(readVisited);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchSession(size)
      .then((data) => alive && setQueue(data))
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
    return () => {
      alive = false;
    };
  }, [size]);

  const open = useCallback(
    (item: SessionItem) => {
      const key = `${item.practice}:${item.id}`;
      const next = visited.includes(key) ? visited : [...visited, key];
      setVisited(next);
      writeVisited(next);
      go(aimAt(item.practice as Practice, item.id));
    },
    [go, visited],
  );

  const startOver = useCallback(() => {
    setVisited([]);
    writeVisited([]);
    fetchSession(size)
      .then(setQueue)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
  }, [size]);

  const pickSize = (n: number) => {
    setSize(n);
    try {
      localStorage.setItem(SIZE_KEY, String(n));
    } catch {
      /* same */
    }
  };

  if (error && !queue) {
    return <div className="lessons-empty">Could not build a queue: {error}</div>;
  }
  if (!queue) return <div className="lessons-empty">Loading…</div>;

  const done = queue.items.filter((i) =>
    visited.includes(`${i.practice}:${i.id}`),
  ).length;
  const next = queue.items.find(
    (i) => !visited.includes(`${i.practice}:${i.id}`),
  );

  return (
    <div className="session-wrap">
      <header className="session-head">
        <div>
          <h2>Session</h2>
          <p className="lessons-intro">
            The coldest thing from each practice, dealt round the table.
            Whatever you have done least, and of those the longest ago.
          </p>
        </div>
        <div className="session-controls">
          <span className="session-count">
            {done} of {queue.items.length} opened
          </span>
          <div className="session-sizes">
            {SIZES.map((n) => (
              <button
                key={n}
                type="button"
                className={`ws-btn${n === size ? " on" : ""}`}
                onClick={() => pickSize(n)}
              >
                {n}
              </button>
            ))}
          </div>
          {next ? (
            <button
              type="button"
              className="ws-btn primary"
              onClick={() => open(next)}
            >
              {done ? "Next" : "Start"}: {next.name}
            </button>
          ) : (
            <button type="button" className="ws-btn" onClick={startOver}>
              Build a new queue
            </button>
          )}
        </div>
      </header>

      <ol className="session-list">
        {queue.items.map((item, i) => {
          const key = `${item.practice}:${item.id}`;
          const seen = visited.includes(key);
          const isNext = next ? key === `${next.practice}:${next.id}` : false;
          return (
            <li key={key}>
              <button
                type="button"
                className={
                  "session-item"
                  + (seen ? " seen" : "")
                  + (isNext ? " next" : "")
                }
                onClick={() => open(item)}
              >
                <span className="session-num">{i + 1}</span>
                <span className="session-where">{item.label}</span>
                <span className="session-name">{item.name}</span>
                <span className="session-goes">
                  {item.done
                    ? `done ${item.done}×`
                    : "not tried"}
                </span>
                {seen ? (
                  <span className="session-tick" title="Opened this session">
                    opened
                  </span>
                ) : null}
              </button>
            </li>
          );
        })}
      </ol>

      <p className="session-note">
        {/* Said out loud, because a tick that looked like a score would be
            the only number here that was not earned. */}
        Opened is this screen remembering the visit, not a mark. Whether it
        counted is recorded by the practice itself, and the queue is rebuilt
        from those counts each time you come back — so anything you opened
        and did not finish is still cold, and will come round again.
      </p>
    </div>
  );
}
