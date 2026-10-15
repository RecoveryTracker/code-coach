/**
 * Farm: The Farmer Was Replaced, in Original, Python, JavaScript or Dart.
 *
 * Laid out like the game: the farm fills the whole screen (FarmScene), and everything
 * else floats over it - a HUD across the top, a menu bottom-left, and windows you can
 * drag, resize, fold up and close (Code, Output, Research, Docs, Playbook).
 *
 * The program runs for real - a Python, Node or Dart process whose every drone command
 * is done by the farm in the server and paced to game time. This screen just watches:
 * it polls the farm a few times a second while a program runs (and every half second
 * when none does, because the farm keeps growing) and draws whatever it is told.
 *
 * Research is the game's: harvest, spend the harvest on unlocks, and the unlocks give
 * the drone new commands and you new parts of the language. A program that uses a part
 * you have not bought yet is refused before it runs, with the line and the unlock it needs.
 */

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";

import {
  buyFarmUnlock,
  farmFile,
  fetchFarm,
  fetchFarmPlaybook,
  fetchFarmState,
  keepFarmCode,
  resetFarm,
  runFarm,
  setFarmWarp,
  stopFarm,
} from "../api";
import { award } from "../lib/momentum";
import type { FarmLine, FarmOverview, FarmState, FarmTip, FarmViolation } from "../types";
import { FarmCode } from "./farm/FarmCode";
import { FarmDocs } from "./farm/FarmDocs";
import { FarmHud } from "./farm/FarmHud";
import { FarmMenu } from "./farm/FarmMenu";
import { FarmOutput } from "./farm/FarmOutput";
import { FarmPlaybook } from "./farm/FarmPlaybook";
import { FarmScene } from "./farm/FarmScene";
import { FarmWindow } from "./farm/FarmWindow";
import { ResearchTree } from "./farm/ResearchTree";
import { droneDoing, useFarmEvents } from "./farm/farmEvents";
import { EXTENSIONS, LANGUAGE_NAMES } from "./farm/farmShared";
import { HUD_H, WINDOW_IDS, useFarmWindows, type Area, type WinId } from "./farm/useFarmWindows";
import { WINDOW_DEFS } from "./farm/windowDefs";
import "../styles/farm.css";

