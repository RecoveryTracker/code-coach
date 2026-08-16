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
import { LanguagePicker } from "./components/LanguagePicker";
import { ProgressPanel } from "./components/ProgressPanel";
import { ScriptLibrary } from "./components/ScriptLibrary";
import { StudyPanel } from "./components/StudyPanel";
import { Terminal } from "./components/Terminal";
import { TypeTarget } from "./components/TypeTarget";
import type {
  DrillEvaluateResult,
  PracticeSession,
  ProgressInfo,
} from "./types";

const DEBOUNCE_MS = 180;

/**
 * Every exercise gets its own buffer.
 *
 * The drill id alone isn't enough: it's shared by all exercises in a lesson,
 * and it stays the same across difficulties (a class's Lesson 1 is `<class>-l1`
 * at every level), so both used to spill their code into each other.
 */
type DraftSlot = { drillId: string; index: number; level: number };

function draftKey({ drillId, index, level }: DraftSlot) {
  return `code-coach:drill:${drillId}:lv${level}:ex${index}`;
}

/** Pre-per-exercise key: one shared buffer for a whole lesson. */
function legacyDraftKey(drillId: string) {
  return `code-coach:drill:${drillId}`;
}

function loadDraft(slot: DraftSlot): string | null {
  try {
    const found = localStorage.getItem(draftKey(slot));
    if (found != null) return found;
    // Work saved before drafts were split per exercise/difficulty lives under
    // the old lesson-wide key. Adopt it for the first exercise rather than
    // silently losing it; the original is left in place as a backstop.
    if (slot.index === 0) {
      return localStorage.getItem(legacyDraftKey(slot.drillId));
    }
    return null;
  } catch {
    return null;
  }
}

function saveDraft(slot: DraftSlot, code: string) {
  try {
    localStorage.setItem(draftKey(slot), code);
  } catch {
    /* ignore */
  }
}

/**
 * Where you were in a lesson, so coming back doesn't dump you on exercise 1
 * looking at a blank editor while your work sits in a slot you can't see.
 */
function posKey(drillId: string, level: number) {
  return `code-coach:pos:${drillId}:lv${level}`;
}

function savePos(drillId: string, level: number, index: number) {
  try {
    localStorage.setItem(posKey(drillId, level), String(index));
  } catch {
    /* ignore */
  }
}

function loadPos(drillId: string, level: number): number | null {
  try {
    const raw = localStorage.getItem(posKey(drillId, level));
    if (raw == null) return null;
    const n = Number.parseInt(raw, 10);
    return Number.isFinite(n) && n >= 0 ? n : null;
  } catch {
    return null;
  }
}

function clearDraft(slot: DraftSlot) {
  try {
    localStorage.removeItem(draftKey(slot));
  } catch {
    /* ignore */
  }
}

/**
 * Every saved editor buffer, everywhere. Only reachable from the Progress
 * panel behind a confirmation — it destroys work you can't see from where you
 * click. Deliberately leaves saved scripts and the free-mode buffer alone.
 */
function clearAllDrafts() {
  try {
    const doomed: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && (k.startsWith("code-coach:drill:") || k.startsWith("code-coach:pos:"))) {
        doomed.push(k);
      }
    }
    doomed.forEach((k) => localStorage.removeItem(k));
  } catch {
    /* ignore */
  }
}

/**
 * term  — terminal height
 * sideW — right column width (wide layout) / sideH — its height when stacked
 * ttH   — "Type this" height inside the right column; the rest is the problem
 */
type Layout = {
  term: number;
  sideW: number;
  sideH: number;
  ttH: number;
  /** "Explain my code" panel — it lives in the auto-sized coach strip, so
   *  without a fixed height it pushes the editor down as it fills. */
  explainH: number;
  /** The green/red coach message box. Fixed so it can't shove the editor;
   *  draggable so it can be a single line when you don't want the room. */
  msgH: number;
  /** "Watch it run" — diagrams need more room than prose, and how much
   *  depends on the structure, so it's yours to set. */
  vizH: number;
  /** Message box collapsed to a single line. The nav still shows the
   *  correct/wrong headline, so nothing is lost by folding it away. */
  msgCollapsed: boolean;
};

