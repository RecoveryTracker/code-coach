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

import { checkWorkbook, fetchWorkbook, saveWorkbookDraft } from "../api";
import type { WorkbookCheck, WorkbookData, WorkbookPage } from "../types";

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
];

export default function Workbook({ language }: Props) {
  const [data, setData] = useState<WorkbookData | null>(null);
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

  const page: WorkbookPage | null = useMemo(
    () => data?.pages.find((p) => p.id === pageId) ?? null,
    [data, pageId],
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
  const exercise = page?.exercises[index] ?? null;

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
      if (!page || !exercise) return;
      pending.current = {
        pageId: page.id,
        exerciseId: exercise.id,
        code: text,
      };
      if (draftTimer.current !== null) window.clearTimeout(draftTimer.current);
      draftTimer.current = window.setTimeout(flushDraft, 600);
    },
    [page, exercise, flushDraft],
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
      if (exercise) {
        setMine((was) => ({ ...was, [exercise.id]: text }));
      }
      rememberDraft(text);
    },
    [exercise, rememberDraft],
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
    const kept = exercise ? (mineRef.current[exercise.id] ?? "") : "";
    setCode(kept);
    setRestored(kept !== "");
    setResult(null);
    setRevealed(false);
    box.current?.focus();
  }, [exercise?.id]); // eslint-disable-line react-hooks/exhaustive-deps

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
      });
      setResult(got);
      if (got.passed) {
        setDone((was) => new Set(was).add(exercise.id));
        setMine((was) => ({ ...was, [exercise.id]: code }));
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't run that.");
    } finally {
      setChecking(false);
    }
  }, [checking, code, exercise, language, page]);

  const pageAfter = useMemo(() => {
    if (!data || !page) return null;
    const at = data.pages.findIndex((p) => p.id === page.id);
    return at === -1 ? null : (data.pages[at + 1] ?? null);
  }, [data, page]);

  const atPageEnd = page ? index >= page.exercises.length - 1 : false;

  const move = useCallback(
    (delta: number) => {
      if (!page) return;
      setIndex((i) => Math.min(page.exercises.length - 1, Math.max(0, i + delta)));
    },
    [page],
  );

  /** Forward: the next exercise, or the next page once this one runs out. */
  const onward = useCallback(() => {
    if (atPageEnd) {
      if (pageAfter) setPageId(pageAfter.id);
      return;
    }
    move(1);
  }, [atPageEnd, move, pageAfter]);

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
                  className={`lessons-pick${p.id === pageId ? " on" : ""}`}
                  onClick={() => setPageId(p.id)}
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
          <header>
            <h3>
              {page.number}. {page.name}
            </h3>
            <p className="lessons-blurb">{page.teaches}</p>
            <p className="wb-example">{page.example}</p>
          </header>

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
              className="ws-btn primary"
              onClick={() => void check()}
              disabled={checking || !code.trim()}
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
              disabled={index === 0}
            >
              ‹ Back
            </button>
            <button
              ref={nextButton}
              type="button"
              className={`ws-btn${result?.passed ? " primary" : ""}`}
              onClick={onward}
              disabled={atPageEnd && !pageAfter}
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
                {!atPageEnd
                  ? "Press Enter for the next one."
                  : allDone && pageAfter
                    ? `Page finished — Enter starts ${pageAfter.name}.`
                    : allDone
                      ? "That is the last page finished."
                      : "Last one on the page. Enter moves on."}
              </div>
            ) : (
              <div className="wb-verdict bad">
                {result.failed_to_run ? (
                  <>
                    <strong>It didn't run.</strong>
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
                        <pre>{result.stdout.trim() || "(nothing)"}</pre>
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
