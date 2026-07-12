import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type CSSProperties,
} from "react";
import {
  backFromReview,
  evaluateDrill,
  fetchCurrentPractice,
  fetchMoreLines,
  gotoLesson,
  navigateCurriculum,
  setDictationLevel,
  startReview,
  updateProgress,
} from "./api";
import { AdaptiveCoach } from "./components/AdaptiveCoach";
import { EditorPane } from "./components/EditorPane";
import { ProgressPanel } from "./components/ProgressPanel";
import { ScriptLibrary } from "./components/ScriptLibrary";
import { Terminal } from "./components/Terminal";
import type {
  DrillEvaluateResult,
  PracticeSession,
  ProgressInfo,
} from "./types";

const DEBOUNCE_MS = 180;

function draftKey(id: string) {
  return `code-coach:drill:${id}`;
}

function loadDraft(id: string): string | null {
  try {
    return localStorage.getItem(draftKey(id));
  } catch {
    return null;
  }
}

function saveDraft(id: string, code: string) {
  try {
    localStorage.setItem(draftKey(id), code);
  } catch {
    /* ignore */
  }
}

function clearDraft(id: string) {
  try {
    localStorage.removeItem(draftKey(id));
  } catch {
    /* ignore */
  }
}

type Layout = { term: number };

function loadLayout(): Layout {
  try {
    const raw = localStorage.getItem("code-coach:workspace-layout-v2");
    if (raw) {
      const p = JSON.parse(raw) as Layout;
      if (p.term) return p;
    }
  } catch {
    /* ignore */
  }
  return { term: 140 };
}

const FREE_KEY = "code-coach:free-buffer";

/**
 * Class → Lesson → Exercise.
 * Exercises auto-advance when completed.
 * ← Back / Next → always steer between lessons (never grayed for "not done").
 * Free mode: coach off, plain coding.
 */
