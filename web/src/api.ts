import type { BrainItem, BrainSummary } from "./components/BrainDrills";
import type { AwardResult } from "./lib/momentumView";
import type {
  GotchaAnswer,
  GotchaCard,
  GotchaLang,
  GotchaRun,
  GotchaSummary,
  GotchaUserCard,
  GotchaUserResult,
} from "./lib/gotchas";
import type {
  FarmOverview,
  FarmTip,
  FarmStart,
  FarmState,
  CanvasCheck,
  CanvasList,
  PyFrame,
  PyEvent,
  PyStart,
  PyWebResponse,
  PyWebSend,
  PyWebStart,
  CheckAnswerResult,
  ConceptTopic,
  CssCheck,
  CssList,
  DrillEvaluateResult,
  MagnetCheck,
  MagnetList,
  MarkupCheck,
  MarkupList,
  FlutterCheck,
  FlutterList,
  SessionHistory,
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

/** The API restarts itself whenever a source file changes, which takes a second
 *  or two; a read that lands in that gap would show an error for something that
 *  works a moment later. Reads are safe to repeat, so they wait it out. */
const READ_RETRIES = 5;
const READ_RETRY_MS = 400;

/** The same read asked for twice at once (a screen mounting twice, two effects
 *  wanting the same list) shares one trip. The workbook alone is 4 MB, and
 *  fetching it twice side by side made each slower than one alone. */
const readsInFlight = new Map<string, Promise<unknown>>();

function request<T>(path: string, init?: RequestInit): Promise<T> {
  const isRead = !init?.method || init.method.toUpperCase() === "GET";
  if (!isRead) return send<T>(path, init, false);
  const shared = readsInFlight.get(path);
  if (shared) return shared as Promise<T>;
  const trip = send<T>(path, init, true).finally(() => readsInFlight.delete(path));
  readsInFlight.set(path, trip);
  return trip;
}

async function send<T>(path: string, init: RequestInit | undefined, isRead: boolean): Promise<T> {
  for (let attempt = 0; ; attempt += 1) {
    let res: Response | null = null;
    try {
      res = await fetch(path, {
        headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
        ...init,
      });
    } catch (e) {
      if (!isRead || attempt >= READ_RETRIES) throw e;
    }
    if (res && res.ok) return res.json() as Promise<T>;
    if (res && (!isRead || res.status < 500 || attempt >= READ_RETRIES)) {
      const text = await res.text();
      throw new Error(text || `${res.status} ${res.statusText}`);
    }
    await new Promise((done) => window.setTimeout(done, READ_RETRY_MS));
  }
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

/** Brain Drills' home: activities, bests, stamps and code ages. */
export function fetchBrain(language = "javascript"): Promise<BrainSummary> {
  return request(`/api/brain?language=${encodeURIComponent(language)}`);
}

/** A fresh round of one Brain Drills activity. */
export function fetchBrainRound(
  activity: string,
  language = "javascript",
): Promise<{ activity: string; items: BrainItem[] }> {
  return request(
    `/api/brain/round?activity=${encodeURIComponent(activity)}&language=${encodeURIComponent(language)}`,
  );
}

/** Keep a finished round; its code age, and whether it beat the best. */
export function postBrainResult(body: {
  activity: string;
  seconds: number;
  errors: number;
  total: number;
  checkId: string;
  language: string;
}): Promise<{ age: number; best: boolean }> {
  return request("/api/brain/result", { method: "POST", body: JSON.stringify(body) });
}

/** The farm when its screen opens. */
export function fetchFarm(): Promise<FarmOverview> {
  return request("/api/farm");
}

/**
 * Take today's welcome-back XP. The pay is the server's: it checks the farm really was opened
 * after an absence, and pays once a day. `ok` false with a `reason` means nothing was paid.
 */
export function claimFarmWelcome(): Promise<AwardResult & { reason?: string }> {
  return request("/api/farm/welcome/claim", { method: "POST", body: "{}" });
}

/** The farm now, with the output since line `since`. */
export function fetchFarmState(since: number): Promise<FarmState> {
  return request(`/api/farm/state?since=${since}`);
}

/** Check a program against what is unlocked, and start it. */
export function runFarm(language: string, code: string, file = ""): Promise<FarmStart> {
  return request("/api/farm/run", { method: "POST", body: JSON.stringify({ language, code, file }) });
}

/**
 * Add, rename, delete or select one of a language's files; answers with the whole farm.
 * Each language has its own farm, so this also takes you to that language's farm: the answer
 * is that farm's overview.
 */
export function farmFile(
  language: string,
  action: "add" | "rename" | "delete" | "select",
  name: string,
  newName = "",
): Promise<FarmOverview & { ok: boolean; error?: string }> {
  return request("/api/farm/file", {
    method: "POST",
    body: JSON.stringify({ language, action, name, new_name: newName }),
  });
}

export function stopFarm(): Promise<{ ok: boolean }> {
  return request("/api/farm/stop", { method: "POST", body: "{}" });
}

/** Keep what is written in a language, without running it. `ok` is false if it was refused
 * (a program is running on another language's farm). */
export function keepFarmCode(language: string, code: string, file = ""): Promise<{ ok: boolean }> {
  return request("/api/farm/code", { method: "POST", body: JSON.stringify({ language, code, file }) });
}

/** Buy the next level of a piece of research; answers with the whole farm. */
export function buyFarmUnlock(name: string): Promise<FarmOverview & { ok: boolean }> {
  return request("/api/farm/unlock", { method: "POST", body: JSON.stringify({ name }) });
}

export function setFarmWarp(warp: number): Promise<{ ok: boolean }> {
  return request("/api/farm/warp", { method: "POST", body: JSON.stringify({ warp }) });
}

/** The Playbook: tips and snippets for the farm. */
export function fetchFarmPlaybook(): Promise<{ entries: FarmTip[] }> {
  return request("/api/farm/playbook");
}

/** Start the farm over: one square of grass, nothing in the barn. */
export function resetFarm(): Promise<FarmOverview> {
  return request("/api/farm/reset", { method: "POST", body: "{}" });
}

/** Every Canvas step, and the harness the preview loads first. */
export function fetchCanvas(): Promise<CanvasList> {
  return request("/api/canvas");
}

/** Play the program in node and run the step's check against it. */
export function checkCanvas(step_id: string, code: string): Promise<CanvasCheck> {
  return request("/api/canvas/check", {
    method: "POST",
    body: JSON.stringify({ step_id, code }),
  });
}

/** One step's finished program - asked for, not shipped with the list. */
export function fetchCanvasAnswer(step_id: string): Promise<{ id: string; solution: string }> {
  return request(`/api/canvas/answer?step_id=${encodeURIComponent(step_id)}`);
}

/**
 * A To-do step's page, built around your code: the preview's ("play"),
 * starting from the localStorage it had, or the hidden one a check plays.
 */
export function fetchCanvasPage(
  step_id: string,
  code: string,
  mode: "play" | "check",
  storage: Record<string, string> = {},
): Promise<{ page: string }> {
  return request("/api/canvas/page", {
    method: "POST",
    body: JSON.stringify({ step_id, code, mode, storage }),
  });
}

/** Run a Python step's program on the server; the first draw calls and its session. */
export function startPyCanvas(step_id: string, code: string): Promise<PyStart> {
  return request("/api/pycanvas/start", {
    method: "POST",
    body: JSON.stringify({ step_id, code }),
  });
}

/** Run the next frame of a Python session: the keys held, and what happened since the last. */
export function stepPyCanvas(
  session: string,
  dt: number,
  keys: string[],
  events: PyEvent[],
): Promise<PyFrame> {
  return request("/api/pycanvas/step", {
    method: "POST",
    body: JSON.stringify({ session, frames: 1, dt, keys, events }),
  });
}

/** End a Python session. `keepalive` lets it finish while the page is going away. */
export function stopPyCanvas(session: string): void {
  void fetch("/api/pycanvas/stop", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session }),
    keepalive: true,
  }).catch(() => {
    /* best effort: the server also ends an idle session by itself */
  });
}

