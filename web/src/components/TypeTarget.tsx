import { useEffect, useLayoutEffect, useRef, useState } from "react";
import type { DrillEvaluateResult, PracticeSession, SupportLink } from "../types";

/**
 * How much the type-along asks for at once — one line up to a whole function.
 * It lives on this panel because this panel is what it changes; in the nav bar
 * it read as a fourth place to navigate and got in the way.
 */
const CHUNK_OPTIONS = [
  { value: 1, label: "Single lines" },
  { value: 2, label: "Lines+" },
  { value: 3, label: "Two-liners" },
  { value: 4, label: "Blocks" },
  { value: 5, label: "Whole functions" },
];

type Props = {
  session: PracticeSession;
  result: DrillEvaluateResult | null;
  exerciseIndex: number;
  onReview: (skillId: string) => void;
  onDictationLevel?: (level: number) => void;
};

/**
 * The code the student is copying, in its own column beside the editor.
 *
 * It gets real height here (the old inline banner capped at 9em and silently
 * hid the rest of a solution), plus line numbers and a scroll fade so a long
 * solution reads as long instead of looking finished at line 6.
 */
export function TypeTarget({
  session,
  result,
  exerciseIndex,
  onReview,
  onDictationLevel,
}: Props) {
  const total = session.steps.length || 1;
  const endless = Boolean(session.endless);
  const complete = !endless && exerciseIndex >= total;
  const step = exerciseIndex < total ? session.steps[exerciseIndex] : null;
  const isBuild = session.lesson_role === "build" || step?.kind === "build";
  const typeLine = step?.label ?? null;
  const hintLines = step?.hint_lines?.length
    ? step.hint_lines
    : typeLine
      ? typeLine.split("\n")
      : [];
  const supports: SupportLink[] = step?.supports ?? [];
  const tip = step?.tip ?? null;
  const keyboardTip =
    step?.keyboard_tip ?? "End of line: ⌘ →   ·   Down a line: ↓";

  const lines = typeLine ? typeLine.split("\n") : [];

  const [hintLevel, setHintLevel] = useState(0);
  useEffect(() => {
    setHintLevel(0);
  }, [exerciseIndex, session.drill_id]);

  // "There's more below" affordance — only shown when it's actually true.
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [moreBelow, setMoreBelow] = useState(false);

  useLayoutEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const update = () => {
      const rest = el.scrollHeight - el.scrollTop - el.clientHeight;
      setMoreBelow(rest > 4);
    };
    update();
    el.addEventListener("scroll", update, { passive: true });
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => {
      el.removeEventListener("scroll", update);
      ro.disconnect();
    };
  }, [typeLine, exerciseIndex]);

  // A new exercise starts at the top of the block, not wherever the last scroll left it.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
  }, [exerciseIndex, session.drill_id]);

  if (complete) {
    return (
      <aside className="tt-panel">
        <div className="tt-head">
          <span className="tt-label">Lesson done</span>
        </div>
        <div className="tt-empty">
          All exercises in this lesson are done. Use Class / Lesson to move on.
        </div>
      </aside>
    );
  }

  return (
    <aside className="tt-panel">
      <div className="tt-head">
        <span className="tt-label">{isBuild ? "Build this" : "Type this"}</span>
        {!isBuild && lines.length > 1 ? (
          <span className="tt-count">{lines.length} lines</span>
        ) : null}
        {/* Position lives in the breadcrumb now — no need to say it twice. */}
        {endless && onDictationLevel ? (
          <label className="tt-chunk" title="How much to type before the coach checks it">
            <span className="tt-chunk-label">Chunk</span>
            <select
              className="tt-chunk-select"
              value={session.dictation_level ?? 1}
              onChange={(e) => onDictationLevel(Number(e.target.value))}
              aria-label="How much to type at once"
            >
              {CHUNK_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        {isBuild ? (
          <button
            type="button"
            className={`coach-chat-toggle hint-btn${hintLevel > 0 ? " active" : ""}`}
            onClick={() => setHintLevel((h) => (h + 1) % 4)}
            title="Each click reveals a bit more"
          >
            {hintLevel === 0
              ? "Hint"
              : hintLevel === 1
                ? "More help"
                : hintLevel === 2
                  ? "Show solution"
                  : "Hide hint"}
          </button>
        ) : null}
      </div>

      <div className={`tt-scroll-wrap${moreBelow ? " has-more" : ""}`}>
        <div className="tt-scroll" ref={scrollRef}>
          {isBuild ? (
            <div className="tt-goal">{typeLine}</div>
          ) : (
            <div className="tt-code">
              {lines.map((ln, i) => (
                <div className="tt-line" key={i}>
                  <span className="tt-ln" aria-hidden>
                    {i + 1}
                  </span>
                  <code className="tt-src">{ln === "" ? " " : ln}</code>
                </div>
              ))}
            </div>
          )}

          {isBuild && hintLevel > 0 ? (
            <div className="tt-hint">
              <div className="hint-popover-title">Think about it</div>
              <p className="hint-popover-text">
                {tip || keyboardTip || "What tool from this class fits?"}
              </p>
              {hintLevel >= 2 && hintLines.length > 0 ? (
                <>
                  <div className="hint-popover-title">It starts like this</div>
                  <pre className="hint-popover-code">
                    {hintLines[0] + (hintLines.length > 1 ? "\n…" : "")}
                  </pre>
                </>
              ) : null}
              {hintLevel >= 3 ? (
                <>
                  <div className="hint-popover-title">Exact lines</div>
                  <pre className="hint-popover-code">
                    {hintLines.join("\n")}
                  </pre>
                </>
              ) : null}
              {supports.length > 0 ? (
                <div className="hint-supports">
                  <div className="hint-popover-title">
                    Practice the basics first (click)
                  </div>
                  {supports.map((s) => (
                    <button
                      key={s.skill_id + s.label}
                      type="button"
                      className="hint-support-link"
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => onReview(s.skill_id)}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
        <span className="tt-more-hint" aria-hidden>
          ↓ more
        </span>
      </div>

      {isBuild && result?.requirements?.length ? (
        <div className="req-list" aria-label="What this goal needs">
          <span className="req-list-label">Needs:</span>
          {result.requirements.map((r) => (
            <span key={r.label} className={`req-item ${r.passed ? "ok" : "todo"}`}>
              <span aria-hidden>{r.passed ? "✓" : "○"}</span> {r.label}
            </span>
          ))}
        </div>
      ) : null}

      {/* One slim line. The problem tip that used to live here grew to ~250px
          and buried the code — it's all in the Problem panel below now. */}
      <div className="tt-foot" title={keyboardTip}>
        ⌨ {keyboardTip}
      </div>
    </aside>
  );
}
