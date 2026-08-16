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

  const active = langs.find((l) => l.id === current);

  async function choose(lang: LanguageInfo) {
    if (!lang.available || lang.id === current || busy) return;
    setBusy(true);
    setError(null);
    try {
      await updateProgress({ language: lang.id });
      onChanged(lang.id);
      setOpen(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't switch language.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="lang-wrap" ref={wrap}>
      <button
        type="button"
        className={`ws-btn${open ? " primary" : ""}`}
        onClick={() => setOpen((o) => !o)}
        title="Which language the drills are written in"
      >
        {active?.name ?? current}
      </button>

      {open ? (
        <div className="lang-menu" role="menu">
          <div className="lang-menu-title">Language</div>
          {langs.map((lang) => (
            <button
              key={lang.id}
              type="button"
              role="menuitemradio"
              aria-checked={lang.id === current}
              className={`lang-item${lang.id === current ? " on" : ""}${
                lang.available ? "" : " off"
              }`}
              disabled={!lang.available || busy}
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
