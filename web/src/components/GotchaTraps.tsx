/**
 * My traps: the cards you have missed and not yet mastered, to study without waiting for the feed to
 * deal them again.
 *
 * "Missed and not yet mastered" is one written-down rule, kept by the server (`GotchaStore.traps`): you
 * answered the card wrong at least once, and your last two answers have not both been right and marked Sure.
 * Only cards you have already answered are here, so showing the code, the trap and the why spoils nothing.
 * Each one has a "Try again" that serves that card in the feed like any other (answer hidden, a normal
 * answer). The list is for the current language by default, or every language. Escape or "Back to the quiz"
 * returns to the feed. The ordering and wording rules are pure functions in lib/gotchas.ts, tested in node.
 */

import { useEffect, useRef, useState } from "react";

import { fetchGotchaTraps } from "../api";
import type { Syntax } from "../lib/codeColors";
import {
  TRAPS_EMPTY,
  accentStyle,
  errorText,
  isTypingTarget,
  missedLine,
  sortTraps,
  trapBadges,
  trapsScope,
} from "../lib/gotchas";
import type { GotchaLang, GotchaTrap, LangInfo } from "../lib/gotchas";
import { CodeBlock } from "./GotchaCode";

export default function GotchaTraps({
  language,
  languages,
  syntax,
  onClose,
  onTry,
}: {
  language: GotchaLang;
  languages: readonly LangInfo[];
  syntax: Record<string, Syntax>;
  onClose: () => void;
  onTry: (trap: GotchaTrap) => void;
}) {
  const [all, setAll] = useState(false);
  const [traps, setTraps] = useState<GotchaTrap[] | null>(null);
  const [error, setError] = useState("");
  const panel = useRef<HTMLElement | null>(null);
  const request = useRef(0);
  const currentName = languages.find((l) => l.id === language)?.name ?? language;

  useEffect(() => {
    const mine = ++request.current;
    setTraps(null);
    setError("");
    fetchGotchaTraps(trapsScope(all, language))
      .then((r) => mine === request.current && setTraps(sortTraps(r.traps)))
      .catch((e) => mine === request.current && setError(errorText(e)));
    return () => {
      request.current++;
    };
  }, [all, language]);

  // The cursor starts on the panel, so Escape works at once.
  useEffect(() => {
    panel.current?.focus({ preventScroll: true });
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape" || e.defaultPrevented) return;
      const el = e.target as HTMLElement | null;
      if (isTypingTarget(el?.tagName ?? "", !!el?.isContentEditable)) return;
      e.preventDefault();
      onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <section className="gq-traps" aria-label="My traps" ref={panel} tabIndex={-1} data-testid="gq-traps">
      <header className="gq-traps-head">
        <div>
          <h3>My traps</h3>
          <p className="gq-sub">
            Cards you missed and have not mastered yet. A card is mastered when your last two answers were right and
            marked Sure.
          </p>
        </div>
        <button type="button" className="ws-btn" onClick={onClose} data-testid="gq-traps-close">
          Back to the quiz
        </button>
      </header>

      <div className="gq-traps-filter" role="group" aria-label="Which language">
        <button type="button" className={`gq-pill${all ? "" : " on"}`} aria-pressed={!all} onClick={() => setAll(false)}>
          {currentName}
        </button>
        <button
          type="button"
          className={`gq-pill${all ? " on" : ""}`}
          aria-pressed={all}
          data-testid="gq-traps-all"
          onClick={() => setAll(true)}
        >
          All languages
        </button>
      </div>

      {error ? (
        <p className="gq-run-note" role="alert">
          {error}
        </p>
      ) : traps === null ? (
        <p className="gq-run-note" aria-busy="true">
          Looking through your cards...
        </p>
      ) : traps.length === 0 ? (
        <p className="gq-traps-empty" data-testid="gq-traps-empty">
          {TRAPS_EMPTY}
        </p>
      ) : (
        <ol className="gq-traps-list" data-testid="gq-traps-list">
          {traps.map((t) => (
            <li
              key={`${t.language}:${t.id}`}
              className="gq-trap-item"
              style={accentStyle(t.language)}
              data-testid="gq-trap-item"
              data-card-id={t.id}
            >
              <div className="gq-trap-top">
                <h4 className="gq-trap-where">
                  {t.language_name} <span aria-hidden="true">{"·"}</span> {t.title}
                </h4>
                <span className="gq-badges">
                  {t.mine ? <span className="gq-badge mine">Yours</span> : null}
                  {trapBadges(t).map((b) => (
                    <span key={b} className={`gq-badge ${b === "Shaky" ? "shaky" : "sure"}`}>
                      {b}
                    </span>
                  ))}
                </span>
              </div>
              <CodeBlock code={t.code} label={`${t.language_name} ${t.title}`} syntax={syntax[t.language]} compact />
              <p className="gq-trap">
                <span className="gq-trap-label">Trap</span> {t.trap}
              </p>
              {t.why ? (
                <p className="gq-why-text">
                  <strong className="gq-why-label">Why</strong> {t.why}
                </p>
              ) : null}
              {t.note ? (
                <p className="gq-thought">
                  <span className="gq-thought-label">What you thought:</span> {t.note}
                </p>
              ) : null}
              <div className="gq-trap-foot">
                <span className="gq-trap-meta">
                  {missedLine(t.misses)}
                  {t.last_day ? ` · last seen ${t.last_day}` : ""}
                </span>
                <button type="button" className="ws-btn primary" onClick={() => onTry(t)} data-testid="gq-trap-try">
                  Try again
                </button>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
