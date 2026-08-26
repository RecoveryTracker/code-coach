import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchTypingCatalog, fetchTypingDrill, submitTypingRun } from "../api";
import type {
  TypingCatalog,
  TypingDrill,
  TypingRunResult,
  TypingSection,
} from "../types";
import TypingCoursePanel from "./TypingCourse";
import TypingGuidePanel from "./TypingGuide";
import TypingKeyboard, { type KeyStat } from "./TypingKeyboard";
import TypingRecords from "./TypingRecords";

/**
 * The typing trainer.
 *
 * Three shapes of drill share this screen. Reaction drills show one key at a
 * time with nothing ahead of it, scored on how fast you find it. Text drills
 * show a line and are scored on words a minute. The timed drill is the same
 * words with a clock over it. All three feed the same per-key history, which
 * is what the results heatmap comes from — the useful output isn't the score,
 * it's knowing which keys you hunt for.
 */

type Phase = "idle" | "running" | "done";
type Tab = "course" | "practice" | "learn" | "records";

/**
 * What happens when you hit a wrong key.
 *
 * "block" keeps the drill flowing and trains the right movement. "delete" is
 * what a real editor does — the wrong character lands and you have to notice
 * it and back it out. Both are worth practising, so it's a choice rather than
 * a decision made for you.
 */
type MistakeMode = "block" | "delete";

type Flash = { char: string; ok: boolean; at: number };

const TIMED_SECONDS = 60;
const SETTINGS_KEY = "code-coach:typing:settings";
/**
 * How long the keyboard can sit still before the clock stops.
 *
 * Words a minute measured against wall-clock time punishes you for pausing to
 * read the next line, or to think about where a key is — which is most of what
 * learning a keyboard is. The clock counts the time you're actually typing.
 */
const IDLE_PAUSE_MS = 2000;

/** Words a minute, using the standard five-characters-is-a-word convention. */
function wpmOf(chars: number, ms: number): number {
  if (ms <= 0) return 0;
  return Math.round(chars / 5 / (ms / 60000));
}

function pct(n: number, d: number): number {
  return d === 0 ? 100 : Math.round((n / d) * 100);
}

const NEWLINE = '\n';
/** Shown where Enter belongs, so the newline is a visible key. */
const RETURN_GLYPH = "\u21B5";

/**
 * The run of spaces starting at `from`, which Enter should skip past.
 *
 * Indentation is real syntax in Python and real habit everywhere else, but
 * counting four spaces by hand is not what anyone practises — every editor
 * puts them there for you. So does this.
 */
function leadingSpaceAt(text: string, from: number): string {
  let i = from;
  while (i < text.length && (text[i] === " " || text[i] === "\t")) i += 1;
  return text.slice(from, i);
}

type Settings = {
  mistakes: MistakeMode;
  section: string;
  mode: string;
  theme: string;
  /** Stop the clock after IDLE_PAUSE_MS of no typing. */
  idlePause: boolean;
  /** Show the speed at all. Some days the number is the thing in the way. */
  showWpm: boolean;
};

/**
 * What the trainer opens on next time.
 *
 * The drill you chose is a setting, not a fresh decision to make on every
 * reload — coming back to Everything/Random after picking Symbols/Key Pairs
 * throws away the choice you just made.
 */
const DEFAULTS: Settings = {
  mistakes: "block",
  section: "everything",
  mode: "random",
  theme: "mixed",
  idlePause: true,
  showWpm: true,
};

function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<Settings>;
      return {
        mistakes:
          parsed.mistakes === "delete" || parsed.mistakes === "block"
            ? parsed.mistakes
            : DEFAULTS.mistakes,
        // Validated against the catalog once it loads, so a section that no
        // longer exists can't strand you on an empty picker.
        section: parsed.section || DEFAULTS.section,
        mode: parsed.mode || DEFAULTS.mode,
        theme: parsed.theme || DEFAULTS.theme,
        // Both default to on, so an older settings blob without them reads
        // the way the trainer has always behaved plus the idle pause.
        idlePause: parsed.idlePause !== false,
        showWpm: parsed.showWpm !== false,
      };
    }
  } catch {
    /* a bad settings blob shouldn't stop you typing */
  }
  return DEFAULTS;
}

