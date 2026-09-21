import { useRef, useState } from "react";

import { menuStyle, useDismiss, useMenuPlacement } from "./menuPlacement";
import type { TypingTheme } from "../types";

type Props = {
  /** The current theme id, which may name several joined with commas. */
  value: string;
  choices: TypingTheme[];
  onChange: (themeId: string) => void;
};

const SEPARATOR = ",";
/** Matches blends.MAX_PARTS on the server. Past this the pool is so
 *  mixed that a sitting never covers any of it. */
const MAX_PARTS = 6;

export function splitThemeId(value: string): string[] {
  return value
    .split(SEPARATOR)
    .map((part) => part.trim())
    .filter(Boolean);
}

/**
 * Which text the drill draws from: one theme, or several at once.
 *
 * The old control was a plain <select>, which is the right shape for
 * "pick one" and cannot express "both". Both is what was actually
 * wanted: somebody learning Python wants its code and its lore in the
 * same sitting, and somebody working on two languages wants all four.
 *
 * The rule the design has to satisfy is that switching stays one
 * click. It was said plainly — "I go to it all the time, I wouldn't
 * want it two clicks away" — and a checkbox list alone would have cost
 * two every time: untick the old, tick the new.
 *
 * So each row does both jobs, and which one you get depends on where
 * you click:
 *
 *   the row   -> switch to just this, and close. One click, as before.
 *   the tick  -> add it to what is already chosen, and stay open.
 *
 * That keeps the common action at its old cost and puts the new one
 * next to it, rather than behind a mode switch that has to be found
 * and understood first.
 */
export function TextPicker({ value, choices, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const wrap = useRef<HTMLDivElement | null>(null);
  const menu = useRef<HTMLDivElement | null>(null);
  /* Shared with the other menus in this row. Placement is three
     bugs deep and all three only appear on a small window, so there
     is one copy of it - see menuPlacement.ts. */
  const at = useMenuPlacement(open, wrap, menu, [choices.length]);
  useDismiss(open, wrap, () => setOpen(false));

  const picked = splitThemeId(value);
  const pickedSet = new Set(picked);


  /** Click the row: this one, on its own. */
  function only(id: string) {
    setOpen(false);
    if (id !== value) onChange(id);
  }

  /** Click the tick: add or remove, keeping the order they were added. */
  function toggle(id: string) {
    let next: string[];
    if (pickedSet.has(id)) {
      next = picked.filter((p) => p !== id);
      // Unticking the last one would leave an empty pool, which the
      // server would answer with the default theme - a silent switch
      // to English prose in the middle of a code drill. Keeping it is
      // the honest refusal.
      if (next.length === 0) return;
    } else {
      if (picked.length >= MAX_PARTS) return;
      next = [...picked, id];
    }
    onChange(next.join(SEPARATOR));
  }

  const names = picked
    .map((id) => choices.find((c) => c.id === id)?.name ?? id)
    .filter(Boolean);
  const label =
    names.length === 0
      ? "Text"
      : names.length === 1
        ? names[0]
        : `${names[0]} +${names.length - 1}`;

  return (
    <div className="text-pick-wrap" ref={wrap}>
      <span className="text-pick-caption">Text</span>
      <button
        type="button"
        className={`text-pick-button${open ? " on" : ""}`}
        onClick={() => setOpen((o) => !o)}
        title={
          names.length > 1
            ? `Drawing from ${names.join(" and ")}`
            : "What the drill draws from"
        }
        aria-expanded={open}
      >
        {label}
      </button>

      {open && (
        <div
          className="text-pick-menu"
          ref={menu}
          style={menuStyle(at)}
        >
          <p className="text-pick-hint">
            Click a name for just that one. Tick to add it to the mix.
          </p>
          <div className="text-pick-list">
            {choices.map((choice) => {
              const on = pickedSet.has(choice.id);
              return (
                <div
                  key={choice.id}
                  className={`text-pick-row${on ? " on" : ""}`}
                >
                  <input
                    type="checkbox"
                    checked={on}
                    onChange={() => toggle(choice.id)}
                    aria-label={`Include ${choice.name}`}
                    title={
                      on && picked.length === 1
                        ? "The last one can't be unticked"
                        : `Include ${choice.name} in the mix`
                    }
                  />
                  <button
                    type="button"
                    className="text-pick-name"
                    onClick={() => only(choice.id)}
                    title={choice.description}
                  >
                    {choice.name}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
