/**
 * Code magnets: the lines of a working program, shuffled.
 *
 * The forms ask you to write a function from nothing. The typing drills ask
 * you to copy a shape until your hands know it. This asks the thing in
 * between, which is oddly harder: here are the exact lines of a program that
 * works, in the wrong order — put them back.
 *
 * Built in labelled stages rather than one list
 * ---------------------------------------------
 * The program area is divided into the stages the program goes through —
 * "define the function", "call it and show the answer" — and each line goes
 * under the stage it belongs to.
 *
 * Those are subgoal labels, and they are the one part of this app with
 * direct research behind them. Students given subgoal labels on a Parsons
 * problem do measurably better than students asked to invent their own or
 * given none: better immediately, better a week later, and better on a task
 * they have not seen. So the labels are given rather than asked for.
 *
 * What is not given is how many lines a stage holds. The server sends the
 * labels and keeps the counts, because "this one takes three lines" answers
 * a good part of the puzzle. A stage takes as many as you put in it.
 *
 * Placing rather than dragging. Drag and drop is the obvious interface and
 * the wrong one here: it needs a mouse and it needs aim, so getting a line
 * into position becomes a test of the pointer rather than of whether you
 * know where the line goes. Clicking a stage selects it, clicking a magnet
 * drops it there, and the arrows move it within the stage — all of which
 * work from the keyboard, which matters in an app about typing.
 *
 * Marked by running it, not by comparing your order with the reference.
 * There is always more than one arrangement that works — a function
 * declaration is hoisted, two independent statements can go either way round
 * — and marking those wrong would teach you to guess at the author's
 * preference rather than at what the language does.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkMagnet, fetchMagnets } from "../api";
import { LAST_KEYS } from "../lastKeys";
import type { MagnetCheck, MagnetList, MagnetPuzzle } from "../types";

/** Which puzzle you were on. */
const LAST_KEY = LAST_KEYS.magnets;

/**
 * Which to offer next: fewest goes, and of those the longest ago.
 * Same rule as every other mode here, for the same reason.
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

/** A magnet, wherever it currently sits. The key keeps duplicates apart. */
type Piece = { key: number; text: string };

/** One stage of the program: its label, and what has been put under it. */
type Bin = { label: string; pieces: Piece[] };

