/** The Playbook window: tips and snippets, in the language you pick, to add to your code. */

import { useState } from "react";

import type { FarmOverview, FarmTip } from "../../types";
import { LANGUAGE_NAMES } from "./farmShared";

type Props = {
  overview: FarmOverview;
  tips: FarmTip[];
  tipLang: string;
  onTipLang: (lang: string) => void;
  copied: string;
  onAdd: (code: string) => void;
  onCopy: (id: string, code: string) => void;
};

export function FarmPlaybook({ overview, tips, tipLang, onTipLang, copied, onAdd, onCopy }: Props) {
  // The Playbook's own controls: a search, "ready to run" only, and which groups are shut.
  const [tipSearch, setTipSearch] = useState("");
  const [readyOnly, setReadyOnly] = useState(false);
  const [shut, setShut] = useState<Record<string, boolean>>({});

  const needle = tipSearch.trim().toLowerCase();
  // The tips are for tipLang, whose farm is not always the one you are on.
  const levelOf = (n: string) => overview.levels?.[tipLang]?.[n] ?? 0;
  const missingFor = (t: FarmTip) => t.needs.filter((n) => levelOf(n) < (t.levels[n] ?? 1));
  const shown = tips.filter(
    (t) =>
      (!needle || `${t.title} ${t.tip} ${t.group}`.toLowerCase().includes(needle)) &&
      (!readyOnly || missingFor(t).length === 0),
  );
  const groups = [...new Set(shown.map((t) => t.group))];

  return (
    <div className="fm-scroll fm-playbook">
      <div className="fm-langs fm-tip-langs" role="tablist" aria-label="Tip language">
        {(overview.languages ?? ["original", "python", "javascript", "dart"]).map((l) => (
          <button
            key={l}
            type="button"
            role="tab"
            aria-selected={tipLang === l}
            className={`fm-btn tab${tipLang === l ? " on" : ""}`}
            onClick={() => onTipLang(l)}
          >
            {LANGUAGE_NAMES[l] ?? l}
          </button>
        ))}
      </div>
      <p className="fm-needs">
        {tipLang === "original"
          ? "Written in the game's own language: this is what the tips look like in the game itself. "
          : "Same tips in " + (LANGUAGE_NAMES[tipLang] ?? tipLang) + ". "}
        Add one to your code, then press Run.
      </p>
      <div className="fm-tip-controls">
        <input
          type="search"
          className="fm-tip-search"
          placeholder="Search the tips (pumpkin, maze, drone…)"
          value={tipSearch}
          onChange={(e) => setTipSearch(e.target.value)}
          aria-label="Search the playbook"
        />
        <label className="fm-tip-ready">
          <input type="checkbox" checked={readyOnly} onChange={(e) => setReadyOnly(e.target.checked)} />
          Ready to run
        </label>
      </div>
      {tips.length === 0 ? <p className="fm-needs">Loading…</p> : null}
      {tips.length > 0 && shown.length === 0 ? (
        <p className="fm-needs">Nothing matches{readyOnly ? " yet - try without Ready to run" : ""}.</p>
      ) : null}
      {groups.map((group) => {
        const inGroup = shown.filter((t) => t.group === group);
        // A search opens everything it found; otherwise a group is open unless shut.
        const open = needle ? true : !shut[group];
        return (
          <div key={group}>
            <button
              type="button"
              className="fm-group"
              aria-expanded={open}
              onClick={() => setShut((was) => ({ ...was, [group]: open }))}
            >
              <span>{open ? "▾" : "▸"}</span> {group} <span className="fm-group-count">{inGroup.length}</span>
            </button>
            {open
              ? inGroup.map((t) => {
                  const code = t.snippets[tipLang] ?? "";
                  const missing = missingFor(t);
                  return (
                    <div key={t.id} className={`fm-tip${missing.length ? " locked" : ""}`}>
                      <strong>{t.title}</strong>
                      <p>{t.tip}</p>
                      {missing.length ? (
                        <p className="fm-needs">
                          Needs{" "}
                          {missing
                            .map((n) => n.replace(/_/g, " ") + ((t.levels[n] ?? 1) > 1 ? ` level ${t.levels[n]}` : ""))
                            .join(" and ")}
                          .
                        </p>
                      ) : null}
                      {code ? <pre className="fm-snippet">{code}</pre> : null}
                      {code ? (
                        <div className="fm-tip-actions">
                          <button type="button" className="fm-btn" onClick={() => onAdd(code)}>
                            Add to my code
                          </button>
                          <button type="button" className="fm-btn" onClick={() => onCopy(t.id, code)}>
                            {copied === t.id ? "Copied" : "Copy"}
                          </button>
                        </div>
                      ) : null}
                    </div>
                  );
                })
              : null}
          </div>
        );
      })}
    </div>
  );
}
