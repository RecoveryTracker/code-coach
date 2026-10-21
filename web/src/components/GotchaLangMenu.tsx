/**
 * The language switch: up to four quick buttons (the languages you used last, Python first until you
 * have used others) and a "More" menu listing every language on offer with its card count. The menu
 * filters as you type, works from the keyboard (arrows, Home/End, Enter, Escape) and closes on a click
 * outside it. The choosing rules (who gets a button, how the list filters, how the arrows move) are in
 * lib/gotchas.ts, tested in node.
 */

import { useEffect, useId, useMemo, useRef, useState } from "react";

import { filterLanguages, moveActive, quickLanguages } from "../lib/gotchas";
import type { LangInfo } from "../lib/gotchas";

export default function GotchaLangMenu({
  languages,
  current,
  recent,
  onPick,
}: {
  languages: readonly LangInfo[];
  current: string;
  recent: readonly string[];
  onPick: (id: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const wrap = useRef<HTMLDivElement | null>(null);
  const input = useRef<HTMLInputElement | null>(null);
  const moreBtn = useRef<HTMLButtonElement | null>(null);
  const listId = useId();

  const quick = useMemo(() => quickLanguages(languages, recent, current), [languages, recent, current]);
  const shown = useMemo(() => filterLanguages(languages, query), [languages, query]);

  const close = (refocus: boolean) => {
    setOpen(false);
    setQuery("");
    if (refocus) moreBtn.current?.focus({ preventScroll: true });
  };

  // Opening puts the cursor in the search box, on the language you are in.
  useEffect(() => {
    if (!open) return;
    setActive(Math.max(0, filterLanguages(languages, "").findIndex((l) => l.id === current)));
    input.current?.focus({ preventScroll: true });
  }, [open, languages, current]);

  // A click outside the menu closes it.
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent | TouchEvent) => {
      if (wrap.current && !wrap.current.contains(e.target as Node)) close(false);
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("touchstart", onDown);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("touchstart", onDown);
    };
  }, [open]);

  // Keep the active row on screen inside the scrolling list.
  useEffect(() => {
    if (!open) return;
    document.getElementById(`${listId}-${active}`)?.scrollIntoView({ block: "nearest" });
  }, [open, active, listId]);

  const choose = (id: string) => {
    close(true);
    onPick(id);
  };

  const onKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      close(true);
    } else if (["ArrowDown", "ArrowUp", "Home", "End"].includes(e.key)) {
      e.preventDefault();
      setActive((a) => moveActive(a, e.key, shown.length));
    } else if (e.key === "Enter") {
      e.preventDefault();
      const pick = shown[active] ?? shown[0];
      if (pick) choose(pick.id);
    } else if (e.key === "Tab") {
      close(false);
    }
  };

  return (
    <div className="gq-lang-wrap" ref={wrap}>
      <div className="gq-lang" role="group" aria-label="Language">
        {quick.map((l) => (
          <button
            key={l.id}
            type="button"
            className={`gq-lang-btn${l.id === current ? " on" : ""}`}
            aria-pressed={l.id === current}
            onClick={() => {
              if (open) close(false);
              onPick(l.id);
            }}
          >
            {l.name}
          </button>
        ))}
        {languages.length > 1 ? (
          <button
            type="button"
            ref={moreBtn}
            className={`gq-lang-btn gq-more${open ? " on" : ""}`}
            aria-haspopup="listbox"
            aria-expanded={open}
            aria-controls={open ? listId : undefined}
            onClick={() => (open ? close(false) : setOpen(true))}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown" && !open) {
                e.preventDefault();
                setOpen(true);
              }
            }}
          >
            More <span aria-hidden="true">{"▾"}</span>
          </button>
        ) : null}
      </div>

      {open ? (
        <div className="gq-menu" role="dialog" aria-label="All languages">
          <input
            ref={input}
            type="text"
            className="gq-menu-search"
            placeholder="Find a language..."
            aria-label="Find a language"
            role="combobox"
            aria-expanded="true"
            aria-controls={listId}
            aria-activedescendant={shown.length > 0 ? `${listId}-${active}` : undefined}
            aria-autocomplete="list"
            autoComplete="off"
            spellCheck={false}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
            onKeyDown={onKey}
          />
          <ul className="gq-menu-list" id={listId} role="listbox" aria-label="Languages">
            {shown.map((l, i) => (
              <li
                key={l.id}
                id={`${listId}-${i}`}
                role="option"
                aria-selected={l.id === current}
                data-lang={l.id}
                className={`gq-menu-item${i === active ? " active" : ""}${l.id === current ? " current" : ""}`}
                onMouseEnter={() => setActive(i)}
                onMouseDown={(e) => {
                  e.preventDefault(); // keep the focus in the search box
                  choose(l.id);
                }}
              >
                <span className="gq-menu-name">{l.name}</span>
                <span className="gq-menu-count">{l.count} cards</span>
              </li>
            ))}
            {shown.length === 0 ? <li className="gq-menu-empty">No language matches {"“"}{query}{"”"}</li> : null}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
