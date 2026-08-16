import { useCallback, useEffect, useRef, useState } from "react";
import { visualizeCode } from "../api";
import {
  ArrayDiagram,
  GridDiagram,
  ListDiagram,
  StackDiagram,
  TreeDiagram,
  heapToTree,
  type TreeNode,
} from "./VizDiagrams";
import type {
  VisualizeResult,
  VizHeapEntry,
  VizStep,
  VizValue,
} from "../types";

type Props = {
  getCode: () => string;
  patternId: string | null;
  problemNumber: number | null;
  /** Reset the trace when the exercise changes. */
  resetKey: string;
};

type Heap = Record<string, VizHeapEntry>;

function isRef(v: VizValue): v is { k: "ref"; id: number } {
  return v.k === "ref";
}

function primText(v: Extract<VizValue, { k: "prim" }>): string {
  if (v.t === "none") return "None";
  if (v.t === "bool") return v.v ? "True" : "False";
  if (v.t === "str") return `"${String(v.v)}${v.clipped ? "…" : ""}"`;
  return String(v.v);
}

/** One-line form, for cells and table entries. */
function shortText(v: VizValue, heap: Heap, depth = 0): string {
  if (v.k === "prim") return primText(v);
  const e = heap[String(v.id)];
  if (!e) return "·";
  if (depth > 1) return e.k === "obj" ? `${e.cls}(…)` : "…";
  switch (e.k) {
    case "list": {
      const inner = e.items.map((x) => shortText(x, heap, depth + 1)).join(", ");
      return e.tuple ? `(${inner})` : `[${inner}]`;
    }
    case "set":
      return `{${e.items.map((x) => shortText(x, heap, depth + 1)).join(", ")}}`;
    case "dict":
      return `{${e.pairs
        .map(([k, val]) => `${shortText(k, heap, depth + 1)}: ${shortText(val, heap, depth + 1)}`)
        .join(", ")}}`;
    case "obj":
      return `${e.cls}(…)`;
    default:
      return e.v;
  }
}

/**
 * A chain of objects linked by one field — a linked list, or a stack of
 * `next` pointers. Returns null when it isn't one, so trees and plain objects
 * fall through to the generic renderer.
 */
function asChain(
  startId: number,
  heap: Heap,
): { label: string; nodes: { id: number; text: string }[]; cyclic: boolean } | null {
  const first = heap[String(startId)];
  if (!first || first.k !== "obj") return null;
  const linkField = ["next", "nxt"].find((f) => f in first.fields);
  if (!linkField) return null;
  const valueField = Object.keys(first.fields).find((f) => f !== linkField);

  const nodes: { id: number; text: string }[] = [];
  const seen = new Set<number>();
  let cursor: number | null = startId;
  let cyclic = false;

  while (cursor != null && nodes.length < 24) {
    if (seen.has(cursor)) {
      cyclic = true;
      break;
    }
    seen.add(cursor);
    // Annotated: without it TS can't break the cycle between `cursor` and the
    // heap lookup that reassigns it.
    const entry: VizHeapEntry | undefined = heap[String(cursor)];
    if (!entry || entry.k !== "obj") break;
    nodes.push({
      id: cursor,
      text: valueField ? shortText(entry.fields[valueField], heap) : "·",
    });
    const link: VizValue | undefined = entry.fields[linkField];
    cursor = link && isRef(link) ? link.id : null;
  }
  return { label: first.cls, nodes, cyclic };
}

/**
 * Lay a binary tree out for drawing.
 *
 * x comes from an in-order walk (each node takes the next free slot), which is
 * the standard trick for a tree drawing where siblings never overlap and the
 * parent sits between its children.
 */
