/**
 * Workbook: a sentence, an empty box, and you type the program.
 *
 * Everywhere else in this app you are reading something or typing along with
 * something already on screen. Here nothing is on screen except what the
 * exercise asks for, which is the only arrangement that finds out whether you
 * can actually write it.
 *
 * One exercise at a time on purpose. A page of twelve laid out at once is a
 * list to skim; one at a time with the next arriving the moment this one
 * passes is a rhythm, and the rhythm is what puts it in your hands.
 *
 * A plain textarea rather than Monaco. These programs are one to four lines,
 * and an editor that completes your brackets is doing the half you came here
 * to practise.
 *
 * Tab does one of two things and you choose which — see TAB_KEY below.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  checkWorkbook,
  explainCode,
  fetchWorkbook,
  saveWorkbookDraft,
} from "../api";
import { award } from "../lib/momentum";
import {
  bounds,
  cleanRange,
  deal,
  poolFor,
  rangeLabel,
  reachedPage,
  readRange,
  writeRange,
  type Card,
  type Range,
} from "../lib/workbookShuffle";
import { VizPanel } from "./VizPanel";
import { WordsUsed } from "./WordsUsed";
import type {
  ExplainResult,
  WorkbookCheck,
  WorkbookData,
  WorkbookPage,
} from "../types";

/** How wide one press of Tab is, when Tab is indenting. */
const INDENT = "    ";

/**
 * Which of the two jobs Tab is doing. Remembered per browser, because it is
 * a habit rather than progress — and the wrong one every time you open the
 * screen would be worse than not having the choice.
 */
const TAB_KEY = "code-coach:workbook-tab";

function readTabMode(): boolean {
  try {
    return localStorage.getItem(TAB_KEY) === "indent";
  } catch {
    return false;
  }
}

type Props = {
  /** Which language you are writing in. Changing it reloads. */
  language: string;
};

/**
 * The sections, in the order they are worked through, with what each one is
 * for. Anything with a tier not listed here still shows, under its own name —
 * better a heading nobody wrote than a page nobody can find.
 */
const TIERS: { id: string; name: string; blurb: string }[] = [
  { id: "beginner", name: "Beginner", blurb: "One new idea per page." },
  { id: "practice", name: "More practice", blurb: "Ideas you have met, again." },
  {
    id: "intermediate",
    name: "Intermediate",
    blurb: "Built on all of it, plus real language features.",
  },
  { id: "advanced", name: "Advanced", blurb: "Later." },
  {
    id: "review",
    name: "Review",
    blurb: "Earlier pages, mixed and brought back.",
  },
];

/**
 * Shuffle: random exercises from a range of pages, instead of one page in
 * order. `deck` is the range dealt out (lib/workbookShuffle.ts), `at` the card
 * on screen, `deals` how many decks have been dealt (so the same exercise
 * coming up again in the next deck still starts with an empty box).
 */
type Shuffle = {
  range: Range;
  deck: Card[];
  at: number;
  deals: number;
  /** Cards answered right on the first Check / cards checked at least once. */
  right: number;
  tried: number;
  /** Whether the card on screen has been checked yet (only the first try is scored). */
  scored: boolean;
};

