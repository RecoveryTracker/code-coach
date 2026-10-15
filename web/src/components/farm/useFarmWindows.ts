/**
 * The Farm's floating windows: where each one is, how big, whether it is open or
 * folded up, and which is in front. Remembered in localStorage under one key.
 *
 * Until you move something the layout is the default one, worked out from the size
 * of the screen, so it follows the browser window. What is shown is always clamped
 * to the screen (a window saved on a big monitor still fits a small one).
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

export const WINDOW_IDS = ["code", "output", "research", "docs", "playbook"] as const;
export type WinId = (typeof WINDOW_IDS)[number];
export type Area = { w: number; h: number };
export type WinRect = { x: number; y: number; w: number; h: number };
export type WinState = WinRect & { open: boolean; min: boolean };
export type Layout = { wins: Record<WinId, WinState>; order: WinId[] };

export const LAYOUT_KEY = "code-coach:farm-windows:v1";
/** The HUD across the top, the menu along the bottom-left, and a window's title bar. */
export const HUD_H = 46;
export const MENU_H = 58;
export const TITLE_H = 34;
export const MIN_W = 260;
export const MIN_H = 150;
/** Under this width the Code window is full width and every other window a full-screen overlay. */
export const NARROW = 700;

export function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n));
}

export function defaultLayout(area: Area): Layout {
  const W = Math.max(area.w, 320);
  const H = Math.max(area.h, 320);
  const top = HUD_H + 8;
  const codeW = Math.round(clamp(W * 0.46, 420, 780));
  const codeH = Math.max(MIN_H, H - top - MENU_H);
  const outW = Math.round(clamp(W * 0.34, 300, 520));
  const outH = Math.round(clamp(H * 0.26, 150, 260));
  const sideX = codeW + 22;
  const sideW = Math.round(clamp(W - sideX - 12, 340, 860));
  const sideH = Math.round(clamp(H * 0.7, 320, 700));
  const closed = (i: number): WinState => ({
    x: sideX + i * 28, y: top + i * 28, w: sideW, h: sideH, open: false, min: false,
  });
  return {
    wins: {
      code: { x: 10, y: top, w: codeW, h: codeH, open: true, min: false },
      output: { x: W - outW - 12, y: H - outH - 12, w: outW, h: outH, open: true, min: false },
      research: closed(0),
      docs: closed(1),
      playbook: closed(2),
    },
    // Last is in front. Code is above Output so that, stacked on a narrow screen, you land on the code.
    order: ["research", "docs", "playbook", "output", "code"],
  };
}

function finite(n: unknown): n is number {
  return typeof n === "number" && Number.isFinite(n);
}

/** What was saved, as far as it can be trusted; anything wrong is dropped (and defaulted later). */
function loadSaved(): Partial<Layout> | null {
  try {
    const raw = localStorage.getItem(LAYOUT_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw) as { wins?: Record<string, Partial<WinState>>; order?: unknown };
    const wins: Partial<Record<WinId, WinState>> = {};
    for (const id of WINDOW_IDS) {
      const s = data.wins?.[id];
      if (s && finite(s.x) && finite(s.y) && finite(s.w) && finite(s.h)) {
        wins[id] = { x: s.x, y: s.y, w: s.w, h: s.h, open: !!s.open, min: !!s.min };
      }
    }
    const order = Array.isArray(data.order)
      ? (data.order.filter((id): id is WinId => (WINDOW_IDS as readonly string[]).includes(id as string)) as WinId[])
      : [];
    return { wins: wins as Record<WinId, WinState>, order };
  } catch {
    return null;
  }
}

function persist(layout: Layout) {
  try {
    localStorage.setItem(LAYOUT_KEY, JSON.stringify(layout));
  } catch {
    /* the layout just isn't remembered */
  }
}

/** The saved layout filled in from the default wherever it is missing. */
function complete(saved: Partial<Layout> | null, area: Area): Layout {
  const base = defaultLayout(area);
  if (!saved) return base;
  const wins = { ...base.wins };
  for (const id of WINDOW_IDS) if (saved.wins?.[id]) wins[id] = saved.wins[id];
  const order = [...(saved.order ?? []).filter((id, i, all) => all.indexOf(id) === i)];
  for (const id of base.order) if (!order.includes(id)) order.unshift(id);
  return { wins, order };
}

