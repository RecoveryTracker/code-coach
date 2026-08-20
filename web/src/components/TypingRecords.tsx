import { useEffect, useMemo, useState } from "react";

import { fetchTypingRecords } from "../api";
import type { TypingRecord } from "../types";

/**
 * The board of personal bests.
 *
 * Grouped by section rather than presented as one ranked list, because a wpm
 * on Home Row Words and a wpm on Coding Punctuation aren't the same
 * measurement — putting them in one column would only invite the comparison
 * that doesn't mean anything. Within a section, the modes are comparable.
 */

type Props = {
  /** Bumped after a run so the board reloads without a full remount. */
  revision: number;
  onPick?: (section: string, mode: string) => void;
};

function when(iso: string): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function TypingRecords({ revision, onPick }: Props) {
  const [records, setRecords] = useState<TypingRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTypingRecords()
      .then(setRecords)
      .catch((e: Error) => setError(e.message));
  }, [revision]);

  const grouped = useMemo(() => {
    const out = new Map<string, { name: string; rows: TypingRecord[] }>();
    for (const r of records ?? []) {
      const group = out.get(r.section) ?? { name: r.section_name, rows: [] };
      group.rows.push(r);
      out.set(r.section, group);
    }
    return [...out.values()];
  }, [records]);

  const totals = useMemo(() => {
    let runs = 0;
    let keys = 0;
    let best = 0;
    for (const r of records ?? []) {
      runs += r.runs;
      keys += r.total_keys;
      best = Math.max(best, r.best_wpm);
    }
    return { runs, keys, best };
  }, [records]);

  if (error) {
    return <div className="typing-error">Couldn't load records: {error}</div>;
  }
  if (!records) return <div className="typing-loading">Loading…</div>;
  if (records.length === 0) {
    return (
      <div className="tr-empty">
        <p>No runs recorded yet.</p>
        <p className="tg-hint">
          Finish any drill and its best time lands here. Each section and mode
          keeps its own record.
        </p>
      </div>
    );
  }

  return (
    <div className="typing-records">
      <div className="tr-totals">
        <div>
          <strong>{totals.best}</strong> best wpm
        </div>
        <div>
          <strong>{totals.runs}</strong> runs
        </div>
        <div>
          <strong>{totals.keys.toLocaleString()}</strong> keys typed
        </div>
      </div>

      {grouped.map((group) => (
        <div className="tr-group" key={group.name}>
          <h4>{group.name}</h4>
          <table className="tr-table">
            <thead>
              <tr>
                <th>Mode</th>
                <th>wpm</th>
                <th>acc</th>
                <th>react</th>
                <th>streak</th>
                <th>runs</th>
                <th>last</th>
              </tr>
            </thead>
            <tbody>
              {group.rows.map((r) => (
                <tr
                  key={r.mode}
                  className={onPick ? "clickable" : ""}
                  onClick={() => onPick?.(r.section, r.mode)}
                >
                  <td>{r.mode_name}</td>
                  <td className="num strong">{r.best_wpm || "—"}</td>
                  <td className="num">
                    {r.best_accuracy ? `${r.best_accuracy}%` : "—"}
                  </td>
                  <td className="num">
                    {r.best_reaction_ms ? `${r.best_reaction_ms}ms` : "—"}
                  </td>
                  <td className="num">{r.best_streak || "—"}</td>
                  <td className="num dim">{r.runs}</td>
                  <td className="num dim">{when(r.updated)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
