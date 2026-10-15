/** The menu cluster, bottom-left: one icon button per window, like the game's menu bar. */

import { ResetIcon } from "./FarmIcons";
import { WINDOW_DEFS } from "./windowDefs";
import { WINDOW_IDS, type WinId } from "./useFarmWindows";

type Props = {
  isOpen: (id: WinId) => boolean;
  onToggle: (id: WinId) => void;
  onReset: () => void;
};

export function FarmMenu({ isOpen, onToggle, onReset }: Props) {
  return (
    <nav className="fm-menu" aria-label="Farm windows">
      {WINDOW_IDS.map((id) => {
        const def = WINDOW_DEFS[id];
        const open = isOpen(id);
        return (
          <button
            key={id}
            type="button"
            className={`fm-menu-btn${open ? " on" : ""}`}
            aria-pressed={open}
            aria-label={`${open ? "Hide" : "Show"} ${def.title}`}
            data-tip={`${def.title}: ${def.hint}`}
            onClick={() => onToggle(id)}
          >
            {def.icon}
          </button>
        );
      })}
      <span className="fm-menu-sep" aria-hidden="true" />
      <button
        type="button"
        className="fm-menu-btn"
        aria-label="Reset the window layout"
        data-tip="Reset layout: put every window back where it started"
        onClick={onReset}
      >
        <ResetIcon />
      </button>
    </nav>
  );
}