export default function App() {
  const [session, setSession] = useState<PracticeSession | null>(null);
  const [progress, setProgress] = useState<ProgressInfo | null>(null);
  const [seedCode, setSeedCode] = useState("");
  const [editorRevision, setEditorRevision] = useState(0);
  const [result, setResult] = useState<DrillEvaluateResult | null>(null);
  const [hasRun, setHasRun] = useState(false);
  const [running, setRunning] = useState(false);
  const [ready, setReady] = useState(false);
  const [bootError, setBootError] = useState<string | null>(null);
  const [layout, setLayout] = useState<Layout>(loadLayout);
  const [watching, setWatching] = useState(false);
  const [freeMode, setFreeMode] = useState(false);
  const [progressOpen, setProgressOpen] = useState(false);
  /** Current exercise within the active lesson. */
  const [exerciseIndex, setExerciseIndex] = useState(0);
  const [exerciseDone, setExerciseDone] = useState(false);
  const exerciseIndexRef = useRef(0);
  const exerciseDoneRef = useRef(false);
  const autoAdvanceTimer = useRef<number | null>(null);

  const codeRef = useRef("");
  const drillRef = useRef<string | null>(null);
  const evalSeq = useRef(0);
  const debounce = useRef<number | null>(null);
  const shellRef = useRef<HTMLDivElement | null>(null);
  const drag = useRef<"coach" | "term" | null>(null);
  const freeModeRef = useRef(false);

  exerciseIndexRef.current = exerciseIndex;
  exerciseDoneRef.current = exerciseDone;
  freeModeRef.current = freeMode;

  const score = useCallback(
    async (
      drillId: string,
      source: string,
      run: boolean,
      atIndex?: number,
    ) => {
      // Which exercise the student is on. Advance paths pass the new index
      // explicitly (the ref only updates on the next render), so the coach
      // message focuses on the line now shown in the box.
      const idx = atIndex ?? exerciseIndexRef.current;
      const seq = ++evalSeq.current;
      if (run) setRunning(true);
      if (!run) setWatching(true);
      try {
        const data = await evaluateDrill(drillId, source, run, idx);
        if (seq !== evalSeq.current || drillId !== drillRef.current) return;
        setResult((prev) => {
          if (!run && prev?.ran) {
            return {
              ...data,
              stdout: prev.stdout,
              stderr: prev.stderr,
              exit_code: prev.exit_code,
              ran: true,
            };
          }
          return data;
        });
        if (run) setHasRun(true);
        if (data.progress) setProgress(data.progress);

        // Current exercise complete → flag for auto-advance (not lesson jump).
        const curPassed = Boolean(data.checks[idx]?.passed);
        setExerciseDone(curPassed);
      } catch {
        setResult(
          (prev) =>
            prev && {
              ...prev,
              observation: "Coach couldn’t reach the server. Try Run again.",
              tone: "error",
              status: "error",
            },
        );
      } finally {
        if (run && seq === evalSeq.current) setRunning(false);
        if (!run && seq === evalSeq.current) setWatching(false);
      }
    },
    [],
  );

  /**
   * Load a practice session.
   * forceClean — only for explicit "Start over" / intentional reset.
   * preserveCode — keep this buffer (used when endless type-along loads more).
   * Never silently wipe the editor after the user has been typing.
   */
  const loadSession = useCallback(
    async (
      s: PracticeSession,
      forceClean = false,
      preserveCode?: string | null,
    ) => {
      setSession(s);
      setProgress(s.progress);
      drillRef.current = s.drill_id;
      setExerciseIndex(0);
      setExerciseDone(false);
      if (autoAdvanceTimer.current) {
        window.clearTimeout(autoAdvanceTimer.current);
        autoAdvanceTimer.current = null;
      }

      let initial = s.starter;
      if (preserveCode != null) {
        // Keep what the user already typed (next endless window, difficulty change)
        initial = preserveCode;
        saveDraft(s.drill_id, preserveCode);
      } else if (forceClean) {
        clearDraft(s.drill_id);
        initial = s.starter;
      } else {
        const draft = loadDraft(s.drill_id);
        if (draft != null && draft !== "") {
          initial = draft;
        }
      }

      codeRef.current = initial;
      setSeedCode(initial);
      setEditorRevision((n) => n + 1);
      setHasRun(false);
      setResult(null);
      await score(s.drill_id, initial, false, 0);
    },
    [score],
  );

  const loadSessionRef = useRef(loadSession);
  loadSessionRef.current = loadSession;

  /** Advance to next *exercise* inside the lesson (automatic when complete). */
  const advanceExercise = useCallback(() => {
    if (!session || freeModeRef.current) return;
    const next = exerciseIndexRef.current + 1;
    const total = session.steps.length;

    if (next >= total) {
      setExerciseDone(false);
      // Foundations type-along is endless — next window, keep editor contents
      if (session.endless || session.drill_id === "class-1-dictation") {
        void (async () => {
          try {
            const keep = codeRef.current;
            const s = await fetchMoreLines();
            await loadSessionRef.current(s, false, keep);
          } catch {
            /* stay at end of window */
            setExerciseIndex(Math.max(0, total - 1));
          }
        })();
        return;
      }
      setExerciseIndex(total);
      // Finished supporting review → back to prior lesson, restoring its work
      if (session.is_review) {
        void (async () => {
          try {
            const s = await backFromReview();
            await loadSessionRef.current(s, false);
          } catch {
            /* stay */
          }
        })();
      }
      return;
    }

    setExerciseIndex(next);
    setExerciseDone(false);
    const id = drillRef.current;
    if (id) void score(id, codeRef.current, false, next);
  }, [session, score]);

  // Auto-advance exercises shortly after the current one is completed
  useEffect(() => {
    if (freeMode || !exerciseDone || !session) return;
    if (autoAdvanceTimer.current) window.clearTimeout(autoAdvanceTimer.current);
    autoAdvanceTimer.current = window.setTimeout(() => {
      autoAdvanceTimer.current = null;
      advanceExercise();
    }, 650);
    return () => {
      if (autoAdvanceTimer.current) {
        window.clearTimeout(autoAdvanceTimer.current);
        autoAdvanceTimer.current = null;
      }
    };
  }, [exerciseDone, exerciseIndex, session, advanceExercise, freeMode]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        // Soft settings — don't hard-fail boot if this races
        try {
          await updateProgress({ mode: "progressive", coach_level: 1 });
        } catch {
          /* continue */
        }
        if (cancelled) return;
        const current = await fetchCurrentPractice();
        if (cancelled) return;
        await loadSession(current);
        if (!cancelled) setReady(true);
      } catch (e) {
        if (!cancelled) {
          setBootError(
            e instanceof Error ? e.message : "API error",
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onChange = useCallback(
    (v: string) => {
      codeRef.current = v;
      if (freeModeRef.current) {
        try {
          localStorage.setItem(FREE_KEY, v);
        } catch {
          /* ignore */
        }
        return;
      }
      if (debounce.current) window.clearTimeout(debounce.current);
      debounce.current = window.setTimeout(() => {
        debounce.current = null;
        const id = drillRef.current;
        if (!id) return;
        saveDraft(id, codeRef.current);
        void score(id, codeRef.current, false);
      }, DEBOUNCE_MS);
    },
    [score],
  );

  const onRun = useCallback(() => {
    if (debounce.current) {
      window.clearTimeout(debounce.current);
      debounce.current = null;
    }
    if (freeModeRef.current) {
      // free mode: still allow run via evaluate with empty drill? use last drill id
      const id = drillRef.current;
      if (!id) return;
      void score(id, codeRef.current, true);
      return;
    }
    const id = drillRef.current;
    if (!id) return;
    saveDraft(id, codeRef.current);
    void score(id, codeRef.current, true);
  }, [score]);

  const jumpTo = useCallback(
    async (body: {
      class_id?: string;
      lesson_number?: number;
      class_delta?: number;
      lesson_delta?: number;
    }) => {
      // Save the lesson you're leaving so you can come back and study it or
      // keep going. Arrive with forceClean=false so loadSession restores the
      // target lesson's saved work (or its starter on a first visit) instead
      // of wiping it.
      if (drillRef.current) saveDraft(drillRef.current, codeRef.current);
      try {
        const next = await navigateCurriculum(body);
        await loadSession(next, false);
      } catch {
        try {
          // fallback for older API
          const next = await gotoLesson(body.lesson_number, body.class_id);
          await loadSession(next, false);
        } catch {
          /* stay */
        }
      }
    },
    [loadSession],
  );

  const onDictationLevel = useCallback(
    async (level: number) => {
      try {
        const keep = codeRef.current;
        const s = await setDictationLevel(level);
        // Keep typed work; only the coach target changes
        await loadSession(s, false, keep);
      } catch {
        /* stay */
      }
    },
    [loadSession],
  );

  const onExerciseDelta = useCallback(
    (d: number) => {
      if (!session) return;
      const total = session.steps.length;
      let next = exerciseIndexRef.current + d;
      if (next < 0) {
        if (session.endless) {
          setExerciseIndex(0);
          return;
        }
        // previous lesson, last exercise — jump lesson back
        void jumpTo({ lesson_delta: -1 });
        return;
      }
      if (next >= total) {
        if (session.endless || session.drill_id === "class-1-dictation") {
          void (async () => {
            try {
              const keep = codeRef.current;
              const s = await fetchMoreLines();
              await loadSessionRef.current(s, false, keep);
            } catch {
              /* stay */
            }
          })();
          return;
        }
        void jumpTo({ lesson_delta: 1 });
        return;
      }
      setExerciseIndex(next);
      setExerciseDone(false);
      const id = drillRef.current;
      if (id) void score(id, codeRef.current, false, next);
    },
    [session, score, jumpTo],
  );

  const onReview = useCallback(
    async (skillId: string) => {
      try {
        if (skillId === "lesson1" && session?.class_id) {
          await jumpTo({ class_id: session.class_id, lesson_number: 1 });
          return;
        }
        // Keep the main lesson's work before detouring into review practice.
        if (drillRef.current) saveDraft(drillRef.current, codeRef.current);
        const next = await startReview(skillId);
        await loadSession(next, false);
      } catch {
        /* stay */
      }
    },
    [loadSession, jumpTo, session],
  );

  const onBackFromReview = useCallback(async () => {
    // Returning from review restores the lesson's saved work, not a blank slate.
    if (drillRef.current) saveDraft(drillRef.current, codeRef.current);
    try {
      const next = await backFromReview();
      await loadSession(next, false);
    } catch {
      /* stay */
    }
  }, [loadSession]);

  const toggleFreeMode = useCallback(() => {
    if (!freeMode) {
      // entering free mode — snapshot free buffer or current code
      try {
        const existing = localStorage.getItem(FREE_KEY);
        const buf = existing ?? codeRef.current;
        localStorage.setItem(FREE_KEY, buf);
        codeRef.current = buf;
        setSeedCode(buf);
        setEditorRevision((n) => n + 1);
      } catch {
        /* */
      }
      setFreeMode(true);
      return;
    }
    // leaving free mode — save free buffer, restore lesson
    try {
      localStorage.setItem(FREE_KEY, codeRef.current);
    } catch {
      /* */
    }
    setFreeMode(false);
    if (session) void loadSession(session, false);
  }, [freeMode, session, loadSession]);

  // Resize terminal height only
  useEffect(() => {
    const move = (e: PointerEvent) => {
      if (!drag.current || !shellRef.current) return;
      const rect = shellRef.current.getBoundingClientRect();
      if (drag.current === "term") {
        const fromBottom = rect.bottom - e.clientY;
        const h = Math.min(Math.max(fromBottom, 80), rect.height - 200);
        setLayout({ term: h });
      }
    };
    const up = () => {
      if (!drag.current) return;
      drag.current = null;
      document.body.classList.remove("is-resizing");
      try {
        localStorage.setItem(
          "code-coach:workspace-layout-v2",
          JSON.stringify(layout),
        );
      } catch {
        /* ignore */
      }
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, [layout]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!(e.metaKey || e.ctrlKey) || e.key !== "Enter") return;
      if ((e.target as HTMLElement)?.closest?.(".monaco-editor")) return;
      e.preventDefault();
      onRun();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onRun]);

  if (bootError) {
    return (
      <div className="ws-boot">
        <h1>Code Coach</h1>
        <p>Can’t reach the API.</p>
        <p className="muted">{bootError}</p>
      </div>
    );
  }

  if (!ready || !session) {
    return <div className="ws-boot">Starting workspace…</div>;
  }

  const checks =
    result?.checks ??
    session.steps.map((s) => ({ label: s.label, passed: false }));

  return (
    <div
      className="ws-shell ws-shell-stack"
      ref={shellRef}
      style={{ "--term-h": `${layout.term}px` } as CSSProperties}
    >
      <header className="ws-top">
        <div className="ws-brand">
          <strong>Code Coach</strong>
        </div>
        {/* No title breadcrumb here — the Class/Lesson steppers below carry
            the same info. Free mode still labels itself in its banner. */}
        <div className="ws-top-actions">
          <ScriptLibrary
            source={freeMode ? "free" : "lesson"}
            getCode={() => codeRef.current}
            setCode={(code) => {
              codeRef.current = code;
              setSeedCode(code);
              setEditorRevision((n) => n + 1);
              if (freeMode) {
                try {
                  localStorage.setItem(FREE_KEY, code);
                } catch {
                  /* */
                }
              } else if (drillRef.current) {
                saveDraft(drillRef.current, code);
                void score(drillRef.current, code, false);
              }
            }}
          />
          <button
            type="button"
            className={`ws-btn${progressOpen ? " primary" : ""}`}
            onClick={() => setProgressOpen((o) => !o)}
            title="Skills, type-along lines, and what's due for review"
          >
            Progress
          </button>
          <button
            type="button"
            className={`ws-btn${freeMode ? " primary" : ""}`}
            onClick={toggleFreeMode}
            title={
              freeMode
                ? "Turn the coach back on"
                : "Code freely without coach prompts"
            }
          >
            {freeMode ? "Coach on" : "Free mode"}
          </button>
          {!freeMode ? (
            <button
              type="button"
              className="ws-btn"
              onClick={() => {
                if (!session) return;
                clearDraft(session.drill_id);
                void loadSession(session, true);
              }}
            >
              Start over
            </button>
          ) : null}
          <button
            type="button"
            className="ws-btn primary"
            onClick={onRun}
            disabled={running}
          >
            {running ? "Running…" : "Run"}
          </button>
        </div>
      </header>

      {/* Coach strip — hidden in free mode */}
      {freeMode ? (
        <div className="coach-banner free-banner">
          <span className="coach-banner-done">
            Free mode — code anything. Use <strong>Save</strong> /{" "}
            <strong>Load…</strong> for your scripts.{" "}
            <strong>Coach on</strong> returns to practice.
          </span>
        </div>
      ) : (
        <AdaptiveCoach
          session={session}
          result={result}
          checks={checks}
          exerciseIndex={exerciseIndex}
          exerciseDone={exerciseDone}
          onClassDelta={(d) => void jumpTo({ class_delta: d })}
          onLessonDelta={(d) => void jumpTo({ lesson_delta: d })}
          onExerciseDelta={onExerciseDelta}
          onSelectClass={(id) =>
            void jumpTo({ class_id: id, lesson_number: 1 })
          }
          onSelectLesson={(n) => void jumpTo({ lesson_number: n })}
          onReview={onReview}
          onBackFromReview={onBackFromReview}
          onDictationLevel={(n) => void onDictationLevel(n)}
          watching={watching}
          getCode={() => codeRef.current}
        />
      )}

      <div className="ws-editor">
        <EditorPane
          code={seedCode}
          revision={editorRevision}
          onChange={onChange}
          onRun={onRun}
        />
      </div>

      <div
        className="ws-split-row"
        onPointerDown={(e) => {
          e.preventDefault();
          drag.current = "term";
          document.body.classList.add("is-resizing");
        }}
      />

      <div className="ws-term" style={{ height: layout.term }}>
        <Terminal
          stdout={result?.stdout ?? ""}
          stderr={result?.stderr ?? ""}
          exitCode={hasRun && result ? result.exit_code : null}
          ran={hasRun}
          running={running}
          onRun={onRun}
        />
      </div>

      {progressOpen && progress ? (
        <ProgressPanel
          progress={progress}
          session={session}
          onClose={() => setProgressOpen(false)}
          onGotoClass={(id) => {
            setProgressOpen(false);
            void jumpTo({ class_id: id, lesson_number: 1 });
          }}
        />
      ) : null}
    </div>
  );
}
