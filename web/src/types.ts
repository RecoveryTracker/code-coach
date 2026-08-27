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

export type TypingCatalog = {
  sections: TypingSection[];
  themes: TypingTheme[];
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
