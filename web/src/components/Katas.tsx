/**
 * Katas: write a function, and it gets called with inputs you did not choose.
 *
 * The Workbook asks a program to print something and compares what came out.
 * That is the right check for a drill, and it trains one thing only, because
 * the program is only ever run on the single input the prompt named. Here the
 * function is called ten times with inputs you never see until afterwards,
 * which is the arrangement that makes an empty list or a negative number
 * something you meet rather than something you are told about.
 *
 * Three decisions worth writing down.
 *
 * The cases are hidden until you run. Showing them turns the exercise into a
 * lookup table, and the count is on screen so you know how many there are
 * without knowing what they are.
 *
 * A failure leads with the input. "Seven of ten" is a score; `count_vowels
 * ("Apple") gave 1, wanted 2` is the next thing to do. The failing cases sort
 * to the top for the same reason.
 *
 * Code that did not run at all is shown differently from code that ran and
 * was wrong. A syntax error and a logic error are different problems, and a
 * red "0 of 10" in front of someone with a missing colon sends them reading
 * their algorithm.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { checkKata, explainCode, fetchKataAnswer, fetchKatas } from "../api";
import { VizPanel } from "./VizPanel";
import type {
  ExplainResult,
  KataCheck,
  KataList,
  KataSummary,
} from "../types";
import { LAST_KEYS } from "../lastKeys";

/** How wide one press of Tab is. */
const INDENT = "    ";

/** What is in the box, per kata, so leaving and coming back keeps it. */
const DRAFT_KEY = "code-coach:kata-drafts";

/** Which kata you were on. */
const LAST_KEY = LAST_KEYS.forms;

/** Which language you were filtering to. */
const LANG_KEY = "code-coach:kata-language";

const LANGUAGE_NAMES: Record<string, string> = {
  python: "Python",
  javascript: "JavaScript",
  dart: "Dart",
};

function readDrafts(): Record<string, string> {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    return raw ? (JSON.parse(raw) as Record<string, string>) : {};
  } catch {
    return {};
  }
}

function writeDrafts(drafts: Record<string, string>): void {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(drafts));
  } catch {
    /* a full or blocked store is not worth interrupting practice for */
  }
}

/**
 * A value as Python would write it, which is the language these are in.
 *
 * JSON.stringify is close and wrong in the three places that matter here:
 * booleans are lower case, None is null, and a string comes back in double
 * quotes where Python's repr prefers single. Reading `want: true` in a Python
 * exercise is a small thing that makes you doubt the whole panel.
 */
function asPython(value: unknown): string {
  if (value === null || value === undefined) return "None";
  if (typeof value === "boolean") return value ? "True" : "False";
  if (typeof value === "string") {
    return value.includes("'") ? JSON.stringify(value) : `'${value}'`;
  }
  if (Array.isArray(value)) {
    return `[${value.map(asPython).join(", ")}]`;
  }
  if (typeof value === "object") {
    const pairs = Object.entries(value as Record<string, unknown>).map(
      ([k, v]) => `${asPython(k)}: ${asPython(v)}`,
    );
    return `{${pairs.join(", ")}}`;
  }
  return String(value);
}

/**
 * A value as the kata's own language writes it.
 *
 * Python gets its repr. JavaScript and Dart both spell true, false and
 * null in lower case; Dart writes strings in single quotes by habit and
 * JavaScript in double, which is what JSON gives.
 */
