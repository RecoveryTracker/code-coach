/**
 * The bar across the top of the scene: what is in the barn (a counter pops "+N" when a
 * harvest pays), which farm and what it is doing, and the speed. Under it, the drone's
 * last few actions as faint lines.
 */

import type { FarmRun, FarmSnapshot } from "../../types";
import { ItemIcon } from "./FarmIcons";
import type { LogEntry, Pop } from "./farmEvents";
import { eventLine } from "./farmEvents";
import { LANGUAGE_NAMES, itemName, runText } from "./farmShared";

type Props = {
  items: Record<string, number>;
  farm: FarmSnapshot;
  language: string;
  run: FarmRun | null;
  multiFile: boolean;
  doing: string;
  warp: number;
  warps: number[];
  onWarp: (value: number) => void;
  pops: Record<string, Pop>;
  log: LogEntry[];
};

export function FarmHud({ items, farm, language, run, multiFile, doing, warp, warps, onWarp, pops, log }: Props) {
  const shown = Object.entries(items).filter(([, n]) => n > 0);
  const status = runText(run, multiFile);
  const lang = LANGUAGE_NAMES[language] ?? language;
  return (
    <>
      <header className="fm-hud">
        <ul className="fm-hud-items" aria-label="Items in the barn">
          {shown.length === 0 ? <li className="fm-hud-empty">Nothing harvested yet</li> : null}
          {shown.map(([item, n]) => {
            const pop = pops[item];
            return (
              <li key={item} className={`fm-chip${pop ? " bump" : ""}`} title={`${itemName(item)}: ${n.toLocaleString()}`}>
                <ItemIcon item={item} />
                <b key={pop ? pop.id : 0} className="fm-chip-n">
                  {n.toLocaleString()}
                </b>
                <span className="fm-sr">{itemName(item)}</span>
                {pop ? (
                  <span key={`p${pop.id}`} className="fm-chip-pop" aria-hidden="true">
                    +{pop.amount.toLocaleString()}
                  </span>
                ) : null}
              </li>
            );
          })}
        </ul>
        <div
          className="fm-hud-status"
          title={`Each language has its own farm, with its own items, research and code. Farm time ${farm.time.toFixed(1)}s`}
        >
          <span>
            {lang} farm · {farm.w}×{farm.h} · speed {farm.speed}×
          </span>
          {status ? <span className={`fm-run ${run?.status ?? ""}`}>{status}</span> : null}
          {doing ? (
            <span className="fm-doing" title="What the drone is doing right now">
              {doing}
            </span>
          ) : null}
        </div>
        <label className="fm-hud-speed" title="Time warp: how many game seconds pass per real second">
          <span>Speed</span>
          <select value={warp} onChange={(e) => onWarp(Number(e.target.value))} aria-label="Time warp">
            {warps.map((w) => (
              <option key={w} value={w}>
                {w === 0 ? "max" : `${w}×`}
              </option>
            ))}
          </select>
        </label>
      </header>
      {log.length ? (
        <ol className="fm-log" aria-label="Action log">
          {log.map((l, i) => (
            <li
              key={l.ev.n}
              className={l.ev.ok ? "" : "failed"}
              style={{ opacity: 0.35 + (0.65 * (i + 1)) / log.length }}
            >
              {eventLine(l.ev)}
            </li>
          ))}
        </ol>
      ) : null}
    </>
  );
}
