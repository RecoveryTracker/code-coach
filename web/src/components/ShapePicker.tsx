import { useRef, useState } from "react";

import { menuStyle, useDismiss, useMenuPlacement } from "./menuPlacement";
import type { TypingShape } from "../types";

type Props = {
  /** The chosen shape id, or "" for whichever the draw lands on. */
  value: string;
  shapes: TypingShape[];
  onChange: (shapeId: string) => void;
};

/**
 * Which kind of line a Same Shape run drills.
 *
 * Same Shape already worked without this: it picked a shape itself,
 * weighted by how many real lines share it, so the commonest shapes
 * came up most. That is the right default and it stays the default —
 * "Any" is the first row and the initial value.
 *
 * What it could not do is the thing actually asked for, which was
 * "twenty console.log calls, now". Weighted-random will get you there
 * eventually and eventually is no use when you have decided what to
 * practise.
 *
 * Each row shows a real line rather than a description of one. "show
 * X" is what the grouping calls this shape internally and it tells
 * you nothing; `console.log(label(7));` is the thing you are about to
 * type twenty times. The count beside it is the honest measure of how
 * common the shape is, which is the reason to choose one over
 * another.
 */
export function ShapePicker({ value, shapes, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const wrap = useRef<HTMLDivElement | null>(null);
  const menu = useRef<HTMLDivElement | null>(null);
  /* Shared with the other menus in this row. Placement is three
     bugs deep and all three only appear on a small window, so there
     is one copy of it - see menuPlacement.ts. */
  const at = useMenuPlacement(open, wrap, menu, [shapes.length]);
  useDismiss(open, wrap, () => setOpen(false));


  function choose(id: string) {
    setOpen(false);
    if (id !== value) onChange(id);
  }

  const active = shapes.find((s) => s.id === value);
  const label = active ? active.example : "Any shape";

  return (
    <div className="shape-pick-wrap" ref={wrap}>
      <span className="shape-pick-caption">Shape</span>
      <button
        type="button"
        className={`shape-pick-button${open ? " on" : ""}`}
        onClick={() => setOpen((o) => !o)}
        title={
          active
            ? `Drilling ${active.example} — ${active.count} real lines`
            : "Which kind of line to drill"
        }
        aria-expanded={open}
        disabled={shapes.length === 0}
      >
        {shapes.length === 0 ? "No shapes" : label}
      </button>

      {open && shapes.length > 0 && (
        <div
          className="shape-pick-menu"
          ref={menu}
          style={menuStyle(at)}
        >
          <p className="shape-pick-hint">
            One of these, over and over, with only the middle changing.
            The number is how many real lines the drill can draw from.
          </p>
          <div className="shape-pick-list">
            <button
              type="button"
              className={`shape-pick-row${value === "" ? " on" : ""}`}
              onClick={() => choose("")}
            >
              <code className="shape-pick-example">Any shape</code>
              <span className="shape-pick-count">
                weighted by how common
              </span>
            </button>
            {shapes.map((shape) => (
              <button
                key={shape.id}
                type="button"
                className={`shape-pick-row${
                  shape.id === value ? " on" : ""
                }`}
                onClick={() => choose(shape.id)}
              >
                <code className="shape-pick-example">{shape.example}</code>
                <span className="shape-pick-count">{shape.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