export default function Workbook({ language }: Props) {
  const [data, setData] = useState<WorkbookData | null>(null);
  const [shuffle, setShuffle] = useState<Shuffle | null>(null);
  /** The "Shuffle" panel in the page list: choose a range, then Start. */
  const [shuffleOpen, setShuffleOpen] = useState(false);
  const [rangeText, setRangeText] = useState({ from: "", to: "" });
  const [error, setError] = useState<string | null>(null);
  const [pageId, setPageId] = useState<string | null>(null);
  const [index, setIndex] = useState(0);
  const [code, setCode] = useState("");
  const [result, setResult] = useState<WorkbookCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [revealed, setRevealed] = useState(false);
  /**
   * True while the box still holds exactly what was restored for this
   * exercise, rather than something typed since arriving.
   *
   * Needed because drafts are now kept as you type: without it, "what you
   * wrote last time" would appear over the sentence you are in the middle of
   * writing, which is both untrue and unnerving.
   */
  const [restored, setRestored] = useState(false);
  /**
   * A line-by-line walkthrough of what is in the box, from /api/explain.
   *
   * Here because the alternative was copying the exercise into the main
   * editor to find out why it printed what it printed, which is a lot of
   * moving about to answer a question the workbook could answer itself.
   */
  const [walkthrough, setWalkthrough] = useState<ExplainResult | null>(null);
  const [explaining, setExplaining] = useState(false);
  /** "Watch it run" — the step-through, same panel as the main screen. */
  const [watching, setWatching] = useState(false);
  /** "Time complexity" — what the shape you just wrote costs. */
  const [costOpen, setCostOpen] = useState(false);
  /** Your own accepted code, restored into the box when you come back. */
  const [mine, setMine] = useState<Record<string, string>>({});
  /** Ids solved this session or in an earlier one. */
  const [done, setDone] = useState<Set<string>>(new Set());
  /** True: Tab puts four spaces in. False: Tab moves between the buttons. */
  const [tabIndents, setTabIndents] = useState(readTabMode);
  const box = useRef<HTMLTextAreaElement | null>(null);
  const nextButton = useRef<HTMLButtonElement | null>(null);
  /** Where to put the caret after an edit React has yet to apply. */
  const caret = useRef<[number, number] | null>(null);
  // Read when the exercise changes, without making the effect depend on it —
  // `mine` changes the moment you pass one, and that must not wipe the box
  // you are still looking at.
  const mineRef = useRef(mine);
  mineRef.current = mine;

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setError(null);
    setShuffle(null);
    setShuffleOpen(false);
    (async () => {
      try {
        const got = await fetchWorkbook(language);
        if (cancelled) return;
        setData(got);
        setDone(new Set(got.done));
        setMine(got.answers ?? {});
        // Where you were last time, not page one. Coming back to the workbook
        // after a break and being sent to "print hello" was the single most
        // annoying thing about it.
        setPageId((id) => {
          const known = (candidate: string | null | undefined) =>
            candidate && got.pages.some((p) => p.id === candidate)
              ? candidate
              : null;
          return known(id) ?? known(got.at) ?? (got.pages[0]?.id ?? null);
        });
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "API error");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [language]);

  // In a shuffle the card decides the page and the exercise; otherwise the
  // page you picked and where you are on it.
  const card = shuffle ? (shuffle.deck[shuffle.at] ?? null) : null;
  const page: WorkbookPage | null = useMemo(
    () => data?.pages.find((p) => p.id === (card ? card.pageId : pageId)) ?? null,
    [data, pageId, card],
  );

  /**
   * The pages grouped into sections, in tier order, keeping each tier's own
   * page order. A tier nobody has written pages for does not appear, and a
   * tier this code has never heard of still does — at the end, under its own
   * name, rather than vanishing.
   */
  const sections = useMemo(() => {
    const all = data?.pages ?? [];
    const known = TIERS.map((t) => ({
      ...t,
      pages: all.filter((p) => p.tier === t.id),
    })).filter((t) => t.pages.length > 0);
    const named = new Set(TIERS.map((t) => t.id));
    const rest = [...new Set(all.map((p) => p.tier))].filter(
      (t) => !named.has(t),
    );
    return [
      ...known,
      ...rest.map((id) => ({
        id,
        name: id,
        blurb: "",
        pages: all.filter((p) => p.tier === id),
      })),
    ];
  }, [data]);
  const exercise = card
    ? (page?.exercises.find((e) => e.id === card.exerciseId) ?? null)
    : (page?.exercises[index] ?? null);
  /** Changes for every card a shuffle shows, so the box empties even if an exercise comes round again. */
  const shuffleTurn = shuffle ? `${shuffle.deals}:${shuffle.at}` : "";

  // Opening a page lands on the first exercise you have not done, so coming
  // back to one you are halfway through carries on rather than making you
  // scroll past twelve ticks.
  //
  // Keyed on the page id and nothing else. Adding `done` would re-run it as
  // soon as you solved one and jump you forward mid-page; adding `index`
  // would fight every Back and Next. The one thing that should move you is
  // arriving at a different page.
  const pageStart = page?.id;
  useEffect(() => {
    if (!page) return;
    const firstUndone = page.exercises.findIndex((e) => !done.has(e.id));
    setIndex(firstUndone === -1 ? 0 : firstUndone);
  }, [pageStart]); // eslint-disable-line react-hooks/exhaustive-deps

  /**
   * The draft not yet sent to the server, and the timer that will send it.
   *
   * Typing is the work, so it has to survive leaving the exercise. Sending on
   * every keystroke would be a request per character, so it waits until you
   * pause — but a pause is not guaranteed before you click away, which is why
   * `flushDraft` exists and why leaving an exercise calls it.
   */
  const pending = useRef<{ pageId: string; exerciseId: string; code: string } | null>(
    null,
  );
  const draftTimer = useRef<number | null>(null);

  const flushDraft = useCallback(() => {
    if (draftTimer.current !== null) {
      window.clearTimeout(draftTimer.current);
      draftTimer.current = null;
    }
    const waiting = pending.current;
    pending.current = null;
    if (!waiting) return;
    // A draft that fails to save is not worth interrupting the typing for.
    void saveWorkbookDraft({
      page_id: waiting.pageId,
      exercise_id: waiting.exerciseId,
      code: waiting.code,
      language,
    }).catch(() => undefined);
  }, [language]);

  const rememberDraft = useCallback(
    (text: string) => {
      // A shuffle is practice from an empty box: what you type there is not
      // kept as the exercise's draft (it would replace the answer you left).
      if (!page || !exercise || shuffle) return;
      pending.current = {
        pageId: page.id,
        exerciseId: exercise.id,
        code: text,
      };
      if (draftTimer.current !== null) window.clearTimeout(draftTimer.current);
      draftTimer.current = window.setTimeout(flushDraft, 600);
    },
    [page, exercise, flushDraft, shuffle],
  );

  // Leaving the screen entirely still has to keep what is in the box.
  useEffect(() => flushDraft, [flushDraft]);

  /**
   * Change the box, and keep the change.
   *
   * Everything that edits the text goes through here — typing, both Tab
   * indents, and Clear — so none of them can be the one that forgets. The
   * restore when the exercise changes deliberately does not: that is reading
   * what was kept, not writing it again.
   */
  const writeCode = useCallback(
    (text: string) => {
      setCode(text);
      setRestored(false);
      // The walkthrough was about the code as it was a moment ago.
      setWalkthrough(null);
      if (exercise && !shuffle) {
        setMine((was) => ({ ...was, [exercise.id]: text }));
      }
      rememberDraft(text);
    },
    [exercise, rememberDraft, shuffle],
  );

  // A new exercise starts empty and focused, so the only thing between
  // reading it and typing it is reading it. One you have already worked on
  // starts with what you wrote — whether or not it was ever checked, and
  // whether or not it was right, because half-finished work is exactly what
  // you came back for.
  useEffect(() => {
    // Send whatever the last exercise was left holding before swapping the
    // box out from under it.
    flushDraft();
    // A shuffle card always starts empty: the point is writing it from nothing.
    const kept = exercise && !shuffleTurn ? (mineRef.current[exercise.id] ?? "") : "";
    setCode(kept);
    setRestored(kept !== "");
    setResult(null);
    setWalkthrough(null);
    setWatching(false);
    setCostOpen(false);
    setRevealed(false);
    box.current?.focus();
  }, [exercise?.id, shuffleTurn]); // eslint-disable-line react-hooks/exhaustive-deps

  // Editing through React means the value comes back on the next render, and
  // the browser has by then put the caret at the end. Anything that edits the
  // text says where the caret belongs and this puts it there.
  useEffect(() => {
    const at = caret.current;
    if (!at || !box.current) return;
    caret.current = null;
    box.current.setSelectionRange(at[0], at[1]);
  }, [code]);

  const toggleTab = useCallback(() => {
    setTabIndents((was) => {
      const next = !was;
      try {
        localStorage.setItem(TAB_KEY, next ? "indent" : "move");
      } catch {
        /* the choice just won't outlive the tab */
      }
      return next;
    });
  }, []);

  // Ctrl+M from anywhere on the screen, so the switch is reachable even when
  // Tab is busy indenting — which is exactly when you need it and exactly
  // when you cannot Tab to the button.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "m" && event.key !== "M") return;
      // Control on every platform, never Command: Cmd+M minimises the window
      // on a Mac. Monaco binds this the same way, and for the same reason.
      if (!event.ctrlKey || event.metaKey || event.altKey) return;
      event.preventDefault();
      toggleTab();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [toggleTab]);

  const check = useCallback(async () => {
    if (!page || !exercise || checking || !code.trim()) return;
    setChecking(true);
    try {
      const got = await checkWorkbook({
        page_id: page.id,
        exercise_id: exercise.id,
        code,
        language,
        review: !!shuffle,
      });
      setResult(got);
      if (shuffle && !shuffle.scored) {
        setShuffle((s) =>
          s ? { ...s, scored: true, tried: s.tried + 1, right: s.right + (got.passed ? 1 : 0) } : s,
        );
      }
      if (got.passed) {
        award("workbook_page", `${page.id}:${exercise.id}`);
        setDone((was) => new Set(was).add(exercise.id));
        setMine((was) => ({ ...was, [exercise.id]: code }));
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't run that.");
    } finally {
      setChecking(false);
    }
  }, [checking, code, exercise, language, page, shuffle]);

  const pageAfter = useMemo(() => {
    if (!data || !page) return null;
    const at = data.pages.findIndex((p) => p.id === page.id);
    return at === -1 ? null : (data.pages[at + 1] ?? null);
  }, [data, page]);

  const atPageEnd = !shuffle && page ? index >= page.exercises.length - 1 : false;

  /**
   * Start a shuffle over pages from..to. Nothing happens for a range with no
   * exercises in it (the panel says so instead).
   */
  const startShuffle = useCallback(
    (want: Range) => {
      if (!data) return;
      const range = cleanRange(want, data.pages);
      const pool = poolFor(data.pages, range);
      if (pool.length === 0) return;
      writeRange(language, range);
      setRangeText({ from: String(range.from), to: String(range.to) });
      setShuffle({ range, deck: deal(pool), at: 0, deals: 1, right: 0, tried: 0, scored: false });
      setShuffleOpen(false);
    },
    [data, language],
  );

  /** The next card, dealing a fresh deck when this one runs out (so a shuffle never ends). */
  const nextCard = useCallback(() => {
    setShuffle((s) => {
      if (!s || !data) return s;
      if (s.at + 1 < s.deck.length) return { ...s, at: s.at + 1, scored: false };
      const deck = deal(poolFor(data.pages, s.range), Math.random, s.deck[s.at]?.pageId ?? "");
      return { ...s, deck, at: 0, deals: s.deals + 1, scored: false };
    });
  }, [data]);

  const move = useCallback(
    (delta: number) => {
      if (shuffle) {
        // Back goes to the card before (it starts empty again, and is not scored twice).
        setShuffle((s) => (s ? { ...s, at: Math.max(0, s.at + delta), scored: true } : s));
        return;
      }
      if (!page) return;
      setIndex((i) => Math.min(page.exercises.length - 1, Math.max(0, i + delta)));
    },
    [page, shuffle],
  );

  // Up and down step through the pages - "Which is bigger" to "Two
  // conditions at once" and back - so moving on never means reaching for
  // the mouse. Not while typing: in the code box (or any field) the arrows
  // belong to the cursor, and a held modifier means some other shortcut.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
      if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
      const target = event.target as HTMLElement | null;
      const typing =
        target instanceof HTMLTextAreaElement ||
        target instanceof HTMLInputElement ||
        target instanceof HTMLSelectElement ||
        target?.isContentEditable;
      if (typing || !data || !page || shuffle) return;
      const at = data.pages.findIndex((p) => p.id === page.id);
      const to = data.pages[at + (event.key === "ArrowDown" ? 1 : -1)];
      event.preventDefault();
      if (to) setPageId(to.id);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [data, page, shuffle]);

  /** Forward: the next exercise, or the next page once this one runs out. */
  const onward = useCallback(() => {
    if (shuffle) {
      nextCard();
      return;
    }
    if (atPageEnd) {
      if (pageAfter) setPageId(pageAfter.id);
      return;
    }
    move(1);
  }, [atPageEnd, move, nextCard, pageAfter, shuffle]);

  // Once an answer is right, the cursor goes to Next so plain Enter carries
  // on. Done in an effect rather than inside check() because the button's
  // disabled state is only settled after the render that shows the verdict.
  useEffect(() => {
    if (result?.passed) nextButton.current?.focus();
  }, [result]);

  /** Indent or outdent, whole lines when several are selected. */
  const indent = (out: boolean) => {
    const el = box.current;
    if (!el) return;
    const from = el.selectionStart;
    const to = el.selectionEnd;
    const lineStart = code.lastIndexOf("\n", from - 1) + 1;

    // Several lines selected: shift every one of them, the way an editor
    // does, rather than replacing the selection with four spaces.
    if (code.slice(from, to).includes("\n")) {
      const lineEnd = code.indexOf("\n", to) === -1 ? code.length : to;
      const block = code.slice(lineStart, lineEnd);
      const shifted = block
        .split("\n")
        .map((line) =>
          out
            ? line.replace(/^ {1,4}/, "")
            : line
              ? INDENT + line
              : line,
        )
        .join("\n");
      writeCode(code.slice(0, lineStart) + shifted + code.slice(lineEnd));
      caret.current = [lineStart, lineStart + shifted.length];
      return;
    }

    if (out) {
      // Take back up to four spaces from in front of the caret.
      const before = code.slice(lineStart, from);
      const spaces = before.length - before.replace(/ {1,4}$/, "").length;
      if (!spaces) return;
      writeCode(code.slice(0, from - spaces) + code.slice(from));
      caret.current = [from - spaces, from - spaces];
      return;
    }

    writeCode(code.slice(0, from) + INDENT + code.slice(to));
    caret.current = [from + INDENT.length, from + INDENT.length];
  };

  const onKeyDown = (event: React.KeyboardEvent) => {
    // Ctrl+Enter checks, and once it has passed, moves on — so the loop works
    // even if focus has wandered back into the box.
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      if (result?.passed) onward();
      else void check();
      return;
    }
    // Escape always gives Tab back, whatever the switch says. A control that
    // swallows Tab has to leave one way out that does not need Tab.
    if (event.key === "Escape") {
      box.current?.blur();
      return;
    }
    if (event.key !== "Tab" || event.ctrlKey || event.metaKey || event.altKey) {
      return;
    }
    if (!tabIndents) return; // let the browser move focus, as it always has
    event.preventDefault();
    indent(event.shiftKey);
  };

  if (error) return <div className="lessons-empty">Couldn't load it: {error}</div>;
  if (!data) return <div className="lessons-empty">Loading…</div>;
  if (!data.has_workbook) {
    return (
      <div className="lessons-empty">
        No workbook in {data.language_name} — it has no statement that prints a line
        and no loop, so every exercise here would have to be faked. Switch
        language to use it.
      </div>
    );
  }

  const reached = reachedPage(data.pages, done, data.at || pageId);

  const pageDone = page
    ? page.exercises.filter((e) => done.has(e.id)).length
    : 0;
  const allDone = page ? pageDone === page.exercises.length : false;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Workbook</h2>
        <p className="lessons-intro">
          A sentence, an empty box, and you write it. {data.pages.length} pages,
          one new idea each, twelve goes at every one.
        </p>
        <ShufflePanel
          pages={data.pages}
          reached={reached}
          active={shuffle}
          open={shuffleOpen}
          rangeText={rangeText}
          setRangeText={setRangeText}
          onToggle={() => {
            if (shuffle) {
              setShuffle(null);
              setShuffleOpen(false);
              return;
            }
            if (!shuffleOpen) {
              const kept = readRange(language);
              const r = kept ? cleanRange(kept, data.pages) : { from: bounds(data.pages).from, to: reached };
              setRangeText({ from: String(r.from), to: String(r.to) });
            }
            setShuffleOpen((o) => !o);
          }}
          onStart={startShuffle}
        />
        {sections.map((section) => (
          <div className="wb-section" key={section.id}>
            <h4 className="wb-section-head">
              {section.name}
              <span className="wb-section-count">
                {section.pages.length} pages
              </span>
            </h4>
            {section.blurb ? (
              <p className="wb-section-blurb">{section.blurb}</p>
            ) : null}
            {section.pages.map((p) => {
              const n = p.exercises.filter((e) => done.has(e.id)).length;
              return (
                <button
                  key={p.id}
                  type="button"
                  className={`lessons-pick${p.id === pageId && !shuffle ? " on" : ""}`}
                  onClick={() => {
                    // Picking a page ends a shuffle: you asked for that page.
                    setShuffle(null);
                    setPageId(p.id);
                  }}
                >
                  <span className="lessons-pick-name">
                    {p.number}. {p.name}
                  </span>
                  <span className="lessons-pick-blurb">
                    {n === p.exercises.length
                      ? "done"
                      : `${n} of ${p.exercises.length}`}
                  </span>
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {page && exercise ? (
        <article className="lessons-open wb">
          {shuffle ? (
            <header className="wb-shuffle-head">
              <p className="wb-shuffle-line">
                <strong>Shuffle</strong> · {rangeLabel(shuffle.range)} ·{" "}
                <span data-testid="wb-shuffle-score">
                  {shuffle.right} of {shuffle.tried} right first try
                </span>
                <button type="button" className="ws-btn wb-shuffle-stop" onClick={() => setShuffle(null)}>
                  Stop shuffle
                </button>
              </p>
              {/* Which page it came from, but not the page's example: that would hand you the shape. */}
              <h3>
                From page {page.number}: {page.name}
              </h3>
            </header>
          ) : (
          <header>
            <h3>
              {page.number}. {page.name}
            </h3>
            <p className="lessons-blurb">{page.teaches}</p>
            <p className="wb-example">{page.example}</p>
          </header>
          )}

          {shuffle ? null : (
          <div className="wb-track" aria-label="Progress through this page">
            {page.exercises.map((e, i) => (
              <button
                key={e.id}
                type="button"
                title={`Exercise ${i + 1}`}
                aria-current={i === index}
                className={
                  "wb-dot" +
                  (done.has(e.id) ? " done" : "") +
                  (i === index ? " on" : "")
                }
                onClick={() => setIndex(i)}
              >
                {i + 1}
              </button>
            ))}
            <span className="wb-count">
              {pageDone} / {page.exercises.length}
            </span>
          </div>
          )}

          <p className="wb-prompt">{exercise.prompt}</p>

          <textarea
            ref={box}
            className={
              "wb-code" +
              (result ? (result.passed ? " ok" : " bad") : "")
            }
            value={code}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            placeholder={`Write it in ${data.language_name}…`}
            onChange={(e) => {
              // Kept immediately, so moving between exercises restores
              // it without waiting for the server; the save that follows is
              // for surviving a reload.
              writeCode(e.target.value);
              // Editing after a wrong answer clears the verdict: leaving it
              // there next to changed code says something untrue.
              if (result && !result.passed) setResult(null);
            }}
            onKeyDown={onKeyDown}
          />

          <div className="wb-actions">
            <button
              type="button"
              className={`ws-btn primary${result ? " on" : ""}`}
              onClick={() => (result ? setResult(null) : void check())}
              disabled={checking || !code.trim()}
              aria-pressed={!!result}
              title={result ? "Click again to hide the result" : undefined}
            >
              {checking ? "Running…" : "Check"}
            </button>
            <span className="wb-chord">Ctrl+Enter</span>
            <span className="wb-chord">Ctrl+M switches Tab</span>
            <span className="wb-spacer" />
            <button
              type="button"
              className="ws-btn"
              onClick={() => move(-1)}
              disabled={shuffle ? shuffle.at === 0 : index === 0}
            >
              ‹ Back
            </button>
            <button
              ref={nextButton}
              type="button"
              className={`ws-btn${result?.passed ? " primary" : ""}`}
              onClick={onward}
              disabled={!shuffle && atPageEnd && !pageAfter}
            >
              {atPageEnd && pageAfter ? "Next page ›" : "Next ›"}
            </button>
            <button
              type="button"
              className="ws-btn"
              onClick={() => {
                writeCode("");
                setResult(null);
                box.current?.focus();
              }}
              disabled={!code}
              title="Empty the box and start this one again"
            >
              Clear
            </button>
            {/* The three "tell me about what I wrote" buttons. They behave
                alike on purpose: each one opens a panel about the code in
                the box, so none of it means leaving the workbook. */}
            <button
              type="button"
              className={walkthrough ? "ws-btn on" : "ws-btn"}
              onClick={async () => {
                if (walkthrough) {
                  setWalkthrough(null);
                  return;
                }
                setExplaining(true);
                try {
                  setWalkthrough(await explainCode(code));
                } catch (e) {
                  setError(
                    e instanceof Error ? e.message : "Couldn't explain that.",
                  );
                } finally {
                  setExplaining(false);
                }
              }}
              disabled={!code.trim() || explaining}
              title="Say what each line does, and why it printed what it printed"
            >
              {explaining
                ? "Reading…"
                : walkthrough
                  ? "Hide explain"
                  : "Explain my code"}
            </button>
            <button
              type="button"
              className={watching ? "ws-btn on" : "ws-btn"}
              onClick={() => setWatching((open) => !open)}
              // Whether there is a tracer is the server's answer, not a
              // list kept here: this read `language !== "python"` while
              // JavaScript and Dart both had one, so the button was grey
              // for two languages that could have answered.
              disabled={!code.trim() || !data.can_trace}
              title={
                data.can_trace
                  ? "Step through it and watch the variables change"
                  : `There is no step-through for ${data.language_name} yet`
              }
            >
              {watching ? "Hide picture" : "Watch it run"}
            </button>
            {page.cost ? (
              /* The button face is the answer — O(n), O(1), whatever the
                 page costs — because that is the part worth seeing at a
                 glance. The reasoning stays behind the click. It is no
                 longer disabled until you have typed: that guard was
                 protecting the explanation, and a greyed-out button would
                 dim the label along with it. */
              <button
                type="button"
                className={costOpen ? "ws-btn mono on" : "ws-btn mono"}
                onClick={() => setCostOpen((open) => !open)}
                title={
                  costOpen
                    ? "Hide why it costs this"
                    : "Time complexity — click for why"
                }
                aria-label={`Time complexity ${page.cost.label}`}
                aria-expanded={costOpen}
              >
                {page.cost.label}
              </button>
            ) : null}
            <button
              type="button"
              className="ws-btn"
              onClick={() => setRevealed((r) => !r)}
            >
              {revealed ? "Hide answer" : "Show answer"}
            </button>
            <button
              type="button"
              className={`ws-btn${tabIndents ? " primary" : ""}`}
              onClick={toggleTab}
              aria-pressed={tabIndents}
              title={
                tabIndents
                  ? "Tab puts four spaces in. Ctrl+M switches it back; Escape leaves the box."
                  : "Tab moves between the buttons. Ctrl+M makes it indent instead."
              }
            >
              {tabIndents ? "Tab: indents" : "Tab: moves on"}
            </button>
          </div>

          {costOpen && page.cost ? (
            /* Just the reasoning. The label is on the button that opened
               this, so repeating it here would say the same thing twice. */
            <p className="wb-cost">{page.cost.note}</p>
          ) : null}

          {watching ? (
            <div className="wb-viz">
              <VizPanel
                getCode={() => code}
                patternId={null}
                problemNumber={null}
                resetKey={exercise.id}
                language={language}
              />
            </div>
          ) : null}

          {walkthrough ? (
            <div className="wb-walkthrough">
              <p className="wb-walkthrough-summary">{walkthrough.summary}</p>
              <ol className="wb-walkthrough-lines">
                {walkthrough.lines.map((line) => (
                  <li key={line.line} style={{ marginLeft: line.depth * 16 }}>
                    <code>{line.source}</code>
                    <span>{line.text}</span>
                  </li>
                ))}
              </ol>
              {walkthrough.output_notes.map((note) => (
                <p className="wb-walkthrough-note" key={note}>
                  {note}
                </p>
              ))}
              {walkthrough.error_note ? (
                <p className="wb-walkthrough-error">{walkthrough.error_note}</p>
              ) : null}
              <WordsUsed words={walkthrough.words} scope="walk" />
            </div>
          ) : null}

          {!result && restored ? (
            <p className="wb-restored">
              This is what you wrote last time. Change it, or hit Clear to do
              it again from nothing.
            </p>
          ) : null}

          {result ? (
            result.passed ? (
              <div className="wb-verdict ok">
                <strong>Right.</strong>{" "}
                {shuffle
                  ? "Press Enter for another."
                  : !atPageEnd
                  ? "Press Enter for the next one."
                  : allDone && pageAfter
                    ? `Page finished — Enter starts ${pageAfter.name}.`
                    : allDone
                      ? "That is the last page finished."
                      : "Last one on the page. Enter moves on."}
                <Printed stdout={result.stdout} label="It printed" />
              </div>
            ) : (
              <div className="wb-verdict bad">
                {result.problem ? (
                  <>
                    <strong>Right output, but the code would crash.</strong>{" "}
                    {result.problem}
                    <Printed stdout={result.stdout} label="It printed" />
                  </>
                ) : result.failed_to_run ? (
                  <>
                    <strong>It didn't run.</strong>
                    <Printed stdout={result.stdout} label="It printed before it stopped" />
                    <pre className="wb-stderr">
                      {result.stderr.trim() || "No output and a non-zero exit."}
                    </pre>
                  </>
                ) : (
                  <>
                    <strong>It ran, and printed the wrong thing.</strong>
                    <div className="wb-diff">
                      <div>
                        <h4>You printed</h4>
                        <pre>{shown(result.stdout) || "(nothing)"}</pre>
                      </div>
                      <div>
                        <h4>It wanted</h4>
                        <pre>{result.expect || "(nothing)"}</pre>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )
          ) : (
            <p className="wb-wanted">
              {exercise.expect === "" ? (
                <>
                  It has to print <strong>nothing at all</strong> — the
                  condition does not hold, so the body never runs.
                </>
              ) : (
                <>
                  It has to print:{" "}
                  <code>{exercise.expect.split("\n").join(" ⏎ ")}</code>
                </>
              )}
            </p>
          )}

          {revealed ? (
            <div className="wb-answer">
              <h4>One way to write it</h4>
              <pre>{exercise.answer || "No reference for this language."}</pre>
            </div>
          ) : null}
        </article>
      ) : null}
    </div>
  );
}

/** Output as printed: only the trailing newline(s) go, so leading spaces and indentation stay visible. */
function shown(stdout: string): string {
  return (stdout ?? "").replace(/\s+$/, "");
}

/** What the program printed, under a verdict. Nothing at all is said plainly, so "it printed nothing" is never a blank. */
function Printed({ stdout, label }: { stdout: string; label: string }) {
  const out = shown(stdout);
  if (!out && label !== "It printed") return null;
  return (
    <div className="wb-printed" data-testid="wb-printed">
      <h4>{label}</h4>
      <pre>{out || "(nothing)"}</pre>
    </div>
  );
}

/**
 * The Shuffle button and its panel, at the top of the page list.
 *
 * Shuffle is a toggle like the rest of the app's buttons: blue while a shuffle
 * is on, and pressing it again stops the shuffle. Not on, it opens the panel:
 * "Up to where I am" (page 1 to the furthest page you have reached) or any
 * range typed as two page numbers - "21 or below" is 1 to 21.
 */
function ShufflePanel({
  pages,
  reached,
  active,
  open,
  rangeText,
  setRangeText,
  onToggle,
  onStart,
}: {
  pages: WorkbookPage[];
  reached: number;
  active: Shuffle | null;
  open: boolean;
  rangeText: { from: string; to: string };
  setRangeText: (r: { from: string; to: string }) => void;
  onToggle: () => void;
  onStart: (r: Range) => void;
}) {
  const first = bounds(pages).from;
  const typed = cleanRange({ from: Number(rangeText.from), to: Number(rangeText.to) }, pages);
  const typedOk = rangeText.from.trim() !== "" && rangeText.to.trim() !== "";
  const count = typedOk ? poolFor(pages, typed).length : 0;
  const upTo = { from: first, to: reached };
  const go = () => {
    if (typedOk && count > 0) onStart(typed);
  };
  return (
    <div className="wb-shuffle">
      <button
        type="button"
        className={active || open ? "ws-btn on" : "ws-btn"}
        aria-pressed={!!active}
        aria-expanded={open}
        onClick={onToggle}
        title={active ? "Stop the shuffle and go back to your page" : "Random exercises from a range of pages"}
      >
        {active ? "Shuffle on" : "Shuffle"}
      </button>
      {open && !active ? (
        <div className="wb-shuffle-panel" data-testid="wb-shuffle-panel">
          <p className="wb-shuffle-blurb">Random exercises from the pages you choose, one at a time, never the same one twice until they have all come up.</p>
          <button type="button" className="ws-btn primary" onClick={() => onStart(upTo)}>
            Up to where I am ({rangeLabel(upTo)})
          </button>
          <div className="wb-shuffle-range">
            <label>
              Pages{" "}
              <input
                type="number"
                inputMode="numeric"
                aria-label="First page"
                value={rangeText.from}
                onChange={(e) => setRangeText({ ...rangeText, from: e.target.value })}
                onKeyDown={(e) => e.key === "Enter" && go()}
              />
            </label>
            <label>
              to{" "}
              <input
                type="number"
                inputMode="numeric"
                aria-label="Last page"
                value={rangeText.to}
                onChange={(e) => setRangeText({ ...rangeText, to: e.target.value })}
                onKeyDown={(e) => e.key === "Enter" && go()}
              />
            </label>
            <button type="button" className="ws-btn" onClick={go} disabled={!typedOk || count === 0}>
              Start
            </button>
          </div>
          <p className="wb-shuffle-count">
            {typedOk
              ? count > 0
                ? `${rangeLabel(typed)}: ${count} exercises`
                : "No exercises on those pages."
              : "Type the first and last page."}
          </p>
        </div>
      ) : null}
    </div>
  );
}