function asTree(startId: number, heap: Heap): TreeNode[] | null {
  const root = heap[String(startId)];
  if (!root || root.k !== "obj") return null;
  if (!("left" in root.fields) && !("right" in root.fields)) return null;
  const valueField = Object.keys(root.fields).find(
    (f) => f !== "left" && f !== "right",
  );

  const out: TreeNode[] = [];
  const seen = new Set<number>();
  let slot = 0;

  const walk = (id: number, depth: number, parent: number | null): void => {
    if (depth > 4 || seen.has(id) || out.length > 40) return;
    const e = heap[String(id)];
    if (!e || e.k !== "obj") return;
    seen.add(id);

    const leftRef = e.fields["left"];
    if (leftRef && isRef(leftRef)) walk(leftRef.id, depth + 1, id);

    const mySlot = slot++;
    out.push({
      id,
      text: valueField ? shortText(e.fields[valueField], heap) : "·",
      depth,
      slot: mySlot,
      parent,
    });

    const rightRef = e.fields["right"];
    if (rightRef && isRef(rightRef)) walk(rightRef.id, depth + 1, id);
  };

  walk(startId, 0, null);
  return out.length ? out : null;
}

/** Variable names pointing at each heap object, for labelling nodes. */
function refLabels(vars: Record<string, VizValue>): Record<number, string[]> {
  const out: Record<number, string[]> = {};
  for (const [name, v] of Object.entries(vars)) {
    if (v.k !== "ref") continue;
    (out[v.id] ||= []).push(name);
  }
  return out;
}

/**
 * Names that conventionally hold a *position* in a sequence.
 *
 * Deliberately a list rather than "any int that happens to be in range":
 * in `two_sum([2,7,11,15], 9)` the element `n = 2` and the complement
 * `need = 7` are both valid indices by coincidence, and drawing arrows for
 * them points at cells that mean nothing.
 */
const INDEX_NAMES = new Set([
  "i", "j", "k", "l", "r", "p", "q",
  "left", "right", "lo", "hi", "low", "high", "mid",
  "start", "end", "begin", "first", "last",
  "slow", "fast", "idx", "index", "pos", "cur", "curr", "current",
  "head", "tail", "write", "read", "pivot", "anchor",
]);

function looksLikeIndex(name: string): boolean {
  const n = name.toLowerCase();
  return (
    INDEX_NAMES.has(n) ||
    n.endsWith("_i") ||
    n.endsWith("idx") ||
    n.endsWith("index") ||
    n.endsWith("_ptr")
  );
}

/** Index-ish variables currently sitting on a valid index of this list. */
function pointersInto(
  length: number,
  vars: Record<string, VizValue>,
): Record<number, string[]> {
  const out: Record<number, string[]> = {};
  for (const [name, v] of Object.entries(vars)) {
    if (v.k !== "prim" || v.t !== "int") continue;
    if (!looksLikeIndex(name)) continue;
    const idx = v.v as number;
    if (idx < 0 || idx >= length) continue;
    (out[idx] ||= []).push(name);
  }
  return out;
}

/**
 * Pairs that conventionally bracket a span. When both are in scope the region
 * between them IS the answer being built — the sliding window, the binary
 * search range, the two-pointer squeeze — so it gets shaded.
 */
const SPAN_PAIRS: [string, string][] = [
  ["left", "right"],
  ["lo", "hi"],
  ["low", "high"],
  ["start", "end"],
  ["l", "r"],
  ["i", "j"],
  ["slow", "fast"],
  ["begin", "end"],
];

function windowFor(
  length: number,
  vars: Record<string, VizValue>,
): { from: number; to: number; label: string } | null {
  const intOf = (name: string): number | null => {
    const v = vars[name];
    return v && v.k === "prim" && v.t === "int" ? (v.v as number) : null;
  };
  for (const [a, b] of SPAN_PAIRS) {
    const x = intOf(a);
    const y = intOf(b);
    if (x == null || y == null) continue;
    const from = Math.max(0, Math.min(x, y));
    const to = Math.min(length - 1, Math.max(x, y));
    if (to < from) continue;
    return { from, to, label: `${a}…${b} (${to - from + 1})` };
  }
  return null;
}

