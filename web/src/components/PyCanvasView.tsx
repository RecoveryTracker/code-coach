/**
 * The preview for a Python Canvas step: a real <canvas> the server draws on.
 *
 * Python cannot draw in a browser, so the program runs on the server in a
 * process of its own (code_coach/canvas/pyharness), one frame per request.
 * This component is the other half: it sends the keys held and the clicks,
 * gets back the draw calls that frame made, and paints them, in order, on
 * the canvas - which, like any canvas, keeps whatever was drawn until
 * something draws over it.
 *
 * One request is in flight at a time. If the browser is faster than the
 * server it simply asks again when the answer comes (so the game runs at the
 * server's pace, with dt - the real seconds since the last frame, capped -
 * telling the program how long that was); it never asks faster than 60 a
 * second. Mount it with a new `key` to Run again: unmounting stops the
 * session, and so does the page going away.
 */

import { useEffect, useRef } from "react";

import { startPyCanvas, stepPyCanvas, stopPyCanvas } from "../api";
import type { PyCall, PyEvent, PyFrame } from "../types";

type Props = {
  stepId: string;
  /** The program, as it was when Run was pressed. */
  code: string;
  /** Lines the program printed. */
  onLog: (lines: string[]) => void;
  /** The program crashed, or the session ended: what to tell the learner. */
  onError: (text: string) => void;
};

/** What the server calls each drawing call, and what the browser calls it. */
const METHODS: Record<string, string> = {
  fill_rect: "fillRect",
  clear_rect: "clearRect",
  stroke_rect: "strokeRect",
  rect: "rect",
  begin_path: "beginPath",
  close_path: "closePath",
  move_to: "moveTo",
  line_to: "lineTo",
  arc: "arc",
  ellipse: "ellipse",
  quadratic_curve_to: "quadraticCurveTo",
  bezier_curve_to: "bezierCurveTo",
  fill: "fill",
  stroke: "stroke",
  fill_text: "fillText",
  stroke_text: "strokeText",
  save: "save",
  restore: "restore",
  translate: "translate",
  rotate: "rotate",
  scale: "scale",
};

