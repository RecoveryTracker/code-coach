// ── Typing trainer ──────────────────────────────────────────

export type TypingKey = {
  char: string;
  shifted: string;
  row: string;
  finger: string;
  reach: number;
};

export type TypingMode = {
  id: string;
  name: string;
  description: string;
  /** Show only the current target — nothing coming up next. */
  hidden: boolean;
  by_name: boolean;
};

export type TypingSection = {
  id: string;
  name: string;
  description: string;
  modes: TypingMode[];
};

/** What the words and lines say — a separate choice from which keys. */
export type TypingTheme = {
  id: string;
  name: string;
  description: string;
  has_words: boolean;
  has_passages: boolean;
  /** Whole functions, not just single lines — the code themes. */
  has_blocks?: boolean;
};

/** A language Learn and Type can teach. */
export type TypingTeachLanguage = {
  id: string;
  name: string;
};

/** One reminder about code that won't run. */
export type SyntaxHint = {
  line: number;
  message: string;
};

export type TypingCatalog = {
  sections: TypingSection[];
  themes: TypingTheme[];
  /** Languages Learn and Type can teach, for its own picker. */
  teach_languages: TypingTeachLanguage[];
  keyboard: TypingKey[][];
  fingers: Record<string, string>;
  /** Spoken names for punctuation, e.g. "|" → "pipe". */
  names: Record<string, string>;
};

export type TypingTarget = {
  text: string;
  prompt: string;
  shift: boolean;
  /** A definition or a verse reference — shown beside the target. */
  note: string;
  finger: string;
};

export type TypingDrill = {
  id: string;
  section: string;
  section_name: string;
  mode: string;
  mode_name: string;
  theme: string;
  theme_name: string;
  description: string;
  hidden: boolean;
  scoring: "reaction" | "wpm";
  targets: TypingTarget[];
};

export type TypingFinger = {
  finger: string;
  name: string;
  hand: "left" | "right";
  home: string;
  keys: string[];
  note: string;
};

export type TypingHomeKey = {
  char: string;
  finger: string;
  name: string;
  /** The two keys with a raised bump — how you find home without looking. */
  anchor: boolean;
};

export type TypingGuide = {
  fingers: TypingFinger[];
  home_row: TypingHomeKey[];
  tips: { title: string; body: string }[];
  faq: { question: string; answer: string }[];
};

export type TypingLesson = {
  number: number;
  title: string;
  why: string;
  section: string;
  mode: string;
  theme: string;
  section_name: string;
  mode_name: string;
  theme_name: string;
  target_wpm: number;
  target_accuracy: number;
  done: boolean;
  best_wpm: number;
  best_accuracy: number;
  runs: number;
};

export type TypingCourse = {
  lessons: TypingLesson[];
  total: number;
  done: number;
  /** The lesson to carry on with. Nothing is locked. */
  current: number;
};

export type TypingRecord = {
  section: string;
  mode: string;
  section_name: string;
  mode_name: string;
  best_wpm: number;
  best_accuracy: number;
  best_reaction_ms: number;
  best_streak: number;
  runs: number;
  total_keys: number;
  last_wpm: number;
  last_accuracy: number;
  updated: string;
};

export type TypingRunResult = {
  record: TypingRecord;
  beat_wpm: boolean;
  beat_accuracy: boolean;
  beat_reaction: boolean;
  beat_streak: boolean;
};

export type SupportLink = {
  skill_id: string;
  label: string;
  lesson_title: string;
};

export type ProblemBriefInfo = {
  number: number;
  title: string;
  difficulty: string;
  statement: string;
  examples: string[];
  note: string;
  idea: string;
  complexity: string;
  url: string;
  /** Full reference solution — powers "show answer" / "check my work". */
  solution: string;
};

export type CheckAnswerResult = {
  ok: boolean;
  matches: boolean;
  note: string;
  solution: string;
  title: string;
};

/** One move in a worked lesson, and the code as it stands after it. */
export type WorkedStageInfo = {
  explain: string;
  code: string;
};

/** One problem taken from the question to a finished solution. */
export type WorkedInfo = {
  problem: number;
  naive: string;
  why_not: string;
  insight: string;
  stages: WorkedStageInfo[];
};

export type PatternLessonInfo = {
  id: string;
  name: string;
  summary: string;
  when: string;
  template: string;
  steps: string[];
  pitfalls: string[];
  /** The lesson proper: how anyone arrives at the solution. */
  worked?: WorkedInfo | null;
};

/** One line on the cheat sheet, and the shortest useful note about it. */
export type ReferenceEntry = {
  code: string;
  note: string;
};

