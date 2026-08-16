/**
 * Drawn diagrams for the visualiser — SVG, not CSS boxes with "→" characters.
 *
 * The shapes follow the way these structures are conventionally drawn in
 * teaching material: an array as a strip of cells with the index underneath
 * and labelled arrows pointing down at the current position; a linked list as
 * split [data|next] boxes joined by curved arrows and terminated with ∅; a
 * binary tree as circles joined by edges, laid out so siblings never collide.
 */

export type ChainNode = { id: number; text: string };
export type TreeNode = {
  id: number;
  text: string;
  depth: number;
  slot: number;
  parent: number | null;
};

/** One shared arrowhead definition per diagram. */
function ArrowHead({ id }: { id: string }) {
  return (
    <defs>
      <marker
        id={id}
        viewBox="0 0 10 10"
        refX="9"
        refY="5"
        markerWidth="6"
        markerHeight="6"
        orient="auto-start-reverse"
      >
        <path d="M 0 0 L 10 5 L 0 10 z" className="vd-arrowfill" />
      </marker>
    </defs>
  );
}

/* ── Array ──────────────────────────────────────────────── */

const CELL_W = 46;
const CELL_H = 34;
const CELL_GAP = 3;
const PTR_BAND = 30; // room above the cells for pointer labels
const IDX_BAND = 16; // room below for indices

export type Window = { from: number; to: number; label: string };

export function ArrayDiagram({
  items,
  pointers,
  extra,
  window: win,
}: {
  items: string[];
  /** index → variable names sitting on it */
  pointers: Record<number, string[]>;
  /** count of items not drawn */
  extra: number;
  /** A shaded span between two pointers — the sliding window itself. */
  window?: Window | null;
}) {
  const n = items.length + (extra > 0 ? 1 : 0);
  const width = Math.max(1, n) * (CELL_W + CELL_GAP);
  const height = PTR_BAND + CELL_H + IDX_BAND;
  const uid = "vd-arr";

  if (items.length === 0 && extra === 0) {
    return <span className="vd-empty">empty list</span>;
  }

  return (
    <svg
      className="vd"
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="array contents"
    >
      <ArrowHead id={uid} />

      {/* The window goes behind the cells so their borders stay crisp. */}
      {win ? (
        <g>
          <rect
            x={win.from * (CELL_W + CELL_GAP) - 2}
            y={PTR_BAND - 4}
            width={(win.to - win.from + 1) * (CELL_W + CELL_GAP) - CELL_GAP + 4}
            height={CELL_H + 8}
            rx={5}
            className="vd-window"
          />
          <text
            x={
              win.from * (CELL_W + CELL_GAP) +
              ((win.to - win.from + 1) * (CELL_W + CELL_GAP) - CELL_GAP) / 2
            }
            y={PTR_BAND + CELL_H + IDX_BAND - 1}
            className="vd-window-label"
            textAnchor="middle"
          >
            {win.label}
          </text>
        </g>
      ) : null}

      {items.map((text, i) => {
        const x = i * (CELL_W + CELL_GAP);
        const names = pointers[i];
        return (
          <g key={i}>
            <rect
              x={x}
              y={PTR_BAND}
              width={CELL_W}
              height={CELL_H}
              rx={4}
              className={`vd-cell${names ? " on" : ""}`}
            />
            <text
              x={x + CELL_W / 2}
              y={PTR_BAND + CELL_H / 2 + 4}
              className="vd-val"
              textAnchor="middle"
            >
              {text}
            </text>
            <text
              x={x + CELL_W / 2}
              y={PTR_BAND + CELL_H + 12}
              className="vd-idx"
              textAnchor="middle"
            >
              {i}
            </text>
            {names ? (
              <>
                <line
                  x1={x + CELL_W / 2}
                  y1={PTR_BAND - 17}
                  x2={x + CELL_W / 2}
                  y2={PTR_BAND - 3}
                  className="vd-ptr-line"
                  markerEnd={`url(#${uid})`}
                />
                <text
                  x={x + CELL_W / 2}
                  y={PTR_BAND - 21}
                  className="vd-ptr-name"
                  textAnchor="middle"
                >
                  {names.join(", ")}
                </text>
              </>
            ) : null}
          </g>
        );
      })}
      {extra > 0 ? (
        <g>
          <rect
            x={items.length * (CELL_W + CELL_GAP)}
            y={PTR_BAND}
            width={CELL_W}
            height={CELL_H}
            rx={4}
            className="vd-cell more"
          />
          <text
            x={items.length * (CELL_W + CELL_GAP) + CELL_W / 2}
            y={PTR_BAND + CELL_H / 2 + 4}
            className="vd-idx"
            textAnchor="middle"
          >
            +{extra}
          </text>
        </g>
      ) : null}
    </svg>
  );
}

