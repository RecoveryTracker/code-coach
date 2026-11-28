/**
 * Slides: passive tutorials. You watch; nothing is asked of you.
 *
 * Pick a deck (data types, syntax, patterns), then step through it with Prev / Next, the arrow keys or
 * Space, or press Play and let it advance by itself. Each slide shows a title, a plain explanation, the code,
 * what the code prints (the "Output" panel appears about a second after the code), and the one thing to
 * remember. Autoplay is off until you turn it on, stops on the last slide, and remembers its speed.
 *
 * The rules that are not pixels (timing, keys, clamping) are in lib/slides.ts, tested in node.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchSlideDeck, fetchSlides } from "../api";
import { tokenize } from "../lib/codeColors";
import { languageName } from "../lib/languageNames";
import {
  DEFAULT_SPEED,
  LOOP_KEY,
  RESUME_KEY,
  SHUFFLE_KEY,
  SPEEDS,
  SPEED_KEY,
  autoStep,
  clampIndex,
  deckPositionLabel,
  isLast,
  keyAction,
  nextDeckId,
  outputDelayMs,
  parseFlag,
  parseResume,
  parseSpeed,
  pressTarget,
  progressLabel,
  resumeLabel,
  serializeResume,
  slideDurationMs,
  speedLabel,
  upNextLabel,
} from "../lib/slides";
import type { SlideDeck, SlideList } from "../lib/slides";
import "../styles/slides.css";

function savedSpeed(): number {
  try {
    return parseSpeed(window.localStorage.getItem(SPEED_KEY));
  } catch {
    return DEFAULT_SPEED;
  }
}

function saveSpeed(speed: number): void {
  try {
    window.localStorage.setItem(SPEED_KEY, String(speed));
  } catch {
    /* private mode or blocked storage: the speed just is not remembered */
  }
}

function savedFlag(key: string, fallback: boolean): boolean {
  try {
    return parseFlag(window.localStorage.getItem(key), fallback);
  } catch {
    return fallback;
  }
}

function saveStore(key: string, value: string): void {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    /* blocked storage: just not remembered */
  }
}

