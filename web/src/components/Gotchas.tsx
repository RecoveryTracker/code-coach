/**
 * Gotchas: an endless feed of trap questions, one card at a time.
 *
 * The kind of post that goes round as "Python Quiz": a short program on a dark card, four answers,
 * and an obvious reading that is wrong. Pick one (click, 1-4 or A-D), see at once whether it was
 * right, read the one-line trap and the plain explanation, optionally run the program for real,
 * and press Next (Enter, Space or the right arrow). A streak counts the right answers in a row.
 *
 * The browser never has the answer before it answers: /api/gotchas/next sends the program and
 * four options, and /api/gotchas/answer says which was right. The rules that are not pixels (the
 * streak, the keys, the deck line) live in lib/gotchas.ts, tested in node.
 *
 * Three things strengthen the think-then-check loop: "How sure are you?" (Sure / Just guessing, keys S and G,
 * sent with the answer so a sure-but-wrong card comes back sooner and a guessed-right one comes back once),
 * an optional "Add my reasoning" note (shown again beside the Why), and "My traps" (GotchaTraps.tsx), the
 * cards you missed and have not mastered. While the cursor is in a text box every quiz shortcut is off.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { answerGotcha, fetchGotchaNext, fetchGotchas, runGotcha } from "../api";
import type { Syntax } from "../lib/codeColors";
import {
  CONFIDENCE_CHOICES,
  DEFAULT_CONFIDENCE,
  NOTE_MAX,
  accentStyle,
  cardAwardKey,
  chooseLanguage,
  clampNote,
  dailyAwardKey,
  dailyLine,
  deckLine,
  errorText,
  excludeParam,
  feedbackLine,
  keyAction,
  noteCounter,
  offeredLanguages,
  optionLetter,
  optionState,
  pushRecent,
  recentIds,
  streakLabel,
  streakTier,
} from "../lib/gotchas";
import type {
  Confidence,
  GotchaAnswer,
  GotchaCard,
  GotchaDaily,
  GotchaLang,
  GotchaRun,
  GotchaSummary,
  GotchaTrap,
  LangInfo,
} from "../lib/gotchas";
import { award } from "../lib/momentum";
import "../styles/gotchas.css";
import GotchaAdd from "./GotchaAdd";
import { CodeBlock } from "./GotchaCode";
import GotchaLangMenu from "./GotchaLangMenu";
import GotchaTraps from "./GotchaTraps";

const LANG_KEY = "code-coach:gotchas-language";
const RECENT_KEY = "code-coach:gotchas-recent";

/** The remembered language (python when nothing is saved); the server's list of offered ones decides if it can be used. */
function savedLanguage(): GotchaLang {
  try {
    const saved = window.localStorage.getItem(LANG_KEY);
    return saved && /^[a-z]{1,12}$/.test(saved) ? saved : "python";
  } catch {
    return "python";
  }
}

/** The languages used lately, newest first (for the quick buttons). */
function savedRecent(): string[] {
  try {
    const raw: unknown = JSON.parse(window.localStorage.getItem(RECENT_KEY) ?? "[]");
    return Array.isArray(raw) ? raw.filter((x): x is string => typeof x === "string").slice(0, 4) : [];
  } catch {
    return [];
  }
}

function DailyCard({
  daily,
  playing,
  busy,
  onPlay,
}: {
  daily: GotchaDaily | null;
  playing: boolean;
  busy: boolean;
  onPlay: () => void;
}) {
  if (!daily || daily.total === 0) return null;
  return (
    <section className={`gq-daily${daily.complete ? " done" : ""}`} aria-label="Daily 5">
      <div className="gq-daily-text">
        <h3>{dailyLine(daily)}</h3>
        <p>
          {daily.complete
            ? "Five cards finished. A fresh five arrives tomorrow."
            : "The same five cards all day. Finish them for a bonus."}
        </p>
      </div>
      <ol className="gq-dots" aria-label="Daily 5 progress">
        {daily.dots.map((d, i) => (
          <li key={i} className={`gq-dot ${d}`}>
            <span className="gq-sr">
              Card {i + 1}: {d === "todo" ? "not answered yet" : d === "right" ? "right" : "missed"}
            </span>
          </li>
        ))}
      </ol>
      {daily.complete ? (
        <span className="gq-daily-done">Done today</span>
      ) : (
        <button type="button" className="ws-btn primary" disabled={busy} onClick={onPlay}>
          {playing ? "Keep going" : daily.done > 0 ? "Continue today's 5" : "Play today's 5"}
        </button>
      )}
    </section>
  );
}

