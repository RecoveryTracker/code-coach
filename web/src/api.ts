import type {
  CheckAnswerResult,
  DrillEvaluateResult,
  ExplainResult,
  LanguageInfo,
  LessonEntry,
  PracticeMode,
  PracticeSession,
  ProgressInfo,
  ReferenceSheet,
  SyntaxHint,
  SkillInfo,
  TypingCatalog,
  TypingCourse,
  TypingDrill,
  TypingGuide,
  TypingRecord,
  TypingRunResult,
  VisualizeResult,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function fetchSkills(): Promise<SkillInfo[]> {
  return request("/api/skills");
}

export function fetchLanguages(): Promise<LanguageInfo[]> {
  return request("/api/languages");
}

export function fetchProgress(): Promise<ProgressInfo> {
  return request("/api/progress");
}

export function updateProgress(body: {
  mode?: PracticeMode;
  coach_level?: number;
  difficulty?: number;
  selected_skills?: string[];
  dictation_level?: number;
  language?: string;
}): Promise<ProgressInfo> {
  return request("/api/progress", {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

/** Change Foundations type-along difficulty (1–5) and load a fresh window. */
export async function setDictationLevel(
  level: number,
): Promise<PracticeSession> {
  await updateProgress({ dictation_level: level });
  return fetchCurrentPractice();
}

export function fetchCurrentPractice(): Promise<PracticeSession> {
  return request("/api/practice/current");
}

/** Reminders about code that won't run. Empty when there's nothing to say. */
export function fetchHints(
  code: string,
  language: string,
): Promise<{ hints: SyntaxHint[] }> {
  return request("/api/hints", {
    method: "POST",
    body: JSON.stringify({ code, language }),
  });
}

/** Open the type-along for one problem, from a lesson. */
export function gotoProblem(
  patternId: string,
  problemNumber: number,
): Promise<PracticeSession> {
  return request("/api/practice/goto-problem", {
    method: "POST",
    body: JSON.stringify({
      pattern_id: patternId,
      problem_number: problemNumber,
    }),
  });
}

export function fetchReference(): Promise<ReferenceSheet> {
  return request("/api/reference");
}

export function fetchLessons(): Promise<LessonEntry[]> {
  return request("/api/lessons");
}

export function fetchNextPractice(): Promise<PracticeSession> {
  return request("/api/practice/next", { method: "POST", body: "{}" });
}

export function evaluateDrill(
  drillId: string,
  code: string,
  run: boolean,
  exerciseIndex?: number,
): Promise<DrillEvaluateResult> {
  return request("/api/practice/evaluate", {
    method: "POST",
    body: JSON.stringify({
      drill_id: drillId,
      code,
      run,
      exercise_index: exerciseIndex ?? null,
    }),
  });
}

export function completeAndNext(
  drillId: string,
  code: string,
): Promise<PracticeSession> {
  return request("/api/practice/complete", {
    method: "POST",
    body: JSON.stringify({ drill_id: drillId, code, run: false }),
  });
}

/** Another Lesson 1 type-along set (endless practice). */
export function fetchMoreLines(): Promise<PracticeSession> {
  return request("/api/practice/more", { method: "POST", body: "{}" });
}

export function gotoLesson(
  lessonNumber?: number,
  classId?: string,
): Promise<PracticeSession> {
  return request("/api/practice/goto-lesson", {
    method: "POST",
    body: JSON.stringify({
      lesson_number: lessonNumber ?? null,
      class_id: classId ?? null,
    }),
  });
}

export function navigateCurriculum(body: {
  class_id?: string;
  lesson_number?: number;
  class_delta?: number;
  lesson_delta?: number;
}): Promise<PracticeSession> {
  return request("/api/practice/navigate", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function startReview(skillId: string): Promise<PracticeSession> {
  return request("/api/practice/review", {
    method: "POST",
    body: JSON.stringify({ skill_id: skillId }),
  });
}

export function backFromReview(): Promise<PracticeSession> {
  return request("/api/practice/back", { method: "POST", body: "{}" });
}

/** Step-through picture of the data while the code runs. */
export function visualizeCode(body: {
  code: string;
  call?: string;
  pattern_id?: string | null;
  problem_number?: number | null;
}): Promise<VisualizeResult> {
  return request("/api/visualize", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Diff your own attempt against a problem's real solution. */
export function checkAnswer(body: {
  code: string;
  pattern_id: string;
  problem_number: number;
}): Promise<CheckAnswerResult> {
  return request("/api/practice/check-answer", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Typing sections, their modes, and the keyboard layout to draw. */
export function fetchTypingCatalog(): Promise<TypingCatalog> {
  return request("/api/typing/catalog");
}

/** One generated run. The seed varies the draw, so "again" isn't a repeat. */
export function fetchTypingDrill(
  section: string,
  mode: string,
  seed: string,
  theme = "mixed",
  count = 30,
): Promise<TypingDrill> {
  const query = new URLSearchParams({
    section,
    mode,
    theme,
    seed,
    count: String(count),
  });
  return request(`/api/typing/drill?${query}`);
}

/** The numbered course, with progress folded in. */
export function fetchTypingCourse(): Promise<TypingCourse> {
  return request("/api/typing/course");
}

/** Finger assignments, technique notes and the FAQ. */
export function fetchTypingGuide(): Promise<TypingGuide> {
  return request("/api/typing/guide");
}

/** Personal bests for every section and mode you've finished. */
export function fetchTypingRecords(): Promise<TypingRecord[]> {
  return request("/api/typing/records");
}

/** Submit a finished run; the reply says which bests it beat. */
export function submitTypingRun(body: {
  section: string;
  mode: string;
  wpm: number;
  accuracy: number;
  reaction_ms: number;
  streak: number;
  keystrokes: number;
}): Promise<TypingRunResult> {
  return request("/api/typing/records", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function chatWithCoach(message: string): Promise<{ reply: string }> {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

/** Plain-English walkthrough of the current editor code. */
export function explainCode(code: string): Promise<ExplainResult> {
  return request("/api/explain", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}