/** Run a Web (Python) step's app on the server; its session, routes and the first console lines. */
export function startPyWeb(step_id: string, code: string): Promise<PyWebStart> {
  return request("/api/pyweb/start", {
    method: "POST",
    body: JSON.stringify({ step_id, code }),
  });
}

/** Make one request to a running app. It comes back as the app answered, whatever the status. */
export function requestPyWeb(session: string, send: PyWebSend): Promise<PyWebResponse> {
  return request("/api/pyweb/request", {
    method: "POST",
    body: JSON.stringify({ session, ...send }),
  });
}

/** End a web session. `keepalive` lets it finish while the page is going away. */
export function stopPyWeb(session: string): void {
  void fetch("/api/pyweb/stop", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session }),
    keepalive: true,
  }).catch(() => {
    /* best effort: the server also ends an idle session by itself */
  });
}

/** Count a pass the browser saw, for a step checked in the browser. */
export function recordCanvasPass(step_id: string): Promise<CanvasCheck> {
  return request("/api/canvas/passed", {
    method: "POST",
    body: JSON.stringify({ step_id }),
  });
}

/** Every Flutter question, with its choices and without its answer. */
export function fetchFlutter(): Promise<FlutterList> {
  return request("/api/flutter");
}

/** Send the choice picked for one Flutter question. */
export function checkFlutter(question_id: string, answer: string): Promise<FlutterCheck> {
  return request("/api/flutter/check", {
    method: "POST",
    body: JSON.stringify({ question_id, answer }),
  });
}