export default function Magnets() {
  const [list, setList] = useState<MagnetList | null>(null);
  const [chosen, setChosen] = useState("");
  const [tray, setTray] = useState<Piece[]>([]);
  const [bins, setBins] = useState<Bin[]>([]);
  const [active, setActive] = useState(0);
  const [result, setResult] = useState<MagnetCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback((keepOn?: string) => {
    return fetchMagnets().then((data) => {
      setList(data);
      const all = data.families.flatMap((f) => f.magnets);
      let want = keepOn ?? "";
      if (!want) {
        try {
          want = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* a blocked store is not worth interrupting practice for */
        }
      }
      const start = all.find((m) => m.id === want) ?? nextUp(all);
      if (start) setChosen(start.id);
      return data;
    });
  }, []);

  useEffect(() => {
    load().catch((e: unknown) =>
      setError(e instanceof Error ? e.message : String(e)),
    );
  }, [load]);

  const puzzle = useMemo(
    () =>
      list?.families.flatMap((f) => f.magnets).find((m) => m.id === chosen) ??
      null,
    [list, chosen],
  );

  /* Keyed on the id rather than the object: the list is rebuilt after a
     pass, which changes the object's identity, and an effect watching the
     object would fire and clear the board it just set. */
  useEffect(() => {
    if (!puzzle) return;
    setTray(puzzle.pieces.map((text, i) => ({ key: i, text })));
    setBins(puzzle.labels.map((label) => ({ label, pieces: [] })));
    setActive(0);
    setResult(null);
    try {
      localStorage.setItem(LAST_KEY, puzzle.id);
    } catch {
      /* same */
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chosen]);

  const place = (piece: Piece) => {
    setTray((was) => was.filter((p) => p.key !== piece.key));
    setBins((was) =>
      was.map((bin, i) =>
        i === active ? { ...bin, pieces: [...bin.pieces, piece] } : bin,
      ),
    );
    setResult(null);
  };

  const takeBack = (piece: Piece) => {
    setBins((was) =>
      was.map((bin) => ({
        ...bin,
        pieces: bin.pieces.filter((p) => p.key !== piece.key),
      })),
    );
    setTray((was) => [...was, piece]);
    setResult(null);
  };

  const move = (binIndex: number, at: number, by: number) => {
    setBins((was) =>
      was.map((bin, i) => {
        if (i !== binIndex) return bin;
        const to = at + by;
        if (to < 0 || to >= bin.pieces.length) return bin;
        const next = [...bin.pieces];
        [next[at], next[to]] = [next[to], next[at]];
        return { ...bin, pieces: next };
      }),
    );
    setResult(null);
  };

  /** Every line, stages read in order — which is the program. */
  const assembled = useMemo(
    () => bins.flatMap((bin) => bin.pieces.map((p) => p.text)),
    [bins],
  );

  const check = useCallback(async () => {
    if (!puzzle || checking) return;
    setChecking(true);
    setError("");
    try {
      const got = await checkMagnet({
        magnet_id: puzzle.id,
        lines: assembled,
      });
      setResult(got);
      if (got.passed) {
        setList((was) =>
          was
            ? {
                ...was,
                families: was.families.map((f) => ({
                  ...f,
                  magnets: f.magnets.map((m) =>
                    m.id === puzzle.id
                      ? { ...m, done: got.done, last: new Date().toISOString() }
                      : m,
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
  }, [puzzle, assembled, checking]);

  /* Another go means another jumble, which has to come from the server —
     the finished order is not in the payload, and a reshuffle on this side
     could only reorder what it already has. */
  const again = useCallback(() => {
    if (!puzzle) return;
    setResult(null);
    load(puzzle.id).catch((e: unknown) =>
      setError(e instanceof Error ? e.message : String(e)),
    );
  }, [puzzle, load]);

  const leastDone = useMemo(
    () => nextUp(list?.families.flatMap((f) => f.magnets) ?? []),
    [list],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !puzzle) return <div className="lessons-empty">Loading…</div>;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Magnets</h2>
        <p className="lessons-intro">
          The lines of a program that works, in the wrong order. Put them
          back under the stage each one belongs to. It is marked by running
          what you built, so any arrangement that prints the right thing is
          right.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button
            type="button"
            className="ws-btn kata-next"
            onClick={() => setChosen(leastDone.id)}
            title={
              leastDone.done
                ? `${leastDone.name} — done ${leastDone.done} so far, and `
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
              <span className="wb-section-count">{family.magnets.length}</span>
            </h4>
            {family.magnets.map((m: MagnetPuzzle) => (
              <button
                key={m.id}
                type="button"
                className={`lessons-pick${m.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(m.id)}
              >
                <span className="lessons-pick-name">{m.name}</span>
                {m.done ? (
                  <span className="lessons-pick-blurb">done {m.done}&#215;</span>
                ) : null}
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {puzzle.name}
            <span className="predict-lang">
              {puzzle.language === "javascript" ? "JavaScript" : "Python"}
            </span>
          </h3>
        </header>

        <p className="lessons-blurb">{puzzle.note}</p>

        <div className="magnet-board">
          <div className="magnet-side">
            <p className="wb-prompt">
              Loose magnets
              {tray.length ? ` (${tray.length})` : " — all placed"}
            </p>
            <div className="magnet-tray">
              {tray.map((piece) => (
                <button
                  key={piece.key}
                  type="button"
                  className="magnet"
                  onClick={() => place(piece)}
                  title={
                    bins.length
                      ? `Put this under "${bins[active]?.label}"`
                      : "Place this line"
                  }
                >
                  <code>{piece.text}</code>
                </button>
              ))}
              {!tray.length ? (
                <p className="magnet-empty">
                  Every piece is placed. Check it, or move lines around.
                </p>
              ) : null}
            </div>
          </div>

          <div className="magnet-side">
            <p className="wb-prompt">Your program, stage by stage</p>
            {bins.map((bin, binIndex) => (
              <section
                key={bin.label}
                className={`magnet-stage${binIndex === active ? " on" : ""}`}
              >
                <button
                  type="button"
                  className="magnet-stage-head"
                  onClick={() => setActive(binIndex)}
                  aria-pressed={binIndex === active}
                  title="Put the next magnet here"
                >
                  <span className="magnet-stage-name">{bin.label}</span>
                  {binIndex === active ? (
                    <span className="magnet-stage-note">next goes here</span>
                  ) : null}
                </button>
                <ol className="magnet-program">
                  {bin.pieces.map((piece, i) => (
                    <li key={piece.key}>
                      <code className="magnet-line">{piece.text}</code>
                      <span className="magnet-controls">
                        <button
                          type="button"
                          className="ws-btn magnet-move"
                          onClick={() => move(binIndex, i, -1)}
                          disabled={i === 0}
                          title="Move up"
                          aria-label={`Move ${piece.text} up`}
                        >
                          ↑
                        </button>
                        <button
                          type="button"
                          className="ws-btn magnet-move"
                          onClick={() => move(binIndex, i, 1)}
                          disabled={i === bin.pieces.length - 1}
                          title="Move down"
                          aria-label={`Move ${piece.text} down`}
                        >
                          ↓
                        </button>
                        <button
                          type="button"
                          className="ws-btn magnet-move"
                          onClick={() => takeBack(piece)}
                          title="Take it back"
                          aria-label={`Remove ${piece.text}`}
                        >
                          ×
                        </button>
                      </span>
                    </li>
                  ))}
                  {!bin.pieces.length ? (
                    <li className="magnet-empty">
                      {binIndex === active
                        ? "Click a magnet to put it here."
                        : "Nothing here yet."}
                    </li>
                  ) : null}
                </ol>
              </section>
            ))}
          </div>
        </div>

        <div className="wb-actions">
          <button
            type="button"
            className="ws-btn primary"
            onClick={() => void check()}
            disabled={checking || tray.length > 0 || !assembled.length}
            title={
              tray.length
                ? "Every magnet has to be placed first"
                : "Run it and see what it prints"
            }
          >
            {checking ? "Running…" : "Check"}
          </button>
          <button
            type="button"
            className="ws-btn"
            onClick={again}
            title="Jumble them again and go once more — the next go is the point"
          >
            Again
          </button>
        </div>

        {error ? <p className="wb-verdict bad">{error}</p> : null}

        {result ? (
          <div className="kata-result">
            <p className={result.passed ? "wb-verdict ok" : "wb-verdict bad"}>
              {result.passed
                ? `That runs and prints exactly that. Done ${result.done}×.`
                : result.broke
                  ? result.broke
                  : "It ran, and printed something else."}
            </p>
            {!result.passed && !result.broke ? (
              <div className="predict-compare">
                <div>
                  <p className="wb-walkthrough-note">Yours printed</p>
                  <pre className="wb-stderr">
                    {result.printed || "(nothing)"}
                  </pre>
                </div>
                <div>
                  <p className="wb-walkthrough-note">It should print</p>
                  <pre className="wb-stderr">{result.expect}</pre>
                </div>
              </div>
            ) : null}
            {result.passed && result.why ? (
              <p className="kata-bug">
                <strong>Why that order:</strong> {result.why}
              </p>
            ) : null}
          </div>
        ) : null}
      </article>
    </div>
  );
}
