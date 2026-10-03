/**
 * Farm: The Farmer Was Replaced, in Python, JavaScript or Dart.
 *
 * The code goes on the left, the farm on the right, and the program runs
 * for real - a Python, Node or Dart process whose every drone command is
 * done by the farm in the server and paced to game time. This screen just
 * watches: it polls the farm a few times a second while a program runs
 * (and every half second when none does, because the farm keeps growing)
 * and draws whatever it is told.
 *
 * Research is the game's: harvest, spend the harvest on unlocks, and the
 * unlocks give the drone new commands and you new parts of the language.
 * A program that uses a part you have not bought yet is refused before it
 * runs, with the line and the unlock it needs.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  buyFarmUnlock,
  fetchFarm,
  fetchFarmState,
  keepFarmCode,
  resetFarm,
  runFarm,
  setFarmWarp,
  stopFarm,
} from "../api";
import { drawFarm } from "../lib/farmDraw";
import type { FarmFunction, FarmLine, FarmOverview, FarmState, FarmUnlock, FarmViolation } from "../types";
import { EditorPane } from "./EditorPane";
import "../styles/farm.css";

const LANGUAGE_NAMES: Record<string, string> = { python: "Python", javascript: "JavaScript", dart: "Dart" };
const FILE_NAMES: Record<string, string> = { python: "farm.py", javascript: "farm.js", dart: "farm.dart" };
const FEATURE_UNLOCKS: Record<string, string> = {
  while: "Loops", if: "Speed", for: "Expand 2", operators: "Operators", variables: "Variables",
  functions: "Functions", lists: "Lists", dicts: "Dictionaries", import: "Import",
};

/** Items.Weird_Substance, spelled the way each language spells it. */
function spellValue(group: string, member: string, language: string): string {
  const pascal = member.split("_").map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join("");
  if (group === "Directions") return language === "dart" ? member.toLowerCase() : member;
  if (language === "javascript") return `${group}.${pascal}`;
  if (language === "dart") return `${group}.${pascal.charAt(0).toLowerCase()}${pascal.slice(1)}`;
  return `${group}.${member}`;
}

function itemName(item: string): string {
  return item.replace(/_/g, " ");
}

function costText(cost: Record<string, number> | null): string {
  if (!cost) return "";
  return Object.entries(cost)
    .map(([item, n]) => `${n.toLocaleString()} ${itemName(item)}`)
    .join(" + ");
}

/** How a function reads in the chosen language, with its parameters. */
function signature(f: FarmFunction, language: string): string {
  const name = language === "javascript" ? f.js : language === "dart" ? f.dart : f.py;
  const params = f.params.map((p) => {
    const bare = p.replace(/=.*/, "").replace(/^\*/, language === "python" ? "*" : "...");
    if (language === "python") return p;
    return p.includes("=") ? `${bare}?` : bare;
  });
  return `${name}(${params.join(", ")})`;
}

