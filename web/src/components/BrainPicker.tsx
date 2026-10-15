/**
 * The Brain Drills question picker: every question in the round as a numbered
 * cell - green for right, red for missed, the current one outlined, the rest
 * plain - to jump straight to any of them. Esc (handled by the round, which
 * knows the picker is open) closes it without leaving the round.
 */

import { useEffect, useRef } from "react";

import { cellLabel, cellStatus, type RoundState } from "../lib/brainRound";

type Props = {
  state: RoundState;
  onPick: (index: number) => void;
  onClose: () => void;
};

export default function BrainPicker({ state, onPick, onClose }: Props) {
  const grid = useRef<HTMLDivElement | null>(null);
  const current = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    current.current?.focus();
  }, []);

  // Arrow keys walk the grid; Tab stays inside the dialog.
  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const cells = Array.from(grid.current?.querySelectorAll<HTMLButtonElement>("button") ?? []);
    const at = cells.indexOf(document.activeElement as HTMLButtonElement);
    const step: Record<string, number> = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -6, ArrowDown: 6 };
    if (e.key in step && at >= 0) {
      e.preventDefault();
      cells[Math.min(cells.length - 1, Math.max(0, at + step[e.key]))]?.focus();
    } else if (e.key === "Tab") {
      const all = Array.from(e.currentTarget.querySelectorAll<HTMLElement>("button"));
      const first = all[0];
      const last = all[all.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  };

  return (
    <div
      className="brain-picker-scrim"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="brain-picker"
        role="dialog"
        aria-modal="true"
        aria-label="Questions"
        onKeyDown={onKeyDown}
      >
        <div className="brain-picker-head">
          <strong>Questions</strong>
          <button type="button" className="ws-btn" onClick={onClose} title="Esc">
            Close
          </button>
        </div>
        <div className="brain-picker-grid" ref={grid}>
          {state.answers.map((_, i) => (
            <button
              key={i}
              type="button"
              ref={i === state.index ? current : undefined}
              className={`brain-cell ${cellStatus(state, i)}${i === state.index ? " current" : ""}`}
              aria-label={cellLabel(state, i)}
              aria-current={i === state.index ? "true" : undefined}
              onClick={() => onPick(i)}
            >
              {i + 1}
            </button>
          ))}
        </div>
        <p className="brain-picker-legend">
          <span className="brain-key right" /> right <span className="brain-key missed" /> missed{" "}
          <span className="brain-key open" /> not answered yet
        </p>
        <p className="brain-picker-hint">
          Jump anywhere. The round ends when every question is answered; looking at an answered one pauses the clock.
        </p>
      </div>
    </div>
  );
}
