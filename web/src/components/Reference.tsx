import { useEffect, useMemo, useState } from "react";

import { fetchReference } from "../api";
import type { ReferenceSheet } from "../types";

type Card = { code: string; note: string; section: string };

/**
 * Reference: the desk mat, and flashcards over the same entries.
 *
 * The sheet is for scanning — dense columns, most-used first, the way you
 * would glance at a printed card beside the keyboard. The cards are for
 * finding out whether you actually know it, which reading never tells you.
 *
 * Both read the same entries, so adding a line to the sheet adds a card too.
 */
type Props = {
  /** Which language's sheet to show. Changing it refetches. */
  language: string;
};

export default function Reference({ language }: Props) {
  const [sheet, setSheet] = useState<ReferenceSheet | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"sheet" | "cards">("sheet");

  // Keyed on the language because the picker now lives on this screen: the
  // panel is no longer remounted on the way in, so nothing else would notice
  // the switch.
  useEffect(() => {
    let cancelled = false;
    setSheet(null);
    setError(null);
    (async () => {
      try {
        const data = await fetchReference(language);
        if (!cancelled) setSheet(data);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "API error");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [language]);

  if (error) {
    return <div className="ref-empty">Couldn't load the reference: {error}</div>;
  }
  if (!sheet) return <div className="ref-empty">Loading…</div>;
  if (!sheet.has_sheet) {
    return (
      <div className="ref-empty">
        No cheat sheet for {sheet.language} yet. Switch language, or ask for one.
      </div>
    );
  }

  return (
    <div className="ref">
      <div className="ref-modes">
        <button
          type="button"
          className={`ref-mode${mode === "sheet" ? " on" : ""}`}
          onClick={() => setMode("sheet")}
        >
          Cheat sheet
        </button>
        <button
          type="button"
          className={`ref-mode${mode === "cards" ? " on" : ""}`}
          onClick={() => setMode("cards")}
        >
          Flashcards
        </button>
      </div>

      {mode === "sheet" ? <SheetView sheet={sheet} /> : <Cards sheet={sheet} />}
    </div>
  );
}

/** The mat. Columns that flow, so a wide window shows more at once. */
function SheetView({ sheet }: { sheet: ReferenceSheet }) {
  return (
    <div className="ref-sheet">
      {sheet.sections.map((section) => (
        <section className="ref-card" key={section.name}>
          <h3>{section.name}</h3>
          <p className="ref-card-blurb">{section.blurb}</p>
          <dl>
            {section.entries.map((entry, i) => (
              <div className="ref-row" key={i}>
                <dt>
                  <code>{entry.code}</code>
                </dt>
                {entry.note ? <dd>{entry.note}</dd> : null}
              </div>
            ))}
          </dl>
        </section>
      ))}
    </div>
  );
}

/**
 * Flashcards over the same entries.
 *
 * The note is the prompt and the code is the answer, because that is the
 * direction you need it in: you know what you are trying to do and you are
 * reaching for how to say it. Self-graded, and the ones you miss come back —
 * a card you got right leaves the deck, a card you missed goes to the back.
 */
function Cards({ sheet }: { sheet: ReferenceSheet }) {
  const all = useMemo<Card[]>(() => {
    const out: Card[] = [];
    // The first section repeats a few lines from the sections below it, which
    // is right on a card and wrong in a deck — you would be asked the same
    // thing twice. First one in wins.
    const already = new Set<string>();
    for (const section of sheet.sections) {
      for (const entry of section.entries) {
        // A card needs a prompt. Entries without a note are reference-only.
        if (!entry.note || already.has(entry.code)) continue;
        already.add(entry.code);
        out.push({ code: entry.code, note: entry.note, section: section.name });
      }
    }
    return out;
  }, [sheet]);

  const [deck, setDeck] = useState<Card[]>([]);
  const [shown, setShown] = useState(false);
  const [right, setRight] = useState(0);
  const [wrong, setWrong] = useState(0);
  const [section, setSection] = useState("all");

  const shuffle = useMemo(
    () => (cards: Card[]) => {
      const out = [...cards];
      for (let i = out.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [out[i], out[j]] = [out[j], out[i]];
      }
      return out;
    },
    [],
  );

  useEffect(() => {
    const pool =
      section === "all" ? all : all.filter((c) => c.section === section);
    setDeck(shuffle(pool));
    setShown(false);
    setRight(0);
    setWrong(0);
  }, [all, section, shuffle]);

  const card = deck[0] ?? null;

  const answer = (knew: boolean) => {
    setShown(false);
    if (knew) {
      setRight((n) => n + 1);
      setDeck((d) => d.slice(1));
    } else {
      setWrong((n) => n + 1);
      // To the back rather than out of the deck: a card you missed is the
      // one worth seeing again this session.
      setDeck((d) => (d.length > 1 ? [...d.slice(1), d[0]] : d));
    }
  };

  return (
    <div className="ref-cards">
      <div className="ref-cards-bar">
        <select value={section} onChange={(e) => setSection(e.target.value)}>
          <option value="all">Everything</option>
          {sheet.sections.map((s) => (
            <option key={s.name} value={s.name}>
              {s.name}
            </option>
          ))}
        </select>
        <span className="ref-score">
          {right} known · {wrong} missed · {deck.length} left
        </span>
      </div>

      {card ? (
        <div className="ref-card-face">
          <span className="ref-card-section">{card.section}</span>
          <p className="ref-prompt">{card.note}</p>

          {shown ? (
            <>
              <pre className="ref-answer">{card.code}</pre>
              <div className="ref-card-actions">
                <button type="button" onClick={() => answer(false)}>
                  Missed it
                </button>
                <button
                  type="button"
                  className="primary"
                  onClick={() => answer(true)}
                >
                  Knew it
                </button>
              </div>
            </>
          ) : (
            <button
              type="button"
              className="ref-show"
              onClick={() => setShown(true)}
            >
              Show the line
            </button>
          )}
        </div>
      ) : (
        <div className="ref-done">
          <p>
            Deck finished — {right} known, {wrong} missed along the way.
          </p>
          <button
            type="button"
            className="primary"
            onClick={() => {
              const pool =
                section === "all"
                  ? all
                  : all.filter((c) => c.section === section);
              setDeck(shuffle(pool));
              setRight(0);
              setWrong(0);
            }}
          >
            Go again
          </button>
        </div>
      )}
    </div>
  );
}