/** Keys a game uses that would otherwise scroll the page. */
const GAME_KEYS = new Set(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "]);
const MIN_FRAME_MS = 1000 / 60;
const MAX_DT = 0.05;
const MAX_EVENTS = 100;

/** Paint a list of recorded calls on a 2d context, in order. */
export function paint(ctx: CanvasRenderingContext2D, calls: PyCall[]): void {
  // What the context was last set to, so a long list does not set the same
  // style over and over. save and restore bring back styles of their own.
  let fill: string | null = null;
  let stroke: string | null = null;
  let extra: PyCall[4] | null = null;
  for (const [name, args, wantFill, wantStroke, state] of calls) {
    const method = METHODS[name];
    if (!method) continue;
    if (wantFill !== fill) ctx.fillStyle = fill = wantFill;
    if (wantStroke !== stroke) ctx.strokeStyle = stroke = wantStroke;
    if (extra === null || extra.lineWidth !== state.lineWidth) ctx.lineWidth = state.lineWidth;
    if (extra === null || extra.font !== state.font) ctx.font = state.font;
    if (extra === null || extra.textAlign !== state.textAlign) ctx.textAlign = state.textAlign as CanvasTextAlign;
    if (extra === null || extra.textBaseline !== state.textBaseline) {
      ctx.textBaseline = state.textBaseline as CanvasTextBaseline;
    }
    if (extra === null || extra.globalAlpha !== state.globalAlpha) ctx.globalAlpha = state.globalAlpha;
    extra = state;
    try {
      (ctx as unknown as Record<string, (...a: unknown[]) => void>)[method](...args);
    } catch {
      /* a call the browser refuses is skipped, as a canvas skips a bad one */
    }
    if (name === "restore" || name === "save") {
      fill = stroke = null;
      extra = null;
    }
  }
}

/** The text of a failed request: the server's own reason when it gave one. */
function reason(e: unknown): string {
  const text = e instanceof Error ? e.message : String(e);
  try {
    const detail = (JSON.parse(text) as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
  } catch {
    /* not JSON: show it as it is */
  }
  return text;
}

export default function PyCanvasView({ stepId, code, onLog, onError }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const logRef = useRef(onLog);
  const errorRef = useRef(onError);
  logRef.current = onLog;
  errorRef.current = onError;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    let alive = true;
    let session = "";
    let raf = 0;
    let busy = false;
    let last = 0;
    const held = new Set<string>();
    let events: PyEvent[] = [];
    let moved: { x: number; y: number } | null = null;
    // What the program asked for last: with no on_frame and no timer there
    // is nothing to advance, so frames are only run for events it can hear.
    let wantFrames = true;
    let wantInput = true;

    const name = (e: KeyboardEvent) => (e.key.length === 1 ? e.key.toLowerCase() : e.key);
    const at = (e: MouseEvent) => {
      // The border is not canvas: measure from the inside of it.
      const box = canvas.getBoundingClientRect();
      return {
        x: ((e.clientX - box.left - canvas.clientLeft) * canvas.width) / (canvas.clientWidth || 1),
        y: ((e.clientY - box.top - canvas.clientTop) * canvas.height) / (canvas.clientHeight || 1),
      };
    };
    const queue = (ev: PyEvent) => {
      if (events.length < MAX_EVENTS) events.push(ev);
    };

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (GAME_KEYS.has(e.key)) e.preventDefault();
      if (e.repeat) return;
      const key = name(e);
      held.add(key);
      queue({ type: "keydown", key });
    };
    const onKeyUp = (e: KeyboardEvent) => {
      const key = name(e);
      held.delete(key);
      queue({ type: "keyup", key });
    };
    const onBlur = () => {
      for (const key of held) queue({ type: "keyup", key });
      held.clear();
    };
    const onMove = (e: MouseEvent) => {
      moved = at(e);
    };
    const onClick = (e: MouseEvent) => {
      canvas.focus();
      const p = at(e);
      moved = null;
      queue({ type: "click", x: p.x, y: p.y });
    };
    canvas.addEventListener("keydown", onKeyDown);
    canvas.addEventListener("keyup", onKeyUp);
    canvas.addEventListener("blur", onBlur);
    canvas.addEventListener("mousemove", onMove);
    canvas.addEventListener("click", onClick);

    const leave = () => {
      if (session) stopPyCanvas(session);
    };
    window.addEventListener("pagehide", leave);
    window.addEventListener("beforeunload", leave);

    /** Paint what came back, say what it printed, and stop if that was the end. */
    const show = (frame: PyFrame): boolean => {
      paint(ctx, frame.calls);
      wantFrames = frame.frames;
      wantInput = frame.input;
      if (frame.logs.length) logRef.current(frame.logs);
      if (frame.error) {
        const where = frame.error.line ? `Line ${frame.error.line}: ` : "";
        errorRef.current(where + frame.error.message);
        return true;
      }
      return !wantFrames && !wantInput; // nothing left that could change the picture
    };
    const finish = () => {
      cancelAnimationFrame(raf);
      if (session) stopPyCanvas(session);
      session = "";
    };

    const tick = (now: number) => {
      if (!alive) return;
      raf = requestAnimationFrame(tick);
      if (busy || now - last < MIN_FRAME_MS - 1) return;
      if (!wantFrames && events.length === 0) return;
      busy = true;
      const dt = Math.min(MAX_DT, Math.max(1 / 60, (now - last) / 1000));
      last = now;
      const sent = events;
      events = [];
      if (moved) {
        sent.unshift({ type: "mousemove", x: moved.x, y: moved.y });
        moved = null;
      }
      stepPyCanvas(session, dt, [...held], sent)
        .then((frame) => {
          if (alive && show(frame)) finish();
        })
        .catch((e: unknown) => {
          if (!alive) return;
          errorRef.current(reason(e));
          finish();
        })
        .finally(() => {
          busy = false;
        });
    };

    startPyCanvas(stepId, code)
      .then((first) => {
        if (!alive) {
          if (first.session) stopPyCanvas(first.session);
          return;
        }
        session = first.session;
        if (show(first) || !session) {
          finish(); // nothing to step: free the server's process now
          return;
        }
        canvas.focus();
        last = performance.now();
        raf = requestAnimationFrame(tick);
      })
      .catch((e: unknown) => {
        if (alive) errorRef.current(reason(e));
      });

    return () => {
      alive = false;
      cancelAnimationFrame(raf);
      window.removeEventListener("pagehide", leave);
      window.removeEventListener("beforeunload", leave);
      canvas.removeEventListener("keydown", onKeyDown);
      canvas.removeEventListener("keyup", onKeyUp);
      canvas.removeEventListener("blur", onBlur);
      canvas.removeEventListener("mousemove", onMove);
      canvas.removeEventListener("click", onClick);
      if (session) stopPyCanvas(session);
    };
  }, [stepId, code]);

  return (
    <canvas
      ref={canvasRef}
      className="canvas-frame py-canvas"
      width={480}
      height={320}
      tabIndex={0}
      aria-label="Your game"
    />
  );
}
