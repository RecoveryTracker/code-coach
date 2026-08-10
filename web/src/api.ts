import type {
  CheckAnswerResult,
  DrillEvaluateResult,
  ExplainResult,
  PracticeMode,
  PracticeSession,
  ProgressInfo,
  SkillInfo,
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

export function fetchProgress(): Promise<ProgressInfo> {
  return request("/api/progress");
}

export function updateProgress(body: {
  mode?: PracticeMode;
  coach_level?: number;
  difficulty?: number;
  selected_skills?: string[];
  dictation_level?: number;
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
