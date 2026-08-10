import { useCallback, useEffect, useRef, useState } from "react";
import { visualizeCode } from "../api";
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

/** A binary tree laid out by depth. */
function asTree(startId: number, heap: Heap): { rows: (string | null)[][] } | null {
  const root = heap[String(startId)];
  if (!root || root.k !== "obj") return null;
  if (!("left" in root.fields) && !("right" in root.fields)) return null;
  const valueField = Object.keys(root.fields).find(
    (f) => f !== "left" && f !== "right",
  );

  const rows: (string | null)[][] = [];
  let level: (number | null)[] = [startId];
  const seen = new Set<number>();

  for (let depth = 0; depth < 5 && level.some((x) => x != null); depth++) {
    const texts: (string | null)[] = [];
    const next: (number | null)[] = [];
    for (const id of level) {
      const e = id == null ? null : heap[String(id)];
      if (!e || e.k !== "obj" || (id != null && seen.has(id))) {
        texts.push(null);
        next.push(null, null);
        continue;
      }
      if (id != null) seen.add(id);
      texts.push(valueField ? shortText(e.fields[valueField], heap) : "·");
      for (const side of ["left", "right"] as const) {
        const child = e.fields[side];
        next.push(child && isRef(child) ? child.id : null);
      }
    }
    rows.push(texts);
    if (texts.every((t) => t == null)) {
      rows.pop();
      break;
    }
    level = next;
  }
  return rows.length ? { rows } : null;
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
    const arrows = pointersInto(entry.items.length, vars);
    return (
      <div className="viz-array">
        <div className="viz-array-cells">
          {entry.items.map((item, i) => (
            <div key={i} className={`viz-cell${arrows[i] ? " pointed" : ""}`}>
              <span className="viz-cell-idx">{i}</span>
              <span className="viz-cell-val">{shortText(item, heap)}</span>
              {arrows[i] ? (
                <span className="viz-cell-ptr">
                  ▲<em>{arrows[i].join(" ")}</em>
                </span>
              ) : null}
            </div>
          ))}
          {entry.n > entry.items.length ? (
            <div className="viz-cell more">+{entry.n - entry.items.length}</div>
          ) : null}
          {entry.items.length === 0 ? <div className="viz-cell empty">empty</div> : null}
        </div>
      </div>
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
      return (
        <div className="viz-tree">
          {tree.rows.map((row, d) => (
            <div key={d} className="viz-tree-row">
              {row.map((cell, i) => (
                <span key={i} className={`viz-tree-node${cell == null ? " gap" : ""}`}>
                  {cell ?? ""}
                </span>
              ))}
            </div>
          ))}
        </div>
      );
    }

    const chain = asChain(value.id, heap);
    if (chain) {
      return (
        <div className="viz-chain">
          {chain.nodes.map((n, i) => (
            <span key={n.id} className="viz-chain-item">
              <span className="viz-node">{n.text}</span>
              {i < chain.nodes.length - 1 ? (
                <span className="viz-chain-arrow" aria-hidden>
                  →
                </span>
              ) : null}
            </span>
          ))}
          <span className="viz-chain-tail">{chain.cyclic ? "↺ loops" : "→ None"}</span>
        </div>
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

export function VizPanel({ getCode, patternId, problemNumber, resetKey }: Props) {
  const [data, setData] = useState<VisualizeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [i, setI] = useState(0);
  const [call, setCall] = useState("");
  const [playing, setPlaying] = useState(false);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    setData(null);
    setI(0);
    setCall("");
    setPlaying(false);
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
        setI(0);
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
    }, 550);
    return () => {
      if (timer.current) window.clearTimeout(timer.current);
    };
  }, [playing, i, last, steps.length]);

  const step = steps[Math.min(i, last)];

  return (
    <div className="viz-panel">
      <div className="viz-bar">
        <button
          type="button"
          className="study-btn"
          onClick={() => void run()}
          disabled={busy}
        >
          {busy ? "Running…" : data ? "Re-run" : "Visualise"}
        </button>

        {steps.length > 0 ? (
          <>
            <button
              type="button"
              className="viz-step-btn"
              onClick={() => {
                setPlaying(false);
                setI((n) => Math.max(0, n - 1));
              }}
              disabled={i <= 0}
              aria-label="Previous step"
            >
              ‹
            </button>
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
            <button
              type="button"
              className="viz-step-btn"
              onClick={() => {
                setPlaying(false);
                setI((n) => Math.min(last, n + 1));
              }}
              disabled={i >= last}
              aria-label="Next step"
            >
              ›
            </button>
            <button
              type="button"
              className={`study-btn${playing ? " on" : ""}`}
              onClick={() => setPlaying((p) => !p)}
              disabled={i >= last && !playing}
            >
              {playing ? "Pause" : "Play"}
            </button>
            <span className="viz-count">
              step {Math.min(i, last) + 1}/{steps.length}
              {step ? ` · line ${step.line}` : ""}
            </span>
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
            in <code>{step.func === "&lt;module&gt;" ? "module" : step.func}</code> ·
            line {step.line}
          </div>
          {Object.keys(step.vars).length === 0 ? (
            <p className="viz-empty">no variables yet</p>
          ) : (
            Object.entries(step.vars).map(([name, value]) => (
              <div key={name} className="viz-var">
                <span className="viz-var-name">{name}</span>
                <div className="viz-var-value">
                  <Value value={value} heap={step.heap} vars={step.vars} name={name} />
                </div>
              </div>
            ))
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