export type ReferenceSection = {
  name: string;
  blurb: string;
  entries: ReferenceEntry[];
};

export type ReferenceSheet = {
  language: string;
  has_sheet: boolean;
  sections: ReferenceSection[];
};

/** One problem a lesson points you at once you've read it. */
export type LessonProblem = {
  number: number;
  title: string;
  difficulty: string;
  idea: string;
  complexity: string;
  url: string;
};

/** A pattern lesson as the Lessons screen wants it: whole, and on its own. */
export type LessonEntry = {
  id: string;
  /** Whether the problems can be opened in this language, or only read. */
  can_open: boolean;
  name: string;
  order: number;
  blurb: string;
  tell: string;
  summary: string;
  when: string;
  template: string;
  steps: string[];
  pitfalls: string[];
  worked: (WorkedInfo & { title: string; statement: string }) | null;
  problems: LessonProblem[];
};

export type StudyInfo = {
  problem: ProblemBriefInfo | null;
  lesson: PatternLessonInfo | null;
};

export type WaypointInfo = {
  id: string;
  label: string;
  tip?: string | null;
  keyboard_tip?: string | null;
  hint_lines?: string[];
  supports?: SupportLink[];
  kind?: string;
  study?: StudyInfo | null;
};

export type CheckItem = {
  id?: string | null;
  label: string;
  passed: boolean;
};

export type PracticeMode = "progressive" | "skill" | "random" | "reps";
export type CoachStyle = "dictation" | "vocabulary";

/** A language the drills can be written in. Only Python is implemented. */
export type LanguageInfo = {
  id: string;
  name: string;
  /** Monaco's syntax-highlighting id. */
  monaco: string;
  extension: string;
  available: boolean;
  /** Why it isn't selectable yet. */
  note: string;
  /** Which pieces exist: runner / checks / bank / tracer. */
  ready: string[];
};

export type SkillInfo = {
  id: string;
  name: string;
  description: string;
  order: number;
  base_difficulty: number;
};

export type SkillProgress = {
  name: string;
  done: number;
  total: number;
  xp: number;
};

export type ReviewDueItem = {
  skill_id: string;
  name: string;
  days: number;
};

export type ProgressInfo = {
  mode: PracticeMode;
  coach_level: number;
  difficulty: number;
  selected_skills: string[];
  total_completes: number;
  unique_drills_done: number;
  total_drills: number;
  current_drill_id: string | null;
  by_skill: Record<string, SkillProgress>;
  updated_at: string;
  curriculum_class?: string;
  curriculum_lesson?: number;
  review_skill?: string | null;
  dictation_level?: number;
  language?: string;
  class1_lines_done?: number;
  class1_batch?: number;
  /** Per-class endless type-along lifetime lines. */
  dictation_lines?: Record<string, number>;
  /** Skills practiced before but not recently (light spaced repetition). */
  review_due?: ReviewDueItem[];
  /** Per-language workbook standing. Only languages you have worked in. */
  workbook?: Record<string, WorkbookStanding>;
};

export type WorkbookStanding = {
  done: number;
  total: number;
  pages_started: number;
  pages_done: number;
  pages_total: number;
};

export type PracticeSession = {
  drill_id: string;
  title: string;
  skill: string;
  skill_name: string;
  difficulty: number;
  prompt: string;
  starter: string;
  steps: WaypointInfo[];
  mode: PracticeMode;
  coach_level: number;
  coach_style: CoachStyle;
  meter: number;
  progress: ProgressInfo;
  is_lesson: boolean;
  class_id?: string;
  class_number?: number;
  class_name?: string;
  lesson_number?: number;
  lesson_role?: string;
  is_review?: boolean;
  can_go_lesson_2?: boolean;
  curriculum?: {
    id: string;
    number?: number;
    name: string;
    description: string;
    lessons: {
      number: number;
      id: string;
      title: string;
      role: string;
      full_title: string;
    }[];
  }[];
  exercise_count?: number;
  /** Foundations Lesson 1 type-along — never ends on its own */
  endless?: boolean;
  dictation_level?: number;
  dictation_level_label?: string;
  lines_done?: number;
  language?: string;
  /** Monaco id for the current language. */
  editor_language?: string;
  /** Everything the class holds, not just the current window of 8. */
  class_total?: number;
  /** Where this window starts inside that total. */
  class_position?: number;
  /** Where a lesson link asked us to land; null means "where you left off". */
  jump_to_exercise?: number | null;
  /** Which window of the endless type-along this is — part of the draft key. */
  window?: number;
  /** "Watch it run" needs a tracer — Python only, for now. */
  can_visualize?: boolean;
  /** "Explain my code" reads the code with Python's ast — Python only. */
  can_explain?: boolean;
};

