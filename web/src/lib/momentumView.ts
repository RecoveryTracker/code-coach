/**
 * What Momentum shows for what the server said. Pure: no React, no fetch, no clock,
 * so it can be tested in node (tests/test_momentum_view.py bundles it with esbuild).
 *
 * The server does the sums (XP, levels, streaks, quests). This only decides which
 * words and numbers go on screen and in what order: the strip in the header, and the
 * little stack of toasts that appears after a success.
 */

export interface MomentumQuest {
  /** The mode (top-bar tab) where this is done. */
  go?: string;
  id: string;
  label: string;
  have: number;
  need: number;
  done: boolean;
  just_done: boolean;
}

export interface MomentumDay {
  day: string;
  xp: number;
}

/** GET /api/momentum, and the part of every other answer that says where you stand. */
export interface MomentumSummary {
  ok: boolean;
  xp_total: number;
  level: number;
  title: string;
  xp_in_level: number;
  xp_for_next: number;
  streak: number;
  today_counted: boolean;
  best_streak: number;
  freezes: number;
  quests: MomentumQuest[];
  chest_ready: boolean;
  chest_claimed: boolean;
  today_xp: number;
  days_last_14: MomentumDay[];
}

export interface LevelUp {
  level: number;
  title: string;
}

/** POST /api/momentum/award */
export interface AwardResult extends MomentumSummary {
  repeat: boolean;
  base: number;
  combo: number;
  combo_mult: number;
  lucky: number | null;
  gained: number;
  level_up: LevelUp | null;
  streak_extended: boolean;
  freeze_used: string | null;
  freeze_earned: boolean;
  /**
   * What it was for, when the server paid it of its own accord ("Farm: first pumpkin! (Python)",
   * "Welcome back"). Null or missing for an award a screen asked for.
   */
  label?: string | null;
}

/** POST /api/momentum/chest */
export interface ChestResult extends MomentumSummary {
  gained: number;
  freeze_earned: boolean;
  level_up: LevelUp | null;
  reason?: string;
}

// ── Toasts ──────────────────────────────────────────────────────────────

export type ToastKind =
  | "xp"
  | "combo"
  | "lucky"
  | "quest"
  | "streak"
  | "freeze"
  | "chest"
  | "milestone"
  | "level";

export interface Toast {
  id: number;
  kind: ToastKind;
  text: string;
  /** A second, smaller line (the level-up card's title). */
  sub?: string;
  /** How long it stays, in milliseconds. */
  ms: number;
}

/** At most this many are on screen at once. */
export const MAX_TOASTS = 3;
export const TOAST_MS = 2500;
export const LEVEL_MS = 4000;

/** Which toast gives way first when there are too many: lowest number first. */
const PRIORITY: Record<ToastKind, number> = {
  combo: 1,
  xp: 3,
  lucky: 4,
  quest: 4,
  streak: 4,
  freeze: 4,
  chest: 4,
  milestone: 4,
  level: 5,
};

export function priority(kind: ToastKind): number {
  return PRIORITY[kind];
}

/** "x1.4": the combo multiplier as it is written. */
export function multText(mult: number): string {
  return `x${(Math.round(mult * 10) / 10).toFixed(1)}`;
}

/** "+20 XP". */
export function xpText(n: number): string {
  return `+${Math.round(n)} XP`;
}

function make(
  next: () => number,
  kind: ToastKind,
  text: string,
  sub?: string,
): Toast {
  return { id: next(), kind, text, sub, ms: kind === "level" ? LEVEL_MS : TOAST_MS };
}

function levelToast(next: () => number, up: LevelUp): Toast {
  return make(next, "level", `Level ${up.level}`, up.title);
}

/**
 * The toasts one award earns, in the order they are told. A repeat, or an answer
 * the server could not keep, earns none: nothing was paid, so nothing is celebrated.
 * The lucky bonus is the part on top of what the XP toast already says.
 */