export default function TypingTrainer() {
  const [catalog, setCatalog] = useState<TypingCatalog | null>(null);
  // Opens on whatever you were last doing — the whole keyboard with an
  // ordinary mixed drill, until you choose otherwise. Landing on a menu, or
  // on a reflex game, makes you choose something before you can type, and the
  // point of opening this is to type.
  const [sectionId, setSectionId] = useState(() => loadSettings().section);
  const [modeId, setModeId] = useState(() => loadSettings().mode);
  // What the words say, which is a separate choice from which keys they use.
  const [themeId, setThemeId] = useState(() => loadSettings().theme);
  const [drill, setDrill] = useState<TypingDrill | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Practice is the front door — a drill is already loaded and waiting. The
  // course is a tab away for anyone who wants to be walked through it.
  const [tab, setTab] = useState<Tab>("practice");
  const [mistakes, setMistakes] = useState<MistakeMode>(
    () => loadSettings().mistakes,
  );
  const [idlePause, setIdlePause] = useState(() => loadSettings().idlePause);
  const [showWpm, setShowWpm] = useState(() => loadSettings().showWpm);

  const [phase, setPhase] = useState<Phase>("idle");
  const [index, setIndex] = useState(0);
  const [typed, setTyped] = useState("");
  const [flash, setFlash] = useState<Flash | null>(null);
  const [combo, setCombo] = useState(0);
  const [bestCombo, setBestCombo] = useState(0);
  const [stats, setStats] = useState<Record<string, KeyStat>>({});
  const [hits, setHits] = useState(0);
  const [misses, setMisses] = useState(0);
  const [restarts, setRestarts] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  /** The clock has stopped itself because nothing has been typed lately. */
  const [paused, setPaused] = useState(false);
  const [outcome, setOutcome] = useState<TypingRunResult | null>(null);
  // Looking back through a finished run. The score is already recorded, so
  // this is read-only.
  const [reviewing, setReviewing] = useState(false);
  const [recordRevision, setRecordRevision] = useState(0);

  // When the last keystroke landed, so a reaction time means something.
  const shownAt = useRef(0);
  // The clock, kept in refs so a keystroke can settle it exactly rather than
  // waiting for the next 100ms tick.
  //   activeMs  — time banked so far, idle gaps already taken out
  //   spanFrom  — when the stretch currently being banked started
  //   lastTyped — any key at all, including a Backspace or a bounced mistake,
  //               because all of those mean you are still at the keyboard
  const activeMs = useRef(0);
  const spanFrom = useRef(0);
  const lastTyped = useRef(0);
  // Guards against submitting the same finished run twice.
  const submitted = useRef(false);

  const section = useMemo(
    () => catalog?.sections.find((s) => s.id === sectionId) ?? null,
    [catalog, sectionId],
  );
  const mode = useMemo(
    () => section?.modes.find((m) => m.id === modeId) ?? null,
    [section, modeId],
  );
  const target = drill?.targets[index] ?? null;
  const isReaction = drill?.scoring === "reaction";
  const isTimed = drill?.mode === "timed";
  const isPerfect = drill?.mode === "perfect";

  useEffect(() => {
    try {
      localStorage.setItem(
        SETTINGS_KEY,
        JSON.stringify({
          mistakes,
          section: sectionId,
          mode: modeId,
          theme: themeId,
          idlePause,
          showWpm,
        }),
      );
    } catch {
      /* nothing to do if storage is full or blocked */
    }
  }, [mistakes, sectionId, modeId, themeId, idlePause, showWpm]);

  // ── Loading ───────────────────────────────────────────────

  useEffect(() => {
    fetchTypingCatalog()
      .then(setCatalog)
      .catch((e: Error) => setError(e.message));
  }, []);

  const loadDrill = useCallback(
    async (nextSection: string, nextMode: string, nextTheme: string) => {
      setError(null);
      try {
        const next = await fetchTypingDrill(
          nextSection,
          nextMode,
          String(Date.now()),
          nextTheme,
        );
        submitted.current = false;
        setDrill(next);
        setPhase("idle");
        setIndex(0);
        setTyped("");
        setFlash(null);
        setCombo(0);
        setBestCombo(0);
        setStats({});
        setHits(0);
        setMisses(0);
        setRestarts(0);
        setElapsed(0);
        setPaused(false);
        activeMs.current = 0;
        setOutcome(null);
        setReviewing(false);
      } catch (e) {
        setError((e as Error).message);
      }
    },
    [],
  );

  // Picking a section whose modes don't include the current one has to land
  // somewhere valid — Bottom Row has no Words mode, so it isn't offered there.
  const chooseSection = useCallback(
    (next: TypingSection) => {
      const keepMode = next.modes.some((m) => m.id === modeId)
        ? modeId
        : next.modes[0].id;
      setSectionId(next.id);
      setModeId(keepMode);
      void loadDrill(next.id, keepMode, themeId);
    },
    [loadDrill, modeId, themeId],
  );

  const chooseMode = useCallback(
    (next: string) => {
      setModeId(next);
      // The server falls back when a theme can't drive a mode, so without
      // this the picker kept saying "Facts" while Python was on screen.
      let theme = themeId;
      const usable = (catalog?.themes ?? []).filter((t) =>
        next === "blocks"
          ? t.has_blocks
          : next === "words" || next === "define"
            ? t.has_words
            : true,
      );
      if (usable.length && !usable.some((t) => t.id === theme)) {
        theme = usable[0].id;
        setThemeId(theme);
      }
      void loadDrill(sectionId, next, theme);
    },
    [catalog, loadDrill, sectionId, themeId],
  );

  const chooseTheme = useCallback(
    (next: string) => {
      setThemeId(next);
      void loadDrill(sectionId, modeId, next);
    },
    [loadDrill, modeId, sectionId],
  );

  const jumpTo = useCallback(
    (nextSection: string, nextMode: string, nextTheme = themeId) => {
      setTab("practice");
      setSectionId(nextSection);
      setModeId(nextMode);
      setThemeId(nextTheme);
      void loadDrill(nextSection, nextMode, nextTheme);
    },
    [loadDrill, themeId],
  );

  useEffect(() => {
    if (!catalog || drill) return;
    // A remembered choice can go stale — a section can be renamed or dropped
    // between versions, and a mode a section no longer offers would 404 into
    // the error screen. Fall back rather than strand someone there.
    const found =
      catalog.sections.find((s) => s.id === sectionId) ?? catalog.sections[0];
    const mode = found.modes.some((m) => m.id === modeId)
      ? modeId
      : found.modes[0].id;
    const theme = catalog.themes.some((t) => t.id === themeId)
      ? themeId
      : DEFAULTS.theme;
    if (found.id !== sectionId) setSectionId(found.id);
    if (mode !== modeId) setModeId(mode);
    if (theme !== themeId) setThemeId(theme);
    void loadDrill(found.id, mode, theme);
  }, [catalog, drill, loadDrill, modeId, sectionId, themeId]);

  // ── The clock ─────────────────────────────────────────────

  useEffect(() => {
    if (phase !== "running") return;
    const id = window.setInterval(() => {
      const now = Date.now();
      // Bank the stretch up to now, or up to the moment the pause began —
      // whichever came first. Everything after that is thinking time.
      const until = idlePause
        ? Math.min(now, lastTyped.current + IDLE_PAUSE_MS)
        : now;
      if (until > spanFrom.current) {
        activeMs.current += until - spanFrom.current;
        spanFrom.current = until;
        setElapsed(activeMs.current);
      }
      setPaused(idlePause && now - lastTyped.current >= IDLE_PAUSE_MS);
      // The timed drill ends on the clock, not on running out of words.
      if (isTimed && activeMs.current >= TIMED_SECONDS * 1000) setPhase("done");
    }, 100);
    return () => window.clearInterval(id);
  }, [idlePause, isTimed, phase]);

  useEffect(() => {
    if (!flash) return;
    const id = window.setTimeout(() => setFlash(null), 180);
    return () => window.clearTimeout(id);
  }, [flash]);

  // ── Scoring ───────────────────────────────────────────────

  const record = useCallback((char: string, ok: boolean, ms: number) => {
    setStats((prev) => {
      const cur = prev[char] ?? { hits: 0, misses: 0, totalMs: 0 };
      return {
        ...prev,
        [char]: {
          hits: cur.hits + (ok ? 1 : 0),
          misses: cur.misses + (ok ? 0 : 1),
          totalMs: cur.totalMs + (ok ? ms : 0),
        },
      };
    });
    if (ok) {
      setHits((n) => n + 1);
      setCombo((c) => {
        const next = c + 1;
        setBestCombo((b) => Math.max(b, next));
        return next;
      });
    } else {
      setMisses((n) => n + 1);
      setCombo(0);
    }
  }, []);

  /**
   * Move by hand rather than by finishing something.
   *
   * Back is for looking at what you just typed — in the hidden modes that's
   * the only way to see it at all, since the whole point was that you
   * couldn't. Skip is for a line you don't want. Neither touches the score:
   * skipping a target you never typed shouldn't count against your accuracy,
   * and going back to look at one shouldn't count twice.
   */
  const step = useCallback(
    (delta: number) => {
      if (!drill) return;
      setIndex((i) => {
        const last = drill.targets.length - 1;
        return Math.min(Math.max(0, i + delta), last);
      });
      setTyped("");
      setFlash(null);
      shownAt.current = Date.now();
    },
    [drill],
  );

  const advance = useCallback(() => {
    setTyped("");
    shownAt.current = Date.now();
    setIndex((i) => {
      const next = i + 1;
      if (drill && next >= drill.targets.length) {
        setPhase("done");
        return i;
      }
      return next;
    });
  }, [drill]);

  // With "delete" turned on, what you typed can diverge from the target and
  // stay that way until you back it out.
  const wrongPrefix = useMemo(() => {
    if (!target) return false;
    return typed !== target.text.slice(0, typed.length);
  }, [target, typed]);

  /**
   * Note that a key was pressed, and close off any idle gap before it.
   *
   * Settling it here rather than in the tick means the gap taken out is
   * exactly the one you sat through, not one rounded to the nearest 100ms.
   */
  const touchClock = useCallback(() => {
    const now = Date.now();
    const resumeAt = lastTyped.current + IDLE_PAUSE_MS;
    if (idlePause && now > resumeAt) {
      if (resumeAt > spanFrom.current) {
        activeMs.current += resumeAt - spanFrom.current;
      }
      spanFrom.current = now;
      setPaused(false);
    }
    lastTyped.current = now;
  }, [idlePause]);

  const onKey = useCallback(
    (event: KeyboardEvent) => {
      if (!drill || tab !== "practice") return;
      if (event.ctrlKey || event.metaKey || event.altKey) return;

      // Arrows move between targets. They never produce a character, so they
      // can't collide with typing.
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        step(event.key === "ArrowLeft" ? -1 : 1);
        return;
      }
      if (phase === "done" && !reviewing) return;
      // While reviewing a finished run, only navigation does anything — the
      // score is already recorded and retyping into it would rewrite numbers
      // you've been given.
      if (reviewing) return;
      if (event.key === "Escape") {
        setPhase("idle");
        return;
      }

      if (event.key === "Backspace") {
        event.preventDefault();
        touchClock();
        setTyped((t) => t.slice(0, -1));
        return;
      }
      // Enter is the newline in a whole-function target. Everywhere else it
      // has no meaning, so it stays ignored rather than counting as a miss.
      const isNewline = event.key === "Enter";
      if (!isNewline && event.key.length !== 1) return;
      event.preventDefault();

      if (phase === "idle") {
        // The first keypress starts the clock rather than a countdown, so
        // there's nothing to sit through before you type.
        const now = Date.now();
        shownAt.current = now;
        activeMs.current = 0;
        spanFrom.current = now;
        lastTyped.current = now;
        setPaused(false);
        setPhase("running");
      } else {
        touchClock();
      }

      const current = drill.targets[index];
      if (!current) return;

      // An uncorrected mistake is already sitting there.
      //
      // In "Must delete" every key still lands, because that is what an editor
      // does: three wrong keys leave three characters and cost three
      // Backspaces. Bouncing them off meant a burst of typing past a mistake
      // was one character to undo, which taught the wrong reflex.
      //
      // Nothing is scored against an expected key here. Past the point where
      // what you typed and the target diverged there is no honest expectation
      // to measure against, so this counts as a miss and no more — the reason
      // the keys used to bounce in the first place.
      if (wrongPrefix) {
        const stray = isNewline ? NEWLINE : event.key;
        setFlash({ char: stray, ok: false, at: Date.now() });
        if (mistakes === "delete" && !isPerfect) {
          setMisses((n) => n + 1);
          setCombo(0);
          setTyped(typed + stray);
        }
        return;
      }

      const want = current.text[typed.length];
      if (want === undefined) return;
      const got = isNewline ? NEWLINE : event.key;
      const ok = got === want;

      // Time since the last keystroke, not since the line appeared. On a
      // reaction drill each target is one key, so the two are the same; on a
      // passage, only the per-key gap says which keys you hunt for.
      const now = Date.now();
      record(want, ok, now - shownAt.current);
      shownAt.current = now;
      setFlash({ char: got, ok, at: now });

      if (ok) {
        let nextTyped = typed + got;
        // An editor indents the new line for you, and counting spaces is not
        // the skill this is teaching. Pressing Enter carries you to the first
        // real character of the next line.
        if (isNewline) {
          nextTyped += leadingSpaceAt(current.text, nextTyped.length);
        }
        if (nextTyped.length >= current.text.length) advance();
        else setTyped(nextTyped);
        return;
      }

      // Wrong key. What happens next is the toggle.
      if (isPerfect) {
        setTyped("");
        setRestarts((n) => n + 1);
      } else if (mistakes === "delete") {
        setTyped(typed + got);
      }
      // "block" mode does nothing further — the key simply bounces off.
    },
    [
      advance,
      drill,
      index,
      isPerfect,
      mistakes,
      phase,
      record,
      reviewing,
      step,
      tab,
      touchClock,
      typed,
      wrongPrefix,
    ],
  );

  useEffect(() => {
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onKey]);

  // ── Derived numbers ───────────────────────────────────────

  const total = hits + misses;
  const accuracy = pct(hits, total);
  const clock = isTimed ? Math.min(elapsed, TIMED_SECONDS * 1000) : elapsed;
  const wpm = wpmOf(hits, clock);
  const remaining = Math.max(0, TIMED_SECONDS - Math.floor(clock / 1000));

  const avgReaction = useMemo(() => {
    let ms = 0;
    let n = 0;
    for (const stat of Object.values(stats)) {
      ms += stat.totalMs;
      n += stat.hits;
    }
    return n === 0 ? 0 : Math.round(ms / n);
  }, [stats]);

  const inScope = useMemo(() => {
    const chars = new Set<string>();
    for (const t of drill?.targets ?? []) {
      for (const ch of t.text) chars.add(ch.toLowerCase());
    }
    return chars;
  }, [drill]);

  /** Weakest keys first — the ones actually worth another round. */
  const weakest = useMemo(() => {
    return Object.entries(stats)
      .filter(([, s]) => s.hits + s.misses >= 3)
      .map(([char, s]) => ({
        char,
        accuracy: pct(s.hits, s.hits + s.misses),
        avgMs: s.hits === 0 ? 0 : Math.round(s.totalMs / s.hits),
      }))
      .sort((a, b) => a.accuracy - b.accuracy || b.avgMs - a.avgMs)
      .slice(0, 8);
  }, [stats]);

  // Record the run once it finishes. A run nobody typed isn't a run.
  useEffect(() => {
    if (phase !== "done" || !drill || submitted.current) return;
    if (total === 0) return;
    submitted.current = true;
    submitTypingRun({
      section: drill.section,
      mode: drill.mode,
      wpm,
      accuracy,
      reaction_ms: avgReaction,
      streak: bestCombo,
      keystrokes: total,
    })
      .then((result) => {
        setOutcome(result);
        setRecordRevision((n) => n + 1);
      })
      .catch(() => {
        /* a failed save shouldn't hide the results you just earned */
      });
  }, [accuracy, avgReaction, bestCombo, drill, phase, total, wpm]);

  // A "name to key" drill is asking you to remember where the key lives, so
  // lighting it up would answer the question. It stays dark until you get it
  // wrong — then showing you is the point.
  // Whole-function targets are source, so they set left and small — centred
  // code hides its own indentation, and prose-sized code costs the keyboard
  // the room it needs to stay on screen.
  const isBlock = modeId === "blocks";
  const byName = mode?.by_name ?? false;
  const revealKey = !byName || flash?.ok === false || reviewing;

  // Which drills actually read from a text source, and so have something for
  // the theme to change. Whole Functions belongs here above all: it is how you
  // choose the language, and hiding it left you typing code with nothing on
  // screen saying which language it was.
  const usesText = [
    "random",
    "words",
    "define",
    "speed",
    "perfect",
    "blocks",
  ].includes(modeId);

  /** The themes this mode can actually be driven by. */
  const themeChoices = useMemo(() => {
    const all = catalog?.themes ?? [];
    if (modeId === "words" || modeId === "define") {
      return all.filter((t) => t.has_words);
    }
    // Whole functions come from the code themes alone. Listing Scripture here
    // and quietly serving Python instead is worse than not listing it.
    if (modeId === "blocks") return all.filter((t) => t.has_blocks);
    return all;
  }, [catalog, modeId]);

  /** The instruction for modes whose task isn't obvious from the screen. */
  const taskLabel = useMemo(() => {
    if (reviewing) return "";
    if (modeId === "define") {
      return "Type the word that means this — one blank per letter";
    }
    if (modeId === "recall") return "Find this key — no help until you miss";
    if (modeId === "drill") {
      // Nonsense on purpose, and worth saying so: a run of random keys trains
      // the reach between them, which is the one thing real words can't.
      return "Random key runs — not words, just the reaches between keys";
    }
    if (modeId === "pairs") return "The pairs your hands should know as one move";
    return "";
  }, [modeId, reviewing]);

  /** What the single big character is, said in words. */
  const bigKeyName = useMemo(() => {
    const char = target?.text ?? "";
    if (!catalog || char.length !== 1) return "";
    if (char === " ") return "";
    const named = catalog.names[char];
    if (named) return named;
    if (/[a-z]/i.test(char)) return `letter ${char}`;
    if (/[0-9]/.test(char)) return `number ${char}`;
    return "";
  }, [catalog, target]);

  /**
   * A short punctuation target, named key by key.
   *
   * Only for short symbol runs: spelling out a whole sentence would be noise,
   * and letters name themselves. Shift is called out because a target like
   * `!=` gives no hint that one of its two keys needs it.
   */
  const spelled = useMemo(() => {
    const text = target?.text ?? "";
    if (!catalog || !text || text.length > 4) return "";
    const symbols = [...text].filter((c) => catalog.names[c]);
    if (symbols.length === 0) return "";
    // The keyboard model knows which characters need Shift: a character a key
    // produces only with Shift held.
    const needsShift = (c: string) =>
      catalog.keyboard.some((row) =>
        row.some((k) => k.shifted === c && k.char !== c),
      );

    const chars = [...text];
    const allShifted = chars.every(needsShift);
    const parts = chars.map((c) => {
      const name = catalog.names[c] ?? c;
      // Saying "(Shift)" after every one of three shifted keys is noise; say
      // it once at the end instead.
      return allShifted || !needsShift(c) ? name : `${name} (Shift)`;
    });
    const spellings = parts.join(", then ");
    return allShifted ? `${spellings} — all with Shift` : spellings;
  }, [catalog, target]);

  // ── Render ────────────────────────────────────────────────

  if (error) {
    // With the picker gone there was no way back from a failed load — the
    // trainer just sat there showing the error until the page was reloaded.
    return (
      <div className="typing-trainer">
        <div className="typing-error">Couldn't load that drill: {error}</div>
        <button
          type="button"
          className="typing-again"
          onClick={() => {
            setSectionId("everything");
            setModeId("random");
            setThemeId("mixed");
            void loadDrill("everything", "random", "mixed");
          }}
        >
          Start over
        </button>
      </div>
    );
  }
  if (!catalog || !drill || !section) {
    return <div className="typing-loading">Loading the keyboard…</div>;
  }

  const progress = isTimed
    ? pct(clock, TIMED_SECONDS * 1000)
    : pct(index, drill.targets.length);

  const tabs: [Tab, string][] = [
    ["practice", "Practice"],
    ["course", "Course"],
    ["learn", "Learn"],
    ["records", "Records"],
  ];

  return (
    <div className="typing-trainer">
      <div className="typing-tabs">
        {tabs.map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={`typing-tab ${tab === id ? "on" : ""}`}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "course" && (
        <TypingCoursePanel revision={recordRevision} onStart={jumpTo} />
      )}
      {tab === "learn" && <TypingGuidePanel />}
      {tab === "records" && (
        <TypingRecords revision={recordRevision} onPick={jumpTo} />
      )}

      {tab === "practice" && (
        <>
          {/* Eighteen sections and eleven modes as chips was a wall of
              buttons. Two named dropdowns say the same thing in one line and
              make it obvious which choice is which. */}
          <div className="typing-picker">
            <div className="typing-controls">
              <label className="typing-field">
                <span>Keys</span>
                <select
                  value={sectionId}
                  onChange={(e) => {
                    const next = catalog.sections.find(
                      (s) => s.id === e.target.value,
                    );
                    if (next) chooseSection(next);
                  }}
                >
                  {catalog.sections.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </label>

              <label className="typing-field">
                <span>Drill</span>
                <select
                  value={modeId}
                  onChange={(e) => chooseMode(e.target.value)}
                >
                  {section.modes.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </label>

              <div
                className="typing-toggle"
                title={
                  mistakes === "block"
                    ? "Wrong keys bounce off. Keeps a drill flowing."
                    : "Wrong keys land and you back them out, like a real editor."
                }
              >
                <span>Mistakes</span>
                <button
                  type="button"
                  className={mistakes === "block" ? "on" : ""}
                  onClick={() => setMistakes("block")}
                >
                  Block
                </button>
                <button
                  type="button"
                  className={mistakes === "delete" ? "on" : ""}
                  onClick={() => setMistakes("delete")}
                >
                  Must delete
                </button>
              </div>

              <div
                className="typing-toggle"
                title={
                  showWpm
                    ? "Speed is on screen while you type."
                    : "Speed is hidden. Runs are still recorded — the Records tab has them when you want them."
                }
              >
                <span>wpm</span>
                <button
                  type="button"
                  className={showWpm ? "on" : ""}
                  onClick={() => setShowWpm(true)}
                >
                  Show
                </button>
                <button
                  type="button"
                  className={!showWpm ? "on" : ""}
                  onClick={() => setShowWpm(false)}
                >
                  Hide
                </button>
              </div>

              <div
                className="typing-toggle"
                title={
                  idlePause
                    ? "The clock stops after two seconds of nothing, so reading ahead or hunting for a key doesn't cost you speed."
                    : "The clock runs from your first keypress to your last, pauses included."
                }
              >
                <span>Clock</span>
                <button
                  type="button"
                  className={idlePause ? "on" : ""}
                  onClick={() => setIdlePause(true)}
                >
                  Pause
                </button>
                <button
                  type="button"
                  className={!idlePause ? "on" : ""}
                  onClick={() => setIdlePause(false)}
                >
                  Always
                </button>
              </div>

              {/* Only the text-based drills have text to theme. Offering it
                  on Whack-a-Key would be a control that does nothing. */}
              {usesText && (
                <label className="typing-field">
                  <span>Text</span>
                  <select
                    value={themeId}
                    onChange={(e) => chooseTheme(e.target.value)}
                  >
                    {themeChoices.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name}
                      </option>
                    ))}
                  </select>
                </label>
              )}

              <button
                type="button"
                className="typing-restart"
                onClick={() => void loadDrill(sectionId, modeId, themeId)}
                title="A fresh set from the same drill"
              >
                New set
              </button>
            </div>
            <p className="typing-blurb">
              {mode?.description ?? section.description}
            </p>
          </div>

          <div className="typing-hud">
            <div className="typing-hud-stats">
            {showWpm && (
              <Stat
                label="wpm"
                value={phase === "idle" ? "—" : String(wpm)}
                note={paused ? "paused" : undefined}
              />
            )}
            <Stat label="accuracy" value={total === 0 ? "—" : `${accuracy}%`} />
            <Stat
              label="reaction"
              value={avgReaction === 0 ? "—" : `${avgReaction}ms`}
            />
            <Stat label="streak" value={String(combo)} highlight={combo >= 10} />
            {isTimed && (
              <Stat
                label="seconds left"
                value={phase === "idle" ? String(TIMED_SECONDS) : String(remaining)}
                highlight={phase === "running" && remaining <= 10}
              />
            )}
            {isPerfect && <Stat label="restarts" value={String(restarts)} />}
            </div>

            {/* Pinned to the stats row on purpose. Sitting under the target,
                these moved every time a line was a different height, so the
                button was somewhere else by the time you reached it. */}
            {(phase !== "done" || reviewing) && (
              <div className="typing-steps">
                <button
                  type="button"
                  onClick={() => step(-1)}
                  disabled={index === 0}
                  title="Look at the one you just did (left arrow)"
                >
                  ‹ Back
                </button>
                <span className="typing-steps-count">
                  {index + 1} of {drill.targets.length}
                </span>
                <button
                  type="button"
                  onClick={() => step(1)}
                  disabled={index >= drill.targets.length - 1}
                  title="Move on without typing this one (right arrow)"
                >
                  {reviewing ? "Next ›" : "Skip ›"}
                </button>
                {reviewing && (
                  <button
                    type="button"
                    className="typing-steps-done"
                    onClick={() => setReviewing(false)}
                  >
                    Back to results
                  </button>
                )}
              </div>
            )}
          </div>

          {phase === "done" && !reviewing ? (
            <div className="typing-results">
              <h3>Run complete</h3>
              {outcome && (
                <div className="typing-bests">
                  {showWpm && outcome.beat_wpm && (
                    <span className="tr-best">new best wpm</span>
                  )}
                  {outcome.beat_accuracy && (
                    <span className="tr-best">new best accuracy</span>
                  )}
                  {outcome.beat_reaction && (
                    <span className="tr-best">fastest reaction</span>
                  )}
                  {outcome.beat_streak && (
                    <span className="tr-best">longest streak</span>
                  )}
                  {!(showWpm && outcome.beat_wpm) &&
                    !outcome.beat_accuracy &&
                    !outcome.beat_reaction &&
                    !outcome.beat_streak &&
                    (outcome.record.best_wpm > 0 ? (
                      <span className="tr-prev">
                        {showWpm
                          ? `Your best here: ${outcome.record.best_wpm} wpm · ` +
                            `${outcome.record.best_accuracy}% · run ${outcome.record.runs}`
                          : `Your best accuracy here: ` +
                            `${outcome.record.best_accuracy}% · run ${outcome.record.runs}`}
                      </span>
                    ) : (
                      <span className="tr-prev">
                        Run {outcome.record.runs} — too short to set a record.
                      </span>
                    ))}
                </div>
              )}
              <div className="typing-result-grid">
                {showWpm && <Stat label="wpm" value={String(wpm)} big />}
                <Stat label="accuracy" value={`${accuracy}%`} big />
                <Stat
                  label="avg reaction"
                  value={avgReaction === 0 ? "—" : `${avgReaction}ms`}
                  big
                />
                <Stat label="best streak" value={String(bestCombo)} big />
              </div>
              {weakest.length > 0 && (
                <>
                  <h4>Keys worth another round</h4>
                  <div className="typing-weak">
                    {weakest.map((w) => (
                      <div className="typing-weak-key" key={w.char}>
                        <span className="typing-weak-char">
                          {w.char === " " ? "space" : w.char}
                        </span>
                        <span className="typing-weak-num">{w.accuracy}%</span>
                        <span className="typing-weak-ms">{w.avgMs}ms</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
              <div className="typing-result-actions">
                <button
                  type="button"
                  className="typing-again"
                  onClick={() => void loadDrill(sectionId, modeId, themeId)}
                >
                  Go again
                </button>
                <button
                  type="button"
                  className="typing-review"
                  onClick={() => {
                    setReviewing(true);
                    setIndex(0);
                    setTyped("");
                  }}
                >
                  Look back through it
                </button>
              </div>
            </div>
          ) : (
            <div className={`typing-stage ${isReaction ? "reaction" : "text"}`}>
              {reviewing ? (
                <p className="typing-reviewing">
                  Looking back — arrows to move
                </p>
              ) : phase === "idle" ? (
                <p className="typing-start">
                  {isTimed
                    ? `Press any key to start the ${TIMED_SECONDS} seconds.`
                    : "Press any key to start."}
                </p>
              ) : null}

              {isReaction ? (
                <div className="typing-single">
                  {taskLabel && <p className="typing-task">{taskLabel}</p>}
                  <div
                    className={`typing-bigkey ${
                      flash?.ok === false ? "wrong" : ""
                    }`}
                    key={index}
                  >
                    {target?.prompt === " " ? "space" : target?.prompt}
                  </div>
                  {/* One character on its own is genuinely ambiguous — a `c`
                      at this size reads as a bracket. Naming it removes the
                      guess. Left off the by-name modes, where the name is the
                      question. */}
                  {!byName && bigKeyName && (
                    <div className="typing-bigkey-name">{bigKeyName}</div>
                  )}
                  {/* Name to Key asked you to remember where a symbol lives.
                      Reviewing it without showing the answer would repeat the
                      question rather than answer it. */}
                  {reviewing && target && target.prompt !== target.text && (
                    <div className="typing-answer">{target.text}</div>
                  )}
                  {target?.shift && revealKey && (
                    <div className="typing-shift">with Shift</div>
                  )}
                </div>
              ) : (
                <div className="typing-line">
                  {target && (
                    <>
                      {/* What the mode is actually asking for. Meaning to
                          Word shows a definition and a row of blanks, and
                          without a sentence saying so that is a puzzle about
                          the app rather than about the word. */}
                      {taskLabel && <p className="typing-task">{taskLabel}</p>}
                      {drill.hidden && target.prompt !== target.text ? (
                        <p className="typing-cue">{target.prompt}</p>
                      ) : null}
                      <p
                        className={`typing-text ${wrongPrefix ? "bad" : ""}${
                          isBlock ? " block" : ""
                        }`}
                      >
                        {(drill.hidden &&
                        target.prompt !== target.text &&
                        !reviewing
                          ? "_".repeat(target.text.length)
                          : target.text
                        )
                          .split("")
                          .map((ch, i) => {
                            const state =
                              i < typed.length
                                ? typed[i] === ch
                                  ? "done"
                                  : "bad"
                                : i === typed.length
                                  ? "at"
                                  : "todo";
                            // A newline is a key you have to press, so it has
                            // to be a thing you can see and put a cursor on.
                            // Without the arrow, Enter is an invisible target.
                            if (ch === NEWLINE) {
                              return (
                                <span key={i} className={`${state} nl`}>
                                  {RETURN_GLYPH}
                                  {NEWLINE}
                                </span>
                              );
                            }
                            return (
                              <span key={i} className={state}>
                                {ch}
                              </span>
                            );
                          })}
                        {/* Anything typed past the end of the line is wrong by
                            definition, and has to be visible to be deleted. */}
                        {typed.length > target.text.length && (
                          <span className="bad">
                            {typed.slice(target.text.length)}
                          </span>
                        )}
                      </p>
                    </>
                  )}
                </div>
              )}

              {/* Symbol targets spelled out. `!=` is two keys and one of them
                  needs Shift, and neither of those facts is visible in the
                  two characters themselves. */}
              {spelled && <p className="typing-spelled">{spelled}</p>}

              {/* Always in the layout, only sometimes visible. Appearing on a
                  mistake pushed everything below it down, which on a screen
                  that just fits meant a scrollbar arriving exactly when you
                  least want the page to move. */}
              <p className={`typing-fix${wrongPrefix ? "" : " quiet"}`}>
                Backspace to fix
              </p>
              {target?.note && <p className="typing-note">{target.note}</p>}

              <div className="typing-progress">
                <div
                  className="typing-progress-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>

            </div>
          )}

          <TypingKeyboard
            layout={catalog.keyboard}
            fingers={catalog.fingers}
            target={
              (phase === "done" && !reviewing) || !revealKey
                ? null
                : (target?.text[typed.length] ?? null)
            }
            flash={flash}
            stats={stats}
            inScope={inScope}
            showHeat={phase === "done" || total > 12}
          />
        </>
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  big,
  highlight,
  note,
}: {
  label: string;
  value: string;
  big?: boolean;
  highlight?: boolean;
  /** A word about the number's state — "paused" while the clock is stopped. */
  note?: string;
}) {
  return (
    <div
      className={`typing-stat ${big ? "big" : ""} ${highlight ? "hot" : ""} ${
        note ? "noted" : ""
      }`}
    >
      <span className="typing-stat-value">{value}</span>
      <span className="typing-stat-label">
        {label}
        {note ? <span className="typing-stat-note">{note}</span> : null}
      </span>
    </div>
  );
}