export type RequirementItem = {
  label: string;
  passed: boolean;
};

export type DrillEvaluateResult = {
  drill_id: string;
  title: string;
  skill: string;
  difficulty: number;
  prompt: string;
  code: string;
  stdout: string;
  stderr: string;
  exit_code: number;
  ran: boolean;
  checks: CheckItem[];
  passed: number;
  total: number;
  complete: boolean;
  coach_level: number;
  coach_style: CoachStyle;
  next_label: string | null;
  next_concept: string | null;
  next_why: string | null;
  next_hint: string | null;
  next_example: string | null;
  next_suggest: string | null;
  next_vocab: string | null;
  accepts_own_values: boolean;
  observation: string | null;
  guidance: string | null;
  adapt_example: string | null;
  tone: string | null;
  status: string | null;
  just_completed: boolean;
  progress: ProgressInfo | null;
  /** Build exercises: the goal's pieces with live pass/fail. */
  requirements?: RequirementItem[] | null;
};

/* ── Visualiser ─────────────────────────────────────────── */

/** A leaf value, or a pointer into the step's heap. */
export type VizValue =
  | { k: "prim"; t: "int" | "float" | "str" | "bool" | "none"; v: unknown; clipped?: boolean }
  | { k: "ref"; id: number };

export type VizHeapEntry =
  | { k: "list"; tuple: boolean; n: number; items: VizValue[] }
  | { k: "dict"; n: number; pairs: [VizValue, VizValue][] }
  | { k: "set"; n: number; items: VizValue[] }
  | { k: "obj"; cls: string; fields: Record<string, VizValue> }
  | { k: "opaque"; cls: string; v: string };

export type VizStep = {
  line: number;
  func: string;
  vars: Record<string, VizValue>;
  /** Keys arrive from JSON as strings. */
  heap: Record<string, VizHeapEntry>;
  /** Present on the frame where a function returns — the value it handed back. */
  returned?: VizValue;
};

export type VisualizeResult = {
  ok: boolean;
  steps: VizStep[];
  truncated: boolean;
  stdout: string;
  stderr: string;
  error: string | null;
  call: string;
};

/** One explained line from /api/explain. */
export type ExplainLine = {
  line: number;
  depth: number;
  source: string;
  text: string;
};

/** Plain-English walkthrough of the current code. */
export type ExplainResult = {
  ok: boolean;
  summary: string;
  lines: ExplainLine[];
  output_notes: string[];
  error_note: string | null;
};

export type ConceptQuestion = {
  ask: string;
  answer: string;
  /** The one an interviewer reaches for when you answer the first well. */
  follow_up: string;
};

export type ConceptTopic = {
  id: string;
  name: string;
  blurb: string;
  order: number;
  questions: ConceptQuestion[];
};

/** One workbook exercise: a sentence, and what the program has to print. */
export type WorkbookExercise = {
  id: string;
  prompt: string;
  expect: string;
  /** The reference program, hidden until asked for. */
  answer: string;
};

/** A page: one new idea and a dozen goes at it. */
export type WorkbookPage = {
  id: string;
  number: number;
  name: string;
  teaches: string;
  example: string;
  /** Which section of the book: beginner | practice | intermediate | advanced. */
  tier: string;
  /**
   * What this page's shape costs once the numbers get big. Null where
   * there is nothing honest to say about it yet, and the screen then
   * shows nothing rather than a guess.
   */
  cost: { label: string; note: string } | null;
  exercises: WorkbookExercise[];
};

export type WorkbookData = {
  /**
   * Whether Watch it run can answer in this language.
   *
   * From the server, which asks the language, rather than a list on
   * this side that goes stale — it said Python only while JavaScript
   * and Dart both had tracers.
   */
  can_trace?: boolean;
  language: string;
  /** The display name, for writing into a sentence. */
  language_name: string;
  has_workbook: boolean;
  pages: WorkbookPage[];
  /** Exercise ids already solved in this language. */
  done: string[];
  /** The page last worked on, so it opens there. "" before you start. */
  at: string;
  /** Your own accepted code, by exercise id. */
  answers: Record<string, string>;
};

export type WorkbookCheck = {
  passed: boolean;
  stdout: string;
  stderr: string;
  expect: string;
  exit_code: number;
  /** The program never ran — a compile or syntax error, not a wrong answer. */
  failed_to_run: boolean;
  done_on_page: number;
  page_total: number;
};

