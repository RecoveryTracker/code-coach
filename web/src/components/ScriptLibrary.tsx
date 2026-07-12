import { useEffect, useState } from "react";
import {
  deleteScript,
  downloadScript,
  listScripts,
  loadScript,
  saveScript,
  type SavedScript,
} from "../lib/scripts";

type Props = {
  getCode: () => string;
  setCode: (code: string) => void;
  source: "free" | "lesson";
};

/**
 * Save / load / download editor scripts (Free mode and coach mode).
 */
export function ScriptLibrary({ getCode, setCode, source }: Props) {
  const [open, setOpen] = useState(false);
  const [scripts, setScripts] = useState<SavedScript[]>([]);
  const [msg, setMsg] = useState<string | null>(null);

  function refresh() {
    setScripts(listScripts());
  }

  useEffect(() => {
    if (open) refresh();
  }, [open]);

  function flash(text: string) {
    setMsg(text);
    window.setTimeout(() => setMsg(null), 2200);
  }

  function onSave() {
    const code = getCode();
    const defaultName =
      source === "free"
        ? `idea-${new Date().toISOString().slice(0, 16).replace("T", "-")}`
        : `lesson-${new Date().toISOString().slice(0, 10)}`;
    const name = window.prompt("Name this script:", defaultName);
    if (name === null) return;
    const entry = saveScript(name, code, source);
    refresh();
    flash(`Saved “${entry.name}”`);
  }

  function onLoad(id: string) {
    const s = loadScript(id);
    if (!s) return;
    if (
      getCode().trim() &&
      !window.confirm(`Replace editor with “${s.name}”?`)
    ) {
      return;
    }
    setCode(s.code);
    setOpen(false);
    flash(`Loaded “${s.name}”`);
  }

  function onDownload(s: SavedScript) {
    downloadScript(s.name, s.code);
  }

  function onDelete(id: string, name: string) {
    if (!window.confirm(`Delete “${name}”?`)) return;
    deleteScript(id);
    refresh();
  }

  return (
    <div className="script-lib">
      <button type="button" className="ws-btn" onClick={onSave}>
        Save
      </button>
      <button
        type="button"
        className="ws-btn"
        onClick={() => setOpen((o) => !o)}
      >
        {open ? "Close library" : "Load…"}
      </button>
      {msg ? <span className="script-lib-msg">{msg}</span> : null}
      {open ? (
        <div className="script-lib-panel">
          <div className="script-lib-head">Saved scripts</div>
          {scripts.length === 0 ? (
            <p className="script-lib-empty">
              No saves yet. Click Save to store the editor.
            </p>
          ) : (
            <ul className="script-lib-list">
              {scripts.map((s) => (
                <li key={s.id}>
                  <div className="script-lib-meta">
                    <strong>{s.name}</strong>
                    <span>
                      {new Date(s.updatedAt).toLocaleString()} · {s.source}
                    </span>
                  </div>
                  <div className="script-lib-actions">
                    <button type="button" onClick={() => onLoad(s.id)}>
                      Load
                    </button>
                    <button type="button" onClick={() => onDownload(s)}>
                      .py
                    </button>
                    <button
                      type="button"
                      className="danger"
                      onClick={() => onDelete(s.id, s.name)}
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : null}
    </div>
  );
}
