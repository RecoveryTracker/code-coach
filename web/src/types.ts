export type SupportLink = {
  skill_id: string;
  label: string;
  lesson_title: string;
};

export type WaypointInfo = {
  id: string;
  label: string;
  tip?: string | null;
  keyboard_tip?: string | null;
  hint_lines?: string[];
  supports?: SupportLink[];
  kind?: string;
};

export type CheckItem = {
  id?: string | null;
  label: string;
  passed: boolean;
};

export type PracticeMode = "progressive" | "skill" | "random" | "reps";
export type CoachStyle = "dictation" | "vocabulary";

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
