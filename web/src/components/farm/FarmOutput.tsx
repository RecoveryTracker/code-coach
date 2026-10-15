/** The Output window: what the program prints, what the gate refuses, errors, and how the run is going. */

import { useEffect, useRef } from "react";

import type { FarmLine, FarmRun, FarmViolation } from "../../types";
import { runText } from "./farmShared";

type Props = {
  lines: FarmLine[];
  violations: FarmViolation[];
  error: string;
  run: FarmRun | null;
  /** More than one file in this language: say which file an error is in. */
  multiFile: boolean;
};

export function FarmOutput({ lines, violations, error, run, multiFile }: Props) {
  const scroller = useRef<HTMLDivElement | null>(null);
  const stuck = useRef(true);

  // Follow the newest line, unless you scrolled up to read.
  useEffect(() => {
    const el = scroller.current;
    if (el && stuck.current) el.scrollTop = el.scrollHeight;
  }, [lines.length, violations.length, error]);

  const status = runText(run, multiFile);
  return (
    <div className="fm-output">
      <div
        ref={scroller}
        className="fm-output-lines"
        aria-live="polite"
        onScroll={(e) => {
          const el = e.currentTarget;
          stuck.current = el.scrollHeight - el.scrollTop - el.clientHeight < 24;
        }}
      >
        {violations.map((v, i) => (
          <div key={`v${i}`} className="fm-line error">
            <span className="fm-line-at">
              {v.file && multiFile ? `${v.file}, line` : "Line"} {v.line}
            </span>{" "}
            {v.message} <code>{v.snippet}</code>
          </div>
        ))}
        {error ? <div className="fm-line error">{error}</div> : null}
        {lines.length === 0 && !violations.length && !error ? (
          <div className="fm-line info">Output, and anything you quick_print, shows here.</div>
        ) : null}
        {lines.map((l, i) => (
          <div key={i} className={`fm-line ${l.kind}`}>
            {l.text}
          </div>
        ))}
      </div>
      <div className="fm-output-status">
        <span className={`fm-run ${run?.status ?? ""}`}>{status || "No program running"}</span>
      </div>
    </div>
  );
}