function asValue(value: unknown, language: string): string {
  if (language === "python") return asPython(value);
  if (value === null || value === undefined) return "null";
  if (typeof value === "string") {
    if (language === "dart" && !value.includes("'")) return `'${value}'`;
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((v) => asValue(v, language)).join(", ")}]`;
  }
  if (typeof value === "object") {
    const pairs = Object.entries(value as Record<string, unknown>).map(
      ([k, v]) => `${asValue(k, language)}: ${asValue(v, language)}`,
    );
    return `{${pairs.join(", ")}}`;
  }
  return String(value);
}

/** `count_vowels('Apple')` — the call that failed, as you would type it. */
function asCall(name: string, args: unknown[], language = "python"): string {
  return `${name}(${args.map((a) => asValue(a, language)).join(", ")})`;
}

/**
 * Which to offer next: fewest goes, and of those the longest ago.
 *
 * The count alone cannot separate two things done twice, and the one
 * from last week is worth more than the one from this morning. Never
 * done sorts first because its date is empty, which is before every
 * real one.
 */
function nextUp<T extends { done: number; last: string }>(
  all: T[],
): T | null {
  if (!all.length) return null;
  return all.reduce((best, item) => {
    if (item.done !== best.done) return item.done < best.done ? item : best;
    return item.last < best.last ? item : best;
  }, all[0]);
}

export default function Katas() {
  const [list, setList] = useState<KataList | null>(null);
  const [chosen, setChosen] = useState<string>("");
  const [code, setCode] = useState("");
  const [result, setResult] = useState<KataCheck | null>(null);
  const [running, setRunning] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [answer, setAnswer] = useState("");
  const [walkthrough, setWalkthrough] = useState<ExplainResult | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [watching, setWatching] = useState(false);
  const [error, setError] = useState("");
  // Which language is on show. Remembered, because it is a decision
  // about what you are learning this month rather than this minute.
  const [only, setOnly] = useState<string>(() => {
    try {
      return localStorage.getItem(LANG_KEY) ?? "";
    } catch {
      return "";
    }
  });
  const box = useRef<HTMLTextAreaElement | null>(null);
  const drafts = useRef<Record<string, string>>(readDrafts());

  useEffect(() => {
    let alive = true;
    fetchKatas()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families.flatMap((f) => f.katas);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          last = "";
        }
        const start = all.find((k) => k.id === last) ?? all[0];
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) => {
        if (alive) setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      alive = false;
    };
  }, []);

  /** The families on show, which is all of them until you narrow it. */
  const shown = useMemo(() => {
    if (!list) return [];
    if (!only) return list.families;
    return list.families.filter((f) => f.language === only);
  }, [list, only]);

  /** The language of the kata on screen, for writing values in it. */
  const kataLanguage = useMemo(
    () =>
      list?.families.find((f) => f.katas.some((k) => k.id === chosen))
        ?.language ?? "python",
    [list, chosen],
  );
  const show = (value: unknown) => asValue(value, kataLanguage);

  const kata: KataSummary | null = useMemo(() => {
    if (!list) return null;
    for (const family of list.families) {
      const found = family.katas.find((k) => k.id === chosen);
      if (found) return found;
    }
    return null;
  }, [list, chosen]);

  // Held in a ref so the effect below can read the current one while
  // depending only on which one it is. Updating the pass count rebuilds
  // every object in the list, and an effect keyed on the object itself
  // then fires and clears the result — so passing a kata wiped the panel
  // that had just said it passed.
  const latest = useRef<KataSummary | null>(null);
  latest.current = kata;

  // Moving to a kata brings back what you had typed for it, or starts you
  // on the signature — an empty box and a name to get exactly right is a
  // worse first second than the line already being there.
  useEffect(() => {
    const kata = latest.current;
    if (!kata) return;
    const saved = drafts.current[kata.id];
    // A broken exercise opens on the broken code; a kata opens on its
    // signature. Either way what you last typed wins, so coming back to
    // one you were halfway through does not throw it away.
    // `||` and not `??` for the second choice: `start` is an empty
    // string for a kata you write yourself, and `??` only falls through
    // on null, so `??` here opened every kata on an empty box instead of
    // its signature.
    setCode(saved ?? (kata.start || `${kata.signature}\n${INDENT}`));
    setResult(null);
    setShowHint(false);
    setAnswer("");
    setWalkthrough(null);
    setWatching(false);
    try {
      localStorage.setItem(LAST_KEY, kata.id);
    } catch {
      /* not worth interrupting practice for */
    }
  }, [chosen]);

  const onCode = useCallback(
    (next: string) => {
      setCode(next);
      // The walkthrough was about the code as it was a moment ago.
      setWalkthrough(null);
      if (kata) {
        drafts.current = { ...drafts.current, [kata.id]: next };
        writeDrafts(drafts.current);
      }
    },
    [kata],
  );

  const run = useCallback(async () => {
    if (!kata || running) return;
    setRunning(true);
    setError("");
    try {
      const got = await checkKata({ kata_id: kata.id, code });
      setResult(got);
      if (got.passed) {
        // The count in the sidebar is the thing that says "again"; it
        // has to move the moment it changes, not on the next reload.
        setList((was) =>
          was
            ? {
                // Spread rather than rebuilt: listing the fields here
                // means every new one has to be remembered in a second
                // place, and the first one added was forgotten.
                ...was,
                families: was.families.map((f) => ({
                  ...f,
                  katas: f.katas.map((k) =>
                    k.id === kata.id
                      ? // The date too, or the picker keeps offering the
                        // one just finished: its count went up but its
                        // last-done was still whatever the page loaded
                        // with.
                        {
                          ...k,
                          done: got.done,
                          last: new Date().toISOString(),
                        }
                      : k,
                  ),
                })),
              }
            : was,
        );
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }, [kata, code, running]);

  // Fetched rather than shipped with the list: looking is a decision,
  // and an answer already sitting in the page is one you did not make.
  const reveal = useCallback(async () => {
    if (!kata) return;
    if (answer) {
      setAnswer("");
      return;
    }
    try {
      const got = await fetchKataAnswer(kata.id);
      setAnswer(got.answer);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [kata, answer]);

  /**
   * Narrow to one language, and move onto something in it.
   *
   * Without the move you stay on the kata you were already on, which
   * has just been filtered out of the list beside it — so the screen
   * shows a Python kata under a heading that says JavaScript, and
   * nothing on the left is highlighted.
   */
  const pickLanguage = useCallback(
    (id: string) => {
      setOnly(id);
      try {
        localStorage.setItem(LANG_KEY, id);
      } catch {
        /* not worth interrupting practice for */
      }
      if (!id || !list) return;
      const here = list.families.find((f) =>
        f.katas.some((k) => k.id === chosen),
      );
      if (here?.language === id) return;
      const first = list.families.find((f) => f.language === id)?.katas[0];
      if (first) setChosen(first.id);
    },
    [list, chosen],
  );

  const onKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        void run();
        return;
      }
      if (event.key !== "Tab") return;
      // Always indent. Python is the one language where the whitespace is
      // the syntax, so a Tab that moved focus would be the wrong trade.
      event.preventDefault();
      const area = event.currentTarget;
      const { selectionStart: from, selectionEnd: to } = area;
      const next = `${code.slice(0, from)}${INDENT}${code.slice(to)}`;
      onCode(next);
      requestAnimationFrame(() => {
        area.selectionStart = area.selectionEnd = from + INDENT.length;
      });
    },
    [code, onCode, run],
  );

  /**
   * The code to step through: what you wrote, plus a call to it.
   *
   * A kata is a function definition and nothing else, so tracing it as
   * written shows the `def` line being reached and then the program
   * ending. There has to be a call, and the interesting call is the one
   * that just failed — watching the input that broke it is the entire
   * reason to open the tracer here rather than reading the code again.
   *
   * Which is why this needs a run first: the cases are hidden until you
   * run, so before that there is no input to call it with.
   */
  const traced = useMemo(() => {
    if (!kata || !result || result.broke) return "";
    const failing = result.results.find((r) => !r.passed);
    const pick = failing ?? result.results[0];
    if (!pick) return "";
    return `${code.trimEnd()}