/**
 * A kata: a function to write, and the inputs it will be called with.
 *
 * The count of cases rather than the cases themselves. Seeing the inputs
 * in advance turns the exercise into a lookup table — the whole point is
 * that the function has to work on inputs you did not pick, so they
 * arrive only when it has been run.
 */
export type KataSummary = {
  id: string;
  name: string;
  brief: string;
  signature: string;
  example: string;
  hint: string;
  cases: number;
  /**
   * Code already in the box and already wrong. Empty for a kata you
   * write yourself; filled for a "fix the bug" exercise, and that is
   * what tells the two apart on screen.
   */
  start: string;
  /**
   * How many times this one has been got right.
   *
   * A count, not a tick. These are practised rather than finished, so
   * the useful question is how many goes you have had — which is also
   * what picks the next one.
   */
  done: number;
  /**
   * When this was last got right, or empty for never.
   *
   * Beside the count because the count alone cannot separate two
   * things you have done twice — and the one you did last week is the
   * one worth doing again before the one you did this morning.
   */
  last: string;
  /**
   * How hard it is, 1 to 5, and the order a family is listed in.
   *
   * Shown on the open kata rather than beside every name in the list:
   * the ordering already says it, and a number against all forty-seven
   * is noise.
   */
  level: number;
};

export type KataFamily = {
  name: string;
  /** Which language its katas are written in. A family never mixes. */
  language: string;
  katas: KataSummary[];
};

export type KataList = {
  /** Every language on offer, in the order the families meet them. */
  languages: string[];
  families: KataFamily[];
};

/** One call, and whether it was right. */
export type KataCaseResult = {
  args: unknown[];
  want: unknown;
  got: unknown;
  error: string;
  passed: boolean;
  /** Changed what it was handed, and was not meant to. */
  changed: boolean;
};

export type KataCheck = {
  passed: boolean;
  count: number;
  total: number;
  results: KataCaseResult[];
  /**
   * Set when the file did not run at all — a syntax error, or no
   * function by that name. A different problem from failing cases, and
   * showing it as "0 of 10" sends you looking in the wrong place.
   */
  broke: string;
  /** Whatever the student printed themselves, without the marker's line. */
  stdout: string;
  /** What the bug was. Only sent once every case passes. */
  bug: string;
  /** Goes at this one that came out right, counting this one. */
  done: number;
};

/**
 * One "what does this print" puzzle.
 *
 * No answer on it, and that is deliberate: the answer is the exercise,
 * so it only arrives once a guess has been sent.
 */
export type PredictPuzzle = {
  id: string;
  name: string;
  code: string;
  /** How many times this one has been answered correctly. */
  done: number;
  /** When it was last right, or empty for never. */
  last: string;
  /** How surprising it is, 1 to 5. */
  level: number;
};

export type PredictFamily = {
  name: string;
  /** Which language its snippets are in. A family never mixes them. */
  language: string;
  puzzles: PredictPuzzle[];
};

export type PredictList = {
  families: PredictFamily[];
};

export type PredictCheck = {
  passed: boolean;
  expect: string;
  guess: string;
  done: number;
  /** Shown whether you were right or wrong. */
  why: string;
};

export type CssQuiz = {
  id: string;
  name: string;
  /** The markup, as it goes inside body. */
  html: string;
  css: string;
  /** Which element is being asked about. Always an id selector. */
  target: string;
  /** The computed property, or rect.width / rect.height for the space
   *  it really takes - which is the question wherever the computed
   *  property reports the declaration and means nothing. */
  prop: string;
  /** Everything on offer, sorted, with the answer hidden among them. */
  choices: string[];
  /** The whole document, so the page shown is the page measured. */
  page: string;
  done: number;
  last: string;
  level: number;
};

export type CssFamily = {
  name: string;
  quizzes: CssQuiz[];
};

export type CssList = {
  families: CssFamily[];
};

export type CssCheck = {
  passed: boolean;
  expect: string;
  choice: string;
  done: number;
  why: string;
};

export type MarkupDrill = {
  id: string;
  name: string;
  /** The code you are copying. Not hidden — copying it is the exercise. */
  code: string;
  note: string;
  /** A page with {{drill}} where the piece goes, or "" when the drill
   *  is itself the whole document. */
  wrapper: string;
  lines: number;
  done: number;
  last: string;
  level: number;
};

export type MarkupFamily = {
  name: string;
  drills: MarkupDrill[];
};

export type MarkupList = {
  families: MarkupFamily[];
};

export type MarkupCheck = {
  passed: boolean;
  done: number;
  /** 1-based, or 0 when it matched. One place to look, not a diff. */
  first_wrong_line: number;
  want_line: string;
  typed_line: string;
};