/** A list whose every item is itself a list — a matrix, not a nested mess. */
function asGrid(entry: VizHeapEntry, heap: Heap): string[][] | null {
  if (entry.k !== "list" || entry.items.length === 0) return null;
  const rows: string[][] = [];
  for (const item of entry.items) {
    if (!isRef(item)) return null;
    const row = heap[String(item.id)];
    if (!row || row.k !== "list") return null;
    rows.push(row.items.map((c) => shortText(c, heap)));
  }
  // A single row reads better as a plain array.
  return rows.length > 1 ? rows : null;
}

/**
 * A Python list is a list — nothing in the data says "this one is a stack" or
 * "this one is a heap". The name does, and by convention it's reliable:
 * heapq operates on a plain list you've called `heap`, and stack problems
 * call theirs `stack`. Getting it right changes the shape drawn, so it's
 * name-based on purpose rather than guessed from contents.
 */
function roleOf(name: string): "stack" | "heap" | null {
  const n = name.toLowerCase();
  if (/(^|_)(stack|stk|st)$/.test(n) || n.endsWith("stack")) return "stack";
  if (/(^|_)(heap|pq)$/.test(n) || n.endsWith("heap")) return "heap";
  return null;
}

/** Row/col-ish variables, for highlighting a cell in a grid. */
function gridMark(
  rows: string[][],
  vars: Record<string, VizValue>,
): [number, number] | null {
  const intOf = (names: string[]): number | null => {
    for (const n of names) {
      const v = vars[n];
      if (v && v.k === "prim" && v.t === "int") return v.v as number;
    }
    return null;
  };
  const r = intOf(["r", "row", "i"]);
  const c = intOf(["c", "col", "j"]);
  if (r == null || c == null) return null;
  if (r < 0 || r >= rows.length) return null;
  if (c < 0 || c >= (rows[r]?.length ?? 0)) return null;
  return [r, c];
}

function Value({
  value,
  heap,
  vars,
  name,
}: {
  value: VizValue;
  heap: Heap;
  vars: Record<string, VizValue>;
  name: string;
}) {
  if (value.k === "prim") {
    return <span className={`viz-prim viz-${value.t}`}>{primText(value)}</span>;
  }
  const entry = heap[String(value.id)];
  if (!entry) return <span className="viz-prim">·</span>;

  if (entry.k === "list") {
    const items = entry.items.map((item) => shortText(item, heap));
    const role = roleOf(name);
    if (role === "stack") return <StackDiagram items={items} />;
    if (role === "heap" && items.length > 0) {
      return <TreeDiagram nodes={heapToTree(items)} pointers={{}} />;
    }
    const grid = asGrid(entry, heap);
    if (grid) {
      return <GridDiagram rows={grid} mark={gridMark(grid, vars)} />;
    }
    return (
      <ArrayDiagram
        items={items}
        pointers={pointersInto(entry.items.length, vars)}
        extra={entry.n - entry.items.length}
        window={windowFor(entry.items.length, vars)}
      />
    );
  }

  if (entry.k === "dict") {
    if (entry.pairs.length === 0) return <span className="viz-empty">empty dict</span>;
    return (
      <div className="viz-map">
        {entry.pairs.map(([k, v], i) => (
          <div key={i} className="viz-map-row">
            <span className="viz-map-key">{shortText(k, heap)}</span>
            <span className="viz-map-arrow" aria-hidden>
              →
            </span>
            <span className="viz-map-val">{shortText(v, heap)}</span>
          </div>
        ))}
      </div>
    );
  }

  if (entry.k === "set") {
    if (entry.items.length === 0) return <span className="viz-empty">empty set</span>;
    return (
      <div className="viz-chips">
        {entry.items.map((item, i) => (
          <span key={i} className="viz-chip">
            {shortText(item, heap)}
          </span>
        ))}
      </div>
    );
  }

  if (entry.k === "obj") {
    const tree = asTree(value.id, heap);
    if (tree) {
      return <TreeDiagram nodes={tree} pointers={refLabels(vars)} />;
    }

    const chain = asChain(value.id, heap);
    if (chain) {
      return (
        <ListDiagram
          nodes={chain.nodes}
          cyclic={chain.cyclic}
          pointers={refLabels(vars)}
          doubly={"prev" in entry.fields}
        />
      );
    }

    return (
      <div className="viz-map">
        {Object.entries(entry.fields).map(([f, v]) => (
          <div key={f} className="viz-map-row">
            <span className="viz-map-key">{f}</span>
            <span className="viz-map-arrow" aria-hidden>
              →
            </span>
            <span className="viz-map-val">{shortText(v, heap)}</span>
          </div>
        ))}
      </div>
    );
  }

  void name;
  return <span className="viz-prim">{entry.v}</span>;
}