const DEFAULT_LAYOUT: Layout = {
  term: 140,
  sideW: 430,
  sideH: 300,
  ttH: 240,
  explainH: 200,
  // 64px ≈ three lines: enough for the usual "line N doesn't match / should
  // be / you typed" without reserving space that's normally empty.
  msgH: 64,
  vizH: 260,
  msgCollapsed: false,
};

/** Every pane keeps at least this much, so a drag can never hide one. */
const MIN_PANE = 90;
const MIN_EDITOR = 280;
/** Editor + right column together never shrink below this. */
const MIN_WORK = 320;
/**
 * …except when you're deliberately dragging a top panel bigger. Reserving the
 * full MIN_WORK left the explain panel a ceiling of ~120px, so it could never
 * be opened up enough to read. Expanding it is an explicit act — let the work
 * area yield down to this instead.
 */
const MIN_WORK_YIELD = 170;

function loadLayout(): Layout {
  try {
    const raw = localStorage.getItem("code-coach:workspace-layout-v5");
    if (raw) {
      const p = JSON.parse(raw) as Partial<Layout>;
      return { ...DEFAULT_LAYOUT, ...p };
    }
  } catch {
    /* ignore */
  }
  return DEFAULT_LAYOUT;
}

function clampNum(v: number, lo: number, hi: number): number {
  // hi can fall below lo on very small windows — lo wins, nothing collapses.
  return Math.max(lo, Math.min(v, Math.max(lo, hi)));
}

