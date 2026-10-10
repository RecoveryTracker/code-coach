/**
 * "What your code does": the plain-English walkthrough under the coach strip.
 * One panel for both places that ask for it - the coach's lessons and Free
 * mode - so the two read the same and a change is made once.
 */

import type { ExplainResult } from "../types";

type Props = {
  explanation: ExplainResult | null;
  busy: boolean;
  error: boolean;
  onRefresh: () => void;
  /** Begin dragging the panel's bottom edge. */
  onGripDown: () => void;
};

export function ExplainPanel({ explanation, busy, error, onRefresh, onGripDown }: Props) {
  return (
    <div className="coach-explain">
      <div className="coach-explain-head">
        <span className="coach-explain-title">{busy ? "Reading your code…" : "What your code does"}</span>
        <button
          type="button"
          className="coach-chat-toggle"
          onClick={onRefresh}
          disabled={busy}
          title="Re-explain after you edit"
        >
          Refresh
        </button>
      </div>
      {error ? (
        <div className="coach-explain-body">
          <p className="explain-note bad">Couldn’t reach the coach — is the API running?</p>
        </div>
      ) : explanation ? (
        <div className="coach-explain-body">
          <p className="explain-summary">{explanation.summary}</p>
          {explanation.error_note ? <p className="explain-note bad">{explanation.error_note}</p> : null}
          {explanation.lines.length > 0 ? (
            <div className="explain-lines">
              {explanation.lines.map((L, i) => (
                <div key={`${L.line}-${i}`} className="explain-row" style={{ paddingLeft: 10 + L.depth * 18 }}>
                  <code className="explain-code">{L.source || " "}</code>
                  <span className="explain-text">{L.text}</span>
                </div>
              ))}
            </div>
          ) : null}
          {explanation.output_notes.length > 0 ? (
            <div className="explain-output">
              <div className="explain-output-title">Why the output looks like this</div>
              {explanation.output_notes.map((n, i) => (
                <p key={i} className="explain-note">
                  {n}
                </p>
              ))}
            </div>
          ) : null}
        </div>
      ) : (
        <div className="coach-explain-body">
          <p className="explain-note">…</p>
        </div>
      )}
      {/* Drag the bottom edge to size the panel. */}
      <div
        className="coach-explain-grip"
        title="Drag to resize"
        onPointerDown={(e) => {
          e.preventDefault();
          onGripDown();
        }}
      />
    </div>
  );
}