export default function FarmMode() {
  const [overview, setOverview] = useState<FarmOverview | null>(null);
  const [state, setState] = useState<FarmState | null>(null);
  const [language, setLanguage] = useState("python");
  /** Each language's files (name to code), and the one Run runs - the open tab. */
  const [files, setFiles] = useState<Record<string, Record<string, string>>>({});
  const [entry, setEntry] = useState<Record<string, string>>({});
  const [revision, setRevision] = useState(0);
  const [lines, setLines] = useState<FarmLine[]>([]);
  const [violations, setViolations] = useState<FarmViolation[]>([]);
  const [tips, setTips] = useState<FarmTip[]>([]);
  const [copied, setCopied] = useState("");
  // The language the tips are shown in. The game's own comes first and is where it starts:
  // the tips are about that language before they are about any other.
  const [tipLang, setTipLang] = useState<string>(() => {
    try {
      return localStorage.getItem("code-coach:playbook-language") || "original";
    } catch {
      return "original";
    }
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const sinceRef = useRef(0);
  const filesRef = useRef(files);
  filesRef.current = files;
  const saveTimer = useRef<number | null>(null);
  /** An edit waiting to be kept: which file, and its text. */
  const pending = useRef<{ language: string; file: string; code: string } | null>(null);
  const file = entry[language] ?? "main";

  /** Bumped each time the screen moves to another language's farm, so a poll for the old one is dropped. */
  const farmGen = useRef(0);
  /** The same, as state: the action log starts afresh on a new farm. */
  const [epoch, setEpoch] = useState(0);

  // The size of the screen the windows float over.
  const rootRef = useRef<HTMLDivElement | null>(null);
  const [area, setArea] = useState<Area>({ w: 0, h: 0 });
  const ready = !!overview && !!state;
  useLayoutEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    const measure = () => setArea((was) => (was.w === el.clientWidth && was.h === el.clientHeight ? was : { w: el.clientWidth, h: el.clientHeight }));
    measure();
    const watcher = new ResizeObserver(measure);
    watcher.observe(el);
    // A hidden pane may not run the observer; the window's own event still says the size changed.
    window.addEventListener("resize", measure);
    return () => {
      watcher.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [ready]);
  const wins = useFarmWindows(area);
  const { reveal } = wins;
  /** Windows that open after the screen has settled take the keyboard focus (the first ones are just there). */
  const settled = useRef(false);
  useEffect(() => {
    if (ready && area.w > 0) settled.current = true;
  }, [ready, area.w]);

  const apply = useCallback((o: FarmOverview) => {
    setOverview(o);
    setState(o);
  }, []);

  /**
   * Go to the farm in this answer - each language has its own, with its own items, research, field,
   * files and tabs. Everything on screen comes from the answer, and the output starts afresh.
   */
  const enterFarm = useCallback(
    (o: FarmOverview) => {
      farmGen.current += 1;
      setEpoch((n) => n + 1);
      apply(o);
      setLanguage(o.languages.includes(o.language) ? o.language : "python");
      setFiles(o.files);
      setEntry(o.entry);
      setLines([]);
      setViolations([]);
      setRevision((r) => r + 1);
      sinceRef.current = o.outputEnd;
    },
    [apply],
  );

  useEffect(() => {
    fetchFarm()
      .then(async (o) => {
        if (!o.languages.includes(o.language)) {
          // Saved on a language this machine can't run (no Node, say): go to Python's farm instead.
          const got = await farmFile("python", "select", o.entry.python ?? "main");
          if (got.ok) o = got;
        }
        enterFarm(o);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, [enterFarm]);

  const running = state?.run?.status === "running" || state?.run?.status === "starting";

  // Watch the farm: often while a program runs, now and then while it grows by itself.
  useEffect(() => {
    if (!overview) return;
    let alive = true;
    const tick = async () => {
      const gen = farmGen.current;
      try {
        const s = await fetchFarmState(sinceRef.current);
        if (!alive || gen !== farmGen.current) return;
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

  // What the drone just did: the counters pop, the action log fills.
  const { log, pops } = useFarmEvents(state?.farm, epoch);

  // An error or a refusal has to be seen: bring the Output window up.
  const hasProblem = !!error || violations.length > 0;
  useEffect(() => {
    if (hasProblem) reveal("output");
  }, [hasProblem, reveal]);

  /** Keep a waiting edit now, before anything that reads the files back. */
  const flush = useCallback(async () => {
    if (saveTimer.current) window.clearTimeout(saveTimer.current);
    saveTimer.current = null;
    const waiting = pending.current;
    pending.current = null;
    if (waiting) await keepFarmCode(waiting.language, waiting.code, waiting.file);
  }, []);

  const onChange = useCallback(
    (value: string) => {
      setFiles((was) => ({ ...was, [language]: { ...(was[language] ?? {}), [file]: value } }));
      pending.current = { language, file, code: value };
      if (saveTimer.current) window.clearTimeout(saveTimer.current);
      saveTimer.current = window.setTimeout(() => void flush(), 800);
    },
    [language, file, flush],
  );

  /** A file operation's answer is the whole farm: take its files and tabs. */
  const fileAnswer = useCallback(
    (o: FarmOverview & { ok: boolean; error?: string }) => {
      apply(o);
      setFiles(o.files);
      setEntry(o.entry);
      setRevision((r) => r + 1);
      setViolations([]);
      setError(o.ok ? "" : o.error ?? "");
    },
    [apply],
  );

  const pickLanguage = useCallback(
    async (next: string) => {
      if (next === language) return;
      await flush();
      try {
        // Each language has its own farm: selecting a file there takes the server to that farm,
        // and its answer is everything to show.
        const got = await farmFile(next, "select", entry[next] ?? "main");
        if (got.ok) enterFarm(got);
        else setError(got.error ?? "Could not switch farms.");
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [language, entry, flush, enterFarm],
  );

  const openFile = useCallback(
    async (name: string) => {
      if (name === file) return;
      await flush();
      setEntry((was) => ({ ...was, [language]: name }));
      setRevision((r) => r + 1);
      setViolations([]);
      void farmFile(language, "select", name);
    },
    [file, language, flush],
  );

  const addFile = useCallback(async () => {
    const name = window.prompt("Name the new file (lowercase letters, digits and _):", "utils");
    if (!name) return;
    await flush();
    fileAnswer(await farmFile(language, "add", name.trim()));
    void farmFile(language, "select", name.trim()).then((o) => o.ok && fileAnswer(o));
  }, [language, flush, fileAnswer]);

  const renameFile = useCallback(
    async (name: string) => {
      const next = window.prompt(`Rename ${name} to:`, name);
      if (!next || next.trim() === name) return;
      await flush();
      fileAnswer(await farmFile(language, "rename", name, next.trim()));
    },
    [language, flush, fileAnswer],
  );

  const deleteFile = useCallback(
    async (name: string) => {
      if (!window.confirm(`Delete ${name}${EXTENSIONS[language]}? Its code goes with it.`)) return;
      await flush();
      fileAnswer(await farmFile(language, "delete", name));
    },
    [language, flush, fileAnswer],
  );

  const run = useCallback(async () => {
    if (busy) return;
    setBusy(true);
    setError("");
    setViolations([]);
    try {
      await flush();
      const got = await runFarm(language, filesRef.current[language]?.[file] ?? "", file);
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
  }, [busy, language, file, flush]);

  const stop = useCallback(() => {
    void stopFarm();
  }, []);

  const buy = useCallback(
    async (name: string) => {
      try {
        const got = await buyFarmUnlock(name);
        if (got.ok) {
          const level = got.unlocks?.find((u) => u.name === name)?.level ?? 0;
          award("farm_buy", `${got.language}:${name}:${level}`);
        }
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
    const name = LANGUAGE_NAMES[language] ?? language;
    if (
      !window.confirm(
        `Start the ${name} farm over? Every item and every unlock in the ${name} farm goes. ` +
          "Your code stays, and so do the other languages' farms - each language has its own.",
      )
    )
      return;
    const o = await resetFarm();
    setEpoch((n) => n + 1);
    apply(o);
    setLines([]);
    sinceRef.current = o.outputEnd;
  }, [apply, language]);

  // The Playbook is fetched the first time it is opened.
  const playbookOpen = wins.layout.wins.playbook.open;
  useEffect(() => {
    if (!playbookOpen || tips.length > 0) return;
    fetchFarmPlaybook()
      .then((got) => setTips(got.entries))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, [playbookOpen, tips.length]);

  const chooseTipLang = useCallback((next: string) => {
    setTipLang(next);
    try {
      localStorage.setItem("code-coach:playbook-language", next);
    } catch {
      /* the choice just isn't remembered */
    }
  }, []);

  /**
   * Add a snippet to the end of the open file in the tips' language, a blank line after what is
   * there. If the editor is on another language it moves to this one, so what you add is what
   * Run runs.
   */
  const addSnippet = useCallback(
    async (code: string) => {
      if (running && tipLang !== language) {
        setError(`Stop the running program first: ${LANGUAGE_NAMES[tipLang] ?? tipLang} has its own farm.`);
        return;
      }
      await flush();
      const name = entry[tipLang] ?? "main";
      const now = filesRef.current[tipLang]?.[name] ?? "";
      const next = (now.trim() ? now.replace(/\s+$/, "") + "\n\n" : "") + code + "\n";
      setFiles((was) => ({ ...was, [tipLang]: { ...(was[tipLang] ?? {}), [name]: next } }));
      const kept = await keepFarmCode(tipLang, next, name);
      if (!kept.ok) {
        setError("Could not add that to your code: stop the running program and try again.");
        return;
      }
      if (tipLang !== language) {
        // Adding code in another language moves to that language's farm, so Run runs what you added.
        const got = await farmFile(tipLang, "select", name);
        if (got.ok) {
          enterFarm(got);
          return;
        }
      }
      setRevision((r) => r + 1);
      // What you added lands in the editor: show it.
      reveal("code");
    },
    [tipLang, language, entry, flush, running, enterFarm, reveal],
  );

  const copySnippet = useCallback((id: string, code: string) => {
    navigator.clipboard
      ?.writeText(code)
      .then(() => {
        setCopied(id);
        window.setTimeout(() => setCopied((c) => (c === id ? "" : c)), 1500);
      })
      .catch(() => setError("Copy was blocked here: use Add to my code instead."));
  }, []);

  if (error && !overview) return <div className="lessons-empty">Could not load the farm: {error}</div>;
  if (!overview || !state) return <div className="lessons-empty">Loading the farm…</div>;

  const multiFile = Object.keys(files[language] ?? {}).length > 1;
  const code = wins.layout.wins.code;
  const codeRect = wins.rects.code;

  // The farm is centred in what the Code window leaves (if it sits on the left) and the HUD leaves.
  const insetX =
    !wins.narrow && code.open && !code.min && codeRect.x <= area.w * 0.3
      ? Math.round(Math.min(codeRect.x + codeRect.w, area.w * 0.55))
      : 0;

  const content = (id: WinId) => {
    switch (id) {
      case "code":
        return (
          <FarmCode
            overview={overview}
            language={language}
            files={files[language] ?? {}}
            file={file}
            running={running}
            busy={busy}
            revision={revision}
            warp={state.warp}
            onWarp={(v) => void warp(v)}
            onPickLanguage={(l) => void pickLanguage(l)}
            onOpenFile={(n) => void openFile(n)}
            onAddFile={() => void addFile()}
            onRenameFile={(n) => void renameFile(n)}
            onDeleteFile={(n) => void deleteFile(n)}
            onChange={onChange}
            onRun={() => void run()}
            onStop={stop}
            onStartOver={() => void startOver()}
          />
        );
      case "output":
        return <FarmOutput lines={lines} violations={violations} error={error} run={state.run} multiFile={multiFile} />;
      case "research":
        return <ResearchTree unlocks={overview.unlocks} items={state.items} onBuy={(n) => void buy(n)} />;
      case "docs":
        return <FarmDocs overview={overview} language={language} />;
      case "playbook":
        return (
          <FarmPlaybook
            overview={overview}
            tips={tips}
            tipLang={tipLang}
            onTipLang={chooseTipLang}
            copied={copied}
            onAdd={(c) => void addSnippet(c)}
            onCopy={copySnippet}
          />
        );
    }
  };

  const top = wins.layout.order[wins.layout.order.length - 1];
  return (
    <div ref={rootRef} className="fm-root">
      <FarmScene snap={state.farm} insetX={insetX} insetY={HUD_H} sim={!!state.simulation} />
      <FarmHud
        items={state.items}
        farm={state.farm}
        language={language}
        run={state.run}
        multiFile={multiFile}
        doing={droneDoing(state.farm, running)}
        warp={state.warp}
        warps={overview.warps}
        onWarp={(v) => void warp(v)}
        pops={pops}
        log={log}
      />
      {state.simulation ? (
        <div className="fm-sim" role="status">
          Simulating <b>{state.simulation.file}</b>
          {state.simulation.speedup ? ` at ${state.simulation.speedup}×` : " as fast as it goes"} - this is
          the simulation&apos;s farm; your real farm is paused and won&apos;t change.
        </div>
      ) : null}
      {area.w > 0
        ? WINDOW_IDS.filter((id) => wins.layout.wins[id].open).map((id) => (
            <FarmWindow
              key={id}
              id={id}
              title={WINDOW_DEFS[id].title}
              icon={WINDOW_DEFS[id].icon}
              rect={wins.rects[id]}
              z={10 + wins.layout.order.indexOf(id)}
              focused={top === id}
              minimised={wins.layout.wins[id].min}
              narrow={wins.narrow}
              area={area}
              autoFocus={settled.current}
              onFocus={() => wins.focus(id)}
              onCommit={(r) => wins.commitRect(id, r)}
              onMinimise={() => wins.toggleMin(id)}
              onClose={() => wins.close(id)}
            >
              {content(id)}
            </FarmWindow>
          ))
        : null}
      <FarmMenu isOpen={(id) => wins.layout.wins[id].open} onToggle={wins.toggle} onReset={wins.reset} />
    </div>
  );
}
