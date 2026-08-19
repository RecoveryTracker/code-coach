import { useEffect, useRef, useState } from "react";
import { fetchLanguages, updateProgress } from "../api";
import type { LanguageInfo } from "../types";

type Props = {
  current: string;
  onChanged: (languageId: string) => void;
};

/**
 * Language menu. Only Python works today — the rest are listed but not
 * selectable, with the reason shown, so the roadmap is visible instead of
 * being a mystery menu that silently does nothing.
 */
export function LanguagePicker({ current, onChanged }: Props) {
  const [langs, setLangs] = useState<LanguageInfo[]>([]);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wrap = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const list = await fetchLanguages();
        if (!cancelled) setLangs(list);
      } catch {
        /* menu simply won't open */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Click outside / Escape closes it.
  useEffect(() => {
    if (!open) return;
    const onDown = (e: PointerEvent) => {
      if (!wrap.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("pointerdown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("pointerdown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // What the button says right now. Set on click so the label changes on the
  // same frame, rather than after the round trips have finished — the work
  // takes ~40ms but waiting to acknowledge the click made it feel stalled.
  const [pending, setPending] = useState<string | null>(null);
  useEffect(() => {
    setPending(null);
  }, [current]);

  const shownId = pending ?? current;
  const active = langs.find((l) => l.id === shownId);

  async function choose(lang: LanguageInfo) {
    if (!lang.available || lang.id === current || busy) return;
    // Acknowledge immediately: close the menu and show the new name.
    setOpen(false);
    setPending(lang.id);
    setBusy(true);
    setError(null);
    try {
      await updateProgress({ language: lang.id });
      onChanged(lang.id);
    } catch (e) {
      setPending(null);
      setOpen(true);
      setError(e instanceof Error ? e.message : "Couldn't switch language.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="lang-wrap" ref={wrap}>
      <button
        type="button"
        className={`ws-btn${open ? " primary" : ""}${busy ? " working" : ""}`}
        onClick={() => setOpen((o) => !o)}
        title="Which language the drills are written in"
      >
        {active?.name ?? shownId}
      </button>

      {open ? (
        <div className="lang-menu" role="menu">
          <div className="lang-menu-title">Language</div>
          {langs.map((lang) => (
            <button
              key={lang.id}
              type="button"
              role="menuitemradio"
              // Menu is already closing; don't grey every row on the way out.
              aria-checked={lang.id === shownId}
              className={`lang-item${lang.id === shownId ? " on" : ""}${
                lang.available ? "" : " off"
              }`}
              disabled={!lang.available}
              onClick={() => void choose(lang)}
              title={lang.available ? "" : lang.note}
            >
              <span className="lang-item-head">
                <span className="lang-item-name">{lang.name}</span>
                {lang.id === current ? (
                  <span className="lang-item-tick" aria-hidden>
                    ✓
                  </span>
                ) : lang.available ? null : (
                  <span className="lang-item-soon">not yet</span>
                )}
              </span>
              {!lang.available ? (
                <span className="lang-item-note">{lang.note}</span>
              ) : null}
            </button>
          ))}
          {error ? <p className="lang-error">{error}</p> : null}
        </div>
      ) : null}
    </div>
  );
}