/* ── Stack ──────────────────────────────────────────────── */

const S_W = 74;
const S_H = 26;
const S_GAP = 3;

/**
 * A list used as a stack, drawn the way stacks are always drawn: vertically,
 * newest on top. Same data as the array view, but the shape carries the
 * meaning — push and pop both happen at the end of the list.
 */
export function StackDiagram({ items }: { items: string[] }) {
  if (items.length === 0) {
    return <span className="vd-empty">empty stack</span>;
  }
  // Last element is the top, so draw the list reversed.
  const rows = [...items].reverse();
  const width = S_W + 76;
  const height = rows.length * (S_H + S_GAP) + 16;
  const uid = "vd-stack";

  return (
    <svg
      className="vd"
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="stack"
    >
      <ArrowHead id={uid} />
      {rows.map((text, r) => {
        const y = r * (S_H + S_GAP) + 8;
        const isTop = r === 0;
        const realIndex = items.length - 1 - r;
        return (
          <g key={r}>
            <rect
              x={40}
              y={y}
              width={S_W}
              height={S_H}
              rx={3}
              className={`vd-cell${isTop ? " on" : ""}`}
            />
            <text
              x={40 + S_W / 2}
              y={y + S_H / 2 + 4}
              className="vd-val"
              textAnchor="middle"
            >
              {text}
            </text>
            <text x={32} y={y + S_H / 2 + 4} className="vd-idx" textAnchor="end">
              {realIndex}
            </text>
            {isTop ? (
              <>
                <text
                  x={40 + S_W + 26}
                  y={y + S_H / 2 - 3}
                  className="vd-ptr-name"
                  textAnchor="middle"
                >
                  top
                </text>
                <line
                  x1={40 + S_W + 24}
                  y1={y + S_H / 2 + 2}
                  x2={40 + S_W + 4}
                  y2={y + S_H / 2 + 2}
                  className="vd-ptr-line"
                  markerEnd={`url(#${uid})`}
                />
              </>
            ) : null}
          </g>
        );
      })}
    </svg>
  );
}

/**
 * Turn a heapq array into tree nodes: children of i live at 2i+1 and 2i+2.
 * Slots come from an in-order walk so the drawing doesn't overlap.
 */
export function heapToTree(items: string[]): TreeNode[] {
  const out: TreeNode[] = [];
  let slot = 0;
  const walk = (i: number, depth: number, parent: number | null) => {
    if (i >= items.length || depth > 4) return;
    walk(2 * i + 1, depth + 1, i);
    out.push({ id: i, text: items[i], depth, slot: slot++, parent });
    walk(2 * i + 2, depth + 1, i);
  };
  walk(0, 0, null);
  return out;
}

/* ── 2D grid / matrix ───────────────────────────────────── */

const G_CELL = 30;
const G_GAP = 2;
const G_LABEL = 16;

/**
 * A list of lists, drawn as a grid rather than nested rows of boxes — that's
 * how matrix and island problems are always drawn, and the shape is the point.
 */
