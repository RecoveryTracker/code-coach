/**
 * Type the markup, and watch what you typed render.
 *
 * The quizzes next door ask what the browser makes of a page. This asks you
 * to write the page, and it is the half that puts it in the hands.
 *
 * The render is the reason this works without a marking engine. What goes
 * into the iframe is what you typed, not the reference, and it updates as
 * you type — so a missing quote is not a message about a missing quote, it
 * is the page going wrong in front of you. That is the thing you actually
 * need to recognise later, and no amount of being told teaches it.
 *
 * The check is character for character against the drill, which is the only
 * honest claim available: HTML prints nothing, there is no engine here to
 * ask, and a marker that tried to judge "is this markup correct" would be
 * judging with an opinion. On a mismatch you get the first line that
 * differs rather than a diff of everything, because you are about to type
 * it again and what you want is the one place to look.
 *
 * The code you are copying stays on screen the whole time. Hiding it would
 * make this a memory test, and it is not one — it is a dozen goes at a
 * shape until your hands know it.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkDrill, fetchDrills } from "../api";
import type { MarkupCheck, MarkupDrill, MarkupList } from "../types";

/** What you had typed, per drill, so leaving and coming back keeps it. */
const DRAFT_KEY = "code-coach:drill-drafts";

/** Which drill you were on. */
const LAST_KEY = "code-coach:drill-last";

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
    /* a blocked store is not worth interrupting practice for */
  }
}

/**
 * Which to offer next: fewest goes, and of those the longest ago.
 *
 * Same rule as every other mode here. It matters more in this one: the
 * whole premise is that you come back to the same shape a dozen times,
 * so what you need offered is the one that has gone coldest.
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

/** The whole page for the iframe, built from what is in the box. */
function documentFor(drill: MarkupDrill, typed: string): string {
  if (!drill.wrapper) return typed;
  return drill.wrapper.replace("{{drill}}", typed);
}

