import { useEffect, useState } from "react";
import { checkAnswer } from "../api";
import { VizPanel } from "./VizPanel";
import type { CheckAnswerResult, StudyInfo } from "../types";

type Props = {
  /** null for non-LeetCode classes — the panel then just says so. */
  study: StudyInfo | null;
  /** Current editor buffer, read fresh when checking work. */
  getCode: () => string;
};

const DIFF_CLASS: Record<string, string> = {
  Easy: "study-diff easy",
  Medium: "study-diff medium",
  Hard: "study-diff hard",
};

export function StudyPanel({ study, getCode }: Props) {
  const [answerOpen, setAnswerOpen] = useState(false);
  const [checking, setChecking] = useState(false);
  const [check, setCheck] = useState<CheckAnswerResult | null>(null);
  const [checkError, setCheckError] = useState(false);

  const problemNo = study?.problem?.number ?? null;
  const patternId = study?.lesson?.id ?? null;

  // A new problem starts un-spoiled and un-checked.
  useEffect(() => {
    setAnswerOpen(false);
    setCheck(null);
    setCheckError(false);
  }, [problemNo, patternId]);

  async function runCheck() {
    if (checking || !patternId || problemNo == null) return;
    setChecking(true);
    setCheckError(false);
    try {
      setCheck(
        await checkAnswer({
          code: getCode(),
          pattern_id: patternId,
          problem_number: problemNo,
        }),
      );
    } catch {
      setCheckError(true);
    } finally {
      setChecking(false);
    }
  }

  // Watching a loop fill a list is just as useful in Foundations as it is on a
  // LeetCode problem, so the visualiser is always available — only the
  // question and pattern notes depend on there being a study payload.
  const viz = (
    <div className="study-section">
      <div className="study-section-label">Watch it run</div>
      <VizPanel
        getCode={getCode}
        patternId={patternId}
        problemNumber={problemNo}
        resetKey={`${patternId}:${problemNo}`}
      />
    </div>
  );

  if (!study || (!study.problem && !study.lesson)) {
    return (
      <div className="study-panel">
        <div className="study-head">
          <span className="study-head-label">Problem</span>
        </div>
        <div className="study-body">
          <p className="study-none">
            No write-up for this exercise — LeetCode classes show the question
            and pattern notes here.
          </p>
          {viz}
        </div>
      </div>
    );
  }

  const { problem, lesson } = study;

  return (
    <div className="study-panel">
      <div className="study-head">
        <span className="study-head-label">Problem</span>
        {problem ? (
          <span className="study-head-title">{problem.title}</span>
        ) : null}
      </div>
      <div className="study-body">
      {problem ? (
        <div className="study-section">
          <div className="study-problem-head">
            <span className="study-problem-num">#{problem.number}</span>
            <span className="study-problem-title">{problem.title}</span>
            <span className={DIFF_CLASS[problem.difficulty] ?? "study-diff"}>
              {problem.difficulty}
            </span>
            {problem.url ? (
              <a
                className="study-lc-link"
                href={problem.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                LC ↗
              </a>
            ) : null}
          </div>

          <p className="study-statement">{problem.statement}</p>

          {problem.examples.length > 0 ? (
            <div className="study-examples">
              {problem.examples.map((ex, i) => (
                <pre key={i} className="study-example-block">
                  {ex}
                </pre>
              ))}
            </div>
          ) : null}

          <div className="study-meta-row">
            {problem.idea ? (
              <span className="study-meta-chip">
                <span className="study-meta-label">Idea</span> {problem.idea}
              </span>
            ) : null}
            {problem.complexity ? (
              <span className="study-meta-chip">
                <span className="study-meta-label">Complexity</span>{" "}
                {problem.complexity}
              </span>
            ) : null}
          </div>

          {problem.note ? (
            <p className="study-note">{problem.note}</p>
          ) : null}

          {/* Self-check: compare what you wrote against the real solution and
              get told which line is off, rather than eyeballing two blocks. */}
          <div className="study-answer">
            <div className="study-answer-actions">
              <button
                type="button"
                className="study-btn"
                onClick={() => void runCheck()}
                disabled={checking}
              >
                {checking ? "Checking…" : "Check my work"}
              </button>
              <button
                type="button"
                className={`study-btn${answerOpen ? " on" : ""}`}
                onClick={() => setAnswerOpen((o) => !o)}
              >
                {answerOpen ? "Hide answer" : "Show answer"}
              </button>
            </div>

            {checkError ? (
              <p className="study-check bad">
                Couldn’t reach the coach — is the API running?
              </p>
            ) : check ? (
              check.matches ? (
                <p className="study-check good">
                  ✓ Your code matches the solution.
                </p>
              ) : (
                <pre className="study-check-diff">
                  {check.note || "Doesn’t match yet — compare with the answer below."}
                </pre>
              )
            ) : null}

            {answerOpen ? (
              <pre className="study-solution">{problem.solution}</pre>
            ) : null}
          </div>
        </div>
      ) : null}

      {/* Watch the data move: arrays with the pointers sitting on them, the
          dict filling up, nodes wiring together — step by step. */}
      {viz}

      {lesson ? (
        <div className="study-section">
          <div className="study-lesson-head">
            <span className="study-lesson-name">{lesson.name} pattern</span>
          </div>

          <p className="study-summary">{lesson.summary}</p>

          {lesson.when ? (
            <div className="study-when">
              <span className="study-when-label">When to use</span>
              <span>{lesson.when}</span>
            </div>
          ) : null}

          {lesson.template ? (
            <div className="study-template-wrap">
              <div className="study-section-label">Template</div>
              <pre className="study-template">{lesson.template}</pre>
            </div>
          ) : null}

          {lesson.steps.length > 0 ? (
            <div className="study-steps-wrap">
              <div className="study-section-label">Steps</div>
              <ol className="study-steps">
                {lesson.steps.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ol>
            </div>
          ) : null}

          {lesson.pitfalls.length > 0 ? (
            <div className="study-pitfalls-wrap">
              <div className="study-section-label">Watch out for</div>
              <ul className="study-pitfalls">
                {lesson.pitfalls.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
      </div>
    </div>
  );
}