function RunIt({ card }: { card: GotchaCard }) {
  const [out, setOut] = useState<GotchaRun | "busy" | "down" | null>(null);
  const alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);
  const run = () => {
    if (out === "busy") return;
    setOut("busy");
    runGotcha({ id: card.id, language: card.language })
      .then((r) => alive.current && setOut(r))
      .catch(() => alive.current && setOut("down"));
  };
  return (
    <div className="gq-run">
      <button type="button" className="ws-btn" onClick={run} disabled={out === "busy"}>
        {out === "busy" ? "Running..." : "Run it"}
      </button>
      {out === "down" ? <p className="gq-run-note">Could not reach the app - is the API running?</p> : null}
      {out && out !== "busy" && out !== "down" ? (
        <div className="gq-run-out" data-testid="gq-run">
          <div className="gq-run-label">{out.compile_error ? "The compiler says" : "It really prints"}</div>
          {out.stdout ? <pre className="gq-run-text">{out.stdout}</pre> : null}
          {out.error ? <pre className="gq-run-text err">{out.error}</pre> : null}
          {!out.stdout && !out.error ? <p className="gq-run-note">It ran and printed nothing.</p> : null}
        </div>
      ) : null}
    </div>
  );
}

export default function Gotchas() {
  const [language, setLanguage] = useState<GotchaLang>(savedLanguage);
  // Which languages the server can run here, with their card counts; null until it has said.
  const [offered, setOffered] = useState<LangInfo[] | null>(null);
  // Every language's colouring rules, sent once with the first summary.
  const [syntax, setSyntax] = useState<Record<string, Syntax>>({});
  const [recentLangs, setRecentLangs] = useState<string[]>(savedRecent);
  const [card, setCard] = useState<GotchaCard | null>(null);
  const [summary, setSummary] = useState<GotchaSummary | null>(null);
  const [chosen, setChosen] = useState<number | null>(null);
  const [result, setResult] = useState<GotchaAnswer | null>(null);
  const [streak, setStreak] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dailyMode, setDailyMode] = useState(false);
  // How sure you are: kept for the session (not saved), so it stays as you left it from card to card.
  const [confidence, setConfidence] = useState<Confidence>(DEFAULT_CONFIDENCE);
  // Your reasoning for this card (optional), and whether its box is open.
  const [note, setNote] = useState("");
  const [noteOpen, setNoteOpen] = useState(false);
  const [trapsOpen, setTrapsOpen] = useState(false);
  const wantCard = useRef("");
  const noteBox = useRef<HTMLTextAreaElement | null>(null);
  const noteBtn = useRef<HTMLButtonElement | null>(null);
  const trapsBtn = useRef<HTMLButtonElement | null>(null);
  const recent = useRef<string[]>([]);
  const busy = useRef(false);
  const alive = useRef(true);
  const nextRef = useRef<HTMLButtonElement | null>(null);
  const requestId = useRef(0);

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);

  const load = useCallback(async (lang: GotchaLang, daily: boolean, first = false, cardId = "") => {
    const mine = ++requestId.current;
    setLoading(true);
    setError("");
    try {
      const c = await fetchGotchaNext(lang, excludeParam(recent.current), daily, cardId);
      if (!alive.current || mine !== requestId.current) return;
      recent.current = recentIds(recent.current, c.id);
      setCard(c);
      setSummary(c.summary);
      setChosen(null);
      setResult(null);
      setNote("");
      setNoteOpen(false);
      if (first) setStreak(c.summary.streak);
      if (daily && c.why_picked !== "daily") setDailyMode(false);
    } catch (e) {
      if (alive.current && mine === requestId.current) setError(errorText(e));
    } finally {
      if (alive.current && mine === requestId.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Python is always there, so ask the server about it first: its answer lists what else can be offered.
    fetchGotchas("python")
      .then((s) => {
        if (!alive.current) return;
        setSyntax(s.syntax ?? {});
        setOffered(offeredLanguages(s.languages));
      })
      .catch(() => alive.current && setOffered(offeredLanguages(undefined)));
  }, []);

  useEffect(() => {
    if (!offered) return;
    const usable = chooseLanguage(language, offered);
    if (usable !== language) {
      setLanguage(usable); // a remembered language this machine cannot run
      return;
    }
    recent.current = [];
    setDailyMode(false);
    const want = wantCard.current; // "Try again" on a card of another language: switch, then serve that card
    wantCard.current = "";
    void load(language, false, true, want);
  }, [language, offered, load]);

  const pickLanguage = (next: GotchaLang) => {
    if (next === language) return;
    const used = pushRecent(recentLangs, next);
    setRecentLangs(used);
    try {
      window.localStorage.setItem(LANG_KEY, next);
      window.localStorage.setItem(RECENT_KEY, JSON.stringify(used));
    } catch {
      /* a remembered choice is only a convenience */
    }
    setCard(null);
    setLanguage(next);
  };

  // The switch shows each language's card count, kept current as you add or delete cards of your own.
  const switchable = useMemo(
    () => (offered ?? []).map((l) => (summary && l.id === summary.language ? { ...l, count: summary.total } : l)),
    [offered, summary],
  );

  const answer = useCallback(
    async (i: number) => {
      if (!card || chosen !== null || busy.current || loading) return;
      busy.current = true;
      setChosen(i);
      try {
        const r = await answerGotcha({
          id: card.id,
          language: card.language,
          chosen: i,
          confidence,
          ...(note.trim() ? { note: note.trim() } : {}),
        });
        if (!alive.current) return;
        setResult(r);
        setStreak(r.streak);
        setSummary(r.summary);
        if (r.correct) award("gotcha", cardAwardKey(card.language, card.id));
        if (r.daily.just_completed) award("gotcha_daily", dailyAwardKey(card.language, r.daily.day));
      } catch (e) {
        if (alive.current) {
          setChosen(null);
          setError(errorText(e));
        }
      } finally {
        busy.current = false;
      }
    },
    [card, chosen, loading, confidence, note],
  );

  // "Try again" in My traps: close the panel and serve that card in the feed (a normal card, a normal answer).
  const tryTrap = (t: GotchaTrap) => {
    setTrapsOpen(false);
    setDailyMode(false);
    if (t.language !== language) {
      wantCard.current = t.id;
      pickLanguage(t.language);
    } else {
      void load(language, false, false, t.id);
    }
  };

  const closeTraps = () => {
    setTrapsOpen(false);
    window.setTimeout(() => trapsBtn.current?.focus({ preventScroll: true }), 0);
  };

  useEffect(() => {
    if (noteOpen) noteBox.current?.focus({ preventScroll: true });
  }, [noteOpen]);

  const next = useCallback(() => {
    if (!result || loading) return;
    const stay = dailyMode && !result.daily.complete;
    if (!stay) setDailyMode(false);
    void load(language, stay);
  }, [result, loading, dailyMode, language, load]);

  const playDaily = () => {
    if (busy.current || loading) return;
    setDailyMode(true);
    void load(language, true);
  };

  // After an answer, the cursor goes to Next so Enter / Space just carry on.
  useEffect(() => {
    if (result) nextRef.current?.focus({ preventScroll: true });
  }, [result]);

  // Keyboard (the decisions are `keyAction` in lib/gotchas.ts): 1-4 / A-D answer, S and G say how sure you are,
  // Enter, Space and the right arrow go on. All of it is off while the cursor is in a text box or My traps is open.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      const act = keyAction(e.key, {
        tag: el?.tagName ?? "",
        editable: !!el?.isContentEditable,
        hasCard: !!card,
        answered: !!result,
        options: card?.options.length ?? 0,
        panelOpen: trapsOpen,
        ctrl: e.ctrlKey || e.metaKey || e.altKey,
      });
      if (act.kind === "none") return;
      e.preventDefault();
      if (act.kind === "next") next();
      else if (act.kind === "answer") void answer(act.index);
      else if (chosen === null) setConfidence(act.value);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [card, result, answer, next, trapsOpen, chosen]);

  const tier = streakTier(streak);
  const verdict = result ? (result.correct ? "right" : "wrong") : "";
  const answerIndex = result ? result.answer_index : null;
  const sureLine = result ? feedbackLine(result.confidence, result.correct) : null;

  return (
    <div className="gq-wrap">
      <header className="gq-head">
        <div>
          <h2>Gotchas</h2>
          <p className="gq-sub">Short programs where the obvious answer is a trap. One at a time, no end.</p>
        </div>
        {offered ? (
          <div className="gq-head-tools">
            <GotchaLangMenu languages={switchable} current={language} recent={recentLangs} onPick={pickLanguage} />
            <button
              type="button"
              ref={trapsBtn}
              className={`gq-traps-btn${trapsOpen ? " on" : ""}`}
              aria-expanded={trapsOpen}
              data-testid="gq-traps-btn"
              onClick={() => setTrapsOpen((open) => !open)}
            >
              My traps
            </button>
          </div>
        ) : null}
      </header>

      {trapsOpen ? (
        <GotchaTraps
          language={language}
          languages={offered ?? []}
          syntax={syntax}
          onClose={closeTraps}
          onTry={tryTrap}
        />
      ) : null}

      <div className="gq-feed" hidden={trapsOpen}>
        <DailyCard
          daily={summary?.daily ?? null}
          playing={dailyMode}
          busy={loading}
          onPlay={playDaily}
        />

        <div className="gq-status">
          <span className="gq-deck" data-testid="gq-deck">
            {summary ? deckLine(summary.seen, summary.total, summary.mine) : "Deck: ..."}
          </span>
          <span className="gq-streak-wrap" aria-live="polite">
            {streak > 0 ? (
              <span key={streak} className={`gq-streak tier${tier}`} data-testid="gq-streak">
                <span aria-hidden="true">{"\u{1F525}"}</span> {streakLabel(streak)}
              </span>
            ) : (
              <span className="gq-streak none" data-testid="gq-streak">
                No streak yet
              </span>
            )}
            {summary && summary.streak_best > 0 ? (
              <span className="gq-best" title="Your longest run of right answers">
                best {summary.streak_best}
              </span>
            ) : null}
          </span>
        </div>

        {error ? (
          <div className="gq-error" role="alert">
            <p>{error}</p>
            <button type="button" className="ws-btn" onClick={() => void load(language, dailyMode)}>
              Try again
            </button>
          </div>
        ) : null}

        {card ? (
          <article
            className={`gq-card ${language}${verdict ? ` ${verdict}` : ""}${loading ? " loading" : ""}`}
            style={accentStyle(card.language)}
            key={card.id}
            aria-label="Quiz card"
            data-testid="gq-card"
            data-card-id={card.id}
            data-state={verdict || (chosen !== null ? "checking" : "asking")}
          >
            <div className="gq-card-top">
              <h3 className="gq-title">{card.title}</h3>
              <span className="gq-badges">
                {dailyMode && summary ? (
                  <span className="gq-badge daily">
                    Daily 5 - {summary.daily.done} of {summary.daily.total} done
                  </span>
                ) : null}
                {card.mine ? <span className="gq-badge mine">Yours</span> : null}
                {card.why_picked === "again" ? <span className="gq-badge again">Back again</span> : null}
              </span>
            </div>

            <CodeBlock
              code={card.code}
              label={(offered ?? []).find((l) => l.id === card.language)?.name ?? card.language}
              syntax={syntax[card.language]}
            />

            <p className="gq-ask" id="gq-ask">
              What does this print? <span className="gq-hint">Click, or press 1-4 or A-D</span>
            </p>
            <div className="gq-sure" role="radiogroup" aria-label="How sure are you?" data-testid="gq-sure">
              <span className="gq-sure-label">How sure are you?</span>
              <span className="gq-sure-pills">
                {CONFIDENCE_CHOICES.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    role="radio"
                    aria-checked={confidence === c.id}
                    className={`gq-sure-btn ${c.id}${confidence === c.id ? " on" : ""}`}
                    disabled={chosen !== null}
                    data-testid={`gq-sure-${c.id}`}
                    onClick={() => setConfidence(c.id)}
                  >
                    {c.label} <span className="gq-sure-key" aria-hidden="true">{c.key}</span>
                  </button>
                ))}
              </span>
            </div>
            <div className="gq-options" role="group" aria-labelledby="gq-ask">
              {card.options.map((text, i) => {
                const st = optionState(i, chosen, answerIndex);
                return (
                  <button
                    key={i}
                    type="button"
                    className={`gq-option ${st}`}
                    disabled={chosen !== null}
                    aria-disabled={chosen !== null}
                    data-testid={`gq-option-${i}`}
                    onClick={() => void answer(i)}
                  >
                    <span className="gq-key" aria-hidden="true">
                      {optionLetter(i)}
                    </span>
                    <span className="gq-opt-text">{text}</span>
                    <span className="gq-mark" aria-hidden="true" />
                    <span className="gq-sr">
                      {st === "right"
                        ? " - your answer, correct"
                        : st === "wrong"
                          ? " - your answer, wrong"
                          : st === "reveal"
                            ? " - the right answer"
                            : ""}
                    </span>
                  </button>
                );
              })}
            </div>

            {!result ? (
              <div className="gq-reason">
                <button
                  type="button"
                  ref={noteBtn}
                  className="gq-reason-toggle"
                  aria-expanded={noteOpen}
                  aria-controls="gq-reason-box"
                  data-testid="gq-reason-toggle"
                  onClick={() => setNoteOpen((open) => !open)}
                >
                  {noteOpen ? "Hide my reasoning" : note.trim() ? "Edit my reasoning" : "Add my reasoning"}
                </button>
                {noteOpen ? (
                  <div className="gq-reason-box" id="gq-reason-box">
                    <textarea
                      ref={noteBox}
                      className="gq-reason-text"
                      data-testid="gq-reason-text"
                      rows={3}
                      maxLength={NOTE_MAX}
                      value={note}
                      placeholder="Why do I think so? (optional)"
                      aria-label="My reasoning (optional)"
                      onChange={(e) => setNote(clampNote(e.target.value))}
                      onKeyDown={(e) => {
                        // Escape closes this box only; every other key is just typing here.
                        if (e.key === "Escape") {
                          e.preventDefault();
                          e.stopPropagation();
                          setNoteOpen(false);
                          noteBtn.current?.focus({ preventScroll: true });
                        }
                      }}
                    />
                    <span className="gq-reason-count" data-testid="gq-reason-count">
                      {noteCounter(note)}
                    </span>
                  </div>
                ) : null}
              </div>
            ) : null}

            {result ? (
              <div className="gq-after">
                <p className={`gq-verdict ${verdict}`} role="status" data-testid="gq-verdict">
                  {result.correct ? "You got it" : "Not quite"}
                  {!result.correct ? (
                    <span>
                      {" - "}the answer is <strong className="gq-answer">{result.answer}</strong>
                    </span>
                  ) : null}
                </p>
                {sureLine ? (
                  <p className={`gq-sure-note ${result.confidence}`} role="status" data-testid="gq-feedback">
                    {sureLine}
                  </p>
                ) : null}
                {!result.correct && result.again_soon ? (
                  <p className="gq-again">This one will come back in a few cards.</p>
                ) : null}
                <section className="gq-why" aria-label="Why">
                  <h4>Why</h4>
                  <p className="gq-trap">
                    <span className="gq-trap-label">Trap</span> {result.trap}
                  </p>
                  <p className="gq-why-text">{result.why}</p>
                  {result.note ? (
                    <p className="gq-thought" data-testid="gq-thought">
                      <span className="gq-thought-label">What you thought:</span> {result.note}
                    </p>
                  ) : null}
                </section>
                {result.daily.just_completed ? (
                  <p className="gq-daily-win" role="status">
                    That is your Daily 5 finished.
                  </p>
                ) : null}
                <div className="gq-actions">
                  <RunIt key={card.id} card={card} />
                  <button
                    type="button"
                    className="ws-btn primary gq-next"
                    ref={nextRef}
                    onClick={next}
                    disabled={loading}
                    data-testid="gq-next"
                  >
                    Next {"→"}
                  </button>
                </div>
              </div>
            ) : null}
          </article>
        ) : !error ? (
          <div className="gq-card skeleton" aria-busy="true">
            <p className="gq-run-note">Dealing a card...</p>
          </div>
        ) : null}

        <GotchaAdd
          language={language}
          name={(offered ?? []).find((l) => l.id === language)?.name ?? language}
          onChanged={(s) => setSummary(s)}
          onTry={() => {
            setDailyMode(false);
            void load(language, false);
          }}
        />
      </div>
    </div>
  );
}