/** Where a window is actually drawn: inside the screen, under the HUD, never smaller than the minimum. */
export function placed(s: WinState, area: Area, narrow: boolean): WinRect {
  const availH = Math.max(MIN_H, area.h - HUD_H);
  if (narrow) return { x: 0, y: HUD_H, w: area.w, h: s.min ? TITLE_H : Math.max(MIN_H, availH - MENU_H) };
  const w = Math.round(clamp(s.w, Math.min(MIN_W, area.w), area.w));
  const full = Math.round(clamp(s.h, Math.min(MIN_H, availH), availH));
  const h = s.min ? TITLE_H : full;
  const x = Math.round(clamp(s.x, 0, Math.max(0, area.w - w)));
  const y = Math.round(clamp(s.y, HUD_H, Math.max(HUD_H, area.h - h)));
  return { x, y, w, h };
}

export function useFarmWindows(area: Area) {
  const [saved, setSaved] = useState<Partial<Layout> | null>(loadSaved);
  const areaRef = useRef(area);
  areaRef.current = area;
  const touched = useRef(false);

  const layout = useMemo(() => complete(saved, area), [saved, area]);
  const narrow = area.w > 0 && area.w < NARROW;
  const rects = useMemo(() => {
    const out = {} as Record<WinId, WinRect>;
    for (const id of WINDOW_IDS) out[id] = placed(layout.wins[id], area, narrow);
    return out;
  }, [layout, area, narrow]);

  // Only a layout the user has changed is saved; the default keeps following the screen.
  useEffect(() => {
    if (touched.current && saved) persist(saved as Layout);
  }, [saved]);

  const change = useCallback((fn: (l: Layout) => Layout) => {
    touched.current = true;
    setSaved((prev) => fn(complete(prev, areaRef.current)));
  }, []);

  const toFront = (l: Layout, id: WinId): Layout =>
    l.order[l.order.length - 1] === id ? l : { ...l, order: [...l.order.filter((o) => o !== id), id] };

  /** Bring to front (a click on a window). */
  const focus = useCallback(
    (id: WinId) => {
      // A click on the window already in front changes nothing, so it should not rewrite the save either.
      setSaved((prev) => {
        const cur = complete(prev, areaRef.current);
        if (cur.order[cur.order.length - 1] === id) return prev;
        touched.current = true;
        return toFront(cur, id);
      });
    },
    [],
  );

  const toggle = useCallback(
    (id: WinId) =>
      change((l) => {
        const w = l.wins[id];
        if (w.open) return { ...l, wins: { ...l.wins, [id]: { ...w, open: false } } };
        return toFront({ ...l, wins: { ...l.wins, [id]: { ...w, open: true, min: false } } }, id);
      }),
    [change],
  );

  /** Open it if it is shut (or fold it out), and put it in front. */
  const reveal = useCallback(
    (id: WinId) =>
      change((l) => {
        const w = l.wins[id];
        const next = w.open && !w.min ? l : { ...l, wins: { ...l.wins, [id]: { ...w, open: true, min: false } } };
        return toFront(next, id);
      }),
    [change],
  );

  const close = useCallback(
    (id: WinId) => change((l) => ({ ...l, wins: { ...l.wins, [id]: { ...l.wins[id], open: false } } })),
    [change],
  );

  const toggleMin = useCallback(
    (id: WinId) => change((l) => ({ ...l, wins: { ...l.wins, [id]: { ...l.wins[id], min: !l.wins[id].min } } })),
    [change],
  );

  /** A drag or resize ended: remember where the window is now (a folded window keeps its full height). */
  const commitRect = useCallback(
    (id: WinId, r: WinRect) =>
      change((l) => {
        const w = l.wins[id];
        return { ...l, wins: { ...l.wins, [id]: { ...w, x: r.x, y: r.y, w: r.w, h: w.min ? w.h : r.h } } };
      }),
    [change],
  );

  const reset = useCallback(() => {
    touched.current = false;
    setSaved(null);
    try {
      localStorage.removeItem(LAYOUT_KEY);
    } catch {
      /* nothing to clear */
    }
  }, []);

  return { layout, rects, narrow, focus, toggle, reveal, close, toggleMin, commitRect, reset };
}
