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

import { checkKata, fetchKatas } from "../api";
import type { KataCheck, KataList, KataSummary } from "../types";

/** How wide one press of Tab is. */
const INDENT = "    ";

/** What is in the box, per kata, so leaving and coming back keeps it. */
const DRAFT_KEY = "code-coach:kata-drafts";

/** Which kata you were on. */
const LAST_KEY = "code-coach:kata-last";

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

/** `count_vowels('Apple')` — the call that failed, as you would type it. */
function asCall(name: string, args: unknown[]): string {
  return `${name}(${args.map(asPython).join(", ")})`;
}

export default function Katas() {
  const [list, setList] = useState<KataList | null>(null);
  const [chosen, setChosen] = useState<string>("");
  const [code, setCode] = useState("");
  const [result, setResult] = useState<KataCheck | null>(null);
  const [running, setRunning] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [error, setError] = useState("");
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

  const kata: KataSummary | null = useMemo(() => {
    if (!list) return null;
    for (const family of list.families) {
      const found = family.katas.find((k) => k.id === chosen);
      if (found) return found;
    }
    return null;
  }, [list, chosen]);

  // Moving to a kata brings back what you had typed for it, or starts you
  // on the signature — an empty box and a name to get exactly right is a
  // worse first second than the line already being there.
  useEffect(() => {
    if (!kata) return;
    const saved = drafts.current[kata.id];
    setCode(saved ?? `${kata.signature}\n${INDENT}`);
    setResult(null);
    setShowHint(false);
    try {
      localStorage.setItem(LAST_KEY, kata.id);
    } catch {
      /* not worth interrupting practice for */
    }
  }, [kata]);

  const onCode = useCallback(
    (next: string) => {
      setCode(next);
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
      setResult(await checkKata({ kata_id: kata.id, code }));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }, [kata, code, running]);

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

  // Failures first. A panel that opens on four passes and buries the one
  // that matters is a panel you have to read rather than glance at.
  const ordered = useMemo(() => {
    if (!result) return [];
    return [...result.results].sort(
      (a, b) => Number(a.passed) - Number(b.passed),
    );
  }, [result]);

  if (error && !list) {
    return <div className="lessons-empty">Could not load the katas: {error}</div>;
  }
  if (!list || !kata) return <div className="lessons-empty">Loading…</div>;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Katas</h2>
        <p className="lessons-intro">
          Write the function. It is called with inputs you have not seen —
          which is where the empty list and the negative number live.
        </p>
        {list.families.map((family) => (
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
                <span className="lessons-pick-blurb">{k.cases} cases</span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>{kata.name}</h3>
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
            onClick={() => onCode(`${kata.signature}\n${INDENT}`)}
          >
            Clear
          </button>
          <button
            type="button"
            className="ws-btn"
            onClick={() => setShowHint((on) => !on)}
          >
            {showHint ? "Hide hint" : "Hint"}
          </button>
        </div>

        {showHint ? <p className="wb-answer">{kata.hint}</p> : null}
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
                    <code className="mono">{asCall(kata.name, c.args)}</code>
                    {c.passed ? (
                      <span className="kata-case-got">
                        → {asPython(c.want)}
                      </span>
                    ) : c.error ? (
                      <span className="kata-case-got">
                        raised {c.error}
                      </span>
                    ) : (
                      <span className="kata-case-got">
                        gave {asPython(c.got)}, wanted {asPython(c.want)}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
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
