import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchTypingCatalog, fetchTypingDrill } from "../api";
import type { TypingCatalog, TypingDrill, TypingSection } from "../types";
import TypingKeyboard, { type KeyStat } from "./TypingKeyboard";

/**
 * The typing trainer.
 *
 * Two shapes of drill share this screen. Reaction drills show one key at a
 * time with nothing ahead of it, and are scored on how fast you find it. Text
 * drills show a whole line and are scored on words a minute. Both feed the
 * same per-key history, which is what the results heatmap is drawn from —
 * the useful output isn't the score, it's knowing which keys you hunt for.
 */

type Phase = "idle" | "running" | "done";

type Flash = { char: string; ok: boolean; at: number };

/** Words a minute, using the standard five-characters-is-a-word convention. */
function wpmOf(chars: number, ms: number): number {
  if (ms <= 0) return 0;
  return Math.round(chars / 5 / (ms / 60000));
}

function pct(n: number, d: number): number {
  return d === 0 ? 100 : Math.round((n / d) * 100);
}

export default function TypingTrainer() {
  const [catalog, setCatalog] = useState<TypingCatalog | null>(null);
  const [sectionId, setSectionId] = useState("home");
  const [modeId, setModeId] = useState("whack");
  const [drill, setDrill] = useState<TypingDrill | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [phase, setPhase] = useState<Phase>("idle");
  const [index, setIndex] = useState(0);
  const [typed, setTyped] = useState("");
  const [flash, setFlash] = useState<Flash | null>(null);
  const [combo, setCombo] = useState(0);
  const [bestCombo, setBestCombo] = useState(0);
  const [stats, setStats] = useState<Record<string, KeyStat>>({});
  const [hits, setHits] = useState(0);
  const [misses, setMisses] = useState(0);
  const [startedAt, setStartedAt] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  // When the current target appeared, so a reaction time means something.
  const shownAt = useRef(0);
  const stageRef = useRef<HTMLDivElement>(null);

  const section = useMemo(
    () => catalog?.sections.find((s) => s.id === sectionId) ?? null,
    [catalog, sectionId],
  );
  const target = drill?.targets[index] ?? null;
  const isReaction = drill?.scoring === "reaction";

  // ── Loading ───────────────────────────────────────────────

  useEffect(() => {
    fetchTypingCatalog()
      .then(setCatalog)
      .catch((e: Error) => setError(e.message));
  }, []);

  const loadDrill = useCallback(
    async (nextSection: string, nextMode: string) => {
      setError(null);
      try {
        const seed = String(Date.now());
        const next = await fetchTypingDrill(nextSection, nextMode, seed);
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
        setElapsed(0);
      } catch (e) {
        setError((e as Error).message);
      }
    },
    [],
  );

  // Picking a section whose modes don't include the current one has to land
  // somewhere valid — Bottom Row has no word list, so Words isn't offered.
  const chooseSection = useCallback(
    (next: TypingSection) => {
      const keepMode = next.modes.some((m) => m.id === modeId)
        ? modeId
        : next.modes[0].id;
      setSectionId(next.id);
      setModeId(keepMode);
      void loadDrill(next.id, keepMode);
    },
    [loadDrill, modeId],
  );

  const chooseMode = useCallback(
    (next: string) => {
      setModeId(next);
      void loadDrill(sectionId, next);
    },
    [loadDrill, sectionId],
  );

  useEffect(() => {
    if (catalog && !drill) void loadDrill(sectionId, modeId);
  }, [catalog, drill, loadDrill, modeId, sectionId]);

  // ── The clock ─────────────────────────────────────────────

  useEffect(() => {
    if (phase !== "running") return;
    const id = window.setInterval(() => {
      setElapsed(Date.now() - startedAt);
    }, 100);
    return () => window.clearInterval(id);
  }, [phase, startedAt]);

  // Clear the hit/miss flash shortly after it fires.
  useEffect(() => {
    if (!flash) return;
    const id = window.setTimeout(() => setFlash(null), 180);
    return () => window.clearTimeout(id);
  }, [flash]);

  // ── Scoring one keypress ──────────────────────────────────

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

  const onKey = useCallback(
    (event: KeyboardEvent) => {
      if (!drill || phase === "done") return;
      // Let the browser keep its own shortcuts.
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      if (event.key === "Escape") {
        setPhase("idle");
        return;
      }
      if (event.key.length !== 1 && event.key !== "Enter") return;
      event.preventDefault();

      if (phase === "idle") {
        // The first keypress starts the clock rather than a countdown, so
        // there's nothing to sit through before you type.
        const now = Date.now();
        setStartedAt(now);
        shownAt.current = now;
        setPhase("running");
        if (event.key.length !== 1) return;
      }

      const current = drill.targets[index];
      if (!current) return;
      const want = current.text[typed.length];
      const got = event.key;
      if (want === undefined) return;

      const ok = got === want;
      // Time since the last keystroke, not since the line appeared. On a
      // reaction drill each target is one key, so the two are the same; on a
      // passage, only the per-key gap says anything about which keys you hunt
      // for.
      const now = Date.now();
      const ms = now - shownAt.current;
      shownAt.current = now;
      record(want, ok, ms);
      setFlash({ char: got, ok, at: Date.now() });

      if (!ok) return; // A wrong key doesn't advance — you fix it and go on.

      const nextTyped = typed + got;
      if (nextTyped.length >= current.text.length) {
        advance();
      } else {
        setTyped(nextTyped);
      }
    },
    [advance, drill, index, phase, record, typed],
  );

  useEffect(() => {
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onKey]);

  // ── Derived numbers ───────────────────────────────────────

  const total = hits + misses;
  const accuracy = pct(hits, total);
  const wpm = wpmOf(hits, elapsed);
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

  // A "name to key" drill is asking you to remember where the key lives, so
  // lighting it up on the board would answer the question for you. It stays
  // dark until you get it wrong — then showing you is the point.
  const byName =
    section?.modes.find((m) => m.id === modeId)?.by_name ?? false;
  const revealKey = !byName || flash?.ok === false;

  // ── Render ────────────────────────────────────────────────

  if (error) {
    return <div className="typing-error">Couldn't load the trainer: {error}</div>;
  }
  if (!catalog || !drill || !section) {
    return <div className="typing-loading">Loading the keyboard…</div>;
  }

  const progress = pct(index, drill.targets.length);

  return (
    <div className="typing-trainer" ref={stageRef}>
      <div className="typing-picker">
        <div className="typing-sections">
          {catalog.sections.map((s) => (
            <button
              key={s.id}
              type="button"
              className={`typing-chip ${s.id === sectionId ? "on" : ""}`}
              onClick={() => chooseSection(s)}
            >
              {s.name}
            </button>
          ))}
        </div>
        <div className="typing-modes">
          {section.modes.map((m) => (
            <button
              key={m.id}
              type="button"
              className={`typing-mode ${m.id === modeId ? "on" : ""}`}
              onClick={() => chooseMode(m.id)}
              title={m.description}
            >
              {m.name}
            </button>
          ))}
        </div>
        <p className="typing-blurb">
          {section.modes.find((m) => m.id === modeId)?.description ??
            section.description}
        </p>
      </div>

      <div className="typing-hud">
        <Stat label="wpm" value={phase === "idle" ? "—" : String(wpm)} />
        <Stat label="accuracy" value={total === 0 ? "—" : `${accuracy}%`} />
        <Stat
          label="reaction"
          value={avgReaction === 0 ? "—" : `${avgReaction}ms`}
        />
        <Stat label="streak" value={String(combo)} highlight={combo >= 10} />
      </div>

      {phase === "done" ? (
        <div className="typing-results">
          <h3>Run complete</h3>
          <div className="typing-result-grid">
            <Stat label="wpm" value={String(wpm)} big />
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
          <button
            type="button"
            className="typing-again"
            onClick={() => void loadDrill(sectionId, modeId)}
          >
            Go again
          </button>
        </div>
      ) : (
        <div className={`typing-stage ${isReaction ? "reaction" : "text"}`}>
          {phase === "idle" && (
            <p className="typing-start">Press any key to start.</p>
          )}

          {isReaction ? (
            <div className="typing-single">
              <div
                className={`typing-bigkey ${flash?.ok === false ? "wrong" : ""}`}
                key={index}
              >
                {target?.prompt === " " ? "space" : target?.prompt}
              </div>
              {target?.shift && revealKey && (
                <div className="typing-shift">with Shift</div>
              )}
            </div>
          ) : (
            <div className="typing-line">
              {target && (
                <>
                  {drill.hidden && target.prompt !== target.text ? (
                    <p className="typing-cue">{target.prompt}</p>
                  ) : null}
                  <p className="typing-text">
                    {(drill.hidden && target.prompt !== target.text
                      ? "_".repeat(target.text.length)
                      : target.text
                    )
                      .split("")
                      .map((ch, i) => (
                        <span
                          key={i}
                          className={
                            i < typed.length
                              ? "done"
                              : i === typed.length
                                ? "at"
                                : "todo"
                          }
                        >
                          {ch}
                        </span>
                      ))}
                  </p>
                </>
              )}
            </div>
          )}

          {target?.note && <p className="typing-note">{target.note}</p>}

          {/* What's coming, unless the mode is meant to hide it. */}
          {!drill.hidden && (
            <div className="typing-upnext">
              {drill.targets.slice(index + 1, index + 4).map((t, i) => (
                <span key={i}>{t.prompt}</span>
              ))}
            </div>
          )}

          <div className="typing-progress">
            <div className="typing-progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      <TypingKeyboard
        layout={catalog.keyboard}
        fingers={catalog.fingers}
        target={
          phase === "done" || !revealKey
            ? null
            : (target?.text[typed.length] ?? null)
        }
        flash={flash}
        stats={stats}
        inScope={inScope}
        showHeat={phase === "done" || total > 12}
      />
    </div>
  );
}

function Stat({
  label,
  value,
  big,
  highlight,
}: {
  label: string;
  value: string;
  big?: boolean;
  highlight?: boolean;
}) {
  return (
    <div className={`typing-stat ${big ? "big" : ""} ${highlight ? "hot" : ""}`}>
      <span className="typing-stat-value">{value}</span>
      <span className="typing-stat-label">{label}</span>
    </div>
  );
}
