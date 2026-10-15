/**
 * The farm as the whole screen's background: one canvas, painted by drawScene() from
 * the latest snapshot and a running clock, from a requestAnimationFrame loop that
 * reads refs (it never makes React render).
 *
 * The canvas is the host's size plus `insetX` and `insetY` on the left and top, tucked
 * out of sight past the host's edge. The scene centres its farm in its canvas, so
 * that makes the farm centre in what is left of the screen after the Code window
 * (left) and the HUD (top). The background still fills everything.
 */

import { useEffect, useLayoutEffect, useRef } from "react";

import { drawScene } from "../../lib/farmScene";
import type { FarmSnapshot } from "../../types";

type Props = {
  snap: FarmSnapshot;
  insetX: number;
  insetY: number;
  /** A simulation's farm is being shown, not yours. */
  sim: boolean;
};

/** The animation runs at about this many frames a second: plenty for a farm, kind to the machine. */
const FRAME_MS = 1000 / 40;
/** No more than this many device pixels per css pixel, and no more than this many pixels altogether. */
const MAX_DPR = 2;
const MAX_PIXELS = 9_000_000;

export function FarmScene({ snap, insetX, insetY, sim }: Props) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const snapRef = useRef(snap);
  snapRef.current = snap;
  const insetRef = useRef({ x: insetX, y: insetY });
  insetRef.current = { x: insetX, y: insetY };
  const size = useRef({ w: 0, h: 0, dpr: 1 });
  const t0 = useRef(performance.now());
  const failed = useRef(false);

  const draw = useRef(() => {});
  draw.current = () => {
    const canvas = canvasRef.current;
    const { w, h, dpr } = size.current;
    if (!canvas || w < 1 || h < 1) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    try {
      drawScene(ctx, snapRef.current, { width: w, height: h, time: (performance.now() - t0.current) / 1000 });
    } catch (e) {
      // A scene that throws must not take the screen with it; say so once.
      if (!failed.current) console.error("farm scene failed to draw", e);
      failed.current = true;
    }
  };

  /** Make the backing store match the host (plus the inset) at the screen's pixel density. */
  const resize = useRef(() => {});
  resize.current = () => {
    const host = hostRef.current;
    const canvas = canvasRef.current;
    if (!host || !canvas) return;
    const w = Math.max(1, Math.round(host.clientWidth + insetRef.current.x));
    const h = Math.max(1, Math.round(host.clientHeight + insetRef.current.y));
    let dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    if (w * h * dpr * dpr > MAX_PIXELS) dpr = Math.max(1, Math.sqrt(MAX_PIXELS / (w * h)));
    const bw = Math.round(w * dpr);
    const bh = Math.round(h * dpr);
    if (canvas.width !== bw || canvas.height !== bh) {
      canvas.width = bw;
      canvas.height = bh;
    }
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    size.current = { w, h, dpr: bw / w };
    draw.current();
  };

  useLayoutEffect(() => {
    resize.current();
  }, [insetX, insetY]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const watcher = new ResizeObserver(() => resize.current());
    watcher.observe(host);
    resize.current();
    return () => watcher.disconnect();
  }, []);

  // The animation loop: stops while the page is hidden and when this screen goes away.
  useEffect(() => {
    let raf = 0;
    let last = 0;
    const frame = (now: number) => {
      raf = requestAnimationFrame(frame);
      if (now - last < FRAME_MS) return;
      last = now;
      draw.current();
    };
    const start = () => {
      if (!raf && !document.hidden) raf = requestAnimationFrame(frame);
    };
    const stop = () => {
      if (raf) cancelAnimationFrame(raf);
      raf = 0;
    };
    const onVisibility = () => (document.hidden ? stop() : start());
    document.addEventListener("visibilitychange", onVisibility);
    start();
    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      stop();
    };
  }, []);

  // A new snapshot is painted at once too (the loop may not run, e.g. in a hidden pane).
  useEffect(() => {
    draw.current();
  }, [snap]);

  return (
    <div ref={hostRef} className={`fm-scene${sim ? " sim" : ""}`} aria-hidden="true">
      <canvas ref={canvasRef} className="fm-canvas" />
    </div>
  );
}
