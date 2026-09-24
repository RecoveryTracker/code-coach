import type {
  CheckAnswerResult,
  ConceptTopic,
  CssCheck,
  CssList,
  DrillEvaluateResult,
  MagnetCheck,
  MagnetList,
  MarkupCheck,
  MarkupList,
  SessionQueue,
  TraceCheck,
  TraceList,
  ErrorCheck,
  ErrorList,
  ExplainResult,
  KataCheck,
  KataList,
  LanguageInfo,
  LessonEntry,
  PredictCheck,
  PredictList,
  PracticeMode,
  PracticeSession,
  ProgressInfo,
  ReferenceSheet,
  SkillInfo,
  SyntaxHint,
  TypingCatalog,
  TypingCourse,
  TypingDrill,
  TypingGuide,
  TypingRecord,
  TypingRunResult,
  TypingShape,
  BugHuntFix,
  BugHuntList,
  BugHuntStep,
  BugHuntTry,
  CaseAnswer,
  CaseList,
  PuzzleCheck,
  PuzzleList,
  RegexCheck,
  RegexList,
  VisualizeResult,
  WorkbookCheck,
  WorkbookData,
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

/* The three reading screens carry a language picker of their own, so they say
   which language they want rather than relying on the store having caught up
   with the switch that triggered the refetch. */
function withLanguage(path: string, language?: string): string {
  return language ? `${path}?language=${encodeURIComponent(language)}` : path;
}

export function fetchReference(language?: string): Promise<ReferenceSheet> {
  return request(withLanguage("/api/reference", language));
}

export function fetchLessons(language?: string): Promise<LessonEntry[]> {
  return request(withLanguage("/api/lessons", language));
}

export function fetchConcepts(language?: string): Promise<ConceptTopic[]> {
  return request(withLanguage("/api/concepts", language));
}

export function fetchWorkbook(language?: string): Promise<WorkbookData> {
  return request(withLanguage("/api/workbook", language));
}

/** Every kata, grouped by family. */
export function fetchKatas(): Promise<KataList> {
  return request("/api/kata");
}

/** Every predict-the-output puzzle, grouped, without its answer. */
export function fetchPredicts(): Promise<PredictList> {
  return request("/api/predict");
}

/** Send a guess, and get back what it really prints and why. */
export function checkPredict(body: {
  puzzle_id: string;
  guess: string;
}): Promise<PredictCheck> {
  return request("/api/predict/check", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Every CSS quiz, grouped, with the answers left out. */
export function fetchCssQuizzes(): Promise<CssList> {
  return request("/api/css");
}

/** Send a pick, and get back what the browser computed and why. */
export function checkCss(body: {
  quiz_id: string;
  choice: string;
}): Promise<CssCheck> {
  return request("/api/css/check", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** The next things to do, across every practice at once. */
export function fetchSession(size = 20): Promise<SessionQueue> {
  return request(`/api/session?size=${size}`);
}

/** Every traced moment, with the question and without the value. */
export function fetchTraces(): Promise<TraceList> {
  return request("/api/trace");
}

/** Send what you think the variable holds at that moment. */
export function checkTrace(body: {
  trace_id: string;
  answer: string;
}): Promise<TraceCheck> {
  return request("/api/trace/check", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Every crash, with its message and without its answers. */
export function fetchErrors(): Promise<ErrorList> {
  return request("/api/errors");
}

/** Send the line and the reading; both are marked separately. */
export function checkError(body: {
  crash_id: string;
  line: number;
  meaning: string;
}): Promise<ErrorCheck> {
  return request("/api/errors/check", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Every bug hunt: the reports and programs, none of the answers. */
export function fetchBugHunts(): Promise<BugHuntList> {
  return request("/api/bughunt");
}

/** Call the broken program with some arguments; the engine says if the
 *  bug showed. */
export function tryBugHunt(huntId: string, args: string): Promise<BugHuntTry> {
  return request("/api/bughunt/try", {
    method: "POST",
    body: JSON.stringify({ hunt_id: huntId, args }),
  });
}

/** Whether a line is the one the fix changes. Line 0 asks to be shown. */
export function checkBugHuntLine(huntId: string, line: number): Promise<BugHuntStep> {
  return request("/api/bughunt/line", {
    method: "POST",
    body: JSON.stringify({ hunt_id: huntId, line }),
  });
}

/** Whether an explanation is the real cause. Empty asks to be shown. */
export function checkBugHuntCause(huntId: string, cause: string): Promise<BugHuntStep> {
  return request("/api/bughunt/cause", {
    method: "POST",
    body: JSON.stringify({ hunt_id: huntId, cause }),
  });
}

/** Run a fixed program against every case. */
export function fixBugHunt(huntId: string, code: string): Promise<BugHuntFix> {
  return request("/api/bughunt/fix", {
    method: "POST",
    body: JSON.stringify({ hunt_id: huntId, code }),
  });
}

/** The fixed program, asked for rather than shipped with the list. */
export function fetchBugHuntAnswer(huntId: string): Promise<{ code: string }> {
  return request(`/api/bughunt/answer?hunt_id=${encodeURIComponent(huntId)}`);
}

/** Every regex task, both sides of it, and no answers. */
export function fetchRegex(): Promise<RegexList> {
  return request("/api/regex");
}

/** Run a pattern in the real engine of the language picked at the top. */
export function checkRegex(taskId: string, pattern: string, language: string): Promise<RegexCheck> {
  return request("/api/regex/check", {
    method: "POST",
    body: JSON.stringify({ task_id: taskId, pattern, language }),
  });
}

export function fetchRegexAnswer(taskId: string): Promise<{ answer: string }> {
  return request(`/api/regex/answer?task_id=${encodeURIComponent(taskId)}`);
}

/** Every two-part puzzle, with both briefs and no answers. */
export function fetchPuzzles(): Promise<PuzzleList> {
  return request("/api/puzzles");
}

export function checkPuzzle(
  puzzleId: string,
  part: number,
  code: string,
  language: string,
): Promise<PuzzleCheck> {
  return request("/api/puzzles/check", {
    method: "POST",
    body: JSON.stringify({ puzzle_id: puzzleId, part, code, language }),
  });
}

export function fetchPuzzleAnswer(
  puzzleId: string,
  part: number,
  language: string,
): Promise<{ code: string }> {
  const q = new URLSearchParams({ puzzle_id: puzzleId, part: String(part), language });
  return request(`/api/puzzles/answer?${q}`);
}

/** Every SQL case file: story, tables and questions. */
export function fetchCases(): Promise<CaseList> {
  return request("/api/cases");
}

/** Any query against a case's own tables, rolled back afterwards. */
export function queryCase(caseId: string, sql: string): Promise<{ out: string; err: string }> {
  return request("/api/cases/query", {
    method: "POST",
    body: JSON.stringify({ case_id: caseId, sql }),
  });
}

export function answerCase(caseId: string, step: number, answer: string): Promise<CaseAnswer> {
  return request("/api/cases/answer", {
    method: "POST",
    body: JSON.stringify({ case_id: caseId, step, answer }),
  });
}

export function revealCase(caseId: string, step: number): Promise<{ query: string }> {
  const q = new URLSearchParams({ case_id: caseId, step: String(step) });
  return request(`/api/cases/reveal?${q}`);
}

/** Every magnet puzzle, with its lines jumbled afresh by the server. */
export function fetchMagnets(): Promise<MagnetList> {
  return request("/api/magnets");
}

/** Send the arrangement, and have it run. */
export function checkMagnet(body: {
  magnet_id: string;
  lines: string[];
}): Promise<MagnetCheck> {
  return request("/api/magnets/check", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Every HTML and CSS typing drill, grouped. */
export function fetchDrills(): Promise<MarkupList> {
  return request("/api/drills");
}

/** Send what was typed, and find out where it first differs. */
export function checkDrill(body: {
  drill_id: string;
  typed: string;
}): Promise<MarkupCheck> {
  return request("/api/drills/check", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** The worked answer for one kata, fetched only when asked for. */
export function fetchKataAnswer(
  kataId: string,
): Promise<{ id: string; answer: string }> {
  return request(`/api/kata/answer?kata_id=${encodeURIComponent(kataId)}`);
}

/** Run one function against every case it has. */
export function checkKata(body: {
  kata_id: string;
  code: string;
}): Promise<KataCheck> {
  return request("/api/kata/check", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function checkWorkbook(body: {
  page_id: string;
  exercise_id: string;
  code: string;
  language: string;
}): Promise<WorkbookCheck> {
  return request("/api/workbook/check", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Keep what is in the box without running it.
 *
 * Sent shortly after typing stops and again when leaving an exercise, so
 * work survives moving around the workbook whether or not it was ever
 * checked. Failures are deliberately swallowed by the caller: losing a
 * draft save is not worth an error message over the exercise you are
 * still typing.
 */
export function saveWorkbookDraft(body: {
  page_id: string;
  exercise_id: string;
  code: string;
  language: string;
}): Promise<{ saved: boolean }> {
  return request("/api/workbook/draft", {
    method: "POST",
    body: JSON.stringify(body),
  });
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
  /** Trace as this language rather than the one being worked in. */
  language?: string | null;
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
export function fetchTypingShapes(
  theme: string,
): Promise<{ theme: string; shapes: TypingShape[] }> {
  const query = new URLSearchParams({ theme });
  return request(`/api/typing/shapes?${query}`);
}

export function fetchTypingDrill(
  section: string,
  mode: string,
  seed: string,
  theme = "mixed",
  count = 30,
  shape = "",
): Promise<TypingDrill> {
  const query = new URLSearchParams({
    section,
    mode,
    theme,
    seed,
    count: String(count),
  });
  // Left out entirely when empty, so the URL of an ordinary drill is
  // unchanged and nothing downstream has to treat "" as a value.
  if (shape) query.set("shape", shape);
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
