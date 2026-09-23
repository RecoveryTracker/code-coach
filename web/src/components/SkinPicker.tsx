import { useRef, useState } from "react";

import { SKINS, applySkin, useSkin, type SkinId } from "../skins";
import { menuStyle, useDismiss, useMenuPlacement } from "./menuPlacement";

/**
 * The look of the whole app, one click to change.
 *
 * In the top bar beside the language, because it applies to every
 * screen - a setting buried in one module would suggest it only
 * affected that module.
 *
 * Each row carries a swatch of the skin's own colours: background,
 * panel, accent, and the right and wrong colours. The swatch is an
 * element with the skin's data attribute, so it is painted by the same
 * rules the app uses and cannot drift from them.
 */
export function SkinPicker() {
  const skin = useSkin();
  const [open, setOpen] = useState(false);
  const wrap = useRef<HTMLDivElement | null>(null);
  const menu = useRef<HTMLDivElement | null>(null);
  const at = useMenuPlacement(open, wrap, menu, [SKINS.length]);
  useDismiss(open, wrap, () => setOpen(false));

  const current = SKINS.find((s) => s.id === skin) ?? SKINS[0];

  function choose(id: SkinId) {
    setOpen(false);
    if (id !== skin) applySkin(id);
  }

  return (
    <div className="skin-pick-wrap" ref={wrap}>
      <button
        type="button"
        className={`ws-btn skin-pick-button${open ? " on" : ""}`}
        onClick={() => setOpen((o) => !o)}
        title="How the app looks"
        aria-expanded={open}
      >
        <Swatch id={current.id} small />
        {current.name}
      </button>

      {open && (
        <div className="skin-pick-menu" ref={menu} style={menuStyle(at)}>
          <p className="skin-pick-hint">How the app looks. Changes it everywhere.</p>
          <div className="skin-pick-list">
            {SKINS.map((s) => (
              <button
                key={s.id}
                type="button"
                className={`skin-pick-row${s.id === skin ? " on" : ""}`}
                onClick={() => choose(s.id)}
              >
                <Swatch id={s.id} />
                <span className="skin-pick-text">
                  <span className="skin-pick-name">{s.name}</span>
                  <span className="skin-pick-desc">{s.hint}</span>
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Swatch({ id, small = false }: { id: SkinId; small?: boolean }) {
  return (
    <span
      data-skin={id}
      className={`skin-swatch${small ? " small" : ""}`}
      aria-hidden="true"
    >
      <span style={{ background: "var(--r-bg)" }} />
      <span style={{ background: "var(--r-bg-panel)" }} />
      <span style={{ background: "var(--r-accent)" }} />
      <span style={{ background: "var(--r-success)" }} />
      <span style={{ background: "var(--r-danger)" }} />
    </span>
  );
}