export default function FarmMode() {
  const [overview, setOverview] = useState<FarmOverview | null>(null);
  const [state, setState] = useState<FarmState | null>(null);
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState<Record<string, string>>({});
  const [revision, setRevision] = useState(0);
  const [lines, setLines] = useState<FarmLine[]>([]);
  const [violations, setViolations] = useState<FarmViolation[]>([]);
  const [panel, setPanel] = useState<"research" | "docs" | null>("research");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const sinceRef = useRef(0);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const boxRef = useRef<HTMLDivElement | null>(null);
  const [px, setPx] = useState(480);
  const codeRef = useRef(code);
  codeRef.current = code;
  const saveTimer = useRef<number | null>(null);

  const apply = useCallback((o: FarmOverview) => {
    setOverview(o);
    setState(o);
  }, []);

  useEffect(() => {
    fetchFarm()
      .then((o) => {
        apply(o);
        setLanguage(o.languages.includes(o.language) ? o.language : "python");
        setCode(o.code);
        setRevision((r) => r + 1);
        sinceRef.current = o.outputEnd;
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, [apply]);

  const running = state?.run?.status === "running" || state?.run?.status === "starting";

  // Watch the farm: often while a program runs, now and then while it grows by itself.
  useEffect(() => {
    if (!overview) return;
    let alive = true;
    const tick = async () => {
      try {
        const s = await fetchFarmState(sinceRef.current);
        if (!alive) return;
        setState(s);
        if (s.output.length) {
          setLines((was) => [...was, ...s.output].slice(-400));
        }
        sinceRef.current = s.outputEnd;
      } catch {
        /* the next poll will try again */
      }
    };
    const id = window.setInterval(tick, running ? 120 : 500);
    return () => {
      alive = false;
      window.clearInterval(id);
    };
  }, [overview, running]);

  // When a run ends, the research list may have changed (unlock() from code, new items).
  const lastStatus = useRef<string | undefined>(undefined);
  useEffect(() => {
    const status = state?.run?.status;
    if (lastStatus.current && lastStatus.current !== status && !running) {
      fetchFarm().then(apply).catch(() => undefined);
    }
    lastStatus.current = status;
  }, [state?.run?.status, running, apply]);

  // Fit the farm to its column.
  useEffect(() => {
    const el = boxRef.current;
    if (!el) return;
    const fit = () => setPx(Math.max(240, Math.min(620, Math.floor(el.clientWidth))));
    fit();
    const watcher = new ResizeObserver(fit);
    watcher.observe(el);
    return () => watcher.disconnect();
  }, [overview]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !state) return;
    const ctx = canvas.getContext("2d");
    if (ctx) drawFarm(ctx, state.farm, px);
  }, [state, px]);

  const onChange = useCallback(
    (value: string) => {
      setCode((was) => ({ ...was, [language]: value }));
      if (saveTimer.current) window.clearTimeout(saveTimer.current);
      saveTimer.current = window.setTimeout(() => {
        void keepFarmCode(language, value);
      }, 800);
    },
    [language],
  );

  const pickLanguage = useCallback(
    (next: string) => {
      if (next === language) return;
      setLanguage(next);
      setRevision((r) => r + 1);
      setViolations([]);
      void keepFarmCode(next, codeRef.current[next] ?? "");
    },
    [language],
  );

  const run = useCallback(async () => {
    if (busy) return;
    setBusy(true);
    setError("");
    setViolations([]);
    try {
      const got = await runFarm(language, codeRef.current[language] ?? "");
      if (!got.ok) {
        if (got.violations?.length) setViolations(got.violations);
        else setError(got.error ?? "Could not start the program.");
      } else {
        setLines([]);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }, [busy, language]);

  const stop = useCallback(() => {
    void stopFarm();
  }, []);

  const buy = useCallback(
    async (name: string) => {
      try {
        const got = await buyFarmUnlock(name);
        apply(got);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [apply],
  );

  const warp = useCallback(async (value: number) => {
    await setFarmWarp(value);
    setState((s) => (s ? { ...s, warp: value } : s));
  }, []);

  const startOver = useCallback(async () => {
    if (!window.confirm("Start the farm over? Every item and every unlock goes.")) return;
    const o = await resetFarm();
    apply(o);
    setLines([]);
  }, [apply]);

  const unlocks = useMemo(() => {
    const list = overview?.unlocks ?? [];
    const rank = (u: FarmUnlock) =>
      u.missing ? 4 : u.available ? (u.affordable ? 0 : 1) : u.level > 0 ? 2 : 3;
    return [...list].sort((a, b) => rank(a) - rank(b));
  }, [overview]);

  if (error && !overview) return <div className="lessons-empty">Could not load the farm: {error}</div>;
  if (!overview || !state) return <div className="lessons-empty">Loading the farm…</div>;

  const items = Object.entries(state.items).filter(([, n]) => n > 0);
  const run_ = state.run;
  const features = new Set(overview.features);

  return (
    <div className="farm-wrap">
      <section className="farm-code">
        <div className="farm-bar">
          <div className="farm-langs" role="tablist" aria-label="Language">
            {overview.languages.map((lang) => (
              <button
                key={lang}
                type="button"
                role="tab"
                aria-selected={lang === language}
                className={`ws-btn${lang === language ? " on" : ""}`}
                onClick={() => pickLanguage(lang)}
                disabled={running}
              >
                {LANGUAGE_NAMES[lang] ?? lang}
              </button>
            ))}
          </div>
          <div className="farm-actions">
            {running ? (
              <button type="button" className="ws-btn primary" onClick={stop}>
                Stop
              </button>
            ) : (
              <button
                type="button"
                className="ws-btn primary"
                onClick={() => void run()}
                disabled={busy}
                title="Run (Ctrl+Enter)"
              >
                {busy ? "Starting…" : "Run"}
              </button>
            )}
            <label className="farm-warp" title="Time warp: how many game seconds pass per real second">
              Warp
              <select value={state.warp} onChange={(e) => void warp(Number(e.target.value))}>
                {overview.warps.map((w) => (
                  <option key={w} value={w}>
                    {w === 0 ? "max" : `${w}×`}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
        <div className="farm-editor">
          <EditorPane
            code={code[language] ?? ""}
            revision={revision}
            onChange={onChange}
            onRun={() => void run()}
            language={language}
            fileName={FILE_NAMES[language]}
          />
        </div>
        <div className="farm-output" aria-live="polite">
          {violations.map((v, i) => (
            <div key={`v${i}`} className="farm-line error">
              Line {v.line}: {v.message} <code>{v.snippet}</code>
            </div>
          ))}
          {error ? <div className="farm-line error">{error}</div> : null}
          {lines.length === 0 && !violations.length && !error ? (
            <div className="farm-line info">Output, and anything you quick_print, shows here.</div>
          ) : null}
          {lines.map((l, i) => (
            <div key={i} className={`farm-line ${l.kind}`}>
              {l.text}
            </div>
          ))}
        </div>
      </section>

      <section className="farm-field">
        <div className="farm-items">
          {items.length === 0 ? <span className="farm-item muted">Nothing harvested yet</span> : null}
          {items.map(([item, n]) => (
            <span key={item} className="farm-item" title={item}>
              <b>{n.toLocaleString()}</b> {itemName(item)}
            </span>
          ))}
        </div>
        <div ref={boxRef} className="farm-canvas-box">
          <canvas ref={canvasRef} width={px} height={px} className="farm-canvas" />
        </div>
        <div className="farm-status">
          <span>
            {state.farm.w}×{state.farm.h} · time {state.farm.time.toFixed(1)}s · speed {state.farm.speed}×
          </span>
          {run_ ? (
            <span className={`farm-run ${run_.status}`}>
              {run_.status === "running"
                ? `running · ${run_.commands} commands`
                : run_.status === "error"
                  ? `stopped with an error${run_.line ? ` on line ${run_.line}` : ""}`
                  : run_.status}
            </span>
          ) : null}
        </div>
        <div className="farm-tabs">
          <button
            type="button"
            className={`ws-btn${panel === "research" ? " on" : ""}`}
            onClick={() => setPanel(panel === "research" ? null : "research")}
          >
            Research
          </button>
          <button
            type="button"
            className={`ws-btn${panel === "docs" ? " on" : ""}`}
            onClick={() => setPanel(panel === "docs" ? null : "docs")}
          >
            Commands
          </button>
          <button type="button" className="ws-btn farm-reset" onClick={() => void startOver()}>
            Start over
          </button>
        </div>

        {panel === "research" ? (
          <div className="farm-panel">
            {unlocks.map((u) => {
              const maxed = u.cost === null;
              return (
                <div
                  key={u.name}
                  className={`farm-unlock${u.available ? " open" : ""}${u.affordable && u.available ? " ready" : ""}${maxed ? " done" : ""}`}
                >
                  <div className="farm-unlock-head">
                    <strong>{u.name.replace(/_/g, " ")}</strong>
                    {u.upgradable || u.level > 0 ? (
                      <span className="farm-level">
                        {u.level}/{u.max}
                      </span>
                    ) : null}
                    {u.missing ? <span className="farm-level">not in Code Coach yet</span> : null}
                    {u.available ? (
                      <button
                        type="button"
                        className="ws-btn primary"
                        disabled={!u.affordable}
                        onClick={() => void buy(u.name)}
                      >
                        {u.level > 0 && u.upgradable ? "Upgrade" : "Unlock"} · {costText(u.cost)}
                      </button>
                    ) : null}
                  </div>
                  <p>{u.about}</p>
                  {!u.available && !maxed && !u.missing ? (
                    <p className="farm-needs">Needs {u.needs.join(" and ") || "nothing"}.</p>
                  ) : null}
                </div>
              );
            })}
          </div>
        ) : null}

        {panel === "docs" ? (
          <div className="farm-panel">
            <p className="farm-needs">
              Language you have:{" "}
              {Object.keys(FEATURE_UNLOCKS).map((f) => (
                <span key={f} className={`farm-feature${features.has(f) ? " on" : ""}`} title={`From ${FEATURE_UNLOCKS[f]}`}>
                  {f}
                </span>
              ))}
            </p>
            {Object.entries(overview.names ?? {}).map(([group, members]) => (
              <p key={group} className="farm-values">
                <span className="farm-needs">{group}: </span>
                {members.map((m) => (
                  <code key={m}>{spellValue(group, m, language)}</code>
                ))}
              </p>
            ))}
            {overview.functions
              .slice()
              .sort((a, b) => Number(b.unlocked) - Number(a.unlocked))
              .map((f) => (
                <div key={f.py} className={`farm-fn${f.unlocked ? "" : " locked"}`}>
                  <code>{signature(f, language)}</code>
                  <span>{f.unlocked ? f.doc : `needs ${f.unlock}`}</span>
                </div>
              ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}
