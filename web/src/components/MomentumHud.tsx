/**
 * The Momentum strip in the top bar: streak flame, level and XP bar, today's quests.
 *
 * One button, so it works the same at any width: wide, it shows the flame, the level
 * and a filling bar and the quest count; narrow, only the flame and its number. Pressing
 * it opens a popover with the whole picture - quests with progress bars, the chest, the
 * last two weeks, the best streak - and a Start button that goes to the Session queue.
 *
 * Nothing in here counts down against you. A streak that has not been added to yet today
 * is shown dimmed, not red, and the words never say what you stand to lose.
 */

import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { claimChest, refresh, useMomentum } from "../lib/momentum";
import { hudView } from "../lib/momentumView";

function Flame({ lit }: { lit: boolean }): ReactNode {
  return (
    <svg className={`mhud-flame${lit ? " lit" : ""}`} viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
      <path
        d="M8 1c.6 2.2 3.8 3.9 3.8 7.4A3.8 3.8 0 0 1 8 12.2 3.8 3.8 0 0 1 4.2 8.4c0-1.4.6-2.3 1.3-3 .1 1 .5 1.6 1.1 1.9C6.4 5.3 6.9 2.6 8 1z"
        fill="currentColor"
      />
    </svg>
  );
}

function Snowflake(): ReactNode {
  return (
    <svg className="mhud-snow" viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
      <path
        d="M8 1v14M2 4.5l12 7M14 4.5l-12 7M6 2l2 1.6L10 2M6 14l2-1.6 2 1.6"
        stroke="currentColor"
        strokeWidth="1.3"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function MomentumHud({
  onStart,
  onGo,
}: {
  onStart: () => void;
  /** Open a mode (a top-bar tab) by its id. */
  onGo: (mode: string) => void;
}): ReactNode {
  const { summary } = useMomentum();
  const [open, setOpen] = useState(false);
  const wrap = useRef<HTMLDivElement>(null);
  const v = hudView(summary);

  useEffect(() => {
    void refresh();
  }, []);

  // Fresh numbers whenever the popover opens (a day may have turned over since).
  useEffect(() => {
    if (open) void refresh();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const away = (e: PointerEvent) => {
      if (wrap.current && !wrap.current.contains(e.target as Node)) setOpen(false);
    };
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("pointerdown", away);
    document.addEventListener("keydown", key);
    return () => {
      document.removeEventListener("pointerdown", away);
      document.removeEventListener("keydown", key);
    };
  }, [open]);

  const quests = summary?.quests ?? [];
  return (
    <div className="mhud" ref={wrap}>
      <button
        type="button"
        className={`mhud-main${v.chest === "ready" ? " chest-ready" : ""}${open ? " on" : ""}`}
        aria-expanded={open}
        aria-haspopup="dialog"
        aria-label={`Momentum: ${v.streakNote}. ${v.levelText}. Quests ${v.questText}.`}
        title={`${v.streakNote}\n${v.levelText}\nQuests ${v.questText}`}
        onClick={() => setOpen((o) => !o)}
      >
        <span className="mhud-streak">
          <Flame lit={v.flameLit} />
          <span className="mhud-streak-n">{v.streak}</span>
          {v.freezes > 0 ? (
            <span className="mhud-freeze" title={v.freezeNote}>
              <Snowflake />
              {v.freezes > 1 ? <span>x{v.freezes}</span> : null}
            </span>
          ) : null}
        </span>
        <span className="mhud-level">
          <span className="mhud-level-text">{v.levelText}</span>
          <span className="mhud-level-short">{v.levelShort}</span>
          <span className="mhud-bar" aria-hidden="true">
            <span className="mhud-bar-fill" style={{ width: `${v.xpPct}%` }} />
          </span>
        </span>
        <span className={`mhud-quest${v.questsDone >= v.questsTotal ? " all" : ""}`}>
          {v.chest === "ready" ? "Chest!" : v.questText}
        </span>
      </button>

      {open ? (
        <div className="mhud-pop" role="dialog" aria-label="Today's momentum">
          <div className="mhud-pop-head">
            <strong>{v.levelText}</strong>
            <span className="mhud-pop-dim">{v.totalText}</span>
          </div>
          <div className="mhud-bar big" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={v.xpPct} aria-label="XP to the next level">
            <span className="mhud-bar-fill" style={{ width: `${v.xpPct}%` }} />
          </div>
          <div className="mhud-pop-dim small">{v.xpText} to Lv {(summary?.level ?? 1) + 1}</div>

          <div className="mhud-pop-row">
            <Flame lit={v.flameLit} />
            <span>{v.streakNote}</span>
          </div>
          <div className="mhud-pop-row dim">
            <Snowflake />
            <span>{v.freezeNote}</span>
          </div>

          <h4 className="mhud-pop-h">Today</h4>
          <ul className="mhud-quests">
            {quests.map((q) => (
              <li key={q.id} className={q.done ? "done" : ""}>
                {/* The whole label is the way there: the quest is a place to go, not text to read. */}
                <button
                  type="button"
                  className="mhud-q-label mhud-q-go"
                  title={`Go to ${q.go ?? "session"}`}
                  onClick={() => {
                    setOpen(false);
                    onGo(q.go ?? "session");
                  }}
                >
                  <span className="mhud-q-tick" aria-hidden="true">{q.done ? "✓" : ""}</span>
                  {q.label}
                  <span className="mhud-q-arrow" aria-hidden="true">→</span>
                </button>
                <span className="mhud-q-n">{q.have}/{q.need}</span>
                <span className="mhud-bar thin" aria-hidden="true">
                  <span className="mhud-bar-fill" style={{ width: `${Math.round((q.have / Math.max(1, q.need)) * 100)}%` }} />
                </span>
              </li>
            ))}
          </ul>

          <div className={`mhud-chest ${v.chest}`}>
            <span>{v.chestNote}</span>
            {v.chest === "ready" ? (
              <button type="button" className="ws-btn primary" onClick={() => void claimChest()}>
                Open chest
              </button>
            ) : null}
          </div>

          <h4 className="mhud-pop-h">Last 14 days</h4>
          <div className="mhud-days" role="img" aria-label="XP per day, last 14 days">
            {v.bars.map((b) => (
              <span key={b.day} className={`mhud-day${b.today ? " today" : ""}`} title={b.label}>
                <span className="mhud-day-fill" style={{ height: `${b.pct}%` }} />
              </span>
            ))}
          </div>
          <div className="mhud-pop-foot">
            <span className="mhud-pop-dim">{v.bestText}</span>
            <button
              type="button"
              className="ws-btn primary"
              onClick={() => {
                setOpen(false);
                onStart();
              }}
              title="One queue across every practice"
            >
              Start
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
