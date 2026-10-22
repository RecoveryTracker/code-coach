/**
 * "Words used": the vocabulary under an Explain result, so the words are learned
 * where they are met. One card per word: the term, a plain definition, its rules,
 * a verified example with what it prints, and "See also" chips. Shared by every
 * place an explanation shows (the coach strip, Free mode, Brain Drills, the
 * Workbook and Katas walkthroughs); the rules for which card is open live in the
 * pure lib/words.ts. The words come from the server (code_coach/glossary).
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { fetchGlossary } from "../api";
import {
  cardDomId,
  columnsOf,
  initialOpen,
  revealOpen,
  seeAlsoAction,
  toggleOpen,
  withExtras,
} from "../lib/words";
import type { Word, WordRef } from "../types";
import "../styles/words.css";

type Cards = {
  shown: Word[];
  open: string[];
  toggle: (id: string) => void;
  seeAlso: (from: Word, ref: WordRef) => void;
  busy: string;
  failed: string;
};

/** The open cards and the words fetched through "see also" chips, for one list on screen. */
function useCards(words: Word[], scope: string, initial: "first" | "none"): Cards {
  const signature = words.map((w) => w.id).join("|");
  const [open, setOpen] = useState<string[]>(() => (initial === "first" ? initialOpen(words) : []));
  const [extras, setExtras] = useState<Word[]>([]);
  const [busy, setBusy] = useState("");
  const [failed, setFailed] = useState("");
  const alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);
  // A new explanation is a new list: start again.
  useEffect(() => {
    setOpen(initial === "first" ? initialOpen(words) : []);
    setExtras([]);
    setFailed("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature, initial]);

  const shown = withExtras(words, extras);

  const focusCard = useCallback(
    (id: string) => {
      window.setTimeout(() => {
        const card = document.getElementById(cardDomId(scope, id));
        card?.scrollIntoView({ block: "nearest" });
        card?.querySelector<HTMLElement>("button")?.focus();
      }, 0);
    },
    [scope],
  );

  const toggle = useCallback((id: string) => setOpen((o) => toggleOpen(o, id)), []);

  const seeAlso = useCallback(
    (from: Word, ref: WordRef) => {
      setFailed("");
      if (seeAlsoAction(shown, ref.id) === "show") {
        setOpen((o) => revealOpen(o, ref.id));
        focusCard(ref.id);
        return;
      }
      setBusy(ref.id);
      fetchGlossary({ language: from.language, term: ref.id })
        .then((found) => {
          if (!alive.current) return;
          if (found.length === 0) {
            setFailed(ref.term);
            return;
          }
          setExtras((e) => withExtras(e, found));
          setOpen((o) => revealOpen(o, found[0].id));
          focusCard(found[0].id);
        })
        .catch(() => alive.current && setFailed(ref.term))
        .finally(() => alive.current && setBusy(""));
    },
    [shown, focusCard],
  );

  return { shown, open, toggle, seeAlso, busy, failed };
}

function hasDetails(w: Word): boolean {
  return w.rules.length > 0 || !!w.example || w.see_also.length > 0 || columnsOf(w).length > 0;
}

function WordCard({
  word,
  scope,
  open,
  onToggle,
  cards,
}: {
  word: Word;
  scope: string;
  open: boolean;
  onToggle: () => void;
  cards: Cards;
}) {
  const domId = cardDomId(scope, word.id);
  const bodyId = `${domId}-body`;
  const details = hasDetails(word);
  const columns = columnsOf(word);
  const multiline = word.example_output.includes("\n");
  return (
    <li className="word-card" id={domId} data-word={word.id}>
      <h4 className="word-term">
        {details ? (
          <button type="button" className="word-toggle" aria-expanded={open} aria-controls={bodyId} onClick={onToggle}>
            <span className="word-chevron" aria-hidden="true">
              {open ? "▾" : "▸"}
            </span>
            <span>{word.term}</span>
          </button>
        ) : (
          <span className="word-toggle word-toggle-plain">{word.term}</span>
        )}
      </h4>
      <p className="word-def">{word.definition}</p>
      {details && open ? (
        <div className="word-body" id={bodyId}>
          {columns.length > 0 ? (
            <div className="word-columns">
              {columns.map((c) => (
                <div key={c.tone} className={`word-col word-col-${c.tone}`}>
                  <h5 className="word-col-title">{c.title}</h5>
                  <ul className="word-col-items">
                    {c.items.map((item) => (
                      <li key={item}>
                        <code>{item}</code>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ) : null}
          {word.rules.length > 0 ? (
            <ul className="word-rules" aria-label={`Rules for ${word.term}`}>
              {word.rules.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          ) : null}
          {word.example ? (
            <div className="word-example">
              <div className="word-label">Example</div>
              <pre className="word-code">
                <code>{word.example}</code>
              </pre>
              <div className="word-prints">
                <span className="word-label">prints:</span>{" "}
                {multiline ? (
                  <pre className="word-code word-out">
                    <code>{word.example_output}</code>
                  </pre>
                ) : (
                  <code className="word-out-inline">{word.example_output}</code>
                )}
              </div>
            </div>
          ) : null}
          {word.see_also.length > 0 ? (
            <div className="word-also">
              <span className="word-label" id={`${bodyId}-also`}>
                See also
              </span>
              <ul className="word-chips" aria-labelledby={`${bodyId}-also`}>
                {word.see_also.map((ref) => (
                  <li key={ref.id}>
                    <button
                      type="button"
                      className="word-chip"
                      onClick={() => cards.seeAlso(word, ref)}
                      disabled={cards.busy === ref.id}
                    >
                      {ref.term}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </li>
  );
}

type Props = {
  words: Word[] | undefined | null;
  /** Heading text; "Words used" unless a screen has a better name. */
  heading?: string;
  /** Names this list's cards in the page, so two lists on one screen never share an element id. */
  scope?: string;
};

export function WordsUsed({ words, heading = "Words used", scope = "used" }: Props) {
  const list = words ?? [];
  const cards = useCards(list, scope, "first");
  if (list.length === 0) return null;
  return (
    <section className="words-used" aria-label={heading} data-testid="words-used">
      <h3 className="words-title">{heading}</h3>
      <ul className="words-list">
        {cards.shown.map((w) => (
          <WordCard
            key={w.id}
            word={w}
            scope={scope}
            open={cards.open.includes(w.id)}
            onToggle={() => cards.toggle(w.id)}
            cards={cards}
          />
        ))}
      </ul>
      {cards.failed ? <p className="words-note">Couldn’t look up “{cards.failed}” just now.</p> : null}
    </section>
  );
}

/**
 * Brain Drills, on a missed question: a quiet line of chips naming the words the question is about.
 * A chip opens that word's card right there, so the vocabulary is learned without pressing Explain.
 */
export function QuestionWords({
  activityId,
  language,
  scope = "question",
}: {
  activityId: string;
  language: string;
  scope?: string;
}) {
  const [words, setWords] = useState<Word[] | null>(null);
  useEffect(() => {
    let live = true;
    setWords(null);
    fetchGlossary({ language, context: activityId })
      .then((found) => live && setWords(found))
      .catch(() => live && setWords([]));
    return () => {
      live = false;
    };
  }, [activityId, language]);
  const cards = useCards(words ?? [], scope, "none");
  if (!words || words.length === 0) return null;
  const picked = cards.shown.filter((w) => cards.open.includes(w.id));
  return (
    <div className="words-question" data-testid="question-words">
      <div className="words-question-line">
        <span className="words-question-label" id={`${scope}-label`}>
          Words in this question:
        </span>
        <ul className="word-chips" aria-labelledby={`${scope}-label`}>
          {words.map((w) => (
            <li key={w.id}>
              <button
                type="button"
                className={cards.open.includes(w.id) ? "word-chip on" : "word-chip"}
                aria-expanded={cards.open.includes(w.id)}
                onClick={() => cards.toggle(w.id)}
              >
                {w.term}
              </button>
            </li>
          ))}
        </ul>
      </div>
      {picked.length > 0 ? (
        <ul className="words-list">
          {picked.map((w) => (
            <WordCard key={w.id} word={w} scope={scope} open onToggle={() => cards.toggle(w.id)} cards={cards} />
          ))}
        </ul>
      ) : null}
    </div>
  );
}