export function toastsForAward(r: AwardResult | null | undefined, next: () => number): Toast[] {
  if (!r || !r.ok || r.repeat) return [];
  const out: Toast[] = [];
  // What it was for comes first ("Farm: first pumpkin!"), then what it paid.
  if (r.label) out.push(make(next, "milestone", r.label));
  const lucky = r.lucky && r.lucky > 1 ? r.lucky : null;
  const plain = lucky ? r.gained / lucky : r.gained;
  if (r.gained > 0) out.push(make(next, "xp", xpText(plain)));
  if (r.combo_mult > 1) out.push(make(next, "combo", `Combo ${multText(r.combo_mult)}`));
  if (lucky) out.push(make(next, "lucky", `Lucky! x${lucky} (+${Math.round(r.gained - plain)})`));
  for (const q of r.quests ?? []) {
    if (q.just_done) out.push(make(next, "quest", `Quest done: ${q.label}`));
  }
  if (r.streak_extended) {
    out.push(
      make(next, "streak", `Streak ${r.streak}${r.freeze_earned ? " - freeze earned" : ""}`),
    );
  } else if (r.freeze_earned) {
    out.push(make(next, "freeze", "Freeze earned"));
  }
  if (r.freeze_used) out.push(make(next, "freeze", "Freeze used - your streak is safe"));
  if (r.level_up) out.push(levelToast(next, r.level_up));
  return out;
}

/**
 * The toasts for answers the server worked out without being asked (a farm milestone a program
 * earned, a quest its harvest finished): one answer or a list, oldest first, told in order.
 */
export function toastsForAnswers(
  answers: AwardResult | AwardResult[] | null | undefined,
  next: () => number,
): Toast[] {
  const list = Array.isArray(answers) ? answers : answers ? [answers] : [];
  return list.flatMap((r) => toastsForAward(r, next));
}

/** The toasts for opening the chest. */
export function toastsForChest(r: ChestResult | null | undefined, next: () => number): Toast[] {
  if (!r || !r.ok) return [];
  const out: Toast[] = [make(next, "chest", `Chest: ${xpText(r.gained)}`)];
  if (r.freeze_earned) out.push(make(next, "freeze", "Freeze earned"));
  if (r.level_up) out.push(levelToast(next, r.level_up));
  return out;
}

/**
 * Add `incoming` to what is showing, and keep it to `max`. When there are too many,
 * the least important goes first (a combo note before an XP note before a quest...)
 * and, among equals, the oldest. A level-up is never the one to go while anything
 * else could, and it is shown first.
 */
export function enqueue(current: Toast[], incoming: Toast[], max: number = MAX_TOASTS): Toast[] {
  // One level-up card at a time: two in a quick row (an award, then a chest) show the
  // newest level, not a pile of cards.
  const lastLevel = incoming.map((t) => t.kind).lastIndexOf("level");
  const fresh = incoming.filter((t, i) => t.kind !== "level" || i === lastLevel);
  const all = [
    ...(lastLevel >= 0 ? current.filter((t) => t.kind !== "level") : current),
    ...fresh,
  ];
  while (all.length > max) {
    let drop = 0;
    for (let i = 1; i < all.length; i++) {
      if (priority(all[i].kind) < priority(all[drop].kind)) drop = i;
    }
    all.splice(drop, 1);
  }
  return displayOrder(all);
}

/** A level-up card on top, then the rest in the order they arrived. */
export function displayOrder(list: Toast[]): Toast[] {
  return [...list.filter((t) => t.kind === "level"), ...list.filter((t) => t.kind !== "level")];
}

export function dismiss(list: Toast[], id: number): Toast[] {
  return list.filter((t) => t.id !== id);
}

// ── The strip in the header, and its popover ────────────────────────────

export interface Bar {
  day: string;
  xp: number;
  /** 0 to 100: the day's share of the busiest day shown (a day with any XP shows a sliver). */
  pct: number;
  label: string;
  today: boolean;
}

export interface HudView {
  /** The streak number in the flame. */
  streak: string;
  /** Lit when today already counts; dimmed (not alarmed) when it does not yet. */
  flameLit: boolean;
  streakNote: string;
  freezes: number;
  freezeNote: string;
  levelText: string;
  levelShort: string;
  /** 0 to 100, for the bar. */
  xpPct: number;
  xpText: string;
  questText: string;
  questsDone: number;
  questsTotal: number;
  chest: "locked" | "ready" | "opened";
  chestNote: string;
  bestText: string;
  bars: Bar[];
  totalText: string;
}

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/** "Wed", read from the date's own digits so the time zone cannot move it. */
export function weekday(day: string): string {
  const [y, m, d] = day.split("-").map(Number);
  if (!y || !m || !d) return day;
  return WEEKDAYS[new Date(Date.UTC(y, m - 1, d)).getUTCDay()];
}

