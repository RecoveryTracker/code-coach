/**
 * What has been done, what has not, and what is due for a refresh.
 *
 * The queue answers "what next". This answers what a queue cannot: how
 * much of each practice has been touched at all, and which things done
 * before are old enough to be worth doing again. The gap is yours to
 * pick - a week suits most things, a few days suits what is new.
 *
 * Built from the same counts the queue uses, so the two cannot disagree.
 * Opening an item here goes the same way as from the queue: it points
 * the mode at the item and opens the mode.
 */

import { useEffect, useState } from "react";

import { fetchSessionHistory } from "../api";
import { aimAt } from "../lastKeys";
import type { Practice } from "../lastKeys";
import type { Mode } from "./ModeBar";
import type { HistoryItem, SessionHistory as History } from "../types";

const GAP_KEY = "code-coach:history-gap";

function ago(days: number): string {
  if (days < 1 / 24) return "just now";
  if (days < 1) return `${Math.round(days * 24)} h ago`;
  if (days < 2) return "yesterday";
  return `${Math.floor(days)} days ago`;
}

function readGap(): number {
  try {
    const saved = Number(localStorage.getItem(GAP_KEY));
    return saved > 0 ? saved : 7;
  } catch {
    return 7;
  }
}

export default function SessionHistory({ go }: { go: (mode: Mode) => void }) {
  const [gap, setGap] = useState<number>(readGap);
  const [data, setData] = useState<History | null>(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState<string>("");

  useEffect(() => {
    let alive = true;
    fetchSessionHistory(gap)
      .then((got) => alive && setData(got))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, [gap]);

  const pickGap = (days: number) => {
    setGap(days);
    try {
      localStorage.setItem(GAP_KEY, String(days));
    } catch {
      /* the gap resets next visit, nothing worse */
    }
  };

  const openItem = (item: HistoryItem) => go(aimAt(item.practice as Practice, item.id));

  if (error && !data) return <div className="lessons-empty">Could not load the history: {error}</div>;
  if (!data) return <div className="lessons-empty">Loading…</div>;

  const dueTotal = data.practices.reduce((n, p) => n + p.due.length, 0);

  return (
    <div className="history">
      <div className="history-controls">
        <span className="session-count">Refresh after</span>
        <div className="session-sizes">
          {data.choices.map((d) => (
            <button
              key={d}
              type="button"
              className={`ws-btn${d === data.refresh_days ? " on" : ""}`}
              onClick={() => pickGap(d)}
            >
              {d} days
            </button>
          ))}
        </div>
        <span className="session-count">
          {dueTotal ? `${dueTotal} due for a refresh` : "Nothing due - all fresh"}
        </span>
      </div>

      <ul className="history-practices">
        {data.practices.map((p) => {
          const share = p.total ? Math.round((p.tried / p.total) * 100) : 0;
          const expanded = open === p.key;
          return (
            <li key={p.key} className="history-practice">
              <button
                type="button"
                className={`history-row${expanded ? " on" : ""}`}
                onClick={() => setOpen(expanded ? "" : p.key)}
                aria-expanded={expanded}
              >
                <span className="history-label">{p.label}</span>
                <span className="history-bar" aria-hidden="true">
                  <span className="history-fill" style={{ width: `${share}%` }} />
                </span>
                <span className="history-tried">
                  {p.tried} of {p.total} tried
                </span>
                <span className={`history-due${p.due.length ? " some" : ""}`}>
                  {p.due.length ? `${p.due.length} due` : "fresh"}
                </span>
              </button>
              {expanded ? (
                p.due.length ? (
                  <ul className="history-items">
                    {p.due.map((item) => (
                      <li key={item.id}>
                        <button type="button" className="session-item" onClick={() => openItem(item)}>
                          <span className="session-name">{item.name}</span>
                          <span className="session-goes">
                            done {item.done}× · last {ago(item.days_ago)}
                          </span>
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="history-empty">
                    {p.tried
                      ? `Everything you have done here was within the last ${data.refresh_days} days.`
                      : "Not started yet - the queue will deal these to you."}
                  </p>
                )
              ) : null}
            </li>
          );
        })}
      </ul>

      <h3 className="history-heading">Recently done</h3>
      {data.recent.length ? (
        <ol className="history-items">
          {data.recent.map((item) => (
            <li key={`${item.practice}:${item.id}`}>
              <button type="button" className="session-item" onClick={() => openItem(item)}>
                <span className="session-where">{item.label}</span>
                <span className="session-name">{item.name}</span>
                <span className="session-goes">{ago(item.days_ago)}</span>
              </button>
            </li>
          ))}
        </ol>
      ) : (
        <p className="history-empty">Nothing yet. Start the queue and it will show up here.</p>
      )}
    </div>
  );
}