export default function Drills() {
  const [list, setList] = useState<MarkupList | null>(null);
  const [chosen, setChosen] = useState("");
  const [typed, setTyped] = useState("");
  const [result, setResult] = useState<MarkupCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [peeking, setPeeking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchDrills()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const all = data.families.flatMap((f) => f.drills);
        let last = "";
        try {
          last = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* same */
        }
        const start = all.find((d) => d.id === last) ?? nextUp(all);
        if (start) setChosen(start.id);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
    return () => {
      alive = false;
    };
  }, []);

  const drill = useMemo(
    () =>
      list?.families.flatMap((f) => f.drills).find((d) => d.id === chosen) ??
      null,
    [list, chosen],
  );

  /* Keyed on the id, not the drill object: the list is rebuilt after a
     pass, which changes the object's identity, and an effect watching
     the object would fire and wipe what it just set. */
  useEffect(() => {
    if (!chosen) return;
    setResult(null);
    setPeeking(false);
    setTyped(readDrafts()[chosen] ?? "");
    try {
      localStorage.setItem(LAST_KEY, chosen);
    } catch {
      /* same */
    }
  }, [chosen]);

  const onType = useCallback(
    (next: string) => {
      setTyped(next);
      if (!chosen) return;
      const drafts = readDrafts();
      drafts[chosen] = next;
      writeDrafts(drafts);
    },
    [chosen],
  );

  const check = useCallback(async () => {
    if (!drill || checking) return;
    setChecking(true);
    setError("");
    try {
      const got = await checkDrill({ drill_id: drill.id, typed });
      setResult(got);
      if (got.passed) {
        setList((was) =>
          was
            ? {
                ...was,
                families: was.families.map((f) => ({
                  ...f,
                  drills: f.drills.map((d) =>
                    d.id === drill.id
                      ? { ...d, done: got.done, last: new Date().toISOString() }
                      : d,
                  ),
                })),
              }
            : was,
        );
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setChecking(false);
    }
  }, [drill, typed, checking]);

  /** Wipe the box for another go. The whole point is the next go. */
  const again = useCallback(() => {
    setResult(null);
    onType("");
  }, [onType]);

  const leastDone = useMemo(
    () => nextUp(list?.families.flatMap((f) => f.drills) ?? []),
    [list],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !drill) return <div className="lessons-empty">Loading…</div>;

  const page = documentFor(drill, typed);

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Type it</h2>
        <p className="lessons-intro">
          Copy the markup, and watch what you typed render beside it. The
          code stays on screen — this is a dozen goes at a shape until your
          hands know it, not a memory test.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button
            type="button"
            className="ws-btn kata-next"
            onClick={() => setChosen(leastDone.id)}
            title={
              leastDone.done
                ? `${leastDone.name} — typed ${leastDone.done} so far, and `
                  + `the longest ago of those`
                : `${leastDone.name} — not tried yet`
            }
          >
            Next up: {leastDone.name}
          </button>
        ) : null}
        {list.families.map((family) => (
          <div key={family.name} className="wb-section">
            <h4 className="wb-section-head">
              {family.name}
              <span className="wb-section-count">{family.drills.length}</span>
            </h4>
            {family.drills.map((d) => (
              <button
                key={d.id}
                type="button"
                className={`lessons-pick${d.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(d.id)}
              >
                <span className="lessons-pick-name">{d.name}</span>
                {d.done ? (
                  <span className="lessons-pick-blurb">
                    typed {d.done}&#215;
                  </span>
                ) : null}
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {drill.name}
            <span className="predict-lang">{drill.lines} lines</span>
          </h3>
        </header>

        <p className="lessons-blurb">{drill.note}</p>

        <p className="wb-walkthrough-note">Type this</p>
        <pre className="predict-code drill-reference">{drill.code}</pre>

        {drill.wrapper ? (
          <details className="drill-wrapper">
            <summary>What it sits inside</summary>
            {/* Visible rather than assumed. You are practising the piece,
                but you should be able to see the page it lands in. */}
            <pre className="predict-code drill-wrapper-code">
              {drill.wrapper.replace("{{drill}}", "        …your lines…")}
            </pre>
          </details>
        ) : null}

        <div className="drill-work">
          <div className="drill-typing">
            <p className="wb-prompt">Your turn</p>
            <textarea
              className={
                "wb-code drill-box"
                + (result ? (result.passed ? " ok" : " bad") : "")
              }
              value={typed}
              spellCheck={false}
              autoCapitalize="off"
              autoCorrect="off"
              autoComplete="off"
              aria-label="Type the markup here"
              placeholder="Type it here…"
              onChange={(e) => {
                onType(e.target.value);
                // A verdict next to changed text says something untrue.
                if (result && !result.passed) setResult(null);
              }}
              onKeyDown={(e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                  e.preventDefault();
                  void check();
                }
                if (e.key === "Tab") {
                  // Indentation is part of what is being practised, and
                  // Tab moving focus out of the box makes it unpractisable.
                  e.preventDefault();
                  const el = e.currentTarget;
                  const at = el.selectionStart;
                  const next =
                    typed.slice(0, at) + "  " + typed.slice(el.selectionEnd);
                  onType(next);
                  requestAnimationFrame(() => {
                    el.selectionStart = el.selectionEnd = at + 2;
                  });
                }
              }}
            />
          </div>

          <div className="drill-preview">
            <p className="wb-prompt">
              What you typed
              {peeking ? ", and what it should look like" : ""}
            </p>
            {/* sandbox="" — no scripts, no forms going anywhere. These
                are documents a person is typing, rendered instantly; it
                should not be possible to type something that runs. */}
            <iframe
              className="drill-frame"
              title="What you typed, rendered"
              sandbox=""
              srcDoc={page}
            />
            {peeking ? (
              <iframe
                className="drill-frame drill-frame-target"
                title="What it should look like"
                sandbox=""
                srcDoc={documentFor(drill, drill.code)}
              />
            ) : null}
          </div>
        </div>

        <div className="wb-actions">
          <button
            type="button"
            className="ws-btn primary"
            onClick={() => void check()}
            disabled={checking || !typed.trim()}
          >
            {checking ? "Checking…" : "Check"}
          </button>
          <span className="wb-chord">Ctrl+Enter</span>
          <button
            type="button"
            className="ws-btn"
            onClick={again}
            title="Clear the box and go again — the next go is the point"
          >
            Again
          </button>
          <button
            type="button"
            className={peeking ? "ws-btn on" : "ws-btn"}
            onClick={() => setPeeking((open) => !open)}
            title="Show the finished version rendered, to compare against"
          >
            {peeking ? "Hide the target" : "Show the target"}
          </button>
        </div>

        {error ? <p className="wb-verdict bad">{error}</p> : null}

        {result ? (
          <div className="kata-result">
            <p className={result.passed ? "wb-verdict ok" : "wb-verdict bad"}>
              {result.passed
                ? `That is it, character for character. Typed ${result.done}×.`
                : `Line ${result.first_wrong_line} is not the same yet.`}
            </p>
            {!result.passed ? (
              <div className="predict-compare">
                <div>
                  <p className="wb-walkthrough-note">It should be</p>
                  <pre className="wb-stderr">
                    {result.want_line || "(nothing — you have a line too many)"}
                  </pre>
                </div>
                <div>
                  <p className="wb-walkthrough-note">You typed</p>
                  <pre className="wb-stderr">
                    {result.typed_line || "(nothing — a line is missing)"}
                  </pre>
                </div>
              </div>
            ) : null}
          </div>
        ) : null}
      </article>
    </div>
  );
}