export function GridDiagram({
  rows,
  mark,
}: {
  rows: string[][];
  /** [row, col] to highlight, when the code has row/col-ish variables */
  mark?: [number, number] | null;
}) {
  const cols = Math.max(...rows.map((r) => r.length));
  const width = G_LABEL + cols * (G_CELL + G_GAP);
  const height = G_LABEL + rows.length * (G_CELL + G_GAP);

  return (
    <svg
      className="vd"
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="grid"
    >
      {Array.from({ length: cols }, (_, c) => (
        <text
          key={`c${c}`}
          x={G_LABEL + c * (G_CELL + G_GAP) + G_CELL / 2}
          y={11}
          className="vd-idx"
          textAnchor="middle"
        >
          {c}
        </text>
      ))}
      {rows.map((row, r) => (
        <g key={r}>
          <text
            x={G_LABEL - 5}
            y={G_LABEL + r * (G_CELL + G_GAP) + G_CELL / 2 + 4}
            className="vd-idx"
            textAnchor="end"
          >
            {r}
          </text>
          {row.map((text, c) => {
            const on = mark && mark[0] === r && mark[1] === c;
            return (
              <g key={c}>
                <rect
                  x={G_LABEL + c * (G_CELL + G_GAP)}
                  y={G_LABEL + r * (G_CELL + G_GAP)}
                  width={G_CELL}
                  height={G_CELL}
                  rx={3}
                  className={`vd-cell${on ? " on" : ""}`}
                />
                <text
                  x={G_LABEL + c * (G_CELL + G_GAP) + G_CELL / 2}
                  y={G_LABEL + r * (G_CELL + G_GAP) + G_CELL / 2 + 4}
                  className="vd-val"
                  textAnchor="middle"
                >
                  {text}
                </text>
              </g>
            );
          })}
        </g>
      ))}
    </svg>
  );
}

/* ── Linked list ────────────────────────────────────────── */

const N_VAL_W = 40;
const N_NEXT_W = 26;
const N_W = N_VAL_W + N_NEXT_W;
const N_H = 34;
const N_GAP = 32;

