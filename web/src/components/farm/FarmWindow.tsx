/**
 * One floating window, like the game's: a title bar you drag it by, a grip in the
 * bottom-right corner you resize it by, and buttons to fold it up or close it.
 *
 * While you drag, the window's style is changed directly (no React render per
 * mouse move); the place it ends up is handed back once, on release.
 */

import { useEffect, useRef, type KeyboardEvent, type PointerEvent, type ReactNode } from "react";

import { CloseIcon, MinimiseIcon, RestoreIcon } from "./FarmIcons";
import { HUD_H, MIN_H, MIN_W, TITLE_H, clamp, type Area, type WinId, type WinRect } from "./useFarmWindows";

type Props = {
  id: WinId;
  title: string;
  icon: ReactNode;
  rect: WinRect;
  z: number;
  focused: boolean;
  minimised: boolean;
  narrow: boolean;
  area: Area;
  /** Take the keyboard focus when it appears (a window opened from the menu). */
  autoFocus?: boolean;
  onFocus: () => void;
  onCommit: (r: WinRect) => void;
  onMinimise: () => void;
  onClose: () => void;
  children: ReactNode;
};

type Drag = { mode: "move" | "size"; sx: number; sy: number; start: WinRect; cur: WinRect; moved: boolean };

export function FarmWindow({
  id, title, icon, rect, z, focused, minimised, narrow, area, autoFocus,
  onFocus, onCommit, onMinimise, onClose, children,
}: Props) {
  const rootRef = useRef<HTMLElement | null>(null);
  const barRef = useRef<HTMLElement | null>(null);
  const drag = useRef<Drag | null>(null);

  useEffect(() => {
    if (autoFocus) barRef.current?.focus({ preventScroll: true });
    // Only when it appears.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const begin = (mode: Drag["mode"]) => (e: PointerEvent<HTMLElement>) => {
    if (e.button !== 0 || narrow) return;
    if (mode === "move" && (e.target as HTMLElement).closest("button")) return;
    if (mode === "size") e.stopPropagation();
    try {
      e.currentTarget.setPointerCapture(e.pointerId);
    } catch {
      /* no capture for a synthetic pointer: the events still arrive here */
    }
    drag.current = { mode, sx: e.clientX, sy: e.clientY, start: rect, cur: rect, moved: false };
    rootRef.current?.classList.add("dragging");
  };

  const move = (e: PointerEvent<HTMLElement>) => {
    const d = drag.current;
    const el = rootRef.current;
    if (!d || !el) return;
    const dx = e.clientX - d.sx;
    const dy = e.clientY - d.sy;
    let r: WinRect;
    if (d.mode === "move") {
      r = {
        ...d.start,
        x: Math.round(clamp(d.start.x + dx, 0, Math.max(0, area.w - d.start.w))),
        y: Math.round(clamp(d.start.y + dy, HUD_H, Math.max(HUD_H, area.h - d.start.h))),
      };
    } else {
      r = {
        ...d.start,
        w: Math.round(clamp(d.start.w + dx, Math.min(MIN_W, area.w - d.start.x), area.w - d.start.x)),
        h: Math.round(clamp(d.start.h + dy, Math.min(MIN_H, area.h - d.start.y), area.h - d.start.y)),
      };
    }
    d.cur = r;
    d.moved = true;
    el.style.left = `${r.x}px`;
    el.style.top = `${r.y}px`;
    el.style.width = `${r.w}px`;
    el.style.height = `${r.h}px`;
  };

  const end = (e: PointerEvent<HTMLElement>) => {
    const d = drag.current;
    drag.current = null;
    rootRef.current?.classList.remove("dragging");
    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch {
      /* nothing was captured */
    }
    if (d?.moved) onCommit(d.cur);
  };

  /** Arrow keys on the title bar move the window; with Shift they resize it. */
  const barKey = (e: KeyboardEvent<HTMLElement>) => {
    if (e.target !== e.currentTarget || narrow) return;
    const step = 24;
    const dx = e.key === "ArrowRight" ? step : e.key === "ArrowLeft" ? -step : 0;
    const dy = e.key === "ArrowDown" ? step : e.key === "ArrowUp" ? -step : 0;
    if (!dx && !dy) return;
    e.preventDefault();
    if (e.shiftKey) {
      if (minimised) return;
      onCommit({
        ...rect,
        w: Math.round(clamp(rect.w + dx, Math.min(MIN_W, area.w - rect.x), area.w - rect.x)),
        h: Math.round(clamp(rect.h + dy, Math.min(MIN_H, area.h - rect.y), area.h - rect.y)),
      });
    } else {
      onCommit({
        ...rect,
        x: Math.round(clamp(rect.x + dx, 0, Math.max(0, area.w - rect.w))),
        y: Math.round(clamp(rect.y + dy, HUD_H, Math.max(HUD_H, area.h - rect.h))),
      });
    }
  };

  /** Esc closes the window you are in - unless the editor wants it (it uses Esc itself). */
  const rootKey = (e: KeyboardEvent<HTMLElement>) => {
    if (e.key !== "Escape" || e.defaultPrevented) return;
    const t = e.target as HTMLElement;
    if (t.closest(".monaco-editor") || t.tagName === "SELECT") return;
    e.stopPropagation();
    onClose();
  };

  return (
    <section
      ref={rootRef}
      className={`fm-win fm-win-${id}${focused ? " focused" : ""}${minimised ? " min" : ""}${narrow ? " narrow" : ""}`}
      style={{ left: rect.x, top: rect.y, width: rect.w, height: minimised ? TITLE_H : rect.h, zIndex: z }}
      role="region"
      aria-label={title}
      data-win={id}
      onPointerDownCapture={onFocus}
      onKeyDown={rootKey}
    >
      <header
        ref={barRef}
        className="fm-win-bar"
        tabIndex={0}
        title="Drag to move (arrow keys move it, Shift+arrows resize it)"
        onPointerDown={begin("move")}
        onPointerMove={move}
        onPointerUp={end}
        onPointerCancel={end}
        onDoubleClick={(e) => {
          if (!(e.target as HTMLElement).closest("button")) onMinimise();
        }}
        onKeyDown={barKey}
      >
        <span className="fm-win-icon">{icon}</span>
        <h2 className="fm-win-title">{title}</h2>
        <div className="fm-win-controls">
          <button
            type="button"
            className="fm-win-btn"
            onClick={onMinimise}
            aria-label={`${minimised ? "Restore" : "Minimise"} ${title}`}
            title={minimised ? "Restore" : "Minimise"}
          >
            {minimised ? <RestoreIcon /> : <MinimiseIcon />}
          </button>
          <button type="button" className="fm-win-btn close" onClick={onClose} aria-label={`Close ${title}`} title="Close (Esc)">
            <CloseIcon />
          </button>
        </div>
      </header>
      <div className="fm-win-body" hidden={minimised}>
        {children}
      </div>
      {minimised || narrow ? null : (
        <div
          className="fm-win-grip"
          title="Drag to resize"
          aria-hidden="true"
          onPointerDown={begin("size")}
          onPointerMove={move}
          onPointerUp={end}
          onPointerCancel={end}
        />
      )}
    </section>
  );
}