/** What has been done, what has not, and what is due for a refresh. */
export function fetchSessionHistory(refreshDays = 7): Promise<SessionHistory> {
  return request(`/api/session/history?refresh_days=${refreshDays}`);
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

/** Plain-English walkthrough of the current editor code. Blank `language` reads the code as the app's saved language; a snippet in a
 *  language of its own (a Brain Drills question) says which. */
export function explainCode(code: string, language = ""): Promise<ExplainResult> {
  return request("/api/explain", {
    method: "POST",
    body: JSON.stringify(language ? { code, language } : { code }),
  });
}

// ── Gotchas: an endless feed of trap questions ──────────────────────────

export function fetchGotchas(language: GotchaLang): Promise<GotchaSummary> {
  return request(`/api/gotchas?language=${encodeURIComponent(language)}`);
}

/** One card, answer withheld. `exclude` is the ids just seen; `daily` serves today's unfinished Daily 5 card. */
export function fetchGotchaNext(language: GotchaLang, exclude: string, daily: boolean): Promise<GotchaCard> {
  return request(
    `/api/gotchas/next?language=${encodeURIComponent(language)}&exclude=${encodeURIComponent(exclude)}`
      + `&daily=${daily ? "true" : "false"}`,
  );
}

export function answerGotcha(body: { id: string; language: GotchaLang; chosen: number }): Promise<GotchaAnswer> {
  return request("/api/gotchas/answer", { method: "POST", body: JSON.stringify(body) });
}

/** Run a card's own program for real: the Run it button, after answering. */
export function runGotcha(body: { id: string; language: GotchaLang }): Promise<GotchaRun> {
  return request("/api/gotchas/run", { method: "POST", body: JSON.stringify(body) });
}

export function fetchGotchaUserCards(language: GotchaLang): Promise<{ cards: GotchaUserCard[] }> {
  return request(`/api/gotchas/user?language=${encodeURIComponent(language)}`);
}

export interface GotchaUserForm {
  language: GotchaLang;
  code: string;
  options: string[];
  guess: number | null;
  why: string;
}

/** Run the pasted code and show the card it would become; nothing is saved. */
export function previewGotchaUser(body: GotchaUserForm): Promise<GotchaUserResult> {
  return request("/api/gotchas/user/preview", { method: "POST", body: JSON.stringify(body) });
}

/** Run the pasted code for real and keep it as a card of your own. */
export function saveGotchaUser(body: GotchaUserForm): Promise<GotchaUserResult> {
  return request("/api/gotchas/user", { method: "POST", body: JSON.stringify(body) });
}

export function deleteGotchaUser(language: GotchaLang, id: string): Promise<{ deleted: string; summary: GotchaSummary }> {
  return request(`/api/gotchas/user/${encodeURIComponent(id)}?language=${encodeURIComponent(language)}`, {
    method: "DELETE",
  });
}