/**
 * Where to land when a trace comes back.
 *
 * Step 1 is almost always `def two_sum(...)` at module scope with nothing
 * defined yet — an empty picture, which reads as "this feature is broken".
 * Skip to the first step that has data worth looking at: inside a function,
 * with a container in scope if there is one.
 */
function firstInterestingStep(steps: VizStep[]): number {
  const hasContainer = (s: VizStep) =>
    Object.values(s.vars).some((v) => v.k === "ref");
  const hasPointer = (s: VizStep) =>
    Object.entries(s.vars).some(
      ([name, v]) => v.k === "prim" && v.t === "int" && looksLikeIndex(name),
    );
  // `__init__` is where nodes get built, not where the algorithm happens —
  // and mid-construction a node's `next` isn't wired yet, so there's nothing
  // to draw. Land in the student's own function instead.
  const isAlgorithm = (s: VizStep) =>
    s.func !== "<module>" && !s.func.startsWith("__");

  // Best: a container AND something pointing into it — the picture that
  // actually explains the algorithm.
  const withPointer = steps.findIndex(
    (s) => isAlgorithm(s) && hasContainer(s) && hasPointer(s),
  );
  if (withPointer >= 0) return withPointer;

  // Next best: inside the algorithm with a structure in scope.
  const inFn = steps.findIndex((s) => isAlgorithm(s) && hasContainer(s));
  if (inFn >= 0) return inFn;

  const anyFn = steps.findIndex(
    (s) => isAlgorithm(s) && Object.keys(s.vars).length > 0,
  );
  if (anyFn >= 0) return anyFn;

  const anyVars = steps.findIndex((s) => hasContainer(s));
  if (anyVars >= 0) return anyVars;

  return 0;
}

/**
 * A plain-English line under each picture saying what it shows.
 *
 * A diagram is only obvious once you already know the structure — which is
 * exactly what someone learning these patterns doesn't yet. The caption names
 * the shape and points at the thing that's moving.
 */
