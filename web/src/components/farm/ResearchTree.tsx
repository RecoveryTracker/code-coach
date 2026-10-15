/**
 * Research as a tree: a card per unlock, in a column by how many unlocks lie behind it,
 * with a line from each unlock it needs. The window scrolls (and you can drag the
 * background to pan) when the tree is bigger than it.
 */

import { useRef, type PointerEvent } from "react";

import type { FarmUnlock } from "../../types";
import { ItemIcon } from "./FarmIcons";
import { costText, itemName } from "./farmShared";

export const CARD_W = 232;
export const CARD_H = 156;
export const COL_GAP = 62;
export const ROW_GAP = 14;
export const TREE_PAD = 18;

export type TreeNode = { u: FarmUnlock; depth: number; row: number; x: number; y: number };
export type TreeEdge = { from: string; to: string; d: string };
export type Tree = { nodes: TreeNode[]; edges: TreeEdge[]; width: number; height: number };

/** Columns by dependency depth (no needs is column 0), rows in a stable order that keeps lines short. */
export function layoutTree(unlocks: FarmUnlock[]): Tree {
  const byName = new Map(unlocks.map((u) => [u.name, u]));
  const index = new Map(unlocks.map((u, i) => [u.name, i]));
  const depthOf = new Map<string, number>();
  const depth = (name: string, trail: string[] = []): number => {
    const known = depthOf.get(name);
    if (known !== undefined) return known;
    const u = byName.get(name);
    // A name we do not know, or a loop, counts for nothing rather than looping forever.
    if (!u || trail.includes(name)) return -1;
    const behind = u.needs.map((n) => depth(n, [...trail, name]));
    const d = behind.length ? Math.max(...behind) + 1 : 0;
    depthOf.set(name, d);
    return d;
  };
  const columns: FarmUnlock[][] = [];
  for (const u of unlocks) {
    const d = Math.max(0, depth(u.name));
    (columns[d] ??= []).push(u);
  }
  const rowOf = new Map<string, number>();
  const nodes: TreeNode[] = [];
  let tallest = 0;
  columns.forEach((col, c) => {
    if (!col) return;
    const keyed = col.map((u) => {
      const rows = u.needs.map((n) => rowOf.get(n)).filter((r): r is number => r !== undefined);
      const mean = rows.length ? rows.reduce((a, b) => a + b, 0) / rows.length : (index.get(u.name) ?? 0) / 1000;
      return { u, mean, i: index.get(u.name) ?? 0 };
    });
    keyed.sort((a, b) => a.mean - b.mean || a.i - b.i);
    keyed.forEach(({ u }, row) => {
      rowOf.set(u.name, row);
      nodes.push({
        u,
        depth: c,
        row,
        x: TREE_PAD + c * (CARD_W + COL_GAP),
        y: TREE_PAD + row * (CARD_H + ROW_GAP),
      });
    });
    tallest = Math.max(tallest, col.length);
  });
  const at = new Map(nodes.map((n) => [n.u.name, n]));
  const edges: TreeEdge[] = [];
  for (const n of nodes) {
    for (const need of n.u.needs) {
      const from = at.get(need);
      if (!from) continue;
      const x1 = from.x + CARD_W;
      const y1 = from.y + CARD_H / 2;
      const x2 = n.x;
      const y2 = n.y + CARD_H / 2;
      const dx = Math.max(24, (x2 - x1) / 2);
      edges.push({ from: need, to: n.u.name, d: `M${x1} ${y1} C${x1 + dx} ${y1} ${x2 - dx} ${y2} ${x2 - 3} ${y2}` });
    }
  }
  const cols = Math.max(1, columns.length);
  return {
    nodes,
    edges,
    width: TREE_PAD * 2 + cols * CARD_W + (cols - 1) * COL_GAP,
    height: TREE_PAD * 2 + Math.max(1, tallest) * CARD_H + Math.max(0, tallest - 1) * ROW_GAP,
  };
}

type Props = {
  unlocks: FarmUnlock[];
  items: Record<string, number>;
  onBuy: (name: string) => void;
};