function readStore(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function Code({ code, syntax }: { code: string; syntax: SlideDeck["syntax"] }) {
  const runs = useMemo(() => tokenize(code, syntax ?? undefined), [code, syntax]);
  return (
    <pre className="sl-code" tabIndex={0} aria-label="Code">
      <code>
        {runs.map((r, i) => (
          <span key={i} className={`tk-${r.kind}`}>
            {r.text}
          </span>
        ))}
      </code>
    </pre>
  );
}

export default function Slides({
  language,
  onChangeLanguage,
}: {
  /** The app's language (the picker at the top). */
  language: string;
  /** Switch the app's language, the same switch as the picker. */
  onChangeLanguage?: (id: string) => void;
}) {
  const [list, setList] = useState<SlideList | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [deck, setDeck] = useState<SlideDeck | null>(null);
  const [deckError, setDeckError] = useState<string | null>(null);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState<number>(savedSpeed);
  const [outputShown, setOutputShown] = useState(false);
  const [loop, setLoop] = useState<boolean>(() => savedFlag(LOOP_KEY, false));
  const [shuffle, setShuffle] = useState<boolean>(() => savedFlag(SHUFFLE_KEY, false));
  const [resumeNote, setResumeNote] = useState<string | null>(null);
  const seenRef = useRef<string[]>([]);
  const openToken = useRef(0);
  const triedResume = useRef(false);

  // The decks for the app's language. Changing the language closes the open deck.
  useEffect(() => {
    let cancelled = false;
    setList(null);
    setListError(null);
    setDeck(null);
    setPlaying(false);
    fetchSlides(language)
      .then((got) => {
        if (!cancelled) setList(got);
      })
      .catch((e: unknown) => {
        if (!cancelled) setListError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [language]);

  const order = useMemo(() => (list ? list.decks.map((d) => d.id) : []), [list]);

  /** Open a deck at a slide. `keepPlaying` is for play-through: autoplay carries on into the new deck. */
  const open = useCallback((id: string, start = 0, keepPlaying = false, resumed = false) => {
    const token = ++openToken.current;
    setDeckError(null);
    if (!keepPlaying) setPlaying(false);
    fetchSlideDeck(id)
      .then((got) => {
        if (token !== openToken.current) return;
        if (!seenRef.current.includes(got.id)) seenRef.current.push(got.id);
        const at = clampIndex(start, got.slides.length);
        setIndex(at);
        setResumeNote(resumed ? resumeLabel(got.title, at) : null);
        setDeck(got);
      })
      .catch((e: unknown) => {
        if (token !== openToken.current) return;
        setPlaying(false);
        setDeckError(e instanceof Error ? e.message : String(e));
      });
  }, []);

  // Reopening the tab picks up where you were, paused. A deck that is gone falls back to the picker.
  useEffect(() => {
    if (!list || triedResume.current) return;
    triedResume.current = true;
    const r = parseResume(readStore(RESUME_KEY), order);
    if (r) open(r.deckId, r.index, false, true);
  }, [list, order, open]);

  const count = deck?.slides.length ?? 0;
  const slide = deck ? deck.slides[clampIndex(index, count)] : null;

  const go = useCallback(
    (to: number) => {
      setIndex(clampIndex(to, count));
    },
    [count],
  );

  // The output shows up a moment after the code, every time a slide appears.
  useEffect(() => {
    setOutputShown(false);
    if (!slide || !slide.code) return undefined;
    const t = window.setTimeout(() => setOutputShown(true), outputDelayMs(speed));
    return () => window.clearTimeout(t);
  }, [deck, index, slide, speed]);

  // Remember the place (deck and slide) for the next visit.
  useEffect(() => {
    if (deck) saveStore(RESUME_KEY, serializeResume({ deckId: deck.id, index: clampIndex(index, count) }));
  }, [deck, index, count]);

  // The deck that follows this one. Shuffle picks at random, so it is picked once per deck (and per option).
  const deckId = deck?.id ?? null;
  const upNextId = useMemo(
    () =>
      deckId ? nextDeckId(order, deckId, { loop, shuffle, seen: seenRef.current, rng: Math.random }) : null,
    [deckId, order, loop, shuffle],
  );
  const upNextTitle = upNextId ? (list?.decks.find((d) => d.id === upNextId)?.title ?? null) : null;

  // Autoplay: stay on a slide for as long as it takes to read, then move on; at the end of a deck go on to
  // the next one (Loop: round to the first), or stop when there is none.
  useEffect(() => {
    if (!playing || !slide) return undefined;
    const t = window.setTimeout(() => {
      const to = autoStep(index, count);
      if (to !== null) setIndex(to);
      else if (upNextId) open(upNextId, 0, true);
      else setPlaying(false);
    }, slideDurationMs(slide, speed));
    return () => window.clearTimeout(t);
  }, [playing, slide, index, count, speed, upNextId, open]);

  const togglePlay = useCallback(() => {
    // Pressing Play on the last slide starts again from the top.
    if (!playing && deck && isLast(index, count) && count > 1) setIndex(0);
    setPlaying((p) => !p);
  }, [playing, deck, index, count]);

  const pick = (to: number) => {
    setPlaying(false);
    go(to);
  };

  const stateRef = useRef({ count, togglePlay });
  stateRef.current = { count, togglePlay };

  useEffect(() => {
    if (!deck) return undefined;
    const onKey = (e: KeyboardEvent) => {
      const el = document.activeElement as HTMLElement | null;
      const action = keyAction(e.key, {
        tag: el?.tagName ?? "",
        editable: !!el?.isContentEditable,
        ctrl: e.ctrlKey,
        alt: e.altKey,
        meta: e.metaKey,
      });
      if (action === "none") return;
      e.preventDefault();
      const s = stateRef.current;
      if (action === "toggle") s.togglePlay();
      else {
        setPlaying(false);
        // Functional update: presses in the same tick each move one slide from the latest index.
        setIndex((cur) => pressTarget(action, cur, s.count));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [deck]);

  const toggleLoop = () => {
    saveStore(LOOP_KEY, loop ? "0" : "1");
    setLoop(!loop);
  };
  const toggleShuffle = () => {
    saveStore(SHUFFLE_KEY, shuffle ? "0" : "1");
    setShuffle(!shuffle);
  };

  const chooseSpeed = (s: number) => {
    setSpeed(s);
    saveSpeed(s);
  };

  // ── The deck picker ──
  if (!deck) {
    const name = languageName(language);
    return (
      <div className="sl-wrap">
        <header className="sl-head">
          <h2>Slides</h2>
          <p className="sl-sub">Short tutorials you watch. Nothing to answer - step through or press Play.</p>
        </header>
        {listError ? <p className="sl-note">Could not load the slides: {listError}</p> : null}
        {!list && !listError ? <p className="sl-note">Loading…</p> : null}
        {list && list.decks.length === 0 ? (
          <div className="sl-empty">
            <p>No slides for {name} yet - the decks are all Python for now.</p>
            <button
              type="button"
              className="sl-btn primary"
              onClick={() => onChangeLanguage?.("python")}
              disabled={!onChangeLanguage}
            >
              Switch to Python
            </button>
          </div>
        ) : null}
        {list && list.decks.length > 0 ? (
          <ul className="sl-cards">
            {list.decks.map((d) => (
              <li key={d.id}>
                <button type="button" className="sl-card" onClick={() => open(d.id)}>
                  <span className="sl-card-title">{d.title}</span>
                  <span className="sl-card-blurb">{d.blurb}</span>
                  <span className="sl-card-count">{d.count} slides</span>
                </button>
              </li>
            ))}
          </ul>
        ) : null}
        {deckError ? <p className="sl-note">Could not open that deck: {deckError}</p> : null}
      </div>
    );
  }

  // ── A deck ──
  const i = clampIndex(index, count);
  const atFirst = i === 0;
  const atLast = isLast(i, count);
  return (
    <div className="sl-wrap">
      <div className="sl-top">
        <button
          type="button"
          className="sl-btn"
          onClick={() => {
            setPlaying(false);
            setDeck(null);
          }}
        >
          Back to decks
        </button>
        <span className="sl-deck-name">{deck.title}</span>
        <span className="sl-count" aria-live="polite">
          {[deckPositionLabel(order, deck.id), progressLabel(i, count)].filter(Boolean).join(" \u00b7 ")}
        </span>
      </div>
      {resumeNote ? <p className="sl-resume">{resumeNote}</p> : null}
      {upNextLabel(playing, atLast, upNextTitle) ? (
        <p className="sl-upnext" role="status">
          {upNextLabel(playing, atLast, upNextTitle)}
        </p>
      ) : null}

      {slide ? (
        <article className="sl-slide" key={`${deck.id}-${i}`}>
          <h2 className="sl-title">{slide.title}</h2>
          <p className="sl-text">{slide.text}</p>
          {slide.code ? <Code code={slide.code} syntax={deck.syntax} /> : null}
          {slide.code ? (
            <div className={`sl-out${outputShown ? " shown" : ""}`} aria-hidden={!outputShown}>
              <div className="sl-out-label">Output</div>
              <pre className="sl-out-body" tabIndex={outputShown ? 0 : -1}>
                {slide.output}
              </pre>
            </div>
          ) : null}
          {slide.point ? (
            <p className="sl-point">
              <span className="sl-point-tag">Remember</span> {slide.point}
            </p>
          ) : null}
        </article>
      ) : null}

      <div className="sl-controls" role="group" aria-label="Slide controls">
        <button type="button" className="sl-btn" onClick={() => pick(i - 1)} disabled={atFirst}>
          Prev
        </button>
        <button
          type="button"
          className={`sl-btn primary${playing ? " on" : ""}`}
          onClick={togglePlay}
          aria-pressed={playing}
        >
          {playing ? "Pause" : "Play"}
        </button>
        <button type="button" className="sl-btn" onClick={() => pick(i + 1)} disabled={atLast}>
          Next
        </button>
        <div className="sl-speeds" role="group" aria-label="Autoplay speed">
          {SPEEDS.map((s) => (
            <button
              key={s}
              type="button"
              className={`sl-speed${s === speed ? " on" : ""}`}
              aria-pressed={s === speed}
              onClick={() => chooseSpeed(s)}
            >
              {speedLabel(s)}
            </button>
          ))}
        </div>
        <div className="sl-flags" role="group" aria-label="Play-through options">
          <button type="button" className={`sl-speed${loop ? " on" : ""}`} aria-pressed={loop} onClick={toggleLoop}>
            Loop
          </button>
          <button
            type="button"
            className={`sl-speed${shuffle ? " on" : ""}`}
            aria-pressed={shuffle}
            onClick={toggleShuffle}
          >
            Shuffle decks
          </button>
        </div>
      </div>

      <ol className="sl-dots" aria-label="Slides">
        {deck.slides.map((s, n) => (
          <li key={n}>
            <button
              type="button"
              className={`sl-dot${n === i ? " on" : ""}${n < i ? " seen" : ""}`}
              aria-label={`Slide ${n + 1}: ${s.title}`}
              aria-current={n === i ? "step" : undefined}
              title={`${n + 1}. ${s.title}`}
              onClick={() => pick(n)}
            />
          </li>
        ))}
      </ol>
      <p className="sl-hint">Right arrow or Space: next. Left arrow: back. P: play or pause. Play carries on into the next deck.</p>
    </div>
  );
}