function captionFor(
  name: string,
  value: VizValue,
  heap: Heap,
  vars: Record<string, VizValue>,
): string | null {
  if (value.k !== "ref") return null;
  const entry = heap[String(value.id)];
  if (!entry) return null;

  if (entry.k === "list") {
    const role = roleOf(name);
    if (role === "stack") {
      const top = entry.items.length
        ? shortText(entry.items[entry.items.length - 1], heap)
        : null;
      return top
        ? `Stack of ${entry.n} — push and pop happen at the top, currently ${top}.`
        : "Stack is empty — nothing to pop.";
    }
    if (role === "heap") {
      const root = entry.items.length ? shortText(entry.items[0], heap) : null;
      return root
        ? `Heap of ${entry.n}, drawn as a tree. The smallest, ${root}, sits at the root — that's what pops next.`
        : "Heap is empty.";
    }
    const grid = asGrid(entry, heap);
    if (grid) {
      const mark = gridMark(grid, vars);
      return `${grid.length}×${grid[0]?.length ?? 0} grid${
        mark ? `, currently at row ${mark[0]}, column ${mark[1]}` : ""
      }.`;
    }
    const win = windowFor(entry.items.length, vars);
    if (win) {
      return `${entry.n} items. The shaded stretch is the current window — ${
        win.to - win.from + 1
      } wide, from index ${win.from} to ${win.to}.`;
    }
    const ptrs = pointersInto(entry.items.length, vars);
    const names = Object.entries(ptrs).map(([i, ns]) => `${ns.join("/")} at ${i}`);
    return names.length
      ? `${entry.n} items, indexed from 0. ${names.join(", ")}.`
      : `${entry.n} items, indexed from 0.`;
  }

  if (entry.k === "dict") {
    return entry.n === 0
      ? "Empty so far — nothing has been recorded yet."
      : `${entry.n} key${entry.n === 1 ? "" : "s"}, each remembering what you saw and where.`;
  }

  if (entry.k === "set") {
    return entry.n === 0
      ? "Empty set — nothing added yet."
      : `${entry.n} value${entry.n === 1 ? "" : "s"}, kept only to answer "have I seen this?".`;
  }

  if (entry.k === "obj") {
    const tree = asTree(value.id, heap);
    if (tree) {
      const depth = Math.max(...tree.map((n) => n.depth)) + 1;
      return `Binary tree, ${tree.length} node${
        tree.length === 1 ? "" : "s"
      }, ${depth} level${depth === 1 ? "" : "s"} deep. Lines run parent to child.`;
    }
    const chain = asChain(value.id, heap);
    if (chain) {
      const doubly = "prev" in entry.fields;
      if (chain.cyclic) {
        return `Linked list that loops — the last node points back instead of ending, so walking it never stops.`;
      }
      return `Linked list of ${chain.nodes.length}. Each box is [value | next]${
        doubly ? ", with dashed arrows underneath for the backward links" : ""
      }, and ∅ marks the end.`;
    }
  }
  return null;
}

/**
 * Decide what each variable should draw.
 *
 * Several variables usually walk the same list — `head`, `cur`, `prev`, `nxt`.
 * Drawing a separate diagram per variable produces four pictures of the same
 * chain. The longest chain is drawn once (its nodes already carry every
 * pointer's label), and the others just say which node they're on.
 */
function visibleVars(step: VizStep): {
  name: string;
  value: VizValue;
  insideChain: string | null;
}[] {
  const chains = new Map<number, { len: number; ids: Set<number> }>();
  for (const value of Object.values(step.vars)) {
    if (value.k !== "ref" || chains.has(value.id)) continue;
    const chain = asChain(value.id, step.heap);
    if (chain && chain.nodes.length > 1) {
      chains.set(value.id, {
        len: chain.nodes.length,
        ids: new Set(chain.nodes.map((n) => n.id)),
      });
    }
  }
  // Longest first, so the fullest picture is the one that gets drawn.
  const ranked = [...chains.entries()].sort((a, b) => b[1].len - a[1].len);
  const covered = new Map<number, string>(); // node id → position in its chain
  const drawnRoots = new Set<number>();
  for (const [rootId, info] of ranked) {
    if (covered.has(rootId)) continue;
    drawnRoots.add(rootId);
    let pos = 1;
    for (const id of info.ids) {
      if (!covered.has(id)) covered.set(id, String(pos));
      pos++;
    }
  }

  // Two variables can name the same list (`head` and `node` both at the top of
  // it). Only the first draws; the rest say so.
  const drawnBy = new Map<number, string>();

  return Object.entries(step.vars).map(([name, value]) => {
    if (value.k !== "ref") return { name, value, insideChain: null };

    if (drawnRoots.has(value.id)) {
      const already = drawnBy.get(value.id);
      if (already) return { name, value, insideChain: "1" };
      drawnBy.set(value.id, name);
      return { name, value, insideChain: null };
    }

    const inside = covered.get(value.id) ?? null;
    return { name, value, insideChain: inside };
  });
}