export function ResearchTree({ unlocks, items, onBuy }: Props) {
  const tree = layoutTree(unlocks);
  const levels = new Map(unlocks.map((u) => [u.name, u.level]));
  const pan = useRef<{ x: number; y: number; left: number; top: number } | null>(null);

  const startPan = (e: PointerEvent<HTMLDivElement>) => {
    if (e.button !== 0 || (e.target as HTMLElement).closest("button, .fm-card")) return;
    const el = e.currentTarget;
    pan.current = { x: e.clientX, y: e.clientY, left: el.scrollLeft, top: el.scrollTop };
    try {
      el.setPointerCapture(e.pointerId);
    } catch {
      /* synthetic pointer */
    }
    el.classList.add("panning");
  };
  const movePan = (e: PointerEvent<HTMLDivElement>) => {
    const p = pan.current;
    if (!p) return;
    e.currentTarget.scrollLeft = p.left - (e.clientX - p.x);
    e.currentTarget.scrollTop = p.top - (e.clientY - p.y);
  };
  const endPan = (e: PointerEvent<HTMLDivElement>) => {
    pan.current = null;
    e.currentTarget.classList.remove("panning");
  };

  return (
    <div
      className="fm-tree"
      onPointerDown={startPan}
      onPointerMove={movePan}
      onPointerUp={endPan}
      onPointerCancel={endPan}
    >
      <div className="fm-tree-canvas" style={{ width: tree.width, height: tree.height }}>
        <svg className="fm-tree-lines" width={tree.width} height={tree.height} aria-hidden="true">
          <defs>
            <marker id="fm-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M0 0L8 4L0 8z" className="fm-arrow" />
            </marker>
            <marker id="fm-arrow-lit" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M0 0L8 4L0 8z" className="fm-arrow lit" />
            </marker>
          </defs>
          {tree.edges.map((edge) => {
            const lit = (levels.get(edge.from) ?? 0) > 0;
            return (
              <path
                key={`${edge.from}>${edge.to}`}
                d={edge.d}
                className={`fm-edge${lit ? " lit" : ""}`}
                markerEnd={`url(#${lit ? "fm-arrow-lit" : "fm-arrow"})`}
              />
            );
          })}
        </svg>
        {tree.nodes.map(({ u, x, y }) => {
          const maxed = u.cost === null;
          const verb = u.level > 0 && u.upgradable ? "Upgrade" : "Unlock";
          const state = u.missing
            ? "missing"
            : u.available && u.affordable && !maxed
              ? "ready"
              : u.available
                ? "open"
                : "locked";
          return (
            <div
              key={u.name}
              className={`fm-card ${state}${u.level > 0 ? " lit" : ""}${maxed ? " done" : ""}`}
              style={{ left: x, top: y, width: CARD_W, height: CARD_H }}
              data-unlock={u.name}
            >
              <div className="fm-card-head">
                <strong title={u.name.replace(/_/g, " ")}>{u.name.replace(/_/g, " ")}</strong>
                {u.upgradable || u.level > 0 ? (
                  <span className="fm-level">
                    {u.level}/{u.max}
                  </span>
                ) : null}
              </div>
              {u.missing ? (
                <div className="fm-card-note">not in Code Coach yet</div>
              ) : maxed ? (
                <div className="fm-card-note ok">{u.max > 1 ? "Fully upgraded" : "Unlocked"}</div>
              ) : (
                <div className="fm-costs" title={costText(u.cost)}>
                  {Object.entries(u.cost ?? {}).map(([item, n]) => {
                    const short = (items[item] ?? 0) < n;
                    return (
                      <span key={item} className={`fm-cost${short ? " short" : ""}`} title={`${itemName(item)}: you have ${(items[item] ?? 0).toLocaleString()}`}>
                        <ItemIcon item={item} size={14} />
                        {n.toLocaleString()}
                        <span className="fm-sr"> {itemName(item)}</span>
                      </span>
                    );
                  })}
                </div>
              )}
              <p className="fm-card-about" title={u.about}>
                {u.about}
              </p>
              <div className="fm-card-foot">
                {maxed || u.missing ? null : (
                  <button
                    type="button"
                    className="fm-btn primary"
                    disabled={!u.available || !u.affordable}
                    onClick={() => onBuy(u.name)}
                  >
                    {verb}
                  </button>
                )}
                {!u.available && !maxed && !u.missing ? (
                  <span className="fm-needs" title={`Needs ${u.needs.join(" and ")}`}>
                    needs {u.needs.map((n) => n.replace(/_/g, " ")).join(", ") || "nothing"}
                  </span>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