/** Matches the .ws-work stacking breakpoint in workspace.css. */
function isStacked(): boolean {
  return window.matchMedia("(max-width: 1050px)").matches;
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
  /** Difficulty the current buffers belong to — part of the draft key. */
  const levelRef = useRef(1);

  /** The slot the editor is currently showing. */
  const slotNow = useCallback(
    (index?: number): DraftSlot => ({
      drillId: drillRef.current ?? "",
      index: index ?? exerciseIndexRef.current,
      level: levelRef.current,
    }),
    [],
  );
  const evalSeq = useRef(0);
  const debounce = useRef<number | null>(null);
  const shellRef = useRef<HTMLDivElement | null>(null);
  const workRef = useRef<HTMLDivElement | null>(null);
  const sideRef = useRef<HTMLDivElement | null>(null);
  const drag = useRef<
    "term" | "side" | "tt" | "explain" | "msg" | "viz" | null
  >(null);
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
      levelRef.current = s.dictation_level ?? 1;

      // Resume where this lesson was left off. A fresh endless window
      // (preserveCode) and Start over (forceClean) both belong at the top.
      let startIndex = 0;
      if (preserveCode == null && !forceClean) {
        const saved = loadPos(s.drill_id, levelRef.current);
        if (saved != null) {
          startIndex = Math.max(0, Math.min(saved, s.steps.length - 1));
        }
      }

      setExerciseIndex(startIndex);
      exerciseIndexRef.current = startIndex;
      setExerciseDone(false);
      if (autoAdvanceTimer.current) {
        window.clearTimeout(autoAdvanceTimer.current);
        autoAdvanceTimer.current = null;
      }

      const slot: DraftSlot = {
        drillId: s.drill_id,
        index: startIndex,
        level: levelRef.current,
      };

      let initial = s.starter;
      if (preserveCode != null) {
        // Keep what the user already typed (next endless window)
        initial = preserveCode;
        saveDraft(slot, preserveCode);
      } else if (forceClean) {
        // Only this exercise. Clearing the whole lesson from here would throw
        // away work on every other exercise in it.
        clearDraft(slot);
        initial = s.starter;
      } else {
        const draft = loadDraft(slot);
        if (draft != null && draft !== "") {
          initial = draft;
        }
      }

      codeRef.current = initial;
      setSeedCode(initial);
      setEditorRevision((n) => n + 1);
      setHasRun(false);
      setResult(null);
      await score(s.drill_id, initial, false, startIndex);
    },
    [score],
  );

  const loadSessionRef = useRef(loadSession);
  loadSessionRef.current = loadSession;

  /**
   * Move to another exercise in the same lesson: bank the current buffer under
   * its own slot, then show whatever that exercise had (or a blank starter).
   */
  const goToExercise = useCallback(
    (next: number, starter: string) => {
      saveDraft(slotNow(), codeRef.current);

      const incoming = loadDraft(slotNow(next));
      const text = incoming ?? starter;

      exerciseIndexRef.current = next;
      setExerciseIndex(next);
      setExerciseDone(false);
      codeRef.current = text;
      setSeedCode(text);
      setEditorRevision((n) => n + 1);

      const id = drillRef.current;
      if (id) {
        savePos(id, levelRef.current, next);
        void score(id, text, false, next);
      }
    },
    [score, slotNow],
  );

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

    goToExercise(next, session.starter);
  }, [session, goToExercise]);

  // No auto-advance. A correct answer lights up Continue and waits there, so
  // the finished code stays on screen to be read.

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
        saveDraft(slotNow(), codeRef.current);
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
    saveDraft(slotNow(), codeRef.current);
    void score(id, codeRef.current, true);
  }, [score, slotNow]);

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
      if (drillRef.current) saveDraft(slotNow(), codeRef.current);
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
        // Bank this level's work under its own slot, then let loadSession pull
        // up whatever that difficulty had. Carrying the buffer across meant a
        // level-1 single line sat in the editor when level 5 asked for a whole
        // function.
        saveDraft(slotNow(), codeRef.current);
        const s = await setDictationLevel(level);
        await loadSession(s, false);
      } catch {
        /* stay */
      }
    },
    [loadSession, slotNow],
  );

  /**
   * The class one step either side of the current one, or null at the ends.
   * Used to carry the *same lesson* across a class boundary.
   */
  const adjacentClass = useCallback(
    (delta: number): string | null => {
      const list = session?.curriculum ?? [];
      const here = list.findIndex((c) => c.id === session?.class_id);
      if (here < 0) return null;
      const target = list[here + delta];
      return target ? target.id : null;
    },
    [session],
  );

  /**
   * Stepping exercises never changes what kind of practice you're doing.
   *
   * Running off either end moves to the next/previous CLASS at the same lesson
   * number — type-along stays type-along, build-from-memory stays
   * build-from-memory. It used to roll into the next lesson of the same class,
   * which silently switched you from typing to building mid-flow.
   */
  const onExerciseDelta = useCallback(
    (d: number) => {
      if (!session) return;
      const total = session.steps.length;
      const next = exerciseIndexRef.current + d;
      const lesson = session.lesson_number ?? 1;

      if (next < 0) {
        const prev = adjacentClass(-1);
        if (prev) void jumpTo({ class_id: prev, lesson_number: lesson });
        return;
      }

      if (next >= total) {
        // An endless type-along has more of its own material — load the next
        // window rather than leaving the class.
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
        const following = adjacentClass(1);
        if (following) void jumpTo({ class_id: following, lesson_number: lesson });
        return;
      }

      goToExercise(next, session.starter);
    },
    [session, goToExercise, jumpTo, adjacentClass],
  );

  const onReview = useCallback(
    async (skillId: string) => {
      try {
        if (skillId === "lesson1" && session?.class_id) {
          await jumpTo({ class_id: session.class_id, lesson_number: 1 });
          return;
        }
        // Keep the main lesson's work before detouring into review practice.
        if (drillRef.current) saveDraft(slotNow(), codeRef.current);
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
    if (drillRef.current) saveDraft(slotNow(), codeRef.current);
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

  /**
   * Clamp every stored size against what's actually on screen right now.
   *
   * The terminal's ceiling is measured, not guessed: the header and coach
   * strip are `auto` rows, so a hardcoded reserve let the terminal squeeze the
   * work area down to ~100px and crush the study panel to a sliver.
   */
  const clampLayout = useCallback((L: Layout): Layout => {
    const shell = shellRef.current?.getBoundingClientRect();
    const work = workRef.current?.getBoundingClientRect();
    const side = sideRef.current?.getBoundingClientRect();
    const next = { ...L };

    if (shell) {
      // Everything above the work area (header + coach strip) plus the
      // work area's own floor is off-limits to the terminal.
      const chrome = work ? work.top - shell.top : 120;
      next.term = clampNum(L.term, 80, shell.height - chrome - MIN_WORK - 6);

      // The explain and message panels sit inside that chrome, so each one's
      // ceiling is whatever is left once the rest of the strip, the terminal
      // and a (reduced) work floor have taken their share.
      const room = (el: Element | null, floor: number) => {
        const own = el ? el.getBoundingClientRect().height : 0;
        return shell.height - (chrome - own) - MIN_WORK_YIELD - next.term - 6 - floor;
      };

      // Fixed range, deliberately NOT measured against remaining space: this
      // is a stored preference, and squeezing it on every reflow would
      // overwrite the size you chose. The explain clamp below measures real
      // chrome (which includes this box), so the work floor is still safe.
      next.msgH = clampNum(L.msgH, 26, 260);

      const explainEl = document.querySelector(".coach-explain");
      if (explainEl) {
        next.explainH = clampNum(L.explainH, 90, room(explainEl, 0));
      }
      const vizEl = document.querySelector(".coach-viz");
      if (vizEl) {
        next.vizH = clampNum(L.vizH, 120, room(vizEl, 0));
      }
    }
    if (work) {
      if (isStacked()) {
        next.sideH = clampNum(L.sideH, MIN_PANE * 2, work.height - MIN_PANE - 6);
      } else {
        next.sideW = clampNum(L.sideW, 260, work.width - MIN_EDITOR - 6);
      }
    }
    // Side height follows from the two above, so clamp ttH against the space
    // the side column will actually have, not the space it has this frame.
    const sideH = isStacked() ? next.sideH : (work?.height ?? side?.height ?? 0);
    if (sideH > 0) {
      next.ttH = clampNum(L.ttH, MIN_PANE, sideH - MIN_PANE - 6);
    }
    return next;
  }, []);

  const sameLayout = (a: Layout, b: Layout) =>
    a.term === b.term &&
    a.sideW === b.sideW &&
    a.sideH === b.sideH &&
    a.ttH === b.ttH &&
    a.explainH === b.explainH &&
    a.msgH === b.msgH &&
    a.vizH === b.vizH &&
    a.msgCollapsed === b.msgCollapsed;

  useEffect(() => {
    const move = (e: PointerEvent) => {
      if (!drag.current || !shellRef.current) return;
      const shell = shellRef.current.getBoundingClientRect();
      const work = workRef.current?.getBoundingClientRect();
      const side = sideRef.current?.getBoundingClientRect();

      setLayout((L) => {
        let raw = L;
        if (drag.current === "term") {
          raw = { ...L, term: shell.bottom - e.clientY };
        } else if (drag.current === "side" && work) {
          raw = isStacked()
            ? { ...L, sideH: work.bottom - e.clientY }
            : { ...L, sideW: work.right - e.clientX };
        } else if (drag.current === "tt" && side) {
          raw = { ...L, ttH: e.clientY - side.top };
        } else if (drag.current === "explain") {
          const box = document.querySelector(".coach-explain");
          if (box) {
            raw = { ...L, explainH: e.clientY - box.getBoundingClientRect().top };
          }
        } else if (drag.current === "msg") {
          const box = document.querySelector(".coach-msg");
          if (box) {
            raw = { ...L, msgH: e.clientY - box.getBoundingClientRect().top };
          }
        } else if (drag.current === "viz") {
          const box = document.querySelector(".coach-viz");
          if (box) {
            raw = { ...L, vizH: e.clientY - box.getBoundingClientRect().top };
          }
        }
        const next = clampLayout(raw);
        return sameLayout(next, L) ? L : next;
      });
    };
    const up = () => {
      if (!drag.current) return;
      drag.current = null;
      document.body.classList.remove("is-resizing");
      try {
        localStorage.setItem(
          "code-coach:workspace-layout-v5",
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
  }, [layout, clampLayout]);

  // Shrinking the window (or switching to the stacked layout) can leave a
  // stored size larger than the space that's left.
  useEffect(() => {
    const reclamp = () =>
      setLayout((L) => {
        const next = clampLayout(L);
        return sameLayout(next, L) ? L : next;
      });
    reclamp();
    window.addEventListener("resize", reclamp);
    return () => window.removeEventListener("resize", reclamp);
  }, [ready, freeMode, clampLayout]);

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

  /**
   * Clear the editor for the exercise you're looking at — nothing else.
   * It deliberately doesn't touch the other exercises' buffers or move you off
   * this one: a button on the main toolbar shouldn't be able to destroy work
   * you can't currently see.
   */
  const onStartOver = () => {
    if (!session) return;
    clearDraft(slotNow());
    const blank = session.starter;
    codeRef.current = blank;
    setSeedCode(blank);
    setEditorRevision((n) => n + 1);
    setExerciseDone(false);
    setHasRun(false);
    setResult(null);
    const id = drillRef.current;
    if (id) void score(id, blank, false, exerciseIndexRef.current);
  };

  // App-level actions. These used to own a whole 44px header row of their own;
  // they now ride along on the coach line, which buys that height back for the
  // editor.
  const toolbar = (
    <div className="ws-top-actions">
      <LanguagePicker
        current={session?.language ?? "python"}
        onChanged={() => {
          // Reload the session so drills, starter and editor mode all come
          // back in the new language.
          void (async () => {
            try {
              await loadSession(await fetchCurrentPractice(), false);
            } catch {
              /* stay */
            }
          })();
        }}
      />
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
            saveDraft(slotNow(), code);
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
          onClick={onStartOver}
          title="Clear the editor for this exercise only — your other exercises are untouched"
        >
          Clear editor
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
  );

  const brand = <span className="ws-brand-inline">Code Coach</span>;

  return (
    <div
      className="ws-shell ws-shell-stack"
      ref={shellRef}
      style={
        {
          "--term-h": `${layout.term}px`,
          "--side-w": `${layout.sideW}px`,
          "--side-h": `${layout.sideH}px`,
          "--tt-h": `${layout.ttH}px`,
          "--explain-h": `${layout.explainH}px`,
          "--msg-h": `${layout.msgCollapsed ? 26 : layout.msgH}px`,
          "--viz-h": `${layout.vizH}px`,
        } as CSSProperties
      }
    >
      {/* Coach strip — hidden in free mode. The app toolbar rides on its
          first line instead of owning a header row. */}
      {freeMode ? (
        <div className="coach-banner free-banner">
          <div className="cur-nav-line">
            <span className="coach-banner-done">
              Free mode — code anything. Use <strong>Save</strong> /{" "}
              <strong>Load…</strong> for your scripts.{" "}
              <strong>Coach on</strong> returns to practice.
            </span>
            {brand}
            {toolbar}
          </div>
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
          onContinue={advanceExercise}
          onExplainDragStart={() => {
            drag.current = "explain";
            document.body.classList.add("is-resizing");
          }}
          onMsgDragStart={() => {
            if (layout.msgCollapsed) return;
            drag.current = "msg";
            document.body.classList.add("is-resizing");
          }}
          msgCollapsed={layout.msgCollapsed}
          onToggleMsg={() =>
            setLayout((L) => {
              const next = { ...L, msgCollapsed: !L.msgCollapsed };
              try {
                localStorage.setItem(
                  "code-coach:workspace-layout-v5",
                  JSON.stringify(next),
                );
              } catch {
                /* ignore */
              }
              return next;
            })
          }
          onVizDragStart={() => {
            drag.current = "viz";
            document.body.classList.add("is-resizing");
          }}
          onBackFromReview={onBackFromReview}
          watching={watching}
          getCode={() => codeRef.current}
          brand={brand}
          toolbar={toolbar}
        />
      )}

      {/* Editor left, code-to-type right. Stacks below ~1050px so the
          target block never squeezes the editor into a gutter. */}
      <div className={`ws-work${freeMode ? " solo" : ""}`} ref={workRef}>
        <div className="ws-editor">
          <EditorPane
            code={seedCode}
            revision={editorRevision}
            onChange={onChange}
            onRun={onRun}
            language={session.editor_language ?? "python"}
            fileName={`practice.${
              session.language === "dart" ? "dart" : "py"
            }`}
          />
        </div>
        {!freeMode ? (
          <>
            <div
              className="ws-split-col"
              onPointerDown={(e) => {
                e.preventDefault();
                drag.current = "side";
                document.body.classList.add("is-resizing");
              }}
            />
            {/* Right column: what to type on top, the problem it comes from
                below, with a divider you can slide between them. */}
            <div className="ws-side" ref={sideRef}>
              <TypeTarget
                session={session}
                result={result}
                exerciseIndex={exerciseIndex}
                onReview={onReview}
                onDictationLevel={(n) => void onDictationLevel(n)}
              />
              <div
                className="ws-split-side"
                onPointerDown={(e) => {
                  e.preventDefault();
                  drag.current = "tt";
                  document.body.classList.add("is-resizing");
                }}
              />
              <StudyPanel
                study={session.steps[exerciseIndex]?.study ?? null}
                getCode={() => codeRef.current}
              />
            </div>
          </>
        ) : null}
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
          onClearAll={() => {
            clearAllDrafts();
            if (session) void loadSession(session, true);
          }}
        />
      ) : null}
    </div>
  );
}