/**
 * Play speeds, in milliseconds per step. The default is deliberately slower
 * than reading pace — the point is to follow what changed, not to watch it
 * flick past.
 */
const SPEEDS = [
  { ms: 1600, label: "Slowest" },
  { ms: 1000, label: "Slow" },
  { ms: 600, label: "Medium" },
  { ms: 300, label: "Fast" },
];
const SPEED_KEY = "code-coach:viz-speed";

function loadSpeed(): number {
  try {
    const raw = Number(localStorage.getItem(SPEED_KEY));
    if (SPEEDS.some((s) => s.ms === raw)) return raw;
  } catch {
    /* ignore */
  }
  return 1000;
}

export function VizPanel({ getCode, patternId, problemNumber, resetKey }: Props) {
  const [data, setData] = useState<VisualizeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [i, setI] = useState(0);
  const [call, setCall] = useState("");
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(loadSpeed);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    setData(null);
    setI(0);
    setCall("");
    setPlaying(false);
  }, [resetKey]);

  // Opening the panel IS the request to see it — don't make them press a
  // second button. Runs once per exercise; "Re-run" handles edits after that.
  const autoRan = useRef<string | null>(null);
  useEffect(() => {
    if (autoRan.current === resetKey) return;
    autoRan.current = resetKey;
    void run();
    // `run` is intentionally omitted: it changes identity whenever `call` or
    // `busy` does, which would re-fire this on every run.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetKey]);

  const run = useCallback(
    async (withCall?: string) => {
      if (busy) return;
      setBusy(true);
      setPlaying(false);
      try {
        const res = await visualizeCode({
          code: getCode(),
          call: withCall ?? call,
          pattern_id: patternId,
          problem_number: problemNumber,
        });
        setData(res);
        setCall(res.call);
        setI(firstInterestingStep(res.steps));
      } catch {
        setData({
          ok: false,
          steps: [],
          truncated: false,
          stdout: "",
          stderr: "",
          error: "Couldn’t reach the coach — is the API running?",
          call: "",
        });
      } finally {
        setBusy(false);
      }
    },
    [busy, call, getCode, patternId, problemNumber],
  );

  const steps: VizStep[] = data?.steps ?? [];
  const last = Math.max(0, steps.length - 1);

  // Auto-play walks the trace; stop at the end rather than looping.
  useEffect(() => {
    if (!playing || steps.length === 0) return;
    timer.current = window.setTimeout(() => {
      setI((n) => {
        if (n >= last) {
          setPlaying(false);
          return n;
        }
        return n + 1;
      });
    }, speed);
    return () => {
      if (timer.current) window.clearTimeout(timer.current);
    };
  }, [playing, i, last, steps.length, speed]);

  const step = steps[Math.min(i, last)];

  return (
    <div className="viz-panel">
      <div className="viz-bar">
        <button
          type="button"
          className="study-btn"
          onClick={() => void run()}
          disabled={busy}
          title="Re-run after editing your code"
        >
          {busy ? "Running…" : "Re-run"}
        </button>

        {steps.length > 0 ? (
          <>
            {/* Stepping one frame at a time is the main way to use this, so
                these are real buttons, not decorations beside the slider. */}
            <div className="viz-steps" role="group" aria-label="Step through">
              <button
                type="button"
                className="viz-step-btn"
                onClick={() => {
                  setPlaying(false);
                  setI((n) => Math.max(0, n - 1));
                }}
                disabled={i <= 0}
                title="Previous step"
              >
                ‹ Back
              </button>
              <button
                type="button"
                className="viz-step-btn"
                onClick={() => {
                  setPlaying(false);
                  setI((n) => Math.min(last, n + 1));
                }}
                disabled={i >= last}
                title="Next step"
              >
                Next ›
              </button>
            </div>

            <button
              type="button"
              className={`study-btn${playing ? " on" : ""}`}
              onClick={() => setPlaying((p) => !p)}
              disabled={i >= last && !playing}
            >
              {playing ? "❚❚ Pause" : "▶ Play"}
            </button>

            <select
              className="viz-speed"
              value={speed}
              onChange={(e) => {
                const ms = Number(e.target.value);
                setSpeed(ms);
                try {
                  localStorage.setItem(SPEED_KEY, String(ms));
                } catch {
                  /* ignore */
                }
              }}
              aria-label="Play speed"
              title="How long each step is held while playing"
            >
              {SPEEDS.map((s) => (
                <option key={s.ms} value={s.ms}>
                  {s.label}
                </option>
              ))}
            </select>

            <span className="viz-count">
              step {Math.min(i, last) + 1}/{steps.length}
              {step ? ` · line ${step.line}` : ""}
            </span>

            <input
              className="viz-slider"
              type="range"
              min={0}
              max={last}
              value={Math.min(i, last)}
              onChange={(e) => {
                setPlaying(false);
                setI(Number(e.target.value));
              }}
              aria-label="Execution step"
            />
          </>
        ) : null}
      </div>

      {/* The call is editable: the auto-guess is only as good as the example. */}
      {data ? (
        <div className="viz-call">
          <span className="viz-call-label">Ran</span>
          <input
            className="viz-call-input"
            value={call}
            placeholder="e.g. two_sum([2, 7, 11, 15], 9)"
            onChange={(e) => setCall(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") void run(call);
            }}
          />
          <button
            type="button"
            className="study-btn"
            onClick={() => void run(call)}
            disabled={busy}
          >
            Go
          </button>
        </div>
      ) : null}

      {data && !data.ok ? (
        <p className="viz-error">{data.error}</p>
      ) : null}

      {data?.ok && steps.length === 0 ? (
        <p className="viz-error">
          Nothing ran. Your code defines a function but never calls it — put a
          call in the box above.
        </p>
      ) : null}

      {step ? (
        <div className="viz-body">
          <div className="viz-scope">
            in{" "}
            <code>
              {step.func === "<module>" ? "your program" : `${step.func}()`}
            </code>{" "}
            · line {step.line}
            {step.returned ? " · finished" : ""}
          </div>

          {/* The payoff frame: what the function actually handed back. */}
          {step.returned ? (
            <div className="viz-returned">
              <span className="viz-returned-label">returns</span>
              <Value
                value={step.returned}
                heap={step.heap}
                vars={step.vars}
                name="__returned__"
              />
            </div>
          ) : null}
          {Object.keys(step.vars).length === 0 ? (
            <p className="viz-empty">no variables yet</p>
          ) : (
            visibleVars(step).map(({ name, value, insideChain }) =>
              insideChain ? (
                // Already drawn as a labelled node in the list above — saying
                // "cur: [3] → ∅" underneath just repeats it.
                <div key={name} className="viz-var">
                  <span className="viz-var-name">{name}</span>
                  <div className="viz-var-value">
                    <span className="viz-inline-note">
                      → node <strong>{insideChain}</strong> in the list above
                    </span>
                  </div>
                </div>
              ) : (
                <div key={name} className="viz-var">
                  <span className="viz-var-name">{name}</span>
                  <div className="viz-var-value">
                    <Value
                      value={value}
                      heap={step.heap}
                      vars={step.vars}
                      name={name}
                    />
                    {(() => {
                      const cap = captionFor(name, value, step.heap, step.vars);
                      return cap ? (
                        <p className="viz-caption">{cap}</p>
                      ) : null;
                    })()}
                  </div>
                </div>
              ),
            )
          )}
          {data?.truncated ? (
            <p className="viz-note">Trace stopped at {steps.length} steps.</p>
          ) : null}
          {data?.stdout ? <pre className="viz-stdout">{data.stdout}</pre> : null}
          {data?.error ? <pre className="viz-error-trace">{data.error}</pre> : null}
        </div>
      ) : null}
    </div>
  );
}