print(${asCall(kata.name, pick.args)})
`;
  }, [code, kata, result]);

  /**
   * The one with the fewest goes at it, ties going to the first.
   *
   * This is what the counts are for. Choosing by hand from forty-four
   * means picking whichever name catches your eye, which is how the
   * same six get practised and the rest go untouched; the least
   * practised is a decision the list can make for you.
   */
  const leastDone = useMemo(
    () => nextUp(shown.flatMap((f) => f.katas)),
    [shown],
  );

  // Failures first. A panel that opens on four passes and buries the one
  // that matters is a panel you have to read rather than glance at.
  const ordered = useMemo(() => {
    if (!result) return [];
    return [...result.results].sort(
      (a, b) => Number(a.passed) - Number(b.passed),
    );
  }, [result]);

  if (error && !list) {
    return <div className="lessons-empty">Could not load the forms: {error}</div>;
  }
  if (!list || !kata) return <div className="lessons-empty">Loading…</div>;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Forms</h2>
        <p className="lessons-intro">
          Write the function. It is called with inputs you have not seen —
          which is where the empty list and the negative number live. A
          form is a sequence you walk through until it is in the body,
          so the count beside each one is goes, not ticks.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button
            type="button"
            className="ws-btn kata-next"
            onClick={() => setChosen(leastDone.id)}
            title={
              leastDone.done
                ? `${leastDone.name} — ${leastDone.done} so far, and the `
                  + `longest ago of those`
                : `${leastDone.name} — not tried yet`
            }
          >
            Next up: {leastDone.name}
          </button>
        ) : null}
        {list.languages.length > 1 ? (
          <div className="kata-langs">
            <button
              type="button"
              className={`ws-btn${only ? "" : " on"}`}
              onClick={() => pickLanguage("")}
            >
              All
            </button>
            {list.languages.map((id) => (
              <button
                key={id}
                type="button"
                className={`ws-btn${only === id ? " on" : ""}`}
                onClick={() => pickLanguage(id)}
              >
                {LANGUAGE_NAMES[id] ?? id}
              </button>
            ))}
          </div>
        ) : null}
        {shown.map((family) => (
          <div key={family.name} className="wb-section">
            <h4 className="wb-section-head">
              {family.name}
              <span className="wb-section-count">
                {family.katas.length} katas
              </span>
            </h4>
            {family.katas.map((k) => (
              <button
                key={k.id}
                type="button"
                className={`lessons-pick${k.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(k.id)}
              >
                <span className="lessons-pick-name">{k.name}</span>
                <span className="lessons-pick-blurb">
                  {k.done ? `done ${k.done}×` : `${k.cases} cases`}
                </span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {kata.name}
            <span className="kata-level" title={`Level ${kata.level} of 5`}>
              {"●".repeat(kata.level)}
              <span className="kata-level-rest">
                {"●".repeat(5 - kata.level)}
              </span>
            </span>
          </h3>
          {/* A change request means nothing without the thing being
              changed, so a Change it drill says what the code does
              today before it says what to do. */}
          {kata.was ? (
            <p className="kata-was">
              <strong>What it does now:</strong> {kata.was}
            </p>
          ) : null}
          <p className="lessons-blurb">{kata.brief}</p>
          {kata.example ? (
            <p className="wb-example">{kata.example}</p>
          ) : null}
        </header>

        <p className="wb-prompt kata-signature">{kata.signature}</p>

        <textarea
          ref={box}
          className={
            "wb-code" +
            (result && !result.broke
              ? result.passed
                ? " ok"
                : " bad"
              : "")
          }
          value={code}
          spellCheck={false}
          aria-label="Your function"
          onChange={(e) => onCode(e.target.value)}
          onKeyDown={onKeyDown}
        />

        <div className="wb-actions">
          <button
            type="button"
            className="ws-btn primary"
            onClick={() => void run()}
            disabled={running}
          >
            {running ? "Running…" : "Run the cases"}
          </button>
          <span className="wb-chord">Ctrl+Enter</span>
          <button
            type="button"
            className="ws-btn"
            onClick={() =>
              onCode(kata.start || `${kata.signature}\n${INDENT}`)
            }
          >
            {kata.start ? "Start over" : "Clear"}
          </button>
          <button
            type="button"
            className="ws-btn"
            onClick={() => setShowHint((on) => !on)}
          >
            {showHint ? "Hide hint" : "Hint"}
          </button>
          <button type="button" className="ws-btn" onClick={() => void reveal()}>
            {answer ? "Hide answer" : "Show answer"}
          </button>
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
            title="Say what each line does"
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
            // Needs a run first: the cases are hidden until then, so
            // there is no input to call the function with.
            disabled={!traced}
            title={
              traced
                ? "Step through it on the case that failed"
                : "Run the cases first — then this steps through the one that failed"
            }
          >
            {watching ? "Hide run" : "Watch it run"}
          </button>
          {answer ? (
            <button
              type="button"
              className="ws-btn"
              title="Put it in the box, so you can run it and then retype it"
              onClick={() => onCode(answer)}
            >
              Copy into the box
            </button>
          ) : null}
        </div>

        {showHint ? <p className="wb-answer">{kata.hint}</p> : null}

        {watching && traced ? (
          <div className="wb-viz">
            {/* What is stepped through is your function plus one call to
                it, so the panel says which call — otherwise the values
                appearing in it have come from nowhere. */}
            <p className="wb-walkthrough-note">
              Running{" "}
              <code>
                {asCall(
                  kata.name,
                  (result?.results.find((r) => !r.passed) ??
                    result?.results[0])?.args ?? [],
                )}
              </code>
            </p>
            <VizPanel
              getCode={() => traced}
              patternId={null}
              problemNumber={null}
              resetKey={`${kata.id}:${traced.length}`}
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
          </div>
        ) : null}
        {answer ? (
          /* One worked answer, not the only one. Several of these have
             a neater version and a plainer one, and the plainer one is
             what is kept — reading a clever line you would not have
             written teaches less than reading the obvious one. */
          <div className="kata-answer">
            <p className="wb-walkthrough-note">One way to write it:</p>
            <pre className="wb-stderr">{answer}</pre>
          </div>
        ) : null}
        {error ? <p className="wb-verdict bad">{error}</p> : null}

        {result ? (
          result.broke ? (
            <div className="kata-result">
              {/* Not a score. Nothing ran, so none of the cases has
                  anything to say and pretending otherwise would point
                  at the wrong thing. */}
              <p className="wb-verdict bad">This did not run:</p>
              <pre className="wb-stderr">{result.broke}</pre>
            </div>
          ) : (
            <div className="kata-result">
              <p className={result.passed ? "wb-verdict ok" : "wb-verdict bad"}>
                {result.passed
                  ? `All ${result.total} cases pass.`
                  : `${result.count} of ${result.total} cases pass.`}
              </p>
              <ul className="kata-cases">
                {ordered.map((c, i) => (
                  <li
                    key={i}
                    className={`kata-case${c.passed ? " ok" : " bad"}`}
                  >
                    <code className="mono">
                      {asCall(kata.name, c.args, kataLanguage)}
                    </code>
                    {c.passed ? (
                      <span className="kata-case-got">
                        → {show(c.want)}
                      </span>
                    ) : c.error ? (
                      <span className="kata-case-got">
                        raised {c.error}
                      </span>
                    ) : (
                      <span className="kata-case-got">
                        {c.changed
                          ? show(c.got) === show(c.want)
                            ? "changed the list it was given — the answer is right, the damage is not"
                            : `changed the list it was given, and gave ${show(c.got)}`
                          : `gave ${show(c.got)}, wanted ${show(c.want)}`}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
              {/* Only arrives once every case passes: naming your own
                  mistake after finding it is what makes it the last
                  time, and naming it beforehand is giving the answer. */}
              {result.bug ? (
                <p className="kata-bug">
                  <strong>What it was:</strong> {result.bug}
                </p>
              ) : null}
              {/* The same idea for a change: why it had to be made that
                  way, once you have made it. */}
              {result.change ? (
                <p className="kata-bug">
                  <strong>The change:</strong> {result.change}
                </p>
              ) : null}
              {result.stdout.trim() ? (
                <>
                  <p className="wb-walkthrough-note">What your code printed:</p>
                  <pre className="wb-stderr">{result.stdout}</pre>
                </>
              ) : null}
            </div>
          )
        ) : null}
      </article>
    </div>
  );
}
