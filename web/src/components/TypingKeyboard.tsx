import { useMemo } from "react";

import type { TypingKey } from "../types";

/**
 * The on-screen keyboard.
 *
 * It draws from the same layout the drills are generated from, so what lights
 * up is always the key the drill actually asked for. Three things are shown at
 * once, and they answer three different questions: which key you want (the
 * target glow), which finger it belongs to (the colour), and how you have been
 * doing on it so far (the heat tint).
 */

/** Row indents in key-widths, so the stagger looks like a real keyboard. */
const ROW_OFFSET = [0, 1.5, 1.75, 2.25];

/** Keys that are wider than one unit, by row index and position. */
const WIDE_LAST = [2, 1.5, 1.75, 2.25];

export type KeyStat = {
  hits: number;
  misses: number;
  /** Total reaction time in ms across hits, for the average. */
  totalMs: number;
};

type Props = {
  layout: TypingKey[][];
  fingers: Record<string, string>;
  /** The character the drill is asking for right now. */
  target: string | null;
  /** The last key pressed, for the hit/miss flash. */
  flash: { char: string; ok: boolean } | null;
  /** Per-character history, used for the heat tint. */
  stats: Record<string, KeyStat>;
  /** Dim every key outside the section being practised. */
  inScope: Set<string>;
  showHeat: boolean;
};

/** Does this key produce the target character, shifted or not? */
function producesChar(key: TypingKey, char: string): boolean {
  return key.char === char || key.shifted === char;
}

/**
 * Accuracy as a 0–1 number, or null when the key hasn't been tried enough to
 * say anything. One attempt is noise, not a weakness.
 */
function accuracyOf(stat: KeyStat | undefined): number | null {
  if (!stat) return null;
  const total = stat.hits + stat.misses;
  if (total < 3) return null;
  return stat.hits / total;
}

export default function TypingKeyboard({
  layout,
  fingers,
  target,
  flash,
  stats,
  inScope,
  showHeat,
}: Props) {
  const shiftNeeded = useMemo(() => {
    if (!target) return false;
    for (const row of layout) {
      for (const key of row) {
        if (key.shifted === target && key.char !== target) return true;
      }
    }
    return false;
  }, [layout, target]);

  return (
    <div className="tk-board" aria-hidden="true">
      {layout.map((row, rowIndex) => (
        <div
          className="tk-row"
          key={rowIndex}
          style={{ paddingLeft: `${ROW_OFFSET[rowIndex] * 2.6}rem` }}
        >
          {row.map((key) => {
            const isTarget = target != null && producesChar(key, target);
            const isFlash = flash != null && producesChar(key, flash.char);
            const scoped = inScope.size === 0 || inScope.has(key.char);
            const acc = showHeat
              ? accuracyOf(stats[key.char] ?? stats[key.shifted])
              : null;

            const classes = ["tk-key", `tk-finger-${key.finger}`];
            if (isTarget) {
              classes.push("tk-target");
              // Which of the two labels is the one being asked for. Guessing
              // it was always the shifted one dimmed the answer whenever it
              // wasn't.
              classes.push(
                target === key.shifted && key.shifted !== key.char
                  ? "tk-want-shifted"
                  : "tk-want-plain",
              );
            }
            if (isFlash) classes.push(flash!.ok ? "tk-hit" : "tk-miss");
            if (!scoped) classes.push("tk-out");

            return (
              <div
                key={key.char}
                className={classes.join(" ")}
                title={fingers[key.finger]}
                style={
                  acc == null
                    ? undefined
                    : // Green when solid, red when weak; the alpha keeps the
                      // finger colour readable underneath.
                      {
                        boxShadow: `inset 0 -0.35rem 0 hsla(${
                          acc * 120
                        }, 70%, 45%, 0.85)`,
                      }
                }
              >
                {key.shifted !== key.char && (
                  <span className="tk-shifted">{key.shifted}</span>
                )}
                <span className="tk-char">{key.char}</span>
              </div>
            );
          })}
          {/* The right-hand edge key, drawn wide so the shape reads right. */}
          <div className="tk-key tk-blank" style={{ flex: WIDE_LAST[rowIndex] }} />
        </div>
      ))}
      <div className="tk-row tk-row-space">
        <div
          className={[
            "tk-key",
            "tk-space",
            "tk-finger-th",
            target === " " ? "tk-target" : "",
            flash?.char === " " ? (flash.ok ? "tk-hit" : "tk-miss") : "",
          ]
            .filter(Boolean)
            .join(" ")}
        >
          space
        </div>
      </div>
      <div className={`tk-shift-hint ${shiftNeeded ? "on" : ""}`}>
        hold <strong>Shift</strong>
      </div>
    </div>
  );
}
