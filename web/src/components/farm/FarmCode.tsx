/** The Code window: language tabs, Run / Stop / Start over / time warp, the file tabs and the editor. */

import type { FarmOverview } from "../../types";
import { EditorPane } from "../EditorPane";
import { PlayIcon, StopIcon } from "./FarmIcons";
import { EXTENSIONS, LANGUAGE_NAMES, LANGUAGE_TIPS } from "./farmShared";

type Props = {
  overview: FarmOverview;
  language: string;
  files: Record<string, string>;
  file: string;
  running: boolean;
  busy: boolean;
  revision: number;
  warp: number;
  onWarp: (value: number) => void;
  onPickLanguage: (lang: string) => void;
  onOpenFile: (name: string) => void;
  onAddFile: () => void;
  onRenameFile: (name: string) => void;
  onDeleteFile: (name: string) => void;
  onChange: (value: string) => void;
  onRun: () => void;
  onStop: () => void;
  onStartOver: () => void;
};

export function FarmCode(p: Props) {
  const { overview, language, files, file, running } = p;
  const names = Object.keys(files);
  return (
    <div className="fm-code">
      <div className="fm-toolbar">
        <div className="fm-langs" role="tablist" aria-label="Language" title="Each language has its own farm">
          {overview.languages.map((lang) => {
            const save = overview.saves?.[lang];
            return (
              <button
                key={lang}
                type="button"
                role="tab"
                aria-selected={lang === language}
                className={`fm-btn tab${lang === language ? " on" : ""}`}
                onClick={() => p.onPickLanguage(lang)}
                title={`${LANGUAGE_TIPS[lang]}. Its own farm${save ? `: ${save.w}×${save.h}` : ""}`}
                disabled={running}
              >
                {LANGUAGE_NAMES[lang] ?? lang}
                {save ? <small>{save.w}×{save.h}</small> : null}
              </button>
            );
          })}
        </div>
        <div className="fm-actions">
          {running ? (
            <button type="button" className="fm-btn stop" onClick={p.onStop}>
              <StopIcon /> Stop
            </button>
          ) : (
            <button
              type="button"
              className="fm-btn primary"
              onClick={p.onRun}
              disabled={p.busy}
              title="Run (Ctrl+Enter)"
            >
              <PlayIcon /> {p.busy ? "Starting…" : `Run ${file}`}
            </button>
          )}
          <label className="fm-warp" title="Time warp: how many game seconds pass per real second">
            Warp
            <select value={p.warp} onChange={(e) => p.onWarp(Number(e.target.value))}>
              {overview.warps.map((w) => (
                <option key={w} value={w}>
                  {w === 0 ? "max" : `${w}×`}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="fm-btn danger"
            onClick={p.onStartOver}
            title={`Start the ${LANGUAGE_NAMES[language] ?? language} farm over (your code stays)`}
          >
            Start over
          </button>
        </div>
      </div>
      {/* The program's files, like the game's code windows. The open tab is
          the one Run runs; the others are there to be imported. */}
      <div className="fm-files" role="tablist" aria-label="Files">
        {names.map((name) => (
          <span key={name} className={`fm-file${name === file ? " on" : ""}`}>
            <button
              type="button"
              role="tab"
              aria-selected={name === file}
              onClick={() => p.onOpenFile(name)}
              onDoubleClick={() => p.onRenameFile(name)}
              disabled={running}
              title="Double-click to rename"
            >
              {name}
              {EXTENSIONS[language]}
            </button>
            {names.length > 1 ? (
              <button
                type="button"
                className="fm-file-x"
                onClick={() => p.onDeleteFile(name)}
                disabled={running}
                aria-label={`Delete ${name}`}
                title={`Delete ${name}`}
              >
                ×
              </button>
            ) : null}
          </span>
        ))}
        <button
          type="button"
          className="fm-file-add"
          onClick={p.onAddFile}
          disabled={running}
          aria-label="Add a file"
          title="Add a file - with Import researched, your files can import each other"
        >
          +
        </button>
      </div>
      {/* The editor gets a definite box: absolutely filled, so Monaco's 100% height has something to be 100% of. */}
      <div className="fm-editor">
        <EditorPane
          code={files[file] ?? ""}
          revision={p.revision}
          onChange={p.onChange}
          onRun={p.onRun}
          language={language === "original" ? "python" : language}
          fileName={`${file}${EXTENSIONS[language]}`}
        />
      </div>
    </div>
  );
}