export function bars(days: MomentumDay[]): Bar[] {
  const top = Math.max(0, ...days.map((d) => d.xp));
  return days.map((d, i) => ({
    day: d.day,
    xp: d.xp,
    pct: d.xp <= 0 || top <= 0 ? 0 : Math.max(8, Math.round((d.xp / top) * 100)),
    label: `${weekday(d.day)}: ${d.xp} XP`,
    today: i === days.length - 1,
  }));
}

export function hudView(s: MomentumSummary | null | undefined): HudView {
  const level = s?.level ?? 1;
  const title = s?.title ?? "Beginner";
  const span = Math.max(1, s?.xp_for_next ?? 100);
  const into = Math.max(0, s?.xp_in_level ?? 0);
  const quests = s?.quests ?? [];
  const done = quests.filter((q) => q.done).length;
  const streak = s?.streak ?? 0;
  const counted = s?.today_counted ?? false;
  const freezes = s?.freezes ?? 0;
  const chest: HudView["chest"] = s?.chest_ready ? "ready" : s?.chest_claimed ? "opened" : "locked";
  return {
    streak: String(streak),
    flameLit: counted,
    streakNote:
      streak === 0
        ? "Do one thing today to start a streak"
        : counted
          ? `${streak} day${streak === 1 ? "" : "s"} in a row - today counts`
          : `${streak} day${streak === 1 ? "" : "s"} in a row - do one thing today to add today`,
    freezes,
    freezeNote:
      freezes === 0
        ? "No freezes yet: you earn one every 7th day of a streak"
        : `${freezes} freeze${freezes === 1 ? "" : "s"}: each covers one missed day`,
    levelText: `Lv ${level} ${title}`,
    levelShort: `Lv ${level}`,
    xpPct: Math.min(100, Math.round((into / span) * 100)),
    xpText: `${into} / ${span} XP`,
    questText: `${done}/${quests.length || 3}`,
    questsDone: done,
    questsTotal: quests.length || 3,
    chest,
    chestNote:
      chest === "ready"
        ? "All three done - your chest is ready"
        : chest === "opened"
          ? "Today's chest is open"
          : "Finish all three quests to open today's chest",
    bestText: `Best streak ${s?.best_streak ?? 0}`,
    bars: bars(s?.days_last_14 ?? []),
    totalText: `${(s?.xp_total ?? 0).toLocaleString("en-US")} XP in all`,
  };
}

// ── The Farm's welcome-back card ────────────────────────────────────────

/** What the server offers when the Farm is opened after a while away (GET /api/farm). */
export interface WelcomeBack {
  /** About how long the farm had not been looked at. */
  minutes: number;
  /** Squares with something ripe (plain grass not counted), as the farm stood when it was opened. */
  ripe: number;
  /** The base pay for claiming it; the combo and any luck come on top. */
  xp: number;
  language: string;
}

export interface WelcomeView {
  title: string;
  body: string;
  /** The honest line: the farm does not run while the app is closed. */
  note: string;
  claim: string;
  dismiss: string;
}

/**
 * Words for the card. It says what is ripe and offers a small payout; there is no
 * clock on it and nothing in it is about what could be lost. A farm with nothing ripe
 * is simply quiet, and the base still pays.
 */
export function welcomeView(w: WelcomeBack): WelcomeView {
  const ripe = Math.max(0, Math.round(w.ripe));
  return {
    title: "Welcome back",
    body:
      ripe === 0
        ? "The farm is quiet and still."
        : ripe === 1
          ? "1 tile is ripe."
          : `${ripe.toLocaleString("en-US")} tiles are ripe.`,
    note: "The farm waits for you: nothing grows while you are away.",
    claim: "Claim welcome-back XP",
    dismiss: "Not now",
  };
}
