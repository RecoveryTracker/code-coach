import { useEffect, useLayoutEffect, useRef, useState } from "react";

/** Where a dropped menu sits, and how tall it is allowed to be. */
export type Placement = {
  left: number;
  top: number;
  maxHeight: number;
};

/** Breathing room kept between a menu and the edge of the window. */
const EDGE = 8;

/**
 * Place a menu under a button so that it is always fully on screen.
 *
 * This exists because the same placement was written twice and had the
 * same bug both times, which is the argument for it existing rather
 * than a third copy.
 *
 * Three things go wrong in order, and each one only shows up on a
 * window smaller than the one you developed on:
 *
 *  1. Anchoring the menu's right edge to the button's sends it off the
 *     left of the screen once the button is near the left edge. That
 *     one shipped, on a half-width window, and the menu was simply
 *     unreadable.
 *  2. Dropping it below the button runs off the bottom on a short
 *     window, so it flips above when there is room above.
 *  3. When there is room in neither direction — a long list on a short
 *     window — flipping cannot help and the menu overflows anyway.
 *     The only answer left is to make it shorter, so the caller is
 *     told how much height it may use and the list scrolls inside
 *     that.
 *
 * The third is the one both copies got wrong: they chose a side and
 * then trusted a CSS max-height that knew nothing about where the
 * button happened to be.
 *
 * Measured rather than guessed, because the width comes from CSS and
 * duplicating it here would be two places to change.
 */
export function useMenuPlacement(
  open: boolean,
  wrap: React.RefObject<HTMLElement | null>,
  menu: React.RefObject<HTMLElement | null>,
  deps: unknown[] = [],
): Placement | null {
  const [at, setAt] = useState<Placement | null>(null);
  // Held in a ref so re-measuring never depends on the last answer,
  // which would loop: setting a max-height changes the height.
  const natural = useRef(0);

  useLayoutEffect(() => {
    if (!open) {
      natural.current = 0;
      return;
    }
    const place = () => {
      const button = wrap.current?.getBoundingClientRect();
      if (!button) return;
      const width = menu.current?.offsetWidth ?? 300;
      // The height it wants, remembered from before it was capped.
      const height = Math.max(natural.current, menu.current?.scrollHeight ?? 0);
      natural.current = height;

      const left = Math.min(
        Math.max(EDGE, button.left),
        Math.max(EDGE, window.innerWidth - width - EDGE),
      );

      const roomBelow = window.innerHeight - button.bottom - 5 - EDGE;
      const roomAbove = button.top - 5 - EDGE;

      // Below when it fits, above when that fits instead, and
      // otherwise whichever side has more room, shortened to it.
      let top: number;
      let maxHeight: number;
      if (height <= roomBelow) {
        top = button.bottom + 5;
        maxHeight = roomBelow;
      } else if (height <= roomAbove) {
        top = button.top - height - 5;
        maxHeight = roomAbove;
      } else if (roomBelow >= roomAbove) {
        top = button.bottom + 5;
        maxHeight = Math.max(120, roomBelow);
      } else {
        maxHeight = Math.max(120, roomAbove);
        top = Math.max(EDGE, button.top - maxHeight - 5);
      }
      setAt({ left, top, maxHeight });
    };
    place();
    window.addEventListener("resize", place);
    window.addEventListener("scroll", place, true);
    return () => {
      window.removeEventListener("resize", place);
      window.removeEventListener("scroll", place, true);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, ...deps]);

  return at;
}

/** Close a menu on a click outside it, or on Escape. */
export function useDismiss(
  open: boolean,
  wrap: React.RefObject<HTMLElement | null>,
  close: () => void,
) {
  useEffect(() => {
    if (!open) return;
    const onDown = (e: PointerEvent) => {
      if (!wrap.current?.contains(e.target as Node)) close();
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("pointerdown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("pointerdown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open, wrap, close]);
}

/** The inline style for a placed menu, hidden until it is measured. */
export function menuStyle(at: Placement | null): React.CSSProperties {
  return at
    ? {
        position: "fixed",
        left: at.left,
        top: at.top,
        maxHeight: at.maxHeight,
        display: "flex",
        flexDirection: "column",
      }
    : { position: "fixed", visibility: "hidden" };
}