export function ListDiagram({
  nodes,
  cyclic,
  pointers,
  doubly,
}: {
  nodes: ChainNode[];
  cyclic: boolean;
  /** node id → variable names referencing it */
  pointers: Record<number, string[]>;
  /** Nodes carry a `prev` too — draw the backward arrows as well. */
  doubly?: boolean;
}) {
  const uid = "vd-list";
  const anyPtr = Object.keys(pointers).length > 0;
  const top = anyPtr ? 28 : 6;
  const width = nodes.length * (N_W + N_GAP) + 34;
  const height = top + N_H + (cyclic ? 30 : doubly ? 22 : 10);

  return (
    <svg
      className="vd"
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="linked list"
    >
      <ArrowHead id={uid} />
      {nodes.map((node, i) => {
        const x = i * (N_W + N_GAP);
        const names = pointers[node.id];
        const isLast = i === nodes.length - 1;
        return (
          <g key={node.id}>
            {/* data | next */}
            <rect
              x={x}
              y={top}
              width={N_W}
              height={N_H}
              rx={4}
              className={`vd-node${names ? " on" : ""}`}
            />
            <line
              x1={x + N_VAL_W}
              y1={top}
              x2={x + N_VAL_W}
              y2={top + N_H}
              className="vd-node-split"
            />
            <text
              x={x + N_VAL_W / 2}
              y={top + N_H / 2 + 4}
              className="vd-val"
              textAnchor="middle"
            >
              {node.text}
            </text>

            {/* the arrow out of the next-half */}
            {!isLast ? (
              <line
                x1={x + N_VAL_W + N_NEXT_W / 2}
                y1={top + N_H / 2}
                x2={x + N_W + N_GAP - 4}
                y2={top + N_H / 2}
                className="vd-edge"
                markerEnd={`url(#${uid})`}
              />
            ) : cyclic ? (
              // Loop back under the row to the first node.
              <path
                d={`M ${x + N_VAL_W + N_NEXT_W / 2} ${top + N_H}
                    C ${x + N_W} ${top + N_H + 26},
                      ${N_W / 2} ${top + N_H + 26},
                      ${N_VAL_W / 2} ${top + N_H + 3}`}
                className="vd-edge cyclic"
                fill="none"
                markerEnd={`url(#${uid})`}
              />
            ) : (
              <>
                <line
                  x1={x + N_VAL_W + N_NEXT_W / 2}
                  y1={top + N_H / 2}
                  x2={x + N_W + 16}
                  y2={top + N_H / 2}
                  className="vd-edge"
                  markerEnd={`url(#${uid})`}
                />
                <text
                  x={x + N_W + 22}
                  y={top + N_H / 2 + 4}
                  className="vd-null"
                >
                  ∅
                </text>
              </>
            )}

            {/* Backward pointer, drawn under the row so it can't be confused
                with the forward one. */}
            {doubly && i > 0 ? (
              <line
                x1={x + 4}
                y1={top + N_H + 9}
                x2={x - N_GAP + N_VAL_W / 2}
                y2={top + N_H + 9}
                className="vd-edge back"
                markerEnd={`url(#${uid})`}
              />
            ) : null}

            {names ? (
              <>
                <text
                  x={x + N_W / 2}
                  y={top - 15}
                  className="vd-ptr-name"
                  textAnchor="middle"
                >
                  {names.join(", ")}
                </text>
                <line
                  x1={x + N_W / 2}
                  y1={top - 12}
                  x2={x + N_W / 2}
                  y2={top - 2}
                  className="vd-ptr-line"
                  markerEnd={`url(#${uid})`}
                />
              </>
            ) : null}
          </g>
        );
      })}
    </svg>
  );
}

/* ── Binary tree ────────────────────────────────────────── */

const T_R = 16;
const T_LEVEL = 52;
const T_SLOT = 42;

export function TreeDiagram({
  nodes,
  pointers,
}: {
  nodes: TreeNode[];
  pointers: Record<number, string[]>;
}) {
  const uid = "vd-tree";
  const slots = Math.max(...nodes.map((n) => n.slot)) + 1;
  const depth = Math.max(...nodes.map((n) => n.depth)) + 1;
  const width = slots * T_SLOT + 20;
  const height = depth * T_LEVEL + 14;
  const cx = (n: TreeNode) => n.slot * T_SLOT + T_SLOT / 2 + 10;
  const cy = (n: TreeNode) => n.depth * T_LEVEL + T_R + 12;
  const byId = new Map(nodes.map((n) => [n.id, n]));

  return (
    <svg
      className="vd"
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="binary tree"
    >
      <ArrowHead id={uid} />
      {/* Edges first so the circles sit on top of them. */}
      {nodes.map((n) => {
        const parent = n.parent == null ? null : byId.get(n.parent);
        if (!parent) return null;
        return (
          <line
            key={`e${n.id}`}
            x1={cx(parent)}
            y1={cy(parent) + T_R}
            x2={cx(n)}
            y2={cy(n) - T_R}
            className="vd-edge"
          />
        );
      })}
      {nodes.map((n) => {
        const names = pointers[n.id];
        return (
          <g key={n.id}>
            <circle
              cx={cx(n)}
              cy={cy(n)}
              r={T_R}
              className={`vd-circle${names ? " on" : ""}`}
            />
            <text
              x={cx(n)}
              y={cy(n) + 4}
              className="vd-val"
              textAnchor="middle"
            >
              {n.text}
            </text>
            {names ? (
              <text
                x={cx(n)}
                y={cy(n) - T_R - 5}
                className="vd-ptr-name"
                textAnchor="middle"
              >
                {names.join(", ")}
              </text>
            ) : null}
          </g>
        );
      })}
    </svg>
  );
}
